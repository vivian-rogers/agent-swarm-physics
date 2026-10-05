# H50 × G16: Choose your own goal! (2025-10-06 → 2025-10-10)

**Verdict:** supported
**Role:** replication
**Period:** regime I · units 16 (5 d, N=7) · 11,522 (peer message, recipient) pairs · 27 human messages, 0 nudges (non-holdout).

## Why this period
Replication layer: the common H50 estimator on every eligible non-holdout unit, so the period is one comparable point on the field/coupling phase diagram (Parts A–C of the card).

## Prediction
*Written 2026-10-04 07:00 UTC, before running on this period. Templated from the card (P2, P5, P6).*
- Peer read-out jump J₁ (talk) > 0 at 95% [0.60]; onset at hop 1 (no response at the in-flight call).
- Activity field excess (full window) > 0.10 [0.35], ≤ 0.20 expected in regime I.
- Talk coupling share f_C (CF) larger than the talk field excess [0.50].
- **Verdict rule (templated, card):** *supported* = (a) peer read-out jump J₁ (talk; placebo-corrected, W = 1.5 × median call interval) > 0 at 95% in the inverse-variance pooled period estimate, (b) activity field excess f_F − f_F,null (full window) > 0.10 in the day-weighted period mean, and (c) no unit with J₁ < 0 at 95% (the ungated rival R2). *failed* = neither (a) nor (b). *mixed* = otherwise.

## Result
Data: `data/processed/H50-field-vs-coupling-transfer-lag/G16/` (one JSON per unit). Figure: [`figures/G16_gate_fir.pdf`](figures/G16_gate_fir.pdf). J₁ = placebo-corrected read-out jump in P(talk call) at the first boundary (call starting just after vs just before a peer message), W = 1.5 × median call interval; CIs from a day bootstrap (1-hour blocks in units with < 3 days). κ = J₁ / right-limit excess. Field excess = f_F − f_F,null (shifted-input null); f_C = counterfactual coupling share of talk co-movement (CF, hop-1 kernel; values > 1 are estimator overshoot at low co-movement, see the synthetic validation).

**Pooled period estimate:** J₁ (IVW) = 0.067 [0.054, 0.079]; activity field excess (full window, day-weighted) = 0.60; units with J₁ < 0 at 95%: 0. Rule: (a) yes, (b) yes, (c) yes → **supported**.

### Peer gate (call-cycle lags)
| unit | days | N | pairs | median call (s) | read-out delay q50 (s) | **J₁ talk** [95% CI] | onset hop | J₂ (hop 2 − hop 1) | J₁ work | J₁ idle | κ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 16 | 5 | 7 | 11,522 | 15.1 | 16 | 0.067 [0.052, 0.078] | 1 | 0.045 [0.027, 0.065] | -0.074 [-0.099, -0.051] | 0.007 [-0.008, 0.023] | 1.12 |

### Equal-time co-movement decomposition
| unit | activity S (full) | **field excess, activity full** (edges alone / rest alone) | field excess, activity trim | talk S (span) | field excess, talk | **talk coupling share f_C** [k₁ CI] | lagged-peer share (talk) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 16 | 1.71 | 0.60 (0.61 / 0.22) | 0.43 | 0.49 | 0.24 | 1.18 [1.02, 1.25] | 0.01 |

### Input transfer functions (Part A) and input gates (Part B)
| unit | input | n | activity G30 [CI] | dead (min) | decay (min) | talk G30 | gate J₁ talk (exo, per recipient) | onset hop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 16 | edge_on | 5 | 3.90 [1.52, 7.80] | 10 | 31 | -1.09 |  | – |
| 16 | pause | 5 | -5.92 [-6.83, -4.41] | 1 | 11 | -3.48 | pause: – [–, –] | – |
| 16 | human | 27 | 0.61 [0.18, 1.67] | 8 | 9 | -0.76 | human_other: 0.161 [0.046, 0.383] | 1 |
| 16 | platform | 74 | 0.59 [0.11, 1.70] | 1 | 10 | -0.02 |  | – |

## Scorecard (period-specific axes)
- **C (adequacy):** the read-out jump is tested against shifted-time placebos (no-coupling synthetic worlds: false-positive rate 3/35 seeds); field excess against shifted inputs. Here: J₁ CI > 0 in 1/1 units.
- **D (unfitted signature):** a step at the read-out call (onset hop 1) in 1/1 units; no unit shows the ungated signature (J₁ < 0).
- **G (ground truth):** activity co-movement is carried by the schedule edges (edges-alone field excess above), as H38 found for regime III.
## Round 2 (2026-10-05)
*Predictions templated from the card's "Round 2" section (written 2026-10-05 02:50 UTC, before any round-2 statistic). Role: replication. Period numbers are inverse-variance means over the period's eligible units.*

| statistic | estimate [95% CI] | reading |
| --- | --- | --- |
| R1 content jump J^c_1 (bge, all) | 0.069 [0.037, 0.102] | content couples at the read-out call (1 unit(s)) |
| R1 J^c_1 named / unnamed | 0.012 [-0.142, 0.167] / 0.074 [0.047, 0.102] | address split |
| R6 relay RD, C-hop ≥ 2 (all / naming C) | 0.021 [-0.044, 0.087] / 0.003 [-0.119, 0.126] | post hoc; biased in regime I (not scored) |


## Notes
