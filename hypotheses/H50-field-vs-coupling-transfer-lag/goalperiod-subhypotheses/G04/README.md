# H50 × G04: Write a story and celebrate it with 100 people in person (2025-05-15 → 2025-06-18)

**Verdict:** mixed
**Role:** replication
**Period:** regime I · units 4a (5 d, N=4), 4b (1 d, N=4), 4c (19 d, N=4), 4d (1 d, N=4) · 20,598 (peer message, recipient) pairs · 2008 human messages, 0 nudges (non-holdout).

## Why this period
Replication layer: the common H50 estimator on every eligible non-holdout unit, so the period is one comparable point on the field/coupling phase diagram (Parts A–C of the card).

## Prediction
*Written 2026-10-04 07:00 UTC, before running on this period. Templated from the card (P2, P5, P6).*
- Peer read-out jump J₁ (talk) > 0 at 95% [0.75]; onset at hop 1 (no response at the in-flight call).
- Activity field excess (full window) > 0.10 [0.35], ≤ 0.20 expected in regime I.
- Talk coupling share f_C (CF) larger than the talk field excess [0.50].
- **Verdict rule (templated, card):** *supported* = (a) peer read-out jump J₁ (talk; placebo-corrected, W = 1.5 × median call interval) > 0 at 95% in the inverse-variance pooled period estimate, (b) activity field excess f_F − f_F,null (full window) > 0.10 in the day-weighted period mean, and (c) no unit with J₁ < 0 at 95% (the ungated rival R2). *failed* = neither (a) nor (b). *mixed* = otherwise.

## Result
Data: `data/processed/H50-field-vs-coupling-transfer-lag/G04/` (one JSON per unit). Figure: [`figures/G04_gate_fir.pdf`](figures/G04_gate_fir.pdf). J₁ = placebo-corrected read-out jump in P(talk call) at the first boundary (call starting just after vs just before a peer message), W = 1.5 × median call interval; CIs from a day bootstrap (1-hour blocks in units with < 3 days). κ = J₁ / right-limit excess. Field excess = f_F − f_F,null (shifted-input null); f_C = counterfactual coupling share of talk co-movement (CF, hop-1 kernel; values > 1 are estimator overshoot at low co-movement, see the synthetic validation).

**Pooled period estimate:** J₁ (IVW) = 0.007 [-0.011, 0.026]; activity field excess (full window, day-weighted) = 0.52; units with J₁ < 0 at 95%: 0. Rule: (a) no, (b) yes, (c) yes → **mixed**.

### Peer gate (call-cycle lags)
| unit | days | N | pairs | median call (s) | read-out delay q50 (s) | **J₁ talk** [95% CI] | onset hop | J₂ (hop 2 − hop 1) | J₁ work | J₁ idle | κ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 4a | 5 | 4 | 4,994 | 12.9 | 11 | -0.031 [-0.059, 0.002] | – | -0.011 [-0.077, 0.021] | 0.034 [-0.005, 0.060] | -0.003 [-0.009, 0.005] | -0.97 |
| 4b | 1 | 4 | 945 | 13.7 | 11 | 0.007 [-0.027, 0.041] | 5 | -0.029 [-0.230, 0.002] | 0.008 [-0.036, 0.044] | -0.015 [-0.020, 0.026] | 13.49 |
| 4c | 19 | 4 | 13,446 | 12.9 | 12 | 0.053 [0.012, 0.085] | 1 | 0.008 [-0.025, 0.038] | -0.048 [-0.083, -0.002] | -0.004 [-0.017, 0.011] | 0.71 |
| 4d | 1 | 4 | 1,213 | 13.4 | 14 | 0.044 [-0.031, 0.112] | 3 | 0.088 [-0.070, 0.181] | -0.054 [-0.114, 0.005] | 0.010 [-0.056, 0.063] | 0.95 |

### Equal-time co-movement decomposition
| unit | activity S (full) | **field excess, activity full** (edges alone / rest alone) | field excess, activity trim | talk S (span) | field excess, talk | **talk coupling share f_C** [k₁ CI] | lagged-peer share (talk) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 4a | 1.04 | 0.46 (0.64 / 0.00) | 0.37 | 0.56 | 0.08 | 0.00 [0.00, 0.03] | 0.05 |
| 4b | 1.52 | 0.17 (0.39 / -0.13) | – | -0.12 | – | – [–, –] | – |
| 4c | 1.13 | 0.52 (0.41 / 0.18) | 0.36 | 0.42 | 0.08 | 0.58 [0.14, 0.86] | 0.06 |
| 4d | 1.44 | 0.98 (0.22 / 0.75) | 1.23 | 0.70 | 0.67 | 0.31 [0.00, 0.80] | 0.04 |

### Input transfer functions (Part A) and input gates (Part B)
| unit | input | n | activity G30 [CI] | dead (min) | decay (min) | talk G30 | gate J₁ talk (exo, per recipient) | onset hop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 4a | edge_on | 5 | 3.58 [1.56, 5.69] | 11 | 9 | 2.03 |  | – |
| 4a | pause | 5 | -3.53 [-4.04, -2.42] | 1 | 10 | -1.85 |  | – |
| 4a | human | 125 | 0.77 [0.68, 1.66] | 1 | 4 | 0.16 | human_other: 0.079 [0.019, 0.187] | 1 |
| 4a | platform | 24 | 0.10 [-2.07, 0.92] | 0 | 3 | -0.14 |  | – |
| 4c | edge_on | 20 | 7.26 [1.05, 11.69] | 7 | 47 | 3.22 |  | – |
| 4c | pause | 20 | -10.49 [-12.16, -5.34] | 3 | 27 | -3.24 | pause: – [-1.244, -0.872] | – |
| 4c | human | 1493 | 0.17 [0.06, 0.28] | 0 | 3 | 0.12 | human_other: 0.055 [0.012, 0.118] | 1 |
| 4c | platform | 57 | 1.32 [-0.43, 3.32] | 1 | – | 0.92 |  | – |

## Scorecard (period-specific axes)
- **C (adequacy):** the read-out jump is tested against shifted-time placebos (no-coupling synthetic worlds: false-positive rate 3/35 seeds); field excess against shifted inputs. Here: J₁ CI > 0 in 1/4 units.
- **D (unfitted signature):** a step at the read-out call (onset hop 1) in 1/4 units; no unit shows the ungated signature (J₁ < 0).
- **G (ground truth):** activity co-movement is carried by the schedule edges (edges-alone field excess above), as H38 found for regime III.
## Round 2 (2026-10-05)
*Predictions templated from the card's "Round 2" section (written 2026-10-05 02:50 UTC, before any round-2 statistic). Role: replication. Period numbers are inverse-variance means over the period's eligible units.*

| statistic | estimate [95% CI] | reading |
| --- | --- | --- |
| R1 content jump J^c_1 (bge, all) | -0.014 [-0.054, 0.026] | CI includes 0 (2 unit(s)) |
| R1 J^c_1 named / unnamed | -0.015 [-0.054, 0.024] / -0.004 [-0.050, 0.042] | address split |
| R6 relay RD, C-hop ≥ 2 (all / naming C) | 0.035 [-0.003, 0.073] / -0.089 [-0.161, -0.017] | post hoc; biased in regime I (not scored) |


## Notes
