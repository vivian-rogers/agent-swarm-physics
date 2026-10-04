# H34 × G39: Build your own interactive world! (2026-04-27 → 2026-05-04)

**Verdict:** mixed
**Verdict (1b):** mixed (ledger visibility: R̂ 0.09, HR₁₀ 8.0 [5.9, 11.3], tail heavy; H57 placebo HR unread/seen 4.5/12.6)
**Role:** exploratory
**Period:** regime III · mode I · 15 agents at start (median room size 11) · 5 non-holdout days. Setup: Each agent builds an interactive world (a webpage visitors can mark). GPT-5.5 joined; rooms reshuffled.

## Why this period
Secondary period for the cross-period criticality link (P4) and transfer of the forecast rule (P7). Mode I (each agent its own objective), regime III.

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
**mixed.** 3170 ideas, 3487 agent first uses, 3185 trees, N_room 11; R̂ = 0.087, contagion share R_c = 0.075, HR₁₀ = 7.18; P(s ≥ 2) = 0.067, largest tree 8.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 R̂ < 1 (upper CI < 1) | R̂ = 0.087 [0.073, 0.100] | critical R = 1 | pass |
| P2 R̂ < H03 n̂_talk | R̂ 0.087 vs n̂ 0.10; R_c = 0.075 | HH108: R̂ > n̂ | pass |
| P3a FN-GW band covers P(s ≥ 3), P(s ≥ 5) | P(s≥3) 0.014 (band 0.008–0.021); P(s≥5) 0.003 (band 0.000–0.002) | GW-NB band covers both: no | fail (s≥5 heavier than FN-GW) |
| P3b pure s^−3/2 rejected; τ_app ≥ 2 | LR 3112.0; τ_app 4.16 | critical branching | pass |
| P5 HR₁₀ > 1, lower CI > 1 (A2) | HR₁₀ = 7.18 [5.34, 9.97] (49 adoptions at k = 0) | field: HR₁₀ ≤ 1 | pass |
| P5a jitter excess (pre-registered; failed guard) | exposed 0.959 vs null 0.968, p = 0.94 | uninterpretable (S2) | n/a |
| P6 pooled HR(2 vs 1) ≤ 2.5 | 3.68 [2.05, 5.89] | complex > 3; heterogeneity inflates | ambiguous |
| P5c cross-room ratio > 3 | 28.3 [13.4, 88.8] (P(adopt) 0.008 vs 0.0003) | field ≈ 1–1.8 (S2) | pass (room fields confound) |
| P7 day-ahead 90% PI coverage (pre-registered FN-GW) | P(s≥2) 0.25, P(s≥3) 0.25 over 4 days | post-hoc V3: 0.25, 0.25 | fail |

**By idea class** (U artifact, D number, N name/coinage, W rare word):

| Class | ideas | agent nodes | R̂ [95% CI] | R_c | P(s ≥ 2) | P(s ≥ 3) | s_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D | 351 | 441 | 0.19 [0.16, 0.23] | 0.17 | 0.188 | 0.039 | 5 |
| N | 2686 | 2886 | 0.07 [0.05, 0.08] | 0.06 | 0.047 | 0.010 | 8 |
| U | 40 | 57 | 0.30 [0.15, 0.43] | 0.00 | 0.275 | 0.075 | 6 |
| W | 93 | 103 | 0.09 [0.03, 0.16] | 0.05 | 0.074 | 0.011 | 4 |

Data: `data/processed/H34-idea-cascades/G39/`. Figures: `../../figures/` (cross-period); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): HR₁₀ beats the field null (lower CI 5.34). D (unfitted shape): FN-GW band misses the tail; pure s^−3/2 rejected. G (rooms): never-exposed agents adopt far less (ratio 28.3), confounded by room fields. E: no natural experiment inside this period was used.

## Notes
- Two rooms active: the cross-room contrast is available but confounded by room-specific fields (rooms often worked on different projects).
- Censoring check: R̂ without trees rooted on the last day = 0.099.
- Root vs non-root mean offspring 0.074 vs 0.222 (GW assumes equal).
- Root types: invented 1.00, from humans 0.001, field (unexposed) 0.004; 0.96 of non-seed first uses were visibly exposed.
