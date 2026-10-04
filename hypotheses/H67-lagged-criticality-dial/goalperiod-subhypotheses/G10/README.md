# H67 × G10: goal period #10

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** goal #10 · regime I · mean N 7.0 · units 10a, 10b · 9046 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = 0.002 [-0.050, 0.054]**, J₁* = 0.000 [-0.009, 0.009], g_eq (same data) = 0.069, H25 trimmed talk dial = 0.174, H42 world-B n_x = 0.010; named-message part of g_lag = -0.005.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 10a | 7 | 2317 | 0.015 [-0.107, 0.186] | 0.002 [-0.018, 0.031] | 6.018 | 0.153 | -0.018 | 0.263 |
| 10b | 7 | 6729 | -0.002 [-0.053, 0.067] | -0.000 [-0.009, 0.011] | 5.994 | 0.040 | -0.001 | 0.105 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).
