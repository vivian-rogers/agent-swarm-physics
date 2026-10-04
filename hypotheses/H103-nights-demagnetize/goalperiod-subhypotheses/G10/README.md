# H103 × G10: which clock the kickoff remanence decays on (2025-08-18 → 2025-08-22)

**Verdict:** failed
**Role:** replication
**Period:** regime I · 7 incumbents · fit days 2025-08-18, 2025-08-19, 2025-08-20, 2025-08-21, 2025-08-22 · 5 non-holdout active days.

## Why this period
The common clock comparison (card O1) on the kickoff remanence of #10, and the two-time night step (O3) on its period units. Regime I: nights rarely start a new context (session or consolidation resets at 6% of first-of-day calls); days are about 3 active h.

## Prediction
*Written 2026-10-04 21:45 UTC, before running on this period (card predictions applied).*
- If the kickoff remanence decays (Δm's CI excludes 0), the active-hour clock fits as well as or better than the night clock (SSE_H ≤ SSE_N): verdict *failed* for HH331 (expected). The night clock wins with the nested night factor λ's CI below 1: *supported*. Otherwise *mixed*; no decay: *descriptive*.
- O3: β_N (night step at fixed active lag) is reported; card-level expectation β_N < 0 at most weakly, β_G ≈ 0, β_gap ≈ 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout).* 29 windows, 7 incumbents, 5 fit days.

| Statistic | bge | gte |
| --- | --- | --- |
| O1 clock fit | winner H; SSE N/H/W/R/0 = 352.92/249.86/264.65/254.63/751.63 (×10⁻³); λ 1.50 [0.05, 1.50]; Δm(best) [0.153, 0.798]; P(N beats H) 0.00 | winner R; SSE N/H/W/R/0 = 518.88/388.89/464.90/386.25/1110.29 (×10⁻³); λ 1.50 [0.45, 1.50]; Δm(best) [0.167, 1.229]; P(N beats H) 0.00 |
| day-1 kickoff excess | 0.346 [0.253, 0.412] | 0.318 |
| night step S_N / day drift D / midday step S_mid | 0.074 / -0.117 / -0.050 | 0.112 / -0.154 / -0.096 |
| O1 verdict | failed | failed |
| O3 unit 10b: β_N / β_G / β_gap | -0.0193 [-0.1409, +0.0953] / – / – | +0.0285 [-0.0893, +0.1615] |

## Scorecard (period-specific axes)
- **C:** midday-step and slot-effect nulls; **D:** the night step and day drift are unfitted signatures; **F:** synthetic clock-selection at this period's skeleton (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H103-nights-demagnetize/results/o1_*.json` (key G10), `o3_*.json`.
