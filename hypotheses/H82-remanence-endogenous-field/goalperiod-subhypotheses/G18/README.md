# H82 × G18: boundary #17 → #18 (day 1 = 2025-10-20)

**Verdict:** failed
**Role:** replication
**Period:** regime I · 7 agents with a prior on day 1 · 21 placebo centroids · newcomers on days 1–5: 1.

## Why this period
Every eligible goal boundary (both sides non-holdout, one regime) is a replication point of the remanence regression. Here the endogenous field is the #17 village centroid.

## Prediction
*Written 2026-10-04 20:07 UTC in the card (P1–P3), before any real-data statistic; this folder was generated after the run.*
- Δγ_1 > 0 beyond the S0 bias (P1), γ[P−1] > γ[P+1] (P2), decay over days 1–5 (P3). Per-boundary verdict rule in `analysis/write_outputs.py`.

## Result
| Quantity | bge | gte |
| --- | --- | --- |
| γ_1 [P−1 centroid] | -0.025 | -0.016 |
| median γ_1 [placebo centroids] | +0.020 | -0.002 |
| γ_1 [P+1 centroid] | -0.170 | -0.078 |
| Δγ_1 [95% agent bootstrap] | -0.046 [-0.116, +0.058] | -0.014 [-0.098, +0.076] |
| asymmetry A_1 = γ[P−1] − γ[P+1] | +0.145 | +0.061 |
| Δγ_d, d = 1…5 | -0.046, +0.098, +0.248, +0.520, +0.350 | -0.014, +0.094, +0.361, +0.612, +0.584 |

S0 bias of Δγ_1 (pooled synthetic): bge +0.022, gte +0.033. Data: `data/processed/H82-remanence-endogenous-field/replication/boundary_rows.parquet`.

## Scorecard (period-specific axes)
- C: Δγ_1 against placebo centroids. D: the time asymmetry and the day profile are unfitted signatures.

## Notes
- One boundary is one design; per-boundary CIs come from resampling agents (few agents in regime I).
