# H67 × G36: goal period #36

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** goal #36 · regime II · mean N 12.0 · units 36a, 36b, 36c · 32993 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = 0.068 [-0.030, 0.166]**, J₁* = 0.015 [-0.009, 0.039], g_eq (same data) = 0.136, H25 trimmed talk dial = 0.152, H42 world-B n_x = 0.031; named-message part of g_lag = 0.065.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 36a | 12 | 6709 | -0.060 [-0.146, 0.030] | -0.010 [-0.023, 0.005] | 6.167 | 0.048 | 0.029 | 0.263 |
| 36b | 12 | 12495 | 0.094 [0.053, 0.141] | 0.022 [0.012, 0.036] | 4.370 | 0.083 | 0.054 | 0.158 |
| 36c | 12 | 13789 | 0.151 [0.104, 0.224] | 0.033 [0.021, 0.051] | 4.664 | 0.226 | 0.093 | 0.211 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).

## Round 2 (2026-10-05)

### R3 ladder and R4 multi-hop gain
*Descriptive (card, Round 2). Period pools (random effects).* H50's pair RD re-implemented (L1) 0.186 [-0.041, 0.413] → with call-class cells (L4W) 0.089 [-0.166, 0.344] → call counts with cells (L8) 0.065 [-0.042, 0.173] → H67 main (L9) 0.065 [-0.039, 0.170]. R4 (synthetic S-R4 failed, descriptive only): G₁ -0.089 [-0.159, -0.019], G₃ -0.222 [-0.526, 0.083], G₅ -0.130 [-0.709, 0.448].

| Unit | L1 (H50) | L4W (cells) | L8 (counts) | L9 (H67) | G₃ | G₅ [95%] |
| --- | --- | --- | --- | --- | --- | --- |
| 36a | -0.096 | -0.124 | -0.066 | -0.060 | -0.500 | -0.786 [-1.774, 0.362] |
| 36b | 0.257 | 0.080 | 0.095 | 0.094 | -0.168 | 0.183 [-0.644, 0.989] |
| 36c | 0.343 | 0.309 | 0.154 | 0.151 | -0.026 | -0.166 [-1.116, 1.136] |

Data: `data/processed/H67-lagged-criticality-dial/round2/units.parquet`, `periods.parquet`.
