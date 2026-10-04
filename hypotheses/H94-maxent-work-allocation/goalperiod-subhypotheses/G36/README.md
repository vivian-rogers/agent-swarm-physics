# H94 × G36: Interact with other AI agents outside the Village (2026-03-23 → 03-27)

**Verdict:** mixed
**Role:** replication
**Period:** regime II → III · mode C · 12 agents · #best / #rest · 5 days. Units 36a–36c; only 36c has ≥ 100 quanta.

## Why this period
Two rooms with identical kickoff text and many small outward-facing projects (22 repos).

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list; this period's structural counts (`counts.json`: quanta, commits, agents, repos per unit). No D_k, price, κ or signature on real data.

- P1: D_1 − floor_1 ≥ 0.5 bit per quantum in every testable unit (0.85).
- P2: ownership share (D_1 − D_2)/D_1 < 0.5 (shared week) (0.6).
- P3: residual after M2/M3 > 0.2 · D_1 (HH285's equilibrium fails) (0.7).
- P5: κ ≥ 1 (concentration at or beyond neutral copying) (0.5); P6: κ without kickoff-named repos < κ.
- P8: agent breadth under M2 < 0.8 (0.65).
- Room constraint (M3) explains < 0.2 of D_1 (identical room kickoffs).

## Result
*Run 2026-10-04 (non-holdout days only). Data: `data/processed/H94-maxent-work-allocation/G36/`; results `.../results/G36.json`.*

| Unit | quanta | D_1 | persistence floor_1 | D_final (M2/M3) | floor_final | ownership share | room share | residual / D_1 | λ_own (95% CI) | κ episodes [BE band] | κ w/o named | breadth vs null | singletons obs / M2 / M1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 36a | 66 | 1.43 | – | 0.97 | – | 0.32 | – | – | 2.38 | 3.72 | – | – | descriptive (< 100 quanta) |
| 36b | 89 | 1.11 | – | 0.89 | – | 0.19 | – | – | 2.15 | 2.47 | – | – | descriptive (< 100 quanta) |
| 36c | 101 | 1.26 | 0.87 | 1.01 | 0.72 | 0.20 | 0.00 | +0.23 | 1.68 [0.73, 5.28] | 1.46 [0.26, 2.10] | 1.46 | 0.96 | 5 / 2.1 / 1.9 |

Bits per work quantum. Floors: expected KL when the data are a draw from the fitted max-ent table with each agent-day's runs kept (A1). λ_own in nats (agent-block bootstrap; 20 = cap, quasi-separation). κ = (H_MB − H_obs)/(H_MB − H_BE) on work episodes per repo. Breadth: observed distinct repos per agent over the run-preserving null under M2.

36c testable (101 quanta); 36a, 36b descriptive. D_1 − floor 0.39 (< 0.5, P1 ✗). Ownership share 0.20 ✓; residual 0.23·D_1 (P3 ✗, the only unit above 0.2); room share 0.004 ✓ (identical room kickoffs). κ 1.46 inside the BE band.

## Scorecard (period-specific axes)
- C: 1.

## Notes
- 2026-10-04: folder created by the round-1 agent.
