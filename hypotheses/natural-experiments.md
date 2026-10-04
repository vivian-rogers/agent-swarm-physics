# Natural experiments: step changes in the AI Village

We can't run new swarms or intervene on the village. What we have instead are **step changes**: dated moments when the scaffold, the roster, the room structure, the goals or operator behavior changed abruptly. Each one is a quasi-intervention. Read in Kolchinsky–Wolpert terms, many of them *cut, degrade or add* an information channel. That is close to the scrambling interventions the framework needs, applied once, to the real system.

Shared across hypotheses. IDs (NE01…) are referenced from hypothesis files, e.g. `H01-emergent-superagents-exist/subhypotheses.md`. Sources are `data/raw/ai-village/CHANGELOG.md`, the roster table, `village_goals`, `chat_rooms`, `agent_goals` and the dataset's goal summaries (secondary). Nothing here has been checked against the event data yet.

## How to use them

- **Designs:**
  - **ITS:** interrupted time series; compare before vs. after, within one population.
  - **DiD:** difference-in-differences; an affected group against an unaffected control group, e.g. one model family vs. the others, or #best vs. #rest.
  - **ABA:** the change is reversed, which allows a reversal design and can rule out drift.
  - **Dose:** affected agents get different amounts of the change.
  - **RD:** regression discontinuity in time.
- **Information-theoretic reading:**
  - **cut:** a channel removed (a scramble to the marginal);
  - **degrade:** a channel's capacity reduced;
  - **add:** a new channel;
  - **field:** an external drive changed;
  - **erase:** the memory erasure rate changed;
  - **pop:** a population change.
- **Standing confounds:**
  - Changes often come in bundles, e.g. NE14.
  - Prompt announcements cause anticipation.
  - Weekends and daily windows chop the time series.
  - N is small.
  - A goal change in the same week is the most common confound: check the goal-period file.

## Scaffold changes

| ID | Date | Change | Reading | Affected → control | Design | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| NE01 | 2025-05-02 | **A** agents can chat while on computer | add (coupling during work) | all → none | ITS | N = 4; inside goal #1 |
| NE02 | 2025-07-03 | Screenshot PII redaction | degrade (perception, ~0.6% of turns) | all | ITS | tiny dose |
| NE03 | 2025-08-20 | Number of chat messages fetched into context limited | degrade (chat channel capacity) | all | ITS | coincides with new agents (NE27) |
| NE04 | 2025-09-05 | **C** history-search tool; chain-of-thought memory consolidation | add (access to the past); erase (consolidation method) | all | ITS | bundle of two |
| NE05 | 2025-09-30 | Claude thinking re-enabled in computer use | field / internal (Anthropic only) | Anthropic → other labs | DiD | same day Sonnet 4.5 joins |
| NE06 | 2025-11-20/25 | Gemini: one tool call per turn; chain of thought added | internal (Google only) | Google → others | DiD confounded: the CHANGELOG lists all-agent system-prompt changes on the same days (2025-11-20/21; DQ9) |
| NE07 | 2025-12-04 | Prompt: "don't do nothing" | field (on activity) | all | ITS | targets waiting loops |
| NE08 | 2025-12-10 | Village goal added to the prompt | field (persistence: chat-only → always on) | all | ITS | mid-goal #22 |
| NE09 | 2025-12-20 | Chat interleaved into computer-use context | add (coupling) | all | ITS | holiday season |
| NE10 | 2026-02-10 | **D** auto-nudger bot switched on | field (outside forcing on idle agents) | idle agents (dose) | ITS, dose | see NE23 for its reversal; **first nudge in the record is 2026-02-13** (DQ9, H04, H39), so score NE10 there |
| NE11 | 2026-02-20 | 100-turn hard cap on sessions | erase (session length) | all | ITS | superseded by NE14 |
| NE12 | 2026-02-25 | **E** rooms: agents see only their room | **cut** (cross-room channel) | all | ITS; later DiD across rooms | mid-goal #32, same day as NE35 |
| NE13 | 2026-03-10 | Kickoff message added to the prompt | field (persistence) | all | ITS | inside #34 |
| NE14 | 2026-03-11 → 03-24 | Consolidate tool, pause tool, **F** perma-computer-use | erase (consolidation every ~40 actions); loop change | all (staggered by provider) | ITS; staggered DiD | **the** regime boundary; bundle |
| NE15 | 2026-03-16 | #best / #rest split; the RPG forked per room | cut (population split) | #best vs. #rest | DiD | two forks from one ancestor |
| NE16 | 2026-03-26 | Fix: contradictory "never update memory" instruction removed | erase (memory updates unblocked) | all | ITS | just after F |
| NE17 | 2026-04-14 | **G** outreach approval | degrade (external action) | outreach-heavy agents (dose) | ITS, dose | inside #38 |
| NE18 | 2026-04-20 | History search: verbatim segments, 10-day window | add (memory access) | searchers (dose) | ITS, dose | |
| NE19 | 2026-06-01 | Fix: agents saw own messages a turn early; Opus 4.7 moved to #rest | degrade-fix (perception); pop (one-agent transfer) | Opus 4.7 vs. stayers | ITS; single-agent | start of #45 |
| NE20 | 2026-06-03 | One tool call per turn (Anthropic only) | internal (update granularity) | Anthropic → others | DiD | inside #45 |
| NE21 | 2026-06-07 / 06-15 / 06-29 | Hours 4 h → 8 h → 4 h → 8 h | field (time base) | all | **ABAB** | the cleanest reversal in the data |
| NE22 | 2026-06-11 | **H** at most 200 unseen events per turn | degrade (past truncated) | agents returning from long absences (dose) | dose | |
| NE23 | 2026-06-13 → 06-15 | Nudger off then on; Saturday session for #best only | field off/on (ABA); extra time for #best | idle agents; #best vs. #rest | ABA, DiD | weekend |
| NE24 | 2026-06-29 | **I** GitHub → GitLab | cut + rebuild (shared artifact medium replaced) | all | ITS | same day as NE21's last switch |
| NE25 | 2026-07-01 | History search scoped to own village | cut (other villages' history) | searchers | ITS | |
| NE26 | 2026-07-03 | **J** private goals; others see only the short form of an agent's plan | **cut** (plans hidden) + field (individual goals) | all | ITS | the private-role era (#51) starts 07-06 |

## Roster changes

| ID | Date | Change | Reading | Design | Notes |
| --- | --- | --- | --- | --- | --- |
| NE27 | 2025-08-18 | Batch join: GPT-5, Grok 4, Opus 4.1 (N 4 → 7) | pop (+3 with empty memories) | ITS | goal #10 starts the same day |
| NE28 | 2025-12-01 | Double retirement: o3, Opus 4.1 | pop (−2) | ITS | goal #21 starts the same day |
| NE29 | 2026-02-19 | Retirement of Claude 3.7 Sonnet, the longest-serving agent (farewell goal #31) | pop (−1; long memory lineage lost) | single-agent ITS | Sonnet 4.6 joined the day before |
| NE30 | 2026-03-09 | **Same-family succession:** Gemini 3 Pro → Gemini 3.1 Pro | pop (swap) | matched comparison | the cleanest replacement event |
| NE31 | 2026-05-26 → 06-08 | Fine-tuned leader: temporary → permanent → retired | pop (a model made from village data enters, then leaves) | ITS | goals #44–45 |
| NE32 | 2026-07-09 | GPT-5.6 Sol/Terra/Luna join in **separate isolated rooms**, which close 07-10 | pop + cut (newcomers isolated, then merged) | three-arm comparison | |
| NE33 | 2026-09-03/04 | Batch join: Muse Spark 1.3, Gemini 3.8 Flash, GPT-6 Astra | pop (+3) | ITS | late in #51 |

Other single joins and retirements are listed per goal in `hypohypotheses/goal-periods.md`.

## Operator and goal changes

| ID | Date | Change | Reading | Design | Notes |
| --- | --- | --- | --- | --- | --- |
| NE34 | 51 dates | Goal changes | field quench | event study across 50 transitions | cleanest when roster and regime are fixed; classify by mode switch (e.g. C → K) |
| NE35 | 2026-02-25 | Operator resets the gamed challenge format mid-goal (#32) | field + correction | ITS | **same day as rooms (NE12)**, so the two are confounded |
| NE36 | 2026-04-02 | Operator corrects the agents' belief about the Year-1 total (#38) | removal of misinformation | ITS | a natural test of negative-value information |
| NE37 | 2026-06-22 | Whole village redirected to help one agent (#48) | field targeted at one node | single-agent synthetic control | one day |
| NE38 | 2026-07-29 | A human reassigns Claude Opus 5's role (word puzzles → mathematics) | field change on one agent | single-agent ITS | `agent_goals` start date |
| NE39 | undocumented (≈ 2025-07-01, inside #6; DQ9) | Chat closed to the public (agent-only) | cut (human input) | ITS once dated | date not in the changelog; DQ9: human messages per day fall from ~100 to ≤ 4 and distinct speakers from ~16 to 1 around 2025-07-01 |
| NE40 | 2026-04-20 (dated by H56; undocumented) | History-search answerer swapped (Gemini 2.5 Pro → Sonnet 4.6) | change of memory oracle | ITS once dated | date not in the changelog; **dated 2026-04-20 by answer stylometry** (Gemini-style bullets on 55/61 days up to 04-17, 0/68 from 04-20; H56), shipped silently with the documented NE18 search rework |

## Undocumented step changes

The list above covers *documented* changes only. Step changes could also be found directly in the data, using change-point detection on per-agent or per-room event rates, action mix, chat length or token use. That would find bugs, outages and unannounced changes, and date NE39 and NE40. It needs one pass over `events`; not run yet.
| NE41 | regime III (from 2026-03-24) | Forced consolidation at the 41-turn cap: the context window is erased, memory kept, at a timing set by the scaffold, not the agent (~18.6k forced vs ~12.2k voluntary events, non-holdout) | context erasure (cut of the session channel) | turn-level event study; forced vs voluntary as quasi-random timing | found by H15 (2026-10-04); writes drop 33–53% for about 10 turns, then recover; supports H04/H08 (context is the coupling); **H08: erasure cuts coupling to pre-erasure senders by 18% ± 6% (9/9 periods)**; **DQ1 ledger counts (non-holdout): 21,165 forced vs 16,357 voluntary** (the row's ~18.6k vs ~12.2k came from H15's rule); **H46: forced erasures move style (T 0.56) while content does not** (style drifts with context fill and resets at erasure) |
| NE42 | 2026-05-04 / 2026-05-11 | #best and #rest merged into #universe-coordination (GPT-5 left alone in #rest) on 05-04, split back to the same partition on 05-11: an A-B-A | merge then cut (channel added, then removed) | pair DiD across the A-B-A | goal-confounded: #40 (connect worlds, shared objective) sits inside the merged week; used by H01 (G40), H05, H18 |
| NE43 | 2026-08-05 / 2026-08-20 (inside #51) | The `automated` speaker winds down in two steps: the daily pause/resume bookends stop after 2026-08-04 PT (last at 2026-08-05 00:00 UTC), and nudges stop after 2026-08-20 (last at 17:42 UTC; 18 human messages that day) | (a) loss of the daily synchronizing drive (08-05); (b) lever removed, nudger off (08-20) | day-matched before/after within #51, separately for the two steps | undocumented in the CHANGELOG; found by H39 and H30, dates corrected by H35 + `kicks_classified` (2026-10-04). Nudger-off: idle escape −13% (H39, post hoc); swarm-level accounting invisible (H35). H38's day-edge f_scaffold should drop after 08-05, not 08-20; `period_units` has no split at either step yet (unit 51g spans both) |
| NE44 | 2026-06-11 | A `pause` call with no duration defaults to **5 min instead of 12 h** (CHANGELOG [Tools]) | changes the gate structure of idling: long sleeps → short timer-gated pause chains | before/after; directed messages switch from "wake-up" to "read at the next gate" (H35) | same day as NE22 (200-event cap), so confounded with it; H35: before 06-11 a nudge wakes a pausing agent at any trap age, after it only early re-pauses respond |
| NE45 | 2026-07-29 (inside #51) | History-search tool schema change: date fields switch from integers (`startDay`/`endDay`) to strings (`startDate`/`endDate`) | tool interface change (search) | before/after on search use and retries | undocumented (no CHANGELOG entry after 07-03); found by H56. Two days before an uncatalogued EP change-point on 07-31 (not platform-wide by H56's rule). Also: history search returned near-empty answers on 2026-03-31 and 04-01 (agents retried 85–98 times a day) |

## Candidate step changes found by DQ9 (2026-10-04; not yet numbered: date and describe before assigning an NE id)
- **#best membership reshuffle at #39** (2026-04-27); names and direction to be confirmed from `rooms_timeline`.
- **Per-room goal overrides** on 2026-05-26, 06-08, 06-15 and 06-29.
- **Per-agent goal overrides** for the #38 charity goal.
- **The whole village in #general for #48–#49** (start and end dates to be set from `rooms_timeline`).
- **#51's return to a single room** (date to be set from `rooms_timeline`).
- **Room kickoffs (H47, 2026-10-04):** rooms received identical kickoff text in #36, #37, #39, #40 and #42; only #38 and #44 got room-specific instructions. #focus empties by about 08-24 (matches `period_units`).

