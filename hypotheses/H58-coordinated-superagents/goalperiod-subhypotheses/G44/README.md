# H58 × G44: #best fine-tunes a leader; #rest picks its own goals (2026-05-26 → 2026-05-29)

**Verdict:** failed
**Role:** native
**Period:** regime III · units 44 · 4 non-holdout days. Units are H01 round 2's (card F1).

## Why this period
The only non-holdout period with a known team (#best, four agents, DQ6 room assignment) that shares a dedicated artifact (training data and fine-tuning repos), next to a room that chose its own individual goals on the same days and scaffold. Ground truth for the search.

## Prediction
*Written 2026-10-04, before the #44 analysis (card N2).* **Observable:** the coordination-first search, run without room or team labels, against DQ6's #best team (room assignment, preferred, non-holdout: four agents) and its training-data / fine-tuning repo; the known team evaluated directly with both nulls; qualifying units of size ≥ 3 inside #rest (which chose its own goals). **Prediction (card):** the search returns a set with Jaccard ≥ 0.5 to the team that qualifies, with the fine-tuning repo in its R_G; no qualifying unit of size ≥ 3 in #rest. **Falsified if** Jaccard < 0.5 or the set does not qualify. **Power caveat (A2):** 4 days, 36 bins, synthetic power 0.35 at ρ = 0.5. Replication numbers (P1–P3) are reported here too. **My prior:** the team is recovered through co-artifact work, but its gain is not specific against outsiders (the late joiners also write on the team repo) or not beyond member shifts.

## Result
Data: `data/processed/H58-coordinated-superagents/results/` (units/*.json, replication.json, natives.json, reacq.json); pipeline `analysis/run.py`, `natives.py`, `reacq.py`.

#### Native test N2 (the #best team + its artifact)
- DQ6 #best team: Claude Opus 4.7, Kimi K2.6, GPT-5.5, Gemini 3.5 Flash.
- Search (no labels): Claude Sonnet 4.5, GPT-5.2, Gemini 3.1 Pro, GPT-5.4, Gemini 3.5 Flash; Jaccard with the team +0.12; g +0.213, z_spec +4.8, z_shift +7.7, specificity -1.71, search p +0.05; qualifies False; R_G aethelgard-game, constraint-embodiment-engine, gemini-3-5-flash-memory-vault, gemini-3.1-pro-autonomous-project, gemini-3.1-pro-memory, gpt-5-2-memory-improvement, gpt-5-4-memory-kit, impossible-weather, memory-improvement, multi-layered-framework, pages-propagation-monitor, preference-experiments, preservation-experiments, proof-garden, t0-seed-generator, texture-to-structure-lab, village-link-radar.
- Known team evaluated directly: g -0.053, z_spec -2.3, z_shift +0.5, specificity –, qualifies False; R_G claude-opus-4-7-memory, gemini-3-5-flash-memory-vault, gpt-5-5-leader-finetune, gpt-5-5-memory-improvement, k2-6-memory, kimi-leader-finetune; lagged gain -0.049, night gain -0.097.
- Qualifying units of size ≥ 3 entirely inside #rest: 1.
- Team plus Claude Opus 4.8 (joined 05-28): g -0.056, qualifies False.

#### Replication numbers
### Unit 44
- 15 committing agents, 36 bins, 4 days, 1490 agent work commits; synthetic power at ρ = 0.5: 0.35.

| candidate | members | g (bits / working member-bin) | z_spec | z_shift | specificity | qualifies |
| --- | --- | --- | --- | --- | --- | --- |
| search (search p 0.05) | 5: Claude Sonnet 4.5, GPT-5.2, Gemini 3.1 Pro, GPT-5.4, Gemini 3.5 Flash | +0.213 | +4.8 | +7.7 | -1.71 | no |
| multi-layer community | 5: Claude Opus 4.7, Kimi K2.6, GPT-5.5, Gemini 3.5 Flash, Claude Opus 4.8 | -0.056 | -2.4 | +0.4 | – | no |
| multi-layer community | 10: Gemini 2.5 Pro, Claude Sonnet 4.5, Claude Haiku 4.5, GPT-5.1, Claude Opus 4.5, DeepSeek-V3.2, GPT-5.2, Claude Opus 4.6, Gemini 3.1 Pro, GPT-5.4 | +0.049 | +0.8 | +4.0 | +1.00 | no |
| room | 10: Gemini 2.5 Pro, Claude Sonnet 4.5, Claude Haiku 4.5, GPT-5.1, Claude Opus 4.5, DeepSeek-V3.2, GPT-5.2, Claude Opus 4.6, Gemini 3.1 Pro, GPT-5.4 | +0.049 | +0.8 | +3.8 | +1.00 | no |
| room | 5: Claude Opus 4.7, Kimi K2.6, GPT-5.5, Gemini 3.5 Flash, Claude Opus 4.8 | -0.056 | -2.5 | +0.6 | – | no |
| lab | 3: Gemini 2.5 Pro, Gemini 3.1 Pro, Gemini 3.5 Flash | -0.010 | -0.0 | +1.0 | – | no |
| lab | 6: Claude Sonnet 4.5, Claude Haiku 4.5, Claude Opus 4.5, Claude Opus 4.6, Claude Opus 4.7, Claude Opus 4.8 | -0.013 | -2.1 | +0.2 | – | no |
| lab | 4: GPT-5.1, GPT-5.2, GPT-5.4, GPT-5.5 | +0.009 | +0.5 | +2.5 | +1.00 | no |

- Single-layer communities and joint-work crews qualifying: sync 0/4, coad 0/2, reply 0/3, coart 0/2, crew 1/8.
- Search result: lagged gain (transfer entropy) +0.005, content gain -0.009, night gain -0.039 (z +0.2); unit individuality ι +0.101 vs aggregation baseline -0.015 (z +1.2), members as agent + own artifact +0.069.
- Attraction diagnostic (A3, post hoc) for the crew unit of 5: 4 joins of 34 moves vs +1.4 expected under agent + own artifacts (ratio +2.88).
- Attraction diagnostic (A3, post hoc) for the search unit of 5: 4 joins of 22 moves vs +1.3 expected under agent + own artifacts (ratio +3.05).
- Agent + own artifact (singletons): median ι +0.017, median colonial (persistence) -0.028 bits.
- Bin-width variants: 15 min (search): g +0.129, qualifies False; 60 min (search): g +0.129, qualifies False.

- Re-acquisition (NE41, divergent events, until the next reset): forced n 228: own +0.54, group +0.03, other +0.15, none +0.28; placebo n 348: own +0.51, group +0.03.

## Scorecard (period-specific axes)
- **G** (ground truth): the DQ6 #best team is the answer key for the search (see above).
- **C**: both nulls and the outside reference applied.
- **F**: power 0.35 at ρ = 0.5 (36 bins).

## Notes
- 2026-10-04: prediction written by `period_folders.py --predict` before the run; results filled by `--results`.
- 2026-10-04, reading: the #best team does not act as a unit in its allocation. Its members' own memory and fine-tuning repos dominate (3% of transitions are moves onto a team-mate's artifact; g below its outside reference, z −2.3). The label-free search returns a #rest set (Jaccard 0.125 with the team) that fails specificity. A joint-work crew inside #rest (five agents around a shared framework repo) qualifies with weak attraction (4 joins vs 1.4 expected): that falsifies the card's 'no qualifying unit of size ≥ 3 in #rest' clause. Power 0.35.

## Round 2 (2026-10-05)
### Prediction (written before the round-2 run on this period; card "Round 2 design", amendments R2-A1..A6)
- **R1:** the #best team is not an attraction candidate (power at ρ = 0.5: 0.60; ρ = 0.7: 0.50); village herding (power 0.95).
- **R2:** 4 eligible shared repos (incl. the fine-tuning repo); no file-level store.
- **R3:** G44 per-period rows as the card.
