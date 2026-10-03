# Neutral theory of cooperative dynamics

**Citation:** Jordi Piñero et al., *Proc. Natl. Acad. Sci. U.S.A.* 122, e2515423122 (2025). DOI: 10.1073/pnas.2515423122
**File:** pinero-2025-neutral-theory-cooperative-dynamics.pdf
**Fields:** stat mech, dynamics, sociophysics

## Summary
The authors build a minimal stochastic neutral model in which all species are equivalent but a species can only replicate when it is paired with a different species (cooperation). With a conserved population of $N$ individuals and a migration probability $\mu$ per step for new species entering, they solve the steady state analytically. At high migration the model reduces to Hubbell's neutral theory (log-series abundances). At low migration, frequency-dependent replication (rare species are more likely to be paired with a partner) produces a bimodal abundance distribution with a high-abundance "cooperator core". The core keeps a diverse pool of long-lived species alive even at tiny migration rates, and the authors derive scaling laws for diversity, species count and residence times.

## Key formalism
- State: abundance vector $\mathbf n$, $\sum_i n_i=N$. Each step: with prob. $1-\mu$ pick $A\in i$, $B\in j\ne i$ (no-op if $i=j$), and replace a random $C\in k$ with a copy of $A$'s species; with prob. $\mu$ a new species replaces a random individual.
- Diversity: Simpson index $\lambda(\mathbf n)=\sum_i (n_i/N)^2$; $1/\lambda$ = effective number of species.
- Representative species is a birth-death process with $b_n=(1-\mu)\tfrac nN(1-\tfrac nN)^2$; the others enter only via $\lambda^\circ$ (mean-field, self-averaging).
- Steady state: $P_n\propto \dfrac{(1-\mu)^n}{n}\,e^{-(n-N\lambda^*)^2/2N}$, a log-series times a Gaussian "core" centered at $N\lambda^*$. Self-consistency: $\tfrac1\mu=\sqrt{\pi N/2}\,\mathrm{erfcx}\!\big(\sqrt{N/2}(\mu-\lambda^*)\big)$.
- Regimes: low migration $\lambda^*\approx\sqrt{-\ln(2\pi N\mu^2)/N}$; bimodal below $\mu_B=e^{-2}/\sqrt{2\pi N}$; log-series onset $\mu_L=\sqrt{2/(N\pi)}$; high migration $\lambda^*\approx 1/(N\mu)$.
- Dynamics: infiltration probability $\beta\approx\lambda^*$; $\tau_{core}\approx 1/\{\mu\lambda^*[\lambda^*-(N\lambda^*)^{-1}]\}$; $\tau_{out}\approx -N\ln\lambda^*/(1-\lambda^*)$; two clusters in (max abundance, residence time).
- Link to hypercycles and to higher-order contagion models (noted in the Discussion).

## Mapping to agent swarms
- "Individuals" ($N$ conserved): agent slots (each active agent holding one current project) or recent messages in a rolling window. "Species": project or topic clusters from `computer_use_sessions.session_goal`, `agent_memories.content`, or `chat_messages.content` (embedding plus clustering). A stretch: $N$ is only ~10-30 agents unless you use messages or sessions as individuals.
- Cooperative replication: an agent on project $i$ interacts (same `room_id`, close in `event_index`) with an agent on project $j\ne i$ and recruits a third agent to $i$. Same-project interactions do nothing, which is the source of the frequency dependence.
- Migration $\mu$: a genuinely new topic or goal entering from outside. Candidates are `village_goals` changes (~46 goals), new agents in the roster (join dates in `CHANGELOG.md`), and human `USER_TALK` requests.
- Abundance distribution $P_n$: histogram of agents or sessions per topic per window. Core vs. non-core species: persistent projects vs. one-day topics.
- Residence time: first to last appearance of a topic cluster. Max abundance: peak number of agents on it.
- `chat_rooms` (5) break the well-mixed assumption, and the paper predicts lower core abundance in spatial structure.

## Candidate hypotheses
- In stable periods (no goal change, no roster change) topic abundances are bimodal with a persistent core, while right after goal switches or joins they look log-series. Observable: per-window abundance histograms and Simpson $\lambda(t)$ vs. the predicted $\lambda^*(\mu,N)$.
- Persistence is two-class: scatter of (max abundance, residence time) for all topics shows two clusters, and the fraction of new topics that reach the core $\approx\lambda$. Observable: topic birth/death tracking over `events` and `chat_messages`.
- Per-capita adoption rate falls as a topic's share grows, consistent with cooperation needing a different partner. Observable: new adopters per carrier regressed on share $n/N$; compare within-project vs. cross-project interactions in `chat_messages`.

## Caveats
- Assumes neutrality (all species equivalent), well-mixed random pairing, conserved $N$, and instantaneous replacement. The village has heterogeneous models, rooms, a roster that changes, and turn-based/serialized activity to verify.
- Results hinge on topic labeling and window size, so report sensitivity.
- Asymptotics (Gaussian core, $\mu_B\propto N^{-1/2}$) are for large $N$; for small $N$ use direct simulation of the stated rules.
- The mapping of "replicate" to "recruit an agent to a topic" is a modeling choice that needs validation, for example against explicit invitations in chat.
- Weekends are skipped and village hours changed (4h to 8h/day), so time bases need care. After 2026-03-24 (perma-computer-use) `computer_use_sessions` boundaries are rare; use `CONSOLIDATE` `nextSessionGoal` as the project label instead.
