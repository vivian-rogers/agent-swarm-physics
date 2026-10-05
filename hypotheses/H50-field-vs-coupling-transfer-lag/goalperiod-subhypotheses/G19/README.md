# H50 × G19: Create a popular daily puzzle game like Wordle (2025-11-03 → 2025-11-14)

**Verdict:** supported
**Role:** replication
**Period:** regime I · units 19a (9 d, N=7), 19b (1 d, N=8) · 32,594 (peer message, recipient) pairs · 11 human messages, 0 nudges (non-holdout).

## Why this period
Replication layer: the common H50 estimator on every eligible non-holdout unit, so the period is one comparable point on the field/coupling phase diagram (Parts A–C of the card).

## Prediction
*Written 2026-10-04 07:00 UTC, before running on this period. Templated from the card (P2, P5, P6).*
- Peer read-out jump J₁ (talk) > 0 at 95% [0.75]; onset at hop 1 (no response at the in-flight call).
- Activity field excess (full window) > 0.10 [0.35], ≤ 0.20 expected in regime I.
- Talk coupling share f_C (CF) larger than the talk field excess [0.50].
- **Verdict rule (templated, card):** *supported* = (a) peer read-out jump J₁ (talk; placebo-corrected, W = 1.5 × median call interval) > 0 at 95% in the inverse-variance pooled period estimate, (b) activity field excess f_F − f_F,null (full window) > 0.10 in the day-weighted period mean, and (c) no unit with J₁ < 0 at 95% (the ungated rival R2). *failed* = neither (a) nor (b). *mixed* = otherwise.

## Result
Data: `data/processed/H50-field-vs-coupling-transfer-lag/G19/` (one JSON per unit). Figure: [`figures/G19_gate_fir.pdf`](figures/G19_gate_fir.pdf). J₁ = placebo-corrected read-out jump in P(talk call) at the first boundary (call starting just after vs just before a peer message), W = 1.5 × median call interval; CIs from a day bootstrap (1-hour blocks in units with < 3 days). κ = J₁ / right-limit excess. Field excess = f_F − f_F,null (shifted-input null); f_C = counterfactual coupling share of talk co-movement (CF, hop-1 kernel; values > 1 are estimator overshoot at low co-movement, see the synthetic validation).

**Pooled period estimate:** J₁ (IVW) = 0.088 [0.076, 0.100]; activity field excess (full window, day-weighted) = 0.52; units with J₁ < 0 at 95%: 0. Rule: (a) yes, (b) yes, (c) yes → **supported**.

### Peer gate (call-cycle lags)
| unit | days | N | pairs | median call (s) | read-out delay q50 (s) | **J₁ talk** [95% CI] | onset hop | J₂ (hop 2 − hop 1) | J₁ work | J₁ idle | κ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 19a | 9 | 7 | 28,725 | 17.3 | 17 | 0.089 [0.078, 0.102] | 1 | 0.075 [0.054, 0.093] | -0.088 [-0.102, -0.075] | -0.001 [-0.008, 0.006] | 0.84 |
| 19b | 1 | 8 | 3,869 | 18.5 | 23 | 0.059 [0.026, 0.156] | 1 | 0.023 [-0.050, 0.073] | -0.041 [-0.149, -0.003] | -0.019 [-0.027, -0.005] | 0.92 |

### Equal-time co-movement decomposition
| unit | activity S (full) | **field excess, activity full** (edges alone / rest alone) | field excess, activity trim | talk S (span) | field excess, talk | **talk coupling share f_C** [k₁ CI] | lagged-peer share (talk) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 19a | 1.27 | 0.54 (0.55 / 0.06) | 0.03 | 0.47 | 0.08 | 1.37 [1.33, 1.36] | 0.28 |
| 19b | 1.30 | 0.36 (0.30 / 0.08) | 0.57 | 0.77 | 0.16 | 0.89 [0.40, 1.07] | 0.07 |

### Input transfer functions (Part A) and input gates (Part B)
| unit | input | n | activity G30 [CI] | dead (min) | decay (min) | talk G30 | gate J₁ talk (exo, per recipient) | onset hop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 19a | edge_on | 9 | -0.02 [-3.32, 2.77] | 0 | 2 | -0.06 |  | – |
| 19a | pause | 9 | -8.21 [-9.68, -6.30] | 2 | 11 | -3.26 | pause: – [537.637, 538.264] | 1 |
| 19a | human | 9 | 0.69 [-0.36, 1.51] | 17 | 21 | -0.09 | human_other: 0.253 [-0.443, 0.987] | – |
| 19a | platform | 93 | 0.55 [-0.34, 1.40] | 1 | 6 | -0.40 |  | – |

## Scorecard (period-specific axes)
- **C (adequacy):** the read-out jump is tested against shifted-time placebos (no-coupling synthetic worlds: false-positive rate 3/35 seeds); field excess against shifted inputs. Here: J₁ CI > 0 in 2/2 units.
- **D (unfitted signature):** a step at the read-out call (onset hop 1) in 2/2 units; no unit shows the ungated signature (J₁ < 0).
- **G (ground truth):** activity co-movement is carried by the schedule edges (edges-alone field excess above), as H38 found for regime III.
## Round 2 (2026-10-05)
*Predictions templated from the card's "Round 2" section (written 2026-10-05 02:50 UTC, before any round-2 statistic). Role: replication. Period numbers are inverse-variance means over the period's eligible units.*

| statistic | estimate [95% CI] | reading |
| --- | --- | --- |
| R1 content jump J^c_1 (bge, all) | 0.045 [0.027, 0.063] | content couples at the read-out call (2 unit(s)) |
| R1 J^c_1 named / unnamed | 0.021 [-0.028, 0.071] / 0.050 [0.027, 0.074] | address split |
| R6 relay RD, C-hop ≥ 2 (all / naming C) | 0.036 [-0.000, 0.072] / 0.007 [-0.024, 0.038] | post hoc; biased in regime I (not scored) |


## Notes
