# H14 × NE43: Drive withdrawal inside #51 (bookends end 08-05, nudges end 08-21)

**Verdict:** failed
**Role:** native
**Period:** regime III · #51 non-holdout days. Two steps at fixed goal, room and hours: the daily pause/resume bookends stop after 08-04 PT, the nudger after 08-20. Windows: 7 calendar days (5 PT weekdays) before and after each step; placebo boundaries 07-13, 07-20, 07-27, 08-12.

## Why this period
The DQ9 cross-index lists NE43 for H14 as an expected null: EP should change at scaffold changes or task changes, not when an outside driver goes quiet. H56 found no EP jump at NE43 on action classes; round 1b repeats it on the scaffold-free fine chain and on semantic states.

## Prediction
*Written 2026-10-04, before running (card, "Round 1b", N1).* Pooled v3 soft EP and pooled act_sh_b3 EP per transition change at each real step by no more than the range of the four placebo boundaries (min–max). Credence 0.7.

## Result
*Run 2026-10-04 (`analysis/native_r1b.py`; `data/processed/H14-behavior-entropy-production/r1b/native_r1b.json`).*

| Boundary | kind | v3 pooled EP before → after (relative change) | act_sh_b3 pooled before → after (relative) | act_sh_b3 per-agent median change (n) |
| --- | --- | --- | --- | --- |
| 08-05 | bookends end | 0.0166 → 0.0084 (−50%) | 0.068 → 0.067 (−1%) | −0.005 (24) |
| 08-21 | nudger off | 0.0113 → 0.0075 (−34%) | 0.094 → 0.106 (+12%) | +0.016 (25) |
| 07-13 | placebo | −45% | −10% | |
| 07-20 | placebo | −17% | −24% | |
| 07-27 | placebo | +183% | −12% | |
| 08-12 | placebo | +6% | +43% | |

Placebo ranges: v3 −45%…+183%, act_sh_b3 −24%…+43%. Three of the four real changes are inside; the bookend change on v3 (−50%) is 5 points outside. **Failed as pre-registered** (one marginal miss); read with the placebo spread, there is no evidence of a step at either NE43 date, and pooled v3 EP over 5 days is very noisy.

## Scorecard (period-specific axes)
E 0 (no predicted change; the null mostly holds). F: the 5-day pooled v3 estimate varies by a factor of ~3 between ordinary weeks.

## Notes
- #51 runs on weekdays, so 7 calendar days give 5 days of data per side.
