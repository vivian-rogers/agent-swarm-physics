# H103 × G08: which clock the kickoff remanence decays on (2025-07-18 → 2025-08-12)

**Verdict:** failed
**Role:** replication
**Period:** regime I · 4 incumbents · fit days 2025-07-18, 2025-07-21, 2025-07-22, 2025-07-23, 2025-07-24 · 18 non-holdout active days.

## Why this period
The common clock comparison (card O1) on the kickoff remanence of #8, and the two-time night step (O3) on its period units. Regime I: nights rarely start a new context (session or consolidation resets at 6% of first-of-day calls); days are about 3 active h.

## Prediction
*Written 2026-10-04 21:45 UTC, before running on this period (card predictions applied).*
- If the kickoff remanence decays (Δm's CI excludes 0), the active-hour clock fits as well as or better than the night clock (SSE_H ≤ SSE_N): verdict *failed* for HH331 (expected). The night clock wins with the nested night factor λ's CI below 1: *supported*. Otherwise *mixed*; no decay: *descriptive*.
- O3: β_N (night step at fixed active lag) is reported; card-level expectation β_N < 0 at most weakly, β_G ≈ 0, β_gap ≈ 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout).* 30 windows, 4 incumbents, 5 fit days.

| Statistic | bge | gte |
| --- | --- | --- |
| O1 clock fit | winner R; SSE N/H/W/R/0 = 601.98/456.15/456.48/450.11/899.34 (×10⁻³); λ 1.50 [0.05, 1.50]; Δm(best) [0.417, 1762.434]; P(N beats H) 0.00 | winner R; SSE N/H/W/R/0 = 994.51/739.71/761.31/739.69/1018.25 (×10⁻³); λ 0.05 [0.05, 1.50]; Δm(best) [0.424, 5245040.288]; P(N beats H) 0.00 |
| day-1 kickoff excess | 0.241 [0.170, 0.280] | 0.257 |
| night step S_N / day drift D / midday step S_mid | -0.064 / 0.022 / 0.040 | -0.025 / -0.010 / 0.048 |
| O1 verdict | failed | failed |
| O3 unit 8: β_N / β_G / β_gap | +0.1135 [+0.0550, +0.1555] / -0.0280 [-0.0647, -0.0092] / -0.0402 [-0.2087, +0.0230] | +0.1742 [+0.1127, +0.2150] |
| O2 previous-centroid day-1 level | -0.115 [-0.127, -0.094]; verdict descriptive | – |

## Scorecard (period-specific axes)
- **C:** midday-step and slot-effect nulls; **D:** the night step and day drift are unfitted signatures; **F:** synthetic clock-selection at this period's skeleton (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H103-nights-demagnetize/results/o1_*.json` (key G08), `o3_*.json`.
