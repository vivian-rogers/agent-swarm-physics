# H08 × G30: Adopt a park and get it cleaned! (2026-02-09 → 2026-02-13)

**Verdict:** failed
**Role:** exploratory
**Period:** regime I · mode C · N ≈ 12 · #general · 5 non-holdout days.

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
*Run 2026-10-04 (`analysis/visibility.py`, `kernels.py`, `cc_exposure.py`, `inflow.py`, `erasure.py`, `sessions.py`). Data: `data/processed/H08-context-is-the-coupling/G30/` (c9/c8/c2/c3/c10.json). Figure: `figures/c9_offsets.pdf`. pp = percentage points; brackets are day-bootstrap 95% CIs.*

Read-out pairs: 26979 own-room (+ 0 other-room); in-flight share 98%, wake share 1%.

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| C9-V1 talk jump D_talk (pp) | -0.28 [-0.87, +0.58] | pseudo-message null | fail |
| C9-V2 addressing jump D_addr (pp) | -0.31 [-0.52, -0.07]; floor G_addr(0) +1.01, G_addr(1) +0.70 | | fail (floor clause fails) |
| A6 pre = G(0) − G(−1), talk / addr (pp) | +0.29 [-0.27, +0.86] / +0.66 [+0.44, +0.88] | ≈ 0 (common cause is flat) | ok |
| C9-V4 G_talk(2) < G_talk(1) | +1.68 vs +2.07 | | pass |
| *post hoc:* recipient did not talk at o = −2, −1 | D_talk +0.01 [-0.53, +0.69]; D_addr +0.38 [+0.21, +0.55]; G_addr(0) +0.12 | | (descriptive) |
| read-out delay, active recipients (descriptive) | median 42 s (IQR 23–89) | | — |
| C8 nudge → target | 1 isolated cells | | descriptive (pooled) |
| C1 room rule recall / precision | 0.991 / 0.575 (2898 events seen, 3177 fetches) | recall ≥ 0.9 | pass |
| C1 history replay share (> 1 day old) | 0%; recall on the current feed 0.991 | | — |
| C1 delay (current feed) | median 17 s, 90th 218 s | minutes | fail |
| C1 coverage by type (n ≥ 30) | 0.53–0.61 (WAIT 0.53, talk 0.57) | WAIT/PAUSE invisible | fail |

**Tests:** T_C9 = fail, T_C8 = n/a, T_C1 = pass → **failed**.

## Scorecard (period-specific axes)
| Axis | This period |
| --- | --- |
| C adequacy | C9 discontinuity vs pseudo-message null: fail |
| G ground truth | Claude Code fetch log vs room rule: pass |
| D unfitted | read-out turn and the zero-parameter kernel come from turn timing only |

## Notes
- Card: [`../../README.md`](../../README.md). Data: `data/processed/H08-context-is-the-coupling/G30/`.
