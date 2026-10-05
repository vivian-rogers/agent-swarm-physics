# H08 × G37: Pick your own goal! (2026-03-30 → 2026-04-01)

**Verdict:** supported
**Verdict (1b):** supported (round 1b, 2026-10-04, context-ledger read-out; C9 talk and addressing jumps both pass on the ledger; round-1 verdict kept above)
**Role:** replication (exploratory)
**Period:** regime III · mode F · N ≈ 13 · #best / #rest · 3 non-holdout days.

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
- **C10-L1 (HH91 as stated):** backlog k per talk turn rises with session hour (ρ > 0; within-agent-day slope CI > 0).

**Verdict rule (fixed now).** Tests: T_C9 = V1 and V2 both pass; T_C8 (powered periods) = P1 band and P3 both hold → pass, Φ outside the band or a rival family winning ≥ 60% → fail, else inconclusive; T_C3 (≥ 300 forced-erased units) = β_F < 0 with CI excluding 0 → pass, β_F > 0 with CI excluding 0 → fail, else inconclusive; T_C1 = recall ≥ 0.9 and (two rooms) other-room coverage ≤ 5% → pass, recall < 0.7 or other-room coverage > 20% → fail. **supported** = T_C9 passes and no other test fails; **failed** = T_C9 fails; **mixed** = T_C9 passes and another test fails. C2, C10 and the secondary items are reported but do not set the verdict.

## Result
*Run 2026-10-04 (`analysis/visibility.py`, `kernels.py`, `cc_exposure.py`, `inflow.py`, `erasure.py`, `sessions.py`). Data: `data/processed/H08-context-is-the-coupling/G37/` (c9/c8/c2/c3/c10.json). Figure: `figures/c9_offsets.pdf`. pp = percentage points; brackets are day-bootstrap 95% CIs.*

Read-out pairs: 4300 own-room (+ 3772 other-room); in-flight share 85%, wake share 14%.

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| C9-V1 talk jump D_talk (pp) | +3.27 [+1.95, +3.79] | pseudo-message null | pass |
| C9-V2 addressing jump D_addr (pp) | +2.60 [+1.55, +3.10]; floor G_addr(0) +0.28, G_addr(1) +2.88 | | pass |
| A6 pre = G(0) − G(−1), talk / addr (pp) | -0.16 [-1.21, +0.62] / -0.12 [-0.60, +0.02] | ≈ 0 (common cause is flat) | ok |
| C9-V4 G_talk(2) < G_talk(1) | +2.70 vs +3.56 | | pass |
| *post hoc:* recipient did not talk at o = −2, −1 | D_talk +2.53 [+0.76, +3.26]; D_addr +2.29 [+1.40, +2.67]; G_addr(0) +0.21 | | (descriptive) |
| C9-V3 other-room placebo D_talk / D_addr (pp) | +0.84 [-0.02, +1.22] / -0.10 [-0.14, +0.00] | ≈ 0 | pass |
| C9-V5 median read-out delay, active recipients | 35 s (IQR 21–71) | 10–40 s | pass |
| C8 nudge → target, cells | 12; A30 4.04 [0.00, 5.33]; read-out median 106 s; paused at kick 67% | | n/a (< 30 cells) |
| C8-P1 Φ(1,5) measured vs F_hr | 0.64 [-0.28, 1.67] vs 0.51 [0.36, 1.03]; diff 0.13 [-0.83, 1.09] | band [−0.3, +0.1] | descriptive |
| C8-P2 t½ of F_hr | 3.0 min | 3–15 min | pass |
| C8-P4 Φ_ren(1,5) > Φ_obs(1,5) | 0.71 vs 0.51 | | pass |
| C1 | no fetches by the Claude Code agent in this period | | n/a |
| C2-I1 elasticity b (raw) / partial R² | -0.73 [-0.84, -0.61] / 0.026 [0.014, 0.032] | b > 0, R² < 0.05 | fail |
| *post hoc:* b with previous-action control | 0.28 [0.17, 0.34] | | (descriptive) |
| C2-I2 talk ratio / ρ(uncached, latency) | 2.80 [2.61, 2.86] / 0.19 [0.17, 0.21] | > 1.2 / > 0 | pass |
| C3-E1 β_F (forced erasure, pp) / relative | -10.86 [-13.65, -3.78] / -0.38 [-0.48, -0.13] (CF units 357) | < 0; rel ≤ −0.30 | pass |
| C3-E2 β_V (pp) | -7.27 [-9.81, -3.82] | within ±50% of β_F | pass |
| C3-E3 ρ(voluntary segment length, inflow per turn) | 0.14 [-0.31, 0.35] (n = 38) | < 0 | fail |
| C10-L1 slope of log(1 + k) per session hour / ρ | 0.002 [-0.050, 0.079] / -0.037 | > 0 | fail |

**Tests:** T_C9 = pass, T_C8 = n/a, T_C1 = n/a, T_C3 = pass → **supported**.

## Round 1b (improved data, 2026-10-04)
*Re-run on the DQ1 context ledger (`scheme/build_turns_ledger.py`, `analysis/visibility_ledger.py`, `analysis/erasure_ledger.py`): turns are ledger calls, o = 1 is the call that received the message (exact by construction), in-flight = the previous call's first record came after the message. Responses: mention (the pre-registered measure), the DQ2 reply-parent author, and the content cosine of the talk with the message (non-mention). Predictions and the verdict rule unchanged. Data: `data/processed/H08-context-is-the-coupling/r1b/G37/` (`c9.json`, `c3.json`). D in percentage points (cosine ×100), day-bootstrap 95% CIs.*

| Statistic | Round 1 (H08 call-start rule) | Round 1b (ledger) | Note |
| --- | --- | --- | --- |
| D_talk | +3.27 [+1.95, +3.79] | +2.68 [+2.47, +3.09] | pre-registered clause |
| D_addr (mention) | +2.60 [+1.55, +3.10] | +2.50 [+0.83, +3.34] | pre-registered clause |
| D_addr, clean recipients (post hoc) | +2.29 [+1.40, +2.67] | +2.50 [+0.84, +3.32] | no talk at o = −2, −1 |
| D, reply author (new) | — | +3.21 [+1.70, +3.90] | DQ2 `reply_pairs.parent` |
| D, content cosine (new, ×100) | — | +1.74 [-2.84, +9.84] | non-mention response |
| other-room placebo D_addr | — | -0.09 [-0.16, +0.00] | two-room periods only |
| read-out delay of in-flight recipients, median | — | first record 30 s; context assembly 11 s | C9-V5 band 10–40 s |
| C3 / NE41 β_F, forced erasure (pp) | -10.86 [-13.65, -3.78] (mention, H15 catalog) | mention -10.44 [-13.60, -7.49]; **reply author -7.99 [-12.37, -6.46]** (relative -30% [-47, -24]; 539 forced-erased units) | ledger `reset_forced` |

**Verdict (1b): supported** (round 1: supported).

## Scorecard (period-specific axes)
| Axis | This period |
| --- | --- |
| C adequacy | C9 discontinuity vs pseudo-message null: pass |
| E interventional | NE41 forced erasure (exogenous timing): pass |
| D unfitted | read-out turn and the zero-parameter kernel come from turn timing only |

## Round 2 (2026-10-05)
*Predictions: the card's "Round 2" section (written 2026-10-05 02:45 UTC, before any round-2 statistic on real data; amendments R2-A1..A3, R4-A1, R5-A1 written after the synthetic guards, still before real data). Role: replication (R2, R5-b, R5-c), native (R4). Reserved days never read. Data: `data/processed/H08-context-is-the-coupling/r2/`. Content values are cosine ×100; brackets are 95% 1-hour-block bootstrap intervals (R4: day bootstrap).*

| Statistic | This period | Prediction | Note |
| --- | --- | --- | --- |
| R2 read − in-flight content at matched lag, no name and no reply (bge / gte) | +1.79 [-13.93, +5.69] / +5.91 [-9.95, +12.66] | > 0 (CI) in both models | read 812, in flight 40 statement rows |
| R2 same, all statements (bge / gte) | +2.86 [-1.47, +5.07] / +5.98 [+1.58, +8.35] | — (robustness) | 52% of rows name or reply to the sender |
| R2 convergence share κ_c (bge, non-name) | 0.67 | [0.2, 0.6]; synthetic gated-only ≈ 0.73 | κ_c > 1: in-flight statements are closer |
| R2 other-room placebo (bge, non-name) | -0.24 [-2.63, +1.70] | \|Δ_other\| < ⅓ Δ_own, CI at 0 | |
| R5-b log-free monitor: flagged agent-days minus floor (bge / gte, pp) | -0.1 / -0.0 (15 agent-days; longest flagged run 0 / 0) | ≤ 2 pp (regime III) | not a validated detector (R5-P4 failed) |
| R5-c ledger items beyond the 200-event cap | 0.00% of 4054 | < 1% before 06-11; ≤ 5% in G51 | |
| R4 forced-erasure units with the sender newly written to memory | 56% of 531 | descriptive | |
| R4 CF × dose on replies (pp) | -7.97 [-14.83, +2.59] | > 0 pooled | pooled power 0.04 at half protection |
| R4 dose salience β_z on replies (pp) | +9.72 [+0.64, +12.70] | > 0 pooled | |

**Reading:** the round-1b content jump (regime III) is carried by statements that name or reply to the sender; without them, read statements are no closer to the message than in-flight statements at the same lag. The period verdict is unchanged (round 2 adds no period verdict rule).

## Notes
- Card: [`../../README.md`](../../README.md). Data: `data/processed/H08-context-is-the-coupling/G37/`.
