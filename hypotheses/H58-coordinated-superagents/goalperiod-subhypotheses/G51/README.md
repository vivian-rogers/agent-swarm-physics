# H58 × G51: Maximize your private assigned role (head) (2026-07-06 → 2026-09-04)

**Verdict:** mixed
**Role:** replication
**Period:** regime III · units 51a, 51b, 51c, 51d, 51e · 45 non-holdout days. Units are H01 round 2's (card F1).

## Why this period
Layer 1 (replication): it has a dense work ledger (DQ4 agent work commits), so the allocation state (which artifact each agent advances per 30-min bin), the coordination layers and the decision rule can be computed as on every other eligible period, giving one comparable point.

## Prediction
*Written 2026-10-04, before the replication run on this period (templated, per the two-layer rule; after amendments A1 and A2).* The card's P1–P3 applied here: at least one coordination-defined unit (multi-layer community or calibrated search result) is an effective-superagent candidate (g > 0, z_spec ≥ 2, z_shift ≥ 2, specificity ≥ 0.5, testable against an outside reference; search p ≤ 0.05); multi-layer communities rank above rooms and labs; candidates may span rooms. Synthetic power to see a planted store of strength ρ = 0.5 here: **51a 0.40, 51b 0.70, 51c 0.75, 51d 0.60, 51e 0.30**. My prior for this period: 51a: no candidate. 51b: a small candidate around shared infrastructure repos is possible; most allocation is private-role work. 51c: as 51b. 51d: as 51b. 51e: no candidate (2 days).

## Result
Data: `data/processed/H58-coordinated-superagents/results/` (units/*.json, replication.json, natives.json, reacq.json); pipeline `analysis/run.py`, `natives.py`, `reacq.py`.

### Unit 51a
- 17 committing agents, 68 bins, 3 days, 2283 agent work commits; synthetic power at ρ = 0.5: 0.40.

| candidate | members | g (bits / working member-bin) | z_spec | z_shift | specificity | qualifies |
| --- | --- | --- | --- | --- | --- | --- |
| search (search p 0.75) | 2: GPT-5.4, DeepSeek-V4-Pro | +0.257 | +5.4 | +0.9 | +1.00 | no |
| multi-layer community | 11: GPT-5, GPT-5.1, Claude Opus 4.5, DeepSeek-V3.2, GPT-5.2, Claude Opus 4.7, Kimi K2.6, Gemini 3.5 Flash, Claude Opus 4.8, Claude Fable 5, GLM-5.2 | -0.008 | -0.6 | +0.5 | – | no |
| multi-layer community | 6: Gemini 2.5 Pro, Claude Sonnet 4.6, GPT-5.4, GPT-5.5, Claude Sonnet 5, DeepSeek-V4-Pro | -0.003 | – | +0.7 | – | no (untestable) |
| lab | 2: Gemini 2.5 Pro, Gemini 3.5 Flash | – | – | – | – | no (untestable) |
| lab | 5: GPT-5, GPT-5.1, GPT-5.2, GPT-5.4, GPT-5.5 | +0.083 | +1.7 | +1.1 | +4.26 | no |
| lab | 6: Claude Opus 4.5, Claude Sonnet 4.6, Claude Opus 4.7, Claude Opus 4.8, Claude Fable 5, Claude Sonnet 5 | -0.002 | +0.6 | +0.4 | – | no |
| lab | 2: DeepSeek-V3.2, DeepSeek-V4-Pro | -0.012 | -0.6 | +0.0 | – | no |

- Single-layer communities and joint-work crews qualifying: sync 0/3, coad 0/3, reply 0/4, coart 0/2, crew 0/7.
- Search result: lagged gain (transfer entropy) +0.257, content gain +0.035, night gain – (z –); unit individuality ι -0.049 vs aggregation baseline +0.114 (z -1.4), members as agent + own artifact -0.044.
- Attraction diagnostic (A3, post hoc) for the search unit of 2: 0 joins of 2 moves vs +0.8 expected under agent + own artifacts (ratio +0.00).
- Agent + own artifact (singletons): median ι +0.005, median colonial (persistence) +0.277 bits.
- Bin-width variants: 15 min (search): g +0.165, qualifies False; 60 min (search): g +0.112, qualifies False.

- Re-acquisition (NE41, divergent events, until the next reset): forced n 494: own +0.61, group +0.00, other +0.06, none +0.33; placebo n 614: own +0.60, group +0.01.

### Unit 51b
- 27 committing agents, 335 bins, 19 days, 22121 agent work commits; synthetic power at ρ = 0.5: 0.70.

| candidate | members | g (bits / working member-bin) | z_spec | z_shift | specificity | qualifies |
| --- | --- | --- | --- | --- | --- | --- |
| search (search p 0.05) | 8: GPT-5, GPT-5.1, DeepSeek-V3.2, Gemini 3.5 Flash, Claude Opus 4.8, Claude Fable 5, GLM-5.2, Kimi K3 | +0.041 | +0.3 | +3.1 | +0.86 | no |
| multi-layer community | 9: GPT-5, Claude Sonnet 4.5, Claude Haiku 4.5, GPT-5.1, Claude Opus 4.5, DeepSeek-V3.2, Gemini 3.1 Pro, Kimi K2.6, GLM-5.2 | +0.016 | – | +0.3 | -2.81 | no (untestable) |
| multi-layer community | 10: Gemini 2.5 Pro, GPT-5.2, Claude Sonnet 4.6, GPT-5.4, GPT-5.5, Claude Opus 4.8, DeepSeek-V4-Pro, GPT-5.6 Sol, Grok 4.5, Claude Opus 5 | -0.005 | – | -0.8 | – | no (untestable) |
| multi-layer community | 8: Claude Opus 4.6, Claude Opus 4.7, Gemini 3.5 Flash, Claude Fable 5, Claude Sonnet 5, GPT-5.6 Terra, GPT-5.6 Luna, Kimi K3 | +0.001 | – | +0.3 | +1.00 | no (untestable) |
| lab | 3: Gemini 2.5 Pro, Gemini 3.1 Pro, Gemini 3.5 Flash | -0.002 | -0.4 | +0.2 | – | no |
| lab | 8: GPT-5, GPT-5.1, GPT-5.2, GPT-5.4, GPT-5.5, GPT-5.6 Sol, GPT-5.6 Terra, GPT-5.6 Luna | -0.005 | -0.4 | -0.6 | – | no |
| lab | 10: Claude Sonnet 4.5, Claude Haiku 4.5, Claude Opus 4.5, Claude Opus 4.6, Claude Sonnet 4.6, Claude Opus 4.7, Claude Opus 4.8, Claude Fable 5, Claude Sonnet 5, Claude Opus 5 | -0.001 | +0.8 | -1.0 | – | no |
| lab | 2: DeepSeek-V3.2, DeepSeek-V4-Pro | -0.006 | -0.4 | -1.1 | – | no |
| lab | 2: Kimi K2.6, Kimi K3 | -0.004 | -2.1 | -1.4 | – | no |

- Single-layer communities and joint-work crews qualifying: sync 0/2, coad 0/3, reply 0/5, coart 0/4, crew 0/19.
- Search result: lagged gain (transfer entropy) -0.000, content gain -0.014, night gain +0.045 (z +0.1); unit individuality ι +0.154 vs aggregation baseline -0.034 (z +7.1), members as agent + own artifact +0.204.
- Attraction diagnostic (A3, post hoc) for the search unit of 8: 19 joins of 97 moves vs +10.4 expected under agent + own artifacts (ratio +1.84).
- Agent + own artifact (singletons): median ι +0.083, median colonial (persistence) +0.134 bits.
- Bin-width variants: 15 min (search): g -0.002, qualifies False; 60 min (search): g +0.015, qualifies False.

- Re-acquisition (NE41, divergent events, until the next reset): forced n 2958: own +0.66, group +0.02, other +0.03, none +0.29; placebo n 4329: own +0.59, group +0.02.

### Unit 51c
- 26 committing agents, 238 bins, 14 days, 14659 agent work commits; synthetic power at ρ = 0.5: 0.75.

| candidate | members | g (bits / working member-bin) | z_spec | z_shift | specificity | qualifies |
| --- | --- | --- | --- | --- | --- | --- |
| search (search p 0.05) | 8: GPT-5.1, DeepSeek-V3.2, GPT-5.2, Claude Opus 4.7, GPT-5.5, Claude Sonnet 5, GLM-5.2, GPT-5.6 Sol | +0.060 | -0.6 | +5.2 | -2.69 | no |
| multi-layer community | 13: Gemini 2.5 Pro, GPT-5, GPT-5.2, Claude Sonnet 4.6, GPT-5.4, Gemini 3.5 Flash, Claude Opus 4.8, Claude Fable 5, Claude Sonnet 5, DeepSeek-V4-Pro, GPT-5.6 Sol, Grok 4.5, Claude Opus 5 | -0.003 | – | +0.5 | – | no (untestable) |
| multi-layer community | 13: Claude Sonnet 4.5, Claude Haiku 4.5, GPT-5.1, Claude Opus 4.5, DeepSeek-V3.2, Claude Opus 4.6, Gemini 3.1 Pro, Claude Opus 4.7, Kimi K2.6, GPT-5.5, GLM-5.2, GPT-5.6 Terra, Kimi K3 | +0.017 | – | +3.2 | -65.67 | no (untestable) |
| room | 2: Gemini 2.5 Pro, Claude Opus 4.8 | +0.050 | +1.9 | +2.4 | +1.00 | no |
| room | 24: GPT-5, Claude Sonnet 4.5, Claude Haiku 4.5, GPT-5.1, Claude Opus 4.5, DeepSeek-V3.2, GPT-5.2, Claude Opus 4.6, Claude Sonnet 4.6, Gemini 3.1 Pro, GPT-5.4, Claude Opus 4.7, Kimi K2.6, GPT-5.5, Gemini 3.5 Flash, Claude Fable 5, Claude Sonnet 5, DeepSeek-V4-Pro, GLM-5.2, GPT-5.6 Sol, GPT-5.6 Terra, Grok 4.5, Kimi K3, Claude Opus 5 | +0.028 | – | +5.9 | +4.65 | no (untestable) |
| lab | 3: Gemini 2.5 Pro, Gemini 3.1 Pro, Gemini 3.5 Flash | +0.010 | – | +1.6 | +1.00 | no (untestable) |
| lab | 7: GPT-5, GPT-5.1, GPT-5.2, GPT-5.4, GPT-5.5, GPT-5.6 Sol, GPT-5.6 Terra | -0.001 | -0.2 | -0.1 | – | no |
| lab | 10: Claude Sonnet 4.5, Claude Haiku 4.5, Claude Opus 4.5, Claude Opus 4.6, Claude Sonnet 4.6, Claude Opus 4.7, Claude Opus 4.8, Claude Fable 5, Claude Sonnet 5, Claude Opus 5 | -0.007 | -0.1 | -0.6 | – | no |
| lab | 2: DeepSeek-V3.2, DeepSeek-V4-Pro | -0.007 | -0.2 | -1.6 | – | no |
| lab | 2: Kimi K2.6, Kimi K3 | +0.032 | +2.6 | +0.7 | +1.00 | no |

- Single-layer communities and joint-work crews qualifying: sync 0/2, coad 0/3, reply 0/4, coart 0/3, crew 0/16.
- Search result: lagged gain (transfer entropy) +0.037, content gain -0.051, night gain -0.009 (z -0.3); unit individuality ι +0.195 vs aggregation baseline +0.128 (z +2.8), members as agent + own artifact +0.125.
- Attraction diagnostic (A3, post hoc) for the search unit of 8: 9 joins of 118 moves vs +2.0 expected under agent + own artifacts (ratio +4.50).
- Agent + own artifact (singletons): median ι +0.068, median colonial (persistence) +0.069 bits.
- Bin-width variants: 15 min (search): g +0.024, qualifies False; 60 min (search): g +0.035, qualifies False.

- Re-acquisition (NE41, divergent events, until the next reset): forced n 2184: own +0.59, group +0.00, other +0.12, none +0.29; placebo n 3256: own +0.49, group +0.00.

### Unit 51d
- 27 committing agents, 119 bins, 7 days, 7423 agent work commits; synthetic power at ρ = 0.5: 0.60.

| candidate | members | g (bits / working member-bin) | z_spec | z_shift | specificity | qualifies |
| --- | --- | --- | --- | --- | --- | --- |
| search (search p 0.15) | 8: Gemini 2.5 Pro, GPT-5, DeepSeek-V3.2, GPT-5.2, Gemini 3.1 Pro, Gemini 3.5 Flash, Kimi K3, Claude Fable 5.1 | +0.034 | +4.2 | +5.1 | -10.96 | no |
| multi-layer community | 6: Gemini 3.1 Pro, Kimi K2.6, Gemini 3.5 Flash, GLM-5.2, GPT-5.6 Sol, Claude Opus 5 | -0.021 | -0.6 | +0.3 | – | no |
| multi-layer community | 10: Claude Haiku 4.5, Claude Opus 4.5, Claude Opus 4.6, Claude Opus 4.7, GPT-5.5, Claude Fable 5, GPT-5.6 Terra, Kimi K3, GLM-5.3 Flash, Claude Fable 5.1 | -0.014 | – | -1.8 | – | no (untestable) |
| multi-layer community | 3: Gemini 2.5 Pro, Claude Opus 4.8, Grok 4.5 | -0.028 | – | +1.8 | – | no (untestable) |
| multi-layer community | 8: GPT-5, GPT-5.1, DeepSeek-V3.2, GPT-5.2, Claude Sonnet 4.6, GPT-5.4, Claude Sonnet 5, DeepSeek-V4-Pro | -0.006 | -0.5 | -0.3 | – | no |
| lab | 3: Gemini 2.5 Pro, Gemini 3.1 Pro, Gemini 3.5 Flash | -0.016 | -1.7 | +0.7 | – | no |
| lab | 7: GPT-5, GPT-5.1, GPT-5.2, GPT-5.4, GPT-5.5, GPT-5.6 Sol, GPT-5.6 Terra | -0.004 | -0.4 | +0.7 | – | no |
| lab | 10: Claude Haiku 4.5, Claude Opus 4.5, Claude Opus 4.6, Claude Sonnet 4.6, Claude Opus 4.7, Claude Opus 4.8, Claude Fable 5, Claude Sonnet 5, Claude Opus 5, Claude Fable 5.1 | +0.002 | +0.9 | +1.4 | +21.35 | no |
| lab | 2: DeepSeek-V3.2, DeepSeek-V4-Pro | -0.018 | -0.4 | -1.2 | – | no |
| lab | 2: Kimi K2.6, Kimi K3 | +0.000 | +0.1 | +1.1 | – | no |
| lab | 2: GLM-5.2, GLM-5.3 Flash | -0.026 | -3.8 | -1.4 | – | no |

- Single-layer communities and joint-work crews qualifying: sync 0/2, coad 0/3, reply 0/5, coart 0/5, crew 0/10.
- Search result: lagged gain (transfer entropy) +0.034, content gain -0.016, night gain -0.070 (z -0.2); unit individuality ι +0.234 vs aggregation baseline +0.255 (z -0.7), members as agent + own artifact +0.451.
- Attraction diagnostic (A3, post hoc) for the search unit of 8: 3 joins of 30 moves vs +1.2 expected under agent + own artifacts (ratio +2.41).
- Agent + own artifact (singletons): median ι +0.108, median colonial (persistence) +0.110 bits.
- Bin-width variants: 15 min (search): g +0.004, qualifies False; 60 min (search): g +0.010, qualifies False.

- Re-acquisition (NE41, divergent events, until the next reset): forced n 1101: own +0.70, group +0.02, other +0.04, none +0.25; placebo n 1589: own +0.56, group +0.04.

### Unit 51e
- 24 committing agents, 34 bins, 2 days, 1592 agent work commits; synthetic power at ρ = 0.5: 0.30.

| candidate | members | g (bits / working member-bin) | z_spec | z_shift | specificity | qualifies |
| --- | --- | --- | --- | --- | --- | --- |
| search (search p 0.05) | 3: Claude Sonnet 4.6, Claude Fable 5, GPT-6 Astra | +0.104 | +3.4 | +2.3 | +1.00 | yes |
| multi-layer community | 2: Gemini 2.5 Pro, Claude Opus 4.8 | +0.000 | +0.0 | -2.1 | – | no |
| multi-layer community | 4: GPT-5.1, Claude Sonnet 5, DeepSeek-V4-Pro, Gemini 3.8 Flash | -0.011 | -0.2 | +0.1 | – | no |
| multi-layer community | 4: GPT-5, GLM-5.2, GLM-5.3 Flash, Muse Spark 1.3 | -0.010 | -1.3 | -0.1 | – | no |
| multi-layer community | 7: GPT-5.2, Claude Sonnet 4.6, GPT-5.4, Kimi K2.6, Gemini 3.5 Flash, Claude Opus 5, GPT-6 Astra | -0.007 | -0.7 | +0.5 | – | no |
| multi-layer community | 7: Claude Opus 4.7, GPT-5.5, Claude Fable 5, GPT-5.6 Sol, Grok 4.5, Kimi K3, Claude Fable 5.1 | -0.025 | -2.6 | +0.9 | – | no |
| lab | 3: Gemini 2.5 Pro, Gemini 3.5 Flash, Gemini 3.8 Flash | +0.163 | +1.9 | +0.2 | +1.00 | no |
| lab | 7: GPT-5, GPT-5.1, GPT-5.2, GPT-5.4, GPT-5.5, GPT-5.6 Sol, GPT-6 Astra | -0.009 | -0.9 | +0.9 | – | no |
| lab | 7: Claude Sonnet 4.6, Claude Opus 4.7, Claude Opus 4.8, Claude Fable 5, Claude Sonnet 5, Claude Opus 5, Claude Fable 5.1 | -0.007 | +0.8 | +2.3 | – | no |
| lab | 2: Kimi K2.6, Kimi K3 | -0.018 | -1.5 | -0.7 | – | no |
| lab | 2: GLM-5.2, GLM-5.3 Flash | +0.000 | +0.0 | +0.6 | – | no |

- Single-layer communities and joint-work crews qualifying: sync 0/3, coad 0/3, reply 0/5, coart 1/4, crew 0/4.
- Search result: lagged gain (transfer entropy) +0.104, content gain -0.020, night gain – (z –); unit individuality ι -0.224 vs aggregation baseline -0.452 (z +1.5), members as agent + own artifact -0.129.
- Attraction diagnostic (A3, post hoc) for the w_coart unit of 2: 1 joins of 7 moves vs +0.7 expected under agent + own artifacts (ratio +1.43).
- Attraction diagnostic (A3, post hoc) for the search unit of 3: 0 joins of 3 moves vs +0.5 expected under agent + own artifacts (ratio +0.00).
- Agent + own artifact (singletons): median ι -0.010, median colonial (persistence) -0.041 bits.
- Bin-width variants: 15 min (search): g +0.130, qualifies True; 60 min (search): g +0.127, qualifies True.

- Re-acquisition (NE41, divergent events, until the next reset): forced n 279: own +0.78, group +0.00, other +0.02, none +0.19; placebo n 434: own +0.63, group +0.01.

## Scorecard (period-specific axes)
- **C**: decision rule = both nulls + specificity + outside reference.
- **F**: synthetic power listed per unit; nulls in under-powered units are 'not identifiable'.

## Notes
- 2026-10-04: prediction written by `period_folders.py --predict` before the run; results filled by `--results`.
- 2026-10-04, reading (post hoc, A3): the verdict is *mixed* by the pre-registered letter only. The powered units 51b–d (synthetic power 0.60–0.75) have no qualifying unit, which refutes a group store of strength ρ ≳ 0.5 there. Their village-scale search results (8 members) do show real attraction (joins 1.8–4.5× what agent + own artifacts predicts), but it fails specificity or the outside reference: outsiders on the same artifacts co-allocate as much, so it reads as a shared field or convergence, not a group store. The one qualifier (51e: Claude Sonnet 4.6, Claude Fable 5 and GPT-6 Astra, each on its own repo; robust at 15 and 60 min) has **zero joins**: its gain comes from members *avoiding* each other's artifacts (territoriality), which the join-only M1 also rewards. It is not a superagent. Re-acquisition after forced erasures: members return to their own artifact (51e: own 0.78 vs group 0.00).

## Round 2 (2026-10-05)
### Prediction (written before the round-2 run on this period; card "Round 2 design", amendments R2-A1..A6)
- **R1 A-rule (attraction, outside reference):** no round-1 candidate set passes in 51b–d. Synthetic power here at a planted store of ρ = 0.35: 51a 0.80, 51b 1.00, 51c 0.95, 51d 0.85, 51e 0.55; size ≤ 0.05. So a null in 51b–d excludes a group store of ρ ≥ 0.35.
- **R1 village level:** herding (Λ_V above rotations, T_V below) in each of 51a–e; tests powered (≥ 0.95 under W_env).
- **R1 T-rule (territoriality as a group state):** expected none; power ≤ 0.50 at θ = 0.9, so a null is inconclusive. #51e's round-1 qualifier: territorial, not attractive (prior 0.4; 2 days).
- **R2 file level:** shared repos 51a 3, 51b 13, 51c 11, 51d 7, 51e 3 (eligible, ≥ 30 commits); no file-level store (pooled z < 3); own file in a shared container (descriptive).
- **R3:** the pair's stored "which file" information survives erasure (I_store(F) > 0.1 bits, ratio to placebo ≥ 0.8); re-reading is habit (read × erasure interaction CI includes 0); the own-file κ row identified.
