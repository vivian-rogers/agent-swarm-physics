# H37 × G40: shared-objective consensus week (2026-05-04 → 2026-05-08)

**Verdict:** mixed (no false faction or pair alarm; conflict level not low)
**Role:** exploratory (false-alarm contrast)
**Period:** regime III · mode C · 15 agents · 3 rooms · 5 days. No assigned conflict.

## Why this period
A detector is useful only if it stays quiet where nothing is going on. #40 is a cooperative week with no assigned sides, used to measure the conflict and faction detector's false-alarm behaviour on real logs.

## Prediction
*Written 2026-10-04 01:53 UTC, before running on this period (card prediction P12).*
- **P12:** f_neg(#40) ≤ ½ f_neg(#12 opposite-team debate replies); at most one significantly negative pair (FDR 0.1); faction score not significant (sign-shuffle p > 0.05). [0.7]

## Result
*Run 2026-10-04 (`analysis/explore.py`, `analysis/calibrate.py`; data `G40/results.json`; figure `figures/g40_shares.pdf`).* 1,904 relevant replies among 14 agents; 66 pairs with ≥ 3 replies.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P12a f_neg(#40) ≤ ½ f_neg(#12 opponents) | 0.197 [0.12, 0.28] vs 0.262 | | **fail** |
| P12b ≤ 1 significantly negative pair | 0 (calibrated null 0.04) | | pass |
| P12c faction score not significant | sign-shuffle p = 0.25; calibrated p = 0.73 | | pass |

**Reading.** The structural parts of the detector (negative pairs, camps) stay quiet in a cooperative week. The raw conflict level does not: Jev labels 20% of #40 replies "oppose". #40 (the 3D-universe week) was full of task corrections (duplicate data, merge conflicts, broken builds), and Jev's "negative" calls are only 30% precise against blind labels (validation). So f_neg measures correction friction plus label noise, not factional conflict, and must not be used alone as an alarm.

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 1 | structural detector components match the calibrated null (no false alarm); the f_neg component fails |

## Notes
