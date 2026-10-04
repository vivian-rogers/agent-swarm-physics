# H48 × NE42: #best/#rest merge and split, A-B-A (2026-05-04 / 05-11)

**Verdict:** mixed
**Role:** native
**Period:** #39 (2026-04-27 → 05-01; two rooms, #best 4 / #rest 10 on day 1) → #40 (05-04 → 05-08; one merged room, #universe-coordination, 15 agents) → #41 (05-11 → 05-15; two rooms, same partition). Regime III, 4 active h/day. Not held out. Exception (c): the transition is the object; each side is still analysed within its own period.

## Why this period
The merge changes the read-out graph abruptly: in #39 and #41 an agent can read only its own room (4 or ~10 agents); in #40 everyone reads everyone (15). If settling is a bulk read-out mixing time, the five room-blocks across the A-B-A (#39 best, #39 rest, #40 merged, #41 best, #41 rest) should settle in the order of their read-out times; the field rival (kickoff clock) predicts no relation. Goal-confounded: each phase is a new goal with its own kickoff (#40's is a shared objective).

## Prediction
*Written 2026-10-04 ~07:10 UTC, before running settling on these periods (read-out predictors were already computed; no content touched).*
- **N1a (primary):** across the five room-blocks, Spearman(τ_S1, T90_block) > 0 (bge), and the same sign for t_mix^bulk; with 5 points only ρ = 1.0 reaches one-sided p < 0.05 (exact), so ρ ≥ 0.7 counts as "consistent", not significant.
- **N1b:** all-pairs coverage reaches 90% only in #40 (a structural check, certain by construction).
- **N1c:** τ_S1(#40, merged) differs from the A-phase room-size-weighted mean in the direction of its T90 change (sign test on one contrast; descriptive).
- **Against:** ρ ≤ 0 (settling order unrelated to read-out order).
- **Credence:** 0.35 for N1a's sign; with n = 5 any outcome is weak evidence.

## Result
Room blocks (day-1 modal room; τ_S1 in active h with the village kickoff; fit span 20 active h per period; * = not detected):

| Block | N | T90 (h) | depth-5 T90 (h) | t_mix bulk (h) | τ_S1 bge | τ_S1 gte |
| --- | --- | --- | --- | --- | --- | --- |
| #39 #best (2) | 4 | 0.39 | 7.06 | 0.139 | 29.7 | 6.5* |
| #39 #rest (3) | 10 | 1.00 | 6.12 | 0.080 | 4.0 | 64.3 |
| #40 merged (4) | 14 | 0.57 | 8.16 | 0.026 | 20.0 | 23.1 |
| #41 #best (2) | 4 | 0.036 | 2.36 | 0.046 | 3.9* | 3.1 |
| #41 #rest (3) | 11 | 0.16 | 1.17 | 0.031 | 7.5 | 14.4 |

| Native prediction | Observed | Null | Verdict |
| --- | --- | --- | --- |
| N1a (primary): Spearman(τ_S1, T90) > 0 over the 5 blocks; same sign for t_mix | bge ρ = 0.30 (exact p 0.34), t_mix ρ = 0.10; gte ρ = 0.90 (p 0.04), t_mix ρ = −0.20; depth-5 T90: bge 0.60, gte 0.30 | exact permutation over 5! orders | mixed: positive for coverage in both models (significant only for gte), not for bulk mixing |
| N1b: all-pairs coverage reaches 90% only in #40 | never reaches 90% in any phase: the reachable share of all pairs is 0.57 (#39), 0.87 (#40), 0.58 (#41), because GPT-5 sat alone in #rest during #40 | – | not met as worded (structural); the merge raises reachability 0.57 → 0.87 → 0.58 |
| N1c: τ(#40) vs the A-phase N-weighted mean, same sign as the T90 change | #40 settles slower (bge 20.0 vs 6.7 h; gte 23.1 vs 17.5 h) and covers slower (0.57 vs 0.28 h) | – | met (one contrast, descriptive) |

**Reading.** The direction is weakly read-out-like for coverage (the merged room, with more pairs to cover, settles slower), but the bulk mixing time goes the other way (the merged room's chain mixes fastest), the models disagree on significance, and three of five τ values sit at or beyond the 20-h fit span, so they are poorly determined. With n = 5 and a goal change at every boundary, this is weak evidence. Figure: [`figures/ne42_blocks.pdf`](figures/ne42_blocks.pdf). Data: `data/processed/H48-settling-mixing-time/NE42/` (`blocks.parquet`, `natives.json`).

## Scorecard (period-specific axes)
- **E:** 0–1. The merge is a read-out intervention; τ moves with coverage in sign (N1c) and in rank for gte only (N1a). Not counted as passed.
- **D:** the predicted bulk-mixing ordering fails (t_mix ρ ≤ 0.1).

## Notes
- Room blocks use the day-1 modal room; GPT-5 alone in #rest during #40 is a singleton and excluded.
