# H103 × G31: which clock the kickoff remanence decays on (2026-02-16 → 2026-02-20)

**Verdict:** mixed
**Role:** replication
**Period:** regime I · 11 incumbents · fit days 2026-02-16, 2026-02-17, 2026-02-18, 2026-02-19, 2026-02-20 · 5 non-holdout active days.

## Why this period
The common clock comparison (card O1) on the kickoff remanence of #31, and the two-time night step (O3) on its period units. Regime I: nights rarely start a new context (session or consolidation resets at 6% of first-of-day calls); days are about 3 active h.

## Prediction
*Written 2026-10-04 21:45 UTC, before running on this period (card predictions applied).*
- If the kickoff remanence decays (Δm's CI excludes 0), the active-hour clock fits as well as or better than the night clock (SSE_H ≤ SSE_N): verdict *failed* for HH331 (expected). The night clock wins with the nested night factor λ's CI below 1: *supported*. Otherwise *mixed*; no decay: *descriptive*.
- O3: β_N (night step at fixed active lag) is reported; card-level expectation β_N < 0 at most weakly, β_G ≈ 0, β_gap ≈ 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout).* 41 windows, 11 incumbents, 5 fit days.

| Statistic | bge | gte |
| --- | --- | --- |
| O1 clock fit | winner N; SSE N/H/W/R/0 = 2066.67/2106.52/2075.31/2067.70/2847.93 (×10⁻³); λ 0.60 [0.30, 1.50]; Δm(best) [0.099, 3.509]; P(N beats H) 0.75 | winner H; SSE N/H/W/R/0 = 2311.89/1907.18/1907.46/1911.38/2509.76 (×10⁻³); λ 1.50 [0.05, 1.50]; Δm(best) [0.158, 1.080]; P(N beats H) 0.01 |
| day-1 kickoff excess | 0.295 [0.232, 0.355] | 0.240 |
| night step S_N / day drift D / midday step S_mid | -0.128 / 0.090 / 0.033 | -0.120 / 0.083 / -0.001 |
| O1 verdict | mixed | failed |
| O2 previous-centroid day-1 level | 0.136 [0.072, 0.189]; verdict descriptive | – |

## Scorecard (period-specific axes)
- **C:** midday-step and slot-effect nulls; **D:** the night step and day drift are unfitted signatures; **F:** synthetic clock-selection at this period's skeleton (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H103-nights-demagnetize/results/o1_*.json` (key G31), `o3_*.json`.
