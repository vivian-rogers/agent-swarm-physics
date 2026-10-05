# H67 × G35: goal period #35

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** goal #35 · regime II · mean N 12.0 · units 35 · 43042 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = 0.046 [0.015, 0.076]**, J₁* = 0.007 [0.002, 0.012], g_eq (same data) = 0.107, H25 trimmed talk dial = 0.127, H42 world-B n_x = 0.010; named-message part of g_lag = 0.021.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 35 | 12 | 43042 | 0.046 [0.016, 0.073] | 0.007 [0.003, 0.012] | 6.427 | 0.107 | 0.021 | 0.000 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).

## Round 2 (2026-10-05)

### R3 ladder and R4 multi-hop gain
*Descriptive (card, Round 2). Period pools (random effects).* H50's pair RD re-implemented (L1) 0.076 [-0.031, 0.182] → with call-class cells (L4W) 0.076 [-0.003, 0.156] → call counts with cells (L8) 0.045 [0.017, 0.073] → H67 main (L9) 0.046 [0.015, 0.076]. R4 (synthetic S-R4 failed, descriptive only): G₁ 0.037 [-0.064, 0.137], G₃ 0.162 [-0.178, 0.501], G₅ 0.517 [-0.153, 1.188].

| Unit | L1 (H50) | L4W (cells) | L8 (counts) | L9 (H67) | G₃ | G₅ [95%] |
| --- | --- | --- | --- | --- | --- | --- |
| 35 | 0.076 | 0.076 | 0.045 | 0.046 | 0.162 | 0.517 [-0.203, 1.135] |

Data: `data/processed/H67-lagged-criticality-dial/round2/units.parquet`, `periods.parquet`.
