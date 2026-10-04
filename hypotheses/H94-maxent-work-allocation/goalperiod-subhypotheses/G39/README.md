# H94 × G39: Build your own interactive world (2026-04-27 → 05-01)

**Verdict:** supported
**Role:** replication
**Period:** regime III · mode I · 14 agents · #best / #rest · 5 days. One unit.

## Why this period
The cleanest own-artifact week: every agent builds its own world (H11 ownership 1.00).

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list; this period's structural counts (`counts.json`: quanta, commits, agents, repos per unit). No D_k, price, κ or signature on real data.

- P1: D_1 − floor_1 ≥ 0.5 bit per quantum in every testable unit (0.85).
- P2: ownership share ≥ 0.5 (own-artifact) (0.6); λ_own ≥ 2 nats with CI > 0 (0.7).
- P3: residual after M2 ≤ 0.2 · D_1 (equilibrium given ownership) (0.4).
- P5: κ < 1 (episodes spread more evenly than neutral copying) (0.5).
- P8: agent breadth under M2 < 0.8 (0.6).
- Expected the strongest ownership: share ≥ 0.8.

## Result
*Run 2026-10-04 (non-holdout days only). Data: `data/processed/H94-maxent-work-allocation/G39/`; results `.../results/G39.json`.*

| Unit | quanta | D_1 | persistence floor_1 | D_final (M2/M3) | floor_final | ownership share | room share | residual / D_1 | λ_own (95% CI) | κ episodes [BE band] | κ w/o named | breadth vs null | singletons obs / M2 / M1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 39 | 380 | 3.68 | 1.55 | 0.03 | 0.00 | 0.99 | 0.00 | +0.01 | 20.00 [16.03, 20.00] | 0.15 [0.27, 2.02] | 0.32 | 1.07 | 18 / 14.6 / 2.0 |

Bits per work quantum. Floors: expected KL when the data are a draw from the fitted max-ent table with each agent-day's runs kept (A1). λ_own in nats (agent-block bootstrap; 20 = cap, quasi-separation). κ = (H_MB − H_obs)/(H_MB − H_BE) on work episodes per repo. Breadth: observed distinct repos per agent over the run-preserving null under M2.

Ownership is almost deterministic: λ_own at the cap (16–20 nats), ownership share 0.99, residual 0.01·D_1, D_final 0.03 bit. κ 0.15 *below* the BE band (episodes spread evenly over own worlds, P5 ✓). M2 predicts 14.6 of 18 singleton repos (M1: 2.0).

## Scorecard (period-specific axes)
- C: 2. G: 2 (every agent its own world).

## Notes
- 2026-10-04: folder created by the round-1 agent.
- 2026-10-04 (after the prediction above, before the real run): the synthetic summary showed the S0-world κ on episodes for this period's synthetic unit, which tracks the real repo-size margin (card amendment A1: 31a 1.64, 39 0.49, 41 1.99, 51d 0.84). The prediction was not changed.
