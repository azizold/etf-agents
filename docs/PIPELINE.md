# How this actually runs

The policy document (`policy/thematic-etf-investment-policy.md`) is the
spec. This file explains how it's wired up as running code.

## Why GitHub Actions, not a Claude Code scheduled session

The obvious-seeming design — a Claude Code scheduled session waking up and
acting as all 8 agents — doesn't work here: this class of sandbox only
allows outbound network access to a small allowlist (GitHub, package
registries, Anthropic's own API). It cannot reach Supabase or Financial
Modeling Prep. Since a scheduled Claude Code session runs in the same kind
of sandbox, it would hit the identical wall.

So the actual runtime is **GitHub Actions**: it runs on a real schedule with
unrestricted internet access, and calls the Anthropic API directly for every
LLM reasoning stage. Claude Code (this repo's authoring environment) is only
used to write and push the code — it isn't part of the running system.

## The two workflows

- `.github/workflows/workflow_a.yml` — Theme Discovery through Logging
  (policy Section 7, Workflow A), on the pre-market / post-close / weekend
  cadence, plus a frequent no-LLM housekeeping pass (reading your Issue
  comments, applying the no-response default).
- `.github/workflows/workflow_b.yml` — the standing-position monitoring
  pass (policy Section 7, Workflow B), monthly by default plus a
  `workflow_dispatch` you can fire manually for an "event-triggered" re-score,
  and the same kind of frequent housekeeping pass for monitoring-deck
  comments.
- `.github/workflows/setup_db.yml` — one-time, manual: applies `db/schema.sql`.

## Deck delivery: GitHub Issues

Every deck is a GitHub Issue in this repo, labeled `new-opportunity-deck` or
`monitoring-deck` (`urgent` added for thesis-broken / structural-risk /
cleared-for-exit). Turn on GitHub mobile notifications (or watch the repo)
so these reach you the moment they post — that's the "push notification"
channel for urgent Workflow B outputs described in policy Section 9.

### Responding to a new-opportunity deck

Comment on the issue with exactly one of:
- `YES` — approved. You then place the paper trade yourself (see below) and
  comment `FILLED: <shares> shares at $<price> on <YYYY-MM-DD>` to log it.
- `NO` — rejected. Add a reason after a colon if you want it logged.
- `MORE INFO[stage]: <question>` — `stage` is one of `composition`,
  `valuation`, `risk` (omit for a general follow-up). Capped at 2 rounds
  (policy Section 8) — a third request gets the best available answer with
  the gap disclosed instead of looping again.

### Responding to a monitoring deck

Comment with exactly one of `CONFIRM`, `OVERRIDE: <what to do instead>`, or
`MORE INFO: <question>`.

### "Placing a paper trade"

There's no broker in this build — Alpaca was deliberately dropped (BofA
outside-account disclosure concerns). "Placing a trade" means recording a
simulated fill against real market prices in our own ledger (`trades`,
`lots` tables). The `FILLED: ...` comment above is literally the trade
execution step — there's nothing to click anywhere else.

## The 8 agents, as actually implemented

Each agent's operating spec lives in `docs/agents/`. `src/agents/*.py` loads
the relevant doc as the system prompt, adds the current data (from
`src/db.py` and `src/market_data.py`), and calls Claude
(`src/claude_client.py`), optionally with server-side web search enabled so
research claims come back with real citations (feeding Section 1's sourcing
rule directly).

| # | Agent | Module | Notes |
|---|---|---|---|
| 1 | Theme Discovery | `agents/theme_discovery.py` | web search on |
| 2 | Fundamental/Composition | `agents/composition.py` | pulls FMP data first |
| 3 | Valuation | `agents/valuation.py` | web search on |
| 4 | Risk/Counter-Case | `agents/risk.py` | `screen()` for Workflow A, `monitor()` for Workflow B |
| 5 | Portfolio-Fit | `agents/portfolio_fit.py` | `check()` for A, `check_lockups()` for B |
| 6 | Verification | `agents/verification.py` | runs before every Synthesis call, both workflows |
| 7 | Synthesis | `agents/synthesis.py` | the only agent that renders deck markdown |
| 8 | Logging | `src/db.py` + orchestrators | no LLM step — pure bookkeeping, per policy Section 7 step 8 |

`src/workflow_a.py` and `src/workflow_b.py` are the orchestrators — they
call the agents in the order the policy specifies, including the
Verification retry loop (send a failure back to the owning agent, capped at
2 retries before refusing to let the deck through).

## Known rough edges to expect on the first real runs

- **FMP endpoints**: the free tier's exact endpoint set shifts over time
  (`src/market_data.py` has a note on this). If a call 401s/404s during the
  dry run, swap it for FMP's current equivalent.
- **`MORE INFO[stage]`**: the housekeeping pass acknowledges the request and
  logs the round, but doesn't yet automatically re-run just that stage —
  it currently asks you to re-trigger `workflow_a` manually
  (`workflow_dispatch`) in the meantime. Automating that targeted re-run is
  a natural next improvement once the basic loop is proven out.
- **Claude model name**: `src/config.py` defaults to `claude-sonnet-5`.
  Override with the `CLAUDE_MODEL` env var / repo variable if a different
  model is preferred (e.g. Haiku for the cheaper screening stages).
