# H103 × G39: which clock the kickoff remanence decays on (2026-04-27 → 2026-05-01)

**Verdict:** failed
**Role:** replication
**Period:** regime III · 14 incumbents · fit days 2026-04-27, 2026-04-28, 2026-04-29, 2026-04-30, 2026-05-01 · 5 non-holdout active days.

## Why this period
The common clock comparison (card O1) on the kickoff remanence of #39, and the two-time night step (O3) on its period units. Regime III: the context carries over the night in most cases, and resets happen every ~41 calls inside the day (NE41); days are 4–8 active h.

## Prediction
*Written 2026-10-04 21:45 UTC, before running on this period (card predictions applied).*
- If the kickoff remanence decays (Δm's CI excludes 0), the active-hour clock fits as well as or better than the night clock (SSE_H ≤ SSE_N): verdict *failed* for HH331 (expected). The night clock wins with the nested night factor λ's CI below 1: *supported*. Otherwise *mixed*; no decay: *descriptive*.
- O3: β_N (night step at fixed active lag) is reported; card-level expectation β_N < 0 at most weakly, β_G ≈ 0, β_gap ≈ 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout).* 40 windows, 14 incumbents, 5 fit days.

| Statistic | bge | gte |
| --- | --- | --- |
| O1 clock fit | winner R; SSE N/H/W/R/0 = 669.10/646.62/666.06/629.16/1049.61 (×10⁻³); λ 1.50 [1.10, 1.50]; Δm(best) [0.081, 2.590]; P(N beats H) 0.02 | winner R; SSE N/H/W/R/0 = 1043.90/1040.40/1043.01/1031.48/1219.07 (×10⁻³); λ 1.50 [0.05, 1.50]; Δm(best) [-0.050, 2327.779]; P(N beats H) 0.14 |
| day-1 kickoff excess | 0.180 [0.140, 0.222] | 0.228 |
| night step S_N / day drift D / midday step S_mid | 0.030 / -0.049 / -0.017 | 0.041 / -0.049 / -0.013 |
| O1 verdict | failed | descriptive |
| O3 unit 39: β_N / β_G / β_gap | -0.0185 [-0.0503, +0.0043] / – / – | -0.0190 [-0.0498, -0.0002] |
| O2 previous-centroid day-1 level | -0.081 [-0.152, -0.016]; verdict descriptive | – |

## Scorecard (period-specific axes)
- **C:** midday-step and slot-effect nulls; **D:** the night step and day drift are unfitted signatures; **F:** synthetic clock-selection at this period's skeleton (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H103-nights-demagnetize/results/o1_*.json` (key G39), `o3_*.json`.
