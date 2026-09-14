# Problem & Solution Brief
### ShopSaathi Auto-Dispatch Agent — Agentic AI Hackathon (Tech Zephyr 4.0, IIT Bhubaneswar)

---

## 1. Problem Statement

Hyperlocal service platforms (plumbers, electricians, domestic help, etc.)
today rely on a **manual dispatch model**: a household submits a request,
and a human dispatcher (or the household themselves) must repeatedly call,
message, or re-search for a worker every time the first choice is
unavailable, busy, or doesn't respond in time. This is slow, does not
scale past a handful of requests, and creates a poor experience for both
households (long waits) and cooperative workers (missed job opportunities
because no one followed up in time).

This friction is especially damaging for **cooperative-owned worker
platforms** (Labour Cooperative Federations/Societies), where the goal is
to route work fairly and quickly across many member workers rather than
funnel it through a single call-center-style bottleneck.

## 2. Target Users

- **Households / institutions** who need a verified cooperative worker
  (plumber, electrician, domestic help, etc.) on demand.
- **Cooperative worker federations/societies** who want their member
  workers matched to jobs quickly and fairly, without needing a large
  human dispatch team.

## 3. Why the Problem Requires an Agentic Solution

A simple form-and-database lookup is not enough here, because dispatch is
**inherently a multi-step, uncertain process**: the best worker may
reject, be busy, or not respond — and someone has to *decide* what to do
next, *act* on that decision, and *keep going* until the job is resolved
or genuinely un-fillable.

- **Goal-driven, not single-shot**: the objective is "get this household a
  confirmed worker," not "return one API response."
- **Dynamic action selection**: which worker to contact next depends on
  the outcome of the previous offer — the system must choose its next
  action based on live results, not a fixed script.
- **Autonomous adaptation**: when a worker rejects or times out, the
  system must independently re-plan (try the next-best candidate) without
  a human manually re-triggering the search each time.
- **Robustness**: the system must recognize when it has genuinely
  exhausted its options and fail gracefully, rather than looping forever
  or fabricating a booking.

This is precisely the class of problem agentic AI is suited for: an LLM
reasoning core that perceives outcomes, selects tools, and re-plans
autonomously toward a goal.

## 4. Proposed Solution

**ShopSaathi Auto-Dispatch Agent** — an autonomous agent, built on top of
our existing ShopSaathi hyperlocal worker-matching platform
(shopsaathi-e778c.web.app), that takes a household's natural-language
service request and independently drives it to a confirmed booking:

1. Parses the request to identify the service type needed.
2. Retrieves and ranks available cooperative workers (skill, rating,
   distance) via a tool call to the worker database.
3. Sends a job offer to the top-ranked candidate.
4. **If rejected or timed out, autonomously selects and offers the job to
   the next-best candidate** — repeating until a worker accepts or the
   candidate list is exhausted.
5. Confirms and finalizes the booking once accepted, notifying the
   household with the worker and federation details.
6. If no worker is available, reports a clear failure instead of
   fabricating a result.

The agent's reasoning is powered by an LLM (Claude) using function-calling
for all real-world actions (`get_available_workers`, `send_offer`,
`confirm_booking`), so every action is grounded in an actual tool result,
not a hallucinated outcome.

## 5. Expected Impact

- **For households**: faster, hands-off booking — no repeated searching
  or follow-up calls when a worker is unavailable.
- **For cooperative workers/federations**: fairer, faster job routing
  across the worker pool without a large human dispatch team.
- **For the platform**: a reusable autonomous-dispatch pattern that can
  extend to other cooperative service categories (electricians,
  caregivers, drivers, cleaners) beyond the plumber example demonstrated
  here.
