# H18 × G36: Interact with other AI agents outside the Village! (2026-03-23 → 2026-03-30)

**Verdict:** supported
**Verdict (1b):** supported (round 1b, 2026-10-04: ledger k, mention response, pre-registered rule; on reply labels: mixed; round-1 verdict kept above)
**Role:** replication (exploratory)
**Period:** regime II/III · mode C · N ≈ 13 · #best / #rest. Splits inside the period: F perma-computer-use 03-24 (NE14); NE16 03-26.

## Why this period
Two rooms, and the regime II → III boundary (perma-computer-use) inside: first timer-PAUSE days.

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
*Run 2026-10-03 (`analysis/fit_periods.py --period G36`); data in `data/processed/H18-attention-dilution/G36/` (`fits.json`). Figure: `figures/curves.pdf`.*

Sample: 5 days, 11 recipients, 1520 talk turns (1149 with k ≥ 1), 2842 scored (talk, sender) units, 744 addressed (rate 0.262). k: median 3, mean 5.7, q90 12; mean room size 6.3.

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| P1 β̂ > 0, CI excl. 0 (expect 0.5–1.2) | β̂ = 0.78 [0.74, 0.82] | M_const: β = 0 | pass |
| P2 budget beats const and recency (within-day-block CV) | best sat (effective: sat~inv; k̂₀ = 1.01, ρ̂ = 0.77); Δℓ/unit inv − const 0.0668 [0.0371, 0.1206], inv − rec 0.0017 [-0.0063, 0.0143] | M_const, M_rec | pass |
| (secondary) day-blocked CV, agent propensities | best sat (sat~inv) | | — |
| P3 ε_S ∈ [−0.2, 0.5] | ε_S = 0.22 [0.19, 0.24]; B̂ = 0.65 senders addressed per talk | ε_S ≈ 1 (no budget) | pass |
| P4 mentions: e^γ ≥ 3, β_M < β_other − 0.3 | e^γ = 2.2; β_other = 0.78 [0.71, 0.85], β_M = 0.80 [0.65, 0.99] (857 mention units) | β_M = β_other | fail |
| P10 invisible ≤ 1.5× non-pending, ≤ ½ pending | invisible 0.153 (n = 157), non-pending 0.054, pending (same talks) 0.288 | | fail |
| P5 D2 timer wakes (300 s) | 40 units, 8 responses | | underpowered |
| P6 room size (same days) | k̄ ratio large/small 2.00, p̄ ratio small/large 0.99, S ratio 0.63; room log-effect -0.13 [-1.09, 0.48] without k → -0.62 [-1.25, -0.18] with k (5 days) | room effect survives k | fail |
| P11 content-reply excess slope ≈ −β̂ (secondary) | overall excess 0.220; log-log slope -0.23 | slope 0 | fail |

Segments at step changes (3): 2026-03-23–2026-03-23: β̂ 0.77; 2026-03-24–2026-03-25: β̂ 0.73 ± 0.01; 2026-03-26–2026-03-27: β̂ 0.83 ± 0.01. Random-effects pooled 0.78 ± 0.05, I² = 0.97.

## Round 1b (improved data, 2026-10-04)
*Re-run on the DQ1 context ledger (`scheme/build_ledger.py`: pending sets = ledger items received since the previous talk call, i.e. `k_since_talk`; talk turns = ledger talk calls; first talk call of the day excluded) and scored two ways on the same units: the pre-registered mention response and the DQ2 reply response (the talk's `reply_pairs` parent is one of the sender's pending messages). `analysis/fit_periods.py --dir data/processed/H18-attention-dilution/r1b --resp resp|resp_reply`; data `data/processed/H18-attention-dilution/r1b/G36/fits_mention.json`, `fits_reply.json`. Day bootstrap B = 100 (#51: 40). Predictions and the verdict rule unchanged.*

| Statistic | Round 1 (call-start rule, mentions) | Round 1b, ledger k, mentions | Round 1b, ledger k, reply parent |
| --- | --- | --- | --- |
| scored units (response rate) | 2842 (0.262) | 2904 (0.262) | 2904 (0.175) |
| β̂ [95% CI] | 0.78 [0.74, 0.82] | 0.80 [0.76, 0.84] | 1.08 [0.95, 1.23] |
| CV winner (effective) | sat~inv | sat~inv | rec |
| ε_S | 0.22 | 0.21 | -0.07 |
| β̂_D2 (timer wakes, 300 s) | underpowered | underpowered | underpowered |
| placebo (mention rates) | invisible 0.153 (n 157) · pending same talks 0.288 · non-pending 0.054 | invisible 0.137 (n 95) · pending same talks 0.293 · non-pending 0.055 | — (a reply parent must be visible) |
| verdict | supported | **supported** | mixed |

*Reading the reply column:* a talk message has at most one reply parent, and DQ2 labelled mostly the top-ranked candidate, so the reply response allocates one reply among the pending senders; its exponent is ≈ 1 minus the elasticity of "replies to someone pending" in k, a budget built into the measurement. It is reported, but the mention column carries the pre-registered test.

**Verdict (1b): supported** (round 1: supported).

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 2 | within-day-block CV: best sat~inv; inv − const Δℓ CI lower bound 0.0371 |
| H comparative | 1 | budget vs. recency: inv − rec Δℓ 0.0017 |
| B assumptions (timing) | 0 | D2 underpowered (β̂_D2 —) |
| G ground truth | 0 | invisible-message placebo |

## Notes
- 2026-10-03: card created with the prediction, before any H18 real-data run.
- 2026-10-03: results filled by `write_period_cards.py results` from `fits.json` (run time 21.3 s).
