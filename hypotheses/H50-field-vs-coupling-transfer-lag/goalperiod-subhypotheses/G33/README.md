# H50 × G33: Discuss, debate, and act on your views about the recent Pentagon-AI company news (2026-03-02 → 2026-03-04)

**Verdict:** mixed
**Role:** replication
**Period:** regime II · units 33 (3 d, N=11) · 21,170 (peer message, recipient) pairs · 1 human messages, 22 nudges (non-holdout).

## Why this period
Replication layer: the common H50 estimator on every eligible non-holdout unit, so the period is one comparable point on the field/coupling phase diagram (Parts A–C of the card).

## Prediction
*Written 2026-10-04 07:00 UTC, before running on this period. Templated from the card (P2, P5, P6).*
- Peer read-out jump J₁ (talk) > 0 at 95% [0.75]; onset at hop 1 (no response at the in-flight call).
- Activity field excess (full window) > 0.10 [0.45], ≤ 0.20 expected in regime I.
- Talk coupling share f_C (CF) larger than the talk field excess [0.50].
- **Verdict rule (templated, card):** *supported* = (a) peer read-out jump J₁ (talk; placebo-corrected, W = 1.5 × median call interval) > 0 at 95% in the inverse-variance pooled period estimate, (b) activity field excess f_F − f_F,null (full window) > 0.10 in the day-weighted period mean, and (c) no unit with J₁ < 0 at 95% (the ungated rival R2). *failed* = neither (a) nor (b). *mixed* = otherwise.

## Result
Data: `data/processed/H50-field-vs-coupling-transfer-lag/G33/` (one JSON per unit). Figure: [`figures/G33_gate_fir.pdf`](figures/G33_gate_fir.pdf). J₁ = placebo-corrected read-out jump in P(talk call) at the first boundary (call starting just after vs just before a peer message), W = 1.5 × median call interval; CIs from a day bootstrap (1-hour blocks in units with < 3 days). κ = J₁ / right-limit excess. Field excess = f_F − f_F,null (shifted-input null); f_C = counterfactual coupling share of talk co-movement (CF, hop-1 kernel; values > 1 are estimator overshoot at low co-movement, see the synthetic validation).

**Pooled period estimate:** J₁ (IVW) = -0.002 [-0.023, 0.020]; activity field excess (full window, day-weighted) = 0.43; units with J₁ < 0 at 95%: 0. Rule: (a) no, (b) yes, (c) yes → **mixed**.

### Peer gate (call-cycle lags)
| unit | days | N | pairs | median call (s) | read-out delay q50 (s) | **J₁ talk** [95% CI] | onset hop | J₂ (hop 2 − hop 1) | J₁ work | J₁ idle | κ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 33 | 3 | 11 | 21,170 | 11.5 | 25 | -0.002 [-0.013, 0.030] | 4 | 0.021 [-0.001, 0.054] | 0.001 [-0.032, 0.014] | 0.001 [-0.001, 0.002] | 0.78 |

### Equal-time co-movement decomposition
| unit | activity S (full) | **field excess, activity full** (edges alone / rest alone) | field excess, activity trim | talk S (span) | field excess, talk | **talk coupling share f_C** [k₁ CI] | lagged-peer share (talk) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 33 | 1.68 | 0.43 (0.69 / -0.13) | 0.28 | 0.22 | 0.54 | 0.00 [0.00, 1.08] | 0.08 |

### Input transfer functions (Part A) and input gates (Part B)
| unit | input | n | activity G30 [CI] | dead (min) | decay (min) | talk G30 | gate J₁ talk (exo, per recipient) | onset hop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 33 | edge_on | 3 | -0.52 [-5.12, 5.14] | 0 | 3 | 0.13 |  | – |
| 33 | pause | 3 | -6.68 [-7.81, -2.73] | 1 | 11 | -0.90 | pause: – [–, –] | – |
| 33 | human | 1 | 0.36 [-1.33, 5.14] | 13 | 5 | -0.52 |  | – |
| 33 | nudge | 22 | -1.56 [-5.44, 0.57] | 2 | 5 | -0.01 | nudge_target: -0.292 [-0.907, 1.096] | 3 |
| 33 | platform | 102 | 0.23 [-0.42, 1.51] | 3 | 4 | 0.22 |  | – |

## Scorecard (period-specific axes)
- **C (adequacy):** the read-out jump is tested against shifted-time placebos (no-coupling synthetic worlds: false-positive rate 3/35 seeds); field excess against shifted inputs. Here: J₁ CI > 0 in 0/1 units.
- **D (unfitted signature):** a step at the read-out call (onset hop 1) in 0/1 units; no unit shows the ungated signature (J₁ < 0).
- **G (ground truth):** activity co-movement is carried by the schedule edges (edges-alone field excess above), as H38 found for regime III.
## Notes
