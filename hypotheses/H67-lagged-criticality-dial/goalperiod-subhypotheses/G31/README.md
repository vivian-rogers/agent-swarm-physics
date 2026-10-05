# H67 × G31: goal period #31

**Verdict:** failed (round 2, chat clock; round 1: failed)
**Role:** replication (exploratory)
**Period:** goal #31 · regime I · mean N 11.2 · units 31a, 31b, 31c, 31d · 33387 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = -0.035 [-0.094, 0.025]**, J₁* = -0.003 [-0.009, 0.002], g_eq (same data) = 0.050, H25 trimmed talk dial = 0.096, H42 world-B n_x = 0.000; named-message part of g_lag = 0.013.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 31a | 11 | 13791 | 0.024 [-0.022, 0.064] | 0.002 [-0.002, 0.006] | 10.119 | 0.077 | 0.026 | 0.053 |
| 31b | 12 | 6455 | -0.076 [-0.223, 0.041] | -0.007 [-0.020, 0.004] | 11.048 | 0.135 | -0.031 | 0.105 |
| 31c | 11 | 6218 | -0.042 [-0.091, 0.054] | -0.004 [-0.009, 0.006] | 9.989 | -0.065 | 0.051 | 0.158 |
| 31d | 11 | 6923 | -0.084 [-0.163, -0.025] | -0.008 [-0.016, -0.003] | 10.154 | 0.020 | -0.008 | 0.316 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).

## Round 2 (2026-10-05)

### R1: the chat clock (regime I)
*Prediction (card, 2026-10-05 02:45 UTC, before the run):* the round-1 rule re-applied on the chat clock, with g_I = g_cu + g_chat in place of g_lag and J*_chat in place of J₁*. Card-level R1-P1: regime-I median g_chat ≥ 0.05 [0.4].

**Result:** g_chat = -0.007 [-0.139, 0.125], J*_chat = -0.001 [-0.015, 0.013], g_cu = -0.027 [-0.059, 0.005], **g_I = -0.042 [-0.179, 0.096]**, g_eq (round 1, same data) = 0.042; 2239 trimmed chat-mode calls. **Round-2 verdict: failed.** Start-time error attenuates g_chat to about 0.23 × truth (synthetic S-R1d), so g_chat is a lower bound.

| Unit | chat calls | J*_chat [95%] | g_chat [95%] | g_cu | g_chat (logged starts) |
| --- | --- | --- | --- | --- | --- |
| 31a | 898 | 0.009 [-0.016, 0.034] | 0.087 [-0.156, 0.327] | 0.006 | n/a |
| 31b | 454 | -0.006 [-0.060, 0.076] | -0.067 [-0.655, 0.833] | -0.057 | n/a |
| 31c | 414 | 0.007 [-0.027, 0.058] | 0.063 [-0.244, 0.529] | -0.033 | n/a |
| 31d | 473 | -0.006 [-0.026, 0.011] | -0.058 [-0.243, 0.102] | -0.060 | n/a |

### R3 ladder and R4 multi-hop gain
*Descriptive (card, Round 2). Period pools (random effects).* H50's pair RD re-implemented (L1) 0.287 [0.190, 0.385] → with call-class cells (L4W) 0.061 [-0.018, 0.141] → call counts with cells (L8) -0.034 [-0.094, 0.025] → H67 main (L9) -0.035 [-0.094, 0.025]. R4 (synthetic S-R4 failed, descriptive only): G₁ -0.092 [-0.264, 0.079], G₃ -0.334 [-1.045, 0.377], G₅ -0.621 [-2.101, 0.859].

| Unit | L1 (H50) | L4W (cells) | L8 (counts) | L9 (H67) | G₃ | G₅ [95%] |
| --- | --- | --- | --- | --- | --- | --- |
| 31a | 0.140 | 0.097 | 0.025 | 0.024 | 0.375 | 0.914 [0.006, 1.774] |
| 31b | 0.204 | 0.058 | -0.077 | -0.076 | -1.216 | -1.992 [-3.639, -0.057] |
| 31c | 0.391 | -0.001 | -0.041 | -0.042 | -0.570 | -1.553 [-2.135, -1.072] |
| 31d | 0.270 | 0.062 | -0.082 | -0.084 | -0.155 | -0.045 [-1.452, 1.448] |

Data: `data/processed/H67-lagged-criticality-dial/round2/units.parquet`, `periods.parquet`.
