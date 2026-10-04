# H127 × G16: free week with operator rules (step at 2025-10-06 17:00 UTC)

**Verdict:** descriptive
**Role:** exploratory (replication)
**Period:** regime I · mode F · 7 incumbents · 1 room(s). Day 1 after the step is the fit window; days 2–5 give the settled level. The step response is the object (exception (c)).

## Why this period
One eligible kickoff (H125's set: shared kickoff, ≥ 5 non-holdout days in one regime). Common estimator, templated rule.

## Prediction
*Written 2026-10-04 22:18 UTC (card) and copied here 2026-10-04 before any run on this period.*
Templated from the card (written 2026-10-04 22:18 UTC, before any real-data statistic), labelled as such. Each rising agent's half-alignment time in hours after t₀ falls with its day-1 call rate (Theil–Sen slope s of log T½^H on log r, near −1), and the spread of log T½ shrinks in calls (CR < 1). Rule: supported if s < 0 with agent-bootstrap 90% CI below 0 and CR < 1; failed if s ≥ 0; mixed otherwise; descriptive if fewer than 5 rising agents have a fitted T½. Regime I: H40 found neither clock for replies here, so the card expects a weaker slope (S1).

## Result
| Statistic | bge_white | gte_white | bge_style | gte_style |
| --- | --- | --- | --- | --- |
| rising / eligible agents | +0.57 | +0.86 | +0.57 | +0.86 |
| agents with fitted T½ | +4 | +6 | +4 | +6 |
| slope s (log T½^H on log r), 90% CI | +0.00 [+0.00, +0.00] | +0.00 [-7.57, +20.76] | +3.79 [+0.00, +14.45] | +0.00 [-46.39, +9.88] |
| collapse ratio CR (calls / hours) | – | +0.31 | – | +1.18 |
| within-agent clock gain ΔSSE | +0.13 | -0.00 | +0.11 | +0.00 |
| median T½^H (h) | +0.000 | +0.023 | +0.000 | +17.355 |
| median T½^C (calls) | +0.1 | +1.3 | +0.1 | +1734.4 |
| share immediate from read-out | +1.00 | +0.50 | +1.00 | +0.33 |
| slope from read-out s^ro | +0.00 | +0.00 | +0.00 | +0.00 |

Verdict reason (bge, white32): fewer than 5 rising agents with a fitted T½.
Data: `data/processed/H127-content-trails-goal-call-clock/G16/results.json`; all configurations in `NE34/kickoffs_all_configs.parquet`.

## Scorecard (period-specific axes)
- C: not tested.
- D: CR (collapse) is an unfitted consequence of slope −1.
- H: read-out rival R_L read from the share of immediate fits from the read-out call.

## Notes
- Holdout masked (`holdout_mask`); #23 excluded throughout.
