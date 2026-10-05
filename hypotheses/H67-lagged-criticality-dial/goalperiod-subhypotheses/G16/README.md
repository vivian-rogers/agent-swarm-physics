# H67 × G16: goal period #16

**Verdict:** failed (round 2, chat clock; round 1: failed)
**Role:** replication (exploratory)
**Period:** goal #16 · regime I · mean N 7.0 · units 16 · 13163 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = 0.031 [-0.022, 0.083]**, J₁* = 0.005 [-0.004, 0.014], g_eq (same data) = 0.231, H25 trimmed talk dial = 0.285, H42 world-B n_x = 0.011; named-message part of g_lag = 0.007.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 16 | 7 | 13163 | 0.031 [-0.023, 0.083] | 0.005 [-0.004, 0.014] | 5.990 | 0.231 | 0.007 | 0.105 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).

## Round 2 (2026-10-05)

### R1: the chat clock (regime I)
*Prediction (card, 2026-10-05 02:45 UTC, before the run):* the round-1 rule re-applied on the chat clock, with g_I = g_cu + g_chat in place of g_lag and J*_chat in place of J₁*. Card-level R1-P1: regime-I median g_chat ≥ 0.05 [0.4].

**Result:** g_chat = -0.050 [-0.184, 0.083], J*_chat = -0.009 [-0.031, 0.014], g_cu = 0.024 [-0.010, 0.058], **g_I = -0.026 [-0.164, 0.112]**, g_eq (round 1, same data) = 0.231; 1589 trimmed chat-mode calls. **Round-2 verdict: failed.** Start-time error attenuates g_chat to about 0.23 × truth (synthetic S-R1d), so g_chat is a lower bound.

| Unit | chat calls | J*_chat [95%] | g_chat [95%] | g_cu | g_chat (logged starts) |
| --- | --- | --- | --- | --- | --- |
| 16 | 1589 | -0.009 [-0.026, 0.019] | -0.050 [-0.151, 0.110] | 0.024 | n/a |

### R3 ladder and R4 multi-hop gain
*Descriptive (card, Round 2). Period pools (random effects).* H50's pair RD re-implemented (L1) 0.397 [0.208, 0.586] → with call-class cells (L4W) 0.075 [-0.067, 0.218] → call counts with cells (L8) 0.027 [-0.031, 0.085] → H67 main (L9) 0.031 [-0.022, 0.083]. R4 (synthetic S-R4 failed, descriptive only): G₁ -0.092 [-0.214, 0.030], G₃ -0.405 [-0.974, 0.165], G₅ -0.447 [-1.782, 0.888].

| Unit | L1 (H50) | L4W (cells) | L8 (counts) | L9 (H67) | G₃ | G₅ [95%] |
| --- | --- | --- | --- | --- | --- | --- |
| 16 | 0.397 | 0.075 | 0.027 | 0.031 | -0.405 | -0.447 [-1.764, 0.802] |

Data: `data/processed/H67-lagged-criticality-dial/round2/units.parquet`, `periods.parquet`.
