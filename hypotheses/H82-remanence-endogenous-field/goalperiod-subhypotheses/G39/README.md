# H82 × G39: boundary #38 → #39 (day 1 = 2026-04-27)

**Verdict:** failed
**Role:** replication
**Period:** regime III · 14 agents with a prior on day 1 · 6 placebo centroids · newcomers on days 1–5: 1.

## Why this period
Every eligible goal boundary (both sides non-holdout, one regime) is a replication point of the remanence regression. Here the endogenous field is the #38 village centroid.

## Prediction
*Written 2026-10-04 20:07 UTC in the card (P1–P3), before any real-data statistic; this folder was generated after the run.*
- Δγ_1 > 0 beyond the S0 bias (P1), γ[P−1] > γ[P+1] (P2), decay over days 1–5 (P3). Per-boundary verdict rule in `analysis/write_outputs.py`.

## Result
| Quantity | bge | gte |
| --- | --- | --- |
| γ_1 [P−1 centroid] | -0.074 | +0.056 |
| median γ_1 [placebo centroids] | +0.077 | +0.064 |
| γ_1 [P+1 centroid] | +0.233 | +0.244 |
| Δγ_1 [95% agent bootstrap] | -0.151 [-0.229, -0.053] | -0.008 [-0.059, +0.065] |
| asymmetry A_1 = γ[P−1] − γ[P+1] | -0.307 | -0.188 |
| Δγ_d, d = 1…5 | -0.151, -0.140, -0.067, -0.104, -0.033 | -0.008, -0.044, -0.080, -0.132, -0.074 |

S0 bias of Δγ_1 (pooled synthetic): bge +0.022, gte +0.033. Data: `data/processed/H82-remanence-endogenous-field/replication/boundary_rows.parquet`.

## Scorecard (period-specific axes)
- C: Δγ_1 against placebo centroids. D: the time asymmetry and the day profile are unfitted signatures.

## Notes
- One boundary is one design; per-boundary CIs come from resampling agents (few agents in regime I).
