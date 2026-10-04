# H103 × G20: which clock the kickoff remanence decays on (2025-11-17 → 2025-11-28)

**Verdict:** supported
**Role:** replication
**Period:** regime I · 8 incumbents · fit days 2025-11-17, 2025-11-18, 2025-11-19, 2025-11-20, 2025-11-21 · 10 non-holdout active days.

## Why this period
The common clock comparison (card O1) on the kickoff remanence of #20, and the two-time night step (O3) on its period units. Regime I: nights rarely start a new context (session or consolidation resets at 6% of first-of-day calls); days are about 3 active h.

## Prediction
*Written 2026-10-04 21:45 UTC, before running on this period (card predictions applied).*
- If the kickoff remanence decays (Δm's CI excludes 0), the active-hour clock fits as well as or better than the night clock (SSE_H ≤ SSE_N): verdict *failed* for HH331 (expected). The night clock wins with the nested night factor λ's CI below 1: *supported*. Otherwise *mixed*; no decay: *descriptive*.
- O3: β_N (night step at fixed active lag) is reported; card-level expectation β_N < 0 at most weakly, β_G ≈ 0, β_gap ≈ 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout).* 40 windows, 8 incumbents, 5 fit days.

| Statistic | bge | gte |
| --- | --- | --- |
| O1 clock fit | winner N; SSE N/H/W/R/0 = 913.31/1117.15/964.40/1156.11/2070.74 (×10⁻³); λ 0.05 [0.05, 0.85]; Δm(best) [0.082, 0.379]; P(N beats H) 0.91 | winner N; SSE N/H/W/R/0 = 818.16/1105.40/863.37/1156.21/2612.76 (×10⁻³); λ 0.05 [0.05, 0.35]; Δm(best) [0.133, 0.301]; P(N beats H) 0.97 |
| day-1 kickoff excess | 0.203 [0.166, 0.246] | 0.250 |
| night step S_N / day drift D / midday step S_mid | 0.037 / -0.078 / -0.054 | 0.064 / -0.112 / -0.039 |
| O1 verdict | supported | supported |
| O3 unit 20c: β_N / β_G / β_gap | +0.2067 [+0.1373, +0.2768] / -0.0363 [-0.0917, +0.0098] / – | +0.1794 [+0.1010, +0.2698] |
| O3 unit 20d: β_N / β_G / β_gap | -0.0816 [-0.1289, -0.0211] / – / – | -0.1609 [-0.2141, -0.0960] |
| O2 previous-centroid day-1 level | 0.049 [0.019, 0.081]; verdict descriptive | – |

## Scorecard (period-specific axes)
- **C:** midday-step and slot-effect nulls; **D:** the night step and day drift are unfitted signatures; **F:** synthetic clock-selection at this period's skeleton (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H103-nights-demagnetize/results/o1_*.json` (key G20), `o3_*.json`.
