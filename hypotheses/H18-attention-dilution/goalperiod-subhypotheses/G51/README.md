# H18 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 2026-09-07)

**Verdict:** mixed
**Role:** exploratory
**Period:** regime III · mode P · N ≈ 21 · #general; GPT-5.6 isolated rooms 07-09/10; #focus 08-05 to 08-24. Splits inside the period: roster joins (N 21 to 29); tail 09-07 onward is held out.

## Why this period
Largest N (21 → 29 on non-holdout days), 8 h days: the within-period size gradient for the J/N question, and the most data.

## Prediction
*Written 2026-10-03, before running on this period (and before any real-data run of H18).*

Card predictions as they apply here (D1 = talk-turn backlog, primary):
- **P1:** β̂ (M_pow, agent×day propensities) > 0 with the day-bootstrap 95% CI excluding 0; expected size 0.5–1.2.
- **P2:** M_inv or M_sat has the best within-day-block held-out log-likelihood among M_const, M_inv, M_sat, M_rec; if M_sat, k̂₀ < 3. *(Effective-winner rule added 2026-10-03 before any real-data fit, card A2: sat with k̂₀ ≥ k_q90 or rec with flat weights count as constant-like.)*
- **P3:** Σ ≈ const: ε_S ∈ [−0.2, 0.5].
- **P4:** e^γ ≥ 3 for messages that @-mention the recipient, with a flatter slope (β_M < β_other − 0.3) where ≥ 100 mention units.
- **P10:** invisible (same-call) messages addressed at ≤ 1.5× the non-pending mention rate.
- **P5 (D2 timer wakes):** β̂_D2 > 0 with CI excluding 0 if ≥ 200 D2 units; β̂_D2 within ±0.4 of β̂_D1. *(Amended 2026-10-03 after the synthetic validation, before any real-data fit: D2 response = first talk within 300 s of the wake; card A1.)*
- **P9 (segments at roster joins):** per-pair uptake p̄ falls as N rises, while the effective budget B̂ stays flat (|ρ| < 0.3).

**Verdict rule (fixed now):** *supported* if P1 and P2 hold and D2 does not contradict (β̂_D2 ≥ 0.2, or < 200 D2 units); *failed* if β̂'s CI includes 0 or M_const is best; *mixed* otherwise (e.g. β̂ > 0 but M_rec best, or D2 contradicts D1). Fewer than 300 scored units: *descriptive*.

## Result
*Run 2026-10-03 (`analysis/fit_periods.py --period G51`); data in `data/processed/H18-attention-dilution/G51/` (`fits.json`). Figure: `figures/curves.pdf`.*

Sample: 45 days, 32 recipients, 39796 talk turns (33125 with k ≥ 1), 195913 scored (talk, sender) units, 20069 addressed (rate 0.102). k: median 7, mean 19.9, q90 45; mean room size 23.7.

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| P1 β̂ > 0, CI excl. 0 (expect 0.5–1.2) | β̂ = 0.61 [0.58, 0.63] | M_const: β = 0 | pass |
| P2 budget beats const and recency (within-day-block CV) | best sat (effective: sat; k̂₀ = 6.02, ρ̂ = 0.95); Δℓ/unit inv − const 0.0134 [0.0094, 0.0175], inv − rec -0.0088 [-0.0115, -0.0061] | M_const, M_rec | fail |
| (secondary) day-blocked CV, agent propensities | best sat (sat) | | — |
| P3 ε_S ∈ [−0.2, 0.5] | ε_S = 0.21 [0.19, 0.23]; B̂ = 0.61 senders addressed per talk | ε_S ≈ 1 (no budget) | pass |
| P4 mentions: e^γ ≥ 3, β_M < β_other − 0.3 | e^γ = 11.6; β_other = 0.81 [0.79, 0.83], β_M = 0.39 [0.37, 0.40] (26573 mention units) | β_M = β_other | pass |
| P10 invisible ≤ 1.5× non-pending, ≤ ½ pending | invisible 0.146 (n = 11870), non-pending 0.026, pending (same talks) 0.134 | | fail |
| P5 D2 β̂ > 0, within ±0.4 of D1 | β̂_D2 = 0.50 [0.45, 0.56] (129567 units, 3520 resp.; wakes talking within 300 s: 0.28); 60 s: 0.51, stint: 0.50 | reactive-constant agents: ≈ 0 | pass |
| P9 #51 segments: p̄ falls with N, B̂ flat (\|ρ\| < 0.3) | across 10 segments (N_room 21 → 31): ρ(p̄, N) = -0.87 (p = 0.001); ρ(B̂, N) = -0.38 (p = 0.28); B̂ 0.46–0.73 | B̂ ∝ N^(1−β) | p̄ part pass; B̂ part borderline (\|ρ\| = 0.38, n.s.) |
| P11 content-reply excess slope ≈ −β̂ (secondary) | overall excess 0.000; log-log slope — | slope 0 | fail |

Segments at step changes (10): 2026-07-06–2026-07-08: β̂ 0.49 ± 0.01; 2026-07-09–2026-07-09: β̂ 0.88; 2026-07-10–2026-07-16: β̂ 1.11 ± 0.03; 2026-07-17–2026-07-23: β̂ 0.93 ± 0.03; 2026-07-24–2026-07-28: β̂ 0.50 ± 0.04; 2026-07-29–2026-08-27: β̂ 0.61 ± 0.02; 2026-08-28–2026-08-31: β̂ 0.50 ± 0.06; 2026-09-01–2026-09-02: β̂ 0.50 ± 0.07; 2026-09-03–2026-09-03: β̂ 0.59; 2026-09-04–2026-09-04: β̂ 0.61. Random-effects pooled 0.67 ± 0.09, I² = 0.99.

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 1 | within-day-block CV: best sat; inv − const Δℓ CI lower bound 0.0094 |
| H comparative | 0 | budget vs. recency: inv − rec Δℓ -0.0088 |
| B assumptions (timing) | 1 | D2 consistent (β̂_D2 0.50) |
| G ground truth | 0 | invisible-message placebo |

## Notes
- 2026-10-03: card created with the prediction, before any H18 real-data run.
- 2026-10-03: results filled by `write_period_cards.py results` from `fits.json` (run time 777.5 s).
