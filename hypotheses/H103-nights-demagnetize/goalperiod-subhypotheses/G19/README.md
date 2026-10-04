# H103 × G19: which clock the kickoff remanence decays on (2025-11-03 → 2025-11-14)

**Verdict:** failed
**Role:** replication
**Period:** regime I · 7 incumbents · fit days 2025-11-03, 2025-11-04, 2025-11-05, 2025-11-06, 2025-11-07 · 10 non-holdout active days.

## Why this period
The common clock comparison (card O1) on the kickoff remanence of #19, and the two-time night step (O3) on its period units. Regime I: nights rarely start a new context (session or consolidation resets at 6% of first-of-day calls); days are about 3 active h.

## Prediction
*Written 2026-10-04 21:45 UTC, before running on this period (card predictions applied).*
- If the kickoff remanence decays (Δm's CI excludes 0), the active-hour clock fits as well as or better than the night clock (SSE_H ≤ SSE_N): verdict *failed* for HH331 (expected). The night clock wins with the nested night factor λ's CI below 1: *supported*. Otherwise *mixed*; no decay: *descriptive*.
- O3: β_N (night step at fixed active lag) is reported; card-level expectation β_N < 0 at most weakly, β_G ≈ 0, β_gap ≈ 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout).* 40 windows, 7 incumbents, 5 fit days.

| Statistic | bge | gte |
| --- | --- | --- |
| O1 clock fit | winner R; SSE N/H/W/R/0 = 1442.30/873.92/876.86/862.85/2128.15 (×10⁻³); λ 1.50 [1.50, 1.50]; Δm(best) [0.468, 0.692]; P(N beats H) 0.00 | winner R; SSE N/H/W/R/0 = 2311.89/2019.21/2018.22/2014.67/2656.65 (×10⁻³); λ 0.05 [0.05, 0.05]; Δm(best) [0.243, 0.748]; P(N beats H) 0.00 |
| day-1 kickoff excess | 0.169 [0.129, 0.202] | 0.139 |
| night step S_N / day drift D / midday step S_mid | -0.015 / -0.062 / 0.059 | -0.018 / -0.023 / 0.054 |
| O1 verdict | failed | failed |
| O3 unit 19a: β_N / β_G / β_gap | +0.1246 [+0.0335, +0.2092] / -0.0952 [-0.1529, -0.0241] / +0.0308 [-0.0456, +0.2494] | +0.1666 [+0.0752, +0.2470] |
| O2 previous-centroid day-1 level | 0.263 [0.212, 0.330]; verdict descriptive | – |

## Scorecard (period-specific axes)
- **C:** midday-step and slot-effect nulls; **D:** the night step and day drift are unfitted signatures; **F:** synthetic clock-selection at this period's skeleton (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H103-nights-demagnetize/results/o1_*.json` (key G19), `o3_*.json`.
