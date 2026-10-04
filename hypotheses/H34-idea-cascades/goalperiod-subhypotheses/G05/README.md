# H34 × G05: Holiday: do whatever you like! Next goal will begin soon (2025-06-19 → 2025-06-26)

**Verdict:** supported
**Verdict (1b):** supported (ledger visibility: R̂ 0.22, HR₁₀ 5.8 [4.0, 8.8], tail ok; H57 placebo HR unread/seen 19.6/7.6)
**Role:** replication (exploratory)
**Period:** regime I · mode F · 4 agents at start (median room size 4) · 5 non-holdout days. Setup: Holiday after the story event. A feedback survey gave a clear mandate for rotating leadership (9 votes).

## Why this period
Secondary period for the cross-period criticality link (P4) and transfer of the forecast rule (P7). Mode F (free / pick your own), regime I.

## Prediction
*Written 2026-10-04 02:00 UTC, before running on this period* (after the synthetic validation and amendments A1–A5 of the main card; no real cascade statistic had been computed for any period).

| # | Prediction here | Counts against |
| --- | --- | --- |
| P1 | R̂ < 1 with upper 95% CI < 1; typical 0.05–0.5 | lower CI ≥ 1 |
| P2 | R̂ < H03 n̂_talk = 0.15; R_c < R̂ | R̂ > n̂_talk beyond its CI |
| P3a (A1) | observed P(s ≥ 3) and P(s ≥ 5) inside the FN-GW 90% band (if ≥ 50 trees) | outside the band |
| P5 (A2) | contagion beyond the field: HR₁₀ > 1 with lower CI > 1 | HR₁₀ CI includes 1 or < 1 |
| P6 (A3) | pooled recency HR(2 vs 1) ≤ 2.5 (not complex) | HR(2 vs 1) > 3 with lower CI > 2.5 |

**Verdict rule (A2):** supported = P5 (HR₁₀ lower CI > 1) and P3a pass; failed = both fail, or R̂ lower CI ≥ 1; mixed = exactly one passes; n/a = fewer than 20 non-seed agent first uses (or < 50 trees for P3a, which then counts as not tested and the verdict rests on P5: supported → mixed at best).

## Result
**supported.** 554 ideas, 738 agent first uses, 592 trees, N_room 4; R̂ = 0.198, contagion share R_c = 0.101, HR₁₀ = 2.05; P(s ≥ 2) = 0.181, largest tree 4.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 R̂ < 1 (upper CI < 1) | R̂ = 0.198 [0.167, 0.226] | critical R = 1 | pass |
| P2 R̂ < H03 n̂_talk | R̂ 0.198 vs n̂ 0.15; R_c = 0.101 | HH108: R̂ > n̂ | fail |
| P3a FN-GW band covers P(s ≥ 3), P(s ≥ 5) | P(s≥3) 0.046 (band 0.030–0.062); P(s≥5) 0.000 (band 0.000–0.000) | GW-NB band covers both: yes | pass |
| P3b pure s^−3/2 rejected; τ_app ≥ 2 | LR 152.0; τ_app 2.78 | critical branching | pass |
| P5 HR₁₀ > 1, lower CI > 1 (A2) | HR₁₀ = 2.05 [1.45, 2.86] (62 adoptions at k = 0) | field: HR₁₀ ≤ 1 | pass |
| P5a jitter excess (pre-registered; failed guard) | exposed 0.863 vs null 0.986, p = 1.00 | uninterpretable (S2) | n/a |
| P6 pooled HR(2 vs 1) ≤ 2.5 | 3.32 [1.96, 5.53] | complex > 3; heterogeneity inflates | ambiguous |
| P7 day-ahead 90% PI coverage (pre-registered FN-GW) | P(s≥2) 0.50, P(s≥3) 1.00 over 4 days | post-hoc V3: 0.50, 1.00 | fail |

**By idea class** (U artifact, D number, N name/coinage, W rare word):

| Class | ideas | agent nodes | R̂ [95% CI] | R_c | P(s ≥ 2) | P(s ≥ 3) | s_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D | 37 | 42 | 0.10 [0.02, 0.18] | 0.07 | 0.105 | 0.000 | 2 |
| N | 444 | 603 | 0.21 [0.18, 0.25] | 0.11 | 0.196 | 0.053 | 4 |
| U | 5 | 7 | 0.29 [0.00, 0.44] | 0.17 | 0.400 | 0.000 | 2 |
| W | 68 | 86 | 0.13 [0.05, 0.22] | 0.06 | 0.107 | 0.027 | 4 |

Data: `data/processed/H34-idea-cascades/G05/`. Figures: `../../figures/` (cross-period); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): HR₁₀ beats the field null (lower CI 1.45). D (unfitted shape): FN-GW band covers the tail; pure s^−3/2 rejected. E: no natural experiment inside this period was used.

## Notes
- Median room size 4: trees cannot exceed 4 agents, so P(s ≥ 5) = 0 and the shape test is uninformative here.
- Censoring check: R̂ without trees rooted on the last day = 0.227.
- Root vs non-root mean offspring 0.199 vs 0.192 (GW assumes equal).
- Root types: invented 0.89, from humans 0.062, field (unexposed) 0.049; 0.86 of non-seed first uses were visibly exposed.
