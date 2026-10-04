# H34 × G36: Interact with other AI agents outside the Village! (2026-03-23 → 2026-03-30)

**Verdict:** mixed
**Verdict (1b):** mixed (ledger visibility: R̂ 0.23, HR₁₀ 14.7 [12.8, 16.9], tail heavy; H57 placebo HR unread/seen 1.3/18.4)
**Role:** exploratory
**Period:** regime II · mode C · 13 agents at start (median room size 8) · 5 non-holdout days. Setup: Interact with AI agents outside the Village: teams, public repos. **Perma-computer-use (F) lands mid-goal** (2026-03-24).

## Why this period
Secondary period for the cross-period criticality link (P4) and transfer of the forecast rule (P7). Mode C (shared objective), regime II.

## Prediction
*Written 2026-10-04 02:00 UTC, before running on this period* (after the synthetic validation and amendments A1–A5 of the main card; no real cascade statistic had been computed for any period).

| # | Prediction here | Counts against |
| --- | --- | --- |
| P1 | R̂ < 1 with upper 95% CI < 1; typical 0.05–0.5 | lower CI ≥ 1 |
| P2 | R̂ < H03 n̂_talk = 0.29; R_c < R̂ | R̂ > n̂_talk beyond its CI |
| P3a (A1) | observed P(s ≥ 3) and P(s ≥ 5) inside the FN-GW 90% band (if ≥ 50 trees) | outside the band |
| P5 (A2) | contagion beyond the field: HR₁₀ > 1 with lower CI > 1 | HR₁₀ CI includes 1 or < 1 |
| P6 (A3) | pooled recency HR(2 vs 1) ≤ 2.5 (not complex) | HR(2 vs 1) > 3 with lower CI > 2.5 |

**Verdict rule (A2):** supported = P5 (HR₁₀ lower CI > 1) and P3a pass; failed = both fail, or R̂ lower CI ≥ 1; mixed = exactly one passes; n/a = fewer than 20 non-seed agent first uses (or < 50 trees for P3a, which then counts as not tested and the verdict rests on P5: supported → mixed at best).

## Result
**mixed.** 3850 ideas, 5210 agent first uses, 4076 trees, N_room 8; R̂ = 0.224, contagion share R_c = 0.209, HR₁₀ = 14.23; P(s ≥ 2) = 0.165, largest tree 9.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 R̂ < 1 (upper CI < 1) | R̂ = 0.224 [0.208, 0.241] | critical R = 1 | pass |
| P2 R̂ < H03 n̂_talk | R̂ 0.224 vs n̂ 0.29; R_c = 0.209 | HH108: R̂ > n̂ | pass |
| P3a FN-GW band covers P(s ≥ 3), P(s ≥ 5) | P(s≥3) 0.062 (band 0.052–0.070); P(s≥5) 0.013 (band 0.004–0.010) | GW-NB band covers both: no | fail (s≥5 heavier than FN-GW) |
| P3b pure s^−3/2 rejected; τ_app ≥ 2 | LR 2183.6; τ_app 3.01 | critical branching | pass |
| P5 HR₁₀ > 1, lower CI > 1 (A2) | HR₁₀ = 14.23 [12.49, 16.04] (308 adoptions at k = 0) | field: HR₁₀ ≤ 1 | pass |
| P5a jitter excess (pre-registered; failed guard) | exposed 0.846 vs null 0.848, p = 0.62 | uninterpretable (S2) | n/a |
| P6 pooled HR(2 vs 1) ≤ 2.5 | 3.27 [2.73, 3.89] | complex > 3; heterogeneity inflates | ambiguous |
| P5c cross-room ratio > 3 | 13.4 [10.9, 17.1] (P(adopt) 0.062 vs 0.0046) | field ≈ 1–1.8 (S2) | pass (room fields confound) |
| P7 day-ahead 90% PI coverage (pre-registered FN-GW) | P(s≥2) 0.50, P(s≥3) 0.25 over 4 days | post-hoc V3: 0.50, 0.75 | fail |

**By idea class** (U artifact, D number, N name/coinage, W rare word):

| Class | ideas | agent nodes | R̂ [95% CI] | R_c | P(s ≥ 2) | P(s ≥ 3) | s_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D | 166 | 231 | 0.27 [0.19, 0.33] | 0.26 | 0.194 | 0.088 | 6 |
| N | 2930 | 3995 | 0.23 [0.21, 0.25] | 0.21 | 0.171 | 0.063 | 9 |
| U | 79 | 133 | 0.34 [0.23, 0.44] | 0.25 | 0.273 | 0.148 | 8 |
| W | 675 | 851 | 0.18 [0.14, 0.22] | 0.17 | 0.121 | 0.043 | 8 |

Data: `data/processed/H34-idea-cascades/G36/`. Figures: `../../figures/` (cross-period); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): HR₁₀ beats the field null (lower CI 12.49). D (unfitted shape): FN-GW band misses the tail; pure s^−3/2 rejected. G (rooms): never-exposed agents adopt far less (ratio 13.4), confounded by room fields. E: no natural experiment inside this period was used.

## Notes
- Two rooms active: the cross-room contrast is available but confounded by room-specific fields (rooms often worked on different projects).
- Censoring check: R̂ without trees rooted on the last day = 0.230.
- Root vs non-root mean offspring 0.193 vs 0.307 (GW assumes equal).
- Root types: invented 0.94, from humans 0.010, field (unexposed) 0.052; 0.85 of non-seed first uses were visibly exposed.
