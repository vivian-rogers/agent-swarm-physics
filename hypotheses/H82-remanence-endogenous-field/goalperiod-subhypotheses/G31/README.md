# H82 × G31: boundary #30 → #31 (day 1 = 2026-02-16)

**Verdict:** supported
**Role:** replication
**Period:** regime I · 10 agents with a prior on day 1 · 22 placebo centroids · newcomers on days 1–5: 0.

## Why this period
Every eligible goal boundary (both sides non-holdout, one regime) is a replication point of the remanence regression. Here the endogenous field is the #30 village centroid.

## Prediction
*Written 2026-10-04 20:07 UTC in the card (P1–P3), before any real-data statistic; this folder was generated after the run.*
- Δγ_1 > 0 beyond the S0 bias (P1), γ[P−1] > γ[P+1] (P2), decay over days 1–5 (P3). Per-boundary verdict rule in `analysis/write_outputs.py`.

## Result
| Quantity | bge | gte |
| --- | --- | --- |
| γ_1 [P−1 centroid] | +0.195 | +0.282 |
| median γ_1 [placebo centroids] | -0.012 | -0.027 |
| γ_1 [P+1 centroid] | n/a | n/a |
| Δγ_1 [95% agent bootstrap] | +0.207 [+0.100, +0.272] | +0.309 [+0.205, +0.416] |
| asymmetry A_1 = γ[P−1] − γ[P+1] | n/a | n/a |
| Δγ_d, d = 1…5 | +0.207, +0.414, +0.148, +0.275, +0.203 | +0.309, +0.209, +0.062, +0.170, +0.157 |

S0 bias of Δγ_1 (pooled synthetic): bge +0.022, gte +0.033. Data: `data/processed/H82-remanence-endogenous-field/replication/boundary_rows.parquet`.

## Scorecard (period-specific axes)
- C: Δγ_1 against placebo centroids. D: the time asymmetry and the day profile are unfitted signatures.

## Notes
- One boundary is one design; per-boundary CIs come from resampling agents (few agents in regime I).
