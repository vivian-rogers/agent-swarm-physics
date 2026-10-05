# H50 × G44: Finetune your leader! (2026-05-26 → 2026-05-29)

**Verdict:** supported
**Role:** replication
**Period:** regime III · units 44a (2 d, N=17), 44b (2 d, N=18) · 15,785 (peer message, recipient) pairs · 59 human messages, 28 nudges (non-holdout).

## Why this period
Replication layer: the common H50 estimator on every eligible non-holdout unit, so the period is one comparable point on the field/coupling phase diagram (Parts A–C of the card).

## Prediction
*Written 2026-10-04 07:00 UTC, before running on this period. Templated from the card (P2, P5, P6).*
- Peer read-out jump J₁ (talk) > 0 at 95% [0.60]; onset at hop 1 (no response at the in-flight call).
- Activity field excess (full window) > 0.10 [0.65], ≥ 0.30 expected from the day edges (H38).
- Talk coupling share f_C (CF) larger than the talk field excess [0.60].
- **Verdict rule (templated, card):** *supported* = (a) peer read-out jump J₁ (talk; placebo-corrected, W = 1.5 × median call interval) > 0 at 95% in the inverse-variance pooled period estimate, (b) activity field excess f_F − f_F,null (full window) > 0.10 in the day-weighted period mean, and (c) no unit with J₁ < 0 at 95% (the ungated rival R2). *failed* = neither (a) nor (b). *mixed* = otherwise.

## Result
Data: `data/processed/H50-field-vs-coupling-transfer-lag/G44/` (one JSON per unit). Figure: [`figures/G44_gate_fir.pdf`](figures/G44_gate_fir.pdf). J₁ = placebo-corrected read-out jump in P(talk call) at the first boundary (call starting just after vs just before a peer message), W = 1.5 × median call interval; CIs from a day bootstrap (1-hour blocks in units with < 3 days). κ = J₁ / right-limit excess. Field excess = f_F − f_F,null (shifted-input null); f_C = counterfactual coupling share of talk co-movement (CF, hop-1 kernel; values > 1 are estimator overshoot at low co-movement, see the synthetic validation).

**Pooled period estimate:** J₁ (IVW) = 0.025 [0.008, 0.043]; activity field excess (full window, day-weighted) = 0.44; units with J₁ < 0 at 95%: 0. Rule: (a) yes, (b) yes, (c) yes → **supported**.

### Peer gate (call-cycle lags)
| unit | days | N | pairs | median call (s) | read-out delay q50 (s) | **J₁ talk** [95% CI] | onset hop | J₂ (hop 2 − hop 1) | J₁ work | J₁ idle | κ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 44a | 2 | 17 | 6,977 | 20.1 | 25 | 0.021 [-0.003, 0.050] | 2 | 0.034 [0.013, 0.067] | -0.017 [-0.046, 0.013] | -0.004 [-0.011, 0.002] | 1.83 |
| 44b | 2 | 18 | 8,808 | 16.7 | 19 | 0.029 [0.007, 0.054] | 1 | -0.005 [-0.036, 0.032] | -0.029 [-0.060, 0.000] | 0.001 [-0.010, 0.010] | 1.45 |

### Equal-time co-movement decomposition
| unit | activity S (full) | **field excess, activity full** (edges alone / rest alone) | field excess, activity trim | talk S (span) | field excess, talk | **talk coupling share f_C** [k₁ CI] | lagged-peer share (talk) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 44a | 2.33 | 0.55 (0.79 / 0.06) | – | 0.07 | 1.04 | 1.80 [0.00, 3.31] | 0.21 |
| 44b | 2.72 | 0.33 (0.65 / 0.04) | 1.29 | 0.18 | 0.01 | 1.23 [0.32, 1.78] | 0.14 |

### Input transfer functions (Part A) and input gates (Part B)
| unit | input | n | activity G30 [CI] | dead (min) | decay (min) | talk G30 | gate J₁ talk (exo, per recipient) | onset hop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 44a | edge_on | 2 | 5.54 [–, –] | 7 | 8 | 1.74 |  | – |
| 44a | pause | 2 | -7.57 [–, –] | 2 | 8 | -1.50 |  | – |
| 44a | human | 10 | 0.24 [–, –] | 1 | 1 | 0.02 | human_other: -0.120 [-0.619, 0.262] | 2 |
| 44a | nudge | 13 | 0.37 [–, –] | 18 | 2 | 0.15 |  | – |
| 44a | platform | 135 | 0.33 [–, –] | 2 | 4 | 0.07 |  | – |
| 44b | edge_on | 2 | 6.20 [–, –] | 6 | 19 | 1.68 |  | – |
| 44b | pause | 2 | -10.68 [–, –] | 2 | 16 | -0.29 |  | – |
| 44b | human | 49 | -0.10 [–, –] | 0 | 2 | -0.07 | human_other: -0.048 [-0.233, 0.051] | – |
| 44b | nudge | 15 | 1.16 [–, –] | 3 | 3 | 0.20 |  | – |
| 44b | platform | 147 | 0.38 [–, –] | 1 | 2 | 0.07 |  | – |

## Scorecard (period-specific axes)
- **C (adequacy):** the read-out jump is tested against shifted-time placebos (no-coupling synthetic worlds: false-positive rate 3/35 seeds); field excess against shifted inputs. Here: J₁ CI > 0 in 1/2 units.
- **D (unfitted signature):** a step at the read-out call (onset hop 1) in 1/2 units; no unit shows the ungated signature (J₁ < 0).
- **G (ground truth):** activity co-movement is carried by the schedule edges (edges-alone field excess above), as H38 found for regime III.
## Round 2 (2026-10-05)
*Predictions templated from the card's "Round 2" section (written 2026-10-05 02:50 UTC, before any round-2 statistic). Role: replication. Period numbers are inverse-variance means over the period's eligible units.*

| statistic | estimate [95% CI] | reading |
| --- | --- | --- |
| R1 content jump J^c_1 (bge, all) | 0.013 [-0.082, 0.108] | CI includes 0 (1 unit(s)) |
| R1 J^c_1 named / unnamed | 0.042 [-0.059, 0.142] / 0.000 [-0.118, 0.118] | address split |
| R6 relay RD, C-hop ≥ 2 (all / naming C) | -0.022 [-0.075, 0.031] / 0.051 [-0.039, 0.141] | post hoc; valid in regime III only |


## Notes
