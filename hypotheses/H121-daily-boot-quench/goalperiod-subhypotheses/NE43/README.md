# H121 × NE43: the operator's daily pause/resume messages stop (2026-08-05, inside #51)

**Verdict:** mixed
**Role:** native (exploratory)
**Period:** regime III · #51 · before = unit 51f (07-29 → 08-04, 5 days) · after = the first 5 active days of unit 51g (08-05 → 08-11) · N ≈ 27. The nudge stop (08-20) is outside both windows.

## Why this period
Before 08-05 the operator posted a resume message at every daily start; after it the runner starts the agents silently (NE43(a)). If the boot transient is a response to the resume message (an exogenous kick read at the first calls), it should shrink or change τ. If it is the runner's start plus the agents' own start-up routine, nothing changes. H38 found the day-edge share of co-activation did not drop on 08-05.

## Prediction
*Written 2026-10-04 22:08 UTC, before running on this period.*
- **P-NE43a (credence 0.55):** τ_boot changes by less than ×1.5 (ratio after/before in [0.67, 1.5]).
- **P-NE43b (credence 0.4):** the boot amplitude |A| falls by ≥ 20% after 08-05 (part of the morning talk answers the resume message).
- Mean field (H121's model) predicts no change in either, because g_lag and τ₀ are unchanged.
- Counts against P-NE43a: a ratio outside [0.67, 1.5] with CI excluding the band edge.

## Result
*Registered estimator.* Before (51f, 135 agent-days) the single-exponential fit sits at the upper bound (τ = 1175 calls); after (51g days 1–5, 134 agent-days) it sits at the lower bound (0.2 calls). The τ ratio (0.0002, CI [0.0002, 24]) and the amplitude ratio (−0.43, CI [−1.7, 2.7]) are both uninformative. P-NE43a and P-NE43b cannot be scored: **mixed**.

*Post hoc (labelled)*: late #51 has **no first-call talk spike on either side**: excess at k = 0 over the k = 20–60 plateau is −0.010 [−0.034, +0.020] before and −0.025 [−0.047, −0.004] after. The operator's resume message did not produce a morning talk spike even while it was posted. The slow excess (talk at k = 20–240 over the steady state) is +0.13 [−0.07, +0.35] before and +0.17 [+0.07, +0.32] after. The slow component does not depend on the resume message either, consistent with H38's finding that the day edges are the runner's schedule.

Data: `data/processed/H121-daily-boot-quench/results/natives.json`, `posthoc.json`.

## Scorecard (period-specific axes)
E, G (agreement with H38's NE43 finding).

## Notes
