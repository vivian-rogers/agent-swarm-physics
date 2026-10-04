# H67 × G41: goal period #41

**Verdict:** supported
**Role:** replication (exploratory)
**Period:** goal #41 · regime III · mean N 15.0 · units 41 · 27880 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = 0.189 [0.093, 0.286]**, J₁* = 0.023 [0.011, 0.035], g_eq (same data) = 0.162, H25 trimmed talk dial = 0.175, H42 world-B n_x = 0.014; named-message part of g_lag = 0.060.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 41 | 15 | 27880 | 0.189 [0.095, 0.288] | 0.023 [0.011, 0.037] | 8.479 | 0.162 | 0.060 | 0.158 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).
