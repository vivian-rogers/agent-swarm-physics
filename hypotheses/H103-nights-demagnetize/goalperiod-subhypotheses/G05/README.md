# H103 × G05: which clock the kickoff remanence decays on (2025-06-19 → 2025-06-25)

**Verdict:** failed
**Role:** replication
**Period:** regime I · 4 incumbents · fit days 2025-06-19, 2025-06-20, 2025-06-23, 2025-06-24, 2025-06-25 · 5 non-holdout active days.

## Why this period
The common clock comparison (card O1) on the kickoff remanence of #5, and the two-time night step (O3) on its period units. Regime I: nights rarely start a new context (session or consolidation resets at 6% of first-of-day calls); days are about 3 active h.

## Prediction
*Written 2026-10-04 21:45 UTC, before running on this period (card predictions applied).*
- If the kickoff remanence decays (Δm's CI excludes 0), the active-hour clock fits as well as or better than the night clock (SSE_H ≤ SSE_N): verdict *failed* for HH331 (expected). The night clock wins with the nested night factor λ's CI below 1: *supported*. Otherwise *mixed*; no decay: *descriptive*.
- O3: β_N (night step at fixed active lag) is reported; card-level expectation β_N < 0 at most weakly, β_G ≈ 0, β_gap ≈ 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout).* 20 windows, 4 incumbents, 5 fit days.

| Statistic | bge | gte |
| --- | --- | --- |
| O1 clock fit | winner R; SSE N/H/W/R/0 = 295.63/205.90/200.86/198.36/465.08 (×10⁻³); λ 0.05 [0.05, 1.30]; Δm(best) [0.282, 7.102]; P(N beats H) 0.03 | winner W; SSE N/H/W/R/0 = 293.38/340.92/279.00/349.35/693.39 (×10⁻³); λ 0.05 [0.05, 0.20]; Δm(best) [0.152, 0.335]; P(N beats H) 0.94 |
| day-1 kickoff excess | 0.136 [0.098, 0.184] | 0.197 |
| night step S_N / day drift D / midday step S_mid | -0.015 / -0.031 / -0.031 | 0.011 / -0.041 / -0.041 |
| O1 verdict | failed | mixed |
| O3 unit 5: β_N / β_G / β_gap | +2.7975 [+1.3153, +5.0967] / -1.2952 [-2.3343, -0.6278] / – | +1.0737 [+0.1919, +2.3500] |
| O2 previous-centroid day-1 level | 0.373 [0.239, 0.488]; verdict supported | – |

## Scorecard (period-specific axes)
- **C:** midday-step and slot-effect nulls; **D:** the night step and day drift are unfitted signatures; **F:** synthetic clock-selection at this period's skeleton (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H103-nights-demagnetize/results/o1_*.json` (key G05), `o3_*.json`.
