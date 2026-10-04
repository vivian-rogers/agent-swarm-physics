# H82 × G04: boundary #3 → #4 (day 1 = 2025-05-15)

**Verdict:** mixed
**Role:** replication
**Period:** regime I · 3 agents with a prior on day 1 · 21 placebo centroids · newcomers on days 1–5: 0.

## Why this period
Every eligible goal boundary (both sides non-holdout, one regime) is a replication point of the remanence regression. Here the endogenous field is the #3 village centroid.

## Prediction
*Written 2026-10-04 20:07 UTC in the card (P1–P3), before any real-data statistic; this folder was generated after the run.*
- Δγ_1 > 0 beyond the S0 bias (P1), γ[P−1] > γ[P+1] (P2), decay over days 1–5 (P3). Per-boundary verdict rule in `analysis/write_outputs.py`.

## Result
| Quantity | bge | gte |
| --- | --- | --- |
| γ_1 [P−1 centroid] | +0.241 | +0.219 |
| median γ_1 [placebo centroids] | -0.012 | -0.032 |
| γ_1 [P+1 centroid] | +0.176 | +0.193 |
| Δγ_1 [95% agent bootstrap] | +0.253 [-0.035, +0.439] | +0.251 [+0.040, +0.549] |
| asymmetry A_1 = γ[P−1] − γ[P+1] | +0.066 | +0.026 |
| Δγ_d, d = 1…5 | +0.253, +0.196, +0.116, +0.061, -0.066 | +0.251, +0.238, +0.205, +0.161, +0.054 |

S0 bias of Δγ_1 (pooled synthetic): bge +0.022, gte +0.033. Data: `data/processed/H82-remanence-endogenous-field/replication/boundary_rows.parquet`.

## Scorecard (period-specific axes)
- C: Δγ_1 against placebo centroids. D: the time asymmetry and the day profile are unfitted signatures.

## Notes
- One boundary is one design; per-boundary CIs come from resampling agents (few agents in regime I).
