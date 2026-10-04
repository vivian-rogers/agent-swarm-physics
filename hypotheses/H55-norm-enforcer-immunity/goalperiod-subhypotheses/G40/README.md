# H55 × G40: Connect your worlds into a 3D universe (NE42 merge) (2026-05-04 → 05-08)

**Verdict:** failed
**Role:** replication
**Period:** regime III · up to 15 agents · 5 non-holdout days · units 40 (matching strata are within unit).

## Why this period
Replication layer: the common H55 estimators on every non-holdout goal period with DQ2 reply labels, giving one comparable point per period (enforcer friction, correction rate, loop persistence, address effect). Per-period immune contrasts need ≥ 15 steps with a directed correction read; no period reaches that, so corrections' effect on escape is estimated only across periods (card, Amendment 1 and Results).

## Prediction
*Templated: the card's P1, P2, P4–P8, written 2026-10-04 06:26 UTC before any H55 outcome statistic.*
- P1: Spearman ρ(correction rate c_j, received field ν_j) > 0 (agent permutation, one-sided p < 0.05), if ≥ 6 agents qualify.
- P2: replies to an agent's corrections are more negative than replies to its other messages (γ < 0, p < 0.05), if ≥ 20 such replies.
- P4/P5/P6: corrections read in a loop or blocked spell raise escape; any directed read raises escape (descriptive per period).
- **Per-period verdict rule:** supported if every scorable primary test (P1, P2) passes; mixed if some do; failed if none does; descriptive if neither is scorable.

## Result
*Run 2026-10-04 (`analysis/explore.py`; data `data/processed/H55-norm-enforcer-immunity/G40/results.json`).*

| Statistic | Observed | Predicted |
| --- | --- | --- |
| P1 ρ(c_j, ν_j) | -0.79 (p 0.981; 7 agents) | > 0 |
| P1b partial ρ (own speaker field removed) | -0.19 (p 0.659) | ≥ half of P1 |
| P2 γ (replies to corrections − other replies, soft stance, FE) | -0.183 [-0.546, 0.111] (p 0.251; 32 replies) | < 0 |
| P2 placebo (long parents) γ | 0.236 (p 0.020) | ≈ 0 |
| P3 share of confident received opposes that are correction/decline subtypes | 0.72 (n 79) | ≥ 0.5 |
| Jev corrections per 100 parented agent messages (S_p) | 9.36 (56 of 598) | – |
| Restatement loops: at-risk steps / with a directed read / with a correction read | 83 / 42 / 0 | – |
| Loop escape rate per step; mean episode length | 0.39; 3.38 | – |
| P6 address effect on loop escape (Δ, matched) | -0.025 [-0.149, 0.168] (n 41) | > 0 |
| v3 blocked spells: at-risk windows / with a directed read / with a correction read | 46 / 11 / 1 | – |
| P6 address effect on blocked escape (Δ) | 0.102 (n 11) | > 0 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 0 | P1/P2 against agent permutation and the within-target design |
| D unfitted predictions | 0 | per-period immune contrast not scorable (too few correction reads) |

## Notes
- Corrections use the validated Jev sensor (precision 0.93, recall ≈ 0.1; card Amendment 1); c_j is a scaled rate.
