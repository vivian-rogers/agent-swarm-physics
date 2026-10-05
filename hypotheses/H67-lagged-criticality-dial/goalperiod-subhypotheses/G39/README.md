# H67 × G39: goal period #39

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** goal #39 · regime III · mean N 15.0 · units 39 · 26127 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = 0.144 [0.066, 0.223]**, J₁* = 0.016 [0.007, 0.025], g_eq (same data) = 0.159, H25 trimmed talk dial = 0.108, H42 world-B n_x = 0.072; named-message part of g_lag = 0.073.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 39 | 15 | 26127 | 0.144 [0.073, 0.219] | 0.016 [0.008, 0.025] | 9.060 | 0.159 | 0.073 | 0.263 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).

## Round 2 (2026-10-05)

### R3 ladder and R4 multi-hop gain
*Descriptive (card, Round 2). Period pools (random effects).* H50's pair RD re-implemented (L1) 0.185 [0.005, 0.366] → with call-class cells (L4W) 0.235 [0.009, 0.460] → call counts with cells (L8) 0.149 [0.070, 0.229] → H67 main (L9) 0.144 [0.063, 0.225]. R4 (synthetic S-R4 failed, descriptive only): G₁ -0.024 [-0.170, 0.122], G₃ -0.093 [-0.835, 0.650], G₅ -0.225 [-1.729, 1.280].

| Unit | L1 (H50) | L4W (cells) | L8 (counts) | L9 (H67) | G₃ | G₅ [95%] |
| --- | --- | --- | --- | --- | --- | --- |
| 39 | 0.185 | 0.235 | 0.149 | 0.144 | -0.093 | -0.225 [-1.770, 1.142] |

Data: `data/processed/H67-lagged-criticality-dial/round2/units.parquet`, `periods.parquet`.
