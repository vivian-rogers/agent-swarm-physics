# 15 · Stochastic thermodynamics of selection: excess, housekeeping, speed limits and replicator closure

**Fields:** thermodynamics, stat mech, origins of life, info theory
**References** (notes in `../../literature/`):
- Kolchinsky, Dechant, Yoshimura & Ito 2026, excess/housekeeping split and speed limits: `kolchinsky-2026-generalized-free-energy-excess-housekeeping.md`.
- Aguilera, Ito & Kolchinsky 2026, entropy-production inference by nonequilibrium max-ent: `aguilera-2026-entropy-production-nonequilibrium-maxent.md`.
- Kolchinsky 2025, thermodynamics of Darwinian selection: `kolchinsky-2025-thermodynamics-darwinian-selection-replicators.md`.
- Kolchinsky 2024, dissipation does not bound replicator rates: `kolchinsky-2024-dissipation-does-not-bound-replicator-rates.md` (model 05).
- OoLEN 2026, replicator growth order, RAF and COT background: `oolen-2026-origins-of-life-review-part2-theory.md`.
- Hordijk 2023, RAF and CAF sets: `hordijk-2023-raf-sets-formal-definition-algorithm.md`.
- Mathis, Bhattacharya & Walker 2017, emergence of selection as a first-order transition: `mathis-2017-emergence-of-life-first-order-transition.md`.
- Sharma et al. 2023, assembly theory: `sharma-2023-assembly-theory-selection-evolution.md`.
- Abrahão et al. 2024, assembly index as LZ-type compression: `abrahao-2024-assembly-theory-lz-compression-critique.md`.
- From memory, not in `literature/`: Hatano & Sasa 2001†; Maes & Netočný 2014†; Hordijk & Steel 2004† and Mossel & Steel 2005† (RAF and CAF originals); von Kiedrowski 1986† and Szathmáry & Gladkih 1989† (parabolic growth); Eigen 1971† (error threshold, hypercycle); Dittrich & Speroni di Fenizio 2007† (chemical organization theory); Lempel & Ziv 1976†.

**Related models:** `../05-replicator-dissipation/` (birth–death replicators; Kolchinsky 2024 says dissipation does not bound growth and decay). This folder adds the bounds that do hold: excess vs housekeeping, speed limits, and the selection-resolution bound, plus closure (RAF) and the assembly-theory claim. `../02-nonequilibrium-ising/` supplies kinetic spins and the pairwise entropy-production bound. `../06-neutral-cooperative-dynamics/` is the neutral null for recruitment.

## The model

The degrees of freedom are occupation distributions and fluxes. A state can be an agent's behavior state, an agent's repo allocation, or a repo's host count. Fluxes are transitions between states counted over the agents of one unit, treated as exchangeable copies of a mean-field master equation. Entropy production here is statistical irreversibility in nats. It is not heat: there is no temperature and no local detailed balance linking tokens to ln(j/j̃).

**1. Entropy-production inference (Aguilera 2026).** For trajectory observables g with forward process p and time reverse p̃:

$$\Sigma\;\ge\;\Sigma_g=\max_\theta\;\theta^\top\langle g\rangle_p-\ln\langle e^{\theta^\top g}\rangle_{\tilde p}$$

- The optimal θ recovers coupling asymmetry: θ_ij − θ_ji ≈ β(w_ij − w_ji).
- A hierarchy Σ₁ ≤ Σ₂ ≤ … ≤ Σ by interaction order separates single-agent from joint irreversibility. σ_coll = Σ_joint − Σ_i Σ_i > 0 needs directed couplings (HH311).
- It is a lower bound. Σ_g = 0 does not imply reversibility.

**2. Excess/housekeeping split (Kolchinsky et al. 2026).** Fluxes j, reverse fluxes j̃ and incidence ∇ on a state graph. EP rate σ = jᵀ ln(j/j̃). The generalized free energy restricts the variational formula to gradient observables:

$$\sigma_{\rm ex}=\max_\phi\big[-j^\top\nabla\phi-j^\top(e^{\nabla\phi}-1)\big],\qquad \sigma_{\rm hk}=\sigma-\sigma_{\rm ex}\ge 0$$

(Eq. 38 as written in the notes; the sum runs over one-way transitions including reverses.) Dual form: σ_ex = min_{j′} D(j′‖j̃) subject to ∇ᵀj′ = ∇ᵀj, the cheapest fluxes that produce the same net change.

- **Excess** is the irreversibility of net occupancy change. It is zero once the occupation stops moving. It needs no steady state, unlike Hatano–Sasa†.
- **Housekeeping** is carried by cycles that change nothing. σ_hk > 0 needs a cycle in the state graph: ≥ 3 states or joint states. A binary on/off chain has σ_hk ≡ 0.
- Excess is inferable from short-time increments across copies at a fixed time. Housekeeping can be time-averaged in stationary windows.
- Linear response: σ_ex ≈ ẋᵀH⁺ẋ, with H the short-time diffusion matrix. The integrated excess scales as 1/T under slow driving.

**3. Thermodynamic speed limits (Kolchinsky et al. 2026).** With activity A = Σ j_ρ, Wasserstein distance W between the initial and final occupation, and 𝒜 = ∫A dt over duration T:

$$\sigma\ge\sigma_{\rm ex}\ge\frac{2\dot W^2}{A},\qquad T\;\ge\;\frac{W}{\bar A}\coth\!\Big(\frac{\Sigma_{\rm ex}}{2W}\Big)\;\ge\;\frac{W}{\bar A}$$

On a complete state graph Ẇ = ‖ṗ‖₁/2, so W is the total-variation distance. The bound T ≥ W/Ā is a counting identity: it cannot fail for Markov jumps observed completely. Its content is the slack S = T Ā / W.

**4. Selection resolution (Kolchinsky 2025).** Replicator X with replication rate ρ, fitness f (the invasion growth rate) and affinity per copy σ (in nats; a different σ from item 2):

$$\sigma\;\ge\;-\ln\!\big(1-\rho/f\big),\qquad \text{selection resolves only } s\ge e^{-\sigma^*}$$

- s = 1 − f′/f is the selection coefficient. σ* is the steady-state affinity of the winner.
- Resolving a fitness gap s costs at least −ln s per copy. At equilibrium every replicator coexists; at infinite affinity only the fittest survives.
- Operational affinity in the village: σ_j = ln(J⁺_j / J⁻_j), recruitments over departures per net copy.
- The theory excludes spontaneous formation. A host made by the kickoff field is formation, not copying.

**5. Replicator growth order (OoLEN 2026).**

$$\dot n=c\,n^{p}$$

- p = 1/2 (parabolic†): sublinear growth, coexistence of competitors.
- p = 1: exponential growth, survival of the fittest.
- p = 2 (hyperbolic): superlinear, winner-take-all, bistability; the hypercycle regime†.
- Eigen's error threshold† (q^L σ > 1) bounds the length of a copied sequence with per-site fidelity q.

**6. Closure: RAF and CAF sets (Hordijk 2023).** A reaction system Q = {X, R, C, F}: types, reactions, catalysis assignments and a food set.
- R′ ⊆ R is a RAF if every reaction in R′ has a catalyst and all its reactants in the closure cl_{R′}(F).
- The maxRAF is unique and found in polynomial time by pruning. Irreducible RAFs (iRAFs) are minimal.
- A CAF additionally requires that reactions can be ordered so each catalyst is present before use. A RAF that is not a CAF needs an uncatalyzed bootstrap.
- Chemical organization theory† adds self-maintenance: a closed set with some flux v > 0 such that Sv ≥ 0.

**7. Emergence of selection as a first-order transition (Mathis 2017).** In a closed system with recycling, the mass distribution switches abruptly from "set by formation" to "set by selection".
- Order parameter: I(R;E), the mutual information between replicator composition and environment composition. Its sign of change depends on the fitness landscape.
- First-order signatures: exponential waiting times, frustrated (aborted) transitions, and a nucleus that is rarely the final winner.
- The exploration rate of new sequences peaks ≈ 100× at the transition. Transition time is non-monotone in the replication rate: fast replication locks resources in unfit replicators.

**8. Assembly theory and its compression critique (Sharma 2023; Abrahão 2024).**

$$A=\sum_{i=1}^{N} e^{a_i}\,\frac{n_i-1}{N_T}$$

- a_i is the assembly index (the shortest construction pathway with reuse). n_i is the copy number. AT reads high a × high n as selection.
- For strings, a equals the minimal context-free grammar size minus the basis, and the LZ factor count satisfies LZ(x) ≤ a(x) + |B| (Abrahão 2024). The assembly index is therefore an LZ-family compression bound.
- The dispute is open. Cronin and co-authors argue the index differs quantitatively from LZW (not read here).

### Order and control parameters
| Sub-model | Order parameter | Control parameters in the village |
| --- | --- | --- |
| EP inference | Σ_g per agent-hour; σ_coll/σ_joint; θ asymmetry | state resolution, bin width, scaffold regime (H56) |
| Excess/housekeeping | σ_ex/σ (kickoff, day edges); σ_hk per transition | kickoff (a quench), DQ8 trimming, nudger (NE43) |
| Speed limit | slack S = T Ā / W | kickoff field strength, cadence (NE20), roster size |
| Selection resolution | σ* of the top repo on its plateau; s of extinct rivals | host turnover (dilution ϕ), herding vs free weeks |
| Growth order | p | shared-artifact vs own-artifact weeks; kickoff naming |
| RAF | maxRAF share of work commits; iRAF sizes; maxCAF | food set (platforms, kickoff-named artifacts); automata (HH244) |
| First-order transition | I(project topics; kickoff field) step; waiting-time distribution | free vs assigned goals; recruitment rate |
| Assembly vs compression | AUC gain of a over LZ/entropy; first-day share of high-a, high-n motifs | automation level; families present |

## Interesting behavior

- **The scheduler's day cycle is excess, not housekeeping.** Day edges are net occupancy change (absent → active within 9–22 s). Housekeeping is the per-call work cycle (H14's fine-action arrows, 0.10–0.20 nats per transition).
- **Excess needs no steady state.** That makes it usable on week-long periods that start with a quench.
- **Speed limits capture a fixed fraction.** On the Brusselator the speed limit captures 1/3–1/2 of the excess. Glycolysis reaches σ_TSL/σ ≈ 0.2–0.5.
- **Selection has a resolution.** Real molecular replicators resolve s ≥ 0.3–3% (σ* ≈ 3.5–5.9). In the chemostat model, each competitor dies when the winner's σ* crosses −ln(1 − k_i/k₁) = 0.29, 0.69 and 1.39 nats.
- **Arbitrary conventions cost infinite affinity to select.** With s → 0, fixation must come from drift, a field or superlinear recruitment (model 13).
- **Closure can exist without realization.** A RAF that is not a CAF waits for an uncatalyzed bootstrap. Here that bootstrap is an agent action.
- **The nucleus is not the winner.** In Mathis's model the replicators that start the transition differ from the ones finally selected.
- **Assembly index tracks compressibility.** Low a means high LZ compressibility and low entropy rate for stationary ergodic sources.

## Mapping to the village

- **Copies (the ensemble):** the agents of one unit (N = 4–32), from `period_units`. Same-type events within a unit (kickoffs, day starts) are a second kind of copy.
- **States:**
  - `behavior_states_v3` (11 states plus absent, 5-min windows, soft `p_*`); ≥ 3 states, so housekeeping is defined;
  - the DQ4 `work_ledger` repo allocation per agent (agent work only), with ∅;
  - `activity_bins_fixed` on/off (a tree: excess only).
- **Fluxes:** sum the soft transitions p_t ⊗ p_{t+1} over agents in bins aligned to the kickoff. Debias ‖ṗ̂‖² with split-half agent cross-products.
- **Speed limit (H75):** W = TV distance between pre-kickoff and settled DQ4 allocations; Ā = repo switches per agent per active hour; T = settling time.
- **Replicators (H77, H78):** a repo j is a replicator with host count n_j (DQ4, label expiry E = 100 own calls, `infra/shared/replicator_hosts.py`). Copying is recruitment through a read (link → read → adopt; `context_ledger_items`). Uncopying is a host leaving. Dilution ϕ is project-independent host loss: roster exits, goal resets, unrecovered erasures. The clock is the swarm call clock (H40).
- **RAF (H79):** types X = artifacts (`artifacts`, `artifact_mentions`); reactions R = session × repo write episodes (DQ4 `work_commits`, inputs from `artifact_commands_text` and ledger reads); catalysts C = artifacts executed in the session (scripts run, services called, automated streams); food F = platforms, kickoff-named and pre-period artifacts. **Agents are not catalysts,** because operators supply them; agent work is the uncatalyzed background.
- **First-order transition:** monomers = agent calls (closed within a period); replicators = projects; E = the kickoff field over topics (`goal_fields`); R = the topic mix of active projects (DQ5 clusters of their commits, both models).
- **Assembly (H80):** objects = command motifs (`actions_bash_head_fixed`, `artifact_commands_text`) and per-repo commit sequences; a = smallest-grammar size (Re-Pair) as an upper bound; copy number counted per independent producer within a period. The baseline set: entropy rate, LZ76, LZ78 factors, gzip/zstd ratio, timing only.

## Identifiability at village sizes

Units have N = 4–32 agents; 71 non-holdout units span 283 days. The round-1 synthetics (H75–H80 cards, 2026-10-04) set what is identifiable.

- **Kickoff excess is not identifiable at village N** (H76 synthetic). Excess scales as 1/T under slow driving, so a 5-h relaxation adds less excess per step than the scheduler's day-start transient. A 30-min quench is detected in 17% of replicates.
- **Day-edge excess and trimming are recoverable at #51 scale** (N 25 × 10 days) **and not at #40 scale** (N 15 × 5 days, SD > 2).
- **Soft labels attenuate housekeeping ×0.19** (H76 synthetic). Absolute σ_hk levels are lower bounds; shares are recoverable at #51 scale.
- **The speed-limit bound never fails** (0 violations in 600 synthetic replicates; H75). Its slack separates churn-dominated settling from an instant freeze (S ≈ 4.5 vs 1.15). It does **not** separate field-limited from activity-limited settling (S ≈ 4.4–4.8 under both).
- **Cadence elasticity of settling is biased** by −0.4 to −0.5, with power 0.19–0.36 to reject activity limitation (H75 synthetic).
- **σ\* depends on the host-label expiry** (H77 synthetic). E = 300 biases σ̂* low (−0.3 to −2.5); E = 50 biases it high (+0.7 to +2); E = 100 gives −0.35 to +0.13 in #31 and #41.
- **The resolution test has no power at village counts** (H77 synthetic: size 0, power 0). It is reported as *not identifiable*.
- **Only superlinear growth order is identified** (H78 synthetic). With fitness heterogeneity, a planted p = 0.5 returns p̂ ≈ 0.95–1.02, and a field-only world returns 0.47–0.69. Conformist p = 1.4 is recovered at 1.25–1.66. Ghost hosts (long label expiry) inflate p̂.
- **Time-respecting RAFs collapse to singletons** (H79 note): the earliest reaction of any set has only earlier inputs. The static, type-level network is the right object for closure; test the time arrow separately.
- **EP inference sample size:** the Ising demonstration used 10⁹ samples; the village has ~235k events. Pairwise Σ on 1-min activity spins sits at the noise floor (H05). Use richer states (H14, H56), cross-fitting and held-out days.
- **First-order waiting times:** one waiting time per period gives few samples per mode. An exponential fit needs hierarchical partial pooling, reported next to per-period values.

## How to fit (or measure)

1. Fix the state space, bin, copies and food set in the card before looking. Report coarse and fine state spaces side by side; lumping lowers σ.
2. **EP:** Aguilera dual on antisymmetric observables, cross-fitted by day; Newton-step bound as a companion. Normalize per agent-hour.
3. **Excess:** solve the convex problem (Eq. 38 in the Kolchinsky 2026 notes) on ensemble fluxes per bin; σ_hk = σ − σ_ex. Use a per-agent block-flip reversible surrogate as the floor (H76 A1).
4. **Speed limit:** compute W, Ā and T per unit; report S with an agent bootstrap.
5. **Selection:** σ* = ln(J⁺/J⁻) for the top repo on its plateau; s for rivals that died after their first link; neutral band from the E = 100 neutral world on the unit's schedule.
6. **Growth order:** per-host recruitment hazard vs n on the call clock, conditional on kickoff naming and on read-gated adoptions.
7. **RAF:** the Hordijk pruning algorithm per period, maxRAF and maxCAF, iRAFs by random deletion.
8. **Assembly:** within-period classifier of agent vs automated sequences; AUC of {entropy, LZ, gzip} vs {+ grammar size}.
9. Write per-unit rows to `per_period_estimates`. Place units on a phase diagram (σ*, S or σ_ex share against field strength, cadence and N).

## Nulls and controls

- **Reversible surrogates:** per-agent block flips for excess (not per-step transpositions, which break each agent's telescoping net change); trimmed block shifts for EP.
- **Ordinary day starts as placebo kickoffs:** the kickoff's σ_ex must exceed every day-start placebo of the period.
- **Neutral copying (model 06):** p = 1 and σ* in the neutral band.
- **Field-only formation:** p = 0 and no extinction ordering. A field-formed project neither grows first-order nor goes extinct.
- **Fitness labels permuted within period** for the resolution test.
- **Rewired and time-reversed catalysis** for RAFs, preserving read counts. A RAF that survives time reversal is not causal.
- **Food-set sensitivity:** add kickoff-named artifacts and common tools to F; a RAF that disappears was the field or the prior.
- **Timing-only and compression baselines** for assembly. The `automated` label is itself defined by timing, so the timing baseline has an advantage by construction.
- **In-flight placebo** for every recruitment: joins with no logged read of the repo at matched time (H53 baseline 1.5%).

## Pitfalls

**The four impostors** (`../../STANDARDS.md` §1):
- **Scheduler field.** The day cycle is a large excess pulse at the edges, nearly absolutely irreversible. Only DQ8 trimming removes it. Cron triggers are timing, not catalysis; require a content dependence. Periodic automata produce the most compressible logs.
- **Exogenous field.** The kickoff forms hosts directly, which is spontaneous formation outside the selection theory. Violations ρ > f(1 − e^{−σ}) flag field formation. Kickoff-named artifacts go in the RAF food set. In Mathis's mapping, E is the field itself, so the test is decoupling from it.
- **Shared model priors.** Families converging on one repo mimic selection. Every LLM emits the same git idioms on day 1, so AT's "high a × high n" is the prior (H80 predicts ≥ 70% of such motifs on first days, across families). Common tools belong in F, or every reaction is trivially catalyzed. Report growth order from hosts of other labs.
- **Contemporaneous convergence.** Two repos updated together without a logged execution or read are not a catalysis edge. Recruitment without a logged read is formation, not copying.

**Thermodynamic traps:**
- **Tokens are not heat.** Spend is paid in both directions, is set per call by cadence, and changes with prices across regimes. Use σ in nats; tokens only as an expected-null secondary.
- **Notation clash.** σ is an EP rate in Kolchinsky 2026 and Aguilera 2026, and an affinity per copy in Kolchinsky 2025. ϕ is a potential in one and a dilution rate in the other. Name both in every card.
- **Merging invariance is not lumping.** σ_ex is invariant to merging transitions with the same stoichiometry, not to lumping states. It does not attribute cause: the scheduler and the agent making the same jump look the same.
- **Non-Markov agents.** Context memory makes the dynamics non-Markov (H56). Bound violations are diagnostics, not errors.
- **Steady state is rare.** Periods last about a week and start with a quench. Use plateau windows and hierarchical pooling, never full pooling.
- **The village is open.** Operators re-inject hosts, compute and goals (NE43). "Self-sustaining" means within a period with F fixed, and at best an egregore is a symbiont of operator-supplied hosts (HH305).
- **Mutation.** Projects fork and edit (H07). The selection theory excludes mutation, which is expected to raise costs.
- **The error threshold never binds.** Git copies exactly (q ≈ 1); chat-borne ideas die for lack of reproduction (H34 R̂ ≈ 0.2), not from copying error.

## Hypothesis seeds

- **HH311 · Collective entropy production beyond the parts.** σ_coll/σ_joint < 0.1 in activity and behavior, concentrated at named-message read-outs.
- **HH323 → H75 · Speed limit on re-allocation.** Slack ≥ 3 in ≥ 2/3 of periods; read against the instant-freeze rival only (H75 A1).
- **HH324 → H76 · Excess/housekeeping split.** ≥ 60% of a day's excess in the first and last 30 min; trimming removes ≥ 70% of excess and < 20% of housekeeping. The kickoff test is marked not identifiable.
- **HH325 → H77 · Selection resolution.** σ* ≥ 1 nat in herding weeks and ≤ 0.3 in fragmented free weeks.
- **HH326 → H78 · Growth order.** p = 1.2–1.5 in herding weeks; the sublinear branch is not identifiable under fitness heterogeneity.
- **HH327 → H79 · Artifact-only RAF.** maxRAF ≤ 20% of work commits; iRAFs of size ≥ 3 in ≤ 1/3 of periods.
- **HH328 → H80 · Assembly vs compression.** Compression AUC ≥ 0.9; assembly index adds < 0.02.
- **Kickoff decoupling is abrupt** (Mathis notes): in free periods, I(project topics; kickoff field) drops in a step with exponential waiting times, and the nucleating project is not the winner in ≥ 1/2 of herding periods.
- **Shared relaxation by additivity** (Kolchinsky 2026 notes, K4): r = σ_ex(all)/Σ_g σ_ex(g) ≥ 0.8 across families, ≤ 0.6 across rooms with different goals.
- **Ideas need formation** (Kolchinsky 2025 notes, D5): f < ϕ for ≥ 90% of H34 items; formation at artifact reads carries ≥ 70% of uses in multi-period survivors.
- **Infrastructure as a chemical organization** (OoLEN notes, HH302): long-lived artifacts receive commit flux at least equal to their decay, with ≥ 30% of post-exit maintenance from non-founders.

**Hypotheses that use this model:** H75, H76, H77, H78, H79 and H80 (primary); H14, H56 and H05 (Aguilera EP estimator); H06, H11 and H53 (neutral coexistence, herding and conformist recruitment as regimes of the selection theory); H48 and H54 (settling time and the kickoff quench that the speed limit and excess measure).
