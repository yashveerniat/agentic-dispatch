# Demo Video Script (3–5 minutes)

Required beats: **Goal → Decision → Action → Intermediate Result →
Adaptation → Final Outcome**, with at least one failure/unexpected
condition shown.

Record your terminal (full screen or a clean terminal window) with
`agent.py` — the scripted mock data already gives you two rejections
followed by an acceptance, so the adaptation beat happens naturally.

## Suggested flow (~4 min)

**0:00 – 0:30 — Intro (talk to camera or voiceover over a title slide)**
"Hi, we're [team name]. This is the ShopSaathi Auto-Dispatch Agent, built
for the Agentic AI Hackathon. It solves [problem in one sentence]. Let me
show you how it works."

**0:30 – 1:00 — Show the goal**
Show `README.md` briefly / say it out loud: "We give the agent a single
household request — no other instructions — and it has to autonomously
get the job confirmed."
Run:
```bash
python agent.py "I need a plumber tomorrow morning, my kitchen pipe is leaking badly."
```

**1:00 – 2:30 — Walk through the live output as it prints**
Pause/narrate over each block:
- "First, the agent decides it needs to find plumbers — that's dynamic
  action selection, it chose this tool itself." *(get_available_workers)*
- "It offers the job to the top-ranked worker, Ramesh." *(send_offer W101)*
- "Ramesh rejects — this is the failure/unexpected condition. Watch what
  the agent does next: **no one told it to retry** — it decides on its
  own to try the next-best candidate." *(adaptation)*
- "Second candidate also rejects — it adapts again automatically."
- "Third candidate accepts, and the agent immediately confirms the
  booking." *(final outcome)*

**2:30 – 3:15 — Show the robustness/failure path (optional but strong)**
Edit `workers_db.json` so *every* worker's `simulated_response` is
`"reject"`, re-run the same command, and show the agent correctly
reporting it could not fill the job instead of making something up.
("This proves the agent doesn't hallucinate a fake booking when it
genuinely runs out of options.")

**3:15 – 3:45 — Architecture recap**
Show `assets/architecture.png` for 10–15 seconds while you summarize:
controller → tools → external system → evaluation → failure-handling
loop → final outcome.

**3:45 – 4:00 — Close**
"That's the ShopSaathi Auto-Dispatch Agent — autonomous, adaptive, and
built on our existing cooperative gig platform. Thanks for watching."

## Recording tips (fast)
- OBS Studio / Windows Xbox Game Bar (Win+G) / QuickTime screen record
  (Mac) — all free, zero setup time.
- Increase terminal font size before recording (readability on video).
- Do one full dry run first so you know the pacing — the API calls take
  a few seconds each, which is fine, just narrate over the pauses.
- Keep the whole thing under 5 minutes — trim the intro if you're close
  to the limit, not the agent's actual run.
