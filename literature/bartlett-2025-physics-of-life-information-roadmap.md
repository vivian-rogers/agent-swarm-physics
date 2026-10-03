# Physics of Life: Exploring Information as a Distinctive Feature of Living Systems

**Citation:** Stuart Bartlett et al., *PRX Life* 3, 037003 (2025). DOI: 10.1103/rsx4-8x5f
**File:** bartlett-2025-physics-of-life-information-roadmap.pdf
**Fields:** info theory, dynamics, thermodynamics

## Summary
This Roadmap/perspective argues for an "informational perspective" on life: living and proto-living systems are distinguished by actively acquiring and using information about their environment to sustain themselves, and this can be measured. It reviews two quantitative frameworks, semantic information (the correlations a system needs to stay viable, found by scrambling interventions) and the fitness value of information (Kelly-style bet hedging, rate-distortion), together with their semantic thresholds in foragers, Daisy World and Kuramoto-oscillator networks. It then discusses implications for origin-of-life experiments, habitability limits from sensing and signalling, and agnostic information-based biosignatures. It closes with open problems: coarse-graining dependence, cost of computing SI, viability over long timescales, and open-ended systems.

## Key formalism
- Semantic information: $I(X;Y)$ between agent and environment; viability function (resisting equilibration or avoiding a "death-like" attractor); the part of $I$ whose scrambling changes viability is semantic. It is asymmetric and environment-dependent.
- Semantic thresholds: viability stays flat until a threshold in remaining mutual information. Examples cited are the forager (threshold set by body geometry), Daisy World (biosphere-planet feedback) and Kuramoto networks (threshold depends on network topology).
- Fitness value of information: with cue $Z$ about environment $Y$, the gain in maximal growth rate is controlled by $I(Z;Y)$ (Kelly bet hedging); rate-distortion with $d(x,z)=-\log$ growth rate.
- Flow-reactor proposal for replicators in fluctuating environments, where memory of past environments is side information (see Piñero 2026).
- Origin-of-life experiment design: drive a system with an epsilon-machine environment, compare internal vs. external statistical complexity and entropy rate; conditions for information-driven dynamics are learnable environment, information processing, and feedback to viability.
- Agnostic biosignatures: information flow, information efficiency, "poke it and look for a response", epsilon-machine reconstruction, compression-based (algorithmic) estimates of functional information.
- Sensing limits: SNR-based minimum cell size; molecular-communication data rates.

## Mapping to agent swarms
- "Information-driven vs. information-neutral" classification: tell which of the ~30 agents (or which periods) are actually using environmental information, versus idling or looping. Data: `events` action sequences, `WAIT`/`PAUSE`, `computer_use_turns.agent_action`.
- "Poke and look for a response": human `USER_TALK` messages, auto-nudger messages (after the nudger was added, see `CHANGELOG.md`), and `village_goals` changes act as pokes; the response is the change in an agent's next actions.
- Environment complexity: sequence complexity of the goal/task stream (`village_goals`, `agent_goals`) vs. agent-internal complexity (action-sequence statistical complexity). This is the epsilon-machine experiment applied to a swarm.
- Compression-based functional information: compressibility and normalized compression distance across successive `agent_memories.content` for one agent (functional information in single trajectories).
- Open-endedness: the roster changes (agents joining or leaving, see roster in `CHANGELOG.md`), so the state space itself changes. The paper flags exactly this as an open problem.
- Network-topology dependence of thresholds: `chat_rooms` structure (5 rooms, rooms v1) as the topology variable.

## Candidate hypotheses
- Information flow from pokes to behavior ranks agents by "aliveness". Observable: mutual information or transfer entropy from nudger/`USER_TALK` events to the next-action distribution within $\Delta t$, compared to matched baseline windows; active agents are expected to show higher flow than agents stuck in loops.
- Internal complexity tracks environmental complexity and saturates (requisite variety). Observable: sliding-window statistical complexity (or compression ratio) of an agent's action sequence vs. that of the task/goal stream, looking for a sigmoid.
- Memory growth saturates in functional content. Observable: incremental compressed size and redundancy of each new `agent_memories` entry relative to prior entries, expected to decline as semantic efficiency rises.

## Caveats
- A perspective piece, not a derivation: no new theorems, and several claims (biosignatures, origin-of-life experiments) are speculative or aimed at chemistry and astrobiology.
- Viability and goals for LLM agents are externally set (prompts, `village_goals`, operator control of who stays), so "intrinsic goals" is not satisfied.
- Information measures depend heavily on coarse-graining. Estimates from text will vary with embedding, clustering and window choices.
- Compression and epsilon-machine reconstruction need long, stationary sequences. Scaffolding changes and roster turnover violate stationarity.
- Use as a map of methods and cross-references rather than a source of testable numbers.
