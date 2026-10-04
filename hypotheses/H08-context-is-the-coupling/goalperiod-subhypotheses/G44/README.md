# H08 × G44: Finetune your leader! (2026-05-26 → 2026-05-29)

**Verdict:** supported
**Role:** exploratory
**Period:** regime III · mode C · N ≈ 16 · #best / #rest · 4 non-holdout days.

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
*Run 2026-10-04 (`analysis/visibility.py`, `kernels.py`, `cc_exposure.py`, `inflow.py`, `erasure.py`, `sessions.py`). Data: `data/processed/H08-context-is-the-coupling/G44/` (c9/c8/c2/c3/c10.json). Figure: `figures/c9_offsets.pdf`. pp = percentage points; brackets are day-bootstrap 95% CIs.*

Read-out pairs: 16710 own-room (+ 12388 other-room); in-flight share 89%, wake share 5%.

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| C9-V1 talk jump D_talk (pp) | +1.25 [+0.44, +1.90] | pseudo-message null | pass |
| C9-V2 addressing jump D_addr (pp) | +1.26 [+0.43, +1.85]; floor G_addr(0) +0.17, G_addr(1) +1.43 | | pass |
| A6 pre = G(0) − G(−1), talk / addr (pp) | -0.58 [-0.71, -0.45] / -0.21 [-0.79, +0.28] | ≈ 0 (common cause is flat) | not ≈ 0 |
| C9-V4 G_talk(2) < G_talk(1) | +0.63 vs +0.85 | | pass |
| *post hoc:* recipient did not talk at o = −2, −1 | D_talk +0.88 [+0.33, +1.54]; D_addr +0.83 [+0.34, +1.15]; G_addr(0) +0.03 | | (descriptive) |
| C9-V3 other-room placebo D_talk / D_addr (pp) | -0.11 [-0.54, +0.55] / -0.02 [-0.05, +0.00] | ≈ 0 | pass |
| C9-V5 median read-out delay, active recipients | 45 s (IQR 27–105) | 10–40 s | fail |
| C8 nudge → target | 9 isolated cells | | descriptive (pooled) |
| C2-I1 elasticity b (raw) / partial R² | -0.45 [-0.48, -0.41] / 0.022 [0.018, 0.027] | b > 0, R² < 0.05 | fail |
| *post hoc:* b with previous-action control | -0.10 [-0.24, 0.15] | | (descriptive) |
| C2-I2 talk ratio / ρ(uncached, latency) | 1.26 [1.11, 1.41] / 0.13 [0.09, 0.17] | > 1.2 / > 0 | pass |
| C3-E1 β_F (forced erasure, pp) / relative | -4.92 [-7.12, -2.38] / -0.23 [-0.33, -0.11] (CF units 1087) | < 0; rel ≤ −0.30 | pass |
| C3-E2 β_V (pp) | -6.61 [-9.85, -3.04] | within ±50% of β_F | pass |
| C3-E3 ρ(voluntary segment length, inflow per turn) | -0.10 [-0.22, 0.02] (n = 115) | < 0 | pass |
| C10-L1 slope of log(1 + k) per session hour / ρ | 0.051 [0.017, 0.080] / -0.006 | > 0 | fail |

**Tests:** T_C9 = pass, T_C8 = n/a, T_C3 = pass → **supported**.

## Scorecard (period-specific axes)
| Axis | This period |
| --- | --- |
| C adequacy | C9 discontinuity vs pseudo-message null: pass |
| E interventional | NE41 forced erasure (exogenous timing): pass |
| D unfitted | read-out turn and the zero-parameter kernel come from turn timing only |

## Notes
- Card: [`../../README.md`](../../README.md). Data: `data/processed/H08-context-is-the-coupling/G44/`.
