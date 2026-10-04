# H82 × G37: boundary #36 → #37 (day 1 = 2026-03-30)

**Verdict:** supported
**Role:** replication
**Period:** regime III · 12 agents with a prior on day 1 · 6 placebo centroids · newcomers on days 1–5: 0.

## Why this period
Every eligible goal boundary (both sides non-holdout, one regime) is a replication point of the remanence regression. Here the endogenous field is the #36 village centroid.

## Prediction
*Written 2026-10-04 20:07 UTC in the card (P1–P3), before any real-data statistic; this folder was generated after the run.*
- Δγ_1 > 0 beyond the S0 bias (P1), γ[P−1] > γ[P+1] (P2), decay over days 1–5 (P3). Per-boundary verdict rule in `analysis/write_outputs.py`.

## Result
| Quantity | bge | gte |
| --- | --- | --- |
| γ_1 [P−1 centroid] | +0.311 | +0.322 |
| median γ_1 [placebo centroids] | +0.088 | +0.072 |
| γ_1 [P+1 centroid] | +0.035 | +0.094 |
| Δγ_1 [95% agent bootstrap] | +0.223 [+0.048, +0.382] | +0.249 [+0.128, +0.358] |
| asymmetry A_1 = γ[P−1] − γ[P+1] | +0.276 | +0.227 |
| Δγ_d, d = 1…3 | +0.223, +0.127, +0.265 | +0.249, +0.149, +0.272 |

S0 bias of Δγ_1 (pooled synthetic): bge +0.022, gte +0.033. Data: `data/processed/H82-remanence-endogenous-field/replication/boundary_rows.parquet`.

## Scorecard (period-specific axes)
- C: Δγ_1 against placebo centroids. D: the time asymmetry and the day profile are unfitted signatures.

## Notes
- One boundary is one design; per-boundary CIs come from resampling agents (few agents in regime I).
