# H80 × G38: (no-automation check) (2026-04-02 → 2026-04-24)

**Verdict:** failed
**Role:** native
**Period:** regime III · 12–14 agents · #best / #rest · 17 days · 1,393 agent work commits, 1 automated commit.

## Why this period
A long, dense regime-III period with almost no automation: the ground truth is "all windows are agent work". A classifier trained elsewhere must not invent scripts here (axis G: known structure; axis I: transfer).

## Prediction
*Written 2026-10-04, before running on this period.*
- **N2a:** classifiers trained on G51+post (all windows), with the threshold that gives 90% sensitivity in training, flag ≤ 5% of G38 windows as automated with C, and with C + A.
- **N2b:** C + A does not lower the false-positive rate by more than 0.02 compared with C (assembly adds no specificity).
- **N2c (scheduler):** T flags ≤ 5% as well. *Against:* T > 10% (timing transfers worse than sequence structure).

## Result
Data: `results/natives.json` (`G38`; post hoc variant `G38_posthoc_train_G51_inperiod`).

| Prediction | Observed (Wilson 95% CI), 63 agent windows | Verdict |
| --- | --- | --- |
| N2a C and C + A flag ≤ 5% | C 0.97 [0.89, 0.99]; C + A 0.97 | failed |
| N2b C + A lowers FPR by ≤ 0.02 | no change | supported |
| N2c T ≤ 5% | T 0.00 [0.00, 0.06]; T without the village-window feature 0.27 [0.18, 0.39] | supported (only with the window feature) |

Trained on G51+post, the 90%-sensitivity threshold must cover the post-period scripts, whose commits look like agent work, so the compression classifier flags nearly every G38 window. Post hoc, trained on the in-period cron stream only: C 0.21, C + A 0.16, A 0.25, T 0.00. The scheduler (village window, hour) transfers; sequence structure does not.

## Scorecard (period-specific axes)
- G: 0. Ground truth (no automation) is violated by the sequence classifiers; the scheduler passes.
- I: 0 for compression transfer; 1 for timing.

## Notes
- 2026-10-04: round 1 run.
