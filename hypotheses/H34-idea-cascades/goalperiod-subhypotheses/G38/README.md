# H34 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 2026-04-27)

**Verdict:** mixed
**Verdict (1b):** mixed (ledger visibility: R̂ 0.26, HR₁₀ 119.8 [102.0, 141.2], tail heavy; H57 placebo HR unread/seen 42.5/138.8)
**Round 2 (2026-10-05):** replication only; the 1b verdict stands. Gamma-mixed branching α̂ 5.30 [4.26, 7.97], tail not covered; semantic R̂ 0.14 (bge) / 0.09 (gte). **NE (round 2), boundary #37→#38:** #best→#best (N 3→6): Δ ln R_src -0.10 [-0.37, +0.24] vs predicted +0.41; #rest→#best (N 7→6): Δ ln R_src -1.10 [-1.47, -0.72] vs predicted -0.08; #rest→#rest (N 7→8): Δ ln R_src +0.46 [+0.28, +0.66] vs predicted +0.07.
**Role:** replication (exploratory)
**Period:** regime III · mode C · 12 agents at start (median room size 8) · 17 non-holdout days. Setup: Second charity fundraiser, a year after #1. Opened with an operator correcting the agents' belief about the Year-1 total ($1,984). Outreach approval (G) arrives mid-goal.

## Why this period
Secondary period for the cross-period criticality link (P4) and transfer of the forecast rule (P7). Mode C (shared objective), regime III.

## Prediction
*Written 2026-10-04 02:00 UTC, before running on this period* (after the synthetic validation and amendments A1–A5 of the main card; no real cascade statistic had been computed for any period).

| # | Prediction here | Counts against |
| --- | --- | --- |
| P1 | R̂ < 1 with upper 95% CI < 1; typical 0.05–0.5 | lower CI ≥ 1 |
| P2 | R̂ < H03 n̂_talk = 0.32; R_c < R̂ | R̂ > n̂_talk beyond its CI |
| P3a (A1) | observed P(s ≥ 3) and P(s ≥ 5) inside the FN-GW 90% band (if ≥ 50 trees) | outside the band |
| P5 (A2) | contagion beyond the field: HR₁₀ > 1 with lower CI > 1 | HR₁₀ CI includes 1 or < 1 |
| P6 (A3) | pooled recency HR(2 vs 1) ≤ 2.5 (not complex) | HR(2 vs 1) > 3 with lower CI > 2.5 |

**Verdict rule (A2):** supported = P5 (HR₁₀ lower CI > 1) and P3a pass; failed = both fail, or R̂ lower CI ≥ 1; mixed = exactly one passes; n/a = fewer than 20 non-seed agent first uses (or < 50 trees for P3a, which then counts as not tested and the verdict rests on P5: supported → mixed at best).

## Result
**mixed.** 7834 ideas, 10760 agent first uses, 7997 trees, N_room 8; R̂ = 0.257, contagion share R_c = 0.253, HR₁₀ = 75.42; P(s ≥ 2) = 0.217, largest tree 7.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 R̂ < 1 (upper CI < 1) | R̂ = 0.257 [0.247, 0.266] | critical R = 1 | pass |
| P2 R̂ < H03 n̂_talk | R̂ 0.257 vs n̂ 0.32; R_c = 0.253 | HH108: R̂ > n̂ | pass |
| P3a FN-GW band covers P(s ≥ 3), P(s ≥ 5) | P(s≥3) 0.086 (band 0.068–0.083); P(s≥5) 0.007 (band 0.005–0.009) | GW-NB band covers both: no | fail |
| P3b pure s^−3/2 rejected; τ_app ≥ 2 | LR 3148.6; τ_app 2.71 | critical branching | pass |
| P5 HR₁₀ > 1, lower CI > 1 (A2) | HR₁₀ = 75.42 [66.69, 85.63] (221 adoptions at k = 0) | field: HR₁₀ ≤ 1 | pass |
| P5a jitter excess (pre-registered; failed guard) | exposed 0.945 vs null 0.971, p = 1.00 | uninterpretable (S2) | n/a |
| P6 pooled HR(2 vs 1) ≤ 2.5 | 2.71 [2.41, 3.04] | complex > 3; heterogeneity inflates | ambiguous |
| P5c cross-room ratio > 3 | 411.0 [206.2, 2382.7] (P(adopt) 0.083 vs 0.0002) | field ≈ 1–1.8 (S2) | pass (room fields confound) |
| P7 day-ahead 90% PI coverage (pre-registered FN-GW) | P(s≥2) 0.50, P(s≥3) 0.31 over 16 days | post-hoc V3: 0.81, 0.81 | fail |

**By idea class** (U artifact, D number, N name/coinage, W rare word):

| Class | ideas | agent nodes | R̂ [95% CI] | R_c | P(s ≥ 2) | P(s ≥ 3) | s_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D | 1405 | 2884 | 0.48 [0.46, 0.49] | 0.47 | 0.494 | 0.281 | 7 |
| N | 6150 | 7456 | 0.17 [0.16, 0.18] | 0.16 | 0.148 | 0.037 | 7 |
| U | 63 | 97 | 0.34 [0.23, 0.44] | 0.30 | 0.266 | 0.141 | 5 |
| W | 216 | 323 | 0.31 [0.25, 0.37] | 0.31 | 0.261 | 0.104 | 6 |

Data: `data/processed/H34-idea-cascades/G38/`. Figures: `../../figures/` (cross-period); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): HR₁₀ beats the field null (lower CI 66.69). D (unfitted shape): FN-GW band misses the tail; pure s^−3/2 rejected. G (rooms): never-exposed agents adopt far less (ratio 411.0), confounded by room fields. E: no natural experiment inside this period was used.

## Notes
- Two rooms active: the cross-room contrast is available but confounded by room-specific fields (rooms often worked on different projects).
- Censoring check: R̂ without trees rooted on the last day = 0.263.
- Root vs non-root mean offspring 0.247 vs 0.284 (GW assumes equal).
- Root types: invented 0.98, from humans 0.000, field (unexposed) 0.020; 0.94 of non-seed first uses were visibly exposed.

## Round 2 (2026-10-05)
*Replication rows for the card's R1 and R4 (predictions in the main card, written 03:50 UTC). Role: replication; no verdict change.*

| Quantity | Value | Reference |
| --- | --- | --- |
| R1 gamma-mixed FN-GW: α̂ (CV² = 1/α), μ̂ | 5.30 [4.26, 7.97], μ̂ 0.269 | LR vs one R: 30.9 (5% point 2.71) |
| R1 tail: P(s ≥ 3), P(s ≥ 5) | 0.090, 0.0076 | Γ-FN 90% band [0.072, 0.085], [0.0093, 0.0140]: not covered |
| R1 non-root / root offspring (unfitted) | 1.17 | Γ-FN band [0.86, 1.00]; one R 0.77; homogeneous skeleton ≤ 0.91 |
| R1 day-ahead log score, Γ-FN minus beta-binomial | -21.2 nats | > 0 favours Γ-FN |
| R4 semantic R̂, bge (θ 0.90) | 0.14 [0.12, 0.15], 2676 first uses | marker R̂ (1b) in the 1b line above |
| R4 semantic R̂, gte (θ 0.877) | 0.09 [0.08, 0.10], 2915 first uses | |
| R4 HR₁₀ (bge / gte) | 32.4 / 58.3 | field null 1 |
| R4 HR_unread5 / HR_seen5 (bge / gte) | 1.25 / 1.27 | copying < 1; marker median 0.56 |

**R2 native, boundary #37→#38** (role native; dilution rule R̂ ∝ (N − 1)^0.451 written before looking): #best→#best (N 3→6): Δ ln R_src -0.10 [-0.37, +0.24] vs predicted +0.41; #rest→#best (N 7→6): Δ ln R_src -1.10 [-1.47, -0.72] vs predicted -0.08; #rest→#rest (N 7→8): Δ ln R_src +0.46 [+0.28, +0.66] vs predicted +0.07. The boundary is also a goal change, so only the difference between groups is read (card, R2).
