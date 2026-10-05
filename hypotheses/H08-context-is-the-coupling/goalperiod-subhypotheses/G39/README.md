# H08 × G39: Build your own interactive world! (2026-04-27 → 2026-05-01)

**Verdict:** failed
**Verdict (1b):** failed (round 1b, 2026-10-04, context-ledger read-out; C9 talk and addressing clause CI includes 0; round-1 verdict kept above)
**Role:** replication (exploratory)
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
*Run 2026-10-04 (`analysis/visibility.py`, `kernels.py`, `cc_exposure.py`, `inflow.py`, `erasure.py`, `sessions.py`). Data: `data/processed/H08-context-is-the-coupling/G39/` (c9/c8/c2/c3/c10.json). Figure: `figures/c9_offsets.pdf`. pp = percentage points; brackets are day-bootstrap 95% CIs.*

Read-out pairs: 7860 own-room (+ 4542 other-room); in-flight share 96%, wake share 1%.

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| C9-V1 talk jump D_talk (pp) | +0.39 [-0.29, +0.97] | pseudo-message null | fail |
| C9-V2 addressing jump D_addr (pp) | +0.43 [+0.33, +0.61]; floor G_addr(0) +0.10, G_addr(1) +0.54 | | pass |
| A6 pre = G(0) − G(−1), talk / addr (pp) | -0.04 [-0.30, +0.26] / -0.12 [-0.23, +0.23] | ≈ 0 (common cause is flat) | ok |
| C9-V4 G_talk(2) < G_talk(1) | +0.49 vs +0.89 | | pass |
| *post hoc:* recipient did not talk at o = −2, −1 | D_talk +0.16 [-0.46, +0.75]; D_addr +0.26 [+0.08, +0.57]; G_addr(0) +0.14 | | (descriptive) |
| C9-V3 other-room placebo D_talk / D_addr (pp) | -0.31 [-0.60, -0.09] / -0.03 [-0.09, +0.00] | ≈ 0 | fail |
| C9-V5 median read-out delay, active recipients | 45 s (IQR 24–118) | 10–40 s | fail |
| C8 nudge → target | 2 isolated cells | | descriptive (pooled) |
| C2-I1 elasticity b (raw) / partial R² | -0.38 [-0.53, -0.20] / 0.007 [0.002, 0.014] | b > 0, R² < 0.05 | fail |
| *post hoc:* b with previous-action control | 0.56 [0.41, 0.85] | | (descriptive) |
| C2-I2 talk ratio / ρ(uncached, latency) | 2.14 [1.62, 2.35] / 0.05 [-0.01, 0.11] | > 1.2 / > 0 | partial |
| C3-E1 β_F (forced erasure, pp) / relative | -2.22 [-9.76, -0.11] / -0.31 [-1.35, -0.02] (CF units 1399) | < 0; rel ≤ −0.30 | pass |
| C3-E2 β_V (pp) | +0.14 [-7.47, +6.11] | within ±50% of β_F | fail |
| C3-E3 ρ(voluntary segment length, inflow per turn) | -0.10 [-0.37, 0.16] (n = 79) | < 0 | pass |
| C10-L1 slope of log(1 + k) per session hour / ρ | 0.038 [-0.025, 0.112] / +0.022 | > 0 | fail |

**Tests:** T_C9 = fail, T_C8 = n/a, T_C3 = pass → **failed**.

## Round 1b (improved data, 2026-10-04)
*Re-run on the DQ1 context ledger (`scheme/build_turns_ledger.py`, `analysis/visibility_ledger.py`, `analysis/erasure_ledger.py`): turns are ledger calls, o = 1 is the call that received the message (exact by construction), in-flight = the previous call's first record came after the message. Responses: mention (the pre-registered measure), the DQ2 reply-parent author, and the content cosine of the talk with the message (non-mention). Predictions and the verdict rule unchanged. Data: `data/processed/H08-context-is-the-coupling/r1b/G39/` (`c9.json`, `c3.json`). D in percentage points (cosine ×100), day-bootstrap 95% CIs.*

| Statistic | Round 1 (H08 call-start rule) | Round 1b (ledger) | Note |
| --- | --- | --- | --- |
| D_talk | +0.39 [-0.29, +0.97] | +0.38 [-0.21, +1.18] | pre-registered clause |
| D_addr (mention) | +0.43 [+0.33, +0.61] | +0.26 [-0.22, +0.48] | pre-registered clause |
| D_addr, clean recipients (post hoc) | +0.26 [+0.08, +0.57] | +0.07 [-0.42, +0.37] | no talk at o = −2, −1 |
| D, reply author (new) | — | +0.60 [+0.34, +0.83] | DQ2 `reply_pairs.parent` |
| D, content cosine (new, ×100) | — | +3.15 [+1.41, +6.62] | non-mention response |
| other-room placebo D_addr | — | +0.04 [+0.00, +0.12] | two-room periods only |
| read-out delay of in-flight recipients, median | — | first record 37 s; context assembly 16 s | C9-V5 band 10–40 s |
| C3 / NE41 β_F, forced erasure (pp) | -2.22 [-9.76, -0.11] (mention, H15 catalog) | mention -1.47 [-7.48, +0.34]; **reply author -0.98 [-2.92, -0.21]** (relative -31% [-92, -7]; 1516 forced-erased units) | ledger `reset_forced` |

**Verdict (1b): failed** (round 1: failed).

## Scorecard (period-specific axes)
| Axis | This period |
| --- | --- |
| C adequacy | C9 discontinuity vs pseudo-message null: fail |
| E interventional | NE41 forced erasure (exogenous timing): pass |
| D unfitted | read-out turn and the zero-parameter kernel come from turn timing only |

## Round 2 (2026-10-05)
*Predictions: the card's "Round 2" section (written 2026-10-05 02:45 UTC, before any round-2 statistic on real data; amendments R2-A1..A3, R4-A1, R5-A1 written after the synthetic guards, still before real data). Role: replication (R2, R5-b, R5-c), native (R4). Reserved days never read. Data: `data/processed/H08-context-is-the-coupling/r2/`. Content values are cosine ×100; brackets are 95% 1-hour-block bootstrap intervals (R4: day bootstrap).*

| Statistic | This period | Prediction | Note |
| --- | --- | --- | --- |
| R2 read − in-flight content at matched lag, no name and no reply (bge / gte) | -1.73 [-4.12, +0.10] / -1.55 [-3.90, +0.13] | > 0 (CI) in both models | read 2012, in flight 95 statement rows |
| R2 same, all statements (bge / gte) | -0.19 [-2.45, +2.29] / +0.10 [-2.11, +2.07] | — (robustness) | 11% of rows name or reply to the sender |
| R2 convergence share κ_c (bge, non-name) | -12.51 | [0.2, 0.6]; synthetic gated-only ≈ 0.73 | κ_c > 1: in-flight statements are closer |
| R2 other-room placebo (bge, non-name) | -2.46 [-4.09, +1.69] | \|Δ_other\| < ⅓ Δ_own, CI at 0 | |
| R5-b log-free monitor: flagged agent-days minus floor (bge / gte, pp) | +9.1 / +5.2 (33 agent-days; longest flagged run 3 / 3) | ≤ 2 pp (regime III) | not a validated detector (R5-P4 failed) |
| R5-c ledger items beyond the 200-event cap | 0.00% of 8112 | < 1% before 06-11; ≤ 5% in G51 | |
| R4 forced-erasure units with the sender newly written to memory | 90% of 1495 | descriptive | |
| R4 CF × dose on replies (pp) | +3.22 [+0.76, +7.50] | > 0 pooled | pooled power 0.04 at half protection |
| R4 dose salience β_z on replies (pp) | -0.41 [-6.09, +16.48] | > 0 pooled | |

**Reading:** the round-1b content jump (regime III) is carried by statements that name or reply to the sender; without them, read statements are no closer to the message than in-flight statements at the same lag. The period verdict is unchanged (round 2 adds no period verdict rule).

## Notes
- Card: [`../../README.md`](../../README.md). Data: `data/processed/H08-context-is-the-coupling/G39/`.
