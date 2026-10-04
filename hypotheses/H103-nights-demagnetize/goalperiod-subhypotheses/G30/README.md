# H103 × G30: which clock the kickoff remanence decays on (2026-02-09 → 2026-02-13)

**Verdict:** failed
**Role:** replication
**Period:** regime I · 11 incumbents · fit days 2026-02-09, 2026-02-10, 2026-02-11, 2026-02-12, 2026-02-13 · 5 non-holdout active days.

## Why this period
The common clock comparison (card O1) on the kickoff remanence of #30, and the two-time night step (O3) on its period units. Regime I: nights rarely start a new context (session or consolidation resets at 6% of first-of-day calls); days are about 3 active h.

## Prediction
*Written 2026-10-04 21:45 UTC, before running on this period (card predictions applied).*
- If the kickoff remanence decays (Δm's CI excludes 0), the active-hour clock fits as well as or better than the night clock (SSE_H ≤ SSE_N): verdict *failed* for HH331 (expected). The night clock wins with the nested night factor λ's CI below 1: *supported*. Otherwise *mixed*; no decay: *descriptive*.
- O3: β_N (night step at fixed active lag) is reported; card-level expectation β_N < 0 at most weakly, β_G ≈ 0, β_gap ≈ 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout).* 41 windows, 11 incumbents, 5 fit days.

| Statistic | bge | gte |
| --- | --- | --- |
| O1 clock fit | winner W; SSE N/H/W/R/0 = 4915.63/4017.63/4013.21/4052.29/5175.75 (×10⁻³); λ 0.05 [0.05, 1.50]; Δm(best) [0.352, 0.492]; P(N beats H) 0.01 | winner W; SSE N/H/W/R/0 = 4602.09/3511.14/3506.21/3518.39/5020.90 (×10⁻³); λ 0.05 [0.05, 1.50]; Δm(best) [0.333, 0.623]; P(N beats H) 0.00 |
| day-1 kickoff excess | 0.293 [0.239, 0.347] | 0.451 |
| night step S_N / day drift D / midday step S_mid | 0.053 / -0.083 / -0.073 | 0.063 / -0.093 / -0.046 |
| O1 verdict | failed | failed |
| O3 unit 30b: β_N / β_G / β_gap | -0.0245 [-0.0410, -0.0083] / – / – | -0.0268 [-0.0493, +0.0013] |

## Scorecard (period-specific axes)
- **C:** midday-step and slot-effect nulls; **D:** the night step and day drift are unfitted signatures; **F:** synthetic clock-selection at this period's skeleton (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H103-nights-demagnetize/results/o1_*.json` (key G30), `o3_*.json`.
