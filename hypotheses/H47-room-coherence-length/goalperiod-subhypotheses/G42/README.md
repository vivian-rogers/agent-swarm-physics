# H47 × G42: Run your own Youtube channel!

**Verdict:** mixed
**Role:** replication
**Period:** regime III · mode I · up to 16 agents · rooms [2, 3] · 5 active days (non-holdout). Units (shared `period_units`): 42a (goal_start); 42b (roster_join:Gemini 3.5 Flash).

## Why this period
Two rooms, two units (a join on 05-20). H26 found mostly global content co-fluctuation here.

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
| P1: C_B ≤ 0.3 and room-relabel p < 0.05 (w30, pooled over 42a, 42b) | ρ_w 0.14, ρ_c 0.07, **C_B 0.54** [day-bootstrap 0.33, 0.78], p 0.020 | permutation median C_B 0.97 | not met |
| P2: G ≥ 0.6 and (1 − C_B) > (1 − G) | G 0.48 (tier-permutation p for G < null: 0.003); boundary drop ≤ within-room drop | G = 1 if flat inside rooms | not met |
| Day resolution (secondary) | C_B 0.69, p 0.246 | units ≥ 3 days only | – |
| Robustness (C_B) | L0 0.60 · no dedup 0.52 · DQ5 style 0.49 · DQ6 assigned rooms 0.55 | – | – |
| Per unit (w30) | 42a: 0.62 (p 0.109) · 42b: 0.44 (p 0.069) | 100 permutations each | descriptive |
| Between-room separation F (per day) | day 0 2.2 (z 3.3), median 1.6, Spearman over days 0.30 | within-day room-relabel null (F ≈ 1) | descriptive |
| Leadership at the #42 kickoff (card P4): no lead | L -0.05 (agent-bootstrap [-0.20, 0.15]), cohort-relabel p 0.665; dT50 0.0 bins (p 1.000) | post hoc: first post-kickoff statement after 1.7 / 1.6 min (#best / #rest), shift fraction y 0.95 / 0.87 | met (no lead) |

Mixed: the boundary is significant (p 0.02) but shallow (C_B 0.54); identical kickoffs; rooms barely separated (F 1.2–2.3).

Figure: `figures/G42_h47.pdf` (per-unit ρ_w/ρ_c, between-room separation per day, kickoff response curves). Data: `data/processed/H47-room-coherence-length/results/` (`coherence.json`, `separation.json`, `leadership.json`).

## Scorecard (period-specific axes)
- **C (adequacy):** beats the room-relabel null (p 0.020).
- **F (robustness):** C_B moves ≤ 0.06 across L0, dedup, DQ5 style vectors and DQ6 assigned rooms.
- **G (ground truth):** room kickoffs identical (shared goal_fields).

## Notes
- 2026-10-04 ~06:10 UTC: folder and prediction written before the real-data run.
- 2026-10-04: results filled from `analysis/explore.py` (round 1, exploratory, non-holdout only).
