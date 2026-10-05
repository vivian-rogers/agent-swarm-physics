# H67 × G06: goal period #6

**Verdict:** failed (round 2, chat clock; round 1: failed)
**Role:** replication (exploratory)
**Period:** goal #6 · regime I · mean N 4.0 · units 6a, 6b · 19966 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = -0.008 [-0.038, 0.023]**, J₁* = -0.003 [-0.013, 0.008], g_eq (same data) = 0.158, H25 trimmed talk dial = 0.210, H42 world-B n_x = 0.000; named-message part of g_lag = -0.008.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 6a | 4 | 8229 | 0.002 [-0.075, 0.106] | 0.001 [-0.025, 0.035] | 3.002 | 0.254 | 0.001 | 0.000 |
| 6b | 4 | 11737 | -0.009 [-0.040, 0.018] | -0.003 [-0.013, 0.006] | 2.994 | 0.091 | -0.015 | 0.053 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).

## Round 2 (2026-10-05)

### R1: the chat clock (regime I)
*Prediction (card, 2026-10-05 02:45 UTC, before the run):* the round-1 rule re-applied on the chat clock, with g_I = g_cu + g_chat in place of g_lag and J*_chat in place of J₁*. Card-level R1-P1: regime-I median g_chat ≥ 0.05 [0.4].

**Result:** g_chat = -0.029 [-0.203, 0.145], J*_chat = -0.010 [-0.071, 0.051], g_cu = -0.000 [-0.020, 0.020], **g_I = -0.035 [-0.196, 0.126]**, g_eq (round 1, same data) = 0.172; 1885 trimmed chat-mode calls. **Round-2 verdict: failed.** Start-time error attenuates g_chat to about 0.23 × truth (synthetic S-R1d), so g_chat is a lower bound.

| Unit | chat calls | J*_chat [95%] | g_chat [95%] | g_cu | g_chat (logged starts) |
| --- | --- | --- | --- | --- | --- |
| 6a | 798 | 0.035 [-0.079, 0.101] | 0.102 [-0.228, 0.292] | -0.008 | n/a |
| 6b | 1087 | -0.032 [-0.080, 0.006] | -0.089 [-0.225, 0.016] | 0.002 | n/a |

### R3 ladder and R4 multi-hop gain
*Descriptive (card, Round 2). Period pools (random effects).* H50's pair RD re-implemented (L1) 0.248 [0.105, 0.390] → with call-class cells (L4W) -0.010 [-0.099, 0.079] → call counts with cells (L8) -0.007 [-0.036, 0.021] → H67 main (L9) -0.008 [-0.038, 0.023]. R4 (synthetic S-R4 failed, descriptive only): G₁ -0.007 [-0.219, 0.205], G₃ 0.022 [-0.569, 0.612], G₅ -0.065 [-0.914, 0.785].

| Unit | L1 (H50) | L4W (cells) | L8 (counts) | L9 (H67) | G₃ | G₅ [95%] |
| --- | --- | --- | --- | --- | --- | --- |
| 6a | 0.248 | -0.083 | 0.000 | 0.002 | 0.341 | 0.387 [-0.388, 1.090] |
| 6b | 0.248 | 0.019 | -0.008 | -0.009 | -0.262 | -0.480 [-1.060, 0.095] |

Data: `data/processed/H67-lagged-criticality-dial/round2/units.parquet`, `periods.parquet`.
