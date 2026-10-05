# H50 × G51: Private roles; the human-input test (#51a–l) (2026-07-06 → 2026-09-04 (non-holdout units 51a–51l))

**Verdict:** mixed (replication supported; native: plain human messages are a hop-1 field, the target/relay tests are underpowered)
**Role:** native
**Period:** regime III · units 51a (3 d, N=21), 51b (1 d, N=24), 51c (5 d, N=25), 51d (5 d, N=26), 51e (3 d, N=27), 51f (5 d, N=27), 51g (13 d, N=27), 51h (4 d, N=27), 51i (2 d, N=28), 51j (2 d, N=29), 51k (1 d, N=31), 51l (1 d, N=32).

## Why this period
The most human messages of regime III (113 non-holdout; 69 name agents), a named target and many room bystanders: the place to tell a field (everyone moved at their own read-out call) from a relay (bystanders moved only after the target's visible reply). Also the replication estimator on its 12 units.

## Prediction
*Written 2026-10-04 07:00 UTC, before running this test.*
- Human message naming agents → target talk: read-out jump J₁ > 0 at 95% (onset hop 1).
- Same messages → bystanders (in the room, not named): J₁ smaller than the target's (ratio < 0.5).
- Relay: the target's reply, used as the source event for the bystanders, gives a read-out jump J₁ > 0, at least as large as the generic peer-message jump in #51 (the reply to a human is a salient peer message).
- Plain human messages (no name) → recipients: J₁ > 0 (a field read at hop 1), with no target/bystander split.
- Replication rule (card) on the pooled units: expected *supported*.
- *Against:* bystander jump ≥ target jump, or no relay jump at the target's reply.

## Result
### Replication layer (common estimator)
Data: `data/processed/H50-field-vs-coupling-transfer-lag/G51/` (one JSON per unit). Figure: [`figures/G51_gate_fir.pdf`](figures/G51_gate_fir.pdf). J₁ = placebo-corrected read-out jump in P(talk call) at the first boundary (call starting just after vs just before a peer message), W = 1.5 × median call interval; CIs from a day bootstrap (1-hour blocks in units with < 3 days). κ = J₁ / right-limit excess. Field excess = f_F − f_F,null (shifted-input null); f_C = counterfactual coupling share of talk co-movement (CF, hop-1 kernel; values > 1 are estimator overshoot at low co-movement, see the synthetic validation).

**Pooled period estimate:** J₁ (IVW) = 0.016 [0.015, 0.018]; activity field excess (full window, day-weighted) = 0.53; units with J₁ < 0 at 95%: 0. Rule: (a) yes, (b) yes, (c) yes → **supported**.

### Peer gate (call-cycle lags)
| unit | days | N | pairs | median call (s) | read-out delay q50 (s) | **J₁ talk** [95% CI] | onset hop | J₂ (hop 2 − hop 1) | J₁ work | J₁ idle | κ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 51a | 3 | 21 | 78,269 | 12.2 | 20 | 0.013 [0.005, 0.018] | 1 | -0.008 [-0.023, 0.001] | -0.008 [-0.014, 0.000] | -0.005 [-0.011, -0.002] | 0.90 |
| 51b | 1 | 24 | 19,061 | 12.3 | 25 | 0.022 [0.008, 0.037] | 1 | -0.016 [-0.035, 0.000] | -0.026 [-0.042, -0.011] | 0.003 [-0.002, 0.011] | 0.79 |
| 51c | 5 | 25 | 94,270 | 11.3 | 33 | 0.021 [0.016, 0.026] | 1 | -0.006 [-0.013, -0.000] | -0.023 [-0.033, -0.016] | 0.002 [-0.003, 0.007] | 1.44 |
| 51d | 5 | 26 | 124,633 | 12.4 | 57 | 0.020 [0.018, 0.023] | 1 | -0.007 [-0.016, -0.000] | -0.017 [-0.026, -0.007] | -0.003 [-0.011, 0.003] | 0.97 |
| 51e | 3 | 27 | 72,860 | 12.7 | 50 | 0.017 [0.011, 0.024] | 1 | 0.002 [-0.008, 0.009] | -0.017 [-0.019, -0.016] | 0.000 [-0.005, 0.005] | 0.96 |
| 51f | 5 | 27 | 111,109 | 13.3 | 82 | 0.009 [0.006, 0.013] | 1 | -0.009 [-0.010, -0.008] | -0.009 [-0.015, -0.005] | 0.000 [-0.003, 0.005] | 0.78 |
| 51g | 13 | 27 | 205,998 | 12.1 | 80 | 0.016 [0.007, 0.025] | 1 | -0.012 [-0.017, -0.008] | -0.014 [-0.022, -0.007] | -0.001 [-0.007, 0.004] | 1.05 |
| 51h | 4 | 27 | 76,123 | 12.4 | 95 | 0.018 [0.012, 0.026] | 1 | -0.012 [-0.014, -0.009] | -0.021 [-0.037, -0.011] | 0.003 [-0.004, 0.009] | 1.09 |
| 51i | 2 | 28 | 39,005 | 13.6 | 74 | 0.019 [0.003, 0.031] | 1 | 0.004 [-0.005, 0.012] | -0.024 [-0.040, -0.004] | 0.005 [-0.003, 0.013] | 1.54 |
| 51j | 2 | 29 | 42,782 | 14.7 | 62 | 0.008 [-0.002, 0.019] | 4 | 0.003 [-0.002, 0.010] | -0.011 [-0.022, 0.000] | 0.003 [-0.004, 0.010] | 1.19 |
| 51k | 1 | 31 | 27,381 | 18.2 | 53 | 0.004 [-0.016, 0.028] | – | -0.008 [-0.022, 0.010] | -0.001 [-0.025, 0.015] | -0.003 [-0.014, 0.008] | -2.79 |
| 51l | 1 | 32 | 34,946 | 19.3 | 45 | -0.005 [-0.018, 0.009] | – | -0.005 [-0.022, 0.009] | -0.002 [-0.024, 0.014] | 0.008 [-0.002, 0.021] | 0.56 |

### Equal-time co-movement decomposition
| unit | activity S (full) | **field excess, activity full** (edges alone / rest alone) | field excess, activity trim | talk S (span) | field excess, talk | **talk coupling share f_C** [k₁ CI] | lagged-peer share (talk) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 51a | 5.56 | 0.37 (0.12 / 0.26) | -2.09 | 0.34 | 0.15 | 1.05 [0.43, 1.24] | 0.09 |
| 51b | 3.77 | 0.27 (0.26 / 0.10) | – | 0.55 | 0.05 | 1.32 [0.64, 1.42] | 0.14 |
| 51c | 3.23 | 0.74 (0.59 / 0.32) | 1.60 | 0.23 | 0.31 | 1.64 [1.39, 1.80] | 0.10 |
| 51d | 1.94 | 0.63 (0.67 / 0.14) | 0.20 | 0.38 | 0.11 | 1.17 [1.10, 1.20] | 0.26 |
| 51e | 4.43 | 0.62 (0.24 / 0.45) | 0.30 | 0.29 | 0.05 | 1.20 [0.89, 1.43] | 0.14 |
| 51f | 1.73 | 0.78 (0.83 / 0.19) | 0.75 | 0.17 | 0.06 | 0.98 [0.63, 1.26] | 0.20 |
| 51g | 1.65 | 0.45 (0.34 / 0.18) | 0.12 | 0.25 | 0.13 | 0.87 [0.45, 1.07] | 0.16 |
| 51h | 1.61 | 0.43 (0.41 / 0.06) | 0.40 | 0.22 | 0.07 | 1.22 [0.96, 1.37] | 0.19 |
| 51i | 1.62 | 0.38 (0.34 / 0.06) | 0.36 | 0.14 | 0.22 | 1.74 [0.37, 2.08] | 0.07 |
| 51j | 2.14 | 0.30 (0.32 / 0.05) | 0.05 | 0.12 | -0.05 | 1.13 [0.00, 2.01] | 0.07 |
| 51k | 1.56 | 0.33 (0.38 / 0.05) | – | 0.21 | 0.26 | 0.44 [0.00, 1.33] | 0.24 |
| 51l | 2.20 | 0.44 (0.31 / 0.16) | 0.09 | 0.52 | 0.55 | 0.00 [0.00, 0.58] | -0.03 |

### Input transfer functions (Part A) and input gates (Part B)
| unit | input | n | activity G30 [CI] | dead (min) | decay (min) | talk G30 | gate J₁ talk (exo, per recipient) | onset hop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 51a | edge_on | 3 | 8.98 [-0.19, 11.65] | 4 | 27 | 1.23 |  | – |
| 51a | pause | 3 | -7.90 [-8.53, -6.21] | 2 | 11 | -0.81 | pause: – [–, –] | – |
| 51a | human | 18 | 0.39 [-1.42, 1.33] | 3 | 8 | 0.29 | human_other: -0.014 [-0.244, 0.123] | – |
| 51a | nudge | 48 | 2.68 [-1.20, 4.88] | 4 | – | 0.28 | nudge_target: 0.568 [0.366, 0.757] | 1 |
| 51a | platform | 349 | 0.41 [-0.19, 0.53] | 1 | 4 | 0.06 |  | – |
| 51c | edge_on | 5 | 8.90 [5.26, 11.63] | 4 | 31 | 0.84 |  | – |
| 51c | pause | 5 | -15.56 [-16.56, -7.64] | 4 | 45 | -0.86 | pause: – [–, –] | – |
| 51c | human | 19 | 0.37 [-0.57, 0.54] | 3 | 2 | 0.17 | human_other: 0.074 [0.054, 0.212] | 1 |
| 51c | nudge | 109 | 1.94 [1.05, 2.50] | 3 | 55 | 0.15 | nudge_target: 0.039 [-0.273, 0.145] | – |
| 51c | platform | 665 | 0.20 [-0.11, 0.34] | 0 | 2 | 0.03 |  | – |
| 51d | edge_on | 5 | 3.10 [1.96, 6.48] | 4 | 7 | 0.46 |  | – |
| 51d | pause | 5 | -8.53 [-9.81, -7.41] | 3 | 16 | -0.79 | pause: – [–, –] | – |
| 51d | human | 5 | 1.67 [0.00, 2.12] | 1 | 3 | 0.55 | human_other: 0.054 [-0.465, 0.204] | 3 |
| 51d | nudge | 105 | 0.95 [0.20, 1.92] | 3 | 15 | 0.17 | nudge_target: -0.070 [-0.467, 0.449] | – |
| 51d | platform | 616 | 0.18 [0.08, 0.33] | 1 | 3 | 0.05 |  | – |
| 51e | edge_on | 3 | 8.35 [0.46, 9.80] | 4 | 24 | 0.66 |  | – |
| 51e | pause | 3 | -6.54 [-7.69, -3.79] | 2 | 13 | -0.51 | pause: – [–, –] | – |
| 51e | human | 12 | -0.02 [-0.11, 0.21] | 0 | 2 | 0.14 | human_other: -0.007 [-0.172, 0.043] | – |
| 51e | nudge | 73 | 3.32 [1.34, 5.07] | 2 | 56 | 0.59 | nudge_target: 0.475 [-0.799, 1.420] | 3 |
| 51e | platform | 354 | 0.09 [-0.07, 0.13] | 1 | 4 | 0.00 |  | – |
| 51f | edge_on | 5 | 6.37 [4.06, 9.62] | 4 | 13 | 0.69 |  | – |
| 51f | pause | 5 | -8.14 [-8.95, -7.26] | 3 | 17 | -0.64 | pause: – [–, –] | – |
| 51f | human | 3 | 0.42 [-2.25, 1.49] | 14 | 7 | 0.18 | human_other: -0.161 [-0.181, -0.047] | – |
| 51f | nudge | 105 | 0.64 [0.31, 1.04] | 2 | 7 | 0.10 | nudge_target: 0.203 [-0.164, 0.532] | – |
| 51f | platform | 716 | 0.14 [0.06, 0.28] | 1 | 2 | 0.02 |  | – |
| 51g | edge_on | 13 | 5.54 [4.16, 7.18] | 1 | 15 | 0.54 |  | – |
| 51g | human | 26 | -0.18 [-0.65, 1.58] | 6 | 2 | 0.03 | human_other: 0.169 [0.005, 0.228] | 1 |
| 51g | nudge | 277 | 0.73 [0.42, 1.14] | 1 | 9 | 0.10 | nudge_target: 0.218 [0.076, 0.319] | 1 |
| 51g | platform | 1761 | 0.14 [0.05, 0.27] | 0 | 3 | 0.02 |  | – |
| 51h | edge_on | 4 | 5.88 [5.13, 7.32] | 2 | 17 | 0.54 |  | – |
| 51h | human | 6 | 0.38 [-0.32, 0.57] | 0 | 5 | 0.16 | human_other: 0.032 [-0.305, 0.117] | – |
| 51h | platform | 536 | 0.27 [0.10, 0.35] | 1 | 6 | 0.04 |  | – |
| 51i | edge_on | 2 | 6.19 [–, –] | 1 | 16 | 0.79 |  | – |
| 51i | human | 1 | -1.85 [–, –] | 7 | 3 | 0.37 | human_other: 0.027 [0.027, 0.027] | 1 |
| 51i | platform | 256 | 0.38 [–, –] | 1 | 9 | 0.02 |  | – |
| 51j | edge_on | 2 | 6.68 [–, –] | 1 | 26 | 0.54 |  | – |
| 51j | human | 5 | 0.34 [–, –] | 1 | 5 | -0.01 | human_other: 0.018 [0.007, 0.025] | 1 |
| 51j | platform | 296 | 0.34 [–, –] | 1 | 10 | 0.05 |  | – |


### Native test
Data: `data/processed/H50-field-vs-coupling-transfer-lag/G51/native.json`. Figure: [`figures/G51_human_relay.pdf`](figures/G51_human_relay.pdf). Pooled over the 12 non-holdout units (day stats concatenated, day bootstrap). Messages: 69 naming agents (63 answered by a target within 30 min; reply latency median 61 s, IQR 19–297 s), 44 plain. Pairs: target 95, bystander 1544, plain 551, reply→bystander 1372.

| prediction | observed J₁ (talk) [95% CI] | verdict |
| --- | --- | --- |
| named target jumps at hop 1 | 0.036 [-0.236, 0.389] (only 119 calls near the read-out boundary) | no (underpowered) |
| bystanders < 0.5 × target | 0.026 [-0.017, 0.061]; ratio 0.72 | no |
| relay: jump at the target's reply ≥ generic peer jump | reply 0.028 [-0.038, 0.120] vs peer 0.014 [0.010, 0.017] | no (point estimate 2×, CI includes 0) |
| plain human messages: jump at hop 1 (field) | 0.188 [0.015, 0.255] | yes |

**Reading.** Plain human messages act as a field read at hop 1: recipients' next call is about 0.19 more likely to be a talk call than the in-flight one. The target/relay design is too thin to read: named targets are rarely mid-loop when the message lands (119 calls near the boundary), and the reply-relay jump is twice the generic peer jump but not significant. Round 2: widen the window (3W), pool regime-I human-rich periods (#4–#6), or use the hop-2..4 kernel for bystanders.

## Scorecard (period-specific axes)
- **C (adequacy):** the read-out jump is tested against shifted-time placebos (no-coupling synthetic worlds: false-positive rate 3/35 seeds); field excess against shifted inputs. Here: J₁ CI > 0 in 9/12 units.
- **D (unfitted signature):** a step at the read-out call (onset hop 1) in 9/12 units; no unit shows the ungated signature (J₁ < 0).
- **G (ground truth):** activity co-movement is carried by the schedule edges (edges-alone field excess above), as H38 found for regime III.
## Round 2 (2026-10-05)
*Predictions templated from the card's "Round 2" section (written 2026-10-05 02:50 UTC, before any round-2 statistic). Role: replication. Period numbers are inverse-variance means over the period's eligible units.*

| statistic | estimate [95% CI] | reading |
| --- | --- | --- |
| R1 content jump J^c_1 (bge, all) | 0.034 [0.027, 0.040] | content couples at the read-out call (12 unit(s)) |
| R1 J^c_1 named / unnamed | 0.082 [0.069, 0.096] / 0.015 [0.008, 0.022] | address split |
| R6 relay RD, C-hop ≥ 2 (all / naming C) | 0.014 [0.005, 0.022] / 0.159 [0.108, 0.210] | post hoc; valid in regime III only |


## Notes
