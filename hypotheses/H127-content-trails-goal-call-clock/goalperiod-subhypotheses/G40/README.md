# H127 × G40: connect worlds into a 3D universe (step at 2026-05-04 17:00 UTC)

**Verdict:** failed
**Role:** exploratory (replication)
**Period:** regime III · mode C · 15 incumbents · 1 room(s). Day 1 after the step is the fit window; days 2–5 give the settled level. The step response is the object (exception (c)).

## Why this period
One eligible kickoff (H125's set: shared kickoff, ≥ 5 non-holdout days in one regime). Common estimator, templated rule.

## Prediction
*Written 2026-10-04 22:18 UTC (card) and copied here 2026-10-04 before any run on this period.*
Templated from the card (written 2026-10-04 22:18 UTC, before any real-data statistic), labelled as such. Each rising agent's half-alignment time in hours after t₀ falls with its day-1 call rate (Theil–Sen slope s of log T½^H on log r, near −1), and the spread of log T½ shrinks in calls (CR < 1). Rule: supported if s < 0 with agent-bootstrap 90% CI below 0 and CR < 1; failed if s ≥ 0; mixed otherwise; descriptive if fewer than 5 rising agents have a fitted T½. Regimes II–III: H40's call clock holds for replies here.

## Result
| Statistic | bge_white | gte_white | bge_style | gte_style |
| --- | --- | --- | --- | --- |
| rising / eligible agents | +0.73 | +0.60 | +0.80 | +0.60 |
| agents with fitted T½ | +11 | +9 | +12 | +9 |
| slope s (log T½^H on log r), 90% CI | +0.00 [-18.66, +0.00] | -10.50 [-27.46, +0.00] | +0.00 [-17.10, +0.00] | -8.91 [-19.04, +0.00] |
| collapse ratio CR (calls / hours) | – | – | – | +0.00 |
| within-agent clock gain ΔSSE | -0.00 | -0.00 | -0.00 | -0.00 |
| median T½^H (h) | +0.000 | +0.000 | +0.000 | +0.000 |
| median T½^C (calls) | +0.1 | +0.1 | +0.1 | +0.1 |
| share immediate from read-out | +0.55 | +0.56 | +0.58 | +0.44 |
| slope from read-out s^ro | +0.00 | -10.50 | +0.00 | -8.87 |

Verdict reason (bge, white32): s ≥ 0.
Data: `data/processed/H127-content-trails-goal-call-clock/G40/results.json`; all configurations in `NE34/kickoffs_all_configs.parquet`.

## Scorecard (period-specific axes)
- C: no slope beyond the agent bootstrap.
- D: CR (collapse) is an unfitted consequence of slope −1.
- H: read-out rival R_L read from the share of immediate fits from the read-out call.

## Notes
- Holdout masked (`holdout_mask`); #23 excluded throughout.
