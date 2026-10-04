# H04 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 2026-04-24)

**Verdict:** failed
**Role:** replication (round 1b, non-holdout; folder created 2026-10-04 after the round-1b run: the prediction is the card's P1–P2 of 2026-10-03, applied unchanged; the period verdict rule below was set at folder creation)
**Period:** regime III · mode C · N ≈ 12 · #best / #rest · 17 non-holdout days, 4 h.

## Why this period
One of the four non-holdout periods with enough nudges for a per-period kernel (round 1 pooled regime III; per-period kernels were its round-2 task). Replication layer: the same corrected estimator on every eligible period.

## Prediction
*The card's exploratory predictions, written 2026-10-03 before any response was computed (templated, labelled as such):*
- **P1 nudge → target:** A60 CI excludes 0; peak lag ≤ 5 min; 1/e relaxation 3–30 min.
- **P2 nudge → bystanders:** 0 ≤ A60(bystander) / A60(target) ≤ 0.2.
- **Period rule (set at folder creation):** supported if P1 and P2 hold; failed if the target A60 point estimate is ≤ 0; mixed otherwise; descriptive if < 30 target cells.

## Result
*Run 2026-10-04 (`analysis/r1b.py --suite G38`; `data/processed/H04-reversible-forcing/r1b/G38.json`). Round-1b design: `activity_bins_fixed`, leading-@ target, every nudge treated (no future-kick isolation), controls eligible on past information only, day fixed effect, presence mask; day-block bootstrap (1,000).*

| Statistic | Value |
| --- | --- |
| nudges · target cells | 110 · 98 (strata fallback 52%) |
| target A30 (extra active min over 30 min) | +0.38 [-0.53, +1.29] |
| target A60 | -0.06 [-2.03, +1.53] |
| peak lag · 1/e relaxation · onset t₂₅ | 9 min · 3 min · 9 min |
| placebo window [−30, −16] | -0.17 [-0.77, +0.32] |
| first nudges (no direct kick in the previous 30 min) A30 | +0.24 [-0.96, +1.28] (n = 66) |
| repeat nudges (nudged in the previous 60 min) A30 | -0.15 [-1.50, +1.02] (n = 43) |
| round-1 isolation rule inside this estimator, A30 | +0.29 [-1.47, +1.72] (n = 43) |
| bystanders A60 · ratio to target | +0.06 [-0.44, +0.61] · -0.92 |
| read-out delay to the target's receiving call (median, q90) | 64 s, 361 s |

| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 | A60 -0.06 [-2.03, +1.53]; peak 9 min; relax 3 min | fail |
| P2 | ratio -0.92 | fail |

**Verdict: failed.**

## Notes
- 2026-10-04: created in the round-1b re-evaluation (replication layer).
