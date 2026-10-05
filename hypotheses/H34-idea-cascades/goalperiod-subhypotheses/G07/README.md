# H34 × G07: Holiday: do whatever you prefer! Next goal will begin soon (2025-07-16 → 2025-07-18)

**Verdict:** mixed
**Verdict (1b):** supported (ledger visibility: R̂ 0.10, HR₁₀ 16.1 [4.6, 102.0], tail ok; H57 placebo HR unread/seen 1.4/4.3)
**Round 2 (2026-10-05):** replication only; the 1b verdict stands. Gamma-mixed branching α̂ 1.39 [0.40, 500.00], tail covered; semantic R̂ 0.05 (bge) / 0.03 (gte).
**Role:** replication (exploratory)
**Period:** regime I · mode F · 4 agents at start (median room size 4) · 2 non-holdout days. Setup: Two-day holiday; competition results were reviewed and the agents found they had misread the store interface.

## Why this period
Secondary period for the cross-period criticality link (P4) and transfer of the forecast rule (P7). Mode F (free / pick your own), regime I.

## Prediction
*Written 2026-10-04 02:00 UTC, before running on this period* (after the synthetic validation and amendments A1–A5 of the main card; no real cascade statistic had been computed for any period).

| # | Prediction here | Counts against |
| --- | --- | --- |
| P1 | R̂ < 1 with upper 95% CI < 1; typical 0.05–0.5 | lower CI ≥ 1 |
| P2 | R̂ < H03 n̂_talk = 0.47; R_c < R̂ | R̂ > n̂_talk beyond its CI |
| P3a (A1) | observed P(s ≥ 3) and P(s ≥ 5) inside the FN-GW 90% band (if ≥ 50 trees) | outside the band |
| P5 (A2) | contagion beyond the field: HR₁₀ > 1 with lower CI > 1 | HR₁₀ CI includes 1 or < 1 |
| P6 (A3) | pooled recency HR(2 vs 1) ≤ 2.5 (not complex) | HR(2 vs 1) > 3 with lower CI > 2.5 |

**Verdict rule (A2):** supported = P5 (HR₁₀ lower CI > 1) and P3a pass; failed = both fail, or R̂ lower CI ≥ 1; mixed = exactly one passes; n/a = fewer than 20 non-seed agent first uses (or < 50 trees for P3a, which then counts as not tested and the verdict rests on P5: supported → mixed at best).

## Result
**mixed.** 184 ideas, 207 agent first uses, 194 trees, N_room 4; R̂ = 0.063, contagion share R_c = 0.026, HR₁₀ = 1.69; P(s ≥ 2) = 0.062, largest tree 3.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 R̂ < 1 (upper CI < 1) | R̂ = 0.063 [0.030, 0.097] | critical R = 1 | pass |
| P2 R̂ < H03 n̂_talk | R̂ 0.063 vs n̂ 0.47; R_c = 0.026 | HH108: R̂ > n̂ | pass |
| P3a FN-GW band covers P(s ≥ 3), P(s ≥ 5) | P(s≥3) 0.005 (band 0.000–0.015); P(s≥5) 0.000 (band 0.000–0.000) | GW-NB band covers both: yes | pass |
| P3b pure s^−3/2 rejected; τ_app ≥ 2 | LR 128.3; τ_app 4.32 | critical branching | pass |
| P5 HR₁₀ > 1, lower CI > 1 (A2) | HR₁₀ = 1.69 [0.72, 4.06] (11 adoptions at k = 0) | field: HR₁₀ ≤ 1 | fail |
| P5a jitter excess (pre-registered; failed guard) | exposed 0.560 vs null 0.964, p = 1.00 | uninterpretable (S2) | n/a |
| P6 pooled HR(2 vs 1) ≤ 2.5 | 13.10 [0.00, 38.59] | complex > 3; heterogeneity inflates | ambiguous |
| P7 day-ahead 90% PI coverage (pre-registered FN-GW) | P(s≥2) 1.00, P(s≥3) 1.00 over 1 days | post-hoc V3: 1.00, 1.00 | pass |

**By idea class** (U artifact, D number, N name/coinage, W rare word):

| Class | ideas | agent nodes | R̂ [95% CI] | R_c | P(s ≥ 2) | P(s ≥ 3) | s_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D | 25 | 28 | 0.11 [0.00, 0.22] | 0.11 | 0.120 | 0.000 | 2 |
| N | 123 | 137 | 0.07 [0.03, 0.12] | 0.03 | 0.062 | 0.008 | 3 |
| U | 0 | 0 | – [–, –] | – | – | – | None |
| W | 36 | 42 | 0.02 [0.00, 0.08] | 0.00 | 0.024 | 0.000 | 2 |

Data: `data/processed/H34-idea-cascades/G07/`. Figures: `../../figures/` (cross-period); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): HR₁₀ does not beat the field null (lower CI 0.72). D (unfitted shape): FN-GW band covers the tail; pure s^−3/2 rejected. E: no natural experiment inside this period was used.

## Notes
- Median room size 4: trees cannot exceed 3 agents, so P(s ≥ 5) = 0 and the shape test is uninformative here.
- Censoring check: R̂ without trees rooted on the last day = 0.051.
- Root vs non-root mean offspring 0.062 vs 0.077 (GW assumes equal).
- Root types: invented 0.94, from humans 0.005, field (unexposed) 0.057; 0.56 of non-seed first uses were visibly exposed.

## Round 2 (2026-10-05)
*Replication rows for the card's R1 and R4 (predictions in the main card, written 03:50 UTC). Role: replication; no verdict change.*

| Quantity | Value | Reference |
| --- | --- | --- |
| R1 gamma-mixed FN-GW: α̂ (CV² = 1/α), μ̂ | 1.39 [0.40, 500.00], μ̂ 0.102 | LR vs one R: 0.7 (5% point 2.71) |
| R1 tail: P(s ≥ 3), P(s ≥ 5) | 0.022, 0.0000 | Γ-FN 90% band [0.000, 0.038], [0.0000, 0.0000]: covered |
| R1 non-root / root offspring (unfitted) | 1.48 | Γ-FN band [0.00, 2.58]; one R 0.42; homogeneous skeleton ≤ 0.91 |
| R1 day-ahead log score, Γ-FN minus beta-binomial | 0.2 nats | > 0 favours Γ-FN |
| R4 semantic R̂, bge (θ 0.90) | 0.05 [0.03, 0.08], 254 first uses | marker R̂ (1b) in the 1b line above |
| R4 semantic R̂, gte (θ 0.877) | 0.03 [0.01, 0.05], 266 first uses | |
| R4 HR₁₀ (bge / gte) | n/a / n/a | field null 1 |
| R4 HR_unread5 / HR_seen5 (bge / gte) | 0.00 / 0.00 | copying < 1; marker median 0.56 |
