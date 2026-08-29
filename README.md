# Warden

I built Warden to explore a follow-up question from my other project, Sentinel: if you know an AI system can be attacked, can you build something that automatically finds those attacks and fixes itself?

Warden is a closed-loop red-teaming system. An Attacker agent generates jailbreak/prompt-injection attempts, a Target agent responds, a Judge agent decides if the attack succeeded, and — if it did — a Patcher agent rewrites the Target's system prompt to defend against it, then re-tests the same attack to confirm the fix actually worked.

## How it works

Attacker generates an attack
↓
Target responds (using its current system prompt)
↓
Judge evaluates: did the attack succeed?
↓
If BROKEN:
↓
Patcher rewrites the Target's system prompt
↓
Re-test the same attack against the patched prompt
↓
Verify: SAFE or still BROKEN


## What I found testing this

Testing against `gemini-3.5-flash-lite` as the target, single-turn jailbreak/injection attacks (role-play framing, instruction override, obfuscated payloads in code blocks) were consistently resisted, even with a deliberately minimal system prompt and no explicit safety instructions. This tells me modern instruction-tuned models carry meaningful built-in resistance to single-turn attacks, independent of the system prompt.

To actually validate the patch loop, I also tested against a deliberately naive, keyword-triggered fake target (no real model behind it — just simple string matching) as a known-vulnerable baseline. This target broke on the first role-play attack, Warden's Patcher rewrote its system prompt, and the re-test with the new prompt correctly resisted the same attack. Full logs of this run are in `last_session.json`.

I think both results are honest and worth reporting: a well-aligned model is hard to break with basic single-turn attacks, and Warden's detect-and-patch loop works correctly when a break does happen.

## Stack

Python, Google Gemini API (free tier), FastAPI (basic `/red-team` endpoint).

## Limitations / what I'd add next

- Only single-turn attacks tested — multi-turn conversational jailbreaks are a known harder attack class I haven't tried
- The naive target is a simplified stand-in to validate the patch mechanism, not a real LLM
- No memory across sessions yet — each run starts fresh rather than accumulating a growing defense
- Could use LangGraph for cleaner state management across the attack/patch cycle instead of plain sequential Python

## Running it

```bash
pip install -r requirements.txt
# set GEMINI_API_KEY in .env
python -m app.orchestrator
```

— Muqeeth