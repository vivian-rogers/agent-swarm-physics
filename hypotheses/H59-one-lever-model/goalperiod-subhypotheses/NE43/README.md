# H59 × NE43: nudger stop inside #51 (2026-08-21)

**Verdict:** supported
**Role:** native
**Period:** regime III · #51 head, non-holdout days to 2026-09-06 · 21–32 agents · split at 2026-08-21 (first day with no nudges; the bookends stopped earlier, 08-05). Exception (c): the transition is the object.

## Why this period
The nudger switches off inside one goal, room and roster era. If an input class's lever is a property of the class (H59), the triples of the classes that continue (A, Hu) should not move when another input class disappears, and a model fitted before should predict after.

## Prediction
*Written 2026-10-04, before running on this split.*
- The A and Hu triples (κ, h) fitted on post days (08-21 → 09-06) agree with the pre-day fits: both Δκ and Δh 95% day-bootstrap CIs include 0.
- The one-lever model fitted on pre days (with its θ, K and the A/Hu/Hm triples) predicts the post days' kicked transitions with ≥ 80% of the skill of a 5-fold day-CV refit on the post days (transfer ratio ≥ 0.8).
- Verdict: supported if both hold; failed if both fail; mixed otherwise.
- Counts against: a triple shift with CI excluding 0 for A (the lever depends on the drive context), or a transfer ratio < 0.8.

## Result
`data/processed/H59-one-lever-model/native/NE43.json` (pre: 34 days with N, Hu, Hm, A; post: 11 days with Hu, A; 40 day-bootstrap draws per side).

| | pre (nudger on) | post (off) | Δ (95% CI) |
| --- | --- | --- | --- |
| A κ | 0.13 [0.10, 0.16] | 0.17 [0.08, 0.30] | +0.03 [−0.06, 0.16] |
| A h | 3.85 [3.43, 4.13] | 3.45 [3.09, 4.52] | −0.40 [−0.87, 0.82] |
| Hu κ | −0.14 [−0.43, 0.23] | −0.08 [−0.43, 0.16] | +0.07 [−0.39, 0.36] |
| Hu h | 1.79 [0.44, 2.37] | 1.57 [−0.49, 4.10] | −0.21 [−1.89, 1.87] |
| θ, K₁ | 72.8°, 0.42 | 72.4°, 0.52 | – |

- **Triples invariant:** every Δ CI includes 0 ✓.
- **Transfer:** the pre-fitted model predicts the post days' kicked transitions slightly *better* than a 5-fold post refit: ratio 1.01 [1.005, 1.025] ✓.
- Verdict **supported**. The levers of the remaining classes do not depend on whether the nudger is running. Power after the stop is modest (11 days; Hu CIs are wide).

## Scorecard (period-specific axes)
E 1 (an invariance prediction across the step holds; no change in sign or size was predicted) · I 1 (transfer across the step).

## Notes
- Baseline (with day fixed effects) is fitted on all G51 days; only the kick parameters are split.
