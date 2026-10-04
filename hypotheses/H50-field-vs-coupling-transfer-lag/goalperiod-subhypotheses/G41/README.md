# H50 × G41: Perform novel research! (2026-05-11 → 2026-05-15)

**Verdict:** mixed
**Role:** replication
**Period:** regime III · units 41 (5 d, N=15) · 18,050 (peer message, recipient) pairs · 7 human messages, 59 nudges (non-holdout).

## Why this period
Replication layer: the common H50 estimator on every eligible non-holdout unit, so the period is one comparable point on the field/coupling phase diagram (Parts A–C of the card).

## Prediction
*Written 2026-10-04 07:00 UTC, before running on this period. Templated from the card (P2, P5, P6).*
- Peer read-out jump J₁ (talk) > 0 at 95% [0.60]; onset at hop 1 (no response at the in-flight call).
- Activity field excess (full window) > 0.10 [0.65], ≥ 0.30 expected from the day edges (H38).
- Talk coupling share f_C (CF) larger than the talk field excess [0.60].
- **Verdict rule (templated, card):** *supported* = (a) peer read-out jump J₁ (talk; placebo-corrected, W = 1.5 × median call interval) > 0 at 95% in the inverse-variance pooled period estimate, (b) activity field excess f_F − f_F,null (full window) > 0.10 in the day-weighted period mean, and (c) no unit with J₁ < 0 at 95% (the ungated rival R2). *failed* = neither (a) nor (b). *mixed* = otherwise.

## Result
Data: `data/processed/H50-field-vs-coupling-transfer-lag/G41/` (one JSON per unit). Figure: [`figures/G41_gate_fir.pdf`](figures/G41_gate_fir.pdf). J₁ = placebo-corrected read-out jump in P(talk call) at the first boundary (call starting just after vs just before a peer message), W = 1.5 × median call interval; CIs from a day bootstrap (1-hour blocks in units with < 3 days). κ = J₁ / right-limit excess. Field excess = f_F − f_F,null (shifted-input null); f_C = counterfactual coupling share of talk co-movement (CF, hop-1 kernel; values > 1 are estimator overshoot at low co-movement, see the synthetic validation).

**Pooled period estimate:** J₁ (IVW) = 0.024 [-0.005, 0.052]; activity field excess (full window, day-weighted) = 0.70; units with J₁ < 0 at 95%: 0. Rule: (a) no, (b) yes, (c) yes → **mixed**.

### Peer gate (call-cycle lags)
| unit | days | N | pairs | median call (s) | read-out delay q50 (s) | **J₁ talk** [95% CI] | onset hop | J₂ (hop 2 − hop 1) | J₁ work | J₁ idle | κ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 41 | 5 | 15 | 18,050 | 13.2 | 23 | 0.024 [0.004, 0.061] | 1 | -0.008 [-0.026, 0.008] | -0.025 [-0.063, -0.004] | 0.001 [-0.000, 0.004] | 1.02 |

### Equal-time co-movement decomposition
| unit | activity S (full) | **field excess, activity full** (edges alone / rest alone) | field excess, activity trim | talk S (span) | field excess, talk | **talk coupling share f_C** [k₁ CI] | lagged-peer share (talk) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 41 | 2.32 | 0.70 (0.83 / 0.08) | – | 0.27 | 0.12 | 0.74 [0.14, 1.43] | 0.16 |

### Input transfer functions (Part A) and input gates (Part B)
| unit | input | n | activity G30 [CI] | dead (min) | decay (min) | talk G30 | gate J₁ talk (exo, per recipient) | onset hop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 41 | edge_on | 5 | 1.80 [-1.77, 5.74] | 12 | 13 | 0.63 |  | – |
| 41 | pause | 5 | -10.55 [-11.68, -7.18] | 2 | 13 | -0.88 |  | – |
| 41 | human | 7 | -0.66 [-2.15, 3.42] | 0 | 4 | 0.08 | human_other: 0.047 [-0.082, 0.374] | 4 |
| 41 | nudge | 59 | 0.05 [-0.77, 1.24] | 1 | 6 | -0.02 | nudge_target: 0.005 [-0.071, 0.131] | 3 |
| 41 | platform | 273 | 0.31 [0.25, 0.71] | 2 | 4 | 0.06 |  | – |

## Scorecard (period-specific axes)
- **C (adequacy):** the read-out jump is tested against shifted-time placebos (no-coupling synthetic worlds: false-positive rate 3/35 seeds); field excess against shifted inputs. Here: J₁ CI > 0 in 1/1 units.
- **D (unfitted signature):** a step at the read-out call (onset hop 1) in 1/1 units; no unit shows the ungated signature (J₁ < 0).
- **G (ground truth):** activity co-movement is carried by the schedule edges (edges-alone field excess above), as H38 found for regime III.
## Notes
