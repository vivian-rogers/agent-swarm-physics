# H08 × G27: Hack the OWASP Juice Shop hacking playground (2026-01-12 → 2026-01-23)

**Verdict:** failed
**Role:** exploratory
**Period:** regime I · mode K · N ≈ 10 · #general · 10 non-holdout days.

## Why this period
Regime I after NE09 (chat interleaved into computer-use context), so the call-start visibility rule applies.

## Prediction
*Written 2026-10-04 (~02:40 UTC), before running on this period (and before any real-data run of H08). Applies the card's round-1 predictions and amendments A1–A6 (written after the synthetic validation, before real data).*

- **C9-V1/V2 (visibility discontinuity, primary for every period):** among (message, recipient) pairs whose o = 0 turn is in flight, talking and addressing the sender jump at the read-out turn: D_talk = G_talk(1) − G_talk(0) > 0 and D_addr > 0, each with the day-bootstrap 95% CI excluding 0. G_addr(0) > 0 (contaminated floor, H18) but below ½ G_addr(1). A6: pre = G(0) − G(−1) ≈ 0.
- **C9-V4:** G_talk(2) < G_talk(1) (the response sits on the first visible turn).

**Verdict rule (fixed now).** Tests: T_C9 = V1 and V2 both pass; T_C8 (powered periods) = P1 band and P3 both hold → pass, Φ outside the band or a rival family winning ≥ 60% → fail, else inconclusive; T_C3 (≥ 300 forced-erased units) = β_F < 0 with CI excluding 0 → pass, β_F > 0 with CI excluding 0 → fail, else inconclusive; T_C1 = recall ≥ 0.9 and (two rooms) other-room coverage ≤ 5% → pass, recall < 0.7 or other-room coverage > 20% → fail. **supported** = T_C9 passes and no other test fails; **failed** = T_C9 fails; **mixed** = T_C9 passes and another test fails. C2, C10 and the secondary items are reported but do not set the verdict.

## Result
*Run 2026-10-04 (`analysis/visibility.py`, `kernels.py`, `cc_exposure.py`, `inflow.py`, `erasure.py`, `sessions.py`). Data: `data/processed/H08-context-is-the-coupling/G27/` (c9/c8/c2/c3/c10.json). Figure: `figures/c9_offsets.pdf`. pp = percentage points; brackets are day-bootstrap 95% CIs.*

Read-out pairs: 33957 own-room (+ 0 other-room); in-flight share 97%, wake share 1%.

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| C9-V1 talk jump D_talk (pp) | -0.71 [-1.41, -0.04] | pseudo-message null | fail |
| C9-V2 addressing jump D_addr (pp) | -0.58 [-1.30, +0.06]; floor G_addr(0) +1.43, G_addr(1) +0.85 | | fail (floor clause fails) |
| A6 pre = G(0) − G(−1), talk / addr (pp) | +0.41 [-0.10, +0.97] / +1.12 [+0.26, +1.87] | ≈ 0 (common cause is flat) | ok |
| C9-V4 G_talk(2) < G_talk(1) | +0.01 vs +0.06 | | pass |
| *post hoc:* recipient did not talk at o = −2, −1 | D_talk -0.56 [-1.28, +0.19]; D_addr +0.43 [+0.24, +0.61]; G_addr(0) +0.07 | | (descriptive) |
| read-out delay, active recipients (descriptive) | median 49 s (IQR 23–128) | | — |

**Tests:** T_C9 = fail → **failed**.

## Scorecard (period-specific axes)
| Axis | This period |
| --- | --- |
| C adequacy | C9 discontinuity vs pseudo-message null: fail |
| D unfitted | read-out turn and the zero-parameter kernel come from turn timing only |

## Notes
- Card: [`../../README.md`](../../README.md). Data: `data/processed/H08-context-is-the-coupling/G27/`.
