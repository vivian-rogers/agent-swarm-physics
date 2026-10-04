# H65 × G35: test your game (forked per room) (2026-03-16 → 2026-03-20)

**Verdict:** mixed
**Role:** native
**Period:** regime II · mode C · 12 agents · 2 room(s) · 5 days. Units analysed: one unit.

## Why this period
Native test: daily-rotating designated lead designers per room (DQ6), so the same agent is observed with and without the role.

## Prediction
*Written 2026-10-04 20:15 UTC, before running on this period.*

**Replication layer (templated).** Per agent: content inflow χ̂ and outflow κ̂ (read-gated linear response, bge-small primary), reply-out share RO, breadth BO and reply-in rate RI. Predictions for this period: R1 ρ(RO, χ̂) > 0 (answering is absorbing) [0.6]; **R2 D_p = ρ(RI, χ̂ | n) − ρ(RI, κ̂ | n) > 0** (the agents others reply to are content sinks, not sources) [0.35]; R3 ρ(χ̂, κ̂) < 0.5 [0.7]. Counts against H65's generalization: D_p < 0 with a bootstrap CI below 0.

**Native (H65-N2, daily lead designers, within agent).** Six DQ6 leader room-days. Agent × room-day estimates (≥ 10 statements); leader-day minus the same agent's other room-days, net of room-day effects; null = leader label permuted among each room-day's agents (5,000): Δχ > 0 [0.5]; Δκ ≤ 0 [0.6]; ΔBO > 0 [0.5]; ΔRI > 0 [0.7, H29]. **Router call** = Δχ > 0 with permutation p < 0.10 and Δκ ≤ 0 [0.25].

## Result
| Unit | agents | ρ(RO, χ̂) | D_p [95% CI] | ρ(χ̂, κ̂) | median λ̂/χ̂ | ρ(κ̂, H32 Out) |
| --- | --- | --- | --- | --- | --- | --- |
| 35 | 11 | +0.32 | +0.19 [-0.93, +0.81] | -0.38 | +0.82 | +0.82 |

Replication verdict rule: supported if D_p > 0 with CI above 0; failed if D_p < 0 (attention goes to sources); descriptive (no decision) if the CI includes 0 (as pre-registered, a D_p < 0 counts against only with its CI below 0).

**Native layer** (bge-small primary; gte and style variants in `natives/<model>/`).

| Metric | β (role) | p (greater) | p (less) | rows |
| --- | --- | --- | --- | --- |
| chi | +0.091 | 0.183 | 0.817 | 52 |
| kappa | +0.003 | 0.458 | 0.542 | 52 |
| RO | +0.003 | 0.494 | 0.506 | 52 |
| BO | +0.064 | 0.104 | 0.896 | 52 |
| RI | +0.388 | 0.005 | 0.995 | 52 |

Router call **False**.
- gte_modernbert: Δχ +0.177 (p 0.009), Δκ -0.003 (p> 0.492), router call True.
- style: Δχ +0.065 (p 0.241), Δκ +0.019 (p> 0.358), router call False.

## Scorecard (period-specific axes)
- **G (ground truth):** DQ6 leader or judge labels.
- **F:** synthetic recovery at this skeleton (card).
- **H:** R-source and R-agenda read off pct κ̂ / Δκ.

## Notes
- Data: `data/processed/H65-leaders-are-routers/G35/` (targets, reads), `replication/<model>/` (periods.json, agents.parquet), `natives/<model>/G35.json`. Holdout masked.
