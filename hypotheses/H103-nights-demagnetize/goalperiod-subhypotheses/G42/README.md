# H103 × G42: which clock the kickoff remanence decays on (2026-05-18 → 2026-05-22)

**Verdict:** failed
**Role:** replication
**Period:** regime III · 15 incumbents · fit days 2026-05-18, 2026-05-19, 2026-05-20, 2026-05-21, 2026-05-22 · 5 non-holdout active days.

## Why this period
The common clock comparison (card O1) on the kickoff remanence of #42, and the two-time night step (O3) on its period units. Regime III: the context carries over the night in most cases, and resets happen every ~41 calls inside the day (NE41); days are 4–8 active h.

## Prediction
*Written 2026-10-04 21:45 UTC, before running on this period (card predictions applied).*
- If the kickoff remanence decays (Δm's CI excludes 0), the active-hour clock fits as well as or better than the night clock (SSE_H ≤ SSE_N): verdict *failed* for HH331 (expected). The night clock wins with the nested night factor λ's CI below 1: *supported*. Otherwise *mixed*; no decay: *descriptive*.
- O3: β_N (night step at fixed active lag) is reported; card-level expectation β_N < 0 at most weakly, β_G ≈ 0, β_gap ≈ 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout).* 40 windows, 15 incumbents, 5 fit days.

| Statistic | bge | gte |
| --- | --- | --- |
| O1 clock fit | winner H; SSE N/H/W/R/0 = 729.84/701.94/719.14/710.03/1259.86 (×10⁻³); λ 1.45 [0.05, 1.50]; Δm(best) [0.052, 2.317]; P(N beats H) 0.38 | winner W; SSE N/H/W/R/0 = 334.27/450.25/328.52/458.31/1208.85 (×10⁻³); λ 0.05 [0.05, 1.40]; Δm(best) [0.077, 0.254]; P(N beats H) 0.85 |
| day-1 kickoff excess | 0.386 [0.351, 0.413] | 0.420 |
| night step S_N / day drift D / midday step S_mid | -0.008 / 0.004 / 0.024 | -0.017 / -0.001 / 0.015 |
| O1 verdict | failed | mixed |
| O3 unit 42b: β_N / β_G / β_gap | -0.0668 [-0.1499, +0.0035] / – / – | -0.0460 [-0.1361, +0.0154] |
| O2 previous-centroid day-1 level | 0.083 [0.025, 0.136]; verdict descriptive | – |

## Scorecard (period-specific axes)
- **C:** midday-step and slot-effect nulls; **D:** the night step and day drift are unfitted signatures; **F:** synthetic clock-selection at this period's skeleton (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H103-nights-demagnetize/results/o1_*.json` (key G42), `o3_*.json`.
