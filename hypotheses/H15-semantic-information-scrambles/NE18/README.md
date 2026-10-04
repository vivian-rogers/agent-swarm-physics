# H15 × NE18: history search widened to verbatim segments and a 10-day window (2026-04-20)

**Verdict:** not supported (n.s., signs mixed)
**Role:** exploratory (round 1, non-holdout); inside goal #38 (`../G38/`).

## Why this NE
NE18 *adds* capacity to the channel from the village's stored past into the agent (an anti-scramble). If information retrieved by search is load-bearing, agents who use search more should gain viability after the widening.

## Design
Within #38: per agent, Δu = mean u(04-20 → 04-24) − mean u(04-02 → 04-17) (u = same-day-differenced, period-standardized V), regressed on the agent's SEARCH_HISTORY rate per window hour before 04-20 (dose). Permutation p (4,000 shuffles of the dose). NE17 (outreach approval, 04-14) falls in the pre window and hits outreach-heavy agents; it is not separated.

## Prediction
*Written 2026-10-03, before running.* Card P7: slope > 0 on V* (V_eng in regime III) and on V_out; expected not significant (one period, ~13 agents). A negative slope with p < 0.05 counts against P7.

## Result
*Run 2026-10-03.* 12 agents with ≥ 5 pre days; pre-period search rate 0 – 1.9 per window hour.

| V | slope of Δu on search rate | permutation p |
| --- | --- | --- |
| V_out | +0.21 | 0.40 |
| V_eng (V*) | −0.15 | 0.80 |
| V_rel | −0.10 | 0.67 |
| V_ord | −0.12 | 0.46 |
| V_coh | +0.12 | 0.62 |

P7 is not supported: the slope on V* has the wrong sign and nothing is significant. It is not falsified either (the falsifier was a negative slope with p < 0.05). With 12 agents and one period, an effect would have had to be very large to show. Source: `results.json` → `NE18`.
