# H06 × G35: Test your game, forked per room (2026-03-16 → 2026-03-20)

**Verdict:** descriptive (round-1b native)
**Verdict (1b):** supported (native: known universe recovered; goals fragment)
**Role:** native (round 1b: a week whose project universe is known)
**Period:** regime II · mode C (shared objective per room) · 12–13 agents · #best (GPT-5.4, Opus 4.6, Gemini 3.1 Pro) / #rest (the other 10) · 5 days. No split inside (NE15 is day 1).

## Why this period
The project universe is known from DQ6 and the git record: each room works on its own fork of the #34 RPG (`rpg-game-best`, `rpg-game-rest`). That makes #35 a **positive control** for H06's pipeline: if labels track projects, they must show two dominant species, one per room. It also tests what intention clusters measure: if stated goals still fragment here, round 1's fragmentation is sub-task topic diversity, not project diversity.

## Prediction
*Written 2026-10-04, before building or running anything on #35 in H06.* Scopes: pooled (both rooms) and per room; label sets: work (DQ4 ledger), attention (shared `project_states`), intention clusters `gte_sr` km24 clustered over the period. **Seen before writing:** H11 round 1b's #35 numbers (work co-location 1.00 vs N2 mean 0.98; attention 0.98; work z_N2 +2.2; ownership 0.00/0.01) and H11's work-label count (228 agent-windows). Nothing from H06's pipeline.
- **N35-1 (positive control, work and attention).** In each room the room's own fork is the modal labelled project in ≥ 80% of labelled agent-windows (work and attention), and per-room λ̄ ≥ 0.6 on work labels. Credence 0.85 (largely implied by H11's co-location).
- **N35-2 (adequacy positive control).** On the testable work or attention label set (card rule: ≥ 3 labelled slots per window, ≥ 20 changes; pooled scope, else the #rest room), at least one of NCD, Hubbell or the conformist model is adequate (joint PPC p ≥ 0.01). If all three fail here too, the joint PPC rejects every real labelling and round 1's "no model is adequate" loses its force as evidence against exchangeability. Credence 0.5.
- **N35-3 (what stated goals measure).** Intention clusters (`gte_sr` km24) are as fragmented as in the free weeks although work sits on one repo per room: pooled singleton fraction ≥ 0.7 and λ̄ ≤ 0.3. Credence 0.7. If so, round 1's "agents carry their own projects" is restated as "agents state their own sub-tasks".

## Result
*Run 2026-10-04.* Data: `data/processed/H06-neutral-cooperative-dynamics/r1b/natives_r1b.json` (`G35`), `light_r1b.json` (G35, G35best, G35rest), `G35/fit_G35_{work,art}.json`.

| Test | Observed | Verdict |
| --- | --- | --- |
| N35-1 own fork modal in ≥ 80%; per-room work λ̄ ≥ 0.6 | own fork: work 96% (#best) / 100% (#rest), attention 98% / 99%; other fork 0%. Per-room work λ̄ 0.99 / 1.00 | **supported** |
| N35-2 an exchangeable model adequate on work or attention | not testable: the labels almost never change (work: 1 non-novel switch; attention: 12), below the card's ≥ 20-change rule | **n/a** |
| N35-3 intention clusters fragment anyway (pooled singletons ≥ 0.7, λ̄ ≤ 0.3) | `gte_sr` km24 pooled: singletons 0.76, λ̄ 0.15 (day-shift null 0.10); #rest room alone 0.74 / 0.23; same under bge and gte without style removal (0.75–0.77) | **supported** |

**Reading.** Where the project universe is known and every agent works on its room's fork, work and attention labels recover it almost perfectly, while stated-goal clusters are as fragmented as in a free week. Intention clusters measure sub-task topics, not projects. Round 1's "agents carry their own projects" (from intention clusters) is restated: agents state their own sub-tasks; whether they work on their own projects is a question for work labels (see the card's round-1b section). The day-shift null cannot separate a persistent shared field (room assignment) from copying: pooled work λ̄ 0.57 equals its null (0.57).

## Notes
- 2026-10-04: folder created for round 1b; predictions written before any H06 computation on #35.
