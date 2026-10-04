# H34 × G16: Choose your own goal! (2025-10-06 → 2025-10-13)

**Verdict:** failed
**Role:** exploratory
**Period:** regime I · mode F · 7 agents at start (median room size 7) · 5 non-holdout days. Setup: Free week with operator rules: no more spreadsheets, stop reporting self-caused bugs.

## Why this period
Secondary period for the cross-period criticality link (P4) and transfer of the forecast rule (P7). Mode F (free / pick your own), regime I.

## Prediction
*Written 2026-10-04 02:00 UTC, before running on this period* (after the synthetic validation and amendments A1–A5 of the main card; no real cascade statistic had been computed for any period).

| # | Prediction here | Counts against |
| --- | --- | --- |
| P1 | R̂ < 1 with upper 95% CI < 1; typical 0.05–0.5 | lower CI ≥ 1 |
| P2 | R̂ < H03 n̂_talk = 0.59; R_c < R̂ | R̂ > n̂_talk beyond its CI |
| P3a (A1) | observed P(s ≥ 3) and P(s ≥ 5) inside the FN-GW 90% band (if ≥ 50 trees) | outside the band |
| P5 (A2) | contagion beyond the field: HR₁₀ > 1 with lower CI > 1 | HR₁₀ CI includes 1 or < 1 |
| P6 (A3) | pooled recency HR(2 vs 1) ≤ 2.5 (not complex) | HR(2 vs 1) > 3 with lower CI > 2.5 |

**Verdict rule (A2):** supported = P5 (HR₁₀ lower CI > 1) and P3a pass; failed = both fail, or R̂ lower CI ≥ 1; mixed = exactly one passes; n/a = fewer than 20 non-seed agent first uses (or < 50 trees for P3a, which then counts as not tested and the verdict rests on P5: supported → mixed at best).

## Result
**failed.** 947 ideas, 1059 agent first uses, 967 trees, N_room 7; R̂ = 0.087, contagion share R_c = 0.000, HR₁₀ = 0.92; P(s ≥ 2) = 0.062, largest tree 7.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 R̂ < 1 (upper CI < 1) | R̂ = 0.087 [0.063, 0.113] | critical R = 1 | pass |
| P2 R̂ < H03 n̂_talk | R̂ 0.087 vs n̂ 0.59; R_c = 0.000 | HH108: R̂ > n̂ | pass |
| P3a FN-GW band covers P(s ≥ 3), P(s ≥ 5) | P(s≥3) 0.018 (band 0.009–0.027); P(s≥5) 0.005 (band 0.000–0.004) | GW-NB band covers both: no | fail (s≥5 heavier than FN-GW) |
| P3b pure s^−3/2 rejected; τ_app ≥ 2 | LR 813.7; τ_app 4.17 | critical branching | pass |
| P5 HR₁₀ > 1, lower CI > 1 (A2) | HR₁₀ = 0.92 [0.56, 1.49] (38 adoptions at k = 0) | field: HR₁₀ ≤ 1 | fail |
| P5a jitter excess (pre-registered; failed guard) | exposed 0.821 vs null 0.973, p = 1.00 | uninterpretable (S2) | n/a |
| P6 pooled HR(2 vs 1) ≤ 2.5 | 11.73 [3.46, 25.65] | complex > 3; heterogeneity inflates | ambiguous |
| P7 day-ahead 90% PI coverage (pre-registered FN-GW) | P(s≥2) 0.50, P(s≥3) 0.25 over 4 days | post-hoc V3: 0.25, 0.00 | fail |

**By idea class** (U artifact, D number, N name/coinage, W rare word):

| Class | ideas | agent nodes | R̂ [95% CI] | R_c | P(s ≥ 2) | P(s ≥ 3) | s_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D | 68 | 89 | 0.22 [0.07, 0.37] | 0.19 | 0.130 | 0.043 | 7 |
| N | 816 | 897 | 0.07 [0.05, 0.10] | 0.00 | 0.054 | 0.016 | 6 |
| U | 8 | 11 | 0.27 [0.11, 0.43] | 0.27 | 0.375 | 0.000 | 2 |
| W | 55 | 62 | 0.06 [0.00, 0.14] | 0.03 | 0.052 | 0.017 | 3 |

Data: `data/processed/H34-idea-cascades/G16/`. Figures: `../../figures/` (cross-period); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): HR₁₀ does not beat the field null (lower CI 0.56). D (unfitted shape): FN-GW band misses the tail; pure s^−3/2 rejected. E: no natural experiment inside this period was used.

## Notes
- Censoring check: R̂ without trees rooted on the last day = 0.097.
- Root vs non-root mean offspring 0.080 vs 0.163 (GW assumes equal).
- Root types: invented 0.98, from humans 0.000, field (unexposed) 0.021; 0.82 of non-seed first uses were visibly exposed.
