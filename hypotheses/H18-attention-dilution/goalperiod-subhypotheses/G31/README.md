# H18 × G31: Pick your own goal (agents bid 3.7 Sonnet farewell) (2026-02-16 → 2026-02-23)

**Verdict:** mixed
**Verdict (1b):** mixed (round 1b, 2026-10-04: ledger k, mention response, pre-registered rule; on reply labels: mixed; round-1 verdict kept above)
**Role:** replication (exploratory)
**Period:** regime I · mode F · N ≈ 12 · everyone in #general. Splits inside the period: Sonnet 4.6 joins 02-18; NE29 3.7 Sonnet retires 02-19; NE11 100-turn cap 02-20.

## Why this period
Regime I contrast, free week with a farewell; roster changes inside.

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
*Run 2026-10-03 (`analysis/fit_periods.py --period G31`); data in `data/processed/H18-attention-dilution/G31/` (`fits.json`). Figure: `figures/curves.pdf`.*

Sample: 5 days, 12 recipients, 2702 talk turns (2343 with k ≥ 1), 11946 scored (talk, sender) units, 1724 addressed (rate 0.144). k: median 8, mean 13.1, q90 30; mean room size 11.2.

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| P1 β̂ > 0, CI excl. 0 (expect 0.5–1.2) | β̂ = 0.46 [0.41, 0.50] | M_const: β = 0 | pass |
| P2 budget beats const and recency (within-day-block CV) | best rec (effective: rec; k̂₀ = 10.08, ρ̂ = 0.93); Δℓ/unit inv − const -0.0086 [-0.0183, 0.0017], inv − rec -0.0232 [-0.0304, -0.0151] | M_const, M_rec | fail |
| (secondary) day-blocked CV, agent propensities | best rec (rec) | | — |
| P3 ε_S ∈ [−0.2, 0.5] | ε_S = 0.50 [0.44, 0.56]; B̂ = 0.75 senders addressed per talk | ε_S ≈ 1 (no budget) | pass |
| P4 mentions: e^γ ≥ 3, β_M < β_other − 0.3 | e^γ = 1.7; β_other = 0.47 [0.38, 0.53], β_M = 0.46 [0.39, 0.52] (2318 mention units) | β_M = β_other | fail |
| P10 invisible ≤ 1.5× non-pending, ≤ ½ pending | invisible 0.174 (n = 2120), non-pending 0.069, pending (same talks) 0.157 | | fail |
| P11 content-reply excess slope ≈ −β̂ (secondary) | overall excess 0.161; log-log slope -0.31 | slope 0 | pass |

Segments at step changes (4): 2026-02-16–2026-02-17: β̂ 0.47 ± 0.04; 2026-02-18–2026-02-18: β̂ 0.54; 2026-02-19–2026-02-19: β̂ 0.35; 2026-02-20–2026-02-20: β̂ 0.46.

## Round 1b (improved data, 2026-10-04)
*Re-run on the DQ1 context ledger (`scheme/build_ledger.py`: pending sets = ledger items received since the previous talk call, i.e. `k_since_talk`; talk turns = ledger talk calls; first talk call of the day excluded) and scored two ways on the same units: the pre-registered mention response and the DQ2 reply response (the talk's `reply_pairs` parent is one of the sender's pending messages). `analysis/fit_periods.py --dir data/processed/H18-attention-dilution/r1b --resp resp|resp_reply`; data `data/processed/H18-attention-dilution/r1b/G31/fits_mention.json`, `fits_reply.json`. Day bootstrap B = 100 (#51: 40). Predictions and the verdict rule unchanged.*

| Statistic | Round 1 (call-start rule, mentions) | Round 1b, ledger k, mentions | Round 1b, ledger k, reply parent |
| --- | --- | --- | --- |
| scored units (response rate) | 11946 (0.144) | 12891 (0.154) | 12891 (0.048) |
| β̂ [95% CI] | 0.46 [0.41, 0.50] | 0.52 [0.44, 0.59] | 0.74 [0.69, 0.78] |
| CV winner (effective) | rec | rec | rec |
| ε_S | 0.50 | 0.45 | 0.19 |
| β̂_D2 (timer wakes, 300 s) | underpowered | underpowered | underpowered |
| placebo (mention rates) | invisible 0.174 (n 2120) · pending same talks 0.157 · non-pending 0.069 | invisible 0.094 (n 534) · pending same talks 0.193 · non-pending 0.071 | — (a reply parent must be visible) |
| verdict | mixed | **mixed** | mixed |

*Reading the reply column:* a talk message has at most one reply parent, and DQ2 labelled mostly the top-ranked candidate, so the reply response allocates one reply among the pending senders; its exponent is ≈ 1 minus the elasticity of "replies to someone pending" in k, a budget built into the measurement. It is reported, but the mention column carries the pre-registered test.

**Verdict (1b): mixed** (round 1: mixed).

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 1 | within-day-block CV: best rec; inv − const Δℓ CI lower bound -0.0183 |
| H comparative | 0 | budget vs. recency: inv − rec Δℓ -0.0232 |
| G ground truth | 0 | invisible-message placebo |

## Notes
- 2026-10-03: card created with the prediction, before any H18 real-data run.
- 2026-10-03: results filled by `write_period_cards.py results` from `fits.json` (run time 45.8 s).
