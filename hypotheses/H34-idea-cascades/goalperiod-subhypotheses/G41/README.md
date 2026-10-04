# H34 × G41: Perform novel research! (2026-05-11 → 2026-05-18)

**Verdict:** mixed
**Verdict (1b):** mixed (ledger visibility: R̂ 0.24, HR₁₀ 47.2 [40.4, 56.0], tail heavy; H57 placebo HR unread/seen 28.4/52.9)
**Role:** replication (exploratory)
**Period:** regime III · mode I · 15 agents at start (median room size 11) · 5 non-holdout days. Setup: Perform novel research. About 11 #rest agents independently proposed studying multi-agent coordination; #best studied AI-judge bias.

## Why this period
Secondary period for the cross-period criticality link (P4) and transfer of the forecast rule (P7). Mode I (each agent its own objective), regime III.

## Prediction
*Written 2026-10-04 02:00 UTC, before running on this period* (after the synthetic validation and amendments A1–A5 of the main card; no real cascade statistic had been computed for any period).

| # | Prediction here | Counts against |
| --- | --- | --- |
| P1 | R̂ < 1 with upper 95% CI < 1; typical 0.05–0.5 | lower CI ≥ 1 |
| P2 | R̂ < H03 n̂_talk = 0.31; R_c < R̂ | R̂ > n̂_talk beyond its CI |
| P3a (A1) | observed P(s ≥ 3) and P(s ≥ 5) inside the FN-GW 90% band (if ≥ 50 trees) | outside the band |
| P5 (A2) | contagion beyond the field: HR₁₀ > 1 with lower CI > 1 | HR₁₀ CI includes 1 or < 1 |
| P6 (A3) | pooled recency HR(2 vs 1) ≤ 2.5 (not complex) | HR(2 vs 1) > 3 with lower CI > 2.5 |

**Verdict rule (A2):** supported = P5 (HR₁₀ lower CI > 1) and P3a pass; failed = both fail, or R̂ lower CI ≥ 1; mixed = exactly one passes; n/a = fewer than 20 non-seed agent first uses (or < 50 trees for P3a, which then counts as not tested and the verdict rests on P5: supported → mixed at best).

## Result
**mixed.** 6020 ideas, 8027 agent first uses, 6150 trees, N_room 11; R̂ = 0.234, contagion share R_c = 0.227, HR₁₀ = 32.84; P(s ≥ 2) = 0.192, largest tree 10.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 R̂ < 1 (upper CI < 1) | R̂ = 0.234 [0.222, 0.245] | critical R = 1 | pass |
| P2 R̂ < H03 n̂_talk | R̂ 0.234 vs n̂ 0.31; R_c = 0.227 | HH108: R̂ > n̂ | pass |
| P3a FN-GW band covers P(s ≥ 3), P(s ≥ 5) | P(s≥3) 0.065 (band 0.055–0.074); P(s≥5) 0.011 (band 0.004–0.010) | GW-NB band covers both: yes | fail (s≥5 heavier than FN-GW) |
| P3b pure s^−3/2 rejected; τ_app ≥ 2 | LR 3350.8; τ_app 2.90 | critical branching | pass |
| P5 HR₁₀ > 1, lower CI > 1 (A2) | HR₁₀ = 32.84 [28.50, 37.52] (233 adoptions at k = 0) | field: HR₁₀ ≤ 1 | pass |
| P5a jitter excess (pre-registered; failed guard) | exposed 0.936 vs null 0.974, p = 1.00 | uninterpretable (S2) | n/a |
| P6 pooled HR(2 vs 1) ≤ 2.5 | 2.43 [2.06, 2.87] | complex > 3; heterogeneity inflates | pass |
| P5c cross-room ratio > 3 | 968.4 [304.1, 1051.2] (P(adopt) 0.040 vs 0.0000) | field ≈ 1–1.8 (S2) | pass (room fields confound) |
| P7 day-ahead 90% PI coverage (pre-registered FN-GW) | P(s≥2) 0.25, P(s≥3) 0.00 over 4 days | post-hoc V3: 0.75, 1.00 | fail |

**By idea class** (U artifact, D number, N name/coinage, W rare word):

| Class | ideas | agent nodes | R̂ [95% CI] | R_c | P(s ≥ 2) | P(s ≥ 3) | s_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D | 693 | 961 | 0.27 [0.24, 0.30] | 0.27 | 0.263 | 0.077 | 7 |
| N | 5228 | 6915 | 0.23 [0.21, 0.24] | 0.22 | 0.180 | 0.062 | 10 |
| U | 34 | 58 | 0.41 [0.24, 0.53] | 0.40 | 0.353 | 0.176 | 6 |
| W | 65 | 93 | 0.28 [0.17, 0.38] | 0.27 | 0.254 | 0.060 | 6 |

Data: `data/processed/H34-idea-cascades/G41/`. Figures: `../../figures/` (cross-period); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): HR₁₀ beats the field null (lower CI 28.50). D (unfitted shape): FN-GW band misses the tail; pure s^−3/2 rejected. G (rooms): never-exposed agents adopt far less (ratio 968.4), confounded by room fields. E: no natural experiment inside this period was used.

## Notes
- Two rooms active: the cross-room contrast is available but confounded by room-specific fields (rooms often worked on different projects).
- Censoring check: R̂ without trees rooted on the last day = 0.257.
- Root vs non-root mean offspring 0.217 vs 0.290 (GW assumes equal).
- Root types: invented 0.98, from humans 0.000, field (unexposed) 0.021; 0.94 of non-seed first uses were visibly exposed.
