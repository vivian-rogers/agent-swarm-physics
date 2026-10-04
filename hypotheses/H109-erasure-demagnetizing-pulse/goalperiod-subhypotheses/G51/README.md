# H109 × G51: #51 unit 51g, #general vs #focus (2026-08-05 → 08-21)

**Verdict:** failed
**Role:** exploratory (native)
**Period:** regime III · #general (≈ 20 stayers) and #focus (2 residents, several hoppers) · 27 agents · 13 days. Other #51 units are single-room and not used.

## Why this period
By far the most forced boundaries (1,489) and the largest read volumes, so the recovery dose–response (κ_R vs posted-unread κ_U) has its power here. H102: content follows the room the agent speaks in.

## Prediction
*Written 2026-10-04 21:31 UTC, before running on this period (card predictions applied).*
- δ_F (gap-matched forced-erasure drop of the room alignment a_t, first ≤ 3 post statements vs ≤ 3 pre) and |δ_K| (kickoff alignment), both models, primary dedupe (restatements dropped).
- Card expectation: no drop (δ_F ≈ 0; P1 kill). HH339: δ_F ≥ 0.30 with CI > 0.
- Counts against my expectation: δ_F ≥ 0.30 with CI lower > 0 and |δ_K| < 0.15 (context-held order).
- Native: recovery slopes. If δ_F > 0: κ_R > 0 and κ_R − κ_U > 0 [0.5]. If no drop: κ_R's CI includes 0 [0.7].
- Verdict rule (card): supported if δ_F ≥ 0.30 with CI lower > 0 and |δ_K| < 0.15; failed if δ_F's CI upper < 0.30 with this period's synthetic power ≥ 0.8; descriptive if the pre-level Ā_pre,F is not identified; mixed (inconclusive) otherwise.

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/report.py`; non-holdout).* Primary: bge style_resid, restatements dropped; gte alongside.

| Statistic | bge | gte |
| --- | --- | --- |
| forced / voluntary / within boundaries | 1430 / 1462 / 7187 | same |
| pre-erasure room alignment Ā_pre [CI] | 0.088 [0.061, 0.122] | 0.103 [0.076, 0.141] |
| δ_F forced drop [agent-day CI] | 0.05 [-0.13, 0.19] | 0.07 [-0.09, 0.21] |
| δ_F agent-cluster CI | [-0.44, 0.29] | [-0.17, 0.29] |
| δ_F regression (± SE) | 0.02 ± 0.07 | 0.04 ± 0.06 |
| gap-matched coverage of F events | 0.82 | 0.82 |
| δ_V voluntary [CI] | 0.03 [-0.10, 0.13] | -0.07 [-0.22, 0.07] |
| δ_K kickoff alignment [CI] (pre level not identified) | -2.24 [-40.06, 15.08] | -0.19 [-0.62, 0.18] |
| κ_R re-read slope [CI]; κ_U | 0.031 [0.008, 0.055]; -0.014 | 0.037 [0.011, 0.063]; -0.018 |
| synthetic power at δ = 0.30 (read30) | 0.97 | 1.00 |

**Verdict:** failed (CI upper < 0.30 with synthetic power 0.97). Negative δ = alignment rises after the erasure.

## Scorecard (period-specific axes)
- **C:** W-boundary placebo (gap-matched within agent) and kickoff control.
- **E:** NE41 forced erasures in this period (exogenous timing).
- **F:** real-skeleton synthetic power 0.97 (bge) at δ = 0.30.

## Notes
- 2026-10-04 21:31 UTC: folder and prediction written before any H109 statistic on this period.
