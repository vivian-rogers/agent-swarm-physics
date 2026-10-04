# H131 × G26: the election (#26, 2026-01-05 → 2026-01-12)

**Verdict:** mixed
**Role:** exploratory (replication + native N4)
**Period:** regime I · mode C · 10 agents · an approval vote, a three-way runoff (agents 0, 6, 17) and its result message (2026-01-05 19:35:22 UTC), then a confirmatory vote (01-09).

## Why this period
The second non-holdout period with a DQ6-dated settlement of a rival-exclusive prize (the runoff result) and named rivals (the three runoff candidates).

## Prediction
*Written 2026-10-04 ~22:25 UTC, before running on this period.*
Structural facts seen before writing (no stance values): result read delays 2–83 s; within ±3 h of the result, 14 rival replies before and 41 after; **0 in-flight rival replies**.
- **P1 (replication, read-aligned DiD):** expected inconclusive (14 open rival replies; H64's synthetic power ≤ 0.33 at 2 logit). Inconclusive unless γ_open's permutation p < 0.05. Credence that it passes: 0.1.
- **N4:** runoff rivals' flag rate falls after each one's read of the result; expected inconclusive. N1-type in-flight test: untestable (0 in-flight rival replies).

## Result
*Run 2026-10-04 ~23:03 UTC, after Amendment A1. Synthetic power of P1 here: 0.11.*

| Prediction | Observed (95% CI) | Null | Verdict |
| --- | --- | --- | --- |
| P1 read-gated DiD | Δ −0.01 [−0.04, +0.02]; γ_open +0.01 [−0.01, +0.03] | rival-set permutation p 0.72 | inconclusive (low power) |
| N4 / in-flight | 0 in-flight rival replies (13 in-flight non-rival replies) | — | untestable |

Cell counts (flag): runoff rivals while open 0/14, others while open 0/91, rivals after their read 1/65, others after 5/609. The period has almost no validated disagreement (6 flags in 779 replies), so there is no antagonism to switch off. The verdict line reads "mixed" because the period-level rule has no "inconclusive" value.

## Scorecard (period-specific axes)
- **C: 0.** Underpowered.
- **G: 1.** DQ6 result message and runoff candidates.
