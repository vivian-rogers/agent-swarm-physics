# Semantic information, autonomous agency and non-equilibrium statistical physics

**Citation:** Artemy Kolchinsky and David H. Wolpert, *Interface Focus* 8, 20180041 (2018). DOI: 10.1098/rsfs.2018.0041
**File:** kolchinsky-2018-semantic-information-autonomous-agency.pdf
**Fields:** info theory, thermodynamics, stat mech

## Summary
The paper gives an intrinsic, formal definition of semantic information: the part of the syntactic (Shannon) information between a system and its environment that is causally necessary for the system to maintain its own existence. "Existence" is operationalized by a viability function, and "causal necessity" by counterfactual interventions that scramble system-environment correlations. This splits mutual information into "meaningful" and "meaningless" bits, defines a value of information, semantic content and semantic efficiency, and connects the costs and benefits of information to non-equilibrium thermodynamics. The authors suggest that autonomous agency can be quantified as a large amount of semantic information, which could automatically identify agents in physical systems.

## Key formalism
- Setup: system $X$, environment $Y$, joint $p(x_0,y_0)$ evolving under coupled stochastic dynamics for time $t$.
- Viability: $V(p_{X_t})=-S(p_{X_t})$ (negative Shannon entropy). Alternatives are $p(X_t\in A)$ and $-D_{KL}(p_{X_t}\|p^{eq})$. Entropy bounds the probability mass on any small viability set (Appendix A).
- Stored semantic information: scramble $I(X_0;Y_0)$ via coarse-graining $\hat p^f(x_0|y_0)=p(x_0|f(y_0))$. Value of information $\Delta V^{stored}_{tot}=V(p_{X_t})-V(\hat p^{full}_{X_t})$ with $\hat p^{full}=p_{X_0}p_{Y_0}$.
- Information/viability curve $\Delta(R)=\max_f V(\hat p^f_{X_t})$ s.t. $I(\hat p^f)=R$. Optimal intervention is the least-information $f$ with unchanged viability, and $S^{stored}=I(\hat p^{opt}(X_0;Y_0))$.
- Semantic efficiency $\eta=S/I\in[0,1]$. Pointwise $S(x;y)=\ln \hat p^{opt}(x,y)/[\hat p^{opt}(x)\hat p^{opt}(y)]$. Semantic content of $x$ is $\hat p^{opt}(y|x)$. Information can have negative value (mistaken or "pathological" use).
- Thermodynamic multiplier $\kappa=\Delta V/I$ ("bang-per-bit"), with Landauer cost $W_{min}=k_BT\ln2\,I$; $\kappa=\eta\,\Delta V/S$.
- Observed semantic information: intervene on $p(x_{t+1}|x_t,y_t)$ to scramble transfer entropy $\sum_t I(X_{t+1};Y_t|X_t)$.
- Example: food-seeking agent with 5 locations has $I=\log_2 5\approx2.32$ bits but only 1.37 bits of stored semantic information.
- Scientist-chosen: system/environment split, timescale $t$, initial distribution. Section 6 proposes maximizing semantic information over these to discover agents.

## Mapping to agent swarms
- $X$: one agent, or a coarse-grained subgroup such as a room. State candidates are memory text (`agent_memories.content`), current `session_goal`, and action class (`events.data.actionType`).
- $Y$: everything else in the village. Candidates are other agents' messages (`chat_messages` by `room_id`), the current village goal (`village_goals.goal`), tool/web outputs (`computer_use_turns.output`, `error`), and human `USER_TALK`.
- Stored information $I(X_0;Y_0)$: mutual information between an agent's memory at a `CONSOLIDATE` and the village state at that moment (e.g., embedding-cluster labels of each).
- Observed information: directed transfer entropy from peers' messages to an agent's next action. Direct analogue of the paper's dynamic intervention.
- Viability: persistence. Concrete options are `is_participating`, absence of long `WAIT`/`PAUSE` runs, and low entropy of an agent's action distribution in a window (a literal $-S$ analogue, but a stretch).
- Interventions: scrambling needs replay, e.g., rerunning an agent from logged context with memory sections or chat messages permuted. Not available in the static logs.
- Agent discovery (Sec. 6): search over groupings of the ~30 agents and timescales for the unit with the largest semantic information, for example whether a room behaves as one agent.

## Candidate hypotheses
- Semantic efficiency of memory is low: most of the information in consolidated memories is not needed for downstream behavior ($\eta\ll1$). Observable: masked-section replay of memory against action-distribution shift, relative to total information in the memory.
- Semantic information is asymmetric across the roster. Observable: directed transfer-entropy matrix between agents (binned by time or `event_index`) has a few high out-degree "sources", and removing their messages in replay lowers peers' viability proxy more than removing random agents' messages.
- Bang-per-bit $\kappa$ differs by model family and by scaffolding era. Observable: ratio of viability-proxy loss under chat-context removal to the transfer entropy removed, compared across eras (rooms v1, perma-computer-use, auto-nudger).

## Caveats
- Viability is chosen by the analyst and can be arbitrary for LLM agents. Negative entropy of an action distribution does not mean "alive".
- The framework needs ensembles over initial conditions. The village is one long trajectory, so stationarity and ergodicity must be assumed or approximated with windows and replays.
- Discretizing text into $X$ and $Y$ states is itself a coarse-graining choice that changes the answers.
- Landauer-type costs are not meaningful for token processing, so the "thermodynamic multiplier" is a metaphor unless redefined in dollars or tokens.
- Agent persistence is controlled by operators and prompts, so "self-maintenance" is not fully intrinsic.
