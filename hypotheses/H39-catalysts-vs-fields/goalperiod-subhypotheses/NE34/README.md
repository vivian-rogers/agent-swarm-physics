# H39 × NE34: Goal kickoffs (every non-holdout consecutive pair in one regime)

**Verdict:** mixed
**Role:** replication (exploratory) (round 1, non-holdout; spanning test)
**Period:** see Prediction for the windows; non-holdout days only.

## Why this test
Goal kickoffs are the candidate *fields* of HH52; transitions are the object (exception c).

## Prediction
*Written 2026-10-04 (UTC), before running this test.* P5 (card):
- Content (C6): φ above the placebo p95 in ≥ 70% of usable kickoffs; content K above the placebo median in ≥ 60% (faster topic churn after a kickoff, H20).
- Behavior (B4): φ above the placebo p95 in ≤ 30% of kickoffs; K inside the placebo [p2.5, p97.5] in ≥ 70% (H04: kickoffs change what, not how much).
- Class: content field (or both); behavior neither. Unit = the transition (named exception c). Placebo = within-goal day boundaries of the same era (regime × hours) and window shape (2 + 2 days unless fewer exist), balanced agent panel.
- Against: behavior φ above p95 in > 30% of kickoffs (kickoffs are behavior fields), or content φ above p95 in < 70% (goals do not tilt content more than an ordinary day change).

## Result
Run 2026-10-04 with `analysis/run_steps.py`; numbers in `data/processed/H39-catalysts-vs-fields/steps/steps_results.json`. 26 kickoffs (content usable in 20; the 2025 periods #2–#8 have too few 30-min content windows).

| Kickoff | era | agents | B4 class | B4 φ pct | B4 K (pct) | Δπ work, chat, idle | C6 class | C6 φ pct | C6 K pct |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| K02-03 | I-early | 4 | neither | 89 | +0.112 (84) | -0.122, +0.217, -0.083 | – | nan | nan |
| K03-04 | I-early | 4 | neither | 80 | +0.270 (96) | +0.083, -0.167, +0.078 | – | nan | nan |
| K04-05 | I-early | 4 | field | 98 | +0.778 (96) | +0.306, +0.148, -0.462 | – | nan | nan |
| K05-06 | I-early | 4 | neither | 80 | -0.066 (16) | +0.132, -0.150, +0.015 | – | nan | nan |
| K06-07 (coincides with B (human helpers, 2025-07-16)) | I-early | 4 | neither | 89 | +0.163 (93) | +0.002, +0.101, -0.103 | – | nan | nan |
| K07-08 | I-early | 4 | neither | 67 | +0.035 (49) | -0.006, -0.086, +0.088 | – | nan | nan |
| K10-11 | I-4h | 7 | neither | 84 | -0.046 (12) | -0.132, +0.048, +0.090 | neither | 67 | 93 |
| K11-12 | I-4h | 7 | neither | 42 | -0.032 (12) | -0.048, +0.046, +0.002 | neither | 0 | 23 |
| K12-13 | I-4h | 6 | catalyst | 21 | -0.104 (2) | +0.030, -0.035, +0.002 | neither | 0 | 56 |
| K16-17 | I-4h | 7 | neither | 84 | +0.057 (72) | -0.132, +0.064, +0.062 | neither | 49 | 93 |
| K17-18 | I-4h | 7 | neither | 93 | +0.055 (72) | +0.178, -0.011, -0.161 | neither | 56 | 30 |
| K18-19 | I-4h | 7 | neither | 47 | +0.006 (47) | -0.055, +0.049, +0.003 | neither | 56 | 79 |
| K19-20 | I-4h | 8 | catalyst | 77 | +0.166 (100) | +0.108, -0.038, -0.075 | neither | 65 | 51 |
| K20-21 | I-4h | 8 | neither | 72 | +0.094 (88) | +0.103, -0.063, -0.040 | neither | 79 | 70 |
| K23-24 | I-4h | 10 | neither | 37 | +0.025 (53) | +0.046, -0.028, -0.018 | neither | 86 | 63 |
| K24-25 | I-4h | 10 | field | 98 | -0.050 (12) | -0.203, +0.115, +0.095 | neither | 70 | 14 |
| K25-26 | I-4h | 10 | neither | 53 | -0.005 (33) | -0.041, +0.058, -0.012 | neither | 19 | 77 |
| K26-27 | I-4h | 10 | both | 100 | +0.141 (98) | +0.274, -0.115, -0.169 | neither | 28 | 63 |
| K30-31 | I-4h | 11 | catalyst | 19 | +0.133 (98) | -0.027, +0.021, +0.007 | neither | 60 | 65 |
| K35-36 (post side cut at the 03-24 regime boundary) | II | 12 | neither | 55 | +0.058 (71) | -0.069, +0.012, +0.059 | field | 99 | 26 |
| K36-37 (pre side includes NE16 (03-26)) | III-4h | 12 | field | 100 | -0.067 (25) | -0.053, -0.011, +0.093 | both | 100 | 100 |
| K37-38 | III-4h | 12 | catalyst | 83 | +0.162 (100) | +0.053, +0.032, -0.056 | field | 100 | 8 |
| K38-39 | III-4h | 14 | field | 100 | +0.024 (83) | +0.085, -0.027, +0.012 | field | 100 | 8 |
| K39-40 (NE42 merge (05-04)) | III-4h | 15 | neither | 67 | +0.089 (92) | -0.020, +0.039, -0.030 | neither | 92 | 83 |
| K40-41 (NE42 split (05-11)) | III-4h | 15 | both | 100 | +0.102 (100) | -0.107, +0.021, +0.107 | neither | 83 | 92 |
| K41-42 | III-4h | 15 | field | 100 | +0.006 (67) | +0.052, -0.050, -0.027 | field | 92 | 17 |

| P5 part | observed | verdict |
| --- | --- | --- |
| content φ above placebo p95 in ≥ 70% | 25% (5/20; 4/20 at or above the 95th percentile rank) | ✗ |
| content K above placebo median in ≥ 60% | 65% | ✓ |
| behavior φ above placebo p95 in ≤ 30% | 27% | ✓ |
| behavior K inside placebo band in ≥ 70% | 77% | ✓ |

- Behavior: individually 27% of kickoffs exceed the placebo p95, but the kickoffs taken together do shift occupancy more than ordinary day boundaries (Stouffer p = 0.0001); the mean shift is small (work +0.017, idle -0.020).
- Content: strongly era-dependent. Regime-III kickoffs (#36 → #42) exceed the placebo p95 in 4 of 6; regime-I 4-h kickoffs in 0 of 13, because content already changes as much between two ordinary days of a regime-I goal (placebo content TV median 0.56 vs 0.29 in regime III).

## Notes
- Run 2026-10-04; placebos are within-goal day boundaries of the same era (regime × hours) and window shape, excluding ±1 day around the tested scaffold steps.
