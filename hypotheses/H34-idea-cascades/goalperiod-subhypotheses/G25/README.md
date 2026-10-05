# H34 × G25: Create a digital museum of 2025 (2025-12-29 → 2026-01-05)

**Verdict:** mixed
**Verdict (1b):** mixed (ledger visibility: R̂ 0.22, HR₁₀ 7.9 [6.2, 10.2], tail heavy; H57 placebo HR unread/seen 3.1/6.9)
**Round 2 (2026-10-05):** replication only; the 1b verdict stands. Gamma-mixed branching α̂ 0.56 [0.49, 0.71], tail covered; semantic R̂ 0.26 (bge) / 0.33 (gte).
**Role:** replication (exploratory)
**Period:** regime I · mode C · 10 agents at start (median room size 10) · 5 non-holdout days. Setup: Create a digital museum of 2025 from village history; each agent made exhibits.

## Why this period
Secondary period for the cross-period criticality link (P4) and transfer of the forecast rule (P7). Mode C (shared objective), regime I.

## Prediction
*Written 2026-10-04 02:00 UTC, before running on this period* (after the synthetic validation and amendments A1–A5 of the main card; no real cascade statistic had been computed for any period).

| # | Prediction here | Counts against |
| --- | --- | --- |
| P1 | R̂ < 1 with upper 95% CI < 1; typical 0.05–0.5 | lower CI ≥ 1 |
| P2 | R̂ < H03 n̂_talk = 0.38; R_c < R̂ | R̂ > n̂_talk beyond its CI |
| P3a (A1) | observed P(s ≥ 3) and P(s ≥ 5) inside the FN-GW 90% band (if ≥ 50 trees) | outside the band |
| P5 (A2) | contagion beyond the field: HR₁₀ > 1 with lower CI > 1 | HR₁₀ CI includes 1 or < 1 |
| P6 (A3) | pooled recency HR(2 vs 1) ≤ 2.5 (not complex) | HR(2 vs 1) > 3 with lower CI > 2.5 |

**Verdict rule (A2):** supported = P5 (HR₁₀ lower CI > 1) and P3a pass; failed = both fail, or R̂ lower CI ≥ 1; mixed = exactly one passes; n/a = fewer than 20 non-seed agent first uses (or < 50 trees for P3a, which then counts as not tested and the verdict rests on P5: supported → mixed at best).

## Result
**mixed.** 2969 ideas, 3795 agent first uses, 3013 trees, N_room 10; R̂ = 0.206, contagion share R_c = 0.162, HR₁₀ = 4.72; P(s ≥ 2) = 0.131, largest tree 10.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 R̂ < 1 (upper CI < 1) | R̂ = 0.206 [0.186, 0.227] | critical R = 1 | pass |
| P2 R̂ < H03 n̂_talk | R̂ 0.206 vs n̂ 0.38; R_c = 0.162 | HH108: R̂ > n̂ | pass |
| P3a FN-GW band covers P(s ≥ 3), P(s ≥ 5) | P(s≥3) 0.059 (band 0.046–0.068); P(s≥5) 0.016 (band 0.005–0.012) | GW-NB band covers both: no | fail (s≥5 heavier than FN-GW) |
| P3b pure s^−3/2 rejected; τ_app ≥ 2 | LR 1905.8; τ_app 3.18 | critical branching | pass |
| P5 HR₁₀ > 1, lower CI > 1 (A2) | HR₁₀ = 4.72 [3.86, 5.75] (111 adoptions at k = 0) | field: HR₁₀ ≤ 1 | pass |
| P5a jitter excess (pre-registered; failed guard) | exposed 0.947 vs null 0.991, p = 1.00 | uninterpretable (S2) | n/a |
| P6 pooled HR(2 vs 1) ≤ 2.5 | 6.50 [5.25, 8.28] | complex > 3; heterogeneity inflates | ambiguous |
| P7 day-ahead 90% PI coverage (pre-registered FN-GW) | P(s≥2) 0.75, P(s≥3) 0.75 over 4 days | post-hoc V3: 0.75, 1.00 | fail |

**By idea class** (U artifact, D number, N name/coinage, W rare word):

| Class | ideas | agent nodes | R̂ [95% CI] | R_c | P(s ≥ 2) | P(s ≥ 3) | s_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D | 108 | 137 | 0.20 [0.09, 0.33] | 0.13 | 0.119 | 0.046 | 8 |
| N | 2739 | 3456 | 0.20 [0.18, 0.22] | 0.16 | 0.124 | 0.057 | 10 |
| U | 24 | 69 | 0.55 [0.40, 0.64] | 0.33 | 0.548 | 0.258 | 7 |
| W | 98 | 133 | 0.25 [0.16, 0.33] | 0.21 | 0.220 | 0.070 | 4 |

Data: `data/processed/H34-idea-cascades/G25/`. Figures: `../../figures/` (cross-period); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): HR₁₀ beats the field null (lower CI 3.86). D (unfitted shape): FN-GW band misses the tail; pure s^−3/2 rejected. E: no natural experiment inside this period was used.

## Notes
- Censoring check: R̂ without trees rooted on the last day = 0.209.
- Root vs non-root mean offspring 0.167 vs 0.358 (GW assumes equal).
- Root types: invented 0.99, from humans 0.000, field (unexposed) 0.015; 0.95 of non-seed first uses were visibly exposed.

## Round 2 (2026-10-05)
*Replication rows for the card's R1 and R4 (predictions in the main card, written 03:50 UTC). Role: replication; no verdict change.*

| Quantity | Value | Reference |
| --- | --- | --- |
| R1 gamma-mixed FN-GW: α̂ (CV² = 1/α), μ̂ | 0.56 [0.49, 0.71], μ̂ 0.172 | LR vs one R: 298.7 (5% point 2.71) |
| R1 tail: P(s ≥ 3), P(s ≥ 5) | 0.061, 0.0178 | Γ-FN 90% band [0.047, 0.063], [0.0134, 0.0238]: covered |
| R1 non-root / root offspring (unfitted) | 2.13 | Γ-FN band [1.91, 2.54]; one R 0.83; homogeneous skeleton ≤ 0.91 |
| R1 day-ahead log score, Γ-FN minus beta-binomial | 4.5 nats | > 0 favours Γ-FN |
| R4 semantic R̂, bge (θ 0.90) | 0.26 [0.23, 0.28], 1669 first uses | marker R̂ (1b) in the 1b line above |
| R4 semantic R̂, gte (θ 0.877) | 0.33 [0.31, 0.36], 1685 first uses | |
| R4 HR₁₀ (bge / gte) | 6.9 / 7.6 | field null 1 |
| R4 HR_unread5 / HR_seen5 (bge / gte) | 1.73 / 1.62 | copying < 1; marker median 0.56 |
