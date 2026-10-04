# H127 × NE38: maximize your private assigned role (step at 2026-07-29 16:51 UTC)

**Verdict:** descriptive
**Role:** exploratory (native)
**Period:** regime III · mode I/K · 27 incumbents · 1 room(s). Day 1 after the step is the fit window; days 2–5 give the settled level. The step response is the object (exception (c)).

## Why this period
One agent (Claude Opus 5) is reassigned at 2026-07-29 16:51 UTC while the others keep their roles: an out-of-sample test of the call-clock constant on an agent whose step was not used to fit it.

## Prediction
*Written 2026-10-04 22:18 UTC (card) and copied here 2026-10-04 before any run on this period.*
N2: Opus 5's measured T½^H (own new role) is closer in |log ratio| to the call-clock prediction (regime-III replication median T½^C divided by Opus 5's call rate) than to the hour-clock prediction (regime-III median T½^H), in both models (credence 0.5). Counts against: the hour-clock prediction is closer.

## Result
| Statistic | bge white32 | gte white32 |
| --- | --- | --- |
| Opus 5 day-1 call rate after 16:51 UTC | 79.7 per hour | 79.7 per hour |
| Opus 5 rising (Δ/SE > 2) | yes | yes |
| Opus 5 measured T½^H (own new role) | 0.20 h (≈ 16 calls) | 0.24 h (≈ 19 calls) |
| call-clock prediction (regime-III median T½^C / r) | 0.001 h | 0.001 h |
| hour-clock prediction (regime-III median T½^H) | < 0.001 h | < 0.001 h |
| \|log ratio\| call / hour | 5.4 / 8.0 | 5.6 / 8.1 |

N2 passes by its letter (the call-clock prediction is closer) but is uninformative: both predictions sit at the grid floor because kickoff rises are immediate (card, Results). Opus 5's own rise is resolved: half of its day-1 plateau after 12–14 min (16–19 of its calls). A mid-day, one-agent reassignment therefore moves content gradually, unlike a village kickoff. Data: `data/processed/H127-content-trails-goal-call-clock/natives/NE38.json`.

## Scorecard (period-specific axes)
- D: the out-of-sample prediction cannot be tested (both rival predictions at the floor).
- E: the single-agent step shows a resolved rise (T½ ≈ 0.2 h); kickoffs do not.

## Notes
- Holdout masked (`holdout_mask`); #23 excluded throughout.
