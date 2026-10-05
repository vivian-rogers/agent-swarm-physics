# H67 × G04: goal period #4

**Verdict:** failed (round 2, chat clock; round 1: failed)
**Role:** replication (exploratory)
**Period:** goal #4 · regime I · mean N 4.0 · units 4a, 4c · 24761 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = 0.011 [-0.023, 0.046]**, J₁* = 0.004 [-0.008, 0.015], g_eq (same data) = 0.268, H25 trimmed talk dial = 0.335, H42 world-B n_x = 0.030; named-message part of g_lag = -0.002.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 4a | 4 | 5613 | -0.007 [-0.063, 0.068] | -0.002 [-0.021, 0.023] | 2.999 | 0.337 | -0.004 | 0.263 |
| 4c | 4 | 19148 | 0.021 [-0.021, 0.065] | 0.007 [-0.007, 0.022] | 2.990 | 0.248 | -0.001 | 0.000 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).

## Round 2 (2026-10-05)

### R1: the chat clock (regime I)
*Prediction (card, 2026-10-05 02:45 UTC, before the run):* the round-1 rule re-applied on the chat clock, with g_I = g_cu + g_chat in place of g_lag and J*_chat in place of J₁*. Card-level R1-P1: regime-I median g_chat ≥ 0.05 [0.4].

**Result:** g_chat = 0.014 [-0.095, 0.123], J*_chat = 0.005 [-0.035, 0.046], g_cu = 0.010 [-0.009, 0.030], **g_I = 0.023 [-0.078, 0.124]**, g_eq (round 1, same data) = 0.292; 3368 trimmed chat-mode calls. **Round-2 verdict: failed.** Start-time error attenuates g_chat to about 0.23 × truth (synthetic S-R1d), so g_chat is a lower bound.

| Unit | chat calls | J*_chat [95%] | g_chat [95%] | g_cu | g_chat (logged starts) |
| --- | --- | --- | --- | --- | --- |
| 4a | 1007 | -0.012 [-0.047, 0.025] | -0.033 [-0.129, 0.068] | 0.014 | n/a |
| 4c | 2361 | 0.030 [-0.018, 0.075] | 0.080 [-0.049, 0.200] | 0.006 | n/a |

### R3 ladder and R4 multi-hop gain
*Descriptive (card, Round 2). Period pools (random effects).* H50's pair RD re-implemented (L1) 0.086 [-0.019, 0.190] → with call-class cells (L4W) 0.001 [-0.050, 0.051] → call counts with cells (L8) -0.009 [-0.057, 0.039] → H67 main (L9) 0.011 [-0.023, 0.046]. R4 (synthetic S-R4 failed, descriptive only): G₁ -0.036 [-0.204, 0.132], G₃ -0.254 [-0.928, 0.421], G₅ -0.583 [-1.847, 0.681].

| Unit | L1 (H50) | L4W (cells) | L8 (counts) | L9 (H67) | G₃ | G₅ [95%] |
| --- | --- | --- | --- | --- | --- | --- |
| 4a | 0.004 | -0.006 | -0.034 | -0.007 | -0.619 | -1.353 [-2.449, -0.160] |
| 4c | 0.121 | 0.007 | 0.015 | 0.021 | 0.071 | -0.043 [-0.633, 0.565] |

Data: `data/processed/H67-lagged-criticality-dial/round2/units.parquet`, `periods.parquet`.
