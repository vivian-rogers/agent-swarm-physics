# H08 × G42: Run your own Youtube channel! (2026-05-18 → 2026-05-22)

**Verdict:** supported
**Verdict (1b):** supported (round 1b, 2026-10-04, context-ledger read-out; C9 talk and addressing jumps both pass on the ledger; round-1 verdict kept above)
**Role:** exploratory
**Period:** regime III · mode I · N ≈ 15 · #best / #rest · 5 non-holdout days.

## Why this period
A few nudges (C8 descriptive; pooled within regime); two rooms, so other-room messages are an invisible placebo (C9-V3); perma-computer-use: consolidations every ≤ 41 turns (NE41 erasures, C3) and token accounting (C2).

## Prediction
*Written 2026-10-04 (~02:40 UTC), before running on this period (and before any real-data run of H08). Applies the card's round-1 predictions and amendments A1–A6 (written after the synthetic validation, before real data).*

- **C9-V1/V2 (visibility discontinuity, primary for every period):** among (message, recipient) pairs whose o = 0 turn is in flight, talking and addressing the sender jump at the read-out turn: D_talk = G_talk(1) − G_talk(0) > 0 and D_addr > 0, each with the day-bootstrap 95% CI excluding 0. G_addr(0) > 0 (contaminated floor, H18) but below ½ G_addr(1). A6: pre = G(0) − G(−1) ≈ 0.
- **C9-V4:** G_talk(2) < G_talk(1) (the response sits on the first visible turn).
- **C9-V3:** messages from the room the recipient is not in: |D_other| < ⅓ of the own-room D, CI including 0.
- **C9-V5:** median read-out delay of in-flight (active) recipients 10–40 s.
- **C8:** too few isolated nudges for a per-period test (expected < 30 cells); the per-period kernel is descriptive and enters the pooled regime estimate (exception (d)).
- **C2-I1/I2:** within agent-days, log uncached tokens rise with log(1 + new room messages) (b > 0, CI excluding 0) but messages explain little (partial R² < 0.05); P(talk | ≥ 1 new message) / P(talk | 0) > 1.2; ρ(uncached, call latency) > 0.
- **C3-E1/E2 (NE41):** where ≥ 300 erased units, addressing an old sender whose message was read before a forced consolidation falls relative to old senders read after it (β_F < 0, CI excluding 0; relative drop ≥ 30%); β_V within ±50% of β_F. **E3:** voluntary segments shorter when inflow per turn is higher (ρ < 0).
- **C10-L1 (HH91 as stated):** backlog k per talk turn rises with session hour (ρ > 0; within-agent-day slope CI > 0).

**Verdict rule (fixed now).** Tests: T_C9 = V1 and V2 both pass; T_C8 (powered periods) = P1 band and P3 both hold → pass, Φ outside the band or a rival family winning ≥ 60% → fail, else inconclusive; T_C3 (≥ 300 forced-erased units) = β_F < 0 with CI excluding 0 → pass, β_F > 0 with CI excluding 0 → fail, else inconclusive; T_C1 = recall ≥ 0.9 and (two rooms) other-room coverage ≤ 5% → pass, recall < 0.7 or other-room coverage > 20% → fail. **supported** = T_C9 passes and no other test fails; **failed** = T_C9 fails; **mixed** = T_C9 passes and another test fails. C2, C10 and the secondary items are reported but do not set the verdict.

## Result
*Run 2026-10-04 (`analysis/visibility.py`, `kernels.py`, `cc_exposure.py`, `inflow.py`, `erasure.py`, `sessions.py`). Data: `data/processed/H08-context-is-the-coupling/G42/` (c9/c8/c2/c3/c10.json). Figure: `figures/c9_offsets.pdf`. pp = percentage points; brackets are day-bootstrap 95% CIs.*

Read-out pairs: 10888 own-room (+ 7709 other-room); in-flight share 96%, wake share 2%.

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| C9-V1 talk jump D_talk (pp) | +1.41 [+0.57, +2.03] | pseudo-message null | pass |
| C9-V2 addressing jump D_addr (pp) | +1.57 [+1.02, +2.03]; floor G_addr(0) +0.08, G_addr(1) +1.65 | | pass |
| A6 pre = G(0) − G(−1), talk / addr (pp) | -0.63 [-1.13, -0.19] / -0.26 [-0.58, +0.04] | ≈ 0 (common cause is flat) | not ≈ 0 |
| C9-V4 G_talk(2) < G_talk(1) | +0.37 vs +1.66 | | pass |
| *post hoc:* recipient did not talk at o = −2, −1 | D_talk +1.18 [+0.33, +1.87]; D_addr +1.06 [+0.73, +1.32]; G_addr(0) +0.10 | | (descriptive) |
| C9-V3 other-room placebo D_talk / D_addr (pp) | -0.23 [-0.67, +0.10] / +0.00 [+0.00, +0.00] | ≈ 0 | pass |
| C9-V5 median read-out delay, active recipients | 39 s (IQR 22–91) | 10–40 s | pass |
| C8 nudge → target | 9 isolated cells | | descriptive (pooled) |
| C2-I1 elasticity b (raw) / partial R² | -0.71 [-0.90, -0.60] / 0.029 [0.023, 0.039] | b > 0, R² < 0.05 | fail |
| *post hoc:* b with previous-action control | 0.42 [0.38, 0.48] | | (descriptive) |
| C2-I2 talk ratio / ρ(uncached, latency) | 1.96 [1.67, 2.24] / 0.10 [0.08, 0.12] | > 1.2 / > 0 | pass |
| C3-E1 β_F (forced erasure, pp) / relative | -4.45 [-8.12, -1.63] / -0.22 [-0.41, -0.08] (CF units 1216) | < 0; rel ≤ −0.30 | pass |
| C3-E2 β_V (pp) | -1.79 [-5.05, +0.18] | within ±50% of β_F | fail |
| C3-E3 ρ(voluntary segment length, inflow per turn) | -0.08 [-0.20, 0.08] (n = 106) | < 0 | pass |
| C10-L1 slope of log(1 + k) per session hour / ρ | 0.041 [0.010, 0.081] / +0.060 | > 0 | pass |

**Tests:** T_C9 = pass, T_C8 = n/a, T_C3 = pass → **supported**.

## Round 1b (improved data, 2026-10-04)
*Re-run on the DQ1 context ledger (`scheme/build_turns_ledger.py`, `analysis/visibility_ledger.py`, `analysis/erasure_ledger.py`): turns are ledger calls, o = 1 is the call that received the message (exact by construction), in-flight = the previous call's first record came after the message. Responses: mention (the pre-registered measure), the DQ2 reply-parent author, and the content cosine of the talk with the message (non-mention). Predictions and the verdict rule unchanged. Data: `data/processed/H08-context-is-the-coupling/r1b/G42/` (`c9.json`, `c3.json`). D in percentage points (cosine ×100), day-bootstrap 95% CIs.*

| Statistic | Round 1 (H08 call-start rule) | Round 1b (ledger) | Note |
| --- | --- | --- | --- |
| D_talk | +1.41 [+0.57, +2.03] | +1.11 [+0.56, +1.50] | pre-registered clause |
| D_addr (mention) | +1.57 [+1.02, +2.03] | +1.87 [+1.20, +2.41] | pre-registered clause |
| D_addr, clean recipients (post hoc) | +1.06 [+0.73, +1.32] | +1.36 [+0.97, +1.67] | no talk at o = −2, −1 |
| D, reply author (new) | — | +1.90 [+1.23, +2.59] | DQ2 `reply_pairs.parent` |
| D, content cosine (new, ×100) | — | +3.42 [+0.48, +6.71] | non-mention response |
| other-room placebo D_addr | — | -0.02 [-0.06, +0.00] | two-room periods only |
| read-out delay of in-flight recipients, median | — | first record 32 s; context assembly 13 s | C9-V5 band 10–40 s |
| C3 / NE41 β_F, forced erasure (pp) | -4.45 [-8.12, -1.63] (mention, H15 catalog) | mention -3.07 [-7.18, -0.19]; **reply author -3.08 [-4.31, -2.27]** (relative -29% [-41, -22]; 1365 forced-erased units) | ledger `reset_forced` |

**Verdict (1b): supported** (round 1: supported).

## Scorecard (period-specific axes)
| Axis | This period |
| --- | --- |
| C adequacy | C9 discontinuity vs pseudo-message null: pass |
| E interventional | NE41 forced erasure (exogenous timing): pass |
| D unfitted | read-out turn and the zero-parameter kernel come from turn timing only |

## Notes
- Card: [`../../README.md`](../../README.md). Data: `data/processed/H08-context-is-the-coupling/G42/`.
