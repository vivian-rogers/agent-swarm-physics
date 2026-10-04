# H12 × G12: Debate tournament, 10 debates (2025-09-01 → 2025-09-05)

**Verdict:** supported
**Role:** native (round 1b, non-holdout)
**Period:** regime I · mode C · 7 agents · one room (#general) · 5 days (debates on 09-01 → 09-04; 09-05 has none). Not scored in round 1 (N < 10).

## Why this period
DQ9 lists #12 as H12's cleanest test of "dimensional collapse under a strong uniform field": each of the 10 debates switches a motion on (the debate phase, `ground_truth_labels` phase `deb`, high confidence) and off at the verdict (an exact instant). H21 found the motion acts as a strong uniform field on content that switches off within 10 min of the verdict. HH58's mechanism (a shared field compresses what agents say onto few directions) predicts lower participation ratio while the motion is on than right after it is lifted. No other period has ten replicate field-on / field-off pairs at known instants.

## Prediction
*Written 2026-10-04 06:35 UTC, before computing any statistic on #12 statements. Seen before: H21's round-1 summary (motion = uniform field, switches off within 10 min of the verdict; family beats team) and the phase timestamps (design facts: debate phases last 3–22 min; post phases are labelled 10 min after each verdict).*

Design: chat statements of the 7 agents, whitened d = 32 (H12's regime-I ruler, bge), and the second model (gte, `statements_white32_gte_modernbert`) as a robustness check. For each debate k: the **on** set = statements inside its `deb` phase; the **off** set = statements from the verdict to 20 min after it (cut at the next debate's start). Statistic: bias-corrected PR of a rarefied pool (n = 12 statements, cap 4 per agent, 100 draws, ratio of means: `h12lib.pr_rarefied`), and the spread TV on the same draws. Debates with < 12 eligible statements on either side are dropped.
- **N12a (collapse under the motion).** PR(on) < PR(off) in ≥ 7 of the usable debates and a one-sided Wilcoxon signed-rank p < 0.05 (bge).
- **N12b (spread).** TV(on) < TV(off) in the majority of usable debates (descriptive direction).
- **N12c (model robustness).** The sign of the median paired difference is the same under gte.
- Credence: N12a 0.35 (round 1 found kickoffs *expand* PR; a debate makes the two teams argue opposite sides, which may add a direction).
- **Verdict rule:** supported if N12a and N12c hold; failed if the median paired difference is ≥ 0 under bge; mixed otherwise.

## Result
*Run 2026-10-04 06:45 UTC (`analysis/r1b_native.py`; per-debate values in `data/processed/H12-groupthink-dimensional-collapse/r1b/native/g12_debates.parquet`). 10 debates; 9 usable (one debate has < 12 eligible statements on a side).*

| Vectors | usable debates | PR(on) < PR(off) | median paired difference (relative) | one-sided Wilcoxon p | TV(on) < TV(off) |
| --- | --- | --- | --- | --- | --- |
| bge, H12's regime-I ruler (primary) | 9 | 7 | −3.1 (−25%) | 0.010 | 6/9 |
| bge, shared unit-normalized | 9 | 8 | −4.3 (−32%) | 0.006 | 8/9 |
| gte (second model) | 9 | 6 | −1.9 (−19%) | 0.064 | 9/9 |

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N12a PR lower under the motion in ≥ 7 debates, Wilcoxon p < 0.05 (bge) | 7/9, p = 0.010 | ✓ |
| N12b TV lower under the motion in the majority | 6/9 (bge), 9/9 (gte) | ✓ |
| N12c same sign under gte | −1.9, 6/9, p = 0.064 | ✓ |

**Verdict: supported.** While a motion is on, what the seven agents write spans fewer directions than in the 20 minutes after the verdict, by about a quarter, in both embedding models. This is the first H12 test where a strong, uniform, switch-off-able field shows HH58's compression; round 1's kickoffs (which open many proposals) and narrated "consensus weeks" did not. Caveats: debate turns are structured speeches (a format effect is possible), the off window is shorter and partly verdict discussion, and N = 7.

## Scorecard (period-specific axes)
- **E (interventional):** ten replicate field-on / field-off pairs at ground-truth instants; PR drops under the field (7/9, p = 0.01).
- **G (ground truth):** DQ6 phase labels (high confidence for `deb`).
- **F (robustness):** same sign under the second embedding model (p = 0.06).

## Notes
- 2026-10-04: folder created with the prediction before the run (round 1b; DQ9 native test for H12).
