# H103 × G13: which clock the kickoff remanence decays on (2025-09-08 → 2025-09-19)

**Verdict:** failed
**Role:** replication
**Period:** regime I · 6 incumbents · fit days 2025-09-08, 2025-09-09, 2025-09-10, 2025-09-11, 2025-09-12 · 10 non-holdout active days.

## Why this period
The common clock comparison (card O1) on the kickoff remanence of #13, and the two-time night step (O3) on its period units. Regime I: nights rarely start a new context (session or consolidation resets at 6% of first-of-day calls); days are about 3 active h.

## Prediction
*Written 2026-10-04 21:45 UTC, before running on this period (card predictions applied).*
- If the kickoff remanence decays (Δm's CI excludes 0), the active-hour clock fits as well as or better than the night clock (SSE_H ≤ SSE_N): verdict *failed* for HH331 (expected). The night clock wins with the nested night factor λ's CI below 1: *supported*. Otherwise *mixed*; no decay: *descriptive*.
- O3: β_N (night step at fixed active lag) is reported; card-level expectation β_N < 0 at most weakly, β_G ≈ 0, β_gap ≈ 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout).* 30 windows, 6 incumbents, 5 fit days.

| Statistic | bge | gte |
| --- | --- | --- |
| O1 clock fit | winner W; SSE N/H/W/R/0 = 386.73/259.65/259.39/263.43/491.22 (×10⁻³); λ 0.05 [0.05, 1.50]; Δm(best) [0.198, 25476432.487]; P(N beats H) 0.00 | winner W; SSE N/H/W/R/0 = 522.67/445.72/441.62/444.04/737.59 (×10⁻³); λ 0.05 [0.05, 1.50]; Δm(best) [0.189, 5.533]; P(N beats H) 0.00 |
| day-1 kickoff excess | 0.128 [0.067, 0.193] | 0.232 |
| night step S_N / day drift D / midday step S_mid | 0.013 / -0.055 / 0.011 | 0.043 / -0.091 / -0.029 |
| O1 verdict | failed | failed |
| O3 unit 13: β_N / β_G / β_gap | +0.0008 [-0.1144, +0.0893] / -0.0072 [-0.0631, +0.0317] / – | -0.0280 [-0.1423, +0.0744] |
| O2 previous-centroid day-1 level | 0.221 [0.152, 0.300]; verdict mixed | – |

## Scorecard (period-specific axes)
- **C:** midday-step and slot-effect nulls; **D:** the night step and day drift are unfitted signatures; **F:** synthetic clock-selection at this period's skeleton (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H103-nights-demagnetize/results/o1_*.json` (key G13), `o3_*.json`.
