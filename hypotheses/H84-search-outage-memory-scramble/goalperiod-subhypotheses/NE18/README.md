# H84 × NE18: search rework (verbatim segments, 10-day window) and answerer swap (2026-04-20, inside #38)

**Verdict:** mixed (inconclusive: no first stage; power under 0.8)
**Role:** native (exploratory)
**Period:** regime III · goal #38 (04-02 → 04-24; units 38a–38e) · pre days 04-06 → 04-17, post days 04-20 → 04-24. Agents: those active on ≥ 3 pre days (later joiners excluded). Same-day change: NE40 (answerer Gemini 2.5 Pro → Sonnet 4.6, dated by H56).

## Why this period
The opposite intervention to the outage: the search channel gained fidelity (verbatim transcript segments, a 10-day window). If search carries semantic information, continuity should rise for searchers. The test is inside one goal period, so the goal field is fixed.

## Prediction
*Written 2026-10-04 ~20:07 UTC, before any outcome statistic.*
- Dose d_a = search calls per 100 ledger calls on 04-06 → 04-17. Model y_{a,t} = α_a + γ_t + β · d_a · Post_t (V1–V4 as in the card).
- **Q1 (KW symmetry):** β_V1 > 0, placebo rank p ≤ 0.10 among placebo boundaries (every other Monday 04-06 → 05-18, five-day post window, the same dose).
- **Q2 first stage:** median answer length per searcher rises after 04-20, and searches per 100 calls do not fall.
- **Q3 joint with G37:** sign(β_NE18) = −sign(β_G37) for V1.
- *Counts against:* β_V1 ≤ 0 or inside the central 80% of placebo boundaries. Same power rule as G37 (synthetic power at a +0.20 shift); NE17 (04-14 outreach approval) sits in the pre window and is a known confound for outreach-heavy agents.

## Result
*Run 2026-10-04 20:20 UTC (`analysis/run.py`, NE18 block).*

**First stage: the change did not reach the searchers as an improvement.** Dose window 04-06 → 04-17: two searchers (dose 1.69 and 0.99; d̄_s 1.34). After 04-20 the top searcher nearly stopped searching (91 → 2 searches), and the other's median answer fell (2,346 → 1,459 characters). So NE18 + NE40 did not raise the fidelity the searchers received.

| Prediction | Observed (β per search per 100 calls) | Placebo (17 boundaries) | Verdict |
| --- | --- | --- | --- |
| Q1 V1 rises with dose after 04-20 | β = +0.055 (effect +0.07 at d̄_s) | rank p 0.11 (A3 needs ≤ 0.05); placebo 10–90% [−0.20, −0.01] | fail |
| Q1 V3 | β = +0.042 | rank p 0.056 | fail (A3) |
| V4 commits per 20 calls | β = +0.32 | rank p 0.44 | null |
| Q2 first stage | answers shorter, searches −0.63 per 100 calls per dose (rank p for a rise 0.94) | — | fail |
| Q3 sign(NE18) = −sign(G37) for V1 | both positive | — | fail |

**Reading.** The search rework did not raise the searchers' answer length or use, so it is not the opposite scramble the design needed. The V1 and V3 rises sit at the edge of an oversized test (synthetic size 0.12–0.22) whose placebo boundaries are all negative (a slow drift in the searchers' continuity). Verdict *inconclusive*: no first stage and power 0.46–0.65 at a 0.20 shift.

## Scorecard (period-specific axes)
- **E:** no first stage, so not an intervention on the channel's fidelity as measured.
- **F:** oversized (A3) and underpowered.
