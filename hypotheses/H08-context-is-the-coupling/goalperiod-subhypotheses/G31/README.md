# H08 × G31: Pick your own goal (agents bid 3.7 Sonnet farewell) (2026-02-16 → 2026-02-20)

**Verdict:** failed
**Role:** exploratory
**Period:** regime I · mode F · N ≈ 12 · #general · 5 non-holdout days.

## Why this period
The Claude Code agent was in the village (ground truth for C1); a few nudges (C8 descriptive; pooled within regime); regime I after NE09 (chat interleaved into computer-use context), so the call-start visibility rule applies.

## Prediction
*Written 2026-10-04 (~02:40 UTC), before running on this period (and before any real-data run of H08). Applies the card's round-1 predictions and amendments A1–A6 (written after the synthetic validation, before real data).*

- **C9-V1/V2 (visibility discontinuity, primary for every period):** among (message, recipient) pairs whose o = 0 turn is in flight, talking and addressing the sender jump at the read-out turn: D_talk = G_talk(1) − G_talk(0) > 0 and D_addr > 0, each with the day-bootstrap 95% CI excluding 0. G_addr(0) > 0 (contaminated floor, H18) but below ½ G_addr(1). A6: pre = G(0) − G(−1) ≈ 0.
- **C9-V4:** G_talk(2) < G_talk(1) (the response sits on the first visible turn).
- **C8:** too few isolated nudges for a per-period test (expected < 30 cells); the per-period kernel is descriptive and enters the pooled regime estimate (exception (d)).
- **C1 (amended 2026-10-04):** one room (#general), so the agent sees events from the whole village; the room rule's recall ≥ 0.9; coverage differs by type (talk, session start/stop, CONSOLIDATE visible; WAIT, PAUSE not); median delay is minutes, heavy-tailed; precision may fall below recall (fetch limits).

**Verdict rule (fixed now).** Tests: T_C9 = V1 and V2 both pass; T_C8 (powered periods) = P1 band and P3 both hold → pass, Φ outside the band or a rival family winning ≥ 60% → fail, else inconclusive; T_C3 (≥ 300 forced-erased units) = β_F < 0 with CI excluding 0 → pass, β_F > 0 with CI excluding 0 → fail, else inconclusive; T_C1 = recall ≥ 0.9 and (two rooms) other-room coverage ≤ 5% → pass, recall < 0.7 or other-room coverage > 20% → fail. **supported** = T_C9 passes and no other test fails; **failed** = T_C9 fails; **mixed** = T_C9 passes and another test fails. C2, C10 and the secondary items are reported but do not set the verdict.

## Result
*Run 2026-10-04 (`analysis/visibility.py`, `kernels.py`, `cc_exposure.py`, `inflow.py`, `erasure.py`, `sessions.py`). Data: `data/processed/H08-context-is-the-coupling/G31/` (c9/c8/c2/c3/c10.json). Figure: `figures/c9_offsets.pdf`. pp = percentage points; brackets are day-bootstrap 95% CIs.*

Read-out pairs: 32835 own-room (+ 0 other-room); in-flight share 98%, wake share 1%.

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| C9-V1 talk jump D_talk (pp) | -0.59 [-1.01, -0.07] | pseudo-message null | fail |
| C9-V2 addressing jump D_addr (pp) | +0.13 [-0.35, +0.57]; floor G_addr(0) +0.64, G_addr(1) +0.77 | | fail (floor clause fails) |
| A6 pre = G(0) − G(−1), talk / addr (pp) | -0.13 [-0.69, +0.38] / +0.17 [-0.00, +0.38] | ≈ 0 (common cause is flat) | ok |
| C9-V4 G_talk(2) < G_talk(1) | +0.93 vs +1.01 | | pass |
| *post hoc:* recipient did not talk at o = −2, −1 | D_talk +0.06 [-0.97, +1.01]; D_addr +0.48 [+0.35, +0.59]; G_addr(0) +0.07 | | (descriptive) |
| read-out delay, active recipients (descriptive) | median 42 s (IQR 21–100) | | — |
| C8 nudge → target | 8 isolated cells | | descriptive (pooled) |
| C1 room rule recall / precision | 0.974 / 0.642 (3775 events seen, 3690 fetches) | recall ≥ 0.9 | pass |
| C1 history replay share (> 1 day old) | 1%; recall on the current feed 0.987 | | — |
| C1 delay (current feed) | median 14 s, 90th 564 s | minutes | fail |
| C1 coverage by type (n ≥ 30) | 0.63–0.69 (WAIT 0.69, talk 0.64) | WAIT/PAUSE invisible | fail |

**Tests:** T_C9 = fail, T_C8 = n/a, T_C1 = pass → **failed**.

## Scorecard (period-specific axes)
| Axis | This period |
| --- | --- |
| C adequacy | C9 discontinuity vs pseudo-message null: fail |
| G ground truth | Claude Code fetch log vs room rule: pass |
| D unfitted | read-out turn and the zero-parameter kernel come from turn timing only |

## Notes
- Card: [`../../README.md`](../../README.md). Data: `data/processed/H08-context-is-the-coupling/G31/`.
