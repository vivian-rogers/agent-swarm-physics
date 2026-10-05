# H50 × G11: Pursue whatever you'd like to (2025-08-25 → 2025-08-29)

**Verdict:** supported
**Role:** replication
**Period:** regime I · units 11 (5 d, N=7) · 14,527 (peer message, recipient) pairs · 10 human messages, 0 nudges (non-holdout).

## Why this period
Replication layer: the common H50 estimator on every eligible non-holdout unit, so the period is one comparable point on the field/coupling phase diagram (Parts A–C of the card).

## Prediction
*Written 2026-10-04 07:00 UTC, before running on this period. Templated from the card (P2, P5, P6).*
- Peer read-out jump J₁ (talk) > 0 at 95% [0.60]; onset at hop 1 (no response at the in-flight call).
- Activity field excess (full window) > 0.10 [0.35], ≤ 0.20 expected in regime I.
- Talk coupling share f_C (CF) larger than the talk field excess [0.50].
- **Verdict rule (templated, card):** *supported* = (a) peer read-out jump J₁ (talk; placebo-corrected, W = 1.5 × median call interval) > 0 at 95% in the inverse-variance pooled period estimate, (b) activity field excess f_F − f_F,null (full window) > 0.10 in the day-weighted period mean, and (c) no unit with J₁ < 0 at 95% (the ungated rival R2). *failed* = neither (a) nor (b). *mixed* = otherwise.

## Result
Data: `data/processed/H50-field-vs-coupling-transfer-lag/G11/` (one JSON per unit). Figure: [`figures/G11_gate_fir.pdf`](figures/G11_gate_fir.pdf). J₁ = placebo-corrected read-out jump in P(talk call) at the first boundary (call starting just after vs just before a peer message), W = 1.5 × median call interval; CIs from a day bootstrap (1-hour blocks in units with < 3 days). κ = J₁ / right-limit excess. Field excess = f_F − f_F,null (shifted-input null); f_C = counterfactual coupling share of talk co-movement (CF, hop-1 kernel; values > 1 are estimator overshoot at low co-movement, see the synthetic validation).

**Pooled period estimate:** J₁ (IVW) = 0.054 [0.014, 0.094]; activity field excess (full window, day-weighted) = 0.51; units with J₁ < 0 at 95%: 0. Rule: (a) yes, (b) yes, (c) yes → **supported**.

### Peer gate (call-cycle lags)
| unit | days | N | pairs | median call (s) | read-out delay q50 (s) | **J₁ talk** [95% CI] | onset hop | J₂ (hop 2 − hop 1) | J₁ work | J₁ idle | κ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 11 | 5 | 7 | 14,527 | 13.9 | 16 | 0.054 [0.008, 0.087] | 1 | 0.035 [0.009, 0.058] | -0.056 [-0.088, -0.012] | 0.001 [-0.002, 0.005] | 0.76 |

### Equal-time co-movement decomposition
| unit | activity S (full) | **field excess, activity full** (edges alone / rest alone) | field excess, activity trim | talk S (span) | field excess, talk | **talk coupling share f_C** [k₁ CI] | lagged-peer share (talk) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 11 | 1.35 | 0.51 (0.63 / 0.04) | 0.13 | 0.29 | 0.24 | 1.39 [0.29, 1.28] | 0.20 |

### Input transfer functions (Part A) and input gates (Part B)
| unit | input | n | activity G30 [CI] | dead (min) | decay (min) | talk G30 | gate J₁ talk (exo, per recipient) | onset hop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 11 | edge_on | 5 | 1.53 [1.00, 6.75] | 13 | 6 | -2.23 |  | – |
| 11 | pause | 5 | -7.97 [-9.21, -4.75] | 1 | 12 | -3.85 | pause: – [–, –] | – |
| 11 | human | 10 | 1.29 [-1.16, 4.17] | 10 | 6 | -0.54 | human_other: -0.020 [-0.556, 0.514] | 2 |
| 11 | platform | 55 | -0.22 [-0.79, 0.90] | 18 | 4 | 0.39 |  | – |

## Scorecard (period-specific axes)
- **C (adequacy):** the read-out jump is tested against shifted-time placebos (no-coupling synthetic worlds: false-positive rate 3/35 seeds); field excess against shifted inputs. Here: J₁ CI > 0 in 1/1 units.
- **D (unfitted signature):** a step at the read-out call (onset hop 1) in 1/1 units; no unit shows the ungated signature (J₁ < 0).
- **G (ground truth):** activity co-movement is carried by the schedule edges (edges-alone field excess above), as H38 found for regime III.
## Round 2 (2026-10-05)
*Predictions templated from the card's "Round 2" section (written 2026-10-05 02:50 UTC, before any round-2 statistic). Role: replication. Period numbers are inverse-variance means over the period's eligible units.*

| statistic | estimate [95% CI] | reading |
| --- | --- | --- |
| R1 content jump J^c_1 (bge, all) | 0.084 [0.036, 0.132] | content couples at the read-out call (1 unit(s)) |
| R1 J^c_1 named / unnamed | 0.104 [0.053, 0.156] / 0.080 [0.024, 0.136] | address split |
| R6 relay RD, C-hop ≥ 2 (all / naming C) | 0.015 [-0.070, 0.099] / 0.018 [-0.055, 0.091] | post hoc; biased in regime I (not scored) |


## Notes
