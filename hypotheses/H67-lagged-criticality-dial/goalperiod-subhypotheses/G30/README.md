# H67 × G30: goal period #30

**Verdict:** failed (round 2, chat clock; round 1: failed)
**Role:** replication (exploratory)
**Period:** goal #30 · regime I · mean N 11.0 · units 30a, 30b · 30837 receiving calls in the all-present window.

## Why this period
Eligible for the replication layer (≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls).

## Prediction
*The card's per-period rule, written 2026-10-04 19:15 UTC before any real-data statistic; this folder was written after the run and copies it.* Supported if the pooled g_lag has upper bound < 1, J₁* > 0 (CI excluding 0) and g_lag > g_eq on the same data; failed if J₁* is not above 0 and g_lag ≤ g_eq, or any unit's lower bound ≥ 1; mixed otherwise.

## Result
Period pool (random effects over units): **g_lag = -0.005 [-0.041, 0.030]**, J₁* = -0.001 [-0.004, 0.003], g_eq (same data) = 0.182, H25 trimmed talk dial = 0.197, H42 world-B n_x = 0.000; named-message part of g_lag = -0.004.

| Unit | N | calls | g_lag [95%] | J₁* [95%] | r̄ | g_eq | g named | shift-null CI≠0 share |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 30a | 11 | 6417 | 0.021 [-0.091, 0.116] | 0.002 [-0.010, 0.011] | 10.096 | 0.161 | 0.003 | 0.316 |
| 30b | 11 | 24420 | -0.009 [-0.052, 0.034] | -0.001 [-0.005, 0.003] | 10.060 | 0.188 | -0.006 | 0.368 |

Data: `data/processed/H67-lagged-criticality-dial/results/units.parquet`, `periods.parquet`.

## Scorecard (period-specific axes)
C: J₁* against the in-flight placebo and the shift null (above). H: g_lag vs the equal-time dial and H42's world-B n_x (above).

## Round 2 (2026-10-05)

### R1: the chat clock (regime I)
*Prediction (card, 2026-10-05 02:45 UTC, before the run):* the round-1 rule re-applied on the chat clock, with g_I = g_cu + g_chat in place of g_lag and J*_chat in place of J₁*. Card-level R1-P1: regime-I median g_chat ≥ 0.05 [0.4].

**Result:** g_chat = -0.135 [-0.479, 0.210], J*_chat = -0.014 [-0.050, 0.022], g_cu = -0.004 [-0.036, 0.028], **g_I = -0.123 [-0.425, 0.180]**, g_eq (round 1, same data) = 0.174; 2105 trimmed chat-mode calls. **Round-2 verdict: failed.** Start-time error attenuates g_chat to about 0.23 × truth (synthetic S-R1d), so g_chat is a lower bound.

| Unit | chat calls | J*_chat [95%] | g_chat [95%] | g_cu | g_chat (logged starts) |
| --- | --- | --- | --- | --- | --- |
| 30a | 378 | -0.033 [-0.059, -0.007] | -0.318 [-0.564, -0.068] | 0.031 | n/a |
| 30b | 1727 | 0.003 [-0.017, 0.025] | 0.034 [-0.169, 0.243] | -0.012 | -0.118 |

### R3 ladder and R4 multi-hop gain
*Descriptive (card, Round 2). Period pools (random effects).* H50's pair RD re-implemented (L1) 0.078 [-0.055, 0.211] → with call-class cells (L4W) 0.047 [-0.039, 0.133] → call counts with cells (L8) -0.006 [-0.043, 0.030] → H67 main (L9) -0.005 [-0.041, 0.030]. R4 (synthetic S-R4 failed, descriptive only): G₁ 0.076 [-0.022, 0.175], G₃ 0.306 [-0.094, 0.706], G₅ 0.633 [-0.322, 1.588].

| Unit | L1 (H50) | L4W (cells) | L8 (counts) | L9 (H67) | G₃ | G₅ [95%] |
| --- | --- | --- | --- | --- | --- | --- |
| 30a | 0.028 | 0.124 | 0.021 | 0.021 | 0.542 | 1.205 [0.228, 2.454] |
| 30b | 0.112 | 0.031 | -0.011 | -0.009 | 0.210 | 0.218 [-0.712, 1.129] |

Data: `data/processed/H67-lagged-criticality-dial/round2/units.parquet`, `periods.parquet`.
