# H67 × G38: goal period #38

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** goal #38 · regime III · mean N 12.8 · units 38a, 38b, 38c, 38d, 38e · 93179 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = 0.066 [0.041, 0.090]**, J₁* = 0.012 [0.008, 0.017], g_eq (same data) = 0.108, H25 trimmed talk dial = 0.071, H42 world-B n_x = 0.036; named-message part of g_lag = 0.037.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 38a | 12 | 51979 | 0.080 [0.045, 0.115] | 0.016 [0.009, 0.023] | 5.029 | 0.127 | 0.050 | 0.105 |
| 38b | 12 | 13445 | 0.039 [-0.017, 0.109] | 0.008 [-0.003, 0.021] | 5.216 | 0.116 | 0.009 | 0.105 |
| 38c | 13 | 6348 | 0.051 [0.007, 0.088] | 0.009 [0.001, 0.015] | 5.566 | 0.106 | 0.025 | 0.316 |
| 38d | 13 | 7056 | 0.112 [-0.023, 0.209] | 0.020 [-0.004, 0.040] | 5.584 | 0.077 | 0.041 | 0.105 |
| 38e | 14 | 14351 | 0.030 [-0.050, 0.154] | 0.005 [-0.008, 0.026] | 6.064 | 0.050 | 0.020 | 0.105 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).

## Round 2 (2026-10-05)

### R3 ladder and R4 multi-hop gain
*Descriptive (card, Round 2). Period pools (random effects).* H50's pair RD re-implemented (L1) 0.129 [0.050, 0.207] → with call-class cells (L4W) 0.136 [0.025, 0.247] → call counts with cells (L8) 0.067 [0.044, 0.091] → H67 main (L9) 0.066 [0.041, 0.091]. R4 (synthetic S-R4 failed, descriptive only): G₁ -0.008 [-0.120, 0.104], G₃ 0.045 [-0.377, 0.467], G₅ -0.016 [-0.967, 0.934].

| Unit | L1 (H50) | L4W (cells) | L8 (counts) | L9 (H67) | G₃ | G₅ [95%] |
| --- | --- | --- | --- | --- | --- | --- |
| 38a | 0.238 | 0.271 | 0.083 | 0.080 | -0.070 | -0.089 [-0.843, 0.738] |
| 38b | 0.087 | 0.052 | 0.041 | 0.039 | 0.294 | -0.148 [-1.523, 1.537] |
| 38c | 0.120 | 0.062 | 0.049 | 0.051 | -0.857 | -1.906 [-4.807, 0.162] |
| 38d | 0.084 | 0.222 | 0.117 | 0.112 | 0.792 | 1.722 [-0.149, 2.466] |
| 38e | 0.020 | 0.070 | 0.027 | 0.030 | -0.273 | -0.637 [-1.833, 1.142] |

Data: `data/processed/H67-lagged-criticality-dial/round2/units.parquet`, `periods.parquet`.
