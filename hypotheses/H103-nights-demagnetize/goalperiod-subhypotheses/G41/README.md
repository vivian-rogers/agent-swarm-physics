# H103 × G41: which clock the kickoff remanence decays on (2026-05-11 → 2026-05-15)

**Verdict:** failed
**Role:** replication
**Period:** regime III · 15 incumbents · fit days 2026-05-11, 2026-05-12, 2026-05-13, 2026-05-14, 2026-05-15 · 5 non-holdout active days.

## Why this period
The common clock comparison (card O1) on the kickoff remanence of #41, and the two-time night step (O3) on its period units. Regime III: the context carries over the night in most cases, and resets happen every ~41 calls inside the day (NE41); days are 4–8 active h.

## Prediction
*Written 2026-10-04 21:45 UTC, before running on this period (card predictions applied).*
- If the kickoff remanence decays (Δm's CI excludes 0), the active-hour clock fits as well as or better than the night clock (SSE_H ≤ SSE_N): verdict *failed* for HH331 (expected). The night clock wins with the nested night factor λ's CI below 1: *supported*. Otherwise *mixed*; no decay: *descriptive*.
- O3: β_N (night step at fixed active lag) is reported; card-level expectation β_N < 0 at most weakly, β_G ≈ 0, β_gap ≈ 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout).* 40 windows, 15 incumbents, 5 fit days.

| Statistic | bge | gte |
| --- | --- | --- |
| O1 clock fit | winner R; SSE N/H/W/R/0 = 1276.46/1212.71/1255.98/1203.42/2828.43 (×10⁻³); λ 1.05 [0.40, 1.50]; Δm(best) [0.126, 0.278]; P(N beats H) 0.17 | winner R; SSE N/H/W/R/0 = 1087.31/1033.78/1074.45/966.13/4312.25 (×10⁻³); λ 1.10 [0.60, 1.50]; Δm(best) [0.216, 0.914]; P(N beats H) 0.13 |
| day-1 kickoff excess | 0.162 [0.140, 0.184] | 0.223 |
| night step S_N / day drift D / midday step S_mid | -0.008 / -0.001 / 0.002 | 0.011 / -0.052 / -0.006 |
| O1 verdict | failed | failed |
| O3 unit 41: β_N / β_G / β_gap | -0.0176 [-0.0526, +0.0344] / – / +0.1693 [+0.1486, +0.1925] | -0.0468 [-0.0839, -0.0010] |
| O2 previous-centroid day-1 level | -0.104 [-0.158, -0.039]; verdict descriptive | – |

## Scorecard (period-specific axes)
- **C:** midday-step and slot-effect nulls; **D:** the night step and day drift are unfitted signatures; **F:** synthetic clock-selection at this period's skeleton (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H103-nights-demagnetize/results/o1_*.json` (key G41), `o3_*.json`.
