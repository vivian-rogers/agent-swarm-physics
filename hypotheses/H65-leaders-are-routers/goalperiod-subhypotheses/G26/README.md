# H65 × G26: elect a leader who sets the goal (2026-01-05 → 2026-01-09)

**Verdict:** failed
**Role:** native
**Period:** regime I · mode C · 10 agents · 1 room(s) · 5 days. Units analysed: one unit.

## Why this period
Native test: an elected leader with a DQ6 start instant (term 1 from 01-05 19:35 UTC).

## Prediction
*Written 2026-10-04 20:15 UTC, before running on this period.*

**Replication layer (templated).** Per agent: content inflow χ̂ and outflow κ̂ (read-gated linear response, bge-small primary), reply-out share RO, breadth BO and reply-in rate RI. Predictions for this period: R1 ρ(RO, χ̂) > 0 (answering is absorbing) [0.6]; **R2 D_p = ρ(RI, χ̂ | n) − ρ(RI, κ̂ | n) > 0** (the agents others reply to are content sinks, not sources) [0.35]; R3 ρ(χ̂, κ̂) < 0.5 [0.7]. Counts against H65's generalization: D_p < 0 with a bootstrap CI below 0.

**Native (H65-N1, elected leader).** Agent 17 (DeepSeek-V3.2) over term 1 (2026-01-05 19:35:22 → 01-09 19:00:43 UTC), ranked among the period's agents with ≥ 30 statements: pct χ̂ ≥ 0.6 [0.45]; pct κ̂ ≤ 0.5 [0.6]; pct BO ≥ 0.5 [0.55]; **router call** (pct χ̂ ≥ 0.6 and pct κ̂ ≤ 0.5) [0.3]. H29 saw this leader's broadcast pull rise most (R-agenda would put pct κ̂ high).

## Result
| Unit | agents | ρ(RO, χ̂) | D_p [95% CI] | ρ(χ̂, κ̂) | median λ̂/χ̂ | ρ(κ̂, H32 Out) |
| --- | --- | --- | --- | --- | --- | --- |
| 26 | 10 | +0.22 | -0.44 [-0.95, +0.13] | +0.01 | +1.14 | +0.08 |

Replication verdict rule: supported if D_p > 0 with CI above 0; failed if D_p < 0 (attention goes to sources); descriptive (no decision) if the CI includes 0 (as pre-registered, a D_p < 0 counts against only with its CI below 0).

**Native layer** (bge-small primary; gte and style variants in `natives/<model>/`).

- leader percentiles among 10 agents: χ̂ 0.22 (CI [0.0, 0.3333333333333333]), κ̂ 1.00 (CI [0.5555555555555556, 1.0]), BO 0.22, RI 0.89, RO 0.00; router index -0.78; router call **False** (bootstrap share 0.00); leader statements 123.
- gte_modernbert: pct χ̂ 0.11, pct κ̂ 0.89, router call False.
- style: pct χ̂ 0.22, pct κ̂ 0.89, router call False.

## Scorecard (period-specific axes)
- **G (ground truth):** DQ6 leader or judge labels.
- **F:** synthetic recovery at this skeleton (card).
- **H:** R-source and R-agenda read off pct κ̂ / Δκ.

## Notes
- Data: `data/processed/H65-leaders-are-routers/G26/` (targets, reads), `replication/<model>/` (periods.json, agents.parquet), `natives/<model>/G26.json`. Holdout masked.
