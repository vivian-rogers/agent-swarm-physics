# H34 × G40: Connect your worlds into a 3D universe! (2026-05-04 → 2026-05-11)

**Verdict:** mixed
**Verdict (1b):** mixed (ledger visibility: R̂ 0.24, HR₁₀ 19.3 [16.4, 22.8], tail heavy; H57 placebo HR unread/seen 27.2/33.6)
**Role:** exploratory
**Period:** regime III · mode C · 15 agents at start (median room size 14) · 5 non-holdout days. Setup: Connect the worlds into one 3D universe; about 15 agents coordinated in a dedicated #universe-coordination room.

## Why this period
Secondary period for the cross-period criticality link (P4) and transfer of the forecast rule (P7). Mode C (shared objective), regime III.

## Prediction
*Written 2026-10-04 02:00 UTC, before running on this period* (after the synthetic validation and amendments A1–A5 of the main card; no real cascade statistic had been computed for any period).

| # | Prediction here | Counts against |
| --- | --- | --- |
| P1 | R̂ < 1 with upper 95% CI < 1; typical 0.05–0.5 | lower CI ≥ 1 |
| P2 | R̂ < H03 n̂_talk = 0.00; R_c < R̂ | R̂ > n̂_talk beyond its CI |
| P3a (A1) | observed P(s ≥ 3) and P(s ≥ 5) inside the FN-GW 90% band (if ≥ 50 trees) | outside the band |
| P5 (A2) | contagion beyond the field: HR₁₀ > 1 with lower CI > 1 | HR₁₀ CI includes 1 or < 1 |
| P6 (A3) | pooled recency HR(2 vs 1) ≤ 2.5 (not complex) | HR(2 vs 1) > 3 with lower CI > 2.5 |

**Verdict rule (A2):** supported = P5 (HR₁₀ lower CI > 1) and P3a pass; failed = both fail, or R̂ lower CI ≥ 1; mixed = exactly one passes; n/a = fewer than 20 non-seed agent first uses (or < 50 trees for P3a, which then counts as not tested and the verdict rests on P5: supported → mixed at best).

## Result
**mixed.** 6042 ideas, 7996 agent first uses, 6100 trees, N_room 14; R̂ = 0.237, contagion share R_c = 0.224, HR₁₀ = 18.51; P(s ≥ 2) = 0.170, largest tree 11.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 R̂ < 1 (upper CI < 1) | R̂ = 0.237 [0.224, 0.251] | critical R = 1 | pass |
| P2 R̂ < H03 n̂_talk | R̂ 0.237 vs n̂ 0.00; R_c = 0.224 | HH108: R̂ > n̂ | fail |
| P3a FN-GW band covers P(s ≥ 3), P(s ≥ 5) | P(s≥3) 0.069 (band 0.058–0.074); P(s≥5) 0.018 (band 0.006–0.012) | GW-NB band covers both: no | fail (s≥5 heavier than FN-GW) |
| P3b pure s^−3/2 rejected; τ_app ≥ 2 | LR 3780.5; τ_app 2.97 | critical branching | pass |
| P5 HR₁₀ > 1, lower CI > 1 (A2) | HR₁₀ = 18.51 [15.64, 22.20] (132 adoptions at k = 0) | field: HR₁₀ ≤ 1 | pass |
| P5a jitter excess (pre-registered; failed guard) | exposed 0.972 vs null 0.994, p = 1.00 | uninterpretable (S2) | n/a |
| P6 pooled HR(2 vs 1) ≤ 2.5 | 3.67 [3.13, 4.28] | complex > 3; heterogeneity inflates | ambiguous |
| P5c cross-room ratio > 3 | ∞ [–, –] (P(adopt) 0.024 vs 0.0000) | field ≈ 1–1.8 (S2) | pass (room fields confound) |
| P7 day-ahead 90% PI coverage (pre-registered FN-GW) | P(s≥2) 0.50, P(s≥3) 0.00 over 4 days | post-hoc V3: 0.50, 0.50 | fail |

**By idea class** (U artifact, D number, N name/coinage, W rare word):

| Class | ideas | agent nodes | R̂ [95% CI] | R_c | P(s ≥ 2) | P(s ≥ 3) | s_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D | 856 | 1594 | 0.45 [0.42, 0.47] | 0.42 | 0.385 | 0.206 | 8 |
| N | 4951 | 6064 | 0.18 [0.17, 0.19] | 0.17 | 0.130 | 0.044 | 10 |
| U | 18 | 36 | 0.50 [0.00, 0.71] | 0.50 | 0.111 | 0.111 | 11 |
| W | 217 | 302 | 0.28 [0.21, 0.35] | 0.26 | 0.212 | 0.088 | 7 |

Data: `data/processed/H34-idea-cascades/G40/`. Figures: `../../figures/` (cross-period); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): HR₁₀ beats the field null (lower CI 15.64). D (unfitted shape): FN-GW band misses the tail; pure s^−3/2 rejected. G (rooms): never-exposed agents adopt far less (ratio ∞), confounded by room fields. E: no natural experiment inside this period was used.

## Notes
- Two rooms active: the cross-room contrast is available but confounded by room-specific fields (rooms often worked on different projects).
- Censoring check: R̂ without trees rooted on the last day = 0.232.
- Root vs non-root mean offspring 0.198 vs 0.364 (GW assumes equal).
- Root types: invented 0.99, from humans 0.001, field (unexposed) 0.009; 0.97 of non-seed first uses were visibly exposed.
