# H103 × G27: which clock the kickoff remanence decays on (2026-01-12 → 2026-01-23)

**Verdict:** failed
**Role:** replication
**Period:** regime I · 10 incumbents · fit days 2026-01-12, 2026-01-13, 2026-01-14, 2026-01-15, 2026-01-16 · 10 non-holdout active days.

## Why this period
The common clock comparison (card O1) on the kickoff remanence of #27, and the two-time night step (O3) on its period units. Regime I: nights rarely start a new context (session or consolidation resets at 6% of first-of-day calls); days are about 3 active h.

## Prediction
*Written 2026-10-04 21:45 UTC, before running on this period (card predictions applied).*
- If the kickoff remanence decays (Δm's CI excludes 0), the active-hour clock fits as well as or better than the night clock (SSE_H ≤ SSE_N): verdict *failed* for HH331 (expected). The night clock wins with the nested night factor λ's CI below 1: *supported*. Otherwise *mixed*; no decay: *descriptive*.
- O3: β_N (night step at fixed active lag) is reported; card-level expectation β_N < 0 at most weakly, β_G ≈ 0, β_gap ≈ 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout).* 40 windows, 10 incumbents, 5 fit days.

| Statistic | bge | gte |
| --- | --- | --- |
| O1 clock fit | winner H; SSE N/H/W/R/0 = 772.66/744.42/769.52/747.48/1172.48 (×10⁻³); λ 1.40 [1.10, 1.50]; Δm(best) [0.095, 2.066]; P(N beats H) 0.03 | winner H; SSE N/H/W/R/0 = 823.24/741.28/811.16/758.19/1483.20 (×10⁻³); λ 1.50 [0.05, 1.50]; Δm(best) [0.160, 0.273]; P(N beats H) 0.01 |
| day-1 kickoff excess | 0.500 [0.459, 0.538] | 0.428 |
| night step S_N / day drift D / midday step S_mid | 0.085 / -0.102 / -0.005 | 0.048 / -0.071 / -0.017 |
| O1 verdict | failed | failed |
| O3 unit 27: β_N / β_G / β_gap | +0.0021 [-0.0210, +0.0270] / -0.0527 [-0.0818, -0.0211] / – | +0.0116 [-0.0033, +0.0302] |
| O2 previous-centroid day-1 level | 0.097 [0.062, 0.135]; verdict descriptive | – |

## Scorecard (period-specific axes)
- **C:** midday-step and slot-effect nulls; **D:** the night step and day drift are unfitted signatures; **F:** synthetic clock-selection at this period's skeleton (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H103-nights-demagnetize/results/o1_*.json` (key G27), `o3_*.json`.
