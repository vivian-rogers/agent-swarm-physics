# H34 × G26: Elect a village leader. They choose this week’s goal! (2026-01-05 → 2026-01-12)

**Verdict:** mixed
**Role:** exploratory
**Period:** regime I · mode C · 10 agents at start (median room size 10) · 5 non-holdout days. Setup: Elect a leader who picks the week's goal. Ballot failure, then chat approval voting with a three-way tie (DeepSeek-V3.2, Claude 3.7 Sonnet, Gemini 2.5 Pro at 9 each). DeepSeek-V3.2 won the runoff 7–1 and set an interactive-fiction game as the goal. That goal is not in `village_goals`.

## Why this period
Secondary period for the cross-period criticality link (P4) and transfer of the forecast rule (P7). Mode C (shared objective), regime I.

## Prediction
*Written 2026-10-04 02:00 UTC, before running on this period* (after the synthetic validation and amendments A1–A5 of the main card; no real cascade statistic had been computed for any period).

| # | Prediction here | Counts against |
| --- | --- | --- |
| P1 | R̂ < 1 with upper 95% CI < 1; typical 0.05–0.5 | lower CI ≥ 1 |
| P2 | R̂ < H03 n̂_talk = 0.56; R_c < R̂ | R̂ > n̂_talk beyond its CI |
| P3a (A1) | observed P(s ≥ 3) and P(s ≥ 5) inside the FN-GW 90% band (if ≥ 50 trees) | outside the band |
| P5 (A2) | contagion beyond the field: HR₁₀ > 1 with lower CI > 1 | HR₁₀ CI includes 1 or < 1 |
| P6 (A3) | pooled recency HR(2 vs 1) ≤ 2.5 (not complex) | HR(2 vs 1) > 3 with lower CI > 2.5 |

**Verdict rule (A2):** supported = P5 (HR₁₀ lower CI > 1) and P3a pass; failed = both fail, or R̂ lower CI ≥ 1; mixed = exactly one passes; n/a = fewer than 20 non-seed agent first uses (or < 50 trees for P3a, which then counts as not tested and the verdict rests on P5: supported → mixed at best).

## Result
**mixed.** 2271 ideas, 3089 agent first uses, 2343 trees, N_room 10; R̂ = 0.242, contagion share R_c = 0.181, HR₁₀ = 4.01; P(s ≥ 2) = 0.144, largest tree 10.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 R̂ < 1 (upper CI < 1) | R̂ = 0.242 [0.219, 0.265] | critical R = 1 | pass |
| P2 R̂ < H03 n̂_talk | R̂ 0.242 vs n̂ 0.56; R_c = 0.181 | HH108: R̂ > n̂ | pass |
| P3a FN-GW band covers P(s ≥ 3), P(s ≥ 5) | P(s≥3) 0.073 (band 0.054–0.085); P(s≥5) 0.024 (band 0.006–0.017) | GW-NB band covers both: no | fail (s≥5 heavier than FN-GW) |
| P3b pure s^−3/2 rejected; τ_app ≥ 2 | LR 1320.5; τ_app 3.02 | critical branching | pass |
| P5 HR₁₀ > 1, lower CI > 1 (A2) | HR₁₀ = 4.01 [3.32, 4.83] (138 adoptions at k = 0) | field: HR₁₀ ≤ 1 | pass |
| P5a jitter excess (pre-registered; failed guard) | exposed 0.912 vs null 0.985, p = 1.00 | uninterpretable (S2) | n/a |
| P6 pooled HR(2 vs 1) ≤ 2.5 | 5.96 [4.60, 7.66] | complex > 3; heterogeneity inflates | ambiguous |
| P7 day-ahead 90% PI coverage (pre-registered FN-GW) | P(s≥2) 0.75, P(s≥3) 0.75 over 4 days | post-hoc V3: 0.75, 1.00 | fail |

**By idea class** (U artifact, D number, N name/coinage, W rare word):

| Class | ideas | agent nodes | R̂ [95% CI] | R_c | P(s ≥ 2) | P(s ≥ 3) | s_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D | 77 | 137 | 0.39 [0.25, 0.49] | 0.25 | 0.238 | 0.131 | 9 |
| N | 2121 | 2825 | 0.23 [0.20, 0.25] | 0.17 | 0.134 | 0.067 | 10 |
| U | 46 | 90 | 0.42 [0.32, 0.50] | 0.35 | 0.423 | 0.212 | 5 |
| W | 27 | 37 | 0.27 [0.04, 0.45] | 0.16 | 0.148 | 0.074 | 5 |

Data: `data/processed/H34-idea-cascades/G26/`. Figures: `../../figures/` (cross-period); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): HR₁₀ beats the field null (lower CI 3.32). D (unfitted shape): FN-GW band misses the tail; pure s^−3/2 rejected. E: no natural experiment inside this period was used.

## Notes
- Censoring check: R̂ without trees rooted on the last day = 0.241.
- Root vs non-root mean offspring 0.184 vs 0.424 (GW assumes equal).
- Root types: invented 0.97, from humans 0.000, field (unexposed) 0.031; 0.91 of non-seed first uses were visibly exposed.
