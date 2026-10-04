# H65 × G44: #best fine-tunes a leader; #rest own goals (2026-05-26 → 2026-05-29)

**Verdict:** descriptive
**Role:** native
**Period:** regime III · mode C · 18 agents · 2 room(s) · 4 days. Units analysed: one unit.

## Why this period
Native test: an installed fine-tuned leader in #best with DQ6 checkpoints.

## Prediction
*Written 2026-10-04 20:15 UTC, before running on this period.*

**Replication layer (templated).** Per agent: content inflow χ̂ and outflow κ̂ (read-gated linear response, bge-small primary), reply-out share RO, breadth BO and reply-in rate RI. Predictions for this period: R1 ρ(RO, χ̂) > 0 (answering is absorbing) [0.6]; **R2 D_p = ρ(RI, χ̂ | n) − ρ(RI, κ̂ | n) > 0** (the agents others reply to are content sinks, not sources) [0.35]; R3 ρ(χ̂, κ̂) < 0.5 [0.7]. Counts against H65's generalization: D_p < 0 with a bootstrap CI below 0.

**Native (H65-N3, installed fine-tuned leader).** Agent 28 in #best from 2026-05-26 19:15:47 UTC (27 statements; thresholds 15 statements / 15 exposed targets for this native, fixed before the run): pct κ̂ ≤ 0.5 [0.8]; pct χ̂ ≥ 0.6 [0.5] (H23: its plans track the room); router call [0.4]. Expected low reliability.

## Result
| Unit | agents | ρ(RO, χ̂) | D_p [95% CI] | ρ(χ̂, κ̂) | median λ̂/χ̂ | ρ(κ̂, H32 Out) |
| --- | --- | --- | --- | --- | --- | --- |
| 44 | 14 | -0.03 | -0.03 [-0.69, +0.30] | +0.49 | +0.59 | +0.24 |

Replication verdict rule: supported if D_p > 0 with CI above 0; failed if D_p < 0 (attention goes to sources); descriptive (no decision) if the CI includes 0 (as pre-registered, a D_p < 0 counts against only with its CI below 0).

**Native layer** (bge-small primary; gte and style variants in `natives/<model>/`).

- leader percentiles among 6 agents: χ̂ 0.20 (CI [0.0, 0.8]), κ̂ 0.00 (CI [0.0, 0.8]), BO 0.20, RI 0.40, RO 0.00; router index +0.20; router call **False** (bootstrap share 0.11); leader statements 27.
- gte_modernbert: pct χ̂ 0.60, pct κ̂ 0.00, router call False.
- style: pct χ̂ 0.60, pct κ̂ 0.00, router call False.

## Scorecard (period-specific axes)
- **G (ground truth):** DQ6 leader or judge labels.
- **F:** synthetic recovery at this skeleton (card).
- **H:** R-source and R-agenda read off pct κ̂ / Δκ.

## Notes
- Data: `data/processed/H65-leaders-are-routers/G44/` (targets, reads), `replication/<model>/` (periods.json, agents.parquet), `natives/<model>/G44.json`. Holdout masked.
