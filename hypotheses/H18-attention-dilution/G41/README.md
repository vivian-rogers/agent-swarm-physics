# H18 × G41: Perform novel research! (2026-05-11 → 2026-05-18)

**Verdict:** mixed
**Role:** exploratory
**Period:** regime III · mode I · N ≈ 15 · #best / #rest (split back 05-11). Splits inside the period: split on the first day.

## Why this period
Merge A-B-A, side A': split back to the #39 partition.

## Prediction
*Written 2026-10-03, before running on this period (and before any real-data run of H18).*

Card predictions as they apply here (D1 = talk-turn backlog, primary):
- **P1:** β̂ (M_pow, agent×day propensities) > 0 with the day-bootstrap 95% CI excluding 0; expected size 0.5–1.2.
- **P2:** M_inv or M_sat has the best within-day-block held-out log-likelihood among M_const, M_inv, M_sat, M_rec; if M_sat, k̂₀ < 3. *(Effective-winner rule added 2026-10-03 before any real-data fit, card A2: sat with k̂₀ ≥ k_q90 or rec with flat weights count as constant-like.)*
- **P3:** Σ ≈ const: ε_S ∈ [−0.2, 0.5].
- **P4:** e^γ ≥ 3 for messages that @-mention the recipient, with a flatter slope (β_M < β_other − 0.3) where ≥ 100 mention units.
- **P10:** invisible (same-call) messages addressed at ≤ 1.5× the non-pending mention rate.
- **P5 (D2 timer wakes):** β̂_D2 > 0 with CI excluding 0 if ≥ 200 D2 units; β̂_D2 within ±0.4 of β̂_D1. *(Amended 2026-10-03 after the synthetic validation, before any real-data fit: D2 response = first talk within 300 s of the wake; card A1.)*
- **P6 (room size):** on the same days, per-pair uptake is higher in the smaller room by about k̄_large/k̄_small (within ×2); the room coefficient's CI includes 0 once k is in the model.
- **P7 (merge A-B-A):** for the agents merged on 05-04, k̄ is higher and per-pair uptake lower in #40 than in #39 and #41; S per talk turn within ±30%. Scored in `../NE42/`.

**Verdict rule (fixed now):** *supported* if P1 and P2 hold and D2 does not contradict (β̂_D2 ≥ 0.2, or < 200 D2 units); *failed* if β̂'s CI includes 0 or M_const is best; *mixed* otherwise (e.g. β̂ > 0 but M_rec best, or D2 contradicts D1). Fewer than 300 scored units: *descriptive*.

## Result
*Run 2026-10-03 (`analysis/fit_periods.py --period G41`); data in `data/processed/H18-attention-dilution/G41/` (`fits.json`). Figure: `figures/curves.pdf`.*

Sample: 5 days, 14 recipients, 2071 talk turns (1789 with k ≥ 1), 5976 scored (talk, sender) units, 1386 addressed (rate 0.232). k: median 4, mean 8.0, q90 18; mean room size 9.4.

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| P1 β̂ > 0, CI excl. 0 (expect 0.5–1.2) | β̂ = 0.65 [0.55, 0.74] | M_const: β = 0 | pass |
| P2 budget beats const and recency (within-day-block CV) | best sat (effective: sat~inv; k̂₀ = 2.94, ρ̂ = 0.87); Δℓ/unit inv − const 0.0357 [0.0068, 0.0723], inv − rec -0.0094 [-0.0207, -0.0022] | M_const, M_rec | pass |
| (secondary) day-blocked CV, agent propensities | best sat (sat~inv) | | — |
| P3 ε_S ∈ [−0.2, 0.5] | ε_S = 0.34 [0.26, 0.42]; B̂ = 0.78 senders addressed per talk | ε_S ≈ 1 (no budget) | pass |
| P4 mentions: e^γ ≥ 3, β_M < β_other − 0.3 | e^γ = 1.9; β_other = 0.69 [0.55, 0.80], β_M = 0.57 [0.48, 0.62] (1753 mention units) | β_M = β_other | fail |
| P10 invisible ≤ 1.5× non-pending, ≤ ½ pending | invisible 0.218 (n = 362), non-pending 0.102, pending (same talks) 0.318 | | fail |
| P5 D2 β̂ > 0, within ±0.4 of D1 | β̂_D2 = 0.14 [-0.83, 0.62] (617 units, 113 resp.; wakes talking within 300 s: 0.49); 60 s: 0.31, stint: 0.20 | reactive-constant agents: ≈ 0 | contradicts |
| P6 room size (same days) | k̄ ratio large/small 2.45, p̄ ratio small/large 1.50, S ratio 0.78; room log-effect 0.72 [0.52, 0.89] without k → 0.07 [-0.14, 0.30] with k (5 days) | room effect survives k | pass |
| P11 content-reply excess slope ≈ −β̂ (secondary) | overall excess 0.254; log-log slope -0.44 | slope 0 | pass |

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 2 | within-day-block CV: best sat~inv; inv − const Δℓ CI lower bound 0.0068 |
| H comparative | 1 | budget vs. recency: inv − rec Δℓ -0.0094 |
| B assumptions (timing) | 0 | D2 contradicts (β̂_D2 0.14) |
| G ground truth | 0 | invisible-message placebo |

## Notes
- 2026-10-03: card created with the prediction, before any H18 real-data run.
- 2026-10-03: results filled by `write_period_cards.py results` from `fits.json` (run time 35.2 s).
