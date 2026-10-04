# H34 × G18: Reduce global poverty as much as you can (2025-10-20 → 2025-11-03)

**Verdict:** mixed
**Role:** exploratory
**Period:** regime I · mode C · 7 agents at start (median room size 8) · 10 non-holdout days. Setup: Reduce global poverty. Two weeks of collaborative research and building; one agent swapped.

## Why this period
Secondary period for the cross-period criticality link (P4) and transfer of the forecast rule (P7). Mode C (shared objective), regime I.

## Prediction
*Written 2026-10-04 02:00 UTC, before running on this period* (after the synthetic validation and amendments A1–A5 of the main card; no real cascade statistic had been computed for any period).

| # | Prediction here | Counts against |
| --- | --- | --- |
| P1 | R̂ < 1 with upper 95% CI < 1; typical 0.05–0.5 | lower CI ≥ 1 |
| P2 | R̂ < H03 n̂_talk = 0.70; R_c < R̂ | R̂ > n̂_talk beyond its CI |
| P3a (A1) | observed P(s ≥ 3) and P(s ≥ 5) inside the FN-GW 90% band (if ≥ 50 trees) | outside the band |
| P5 (A2) | contagion beyond the field: HR₁₀ > 1 with lower CI > 1 | HR₁₀ CI includes 1 or < 1 |
| P6 (A3) | pooled recency HR(2 vs 1) ≤ 2.5 (not complex) | HR(2 vs 1) > 3 with lower CI > 2.5 |

**Verdict rule (A2):** supported = P5 (HR₁₀ lower CI > 1) and P3a pass; failed = both fail, or R̂ lower CI ≥ 1; mixed = exactly one passes; n/a = fewer than 20 non-seed agent first uses (or < 50 trees for P3a, which then counts as not tested and the verdict rests on P5: supported → mixed at best).

## Result
**mixed.** 3128 ideas, 4758 agent first uses, 3294 trees, N_room 8; R̂ = 0.308, contagion share R_c = 0.181, HR₁₀ = 2.43; P(s ≥ 2) = 0.225, largest tree 8.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 R̂ < 1 (upper CI < 1) | R̂ = 0.308 [0.291, 0.324] | critical R = 1 | pass |
| P2 R̂ < H03 n̂_talk | R̂ 0.308 vs n̂ 0.70; R_c = 0.181 | HH108: R̂ > n̂ | pass |
| P3a FN-GW band covers P(s ≥ 3), P(s ≥ 5) | P(s≥3) 0.111 (band 0.091–0.120); P(s≥5) 0.030 (band 0.012–0.025) | GW-NB band covers both: no | fail (s≥5 heavier than FN-GW) |
| P3b pure s^−3/2 rejected; τ_app ≥ 2 | LR 1023.8; τ_app 2.55 | critical branching | pass |
| P5 HR₁₀ > 1, lower CI > 1 (A2) | HR₁₀ = 2.43 [2.17, 2.72] (361 adoptions at k = 0) | field: HR₁₀ ≤ 1 | pass |
| P5a jitter excess (pre-registered; failed guard) | exposed 0.900 vs null 0.982, p = 1.00 | uninterpretable (S2) | n/a |
| P6 pooled HR(2 vs 1) ≤ 2.5 | 3.74 [2.90, 4.63] | complex > 3; heterogeneity inflates | ambiguous |
| P7 day-ahead 90% PI coverage (pre-registered FN-GW) | P(s≥2) 0.22, P(s≥3) 0.33 over 9 days | post-hoc V3: 0.56, 0.78 | fail |

**By idea class** (U artifact, D number, N name/coinage, W rare word):

| Class | ideas | agent nodes | R̂ [95% CI] | R_c | P(s ≥ 2) | P(s ≥ 3) | s_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D | 127 | 222 | 0.39 [0.29, 0.48] | 0.27 | 0.265 | 0.125 | 8 |
| N | 2634 | 3754 | 0.27 [0.25, 0.28] | 0.14 | 0.189 | 0.083 | 8 |
| U | 51 | 166 | 0.55 [0.47, 0.63] | 0.40 | 0.486 | 0.324 | 7 |
| W | 316 | 616 | 0.47 [0.43, 0.50] | 0.35 | 0.451 | 0.296 | 8 |

Data: `data/processed/H34-idea-cascades/G18/`. Figures: `../../figures/` (cross-period); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): HR₁₀ beats the field null (lower CI 2.17). D (unfitted shape): FN-GW band misses the tail; pure s^−3/2 rejected. E: no natural experiment inside this period was used.

## Notes
- Censoring check: R̂ without trees rooted on the last day = 0.312.
- Root vs non-root mean offspring 0.287 vs 0.355 (GW assumes equal).
- Root types: invented 0.95, from humans 0.002, field (unexposed) 0.049; 0.90 of non-seed first uses were visibly exposed.
