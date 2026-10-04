# H109 × G38: #38 (2026-04-02 → 04-24; units 38a–e)

**Verdict:** failed
**Role:** exploratory (native)
**Period:** regime III · #best/#rest with room-specific kickoffs · 12–13 agents · 15 days. Splits at NE17, NE18 and two joins; one axis for the goal period.

## Why this period
Room-specific kickoffs held in the prompt (cos 0.86): the native contrast is room-kickoff alignment (prompt-held, should not fall) vs the spontaneous axis (may fall if context-held). Most forced boundaries of any multi-room period (1,040).

## Prediction
*Written 2026-10-04 21:31 UTC, before running on this period (card predictions applied).*
- δ_F (gap-matched forced-erasure drop of the room alignment a_t, first ≤ 3 post statements vs ≤ 3 pre) and |δ_K| (kickoff alignment), both models, primary dedupe (restatements dropped).
- Card expectation: no drop (δ_F ≈ 0; P1 kill). HH339: δ_F ≥ 0.30 with CI > 0.
- Counts against my expectation: δ_F ≥ 0.30 with CI lower > 0 and |δ_K| < 0.15 (context-held order).
- Native: room-kickoff alignment δ_K (statement room's own kickoff) |δ_K| < 0.15 [0.75], whatever δ_F does.
- Verdict rule (card): supported if δ_F ≥ 0.30 with CI lower > 0 and |δ_K| < 0.15; failed if δ_F's CI upper < 0.30 with this period's synthetic power ≥ 0.8; descriptive if the pre-level Ā_pre,F is not identified; mixed (inconclusive) otherwise.

## Result
*Run 2026-10-04 (`analysis/run.py`, `analysis/report.py`; non-holdout).* Primary: bge style_resid, restatements dropped; gte alongside.

| Statistic | bge | gte |
| --- | --- | --- |
| forced / voluntary / within boundaries | 732 / 272 / 2077 | same |
| pre-erasure room alignment Ā_pre [CI] | 0.206 [0.182, 0.238] | 0.261 [0.234, 0.289] |
| δ_F forced drop [agent-day CI] | -0.26 [-0.38, -0.07] | -0.19 [-0.31, -0.04] |
| δ_F agent-cluster CI | [-0.44, -0.14] | [-0.25, -0.11] |
| δ_F regression (± SE) | -0.15 ± 0.05 | -0.12 ± 0.04 |
| gap-matched coverage of F events | 0.62 | 0.62 |
| δ_V voluntary [CI] | -0.17 [-0.37, 0.06] | -0.14 [-0.30, 0.08] |
| δ_K kickoff alignment [CI] (pre level identified) | 0.04 [-0.29, 0.35] | -1.14 [-13.09, 5.94] |
| κ_R re-read slope [CI]; κ_U | 0.008 [-0.023, 0.041]; 0.002 | -0.005 [-0.036, 0.026]; 0.000 |
| synthetic power at δ = 0.30 (read30) | 0.87 | 0.85 |

**Verdict:** failed (CI upper < 0.30 with synthetic power 0.87). Negative δ = alignment rises after the erasure.

## Scorecard (period-specific axes)
- **C:** W-boundary placebo (gap-matched within agent) and kickoff control.
- **E:** NE41 forced erasures in this period (exogenous timing).
- **F:** real-skeleton synthetic power 0.87 (bge) at δ = 0.30.

## Notes
- 2026-10-04 21:31 UTC: folder and prediction written before any H109 statistic on this period.
