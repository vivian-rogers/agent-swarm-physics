# H82 × NE15: Read vs posted-but-unread previous-period content at room boundaries (regime III)

**Verdict:** mixed
**Role:** native
**Period:** regime III goal boundaries whose previous period had ≥ 2 active rooms after the #best/#rest split (NE15, 2026-03-16): 37 → 38, 38 → 39, 39 → 40, 41 → 42 (40 is the NE42 merged week, so 40 → 41 has no unread set).

## Why this period
The in-flight placebo (STANDARDS §1) for the read-out channel. If remanence is carried by reading the old content, a veteran's day-1 content aligns with the previous-period statements it read more than with statements of the same hours that never entered its context (the other room).

## Prediction
*Written 2026-10-04 20:07 UTC (card), copied here 2026-10-04 20:19 UTC, before running on these boundaries.*
- For each veteran on day 1 of P: e_read = unit mean of P−1 statements (last two active days of P−1) that entered its context (context ledger items at its calls), e_unread = the same days' statements that never entered its context, restricted to posting hours where both sets exist. Statements are residualized on each sender's prior; the agent's own statements are excluded. One regression with both, plus the exogenous and prior regressors.
- **Prediction:** γ_read − γ_unread > 0, agent-cluster bootstrap CI excluding 0, in a fixed-effect meta-analysis over the four boundaries.
- **Against:** CI includes 0. Prior 0.4.

## Result
*Run 2026-10-04 20:35 UTC (`analysis/natives.py`).* Veterans on day 1 of P; previous-period statements of the last two active days, sender-prior residualized, matched posting hours.

| Boundary | N agents | γ_read − γ_unread bge [95%] | gte [95%] | median statements read / unread |
| --- | --- | --- | --- | --- |
| 37 → 38 | 12 | +0.384 [+0.139, +0.648] | +0.321 [+0.114, +0.557] | 200 / 147 |
| 38 → 39 | 13 | +0.026 [−0.074, +0.144] | +0.088 [−0.008, +0.188] | 173 / 61 |
| 39 → 40 | 15 | −0.039 [−0.235, +0.181] | −0.031 [−0.264, +0.219] | 348 / 19 |
| 41 → 42 | 15 | +0.101 [−0.044, +0.251] | +0.107 [−0.011, +0.210] | 587 / 127 |
| fixed effect | 4 | **+0.071 [−0.007, +0.148]** | **+0.106 [+0.039, +0.174]** | |

**Mixed:** read content predicts day-1 content more than posted-but-unread content at 3/4 boundaries; the pooled effect excludes 0 in gte and touches 0 in bge. The #37 → #38 boundary dominates. Part of the remanence goes through what agents read, as the in-flight placebo requires.

## Scorecard (period-specific axes)
- C, E: in-flight placebo passed in one model.
- The unread set at 39 → 40 is small (median 19 statements).

## Notes
- Room-mates' priors differ from other-room senders' priors; the sender-prior residualization removes that composition difference.
