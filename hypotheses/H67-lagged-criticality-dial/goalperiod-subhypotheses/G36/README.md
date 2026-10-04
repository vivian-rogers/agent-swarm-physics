# H67 × G36: goal period #36

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** goal #36 · regime II · mean N 12.0 · units 36a, 36b, 36c · 32993 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = 0.068 [-0.030, 0.166]**, J₁* = 0.015 [-0.009, 0.039], g_eq (same data) = 0.136, H25 trimmed talk dial = 0.152, H42 world-B n_x = 0.031; named-message part of g_lag = 0.065.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 36a | 12 | 6709 | -0.060 [-0.146, 0.030] | -0.010 [-0.023, 0.005] | 6.167 | 0.048 | 0.029 | 0.263 |
| 36b | 12 | 12495 | 0.094 [0.053, 0.141] | 0.022 [0.012, 0.036] | 4.370 | 0.083 | 0.054 | 0.158 |
| 36c | 12 | 13789 | 0.151 [0.104, 0.224] | 0.033 [0.021, 0.051] | 4.664 | 0.226 | 0.093 | 0.211 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).
