# H34 × G26: Elect a village leader. They choose this week’s goal! (2026-01-05 → 2026-01-12)

**Verdict:** mixed
**Verdict (1b):** failed (native: elected-leader seeds spread less, P(s≥2) ratio 0.36 [0.27, 0.46]; replication mixed, HR₁₀ 12.3)
**Role:** native (round 1b: the elected leader as idea seeder, DQ6; round 1: exploratory)
**Period:** regime I · mode C · 10 agents at start (median room size 10) · 5 non-holdout days. Setup: Elect a leader who picks the week's goal. Ballot failure, then chat approval voting with a three-way tie (DeepSeek-V3.2, Claude 3.7 Sonnet, Gemini 2.5 Pro at 9 each). DeepSeek-V3.2 won the runoff 7–1 and set an interactive-fiction game as the goal. That goal is not in `village_goals`.

## Why this period
Secondary period for the cross-period criticality link (P4) and transfer of the forecast rule (P7). Mode C (shared objective), regime I.

## Prediction
*Written 2026-10-04 02:00 UTC, before running on this period* (after the synthetic validation and amendments A1–A5 of the main card; no real cascade statistic had been computed for any period).

| # | Prediction here | Counts against |
| --- | --- | --- |
| P1 | R̂ < 1 with upper 95% CI < 1; typical 0.05–0.5 | lower CI ≥ 1 |
| P2 | R̂ < H03 n̂_talk = 0.56; R_c < R̂ | R̂ > n̂_talk beyond its CI |
| P3a (A1) | observed P(s ≥ 3) and P(s ≥ 5) inside the FN-GW 90% band (if ≥ 50 trees) | outside the band |
| P5 (A2) | contagion beyond the field: HR₁₀ > 1 with lower CI > 1 | HR₁₀ CI includes 1 or < 1 |
| P6 (A3) | pooled recency HR(2 vs 1) ≤ 2.5 (not complex) | HR(2 vs 1) > 3 with lower CI > 2.5 |

**Verdict rule (A2):** supported = P5 (HR₁₀ lower CI > 1) and P3a pass; failed = both fail, or R̂ lower CI ≥ 1; mixed = exactly one passes; n/a = fewer than 20 non-seed agent first uses (or < 50 trees for P3a, which then counts as not tested and the verdict rests on P5: supported → mixed at best).

## Result
**mixed.** 2271 ideas, 3089 agent first uses, 2343 trees, N_room 10; R̂ = 0.242, contagion share R_c = 0.181, HR₁₀ = 4.01; P(s ≥ 2) = 0.144, largest tree 10.

| Prediction | Observed | Null / reference | Verdict |
| --- | --- | --- | --- |
| P1 R̂ < 1 (upper CI < 1) | R̂ = 0.242 [0.219, 0.265] | critical R = 1 | pass |
| P2 R̂ < H03 n̂_talk | R̂ 0.242 vs n̂ 0.56; R_c = 0.181 | HH108: R̂ > n̂ | pass |
| P3a FN-GW band covers P(s ≥ 3), P(s ≥ 5) | P(s≥3) 0.073 (band 0.054–0.085); P(s≥5) 0.024 (band 0.006–0.017) | GW-NB band covers both: no | fail (s≥5 heavier than FN-GW) |
| P3b pure s^−3/2 rejected; τ_app ≥ 2 | LR 1320.5; τ_app 3.02 | critical branching | pass |
| P5 HR₁₀ > 1, lower CI > 1 (A2) | HR₁₀ = 4.01 [3.32, 4.83] (138 adoptions at k = 0) | field: HR₁₀ ≤ 1 | pass |
| P5a jitter excess (pre-registered; failed guard) | exposed 0.912 vs null 0.985, p = 1.00 | uninterpretable (S2) | n/a |
| P6 pooled HR(2 vs 1) ≤ 2.5 | 5.96 [4.60, 7.66] | complex > 3; heterogeneity inflates | ambiguous |
| P7 day-ahead 90% PI coverage (pre-registered FN-GW) | P(s≥2) 0.75, P(s≥3) 0.75 over 4 days | post-hoc V3: 0.75, 1.00 | fail |

**By idea class** (U artifact, D number, N name/coinage, W rare word):

| Class | ideas | agent nodes | R̂ [95% CI] | R_c | P(s ≥ 2) | P(s ≥ 3) | s_max |
| --- | --- | --- | --- | --- | --- | --- | --- |
| D | 77 | 137 | 0.39 [0.25, 0.49] | 0.25 | 0.238 | 0.131 | 9 |
| N | 2121 | 2825 | 0.23 [0.20, 0.25] | 0.17 | 0.134 | 0.067 | 10 |
| U | 46 | 90 | 0.42 [0.32, 0.50] | 0.35 | 0.423 | 0.212 | 5 |
| W | 27 | 37 | 0.27 [0.04, 0.45] | 0.16 | 0.148 | 0.074 | 5 |

Data: `data/processed/H34-idea-cascades/G26/`. Figures: `../../figures/` (cross-period); numbers from `analysis/explore.py` → `results/periods.json`.

## Scorecard (period-specific axes)
C (adequacy): HR₁₀ beats the field null (lower CI 3.32). D (unfitted shape): FN-GW band misses the tail; pure s^−3/2 rejected. E: no natural experiment inside this period was used.

## Notes
- Censoring check: R̂ without trees rooted on the last day = 0.241.
- Root vs non-root mean offspring 0.184 vs 0.424 (GW assumes equal).
- Root types: invented 0.97, from humans 0.000, field (unexposed) 0.031; 0.91 of non-seed first uses were visibly exposed.

## Round 1b native: is the elected leader an idea source? (DQ6)
*Prediction written 2026-10-04 16:50 UTC, before running.* **Seen beforehand:** round 1 for this period (above) and the card; DQ6's `ground_truth_labels` rows (leader terms and lead designers; codes and times only); H29's round-1b native summary (#35: designated leaders get 1.4x more replies per message; #26: the elected leader's broadcast pull rose most); H32's round-1 finding that formal leaders are not content sources. No round-1b H34 statistic (ledger trees, any idea split by seeder) had been computed.

**Design.** DeepSeek-V3.2 (agent 17), elected 01-05 19:35:22 UTC (term 1, to 01-09 19:00:43; term 2 to the end of the period). Window = both terms (non-holdout days). Trees from the round-1b build (context-ledger visibility: j's first use is *exposed* if an earlier use reached one of j's receiving calls before the call that produced j's use). For each idea whose **seed** (first use in the period) falls in the window, the seed's tree size s (agents reached through visible exposure). Statistic: the ratio of P(s ≥ 2) for leader-seeded ideas to that for ideas seeded by other agents in the same room and window, with an idea-bootstrap 95% CI (2,000 draws); mean s as a secondary.

**Predictions:**
- **N26a:** no leader premium: the P(s ≥ 2) ratio's 95% CI includes 1 [0.55].
- **N26b:** the leader seeds no more ideas per message than the other agents (ideas seeded / agent messages within ±25% of the others' pooled rate) [0.5].

**Verdict rule (H34 here):** *supported* (the leader is an idea source) if the ratio > 1 with CI excluding 1; *failed* if the CI includes 1 or the ratio < 1; descriptive N26b.

### Result (round 1b, run 2026-10-04)
`analysis/r1b_natives.py natives` → `data/processed/H34-idea-cascades/r1b/results/natives.json`.

| Test | Observed | Prediction | Verdict |
| --- | --- | --- | --- |
| N26a P(s ≥ 2), DeepSeek-seeded / other-seeded, from 01-05 19:35 UTC (863 vs 1,263 seeds) | **0.36 [0.27, 0.46]**; P(s ≥ 2) 0.07 vs 0.21; mean size 1.16 vs 1.46 | CI includes 1 | **failed** (significantly *below* 1) |
| N26b ideas seeded per agent message | DeepSeek 5.46 vs others 0.73 (**×7.5**) | within ±25% | **failed** |

**Reading.** The elected leader introduced far more new markers per message than anyone else (long, term-dense messages: its goal announcement and plans), and each of them was far less likely to be picked up. Leadership here is a high-volume, low-uptake source of new terms. This matches H32 (the leader is not a content source) and the reading that the pooled R̂ averages over very unequal seeders.

**Verdict (H34 here):** failed (the elected leader is not an idea source in the branching sense).
