# H138 × G38: the long shared week with births all through (#38, 2026-04-02 → 2026-04-27)

**Verdict:** descriptive
**Role:** exploratory (replication + native N1)
**Period:** regime III · mode C · 12 agents · two rooms (#best / #rest, room-specific kickoffs) · 17 days. Units from `period_units`.

## Why this period
New projects appear all through the 17 days (H129's native N2: net flow to newer projects m_2 0.17, p 0.027). So the open-option count q_live swings inside one goal, at a fixed goal field. That is the cleanest within-period test of Glauber escape. Work switches: 87 (H11 round 2).

## Prediction
*Written 2026-10-07 ~09:10 UTC, before running on this period. Seen: the switch total and H129's flow statistics; no q count and no hazard statistic.*
- **P1 (replication):** ε̂_q > 0 with CI above 0 (work channel). Credence 0.3.
- **N1 (native):** the leave hazard per own call in the top q_live tercile over the bottom tercile equals (mean q_live ratio)^ε̂_q within ×1.5, and ε̂_q CI above 0. Credence 0.3.
- **P3 (lead placebo):** ε̂_q − ε̂_lead > 0 with CI above 0. Credence 0.3.
- Counts against: ε̂_q CI includes 0 with synthetic power ≥ 0.8; or ε̂_lead ≥ ε̂_q (co-arrival).
- Room variant (q_room) is reported; rooms are fixed for the week (H102), so it measures the menu in the agent's own room, not room hopping.

## Result
*Round 1, 2026-10-07 (exploration). Estimator: cloglog hazard per own call, agent effects, active-time spline, agent-cluster sandwich (card Amendment A1). Power from the real-skeleton synthetic (W1 worlds, 200 replicates). The work power at ε_q = 0.5 is below 0.8 in every unit (card A2), so a work null is unpowered.*

| Channel · unit | Leaves | ε̂_q [95% CI] | permutation p | ε̂_q − ε̂_lead [boot CI] | ε̂_Z [CI] | β̂_own [CI] | power at ε 0.5 / 1 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| work · 38 | 44 | −0.73 [−1.76, 0.30] | 0.181 | −1.30 [−4.15, −0.58] | −0.58 [−1.12, −0.03] | 0.69 [−0.57, 1.95] | 0.29 / 0.63 |
| attention · 38 | 242 | −0.14 [−0.63, 0.34] | 0.580 | −0.74 [−1.50, 0.01] | 0.13 [−0.29, 0.54] | −0.37 [−0.77, 0.02] | 0.41 / 0.96 |

| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 (work): ε̂_q CI above 0 | −0.73 [−1.76, 0.30]; permutation p 0.18 | fails; unpowered (0.29) |
| N1: tercile hazard ratio = (q ratio)^ε̂ within ×1.5, and ε̂_q CI above 0 | top/bottom q_live tercile (q̄ 5.2 vs 1.6; 15 vs 17 leaves): hazard 0.184 vs 0.153 per 100 own calls, ratio 1.20; predicted (5.2/1.6)^−0.73 = 0.41; observed/predicted 2.89 | fails (outside ×1.5; ε̂ CI includes 0); unpowered |
| P3 (work): ε̂_q − ε̂_lead CI above 0 | −1.30 [−4.15, −0.58] | fails (lead > lag) |
| Attention (secondary) | −0.14 [−0.63, 0.34] | fails; unpowered (0.41) |

- Period verdict: **descriptive** (unpowered negative). Inside the 17-day goal the raw leave rate is about the same at low and high q_live (ratio 1.20). After agent effects, the time spline and the stay terms, the elasticity is negative. Neither form follows the Glauber prediction.
- The work lead placebo is negative: leaves line up more with projects that appear in the next 2 active hours than with those open before (R-coarrival).
- Descriptive: 0.12 leaves per 100 own calls; q̄ = 3.0; 52% of work leaves go to a project born in the 2 h before. Kickoff-named options are counted apart in the card's pooled q_named/q_free variant.
- Figure: `figures/n1_terciles.png`.

## Scorecard (period-specific axes)
C 0 (ε̂_q does not beat 0); D 1 (the unfitted tercile check was run and fails: 2.89 vs ×1.5); E 0 (no NE); H 0 (lead > lag: R-coarrival fits better).

## Notes
- Kickoff-named projects are counted apart (q_named, q_free): #38 has room-specific kickoffs.
