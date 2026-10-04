# H50 × G20: Start a Substack and join the blogosphere (2025-11-17 → 2025-11-28)

**Verdict:** supported
**Role:** replication
**Period:** regime I · units 20a (2 d, N=8), 20b (1 d, N=9), 20c (3 d, N=9), 20d (4 d, N=10) · 37,758 (peer message, recipient) pairs · 15 human messages, 0 nudges (non-holdout).

## Why this period
Replication layer: the common H50 estimator on every eligible non-holdout unit, so the period is one comparable point on the field/coupling phase diagram (Parts A–C of the card).

## Prediction
*Written 2026-10-04 07:00 UTC, before running on this period. Templated from the card (P2, P5, P6).*
- Peer read-out jump J₁ (talk) > 0 at 95% [0.75]; onset at hop 1 (no response at the in-flight call).
- Activity field excess (full window) > 0.10 [0.35], ≤ 0.20 expected in regime I.
- Talk coupling share f_C (CF) larger than the talk field excess [0.50].
- **Verdict rule (templated, card):** *supported* = (a) peer read-out jump J₁ (talk; placebo-corrected, W = 1.5 × median call interval) > 0 at 95% in the inverse-variance pooled period estimate, (b) activity field excess f_F − f_F,null (full window) > 0.10 in the day-weighted period mean, and (c) no unit with J₁ < 0 at 95% (the ungated rival R2). *failed* = neither (a) nor (b). *mixed* = otherwise.

## Result
Data: `data/processed/H50-field-vs-coupling-transfer-lag/G20/` (one JSON per unit). Figure: [`figures/G20_gate_fir.pdf`](figures/G20_gate_fir.pdf). J₁ = placebo-corrected read-out jump in P(talk call) at the first boundary (call starting just after vs just before a peer message), W = 1.5 × median call interval; CIs from a day bootstrap (1-hour blocks in units with < 3 days). κ = J₁ / right-limit excess. Field excess = f_F − f_F,null (shifted-input null); f_C = counterfactual coupling share of talk co-movement (CF, hop-1 kernel; values > 1 are estimator overshoot at low co-movement, see the synthetic validation).

**Pooled period estimate:** J₁ (IVW) = 0.008 [0.002, 0.013]; activity field excess (full window, day-weighted) = 0.48; units with J₁ < 0 at 95%: 0. Rule: (a) yes, (b) yes, (c) yes → **supported**.

### Peer gate (call-cycle lags)
| unit | days | N | pairs | median call (s) | read-out delay q50 (s) | **J₁ talk** [95% CI] | onset hop | J₂ (hop 2 − hop 1) | J₁ work | J₁ idle | κ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20a | 2 | 8 | 5,627 | 18.0 | 17 | 0.036 [0.007, 0.074] | 1 | 0.025 [-0.017, 0.062] | -0.037 [-0.074, -0.010] | 0.001 [-0.001, 0.003] | 0.99 |
| 20b | 1 | 9 | 2,084 | 21.2 | 15 | 0.035 [0.001, 0.085] | 1 | 0.014 [-0.015, 0.052] | -0.041 [-0.104, -0.001] | 0.006 [-0.003, 0.024] | 2.02 |
| 20c | 3 | 9 | 8,009 | 15.6 | 15 | 0.006 [0.000, 0.012] | 1 | 0.004 [-0.011, 0.036] | -0.005 [-0.008, -0.001] | -0.001 [-0.004, 0.001] | -0.07 |
| 20d | 4 | 10 | 22,038 | 17.0 | 22 | 0.026 [-0.003, 0.058] | 2 | 0.026 [0.018, 0.036] | -0.027 [-0.060, 0.004] | 0.001 [-0.011, 0.013] | 0.77 |

### Equal-time co-movement decomposition
| unit | activity S (full) | **field excess, activity full** (edges alone / rest alone) | field excess, activity trim | talk S (span) | field excess, talk | **talk coupling share f_C** [k₁ CI] | lagged-peer share (talk) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 20a | 1.92 | 0.34 (0.58 / -0.07) | 0.00 | 0.39 | 0.12 | 0.78 [0.16, 1.42] | 0.31 |
| 20b | 2.38 | 0.25 (0.69 / -0.01) | – | 0.15 | 0.49 | 1.39 [0.05, 2.21] | 0.31 |
| 20c | 2.41 | 0.54 (0.73 / 0.04) | 0.38 | 0.26 | 0.30 | 0.19 [0.01, 0.37] | 0.09 |
| 20d | 2.01 | 0.57 (0.63 / 0.08) | 0.28 | 0.38 | 0.31 | 0.79 [0.00, 1.50] | 0.18 |

### Input transfer functions (Part A) and input gates (Part B)
| unit | input | n | activity G30 [CI] | dead (min) | decay (min) | talk G30 | gate J₁ talk (exo, per recipient) | onset hop |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 20a | edge_on | 2 | 6.57 [–, –] | 9 | 5 | -2.95 |  | – |
| 20a | pause | 2 | -9.65 [–, –] | 1 | 13 | 1.67 |  | – |
| 20a | human | 6 | 0.33 [–, –] | 0 | 4 | -0.32 | human_other: 0.002 [0.001, 0.002] | 1 |
| 20a | platform | 20 | 1.47 [–, –] | 11 | 2 | -0.04 |  | – |
| 20c | edge_on | 3 | 1.64 [-0.97, 8.21] | 19 | 8 | 0.08 |  | – |
| 20c | pause | 3 | -8.45 [-8.47, -6.00] | 1 | 10 | -1.66 |  | – |
| 20c | human | 3 | -0.78 [-1.08, 2.02] | 0 | 8 | 0.04 | human_other: 0.658 [0.332, 0.757] | 1 |
| 20c | platform | 57 | 0.53 [-0.42, 2.73] | 2 | 6 | 0.20 |  | – |
| 20d | edge_on | 4 | 6.32 [2.68, 8.63] | 7 | 30 | -0.21 |  | – |
| 20d | pause | 4 | -6.98 [-7.52, -5.23] | 1 | 10 | -0.97 | pause: – [–, –] | – |
| 20d | human | 2 | -3.27 [-6.47, 1.53] | 2 | 11 | 0.99 |  | – |
| 20d | platform | 49 | 1.08 [-0.09, 2.81] | 2 | 21 | 0.11 |  | – |

## Scorecard (period-specific axes)
- **C (adequacy):** the read-out jump is tested against shifted-time placebos (no-coupling synthetic worlds: false-positive rate 3/35 seeds); field excess against shifted inputs. Here: J₁ CI > 0 in 3/4 units.
- **D (unfitted signature):** a step at the read-out call (onset hop 1) in 3/4 units; no unit shows the ungated signature (J₁ < 0).
- **G (ground truth):** activity co-movement is carried by the schedule edges (edges-alone field excess above), as H38 found for regime III.
## Notes
