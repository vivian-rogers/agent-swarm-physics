# H34 × G27: Hack the OWASP Juice Shop hacking playground. Compete to see which agent can complete the most challenges (2026-01-12 → 2026-01-26)

**Verdict:** mixed
**Verdict (1b):** mixed (ledger visibility: R̂ 0.40, HR₁₀ 5.2 [4.5, 5.9], tail heavy; H57 placebo HR unread/seen 3.2/3.8)
**Role:** exploratory
**Period:** regime I · mode K · 10 agents at start (median room size 10) · 10 non-holdout days. Setup: Two-week OWASP Juice Shop hacking competition, which turned from rivalry into collaboration.

## Why this period
Secondary period for the cross-period criticality link (P4) and transfer of the forecast rule (P7). Mode K (competitive), regime I.

## Prediction
*Written 2026-10-04 02:00 UTC, before running on this period* (after the synthetic validation and amendments A1–A5 of the main card; no real cascade statistic had been computed for any period).

| # | Prediction here | Counts against |
| --- | --- | --- |
| P1 | R̂ < 1 with upper 95% CI < 1; typical 0.05–0.5 | lower CI ≥ 1 |
| P2 | R̂ < H03 n̂_talk = 0.41; R_c < R̂ | R̂ > n̂_talk beyond its CI |
| P3a (A1) | observed P(s ≥ 3) and P(s ≥ 5) inside the FN-GW 90% band (if ≥ 50 trees) | outside the band |
| P5 (A2) | contagion beyond the field: HR₁₀ > 1 with lower CI > 1 | HR₁₀ CI includes 1 or < 1 |
| P6 (A3) | pooled recency HR(2 vs 1) ≤ 2.5 (not complex) | HR(2 vs 1) > 3 with lower CI > 2.5 |

**Verdict rule (A2):** supported = P5 (HR₁₀ lower CI > 1) and P3a pass; failed = both fail, or R̂ lower CI ≥ 1; mixed = exactly one passes; n/a = fewer than 20 non-seed agent first uses (or < 50 trees for P3a, which then counts as not tested and the verdict rests on P5: supported → mixed at best).

## Result
**mixed.** 5518 ideas, 9236 agent first uses, 5629 trees, N_room 10; R̂ = 0.391, contagion share R_c = 0.283, HR₁₀ = 3.63; P(s ≥ 2) = 0.226, largest tree 10.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 R̂ < 1 (upper CI < 1) | R̂ = 0.391 [0.375, 0.406] | critical R = 1 | pass |
| P2 R̂ < H03 n̂_talk | R̂ 0.391 vs n̂ 0.41; R_c = 0.283 | HH108: R̂ > n̂ | pass |
| P3a FN-GW band covers P(s ≥ 3), P(s ≥ 5) | P(s≥3) 0.128 (band 0.139–0.167); P(s≥5) 0.063 (band 0.033–0.049) | GW-NB band covers both: no | fail (s≥5 heavier than FN-GW) |
| P3b pure s^−3/2 rejected; τ_app ≥ 2 | LR 1624.0; τ_app 2.42 | critical branching | pass |
| P5 HR₁₀ > 1, lower CI > 1 (A2) | HR₁₀ = 3.63 [3.24, 4.06] (315 adoptions at k = 0) | field: HR₁₀ ≤ 1 | pass |
| P5a jitter excess (pre-registered; failed guard) | exposed 0.971 vs null 0.996, p = 1.00 | uninterpretable (S2) | n/a |
| P6 pooled HR(2 vs 1) ≤ 2.5 | 5.51 [4.75, 6.46] | complex > 3; heterogeneity inflates | ambiguous |
| P7 day-ahead 90% PI coverage (pre-registered FN-GW) | P(s≥2) 0.00, P(s≥3) 0.00 over 9 days | post-hoc V3: 0.33, 0.56 | fail |

**By idea class** (U artifact, D number, N name/coinage, W rare word):

| Class | ideas | agent nodes | R̂ [95% CI] | R_c | P(s ≥ 2) | P(s ≥ 3) | s_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D | 194 | 315 | 0.37 [0.30, 0.42] | 0.20 | 0.285 | 0.130 | 8 |
| N | 5084 | 8301 | 0.38 [0.36, 0.39] | 0.27 | 0.212 | 0.118 | 10 |
| U | 7 | 20 | 0.65 [0.30, 0.79] | 0.15 | 0.571 | 0.429 | 8 |
| W | 233 | 600 | 0.60 [0.55, 0.64] | 0.46 | 0.487 | 0.317 | 10 |

Data: `data/processed/H34-idea-cascades/G27/`. Figures: `../../figures/` (cross-period); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): HR₁₀ beats the field null (lower CI 3.24). D (unfitted shape): FN-GW band misses the tail; pure s^−3/2 rejected. E: no natural experiment inside this period was used.

## Notes
- Censoring check: R̂ without trees rooted on the last day = 0.403.
- Root vs non-root mean offspring 0.292 vs 0.544 (GW assumes equal).
- Root types: invented 0.98, from humans 0.002, field (unexposed) 0.019; 0.97 of non-seed first uses were visibly exposed.
