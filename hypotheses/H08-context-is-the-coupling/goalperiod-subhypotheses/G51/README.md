# H08 × G51: Each agent: Maximize your assigned goal! (2026-07-06 → 2026-09-04)

**Verdict:** supported
**Verdict (1b):** supported (round 1b, 2026-10-04, context-ledger read-out; C9 talk and addressing jumps both pass on the ledger; round-1 verdict kept above)
**Role:** replication (exploratory)
**Period:** regime III · mode P · N ≈ 21 · #general (+ short side rooms, #focus 08-05 to 08-24) · 45 non-holdout days.

## Why this period
Enough isolated nudges for a per-period kernel (C8); the largest rooms and 8 h days (C10's long sessions); most pauses; perma-computer-use: consolidations every ≤ 41 turns (NE41 erasures, C3) and token accounting (C2).

## Prediction
*Written 2026-10-04 (~02:40 UTC), before running on this period (and before any real-data run of H08). Applies the card's round-1 predictions and amendments A1–A6 (written after the synthetic validation, before real data).*

- **C9-V1/V2 (visibility discontinuity, primary for every period):** among (message, recipient) pairs whose o = 0 turn is in flight, talking and addressing the sender jump at the read-out turn: D_talk = G_talk(1) − G_talk(0) > 0 and D_addr > 0, each with the day-bootstrap 95% CI excluding 0. G_addr(0) > 0 (contaminated floor, H18) but below ½ G_addr(1). A6: pre = G(0) − G(−1) ≈ 0.
- **C9-V4:** G_talk(2) < G_talk(1) (the response sits on the first visible turn).
- **C9-V5:** median read-out delay of in-flight (active) recipients 10–40 s.
- **C8-P1 (HH92, zero-parameter kernel):** nudge → target kernel (H04's design, this period only): the 95% CI of Φ(1,5)_measured − Φ(1,5)_predicted (headroom-weighted read-out CDF F_hr) overlaps [−0.3, +0.1].
- **C8-P2:** F_hr(observed read-out) reaches half its 45-min value between 3 and 15 min.
- **C8-P3:** in 100 day-split CVs the best context-family model beats the best immediate, constant-delay and Hawkes models each in ≥ 60% of splits, with median SSE ≤ 1.1 × the gamma ceiling.
- **C8-P4:** the renewal prediction (no kick information) has a faster onset than the observed-read-out one (Φ_ren(1,5) > Φ_obs(1,5)).
- **C8-P5 (pause-matched):** the early response (mean G over τ = 1–5) is larger for kicks to non-paused agents than for kicks to agents with ≥ 5 min of declared pause left (CI of the difference excludes 0). Expected caveat from the synthetic #51 skeletons: idle agents' read-outs are often > 60 min away, so the kernel may be small.
- **C2-I1/I2:** within agent-days, log uncached tokens rise with log(1 + new room messages) (b > 0, CI excluding 0) but messages explain little (partial R² < 0.05); P(talk | ≥ 1 new message) / P(talk | 0) > 1.2; ρ(uncached, call latency) > 0.
- **C3-E1/E2 (NE41):** where ≥ 300 erased units, addressing an old sender whose message was read before a forced consolidation falls relative to old senders read after it (β_F < 0, CI excluding 0; relative drop ≥ 30%); β_V within ±50% of β_F. **E3:** voluntary segments shorter when inflow per turn is higher (ρ < 0).
- **C10-L1 (HH91 as stated):** backlog k per talk turn rises with session hour (ρ > 0; within-agent-day slope CI > 0). **L2:** Hawkes n̂ is higher in the second half of the day (Δn̂ > 0, CI excluding 0). **L3:** across weeks, ρ(n̂, mean k) > 0.

**Verdict rule (fixed now).** Tests: T_C9 = V1 and V2 both pass; T_C8 (powered periods) = P1 band and P3 both hold → pass, Φ outside the band or a rival family winning ≥ 60% → fail, else inconclusive; T_C3 (≥ 300 forced-erased units) = β_F < 0 with CI excluding 0 → pass, β_F > 0 with CI excluding 0 → fail, else inconclusive; T_C1 = recall ≥ 0.9 and (two rooms) other-room coverage ≤ 5% → pass, recall < 0.7 or other-room coverage > 20% → fail. **supported** = T_C9 passes and no other test fails; **failed** = T_C9 fails; **mixed** = T_C9 passes and another test fails. C2, C10 and the secondary items are reported but do not set the verdict.

## Result
*Run 2026-10-04 (`analysis/visibility.py`, `kernels.py`, `cc_exposure.py`, `inflow.py`, `erasure.py`, `sessions.py`). Data: `data/processed/H08-context-is-the-coupling/G51/` (c9/c8/c2/c3/c10.json). Figure: `figures/c9_offsets.pdf`. pp = percentage points; brackets are day-bootstrap 95% CIs.*

Read-out pairs: 951633 own-room (+ 0 other-room); in-flight share 72%, wake share 28%.

| Prediction | Observed | Null / rival | Verdict |
| --- | --- | --- | --- |
| C9-V1 talk jump D_talk (pp) | +0.61 [+0.47, +0.74] | pseudo-message null | pass |
| C9-V2 addressing jump D_addr (pp) | +0.68 [+0.60, +0.75]; floor G_addr(0) +0.08, G_addr(1) +0.76 | | pass |
| A6 pre = G(0) − G(−1), talk / addr (pp) | -0.28 [-0.43, -0.14] / -0.20 [-0.24, -0.15] | ≈ 0 (common cause is flat) | not ≈ 0 |
| C9-V4 G_talk(2) < G_talk(1) | +0.27 vs +0.77 | | pass |
| *post hoc:* recipient did not talk at o = −2, −1 | D_talk +0.50 [+0.38, +0.64]; D_addr +0.47 [+0.42, +0.54]; G_addr(0) +0.07 | | (descriptive) |
| C9-V5 median read-out delay, active recipients | 45 s (IQR 22–137) | 10–40 s | fail |
| C8 nudge → target, cells | 303; A30 1.66 [0.79, 2.41]; read-out median 104 s; paused at kick 68% | | inconclusive |
| C8-P1 Φ(1,5) measured vs F_hr | 0.03 [-0.83, 0.57] vs 0.52 [0.48, 0.57]; diff -0.50 [-1.37, 0.01] | band [−0.3, +0.1] | consistent |
| C8-P2 t½ of F_hr | 3.0 min | 3–15 min | pass |
| C8-P4 Φ_ren(1,5) > Φ_obs(1,5) | 0.57 vs 0.52 | | pass |
| C8-P3 day-split CV (100 splits) | best: ctx 0.27, delay 0.26, gamma 0.24; ctx beats imm 0.77, delay 0.41, Hawkes 0.80; gamma/ctx SSE 0.97 | ≥ 0.60 each | fail |
| C8-P5 early response, not paused − paused ≥ 5 min | -0.024 [-0.088, 0.047] (n = 98 / 42) | > 0 | fail |
| C2-I1 elasticity b (raw) / partial R² | -0.13 [-0.16, -0.10] / 0.002 [0.001, 0.003] | b > 0, R² < 0.05 | fail |
| *post hoc:* b with previous-action control | 0.60 [0.55, 0.65] | | (descriptive) |
| C2-I2 talk ratio / ρ(uncached, latency) | 1.44 [1.37, 1.50] / 0.13 [0.12, 0.14] | > 1.2 / > 0 | pass |
| C3-E1 β_F (forced erasure, pp) / relative | -1.74 [-2.00, -1.50] / -0.21 [-0.25, -0.18] (CF units 62966) | < 0; rel ≤ −0.30 | pass |
| C3-E2 β_V (pp) | -1.94 [-2.26, -1.62] | within ±50% of β_F | pass |
| C3-E3 ρ(voluntary segment length, inflow per turn) | -0.11 [-0.15, -0.07] (n = 3613) | < 0 | pass |
| C10-L1 slope of log(1 + k) per session hour / ρ | 0.018 [0.010, 0.025] / +0.040 | > 0 | pass |
| C10-L2 Hawkes n̂ second − first half | 0.702 − 0.504 = 0.198 [0.102, 0.293] | > 0 | pass |
| C10-L3 weeks: ρ(n̂, mean k) | +0.62 (9 weeks) | > 0 | pass |

**Tests:** T_C9 = pass, T_C8 = inconclusive, T_C3 = pass → **supported**.

## Round 1b (improved data, 2026-10-04)
*Re-run on the DQ1 context ledger (`scheme/build_turns_ledger.py`, `analysis/visibility_ledger.py`, `analysis/erasure_ledger.py`): turns are ledger calls, o = 1 is the call that received the message (exact by construction), in-flight = the previous call's first record came after the message. Responses: mention (the pre-registered measure), the DQ2 reply-parent author, and the content cosine of the talk with the message (non-mention). Predictions and the verdict rule unchanged. Data: `data/processed/H08-context-is-the-coupling/r1b/G51/` (`c9.json`, `c3.json`). D in percentage points (cosine ×100), day-bootstrap 95% CIs.*

| Statistic | Round 1 (H08 call-start rule) | Round 1b (ledger) | Note |
| --- | --- | --- | --- |
| D_talk | +0.61 [+0.47, +0.74] | +0.69 [+0.53, +0.89] | pre-registered clause |
| D_addr (mention) | +0.68 [+0.60, +0.75] | +0.81 [+0.71, +0.91] | pre-registered clause |
| D_addr, clean recipients (post hoc) | +0.47 [+0.42, +0.54] | +0.55 [+0.49, +0.63] | no talk at o = −2, −1 |
| D, reply author (new) | — | +0.93 [+0.85, +1.03] | DQ2 `reply_pairs.parent` |
| D, content cosine (new, ×100) | — | +1.99 [+1.68, +2.35] | non-mention response |
| other-room placebo D_addr | — | — | two-room periods only |
| read-out delay of in-flight recipients, median | — | first record 33 s; context assembly 14 s | C9-V5 band 10–40 s |
| C3 / NE41 β_F, forced erasure (pp) | -1.74 [-2.00, -1.50] (mention, H15 catalog) | mention -1.60 [-1.87, -1.34]; **reply author -1.69 [-1.94, -1.42]** (relative -33% [-37, -27]; 91862 forced-erased units) | ledger `reset_forced` |

**Verdict (1b): supported** (round 1: supported).

## Scorecard (period-specific axes)
| Axis | This period |
| --- | --- |
| C adequacy | C9 discontinuity vs pseudo-message null: pass; C8 CV vs rivals: inconclusive |
| E interventional | NE41 forced erasure (exogenous timing): pass |
| D unfitted | read-out turn and the zero-parameter kernel come from turn timing only |

## Round 2 (2026-10-05)
*Predictions: the card's "Round 2" section (written 2026-10-05 02:45 UTC, before any round-2 statistic on real data; amendments R2-A1..A3, R4-A1, R5-A1 written after the synthetic guards, still before real data). Role: replication (R2, R5-b, R5-c), native (R4). Reserved days never read. Data: `data/processed/H08-context-is-the-coupling/r2/`. Content values are cosine ×100; brackets are 95% 1-hour-block bootstrap intervals (R4: day bootstrap).*

| Statistic | This period | Prediction | Note |
| --- | --- | --- | --- |
| R2 read − in-flight content at matched lag, no name and no reply (bge / gte) | -0.39 [-0.62, -0.12] / -0.15 [-0.39, +0.11] | > 0 (CI) in both models | read 257734, in flight 9967 statement rows |
| R2 same, all statements (bge / gte) | +1.25 [+0.98, +1.60] / +1.83 [+1.56, +2.19] | — (robustness) | 19% of rows name or reply to the sender |
| R2 convergence share κ_c (bge, non-name) | 1.68 | [0.2, 0.6]; synthetic gated-only ≈ 0.73 | κ_c > 1: in-flight statements are closer |
| R5-b log-free monitor: flagged agent-days minus floor (bge / gte, pp) | +9.6 / +10.7 (736 agent-days; longest flagged run 13 / 13) | ≤ 2 pp (regime III) | not a validated detector (R5-P4 failed) |
| R5-c ledger items beyond the 200-event cap | 3.65% of 930422 | < 1% before 06-11; ≤ 5% in G51 | |
| R4 forced-erasure units with the sender newly written to memory | 48% of 90959 | descriptive | |
| R4 CF × dose on replies (pp) | -0.64 [-0.95, -0.28] | > 0 pooled | pooled power 0.04 at half protection |
| R4 dose salience β_z on replies (pp) | +5.84 [+4.99, +6.70] | > 0 pooled | |

**Reading:** the round-1b content jump (regime III) is carried by statements that name or reply to the sender; without them, read statements are no closer to the message than in-flight statements at the same lag. The period verdict is unchanged (round 2 adds no period verdict rule).

## Notes
- Card: [`../../README.md`](../../README.md). Data: `data/processed/H08-context-is-the-coupling/G51/`.
