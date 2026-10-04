# H34 × G08: Design the AI Village benchmark for open-ended goal pursuit – and test yourselves on it! (2025-07-18 → 2025-08-13)

**Verdict:** mixed
**Role:** exploratory
**Period:** regime I · mode C · 4 agents at start (median room size 4) · 18 non-holdout days. Setup: Agents design a benchmark for their own open-ended goal pursuit and test themselves. o3, Claude Opus 4 and Claude 3.7 Sonnet independently wrote nearly identical frameworks. Human helpers (B) arrive two days earlier.

## Why this period
Secondary period for the cross-period criticality link (P4) and transfer of the forecast rule (P7). Mode C (shared objective), regime I.

## Prediction
*Written 2026-10-04 02:00 UTC, before running on this period* (after the synthetic validation and amendments A1–A5 of the main card; no real cascade statistic had been computed for any period).

| # | Prediction here | Counts against |
| --- | --- | --- |
| P1 | R̂ < 1 with upper 95% CI < 1; typical 0.05–0.5 | lower CI ≥ 1 |
| P2 | R̂ < H03 n̂_talk = 0.27; R_c < R̂ | R̂ > n̂_talk beyond its CI |
| P3a (A1) | observed P(s ≥ 3) and P(s ≥ 5) inside the FN-GW 90% band (if ≥ 50 trees) | outside the band |
| P5 (A2) | contagion beyond the field: HR₁₀ > 1 with lower CI > 1 | HR₁₀ CI includes 1 or < 1 |
| P6 (A3) | pooled recency HR(2 vs 1) ≤ 2.5 (not complex) | HR(2 vs 1) > 3 with lower CI > 2.5 |

**Verdict rule (A2):** supported = P5 (HR₁₀ lower CI > 1) and P3a pass; failed = both fail, or R̂ lower CI ≥ 1; mixed = exactly one passes; n/a = fewer than 20 non-seed agent first uses (or < 50 trees for P3a, which then counts as not tested and the verdict rests on P5: supported → mixed at best).

## Result
**mixed.** 1553 ideas, 1787 agent first uses, 1560 trees, N_room 4; R̂ = 0.127, contagion share R_c = 0.011, HR₁₀ = 1.10; P(s ≥ 2) = 0.107, largest tree 4.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 R̂ < 1 (upper CI < 1) | R̂ = 0.127 [0.109, 0.143] | critical R = 1 | pass |
| P2 R̂ < H03 n̂_talk | R̂ 0.127 vs n̂ 0.27; R_c = 0.011 | HH108: R̂ > n̂ | pass |
| P3a FN-GW band covers P(s ≥ 3), P(s ≥ 5) | P(s≥3) 0.029 (band 0.013–0.029); P(s≥5) 0.000 (band 0.000–0.000) | GW-NB band covers both: yes | pass |
| P3b pure s^−3/2 rejected; τ_app ≥ 2 | LR 702.0; τ_app 3.45 | critical branching | pass |
| P5 HR₁₀ > 1, lower CI > 1 (A2) | HR₁₀ = 1.10 [0.70, 1.69] (42 adoptions at k = 0) | field: HR₁₀ ≤ 1 | fail |
| P5a jitter excess (pre-registered; failed guard) | exposed 0.970 vs null 0.995, p = 0.99 | uninterpretable (S2) | n/a |
| P6 pooled HR(2 vs 1) ≤ 2.5 | 18.21 [6.84, 36.33] | complex > 3; heterogeneity inflates | ambiguous |
| P7 day-ahead 90% PI coverage (pre-registered FN-GW) | P(s≥2) 0.29, P(s≥3) 0.65 over 17 days | post-hoc V3: 0.88, 0.94 | fail |

**By idea class** (U artifact, D number, N name/coinage, W rare word):

| Class | ideas | agent nodes | R̂ [95% CI] | R_c | P(s ≥ 2) | P(s ≥ 3) | s_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D | 42 | 46 | 0.09 [0.02, 0.18] | – | 0.095 | 0.000 | 2 |
| N | 1373 | 1583 | 0.13 [0.11, 0.15] | 0.00 | 0.107 | 0.030 | 4 |
| U | 61 | 65 | 0.06 [0.02, 0.12] | 0.02 | 0.066 | 0.000 | 2 |
| W | 77 | 93 | 0.17 [0.09, 0.25] | 0.14 | 0.156 | 0.039 | 4 |

Data: `data/processed/H34-idea-cascades/G08/`. Figures: `../../figures/` (cross-period); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): HR₁₀ does not beat the field null (lower CI 0.70). D (unfitted shape): FN-GW band covers the tail; pure s^−3/2 rejected. E: no natural experiment inside this period was used.

## Notes
- Median room size 4: trees cannot exceed 4 agents, so P(s ≥ 5) = 0 and the shape test is uninformative here.
- Censoring check: R̂ without trees rooted on the last day = 0.128.
- Root vs non-root mean offspring 0.118 vs 0.189 (GW assumes equal).
- Root types: invented 0.99, from humans 0.001, field (unexposed) 0.004; 0.97 of non-seed first uses were visibly exposed.
