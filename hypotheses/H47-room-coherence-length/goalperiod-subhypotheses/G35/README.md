# H47 × G35: Test your game to make it as fun and functional as you can!

**Verdict:** supported
**Role:** replication
**Period:** regime II · mode C · up to 12 agents · rooms [2, 3] · 5 active days (non-holdout). Units (shared `period_units`): 35 (goal_start).

## Why this period
First week after the NE15 split (the split itself is confirmatory-only: its pre-side #34 is held out). Regime II. #best 4 agents, #rest 10. Same game task in both rooms but separate forks of the RPG (NE15), so room-specific artifact drives exist.

## Prediction
*Written 2026-10-04 ~06:10 UTC, before running H47 on this period. Templated replication prediction (card P1, P2), not tailored.*
- **P1 (coherence length = room):** at w30, pooled over the period's units, C_B = ρ_c/ρ_w ≤ 0.3 and the room-relabel permutation p for Δ_B = ρ_w − ρ_c is < 0.05.
- **P2 (flat inside the room):** G = ρ_w,low/ρ_w,high ≥ 0.6, and (1 − C_B) > (1 − G).
- **Leadership (card P4), if this period starts with a multi-room goal change:** |L| not significant (cohort-relabel p ≥ 0.05).
- **Verdict rule (card):** supported if C_B ≤ 0.3 and p < 0.05; failed if C_B ≥ 0.6 or p > 0.2; mixed otherwise.
- Against: C_B ≥ 0.6 (content co-moves across rooms as much as within) or no difference from random room labels.

## Result
| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1: C_B ≤ 0.3 and room-relabel p < 0.05 (w30, pooled over 35) | ρ_w 0.55, ρ_c 0.05, **C_B 0.10** [day-bootstrap 0.00, 0.18], p 0.003 | permutation median C_B 1.06 | met |
| P2: G ≥ 0.6 and (1 − C_B) > (1 − G) | G 1.03 (tier-permutation p for G < null: 0.635); boundary drop > within-room drop | G = 1 if flat inside rooms | met |
| Day resolution (secondary) | C_B 0.06, p 0.003 | units ≥ 3 days only | – |
| Robustness (C_B) | L0 0.12 · no dedup 0.10 · DQ5 style 0.09 · DQ6 assigned rooms 0.09 | – | – |
| Per unit (w30) | 35: 0.10 (p 0.010) | 100 permutations each | descriptive |
| Between-room separation F (per day) | day 0 3.6 (z 4.3), median 3.6, Spearman over days 0.30 | within-day room-relabel null (F ≈ 1) | descriptive |

Sharpest replication boundary (separate RPG forks per room). Inside rooms correlation is flat across mention tiers (G ≈ 1), the only period where the room behaves as a flat block.

Figure: `figures/G35_h47.pdf` (per-unit ρ_w/ρ_c, between-room separation per day, kickoff response curves). Data: `data/processed/H47-room-coherence-length/results/` (`coherence.json`, `separation.json`, `leadership.json`).

## Scorecard (period-specific axes)
- **C (adequacy):** beats the room-relabel null (p 0.003).
- **F (robustness):** C_B moves ≤ 0.02 across L0, dedup, DQ5 style vectors and DQ6 assigned rooms.
- **G (ground truth):** room kickoffs forks (shared goal_fields).

## Notes
- 2026-10-04 ~06:10 UTC: folder and prediction written before the real-data run.
- 2026-10-04: results filled from `analysis/explore.py` (round 1, exploratory, non-holdout only).
