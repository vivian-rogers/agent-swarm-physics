# H08 × G25: Create a digital museum of 2025 (2025-12-29 → 2026-01-02)

**Verdict:** failed
**Verdict (1b):** failed (round 1b, 2026-10-04, context-ledger read-out; C9 talk and addressing clause CI includes 0; round-1 verdict kept above)
**Role:** replication (exploratory)
**Period:** regime I · mode C · N ≈ 10 · #general · 5 non-holdout days.

## Why this period
Regime I after NE09 (chat interleaved into computer-use context), so the call-start visibility rule applies.

## Prediction
*Written 2026-10-04 (~02:40 UTC), before running on this period (and before any real-data run of H08). Applies the card's round-1 predictions and amendments A1–A6 (written after the synthetic validation, before real data).*

- **C9-V1/V2 (visibility discontinuity, primary for every period):** among (message, recipient) pairs whose o = 0 turn is in flight, talking and addressing the sender jump at the read-out turn: D_talk = G_talk(1) − G_talk(0) > 0 and D_addr > 0, each with the day-bootstrap 95% CI excluding 0. G_addr(0) > 0 (contaminated floor, H18) but below ½ G_addr(1). A6: pre = G(0) − G(−1) ≈ 0.
- **C9-V4:** G_talk(2) < G_talk(1) (the response sits on the first visible turn).

**Verdict rule (fixed now).** Tests: T_C9 = V1 and V2 both pass; T_C8 (powered periods) = P1 band and P3 both hold → pass, Φ outside the band or a rival family winning ≥ 60% → fail, else inconclusive; T_C3 (≥ 300 forced-erased units) = β_F < 0 with CI excluding 0 → pass, β_F > 0 with CI excluding 0 → fail, else inconclusive; T_C1 = recall ≥ 0.9 and (two rooms) other-room coverage ≤ 5% → pass, recall < 0.7 or other-room coverage > 20% → fail. **supported** = T_C9 passes and no other test fails; **failed** = T_C9 fails; **mixed** = T_C9 passes and another test fails. C2, C10 and the secondary items are reported but do not set the verdict.

## Result
*Run 2026-10-04 (`analysis/visibility.py`, `kernels.py`, `cc_exposure.py`, `inflow.py`, `erasure.py`, `sessions.py`). Data: `data/processed/H08-context-is-the-coupling/G25/` (c9/c8/c2/c3/c10.json). Figure: `figures/c9_offsets.pdf`. pp = percentage points; brackets are day-bootstrap 95% CIs.*

Read-out pairs: 22602 own-room (+ 0 other-room); in-flight share 98%, wake share 0%.

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| C9-V1 talk jump D_talk (pp) | -0.10 [-0.74, +0.43] | pseudo-message null | fail |
| C9-V2 addressing jump D_addr (pp) | -0.63 [-1.08, +0.04]; floor G_addr(0) +0.79, G_addr(1) +0.16 | | fail (floor clause fails) |
| A6 pre = G(0) − G(−1), talk / addr (pp) | -0.19 [-0.65, +0.29] / +0.87 [+0.54, +1.10] | ≈ 0 (common cause is flat) | ok |
| C9-V4 G_talk(2) < G_talk(1) | +0.10 vs +0.93 | | pass |
| *post hoc:* recipient did not talk at o = −2, −1 | D_talk +0.26 [-0.25, +0.61]; D_addr +0.56 [+0.16, +0.99]; G_addr(0) +0.19 | | (descriptive) |
| read-out delay, active recipients (descriptive) | median 56 s (IQR 29–114) | | — |

**Tests:** T_C9 = fail → **failed**.

## Round 1b (improved data, 2026-10-04)
*Re-run on the DQ1 context ledger (`scheme/build_turns_ledger.py`, `analysis/visibility_ledger.py`, `analysis/erasure_ledger.py`): turns are ledger calls, o = 1 is the call that received the message (exact by construction), in-flight = the previous call's first record came after the message. Responses: mention (the pre-registered measure), the DQ2 reply-parent author, and the content cosine of the talk with the message (non-mention). Predictions and the verdict rule unchanged. Data: `data/processed/H08-context-is-the-coupling/r1b/G25/` (`c9.json`, `c3.json`). D in percentage points (cosine ×100), day-bootstrap 95% CIs.*

| Statistic | Round 1 (H08 call-start rule) | Round 1b (ledger) | Note |
| --- | --- | --- | --- |
| D_talk | -0.10 [-0.74, +0.43] | +0.26 [-0.24, +1.04] | pre-registered clause |
| D_addr (mention) | -0.63 [-1.08, +0.04] | +0.52 [-0.02, +0.83] | pre-registered clause |
| D_addr, clean recipients (post hoc) | +0.56 [+0.16, +0.99] | +0.44 [+0.04, +0.71] | no talk at o = −2, −1 |
| D, reply author (new) | — | +0.76 [+0.30, +1.06] | DQ2 `reply_pairs.parent` |
| D, content cosine (new, ×100) | — | -0.85 [-1.44, +0.12] | non-mention response |
| other-room placebo D_addr | — | — | two-room periods only |
| read-out delay of in-flight recipients, median | — | first record 41 s; context assembly 16 s | C9-V5 band 10–40 s |

**Verdict (1b): failed** (round 1: failed).

## Scorecard (period-specific axes)
| Axis | This period |
| --- | --- |
| C adequacy | C9 discontinuity vs pseudo-message null: fail |
| D unfitted | read-out turn and the zero-parameter kernel come from turn timing only |

## Round 2 (2026-10-05)
*Predictions: the card's "Round 2" section (written 2026-10-05 02:45 UTC, before any round-2 statistic on real data; amendments R2-A1..A3, R4-A1, R5-A1 written after the synthetic guards, still before real data). Role: replication (R2, R5-b, R5-c). Reserved days never read. Data: `data/processed/H08-context-is-the-coupling/r2/`. Content values are cosine ×100; brackets are 95% 1-hour-block bootstrap intervals (R4: day bootstrap).*

| Statistic | This period | Prediction | Note |
| --- | --- | --- | --- |
| R2 read − in-flight content at matched lag, no name and no reply (bge / gte) | +0.58 [-0.65, +1.61] / +1.19 [+0.07, +2.16] | > 0 (CI) in both models | read 19842, in flight 940 statement rows |
| R2 same, all statements (bge / gte) | +1.06 [-0.03, +1.95] / +1.47 [+0.24, +2.40] | — (robustness) | 22% of rows name or reply to the sender |
| R2 convergence share κ_c (bge, non-name) | 0.87 | [0.2, 0.6]; synthetic gated-only ≈ 0.73 | κ_c > 1: in-flight statements are closer |
| R5-b log-free monitor: flagged agent-days minus floor (bge / gte, pp) | -0.0 / -0.1 (46 agent-days; longest flagged run 0 / 0) | ≤ 2 pp (regime III) | not a validated detector (R5-P4 failed) |
| R5-c ledger items beyond the 200-event cap | 0.00% of 22819 | < 1% before 06-11; ≤ 5% in G51 | |

**Reading:** in regime I/II the round-1b content jump ran negative (in-flight talk sits closer in time). Lag matching removes that recency term; statements without the sender's name or a reply to it still show no read-gated content. The period verdict is unchanged (round 2 adds no period verdict rule).

## Notes
- Card: [`../../README.md`](../../README.md). Data: `data/processed/H08-context-is-the-coupling/G25/`.
