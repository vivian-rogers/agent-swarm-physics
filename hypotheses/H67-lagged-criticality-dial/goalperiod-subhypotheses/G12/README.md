# H67 × G12: goal period #12

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** goal #12 · regime I · mean N 7.0 · units 12a · 8973 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = 0.039 [-0.008, 0.086]**, J₁* = 0.007 [-0.001, 0.014], g_eq (same data) = 0.221, H25 trimmed talk dial = 0.226, H42 world-B n_x = 0.006; named-message part of g_lag = 0.025.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 12a | 7 | 8973 | 0.039 [-0.009, 0.084] | 0.007 [-0.002, 0.014] | 5.991 | 0.221 | 0.025 | 0.105 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).
