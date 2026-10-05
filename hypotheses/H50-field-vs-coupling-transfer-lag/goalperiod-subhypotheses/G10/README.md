# H50 × G10: Complete as many games as you can in a week! (2025-08-18 → 2025-08-22)

**Verdict:** mixed
**Role:** replication
**Period:** regime I · units 10a (2 d, N=7), 10b (3 d, N=7) · 7,420 (peer message, recipient) pairs · 21 human messages, 0 nudges (non-holdout).

## Why this period
Replication layer: the common H50 estimator on every eligible non-holdout unit, so the period is one comparable point on the field/coupling phase diagram (Parts A–C of the card).

## Prediction
*Written 2026-10-04 07:00 UTC, before running on this period. Templated from the card (P2, P5, P6).*
- Peer read-out jump J₁ (talk) > 0 at 95% [0.60]; onset at hop 1 (no response at the in-flight call).
- Activity field excess (full window) > 0.10 [0.35], ≤ 0.20 expected in regime I.
- Talk coupling share f_C (CF) larger than the talk field excess [0.50].
- **Verdict rule (templated, card):** *supported* = (a) peer read-out jump J₁ (talk; placebo-corrected, W = 1.5 × median call interval) > 0 at 95% in the inverse-variance pooled period estimate, (b) activity field excess f_F − f_F,null (full window) > 0.10 in the day-weighted period mean, and (c) no unit with J₁ < 0 at 95% (the ungated rival R2). *failed* = neither (a) nor (b). *mixed* = otherwise.

## Result
Data: `data/processed/H50-field-vs-coupling-transfer-lag/G10/` (one JSON per unit). Figure: [`figures/G10_gate_fir.pdf`](figures/G10_gate_fir.pdf). J₁ = placebo-corrected read-out jump in P(talk call) at the first boundary (call starting just after vs just before a peer message), W = 1.5 × median call interval; CIs from a day bootstrap (1-hour blocks in units with < 3 days). κ = J₁ / right-limit excess. Field excess = f_F − f_F,null (shifted-input null); f_C = counterfactual coupling share of talk co-movement (CF, hop-1 kernel; values > 1 are estimator overshoot at low co-movement, see the synthetic validation).

**Pooled period estimate:** J₁ (IVW) = 0.010 [-0.014, 0.034]; activity field excess (full window, day-weighted) = 0.46; units with J₁ < 0 at 95%: 0. Rule: (a) no, (b) yes, (c) yes → **mixed**.

### Peer gate (call-cycle lags)
| unit | days | N | pairs | median call (s) | read-out delay q50 (s) | **J₁ talk** [95% CI] | onset hop | J₂ (hop 2 − hop 1) | J₁ work | J₁ idle | κ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 10a | 2 | 7 | 2,852 | 22.7 | 17 | 0.019 [-0.017, 0.109] | 2 | 0.109 [0.017, 0.144] | -0.019 [-0.109, 0.017] | 0.000 [0.000, 0.000] | 0.82 |
| 10b | 3 | 7 | 4,568 | 18.9 | 15 | 0.009 [-0.030, 0.021] | – | 0.031 [-0.006, 0.044] | -0.012 [-0.020, 0.013] | 0.003 [-0.002, 0.017] | 2.07 |

### Equal-time co-movement decomposition
| unit | activity S (full) | **field excess, activity full** (edges alone / rest alone) | field excess, activity trim | talk S (span) | field excess, talk | **talk coupling share f_C** [k₁ CI] | lagged-peer share (talk) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 10a | 2.97 | 0.26 (0.19 / 0.09) | 0.27 | 0.43 | 0.31 | 0.21 [0.00, -3.67] | -0.01 |
| 10b | 1.87 | 0.60 (0.82 / 0.04) | – | 0.13 | 0.51 | 0.47 [0.00, 1.10] | 0.00 |

### Input transfer functions (Part A) and input gates (Part B)
| unit | input | n | activity G30 [CI] | dead (min) | decay (min) | talk G30 | gate J₁ talk (exo, per recipient) | onset hop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 10a | edge_on | 2 | 10.79 [–, –] | 4 | 16 | 4.42 |  | – |
| 10a | pause | 1 | -20.17 [–, –] | 2 | 11 | -4.31 |  | – |
| 10a | human | 12 | -0.68 [–, –] | 1 | 2 | -0.66 | human_other: -0.157 [-0.838, -0.037] | – |
| 10a | platform | 5 | 3.97 [–, –] | 3 | 2 | 0.48 |  | – |
| 10b | edge_on | 3 | -0.64 [-1.61, 4.20] | 0 | 3 | 0.65 |  | – |
| 10b | pause | 3 | -10.14 [-13.33, 2.07] | 2 | 11 | -0.71 |  | – |
| 10b | human | 9 | 1.08 [0.95, 3.02] | 2 | 16 | 0.30 | human_other: -0.153 [-0.238, -0.033] | – |
| 10b | platform | 32 | 0.27 [-0.26, 2.78] | 9 | 2 | 0.19 |  | – |

## Scorecard (period-specific axes)
- **C (adequacy):** the read-out jump is tested against shifted-time placebos (no-coupling synthetic worlds: false-positive rate 3/35 seeds); field excess against shifted inputs. Here: J₁ CI > 0 in 0/2 units.
- **D (unfitted signature):** a step at the read-out call (onset hop 1) in 0/2 units; no unit shows the ungated signature (J₁ < 0).
- **G (ground truth):** activity co-movement is carried by the schedule edges (edges-alone field excess above), as H38 found for regime III.
## Round 2 (2026-10-05)
*Predictions templated from the card's "Round 2" section (written 2026-10-05 02:50 UTC, before any round-2 statistic). Role: replication. Period numbers are inverse-variance means over the period's eligible units.*

| statistic | estimate [95% CI] | reading |
| --- | --- | --- |
| R1 content jump J^c_1 (bge, all) | 0.023 [0.005, 0.042] | content couples at the read-out call (2 unit(s)) |
| R1 J^c_1 named / unnamed | -0.029 [-0.191, 0.132] / 0.019 [0.004, 0.034] | address split |
| R6 relay RD, C-hop ≥ 2 (all / naming C) | 0.026 [-0.006, 0.058] / 0.087 [-0.089, 0.264] | post hoc; biased in regime I (not scored) |


## Notes
