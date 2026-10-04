# H18 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 2026-04-27)

**Verdict:** mixed
**Verdict (1b):** mixed (round 1b, 2026-10-04: ledger k, mention response, pre-registered rule; on reply labels: mixed; round-1 verdict kept above)
**Role:** exploratory
**Period:** regime III · mode C · N ≈ 12 · #best / #rest (Sonnet 4.6 moves to #best 04-02). Splits inside the period: NE17 outreach approval 04-14; NE18 04-20; joins 04-17, 04-22.

## Why this period
Longest two-room period (17 days): most power for β and the D2 wake design; roster grows by 2.

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

**Verdict rule (fixed now):** *supported* if P1 and P2 hold and D2 does not contradict (β̂_D2 ≥ 0.2, or < 200 D2 units); *failed* if β̂'s CI includes 0 or M_const is best; *mixed* otherwise (e.g. β̂ > 0 but M_rec best, or D2 contradicts D1). Fewer than 300 scored units: *descriptive*.

## Result
*Run 2026-10-03 (`analysis/fit_periods.py --period G38`); data in `data/processed/H18-attention-dilution/G38/` (`fits.json`). Figure: `figures/curves.pdf`.*

Sample: 17 days, 14 recipients, 4341 talk turns (3123 with k ≥ 1), 6806 scored (talk, sender) units, 1319 addressed (rate 0.194). k: median 3, mean 5.3, q90 11; mean room size 6.4.

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| P1 β̂ > 0, CI excl. 0 (expect 0.5–1.2) | β̂ = 0.69 [0.62, 0.80] | M_const: β = 0 | pass |
| P2 budget beats const and recency (within-day-block CV) | best sat (effective: sat~inv; k̂₀ = 1.83, ρ̂ = 0.80); Δℓ/unit inv − const 0.0362 [0.0210, 0.0518], inv − rec -0.0056 [-0.0142, 0.0023] | M_const, M_rec | pass |
| (secondary) day-blocked CV, agent propensities | best sat (sat~inv) | | — |
| P3 ε_S ∈ [−0.2, 0.5] | ε_S = 0.29 [0.20, 0.37]; B̂ = 0.43 senders addressed per talk | ε_S ≈ 1 (no budget) | pass |
| P4 mentions: e^γ ≥ 3, β_M < β_other − 0.3 | e^γ = 2.4; β_other = 0.75 [0.68, 0.85], β_M = 0.51 [0.38, 0.68] (1532 mention units) | β_M = β_other | fail |
| P10 invisible ≤ 1.5× non-pending, ≤ ½ pending | invisible 0.131 (n = 360), non-pending 0.080, pending (same talks) 0.246 | | fail |
| P5 D2 β̂ > 0, within ±0.4 of D1 | β̂_D2 = -0.13 [-0.41, 0.03] (1335 units, 89 resp.; wakes talking within 300 s: 0.43); 60 s: -0.08, stint: -0.10 | reactive-constant agents: ≈ 0 | contradicts |
| P6 room size (same days) | k̄ ratio large/small 0.91, p̄ ratio small/large 2.76, S ratio 2.23; room log-effect 0.62 [0.23, 0.92] without k → 0.66 [0.32, 1.01] with k (16 days) | room effect survives k | fail |
| P11 content-reply excess slope ≈ −β̂ (secondary) | overall excess 0.000; log-log slope — | slope 0 | fail |

Segments at step changes (5): 2026-04-02–2026-04-13: β̂ 0.69 ± 0.07; 2026-04-14–2026-04-16: β̂ 0.77 ± 0.22; 2026-04-17–2026-04-17: β̂ 1.01; 2026-04-20–2026-04-21: β̂ 0.63 ± 0.15; 2026-04-22–2026-04-24: β̂ 0.57 ± 0.15. Random-effects pooled 0.67 ± 0.05, I² = 0.00.

## Round 1b (improved data, 2026-10-04)
*Re-run on the DQ1 context ledger (`scheme/build_ledger.py`: pending sets = ledger items received since the previous talk call, i.e. `k_since_talk`; talk turns = ledger talk calls; first talk call of the day excluded) and scored two ways on the same units: the pre-registered mention response and the DQ2 reply response (the talk's `reply_pairs` parent is one of the sender's pending messages). `analysis/fit_periods.py --dir data/processed/H18-attention-dilution/r1b --resp resp|resp_reply`; data `data/processed/H18-attention-dilution/r1b/G38/fits_mention.json`, `fits_reply.json`. Day bootstrap B = 100 (#51: 40). Predictions and the verdict rule unchanged.*

| Statistic | Round 1 (call-start rule, mentions) | Round 1b, ledger k, mentions | Round 1b, ledger k, reply parent |
| --- | --- | --- | --- |
| scored units (response rate) | 6806 (0.194) | 6921 (0.195) | 6921 (0.199) |
| β̂ [95% CI] | 0.69 [0.62, 0.80] | 0.69 [0.62, 0.80] | 0.99 [0.94, 1.06] |
| CV winner (effective) | sat~inv | sat~inv | rec |
| ε_S | 0.29 | 0.29 | 0.01 |
| β̂_D2 (timer wakes, 300 s) | -0.13 [-0.41, 0.03] (1335 units) | -0.02 [-0.29, 0.19] (1265 units) | 0.55 [0.27, 0.85] (1265 units) |
| placebo (mention rates) | invisible 0.131 (n 360) · pending same talks 0.246 · non-pending 0.080 | invisible 0.087 (n 184) · pending same talks 0.307 · non-pending 0.080 | — (a reply parent must be visible) |
| verdict | mixed | **mixed** | mixed |

*Reading the reply column:* a talk message has at most one reply parent, and DQ2 labelled mostly the top-ranked candidate, so the reply response allocates one reply among the pending senders; its exponent is ≈ 1 minus the elasticity of "replies to someone pending" in k, a budget built into the measurement. It is reported, but the mention column carries the pre-registered test.

**Verdict (1b): mixed** (round 1: mixed).

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 2 | within-day-block CV: best sat~inv; inv − const Δℓ CI lower bound 0.0210 |
| H comparative | 1 | budget vs. recency: inv − rec Δℓ -0.0056 |
| B assumptions (timing) | 0 | D2 contradicts (β̂_D2 -0.13) |
| G ground truth | 0 | invisible-message placebo |

## Notes
- 2026-10-03: card created with the prediction, before any H18 real-data run.
- 2026-10-03: results filled by `write_period_cards.py results` from `fits.json` (run time 55.9 s).
