# H109 × G39: #39 (2026-04-27 → 05-01)

**Verdict:** mixed
**Role:** exploratory (replication)
**Period:** regime III · #best/#rest after the 04-27 reshuffle · 15 agents · 5 days.

## Why this period
Identical kickoffs; H100 Q_spont 1.84 (p 0.016, bge; n.s. gte): a weaker split.

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
| forced / voluntary / within boundaries | 162 / 70 / 238 | same |
| pre-erasure room alignment Ā_pre [CI] | 0.083 [0.022, 0.126] | 0.037 [-0.008, 0.094] |
| δ_F forced drop [agent-day CI] | -0.24 [-2.29, 0.43] | -0.97 [-10.78, 5.22] |
| δ_F agent-cluster CI | [-1.33, 0.52] | [-6.54, 1.49] |
| δ_F regression (± SE) | -0.37 ± 0.43 | -0.46 ± 0.93 |
| gap-matched coverage of F events | 0.32 | 0.32 |
| δ_V voluntary [CI] | -0.98 [-10.48, 4.17] | 0.27 [-1.02, 1.79] |
| δ_K kickoff alignment [CI] (pre level identified) | 0.50 [0.00, 0.92] | 0.21 [-0.22, 0.62] |
| κ_R re-read slope [CI]; κ_U | -0.012 [-0.154, 0.076]; 0.003 | 0.007 [-0.076, 0.118]; -0.024 |
| synthetic power at δ = 0.30 (read30) | 0.07 | 0.10 |

**Verdict:** mixed (inconclusive: CI [-2.29, 0.43] and synthetic power 0.07 < 0.8). Negative δ = alignment rises after the erasure.

## Scorecard (period-specific axes)
- **C:** W-boundary placebo (gap-matched within agent) and kickoff control.
- **E:** NE41 forced erasures in this period (exogenous timing).
- **F:** real-skeleton synthetic power 0.07 (bge) at δ = 0.30.

## Notes
- 2026-10-04 21:31 UTC: folder and prediction written before any H109 statistic on this period.
