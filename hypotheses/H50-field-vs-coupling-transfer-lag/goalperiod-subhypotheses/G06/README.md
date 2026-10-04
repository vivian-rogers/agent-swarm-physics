# H50 × G06: Create your own merch store. Whichever agent's store makes the most profit wins! (2025-06-26 → 2025-07-15)

**Verdict:** supported
**Role:** replication
**Period:** regime I · units 6a (6 d, N=4), 6b (9 d, N=4) · 6,667 (peer message, recipient) pairs · 443 human messages, 0 nudges (non-holdout).

## Why this period
Replication layer: the common H50 estimator on every eligible non-holdout unit, so the period is one comparable point on the field/coupling phase diagram (Parts A–C of the card).

## Prediction
*Written 2026-10-04 07:00 UTC, before running on this period. Templated from the card (P2, P5, P6).*
- Peer read-out jump J₁ (talk) > 0 at 95% [0.60]; onset at hop 1 (no response at the in-flight call).
- Activity field excess (full window) > 0.10 [0.35], ≤ 0.20 expected in regime I.
- Talk coupling share f_C (CF) larger than the talk field excess [0.50].
- **Verdict rule (templated, card):** *supported* = (a) peer read-out jump J₁ (talk; placebo-corrected, W = 1.5 × median call interval) > 0 at 95% in the inverse-variance pooled period estimate, (b) activity field excess f_F − f_F,null (full window) > 0.10 in the day-weighted period mean, and (c) no unit with J₁ < 0 at 95% (the ungated rival R2). *failed* = neither (a) nor (b). *mixed* = otherwise.

## Result
Data: `data/processed/H50-field-vs-coupling-transfer-lag/G06/` (one JSON per unit). Figure: [`figures/G06_gate_fir.pdf`](figures/G06_gate_fir.pdf). J₁ = placebo-corrected read-out jump in P(talk call) at the first boundary (call starting just after vs just before a peer message), W = 1.5 × median call interval; CIs from a day bootstrap (1-hour blocks in units with < 3 days). κ = J₁ / right-limit excess. Field excess = f_F − f_F,null (shifted-input null); f_C = counterfactual coupling share of talk co-movement (CF, hop-1 kernel; values > 1 are estimator overshoot at low co-movement, see the synthetic validation).

**Pooled period estimate:** J₁ (IVW) = 0.090 [0.048, 0.132]; activity field excess (full window, day-weighted) = 0.55; units with J₁ < 0 at 95%: 0. Rule: (a) yes, (b) yes, (c) yes → **supported**.

### Peer gate (call-cycle lags)
| unit | days | N | pairs | median call (s) | read-out delay q50 (s) | **J₁ talk** [95% CI] | onset hop | J₂ (hop 2 − hop 1) | J₁ work | J₁ idle | κ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 6a | 6 | 4 | 2,954 | 14.1 | 10 | 0.082 [0.024, 0.122] | 1 | 0.050 [-0.008, 0.103] | -0.090 [-0.135, -0.030] | 0.008 [-0.001, 0.023] | 0.82 |
| 6b | 9 | 4 | 3,713 | 13.7 | 11 | 0.113 [0.034, 0.204] | 1 | 0.093 [0.029, 0.164] | -0.110 [-0.210, -0.028] | -0.003 [-0.023, 0.010] | 1.07 |

### Equal-time co-movement decomposition
| unit | activity S (full) | **field excess, activity full** (edges alone / rest alone) | field excess, activity trim | talk S (span) | field excess, talk | **talk coupling share f_C** [k₁ CI] | lagged-peer share (talk) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 6a | 1.79 | 0.54 (0.16 / 0.23) | 0.57 | 0.55 | 0.21 | 0.93 [0.28, 1.29] | 0.23 |
| 6b | 1.34 | 0.56 (0.61 / 0.04) | 1.14 | 0.12 | 0.16 | 3.04 [1.15, 3.44] | -0.00 |

### Input transfer functions (Part A) and input gates (Part B)
| unit | input | n | activity G30 [CI] | dead (min) | decay (min) | talk G30 | gate J₁ talk (exo, per recipient) | onset hop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 6a | edge_on | 7 | 14.40 [5.91, 19.11] | 4 | 39 | 3.28 |  | – |
| 6a | pause | 5 | -14.71 [-17.88, -5.56] | 3 | 38 | -2.38 | pause: – [-0.506, -0.056] | 4 |
| 6a | human | 396 | 0.08 [-0.09, 0.37] | 0 | 3 | 0.04 | human_other: 0.043 [0.002, 0.137] | 1 |
| 6a | platform | 25 | 5.82 [2.31, 8.45] | 3 | – | 1.91 |  | – |
| 6b | edge_on | 9 | 4.28 [1.64, 9.00] | 7 | 36 | 1.49 |  | – |
| 6b | pause | 7 | -8.92 [-9.50, -7.43] | 2 | 11 | -1.11 | pause: – [–, –] | – |
| 6b | human | 47 | 0.46 [0.19, 2.14] | 2 | 4 | 0.04 | human_other: 0.023 [-0.027, 0.317] | 2 |
| 6b | platform | 36 | 1.15 [0.41, 3.24] | 4 | 5 | 0.67 |  | – |

## Scorecard (period-specific axes)
- **C (adequacy):** the read-out jump is tested against shifted-time placebos (no-coupling synthetic worlds: false-positive rate 3/35 seeds); field excess against shifted inputs. Here: J₁ CI > 0 in 2/2 units.
- **D (unfitted signature):** a step at the read-out call (onset hop 1) in 2/2 units; no unit shows the ungated signature (J₁ < 0).
- **G (ground truth):** activity co-movement is carried by the schedule edges (edges-alone field excess above), as H38 found for regime III.
## Notes
