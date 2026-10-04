# H18 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 2026-09-07)

**Verdict:** mixed
**Verdict (1b):** mixed (round 1b, 2026-10-04: ledger k, mention response, pre-registered rule; on reply labels: mixed; round-1 verdict kept above)
**Role:** native (round 1b: N sweep at fixed goal; also carries the replication row; round 1 was exploratory)
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

## Round 1b (improved data, 2026-10-04)
*Re-run on the DQ1 context ledger (`scheme/build_ledger.py`: pending sets = ledger items received since the previous talk call, i.e. `k_since_talk`; talk turns = ledger talk calls; first talk call of the day excluded) and scored two ways on the same units: the pre-registered mention response and the DQ2 reply response (the talk's `reply_pairs` parent is one of the sender's pending messages). `analysis/fit_periods.py --dir data/processed/H18-attention-dilution/r1b --resp resp|resp_reply`; data `data/processed/H18-attention-dilution/r1b/G51/fits_mention.json`, `fits_reply.json`. Day bootstrap B = 100 (#51: 40). Predictions and the verdict rule unchanged.*

| Statistic | Round 1 (call-start rule, mentions) | Round 1b, ledger k, mentions | Round 1b, ledger k, reply parent |
| --- | --- | --- | --- |
| scored units (response rate) | 195913 (0.102) | 197539 (0.105) | 197539 (0.077) |
| β̂ [95% CI] | 0.61 [0.58, 0.63] | 0.61 [0.58, 0.62] | 0.72 [0.69, 0.75] |
| CV winner (effective) | sat | sat | rec |
| ε_S | 0.21 | 0.20 | 0.04 |
| β̂_D2 (timer wakes, 300 s) | 0.50 [0.45, 0.56] (129567 units) | 0.45 [0.41, 0.50] (107411 units) | 0.62 [0.55, 0.69] (107411 units) |
| placebo (mention rates) | invisible 0.146 (n 11870) · pending same talks 0.134 · non-pending 0.026 | invisible 0.096 (n 5672) · pending same talks 0.153 · non-pending 0.026 | — (a reply parent must be visible) |
| verdict | mixed | **mixed** | mixed |

*Reading the reply column:* a talk message has at most one reply parent, and DQ2 labelled mostly the top-ranked candidate, so the reply response allocates one reply among the pending senders; its exponent is ≈ 1 minus the elasticity of "replies to someone pending" in k, a budget built into the measurement. It is reported, but the mention column carries the pre-registered test.

**Verdict (1b): mixed** (round 1: mixed).

## Scorecard (period-specific axes)
| Axis | Score | Evidence |
| --- | --- | --- |
| C adequacy | 1 | within-day-block CV: best sat; inv − const Δℓ CI lower bound 0.0094 |
| H comparative | 0 | budget vs. recency: inv − rec Δℓ -0.0088 |
| B assumptions (timing) | 1 | D2 consistent (β̂_D2 0.50) |
| G ground truth | 0 | invisible-message placebo |

## Round 1b prediction (native: the N sweep)
*Written 2026-10-04 06:37 UTC, before the round-1b run on this period.* #51 is the only period where N changes (21 → 29 on non-holdout days, in dated roster steps) at a fixed goal, room and hours (DQ9). Segments = the shared `period_units` units 51a–51l (non-holdout). Response = reply parent (`reply_pairs`, message-specific: the talk's parent is one of j's pending messages); k = ledger `k_since_talk`.
- **N1a:** across segments, per-pair reply uptake p̄ falls with mean room size (Spearman ρ < −0.5).
- **N1b:** the per-turn budget B̂ (pending parents per talk turn) does not (|ρ| < 0.3), and CV(B̂) < CV(p̄).
- **N1c:** β̂ (reply) > 0 with CI excluding 0 in ≥ 2/3 of segments with ≥ 1,000 units.
- **Note on the measurement:** a talk message has at most one parent, so B̂ ≤ 1 per message by construction; N1b is therefore partly built in, and N1a is the informative clause.

**Verdict rule (fixed now):** supported if N1a and N1b hold; failed if N1a fails; mixed otherwise.

## Round 1b result (native: the N sweep, 2026-10-04)
*Run `analysis/r1b_native.py` (`data/processed/H18-attention-dilution/r1b/native.json`). Segments = shared `period_units` 51a–51l. Cells: p̄ · B̂ · β̂ day-bootstrap 95% CI (30 refits; the full-sample segment fits are unstable, so only the bootstrap intervals are shown).*

| Unit | days | mean room size | reply parent: p̄ · B̂ · β̂ CI | mention: p̄ · B̂ · β̂ CI |
| --- | --- | --- | --- | --- |
| 51a | 2026-07-06 → 2026-07-08 | 21.0 | 0.074 · 0.45 · [0.63, 0.76] | 0.120 · 0.72 · [0.61, 0.64] |
| 51b | 2026-07-09 → 2026-07-09 | 22.1 | 0.090 · 0.55 · — | 0.119 · 0.72 · — |
| 51c | 2026-07-10 → 2026-07-16 | 24.9 | 0.070 · 0.42 · [0.65, 0.83] | 0.096 · 0.57 · [0.62, 0.70] |
| 51d | 2026-07-17 → 2026-07-23 | 25.9 | 0.073 · 0.48 · [0.65, 0.76] | 0.114 · 0.75 · [0.61, 0.69] |
| 51e | 2026-07-24 → 2026-07-28 | 26.8 | 0.066 · 0.51 · [0.54, 0.68] | 0.096 · 0.73 · [0.47, 0.59] |
| 51f | 2026-07-29 → 2026-08-04 | 27.0 | 0.075 · 0.46 · [0.60, 0.68] | 0.117 · 0.71 · [0.53, 0.61] |
| 51g | 2026-08-05 → 2026-08-21 | 20.6 | 0.102 · 0.50 · [0.77, 0.85] | 0.112 · 0.55 · [0.56, 0.65] |
| 51h | 2026-08-24 → 2026-08-27 | 26.0 | 0.085 · 0.41 · [0.77, 0.85] | 0.112 · 0.55 · [0.64, 0.75] |
| 51i | 2026-08-28 → 2026-08-31 | 27.7 | 0.056 · 0.36 · [0.63, 0.71] | 0.075 · 0.48 · [0.50, 0.66] |
| 51j | 2026-09-01 → 2026-09-02 | 28.6 | 0.048 · 0.31 · [0.87, 0.93] | 0.073 · 0.47 · [0.59, 0.74] |
| 51k | 2026-09-03 → 2026-09-03 | 30.4 | 0.056 · 0.39 · — | 0.091 · 0.64 · — |
| 51l | 2026-09-04 → 2026-09-04 | 31.4 | 0.054 · 0.42 · — | 0.076 · 0.59 · — |

| Prediction | Reply parent (primary) | Mention | Verdict |
| --- | --- | --- | --- |
| N1a: ρ(p̄, room size) < −0.5 | ρ = -0.80 | ρ = -0.73 | pass |
| N1b: \|ρ(B̂, room size)\| < 0.3 and CV(B̂) < CV(p̄) | ρ = -0.64; CV 0.15 vs 0.22 | ρ = -0.28; CV 0.16 vs 0.17 | **fail** on replies (pass on mentions) |
| N1c: β̂ CI > 0 in ≥ 2/3 of segments with ≥ 1,000 units | 75% of 12 | 75% of 12 | pass |

- **Reading:** per-pair uptake falls as the room grows from 21 to 31 agents, with either response. On reply labels the per-turn budget also falls (fewer talk turns reply to anyone pending in larger rooms), so the "conserved budget" half holds only for mentions.

**Verdict (1b, native): mixed** (N1a and N1c hold; N1b fails on the primary response).

## Notes
- 2026-10-03: card created with the prediction, before any H18 real-data run.
- 2026-10-03: results filled by `write_period_cards.py results` from `fits.json` (run time 777.5 s).
