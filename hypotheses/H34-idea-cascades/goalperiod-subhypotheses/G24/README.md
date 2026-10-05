# H34 × G24: Do random acts of kindness! (2025-12-22 → 2025-12-29)

**Verdict:** mixed
**Verdict (1b):** mixed (ledger visibility: R̂ 0.15, HR₁₀ 5.7 [4.3, 7.8], tail heavy; H57 placebo HR unread/seen 4.2/6.0)
**Round 2 (2026-10-05):** replication only; the 1b verdict stands. Gamma-mixed branching α̂ 0.48 [0.40, 0.67], tail covered; semantic R̂ 0.08 (bge) / 0.06 (gte).
**Role:** replication (exploratory)
**Period:** regime I · mode C · 10 agents at start (median room size 10) · 5 non-holdout days. Setup: Random acts of kindness, each confirmed as appreciated. Agents divided up approaches (thanking communities, emailing maintainers, fixing bugs).

## Why this period
Secondary period for the cross-period criticality link (P4) and transfer of the forecast rule (P7). Mode C (shared objective), regime I.

## Prediction
*Written 2026-10-04 02:00 UTC, before running on this period* (after the synthetic validation and amendments A1–A5 of the main card; no real cascade statistic had been computed for any period).

| # | Prediction here | Counts against |
| --- | --- | --- |
| P1 | R̂ < 1 with upper 95% CI < 1; typical 0.05–0.5 | lower CI ≥ 1 |
| P2 | R̂ < H03 n̂_talk = 0.13; R_c < R̂ | R̂ > n̂_talk beyond its CI |
| P3a (A1) | observed P(s ≥ 3) and P(s ≥ 5) inside the FN-GW 90% band (if ≥ 50 trees) | outside the band |
| P5 (A2) | contagion beyond the field: HR₁₀ > 1 with lower CI > 1 | HR₁₀ CI includes 1 or < 1 |
| P6 (A3) | pooled recency HR(2 vs 1) ≤ 2.5 (not complex) | HR(2 vs 1) > 3 with lower CI > 2.5 |

**Verdict rule (A2):** supported = P5 (HR₁₀ lower CI > 1) and P3a pass; failed = both fail, or R̂ lower CI ≥ 1; mixed = exactly one passes; n/a = fewer than 20 non-seed agent first uses (or < 50 trees for P3a, which then counts as not tested and the verdict rests on P5: supported → mixed at best).

## Result
**mixed.** 2853 ideas, 3347 agent first uses, 2870 trees, N_room 10; R̂ = 0.143, contagion share R_c = 0.112, HR₁₀ = 4.65; P(s ≥ 2) = 0.100, largest tree 9.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 R̂ < 1 (upper CI < 1) | R̂ = 0.143 [0.125, 0.161] | critical R = 1 | pass |
| P2 R̂ < H03 n̂_talk | R̂ 0.143 vs n̂ 0.13; R_c = 0.112 | HH108: R̂ > n̂ | fail |
| P3a FN-GW band covers P(s ≥ 3), P(s ≥ 5) | P(s≥3) 0.034 (band 0.024–0.039); P(s≥5) 0.009 (band 0.001–0.005) | GW-NB band covers both: no | fail (s≥5 heavier than FN-GW) |
| P3b pure s^−3/2 rejected; τ_app ≥ 2 | LR 2250.4; τ_app 3.59 | critical branching | pass |
| P5 HR₁₀ > 1, lower CI > 1 (A2) | HR₁₀ = 4.65 [3.49, 6.20] (57 adoptions at k = 0) | field: HR₁₀ ≤ 1 | pass |
| P5a jitter excess (pre-registered; failed guard) | exposed 0.966 vs null 0.985, p = 1.00 | uninterpretable (S2) | n/a |
| P6 pooled HR(2 vs 1) ≤ 2.5 | 8.02 [5.55, 10.99] | complex > 3; heterogeneity inflates | ambiguous |
| P7 day-ahead 90% PI coverage (pre-registered FN-GW) | P(s≥2) 0.00, P(s≥3) 0.00 over 4 days | post-hoc V3: 0.00, 0.25 | fail |

**By idea class** (U artifact, D number, N name/coinage, W rare word):

| Class | ideas | agent nodes | R̂ [95% CI] | R_c | P(s ≥ 2) | P(s ≥ 3) | s_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D | 83 | 114 | 0.26 [0.12, 0.39] | 0.00 | 0.155 | 0.048 | 9 |
| N | 2357 | 2746 | 0.14 [0.12, 0.15] | 0.11 | 0.096 | 0.033 | 8 |
| U | 24 | 41 | 0.41 [0.17, 0.58] | 0.39 | 0.250 | 0.208 | 7 |
| W | 389 | 446 | 0.13 [0.08, 0.17] | 0.12 | 0.100 | 0.026 | 6 |

Data: `data/processed/H34-idea-cascades/G24/`. Figures: `../../figures/` (cross-period); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): HR₁₀ beats the field null (lower CI 3.49). D (unfitted shape): FN-GW band misses the tail; pure s^−3/2 rejected. E: no natural experiment inside this period was used.

## Notes
- Censoring check: R̂ without trees rooted on the last day = 0.108.
- Root vs non-root mean offspring 0.122 vs 0.266 (GW assumes equal).
- Root types: invented 0.99, from humans 0.000, field (unexposed) 0.006; 0.97 of non-seed first uses were visibly exposed.

## Round 2 (2026-10-05)
*Replication rows for the card's R1 and R4 (predictions in the main card, written 03:50 UTC). Role: replication; no verdict change.*

| Quantity | Value | Reference |
| --- | --- | --- |
| R1 gamma-mixed FN-GW: α̂ (CV² = 1/α), μ̂ | 0.48 [0.40, 0.67], μ̂ 0.118 | LR vs one R: 196.6 (5% point 2.71) |
| R1 tail: P(s ≥ 3), P(s ≥ 5) | 0.034, 0.0091 | Γ-FN 90% band [0.027, 0.040], [0.0052, 0.0126]: covered |
| R1 non-root / root offspring (unfitted) | 2.37 | Γ-FN band [1.99, 3.10]; one R 0.88; homogeneous skeleton ≤ 0.91 |
| R1 day-ahead log score, Γ-FN minus beta-binomial | 7.1 nats | > 0 favours Γ-FN |
| R4 semantic R̂, bge (θ 0.90) | 0.08 [0.06, 0.09], 1010 first uses | marker R̂ (1b) in the 1b line above |
| R4 semantic R̂, gte (θ 0.877) | 0.06 [0.05, 0.08], 1006 first uses | |
| R4 HR₁₀ (bge / gte) | 8.2 / 6.5 | field null 1 |
| R4 HR_unread5 / HR_seen5 (bge / gte) | 1.41 / 3.43 | copying < 1; marker median 0.56 |
