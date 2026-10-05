# H67 × G02: goal period #2

**Verdict:** failed (round 2, chat clock; round 1: failed)
**Role:** replication (exploratory)
**Period:** goal #2 · regime I · mean N 4.0 · units 2 · 1501 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = 0.021 [-0.081, 0.124]**, J₁* = 0.008 [-0.036, 0.052], g_eq (same data) = 0.406, H25 trimmed talk dial = 0.434, H42 world-B n_x = 0.022; named-message part of g_lag = 0.020.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2 | 4 | 1501 | 0.021 [-0.022, 0.101] | 0.008 [-0.007, 0.051] | 2.712 | 0.406 | 0.020 | 0.316 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).

## Round 2 (2026-10-05)

### R1: the chat clock (regime I)
*Prediction (card, 2026-10-05 02:45 UTC, before the run):* the round-1 rule re-applied on the chat clock, with g_I = g_cu + g_chat in place of g_lag and J*_chat in place of J₁*. Card-level R1-P1: regime-I median g_chat ≥ 0.05 [0.4].

**Result:** g_chat = -0.055 [-0.143, 0.033], J*_chat = -0.022 [-0.058, 0.014], g_cu = 0.043 [-0.020, 0.106], **g_I = -0.012 [-0.121, 0.097]**, g_eq (round 1, same data) = 0.406; 340 trimmed chat-mode calls. **Round-2 verdict: failed.** Start-time error attenuates g_chat to about 0.23 × truth (synthetic S-R1d), so g_chat is a lower bound.

| Unit | chat calls | J*_chat [95%] | g_chat [95%] | g_cu | g_chat (logged starts) |
| --- | --- | --- | --- | --- | --- |
| 2 | 340 | -0.022 [-0.030, 0.051] | -0.055 [-0.073, 0.126] | 0.043 | n/a |

### R3 ladder and R4 multi-hop gain
*Descriptive (card, Round 2). Period pools (random effects).* H50's pair RD re-implemented (L1) 0.184 [-0.378, 0.746] → with call-class cells (L4W) 0.107 [-0.116, 0.331] → call counts with cells (L8) -0.013 [-0.086, 0.060] → H67 main (L9) 0.021 [-0.099, 0.141]. R4 (synthetic S-R4 failed, descriptive only): G₁ 0.088 [-0.023, 0.200], G₃ 1.265 [0.578, 1.953], G₅ 3.139 [1.499, 4.780].

| Unit | L1 (H50) | L4W (cells) | L8 (counts) | L9 (H67) | G₃ | G₅ [95%] |
| --- | --- | --- | --- | --- | --- | --- |
| 2 | 0.184 | 0.107 | -0.013 | 0.021 | 1.265 | 3.139 [0.592, 3.564] |

Data: `data/processed/H67-lagged-criticality-dial/round2/units.parquet`, `periods.parquet`.
