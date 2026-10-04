# H34 × G12: Form two teams and debate each other, while one agent judges. Choose your teammates wisely! (2025-09-01 → 2025-09-08)

**Verdict:** mixed
**Verdict (1b):** mixed (ledger visibility: R̂ 0.28, HR₁₀ 6.2 [4.7, 8.4], tail heavy; H57 placebo HR unread/seen 9.8/11.3)
**Role:** exploratory
**Period:** regime I · mode M · 7 agents at start (median room size 7) · 5 non-holdout days. Setup: Two teams debate (Asian Parliamentary format) while one agent judges. Teams were chosen by the agents.

## Why this period
Secondary period for the cross-period criticality link (P4) and transfer of the forecast rule (P7). Mode M (mixed (teams)), regime I.

## Prediction
*Written 2026-10-04 02:00 UTC, before running on this period* (after the synthetic validation and amendments A1–A5 of the main card; no real cascade statistic had been computed for any period).

| # | Prediction here | Counts against |
| --- | --- | --- |
| P1 | R̂ < 1 with upper 95% CI < 1; typical 0.05–0.5 | lower CI ≥ 1 |
| P2 | R̂ < H03 n̂_talk = 0.63; R_c < R̂ | R̂ > n̂_talk beyond its CI |
| P3a (A1) | observed P(s ≥ 3) and P(s ≥ 5) inside the FN-GW 90% band (if ≥ 50 trees) | outside the band |
| P5 (A2) | contagion beyond the field: HR₁₀ > 1 with lower CI > 1 | HR₁₀ CI includes 1 or < 1 |
| P6 (A3) | pooled recency HR(2 vs 1) ≤ 2.5 (not complex) | HR(2 vs 1) > 3 with lower CI > 2.5 |

**Verdict rule (A2):** supported = P5 (HR₁₀ lower CI > 1) and P3a pass; failed = both fail, or R̂ lower CI ≥ 1; mixed = exactly one passes; n/a = fewer than 20 non-seed agent first uses (or < 50 trees for P3a, which then counts as not tested and the verdict rests on P5: supported → mixed at best).

## Result
**mixed.** 934 ideas, 1331 agent first uses, 1024 trees, N_room 7; R̂ = 0.231, contagion share R_c = 0.101, HR₁₀ = 1.78; P(s ≥ 2) = 0.172, largest tree 7.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 R̂ < 1 (upper CI < 1) | R̂ = 0.231 [0.201, 0.260] | critical R = 1 | pass |
| P2 R̂ < H03 n̂_talk | R̂ 0.231 vs n̂ 0.63; R_c = 0.101 | HH108: R̂ > n̂ | pass |
| P3a FN-GW band covers P(s ≥ 3), P(s ≥ 5) | P(s≥3) 0.067 (band 0.048–0.082); P(s≥5) 0.018 (band 0.003–0.016) | GW-NB band covers both: no | fail (s≥5 heavier than FN-GW) |
| P3b pure s^−3/2 rejected; τ_app ≥ 2 | LR 439.3; τ_app 2.90 | critical branching | pass |
| P5 HR₁₀ > 1, lower CI > 1 (A2) | HR₁₀ = 1.78 [1.42, 2.23] (133 adoptions at k = 0) | field: HR₁₀ ≤ 1 | pass |
| P5a jitter excess (pre-registered; failed guard) | exposed 0.777 vs null 0.978, p = 1.00 | uninterpretable (S2) | n/a |
| P6 pooled HR(2 vs 1) ≤ 2.5 | 4.06 [2.72, 5.78] | complex > 3; heterogeneity inflates | ambiguous |
| P7 day-ahead 90% PI coverage (pre-registered FN-GW) | P(s≥2) 0.00, P(s≥3) 0.50 over 4 days | post-hoc V3: 0.50, 0.50 | fail |

**By idea class** (U artifact, D number, N name/coinage, W rare word):

| Class | ideas | agent nodes | R̂ [95% CI] | R_c | P(s ≥ 2) | P(s ≥ 3) | s_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D | 57 | 63 | 0.08 [0.00, 0.20] | 0.02 | 0.034 | 0.017 | 5 |
| N | 737 | 1032 | 0.22 [0.19, 0.25] | 0.09 | 0.164 | 0.063 | 7 |
| U | 24 | 37 | 0.35 [0.17, 0.48] | 0.35 | 0.333 | 0.167 | 4 |
| W | 116 | 199 | 0.31 [0.22, 0.38] | 0.12 | 0.246 | 0.094 | 7 |

Data: `data/processed/H34-idea-cascades/G12/`. Figures: `../../figures/` (cross-period); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): HR₁₀ beats the field null (lower CI 1.42). D (unfitted shape): FN-GW band misses the tail; pure s^−3/2 rejected. E: no natural experiment inside this period was used.

## Notes
- Censoring check: R̂ without trees rooted on the last day = 0.240.
- Root vs non-root mean offspring 0.205 vs 0.316 (GW assumes equal).
- Root types: invented 0.91, from humans 0.004, field (unexposed) 0.087; 0.78 of non-seed first uses were visibly exposed.
