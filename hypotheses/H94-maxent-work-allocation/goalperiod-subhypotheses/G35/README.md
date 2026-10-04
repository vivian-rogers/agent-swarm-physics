# H94 × G35: Test your game (forked per room) (2026-03-16 → 03-20)

**Verdict:** mixed
**Role:** native
**Period:** regime II · mode C · 12 agents · #best / #rest · 5 days. One unit (216 quanta, 3 repos).

## Why this period
**Native: an operator-assigned room constraint.** Each room evolves its own fork of the #34 RPG. The allocation should be explained by which room an agent is in (M3), not by ownership: fork ownership belongs to whoever pushed first, while the room assignment is the field.

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list; this period's structural counts (`counts.json`: quanta, commits, agents, repos per unit). No D_k, price, κ or signature on real data.

- N1: the room constraint carries most of the allocation information: (D_2 − D_3)/D_1 ≥ 0.5, or (D_1 − D_3)/D_1 ≥ 0.7 (0.6).
- N2: residual after M3 ≤ 0.2 · D_1 (max-ent given room and ownership) (0.5).
- N3: κ < 1 (two or three forks share the episodes about evenly) (0.5).
- Against: residual > 0.5 · D_1 after M3.

## Result
*Run 2026-10-04.*

| Unit | quanta | D_1 | persistence floor_1 | D_final (M2/M3) | floor_final | ownership share | room share | residual / D_1 | λ_own (95% CI) | κ episodes [BE band] | κ w/o named | breadth vs null | singletons obs / M2 / M1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 35 | 216 | 0.96 | 0.25 | 0.20 | 0.10 | 0.18 | 0.61 | +0.10 | 3.07 [2.20, 7.89] | 1.35 [-0.06, 3.21] | n/a | 0.72 | 0 / 0.3 / 0.3 |

Bits per work quantum. Floors: expected KL when the data are a draw from the fitted max-ent table with each agent-day's runs kept (A1). λ_own in nats (agent-block bootstrap; 20 = cap, quasi-separation). κ = (H_MB − H_obs)/(H_MB − H_BE) on work episodes per repo. Breadth: observed distinct repos per agent over the run-preserving null under M2.

Room share 0.61 of D_1 (N1 ✓): the fork-per-room assignment carries most of the allocation information. Residual after M3 0.10·D_1 (N2 ✓). κ 1.35 inside the BE band (N3 ✗; predicted < 1). Breadth 0.72 (the one unit below 0.8).

## Scorecard (period-specific axes)
- C: 2. E: 1 (an operator assignment appears as a room price, λ_room). G: 2 (DQ6 room assignments).

## Notes
- 2026-10-04: folder created by the round-1 agent.
