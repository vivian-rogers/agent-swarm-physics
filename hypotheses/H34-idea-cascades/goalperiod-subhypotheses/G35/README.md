# H34 × G35: Test your game to make it as fun and functional as you can! (2026-03-16 → 2026-03-23)

**Verdict:** mixed
**Role:** exploratory
**Period:** regime II · mode C · 13 agents at start (median room size 9) · 5 non-holdout days. Setup: Test your game. The village split into #best (GPT-5.4, Opus 4.6, Gemini 3.1 Pro) and #rest to evolve **separate forks** of the RPG.

## Why this period
Secondary period for the cross-period criticality link (P4) and transfer of the forecast rule (P7). Mode C (shared objective), regime II.

## Prediction
*Written 2026-10-04 02:00 UTC, before running on this period* (after the synthetic validation and amendments A1–A5 of the main card; no real cascade statistic had been computed for any period).

| # | Prediction here | Counts against |
| --- | --- | --- |
| P1 | R̂ < 1 with upper 95% CI < 1; typical 0.05–0.5 | lower CI ≥ 1 |
| P2 | R̂ < H03 n̂_talk = 0.08; R_c < R̂ | R̂ > n̂_talk beyond its CI |
| P3a (A1) | observed P(s ≥ 3) and P(s ≥ 5) inside the FN-GW 90% band (if ≥ 50 trees) | outside the band |
| P5 (A2) | contagion beyond the field: HR₁₀ > 1 with lower CI > 1 | HR₁₀ CI includes 1 or < 1 |
| P6 (A3) | pooled recency HR(2 vs 1) ≤ 2.5 (not complex) | HR(2 vs 1) > 3 with lower CI > 2.5 |

**Verdict rule (A2):** supported = P5 (HR₁₀ lower CI > 1) and P3a pass; failed = both fail, or R̂ lower CI ≥ 1; mixed = exactly one passes; n/a = fewer than 20 non-seed agent first uses (or < 50 trees for P3a, which then counts as not tested and the verdict rests on P5: supported → mixed at best).

## Result
**mixed.** 3000 ideas, 4839 agent first uses, 3350 trees, N_room 9; R̂ = 0.332, contagion share R_c = 0.318, HR₁₀ = 22.66; P(s ≥ 2) = 0.238, largest tree 12.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 R̂ < 1 (upper CI < 1) | R̂ = 0.332 [0.315, 0.350] | critical R = 1 | pass |
| P2 R̂ < H03 n̂_talk | R̂ 0.332 vs n̂ 0.08; R_c = 0.318 | HH108: R̂ > n̂ | fail |
| P3a FN-GW band covers P(s ≥ 3), P(s ≥ 5) | P(s≥3) 0.097 (band 0.104–0.130); P(s≥5) 0.030 (band 0.019–0.030) | GW-NB band covers both: no | fail |
| P3b pure s^−3/2 rejected; τ_app ≥ 2 | LR 1400.8; τ_app 2.61 | critical branching | pass |
| P5 HR₁₀ > 1, lower CI > 1 (A2) | HR₁₀ = 22.66 [20.09, 25.79] (288 adoptions at k = 0) | field: HR₁₀ ≤ 1 | pass |
| P5a jitter excess (pre-registered; failed guard) | exposed 0.847 vs null 0.854, p = 0.98 | uninterpretable (S2) | n/a |
| P6 pooled HR(2 vs 1) ≤ 2.5 | 3.54 [2.98, 4.15] | complex > 3; heterogeneity inflates | ambiguous |
| P5c cross-room ratio > 3 | 13.5 [10.7, 17.6] (P(adopt) 0.066 vs 0.0049) | field ≈ 1–1.8 (S2) | pass (room fields confound) |
| P7 day-ahead 90% PI coverage (pre-registered FN-GW) | P(s≥2) 0.00, P(s≥3) 0.00 over 4 days | post-hoc V3: 0.50, 1.00 | fail |

**By idea class** (U artifact, D number, N name/coinage, W rare word):

| Class | ideas | agent nodes | R̂ [95% CI] | R_c | P(s ≥ 2) | P(s ≥ 3) | s_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D | 78 | 117 | 0.34 [0.24, 0.44] | 0.33 | 0.265 | 0.084 | 5 |
| N | 2863 | 4617 | 0.33 [0.31, 0.35] | 0.32 | 0.238 | 0.098 | 12 |
| U | 8 | 26 | 0.69 [0.27, 0.81] | 0.68 | 0.667 | 0.333 | 9 |
| W | 51 | 79 | 0.24 [0.08, 0.38] | 0.21 | 0.161 | 0.065 | 5 |

Data: `data/processed/H34-idea-cascades/G35/`. Figures: `../../figures/` (cross-period); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): HR₁₀ beats the field null (lower CI 20.09). D (unfitted shape): FN-GW band misses the tail; pure s^−3/2 rejected. G (rooms): never-exposed agents adopt far less (ratio 13.5), confounded by room fields. E: no natural experiment inside this period was used.

## Notes
- Two rooms active: the cross-room contrast is available but confounded by room-specific fields (rooms often worked on different projects).
- Censoring check: R̂ without trees rooted on the last day = 0.341.
- Root vs non-root mean offspring 0.284 vs 0.361 (GW assumes equal).
- Root types: invented 0.88, from humans 0.038, field (unexposed) 0.087; 0.85 of non-seed first uses were visibly exposed.
