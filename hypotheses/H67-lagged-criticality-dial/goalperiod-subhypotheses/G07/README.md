# H67 × G07: goal period #7

**Verdict:** supported (round 2, chat clock; round 1: failed)
**Role:** replication (exploratory)
**Period:** goal #7 · regime I · mean N 4.0 · units 7 · 3051 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = 0.035 [-0.029, 0.099]**, J₁* = 0.012 [-0.010, 0.033], g_eq (same data) = 0.111, H25 trimmed talk dial = 0.136, H42 world-B n_x = 0.000; named-message part of g_lag = 0.012.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 7 | 4 | 3051 | 0.035 [-0.023, 0.097] | 0.012 [-0.008, 0.032] | 3.014 | 0.111 | 0.012 | 0.316 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).

## Round 2 (2026-10-05)

### R1: the chat clock (regime I)
*Prediction (card, 2026-10-05 02:45 UTC, before the run):* the round-1 rule re-applied on the chat clock, with g_I = g_cu + g_chat in place of g_lag and J*_chat in place of J₁*. Card-level R1-P1: regime-I median g_chat ≥ 0.05 [0.4].

**Result:** g_chat = 0.358 [0.088, 0.627], J*_chat = 0.125 [0.031, 0.218], g_cu = -0.012 [-0.045, 0.021], **g_I = 0.345 [0.074, 0.617]**, g_eq (round 1, same data) = 0.111; 347 trimmed chat-mode calls. **Round-2 verdict: supported.** Start-time error attenuates g_chat to about 0.23 × truth (synthetic S-R1d), so g_chat is a lower bound.

| Unit | chat calls | J*_chat [95%] | g_chat [95%] | g_cu | g_chat (logged starts) |
| --- | --- | --- | --- | --- | --- |
| 7 | 347 | 0.125 [0.013, 0.198] | 0.358 [0.037, 0.569] | -0.012 | n/a |

### R3 ladder and R4 multi-hop gain
*Descriptive (card, Round 2). Period pools (random effects).* H50's pair RD re-implemented (L1) -0.065 [-0.336, 0.205] → with call-class cells (L4W) 0.033 [-0.081, 0.147] → call counts with cells (L8) 0.028 [-0.030, 0.086] → H67 main (L9) 0.035 [-0.029, 0.099]. R4 (synthetic S-R4 failed, descriptive only): G₁ -0.062 [-0.181, 0.057], G₃ -0.256 [-0.502, -0.009], G₅ -0.508 [-1.055, 0.039].

| Unit | L1 (H50) | L4W (cells) | L8 (counts) | L9 (H67) | G₃ | G₅ [95%] |
| --- | --- | --- | --- | --- | --- | --- |
| 7 | -0.065 | 0.033 | 0.028 | 0.035 | -0.256 | -0.508 [-1.260, -0.131] |

Data: `data/processed/H67-lagged-criticality-dial/round2/units.parquet`, `periods.parquet`.
