# H109 × G37: #37 (2026-03-30 → 04-01)

**Verdict:** mixed
**Role:** exploratory (replication)
**Period:** regime III · #best/#rest · 10 agents · 3 days.

## Why this period
Identical kickoffs; H100 Q_spont 2.55 (p 0.027): a field-free room split, short period (116 forced boundaries).

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
| forced / voluntary / within boundaries | 116 / 77 / 422 | same |
| pre-erasure room alignment Ā_pre [CI] | 0.141 [0.073, 0.208] | 0.137 [0.078, 0.211] |
| δ_F forced drop [agent-day CI] | 0.23 [-0.25, 0.50] | -0.04 [-1.08, 0.29] |
| δ_F agent-cluster CI | [0.00, 0.44] | [-0.38, 0.15] |
| δ_F regression (± SE) | 0.11 ± 0.16 | -0.00 ± 0.15 |
| gap-matched coverage of F events | 0.36 | 0.36 |
| δ_V voluntary [CI] | -0.01 [-0.56, 0.23] | 0.42 [-0.27, 0.79] |
| δ_K kickoff alignment [CI] (pre level identified) | 0.13 [-4.72, 3.77] | 0.54 [-2.54, 2.34] |
| κ_R re-read slope [CI]; κ_U | 0.045 [-0.022, 0.106]; 0.027 | -0.007 [-0.047, 0.049]; 0.024 |
| synthetic power at δ = 0.30 (read30) | 0.03 | 0.05 |

**Verdict:** mixed (inconclusive: CI [-0.25, 0.50] and synthetic power 0.03 < 0.8). Negative δ = alignment rises after the erasure.

## Scorecard (period-specific axes)
- **C:** W-boundary placebo (gap-matched within agent) and kickoff control.
- **E:** NE41 forced erasures in this period (exogenous timing).
- **F:** real-skeleton synthetic power 0.03 (bge) at δ = 0.30.

## Notes
- 2026-10-04 21:31 UTC: folder and prediction written before any H109 statistic on this period.
