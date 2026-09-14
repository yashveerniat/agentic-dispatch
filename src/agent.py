"""
ShopSaathi Auto-Dispatch Agent
--------------------------------
An autonomous agent that takes a household's service request in natural
language and independently finds, offers, and confirms a cooperative
worker for the job -- including automatically retrying with the next
best candidate if a worker rejects or times out, with NO human in the
loop for that re-planning step.

Demonstrates: Goal-Driven Execution, Dynamic Action Selection,
Multi-Step Execution, Adaptation (failure -> retry), Robustness.

Usage:
    export ANTHROPIC_API_KEY=your_key_here
    python agent.py "I need a plumber tomorrow morning, my kitchen pipe is leaking"
"""

import json
import os
import sys
import time
from pathlib import Path

from anthropic import Anthropic

MODEL = "claude-sonnet-5"  # update to whichever current model your API key has access to
DB_PATH = Path(__file__).parent / "workers_db.json"

# ---------------------------------------------------------------------------
# Tools available to the agent. Each tool is a real Python function; the
# agent decides WHEN and WHETHER to call them and WHAT to do with the result.
# ---------------------------------------------------------------------------

def _load_db():
    with open(DB_PATH) as f:
        return json.load(f)["workers"]


def get_available_workers(service_type: str, exclude_ids=None):
    """Tool: fetch cooperative workers matching a service type, ranked by
    the platform's own scoring (rating desc, distance asc). This simulates
    a Firestore query against the ShopSaathi worker collection."""
    exclude_ids = exclude_ids or []
    workers = _load_db()
    matches = [
        w for w in workers
        if w["skill"] == service_type and w["id"] not in exclude_ids
    ]
    matches.sort(key=lambda w: (-w["rating"], w["distance_km"]))
    return matches


def send_offer(worker_id: str):
    """Tool: send a job offer to a specific worker and return their
    response. In production this would push a notification and await a
    webhook; here it returns a pre-scripted response so the demo is
    reproducible for judges."""
    workers = _load_db()
    worker = next((w for w in workers if w["id"] == worker_id), None)
    if not worker:
        return {"status": "error", "message": "worker not found"}
    # simulate real-world latency of a notification round-trip
    time.sleep(0.4)
    return {
        "status": worker["simulated_response"],
        "worker_id": worker_id,
        "worker_name": worker["name"],
        "reason": worker["simulated_reason"],
    }


def confirm_booking(worker_id: str, service_type: str, household_request: str):
    """Tool: finalize the booking once a worker has accepted."""
    workers = _load_db()
    worker = next((w for w in workers if w["id"] == worker_id), None)
    return {
        "status": "CONFIRMED",
        "worker_id": worker_id,
        "worker_name": worker["name"] if worker else worker_id,
        "federation": worker["federation"] if worker else "unknown",
        "service_type": service_type,
        "request": household_request,
    }


TOOLS = [
    {
        "name": "get_available_workers",
        "description": (
            "Fetch cooperative workers who match the requested service type, "
            "ranked by rating and distance. Pass exclude_ids to skip workers "
            "already tried in this dispatch attempt."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "service_type": {"type": "string", "description": "e.g. plumber, electrician, cleaner"},
                "exclude_ids": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "worker ids already contacted and rejected in this session",
                },
            },
            "required": ["service_type"],
        },
    },
    {
        "name": "send_offer",
        "description": "Send a job offer notification to a specific worker and get their response (accept/reject).",
        "input_schema": {
            "type": "object",
            "properties": {"worker_id": {"type": "string"}},
            "required": ["worker_id"],
        },
    },
    {
        "name": "confirm_booking",
        "description": "Finalize and confirm the booking once a worker has accepted the offer.",
        "input_schema": {
            "type": "object",
            "properties": {
                "worker_id": {"type": "string"},
                "service_type": {"type": "string"},
                "household_request": {"type": "string"},
            },
            "required": ["worker_id", "service_type", "household_request"],
        },
    },
]

TOOL_IMPL = {
    "get_available_workers": lambda **kw: get_available_workers(**kw),
    "send_offer": lambda **kw: send_offer(**kw),
    "confirm_booking": lambda **kw: confirm_booking(**kw),
}

SYSTEM_PROMPT = """You are the ShopSaathi Auto-Dispatch Agent, an autonomous
dispatch system for a cooperative-owned gig services platform.

GOAL: given a household's natural-language service request, find and
CONFIRM a suitable cooperative worker for the job -- fully autonomously.

RULES YOU MUST FOLLOW:
1. Identify the service type needed from the request (plumber, electrician, etc).
2. Call get_available_workers to retrieve ranked candidates.
3. Offer the job to the TOP-ranked candidate first via send_offer.
4. If the worker REJECTS: do NOT ask the human what to do. Autonomously
   select the next best candidate (excluding already-tried workers) and
   send_offer to them. Repeat until a worker accepts or candidates are
   exhausted.
5. Once a worker ACCEPTS, immediately call confirm_booking to finalize.
6. Narrate each decision briefly (which worker you're trying and why,
   what happened, what you're doing next) so your reasoning is visible.
7. If all candidates are exhausted without an acceptance, clearly report
   failure and what you attempted -- do not fabricate a booking.
"""


def run_agent(household_request: str, verbose=True):
    client = Anthropic()  # reads ANTHROPIC_API_KEY from env
    messages = [{"role": "user", "content": household_request}]
    tried_workers = []

    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            tools=TOOLS,
            messages=messages,
        )

        # Print any reasoning/narration text the agent produced this turn
        for block in response.content:
            if block.type == "text" and block.text.strip():
                print(f"\n[AGENT] {block.text.strip()}")

        if response.stop_reason != "tool_use":
            break  # agent is done (booked, or reported failure)

        messages.append({"role": "assistant", "content": response.content})
        tool_results = []

        for block in response.content:
            if block.type != "tool_use":
                continue
            name, tool_input, tool_id = block.name, block.input, block.id

            if verbose:
                print(f"  -> ACTION: {name}({json.dumps(tool_input)})")

            result = TOOL_IMPL[name](**tool_input)

            if name == "send_offer":
                tried_workers.append(tool_input.get("worker_id"))
                tag = "✅ ACCEPTED" if result["status"] == "accept" else "❌ REJECTED"
                print(f"     {tag} — {result['worker_name']}: {result['reason']}")
            elif name == "get_available_workers":
                print(f"     Found {len(result)} candidate(s): "
                      f"{[w['name'] for w in result]}")
            elif name == "confirm_booking":
                print(f"     🎉 BOOKING CONFIRMED with {result['worker_name']} "
                      f"({result['federation']})")

            tool_results.append({
                "type": "tool_result",
                "tool_use_id": tool_id,
                "content": json.dumps(result),
            })

        messages.append({"role": "user", "content": tool_results})

    return tried_workers


if __name__ == "__main__":
    request = " ".join(sys.argv[1:]) or (
        "I need a plumber tomorrow morning, my kitchen pipe is leaking badly."
    )
    print(f"HOUSEHOLD REQUEST: \"{request}\"")
    print("=" * 70)
    run_agent(request)
