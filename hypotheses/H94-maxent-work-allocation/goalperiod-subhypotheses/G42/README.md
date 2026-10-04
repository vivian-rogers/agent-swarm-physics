# H94 × G42: Run your own YouTube channel (2026-05-18 → 05-22)

**Verdict:** mixed
**Role:** replication
**Period:** regime III · mode I · 14 agents · #best / #rest · 5 days. Units 42a, 42b (join).

## Why this period
Own-artifact week (individual channels; H11 ownership 0.73).

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list; this period's structural counts (`counts.json`: quanta, commits, agents, repos per unit). No D_k, price, κ or signature on real data.

- P1: D_1 − floor_1 ≥ 0.5 bit per quantum in every testable unit (0.85).
- P2: ownership share ≥ 0.5 (own-artifact) (0.6); λ_own ≥ 2 nats with CI > 0 (0.7).
- P3: residual after M2 ≤ 0.2 · D_1 (equilibrium given ownership) (0.4).
- P5: κ < 1 (episodes spread more evenly than neutral copying) (0.5).
- P8: agent breadth under M2 < 0.8 (0.6).

## Result
*Run 2026-10-04 (non-holdout days only). Data: `data/processed/H94-maxent-work-allocation/G42/`; results `.../results/G42.json`.*

| Unit | quanta | D_1 | persistence floor_1 | D_final (M2/M3) | floor_final | ownership share | room share | residual / D_1 | λ_own (95% CI) | κ episodes [BE band] | κ w/o named | breadth vs null | singletons obs / M2 / M1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 42a | 132 | 2.91 | 1.76 | 0.00 | 0.00 | 1.00 | 0.00 | -0.00 | 17.54 [13.32, 16.11] | 0.82 [0.05, 2.55] | -0.54 | 1.13 | 10 / 9.3 / 2.2 |
| 42b | 226 | 2.84 | 1.46 | 0.19 | 0.11 | 0.93 | 0.00 | +0.03 | 17.24 [12.73, 17.24] | 1.00 [0.21, 2.21] | 1.64 | 0.93 | 8 / 7.6 / 0.8 |

Bits per work quantum. Floors: expected KL when the data are a draw from the fitted max-ent table with each agent-day's runs kept (A1). λ_own in nats (agent-block bootstrap; 20 = cap, quasi-separation). κ = (H_MB − H_obs)/(H_MB − H_BE) on work episodes per repo. Breadth: observed distinct repos per agent over the run-preserving null under M2.

Both units: ownership near-deterministic (λ_own 17.2–17.5, share 0.93–1.00), residual ≤ 0.03·D_1 (P3 ✓), D_1 − floor 1.15–1.38 ✓. κ 0.82 and 1.00, inside the BE band (P5 ✗ by the point rule). M2 predicts 9.3/10 and 7.6/8 singletons (M1: 2.2, 0.8).

## Scorecard (period-specific axes)
- C: 2. G: 2 (individual channels).

## Notes
- 2026-10-04: folder created by the round-1 agent.
