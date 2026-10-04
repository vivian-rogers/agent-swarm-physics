# H67 × G42: goal period #42

**Verdict:** supported
**Role:** replication (exploratory)
**Period:** goal #42 · regime III · mean N 15.5 · units 42a, 42b · 35639 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = 0.154 [0.059, 0.248]**, J₁* = 0.018 [0.006, 0.030], g_eq (same data) = 0.091, H25 trimmed talk dial = 0.133, H42 world-B n_x = 0.047; named-message part of g_lag = 0.083.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 42a | 15 | 15767 | 0.199 [0.136, 0.284] | 0.024 [0.016, 0.033] | 8.439 | 0.108 | 0.118 | 0.053 |
| 42b | 16 | 19872 | 0.103 [0.005, 0.190] | 0.012 [0.001, 0.022] | 8.901 | 0.077 | 0.056 | 0.105 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).
