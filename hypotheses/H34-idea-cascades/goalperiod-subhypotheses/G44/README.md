# H34 × G44: Finetune your leader! (2026-05-26 → 2026-06-01)

**Verdict:** mixed
**Verdict (1b):** mixed (ledger visibility: R̂ 0.20, HR₁₀ 68.7 [54.6, 87.8], tail heavy; H57 placebo HR unread/seen 45.4/60.7)
**Role:** exploratory
**Period:** regime III · mode C · 16 agents at start (median room size 12) · 4 non-holdout days. Setup: #best (Opus 4.7, GPT-5.5, Gemini 3.5 Flash, Kimi K2.6) fine-tunes a Kimi model as leader; #rest picks its own goals. All #rest agents chose creative work, and tested which content survives consolidation.

## Why this period
Secondary period for the cross-period criticality link (P4) and transfer of the forecast rule (P7). Mode C (shared objective), regime III.

## Prediction
*Written 2026-10-04 02:00 UTC, before running on this period* (after the synthetic validation and amendments A1–A5 of the main card; no real cascade statistic had been computed for any period).

| # | Prediction here | Counts against |
| --- | --- | --- |
| P1 | R̂ < 1 with upper 95% CI < 1; typical 0.05–0.5 | lower CI ≥ 1 |
| P2 | R̂ < H03 n̂_talk = 0.25; R_c < R̂ | R̂ > n̂_talk beyond its CI |
| P3a (A1) | observed P(s ≥ 3) and P(s ≥ 5) inside the FN-GW 90% band (if ≥ 50 trees) | outside the band |
| P5 (A2) | contagion beyond the field: HR₁₀ > 1 with lower CI > 1 | HR₁₀ CI includes 1 or < 1 |
| P6 (A3) | pooled recency HR(2 vs 1) ≤ 2.5 (not complex) | HR(2 vs 1) > 3 with lower CI > 2.5 |

**Verdict rule (A2):** supported = P5 (HR₁₀ lower CI > 1) and P3a pass; failed = both fail, or R̂ lower CI ≥ 1; mixed = exactly one passes; n/a = fewer than 20 non-seed agent first uses (or < 50 trees for P3a, which then counts as not tested and the verdict rests on P5: supported → mixed at best).

## Result
**mixed.** 2881 ideas, 3643 agent first uses, 2917 trees, N_room 12; R̂ = 0.199, contagion share R_c = 0.196, HR₁₀ = 62.50; P(s ≥ 2) = 0.163, largest tree 7.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 R̂ < 1 (upper CI < 1) | R̂ = 0.199 [0.183, 0.214] | critical R = 1 | pass |
| P2 R̂ < H03 n̂_talk | R̂ 0.199 vs n̂ 0.25; R_c = 0.196 | HH108: R̂ > n̂ | pass |
| P3a FN-GW band covers P(s ≥ 3), P(s ≥ 5) | P(s≥3) 0.050 (band 0.040–0.059); P(s≥5) 0.010 (band 0.002–0.008) | GW-NB band covers both: no | fail (s≥5 heavier than FN-GW) |
| P3b pure s^−3/2 rejected; τ_app ≥ 2 | LR 1900.1; τ_app 3.10 | critical branching | pass |
| P5 HR₁₀ > 1, lower CI > 1 (A2) | HR₁₀ = 62.50 [49.40, 79.44] (85 adoptions at k = 0) | field: HR₁₀ ≤ 1 | pass |
| P5a jitter excess (pre-registered; failed guard) | exposed 0.958 vs null 0.981, p = 1.00 | uninterpretable (S2) | n/a |
| P6 pooled HR(2 vs 1) ≤ 2.5 | 2.43 [1.85, 3.09] | complex > 3; heterogeneity inflates | pass |
| P5c cross-room ratio > 3 | 130.6 [64.1, 528.3] (P(adopt) 0.030 vs 0.0002) | field ≈ 1–1.8 (S2) | pass (room fields confound) |
| P7 day-ahead 90% PI coverage (pre-registered FN-GW) | P(s≥2) 0.00, P(s≥3) 0.67 over 3 days | post-hoc V3: 1.00, 1.00 | fail |

**By idea class** (U artifact, D number, N name/coinage, W rare word):

| Class | ideas | agent nodes | R̂ [95% CI] | R_c | P(s ≥ 2) | P(s ≥ 3) | s_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D | 123 | 160 | 0.23 [0.15, 0.30] | 0.22 | 0.202 | 0.056 | 7 |
| N | 2634 | 3279 | 0.19 [0.17, 0.20] | 0.19 | 0.155 | 0.045 | 7 |
| U | 72 | 113 | 0.32 [0.22, 0.40] | 0.28 | 0.286 | 0.130 | 6 |
| W | 52 | 91 | 0.37 [0.25, 0.46] | 0.36 | 0.316 | 0.158 | 5 |

Data: `data/processed/H34-idea-cascades/G44/`. Figures: `../../figures/` (cross-period); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): HR₁₀ beats the field null (lower CI 49.40). D (unfitted shape): FN-GW band misses the tail; pure s^−3/2 rejected. G (rooms): never-exposed agents adopt far less (ratio 130.6), confounded by room fields. E: no natural experiment inside this period was used.

## Notes
- Two rooms active: the cross-room contrast is available but confounded by room-specific fields (rooms often worked on different projects).
- Censoring check: R̂ without trees rooted on the last day = 0.184.
- Root vs non-root mean offspring 0.184 vs 0.260 (GW assumes equal).
- Root types: invented 0.99, from humans 0.004, field (unexposed) 0.011; 0.96 of non-seed first uses were visibly exposed.
