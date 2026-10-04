# H04 × G44: Finetune your leader! (2026-05-26 → 2026-05-29)

**Verdict:** descriptive
**Role:** replication (round 1b, non-holdout; folder created 2026-10-04 after the round-1b run: the prediction is the card's P1–P2 of 2026-10-03, applied unchanged; the period verdict rule below was set at folder creation)
**Period:** regime III · mode C · N ≈ 16 · #best / #rest · 4 non-holdout days, 4 h.

## Why this period
One of the four non-holdout periods with enough nudges for a per-period kernel (round 1 pooled regime III; per-period kernels were its round-2 task). Replication layer: the same corrected estimator on every eligible period.

## Prediction
*The card's exploratory predictions, written 2026-10-03 before any response was computed (templated, labelled as such):*
- **P1 nudge → target:** A60 CI excludes 0; peak lag ≤ 5 min; 1/e relaxation 3–30 min.
- **P2 nudge → bystanders:** 0 ≤ A60(bystander) / A60(target) ≤ 0.2.
- **Period rule (set at folder creation):** supported if P1 and P2 hold; failed if the target A60 point estimate is ≤ 0; mixed otherwise; descriptive if < 30 target cells.

## Result
*Run 2026-10-04 (`analysis/r1b.py --suite G44`; `data/processed/H04-reversible-forcing/r1b/G44.json`). Round-1b design: `activity_bins_fixed`, leading-@ target, every nudge treated (no future-kick isolation), controls eligible on past information only, day fixed effect, presence mask; day-block bootstrap (1,000).*

| Statistic | Value |
| --- | --- |
| nudges · target cells | 28 · 24 (strata fallback 67%) |
| target A30 (extra active min over 30 min) | +2.11 [+1.52, +2.42] |
| target A60 | +2.01 [-0.04, +3.98] |
| peak lag · 1/e relaxation · onset t₂₅ | 4 min · 3 min · 4 min |
| placebo window [−30, −16] | +0.45 [-0.19, +1.33] |
| first nudges (no direct kick in the previous 30 min) A30 | +4.13 [+2.32, +6.43] (n = 16) |
| repeat nudges (nudged in the previous 60 min) A30 | +0.65 [-3.58, +6.48] (n = 8) |
| round-1 isolation rule inside this estimator, A30 | +7.27 [+4.03, +10.57] (n = 10) |
| bystanders A60 · ratio to target | -0.60 [-1.22, +0.92] · -0.30 |
| read-out delay to the target's receiving call (median, q90) | 16 s, 218 s |

| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 | A60 +2.01 [-0.04, +3.98]; peak 4 min; relax 3 min | fail |
| P2 | ratio -0.30 | fail |

**Verdict: descriptive.**

## Notes
- 2026-10-04: created in the round-1b re-evaluation (replication layer).
