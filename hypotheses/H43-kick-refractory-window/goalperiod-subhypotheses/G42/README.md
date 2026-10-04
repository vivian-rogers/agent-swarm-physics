# H43 × G42: kick refractory window (2026-05-18 → 2026-05-22)

**Verdict:** failed
**Role:** replication
**Period:** regime III · 16 agents · 2 room(s) · 5 non-holdout days. Units (matching strata, `period_units`): 42a, 42b.

## Why this period
Replication layer: the common estimator on every eligible non-holdout period, so that fitted refractory windows are comparable phase-diagram points. Nothing period-specific is claimed here; the native tests are NE43, G38 and G04.

Structural counts (treatment structure only, no outcomes; primary read state per class; second kicks within 240 min):
| Class | kick-receiving calls | primers (30-min quiet) | in primary read state | second kicks |
| --- | --- | --- | --- | --- |
| N | 27 | 6 | 3 | 1 |
| H | 84 | 5 | 4 | 3 |
| A | 1063 | 118 | 102 | 98 |

Writes per agent-day: 20.72 (O3 computed only if ≥ 1).

## Prediction
*Written 2026-10-04, before running on this period. Templated (replication layer; card, "Replication layer").*
Every powered class (≥ 20 primers in the primary read state and ≥ 20 second kicks) whose first-kick effect is positive (E1 day-bootstrap 95% CI above 0) has R(short) < R(long) and a refractory window δ½ within a factor 2 of the median launched-episode length L̃. Powered by structure here: @-mentions (O2, busy recipients). Synthetic power (card, Synthetic validation): only mention curves are resolvable at G51 size; elsewhere expect wide intervals.
Verdict rule: all testable classes pass → supported; none → failed; some → mixed; no testable class → descriptive.

## Result
Run 2026-10-04 with `analysis/run_period.py --period G42` (B = 300 two-way day-block bootstrap draws); numbers in `data/processed/H43-kick-refractory-window/G42/results.json`.
Effects are pooled log hazard ratios over the outcome window (E1: isolated first kick vs matched no-kick calls; E2: second kick vs post-primer calls without one, same spacing bin). R = E2/E1 with E1 standardized to the second kicks' stratum mix; R is meaningful only where E1 > 0.

| Class | outcome | primers / second kicks | E1 (lnHR) | R (0–15 min] | R (15–60] | R (60–240] | δ½ (min) vs L̃ | test |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| N | O1 | 3 / 0 | -0.85 [-2.56, 0.00] | – | – | – | – vs L̃ 19 | underpowered (< 20 primers or < 20 second kicks) |
| H | O2 | 4 / 3 | 0.17 [0.13, 0.17] | – | – | – | – vs L̃ 112 | underpowered (< 20 primers or < 20 second kicks) |
| A | O2 | 102 / 83 | 0.59 [0.29, 1.24] | 1.27 [-0.39, 3.34] | 1.97 [0.06, 6.01] | – | 0.0 [0.0, 292.7] vs L̃ 56 | fail |

Templated verdict: **failed**. A test "passes" when R(short) < R(long) and δ½ lies within [L̃/2, 2L̃]; "underpowered" or "no first-kick effect" classes do not count.
