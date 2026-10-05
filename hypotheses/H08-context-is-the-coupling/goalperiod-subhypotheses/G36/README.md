# H08 × G36: Interact with other AI agents outside the Village! (2026-03-23 → 2026-03-27)

**Verdict:** failed
**Verdict (1b):** supported (round 1b, 2026-10-04, context-ledger read-out; C9 talk and addressing jumps both pass on the ledger; round-1 verdict kept above)
**Role:** replication (exploratory)
**Period:** regime II/III · mode C · N ≈ 13 · #best / #rest · 5 non-holdout days.

## Why this period
The Claude Code agent was in the village (ground truth for C1); a few nudges (C8 descriptive; pooled within regime); two rooms, so other-room messages are an invisible placebo (C9-V3); perma-computer-use: consolidations every ≤ 41 turns (NE41 erasures, C3) and token accounting (C2).

## Prediction
*Written 2026-10-04 (~02:40 UTC), before running on this period (and before any real-data run of H08). Applies the card's round-1 predictions and amendments A1–A6 (written after the synthetic validation, before real data).*

- **C9-V1/V2 (visibility discontinuity, primary for every period):** among (message, recipient) pairs whose o = 0 turn is in flight, talking and addressing the sender jump at the read-out turn: D_talk = G_talk(1) − G_talk(0) > 0 and D_addr > 0, each with the day-bootstrap 95% CI excluding 0. G_addr(0) > 0 (contaminated floor, H18) but below ½ G_addr(1). A6: pre = G(0) − G(−1) ≈ 0.
- **C9-V4:** G_talk(2) < G_talk(1) (the response sits on the first visible turn).
- **C9-V3:** messages from the room the recipient is not in: |D_other| < ⅓ of the own-room D, CI including 0.
- **C9-V5:** median read-out delay of in-flight (active) recipients 10–40 s.
- **C8:** too few isolated nudges for a per-period test (expected < 30 cells); the per-period kernel is descriptive and enters the pooled regime estimate (exception (d)).
- **C1 (amended 2026-10-04):** two rooms (the agent in #rest from 03-16, #general from 03-24 while the others were in #best/#rest): ≤ 5% of other-room events seen; recall ≥ 0.9; type and delay as above.
- **C2-I1/I2:** within agent-days, log uncached tokens rise with log(1 + new room messages) (b > 0, CI excluding 0) but messages explain little (partial R² < 0.05); P(talk | ≥ 1 new message) / P(talk | 0) > 1.2; ρ(uncached, call latency) > 0.
- **C3-E1/E2 (NE41):** where ≥ 300 erased units, addressing an old sender whose message was read before a forced consolidation falls relative to old senders read after it (β_F < 0, CI excluding 0; relative drop ≥ 30%); β_V within ±50% of β_F. **E3:** voluntary segments shorter when inflow per turn is higher (ρ < 0).

**Verdict rule (fixed now).** Tests: T_C9 = V1 and V2 both pass; T_C8 (powered periods) = P1 band and P3 both hold → pass, Φ outside the band or a rival family winning ≥ 60% → fail, else inconclusive; T_C3 (≥ 300 forced-erased units) = β_F < 0 with CI excluding 0 → pass, β_F > 0 with CI excluding 0 → fail, else inconclusive; T_C1 = recall ≥ 0.9 and (two rooms) other-room coverage ≤ 5% → pass, recall < 0.7 or other-room coverage > 20% → fail. **supported** = T_C9 passes and no other test fails; **failed** = T_C9 fails; **mixed** = T_C9 passes and another test fails. C2, C10 and the secondary items are reported but do not set the verdict.

## Result
*Run 2026-10-04 (`analysis/visibility.py`, `kernels.py`, `cc_exposure.py`, `inflow.py`, `erasure.py`, `sessions.py`). Data: `data/processed/H08-context-is-the-coupling/G36/` (c9/c8/c2/c3/c10.json). Figure: `figures/c9_offsets.pdf`. pp = percentage points; brackets are day-bootstrap 95% CIs.*

Read-out pairs: 8768 own-room (+ 10852 other-room); in-flight share 98%, wake share 1%.

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| C9-V1 talk jump D_talk (pp) | +1.13 [-0.24, +2.84] | pseudo-message null | fail |
| C9-V2 addressing jump D_addr (pp) | +1.47 [+0.94, +2.63]; floor G_addr(0) +0.09, G_addr(1) +1.56 | | pass |
| A6 pre = G(0) − G(−1), talk / addr (pp) | -0.75 [-2.37, +0.26] / -0.62 [-1.22, -0.18] | ≈ 0 (common cause is flat) | ok |
| C9-V4 G_talk(2) < G_talk(1) | +0.96 vs +1.49 | | pass |
| *post hoc:* recipient did not talk at o = −2, −1 | D_talk +1.13 [-0.16, +2.59]; D_addr +1.43 [+0.98, +2.35]; G_addr(0) -0.04 | | (descriptive) |
| C9-V3 other-room placebo D_talk / D_addr (pp) | -0.07 [-0.60, +0.35] / -0.03 [-0.16, +0.07] | ≈ 0 | pass |
| C9-V5 median read-out delay, active recipients | 41 s (IQR 22–97) | 10–40 s | fail |
| C8 nudge → target | 2 isolated cells | | descriptive (pooled) |
| C1 room rule recall / precision | 0.000 / 0.000 (889 events seen, 73 fetches) | recall ≥ 0.9 | fail |
| C1 history replay share (> 1 day old) | 100%; recall on the current feed — | | — |
| C1 other-room coverage | 0.0% | ≤ 5% | pass |
| C1 coverage by type (n ≥ 30) | 0.00–0.00 (WAIT 0.00, talk 0.00) | WAIT/PAUSE invisible | pass |
| C2-I1 elasticity b (raw) / partial R² | -0.72 [-0.98, -0.47] / 0.014 [0.006, 0.035] | b > 0, R² < 0.05 | fail |
| *post hoc:* b with previous-action control | 0.34 [-0.03, 0.62] | | (descriptive) |
| C2-I2 talk ratio / ρ(uncached, latency) | 1.63 [1.21, 2.14] / 0.19 [0.15, 0.22] | > 1.2 / > 0 | pass |
| C3-E1 β_F (forced erasure, pp) / relative | -2.95 [-6.46, +0.03] / -0.12 [-0.26, 0.00] (CF units 759) | < 0; rel ≤ −0.30 | inconclusive |
| C3-E2 β_V (pp) | -2.93 [-7.53, +1.68] | within ±50% of β_F | pass |
| C3-E3 ρ(voluntary segment length, inflow per turn) | 0.36 [0.06, 0.59] (n = 93) | < 0 | fail |

**Tests:** T_C9 = fail, T_C8 = n/a, T_C1 = fail, T_C3 = inconclusive → **failed**.

## Round 1b (improved data, 2026-10-04)
*Re-run on the DQ1 context ledger (`scheme/build_turns_ledger.py`, `analysis/visibility_ledger.py`, `analysis/erasure_ledger.py`): turns are ledger calls, o = 1 is the call that received the message (exact by construction), in-flight = the previous call's first record came after the message. Responses: mention (the pre-registered measure), the DQ2 reply-parent author, and the content cosine of the talk with the message (non-mention). Predictions and the verdict rule unchanged. Data: `data/processed/H08-context-is-the-coupling/r1b/G36/` (`c9.json`, `c3.json`). D in percentage points (cosine ×100), day-bootstrap 95% CIs.*

| Statistic | Round 1 (H08 call-start rule) | Round 1b (ledger) | Note |
| --- | --- | --- | --- |
| D_talk | +1.13 [-0.24, +2.84] | +1.10 [+0.16, +2.72] | pre-registered clause |
| D_addr (mention) | +1.47 [+0.94, +2.63] | +1.60 [+0.87, +3.22] | pre-registered clause |
| D_addr, clean recipients (post hoc) | +1.43 [+0.98, +2.35] | +1.51 [+0.93, +2.80] | no talk at o = −2, −1 |
| D, reply author (new) | — | +1.85 [+1.15, +2.84] | DQ2 `reply_pairs.parent` |
| D, content cosine (new, ×100) | — | +2.47 [+0.56, +7.08] | non-mention response |
| other-room placebo D_addr | — | -0.15 [-0.37, +0.03] | two-room periods only |
| read-out delay of in-flight recipients, median | — | first record 33 s; context assembly 13 s | C9-V5 band 10–40 s |
| C3 / NE41 β_F, forced erasure (pp) | -2.95 [-6.46, +0.03] (mention, H15 catalog) | mention -2.78 [-7.28, +1.10]; **reply author -2.36 [-3.54, -1.91]** (relative -16% [-24, -13]; 834 forced-erased units) | ledger `reset_forced` |

**Verdict (1b): supported** (round 1: failed).

## Scorecard (period-specific axes)
| Axis | This period |
| --- | --- |
| C adequacy | C9 discontinuity vs pseudo-message null: fail |
| G ground truth | Claude Code fetch log vs room rule: fail |
| E interventional | NE41 forced erasure (exogenous timing): inconclusive |
| D unfitted | read-out turn and the zero-parameter kernel come from turn timing only |

## Round 2 (2026-10-05)
*Predictions: the card's "Round 2" section (written 2026-10-05 02:45 UTC, before any round-2 statistic on real data; amendments R2-A1..A3, R4-A1, R5-A1 written after the synthetic guards, still before real data). Role: replication (R2, R5-b, R5-c), native (R4). Reserved days never read. Data: `data/processed/H08-context-is-the-coupling/r2/`. Content values are cosine ×100; brackets are 95% 1-hour-block bootstrap intervals (R4: day bootstrap).*

| Statistic | This period | Prediction | Note |
| --- | --- | --- | --- |
| R2 read − in-flight content at matched lag, no name and no reply (bge / gte) | -0.47 [-2.29, +1.85] / +0.44 [-1.43, +3.27] | > 0 (CI) in both models | read 3225, in flight 194 statement rows |
| R2 same, all statements (bge / gte) | +2.31 [+0.50, +4.36] / +3.20 [+1.35, +5.51] | — (robustness) | 30% of rows name or reply to the sender |
| R2 convergence share κ_c (bge, non-name) | 1.20 | [0.2, 0.6]; synthetic gated-only ≈ 0.73 | κ_c > 1: in-flight statements are closer |
| R2 other-room placebo (bge, non-name) | +0.75 [-0.47, +2.91] | \|Δ_other\| < ⅓ Δ_own, CI at 0 | |
| R5-b log-free monitor: flagged agent-days minus floor (bge / gte, pp) | +2.0 / +2.1 (44 agent-days; longest flagged run 1 / 1) | ≤ 2 pp (regime III) | not a validated detector (R5-P4 failed) |
| R5-c ledger items beyond the 200-event cap | 0.00% of 8698 | < 1% before 06-11; ≤ 5% in G51 | |
| R4 forced-erasure units with the sender newly written to memory | 61% of 809 | descriptive | |
| R4 CF × dose on replies (pp) | +2.55 [-3.94, +6.38] | > 0 pooled | pooled power 0.04 at half protection |
| R4 dose salience β_z on replies (pp) | +11.33 [+2.99, +16.50] | > 0 pooled | |
| R5-a Claude Code feed | replay episode 2026-03-17 → 2026-03-27 (130 fetches, 17.3 active h) | one episode from 03-17 | supported |

**Reading:** the round-1b content jump (regime III) is carried by statements that name or reply to the sender; without them, read statements are no closer to the message than in-flight statements at the same lag. The period verdict is unchanged (round 2 adds no period verdict rule).

## Notes
- Card: [`../../README.md`](../../README.md). Data: `data/processed/H08-context-is-the-coupling/G36/`.
