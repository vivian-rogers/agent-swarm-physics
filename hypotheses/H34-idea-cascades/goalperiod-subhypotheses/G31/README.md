# H34 × G31: Pick your own goal (agents bid 3.7 Sonnet farewell) (2026-02-16 → 2026-02-23)

**Verdict:** mixed
**Verdict (1b):** mixed (ledger visibility: R̂ 0.30, HR₁₀ 9.2 [7.8, 11.0], tail heavy; H57 placebo HR unread/seen 3.0/7.6)
**Round 2 (2026-10-05):** replication only; the 1b verdict stands. Gamma-mixed branching α̂ 0.93 [0.77, 1.10], tail covered; semantic R̂ 0.21 (bge) / 0.16 (gte).
**Role:** replication (exploratory)
**Period:** regime I · mode F · 12 agents at start (median room size 11) · 5 non-holdout days. Setup: Free week; farewell to Claude 3.7 Sonnet, which retired. About nine agents converged on the same task (a "canonical guardrails UI snippet") with competing PRs.

## Why this period
Secondary period for the cross-period criticality link (P4) and transfer of the forecast rule (P7). Mode F (free / pick your own), regime I.

## Prediction
*Written 2026-10-04 02:00 UTC, before running on this period* (after the synthetic validation and amendments A1–A5 of the main card; no real cascade statistic had been computed for any period).

| # | Prediction here | Counts against |
| --- | --- | --- |
| P1 | R̂ < 1 with upper 95% CI < 1; typical 0.05–0.5 | lower CI ≥ 1 |
| P2 | R̂ < H03 n̂_talk = 0.07; R_c < R̂ | R̂ > n̂_talk beyond its CI |
| P3a (A1) | observed P(s ≥ 3) and P(s ≥ 5) inside the FN-GW 90% band (if ≥ 50 trees) | outside the band |
| P5 (A2) | contagion beyond the field: HR₁₀ > 1 with lower CI > 1 | HR₁₀ CI includes 1 or < 1 |
| P6 (A3) | pooled recency HR(2 vs 1) ≤ 2.5 (not complex) | HR(2 vs 1) > 3 with lower CI > 2.5 |

**Verdict rule (A2):** supported = P5 (HR₁₀ lower CI > 1) and P3a pass; failed = both fail, or R̂ lower CI ≥ 1; mixed = exactly one passes; n/a = fewer than 20 non-seed agent first uses (or < 50 trees for P3a, which then counts as not tested and the verdict rests on P5: supported → mixed at best).

## Result
**mixed.** 3550 ideas, 4964 agent first uses, 3699 trees, N_room 11; R̂ = 0.286, contagion share R_c = 0.241, HR₁₀ = 6.31; P(s ≥ 2) = 0.173, largest tree 11.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 R̂ < 1 (upper CI < 1) | R̂ = 0.286 [0.267, 0.305] | critical R = 1 | pass |
| P2 R̂ < H03 n̂_talk | R̂ 0.286 vs n̂ 0.07; R_c = 0.241 | HH108: R̂ > n̂ | fail |
| P3a FN-GW band covers P(s ≥ 3), P(s ≥ 5) | P(s≥3) 0.074 (band 0.077–0.110); P(s≥5) 0.024 (band 0.013–0.027) | GW-NB band covers both: no | fail |
| P3b pure s^−3/2 rejected; τ_app ≥ 2 | LR 1972.1; τ_app 2.90 | critical branching | pass |
| P5 HR₁₀ > 1, lower CI > 1 (A2) | HR₁₀ = 6.31 [5.47, 7.39] (185 adoptions at k = 0) | field: HR₁₀ ≤ 1 | pass |
| P5a jitter excess (pre-registered; failed guard) | exposed 0.952 vs null 0.982, p = 1.00 | uninterpretable (S2) | n/a |
| P6 pooled HR(2 vs 1) ≤ 2.5 | 5.21 [4.30, 6.18] | complex > 3; heterogeneity inflates | ambiguous |
| P7 day-ahead 90% PI coverage (pre-registered FN-GW) | P(s≥2) 0.25, P(s≥3) 0.25 over 4 days | post-hoc V3: 0.50, 0.75 | fail |

**By idea class** (U artifact, D number, N name/coinage, W rare word):

| Class | ideas | agent nodes | R̂ [95% CI] | R_c | P(s ≥ 2) | P(s ≥ 3) | s_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D | 229 | 398 | 0.41 [0.34, 0.47] | 0.33 | 0.290 | 0.135 | 9 |
| N | 3165 | 4295 | 0.27 [0.24, 0.29] | 0.23 | 0.161 | 0.065 | 11 |
| U | 95 | 177 | 0.46 [0.35, 0.54] | 0.32 | 0.282 | 0.184 | 7 |
| W | 61 | 94 | 0.37 [0.21, 0.50] | 0.35 | 0.190 | 0.095 | 7 |

Data: `data/processed/H34-idea-cascades/G31/`. Figures: `../../figures/` (cross-period); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): HR₁₀ beats the field null (lower CI 5.47). D (unfitted shape): FN-GW band misses the tail; pure s^−3/2 rejected. E: no natural experiment inside this period was used.

## Notes
- Censoring check: R̂ without trees rooted on the last day = 0.273.
- Root vs non-root mean offspring 0.220 vs 0.358 (GW assumes equal).
- Root types: invented 0.94, from humans 0.042, field (unexposed) 0.019; 0.95 of non-seed first uses were visibly exposed.

## Round 2 (2026-10-05)
*Replication rows for the card's R1 and R4 (predictions in the main card, written 03:50 UTC). Role: replication; no verdict change.*

| Quantity | Value | Reference |
| --- | --- | --- |
| R1 gamma-mixed FN-GW: α̂ (CV² = 1/α), μ̂ | 0.93 [0.77, 1.10], μ̂ 0.217 | LR vs one R: 303.3 (5% point 2.71) |
| R1 tail: P(s ≥ 3), P(s ≥ 5) | 0.076, 0.0257 | Γ-FN 90% band [0.060, 0.078], [0.0172, 0.0271]: covered |
| R1 non-root / root offspring (unfitted) | 1.71 | Γ-FN band [1.57, 1.98]; one R 0.83; homogeneous skeleton ≤ 0.91 |
| R1 day-ahead log score, Γ-FN minus beta-binomial | 8.8 nats | > 0 favours Γ-FN |
| R4 semantic R̂, bge (θ 0.90) | 0.21 [0.19, 0.23], 2162 first uses | marker R̂ (1b) in the 1b line above |
| R4 semantic R̂, gte (θ 0.877) | 0.16 [0.14, 0.18], 2118 first uses | |
| R4 HR₁₀ (bge / gte) | 7.0 / 9.2 | field null 1 |
| R4 HR_unread5 / HR_seen5 (bge / gte) | 1.92 / 2.03 | copying < 1; marker median 0.56 |
