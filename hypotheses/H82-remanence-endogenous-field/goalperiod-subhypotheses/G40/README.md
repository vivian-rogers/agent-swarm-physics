# H82 × G40: boundary #39 → #40 (day 1 = 2026-05-04)

**Verdict:** supported
**Role:** replication
**Period:** regime III · 15 agents with a prior on day 1 · 6 placebo centroids · newcomers on days 1–5: 0.

## Why this period
Every eligible goal boundary (both sides non-holdout, one regime) is a replication point of the remanence regression. Here the endogenous field is the #39 village centroid.

## Prediction
*Written 2026-10-04 20:07 UTC in the card (P1–P3), before any real-data statistic; this folder was generated after the run.*
- Δγ_1 > 0 beyond the S0 bias (P1), γ[P−1] > γ[P+1] (P2), decay over days 1–5 (P3). Per-boundary verdict rule in `analysis/write_outputs.py`.

## Result
| Quantity | bge | gte |
| --- | --- | --- |
| γ_1 [P−1 centroid] | +0.330 | +0.511 |
| median γ_1 [placebo centroids] | -0.019 | -0.040 |
| γ_1 [P+1 centroid] | +0.023 | +0.007 |
| Δγ_1 [95% agent bootstrap] | +0.350 [+0.283, +0.411] | +0.551 [+0.454, +0.630] |
| asymmetry A_1 = γ[P−1] − γ[P+1] | +0.308 | +0.505 |
| Δγ_d, d = 1…5 | +0.350, +0.439, +0.360, +0.215, +0.313 | +0.551, +0.460, +0.376, +0.268, +0.263 |

S0 bias of Δγ_1 (pooled synthetic): bge +0.022, gte +0.033. Data: `data/processed/H82-remanence-endogenous-field/replication/boundary_rows.parquet`.

## Scorecard (period-specific axes)
- C: Δγ_1 against placebo centroids. D: the time asymmetry and the day profile are unfitted signatures.

## Notes
- One boundary is one design; per-boundary CIs come from resampling agents (few agents in regime I).
