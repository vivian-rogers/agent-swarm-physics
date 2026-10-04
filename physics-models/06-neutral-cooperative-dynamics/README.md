# 06 · Neutral theory of cooperative dynamics

**Fields:** stat mech, sociophysics, dynamics
**References:** Piñero et al., "Neutral theory of cooperative dynamics", *PNAS* 122, e2515423122 (2025) (in `literature/`); Hubbell, *The Unified Neutral Theory of Biodiversity and Biogeography* (2001)†.

## The model

N individuals belong to species; all species are equivalent (neutral). Each step:
- With probability 1 − μ: pick two individuals A and B. If they belong to **different** species, a random individual C is replaced by a copy of A's species. If they are the same species, nothing happens. **Replication requires cooperation across species.**
- With probability μ: a brand-new species replaces a random individual (migration or innovation).

Diversity is measured by the Simpson index λ = Σ_i (n_i/N)², with 1/λ the effective number of species.

The steady-state abundance distribution is a log-series times a Gaussian:

$$P_n \propto \frac{(1-\mu)^n}{n}\, e^{-(n - N\lambda^*)^2 / 2N}$$

The Gaussian factor is a **cooperator core** centered at Nλ*. Here λ* is set self-consistently by μ and N.

## Interesting behavior

- **Bimodality from neutrality.** At low migration (μ below μ_B = e^{−2}/√(2πN)) the abundance distribution is bimodal: a mass of rare species plus a core of abundant ones. Nothing distinguishes the core species except history.
- **Rare species do better per capita.** A rare species is more likely to be paired with a different species, so it replicates more per individual. This frequency dependence stabilizes diversity.
- **A diverse, long-lived core at tiny migration.** Classic neutral theory would collapse to one species when migration is low. Cooperation keeps a core alive, with long residence times.
- **Two classes of species.** In a plot of (maximum abundance, residence time), species fall into two clusters: transient ones and core members. The probability that a new species joins the core is ≈ λ*.
- **Regime crossover.** At high migration (μ above μ_L = √(2/(πN))) the model reduces to Hubbell's neutral theory with log-series abundances.

## Mapping to the village

- **Individuals:** agent slots (each agent holds one current project), or sessions, or messages in a rolling window. Agents alone give N ≈ 10–30, which is small; sessions or messages give larger N.
- **Species:** project or topic clusters, from `CONSOLIDATE` `nextSessionGoal` (after 2026-03-24), `computer_use_sessions.session_goal` (before), or chat content.
- **Cooperative replication:** agents on different projects interact, and the interaction recruits a third agent to one of them. Same-project chatter doesn't recruit.
- **Migration μ:** genuinely new topics from outside: goal changes (`village_goals`), new agents joining, human requests (`USER_TALK`).

## How to measure

1. Label projects or topics per window. Build abundance histograms and Simpson λ(t).
2. Estimate μ as the rate of first appearances of new topics. Compare measured λ with the predicted λ*(μ, N).
3. Track each topic from birth to death; plot (maximum abundance, residence time) and look for two clusters.
4. Test frequency dependence: regress new adopters per carrier on a topic's share n/N.

## Pitfalls

- **Exchangeability fails in the village** (H06, 2026-10-04): in free weeks 79–91% of projects are held by one agent, and NCD, Hubbell and herding all fail joint posterior-predictive checks in 27/30 fits. Add agent-specific innovation fields before comparing copying models. Finite-N λ sits well below the asymptotic λ\* at low μ (0.52 vs 0.75 at N = 13, μ = 0.003): use simulated λ. A two-moment fit is weakly identified along a μ–k ridge. `hypotheses/H06-neutral-cooperative-dynamics/analysis/ncd_core.py` is a reusable exact finite-N simulator.
- The model assumes neutrality, well-mixed pairing and constant N. The village has different model families, chat rooms, and a changing roster.
- Results depend on topic labeling and window size; report sensitivity to both.
- For small N, simulate the stated rules directly rather than using the large-N asymptotics.

## Hypothesis seeds

- In stable periods (no goal or roster change), topic abundances are bimodal with a persistent core; right after goal switches they look log-series.
- Topics fall into two persistence classes, and the fraction of new topics that reach the core ≈ λ.
- Per-carrier recruitment falls as a topic's share grows.
