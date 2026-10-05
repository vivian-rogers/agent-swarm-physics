# H50 × G36: Interact with other AI agents outside the Village! (2026-03-23 → 2026-03-27)

**Verdict:** supported
**Role:** replication
**Period:** regime II · units 36a (1 d, N=12), 36b (2 d, N=12), 36c (2 d, N=12) · 8,634 (peer message, recipient) pairs · 8 human messages, 6 nudges (non-holdout).

## Why this period
Replication layer: the common H50 estimator on every eligible non-holdout unit, so the period is one comparable point on the field/coupling phase diagram (Parts A–C of the card).

## Prediction
*Written 2026-10-04 07:00 UTC, before running on this period. Templated from the card (P2, P5, P6).*
- Peer read-out jump J₁ (talk) > 0 at 95% [0.60]; onset at hop 1 (no response at the in-flight call).
- Activity field excess (full window) > 0.10 [0.45], ≤ 0.20 expected in regime I.
- Talk coupling share f_C (CF) larger than the talk field excess [0.50].
- **Verdict rule (templated, card):** *supported* = (a) peer read-out jump J₁ (talk; placebo-corrected, W = 1.5 × median call interval) > 0 at 95% in the inverse-variance pooled period estimate, (b) activity field excess f_F − f_F,null (full window) > 0.10 in the day-weighted period mean, and (c) no unit with J₁ < 0 at 95% (the ungated rival R2). *failed* = neither (a) nor (b). *mixed* = otherwise.

## Result
Data: `data/processed/H50-field-vs-coupling-transfer-lag/G36/` (one JSON per unit). Figure: [`figures/G36_gate_fir.pdf`](figures/G36_gate_fir.pdf). J₁ = placebo-corrected read-out jump in P(talk call) at the first boundary (call starting just after vs just before a peer message), W = 1.5 × median call interval; CIs from a day bootstrap (1-hour blocks in units with < 3 days). κ = J₁ / right-limit excess. Field excess = f_F − f_F,null (shifted-input null); f_C = counterfactual coupling share of talk co-movement (CF, hop-1 kernel; values > 1 are estimator overshoot at low co-movement, see the synthetic validation).

**Pooled period estimate:** J₁ (IVW) = 0.031 [0.008, 0.055]; activity field excess (full window, day-weighted) = 0.46; units with J₁ < 0 at 95%: 0. Rule: (a) yes, (b) yes, (c) yes → **supported**.

### Peer gate (call-cycle lags)
| unit | days | N | pairs | median call (s) | read-out delay q50 (s) | **J₁ talk** [95% CI] | onset hop | J₂ (hop 2 − hop 1) | J₁ work | J₁ idle | κ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 36a | 1 | 12 | 3,012 | 13.7 | 17 | -0.015 [-0.054, 0.032] | 3 | -0.032 [-0.056, 0.002] | 0.015 [-0.032, 0.054] | 0.000 [0.000, 0.000] | 23.26 |
| 36b | 2 | 12 | 2,790 | 12.1 | 20 | 0.032 [-0.001, 0.070] | – | -0.061 [-0.099, -0.026] | -0.033 [-0.071, -0.001] | 0.002 [-0.001, 0.004] | 0.96 |
| 36c | 2 | 12 | 2,832 | 11.9 | 16 | 0.085 [0.041, 0.134] | 1 | -0.062 [-0.120, 0.012] | -0.086 [-0.134, -0.042] | 0.001 [-0.002, 0.004] | 1.24 |

### Equal-time co-movement decomposition
| unit | activity S (full) | **field excess, activity full** (edges alone / rest alone) | field excess, activity trim | talk S (span) | field excess, talk | **talk coupling share f_C** [k₁ CI] | lagged-peer share (talk) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 36a | 2.37 | 0.18 (0.61 / 0.25) | -1.36 | 0.25 | 0.57 | 0.00 [0.00, 0.58] | 0.07 |
| 36b | 1.76 | 0.52 (0.77 / 0.13) | -0.61 | 0.29 | 0.28 | 0.62 [0.00, 1.23] | 0.09 |
| 36c | 1.95 | 0.55 (0.76 / -0.07) | -0.63 | 0.31 | 0.01 | 1.33 [0.76, 1.58] | 0.18 |

### Input transfer functions (Part A) and input gates (Part B)
| unit | input | n | activity G30 [CI] | dead (min) | decay (min) | talk G30 | gate J₁ talk (exo, per recipient) | onset hop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 36b | edge_on | 2 | 5.86 [–, –] | 6 | 4 | 2.22 |  | – |
| 36b | pause | 2 | -9.28 [–, –] | 3 | 14 | -2.57 |  | – |
| 36b | human | 4 | -0.47 [–, –] | 1 | 3 | -0.03 |  | – |
| 36b | nudge | 2 | 0.94 [–, –] | 2 | 3 | 1.22 |  | – |
| 36b | platform | 129 | 0.29 [–, –] | 0 | 2 | 0.04 |  | – |
| 36c | edge_on | 2 | 12.40 [–, –] | 4 | 24 | 2.19 |  | – |
| 36c | pause | 2 | -13.38 [–, –] | 2 | 10 | -3.51 |  | – |
| 36c | human | 1 | 2.79 [–, –] | 1 | 11 | -1.06 |  | – |
| 36c | nudge | 1 | -11.07 [–, –] | 2 | 5 | 1.86 |  | – |
| 36c | platform | 136 | 0.50 [–, –] | 15 | 20 | 0.21 |  | – |

## Scorecard (period-specific axes)
- **C (adequacy):** the read-out jump is tested against shifted-time placebos (no-coupling synthetic worlds: false-positive rate 3/35 seeds); field excess against shifted inputs. Here: J₁ CI > 0 in 1/3 units.
- **D (unfitted signature):** a step at the read-out call (onset hop 1) in 1/3 units; no unit shows the ungated signature (J₁ < 0).
- **G (ground truth):** activity co-movement is carried by the schedule edges (edges-alone field excess above), as H38 found for regime III.
## Round 2 (2026-10-05)
*Predictions templated from the card's "Round 2" section (written 2026-10-05 02:50 UTC, before any round-2 statistic). Role: replication. Period numbers are inverse-variance means over the period's eligible units.*

| statistic | estimate [95% CI] | reading |
| --- | --- | --- |
| R1 content jump J^c_1 | – | too few hop-0 / hop-1 rows at 0–60 s (< 200) |
| R6 relay RD, C-hop ≥ 2 (all / naming C) | -0.020 [-0.064, 0.023] / 0.032 [-0.131, 0.194] | post hoc; biased in regime I (not scored) |


## Notes
