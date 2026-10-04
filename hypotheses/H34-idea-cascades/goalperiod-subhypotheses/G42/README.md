# H34 × G42: Run your own Youtube channel! (2026-05-18 → 2026-05-25)

**Verdict:** supported
**Verdict (1b):** supported (ledger visibility: R̂ 0.13, HR₁₀ 49.8 [38.5, 66.7], tail ok; H57 placebo HR unread/seen 13.3/47.1)
**Role:** replication (exploratory)
**Period:** regime III · mode I · 15 agents at start (median room size 11) · 5 non-holdout days. Setup: Each agent runs a YouTube channel (1–10 videos); several agents read "1–10" as "10".

## Why this period
Card candidate (03 Contagion ranked first: the "1–10 means 10" reading spread between agents). Two rooms (#best / #rest) give a never-exposed control group for the cross-room field contrast (P5c), the cleanest contagion-vs-field design available outside the holdout.

## Prediction
*Written 2026-10-04 02:00 UTC, before running on this period* (after the synthetic validation and amendments A1–A5 of the main card; no real cascade statistic had been computed for any period).

| # | Prediction here | Counts against |
| --- | --- | --- |
| P1 | R̂ < 1 with upper 95% CI < 1; typical 0.05–0.5 | lower CI ≥ 1 |
| P2 | R̂ < H03 n̂_talk = 0.20; R_c < R̂ | R̂ > n̂_talk beyond its CI |
| P3a (A1) | observed P(s ≥ 3) and P(s ≥ 5) inside the FN-GW 90% band (if ≥ 50 trees) | outside the band |
| P5 (A2) | contagion beyond the field: HR₁₀ > 1 with lower CI > 1 | HR₁₀ CI includes 1 or < 1 |
| P6 (A3) | pooled recency HR(2 vs 1) ≤ 2.5 (not complex) | HR(2 vs 1) > 3 with lower CI > 2.5 |
| G42-a | cross-room contrast: P(adopt \| exposed) / P(adopt \| never exposed) > 3 (P5c) | ratio ≤ 2 (the field) |
| G42-b | low branching (mode I, separate channels): R̂ ≤ 0.3 | R̂ > 0.5 |

**Verdict rule (A2):** supported = P5 (HR₁₀ lower CI > 1) and P3a pass; failed = both fail, or R̂ lower CI ≥ 1; mixed = exactly one passes; n/a = fewer than 20 non-seed agent first uses (or < 50 trees for P3a, which then counts as not tested and the verdict rests on P5: supported → mixed at best).

## Result
**supported.** 3914 ideas, 4551 agent first uses, 3944 trees, N_room 11; R̂ = 0.133, contagion share R_c = 0.130, HR₁₀ = 45.16; P(s ≥ 2) = 0.111, largest tree 9.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 R̂ < 1 (upper CI < 1) | R̂ = 0.133 [0.121, 0.146] | critical R = 1 | pass |
| P2 R̂ < H03 n̂_talk | R̂ 0.133 vs n̂ 0.20; R_c = 0.130 | HH108: R̂ > n̂ | pass |
| P3a FN-GW band covers P(s ≥ 3), P(s ≥ 5) | P(s≥3) 0.030 (band 0.021–0.031); P(s≥5) 0.003 (band 0.001–0.004) | GW-NB band covers both: yes | pass |
| P3b pure s^−3/2 rejected; τ_app ≥ 2 | LR 3180.3; τ_app 3.57 | critical branching | pass |
| P5 HR₁₀ > 1, lower CI > 1 (A2) | HR₁₀ = 45.16 [34.81, 58.85] (61 adoptions at k = 0) | field: HR₁₀ ≤ 1 | pass |
| P5a jitter excess (pre-registered; failed guard) | exposed 0.955 vs null 0.957, p = 0.66 | uninterpretable (S2) | n/a |
| P6 pooled HR(2 vs 1) ≤ 2.5 | 3.10 [2.26, 3.97] | complex > 3; heterogeneity inflates | ambiguous |
| P5c cross-room ratio > 3 | 80.7 [40.3, 391.0] (P(adopt) 0.019 vs 0.0002) | field ≈ 1–1.8 (S2) | pass (room fields confound) |
| P7 day-ahead 90% PI coverage (pre-registered FN-GW) | P(s≥2) 0.00, P(s≥3) 0.50 over 4 days | post-hoc V3: 0.50, 1.00 | fail |
| G42-a cross-room ratio > 3 | 80.7 [40.3, 391.0] | field ≈ 1–1.8 (S2) | pass (room fields confound) |
| G42-b R̂ ≤ 0.3 | 0.133 | – | pass |

**By idea class** (U artifact, D number, N name/coinage, W rare word):

| Class | ideas | agent nodes | R̂ [95% CI] | R_c | P(s ≥ 2) | P(s ≥ 3) | s_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D | 101 | 106 | 0.05 [0.01, 0.08] | 0.05 | 0.050 | 0.000 | 2 |
| N | 3683 | 4249 | 0.13 [0.12, 0.14] | 0.13 | 0.108 | 0.029 | 9 |
| U | 22 | 27 | 0.11 [0.00, 0.24] | 0.00 | 0.125 | 0.000 | 2 |
| W | 108 | 169 | 0.30 [0.21, 0.37] | 0.28 | 0.252 | 0.101 | 5 |

Data: `data/processed/H34-idea-cascades/G42/`. Figures: `../../figures/` (cross-period); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): HR₁₀ beats the field null (lower CI 34.81). D (unfitted shape): FN-GW band covers the tail; pure s^−3/2 rejected. G (rooms): never-exposed agents adopt far less (ratio 80.7), confounded by room fields. E: no natural experiment inside this period was used.

## Notes
- Two rooms active: the cross-room contrast is available but confounded by room-specific fields (rooms often worked on different projects).
- Censoring check: R̂ without trees rooted on the last day = 0.141.
- Root vs non-root mean offspring 0.124 vs 0.193 (GW assumes equal).
- Root types: invented 0.99, from humans 0.001, field (unexposed) 0.007; 0.95 of non-seed first uses were visibly exposed.
