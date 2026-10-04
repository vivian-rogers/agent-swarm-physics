# H94 × G37: Pick your own goal (free week, two rooms) (2026-03-30 → 04-01)

**Verdict:** descriptive
**Role:** replication
**Period:** regime III · mode F · 12 agents · #best / #rest · 3 days. One unit (94 quanta).

## Why this period
Free week in two rooms with identical kickoff text; below the 100-quantum testability rule.

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list; this period's structural counts (`counts.json`: quanta, commits, agents, repos per unit). No D_k, price, κ or signature on real data.

- Descriptive (94 quanta < 100): D_1, ownership share and κ reported without floors.
- Expect κ ≥ 1 and ownership share < 0.5 as in other free weeks.

## Result
*Run 2026-10-04 (non-holdout days only). Data: `data/processed/H94-maxent-work-allocation/G37/`; results `.../results/G37.json`.*

| Unit | quanta | D_1 | persistence floor_1 | D_final (M2/M3) | floor_final | ownership share | room share | residual / D_1 | λ_own (95% CI) | κ episodes [BE band] | κ w/o named | breadth vs null | singletons obs / M2 / M1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 37 | 94 | 1.88 | – | 1.32 | – | 0.22 | – | – | 2.55 | 1.98 | – | – | descriptive (< 100 quanta) |

Bits per work quantum. Floors: expected KL when the data are a draw from the fitted max-ent table with each agent-day's runs kept (A1). λ_own in nats (agent-block bootstrap; 20 = cap, quasi-separation). κ = (H_MB − H_obs)/(H_MB − H_BE) on work episodes per repo. Breadth: observed distinct repos per agent over the run-preserving null under M2.

94 quanta (< 100): descriptive. D_1 1.88, ownership share 0.22, κ 1.98.

## Scorecard (period-specific axes)
- —

## Notes
- 2026-10-04: folder created by the round-1 agent.
