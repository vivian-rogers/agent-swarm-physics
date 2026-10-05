# H50 × G18: Reduce global poverty as much as you can (2025-10-20 → 2025-10-31)

**Verdict:** supported
**Role:** replication
**Period:** regime I · units 18a (2 d, N=7), 18b (5 d, N=8), 18c (3 d, N=7) · 46,588 (peer message, recipient) pairs · 22 human messages, 0 nudges (non-holdout).

## Why this period
Replication layer: the common H50 estimator on every eligible non-holdout unit, so the period is one comparable point on the field/coupling phase diagram (Parts A–C of the card).

## Prediction
*Written 2026-10-04 07:00 UTC, before running on this period. Templated from the card (P2, P5, P6).*
- Peer read-out jump J₁ (talk) > 0 at 95% [0.75]; onset at hop 1 (no response at the in-flight call).
- Activity field excess (full window) > 0.10 [0.35], ≤ 0.20 expected in regime I.
- Talk coupling share f_C (CF) larger than the talk field excess [0.50].
- **Verdict rule (templated, card):** *supported* = (a) peer read-out jump J₁ (talk; placebo-corrected, W = 1.5 × median call interval) > 0 at 95% in the inverse-variance pooled period estimate, (b) activity field excess f_F − f_F,null (full window) > 0.10 in the day-weighted period mean, and (c) no unit with J₁ < 0 at 95% (the ungated rival R2). *failed* = neither (a) nor (b). *mixed* = otherwise.

## Result
Data: `data/processed/H50-field-vs-coupling-transfer-lag/G18/` (one JSON per unit). Figure: [`figures/G18_gate_fir.pdf`](figures/G18_gate_fir.pdf). J₁ = placebo-corrected read-out jump in P(talk call) at the first boundary (call starting just after vs just before a peer message), W = 1.5 × median call interval; CIs from a day bootstrap (1-hour blocks in units with < 3 days). κ = J₁ / right-limit excess. Field excess = f_F − f_F,null (shifted-input null); f_C = counterfactual coupling share of talk co-movement (CF, hop-1 kernel; values > 1 are estimator overshoot at low co-movement, see the synthetic validation).

**Pooled period estimate:** J₁ (IVW) = 0.090 [0.079, 0.101]; activity field excess (full window, day-weighted) = 0.49; units with J₁ < 0 at 95%: 0. Rule: (a) yes, (b) yes, (c) yes → **supported**.

### Peer gate (call-cycle lags)
| unit | days | N | pairs | median call (s) | read-out delay q50 (s) | **J₁ talk** [95% CI] | onset hop | J₂ (hop 2 − hop 1) | J₁ work | J₁ idle | κ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 18a | 2 | 7 | 3,561 | 17.2 | 21 | 0.129 [0.072, 0.175] | 1 | 0.065 [0.001, 0.124] | -0.185 [-0.256, -0.101] | 0.056 [-0.008, 0.103] | 0.80 |
| 18b | 5 | 8 | 31,389 | 16.1 | 22 | 0.073 [0.048, 0.106] | 1 | 0.057 [0.039, 0.075] | -0.075 [-0.105, -0.051] | 0.001 [-0.002, 0.006] | 0.84 |
| 18c | 3 | 7 | 11,638 | 16.3 | 15 | 0.091 [0.076, 0.100] | 1 | 0.063 [0.007, 0.086] | -0.081 [-0.084, -0.073] | -0.010 [-0.016, -0.002] | 1.12 |

### Equal-time co-movement decomposition
| unit | activity S (full) | **field excess, activity full** (edges alone / rest alone) | field excess, activity trim | talk S (span) | field excess, talk | **talk coupling share f_C** [k₁ CI] | lagged-peer share (talk) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 18a | 1.45 | 0.55 (0.62 / 0.45) | 0.50 | 0.61 | 0.01 | 1.12 [0.86, 1.05] | 0.06 |
| 18b | 1.10 | 0.49 (0.54 / 0.03) | 0.15 | 0.49 | 0.05 | 1.33 [1.26, 1.07] | 0.36 |
| 18c | 1.39 | 0.46 (0.54 / 0.14) | 0.28 | 0.42 | 0.27 | 1.53 [1.49, 1.52] | 0.03 |

### Input transfer functions (Part A) and input gates (Part B)
| unit | input | n | activity G30 [CI] | dead (min) | decay (min) | talk G30 | gate J₁ talk (exo, per recipient) | onset hop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 18a | edge_on | 2 | 5.79 [–, –] | 8 | 26 | -0.60 |  | – |
| 18a | pause | 2 | -3.27 [–, –] | 2 | 10 | -1.09 |  | – |
| 18a | human | 2 | 5.88 [–, –] | 7 | 26 | -0.64 |  | – |
| 18a | platform | 16 | 1.29 [–, –] | 0 | 2 | -0.05 |  | – |
| 18b | edge_on | 5 | 3.06 [0.09, 4.72] | 11 | 9 | -1.21 |  | – |
| 18b | pause | 5 | -3.19 [-4.03, -2.37] | 1 | 10 | -2.07 | pause: – [–, –] | – |
| 18b | human | 17 | 0.71 [0.01, 3.22] | 5 | 5 | -0.20 | human_other: 0.097 [-0.157, 0.504] | – |
| 18b | platform | 71 | 0.36 [-0.51, 0.81] | 1 | 12 | 0.40 |  | – |
| 18c | edge_on | 3 | 1.33 [-1.97, 5.05] | 12 | 12 | -1.58 |  | – |
| 18c | pause | 3 | -3.04 [-3.39, -1.80] | 1 | 11 | -3.65 |  | – |
| 18c | human | 3 | -2.26 [-5.33, 0.00] | 2 | 20 | 4.19 | human_other: – [-2.223, -1.997] | 2 |
| 18c | platform | 43 | 0.29 [0.17, 1.60] | 1 | 9 | 0.19 |  | – |

## Scorecard (period-specific axes)
- **C (adequacy):** the read-out jump is tested against shifted-time placebos (no-coupling synthetic worlds: false-positive rate 3/35 seeds); field excess against shifted inputs. Here: J₁ CI > 0 in 3/3 units.
- **D (unfitted signature):** a step at the read-out call (onset hop 1) in 3/3 units; no unit shows the ungated signature (J₁ < 0).
- **G (ground truth):** activity co-movement is carried by the schedule edges (edges-alone field excess above), as H38 found for regime III.
## Round 2 (2026-10-05)
*Predictions templated from the card's "Round 2" section (written 2026-10-05 02:50 UTC, before any round-2 statistic). Role: replication. Period numbers are inverse-variance means over the period's eligible units.*

| statistic | estimate [95% CI] | reading |
| --- | --- | --- |
| R1 content jump J^c_1 (bge, all) | 0.030 [-0.007, 0.068] | CI includes 0 (3 unit(s)) |
| R1 J^c_1 named / unnamed | 0.066 [0.010, 0.122] / 0.022 [-0.018, 0.063] | address split |
| R6 relay RD, C-hop ≥ 2 (all / naming C) | 0.054 [0.013, 0.095] / 0.058 [0.026, 0.090] | post hoc; biased in regime I (not scored) |


## Notes
