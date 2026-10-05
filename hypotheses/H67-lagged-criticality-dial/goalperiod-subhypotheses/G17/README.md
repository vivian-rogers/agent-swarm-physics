# H67 × G17: goal period #17

**Verdict:** failed (round 2, chat clock; round 1: failed)
**Role:** replication (exploratory)
**Period:** goal #17 · regime I · mean N 7.0 · units 17 · 9964 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = 0.038 [-0.075, 0.150]**, J₁* = 0.006 [-0.012, 0.025], g_eq (same data) = 0.347, H25 trimmed talk dial = 0.395, H42 world-B n_x = 0.000; named-message part of g_lag = 0.002.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 17 | 7 | 9964 | 0.038 [-0.068, 0.162] | 0.006 [-0.011, 0.027] | 6.001 | 0.347 | 0.002 | 0.053 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).

## Round 2 (2026-10-05)

### R1: the chat clock (regime I)
*Prediction (card, 2026-10-05 02:45 UTC, before the run):* the round-1 rule re-applied on the chat clock, with g_I = g_cu + g_chat in place of g_lag and J*_chat in place of J₁*. Card-level R1-P1: regime-I median g_chat ≥ 0.05 [0.4].

**Result:** g_chat = 0.006 [-0.215, 0.228], J*_chat = 0.001 [-0.036, 0.038], g_cu = 0.017 [-0.018, 0.052], **g_I = 0.024 [-0.200, 0.248]**, g_eq (round 1, same data) = 0.347; 2562 trimmed chat-mode calls. **Round-2 verdict: failed.** Start-time error attenuates g_chat to about 0.23 × truth (synthetic S-R1d), so g_chat is a lower bound.

| Unit | chat calls | J*_chat [95%] | g_chat [95%] | g_cu | g_chat (logged starts) |
| --- | --- | --- | --- | --- | --- |
| 17 | 2562 | 0.001 [-0.036, 0.038] | 0.006 [-0.214, 0.227] | 0.017 | n/a |

### R3 ladder and R4 multi-hop gain
*Descriptive (card, Round 2). Period pools (random effects).* H50's pair RD re-implemented (L1) 0.643 [0.449, 0.837] → with call-class cells (L4W) 0.149 [-0.061, 0.358] → call counts with cells (L8) 0.032 [-0.069, 0.133] → H67 main (L9) 0.038 [-0.075, 0.150]. R4 (synthetic S-R4 failed, descriptive only): G₁ 0.224 [0.011, 0.437], G₃ 1.220 [0.213, 2.228], G₅ 2.557 [0.389, 4.724].

| Unit | L1 (H50) | L4W (cells) | L8 (counts) | L9 (H67) | G₃ | G₅ [95%] |
| --- | --- | --- | --- | --- | --- | --- |
| 17 | 0.643 | 0.149 | 0.032 | 0.038 | 1.220 | 2.557 [0.631, 5.095] |

Data: `data/processed/H67-lagged-criticality-dial/round2/units.parquet`, `periods.parquet`.
