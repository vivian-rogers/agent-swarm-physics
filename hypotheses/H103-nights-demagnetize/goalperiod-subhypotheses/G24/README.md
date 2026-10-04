# H103 × G24: which clock the kickoff remanence decays on (2025-12-22 → 2025-12-26)

**Verdict:** failed
**Role:** replication
**Period:** regime I · 10 incumbents · fit days 2025-12-22, 2025-12-23, 2025-12-24, 2025-12-25, 2025-12-26 · 5 non-holdout active days.

## Why this period
The common clock comparison (card O1) on the kickoff remanence of #24, and the two-time night step (O3) on its period units. Regime I: nights rarely start a new context (session or consolidation resets at 6% of first-of-day calls); days are about 3 active h.

## Prediction
*Written 2026-10-04 21:45 UTC, before running on this period (card predictions applied).*
- If the kickoff remanence decays (Δm's CI excludes 0), the active-hour clock fits as well as or better than the night clock (SSE_H ≤ SSE_N): verdict *failed* for HH331 (expected). The night clock wins with the nested night factor λ's CI below 1: *supported*. Otherwise *mixed*; no decay: *descriptive*.
- O3: β_N (night step at fixed active lag) is reported; card-level expectation β_N < 0 at most weakly, β_G ≈ 0, β_gap ≈ 0.

## Result
*Run 2026-10-04 (`analysis/run.py`; non-holdout).* 39 windows, 10 incumbents, 5 fit days.

| Statistic | bge | gte |
| --- | --- | --- |
| O1 clock fit | winner H; SSE N/H/W/R/0 = 649.42/633.23/645.00/651.46/861.28 (×10⁻³); λ 1.05 [1.03, 1.50]; Δm(best) [0.035, 26939449.208]; P(N beats H) 0.03 | winner N; SSE N/H/W/R/0 = 379.07/385.07/380.62/383.83/406.65 (×10⁻³); λ 0.15 [0.05, 1.50]; Δm(best) [-1.324, 0.121]; P(N beats H) 0.54 |
| day-1 kickoff excess | 0.161 [0.127, 0.203] | 0.019 |
| night step S_N / day drift D / midday step S_mid | 0.000 / -0.025 / -0.032 | -0.006 / 0.016 / -0.010 |
| O1 verdict | failed | descriptive |
| O3 unit 24: β_N / β_G / β_gap | +0.0439 [+0.0103, +0.0752] / – / – | +0.0475 [+0.0231, +0.0733] |

## Scorecard (period-specific axes)
- **C:** midday-step and slot-effect nulls; **D:** the night step and day drift are unfitted signatures; **F:** synthetic clock-selection at this period's skeleton (`synthetic/synthetic.json`).

## Notes
- Data: `data/processed/H103-nights-demagnetize/results/o1_*.json` (key G24), `o3_*.json`.
