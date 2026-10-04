# H104 × G51: private roles (2026-07-06 → 09-04, non-holdout)

**Verdict:** mixed
**Role:** exploratory (replication; hosts the NE38 and NE43 natives in their own folders)
**Period:** regime III · 21–32 agents · #general (+ #focus 08-05 → 08-21) · 44 non-holdout days · 50 human sessions, 24 isolated eligible steps · work and attention channels.

## Why this period
The only period with enough isolated human steps (24) to test a step response, and with enough quiet windows (221) to test between-step Poisson switching (Amendment A1).

## Prediction
*Written 2026-10-04 21:04 UTC, before running on this period.* Card P1–P7 as amended (A1): X > 1 with p < 0.05 and X_pre inside [0.8, 1.25] (credence 0.45 attention, 0.3 work); D in [0.8, 1.25] (credence 0.2: endogenous herding, H28/H53/H63, should make D > 1.25); BR CI > 1 (0.4); dose ρ_s > 0 (0.3); tail inconclusive by A1. Verdict rule (A1): *supported* needs X > 1, D in band and BR CI > 1; *failed* if X ≤ 1, or D > 1.25 with BR CI including 1.

## Result
*Run 2026-10-04 21:04 UTC. Data: `data/processed/H104-barkhausen-avalanches/results/periods.parquet` (primary variant).*

| Channel | Steps | X [95% CI] (p) | V (p) | F_A [CI] | τ̂ (π̂) | D (p) | BR [CI] | ρ(m, E) | X_pre | K |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| work | 24 | 1.09 [0.84, 1.32] (0.25) | 1.19 (0.23) | 2.4 [−1.4, 26] | edge (0.99) | 1.12 (0.066) | 0.52 [0.31, 1.27] | −0.30 (p 0.16) | 0.82 | 2.42 |
| attention | 24 | 1.07 [0.97, 1.18] (0.069) | 1.02 (0.43) | 0.15 [−17.7, 12.9] | edge (0.57) | 1.18 (0.011) | 1.40 [0.31, 4.78] | −0.10 (p 0.65) | 0.93 | 1.65 |

- **Verdict by the A1 rule: mixed** (X > 1 but not significant; D ≤ 1.25; BR CI includes 1). Read with the synthetic: the Barkhausen world gives X ≈ 1.87 / 1.25 (5th percentiles 1.47 / 1.13), so the observed step response is below that effect size in both channels. The HH kill condition (bursts as frequent between steps as after) is met.
- Exceedance of the null 95th percentile: 0.00 after steps vs 0.04 in quiet windows (work), 0.04 vs 0.04 (attention).
- Peri-step curve: `../../figures/summary_obs_col.pdf` (switching per 10-min bin / null, −60 to +120 min).
- Read-out split (work): 0 switches before the receiving call in 43 agent-hours vs 54 after; read as idleness (no commit without a call), not as a read effect. Attention: 0.68× null.
