# H34 × G06: Create your own merch store. Whichever agent's store makes the most profit wins! (2025-06-26 → 2025-07-16)

**Verdict:** supported
**Verdict (1b):** supported (ledger visibility: R̂ 0.11, HR₁₀ 5.6 [3.2, 10.2], tail ok; H57 placebo HR unread/seen 2.2/3.6)
**Round 2 (2026-10-05):** replication only; the 1b verdict stands. Gamma-mixed branching α̂ 0.94 [0.53, 3.91], tail covered; semantic R̂ 0.02 (bge) / 0.01 (gte).
**Role:** replication (exploratory)
**Period:** regime I · mode K · 4 agents at start (median room size 4) · 15 non-holdout days. Setup: First competition: each agent builds its own merch store; most profit wins. Claude Opus 4 won ($126 from 24 orders), ahead of Sonnet ($68), o3 ($39) and Gemini ($22).

## Why this period
Secondary period for the cross-period criticality link (P4) and transfer of the forecast rule (P7). Mode K (competitive), regime I.

## Prediction
*Written 2026-10-04 02:00 UTC, before running on this period* (after the synthetic validation and amendments A1–A5 of the main card; no real cascade statistic had been computed for any period).

| # | Prediction here | Counts against |
| --- | --- | --- |
| P1 | R̂ < 1 with upper 95% CI < 1; typical 0.05–0.5 | lower CI ≥ 1 |
| P2 | R̂ < H03 n̂_talk = 0.65; R_c < R̂ | R̂ > n̂_talk beyond its CI |
| P3a (A1) | observed P(s ≥ 3) and P(s ≥ 5) inside the FN-GW 90% band (if ≥ 50 trees) | outside the band |
| P5 (A2) | contagion beyond the field: HR₁₀ > 1 with lower CI > 1 | HR₁₀ CI includes 1 or < 1 |
| P6 (A3) | pooled recency HR(2 vs 1) ≤ 2.5 (not complex) | HR(2 vs 1) > 3 with lower CI > 2.5 |

**Verdict rule (A2):** supported = P5 (HR₁₀ lower CI > 1) and P3a pass; failed = both fail, or R̂ lower CI ≥ 1; mixed = exactly one passes; n/a = fewer than 20 non-seed agent first uses (or < 50 trees for P3a, which then counts as not tested and the verdict rests on P5: supported → mixed at best).

## Result
**supported.** 1159 ideas, 1307 agent first uses, 1171 trees, N_room 4; R̂ = 0.104, contagion share R_c = 0.055, HR₁₀ = 2.14; P(s ≥ 2) = 0.096, largest tree 4.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 R̂ < 1 (upper CI < 1) | R̂ = 0.104 [0.084, 0.122] | critical R = 1 | pass |
| P2 R̂ < H03 n̂_talk | R̂ 0.104 vs n̂ 0.65; R_c = 0.055 | HH108: R̂ > n̂ | pass |
| P3a FN-GW band covers P(s ≥ 3), P(s ≥ 5) | P(s≥3) 0.014 (band 0.007–0.021); P(s≥5) 0.000 (band 0.000–0.000) | GW-NB band covers both: yes | pass |
| P3b pure s^−3/2 rejected; τ_app ≥ 2 | LR 600.4; τ_app 3.69 | critical branching | pass |
| P5 HR₁₀ > 1, lower CI > 1 (A2) | HR₁₀ = 2.14 [1.35, 3.40] (30 adoptions at k = 0) | field: HR₁₀ ≤ 1 | pass |
| P5a jitter excess (pre-registered; failed guard) | exposed 0.921 vs null 0.971, p = 1.00 | uninterpretable (S2) | n/a |
| P6 pooled HR(2 vs 1) ≤ 2.5 | 3.80 [0.90, 7.86] | complex > 3; heterogeneity inflates | ambiguous |
| P7 day-ahead 90% PI coverage (pre-registered FN-GW) | P(s≥2) 0.93, P(s≥3) 0.93 over 14 days | post-hoc V3: 0.93, 1.00 | pass |

**By idea class** (U artifact, D number, N name/coinage, W rare word):

| Class | ideas | agent nodes | R̂ [95% CI] | R_c | P(s ≥ 2) | P(s ≥ 3) | s_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D | 87 | 107 | 0.17 [0.10, 0.25] | 0.11 | 0.169 | 0.022 | 4 |
| N | 984 | 1083 | 0.08 [0.07, 0.10] | 0.05 | 0.077 | 0.008 | 4 |
| U | 6 | 7 | 0.14 [0.00, 0.33] | 0.14 | 0.167 | 0.000 | 2 |
| W | 82 | 110 | 0.25 [0.16, 0.34] | 0.02 | 0.232 | 0.073 | 4 |

Data: `data/processed/H34-idea-cascades/G06/`. Figures: `../../figures/` (cross-period); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): HR₁₀ beats the field null (lower CI 1.35). D (unfitted shape): FN-GW band covers the tail; pure s^−3/2 rejected. E: no natural experiment inside this period was used.

## Notes
- Median room size 4: trees cannot exceed 4 agents, so P(s ≥ 5) = 0 and the shape test is uninformative here.
- Censoring check: R̂ without trees rooted on the last day = 0.104.
- Root vs non-root mean offspring 0.103 vs 0.110 (GW assumes equal).
- Root types: invented 0.98, from humans 0.014, field (unexposed) 0.011; 0.92 of non-seed first uses were visibly exposed.

## Round 2 (2026-10-05)
*Replication rows for the card's R1 and R4 (predictions in the main card, written 03:50 UTC). Role: replication; no verdict change.*

| Quantity | Value | Reference |
| --- | --- | --- |
| R1 gamma-mixed FN-GW: α̂ (CV² = 1/α), μ̂ | 0.94 [0.53, 3.91], μ̂ 0.111 | LR vs one R: 12.4 (5% point 2.71) |
| R1 tail: P(s ≥ 3), P(s ≥ 5) | 0.018, 0.0000 | Γ-FN 90% band [0.012, 0.034], [0.0000, 0.0000]: covered |
| R1 non-root / root offspring (unfitted) | 1.26 | Γ-FN band [0.60, 1.64]; one R 0.59; homogeneous skeleton ≤ 0.91 |
| R1 day-ahead log score, Γ-FN minus beta-binomial | 2.1 nats | > 0 favours Γ-FN |
| R4 semantic R̂, bge (θ 0.90) | 0.02 [0.02, 0.03], 1358 first uses | marker R̂ (1b) in the 1b line above |
| R4 semantic R̂, gte (θ 0.877) | 0.01 [0.01, 0.02], 1415 first uses | |
| R4 HR₁₀ (bge / gte) | 3.2 / 4.4 | field null 1 |
| R4 HR_unread5 / HR_seen5 (bge / gte) | 2.05 / 3.21 | copying < 1; marker median 0.56 |
