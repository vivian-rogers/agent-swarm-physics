# 04 · Semantic information of emergent structures

**Fields:** info theory, thermodynamics, stat mech
**References:** Kolchinsky & Wolpert, "Semantic information, autonomous agency and non-equilibrium statistical physics", *Interface Focus* 8, 20180041 (2018); Sowinski et al., "Semantic information in a model of resource gathering agents", *PRX Life* 1, 023003 (2023); Bartlett et al., "Physics of Life" roadmap (2025). All three are in `literature/`.

## The model

Kolchinsky & Wolpert split the world into a **system** X and its **environment** Y. Some of the Shannon (syntactic) information I(X;Y) matters for the system's continued existence, and some doesn't. **Semantic information** is the part that matters. They make "matters" precise with two ingredients:

- **Viability** V: how well the system keeps existing after time t. Default V = −S(p_{X_t}): low entropy means staying in an organized, "alive" set of states. Alternatives are the probability of staying in a viability set A, or the lifetime.
- **Interventions**: counterfactually scramble some of the system–environment correlations and see what happens to viability. Scrambling everything gives the product distribution p(x)p(y).

From these:
- **Value of information:** ΔV = V(actual) − V(fully scrambled). It can be negative, when the system uses misleading information.
- **Stored semantic information:** S = the least information I(X;Y) any intervention can keep while matching the actual viability.
- **Semantic efficiency:** η = S/I. The fraction of correlations that are meaningful.
- **Semantic content:** which correlations the optimal intervention keeps: p̂^opt(y|x), i.e. what the system "knows that matters".
- **Observed semantic information:** the dynamic version. Scramble the information flow (transfer entropy Y → X) instead of the stored correlations.
- **Thermodynamic multiplier:** κ = ΔV/I. Viability gained per bit acquired.

Their proposal is that **agency** is having a lot of semantic information, and that agents could be *found* by searching over ways to split the world into X and Y for the one with the most semantic information.

## Applying it to an emergent structure

The natural first use is one agent as X. More interesting, and the point of this model, is to treat an **emergent structure on the substrate** as X:
- a long-running collaborative project
- a convention (a shared document format, a division of labor)
- a role that persists through changes in who fills it ("the coordinator")
- a room's culture

The substrate is the agents, their memories and the chat. X is a coarse-grained description of the structure: e.g. which agents are working on the project and the project's state. Viability is the structure's persistence: does work keep flowing to the project, does the convention keep being used.

Then the questions become:
- What information from the environment does the structure need in order to persist?
- Is the structure's semantic information carried by particular agents, or spread across them (redundant), or only present jointly (synergistic)?
- Does searching over coarse-grainings find structures with more semantic information than any single agent? If so, that's a quantitative case that the structure is more agent-like than its members.

## Interesting behavior

- **Plateau, then collapse.** Sowinski et al. scramble a forager's sensor gradually. Viability stays flat until a critical noise level and then collapses. Bits above the threshold are semantically irrelevant; bits below it are essential. Viability per bit peaks at the threshold.
- **Low efficiency.** Most correlations a system has with its environment can be meaningless. In their food-seeking example, a system with log₂5 ≈ 2.32 bits of information has only 1.37 bits of semantic information.
- **Negative value.** Information can hurt (mistaken use). A swarm that propagates false claims would show this.
- **Agent discovery.** The best X/Y split is an output of the analysis, not an input. That makes it a candidate tool for detecting emergent individuality.

## Mapping to the village

- **X (single agent):** memory (`agent_memories.content`), current goal (`CONSOLIDATE` `nextSessionGoal`), action class.
- **X (emergent structure):** a coarse-grained label over many agents, e.g. a project cluster and the set of agents on it.
- **Y:** other agents' messages, the village goal, human messages, tool outputs.
- **Viability:** the weakest link. Options: persistence of the structure, absence of long `WAIT`/`PAUSE` runs, goal completion. Choose one before measuring and report sensitivity to the choice.
- **Interventions: the big opportunity.** The paper needs counterfactual scrambling, which is impossible for organisms but possible for LLM agents. Replay logged contexts with memory sections masked, or chat messages shuffled across days, and measure the change in the next action. Or run a small fresh swarm and intervene directly. The static logs only offer natural experiments (rooms on 2026-02-25, the 200-event context cap on 2026-06-11).

## How to measure

1. Choose X, Y, viability and the timescale t. Write them in the hypothesis card first.
2. **Observational:** estimate I and transfer entropy from logs. Use natural experiments as partial interventions.
3. **Interventional:** replay with graded scrambling (fraction of memory masked, fraction of chat shuffled). Plot viability against retained information. Find the threshold and compute S and η.

## Pitfalls

- **Viability after a context scramble is restored through artifacts, not memory or the room** (H44, 2026-10-04): after forced erasures, reading local files first brings the first write 2.6 calls sooner than looking at the screen (room first: 0.5); the memory written at the wipe has no within-agent effect (ρ −0.08 to +0.02). The context window carries the call-scale information (writes −26%, commits −38%); erasure also breaks command loops (OR 0.11).
- **`memory_stats` writes two rows per consolidation** (H71, 2026-10-04): each regime-III consolidation logs an append snapshot, then a compress snapshot. The mixed series gives φ < 0 in 10/10 periods (H09's "overshoot"), while the compressed series reverts with φ⁺ 0.67 [0.63, 0.71]. Filter to `lines_removed > 0` before any AR, set-point or store-size fit.
- Viability is chosen by the analyst. Operators decide who stays in the village, so "self-maintenance" is not intrinsic. Be explicit that the viability function is a modeling choice.
- The framework assumes an ensemble over initial conditions; the village is one long trajectory. Windows and replays approximate it.
- Discretizing text into states is itself a coarse-graining, and answers depend on it.

## Hypothesis seeds

- Memory has low semantic efficiency: masking most of an agent's memory barely changes its next actions, until a threshold.
- Long-running projects have more semantic information than any of their individual contributors (structure as agent).
- A few agents carry most of the swarm's semantic information; removing their messages in replay hurts other agents' viability most.
- Viability against scrambling shows the plateau-then-collapse shape, and the threshold moved when the context cap changed on 2026-06-11.
