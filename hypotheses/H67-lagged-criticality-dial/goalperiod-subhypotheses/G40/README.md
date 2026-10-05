# H67 × G40: goal period #40

**Verdict:** mixed
**Role:** replication (exploratory)
**Period:** goal #40 · regime III · mean N 15.0 · units 40 · 40015 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = 0.003 [-0.110, 0.117]**, J₁* = 0.000 [-0.009, 0.009], g_eq (same data) = -0.048, H25 trimmed talk dial = -0.031, H42 world-B n_x = 0.004; named-message part of g_lag = 0.035.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 40 | 15 | 40015 | 0.003 [-0.106, 0.109] | 0.000 [-0.008, 0.009] | 12.722 | -0.048 | 0.035 | 0.105 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).

## Round 2 (2026-10-05)

### R3 ladder and R4 multi-hop gain
*Descriptive (card, Round 2). Period pools (random effects).* H50's pair RD re-implemented (L1) 0.179 [-0.030, 0.389] → with call-class cells (L4W) 0.130 [-0.105, 0.366] → call counts with cells (L8) 0.005 [-0.107, 0.117] → H67 main (L9) 0.003 [-0.110, 0.117]. R4 (synthetic S-R4 failed, descriptive only): G₁ -0.054 [-0.248, 0.141], G₃ -0.276 [-0.956, 0.405], G₅ -0.459 [-1.646, 0.728].

| Unit | L1 (H50) | L4W (cells) | L8 (counts) | L9 (H67) | G₃ | G₅ [95%] |
| --- | --- | --- | --- | --- | --- | --- |
| 40 | 0.179 | 0.130 | 0.005 | 0.003 | -0.276 | -0.459 [-1.541, 0.602] |

Data: `data/processed/H67-lagged-criticality-dial/round2/units.parquet`, `periods.parquet`.
