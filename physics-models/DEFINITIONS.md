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

### H29 named variants (2026-10-04; see `hypotheses/H29-driver-nodes/README.md`)
- **Influence coupling (content pull):** the slope a(S) = Σ y·u / Σ |u|² of a recipient's statement step y = x(τ_n) − x(τ_{n−1}) on the offset u = x_m − x(τ_{n−1}) to a message m, over a set S of (message, next-statement) rows. Net pull κ subtracts a cross-day placebo (same sender, another day) and the invisible-row pull.
- **Visibility jump (boundary test):** the field-corrected pull of visible minus truly invisible messages (call window ≤ 30 s), within matched 10-s age bins, named vs named and unnamed vs unnamed. The preferred influence estimator (post hoc in H29).
- **Driver score (mean-output Gramian):** D_k, the summed squared swarm response to a unit injection at agent k under the fitted linear pull network A with leak Γ. Steering energy E_k = N²/D_k.
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
- **MSM (soft, shifted estimator):** a Markov state model on Jev v3 probability vectors (soft occupancies) with the noise-cancelling shifted count estimator; implied timescales t2* and PCCA+ macro states. Needs ≥ ~15k windows per period; per-period verdicts are descriptive below that.
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
- **Change-point alarm (multi-channel)** (H74): Z(d) = max(z_S, z_M, z_O, z_D, z_C) over the schema, mix, oracle-format, drive and content channels. Each z is a trailing z (median and trimmed SD) against the previous 10 non-holdout active days. Alarm at Z ≥ 4; the fused alarm's per-day false-alarm rate is 0.18.

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
- **Nudge index ν(x)** (H60): the expected extra active calls in 30 min that a nudge read at an idle gate buys in state x = (a, k, r), with k the gate index in the trap. It is the myopic (Whittle-subsidy) index. Written ĝ(x) in H60; not the goal field ĝ.
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
- **Assembly proxy (Re-Pair grammar size)** (H80): a_RP = number of Re-Pair rules + (length of the final Re-Pair string − 1), an upper bound on the assembly index. It equals the exact index in 97.6% of validation strings.
- **Scheduler baseline** (H80): an L2 logistic classifier on timing features only (inter-commit gap statistics, second-of-minute, hour of day, share in the village window). It is the first rival for any sequence-based agent-vs-script signature.

### H86 named variants (2026-10-04): Taylor field gauge (see `hypotheses/H86-taylor-law-field-gauge/README.md`)
- **Taylor coefficients (a, c_T, b)** (H86): across the present agents of one unit, V_i = a μ_i + c_T μ_i² for the per-agent mean μ_i and variance V_i of counts per 15-min bin (1 h for commits); b = the slope of ln V on ln μ. c_T ≈ c_× + mean private burstiness, so neither c_T nor b is a field gauge.
- **Taylor field gauge c_×** (H86): c_× = Σ_{i<j} Cov(y_i, y_j) / Σ_{i<j} μ_i μ_j, the variance of a shared multiplicative field without private burstiness. Report `taylor_c_shared` on channel `activity_trim` (and `activity_raw`) from `per_period_estimates`. On talk it counts field plus equal-time coupling.
- **Shared share φ_sh** (H86): c_× Σ_i μ_i² / Σ_i (V_i − μ_i), the share of super-Poisson variance that the shared field carries. Written φ in H86 (`taylor_phi_shared`).
- **Within-day shared coefficient c_×w** (H86): c_× on counts demeaned within agent-day. c_× − c_×w is the day-level field.
