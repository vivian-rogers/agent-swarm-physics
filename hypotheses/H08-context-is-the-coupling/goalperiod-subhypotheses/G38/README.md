# H08 × G38: Choose a charity and raise as much money as you can for it (2026-04-02 → 2026-04-24)

**Verdict:** supported
**Verdict (1b):** supported (round 1b, 2026-10-04, context-ledger read-out; C9 talk and addressing jumps both pass on the ledger; round-1 verdict kept above)
**Role:** replication (exploratory)
**Period:** regime III · mode C · N ≈ 12 · #best / #rest · 17 non-holdout days.

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
- **C10-L1 (HH91 as stated):** backlog k per talk turn rises with session hour (ρ > 0; within-agent-day slope CI > 0). **L2:** Hawkes n̂ is higher in the second half of the day (Δn̂ > 0, CI excluding 0).

**Verdict rule (fixed now).** Tests: T_C9 = V1 and V2 both pass; T_C8 (powered periods) = P1 band and P3 both hold → pass, Φ outside the band or a rival family winning ≥ 60% → fail, else inconclusive; T_C3 (≥ 300 forced-erased units) = β_F < 0 with CI excluding 0 → pass, β_F > 0 with CI excluding 0 → fail, else inconclusive; T_C1 = recall ≥ 0.9 and (two rooms) other-room coverage ≤ 5% → pass, recall < 0.7 or other-room coverage > 20% → fail. **supported** = T_C9 passes and no other test fails; **failed** = T_C9 fails; **mixed** = T_C9 passes and another test fails. C2, C10 and the secondary items are reported but do not set the verdict.

## Result
*Run 2026-10-04 (`analysis/visibility.py`, `kernels.py`, `cc_exposure.py`, `inflow.py`, `erasure.py`, `sessions.py`). Data: `data/processed/H08-context-is-the-coupling/G38/` (c9/c8/c2/c3/c10.json). Figure: `figures/c9_offsets.pdf`. pp = percentage points; brackets are day-bootstrap 95% CIs.*

Read-out pairs: 25198 own-room (+ 28649 other-room); in-flight share 91%, wake share 7%.

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| C9-V1 talk jump D_talk (pp) | +0.85 [+0.29, +1.46] | pseudo-message null | pass |
| C9-V2 addressing jump D_addr (pp) | +0.88 [+0.62, +1.11]; floor G_addr(0) +0.06, G_addr(1) +0.94 | | pass |
| A6 pre = G(0) − G(−1), talk / addr (pp) | -0.68 [-1.10, -0.24] / -0.31 [-0.47, -0.12] | ≈ 0 (common cause is flat) | not ≈ 0 |
| C9-V4 G_talk(2) < G_talk(1) | +0.47 vs +1.27 | | pass |
| *post hoc:* recipient did not talk at o = −2, −1 | D_talk +0.63 [+0.02, +1.18]; D_addr +0.83 [+0.58, +1.06]; G_addr(0) +0.04 | | (descriptive) |
| C9-V3 other-room placebo D_talk / D_addr (pp) | +0.06 [-0.35, +0.46] / +0.00 [+0.00, +0.01] | ≈ 0 | pass |
| C9-V5 median read-out delay, active recipients | 35 s (IQR 20–93) | 10–40 s | pass |
| C8 nudge → target, cells | 26; A30 -1.33 [-3.43, 0.10]; read-out median 64 s; paused at kick 46% | | n/a (< 30 cells) |
| C8-P1 Φ(1,5) measured vs F_hr | 5.20 [-28.28, 40.14] vs 0.45 [0.27, 0.59]; diff 4.75 [-28.78, 39.67] | band [−0.3, +0.1] | descriptive |
| C8-P2 t½ of F_hr | 4.0 min | 3–15 min | pass |
| C8-P4 Φ_ren(1,5) > Φ_obs(1,5) | 0.72 vs 0.45 | | pass |
| C8-P3 day-split CV (100 splits) | best: imm 0.42, hawkes 0.27, ctx 0.12; ctx beats imm 0.00, delay 0.00, Hawkes 0.00; gamma/ctx SSE 1.00 | ≥ 0.60 each | fail |
| C2-I1 elasticity b (raw) / partial R² | -0.90 [-0.98, -0.84] / 0.039 [0.033, 0.045] | b > 0, R² < 0.05 | fail |
| *post hoc:* b with previous-action control | 0.22 [0.14, 0.29] | | (descriptive) |
| C2-I2 talk ratio / ρ(uncached, latency) | 1.33 [1.19, 1.47] / 0.12 [0.10, 0.13] | > 1.2 / > 0 | pass |
| C3-E1 β_F (forced erasure, pp) / relative | -0.98 [-2.39, +1.22] / -0.07 [-0.16, 0.08] (CF units 3028) | < 0; rel ≤ −0.30 | inconclusive |
| C3-E2 β_V (pp) | +3.33 [+1.44, +5.43] | within ±50% of β_F | fail |
| C3-E3 ρ(voluntary segment length, inflow per turn) | 0.02 [-0.08, 0.14] (n = 214) | < 0 | fail |
| C10-L1 slope of log(1 + k) per session hour / ρ | 0.024 [0.009, 0.039] / +0.028 | > 0 | pass |
| C10-L2 Hawkes n̂ second − first half | 0.142 − 0.190 = -0.048 [-0.180, 0.092] | > 0 | fail |

**Tests:** T_C9 = pass, T_C8 = n/a, T_C3 = inconclusive → **supported**.

## Round 1b (improved data, 2026-10-04)
*Re-run on the DQ1 context ledger (`scheme/build_turns_ledger.py`, `analysis/visibility_ledger.py`, `analysis/erasure_ledger.py`): turns are ledger calls, o = 1 is the call that received the message (exact by construction), in-flight = the previous call's first record came after the message. Responses: mention (the pre-registered measure), the DQ2 reply-parent author, and the content cosine of the talk with the message (non-mention). Predictions and the verdict rule unchanged. Data: `data/processed/H08-context-is-the-coupling/r1b/G38/` (`c9.json`, `c3.json`). D in percentage points (cosine ×100), day-bootstrap 95% CIs.*

| Statistic | Round 1 (H08 call-start rule) | Round 1b (ledger) | Note |
| --- | --- | --- | --- |
| D_talk | +0.85 [+0.29, +1.46] | +1.60 [+0.93, +2.22] | pre-registered clause |
| D_addr (mention) | +0.88 [+0.62, +1.11] | +1.14 [+0.80, +1.41] | pre-registered clause |
| D_addr, clean recipients (post hoc) | +0.83 [+0.58, +1.06] | +1.03 [+0.70, +1.31] | no talk at o = −2, −1 |
| D, reply author (new) | — | +1.69 [+1.39, +1.95] | DQ2 `reply_pairs.parent` |
| D, content cosine (new, ×100) | — | +2.00 [+0.14, +3.69] | non-mention response |
| other-room placebo D_addr | — | +0.01 [+0.00, +0.02] | two-room periods only |
| read-out delay of in-flight recipients, median | — | first record 29 s; context assembly 11 s | C9-V5 band 10–40 s |
| C3 / NE41 β_F, forced erasure (pp) | -0.98 [-2.39, +1.22] (mention, H15 catalog) | mention +0.50 [-0.76, +2.12]; **reply author -1.29 [-2.69, +0.10]** (relative -9% [-18, +1]; 4106 forced-erased units) | ledger `reset_forced` |

**Verdict (1b): supported** (round 1: supported).

## Scorecard (period-specific axes)
| Axis | This period |
| --- | --- |
| C adequacy | C9 discontinuity vs pseudo-message null: pass |
| E interventional | NE41 forced erasure (exogenous timing): inconclusive |
| D unfitted | read-out turn and the zero-parameter kernel come from turn timing only |

## Notes
- Card: [`../../README.md`](../../README.md). Data: `data/processed/H08-context-is-the-coupling/G38/`.
