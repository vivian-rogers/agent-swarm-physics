# H84 × G51: failed search answers as call-scale scrambles (#51 non-holdout head)

**Verdict:** descriptive
**Role:** native (exploratory)
**Period:** regime III · private-role era · #51 non-holdout head (07-06 → 09-04) · the period with 5.9 k of the 7.8 k non-holdout searches.

## Why this period
The only period with enough searches for a call-scale estimate of the search channel's value and its information I_Q. Single searches sometimes return near-empty answers (< 150 characters). These failures are not assigned at random (a query about nothing returns nothing), so this native is descriptive.

## Prediction
*Written 2026-10-04 ~20:07 UTC, before any outcome statistic.*
- Events: every search call; failed = answer < 150 characters. Outcomes over the next 20 calls (truncated at the next reset): V = work commits per 20 calls; return = 1[X⁺ = A⁻] among events with a commit.
- Poisson (V) and linear probability (return) with agent fixed effects and controls log query length and context position.
- **G1:** failed answers lower V by ≥ 10% (rate ratio ≤ 0.90, CI excluding 1).
- **G2:** failed answers lower return by ≥ 5 pp.
- **G3 (replication within the native):** I_Q > 0 (permutation p < 0.05).
- Verdict rule: *descriptive* in all cases (no exogenous assignment); the result says whether the pattern is "consistent" (G1 and G2) or "not consistent".

## Result
*Run 2026-10-04 20:20 UTC (`analysis/run.py`, G51 and replication blocks).*

- **Sample:** 3,954 search calls with ≥ 10 calls of window (32 agents, 427 agent-days); 83 failed answers (< 150 characters, 2.1%).
- **G1 output:** failed answers have rate ratio 1.25 [0.52, 2.42] on work commits per 20 calls (agent FE, log query length, log context position; agent-day bootstrap). Mean V 1.07 after failed vs 0.79 after normal answers. Not consistent with G1.
- **G2 return:** return to the own artifact +0.059 [−0.020, +0.134] after failed answers (n 1,394 search calls with a commit and an own artifact). Not consistent with G2.
- **G3 information:** I_Q = 0.028 bits [0.004, 0.057], permutation p 0.005. 26.8% of answers name a work repo; 13.1% name the agent's own artifact.
- **Return by pointer (H58 anchor):** P(X⁺ = A⁻) 0.99 when the answer names the own artifact (n 181) vs 0.92 otherwise (n 1,213).

**Reading (descriptive).** In the period where search is used most, a failed answer costs nothing measurable. A search that names the agent's own artifact precedes a return to it 99% of the time, but the agent chose the query, so this is selection, not value. The pattern is *not consistent* with a valuable search channel.

## Scorecard (period-specific axes)
- **C, D:** I_Q > 0 beats the within-agent permutation floor; the value contrast is observational (failures are not assigned).
