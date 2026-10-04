# H50 × G21: Forecast the abilities and effects of AI (2025-12-01 → 2025-12-05)

**Verdict:** supported
**Role:** replication
**Period:** regime I · units 21a (3 d, N=8), 21b (2 d, N=9) · 18,078 (peer message, recipient) pairs · 5 human messages, 0 nudges (non-holdout).

## Why this period
Replication layer: the common H50 estimator on every eligible non-holdout unit, so the period is one comparable point on the field/coupling phase diagram (Parts A–C of the card).

## Prediction
*Written 2026-10-04 07:00 UTC, before running on this period. Templated from the card (P2, P5, P6).*
- Peer read-out jump J₁ (talk) > 0 at 95% [0.60]; onset at hop 1 (no response at the in-flight call).
- Activity field excess (full window) > 0.10 [0.35], ≤ 0.20 expected in regime I.
- Talk coupling share f_C (CF) larger than the talk field excess [0.50].
- **Verdict rule (templated, card):** *supported* = (a) peer read-out jump J₁ (talk; placebo-corrected, W = 1.5 × median call interval) > 0 at 95% in the inverse-variance pooled period estimate, (b) activity field excess f_F − f_F,null (full window) > 0.10 in the day-weighted period mean, and (c) no unit with J₁ < 0 at 95% (the ungated rival R2). *failed* = neither (a) nor (b). *mixed* = otherwise.

## Result
Data: `data/processed/H50-field-vs-coupling-transfer-lag/G21/` (one JSON per unit). Figure: [`figures/G21_gate_fir.pdf`](figures/G21_gate_fir.pdf). J₁ = placebo-corrected read-out jump in P(talk call) at the first boundary (call starting just after vs just before a peer message), W = 1.5 × median call interval; CIs from a day bootstrap (1-hour blocks in units with < 3 days). κ = J₁ / right-limit excess. Field excess = f_F − f_F,null (shifted-input null); f_C = counterfactual coupling share of talk co-movement (CF, hop-1 kernel; values > 1 are estimator overshoot at low co-movement, see the synthetic validation).

**Pooled period estimate:** J₁ (IVW) = 0.026 [0.006, 0.046]; activity field excess (full window, day-weighted) = 0.41; units with J₁ < 0 at 95%: 0. Rule: (a) yes, (b) yes, (c) yes → **supported**.

### Peer gate (call-cycle lags)
| unit | days | N | pairs | median call (s) | read-out delay q50 (s) | **J₁ talk** [95% CI] | onset hop | J₂ (hop 2 − hop 1) | J₁ work | J₁ idle | κ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 21a | 3 | 8 | 9,297 | 17.7 | 22 | 0.032 [0.015, 0.068] | 1 | 0.008 [-0.025, 0.034] | -0.036 [-0.062, -0.025] | 0.004 [-0.006, 0.017] | 0.98 |
| 21b | 2 | 9 | 8,781 | 14.6 | 25 | 0.017 [-0.011, 0.050] | 3 | -0.001 [-0.023, 0.020] | -0.021 [-0.056, 0.013] | 0.004 [-0.021, 0.025] | 0.58 |

### Equal-time co-movement decomposition
| unit | activity S (full) | **field excess, activity full** (edges alone / rest alone) | field excess, activity trim | talk S (span) | field excess, talk | **talk coupling share f_C** [k₁ CI] | lagged-peer share (talk) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 21a | 1.87 | 0.44 (0.51 / -0.01) | 0.38 | 0.63 | 0.24 | 0.57 [0.27, 1.08] | 0.31 |
| 21b | 2.09 | 0.36 (0.51 / 0.05) | 0.32 | 0.23 | 0.16 | 0.61 [0.00, 1.61] | -0.14 |

### Input transfer functions (Part A) and input gates (Part B)
| unit | input | n | activity G30 [CI] | dead (min) | decay (min) | talk G30 | gate J₁ talk (exo, per recipient) | onset hop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 21a | edge_on | 3 | 6.98 [-0.22, 8.50] | 8 | – | -2.79 |  | – |
| 21a | pause | 3 | -6.92 [-8.73, -4.04] | 1 | 10 | -1.03 |  | – |
| 21a | human | 2 | -3.97 [-5.05, 0.00] | 3 | 50 | 0.63 |  | – |
| 21a | platform | 14 | 0.63 [0.56, 3.75] | 16 | 5 | -0.17 |  | – |
| 21b | edge_on | 2 | 13.87 [–, –] | 6 | – | -0.05 |  | – |
| 21b | pause | 2 | -3.62 [–, –] | 2 | 12 | -4.55 |  | – |
| 21b | human | 3 | 1.10 [–, –] | 11 | 4 | -1.51 | human_other: 0.049 [0.049, 0.049] | 1 |
| 21b | platform | 13 | 4.35 [–, –] | 2 | 4 | 0.67 |  | – |

## Scorecard (period-specific axes)
- **C (adequacy):** the read-out jump is tested against shifted-time placebos (no-coupling synthetic worlds: false-positive rate 3/35 seeds); field excess against shifted inputs. Here: J₁ CI > 0 in 1/2 units.
- **D (unfitted signature):** a step at the read-out call (onset hop 1) in 1/2 units; no unit shows the ungated signature (J₁ < 0).
- **G (ground truth):** activity co-movement is carried by the schedule edges (edges-alone field excess above), as H38 found for regime III.
## Notes
