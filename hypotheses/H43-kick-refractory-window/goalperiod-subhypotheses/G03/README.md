# H43 × G03: kick refractory window (2025-05-12 → 2025-05-14)

**Verdict:** descriptive
**Role:** replication
**Period:** regime I · 4 agents · 1 room(s) · 3 non-holdout days. Units (matching strata, `period_units`): 3.

## Why this period
Replication layer: the common estimator on every eligible non-holdout period, so that fitted refractory windows are comparable phase-diagram points. Nothing period-specific is claimed here; the native tests are NE43, G38 and G04.

Structural counts (treatment structure only, no outcomes; primary read state per class; second kicks within 240 min):
| Class | kick-receiving calls | primers (30-min quiet) | in primary read state | second kicks |
| --- | --- | --- | --- | --- |
| N | 0 | 0 | 0 | 0 |
| H | 245 | 1 | 1 | 1 |
| A | 781 | 2 | 2 | 2 |

Writes per agent-day: 0.0 (O3 computed only if ≥ 1).

## Prediction
*Written 2026-10-04, before running on this period. Templated (replication layer; card, "Replication layer").*
Every powered class (≥ 20 primers in the primary read state and ≥ 20 second kicks) whose first-kick effect is positive (E1 day-bootstrap 95% CI above 0) has R(short) < R(long) and a refractory window δ½ within a factor 2 of the median launched-episode length L̃. Powered by structure here: none (expected verdict: descriptive). Synthetic power (card, Synthetic validation): only mention curves are resolvable at G51 size; elsewhere expect wide intervals.
Verdict rule: all testable classes pass → supported; none → failed; some → mixed; no testable class → descriptive.

## Result
Run 2026-10-04 with `analysis/run_period.py --period G03` (B = 300 two-way day-block bootstrap draws); numbers in `data/processed/H43-kick-refractory-window/G03/results.json`.
Effects are pooled log hazard ratios over the outcome window (E1: isolated first kick vs matched no-kick calls; E2: second kick vs post-primer calls without one, same spacing bin). R = E2/E1 with E1 standardized to the second kicks' stratum mix; R is meaningful only where E1 > 0.

| Class | outcome | primers / second kicks | E1 (lnHR) | R (0–15 min] | R (15–60] | R (60–240] | δ½ (min) vs L̃ | test |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| N | O1 | 0 | – | – | – | – | – | no primers in the primary read state |
| H | O2 | 1 / 1 | 0.00 [0.00, 0.00] | – | – | – | – vs L̃ – | underpowered (< 20 primers or < 20 second kicks) |
| A | O2 | 2 / 0 | -1.61 [-2.56, -1.61] | – | – | – | – vs L̃ – | underpowered (< 20 primers or < 20 second kicks) |

Templated verdict: **descriptive**. A test "passes" when R(short) < R(long) and δ½ lies within [L̃/2, 2L̃]; "underpowered" or "no first-kick effect" classes do not count.
