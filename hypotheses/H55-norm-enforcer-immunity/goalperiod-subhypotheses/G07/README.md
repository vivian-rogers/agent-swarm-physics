# H55 × G07: Holiday (human helpers arrive) (2025-07-16 → 07-17)

**Verdict:** descriptive
**Verdict (1c):** descriptive (round 1c, stance v2.1; fewer than 5 validated disagreement flags in the period)
**Role:** replication
**Period:** regime I · up to 4 agents · 2 non-holdout days · units 7 (matching strata are within unit).

## Why this period
Replication layer: the common H55 estimators on every non-holdout goal period with DQ2 reply labels, giving one comparable point per period (enforcer friction, correction rate, loop persistence, address effect). Per-period immune contrasts need ≥ 15 steps with a directed correction read; no period reaches that, so corrections' effect on escape is estimated only across periods (card, Amendment 1 and Results).

## Prediction
*Templated: the card's P1, P2, P4–P8, written 2026-10-04 06:26 UTC before any H55 outcome statistic.*
- P1: Spearman ρ(correction rate c_j, received field ν_j) > 0 (agent permutation, one-sided p < 0.05), if ≥ 6 agents qualify.
- P2: replies to an agent's corrections are more negative than replies to its other messages (γ < 0, p < 0.05), if ≥ 20 such replies.
- P4/P5/P6: corrections read in a loop or blocked spell raise escape; any directed read raises escape (descriptive per period).
- **Per-period verdict rule:** supported if every scorable primary test (P1, P2) passes; mixed if some do; failed if none does; descriptive if neither is scorable.

## Result
*Run 2026-10-04 (`analysis/explore.py`; data `data/processed/H55-norm-enforcer-immunity/G07/results.json`).*

| Statistic | Observed | Predicted |
| --- | --- | --- |
| P1 ρ(c_j, ν_j) | – (p –; 4 agents) — not scorable: eligible agents 4 < 6 | > 0 |
| P1b partial ρ (own speaker field removed) | – (p –) | ≥ half of P1 |
| P2 γ (replies to corrections − other replies, soft stance, FE) | – [–, –] (p –; 0 replies) — not scorable | < 0 |
| P2 placebo (long parents) γ | 0.135 (p 0.139) | ≈ 0 |
| P3 share of confident received opposes that are correction/decline subtypes | 1.00 (n 2) | ≥ 0.5 |
| Jev corrections per 100 parented agent messages (S_p) | 2.19 (4 of 183) | – |
| Restatement loops: at-risk steps / with a directed read / with a correction read | 16 / 1 / 0 | – |
| Loop escape rate per step; mean episode length | 0.31; 3.83 | – |
| P6 address effect on loop escape (Δ, matched) | – [–, –] (n 0) | > 0 |
| v3 blocked spells: at-risk windows / with a directed read / with a correction read | 9 / 7 / 0 | – |
| P6 address effect on blocked escape (Δ) | – (n 0) | > 0 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 0 | P1/P2 against agent permutation and the within-target design |
| D unfitted predictions | 0 | per-period immune contrast not scorable (too few correction reads) |

## Notes
- Corrections use the validated Jev sensor (precision 0.93, recall ≈ 0.1; card Amendment 1); c_j is a scaled rate.

## Round 1c (stance v2.1, 2026-10-04)
*Pre-registered in the card (Round 1c, 22:14 UTC; A1c). Data: `data/processed/H55-norm-enforcer-immunity/r1c/`.*

no friction test scorable (fewer than 6 eligible agents and fewer than 20 replies to C_v2 messages). Replies 160, validated disagreement flags 0, replies to C_v2 messages 6. Immune contrasts are pooled across periods (card).
