# H109 × G42: #42 (2026-05-18 → 05-22; units 42a, 42b)

**Verdict:** mixed
**Role:** exploratory (replication)
**Period:** regime III · #best/#rest · 14–15 agents · 5 days. Split at a roster join (05-20).

## Why this period
Identical kickoffs; H100 Q_spont 1.61 (p 0.069 bge; gte significant).

## Prediction
*Written 2026-10-04 21:31 UTC, before running on this period (card predictions applied).*
- δ_F (gap-matched forced-erasure drop of the room alignment a_t, first ≤ 3 post statements vs ≤ 3 pre) and |δ_K| (kickoff alignment), both models, primary dedupe (restatements dropped).
- Card expectation: no drop (δ_F ≈ 0; P1 kill). HH339: δ_F ≥ 0.30 with CI > 0.
- Counts against my expectation: δ_F ≥ 0.30 with CI lower > 0 and |δ_K| < 0.15 (context-held order).
- Verdict rule (card): supported if δ_F ≥ 0.30 with CI lower > 0 and |δ_K| < 0.15; failed if δ_F's CI upper < 0.30 with this period's synthetic power ≥ 0.8; descriptive if the pre-level Ā_pre,F is not identified; mixed (inconclusive) otherwise.

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/report.py`; non-holdout).* Primary: bge style_resid, restatements dropped; gte alongside.

| Statistic | bge | gte |
| --- | --- | --- |
| forced / voluntary / within boundaries | 233 / 174 / 568 | same |
| pre-erasure room alignment Ā_pre [CI] | 0.106 [0.058, 0.162] | 0.108 [0.061, 0.151] |
| δ_F forced drop [agent-day CI] | -0.32 [-1.17, 0.64] | -0.10 [-1.02, 0.49] |
| δ_F agent-cluster CI | [-1.11, 0.60] | [-0.90, 0.43] |
| δ_F regression (± SE) | -0.15 ± 0.26 | -0.21 ± 0.20 |
| gap-matched coverage of F events | 0.30 | 0.30 |
| δ_V voluntary [CI] | -0.19 [-0.84, 0.28] | -0.44 [-2.12, 0.15] |
| δ_K kickoff alignment [CI] (pre level identified) | -0.10 [-0.55, 0.21] | -0.12 [-0.39, 0.09] |
| κ_R re-read slope [CI]; κ_U | 0.030 [-0.032, 0.084]; 0.008 | -0.010 [-0.066, 0.044]; 0.006 |
| synthetic power at δ = 0.30 (read30) | 0.03 | 0.05 |

**Verdict:** mixed (inconclusive: CI [-1.17, 0.64] and synthetic power 0.03 < 0.8). Negative δ = alignment rises after the erasure.

## Scorecard (period-specific axes)
- **C:** W-boundary placebo (gap-matched within agent) and kickoff control.
- **E:** NE41 forced erasures in this period (exogenous timing).
- **F:** real-skeleton synthetic power 0.03 (bge) at δ = 0.30.

## Notes
- 2026-10-04 21:31 UTC: folder and prediction written before any H109 statistic on this period.
