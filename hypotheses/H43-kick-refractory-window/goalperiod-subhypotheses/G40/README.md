# H43 × G40: kick refractory window (2026-05-04 → 2026-05-08)

**Verdict:** descriptive
**Role:** replication
**Period:** regime III · 15 agents · 1 room(s) · 5 non-holdout days. Units (matching strata, `period_units`): 40.

## Why this period
Replication layer: the common estimator on every eligible non-holdout period, so that fitted refractory windows are comparable phase-diagram points. Nothing period-specific is claimed here; the native tests are NE43, G38 and G04.

Structural counts (treatment structure only, no outcomes; primary read state per class; second kicks within 240 min):
| Class | kick-receiving calls | primers (30-min quiet) | in primary read state | second kicks |
| --- | --- | --- | --- | --- |
| N | 11 | 5 | 2 | 2 |
| H | 30 | 0 | 0 | 0 |
| A | 1275 | 98 | 78 | 88 |

Writes per agent-day: 39.31 (O3 computed only if ≥ 1).

## Prediction
*Written 2026-10-04, before running on this period. Templated (replication layer; card, "Replication layer").*
Every powered class (≥ 20 primers in the primary read state and ≥ 20 second kicks) whose first-kick effect is positive (E1 day-bootstrap 95% CI above 0) has R(short) < R(long) and a refractory window δ½ within a factor 2 of the median launched-episode length L̃. Powered by structure here: @-mentions (O2, busy recipients). Synthetic power (card, Synthetic validation): only mention curves are resolvable at G51 size; elsewhere expect wide intervals.
Verdict rule: all testable classes pass → supported; none → failed; some → mixed; no testable class → descriptive.

## Result
Run 2026-10-04 with `analysis/run_period.py --period G40` (B = 300 two-way day-block bootstrap draws); numbers in `data/processed/H43-kick-refractory-window/G40/results.json`.
Effects are pooled log hazard ratios over the outcome window (E1: isolated first kick vs matched no-kick calls; E2: second kick vs post-primer calls without one, same spacing bin). R = E2/E1 with E1 standardized to the second kicks' stratum mix; R is meaningful only where E1 > 0.

| Class | outcome | primers / second kicks | E1 (lnHR) | R (0–15 min] | R (15–60] | R (60–240] | δ½ (min) vs L̃ | test |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| N | O1 | 2 / 0 | 0.01 [0.00, 0.02] | – | – | – | – vs L̃ 36 | underpowered (< 20 primers or < 20 second kicks) |
| H | O2 | 0 | – | – | – | – | – | no primers in the primary read state |
| A | O2 | 78 / 82 | 0.22 [-0.07, 0.57] | 0.30 [-10.47, 3.07] | 1.66 [-7.28, 69.39] | 3.94 [-45.22, 36.21] | – vs L̃ 44 | no first-kick effect (E1 CI includes 0) |

Templated verdict: **descriptive**. A test "passes" when R(short) < R(long) and δ½ lies within [L̃/2, 2L̃]; "underpowered" or "no first-kick effect" classes do not count.
