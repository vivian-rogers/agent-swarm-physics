# H67 × G33: goal period #33

**Verdict:** failed
**Role:** replication (exploratory)
**Period:** goal #33 · regime II · mean N 11.0 · units 33 · 14649 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = -0.029 [-0.133, 0.076]**, J₁* = -0.003 [-0.013, 0.007], g_eq (same data) = 0.083, H25 trimmed talk dial = 0.083, H42 world-B n_x = 0.000; named-message part of g_lag = -0.019.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 33 | 11 | 14649 | -0.029 [-0.119, 0.084] | -0.003 [-0.012, 0.008] | 10.161 | 0.083 | -0.019 | 0.000 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).

## Round 2 (2026-10-05)

### R3 ladder and R4 multi-hop gain
*Descriptive (card, Round 2). Period pools (random effects).* H50's pair RD re-implemented (L1) 0.182 [-0.008, 0.371] → with call-class cells (L4W) 0.041 [-0.112, 0.193] → call counts with cells (L8) -0.027 [-0.130, 0.076] → H67 main (L9) -0.029 [-0.133, 0.076]. R4 (synthetic S-R4 failed, descriptive only): G₁ -0.225 [-0.436, -0.014], G₃ -0.534 [-1.213, 0.145], G₅ -1.153 [-2.493, 0.188].

| Unit | L1 (H50) | L4W (cells) | L8 (counts) | L9 (H67) | G₃ | G₅ [95%] |
| --- | --- | --- | --- | --- | --- | --- |
| 33 | 0.182 | 0.041 | -0.027 | -0.029 | -0.534 | -1.153 [-2.328, 0.390] |

Data: `data/processed/H67-lagged-criticality-dial/round2/units.parquet`, `periods.parquet`.
