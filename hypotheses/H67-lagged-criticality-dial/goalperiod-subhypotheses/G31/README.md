# H67 × G31: goal period #31

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** goal #31 · regime I · mean N 11.2 · units 31a, 31b, 31c, 31d · 33387 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = -0.035 [-0.094, 0.025]**, J₁* = -0.003 [-0.009, 0.002], g_eq (same data) = 0.050, H25 trimmed talk dial = 0.096, H42 world-B n_x = 0.000; named-message part of g_lag = 0.013.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 31a | 11 | 13791 | 0.024 [-0.022, 0.064] | 0.002 [-0.002, 0.006] | 10.119 | 0.077 | 0.026 | 0.053 |
| 31b | 12 | 6455 | -0.076 [-0.223, 0.041] | -0.007 [-0.020, 0.004] | 11.048 | 0.135 | -0.031 | 0.105 |
| 31c | 11 | 6218 | -0.042 [-0.091, 0.054] | -0.004 [-0.009, 0.006] | 9.989 | -0.065 | 0.051 | 0.158 |
| 31d | 11 | 6923 | -0.084 [-0.163, -0.025] | -0.008 [-0.016, -0.003] | 10.154 | 0.020 | -0.008 | 0.316 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).
