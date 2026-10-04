# H47 × G37: Pick your own goal!

**Verdict:** mixed
**Role:** replication
**Period:** regime III · mode F · up to 12 agents · rooms [2, 3] · 3 active days (non-holdout). Units (shared `period_units`): 37 (goal_start).

## Why this period
Two rooms, three days, free goal (mode F). H26 found content co-moving across rooms here (its smallest room excess), so it is the likeliest replication failure.

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
| P1: C_B ≤ 0.3 and room-relabel p < 0.05 (w30, pooled over 37) | ρ_w 0.20, ρ_c 0.11, **C_B 0.55** [day-bootstrap 0.14, 0.78], p 0.080 | permutation median C_B 1.03 | not met |
| P2: G ≥ 0.6 and (1 − C_B) > (1 − G) | G 0.16 (tier-permutation p for G < null: 0.003); boundary drop ≤ within-room drop | G = 1 if flat inside rooms | not met |
| Day resolution (secondary) | C_B 0.97, p 0.458 | units ≥ 3 days only | – |
| Robustness (C_B) | L0 0.52 · no dedup 0.55 · DQ5 style 0.45 · DQ6 assigned rooms 0.54 | – | – |
| Per unit (w30) | 37: 0.55 (p 0.079) | 100 permutations each | descriptive |
| Between-room separation F (per day) | day 0 1.7 (z 1.2), median 3.0, Spearman over days 1.00 | within-day room-relabel null (F ≈ 1) | descriptive |
| Leadership at the #37 kickoff (card P4): no lead | L -0.28 (agent-bootstrap [-0.38, -0.00]), cohort-relabel p 0.178; dT50 -4.0 bins (p 0.345) | post hoc: first post-kickoff statement after 1.3 / 10.6 min (#best / #rest), shift fraction y 0.45 / 0.67 | met (no lead) |

Mixed: the boundary is weak (cross-room correlation half the within-room level; permutation p 0.08); at day level C_B ≈ 1. Identical room kickoffs, free goal, rooms barely separated (F ≤ 3).

Figure: `figures/G37_h47.pdf` (per-unit ρ_w/ρ_c, between-room separation per day, kickoff response curves). Data: `data/processed/H47-room-coherence-length/results/` (`coherence.json`, `separation.json`, `leadership.json`).

## Scorecard (period-specific axes)
- **C (adequacy):** does not beat the room-relabel null (p 0.080).
- **F (robustness):** C_B moves ≤ 0.10 across L0, dedup, DQ5 style vectors and DQ6 assigned rooms.
- **G (ground truth):** room kickoffs identical (shared goal_fields).

## Notes
- 2026-10-04 ~06:10 UTC: folder and prediction written before the real-data run.
- 2026-10-04: results filled from `analysis/explore.py` (round 1, exploratory, non-holdout only).
