# H50 × G05: Holiday: do whatever you like! Next goal will begin soon (2025-06-19 → 2025-06-25)

**Verdict:** supported
**Role:** replication
**Period:** regime I · units 5 (5 d, N=4) · 3,354 (peer message, recipient) pairs · 881 human messages, 0 nudges (non-holdout).

## Why this period
Replication layer: the common H50 estimator on every eligible non-holdout unit, so the period is one comparable point on the field/coupling phase diagram (Parts A–C of the card).

## Prediction
*Written 2026-10-04 07:00 UTC, before running on this period. Templated from the card (P2, P5, P6).*
- Peer read-out jump J₁ (talk) > 0 at 95% [0.40]; onset at hop 1 (no response at the in-flight call).
- Activity field excess (full window) > 0.10 [0.35], ≤ 0.20 expected in regime I.
- Talk coupling share f_C (CF) larger than the talk field excess [0.50].
- **Verdict rule (templated, card):** *supported* = (a) peer read-out jump J₁ (talk; placebo-corrected, W = 1.5 × median call interval) > 0 at 95% in the inverse-variance pooled period estimate, (b) activity field excess f_F − f_F,null (full window) > 0.10 in the day-weighted period mean, and (c) no unit with J₁ < 0 at 95% (the ungated rival R2). *failed* = neither (a) nor (b). *mixed* = otherwise.

## Result
Data: `data/processed/H50-field-vs-coupling-transfer-lag/G05/` (one JSON per unit). Figure: [`figures/G05_gate_fir.pdf`](figures/G05_gate_fir.pdf). J₁ = placebo-corrected read-out jump in P(talk call) at the first boundary (call starting just after vs just before a peer message), W = 1.5 × median call interval; CIs from a day bootstrap (1-hour blocks in units with < 3 days). κ = J₁ / right-limit excess. Field excess = f_F − f_F,null (shifted-input null); f_C = counterfactual coupling share of talk co-movement (CF, hop-1 kernel; values > 1 are estimator overshoot at low co-movement, see the synthetic validation).

**Pooled period estimate:** J₁ (IVW) = 0.086 [0.070, 0.102]; activity field excess (full window, day-weighted) = 0.52; units with J₁ < 0 at 95%: 0. Rule: (a) yes, (b) yes, (c) yes → **supported**.

### Peer gate (call-cycle lags)
| unit | days | N | pairs | median call (s) | read-out delay q50 (s) | **J₁ talk** [95% CI] | onset hop | J₂ (hop 2 − hop 1) | J₁ work | J₁ idle | κ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 5 | 4 | 3,354 | 14.4 | 12 | 0.086 [0.068, 0.100] | 1 | 0.014 [-0.029, 0.053] | -0.096 [-0.106, -0.086] | 0.010 [0.000, 0.018] | 1.38 |

### Equal-time co-movement decomposition
| unit | activity S (full) | **field excess, activity full** (edges alone / rest alone) | field excess, activity trim | talk S (span) | field excess, talk | **talk coupling share f_C** [k₁ CI] | lagged-peer share (talk) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | 1.35 | 0.52 (0.74 / -0.03) | 0.64 | 0.08 | -0.03 | 3.70 [3.05, 4.15] | 0.03 |

### Input transfer functions (Part A) and input gates (Part B)
| unit | input | n | activity G30 [CI] | dead (min) | decay (min) | talk G30 | gate J₁ talk (exo, per recipient) | onset hop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 5 | edge_on | 5 | 6.81 [6.39, 12.90] | 9 | 29 | 2.23 |  | – |
| 5 | pause | 5 | -7.81 [-8.49, -4.31] | 2 | 10 | -3.86 |  | – |
| 5 | human | 881 | 0.06 [0.04, 0.27] | 2 | 3 | -0.02 | human_other: 0.062 [-0.006, 0.139] | – |
| 5 | platform | 16 | 0.84 [-2.71, 4.31] | 1 | 13 | 0.96 |  | – |

## Scorecard (period-specific axes)
- **C (adequacy):** the read-out jump is tested against shifted-time placebos (no-coupling synthetic worlds: false-positive rate 3/35 seeds); field excess against shifted inputs. Here: J₁ CI > 0 in 1/1 units.
- **D (unfitted signature):** a step at the read-out call (onset hop 1) in 1/1 units; no unit shows the ungated signature (J₁ < 0).
- **G (ground truth):** activity co-movement is carried by the schedule edges (edges-alone field excess above), as H38 found for regime III.
## Round 2 (2026-10-05)
*Predictions templated from the card's "Round 2" section (written 2026-10-05 02:50 UTC, before any round-2 statistic). Role: replication. Period numbers are inverse-variance means over the period's eligible units.*

| statistic | estimate [95% CI] | reading |
| --- | --- | --- |
| R1 content jump J^c_1 (bge, all) | 0.036 [-0.016, 0.089] | CI includes 0 (1 unit(s)) |
| R1 J^c_1 named / unnamed | 0.019 [-0.155, 0.192] / 0.043 [0.005, 0.080] | address split |
| R6 relay RD, C-hop ≥ 2 (all / naming C) | 0.079 [-0.039, 0.197] / 0.039 [-0.210, 0.289] | post hoc; biased in regime I (not scored) |


## Notes
