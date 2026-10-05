# H67 × G42: goal period #42

**Verdict:** supported
**Role:** replication (exploratory)
**Period:** goal #42 · regime III · mean N 15.5 · units 42a, 42b · 35639 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = 0.154 [0.059, 0.248]**, J₁* = 0.018 [0.006, 0.030], g_eq (same data) = 0.091, H25 trimmed talk dial = 0.133, H42 world-B n_x = 0.047; named-message part of g_lag = 0.083.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 42a | 15 | 15767 | 0.199 [0.136, 0.284] | 0.024 [0.016, 0.033] | 8.439 | 0.108 | 0.118 | 0.053 |
| 42b | 16 | 19872 | 0.103 [0.005, 0.190] | 0.012 [0.001, 0.022] | 8.901 | 0.077 | 0.056 | 0.105 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).

## Round 2 (2026-10-05)

### R3 ladder and R4 multi-hop gain
*Descriptive (card, Round 2). Period pools (random effects).* H50's pair RD re-implemented (L1) 0.224 [0.148, 0.301] → with call-class cells (L4W) 0.195 [-0.038, 0.429] → call counts with cells (L8) 0.156 [0.060, 0.252] → H67 main (L9) 0.155 [0.060, 0.249]. R4 (synthetic S-R4 failed, descriptive only): G₁ 0.090 [-0.065, 0.246], G₃ 0.275 [-0.266, 0.815], G₅ 0.313 [-0.745, 1.371].

| Unit | L1 (H50) | L4W (cells) | L8 (counts) | L9 (H67) | G₃ | G₅ [95%] |
| --- | --- | --- | --- | --- | --- | --- |
| 42a | 0.210 | 0.296 | 0.199 | 0.199 | 0.486 | 0.713 [-0.908, 1.820] |
| 42b | 0.245 | 0.054 | 0.101 | 0.103 | 0.043 | -0.212 [-1.770, 1.271] |

Data: `data/processed/H67-lagged-criticality-dial/round2/units.parquet`, `periods.parquet`.
