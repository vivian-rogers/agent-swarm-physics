# H65 × G51: maximize your private assigned role (2026-07-06 → 2026-09-04)

**Verdict:** descriptive
**Role:** replication
**Period:** regime III · mode I/K · 32 agents · 2 room(s) · 45 days. Units analysed: 51a, 51b, 51c, 51d, 51e, 51f, 51g, 51h, 51i, 51j, 51k, 51l.

## Why this period
A replication point: the router alignment D_p computed with the common estimator.

## Prediction
*Written 2026-10-04 20:15 UTC, before running on this period.*

**Replication layer (templated).** Per agent: content inflow χ̂ and outflow κ̂ (read-gated linear response, bge-small primary), reply-out share RO, breadth BO and reply-in rate RI. Predictions for this period: R1 ρ(RO, χ̂) > 0 (answering is absorbing) [0.6]; **R2 D_p = ρ(RI, χ̂ | n) − ρ(RI, κ̂ | n) > 0** (the agents others reply to are content sinks, not sources) [0.35]; R3 ρ(χ̂, κ̂) < 0.5 [0.7]. Counts against H65's generalization: D_p < 0 with a bootstrap CI below 0.


## Result
| Unit | agents | ρ(RO, χ̂) | D_p [95% CI] | ρ(χ̂, κ̂) | median λ̂/χ̂ | ρ(κ̂, H32 Out) |
| --- | --- | --- | --- | --- | --- | --- |
| 51a | 19 | +0.54 | +0.18 [-0.16, +0.65] | +0.45 | +0.15 | — |
| 51b | 12 | +0.73 | +0.20 [-0.55, +0.80] | +0.45 | +0.12 | — |
| 51c | 21 | +0.18 | -0.11 [-0.49, +0.55] | -0.26 | +0.22 | — |
| 51d | 22 | +0.34 | -0.18 [-0.48, +0.22] | +0.08 | +0.39 | — |
| 51e | 20 | +0.52 | -0.50 [-0.75, +0.08] | +0.36 | +0.29 | — |
| 51f | 21 | +0.43 | -0.09 [-0.47, +0.28] | +0.27 | +0.23 | — |
| 51g | 24 | +0.56 | -0.28 [-0.49, -0.01] | +0.14 | +0.32 | — |
| 51h | 16 | +0.27 | -0.21 [-0.74, +0.11] | +0.06 | +0.33 | — |
| 51i | 13 | -0.03 | -0.21 [-0.71, +0.22] | -0.12 | +0.18 | — |
| 51j | 17 | +0.16 | +0.03 [-0.58, +0.41] | +0.22 | +0.18 | — |
| 51k | 11 | +0.44 | +0.54 [-0.56, +1.12] | -0.15 | +0.17 | — |
| 51l | 14 | -0.28 | -0.33 [-1.17, +0.20] | -0.40 | +0.04 | — |

Replication verdict rule: supported if D_p > 0 with CI above 0; failed if D_p < 0 (attention goes to sources); descriptive (no decision) if the CI includes 0 (as pre-registered, a D_p < 0 counts against only with its CI below 0).

## Scorecard (period-specific axes)
- **C/D:** D_p with block-bootstrap CI; R1 mechanics.

## Notes
- Data: `data/processed/H65-leaders-are-routers/G51/` (targets, reads), `replication/<model>/` (periods.json, agents.parquet). Holdout masked.
