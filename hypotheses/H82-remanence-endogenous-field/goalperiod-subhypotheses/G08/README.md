# H82 × G08: boundary #7 → #8 (day 1 = 2025-07-18)

**Verdict:** mixed
**Role:** replication
**Period:** regime I · 4 agents with a prior on day 1 · 22 placebo centroids · newcomers on days 1–5: 0.

## Why this period
Every eligible goal boundary (both sides non-holdout, one regime) is a replication point of the remanence regression. Here the endogenous field is the #7 village centroid.

## Prediction
*Written 2026-10-04 20:07 UTC in the card (P1–P3), before any real-data statistic; this folder was generated after the run.*
- Δγ_1 > 0 beyond the S0 bias (P1), γ[P−1] > γ[P+1] (P2), decay over days 1–5 (P3). Per-boundary verdict rule in `analysis/write_outputs.py`.

## Result
| Quantity | bge | gte |
| --- | --- | --- |
| γ_1 [P−1 centroid] | -0.103 | -0.062 |
| median γ_1 [placebo centroids] | -0.023 | -0.017 |
| γ_1 [P+1 centroid] | n/a | n/a |
| Δγ_1 [95% agent bootstrap] | -0.080 [-0.130, +0.000] | -0.045 [-0.117, +0.092] |
| asymmetry A_1 = γ[P−1] − γ[P+1] | n/a | n/a |
| Δγ_d, d = 1…5 | -0.080, -0.153, -0.088, +0.011, +0.174 | -0.045, -0.214, -0.078, -0.139, +0.099 |

S0 bias of Δγ_1 (pooled synthetic): bge +0.022, gte +0.033. Data: `data/processed/H82-remanence-endogenous-field/replication/boundary_rows.parquet`.

## Scorecard (period-specific axes)
- C: Δγ_1 against placebo centroids. D: the time asymmetry and the day profile are unfitted signatures.

## Notes
- One boundary is one design; per-boundary CIs come from resampling agents (few agents in regime I).
