# H103 × G06: which clock the kickoff remanence decays on (2025-06-26 → 2025-07-15)

**Verdict:** descriptive
**Role:** native
**Period:** regime I · 4 incumbents · fit days 2025-06-26, 2025-06-27, 2025-06-29, 2025-06-30, 2025-07-01 · 15 non-holdout active days.

## Why this period
The common clock comparison (card O1) on the kickoff remanence of #6, and the two-time night step (O3) on its period units. Regime I: nights rarely start a new context (session or consolidation resets at 6% of first-of-day calls); days are about 3 active h.

## Prediction
*Written 2026-10-04 21:45 UTC, before running on this period (card predictions applied).*
- If the kickoff remanence decays (Δm's CI excludes 0), the active-hour clock fits as well as or better than the night clock (SSE_H ≤ SSE_N): verdict *failed* for HH331 (expected). The night clock wins with the nested night factor λ's CI below 1: *supported*. Otherwise *mixed*; no decay: *descriptive*.
- O3: β_N (night step at fixed active lag) is reported; card-level expectation β_N < 0 at most weakly, β_G ≈ 0, β_gap ≈ 0.

### Native N3 (village-off midday breaks)
*Written 2026-10-04 21:45 UTC, before running (card N3).* Two village-wide midday breaks of near-night length exist in the non-holdout record, both in regime I: 2025-06-18 (#4, 300 min) and 2025-06-29 (#6, 774 min). For the same agents on that day and the adjacent active days: self-overlap of window pairs across the break vs same-side pairs and cross-night pairs at matched active lag (break time excluded).
- Prediction: across-break overlap is within the range of same-side pairs, not at the cross-night level [0.6]. Descriptive (4 agents, 2 events). Both events are reported here.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout).* 24 windows, 4 incumbents, 5 fit days.

| Statistic | bge | gte |
| --- | --- | --- |
| O1 clock fit | winner H; SSE N/H/W/R/0 = 418.58/331.97/382.58/385.92/585.68 (×10⁻³); λ 1.10 [1.05, 1.50]; Δm(best) [0.152, 2.529]; P(N beats H) 0.00 | winner R; SSE N/H/W/R/0 = 156.79/150.37/154.61/132.94/228.83 (×10⁻³); λ 1.00 [0.95, 1.50]; Δm(best) [0.137, 4.257]; P(N beats H) 0.26 |
| day-1 kickoff excess | 0.145 [0.091, 0.239] | 0.162 |
| night step S_N / day drift D / midday step S_mid | -0.010 / -0.005 / 0.003 | -0.002 / -0.006 / -0.002 |
| O1 verdict | failed | failed |
| O3 unit 6a: β_N / β_G / β_gap | -0.1613 [-0.5790, +0.1947] / +0.4139 [-6.4864, +0.5564] / +0.0473 [+0.0283, +0.0636] | +0.0137 [-0.4848, +0.4730] |
| O3 unit 6b: β_N / β_G / β_gap | -0.0805 [-0.1927, -0.0085] / +0.0153 [-0.0143, +0.0442] / +0.0894 [+0.0771, +0.1162] | -0.1208 [-0.2918, +0.0276] |
| O2 previous-centroid day-1 level | -0.011 [-0.079, 0.067]; verdict descriptive | – |

### Native N3 result (village-off midday breaks)
| Day | break (min) | across-break C | same-side C (matched lag) | cross-night C (matched lag) |
| --- | --- | --- | --- | --- |
| 2025-06-18 (#4) | 300 | 0.371 (n 76) | 0.345 (n 39) | 0.515 (n 44) |
| 2025-06-29 (#6) | 774 | – (n None) | – (n None) | – (n None) |

The folder verdict is the native's (descriptive); the O1 replication verdict for #6 is failed.

## Scorecard (period-specific axes)
- **C:** midday-step and slot-effect nulls; **D:** the night step and day drift are unfitted signatures; **F:** synthetic clock-selection at this period's skeleton (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H103-nights-demagnetize/results/o1_*.json` (key G06), `o3_*.json`.
