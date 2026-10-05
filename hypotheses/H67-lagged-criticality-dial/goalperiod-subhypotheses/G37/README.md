# H67 × G37: goal period #37

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** goal #37 · regime III · mean N 12.0 · units 37 · 15932 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = 0.220 [0.141, 0.299]**, J₁* = 0.038 [0.023, 0.052], g_eq (same data) = 0.230, H25 trimmed talk dial = 0.231, H42 world-B n_x = 0.027; named-message part of g_lag = 0.139.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 37 | 12 | 15932 | 0.220 [0.146, 0.292] | 0.038 [0.022, 0.051] | 5.812 | 0.230 | 0.139 | 0.053 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).

## Round 2 (2026-10-05)

### R3 ladder and R4 multi-hop gain
*Descriptive (card, Round 2). Period pools (random effects).* H50's pair RD re-implemented (L1) 0.500 [0.349, 0.651] → with call-class cells (L4W) 0.540 [0.354, 0.727] → call counts with cells (L8) 0.213 [0.128, 0.298] → H67 main (L9) 0.220 [0.135, 0.305]. R4 (synthetic S-R4 failed, descriptive only): G₁ -0.084 [-0.254, 0.086], G₃ 0.086 [-0.521, 0.692], G₅ 0.573 [-0.361, 1.507].

| Unit | L1 (H50) | L4W (cells) | L8 (counts) | L9 (H67) | G₃ | G₅ [95%] |
| --- | --- | --- | --- | --- | --- | --- |
| 37 | 0.500 | 0.540 | 0.213 | 0.220 | 0.086 | 0.573 [-0.363, 1.480] |

Data: `data/processed/H67-lagged-criticality-dial/round2/units.parquet`, `periods.parquet`.
