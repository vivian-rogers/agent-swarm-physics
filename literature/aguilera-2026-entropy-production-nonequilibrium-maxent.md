# Inferring Entropy Production in Many-Body Systems Using Nonequilibrium Maximum Entropy

**Citation:** Miguel Aguilera, Sosuke Ito and Artemy Kolchinsky, *Phys. Rev. Lett.* 136, 077101 (2026). DOI: 10.1103/xgkj-dxzh
**File:** aguilera-2026-entropy-production-nonequilibrium-maxent.pdf
**Fields:** stat mech, thermodynamics, info theory

## Summary
Entropy production (EP) measures how irreversible a stochastic process is, but it is intractable to estimate directly for high-dimensional or long-memory systems. The authors give a method that works from samples of trajectory observables (such as time-lagged correlations). It finds the distribution closest to the time-reversed process that matches the forward expectations of those observables; the dual form is a convex optimization problem. This yields a lower bound on average EP, an estimate of trajectory-level EP, a Pythagorean decomposition, hierarchical (pairwise, triplet, ...) bounds, and a higher-order thermodynamic uncertainty relation. It is demonstrated on a 1000-spin disordered nonequilibrium Ising model and on Neuropixels spike trains, where EP is interpreted as statistical irreversibility, not heat.

## Key formalism
- Trajectory EP $\sigma(x)=\ln p(x)/\tilde p(x)$ and average $\Sigma=D(p\|\tilde p)$, with $\tilde p$ the time-reversed process.
- Observables $g(x)\in\mathbb R^d$. Bound $\Sigma_g=\min_q D(q\|\tilde p)$ s.t. $\langle g\rangle_q=\langle g\rangle_p$, satisfying $0\le\Sigma_g\le\Sigma_g^{DPI}\le\Sigma$.
- Dual (convex, unconstrained): $\Sigma_g=\max_\theta\ \theta^\top\langle g\rangle_p-\ln\langle e^{\theta^\top g}\rangle_{\tilde p}$. For antisymmetric $g$ in steady state, only forward samples are needed.
- Optimal $q_\theta=\tilde p\,e^{\theta^\top g-\ln\langle e^{\theta^\top g}\rangle}$ is also the maximum-likelihood fit to forward data; Pythagorean split $D(p\|\tilde p)=D(q^*\|\tilde p)+D(p\|q^*)$, i.e. $\Sigma=\Sigma_g+\Sigma_g^\perp$.
- Trajectory estimator $\sigma_\theta(x)=\theta^\top g(x)-\ln\langle e^{\theta^\top g}\rangle_{\tilde p}$, equal to $\theta^\top[g(x)-g(\tilde x)]/2$ when $g$ is antisymmetric and the system is stationary.
- Hierarchy $\Sigma_1\le\Sigma_2\le\dots\le\Sigma$ by interaction order; Gaussian/Newton-step bound $\hat\Sigma_g$; TUR $\Sigma\ge\ln(1+2\langle g\rangle^\top K^{-1}\langle g\rangle)$.
- Multipartite dynamics (one unit updates at a time) splits the problem into $N$ independent ones. Observables: $g_{ij}=(x_{i,1}-x_{i,0})x_{j,0}$ (multipartite), or $x_{i,1}x_{j,0}-x_{i,0}x_{j,1}$ (parallel updates).
- Results: $\theta_{ij}-\theta_{ji}\approx\beta(w_{ij}-w_{ji})$ recovers coupling asymmetry; EP grows superlinearly with neurons and is largest in the active behavior condition.

## Mapping to agent swarms
- State $x_{i,t}\in\{-1,+1\}$: whether agent $i$ acted or spoke in time bin $t$ (from `events` `AGENT_TALK`, or `chat_messages.agent_speaker_id` and `created_at`), per `room_id`. An alternative discrete time is `events.event_index` (canonical ordering). One could also use a categorical state such as action class or topic cluster.
- $p$ vs. $\tilde p$: the real activity sequence vs. the time-reversed sequence over the same window. $\Sigma_g$ is the measurable lower bound on the swarm's temporal irreversibility; this is the most directly computable quantity among the seven papers.
- $\theta_{ij}$, the inferred asymmetric coupling, is a directed influence network among the ~30 agents (who follows whom).
- Multipartite check: `villages.active_agent_id` and `turn_id` suggest a turn pointer. If activity is effectively one-agent-at-a-time, use the multipartite form; otherwise use the antisymmetrized form. This must be verified in the data.
- EP normalized by expected activity (the paper's $R$) is comparable across eras: rooms v1 (2026-02-25), perma-computer-use (2026-03-24), nudger, village hours.
- It is a stretch to call this dissipation: there is no heat bath. Irreversibility is a statistical, information-theoretic measure, as in the neural example.

## Candidate hypotheses
- Swarm activity is measurably irreversible ($\Sigma_g>0$ on held-out data) relative to time-shuffled and block-shuffled surrogates, and higher in coordination-heavy periods (e.g., "organise an event" goal) than in "pick your own goal" or #rest periods. Observable: held-out $\Sigma_g$ per day or room, with message-rate normalization.
- The inferred antisymmetric couplings give a stable leader-follower hierarchy. Observable: split-half correlation of $\theta_{ij}-\theta_{ji}$ across months, and agreement with lagged cross-correlation sign; test whether hierarchy relates to roster join date or model family.
- $\Sigma_g$ grows superlinearly with the number of agents sampled (as for neurons) and the pairwise term $\Sigma_2$ accounts for most of it. Observable: random subsets of agents, $N=5$ to $\sim30$, normalized by expected activity; compare $\Sigma_1,\Sigma_2$.

## Caveats
- Requires stationarity within the estimation window; the village changes continuously (new agents, scaffolding, hours, goals), so estimates must be windowed with enough samples.
- Time-reversal symmetry needs care for agents whose actions are causally ordered by tool use; "reversed" sequences may not be physically meaningful, and results depend on bin width.
- Discrete binary activity discards content; richer states (topics) increase dimension and need more data.
- Lower bound only: the true $\Sigma$ may be much larger, and $\Sigma_g=0$ does not imply reversibility.
- The paper uses 10^9 samples for the Ising model; the village has ~235k events, so rely on its held-out/early-stopping protocol and surrogates.
