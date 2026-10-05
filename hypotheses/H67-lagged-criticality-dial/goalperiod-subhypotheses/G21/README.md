# H67 × G21: goal period #21

**Verdict:** failed (round 2, chat clock; round 1: failed)
**Role:** replication (exploratory)
**Period:** goal #21 · regime I · mean N 8.5 · units 21a, 21b · 18141 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = -0.018 [-0.051, 0.014]**, J₁* = -0.002 [-0.007, 0.002], g_eq (same data) = 0.154, H25 trimmed talk dial = 0.211, H42 world-B n_x = 0.002; named-message part of g_lag = -0.005.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 21a | 8 | 10825 | -0.025 [-0.057, 0.012] | -0.004 [-0.008, 0.002] | 6.982 | 0.142 | 0.001 | 0.105 |
| 21b | 9 | 7316 | 0.003 [-0.072, 0.057] | 0.000 [-0.009, 0.007] | 7.993 | 0.172 | -0.014 | 0.158 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).

## Round 2 (2026-10-05)

### R1: the chat clock (regime I)
*Prediction (card, 2026-10-05 02:45 UTC, before the run):* the round-1 rule re-applied on the chat clock, with g_I = g_cu + g_chat in place of g_lag and J*_chat in place of J₁*. Card-level R1-P1: regime-I median g_chat ≥ 0.05 [0.4].

**Result:** g_chat = -0.059 [-0.276, 0.159], J*_chat = -0.008 [-0.039, 0.023], g_cu = -0.009 [-0.019, 0.001], **g_I = -0.067 [-0.274, 0.141]**, g_eq (round 1, same data) = 0.157; 2889 trimmed chat-mode calls. **Round-2 verdict: failed.** Start-time error attenuates g_chat to about 0.23 × truth (synthetic S-R1d), so g_chat is a lower bound.

| Unit | chat calls | J*_chat [95%] | g_chat [95%] | g_cu | g_chat (logged starts) |
| --- | --- | --- | --- | --- | --- |
| 21a | 1380 | -0.020 [-0.042, 0.008] | -0.137 [-0.284, 0.056] | -0.003 | n/a |
| 21b | 1509 | 0.013 [-0.024, 0.053] | 0.097 [-0.184, 0.409] | -0.011 | n/a |

### R3 ladder and R4 multi-hop gain
*Descriptive (card, Round 2). Period pools (random effects).* H50's pair RD re-implemented (L1) 0.190 [0.019, 0.362] → with call-class cells (L4W) -0.041 [-0.130, 0.048] → call counts with cells (L8) -0.021 [-0.053, 0.012] → H67 main (L9) -0.018 [-0.051, 0.014]. R4 (synthetic S-R4 failed, descriptive only): G₁ -0.008 [-0.092, 0.077], G₃ -0.001 [-0.349, 0.347], G₅ -0.086 [-0.712, 0.540].

| Unit | L1 (H50) | L4W (cells) | L8 (counts) | L9 (H67) | G₃ | G₅ [95%] |
| --- | --- | --- | --- | --- | --- | --- |
| 21a | 0.323 | -0.051 | -0.027 | -0.025 | -0.091 | -0.217 [-1.054, 0.413] |
| 21b | 0.133 | -0.001 | -0.005 | 0.003 | 0.188 | 0.354 [-0.757, 1.703] |

Data: `data/processed/H67-lagged-criticality-dial/round2/units.parquet`, `periods.parquet`.
