# H50 × G39: Build your own interactive world! (2026-04-27 → 2026-05-01)

**Verdict:** supported
**Role:** replication
**Period:** regime III · units 39 (5 d, N=15) · 7,764 (peer message, recipient) pairs · 13 human messages, 7 nudges (non-holdout).

## Why this period
Replication layer: the common H50 estimator on every eligible non-holdout unit, so the period is one comparable point on the field/coupling phase diagram (Parts A–C of the card).

## Prediction
*Written 2026-10-04 07:00 UTC, before running on this period. Templated from the card (P2, P5, P6).*
- Peer read-out jump J₁ (talk) > 0 at 95% [0.60]; onset at hop 1 (no response at the in-flight call).
- Activity field excess (full window) > 0.10 [0.65], ≥ 0.30 expected from the day edges (H38).
- Talk coupling share f_C (CF) larger than the talk field excess [0.60].
- **Verdict rule (templated, card):** *supported* = (a) peer read-out jump J₁ (talk; placebo-corrected, W = 1.5 × median call interval) > 0 at 95% in the inverse-variance pooled period estimate, (b) activity field excess f_F − f_F,null (full window) > 0.10 in the day-weighted period mean, and (c) no unit with J₁ < 0 at 95% (the ungated rival R2). *failed* = neither (a) nor (b). *mixed* = otherwise.

## Result
Data: `data/processed/H50-field-vs-coupling-transfer-lag/G39/` (one JSON per unit). Figure: [`figures/G39_gate_fir.pdf`](figures/G39_gate_fir.pdf). J₁ = placebo-corrected read-out jump in P(talk call) at the first boundary (call starting just after vs just before a peer message), W = 1.5 × median call interval; CIs from a day bootstrap (1-hour blocks in units with < 3 days). κ = J₁ / right-limit excess. Field excess = f_F − f_F,null (shifted-input null); f_C = counterfactual coupling share of talk co-movement (CF, hop-1 kernel; values > 1 are estimator overshoot at low co-movement, see the synthetic validation).

**Pooled period estimate:** J₁ (IVW) = 0.026 [0.003, 0.049]; activity field excess (full window, day-weighted) = 0.73; units with J₁ < 0 at 95%: 0. Rule: (a) yes, (b) yes, (c) yes → **supported**.

### Peer gate (call-cycle lags)
| unit | days | N | pairs | median call (s) | read-out delay q50 (s) | **J₁ talk** [95% CI] | onset hop | J₂ (hop 2 − hop 1) | J₁ work | J₁ idle | κ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 39 | 5 | 15 | 7,764 | 13.5 | 24 | 0.026 [0.003, 0.049] | 1 | -0.004 [-0.022, 0.006] | -0.028 [-0.052, -0.002] | 0.002 [-0.002, 0.007] | 0.90 |

### Equal-time co-movement decomposition
| unit | activity S (full) | **field excess, activity full** (edges alone / rest alone) | field excess, activity trim | talk S (span) | field excess, talk | **talk coupling share f_C** [k₁ CI] | lagged-peer share (talk) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 39 | 2.07 | 0.73 (0.85 / 0.20) | – | 0.18 | 0.23 | 0.88 [0.12, 1.43] | 0.04 |

### Input transfer functions (Part A) and input gates (Part B)
| unit | input | n | activity G30 [CI] | dead (min) | decay (min) | talk G30 | gate J₁ talk (exo, per recipient) | onset hop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 39 | edge_on | 5 | 1.37 [-1.31, 6.85] | 10 | 8 | -0.33 |  | – |
| 39 | pause | 5 | -9.49 [-10.12, -6.40] | 2 | 13 | -0.27 |  | – |
| 39 | human | 13 | 0.18 [-0.50, 1.81] | 1 | 3 | 0.12 | human_other: -0.201 [-1.564, -0.060] | – |
| 39 | nudge | 7 | 0.04 [-2.01, 1.78] | 7 | 4 | 0.03 |  | – |
| 39 | platform | 343 | 0.45 [0.29, 0.94] | 2 | 34 | 0.05 |  | – |

## Scorecard (period-specific axes)
- **C (adequacy):** the read-out jump is tested against shifted-time placebos (no-coupling synthetic worlds: false-positive rate 3/35 seeds); field excess against shifted inputs. Here: J₁ CI > 0 in 1/1 units.
- **D (unfitted signature):** a step at the read-out call (onset hop 1) in 1/1 units; no unit shows the ungated signature (J₁ < 0).
- **G (ground truth):** activity co-movement is carried by the schedule edges (edges-alone field excess above), as H38 found for regime III.
## Notes
