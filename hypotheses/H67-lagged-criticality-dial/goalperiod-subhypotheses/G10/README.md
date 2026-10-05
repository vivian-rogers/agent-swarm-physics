# H67 × G10: goal period #10

**Verdict:** failed (round 2, chat clock; round 1: failed)
**Role:** replication (exploratory)
**Period:** goal #10 · regime I · mean N 7.0 · units 10a, 10b · 9046 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = 0.002 [-0.050, 0.054]**, J₁* = 0.000 [-0.009, 0.009], g_eq (same data) = 0.069, H25 trimmed talk dial = 0.174, H42 world-B n_x = 0.010; named-message part of g_lag = -0.005.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 10a | 7 | 2317 | 0.015 [-0.107, 0.186] | 0.002 [-0.018, 0.031] | 6.018 | 0.153 | -0.018 | 0.263 |
| 10b | 7 | 6729 | -0.002 [-0.053, 0.067] | -0.000 [-0.009, 0.011] | 5.994 | 0.040 | -0.001 | 0.105 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).

## Round 2 (2026-10-05)

### R1: the chat clock (regime I)
*Prediction (card, 2026-10-05 02:45 UTC, before the run):* the round-1 rule re-applied on the chat clock, with g_I = g_cu + g_chat in place of g_lag and J*_chat in place of J₁*. Card-level R1-P1: regime-I median g_chat ≥ 0.05 [0.4].

**Result:** g_chat = -0.147 [-0.277, -0.016], J*_chat = -0.027 [-0.050, -0.003], g_cu = 0.006 [-0.039, 0.052], **g_I = -0.141 [-0.279, -0.002]**, g_eq (round 1, same data) = 0.097; 344 trimmed chat-mode calls. **Round-2 verdict: failed.** Start-time error attenuates g_chat to about 0.23 × truth (synthetic S-R1d), so g_chat is a lower bound.

| Unit | chat calls | J*_chat [95%] | g_chat [95%] | g_cu | g_chat (logged starts) |
| --- | --- | --- | --- | --- | --- |
| 10a | n/a | n/a [n/a, n/a] | n/a [n/a, n/a] | n/a | n/a |
| 10b | 344 | -0.027 [-0.053, -0.006] | -0.147 [-0.293, -0.034] | 0.006 | n/a |

### R3 ladder and R4 multi-hop gain
*Descriptive (card, Round 2). Period pools (random effects).* H50's pair RD re-implemented (L1) 0.051 [-0.181, 0.283] → with call-class cells (L4W) -0.072 [-0.214, 0.069] → call counts with cells (L8) 0.002 [-0.047, 0.051] → H67 main (L9) 0.000 [-0.057, 0.057]. R4 (synthetic S-R4 failed, descriptive only): G₁ -0.082 [-0.262, 0.099], G₃ 0.320 [-0.612, 1.253], G₅ 0.987 [-1.377, 3.351].

| Unit | L1 (H50) | L4W (cells) | L8 (counts) | L9 (H67) | G₃ | G₅ [95%] |
| --- | --- | --- | --- | --- | --- | --- |
| 10a | 0.348 | -0.172 | 0.015 | 0.015 | 1.169 | 2.823 [-1.955, 4.863] |
| 10b | 0.014 | -0.020 | 0.001 | -0.002 | 0.054 | 0.195 [-0.938, 1.352] |

Data: `data/processed/H67-lagged-criticality-dial/round2/units.parquet`, `periods.parquet`.
