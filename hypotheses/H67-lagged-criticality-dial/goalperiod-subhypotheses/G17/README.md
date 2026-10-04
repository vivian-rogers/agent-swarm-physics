# H67 × G17: goal period #17

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** goal #17 · regime I · mean N 7.0 · units 17 · 9964 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = 0.038 [-0.075, 0.150]**, J₁* = 0.006 [-0.012, 0.025], g_eq (same data) = 0.347, H25 trimmed talk dial = 0.395, H42 world-B n_x = 0.000; named-message part of g_lag = 0.002.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 17 | 7 | 9964 | 0.038 [-0.068, 0.162] | 0.006 [-0.011, 0.027] | 6.001 | 0.347 | 0.002 | 0.053 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).
