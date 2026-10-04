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
- **Variant: entropy production (pairwise AIK bound on activity spins)** (H05, 2026-10-03). Σ_g from g_ij = s_i(t+1)s_j(t) − s_i(t)s_j(t+1) on 1-min ±1 activity spins; θ cross-fitted or held out by day; reported per agent-hour; null = cross-day surrogate (the within-day circular-shift null manufactures irreversibility on real data). Companion: the cross-fitted Newton-step bound, lower noise floor. Recovers 69–85% of exact Σ on synthetic kinetic Ising; at village sample sizes, real-data Σ is at the noise floor. See `hypotheses/H05-rooms-cut/README.md`.

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

### Lineage
- **Status:** draft (H07, 2026-10-03)
- **Definition:** one artifact repository's default-branch history restricted to commits after a fork point A (`A..main`), where A is the newest ancestor commit contained in every fork's main. Fork membership and authorship come from commit e-mails (`<slug>@agentvillage.org`, 100% mapped to roster agents). See `hypotheses/H07-rpg-forks/README.md`.

### Copy information (fork variant)
- **Status:** draft (H07, 2026-10-03); unverified against the source paper
- **Definition:** for an ancestor feature X (file contents, identifiers, names, numbers keyed by position in the ancestor) and its descendant Y in one lineage, I(X;Y) = I_copy + I_transform. I_copy = Σ_x p(x) · d(p(Y=x|X=x) ‖ p_Y(x)) · 1[p(Y=x|X=x) > p_Y(x)], with d the binary KL divergence; I_transform = I(X;Y) − I_copy ≥ 0. Report copy fraction c = P(Y = X) and chance-corrected κ alongside.
- **Caveat:** this is H07's reading of Kolchinsky & Corominas-Murtra (model 08); the paper is not in `literature/`, so the definition still has to be checked against it.

### Action (turn-merged)
- **Status:** draft (H03, 2026-10-03)
- **Definition:** an agent's `events` within 1 s of its own previous event count as one compound turn. Used for event-time (Hawkes) models so that one tool call logged as several events isn't counted as self-excitation. In regime III `events_core` lacks computer-use turns, so "all events" changes meaning there; use `actions` for regime III turns.

### H01 named variants (2026-10-03; see `hypotheses/H01-emergent-superagents-exist/README.md`)
- **Semantic entropy (rarefied k-means):** entropy over k = 40 k-means clusters of per-regime whitened bge statement vectors (n = 32); each agent rarefied to 8 statements per day.
- **Agent state (vector), whitened statement mean:** normalized mean of whitened statement vectors per agent-day; also a fixed-8-statement version, so exposure isn't confounded with how much an agent wrote.
- **Interaction (exposure count):** number of j's messages on day d that reached i (from `exposure`), used as log(1 + E).
- **Goal field ĝ:** embedding of the goal text plus kickoff; per-room and per-agent versions exist (#38, #44 rooms; #51 private goals).
- **Agent field h_i:** cross-fitted from other periods, or first-day (fallback when cross-period invariance fails: it did in regimes II and III).
- **Residual alignment:** cosine of two agents' vectors after projecting out ĝ and both agents' fields.

### Exposure (turn read-out) (H08, 2026-10-04)
- **Call start:** the previous turn's time, or the pause expiry after a pause turn.
- **Read-out turn:** an agent's first turn whose call starts after a message arrives. **In-flight turn:** a turn whose call started before the message.
- Responses (addressing the sender) jump at the read-out turn, not the in-flight one (10/11 regime-II/III periods). Use this as the visibility rule; the shared context ledger (`infra/shared/context_ledger.py`) implements it.
