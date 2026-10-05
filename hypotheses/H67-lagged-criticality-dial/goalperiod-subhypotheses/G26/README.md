# H67 × G26: goal period #26

**Verdict:** failed (round 2, chat clock; round 1: failed)
**Role:** replication (exploratory)
**Period:** goal #26 · regime I · mean N 10.0 · units 26 · 13330 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = 0.012 [-0.055, 0.079]**, J₁* = 0.001 [-0.006, 0.009], g_eq (same data) = 0.310, H25 trimmed talk dial = 0.310, H42 world-B n_x = 0.030; named-message part of g_lag = -0.008.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 26 | 10 | 13330 | 0.012 [-0.053, 0.083] | 0.001 [-0.006, 0.009] | 9.033 | 0.310 | -0.008 | 0.158 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).

## Round 2 (2026-10-05)

### R1: the chat clock (regime I)
*Prediction (card, 2026-10-05 02:45 UTC, before the run):* the round-1 rule re-applied on the chat clock, with g_I = g_cu + g_chat in place of g_lag and J*_chat in place of J₁*. Card-level R1-P1: regime-I median g_chat ≥ 0.05 [0.4].

**Result:** g_chat = -0.005 [-0.223, 0.213], J*_chat = -0.001 [-0.026, 0.025], g_cu = 0.009 [-0.041, 0.059], **g_I = 0.004 [-0.219, 0.228]**, g_eq (round 1, same data) = 0.310; 1510 trimmed chat-mode calls. **Round-2 verdict: failed.** Start-time error attenuates g_chat to about 0.23 × truth (synthetic S-R1d), so g_chat is a lower bound.

| Unit | chat calls | J*_chat [95%] | g_chat [95%] | g_cu | g_chat (logged starts) |
| --- | --- | --- | --- | --- | --- |
| 26 | 1510 | -0.001 [-0.029, 0.022] | -0.005 [-0.244, 0.186] | 0.009 | 0.056 |

### R3 ladder and R4 multi-hop gain
*Descriptive (card, Round 2). Period pools (random effects).* H50's pair RD re-implemented (L1) 0.389 [0.154, 0.624] → with call-class cells (L4W) 0.057 [-0.092, 0.206] → call counts with cells (L8) 0.012 [-0.051, 0.075] → H67 main (L9) 0.012 [-0.055, 0.079]. R4 (synthetic S-R4 failed, descriptive only): G₁ 0.005 [-0.226, 0.236], G₃ -0.009 [-0.882, 0.865], G₅ 0.193 [-1.462, 1.847].

| Unit | L1 (H50) | L4W (cells) | L8 (counts) | L9 (H67) | G₃ | G₅ [95%] |
| --- | --- | --- | --- | --- | --- | --- |
| 26 | 0.389 | 0.057 | 0.012 | 0.012 | -0.009 | 0.193 [-1.289, 1.854] |

Data: `data/processed/H67-lagged-criticality-dial/round2/units.parquet`, `periods.parquet`.
