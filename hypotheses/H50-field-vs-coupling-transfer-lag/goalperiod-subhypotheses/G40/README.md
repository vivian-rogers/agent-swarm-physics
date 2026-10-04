# H50 × G40: Connect your worlds into a 3D universe! (2026-05-04 → 2026-05-08)

**Verdict:** mixed
**Role:** replication
**Period:** regime III · units 40 (5 d, N=15) · 22,375 (peer message, recipient) pairs · 4 human messages, 11 nudges (non-holdout).

## Why this period
Replication layer: the common H50 estimator on every eligible non-holdout unit, so the period is one comparable point on the field/coupling phase diagram (Parts A–C of the card).

## Prediction
*Written 2026-10-04 07:00 UTC, before running on this period. Templated from the card (P2, P5, P6).*
- Peer read-out jump J₁ (talk) > 0 at 95% [0.75]; onset at hop 1 (no response at the in-flight call).
- Activity field excess (full window) > 0.10 [0.65], ≥ 0.30 expected from the day edges (H38).
- Talk coupling share f_C (CF) larger than the talk field excess [0.60].
- **Verdict rule (templated, card):** *supported* = (a) peer read-out jump J₁ (talk; placebo-corrected, W = 1.5 × median call interval) > 0 at 95% in the inverse-variance pooled period estimate, (b) activity field excess f_F − f_F,null (full window) > 0.10 in the day-weighted period mean, and (c) no unit with J₁ < 0 at 95% (the ungated rival R2). *failed* = neither (a) nor (b). *mixed* = otherwise.

## Result
Data: `data/processed/H50-field-vs-coupling-transfer-lag/G40/` (one JSON per unit). Figure: [`figures/G40_gate_fir.pdf`](figures/G40_gate_fir.pdf). J₁ = placebo-corrected read-out jump in P(talk call) at the first boundary (call starting just after vs just before a peer message), W = 1.5 × median call interval; CIs from a day bootstrap (1-hour blocks in units with < 3 days). κ = J₁ / right-limit excess. Field excess = f_F − f_F,null (shifted-input null); f_C = counterfactual coupling share of talk co-movement (CF, hop-1 kernel; values > 1 are estimator overshoot at low co-movement, see the synthetic validation).

**Pooled period estimate:** J₁ (IVW) = 0.010 [-0.001, 0.022]; activity field excess (full window, day-weighted) = 0.68; units with J₁ < 0 at 95%: 0. Rule: (a) no, (b) yes, (c) yes → **mixed**.

### Peer gate (call-cycle lags)
| unit | days | N | pairs | median call (s) | read-out delay q50 (s) | **J₁ talk** [95% CI] | onset hop | J₂ (hop 2 − hop 1) | J₁ work | J₁ idle | κ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 40 | 5 | 15 | 22,375 | 13.1 | 18 | 0.010 [-0.004, 0.019] | 4 | -0.004 [-0.015, 0.010] | -0.012 [-0.020, 0.002] | 0.002 [-0.002, 0.006] | 1.07 |

### Equal-time co-movement decomposition
| unit | activity S (full) | **field excess, activity full** (edges alone / rest alone) | field excess, activity trim | talk S (span) | field excess, talk | **talk coupling share f_C** [k₁ CI] | lagged-peer share (talk) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 40 | 2.70 | 0.68 (0.83 / 0.12) | -0.51 | 0.01 | 4.13 | 6.34 [0.00, 11.03] | -0.41 |

### Input transfer functions (Part A) and input gates (Part B)
| unit | input | n | activity G30 [CI] | dead (min) | decay (min) | talk G30 | gate J₁ talk (exo, per recipient) | onset hop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 40 | edge_on | 5 | -0.01 [-0.39, 3.66] | 0 | 3 | -0.19 |  | – |
| 40 | pause | 5 | -11.44 [-12.42, -10.42] | 2 | 15 | -1.42 |  | – |
| 40 | human | 4 | -0.02 [-0.79, 1.54] | 4 | 4 | 0.38 | human_other: – [–, –] | – |
| 40 | nudge | 11 | 0.20 [-2.24, 1.30] | 0 | 8 | 0.31 |  | – |
| 40 | platform | 259 | 0.20 [0.14, 0.88] | 1 | 3 | 0.04 |  | – |

## Scorecard (period-specific axes)
- **C (adequacy):** the read-out jump is tested against shifted-time placebos (no-coupling synthetic worlds: false-positive rate 3/35 seeds); field excess against shifted inputs. Here: J₁ CI > 0 in 0/1 units.
- **D (unfitted signature):** a step at the read-out call (onset hop 1) in 0/1 units; no unit shows the ungated signature (J₁ < 0).
- **G (ground truth):** activity co-movement is carried by the schedule edges (edges-alone field excess above), as H38 found for regime III.
## Notes
