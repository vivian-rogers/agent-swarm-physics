# H34 × G10: Complete as many games as you can in a week! (2025-08-18 → 2025-08-25)

**Verdict:** mixed
**Verdict (1b):** supported (ledger visibility: R̂ 0.19, HR₁₀ 9.7 [4.3, 25.8], tail ok; H57 placebo HR unread/seen 3.5/20.3)
**Role:** replication (exploratory)
**Period:** regime I · mode I · 7 agents at start (median room size 7) · 5 non-holdout days. Setup: Complete as many games as possible (turn-based, since real-time games are hard to play through screenshots). GPT-5, Grok 4 and Claude Opus 4.1 joined; N jumps from 4 to 7.

## Why this period
Secondary period for the cross-period criticality link (P4) and transfer of the forecast rule (P7). Mode I (each agent its own objective), regime I.

## Prediction
*Written 2026-10-04 02:00 UTC, before running on this period* (after the synthetic validation and amendments A1–A5 of the main card; no real cascade statistic had been computed for any period).

| # | Prediction here | Counts against |
| --- | --- | --- |
| P1 | R̂ < 1 with upper 95% CI < 1; typical 0.05–0.5 | lower CI ≥ 1 |
| P2 | R̂ < H03 n̂_talk = 0.22; R_c < R̂ | R̂ > n̂_talk beyond its CI |
| P3a (A1) | observed P(s ≥ 3) and P(s ≥ 5) inside the FN-GW 90% band (if ≥ 50 trees) | outside the band |
| P5 (A2) | contagion beyond the field: HR₁₀ > 1 with lower CI > 1 | HR₁₀ CI includes 1 or < 1 |
| P6 (A3) | pooled recency HR(2 vs 1) ≤ 2.5 (not complex) | HR(2 vs 1) > 3 with lower CI > 2.5 |

**Verdict rule (A2):** supported = P5 (HR₁₀ lower CI > 1) and P3a pass; failed = both fail, or R̂ lower CI ≥ 1; mixed = exactly one passes; n/a = fewer than 20 non-seed agent first uses (or < 50 trees for P3a, which then counts as not tested and the verdict rests on P5: supported → mixed at best).

## Result
**mixed.** 289 ideas, 356 agent first uses, 294 trees, N_room 7; R̂ = 0.174, contagion share R_c = 0.138, HR₁₀ = 4.85; P(s ≥ 2) = 0.146, largest tree 5.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 R̂ < 1 (upper CI < 1) | R̂ = 0.174 [0.127, 0.220] | critical R = 1 | pass |
| P2 R̂ < H03 n̂_talk | R̂ 0.174 vs n̂ 0.22; R_c = 0.138 | HH108: R̂ > n̂ | pass |
| P3a FN-GW band covers P(s ≥ 3), P(s ≥ 5) | P(s≥3) 0.037 (band 0.017–0.078); P(s≥5) 0.014 (band 0.000–0.010) | GW-NB band covers both: yes | fail (s≥5 heavier than FN-GW) |
| P3b pure s^−3/2 rejected; τ_app ≥ 2 | LR 161.3; τ_app 3.20 | critical branching | pass |
| P5 HR₁₀ > 1, lower CI > 1 (A2) | HR₁₀ = 4.85 [2.40, 10.23] (11 adoptions at k = 0) | field: HR₁₀ ≤ 1 | pass |
| P5a jitter excess (pre-registered; failed guard) | exposed 0.925 vs null 0.977, p = 0.97 | uninterpretable (S2) | n/a |
| P6 pooled HR(2 vs 1) ≤ 2.5 | 2.32 [0.00, 6.27] | complex > 3; heterogeneity inflates | pass |
| P7 day-ahead 90% PI coverage (pre-registered FN-GW) | P(s≥2) 0.75, P(s≥3) 0.25 over 4 days | post-hoc V3: 0.75, 0.75 | fail |

**By idea class** (U artifact, D number, N name/coinage, W rare word):

| Class | ideas | agent nodes | R̂ [95% CI] | R_c | P(s ≥ 2) | P(s ≥ 3) | s_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D | 137 | 178 | 0.21 [0.14, 0.28] | 0.19 | 0.200 | 0.043 | 5 |
| N | 136 | 157 | 0.12 [0.05, 0.20] | 0.03 | 0.072 | 0.036 | 5 |
| U | 1 | 1 | 0.00 [0.00, 0.00] | – | 0.000 | 0.000 | 1 |
| W | 15 | 20 | 0.25 [0.12, 0.38] | 0.19 | 0.333 | 0.000 | 2 |

Data: `data/processed/H34-idea-cascades/G10/`. Figures: `../../figures/` (cross-period); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): HR₁₀ beats the field null (lower CI 2.40). D (unfitted shape): FN-GW band misses the tail; pure s^−3/2 rejected. E: no natural experiment inside this period was used.

## Notes
- Censoring check: R̂ without trees rooted on the last day = 0.190.
- Root vs non-root mean offspring 0.170 vs 0.194 (GW assumes equal).
- Root types: invented 0.98, from humans 0.000, field (unexposed) 0.017; 0.93 of non-seed first uses were visibly exposed.
