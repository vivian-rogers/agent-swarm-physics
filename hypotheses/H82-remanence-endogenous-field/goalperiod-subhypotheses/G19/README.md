# H82 × G19: boundary #18 → #19 (day 1 = 2025-11-03)

**Verdict:** supported
**Role:** replication
**Period:** regime I · 7 agents with a prior on day 1 · 21 placebo centroids · newcomers on days 1–5: 0.

## Why this period
Every eligible goal boundary (both sides non-holdout, one regime) is a replication point of the remanence regression. Here the endogenous field is the #18 village centroid.

## Prediction
*Written 2026-10-04 20:07 UTC in the card (P1–P3), before any real-data statistic; this folder was generated after the run.*
- Δγ_1 > 0 beyond the S0 bias (P1), γ[P−1] > γ[P+1] (P2), decay over days 1–5 (P3). Per-boundary verdict rule in `analysis/write_outputs.py`.

## Result
| Quantity | bge | gte |
| --- | --- | --- |
| γ_1 [P−1 centroid] | +0.341 | +0.325 |
| median γ_1 [placebo centroids] | -0.117 | -0.075 |
| γ_1 [P+1 centroid] | +0.286 | +0.126 |
| Δγ_1 [95% agent bootstrap] | +0.458 [+0.292, +0.602] | +0.400 [+0.326, +0.459] |
| asymmetry A_1 = γ[P−1] − γ[P+1] | +0.055 | +0.199 |
| Δγ_d, d = 1…5 | +0.458, +0.280, +0.489, +0.543, +0.544 | +0.400, +0.189, +0.463, +0.380, +0.437 |

S0 bias of Δγ_1 (pooled synthetic): bge +0.022, gte +0.033. Data: `data/processed/H82-remanence-endogenous-field/replication/boundary_rows.parquet`.

## Scorecard (period-specific axes)
- C: Δγ_1 against placebo centroids. D: the time asymmetry and the day profile are unfitted signatures.

## Notes
- One boundary is one design; per-boundary CIs come from resampling agents (few agents in regime I).
