# H04 × G41: Perform novel research! (2026-05-11 → 2026-05-15)

**Verdict:** mixed
**Role:** replication (round 1b, non-holdout; folder created 2026-10-04 after the round-1b run: the prediction is the card's P1–P2 of 2026-10-03, applied unchanged; the period verdict rule below was set at folder creation)
**Period:** regime III · mode I · N ≈ 15 · #best / #rest · 5 days, 4 h.

## Why this period
One of the four non-holdout periods with enough nudges for a per-period kernel (round 1 pooled regime III; per-period kernels were its round-2 task). Replication layer: the same corrected estimator on every eligible period.

## Prediction
*The card's exploratory predictions, written 2026-10-03 before any response was computed (templated, labelled as such):*
- **P1 nudge → target:** A60 CI excludes 0; peak lag ≤ 5 min; 1/e relaxation 3–30 min.
- **P2 nudge → bystanders:** 0 ≤ A60(bystander) / A60(target) ≤ 0.2.
- **Period rule (set at folder creation):** supported if P1 and P2 hold; failed if the target A60 point estimate is ≤ 0; mixed otherwise; descriptive if < 30 target cells.

## Result
*Run 2026-10-04 (`analysis/r1b.py --suite G41`; `data/processed/H04-reversible-forcing/r1b/G41.json`). Round-1b design: `activity_bins_fixed`, leading-@ target, every nudge treated (no future-kick isolation), controls eligible on past information only, day fixed effect, presence mask; day-block bootstrap (1,000).*

| Statistic | Value |
| --- | --- |
| nudges · target cells | 59 · 55 (strata fallback 62%) |
| target A30 (extra active min over 30 min) | +1.59 [-0.17, +3.38] |
| target A60 | +2.56 [-0.98, +5.21] |
| peak lag · 1/e relaxation · onset t₂₅ | 31 min · 4 min · 8 min |
| placebo window [−30, −16] | +0.70 [-0.71, +1.92] |
| first nudges (no direct kick in the previous 30 min) A30 | +1.64 [+0.48, +2.74] (n = 26) |
| repeat nudges (nudged in the previous 60 min) A30 | +1.35 [-1.02, +4.90] (n = 33) |
| round-1 isolation rule inside this estimator, A30 | +1.48 [-0.58, +2.10] (n = 15) |
| bystanders A60 · ratio to target | +0.32 [-0.13, +0.94] · 0.12 |
| read-out delay to the target's receiving call (median, q90) | 26 s, 359 s |

| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 | A60 +2.56 [-0.98, +5.21]; peak 31 min; relax 4 min | fail |
| P2 | ratio 0.12 | pass |

**Verdict: mixed.**

## Notes
- 2026-10-04: created in the round-1b re-evaluation (replication layer).
