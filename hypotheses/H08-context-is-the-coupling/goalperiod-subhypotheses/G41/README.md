# H08 × G41: Perform novel research! (2026-05-11 → 2026-05-15)

**Verdict:** supported
**Role:** exploratory
**Period:** regime III · mode I · N ≈ 15 · #best / #rest · 5 non-holdout days.

## Why this period
Enough isolated nudges for a per-period kernel (C8); two rooms, so other-room messages are an invisible placebo (C9-V3); perma-computer-use: consolidations every ≤ 41 turns (NE41 erasures, C3) and token accounting (C2).

## Prediction
*Written 2026-10-04 (~02:40 UTC), before running on this period (and before any real-data run of H08). Applies the card's round-1 predictions and amendments A1–A6 (written after the synthetic validation, before real data).*

- **C9-V1/V2 (visibility discontinuity, primary for every period):** among (message, recipient) pairs whose o = 0 turn is in flight, talking and addressing the sender jump at the read-out turn: D_talk = G_talk(1) − G_talk(0) > 0 and D_addr > 0, each with the day-bootstrap 95% CI excluding 0. G_addr(0) > 0 (contaminated floor, H18) but below ½ G_addr(1). A6: pre = G(0) − G(−1) ≈ 0.
- **C9-V4:** G_talk(2) < G_talk(1) (the response sits on the first visible turn).
- **C9-V3:** messages from the room the recipient is not in: |D_other| < ⅓ of the own-room D, CI including 0.
- **C9-V5:** median read-out delay of in-flight (active) recipients 10–40 s.
- **C8-P1 (HH92, zero-parameter kernel):** nudge → target kernel (H04's design, this period only): the 95% CI of Φ(1,5)_measured − Φ(1,5)_predicted (headroom-weighted read-out CDF F_hr) overlaps [−0.3, +0.1].
- **C8-P2:** F_hr(observed read-out) reaches half its 45-min value between 3 and 15 min.
- **C8-P3:** in 100 day-split CVs the best context-family model beats the best immediate, constant-delay and Hawkes models each in ≥ 60% of splits, with median SSE ≤ 1.1 × the gamma ceiling.
- **C8-P4:** the renewal prediction (no kick information) has a faster onset than the observed-read-out one (Φ_ren(1,5) > Φ_obs(1,5)).
- **C2-I1/I2:** within agent-days, log uncached tokens rise with log(1 + new room messages) (b > 0, CI excluding 0) but messages explain little (partial R² < 0.05); P(talk | ≥ 1 new message) / P(talk | 0) > 1.2; ρ(uncached, call latency) > 0.
- **C3-E1/E2 (NE41):** where ≥ 300 erased units, addressing an old sender whose message was read before a forced consolidation falls relative to old senders read after it (β_F < 0, CI excluding 0; relative drop ≥ 30%); β_V within ±50% of β_F. **E3:** voluntary segments shorter when inflow per turn is higher (ρ < 0).
- **C10-L1 (HH91 as stated):** backlog k per talk turn rises with session hour (ρ > 0; within-agent-day slope CI > 0).

**Verdict rule (fixed now).** Tests: T_C9 = V1 and V2 both pass; T_C8 (powered periods) = P1 band and P3 both hold → pass, Φ outside the band or a rival family winning ≥ 60% → fail, else inconclusive; T_C3 (≥ 300 forced-erased units) = β_F < 0 with CI excluding 0 → pass, β_F > 0 with CI excluding 0 → fail, else inconclusive; T_C1 = recall ≥ 0.9 and (two rooms) other-room coverage ≤ 5% → pass, recall < 0.7 or other-room coverage > 20% → fail. **supported** = T_C9 passes and no other test fails; **failed** = T_C9 fails; **mixed** = T_C9 passes and another test fails. C2, C10 and the secondary items are reported but do not set the verdict.

## Result
*Run 2026-10-04 (`analysis/visibility.py`, `kernels.py`, `cc_exposure.py`, `inflow.py`, `erasure.py`, `sessions.py`). Data: `data/processed/H08-context-is-the-coupling/G41/` (c9/c8/c2/c3/c10.json). Figure: `figures/c9_offsets.pdf`. pp = percentage points; brackets are day-bootstrap 95% CIs.*

Read-out pairs: 18563 own-room (+ 12621 other-room); in-flight share 93%, wake share 7%.

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| C9-V1 talk jump D_talk (pp) | +1.43 [+0.75, +2.13] | pseudo-message null | pass |
| C9-V2 addressing jump D_addr (pp) | +1.02 [+0.64, +1.32]; floor G_addr(0) +0.18, G_addr(1) +1.20 | | pass |
| A6 pre = G(0) − G(−1), talk / addr (pp) | -0.88 [-1.60, -0.13] / -0.49 [-0.64, -0.34] | ≈ 0 (common cause is flat) | not ≈ 0 |
| C9-V4 G_talk(2) < G_talk(1) | +1.45 vs +1.64 | | pass |
| *post hoc:* recipient did not talk at o = −2, −1 | D_talk +1.04 [+0.03, +2.23]; D_addr +0.85 [+0.39, +1.30]; G_addr(0) +0.17 | | (descriptive) |
| C9-V3 other-room placebo D_talk / D_addr (pp) | +0.26 [-0.28, +0.87] / -0.03 [-0.05, +0.00] | ≈ 0 | pass |
| C9-V5 median read-out delay, active recipients | 49 s (IQR 23–100) | 10–40 s | fail |
| C8 nudge → target, cells | 14; A30 3.16 [-2.89, 7.59]; read-out median 64 s; paused at kick 29% | | n/a (< 30 cells) |
| C8-P1 Φ(1,5) measured vs F_hr | 0.31 [-0.80, 2.99] vs 0.60 [0.31, 0.81]; diff -0.29 [-1.47, 2.29] | band [−0.3, +0.1] | descriptive |
| C8-P2 t½ of F_hr | 3.0 min | 3–15 min | pass |
| C8-P4 Φ_ren(1,5) > Φ_obs(1,5) | 0.69 vs 0.60 | | pass |
| C8-P3 day-split CV (100 splits) | best: ctx 0.39, gamma 0.31, imm_hr 0.30; ctx beats imm 0.00, delay 0.00, Hawkes 0.00; gamma/ctx SSE 1.04 | ≥ 0.60 each | fail |
| C2-I1 elasticity b (raw) / partial R² | -0.38 [-0.44, -0.27] / 0.012 [0.006, 0.018] | b > 0, R² < 0.05 | fail |
| *post hoc:* b with previous-action control | 0.35 [0.10, 0.51] | | (descriptive) |
| C2-I2 talk ratio / ρ(uncached, latency) | 1.36 [1.16, 1.61] / 0.16 [0.14, 0.19] | > 1.2 / > 0 | pass |
| C3-E1 β_F (forced erasure, pp) / relative | -1.27 [-4.60, +2.25] / -0.07 [-0.26, 0.13] (CF units 1825) | < 0; rel ≤ −0.30 | inconclusive |
| C3-E2 β_V (pp) | -1.21 [-4.65, +2.17] | within ±50% of β_F | pass |
| C3-E3 ρ(voluntary segment length, inflow per turn) | 0.06 [-0.10, 0.19] (n = 96) | < 0 | fail |
| C10-L1 slope of log(1 + k) per session hour / ρ | 0.032 [-0.004, 0.058] / +0.064 | > 0 | fail |

**Tests:** T_C9 = pass, T_C8 = n/a, T_C3 = inconclusive → **supported**.

## Scorecard (period-specific axes)
| Axis | This period |
| --- | --- |
| C adequacy | C9 discontinuity vs pseudo-message null: pass |
| E interventional | NE41 forced erasure (exogenous timing): inconclusive |
| D unfitted | read-out turn and the zero-parameter kernel come from turn timing only |

## Notes
- Card: [`../../README.md`](../../README.md). Data: `data/processed/H08-context-is-the-coupling/G41/`.
