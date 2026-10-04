# H103 × G21: which clock the kickoff remanence decays on (2025-12-01 → 2025-12-05)

**Verdict:** failed
**Role:** replication
**Period:** regime I · 8 incumbents · fit days 2025-12-01, 2025-12-02, 2025-12-03, 2025-12-04, 2025-12-05 · 5 non-holdout active days.

## Why this period
The common clock comparison (card O1) on the kickoff remanence of #21, and the two-time night step (O3) on its period units. Regime I: nights rarely start a new context (session or consolidation resets at 6% of first-of-day calls); days are about 3 active h.

## Prediction
*Written 2026-10-04 21:45 UTC, before running on this period (card predictions applied).*
- If the kickoff remanence decays (Δm's CI excludes 0), the active-hour clock fits as well as or better than the night clock (SSE_H ≤ SSE_N): verdict *failed* for HH331 (expected). The night clock wins with the nested night factor λ's CI below 1: *supported*. Otherwise *mixed*; no decay: *descriptive*.
- O3: β_N (night step at fixed active lag) is reported; card-level expectation β_N < 0 at most weakly, β_G ≈ 0, β_gap ≈ 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout).* 40 windows, 8 incumbents, 5 fit days.

| Statistic | bge | gte |
| --- | --- | --- |
| O1 clock fit | winner R; SSE N/H/W/R/0 = 1735.85/1529.29/1688.30/1521.46/3922.30 (×10⁻³); λ 1.50 [0.40, 1.50]; Δm(best) [0.338, 0.575]; P(N beats H) 0.00 | winner H; SSE N/H/W/R/0 = 1786.71/1667.82/1668.68/1679.57/2506.74 (×10⁻³); λ 1.50 [1.40, 1.50]; Δm(best) [0.212, 0.683]; P(N beats H) 0.00 |
| day-1 kickoff excess | 0.385 [0.320, 0.437] | 0.349 |
| night step S_N / day drift D / midday step S_mid | 0.096 / -0.161 / -0.015 | 0.111 / -0.166 / -0.003 |
| O1 verdict | failed | failed |
| O3 unit 21a: β_N / β_G / β_gap | +5.0392 [-0.9208, +10.7494] / – / – | +4.0616 [-0.1082, +7.4009] |
| O2 previous-centroid day-1 level | -0.067 [-0.121, -0.027]; verdict mixed | – |

## Scorecard (period-specific axes)
- **C:** midday-step and slot-effect nulls; **D:** the night step and day drift are unfitted signatures; **F:** synthetic clock-selection at this period's skeleton (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H103-nights-demagnetize/results/o1_*.json` (key G21), `o3_*.json`.
