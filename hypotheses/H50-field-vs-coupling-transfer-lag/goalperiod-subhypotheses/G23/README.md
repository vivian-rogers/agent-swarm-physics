# H50 × G23: Compete against each other in an online chess tournament (2025-12-15 → 2025-12-19)

**Verdict:** mixed
**Role:** replication
**Period:** regime I · units 23 (5 d, N=10) · 15,919 (peer message, recipient) pairs · 23 human messages, 0 nudges (non-holdout).

## Why this period
Replication layer: the common H50 estimator on every eligible non-holdout unit, so the period is one comparable point on the field/coupling phase diagram (Parts A–C of the card).

## Prediction
*Written 2026-10-04 07:00 UTC, before running on this period. Templated from the card (P2, P5, P6).*
- Peer read-out jump J₁ (talk) > 0 at 95% [0.60]; onset at hop 1 (no response at the in-flight call).
- Activity field excess (full window) > 0.10 [0.35], ≤ 0.20 expected in regime I.
- Talk coupling share f_C (CF) larger than the talk field excess [0.50].
- **Verdict rule (templated, card):** *supported* = (a) peer read-out jump J₁ (talk; placebo-corrected, W = 1.5 × median call interval) > 0 at 95% in the inverse-variance pooled period estimate, (b) activity field excess f_F − f_F,null (full window) > 0.10 in the day-weighted period mean, and (c) no unit with J₁ < 0 at 95% (the ungated rival R2). *failed* = neither (a) nor (b). *mixed* = otherwise.

## Result
Data: `data/processed/H50-field-vs-coupling-transfer-lag/G23/` (one JSON per unit). Figure: [`figures/G23_gate_fir.pdf`](figures/G23_gate_fir.pdf). J₁ = placebo-corrected read-out jump in P(talk call) at the first boundary (call starting just after vs just before a peer message), W = 1.5 × median call interval; CIs from a day bootstrap (1-hour blocks in units with < 3 days). κ = J₁ / right-limit excess. Field excess = f_F − f_F,null (shifted-input null); f_C = counterfactual coupling share of talk co-movement (CF, hop-1 kernel; values > 1 are estimator overshoot at low co-movement, see the synthetic validation).

**Pooled period estimate:** J₁ (IVW) = 0.008 [-0.013, 0.029]; activity field excess (full window, day-weighted) = 0.68; units with J₁ < 0 at 95%: 0. Rule: (a) no, (b) yes, (c) yes → **mixed**.

### Peer gate (call-cycle lags)
| unit | days | N | pairs | median call (s) | read-out delay q50 (s) | **J₁ talk** [95% CI] | onset hop | J₂ (hop 2 − hop 1) | J₁ work | J₁ idle | κ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 23 | 5 | 10 | 15,919 | 14.7 | 14 | 0.008 [-0.013, 0.030] | – | 0.005 [-0.030, 0.034] | -0.008 [-0.032, 0.014] | -0.000 [-0.003, 0.002] | 0.78 |

### Equal-time co-movement decomposition
| unit | activity S (full) | **field excess, activity full** (edges alone / rest alone) | field excess, activity trim | talk S (span) | field excess, talk | **talk coupling share f_C** [k₁ CI] | lagged-peer share (talk) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 23 | 2.39 | 0.68 (0.76 / -0.11) | 1.16 | 0.31 | 0.48 | 0.28 [0.00, 0.96] | -0.01 |

### Input transfer functions (Part A) and input gates (Part B)
| unit | input | n | activity G30 [CI] | dead (min) | decay (min) | talk G30 | gate J₁ talk (exo, per recipient) | onset hop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 23 | edge_on | 5 | 1.99 [1.23, 3.40] | 15 | 35 | -0.69 |  | – |
| 23 | pause | 5 | -5.45 [-5.60, -4.67] | 1 | 11 | -0.70 | pause: – [–, –] | – |
| 23 | human | 23 | -0.05 [-0.17, 1.98] | 20 | 5 | 0.06 | human_other: 0.064 [-0.138, 0.085] | 2 |
| 23 | platform | 106 | 0.13 [-0.12, 0.96] | 16 | 8 | 0.02 |  | – |

## Scorecard (period-specific axes)
- **C (adequacy):** the read-out jump is tested against shifted-time placebos (no-coupling synthetic worlds: false-positive rate 3/35 seeds); field excess against shifted inputs. Here: J₁ CI > 0 in 0/1 units.
- **D (unfitted signature):** a step at the read-out call (onset hop 1) in 0/1 units; no unit shows the ungated signature (J₁ < 0).
- **G (ground truth):** activity co-movement is carried by the schedule edges (edges-alone field excess above), as H38 found for regime III.
## Round 2 (2026-10-05)
*Predictions templated from the card's "Round 2" section (written 2026-10-05 02:50 UTC, before any round-2 statistic). Role: replication. Period numbers are inverse-variance means over the period's eligible units.*

| statistic | estimate [95% CI] | reading |
| --- | --- | --- |
| R1 content jump J^c_1 (bge, all) | -0.019 [-0.040, 0.002] | CI includes 0 (1 unit(s)) |
| R1 J^c_1 named / unnamed | -0.123 [-0.215, -0.030] / -0.009 [-0.036, 0.018] | address split |
| R6 relay RD, C-hop ≥ 2 (all / naming C) | 0.003 [-0.024, 0.031] / 0.050 [-0.038, 0.139] | post hoc; biased in regime I (not scored) |


## Notes
