# H43 × G51: kick refractory window (2026-07-06 → 2026-09-04)

**Verdict:** failed
**Role:** replication
**Period:** regime III · 32 agents · 2 room(s) · 45 non-holdout days. Units (matching strata, `period_units`): 51a, 51b, 51c, 51d, 51e, 51f, 51g, 51h, 51i, 51j, 51k, 51l.

## Why this period
Replication layer: the common estimator on every eligible non-holdout period, so that fitted refractory windows are comparable phase-diagram points. Nothing period-specific is claimed here; the native tests are NE43, G38 and G04.

Structural counts (treatment structure only, no outcomes; primary read state per class; second kicks within 240 min):
| Class | kick-receiving calls | primers (30-min quiet) | in primary read state | second kicks |
| --- | --- | --- | --- | --- |
| N | 970 | 302 | 259 | 196 |
| H | 1805 | 382 | 209 | 203 |
| A | 32071 | 3150 | 1904 | 2804 |

Writes per agent-day: 46.93 (O3 computed only if ≥ 1).

## Prediction
*Written 2026-10-04, before running on this period. Templated (replication layer; card, "Replication layer").*
Every powered class (≥ 20 primers in the primary read state and ≥ 20 second kicks) whose first-kick effect is positive (E1 day-bootstrap 95% CI above 0) has R(short) < R(long) and a refractory window δ½ within a factor 2 of the median launched-episode length L̃. Powered by structure here: nudges (O1, idle recipients), human messages (O2, busy recipients), @-mentions (O2, busy recipients). Synthetic power (card, Synthetic validation): only mention curves are resolvable at G51 size; elsewhere expect wide intervals.
Verdict rule: all testable classes pass → supported; none → failed; some → mixed; no testable class → descriptive.

## Result
Run 2026-10-04 with `analysis/run_period.py --period G51` (B = 300 two-way day-block bootstrap draws); numbers in `data/processed/H43-kick-refractory-window/G51/results.json`.
Effects are pooled log hazard ratios over the outcome window (E1: isolated first kick vs matched no-kick calls; E2: second kick vs post-primer calls without one, same spacing bin). R = E2/E1 with E1 standardized to the second kicks' stratum mix; R is meaningful only where E1 > 0.

| Class | outcome | primers / second kicks | E1 (lnHR) | R (0–15 min] | R (15–60] | R (60–240] | δ½ (min) vs L̃ | test |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| N | O1 | 259 / 159 | 0.07 [-0.19, 0.28] | 3.13 [-24.27, 83.54] | 1.23 [-0.09, 6.59] | 1.09 [-0.46, 9.45] | – vs L̃ 7 | no first-kick effect (E1 CI includes 0) |
| H | O2 | 209 / 104 | 0.62 [0.24, 1.02] | 0.49 [-0.43, 2.23] | -0.22 [-6.64, 2.77] | 0.67 [-3.47, 3.71] | 133.3 [0.0, 332.7] vs L̃ 31 | fail |
| A | O2 | 1904 / 1931 | 0.74 [0.63, 0.84] | 0.76 [0.60, 1.01] | 0.92 [0.58, 1.31] | 0.89 [0.47, 1.43] | 0.0 [0.0, 1.6] vs L̃ 20 | fail |

Templated verdict: **failed**. A test "passes" when R(short) < R(long) and δ½ lies within [L̃/2, 2L̃]; "underpowered" or "no first-kick effect" classes do not count.
