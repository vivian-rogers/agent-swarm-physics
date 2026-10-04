# H65 × G30: adopt a park (2026-02-09 → 2026-02-13)

**Verdict:** descriptive
**Role:** replication
**Period:** regime I · mode C · 11 agents · 1 room(s) · 5 days. Units analysed: one unit.

## Why this period
A replication point: the router alignment D_p computed with the common estimator.

## Prediction
*Written 2026-10-04 20:15 UTC, before running on this period.*

**Replication layer (templated).** Per agent: content inflow χ̂ and outflow κ̂ (read-gated linear response, bge-small primary), reply-out share RO, breadth BO and reply-in rate RI. Predictions for this period: R1 ρ(RO, χ̂) > 0 (answering is absorbing) [0.6]; **R2 D_p = ρ(RI, χ̂ | n) − ρ(RI, κ̂ | n) > 0** (the agents others reply to are content sinks, not sources) [0.35]; R3 ρ(χ̂, κ̂) < 0.5 [0.7]. Counts against H65's generalization: D_p < 0 with a bootstrap CI below 0.


## Result
| Unit | agents | ρ(RO, χ̂) | D_p [95% CI] | ρ(χ̂, κ̂) | median λ̂/χ̂ | ρ(κ̂, H32 Out) |
| --- | --- | --- | --- | --- | --- | --- |
| 30 | 11 | -0.15 | -0.35 [-0.82, +0.28] | -0.10 | +0.64 | +0.65 |

Replication verdict rule: supported if D_p > 0 with CI above 0; failed if D_p < 0 (attention goes to sources); descriptive (no decision) if the CI includes 0 (as pre-registered, a D_p < 0 counts against only with its CI below 0).

## Scorecard (period-specific axes)
- **C/D:** D_p with block-bootstrap CI; R1 mechanics.

## Notes
- Data: `data/processed/H65-leaders-are-routers/G30/` (targets, reads), `replication/<model>/` (periods.json, agents.parquet). Holdout masked.
