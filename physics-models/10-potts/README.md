# 10 · Potts models (categorical states)

**Fields:** stat mech, sociophysics, info theory
**References:** Wu, "The Potts model", *Rev. Mod. Phys.* 54, 235 (1982)†; Weigt et al., "Identification of direct residue contacts in protein–protein interaction by message passing", *PNAS* 106, 67 (2009)†; Morcos et al., "Direct-coupling analysis of residue coevolution", *PNAS* 108, E1293 (2011)†; Ekeberg et al., "Improved contact prediction in proteins: using pseudolikelihoods to infer Potts models", *PRE* 87, 012707 (2013)†; Reichardt & Bornholdt, "Statistical mechanics of community detection", *PRE* 74, 016110 (2006)†; Castellano, Fortunato & Loreto, "Statistical physics of social dynamics", *Rev. Mod. Phys.* 81, 591 (2009)†.

## The model

Each agent i has a categorical state σ_i ∈ {1, …, q} instead of a binary spin:

$$P(\boldsymbol\sigma) = \frac{1}{Z}\exp\Big(\sum_i h_i(\sigma_i) + \sum_{i<j} J_{ij}(\sigma_i, \sigma_j)\Big)$$

- **Standard Potts:** J_ij(a, b) = J_ij δ_ab. Agents gain from being in the *same* state (J > 0, ferromagnetic) or from being in *different* states (J < 0, antiferromagnetic). Every state is treated alike.
- **Generalized Potts:** each pair has a full q × q coupling matrix J_ij(a, b). This is the maximum-entropy model that reproduces all one- and two-point categorical marginals. It is the model behind direct-coupling analysis (DCA) of protein sequences.
- **Special cases:** q = 2 is Ising (model 01). The clock model puts the q states on a circle, and in the q → ∞ limit becomes the XY model (model 11).
- **Dynamics:** a kinetic Potts model has each agent's next state drawn from a softmax over the q states, conditioned on the others' current states. That is a multinomial logistic regression per agent, and it is the categorical version of model 02.

## Interesting behavior

- **Discontinuous consensus.** Ising ordering is continuous. The mean-field ferromagnetic Potts transition is *first-order* for q ≥ 3 (on 2D lattices, for q > 4). The result is coexistence, hysteresis and metastable states, with sudden jumps to one dominant state rather than gradual drift.
- **Symmetric ties.** With equal fields, the q states are interchangeable, and ordering means spontaneously picking one. A three-way tie in a vote is the system sitting at its permutation-symmetric point.
- **Antiferromagnetic Potts is graph coloring.** At zero temperature, "neighbors must differ" is exactly the graph-coloring problem. That makes it a natural model of **division of labor**: agents who interact take different tasks. Frustration appears when the interaction graph can't be colored with q colors.
- **Communities as ground states.** Modularity-based community detection is the ground state of a Potts Hamiltonian on the interaction graph (Reichardt & Bornholdt). Rooms, teams and factions can be read as Potts domains.
- **Social-dynamics relatives.** The voter model, the naming game and the Axelrod culture model (several Potts variables per agent) are all Potts-like coarsening dynamics. They come with known consensus-time scalings.

## Mapping to the village

The state can be any categorical label per agent per time window:

| σ_i | q | Source |
| --- | --- | --- |
| project or topic cluster | 5–30 | session goals, `CONSOLIDATE` `nextSessionGoal`, chat content |
| chat room | ≤ 5 at once | room membership (from `ENTER_ROOM`) |
| action class | ~8–17 | `events.data.actionType`, `computer_use_turns` action |
| vote or endorsement | candidates | chat, during the election (goal #26) and saboteur votes (#34) |
| team or role | 2–25 | debate teams (#12), RPG saboteur/villager (#34), private roles (#51) |

Fields h_i(a) carry agent-specific preferences, e.g. a model family's prior for a topic. Common drive (the goal prompt) shows up as a field shared by all agents. See "Agent state (categorical)" in `../DEFINITIONS.md`.

## How to fit

1. Define the label and q; check that the labels mean the same thing across the window. Topic clusters drift, so fit within a regime.
2. **Pseudolikelihood (plmDCA style):** one softmax regression per agent, with L2 regularization. There are q²N²/2 coupling parameters, so regularization is mandatory.
3. **Gauge:** J_ij(a, b) is only defined up to shifts; fix a zero-sum gauge before interpreting it. The Frobenius norm of each J_ij block, with average-product correction, gives one coupling strength per pair.
4. For dynamics, fit the kinetic version and compare its antisymmetric part with models 02 and 09.

## Nulls and controls

- **Label permutation** within each agent's time series: keeps marginals, destroys co-occurrence.
- **Circular shift** per agent, as in model 01.
- **Independent model** (fields only): the Potts couplings must beat it on held-out likelihood.

## Mean-field forward version

Uniform-coupling q-state Potts in mean field. The order parameter is the dominant option's share x, which solves a self-consistency equation. For q ≥ 3 the transition is **first-order**, at a critical coupling of order βJ_c = 2(q−1) ln(q−1)/(q−2) for the standard J/N normalization (check the normalization before use). Below it the symmetric (disordered) solution is stable; above it a jump to consensus. Fit βJ from the dominant share and its fluctuations, then predict the jump size and the hysteresis width. Forward-testable on consensus events without inferring q²N² couplings. HH84.

## Pitfalls

- Clustering choices define q and the labels. Results must be stable across reasonable clusterings.
- Rare states make J poorly determined. Merge rare states into "other".
- The equilibrium Potts model has symmetric couplings only; directed influence needs the kinetic version.

## Hypothesis seeds

- In collaborative weeks agents spread across subtasks (antiferromagnetic couplings, division of labor). In free weeks they herd onto the same project (ferromagnetic condensation; see goal #31).
- Consensus on a shared choice (the puzzle-game concept in #19, interface standards in #40) arrives as a discontinuous jump, not a gradual drift. That is the first-order Potts signature.
- Room choice is a Potts variable with family-dependent fields: agents of one family cluster in rooms beyond what operator assignment explains.
