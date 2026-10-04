# H94 × G30: Adopt a park and get it cleaned (2026-02-09 → 02-13)

**Verdict:** descriptive
**Role:** replication
**Period:** regime I · mode C · 11 agents · #general · 5 days. Units 30a, 30b (NE10).

## Why this period
Shared week with one park repo (2 work repos in all): the degenerate end of the allocation space.

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list; this period's structural counts (`counts.json`: quanta, commits, agents, repos per unit). No D_k, price, κ or signature on real data.

- Both units have < 3 repos: descriptive (D_1 and κ reported, no test).
- D_1 small (< 0.3 bit) because one repo takes almost everything.

## Result
*Run 2026-10-04 (non-holdout days only). Data: `data/processed/H94-maxent-work-allocation/G30/`; results `.../results/G30.json`.*

| Unit | quanta | D_1 | persistence floor_1 | D_final (M2/M3) | floor_final | ownership share | room share | residual / D_1 | λ_own (95% CI) | κ episodes [BE band] | κ w/o named | breadth vs null | singletons obs / M2 / M1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 30a | 30 | 0.27 | – | 0.27 | – | 0.00 | – | – | 0.51 | n/a | – | – | descriptive (< 100 quanta) |
| 30b | 144 | 0.19 | – | 0.19 | – | 0.00 | – | – | 0.83 | n/a | – | – | descriptive (< 100 quanta) |

Bits per work quantum. Floors: expected KL when the data are a draw from the fitted max-ent table with each agent-day's runs kept (A1). λ_own in nats (agent-block bootstrap; 20 = cap, quasi-separation). κ = (H_MB − H_obs)/(H_MB − H_BE) on work episodes per repo. Breadth: observed distinct repos per agent over the run-preserving null under M2.

Both units have 2 repos: descriptive. D_1 0.19–0.27 bit; one park repo carries the work.

## Scorecard (period-specific axes)
- —

## Notes
- 2026-10-04: folder created by the round-1 agent.
