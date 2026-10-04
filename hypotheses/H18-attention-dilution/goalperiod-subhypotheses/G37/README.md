# H18 × G37: Pick your own goal! (2026-03-30 → 2026-04-02)

**Verdict:** mixed
**Verdict (1b):** mixed (round 1b, 2026-10-04: ledger k, mention response, pre-registered rule; on reply labels: supported; round-1 verdict kept above)
**Role:** exploratory
**Period:** regime III · mode F · N ≈ 13 · #best / #rest. Splits inside the period: none.

## Why this period
First regime-III week, free mode, two rooms; short (3 days).

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
*Run 2026-10-03 (`analysis/fit_periods.py --period G37`); data in `data/processed/H18-attention-dilution/G37/` (`fits.json`). Figure: `figures/curves.pdf`.*

Sample: 3 days, 10 recipients, 665 talk turns (489 with k ≥ 1), 937 scored (talk, sender) units, 368 addressed (rate 0.393). k: median 2, mean 5.0, q90 12; mean room size 6.9.

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| P1 β̂ > 0, CI excl. 0 (expect 0.5–1.2) | β̂ = 0.75 [0.52, 0.98] | M_const: β = 0 | pass |
| P2 budget beats const and recency (within-day-block CV) | best rec (effective: rec; k̂₀ = 1.36, ρ̂ = 0.68); Δℓ/unit inv − const 0.0710 [0.0040, 0.1008], inv − rec -0.0289 [-0.0438, -0.0214] | M_const, M_rec | fail |
| (secondary) day-blocked CV, agent propensities | best rec (rec) | | — |
| P3 ε_S ∈ [−0.2, 0.5] | ε_S = 0.19 [0.06, 0.35]; B̂ = 0.76 senders addressed per talk | ε_S ≈ 1 (no budget) | pass |
| P4 mentions: e^γ ≥ 3, β_M < β_other − 0.3 | e^γ = 2.1; β_other = 0.80 [0.50, 0.90], β_M = 0.62 [0.54, 1.33] (396 mention units) | β_M = β_other | fail |
| P10 invisible ≤ 1.5× non-pending, ≤ ½ pending | invisible 0.313 (n = 83), non-pending 0.041, pending (same talks) 0.490 | | fail |
| P5 D2 β̂ > 0, within ±0.4 of D1 | β̂_D2 = 0.79 [0.71, 0.86] (301 units, 47 resp.; wakes talking within 300 s: 0.42); 60 s: 0.78, stint: 0.75 | reactive-constant agents: ≈ 0 | pass |
| P6 room size (same days) | k̄ ratio large/small 1.82, p̄ ratio small/large 1.38, S ratio 0.76; room log-effect 0.64 [0.08, 1.19] without k → 0.06 [-0.30, 0.73] with k (3 days) | room effect survives k | pass |
| P11 content-reply excess slope ≈ −β̂ (secondary) | overall excess 0.354; log-log slope -0.20 | slope 0 | fail |

## Round 1b (improved data, 2026-10-04)
*Re-run on the DQ1 context ledger (`scheme/build_ledger.py`: pending sets = ledger items received since the previous talk call, i.e. `k_since_talk`; talk turns = ledger talk calls; first talk call of the day excluded) and scored two ways on the same units: the pre-registered mention response and the DQ2 reply response (the talk's `reply_pairs` parent is one of the sender's pending messages). `analysis/fit_periods.py --dir data/processed/H18-attention-dilution/r1b --resp resp|resp_reply`; data `data/processed/H18-attention-dilution/r1b/G37/fits_mention.json`, `fits_reply.json`. Day bootstrap B = 100 (#51: 40). Predictions and the verdict rule unchanged.*

| Statistic | Round 1 (call-start rule, mentions) | Round 1b, ledger k, mentions | Round 1b, ledger k, reply parent |
| --- | --- | --- | --- |
| scored units (response rate) | 937 (0.393) | 961 (0.406) | 961 (0.368) |
| β̂ [95% CI] | 0.75 [0.52, 0.98] | 0.72 [0.53, 0.91] | 1.05 [1.00, 1.19] |
| CV winner (effective) | rec | rec | inv |
| ε_S | 0.19 | 0.21 | -0.08 |
| β̂_D2 (timer wakes, 300 s) | 0.79 [0.71, 0.86] (301 units) | 0.77 [0.70, 1.02] (276 units) | 1.07 [0.89, 1.41] (276 units) |
| placebo (mention rates) | invisible 0.313 (n 83) · pending same talks 0.490 · non-pending 0.041 | invisible 0.118 (n 34) · pending same talks 0.467 · non-pending 0.042 | — (a reply parent must be visible) |
| verdict | mixed | **mixed** | supported |

*Reading the reply column:* a talk message has at most one reply parent, and DQ2 labelled mostly the top-ranked candidate, so the reply response allocates one reply among the pending senders; its exponent is ≈ 1 minus the elasticity of "replies to someone pending" in k, a budget built into the measurement. It is reported, but the mention column carries the pre-registered test.

**Verdict (1b): mixed** (round 1: mixed).

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 1 | within-day-block CV: best rec; inv − const Δℓ CI lower bound 0.0040 |
| H comparative | 0 | budget vs. recency: inv − rec Δℓ -0.0289 |
| B assumptions (timing) | 1 | D2 consistent (β̂_D2 0.79) |
| G ground truth | 0 | invisible-message placebo |

## Notes
- 2026-10-03: card created with the prediction, before any H18 real-data run.
- 2026-10-03: results filled by `write_period_cards.py results` from `fits.json` (run time 13.9 s).
