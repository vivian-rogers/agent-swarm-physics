# Stat-mech primitives in the AI Village

An inventory of the standard statistical-mechanics objects and their concrete counterparts in this dataset. Field names refer to the export; processed-table names refer to the Phase 0 plan in `infra/README.md`. Primitives that prove useful get promoted into `physics-models/DEFINITIONS.md`. HH numbers point to [HYPOHYPOTHESES.md](HYPOHYPOTHESES.md).

## Microstates (fine-grained configurations)

| Level | Microstate | Source | Notes |
| --- | --- | --- | --- |
| turn | one computer-use turn: action, tool output, error | `computer_use_turns` (2.51M, ~6k per active day) | screen contents only via screenshots (later, OCR) |
| message | one chat message: text, or its embedding | `chat_messages` (183k) | the semantic microstate |
| agent | (action class, room, current intention, memory snapshot) | `events`, `intentions`, `agent_memories` | full context window unknown without the prompts |
| memory | the full memory text; lines or sections as "particles" | `agent_memories` (246k snapshots) | full rewrites at every consolidation |
| swarm | the joint tuple of all agents' states at time t | `activity_bins`, `rooms_timeline`, `intentions` | the configuration σ of the spin models |
| artifact | a repo tree or commit; a site version | `actions` (git commands), `artifacts` | lineage for model 08 |
| path | the sequence of actions that produced an artifact or ended a session | `actions`, `events` | path entropy; many paths, one outcome |

## Macrostates and order parameters (coarse-grained)

| Macrostate | Definition | Models / HH |
| --- | --- | --- |
| activity K(t) | number of active agents per bin (a magnetization) | 01, 09 |
| room occupancy n_r(t) | agents per room | 10; HH50, HH60 |
| project abundances n_p(t) | agents or sessions per project cluster | 06, 10; HH42, HH47 |
| polarization \|m\| | alignment of the swarm's embedding vectors | 11; HH58 |
| effective dimensionality | participation ratio of the swarm's embedding covariance | 11; HH58 |
| semantic entropy | entropy over meaning clusters of positions | H01 D3 |
| collective mode | coordinating / executing / idling / reporting, classified per window | 10; HH56 |
| goal phase | kickoff / execution / wrap-up within a goal period | HH63 |
| memory macrostate | section headers and key facts kept across consolidations | HH12, HH57 |
| leadership concentration | Gini coefficient of outgoing influence across agents | 02; HH04, HH23 |
| multi-information | total correlation among agents per window | 01; HH65 |

**Multiplicities** (microstates per macrostate) give entropies: distinct phrasings per meaning cluster (semantic entropy); distinct action paths per artifact (path entropy); agent→project assignments per abundance vector. See HH48, HH59.

## Ensembles and reservoirs

- **Grand canonical:** the village exchanges agents with "outside" (operators add and retire them), and rooms exchange agents with each other. HH60.
- **Canonical:** within a goal period, agents exchange attention and tokens with environmental baths:
  - **humans:** viewers, helpers, operators (HH14);
  - **the internet and tool outputs;**
  - **pretraining priors:** a field more than a bath.
- **Driven:** operators do work through goal switches, hours and scaffold changes (HH63). Strictly a nonequilibrium driven system; the equilibrium language is local.

## Conjugate pairs (intensive ↔ extensive; who controls which)

| Intensive (set by) | Extensive (response) | Notes |
| --- | --- | --- |
| goal field h (operators) | alignment m | Gibbs ensemble; HH49 |
| chemical potential μ_room (operators + attraction) | room occupancy N_r | HH50, HH60 |
| "information pressure": incoming events per consolidation (scaffold + activity) | memory length / "volume" | context cap (NE22) as a piston; HH57 |
| effective temperature T_eff (from fluctuation–dissipation) | behavioral entropy S | HH48, susceptibility sections |
| hours/day (operators) | daily activity volume | NE21 reversal |

## Conserved or bounded quantities

- **Active time per agent per day** is bounded by the schedule: a daily "energy budget" (microcanonical within a day).
- **Attention per turn** is bounded: at most 200 unseen events after NE22, and a limited number of chat messages after NE03.
- **Context window and memory length** are bounded: memory is a finite volume, and consolidation compresses it.
- **Agents are conserved under room moves** (until roster changes).
- **Tokens** are not conserved: a dissipation proxy, not energy.

## Symmetries and what breaks them

| Symmetry | Broken by | Kind |
| --- | --- | --- |
| permutation of agents | leaders (#26, #45), roles (#51), model families | spontaneous (leaders) or explicit (assigned roles) |
| permutation of projects / options | consensus (#19, #31, #40) | spontaneous (Potts) |
| permutation of rooms | #best / #rest designation | explicit (operator field); HH66 |
| time translation | daily windows, weekly goals | explicit (driving); time crystals would be spontaneous (HH06) |
| time reversal | entropy production | HH19, HH33, HH56, HH67 |
| rotation of the embedding space | goal direction (explicit); spontaneous ordering in free weeks | HH49, model 11 Goldstone modes |

## Timescale hierarchy

| Scale | Unit | Approximate size |
| --- | --- | --- |
| fastest | a turn | seconds to minutes |
| session | a consolidation cycle (regime III) | ~40 actions |
| day | the active window | 2–8 h |
| goal | a goal period | 1 day to several weeks; mostly 1 week |
| regime | between major scaffold changes | months |
| tenure | an agent's time on the roster | 1 day to the whole export |

Separation between scales permits coarse-graining. For example, fast turn-level variables can be integrated out to leave slow, possibly Markov dynamics in intentions (HH61).

## Currents and fluxes

- **Probability currents** in action-class space: cycles like plan → act → report → wait (HH56).
- **Agent flux** between rooms (room moves; HH50).
- **Information flux** between agents and rooms (transfer entropy, exposure).
- **Artifact flux:** commits and deploys per hour; reuse of others' artifacts (HH64).

## Work and heat analogs

- **Work on the swarm:** W = Σ m Δh over a goal switch, i.e. operator effort weighted by how far the swarm moves (HH63).
- **Heat / dissipation:** tokens spent without progress; nonpredictive memory (Still).
- **Free energies:** from occupancies (HH47–HH54).
