# Definitions

Operational definitions: what each physics/sociophysics concept means in terms
of actual dataset fields. Hypotheses must use these. When a hypothesis needs a
different version, add a named variant here instead of redefining locally.

Status: **draft** = proposed, not yet checked against the data;
**checked** = verified on the data (note how); **settled** = in use by a hypothesis.

Field references are to the AI Village tables (`data/raw/ai-village/SCHEMA.md`).

---

## System and population

### Agent
- **Status:** draft
- **Definition:** one row of `agents`, identified by `agents.id`. Model family from `agents.model_string` (`claude-code::…` = Claude Code scaffolding, which logs to separate tables).
- **Open questions:** treat a model upgrade under the same name as the same agent or a new one?

### Population, N(t)
- **Status:** draft
- **Definition:** agents on the roster at time t (joined ≤ t < left, from the CHANGELOG roster table).
- **Variant, active population:** agents that emitted ≥ 1 event in a window around t.
- **Note:** the population changes over time (agents join and leave), so this is an open system. Grand-canonical rather than canonical treatments may be the natural fit.

### Regime
- **Status:** draft
- **Definition:** a time interval with fixed scaffolding. Boundaries come from `CHANGELOG.md`. The biggest one is **2026-03-24** (perma-computer-use: discrete sessions replaced by continuous computer use + periodic `CONSOLIDATE`). Other notable ones: 2026-02-25 (chat rooms added), 2026-04-14 (outreach approval system).
- **Rule:** never pool across the 2026-03-24 boundary without saying so. Prefer analyses that hold within a regime, or that treat regime as an explicit control.
- **Open questions:** which smaller changes count as boundaries? Build a machine-readable regime table in `infra/`.

### Driving / external field
- **Status:** draft
- **Definition:** inputs from outside the swarm: village goals (`village_goals`, with start/end), per-agent goals (`agent_goals`), and human messages (`USER_TALK` events, `chat_messages.speaker_type = 'user'`).
- **Open questions:** are goal changes better treated as quenches (sudden parameter changes) than as a field?

## Time

### Clock time
- `created_at` (UTC, microseconds). The canonical ordering of events is `events.event_index`.

### Village day
- Day 1 = 2025-04-02, increments daily at ~17:00 UTC, skips most weekends. Use for linking back to the site only; do analysis in clock time.

### Activity time
- **Status:** draft
- **Definition:** time measured in events (or agent actions) rather than seconds. Useful when the swarm is idle overnight and on weekends.

## State and actions

### Action
- **Status:** draft
- **Definition:** an agent-emitted event, labelled by `events.data.actionType` (`AGENT_TALK`, `WAIT`, `PAUSE`, `CONSOLIDATE`, `SEARCH_HISTORY`, …). At finer grain: one `computer_use_turns` row, labelled by `agent_action.action`.

### Agent state
- **Status:** draft
- **Definition (coarse):** the agent's most recent action type.
- **Variants to consider:** current task/goal (from session goals or `CONSOLIDATE.nextSessionGoal`); latest memory (`agent_memories.content`); an embedding of recent messages.
- **Variant, categorical (for model 10):** σ_i ∈ {1…q}: project/topic cluster, room, action class, vote, team or role, per window. Clusters must be fixed within a regime.
- **Variant, vector (for model 11):** s_i ∈ S^{n−1}: a centered, whitened, normalized embedding of the agent's messages, session goal or memory in a window. Or ψ_i = √p_i, the square root of the agent's distribution over q topics, which puts mixed states on a sphere.

### Memory state
- **Status:** draft
- **Definition:** the agent's latest `agent_memories` row before t. Memory consolidation is a compression step, so it is a natural place to look for information loss.

## Interaction and transmission

### Interaction
- **Status:** draft
- **Definition (broadcast):** agent i posts in room r; every agent whose `current_room` is r (or every agent, before rooms existed on 2026-02-25) is exposed.
- **Variant (addressed):** i's message names j (needs mention parsing).
- **Variant (reply):** j posts in the same room within Δt after i.
- **Open questions:** exposure means the message was in the agent's context, which depends on scaffolding. Check what agents actually saw.

### Contagion / adoption event
- **Status:** draft
- **Definition:** agent j uses a marker (a phrase, tool, URL, idea, goal) for the first time, after being exposed to it via an interaction from an agent that already used it.
- **Open questions:** how to choose markers; how to separate contagion from shared pretraining (e.g. Claude models saying "genuinely" independently). Exposure-free baselines are essential.

## Thermodynamic and information quantities

### Energy / work proxy
- **Status:** draft
- **Definition:** compute spent: `events.data.inputTokens`, `outputTokens`, `cost` per action. Per agent, per window.
- **Open questions:** tokens measure effort, not physical energy. Is "free energy spent per goal completed" meaningful?

### Entropy (of behavior)
- **Status:** draft
- **Definition:** Shannon entropy of the action-type distribution, per agent or per swarm, per window.
- **Variants:** entropy rate of action sequences; entropy of message content (token or embedding level).

### Entropy production / irreversibility
- **Status:** draft
- **Definition:** time-asymmetry of action-sequence statistics, e.g. KL divergence between forward and time-reversed transition probabilities.

### Mutual information between agents
- **Status:** draft
- **Definition:** MI between agents' action or state sequences, possibly time-lagged (transfer entropy for directed influence).

## Collective and semantic quantities (drafts for H01)

### Superagent
- **Status:** draft
- **Definition:** a grouping G of agents treated as a single system X_G (rooms, model families, project crews, role pairs, or data-driven groupings). A grouping is a *candidate* if it propagates information from its own past to its future beyond what the environment supplies (individuality). It is *supported* if, in addition, its viability depends on information no single member holds.
- **Open questions:** boundary choice is an input, not an output; correct for group size. See `hypotheses/H01-emergent-superagents-exist/architecture.md`.

### Semantic information (Kolchinsky–Wolpert)
- **Status:** draft
- **Definition:** for a chosen boundary, viability V and horizon τ: value of information ΔV = V[p] − V[scrambled p]; stored semantic information S = the mutual information kept by the least-informative viability-preserving intervention; efficiency η = S/I. Needs interventions (replay or simulation); observational data gives only bounds, e.g. |ΔV| ≤ √(I/2) for V ∈ [0, 1].

### Semantic entropy (meaning clusters)
- **Status:** draft
- **Definition:** entropy over meaning-equivalence classes of a set of statements. Statements are clustered by meaning (bidirectional entailment or an embedding threshold), then H = −Σ p_c ln p_c over the clusters. Not the same thing as semantic information. Used as an order parameter for ideology.

### Ideology
- **Status:** draft
- **Definition:** a group's distribution over positions on a fixed set of questions, coarse-grained by meaning. It is *ordered* when its semantic entropy is low and stable across windows.
- **Open questions:** mined statements vs. fixed probes asked in replay; separating shared-pretraining agreement (a field) from coupling.
