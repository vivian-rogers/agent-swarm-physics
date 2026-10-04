# H47 × G39: Build your own interactive world!

**Verdict:** mixed
**Role:** replication
**Period:** regime III · mode I · up to 15 agents · rooms [2, 3] · 5 active days (non-holdout). Units (shared `period_units`): 39 (goal_start).

## Why this period
Two rooms; #best only 4 agents. The A of NE42's A-B-A (also scored there). H05 found no talk block structure in #39.

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
| P1: C_B ≤ 0.3 and room-relabel p < 0.05 (w30, pooled over 39) | ρ_w 0.08, ρ_c 0.05, **C_B 0.57** [day-bootstrap 0.15, 1.34], p 0.113 | permutation median C_B 1.03 | not met |
| P2: G ≥ 0.6 and (1 − C_B) > (1 − G) | G 0.16 (tier-permutation p for G < null: 0.003); boundary drop ≤ within-room drop | G = 1 if flat inside rooms | not met |
| Day resolution (secondary) | C_B 0.40, p 0.047 | units ≥ 3 days only | – |
| Robustness (C_B) | L0 0.63 · no dedup 0.57 · DQ5 style 0.70 · DQ6 assigned rooms 0.57 | – | – |
| Per unit (w30) | 39: 0.57 (p 0.099) | 100 permutations each | descriptive |
| Between-room separation F (per day) | day 0 1.1 (z 0.2), median 2.1, Spearman over days 0.90 | within-day room-relabel null (F ≈ 1) | descriptive |
| Leadership at the #39 kickoff (card P4): no lead | L -0.14 (agent-bootstrap [-0.36, 0.04]), cohort-relabel p 0.182; dT50 0.0 bins (p 1.000) | post hoc: first post-kickoff statement after 3.1 / 2.4 min (#best / #rest), shift fraction y 0.69 / 0.82 | met (no lead) |

Mixed: weak boundary (C_B 0.57, p 0.11), the lowest within-room correlation of all periods (ρ_w 0.08), identical kickoffs and barely separated rooms (F 1.1–2.3). Matches H05's finding of no talk block structure in #39. Also the A1 phase of NE42.

Figure: `figures/G39_h47.pdf` (per-unit ρ_w/ρ_c, between-room separation per day, kickoff response curves). Data: `data/processed/H47-room-coherence-length/results/` (`coherence.json`, `separation.json`, `leadership.json`).

## Scorecard (period-specific axes)
- **C (adequacy):** does not beat the room-relabel null (p 0.113).
- **F (robustness):** C_B moves ≤ 0.13 across L0, dedup, DQ5 style vectors and DQ6 assigned rooms.
- **G (ground truth):** room kickoffs identical (shared goal_fields).

## Notes
- 2026-10-04 ~06:10 UTC: folder and prediction written before the real-data run.
- 2026-10-04: results filled from `analysis/explore.py` (round 1, exploratory, non-holdout only).
