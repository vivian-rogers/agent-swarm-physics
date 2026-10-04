# H111 × NE42: room merge and split at a fixed roster (#39 → #40 → #41, 2026-04-27 → 05-15)

**Verdict:** failed
**Role:** native (exploratory)
**Period:** goals #39 (two rooms), #40 (one merged room; GPT-5 alone in #rest), #41 (two rooms again) · 15 agents · regime III · 5 days each. Units 39, 40, 41.

## Why this period
An A-B-A change of room structure at a fixed roster. H67 measured the read-out loop gain g_lag 0.144 → 0.003 → 0.189 across it. The sum rule turns this into a parameter-free prediction for the collective Fano ratio: Φ_pred ≈ 1.36 → 1.01 → 1.49 (room-adjusted values computed in the run). A shared field that does not depend on reading (the #40 joint objective, the schedule) should not follow g_lag.

## Prediction
*Written 2026-10-04 21:30 UTC, before running on these periods. Seen: H67's, H25's and H99's NE42 results (g_lag and g_eq collapse in #40; g_χ falls by 0.13–0.22). No H111 statistic.*
- **N42a (sum rule):** Φ_obs(15) in #40 is below the mean of #39 and #41 by at least half of the predicted drop Φ_pred(#39, #41 mean) − Φ_pred(#40). [0.35]
- **N42b (excess is a field):** the sum-rule excess Δ_F = Φ_obs − Φ_pred changes by less than 0.2 between #40 and the mean of #39 and #41 (a field independent of reading). [0.4]
- **Counts against the sum rule:** Φ_obs(#40) ≥ the mean of #39 and #41 (talk co-varies as much without read-out coupling).

## Result
*Run 2026-10-04 ~21:45 UTC (per-call clock, T = 10 min, Amendment A1).*

| Unit | H67 g_lag | Φ_pred | Φ(10) [95%] | Φ(10) wall | r_F | Δ_F |
| --- | --- | --- | --- | --- | --- | --- |
| #39 | 0.144 | 1.35 | 1.12 [0.72, 1.49] | 1.06 | 0.83 | -0.23 |
| #40 | 0.003 | 1.01 | 1.24 [0.90, 1.59] | 1.23 | 1.24 | +0.24 |
| #41 | 0.189 | 1.49 | 1.28 [0.94, 1.66] | 1.62 | 0.86 | -0.21 |

- **N42a** (Φ falls in #40 by ≥ half the predicted drop): predicted drop 0.41, observed -0.04. **Failed.**
- **N42b** (excess constant within 0.2): Δ_F changes by +0.46. **Failed.**
- **Reading:** collective talk variance does not follow the read-out gain across the merge. In #40, where H67 finds no read-out coupling, Φ(10) stays at 1.24 [0.90, 1.59]: about 0.24 of excess the read-out loop does not explain, during a week with a shared joint objective (a goal field). The per-unit CIs are ±0.35, so a drop of 0.41 is about 1.5 SE from what was seen: the failure is real but weak.

## Scorecard (period-specific axes)
E: the change across the merge and split.

## Notes
