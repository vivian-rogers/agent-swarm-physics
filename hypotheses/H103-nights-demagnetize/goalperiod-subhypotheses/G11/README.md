# H103 × G11: which clock the kickoff remanence decays on (2025-08-25 → 2025-08-29)

**Verdict:** mixed
**Role:** replication
**Period:** regime I · 7 incumbents · fit days 2025-08-25, 2025-08-26, 2025-08-27, 2025-08-28, 2025-08-29 · 5 non-holdout active days.

## Why this period
The common clock comparison (card O1) on the kickoff remanence of #11, and the two-time night step (O3) on its period units. Regime I: nights rarely start a new context (session or consolidation resets at 6% of first-of-day calls); days are about 3 active h.

## Prediction
*Written 2026-10-04 21:45 UTC, before running on this period (card predictions applied).*
- If the kickoff remanence decays (Δm's CI excludes 0), the active-hour clock fits as well as or better than the night clock (SSE_H ≤ SSE_N): verdict *failed* for HH331 (expected). The night clock wins with the nested night factor λ's CI below 1: *supported*. Otherwise *mixed*; no decay: *descriptive*.
- O3: β_N (night step at fixed active lag) is reported; card-level expectation β_N < 0 at most weakly, β_G ≈ 0, β_gap ≈ 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout).* 30 windows, 7 incumbents, 5 fit days.

| Statistic | bge | gte |
| --- | --- | --- |
| O1 clock fit | winner N; SSE N/H/W/R/0 = 251.70/262.30/253.01/256.81/377.58 (×10⁻³); λ 1.05 [0.55, 1.50]; Δm(best) [0.056, 3.364]; P(N beats H) 0.89 | winner H; SSE N/H/W/R/0 = 363.67/362.57/363.44/362.79/368.66 (×10⁻³); λ 1.45 [0.05, 1.50]; Δm(best) [-154236.072, 0.032]; P(N beats H) 0.33 |
| day-1 kickoff excess | 0.026 [-0.018, 0.079] | -0.017 |
| night step S_N / day drift D / midday step S_mid | -0.034 / 0.014 / 0.003 | -0.010 / -0.001 / -0.010 |
| O1 verdict | mixed | descriptive |
| O3 unit 11: β_N / β_G / β_gap | +0.2058 [+0.1366, +0.2708] / – / +0.2571 [+0.1410, +0.3345] | +0.2050 [+0.1421, +0.2803] |
| O2 previous-centroid day-1 level | 0.223 [0.064, 0.353]; verdict descriptive | – |

## Scorecard (period-specific axes)
- **C:** midday-step and slot-effect nulls; **D:** the night step and day drift are unfitted signatures; **F:** synthetic clock-selection at this period's skeleton (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H103-nights-demagnetize/results/o1_*.json` (key G11), `o3_*.json`.
