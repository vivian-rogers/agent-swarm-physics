# H47 × G36: Interact with other AI agents outside the Village!

**Verdict:** supported
**Role:** replication
**Period:** regime II/III · mode C · up to 12 agents · rooms [2, 3] · 5 active days (non-holdout). Units (shared `period_units`): 36a (goal_start); 36b (ne:NE14; ne:NE41); 36c (ne:NE16).

## Why this period
Two rooms, three units (36a regime II; NE14 regime boundary on 03-24; NE16 on 03-26). Outreach goal. Kickoff 03-23 is a multi-room goal change for the leadership test.

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
| P1: C_B ≤ 0.3 and room-relabel p < 0.05 (w30, pooled over 36a, 36b, 36c) | ρ_w 0.27, ρ_c 0.06, **C_B 0.24** [day-bootstrap -0.01, 0.56], p 0.003 | permutation median C_B 0.99 | met |
| P2: G ≥ 0.6 and (1 − C_B) > (1 − G) | G 0.51 (tier-permutation p for G < null: 0.003); boundary drop > within-room drop | G = 1 if flat inside rooms | half |
| Day resolution (secondary) | C_B –, p – | units ≥ 3 days only | – |
| Robustness (C_B) | L0 0.25 · no dedup 0.25 · DQ5 style 0.24 · DQ6 assigned rooms 0.23 | – | – |
| Per unit (w30) | 36a: 0.12 (p 0.010) · 36b: -0.07 (p 0.030) · 36c: 0.72 (p 0.158) | 100 permutations each | descriptive |
| Between-room separation F (per day) | day 0 2.0 (z 2.3), median 3.0, Spearman over days -0.40 | within-day room-relabel null (F ≈ 1) | descriptive |
| Leadership at the #36 kickoff (card P4): no lead | L 0.23 (agent-bootstrap [0.06, 0.42]), cohort-relabel p 0.273; dT50 0.0 bins (p 1.000) | post hoc: first post-kickoff statement after 1.3 / 1.4 min (#best / #rest), shift fraction y 0.85 / 0.69 | met (no lead) |

Supported, with identical room kickoffs. Inside the rooms, correlation is concentrated in pairs that mention each other (G 0.51).

Figure: `figures/G36_h47.pdf` (per-unit ρ_w/ρ_c, between-room separation per day, kickoff response curves). Data: `data/processed/H47-room-coherence-length/results/` (`coherence.json`, `separation.json`, `leadership.json`).

## Scorecard (period-specific axes)
- **C (adequacy):** beats the room-relabel null (p 0.003).
- **F (robustness):** C_B moves ≤ 0.01 across L0, dedup, DQ5 style vectors and DQ6 assigned rooms.
- **G (ground truth):** room kickoffs identical (shared goal_fields).

## Notes
- 2026-10-04 ~06:10 UTC: folder and prediction written before the real-data run.
- 2026-10-04: results filled from `analysis/explore.py` (round 1, exploratory, non-holdout only).
