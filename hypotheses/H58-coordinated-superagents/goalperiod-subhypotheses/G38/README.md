# H58 × G38: Charity fundraiser, year 2 (2026-04-02 → 2026-04-24)

**Verdict:** n/a
**Role:** replication
**Period:** regime III · units 38a, 38b, 38c · 17 non-holdout days. Units are H01 round 2's (card F1).

## Why this period
Layer 1 (replication): it has a dense work ledger (DQ4 agent work commits), so the allocation state (which artifact each agent advances per 30-min bin), the coordination layers and the decision rule can be computed as on every other eligible period, giving one comparable point.

## Prediction
*Written 2026-10-04, before the replication run on this period (templated, per the two-layer rule; after amendments A1 and A2).* The card's P1–P3 applied here: at least one coordination-defined unit (multi-layer community or calibrated search result) is an effective-superagent candidate (g > 0, z_spec ≥ 2, z_shift ≥ 2, specificity ≥ 0.5, testable against an outside reference; search p ≤ 0.05); multi-layer communities rank above rooms and labs; candidates may span rooms. Synthetic power to see a planted store of strength ρ = 0.5 here: **38a 0.35, 38b 0.00, 38c 0.05** (a null here is 'not identifiable', A2.1). My prior for this period: 38a: no candidate; charity pages are mostly individual. 38b: no candidate. 38c: no candidate.

## Result
Data: `data/processed/H58-coordinated-superagents/results/` (units/*.json, replication.json, natives.json, reacq.json); pipeline `analysis/run.py`, `natives.py`, `reacq.py`.

### Unit 38a
- 12 committing agents, 71 bins, 8 days, 670 agent work commits; synthetic power at ρ = 0.5: 0.35.

| candidate | members | g (bits / working member-bin) | z_spec | z_shift | specificity | qualifies |
| --- | --- | --- | --- | --- | --- | --- |
| search (search p 0.15) | 5: Claude Sonnet 4.5, Claude Haiku 4.5, GPT-5.1, Claude Opus 4.5, DeepSeek-V3.2 | +0.498 | +4.3 | +1.8 | -0.04 | no |
| multi-layer community | 4: Claude Opus 4.6, Claude Sonnet 4.6, Gemini 3.1 Pro, GPT-5.4 | -0.155 | -3.0 | -0.9 | – | no |
| multi-layer community | 8: Gemini 2.5 Pro, GPT-5, Claude Sonnet 4.5, Claude Haiku 4.5, GPT-5.1, Claude Opus 4.5, DeepSeek-V3.2, GPT-5.2 | +0.256 | – | +1.4 | +1.00 | no (untestable) |
| room | 8: Gemini 2.5 Pro, GPT-5, Claude Sonnet 4.5, Claude Haiku 4.5, GPT-5.1, Claude Opus 4.5, DeepSeek-V3.2, GPT-5.2 | +0.256 | – | +1.5 | +1.00 | no (untestable) |
| room | 4: Claude Opus 4.6, Claude Sonnet 4.6, Gemini 3.1 Pro, GPT-5.4 | -0.155 | -2.4 | -0.7 | – | no |
| lab | 2: Gemini 2.5 Pro, Gemini 3.1 Pro | – | – | – | – | no (untestable) |
| lab | 4: GPT-5, GPT-5.1, GPT-5.2, GPT-5.4 | -0.019 | -1.1 | +0.6 | – | no |
| lab | 5: Claude Sonnet 4.5, Claude Haiku 4.5, Claude Opus 4.5, Claude Opus 4.6, Claude Sonnet 4.6 | +0.000 | – | – | – | no (untestable) |

- Single-layer communities and joint-work crews qualifying: sync 0/4, coad 0/2, reply 0/2, coart 0/2, crew 1/10.
- Search result: lagged gain (transfer entropy) +0.201, content gain -0.003, night gain -0.094 (z -2.0); unit individuality ι +0.251 vs aggregation baseline +0.204 (z +0.8), members as agent + own artifact +0.148.
- Attraction diagnostic (A3, post hoc) for the crew unit of 2: 2 joins of 2 moves vs +1.1 expected under agent + own artifacts (ratio +1.84).
- Attraction diagnostic (A3, post hoc) for the search unit of 5: 11 joins of 18 moves vs +4.6 expected under agent + own artifacts (ratio +2.41).
- Agent + own artifact (singletons): median ι +0.047, median colonial (persistence) +0.051 bits.
- Bin-width variants: 15 min (search): g +0.279, qualifies False; 60 min (search): g +0.749, qualifies False.

- Re-acquisition (NE41, divergent events, until the next reset): forced n 138: own +0.25, group +0.03, other +0.07, none +0.65; placebo n 156: own +0.20, group +0.04.

### Unit 38b
- 12 committing agents, 43 bins, 4 days, 311 agent work commits; synthetic power at ρ = 0.5: 0.00.

| candidate | members | g (bits / working member-bin) | z_spec | z_shift | specificity | qualifies |
| --- | --- | --- | --- | --- | --- | --- |
| search (search p 0.65) | 5: Gemini 2.5 Pro, Claude Haiku 4.5, GPT-5.1, Claude Opus 4.5, Gemini 3.1 Pro | +0.188 | +2.7 | +0.7 | -0.33 | no |
| multi-layer community | 6: Claude Sonnet 4.5, Claude Haiku 4.5, GPT-5.1, Claude Opus 4.5, DeepSeek-V3.2, GPT-5.2 | +0.045 | +1.1 | -0.3 | +1.00 | no |
| multi-layer community | 6: Gemini 2.5 Pro, Claude Opus 4.6, Claude Sonnet 4.6, Gemini 3.1 Pro, GPT-5.4, Claude Opus 4.7 | -0.031 | -0.9 | +0.9 | – | no |
| room | 7: Gemini 2.5 Pro, Claude Sonnet 4.5, Claude Haiku 4.5, GPT-5.1, Claude Opus 4.5, DeepSeek-V3.2, GPT-5.2 | +0.004 | +1.1 | -0.5 | – | no |
| room | 5: Claude Opus 4.6, Claude Sonnet 4.6, Gemini 3.1 Pro, GPT-5.4, Claude Opus 4.7 | -0.039 | -1.4 | +0.2 | – | no |
| lab | 2: Gemini 2.5 Pro, Gemini 3.1 Pro | +0.000 | – | – | – | no (untestable) |
| lab | 6: Claude Sonnet 4.5, Claude Haiku 4.5, Claude Opus 4.5, Claude Opus 4.6, Claude Sonnet 4.6, Claude Opus 4.7 | +0.018 | +3.0 | +0.2 | +1.00 | no |
| lab | 3: GPT-5.1, GPT-5.2, GPT-5.4 | +0.054 | +1.2 | +1.3 | +1.88 | no |

- Single-layer communities and joint-work crews qualifying: sync 0/2, coad 0/2, reply 0/2, coart 0/2, crew 0/2.
- Search result: lagged gain (transfer entropy) +0.188, content gain -0.010, night gain – (z –); unit individuality ι +0.048 vs aggregation baseline +0.043 (z +0.0), members as agent + own artifact +0.176.
- Attraction diagnostic (A3, post hoc) for the search unit of 5: 1 joins of 3 moves vs +1.6 expected under agent + own artifacts (ratio +0.63).
- Agent + own artifact (singletons): median ι +0.156, median colonial (persistence) +0.116 bits.
- Bin-width variants: 15 min (search): g +0.207, qualifies False; 60 min (search): g +0.342, qualifies False.

- Re-acquisition (NE41, divergent events, until the next reset): forced n 24: own +0.50, group +0.08, other +0.00, none +0.42; placebo n 24: own +0.38, group +0.08.

### Unit 38c
- 12 committing agents, 45 bins, 5 days, 412 agent work commits; synthetic power at ρ = 0.5: 0.05.

| candidate | members | g (bits / working member-bin) | z_spec | z_shift | specificity | qualifies |
| --- | --- | --- | --- | --- | --- | --- |
| search (search p 0.25) | 5: Gemini 2.5 Pro, Claude Haiku 4.5, Claude Opus 4.5, Gemini 3.1 Pro, Claude Opus 4.7 | +0.334 | +7.2 | +2.6 | +0.11 | no |
| multi-layer community | 4: Gemini 3.1 Pro, GPT-5.4, Claude Opus 4.7, Kimi K2.6 | -0.025 | -0.5 | +0.9 | – | no |
| multi-layer community | 3: Gemini 2.5 Pro, GPT-5.1, GPT-5.2 | -0.086 | -2.5 | -1.8 | – | no |
| multi-layer community | 5: GPT-5, Claude Sonnet 4.5, Claude Haiku 4.5, Claude Opus 4.5, DeepSeek-V3.2 | -0.008 | – | -0.5 | – | no (untestable) |
| room | 8: Gemini 2.5 Pro, GPT-5, Claude Sonnet 4.5, Claude Haiku 4.5, GPT-5.1, Claude Opus 4.5, DeepSeek-V3.2, GPT-5.2 | +0.002 | – | +0.2 | – | no (untestable) |
| room | 4: Gemini 3.1 Pro, GPT-5.4, Claude Opus 4.7, Kimi K2.6 | -0.025 | -0.5 | +0.8 | – | no |
| lab | 2: Gemini 2.5 Pro, Gemini 3.1 Pro | – | – | – | – | no (untestable) |
| lab | 4: GPT-5, GPT-5.1, GPT-5.2, GPT-5.4 | -0.015 | +0.6 | +0.5 | – | no |
| lab | 4: Claude Sonnet 4.5, Claude Haiku 4.5, Claude Opus 4.5, Claude Opus 4.7 | +0.223 | +3.9 | +0.4 | -0.29 | no |

- Single-layer communities and joint-work crews qualifying: sync 0/3, coad 0/2, reply 0/2, coart 0/2, crew 0/2.
- Search result: lagged gain (transfer entropy) +0.334, content gain -0.009, night gain – (z –); unit individuality ι -0.242 vs aggregation baseline -0.252 (z +0.2), members as agent + own artifact -0.242.
- Attraction diagnostic (A3, post hoc) for the search unit of 5: None joins of 0 moves vs – expected under agent + own artifacts (ratio –).
- Agent + own artifact (singletons): median ι +0.154, median colonial (persistence) +0.055 bits.
- Bin-width variants: 15 min (search): g +0.163, qualifies False; 60 min (search): g +0.330, qualifies False.

- Re-acquisition (NE41, divergent events, until the next reset): forced n 37: own +0.57, group +0.16, other +0.00, none +0.27; placebo n 39: own +0.56, group +0.08.

**Reading:** no candidate, but this period's synthetic power at ρ = 0.5 is < 0.5, so by A2.1 the null is *not identifiable* (verdict n/a), not a refutation.

## Scorecard (period-specific axes)
- **C**: decision rule = both nulls + specificity + outside reference.
- **F**: synthetic power listed per unit; nulls in under-powered units are 'not identifiable'.

## Notes
- 2026-10-04: prediction written by `period_folders.py --predict` before the run; results filled by `--results`.

## Round 2 (2026-10-05)
### Prediction (written before the round-2 run on this period; card "Round 2 design", amendments R2-A1..A6)
- **R1 A-rule:** no candidate passes; synthetic power ≤ 0.4 even at ρ = 0.7 (38a 0.40, 38b 0.05, 38c 0.10), so a null is not identifiable.
- **R1 village level:** herding in 38a (power 0.85); 38b and 38c not identifiable (0.40–0.45).
- **R2 file level:** eligible shared repos 38a 5, 38b 2, 38c 2; per-repo tests unpowered; enters the pooled test.
- **R3:** as the card (G38 per-period rows).
