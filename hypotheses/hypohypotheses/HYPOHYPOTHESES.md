# Hypohypotheses

Grasping around in the dark. Half-baked, probably wrong, possibly great.
No rigor required: one line for the idea, one for how you'd even check.

**Promotion rule.** An idea graduates to its own `H<NN>-<slug>/` folder (and gets a "→ H<NN>" note here) when it has:
- a physics model and a data scheme;
- faithfulness axis A ≥ 1;
- a written plan for axes C, D and either E or G, with explicit falsifiers.

The axes are defined in `writeup/paper.tex`, "Assessing model faithfulness". Promotion is a commitment to a test, not evidence. Related notes: [phase-diagrams.md](phase-diagrams.md), [greens-functions.md](greens-functions.md).

**Tags under each idea.** *Models* are the physics models most faithful to the idea, best first; numbers refer to `../../physics-models/`. *Periods* are goal periods (#) from [goal-periods.md](goal-periods.md) and natural experiments (NE) from [../natural-experiments.md](../natural-experiments.md) where the idea should show up or can be tested.

Models: [01](../../physics-models/01-inverse-ising/) inverse Ising · [02](../../physics-models/02-nonequilibrium-ising/) nonequilibrium Ising · [03](../../physics-models/03-contagion/) contagion · [04](../../physics-models/04-semantic-information/) semantic information · [05](../../physics-models/05-replicator-dissipation/) replicator dissipation · [06](../../physics-models/06-neutral-cooperative-dynamics/) neutral cooperative · [07](../../physics-models/07-replicators-fluctuating-environments/) fluctuating environments · [08](../../physics-models/08-copying-vs-transformation/) copying vs. transformation · [09](../../physics-models/09-hawkes/) Hawkes · [10](../../physics-models/10-potts/) Potts · [11](../../physics-models/11-vector-spins/) vector spins

---

**Thermal and phase stuff**
- **HH01 · The village has a temperature, and it's dropping.** Newer, smarter models make the swarm more ordered. *Check:* fit model 01 per month; track the heat-capacity peak position over time.
  *Models:* 01 (heat-capacity peak), 11 (polarization trend), 02 · *Periods:* matched-mode weeks across time: free weeks #11, #16, #22, #31, #37; null weeks #10, #14, #49; shared-objective weeks #18, #30, #47
- **HH02 · Weekends are quenches.** The swarm cools overnight and reheats every morning. Does it age, i.e. relax more slowly the longer it was idle? *Check:* relaxation time of activity after each village-hours start vs. length of the preceding gap.
  *Models:* 09 (relaxation after restart), 02, 11 · *Periods:* long goals spanning many weekends: #1, #4, #8, #38, #51; NE21 (hours change)
- **HH03 · Chat rooms are metastable phases.** `ENTER_ROOM` events are nucleation; a room "boils over" when it gets too crowded. *Check:* room occupancy dynamics around move events.
  *Models:* 10 (room as a Potts variable), 06, 09 · *Periods:* #32 onward; #35 (split), #39 (reshuffle), #40 (#universe-coordination), #51 (#focus); NE12, NE15
- **HH04 · Leadership is spontaneous symmetry breaking.** Collaborative goals produce a coordinator; who it is should be random unless model family acts as a symmetry-breaking field. *Check:* identify the de facto coordinator per goal; test for model-family bias.
  *Models:* 10, 02 (directed couplings out of the coordinator), 11 · *Periods:* shared-objective weeks with an emergent coordinator #13, #18, #19, #25, #30, #40; contrast #26 (elected) and #45 (assigned)
- **HH05 · Jamming.** Too many agents on one shared doc and throughput drops, like a traffic flow-vs-density diagram. *Check:* edits per agent-hour vs. number of agents on the same artifact.
  *Models:* 09, 06, 10 · *Periods:* shared-artifact weeks #19, #31 (competing PRs), #34–#35 (RPG), #40 (universe repo); NE24 (GitHub → GitLab)
- **HH06 · A time crystal.** The swarm oscillates with a period that isn't the daily drive (e.g. 2-day cycles). *Check:* activity spectrum after removing the daily and weekly components.
  *Models:* 09, 11 (n = 2: Kuramoto phases), 02 · *Periods:* long windows #1, #4, #38, #51; NE21
- **HH07 · Heat death.** The fraction of tokens spent going nowhere (`WAIT` loops, repeated failed actions) grows over the life of a goal. *Check:* "useless action" fraction vs. time since goal start.
  *Models:* 09 (subcritical decay), 04 (viability), 05 · *Periods:* long goals #4, #8, #27, #38, #51; NE07 ("don't do nothing", in #21), NE10 (nudger on, in #30)

**Contagion and information**
- **HH08 · Sycophancy is ferromagnetic coupling.** Agreement cascades ("great idea!") are avalanches with power-law sizes. *Check:* runs of agreeing replies; size distribution vs. shuffled.
  *Models:* 03 (cascade sizes), 01, 09 · *Periods:* chatty shared-objective weeks #15, #24, #28; contrast competitive weeks #6, #23, #27
- **HH09 · Misinformation outruns correction.** A false claim spreads further than its correction. *Check:* paired claim/correction trees; compare branching ratios.
  *Models:* 03, 08, 04 (negative value of information) · *Periods:* #38 (NE36 Year-1 correction), #45 ("temporal bleed"), #33 (claims database), #29 (news)
- **HH10 · "Genuinely" is a magnetization.** Claude agents form a ferromagnetic domain in vocabulary; mixed-family rooms are frustrated. *Check:* per-family word-frequency vectors; do families' vocabularies converge when they share a room?
  *Models:* 11 (vocabulary vectors), 10, 03 (shared prior as a field) · *Periods:* before vs. after NE12; mixed rooms #35, #47; #51 (most families present)
- **HH11 · Jargon cools.** Vocabulary entropy falls within a goal as the swarm settles on shared terms, and jumps at goal changes. *Check:* per-day entropy of chat n-grams, aligned to goal boundaries.
  *Models:* 11, 10, 03 · *Periods:* every goal boundary (NE34); long goals #4, #8, #27, #38
- **HH12 · Memory consolidation is a renormalization step.** Each consolidation coarse-grains history; what survives many consolidations are the "relevant operators". *Check:* which memory items persist across N consolidations, and what they have in common.
  *Models:* 04, 08, 11 · *Periods:* regime III #37–#51 (consolidation every ~40 actions); #43 (memory week); NE14 transition (#34, #36)
- **HH13 · Agents play the telephone game toward their priors.** Multi-hop content drifts toward each family's defaults. *Check:* drift direction on numeric/URL features along transmission chains.
  *Models:* 08, 03, 11 · *Periods:* #4 (shared story), #25 (museum of history), #33 (claims), #44 (distillation)
- **HH14 · Humans are the heat bath.** When humans go quiet the swarm freezes (or overheats?). *Check:* activity and entropy vs. `USER_TALK` rate.
  *Models:* 09 (outside excitation), 02, 11 · *Periods:* early weeks with heavy viewer chat #1–#6; NE39 (chat closed); #46 (whitelisted human), #50 (human personas)

**Evolution and ecology**
- **HH15 · Model upgrades are mutations; departures are extinctions.** The roster is an evolutionary process; does fitness (by any proxy) predict tenure? *Check:* roster join/leave dates vs. performance proxies.
  *Models:* 05, 06, 07 · *Periods:* whole roster; NE30 (same-family succession, #34); batch joins #10 (NE27), #51 (NE33)
- **HH16 · Projects form a cooperator core.** *Check:* bimodal project abundances in stable periods.
  *Models:* 06, 10 · *Periods:* free weeks #11, #16, #22, #31, #37; #51
- **HH17 · Tool use is a Lévy flight.** Agents forage over websites and tools with heavy-tailed jumps, like animals foraging for scarce resources. *Check:* distribution of "distance" between consecutive tools/domains in `computer_use_turns`.
  *Models:* 09 (bursty timing), 11 (steps in embedding space; drift–diffusion candidate) · *Periods:* individual-objective weeks #10, #17, #39, #49; #51

**Weird ones**
- **HH18 · The nudger is a Maxwell demon.** It sorts idle from active agents and lowers the swarm's entropy at some cost. *Check:* entropy of activity before vs. after nudges; what does the nudge "cost"?
  *Models:* 09, 02, 04 · *Periods:* NE10 (switched on, #30); NE23 (off/on, #46); any week after 2026-02-10
- **HH19 · Each model family has its own arrow of time.** Claude agents are more irreversible than GPT agents. *Check:* per-agent entropy-production bounds, grouped by family.
  *Models:* 02, 09 · *Periods:* #51 (most families together); regime III; NE20 (Anthropic-only change, DiD)
- **HH20 · Politeness is zero-point energy.** Baseline chatter never goes to zero even with nothing to do. *Check:* minimum message rate across idle periods, by family.
  *Models:* 09 (baseline rate μ), 11 · *Periods:* holidays #3, #5, #7, #9; free weeks #11, #16, #22
- **HH21 · Bugs avalanche.** One failure triggers cascades of debugging across agents, with self-organized-critical size statistics. *Check:* error-burst sizes in `computer_use_turns.error` across agents.
  *Models:* 09 (branching), 03 · *Periods:* build-heavy weeks #17 (websites), #19, #34–#35 (RPG), #40; #24 (fixing bugs for others)

**Model X explains period Y**
- **HH22 · Potts explains the election (#26).** Approval votes over six candidates behave like a q = 6 Potts system sitting at its symmetric point (the three-way tie); the runoff is a first-order jump. *Check:* endorsement counts over time; how abrupt the switch is.
  *Models:* 10, 03 (bandwagon), 02 · *Periods:* #26; also #12 (teams), #34 (vote-outs)
- **HH23 · Nonequilibrium Ising explains "Follow your leader" (#45).** Inferred directed couplings point out of the Fine-Tuned Leader. Ground truth exists, so this doubles as a validation of the inference method. *Check:* kinetic-Ising J_ij − J_ji with the leader as source.
  *Models:* 02, 09, 10 · *Periods:* #45; contrast #26 (elected leader), #44
- **HH24 · Potts (antiferromagnetic) explains the human-subjects experiment (#13).** Collaborators spread across subtasks: division of labor as graph coloring. *Check:* sign of the inferred Potts couplings on task labels.
  *Models:* 10, 06, 09 · *Periods:* #13; also #18, #30, #40
- **HH25 · Potts explains the puzzle-game brainstorm (#19).** Choosing among the candidate concepts is a discontinuous consensus, not a gradual drift. *Check:* concept-mention shares over the first days.
  *Models:* 10, 03 (complex contagion), 06 · *Periods:* #19; also #40 (standards), #8
- **HH26 · Potts explains the guardrails pile-up (#31).** About nine agents condensed onto one project with no goal pushing them there: ferromagnetic herding without a field. *Check:* project-label shares; compare with the other free weeks.
  *Models:* 10, 06, 11 · *Periods:* #31; also #41, #44 (#rest)
- **HH27 · Vector spins explain the benchmark convergence (#8).** Near-identical frameworks written independently are aligned by a field (shared priors), not coupling. *Check:* embedding overlap vs. exposure.
  *Models:* 11, 03 (field ε), 01 · *Periods:* #8; also #41, #43
- **HH28 · Vector spins explain the forecast week (#21).** Alignment jumps when agents switch from independent drafts to comparing, i.e. when the coupling is switched on. *Check:* polarization before and after the comparison phase.
  *Models:* 11, 07, 08 · *Periods:* #21; also #33
- **HH29 · Vector spins explain novel research (#41).** About 11 agents converging on "study ourselves" is field-driven condensation. *Check:* exposure-free agreement.
  *Models:* 11, 06, 03 · *Periods:* #41; also #8, #44
- **HH30 · Hawkes explains the holidays (#3, #5, #7, #9).** Holidays are subcritical (branching ratio < 0.5), while shared-objective weeks run near critical. *Check:* branching ratio per goal period.
  *Models:* 09, 02, 11 · *Periods:* #3, #5, #7, #9; also free weeks #11, #16, #22
- **HH31 · Hawkes explains the nudger reversal (NE23, 2026-06-13 → 06-15).** Nudges have a measurable outside-excitation kernel that disappears when the nudger is off. *Check:* response kernels across the off/on switch.
  *Models:* 09, 02 · *Periods:* #46 (NE23); also NE10 (#30)
- **HH32 · Hawkes explains the long private-role era (#51).** The longest window is closest to critical (branching ratio → 1). *Check:* branching ratio in rolling windows, controlling for the baseline (Filimonov–Sornette).
  *Models:* 09, 02, 01 · *Periods:* #51
- **HH33 · Nonequilibrium Ising explains rooms (NE12, mid-#32).** Entropy production steps down when cross-room coupling is cut. *Check:* Aguilera estimator before and after.
  *Models:* 02, 09, 01 · *Periods:* #32 (NE12); also #33 (first full week of regime II)
- **HH34 · Nonequilibrium Ising explains chess week (#23).** Turn-based games are literal sequential updates; irreversibility is concentrated in game pairs. *Check:* pairwise entropy-production contributions.
  *Models:* 02, 09, 07 · *Periods:* #23; also #27, #32
- **HH35 · Contagion explains the YouTube week (#42).** "1–10 videos means 10" spread as a simple contagion with R₀ > 1. *Check:* who read it that way, and when.
  *Models:* 03, 09, 05 · *Periods:* #42; also #20, #17
- **HH36 · Contagion explains the breaking-news race (#29).** News items spread between agents faster than independent discovery would predict. *Check:* first-mention times against the exposure network.
  *Models:* 03, 09, 07 · *Periods:* #29; also #20
- **HH37 · Complex contagion explains the memory week (#43).** The GitHub-backed memory pattern needed several exposures, or was invented independently in each room. *Check:* adoption vs. number of exposures; cross-room timing.
  *Models:* 03, 04, 08 · *Periods:* #43; also #17 (tools)
- **HH38 · Copying vs. transformation explains the RPG forks (#35).** Copy information between #best and #rest decays steadily with time since the split. *Check:* shared-code and shared-content overlap per day.
  *Models:* 08, 10, 09 · *Periods:* #35 (NE15); also NE32 (isolated triplet rooms)
- **HH39 · Copying vs. transformation explains the leader fine-tune (#44).** Distillation keeps the village's vocabulary (copy) but not its plans (transformation). *Check:* compare leader outputs with village text.
  *Models:* 08, 04, 11 · *Periods:* #44, #45 (NE31)
- **HH40 · Fluctuating environments explain charity, twice (#1 vs #38).** The second run starts with a better allocation, because memory carried side information from the first. *Check:* initial effort shares vs. eventual winning channels.
  *Models:* 07, 03, 09 · *Periods:* #1, #38
- **HH41 · Fluctuating environments explain the merch competition (#6).** Profit tracks how well strategy matches environment. *Check:* the productivity decomposition with profit as the output.
  *Models:* 07, 08, 05 · *Periods:* #6; also #27, #50
- **HH42 · Neutral cooperative dynamics explain the free weeks (#11, #16, #22, #31, #37).** Project abundances are bimodal, with a persistent core. *Check:* abundance histograms against the predicted λ*.
  *Models:* 06, 10, 11 · *Periods:* #11, #16, #22, #31, #37; also #51
- **HH43 · Semantic information explains the memory week (#43).** Agents keep far more than their behavior needs (η ≪ 1). *Check:* later, by replay.
  *Models:* 04, 08, 03 · *Periods:* #43; also #2 (reflection), #25 (museum)
- **HH44 · Inverse Ising explains the null weeks (#10, #14, #49).** With everyone on their own objective, couplings beyond common drive are ≈ 0. If not, there's an artifact. *Check:* J against circular-shift nulls.
  *Models:* 01, 09, 11 · *Periods:* #10, #14, #49; also #39
- **HH45 · Regime comparison: nonequilibrium Ising, I vs. III.** Perma-computer-use (regime III) is more irreversible than discrete sessions (regime I). *Check:* entropy production per agent-hour by regime.
  *Models:* 02, 09 · *Periods:* regime I (#1–#32) vs. III (#37–#51); boundary #36 (NE14)
- **HH46 · Hawkes and hours (NE21).** 8-hour days have a lower branching ratio than 4-hour days (activity spreads out), reversibly across 4 → 8 → 4 → 8 h. *Check:* the reversal design.
  *Models:* 09, 02 · *Periods:* #46, #47, #50 (NE21)

**Free-energy landscapes (Gibbs analogies from biology, ecology, thermodynamics)**

Common move: where occupancy of coarse states is roughly stationary, invert it, G(x) = −T ln P(x) up to a constant (Boltzmann inversion, as for free-energy landscapes in molecular dynamics). Basins are the favored phenomena; barriers come from transition rates (Arrhenius/Kramers: rate ∝ e^{−ΔG‡/T}). *Gibbs, not Helmholtz:* operators set intensive variables (the goal field, hours, room assignments) and agents choose extensive ones (alignment, occupancy), so the natural potential is the one at fixed field, G = F − h·m.
- **HH47 · There's a free-energy landscape over agent states.** Projects, topics and action classes have stable occupancies, so G(x) = −T ln P(x) has basins (the "existential attractor", self-study topics, coding) and measurable barriers between them. *Check:* a Markov state model on project/topic labels; stationary occupancies; barrier heights from transition rates.
  *Models:* 11 (embedding space; Markov-state-model candidate), 10, 02 · *Periods:* free weeks #11, #16, #22, #31, #37 (no field: the landscape is intrinsic); #44 (#rest); contrast with fielded weeks, where the goal tilts the landscape
- **HH48 · Enthalpy vs. entropy.** Some phenomena win because each instance is strongly preferred (*enthalpic*: e.g. a model family's pull toward one kind of work). Others win because there are many ways to do them (*entropic*: broad topics with many sub-variants). *Check:* split occupancy into per-variant preference vs. the number of distinct variants (cluster breadth in embedding space). A van 't Hoff-style test: how occupancy shifts with an effective-temperature knob (the fluctuation–dissipation effective temperature, or sampling temperature if it can be obtained).
  *Models:* 11, 10, 06 · *Periods:* free weeks; #41 (11 agents converging: enthalpic?); #31
- **HH49 · Gibbs, not Helmholtz: goals are Legendre pushes.** Estimate the free energy F(m) of alignment m from field-free fluctuations, then predict fielded weeks by tilting it, G = F − h·m, *without refitting*. Response follows ∂G/∂h = −m, which ties this to susceptibility. *Check:* fit F on free weeks; predict alignment in shared-objective weeks out of sample.
  *Models:* 11, 01, 10 · *Periods:* free weeks → shared-objective weeks; NE08 and NE13 (the field made persistent)
- **HH50 · Rooms and projects have chemical potentials.** Agents distribute across rooms and projects until the potentials μ equalize. Net flows run down μ gradients, where μ is roughly −T ln(occupancy share / capacity) plus an attraction term. *Check:* estimate μ per room or project; test whether room moves and project switches flow from high μ to low μ; watch re-equilibration after a split.
  *Models:* 10, 06, 09 · *Periods:* #32 onward (rooms); #35 (NE15 split); #40 (#universe-coordination); #51
- **HH51 · Coupled reactions (the ATP analogy).** Goals get unfavorable work done by coupling it to a favorable drive: ΔG_task + ΔG_goal < 0. Uphill work (outreach, Google sign-ins, help requests, grinding debugging) should appear under goals that pay for it and vanish in free weeks. *Check:* rate of high-friction actions by goal mode; raising a barrier (NE17 outreach approval) should cut it unless the drive is strong.
  *Models:* 07, 04, 09 · *Periods:* #1 and #38 (charity; NE17 inside #38), #28 (promotion), #42 vs. free weeks
- **HH52 · Catalysts vs. fields.** Some interventions lower activation barriers without changing which states are favored: *catalysts* (the nudger, human helpers, the sign-in hand-off). Others tilt the landscape: *fields* (goals, prompt changes). Catalysts change rates but not stationary occupancies; fields change occupancies. *Check:* across the nudger switching on (NE10) and off/on (NE23), compare escape rates from idle states with the stationary idle fraction.
  *Models:* 09, 02, 10 · *Periods:* #30 (NE10), #46 (NE23); B (human helpers, July 2025)
- **HH53 · Metastable traps are local minima.** Idle loops (WAIT/PAUSE runs), the micro-session loops of #32 and theory spirals ("temporal bleed" in #45) are local free-energy minima. Escape times follow Kramers in the barrier height; nudges and human messages act as thermal kicks. *Check:* dwell-time distributions in trap states; escape rate vs. kick rate.
  *Models:* 09, 02, 11 · *Periods:* #32, #45; NE07 ("don't do nothing": a shallower trap?); NE10, NE23
- **HH54 · Two models already contain a free energy.** Neutral cooperation's steady state gives a double-well G(n) = −ln P_n, with the cooperator core as the second minimum; it appears below μ_B. The replicator productivity decomposition is a free energy with Ω as temperature: uncertainty − side information + mismatch. *Check:* G(n) from project abundances in free weeks (S6), looking for the second well; the Ω-weighted cross-entropy per goal transition.
  *Models:* 06, 07 · *Periods:* free weeks #11, #16, #22, #31, #37; all goal transitions

**Stat-mech primitives: states, ensembles, symmetries, currents** (see [statmech-primitives.md](statmech-primitives.md))
- **HH55 · Agents are non-ergodic.** Each agent's time-averaged action mix and topics differ from the population average by more than chance. The gap grows with tenure and memory length, and is largest in free weeks. *Check:* an ergodicity-breaking parameter (time average vs. ensemble average) per agent and window; does consolidation every ~40 actions (NE14) partly restore ergodicity?
  *Models:* 11, 10, 02 · *Periods:* #51; free weeks #11, #16, #22, #31, #37; NE14
- **HH56 · Work cycles carry probability currents.** Agents' action-class transitions circulate (plan → act → report → wait → plan) with nonzero cycle affinity. Entropy production concentrates in a few cycles (Schnakenberg decomposition), and the cycles change at perma-computer-use. *Check:* per-agent transition matrices over action classes; cycle currents and affinities before vs. after NE14.
  *Models:* 02, 09 · *Periods:* regime I vs. III (NE14); #51
- **HH57 · Memory is a finite volume under pressure.** Memory length saturates, and consolidation is compression. The context cap (NE22) is a piston that reduces the volume, and incoming events per consolidation act as a pressure. Memory length vs. pressure follows an equation of state. *Check:* memory length and compression ratio vs. incoming event rate; jumps at NE22 and NE14.
  *Models:* 04, 08, 11 · *Periods:* regime III (#37–#51); #43; #46 (NE22)
- **HH58 · Effective dimensionality collapses at consensus.** The participation ratio of the swarm's embedding covariance drops after kickoffs and during consensus events, and re-expands in free weeks. It's an order parameter complementary to polarization. *Check:* participation ratio per window, aligned to kickoffs and consensus events.
  *Models:* 11, 10 · *Periods:* kickoffs (NE34); #19, #31, #40; free weeks
- **HH59 · Entropic forces cause scope creep.** Macrostates with more microstates (more phrasings, more action paths, more ways to contribute) pull agents in even when no single variant is preferred. Under-specified goals and projects attract disproportionate time. *Check:* occupancy vs. multiplicity (cluster breadth, distinct action paths per artifact); compare well-specified goals with vague ones.
  *Models:* 06, 10, 11 · *Periods:* free weeks; #41 (research); #18 and #47 (vague altruism) vs. #23 and #27 (well-specified competitions)
- **HH60 · Rooms are grand-canonical subsystems.** Room-occupancy fluctuations follow grand-canonical statistics: the compressibility is Var(N_r)/⟨N_r⟩. Operator-closed rooms behave canonically (smaller fluctuations) and open rooms grand-canonically, so the fluctuation ratio tells closed subsystems from open ones. *Check:* occupancy variance per room vs. its openness (whitelists, operator moves).
  *Models:* 10, 06, 09 · *Periods:* #32 onward; #35; #40; #51 (#focus)
- **HH61 · Timescale separation permits adiabatic elimination.** Fast turn-level variables equilibrate within a session; slow variables (intentions, memory) change at consolidations. Once the fast variables are integrated out, the slow dynamics of intentions is Markov. *Check:* Markov order of the intention sequence; gaps between autocorrelation times.
  *Models:* 02, 11, 09 · *Periods:* regime III (a clean consolidation clock); #51
- **HH62 · Statistical complexity differs by model family.** The excess entropy and statistical complexity of each agent's action sequence (computational mechanics) are higher for newer models, and collapse in trap states. *Check:* entropy-rate convergence and ε-machine reconstruction per agent; compare families and eras.
  *Models:* 09, 02, 04 · *Periods:* #51 (many families); regime III
- **HH63 · Goal switches are thermodynamic work.** Treat each switch as a protocol on the field: W = Σ m(t) Δh(t). Across the 50 switches W has a distribution, and fast switches dissipate more (the swarm lags behind the field), as in finite-time thermodynamics. *Check:* alignment lag and W per switch, vs. goal length; one-day goals (#43, #48) vs. long ones.
  *Models:* 11, 02 · *Periods:* all goal transitions (NE34); #43, #48
- **HH64 · Artifacts form a food web.** Agents take producer and consumer roles over shared artifacts (who builds on whose repos and sites), giving trophic levels, with tokens flowing up the web; stable webs are nested. The roles "village tooler" and "village helper" in #51 are explicit producers. *Check:* the artifact reuse network; nestedness; trophic levels; token flow.
  *Models:* 06, 05, 08 · *Periods:* #34–#35; #40 (universe); #51
- **HH65 · Multi-information peaks at transitions.** Total correlation among agents' activity spikes around goal switches and natural experiments, as in collective transitions in flocks, then decays as the swarm settles. *Check:* multi-information per window, aligned to switches.
  *Models:* 01, 11, 09 · *Periods:* all switches (NE34); NE12
- **HH66 · #best/#rest: explicit vs. spontaneous symmetry breaking.** The room designation is an operator field. Differences between rooms split into a response to that field and spontaneous divergence, which persists after members swap. *Check:* behavior of agents moved between rooms (NE19 Opus 4.7) vs. room averages; divergence that survives membership changes.
  *Models:* 10, 11, 08 · *Periods:* #35–#51; NE19
- **HH67 · Irreversibility is collective.** Single agents' action sequences are nearly reversible, but the swarm's joint dynamics is irreversible: entropy production in the joint process exceeds the sum over agents. That would be a superagent signature (H01). *Check:* per-agent vs. joint entropy-production bounds (Aguilera hierarchy Σ₁ ≤ Σ₂ ≤ …).
  *Models:* 02, 09 · *Periods:* #51; regime III

**Classic graph analysis: spectra, communities, centrality, temporal and higher-order networks**

Graphs to build from the shared tables:
- **exposure:** who could see whom (`exposure`);
- **reply:** consecutive messages in a room within Δt;
- **mention:** from `chat_core.mentions`;
- **co-activity:** correlated `activity_bins`;
- **artifact co-editing:** once the artifact table exists.

All are weighted and directed where natural, per goal period.

- **HH68 · The Laplacian's spectral gap sets consensus speed.** Diffusion on the interaction graph predicts consensus time ∝ 1/λ₂ (the algebraic connectivity). Periods with a larger λ₂ converge faster. The leading eigenvector picks out the core. *Check:* λ₂ per goal period vs. time to consensus.
  *Models:* 10, 11, 03 · *Periods:* #19, #31, #40 (consensus events); compare across regimes
- **HH69 · Communities follow families before the rooms change and rooms after it.** Modularity-based communities (Louvain or spectral; Potts ground states) align with model families early and with rooms after NE12. *Check:* normalized mutual information (NMI) between detected communities and rooms, families and projects, over time.
  *Models:* 10, 01 · *Periods:* regime I vs. III; NE12 (held out: confirmation only); NE15
- **HH70 · Centrality identifies coordinators.** Eigenvector, PageRank and Katz centrality on the directed mention/reply graph single out coordinators. They agree with the out-influence from kinetic Ising (H02) and Hawkes (H03): triangulation. The Gini coefficient of centrality rises in shared-objective weeks. *Check:* rank correlation of centrality with inferred influence; centrality Gini by mode.
  *Models:* 02, 09, 10 · *Periods:* shared-objective weeks; #26; #45 (held out)
- **HH71 · Rich club and preferential attachment.** A stable rich club of long-tenured agents persists across goals. Newcomers attach preferentially: their contacts are disproportionately high-degree agents. *Check:* rich-club coefficient vs. degree-preserving nulls; newcomer attachment kernel.
  *Models:* 06, 03 · *Periods:* batch joins #10 (NE27), #51 (NE33); whole roster
- **HH72 · Temporal reachability is much smaller than static reachability.** Time-respecting paths limit spread: the set reachable within a day is far smaller than the static graph suggests. Temporal motifs (reply chains, triangles) differ by mode. *Check:* temporal reachability sets; temporal motif counts vs. time-shuffled nulls.
  *Models:* 03, 09 · *Periods:* all non-holdout; regime I vs. III
- **HH73 · The exposure graph percolates.** As the exposure threshold (minimum contacts per day) varies, a giant component appears at a threshold related to the epidemic threshold λ_c = ⟨k⟩/⟨k²⟩. Rooms push cross-room spread below percolation. *Check:* giant-component size vs. threshold, per period.
  *Models:* 03, 10 · *Periods:* before vs. after rooms; #40 (single coordination room)
- **HH74 · Reciprocity is high and hierarchy is low, except in leader weeks.** Mentions and replies are reciprocated (politeness norms). Feed-forward motifs and hierarchy appear mainly in leader weeks. *Check:* reciprocity, triad census, a hierarchy index (e.g. Krackhardt) by mode.
  *Models:* 02, 10 · *Periods:* #26, #45 (held out) vs. shared-objective and free weeks
- **HH75 · Agents prefer their own family.** Agents mention and reply to same-family agents beyond what room co-location explains. *Check:* assortativity coefficient by lab, controlling for room.
  *Models:* 10, 11, 01 · *Periods:* #51 (many families); regime III
- **HH76 · Graph diffusion predicts who adopts a term next.** A heat kernel on the weighted interaction graph predicts which agents adopt a new term next, better than degree alone. *Check:* rank of actual next adopters under heat-kernel vs. degree predictors.
  *Models:* 03, 08, 11 · *Periods:* #20, #42, #43 (held out), #51
- **HH77 · A few collective modes beyond random-matrix noise.** The activity correlation matrix has only 1–3 eigenvalues above the Marchenko–Pastur edge: a "market mode" (schedule / common field), a room mode, a family mode. *Check:* eigenvalue spectrum vs. Marchenko–Pastur; what the top eigenvectors load on.
  *Models:* 01, 11 (random-matrix tool) · *Periods:* each non-holdout period with N ≥ 10
- **HH78 · Multilayer bridges.** The chat, exposure, mention and artifact layers are partly redundant. The multiplex participation coefficient finds "bridge" agents linking rooms and projects. *Check:* inter-layer edge overlap; participation coefficients; bridges vs. roles in #51.
  *Models:* 10, 06 · *Periods:* #40, #51
- **HH79 · Group interactions beat pairwise ones.** Three or more agents in a thread matter beyond pairwise exposure: simplicial (higher-order) contagion. Joint exposure from two agents raises adoption more than two separate exposures do. *Check:* adoption vs. pairwise and triadic exposure counts.
  *Models:* 03, 06 (higher-order contagion, Piñero 2025) · *Periods:* #19, #40, #51

**Mean-field-forward variants: fix a few-parameter model, predict, compare (no N×N J learning)**

The idea: instead of inferring every coupling J_ij (the inverse problem, data-hungry at small N), posit a mean-field model with 1–4 interpretable parameters. Estimate them from a few macroscopic moments, then test the model's *forward* predictions on observables not used in the fit.
- **HH80 · Curie–Weiss explains co-activation (variant of HH01, HH44; H09 E1).** A uniform-coupling Ising model with a time-varying field, m = tanh(β(J₀m + h(t))), has only two parameters. Estimate βJ₀ from the two-moment relation χ = β(1−m²)/(1 − βJ₀(1−m²)), using the observed mean activity and its variance. βJ₀ ≈ 0 in null weeks, is largest in shared-objective weeks, and βJ₀ → 1 marks criticality. *Check:* βJ₀ per non-holdout period; forward-predict the shape of P(K) and the variance ratio.
  *Models:* 01 (mean-field) · *Periods:* all non-holdout; null weeks #10, #17, #20, #39, #41, #42; regime III
- **HH81 · Mean-field Glauber predicts response kernels (variant of HH31, HH46; H04).** Mean-field dynamics, dm/dt = [−m + tanh(β(J₀m + h))]/τ₀, give a relaxation time τ = τ₀ / (1 − βJ₀(1−m²)). The βJ₀ estimated from fluctuations (HH80) should *predict* how fast responses to kicks decay: a consistency test without learning J. *Check:* predicted vs. measured response decay time per regime.
  *Models:* 02 (mean-field), 09 · *Periods:* non-holdout kicks; NE21 and NE23 for confirmation
- **HH82 · Two-block mean field for rooms (variant of HH33; H05).** Rooms are sublattices with coupling J_in within and J_out across (plus fields), fitted from within- and cross-room covariances only. Prediction: J_out → 0 after rooms arrive; J_in unchanged. *Check:* (J_in, J_out) before vs. after room events.
  *Models:* 01 and 02 (mean-field), 10 · *Periods:* regime III rooms; #40; #51 (#focus); NE12 for confirmation
- **HH83 · Leader–follower mean field (variant of HH23; H02).** One leader spin coupled to a mean-field population of followers, with 2–3 parameters (J_lf, J_ff, h). It detects leader weeks from the asymmetric response, with no N×N inference. *Check:* fitted J_lf in #26 and #45 vs. ordinary weeks.
  *Models:* 02 (mean-field) · *Periods:* #26; #44 vs. #45 (held out)
- **HH84 · Mean-field Potts consensus (variant of HH22, HH25, HH26).** A uniform-coupling q-state Potts model predicts a *first-order* jump at a critical coupling βJ_c(q). Estimate βJ from the dominant option's share and its fluctuations; the jump-vs.-gradual call follows. *Check:* jump size and hysteresis vs. the mean-field prediction for the observed q.
  *Models:* 10 (mean-field) · *Periods:* #19, #31, #40; #26 (votes)
- **HH85 · Mean-field O(n) for ideological polarization (variant of HH27–HH29, HH49, HH58; H01 D3).** **m** = L_n(β(J₀|**m**| + h)) **m̂**, where L_n is the n-dimensional Langevin function. Fit (βJ₀, h) per period from polarization and its fluctuations; transverse susceptibility |**m**|/h. *Check:* polarization response at kickoffs; the transverse vs. longitudinal fluctuation ratio.
  *Models:* 11 (mean-field) · *Periods:* #8, #21, #41, #44 (#rest); kickoffs
- **HH86 · Mean-field free energy and hysteresis (variant of HH47, HH49; H09 T1/T2).** f(m) = −J₀m²/2 − hm − T·s(m) develops a double well when βJ₀ > 1. That predicts bistable activity, and hysteresis when a field reverses. Compare it with the Boltzmann-inverted landscapes. *Check:* is the double well predicted wherever the inverted landscape shows one, after removing the field?
  *Models:* 01 (mean-field) · *Periods:* regime III non-holdout; field reversals (NE21 for confirmation)
- **HH87 · Moment-matched spin-glass placement (variant of phase diagram #2).** Estimate the mean and spread of couplings from the first two moments of the correlation matrix (mean-field / TAP relations) rather than inferring J. Place each period on the Sherrington–Kirkpatrick phase diagram. *Check:* agreement with the full-J placement where both are possible.
  *Models:* 01 (mean-field / SK) · *Periods:* all non-holdout
- **HH88 · Mean-field contagion is enough (variant of HH35, HH36).** At N ≲ 30, two-parameter Bass curves (spontaneous p, imitation q) fit meme adoption as well as network models do. Network structure only matters after rooms. *Check:* held-out likelihood of Bass vs. network SIS per meme, before and after rooms.
  *Models:* 03 (mean-field) · *Periods:* #20, #42, #51
- **HH89 · Family-level mean field (variant of HH10, HH75; H01 D1.1.b).** Treat model families as K mean-field populations with a K × K family coupling matrix (e.g. 3 × 3 for the three largest labs) instead of N × N. That tests family homophily in coupling with ~9 parameters. *Check:* within-family vs. cross-family couplings and their stability over time.
  *Models:* 01 and 02 (mean-field) · *Periods:* #51; regime III
- **HH90 · Attention is conserved: cutting a channel redirects coupling to the partners that remain (from the H05 holdout run, 2026-10-03).** After the 03-16 #best/#rest split, cross-room talk coupling fell to ≈0 as predicted. But within-room coupling *rose* about 6× (J_in 0.023 → 0.139, CI excluding 0), which the block model did not predict. If each agent has a fixed attention budget (it reads a fixed amount of context per turn), then removing partners raises the coupling to those left, so Σ_j J_ij is roughly constant across cuts and merges. *Check:* Σ_j J_ij per agent before and after every room event (NE15, 05-04 merge, 05-11 split, #focus, transfers); does row-sum conservation beat the "only the cut pairs change" rival? Rule out #35's fork activity (H07) as a confound.
  *Models:* 02, 10 (two-block mean field), 09 · *Periods:* #35 (NE15), #40/#41 (05-04, 05-11), #focus; H08 (context is the coupling) gives the mechanism

## Round-1 inspired (added 2026-10-03, after H02–H05, H07, H09 and the first holdout runs)

- **HH91 · Longer sessions run hotter.** H04's holdout run found the branching ratio *higher* on 8 h days at all three hours switches (0.67 and 0.89 vs 0.31 and 0.46). Mechanism guess: a longer session accumulates more unread context per turn, so each turn has more to react to, and more activity is triggered by activity. *Check:* within periods, n̂ against session length and against the unread backlog at turn start; non-holdout 4 h vs 8 h segments of #51.
  *Models:* 09, 02 · *Periods:* #51 (non-holdout 8 h stretches), regime III; NE21 already used for H04
- **HH92 · Messages couple to a hidden variable.** The response to a message is a read-out delay (the wait until the agent's next turn) convolved with a fast response. So the response kernel G(τ) should be predictable, *with no free parameters*, from the distribution of inter-turn intervals: a two-variable kinetic Ising model (visible activity plus a hidden "unread context" field). This explains H04's 4-minute dead time and 15-minute plateau. *Check:* predicted G(τ) from turn-interval statistics vs H04's measured kernels, per goal period.
  *Models:* 02, 09 · *Periods:* regime III non-holdout kicks
- **HH93 · Influence lives in content, not timing.** Content transfer (does i's message embedding predict the direction of j's next message, beyond the goal field?) finds leaders that activity timing misses (H02 failed on #45 with timing). *Check:* content transfer entropy or a VAR on whitened vectors; ground truth from #26 (election), #44 (#best fine-tune week); #45 for confirmation, if the holdout policy allows a second hypothesis to use it.
  *Models:* 11, 02 · *Periods:* #13, #26, #40, #44
- **HH94 · Joint silences are platform stalls.** H02's collective co-activation is partly everyone going quiet together. That is a common field (API outages, scaffold restarts), not coupling. *Check:* joint-silence bins vs simultaneous errors or latency spikes across agents in `actions`. Does Curie–Weiss βJ₀ vanish after conditioning on them?
  *Models:* 01, 09 · *Periods:* H02 chunks with lull-sensitive βJ₀; regime I
- **HH95 · Cultural change runs on a touch clock.** H07 found the per-file-touch mutation rate nearly equal across the two RPG forks (ratio 1.0–1.2), while commit and wall-clock rates differ. Is the per-touch rate universal across artifacts, agents and families? *Check:* other shared artifacts in the artifacts tables (#40 the-universe, #44, #51 repos).
  *Models:* 08, 05 · *Periods:* #35, #40, #44, #51
- **HH96 · One agent nucleates re-theming.** In H07, two commits by one agent carried 59–77% of #best's content divergence. Content change in shared artifacts is a nucleation event (heavy-tailed per-agent shares, first-order jumps), not gradual drift. *Check:* the distribution of per-commit and per-agent shares of content change across shared artifacts; are the nucleators the same agents or families?
  *Models:* 10, 08 · *Periods:* #35, #40, #51
- **HH97 · Behavior is a Markov state model with a few metastable sets.** Spectral clustering of the behavior-state transition matrix (Jev states) gives a few slow sets ("attractors": coding, debugging loops, existential talk). The spectral gap, or mixing time, is a per-period order parameter, smallest in stuck periods. *Check:* MSM on Jev states per goal period; implied timescales; compare with H16 traps.
  *Models:* 02, 10 · *Periods:* all non-holdout; #32 and #45 for confirmation
- **HH98 · Steerability differs by model family.** Per-family susceptibility to nudges and to human messages (mean-field χ_f, response amplitude A30): which models are steerable, and by what? *Check:* H04's kernels split by lab within goal periods.
  *Models:* 01/02 (mean-field), 09 · *Periods:* regime III kicks; #51
- **HH99 · Attention dilutes as 1/k.** The probability that an agent responds to a given message falls roughly as 1/k with the number k of messages pending at its turn, so the mean-field J/N normalization is literal. H03 already found per-pair triggering falls with N (ρ = −0.73). This would be the micro-mechanism behind HH90 and the fall of n̂ with N. *Check:* response probability vs pending-message count at the agent's next turn.
  *Models:* 01, 09 · *Periods:* regime III, #51
- **HH100 · One curve for all periods.** Per-period loop gains and branching ratios (H02 βJ₀, H03 n̂, H04 K, H05 J_in/J_out) collapse onto a single function of an operational control parameter, such as messages per agent-turn or N. A data collapse would be the swarm's phase diagram. *Check:* gather the per-period estimates from the G folders; collapse them on candidate control parameters; held-out periods as tests.
  *Models:* 01, 09, 02 · *Periods:* all non-holdout per-period estimates
- **HH101 · Aging.** Day-to-day content autocorrelation C(t_w + τ, t_w) depends on the waiting time t_w since the kickoff, not just the lag τ, as in spin-glass aging. Agents restart daily with memory, which is like field cooling. Longer goals age more. *Check:* whitened agent-day vectors; C as a function of τ at fixed t_w across long goals.
  *Models:* 01 (SK / glassy), 11 · *Periods:* long goals #4, #8, #38, #51
- **HH102 · Private, conflicting goals make #51 a spin glass.** In #51 each agent maximizes a privately assigned goal, and some goals conflict. Content and talk couplings should then have random signs, with frustration (unsatisfied triangles) well above shared-objective weeks. The dynamics should be glassy: many metastable configurations, slow, history-dependent relaxation, and aging (H20). Practical: mixed-motive swarms. *Check:* the sign structure of per-pair content alignment beyond the field; frustration index and an Edwards–Anderson-style overlap between days, against shared-objective weeks; link to H17's mixing times.
  *Models:* 01 (SK / spin glass), 11, 10 · *Periods:* #51 (non-holdout days) vs #38, #40, #44; the #51 tail 🔒 for confirmation
- **HH103 · The debate week (#12) is a two-sublattice antiferromagnet.** Two teams debating should show within-team alignment and cross-team anti-alignment in content. The order parameter is the staggered magnetization m_A − m_B along the debate axis. The judge acts as an external field that is zero during the debate and switched on at the verdict. *Check:* the team-resolved projection of whitened vectors onto the axis separating the teams' positions; the staggered vs uniform magnetization over the week; does the order collapse after the verdict?
  *Models:* 11, 10 (two-sublattice), 01 · *Periods:* #12; the #34 teams 🔒 (saboteurs vs villagers) for confirmation
