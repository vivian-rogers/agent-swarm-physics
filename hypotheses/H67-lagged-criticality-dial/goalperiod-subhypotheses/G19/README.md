# H67 × G19: goal period #19

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** goal #19 · regime I · mean N 7.5 · units 19a, 19b · 30746 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = -0.003 [-0.032, 0.026]**, J₁* = -0.001 [-0.005, 0.004], g_eq (same data) = 0.248, H25 trimmed talk dial = 0.280, H42 world-B n_x = 0.000; named-message part of g_lag = -0.011.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 19a | 7 | 27714 | 0.003 [-0.029, 0.039] | 0.001 [-0.005, 0.006] | 5.996 | 0.257 | -0.012 | 0.158 |
| 19b | 8 | 3032 | -0.019 [-0.061, 0.063] | -0.003 [-0.009, 0.009] | 7.024 | 0.161 | -0.006 | 0.211 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).
