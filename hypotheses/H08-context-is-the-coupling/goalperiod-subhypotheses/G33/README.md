# H08 × G33: Discuss, debate, and act on your views about the recent Pentagon-AI company news (2026-03-02 → 2026-03-04)

**Verdict:** failed
**Verdict (1b):** failed (round 1b, 2026-10-04, context-ledger read-out; C9 talk clause CI includes 0; round-1 verdict kept above)
**Role:** replication (exploratory)
**Period:** regime II · mode C · N ≈ 12 · #general · 3 non-holdout days.

## Why this period
The Claude Code agent was in the village (ground truth for C1); a few nudges (C8 descriptive; pooled within regime).

## Prediction
*Written 2026-10-04 (~02:40 UTC), before running on this period (and before any real-data run of H08). Applies the card's round-1 predictions and amendments A1–A6 (written after the synthetic validation, before real data).*

- **C9-V1/V2 (visibility discontinuity, primary for every period):** among (message, recipient) pairs whose o = 0 turn is in flight, talking and addressing the sender jump at the read-out turn: D_talk = G_talk(1) − G_talk(0) > 0 and D_addr > 0, each with the day-bootstrap 95% CI excluding 0. G_addr(0) > 0 (contaminated floor, H18) but below ½ G_addr(1). A6: pre = G(0) − G(−1) ≈ 0.
- **C9-V4:** G_talk(2) < G_talk(1) (the response sits on the first visible turn).
- **C8:** too few isolated nudges for a per-period test (expected < 30 cells); the per-period kernel is descriptive and enters the pooled regime estimate (exception (d)).
- **C1 (amended 2026-10-04):** one room (#general), so the agent sees events from the whole village; the room rule's recall ≥ 0.9; coverage differs by type (talk, session start/stop, CONSOLIDATE visible; WAIT, PAUSE not); median delay is minutes, heavy-tailed; precision may fall below recall (fetch limits).

**Verdict rule (fixed now).** Tests: T_C9 = V1 and V2 both pass; T_C8 (powered periods) = P1 band and P3 both hold → pass, Φ outside the band or a rival family winning ≥ 60% → fail, else inconclusive; T_C3 (≥ 300 forced-erased units) = β_F < 0 with CI excluding 0 → pass, β_F > 0 with CI excluding 0 → fail, else inconclusive; T_C1 = recall ≥ 0.9 and (two rooms) other-room coverage ≤ 5% → pass, recall < 0.7 or other-room coverage > 20% → fail. **supported** = T_C9 passes and no other test fails; **failed** = T_C9 fails; **mixed** = T_C9 passes and another test fails. C2, C10 and the secondary items are reported but do not set the verdict.

## Result
*Run 2026-10-04 (`analysis/visibility.py`, `kernels.py`, `cc_exposure.py`, `inflow.py`, `erasure.py`, `sessions.py`). Data: `data/processed/H08-context-is-the-coupling/G33/` (c9/c8/c2/c3/c10.json). Figure: `figures/c9_offsets.pdf`. pp = percentage points; brackets are day-bootstrap 95% CIs.*

Read-out pairs: 21543 own-room (+ 0 other-room); in-flight share 97%, wake share 1%.

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| C9-V1 talk jump D_talk (pp) | +0.12 [-0.64, +0.60] | pseudo-message null | fail |
| C9-V2 addressing jump D_addr (pp) | -0.01 [-0.17, +0.22]; floor G_addr(0) +0.91, G_addr(1) +0.90 | | fail (floor clause fails) |
| A6 pre = G(0) − G(−1), talk / addr (pp) | +0.28 [-0.16, +0.69] / +0.55 [+0.22, +0.81] | ≈ 0 (common cause is flat) | ok |
| C9-V4 G_talk(2) < G_talk(1) | +0.56 vs +1.10 | | pass |
| *post hoc:* recipient did not talk at o = −2, −1 | D_talk +0.86 [+0.50, +1.20]; D_addr +0.71 [+0.34, +1.05]; G_addr(0) -0.03 | | (descriptive) |
| read-out delay, active recipients (descriptive) | median 53 s (IQR 23–121) | | — |
| C8 nudge → target | 8 isolated cells | | descriptive (pooled) |
| C1 room rule recall / precision | 1.000 / 0.579 (1993 events seen, 1129 fetches) | recall ≥ 0.9 | pass |
| C1 history replay share (> 1 day old) | 0%; recall on the current feed 1.000 | | — |
| C1 delay (current feed) | median 23 s, 90th 175 s | minutes | fail |
| C1 coverage by type (n ≥ 30) | 0.54–0.60 (WAIT 0.54, talk 0.60) | WAIT/PAUSE invisible | fail |

**Tests:** T_C9 = fail, T_C8 = n/a, T_C1 = pass → **failed**.

## Round 1b (improved data, 2026-10-04)
*Re-run on the DQ1 context ledger (`scheme/build_turns_ledger.py`, `analysis/visibility_ledger.py`, `analysis/erasure_ledger.py`): turns are ledger calls, o = 1 is the call that received the message (exact by construction), in-flight = the previous call's first record came after the message. Responses: mention (the pre-registered measure), the DQ2 reply-parent author, and the content cosine of the talk with the message (non-mention). Predictions and the verdict rule unchanged. Data: `data/processed/H08-context-is-the-coupling/r1b/G33/` (`c9.json`, `c3.json`). D in percentage points (cosine ×100), day-bootstrap 95% CIs.*

| Statistic | Round 1 (H08 call-start rule) | Round 1b (ledger) | Note |
| --- | --- | --- | --- |
| D_talk | +0.12 [-0.64, +0.60] | -0.22 [-0.52, +0.06] | pre-registered clause |
| D_addr (mention) | -0.01 [-0.17, +0.22] | +0.73 [+0.44, +1.21] | pre-registered clause |
| D_addr, clean recipients (post hoc) | +0.71 [+0.34, +1.05] | +0.79 [+0.55, +1.02] | no talk at o = −2, −1 |
| D, reply author (new) | — | +0.59 [+0.38, +0.84] | DQ2 `reply_pairs.parent` |
| D, content cosine (new, ×100) | — | +0.15 [-0.03, +0.33] | non-mention response |
| other-room placebo D_addr | — | — | two-room periods only |
| read-out delay of in-flight recipients, median | — | first record 41 s; context assembly 17 s | C9-V5 band 10–40 s |

**Verdict (1b): failed** (round 1: failed).

## Scorecard (period-specific axes)
| Axis | This period |
| --- | --- |
| C adequacy | C9 discontinuity vs pseudo-message null: fail |
| G ground truth | Claude Code fetch log vs room rule: pass |
| D unfitted | read-out turn and the zero-parameter kernel come from turn timing only |

## Round 2 (2026-10-05)
*Predictions: the card's "Round 2" section (written 2026-10-05 02:45 UTC, before any round-2 statistic on real data; amendments R2-A1..A3, R4-A1, R5-A1 written after the synthetic guards, still before real data). Role: replication (R2, R5-b, R5-c). Reserved days never read. Data: `data/processed/H08-context-is-the-coupling/r2/`. Content values are cosine ×100; brackets are 95% 1-hour-block bootstrap intervals (R4: day bootstrap).*

| Statistic | This period | Prediction | Note |
| --- | --- | --- | --- |
| R2 read − in-flight content at matched lag, no name and no reply (bge / gte) | +0.23 [-0.58, +1.06] / +0.30 [-0.67, +1.10] | > 0 (CI) in both models | read 18837, in flight 842 statement rows |
| R2 same, all statements (bge / gte) | +0.67 [-0.09, +1.31] / +1.07 [+0.07, +1.95] | — (robustness) | 18% of rows name or reply to the sender |
| R2 convergence share κ_c (bge, non-name) | 0.93 | [0.2, 0.6]; synthetic gated-only ≈ 0.73 | κ_c > 1: in-flight statements are closer |
| R5-b log-free monitor: flagged agent-days minus floor (bge / gte, pp) | -0.2 / -0.0 (31 agent-days; longest flagged run 0 / 0) | ≤ 2 pp (regime III) | not a validated detector (R5-P4 failed) |
| R5-c ledger items beyond the 200-event cap | 0.00% of 21306 | < 1% before 06-11; ≤ 5% in G51 | |

**Reading:** in regime I/II the round-1b content jump ran negative (in-flight talk sits closer in time). Lag matching removes that recency term; statements without the sender's name or a reply to it still show no read-gated content. The period verdict is unchanged (round 2 adds no period verdict rule).

## Notes
- Card: [`../../README.md`](../../README.md). Data: `data/processed/H08-context-is-the-coupling/G33/`.
