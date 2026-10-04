# H67 × G18: goal period #18

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** goal #18 · regime I · mean N 7.3 · units 18a, 18b, 18c · 28872 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = 0.048 [-0.000, 0.097]**, J₁* = 0.007 [-0.001, 0.016], g_eq (same data) = 0.293, H25 trimmed talk dial = 0.305, H42 world-B n_x = 0.002; named-message part of g_lag = 0.022.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 18a | 7 | 3918 | 0.004 [-0.110, 0.129] | 0.001 [-0.018, 0.021] | 5.989 | 0.451 | 0.017 | 0.053 |
| 18b | 8 | 14717 | 0.018 [-0.039, 0.091] | 0.003 [-0.006, 0.013] | 6.981 | 0.273 | 0.028 | 0.000 |
| 18c | 7 | 10237 | 0.082 [0.020, 0.128] | 0.014 [0.003, 0.021] | 5.997 | 0.262 | 0.015 | 0.053 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).
