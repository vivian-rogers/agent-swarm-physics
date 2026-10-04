# H18 × G35: Test your game to make it as fun and functional as you can! (2026-03-16 → 2026-03-23)

**Verdict:** mixed
**Verdict (1b):** mixed (round 1b, 2026-10-04: ledger k, mention response, pre-registered rule; on reply labels: mixed; round-1 verdict kept above)
**Role:** exploratory
**Period:** regime II · mode C · N ≈ 13 · #best (3) / #rest (10) from 03-16 (NE15). Splits inside the period: NE15 split on the first day.

## Why this period
The NE15 split's first non-holdout week: #best (3 agents) and #rest (10) on the same days, same goal. The cleanest same-day room-size contrast in the data.

## Prediction
*Written 2026-10-03, before running on this period (and before any real-data run of H18).*

Card predictions as they apply here (D1 = talk-turn backlog, primary):
- **P1:** β̂ (M_pow, agent×day propensities) > 0 with the day-bootstrap 95% CI excluding 0; expected size 0.5–1.2.
- **P2:** M_inv or M_sat has the best within-day-block held-out log-likelihood among M_const, M_inv, M_sat, M_rec; if M_sat, k̂₀ < 3. *(Effective-winner rule added 2026-10-03 before any real-data fit, card A2: sat with k̂₀ ≥ k_q90 or rec with flat weights count as constant-like.)*
- **P3:** Σ ≈ const: ε_S ∈ [−0.2, 0.5].
- **P4:** e^γ ≥ 3 for messages that @-mention the recipient, with a flatter slope (β_M < β_other − 0.3) where ≥ 100 mention units.
- **P10:** invisible (same-call) messages addressed at ≤ 1.5× the non-pending mention rate.
- **P6 (room size):** on the same days, per-pair uptake is higher in the smaller room by about k̄_large/k̄_small (within ×2); the room coefficient's CI includes 0 once k is in the model.

**Verdict rule (fixed now):** *supported* if P1 and P2 hold; *failed* if β̂'s CI includes 0 or M_const is best; *mixed* otherwise (e.g. β̂ > 0 but M_rec best). Fewer than 300 scored units: *descriptive*.

## Result
*Run 2026-10-03 (`analysis/fit_periods.py --period G35`); data in `data/processed/H18-attention-dilution/G35/` (`fits.json`). Figure: `figures/curves.pdf`.*

Sample: 5 days, 12 recipients, 1995 talk turns (1679 with k ≥ 1), 5568 scored (talk, sender) units, 895 addressed (rate 0.161). k: median 4, mean 7.7, q90 16; mean room size 7.3.

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| P1 β̂ > 0, CI excl. 0 (expect 0.5–1.2) | β̂ = 0.75 [0.63, 0.82] | M_const: β = 0 | pass |
| P2 budget beats const and recency (within-day-block CV) | best rec (effective: rec; k̂₀ = 1.84, ρ̂ = 0.79); Δℓ/unit inv − const 0.0274 [0.0117, 0.0400], inv − rec -0.0121 [-0.0207, -0.0044] | M_const, M_rec | fail |
| (secondary) day-blocked CV, agent propensities | best rec (rec) | | — |
| P3 ε_S ∈ [−0.2, 0.5] | ε_S = 0.25 [0.20, 0.31]; B̂ = 0.54 senders addressed per talk | ε_S ≈ 1 (no budget) | pass |
| P4 mentions: e^γ ≥ 3, β_M < β_other − 0.3 | e^γ = 1.1; β_other = 0.77 [0.63, 0.84], β_M = 0.63 [0.58, 0.67] (1041 mention units) | β_M = β_other | fail |
| P10 invisible ≤ 1.5× non-pending, ≤ ½ pending | invisible 0.144 (n = 529), non-pending 0.035, pending (same talks) 0.160 | | fail |
| P6 room size (same days) | k̄ ratio large/small 3.62, p̄ ratio small/large 2.05, S ratio 0.73; room log-effect 0.95 [0.87, 1.04] without k → -0.14 [-0.19, -0.09] with k (3 days) | room effect survives k | fail |
| P11 content-reply excess slope ≈ −β̂ (secondary) | overall excess 0.206; log-log slope -0.22 | slope 0 | fail |

## Round 1b (improved data, 2026-10-04)
*Re-run on the DQ1 context ledger (`scheme/build_ledger.py`: pending sets = ledger items received since the previous talk call, i.e. `k_since_talk`; talk turns = ledger talk calls; first talk call of the day excluded) and scored two ways on the same units: the pre-registered mention response and the DQ2 reply response (the talk's `reply_pairs` parent is one of the sender's pending messages). `analysis/fit_periods.py --dir data/processed/H18-attention-dilution/r1b --resp resp|resp_reply`; data `data/processed/H18-attention-dilution/r1b/G35/fits_mention.json`, `fits_reply.json`. Day bootstrap B = 100 (#51: 40). Predictions and the verdict rule unchanged.*

| Statistic | Round 1 (call-start rule, mentions) | Round 1b, ledger k, mentions | Round 1b, ledger k, reply parent |
| --- | --- | --- | --- |
| scored units (response rate) | 5568 (0.161) | 5791 (0.166) | 5791 (0.131) |
| β̂ [95% CI] | 0.75 [0.63, 0.82] | 0.77 [0.69, 0.82] | 0.97 [0.85, 1.06] |
| CV winner (effective) | rec | rec | rec |
| ε_S | 0.25 | 0.23 | 0.00 |
| β̂_D2 (timer wakes, 300 s) | underpowered | underpowered | underpowered |
| placebo (mention rates) | invisible 0.144 (n 529) · pending same talks 0.160 · non-pending 0.035 | invisible 0.047 (n 213) · pending same talks 0.182 · non-pending 0.036 | — (a reply parent must be visible) |
| verdict | mixed | **mixed** | mixed |

*Reading the reply column:* a talk message has at most one reply parent, and DQ2 labelled mostly the top-ranked candidate, so the reply response allocates one reply among the pending senders; its exponent is ≈ 1 minus the elasticity of "replies to someone pending" in k, a budget built into the measurement. It is reported, but the mention column carries the pre-registered test.

**Verdict (1b): mixed** (round 1: mixed).

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 1 | within-day-block CV: best rec; inv − const Δℓ CI lower bound 0.0117 |
| H comparative | 0 | budget vs. recency: inv − rec Δℓ -0.0121 |
| G ground truth | 0 | invisible-message placebo |

## Notes
- 2026-10-03: card created with the prediction, before any H18 real-data run.
- 2026-10-03: results filled by `write_period_cards.py results` from `fits.json` (run time 29.5 s).
