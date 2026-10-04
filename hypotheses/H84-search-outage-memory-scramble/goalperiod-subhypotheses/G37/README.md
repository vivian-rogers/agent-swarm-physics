# H84 × G37: the history-search outage (2026-03-31, 04-01; recovery 04-02, 04-03)

**Verdict:** failed
**Role:** native (exploratory)
**Period:** regime III · 12 agents · goal #37 (03-30 → 04-01; unit 37) plus recovery days 04-02/03 (#38a). Placebo days: regime-III non-holdout weekdays 03-24 → 05-29 (#36b–#42, #44).

## Why this period
The only non-holdout window in which the history-search oracle failed for whole days (median answers 383 and 42 characters vs 1.4–3 k; 85–98 searches a day). It is an involuntary degradation of one channel, with each agent's exposure set by its pre-outage search dose.

## Prediction
*Written 2026-10-04 ~20:05 UTC, before any outcome statistic.* The card's P1–P5:
- **P1** β_V1 < 0 (continuity share falls with search dose on outage days); placebo rank p ≤ 0.10 among all and kickoff-matched pairs; ≥ 0.10 drop at the mean searcher dose.
- **P2** recovery β_rec(V1) inside the central 80% of placebo β.
- **P3** duplicates up (β_V2 > 0), earlier-goal references down (β_V3 < 0), each beyond the placebo 80th/20th percentile.
- **P4** first stage: each searcher's outage-day median answer < 25% of its pre-outage median; searches per 100 calls rise.
- **P5** own-artifact re-reads per 100 calls rise with dose (β > 0; R1 substitution).
- *Counts against:* β_V1 ≥ 0 or inside the central 80% of placebos. Verdict: supported (P1 and P2), failed (P1 fails with power ≥ 0.8 at a 0.20 dip), inconclusive (P1 fails with power < 0.8), mixed otherwise.

## Result
*Run 2026-10-04 20:20 UTC (`analysis/run.py` → `data/processed/H84-search-outage-memory-scramble/results/results.json`); post-hoc single-agent check 20:25 UTC (`analysis/posthoc_single_agent.py`).*

**First stage (P4): the scramble reached one agent.** The top-dose agent (code 17, dose 2.0 searches per 100 calls) had its median answer fall from 2,880 to 42 characters, and its search rate rose from 2.0 to 8.8 per 100 calls (128 retries). The second searcher's answers halved (1,516 → 683 characters; rate 0.84 → 0.93). The third did not search on outage days. P4 holds for one of three searchers.

| Prediction | Observed (β per search per 100 calls; effect at d̄_s = 1.05) | Placebo (38 pairs; 5 kickoff-matched) | Verdict |
| --- | --- | --- | --- |
| P1 V1 continuity falls with dose | β = +0.12 (effect +0.13); share 0.80 for searchers on other days | rank p (dip) 0.87; central 80% [−0.16, +0.13]; above all 5 kickoff-matched | fail |
| P2 recovery inside placebo central 80% | β_rec = +0.24 (above q90) | — | fail (wrong side) |
| P3 V2 duplicates up | β = −0.004 (13 duplicates in the whole panel) | rank p 0.13 | fail (unpowered) |
| P3 V3 earlier-goal refs down | β = +0.16 (effect +0.17) | the largest of 38 (p for a dip 1.0) | fail (opposite) |
| R3 V4 commits per 20 calls | β = +0.03 (effect +0.03 ± 0.51) | rank p 0.56 | null |
| P4 first stage | 1 of 3 searchers degraded; search rate β = +2.5 (dose perm p 0.046; rank p 0.10) | — | partial |
| P5 own-artifact re-reads up | β = +6.4 per 100 calls (dose perm p 0.048; rank p 0.23); without agent 17: +1.1 | — | partial |

- **Leave-one-agent-out:** β_V1 stays in [+0.10, +0.26]; β_V3 in [+0.10, +0.37]. Dropping agent 17 raises both, so the positive sign does not come from the scrambled agent; it comes from the two partly reached searchers.
- **Variants:** commit-weighted β_V1 +0.13; binary searcher dose +0.16.
- **Post hoc, single-agent ITS (agent 17; agent and day fixed effects fitted on non-outage days):** V1 residual +0.19 on outage days (placebo 10–90% [−0.22, +0.16], p 0.43); V3 +0.22 (p 0.026) but +0.31 on the recovery days; commits per 20 calls +0.10 (p 0.77); search rate +5.8 per 100 calls (p 0.08); re-reads +13.7 (p 0.18) and +12.9 on recovery days.
- **Power (synthetic, Amendment A1):** V1 power 0.85–0.91 at a 0.30 dip at d̄_s; the observed β is +0.12, so a dose-proportional dip of 0.30 is excluded at the placebo spread (SD × d̄_s = 0.15). A 0.20 dip is not excluded at power ≥ 0.8.

**Reading.** Losing history search for two days cost the scrambled agent no continuity and no output. The agent retried and re-read its own artifacts more, and referenced earlier-goal artifacts more, but these rises persist into the recovery days and so are not specific to the outage. The verdict is *failed* under the pre-registered rule as amended (A1), scoped to "no dose-proportional V1 dip ≥ 0.30 at the mean searcher dose". The scope is narrow: one fully scrambled agent and two days.

**Replication point (I_Q at G37 search calls):** 0.015 bits [−0.029, +0.054], p 0.38, n 139 (most answers are empty outage answers, so the pointer is mostly "none").

## Scorecard (period-specific axes)
- **E (interventional):** the outage is an involuntary scramble with pre-set dose; the predicted dip did not occur (scope: one agent fully reached).
- **F:** power from the synthetic at real counts (A1); kickoff-matched placebos limited to 5 pairs (min p 0.17).
- **C:** placebo pairs and dose permutation are the null hierarchy; no outcome beats them in the predicted direction.
