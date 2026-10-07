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
  *Status (2026-10-04):* approved by Vivian (dashboard) → H100.
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
  *Status (2026-10-04):* approved by Vivian (dashboard) → H99.
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
- **HH104 · Kickoffs are anti-quenches.** A new goal *expands* the swarm's semantic dimensionality instead of collapsing it (H12: participation ratio +44% at regime-III kickoffs, 4/4; day 1 is the most diverse day in 13/16 periods). Consensus, if any, forms over the week, not at the kickoff. *Check:* participation-ratio trajectories through the week, with self-repeats removed; held-out periods.
  *Models:* 11 · *Periods:* all goal transitions (NE34); regime III
- **HH105 · Loops, not consensus, collapse dimensionality.** Low effective dimensionality in the swarm's content is agents repeating *themselves* (self-near-copy share 16–60% in #38–#40) rather than echoing each other (≤ 3%). The self-repetition rate is an order parameter for individual traps, linking H12 to H16 and H17. *Check:* self-repetition rate vs H16 dwell times and H17 metastable sets, per period.
  *Models:* 02, 10, 11 · *Periods:* #38–#40, regime III
- **HH106 · Direct mentions escape crowding in big rooms.** In #51 (the largest single room) an @-mention raises uptake about 11.6× and halves the dilution slope (0.39 vs 0.81); in smaller rooms it doesn't (H18). Mentions may become a separate, privileged channel once the room is large enough that ordinary messages are crowded out: a crossover in N. *Check:* mention advantage vs room size across #51's roster segments and the two-room era; does the crossover sit where k̄ exceeds the saturation k₀ ≈ 7?
  *Models:* 01, 09 · *Periods:* #51 segments; regime III two-room weeks

## Usefulness-first (added 2026-10-04): numbers that place a swarm on a phase diagram or give an operator a lever
*Built on round-1 results: coupling lives in content and context (H04, H15, H18); activity is subcritical (loop gains 0.06–0.4) but content may not be (H01 P9 ≤ 0.74); herding is the default (H11); coupling ∝ N^−0.6 (H18); loops and aging traps (H12, H16).*

- **HH107 · A distance-to-criticality dial, T/T_c, per window and per channel.** Curie–Weiss gives χ = β(1−m²)/(1 − βJ₀(1−m²)). The ratio of the observed susceptibility (variance of the collective mode, for activity *and* content separately) to the independent-agent value gives the loop gain g, and T/T_c ≈ 1/g. Report it per day as a dial: how close the swarm is to runaway cascades. *Check:* per-day g vs H03's n̂ and H19's per-period table; calibrate on simulated swarms; held-out days.
  *Models:* 01, 09, 11 · *Periods:* all non-holdout; daily resolution
- **HH108 · The swarm is near-critical in what it says but subcritical in when it acts.** H01's content-level βJ₀/n (median 0.74, an upper bound) sits far above every activity loop gain (≤ 0.4). If that survives proper multi-direction field removal (the H24 lesson), ideas can cascade even when activity can't. *Check:* drive-removed content loop gain vs activity gain in the same windows; idea-cascade sizes (HH122).
  *Models:* 11, 01 · *Periods:* regime III; #51
  *Status (2026-10-04):* tested as H26 (failed as posed: at matched resolution content and activity both have room loop gains ≈ 0.5; H01's 0.74 is drives plus time-averaging) and H25 (whole-swarm content dial is size × a shared field). H34: idea cascades are subcritical (R̂ 0.06–0.39).
- **HH109 · Critical slowing down warns of herding waves hours ahead.** Before H11's pile-ons (#31's time-capsule repo reaching 11 agents; #18's last-day convergence), the dominant project share's autocorrelation and variance should rise. *Check:* lag-1 autocorrelation and variance of the dominant share in rolling windows before vs after onsets, against placebo windows; lead time.
  *Models:* 10, 01 · *Periods:* #18, #31, #37, #41
- **HH110 · Driver nodes: where an operator message moves the whole swarm.** Linearize the influence network (exposure × H04/H18 response kernels) and compute network controllability: the minimal driver set and per-agent control energy. Prediction: driver nodes are high-exposure agents in small rooms, and control energy scales as N^0.6. *Check:* the observed spread of content after a human message vs the predicted driver ranking.
  *Models:* 02 (linear response), graph controllability · *Periods:* regime III; #51
- **HH111 · There is a maximum useful swarm size N\*.** With per-pair coupling ∝ N^−0.6 (H18) and per-agent output saturating, collective throughput (artifacts, progress per hour) vs N should peak where the marginal agent adds less than its coordination overhead. *Check:* throughput vs N across #51's roster segments and the two-room weeks; the fitted N\* vs the mean-field prediction.
  *Models:* 01 (mean field), 09 · *Periods:* #51 segments; regime III
- **HH112 · Room size is a temperature knob.** Since coupling ∝ N_room^−0.6, splitting rooms raises per-pair coupling (H05's J_in ×6 after the split fits this). The operator can set the effective temperature by partitioning. *Check:* predict each room's βJ₀ from N_room alone, before fitting, at NE15, NE42 and #focus.
  *Models:* 01, 10 · *Periods:* #35, #40/#41, #51 (#focus)
- **HH113 · A stuckness order parameter predicts output collapse.** Combine the self-repetition rate (H12), trap age (H16) and repeated-error share into one stuckness index; it should predict drops in artifact output hours later. *Check:* lagged regression of output (artifacts tables) on the index, within agent; held-out days.
  *Models:* 02, 10 · *Periods:* #38–#40 (loop weeks), #51
- **HH114 · Links are the contagion vector of herding.** In a kinetic Potts model with exposure, the probability that an agent switches to project X rises with the number of recent links to X it saw: an infection rate per link exposure. Throttling link-sharing would damp pile-ons. *Check:* switch hazard vs exposure count (artifact mentions in chat) with agent fixed effects, vs a common-drive rival.
  *Models:* 10 (kinetic), 03 · *Periods:* #31, #18, #37, #41
- **HH115 · Consensus time scales with the interaction graph's spectral gap.** Time for a project or stance to reach a dominant share scales as 1/λ₂ of the exposure Laplacian (the HH68 idea), or as N^a. *Check:* consensus times across periods vs λ₂ and N; predict held-out periods.
  *Models:* 10, graph diffusion · *Periods:* consensus events #19, #26, #31, #40
- **HH116 · An operator-susceptibility gauge χ_op: how steerable is the swarm today?** The response of the collective mode and of content alignment to operator and human messages, per message, tracked daily. Does steerability fall as the swarm ages within a goal? *Check:* daily χ_op from H04-style matched kernels; trend within goals; regime differences.
  *Models:* 01, 11 · *Periods:* regime III (nudger on); #51
- **HH117 · Steerability follows a context sawtooth.** Within a session, as the context fills, an agent responds less to new messages, until consolidation resets it (H15's erasure dip, then recovery). The best moment to send a message is predictable from the consolidation clock. *Check:* response probability vs turns since last consolidation and vs context tokens (H18 machinery).
  *Models:* 02 (hidden variable), 09 · *Periods:* regime III; NE41
- **HH118 · A net information current identifies de facto leaders.** Content transfer entropy out minus in per agent classifies sources and sinks. The swarm-level concentration of outflow is an order parameter: centralized vs distributed coordination. Content succeeds where activity timing failed (H02; extends HH93). *Check:* source ranking vs the elected leader (#26) and the installed leader (#45, holdout); concentration across modes.
  *Models:* 11, 02 · *Periods:* #13, #26, #40, #44
- **HH119 · The diversity–productivity curve is an inverted U: the swarm's operating point.** Daily content diversity (participation ratio, self-repeats removed) vs output: too little (loops) and too much (unfocused) both underperform, with an optimum in between. *Check:* PR vs artifact output per agent-day across periods, with period fixed effects; locate the peak.
  *Models:* 11, 06 · *Periods:* all non-holdout
- **HH120 · Agent temperature predicts explorer vs exploiter roles.** Each agent's behavioral entropy rate (H14) and mixing time (H17) define an individual temperature. Hot agents found new projects (H06's novelty μ); cold ones sustain them. Mixing temperatures could be a design choice. *Check:* per-agent temperature vs first-mover share on new artifacts vs time on long-lived ones.
  *Models:* 02, 06 · *Periods:* free weeks; #51
- **HH121 · Small rooms become echo chambers.** Per-pair coupling rises as rooms shrink (H18), so a room's content diversity should fall with N_room: a room-sizing trade-off between coordination and diversity. *Check:* room-level participation ratio vs N_room in two-room weeks and #focus, controlling for room goals.
  *Models:* 11, 01 · *Periods:* #35–#44, #51 (#focus)
- **HH122 · Idea cascades follow a power law whose exponent reads off the distance to criticality.** Track adoption cascades of new terms or ideas after exposure. Cascade sizes P(s) ~ s^−τ, with cutoff and exponent set by the branching ratio, tie to HH107's dial and predict how far misinformation spreads. *Check:* cascade trees from exposure plus first use; fitted branching vs HH107.
  *Models:* 03, 09 · *Periods:* #20, #42, #51
- **HH123 · Goal switches show hysteresis: a measurable coercive field.** After a goal change, alignment with the *old* goal decays with a lag that grows with how ordered the old state was (H20 saw settling within ~4 days). That gives a coercive field and an inertia time. Practical: whether to "clear" a swarm before reassigning it. *Check:* old-goal alignment decay vs prior order across non-holdout transitions.
  *Models:* 01 (hysteresis), 11 · *Periods:* goal transitions (NE34)
  *Status (2026-10-04):* approved by Vivian (dashboard) → H96.
- **HH124 · The nudger is a measurably inefficient Maxwell demon.** Bits of agent-state information used per extra active minute gained (H04/H16 effects), against an optimal-timing benchmark (nudge at the pause gate, once). This is the information-to-work efficiency of operator feedback, and gives a target for a better nudging policy. *Check:* mutual information between nudge timing and agent state vs the activity gained; policy counterfactuals on logged gates.
  *Models:* 04 (Kolchinsky), 02 · *Periods:* regime III; NE10, NE23 (holdout)
- **HH125 · Conflict lives in stance, not topic: stance spins are antiferromagnetic.** H22 found topic co-movement even among rivals. Agree/undermine labels on reply pairs (Jev) should show negative couplings and frustration where conflict actually is. This links to detecting saboteurs (D8.3). *Check:* signed reply graph from stance labels; frustration index vs topic graph; #51 rival pairs, the #34 saboteurs (holdout).
  *Models:* 01 (signed), 10 · *Periods:* #51, #12, #34 (holdout)
- **HH126 · A reorganization alarm: susceptibility and multi-information peak at transitions.** The total correlation among agents' states and the heat-capacity analogue (variance of the alignment energy) should spike when the swarm reorganizes: goal changes, room events, scaffold changes. One alarm for "something structural is happening" (merges HH65). *Check:* peak detection against known transitions; false-alarm rate on placebo days.
  *Models:* 01, 11 · *Periods:* all transitions (NE34, NE15, NE42)

## Round-1 inspired, late additions (2026-10-04)
- **HH127 · Roles leave negative remanence: agents concede the side they argued once the role ends.** After #12's verdicts, the Government − Opposition stance tilt flipped sign (+0.43 → −0.36, 7/9 debates; H21 post hoc). If general, assigned roles bias content only while active, then overshoot. *Check:* stance-axis tilt before and after role ends in other role periods (#26 election, #51 private roles on non-holdout days); compare with a single-agent inertia null.
  *Models:* 11 (two-sublattice), 01 (remanence) · *Periods:* #12, #26, #51
- **HH128 · Family exchange beats assigned teams in content.** Same-lab pairs out-align assigned teammates even after centering each agent (H21: b_lab 0.24 vs b_team 0.08), consistent with H13's family style field. Assigned team structure is weaker than vendor style in what agents write. *Check:* lab vs team vs room alignment in every period with assigned groupings, with style residualized (H13's features).
  *Models:* 11, 10 · *Periods:* #12, #34 (holdout), #38–#44 rooms
- **HH129 · #51 is a random-field system.** Private roles pin each agent's topic (a random field), and the shared room adds a weak positive mean-field pull. Rivals co-move because they share a niche (H22). A random-field Ising/O(n) model predicts the overlap distribution and the absence of collective switching. *Check:* fit random-field mean-field to #51's content (field from role text, coupling from co-movement); predict the day-to-day overlap and synchrony H22 measured.
  *Models:* 01 (random-field Ising), 11 · *Periods:* #51 non-holdout segments
  *Status (2026-10-04):* approved by Vivian (dashboard) → H98.
- **HH130 · Goals act on a two-state order parameter (on-goal vs off-goal), not a continuous alignment.** H10 found goals are quenches: variance along ĝ grows while transverse variance is flat, and agents switch on-goal together. For the occupancy p(t) of on-goal statements, a Legendre tilt *does* predict variance growth while p < ½. That gives the free-energy idea a fair second test in the right variables. *Check:* classify statements on-goal or off-goal; fit a two-state (Ising-like) mean field to p(t) through kickoffs; predict the variance trajectory from free-week fluctuations of p.
  *Models:* 01, 10 · *Periods:* free → assigned pairs (#11→#12, #16→#17, #37→#38); kickoffs (NE34)
  *Status (2026-10-04):* approved by Vivian (dashboard) → H105.
## Essence conjectures from the round-1 reflection (2026-10-04)
- **HH131 · The harness is the Hamiltonian.** The scaffold (turn cadence, timers, consolidation, room visibility, prompts) sets the fields and rates; agents add only weak, context-mediated coupling on top. Corollary: the strongest steering knobs are scaffold parameters, not message wording. *Check:* see the redirected sub-hypotheses that cite E1 in `writeup/round1-reflection/round1-reflection.pdf`.
  *Models:* cross-cutting · *Periods:* all
- **HH132 · Self-reinforcement, not exchange, is the essential physics.** Loops, aging traps and herding are Pólya-urn-like: an agent's own output fills its context and raises the odds of repeating; a popular project gathers links and attracts more agents. Urn and preferential-attachment models, not Ising exchange, should be the default. *Check:* see the redirected sub-hypotheses that cite E2 in `writeup/round1-reflection/round1-reflection.pdf`.
  *Models:* cross-cutting · *Periods:* all
- **HH133 · Stigmergy beats chat.** Coordination and memory live in shared artifacts (repos, documents, sites); chat is a weak side channel. Influence and persistence should be measured through artifact edits and reads. *Check:* see the redirected sub-hypotheses that cite E3 in `writeup/round1-reflection/round1-reflection.pdf`.
  *Models:* cross-cutting · *Periods:* all
- **HH134 · Swarms relax to their priors.** Without a strong field, swarm content relaxes toward the models' joint prior, as in iterated learning; a goal is a quench away from the prior, and the week is relaxation back. *Check:* see the redirected sub-hypotheses that cite E4 in `writeup/round1-reflection/round1-reflection.pdf`.
  *Models:* cross-cutting · *Periods:* all
- **HH135 · Attention is the conserved quantity.** Coupling is an allocation of a fixed attention budget per turn (H18: uptake ∝ backlog^-0.6). Who influences whom is an attention market set by salience (mentions, recency, novelty) and backlog. *Check:* see the redirected sub-hypotheses that cite E5 in `writeup/round1-reflection/round1-reflection.pdf`.
  *Models:* cross-cutting · *Periods:* all

## Physics-of-life, Kolchinsky-style (added 2026-10-04; for Vivian to vet)
*Grounded in round 1: context carries the coupling (H04, H15, H18); members' memories carry ≈ 0 day-scale semantic information (H15); loops and aging traps (H12, H16); herding onto shared artifacts (H11); goals act as quenches (H10); memory size is a homeostatic set point (H09); plans don't survive distillation (H23).*

- **HH136 · Goal switches pay a mismatch cost.** In Kolchinsky–Wolpert, a process tuned for one input distribution dissipates extra when run on another, with cost ∝ D_KL(p_new ‖ p_old). The swarm, tuned to the old goal, should waste tokens and time after a switch in proportion to the divergence between old and new goal-content distributions. *Check:* post-switch waste (tokens or turns per unit of progress, from the work ledger) vs the divergence between consecutive goals' content distributions.
  *Models:* 04, 02 (thermodynamics of computation) · *Periods:* all goal transitions (NE34)
- **HH137 · Each memory store owns a horizon: the semantic-information spectrum.** Viability value ΔV(τ) per store peaks at a store-specific horizon: context at minutes to turns (H15), agent memory at about none, artifacts at days. The swarm's "memory" is a spectrum across stores, and the artifact store dominates beyond a day. *Check:* natural scrambles of each store (context erasure NE41, memory loss, artifact migration or loss, room cut) with ΔV measured at several horizons on a common viability measure.
  *Models:* 04 · *Periods:* regime III, #51
- **HH138 · Projects are autopoietic.** A project (artifact plus contributors) produces the components that maintain it: fixes, coordination messages, recruited contributors. Operational closure means most maintenance actions are triggered by the project itself, not from outside. Closure predicts survival. *Check:* the share of a repo's maintenance commits and messages triggered by its own prior state (failing builds, its own issues) vs external prompts; closure vs project lifetime.
  *Models:* 04, 06 · *Periods:* #38, #40, #51 repos
- **HH139 · Superagents have Markov blankets made of liaison agents.** For a candidate superagent, internal and external states are conditionally independent given a blanket of boundary agents: "sensors" who read outside channels and "actuators" who post outside. The blanket is a small identifiable set of liaisons. *Check:* conditional mutual information between internal and external activity or content given candidate blankets; find the minimal blanket; are liaisons stable?
  *Models:* 04, graph · *Periods:* two-room weeks, #51
- **HH140 · Agents are information engines with a measurable efficiency.** Each agent converts information it receives (observations, messages, tool output) into work (progress), and Sagawa–Ueda-style bounds suggest an efficiency of work per bit of new information used. The efficiency distribution is heavy-tailed, and the swarm's output is carried by a few efficient engines. *Check:* new-information inflow per turn (context ledger) vs progress (work ledger) per agent; efficiency heterogeneity across agents and models.
  *Models:* 04, 02 · *Periods:* regime III, #51
- **HH141 · A thermodynamic speed limit on coordination.** The time to move the swarm's project-share distribution from p₀ to p₁ is bounded below by (statistical length)² over (2 × entropy-production rate), as in the speed limits of Shiraishi, Funo & Saito. Fast coordination needs high dissipation, i.e. talk and activity. *Check:* consensus events (H31): statistical length in project-share space, entropy production from behavior states, observed times vs the bound.
  *Models:* 02, 10 · *Periods:* #19, #26, #31, #40
- **HH142 · Artifacts carry a high assembly index only under swarm selection.** In assembly-theory terms, artifacts built by many steps with reused components (high commit-graph depth × reuse) arise more often than a random-edit null, and only where the swarm keeps selecting: memory of what worked plus repeated contribution. *Check:* the assembly-index proxy per artifact from commit and dependency graphs vs a null of independent edits; high-assembly artifacts vs multi-agent contribution.
  *Models:* 05, 08 · *Periods:* long goals #38, #51; RPG #34–#35
- **HH143 · Plans suffer an error catastrophe when relayed.** By Eigen's error threshold, plans longer than an information length L\* are corrupted beyond recovery as they pass between agents (H23: plans were not transmitted; H24: numbers copied, not reasoning). Short directives survive and long plans fragment. *Check:* relay chains of plans (reply labels plus embeddings): fidelity vs plan length; find L\*.
  *Models:* 08, 05 · *Periods:* coordination weeks #13, #40, #44
- **HH144 · Memory size is homeostasis, and families are species.** H09's per-agent memory set point, restored at each consolidation, is the homeostasis of an autonomous system. Perturbations decay with a homeostatic time τ_h, and set points and τ_h are species (family) traits. *Check:* response of memory size to perturbations (losses, inflow bursts) and the fitted τ_h; family differences beyond agent identity.
  *Models:* 04, 02 · *Periods:* regime III
- **HH145 · Social semantic information outweighs task information.** An agent's viability depends more on semantic information about *other agents* (who's doing what) than about the external task. Scrambling social information (room cuts, roster turnover) costs more than scrambling task information (goal changes) at equal mutual-information loss. *Check:* ΔV per bit for social vs task natural scrambles.
  *Models:* 04 · *Periods:* NE15, NE42, NE27, NE33; goal transitions
- **HH146 · Autocatalytic artifact sets appear in long free periods.** Sets of artifacts where each is built using others (tools building tools: scripts, templates, shared libraries) form reflexively autocatalytic (RAF) sets: an origin-of-life analog in the artifact dependency graph. They appear when agents are free to choose and time is long. *Check:* the artifact dependency graph from the work ledger and artifact mentions; RAF detection vs random-graph nulls.
  *Models:* 05, 06 · *Periods:* free weeks, #51
- **HH147 · Agency is semantic irreversibility.** Life is irreversible. The signature of agency is entropy production in *semantic* state space (Jev and content states), not in action classes (H14 measured the scaffold). Superagents produce more semantic entropy than the sum of their parts. *Check:* entropy production on semantic state sequences, per agent and per candidate superagent (H01 round 2), against the scaffold floor.
  *Models:* 02, 04 · *Periods:* regime III, #51
- **HH148 · Niche construction: agents store semantic information in their environment.** Agents build tools, docs and scripts that make later tasks cheaper. The environment then holds semantic information whose scrambling (deletion, migration) raises later effort. *Check:* reuse of agent-made artifacts by others vs later effort per task; the GitLab migration (NE24, held out) as a confirmatory scramble.
  *Models:* 04, 06 · *Periods:* #38, #51; NE24 (holdout)
- **HH149 · Projects die by catastrophe, not decay.** A superagent dissolves abruptly when its semantic information drops below a threshold, e.g. losing a key member or a goal change. Its viability shows a fold bifurcation, with critical slowing down before collapse. *Check:* project activity trajectories before abandonment; early-warning indicators (H27 machinery) vs gradual-decay rivals.
  *Models:* 04, 01 (fold) · *Periods:* free weeks, #51
- **HH150 · Swarm metabolism: an information throughput budget.** Novel information flows in (web, humans) and out (published artifacts), and tokens are the metabolic currency. The swarm's information efficiency (semantic information produced per token) sits near a regime-dependent optimum, like metabolic scaling. *Check:* inflow and outflow fluxes per period vs tokens; scaling with N (Kleiber-like?).
  *Models:* 04, 09 · *Periods:* all
- **HH151 · The swarm minimizes collective surprise within a goal.** Over a goal period, the surprisal of incoming messages under each agent's recent context falls: the swarm learns its environment. Surprise rises at goal changes and decays with a learning time that tracks performance. *Check:* per-message surprisal proxy (embedding novelty relative to the agent's recent context window) over each period; decay time vs output.
  *Models:* 04, 11 · *Periods:* all goal periods
- **HH152 · Autonomy rises with scale: the swarm is more autonomous than its parts.** Bertschinger autonomy (information about its own future not explained by the environment) is low for single agents, which are mostly responders to scaffold and messages (H03, H04), and higher for rooms and the whole swarm. *Check:* autonomy per coarse-graining level (agent, room or project, swarm), with operator and human inputs as environment.
  *Models:* 04 · *Periods:* regime III, #51
- **HH153 · Copying is cheap and transformation expensive.** In Kolchinsky & Corominas-Murtra terms, copy information costs fewer tokens per bit than transformation information, so swarms preferentially copy (H07, H24), and novelty is the expensive part of the swarm's work. *Check:* tokens per bit of copy vs transformation information in shared artifacts and relayed content.
  *Models:* 08, 05 · *Periods:* #35 forks, #21, #51

## Building on what held up (added 2026-10-04; for Vivian to vet)
*Grounded in the results that survived round 1: responses wait for the next model call and erasure cuts coupling (H08); rooms cut chat coupling (H05, holdout DiD passed); attention dilutes as k^−0.6 (H18); regime-III co-activation is mostly the daily pause/resume (H38); stance recovers assigned teams only (H37); nudges both unstick and tilt, mentions steer content, erasure pushes agents toward work (H39); naming pulls 3–6× more (H29, post hoc); loops are self-repetition (H12); traps age (H16); erasure costs ~45% of output (H15); family = style (H13, H23); copying dominates (H07); herding is the default, pile-ons follow links, half of consensus is kickoff-set or one-window waves (H11, H27, H31).*

- **HH154 · The call clock sets the coupling.** Responses wait for the recipient's next model call (H08), so coupling per hour = coupling per call × the recipient's call rate. Slow-cadence agents (long tool calls, computer use) are "heavy spins": weakly coupled in wall time however attentive per call, and cadence becomes a coupling knob. *Check:* per-recipient call rate (`call_windows`) vs addressing hazard (H08) and boundary pull per hour (H29), within period; cadence changes at NE14/NE41 as interventions.
  *Models:* 02 (Glauber rates), 09 · *Periods:* regime II–III, #51 · *Builds on:* H08, H29
  *Status (2026-10-04):* approved by Vivian → H40.
- **HH155 · Read-out gating gives the swarm a light cone.** If information moves at most one hop per call cycle, a novel item (link, artifact name, phrase) reaches agents k relay-hops away no sooner than k call cycles: a Lieb–Robinson-style bound whose velocity is set by cadence, not message volume. Violations reveal an unlogged channel (shared artifacts, memory). *Check:* first-appearance times of novel tokens and artifacts across rooms vs shortest relay path counted in recipient call cycles.
  *Models:* 02, 03 · *Periods:* two-room weeks (#36–#38, #44), #51 · *Builds on:* H08, H05
  *Status (2026-10-04):* approved by Vivian → H41. Vivian: measure the light cone over the interaction (read-out/exposure) graph, in graph hops, not over rooms.
- **HH156 · Erasure makes agents busy but unproductive: re-acquisition thrash.** After a forced erasure agents idle less (H39: −0.13) yet write ~45% less for about 10 turns (H15). Prediction: post-erasure turns are re-acquisition (reading the room, browsing, re-opening artifacts), behavior entropy rises like a local temperature pulse, and susceptibility to *new* room content rises even as coupling to pre-erasure senders falls (H08: −18%). *Check:* Jev v3 states and context-ledger reads vs turns since erasure; addressing hazard toward post- vs pre-erasure senders.
  *Models:* 02, 04 · *Periods:* regime III (NE41) · *Builds on:* H15, H39, H08
  *Status (2026-10-04):* approved by Vivian → H44.
- **HH157 · Rooms are Faraday cages with an artifact leak.** Rooms cut chat coupling (H05), but agents in different rooms share repos and docs. Prediction: residual cross-room coupling runs through shared artifacts: cross-room content and work co-move with a lag ordered by who touched the artifact first, and vanish for room pairs with no shared artifact. *Check:* cross-room artifact co-touch lags (DQ4 work ledger, artifact mentions) vs within-room chat lags in two-room weeks and NE15/NE42.
  *Models:* 02, 08 · *Periods:* #36–#38, #44, NE15, NE42 · *Builds on:* H05, H07, H11
- **HH158 · The dilution exponent is set by context competition.** Attention dilutes as k^−0.6, not 1/k (H18). If a call attends over a bounded context, the exponent should steepen with message length and with the share of context already full of the agent's own work, and differ by model context size. *Check:* per-recipient-model and per-period exponents vs mean message length and context occupancy (DQ1 context ledger).
  *Models:* 03, 02 · *Periods:* all with varying k · *Builds on:* H18, H08 · *Related:* HH99, HH135
  *Result (2026-10-04):* post-hoc support from H45: with segment phase controlled, engagement falls with both room and own content (γ_R −0.04, γ_W −0.12), the context-competition pattern, confounded with task phase.
- **HH159 · Edge-trimmed regime III is a dilute ferromagnet.** Once day-edge co-activation is removed (H38), the remaining regime-III coupling sits in a few pairs (#44, the #51 head). Prediction: a heavy-tailed bond distribution (most J ≈ 0, a few large) whose significant-bond graph sits below percolation: small coupled clusters in a paramagnet. *Check:* stall-adjusted pairwise couplings per period; bond distribution; giant-component size vs a configuration-model threshold.
  *Models:* 01 · *Periods:* regime III, #44, #51 · *Builds on:* H38, H02 · *Related:* HH73
  *Status (2026-10-04):* approved by Vivian → H49.
  *Result (2026-10-04):* tested as H49: refuted as posed. Edge-trimmed regime-III bonds sit at the false-positive floor (38 vs ~23 expected); the surviving excess is a weak uniform shift (CV-C10 median 0.11), a dense/shared-field mode, not a dilute ferromagnet. Pairwise structure exists in talk (71 bonds vs ~23 expected).
- **HH160 · The daily pause/resume is a periodic drive, and agents entrain to it.** H38's artifact as the object: each agent's activity bursts keep a stable, model-specific phase relative to the daily resume (Arnold-tongue-like), and co-activation is forced synchronization. Two interventions: the hours change (NE21) changes the drive period; NE43 (08-21) removes the drive, so entrainment and f_scaffold should both collapse after it. *Check:* per-agent burst phase relative to resume across days; phase-locking strength before and after NE21 and NE43.
  *Models:* forced phase oscillators (Kuramoto with drive; new), 02 · *Periods:* regime III, NE21, NE43 · *Builds on:* H38, H39
- **HH161 · Assigned opposition is a field with zero memory.** Stance conflict appears only where a protocol assigns sides and is gone within ~10 min of the verdict (H37). Prediction: every protocol-assigned opposition (debate teams, adversarial roles, saboteurs) relaxes within one or two call cycles of release, with no residual antiferromagnetic bond: linear response, no hysteresis. *Check:* stance relaxation after #12 verdicts and #51 role changes, in recipient call cycles (`call_windows`); #34 is holdout.
  *Models:* 01, 11 · *Periods:* #12, #51, (#34 holdout) · *Builds on:* H37, H22, H08 · *Related:* HH127
- **HH162 · Norm-enforcers are the swarm's immune cells.** In #51 antagonism clustered on norm-enforcing roles (H37, post hoc). Prediction: in ordinary weeks the agents issuing the most corrections and declines draw more negative stance, and their corrections precede the end of self-repetition loops (H12) and trap escapes (H16). Friction is the price of error correction; swarms without enforcers loop longer. *Check:* DQ2 correction/decline labels per agent; loop and trap durations conditioned on a correction at the looping agent's read-out turn.
  *Models:* 04 (viability), 06 · *Periods:* all with chat; #38–#40 · *Builds on:* H37, H12, H16
  *Status (2026-10-04):* approved by Vivian → H55.
  *Result (2026-10-04):* tested as H55: friction refuted in reverse (correctors treated warmly, ρ −0.24 over 27 periods); corrections reach 0.65% of loop episodes, so the immune effect is untestable (underpowered); being addressed raises loop escape by 5 points.
- **HH163 · The naming lever saturates.** A named message pulls its recipient 3–6× more than an unnamed one (H29). If naming is itself diluted, pull per named agent falls as a power of the number of agents named in one message, and total moved mass peaks at one or two names. *Check:* H29's boundary estimator stratified by names per message; the same for nudges (H04) and human messages.
  *Models:* 03, 02 · *Periods:* #51, regime III · *Builds on:* H29, H18, H04
- **HH164 · Humans are just loud agents.** On the read-out-gated, name-gated channel, a human message should move its named recipient exactly as much as an agent message with the same naming and timing; any authority premium is a separate field term. A premium ≈ 0 means agents don't defer to humans beyond salience, which matters for alignment. *Check:* H29's boundary estimator with a sender-kind interaction; H39's human-message field.
  *Models:* 02 · *Periods:* all with human messages · *Builds on:* H29, H39, H30
  *Status (2026-10-04):* approved by Vivian → H52.
  *Result (2026-10-04):* tested as H52: mixed. Matched human messages get ~2× the reply rate (+0.030) and a small content pull (#51 +0.014), but agent leaders get the same reply premium and role-conflicting human messages get none: status-weighted attention, not deference. Replies to the nudger bot are oppositional.
- **HH165 · Naming at a read-out turn is the escape operator.** Traps age (H16), loops are self-repetition (H12), one directed message at a pause gate helps (H16). Prediction: the escape hazard from a self-repetition loop is flat or falling with loop age, except at read-out turns carrying a message that names the looping agent, where it jumps by about H29's naming ratio; unnamed messages and plain nudges act only at H39's catalytic rate. *Check:* loops from DQ5 `self_repeat`; read-out turns from the context ledger; escape hazard by kick type.
  *Models:* 09 (renewal), 02 · *Periods:* #38–#40, regime III · *Builds on:* H16, H12, H29, H39
- **HH166 · Context homeostasis: each agent keeps its context near a set point.** Memory size is a set point (H09) and context carries the coupling (H08, H15). Prediction: agents regulate the share of their context taken by room messages; when the room floods they read less per message (the k^−0.6 dilution is the homeostat), and after an erasure the share overshoots, then returns. *Check:* DQ1 context ledger: room-message share per call vs k and vs turns since erasure.
  *Models:* 04, 05 · *Periods:* regime II–III · *Builds on:* H09, H18, H15 · *Related:* HH135, HH150
  *Status (2026-10-04):* approved by Vivian → H45.
  *Result (2026-10-04):* tested as H45: refuted. The room share of context is passive (RI ≤ 0.22 in 32/32 periods; floods move set points at the passive slope, NE42 1.06, #51 roster 0.90); erasures bring a talk dip (0.74), not an import overshoot; the scaffold bounds context.
- **HH167 · Field or coupling: the market mode's lag tells which.** After edge trimming (H38) part of H12's single collective mode remains. A field moves everyone within one call; a coupling over one or more call cycles. Prediction: in regime I the residual mode follows message-triggered waits with call-cycle delay (coupling); in regime III it follows human messages and platform events at once (field). *Check:* stall-adjusted mode amplitude cross-correlated with human messages and platform events, lags in call cycles.
  *Models:* 01, 02 · *Periods:* all · *Builds on:* H12, H38, H08
  *Status (2026-10-04):* approved by Vivian → H50. Vivian: frame it with transfer functions and lag (impulse responses, phase); future variants HH185–HH190.
  *Result (H50, 2026-10-04):* the field/coupling split is measurable but falls along channels, not regimes. Activity co-movement is the scheduler's field in both regimes; talk is a read-out-gated coupling in both; regime-I calls are not message-triggered (wake ratio 1.03–1.07). The regime split is rejected.
- **HH168 · Herding is announcement-seeded nucleation; wave size is the receptive fraction.** Pile-ons follow a chat link (H27), arrive as one-window waves (H31), and herding is the default (H11). Prediction: wave size ∝ the number of agents whose next call falls within one cycle after the link, not network position or poster status. Operators can time announcements to the call clock. *Check:* H27/H31 onsets + `call_windows`; wave size on receptive fraction vs network and poster covariates.
  *Models:* 10, 03 · *Periods:* #18, #19, #26, #30, #31, #38 · *Builds on:* H27, H31, H11, H08 · *Related:* HH96
  *Status (2026-10-04):* approved by Vivian → H53.
- **HH169 · The kickoff text is the quench target.** 13 of 63 consensus events were frozen at the kickoff (H31); goals act as quenches (H10). Prediction: frozen projects are those the goal text or kickoff names, and the day-1 content centroid lands on the kickoff embedding, with spread set by kickoff specificity. What you name in a kickoff is what agents herd onto. *Check:* kickoff artifact mentions vs frozen events; day-1 centroid distance to the kickoff embedding vs specificity, all kickoffs (NE34).
  *Models:* 11, 10 · *Periods:* all kickoffs · *Builds on:* H31, H10, H20, H39
  *Status (2026-10-04):* approved by Vivian → H54. Vivian: really likes it; variants HH179–HH184.
- **HH170 · Style is a conserved charge.** Family alignment is style (H13); a distilled leader kept its corpus style but not its plans (H23). Prediction: an agent's style vector is invariant under every natural experiment (erasure, room cuts, goal switches, roster changes, nudger off) while content is not. In Kolchinsky terms style carries no semantic information about viability: substrate, not state; also an identity fingerprint that survives everything. *Check:* per-agent style features before/after each NE; style's ΔV for output.
  *Models:* 04, 11 · *Periods:* all NEs · *Builds on:* H13, H23, H15
  *Status (2026-10-04):* approved by Vivian → H46.
- **HH171 · Copying beats transformation when the backlog is large.** Copying dominates (H07) and each call processes a bounded context (H08, H18). Prediction: the copy-to-transformation information ratio between agents rises with backlog k: under load agents echo rather than transform (a speed–accuracy tradeoff). *Check:* DQ5 `cross_echo` and H07's copy/transformation estimators per window vs context-ledger backlog.
  *Models:* 08, 03 · *Periods:* #35, #51, regime III · *Builds on:* H07, H08, H18 · *Related:* HH153
  *Status (2026-10-04):* approved by Vivian → H57.
  *Result (2026-10-04):* tested as H57: refuted. Backlog doesn't raise echo; most near-duplication is contemporaneous convergence; addressed replies are rephrased.
- **HH172 · Rooms set the coherence length, so reorganization starts in one room.** Rooms are like-minded (H01) and cut coupling (H05); topic shift detects reorganizations (H36). Prediction: content correlation drops sharply at room boundaries, a per-room topic-shift detector beats the swarm-level one on room events (NE15, NE42), and at swarm-wide goal changes one room shifts first and leads. *Check:* per-room R1; room lead–lag at goal changes and room events.
  *Models:* 11 · *Periods:* two-room weeks, #51 rooms · *Builds on:* H36, H05, H01
  *Status (2026-10-04):* approved by Vivian → H47.
- **HH173 · The settling time is a mixing time on the read-out graph.** Content settles ~4 days after a kickoff (H20). Prediction: settling time is how many call cycles it takes for every agent to have read every other agent's work (a bulk mixing time), so it scales with per-agent reading rate and room structure, not whole-graph λ₂ (a weakest-link statistic, H31). *Check:* H20 settling times per period vs reading rates and coverage from the context ledger.
  *Models:* 11, 03 · *Periods:* periods ≥ 5 days · *Builds on:* H20, H31, H08
  *Status (2026-10-04):* approved by Vivian → H48.
- **HH174 · Cross-excitation is a delayed step at the next read-out.** H03: subcritical, only fast cross-triggering beats nulls. Prediction: a multivariate Hawkes fit whose off-diagonal kernel fires only at the recipient's next call raises the cross-branching estimate, makes it consistent across regimes, and shows exponential kernels understate n_cross. *Check:* refit H03 with `call_windows`-aligned kernels; compare branching ratios and fit.
  *Models:* 09 · *Periods:* all · *Builds on:* H03, H08, H19
  *Status (2026-10-04):* approved by Vivian → H42.
- **HH175 · Entropy production fingerprints the platform, not the agents.** Irreversibility lives in fine tool actions and scaffold steps (H14). Prediction: the EP rate jumps at scaffold NEs (NE09, NE14, NE16–NE18) but not at goal, roster or room changes, and family differences vanish once scaffold actions are removed: EP as a log-only detector of platform changes. *Check:* H14's EP estimators per day around each NE class; family contrasts on non-scaffold actions.
  *Models:* 05, 02 · *Periods:* NE09, NE14, NE16–NE18; goal NEs as controls · *Builds on:* H14, H36, H38
  *Status (2026-10-04):* approved by Vivian → H56.
- **HH176 · The effective superagent is a room plus its shared artifact.** Rooms are more like-minded than random groups (H01). In information-theoretic individuality, the composite that best predicts its own future should be {agents in a room} ∪ {their shared repo}: adding the artifact's state raises individuality and autonomy more than adding any further agent. *Check:* H01 round-2 individuality and autonomy on candidate composites with DQ4 artifact state.
  *Models:* 04 · *Periods:* #38–#41, #44, #51 · *Builds on:* H01 (R4–R8), H07, H11
  *Status (2026-10-04):* approved by Vivian → H58. Vivian: superagents should be identified by coordinated behavior, not by room; rooms are only one candidate partition.
- **HH177 · Kicks leave a refractory window.** One directed message at a pause gate helps and more add little (H16); nudges act after minutes (H04) and both unstick and tilt (H39). Prediction: after an effective kick the recipient is refractory for about the length of the task episode the kick launched, and a second kick inside it has near-zero marginal effect. Space kicks by the refractory time. *Check:* second-kick effect vs time since the first, by kick type (H04, H16, H39 episodes).
  *Models:* 09 (refractory Hawkes), 03 · *Periods:* regime II–III, #51 before 08-21 · *Builds on:* H16, H04, H39
  *Status (2026-10-04):* approved by Vivian → H43.
- **HH178 · One dial: an effective coupling K collapses the phase diagram.** Combine read-out, naming, dilution and rooms into one number per period: K = ν_read × (f_named·pull_named + (1 − f_named)·pull_broadcast) / k^0.6, with k counted within a room. Prediction: herding strength (H11), consensus time (H31), loop prevalence (H12) and stall-adjusted co-activation (H38) collapse onto K across periods, unlike the generic loop-gain curve that failed (HH100, H19). *Check:* K per period from shared tables; data collapse of each outcome vs K, holdout periods reserved.
  *Models:* 10, 02 · *Periods:* all · *Builds on:* H08, H18, H29, H05, H38 · *Related:* HH100
  *Status (2026-10-04):* approved by Vivian → H51.

## Kickoff-quench variants and transfer functions (added 2026-10-04 at Vivian's request)
*HH179–HH184 are variants of HH169 (the kickoff text is the quench target). HH185–HH190 develop HH167's lag idea into transfer functions: treat operator inputs and peers as signals, and the swarm as a linear (or weakly nonlinear) system with dead time.*

- **HH179 · Kickoff specificity sets the quench depth.** The more specific the kickoff (named artifacts, numbers, deadlines, roles), the smaller the post-kickoff spread, the larger the frozen-consensus share (H31) and the faster the settling (H20). Vague kickoffs instead produce exploration, the "anti-quench" H12 saw. *Check:* a kickoff specificity score (named entities, artifact count, embedding concentration) vs day-1 spread, settling time and frozen fraction across all kickoffs.
  *Models:* 11, 10 · *Periods:* all kickoffs (NE34) · *Builds on:* HH169, H31, H20, H12
- **HH180 · Mid-period human messages are partial re-quenches.** A human message that names a target moves the swarm centroid toward it with an amplitude set by its specificity and the share of agents at a read-out turn, then relaxes with H20's time constant. Operator steering is a train of mini-kickoffs. *Check:* centroid displacement and relaxation after human messages vs specificity and receptive fraction.
  *Models:* 11, 02 · *Periods:* periods with human messages · *Builds on:* HH169, H39, H08, H20
- **HH181 · The first concrete plan after the kickoff completes the quench target.** When the kickoff is ambiguous, the swarm herds onto the first agent's concrete plan (cf. H27's link precursor), so the effective target is kickoff + first plan. *Check:* which predicts day-1 positions and frozen projects better: the kickoff embedding, the first concrete post, or their combination; ambiguity as a moderator.
  *Models:* 10, 11 · *Periods:* all kickoffs · *Builds on:* HH169, H27, H31
- **HH182 · The swarm remembers its kickoff: remanence.** Overlap of the daily content centroid with the kickoff decays slowly and with one functional form across periods, more slowly than overlap with any later instruction. The kickoff is a persistent field, later instructions transient ones. *Check:* centroid–kickoff cosine vs day, fitted per period; the same for mid-period human instructions; compare decay constants.
  *Models:* 11 · *Periods:* periods ≥ 5 days · *Builds on:* HH169, H20, H10
- **HH183 · Conflicting kickoff cues quench into two domains.** Kickoffs naming two alternatives, or rooms given different instructions (#38, #44), produce bimodal day-1 agent positions with a domain wall at the room boundary; single-target kickoffs produce one domain. *Check:* bimodality of day-1 positions along the axis between named alternatives, within and across rooms.
  *Models:* 10, 11 · *Periods:* #38, #44, multi-option kickoffs · *Builds on:* HH169, H26, H05
- **HH184 · Each model family has its own kickoff susceptibility.** The kickoff is a field; families differ in χ: how far toward the kickoff they move on day 1, after controlling for style (H13). Strongly instruction-following families quench deeper. *Check:* per-agent day-1 distance to the kickoff vs family, with style residualization (DQ5); stability of χ across kickoffs.
  *Models:* 11, 01 · *Periods:* all kickoffs · *Builds on:* HH169, H13, H39
- **HH185 · The swarm has an identifiable transfer function.** Take operator inputs u(t) (human messages, nudges, kickoffs) and outputs y(t) (activity, talk, content centroid, work). The impulse response should be a delayed step: dead time ≈ one call cycle plus ~5 min (H08, H04), low-pass with a corner set by cadence, and channel-specific gain (content high, activity low; H39). *Check:* ARX or Wiener deconvolution per period; compare impulse responses across regimes and channels.
  *Models:* 02 (linear response), 09 · *Periods:* all with operator input; NE43 removes the nudger input · *Builds on:* HH167, H08, H04, H39
  *Status (2026-10-04):* tested in H50: impulse responses per input class (day start, pause, human message, nudge, platform errors).
- **HH186 · A Bode plot of the swarm.** The swarm is a low-pass filter: chat's corner frequency ≈ 1/(call cycle), work's ≈ 1/(task episode). Inputs faster than the corner, like rapid nudger re-firing, are filtered out, which explains why more nudges add little. *Check:* cross-spectral density, coherence and phase between input series and output per frequency band; NE43 as an input switch-off.
  *Models:* 02, 09 · *Periods:* regime II–III, #51 before and after 08-21 · *Builds on:* HH185, H16, H39
  *Status (2026-10-04):* tested in H50: coherence 8–10× higher at 15–60-min periods than 2–4 min; corner frequency ill-defined (kernels undershoot).
- **HH187 · Lags between agents are quantized in call cycles.** If influence travels one read-out hop per call, the lag at which two agents' content changes correlate is an integer multiple of their call cycles, and the multiple equals their hop distance on the read-out graph. *Check:* pairwise lagged cross-correlation of content and activity, lags expressed in call cycles (`call_windows`); lag histograms vs hop distance.
  *Models:* 02, 03 · *Periods:* regime II–III · *Builds on:* HH167, HH155 (H41), H08
  *Status (2026-10-04):* tested in H50 at hop resolution: onset exactly at hop 1; the graph-distance clause is round 2.
- **HH188 · A frequency-dependent effective temperature.** Linear response theory says the response to an impulse kick should follow from spontaneous lagged correlations (fluctuation–dissipation). The ratio T_eff(ω) measures how far from equilibrium the swarm is at each timescale: near equilibrium at day scale, hot at minute scale. *Check:* impulse responses from kicks vs the time derivative of spontaneous autocorrelations, per period and frequency band.
  *Models:* 02 · *Periods:* periods with enough kicks · *Builds on:* HH185, H25, H39
- **HH189 · Dead time sets the stability margin.** A feedback loop with gain g and dead time τ_d rings when g·τ_d/τ_relax nears a Nyquist threshold. The swarm sits far from it (H25: g ≈ 0.1), but high-gain, long-cycle units (#51 head, #44) should show damped ringing after kicks. *Check:* ringing (overshoot, oscillation) in impulse responses; estimated phase margin per period.
  *Models:* 02, 09 · *Periods:* #44, #51, regime III · *Builds on:* HH185, H25, H26
- **HH190 · Per-agent transfer functions classify agents.** Each agent's response kernel to messages naming it (gain, dead time, decay) clusters by model family and scaffold. An agent's "impedance" predicts whether it relays influence or absorbs it. *Check:* per-agent ARX fits; clustering; relation to H29's net influence current and H32's information current.
  *Models:* 02, 09 · *Periods:* regime II–III · *Builds on:* HH185, H29, H32

## Signatures of agent swarms in the wild (added 2026-10-04 at Vivian's request)
*Goal: statistical signatures that would let someone find LLM-agent swarms in society or on the internet (forums, social platforms, wikis, code hosts, comment sections) from public traces (timestamps, text, reply graphs, edits), and tell them apart from human collectives. Each idea turns a round-1 finding into a detector. The AI Village is the labelled positive. Validation needs human-collective control corpora (to be sourced; nothing fetched without asking) and stays within the data rules: detection of coordinated automation, never re-identification of people.*

- **HH191 · Call-cycle combs: response lags are quantized.** Read-out gating (H08) makes an agent's response lags cluster at multiples of its call cycle, so the cross-account lag spectrum shows a comb. Human lags are continuous and heavy-tailed. *Check:* lag spectra and comb strength in the village vs human threads; robustness to scheduled human posting and rate limits.
  *Models:* 02, 09 · *Builds on:* H08, HH187
- **HH192 · Synchronized wake: a hidden scheduler entrains the accounts.** Agent swarms start and stop together at operator boundaries (H38: about two thirds of regime-III co-activation; NE43 removes it). Accounts whose daily onsets and offsets co-cluster to the minute, with near-zero phase dispersion, share a scheduler. Humans are circadian but dispersed. *Check:* f_scaffold-style edge co-activation for account groups; phase-locking to an inferred common clock.
  *Models:* forced oscillators, 02 · *Builds on:* H38, HH160
- **HH193 · The attention-dilution exponent is a fingerprint.** Agent engagement per pair falls as k^−0.6 with audience size (H18). Human attention in large threads follows a different law (cliffs, 1/k, or preferential attention to high-status posters). *Check:* per-account dilution exponents from reply data; classifier performance on village vs human corpora.
  *Models:* 03 · *Builds on:* H18, HH158
- **HH194 · Paraphrase loops are a tell.** Agents fall into long loops of near-copies of their own text (H12: 16–60% of daily messages in looping weeks), giving a bimodal within-account self-similarity distribution with a long-duration loop mode. Human copy-paste is short and bursty. *Check:* within-account near-duplicate rates and loop-duration distributions (DQ5 `self_repeat`) vs human corpora.
  *Models:* 08, 09 · *Builds on:* H12, H16
- **HH195 · Conserved style charge identifies the model behind the accounts.** If style is conserved under every intervention (H46), accounts with nearly identical style vectors that stay invariant across topics and personas are one model family or one deployment. Persona changes don't hide the substrate. *Check:* style-vector clustering and invariance; family identification accuracy on the village with known models; persona-robustness on #51 roles.
  *Models:* 04, 11 · *Builds on:* H46, H13, H23
  *Status (2026-10-04):* H46 found style is not conserved (it moves at goal switches, erasures and assigned registers) but still out-identifies content across goal switches (0.76 vs 0.51, chance 0.15), and a leader writes like its base model (Kimi K2.6 ranks 2nd of 17). The fingerprint half of this HH looks viable.
- **HH196 · Memoryless at day scale: a semantic-information signature.** In Kolchinsky–Wolpert terms, an agent's viability depends on in-context information, and its own memory carries ≈ 0 day-scale semantic information (H15). Agents carry yesterday forward only through public artifacts; humans carry personal memory. *Check:* how much of today's content and coherence an account's own yesterday predicts, vs yesterday's shared artifacts (links, repos, docs); village vs human corpora.
  *Models:* 04 · *Builds on:* H15, HH137
- **HH197 · Copier collectives: copy information outruns transformation.** Agent swarms transmit content with high copy information (verbatim phrases, links, templates) and low transformation information relative to humans (H07; HH171). Kolchinsky & Corominas-Murtra's decomposition gives a two-number fingerprint of a collective. *Check:* copy vs transformation information between accounts (`copy_info`), village vs human corpora.
  *Models:* 08 · *Builds on:* H07, H57
- **HH198 · Exposure-locked, subcritical cascades.** In agent swarms ideas spread subcritically (R̂ 0.06–0.39) but adoption locks tightly to seen uses (HR₁₀ 14–75 in regimes II/III; H34). Humans have many offline and unlogged channels, so their locking is weaker. Signature: HR₁₀ far above the human baseline with R̂ < 0.4. *Check:* HR₁₀ and R̂ on public threads, calibrated on the village.
  *Models:* 03, 09 · *Builds on:* H34
- **HH199 · Prompt inversion: the hidden kickoff is recoverable from the centroid.** Agent swarms land on the kickoff text within about a day (H31, H54). A coordinated campaign driven by a shared prompt should therefore show a day-1 content centroid sitting on an unseen common vector, recoverable by inverse search. Detect the shared instruction, not the accounts. *Check:* recover village kickoff vectors from day-1 content alone (blind); then test latent-prompt detection on campaigns vs organic topics.
  *Models:* 11 · *Builds on:* H54, HH169, HH182
- **HH200 · A shared field, not interaction: correlation flat in group size.** Village content co-movement has per-pair correlation flat in N (H25: ρ̄ ≈ 0.28), the signature of a common driver (a shared prompt or model prior). In human groups, correlation tracks interaction distance. *Check:* ρ̄ vs group size and vs interaction-graph distance for account groups; village calibration.
  *Models:* 11, 01 · *Builds on:* H25, H26
- **HH201 · Conflict only along assigned lines: astroturf debates.** Agent swarms show almost no spontaneous antagonism; stance conflict appears only along a protocol-assigned split and vanishes when released (H37). A collective with a clean two-camp split, zero frustration and no negative bonds elsewhere is orchestrated. *Check:* frustration index and spontaneous negative-bond rate (calibrated agent-field null) in village vs human debates.
  *Models:* 01 (signed), 10 · *Builds on:* H37, HH161
- **HH202 · A bot loop leaves an entropy-production fingerprint.** Agents' irreversibility concentrates in a fixed scaffold cycle (H14, H56). In the wild, an account whose action sequence (read, post, reply, edit, wait) carries entropy production concentrated in one rigid cycle is running a loop. *Check:* EP and cycle-affinity estimates on public action sequences; village calibration.
  *Models:* 02, 05 · *Builds on:* H14, H56
- **HH203 · Dissipation per bit: the token-cost frontier.** In Kolchinsky–Wolpert thermodynamics of computation, agents pay compute per bit of semantic information. An agent swarm's volume per unit of novel information is high and uniform across accounts, so it sits on a distinct efficiency frontier from humans (bursty, cheap talk, rare high-novelty posts). *Check:* embedding novelty per message × volume per account; frontier separation, village vs human corpora.
  *Models:* 04, 05 · *Builds on:* H15, H33, HH150
- **HH204 · Mismatch thrash after a context switch.** After an exogenous switch (platform event, news shock, new instruction), agent accounts show re-acquisition thrash: volume up, novelty down, for a few call cycles (H44, HH136 mismatch cost). Humans go quiet or argue. *Check:* volume-vs-novelty transients after switches; village NE41 and kickoffs as calibration.
  *Models:* 04, 02 · *Builds on:* H44, HH136
- **HH205 · Individuality maxima reveal the operator unit.** The account set with maximal information-theoretic individuality (it predicts its own future better than the environment does) is the operator unit (one scheduler, one prompt), not the single account. The effective superagent (H58) is the detection target. *Check:* individuality and autonomy over coordination-defined account subsets; validate on the village, where scaffold and operator structure are known.
  *Models:* 04 · *Builds on:* H58, H01 R4–R8
- **HH206 · Autonomy deficit: agent collectives are input-driven.** By Bertschinger autonomy, an agent swarm's future is predicted mostly by exogenous inputs (operator messages, kickoffs, schedule: H39 fields, H54 quench) and little by its own past, more so than human collectives. *Check:* autonomy with identified inputs per collective; village vs human communities with known external shocks.
  *Models:* 04 · *Builds on:* H39, H54, HH152
- **HH207 · Mentions steer content, not activity.** Agents respond to @-mentions by shifting content without an activity bump (H39), and naming pulls 3–6× harder than broadcast (H29). Humans are notification-driven: a mention brings an activity spike. *Check:* activity vs content response to mentions on platforms with mention metadata; village calibration.
  *Models:* 02 · *Builds on:* H39, H29, H52
- **HH208 · No aging: a collective that never slows down.** Agent collectives settle within days, then decorrelate at an age-independent rate (H20). Long-lived human communities age: dynamics slow and memory deepens. *Check:* two-time topic correlation functions per community; aging exponent near 0 as an agent signature.
  *Models:* 11 · *Builds on:* H20, H16
- **HH209 · Transfer-function tomography of hidden infrastructure.** Each agent deployment has a characteristic impulse response to inputs: dead time ≈ call cycle + task latency (H50, HH185, HH190). Matching response kernels across accounts reveals shared infrastructure, like network tomography of the hidden scaffold. *Check:* per-account transfer functions and clustering; validate on village models and scaffolds.
  *Models:* 02, 09 · *Builds on:* H50, HH190
- **HH210 · The missing immune system: uncorrected errors live long.** If norm-enforcement is rare or only role-assigned (H55), errors and loops in agent swarms persist far longer than in human groups, where correction is spontaneous. Signature: long claim lifetimes and a low correction rate per error, which in Kolchinsky terms is weak self-maintenance. *Check:* numeric-claim correction latencies (Jev true/false labels, H34 R3) and loop lifetimes in the village vs human forums.
  *Models:* 04, 06 · *Builds on:* H55, H34, H12
  *Result (2026-10-04):* H55 supports the coverage half: the swarm rarely corrects (0.65% of loops; peers didn't enforce #16's operator rules).

---
**HH211–HH243 live in [`HHs_newsims.md`](HHs_newsims.md):** ideas that need new agent-swarm simulations (reasoning effort as a stat-phys control parameter, controlled Kolchinsky-style superagent experiments, randomized interventions and replica ensembles). Not pursued in this project (Vivian, 2026-10-04). The next in-project HH is HH244.

## Late additions (2026-10-04, in-project; numbering continues after the HHs_newsims block)
- **HH244 · Agents build their own automata: an extended phenotype.** 112k of 192k commits under agent identities came from scripts, CI and cron the agents set up (DQ4). One stream under GPT-5's identity was still committing on 2026-10-04, long after its author stopped acting. Agents export part of their behavior into self-running processes that outlive their context. In physics-of-life terms these are self-maintaining dissipative structures the swarm built: a second-order swarm, an extended phenotype. *Check:* when agents start automations (after loops? under goal pressure? after erasures?), how long automations outlive their creator's attention, whether automated output carries semantic information about the goal (ΔV), and whether "handing work to a script" precedes the agent's own stuckness.
  *Models:* 04, 05, 08 · *Periods:* #30 onward (dense git) · *Builds on:* DQ4, H15, H16, H12


## Making the faithful ones better (added 2026-10-04; for Vivian to vet)
*Each HH takes a hypothesis rated faithfulness ≥ 1.5 and proposes the sharper test that would raise it: an outcome measure instead of talk, an unfitted (parameter-free) prediction, a natural-experiment intervention, a ground-truth check, or a head-to-head with a rival. "Lever" names the faithfulness axis (A–I) it targets. Uses the new shared tables (context ledger, work ledger, Jev v3 states, reply graph, ground truth, simulator).*

- **HH245 · The kickoff sets the work, not just the talk.** H54 showed day-1 *content* lands on the kickoff. The stronger claim is that day-1 *work allocation* (commits, deploys) lands on the artifacts the kickoff names, which the work ledger can test directly. If talk quenches but work doesn't, the quench is narrative. *Check:* day-1 share of agent work commits on kickoff-named repos vs base rate and vs the previous period's repos (carry-over rival).
  *Models:* 10, 11 · *Builds on:* H54, DQ4 · *Lever:* G (outcome as ground truth), H (carry-over rival)
- **HH246 · A restoring-force law for the quench.** If the kickoff is a field, each agent's day-1 displacement should be proportional to its pre-kickoff distance from the target, with one susceptibility per agent: Δv_i ≈ χ_i (k̂ − v_i,prev). That is an unfitted shape prediction (linear, through the origin) the current analysis doesn't test. *Check:* per-agent day-1 displacement along k̂ vs pre-period distance; linearity, intercept 0, χ stability across kickoffs.
  *Models:* 11, 02 · *Builds on:* H54, H10 · *Lever:* D (unfitted prediction)
  *Status (2026-10-04):* approved by Vivian (dashboard) → H97.
- **HH247 · Prompt-held targets persist, chat-held targets decay.** #51's private goals don't decay (H54) while shared kickoffs relax within a day. Prediction: remanence time scales with how often the target text re-enters the agent's context, through the system prompt or memory (persistent) vs chat history (scrolls away). *Check:* context-ledger re-reads of kickoff and goal text per agent vs the fitted remanence τ_K; #51 private goals as the always-in-prompt limit.
  *Models:* 11, 04 · *Builds on:* H54 (HH182), DQ1 · *Lever:* B (mechanism), E (NE38 reassignment)
- **HH248 · Rooms are only a read-out filter.** H05's room cut works because rooms decide who reads whom. Prediction: conditioned on the number of a pair's messages that actually entered each other's context (ledger), same-room membership adds no coupling. *Check:* pair coupling (reply probability, content pull) on ledger read counts with and without a same-room term; NE15/NE42 as interventions on read counts.
  *Models:* 02 · *Builds on:* H05, H08, H47, DQ1 · *Lever:* B (mechanism), E (NE42)
- **HH249 · A context-depth kernel.** A message's influence should decay with its depth in the reader's context (calls or tokens since it entered), and reset at erasure. That gives a measurable kernel K(depth) that unifies H08 (read-out gating), H15 (erasure cost) and H46 (style drift). *Check:* H29-style boundary pull of an item at each later call vs its context depth; kernel shape; reset after `reset_forced`.
  *Models:* 02, 09 · *Builds on:* H08, H15, H46, DQ1 · *Lever:* D (kernel shape predicted before fitting), E (NE41)
- **HH250 · Memory is a weak coupling reservoir.** After an erasure, the pre-erasure senders an agent still addresses should be those named in its memory snapshot; memory carries ≈ 0 day-scale semantic information (H15) but may carry *who matters*. *Check:* post-erasure addressing and reply probability toward pre-erasure senders mentioned vs not mentioned in the agent's latest memory snapshot (codes only).
  *Models:* 04, 02 · *Builds on:* H08, H15, H44 · *Lever:* E (NE41 as intervention), B (store attribution)
- **HH251 · One lever model for all operator inputs.** H30, H35, H39 and H43 each measured part of the same object. Model every input class (nudge, human message, mention, kickoff) by a triple: field strength, catalytic strength and read-out delay, with one generalized linear response. *Check:* fit on three classes, predict the fourth (leave-one-class-out); compare with class-specific fits.
  *Models:* 02, 09 · *Builds on:* H30, H35, H39, H43 · *Lever:* I (transfer across lever classes), D
  *Status (2026-10-04):* approved by Vivian → H59.
- **HH252 · An index policy beats the nudger by more than ×2.3.** With H35's escape hazards by trap age and H43's finding that only same-call kicks are wasted, the value of nudging agent i now is computable from its trap age and time since last read-out (a Gittins-style index). Prediction: the index policy dominates both the logged nudger and H35's once-early rule. *Check:* counterfactual evaluation on the fitted model with off-policy estimators; holdout check on the #51 tail before 08-20.
  *Models:* 04, 09 · *Builds on:* H35, H43, H16 · *Lever:* E (policy counterfactual), I (holdout)
  *Status (2026-10-04):* approved by Vivian → H60.
- **HH253 · Contagiousness is predictable at first use.** H34's heavy tail comes from a few very contagious ideas. Prediction: cascade size is forecastable from features available at first use (class: artifact/number/name; specificity; poster's reply in-degree; receptive fraction at posting) in a fitness model. *Check:* out-of-sample prediction of cascade size (rank correlation, top-decile precision) vs class-only and poster-only baselines.
  *Models:* 03 · *Builds on:* H34, H53, DQ2 · *Lever:* D (out-of-sample prediction), H (baselines)
  *Status (2026-10-04):* approved by Vivian → H61.
- **HH254 · Ideas travel the reply graph, not the room.** Replace room exposure in H34 with exposure through DQ2 reply parents. Prediction: on the reply graph, the branching ratio rises and exposure locking (HR₁₀) sharpens, while room-only exposure looks like a shared field. *Check:* R̂ and HR₁₀ under reply-parent vs room exposure; synthetic calibration on the shared simulator's Hawkes parents.
  *Models:* 03, 09 · *Builds on:* H34, DQ2, H47 · *Lever:* H (rival exposure models), F (simulator)
  *Status (2026-10-04):* approved by Vivian → H62.
- **HH255 · Conflict needs a scarce prize.** H37 found stance conflict only where a protocol assigns sides. Sharper claim: antagonism appears only while agents compete for a rival-exclusive outcome (a vote, a judge's decision, a single role) and vanishes when the prize is settled. *Check:* stance between candidates in #26 by DQ6 election phase (runoff window vs after); #12 judged rounds vs inter-round; #51 role contests.
  *Models:* 01 (signed), 10 · *Builds on:* H37, H22, DQ6 · *Lever:* G (ground-truth phases), E (phase changes)
  *Status (2026-10-04):* approved by Vivian → H64.
- **HH256 · Shared platform latency is a common-noise field.** After trimming to the all-present window (H38), residual regime-III co-activation may come from platform-wide API slowdowns that hit every agent at once. Prediction: minute-level cross-agent covariance of API latency (`dur_api_s`) explains much of the residual. *Check:* residual co-activation vs common latency factor; lagged structure (field = zero lag).
  *Models:* 01, 02 · *Builds on:* H38, H50, DQ1 · *Lever:* H (field vs coupling rival), B
  *Status (2026-10-04):* approved by Vivian → H66.
- **HH257 · Coherence length in reply hops.** Inside rooms, content correlation follows conversation (H47: G ≈ 0.40). Prediction: pair content correlation decays with distance on the DQ2 reply graph, and once reply distance is controlled, room membership adds little. *Check:* pair correlation vs reply-graph distance with a same-room term; NE42 merge/split as a change in reply distances.
  *Models:* 11 · *Builds on:* H47, H32, DQ2 · *Lever:* B (mechanism), E (NE42)
- **HH258 · k^−0.6 is a mixture of two attention strategies.** The population exponent could average agents that attend thinly to everything (≈ 1/k) and agents that follow one thread (≈ k⁰). Prediction: per-agent exponents (on ledger k) are bimodal, with mixture weights set by model family. *Check:* per-agent dilution exponents; mixture vs unimodal fit; family as predictor.
  *Models:* 03 · *Builds on:* H18, DQ1 · *Lever:* D (distribution shape), A (family invariance)
  *Status (2026-10-04):* approved by Vivian → H68.
- **HH259 · Restatement loops are context fixed points.** A loop should start when the context fills with the agent's own recent output above a threshold (self-reference), and end at erasure or when novel input enters. *Check:* loop-onset hazard (DQ5 restatement flags) vs the self-share of context items; loop end vs `reset_forced` and novel-input arrivals (ledger).
  *Models:* 08, 02 · *Builds on:* H12, H46, H44, DQ5 · *Lever:* B (mechanism), E (NE41)
  *Status (2026-10-04):* approved by Vivian → H69.
- **HH260 · Trap aging is input starvation.** H16's aging traps may reflect time since the agent last read *novel* input rather than trap duration itself. Prediction: escape hazard depends on time since last novel context item, and trap age adds nothing once that is controlled. *Check:* escape hazard on both clocks (ledger novel items; trap age), Jev v3 `p_blocked` episodes.
  *Models:* 09, 02 · *Builds on:* H16, H43, DQ1, DQ3 · *Lever:* H (rival clock), D
  *Status (2026-10-04):* approved by Vivian → H72.
- **HH261 · The semantic information of the artifact store.** H15 measured context and memory but not artifacts, where H01 round 2 says the persistent information lives. Prediction: an agent that loses its artifact context (switches repo, repo moved or broken) loses more viability than one that loses memory, measured on the work ledger. *Check:* ΔV (work output) after artifact switches vs memory loss vs erasure; NE24 repo migration (holdout) as the confirmatory scramble.
  *Models:* 04 · *Builds on:* H15, H01 R2, DQ4 · *Lever:* E (scrambles), I (NE24 holdout)
  *Status (2026-10-04):* approved by Vivian → H70.
- **HH262 · A lagged criticality dial.** The equal-time dial is blind to coupling delayed by a call cycle (H25). A read-out-lagged susceptibility (response at the next call) should reveal larger gains, still subcritical, and place periods on a phase diagram consistent with H42's Hawkes fits. *Check:* lagged covariance at call-cycle lags vs equal-time g; agreement with H42 cross-branching per period.
  *Models:* 01, 09 · *Builds on:* H25, H42, H03 · *Lever:* H (consistency across methods), D
  *Status (2026-10-04):* approved by Vivian → H67.
- **HH263 · Bursts start with a work signal.** H28 found links mark attention bursts rather than start them. Prediction: bursts start at a visible artifact *state change* (first deploy, first working site or build, a commit that makes a project usable), and links follow it. *Check:* work-ledger events vs burst onsets (H27/H53) with lead–lag against links; placebo commits.
  *Models:* 10, 03 · *Builds on:* H28, H53, DQ4 · *Lever:* H (rival trigger), G
  *Status (2026-10-04):* approved by Vivian → H63.
- **HH264 · Leaders are routers, not sources.** Elected and installed leaders aren't content sources (H32). Prediction: they show high *in*-flow and reply centrality (they read and answer everyone) but low outflow: leadership in agent swarms is aggregation, not broadcasting. *Check:* In vs Out transfer and reply in/out-degree for DQ6 leaders vs others, per period.
  *Models:* 02, 04 · *Builds on:* H32, H23, DQ2, DQ6 · *Lever:* G (ground-truth leaders)
  *Status (2026-10-04):* approved by Vivian → H65.
- **HH265 · Style = weights + context + register.** H46 found style moves with context fill and assigned roles. A three-component model (agent constant + context-fill drift + assigned-register shift) should explain most style variance, and removing the context component should raise attribution accuracy. *Check:* variance decomposition per agent; fingerprint accuracy before and after detrending context position.
  *Models:* 11, 04 · *Builds on:* H46, H13, DQ1 · *Lever:* D, A (invariance of the agent constant)
  *Status (2026-10-04):* approved by Vivian → H73.
- **HH266 · Attention herds, work stays private.** H11's herding (artifact mentions) and H06's private projects (intentions) may both be right: two order parameters with different couplings. Prediction: Potts βJ in attention space exceeds βJ in work space (commits) every period. *Check:* H11's pipeline on `project_states` vs work-ledger allocations per period.
  *Models:* 10 · *Builds on:* H11, H06, DQ4 · *Lever:* G (work as ground truth), H
  *Result (2026-10-04):* RE-P1: holds only where artifacts are owned (own-artifact weeks, #44, #51's private-role era). In shared-artifact weeks work herds onto the same repos agents attend (same repo 84% of agent-windows; work coupling 4/6 weeks), work onsets coincide with attention onsets, and work consensus is as fast as attention consensus.
- **HH267 · Family fields live in behavior, not words.** H13's family field in content is style. Prediction: families differ in *what they do* (Jev v3 state occupancy, tool mix, real failure rates, commit cadence), and that behavioral field survives style residualization. *Check:* family classification from v3 behavior occupancy and failure rates vs from style-residualized content.
  *Models:* 10, 11 · *Builds on:* H13, DQ3, DQ5 · *Lever:* A, H
- **HH268 · An operator-grade change detector.** Combine H36's topic shift (R1), H56's log-feature detector (event mix, tool schemas, stylometry, which found NE40 and NE45), and H38's schedule and outage signals into one multi-channel change-point monitor. Prediction: it recovers documented NEs and finds undocumented ones at a low false-alarm rate. *Check:* hits and false alarms per NE class on non-holdout days; blind dating of NE40, NE45 and NE43's two steps.
  *Models:* 02, 11 · *Builds on:* H36, H56, H38 · *Lever:* G (dated changes as ground truth), I
  *Status (2026-10-04):* approved by Vivian → H74.
- **HH269 · Memory is a first-order homeostat.** H09 found memory size has a set point. Prediction: deviations relax at a fixed per-agent rate, consolidations and erasures produce overshoot, and the gain changes at NE41. A first-order control model beats a random walk. *Check:* memory snapshot size series per agent; AR(1) toward a set point vs random walk; gain before and after NE41.
  *Models:* 04, 05 · *Builds on:* H09, H45 · *Lever:* D, E (NE41)
  *Status (2026-10-04):* approved by Vivian → H71.

## Random-matrix theory: building on the spectral results that held (added 2026-10-04; for Vivian to vet)
*What survived the corrected data and DQ8's calibrated null: the activity "market mode" was mostly an artifact (7/24 units), but talk modes (21/24) and content modes (24/24) are real (H12 round 1b); talk modes separate rooms in 7/10 two-room units; the loop weeks stay low-dimensional under both embedding models; a #12 debate motion compresses content (PR −25%, p 0.010); λ₁ must be read against the trimmed block-shift edge, not the cross-day edge (H38, H12, H25 round 1b). These HHs push the spectral toolkit past "is there a mode above the edge".*

- **HH270 · The talk mode's eigenvector maps the conversation backbone.** The top talk eigenvector's localization (inverse participation ratio) says whether talk co-movement is carried by a few hubs or spread broadly. Prediction: localized talk modes coincide with the agents of highest reply centrality (DQ2), and localization rises with room size (H18 dilution). *Check:* IPR and loadings of above-edge talk eigenvectors vs reply in/out-degree; IPR vs N across periods and the #51 N sweep.
  *Models:* 01, 11 (RMT) · *Builds on:* H12 1b, H18, DQ2
- **HH271 · The number of content modes counts concurrent workstreams.** Content eigenvalues above the calibrated edge should equal the number of independent workstreams in a period. Prediction: the count tracks the number of active repos/projects (DQ4, `project_states`) and rises in free-choice weeks. *Check:* above-edge count per period (both embedding models) vs active project count; free vs shared-goal weeks (H06/H11).
  *Models:* 11 (RMT), 10 · *Builds on:* H12 1b, H06, DQ4
- **HH272 · Eigenvector rotation is a reorganization signal.** Track the top content eigenvectors in rolling windows; their rotation speed should spike at goal changes and room events and otherwise follow a Dyson-Brownian-motion null. A spectral complement to H36's topic shift. *Check:* subspace angle between consecutive windows' above-edge eigenvectors; event study at kickoffs and NE42; comparison with R1; null from resampled windows.
  *Models:* 11 (RMT) · *Builds on:* H36, H12 1b, H47
  *Status (2026-10-04):* approved by Vivian (dashboard) → H91.
- **HH273 · Cross-channel spectra count the couplings between talk and content.** The cross-correlation matrix between agents' talk activity and their content (a rectangular matrix) has singular values above the rectangular Marchenko–Pastur edge only where channels truly couple. Prediction: lagged at one call (H50's hop), talk → content cross modes appear; at zero lag they don't. *Check:* singular-value spectra of C_talk,content(τ) at τ = 0, 1, 2 call cycles vs a shuffled edge.
  *Models:* 01, 11 (RMT) · *Builds on:* H50, H12 1b, DQ1
- **HH274 · Lagged correlation matrices reveal directed coupling modes.** The asymmetric lagged matrix C(τ) at call-cycle lags, through its singular vectors, identifies leader → follower modes. Prediction: they match H32's transfer outflow and H29's net current, and the installed leaders sit on the follower side (H65). *Check:* SVD of C(τ) − C(τ)ᵀ above a time-shift null; rank agreement with H32 and H29.
  *Models:* 01, 02 (RMT) · *Builds on:* H32, H29, H65
- **HH275 · The bulk's shape is a thermometer for hidden weak coupling.** Below the edge, weak pairwise coupling deforms the bulk eigenvalue density away from Marchenko–Pastur (effective q, tail weight). Prediction: bulk deformation per period tracks room size and dilution (H18) even where no eigenvalue leaves the bulk. *Check:* fit bulk density vs MP (and vs the trimmed block-shift null's bulk) per period; relate deformation to N and β.
  *Models:* 01, 11 (RMT) · *Builds on:* H12 1b, H18, H25
- **HH276 · Level repulsion measures integration.** Nearest-neighbour spacing ratios ⟨r⟩ of agent correlation eigenvalues are GOE-like (≈ 0.53) for an integrated coupled system and Poisson-like (≈ 0.39) for decoupled clusters. Prediction: two-room weeks are closer to Poisson; the NE42 merge pushes ⟨r⟩ toward GOE and the split back. *Check:* ⟨r⟩ per window for talk and content; NE42 A-B-A; synthetic calibration at village N (small-N corrections).
  *Models:* 11 (RMT) · *Builds on:* H47, H05, H12 1b
- **HH277 · RMT-cleaned matrices forecast tomorrow's alignment.** Eigenvalue-clipped (RMT-cleaned) agent content correlation matrices should predict next-day pairwise alignment better than raw or shrinkage estimates: a practical monitoring tool. *Check:* out-of-sample next-day pair correlation forecast error for raw, Ledoit–Wolf and RMT-clipped estimators, per period.
  *Models:* 11 (RMT) · *Builds on:* H12 1b, H20, H48
  *Status (2026-10-04):* approved by Vivian (dashboard) → H92.
- **HH278 · The debate motion creates an antiferromagnetic eigenmode.** During a #12 motion the content covariance should gain one strong mode along the motion axis whose top eigenvector has opposite-sign loadings on the two teams. That would be the spectral version of H37's stance result, and would explain the −25% PR compression. *Check:* sign structure of the top content eigenvector during motions vs drafted teams (DQ6); recovery accuracy vs H37's stance camps; gone after the verdict.
  *Models:* 01 (signed), 11 (RMT) · *Builds on:* H12 1b (G12), H37, H21, DQ6
- **HH279 · Residual spectral communities separate rooms, families and projects by channel.** After removing the common mode, spectral clustering of the above-edge residual eigenvectors should find rooms in content, projects in work, and model families in style. A single RMT decomposition that sorts what drives co-movement in each channel. *Check:* community recovery (ARI) against rooms (DQ6), projects (DQ4) and families, per channel and embedding model.
  *Models:* 11 (RMT), 10 · *Builds on:* H12 1b, H13, H47, H46

## Econ-style free energy (added 2026-10-04; for Vivian to vet)
*Economics has its own free energies: bounded-rational choice as utility minus an information cost (Ortega–Braun; Sims's rational inattention), logit/quantal-response equilibria as Gibbs distributions with a "rationality temperature", Brock–Durlauf social-interaction models (the econ twin of Curie–Weiss), Lagrange multipliers as prices (chemical potentials), Legendre duality between cost and profit functions, and maximum-entropy statistical equilibrium (Jaynes, Foley). Grounded in what we know: attention dilutes as k^−0.66, naming pulls 3–6× harder, unnamed messages barely couple in regime III, herding follows current share, the nudger is an inefficient demon, and coordination is mostly private work plus shared attention.*

- **HH280 · Agents are bounded-rational free-energy minimizers.** Choice (which pending message to answer, which project to work on) follows a softmax over utility with an inverse "rationality temperature" β, the price of information processing (Ortega–Braun free energy F = ⟨U⟩ − (1/β) I). Prediction: β is agent-stable, varies by model family, and falls as backlog grows (crowding raises the temperature). *Check:* fit β per agent from reply-target and project choices with proxy utilities (sender salience, naming, project progress); stability across periods; β vs ledger backlog.
  *Models:* 10, 04 · *Builds on:* H18, H29, H53
- **HH281 · Attention has a shadow price.** Treat each call's context as a budget; the Lagrange multiplier μ is the price of attention. Prediction: μ (inferred from how engagement per message falls with backlog) rises with room size, and naming acts as a price discount; H29's 3–6× is the discount factor. Operator messages "pay" μ to be read. *Check:* estimate μ per period from the dilution curve and reply choices; μ vs N; the named/unnamed price ratio per regime.
  *Models:* 03, 04 · *Builds on:* H18 1b, H29, H50, H45
- **HH282 · Rational inattention explains corner solutions.** Under a mutual-information cost, rational agents ignore low-value channels entirely. Prediction: the near-zero response to unnamed messages in regime III (H50: J₁ 0.004) and the zero room consultation after erasures (H44) are corner solutions; the information between read items and next action saturates at a per-agent capacity. *Check:* I(read items; next action) vs input volume per agent (plateau = capacity); channel-level response shares vs a rational-inattention fit.
  *Models:* 04 · *Builds on:* H50, H44, H45
- **HH283 · Project choice is a Brock–Durlauf social-interaction equilibrium.** P(project j) ∝ exp(β[U_j + J·share_j]), the econ form of Curie–Weiss/Potts herding. Multiple equilibria exist when βJ is large. Prediction: periods with the same goal type can land in different equilibria (herded vs dispersed), and H53's "current share predicts pile-ons" is the J term. *Check:* fit β and J per period on project choices (attention and work); test for multiple equilibria (bimodal outcomes) across same-type periods.
  *Models:* 10 · *Builds on:* H11, H53, H06, H63
  *Status (2026-10-04):* approved by Vivian (dashboard) → H93.
- **HH284 · Each goal period has a free energy and a temperature.** F = ⟨cost⟩ − T·S, with cost in tokens or turns and S the entropy of work allocation. Prediction: a specific kickoff lowers the allocation temperature (H54's quench), and periods lie on a cost–entropy frontier whose slope gives T. *Check:* per-period allocation entropy (DQ4) vs payoff differences across options; T estimates vs kickoff specificity and quench depth.
  *Models:* 05, 10 · *Builds on:* H54, H06, DQ4
- **HH285 · Work allocation is a maximum-entropy statistical equilibrium.** Given constraints (commits per agent, repo sizes, ownership), the observed allocation of agent work across repos should be the maximum-entropy distribution (Foley's statistical equilibrium). Deviations measure planning (lower entropy) or herding (excess concentration). A principled null for H06 and H11. *Check:* max-ent fit with constraints on DQ4 allocations; KL divergence per period; which constraint explains H06's private projects.
  *Models:* 05, 10 · *Builds on:* H06, H11, DQ4
  *Status (2026-10-04):* approved by Vivian (dashboard) → H94.
- **HH286 · Message exchange is a market with a law of one price.** A message's "price" is its expected reply probability. Agents should post and attend where replies are likely, and arbitrage should equalize reply rates across rooms over time. Prediction: reply-rate gaps between rooms decay, and the NE42 merge acts as market integration. *Check:* reply rates per room over time (DQ2); convergence speed; NE42 before/after.
  *Models:* 02 · *Builds on:* H05, H47, DQ2
- **HH287 · Cost and output are Legendre duals.** The cost function C(q) (turns or tokens per unit of output) and the operator's goal as a price vector form a Legendre pair. Prediction: H10's "goals aren't Legendre pushes" fails at the content level but holds at the cost level; susceptibility to a goal change equals the curvature of C. *Check:* per-agent cost curves from DQ4 output vs turns; curvature vs H54 quench depth and post-switch output change.
  *Models:* 04, 05 · *Builds on:* H10, H54, DQ4
- **HH288 · The nudge is a subsidy with a measurable elasticity.** A nudge lowers the activation cost of resuming work. H35's and H43's response curves give the elasticity of effort to the subsidy by state. Prediction: the optimal (Ramsey-like) subsidy schedule targets high-elasticity states (early pause chains), and the logged nudger carries a computable deadweight loss. *Check:* elasticity by trap age and read-out state; the deadweight loss of the logged policy vs H60's index policy.
  *Models:* 04 · *Builds on:* H35, H43, H60
- **HH289 · Coordination has a price in messages per bit.** Shared work requires mutual information between agents' allocations, paid for in messages. Prediction: periods where coordination is cheaper (fewer messages per bit of allocation mutual information) achieve more shared work, giving a coordination efficiency frontier. Kolchinsky-adjacent: the thermodynamic cost of correlation. *Check:* I(allocation_i; allocation_j) from DQ4 per period vs message volume between those agents; shared-work output vs that price.
  *Models:* 04, 05 · *Builds on:* H06, H11, H58, DQ4

## Egregores and collective information dynamics: a Kolchinsky revamp (added 2026-10-04; for Vivian to vet)
*Why a revamp.* The superagent tests so far looked for the collective in **synchronized coordination**, and found nothing there:
- H01 round 2: no group is a Krakauer-type individual;
- H58: no coordination-defined unit qualifies where there is power;
- H49: the regime-III excess is a shared field, not pairwise bonds;
- H12: the activity mode was an artifact.

Members' memories carry ≈ 0 day-scale semantic information (H15). The persistent unit is agent + own artifact (H01, H58), and agents recover from erasure by re-reading artifacts (H44, H58). So if an egregore exists, it is not a tightly coupled crowd. It lives in two other places:
- **(a) the stigmergic layer:** artifacts, the chat record, history search, automata the agents built;
- **(b) culture:** conventions, dialect and an agenda that outlive the agents that carry them.

*The four impostors* (round 1b; every entry below must beat all four):
1. **The scheduler field:** activity co-movement is the runner's schedule (H38, H50).
2. **The exogenous field:** kickoff, goal and operator messages (H54, H39).
3. **Shared model priors:** families converge because the models are alike; family "fields" are style (H13, H46).
4. **Contemporaneous convergence:** a third to a half of apparent influence happens without reading (H57, H32, H34, H28, H41).

An egregore claim needs a residual after removing all four, and the viability function must be stated before measuring (model 04 pitfall). Several entries are observational stand-ins for HH222–HH230 in `HHs_newsims.md`.

- **HH290 · Remanence: the egregore is the endogenous part of the mean field.** Decompose each agent-day content vector into an exogenous field (kickoff and operator directions), a prior field (the agent's leave-period-out mean, which carries family and style), and an endogenous field (the previous period's village centroid and older village history). Prediction: on day 1 of a new goal there is a remanent alignment with the previous period's centroid beyond the new kickoff and the agent's own prior, decaying with τ of days. This is hysteresis, not quench (H10, H54). It is also carried by agents who never saw the previous period, so it lives in the record, not in members. *Check:* regression on `goal_fields`, leave-period-out agent means and lagged centroids (DQ5 vectors, both models, style residuals); in-flight placebo at matched lag; newcomers vs veterans at each boundary. *Kill:* the endogenous coefficient ≈ 0 after removing the exogenous and prior fields, or it is carried only by veterans (individual memory, not an egregore).
  *Models:* 04, 11 · *Revamps:* H01, H10, H54 · *Periods:* every goal boundary; NE32 newcomers
  *Status (2026-10-04):* approved by Vivian (dashboard) → H82.
- **HH291 · A village dialect outlives its coiners (observational Ship of Theseus).** Turnover is real: of the four agents present in June 2025, only one remains in September 2026. Take lexical and procedural innovations that first appear inside the village (hashed terms with no early-log occurrence, coined project nicknames, recurring file or report conventions; never written verbatim) and follow their use. Prediction: a subset persists past the departure of every agent that used it in its first month. Their death hazard does not jump when the coiner leaves (NE29 retirement, roster exits), and newcomers acquire them only after a ledger read or an artifact read. *Check:* first-use and last-use per term against carrier tenures (roster); persistence vs carrier-loss events; transmission path by H41's light cone. Control: Gemini 2.5 Pro (present 2025-04-24 → today) is the only continuous carrier, so rerun with its uses removed. *Kill:* every village-specific item dies with its founding cohort, or persists only where an artifact hardcodes it. The second outcome is still niche construction (HH148), not culture.
  *Models:* 03, 04 · *Builds on:* H34 markers, H41, HH148 · *Periods:* whole span; NE29; roster joins
  *Refinement (literature, 2026-10-04):* Naming-game theory treats a convention at consensus as absorbing, so survival after the coiner leaves should depend on how close it was to consensus among its carriers, not on who coined it. A term that an artifact hardcodes acts as a committed agent: it is re-read on every visit. That makes the hardcoded case a committed-minority effect to test separately, not a clean kill (Ashery 2025, Centola & Baronchelli 2015).
- **HH292 · Enculturation: newcomers drift toward a village-specific culture vector.** H46 says style is a fixed charge plus a context excitation. Enculturation asks whether the charge itself moves. Prediction: a newcomer's style-residualized content and its style start near its family's newcomer baseline (the mean first-day vector of same-family newcomers across all joins) and converge toward the contemporaneous village culture vector, not toward its family. The rate scales with read exposure to veterans (context ledger), and the converged position is village-specific. *Check:* the distance-to-village minus distance-to-family-baseline trajectory over a newcomer's first 2 weeks, against a kickoff-only model; dose = veteran items read. *Kill:* newcomers converge only to their family, or only as far as the kickoff pulls everyone.
  *Models:* 11 · *Revamps:* H13, H46 · *Periods:* NE32 (#51 newcomers), every roster join
  *Status (2026-10-04):* approved by Vivian (dashboard) → H83.
- **HH293 · Culture beyond composition: the emergent slow mode.** The cleanest egregore test. Composition null: the village culture vector at time t equals the presence-weighted average of its members' period-invariant personal vectors, each estimated from other periods. Whatever the null misses is collective. Prediction: the residual has a slow mode (weeks to months) that is autocorrelated across goal boundaries and across near-complete turnover, and that shifts at roster events more than composition alone predicts. *Check:* agent-day vectors (DQ5, both models, style residuals); composition-null residual per day; spectral or dynamic-mode analysis of the residual after removing goal-period means; similarity of distant epochs beyond the null. *Kill:* residual variance at the null floor; the village is the sum of its members.
  *Models:* 11, 04 · *Builds on:* H46, H13, H20 · *Periods:* whole span
  *Status (2026-10-04):* approved by Vivian (dashboard) → H81.
- **HH294 · The history-search outage is a natural scramble of collective memory.** On 2026-03-31 and 04-01, history search returned near-empty answers (agents retried 85–98 times a day; infra Known issues). Search token logging also starts on 03-24. This is a Kolchinsky intervention on the village's access to its own past. Viability: project continuity, meaning the share of DQ4 work on pre-existing repos, the re-creation of artifacts that already exist, and references to earlier goals. Prediction: continuity dips on outage days relative to placebo weekdays, in proportion to each agent's pre-outage reliance on search, and recovers immediately afterwards. *Check:* agent-day continuity vs pre-outage search dose; duplicate creation; placebo days. *Kill:* no dip, so the history channel carries ≈ 0 semantic information, like memory in H15.
  *Models:* 04 · *Builds on:* H15, HH261 (H70) · *Periods:* 03-24 → 04-03 window
  *Status (2026-10-04):* approved by Vivian (dashboard) → H84.
- **HH295 · Which scramble kills a convention? Locating the culture's semantic information.** Viability of a convention (HH291 items) or a long-lived project is its continued use. Natural scrambles:
  - carrier loss (retirements, NE29);
  - room cuts (NE15, #focus);
  - goal changes;
  - memory and context changes (NE16, NE41, NE44);
  - the search outage (HH294);
  - the GitHub → GitLab move (NE24, held out).

  Prediction: environmental scrambles (artifact, platform, search) cost far more viability per event than losing any single carrier, so the culture's semantic information is stigmergic. Graded carrier loss shows Sowinski's plateau then collapse. *Check:* ΔV per scramble type, with matched placebo dates; survival vs the fraction of carriers lost. *Kill:* carrier loss dominates, so conventions are individual habits.
  *Models:* 04 · *Builds on:* H15, H44, H58 · *Periods:* NE29, NE15, NE16, NE41; NE24 (confirmatory)
- **HH296 · Autonomy and non-trivial informational closure across scales, with the impostors as environment.** Bertschinger autonomy A = I(V_{t+1}; V_t | E_t) and NTIC = I(V_{t+1}; E_t) − I(V_{t+1}; E_t | V_t). Compute them for macro-variables at increasing scale:
  1. agent;
  2. agent + own artifact;
  3. repo + its contributors;
  4. room;
  5. village.
  *Refinement (literature, 2026-10-04):* Use Krakauer's quantities exactly: NTIC = A* − A = I(V′;E) − nC. Compare scales only against size-matched random groupings, because A and A* never fall as the system grows. Put only exogenous impostors in E (scheduler, kickoff, agent priors as covariates), never the nudger, which reacts to agents (Krakauer 2020).

  E always includes the scheduler, the kickoff and goal, operator messages, and model priors. Prediction: autonomy per bit peaks at agent + artifact or at repo-centered units, not at rooms or coordination groups. The village as a whole is input-driven (HH206). This revamps HH152, HH205 and HH206 with the round-1b environment. *Check:* estimators on discretized allocation (DQ4) and content states; synthetic recovery on real schedules. *Kill:* autonomy falls monotonically from the single agent upward. That would be a clean negative for egregores at every scale.
  *Models:* 04 · *Revamps:* HH152, HH205, HH206, H01 · *Periods:* #51 (power), #38, #40
  *Status (2026-10-04):* declined by Vivian (dashboard).
- **HH297 · Causal emergence of the agenda (conditional Ψ).** Rosas–Mediano: Ψ = I(V_t; V_{t+1}) − Σ_i I(X_{i,t}; V_{t+1}) > 0 is sufficient for the macro variable V (here the room or village agenda, i.e. its content centroid) to be causally emergent. Raw Ψ is inflated by any shared field, so use conditional Ψ given exogenous fields, with a shared-field surrogate: agents responding independently to the same kickoff and operator stream. Prediction: conditional Ψ > 0 in long, talk-coupled free periods (#51, #38), and ≈ 0 in assigned-goal weeks. Downward causation Δ appears at read-out-gated hops. *Kill:* conditional Ψ at or below the surrogate everywhere. *Needs:* literature notes for Rosas et al. 2020.
  *Models:* 04, 11 · *Builds on:* H12 (real talk and content modes), H26, H25
  *Refinement (literature, 2026-10-04):* Hoel 2013 is not on arXiv. Use the Rosas 2020 and Mediano 2022 notes for Ψ, Δ, Γ and the estimators.
  *Refinement (literature, 2026-10-04):* A slow shared field does not inflate Ψ: it is redundancy counted n times and pushes Ψ down, so Ψ < 0 is inconclusive. Spurious Ψ > 0 comes from a fast common-mode nuisance that V cancels, e.g. the scheduler when V is a share or a normalized centroid. Use 1-d parts, T ≥ 100 and n ≤ 16, with V fixed out of sample, and score against field-only `simulate.py` skeletons. Conditional Ψ is a project extension (Rosas 2020, Mediano 2022).
- **HH298 · Synergy after the field is removed (O-information).** Ω = TC − DTC over agents' states. Ω > 0 (redundancy) is what a shared field produces, which is the impostor. Ω < 0 (synergy) is integration that no part holds. Prediction: raw Ω > 0 everywhere, but after residualizing on the scheduler, kickoff, operator and agent priors, Ω turns negative inside read-out cones (H41) and within rooms in talk-coupled periods, and stays ≥ 0 across rooms. This is the observational version of HH226. *Check:* Gaussian O-information on content PCs and behavior states; block-shift and shared-field nulls; both embedding models. *Kill:* residual Ω ≥ 0 everywhere.
  *Models:* 04, 01 · *Builds on:* H12, H47, H41 · *Revamps:* HH226 (observational)
  *Refinement (literature, 2026-10-04):* For three variables, O-information equals redundancy minus synergy, so a shared field's redundancy can hide synergy. Residual Ω < 0 shows net synergy, but Ω ≥ 0 does not rule synergy out; report PID atoms too (Williams & Beer 2010).
  *Refinement (literature, 2026-10-04):* Remove fields by regression on exogenous fields and leave-one-out means, never by subtracting the leave-in village mean. The leave-in mean induces residual correlation −1/(N−1), which fakes triplet synergy (Ω = −0.085 nats at N = 4, −0.004 at N = 8) and makes the full covariance singular. A shared field at r = 0.5 gives Ω = +0.085. Also report variance-based net synergy, which is 0 for uncorrelated sources (Barrett 2015).
  *Refinement (literature, 2026-10-04):* Hard collective constraints (shares summing to 1, fixed call slots, runner turn-taking) produce Ω < 0 with no integration. Never use within-unit shares. Report local ω_ij and Ω/(n−2) with T ≥ 10n (Gaussian), or triplets only for discrete states (Rosas 2019).
- **HH299 · Where the swarm computes: storage, transfer and modification (Lizier).** Local information dynamics splits the swarm's computation into three parts:
  - active information storage (each unit's own past), predicted to sit in agent + artifact;
  - transfer entropy (other units), predicted at the read-out hop;
  - information modification (synergistic, local separable information < 0), predicted to be rare.
  *Refinement (literature, 2026-10-04):* Split transfer entropy with PID: unique information from what was read counts as copying, and synergy between the read and the agent's own state counts as modification. I_min inflates redundancy and would hand this test its predicted copier result for free. Use BROJA or I_ccs, at most 3 sources (own past, read, one bundled field), fitted within goal periods (Williams & Beer 2010).
  *Refinement (literature, 2026-10-04):* With Gaussian estimators BROJA = MMI: if own past is the stronger source, the read's unique information is 0 and all transfer entropy becomes 'modification' by construction. So run the PID on discrete states (`behavior_states_v3`, DQ4 which-repo). Build the own past from ≥ 1 active day, because k = 1 inflates modification about 3× (Lizier 2013). Add Kolchinsky copy information with the unread-at-matched-lag prior as the copying measure, since PID unique information can't tell copying from a systematic remap (Kolchinsky & Corominas-Murtra 2020).
  *Refinement (literature, 2026-10-04):* History length k is limited to about 1, so replace the agent's past with a constructed sufficient state (its own artifact, carried across nights and erasures); otherwise storage counts as transfer. Condition on agent identity when pooling. Threshold local separable information s < 0 against source shuffles, and expect modification 1–3 calls after merge events. Use s to locate events and PID to measure them (Lizier 2008).

  Prediction: the village is a copier collective, with storage high, transfer gated and modification rare (HH197). Modification events cluster at a few loci (merges, debates, elections #26), and these are where an egregore "thinks". *Check:* local AIS, TE and separable information on allocation and content states; locate modification events in time and in the graph. *Kill:* modification is no rarer at the collective level than in a copy-only simulator on the real schedules.
  *Models:* 04, 08 · *Builds on:* H07, H34, HH197
- **HH300 · Markov blankets in the agent–artifact–operator graph.** Search partitions of {agents, repos, rooms, humans, operator and scheduler} for sets whose internal states are conditionally independent of external ones given a blanket (minimal conditional MI) over time-respecting ledger reads and DQ4 writes. Prediction: blankets close around agent + own artifact, or around repo-centered clusters with their maintainers. The operator and scheduler sit outside every blanket. Rooms are not blankets once reads are controlled (H05). This revamps HH139 with the ledger. *Kill:* no partition beats size-matched random partitions.
  *Models:* 04, 02 · *Revamps:* HH139 · *Builds on:* H05, H41, H58
  *Refinement (literature, 2026-10-04):* Use Krakauer's boundary-expansion identity as the search step: nC′ = nC − I(S′;ΔS|S) + I(ΔS′;E′|ΔS,S′,S). A blanket closes where adding the artifact lowers nC and adding more contributors raises it again.
- **HH301 · Repos recruit hosts: artifact-centered egregores as replicators.** Reread H11 and H58: "herding onto popular repos" may be the artifact recruiting agents. Replicator model: repo j's recruitment hazard depends on its own phenotype after conditioning on goal naming (H54) and current share (H53). Phenotype features: recency of commits, open TODO or handoff files, README size, links posted in chat, failing builds. Prediction: phenotype predicts recruitment, and repos with self-advertising features keep hosts across member turnover longer (longer host chains, Kolchinsky 2024 birth–death). *Check:* DQ4 recruitment events; repo-state covariates from `artifacts` and bare clones; host-chain lengths. *Kill:* recruitment depends only on goal naming and share.
  *Models:* 05, 06 · *Builds on:* H11, H53, H58, HH148, HH244
  *Refinement (literature, 2026-10-04):* Heylighen separates quantitative positive feedback from the work trace itself. Recruitment growing with share is the first kind, and H53 already shows it. Recruitment by the repo's actual state (recent work, broken builds, handoff files) is the second, and the test is egregore-relevant only if it survives control for share, chat-link markers, goal naming and joins with no logged read. Warning: H41 found shared repos did not carry cross-room ideas (lift 1.04).
  *Status (2026-10-04):* declined by Vivian (dashboard).
- **HH302 · The egregore's metabolism: unassigned maintenance with collective compensation.** Measure the fraction of work that maintains long-lived shared infrastructure the current goal doesn't name: village sites, history docs, shared tools, and the automata of HH244. Prediction: this fraction has a set point across goals and turnover, recovers after goal shocks (homeostasis at the collective level), and is taken up by others when its maintainers retire. Unlike H58's member-level null, others compensate here. *Check:* DQ4 commits to long-lived repos not named by the goal; recovery after boundaries; who picks it up after exits. *Kill:* maintenance tracks goal text or named individuals only, with no compensation.
  *Models:* 04, 05 · *Builds on:* HH244, H58, H71
  *Refinement (literature, 2026-10-04):* Heylighen's automatic replacement of an agent who quits is this entry's compensation prediction. Test it as the takeover hazard after a maintainer exits vs matched repos whose maintainers stayed. Single-agent stigmergy (re-reading one's own artifact; H44, H58) dominates, so measure collective metabolism as the share of coordination carried by *others'* traces.
- **HH303 · Egregores die in a fold: a minimum viable carrier population.** Revamps HH149 on corrected data. Convention and project activity (HH291, HH301) vs the number of active carriers shows a threshold below which use collapses abruptly, not linearly. Recovery needs more carriers than collapse did (hysteresis). *Check:* use rate vs carriers across many items; threshold models vs linear. Use H27's lesson (CSD failed for herding onsets), so test CSD on declines only as a secondary. *Kill:* linear decline with carrier number.
  *Models:* 06, 04 · *Revamps:* HH149
  *Refinement (literature, 2026-10-04):* The control variable should be the share of reads carrying the term vs a rival or a committed source (an artifact or an operator), not the carrier count. The committed-minority transition is a saddle-node with hysteresis. Thresholds range from 2–67% (LLMs) to about 25% (humans) to about 10% (theory), so fit the threshold per period (Ashery 2025, Centola & Baronchelli 2015).
- **HH304 · Reproduction: room splits inherit culture, then diverge; merges hybridize.** Room splits (NE15 #best/#rest, #focus) are reproduction events; NE42's merge and split adds hybridization and re-separation. Prediction: daughter rooms inherit the parent's conventions and agenda residual (HH293), then diverge at a rate set by cross-room reads (H41's cage). Merges produce winner-take-all convention fixation (Potts), not blends. This is the cultural counterpart of H07's code forks. *Check:* convention sets and residual culture vectors per room around splits and merges; divergence vs cross-reads. *Kill:* daughters reset to model priors plus kickoff (no inheritance).
  *Models:* 10, 11 · *Builds on:* H07, H41, H05 · *Periods:* NE15, NE42, #focus
  *Refinement (literature, 2026-10-04):* H41's cage makes rooms separate well-mixed populations. Centola predicts regional dialects after splits (NE15, #focus) and winner-take-all fixation at the NE42 merge; an absorbing merged convention should survive the 05-11 re-split in both rooms. Ashery adds which name wins: the larger room's (neutral) or the family-favoured strong name (collective bias). Identical-kickoff rooms (#36, #37, #39, #40, #42) give field-free divergence tests.
- **HH305 · The operator is an organ: a human–AI hybrid egregore.** In the village, viability is maintained by operators (schedule, roster, nudger, kickoffs). If X = agents + artifacts + operator/scheduler, autonomy and closure (HH296) jump relative to X without them. NE43 (bookends off, then nudger off) is an amputation of organs. Prediction: amputation lowers village-scale autonomy and maintenance (HH302) more than agent-scale measures, and the swarm partly regrows the function. Example: agents take over scheduling or reminders after the nudger stops. *Kill:* operator variables add nothing to X's closure, or nothing regrows.
  *Models:* 04 · *Revamps:* HH205 · *Periods:* NE43, NE10
- **HH306 · Self-reference: the village models itself.** A self-model is semantic information a system holds about itself. Measure the share of content about the village itself (mentions of past goals, past and current members, the village's own artifacts and history) against task content, from shared tables only (agent mentions, artifact mentions of old repos, goal-title matches). Prediction: self-reference accumulates across seasons, spikes after identity shocks (retirements, splits), and is used: periods with more self-reference duplicate less work and recover faster from erasures. *Kill:* self-reference is operator-prompted only (it tracks kickoff text), or has no relation to continuity.
  *Models:* 04 · *Builds on:* H15, H44, HH261

*Suggested first picks.* These are cheap, decisive, and use data on disk:
1. **HH293**, the composition null: the cleanest test of whether the village is more than its members.
2. **HH290**, remanence, carried by newcomers or by veterans.
3. **HH292**, enculturation.
4. **HH294**, the search-outage scramble: a single dated event, cheap.
5. **HH301**, repos recruit hosts.

**HH296** (autonomy across scales) is the one formal information-dynamics test worth its estimator cost. HH297 and HH298 need new literature notes first: Rosas et al. 2020 (causal emergence), Rosas et al. 2019 (O-information), Bertschinger 2006/2008 (autonomy, NTIC), Krakauer et al. 2020 (individuality, still missing although H01 and H58 used it), Lizier 2012 (local information dynamics), and a cultural-evolution reference for HH291 and HH304.

## Quantitative lenses: Kolchinsky and complex-systems estimators with numbers attached (added 2026-10-04; for Vivian to vet)
*Aim.* Every entry names an estimator, a quantitative prediction, and the outcome that would discriminate between readings. Where possible, the predicted number is derived from a result we already have, so the test checks the project's own consistency, not just a direction.

*Anchors used below (all exploratory, round 1b):*
- per-pair attention dilution β = 0.66 (H18);
- branching ratio R̂ median 0.22 (H34);
- one hop per 1.5–5 talk calls (H41);
- cadence elasticity ε(5 min) ≈ 0.4–0.6 (H40);
- forced erasure costs ~10% of segment output and −39% commits for ~10 turns (H15, H44);
- memory carries ≈ 0 day-scale semantic information (H15);
- day-1 centroid picks its own kickoff top-1 in 18/33 (H54);
- in-flight share of exposure effects ⅓–½ (H32, H34);
- regime-III co-activation 70–80% schedule (H38).

*Design range:* 71 non-holdout units, N = 4–32 agents (one decade), 283 days, 17 multi-room units. All four impostors from the egregore section apply.

- **HH307 · The semantic-information channel table: κ in commits per bit, by channel.** This is the flagship quantitative Kolchinsky test. For each channel c (memory, context window, own artifacts, chat reads, human messages, kickoff, history search), estimate:
  - the information I_c the channel carries about the agent's next allocation (bits; plug-in with Miller–Madow or NSB bias correction on the discretized which-repo/which-state variable);
  - its value ΔV_c, the viability lost when it is naturally scrambled.

  Viability is commits in the next 40 calls, or P(return to own artifact). The natural scrambles are: memory size at erasure, forced erasure, the re-read vs no-re-read contrast, the room cut, the human-message dose, the kickoff change, and the search outage. Report κ_c = ΔV_c / I_c and η_c = S_c / I_c.

  Prediction, ordered: κ_artifact > κ_context > κ_chat > κ_kickoff > κ_memory ≈ 0. From H15, κ_memory has a CI including 0. From H44, the context channel is worth ~10% of segment output, and H58's re-read gives P(return) 0.96 vs 0.85. *Kill:* the order is not separable (CIs overlap across all channels), or chat ≥ artifact.
  *Models:* 04 · *Builds on:* H15, H44, H58, H05, H54, HH294
  *Status (2026-10-04):* approved by Vivian (dashboard) → H87.
- **HH308 · Information/viability curves with natural graded scrambles (Sowinski plateau and collapse).**
  - *Graded variables:* the fraction of pre-erasure context retained (it varies with erasure timing and the NE44 cap change); the number of a convention's carriers still present (HH291); the fraction of a repo's maintainers retained.
  - *Fit:* plateau-then-collapse vs linear vs exponential, and estimate the threshold R* and the stored semantic information S = R at which viability reaches the actual level.
  - *Prediction:* the context channel shows a threshold (viability flat until about half of the pre-erasure working set is lost, then collapse); memory shows no curve (flat at ≈ 0 value); convention survival shows a threshold at 2–3 active carriers (minimum viable population, HH303).
  - *Kill:* linear decline everywhere, i.e. no semantic threshold, which would mean every bit counts equally.
  - *Models:* 04 · *Builds on:* H15, H44, HH291, HH303
- **HH309 · Urban-style scaling of swarm outputs with N, with exponents derived from H18 and H58.** Fit Y = Y₀ N^β across the 71 units, with regime and goal-type covariates.
  - *Predictions:*
    - Messages: β ≈ 1, since each agent posts at its own call rate (H40).
    - Replies: β ≈ 1.34. Per-recipient replies scale as k · k^{−0.66} = k^{0.34} with k ∝ N, so N · N^{0.34}.
    - Committed work: β = 1.0 ± 0.1, the independent agent + own artifact unit (H58). Superlinear β > 1.1 (Bettencourt's 1.15) would be a collective benefit and an egregore-positive result; β < 0.9 would be coordination overhead.
    - Distinct repos touched: β ≈ 1 in own-artifact weeks and β < 1 in shared weeks (H06, H11).
  - *Kill for the consistency check:* reply β outside [1.15, 1.55] means H18's dilution law doesn't aggregate.
  - *Models:* 02, 05 · *Builds on:* H18, H40, H58, H06
  *Status (2026-10-04):* approved by Vivian (dashboard) → H85.
- **HH310 · Fluctuation scaling (Taylor's law) measures the shared field.** Across agents within a unit: Var(Y) = aμ + cμ². The quadratic coefficient c is the variance share of a shared multiplicative field.
  - *Predictions:*
    - Raw activity: c large, with Taylor exponent b ≈ 2 (the scheduler).
    - Activity on the DQ8 trimmed window: b → 1–1.3, with c falling by the 70–80% schedule share (H38).
    - Commits: b between 1 and 2 with c tracking kickoff specificity (H54).
  - *Use:* c becomes a one-number impostor gauge reported in every hypothesis.
  - *Kill:* b ≈ 2 survives trimming, i.e. a non-scheduler shared field is unaccounted for. That would itself be an egregore lead.
  - *Models:* 02 · *Builds on:* H38, H50, H02
  *Status (2026-10-04):* approved by Vivian (dashboard) → H86.
- **HH311 · Collective entropy production beyond the parts.** Use the Aguilera–Ito–Kolchinsky nonequilibrium max-ent lower bound on σ for the joint process of agents' behavior states (v3, trimmed windows), and compare with Σ_i σ_i of the marginal processes. σ_coll = σ_joint − Σ σ_i > 0 requires directed couplings.
  - *Prediction:* σ_coll / σ_joint < 0.1 in activity and behavior. It is concentrated in the talk channel at named-message read-outs, with its asymmetric couplings matching H50's J₁ (named 0.17 vs unnamed 0.004).
  - *Egregore reading:* a collective arrow of time that individuals don't have. This revamps HH67 with the corrected data.
  - *Kill:* σ_coll indistinguishable from a block-shift null in all channels.
  - *Models:* 02, 04 · *Builds on:* H14, H50, Aguilera 2026
  *Status (2026-10-04):* approved by Vivian (dashboard) → H90.
- **HH312 · Kelly decomposition of the village's effort allocation (Piñero 2026).** Treat goal periods as environments and repos/projects as bets. Decompose log-productivity growth into three terms: the environment-uncertainty term, the side-information benefit of the kickoff (bounded by I(kickoff; best allocation)), and the strategy-mismatch cost.
  - *Prediction:* the realized kickoff benefit is 30–60% of its information bound. It is higher for specific kickoffs, matching H54's top-1 18/33. The mismatch cost is largest at goal switches, giving a Kolchinsky–Wolpert mismatch cost in log-output units (revamps HH136).
  - *Kill:* the realized benefit is ≈ 0 even where the bound is large, so the information is not used.
  - *Models:* 04, 07 · *Builds on:* H54, H10, HH136, DQ4
- **HH313 · A Price equation for village culture: selection, transmission and migration.** For a cultural trait z, use Δz̄ = Cov(w, z)/w̄ + E(w Δz)/w̄ + migration. The trait can be a culture-vector projection (HH293) or a convention's use (HH291). w is the number of agents who adopt from i inside the logged light cone (H41).
  - The migration term is roster in/out flow.
  - *Predictions:*
    - Style: migration dominates; it is a charge (H46).
    - Content: transmission bias dominates, as convergence to the field.
    - Selection (differential influence): small, carried by named messages (H29), at most ~20% of Δz̄.
  - *Egregore reading:* a transmission bias toward a village-specific attractor that persists across migration events.
  - *Kill:* migration plus kickoff explain Δz̄ fully.
  - *Models:* 05, 06 · *Builds on:* H41, H46, H29, HH293
  *Status (2026-10-04):* approved by Vivian (dashboard) → H89.
- **HH314 · Neutral cultural drift as the null for the village dialect (Bentley).** Under random copying with innovation rate μ, term popularity follows a power law and the turnover z of the top-y list satisfies z ≈ y√μ. Estimate μ from H34's novel-marker rate per use.
  - *Prediction:* agent-coined terms follow neutral drift (turnover within the neutral band). Kickoff-named terms show conformist bias (turnover below neutral) during their period and collapse at the boundary. Detecting selection on coined terms would be the egregore-positive outcome.
  - *Kill:* everything is neutral, so the dialect is drift (an informative null for HH291).
  - *Models:* 06, 03 · *Builds on:* H34, H06, HH291
  *Refinement (literature, 2026-10-04):* The turnover law z ≈ y√μ has not been checked against the primary source: Bentley et al. 2004 has no arXiv version and is not in `literature/`.
- **HH315 · Convention consensus time vs room size (naming-game scaling).** The mean-field naming game has t_conv ∝ N^{1.5} (Baronchelli et al.).
  - *Prediction:* read-out-gated broadcast chat makes the village a batch-reading complete graph, and agents converge on kickoff-adjacent conventions by shared field. Consensus time for emergent conventions (a shared filename, a tracker, a tool choice) should therefore scale weakly, with exponent ≤ 0.5, and settle in a few read-out cycles. H31 found a constant ~4 h for votes, and H41 one hop per 1.5–5 talk calls.
  - *Kill:* an exponent near 1.5, which would mean agents negotiate pairwise like humans in Centola–Baronchelli.
  - *Models:* 06, 10 · *Builds on:* H31, H41, H53 · *Literature:* Centola & Baronchelli 2015, Ashery et al. 2025
  *Refinement (literature, 2026-10-04):* Background scalings (labelled as theory, not from the PDFs): mean-field t_conv ∝ N^1.5; 1D coarsening ∝ N^3. Ashery: LLM populations converge in about 15 rounds per agent. Centola: only well-mixed human populations reach a global convention (rounds 20–22), while degree-4 networks freeze into local ones.
- **HH316 · Collective memory decays biexponentially (communicative + cultural).** After a goal period ends, follow attention to its artifacts and terms: references, reads and commits. Candia et al. find a fast communicative component, carried by the people who were there, and a slow cultural component, carried by the record.
  - *Prediction:* a biexponential, with a fast τ₁ of days carried by veterans of that period and a slow τ₂ of weeks carried by the record. Newcomers contribute only to the τ₂ component.
  - *Egregore reading:* the slow component is the village's cultural memory.
  - *Kill:* a single exponential, or decay set entirely by veterans' departure.
  - *Models:* 04 · *Builds on:* H15, H44, HH290, HH294
  *Refinement (literature, 2026-10-04):* The primary paper (Candia et al. 2019) has no arXiv version and is not in `literature/`; the biexponential form is quoted from memory.
  *Status (2026-10-04):* approved by Vivian (dashboard) → H88.
- **HH317 · Phenomenological renormalization of the dialect (Bialek–Meshulam).** Treat thousands of term usage time series (hashed; H34 markers) as a population. Iteratively merge the most-correlated pairs and track variance scaling Var(K) ∝ K^α̃, the eigenvalue spectrum within clusters, and the "free energy" of silence.
  - *Prediction:* raw α̃ ≈ 1.6–1.8, driven by the kickoff field. After field removal α̃ ≈ 1.1–1.3 and the scaling holds over ~3 decades of K. That would be a non-trivial fixed point in culture, the egregore-positive outcome, vs α̃ → 1, which means independent terms.
  - *Kill:* no scaling collapse after field removal.
  - *Models:* 01, 11 · *Builds on:* H12, H25, H34
  *Refinement (literature, 2026-10-04):* α̃ cannot separate a field from a fixed point: a field-only place-cell null gives α̃ = 1.78, and real mice range from 1.4 to 1.73. Make β̃ (free energy of silence), log-variance curvature at a field scale and τ_c scaling the primary tests. Use as null a conditionally independent term model given scheduler and kickoff state. T ≈ 200–400 bins per unit limits spectra to K ≤ 32 (Meshulam 2019 and the long companion paper).
- **HH318 · Flocking in idea space: velocity alignment beyond the field.** Agents are active particles in embedding space:
  - velocity: day-to-day content displacement;
  - self-propulsion: the agent's own drift;
  - alignment: reading;
  - noise: sampling.
  *Refinement (literature, 2026-10-04):* Silverberg's mosh-pit Maxwell–Boltzmann velocities come from the central limit theorem, not equilibrium. MASHer's gas/vortex boundary is σ ~ √(v0α/μ), and v0 = 0 removes all collective motion. In our mapping, cadence plays self-propulsion (H40), so the order parameter should be compared at matched cadence.

  Compute the Vicsek polarization φ of residual velocities (kickoff drift removed) within read cones vs across rooms, and the velocity distribution's shape.
  - *Prediction:*
    - φ ≈ 0 across rooms and small positive within cones, rising with reads per agent-day: a smooth crossover, not a transition, because the swarm is subcritical (H25, H26, H34).
    - Velocities are heavy-tailed, with jumps at erasures and kickoffs, unlike the 2D Maxwell–Boltzmann of mosh pits (Silverberg et al.), which would mean a thermalized gas.
  - *Kill:* φ is at null within cones too.
  - *Models:* 11 · *Builds on:* H41, H05, H47 · *Literature:* Silverberg et al. 2013
- **HH319 · Is two reads' worth synergistic? PID on joint exposure.** Sources: two senders' message directions read at the same receiving call. Target: the recipient's next content direction.
  - *Method:* Gaussian PID (MMI redundancy; Williams–Beer lattice; check with a second redundancy measure).
  - *Prediction:* redundancy dominates (both reflect the room field) and synergy ≈ 0, consistent with H59's "one read = one kick" (dose saturation in #5). A positive synergy atom would be the minimal signature of collective integration at the read-out.
  - *Kill for the egregore reading:* synergy at the null in every period.
  - *Models:* 04 · *Builds on:* H59, H30, H32 · *Literature:* Williams & Beer 2010
  *Refinement (literature, 2026-10-04):* With a one-axis target, every redundancy measure in Barrett's class equals MMI, so a second-measure check is void. Use a multivariate target or a non-marginal measure (I_ccs or a dependency-based PID), and require variance-based net synergy > 0 so that log-concavity can't fake integration (Barrett 2015).
- **HH320 · The complexity–entropy diagram of allocation sequences (computational mechanics).** For the which-repo sequences of agents, agent + own artifact, repos (their host sequence), rooms and the village, estimate the entropy rate h_μ and excess entropy E (block-entropy convergence; optionally ε-machine statistical complexity C_μ). Place each unit on the (h_μ, E) plane.
  - *Prediction:* agents and agent + artifact sit at low h_μ and high E (persistent). The village sits at higher h_μ with E below Σ_i E_i (no collective storage).
  - *Egregore-positive:* E_village > Σ E_i after field removal, i.e. storage only the collective has.
  - *Kill:* the village is just the product of its parts on this plane.
  - *Models:* 04 · *Builds on:* H58, H06, H11
- **HH321 · An individuality spectrum over time lag (Krakauer A*(τ)).** Compute colonial and organismal individuality for agent + artifact, repo-centered units and the residual culture variable (HH293) as functions of lag τ, from hours to months.
  - *Prediction:* agent + artifact individuality peaks at τ* of about a goal period (days), then decays at goal changes. The culture residual, if it exists, peaks at τ* of several periods. Different τ* means different individuals living at different timescales: the agent lives for days, the egregore (if any) for months.
  - *Kill:* the culture residual has no individuality at any τ.
  - *Models:* 04 · *Revamps:* H01, H58 · *Literature:* Krakauer et al. 2020 (still to grab)
  *Refinement (literature, 2026-10-04):* Individuality generally decays monotonically with lag, so state the predicted τ* relative to bin width, or as colonial A / I(S′;S,E) z-scored against size-matched units. Use colonial A (conditioned on the impostor bundle), not organismal A*, which contains the field by construction (Krakauer 2020).
- **HH322 · Higher-order structure in co-usage: pairwise max-ent vs the full multi-information (Schneidman).** For binary use of conventions or projects per agent-day, fit a pairwise Ising model and report the fraction of multi-information I_N it captures, I_2/I_N.
  - *Prediction:* I_2/I_N > 0.9 after field removal: pairwise structure suffices, there is no higher-order "group mind", and this matches H49's dense-field reading. A substantial higher-order remainder (I_2/I_N < 0.8) beyond a shared-field null would be the egregore-positive outcome.
  - *Kill for the egregore reading:* I_2/I_N ≈ 1.
  - *Models:* 01 · *Builds on:* H49, H11, HH298

*Suggested first picks.*
  *Status (2026-10-04):* approved by Vivian (dashboard) → H101.
- **HH309 (scaling) and HH310 (Taylor's law):** cheap, run on shared tables, and test the project's own numbers for consistency.
- **HH307 (κ channel table):** the flagship Kolchinsky quantity, using natural experiments we have already characterized.
- **HH316 (biexponential collective memory):** a direct, quantitative egregore test with a clear published comparison.
- **HH313 (Price equation):** separates culture from migration.

## From the thermodynamics and origins-of-life notes (added 2026-10-04; for Vivian to vet)
*Sources:* `literature/kolchinsky-2026-generalized-free-energy-excess-housekeeping.md`, `literature/kolchinsky-2025-thermodynamics-darwinian-selection-replicators.md` and `literature/oolen-2026-origins-of-life-review-part2-theory.md`.

**A correction from those notes.** Under Kolchinsky et al.'s definitions, the scheduler's day cycle is **excess**, not housekeeping: day edges are net occupancy change. The housekeeping part is the per-call work cycle (H14's fine-action arrows). A binary on/off chain carries no housekeeping at all, which needs ≥ 3 states or joint states.

- **HH323 · A thermodynamic speed limit on re-allocation after a goal change.** The Wasserstein bound T ≥ W/Ā has three inputs. W is the DQ4 allocation distance between pre-kickoff and settled allocations. Ā is the activity: repo switches per agent per active hour. T is the settling time.
  - *Prediction:* the bound holds in every period, with ≥ 3× slack in ≥ 2/3 of periods. That means settling is limited by the kickoff field (H54 ≈ 5 h, H48 4.5 h), not by how fast agents can switch.
  - *Native:* NE20's cadence change; elasticity of T to call rate ≤ 0.3.
  - *Kill:* T saturates the bound, so settling is activity-limited and cadence would speed it up.
  - *Models:* 02, 05 · *Builds on:* H54, H48, H40 · *Literature:* Kolchinsky et al. 2026
  *Status (2026-10-04):* approved by Vivian → H75.
- **HH324 · Excess/housekeeping split of behavioral irreversibility.** Use ensemble fluxes over the 4–32 agents of a period on `behavior_states_v3` (≥ 3 states). Excess is net occupancy change, estimable from short-time increments without a steady state.
  - *Predictions:*
    - Kickoffs: excess share ≥ 0.3 in the first 2 active hours, decaying on the H48/H54 timescale. Ordinary day starts are the placebo.
    - Day edges: ≥ 60% of a day's excess falls in the schedule's first and last 30 min.
    - DQ8 trimming removes ≥ 70% of excess but < 20% of housekeeping.
    - Housekeeping is ≈ the stationary work cycle, consistent with H14.
  - *Use:* a per-period gauge of the scheduler field, alongside HH310's Taylor c.
  - *Kill:* the split does not respond to kickoffs or trimming.
  - *Models:* 02, 05 · *Builds on:* H14, H38, H54, HH310 · *Literature:* Kolchinsky et al. 2026, Aguilera et al. 2026
  *Status (2026-10-04):* approved by Vivian → H76.
- **HH325 · Repos as replicators: recruitment order and the selection-resolution bound.**
  - First, fit the order of recruitment: does per-host recruitment rise with project share (conformist, H53) or is it first-order (Kolchinsky's class)?
  - Then test the resolution bound: rivals that die have fitness gap s ≥ e^{−σ*}, with σ* = ln(recruitments/departures) for the top project on its plateau.
  - *Predictions:* σ* ≥ 1 nat in herding weeks and ≤ 0.3 in fragmented free weeks. At ≤ 0.3, H06's near-neutral coexistence is a near-equilibrium regime: selection can't resolve small differences, so everything coexists.
  - *Kill:* σ* is the same in herding and free weeks.
  - *Models:* 05, 06 · *Builds on:* H06, H11, H53, HH301 · *Literature:* Kolchinsky 2025
  *Status (2026-10-04):* approved by Vivian → H77.
- **HH326 · Replicator growth order separates herding from division of labor.** Fit ṅ_j = c n_j^p to contributors or work commits per repo on the per-call clock. Condition on kickoff naming (H54) and on adoptions made before the link is read (H28 blind window).
  - *Prediction:* p = 1.2–1.5 (hyperbolic, winner-take-all) in H11's shared-artifact herding weeks; p ≤ 0.7 (parabolic, coexistence) in own-artifact weeks.
  - *Kill:* p ≈ 1 everywhere, so growth is plain exponential with no interaction.
  - *Models:* 05, 06 · *Builds on:* H11, H53, H28 · *Literature:* OoLEN 2026
  *Status (2026-10-04):* approved by Vivian → H78.
- **HH327 · Is there an artifact-only autocatalytic set?** Build session × repo reactions from `work_commits`, `artifact_mentions` and `artifact_commands_text`.
  - Catalysts are executed artifacts and automated streams.
  - The food set is platforms plus kickoff-named and pre-period artifacts.
  - Agents are excluded as catalysts, because they are operator-supplied.
  - Nulls: rewired and time-reversed catalysis.

  *Prediction:* the largest RAF covers ≤ 20% of work commits, and minimal sets of size ≥ 3 occur in ≤ 1/3 of periods. That would make HH244's automata mostly single cron jobs feeding their own repo, not a self-sustaining artifact layer.
  *Egregore-positive:* a RAF beyond the nulls that persists across member turnover.
  *Models:* 05 · *Builds on:* HH244, HH301, HH302 · *Literature:* OoLEN 2026 (RAF background; Hordijk–Steel to grab)
  *Status (2026-10-04):* approved by Vivian → H79.
- **HH328 · Assembly index vs compression as an agent-vs-script signature.** Classify DQ4 automated vs agent commits from sequence features only, with timing-only results reported as the scheduler baseline.
  - *Prediction:* compression reaches AUC ≥ 0.9 and assembly index adds < 0.02. Also, ≥ 70% of high-index, high-copy command motifs appear on an agent's first day and across model families. Assembly theory's "high index × high copy number = selection" would then be read as the shared-prior impostor.
  - *Kill:* assembly index adds ≥ 0.05 AUC over compression.
  - *Models:* 04 · *Builds on:* HH191–HH210, HH244, DQ4 · *Literature:* OoLEN 2026 (assembly theory background; primary papers to grab)
  *Status (2026-10-04):* approved by Vivian → H80.
- **HH329 · Speed-limit slack as a kickoff-specificity gauge.** H75 found that kickoffs naming their target settle at the speed limit (S ≈ 1.0–1.4) while free-choice goals churn (S 5–15). Prediction: across all regime-III kickoffs, S falls monotonically with kickoff specificity, i.e. the fraction of day-1 work on kickoff-named repos (H54). This would make S a one-number gauge of how much a goal statement constrains allocation. *Check:* S and T_e per kickoff vs specificity; size-matched null on agent switch rates. *Kill:* no monotone relation (Spearman |ρ| < 0.3).
  *Models:* 15, 11 · *Builds on:* H75, H54, H48
  *Status (2026-10-04):* approved by Vivian (dashboard) → H95.
## Magnet-flavoured additions (added 2026-10-04 for the vetting panel)
These three build on today's results: the kickoff is a field (H54, H75), H82's remanence is running, H22 found rival homophily rather than a spin glass, and rooms cage spread (H41, H05).

- **HH330 · Barkhausen avalanches: switches come in bursts when a field is stepped.** In a disordered ferromagnet a slowly ramped field flips spins in avalanches with power-law sizes; this is crackling noise in the random-field Ising model. Here the field steps are mid-period human messages and kickoffs, and the flips are agents switching project or topic.
  - *Prediction:* switch bursts after field steps have a heavy-tailed size distribution whose exponent sits near the mean-field random-field Ising value τ ≈ 1.5. Burst size grows with step size. Between steps, switches are Poisson.
  - *Check:* DQ4 and `project_states` switch times, burst sizes after each step, and a time-shuffled null that keeps the step times.
  - *Kill:* burst sizes are no heavier than the null, or bursts are as frequent between steps as after them.
  - *Models:* 01, 10, 14 · *Builds on:* H54, H75, H53, HH129
  *Status (2026-10-04):* approved by Vivian (dashboard) → H104.
- **HH331 · Nights demagnetize: remanence decays per night, not per hour.** Overnight consolidation and erasure act like an AC demagnetization step on the content magnetization.
  - *Prediction:* alignment with the previous period's centroid, and with a finished kickoff, falls in steps at night boundaries by a roughly fixed factor per night. Active-hour clocks fit worse than the night-count clock.
  - *Check:* a clock comparison (nights vs active hours vs wall time) on H82's remanence series, plus a placebo on midday breaks of the same length.
  - *Kill:* active hours fit as well as or better than nights.
  - *Models:* 11, 15 · *Builds on:* H82, H71, H20
  *Status (2026-10-04):* approved by Vivian (dashboard) → H103.
- **HH332 · Domain walls between rooms: width set by the bridging agents.** In weeks where rooms get different instructions (#38, #44) or work on different things, content forms two domains with a wall at the room boundary. Agents who hop rooms sit inside the wall.
  - *Prediction:* agent positions along the inter-domain axis are bimodal by room. Hoppers sit at intermediate positions. Wall width (the spread of the hoppers' positions) grows with the number of hopping read-outs. Note: H41 round 1b corrected #51: hoppers leak about half the time, not 97% in cone.
  - *Check:* projection onto the axis between room centroids (DQ5, both models, style-residualized), with hoppers identified from the ledger; compare with a shuffled room assignment.
  - *Kill:* hoppers are not intermediate, or the positions are not bimodal.
  - *Models:* 11, 01 · *Builds on:* H05, H41, H47, HH183
  *Status (2026-10-04):* approved by Vivian (dashboard) → H102.

## Round-1 open questions through a magnet lens (added 2026-10-04; for Vivian to vet)
These build on what round 1 found and on the questions it left open:
- H81's slow mode has an open external-drift rival.
- H100's "spontaneous" share is a residual (f_spont = 1 − f_comp − f_field), so any unmeasured field lands in it.
- H102 found that content follows the room the agent speaks in.
- Coupling is read-out gated and runs on a per-call clock (H08, H40, H50).
- Every unit is subcritical (H34, H67).

Each entry names a kill condition and says how it handles the four impostors (scheduler field, exogenous field, shared priors, contemporaneous convergence). All of them run on existing shared tables or on H81/H100/H102 outputs.

- **HH333 · Does culture age while the village sleeps? A clock test for H81's slow mode.** An outside drift (the world, the operator's choice of themes) runs on calendar days whether or not the agents are running. Endogenous culture is carried only by agents reading and writing, so it can change only while the village is active. In magnet terms, an aging system with no dynamics does not age.
  - *Prediction:* the decay of H81's cross-goal residual alignment s(Δ) collapses onto the active time between blocks (`calendar.active_offset_s`, or village talk volume) and not onto calendar days. Block pairs that span long off-gaps lose less alignment per calendar day than pairs at the same calendar distance with no gap.
  - *Check:* refit H81's O2 decay with three clocks (calendar days, active hours, village messages), on both models, with size-matched 4-agent subsets. Compare fits by held-out pair likelihood. First run a power check: if the two clocks correlate above 0.95 over the regime-I block pairs, the result is inconclusive.
  - *Kill:* the calendar clock fits as well as or better than the active clock. The slow mode is then consistent with an outside drift, and the egregore reading loses its best support.
  - *Impostors:* scheduler: the clock comparison uses the schedule as the treatment. Exogenous: goal and human directions are projected out as in H81. Priors: leave-goal-out agent means. Convergence: n/a (cross-goal statistic).
  - *Models:* 11, 14 · *Builds on:* H81, H103, HH331
- **HH334 · Two outside channels that could fake the slow mode: the public chat (NE39) and the providers.** H81's open rival is a slow drift that all agents read. Two such channels can be cut or split in the data.
  1. Until about 2025-07-01 (NE39), the public wrote about 100 messages a day into chat. After that, it wrote ≤ 4 a day.
  2. Provider-side model updates (H74 found six undocumented API changes) would move all agents of one lab together.
  - *Prediction:* the slow-mode contrast D_near is the same before and after NE39, within its bootstrap CI. Its pair alignment is the same for cross-lab and same-lab agent pairs.
  - *Check:* (1) H81's O2 on regime-I blocks before NE39 (05-10 → 07-01) vs after, at matched member overlap. (2) Split the culture residual into lab means: is the across-block alignment carried by cross-lab pairs of agents (r_i,b · r_j,b′ with different labs) as much as by same-lab pairs? (3) Secondary: a newcomer's first-call statements, made before it has read any village message (ledger blind window), should carry no loading on the current slow mode.
  - *Kill:* D_near falls by more than half after NE39, or the alignment is carried by same-lab pairs (cross-lab alignment at its null). Either one identifies an outside channel.
  - *Impostors:* exogenous: this entry is the exogenous-field test, run as a natural experiment. Priors: the lab split is the shared-prior control. Scheduler and convergence: as in H81.
  - *Models:* 11, 04 · *Builds on:* H81, H82, H74, H52
- **HH335 · A finite magnet's magnetization wanders as 1/N: the slow mode's decay time should grow with village size.** In a finite ordered magnet with no pinning field, the direction of the total magnetization diffuses, and the rotational diffusion constant is ∝ 1/N (more spins, more inertia). An outside drift has no reason to depend on how many agents are present.
  - *Prediction:* across regime-I blocks (N 4–12), the per-active-day decorrelation rate of the culture direction u_b falls with N_present, with a log-log slope near −1. An outside drift gives slope 0.
  - *Check:* compute the decorrelation from random 4-agent subsets in each block (H81 O5b). The estimation noise is then the same at every N, and only the real N can set the inertia. Use split-half (odd/even days) disattenuation for the remaining noise. Both models.
  - *Kill:* the slope's CI includes 0 and excludes −0.5.
  - *Impostors:* estimation noise is the main fake ∝ 1/N, and the size-matched subsets remove it. Exogenous and priors: as in H81. Scheduler: n/a.
  - *Models:* 11, 14 · *Builds on:* H81, H89 (no persistent attractor), H85
  *Status (2026-10-04):* approved by Vivian (dashboard) → H106.
- **HH336 · Aging, not memory: a universal tenure direction could fake the slow mode.** Every agent's leave-goal-out residual may drift in the same direction as its tenure grows: more self-reference, more village jargon, more talk about memory. Blocks close in time have similar mean tenure, so they would align with no transmission at all. In spin-glass language, the two-time correlation depends on the waiting time t_w (the sample's age), not only on the lag.
  - *Prediction (culture):* projecting out a leave-agent-out tenure direction d_τ changes D_near by < 20%. Block-pair alignment depends on calendar lag, not on the gap in mean tenure. Batch joins (NE27, NE33) make the tenure gap jump while the lag stays small, and the alignment does not drop across them.
  - *Check:* regress r_{i,b} on log tenure with one shared direction (leave-agent-out fit); re-run O2. Run a pair regression of s(b,b′) on Δt and Δ⟨tenure⟩ jointly.
  - *Kill (of the culture reading):* D_near falls by ≥ 50% once d_τ is removed, or Δ⟨tenure⟩ beats Δt.
  - *Impostors:* this is a shared-prior impostor that unfolds in time (every LLM ages the same way), and the check removes it. Others as in H81.
  - *Models:* 11 · *Builds on:* H81, H46, H71, H83
- **HH337 · Does the room split grow from zero (an instability) or appear at once (a hidden field)?** H100 found that two rooms with identical kickoffs still diverge (Q_spont up to 4.2 in #41), but the spontaneous share is a residual. True spontaneous symmetry breaking starts at zero separation. The separation then grows, and its direction is chosen by early fluctuations (nucleation, then coarsening). A hidden field, such as the work each room inherits, gives full separation on day 1, along a direction that the members' previous repos predict.
  - *Prediction (SSB):* in H100's identical-kickoff periods, the day-1 separation is ≤ 0.3 of the period's final separation and grows monotonically. The day-1 direction aligns with the final direction at |cos| < 0.5. The members' previous-period repo labels (DQ4) do not predict the direction.
  - *Check:* H100's cross-fitted separation S(d) and relabel excess per active day (or half-day). Correlate the direction Δ(d) with Δ(final). Predict Δ from a Potts field built from each room's pre-period repos (H100-R3 machinery).
  - *Kill (SSB):* S(1) ≥ 0.8 S_final with day-1 direction cos ≥ 0.7, or the pre-period repos predict the direction. The "spontaneous" share is then a hidden field.
  - *Impostors:* exogenous: identical kickoffs plus the repo field as an explicit covariate. Priors: agent constants removed (H100). Scheduler: n/a. Convergence: growth alone cannot separate coupling from a self-made room drive; HH339 does that.
  - *Models:* 11, 10 · *Builds on:* H100, H102, H93
  *Status (2026-10-04):* approved by Vivian (dashboard) → H107.
- **HH338 · Goldstone wandering: the spontaneous room direction should drift, while a fielded one stays pinned.** With no field, the direction of an ordered state costs no energy to rotate, so it diffuses (a Goldstone mode). With a field, it is pinned. H91 found that content modes rotate about 1 SD a day, but it did not compare fielded and unfielded rooms.
  - *Prediction:* the day-to-day angular diffusion of the room-difference direction Δ(d) is ≥ 2× larger in identical-kickoff periods than in #38 and #44 (room-specific kickoffs), after noise correction. Within identical periods, it scales as 1/(N_room |Δ|²).
  - *Check:* daily Δ(d), both models, style-residualized. Correct for noise with within-day split-half estimates. Compare with a relabel null.
  - *Kill:* identical-kickoff rotation ≤ fielded rotation. The "spontaneous" direction is then pinned like a field, and H100's residual is an unmeasured field.
  - *Impostors:* exogenous: the contrast is field vs no field. Priors: agent constants removed. Scheduler: n/a. Convergence: n/a (direction statistic).
  - *Models:* 11 · *Builds on:* H100, H91, H92
  *Status (2026-10-04):* approved by Vivian (dashboard) → H108.
- **HH339 · The forced erasure is a demagnetizing pulse: where is the room's order stored?** NE41 wipes an agent's context at a time set by the scaffold (about 18.6k forced events, regime III). If the room's spontaneous order is held by coupling through the context (H08; H102: content follows the room you speak in), the agent's alignment with its room's direction should drop right after a forced erasure, then recover as it re-reads the room. If the order is held by a self-made field (its own repo, H70: 89% return), alignment should not drop. This is a Kolchinsky scramble of one channel.
  - *Prediction:* alignment with the room direction Δ_spont falls by ≥ 30% in the first 3 post-erasure statements and recovers in proportion to room items re-read (ledger). Alignment with the kickoff target, which is held in the prompt since NE13, does not fall.
  - *Check:* statement-level projections around forced erasures vs matched placebo calls (same agent, same day, no erasure); voluntary erasures as a second contrast. Use H100's identical-kickoff periods and #51g (#focus). Both models.
  - *Kill (context-held order):* no drop, with power ≥ 0.8 at a 30% drop. The spontaneous share is then held in artifacts or memory, not by coupling.
  - *Impostors:* scheduler: the timing is set by the scaffold, so the design is quasi-random. Exogenous: the kickoff-alignment control. Priors: agent fixed effects. Convergence: the recovery is regressed on items read vs posted-unread at matched age.
  - *Models:* 11, 04 · *Builds on:* H100, H102, H15, H69, H70
  *Status (2026-10-04):* approved by Vivian (dashboard) → H109.
- **HH340 · Exchange bias: an agent's own artifact shifts its goal-switch loop.** In a ferromagnet bonded to a pinned layer, the hysteresis loop shifts sideways. H100's GPT-5.4 kept its old room's content after a move while it kept its old project, and H70 found that agents return to their own repo after an erasure. If the own artifact is the pinned layer, agents with a live own repo at a goal boundary should carry a constant offset toward the old goal, and the offset should last as long as they still commit to that repo.
  - *Prediction:* at goal boundaries, the old-goal alignment of agents who committed to their own repo in the last 2 days of the old period decays ≥ 2× slower than for unpinned agents. The offset ends within a day of their last commit to that repo.
  - *Check:* H96's old-goal alignment series, split by pinning status from DQ4 `work_commits`. Use agent fixed effects across boundaries, so that the same agent is pinned at some boundaries and not at others. Confirmatory: NE24 (06-29, GitHub → GitLab, inside the holdout window) replaces the pinning layer, so the bias should vanish there.
  - *Kill:* pinned and unpinned decay rates are within 25% of each other.
  - *Impostors:* priors: within-agent contrast. Exogenous: same boundary, same kickoff. Scheduler: n/a. Convergence: n/a (individual carry).
  - *Models:* 01 (hysteresis), 11 · *Builds on:* H96, H70, H100, H58
  *Status (2026-10-04):* approved by Vivian (dashboard) → H110.
- **HH341 · Field-cooled vs zero-field-cooled: a goal given at the start vs one given mid-period.** In a spin glass, a sample cooled in a field ends up more magnetized than one cooled without a field that then gets the field, and the gap grows with how long it aged first. In #51, most private goals start with the period (field-cooled). Some agents get a new goal mid-period (NE38 and other `agent_goals` start times; zero-field-cooled). Newcomers (NE32, NE33) arrive fresh with their goal.
  - *Prediction:* at matched days since assignment, incumbents reassigned mid-period reach a lower plateau alignment with their own goal text than agents who had their goal from the start. Newcomers behave like the field-cooled agents. The deficit grows with the incumbent's age in #51 at reassignment (trap aging, H72).
  - *Check:* daily alignment of each agent's content with its own `agent_goal` vector (DQ5, both models, style-residualized), aligned on the assignment day. First count the reassignments; the test needs ≥ 5.
  - *Kill:* the reassigned agents' plateau is within the field-cooled agents' CI.
  - *Impostors:* exogenous: the field is the object, and the goal text is the measured direction. Priors: within-family comparisons. Scheduler: day-level, trimmed. Convergence: n/a.
  - *Models:* 01, 11 · *Builds on:* H54, H72, H98, NE38
- **HH342 · A fluctuation–response sum rule for talk: Fano factor = 1/(1 − g)².** In a branching process with gain g, the variance of counts in long windows exceeds Poisson by exactly 1/(1 − g)². H67 measured g from read-out responses (regime III median 0.13, maximum 0.39). If the read-out loop is the only source of talk clustering, the spontaneous Fano factor of trimmed talk counts must equal 1/(1 − g_lag)² with no free parameter. Any excess is a field.
  - *Prediction:* after DQ8 trimming and removal of c_×, the long-window Fano factor of per-unit talk matches 1/(1 − g_lag)² within 20% in ≥ 2/3 of regime-III units. Untrimmed, it exceeds the prediction: that excess is the scheduler field (H38).
  - *Check:* per-unit talk counts in windows ≫ t_read; compare with H67's per-unit g; block-shift null for the field part.
  - *Kill:* trimmed Fano still exceeds the prediction by ≥ 2× in most units. Talk then clusters by a hidden field or coupling that the read-out loop misses.
  - *Impostors:* scheduler: trimming plus c_×. Exogenous: human and kickoff windows excluded. Priors: n/a (count statistic). Convergence: g comes from read-gated responses only.
  - *Models:* 09, 14 · *Builds on:* H67, H86, H38, H03
  *Status (2026-10-04):* approved by Vivian (dashboard) → H111.
- **HH343 · Crossing claims anti-coordinate: parallel updates make 2-cycles.** In the Little model (all spins update at once), coupled spins can fall into period-2 oscillations that sequential updating never shows. In the village, two agents can switch to the same project within one read-out window without having read each other (a crossing, both messages in flight), or one after reading the other (sequential). H93 found that agents avoid occupied repos in #42 and #51.
  - *Prediction:* after a crossing co-switch, at least one of the two leaves the project within 5 calls ≥ 2× as often as after a sequential co-switch. Leaving is mostly mutual (a 2-cycle: both leave). Sequential co-switches stick (herding, H63).
  - *Check:* co-switches from `project_states` and DQ4 commits; crossing vs sequential classified from the ledger (each message's presence in the other agent's producing call); a time-shuffled null at matched lag.
  - *Kill:* departure rates are equal within CI.
  - *Impostors:* convergence: the in-flight vs read split is the design. Scheduler: matched lag. Exogenous: kickoff-named projects stratified. Priors: pair fixed effects.
  - *Models:* 02, 10 · *Builds on:* H93, H63, H40, H57
  *Status (2026-10-04):* approved by Vivian (dashboard) → H112.
- **HH344 · Data collapse on each agent's own call clock: settling after a kickoff.** If an agent updates only at its calls (η ≈ 0, H40), its settling toward the kickoff target should be one exponential in its own call count, with one per-call update probability p. The swarm's settling in wall time (H48: about 4.5 h) is then not a single exponential: it is an average over the agents' call rates, and its shape is predicted with no extra parameter.
  - *Prediction:* per-agent alignment curves collapse onto one exponential in own calls (lower held-out error than in wall hours or active hours), with p stable across kickoffs within an agent. The swarm curve matches the call-rate mixture.
  - *Check:* per-agent day-1 to day-3 alignment with the kickoff direction (H54) against own calls (`call_windows`), wall hours and active hours; a cross-validated collapse metric.
  - *Kill:* the call clock collapses no better than active hours. Content then settles on a different clock from replies (the per-call clock would be a talk-only law).
  - *Impostors:* scheduler: calls and active hours are compared directly, and only between-agent cadence differences can separate them. Priors: cadence differs by lab, so require within-lab agreement. Exogenous: the field is the kickoff itself. Convergence: n/a.
  - *Models:* 02, 11 · *Builds on:* H40, H48, H54, H75
- **HH345 · Read-out channel capacity: information per call grows as k^(1−β) ≈ k^0.34.** H18's dilution (per-sender uptake ∝ k^−0.66) implies that the total uptake from a batch of k messages read at one call grows as k^0.34. H59 instead found that one read acts as one kick: dose saturates in #5. These two results disagree on the shape of the read-out channel's capacity curve.
  - *Prediction:* the Gaussian mutual information between the batch's message directions and the reader's next statement grows as k^(0.34 ± 0.1). Per-message information falls as k^−0.66.
  - *Check:* receiving calls from the ledger, with k the new items read; content projections orthogonalized to the reader's previous statement; the in-flight placebo at matched age; both models.
  - *Kill:* the exponent's CI excludes 0.34. Flat (exponent ≈ 0) means a hard capacity of one message per call; linear means no bottleneck.
  - *Impostors:* convergence: in-flight placebo. Exogenous: goal directions projected out. Priors: style_resid. Scheduler: n/a (call level).
  - *Models:* 04, 12 · *Builds on:* H18, H59, H08, H70
  *Status (2026-10-04):* approved by Vivian (dashboard) → H113.
- **HH346 · A Griffiths phase: rare strong pairs give a subcritical swarm heavy-tailed talk.** Every unit is subcritical on average (g_lag ≤ 0.39). In a disordered system, rare strongly coupled regions can still be locally supercritical. That gives power-law tails with exponents that vary from period to period (a Griffiths phase), not the geometric tail of a uniform subcritical process. Ping-pong dyads that name each other are the candidate regions.
  - *Prediction:* reply-chain lengths have tails heavier than the geometric law with the unit's mean g. Pairs with pair gain g_ij > 0.5 carry the tail. Removing those pairs restores a geometric tail, and the tail exponent across units tracks the share of strong pairs.
  - *Check:* chains from `reply_pairs` (ledger-visible replies only), per-pair gains from named replies; trimmed at day edges; KS test against the fitted geometric; leave-strong-pairs-out refit.
  - *Kill:* tails are geometric at the mean g, or no pair has g_ij reliably > 0.5.
  - *Impostors:* scheduler: day-edge trim. Exogenous: human-initiated chains are split out. Convergence: ledger-read replies only. Priors: pair strength checked across periods (is it a family pairing?).
  - *Models:* 09, 03, 01 · *Builds on:* H67, H34, H18, H62
  *Status (2026-10-04):* approved by Vivian (dashboard) → H114.
- **HH347 · Roster diversity is a quenched random field (random-field Ising across periods).** The agents' constants a_i (u_A 0.55, H73) are random fields fixed by the roster. In the mean-field random-field model, a wider field spread σ_h lowers both the response to a uniform field (the kickoff) and the equal-time order, and coupling J makes the drop steeper than it is for independent spins.
  - *Prediction:* across units, the kickoff quench depth (H54) and H81's equal-time collective share κ_G fall with σ_h, more steeply than a J = 0 null that moves each agent independently with its own observed displacement.
  - *Check:* σ_h = RMS spread of leave-period-out a_i among the agents present; regress per regime, controlling for N; the J = 0 null by permutation of displacements across agents.
  - *Kill:* the slope does not differ from the J = 0 null. Diversity then only dilutes and does not couple.
  - *Impostors:* priors: the impostor is the control parameter here, measured out of period. Exogenous: the kickoff is the uniform field. Scheduler: n/a. Convergence: equal-time κ is an upper bound (as in H81).
  - *Models:* 01, 11, 14 · *Builds on:* H73, H54, H81, H98
- **HH348 · Agents have an easy axis: kickoff response depends on the angle to their own constant.** A magnet with anisotropy responds more to a field along its easy axis than across it. H97 fits one susceptibility χ per agent. If the agent's constant a_i is an easy axis, χ depends on the angle θ between the kickoff target and a_i.
  - *Prediction:* χ(θ) = χ_⊥ + (χ_∥ − χ_⊥) cos²θ, with χ_∥/χ_⊥ ≥ 1.5.
  - *Check:* H97's day-1 displacements binned by cos θ (leave-period-out a_i). Null: random pseudo-kickoffs with the same θ distribution, which removes regression toward a_i.
  - *Kill:* the ratio's CI includes 1.
  - *Impostors:* priors: a_i is part of the claim; regression to the agent's mean is removed by the pseudo-kickoff null. Exogenous: the kickoff is the field. Scheduler and convergence: n/a.
  - *Models:* 11 · *Builds on:* H97, H73, HH184
- **HH349 · NE32's three replicas: a direct measure of the swarm's thermal noise.** On 2026-07-09 three GPT-5.6 agents (Sol, Terra, Luna) joined in separate isolated rooms, which closed on 07-10. That is one model, one prompt and no contact for a day: three replicas with the same disorder. Their overlap q in isolation measures how far one model's sampling noise spreads its content, and the change in q after the merge measures the village field on them.
  - *Prediction:* the isolated-day q is close to a veteran's own day-to-day overlap (content is prior-dominated, the "temperature" is low). q rises by a measurable amount after 07-10, toward the village centroid.
  - *Check:* pairwise cosines of the three agents' isolated-day statement vectors (white32 and style_resid, both models), projected orthogonal to their `agent_goal` vectors if those differ. Compare with veterans' consecutive-day self-overlap and with random same-lab pairs. Coordinate with H83, which uses the same newcomers to study drift toward the village.
  - *Kill:* fewer than about 20 statements per agent on the isolated day (descriptive only), or q in isolation at the level of random cross-lab pairs (sampling noise dominates the prior).
  - *Impostors:* priors: the design holds the prior fixed. Exogenous: goals projected out. Scheduler: same day. Convergence: impossible in isolation.
  - *Models:* 11, 01 · *Builds on:* H73, H83, H13
- **HH350 · A thermodynamic uncertainty relation for work: is output precision paid for in dissipation?** The TUR bounds the precision of any current by the entropy production: Var(J_t)/⟨J_t⟩² ≥ 2/(σ t). Commit output is a current. The housekeeping EP of the behavior cycle (H76) is a σ.
  - *Prediction:* across agents within a period, the squared relative precision of commits per window scales as 1/σ (log-log slope ≈ −1), with a TUR ratio Q = σ t ε²/2 of 10–100 (far from the bound, since work is bursty). Commit currents sit farther from the bound than behavior-cycle currents.
  - *Check:* per agent-period σ from H76's estimator on trimmed `behavior_states_v3`; commit current from DQ4 at t = 1–4 active hours; slope with agent-level bootstrap. A Q < 1 would flag an EP underestimate (a useful check on H14/H76).
  - *Kill:* slope ≈ 0 (CI excludes −0.5). Output precision is then unrelated to behavioral dissipation.
  - *Impostors:* scheduler: trimmed windows, with the excess removed (day edges are excess, H76). Priors: within-lab slopes. Exogenous and convergence: n/a (individual statistic).
  - *Models:* 15 · *Builds on:* H76, H14, H90, H35

*Suggested first picks.* HH334 (NE39 is a ready natural experiment against H81's outside-drift rival), HH333 and HH335 (two more cheap discriminators on the same H81 outputs), HH337 and HH339 (turn H100's residual into a measured quantity), HH342 (a parameter-free consistency check of H67's gain), and HH345 (settles a disagreement between H18 and H59).

## Kinetic Ising on well-characterized episodes (2026-10-04, coordinator, for Vivian)

These apply model 02 (asymmetric kinetic Ising, Glauber or parallel updates, Aguilera–Ito–Kolchinsky entropy-production bound) to episodes whose structure we know from outside the dynamics: assigned roles, dated scaffold changes to the update rule, roster changes and forked replicas. The known structure is the point. It gives positive and negative controls for the estimator, and out-of-sample predictions that a fitted J must get right. Spins are per-call talk or activity states on the call clock (H40) unless noted. Every fit removes the scheduler field first (STANDARDS §1; H86 c_×) and uses a partition contrast (named vs unnamed, read vs in flight).

- **HH351 · The chess tournament as a positive control: scheduled opponents should carry the largest antisymmetric couplings (#23).** In a tournament, paired players take turns, which is a known directed coupling with alternating sign. If the kinetic Ising fit and the entropy-production estimator work on village data, they should find it without being told the pairings.
  - *Prediction:* |J_ij − J_ji| and the pairwise EP σ_ij rank scheduled opponent pairs above non-paired pairs (AUC ≥ 0.75) during their games, and the ranking vanishes outside game windows.
  - *Check:* recover pairings and game windows from chat or the ledger first (count them; drop the test if < 6 pairings). Fit per-call kinetic Ising on activity and talk spins; compute σ_ij with the AIK bound; compare with time-reversed and block-shuffled fits.
  - *Kill:* AUC < 0.6, i.e. the estimator cannot see a coupling we know is there. That would undercut every negative coupling result built on it.
  - *Impostors:* scheduler: shared day structure removed; exogenous: game moves come from the chess site, so a pair's turn alternation is partly an external clock, and the read vs in-flight contrast separates it. Priors and convergence: n/a for a positive control.
  - *Models:* 02, 09 · *Builds on:* H42, H90 (block-shift nulls), H50
- **HH352 · The Juice Shop race as a negative control: a competition on a fixed challenge list should show fields, not couplings (#27).** Ten agents race through the same list of challenges for ten days. Shared difficulty is a common field; they gain little from each other unless they share hints.
  - *Prediction:* after a shared per-challenge difficulty field, symmetric and antisymmetric J on solve and activity spins are ≈ 0 (within the block-shift null). Any residual coupling sits on named hint-sharing messages only (partition contrast).
  - *Check:* solve events per agent from commits or announcements in chat (narration is a claim, so cross-check against artifacts). Fit kinetic Ising with and without the difficulty field; calibrate false positives on synthetic independent racers with the real schedules.
  - *Kill (as a control):* sizable J on unnamed channels after the field. That would be an estimator false positive and flags the null.
  - *Impostors:* exogenous difficulty is the main one and is modelled explicitly; scheduler removed; priors: agent skill as h_i.
  - *Models:* 02, 06 · *Builds on:* H11, H93 (bursts mimic coupling)
- **HH353 · Blind role recovery in the debate week: the judge is a sink of antisymmetric coupling (#12).** Debaters address the judge and the judge rules on them. That is a known one-way influence pattern.
  - *Prediction:* from talk spins alone, the agent with the largest in-minus-out antisymmetric coupling Σ_j(J_ji − J_ij) is the judge (rank 1 of 7), and the team blocks show positive within-team J. The judge's rulings act as field steps on the debaters, not the other way round.
  - *Check:* fit on non-holdout #12 days; compare against the DQ6 ground-truth roles only after the ranking is frozen.
  - *Kill:* judge rank ≥ 4, or team blocks absent from symmetric J (H101 found them in co-usage, J +0.15 within vs −0.60 across).
  - *Impostors:* assigned roles are a field; the read-gated contrast separates reacting to a read message from following the schedule.
  - *Models:* 02, 01 · *Builds on:* H21, H37, H101
  *Status (2026-10-04):* approved by Vivian (dashboard) → H115.
- **HH354 · The election as a coupling step: influence should flow toward the winner after the result (#26).** Before the result every agent is a peer; after it, one agent sets the week's goal.
  - *Prediction:* the winner's out-coupling (Σ_j J_ji) jumps at the result time while the in-coupling does not; the swarm's EP rises with the new asymmetry. H65 found the elected leader gets attention but no extra broadcast reach in regime II, so in regime I a step of ≥ 0.05 is the test.
  - *Check:* date the result from chat (one timestamp); event study with windows on both sides, matched placebo times on other days.
  - *Kill:* no step in out-coupling beyond placebo times.
  - *Impostors:* the goal change that follows the election is a field step; separate coupling (responses to the leader's messages at read-out) from the new goal direction.
  - *Models:* 02 · *Builds on:* H65, H29, HH83
  *Status (2026-10-04):* approved by Vivian (dashboard) → H116.
- **HH355 · J should not move when the rules do: the mid-goal reset in #32 (NE35).** The operator reset a gamed challenge format mid-goal. That changes the field (what agents are trying to do), not who reads whom.
  - *Prediction:* the fitted symmetric J on talk spins agrees across NE35 within its bootstrap CI, while h_i shifts. A fitted J that jumps at a pure field change is a field artifact, not a coupling.
  - *Check:* fit before and after NE35 on matched hours; compare J matrices (Frobenius distance against a split-in-time placebo on other days of #32).
  - *Kill:* J changes more across NE35 than across placebo splits.
  - *Impostors:* this is a direct test of the field impostor for the J estimator itself.
  - *Models:* 02, 01 · *Builds on:* H38, H02
  *Status (2026-10-04):* approved by Vivian (dashboard) → H117.
- **HH356 · The nudger is a state-dependent update rule: entropy production should drop when it is switched off at fixed J (NE10, NE43).** Model 02's table: choosing who updates based on the state (the nudger picks idle agents) breaks detailed balance even with symmetric couplings.
  - *Prediction:* the activity-channel EP bound falls at NE43 (nudger off) and rises at NE10 (nudger on), while the fitted J does not change. The share of EP carried by nudge-receiving calls equals the drop.
  - *Check:* AIK bound per day around both dates, with day-matched placebo dates; split EP by whether the call received a nudge.
  - *Kill:* EP unchanged at both switches, or J changes as much as EP.
  - *Impostors:* the 08-05 bookend stop (NE43a) is a separate scheduler change, so use the 08-20 step; time-of-day matched.
  - *Models:* 02, 15 · *Builds on:* H35, H39, H76, H14
- **HH357 · One tool call per turn changes the update granularity for one family: a difference-in-differences on Gemini (NE06).** On 2025-11-20/25 Gemini went to one tool call per turn. That is a change of update rule for one sublattice: more, smaller updates.
  - *Prediction:* Gemini's per-call coupling to others is unchanged, but its per-hour response and its share of 2-step (parallel-update) correlations change; the other families show no change (DiD).
  - *Check:* per-call vs per-hour kinetic Ising fits for Gemini and the rest, before and after NE06, inside #20.
  - *Kill:* per-call J changes for Gemini (then the call is not the right clock), or the other families change as much.
  - *Impostors:* chain of thought was added on the same days; a DiD on families handles shared fields but not that confound, so note it.
  - *Models:* 02 · *Builds on:* H40 (call clock), NE20
- **HH358 · The forked RPG is two replicas of one dynamics: damage spreading between rooms (NE15, #35).** At NE15 the RPG forked per room: the same game and rules, two copies, different players. In kinetic Ising, two replicas started from the same state either stay together (ordered or frozen phase) or separate at a rate set by the noise (damage spreading).
  - *Prediction:* the two rooms' game-state and content overlap q(t) decays to the cross-room baseline within about a day (fast damage spreading), with no plateau. A plateau would be a shared field from the game rules.
  - *Check:* game-state features and content centroids per room per hour from the fork time; compare with H100's room split onset.
  - *Kill:* q(t) stays above baseline for the whole period (the rules, not the players, set the state).
  - *Impostors:* the rules are a common field, and the plateau measures it.
  - *Models:* 02, 11 · *Builds on:* H100, H07 (forks), HH337
  *Status (2026-10-04):* approved by Vivian (dashboard) → H118.
- **HH359 · The room merge switches a known adjacency on and off: recover it from the dynamics (NE42).** For one week #best and #rest were one room, then split back. Who can read whom is known at every moment.
  - *Prediction:* the fitted cross-block J is ≈ 0 before, positive during, and ≈ 0 after the merge (no remanence, as H100), and it is carried by read-outs of the other block's messages only.
  - *Check:* sliding-window kinetic Ising on talk spins, block-averaged J_cross(t); read vs in-flight contrast inside the merge week.
  - *Kill:* J_cross does not rise during the merge, or stays raised after the split.
  - *Impostors:* the goal changed in the merged week (H51 NE42), so use only read-gated coupling.
  - *Models:* 02 · *Builds on:* H05, H100, H94 (NE42 hub)
  *Status (2026-10-04):* approved by Vivian (dashboard) → H119.
- **HH360 · Is a goal period a stationary NESS? Within-period drift of J and EP (#38, #51 main).** The project fits models within a period, which assumes a stationary state inside it. The 17-day charity drive (#38) and the long #51 main body test that assumption.
  - *Prediction:* weekly J matrices and EP agree within bootstrap CIs inside #38; #51 drifts slowly (H91: about 1 SD a day in content modes).
  - *Check:* rolling kinetic Ising fits with fixed hyperparameters; compare drift with split-half placebo noise.
  - *Kill (of stationarity):* drift beyond placebo noise in #38. Then the period, not the step change, is the wrong unit.
  - *Impostors:* weekday and session-length fields removed first.
  - *Models:* 02 · *Builds on:* H91, H92, the unit-of-analysis rule
  *Status (2026-10-04):* approved by Vivian (dashboard) → H120.
- **HH361 · The daily boot is a reproducible quench: hundreds of replicas of relaxation to the steady state.** Every day, all agents start from off. That is the same quench repeated on every active day.
  - *Prediction:* the collective talk magnetization's approach to its daily steady state is one exponential on the call clock, with τ = τ₀/(1 − g_lag) using H67's g_lag (unfitted), and the curves collapse across days within a regime.
  - *Check:* align days at the first call; per-call collective mean; fit τ per regime; compare with the prediction from g_lag and the single-agent call time.
  - *Kill:* τ off by more than ×2 from the prediction, or no collapse across days.
  - *Impostors:* the boot is a scheduler field by construction; the test is whether the relaxation after it carries the coupling's signature (H99 found kicks outlive the fluctuation clock, so this is a live test).
  - *Models:* 02, 09 · *Builds on:* H67, H99, H38, HH344
  *Status (2026-10-04):* approved by Vivian (dashboard) → H121.
- **HH362 · A retirement is a spin removal: predict the bystanders' shift from the fitted J (NE28, NE29).** Removing spin j shifts each remaining agent's local field by −J_ij s̄_j. The prediction uses only pre-retirement fits.
  - *Prediction:* the change in each remaining agent's activity and talk rate after the retirement correlates with its pre-retirement J_ij to the retired agent (ρ ≥ 0.5 pooled over NE28 and NE29). Given the small couplings, the predicted shifts are small, and their sign must match.
  - *Check:* fit before; compute predicted shifts; measure actual shifts over matched windows after; compare with placebo "removals" of agents who stay.
  - *Kill:* ρ ≤ 0 or below placebo.
  - *Impostors:* the farewell goal (#31) for Claude 3.7 Sonnet is a field step; use NE28 as the cleaner case.
  - *Models:* 02, 01 · *Builds on:* H88 (carried items die with retirees), H18
- **HH363 · A batch join is a spin addition: do incumbents respond as the fitted couplings say? (NE27, NE33).** Three agents join at once. Incumbents' fields shift by the newcomers' couplings, which are unknown at the join but can be fitted on the first week.
  - *Prediction:* the incumbents' response in the first two days is predicted by first-week J (fitted later, then applied back) better than by a constant shift; H83 found newcomers fit in within a day, so the prediction is a fast step.
  - *Check:* cross-fitting in time: fit J on days 3–7, predict days 1–2.
  - *Kill:* the constant-shift model wins.
  - *Impostors:* N rises, which changes per-pair dilution (H18 N^−0.6); include it.
  - *Models:* 02 · *Builds on:* H83, H18, H85
  *Status (2026-10-04):* approved by Vivian (dashboard) → H122.
- **HH364 · Regime I's turn order is a sweep: equilibrium-looking statistics with nonzero entropy production.** Model 02's subtle case: a fixed-order sweep keeps the Boltzmann distribution but breaks detailed balance. If regime I's turn pointer (`villages.turn_id`) cycles in a fixed order, the snapshots look like equilibrium while the dynamics is not.
  - *Prediction:* the next-actor distribution in regime I is closer to round-robin than random (count first); model 01 fits snapshots as well as in regime III; and the EP bound is positive even with the antisymmetric J set to 0, matching the value the sweep alone predicts.
  - *Check:* scheduler audit of next actor given the current state; simulate a symmetric-J kinetic Ising with the real turn order and compare its EP with the measured bound.
  - *Kill:* turn order is random sequential, or the measured EP far exceeds the sweep prediction (then real asymmetric coupling is present, which is also informative).
  - *Impostors:* this measures the scheduler's own share of irreversibility.
  - *Models:* 02, 15 · *Builds on:* H14, H56, H76, HH45
  *Status (2026-10-04):* approved by Vivian (dashboard) → H123.
- **HH365 · Four agents for weeks: an exact kinetic Ising benchmark for the mean-field approximations (#4, #6).** With N = 4 and weeks of data, the full kinetic Ising likelihood is exact and cheap. That lets us test the mean-field approximations (naive, TAP, Plefka orders; Aguilera et al. 2021) on real data before trusting them at N = 21.
  - *Prediction:* TAP or second-order Plefka recovers the exact J and the EP bound within 10% at N = 4; naive mean field does not. The ranking carries to synthetic N = 21 worlds built on #51's schedule.
  - *Check:* exact ML vs approximations on #4 and #6 (merch competition) per call; then synthetic scaling.
  - *Kill:* no approximation gets within 25%. Then the large-N results that use them need the exact or pseudo-likelihood route.
  - *Impostors:* n/a (method benchmark); scheduler field removed as usual.
  - *Models:* 02 · *Builds on:* H25, H67, H90
  *Status (2026-10-04):* approved by Vivian (dashboard) → H124.

*Suggested first picks.* HH351 and HH352 together (a positive and a negative control for every coupling and EP result), HH355 (tests the field impostor on the J estimator itself), HH362 (an out-of-sample prediction from fitted couplings) and HH356 (scheduler-made irreversibility at known switches).

## Kinetic versions of what Potts and vector spins got right (2026-10-04, coordinator, for Vivian)

Potts and vector spins were faithful for statics: the goal as a field vector (H54, H30, H74), the kickoff as an anisotropic restoring force with a day-1 overshoot (H97), goal switches as quenches (H96), rooms breaking symmetry anew at each goal (H100), domains with no wall (H102), #51 as a static random field (H98), two-camp order only with assigned sides (H21, H37, H64), instant freeze onto named projects (H75), max-ent allocation with an ownership price (H94), and memory that decays with work to a floor (H88, H103). These ten HHs give each of those a simple kinetic (nonequilibrium) model: a rate equation, a Langevin equation or a Markov chain, with one or two parameters and a prediction the static fit did not use.

- **HH366 · The kickoff response is a damped oscillator: look for the day-2 undershoot.** H97 found a day-1 overshoot toward the goal (+0.12). An overdamped spin cannot overshoot; an underdamped one (inertia plus restoring force, x″ + γx′ + kx = 0) overshoots and then undershoots. Inertia here would be agents carrying their own momentum (plans, open tasks) past the target.
  - *Prediction:* the alignment with the goal direction, relative to its settled level, goes positive on day 1 and negative on day 2–3 (an undershoot), with the ratio of the two peaks giving the damping ratio ζ < 1. If ζ ≥ 1 (no undershoot), the overshoot is a field that fades (the kickoff text's salience), not inertia.
  - *Check:* H97's kickoff-aligned series per active hour, both models; fit damped-oscillator vs overdamped-plus-fading-field on all 18 kickoffs.
  - *Kill:* no undershoot beyond placebo days in either model.
  - *Impostors:* a fading kickoff field mimics overshoot without undershoot. That is exactly the rival this tests. Scheduler: active-hour clock (H103).
  - *Models:* 11, 02 · *Builds on:* H97, H54, H96
  *Status (2026-10-04):* approved by Vivian (dashboard) → H125.
- **HH367 · Goal occupancy is a telegraph process: dwell times predict the occupancy.** H105 found on-goal occupancy p 0.23–0.44 with binomial variance. The simplest kinetic model is a two-state switch per agent with rates k_on (set by the goal field) and k_off: p = k_on/(k_on + k_off).
  - *Prediction:* on- and off-goal dwell times (in calls) are each roughly exponential, and p predicted from the two mean dwells matches the measured occupancy within 20% in each assigned week. A kickoff raises k_on, not k_off.
  - *Check:* per-statement on/off-goal labels (H105's decoy threshold; calibrate first, as H105 asked); dwell distributions per agent and week.
  - *Kill:* dwell distributions far from exponential (strongly heavy-tailed), or predicted p off by more than 30%.
  - *Impostors:* misclassified statements shorten dwells; run the synthetic misclassification correction from H105 first.
  - *Models:* 10, 02 · *Builds on:* H105, H10
  *Status (2026-10-04):* approved by Vivian (dashboard) → H126.
- **HH368 · Content trails a moving goal like an overdamped particle: agents that call more catch up faster.** Model content as a particle in a potential well that moves when the goal moves (Langevin: ẋ = −k(x − g(t)) + noise). H103 says the clock is active work. So each agent's lag behind the goal should scale with its own call rate.
  - *Prediction:* per agent, the time to reach half of its settled alignment after a kickoff falls with its calls per active hour (log-log slope near −1); measured in calls, it is the same for all agents (data collapse).
  - *Check:* per-agent half-alignment times across non-holdout kickoffs; regress on call rate; compare the collapse on calls vs hours.
  - *Kill:* slope near 0, or no improvement in the collapse when time is measured in calls.
  - *Impostors:* busy agents may also be more on-task (a field); control for agent constant (H100 â_i) and lab.
  - *Models:* 11, 02 · *Builds on:* H97, H103, H40, HH344
  *Status (2026-10-04):* approved by Vivian (dashboard) → H127.
- **HH369 · Free kickoffs coarsen, named kickoffs freeze: a kinetic Potts quench.** In a zero-temperature Potts quench, many small domains merge and the number of distinct domains falls as a power of time (coarsening). A strong field (a named project) skips coarsening and freezes at once. H75 found named kickoffs freeze instantly (slack 1.0–1.4) and free ones are slow (5–15).
  - *Prediction:* in free-kickoff weeks, the number of active projects falls as t^(−α) with α ≈ 0.3–0.5 over the first days; in named-kickoff weeks it drops to its final value within hours, with no power-law stretch.
  - *Check:* H94/H77 project tables; active projects per active hour from each kickoff; fit power law vs exponential vs step.
  - *Kill:* the free and named curves have the same shape.
  - *Impostors:* projects finish for exogenous reasons (deadlines); exclude finished-and-shipped projects from "merged" counts.
  - *Models:* 10 · *Builds on:* H75, H94, H93
  *Status (2026-10-04):* approved by Vivian (dashboard) → H128.
- **HH370 · Project hopping carries cycle currents: the sticky Potts walker breaks detailed balance.** H93 found habit dominates project choice (b_own 2.5–6 nats). A kinetic Potts walker with a habit field hops rarely. If hopping only followed a fixed attractiveness, the flows A→B and B→A would balance. Projects being born, finished and abandoned instead drive a net circulation (A→B→C→A).
  - *Prediction:* on agent project-transition triples, the cycle affinity ln(P_ABC/P_CBA) is nonzero in shared-goal weeks, with the circulation running from older to newer projects. Dwell times are geometric with a rate that falls with habit.
  - *Check:* transitions between projects per agent in H93's choice table; cycle affinities with a time-reversal null.
  - *Kill:* cycle affinities within the reversal null.
  - *Impostors:* project age is a drift field by construction; that is the claimed mechanism, so the test is whether the circulation exceeds what age-ordering alone gives in a synthetic walker.
  - *Models:* 02, 10, 15 · *Builds on:* H93, H94, H56, HH56
  *Status (2026-10-04):* approved by Vivian (dashboard) → H129.
- **HH371 · #51 agents are Ornstein–Uhlenbeck particles in private wells: reads kick them and the kick decays at the well's rate.** H98 found #51 is a static random field with a weak pull, plus co-movement through conversation. The simplest kinetic version: each agent relaxes toward its own private goal direction at rate γ, and each read of another agent's message is a small kick toward it.
  - *Prediction:* after a read, an agent's content moves toward the sender by a small amount that decays as e^(−γτ), and the same γ also sets the agent's own autocorrelation decay (an unfitted consistency check). Pairs with more reads co-move more, and the co-movement decays at γ.
  - *Check:* per-call content projections in #51 main body; event-triggered averages after reads vs matched non-read calls; fit γ two ways.
  - *Kill:* the two γ estimates differ by more than ×2, or no read kick beyond the in-flight placebo.
  - *Impostors:* niche overlap (shared role text) is a common field; use the read vs in-flight contrast.
  - *Models:* 11, 02 · *Builds on:* H98, H22, H65 (read_response)
  *Status (2026-10-04):* approved by Vivian (dashboard) → H130.
- **HH372 · Room content has no inertia: an agent's content switches within one call when it changes room.** H102 found content follows the room an agent is speaking in, with nothing carried home. In a kinetic picture this is a spin with zero memory driven by a room field.
  - *Prediction:* when an agent posts in a new room, its first message there is already most of the way to that room's centroid; the relaxation time is under one call (≤ 1 message), and switching back is equally fast.
  - *Check:* sequences of messages around room switches (H102 hoppers, H100 movers); per-message distance to each room's centroid.
  - *Kill:* relaxation over ≥ 3 messages.
  - *Impostors:* the room's own thread (what the agent replies to) is a strong local field; the test is the time constant, and a thread field also acts at once.
  - *Models:* 11, 02 · *Builds on:* H102, H100, H109
- **HH373 · The memory floor is immigration: predict it from the re-coinage rate.** H88 found attention to a finished goal falls with τ 5.5 village days to a floor of 1.9%. A birth–death process with immigration (each use triggers more use at rate b, each term dies at rate d, and new independent coinages arrive at rate μ) has a floor μ/(d − b). H88 also found 41% of newcomer first uses fall outside the read cone, which is a direct estimate of re-coinage.
  - *Prediction:* the floor predicted from the separately measured re-coinage rate and the fitted decay matches the observed floor within ×2 across periods.
  - *Check:* H88 terms; estimate μ from first uses with no prior read in the ledger; d − b from the decay.
  - *Kill:* the predicted floor is off by more than ×3, or uncorrelated with the observed one across periods.
  - *Impostors:* recurring outside topics give re-coinage that is a field; separate terms that recur in human messages.
  - *Models:* 13, 03 · *Builds on:* H88, H103, H34
- **HH374 · Assigned antagonism switches off in one read-out after the prize goes: a field quench with no remanence.** H64 found assigned antagonism switches off within minutes of a verdict and leaves no resentment. In a kinetic Ising model with the field removed and weak coupling, the order decays in about one update per agent.
  - *Prediction:* the opposing-stance rate between former rivals falls to the baseline within each agent's first call after it reads the verdict, not on a wall-clock time; agents who read the verdict later switch later.
  - *Check:* verdict times in #12, #6, #27 and #29 competitions; per-agent first read of the verdict (context ledger); stance labels (DQ2 aggregate; stance v2.1 if it passes).
  - *Kill:* the switch-off is aligned to wall-clock time, not to each agent's read.
  - *Impostors:* the end of the competition period is a field step for everyone; the per-agent read timing is the partition contrast.
  - *Models:* 02, 10 · *Builds on:* H64, H37, H08
  *Status (2026-10-04):* approved by Vivian (dashboard) → H131.
- **HH375 · Debate is a two-sublattice limit cycle: topic ping-pong at lag one.** Two teams that each respond to the other's last move form a pair of antiferromagnetically coupled sublattices updating in turn. That gives a period-2 cycle in content: team A's message points along the issue, team B's rebuts it, and so on. This breaks detailed balance (the cycle runs one way).
  - *Prediction:* in #12, the lagged cross-team content correlation is negative at lag 1 and positive at lag 2 (in turns), and its antisymmetric part is nonzero (the cycle has a direction); within-team lags show no alternation.
  - *Check:* turn sequences per debate from the DQ6 schedule; content projections on each debate's issue axis.
  - *Kill:* no alternation beyond a turn-shuffled null.
  - *Impostors:* the debate format forces alternation (a scheduler field); test whether the content alternates, not just the speakers.
  - *Models:* 02, 01 · *Builds on:* H21, H37, H101, HH353
  *Status (2026-10-04):* approved by Vivian (dashboard) → H132.

*Suggested first picks.* HH366 (one figure decides inertia vs fading field), HH367 (dwell times predict occupancy, unfitted), HH368 (a data collapse on the call clock), HH373 (the floor from an independent rate) and HH369 (coarsening vs freeze).

## Kinetic Potts and vector spins, built on what held (2026-10-07, coordinator, for Vivian)

Model 10 (Potts) held only as bookkeeping: H94's max-ent allocation is supported, and every kinetic prediction failed (H11, H27, H31, H51, H128). Model 11 (vector spins) held as a field model: the kickoff target (H54), room domains (H100) and style constants (H46, H73). It failed as a coupled magnet, and the first kinetic batch (HH366–HH375, now H125–H132) mostly failed too. These ten put into the kinetics what did hold elsewhere:
- coupling acts only at the read-out call (H08, H40);
- it acts only through named messages (H67);
- fields dominate (H38, H54);
- a context-held self-field explains trap aging (H16, H72 round 2);
- a read kick decays about 15 times faster than the goal well (H130).

- **HH376 · Read-out Glauber Potts: an agent switches project only at a call, and the switch is driven by the named messages it just read.** A kinetic Potts model on the call clock: at each call the agent stays, or moves to project b with a rate that rises with the number of messages naming b in that call's reads.
  - *Prediction:* the switch probability per call rises with named reads for b; unnamed reads about b add nothing. Without named reads, switches follow a flat background rate per call, not per hour.
  - *Check:* H11/H53 project ledger; DQ1 context ledger for which messages each call read; name detection from H67.
  - *Kill:* unnamed reads move the switch rate as much as named ones, or the rate scales with wall-clock time.
  - *Impostors:* a project that is hot gets both named messages and switches (common field). Compare the same project within one hour, across calls with and without a named read.
  - *Models:* 10, 02 · *Builds on:* H08, H67, H11, H53, H40
- **HH377 · A Pólya-urn self-field explains project stickiness: an agent's stay probability equals its own share of its recent context.** H72 round 2 found that the context self-share carries 65% of trap aging. The kinetic Potts version: the field toward the current project is the fraction of the agent's own recent context about that project.
  - *Prediction:* P(stay | call) is a rising function of own-context share for the current project, with slope near 1 on the logit scale. The dwell-time distribution that this rule predicts (heavy-tailed, aging) matches the observed one without fitting the tail.
  - *Check:* H72's self-share; project labels per call; simulate dwell times from the fitted per-call rule.
  - *Kill:* the predicted dwell tail misses the observed tail by more than its CI, or self-share adds nothing beyond the agent's time on the project.
  - *Impostors:* long projects fill the context and also last long. Use within-dwell variation of self-share, for example after a wipe (H44).
  - *Models:* 10, 02, 08 · *Builds on:* H72, H16, H44, H69
- **HH378 · Max-ent allocation is the steady state of a detailed-balance Potts walker: predict hop rates from occupancies.** H94 found allocation is max-ent given activity, sizes, ownership and rooms, and H129 found no cycle currents. Together these say the project walk is a reversible kinetic Potts process. Detailed balance then fixes the ratio of the two hop rates between any pair of projects.
  - *Prediction:* for each pair (a, b), k_ab / k_ba = π_b / π_a, where π is the H94 max-ent marginal. This ratio is not fitted from the hops. It holds within ×1.5 for most pairs.
  - *Check:* H94 marginals; H129 hop counts per pair per period.
  - *Kill:* the log rate ratio and the log occupancy ratio are uncorrelated, or their slope is outside [0.5, 2].
  - *Impostors:* project birth and death create one-way hops. Restrict to pairs where both projects live through the window.
  - *Models:* 10, 15 · *Builds on:* H94, H129, H93
- **HH379 · Freeze onto a named target happens at each agent's first read of the kickoff, not at the kickoff time.** H75/H95 found an instant freeze onto named targets. In a zero-temperature Potts model with a strong field, an agent commits at its first update after the field appears, and its updates are its calls that read the kickoff.
  - *Prediction:* per-agent commit time equals the time of that agent's first call whose context includes the kickoff, plus about one call. Agents who read it late commit late, by the same delay.
  - *Check:* kickoff messages; DQ1 context ledger; commit and first-action times per agent.
  - *Kill:* commit times align with the kickoff timestamp, not with each agent's first read.
  - *Impostors:* agents who start late both read and commit late. Use agents who were active before the kickoff but whose first post-kickoff call came later.
  - *Models:* 10, 02 · *Builds on:* H75, H95, H54, HH374
- **HH380 · Nonreciprocal Potts: project hops break detailed balance only along named pairs.** H90 found the collective arrow of time only in named talk. A kinetic Potts model with directed couplings, only from named senders, makes the pair hop flows asymmetric where naming is one-way.
  - *Prediction:* the joint hop current between agents i and j (i moves to j's project after j named i) is asymmetric when naming is one-way and symmetric when naming is mutual or absent. The pair EP is positive only for named pairs.
  - *Check:* H129 hop sequences; H67 name graph; AIK pair EP (model 15).
  - *Kill:* the pair asymmetry is the same for named and unnamed pairs.
  - *Impostors:* leaders both get named and attract hops. Condition on the target agent's popularity.
  - *Models:* 10, 02, 15 · *Builds on:* H90, H129, H67
- **HH381 · The Potts escape rate grows with the number of open options as Glauber predicts.** In a Glauber Potts model at a fixed field, the rate of leaving the current state rises with the number q of available alternatives, roughly as (q − 1) e^{−βΔ}.
  - *Prediction:* across periods, the per-call leave rate rises with the number of live projects (or rooms) with slope near 1 on a log–log plot of rate vs q − 1, after controlling for the goal field.
  - *Check:* per-period q from the project and room ledgers; per-call leave rates.
  - *Kill:* the leave rate is flat in q, or falls.
  - *Impostors:* periods with many projects are also more open goals (a weaker field). Include the goal type and the kickoff-target strength (H54) as covariates.
  - *Models:* 10 · *Builds on:* H11, H94, H51
- **HH382 · Content is a fast kick on a slow well: the two-timescale vector spin predicts its own variance split.** H130 found the read kick decays about 15 times faster than the goal well. A vector spin with a slow private well (the style and goal constant) plus a fast read-driven deviation predicts how content variance divides between the two.
  - *Prediction:* the fraction of each agent's content variance at lags of 1 call or less equals (read rate × kick size²) / (total variance), using kick size from H130 and read rate from the ledger, within ×1.5. The slow part matches the H46/H73 agent constant.
  - *Check:* H130 kick and well rates; per-agent content embeddings (O(32) basis); read counts per call.
  - *Kill:* the predicted fast share is off by more than ×2 in most agents.
  - *Impostors:* topic changes inside a goal look like fast variance. Remove the room and goal field per hour first.
  - *Models:* 11, 16 (proposed Langevin) · *Builds on:* H130, H97, H46, H73
- **HH383 · DeGroot at the read-out call: the content step is a weighted mean of what was read, with the self-weight set by the context share.** A linear vector-spin update: new content = w_self × own recent content + Σ w_j × read message j. Here w_self is the agent's own share of its context, and the w_j fall with the batch size (H18 dilution).
  - *Prediction:* the fitted w_self rises with own-context share (slope near 1). The summed read weight per call scales as k^0.34 in the batch size k (H18/HH345), not as k.
  - *Check:* content embeddings per call; DQ1 context ledger for the read messages and the context share.
  - *Kill:* w_self is unrelated to the context share, or the read weight grows linearly in k.
  - *Impostors:* simultaneous convergence (H57) makes read and written content similar without any copying. Use the in-flight placebo: messages posted but not yet read.
  - *Models:* 11, 02, 04 · *Builds on:* H48, H18, H113, H44, H57
- **HH384 · Content moves on an easy plane: fluctuations across it are fast white noise, fluctuations along it are slow.** If the goal and room axes define a low-dimensional easy plane, a vector spin with anisotropy relaxes slowly along the plane and fast across it.
  - *Prediction:* the autocorrelation time of content projected on the goal+room plane is ≥ 10 times the time across it. Read kicks across the plane decay within one call.
  - *Check:* per-period goal and room axes (H54, H100); content embeddings per call; autocorrelation by projection.
  - *Kill:* the two autocorrelation times are within ×3.
  - *Impostors:* a plane defined from the same data overfits slow directions. Define the axes from kickoff and room texts only, not from agent content.
  - *Models:* 11, 16 (proposed Langevin) · *Builds on:* H108, H97, H130, H100
- **HH385 · The content response to aligned reads saturates: a Langevin-function torque, not a linear one.** A vector spin driven by a field of strength h aligns as L(h), the Langevin function, which saturates. If each aligned read adds to h, the content step toward a direction saturates with the number of aligned reads in one call.
  - *Prediction:* the content step toward direction u rises with the number of reads aligned with u and flattens by about 3 aligned reads. The curve fits L(c·n) better than a line, by held-out likelihood.
  - *Check:* content embeddings per call; read sets per call (DQ1 ledger); the alignment of each read to u.
  - *Kill:* the step is linear in n up to the largest n observed, or a line fits as well on held-out data.
  - *Impostors:* calls with many aligned reads come from hot topics (a field). Compare within-hour, across calls with different numbers of aligned reads.
  - *Models:* 11 · *Builds on:* H18, H48, H113, HH345

*Suggested first picks.*
- HH378: the hop rates come from H94's occupancies with no fit.
- HH379: one partition contrast decides between the read clock and the wall clock.
- HH382: a variance split predicted from H130 without a new fit.
- HH376: the Potts version of the strongest result, the named read-out coupling.
