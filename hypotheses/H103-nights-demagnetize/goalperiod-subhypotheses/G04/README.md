# H103 × G04: which clock the kickoff remanence decays on (2025-05-15 → 2025-06-18)

**Verdict:** descriptive
**Role:** replication
**Period:** regime I · 4 incumbents · fit days 2025-05-15, 2025-05-16, 2025-05-19, 2025-05-20, 2025-05-21 · 25 non-holdout active days.

## Why this period
The common clock comparison (card O1) on the kickoff remanence of #4, and the two-time night step (O3) on its period units. Regime I: nights rarely start a new context (session or consolidation resets at 6% of first-of-day calls); days are about 3 active h.

## Prediction
*Written 2026-10-04 21:45 UTC, before running on this period (card predictions applied).*
- If the kickoff remanence decays (Δm's CI excludes 0), the active-hour clock fits as well as or better than the night clock (SSE_H ≤ SSE_N): verdict *failed* for HH331 (expected). The night clock wins with the nested night factor λ's CI below 1: *supported*. Otherwise *mixed*; no decay: *descriptive*.
- O3: β_N (night step at fixed active lag) is reported; card-level expectation β_N < 0 at most weakly, β_G ≈ 0, β_gap ≈ 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout).* 20 windows, 4 incumbents, 5 fit days.

| Statistic | bge | gte |
| --- | --- | --- |
| O1 clock fit | winner H; SSE N/H/W/R/0 = 311.62/310.66/323.74/317.13/442.49 (×10⁻³); λ 1.30 [0.05, 1.50]; Δm(best) [-506138.773, 5.834]; P(N beats H) 0.28 | winner R; SSE N/H/W/R/0 = 445.26/433.59/459.92/433.28/506.06 (×10⁻³); λ 0.05 [0.05, 1.50]; Δm(best) [-3248631.238, 15.741]; P(N beats H) 0.13 |
| day-1 kickoff excess | 0.177 [-0.039, 0.391] | 0.138 |
| night step S_N / day drift D / midday step S_mid | 0.020 / -0.030 / -0.030 | -0.023 / 0.016 / 0.016 |
| O1 verdict | descriptive | descriptive |
| O3 unit 4a: β_N / β_G / β_gap | +0.1679 [-0.1968, +0.4913] / -0.0598 [-0.1986, +0.0749] / – | +0.2068 [-0.0655, +0.5040] |
| O3 unit 4c: β_N / β_G / β_gap | +0.0823 [-0.1389, +0.3096] / -0.0319 [-0.0533, -0.0127] / – | +0.0447 [-0.1285, +0.2384] |
| O2 previous-centroid day-1 level | 0.112 [-0.115, 0.340]; verdict descriptive | – |

## Scorecard (period-specific axes)
- **C:** midday-step and slot-effect nulls; **D:** the night step and day drift are unfitted signatures; **F:** synthetic clock-selection at this period's skeleton (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H103-nights-demagnetize/results/o1_*.json` (key G04), `o3_*.json`.
