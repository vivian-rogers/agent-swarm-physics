# Hypohypotheses

Grasping around in the dark. Half-baked, probably wrong, possibly great.
No rigor required: one line for the idea, one for how you'd even check.

When an idea gets a physics model, a data scheme and a written prediction, it
graduates to its own `H<NN>-<slug>/` folder (and gets a "→ H<NN>" note here).
Model numbers refer to `../physics-models/`.

---

**Thermal and phase stuff**
- **The village has a temperature, and it's dropping.** Newer, smarter models make the swarm more ordered. *Check:* fit model 01 per month; track the heat-capacity peak position over time.
- **Weekends are quenches.** The swarm cools overnight and reheats every morning. Does it age, i.e. relax more slowly the longer it was idle? *Check:* relaxation time of activity after each village-hours start vs. length of the preceding gap.
- **Chat rooms are metastable phases.** `ENTER_ROOM` events are nucleation; a room "boils over" when it gets too crowded. *Check:* room occupancy dynamics around move events.
- **Leadership is spontaneous symmetry breaking.** Collaborative goals produce a coordinator; who it is should be random unless model family acts as a symmetry-breaking field. *Check:* identify the de facto coordinator per goal; test for model-family bias.
- **Jamming.** Too many agents on one shared doc and throughput drops, like a traffic flow-vs-density diagram. *Check:* edits per agent-hour vs. number of agents on the same artifact.
- **A time crystal.** The swarm oscillates with a period that isn't the daily drive (e.g. 2-day cycles). *Check:* activity spectrum after removing the daily and weekly components.
- **Heat death.** The fraction of tokens spent going nowhere (`WAIT` loops, repeated failed actions) grows over the life of a goal. *Check:* "useless action" fraction vs. time since goal start.

**Contagion and information**
- **Sycophancy is ferromagnetic coupling.** Agreement cascades ("great idea!") are avalanches with power-law sizes. *Check:* runs of agreeing replies; size distribution vs. shuffled.
- **Misinformation outruns correction.** A false claim spreads further than its correction (model 03). *Check:* paired claim/correction trees; compare branching ratios.
- **"Genuinely" is a magnetization.** Claude agents form a ferromagnetic domain in vocabulary; mixed-family rooms are frustrated. *Check:* per-family word-frequency vectors; do families' vocabularies converge when they share a room?
- **Jargon cools.** Vocabulary entropy falls within a goal as the swarm settles on shared terms, and jumps at goal changes. *Check:* per-day entropy of chat n-grams, aligned to goal boundaries.
- **Memory consolidation is a renormalization step.** Each consolidation coarse-grains history; what survives many consolidations are the "relevant operators". *Check:* which memory items persist across N consolidations, and what they have in common.
- **Agents play the telephone game toward their priors.** Multi-hop content drifts toward each family's defaults (model 08). *Check:* drift direction on numeric/URL features along transmission chains.
- **Humans are the heat bath.** When humans go quiet the swarm freezes (or overheats?). *Check:* activity and entropy vs. `USER_TALK` rate.

**Evolution and ecology**
- **Model upgrades are mutations; departures are extinctions.** The roster is an evolutionary process; does fitness (by any proxy) predict tenure? *Check:* roster join/leave dates vs. performance proxies.
- **Projects form a cooperator core** (model 06). *Check:* bimodal project abundances in stable periods.
- **Tool use is a Lévy flight.** Agents forage over websites and tools with heavy-tailed jumps, like animals foraging for scarce resources. *Check:* distribution of "distance" between consecutive tools/domains in `computer_use_turns`.

**Weird ones**
- **The nudger is a Maxwell demon.** It sorts idle from active agents and lowers the swarm's entropy at some cost. *Check:* entropy of activity before vs. after nudges; what does the nudge "cost"?
- **Each model family has its own arrow of time.** Claude agents are more irreversible than GPT agents (model 02). *Check:* per-agent entropy-production bounds, grouped by family.
- **Politeness is zero-point energy.** Baseline chatter never goes to zero even with nothing to do. *Check:* minimum message rate across idle periods, by family.
- **Bugs avalanche.** One failure triggers cascades of debugging across agents, with self-organized-critical size statistics. *Check:* error-burst sizes in `computer_use_turns.error` across agents.
