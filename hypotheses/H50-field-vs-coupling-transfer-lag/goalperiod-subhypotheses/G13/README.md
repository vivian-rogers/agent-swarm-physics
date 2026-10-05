# H50 × G13: Design, run and write up a human subjects experiment (2025-09-08 → 2025-09-19)

**Verdict:** supported
**Role:** replication
**Period:** regime I · units 13 (10 d, N=6) · 22,817 (peer message, recipient) pairs · 50 human messages, 0 nudges (non-holdout).

## Why this period
Replication layer: the common H50 estimator on every eligible non-holdout unit, so the period is one comparable point on the field/coupling phase diagram (Parts A–C of the card).

## Prediction
*Written 2026-10-04 07:00 UTC, before running on this period. Templated from the card (P2, P5, P6).*
- Peer read-out jump J₁ (talk) > 0 at 95% [0.75]; onset at hop 1 (no response at the in-flight call).
- Activity field excess (full window) > 0.10 [0.35], ≤ 0.20 expected in regime I.
- Talk coupling share f_C (CF) larger than the talk field excess [0.50].
- **Verdict rule (templated, card):** *supported* = (a) peer read-out jump J₁ (talk; placebo-corrected, W = 1.5 × median call interval) > 0 at 95% in the inverse-variance pooled period estimate, (b) activity field excess f_F − f_F,null (full window) > 0.10 in the day-weighted period mean, and (c) no unit with J₁ < 0 at 95% (the ungated rival R2). *failed* = neither (a) nor (b). *mixed* = otherwise.

## Result
Data: `data/processed/H50-field-vs-coupling-transfer-lag/G13/` (one JSON per unit). Figure: [`figures/G13_gate_fir.pdf`](figures/G13_gate_fir.pdf). J₁ = placebo-corrected read-out jump in P(talk call) at the first boundary (call starting just after vs just before a peer message), W = 1.5 × median call interval; CIs from a day bootstrap (1-hour blocks in units with < 3 days). κ = J₁ / right-limit excess. Field excess = f_F − f_F,null (shifted-input null); f_C = counterfactual coupling share of talk co-movement (CF, hop-1 kernel; values > 1 are estimator overshoot at low co-movement, see the synthetic validation).

**Pooled period estimate:** J₁ (IVW) = 0.044 [0.023, 0.066]; activity field excess (full window, day-weighted) = 0.74; units with J₁ < 0 at 95%: 0. Rule: (a) yes, (b) yes, (c) yes → **supported**.

### Peer gate (call-cycle lags)
| unit | days | N | pairs | median call (s) | read-out delay q50 (s) | **J₁ talk** [95% CI] | onset hop | J₂ (hop 2 − hop 1) | J₁ work | J₁ idle | κ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 13 | 10 | 6 | 22,817 | 13.7 | 15 | 0.044 [0.023, 0.066] | 1 | 0.026 [-0.012, 0.055] | -0.046 [-0.067, -0.025] | 0.002 [-0.002, 0.005] | 1.03 |

### Equal-time co-movement decomposition
| unit | activity S (full) | **field excess, activity full** (edges alone / rest alone) | field excess, activity trim | talk S (span) | field excess, talk | **talk coupling share f_C** [k₁ CI] | lagged-peer share (talk) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 13 | 1.18 | 0.74 (0.77 / 0.21) | 0.68 | 0.14 | 0.14 | 2.42 [1.41, 3.08] | -0.06 |

### Input transfer functions (Part A) and input gates (Part B)
| unit | input | n | activity G30 [CI] | dead (min) | decay (min) | talk G30 | gate J₁ talk (exo, per recipient) | onset hop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 13 | edge_on | 10 | 2.50 [0.84, 4.45] | 11 | 15 | -0.58 |  | – |
| 13 | pause | 10 | -8.34 [-9.54, -6.44] | 2 | 12 | -3.68 | pause: – [–, –] | – |
| 13 | human | 50 | -0.21 [-0.65, 0.25] | 1 | 10 | 0.13 | human_other: 0.283 [-0.123, 0.560] | – |
| 13 | platform | 132 | 0.94 [0.63, 1.33] | 1 | 5 | 0.23 |  | – |

## Scorecard (period-specific axes)
- **C (adequacy):** the read-out jump is tested against shifted-time placebos (no-coupling synthetic worlds: false-positive rate 3/35 seeds); field excess against shifted inputs. Here: J₁ CI > 0 in 1/1 units.
- **D (unfitted signature):** a step at the read-out call (onset hop 1) in 1/1 units; no unit shows the ungated signature (J₁ < 0).
- **G (ground truth):** activity co-movement is carried by the schedule edges (edges-alone field excess above), as H38 found for regime III.
## Round 2 (2026-10-05)
*Predictions templated from the card's "Round 2" section (written 2026-10-05 02:50 UTC, before any round-2 statistic). Role: replication. Period numbers are inverse-variance means over the period's eligible units.*

| statistic | estimate [95% CI] | reading |
| --- | --- | --- |
| R1 content jump J^c_1 (bge, all) | 0.102 [0.073, 0.131] | content couples at the read-out call (1 unit(s)) |
| R1 J^c_1 named / unnamed | 0.079 [0.030, 0.127] / 0.108 [0.074, 0.143] | address split |
| R6 relay RD, C-hop ≥ 2 (all / naming C) | 0.015 [-0.040, 0.070] / 0.035 [-0.078, 0.149] | post hoc; biased in regime I (not scored) |


## Notes
