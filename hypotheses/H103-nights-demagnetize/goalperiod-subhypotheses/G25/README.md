# H103 × G25: which clock the kickoff remanence decays on (2025-12-29 → 2026-01-02)

**Verdict:** descriptive
**Role:** replication
**Period:** regime I · 10 incumbents · fit days 2025-12-29, 2025-12-30, 2025-12-31, 2026-01-01, 2026-01-02 · 5 non-holdout active days.

## Why this period
The common clock comparison (card O1) on the kickoff remanence of #25, and the two-time night step (O3) on its period units. Regime I: nights rarely start a new context (session or consolidation resets at 6% of first-of-day calls); days are about 3 active h.

## Prediction
*Written 2026-10-04 21:45 UTC, before running on this period (card predictions applied).*
- If the kickoff remanence decays (Δm's CI excludes 0), the active-hour clock fits as well as or better than the night clock (SSE_H ≤ SSE_N): verdict *failed* for HH331 (expected). The night clock wins with the nested night factor λ's CI below 1: *supported*. Otherwise *mixed*; no decay: *descriptive*.
- O3: β_N (night step at fixed active lag) is reported; card-level expectation β_N < 0 at most weakly, β_G ≈ 0, β_gap ≈ 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout).* 39 windows, 10 incumbents, 5 fit days.

| Statistic | bge | gte |
| --- | --- | --- |
| O1 clock fit | winner W; SSE N/H/W/R/0 = 2169.73/2185.32/2168.07/2197.45/2848.27 (×10⁻³); λ 1.45 [1.00, 1.50]; Δm(best) [-5.914, 0.249]; P(N beats H) 0.89 | winner H; SSE N/H/W/R/0 = 1146.31/1135.68/1136.17/1142.98/1313.29 (×10⁻³); λ 1.50 [0.05, 1.50]; Δm(best) [-0.002, 0.171]; P(N beats H) 0.34 |
| day-1 kickoff excess | 0.166 [0.130, 0.196] | 0.324 |
| night step S_N / day drift D / midday step S_mid | 0.060 / -0.059 / -0.023 | 0.068 / -0.072 / -0.033 |
| O1 verdict | descriptive | descriptive |
| O3 unit 25: β_N / β_G / β_gap | -0.0744 [-0.0979, -0.0512] / – / +0.1326 [+0.1061, +0.1673] | -0.0912 [-0.1148, -0.0744] |
| O2 previous-centroid day-1 level | -0.017 [-0.066, 0.017]; verdict supported | – |

## Scorecard (period-specific axes)
- **C:** midday-step and slot-effect nulls; **D:** the night step and day drift are unfitted signatures; **F:** synthetic clock-selection at this period's skeleton (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H103-nights-demagnetize/results/o1_*.json` (key G25), `o3_*.json`.
