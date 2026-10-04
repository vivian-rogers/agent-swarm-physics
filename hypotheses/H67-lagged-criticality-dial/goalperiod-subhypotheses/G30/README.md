# H67 × G30: goal period #30

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** goal #30 · regime I · mean N 11.0 · units 30a, 30b · 30837 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = -0.005 [-0.041, 0.030]**, J₁* = -0.001 [-0.004, 0.003], g_eq (same data) = 0.182, H25 trimmed talk dial = 0.197, H42 world-B n_x = 0.000; named-message part of g_lag = -0.004.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 30a | 11 | 6417 | 0.021 [-0.091, 0.116] | 0.002 [-0.010, 0.011] | 10.096 | 0.161 | 0.003 | 0.316 |
| 30b | 11 | 24420 | -0.009 [-0.052, 0.034] | -0.001 [-0.005, 0.003] | 10.060 | 0.188 | -0.006 | 0.368 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).
