# H34 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 2026-09-20)

**Verdict:** mixed
**Verdict (1b):** mixed (ledger visibility: R̂ 0.23, HR₁₀ 26.3 [23.9, 29.2], tail heavy; H57 placebo HR unread/seen 8.8/49.4)
**Role:** exploratory
**Period:** regime III · mode I/K · 21 agents at start (median room size 25) · 45 non-holdout days. Setup: Standing goal: each agent maximizes a private assigned role (Table IV of the overview). 21 → 32 agents, 8 h/day, the longest stationary-ish window in the data (~12k agent-hours). Some roles are held by two agents (direct competition). Humans occasionally reassign roles.

## Why this period
Card candidate and the largest sample (≈ 45 non-holdout days, 21–29 agents, 8 h/day, private roles). It has the most ideas and trees, so the tail shape (FN-GW band, τ_app) and the day-ahead forecast rule are best powered here. Side rooms (GPT-5.6 isolation 07-09/10, #focus 08-05 → 08-24) add some never-exposed agents.

## Prediction
*Written 2026-10-04 02:00 UTC, before running on this period* (after the synthetic validation and amendments A1–A5 of the main card; no real cascade statistic had been computed for any period).

| # | Prediction here | Counts against |
| --- | --- | --- |
| P1 | R̂ < 1 with upper 95% CI < 1; typical 0.05–0.5 | lower CI ≥ 1 |
| P2 | R̂ < H03 n̂_talk = 0.54; R_c < R̂ | R̂ > n̂_talk beyond its CI |
| P3a (A1) | observed P(s ≥ 3) and P(s ≥ 5) inside the FN-GW 90% band (if ≥ 50 trees) | outside the band |
| P5 (A2) | contagion beyond the field: HR₁₀ > 1 with lower CI > 1 | HR₁₀ CI includes 1 or < 1 |
| P6 (A3) | pooled recency HR(2 vs 1) ≤ 2.5 (not complex) | HR(2 vs 1) > 3 with lower CI > 2.5 |
| G51-a | the largest tree-count period: pure s^−3/2 rejected (LR p < 0.05); τ_app ≥ 2 (⇔ R ≲ 0.5 by S1) | s^−3/2 not rejected |
| G51-b | day-ahead FN-GW forecasts cover the observed P(s ≥ 2) and P(s ≥ 3) on ≥ 80% of days with ≥ 20 trees (P7) | coverage < 70% |

**Verdict rule (A2):** supported = P5 (HR₁₀ lower CI > 1) and P3a pass; failed = both fail, or R̂ lower CI ≥ 1; mixed = exactly one passes; n/a = fewer than 20 non-seed agent first uses (or < 50 trees for P3a, which then counts as not tested and the verdict rests on P5: supported → mixed at best).

## Result
**mixed.** 51867 ideas, 68527 agent first uses, 53355 trees, N_room 25; R̂ = 0.221, contagion share R_c = 0.209, HR₁₀ = 18.35; P(s ≥ 2) = 0.179, largest tree 26.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 R̂ < 1 (upper CI < 1) | R̂ = 0.221 [0.217, 0.225] | critical R = 1 | pass |
| P2 R̂ < H03 n̂_talk | R̂ 0.221 vs n̂ 0.54; R_c = 0.209 | HH108: R̂ > n̂ | pass |
| P3a FN-GW band covers P(s ≥ 3), P(s ≥ 5) | P(s≥3) 0.055 (band 0.051–0.063); P(s≥5) 0.012 (band 0.006–0.009) | GW-NB band covers both: no | fail (s≥5 heavier than FN-GW) |
| P3b pure s^−3/2 rejected; τ_app ≥ 2 | LR 40959.2; τ_app 3.03 | critical branching | pass |
| P5 HR₁₀ > 1, lower CI > 1 (A2) | HR₁₀ = 18.35 [16.86, 20.09] (591 adoptions at k = 0) | field: HR₁₀ ≤ 1 | pass |
| P5a jitter excess (pre-registered; failed guard) | exposed 0.911 vs null 0.933, p = 1.00 | uninterpretable (S2) | n/a |
| P6 pooled HR(2 vs 1) ≤ 2.5 | 1.31 [1.16, 1.46] | complex > 3; heterogeneity inflates | pass |
| P7 day-ahead 90% PI coverage (pre-registered FN-GW) | P(s≥2) 0.32, P(s≥3) 0.41 over 44 days | post-hoc V3: 0.91, 0.95 | fail |
| G51-a pure s^−3/2 rejected; τ_app ≥ 2 | LR 40959; τ_app 3.03 | – | pass |
| G51-b day-ahead coverage ≥ 80% (P7) | P(s≥2) 0.32, P(s≥3) 0.41 | post-hoc V3: 0.91, 0.95 | fail (post-hoc V3 passes) |

**By idea class** (U artifact, D number, N name/coinage, W rare word):

| Class | ideas | agent nodes | R̂ [95% CI] | R_c | P(s ≥ 2) | P(s ≥ 3) | s_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D | 6119 | 11187 | 0.38 [0.37, 0.39] | 0.36 | 0.378 | 0.133 | 16 |
| N | 43737 | 54232 | 0.18 [0.18, 0.19] | 0.17 | 0.145 | 0.041 | 26 |
| U | 599 | 953 | 0.36 [0.31, 0.40] | 0.30 | 0.213 | 0.111 | 12 |
| W | 1412 | 2155 | 0.32 [0.30, 0.35] | 0.30 | 0.249 | 0.088 | 21 |

Data: `data/processed/H34-idea-cascades/G51/`. Figures: `../../figures/` (cross-period); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): HR₁₀ beats the field null (lower CI 16.86). D (unfitted shape): FN-GW band misses the tail; pure s^−3/2 rejected. E: no natural experiment inside this period was used.

## Notes
- Censoring check: R̂ without trees rooted on the last day = 0.221.
- Root vs non-root mean offspring 0.206 vs 0.276 (GW assumes equal).
- Root types: invented 0.97, from humans 0.000, field (unexposed) 0.028; 0.91 of non-seed first uses were visibly exposed.
