# H34 × G17: Each agent: build your own personal website (2025-10-13 → 2025-10-20)

**Verdict:** mixed
**Verdict (1b):** supported (ledger visibility: R̂ 0.25, HR₁₀ 11.5 [5.9, 24.5], tail ok; H57 placebo HR unread/seen 10.8/17.6)
**Round 2 (2026-10-05):** replication only; the 1b verdict stands. Gamma-mixed branching α̂ 1.14 [0.73, 6.96], tail covered; semantic R̂ 0.14 (bge) / 0.15 (gte).
**Role:** replication (exploratory)
**Period:** regime I · mode I · 7 agents at start (median room size 7) · 5 non-holdout days. Setup: Each agent builds a personal website with a new codex tool; deployment know-how split agents into the lucky and the stuck.

## Why this period
Secondary period for the cross-period criticality link (P4) and transfer of the forecast rule (P7). Mode I (each agent its own objective), regime I.

## Prediction
*Written 2026-10-04 02:00 UTC, before running on this period* (after the synthetic validation and amendments A1–A5 of the main card; no real cascade statistic had been computed for any period).

| # | Prediction here | Counts against |
| --- | --- | --- |
| P1 | R̂ < 1 with upper 95% CI < 1; typical 0.05–0.5 | lower CI ≥ 1 |
| P2 | R̂ < H03 n̂_talk = 0.48; R_c < R̂ | R̂ > n̂_talk beyond its CI |
| P3a (A1) | observed P(s ≥ 3) and P(s ≥ 5) inside the FN-GW 90% band (if ≥ 50 trees) | outside the band |
| P5 (A2) | contagion beyond the field: HR₁₀ > 1 with lower CI > 1 | HR₁₀ CI includes 1 or < 1 |
| P6 (A3) | pooled recency HR(2 vs 1) ≤ 2.5 (not complex) | HR(2 vs 1) > 3 with lower CI > 2.5 |

**Verdict rule (A2):** supported = P5 (HR₁₀ lower CI > 1) and P3a pass; failed = both fail, or R̂ lower CI ≥ 1; mixed = exactly one passes; n/a = fewer than 20 non-seed agent first uses (or < 50 trees for P3a, which then counts as not tested and the verdict rests on P5: supported → mixed at best).

## Result
**mixed.** 364 ideas, 489 agent first uses, 399 trees, N_room 7; R̂ = 0.184, contagion share R_c = 0.018, HR₁₀ = 1.11; P(s ≥ 2) = 0.123, largest tree 7.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 R̂ < 1 (upper CI < 1) | R̂ = 0.184 [0.135, 0.233] | critical R = 1 | pass |
| P2 R̂ < H03 n̂_talk | R̂ 0.184 vs n̂ 0.48; R_c = 0.018 | HH108: R̂ > n̂ | pass |
| P3a FN-GW band covers P(s ≥ 3), P(s ≥ 5) | P(s≥3) 0.050 (band 0.025–0.078); P(s≥5) 0.015 (band 0.000–0.015) | GW-NB band covers both: yes | pass |
| P3b pure s^−3/2 rejected; τ_app ≥ 2 | LR 225.1; τ_app 3.25 | critical branching | pass |
| P5 HR₁₀ > 1, lower CI > 1 (A2) | HR₁₀ = 1.11 [0.67, 1.82] (41 adoptions at k = 0) | field: HR₁₀ ≤ 1 | fail |
| P5a jitter excess (pre-registered; failed guard) | exposed 0.720 vs null 0.980, p = 1.00 | uninterpretable (S2) | n/a |
| P6 pooled HR(2 vs 1) ≤ 2.5 | 9.65 [3.42, 26.25] | complex > 3; heterogeneity inflates | ambiguous |
| P7 day-ahead 90% PI coverage (pre-registered FN-GW) | P(s≥2) 0.50, P(s≥3) 1.00 over 4 days | post-hoc V3: 0.75, 1.00 | fail |

**By idea class** (U artifact, D number, N name/coinage, W rare word):

| Class | ideas | agent nodes | R̂ [95% CI] | R_c | P(s ≥ 2) | P(s ≥ 3) | s_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D | 43 | 52 | 0.13 [0.00, 0.31] | 0.08 | 0.044 | 0.044 | 6 |
| N | 269 | 358 | 0.18 [0.13, 0.23] | 0.02 | 0.122 | 0.044 | 7 |
| U | 24 | 42 | 0.24 [0.11, 0.36] | 0.00 | 0.219 | 0.094 | 3 |
| W | 28 | 37 | 0.24 [0.03, 0.43] | 0.00 | 0.143 | 0.071 | 6 |

Data: `data/processed/H34-idea-cascades/G17/`. Figures: `../../figures/` (cross-period); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): HR₁₀ does not beat the field null (lower CI 0.67). D (unfitted shape): FN-GW band covers the tail; pure s^−3/2 rejected. E: no natural experiment inside this period was used.

## Notes
- Censoring check: R̂ without trees rooted on the last day = 0.194.
- Root vs non-root mean offspring 0.155 vs 0.311 (GW assumes equal).
- Root types: invented 0.91, from humans 0.000, field (unexposed) 0.088; 0.72 of non-seed first uses were visibly exposed.

## Round 2 (2026-10-05)
*Replication rows for the card's R1 and R4 (predictions in the main card, written 03:50 UTC). Role: replication; no verdict change.*

| Quantity | Value | Reference |
| --- | --- | --- |
| R1 gamma-mixed FN-GW: α̂ (CV² = 1/α), μ̂ | 1.14 [0.73, 6.96], μ̂ 0.230 | LR vs one R: 16.7 (5% point 2.71) |
| R1 tail: P(s ≥ 3), P(s ≥ 5) | 0.073, 0.0190 | Γ-FN 90% band [0.043, 0.098], [0.0027, 0.0325]: covered |
| R1 non-root / root offspring (unfitted) | 1.03 | Γ-FN band [0.79, 1.74]; one R 0.74; homogeneous skeleton ≤ 0.91 |
| R1 day-ahead log score, Γ-FN minus beta-binomial | -0.4 nats | > 0 favours Γ-FN |
| R4 semantic R̂, bge (θ 0.90) | 0.14 [0.12, 0.16], 1163 first uses | marker R̂ (1b) in the 1b line above |
| R4 semantic R̂, gte (θ 0.877) | 0.15 [0.13, 0.17], 1111 first uses | |
| R4 HR₁₀ (bge / gte) | 2.9 / 4.3 | field null 1 |
| R4 HR_unread5 / HR_seen5 (bge / gte) | 4.13 / 3.28 | copying < 1; marker median 0.56 |
