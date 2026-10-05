# H43 × G37: kick refractory window (2026-03-30 → 2026-04-01)

**Verdict:** descriptive
**Role:** replication
**Period:** regime III · 12 agents · 2 room(s) · 3 non-holdout days. Units (matching strata, `period_units`): 37.

## Why this period
Replication layer: the common estimator on every eligible non-holdout period, so that fitted refractory windows are comparable phase-diagram points. Nothing period-specific is claimed here; the native tests are NE43, G38 and G04.

Structural counts (treatment structure only, no outcomes; primary read state per class; second kicks within 240 min):
| Class | kick-receiving calls | primers (30-min quiet) | in primary read state | second kicks |
| --- | --- | --- | --- | --- |
| N | 22 | 9 | 5 | 3 |
| H | 25 | 0 | 0 | 0 |
| A | 471 | 59 | 42 | 49 |

Writes per agent-day: 5.53 (O3 computed only if ≥ 1).

## Prediction
*Written 2026-10-04, before running on this period. Templated (replication layer; card, "Replication layer").*
Every powered class (≥ 20 primers in the primary read state and ≥ 20 second kicks) whose first-kick effect is positive (E1 day-bootstrap 95% CI above 0) has R(short) < R(long) and a refractory window δ½ within a factor 2 of the median launched-episode length L̃. Powered by structure here: @-mentions (O2, busy recipients). Synthetic power (card, Synthetic validation): only mention curves are resolvable at G51 size; elsewhere expect wide intervals.
Verdict rule: all testable classes pass → supported; none → failed; some → mixed; no testable class → descriptive.

## Result
Run 2026-10-04 with `analysis/run_period.py --period G37` (B = 300 two-way day-block bootstrap draws); numbers in `data/processed/H43-kick-refractory-window/G37/results.json`.
Effects are pooled log hazard ratios over the outcome window (E1: isolated first kick vs matched no-kick calls; E2: second kick vs post-primer calls without one, same spacing bin). R = E2/E1 with E1 standardized to the second kicks' stratum mix; R is meaningful only where E1 > 0.

| Class | outcome | primers / second kicks | E1 (lnHR) | R (0–15 min] | R (15–60] | R (60–240] | δ½ (min) vs L̃ | test |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| N | O1 | 5 / 0 | 2.10 [0.50, 2.91] | – | – | – | – vs L̃ 26 | underpowered (< 20 primers or < 20 second kicks) |
| H | O2 | 0 | – | – | – | – | – | no primers in the primary read state |
| A | O2 | 42 / 36 | 0.50 [-0.33, 1.27] | 3.26 [-10.35, 3.26] | -2.82 [-3.05, 4.74] | – | – vs L̃ 20 | no first-kick effect (E1 CI includes 0) |

Templated verdict: **descriptive**. A test "passes" when R(short) < R(long) and δ½ lies within [L̃/2, 2L̃]; "underpowered" or "no first-kick effect" classes do not count.

## Round 2 (2026-10-05): pooled timer-wake test (card R5)
*Prediction (card R5-P1, written before the run): a directed read at an after-PAUSE timer wake works as well after an effective isolated directed primer (re-kicked) as at a fresh wake (no directed read in 60 min). Read only inside the partial pooling; this period is too small to decide alone.*

| Quantity | Value |
| --- | --- |
| directed wakes, fresh / re-kicked | 7 / 29 (3 days) |
| escape at the wake, fresh: no read / read | 0.25 / 0.86 (28 / 7 wakes) |
| escape at the wake, re-kicked: no read / read | 0.73 / 0.79 (117 / 29) |
| log OR fresh / re-kicked (N(0, 2.5²) prior, post hoc: separation) | +2.48 [1.57, 3.44] / +0.68 [0.08, 3.07] |
| re-kicked − fresh | −1.81 [−3.25, +1.12] |

Reading: the point estimate is a large reduction, but 7 fresh directed wakes and a CI that spans 0 make it uninformative alone. Round-2 role: one of four periods in the partial pooling. Verdict unchanged (descriptive).
