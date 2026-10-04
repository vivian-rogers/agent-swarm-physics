# H67 × G11: goal period #11

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** goal #11 · regime I · mean N 7.0 · units 11 · 11759 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = 0.027 [-0.026, 0.080]**, J₁* = 0.005 [-0.004, 0.013], g_eq (same data) = 0.192, H25 trimmed talk dial = 0.126, H42 world-B n_x = 0.013; named-message part of g_lag = -0.008.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 11 | 7 | 11759 | 0.027 [-0.027, 0.074] | 0.005 [-0.004, 0.012] | 5.983 | 0.192 | -0.008 | 0.105 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).
