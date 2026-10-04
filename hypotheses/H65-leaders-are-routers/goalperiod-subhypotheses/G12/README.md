# H65 × G12: debate tournament (10 debates) (2025-09-01 → 2025-09-05)

**Verdict:** mixed
**Role:** native
**Period:** regime I · mode M · 7 agents · 1 room(s) · 5 days. Units analysed: one unit.

## Why this period
Native test: rotating debate judges (DQ6), so the same agent is observed as judge and as debater.

## Prediction
*Written 2026-10-04 20:15 UTC, before running on this period.*

**Replication layer (templated).** Per agent: content inflow χ̂ and outflow κ̂ (read-gated linear response, bge-small primary), reply-out share RO, breadth BO and reply-in rate RI. Predictions for this period: R1 ρ(RO, χ̂) > 0 (answering is absorbing) [0.6]; **R2 D_p = ρ(RI, χ̂ | n) − ρ(RI, κ̂ | n) > 0** (the agents others reply to are content sinks, not sources) [0.35]; R3 ρ(χ̂, κ̂) < 0.5 [0.7]. Counts against H65's generalization: D_p < 0 with a bootstrap CI below 0.

**Native (H65-N4, rotating judges, within agent).** Each agent's statements as the judge of a debate vs as a debater in other debates (debate windows from DQ6; ≥ 5 statements per agent-debate); net of debate effects; null = judge label permuted among each debate's participants (5,000): Δκ > 0 (judges set the motion: R-agenda) [0.45]; Δχ > 0 [0.5]; router call [0.3].

## Result
| Unit | agents | ρ(RO, χ̂) | D_p [95% CI] | ρ(χ̂, κ̂) | median λ̂/χ̂ | ρ(κ̂, H32 Out) |
| --- | --- | --- | --- | --- | --- | --- |
| 12 | 7 | +0.50 | -0.37 [-1.09, +0.19] | +0.54 | +1.73 | +0.93 |

Replication verdict rule: supported if D_p > 0 with CI above 0; failed if D_p < 0 (attention goes to sources); descriptive (no decision) if the CI includes 0 (as pre-registered, a D_p < 0 counts against only with its CI below 0).

**Native layer** (bge-small primary; gte and style variants in `natives/<model>/`).

| Metric | β (role) | p (greater) | p (less) | rows |
| --- | --- | --- | --- | --- |
| chi | -0.028 | 0.589 | 0.411 | 65 |
| kappa | -0.059 | 0.938 | 0.062 | 65 |
| RO | +0.050 | 0.167 | 0.833 | 65 |
| BO | +0.157 | 0.003 | 0.997 | 65 |
| RI | +0.453 | 0.007 | 0.993 | 65 |

Router call **False**.
- gte_modernbert: Δχ +0.084 (p 0.191), Δκ -0.034 (p> 0.851), router call False.
- style: Δχ -0.132 (p 0.853), Δκ -0.055 (p> 0.908), router call False.

## Scorecard (period-specific axes)
- **G (ground truth):** DQ6 leader or judge labels.
- **F:** synthetic recovery at this skeleton (card).
- **H:** R-source and R-agenda read off pct κ̂ / Δκ.

## Notes
- Data: `data/processed/H65-leaders-are-routers/G12/` (targets, reads), `replication/<model>/` (periods.json, agents.parquet), `natives/<model>/G12.json`. Holdout masked.
