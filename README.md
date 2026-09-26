# etf-agents

Agent-run thematic ETF research and paper-trading sandbox. The full mandate
is `policy/thematic-etf-investment-policy.md` — every agent checks against
it. How the system actually runs (GitHub Actions, not a chat session) is in
`docs/PIPELINE.md`.

## One-time setup (do this once, in order)

1. **Repo secrets** — already set: `DATABASE_URL`, `SUPABASE_URL`,
   `SUPABASE_SERVICE_ROLE_KEY`, `FMP_API_KEY`, `ANTHROPIC_API_KEY`.
2. **Database schema** — go to the repo's **Actions** tab → "One-time DB
   schema setup" → **Run workflow**. Safe to re-run.
3. **Notional starting cash** — record the $20,000 sandbox capital once:
   ```sql
   insert into cash_ledger (entry_type, amount, notes)
   values ('deposit', 20000, 'sandbox starting capital');
   ```
   (run this in the Supabase SQL editor)
4. **Enable Issues** on this repo if it isn't already (Settings → General →
   Features → Issues) — decks are delivered as Issues.
5. **Turn on notifications** for this repo (Watch → All Activity, or at
   least Issues) so decks reach you promptly.

## Running it

Both workflows run on their own schedule automatically once the above is
done — see `.github/workflows/workflow_a.yml` and `workflow_b.yml` for the
exact cadence. You can also trigger either manually from the Actions tab
(`workflow_dispatch`) — useful for the first dry run, or an off-cycle
"event-triggered" monitoring pass (policy Section 7B).

## Local development

```
pip install -r requirements.txt
cp .env.example .env   # fill in real values, never commit this file
python -m src.workflow_a discover --source manual
```

## Layout

```
policy/                  the investment policy document (source of truth)
docs/agents/              one operating spec per agent, loaded as system prompts
docs/PIPELINE.md          how the workflows are wired up, and why
db/schema.sql             Postgres schema
src/                      orchestration code (agents/, config, db, market data, Claude, GitHub Issues)
.github/workflows/        the actual scheduled runtime
```
