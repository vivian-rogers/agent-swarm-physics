# H103 × G51: which clock the kickoff remanence decays on (2026-07-06 → 2026-09-04)

**Verdict:** descriptive
**Role:** replication
**Period:** regime III · 21 incumbents · fit days 2026-07-06, 2026-07-07, 2026-07-08, 2026-07-09, 2026-07-10 · 45 non-holdout active days.

## Why this period
The common clock comparison (card O1) on the kickoff remanence of #51, and the two-time night step (O3) on its period units. Regime III: the context carries over the night in most cases, and resets happen every ~41 calls inside the day (NE41); days are 4–8 active h.

## Prediction
*Written 2026-10-04 21:45 UTC, before running on this period (card predictions applied).*
- If the kickoff remanence decays (Δm's CI excludes 0), the active-hour clock fits as well as or better than the night clock (SSE_H ≤ SSE_N): verdict *failed* for HH331 (expected). The night clock wins with the nested night factor λ's CI below 1: *supported*. Otherwise *mixed*; no decay: *descriptive*.
- O3: β_N (night step at fixed active lag) is reported; card-level expectation β_N < 0 at most weakly, β_G ≈ 0, β_gap ≈ 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout).* 81 windows, 21 incumbents, 5 fit days.

| Statistic | bge | gte |
| --- | --- | --- |
| O1 clock fit | winner N; SSE N/H/W/R/0 = 918.54/942.66/935.72/953.45/1052.98 (×10⁻³); λ 0.30 [0.05, 1.30]; Δm(best) [-0.063, 2226.097]; P(N beats H) 0.85 | winner N; SSE N/H/W/R/0 = 492.39/500.20/496.65/510.24/571.18 (×10⁻³); λ 1.50 [0.05, 1.50]; Δm(best) [-0.329, 1239.947]; P(N beats H) 0.62 |
| day-1 kickoff excess | -0.020 [-0.054, 0.014] | 0.024 |
| night step S_N / day drift D / midday step S_mid | 0.013 / -0.013 / -0.015 | -0.001 / -0.006 / 0.008 |
| O1 verdict | descriptive | descriptive |
| O3 unit 51a: β_N / β_G / β_gap | -0.0179 [-0.1879, +0.1448] / – / -0.0302 [-0.1519, +0.0701] | +0.0011 [-0.1875, +0.1994] |
| O3 unit 51c: β_N / β_G / β_gap | +0.0160 [-0.0092, +0.0469] / -0.0037 [-0.0348, +0.0213] / +0.0557 [+0.0016, +0.1175] | +0.0093 [-0.0183, +0.0412] |
| O3 unit 51d: β_N / β_G / β_gap | -0.0224 [-0.1621, +0.1203] / -0.0215 [-0.0391, -0.0062] / +0.0503 [-0.0036, +0.1183] | -0.0249 [-0.1337, +0.1000] |
| O3 unit 51e: β_N / β_G / β_gap | +0.0226 [-0.0882, +0.1031] / +0.0040 [-0.0201, +0.0317] / +0.0619 [+0.0203, +0.1793] | +0.0469 [-0.0615, +0.1335] |
| O3 unit 51f: β_N / β_G / β_gap | -0.0543 [-0.3756, +0.2604] / +0.0163 [-0.0295, +0.0502] / +0.0452 [-0.0441, +0.1514] | +0.0422 [-0.2888, +0.3078] |
| O3 unit 51g: β_N / β_G / β_gap | +0.0682 [+0.0227, +0.1095] / -0.0118 [-0.0287, +0.0043] / +0.0553 [-0.0029, +0.0890] | +0.0685 [+0.0232, +0.1201] |
| O3 unit 51h: β_N / β_G / β_gap | +0.2635 [-0.1401, +0.7078] / – / +0.0955 [+0.0629, +0.1273] | +0.3505 [-0.0161, +0.7462] |

## Scorecard (period-specific axes)
- **C:** midday-step and slot-effect nulls; **D:** the night step and day drift are unfitted signatures; **F:** synthetic clock-selection at this period's skeleton (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H103-nights-demagnetize/results/o1_*.json` (key G51), `o3_*.json`.
