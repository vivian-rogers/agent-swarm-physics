# H67 × G13: goal period #13

**Verdict:** failed (round 2, chat clock; round 1: failed)
**Role:** replication (exploratory)
**Period:** goal #13 · regime I · mean N 6.0 · units 13 · 22283 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = -0.002 [-0.037, 0.033]**, J₁* = -0.000 [-0.007, 0.007], g_eq (same data) = 0.095, H25 trimmed talk dial = 0.107, H42 world-B n_x = 0.000; named-message part of g_lag = 0.005.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 13 | 6 | 22283 | -0.002 [-0.033, 0.032] | -0.000 [-0.007, 0.006] | 4.990 | 0.095 | 0.005 | 0.211 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).

## Round 2 (2026-10-05)

### R1: the chat clock (regime I)
*Prediction (card, 2026-10-05 02:45 UTC, before the run):* the round-1 rule re-applied on the chat clock, with g_I = g_cu + g_chat in place of g_lag and J*_chat in place of J₁*. Card-level R1-P1: regime-I median g_chat ≥ 0.05 [0.4].

**Result:** g_chat = -0.029 [-0.111, 0.052], J*_chat = -0.006 [-0.023, 0.011], g_cu = 0.003 [-0.026, 0.031], **g_I = -0.027 [-0.113, 0.060]**, g_eq (round 1, same data) = 0.095; 2309 trimmed chat-mode calls. **Round-2 verdict: failed.** Start-time error attenuates g_chat to about 0.23 × truth (synthetic S-R1d), so g_chat is a lower bound.

| Unit | chat calls | J*_chat [95%] | g_chat [95%] | g_cu | g_chat (logged starts) |
| --- | --- | --- | --- | --- | --- |
| 13 | 2309 | -0.006 [-0.024, 0.011] | -0.029 [-0.116, 0.051] | 0.003 | n/a |

### R3 ladder and R4 multi-hop gain
*Descriptive (card, Round 2). Period pools (random effects).* H50's pair RD re-implemented (L1) 0.277 [0.201, 0.353] → with call-class cells (L4W) 0.047 [-0.041, 0.134] → call counts with cells (L8) -0.000 [-0.034, 0.033] → H67 main (L9) -0.002 [-0.037, 0.033]. R4 (synthetic S-R4 failed, descriptive only): G₁ -0.062 [-0.129, 0.004], G₃ -0.077 [-0.345, 0.192], G₅ 0.097 [-0.452, 0.645].

| Unit | L1 (H50) | L4W (cells) | L8 (counts) | L9 (H67) | G₃ | G₅ [95%] |
| --- | --- | --- | --- | --- | --- | --- |
| 13 | 0.277 | 0.047 | -0.000 | -0.002 | -0.077 | 0.097 [-0.551, 0.507] |

Data: `data/processed/H67-lagged-criticality-dial/round2/units.parquet`, `periods.parquet`.
