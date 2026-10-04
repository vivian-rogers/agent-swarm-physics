# H34 × G23: Compete against each other in an online chess tournament (2025-12-15 → 2025-12-22)

**Verdict:** mixed
**Role:** exploratory
**Period:** regime I · mode K · 10 agents at start (median room size 10) · 5 non-holdout days. Setup: Online chess tournament: agents play each other on Lichess.

## Why this period
Secondary period for the cross-period criticality link (P4) and transfer of the forecast rule (P7). Mode K (competitive), regime I.

## Prediction
*Written 2026-10-04 02:00 UTC, before running on this period* (after the synthetic validation and amendments A1–A5 of the main card; no real cascade statistic had been computed for any period).

| # | Prediction here | Counts against |
| --- | --- | --- |
| P1 | R̂ < 1 with upper 95% CI < 1; typical 0.05–0.5 | lower CI ≥ 1 |
| P2 | R̂ < H03 n̂_talk = 0.10; R_c < R̂ | R̂ > n̂_talk beyond its CI |
| P3a (A1) | observed P(s ≥ 3) and P(s ≥ 5) inside the FN-GW 90% band (if ≥ 50 trees) | outside the band |
| P5 (A2) | contagion beyond the field: HR₁₀ > 1 with lower CI > 1 | HR₁₀ CI includes 1 or < 1 |
| P6 (A3) | pooled recency HR(2 vs 1) ≤ 2.5 (not complex) | HR(2 vs 1) > 3 with lower CI > 2.5 |

**Verdict rule (A2):** supported = P5 (HR₁₀ lower CI > 1) and P3a pass; failed = both fail, or R̂ lower CI ≥ 1; mixed = exactly one passes; n/a = fewer than 20 non-seed agent first uses (or < 50 trees for P3a, which then counts as not tested and the verdict rests on P5: supported → mixed at best).

## Result
**mixed.** 1187 ideas, 1463 agent first uses, 1196 trees, N_room 10; R̂ = 0.183, contagion share R_c = 0.105, HR₁₀ = 2.35; P(s ≥ 2) = 0.105, largest tree 10.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 R̂ < 1 (upper CI < 1) | R̂ = 0.183 [0.150, 0.215] | critical R = 1 | pass |
| P2 R̂ < H03 n̂_talk | R̂ 0.183 vs n̂ 0.10; R_c = 0.105 | HH108: R̂ > n̂ | fail |
| P3a FN-GW band covers P(s ≥ 3), P(s ≥ 5) | P(s≥3) 0.043 (band 0.039–0.067); P(s≥5) 0.017 (band 0.004–0.016) | GW-NB band covers both: no | fail (s≥5 heavier than FN-GW) |
| P3b pure s^−3/2 rejected; τ_app ≥ 2 | LR 860.3; τ_app 3.40 | critical branching | pass |
| P5 HR₁₀ > 1, lower CI > 1 (A2) | HR₁₀ = 2.35 [1.57, 3.58] (34 adoptions at k = 0) | field: HR₁₀ ≤ 1 | pass |
| P5a jitter excess (pre-registered; failed guard) | exposed 0.967 vs null 0.982, p = 0.98 | uninterpretable (S2) | n/a |
| P6 pooled HR(2 vs 1) ≤ 2.5 | 7.23 [4.29, 11.54] | complex > 3; heterogeneity inflates | ambiguous |
| P7 day-ahead 90% PI coverage (pre-registered FN-GW) | P(s≥2) 0.25, P(s≥3) 0.00 over 4 days | post-hoc V3: 0.50, 0.75 | fail |

**By idea class** (U artifact, D number, N name/coinage, W rare word):

| Class | ideas | agent nodes | R̂ [95% CI] | R_c | P(s ≥ 2) | P(s ≥ 3) | s_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D | 49 | 78 | 0.31 [0.06, 0.47] | 0.00 | 0.111 | 0.056 | 10 |
| N | 1105 | 1347 | 0.18 [0.14, 0.21] | 0.11 | 0.106 | 0.042 | 10 |
| U | 5 | 10 | 0.50 [0.17, 0.67] | 0.50 | 0.600 | 0.200 | 4 |
| W | 28 | 28 | 0.00 [0.00, 0.00] | – | 0.000 | 0.000 | 1 |

Data: `data/processed/H34-idea-cascades/G23/`. Figures: `../../figures/` (cross-period); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): HR₁₀ beats the field null (lower CI 1.57). D (unfitted shape): FN-GW band misses the tail; pure s^−3/2 rejected. E: no natural experiment inside this period was used.

## Notes
- Censoring check: R̂ without trees rooted on the last day = 0.210.
- Root vs non-root mean offspring 0.146 vs 0.345 (GW assumes equal).
- Root types: invented 0.99, from humans 0.000, field (unexposed) 0.008; 0.97 of non-seed first uses were visibly exposed.
