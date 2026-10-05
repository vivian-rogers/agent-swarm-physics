# H58 × NE42: NE42 merge (05-04) and split (05-11): #39 -> #40 -> #41 (2026-04-27 → 2026-05-15)

**Verdict:** mixed
**Role:** native
**Period:** regime III · units 39, 40, 41 · 15 non-holdout days. Units are H01 round 2's (card F1).

## Why this period
The only A-B-A channel manipulation at a fixed roster (merge into one room, split back), with the store reorganized in between: 15 own artifacts (#39) joined into one shared repo (#40), then independent research (#41). DQ9 lists #40 (one artifact, one room, 14 contributors) as H58's first native test.

## Prediction
*Written 2026-10-04, before the NE42 analysis (card N1).* **Observable:** the size and qualification of the best coordination-defined unit across the A-B-A (#39 own worlds → #40 one merged room and one shared universe repo → #41 split back), and, inside #40's shared repo, the coordination gain at **file granularity** (read-only `git log --name-only`: the hub file vs per-agent landmark files) against the agent + own file null. **Prediction (card):** #40's search result has ≥ 4 members and qualifies; no qualifying unit of size ≥ 4 in #39 or #41; at file level g > 0 with z_shift ≥ 2. **Falsified if** #40 has no qualifying unit of size ≥ 4. **Power caveat (A2):** 5-day units have synthetic power 0.15–0.30 at ρ = 0.5, so a null in #40 is weak. **My prior:** at file level members keep to their own landmark file and the hub file is a common field; #40 does not qualify.

## Result
Data: `data/processed/H58-coordinated-superagents/results/` (units/*.json, replication.json, natives.json, reacq.json); pipeline `analysis/run.py`, `natives.py`, `reacq.py`.

| unit | search result (size) | qualifies | g | z_spec | z_shift | specificity | largest qualifying unit |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 39 | GPT-5.1, GPT-5.2 (2) | False | +0.147 | +2.8 | +2.5 | +1.00 | 0 |
| 40 | Claude Sonnet 4.5, Claude Opus 4.5, Gemini 3.1 Pro (3) | False | +0.064 | – | +1.1 | +1.33 | 0 |
| 41 | Gemini 2.5 Pro, Claude Sonnet 4.5, Claude Haiku 4.5, GPT-5.1, GPT-5.2, GPT-5.4, Claude Opus 4.7, Kimi K2.6 (8) | False | +0.248 | +1.7 | +7.0 | -0.21 | 0 |

**File level inside #40's shared repo** (artifact = file group, path depth ≤ 2):
- 164 file groups, 12 writers; the hub file takes +0.55 of working bins; median top-file share per agent +0.75.
- All writers as one unit: g -0.042, z_spec –, z_shift -1.0, specificity – (untestable: no outsiders), qualifies False.
- File-level search: Gemini 2.5 Pro, Claude Haiku 4.5, DeepSeek-V3.2, GPT-5.2, Gemini 3.1 Pro, Claude Opus 4.7, Kimi K2.6, GPT-5.5; g +0.128, z_spec –, z_shift +2.5, specificity -0.98, search p +0.55, qualifies False.
- Multi-layer communities at file level: 3 members, g +0.051, qualifies False; 9 members, g +0.059, qualifies False.

**Verdict rule (card N1):** #40 qualifying unit of size ≥ 4: False; none in #39/#41: True; file-level g > 0 with z_shift ≥ 2: True. Power caveat (A2): 0.15–0.30 at ρ = 0.5.

## Scorecard (period-specific axes)
- **E** (interventional): the prediction did not hold or was not testable.
- **G**: rooms and the A-B-A dates are known; the file-level and room assignments come from logged fields.
- **F**: 5-day units have low synthetic power (A2).

## Notes
- 2026-10-04: prediction written by `period_folders.py --predict` before the run; results filled by `--results`.
- 2026-10-04, reading: *mixed* by the letter only. The file-level part passes on g > 0 and z_shift ≥ 2, but that set is untestable against an outside reference (no file-level outsiders), its specificity is negative and its search p is 0.55. The main part fails: #40 has no qualifying unit of any size, and neither do #39 or #41. Inside the shared repo, half of all working bins are on the hub file (a common field), and each agent keeps 75% of its work on its own top file (median): agent + own file, inside a shared container. Power is low (0.15–0.30 at ρ = 0.5).

## Round 2 (2026-10-05)
### Prediction (written before the round-2 run on these units; card "Round 2 design", amendments R2-A1..A6)
- **R1:** no A-rule candidate in #39, #40 or #41 (power at ρ = 0.7: 0.80, 0.35, 0.40); village herding in #40 (one shared repo) and #41; #39 has no shared repo.
- **R2 file level, #40's shared universe repo:** own file in a shared container (exclusivity above the random partition), hub file as a common field, no file-level store (Λ_file z_shift < 2; per-repo power is low, so a null is not identifiable on its own).
- **R3:** G39–G41 per-period rows as the card.
