# H52 × G04: within-call contrast in the 2025 public chat (2025-05-15 → 2025-06-18)

**Verdict:** mixed — reply +0.025*, content +0.012 (boundary +0.05*); within-call n.s.
**Role:** native
**Period:** regime I · 4 agents · one public room · 25 active days (period units 4a–4d split at roster swaps and a 300-min outage; absorbed by day fixed effects and by the within-call design). Human messages: 1,724 non-kickoff messages from the viewing public (6,645 message × recipient rows).

## Why this period
The only period where human messages are dense enough that the same receiving call often holds both a human and an agent message (2,495 calls). Within one call the recipient, its state, the read-out moment, the room and the post-call statement are identical by construction, so the contrast "which of the two messages did the recipient move toward / answer?" removes every call-level confounder. The remaining differences (novelty, length, read-out age) are adjusted by regression on within-pair differences. The replication estimator is also run here (numbers below).

## Prediction
*Written 2026-10-04 ~06:10 UTC (card, native N1), before running on this period.*
- **Content:** within calls, the recipient's DiD content pull toward the human message minus toward the agent message (same named status; adjusted for novelty, log length, log age differences) is ≤ 0 (credence 0.6): in public chat, agents' work follows agents. H52 predicts ≈ 0.
- **Reply choice:** among pairs where exactly one of the two becomes the parent of the recipient's reply, the adjusted odds favour the human message (> 1; credence 0.55): *humans get answers, not influence*. H52 predicts odds ≈ 1.
- Counts against my expectation: a content difference > 0 with CI excluding 0. Counts against H52: either contrast with CI excluding 0.
- Caveat known before the run (synthetic, Amendment A1): with dense co-arriving messages the shared post-call statement spreads a human message's pull onto agent messages of the same call, so within-call content contrasts are attenuated toward 0.

## Result
In the verdict line, * marks a 95% CI that excludes 0.

**Native N1 (within-call contrast)** (`native/n1_G04_within_call.json`; day-block bootstrap, 1000 draws, each call weighted equally). 2,180 receiving calls hold at least one human and one agent message of the same named status (38,166 pairs; 99% unnamed).

| Contrast | Observed | H52 / expectation | Verdict |
| --- | --- | --- | --- |
| content: DiD χ(human) − χ(agent), same call | raw −0.034 [−0.066, 0.002]; adjusted for novelty, log length, log age differences −0.006 [−0.024, 0.014] (9,000 pairs, 2,076 calls); novelty difference carries the raw gap (slope 0.31) | H52 ≈ 0 ✓; expectation ≤ 0 ✓ | consistent with no premium, but attenuated toward 0 by co-arrival spillover (synthetic, A1) |
| reply choice: which of the two becomes the parent | raw P(human chosen) 0.33 (631 discordant pairs, 373 calls); adjusted log-odds +0.40 [−0.12, 1.02], odds 1.49 | H52: odds 1; expectation > 1 | inconclusive (direction as expected) |

**Replication estimator** (`G04/results.json`; 1,692 human messages, 6,061 content rows; powered):

| Outcome | Human premium [95% CI] | Naive | Agent naming effect | Note |
| --- | --- | --- | --- | --- |
| content (DiD χ) | +0.012 [−0.001, 0.024] | +0.013 | −0.018 | gte +0.013 [0.003, 0.024]; style-residualized +0.012 [0.002, 0.021]; joint deconvolution +0.019 [0.010, 0.028]; H30 orthogonalized +0.015 [−0.000, 0.028]; **H29 boundary design human − agent jump (unnamed) +0.052 [0.027, 0.074]**; named human rows +0.069 [0.011, 0.108]. Regime-I DiD carries a synthetic null bias of about −0.024, so the true premium is likely larger |
| reply | +0.025 [0.001, 0.047] (matched agent rate 0.035) | **−0.030** | +0.081 | matching flips the sign: viewers rarely name agents (5% vs 19% of agent items), and naming drives replies; named human messages +0.152 [0.010, 0.268] |
| activity (BC) | +0.17 [−0.44, 0.74] | +0.16 | +0.10 | equivalent to 0 within ±0.5 min? no (CI too wide); inconclusive |
| stance | +0.074 [0.002, 0.128] | +0.081 | −0.107 | replies to viewers are more supportive (aggregate; Jev is told the author is "a human viewer") |

Reading: in the 2025 public chat, agents answer viewers' messages about 1.7× as often as comparable agent messages, reply more supportively, and move a little toward what viewers add (content premium ≈ +0.01 to +0.05 depending on the statistic, all ≥ 0). Within a single call, the recipient's choice between a human and an agent message is not detectably tilted once novelty and length are adjusted. The within-call design is attenuated by spillover through the shared post-call statement. My expectation that "humans get answers, not influence" is half right: answers yes; influence small but not zero.

## Scorecard (period-specific axes)
- C: reply and stance premia beat the matched-agent null (day-block CIs > 0); content only with the boundary, gte, style-residualized and joint statistics.
- D: the H29 boundary design (an independent statistic, not fitted) agrees in sign with the DiD premium.
- F: synthetic G04 skeleton: reply and stance recovered; DiD content biased about −0.024 (A1).

## Notes
- 2026-10-04: native test N1; script `analysis/native.py n1`; data `data/processed/H52-humans-loud-agents/native/n1_G04_within_call.json`.
