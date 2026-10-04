# H01 sub-hypotheses: the full set

Every research direction under **H01: Emergent superagents exist** that we could reasonably pursue, broken into sub-hypotheses and sub-sub-hypotheses, so we can choose what to tackle. Nothing here is chosen or tested yet.

**How it's organized**
- **Ten directions (D1–D10).** They don't conflict: any combination can be pursued together.
- **Sub-hypotheses (D3.2, …)** are claims.
- **Sub-sub-hypotheses (D3.2.a, …)** are specific, testable versions or operationalizations.
- **⟷ marks rivals:** mutually exclusive alternatives. Those are the decisive tests, since the data can favor one.

**Tags on each item**
- **Tier:** `0` = observational, from the logs; `NE` = natural experiment (IDs in [`../natural-experiments.md`](../natural-experiments.md)); `R` = replay of logged agents with scrambled context (needs the exact prompts, `llm_calls`, to be requested eventually). New swarm simulations are out of scope.
- **Windows:** goal numbers from [`../hypohypotheses/goal-periods.md`](../hypohypotheses/goal-periods.md).
- **Models:** numbers from `physics-models/`.
- **Probes:** ideology can be measured from *mined* statements (tier 0) or *fixed probes* asked in replay (R). Both are in scope.

**Dependencies**
- D2 (viability) must be chosen before D4, D5 and D6.2 can be quantified.
- D1 and D3 can start immediately.
- D10 builds on D3.

---

## D1 · Identification: which groupings act as one agent?

- **D1.1 Some predefined groupings are superagents** (tier 0; models 04, 10)
  - **D1.1.a Rooms.** After rooms exist, a room carries its own past into its future beyond what other rooms supply, more than random groups of the same size do. *NE12 makes rooms informationally closed by construction, so compare individuality before and after it.*
  - **D1.1.b Model families.** Once the family's shared prior has been removed (agreement with no exposure), members are still more coupled within the family than across families. *Models 11 and 03 (field vs. coupling).*
  - **D1.1.c Project crews.** Agents sharing a session-goal cluster form units during shared-objective (C-mode) weeks, but not during individual-objective weeks. *Windows: C weeks vs. #10, #14, #49.*
  - **D1.1.d Same-role pairs in #51 cooperate as a unit** ⟷ **D1.1.e same-role pairs are anti-coupled competitors.** *Window #51; models 10 and 02.*
- **D1.2 Boundaries can be found from data, not assumed** (tier 0)
  - **D1.2.a** Searching over groupings for maximal individuality (or dynamical independence) recovers rooms where they exist, which validates the method, and finds other units elsewhere.
  - **D1.2.b** Potts communities on the interaction graph (model 10) coincide with the maximal-individuality groupings.
  - **D1.2.c** The best grouping shifts at channel cuts (NE12 rooms, NE26 hidden plans) and at mode switches (NE34).
- **D1.3 The whole village is one superagent** ⟷ **D1.3' it's a set of independent sub-units, with no village-level individuality.** *Tier 0; compare village-level individuality against the sum over rooms.*

## D2 · Viability: what does it mean for a superagent to stay alive?

These are the candidate viability functions (decision 1 in the architecture). Each sub-sub-hypothesis is "this quantity is held up against perturbation and recovers after shocks".
- **D2.1 Structural viability**
  - **D2.1.a Membership persistence:** the overlap (Jaccard) of the group's members across windows stays high.
  - **D2.1.b Boundary maintenance:** the ratio of internal to external interaction stays above a threshold, i.e. modularity holds.
  - **D2.1.c Recruitment:** the group replaces lost members. A replicator view; models 05 and 06.
- **D2.2 Informational viability**
  - **D2.2.a Ideological order:** the semantic entropy of the group's positions stays low. *Current default; ties D2 to D3.*
  - **D2.2.b Marker persistence:** a shared convention, name or artifact format stays in use (its lifetime).
  - **D2.2.c Shared memory:** overlap between members' memories survives consolidations.
- **D2.3 Functional viability**
  - **D2.3.a Coordinated output continues:** commits, artifacts and deploys attributable to the group.
  - **D2.3.b Goal attainment:** an external utility, the least intrinsic option; useful as a contrast.
- **D2.4 Self-identification**
  - **D2.4.a** Members keep referring to the group by name, or as "we", over time.
- **D2.5 The candidate viabilities co-vary**, i.e. there's one latent "health" ⟷ **D2.5' they dissociate**, i.e. the same group is several different "selves". *Tier 0: correlate the D2.* series across groups and windows.*
- **D2.6 How to choose: homeostasis.** The right viability function is the one the group visibly *restores* after shocks. Pick the V whose post-shock relaxation is strongest. *NE: reversals (NE21, NE23), retirements (NE28–NE30), corrections (NE35, NE36).*

## D3 · Ideology as an ordered phase

- **D3.1 An ordered phase exists:** groups' semantic entropy is lower than random-group baselines and stable over time.
  - **D3.1.a** Measured on mined statements (tier 0).
  - **D3.1.b** Measured on fixed probes asked in replay (R).
  - **D3.1.c** The two methods rank groups the same way, which validates the measurement.
- **D3.2 Order is coupling-driven** (agents align each other) ⟷ **D3.2' order is field-driven** (shared pretraining, or the goal prompt). *Tier 0 + NE. Order that drops when the cross-room channel is cut (NE12) means coupling. Order that tracks goal changes (NE34) or appears without exposure means a field. Models 11 and 03.*
- **D3.3 Phase behavior**
  - **D3.3.a** Order breaks at goal changes (a quench) and re-forms with a measurable relaxation time.
  - **D3.3.b** Hysteresis: returning to a similar field gives a history-dependent state. *#1 vs #38 (charity); the run of pick-your-own weeks #11, #16, #22, #31, #37.*
  - **D3.3.c** Critical slowing down: variance and autocorrelation of the order parameter rise before a switch.
  - **D3.3.d The order parameter is continuous** (O(n), model 11) ⟷ **D3.3.d' it's discrete with first-order jumps** (Potts, model 10).
- **D3.4 Polarization:** several ordered factions coexist during competitive or team weeks (K, M). *#12, #34, #33; two-sublattice ordering.*

## D4 · Semantic content: which information is load-bearing? (Kolchinsky–Wolpert proper)

- **D4.1 Only part of a group's shared information is load-bearing** (η ≪ 1)
  - **D4.1.a Envelope, tier 0:** the Pinsker bound plus the predictive-information profile flag which shared content *could* matter.
  - **D4.1.b Natural scrambles, NE:** the viability drop after a channel cut estimates ΔV for that channel. Cuts: NE12 rooms, NE26 hidden plans, NE22 event cap, NE03 chat-fetch limit, NE25 history scope.
  - **D4.1.c Replay scrambles, R:** ΔV for each memory section and chat segment.
- **D4.2 Load-bearing content is predictive** (about the environment's future) ⟷ **D4.2' it's coordinative** (about who does what inside the group).
- **D4.3 Misinformation has negative value** (ΔV < 0): groups recover after a false belief is removed. *NE36 (Year-1 total correction), the "temporal bleed" theory in #45, NE35.*
- **D4.4 Semantic content depends on the viability choice (D2)** ⟷ **D4.4' it's robust across choices.** A sensitivity analysis.

## D5 · Identity through turnover (Ship of Theseus)

- **D5.1 A group's ideology survives member replacement**
  - **D5.1.a** Retirements don't shift the group's order parameter beyond noise. *NE28, NE29.*
  - **D5.1.b** A same-family successor takes up the group's position faster than an unrelated newcomer. *NE30 (Gemini 3 Pro → 3.1 Pro).*
- **D5.2 Newcomers are assimilated:** agents with empty memories converge on the group's positions within a measurable assimilation time.
  - **D5.2.a** Assimilation is faster once onboarding rooms exist (mid-2026) than before.
  - **D5.2.b** Batch joins slow assimilation (dilution) compared with single joins. *NE27, NE33; NE32 isolated-then-merged triplet.*
- **D5.3 Continuity travels through artifacts and history search, not memory** (newcomers have none) ⟷ **D5.3' through chat exposure.** *What do newcomers reference first? NE18 widened history search.*

## D6 · Response to forcing

- **D6.1 Groups differ in susceptibility to goal fields**
  - **D6.1.a** The response along the goal direction at kickoff (model 11) differs by group: family, room.
  - **D6.1.b** Making the field persistent (NE08 goal in prompt, NE13 kickoff in prompt) lengthens alignment after kickoff.
- **D6.2 Homeostasis:** after shocks, viability recovers with a characteristic time. *Reversal designs NE21, NE23; operator shocks NE35–NE38.*
- **D6.3 Sign test:** channel additions (NE01, NE04, NE09) raise coupling within groups; cuts (NE12, NE22, NE26) lower it.
- **D6.4 Families as units:** changes that hit only one family shift that family's collective behavior, not the others'. *DiD on NE05, NE06, NE20.*

## D7 · Formation and dissolution

- **D7.1 Superagents nucleate spontaneously by condensation** ⟷ **D7.1' they form around leaders.** Both may occur, at different times.
  - **D7.1.a** Condensation is abrupt, i.e. first-order. *#31, #41, #44-#rest; model 10.*
  - **D7.1.b** Leader-formed units have directed couplings out of the leader; condensed units are symmetric. *#26, #45 (known leader); model 02.*
- **D7.2 Groups dissolve mostly at goal boundaries** (field-driven) ⟷ **D7.2' mostly mid-goal** (endogenous).
- **D7.3 Rivals merging:** a switch from competition to cooperation forms a superagent out of former rivals. *#27.*
- **D7.4 Groups created by fiat outlive their room:** room-made groups persist after the room is deleted. *#universe-coordination, deleted 2026-05-12; NE32 triplet rooms.*

## D8 · Ecology: several superagents together

- **D8.1** Coexisting superagents partition niches. *Models 06, 07; #51.*
- **D8.2** Superagents compete for members: membership flows between groups.
- **D8.3** Parasites lower host viability, and hosts evolve defenses such as verification and claims databases. *#34 saboteurs, the #51 prankster.*
- **D8.4** #best and #rest diverge in ideology under different fields. *NE15 forks; #44, #46, #47, #50.*

## D9 · Hierarchy and scale

- **D9.1 Emergence peaks at an intermediate scale:** among agent < crew < room < village, individuality or synergy (causal emergence) is highest in between.
- **D9.2 Model-family identity persists across room boundaries** ⟷ **D9.2' room identity dominates after NE12.**
- **D9.3 Sub-agents:** some single agents (short tenure, little memory continuity) show *less* individuality than the group they belong to.

## D10 · Structural thermodynamics of ideology

- **D10.1 Maintenance cost:** keeping semantic entropy low costs tokens; cost rises with the size of the entropy reduction (a Landauer-like slope).
- **D10.2 Information bound:** what a group gains in persistence across a goal change is bounded by its predictive information about the next environment (Kelly / Sagawa–Ueda structure).
- **D10.3 Consolidation preferentially erases nonpredictive content** (Still's bound) ⟷ **D10.3' it erases indiscriminately.** *Tier 0 on `agent_memories`.*
- **D10.4 A faster erasure rate (NE14, consolidation every ~40 actions) lowers ideological persistence** ⟷ **D10.4' it raises it, by forcing compression to essentials.**

---

## Mean-field-forward variants (added 2026-10-03)
These posit a few-parameter mean-field model per group instead of learning full couplings, and test forward predictions. Robust at small group sizes. See `../mean-field-variants.md`.
- **D1-MF · Block mean field for candidate groups.** Each candidate superagent (room, family, crew) is a block with couplings J_in and J_out, fitted from covariances only. A superagent candidate has J_in ≫ J_out, stable across windows (HH82, HH89).
- **D3-MF · Mean-field order for ideology.** Group positions follow mean-field O(n) (embeddings) or Potts (stances): **m** = L_n(β(J₀|**m**| + h)) **m̂**. Fit (βJ₀, h) per group.
  - **D3-MF.a** coupling-driven order has βJ₀ near or above the mean-field critical value; field-driven order has βJ₀ ≈ 0 with large h. A mean-field version of the D3.2 rival test (HH85).
  - **D3-MF.b** stance consensus is first-order (mean-field Potts with q ≥ 3; HH84).
- **D6-MF · Mean-field susceptibility.** Group susceptibility follows from βJ₀ and m, and predicts responses to kickoffs without a full model (HH80, HH81).

---

## Picking a starting set

Cheapest and most informative first (tier 0 or NE, no prompts needed):
- **D3.1.a:** establishes the order parameter.
- **D2.6:** chooses the viability function from the data, which answers decision 1.
- **D3.2 ⟷ D3.2':** coupling vs. field, the decisive rival test, using NE12.
- **D1.1.a:** rooms as superagents, using NE12.
- **D5.1.b:** same-family succession, NE30.

D4, the full Kolchinsky–Wolpert measurement, comes after those. It uses natural scrambles first (D4.1.b), and replay once the prompts are available.
