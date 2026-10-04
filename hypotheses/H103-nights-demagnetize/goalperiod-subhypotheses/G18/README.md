# H103 × G18: which clock the kickoff remanence decays on (2025-10-20 → 2025-10-31)

**Verdict:** failed
**Role:** replication
**Period:** regime I · 7 incumbents · fit days 2025-10-20, 2025-10-21, 2025-10-22, 2025-10-23, 2025-10-24 · 10 non-holdout active days.

## Why this period
The common clock comparison (card O1) on the kickoff remanence of #18, and the two-time night step (O3) on its period units. Regime I: nights rarely start a new context (session or consolidation resets at 6% of first-of-day calls); days are about 3 active h.

## Prediction
*Written 2026-10-04 21:45 UTC, before running on this period (card predictions applied).*
- If the kickoff remanence decays (Δm's CI excludes 0), the active-hour clock fits as well as or better than the night clock (SSE_H ≤ SSE_N): verdict *failed* for HH331 (expected). The night clock wins with the nested night factor λ's CI below 1: *supported*. Otherwise *mixed*; no decay: *descriptive*.
- O3: β_N (night step at fixed active lag) is reported; card-level expectation β_N < 0 at most weakly, β_G ≈ 0, β_gap ≈ 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout).* 36 windows, 7 incumbents, 5 fit days.

| Statistic | bge | gte |
| --- | --- | --- |
| O1 clock fit | winner W; SSE N/H/W/R/0 = 1117.48/1019.82/1007.02/1058.47/1514.11 (×10⁻³); λ 0.10 [0.05, 1.50]; Δm(best) [0.170, 0.301]; P(N beats H) 0.03 | winner R; SSE N/H/W/R/0 = 3398.15/3351.18/3375.58/3302.94/5812.96 (×10⁻³); λ 0.75 [0.45, 1.45]; Δm(best) [0.321, 0.491]; P(N beats H) 0.18 |
| day-1 kickoff excess | 0.229 [0.187, 0.262] | 0.331 |
| night step S_N / day drift D / midday step S_mid | 0.046 / -0.081 / -0.042 | -0.044 / 0.011 / -0.045 |
| O1 verdict | failed | failed |
| O3 unit 18b: β_N / β_G / β_gap | -0.1940 [-0.3005, -0.0751] / -0.0031 [-0.0483, +0.0581] / – | -0.2524 [-0.3603, -0.1686] |
| O3 unit 18c: β_N / β_G / β_gap | -0.0342 [-0.1019, +0.0428] / – / – | -0.0971 [-0.1811, -0.0072] |
| O2 previous-centroid day-1 level | 0.008 [-0.061, 0.075]; verdict descriptive | – |

## Scorecard (period-specific axes)
- **C:** midday-step and slot-effect nulls; **D:** the night step and day drift are unfitted signatures; **F:** synthetic clock-selection at this period's skeleton (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H103-nights-demagnetize/results/o1_*.json` (key G18), `o3_*.json`.
