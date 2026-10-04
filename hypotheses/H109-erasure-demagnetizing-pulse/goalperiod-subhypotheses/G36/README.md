# H109 × G36: #36 regime-III part (units 36b, 36c; 2026-03-24 → 03-27)

**Verdict:** descriptive
**Role:** exploratory (replication)
**Period:** regime III · #best/#rest · 12 agents · 4 days. Splits: 36a (03-23, regime II) excluded; 36b/36c split at NE16.

## Why this period
First regime-III week with two rooms; identical kickoffs. H100: Q 1.68 (n.s.), so the room axis may be weak; δ_F may be unidentified (descriptive).

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
| forced / voluntary / within boundaries | 219 / 106 / 638 | same |
| pre-erasure room alignment Ā_pre [CI] | 0.086 [-0.013, 0.161] | 0.094 [0.018, 0.149] |
| δ_F forced drop [agent-day CI] | -0.12 [-3.15, 2.63] | 0.28 [-1.60, 2.16] |
| δ_F agent-cluster CI | [-2.74, 4.51] | [-3.13, 2.51] |
| δ_F regression (± SE) | -0.11 ± 0.30 | 0.12 ± 0.30 |
| gap-matched coverage of F events | 0.36 | 0.36 |
| δ_V voluntary [CI] | -0.02 [-1.80, 2.62] | -0.13 [-1.41, 3.42] |
| δ_K kickoff alignment [CI] (pre level identified) | -0.07 [-0.63, 0.36] | 0.23 [-0.22, 0.56] |
| κ_R re-read slope [CI]; κ_U | -0.020 [-0.084, 0.033]; -0.028 | -0.008 [-0.073, 0.055]; -0.018 |
| synthetic power at δ = 0.30 (read30) | 0.00 | 0.00 |

**Verdict:** descriptive (pre-erasure room alignment not identified (CI includes 0)). Negative δ = alignment rises after the erasure.

## Scorecard (period-specific axes)
- **C:** W-boundary placebo (gap-matched within agent) and kickoff control.
- **E:** NE41 forced erasures in this period (exogenous timing).
- **F:** real-skeleton synthetic power 0.00 (bge) at δ = 0.30.

## Notes
- 2026-10-04 21:31 UTC: folder and prediction written before any H109 statistic on this period.
