# H127 × G51: maximize your private assigned role (step at 2026-07-06 16:00 UTC)

**Verdict:** failed
**Role:** exploratory (native (+ replication))
**Period:** regime III · mode I/K · 21 incumbents · 1 room(s). Day 1 after the step is the fit window; days 2–5 give the settled level. The step response is the object (exception (c)).

## Why this period
#51 kickoff 2026-07-06: ~21 agents receive private roles at once, with call rates spread about 7× (H40: 25–184 calls per hour). The own-role excess alignment gives the widest cadence lever in one period.

## Prediction
*Written 2026-10-04 22:18 UTC (card) and copied here 2026-10-04 before any run on this period.*
N1: own-role half-alignment time falls with call rate: Theil–Sen s < 0 with 90% CI below 0 in both models (credence 0.4). Counts against: s CI contains 0. The shared-kickoff replication (templated rule) is reported beside it.

## Result
**N1 (native, own roles; the verdict line).**

| Statistic | bge white32 | gte white32 |
| --- | --- | --- |
| rising / eligible agents | 18 / 21 | 19 / 21 |
| share of half times at the grid floor (immediate) from t₀ / from the read-out call | 1.00 / 0.83 | 1.00 / 0.84 |
| median T½^H | < 1 s (floor) | < 1 s (floor) |
| Theil–Sen slope s on log call rate (agents' rates 47–243 per hour) | 0 (all tied at the floor) | 0 (all tied at the floor) |

N1 fails: every agent's own-role alignment reaches its day-1 plateau at its first statement after t₀, so there is no half time to scale with the 5× spread in call rates. Data: `data/processed/H127-content-trails-goal-call-clock/natives/G51.json`.

**Shared-kickoff replication (templated rule).**

| Statistic | bge_white | gte_white | bge_style | gte_style |
| --- | --- | --- | --- | --- |
| rising / eligible agents | +0.38 | +0.38 | +0.38 | +0.38 |
| agents with fitted T½ | +8 | +8 | +8 | +8 |
| slope s (log T½^H on log r), 90% CI | +0.00 [+0.00, +20.98] | -0.00 [-46.90, +0.00] | -0.00 [-4.68, +20.98] | -0.00 [-20.70, +18.04] |
| collapse ratio CR (calls / hours) | – | – | – | – |
| within-agent clock gain ΔSSE | +0.00 | +0.00 | +0.00 | +0.00 |
| median T½^H (h) | +0.000 | +0.000 | +0.000 | +0.000 |
| median T½^C (calls) | +0.1 | +0.1 | +0.1 | +0.1 |
| share immediate from read-out | +0.75 | +0.75 | +0.75 | +0.50 |
| slope from read-out s^ro | +0.00 | +0.00 | -0.00 | +0.00 |

Verdict reason (bge, white32): s ≥ 0.
Data: `data/processed/H127-content-trails-goal-call-clock/G51/results.json`; all configurations in `NE34/kickoffs_all_configs.parquet`.

## Scorecard (period-specific axes)
- C: no slope beyond the agent bootstrap.
- D: CR (collapse) is an unfitted consequence of slope −1.
- H: read-out rival R_L read from the share of immediate fits from the read-out call.

## Notes
- Holdout masked (`holdout_mask`); #23 excluded throughout.
