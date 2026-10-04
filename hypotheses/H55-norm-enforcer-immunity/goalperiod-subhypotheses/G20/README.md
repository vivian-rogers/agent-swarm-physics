# H55 × G20: Substack blogs (2025-11-17 → 11-28)

**Verdict:** failed
**Role:** replication
**Period:** regime I · up to 10 agents · 10 non-holdout days · units 20a, 20b, 20c, 20d (matching strata are within unit).

## Why this period
Replication layer: the common H55 estimators on every non-holdout goal period with DQ2 reply labels, giving one comparable point per period (enforcer friction, correction rate, loop persistence, address effect). Per-period immune contrasts need ≥ 15 steps with a directed correction read; no period reaches that, so corrections' effect on escape is estimated only across periods (card, Amendment 1 and Results).

## Prediction
*Templated: the card's P1, P2, P4–P8, written 2026-10-04 06:26 UTC before any H55 outcome statistic.*
- P1: Spearman ρ(correction rate c_j, received field ν_j) > 0 (agent permutation, one-sided p < 0.05), if ≥ 6 agents qualify.
- P2: replies to an agent's corrections are more negative than replies to its other messages (γ < 0, p < 0.05), if ≥ 20 such replies.
- P4/P5/P6: corrections read in a loop or blocked spell raise escape; any directed read raises escape (descriptive per period).
- **Per-period verdict rule:** supported if every scorable primary test (P1, P2) passes; mixed if some do; failed if none does; descriptive if neither is scorable.

## Result
*Run 2026-10-04 (`analysis/explore.py`; data `data/processed/H55-norm-enforcer-immunity/G20/results.json`).*

| Statistic | Observed | Predicted |
| --- | --- | --- |
| P1 ρ(c_j, ν_j) | -0.22 (p 0.750; 10 agents) | > 0 |
| P1b partial ρ (own speaker field removed) | -0.22 (p 0.730) | ≥ half of P1 |
| P2 γ (replies to corrections − other replies, soft stance, FE) | -0.124 [-0.584, 0.189] (p 0.534; 39 replies) | < 0 |
| P2 placebo (long parents) γ | 0.134 (p 0.000) | ≈ 0 |
| P3 share of confident received opposes that are correction/decline subtypes | 0.72 (n 76) | ≥ 0.5 |
| Jev corrections per 100 parented agent messages (S_p) | 2.92 (45 of 1543) | – |
| Restatement loops: at-risk steps / with a directed read / with a correction read | 431 / 59 / 3 | – |
| Loop escape rate per step; mean episode length | 0.29; 4.33 | – |
| P6 address effect on loop escape (Δ, matched) | 0.004 [-0.132, 0.149] (n 59) | > 0 |
| v3 blocked spells: at-risk windows / with a directed read / with a correction read | 381 / 199 / 7 | – |
| P6 address effect on blocked escape (Δ) | 0.026 (n 196) | > 0 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 0 | P1/P2 against agent permutation and the within-target design |
| D unfitted predictions | 0 | per-period immune contrast not scorable (too few correction reads) |

## Notes
- Corrections use the validated Jev sensor (precision 0.93, recall ≈ 0.1; card Amendment 1); c_j is a scaled rate.
