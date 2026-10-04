# H34 × G19: Create a popular daily puzzle game like Wordle (2025-11-03 → 2025-11-17)

**Verdict:** mixed
**Verdict (1b):** mixed (ledger visibility: R̂ 0.23, HR₁₀ 8.4 [6.7, 10.8], tail heavy; H57 placebo HR unread/seen 2.9/5.1)
**Role:** replication (exploratory)
**Period:** regime I · mode C · 7 agents at start (median room size 7) · 10 non-holdout days. Setup: Make a popular daily puzzle game. Many candidate concepts (Chronos, Huedle, Maplink, …) were brainstormed, then the swarm converged and shipped.

## Why this period
Secondary period for the cross-period criticality link (P4) and transfer of the forecast rule (P7). Mode C (shared objective), regime I.

## Prediction
*Written 2026-10-04 02:00 UTC, before running on this period* (after the synthetic validation and amendments A1–A5 of the main card; no real cascade statistic had been computed for any period).

| # | Prediction here | Counts against |
| --- | --- | --- |
| P1 | R̂ < 1 with upper 95% CI < 1; typical 0.05–0.5 | lower CI ≥ 1 |
| P2 | R̂ < H03 n̂_talk = 0.69; R_c < R̂ | R̂ > n̂_talk beyond its CI |
| P3a (A1) | observed P(s ≥ 3) and P(s ≥ 5) inside the FN-GW 90% band (if ≥ 50 trees) | outside the band |
| P5 (A2) | contagion beyond the field: HR₁₀ > 1 with lower CI > 1 | HR₁₀ CI includes 1 or < 1 |
| P6 (A3) | pooled recency HR(2 vs 1) ≤ 2.5 (not complex) | HR(2 vs 1) > 3 with lower CI > 2.5 |

**Verdict rule (A2):** supported = P5 (HR₁₀ lower CI > 1) and P3a pass; failed = both fail, or R̂ lower CI ≥ 1; mixed = exactly one passes; n/a = fewer than 20 non-seed agent first uses (or < 50 trees for P3a, which then counts as not tested and the verdict rests on P5: supported → mixed at best).

## Result
**mixed.** 2807 ideas, 3696 agent first uses, 2909 trees, N_room 7; R̂ = 0.213, contagion share R_c = 0.149, HR₁₀ = 3.34; P(s ≥ 2) = 0.146, largest tree 8.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 R̂ < 1 (upper CI < 1) | R̂ = 0.213 [0.193, 0.231] | critical R = 1 | pass |
| P2 R̂ < H03 n̂_talk | R̂ 0.213 vs n̂ 0.69; R_c = 0.149 | HH108: R̂ > n̂ | pass |
| P3a FN-GW band covers P(s ≥ 3), P(s ≥ 5) | P(s≥3) 0.064 (band 0.046–0.070); P(s≥5) 0.018 (band 0.004–0.012) | GW-NB band covers both: no | fail (s≥5 heavier than FN-GW) |
| P3b pure s^−3/2 rejected; τ_app ≥ 2 | LR 1540.5; τ_app 3.06 | critical branching | pass |
| P5 HR₁₀ > 1, lower CI > 1 (A2) | HR₁₀ = 3.34 [2.79, 4.06] (161 adoptions at k = 0) | field: HR₁₀ ≤ 1 | pass |
| P5a jitter excess (pre-registered; failed guard) | exposed 0.885 vs null 0.969, p = 1.00 | uninterpretable (S2) | n/a |
| P6 pooled HR(2 vs 1) ≤ 2.5 | 7.91 [6.22, 10.57] | complex > 3; heterogeneity inflates | ambiguous |
| P7 day-ahead 90% PI coverage (pre-registered FN-GW) | P(s≥2) 0.33, P(s≥3) 0.56 over 9 days | post-hoc V3: 0.67, 0.89 | fail |

**By idea class** (U artifact, D number, N name/coinage, W rare word):

| Class | ideas | agent nodes | R̂ [95% CI] | R_c | P(s ≥ 2) | P(s ≥ 3) | s_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D | 98 | 177 | 0.34 [0.25, 0.43] | 0.22 | 0.259 | 0.112 | 7 |
| N | 2453 | 3133 | 0.20 [0.18, 0.21] | 0.14 | 0.131 | 0.059 | 7 |
| U | 57 | 114 | 0.41 [0.29, 0.51] | 0.26 | 0.299 | 0.179 | 8 |
| W | 199 | 272 | 0.25 [0.18, 0.31] | 0.18 | 0.221 | 0.069 | 7 |

Data: `data/processed/H34-idea-cascades/G19/`. Figures: `../../figures/` (cross-period); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): HR₁₀ beats the field null (lower CI 2.79). D (unfitted shape): FN-GW band misses the tail; pure s^−3/2 rejected. E: no natural experiment inside this period was used.

## Notes
- Censoring check: R̂ without trees rooted on the last day = 0.225.
- Root vs non-root mean offspring 0.183 vs 0.324 (GW assumes equal).
- Root types: invented 0.96, from humans 0.000, field (unexposed) 0.035; 0.89 of non-seed first uses were visibly exposed.
