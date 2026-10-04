# H103 × G40: which clock the kickoff remanence decays on (2026-05-04 → 2026-05-08)

**Verdict:** mixed
**Role:** replication
**Period:** regime III · 15 incumbents · fit days 2026-05-04, 2026-05-05, 2026-05-06, 2026-05-07, 2026-05-08 · 5 non-holdout active days.

## Why this period
The common clock comparison (card O1) on the kickoff remanence of #40, and the two-time night step (O3) on its period units. Regime III: the context carries over the night in most cases, and resets happen every ~41 calls inside the day (NE41); days are 4–8 active h.

## Prediction
*Written 2026-10-04 21:45 UTC, before running on this period (card predictions applied).*
- If the kickoff remanence decays (Δm's CI excludes 0), the active-hour clock fits as well as or better than the night clock (SSE_H ≤ SSE_N): verdict *failed* for HH331 (expected). The night clock wins with the nested night factor λ's CI below 1: *supported*. Otherwise *mixed*; no decay: *descriptive*.
- O3: β_N (night step at fixed active lag) is reported; card-level expectation β_N < 0 at most weakly, β_G ≈ 0, β_gap ≈ 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout).* 40 windows, 15 incumbents, 5 fit days.

| Statistic | bge | gte |
| --- | --- | --- |
| O1 clock fit | winner N; SSE N/H/W/R/0 = 542.89/581.19/549.63/583.74/1797.65 (×10⁻³); λ 0.75 [0.35, 1.15]; Δm(best) [0.089, 8.214]; P(N beats H) 0.94 | winner N; SSE N/H/W/R/0 = 609.50/646.81/610.93/622.92/2259.50 (×10⁻³); λ 0.55 [0.20, 1.05]; Δm(best) [0.106, 6.936]; P(N beats H) 0.87 |
| day-1 kickoff excess | 0.484 [0.417, 0.546] | 0.472 |
| night step S_N / day drift D / midday step S_mid | 0.036 / -0.063 / -0.035 | 0.034 / -0.075 / -0.031 |
| O1 verdict | mixed | mixed |
| O3 unit 40: β_N / β_G / β_gap | -0.0567 [-0.1165, +0.0062] / – / – | -0.0727 [-0.1412, -0.0081] |
| O2 previous-centroid day-1 level | 0.290 [0.220, 0.346]; verdict failed | – |

## Scorecard (period-specific axes)
- **C:** midday-step and slot-effect nulls; **D:** the night step and day drift are unfitted signatures; **F:** synthetic clock-selection at this period's skeleton (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H103-nights-demagnetize/results/o1_*.json` (key G40), `o3_*.json`.
