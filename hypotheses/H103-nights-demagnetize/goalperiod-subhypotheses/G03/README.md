# H103 × G03: which clock the kickoff remanence decays on (2025-05-12 → 2025-05-14)

**Verdict:** descriptive
**Role:** replication
**Period:** regime I · 4 incumbents · fit days 2025-05-12, 2025-05-13, 2025-05-14 · 3 non-holdout active days.

## Why this period
The common clock comparison (card O1) on the kickoff remanence of #3, and the two-time night step (O3) on its period units. Regime I: nights rarely start a new context (session or consolidation resets at 6% of first-of-day calls); days are about 3 active h.

## Prediction
*Written 2026-10-04 21:45 UTC, before running on this period (card predictions applied).*
- If the kickoff remanence decays (Δm's CI excludes 0), the active-hour clock fits as well as or better than the night clock (SSE_H ≤ SSE_N): verdict *failed* for HH331 (expected). The night clock wins with the nested night factor λ's CI below 1: *supported*. Otherwise *mixed*; no decay: *descriptive*.
- O3: β_N (night step at fixed active lag) is reported; card-level expectation β_N < 0 at most weakly, β_G ≈ 0, β_gap ≈ 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout).* 12 windows, 4 incumbents, 3 fit days.

| Statistic | bge | gte |
| --- | --- | --- |
| O1 clock fit | winner R; SSE N/H/W/R/0 = 223.12/208.11/223.00/196.11/262.00 (×10⁻³); λ 0.05 [0.05, 1.50]; Δm(best) [-25.851, 724256.993]; P(N beats H) 0.40 | winner R; SSE N/H/W/R/0 = 144.01/188.46/152.71/119.26/281.08 (×10⁻³); λ 0.05 [0.05, 1.40]; Δm(best) [-1.525, 105.724]; P(N beats H) 0.95 |
| day-1 kickoff excess | -0.148 [-0.208, -0.093] | -0.004 |
| night step S_N / day drift D / midday step S_mid | 0.012 / 0.020 / 0.020 | 0.015 / 0.010 / 0.010 |
| O1 verdict | descriptive | descriptive |
| O3 unit 3: β_N / β_G / β_gap | -0.5385 [-1.5641, +0.7952] / – / – | -0.0039 [-0.7688, +1.0696] |
| O2 previous-centroid day-1 level | -0.111 [-0.188, -0.034]; verdict descriptive | – |

## Scorecard (period-specific axes)
- **C:** midday-step and slot-effect nulls; **D:** the night step and day drift are unfitted signatures; **F:** synthetic clock-selection at this period's skeleton (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H103-nights-demagnetize/results/o1_*.json` (key G03), `o3_*.json`.
