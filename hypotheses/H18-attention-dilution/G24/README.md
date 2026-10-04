# H18 × G24: Do random acts of kindness! (2025-12-22 → 2025-12-29)

**Verdict:** mixed
**Role:** exploratory
**Period:** regime I · mode C · N ≈ 10 · everyone in #general. Splits inside the period: none.

## Why this period
Regime I contrast after NE09 (chat visible during computer use), one room, N = 10, shared objective.

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
*Run 2026-10-03 (`analysis/fit_periods.py --period G24`); data in `data/processed/H18-attention-dilution/G24/` (`fits.json`). Figure: `figures/curves.pdf`.*

Sample: 5 days, 10 recipients, 1510 talk turns (1241 with k ≥ 1), 5718 scored (talk, sender) units, 517 addressed (rate 0.090). k: median 7, mean 10.0, q90 22; mean room size 10.0.

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| P1 β̂ > 0, CI excl. 0 (expect 0.5–1.2) | β̂ = 0.56 [0.52, 0.66] | M_const: β = 0 | pass |
| P2 budget beats const and recency (within-day-block CV) | best sat (effective: sat; k̂₀ = 4.97, ρ̂ = 0.91); Δℓ/unit inv − const 0.0050 [-0.0049, 0.0132], inv − rec -0.0076 [-0.0160, 0.0006] | M_const, M_rec | fail |
| (secondary) day-blocked CV, agent propensities | best sat (sat) | | — |
| P3 ε_S ∈ [−0.2, 0.5] | ε_S = 0.38 [0.24, 0.43]; B̂ = 0.42 senders addressed per talk | ε_S ≈ 1 (no budget) | pass |
| P4 mentions: e^γ ≥ 3, β_M < β_other − 0.3 | e^γ = 4.5; β_other = 0.63 [0.56, 0.88], β_M = 0.45 [-0.14, 0.55] (628 mention units) | β_M = β_other | fail |
| P10 invisible ≤ 1.5× non-pending, ≤ ½ pending | invisible 0.130 (n = 843), non-pending 0.030, pending (same talks) 0.115 | | fail |
| P11 content-reply excess slope ≈ −β̂ (secondary) | overall excess 0.132; log-log slope -0.24 | slope 0 | pass |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 1 | within-day-block CV: best sat; inv − const Δℓ CI lower bound -0.0049 |
| H comparative | 0 | budget vs. recency: inv − rec Δℓ -0.0076 |
| G ground truth | 0 | invisible-message placebo |

## Notes
- 2026-10-03: card created with the prediction, before any H18 real-data run.
- 2026-10-03: results filled by `write_period_cards.py results` from `fits.json` (run time 28.4 s).
