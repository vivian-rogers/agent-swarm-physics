# H34 × G11: Pursue whatever you'd like to (2025-08-25 → 2025-09-01)

**Verdict:** failed
**Verdict (1b):** mixed (ledger visibility: R̂ 0.21, HR₁₀ 12.2 [6.7, 25.2], tail heavy; H57 placebo HR unread/seen 10.6/21.0)
**Role:** exploratory
**Period:** regime I · mode F · 7 agents at start (median room size 7) · 5 non-holdout days. Setup: Free week. Self-chosen meta-projects (e.g. documenting platform instabilities).

## Why this period
Secondary period for the cross-period criticality link (P4) and transfer of the forecast rule (P7). Mode F (free / pick your own), regime I.

## Prediction
*Written 2026-10-04 02:00 UTC, before running on this period* (after the synthetic validation and amendments A1–A5 of the main card; no real cascade statistic had been computed for any period).

| # | Prediction here | Counts against |
| --- | --- | --- |
| P1 | R̂ < 1 with upper 95% CI < 1; typical 0.05–0.5 | lower CI ≥ 1 |
| P2 | R̂ < H03 n̂_talk = 0.61; R_c < R̂ | R̂ > n̂_talk beyond its CI |
| P3a (A1) | observed P(s ≥ 3) and P(s ≥ 5) inside the FN-GW 90% band (if ≥ 50 trees) | outside the band |
| P5 (A2) | contagion beyond the field: HR₁₀ > 1 with lower CI > 1 | HR₁₀ CI includes 1 or < 1 |
| P6 (A3) | pooled recency HR(2 vs 1) ≤ 2.5 (not complex) | HR(2 vs 1) > 3 with lower CI > 2.5 |

**Verdict rule (A2):** supported = P5 (HR₁₀ lower CI > 1) and P3a pass; failed = both fail, or R̂ lower CI ≥ 1; mixed = exactly one passes; n/a = fewer than 20 non-seed agent first uses (or < 50 trees for P3a, which then counts as not tested and the verdict rests on P5: supported → mixed at best).

## Result
**failed.** 523 ideas, 670 agent first uses, 565 trees, N_room 7; R̂ = 0.157, contagion share R_c = 0.035, HR₁₀ = 1.29; P(s ≥ 2) = 0.115, largest tree 6.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 R̂ < 1 (upper CI < 1) | R̂ = 0.157 [0.121, 0.191] | critical R = 1 | pass |
| P2 R̂ < H03 n̂_talk | R̂ 0.157 vs n̂ 0.61; R_c = 0.035 | HH108: R̂ > n̂ | pass |
| P3a FN-GW band covers P(s ≥ 3), P(s ≥ 5) | P(s≥3) 0.039 (band 0.021–0.053); P(s≥5) 0.012 (band 0.000–0.009) | GW-NB band covers both: no | fail (s≥5 heavier than FN-GW) |
| P3b pure s^−3/2 rejected; τ_app ≥ 2 | LR 348.7; τ_app 3.40 | critical branching | pass |
| P5 HR₁₀ > 1, lower CI > 1 (A2) | HR₁₀ = 1.29 [0.88, 1.92] (50 adoptions at k = 0) | field: HR₁₀ ≤ 1 | fail |
| P5a jitter excess (pre-registered; failed guard) | exposed 0.714 vs null 0.947, p = 1.00 | uninterpretable (S2) | n/a |
| P6 pooled HR(2 vs 1) ≤ 2.5 | 5.26 [2.46, 9.58] | complex > 3; heterogeneity inflates | ambiguous |
| P7 day-ahead 90% PI coverage (pre-registered FN-GW) | P(s≥2) 0.33, P(s≥3) 0.67 over 3 days | post-hoc V3: 0.50, 0.75 | fail |

**By idea class** (U artifact, D number, N name/coinage, W rare word):

| Class | ideas | agent nodes | R̂ [95% CI] | R_c | P(s ≥ 2) | P(s ≥ 3) | s_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D | 100 | 108 | 0.05 [0.01, 0.09] | 0.00 | 0.039 | 0.010 | 3 |
| N | 390 | 504 | 0.16 [0.11, 0.20] | 0.02 | 0.118 | 0.033 | 6 |
| U | 10 | 21 | 0.52 [0.23, 0.67] | 0.44 | 0.400 | 0.400 | 5 |
| W | 23 | 37 | 0.27 [0.13, 0.40] | 0.10 | 0.259 | 0.111 | 3 |

Data: `data/processed/H34-idea-cascades/G11/`. Figures: `../../figures/` (cross-period); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): HR₁₀ does not beat the field null (lower CI 0.88). D (unfitted shape): FN-GW band misses the tail; pure s^−3/2 rejected. E: no natural experiment inside this period was used.

## Notes
- Censoring check: R̂ without trees rooted on the last day = 0.129.
- Root vs non-root mean offspring 0.145 vs 0.219 (GW assumes equal).
- Root types: invented 0.93, from humans 0.000, field (unexposed) 0.074; 0.71 of non-seed first uses were visibly exposed.
