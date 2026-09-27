-- Thematic ETF Agent Sandbox — database schema
-- Mirrors thematic-etf-investment-policy.md. Run once against the Supabase Postgres instance.

create extension if not exists "pgcrypto";

-- ── Themes & funds ──────────────────────────────────────────────────────────

create table if not exists themes (
    id              uuid primary key default gen_random_uuid(),
    name            text not null,
    description     text not null,
    convergence     text,              -- the independent signals that converged (Section 7.1)
    why_now         text,              -- the fresh inflection, not an already-priced-in story
    status          text not null default 'candidate'
                        check (status in ('candidate','screened_out','active','closed')),
    discovered_at   timestamptz not null default now(),
    discovery_source text            -- which Workflow A run/schedule slot found it
);

-- Screened-out themes are recorded too (status='screened_out', reason in both
-- `description` and here) so Theme Discovery can be told what it already
-- rejected recently and skip re-researching it from scratch every run —
-- without this, an already-priced-in theme (nuclear, grid, quantum, ...) gets
-- fully re-researched with fresh web searches on every discovery run even
-- though the answer hasn't changed since the last one, hours or days ago.
alter table themes add column if not exists screened_out_reason text;

create table if not exists funds (
    id                  uuid primary key default gen_random_uuid(),
    ticker              text not null unique,
    name                text not null,
    theme_id            uuid references themes(id),
    asset_class         text check (asset_class in ('equity','commodity','commodity_futures','novel')),
    tier                text check (tier in ('core','speculative','excluded')),
    aum_usd             numeric,
    inception_date      date,
    expense_ratio       numeric,        -- decimal, e.g. 0.0075
    is_leveraged_inverse boolean not null default false,
    is_single_company   boolean not null default false,
    is_fx_exposed       boolean not null default false,
    fx_note             text,
    last_screened_at    timestamptz,
    screen_result       text check (screen_result in ('passed','excluded_aum','excluded_single_company','excluded_other')),
    screen_notes        text,
    selected_over       jsonb,          -- tickers of alternative funds considered for the same theme + why this one won
    created_at          timestamptz not null default now()
);

-- ── Decks ───────────────────────────────────────────────────────────────────

create table if not exists decks (
    id                  uuid primary key default gen_random_uuid(),
    deck_type           text not null check (deck_type in ('new_opportunity','monitoring')),
    fund_id             uuid references funds(id),
    position_id         uuid,           -- set for monitoring decks; fk added below after positions exists
    theme_id            uuid references themes(id),
    status              text not null default 'pending'
                        check (status in ('pending','more_info_requested','approved','rejected','expired')),
    round_count         integer not null default 0,   -- more-information loop counter, capped at 2 (Section 8)
    content             jsonb not null,                -- full structured deck content (Section 8 / monitoring format)
    confidence          text check (confidence in ('high','medium')),
    recommended_action  text,           -- monitoring decks: hold/add, trim, exit
    github_issue_number integer,
    github_issue_url    text,
    urgent              boolean not null default false, -- thesis-broken / structural-risk / cleared-for-exit
    created_at          timestamptz not null default now(),
    decided_at          timestamptz,
    decision            text check (decision in ('yes','no','more_info','confirm','override')),
    decision_notes      text,
    expires_at          timestamptz     -- created_at + 5 business days (Section 8 no-response default)
);

-- ── Positions & lots (LIFO, 30-day hold) ────────────────────────────────────

create table if not exists positions (
    id                      uuid primary key default gen_random_uuid(),
    fund_id                 uuid not null references funds(id),
    status                  text not null default 'open' check (status in ('open','closed')),
    thesis                  text not null,
    thesis_evidence         text not null,      -- evidence categories thesis was built on
    invalidation_condition  text not null,
    thesis_state            text not null default 'exceeding'
                            check (thesis_state in ('exceeding','drifting','broken')),
    confidence              text not null check (confidence in ('high','medium')),
    tier                    text not null check (tier in ('core','speculative')),
    opened_at               timestamptz not null default now(),
    closed_at               timestamptz,
    last_scored_at          timestamptz,
    opening_deck_id         uuid references decks(id)
);

alter table decks
    add constraint decks_position_id_fkey foreign key (position_id) references positions(id);

create table if not exists lots (
    id                  uuid primary key default gen_random_uuid(),
    position_id         uuid not null references positions(id),
    shares              numeric not null,
    fill_price          numeric not null,
    opened_at           timestamptz not null default now(),      -- simulated fill date/time
    eligible_exit_at    timestamptz not null,                    -- opened_at + 30 days
    status              text not null default 'open' check (status in ('open','closed')),
    closed_at           timestamptz,
    closing_trade_id    uuid,           -- fk added after trades exists
    deck_id             uuid references decks(id)                -- the approved deck that authorized this lot
);

-- ── Trades (simulated fills — our own ledger, no broker involved) ──────────

create table if not exists trades (
    id              uuid primary key default gen_random_uuid(),
    lot_id          uuid references lots(id),
    position_id     uuid not null references positions(id),
    side            text not null check (side in ('buy','sell')),
    shares          numeric not null,
    price           numeric not null,
    executed_at     timestamptz not null default now(),
    deck_id         uuid references decks(id),
    notes           text
);

alter table lots
    add constraint lots_closing_trade_id_fkey foreign key (closing_trade_id) references trades(id);

-- ── Cash ledger (notional $20k sandbox capital, Section 9) ─────────────────

create table if not exists cash_ledger (
    id          uuid primary key default gen_random_uuid(),
    entry_type  text not null check (entry_type in ('deposit','buy','sell','dividend')),
    amount      numeric not null,     -- positive = cash in, negative = cash out
    trade_id    uuid references trades(id),
    occurred_at timestamptz not null default now(),
    notes       text
);

-- ── Sourcing (anti-hallucination — Section 1 / Verification Agent) ─────────

create table if not exists sources (
    id          uuid primary key default gen_random_uuid(),
    deck_id     uuid references decks(id),
    claim       text not null,        -- the exact stated fact
    source      text not null,        -- provider/filing/article it came from
    url         text,
    verified    boolean not null default false,
    created_at  timestamptz not null default now()
);

-- ── Price history (for target-price tracking, not live trading) ───────────

create table if not exists price_history (
    id          uuid primary key default gen_random_uuid(),
    ticker      text not null,
    price_date  date not null,
    close_price numeric not null,
    source      text not null default 'fmp',
    unique (ticker, price_date)
);

-- ── Agent run log (every pipeline stage, both workflows) ───────────────────

create table if not exists agent_runs (
    id              uuid primary key default gen_random_uuid(),
    workflow        text not null check (workflow in ('A','B')),
    agent_name      text not null,
    theme_id        uuid references themes(id),
    fund_id         uuid references funds(id),
    position_id     uuid references positions(id),
    deck_id         uuid references decks(id),
    started_at      timestamptz not null default now(),
    finished_at     timestamptz,
    status          text not null default 'running' check (status in ('running','ok','failed','sent_back')),
    input_summary   jsonb,
    output_summary  jsonb,
    error           text
);

create index if not exists idx_decks_status on decks(status);
create index if not exists idx_positions_status on positions(status);
create index if not exists idx_lots_position on lots(position_id);
create index if not exists idx_lots_status on lots(status);
create index if not exists idx_agent_runs_workflow on agent_runs(workflow, agent_name);
