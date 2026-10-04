# H103 × G38: which clock the kickoff remanence decays on (2026-04-02 → 2026-04-24)

**Verdict:** descriptive
**Role:** replication
**Period:** regime III · 12 incumbents · fit days 2026-04-02, 2026-04-03, 2026-04-06, 2026-04-07, 2026-04-08 · 17 non-holdout active days.

## Why this period
The common clock comparison (card O1) on the kickoff remanence of #38, and the two-time night step (O3) on its period units. Regime III: the context carries over the night in most cases, and resets happen every ~41 calls inside the day (NE41); days are 4–8 active h.

## Prediction
*Written 2026-10-04 21:45 UTC, before running on this period (card predictions applied).*
- If the kickoff remanence decays (Δm's CI excludes 0), the active-hour clock fits as well as or better than the night clock (SSE_H ≤ SSE_N): verdict *failed* for HH331 (expected). The night clock wins with the nested night factor λ's CI below 1: *supported*. Otherwise *mixed*; no decay: *descriptive*.
- O3: β_N (night step at fixed active lag) is reported; card-level expectation β_N < 0 at most weakly, β_G ≈ 0, β_gap ≈ 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout).* 40 windows, 12 incumbents, 5 fit days.

| Statistic | bge | gte |
| --- | --- | --- |
| O1 clock fit | winner W; SSE N/H/W/R/0 = 518.59/453.34/452.73/454.77/552.40 (×10⁻³); λ 0.05 [0.05, 1.50]; Δm(best) [-1.572, 0.206]; P(N beats H) 0.29 | winner W; SSE N/H/W/R/0 = 469.49/327.03/325.57/327.10/581.14 (×10⁻³); λ 0.05 [0.05, 1.50]; Δm(best) [0.114, 2.644]; P(N beats H) 0.00 |
| day-1 kickoff excess | 0.060 [-0.010, 0.134] | 0.066 |
| night step S_N / day drift D / midday step S_mid | 0.015 / -0.035 / -0.015 | -0.020 / -0.011 / 0.001 |
| O1 verdict | descriptive | failed |
| O3 unit 38a: β_N / β_G / β_gap | -0.0136 [-0.0421, +0.0181] / -0.0136 [-0.0591, +0.0303] / – | -0.0105 [-0.0390, +0.0186] |
| O3 unit 38b: β_N / β_G / β_gap | -0.0490 [-0.0874, -0.0148] / – / – | -0.0245 [-0.0527, +0.0074] |
| O3 unit 38e: β_N / β_G / β_gap | +0.1711 [-1.0755, +1.8673] / – / +0.2414 [+0.2163, +0.2640] | +1.2141 [-0.0376, +2.4037] |
| O2 previous-centroid day-1 level | 0.042 [-0.014, 0.099]; verdict descriptive | – |

## Scorecard (period-specific axes)
- **C:** midday-step and slot-effect nulls; **D:** the night step and day drift are unfitted signatures; **F:** synthetic clock-selection at this period's skeleton (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H103-nights-demagnetize/results/o1_*.json` (key G38), `o3_*.json`.
