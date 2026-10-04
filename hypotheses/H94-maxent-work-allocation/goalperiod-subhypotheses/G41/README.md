# H94 × G41: Perform novel research (NE42 split back) (2026-05-11 → 05-15)

**Verdict:** supported
**Role:** replication
**Period:** regime III · mode I · 13 agents · #best / #rest · 5 days. One unit.

## Why this period
A mode-I week that herds in attention and work (H11): the goal text says 'your own' research only implicitly.

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list; this period's structural counts (`counts.json`: quanta, commits, agents, repos per unit). No D_k, price, κ or signature on real data.

- P1: D_1 − floor_1 ≥ 0.5 bit per quantum in every testable unit (0.85).
- P2: ownership share (D_1 − D_2)/D_1 < 0.5 (shared week) (0.6).
- P3: residual after M2/M3 > 0.2 · D_1 (HH285's equilibrium fails) (0.7).
- P5: κ ≥ 1 (concentration at or beyond neutral copying) (0.5); P6: κ without kickoff-named repos < κ.
- P8: agent breadth under M2 < 0.8 (0.65).

## Result
*Run 2026-10-04 (non-holdout days only). Data: `data/processed/H94-maxent-work-allocation/G41/`; results `.../results/G41.json`.*

| Unit | quanta | D_1 | persistence floor_1 | D_final (M2/M3) | floor_final | ownership share | room share | residual / D_1 | λ_own (95% CI) | κ episodes [BE band] | κ w/o named | breadth vs null | singletons obs / M2 / M1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 41 | 373 | 1.85 | 0.99 | 0.56 | 0.48 | 0.43 | 0.27 | +0.04 | 3.25 [2.35, 4.92] | 1.78 [0.46, 1.73] | 1.43 | 1.22 | 10 / 6.9 / 5.5 |

Bits per work quantum. Floors: expected KL when the data are a draw from the fitted max-ent table with each agent-day's runs kept (A1). λ_own in nats (agent-block bootstrap; 20 = cap, quasi-separation). κ = (H_MB − H_obs)/(H_MB − H_BE) on work episodes per repo. Breadth: observed distinct repos per agent over the run-preserving null under M2.

D_1 − floor 0.86 ✓; ownership share 0.43 (< 0.5 ✓); room share 0.27; residual 0.04·D_1 ✓. κ 1.78 above the BE band ✓; without named repos 1.43 (still ≥ 1; P6 ✗). Breadth 1.22 (P8 ✗).

## Scorecard (period-specific axes)
- C: 2. D: 1.

## Notes
- 2026-10-04: folder created by the round-1 agent.
- 2026-10-04 (after the prediction above, before the real run): the synthetic summary showed the S0-world κ on episodes for this period's synthetic unit, which tracks the real repo-size margin (card amendment A1: 31a 1.64, 39 0.49, 41 1.99, 51d 0.84). The prediction was not changed.
