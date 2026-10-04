# H94 × G33: Discuss, debate and act on the Pentagon–AI news (2026-03-02 → 03-04)

**Verdict:** mixed
**Role:** replication
**Period:** regime II · mode C · 11 agents · #general · 3 days. One unit.

## Why this period
Short shared-artifact week; work herds (H11 z +9.0, co-location 0.94).

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list; this period's structural counts (`counts.json`: quanta, commits, agents, repos per unit). No D_k, price, κ or signature on real data.

- P1: D_1 − floor_1 ≥ 0.5 bit per quantum in every testable unit (0.85).
- P2: ownership share (D_1 − D_2)/D_1 < 0.5 (shared week) (0.6).
- P3: residual after M2/M3 > 0.2 · D_1 (HH285's equilibrium fails) (0.7).
- P5: κ ≥ 1 (concentration at or beyond neutral copying) (0.5); P6: κ without kickoff-named repos < κ.
- P8: agent breadth under M2 < 0.8 (0.65).

## Result
*Run 2026-10-04 (non-holdout days only). Data: `data/processed/H94-maxent-work-allocation/G33/`; results `.../results/G33.json`.*

| Unit | quanta | D_1 | persistence floor_1 | D_final (M2/M3) | floor_final | ownership share | room share | residual / D_1 | λ_own (95% CI) | κ episodes [BE band] | κ w/o named | breadth vs null | singletons obs / M2 / M1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 33 | 176 | 0.29 | 0.36 | 0.25 | 0.33 | 0.14 | 0.00 | -0.27 | 1.32 [-0.48, 8.18] | 3.07 [0.14, 2.18] | 3.32 | 1.15 | 5 / 1.6 / 1.6 |

Bits per work quantum. Floors: expected KL when the data are a draw from the fitted max-ent table with each agent-day's runs kept (A1). λ_own in nats (agent-block bootstrap; 20 = cap, quasi-separation). κ = (H_MB − H_obs)/(H_MB − H_BE) on work episodes per repo. Breadth: observed distinct repos per agent over the run-preserving null under M2.

One unit (176 quanta). D_1 0.29 sits *below* the persistence floor 0.36: work is as unstructured as max-ent allows (P1 ✗). Ownership share 0.14 ✓; κ 3.07 above the BE band ✓ but unchanged without named repos (3.32; P6 ✗). Breadth 1.15 (P8 ✗).

## Scorecard (period-specific axes)
- C: 2. D: 0.

## Notes
- 2026-10-04: folder created by the round-1 agent.
