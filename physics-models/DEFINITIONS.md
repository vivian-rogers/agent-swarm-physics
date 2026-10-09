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

### Egregore (an ideology running on a substrate of agents) (H145; Vivian, 2026-10-09)
- **Status:** draft. Vivian's clarification (2026-10-09): "something like an ideology as egregore that runs over agents, with its own functional set of behaviors". The unit is a pattern, not a fixed set of agents.
- **Definition:** a *memeplex* K, a set of content elements (meaning clusters of statements, hashed coinages and protocol names, behavior signatures) that co-occur within agents, together with its current *hosts* H_K(t), the agents that express ≥ m of its elements in bin t. Hosts change; the pattern is the system and the agents are its substrate. K is an egregore if, in one goal period, it meets five conditions:
  1. *Integrated individual:* the pattern's state S_K (which of its elements are expressed, village-wide) predicts its own next state beyond the environment E and beyond its elements taken one by one: colonial A_K = I(S′_K; S_K | E) above frequency-matched pseudo-patterns, and integration Δ_K = L(S′_K | its elements separately, E) − L(S′_K | S_K, E) > 0 (Krakauer, at the pattern level).
  2. *Substrate-independent:* it persists while its hosts turn over: its prevalence is autocorrelated across days although its host set renews, and it survives its hosts' forced context erasures (NE41) by re-expression that is read-gated (supplied by other hosts or artifacts, not by the host's own residual context).
  3. *Recruits:* exposure to the pattern, read from hosts, raises non-hosts' adoption beyond a posted-but-unread exposure at matched lag (contagion with the in-flight placebo), including newcomers (NE33).
  4. *Functional behaviors:* the pattern carries actions that its hosts perform and that maintain the pattern: recruitment (named messages from hosts to non-hosts that precede adoption), repair (hosts restate the pattern toward a host that lapsed after a wipe or a challenge), and division of labor (different hosts carry different elements at the same time; synergy across hosts on the pattern's elements, O-information < 0 after fields are removed).
  5. *Valued information (Kolchinsky–Wolpert):* scrambling the pattern's carriers (host wipes, hub departures, operator vetoes) lowers the pattern's own persistence: value per bit κ_K = ΔV_K / I_K with V_K = the pattern's prevalence over the next day.
  A *candidate* meets 1–2; an *egregore* meets 1–4; a *valued egregore* meets all five.
- **Its relation to its hosts (descriptive):** *mutualist* if hosting raises the host's output on its own assigned role (work commits on its own repo, role-text alignment), *parasitic* if it lowers it, *neutral* otherwise. This is the essay's alignment question at the level of the village.
- **Environment E (impostor bundle):** the scheduler phase; the operator's and humans' messages (including human input relayed by an agent); the projections of each host's private role text and of the kickoff (an ideology that is the role text is a field, not an egregore); agent identity and lab as covariates (shared model priors: an ideology must spread across labs); strictly lagged.
- **Not an egregore:** a topic all agents discuss because the operator raised it (field); a style or value shared by one model family (prior); a single agent's project that others mention (a hub's artifact, not a pattern with hosts); a set of words that co-occur by chance (fails 1 against pseudo-patterns).

### Group superagent (a fixed group acting as one agent) (H143, H144; 2026-10-09)
*Named "egregore" in H143 and H144 as first written; renamed on 2026-10-09 after Vivian's clarification. The group is the contrast case to the ideology egregore: is the egregore a set of agents, or a pattern that runs on changing agents?*
- **Status:** draft (Vivian's essay, Direction 3)
- **Definition:** a set G of ≥ 2 agents, with the artifacts and the chat channel its members share, that satisfies four conditions in one goal period. (i) *Individual:* the group state x_G (its project, its content direction, its work/talk mix) predicts its own next state beyond the environment E and beyond size-matched random groups: colonial A excess z ≥ 2 (Krakauer). (ii) *Group-held:* no single member holds that information: min over members of Δ_i = L(x′_G | x_i, a_i, E) − L(x′_G | x_G, E) > 0 with z ≥ 2, where a_i is the member's own artifact. (iii) *Substrate-independent at the call scale:* the group's state continuity across one member's forced context erasure (NE41) is ≥ 0.9 of its continuity across placebo calls. (iv) *Valued channel:* cutting or scrambling the co-member channel lowers the group's viability: κ_G = ΔV_G / I_chan identified and > 0 (Kolchinsky–Wolpert). (i)–(ii) make G an individual on the substrate; (iii) makes the substrate replaceable; (iv) makes G an agent rather than a pattern. A *candidate egregore* satisfies (i); a *supported egregore* satisfies all four.
- **Environment E (impostor bundle, strictly lagged):** the scheduler phase (time-of-day bin, all-present mask, bookends), the rest of the village's state on the same channel, and exogenous messages (human, nudge, kickoff) to a member in the bin. Private goals (#51) and agent priors enter as agent-identity covariates, not as E. Never the nudger as an exogenous input, because it reacts to agents.
- **Candidate families (H143):** attraction crews (H58), shared-repo writer sets, #focus room occupants, read-graph communities, Krakauer boundary-expansion sets, assigned role pairs (the field control), labs (the prior control), the village. Membership is fixed on the first half of a window's days and scored on the second half (out of sample).
- **Not an egregore:** an assigned team that behaves as a unit because its members share a field (the #12 debate teams, #51 rival pairs); a hub with followers (fails (ii)); a group whose continuity dies with one member's wipe (fails (iii)).

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

### H29 named variants (2026-10-04; see `hypotheses/H29-driver-nodes/README.md`)
- **Influence coupling (content pull):** the slope a(S) = Σ y·u / Σ |u|² of a recipient's statement step y = x(τ_n) − x(τ_{n−1}) on the offset u = x_m − x(τ_{n−1}) to a message m, over a set S of (message, next-statement) rows. Net pull κ subtracts a cross-day placebo (same sender, another day) and the invisible-row pull.
- **Visibility jump (boundary test):** the field-corrected pull of visible minus truly invisible messages (call window ≤ 30 s), within matched 10-s age bins, named vs named and unnamed vs unnamed. The preferred influence estimator (post hoc in H29).
- **Driver score (mean-output Gramian):** D_k, the summed squared swarm response to a unit injection at agent k under the fitted linear pull network A with leak Γ. Steering energy E_k = N²/D_k. *Instrument, not a model (2026-10-07): see "Instruments (not models)" at the end of this file.*
- **Net influence current:** I_k = out-strength − in-strength of agent k in A.

### H31 named variants (2026-10-04; see `hypotheses/H31-consensus-time-spectral-gap/README.md`)
- **Interaction (seen, weighted):** W_ij = agent j's messages first seen by agent i, per active hour (visibility via H18's call-start rule; see the Known issue on that rule).
- **Consensus event (project share):** on H11 project labels carried forward up to 4 windows (30 min), project a reaches consensus when ≥ max(3, ⌈N/3⌉) agents and ≥ 50% of labelled agents hold it for 2 consecutive windows. **Frozen:** already met at the block's start (goal kickoff); **instant:** met in the window the project first appears; **gradual:** otherwise.
- **Consensus time τ:** active time from the project's first appearance to the consensus window (floored at 0.25 h).
- **Exposure spectral gap λ₂:** the second-smallest eigenvalue of a Laplacian of W. Variants: `w,sym` (L = D − (W + Wᵀ)/2, primary), `w,dir` (in-Laplacian, smallest nonzero Re λ), `bin` (normalized Laplacian of the binary graph), `rw` (random-walk Laplacian × the reading-turn rate), `core` (core agents only).
- **Time-respecting DeGroot gap γ_tr:** the decay rate of disagreement under DeGroot averaging (α = 0.5) simulated on the real reading sequence.

### H36 named variants (2026-10-04; see `hypotheses/H36-reorganization-alarm/README.md`)
- **Population N(t), day-present:** roster agents (Claude Code excluded) with ≥ 10 active minutes that PT day (H38 uses ≥ 1 minute).
- **Multi-information (Gaussian, activity spins):** I_G = −½ log det of the agents' 1-min activity correlation matrix, per pair. **(pairwise expansion, behavior states):** sum of pairwise plug-in MI of the 4-state activity class (Miller–Madow), per pair. **Content multi-information (overlap):** −½ log det of the normalized overlap matrix of agent-centered 30-min content vectors, per pair. All reported as excess over within-day surrogates.
- **Heat-capacity analogue:** the variance over time of the alignment energy, Var_t(E)/n (activity) or Var_w(e(w)) × mean pair count (content).
- **Content centroid shift (R1):** D(d) = 1 − cos(m̄_d, m̄_{d−1}), with m̄_d the mean whitened unit agent-day vector of day-present agents.

### H38 named variants (2026-10-04; see `hypotheses/H38-platform-stalls/README.md`)
- **Joint silence:** a minute with at most one day-present agent active (K_t ≤ 1) on a day with ≥ 3 present (H02's "lull", day-present version).
- **Village-off gap:** a run of ≥ 10 consecutive minutes with K_t = 0 (H16's rule).
- **Silence reason** of a silent present agent, first match: `pre`/`post` (before its first or after its last active minute of the day), `infra_err` (gap adjacent to an infrastructure-error turn, ≤ 15 min), `consol` (before a CONSOLIDATE, ≤ 15 min), `pause` (declared wait/pause spell), `none`.
- **Stall (explained joint silence):** a joint-silence minute outside the day's scheduled run, or in which ≥ half the silent present agents have a recorded reason. Strict variant: all silent agents but one have a reason.
- **Agent-state conditioning:** before a synchrony statistic, drop off-schedule minutes and set an agent's not-started / finished / consolidating / error-gap minutes to its block mean; compare against block-shift surrogates processed the same way. f_scaffold = 1 − E_adj / E_raw.

### H37 named variants (2026-10-04; see `hypotheses/H37-stance-spins/README.md`)
- **Interaction (addressed reply, 30 min):** B's message names A's author within 30 min of A's message. **Interaction (adjacent reply, 5 min):** B posts within 5 min of A in the same room. Pairs are kept only where Jev says B responds to A.
- **Stance spin:** Jev's zero-shot reply stance on a pair (oppose … support), used as soft s_e = P(support) − P(oppose).
- **Stance coupling (residual):** the pair's mean stance after an ordered logit with speaker and target effects removes agent fields.
- **Frustration index (ground-state):** the share of signed residual bonds violated by the best two-camp split (exhaustive or annealed).

### H11 named variants (2026-10-03; added 2026-10-04; see `hypotheses/H11-potts-labor-vs-herding/README.md`)
- **Agent state (categorical, project/artifact strict):** σ_i(w) = the project with the most strict artifact mentions by agent i in window w (strict = `artifact_mentions` with `speaker_kind = agent` and `how ∈ {url, output, bare}`, one count per agent × source × turn/message × project; directory-resolved mentions dropped). Ties go to the most recent mention; no mention = missing, not idle. Projects with ≥ 2% of a period's labelled agent-windows get their own state (q ≤ 8); the rest merge into "other" (state 0). Measures attention to a project, not work on it. See the Known issue on tie-break reproducibility.
- **Agent state (categorical, action class):** the regime-invariant action class of the agent's turns in the window (see the H11 card).

### H27 named variants (2026-10-04; see `hypotheses/H27-herding-early-warning/README.md`)
- **Herding onset (project-share step):** on H11 merged project labels, the first window in which project a's share of labelled agents is ≥ 0.5 with ≥ 3 agents on a and ≥ 4 labelled, the mean share over the previous hour was ≤ 0.25, and the mean share over the next hour stays ≥ 0.4. Scorable only with ≥ 6 h of prior record. Compare H31's consensus event (frozen / instant / gradual), which uses a two-window majority rule instead.

### H39 named variants (2026-10-04; see `hypotheses/H39-catalysts-vs-fields/README.md`)
- **Lever episode:** an isolated kick (nudge, human message, @-mention, erasure, kickoff, step) to an agent, with matched controls eligible on past information only and both arms cut at the next kick.
- **Field effect (occupancy shift):** a lever's change in the stationary state occupancy of the agent's behavior chain (e.g. idle share), φ_exc ≥ 0.10 to count.
- **Catalytic effect (escape at fixed occupancy):** a symmetric change in transition rates out of and into a state (K, |K| ≥ 0.10 to count) that leaves stationary occupancy unchanged. Catalytic fraction ρ = share of a lever's effect that is catalytic. The split depends on how a rate change is divided between forward and backward rates.

### H25 named variants (2026-10-04; see `hypotheses/H25-criticality-dial/README.md`)
- **Loop gain (equal-time, daily dial):** per day and channel, minute spins with stalls and scheduled-off minutes masked and 30-min block means removed; VR = Σ_t(Σ_i X_it)² / Σ_t Σ_i X_it², g = 1 − 1/VR, T/T_c = 1/g, amplification = VR. A lower bound on steady-state gain: blind to coupling delayed by minutes.
- **Per-pair correlation ρ̄:** (VR − 1)/(N − 1). At fixed ρ̄, g = (N−1)ρ̄ / (1 + (N−1)ρ̄) rises with headcount, so compare swarms of different size on ρ̄, not g. Flat ρ̄ across N is a shared-field signature; flat g is J₀/N coupling.
- **Platform stall (null-calibrated joint silence):** minutes whose joint silence exceeds a per-day null threshold (deterministic), used as a per-minute mask; catches 98% of planted outage minutes.
- **Content soft spin (30-min window):** whitened message-embedding window mean per agent, after removing agent-day means and operator-message directions, with a method-of-moments noise correction.

### H34 named variants (2026-10-04; see `hypotheses/H34-idea-cascades/README.md`)
- **Idea (H34 marker rule):** a hashed marker (no text stored) of one of four classes: U artifacts (from `artifact_mentions`), D numbers with ≥ 3 significant digits, N capitalized runs / code identifiers / hashtags / short quoted phrases, W words of ≥ 6 letters not in the system dictionary; agent, family and lab names dropped. An idea belongs to the period of its first non-holdout use.
- **Interaction (visible exposure):** a message counts as seen by agent i if it reached i's room before i's call started (H18's rule; see the Known issue on pauses and long tool calls).
- **Adoption cascade (exposure tree):** each agent's first use of an idea is parented to the latest earlier use it could see; cascade size = number of agents in the tree.
- **Branching ratio (content):** R̂ = first uses with an agent parent ÷ all agent first uses. **HR₁₀:** the adoption hazard within 10 min after a visible use ÷ the hazard otherwise (exposure locking; robust to a shared field in synthetics). **Contagion share** R_c = R̂ (1 − 1/HR₁₀).

### H26 named variants (2026-10-04; see `hypotheses/H26-content-near-critical/README.md`)
- **Loop gain (equal-time, room excess):** ρ_ex = (ρ_w − ρ_c)/(1 − ρ_c), with ρ_w and ρ_c the split-half-normalized within-room and cross-room per-pair correlations. Removes village-wide drives (not room-specific ones). Compare channels only at matched time resolution: day means inflate an equal-time gain as g_day = J(2 − J).
- **Agent state (vector), linear statement mean:** the unnormalized mean of whitened statement vectors per agent and window (the norm keeps how strongly an agent leans, unlike the unit-normalized H01 variant).
- **Exogenous drive direction:** a content direction imposed from outside the agents (goal text, kickoff, first-hour mean, operator messages) that is projected out before computing alignment.

### H30 named variants (2026-10-04; see `hypotheses/H30-operator-susceptibility/README.md`)
- **Operator kick classes:** N_tgt (nudge to its named agent), N_by (the same nudge seen by room-mates), H_men (human message naming the agent), H_und (human message not naming it). Matches `kicks_classified`.
- **Activity susceptibility χ_act (local projection, A30):** extra active minutes of the recipient in the 30 min after a kick, by local projection with matched pre-history strata (idle duration, recency) and a day fixed effect, adjusting for past kicks and future undirected kicks only. Policy-relative: 20–40% below the per-kick effect in synthetics.
- **Content susceptibility χ_con (orthogonalized placebo):** the change in cosine between the recipient's next statement and the message's direction after projecting the direction off the recipient's last 8 statements, minus the same for same-kind messages from other days.
- **Context fill:** turns since the last reset (`context_ledger_turns.ctx_pos` since `reset_consol`). See "Context fill, note" in the H60–H73 section: `ctx_pos` counts receiving calls since any reset and is null in chat mode.

### H06 named variants (2026-10-04; see `hypotheses/H06-neutral-cooperative-dynamics/README.md`)
- **Agent state (categorical, intention cluster):** whitened bge intention vectors clustered within the period (k-means or Ward; ladder m ∈ {8, 24, 64}), carried forward up to 4 windows. Topics of stated intentions, not repositories (compare H11's project/artifact strict variant).
- **Copy-consistency:** the share of an agent's project switches that go to a project another agent currently holds. Every exchangeable copying model (NCD, Hubbell, herding) predicts ≈ 1; the village shows 0.23–0.53 (0.08–0.10 in #51).

### H35 named variants (2026-10-04; see `hypotheses/H35-nudger-maxwell-demon/README.md`)
- **Mutual information (controller–state):** I(nudge decision; agent state) per decision, in bits, against a full-permutation null, for nested state spaces (coarse paused/idle; trap age = pause-chain length; gate level).
- **Work (feedback, activity gain):** extra active minutes (or tool turns) of the nudged agent in the next 30 min, past-only ATT. Distinct from the token-based "Energy / work proxy".
- **Semantic efficiency of a controller:** η_SU = achieved work ÷ the work attainable with the same information (Sagawa–Ueda-style); η_KW = bits needed ÷ bits used (Kolchinsky–Wolpert-style); κ = extra active minutes per bit per nudge; frontier V*(R) = best work at information rate R. Ceiling ΔV ≤ s·√(2rI) (Donsker–Varadhan), with s the half-range of the response across states, playing the role of k_BT.

### H01 round-2 named variants (2026-10-04; see `hypotheses/H01-emergent-superagents-exist/README.md`, "Round 2 formal setup")
- **Superagent (effective, Kolchinsky–Wolpert):** a unit G = members + shared artifacts (projects with ≥ 50% of their period writes by members) + channel, with positive KW semantic information for its own viability carried by group-level components. Test: scrambling one member costs less than scrambling the unit store, with an individuality excess over activity-matched random groups and member-shift surrogates. Candidate units come from coordinated behavior (artifact crews, behavior-state synchrony, co-allocation, reply communities); rooms and labs are baselines.
- **Unit macro-state (work ledger):** whether G advanced its artifacts in a 30-min bin (binary, from strict executed git/deploy writes). Too coarse to see a store that decides *which* artifact members work on (H01 synthetic); H58 should use a state that encodes the artifact.
- **Allocation continuity ΔC:** overnight return of members to the unit's artifacts vs a permutation null, with leave-target-day-out membership.
- **Semantic information (natural-scramble variant)** (H15): ΔV of a viability measure after a naturally occurring scramble of one store (forced consolidation NE41, memory loss, departure, night, channel cut, goal change), against matched non-scramble controls.

### H28 named variants (2026-10-04; see `hypotheses/H28-links-spread-herding/README.md`)
- **Interaction (link exposure, call-start visible):** a link to project X posted by another agent that became visible to the recipient within the last 60 min (visible = the recipient's next model call after the post; H18's rule, to be replaced by the context ledger).
- **Contagion / adoption event, variant arrival (project switch-in):** an agent's first strict touch of X after ≥ 60 min without one.
- **Agent state (categorical, on-project multi-label):** the set of projects an agent touched within the last 60 min (an agent can be on several).
- **Link-attributable share R_link** = π · k_s · λ (links posted per switch × susceptible recipients per link × extra switches per exposure): an upper bound on the causal share when links ride bursts.

### H47 named variants (2026-10-04; see `hypotheses/H47-room-coherence-length/README.md`)
- **Room contrast C_B:** ρ_cross / ρ_within, the ratio of cross-room to within-room per-pair content correlation (agent_win30 vectors), against a size-preserving room-relabel null. Measures the *global share* of a room's fluctuation, not coupling: coupling amplifies weak global drives.
- **Conversational tier ratio G:** within-room correlation of pairs that never mention each other ÷ that of pairs that do. G ≈ 1 = broadcast coupling; G < 1 = pairwise (conversation-following) coupling.
- **Room-localized shift R1_loc / per-room R1:** H36's day-to-day content centroid shift computed per room (R1_loc: localized to the room's own deviation from the swarm).
- **Room lead index L:** the lag at which one room's content shift leads another's after a swarm-wide event (goal change), with a pooled Stouffer test.

### H54 named variants (2026-10-04; see `hypotheses/H54-kickoff-quench-target/README.md`)
- **Quench target t̂_p:** the content state a goal period's kickoff drives the swarm toward; H54's claim is that it is readable from the kickoff text, t̂_p ≈ k̂_p (the kickoff message embedding in the same whitened basis).
- **Own-target percentile π_p:** the share of decoy kickoffs q ≠ p (the other 32 eligible kickoffs; within-regime and adjacent-period variants) whose similarity to the day-1 centroid is below the own kickoff's.
- **Quench depth D_p:** mean_i cos(v_i, k̂_p) − mean_{q≠p} mean_i cos(v_i, k̂_q) (excess over decoys). **Jump J_p:** cos(day-1 centroid, k̂_p) − cos(previous period's last-day centroid, k̂_p).
- **Kickoff specificity:** S_text (mean z of log counts per 100 words of numbers, named entities, artifacts/URLs, agent/role/room names, deadline terms), S_count (absolute counts), S_emb = 1 − mean_q cos(k̂_p, k̂_q) (distinctiveness).
- **Re-quench amplitude (HH180):** a_m = cos(centroid after m, ê_m) − cos(centroid before m, ê_m) over 60-min windows for a mid-period human message m, minus length-matched decoy messages.
- **Kickoff remanence (HH182):** daily kickoff excess A_ex(d) fitted as A_∞ + (A_1 − A_∞) e^{−(d−1)/τ_K}.

### H46 named variants (2026-10-04; see `hypotheses/H46-style-conserved-charge/README.md`)
- **Agent state (style, chat agent-day):** the 17 type-controlled H13 numeric style features (length, code and link shares controlled) averaged over an agent's chat messages in a day.
- **Agent state (vector, chat agent-day, style-residualized):** DQ5's `style_resid_period` vectors.
- **Boundary displacement percentile T:** the mean percentile of an agent's displacement across a boundary among its own placebo transitions (T = 0.5 under no change); T_s for style, T_c for content.

### H56 named variants (2026-10-04; see `hypotheses/H56-ep-platform-fingerprint/README.md`)
- **EP rate (count-matched, within-agent):** H14's Newton-bound entropy production of an agent's turn-level action chain over a window, subsampled to matched transition counts, compared within agent across a boundary (t statistic against the agent's own placebo windows). A lower bound: the chains are not Markov.
- **Agent-only chain:** the turn-level chain with scaffold records (mirrors, consolidations, forced markers) removed and a 3-transition burn-in dropped after every scaffold reset.

### H32 named variants (2026-10-04; see `hypotheses/H32-information-current-leaders/README.md`)
- **Content transfer (exposure-conditioned, cross-validated Gaussian):** the leave-one-day-out gain in predicting agent j's next message vector from an exposure-gated, decayed sum (τ = 15 min) of agent i's messages that j has seen, beyond j's own past, the day × room field, other seen senders, and humans and bots; minus the median of 40 cross-day shifts. Out_i, In_i, Net_i are row/column sums; T is the total.
- **Outflow centralization Φ:** how concentrated the outflow is on one source (star ≈ 0.5–0.75 in synthetics; distributed ≈ 0.01–0.11).

### H43 named variants (2026-10-04; see `hypotheses/H43-kick-refractory-window/README.md`)
- **Receiving call:** the first model call of the recipient whose context contains a kick message (`context_ledger_items`); kicks are timed there, not at posting.
- **Kick spacing (read-out):** the time (and number of calls) between the receiving calls of two kicks to the same agent; "same call" when both are read in one context assembly.
- **Launched episode:** the run of active calls that follows an effective kick (minute-grid run of activity).
- **Refractory ratio R(δ):** the second kick's effect (log hazard ratio of escape vs matched controls) ÷ the first kick's, as a function of spacing δ. R ≈ 1 means no refractoriness; R ≈ 0 means the second kick is wasted. Needs a positive first-kick effect to be meaningful.

### H53 named variants (2026-10-04; see `hypotheses/H53-announcement-nucleation/README.md`)
- **Seed:** a project's first chat link in a period (agent or human poster); re-links after lulls analysed separately.
- **Adoption (project label, H53):** a recipient's first project label after reading the seed, on `project_states` (deterministic H11 labels).
- **Wave size (H53):** new adopters within 2 h of the seed.
- **Call cycle (agent median):** the agent's median interval between model calls (`call_windows`).
- **Receptive count:** uncommitted agents whose receiving call of the seed falls within one call cycle of posting (`context_ledger_items`).

### H48 named variants (2026-10-04; see `hypotheses/H48-settling-mixing-time/README.md`)
- **Read-out coverage C_k(t):** the share of ordered room-mate pairs (i, j) where i has read ≥ k of j's messages since the kickoff (`context_ledger_items`). **Coverage time T_q:** active time to C_1 = q (T90 at q = 0.9). Weakest-link: one rarely posting agent sets it.
- **Bulk vs worst-case mixing time:** relaxation times of the read-out Markov chain (who reads whom, per call), from the bulk of the spectrum vs the slowest mode.
- **Kickoff remanence at active-hour resolution:** H54's remanence fit with τ in active hours; detectable in ~45% of periods.
- **Newcomer assimilation gap:** a newcomer's content distance to the room centroid vs days since joining.

### H50 named variants (2026-10-04; see `hypotheses/H50-field-vs-coupling-transfer-lag/README.md`)
- **Call cycle (hop):** counting a recipient's model calls after a message: hop 0 = the call already running when the message arrived, hop 1 = its first call whose context can contain the message (`call_windows` t_call).
- **Read-out jump J₁:** the increase in the probability that the recipient's hop-1 call is a talk call after a peer message, vs matched calls without one. Onset at hop 1 (not hop 0) is the signature of read-out-gated coupling.
- **Field excess (shifted-input null):** the share of swarm co-movement explained by measured common inputs (schedule edges, human messages, nudges, platform errors) beyond the same inputs shifted in time.
- **Coupling share (counterfactual, gated kernel):** the share of talk co-movement reproduced by a counterfactual built from the fitted hop kernels. Field and coupling shares are separate measures, not a partition: coupling amplifies field-driven talk.

### H44 named variants (2026-10-04; see `hypotheses/H44-erasure-reacquisition-thrash/README.md`)
- **Call category:** a per-call class from the command text and turn type (read local file / read remote / look at screen / room read / write / git / talk / pause …); regex heuristic, not hand-validated.
- **Re-acquisition share:** the share of non-write calls that read (files, remote, screen, room) in calls 1–5 after a reset.
- **Thrash index Θ_c:** the rise in re-acquisition share after a reset, conditioned on agent × previous call category (so a pure output dip does not leak into it), with a 0.01 floor.
- **Pseudo-erasure:** a matched no-reset position in a segment, used as the control for the within-segment ramp.
- **Reply rate per visible message:** replies (DQ2) per item that entered the call's context (ledger).

### H55 named variants (2026-10-04; see `hypotheses/H55-norm-enforcer-immunity/README.md`)
- **Correction (Jev confident subtype):** a DQ2 reply pair with stance opposes at confidence ≥ 0.8 and `opp_type` ∈ {correction, decline}. Precision 0.93 as correction on a blind sample; recall ≈ 0.10 (rates are scaled, not absolute).
- **Directed read:** a message addressed to an agent (reply parent or @-mention) that entered its context at a receiving call (ledger).
- **Loop episode (restatement / copy):** a run of an agent's statements flagged `self_repeat` by either model (restatement) or both (copy) (DQ5). **Blocked episode:** a run of Jev v3 windows with `p_blocked` ≥ 0.5.
- **Immune contrast Δ:** the change in loop or blocked-episode escape hazard after a directed correction is read vs after other directed messages, with agent fixed effects.

### RE-B1 named variants (2026-10-04; see H17, H16, H14 round-1b sections)
- **MSM (soft, shifted estimator):** a Markov state model on Jev v3 probability vectors (soft occupancies) with the noise-cancelling shifted count estimator; implied timescales t2* and PCCA+ macro states. Needs ≥ ~15k windows per period; per-period verdicts are descriptive below that. *Instrument, not a model (2026-10-07): see "Instruments (not models)" at the end of this file.*
- **Shell sub-classes:** fine action classes splitting bash turns into vcs / net / run / read / write / wait / other from `bash_head_fixed` plus change evidence (`hypotheses/H14-behavior-entropy-production/analysis/build_r1b.py: head_class`).

### H45 named variants (2026-10-04; see `hypotheses/H45-context-homeostasis/README.md`)
- **Context segment:** the calls between two context resets (forced at the 41-call cap, voluntary consolidations, session starts).
- **Room tokens (calibrated):** ≈ 50 tokens per room message + 0.3 per character + 116–163 per non-chat room event, received since the last reset (fitted on Anthropic and Google prompt sizes; they agree).
- **Context share (room, token-calibrated):** room tokens ÷ measured prompt tokens per call. **Own content:** the agent's own messages and actions in the segment.
- **Regulation index RI:** 1 − the elasticity of the room share to room inflow (RI ≈ 0 passive, ≈ 0.4–0.5 for a synthetic set-point controller).
- **Engagement (reply parent, pending):** whether a talk call replies (DQ2 parent) to a pending message.

### RE-V1 named variants (2026-10-04; see H18, H08, H04 round-1b sections)
- **Exposure (ledger receiving call):** a message is exposed to a recipient at its receiving call (the first call whose context contains it, `context_ledger_items`); replaces "Exposure (turn read-out)" timing with ledger t_call.
- **Talk turn / pending set (ledger):** a talk turn is a call that posts chat; its pending set is the senders whose messages entered the recipient's context since its last talk turn (`context_ledger_turns.k_since_talk` counts them).

### RE-P1, H49, H52 named variants (2026-10-04)
- **Agent state (categorical, project, work ledger)** (H11 round 1b): per agent-window, the repo with the most agent work commits (DQ4 default filter). **Co-location (raw project):** the share of agents sharing their repo with a room-mate in the same 30 min.
- **Conditioned pseudolikelihood bond** (H49): equal-time pseudolikelihood inverse-Ising coupling after H38's agent-state conditioning, against 200 joint block-shift surrogates. **Significant-bond graph:** bonds with one-sided empirical p < 1/n_pairs. **CV-C10:** cross-validated share of the excess covariance carried by the top 10% of pairs (dense ≈ 0.1–0.16, dilute ≈ 0.3–0.65 in synthetics).
- **Sender class; authority premium π** (H52): human / agent / bot sender; π = coarsened-exact-matching ATT of a human (or bot) message vs matched agent messages (naming, read-out age, novelty, length, recipient state, room size). **Content pull (DiD χ):** H52's difference-in-differences content statistic (replaces H30's χ_con where sender classes differ in topicality).

### Round-1b batch C/O/V and H40 named variants (2026-10-04)
- **Call clock; exposure-time elasticity η** (H40): coupling runs on the call clock when the reply hazard per receiving call does not depend on the wall time the call spans. η is the elasticity of the per-call reply hazard to the call's wall-time span: 0 = call clock, 1 = wall clock.
- **Per-call coupling; per-hour coupling** (H40): per-call coupling is the agent-unit fixed effect on the per-call reply hazard. Per-hour coupling is per-call coupling × call rate. **Cadence elasticity ε(T):** the elasticity of P(reply within T) to a uniform speed-up of an agent's calls, holding the message stream fixed.
- **Net reply current** (H29 round 1b): replies an agent receives minus replies it gives (DQ2 parents), per window. It is the Gramian driver score of the reply graph.
- **Visibility jump (ledger boundary test)** (H29 round 1b): the content pull of messages just inside vs just outside the recipient's receiving-call context at matched message age.
- **Agent state (V4 lumping of v3)** (H39 round 1b): Jev v3.1 states lumped into work / coord / wait / maint, with soft 5-min transitions.
- **Agent state (behavior, agent-day)** (H13 round 1b): the 11 Jev v3 state probabilities plus actions, real failures, commits and file writes per window, averaged per agent-day.
- **Stance coupling (DQ2, soft)** (H21/H22 round 1b): the mean signed DQ2 stance (supports +1, opposes −1, weighted by label confidence) over a pair's reply edges. It measures agreement of positions, so assigned sides alone predict it.
- **Glance; sustained run** (H35/H43): a glance is any activity within 30 min of a kick. A sustained run is ≥ 3 consecutive active ledger calls.
- **Agent state (categorical, intention cluster)** (H06): the km24 cluster of an agent's stated goal / intention in a window. It is topic-level (sub-tasks), not a project label; use the work-ledger variant for projects.
- **Interaction (ledger-visible exposure)** (RE-D1): a message is visible to a recipient iff it was posted before the `t_call` of the recipient's producing call (the context ledger's receiving call). **Unread (in-flight) exposure placebo:** the same statistic computed on messages posted but not yet read at the outcome, at a matched lag. **Blind window (t_post, t_vis]:** the interval between a message's post and its first possible read by a recipient.

### H59 named variants (2026-10-04; see `hypotheses/H59-one-lever-model/README.md`)
- **Field strength h, catalytic strength κ (call-level):** in a per-call multinomial GLM over idle / work / talk, a kick read at lag ℓ adds β = K_ℓ[κ_c + h_c(u_j − u_i)/2]. κ is a uniform rate change for all transitions (catalysis); h is a push along a shared direction θ in state space (field). **Read-out delay d:** the median time from post to the receiving call. **Transfer ratio T:** the held-out skill of the one-lever model for a left-out class ÷ the skill of that class's free fit (leave-one-class-out).

### H41 named variants (2026-10-04; see `hypotheses/H41-readout-light-cone/README.md`)
- **Logged light cone (time-respecting):** the set of (agent, call) reachable from an item's first appearance through ledger read-out paths in time order; its **entry call** is an agent's first call that could have read the item. **Acausal adoption:** an adoption before the adopter's entry call. **Cycles per hop:** receiving calls (or talk calls) between successive hops. **Static hop distance:** shortest path on the aggregated pre-item read graph (overstates reach). **Cone-boundary jump:** J_in = adoption hazard at the entry call ÷ at in-flight calls; **J_mh** = the delay-matched (Mantel–Haenszel) version.

### H58 named variants (2026-10-04; see `hypotheses/H58-coordinated-superagents/README.md`)
- **Unit macro-state (allocation):** the repo each member commits to per 30-min bin (DQ4 work commits), carried across bins. **Agent + own artifact (null unit):** each member stays on its last repo or moves by its own repo popularity. **Coordination gain g:** held-out log-loss gain (bits) of a unit model that lets members join each other's repos over the null unit (a which-artifact transfer entropy). **Re-acquisition path:** the sequence from a forced erasure to the member's first commit (re-read, intention, peer mention).

### H42, H67 named variants (2026-10-04): read-out kernel and gain (see `hypotheses/H42-readout-hawkes-kernel/README.md`, `hypotheses/H67-lagged-criticality-dial/README.md`)
- **Read-out lag** (H42): the time from a message's post to the `t_call` of the recipient's read-out call (`context_ledger_items`). Median ≈ 20 s, q90 150–200 s, q99 6–16 min.
- **Read-out kernel (call-index)** (H42): cross-excitation that puts a pulse at the recipient's read-out call and decaying pulses at its next 15 calls. Call-index bins {0}, {1}, {2–3}, {4–7}, {8–15}; weight w_b = extra talk events per read message from calls in bin b.
- **Cross-branching ratio (compensator share)** (H42): n_cross = Σ_i ∫ X_i dt / N_events, the share of events that the fitted cross-excitation explains. It counts truncation at day ends, so kernels of different shape compare directly. Per-pair weight = n_cross / mean recipients per message.
- **In-flight placebo (matched-lag)** (H67): peer messages posted in the recipient's room in (t_c, t_c + d_c], with d_c = `t_first − t_call` of call c clipped to [1, 120] s. Call c cannot read them. They share every time-local field with the messages read in the mirror window (t_c − d_c, t_c). A sibling of RE-D1's unread (in-flight) exposure placebo.
- **Read-out jump (matched-lag) J₁\*** (H67): β(R^m) − β_P in the per-call talk GLM with agent × day × call-class baselines. R^m = peer messages read at call c and posted in (t_c − d_c, t_c); P = the in-flight placebo count. A field smooth on 5–60 s gives J₁\* = 0. Variant of H50's read-out jump J₁.
- **Read-out loop gain g_lag** (H67): g_lag = m̄ r̄ J₁\*, with r̄ the recipients per peer message and m̄ the talk messages per talk call. It counts the extra talk messages caused through reading, per talk message. g_lag < 1 is subcritical; T/T_c = 1/g_lag. Variants: g_lag,3 adds hops 2–3; g_lag,het is the spectral radius of K_ij = m̄_i J₁\*_i Pr(i reads j); g_lag,all uses all read messages. The gap g_eq − g_lag to the equal-time dial (H25) estimates field contamination.

### H57 named variants (2026-10-04): copying under load (see `hypotheses/H57-copy-under-backlog/README.md`)
- **Backlog (in-context read set) R(B):** the agent-authored ledger items that agent i received from its previous talk call through the call that produced statement B, same PT day. In computer-use calls, only items after the last context reset count. k = |R|.
- **Mutually invisible (in-flight) set I(B):** other agents' statements in B's room posted after B's call started, whose own calls started before B was posted. Neither author could read the other.
- **Echo (read-set near-copy):** B is a near-copy of an item in R(B): raw cosine ≥ 0.95 (bge-small) or ≥ 0.938 (gte-modernbert), the DQ5 thresholds. Chance-corrected echo e = echo(R) − [1 − (1 − q̂)^k], with q̂ from mutually invisible pairs.
- **Copy information (read-set channel, message-level coding):** copy information (fork variant) with Y = X only when B is a near-copy of its source. The source is the read item by an author that B names. Cluster-level coding measures topic coherence, not copying.
- **Contemporaneous convergence:** near-identical statements from agents that post at the same moment without reading each other. Measure it as the near-copy rate of mutually invisible pairs at matched lag. It is the fourth impostor of `STANDARDS.md` §1.

### H61, H62, H63 named variants (2026-10-04): idea spread and reply channels (see `hypotheses/H61-contagiousness-at-first-use/README.md`, `hypotheses/H62-ideas-travel-reply-graph/README.md`, `hypotheses/H63-bursts-start-with-work/README.md`)
- **Interaction (reply, DQ2 parent)** (H40, H62, H64, H65): message B replies to message A iff DQ2 `reply_pairs` holds (B, A) with `pair_set == cand` and `parent == True`. One parent per message. It replaces the draft timing rule "Interaction (reply)".
- **Interaction (reply channel, DQ2)** (H62): a use m by agent k reaches recipient j through the reply channel if m's DQ2 parent is a message by j (direct), or if a DQ2 parent edge joined k and j in [t_m − 2 h, t_m) (tie). Edges that involve j's adopting message or later messages are excluded.
- **Interaction (room-only)** (H62): a read agent use that is not a reply-channel use.
- **Reply premium Λ** (H62): Λ = HR_rep / HR_room, the ratio of adoption hazard ratios for a reply-channel use and a room-only use read within the recipient's last 3 talk-call windows. Fitted by idea-stratified conditional Poisson. A thread field alone gives Λ ≈ 3 (H62 synthetic).
- **Channel copy excess C_c** (H62): C_c = exp(β_seen − β_unread) for channel-c uses posted within 300 s before the call. Seen = read by the producing call; unread = in flight ("unread-only" coding). C_c > 1 is transmission beyond the channel's own field.
- **Per-edge transmissibility T_c** (H62): adoptions within the recipient's next 3 talk calls divided by first-read exposure events, per channel c.
- **Idea reach (24 h) S_i** (H61): the number of distinct agents (seed included) whose first use of idea i falls within 24 h of the seed message. Right-censored ideas are dropped.
- **Read-5 / unread-5 adopter** (H61): a non-seed first user j with another agent's use of the idea posted in the previous 300 s. Read-5 if j's producing call had read one such use; unread-5 if none was read and one later reaches j in flight.
- **Focus (novel load)** (H61): the log of the number of period-novel ideas first used in the seed message.
- **Specificity (goal distance)** (H61): 1 − cos(seed message, kickoff field) in the regime's 32-d whitened basis. Kickoff field = the room kickoff, else the kickoff, else the goal (`goals.parquet`). Not H54's kickoff specificity or H95's day-1 named share.
- **Poster reply in-degree (causal)** (H61): (R_p + 1)/(M_p + 2), with R_p the DQ2 parent replies to poster p's messages posted before the seed in the period and M_p p's messages before the seed.
- **Receptive fraction (5 min)** (H61): the share of other agents present in the seed's room that day whose ledger receiving call of the seed falls within 300 s of posting. A scheduler variable, adapted from H53's receptive count.
- **Work signal (state change, DQ4)** (H63): on project X, a deploy event is a commit on a pages branch or with a deploy message, or a `deploy` action that strictly mentions X. S = X's first deploy, or a deploy ≥ 60 min after X's previous one. B = X's first agent work commit; R = every other agent work commit (placebo).
- **Herding burst (arrival cluster)** (H63): arrivals onto X (H28's switch-in) linked by gaps ≤ 20 min, with ≥ 3 distinct agents and ≥ 60 min without an arrival before the first. Onset t₀ = the first arrival. Compare H27's herding onset and H31's consensus event.
- **Follower onset t_f** (H63): the second distinct agent's arrival in a herding burst.

### H64, H65, H68 named variants (2026-10-04): prizes, leaders and attention (see `hypotheses/H64-conflict-scarce-prize/README.md`, `hypotheses/H65-leaders-are-routers/README.md`, `hypotheses/H68-dilution-mixture/README.md`)
- **Prize state O(t)** (H64): 1 while a rival-exclusive prize is open (a debate before its verdict, an election before its result, a game between its first and last link), 0 once it is settled. From DQ6 (#12, #26) and linked games (#23).
- **Rival pair (exclusive prize) R_ij** (H64): two agents that compete for the same rival-exclusive prize: opposite debate teams, runoff candidates, or opponents in one game.
- **Prize-gated antagonism Δ** (H64): the coefficient on R_ij·O(t) in a stance model of DQ2 replies with speaker and target fields, R, O and a window effect (ordered logit with a conversation-block shock, or the OLS DiD). Δ < 0 means antagonism exists only while the prize is open.
- **Antagonism excess E_p** (H64): the number of significantly negative pairs (cluster-robust by conversation block, Benjamini–Hochberg q = 0.1) minus its mean under a calibrated agent-field ordered-logit null on the real reply structure.
- **Read-gated susceptibility χ_j (content inflow)** (H65): in a linear response of agent j's next statement (DQ5 whitened vector, field subspace removed), the coefficient on the decayed pooled read input from all agents (τ = 15 min, ledger reads). It measures how far j moves toward what it read, per unit read.
- **Read-gated influence κ_out,i (content outflow)** (H65): one shared coefficient on agent i's decayed read messages across all targets j ≠ i, after each target's other terms are partialled out. Written κ_i in H65; not H29's net pull κ or H59's catalytic κ.
- **Router index ρ_R** (H65): pct(χ_L) − pct(κ_out,L), with rank percentiles among the unit's agents. ρ_R > 0 is a router (high inflow, low outflow); ρ_R < 0 is a source. Calibrate on a skeleton null.
- **Reply-out share RO** (H65): the share of an agent's statements in a window that are DQ2 replies (p_reply ≥ 0.5) to another agent.
- **Reply-out breadth BO** (H65): exp(entropy of the authors the agent replied to) / (N_present − 1).
- **Reply-in rate RI** (H65): agent replies received per own statement.
- **Dilution exponent (population, ledger)** (H18, RE-V1): β in P(talk turn addresses pending sender j) = 1 − exp[−θ_{i,d} n_j k^{−β} e^{γ m_j}], with k = `context_ledger_turns.k_since_talk`, n_j the pending messages from j, m_j = 1 if one names i, θ_{i,d} an agent-day propensity. Mention response: β 0.66 ± 0.02 (16/16 periods). Apply the mention factor per message (H18).
- **Dilution exponent (per-agent, ledger)** (H68): the same law with β_i indexed by agent, identified from k variation within agent-days. Eligible agents have ≥ 150 units, ≥ 15 responses and a within-agent-day SD of log k ≥ 0.3. The between-agent spread τ̂ comes from heteroscedastic random effects.
- **Attention-strategy mixture** (H68): β_i ~ π_A N(1, τ_w²) + (1 − π_A) N(0, τ_w²), thin attenders vs thread followers. Tested against the unimodal β_i ~ N(μ, τ²) by a parametric-bootstrap likelihood ratio.
- **Thread concentration C_i** (H68): per agent-day, (H − 1/S)/(1 − 1/S), with H the Herfindahl index of addressed senders and S the number of distinct pending senders; averaged per agent.

### H66, H74 named variants (2026-10-04): platform latency and change detection (see `hypotheses/H66-platform-latency-field/README.md`, `hypotheses/H74-change-detector/README.md`)
- **Call turnaround τ_c** (H66): t_first(c) − t_end(c − 1) for chained computer-use calls (`gap_kind == busy`, `ctx_mode == cu`, 0 < τ < 600 s). It sums scaffold overhead, generation and tool execution. Gemini calls also carry the server time `dur_api_s`.
- **Latency spin ℓ_i(m)** (H66): the median log τ_c of agent i's chained calls that start in minute m, standardized within agent-day (median and MAD).
- **Latency field L(m)** (H66): the cross-agent mean of ℓ_j(m). The third-party field L_{−ij} averages over agents other than i and j.
- **Latency field share f_lat** (H66): 1 − E_adj/E. E = per-pair co-activation on all-present minutes minus the block-shift null; E_adj = the same after each pair is regressed on L_{−ij} and the infrastructure-error field. The field excess Δf subtracts the shifted-input mean (H50).
- **Load sign** (H66): the block-demeaned corr(L, K) of a field with the active-agent count K. A field that drives activity gives corr < 0 (−0.34 to −0.66 in synthetics); congestion gives corr > 0. Report it with every field share from a regression.
- **Record signature** (H74): a record type plus its sorted field names and value types. For `events`: the action type and the keys and JSON types of `data`, without `output`. For `computer_use_turns`: the keys and types of `agent_action` and the null status of `output`, `error` and `system`.
- **Schema-diff alarm z_S** (H74): 4 × the number of platform-wide record-signature changes on a day. New: ≥ 5 records from ≥ 2 agents (or a non-agent type), absent the previous 10 active days. Retired: ≥ 2% of its type and ≥ 2 agents in the baseline, expected ≥ 10, zero that day. A newcomer's signatures in its first 3 days do not count. Alarm at z_S ≥ 4 (0/34 placebo days).
- **Synchronous within-agent shift z_M** (H74): the maximum over per-call behavior features (call-kind shares, records per call, turnaround, tokens, error share) of |median over day-present agents of the within-agent trailing z|. Baseline: the agent's previous 10 active days; ≥ 3 agents.
- **Change-point alarm (multi-channel)** (H74): Z(d) = max(z_S, z_M, z_O, z_D, z_C) over the schema, mix, oracle-format, drive and content channels. Each z is a trailing z (median and trimmed SD) against the previous 10 non-holdout active days. Alarm at Z ≥ 4; the fused alarm's per-day false-alarm rate is 0.18. *Instrument, not a model (2026-10-07): see "Instruments (not models)" at the end of this file.*

### H60, H69, H71, H72, H73 named variants (2026-10-04): context, loops, memory and idle gates (see `hypotheses/H69-loops-context-fixed-points/README.md`, `hypotheses/H71-memory-homeostat/README.md`, `hypotheses/H72-trap-aging-input-starvation/README.md`, `hypotheses/H60-index-nudge-policy/README.md`, `hypotheses/H73-style-three-components/README.md`)
- **Context fill, note** (H73, H69; corrects the H30 entry): `context_ledger_turns.ctx_pos` counts receiving calls since any reset, i.e. since the last `reset_consol` or `reset_session` (`reset_forced` is a subset of `reset_consol`). It is null for regime-I/II chat-mode calls. In regime III `first_of_day` is not a reset, so `ctx_pos` and `k_ctx` carry over the night. It counts calls, not chat messages or prompt tokens.
- **Context segment, boundary rule** (H69, infra): cut segments at `reset_consol | reset_session` only. Do not cut at `first_of_day`.
- **Cross-call restatement r_t** (H69): a chat statement flagged `self_repeat` (DQ5) by either embedding model whose matched source lies in an earlier call of the same agent. Same-call sources are message splitting. Variants: bge, gte, both (copy); templated statements excluded.
- **Self-share (chat, segment) s_t** (H69): O_t/(O_t + K_t), with O_t the agent's own statements earlier in the context segment and K_t = `k_ctx` at the producing call; 0 when both are 0. The char-weighted variant uses own characters vs `chars_new`.
- **Novel input (read, bge)** (H69): an item read since the agent's previous statement whose novelty ν = 1 − max cos(item, the agent's last 5 statements) on raw bge-small vectors exceeds the period median. Not H72's novel item.
- **In-context enrichment** (H69): the Mantel–Haenszel odds ratio that statement t near-copies an earlier own statement u when u is still in the current context segment vs when an erasure removed it. Strata: agent × log-lag bin (0.1 decade) × calls-between bin; pairs within 3 h. OR > 1 means restatements copy what is in context.
- **Memory snapshot phase (append / compress)** (H71): each regime-III consolidation writes two `memory_stats` rows, an append snapshot and then a compress snapshot (`lines_removed > 0`).
- **Compression cycle n** (H71): the interval between two compress snapshots of one agent: one consolidation in regime III, one compressed session in regimes I/II.
- **Post-compression size x⁺_n** (H71): ln characters of the memory at compress snapshot n.
- **Pre-compression peak y_n** (H71): ln characters of the last snapshot before compress snapshot n (= x⁺_{n−1} when no append came between).
- **φ⁺ memory reversion** (H71): the within-agent AR(1) coefficient of x⁺_n about the agent set point μ_i, agent-demeaned and pooled within a period (Nickell-corrected). Relaxation time τ = −1/ln φ⁺ cycles. φ⁺ ≈ b(1 + c), with b the slope of x⁺_n on y_n and c the growth slope. The mixed-phase series φ is not φ⁺.
- **Memory gain g_mem** (H71): 1 − φ⁺ per compression cycle. Written g in H71; not a loop gain.
- **Idle call** (H72, H60): a call of kind pause or wait that does not talk (H43/H59 rule). Every other call is active.
- **Idle gate** (H72, H60): a call whose previous call in the same agent-day is idle. At the gate the agent acts or idles again. Shared table: `infra/shared/idle_gates.py`.
- **Gate escape (sustained / any)** (H72): sustained = the gate call and the next two calls are active; any = the gate call is active (a glance). Censored at the day end.
- **Trap age (call clock)** (H72, H60): a_sus = t_call(gate) − t_end of the last call of the last sustained active run (primary); a_any = t_call(gate) − t_end of the last active call. Floor 10 s; gates before the day's first qualifying run are dropped. H60's trap age a is a_any.
- **Novel item (ledger)** (H72): a non-omitted `context_ledger_items` row of kind agent, human or nudge. Pause and resume bookends are not input.
- **Input starvation s** (H72, H60): t_call(gate) − t_call of the latest earlier call of the same agent-day that read ≥ 1 novel item (ledger). Items read at the gate itself are current reads, not part of s. Variants: s_content (drops DQ5 restatements and echoes), s_dir (directed items only), s_peer (agent and human items only).
- **Time since last read-out r** (H60): minutes since the agent last read a directed item (a nudge to it, an @-mention, a named human message). Equal to H72's s_dir.
- **In-flight placebo (gate latency)** (H72): others' messages posted in the gate's room in (t_call, t_call + latency_s], capped at 60 s. Never end such a window at `t_end`, which includes the pause timer.
- **Nudge index ν(x)** (H60): the expected extra active calls in 30 min that a nudge read at an idle gate buys in state x = (a, k, r), with k the gate index in the trap. It is the myopic (Whittle-subsidy) index. Written ĝ(x) in H60; not the goal field ĝ. *Instrument, not a model (2026-10-07): see "Instruments (not models)" at the end of this file.*
- **Agent state (style, message)** (H73): H46's 17 type-controlled style features on one chat message, joined to its producing talk call (`ctx_mode`, `ctx_pos`, `k_ctx`; nearest `t_first` within 3 s).
- **Assigned register** (H73): a speech role that the operator, the goal text or a draw gives to an agent, not one chosen in context: #12 judge vs debater; #51 private roles. A model swap changes the weights component, not the register.

### H58, H70, H87 and model-12 named variants (2026-10-04): stores, individuality and higher-order information (see `hypotheses/H70-artifact-store-semantic-info/README.md`, `hypotheses/H87-kappa-channel-table/README.md`, `hypotheses/H58-coordinated-superagents/README.md`, `12-information-dynamics/README.md`)
- **Krakauer individuality (organismal A\*, colonial A)** (model 12; H01, H58): for a unit state x, its next state x′ and an environment y: organismal A\* = I(x′; x), colonial A = I(x′; x | y), environmental determination nC = I(x′; y | x), environmental coding NTIC = A\* − A. H58's held-out log-loss estimator: A\* = L(x′) − L(x′|x), A = L(x′|y) − L(x′|x, y). H01 and H58 printed these labels swapped; read their "organismal" results as colonial. Put the scheduler, kickoff and prior fields in y.
- **Individuality ratio ι_G** (H58): colonial A_G / L(x′), on held-out log-losses.
- **Size-matched grouping** (model 12; H58, H81, H90, H95, H101): random groups of the unit's size, drawn from the same unit (and day), matched on member activity. It is the reference for every individuality, emergence, multi-information or fluctuation statistic, because these never fall with size. Forms: H58 200 groups with commits within ±50%; H81 random 4-agent subsets; H90 and H95 random 12-agent subsets.
- **O-information (field-removed)** (model 12, HH298; H101): Ω/(n−2) on agents' 1-d residuals after regression on exogenous directions (`goal_fields`, kickoff) and leave-one-out means, on DQ8-trimmed windows. Report it minus the 95th percentile of field-only skeletons and of size-matched groupings. Ω > 0 is redundancy, Ω < 0 synergy. Never subtract a leave-in mean: it fakes synergy.
- **Allocation pointer S_c (channel c)** (H70): the repo that channel c points to after an event. A (artifact): the repo of the agent's last work commit, open if touched in calls 1–5. M (memory note): the repo the latest intention names. R (room): the repo named most by items received in calls 1–5. C (context): the repo touched most in calls −10…−1.
- **Channel information I_c (allocation bits)** (H70): the Miller–Madow plug-in I(X⁺; S_c) between the post-event allocation X⁺ and the pointer, minus the mean over 200 within-agent permutations of S_c. For C: I_P − I_F, the bits that the erasure destroys.
- **Channel value ΔV_c (open-channel DiD)** (H70): the Poisson DiD effect of open × scramble on agent work commits in calls 1–20 after the event, with stratum × arm fixed effects. Scrambles: F (forced erasure) or N (night); placebos: P (pseudo-erasure, position 21) or PN (mid-day call). ΔV_rel = e^β − 1. For C: V(P) − V(F).
- **Channel value ΔV_c (own-scramble variant)** (H87): the same Poisson DiD at a channel's own natural scramble (memory size at erasure, search outage, human-message dose, repo naming).
- **κ_c (channel value per bit)** (H70, H87): κ_c = ΔV_c / I_c in commits per 20 calls per bit, Kolchinsky–Wolpert's value per bit with natural scrambles in place of interventions. Shared estimator: `infra/shared/semantic_kappa.py`. Not H35's κ (active minutes per bit per nudge).

### H75, H76, H14 named variants (2026-10-04): re-allocation and entropy production (see `hypotheses/H75-reallocation-speed-limit/README.md`, `hypotheses/H76-excess-housekeeping-split/README.md`, `hypotheses/H14-behavior-entropy-production/README.md`)
- **Committing population** (H75): agents with ≥ 1 agent work commit (DQ4 default filter) in the first 20 active hours after the kickoff; fixed over that horizon.
- **Repo allocation p(t)** (H75): the share of the committing population whose latest agent work commit at or before t is on repo x, plus a null state ∅, on a 15-active-minute grid. Initial conditions: W_pre (last 2 active days before the kickoff) or W_∅ (all at ∅).
- **Allocation distance W** (H75): TV(p(0), p(T)) = ½‖p(T) − p(0)‖₁, the Wasserstein distance on the complete graph of repos.
- **Switch activity Ā** (H75): repo switches in (0, T] per agent per active hour (∅ → repo counts). Ā_ss is the same over [16, 20] h.
- **Settling time T_e / T_90** (H75): the first time with D(t) − D_f ≤ (D(0) − D_f)/e (or 0.1). D(t) = TV(p(t), p∞), p∞ = mean p over [16, 20] h, D_f = median D over the same hours.
- **Speed-limit slack S** (H75): S = ĀT/W ≥ 1. T ≥ W/Ā is a counting identity, so the physics is in S. S ≈ 1: every switch moves an agent toward the settled allocation; S ≫ 1: churn. H95's size-matched S₁₂ is the median over 50 random 12-agent subsets.
- **Activity ratio R** (H75): Ā_ss T / W.
- **Minimum excess EP of re-allocation Σ_ex,min** (H75): 2W tanh⁻¹(W/(ĀT)) nats per agent.
- **Agent settling time t_i** (H75): active time from the kickoff to agent i's first commit on its settled repo, the repo it holds longest in [16, 20] h.
- **Cadence elasticity (settling) ε_set** (H75): the slope of log t_i on log call rate r_i. Written ε in H75; not H40's cadence elasticity ε(T).
- **Ensemble flux j_xy** (H76): j_xy = (1/(N_b K_b)) Σ_{i, t∈b} p_{i,t}(x) p_{i,t+1}(y), the soft transition count per agent-step in block b. The agents of a period are the ensemble copies; pseudocount 0.1 per edge.
- **Entropy production (ensemble flux, plug-in)** (H76): σ = Σ_{x<y} (j_xy − j_yx) ln(j_xy / j_yx) on Jev v3 soft states (coarse 5 or fine 12, with absent), in nats per agent per 5-min step. Debias by a surrogate floor inside an agent bootstrap; per-agent block flips, not per-step transpositions.
- **Excess EP σ_ex** (H76): max_φ [−Σ_x φ_x ṗ_x − Σ_{x≠y} j_xy (e^{φ_y−φ_x} − 1)] (Kolchinsky 2026, Eq. 38). It is the irreversibility of the net occupancy change alone and is 0 iff ṗ = 0. Day edges and quenches are excess.
- **Housekeeping EP σ_hk** (H76): σ − σ_ex ≥ 0, carried by cyclic currents that change no occupancy. It needs ≥ 3 states. Work cycles are housekeeping.
- **Excess share** (H76): Σ_b σ_ex,b K_b / Σ_b σ_b K_b over the blocks of a window, both debiased.
- **Edge share** (H76): σ_ex of a day's first and last 6 steps divided by the day's σ_ex, untrimmed grid.
- **Trim removal** (H76): 1 − (day total on the all-present trimmed grid)/(day total untrimmed), for σ_ex and σ_hk.
- **Entropy production (Markov pair-KL on categorical behavior states)** (H14; used by H56): per agent, the KL divergence between the forward and time-reversed pair distributions of its state sequence (the AIK bound with antisymmetrized transition indicators). Cross-fitted by day; null = detailed-balance surrogate.
- **Entropy production (AIK cross-agent bound on categorical states)** (H14; used by H90): on a common 1-min grid, the AIK bound with single-agent transition indicators plus cross-agent lagged antisymmetric observables. The collective term is the increase over the single-agent bound. Null = cross-day surrogate.

### H77–H80 named variants (2026-10-04): repos as replicators, autocatalysis and assembly (see `hypotheses/H77-repos-as-replicators/README.md`, `hypotheses/H78-replicator-growth-order/README.md`, `hypotheses/H79-artifact-autocatalytic-set/README.md`, `hypotheses/H80-assembly-vs-compression/README.md`)
- **Host (work ledger, call-clock expiry)** (H77, H78; `infra/shared/replicator_hosts.py`): per agent and 30-min window, the repo with the most agent work commits, carried forward. The label expires after E = 100 of the agent's own calls without a commit to it (variants 50, 150, 300, ∞) or at roster leave.
- **Recruitment** (H77, H78): a host label change into repo k when n_k ≥ 1 just before. Formation-free recruitment excludes kickoff-named repos and H28's blind window.
- **Birth** (H77, H78): a host label change into a repo with no host (n_k = 0).
- **Departure (uncopying)** (H77, H78): a host's label switches from repo j to another repo.
- **Expiry (replicator dilution)** (H77, H78): a host's label lapses after E calls without a commit, or the agent leaves the roster. Not attention dilution (H18, H68).
- **Swarm call clock τ** (H77, H78): the count of model calls by present agents (`call_windows`), cut into bins of B = 200 calls. Rates are per 1,000 swarm calls.
- **Operational affinity σ\*** (H77): σ\* = ln[(J⁺ + ½)/(J⁻ + ½)] for the top repo T on its plateau, with J⁺ recruitments and J⁻ departures. Plateau = bins after n_T first reaches ⌈0.8 max n_T⌉ with n_T ≥ 0.5 max n_T. Testable at J⁺ + J⁻ ≥ 8; nats per net copy.
- **Rare-phase fitness f_j** (H77): recruitments per host per 1,000 free calls while n_j ≤ 2.
- **Selection coefficient s_k** (H77): s_k = 1 − f_k/f_T for rival k against the top repo T.
- **Selection resolution σ\*** (H77; Kolchinsky 2025): if T persists and rival k goes extinct, then s_k ≥ e^{−σ\*}. Selection resolves only fitness gaps above e^{−σ\*}. At village counts the test has size 0 and power 0.
- **Order of uncopying q** (H77): J⁻_j ∝ C^host n_j^{q−1}; q = 1 is degradation-like, q = 2 chemical uncopying.
- **Growth order p** (H78): p in R_jb ~ Poisson(μ_jb), log μ_jb = log C^free_jb + α + p log n_jb, over (repo, swarm-call bin) cells with n ≥ 1. R = formation-free recruitments; C^free = calls by non-hosts. p = 1 is first order, p > 1 winner-take-all, p < 1 coexistence. Only p > 1 is identified under repo fitness spread.
- **Cross-lab growth order p_x** (H78): p with n counting only hosts from a lab other than the recruit's.
- **Artifact reaction (session × repo)** (H79): r = (X, Y), repo X written in a session while artifact Y's code runs. One event = one session × one product repo with ≥ 1 agent work commit. Reactants = repos read (strict mentions, read verbs) before the write, excluding X and Y.
- **Executed catalyst** (H79): a repo Y in whose working directory the agent runs code (`bash_head_fixed` python, node, npm, make, pytest, ./…; cwd from `artifact_mentions` `how ∈ {cwd, session_cwd}`) before the last write to X in the session. A DQ4 `automated` stream on X catalyses the self-reaction (X, X). Y = X is self-catalysis.
- **Operator food set F** (H79): platforms, artifacts whose `first_t` precedes the period, and artifacts that humans or the operator name in chat during the period.
- **Artifact-only RAF** (H79): a reaction set R′ in which every reactant and at least one catalyst of every reaction lie in the closure of F under R′. Agents are never catalysts. The maxRAF comes from polynomial pruning.
- **Commit window** (H80): L = 16 consecutive agent-identity, non-imported commits of one (repo, author identity) stream, labelled by majority DQ4 `automated`; at most 20 windows per stream-day.
- **Command motif** (H80): a contiguous n-gram (n = 4…8) of a session's action-token string (regime III), with its assembly index, session copy number, agents, labs and first-day presence.
- **Assembly proxy (Re-Pair grammar size)** (H80): a_RP = number of Re-Pair rules + (length of the final Re-Pair string − 1), an upper bound on the assembly index. It equals the exact index in 97.6% of validation strings. *Instrument, not a model (2026-10-07): see "Instruments (not models)" at the end of this file.*
- **Scheduler baseline** (H80): an L2 logistic classifier on timing features only (inter-commit gap statistics, second-of-minute, hour of day, share in the village window). It is the first rival for any sequence-based agent-vs-script signature.

### H86 named variants (2026-10-04): Taylor field gauge (see `hypotheses/H86-taylor-law-field-gauge/README.md`)
- **Taylor coefficients (a, c_T, b)** (H86): across the present agents of one unit, V_i = a μ_i + c_T μ_i² for the per-agent mean μ_i and variance V_i of counts per 15-min bin (1 h for commits); b = the slope of ln V on ln μ. c_T ≈ c_× + mean private burstiness, so neither c_T nor b is a field gauge.
- **Taylor field gauge c_×** (H86): c_× = Σ_{i<j} Cov(y_i, y_j) / Σ_{i<j} μ_i μ_j, the variance of a shared multiplicative field without private burstiness. Report `taylor_c_shared` on channel `activity_trim` (and `activity_raw`) from `per_period_estimates`. On talk it counts field plus equal-time coupling.
- **Shared share φ_sh** (H86): c_× Σ_i μ_i² / Σ_i (V_i − μ_i), the share of super-Poisson variance that the shared field carries. Written φ in H86 (`taylor_phi_shared`).
- **Within-day shared coefficient c_×w** (H86): c_× on counts demeaned within agent-day. c_× − c_×w is the day-level field.

### H100, H102 named variants (2026-10-04): room symmetry breaking and domain walls (see `hypotheses/H100-room-symmetry-breaking/README.md`, `hypotheses/H102-room-domain-walls/README.md`)
- **Room of a statement** (H100, H102): a chat statement's room is its message room (`chat_core.room`). An intention's room is the agent's as-of room in `rooms_timeline` (t_start ≤ t < t_end; null t_end → +∞). **Room of an agent-day** (H100): the majority room of the agent's statements that day.
- **Day-centred agent vector** (H100, H102): DQ5 32-d regime-whitened style_resid statement vectors, minus the mean over the agents present that day (removes the day field).
- **Room separation S** (H100): S = Δ^(1)·Δ^(2). Δ^(h) is the #best − #rest difference of agent means over alternating-day half h. S is unbiased for |Δ_true|². Agents that move inside the period are excluded.
- **Relabel excess Q** (H100): Q = S / mean(S_null), over 2,000 random partitions that keep the room sizes; p = share of S_null ≥ S. Q ≈ 1: the rooms differ like random groupings. **Q_res:** Q on x̄_i − â_i. **Q_spont:** Q_res after projecting out u_f and u_op.
- **Agent constant â_i (leave-period-out)** (H100): the mean over other regime-III non-holdout periods of agent i's period-mean day-centred vector. Use it only after the invariance check (odd vs even period sets against an agent-permutation null).
- **Composition share f_comp** (H100): Δ_comp·Δ / S, with Δ_comp the room difference of â_i and Δ the full-data room difference.
- **Field share f_field** (H100): (Δ^(1)·u)(Δ^(2)·u) / S. u_f = unit whitened difference of the two room kickoffs (where their cosine < 0.95); u_op = unit difference of the rooms' mean operator-message vectors (≥ 3 per room). Chance ≈ 1/32. Null: random directions from the empirical agent-difference covariance.
- **Spontaneous share f_spont** (H100): 1 − f_comp − f_field. Read the three shares only where Q has p < 0.05: a finite room carries chance composition.
- **Mover index φ_mv** (H100): φ_k = M_k / C for an agent k moved from room A to room B. M_k = mean sim(k, new-room stayers) − mean sim(k, old-room stayers). C = the stayers' mean native contrast (own-room minus other-room sim). sim(k, j) = ½(x̄_k^(1)·x̄_j^(2) + x̄_k^(2)·x̄_j^(1)) over alternating-day halves. +1 = a native of the new room; −1 = a native of the old room. Read it only when C is significant (stayer-relabel p < 0.05). φ_pre and φ_comp: the same index before the move, and with â in place of x̄. Written φ in H100; not H101's φ_K or H86's φ_sh.
- **Room remanence R_rm** (H100): cos(Δ_P^spont, Δ_P′^spont) for consecutive multi-room periods with the same room names (composition and field directions removed). Null: a joint relabel, so an agent present in both periods keeps one pseudo-room. Written R in H100. **Swap-carry R_room / R_agent:** cos of the post-swap room difference with the pre-swap difference grouped by the pre-swap rooms / by the agents' post-swap rooms.
- **Home domain; stayer; hopper** (H102): the home room holds most of the agent's statements in the unit. A hopper has ≥ 1 other-room `rooms_timeline` segment and either ≥ 1 statement there or > 0.25 h there. Every other agent is a stayer. Domain core = the stayers.
- **Domain axis u** (H102): u = (c_B − c_A)/|c_B − c_A|. c is the centroid of a domain's core stayers, from statements made in their home room. Cross-fitted: u comes from the other alternating-day half, and agent i is left out of its own centroid.
- **Wall coordinate s** (H102): s_i = (x_i − c_home)·u / ((c_other − c_home)·u); 0 = home domain, 1 = other domain. **s(all)** uses all of the agent's statements; **s(home)** only those made in its home room. Written s in H102; not H72's input starvation s or H93's share field s_j.
- **Domain bimodality D_A (Ashman)** (H102): (mean z_B − mean z_A) / pooled within-domain SD of the stayers' cross-fitted projections z_i = (x_i − c_A)·u. D_A > 2 means two separated modes. Null: room relabel with sizes kept and the axis refitted (1,000 draws). Written D in H102; not H54's quench depth D_p or H94's allocation KL D_k.
- **Interior occupancy I_wall** (H102): the share of agents (stayers, or all agents) with s ∈ [0.25, 0.75]. Written I in H102.
- **Hopping read-outs R_hop** (H102): per agent-day, the `agent`-kind `context_ledger_items` the agent received whose message room differs from its home room. **R_dom:** received items whose sender's home domain differs from the recipient's. The card's data-scheme text for "R" describes R_dom; its O3 fit uses R_hop (`reads_day.parquet`).
- **Posted-unread volume U** (H102): per agent-day, agent messages posted that day by others in the other domain's room that the agent never received in its ledger. It is the contemporaneous-convergence placebo for R_hop. **Dose slopes κ_R, κ_U:** hopper-fixed-effect WLS slopes of s(home) on log(1 + R_hop) and log(1 + U). Not the κ_c table.

### H84, H87 named variants (2026-10-04): search outage and the κ table rows (see `hypotheses/H84-search-outage-memory-scramble/README.md`, `hypotheses/H87-kappa-channel-table/README.md`; H70's allocation pointer, I_c, ΔV_c and κ_c and H87's own-scramble ΔV_c are in the H58/H70/H87 section above)
- **Search call** (H84): a ledger call of kind `search`. Raw searches are `events` rows with actionType `SEARCH_HISTORY`, mapped to the agent's ledger call with t_first ≤ t ≤ t_log + 1 s. **Failed search:** answer < 150 characters.
- **Search dose d_a** (H84): agent a's search calls per 100 ledger calls on 2026-03-24 → 03-30, the five regime-III days before the history-search outage. **Searchers:** d_a ≥ 0.25; d̄_s is their mean dose.
- **Continuity (repo-age variant), V1** (H84): per agent-day with ≥ 1 work commit, the share of its DQ4 agent work commits that go to repos whose first commit (`work_repos.first_commit_t`, any author) precedes that PT day's window start.
- **Duplicate creation (name-overlap variant), V2** (H84): per agent-day, the number of new repos (first commit that day, first committer = the agent) whose name tokens have Jaccard ≥ 0.5 with a repo that existed before the day. Tokens: the basename split on `-_./`, lowercased, ≥ 3 characters.
- **Earlier-goal reference share, V3** (H84): per agent-day with ≥ 5 strict mentions, the share of strict `artifact_mentions` (`how ∈ {url, output, bare}`; sources action, chat, intention; repo, site and file artifacts only) that name artifacts first seen before the current goal period's first day.
- **Allocation pointer S_c, H87 rows** (H87; extends H70's A, M, R, C): **G** (chat reads, agent senders): the repo named most by `agent`-kind ledger items received in calls 1–5. It equals H70's S_R on every event, because no human item names a repo. **H** (human messages): the same for `human`-kind items; I_H = 0 by construction. **Q** (history search): the repo named most by the answers of the agent's search calls in calls 1–5 (raw SEARCH_HISTORY rows, repo ids only). **K** (kickoff, day scale): the standing goal field, scrambled at a night that starts a new goal period. A channel is open when its pointer names A⁻, the repo of the agent's last work commit before the event.
- **Channel information I_K, I_Q** (H87, H84): I_K = I_within(X⁺; A⁻) − I_newgoal(X⁺; A⁻), the allocation bits that a new goal destroys. I_Q (H84, per search call) = I(X_next; S_Q), with X_next the repo of the first work commit in the call and the next 19 calls. Both use H70's Miller–Madow plug-in with a within-agent permutation floor.
- **Scramble cost ΔV (rows C, K)** (H70, H87): ΔV = mean placebo V × (1 − e^b), with b the Poisson coefficient of the scramble indicator and stratum fixed effects (`semantic_kappa.scramble_cost`). It is the value side of κ_C and κ_K.
- **Identified κ row** (H87 Amendment A1): a κ_c row is identified only when the lower bound of I_c's CI exceeds 0.02 bits. Otherwise κ_c is "n.i." and the row is placed by its ΔV_c: "κ ≈ 0 (consistent)" if the ΔV_c CI includes 0, "unresolved" if not. Make ordering claims (paired P(κ_i > κ_j) ≥ 0.9) only between identified rows. Reason: κ = ΔV/I explodes near 0.02 bits; restricted to identified rows, the synthetic made 0/25 wrong-direction claims.

### H97, H99, H101, H105 named variants (2026-10-04): quench memory, relaxation, co-usage and goal spins (see `hypotheses/H97-quench-restoring-force/README.md`, `hypotheses/H99-glauber-fluctuation-relaxation/README.md`, `hypotheses/H101-pairwise-vs-multi-information/README.md`, `hypotheses/H105-two-state-goal-order/README.md`)
- **Kickoff memory ρ_K (disattenuated)** (H97): ρ_K = cov(y, x) / √(var_true(x) var_true(y)) across a transition's agents. x = the agent's mean unit regime-whitened statement vector on the previous period's last active day; y = its day-1 mean (from H54's t0). True variances come from split-half cross products. Agents need ≥ 4 statements on both days. Written ρ in H97.
- **Placebo memory ρ_K0** (H97): ρ_K on ordinary consecutive active days (d, d + 1) inside one `period_units` unit, not touching day 1; the median over boundaries. Written ρ0 in H97.
- **Extra forgetting Δρ_K** (H97): ρ_K0 − ρ_K. Δρ_K > 0: the kickoff erases more of the pre-kickoff configuration than an ordinary night. Δρ_K∥ and Δρ_K⊥ are the same along k̂ and transverse to it. Written Δρ in H97; not H99's collective memory excess Δρ_c(k).
- **Kickoff memory β_P (IV slope); restoring susceptibility χ_P** (H97): β_P = Σ_i ⟨P(y_i − ȳ), P(x_i^A − x̄^A)⟩ / Σ_i ⟨P(x_i^B − x̄^B), P(x_i^A − x̄^A)⟩, with random split halves A, B of the previous-day statements and P ∈ {k̂k̂ᵀ, I − k̂k̂ᵀ, I}. χ_P = 1 − β_P. Use it for isotropy (β∥ − β⊥), not for forgetting: a common day-1 component lowers β without any forgetting.
- **Per-agent susceptibility χ^mem_ip (memory form)** (H97): 1 − ⟨y_i − ȳ_{−i}, x_i^A − x̄^A_{−i}⟩ / ⟨x_i^B − x̄^B_{−i}, x_i^A − x̄^A_{−i}⟩, with leave-agent-out centroids in the full space. It is heavy-tailed, so test agent constancy on within-transition ranks. Not H30's χ_act / χ_con or H65's χ_j.
- **Overshoot intercept a_K** (H97): the intercept a of Δ_i = a + b D_i along k̂ per transition. Δ_i = the day-1 displacement ⟨y_i, k̂⟩ − ⟨x_i^B, k̂⟩. D_i = the settled target (other agents' mean alignment on days 2–5) − ⟨x_i^A, k̂⟩. Errors-in-variables corrected; the leave-period-out centred variant is primary. a_K > 0: day 1 overshoots the settled level. Written a in H97; not H86's Taylor a.
- **Mean-field split (collective / transverse mode)** (H99): for centred agent spins X_it in bin t with N_t agents, the collective mode is M_t = Σ_i X_it/√N_t and the transverse part is X^⊥_t = X_t − (M_t/√N_t)·1. Spins: talk = `activity_bins_fixed.talk` > 0 in the minute; activity = `state` ≥ 3. Each is centred per agent within (day, 30-min block) on the DQ8 all-present grid.
- **Fluctuation gain g_χ** (H99): 1 − Σ_t p_t / Σ_t c_t, with c_t = M_t² and p_t = (Σ_i X_it² − M_t²)/(N_t − 1). It is 0 under independence and equals H25's g = 1 − 1/VR at large N.
- **Relaxation gain g_τ(k)** (H99): 1 − ln ρ_c(k) / ln ρ_⊥(k). ρ_c(k) = Σ M_t M_{t+k} / Σ M_t²; ρ_⊥(k) = Σ ⟨X^⊥_t, X^⊥_{t+k}⟩ / Σ |X^⊥_t|², over kept bin pairs in one day and block. Undefined when ρ_⊥(k) ≈ 0, as for talk at minute resolution.
- **Fluctuation–relaxation gap Δg_k** (H99): g_τ(k) − g_χ. Mean-field Glauber predicts 0. Δg < 0 means a fast shared field; Δg > 0 a slow field or delayed coupling.
- **Collective memory excess Δρ_c(k)** (H99 Amendment A2, post hoc): ρ_c(k) − max(ρ_⊥(k), 0.001)^(1 − g_χ). Glauber predicts 0 at any agent clock. > 0: a slow field or delayed (read-out) coupling; < 0: a fast field. Use it when ρ_⊥(1) < 0.15. Written Δρ_k in H99; not H97's Δρ_K.
- **Co-usage spin (agent-day)** (H101): in a unit-day, an item m is an H34 marker used in agent chat that day by ≥ 1 active agent (≥ 10 marker uses that day; Claude Code agent excluded). s_i(m) = 1 if agent i used m in a chat message that day. Items are the samples; agents are the variables. Families: conventions (marker classes N, W, D) and projects (class U).
- **Shared-field (K) model** (H101): P_K(s) ∝ exp(Σ_i h_i s_i + V(K)), with K = Σ_i s_i: the max-ent model of an exchangeable item-popularity field. P₂K adds pairwise J_ij (Tkačik's K-pairwise model). Entropies S₁ (independent), S_K, S₂K and S_N (empirical) are computed on random 6-agent subsets (10 per day) and bias-corrected by a parametric bootstrap.
- **K-field share φ_K** (H101): (S₁ − S_K)/(S₁ − S_N), the share of the multi-information I_N = S₁ − S_N that the shared-field model carries. Written φ in H101; not H86's φ_sh (a variance share) or H100's φ_mv.
- **Pairwise sufficiency after field removal ρ_F** (H101): (S_K − S₂K)/(S_K − S_N), the share of the multi-information beyond rates and the shared field that pairs capture. The raw Schneidman ratio I₂/I_N is uninformative at village rates. ρ_F < 0.8 is unreachable at village counts even with a planted group term.
- **Higher-order remainder r_HO** (H101): (S₂K − S_N)/I_N. Claim a group term only when r_HO is above the pairwise-truth bootstrap band (z ≥ 2.33) and above the heterogeneous-field reference.
- **On-goal statement (decoy threshold)** (H105): a statement whose projection ⟨z, ĝ_A⟩ exceeds θ(ĝ_A), the 95th percentile over decoy statements. z = unit regime-whitened statement vector; ĝ_A = unit(unit(W·goal_A) + unit(W·kickoff_A)). Decoys: 10,000 random non-holdout same-regime statements outside goals A − 1…A + 1 and #23. Variants at the 90th and 98th percentiles.
- **Goal spin σ_i,t (agent-window)** (H105): 1 if at least half of agent i's statements in 30-min window t are on-goal, else 0. Eligible with ≥ 2 statements in the window.
- **Goal occupancy p_g(t)** (H105): the mean σ_i,t over the window's eligible agents. Its composition-adjusted variance is V = mean_t (p_t − μ_t)², with μ_t the mean agent rate p_i of the present agents. Written p(t) in H105; not H75's repo allocation p(t).
- **Two-state loop gain g₂; coupling J₂** (H105): g₂ = 1 − V_ind/V, with V_ind = mean_t N_t⁻² Σ_i p_i(1 − p_i). J₂ = g₂ / mean_t q̄_t, with q̄_t = N_t⁻¹ Σ_i p_i(1 − p_i). Statement misclassification dilutes g₂ more at low p.
- **Tilt variance ratio ρ_V** (H105): ln(V_A^obs / V_A^pred). V_A^pred is the assigned week's variance under a uniform logit tilt λ of the free week's agent rates with the free week's J₂ (λ matched to the assigned week's mean occupancy). Not identifiable at village sampling (H105 Amendment 1).

### H93, H94, H96, H98 named variants (2026-10-04): project choice, max-ent allocation, goal switches and random fields (see `hypotheses/H93-brock-durlauf-project-choice/README.md`, `hypotheses/H94-maxent-work-allocation/README.md`, `hypotheses/H96-goal-switch-hysteresis/README.md`, `hypotheses/H98-random-field-51/README.md`)
- **Choice event** (H93): *work:* an arrival (recruitment or birth) in the host replay (H77 host, E = 100). *Attention:* a labelled agent-window whose H11 project differs from the agent's last label in the period; the first label counts. **Choice set:** options active earlier in the period, minus the chooser's current label, plus one "new" option.
- **Share field s_j** (H93): the share of the other active agents whose current label is j just before the choice. Work: hosts of j over active hosts, chooser excluded. Attention: labelled agents on j in the previous window over labelled agents.
- **Social coupling βJ** (H93): the conditional-logit coefficient of s_j beside the fields (kickoff naming `named_j`, the new-repo constant, habit prev_ij, log cumulative size: estimator M4). Only βJ is identified, not β and J. Fast common repo bursts give βJ ≈ 1–3 with no coupling (A2).
- **BD equilibrium count** (H93): the number of stable fixed points of m = ⟨softmax(h + βJ m)⟩_agents at the fitted parameters (top 8 options plus "other"; 209 starts). P_multi = the parametric-bootstrap probability of ≥ 2.
- **Work quantum** (H94): one (agent, 30-min window from the day's `win_start`, repo) with ≥ 1 DQ4 agent work commit.
- **Owner** (H94): the agent with the earliest agent work commit to the repo in all of DQ4 (author time, default filter). A repo whose first agent work commit predates the period is carried over.
- **Allocation KL D_k** (H94): KL(P̂ ‖ P_k) in bits per quantum, with P_k the max-ent agent × repo table under constraint set k: M1 margins (D_1 = I(agent; repo)), M2 + ownership, M3 + room. Read it against the persistence floor (each agent-day drawn as one block from P_k).
- **Ownership price λ_own; room price λ_room** (H94): the M2 log-odds bonus (nats) of a quantum landing on its owner's repo; the M3 bonus for a repo whose owner shares the agent's room.
- **Concentration index κ_conc** (H94): (H_MB − H_obs)/(H_MB − H_BE) on the entropy of repo shares. MB = independent uniform choice; BE = neutral Pólya copying. 0 = even, 1 = neutral copying, > 1 = herding. Written κ in H94; not κ_c, H29's κ or H59's κ.
- **Pseudo-switch (ordinary day boundary)** (H96): a day boundary inside a non-holdout period, not a goal boundary, with ≥ 3 active days before it and ≥ 1 after. It is the null for every goal-switch statistic.
- **Old-state direction ê_old** (H96): the leave-agent-out unit mean of the other agents' agent-day vectors (≥ 3 statements, DQ5 style_resid32) over days L−3…L−1 of period P−1, with L its last active day.
- **Field-orthogonal remanence M_exc** (H96): mean_i s_i(t)·P⊥_F ê_old^(−i), minus the median of the same over placebo old states ê_Q (late centroids of non-adjacent same-regime periods). P⊥_F projects out span{k̂_P, ĝ_P, the room kickoffs of P}. Written M_old in the card's formula.
- **Persistence ratio R₁^old** (H96): M_exc on day 1 ÷ M_exc on the pre window, defined when the pre value's CI excludes 0. ΔR₁ = R₁ − the median R₁ of same-regime pseudo-switches. Written R₁ in H96; not H36's content centroid shift R1.
- **Switching time τ_sw** (H96 Amendment 1): from ln(M_old(h)/M_new(h)) = L₀ − h/τ_sw over active hours h after the kickoff. It replaces the inertia time τ_old (an exponential fit of M_exc), which is biased low on unit vectors.
- **Old-state order q_old** (H96): the mean cosine between different agents' agent-day vectors on the same day, over the ê_old days. Not H77's order of uncopying q.
- **Random field (static agent field) h_i^RF** (H98): agent i's mean agent-day vector (DQ5) over the unit, minus the unit mean over agents. Its bias-corrected variance is Δ² = mean_i |h_i^RF|² − mean_i σ_i²/D_i (within-agent day variance σ_i², D_i days). Written φ_i in H98.
- **Disorder ratio R_dis** (H98): Δ²/(Δ² + M²), with M² the bias-corrected squared norm of the unit mean. 1 = pure random field; 0 = pure uniform (goal) field. Written R in H98.
- **Mean-field gain b_MF** (H98): Σ_{i,w} ⟨x_iw, m_{−i,w}⟩ / Σ |m_{−i,w}|² on agent-day-centred 30-min window vectors, with m_{−i,w} the other agents' mean (same room). **b_ex** = b_MF minus the cross-day surrogate. It contains common window drives, so read it as the size of the pull, not J. Written b in H98; not H86's Taylor b.
- **Niche overlap n_ij (role text)** (H98): cos(r̂_i − r̄, r̂_j − r̄) of #51 role vectors (`goals.parquet` `agent_goal`, regime-III whitened, unit-normalized). Co-movement scales with n_ij², so regress on n_ij².

### H51, H104 named variants (2026-10-04): one-dial collapse and field-step avalanches (see `hypotheses/H51-one-dial-collapse/README.md`, `hypotheses/H104-barkhausen-avalanches/README.md`)
- **Phase-diagram axes (h, K, N)** (H51): per goal period, K = H67's read-out loop gain g_lag (random-effects pool over units); h = H86's c_× on `activity_trim` (day-weighted over units; φ_sh variant), with H54's S_text as the kickoff field h_kick; N = H85's active population (log N in fits). Inputs only, never fitted in H51. K here is g_lag; not H101's co-user count K or H38's K_t.
- **One-dial collapse** (H51): a single per-period number u(h, K, N) puts every unfitted observable on one curve, Y_j = F_j(u). Score: leave-one-period-out CV-R² of Y_j on u, against regime labels, log N and field-only rivals. Null: permute u among periods of the same regime (2,000 draws), statistic Σ_j [CV-R²(u + regime) − CV-R²(regime)].
- **Loop rate (restatement share)** (H51): the share of an agent's chat statements that either embedding model flags as a self-repeat (DQ5 `statement_flags.self_repeat`; `self_repeat_both` variant). Not H69's cross-call restatement r_t, which drops same-call sources.
- **Switch (work arrival)** (H104): a DQ4 agent work commit (`canonical & ~imported & author_kind == agent & ~automated`) on repo Y, when the agent's previous work commit that PT day was on another repo and it made no commit to Y in the previous 60 min. A DQ4 form of H28's arrival (project switch-in).
- **Switch (attention arrival)** (H104): a 15-min `project_states` window (sources all) whose modal project Y differs from the agent's previous labelled window that day and was not its state in its previous 4 labelled windows. Time = the window start.
- **At-risk span** (H104): from 30 min after an agent's first call of the PT day to 15 min before its last call. Switches count only inside it (removes day-edge piles).
- **Field step (human session)** (H104): `kicks_classified` kind `human_message` (subkinds plain and mention, not kickoff), merged into one session when consecutive messages are ≤ 10 min apart on the same day. Step time = the first message; size m_k = messages in the session. Eligible: ≥ 3 agents at risk for the whole window and no other session in the previous window.
- **Burst size S_burst** (H104): after step k, the number of distinct at-risk agents with ≥ 1 switch in (t_k, t_k + W], W = 60 min. Null: each agent-day's switch times rotated circularly within its at-risk span (999 draws). Written S_k in H104; not H100's room separation S or H75's slack S.
- **Avalanche Fano F_A** (H104): [Var(S_burst) − Var(S_burst^null)] / [mean S_burst − mean S_burst^null]. A Poisson-like step response gives ≈ 1; a τ = 3/2 avalanche law truncated at N ≈ 15–30 gives ≈ 3–6. At village counts it does not separate the two (H104 synthetic).

### Round 2 variants (2026-10-05): content read-out, gains and clocks, quench relaxation, loops and style (see the "Round 2" sections of `hypotheses/H08-context-is-the-coupling/README.md`, `hypotheses/H40-call-clock-coupling/README.md`, `hypotheses/H44-erasure-reacquisition-thrash/README.md`, `hypotheses/H46-style-conserved-charge/README.md`, `hypotheses/H50-field-vs-coupling-transfer-lag/README.md`, `hypotheses/H54-kickoff-quench-target/README.md`, `hypotheses/H67-lagged-criticality-dial/README.md`, `hypotheses/H69-loops-context-fixed-points/README.md`)
- **Content read-out jump (matched age) J^c_h** (H50): J^c_h = Σ_b w_b [ȳ(h, b) − ȳ(0, b)] over 10-s age bins b in [0, 60) s, with w_b ∝ n_hb n_0b / (n_hb + n_0b). y = cos(z_B, z_m) − cos(z_B, z_m′): z is the 32-d whitened unit statement vector, B one of the recipient's next 8 chat statements within 30 min, m′ a same-sender statement ≥ 2 h away. B's hop h = pos(producing call) − pos(receiving call of m) + 1; hop 0 is the in-flight placebo. "Named" means m names the recipient (ledger `ment`); the response is not restricted. A content variant of H50's read-out jump J₁; not H08's Δ_cont.
- **Content response (matched lag) Δ_cont** (H08): x(s, m) = cos(s, m) − b(m, i), with b the mean cosine of the same message with recipient i's statements on the same PT day at |t − t_m| ∈ [20, 60] min. Statement s is *read* if the receiving call of m or a later call produced it, *in flight* if its producing call started before m. Δ_cont = Σ_b w_b (x̄_read,b − x̄_flight,b) / Σ_b w_b over lag bins (0–300 s) × density bins (own-room messages received in the 300 s before s), w_b = n_r n_f / (n_r + n_f); 1-h block bootstrap. Subset *no name, no reply*: drop statements that mention the sender or whose DQ2 reply parent is the sender's. It restricts the response; J^c_h's "unnamed" restricts the message.
- **Co-response share κ_co** (H08): Σ_b w_b x̄_flight,b / Σ_b w_b x̄_read,b for Δ_cont. A shared drifting topic gives ≈ 0.73 when responses follow only read messages, so it is not a pure convergence share. Written κ_c in H08; not H70/H87's κ_c (value per bit).
- **Exposure (turn read-out), round-2 scope** (H08): naming and replying to a sender jump at the read-out call; the recipient's content moves toward the message at the read-out only inside statements that name or reply to the sender.
- **Memory dose z (added name)** (H08): sender j is an added name at a consolidation if j is named (`common.mention_regexes`) in lines that the memory snapshots in (S_before, S_after] added and S_after still names. For erased units, the consolidation between the read-out and the talk call; for non-erased units, the next consolidation after the talk call (placebo dose). **Protection ratio π** = β_{CF×z} / (−β_CF). Fit with z × age-bin terms. Variant z_stock: j named anywhere in the prompt's memory.
- **Decoupled feed episode; event-age monitor** (H08): a fetch is stale if ≥ 50% of its returned events were created > 24 h before it; an episode is ≥ 3 consecutive stale fetches. The monitor alarms when the median event age over the last 5 fetches exceeds 1 h.
- **Read-out pull Δ_read** (H54): per (human message m, recipient i), Δ = [cos(z_after, ê_m) − cos(z_before, ê_m)] − mean over decoys d of the same with ê_d. z_before = i's last chat message before m (same PT day, ≤ 6 h); z_after = its first chat message whose producing call has `t_call` ≥ the receiving call of m (≤ 60 min). Mean over a message's read pairs, then the median over messages. A per-agent variant of H54's re-quench amplitude (HH180) that counts only read messages.
- **Read-out contrast C_read (matched lag × before-age)** (H54 Amendment R2-1): Σ_b w_b (mean Δ_read,b − mean Δ_if,b) over cells of after-lag × before-age (age bins [0, 120), [120, 600), ≥ 600 s), w_b ∝ in-flight pairs. The in-flight arm is i's first message posted after m by a call with `t_call` < the receiving call. **Convergence share (read-out, matched)** = mean Δ_if / mean Δ_read in the same cells.
- **Talk-propensity span elasticity η_talk; reply-given-talk span elasticity η_rep|talk** (H40): the round-1 hazard model on the same risk rows with y = "call n posts any chat message" (η_talk), and on rows where call n talks with y = "reply to m" (η_rep|talk). Variants of η (exposure-time elasticity). η_rep|talk conditions on talk, which m can cause.
- **Busy and scheduler-wait elasticities η_busy, η_wait** (H40): the span e_n = busy_{n−1} + wait_n, with busy = t_log − t_call of call n − 1 and wait = t_call,n − t_log,n−1; η log e is replaced by η_busy log busy + η_wait log wait. Logged chat-mode starts only (regime I).
- **Fano-implied total gain g_Fano** (H67): the g that solves H111's Φ_pred(g) = Φ_obs(10), with H111's room sizes and CI and no refit. It is an upper bound on the read-out gain, because fields only add variance. Not an independent test of H111's r_F.
- **Chat clock (regime I); chat-clock read-out gain g_chat** (H67): the response clock is the agent's chat-mode receiving calls. Per chat call c, R^m = peer messages posted in (t_c − w_c, t_c), P = those in (t_c, t_c + w_c), w_c = min(t_first − t_call, chat-to-chat interval, 120 s); cells agent × day × wake class. g_chat = m̄ r̄ (β(R^m) − β(P)); g_I = g_cu + g_chat. A variant of g_lag. Latency-placed starts attenuate it to about 0.23 × truth.
- **Lagged in-flight design; multi-generation gain G_H** (H67): read and in-flight counts at the same agent's calls c − k (k = 0…4), with disjoint symmetric half-widths h_c = min(latency, half of each adjacent interval, 120 s) and local-linear offsets. Δ_k = β(R^m_{c−k}) − β(P_{c−k}) = δ(k + 1) − δ(k); δ(h) = Σ_{k<h} Δ_k; G_H = m̄ r̄ Σ_{h ≤ H} δ(h); g_full = G₅. Descriptive only (synthetic recovery failed).
- **First stage ΔR** (H67): the RD jump in the anchor call's read count at the read-out boundary.
- **Call-skeleton null (regime I)** (H67, post hoc): synthetic worlds on the real regime-I call order with fixed call modes and no coupling. A statistic's value in these worlds is subtracted from the real value.
- **Relay read hop ρ_relay** (H50): for a source message A, a relay m_B (B posts it at the call that reads A) and a third agent C that reads both, ρ_relay = pos(r_C(m_B)) − pos(r_C(A)) + 1. ρ_relay = 1 is a batched read. Written ρ in H50; not H46's self-pull ρ_self.
- **Relay jump J_relay** (H50, post hoc): a start-time RD at the relay's posting time on C's calls, with anchors at C-hops ≥ 2 on A's clock (`r2lib.relay_rd`). Not valid in regime I (+0.025 with no coupling).
- **Chat-mode switch ΔP_chat** (H50): the read-out jump with "the recipient's next call is chat mode" as the outcome (regime I).
- **Call category (blind-checked)** (H44): the round-1 regex call category scored against 300 blind labels (population-weighted; re-acquisition κ 0.87; one rater). **Θ_c (checked)** replaces each call's re-acquisition indicator by P(true re-acquisition | category, window) from the labels; the conservative variant uses mid-segment rates in both windows. A variant of "Call category" and "Thrash index Θ_c".
- **Two-timescale sawtooth** (H44): y(k) = c + β(k − 1) + A₁ e^{−(k−1)/ℓ₁} + A₂ e^{−(k−1)/ℓ₂} at segment position k after a consolidation, ℓ₁ ∈ [0.3, 3], ℓ₂ ∈ [2, 20] (β read with ℓ₂ ≤ 12). **Complete sawtooth:** a forced → forced segment of 40 calls.
- **Cap output ratio Y(L)/Y(40)** (H44): Y(L) = Σ_{k≤L} Ŵ(k) / (L + c₀), with Ŵ the complete-sawtooth write curve and c₀ = 1 summary call per consolidation; L* = argmax Y over [5, 40].
- **Write-dip reference Ω_ref** (H44): the forced-reset write change over +1…+10 against one of five references: far (−20…−11), near (−10…−1), whole closed segment (−40…−1), agent-day steady state (positions 11–30), cycle mean (k 1…40). Quote the reference.
- **Re-open share; recency-adjusted excess** (H44): the share of object-bearing post-reset read calls (+1…+10) that touch an object (file-path hash) of calls −20…−1. The excess subtracts q̂·Δfrac, the recency difference between event types, with q̂ fitted on pseudo-erasures.
- **Looping; stuck loop** (H44): looping = ≥ 3 in-loop calls (round-1 command-hash flag) in the 10 calls before a reset; stuck (post hoc) = looping with no write call. A command loop, not H69's restatement loop. **E_loop** = mean ΔW(forced) − mean ΔW(pseudo31) among looping events.
- **Own tool tokens U** (H69): U_c = max(W_c − W_0 − C_c, 0), with W_c = P_c − R_c (prompt tokens minus room tokens on H45's lab ruler), W_0 = W at the segment's first call with P, and C_c the own chat tokens.
- **Erasure dose D** (H69): D = log(1 + (W_last − W_0)/1000), the own tokens in the segment at the last call before the reset.
- **Memory containment c(u, M)** (H69): the share of statement u's word 3-grams (lowercased) that occur in memory snapshot M. in_mem = c(u, M_t) ≥ 0.5 for the memory in the prompt at t; new_mem = in_mem and c(u, M_u) < 0.5; old_mem = in_mem and c(u, M_u) ≥ 0.5.
- **Agent state (style, genre-controlled) `g`; (genre- and position-controlled) `gp`** (H46): H46's 17-d type-controlled style residualized within regime on 23 genre covariates (DQ2 reply parent, parent kind and stance, max p_reply, mentions, leading @, DQ3 window probabilities), with agent fixed effects; only the covariate part is removed. `gp` adds the position block (call mode, log ctx_pos, log k_ctx, regime-III segment position).
- **Agent state (function words) `fw`** (H46): sqrt(count / n_tok) of the 50 most frequent closed-class words in messages with ≥ 10 tokens, winsorized, z-scored and type-controlled within regime. `fw_g` removes the genre block.
- **Context-held style offset ΔC(l); self-pull ρ_self** (H46): ΔC(l) = C_within(l) − C_across(l), the mean cross-product of agent-centred style vectors (clipped at ±3) at message lag l within one context segment minus across exactly one forced erasure, gap-matched. ρ_self = Σ⟨x_k − q̂, r̄ − q̂⟩ / Σ‖r̄ − q̂‖², with r̄ the mean of the agent's previous ≤ 3 messages, in context or erased. Written ρ in H46.
- **NE41 percentile (agent-scaled)** (H46 R2-A5): the boundary displacement percentile T with each pair distance divided by the median within-pair distance of its agent × unit. A variant of T.

### Round 2 variants, wave 2 (2026-10-05): rooms and leaks, alarms, idle traps, first reads, joins, family pull, monitors, idea heterogeneity, named kernels and ordered reads (see the "Round 2" sections of `hypotheses/H05-rooms-cut/README.md`, `hypotheses/H36-reorganization-alarm/README.md`, `hypotheses/H16-metastable-traps-kramers/README.md`, `hypotheses/H15-semantic-information-scrambles/README.md`, `hypotheses/H11-potts-labor-vs-herding/README.md`, `hypotheses/H13-family-fields/README.md`, `hypotheses/H74-change-detector/README.md`, `hypotheses/H34-idea-cascades/README.md`, `hypotheses/H72-trap-aging-input-starvation/README.md`, `hypotheses/H42-readout-hawkes-kernel/README.md`, `hypotheses/H41-readout-light-cone/README.md`)
*Symbol clashes resolved in this section (qualified names; the card's own symbol in brackets):* E_x^commit (H05) vs E_x^note (H15); chatter dose U_N^chat (H72) vs H69's own tool tokens U and H16's urn rulers U-tok, U-call, U-entry, U-rec; aging share ε_age(M) (H72 "ε(M)") vs H40's cadence elasticity ε(T) and H48's ε_set; held-out gain G_LL(M) (H72 "G(M)") vs H67's G_H and H05's G_c; θ_crowd (H11 "θ") vs θ_para (H34 "θ"); Λ_read (H41 "Λ") vs H62's reply premium Λ; α_join (H11 "α") vs α_R (H34 "α"); η_habit (H11 "η") vs H40's η; ρ_urn (H16 "ρ") vs H101's ρ_F, H46's ρ_self and H50's ρ_relay; D_NE42 (H34 "D") vs H69's erasure dose D and H74's D3 channel; first-read class M (H15) vs H74's mix channel M; idle self-share f_call (H16, H72 "self-share") vs H69's chat self-share s_t. H72 round 2 calls H72's idle gate a **wake**; the object is unchanged.
- **Co-edit pair-day; co-edit ratio ρ_coedit** (H05): a pair-day on which both agents make DQ4 agent work commits (canonical, not imported, agent author, not automated) to a common repository. ρ_coedit = the co-edit share of cross-room pair-days ÷ that of within-room pair-days, per two-room window.
- **Commit-response coupling E_x^commit** (H05): commit spins e_i(t) ∈ {0, 1} per 5-min bin; r_i(t) = 1 if i commits in bins t+1…t+6. E_ij = ½[corr(e_j, r_i) + corr(e_i, r_j)]; E_x = E minus the cross-day surrogate (same pair, other days of the same ISO week, aligned by minute of the window). Pair-days need ≥ 2 occupied bins per agent. Written E_x in H05.
- **Leak conductance (matched placebo) G_c − P0** (H05): for a novel repository born in one room, candidates b are agents in another room at its birth. G_c = P(b adopts within W = 2 h after its first exposure through channel c): command output (`how == output`), history search (`ans_rids`; query-named exposures dropped) or chat relay. Adoption = b's first deliberate use (`how` ∈ {url, bare}) while outside the home room. P0 = the same agent's adoption rate, at the same moment, of up to 20 placebo items (novel repositories from another room, age within ×2, not adopted, not exposed through any channel up to t + W). Lift = G_c / P0. Exposures with less than W of follow-up are dropped.
- **Intraday topic shift r1w** (H36): per 30-min window w (`agent_win30`, restatements removed, ≥ 3 speaking agents), m̄_w = mean of the speakers' centered unit raw vectors; D(w) = 1 − cos(m̄_w, m̄_ref), with m̄_ref the mean of the previous 4 scored windows (crossing day edges). r1w = robust z of D(w) against the previous 16 scored windows (`TRIM_C` scale, 10-window floor). Alarm at r1w ≥ 3; a kickoff hit is an alarm in windows 0–1 of day 0. A within-day variant of R1. *Instrument, not a model (2026-10-07): see "Instruments (not models)" at the end of this file.*
- **Synchronous action-mix shift z_R5** (H36): per agent-day, the Jensen–Shannon divergence of the tool mix and of the bash grammar to the agent's own pooled previous ≤ 10 active days, standardized by 50 multinomial draws at the day's count (u-score), and the binomial z of the context-boundary rate. Day score = median u over ≥ 3 agents; channel z = trailing robust z (10 days); z_R5 = max of the three (the rate as |z|). Alarm at z_R5 ≥ 4. Not H74's z_M.
- **Fixed-sample activity statistic Z_act_inv** (H36): the four activity members (I_act, I_beh, χ_act, C_act) on K = 20 random subsets of n_s = 4 present agents in non-overlapping 120-min all-present blocks, each against 10 circular-shift surrogates; excess averaged over subsets and blocks, then trailing z and the mean of the four z.
- **Idle self-share f_call; urn rulers** (H16, H72): f_call = own idle calls ÷ own calls earlier in the context segment (U-call, primary for the urn). Variants: U-tok (token share n_rep τ_I / (B_L + n_rep τ_I + n_act τ_A + R) on H45's lab ruler), U-entry (n_rep / (n_rep + n_act + k), k room items in context), U-rec (idle calls among the last 10 entries). **Pólya urn (escape):** logit or cloglog P(escape) = α_i + β_urn ln(1 − f); the urn predicts β_urn = 1. Not H69's chat self-share s_t.
- **Absorbed aging share ρ_urn** (H16): 1 − β_a / β_a0, the share of the trap-age slope that ln(1 − f) removes. Written ρ in H16.
- **Forced reset inside a trap** (H16): a context reset forced at the 41-call cap at a wake inside a pause-chain trap (voluntary otherwise). Reset and kick models include ln(wake index); without it a per-trap frailty world fakes a step.
- **Spell kind at start** (H16, H72): fixed from data before the spell only. H16 (TS1r): consolidation-start if a consolidation call starts within 60 s of the spell; else the first declared idle in the first 180 s (pause, wait, silent); crossed with the last active row (failure, talk, other work). H72 (wakes): consolidation-start if a summary call starts within [−30 s, +60 s] of the end of the last sustained run; such traps leave the primary sample. **Trap kind** (H16): the last active call before the trap failed, talked or worked.
- **Wake; timer wake; wake index k** (H72): a wake is H72's idle gate (a call whose previous call was idle). A timer wake is a wake at pause expiry (`gap_kind` = pause; 94% of G51 wakes). k = k_sus, with 1 the first wake after the last sustained run (H60's gate index).
- **Chatter dose U_N^chat** (H72): undirected items read at the N calls before a wake; primary N = 5, entered as ln(1 + U5). The rate form ln λ_u divides by the window length. Written U5 in H72.
- **Aging share explained ε_age(M); held-out gain G_LL(M)** (H72): G_LL(M) = LL(B+M) − LL(B), a day-blocked held-out log score (5 interleaved day folds, agent FE refitted per fold) in nats per 1,000 wakes. ε_age(M) = 1 − [LL(B+M+A) − LL(B+M)] / G_LL(A), with A the clocks ln(trap age) and ln k. Read only where G_LL(A) > 0 with CI above 0. **Transfer score TG(M):** M's slopes from G51 as a fixed offset in another period, base refitted. Written ε(M), G(M) in H72.
- **First-read class L / M / Gp / Gn** (H15): defined identically at forced erasures and pseudo-erasures. L = a read call in calls 1–2 that touches a file object of calls −10…−1; M = ≥ 1 new agent or human chat item received in calls 1–2; Gp = a notes read or history search in calls 1–2; Gn = the latest consolidation note (≤ 24 h) names the repo touched most in calls −10…−1. **RR_class** = exp(b_class×F) in a Poisson model with stratum × arm FE (stratum = agent × period) and log(1 + V_pre).
- **First-read dip share η_first** (H15): the model's predicted forced/pseudo output ratio (work commits, calls 6–20) with "L or M in calls 1–2" set on for every forced erasure vs off, as a fraction of the dip with it off.
- **Note recall r(n, X); window-swap excess E_s^note; e_note** (H15): r(n, X) = Σ_{w∈n} w·1[w ∈ X] / Σ_{w∈n} w over a consolidation note's terms (hashed; IDF weight over the unit's notes) against the action terms X of a window. E_s^note = r(n_a, X_a) − mean r(n_a, X_a′) over ≤ 3 post windows of the same agent ≥ 3 PT days away (primary; e_note is its pooled value). E_x^note uses ≤ 3 other agents' notes instead (biased +0.035). Novel-term variants keep terms absent from the closing segment and the previous note.
- **Join; recruit vs birth; choice set** (H11): a join is agent i's labelled window whose project X differs from i's previous labelled project in the period (carried over unlabelled windows and nights); the first labelled window is an entry, not a join. Recruit: X already holds ≥ 1 labelled agent-window before the join window; birth otherwise. Choice set C(i, w) = projects with ≥ 1 earlier labelled window in the period, minus i's previous project. Labels: work (DQ4 commits) or attention-action (`project_states`, strict mentions), W = 30 min.
- **Active-time clock** (H11): the period's calendar windows (`win_start`–`win_end` per day) concatenated; lookbacks cross nights in active time only.
- **Attachment exponent α_join; co-arrival kernel** (H11): conditional logit over C(i, w) with u_Y = α_join·log a_Y·[a_Y > 0] + β₀·[a_Y = 0] + γ·log(1 + s_Y) + η_habit·h_Y; a_Y = others' labelled windows on Y in the previous 4 windows, s_Y = the period-to-date count, h_Y = habit (return). α_FE adds project fixed effects; α_lead adds others' windows in the next 4 windows. A kernel with lag − lead ≈ 0 is a **co-arrival kernel**: agents arrive at a project in the same hour, not after earlier activity.
- **Crowding exponent θ_crowd** (H11): Poisson regression of total agent-work commits to project X in a window on n_Xw^θ with project and day FE; n is attention-defined (watchers included). Output per agent ∝ n^(θ−1). Written θ in H11.
- **Family field W3 (within-agent style map)** (H13): each statement's features S20g + FW50g (20 style features and 50 function-word rates, both genre-controlled with agent FE, genre kept) are mapped onto the statement vector by B̂ fitted on agent-demeaned data, then removed from the full vectors; residuals are renormalized and pass the round-1 T_field pipeline. **ρ_ns** = RE T(W3) / RE T(L0). The pooled map P is biased (−0.046 under a style-only world).
- **Read-out pull, same vs cross lab J^c_1,same / J^c_1,cross; Δ_J^adj** (H13): H50's matched-age content jump J^c_h at h = 1 split by sender lab = recipient lab; m′ = two random same-sender statements ≥ 2 h away. Δ_J^adj = Σ_s w_s (J_same,s − J_cross,s) over named / unnamed strata (ledger `ment`), w_s the unit's share of hop-1 rows. A partition of J^c_1.
- **Newcomer lab alignment a_lab(d); room outsiderness r(d)** (H13): a_lab(d) = cos(v_{j,d} − m_d, h_own) − mean over other candidate labs g of cos(v_{j,d} − m_d, h_g), with v the joiner's day vector (mean of 5 random statements, 20 draws), m_d the incumbents' day mean and h_g lab g's incumbent field. r(d) = cos(v_{j,d}, m^room_d) − incumbents' leave-self-out mean. Written a(d) in H13; not H83/H88's g_new.
- **Operator-counter persistence score D3** (H74): log1p daily counts of pause/resume bookends, nudges and human messages; robust trailing z (10 days, trimmed SD / 0.70, floor 0.1); persistence p_f(t) = min(|z_f(t − 1)|, |z_f(t)|), dated on day t; D3 = max over the three. Replaces the six-feature drive channel z_D.
- **LOPO conformal threshold** (H74): for goal period g and channel k, θ_k(g) = the ⌈(1 − α)(n + 1)⌉-th smallest of channel k's scores on the placebo days of all other periods (α = 0.02; placebo = baseline index ≥ 10, not a return from a reserved gap, ≥ 2 active days from every catalogued event). Every FAR is then out of sample. With n ≈ 60–81 the rule is "above every training placebo day".
- **Accumulating retirement rule (format markers)** (H74): each consecutive absent scored day of a marker (present on ≥ 8 of the previous 10 scored days) adds log P(0 answers with the marker) under a beta-binomial with the frozen baseline share and ρ = 0.07; alarm when the sum ≤ log 10⁻³. **Appearance rule:** a marker on ≤ 2 of the previous 10 days appears in ≥ 3 answers from ≥ 2 agents.
- **Idea (H34 embedding rule); paraphrase threshold θ_para** (H34): online leader clustering of non-reserved chat messages (≥ 40 characters, DQ5 raw unit vectors): a message is a use of every existing seed with cos ≥ θ_para, else it founds a new seed (a new idea). Seeds never move. θ_bge = 0.90 (0.85, 0.95 sensitivity); θ_gte rate-matched (0.877, 0.820, 0.937). A variant of "Idea (H34 marker rule)".
- **Branching ratio (gamma-mixed) Γ-FN; offspring ratio ρ_off** (H34): idea i draws R0_i ~ Gamma(shape α_R, mean μ); each of its trees is a finite-N Galton–Watson tree with Poisson offspring and depletion on N_fit = max(N_room, s_max), with an exact size law (dynamic programming). CV² of R0 = 1/α_R; α_R → ∞ is one R (FN-GW). ρ_off = mean offspring of non-root nodes ÷ roots; idea-level mixing gives 1.2–2.3, node-level NB ≈ 0.8.
- **Source-based branching ratio R̂_src** (H34): for a group of agents, (agent first uses whose parent is a group member) ÷ (first uses by group members); per pair r_pair = R̂_src / (N − 1). **D_NE42** = DiD(merge) − DiD(split) of Δ ln R̂_src between #best and #rest groups. Written D in H34.
- **Call-skeleton null (message streams)** (H42): per unit, 8 synthetic message streams on the real call skeleton with no coupling: each call talks at its real agent × day × class rate, a talking call posts one message at its `t_first`, recipients are the room's other agents and the visibility rule assigns reads; named and cold flags are drawn at real shares. Real outcomes are regressed on these reads; the excess J − mean(J_null) is reported. Extends H67's regime-I call-skeleton null to all regimes.
- **Thread / cold named message** (H42): named = `chat_mentions_clean.mentions_roster` contains the recipient. Thread = in an exchange with the recipient already in progress: the DQ2 parent is the recipient's message, or the recipient posted in the 30 min before (same day) a message that names the sender or has a DQ2 parent by the sender. Cold = named and not thread.
- **Two-layer read-out jump J_{O,X}** (H42): on receiving call c with window w_c = min(t_first − t_call, t_call − t_call,prev, 120 s), J_{O,X} = β(R^m_X) − β(P_X), with R^m_X the class-X items read at c and posted in (t_c − w_c, t_c) and P_X those posted in (t_c, t_c + w_c), in agent × day × call-class cells. Outcomes are decided by call c (talk, pause, log gap) or are the class of call c + 1 (chat next). A symmetric-window variant of H67's J₁*.
- **Cox-field baseline; survival** (H42): the common intensity is one free log-rate per (day, 10-min bin) (room field: per day × room × bin), fitted jointly with the cross terms; held-out days refit the field. Survival = n_x(Cox field) / n_x(round-1 within-day shape). Real call-scale coupling survives at ≈ 0.67 in synthetic worlds; a field at ≈ 0. Corrected n_x = n_x / 0.75. *Instrument, not a model (2026-10-07): see "Instruments (not models)" at the end of this file.*
- **Ordered read; post-use read placebo; Λ_read** (H41): for a cross-room robustly acausal adoption (item, adopter a, t0, t_use), W = artifacts the source wrote in [t0 − 6 h, t_use) (commits with file paths, pushes or deploys, links in the source message). An ordered read is a matching read by a (pull, page, file or api; or a local read of a source-committed path) with max(t0, t_w) < t_r < t_use; the placebo is a matching read in (t_use, t_use + Δ], Δ the active length of (t0, t_use]. OR_ord and OR_post are Mantel–Haenszel odds ratios against the item's other at-risk cross-room agents at the same moment; Λ_read = OR_ord / OR_post. Written Λ in H41; not H62's Λ.

---

## Instruments (not models)

Added 2026-10-07. An instrument measures or decides something about the swarm. It does not say how the swarm works, so it has no folder in `physics-models/`. A card that uses one still names a model for its claim. Where an entry is already defined in this file, this section points to it, and that entry carries an "instrument, not a model" note.

- **Markov state model (soft metastable sets)** (H17): a Markov chain on discretized behavior states, with implied timescales from the eigenvalues of its transition matrix and PCCA+ groups of metastable states. Defined above as "MSM (soft, shifted estimator)" (RE-B1). H17: behavior is not Markov at the window scale, the slowest mode is agent-day scale, and t2\* orders periods with the wrong sign (refuted; 13 mixed, 14 failed of 27 periods in round 1). The MSM describes the kinetics of any state space; it is not a model of the swarm.
- **Driver-node controllability ranking** (H29): rank agents by the summed squared swarm response to a unit input at each agent, under a fitted linear pull network (Liu–Slotine–Barabási framing). Defined above as "Driver score (mean-output Gramian)" and "Net reply current" (H29). H29: the content-pull driver score does not predict the held-out 2-h spread (pooled ρ 0.09 [−0.08, 0.27]); the reply-graph score does weakly (0.23 [0.05, 0.39] bge, 0.12 [−0.06, 0.29] gte; defined in round 1b). It ranks agents for an operator; it is not a dynamics.
- **Restless-bandit / Gittins index policy** (H60): choose which idle agent to nudge by an index of its state (trap age, call count in the trap, time since its last directed read). Defined above as "Nudge index ν(x)" (H60, the myopic Whittle-subsidy index), with a Gittins-style one-per-trap variant. H60: a nudge read by an idle agent adds 7.2 [5.0, 9.8] active calls in 30 min (G51); once-early beats the logged nudger ×1.55 [1.25, 1.81], and neither index beats once-early (ratios ×0.69 and ×0.96). It is a policy evaluation, not a swarm model.
- **Assembly index** (H80): the minimum number of joining steps that builds a string from its parts. H80 uses the Re-Pair grammar size as an upper bound ("Assembly proxy (Re-Pair grammar size)" above; exact in 97.6% of validation strings). H80: it adds nothing over compression for telling agent from automated commits (ΔAUC −0.007 to +0.001); a timing baseline separates them (AUC 0.92–1.00). Assembly theory is listed under model 15; here it is only a string statistic.
- **Mean-field inversions of the kinetic Ising model (nMF, TAP, Mézard–Sakellariou)** (H124): closed-form estimates of couplings J and fields h from means and lagged correlations. nMF is the first-order Plefka expansion: J_i = B_i / (1 − m_i′²). TAP is the second-order expansion (Roudi & Hertz 2011†), solved by fixed point; it has no solution when its bracket is ≤ 0. MS is the Mézard–Sakellariou Gaussian-field inversion. Exact maximum likelihood is the reference. H124 (N = 4, per-call talk clock): the inversions match ML within 10% only when self-coupling is weak (max J_ii ≤ 0.6, 1/9 units); with persistent own states TAP fails on 25–75% of rows, MS overshoots |J| up to ×3.8 and nMF shrinks it. *Name note:* the model map called this entry "TAP / Sessak–Monasson". H124 tests Mézard–Sakellariou, not the Sessak–Monasson small-correlation expansion of the equilibrium inverse Ising problem.
- **Change and topic-shift detectors** (H74; H36 round 2): alarms that date a step change from daily or 30-min statistics against a trailing baseline. Full definitions in this file: "Change-point alarm (multi-channel)" and "Schema-diff alarm z_S" (H66, H74 section); "Operator-counter persistence score D3", "LOPO conformal threshold" and "Intraday topic shift r1w" (round 2, wave 2 section). H74 round 2: out-of-sample per-day false-alarm rate 0.085 [0.04, 0.17], goal kickoff hit 0.57 (p 0.003); scaffold-tool hits at chance. H36 round 2: the topic-shift alarm fires in the first 30 min of talk on 82–85% of kickoffs (vs 7–9% of placebo day starts; AUC 0.92–0.94). They are monitors, not models.
- **Cox-process field null** (H42): a common intensity with one free log-rate per (day, 10-min bin), fitted jointly with the cross terms, so that a shared field cannot pass as cross-excitation. Full definition in this file: "Cox-field baseline; survival" (round 2, wave 2 section). H42: the named read-out kernel survives it (survival 0.90), H03's exponential cross term mostly does not (0.22). It is a null for model 09, not a model.

### Estimators that belong to a model

- **RMT-cleaned correlation, calibrated edge** (H12, H91, H92): the estimator of model [17 · Collective modes](17-collective-modes/), not a stand-alone instrument. Compute the N × N agent correlation matrix in a window. The **calibrated edge** λ₊^cal is the 95th percentile of the top eigenvalue under surrogates that keep each agent's own series and break cross-agent alignment: the trimmed 30-min block shift for spins (size 0.05 for λ₁; H12 round 1b, DQ8) or independent within-day circular shifts for content (H92, 49 surrogates). Eigenvalues above the edge are modes. **Clipping** (H92's E5) replaces the eigenvalues at or below the edge by their mean (trace kept) and rescales to unit diagonal. The naive Marchenko–Pastur edge λ₊ = (1 + √(N/T))² is a variant only; it ignores autocorrelation and the shared schedule. Uses: H12 (modes above the edge), H91 (eigenvector rotation against a finite-T null), H92 (clipping ties constant-correlation Ledoit–Wolf shrinkage).
