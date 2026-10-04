# H82 × G38: boundary #37 → #38 (day 1 = 2026-04-02)

**Verdict:** mixed
**Role:** replication
**Period:** regime III · 12 agents with a prior on day 1 · 6 placebo centroids · newcomers on days 1–5: 0.

## Why this period
Every eligible goal boundary (both sides non-holdout, one regime) is a replication point of the remanence regression. Here the endogenous field is the #37 village centroid.

## Prediction
*Written 2026-10-04 20:07 UTC in the card (P1–P3), before any real-data statistic; this folder was generated after the run.*
- Δγ_1 > 0 beyond the S0 bias (P1), γ[P−1] > γ[P+1] (P2), decay over days 1–5 (P3). Per-boundary verdict rule in `analysis/write_outputs.py`.

## Result
| Quantity | bge | gte |
| --- | --- | --- |
| γ_1 [P−1 centroid] | +0.118 | +0.281 |
| median γ_1 [placebo centroids] | +0.105 | +0.132 |
| γ_1 [P+1 centroid] | -0.057 | -0.037 |
| Δγ_1 [95% agent bootstrap] | +0.013 [-0.087, +0.081] | +0.149 [+0.060, +0.282] |
| asymmetry A_1 = γ[P−1] − γ[P+1] | +0.175 | +0.319 |
| Δγ_d, d = 1…5 | +0.013, +0.169, +0.153, +0.147, +0.112 | +0.149, +0.170, +0.258, +0.207, +0.234 |

S0 bias of Δγ_1 (pooled synthetic): bge +0.022, gte +0.033. Data: `data/processed/H82-remanence-endogenous-field/replication/boundary_rows.parquet`.

## Scorecard (period-specific axes)
- C: Δγ_1 against placebo centroids. D: the time asymmetry and the day profile are unfitted signatures.

## Notes
- One boundary is one design; per-boundary CIs come from resampling agents (few agents in regime I).
