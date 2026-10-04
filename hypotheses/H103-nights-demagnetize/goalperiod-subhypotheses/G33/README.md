# H103 × G33: which clock the kickoff remanence decays on (2026-03-02 → 2026-03-04)

**Verdict:** failed
**Role:** replication
**Period:** regime II · 11 incumbents · fit days 2026-03-02, 2026-03-03, 2026-03-04 · 3 non-holdout active days.

## Why this period
The common clock comparison (card O1) on the kickoff remanence of #33, and the two-time night step (O3) on its period units. Regime II: nights rarely start a new context (10% of first-of-day calls); days are about 4 active h.

## Prediction
*Written 2026-10-04 21:45 UTC, before running on this period (card predictions applied).*
- If the kickoff remanence decays (Δm's CI excludes 0), the active-hour clock fits as well as or better than the night clock (SSE_H ≤ SSE_N): verdict *failed* for HH331 (expected). The night clock wins with the nested night factor λ's CI below 1: *supported*. Otherwise *mixed*; no decay: *descriptive*.
- O3: β_N (night step at fixed active lag) is reported; card-level expectation β_N < 0 at most weakly, β_G ≈ 0, β_gap ≈ 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout).* 24 windows, 11 incumbents, 3 fit days.

| Statistic | bge | gte |
| --- | --- | --- |
| O1 clock fit | winner H; SSE N/H/W/R/0 = 1875.13/1830.58/1864.72/1901.67/2928.58 (×10⁻³); λ 1.25 [1.05, 1.50]; Δm(best) [0.863, 7.101]; P(N beats H) 0.00 | winner H; SSE N/H/W/R/0 = 578.13/567.03/574.80/575.11/1130.39 (×10⁻³); λ 1.50 [1.05, 1.50]; Δm(best) [0.196, 23.592]; P(N beats H) 0.06 |
| day-1 kickoff excess | 0.150 [0.115, 0.185] | 0.124 |
| night step S_N / day drift D / midday step S_mid | 0.128 / -0.147 / -0.042 | 0.120 / -0.179 / -0.009 |
| O1 verdict | failed | failed |
| O3 unit 33: β_N / β_G / β_gap | +0.0780 [+0.0016, +0.1470] / – / +0.3198 [+0.2642, +0.3691] | +0.1149 [+0.0087, +0.2051] |

## Scorecard (period-specific axes)
- **C:** midday-step and slot-effect nulls; **D:** the night step and day drift are unfitted signatures; **F:** synthetic clock-selection at this period's skeleton (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H103-nights-demagnetize/results/o1_*.json` (key G33), `o3_*.json`.
