# H67 × G20: goal period #20

**Verdict:** failed (round 2, chat clock; round 1: failed)
**Role:** replication (exploratory)
**Period:** goal #20 · regime I · mean N 9.0 · units 20a, 20b, 20c, 20d · 38927 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = -0.020 [-0.046, 0.006]**, J₁* = -0.002 [-0.006, 0.001], g_eq (same data) = 0.148, H25 trimmed talk dial = 0.169, H42 world-B n_x = 0.002; named-message part of g_lag = 0.003.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20a | 8 | 7473 | -0.029 [-0.091, 0.019] | -0.004 [-0.013, 0.003] | 6.983 | 0.175 | -0.018 | 0.158 |
| 20b | 9 | 4156 | -0.033 [-0.078, 0.006] | -0.004 [-0.010, 0.001] | 8.000 | 0.003 | -0.009 | 0.211 |
| 20c | 9 | 14683 | -0.013 [-0.053, 0.037] | -0.002 [-0.007, 0.005] | 7.990 | 0.137 | 0.008 | 0.053 |
| 20d | 10 | 12615 | 0.029 [-0.064, 0.109] | 0.003 [-0.007, 0.012] | 8.940 | 0.193 | 0.015 | 0.105 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).

## Round 2 (2026-10-05)

### R1: the chat clock (regime I)
*Prediction (card, 2026-10-05 02:45 UTC, before the run):* the round-1 rule re-applied on the chat clock, with g_I = g_cu + g_chat in place of g_lag and J*_chat in place of J₁*. Card-level R1-P1: regime-I median g_chat ≥ 0.05 [0.4].

**Result:** g_chat = -0.062 [-0.239, 0.115], J*_chat = -0.008 [-0.031, 0.016], g_cu = -0.004 [-0.025, 0.016], **g_I = -0.067 [-0.244, 0.111]**, g_eq (round 1, same data) = 0.127; 3873 trimmed chat-mode calls. **Round-2 verdict: failed.** Start-time error attenuates g_chat to about 0.23 × truth (synthetic S-R1d), so g_chat is a lower bound.

| Unit | chat calls | J*_chat [95%] | g_chat [95%] | g_cu | g_chat (logged starts) |
| --- | --- | --- | --- | --- | --- |
| 20a | 791 | -0.006 [-0.035, 0.020] | -0.042 [-0.234, 0.136] | -0.017 | n/a |
| 20b | n/a | n/a [n/a, n/a] | n/a [n/a, n/a] | n/a | n/a |
| 20c | 1136 | -0.027 [-0.055, -0.003] | -0.212 [-0.423, -0.024] | 0.001 | n/a |
| 20d | 1946 | 0.015 [-0.024, 0.041] | 0.133 [-0.207, 0.360] | 0.008 | n/a |

### R3 ladder and R4 multi-hop gain
*Descriptive (card, Round 2). Period pools (random effects).* H50's pair RD re-implemented (L1) 0.191 [0.035, 0.346] → with call-class cells (L4W) -0.005 [-0.064, 0.054] → call counts with cells (L8) -0.020 [-0.046, 0.006] → H67 main (L9) -0.020 [-0.046, 0.007]. R4 (synthetic S-R4 failed, descriptive only): G₁ -0.045 [-0.126, 0.036], G₃ -0.157 [-0.426, 0.112], G₅ -0.454 [-1.109, 0.200].

| Unit | L1 (H50) | L4W (cells) | L8 (counts) | L9 (H67) | G₃ | G₅ [95%] |
| --- | --- | --- | --- | --- | --- | --- |
| 20a | 0.135 | -0.041 | -0.030 | -0.029 | -0.622 | -1.058 [-2.148, 0.119] |
| 20b | 0.333 | 0.051 | -0.032 | -0.033 | -0.017 | -0.111 [-0.420, 0.514] |
| 20c | 0.014 | -0.046 | -0.015 | -0.013 | 0.058 | 0.182 [-0.574, 0.851] |
| 20d | 0.263 | 0.084 | 0.029 | 0.029 | -0.583 | -1.491 [-2.720, -0.179] |

Data: `data/processed/H67-lagged-criticality-dial/round2/units.parquet`, `periods.parquet`.
