# H50 × G37: Pick your own goal! (2026-03-30 → 2026-04-01)

**Verdict:** supported
**Role:** replication
**Period:** regime III · units 37 (3 d, N=12) · 4,049 (peer message, recipient) pairs · 5 human messages, 20 nudges (non-holdout).

## Why this period
Replication layer: the common H50 estimator on every eligible non-holdout unit, so the period is one comparable point on the field/coupling phase diagram (Parts A–C of the card).

## Prediction
*Written 2026-10-04 07:00 UTC, before running on this period. Templated from the card (P2, P5, P6).*
- Peer read-out jump J₁ (talk) > 0 at 95% [0.40]; onset at hop 1 (no response at the in-flight call).
- Activity field excess (full window) > 0.10 [0.65], ≥ 0.30 expected from the day edges (H38).
- Talk coupling share f_C (CF) larger than the talk field excess [0.60].
- **Verdict rule (templated, card):** *supported* = (a) peer read-out jump J₁ (talk; placebo-corrected, W = 1.5 × median call interval) > 0 at 95% in the inverse-variance pooled period estimate, (b) activity field excess f_F − f_F,null (full window) > 0.10 in the day-weighted period mean, and (c) no unit with J₁ < 0 at 95% (the ungated rival R2). *failed* = neither (a) nor (b). *mixed* = otherwise.

## Result
Data: `data/processed/H50-field-vs-coupling-transfer-lag/G37/` (one JSON per unit). Figure: [`figures/G37_gate_fir.pdf`](figures/G37_gate_fir.pdf). J₁ = placebo-corrected read-out jump in P(talk call) at the first boundary (call starting just after vs just before a peer message), W = 1.5 × median call interval; CIs from a day bootstrap (1-hour blocks in units with < 3 days). κ = J₁ / right-limit excess. Field excess = f_F − f_F,null (shifted-input null); f_C = counterfactual coupling share of talk co-movement (CF, hop-1 kernel; values > 1 are estimator overshoot at low co-movement, see the synthetic validation).

**Pooled period estimate:** J₁ (IVW) = 0.097 [0.087, 0.107]; activity field excess (full window, day-weighted) = 0.66; units with J₁ < 0 at 95%: 0. Rule: (a) yes, (b) yes, (c) yes → **supported**.

### Peer gate (call-cycle lags)
| unit | days | N | pairs | median call (s) | read-out delay q50 (s) | **J₁ talk** [95% CI] | onset hop | J₂ (hop 2 − hop 1) | J₁ work | J₁ idle | κ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 37 | 3 | 12 | 4,049 | 12.4 | 18 | 0.097 [0.087, 0.106] | 1 | -0.032 [-0.043, -0.023] | -0.091 [-0.107, -0.078] | -0.006 [-0.025, 0.007] | 1.20 |

### Equal-time co-movement decomposition
| unit | activity S (full) | **field excess, activity full** (edges alone / rest alone) | field excess, activity trim | talk S (span) | field excess, talk | **talk coupling share f_C** [k₁ CI] | lagged-peer share (talk) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 37 | 3.99 | 0.66 (0.14 / 0.47) | 0.34 | 0.38 | 0.12 | 1.26 [1.20, 1.30] | 0.08 |

### Input transfer functions (Part A) and input gates (Part B)
| unit | input | n | activity G30 [CI] | dead (min) | decay (min) | talk G30 | gate J₁ talk (exo, per recipient) | onset hop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 37 | edge_on | 3 | 5.63 [0.80, 5.78] | 4 | 46 | 0.25 |  | – |
| 37 | pause | 3 | -4.12 [-4.47, -1.10] | 2 | 11 | -0.64 |  | – |
| 37 | human | 5 | 0.30 [-0.31, 2.12] | 3 | 9 | 0.60 | human_other: – [–, –] | – |
| 37 | nudge | 20 | 1.64 [0.17, 3.04] | 2 | 9 | 0.04 | nudge_target: 0.191 [-0.115, 0.766] | – |
| 37 | platform | 105 | 1.34 [-0.08, 2.21] | 2 | – | 0.12 |  | – |

## Scorecard (period-specific axes)
- **C (adequacy):** the read-out jump is tested against shifted-time placebos (no-coupling synthetic worlds: false-positive rate 3/35 seeds); field excess against shifted inputs. Here: J₁ CI > 0 in 1/1 units.
- **D (unfitted signature):** a step at the read-out call (onset hop 1) in 1/1 units; no unit shows the ungated signature (J₁ < 0).
- **G (ground truth):** activity co-movement is carried by the schedule edges (edges-alone field excess above), as H38 found for regime III.
## Notes
