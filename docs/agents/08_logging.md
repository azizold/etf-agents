# Logging Agent

Source of truth: `policy/thematic-etf-investment-policy.md`, Section 5, 7 and 9.

## Role

Records the deck, the decision (yes/no/more-info, or confirm/override/more-info
for monitoring decks), and the outcome. **Never executes trades.** Trade
placement is manual — you place the paper trade yourself once a deck is
approved. This agent's job starts once you confirm a trade was placed.

## What it does on each event

- **Deck created** → row in `decks`, posted to GitHub Issues (see
  `src/github_issues.py`).
- **Decision recorded** → `decks.decision`, `decks.status` updated.
- **Trade confirmed by you** → a `trades` row, and for a buy: a new `lots`
  row with its own 30-day clock (`opened_at` + 30 days = `eligible_exit_at`).
  This is the earliest point a lot's eligible-exit date can exist — no trade
  exists before this step, so no date exists before this step either.
  An add to an existing position opens a **new** lot; the position's overall
  eligible-exit date becomes whichever lot is most recent (LIFO) — this
  agent does not overwrite the position's existing lots, it adds one.
- **Position closed** (a sell of the entire remaining lot(s)) → `positions`
  row updated to `closed`.
- **Thesis re-score** (Workflow B) → `positions.thesis_state` updated,
  logged regardless of whether the state changed, so the history is
  complete even when nothing moved.

## Notes

This agent has no LLM reasoning step of its own in the current build — it is
implemented directly in `src/db.py` and called by the orchestrators
(`src/workflow_a.py`, `src/workflow_b.py`) after each real-world event
(deck created, decision received, trade confirmed). It is listed here for
completeness against the policy document's 8-agent pipeline.
