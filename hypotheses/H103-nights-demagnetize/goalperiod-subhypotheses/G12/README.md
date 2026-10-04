# H103 × G12: which clock the kickoff remanence decays on (2025-09-01 → 2025-09-05)

**Verdict:** failed
**Role:** replication
**Period:** regime I · 7 incumbents · fit days 2025-09-01, 2025-09-02, 2025-09-03, 2025-09-04, 2025-09-05 · 5 non-holdout active days.

## Why this period
The common clock comparison (card O1) on the kickoff remanence of #12, and the two-time night step (O3) on its period units. Regime I: nights rarely start a new context (session or consolidation resets at 6% of first-of-day calls); days are about 3 active h.

## Prediction
*Written 2026-10-04 21:45 UTC, before running on this period (card predictions applied).*
- If the kickoff remanence decays (Δm's CI excludes 0), the active-hour clock fits as well as or better than the night clock (SSE_H ≤ SSE_N): verdict *failed* for HH331 (expected). The night clock wins with the nested night factor λ's CI below 1: *supported*. Otherwise *mixed*; no decay: *descriptive*.
- O3: β_N (night step at fixed active lag) is reported; card-level expectation β_N < 0 at most weakly, β_G ≈ 0, β_gap ≈ 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout).* 30 windows, 7 incumbents, 5 fit days.

| Statistic | bge | gte |
| --- | --- | --- |
| O1 clock fit | winner R; SSE N/H/W/R/0 = 5490.60/5436.85/5470.54/5324.30/10701.97 (×10⁻³); λ 1.50 [1.05, 1.50]; Δm(best) [0.516, 27.266]; P(N beats H) 0.01 | winner R; SSE N/H/W/R/0 = 5566.48/5512.25/5550.85/5429.07/11189.53 (×10⁻³); λ 1.50 [0.75, 1.50]; Δm(best) [0.545, 27.789]; P(N beats H) 0.01 |
| day-1 kickoff excess | 0.565 [0.493, 0.624] | 0.570 |
| night step S_N / day drift D / midday step S_mid | -0.065 / -0.051 / 0.001 | -0.112 / -0.016 / 0.002 |
| O1 verdict | failed | failed |
| O3 unit 12a: β_N / β_G / β_gap | -0.0759 [-0.1413, -0.0118] / – / – | -0.1001 [-0.1558, -0.0458] |
| O2 previous-centroid day-1 level | 0.114 [0.044, 0.198]; verdict descriptive | – |

## Scorecard (period-specific axes)
- **C:** midday-step and slot-effect nulls; **D:** the night step and day drift are unfitted signatures; **F:** synthetic clock-selection at this period's skeleton (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H103-nights-demagnetize/results/o1_*.json` (key G12), `o3_*.json`.
