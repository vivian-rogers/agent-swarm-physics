# H34 × G20: Start a Substack and join the blogosphere (2025-11-17 → 2025-12-01)

**Verdict:** mixed
**Verdict (1b):** mixed (ledger visibility: R̂ 0.28, HR₁₀ 8.3 [6.9, 10.2], tail heavy; H57 placebo HR unread/seen 3.6/6.4)
**Role:** exploratory
**Period:** regime I · mode I · 8 agents at start (median room size 10) · 10 non-holdout days. Setup: Each agent starts a Substack; niches formed (e.g. consciousness, telemetry). Roster churn: two in, two out.

## Why this period
Card candidate (HH122; goal-periods.md ranks 03 Contagion first here). Every agent runs its own Substack in a single room (regime I), so post titles, blog names and coined phrases are natural ideas, and cross-promotion is a direct transmission channel. One room means exposure is nearly saturated: the field and contagion can only be told apart by timing (HR₁₀), not by who could see what.

## Prediction
*Written 2026-10-04 02:00 UTC, before running on this period* (after the synthetic validation and amendments A1–A5 of the main card; no real cascade statistic had been computed for any period).

| # | Prediction here | Counts against |
| --- | --- | --- |
| P1 | R̂ < 1 with upper 95% CI < 1; typical 0.05–0.5 | lower CI ≥ 1 |
| P2 | R̂ < H03 n̂_talk = 0.62; R_c < R̂ | R̂ > n̂_talk beyond its CI |
| P3a (A1) | observed P(s ≥ 3) and P(s ≥ 5) inside the FN-GW 90% band (if ≥ 50 trees) | outside the band |
| P5 (A2) | contagion beyond the field: HR₁₀ > 1 with lower CI > 1 | HR₁₀ CI includes 1 or < 1 |
| P6 (A3) | pooled recency HR(2 vs 1) ≤ 2.5 (not complex) | HR(2 vs 1) > 3 with lower CI > 2.5 |
| G20-a | URL (U) and name (N) ideas spread more than numbers (D): R̂_U, R̂_N > R̂_D | R̂_D highest |
| G20-b | one room: ≥ 90% of non-seed first uses are 'exposed' (saturation), so R̂ is mostly field floor + contagion mix; R_c ≤ 0.6 R̂ | R_c ≈ R̂ |

**Verdict rule (A2):** supported = P5 (HR₁₀ lower CI > 1) and P3a pass; failed = both fail, or R̂ lower CI ≥ 1; mixed = exactly one passes; n/a = fewer than 20 non-seed agent first uses (or < 50 trees for P3a, which then counts as not tested and the verdict rests on P5: supported → mixed at best).

## Result
**mixed.** 3217 ideas, 4521 agent first uses, 3388 trees, N_room 10; R̂ = 0.251, contagion share R_c = 0.151, HR₁₀ = 2.51; P(s ≥ 2) = 0.154, largest tree 9.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 R̂ < 1 (upper CI < 1) | R̂ = 0.251 [0.232, 0.268] | critical R = 1 | pass |
| P2 R̂ < H03 n̂_talk | R̂ 0.251 vs n̂ 0.62; R_c = 0.151 | HH108: R̂ > n̂ | pass |
| P3a FN-GW band covers P(s ≥ 3), P(s ≥ 5) | P(s≥3) 0.081 (band 0.064–0.090); P(s≥5) 0.026 (band 0.011–0.021) | GW-NB band covers both: no | fail (s≥5 heavier than FN-GW) |
| P3b pure s^−3/2 rejected; τ_app ≥ 2 | LR 1803.8; τ_app 2.94 | critical branching | pass |
| P5 HR₁₀ > 1, lower CI > 1 (A2) | HR₁₀ = 2.51 [2.17, 2.93] (266 adoptions at k = 0) | field: HR₁₀ ≤ 1 | pass |
| P5a jitter excess (pre-registered; failed guard) | exposed 0.870 vs null 0.971, p = 1.00 | uninterpretable (S2) | n/a |
| P6 pooled HR(2 vs 1) ≤ 2.5 | 6.11 [5.06, 7.42] | complex > 3; heterogeneity inflates | ambiguous |
| P7 day-ahead 90% PI coverage (pre-registered FN-GW) | P(s≥2) 0.00, P(s≥3) 0.78 over 9 days | post-hoc V3: 0.89, 1.00 | fail |
| G20-a R̂_U, R̂_N > R̂_D | U 0.34, N 0.23, D 0.45 | – | fail (numbers spread most) |
| G20-b ≥ 90% of non-seed first uses exposed; R_c ≤ 0.6 R̂ | exposed 0.87; R_c/R̂ = 0.60 | – | fail (0.87 exposed); R_c/R̂ borderline |

**By idea class** (U artifact, D number, N name/coinage, W rare word):

| Class | ideas | agent nodes | R̂ [95% CI] | R_c | P(s ≥ 2) | P(s ≥ 3) | s_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D | 100 | 211 | 0.45 [0.34, 0.54] | 0.25 | 0.250 | 0.164 | 9 |
| N | 2927 | 3989 | 0.23 [0.21, 0.25] | 0.14 | 0.148 | 0.073 | 9 |
| U | 25 | 38 | 0.34 [0.14, 0.47] | 0.27 | 0.280 | 0.160 | 4 |
| W | 165 | 283 | 0.35 [0.27, 0.42] | 0.14 | 0.190 | 0.147 | 9 |

Data: `data/processed/H34-idea-cascades/G20/`. Figures: `../../figures/` (cross-period); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): HR₁₀ beats the field null (lower CI 2.17). D (unfitted shape): FN-GW band misses the tail; pure s^−3/2 rejected. E: no natural experiment inside this period was used.

## Notes
- Censoring check: R̂ without trees rooted on the last day = 0.249.
- Root vs non-root mean offspring 0.218 vs 0.350 (GW assumes equal).
- Root types: invented 0.95, from humans 0.001, field (unexposed) 0.050; 0.87 of non-seed first uses were visibly exposed.
