# H139 × G51: private roles, where the two rates were measured (#51 main body, units 51a–51l)

**Verdict:** n/a (inconclusive: below resolution). S1 fired before real data; P1 and P2 are untestable here.
**Role:** exploratory (replication over 12 units + native N2)
**Period:** regime III · mode I/K (private roles) · up to 21 agents · #general (and #focus from 08-05) · non-reserved days 2026-07-06 → 2026-09-04. The tail (2026-09-07 → 09-21) is reserved and not used.

## Why this period
H130 measured the kick (J_K 0.044 [0.038, 0.050]), its decay (γ_kick ≈ 0.13–0.17 per call) and the well (γ_auto 0.0094 [0.0076, 0.0115]) on these units. H139 asks whether the agent's own autocovariance holds a fast component of the size those numbers fix. The statistic (an autocovariance) differs from H130's (read-dose regressions), so the check is unfitted, but it reuses the same units.

## Prediction
*Written 2026-10-07 ~10:00 UTC, before running on this period. Seen: H130's card in full; no read count per call and no 1-call autocovariance.*
- **N2 / P1:** pooled Q_k over 51a–51l in [⅔, 1.5] with 90% CI inside [0.5, 2]. Credence 0.1. Expected failure mode: Q_k ≫ 2 (R-innovation), or below resolution (S1).
- **P2:** slope of ln Â_k,i on ln r̄_i across agents in [0.5, 1.5] with CI above 0. Credence 0.25.
- **P4:** split-unit Spearman of the slow share ≥ 0.3 (odd vs even units), permutation p < 0.05. Credence 0.35.
- Counts against: the kill rule of the card (Q_k,i outside [0.5, 2] in most resolved agent-units and pooled CI excluding [0.5, 2]).

## Result
*Run 2026-10-07 14:32 UTC (exploratory, non-reserved). Primary variant `style_resid_period` × bge, drive-corrected. S1 (A_min > 2 A_k^pred) was fixed as the decision before real data (card, Amendment A1). Data: `data/processed/H139-two-rate-variance-split/G51/` and `results/units_G51.parquet`. Figures: the card's `figures/`.*

| Unit | Days | r̄ /call | J_K used | A_k^pred | A_min (synthetic) | A_min (real scale, post hoc) | Â_k [95% CI] | f_s | two-rate beats one (OOF) | γ_s /call | P1 |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 51a | 3 | 1.13 | 0.043 | 0.0094 | 0.97 | 0.075 | 0.012 [-0.037, 0.040] | 0.95 | False | 0.0075 | untestable (S1) |
| 51b | 1 | 0.99 | 0.060 | 0.0161 | — | — | 0.016 [-0.079, 0.056] | 0.89 | None | 0.0018 | descriptive (< 3 days) |
| 51c | 5 | 0.74 | 0.051 | 0.0031 | 1.15 | 0.220 | -0.162 [-0.290, -0.047] | 2.34 | False | 0.0234 | untestable (S1) |
| 51d | 5 | 1.20 | 0.043 | 0.0121 | 0.86 | 0.083 | -0.013 [-0.055, 0.049] | 1.08 | False | 0.0132 | untestable (S1) |
| 51e | 3 | 1.08 | 0.053 | 0.0057 | 1.39 | 0.111 | -0.056 [-0.121, -0.002] | 1.32 | True | 0.0132 | untestable (S1) |
| 51f | 5 | 1.10 | 0.046 | 0.0175 | 1.22 | 0.142 | -0.050 [-0.134, -0.007] | 1.31 | True | 0.0110 | untestable (S1) |
| 51g | 13 | 0.77 | 0.044 | 0.0055 | 0.59 | 0.116 | -0.097 [-0.183, -0.050] | 1.97 | False | 0.0160 | untestable (S1) |
| 51h | 4 | 0.90 | 0.055 | 0.0036 | 1.22 | 0.304 | -0.150 [-0.377, -0.067] | 2.93 | False | 0.0160 | untestable (S1) |
| 51i | 2 | 0.97 | 0.044 | 0.0058 | — | — | -0.288 [-0.533, -0.047] | 3.79 | True | 0.0375 | descriptive (< 3 days) |
| 51j | 2 | 1.05 | 0.051 | 0.0071 | — | — | -0.115 [-0.221, -0.032] | 2.16 | False | 0.0100 | descriptive (< 3 days) |
| 51k | 1 | 1.45 | 0.038 | 0.0075 | — | — | 0.012 [-0.247, 0.055] | 0.94 | None | 0.0056 | descriptive (< 3 days) |
| 51l | 1 | 1.62 | 0.018 | 0.0019 | — | — | 0.000 [-0.206, 0.101] | 1.00 | None | 0.0193 | descriptive (< 3 days) |

| Prediction | Observed | Verdict |
| --- | --- | --- |
| N2 / P1 pooled Q_k in [⅔, 1.5] | untestable: A_min/A_k^pred 102–184 (synthetic), 6.8–85 (real scale). Bound: pooled #51 Â_k -0.053 [-0.093, -0.012] (7 units, I² 0.60) vs A_k^pred median 0.0057 | untestable → inconclusive |
| P2 dose slope | not computed (Amendment A1.3) | untestable |
| P3 f_s ≥ 0.8 | 7/7 units (f_s > 1 where Â_k < 0) | passes; non-diagnostic |
| P4 split-unit Spearman ≥ 0.3, p < 0.05 | ρ -0.20 [-0.61, 0.27], permutation p 0.81, 23 agents (odd vs even units) | failed |

Post hoc: the lag-1 covariance is below the lag-2 covariance in 7/7 testable #51 units, so the constrained Â_k is negative (CI below 0 in 51c, 51e, 51f, 51g, 51h). The slow rate γ_s 0.0075–0.023/call (median 0.013) is close to H130's γ_auto 0.0094.

## Scorecard (period-specific axes)
C 0 (two-rate beats one-rate in 2/7 units; non-diagnostic). D 0 (unfitted prediction below resolution). F 1 (synthetic on 51a, 51c–51h; estimator unbiased only at A ≥ 1). H 0 (rivals not separable).

## Notes
- H130's per-unit γ_kick enters O2 as a fixed rate; the free-rate fit is a variant.
