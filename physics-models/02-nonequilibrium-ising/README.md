# 02 · Nonequilibrium Ising (broken detailed balance)

**Fields:** stat mech, thermodynamics, dynamics
**References:** Aguilera, Ito & Kolchinsky, *PRL* 136, 077101 (2026) (in `literature/`); Aguilera, Moosavi & Shimazaki, "A unifying framework for mean-field theories of asymmetric kinetic Ising systems", *Nat. Commun.* 12, 1197 (2021)†; Roudi & Hertz, *PRL* 106, 048702 (2011)†; Manousiouthakis & Deem, "Strict detailed balance is unnecessary in Monte Carlo simulation", *J. Chem. Phys.* 110, 2753 (1999)†; Suwa & Todo, *PRL* 105, 120603 (2010)†; Bak & Sneppen, *PRL* 71, 4083 (1993)†.

## The model

Same binary spins as model 01, but now the **dynamics** is the model, not just the stationary distribution. In the kinetic Ising model, a spin chosen to update takes value s_i' with probability

$$P(s_i' \mid \mathbf s) = \frac{e^{s_i' H_i(\mathbf s)}}{2\cosh H_i(\mathbf s)}, \qquad H_i(\mathbf s) = h_i + \sum_j J_{ij} s_j$$

Two independent ways to break detailed balance:

**1. Asymmetric couplings (J_ij ≠ J_ji).** i influences j differently than j influences i. There is no energy function; the system settles into a nonequilibrium steady state with probability currents. For parallel updates, the steady-state entropy production per step is

$$\sigma = \sum_{ij} (J_{ij} - J_{ji})\, D_{ij}, \qquad D_{ij} = \langle s_i(t+1)\, s_j(t) \rangle$$

So irreversibility comes directly from the antisymmetric part of J weighted by lagged correlations.

**2. Non-random update order, even with symmetric J.** In textbook Monte Carlo, a random site is picked each step, and detailed balance holds with respect to the Boltzmann distribution. Change how the next site is picked and things break in stages:

| Update rule | Stationary distribution | Detailed balance | Entropy production |
| --- | --- | --- | --- |
| Random sequential | Boltzmann | yes | 0 |
| Fixed-order sweep (1, 2, …, N, 1, 2, …) | still Boltzmann | **no** | > 0 |
| Parallel (all at once) | not Boltzmann; 2-cycles possible at low T | no | > 0 |
| State-dependent order (who updates depends on the configuration) | generally not Boltzmann | no | > 0 |

The fixed-order sweep is the subtle case. Each single-site update satisfies detailed balance on its own, so the sweep preserves the Boltzmann distribution (global balance). But the sweep is not its own time reverse: reversing it gives the sweep in order N, …, 1. Snapshots look exactly like equilibrium, yet trajectories have a direction. Only time-lagged statistics can reveal it.

## Interesting behavior

- **Equilibrium-looking statics, nonequilibrium dynamics.** As above. Model 01 fitted to such a system would look perfectly fine and miss the irreversibility entirely.
- **Directed influence as broken symmetry.** The antisymmetric part J_ij − J_ji is a leader/follower structure. It can be recovered without a model: the Aguilera–Ito–Kolchinsky nonequilibrium maximum-entropy estimator gives θ_ij − θ_ji ≈ β(J_ij − J_ji) from lagged correlations alone.
- **Self-organization from scheduling.** Extremal update rules ("always update the least stable unit") are the mechanism behind Bak–Sneppen self-organized criticality: power-law avalanches with no tuning. Whether LLM-agent scheduling (respond to whoever addressed you, react to whatever is most urgent) produces an analog is open.
- **Asymmetric disorder kills glassiness.** Fully asymmetric random couplings destroy the spin-glass phase; the dynamics becomes noisy and has no stable memory states. In swarm terms, purely one-directional influence may prevent stable factions.
- **Hierarchy of irreversibility.** The entropy-production lower bounds from single-spin, pairwise and triplet observables satisfy Σ₁ ≤ Σ₂ ≤ … ≤ Σ. The gaps tell you which order of interaction produces the arrow of time.

## Mapping to the village

- **Spins:** as in model 01, on a finer time grid, or in event time using `events.event_index` (see Activity time in `../DEFINITIONS.md`).
- **Update order is a measurable property of the scaffolding.** The village has a turn pointer (`villages.turn_id`, `active_agent_id`), agents can choose to `WAIT` or `PAUSE`, and an auto-nudger pokes idle agents. The questions are concrete:
  - Is the order random sequential, round-robin (fixed sweep) or state-dependent?
  - Does who acts next depend on who was just addressed in chat? That would make the order state-dependent.
  - The answer decides whether detailed balance can hold at all, before looking at agent behavior.
- **Multipartite vs. parallel.** If effectively one agent acts at a time, use the multipartite form of the Aguilera estimator, with observables g_ij = (s_{i,t+1} − s_{i,t}) s_{j,t}. If several act at once, use the antisymmetrized parallel form.

## How to fit

1. **Kinetic Ising, maximum likelihood.** Each spin's transition probability is a logistic regression on the previous configuration. The likelihood is exact and convex, with no partition function, so this is easier than model 01.
2. **Model-free entropy production.** Run the Aguilera–Ito–Kolchinsky estimator on held-out data. It gives a lower bound on Σ and an inferred θ_ij.
3. **Scheduler audit.** Before either, characterize the update rule empirically: the distribution of who acts next given the current state.

## Nulls and controls

- **Time reversal:** reverse each window and refit. A time-symmetric process gives the same parameters.
- **Block shuffles:** shuffle whole blocks of time bins. This keeps short-range statistics and destroys long-range order.
- **Synthetic check:** simulate the kinetic Ising model with known J and the village's empirical update order, and confirm the estimator recovers J.

## Susceptibility, response and effective temperature

- **Response function.** R_ij(t, t′) = ∂⟨s_i(t)⟩/∂h_j(t′): how much agent i's state at time t moves after a small push on agent j at t′. In a fitted kinetic Ising model it can be computed exactly, by propagating a small field perturbation forward. Linearized, for parallel updates: δm(t+1) ≈ D(t)[δh(t) + J δm(t)], with D = diag(1 − m_i²). The static susceptibility is χ = Σ_t R.
- **Measured response.** Use event-triggered averages after kicks that actually happened, compared with matched times without a kick:
  - nudger messages (NE10; switched off and on in NE23);
  - human messages (`USER_TALK`);
  - goal kickoffs (NE34), which are step fields on everyone;
  - fields targeted at one agent (#48 = NE37, NE38), whose effect on the *other* agents gives off-diagonal R_ij;
  - changes that hit one family only (NE05, NE06, NE20), whose effect on the other families gives a cross-susceptibility between sublattices.
- **Fluctuation–dissipation violation.** In equilibrium the response equals the time derivative of the correlation, R(t, t′) = ∂_{t′} C(t, t′) (temperature absorbed). Define X = R / ∂_{t′}C and an **effective temperature** T_eff = 1/X. Plot integrated response against correlation: slope 1 means equilibrium, and a different slope gives T_eff (Cugliandolo, Kurchan & Peliti, *PRE* 55, 3898 (1997)†). X ≠ 1 measures distance from equilibrium and complements the entropy-production estimate above.
- **Link to model 09.** Hawkes kernels are linear response functions for event rates. The total response to one outside event is 1/(1 − n), where n is the branching ratio, so it diverges as n → 1.
- **Caveats.**
  - Kicks have no natural units, so compare relative χ across agents, families and periods.
  - Kicks aren't random: the nudger targets idle agents, so use matched controls.
  - Overlapping kicks need deconvolution, e.g. a Hawkes fit.

## Mean-field forward version

- **Mean-field Glauber dynamics:** τ₀ dm/dt = −m + tanh(β(J₀ m + h(t))). Linearized, the relaxation time is τ = τ₀ / (1 − βJ₀(1−m²)), which diverges at criticality. The βJ₀ from fluctuations (model 01, Curie–Weiss inversion) should *predict* the decay of measured responses to kicks: a forward consistency test with no J matrix. HH81.
- **Leader–follower mean field:** one leader spin σ_L coupled to a follower population m_F, with τ₀ ṁ_F = −m_F + tanh(β(J_ff m_F + J_lf σ_L + h)). Two or three parameters capture directed influence; compare the fitted J_lf across weeks. HH83.
- **Entropy production in mean field:** for the two-population model, the irreversibility comes from J_lf ≠ J_fl, so it can be predicted from the fitted parameters and compared with the model-free estimate.

## Pitfalls

- **A pure output dip leaks into composition statistics** (H44, 2026-10-04): after a reset, raw call-mix shares change even with no re-acquisition (Markov and agent-mix spillover); condition on agent × previous state. Entropy is not a temperature signature under a field quench (it fell slightly after forced erasures).
- **Field and coupling separate by channel, not regime** (H50, 2026-10-04): activity co-movement is a scheduler field (start/stop edges explain ~0.6–0.7; within the all-present window per-pair correlation is 0.005–0.056), while talk co-movement is a coupling gated at exactly the recipient's next call (hop 1). A hop-1 minus hop-0 difference fails under a common drive (the call in flight at a message tends to be a long one), two-sided peer regressions remove co-movement mechanically, and day cross-fitting adds spurious co-movement; use a shifted-input null and gated kernels.
- **EP does not fingerprint the platform, and resets leave transients** (H56, 2026-10-04): turn-level entropy production did not jump at 32 documented scaffold changes or at NE14b (t −1.33, inside the spread of ordinary days); goal kickoffs and tool-use style move it more, and family differences survive scaffold removal. After every scaffold reset, drop a burn-in (3 transitions) or the relaxation transient reads as a change. Count matching by subsampling does not equalize the bias of the plug-in or cross-fitted estimators; the Newton bound is robust to count changes.
- **Field vs catalyst is convention-dependent, and transients mislead** (H39, 2026-10-04): splitting a lever's rate change into an occupancy shift and a catalytic part depends on how the change is divided between forward and backward rates, and |K| < 0.10 is not interpretable. A pure catalyst lowers the 30-min idle share while the stationary share stays put (the transient fallacy): measure stationary occupancy, not short-window shares.
- Nonstationarity within a window (new agents, goal changes) can masquerade as irreversibility. Use windows within one regime (`../DEFINITIONS.md`, Regime).
- Bin width changes everything: too coarse merges cause and effect into the same bin and hides the arrow of time.
- Causally ordered tool use (open a file, then edit it) is trivially irreversible inside one agent. Decide whether that counts as signal or as nuisance before measuring.

## Hypothesis seeds

- The village's update order is state-dependent: the probability that agent j acts next rises sharply after j is mentioned. Detailed balance is therefore broken by the scaffolding alone.
- Swarm activity is irreversible (Σ_g > 0 vs. block-shuffled surrogates), and more so in coordination-heavy goal periods.
- The antisymmetric couplings give a stable who-follows-whom hierarchy that persists across months, and correlates with model family or join date.
- Model 01 fitted to the same data reports good pairwise sufficiency, while model 02 reports substantial entropy production: equilibrium statics, nonequilibrium dynamics.
