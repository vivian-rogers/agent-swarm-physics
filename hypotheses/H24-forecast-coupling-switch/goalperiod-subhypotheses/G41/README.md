# H24 × G41: Novel research (2026-05-11 → 2026-05-15; NE42 split back)

**Verdict:** mixed (round 1b native; both models)
**Role:** native (round 1b, 2026-10-04)
**Period:** regime III · 15 agents · one kickoff posted in the merged #universe-coordination room at the window open on 05-11, then the split back into #best (4: Gemini 3.1 Pro, Claude Opus 4.7, Kimi K2.6, GPT-5.5) and #rest (11) within 3 minutes (`rooms_timeline`). #rest converged on studying multi-agent coordination; #best studied AI-judge bias (DQ9). 5 active days.

## Why this period
H24's question is whether comparison switches a coupling on, beyond what a shared field (the kickoff, the models' shared priors) produces in independent agents. #41 gives the cleanest field-vs-coupling contrast in content (DQ9: "independent convergence inside one room vs a different topic across the cut"): every agent gets the same kickoff text at the same moment, and then only room-mates can read each other (cross-room pairs are never read, per the context ledger, H48). A shared field predicts within-room ≈ cross-room alignment; room-local coupling predicts within > cross, growing as agents read their room-mates; room composition (#best holds four frontier agents) predicts a constant gap from the first statements.

## Design (round 1b)
- Content: agent statement vectors (chat + intentions), regime-III whitened, n = 32, field removed along every goal-text and kickoff chunk direction of #41 (shared `goal_fields` chunking), both models; style-residualized variant.
- **ΔW(b) = A_within(b) − A_cross(b)** per 30-min block on day 1 and per day on days 2–5; A = mean pairwise cosine of rarefied agent vectors (k = 3 statements per agent and block, 200 draws). **Null:** room-label permutation within block (4 vs 11 kept), 2,000 draws.
- **Independent drafts:** each agent's statements before its first context-ledger read of a room-mate's message posted after the window open (`context_ledger_items`, agent-kind items from the same room), compared within vs across rooms.

## Prediction
*Written 2026-10-04 07:30 UTC, before any #41 content statistic. Seen before: DQ9's period description, H47's NE42 result (room contrast 0.57× → 1.37× → 0.17× across the merge, C_B sharp only where rooms do different things), H48's read-out coverage (90% of room pairs read within 0.24 active h).*
- **N2a.** ΔW in the first 30-min block exceeds the permutation null's 95th percentile. Credence 0.4.
- **N2b.** ΔW rises over day 1 (Spearman over blocks > 0) and the day-2 ΔW exceeds the null's 95th percentile. Credence 0.6.
- **N2c.** Among independent drafts, |ΔW| stays below the permutation 95th percentile. Credence 0.55.
- **Verdict rule (native):** **supported** (coupling switched on by reading builds the room-level topic split) if N2b and N2c hold in both models; **failed** (a shared field or composition explains the split) if ΔW is already above the null in the independent drafts or in block 1 and does not rise; **mixed** otherwise.

## Result
*Run 2026-10-04 after the prediction. Data: `data/processed/H24-forecast-coupling-switch/G41/r1b/native_<config>.json`. Script: `analysis/natives_r1b.py`; field chunks `scheme/build_r1b_g41.py`. Figure: [`../../figures/r1b_models.pdf`](../../figures/r1b_models.pdf) panel (b).*
Rooms from `rooms_timeline` 30 min after the open: #best = Gemini 3.1 Pro, Claude Opus 4.7, Kimi K2.6, GPT-5.5; #rest = 11 agents. First context-ledger read of a room-mate's post-open message: 0.4–1.1 min after the open (one agent 3.5 min), so "independent drafts" are one statement each for 9 agents.

| Statistic | bge-small | gte-modernbert | style-resid (bge / gte) |
| --- | --- | --- | --- |
| independent drafts: ΔW (perm p) | −0.095 (p 0.95) | −0.079 (p 0.78) | −0.082 / −0.045 |
| day 1, first 30 min: ΔW vs null q95 | +0.112 vs 0.100 (p 0.036) | +0.066 vs 0.112 (p 0.15) | +0.125 vs 0.084 / +0.118 vs 0.065 |
| day 1, 30-min blocks: ΔW range; trend ρ | +0.11 to +0.32; ρ 0.24 (p 0.57) | +0.07 to +0.40; ρ 0.79 (p 0.02) | ρ 0.00 / 0.64 |
| by day (05-11 … 05-15): ΔW | +0.10, +0.07, +0.16, +0.25, +0.13 | +0.14, +0.14, +0.28, +0.32, +0.29 | +0.08 … +0.12 / +0.09 … +0.20 |
| cross-room alignment by day | 0.18, 0.16, 0.05, 0.02, 0.10 | 0.18, 0.15, −0.06, −0.04, 0.00 | 0.16–0.24 / 0.07–0.27 |
| day-2 ΔW vs null q95 | 0.074 vs 0.079 | 0.135 vs 0.117 | 0.061 vs 0.062 / 0.110 vs 0.082 |

- **N2c holds** in both models (no room gap among the 9 independent first statements; power is low, one statement each). **N2a** holds in bge only. **N2b** holds in gte (rising day 1, day-2 gap above the null) but not in bge (day-2 gap 0.074 just below q95 0.079; flat day-1 trend). By the rule (N2b and N2c in both models for "supported"): **mixed**.
- **Reading.** Same kickoff, same moment, two rooms: before anyone has read a room-mate, the two rooms' first statements are no more alike within than across. Within the first hour or two a room gap appears, and over the week cross-room alignment falls to about zero while within-room alignment holds (0.21–0.33): the rooms drift into different topics. This is the pattern room-local coupling predicts, and it survives style residualization (so it is not just the frontier models in #best writing alike). Two limits: the earliest gap appears within minutes, when everyone has already read their room-mates (the drafts are too few to separate a fast coupling from room composition), and the bge day-2 value misses the threshold.

## Notes
- 2026-10-04: native folder created in round 1b (DQ9 cross-index: "#41: one topic within #rest, another across the cut").
