# H43 × G27: kick refractory window (2026-01-12 → 2026-01-23)

**Verdict:** failed
**Role:** replication
**Period:** regime I · 10 agents · 1 room(s) · 10 non-holdout days. Units (matching strata, `period_units`): 27.

## Why this period
Replication layer: the common estimator on every eligible non-holdout period, so that fitted refractory windows are comparable phase-diagram points. Nothing period-specific is claimed here; the native tests are NE43, G38 and G04.

Structural counts (treatment structure only, no outcomes; primary read state per class; second kicks within 240 min):
| Class | kick-receiving calls | primers (30-min quiet) | in primary read state | second kicks |
| --- | --- | --- | --- | --- |
| N | 0 | 0 | 0 | 0 |
| H | 67 | 5 | 4 | 0 |
| A | 2535 | 156 | 145 | 142 |

Writes per agent-day: 0.63 (O3 computed only if ≥ 1).

## Prediction
*Written 2026-10-04, before running on this period. Templated (replication layer; card, "Replication layer").*
Every powered class (≥ 20 primers in the primary read state and ≥ 20 second kicks) whose first-kick effect is positive (E1 day-bootstrap 95% CI above 0) has R(short) < R(long) and a refractory window δ½ within a factor 2 of the median launched-episode length L̃. Powered by structure here: @-mentions (O2, busy recipients). Synthetic power (card, Synthetic validation): only mention curves are resolvable at G51 size; elsewhere expect wide intervals.
Verdict rule: all testable classes pass → supported; none → failed; some → mixed; no testable class → descriptive.

## Result
Run 2026-10-04 with `analysis/run_period.py --period G27` (B = 300 two-way day-block bootstrap draws); numbers in `data/processed/H43-kick-refractory-window/G27/results.json`.
Effects are pooled log hazard ratios over the outcome window (E1: isolated first kick vs matched no-kick calls; E2: second kick vs post-primer calls without one, same spacing bin). R = E2/E1 with E1 standardized to the second kicks' stratum mix; R is meaningful only where E1 > 0.

| Class | outcome | primers / second kicks | E1 (lnHR) | R (0–15 min] | R (15–60] | R (60–240] | δ½ (min) vs L̃ | test |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| N | O1 | 0 | – | – | – | – | – | no primers in the primary read state |
| H | O2 | 4 / 0 | 0.36 [0.08, 0.68] | – | – | – | – vs L̃ 7 | underpowered (< 20 primers or < 20 second kicks) |
| A | O2 | 145 / 132 | 0.65 [0.39, 0.87] | 0.48 [-0.11, 1.24] | -0.07 [-3.04, 2.10] | 0.81 [-0.87, 2.95] | 87.5 [0.0, 332.7] vs L̃ 5 | fail |

Templated verdict: **failed**. A test "passes" when R(short) < R(long) and δ½ lies within [L̃/2, 2L̃]; "underpowered" or "no first-kick effect" classes do not count.
