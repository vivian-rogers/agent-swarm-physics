# H34 × G13: Design, run and write up a human subjects experiment (2025-09-08 → 2025-09-22)

**Verdict:** mixed
**Verdict (1b):** mixed (ledger visibility: R̂ 0.15, HR₁₀ 4.4 [3.0, 6.7], tail heavy; H57 placebo HR unread/seen 2.8/3.3)
**Round 2 (2026-10-05):** replication only; the 1b verdict stands. Gamma-mixed branching α̂ 0.59 [0.44, 1.14], tail covered; semantic R̂ 0.06 (bge) / 0.07 (gte).
**Role:** replication (exploratory)
**Period:** regime I · mode C · 6 agents at start (median room size 6) · 10 non-holdout days. Setup: Design, run and write up a real human-subjects experiment (power analysis: 126 participants). Two weeks, collaborative.

## Why this period
Secondary period for the cross-period criticality link (P4) and transfer of the forecast rule (P7). Mode C (shared objective), regime I.

## Prediction
*Written 2026-10-04 02:00 UTC, before running on this period* (after the synthetic validation and amendments A1–A5 of the main card; no real cascade statistic had been computed for any period).

| # | Prediction here | Counts against |
| --- | --- | --- |
| P1 | R̂ < 1 with upper 95% CI < 1; typical 0.05–0.5 | lower CI ≥ 1 |
| P2 | R̂ < H03 n̂_talk = 0.57; R_c < R̂ | R̂ > n̂_talk beyond its CI |
| P3a (A1) | observed P(s ≥ 3) and P(s ≥ 5) inside the FN-GW 90% band (if ≥ 50 trees) | outside the band |
| P5 (A2) | contagion beyond the field: HR₁₀ > 1 with lower CI > 1 | HR₁₀ CI includes 1 or < 1 |
| P6 (A3) | pooled recency HR(2 vs 1) ≤ 2.5 (not complex) | HR(2 vs 1) > 3 with lower CI > 2.5 |

**Verdict rule (A2):** supported = P5 (HR₁₀ lower CI > 1) and P3a pass; failed = both fail, or R̂ lower CI ≥ 1; mixed = exactly one passes; n/a = fewer than 20 non-seed agent first uses (or < 50 trees for P3a, which then counts as not tested and the verdict rests on P5: supported → mixed at best).

## Result
**mixed.** 1235 ideas, 1462 agent first uses, 1261 trees, N_room 6; R̂ = 0.137, contagion share R_c = 0.078, HR₁₀ = 2.30; P(s ≥ 2) = 0.103, largest tree 6.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 R̂ < 1 (upper CI < 1) | R̂ = 0.137 [0.114, 0.162] | critical R = 1 | pass |
| P2 R̂ < H03 n̂_talk | R̂ 0.137 vs n̂ 0.57; R_c = 0.078 | HH108: R̂ > n̂ | pass |
| P3a FN-GW band covers P(s ≥ 3), P(s ≥ 5) | P(s≥3) 0.031 (band 0.016–0.044); P(s≥5) 0.009 (band 0.000–0.004) | GW-NB band covers both: no | fail (s≥5 heavier than FN-GW) |
| P3b pure s^−3/2 rejected; τ_app ≥ 2 | LR 773.9; τ_app 3.54 | critical branching | pass |
| P5 HR₁₀ > 1, lower CI > 1 (A2) | HR₁₀ = 2.30 [1.65, 3.32] (50 adoptions at k = 0) | field: HR₁₀ ≤ 1 | pass |
| P5a jitter excess (pre-registered; failed guard) | exposed 0.885 vs null 0.989, p = 1.00 | uninterpretable (S2) | n/a |
| P6 pooled HR(2 vs 1) ≤ 2.5 | 5.73 [3.23, 9.21] | complex > 3; heterogeneity inflates | ambiguous |
| P7 day-ahead 90% PI coverage (pre-registered FN-GW) | P(s≥2) 0.89, P(s≥3) 0.67 over 9 days | post-hoc V3: 0.78, 0.78 | fail |

**By idea class** (U artifact, D number, N name/coinage, W rare word):

| Class | ideas | agent nodes | R̂ [95% CI] | R_c | P(s ≥ 2) | P(s ≥ 3) | s_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D | 177 | 201 | 0.12 [0.06, 0.17] | 0.11 | 0.090 | 0.023 | 5 |
| N | 960 | 1134 | 0.13 [0.11, 0.16] | 0.07 | 0.098 | 0.030 | 6 |
| U | 41 | 56 | 0.27 [0.16, 0.36] | 0.23 | 0.293 | 0.073 | 3 |
| W | 57 | 71 | 0.14 [0.05, 0.24] | 0.00 | 0.098 | 0.049 | 4 |

Data: `data/processed/H34-idea-cascades/G13/`. Figures: `../../figures/` (cross-period); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): HR₁₀ beats the field null (lower CI 1.65). D (unfitted shape): FN-GW band misses the tail; pure s^−3/2 rejected. E: no natural experiment inside this period was used.

## Notes
- Censoring check: R̂ without trees rooted on the last day = 0.128.
- Root vs non-root mean offspring 0.120 vs 0.249 (GW assumes equal).
- Root types: invented 0.98, from humans 0.000, field (unexposed) 0.021; 0.89 of non-seed first uses were visibly exposed.

## Round 2 (2026-10-05)
*Replication rows for the card's R1 and R4 (predictions in the main card, written 03:50 UTC). Role: replication; no verdict change.*

| Quantity | Value | Reference |
| --- | --- | --- |
| R1 gamma-mixed FN-GW: α̂ (CV² = 1/α), μ̂ | 0.59 [0.44, 1.14], μ̂ 0.137 | LR vs one R: 57.9 (5% point 2.71) |
| R1 tail: P(s ≥ 3), P(s ≥ 5) | 0.035, 0.0089 | Γ-FN 90% band [0.023, 0.050], [0.0016, 0.0129]: covered |
| R1 non-root / root offspring (unfitted) | 1.82 | Γ-FN band [1.18, 2.13]; one R 0.74; homogeneous skeleton ≤ 0.91 |
| R1 day-ahead log score, Γ-FN minus beta-binomial | 5.1 nats | > 0 favours Γ-FN |
| R4 semantic R̂, bge (θ 0.90) | 0.06 [0.05, 0.07], 2658 first uses | marker R̂ (1b) in the 1b line above |
| R4 semantic R̂, gte (θ 0.877) | 0.07 [0.06, 0.08], 2432 first uses | |
| R4 HR₁₀ (bge / gte) | 4.9 / 3.8 | field null 1 |
| R4 HR_unread5 / HR_seen5 (bge / gte) | 1.99 / 2.40 | copying < 1; marker median 0.56 |
