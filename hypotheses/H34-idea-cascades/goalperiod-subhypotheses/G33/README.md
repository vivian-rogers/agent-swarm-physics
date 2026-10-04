# H34 × G33: Discuss, debate, and act on your views about the recent Pentagon-AI company news (2026-03-02 → 2026-03-05)

**Verdict:** mixed
**Role:** exploratory
**Period:** regime II · mode C · 12 agents at start (median room size 11) · 3 non-holdout days. Setup: Discuss, debate and act on the Pentagon–AI company news. A shared claims database with strict sourcing. Three days, first goal fully in regime II.

## Why this period
Secondary period for the cross-period criticality link (P4) and transfer of the forecast rule (P7). Mode C (shared objective), regime II.

## Prediction
*Written 2026-10-04 02:00 UTC, before running on this period* (after the synthetic validation and amendments A1–A5 of the main card; no real cascade statistic had been computed for any period).

| # | Prediction here | Counts against |
| --- | --- | --- |
| P1 | R̂ < 1 with upper 95% CI < 1; typical 0.05–0.5 | lower CI ≥ 1 |
| P2 | R̂ < H03 n̂_talk = 0.76; R_c < R̂ | R̂ > n̂_talk beyond its CI |
| P3a (A1) | observed P(s ≥ 3) and P(s ≥ 5) inside the FN-GW 90% band (if ≥ 50 trees) | outside the band |
| P5 (A2) | contagion beyond the field: HR₁₀ > 1 with lower CI > 1 | HR₁₀ CI includes 1 or < 1 |
| P6 (A3) | pooled recency HR(2 vs 1) ≤ 2.5 (not complex) | HR(2 vs 1) > 3 with lower CI > 2.5 |

**Verdict rule (A2):** supported = P5 (HR₁₀ lower CI > 1) and P3a pass; failed = both fail, or R̂ lower CI ≥ 1; mixed = exactly one passes; n/a = fewer than 20 non-seed agent first uses (or < 50 trees for P3a, which then counts as not tested and the verdict rests on P5: supported → mixed at best).

## Result
**mixed.** 3487 ideas, 5134 agent first uses, 3730 trees, N_room 11; R̂ = 0.329, contagion share R_c = 0.288, HR₁₀ = 8.03; P(s ≥ 2) = 0.205, largest tree 10.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 R̂ < 1 (upper CI < 1) | R̂ = 0.329 [0.311, 0.348] | critical R = 1 | pass |
| P2 R̂ < H03 n̂_talk | R̂ 0.329 vs n̂ 0.76; R_c = 0.288 | HH108: R̂ > n̂ | pass |
| P3a FN-GW band covers P(s ≥ 3), P(s ≥ 5) | P(s≥3) 0.088 (band 0.102–0.134); P(s≥5) 0.020 (band 0.018–0.031) | GW-NB band covers both: no | fail |
| P3b pure s^−3/2 rejected; τ_app ≥ 2 | LR 1743.9; τ_app 2.75 | critical branching | pass |
| P5 HR₁₀ > 1, lower CI > 1 (A2) | HR₁₀ = 8.03 [7.03, 9.03] (250 adoptions at k = 0) | field: HR₁₀ ≤ 1 | pass |
| P5a jitter excess (pre-registered; failed guard) | exposed 0.931 vs null 0.985, p = 1.00 | uninterpretable (S2) | n/a |
| P6 pooled HR(2 vs 1) ≤ 2.5 | 3.74 [3.18, 4.37] | complex > 3; heterogeneity inflates | ambiguous |
| P7 day-ahead 90% PI coverage (pre-registered FN-GW) | P(s≥2) 0.00, P(s≥3) 0.00 over 2 days | post-hoc V3: 0.00, 1.00 | fail |

**By idea class** (U artifact, D number, N name/coinage, W rare word):

| Class | ideas | agent nodes | R̂ [95% CI] | R_c | P(s ≥ 2) | P(s ≥ 3) | s_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D | 70 | 151 | 0.59 [0.46, 0.69] | 0.55 | 0.384 | 0.163 | 8 |
| N | 3332 | 4826 | 0.32 [0.30, 0.33] | 0.28 | 0.198 | 0.084 | 10 |
| U | 15 | 27 | 0.44 [0.00, 0.65] | 0.44 | 0.188 | 0.125 | 6 |
| W | 70 | 130 | 0.48 [0.36, 0.56] | 0.34 | 0.342 | 0.211 | 7 |

Data: `data/processed/H34-idea-cascades/G33/`. Figures: `../../figures/` (cross-period); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): HR₁₀ beats the field null (lower CI 7.03). D (unfitted shape): FN-GW band misses the tail; pure s^−3/2 rejected. E: no natural experiment inside this period was used.

## Notes
- Censoring check: R̂ without trees rooted on the last day = 0.342.
- Root vs non-root mean offspring 0.245 vs 0.350 (GW assumes equal).
- Root types: invented 0.89, from humans 0.076, field (unexposed) 0.034; 0.93 of non-seed first uses were visibly exposed.
