# H50 × G42: Run your own Youtube channel! (2026-05-18 → 2026-05-22)

**Verdict:** supported
**Role:** replication
**Period:** regime III · units 42a (2 d, N=15), 42b (3 d, N=16) · 10,420 (peer message, recipient) pairs · 10 human messages, 25 nudges (non-holdout).

## Why this period
Replication layer: the common H50 estimator on every eligible non-holdout unit, so the period is one comparable point on the field/coupling phase diagram (Parts A–C of the card).

## Prediction
*Written 2026-10-04 07:00 UTC, before running on this period. Templated from the card (P2, P5, P6).*
- Peer read-out jump J₁ (talk) > 0 at 95% [0.60]; onset at hop 1 (no response at the in-flight call).
- Activity field excess (full window) > 0.10 [0.65], ≥ 0.30 expected from the day edges (H38).
- Talk coupling share f_C (CF) larger than the talk field excess [0.60].
- **Verdict rule (templated, card):** *supported* = (a) peer read-out jump J₁ (talk; placebo-corrected, W = 1.5 × median call interval) > 0 at 95% in the inverse-variance pooled period estimate, (b) activity field excess f_F − f_F,null (full window) > 0.10 in the day-weighted period mean, and (c) no unit with J₁ < 0 at 95% (the ungated rival R2). *failed* = neither (a) nor (b). *mixed* = otherwise.

## Result
Data: `data/processed/H50-field-vs-coupling-transfer-lag/G42/` (one JSON per unit). Figure: [`figures/G42_gate_fir.pdf`](figures/G42_gate_fir.pdf). J₁ = placebo-corrected read-out jump in P(talk call) at the first boundary (call starting just after vs just before a peer message), W = 1.5 × median call interval; CIs from a day bootstrap (1-hour blocks in units with < 3 days). κ = J₁ / right-limit excess. Field excess = f_F − f_F,null (shifted-input null); f_C = counterfactual coupling share of talk co-movement (CF, hop-1 kernel; values > 1 are estimator overshoot at low co-movement, see the synthetic validation).

**Pooled period estimate:** J₁ (IVW) = 0.022 [0.018, 0.027]; activity field excess (full window, day-weighted) = 0.54; units with J₁ < 0 at 95%: 0. Rule: (a) yes, (b) yes, (c) yes → **supported**.

### Peer gate (call-cycle lags)
| unit | days | N | pairs | median call (s) | read-out delay q50 (s) | **J₁ talk** [95% CI] | onset hop | J₂ (hop 2 − hop 1) | J₁ work | J₁ idle | κ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 42a | 2 | 15 | 3,630 | 13.3 | 16 | 0.039 [0.021, 0.068] | 1 | -0.028 [-0.045, -0.008] | -0.035 [-0.056, -0.019] | -0.004 [-0.011, 0.001] | 1.01 |
| 42b | 3 | 16 | 6,790 | 13.6 | 18 | 0.022 [0.018, 0.028] | 1 | -0.008 [-0.018, 0.013] | -0.028 [-0.031, -0.026] | 0.007 [0.003, 0.010] | 0.95 |

### Equal-time co-movement decomposition
| unit | activity S (full) | **field excess, activity full** (edges alone / rest alone) | field excess, activity trim | talk S (span) | field excess, talk | **talk coupling share f_C** [k₁ CI] | lagged-peer share (talk) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 42a | 2.63 | 0.46 (0.81 / 0.25) | -0.20 | 0.48 | 0.65 | 0.71 [0.41, 1.08] | 0.06 |
| 42b | 2.58 | 0.59 (0.74 / -0.09) | – | 0.14 | 0.29 | 1.11 [0.94, 1.37] | 0.14 |

### Input transfer functions (Part A) and input gates (Part B)
| unit | input | n | activity G30 [CI] | dead (min) | decay (min) | talk G30 | gate J₁ talk (exo, per recipient) | onset hop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 42a | edge_on | 2 | 0.93 [–, –] | 9 | 17 | 0.21 |  | – |
| 42a | pause | 2 | -12.14 [–, –] | 2 | 10 | -2.77 |  | – |
| 42a | human | 4 | 1.29 [–, –] | 8 | 12 | 0.37 | human_other: – [–, –] | – |
| 42a | nudge | 8 | 0.37 [–, –] | 0 | 1 | 0.01 |  | – |
| 42a | platform | 191 | 0.20 [–, –] | 0 | 2 | 0.01 |  | – |
| 42b | edge_on | 7 | 2.46 [1.43, 3.04] | 6 | 51 | 0.18 |  | – |
| 42b | pause | 3 | -4.00 [-4.12, -1.81] | 2 | 11 | -0.43 |  | – |
| 42b | human | 6 | 0.95 [0.00, 2.76] | 2 | 7 | 0.06 | human_other: 0.041 [-0.633, 0.052] | – |
| 42b | nudge | 17 | -1.50 [-2.69, -1.03] | 13 | 8 | 0.09 |  | – |
| 42b | platform | 219 | 0.41 [0.32, 1.04] | 5 | 6 | -0.00 |  | – |

## Scorecard (period-specific axes)
- **C (adequacy):** the read-out jump is tested against shifted-time placebos (no-coupling synthetic worlds: false-positive rate 3/35 seeds); field excess against shifted inputs. Here: J₁ CI > 0 in 2/2 units.
- **D (unfitted signature):** a step at the read-out call (onset hop 1) in 2/2 units; no unit shows the ungated signature (J₁ < 0).
- **G (ground truth):** activity co-movement is carried by the schedule edges (edges-alone field excess above), as H38 found for regime III.
## Notes
