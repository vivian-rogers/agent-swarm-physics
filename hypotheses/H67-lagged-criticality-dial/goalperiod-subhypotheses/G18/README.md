# H67 × G18: goal period #18

**Verdict:** failed (round 2, chat clock; round 1: failed)
**Role:** replication (exploratory)
**Period:** goal #18 · regime I · mean N 7.3 · units 18a, 18b, 18c · 28872 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = 0.048 [-0.000, 0.097]**, J₁* = 0.007 [-0.001, 0.016], g_eq (same data) = 0.293, H25 trimmed talk dial = 0.305, H42 world-B n_x = 0.002; named-message part of g_lag = 0.022.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 18a | 7 | 3918 | 0.004 [-0.110, 0.129] | 0.001 [-0.018, 0.021] | 5.989 | 0.451 | 0.017 | 0.053 |
| 18b | 8 | 14717 | 0.018 [-0.039, 0.091] | 0.003 [-0.006, 0.013] | 6.981 | 0.273 | 0.028 | 0.000 |
| 18c | 7 | 10237 | 0.082 [0.020, 0.128] | 0.014 [0.003, 0.021] | 5.997 | 0.262 | 0.015 | 0.053 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).

## Round 2 (2026-10-05)

### R1: the chat clock (regime I)
*Prediction (card, 2026-10-05 02:45 UTC, before the run):* the round-1 rule re-applied on the chat clock, with g_I = g_cu + g_chat in place of g_lag and J*_chat in place of J₁*. Card-level R1-P1: regime-I median g_chat ≥ 0.05 [0.4].

**Result:** g_chat = -0.036 [-0.151, 0.080], J*_chat = -0.006 [-0.025, 0.014], g_cu = 0.027 [0.011, 0.042], **g_I = -0.009 [-0.125, 0.108]**, g_eq (round 1, same data) = 0.328; 7134 trimmed chat-mode calls. **Round-2 verdict: failed.** Start-time error attenuates g_chat to about 0.23 × truth (synthetic S-R1d), so g_chat is a lower bound.

| Unit | chat calls | J*_chat [95%] | g_chat [95%] | g_cu | g_chat (logged starts) |
| --- | --- | --- | --- | --- | --- |
| 18a | 833 | -0.028 [-0.057, 0.010] | -0.160 [-0.326, 0.057] | 0.032 | n/a |
| 18b | 4239 | -0.006 [-0.018, 0.010] | -0.039 [-0.121, 0.065] | 0.021 | n/a |
| 18c | 2062 | 0.019 [-0.020, 0.051] | 0.110 [-0.116, 0.292] | 0.033 | n/a |

### R3 ladder and R4 multi-hop gain
*Descriptive (card, Round 2). Period pools (random effects).* H50's pair RD re-implemented (L1) 0.634 [0.513, 0.755] → with call-class cells (L4W) 0.099 [0.038, 0.159] → call counts with cells (L8) 0.050 [0.002, 0.098] → H67 main (L9) 0.049 [-0.000, 0.097]. R4 (synthetic S-R4 failed, descriptive only): G₁ 0.011 [-0.095, 0.118], G₃ 0.066 [-0.298, 0.431], G₅ 0.296 [-0.454, 1.046].

| Unit | L1 (H50) | L4W (cells) | L8 (counts) | L9 (H67) | G₃ | G₅ [95%] |
| --- | --- | --- | --- | --- | --- | --- |
| 18a | 0.677 | 0.087 | 0.005 | 0.004 | -0.499 | -0.221 [-2.585, 2.922] |
| 18b | 0.574 | 0.071 | 0.017 | 0.018 | 0.175 | 0.623 [-0.454, 1.656] |
| 18c | 0.649 | 0.143 | 0.080 | 0.082 | 0.013 | -0.093 [-1.381, 0.803] |

Data: `data/processed/H67-lagged-criticality-dial/round2/units.parquet`, `periods.parquet`.
