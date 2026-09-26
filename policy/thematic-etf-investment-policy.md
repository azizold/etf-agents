# Thematic ETF Investment Policy — Agent-Run Sandbox

**Purpose:** This document is the mandate every agent in the pipeline checks against before a recommendation reaches the human reviewer. Nothing gets into a deck that violates these rules.

---

## 1. Investment Philosophy

- **High conviction, not diversification.** This is not a hedged, broad-market approach. It's a small number of high-conviction thematic bets.
- **Thesis drives decisions, not price.** Price is information, not a trigger. A falling price with an intact thesis is a potential *add* signal, not a sell signal.
- **Themes are open-ended.** No fixed sector list (space, cybersecurity, robotics, AI infra, etc. are examples, not a whitelist). Any theme with genuine structural tailwinds and a clear "why now" qualifies — industries, countries, technologies, policy-driven shifts, anything.
- **ETFs only.** No single-stock positions (per compliance restriction). Eligible asset classes are open — equities and commodities/commodity futures are examples, not an exhaustive list; any asset class is in scope if a specific opportunity has real tailwinds (e.g., real estate, currencies, alternative structures).
  - **Excluded regardless of theme quality:** single-company ETFs (satisfy the letter of "it's an ETF" while violating the spirit of the single-stock restriction), bonds (a stated preference, not an oversight), and broad-market index funds (SPY, total market) as core holdings — this is intentionally not a diversified core-satellite approach.
- **Leveraged and inverse ETFs are capped at 15% of total portfolio**, combined. These decay from daily rebalancing even when directionally right over time, which is a structurally different risk than anything else in this doc — treat as a distinct sub-category with its own disclosure requirement (decay risk explained in the deck, not just the directional thesis).
- **Valuation methodology is routed by asset class** — full mechanics in Section 6, ownership in Section 7.
- **Every stated fact must be sourced.** Any figure or claim presented as fact — AUM, expense ratio, holdings weights, a company's revenue/EBITDA figure, a macro data point, a news event cited as a tailwind — must carry a traceable source (the data provider, filing, or article it came from) wherever it appears in a deck. A forecast, assumption, or opinion (a projected growth rate, a multiple assumption, a confidence rating) is not a "fact" and doesn't need a source, but must be clearly labeled as the agent's own assumption, not asserted as if it were established data. This is the primary anti-hallucination control across every agent — an unsourced number is treated as unverified and cannot appear in a deck as though it were established. See Section 7 for which agent enforces this before a deck reaches you.

---

## 2. Portfolio Construction

- **Target holding count: 4–8 positions.** Below 4 = insufficient idea diversity. Above 8 = conviction diluted, thesis-tracking quality degrades.
- **No forced rebalancing on position size.** A winning position is allowed to grow past any nominal "percent of book" figure. Concentration from conviction is accepted, not capped.
- **Mandatory overlap check on every recommendation**, regardless of theme. Thematic ETFs frequently share the same 15–20 mega-cap names underneath a different label. The Portfolio-Fit Agent must calculate and report holdings overlap between any candidate and existing positions before it reaches the deck stage.
- **When at target count (8) and a new high-conviction idea appears:** it does not automatically queue behind existing positions — conviction ranks candidates against your *current* weakest holding, not by arrival order. The deck for the new idea includes a direct comparison against your lowest-conviction current position (weighted by confidence level and current thesis state per Section 4 — a position that's "drifting" with Medium confidence ranks below a new "exceeding"/High candidate). You then decide: replace that position (sell, subject to the 30-day LIFO lock, Section 5), let the new idea queue until a slot opens naturally, or override to run at 9 temporarily. No automatic bump to 9–10 without that explicit decision at review time — the comparison is required, the outcome isn't automated.

---

## 3. Fund Classification: Two Tiers Plus Exclusion

| Tier | AUM Minimum | Age Minimum | Max Single Position Size |
|---|---|---|---|
| **Core** | $500M+ | 2+ years | No cap (conviction-sized) |
| **Speculative** | $50M+ | None | 10% of total book |
| **Excluded** | Under $50M AUM | — | N/A — not investable |

- The $500M / $50M lines are starting points — revisit after the sandbox period once real data on your candidate universe is in hand.
- **Combined Speculative-tier exposure is capped at 25% of total portfolio**, on top of the existing 10% per-position cap — so multiple Speculative positions can't quietly stack into a majority of the book even though each one individually respects its own cap. The Portfolio-Fit Agent enforces this alongside the per-position cap.
- A brand-new, high-conviction launch (the "DRAM at inception" case) can only ever enter through the Speculative tier, capped at 10% per position, never Core, regardless of how strong the thesis looks.
- Structural risk (issuer distress, liquidity drying up, AUM collapsing post-entry) triggers an immediate exit flag regardless of tier, thesis status, or price — subject to the 30-day hold (Section 5).

---

## 4. Thesis-Driven Position Management (replaces price-based rebalancing)

Every position is scored into one of three states on an ongoing basis, using the **same evidence categories** the original thesis was built on (no post-hoc justification):

1. **Thesis Exceeding / Playing Out** — evidence is confirming or strengthening (e.g., fundamentals improving, structural story deepening). **Action: hold, or add if a dip creates a better entry.**
2. **Thesis Drifting** — evidence is mixed or weakening but not disproven. **Action: trim toward a smaller size** (if outside the 30-day lock), watch for confirmation either direction.
3. **Thesis Broken** — the specific invalidation condition stated at entry has occurred. **Action: exit regardless of price or position size**, as soon as the 30-day hold allows.

Every deck must state, at entry: the thesis, the specific evidence supporting it, and the specific condition that would break it.

**Price drops are not a sell trigger.** A price decline with an intact thesis is flagged as a potential add opportunity, not an exit signal.

---

## 5. Compliance Constraints: Pre-Clearance + LIFO 30-Day Hold

- **Pre-clearance required on every trade, buy and sell alike.** Nothing executes without your explicit approval first — this is already how the review workflow works (Section 8's yes/no/more-info and confirm/override/more-info outcomes), now confirmed as a compliance requirement, not just a design choice.
- **The 30-day hold is tracked per lot, on a LIFO basis, not once per position.** Each purchase — the initial buy or any later add — starts its own 30-day clock from its own trade date. When selling, the most recently acquired lot must be sold first.
- **Consequence: adding to a position extends the whole position's effective lockup, not just the new shares.** If you buy on day 0 and add more on day 20, the day-20 lot isn't eligible until day 50 — and because LIFO requires that lot to be sold first, you can't touch the older, already-eligible day-0 shares underneath it until the day-20 lot clears. **A position's true eligible-exit date is always its most recent lot's date, not its original entry date.**
- This directly affects the "add on a dip" behavior in Section 4 (Thesis Exceeding): an add is not free from a liquidity standpoint. It should be weighed against the 30-day outlook and macro backdrop, same as a new entry, since it re-locks the entire position for another 30 days from the add date.
- Thesis-broken and structural-risk flags still fire immediately regardless of any lock, but **execution of an exit waits until the position's current (most-recent-lot) eligible-exit date.**
- A **Thesis Drifting trim (Section 4)** can only execute once the most recent lot has cleared — you cannot sell older shares out from under a newer, still-locked lot under strict LIFO.
- **Entry discipline is the primary risk control, more so now that adds also re-lock the position:**
  - Every deck includes a **30-day outlook** section — what could plausibly happen in the near term, independent of the long-term thesis.
  - Fast-moving, event-driven, or newly-launched candidates get smaller sizing specifically because of lockup exposure.
- **Compliance note:** confirm with your compliance desk whether other restrictions (restricted list, position limits) apply beyond pre-clearance and the LIFO hold before going live with real capital.

**Tax note (relevant once live, not during paper sandbox):** because the minimum hold is only 30 days, most exits will land in short-term capital gains territory — taxed as ordinary income rather than the lower long-term rate (which requires holding over a year). This is a real drag on net returns at a high income level and worth factoring into whether a position is worth the round-trip, not just whether the pre-tax thesis worked. Not tax advice — worth a conversation with a tax professional before trading real capital.

---

## 6. Target Price Methodology (required on every deck)

**Approach: bottom-up, built from per-holding EV/equity-value analysis, rolled up to the fund level.** This mirrors the single-stock methodology (forecast a key figure → apply a forward multiple → future EV → future equity value → target price → implied return), applied to each top holding individually, then weighted and combined.

**Steps 2–5 repeat for each scenario (bear/base/bull); step 1 is done once and reused across all three:**

1. **Select the top holdings** covering the majority of fund weight (concentrated funds may only need 3–5 names; broader funds may need more — the deck states the coverage % achieved and why the cutoff was chosen).
2. **For each selected holding:** forecast the relevant figure (revenue, EBITDA, etc.) at the target date, apply a forward multiple, derive future EV → future equity value → target share price → implied % return. Show the reasoning behind both the forecast figure and the multiple assumption for each name.
3. **Weight each holding's implied return by its current portfolio weight** in the ETF, and sum to get the fund's weighted implied return.
4. **Adjust for expense ratio drag** (subtract annualized expense ratio from the implied return, more material for actively managed funds).
5. **Convert to a target price** by applying the weighted implied return to the ETF's current price.

**Required disclosures on every target:**
- **Coverage %** — how much of the fund's weight the modeled holdings represent, and how the un-modeled remainder is treated (assumed in-line with theme, or excluded with weights rescaled).
- **Rebalancing risk** — for actively managed / periodically rebalanced funds, note that current weights may shift before the target date.
- **Concentration transparency** — for highly concentrated funds, state plainly that the target is effectively a weighted view on 2–3 single names, not a diversified basket call.
- **Data maturity** — flag when the fund is too young/thin to sanity-check assumptions against its own trading history.

**Commodity / commodity futures ETFs — different methodology.** These have no earnings or EV to model, so the EV/equity-value approach doesn't apply. Instead:
1. **Forecast the commodity price itself** at the target date, based on supply/demand fundamentals (production capacity, demand drivers tied to the theme, inventory levels), not a multiple.
2. **Convert to fund-level return** — for a physically-backed fund, this maps roughly 1:1 to the commodity price move (minus expense ratio); for a futures-based fund, factor in **roll yield** (contango erodes returns over time, backwardation adds to them) since a futures ETF's return can diverge meaningfully from the spot commodity price even when the price call is right.
3. **Flag structure explicitly in the deck** — physically-backed vs. futures-based, and if futures-based, current contango/backwardation state and its expected drag/boost.
4. **Tax note:** many commodity futures ETFs issue a K-1 tax form rather than a standard 1099, which has different filing implications — worth confirming with a tax professional before trading these live.

**Novel / other asset classes — no fixed template.** For anything that doesn't fit the equity or commodity approach (e.g., real estate, currency, or other structures), the Valuation Agent builds a bespoke forecast using whatever the relevant driver actually is for that asset type (funds from operations for REIT-style funds, rate differentials for currency-themed funds, etc.). The deck must show the full reasoning chain explicitly — what was forecast, why, and how it converts to an implied return — rather than forcing it into the equity or commodity template. If the Valuation Agent can't build a defensible forecast at all for a given structure, that's disclosed as a limitation rather than skipped silently.

---

## 7. Agent Pipeline

This is two distinct workflows, not one linear chain — they run on different triggers and shouldn't be built as a single sequential pipeline.

### Workflow A — New Opportunity (triggered by a candidate theme/fund)

1. **Theme Discovery Agent** — scans for structural tailwinds (policy shifts, capital flows, demographic/tech inflections, new fund launches as a flow signal). Open-ended, no fixed theme list. Flags whether a theme is well-served by an existing ETF or not.
   - **Cadence:** scheduled, not continuous — pre-market before each trading day, post-close after each trading day, and once at the end of the weekend (pre-Monday-open) so candidates are freshest right before your weekend review. Aligns discovery frequency with your review cadence instead of running faster than decisions can be made; downstream hard screens (below) still throttle volume.
   - **Two standards a candidate must clear:** (a) **convergence** — multiple independent signals pointing the same direction, not one compelling narrative; (b) **"why now"** — a fresh inflection, not an already-priced-in story.
2. **Fundamental / Composition Agent** — holdings breakdown, sector concentration, expense ratio, AUM, liquidity, tracking error, currency/geographic exposure.
   - **Hard screens (stop the pipeline here):** single-company ETFs; AUM under $50M (Excluded tier, Section 3).
   - **Sets tier classification** (Core/Speculative, for anything that passes) from the AUM/age data it gathers.
   - **Flags asset-class type** to route to the correct valuation method (equity-style, commodity-style, or novel/other, per Section 6).
   - **Multi-ETF theme selection:** when a theme is served by more than one ETF, this agent compares all candidates (AUM, age, expense ratio, liquidity, concentration, overlap with existing holdings) and advances only the single best fit to the rest of the pipeline — Valuation, Risk, and Portfolio-Fit run once per theme, not once per fund. The deck must state why the chosen fund won out over the alternatives. **Exception:** if two funds serving the same theme genuinely occupy different roles (e.g., an established Core-eligible broad fund vs. a newer Speculative-only pure-play), both may advance as separate opportunities — but each still goes through its own overlap check so you're not unknowingly doubling up on the same underlying holdings.
3. **Valuation Agent** — owns all of Section 6: per-holding revenue/EBITDA forecasts and multiple assumptions, the weighted roll-up math, the commodity price/roll-yield methodology, the novel/other bespoke path, **an explicit currency assumption for any candidate the Composition Agent flags as FX-exposed**, and all required disclosures.
4. **Risk / Counter-Case Agent (screening pass)** — argues against the thesis for this specific candidate, and checks the current macro backdrop for this asset type (see Workflow B below for this agent's separate ongoing monitoring role).
5. **Portfolio-Fit Agent** — overlap/correlation check against current holdings; consumes the tier tag set by the Composition Agent (does not set it) to apply tier-based caps (10% per Speculative position, 25% combined Speculative exposure, per Section 3); **computes the actual position-size recommendation** (Section 8) using the Risk Agent's confidence rating, the tier cap, and the number of currently open slots — no other agent owns this number; **tracks and enforces the 15% combined cap on leveraged/inverse exposure** (Section 1) against the current book plus the candidate. **At 8 positions, ranks the new candidate against your current weakest holding** (by confidence level and thesis state, Section 4) and surfaces that comparison in the deck (Section 2) rather than defaulting to a queue.
6. **Verification Agent** — the anti-hallucination check, runs after all upstream agents and before Synthesis assembles anything. Checks every factual claim collected so far (Section 1's sourcing rule) has a traceable source attached; flags any unsourced figure rather than letting it pass through as if verified. Independently re-checks that the Valuation Agent's math (Section 6) actually computes correctly from its own stated inputs — coverage % and weights sum correctly, the forecast-to-target-price chain follows from the stated assumptions — catching an arithmetic or logic error before it reaches you, not relying on your own review to be the only backstop. Sends anything that fails back to the owning agent rather than passing it forward with a caveat.
7. **Synthesis Agent** — assembles the standardized deck (Section 8) from all of the above, only once the Verification Agent has cleared it.
8. **Logging Agent** — records the deck, your decision (yes/no/more info), and outcome. **Does not execute trades** — trade placement stays manual, done by you directly on the broker's paper platform once you approve a deck. Once you confirm a trade was placed, this agent logs it and **opens a lot-level eligible-exit date** (trade date + 30 days, Section 5) for that specific lot — an add to an existing position opens a new lot with its own date, and the position's overall eligible-exit date becomes whichever lot is most recent (LIFO). This is the earliest point a lot's eligible-exit date can exist, since no trade exists before this step.

### Workflow B — Standing Position Monitoring (runs on a schedule, independent of new candidates)

- **Risk / Counter-Case Agent (monitoring pass)** — runs monthly or event-triggered against every *existing* position: re-scores the three-state thesis status (Section 4) against the original evidence categories, and separately runs the portfolio-level macro scan regardless of any individual thesis's status.
- **Portfolio-Fit Agent** — checks each existing position's eligible-exit date; when a flagged (thesis-broken or structural-risk) position's lockup clears, **flags it as cleared for exit** and hands off to Synthesis — Portfolio-Fit detects the condition, it doesn't assemble the deck.
- **Verification Agent** — same sourcing and consistency check as Workflow A, applied to whatever changed evidence is driving the re-score, before it reaches Synthesis.
- **Synthesis Agent** — the sole deck-assembler, same as in Workflow A. Packages any thesis-state change or cleared-exit flag into a **monitoring deck** (Section 8, lightweight format), not the full new-opportunity deck.
- **Logging Agent** — records every thesis re-score and outcome.

---

## 8. Standard Deck Format

1. Thesis (1–2 sentences) + specific supporting evidence, each factual claim sourced (Section 1) — verified by the Verification Agent (Section 7) before reaching this deck
2. Tier classification (Core / Speculative) + why
3. Asset class + valuation methodology used (equity-style / commodity-style / novel — per Section 6)
4. Currency/geographic exposure (or confirmation of none) — target price must build in a currency assumption if flagged, not just disclose the exposure
5. Counter-case (not softened) + macro backdrop flag (headwind or tailwind for this asset type, independent of the specific thesis)
6. Overlap/correlation check against current book
7. 30-day outlook
8. Thesis invalidation trigger (specific, checkable)
9. Target price: bear / base / bull, with full math shown
10. Position size recommendation (see sizing note below)
11. Confidence level: **High** or **Medium** — no "Low" (see confidence note below)

**Confidence scale:** there's no "Low" tier — given the high-conviction mandate (Section 1), anything the Risk Agent can't support to at least Medium doesn't reach a deck at all; it's filtered out before Synthesis, not presented weakly. **High** = strong convergence across independent signals, a clear "why now," no serious unresolved flaw from the counter-case. **Medium** = a real thesis with a genuine open uncertainty or an unresolved counter-case concern.

**Sizing note:** the Portfolio-Fit Agent (Section 7) computes this using confidence, tier cap, and open slots — not a fixed formula, but never presented without that reasoning shown. High confidence, Core tier can size toward a leading position, consistent with "let conviction run" (Section 2). Medium confidence, Core tier starts smaller, with room to add if the thesis later moves to "exceeding" (Section 4). Speculative tier follows the same logic scaled within its 10% cap (Section 3) — High near the cap, Medium meaningfully below it, preserving room to add later.

**Review outcomes:** every deck resolves to one of three responses — **yes** (approve; you place the paper trade manually on the broker platform, then the Logging Agent records it), **no** (reject, logged with reason if given), or **more information** (deck goes back to the relevant agent(s) for deeper research on the specific open question — e.g., back to Fundamental/Composition for a deeper holding-level breakdown, or back to Risk/Counter-Case if the concern is about the bear case — and returns as a revised deck, not a new one).

**No-response default:** if a deck receives no response within 5 business days, it defaults to **no** — consistent with pre-clearance (Section 5): silence is not approval, nothing executes without an explicit yes. The candidate is logged as expired, not rejected on the merits, and can resurface later as a fresh deck if the theme still holds.

**More-information loop cap:** capped at 2 rounds per deck. If a second round of "more information" still leaves an open question, the deck presents its best available answer with the gap explicitly disclosed, and you decide yes/no on what's actually known — this prevents an unresolvable question from looping indefinitely instead of surfacing the limitation.

### Monitoring Deck Format (Workflow B — lighter than the full deck above)

A monitoring deck doesn't need a fresh target price or a from-scratch counter-case — it's reporting a change, not pitching a new idea:

1. **Position + trigger type** — which holding, and why this deck exists (thesis re-score / structural-risk flag / cleared-for-exit)
2. **Current thesis state** (per Section 4: exceeding / drifting / broken) and what specifically changed since the last check, using the same evidence categories the original thesis was built on
3. **Macro backdrop update**, only if it changed materially since entry or the last check
4. **Recommended action**, per Section 4's rules for that state (hold/add, trim, or exit) — subject to the 30-day lock if applicable
5. **Lockup status** — eligible-exit date, and whether it's currently open or cleared
6. **Confidence in the re-score**

**Review outcomes for monitoring decks:** **confirm** (accept the recommended action; if it's an exit, you execute manually once eligible, same as any trade), **override** (take a different action than recommended — logged with your reasoning), or **more information** (Risk or Portfolio-Fit agent digs deeper on the specific question).

---

## 9. Sandbox Testing

- **Duration:** 4–5 months, paper trading only (e.g., Alpaca paper API).
- **Notional starting capital:** $20,000. This is what tier caps and sizing percentages (Sections 3, 8) translate against when placing actual paper trades.
- **Benchmark: S&P 500, compared against invested capital's return only — idle cash excluded.** The sandbox fills gradually (roughly 1 position/week), so most of the $20,000 sits uninvested early on. Comparing full portfolio value (idle cash included) against the S&P 500 would show a lag that's just an artifact of not being deployed yet, not a reflection of the picks. Every return figure in this section, including the success criteria below, refers to this invested-capital return, not total portfolio value.
- **Execution assumption:** paper trades fill at any point during the next trading day following your approval, not a fixed open/close price — this reflects that the time between a deck reaching you and your actual approval varies (same allowance applies to exits once the 30-day lock clears). This is a deliberate approximation, not precise-fill modeling, so treat the sandbox return as directionally indicative rather than an exact preview of live execution quality, especially for thinner Speculative-tier funds where fill timing matters more.
- **Dividends/distributions:** assumed **not reinvested** — tracked as cash received, not compounded back into the position, for both return tracking and target price math.
- **Review cadence:** New-opportunity decks generated for weekend review, typically 1/week, max 2–3. Mid-week decks only for genuinely time-sensitive, high-relevance opportunities. **This same time-sensitive exception applies to Workflow B outputs** — a thesis-broken flag, a structural-risk flag, or a cleared-for-exit notice is delivered as soon as it fires, never batched to the weekend queue.
- **Delivery channel:** weekend-batched decks (new-opportunity and routine monitoring updates) arrive conversationally — delivered into a session where you can read the deck and ask follow-up questions before answering, rather than a static document. Urgent Workflow B outputs (thesis-broken, structural-risk, cleared-for-exit) are additionally pushed as a direct notification (phone/email) at the moment they fire, so they don't sit unseen until the weekend batch.
- **Logging (from day one):** every deck, every decision (yes/no/more info), every thesis re-score, and outcome — stored for post-sandbox evaluation of decision quality, not just returns.
- **End-of-sandbox review:** compare invested-capital return vs. S&P 500, and separately evaluate decision quality (how often did flagged risks materialize, how often did "add on dip" calls work out, how often was a thesis break caught before major damage).
- **A book smaller than the 4–8 target at the end of the sandbox is not itself a process failure.** If genuinely only 2–3 ideas cleared the full pipeline in 4–5 months, that's the high-conviction filter working as designed (Section 1), not evidence the system underperformed — decision quality (below) is judged on the ideas that were surfaced and their outcomes, not on hitting a target count.

**Success criteria for going live:**
- **Return bar:** invested-capital return outperforms the S&P 500 by 5%+ over the 4–5 month sandbox period.
- **Drawdown:** no hard numerical cap — judged holistically alongside decision quality rather than an automatic disqualifier. A rough patch driven by a sound process that's still intact matters differently than one driven by a process failure.
- **Decision quality, weighted alongside the return number:** did thesis-break flags catch problems early, did the counter-case analysis hold up, were overlap/structural risks correctly identified. A good return with a broken process is a warning sign, not a green light; a mediocre return with a sound process might still be worth continuing to refine rather than abandoning.

---

## 10. Status

All open items resolved. Compliance is fully specified: pre-clearance on every trade, buy and sell, and the 30-day hold tracked per lot on a LIFO basis (Section 5). AUM/age thresholds (Section 3) remain as deliberately-set starting points, to be refined once real candidate data comes in during the sandbox. Ready to build against.
