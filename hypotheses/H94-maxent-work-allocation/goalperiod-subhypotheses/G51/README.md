# H94 × G51: Each agent: maximize your assigned goal (private roles) (2026-07-06 → 09-04 (non-holdout units 51a–51l))

**Verdict:** mixed
**Role:** replication
**Period:** regime III · mode I/K · 21–32 agents · #general (+ #focus in 51g) · 45 non-holdout days. Units 51a–51l; 51m held out.

## Why this period
Twelve own-role units under one goal type: the largest set of same-type replicas, and the strongest ownership field.

## Prediction
*Written 2026-10-04, before running on this period.* **What I had seen:** the card's list; this period's structural counts (`counts.json`: quanta, commits, agents, repos per unit). No D_k, price, κ or signature on real data.

- P1: D_1 − floor_1 ≥ 0.5 bit per quantum in every testable unit (0.85).
- P2: ownership share ≥ 0.5 (own-artifact) (0.6); λ_own ≥ 2 nats with CI > 0 (0.7).
- P3: residual after M2 ≤ 0.2 · D_1 (equilibrium given ownership) (0.4).
- P5: κ < 1 (episodes spread more evenly than neutral copying) (0.5).
- P8: agent breadth under M2 < 0.8 (0.6).
- λ_own stable across units: coefficient of variation ≤ 0.25 (a constant price) (0.45).

## Result
*Run 2026-10-04 (non-holdout days only). Data: `data/processed/H94-maxent-work-allocation/G51/`; results `.../results/G51.json`.*

| Unit | quanta | D_1 | persistence floor_1 | D_final (M2/M3) | floor_final | ownership share | room share | residual / D_1 | λ_own (95% CI) | κ episodes [BE band] | κ w/o named | breadth vs null | singletons obs / M2 / M1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 51a | 465 | 3.14 | 1.35 | 0.45 | 0.30 | 0.86 | 0.00 | +0.05 | 5.47 [4.10, 9.03] | 2.24 [0.50, 1.68] | 2.37 | 1.23 | 20 / 11.9 / 6.8 |
| 51b | 146 | 3.29 | 2.17 | 0.64 | 0.38 | 0.81 | 0.00 | +0.08 | 5.57 [3.82, 17.26] | 3.29 [0.22, 2.04] | 3.28 | 1.11 | 19 / 13.3 / 6.0 |
| 51c | 968 | 3.38 | 1.27 | 0.50 | 0.19 | 0.85 | 0.00 | +0.09 | 6.54 [4.77, 14.82] | 3.10 [0.60, 1.54] | 3.16 | 1.09 | 23 / 13.2 / 7.6 |
| 51d | 1188 | 3.60 | 1.44 | 0.56 | 0.19 | 0.85 | 0.00 | +0.10 | 8.07 [6.01, 14.64] | 2.59 [0.54, 1.58] | 2.61 | 1.07 | 16 / 14.5 / 3.9 |
| 51e | 803 | 3.66 | 1.73 | 0.46 | 0.19 | 0.87 | 0.00 | +0.07 | 8.52 [6.89, 14.40] | 2.55 [0.58, 1.56] | 2.62 | 1.13 | 20 / 16.1 / 4.4 |
| 51f | 1252 | 3.49 | 1.29 | 0.69 | 0.32 | 0.80 | 0.00 | +0.11 | 6.13 [4.79, 14.83] | 2.53 [0.64, 1.43] | 2.69 | 0.87 | 26 / 14.3 / 6.7 |
| 51g | 3371 | 3.76 | 0.80 | 0.48 | 0.12 | 0.86 | 0.01 | +0.09 | 6.81 [5.46, 11.06] | 3.16 [0.72, 1.35] | 3.10 | 1.00 | 52 / 28.1 / 13.7 |
| 51h | 980 | 3.60 | 1.42 | 0.66 | 0.27 | 0.82 | 0.00 | +0.11 | 6.92 [5.53, 11.58] | 2.35 [0.63, 1.56] | 2.33 | 1.08 | 31 / 18.7 / 6.2 |
| 51i | 478 | 3.60 | 1.85 | 0.74 | 0.27 | 0.79 | 0.00 | +0.13 | 7.82 [5.58, 15.06] | 2.54 [0.52, 1.64] | 2.49 | 1.00 | 26 / 18.7 / 5.2 |
| 51j | 529 | 3.90 | 2.17 | 0.32 | 0.07 | 0.92 | 0.00 | +0.06 | 12.04 [8.56, 16.61] | 2.65 [0.53, 1.49] | 2.68 | 1.03 | 28 / 26.2 / 5.8 |
| 51k | 260 | 3.96 | 2.68 | 0.27 | 0.06 | 0.93 | 0.00 | +0.05 | 18.18 [14.44, 18.75] | 3.33 [0.38, 1.83] | 3.15 | 1.00 | 24 / 20.9 / 4.8 |
| 51l | 290 | 4.13 | 2.87 | 0.21 | 0.05 | 0.95 | 0.00 | +0.04 | 17.83 [13.84, 16.95] | 2.88 [0.39, 1.94] | 2.76 | 1.01 | 25 / 22.0 / 3.8 |

Bits per work quantum. Floors: expected KL when the data are a draw from the fitted max-ent table with each agent-day's runs kept (A1). λ_own in nats (agent-block bootstrap; 20 = cap, quasi-separation). κ = (H_MB − H_obs)/(H_MB − H_BE) on work episodes per repo. Breadth: observed distinct repos per agent over the run-preserving null under M2.

Twelve testable units. Ownership carries 0.79–0.95 of D_1 (λ_own 5.5–18.2; CV 0.47 across units, so the price is not constant: the extra prediction fails). Residual after M2 is 0.04–0.13·D_1 (P3 ✓) but D_final exceeds the persistence floor's 95% in 10 of 12 units (not 51a, 51b) by 0.1–0.3 bit: a small, significant structure remains. κ 2.2–3.3, above the BE band in all 12 (P5 ✗): episodes concentrate on a few repos because agents differ in activity (post hoc κ on distinct agents per repo: −0.9 to 4.4, inside the BE band in 9/12). M2 recovers 54–94% of singleton repos, M1 15–34% (P7 within ±25% in 5/12). Near the cap the agent-block bootstrap is unstable (51l's percentile CI excludes its point estimate).

## Scorecard (period-specific axes)
- C: 1 (small residual above the floor). D: 1 (singleton counts). I: 1 (12 same-goal units agree on ownership share 0.79–0.95).

## Notes
- 2026-10-04: folder created by the round-1 agent.
- 2026-10-04 (after the prediction above, before the real run): the synthetic summary showed the S0-world κ on episodes for this period's synthetic unit, which tracks the real repo-size margin (card amendment A1: 31a 1.64, 39 0.49, 41 1.99, 51d 0.84). The prediction was not changed.
