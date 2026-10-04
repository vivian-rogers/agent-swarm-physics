# H67 × G04: goal period #4

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** goal #4 · regime I · mean N 4.0 · units 4a, 4c · 24761 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = 0.011 [-0.023, 0.046]**, J₁* = 0.004 [-0.008, 0.015], g_eq (same data) = 0.268, H25 trimmed talk dial = 0.335, H42 world-B n_x = 0.030; named-message part of g_lag = -0.002.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 4a | 4 | 5613 | -0.007 [-0.063, 0.068] | -0.002 [-0.021, 0.023] | 2.999 | 0.337 | -0.004 | 0.263 |
| 4c | 4 | 19148 | 0.021 [-0.021, 0.065] | 0.007 [-0.007, 0.022] | 2.990 | 0.248 | -0.001 | 0.000 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).
