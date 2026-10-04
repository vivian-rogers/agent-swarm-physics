# H18 × G40: Connect your worlds into a 3D universe! (2026-05-04 → 2026-05-11)

**Verdict:** mixed
**Role:** exploratory
**Period:** regime III · mode C · N ≈ 15 · merged into #universe-coordination (GPT-5 alone in #rest). Splits inside the period: merge on the first day.

## Why this period
Merge A-B-A, side B: almost everyone in one room (#universe-coordination), so k per turn should rise for the merged agents.

## Prediction
*Written 2026-10-03, before running on this period (and before any real-data run of H18).*

Card predictions as they apply here (D1 = talk-turn backlog, primary):
- **P1:** β̂ (M_pow, agent×day propensities) > 0 with the day-bootstrap 95% CI excluding 0; expected size 0.5–1.2.
- **P2:** M_inv or M_sat has the best within-day-block held-out log-likelihood among M_const, M_inv, M_sat, M_rec; if M_sat, k̂₀ < 3. *(Effective-winner rule added 2026-10-03 before any real-data fit, card A2: sat with k̂₀ ≥ k_q90 or rec with flat weights count as constant-like.)*
- **P3:** Σ ≈ const: ε_S ∈ [−0.2, 0.5].
- **P4:** e^γ ≥ 3 for messages that @-mention the recipient, with a flatter slope (β_M < β_other − 0.3) where ≥ 100 mention units.
- **P10:** invisible (same-call) messages addressed at ≤ 1.5× the non-pending mention rate.
- **P5 (D2 timer wakes):** β̂_D2 > 0 with CI excluding 0 if ≥ 200 D2 units; β̂_D2 within ±0.4 of β̂_D1. *(Amended 2026-10-03 after the synthetic validation, before any real-data fit: D2 response = first talk within 300 s of the wake; card A1.)*
- **P7 (merge A-B-A):** for the agents merged on 05-04, k̄ is higher and per-pair uptake lower in #40 than in #39 and #41; S per talk turn within ±30%. Scored in `../NE42/`.

**Verdict rule (fixed now):** *supported* if P1 and P2 hold and D2 does not contradict (β̂_D2 ≥ 0.2, or < 200 D2 units); *failed* if β̂'s CI includes 0 or M_const is best; *mixed* otherwise (e.g. β̂ > 0 but M_rec best, or D2 contradicts D1). Fewer than 300 scored units: *descriptive*.

## Result
*Run 2026-10-03 (`analysis/fit_periods.py --period G40`); data in `data/processed/H18-attention-dilution/G40/` (`fits.json`). Figure: `figures/curves.pdf`.*

Sample: 5 days, 14 recipients, 1656 talk turns (1529 with k ≥ 1), 7002 scored (talk, sender) units, 818 addressed (rate 0.117). k: median 6, mean 11.0, q90 23; mean room size 14.0.

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| P1 β̂ > 0, CI excl. 0 (expect 0.5–1.2) | β̂ = 0.60 [0.51, 0.71] | M_const: β = 0 | pass |
| P2 budget beats const and recency (within-day-block CV) | best sat (effective: sat; k̂₀ = 4.41, ρ̂ = 0.90); Δℓ/unit inv − const 0.0134 [0.0011, 0.0252], inv − rec -0.0075 [-0.0180, 0.0045] | M_const, M_rec | fail |
| (secondary) day-blocked CV, agent propensities | best sat (sat) | | — |
| P3 ε_S ∈ [−0.2, 0.5] | ε_S = 0.38 [0.29, 0.45]; B̂ = 0.54 senders addressed per talk | ε_S ≈ 1 (no budget) | pass |
| P4 mentions: e^γ ≥ 3, β_M < β_other − 0.3 | e^γ = 2.7; β_other = 0.59 [0.47, 0.72], β_M = 0.65 [0.50, 0.96] (989 mention units) | β_M = β_other | fail |
| P10 invisible ≤ 1.5× non-pending, ≤ ½ pending | invisible 0.097 (n = 258), non-pending 0.040, pending (same talks) 0.162 | | fail |
| P5 D2 β̂ > 0, within ±0.4 of D1 | β̂_D2 = 0.57 [-0.03, 1.81] (206 units, 13 resp.; wakes talking within 300 s: 0.50); 60 s: 0.39, stint: 0.57 | reactive-constant agents: ≈ 0 | partial |
| P11 content-reply excess slope ≈ −β̂ (secondary) | overall excess 0.095; log-log slope -0.27 | slope 0 | pass |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 1 | within-day-block CV: best sat; inv − const Δℓ CI lower bound 0.0011 |
| H comparative | 0 | budget vs. recency: inv − rec Δℓ -0.0075 |
| B assumptions (timing) | 1 | D2 consistent (β̂_D2 0.57) |
| G ground truth | 0 | invisible-message placebo |

## Notes
- 2026-10-03: card created with the prediction, before any H18 real-data run.
- 2026-10-03: results filled by `write_period_cards.py results` from `fits.json` (run time 33.4 s).
