# H67 × G05: goal period #5

**Verdict:** failed (round 2, chat clock; round 1: supported)
**Role:** replication (exploratory)
**Period:** goal #5 · regime I · mean N 4.0 · units 5 · 5634 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = 0.052 [0.006, 0.099]**, J₁* = 0.017 [0.002, 0.033], g_eq (same data) = 0.037, H25 trimmed talk dial = 0.081, H42 world-B n_x = 0.026; named-message part of g_lag = 0.019.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 4 | 5634 | 0.052 [0.014, 0.104] | 0.017 [0.005, 0.035] | 3.001 | 0.037 | 0.019 | 0.263 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).

## Round 2 (2026-10-05)

### R1: the chat clock (regime I)
*Prediction (card, 2026-10-05 02:45 UTC, before the run):* the round-1 rule re-applied on the chat clock, with g_I = g_cu + g_chat in place of g_lag and J*_chat in place of J₁*. Card-level R1-P1: regime-I median g_chat ≥ 0.05 [0.4].

**Result:** g_chat = -0.006 [-0.210, 0.198], J*_chat = -0.002 [-0.076, 0.071], g_cu = 0.041 [0.004, 0.079], **g_I = 0.035 [-0.172, 0.243]**, g_eq (round 1, same data) = 0.037; 696 trimmed chat-mode calls. **Round-2 verdict: failed.** Start-time error attenuates g_chat to about 0.23 × truth (synthetic S-R1d), so g_chat is a lower bound.

| Unit | chat calls | J*_chat [95%] | g_chat [95%] | g_cu | g_chat (logged starts) |
| --- | --- | --- | --- | --- | --- |
| 5 | 696 | -0.002 [-0.063, 0.068] | -0.006 [-0.174, 0.187] | 0.041 | n/a |

### R3 ladder and R4 multi-hop gain
*Descriptive (card, Round 2). Period pools (random effects).* H50's pair RD re-implemented (L1) 0.193 [0.019, 0.367] → with call-class cells (L4W) 0.113 [-0.010, 0.237] → call counts with cells (L8) 0.048 [0.007, 0.090] → H67 main (L9) 0.052 [0.006, 0.099]. R4 (synthetic S-R4 failed, descriptive only): G₁ 0.246 [0.135, 0.358], G₃ 0.546 [0.143, 0.949], G₅ 0.752 [-0.251, 1.755].

| Unit | L1 (H50) | L4W (cells) | L8 (counts) | L9 (H67) | G₃ | G₅ [95%] |
| --- | --- | --- | --- | --- | --- | --- |
| 5 | 0.193 | 0.113 | 0.048 | 0.052 | 0.546 | 0.752 [-0.357, 1.620] |

Data: `data/processed/H67-lagged-criticality-dial/round2/units.parquet`, `periods.parquet`.
