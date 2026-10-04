# H65 × G38: charity fundraiser (year 2) (2026-04-02 → 2026-04-24)

**Verdict:** failed
**Role:** replication
**Period:** regime III · mode C · 14 agents · 2 room(s) · 17 days. Units analysed: one unit.

## Why this period
A replication point: the router alignment D_p computed with the common estimator.

## Prediction
*Written 2026-10-04 20:15 UTC, before running on this period.*

**Replication layer (templated).** Per agent: content inflow χ̂ and outflow κ̂ (read-gated linear response, bge-small primary), reply-out share RO, breadth BO and reply-in rate RI. Predictions for this period: R1 ρ(RO, χ̂) > 0 (answering is absorbing) [0.6]; **R2 D_p = ρ(RI, χ̂ | n) − ρ(RI, κ̂ | n) > 0** (the agents others reply to are content sinks, not sources) [0.35]; R3 ρ(χ̂, κ̂) < 0.5 [0.7]. Counts against H65's generalization: D_p < 0 with a bootstrap CI below 0.


## Result
| Unit | agents | ρ(RO, χ̂) | D_p [95% CI] | ρ(χ̂, κ̂) | median λ̂/χ̂ | ρ(κ̂, H32 Out) |
| --- | --- | --- | --- | --- | --- | --- |
| 38 | 12 | +0.36 | -0.94 [-1.34, -0.17] | +0.40 | +0.93 | +0.63 |

Replication verdict rule: supported if D_p > 0 with CI above 0; failed if D_p < 0 (attention goes to sources); descriptive (no decision) if the CI includes 0 (as pre-registered, a D_p < 0 counts against only with its CI below 0).

## Scorecard (period-specific axes)
- **C/D:** D_p with block-bootstrap CI; R1 mechanics.

## Notes
- Data: `data/processed/H65-leaders-are-routers/G38/` (targets, reads), `replication/<model>/` (periods.json, agents.parquet). Holdout masked.
