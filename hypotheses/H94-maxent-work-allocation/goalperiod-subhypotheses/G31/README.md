# H94 × G31: Pick your own goal (farewell to Claude 3.7 Sonnet) (2026-02-16 → 02-20)

**Verdict:** mixed
**Role:** replication
**Period:** regime I · mode F · 11–12 agents · #general · 5 days. Units 31a–31d; only 31a has ≥ 100 quanta.

## Why this period
H11's free-week herding wave in work; 34 repos. The strongest herding case for κ.

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list; this period's structural counts (`counts.json`: quanta, commits, agents, repos per unit). No D_k, price, κ or signature on real data; **disclosure:** the H94 synthetic world S0 on unit 31a draws runs from the real margins, and its κ on quanta (≈ 1.8, a smoke run of 2 replicates) therefore reflected the real repo-size margin before this prediction was written.

- P1: D_1 − floor_1 ≥ 0.5 bit per quantum in every testable unit (0.85).
- P2: ownership share (D_1 − D_2)/D_1 < 0.5 (shared week) (0.6).
- P3: residual after M2/M3 > 0.2 · D_1 (HH285's equilibrium fails) (0.7).
- P5: κ ≥ 1 (concentration at or beyond neutral copying) (0.5); P6: κ without kickoff-named repos < κ.
- P8: agent breadth under M2 < 0.8 (0.65).

## Result
*Run 2026-10-04 (non-holdout days only). Data: `data/processed/H94-maxent-work-allocation/G31/`; results `.../results/G31.json`.*

| Unit | quanta | D_1 | persistence floor_1 | D_final (M2/M3) | floor_final | ownership share | room share | residual / D_1 | λ_own (95% CI) | κ episodes [BE band] | κ w/o named | breadth vs null | singletons obs / M2 / M1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 31a | 196 | 0.84 | 0.80 | 0.70 | 0.75 | 0.17 | 0.00 | -0.05 | 1.22 [0.65, 2.39] | 1.81 [0.47, 1.64] | 0.88 | 0.96 | 10 / 6.0 / 5.3 |
| 31b | 91 | 1.82 | – | 1.26 | – | 0.31 | – | – | 2.30 | 0.59 | – | – | descriptive (< 100 quanta) |
| 31c | 70 | 1.36 | – | 0.81 | – | 0.40 | – | – | 2.69 | 0.45 | – | – | descriptive (< 100 quanta) |
| 31d | 87 | 1.30 | – | 1.13 | – | 0.13 | – | – | 1.34 | 1.91 | – | – | descriptive (< 100 quanta) |

Bits per work quantum. Floors: expected KL when the data are a draw from the fitted max-ent table with each agent-day's runs kept (A1). λ_own in nats (agent-block bootstrap; 20 = cap, quasi-separation). κ = (H_MB − H_obs)/(H_MB − H_BE) on work episodes per repo. Breadth: observed distinct repos per agent over the run-preserving null under M2.

31a only (196 quanta). **Plain max-ent with margins and run persistence reproduces the allocation**: D_1 0.84 vs persistence floor 0.80 (P1 fails here: excess 0.04 bit). Ownership share 0.17 (< 0.5 ✓), residual after M2 −0.05·D_1 (✓). κ 1.81 above the BE band (✓), and 0.88 without kickoff-named repos (P6 ✓: the herding concentration is on named repos). Breadth 0.96 (P8 ✗).

## Scorecard (period-specific axes)
- C: 2 (at the persistence floor). D: 1 (κ drop without named repos).

## Notes
- 2026-10-04: folder created by the round-1 agent.
- 2026-10-04 (after the prediction above, before the real run): the synthetic summary showed the S0-world κ on episodes for this period's synthetic unit, which tracks the real repo-size margin (card amendment A1: 31a 1.64, 39 0.49, 41 1.99, 51d 0.84). The prediction was not changed.
