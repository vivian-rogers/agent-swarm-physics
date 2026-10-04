# H103 × G17: which clock the kickoff remanence decays on (2025-10-13 → 2025-10-17)

**Verdict:** descriptive
**Role:** replication
**Period:** regime I · 7 incumbents · fit days 2025-10-13, 2025-10-14, 2025-10-15, 2025-10-16, 2025-10-17 · 5 non-holdout active days.

## Why this period
The common clock comparison (card O1) on the kickoff remanence of #17, and the two-time night step (O3) on its period units. Regime I: nights rarely start a new context (session or consolidation resets at 6% of first-of-day calls); days are about 3 active h.

## Prediction
*Written 2026-10-04 21:45 UTC, before running on this period (card predictions applied).*
- If the kickoff remanence decays (Δm's CI excludes 0), the active-hour clock fits as well as or better than the night clock (SSE_H ≤ SSE_N): verdict *failed* for HH331 (expected). The night clock wins with the nested night factor λ's CI below 1: *supported*. Otherwise *mixed*; no decay: *descriptive*.
- O3: β_N (night step at fixed active lag) is reported; card-level expectation β_N < 0 at most weakly, β_G ≈ 0, β_gap ≈ 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout).* 30 windows, 7 incumbents, 5 fit days.

| Statistic | bge | gte |
| --- | --- | --- |
| O1 clock fit | winner R; SSE N/H/W/R/0 = 2817.65/2790.03/2805.99/2789.90/2862.32 (×10⁻³); λ 1.35 [1.25, 1.50]; Δm(best) [-2.477, 21726399.549]; P(N beats H) 0.17 | winner R; SSE N/H/W/R/0 = 3222.29/3042.09/3107.62/3041.20/3249.52 (×10⁻³); λ 1.40 [0.05, 1.50]; Δm(best) [-1.744, 39225851.415]; P(N beats H) 0.01 |
| day-1 kickoff excess | 0.242 [0.144, 0.350] | 0.259 |
| night step S_N / day drift D / midday step S_mid | 0.095 / -0.082 / -0.028 | 0.115 / -0.107 / -0.029 |
| O1 verdict | descriptive | descriptive |
| O3 unit 17: β_N / β_G / β_gap | -0.0610 [-0.1352, +0.0287] / – / – | -0.0903 [-0.1811, +0.0121] |
| O2 previous-centroid day-1 level | 0.019 [-0.057, 0.082]; verdict descriptive | – |

## Scorecard (period-specific axes)
- **C:** midday-step and slot-effect nulls; **D:** the night step and day drift are unfitted signatures; **F:** synthetic clock-selection at this period's skeleton (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H103-nights-demagnetize/results/o1_*.json` (key G17), `o3_*.json`.
