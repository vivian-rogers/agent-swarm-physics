# H34 × G21: Forecast the abilities and effects of AI (2025-12-01 → 2025-12-08)

**Verdict:** mixed
**Role:** exploratory
**Period:** regime I · mode I · 8 agents at start (median room size 8) · 5 non-holdout days. Setup: Forecast AI abilities and effects. Agents deliberately drafted independent predictions first, then compared.

## Why this period
Secondary period for the cross-period criticality link (P4) and transfer of the forecast rule (P7). Mode I (each agent its own objective), regime I.

## Prediction
*Written 2026-10-04 02:00 UTC, before running on this period* (after the synthetic validation and amendments A1–A5 of the main card; no real cascade statistic had been computed for any period).

| # | Prediction here | Counts against |
| --- | --- | --- |
| P1 | R̂ < 1 with upper 95% CI < 1; typical 0.05–0.5 | lower CI ≥ 1 |
| P2 | R̂ < H03 n̂_talk = 0.68; R_c < R̂ | R̂ > n̂_talk beyond its CI |
| P3a (A1) | observed P(s ≥ 3) and P(s ≥ 5) inside the FN-GW 90% band (if ≥ 50 trees) | outside the band |
| P5 (A2) | contagion beyond the field: HR₁₀ > 1 with lower CI > 1 | HR₁₀ CI includes 1 or < 1 |
| P6 (A3) | pooled recency HR(2 vs 1) ≤ 2.5 (not complex) | HR(2 vs 1) > 3 with lower CI > 2.5 |

**Verdict rule (A2):** supported = P5 (HR₁₀ lower CI > 1) and P3a pass; failed = both fail, or R̂ lower CI ≥ 1; mixed = exactly one passes; n/a = fewer than 20 non-seed agent first uses (or < 50 trees for P3a, which then counts as not tested and the verdict rests on P5: supported → mixed at best).

## Result
**mixed.** 1887 ideas, 2434 agent first uses, 1968 trees, N_room 8; R̂ = 0.191, contagion share R_c = 0.091, HR₁₀ = 1.91; P(s ≥ 2) = 0.123, largest tree 9.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 R̂ < 1 (upper CI < 1) | R̂ = 0.191 [0.168, 0.216] | critical R = 1 | pass |
| P2 R̂ < H03 n̂_talk | R̂ 0.191 vs n̂ 0.68; R_c = 0.091 | HH108: R̂ > n̂ | pass |
| P3a FN-GW band covers P(s ≥ 3), P(s ≥ 5) | P(s≥3) 0.050 (band 0.035–0.061); P(s≥5) 0.017 (band 0.003–0.010) | GW-NB band covers both: no | fail (s≥5 heavier than FN-GW) |
| P3b pure s^−3/2 rejected; τ_app ≥ 2 | LR 1259.6; τ_app 3.27 | critical branching | pass |
| P5 HR₁₀ > 1, lower CI > 1 (A2) | HR₁₀ = 1.91 [1.53, 2.34] (144 adoptions at k = 0) | field: HR₁₀ ≤ 1 | pass |
| P5a jitter excess (pre-registered; failed guard) | exposed 0.852 vs null 0.964, p = 1.00 | uninterpretable (S2) | n/a |
| P6 pooled HR(2 vs 1) ≤ 2.5 | 5.98 [3.99, 8.20] | complex > 3; heterogeneity inflates | ambiguous |
| P7 day-ahead 90% PI coverage (pre-registered FN-GW) | P(s≥2) 0.00, P(s≥3) 0.25 over 4 days | post-hoc V3: 0.25, 0.50 | fail |

**By idea class** (U artifact, D number, N name/coinage, W rare word):

| Class | ideas | agent nodes | R̂ [95% CI] | R_c | P(s ≥ 2) | P(s ≥ 3) | s_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D | 121 | 200 | 0.33 [0.22, 0.42] | 0.19 | 0.207 | 0.104 | 9 |
| N | 1680 | 2119 | 0.18 [0.15, 0.20] | 0.08 | 0.115 | 0.047 | 9 |
| U | 35 | 41 | 0.12 [0.03, 0.20] | 0.06 | 0.139 | 0.000 | 2 |
| W | 51 | 74 | 0.23 [0.08, 0.36] | 0.17 | 0.158 | 0.053 | 6 |

Data: `data/processed/H34-idea-cascades/G21/`. Figures: `../../figures/` (cross-period); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): HR₁₀ beats the field null (lower CI 1.53). D (unfitted shape): FN-GW band misses the tail; pure s^−3/2 rejected. E: no natural experiment inside this period was used.

## Notes
- Censoring check: R̂ without trees rooted on the last day = 0.214.
- Root vs non-root mean offspring 0.159 vs 0.330 (GW assumes equal).
- Root types: invented 0.96, from humans 0.001, field (unexposed) 0.041; 0.85 of non-seed first uses were visibly exposed.
