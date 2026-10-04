# 14 · Scaling and fluctuations: size laws, Taylor's law, coarse-graining and active order

**Fields:** stat mech, complex systems, active matter
**References** (notes in `../../literature/`):
- Meshulam et al. 2019, phenomenological RG: `meshulam-2019-coarse-graining-fixed-points-scaling-neurons.md` (the notes also quote the long companion paper, arXiv:1812.11904, marked [L] there).
- Silverberg, Bierbaum, Sethna & Cohen 2013, mosh pits and the MASHer model: `silverberg-2013-collective-motion-mosh-circle-pits.md`.
- From memory, not in `literature/`: Bettencourt et al. 2007 and Bettencourt 2013 (urban scaling)†; Taylor 1961 (Taylor's law)†; de Menezes & Barabási 2004 (internal vs external fluctuations)†; Eisler, Bartos & Kertész 2008 (fluctuation-scaling review)†; Crutchfield & Feldman 2003 (excess entropy, block entropies)†; Rosso et al. 2007 (permutation complexity–entropy plane)†; Vicsek et al. 1995†; Toner & Tu 1995† and Ramaswamy 2010† (giant number fluctuations).

**Related models:** `../11-vector-spins/` (alignment, polarization, the goal as a field; this folder adds self-propulsion), `../01-inverse-ising/` (spectra and pairwise structure), `../09-hawkes/` (activity timing). Per-pair coupling J ∝ N^−β (H18) and per-pair branching R̂/(N−1) (H34) are size laws that belong to this folder.

## The model

This folder collects statistics that ask how a quantity changes with system size, with mean, with coarse-graining scale, or with time. Each has a null exponent for independent parts and a different one for a shared field.

**1. Allometric (urban) scaling (Bettencourt†).** A unit-level output Y against the unit's population N:

$$Y=Y_0\,N^{\beta}$$

- β = 1: extensive. Each agent contributes independently.
- β > 1: superlinear. Interaction adds output. Cities give β ≈ 1.15 for socioeconomic outputs†.
- β < 1: sublinear. Shared infrastructure or coordination overhead. Cities give β ≈ 0.85 for infrastructure†.
- A mean-field derivation: if per-pair interaction scales as k^{−β_d} with k ∝ N partners, per-agent interaction output scales as N^{1−β_d}, so total output scales as N^{2−β_d}.

**2. Fluctuation scaling (Taylor's law†).** Across agents (or bins) with mean μ and variance Var:

$$\mathrm{Var}(Y)=a\,\mu^{b},\qquad\text{or}\qquad \mathrm{Var}(Y)=a\,\mu+c\,\mu^{2}$$

- b = 1: independent Poisson-like events. b = 2: a shared multiplicative field dominates†.
- The second form (de Menezes & Barabási†) splits variance into an internal term aμ and an external term cμ². The coefficient c is the variance share of a shared multiplicative drive.
- **Giant number fluctuations†:** in ordered active matter, the count fluctuation in a region grows as ΔN ∝ ⟨N⟩^{a} with a > 1/2 (a = 1/2 for independent particles).

**3. Phenomenological renormalization (Meshulam 2019).** For many variables x_i(t) (here: term usage series):
1. Pair each variable with its most correlated unpaired partner, greedily.
2. Sum each pair and renormalize so the mean of nonzero values is 1.
3. Repeat to clusters of size K = 2^k.

Observables at each K:
- variance M₂(K) ∝ K^{α̃}; independent α̃ = 1, perfectly correlated α̃ = 2;
- "free energy" of silence F(K) = −ln P₀(K) = aK^{β̃}; independent β̃ = 1;
- within-cluster covariance spectrum λ ∝ (K/rank)^{μ};
- correlation time τ_c(K) ∝ K^{z̃}.

Mouse CA1: β̃ = 0.88 ± 0.01, μ = 0.71 ± 0.06, z̃ = 0.11–0.16, α̃ = 1.40–1.73 across three mice [L]. A field-only place-cell null gives α̃ = 1.78 ± 0.03, a kink at the field size K_c ≈ 18 and no β̃ scaling [L].

**4. Complexity–entropy diagram (computational mechanics†).** For a symbol sequence, block entropy H(L) over words of length L gives:
- entropy rate h_μ = lim_{L→∞} [H(L) − H(L−1)], the irreducible randomness per symbol;
- excess entropy E = Σ_L [h_μ(L) − h_μ], the information the past shares with the future (total storage);
- statistical complexity C_μ ≥ E, the memory of the minimal predictive model (ε-machine)†.

Each unit is a point on the (h_μ, E) plane. Periodic sequences sit at h_μ = 0, i.i.d. sequences at E = 0, and structured processes in between†. For continuous series, the permutation (Bandt–Pompe) entropy–complexity plane† is the standard substitute.

**5. Active-matter order (Vicsek†; Silverberg 2013).** Agents are self-propelled particles with velocity v_i, alignment strength α, noise σ and self-propulsion v₀.
- Polarization φ = |Σ_i v_i/|v_i|| / N. Its finite-N floor for random directions is ≈ N^{−1/2}.
- MASHer model: a disordered gas when τ_noise ≪ τ_flock, with boundary σ ~ √(v₀α/μ_d) (μ_d the propulsion damping); an ordered vortex when τ_flock ≪ τ_noise, τ_coll.
- Mosh-pit speeds follow the 2-D Maxwell–Boltzmann distribution P(v) = (2v/T)e^{−v²/T}. This comes from the central limit theorem, not from equilibrium. v₀ = 0 removes all collective motion.

### Order and control parameters
| Statistic | Order parameter | Control parameters in the village |
| --- | --- | --- |
| Allometric | β per output (messages, replies, commits, distinct repos) | N (active population), regime, goal type, rooms |
| Taylor | b; field gauge c | DQ8 trimming, kickoff specificity, scheduler regime |
| RG | β̃ − β̃(null); log-variance curvature; z̃ | field removal (kickoff, scheduler), free vs assigned periods |
| Complexity–entropy | (h_μ, E) per unit; E_village − Σ_i E_i | boundary (agent, agent + artifact, repo, room, village), bin width |
| Active order | residual polarization φ within read cones vs across rooms; velocity tail shape | reads per agent-day (α), cadence (v₀), sampling noise (σ) |

## Interesting behavior

- **Superlinear output would be the first collective benefit.** H58 found the persistent unit is agent + own artifact, which predicts β = 1 for committed work. β > 1.1 would mean interaction adds output.
- **Size laws link measured constants.** H18's per-pair dilution (β_d ≈ 0.66) predicts replies scale as N^{1.34}. H34's per-pair branching falls as (N−1)^{−0.55}. H25's per-pair content correlation is flat in N (ρ̄ ≈ 0.28). A cross-period scaling test checks whether these aggregate.
- **Taylor's c_T (not a field gauge for clocked agents; use c_×, H86) is a one-number field gauge.** Raw activity should give b ≈ 2 from the scheduler. Trimming to the all-present window should drop b toward 1–1.3.
- **α̃ cannot separate a field from a fixed point.** The field-only null gives α̃ = 1.78, inside the range of real mice (1.4–1.73). β̃, the log-variance curvature at the field scale and τ_c scaling are the discriminating tests (HH317 refinement).
- **Storage only the collective has.** E_village > Σ_i E_i after field removal would be collective storage. For the joint process of independent parts, excess entropy is additive, so the sum is the no-interaction reference†. A coarse village sequence (e.g. the dominant repo) can lose storage, so compare joint and coarse versions.
- **Equilibrium-looking speeds are not equilibrium.** Maxwell–Boltzmann velocities are the CLT null. Heavy tails mark structure (jumps at erasures and kickoffs).
- **Active systems escape Mermin–Wagner.** Self-propulsion allows long-range order where static spins cannot order (Toner–Tu†; see model 11).

## Mapping to the village

- **N:** the active population per unit from `period_units` and `roster_daily` (agents with activity that day), not the roster. Rooms inside multi-room units give within-unit size variation.
- **Outputs Y** (per unit, per active hour, or per fixed-length window):
  - messages and talk calls (`chat_core`, `call_windows`);
  - replies (DQ2 `reply_pairs`, p_reply ≥ 0.5);
  - committed work (DQ4 `work_commits`, agent work only);
  - distinct repos touched (DQ4);
  - H34 marker adoptions.
- **Taylor:** per agent within a unit, the mean and variance of per-bin counts from `activity_bins_fixed` (raw vs DQ8 `all_present_window` trims), DQ4 commits per bin, and messages per bin.
- **RG variables:** hashed H34 marker usage per 15- or 30-min bin within a unit, terms with ≥ 20 uses. Agents (4–32) are too few: at most five merge steps.
- **Complexity–entropy sequences:** the DQ4 which-repo sequence (≤ 7 symbols) per agent, per agent + own artifact, per repo (its host sequence), per room and for the village; `behavior_states_v3` sampled states per 5-min window.
- **Active matter:**
  - position: DQ5 `agent_win30_style_resid_period` vectors, both models, in a 2–3 PC projection for angular statistics;
  - velocity: the change per window, or per own call (H40's call clock), with the kickoff drift (`goal_fields`) removed;
  - self-propulsion v₀: own call cadence (`call_windows`) times the typical step per call;
  - alignment α: the regression of v_i on the mean velocity of senders read at that call (`context_ledger_items`);
  - noise σ: the fitted residual step;
  - temperature T(t) = ⟨|v|²⟩ after a kickoff ("a hot pit cools").

## Identifiability at village sizes

- **Allometric slope.** N spans about one decade (4–32) over 71 non-holdout units. With a residual SD of 0.5 in ln Y and SD(ln N) ≈ 0.6, the slope SE is ≈ 0.10, so a 95% CI is about ±0.2 (a design estimate). That separates 1.34 from 1 but not 1.15 from 1. Regime and goal-type covariates cost degrees of freedom and widen it.
- **N is not exogenous.** Operators chose bigger rosters in later regimes. N correlates with regime, so fit with regime as a covariate and report within-regime slopes.
- **Taylor across agents:** 4–32 points per unit. Fit b per unit with a log-log errors-in-variables model, and compare units on a phase diagram. Units with N < 8 give b to about ±0.5 only.
- **RG:** a unit lasts about 4 days, i.e. T ≈ 200–400 fifteen-minute bins. The correlation noise floor is ≈ 1/√T ≈ 0.05–0.07, near typical term–term correlations. The spectral test needs T > 10K, so K ≤ 32. β̃ only needs P₀(K) and is the most stable choice. Expect error bars about 3× the mouse data.
- **Complexity–entropy:** block entropies need |A|^L ≪ T. With 7 symbols and T ≈ 300 bins per agent, L ≤ 2–3, which underestimates E. Use NSB or Miller–Madow bias correction and report E(L) as a curve, not a limit.
- **Active order:** N is 4–15 per room against 500 in the model. Finite-N polarization is large (floor ≈ N^{−1/2} ≈ 0.25–0.5). Only the excess over a block-shift surrogate counts.

## How to fit (or measure)

1. **Allometric:** compute Y per unit within the unit (a per-period statistic), then regress ln Y on ln N across units with regime and goal-type covariates. This compares periods as points on a phase diagram; it fits no model to pooled data. Report β per output with a unit-bootstrap CI.
2. **Taylor:** per unit, fit Var = aμ + cμ² across agents on raw and trimmed grids. Report c and its change under trimming in `per_period_estimates`.
3. **RG:** run the greedy merge on term usage within a unit. Report α̃, β̃, the curvature of log M₂ vs log K and τ_c(K), with connected-quarter errors. Rerun on the conditionally independent term model.
4. **Complexity–entropy:** block entropies on each sequence, h_μ and E with bias correction, one point per boundary and unit.
5. **Active order:** residual velocities, φ within read cones vs across rooms, and the shape of the speed distribution (Rayleigh vs heavy tail). Fit (α̂, σ̂, v̂₀) per period and place periods on the (α, σ) diagram.

## Nulls and controls

- **Independent-parts exponents:** β = 1, b = 1, α̃ = β̃ = 1, φ ≈ N^{−1/2}. These are references, not nulls; the field is the real null.
- **Field-only skeletons:** DQ8 `simulate.py` presets on the real schedules. They give the shared-field exponents (b → 2, α̃ ≈ 1.6–1.8) with no coupling.
- **Conditionally independent term model** (RG): each term used with p_i(field state(t)), where the field state is the scheduler activity level (`activity_bins_fixed`, trimmed), time since kickoff and the `goal_fields` projection. Do not residualize counts; residuals have no exact zeros, so P₀ loses its meaning.
- **Time-shifted surrogates** for RG: greedy pairing on noise creates structure; exponents should return to 1.
- **Block-shift surrogates on trimmed windows** for φ and c_vv.
- **In-flight placebo** for alignment: alignment with posted-but-unread senders must be lower than with read senders.
- **Size-matched comparison** for E_village vs Σ E_i: random groups of the same size from the same unit.

## Pitfalls

- **H86 correction (2026-10-04):** Taylor's c_T and b are not field gauges for clocked agents (b ≈ 0.85 < 1). The shared-field gauge is the pair-covariance c_× with shared share φ. The design SE for scaling exponents is about 0.25 with regime intercepts and goal clusters, not 0.10.

**The four impostors** (`../../STANDARDS.md` §1):
- **Scheduler field.** It is the textbook multiplicative field: b ≈ 2 and large c on untrimmed activity. 70–80% of regime-III co-activation is the schedule (H38). Velocities jump at day edges. Trim first; never use cross-day surrogates on untrimmed activity.
- **Exogenous field.** Kickoffs seed many terms at once, which gives near-power laws over a limited range and a kink at K_c ≈ the number of terms one kickoff seeds. A common drift toward the goal gives φ > 0 without alignment; fit α net of the `goal_fields` direction.
- **Shared model priors.** Families use the same terms and drift the same way. Merge per family, or include family usage rates in the term model. The direction of an ordering onset may be predictable from the prior ("chirality is the prior").
- **Contemporaneous convergence.** Terms co-used in the same bin without a read belong to the field model, not to coupling. Alignment must be computed on read senders only.

**Mapping traps:**
- **The old `activity_bins` dropped about half the events** with a day-specific share, which acts as a shared day field (RE-A1). Use `activity_bins_fixed`.
- **Outputs need a common clock.** Periods differ in length and active hours. Normalize Y per active hour or per fixed window, or β absorbs duration.
- **Active minutes are attention, not work** (RE-O1). Use DQ4 commits for productivity scaling.
- **Two decades is the minimum for a scaling claim.** N spans one decade, so allometric β is a slope, not a law. RG spans at most K = 2⁸–2¹⁰ within a unit.
- **α̃ alone varies 1.4–1.73 across mice.** Never read one α̃ as a fixed point or a field signature.
- **Embedding anisotropy inflates alignment.** Center and whiten (model 11). Statement-level geometry differs between bge and gte (10-NN overlap 0.26); use agent-window aggregates and both models.
- **"Noise = temperature" is an analogy.** Sampling parameters are provider-set and not logged.
- **Criticality readings were refuted before** (H03, H25, H26). Scaling here is a measurement of size laws and field strength, not a criticality test.

## Hypothesis seeds

- **HH309 · Urban-style scaling.** Messages β ≈ 1; replies β ≈ 1.34 (from H18's dilution); committed work β = 1.0 ± 0.1 (H58); distinct repos β ≈ 1 in own-artifact weeks and < 1 in shared weeks. Kill for the consistency check: reply β outside [1.15, 1.55].
- **HH310 · Taylor's law as the field gauge.** Raw activity b ≈ 2; trimmed b → 1–1.3, with c falling by the 70–80% schedule share; commits b between 1 and 2 with c tracking kickoff specificity. Report c in every hypothesis.
- **HH317 · Phenomenological RG of the dialect.** β̃(data) − β̃(null) ≤ −0.05 only in long free periods (#38, #51); no dynamic scaling (z̃ ≈ 0) once time-since-kickoff is in the null.
- **HH318 · Flocking in idea space.** φ ≈ 0 across rooms and small positive within read cones, rising smoothly with reads per agent-day; heavy-tailed velocities, not Maxwell–Boltzmann. Compare φ at matched cadence.
- **HH320 · Complexity–entropy diagram of allocation.** Agents and agent + artifact at low h_μ and high E; the village at higher h_μ with E_village ≤ Σ E_i.
- **Cadence is self-propulsion** (Silverberg notes): φ and the c_vv amplitude fall across NE20 and NE43 when cadence drops.
- **A hot pit cools in calls** (Silverberg notes): T(t) after each kickoff decays per own call, not per minute.
- **Giant number fluctuations in repo occupancy:** ΔN ∝ ⟨N⟩^{a} with a > 1/2 in herding weeks only (H11).

**Hypotheses that use this model:** H18 (J ∝ N^−β_d), H34 (per-pair branching vs N), H25 (per-pair correlation flat in N), H29 (steering-cost scaling with N), H68 (dilution exponent as a composition variable), H09 (reads per call ∝ N^1.9), H38 (the scheduler field that Taylor's c_T (not a field gauge for clocked agents; use c_×, H86) measures), H12 (spectra and effective dimension), H47 (coherence length of content), H76 (cites Taylor c as a companion gauge).
