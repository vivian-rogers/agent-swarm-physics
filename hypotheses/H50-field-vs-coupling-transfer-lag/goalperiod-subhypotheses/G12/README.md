# H50 × G12: Form two teams and debate each other, while one agent judges. Choose your teammates wisely! (2025-09-01 → 2025-09-05)

**Verdict:** supported
**Role:** replication
**Period:** regime I · units 12a (4 d, N=7), 12b (1 d, N=7) · 21,549 (peer message, recipient) pairs · 16 human messages, 0 nudges (non-holdout).

## Why this period
Replication layer: the common H50 estimator on every eligible non-holdout unit, so the period is one comparable point on the field/coupling phase diagram (Parts A–C of the card).

## Prediction
*Written 2026-10-04 07:00 UTC, before running on this period. Templated from the card (P2, P5, P6).*
- Peer read-out jump J₁ (talk) > 0 at 95% [0.75]; onset at hop 1 (no response at the in-flight call).
- Activity field excess (full window) > 0.10 [0.35], ≤ 0.20 expected in regime I.
- Talk coupling share f_C (CF) larger than the talk field excess [0.50].
- **Verdict rule (templated, card):** *supported* = (a) peer read-out jump J₁ (talk; placebo-corrected, W = 1.5 × median call interval) > 0 at 95% in the inverse-variance pooled period estimate, (b) activity field excess f_F − f_F,null (full window) > 0.10 in the day-weighted period mean, and (c) no unit with J₁ < 0 at 95% (the ungated rival R2). *failed* = neither (a) nor (b). *mixed* = otherwise.

## Result
Data: `data/processed/H50-field-vs-coupling-transfer-lag/G12/` (one JSON per unit). Figure: [`figures/G12_gate_fir.pdf`](figures/G12_gate_fir.pdf). J₁ = placebo-corrected read-out jump in P(talk call) at the first boundary (call starting just after vs just before a peer message), W = 1.5 × median call interval; CIs from a day bootstrap (1-hour blocks in units with < 3 days). κ = J₁ / right-limit excess. Field excess = f_F − f_F,null (shifted-input null); f_C = counterfactual coupling share of talk co-movement (CF, hop-1 kernel; values > 1 are estimator overshoot at low co-movement, see the synthetic validation).

**Pooled period estimate:** J₁ (IVW) = 0.054 [0.041, 0.066]; activity field excess (full window, day-weighted) = 0.42; units with J₁ < 0 at 95%: 0. Rule: (a) yes, (b) yes, (c) yes → **supported**.

### Peer gate (call-cycle lags)
| unit | days | N | pairs | median call (s) | read-out delay q50 (s) | **J₁ talk** [95% CI] | onset hop | J₂ (hop 2 − hop 1) | J₁ work | J₁ idle | κ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 12a | 4 | 7 | 17,983 | 14.5 | 19 | 0.061 [0.043, 0.078] | 1 | 0.028 [0.015, 0.041] | -0.057 [-0.075, -0.038] | -0.004 [-0.017, 0.009] | 0.49 |
| 12b | 1 | 7 | 3,566 | 12.7 | 15 | 0.045 [0.030, 0.066] | 1 | 0.009 [-0.030, 0.038] | -0.072 [-0.133, -0.045] | 0.027 [0.010, 0.065] | 1.81 |

### Equal-time co-movement decomposition
| unit | activity S (full) | **field excess, activity full** (edges alone / rest alone) | field excess, activity trim | talk S (span) | field excess, talk | **talk coupling share f_C** [k₁ CI] | lagged-peer share (talk) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 12a | 1.26 | 0.50 (0.46 / 0.22) | 0.13 | 0.43 | 0.11 | 1.42 [1.15, 1.48] | 0.17 |
| 12b | 1.43 | 0.12 (0.32 / -0.08) | -0.15 | 0.25 | 0.34 | 1.51 [1.12, 1.79] | -0.21 |

### Input transfer functions (Part A) and input gates (Part B)
| unit | input | n | activity G30 [CI] | dead (min) | decay (min) | talk G30 | gate J₁ talk (exo, per recipient) | onset hop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 12a | edge_on | 4 | 2.83 [0.70, 3.82] | 7 | 28 | -0.01 |  | – |
| 12a | pause | 4 | -2.77 [-3.14, -1.90] | 1 | 10 | -4.87 | pause: – [–, –] | – |
| 12a | human | 16 | -0.42 [-1.68, 0.50] | 9 | 11 | 0.75 | human_other: 0.157 [0.013, 0.268] | 1 |
| 12a | platform | 36 | 2.76 [1.92, 4.48] | 1 | 24 | -0.78 |  | – |

## Scorecard (period-specific axes)
- **C (adequacy):** the read-out jump is tested against shifted-time placebos (no-coupling synthetic worlds: false-positive rate 3/35 seeds); field excess against shifted inputs. Here: J₁ CI > 0 in 2/2 units.
- **D (unfitted signature):** a step at the read-out call (onset hop 1) in 2/2 units; no unit shows the ungated signature (J₁ < 0).
- **G (ground truth):** activity co-movement is carried by the schedule edges (edges-alone field excess above), as H38 found for regime III.
## Round 2 (2026-10-05)
*Predictions templated from the card's "Round 2" section (written 2026-10-05 02:50 UTC, before any round-2 statistic). Role: replication. Period numbers are inverse-variance means over the period's eligible units.*

| statistic | estimate [95% CI] | reading |
| --- | --- | --- |
| R1 content jump J^c_1 (bge, all) | 0.096 [0.078, 0.113] | content couples at the read-out call (2 unit(s)) |
| R1 J^c_1 named / unnamed | 0.102 [0.058, 0.146] / 0.095 [0.071, 0.118] | address split |
| R6 relay RD, C-hop ≥ 2 (all / naming C) | 0.021 [-0.020, 0.061] / 0.028 [-0.042, 0.098] | post hoc; biased in regime I (not scored) |


## Notes
