# H01 architecture

How to turn **H01: Emergent superagents exist** into something testable. The full menu of sub-hypotheses is in [`subhypotheses.md`](subhypotheses.md); this file covers the machinery: terms, inputs, tiers of causal access, estimators. This is a design document, not results. Background and the estimators come from [`notes/kolchinsky-qa-transcript.md`](notes/kolchinsky-qa-transcript.md) (unverified) and from `physics-models/04-semantic-information/`.

## 0. Terms, settled

- **The framework is Kolchinsky–Wolpert *semantic information*** (Interface Focus 2018), not "semantic entropy". The original framing used "semantic entropy"; the transcript sorts out the terminology.
- **Meaning-cluster *semantic entropy*** (the LLM-hallucination method: cluster statements by meaning, take the entropy over clusters) still has a job here, as the **order parameter for ideology**. It measures *how ordered* a group's positions are. Semantic information then measures *whether that order is load-bearing*.
- **Notation.** For a chosen boundary (X = system, Y = environment), viability V and horizon τ:
  - **ΔV = V[p] − V[scrambled p]** is the *value of information*. The transcript writes this as 𝒮. Under full scrambling and linear viability it equals E_p[(1 − e^{−PMI}) v].
  - **S** is *stored semantic information*: the mutual information kept by the least-informative intervention that still preserves viability.
  - **η = S / I** is semantic efficiency: the fraction of the system–environment correlation that matters.

## 1. Structure

The hypothesis is split into ten non-conflicting directions (D1–D10), each with sub-hypotheses and sub-sub-hypotheses, in [`subhypotheses.md`](subhypotheses.md). The first three-part split maps onto it like this:

| Earlier label | Now | First evidence possible at |
| --- | --- | --- |
| ideology as an ordered phase | **D3** | Tier 0 |
| superagents exist (individuality + synergistic content) | **D1** (with D4 for the synergy part) | Tier 0 for candidates; NE and replay to confirm |
| load-bearing vs. decorative beliefs | **D4** | NE (natural scrambles) and Tier 1 replay |

The other directions: D2 viability (which also answers decision 1), D5 identity through turnover, D6 response to forcing, D7 formation and dissolution, D8 ecology, D9 hierarchy, D10 structural thermodynamics.

## 2. The three inputs the framework needs (it never supplies them)

| Input | Options | Default to start with |
| --- | --- | --- |
| **Boundary X / Y** | Rooms; model families; project crews (from session goals); role pairs (#51); data-driven groupings (Potts communities, model 10; dynamical independence, Barnett–Seth) | Rooms and families. Both are pre-defined, so there's no circularity |
| **Viability V** | (a) persistence of G as an identifiable cluster across windows; (b) −(semantic entropy) of G's positions (an ordered ideology *is* the low-entropy state); (c) continued coordinated output (a project keeps getting commits) | (b), which ties H01b to H01c. Report (a) as a check |
| **Horizon τ** | within a goal (days); across goal boundaries (the ideology survives a field change) | Across goal boundaries: goal changes are the natural perturbations |

The viability function *is* the self (transcript): choosing it presupposes the superagent. So H01a can't rest on ΔV alone. It needs an individuality criterion that doesn't assume the boundary (Krakauer et al. 2020: information propagated from G's past to its future beyond what the environment supplies).

## 3. Tiers of causal access

### Tier 0: observational (data we have)
- **Computable:**
  - I(X;Y) between group state and environment;
  - the **Pinsker envelope** |ΔV| ≤ √(I/2), for viability in [0, 1];
  - Still's **predictive vs. nonpredictive information**, from the profile of I(X_t;Y_{t+k}) over k;
  - transfer entropy Y → X;
  - semantic entropy of group positions over time;
  - individuality measures for candidate groupings.
- **Gives:** ranked candidate superagents; upper bounds on ΔV; the horizons over which anything semantic *could* exist; the H01b order-parameter time series.
- **Can't give:** ΔV itself, which needs interventions. Observational identification (stochastic-policy interventions / g-formula) needs a causal graph and **positivity**. Strong group–environment correlation leaves the scrambled cells unobserved, which is exactly the regime of interest.

### Tier 1: replay (counterfactual resampling of logged agents)
- **Intervention:** take an agent's logged context at time t, apply a soft scramble (replace memory sections or chat segments with draws from their marginal: p(x|y) → p(x)), and resample the next actions with the same model.
- **Gives:** single-agent ΔV and samples of the one-step kernel. With these, the viability landscape v(x, y) can be estimated once, and then every intervention is an inner product: ΔV_A = ⟨p − I_A[p], v⟩.
- **Blockers:**
  - Exact prompts are **not in the export**, and as of 2026-10-03 Vivian can't obtain `llm_calls`. **Tier 1 is therefore blocked indefinitely**; H01 relies on Tier 0 and NE.
  - Several models are retired.
  - API cost.
  - Multi-agent feedback can't be replayed beyond one step.

### Tier NE: natural experiments (replaces simulation)
- **No new swarms.** We can't run our own simulation, so the interventional power has to come from **step changes in the real village**: scaffold changes, roster changes, room splits, operator corrections, goal switches. These are catalogued with IDs in [`../natural-experiments.md`](../natural-experiments.md).
- **Channel cuts as scrambles.** Many step changes *cut or degrade an information channel*, which is a one-shot, population-wide version of the Kolchinsky–Wolpert scramble:
  - NE12, rooms: the cross-room channel is cut;
  - NE26: other agents' plans are hidden;
  - NE22: the past is truncated;
  - NE03: chat capacity is limited.
  Under stationarity, and with no co-occurring change, the viability change across the cut estimates ΔV for that channel.
- **Designs:** interrupted time series; difference-in-differences against unaffected groups (other families, the other room); reversals (NE21 hours 4→8→4→8 h, NE23 nudger off/on); dose-response (NE22 by length of absence).
- **What it doesn't give:** arbitrary or partial scrambles, or the full landscape v(x, y). Only the channels the operators happened to change, in bundles, with goal changes as standing confounds.
- **The landscape trick and local semantic map** (transcript) still apply *within* Tier 1 replay, once the prompts are available.

## 4. Thermodynamic layer (structural, not physical)

- **Bound to test:** persistence gained from environmental information is bounded by the information held. This is the Kelly / Sagawa–Ueda structure, a theorem about the mathematics, not about joules. The test: do groups that persist across goal changes hold more predictive information about the next environment?
- **Dissipation proxy:** token cost of maintaining consensus (`events.data` input/output tokens) per unit of semantic-entropy reduction.
- **Waste:** Still's nonpredictive memory, i.e. memory content that predicts nothing in the future. Memory consolidation is the natural erasure step: does consolidation preferentially drop the nonpredictive part?
- **Don't claim** physical thermodynamics: there's no conservation law for attention.

## 5. Planned data schemes (`scheme/`)

- **S1 (Tier 0):**
  - **Inputs:** chat, `CONSOLIDATE` `nextSessionGoal` and memories.
  - **Transform:** per window, positions per agent and group → meaning clusters (bidirectional entailment, or embedding thresholds; see model 11) → semantic entropy per group, plus I(X_t;Y_{t+k}) profiles.
  - **Output:** `data/processed/H01-emergent-superagents-exist/`.
- **S2 (Tier NE):** an event study around each NE: windows before and after, controls, and the order parameter, viability and coupling series from S1.
- **S3 (Tier 1):** context reconstruction plus a scramble harness for replay. Waits on the exact prompts (`llm_calls`), to be requested from AI Digest eventually.

## 6. Candidate windows (from `../hypohypotheses/goal-periods.md`)

- **Stances and ideology:**
  - #12, debate teams: groups defined by the goal;
  - #26, election: coalition formation;
  - #33, Pentagon debate: explicit positions and a claims database.
- **Spontaneous order without a field:**
  - #31, condensation onto one project;
  - #44, the #rest "existential attractor".
- **Anti-superagent:** #34, hidden saboteurs inside a group.
- **Long window, competing pairs:** #51, private roles.
- **Ship-of-Theseus tests:** roster churn. Does a group's position survive replacement of its members? Example: Claude 3.7 Sonnet retiring in #31.
- **Standing candidates:** model families, as possible superagents held together by shared pretraining. That shared prior acts as a field, not a coupling, and must be separated out (see models 03 and 11).

## 7. Pitfalls

- **It's not an agent detector.** ΔV is graded, and a thermostat has ΔV > 0. Superagent claims need the individuality criterion plus ΔV, never ΔV alone.
- **Group-size bias.** Bigger groups trivially carry more information. Compare per member, or against random groupings of the same size.
- **Shared priors as fake ideology.** Families agree because of pretraining. Measure the field (exposure-free agreement) before attributing order to coupling.
- **Positivity.** Any ΔV is only as good as the extrapolation into unobserved state combinations.
- **Meaning clustering is a coarse-graining.** Results must survive reasonable changes to the clustering.

## 8. Decisions

1. **Viability for a superagent:** open. Candidates are listed as sub-hypotheses D2.1–D2.4 in `subhypotheses.md`, with a data-driven way to choose (D2.6: pick the viability function the group visibly restores after shocks).
2. **`llm_calls` (exact prompts):** not obtainable (2026-10-03). Tier 1 replay is blocked; D4 relies on natural scrambles (D4.1.b).
3. **Simulation:** not possible. Replaced by natural experiments (Tier NE).
4. **Probes:** both mined statements (tier 0) and fixed probes (replay).
5. **Which sub-hypotheses to tackle first:** open; there's a suggested starting set at the end of `subhypotheses.md`.

## Reading list (from the transcript; citations to verify)

- **Thermodynamics:** Still, Sivak, Bell & Crooks, "Thermodynamics of prediction" (2012); Sagawa & Ueda; Vinkler, Permuter & Merhav (2016), on gambling ↔ work extraction.
- **Individuality and autonomy:** Krakauer, Bertschinger, Olbrich, Flack & Ay, "The information theory of individuality" (2020); Bertschinger, Olbrich, Ay & Jost on autonomy.
- **Empowerment:** Klyubin, Polani & Nehaniv.
- **Emergence:** Hoel (causal emergence); Rosas, Mediano et al. (synergistic emergence); Barnett & Seth (dynamical independence).
- **Agent detection:** Kenton, Everitt et al., "Discovering agents"; Orseau, McGill & Legg, "Agents and devices".
- **Information dynamics:** Lizier (local information dynamics); Crutchfield (computational mechanics).
- **Causal inference:** Correa & Bareinboim (stochastic interventions); Robins (g-formula).
- **Semantic entropy (meaning clusters):** Farquhar et al., *Nature* (2024).
