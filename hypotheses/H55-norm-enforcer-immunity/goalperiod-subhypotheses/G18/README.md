# H55 × G18: Reduce global poverty (2025-10-20 → 10-31)

**Verdict:** failed
**Verdict (1c):** failed (round 1c, stance v2.1)
**Role:** replication
**Period:** regime I · up to 8 agents · 10 non-holdout days · units 18a, 18b, 18c (matching strata are within unit).

## Why this period
Replication layer: the common H55 estimators on every non-holdout goal period with DQ2 reply labels, giving one comparable point per period (enforcer friction, correction rate, loop persistence, address effect). Per-period immune contrasts need ≥ 15 steps with a directed correction read; no period reaches that, so corrections' effect on escape is estimated only across periods (card, Amendment 1 and Results).

## Prediction
*Templated: the card's P1, P2, P4–P8, written 2026-10-04 06:26 UTC before any H55 outcome statistic.*
- P1: Spearman ρ(correction rate c_j, received field ν_j) > 0 (agent permutation, one-sided p < 0.05), if ≥ 6 agents qualify.
- P2: replies to an agent's corrections are more negative than replies to its other messages (γ < 0, p < 0.05), if ≥ 20 such replies.
- P4/P5/P6: corrections read in a loop or blocked spell raise escape; any directed read raises escape (descriptive per period).
- **Per-period verdict rule:** supported if every scorable primary test (P1, P2) passes; mixed if some do; failed if none does; descriptive if neither is scorable.

## Result
*Run 2026-10-04 (`analysis/explore.py`; data `data/processed/H55-norm-enforcer-immunity/G18/results.json`).*

| Statistic | Observed | Predicted |
| --- | --- | --- |
| P1 ρ(c_j, ν_j) | 0.48 (p 0.119; 8 agents) | > 0 |
| P1b partial ρ (own speaker field removed) | 0.38 (p 0.181) | ≥ half of P1 |
| P2 γ (replies to corrections − other replies, soft stance, FE) | 0.118 [-0.009, 0.242] (p 0.079; 65 replies) | < 0 |
| P2 placebo (long parents) γ | 0.026 (p 0.357) | ≈ 0 |
| P3 share of confident received opposes that are correction/decline subtypes | 0.49 (n 126) | ≥ 0.5 |
| Jev corrections per 100 parented agent messages (S_p) | 1.33 (43 of 3225) | – |
| Restatement loops: at-risk steps / with a directed read / with a correction read | 1900 / 226 / 0 | – |
| Loop escape rate per step; mean episode length | 0.23; 5.31 | – |
| P6 address effect on loop escape (Δ, matched) | 0.092 [0.037, 0.155] (n 226) | > 0 |
| v3 blocked spells: at-risk windows / with a directed read / with a correction read | 843 / 420 / 10 | – |
| P6 address effect on blocked escape (Δ) | 0.057 (n 418) | > 0 |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 0 | P1/P2 against agent permutation and the within-target design |
| D unfitted predictions | 0 | per-period immune contrast not scorable (too few correction reads) |

## Notes
- Corrections use the validated Jev sensor (precision 0.93, recall ≈ 0.1; card Amendment 1); c_j is a scaled rate.

## Round 1c (stance v2.1, 2026-10-04)
*Pre-registered in the card (Round 1c, 22:14 UTC; A1c). Data: `data/processed/H55-norm-enforcer-immunity/r1c/`.*

P1-v2 ρ(c_j, ν^D_j) -0.60 (8 agents; p greater 0.94, less 0.06); P2-v2 γ^D -0.90 pp (163 replies to C_v2 messages; label-noise null p greater 0.83); flag rate 0.61% vs 1.77%. Replies 3715, validated disagreement flags 64, replies to C_v2 messages 163. Immune contrasts are pooled across periods (card).
