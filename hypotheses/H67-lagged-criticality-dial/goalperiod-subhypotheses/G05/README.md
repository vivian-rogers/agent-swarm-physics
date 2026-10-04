# H67 × G05: goal period #5

**Verdict:** supported
**Role:** replication (exploratory)
**Period:** goal #5 · regime I · mean N 4.0 · units 5 · 5634 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = 0.052 [0.006, 0.099]**, J₁* = 0.017 [0.002, 0.033], g_eq (same data) = 0.037, H25 trimmed talk dial = 0.081, H42 world-B n_x = 0.026; named-message part of g_lag = 0.019.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 4 | 5634 | 0.052 [0.014, 0.104] | 0.017 [0.005, 0.035] | 3.001 | 0.037 | 0.019 | 0.263 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).
