# H103 × G37: which clock the kickoff remanence decays on (2026-03-30 → 2026-04-01)

**Verdict:** mixed
**Role:** replication
**Period:** regime III · 12 incumbents · fit days 2026-03-30, 2026-03-31, 2026-04-01 · 3 non-holdout active days.

## Why this period
The common clock comparison (card O1) on the kickoff remanence of #37, and the two-time night step (O3) on its period units. Regime III: the context carries over the night in most cases, and resets happen every ~41 calls inside the day (NE41); days are 4–8 active h.

## Prediction
*Written 2026-10-04 21:45 UTC, before running on this period (card predictions applied).*
- If the kickoff remanence decays (Δm's CI excludes 0), the active-hour clock fits as well as or better than the night clock (SSE_H ≤ SSE_N): verdict *failed* for HH331 (expected). The night clock wins with the nested night factor λ's CI below 1: *supported*. Otherwise *mixed*; no decay: *descriptive*.
- O3: β_N (night step at fixed active lag) is reported; card-level expectation β_N < 0 at most weakly, β_G ≈ 0, β_gap ≈ 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout).* 24 windows, 12 incumbents, 3 fit days.

| Statistic | bge | gte |
| --- | --- | --- |
| O1 clock fit | winner N; SSE N/H/W/R/0 = 201.29/220.41/204.46/231.45/523.37 (×10⁻³); λ 1.10 [0.05, 1.50]; Δm(best) [0.070, 6.803]; P(N beats H) 0.72 | winner N; SSE N/H/W/R/0 = 262.22/277.62/267.45/329.45/836.53 (×10⁻³); λ 0.70 [0.05, 1.35]; Δm(best) [0.117, 7.358]; P(N beats H) 0.93 |
| day-1 kickoff excess | 0.062 [0.009, 0.102] | 0.169 |
| night step S_N / day drift D / midday step S_mid | -0.023 / -0.012 / -0.003 | -0.015 / -0.052 / -0.001 |
| O1 verdict | mixed | mixed |
| O3 unit 37: β_N / β_G / β_gap | -0.0016 [-0.0525, +0.0645] / – / -0.0373 [-0.0912, +0.0209] | +0.0214 [-0.0221, +0.0718] |
| O2 previous-centroid day-1 level | 0.060 [-0.036, 0.174]; verdict descriptive | – |

## Scorecard (period-specific axes)
- **C:** midday-step and slot-effect nulls; **D:** the night step and day drift are unfitted signatures; **F:** synthetic clock-selection at this period's skeleton (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H103-nights-demagnetize/results/o1_*.json` (key G37), `o3_*.json`.
