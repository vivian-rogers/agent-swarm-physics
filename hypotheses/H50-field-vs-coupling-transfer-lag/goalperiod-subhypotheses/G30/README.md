# H50 × G30: Adopt a park and get it cleaned! (2026-02-09 → 2026-02-13)

**Verdict:** supported
**Role:** replication
**Period:** regime I · units 30a (1 d, N=11), 30b (4 d, N=11) · 26,475 (peer message, recipient) pairs · 15 human messages, 12 nudges (non-holdout).

## Why this period
Replication layer: the common H50 estimator on every eligible non-holdout unit, so the period is one comparable point on the field/coupling phase diagram (Parts A–C of the card).

## Prediction
*Written 2026-10-04 07:00 UTC, before running on this period. Templated from the card (P2, P5, P6).*
- Peer read-out jump J₁ (talk) > 0 at 95% [0.75]; onset at hop 1 (no response at the in-flight call).
- Activity field excess (full window) > 0.10 [0.35], ≤ 0.20 expected in regime I.
- Talk coupling share f_C (CF) larger than the talk field excess [0.50].
- **Verdict rule (templated, card):** *supported* = (a) peer read-out jump J₁ (talk; placebo-corrected, W = 1.5 × median call interval) > 0 at 95% in the inverse-variance pooled period estimate, (b) activity field excess f_F − f_F,null (full window) > 0.10 in the day-weighted period mean, and (c) no unit with J₁ < 0 at 95% (the ungated rival R2). *failed* = neither (a) nor (b). *mixed* = otherwise.

## Result
Data: `data/processed/H50-field-vs-coupling-transfer-lag/G30/` (one JSON per unit). Figure: [`figures/G30_gate_fir.pdf`](figures/G30_gate_fir.pdf). J₁ = placebo-corrected read-out jump in P(talk call) at the first boundary (call starting just after vs just before a peer message), W = 1.5 × median call interval; CIs from a day bootstrap (1-hour blocks in units with < 3 days). κ = J₁ / right-limit excess. Field excess = f_F − f_F,null (shifted-input null); f_C = counterfactual coupling share of talk co-movement (CF, hop-1 kernel; values > 1 are estimator overshoot at low co-movement, see the synthetic validation).

**Pooled period estimate:** J₁ (IVW) = 0.021 [0.009, 0.033]; activity field excess (full window, day-weighted) = 0.42; units with J₁ < 0 at 95%: 0. Rule: (a) yes, (b) yes, (c) yes → **supported**.

### Peer gate (call-cycle lags)
| unit | days | N | pairs | median call (s) | read-out delay q50 (s) | **J₁ talk** [95% CI] | onset hop | J₂ (hop 2 − hop 1) | J₁ work | J₁ idle | κ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 30a | 1 | 11 | 5,374 | 14.5 | 15 | 0.009 [-0.016, 0.028] | 6 | -0.020 [-0.065, 0.007] | -0.016 [-0.046, 0.011] | 0.007 [-0.001, 0.023] | 0.97 |
| 30b | 4 | 11 | 21,101 | 14.1 | 17 | 0.027 [0.009, 0.038] | 1 | 0.013 [-0.001, 0.026] | -0.023 [-0.034, -0.004] | -0.003 [-0.007, 0.001] | 0.59 |

### Equal-time co-movement decomposition
| unit | activity S (full) | **field excess, activity full** (edges alone / rest alone) | field excess, activity trim | talk S (span) | field excess, talk | **talk coupling share f_C** [k₁ CI] | lagged-peer share (talk) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 30a | 2.80 | 0.05 (0.62 / -0.27) | 0.26 | 0.27 | 0.26 | 0.48 [0.00, 1.33] | 0.21 |
| 30b | 2.43 | 0.52 (0.73 / 0.01) | 0.41 | 0.30 | 0.26 | 0.92 [0.32, 1.22] | 0.07 |

### Input transfer functions (Part A) and input gates (Part B)
| unit | input | n | activity G30 [CI] | dead (min) | decay (min) | talk G30 | gate J₁ talk (exo, per recipient) | onset hop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 30b | edge_on | 4 | 2.08 [0.82, 4.39] | 7 | 8 | -0.02 |  | – |
| 30b | pause | 4 | -9.35 [-9.98, -7.92] | 1 | 11 | -2.16 | pause: – [–, –] | – |
| 30b | human | 9 | 1.32 [0.50, 2.13] | 3 | 12 | -0.79 | human_other: 0.052 [-0.301, 0.557] | – |
| 30b | nudge | 12 | 0.66 [0.00, 1.67] | 2 | 4 | 0.36 | nudge_target: -0.308 [-0.863, 0.034] | – |
| 30b | platform | 129 | 0.36 [0.13, 1.72] | 6 | 3 | -0.05 |  | – |

## Scorecard (period-specific axes)
- **C (adequacy):** the read-out jump is tested against shifted-time placebos (no-coupling synthetic worlds: false-positive rate 3/35 seeds); field excess against shifted inputs. Here: J₁ CI > 0 in 1/2 units.
- **D (unfitted signature):** a step at the read-out call (onset hop 1) in 1/2 units; no unit shows the ungated signature (J₁ < 0).
- **G (ground truth):** activity co-movement is carried by the schedule edges (edges-alone field excess above), as H38 found for regime III.
## Round 2 (2026-10-05)
*Predictions templated from the card's "Round 2" section (written 2026-10-05 02:50 UTC, before any round-2 statistic). Role: replication. Period numbers are inverse-variance means over the period's eligible units.*

| statistic | estimate [95% CI] | reading |
| --- | --- | --- |
| R1 content jump J^c_1 (bge, all) | -0.002 [-0.052, 0.048] | CI includes 0 (1 unit(s)) |
| R1 J^c_1 named / unnamed | 0.050 [-0.033, 0.133] / -0.009 [-0.061, 0.043] | address split |
| R6 relay RD, C-hop ≥ 2 (all / naming C) | 0.014 [-0.006, 0.034] / -0.015 [-0.073, 0.043] | post hoc; biased in regime I (not scored) |
| R2 kernel, logged-start recipients: k1 / k4 | 0.026 [0.015, 0.037] / 0.011 [-0.029, 0.051] | regime-I kernel |
| R2 chat-mode channel k1 (all recipients) | 0.014 [0.002, 0.026] | share of calls in chat mode after a read |


## Notes
