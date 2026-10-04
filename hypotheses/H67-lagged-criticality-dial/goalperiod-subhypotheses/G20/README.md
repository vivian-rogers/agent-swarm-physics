# H67 × G20: goal period #20

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** goal #20 · regime I · mean N 9.0 · units 20a, 20b, 20c, 20d · 38927 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = -0.020 [-0.046, 0.006]**, J₁* = -0.002 [-0.006, 0.001], g_eq (same data) = 0.148, H25 trimmed talk dial = 0.169, H42 world-B n_x = 0.002; named-message part of g_lag = 0.003.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20a | 8 | 7473 | -0.029 [-0.091, 0.019] | -0.004 [-0.013, 0.003] | 6.983 | 0.175 | -0.018 | 0.158 |
| 20b | 9 | 4156 | -0.033 [-0.078, 0.006] | -0.004 [-0.010, 0.001] | 8.000 | 0.003 | -0.009 | 0.211 |
| 20c | 9 | 14683 | -0.013 [-0.053, 0.037] | -0.002 [-0.007, 0.005] | 7.990 | 0.137 | 0.008 | 0.053 |
| 20d | 10 | 12615 | 0.029 [-0.064, 0.109] | 0.003 [-0.007, 0.012] | 8.940 | 0.193 | 0.015 | 0.105 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).
