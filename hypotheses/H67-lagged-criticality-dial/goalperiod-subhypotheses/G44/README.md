# H67 × G44: goal period #44

**Verdict:** supported
**Role:** replication (exploratory)
**Period:** goal #44 · regime III · mean N 18.0 · units 44b · 7865 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = 0.234 [0.129, 0.340]**, J₁* = 0.027 [0.015, 0.039], g_eq (same data) = 0.121, H25 trimmed talk dial = 0.054, H42 world-B n_x = 0.000; named-message part of g_lag = 0.080.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 44b | 18 | 7865 | 0.234 [0.122, 0.320] | 0.027 [0.014, 0.036] | 8.897 | 0.121 | 0.080 | 0.368 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).

## Round 2 (2026-10-05)

### R3 ladder and R4 multi-hop gain
*Descriptive (card, Round 2). Period pools (random effects).* H50's pair RD re-implemented (L1) 0.184 [0.038, 0.331] → with call-class cells (L4W) 0.325 [0.035, 0.616] → call counts with cells (L8) 0.246 [0.144, 0.347] → H67 main (L9) 0.234 [0.129, 0.340]. R4 (synthetic S-R4 failed, descriptive only): G₁ 0.066 [-0.410, 0.542], G₃ 0.844 [-0.568, 2.257], G₅ 1.866 [-0.273, 4.005].

| Unit | L1 (H50) | L4W (cells) | L8 (counts) | L9 (H67) | G₃ | G₅ [95%] |
| --- | --- | --- | --- | --- | --- | --- |
| 44b | 0.184 | 0.325 | 0.246 | 0.234 | 0.844 | 1.866 [-0.449, 3.803] |

Data: `data/processed/H67-lagged-criticality-dial/round2/units.parquet`, `periods.parquet`.
