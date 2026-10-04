# H103 × G26: which clock the kickoff remanence decays on (2026-01-05 → 2026-01-09)

**Verdict:** failed
**Role:** replication
**Period:** regime I · 10 incumbents · fit days 2026-01-05, 2026-01-06, 2026-01-07, 2026-01-08, 2026-01-09 · 5 non-holdout active days.

## Why this period
The common clock comparison (card O1) on the kickoff remanence of #26, and the two-time night step (O3) on its period units. Regime I: nights rarely start a new context (session or consolidation resets at 6% of first-of-day calls); days are about 3 active h.

## Prediction
*Written 2026-10-04 21:45 UTC, before running on this period (card predictions applied).*
- If the kickoff remanence decays (Δm's CI excludes 0), the active-hour clock fits as well as or better than the night clock (SSE_H ≤ SSE_N): verdict *failed* for HH331 (expected). The night clock wins with the nested night factor λ's CI below 1: *supported*. Otherwise *mixed*; no decay: *descriptive*.
- O3: β_N (night step at fixed active lag) is reported; card-level expectation β_N < 0 at most weakly, β_G ≈ 0, β_gap ≈ 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout).* 33 windows, 10 incumbents, 5 fit days.

| Statistic | bge | gte |
| --- | --- | --- |
| O1 clock fit | winner R; SSE N/H/W/R/0 = 6822.60/6616.46/6651.91/6521.64/10207.59 (×10⁻³); λ 1.50 [1.40, 1.50]; Δm(best) [0.264, 0.528]; P(N beats H) 0.27 | winner R; SSE N/H/W/R/0 = 5547.65/5033.43/5057.39/4994.41/6608.52 (×10⁻³); λ 1.50 [1.35, 1.50]; Δm(best) [0.269, 0.437]; P(N beats H) 0.00 |
| day-1 kickoff excess | 0.219 [0.158, 0.279] | 0.185 |
| night step S_N / day drift D / midday step S_mid | 0.180 / -0.247 / -0.144 | 0.102 / -0.128 / -0.133 |
| O1 verdict | failed | failed |
| O3 unit 26: β_N / β_G / β_gap | -0.0319 [-0.0619, +0.0016] / – / – | -0.0284 [-0.0596, +0.0083] |
| O2 previous-centroid day-1 level | 0.118 [0.077, 0.165]; verdict failed | – |

## Scorecard (period-specific axes)
- **C:** midday-step and slot-effect nulls; **D:** the night step and day drift are unfitted signatures; **F:** synthetic clock-selection at this period's skeleton (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H103-nights-demagnetize/results/o1_*.json` (key G26), `o3_*.json`.
