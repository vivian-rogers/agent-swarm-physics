# H08 × G35: Test your game to make it as fun and functional as you can! (2026-03-16 → 2026-03-20)

**Verdict:** failed
**Verdict (1b):** failed (round 1b, 2026-10-04, context-ledger read-out; C9 talk clause CI includes 0; round-1 verdict kept above)
**Role:** exploratory
**Period:** regime II · mode C · N ≈ 13 · #best (3) / #rest (10) from 03-16 · 5 non-holdout days.

## Why this period
The Claude Code agent was in the village (ground truth for C1); a few nudges (C8 descriptive; pooled within regime); two rooms, so other-room messages are an invisible placebo (C9-V3).

## Prediction
*Written 2026-10-04 (~02:40 UTC), before running on this period (and before any real-data run of H08). Applies the card's round-1 predictions and amendments A1–A6 (written after the synthetic validation, before real data).*

- **C9-V1/V2 (visibility discontinuity, primary for every period):** among (message, recipient) pairs whose o = 0 turn is in flight, talking and addressing the sender jump at the read-out turn: D_talk = G_talk(1) − G_talk(0) > 0 and D_addr > 0, each with the day-bootstrap 95% CI excluding 0. G_addr(0) > 0 (contaminated floor, H18) but below ½ G_addr(1). A6: pre = G(0) − G(−1) ≈ 0.
- **C9-V4:** G_talk(2) < G_talk(1) (the response sits on the first visible turn).
- **C9-V3:** messages from the room the recipient is not in: |D_other| < ⅓ of the own-room D, CI including 0.
- **C8:** too few isolated nudges for a per-period test (expected < 30 cells); the per-period kernel is descriptive and enters the pooled regime estimate (exception (d)).
- **C1 (amended 2026-10-04):** two rooms (the agent in #rest from 03-16, #general from 03-24 while the others were in #best/#rest): ≤ 5% of other-room events seen; recall ≥ 0.9; type and delay as above.

**Verdict rule (fixed now).** Tests: T_C9 = V1 and V2 both pass; T_C8 (powered periods) = P1 band and P3 both hold → pass, Φ outside the band or a rival family winning ≥ 60% → fail, else inconclusive; T_C3 (≥ 300 forced-erased units) = β_F < 0 with CI excluding 0 → pass, β_F > 0 with CI excluding 0 → fail, else inconclusive; T_C1 = recall ≥ 0.9 and (two rooms) other-room coverage ≤ 5% → pass, recall < 0.7 or other-room coverage > 20% → fail. **supported** = T_C9 passes and no other test fails; **failed** = T_C9 fails; **mixed** = T_C9 passes and another test fails. C2, C10 and the secondary items are reported but do not set the verdict.

## Result
*Run 2026-10-04 (`analysis/visibility.py`, `kernels.py`, `cc_exposure.py`, `inflow.py`, `erasure.py`, `sessions.py`). Data: `data/processed/H08-context-is-the-coupling/G35/` (c9/c8/c2/c3/c10.json). Figure: `figures/c9_offsets.pdf`. pp = percentage points; brackets are day-bootstrap 95% CIs.*

Read-out pairs: 14570 own-room (+ 10621 other-room); in-flight share 98%, wake share 0%.

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| C9-V1 talk jump D_talk (pp) | -0.72 [-1.20, -0.21] | pseudo-message null | fail |
| C9-V2 addressing jump D_addr (pp) | +0.61 [+0.43, +0.82]; floor G_addr(0) +0.75, G_addr(1) +1.36 | | pass (floor clause fails) |
| A6 pre = G(0) − G(−1), talk / addr (pp) | +0.36 [-0.72, +1.37] / +0.16 [-0.21, +0.55] | ≈ 0 (common cause is flat) | ok |
| C9-V4 G_talk(2) < G_talk(1) | +2.38 vs +2.56 | | pass |
| *post hoc:* recipient did not talk at o = −2, −1 | D_talk +0.31 [-0.41, +1.15]; D_addr +0.77 [+0.40, +1.07]; G_addr(0) +0.11 | | (descriptive) |
| C9-V3 other-room placebo D_talk / D_addr (pp) | -0.47 [-0.91, -0.05] / +0.03 [-0.11, +0.27] | ≈ 0 | fail |
| read-out delay, active recipients (descriptive) | median 32 s (IQR 19–65) | | — |
| C8 nudge → target | 4 isolated cells | | descriptive (pooled) |
| C1 room rule recall / precision | 0.308 / 0.145 (1366 events seen, 124 fetches) | recall ≥ 0.9 | fail |
| C1 history replay share (> 1 day old) | 65%; recall on the current feed 0.959 | | — |
| C1 other-room coverage | 1.6% | ≤ 5% | pass |
| C1 delay (current feed) | median 266 s, 90th 715 s | minutes | pass |
| C1 coverage by type (n ≥ 30) | 0.14–0.19 (WAIT 0.19, talk 0.15) | WAIT/PAUSE invisible | pass |

**Tests:** T_C9 = fail, T_C8 = n/a, T_C1 = fail → **failed**.

## Round 1b (improved data, 2026-10-04)
*Re-run on the DQ1 context ledger (`scheme/build_turns_ledger.py`, `analysis/visibility_ledger.py`, `analysis/erasure_ledger.py`): turns are ledger calls, o = 1 is the call that received the message (exact by construction), in-flight = the previous call's first record came after the message. Responses: mention (the pre-registered measure), the DQ2 reply-parent author, and the content cosine of the talk with the message (non-mention). Predictions and the verdict rule unchanged. Data: `data/processed/H08-context-is-the-coupling/r1b/G35/` (`c9.json`, `c3.json`). D in percentage points (cosine ×100), day-bootstrap 95% CIs.*

| Statistic | Round 1 (H08 call-start rule) | Round 1b (ledger) | Note |
| --- | --- | --- | --- |
| D_talk | -0.72 [-1.20, -0.21] | +0.75 [-0.08, +1.25] | pre-registered clause |
| D_addr (mention) | +0.61 [+0.43, +0.82] | +0.48 [+0.17, +0.71] | pre-registered clause |
| D_addr, clean recipients (post hoc) | +0.77 [+0.40, +1.07] | +0.47 [+0.11, +0.80] | no talk at o = −2, −1 |
| D, reply author (new) | — | +1.03 [+0.84, +1.19] | DQ2 `reply_pairs.parent` |
| D, content cosine (new, ×100) | — | -0.33 [-0.90, +0.57] | non-mention response |
| other-room placebo D_addr | — | +0.00 [-0.10, +0.09] | two-room periods only |
| read-out delay of in-flight recipients, median | — | first record 27 s; context assembly 10 s | C9-V5 band 10–40 s |

**Verdict (1b): failed** (round 1: failed).

## Scorecard (period-specific axes)
| Axis | This period |
| --- | --- |
| C adequacy | C9 discontinuity vs pseudo-message null: fail |
| G ground truth | Claude Code fetch log vs room rule: fail |
| D unfitted | read-out turn and the zero-parameter kernel come from turn timing only |

## Notes
- Card: [`../../README.md`](../../README.md). Data: `data/processed/H08-context-is-the-coupling/G35/`.
