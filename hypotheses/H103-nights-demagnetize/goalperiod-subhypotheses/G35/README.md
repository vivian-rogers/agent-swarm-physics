# H103 × G35: which clock the kickoff remanence decays on (2026-03-16 → 2026-03-20)

**Verdict:** descriptive
**Role:** replication
**Period:** regime II · 12 incumbents · fit days 2026-03-16, 2026-03-17, 2026-03-18, 2026-03-19, 2026-03-20 · 5 non-holdout active days.

## Why this period
The common clock comparison (card O1) on the kickoff remanence of #35, and the two-time night step (O3) on its period units. Regime II: nights rarely start a new context (10% of first-of-day calls); days are about 4 active h.

## Prediction
*Written 2026-10-04 21:45 UTC, before running on this period (card predictions applied).*
- If the kickoff remanence decays (Δm's CI excludes 0), the active-hour clock fits as well as or better than the night clock (SSE_H ≤ SSE_N): verdict *failed* for HH331 (expected). The night clock wins with the nested night factor λ's CI below 1: *supported*. Otherwise *mixed*; no decay: *descriptive*.
- O3: β_N (night step at fixed active lag) is reported; card-level expectation β_N < 0 at most weakly, β_G ≈ 0, β_gap ≈ 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout).* 40 windows, 12 incumbents, 5 fit days.

| Statistic | bge | gte |
| --- | --- | --- |
| O1 clock fit | winner R; SSE N/H/W/R/0 = 2041.47/1746.03/1746.17/1743.13/2210.09 (×10⁻³); λ 1.50 [0.05, 1.50]; Δm(best) [-2.710, 214677.139]; P(N beats H) 0.07 | winner R; SSE N/H/W/R/0 = 2016.84/1764.76/1783.30/1764.21/2390.51 (×10⁻³); λ 1.50 [0.05, 1.50]; Δm(best) [0.149, 295589.852]; P(N beats H) 0.01 |
| day-1 kickoff excess | 0.107 [0.065, 0.143] | 0.106 |
| night step S_N / day drift D / midday step S_mid | 0.052 / -0.062 / -0.027 | 0.044 / -0.065 / -0.053 |
| O1 verdict | descriptive | failed |
| O3 unit 35: β_N / β_G / β_gap | +0.0004 [-0.1127, +0.1149] / – / – | -0.0095 [-0.1201, +0.1077] |

## Scorecard (period-specific axes)
- **C:** midday-step and slot-effect nulls; **D:** the night step and day drift are unfitted signatures; **F:** synthetic clock-selection at this period's skeleton (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H103-nights-demagnetize/results/o1_*.json` (key G35), `o3_*.json`.
