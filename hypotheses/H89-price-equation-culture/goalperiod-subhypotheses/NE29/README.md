# H89 × NE29: Retirement of the longest-serving agent (#31, 2026-02-18 / 02-19)

**Verdict:** supported
**Role:** native
**Period:** inside G31 · regime I · non-holdout days only.

## Why this test
NE29: Claude Sonnet 4.6 joins on 02-18 and Claude 3.7 Sonnet, the agent present since 2025-04-02, leaves on 02-19, inside goal period #31 with no other roster change. It is the cleanest single-carrier loss in the non-holdout record. Exception (c): the transitions across the two roster events are the object; #30 and #31's other transitions are the placebos.

## Prediction
*Written 2026-10-04 20:35 UTC, before any native statistic.*
- **N1-a:** at each roster-flow transition (into 02-18: one entrant; into 02-19: one leaver), the roster-migration share of style exceeds that of content (cross-fitted, that transition alone).
- **N1-b:** the stayers' content change (Sel + Trans) at the retirement transition is not larger than at the placebo transitions of #30 and #31: cross-fitted |Sel + Trans|² percentile < 0.9.
- Prior 0.5. **Verdict:** supported = N1-a at both transitions and N1-b; failed = neither; mixed otherwise.
- *Counts against:* content migration share ≥ style's at a roster transition; the retirement transition is the largest stayer change in #30–#31.

## Result
**supported.** Single-transition energy shares (cross-fitted between message halves).

| Prediction | Observed | Reference | Verdict |
| --- | --- | --- | --- |
| N1-a entry (02-17 → 02-18, Sonnet 4.6 joins): style roster share > content | style +0.164, content bge +0.051, gte +0.038, conventions +0.009 (ρ_Δ style 0.77, content 0.91) | 0 | pass |
| N1-a retirement (02-18 → 02-19, Claude 3.7 Sonnet leaves): style roster share > content | style +0.033, content bge -0.002, gte -0.021, conventions +0.003 (ρ_Δ style 0.95, content 0.84) | 0 | pass |
| N1-b stayers' content change at the retirement not above placebo | percentile 0.00 among 7 placebo transitions of #30–#31 | < 0.9 | pass |

## Scorecard (period-specific axes)
E (interventional): a single-carrier loss and a single join, each one transition; style vs content migration shares at the event. G: roster dates from `roster`.

## Notes
