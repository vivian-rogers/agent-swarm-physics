# H85 × NE42: #best and #rest merged for one week (2026-05-04 → 05-11), G39 → G40 → G41

**Verdict:** failed
**Role:** native (exploratory)
**Period:** regime III · 15 agents present in all three units (39, 40, 41) · room population ≈ 7.5 in the split weeks vs ≈ 15 merged · goal #40 (connect worlds, shared objective) sits inside the merged week.

## Why this period
The same agents meet a doubled room population for one week: an N step without roster change (exception (c): the transition is the object).

## Prediction
*Written 2026-10-04 20:04 UTC in the card.* Per-agent message rate ratio (merged / mean of split weeks) ∈ [0.8, 1.25]; k_talk ratio ≥ 1.5; per-agent addressed-pair ratio = (k ratio)^0.34 ± 0.15 and > 1. Placebo #39 → #41 (no room change): ratios within [0.8, 1.25]. *Against:* k ratio < 1.3, or addressed-pair ratio ≤ 1 with k ratio ≥ 1.5.

## Result
*Run 2026-10-04 20:15 UTC (`analysis/natives.py`). Per-agent rates per present hour; agent bootstrap (2,000).*

| Output | merged / split [95% CI] | placebo #41 / #39 [95% CI] |
| --- | --- | --- |
| msg | 1.14 [0.90, 1.41] | 2.48 [1.80, 3.68] |
| ment | 0.90 [0.42, 1.59] | 6.02 [3.71, 10.38] |
| reply | 0.89 [0.61, 1.15] | 7.46 [4.90, 12.46] |
| commit | 1.45 [1.01, 1.70] | 0.81 [0.49, 1.26] |
| talk_calls | 1.11 [0.88, 1.36] | 2.53 [1.85, 3.67] |
| k_talk | 1.34 [0.89, 2.01] | 0.74 [0.41, 1.22] |

- Predicted addressed-pair ratio from k: 1.10 [0.96, 1.27]; observed 0.90.
- **The placebo fails badly:** #41 differs from #39 by ×2.5 (messages) to ×7.5 (reply parents) with no room change, so goal effects swamp any N step. The k ratio (1.34, CI includes 1) is below the predicted ≥ 1.5, and addressed pairs do not rise (0.90).
- **Verdict: failed** (design invalid at this resolution; the merge did not visibly enlarge the pending set). Commits per agent-hour rose ×1.45 [1.01, 1.70] in the merged week (placebo 0.81): descriptive, confounded with goal #40.

## Scorecard (period-specific axes)
- E (interventional): not informative (placebo violated).
