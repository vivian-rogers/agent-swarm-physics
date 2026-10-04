# H82 × G07: boundary #6 → #7 (day 1 = 2025-07-16)

**Verdict:** supported
**Role:** replication
**Period:** regime I · 4 agents with a prior on day 1 · 21 placebo centroids · newcomers on days 1–5: 0.

## Why this period
Every eligible goal boundary (both sides non-holdout, one regime) is a replication point of the remanence regression. Here the endogenous field is the #6 village centroid.

## Prediction
*Written 2026-10-04 20:07 UTC in the card (P1–P3), before any real-data statistic; this folder was generated after the run.*
- Δγ_1 > 0 beyond the S0 bias (P1), γ[P−1] > γ[P+1] (P2), decay over days 1–5 (P3). Per-boundary verdict rule in `analysis/write_outputs.py`.

## Result
| Quantity | bge | gte |
| --- | --- | --- |
| γ_1 [P−1 centroid] | +0.502 | +0.597 |
| median γ_1 [placebo centroids] | -0.025 | -0.037 |
| γ_1 [P+1 centroid] | +0.111 | +0.036 |
| Δγ_1 [95% agent bootstrap] | +0.526 [+0.416, +0.670] | +0.634 [+0.432, +0.751] |
| asymmetry A_1 = γ[P−1] − γ[P+1] | +0.390 | +0.560 |
| Δγ_d, d = 1…2 | +0.526, +0.587 | +0.634, +0.755 |

S0 bias of Δγ_1 (pooled synthetic): bge +0.022, gte +0.033. Data: `data/processed/H82-remanence-endogenous-field/replication/boundary_rows.parquet`.

## Scorecard (period-specific axes)
- C: Δγ_1 against placebo centroids. D: the time asymmetry and the day profile are unfitted signatures.

## Notes
- One boundary is one design; per-boundary CIs come from resampling agents (few agents in regime I).
