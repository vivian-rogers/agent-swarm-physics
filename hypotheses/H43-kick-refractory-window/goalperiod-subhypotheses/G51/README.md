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

## Round 2 (2026-10-05): nudger selection, the k-th kick in one read, timer wakes (card R2, R3, R5)
*Predictions written in the card before the run (R2-P1…P5, R3-P1…P6, R5-P1…P4), with amendments A2-1…A2-4 after the synthetic validation and before any outcome. Role: native for R2 (the nudger exists only in #51 before 08-21), replication for R3 and R5. NE43 (R6) has its own folder.*

| Test | Observed (day-bootstrap 95% CI) | Outcome |
| --- | --- | --- |
| R2 re-fired − first nudge, sustained escape at the wake (proxy model; 182 first, 374 re-fires; before 08-21) | −0.06 [−0.84, +0.61]; base +0.08; agent-day FE −0.24 | inconclusive (power 0.5): no re-fire advantage |
| R2 split | re-fire after a sustained run +0.28 [−0.36, +0.85] vs first; re-fire inside the same trap **−1.42 [−2.60, −0.37]** | same-trap re-fires lose the effect (refractoriness or selection of non-responsive traps) |
| R2 first nudge at the wake (post hoc reading) | +0.99 [0.28, 1.53] (proxy), +1.70 [1.27, 2.29] (base); raw escape at k 10–29: 0.28 vs 0.07 | contradicts round 1's "no sustained effect", which compared deep nudged traps with shallow quiet ones |
| R3 batching ratio ρ₂ (talk at the receiving call) | **0.11 [0.01, 0.21]**; m₃ −0.19 [−0.45, +0.03]; Gemini logged starts 0.08 [−0.10, 0.32]; no uncertain items 0.07; bounds 0.08 / 0.30 | holds: one read is one kick |
| R3 next-call kick (round-1 estimator, Gemini recipients) | R(δ ≤ 2 min) 0.68 [0.26, 1.14] vs 0.75 for the others | the short-spacing dip is not a start-placement artifact |
| R3 timer-wake ρ₂ (sustained escape) | 0.35 [−0.13, 0.92] | holds (about a third, as in H16) |
| R5 directed read at re-kicked vs fresh wakes | fresh +0.62 [0.41, 0.87], re-kicked +0.40 [0.26, 0.55]; difference −0.22 [−0.47, +0.04]; R_w 0.64 [0.38, 1.08] | partly: a shallow dip, not a window |

Verdict for this folder unchanged (failed under the round-1 replication template). Round 2 adds: one read is one kick here, and a nudge into an unbroken trap that ignored the previous nudge is wasted.
