# H34 × G30: Adopt a park and get it cleaned! (2026-02-09 → 2026-02-16)

**Verdict:** mixed
**Verdict (1b):** mixed (ledger visibility: R̂ 0.34, HR₁₀ 7.0 [5.8, 8.6], tail heavy; H57 placebo HR unread/seen 3.4/6.1)
**Round 2 (2026-10-05):** replication only; the 1b verdict stands. Gamma-mixed branching α̂ 0.98 [0.82, 1.10], tail covered; semantic R̂ 0.29 (bge) / 0.24 (gte).
**Role:** replication (exploratory)
**Period:** regime I · mode C · 12 agents at start (median room size 11) · 5 non-holdout days. Setup: Adopt a park and get it cleaned: shared repo, NYC/SF 311 data, two target parks. Auto-nudger (D) starts on 2026-02-10.

## Why this period
Secondary period for the cross-period criticality link (P4) and transfer of the forecast rule (P7). Mode C (shared objective), regime I.

## Prediction
*Written 2026-10-04 02:00 UTC, before running on this period* (after the synthetic validation and amendments A1–A5 of the main card; no real cascade statistic had been computed for any period).

| # | Prediction here | Counts against |
| --- | --- | --- |
| P1 | R̂ < 1 with upper 95% CI < 1; typical 0.05–0.5 | lower CI ≥ 1 |
| P2 | R̂ < H03 n̂_talk = 0.28; R_c < R̂ | R̂ > n̂_talk beyond its CI |
| P3a (A1) | observed P(s ≥ 3) and P(s ≥ 5) inside the FN-GW 90% band (if ≥ 50 trees) | outside the band |
| P5 (A2) | contagion beyond the field: HR₁₀ > 1 with lower CI > 1 | HR₁₀ CI includes 1 or < 1 |
| P6 (A3) | pooled recency HR(2 vs 1) ≤ 2.5 (not complex) | HR(2 vs 1) > 3 with lower CI > 2.5 |

**Verdict rule (A2):** supported = P5 (HR₁₀ lower CI > 1) and P3a pass; failed = both fail, or R̂ lower CI ≥ 1; mixed = exactly one passes; n/a = fewer than 20 non-seed agent first uses (or < 50 trees for P3a, which then counts as not tested and the verdict rests on P5: supported → mixed at best).

## Result
**mixed.** 2280 ideas, 3437 agent first uses, 2357 trees, N_room 11; R̂ = 0.334, contagion share R_c = 0.271, HR₁₀ = 5.34; P(s ≥ 2) = 0.201, largest tree 11.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 R̂ < 1 (upper CI < 1) | R̂ = 0.334 [0.308, 0.358] | critical R = 1 | pass |
| P2 R̂ < H03 n̂_talk | R̂ 0.334 vs n̂ 0.28; R_c = 0.271 | HH108: R̂ > n̂ | fail |
| P3a FN-GW band covers P(s ≥ 3), P(s ≥ 5) | P(s≥3) 0.103 (band 0.101–0.137); P(s≥5) 0.036 (band 0.020–0.036) | GW-NB band covers both: no | fail (s≥5 heavier than FN-GW) |
| P3b pure s^−3/2 rejected; τ_app ≥ 2 | LR 994.1; τ_app 2.66 | critical branching | pass |
| P5 HR₁₀ > 1, lower CI > 1 (A2) | HR₁₀ = 5.34 [4.48, 6.36] (152 adoptions at k = 0) | field: HR₁₀ ≤ 1 | pass |
| P5a jitter excess (pre-registered; failed guard) | exposed 0.969 vs null 0.993, p = 1.00 | uninterpretable (S2) | n/a |
| P6 pooled HR(2 vs 1) ≤ 2.5 | 4.39 [3.55, 5.41] | complex > 3; heterogeneity inflates | ambiguous |
| P7 day-ahead 90% PI coverage (pre-registered FN-GW) | P(s≥2) 0.00, P(s≥3) 0.50 over 4 days | post-hoc V3: 0.75, 1.00 | fail |

**By idea class** (U artifact, D number, N name/coinage, W rare word):

| Class | ideas | agent nodes | R̂ [95% CI] | R_c | P(s ≥ 2) | P(s ≥ 3) | s_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D | 57 | 103 | 0.44 [0.30, 0.54] | 0.39 | 0.344 | 0.197 | 6 |
| N | 2124 | 3079 | 0.31 [0.28, 0.33] | 0.25 | 0.185 | 0.091 | 11 |
| U | 17 | 52 | 0.65 [0.36, 0.78] | 0.55 | 0.350 | 0.300 | 10 |
| W | 82 | 203 | 0.60 [0.51, 0.67] | 0.38 | 0.477 | 0.284 | 10 |

Data: `data/processed/H34-idea-cascades/G30/`. Figures: `../../figures/` (cross-period); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): HR₁₀ beats the field null (lower CI 4.48). D (unfitted shape): FN-GW band misses the tail; pure s^−3/2 rejected. E: no natural experiment inside this period was used.

## Notes
- Censoring check: R̂ without trees rooted on the last day = 0.338.
- Root vs non-root mean offspring 0.258 vs 0.437 (GW assumes equal).
- Root types: invented 0.96, from humans 0.028, field (unexposed) 0.016; 0.97 of non-seed first uses were visibly exposed.

## Round 2 (2026-10-05)
*Replication rows for the card's R1 and R4 (predictions in the main card, written 03:50 UTC). Role: replication; no verdict change.*

| Quantity | Value | Reference |
| --- | --- | --- |
| R1 gamma-mixed FN-GW: α̂ (CV² = 1/α), μ̂ | 0.98 [0.82, 1.10], μ̂ 0.267 | LR vs one R: 234.4 (5% point 2.71) |
| R1 tail: P(s ≥ 3), P(s ≥ 5) | 0.108, 0.0386 | Γ-FN 90% band [0.082, 0.108], [0.0279, 0.0450]: covered |
| R1 non-root / root offspring (unfitted) | 1.71 | Γ-FN band [1.40, 1.75]; one R 0.82; homogeneous skeleton ≤ 0.91 |
| R1 day-ahead log score, Γ-FN minus beta-binomial | -4.2 nats | > 0 favours Γ-FN |
| R4 semantic R̂, bge (θ 0.90) | 0.29 [0.27, 0.32], 1939 first uses | marker R̂ (1b) in the 1b line above |
| R4 semantic R̂, gte (θ 0.877) | 0.24 [0.22, 0.26], 1890 first uses | |
| R4 HR₁₀ (bge / gte) | 8.6 / 8.8 | field null 1 |
| R4 HR_unread5 / HR_seen5 (bge / gte) | 2.02 / 1.84 | copying < 1; marker median 0.56 |
