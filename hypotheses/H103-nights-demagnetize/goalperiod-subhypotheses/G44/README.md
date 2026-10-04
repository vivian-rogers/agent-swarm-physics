# H103 × G44: which clock the kickoff remanence decays on (2026-05-26 → 2026-05-29)

**Verdict:** descriptive
**Role:** replication
**Period:** regime III · 16 incumbents · fit days 2026-05-26, 2026-05-27, 2026-05-28, 2026-05-29 · 4 non-holdout active days.

## Why this period
The common clock comparison (card O1) on the kickoff remanence of #44, and the two-time night step (O3) on its period units. Regime III: the context carries over the night in most cases, and resets happen every ~41 calls inside the day (NE41); days are 4–8 active h.

## Prediction
*Written 2026-10-04 21:45 UTC, before running on this period (card predictions applied).*
- If the kickoff remanence decays (Δm's CI excludes 0), the active-hour clock fits as well as or better than the night clock (SSE_H ≤ SSE_N): verdict *failed* for HH331 (expected). The night clock wins with the nested night factor λ's CI below 1: *supported*. Otherwise *mixed*; no decay: *descriptive*.
- O3: β_N (night step at fixed active lag) is reported; card-level expectation β_N < 0 at most weakly, β_G ≈ 0, β_gap ≈ 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout).* 32 windows, 16 incumbents, 4 fit days.

| Statistic | bge | gte |
| --- | --- | --- |
| O1 clock fit | winner R; SSE N/H/W/R/0 = 352.38/352.63/352.09/346.90/414.33 (×10⁻³); λ 1.50 [0.05, 1.50]; Δm(best) [-0.038, 19.962]; P(N beats H) 0.55 | winner R; SSE N/H/W/R/0 = 463.86/466.20/462.39/423.28/980.37 (×10⁻³); λ 1.50 [1.05, 1.50]; Δm(best) [1.251, 12.218]; P(N beats H) 0.62 |
| day-1 kickoff excess | 0.011 [-0.049, 0.091] | 0.070 |
| night step S_N / day drift D / midday step S_mid | -0.003 / -0.016 / 0.000 | -0.024 / -0.033 / 0.007 |
| O1 verdict | descriptive | mixed |

## Scorecard (period-specific axes)
- **C:** midday-step and slot-effect nulls; **D:** the night step and day drift are unfitted signatures; **F:** synthetic clock-selection at this period's skeleton (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H103-nights-demagnetize/results/o1_*.json` (key G44), `o3_*.json`.
