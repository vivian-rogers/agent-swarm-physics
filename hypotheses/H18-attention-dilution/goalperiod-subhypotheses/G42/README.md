# H18 × G42: Run your own Youtube channel! (2026-05-18 → 2026-05-25)

**Verdict:** mixed
**Verdict (1b):** mixed (round 1b, 2026-10-04: ledger k, mention response, pre-registered rule; on reply labels: mixed; round-1 verdict kept above)
**Role:** replication (exploratory)
**Period:** regime III · mode I · N ≈ 15 · #best / #rest. Splits inside the period: Gemini 3.5 Flash joins 05-20.

## Why this period
Two rooms, individual objectives; a join inside.

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
*Run 2026-10-03 (`analysis/fit_periods.py --period G42`); data in `data/processed/H18-attention-dilution/G42/` (`fits.json`). Figure: `figures/curves.pdf`.*

Sample: 5 days, 15 recipients, 1134 talk turns (926 with k ≥ 1), 2744 scored (talk, sender) units, 671 addressed (rate 0.245). k: median 4, mean 7.0, q90 14; mean room size 9.7.

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| P1 β̂ > 0, CI excl. 0 (expect 0.5–1.2) | β̂ = 0.72 [0.69, 0.86] | M_const: β = 0 | pass |
| P2 budget beats const and recency (within-day-block CV) | best rec (effective: rec; k̂₀ = 1.58, ρ̂ = 0.77); Δℓ/unit inv − const 0.0393 [0.0277, 0.0530], inv − rec -0.0171 [-0.0351, -0.0003] | M_const, M_rec | fail |
| (secondary) day-blocked CV, agent propensities | best rec (rec) | | — |
| P3 ε_S ∈ [−0.2, 0.5] | ε_S = 0.17 [0.09, 0.27]; B̂ = 0.73 senders addressed per talk | ε_S ≈ 1 (no budget) | pass |
| P4 mentions: e^γ ≥ 3, β_M < β_other − 0.3 | e^γ = 5.2; β_other = 0.80 [0.50, 1.20], β_M = 0.65 [0.48, 1.02] (768 mention units) | β_M = β_other | fail |
| P10 invisible ≤ 1.5× non-pending, ≤ ½ pending | invisible 0.289 (n = 121), non-pending 0.064, pending (same talks) 0.382 | | fail |
| P5 D2 timer wakes (300 s) | 125 units, 34 responses | | underpowered |
| P6 room size (same days) | k̄ ratio large/small 2.00, p̄ ratio small/large 2.97, S ratio 1.44; room log-effect 0.61 [0.28, 0.88] without k → 0.08 [-0.29, 0.29] with k (5 days) | room effect survives k | pass |
| P11 content-reply excess slope ≈ −β̂ (secondary) | overall excess 0.000; log-log slope — | slope 0 | fail |

Segments at step changes (2): 2026-05-18–2026-05-19: β̂ 0.69 ± 0.02; 2026-05-20–2026-05-22: β̂ 0.75 ± 0.10. Random-effects pooled 0.69 ± 0.02, I² = 0.00.

## Round 1b (improved data, 2026-10-04)
*Re-run on the DQ1 context ledger (`scheme/build_ledger.py`: pending sets = ledger items received since the previous talk call, i.e. `k_since_talk`; talk turns = ledger talk calls; first talk call of the day excluded) and scored two ways on the same units: the pre-registered mention response and the DQ2 reply response (the talk's `reply_pairs` parent is one of the sender's pending messages). `analysis/fit_periods.py --dir data/processed/H18-attention-dilution/r1b --resp resp|resp_reply`; data `data/processed/H18-attention-dilution/r1b/G42/fits_mention.json`, `fits_reply.json`. Day bootstrap B = 100 (#51: 40). Predictions and the verdict rule unchanged.*

| Statistic | Round 1 (call-start rule, mentions) | Round 1b, ledger k, mentions | Round 1b, ledger k, reply parent |
| --- | --- | --- | --- |
| scored units (response rate) | 2744 (0.245) | 2816 (0.243) | 2816 (0.156) |
| β̂ [95% CI] | 0.72 [0.69, 0.86] | 0.72 [0.68, 0.90] | 0.94 [0.85, 1.06] |
| CV winner (effective) | rec | rec | rec |
| ε_S | 0.17 | 0.16 | -0.09 |
| β̂_D2 (timer wakes, 300 s) | underpowered | underpowered | underpowered |
| placebo (mention rates) | invisible 0.289 (n 121) · pending same talks 0.382 · non-pending 0.064 | invisible 0.253 (n 91) · pending same talks 0.397 · non-pending 0.065 | — (a reply parent must be visible) |
| verdict | mixed | **mixed** | mixed |

*Reading the reply column:* a talk message has at most one reply parent, and DQ2 labelled mostly the top-ranked candidate, so the reply response allocates one reply among the pending senders; its exponent is ≈ 1 minus the elasticity of "replies to someone pending" in k, a budget built into the measurement. It is reported, but the mention column carries the pre-registered test.

**Verdict (1b): mixed** (round 1: mixed).

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 1 | within-day-block CV: best rec; inv − const Δℓ CI lower bound 0.0277 |
| H comparative | 0 | budget vs. recency: inv − rec Δℓ -0.0171 |
| B assumptions (timing) | 0 | D2 underpowered (β̂_D2 —) |
| G ground truth | 0 | invisible-message placebo |

## Notes
- 2026-10-03: card created with the prediction, before any H18 real-data run.
- 2026-10-03: results filled by `write_period_cards.py results` from `fits.json` (run time 19.8 s).
