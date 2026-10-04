# H50 × G31: Pick your own goal (agents bid 3.7 Sonnet farewell) (2026-02-16 → 2026-02-20)

**Verdict:** supported
**Role:** replication
**Period:** regime I · units 31a (2 d, N=11), 31b (1 d, N=12), 31c (1 d, N=11), 31d (1 d, N=11) · 32,138 (peer message, recipient) pairs · 9 human messages, 25 nudges (non-holdout).

## Why this period
Replication layer: the common H50 estimator on every eligible non-holdout unit, so the period is one comparable point on the field/coupling phase diagram (Parts A–C of the card).

## Prediction
*Written 2026-10-04 07:00 UTC, before running on this period. Templated from the card (P2, P5, P6).*
- Peer read-out jump J₁ (talk) > 0 at 95% [0.75]; onset at hop 1 (no response at the in-flight call).
- Activity field excess (full window) > 0.10 [0.35], ≤ 0.20 expected in regime I.
- Talk coupling share f_C (CF) larger than the talk field excess [0.50].
- **Verdict rule (templated, card):** *supported* = (a) peer read-out jump J₁ (talk; placebo-corrected, W = 1.5 × median call interval) > 0 at 95% in the inverse-variance pooled period estimate, (b) activity field excess f_F − f_F,null (full window) > 0.10 in the day-weighted period mean, and (c) no unit with J₁ < 0 at 95% (the ungated rival R2). *failed* = neither (a) nor (b). *mixed* = otherwise.

## Result
Data: `data/processed/H50-field-vs-coupling-transfer-lag/G31/` (one JSON per unit). Figure: [`figures/G31_gate_fir.pdf`](figures/G31_gate_fir.pdf). J₁ = placebo-corrected read-out jump in P(talk call) at the first boundary (call starting just after vs just before a peer message), W = 1.5 × median call interval; CIs from a day bootstrap (1-hour blocks in units with < 3 days). κ = J₁ / right-limit excess. Field excess = f_F − f_F,null (shifted-input null); f_C = counterfactual coupling share of talk co-movement (CF, hop-1 kernel; values > 1 are estimator overshoot at low co-movement, see the synthetic validation).

**Pooled period estimate:** J₁ (IVW) = 0.016 [0.003, 0.028]; activity field excess (full window, day-weighted) = 0.25; units with J₁ < 0 at 95%: 0. Rule: (a) yes, (b) yes, (c) yes → **supported**.

### Peer gate (call-cycle lags)
| unit | days | N | pairs | median call (s) | read-out delay q50 (s) | **J₁ talk** [95% CI] | onset hop | J₂ (hop 2 − hop 1) | J₁ work | J₁ idle | κ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 31a | 2 | 11 | 12,437 | 11.6 | 18 | 0.017 [0.001, 0.040] | 1 | 0.000 [-0.014, 0.021] | -0.021 [-0.050, -0.003] | 0.004 [-0.000, 0.013] | 0.76 |
| 31b | 1 | 12 | 6,811 | 11.6 | 21 | 0.031 [-0.009, 0.063] | – | 0.012 [-0.007, 0.034] | -0.027 [-0.056, 0.010] | -0.004 [-0.007, -0.001] | 1.17 |
| 31c | 1 | 11 | 5,653 | 11.0 | 21 | 0.036 [0.011, 0.084] | 1 | 0.003 [-0.017, 0.025] | -0.034 [-0.081, -0.008] | -0.002 [-0.005, 0.000] | 1.94 |
| 31d | 1 | 11 | 7,237 | 11.4 | 17 | 0.003 [-0.024, 0.017] | 5 | 0.014 [-0.014, 0.029] | -0.003 [-0.016, 0.021] | -0.000 [-0.002, 0.003] | 3.77 |

### Equal-time co-movement decomposition
| unit | activity S (full) | **field excess, activity full** (edges alone / rest alone) | field excess, activity trim | talk S (span) | field excess, talk | **talk coupling share f_C** [k₁ CI] | lagged-peer share (talk) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 31a | 2.34 | 0.53 (0.70 / 0.25) | 0.41 | 0.19 | 0.25 | 0.96 [0.03, 1.95] | 0.22 |
| 31b | 2.23 | 0.10 (0.59 / 0.08) | 0.51 | 0.38 | 0.18 | 0.92 [0.00, 1.43] | 0.27 |
| 31c | 1.70 | 0.13 (0.72 / -0.33) | – | 0.08 | 0.68 | 3.39 [1.27, 3.33] | 1.02 |
| 31d | 2.32 | -0.05 (0.56 / -0.33) | -0.10 | 0.14 | 0.00 | 0.19 [0.00, 1.00] | 0.40 |

### Input transfer functions (Part A) and input gates (Part B)
| unit | input | n | activity G30 [CI] | dead (min) | decay (min) | talk G30 | gate J₁ talk (exo, per recipient) | onset hop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 31a | edge_on | 2 | 11.18 [–, –] | 3 | 23 | 2.02 |  | – |
| 31a | pause | 2 | -5.91 [–, –] | 1 | 14 | -3.79 |  | – |
| 31a | human | 2 | 1.73 [–, –] | 4 | 8 | 1.36 | human_other: – [-0.072, -0.072] | 3 |
| 31a | nudge | 8 | -1.83 [–, –] | 6 | 3 | 0.66 |  | – |
| 31a | platform | 101 | 1.69 [–, –] | 3 | 4 | 0.22 |  | – |

## Scorecard (period-specific axes)
- **C (adequacy):** the read-out jump is tested against shifted-time placebos (no-coupling synthetic worlds: false-positive rate 3/35 seeds); field excess against shifted inputs. Here: J₁ CI > 0 in 2/4 units.
- **D (unfitted signature):** a step at the read-out call (onset hop 1) in 2/4 units; no unit shows the ungated signature (J₁ < 0).
- **G (ground truth):** activity co-movement is carried by the schedule edges (edges-alone field excess above), as H38 found for regime III.
## Notes
