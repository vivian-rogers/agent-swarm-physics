# H19 × NE42: #best and #rest merged (05-04) and split back (05-11) at a fixed roster

**Verdict:** failed
**Role:** native
**Period:** #39 (two rooms) → #40 (one merged room, GPT-5 alone in #rest) → #41 (two rooms): an A-B-A in room size at N = 15 (regime III). Goal-confounded (each week has its own goal; #40 is a shared-objective week).

## Why this period
The only A-B-A change in room size at a fixed roster (DQ9: H19 → NE42). The attention-budget reading of round 1 (each message buys a fixed ~0.07 cross-agent offspring, shared among whoever can see it) and a fixed per-pair coupling make opposite predictions when the room doubles: the budget keeps total cross-triggering per message constant; a per-pair coupling doubles it.

## Prediction
*Written 2026-10-04 06:50 UTC, before any round-1b fit of #39–#41.*
- **N42-a (talk channel, budget per message).** Total fast cross-triggering per TALK event n_x (H03 M3, τ ≤ 300 s) in #40 is between 0.67× and 1.5× the mean of #39 and #41 (a per-pair coupling predicts ≈ 2×). Same direction for g_eq talk.
- **N42-b (activity channel).** The DQ8-trimmed activity gain in #40 is within ±0.07 of the #39/#41 mean (activity co-activation is not room-mediated), while the raw (whole-day) gain in #40 exceeds both neighbours (day-edge synchrony in a coordination week).
- Counts against: n_x in #40 ≥ 1.5× its neighbours (per-pair coupling), or the trimmed activity gain tracking the merge.
- Caveat stated in advance: regime-III fast n_x was near 0 in round 1 (#39 0.009, #40 0.000, #41 0.040), so N42-a may be unpowered.

## Result
*Run 2026-10-04 (round-1b inputs; `analysis/r1b_native.py ne42`, `data/processed/H19-loop-gain-collapse/r1b/native_ne42.json`).*

| | #39 (two rooms) | **#40 (merged)** | #41 (two rooms) | #40 − mean(#39, #41) |
| --- | --- | --- | --- | --- |
| H03 fast n_x, TALK (shift null) | 0.008 (0.006) | **0.000** (0.000) | 0.040 (0.003) | ratio ≈ 0 |
| H03 n̂ TALK | 0.10 | **0.00** | 0.31 | −0.20 |
| g_eq talk | 0.13 ± 0.05 | **0.02 ± 0.06** | 0.20 ± 0.05 | −0.14 |
| g_eq active, raw (whole day) | 0.24 ± 0.03 | **0.43 ± 0.03** | 0.30 ± 0.08 | +0.16 |
| g_eq active, DQ8 trim | −0.05 ± 0.01 | **0.07 ± 0.04** | −0.01 ± 0.06 | +0.11 |
| g_eq active, H38-conditioned | 0.07 ± 0.04 | **0.02 ± 0.03** | 0.14 ± 0.05 | −0.09 |

- **N42-a: failed, but not in the per-pair direction.** In the merged week, talk triggering does not double (per-pair coupling) or stay constant (budget per message): it vanishes. n̂ TALK, fast n_x and the equal-time talk gain are all ≈ 0 in #40 and recover in #41. Neither model predicted this; a backlog effect (every agent sees twice the messages, and fast replies stop) fits it, but #40's shared-objective goal is the confound named in the NE catalog.
- **N42-b: mixed → failed.** The raw activity gain peaks in #40 (as predicted), but the trimmed gain rises by +0.11, outside the ±0.07 band, while the H38-conditioned gain falls by −0.09: the two day-edge adjustments disagree in sign, so the activity channel says nothing robust about room size.
- **Verdict: failed.** The A-B-A does not discriminate the round-1 dilution models; it shows talk triggering switching off in the one-room week.
