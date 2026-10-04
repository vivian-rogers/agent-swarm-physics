# H94 × G38: Choose a charity and raise money (year 2) (2026-04-02 → 04-24)

**Verdict:** mixed
**Role:** replication
**Period:** regime III · mode C · 12–14 agents · #best / #rest (room-specific kickoffs) · 17 days. Units 38a–38e; only 38a has ≥ 100 quanta.

## Why this period
Long shared-objective period with room-specific kickoffs: the room constraint should matter here if anywhere among shared weeks.

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list; this period's structural counts (`counts.json`: quanta, commits, agents, repos per unit). No D_k, price, κ or signature on real data.

- P1: D_1 − floor_1 ≥ 0.5 bit per quantum in every testable unit (0.85).
- P2: ownership share (D_1 − D_2)/D_1 < 0.5 (shared week) (0.6).
- P3: residual after M2/M3 > 0.2 · D_1 (HH285's equilibrium fails) (0.7).
- P5: κ ≥ 1 (concentration at or beyond neutral copying) (0.5); P6: κ without kickoff-named repos < κ.
- P8: agent breadth under M2 < 0.8 (0.65).
- Room constraint (M3) explains ≥ 0.1 of D_1 (room kickoffs differ).

## Result
*Run 2026-10-04 (non-holdout days only). Data: `data/processed/H94-maxent-work-allocation/G38/`; results `.../results/G38.json`.*

| Unit | quanta | D_1 | persistence floor_1 | D_final (M2/M3) | floor_final | ownership share | room share | residual / D_1 | λ_own (95% CI) | κ episodes [BE band] | κ w/o named | breadth vs null | singletons obs / M2 / M1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 38a | 350 | 1.58 | 1.12 | 1.05 | 0.85 | 0.22 | 0.12 | +0.13 | 2.18 [1.73, 4.36] | 4.08 [0.58, 1.56] | 4.13 | 0.96 | 63 / 32.7 / 30.6 |
| 38b | 77 | 1.29 | – | 0.13 | – | 0.29 | – | – | 5.45 | 1.90 | – | – | descriptive (< 100 quanta) |
| 38c | 31 | 1.22 | – | 0.00 | – | 0.48 | – | – | 13.56 | 0.88 | – | – | descriptive (< 100 quanta) |
| 38d | 46 | 1.00 | – | 0.24 | – | 0.14 | – | – | 3.27 | 1.96 | – | – | descriptive (< 100 quanta) |
| 38e | 72 | 1.20 | – | 0.53 | – | 0.05 | – | – | 1.33 | 2.63 | – | – | descriptive (< 100 quanta) |

Bits per work quantum. Floors: expected KL when the data are a draw from the fitted max-ent table with each agent-day's runs kept (A1). λ_own in nats (agent-block bootstrap; 20 = cap, quasi-separation). κ = (H_MB − H_obs)/(H_MB − H_BE) on work episodes per repo. Breadth: observed distinct repos per agent over the run-preserving null under M2.

38a testable (350 quanta); 38b–e descriptive. D_1 − floor 0.46 (P1 ✗ narrowly). Ownership share 0.22 ✓; room share 0.12 ✓ (room kickoffs differ; predicted ≥ 0.1); residual 0.13·D_1 (P3 ✓). κ 4.08 above the BE band and unchanged without named repos (P6 ✗). Breadth 0.96 (P8 ✗).

## Scorecard (period-specific axes)
- C: 1. G: 1 (room-specific kickoffs carry 0.19 bit).

## Notes
- 2026-10-04: folder created by the round-1 agent.
