# H67 × G03: goal period #3

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** goal #3 · regime I · mean N 4.0 · units 3 · 1676 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = 0.017 [-0.090, 0.124]**, J₁* = 0.006 [-0.030, 0.041], g_eq (same data) = 0.353, H25 trimmed talk dial = 0.290, H42 world-B n_x = 0.067; named-message part of g_lag = -0.007.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3 | 4 | 1676 | 0.017 [-0.078, 0.115] | 0.006 [-0.026, 0.038] | 2.991 | 0.353 | -0.007 | 0.211 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).
