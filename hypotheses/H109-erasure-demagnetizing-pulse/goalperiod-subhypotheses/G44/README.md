# H109 × G44: #44 (2026-05-26 → 05-29; units 44a, 44b)

**Verdict:** mixed
**Role:** exploratory (native)
**Period:** regime III · #best/#rest with room-specific kickoffs · 15–16 agents · 4 days. Split at roster joins (05-28).

## Why this period
Room-specific kickoffs (cos 0.81) and heavy operator traffic in #best: the room-kickoff alignment control should stay flat while the spontaneous axis is tested.

## Prediction
*Written 2026-10-04 21:31 UTC, before running on this period (card predictions applied).*
- δ_F (gap-matched forced-erasure drop of the room alignment a_t, first ≤ 3 post statements vs ≤ 3 pre) and |δ_K| (kickoff alignment), both models, primary dedupe (restatements dropped).
- Card expectation: no drop (δ_F ≈ 0; P1 kill). HH339: δ_F ≥ 0.30 with CI > 0.
- Counts against my expectation: δ_F ≥ 0.30 with CI lower > 0 and |δ_K| < 0.15 (context-held order).
- Native: room-kickoff alignment δ_K |δ_K| < 0.15 [0.75], whatever δ_F does.
- Verdict rule (card): supported if δ_F ≥ 0.30 with CI lower > 0 and |δ_K| < 0.15; failed if δ_F's CI upper < 0.30 with this period's synthetic power ≥ 0.8; descriptive if the pre-level Ā_pre,F is not identified; mixed (inconclusive) otherwise.

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/report.py`; non-holdout).* Primary: bge style_resid, restatements dropped; gte alongside.

| Statistic | bge | gte |
| --- | --- | --- |
| forced / voluntary / within boundaries | 209 / 212 / 1160 | same |
| pre-erasure room alignment Ā_pre [CI] | 0.233 [0.185, 0.274] | 0.288 [0.243, 0.330] |
| δ_F forced drop [agent-day CI] | -0.08 [-0.40, 0.13] | -0.00 [-0.24, 0.14] |
| δ_F agent-cluster CI | [-0.42, 0.11] | [-0.21, 0.13] |
| δ_F regression (± SE) | -0.04 ± 0.06 | -0.06 ± 0.06 |
| gap-matched coverage of F events | 0.59 | 0.59 |
| δ_V voluntary [CI] | -0.17 [-0.52, 0.16] | -0.07 [-0.37, 0.13] |
| δ_K kickoff alignment [CI] (pre level not identified) | 12.32 [-17.05, 11.16] | 4.55 [-12.92, 16.04] |
| κ_R re-read slope [CI]; κ_U | 0.011 [-0.054, 0.064]; 0.017 | 0.001 [-0.075, 0.061]; -0.002 |
| synthetic power at δ = 0.30 (read30) | 0.43 | 0.25 |

**Verdict:** mixed (inconclusive: CI [-0.40, 0.13] and synthetic power 0.43 < 0.8). Negative δ = alignment rises after the erasure.

## Scorecard (period-specific axes)
- **C:** W-boundary placebo (gap-matched within agent) and kickoff control.
- **E:** NE41 forced erasures in this period (exogenous timing).
- **F:** real-skeleton synthetic power 0.43 (bge) at δ = 0.30.

## Notes
- 2026-10-04 21:31 UTC: folder and prediction written before any H109 statistic on this period.
