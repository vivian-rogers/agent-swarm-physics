# H04 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 2026-09-04 (non-holdout))

**Verdict:** supported
**Role:** replication (round 1b, non-holdout; folder created 2026-10-04 after the round-1b run: the prediction is the card's P1–P2 of 2026-10-03, applied unchanged; the period verdict rule below was set at folder creation)
**Period:** regime III · mode P · N 21 → 32 · #general · 45 non-holdout days, 8 h; nudges end 08-20 (NE43).

## Why this period
One of the four non-holdout periods with enough nudges for a per-period kernel (round 1 pooled regime III; per-period kernels were its round-2 task). Replication layer: the same corrected estimator on every eligible period.

## Prediction
*The card's exploratory predictions, written 2026-10-03 before any response was computed (templated, labelled as such):*
- **P1 nudge → target:** A60 CI excludes 0; peak lag ≤ 5 min; 1/e relaxation 3–30 min.
- **P2 nudge → bystanders:** 0 ≤ A60(bystander) / A60(target) ≤ 0.2.
- **Period rule (set at folder creation):** supported if P1 and P2 hold; failed if the target A60 point estimate is ≤ 0; mixed otherwise; descriptive if < 30 target cells.

## Result
*Run 2026-10-04 (`analysis/r1b.py --suite G51`; `data/processed/H04-reversible-forcing/r1b/G51.json`). Round-1b design: `activity_bins_fixed`, leading-@ target, every nudge treated (no future-kick isolation), controls eligible on past information only, day fixed effect, presence mask; day-block bootstrap (1,000).*

| Statistic | Value |
| --- | --- |
| nudges · target cells | 729 · 697 (strata fallback 16%) |
| target A30 (extra active min over 30 min) | +1.16 [+0.75, +1.57] |
| target A60 | +1.65 [+0.79, +2.52] |
| peak lag · 1/e relaxation · onset t₂₅ | 4 min · 29 min · 7 min |
| placebo window [−30, −16] | +0.25 [+0.05, +0.46] |
| first nudges (no direct kick in the previous 30 min) A30 | +1.38 [+0.92, +1.83] (n = 483) |
| repeat nudges (nudged in the previous 60 min) A30 | +0.90 [+0.31, +1.53] (n = 314) |
| round-1 isolation rule inside this estimator, A30 | +1.48 [+0.88, +2.06] (n = 302) |
| bystanders A60 · ratio to target | +0.04 [-0.08, +0.16] · 0.03 |
| read-out delay to the target's receiving call (median, q90) | 108 s, 333 s |

| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 | A60 +1.65 [+0.79, +2.52]; peak 4 min; relax 29 min | pass |
| P2 | ratio 0.03 | pass |

**Verdict: supported.**

## Notes
- 2026-10-04: created in the round-1b re-evaluation (replication layer).
