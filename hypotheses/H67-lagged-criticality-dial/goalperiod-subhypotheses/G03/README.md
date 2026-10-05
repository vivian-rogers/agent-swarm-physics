# H67 × G03: goal period #3

**Verdict:** failed (round 2, chat clock; round 1: failed)
**Role:** replication (exploratory)
**Period:** goal #3 · regime I · mean N 4.0 · units 3 · 1676 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = 0.017 [-0.090, 0.124]**, J₁* = 0.006 [-0.030, 0.041], g_eq (same data) = 0.353, H25 trimmed talk dial = 0.290, H42 world-B n_x = 0.067; named-message part of g_lag = -0.007.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 3 | 4 | 1676 | 0.017 [-0.078, 0.115] | 0.006 [-0.026, 0.038] | 2.991 | 0.353 | -0.007 | 0.211 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).

## Round 2 (2026-10-05)

### R1: the chat clock (regime I)
*Prediction (card, 2026-10-05 02:45 UTC, before the run):* the round-1 rule re-applied on the chat clock, with g_I = g_cu + g_chat in place of g_lag and J*_chat in place of J₁*. Card-level R1-P1: regime-I median g_chat ≥ 0.05 [0.4].

**Result:** g_chat = 0.006 [-0.131, 0.143], J*_chat = 0.002 [-0.047, 0.052], g_cu = n/a [n/a, n/a], **g_I = 0.006 [-0.131, 0.143]**, g_eq (round 1, same data) = 0.353; 1074 trimmed chat-mode calls. **Round-2 verdict: failed.** Start-time error attenuates g_chat to about 0.23 × truth (synthetic S-R1d), so g_chat is a lower bound.

| Unit | chat calls | J*_chat [95%] | g_chat [95%] | g_cu | g_chat (logged starts) |
| --- | --- | --- | --- | --- | --- |
| 3 | 1074 | 0.002 [-0.059, 0.032] | 0.006 [-0.164, 0.088] | n/a | n/a |

### R3 ladder and R4 multi-hop gain
*Descriptive (card, Round 2). Period pools (random effects).* H50's pair RD re-implemented (L1) 0.149 [0.054, 0.243] → with call-class cells (L4W) -0.008 [-0.274, 0.258] → call counts with cells (L8) 0.020 [-0.066, 0.105] → H67 main (L9) 0.017 [-0.090, 0.124]. R4 (synthetic S-R4 failed, descriptive only): G₁ 0.157 [0.068, 0.246], G₃ 0.764 [0.159, 1.369], G₅ 1.570 [-0.141, 3.281].

| Unit | L1 (H50) | L4W (cells) | L8 (counts) | L9 (H67) | G₃ | G₅ [95%] |
| --- | --- | --- | --- | --- | --- | --- |
| 3 | 0.149 | -0.008 | 0.020 | 0.017 | 0.764 | 1.570 [0.730, 4.148] |

Data: `data/processed/H67-lagged-criticality-dial/round2/units.parquet`, `periods.parquet`.
