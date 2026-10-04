# H55 × G11: Free week (2025-08-25 → 08-29)

**Verdict:** failed
**Verdict (1c):** descriptive (round 1c, stance v2.1; fewer than 5 validated disagreement flags in the period)
**Role:** replication
**Period:** regime I · up to 7 agents · 5 non-holdout days · units 11 (matching strata are within unit).

## Why this period
Replication layer: the common H55 estimators on every non-holdout goal period with DQ2 reply labels, giving one comparable point per period (enforcer friction, correction rate, loop persistence, address effect). Per-period immune contrasts need ≥ 15 steps with a directed correction read; no period reaches that, so corrections' effect on escape is estimated only across periods (card, Amendment 1 and Results).

## Prediction
*Templated: the card's P1, P2, P4–P8, written 2026-10-04 06:26 UTC before any H55 outcome statistic.*
- P1: Spearman ρ(correction rate c_j, received field ν_j) > 0 (agent permutation, one-sided p < 0.05), if ≥ 6 agents qualify.
- P2: replies to an agent's corrections are more negative than replies to its other messages (γ < 0, p < 0.05), if ≥ 20 such replies.
- P4/P5/P6: corrections read in a loop or blocked spell raise escape; any directed read raises escape (descriptive per period).
- **Per-period verdict rule:** supported if every scorable primary test (P1, P2) passes; mixed if some do; failed if none does; descriptive if neither is scorable.

## Result
*Run 2026-10-04 (`analysis/explore.py`; data `data/processed/H55-norm-enforcer-immunity/G11/results.json`).*

| Statistic | Observed | Predicted |
| --- | --- | --- |
| P1 ρ(c_j, ν_j) | 0.39 (p 0.231; 6 agents) | > 0 |
| P1b partial ρ (own speaker field removed) | 0.34 (p 0.303) | ≥ half of P1 |
| P2 γ (replies to corrections − other replies, soft stance, FE) | – [–, –] (p –; 2 replies) — not scorable | < 0 |
| P2 placebo (long parents) γ | 0.103 (p 0.040) | ≈ 0 |
| P3 share of confident received opposes that are correction/decline subtypes | 0.60 (n 5) | ≥ 0.5 |
| Jev corrections per 100 parented agent messages (S_p) | 0.49 (3 of 612) | – |
| Restatement loops: at-risk steps / with a directed read / with a correction read | 463 / 39 / 0 | – |
| Loop escape rate per step; mean episode length | 0.28; 4.50 | – |
| P6 address effect on loop escape (Δ, matched) | 0.109 [-0.006, 0.295] (n 39) | > 0 |
| v3 blocked spells: at-risk windows / with a directed read / with a correction read | 186 / 80 / 0 | – |
| P6 address effect on blocked escape (Δ) | 0.072 (n 80) | > 0 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 0 | P1/P2 against agent permutation and the within-target design |
| D unfitted predictions | 0 | per-period immune contrast not scorable (too few correction reads) |

## Notes
- Corrections use the validated Jev sensor (precision 0.93, recall ≈ 0.1; card Amendment 1); c_j is a scaled rate.

## Round 1c (stance v2.1, 2026-10-04)
*Pre-registered in the card (Round 1c, 22:14 UTC; A1c). Data: `data/processed/H55-norm-enforcer-immunity/r1c/`.*

P1-v2 ρ(c_j, ν^D_j) -0.09 (6 agents; p greater 0.60, less 0.46); P2-v2 γ^D +0.30 pp (25 replies to C_v2 messages; label-noise null p greater 0.05); flag rate 0.00% vs 0.15%. Replies 711, validated disagreement flags 1, replies to C_v2 messages 25. Immune contrasts are pooled across periods (card).
