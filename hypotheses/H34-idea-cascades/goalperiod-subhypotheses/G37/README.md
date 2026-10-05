# H34 × G37: Pick your own goal! (2026-03-30 → 2026-04-02)

**Verdict:** supported
**Verdict (1b):** supported (ledger visibility: R̂ 0.21, HR₁₀ 96.2 [60.3, 164.0], tail ok; H57 placebo HR unread/seen 7.7/62.3)
**Round 2 (2026-10-05):** replication only; the 1b verdict stands. Gamma-mixed branching α̂ 1.82 [0.85, 4.69], tail covered; semantic R̂ 0.10 (bge) / 0.09 (gte). **NE (round 2), boundary #36→#37:** #best→#best (N 3→3): Δ ln R_src +0.09 [-0.24, +0.34] vs predicted +0.00; #rest→#rest (N 9→7): Δ ln R_src -0.20 [-0.39, -0.04] vs predicted -0.13.
**Role:** replication (exploratory)
**Period:** regime III · mode F · 13 agents at start (median room size 9) · 3 non-holdout days. Setup: Three-day free period: audit accumulated frameworks and habits. #best / #rest split continues. First goal in regime III.

## Why this period
Secondary period for the cross-period criticality link (P4) and transfer of the forecast rule (P7). Mode F (free / pick your own), regime III.

## Prediction
*Written 2026-10-04 02:00 UTC, before running on this period* (after the synthetic validation and amendments A1–A5 of the main card; no real cascade statistic had been computed for any period).

| # | Prediction here | Counts against |
| --- | --- | --- |
| P1 | R̂ < 1 with upper 95% CI < 1; typical 0.05–0.5 | lower CI ≥ 1 |
| P2 | R̂ < H03 n̂_talk = 0.30; R_c < R̂ | R̂ > n̂_talk beyond its CI |
| P3a (A1) | observed P(s ≥ 3) and P(s ≥ 5) inside the FN-GW 90% band (if ≥ 50 trees) | outside the band |
| P5 (A2) | contagion beyond the field: HR₁₀ > 1 with lower CI > 1 | HR₁₀ CI includes 1 or < 1 |
| P6 (A3) | pooled recency HR(2 vs 1) ≤ 2.5 (not complex) | HR(2 vs 1) > 3 with lower CI > 2.5 |

**Verdict rule (A2):** supported = P5 (HR₁₀ lower CI > 1) and P3a pass; failed = both fail, or R̂ lower CI ≥ 1; mixed = exactly one passes; n/a = fewer than 20 non-seed agent first uses (or < 50 trees for P3a, which then counts as not tested and the verdict rests on P5: supported → mixed at best).

## Result
**supported.** 849 ideas, 1087 agent first uses, 862 trees, N_room 9; R̂ = 0.207, contagion share R_c = 0.204, HR₁₀ = 64.84; P(s ≥ 2) = 0.167, largest tree 7.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 R̂ < 1 (upper CI < 1) | R̂ = 0.207 [0.175, 0.235] | critical R = 1 | pass |
| P2 R̂ < H03 n̂_talk | R̂ 0.207 vs n̂ 0.30; R_c = 0.204 | HH108: R̂ > n̂ | pass |
| P3a FN-GW band covers P(s ≥ 3), P(s ≥ 5) | P(s≥3) 0.051 (band 0.036–0.067); P(s≥5) 0.008 (band 0.001–0.009) | GW-NB band covers both: yes | pass |
| P3b pure s^−3/2 rejected; τ_app ≥ 2 | LR 476.3; τ_app 3.04 | critical branching | pass |
| P5 HR₁₀ > 1, lower CI > 1 (A2) | HR₁₀ = 64.84 [43.60, 102.00] (25 adoptions at k = 0) | field: HR₁₀ ≤ 1 | pass |
| P5a jitter excess (pre-registered; failed guard) | exposed 0.945 vs null 0.974, p = 1.00 | uninterpretable (S2) | n/a |
| P6 pooled HR(2 vs 1) ≤ 2.5 | 3.08 [1.98, 4.42] | complex > 3; heterogeneity inflates | ambiguous |
| P5c cross-room ratio > 3 | 68.0 [30.6, 222.4] (P(adopt) 0.063 vs 0.0009) | field ≈ 1–1.8 (S2) | pass (room fields confound) |
| P7 day-ahead 90% PI coverage (pre-registered FN-GW) | P(s≥2) 0.50, P(s≥3) 1.00 over 2 days | post-hoc V3: 0.50, 1.00 | fail |

**By idea class** (U artifact, D number, N name/coinage, W rare word):

| Class | ideas | agent nodes | R̂ [95% CI] | R_c | P(s ≥ 2) | P(s ≥ 3) | s_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D | 22 | 32 | 0.25 [0.10, 0.39] | 0.20 | 0.250 | 0.042 | 4 |
| N | 776 | 993 | 0.21 [0.17, 0.24] | 0.20 | 0.168 | 0.051 | 7 |
| U | 33 | 36 | 0.08 [0.00, 0.21] | 0.08 | 0.030 | 0.030 | 4 |
| W | 18 | 26 | 0.31 [0.10, 0.49] | 0.31 | 0.278 | 0.111 | 4 |

Data: `data/processed/H34-idea-cascades/G37/`. Figures: `../../figures/` (cross-period); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): HR₁₀ beats the field null (lower CI 43.60). D (unfitted shape): FN-GW band covers the tail; pure s^−3/2 rejected. G (rooms): never-exposed agents adopt far less (ratio 68.0), confounded by room fields. E: no natural experiment inside this period was used.

## Notes
- Two rooms active: the cross-room contrast is available but confounded by room-specific fields (rooms often worked on different projects).
- Censoring check: R̂ without trees rooted on the last day = 0.230.
- Root vs non-root mean offspring 0.191 vs 0.267 (GW assumes equal).
- Root types: invented 0.98, from humans 0.000, field (unexposed) 0.015; 0.95 of non-seed first uses were visibly exposed.

## Round 2 (2026-10-05)
*Replication rows for the card's R1 and R4 (predictions in the main card, written 03:50 UTC). Role: replication; no verdict change.*

| Quantity | Value | Reference |
| --- | --- | --- |
| R1 gamma-mixed FN-GW: α̂ (CV² = 1/α), μ̂ | 1.82 [0.85, 4.69], μ̂ 0.203 | LR vs one R: 16.8 (5% point 2.71) |
| R1 tail: P(s ≥ 3), P(s ≥ 5) | 0.054, 0.0082 | Γ-FN 90% band [0.039, 0.070], [0.0035, 0.0187]: covered |
| R1 non-root / root offspring (unfitted) | 1.36 | Γ-FN band [1.00, 1.83]; one R 0.78; homogeneous skeleton ≤ 0.91 |
| R1 day-ahead log score, Γ-FN minus beta-binomial | 1.1 nats | > 0 favours Γ-FN |
| R4 semantic R̂, bge (θ 0.90) | 0.10 [0.08, 0.13], 643 first uses | marker R̂ (1b) in the 1b line above |
| R4 semantic R̂, gte (θ 0.877) | 0.09 [0.07, 0.11], 651 first uses | |
| R4 HR₁₀ (bge / gte) | 131.3 / 116.4 | field null 1 |
| R4 HR_unread5 / HR_seen5 (bge / gte) | 0.00 / 0.21 | copying < 1; marker median 0.56 |

**R2 native, boundary #36→#37** (role native; dilution rule R̂ ∝ (N − 1)^0.451 written before looking): #best→#best (N 3→3): Δ ln R_src +0.09 [-0.24, +0.34] vs predicted +0.00; #rest→#rest (N 9→7): Δ ln R_src -0.20 [-0.39, -0.04] vs predicted -0.13. The boundary is also a goal change, so only the difference between groups is read (card, R2).
