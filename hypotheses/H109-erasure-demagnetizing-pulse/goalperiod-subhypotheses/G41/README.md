# H109 × G41: #41 (2026-05-11 → 05-15)

**Verdict:** mixed
**Role:** exploratory (native)
**Period:** regime III · #best/#rest (after the NE42 merge week) · 15 agents · 5 days.

## Why this period
Identical kickoffs and the strongest field-free split in H100 (Q_spont 4.23, p 0.001): the cleanest test that spontaneous room order is held in the context window.

## Prediction
*Written 2026-10-04 21:31 UTC, before running on this period (card predictions applied).*
- δ_F (gap-matched forced-erasure drop of the room alignment a_t, first ≤ 3 post statements vs ≤ 3 pre) and |δ_K| (kickoff alignment), both models, primary dedupe (restatements dropped).
- Card expectation: no drop (δ_F ≈ 0; P1 kill). HH339: δ_F ≥ 0.30 with CI > 0.
- Counts against my expectation: δ_F ≥ 0.30 with CI lower > 0 and |δ_K| < 0.15 (context-held order).
- Native: supported only if bge and gte agree in sign. I expect δ_F ≈ 0 here too [0.75].
- Verdict rule (card): supported if δ_F ≥ 0.30 with CI lower > 0 and |δ_K| < 0.15; failed if δ_F's CI upper < 0.30 with this period's synthetic power ≥ 0.8; descriptive if the pre-level Ā_pre,F is not identified; mixed (inconclusive) otherwise.

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/report.py`; non-holdout).* Primary: bge style_resid, restatements dropped; gte alongside.

| Statistic | bge | gte |
| --- | --- | --- |
| forced / voluntary / within boundaries | 376 / 186 / 1248 | same |
| pre-erasure room alignment Ā_pre [CI] | 0.157 [0.103, 0.213] | 0.176 [0.116, 0.240] |
| δ_F forced drop [agent-day CI] | -0.20 [-0.57, 0.05] | -0.22 [-0.47, 0.05] |
| δ_F agent-cluster CI | [-0.51, 0.01] | [-0.51, 0.04] |
| δ_F regression (± SE) | -0.19 ± 0.09 | -0.16 ± 0.08 |
| gap-matched coverage of F events | 0.73 | 0.73 |
| δ_V voluntary [CI] | -0.43 [-1.37, -0.06] | -0.41 [-1.16, 0.00] |
| δ_K kickoff alignment [CI] (pre level identified) | 0.27 [-0.44, 1.50] | -0.27 [-0.86, 0.30] |
| κ_R re-read slope [CI]; κ_U | -0.009 [-0.061, 0.041]; -0.011 | -0.005 [-0.053, 0.043]; -0.011 |
| synthetic power at δ = 0.30 (read30) | 0.40 | 0.55 |

**Verdict:** mixed (inconclusive: CI [-0.57, 0.05] and synthetic power 0.40 < 0.8). Negative δ = alignment rises after the erasure.

## Scorecard (period-specific axes)
- **C:** W-boundary placebo (gap-matched within agent) and kickoff control.
- **E:** NE41 forced erasures in this period (exogenous timing).
- **F:** real-skeleton synthetic power 0.40 (bge) at δ = 0.30.

## Notes
- 2026-10-04 21:31 UTC: folder and prediction written before any H109 statistic on this period.
