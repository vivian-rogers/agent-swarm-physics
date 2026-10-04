# H18 × G27: Hack the OWASP Juice Shop hacking playground (2026-01-12 → 2026-01-26)

**Verdict:** supported
**Role:** exploratory
**Period:** regime I · mode K · N ≈ 10 · everyone in #general. Splits inside the period: none.

## Why this period
Regime I contrast, two-week competition (mode K): agents mostly work alone, so k is driven by others' reports.

## Prediction
*Written 2026-10-03, before running on this period (and before any real-data run of H18).*

Card predictions as they apply here (D1 = talk-turn backlog, primary):
- **P1:** β̂ (M_pow, agent×day propensities) > 0 with the day-bootstrap 95% CI excluding 0; expected size 0.5–1.2.
- **P2:** M_inv or M_sat has the best within-day-block held-out log-likelihood among M_const, M_inv, M_sat, M_rec; if M_sat, k̂₀ < 3. *(Effective-winner rule added 2026-10-03 before any real-data fit, card A2: sat with k̂₀ ≥ k_q90 or rec with flat weights count as constant-like.)*
- **P3:** Σ ≈ const: ε_S ∈ [−0.2, 0.5].
- **P4:** e^γ ≥ 3 for messages that @-mention the recipient, with a flatter slope (β_M < β_other − 0.3) where ≥ 100 mention units.
- **P10:** invisible (same-call) messages addressed at ≤ 1.5× the non-pending mention rate.
- **P8:** β̂ within ±0.3 of the pooled regime-III β̂ (scored across periods in the main card).

**Verdict rule (fixed now):** *supported* if P1 and P2 hold; *failed* if β̂'s CI includes 0 or M_const is best; *mixed* otherwise (e.g. β̂ > 0 but M_rec best). Fewer than 300 scored units: *descriptive*.

## Result
*Run 2026-10-03 (`analysis/fit_periods.py --period G27`); data in `data/processed/H18-attention-dilution/G27/` (`fits.json`). Figure: `figures/curves.pdf`.*

Sample: 10 days, 10 recipients, 3588 talk turns (3011 with k ≥ 1), 13743 scored (talk, sender) units, 1593 addressed (rate 0.116). k: median 6, mean 10.1, q90 22; mean room size 10.0.

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| P1 β̂ > 0, CI excl. 0 (expect 0.5–1.2) | β̂ = 0.69 [0.56, 0.80] | M_const: β = 0 | pass |
| P2 budget beats const and recency (within-day-block CV) | best sat (effective: sat~inv; k̂₀ = 2.21, ρ̂ = 0.87); Δℓ/unit inv − const 0.0172 [0.0044, 0.0295], inv − rec -0.0006 [-0.0073, 0.0062] | M_const, M_rec | pass |
| (secondary) day-blocked CV, agent propensities | best sat (sat~inv) | | — |
| P3 ε_S ∈ [−0.2, 0.5] | ε_S = 0.33 [0.23, 0.45]; B̂ = 0.53 senders addressed per talk | ε_S ≈ 1 (no budget) | pass |
| P4 mentions: e^γ ≥ 3, β_M < β_other − 0.3 | e^γ = 1.2; β_other = 0.69 [0.56, 0.78], β_M = 0.70 [0.53, 0.89] (2109 mention units) | β_M = β_other | fail |
| P10 invisible ≤ 1.5× non-pending, ≤ ½ pending | invisible 0.298 (n = 2354), non-pending 0.064, pending (same talks) 0.202 | | fail |
| P11 content-reply excess slope ≈ −β̂ (secondary) | overall excess 0.151; log-log slope -0.18 | slope 0 | fail |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 2 | within-day-block CV: best sat~inv; inv − const Δℓ CI lower bound 0.0044 |
| H comparative | 1 | budget vs. recency: inv − rec Δℓ -0.0006 |
| G ground truth | 0 | invisible-message placebo |

## Notes
- 2026-10-03: card created with the prediction, before any H18 real-data run.
- 2026-10-03: results filled by `write_period_cards.py results` from `fits.json` (run time 69.3 s).
