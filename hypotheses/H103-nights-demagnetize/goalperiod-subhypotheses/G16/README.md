# H103 × G16: which clock the kickoff remanence decays on (2025-10-06 → 2025-10-10)

**Verdict:** descriptive
**Role:** replication
**Period:** regime I · 7 incumbents · fit days 2025-10-06, 2025-10-07, 2025-10-08, 2025-10-09, 2025-10-10 · 5 non-holdout active days.

## Why this period
The common clock comparison (card O1) on the kickoff remanence of #16, and the two-time night step (O3) on its period units. Regime I: nights rarely start a new context (session or consolidation resets at 6% of first-of-day calls); days are about 3 active h.

## Prediction
*Written 2026-10-04 21:45 UTC, before running on this period (card predictions applied).*
- If the kickoff remanence decays (Δm's CI excludes 0), the active-hour clock fits as well as or better than the night clock (SSE_H ≤ SSE_N): verdict *failed* for HH331 (expected). The night clock wins with the nested night factor λ's CI below 1: *supported*. Otherwise *mixed*; no decay: *descriptive*.
- O3: β_N (night step at fixed active lag) is reported; card-level expectation β_N < 0 at most weakly, β_G ≈ 0, β_gap ≈ 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout).* 30 windows, 7 incumbents, 5 fit days.

| Statistic | bge | gte |
| --- | --- | --- |
| O1 clock fit | winner R; SSE N/H/W/R/0 = 550.17/557.19/551.60/544.06/879.41 (×10⁻³); λ 0.75 [0.30, 1.35]; Δm(best) [-6.665, -0.038]; P(N beats H) 0.90 | winner N; SSE N/H/W/R/0 = 360.57/364.76/361.30/362.18/400.10 (×10⁻³); λ 0.60 [0.05, 1.50]; Δm(best) [-1.092, 0.177]; P(N beats H) 0.56 |
| day-1 kickoff excess | -0.055 [-0.096, -0.014] | 0.035 |
| night step S_N / day drift D / midday step S_mid | -0.022 / 0.029 / 0.024 | -0.046 / 0.048 / 0.019 |
| O1 verdict | descriptive | descriptive |
| O3 unit 16: β_N / β_G / β_gap | -0.1174 [-0.2635, +0.0368] / – / – | -0.0870 [-0.2152, +0.0715] |

## Scorecard (period-specific axes)
- **C:** midday-step and slot-effect nulls; **D:** the night step and day drift are unfitted signatures; **F:** synthetic clock-selection at this period's skeleton (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H103-nights-demagnetize/results/o1_*.json` (key G16), `o3_*.json`.
