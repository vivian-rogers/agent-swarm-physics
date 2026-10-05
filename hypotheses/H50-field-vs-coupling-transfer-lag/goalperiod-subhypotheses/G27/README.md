# H50 × G27: Hack the OWASP Juice Shop hacking playground. Compete to see which agent can complete the most challenges (2026-01-12 → 2026-01-23)

**Verdict:** supported
**Role:** replication
**Period:** regime I · units 27 (10 d, N=10) · 33,604 (peer message, recipient) pairs · 7 human messages, 0 nudges (non-holdout).

## Why this period
Replication layer: the common H50 estimator on every eligible non-holdout unit, so the period is one comparable point on the field/coupling phase diagram (Parts A–C of the card).

## Prediction
*Written 2026-10-04 07:00 UTC, before running on this period. Templated from the card (P2, P5, P6).*
- Peer read-out jump J₁ (talk) > 0 at 95% [0.75]; onset at hop 1 (no response at the in-flight call).
- Activity field excess (full window) > 0.10 [0.35], ≤ 0.20 expected in regime I.
- Talk coupling share f_C (CF) larger than the talk field excess [0.50].
- **Verdict rule (templated, card):** *supported* = (a) peer read-out jump J₁ (talk; placebo-corrected, W = 1.5 × median call interval) > 0 at 95% in the inverse-variance pooled period estimate, (b) activity field excess f_F − f_F,null (full window) > 0.10 in the day-weighted period mean, and (c) no unit with J₁ < 0 at 95% (the ungated rival R2). *failed* = neither (a) nor (b). *mixed* = otherwise.

## Result
Data: `data/processed/H50-field-vs-coupling-transfer-lag/G27/` (one JSON per unit). Figure: [`figures/G27_gate_fir.pdf`](figures/G27_gate_fir.pdf). J₁ = placebo-corrected read-out jump in P(talk call) at the first boundary (call starting just after vs just before a peer message), W = 1.5 × median call interval; CIs from a day bootstrap (1-hour blocks in units with < 3 days). κ = J₁ / right-limit excess. Field excess = f_F − f_F,null (shifted-input null); f_C = counterfactual coupling share of talk co-movement (CF, hop-1 kernel; values > 1 are estimator overshoot at low co-movement, see the synthetic validation).

**Pooled period estimate:** J₁ (IVW) = 0.026 [0.017, 0.035]; activity field excess (full window, day-weighted) = 0.65; units with J₁ < 0 at 95%: 0. Rule: (a) yes, (b) yes, (c) yes → **supported**.

### Peer gate (call-cycle lags)
| unit | days | N | pairs | median call (s) | read-out delay q50 (s) | **J₁ talk** [95% CI] | onset hop | J₂ (hop 2 − hop 1) | J₁ work | J₁ idle | κ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 27 | 10 | 10 | 33,604 | 12.6 | 21 | 0.026 [0.017, 0.036] | 1 | 0.017 [0.007, 0.030] | -0.027 [-0.039, -0.017] | 0.001 [-0.000, 0.004] | 1.09 |

### Equal-time co-movement decomposition
| unit | activity S (full) | **field excess, activity full** (edges alone / rest alone) | field excess, activity trim | talk S (span) | field excess, talk | **talk coupling share f_C** [k₁ CI] | lagged-peer share (talk) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 27 | 1.62 | 0.65 (0.74 / 0.01) | 0.53 | 0.14 | 0.65 | 1.40 [0.96, 1.83] | 0.03 |

### Input transfer functions (Part A) and input gates (Part B)
| unit | input | n | activity G30 [CI] | dead (min) | decay (min) | talk G30 | gate J₁ talk (exo, per recipient) | onset hop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 27 | edge_on | 10 | 2.21 [0.86, 3.76] | 11 | 31 | 0.40 |  | – |
| 27 | pause | 10 | -9.83 [-11.66, -7.48] | 1 | 12 | -1.56 | pause: – [–, –] | – |
| 27 | human | 7 | -0.60 [-3.24, 0.14] | 0 | 1 | 0.23 | human_other: -0.106 [-0.249, 0.493] | – |
| 27 | platform | 546 | 0.15 [0.08, 0.27] | 0 | 3 | 0.05 |  | – |

## Scorecard (period-specific axes)
- **C (adequacy):** the read-out jump is tested against shifted-time placebos (no-coupling synthetic worlds: false-positive rate 3/35 seeds); field excess against shifted inputs. Here: J₁ CI > 0 in 1/1 units.
- **D (unfitted signature):** a step at the read-out call (onset hop 1) in 1/1 units; no unit shows the ungated signature (J₁ < 0).
- **G (ground truth):** activity co-movement is carried by the schedule edges (edges-alone field excess above), as H38 found for regime III.
## Round 2 (2026-10-05)
*Predictions templated from the card's "Round 2" section (written 2026-10-05 02:50 UTC, before any round-2 statistic). Role: replication. Period numbers are inverse-variance means over the period's eligible units.*

| statistic | estimate [95% CI] | reading |
| --- | --- | --- |
| R1 content jump J^c_1 (bge, all) | 0.029 [-0.000, 0.058] | CI includes 0 (1 unit(s)) |
| R1 J^c_1 named / unnamed | -0.049 [-0.110, 0.011] / 0.041 [0.007, 0.074] | address split |
| R6 relay RD, C-hop ≥ 2 (all / naming C) | -0.008 [-0.033, 0.018] / 0.052 [-0.011, 0.115] | post hoc; biased in regime I (not scored) |
| R2 kernel, logged-start recipients: k1 / k4 | 0.063 [0.002, 0.124] / 0.211 [-0.045, 0.467] | regime-I kernel |
| R2 chat-mode channel k1 (all recipients) | 0.025 [0.011, 0.040] | share of calls in chat mode after a read |


## Notes
