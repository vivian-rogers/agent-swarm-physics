# Generalized free energy and excess/housekeeping decomposition in nonequilibrium systems: from large deviations to thermodynamic speed limits

**Citation:** Artemy Kolchinsky, Andreas Dechant, Kohei Yoshimura and Sosuke Ito, *Phys. Rev. Research* 8, 023025 (2026). DOI: 10.1103/r48t-dghl
**File:** kolchinsky-2026-generalized-free-energy-excess-housekeeping.pdf
**Fields:** thermodynamics, stat mech, info theory

## Summary
Driven systems have nonconservative forces, so no free energy governs them. The authors define a generalized free energy anyway, by restricting the variational (Donsker–Varadhan) formula for entropy production (EP) to gradient observables. This splits EP into two parts, as an information-geometric Pythagorean theorem:
- **excess:** conservative, tied to net state change, and zero once the state stops moving;
- **housekeeping:** nonconservative, carried by cycles that change nothing.

Excess EP is the large-deviation rate at which the *net state change* runs backward. It can be inferred from short-time increments of observables and obeys Wasserstein speed limits. Unlike Hatano–Sasa, it needs no steady state. The framework applies to linear and mean-field master equations and to chemical networks; the paper's examples are a driven ring, the Brusselator and metabolism.

## Key formalism
- **Setup.** State x (a distribution p, or concentrations). Fluxes j and reverse fluxes j̃ on m one-way transitions; incidence matrix ∇, with ẋ = ∇ᵀj − I. Forces f = ln(j/j̃). EPR σ = jᵀf = D(j‖j̃), where D(a‖b) = Σ a ln(a/b) − a + b. All quantities are dimensionless; local detailed balance (LDB) is only needed to call σ heat.
- **Variational EP:** σ = max_θ [jᵀθ − j̃ᵀ(e^θ − 1)], with optimum θ = f.
- **Generalized free energy (Eq. 38):** σ_ex = max_φ [−jᵀ∇φ − jᵀ(e^{∇φ} − 1)]. The optimal φ* solves ∇ᵀ(j∘e^{∇φ*}) = −∇ᵀj.
  - Dual form: σ_ex = min_{j′} D(j′‖j̃) s.t. ∇ᵀj′ = ∇ᵀj, i.e. the cheapest fluxes that produce the same net change.
  - 0 ≤ σ_ex ≤ σ, and σ_ex = 0 iff ∇ᵀj = 0 (in a closed system, iff ẋ = 0).
- **Housekeeping:** σ_hk = σ − σ_ex = min_φ D(j‖j̃∘e^{−∇φ}), the distance from f to the nearest conservative force.
  - It is carried by cyclic fluxes j_hk = j − j*, with ∇ᵀj_hk = 0.
  - Pythagorean form: D(j‖j̃) = D(j*‖j̃) + D(j‖j*).
  - σ_hk > 0 only if rank ∇ < m/2, i.e. only if the state graph has a cycle.
- **Versus Hatano–Sasa (HS):**
  - HS excess is −ṗᵀ ln(p/p_ss), the lag behind the instantaneous steady state; the paper's excess is the gradient part instead.
  - σ_ex ≥ σ_ex^HS. The gap is the "coupling EPR" between the HS and Maes–Netočný housekeeping, and the potential tends to Maes–Netočný's in the Fokker–Planck limit.
  - In the driven 21-state ring, HS excess ignores the driving γ and violates the speed limits below; σ_ex does neither.
- **Invariance under merging** transitions with the same stoichiometry (e.g. several reservoirs behind one i→j). It is additive across subsystems that share φ*. Lumping states is *not* covered.
- **Linear response:** σ_ex ≈ ẋᵀH⁺ẋ, where H = ½∇ᵀdiag(j)∇ is the short-time diffusion matrix and an Onsager metric (thermodynamic length). The integrated excess is ∝ 1/T under slow driving.
- **Large deviations:** with n copies, reversing all fluxes costs ≍ e^{−nσ dt}, and reversing the net production costs ≍ e^{−nσ_ex dt}. φ* is the most irreversible observable: σ_ex = max_φ L(φ).
- **TUR and inference (Eq. 79):** for any φ, σ_ex ≥ (1/dt)[−2K⁽¹⁾ − Σ_{k≥2} K⁽ᵏ⁾/k!], where K⁽ᵏ⁾ are the cumulants of φ's short-time increment across copies. The bound is tight with d observables and needs no knowledge of which mechanism made each jump.
- **Speed limits:**
  - Activity A = Σ j_ρ.
  - Wasserstein speed Ẇ = min{1ᵀa : ∇ᵀa = ∇ᵀj, a ≥ 0} ≥ ‖ṗ‖₁/2, with equality on a complete graph.
  - Instantaneous: σ ≥ σ_ex ≥ 2Ẇ tanh⁻¹(Ẇ/A) ≥ 2Ẇ²/A.
  - Finite time: Σ_ex ≥ 2W tanh⁻¹(W/𝒜), so **T ≥ (W/Ā) coth(Σ_ex/2W) ≥ W/Ā**. Here W is the geodesic distance and 𝒜 = ∫A dt.
  - Autonomous master equation: Σ_ex(T) ≥ D(p(0)‖p(T)).
- **Numbers:**
  - On the Brusselator cycle, the speed limit captures 1/3–1/2 of the excess EP; a bound on total EP is orders of magnitude slack.
  - Glycolysis reaches σ_TSL/σ ≈ 0.5 (E. coli, mammalian) and 0.2 (yeast), with rank = m/2, so no housekeeping. Holding R5P fixed (chemostatting it) creates a futile cycle.
- **Estimable from trajectories alone:** σ (from jump counts; a lower bound), σ_ex and φ*, A, Ẇ, W, D(p(0)‖p(T)), and σ_hk = σ − σ_ex. The excess needs **copies at a fixed time**; the housekeeping can be time-averaged in stationary windows.

## Mapping to agent swarms
- **Setup.**
  - Copies: the agents of one goal period (N = 4–32), treated as exchangeable units of a mean-field master equation (App. A). The shared field is allowed.
  - States: `behavior_states_v3` (11 states plus absent, 5-min, soft p_*), DQ4 repo allocation, or `activity_bins_fixed` (DQ8-trimmed).
  - Estimator: sum the soft transitions p_t⊗p_{t+1} over agents to get the fluxes j_ij(t) in bins aligned to the kickoff. Solve Eq. 38 (convex) for σ_ex and φ*; take σ from H14's Newton/cfx estimators. Debias ‖ṗ̂‖² with split-half agent cross-products.
- **Excess = kickoff quench (H54, H10): valid.**
  - But "relaxation toward a changing target" is the HS reading. Here, excess is the irreversibility of *any* net occupancy change.
  - HS needs p_ss(t), which we can't estimate; this paper's version is the usable one.
- **Scheduler day cycle (H38, H50): not housekeeping.** At the day edges, everyone switches absent→active within 9–22 s. That is net change, so it is excess: a Brusselator-like limit cycle, nearly absolutely irreversible, which needs pseudocounts. Only trimmed windows remove it.
- **Nudges** (≈ 1 active minute; H04, H30): an excess pulse.
- **Housekeeping = the per-call work cycle.** These are stationary cyclic currents (execute→verify→research→…), e.g. H14's fine arrows: 0.10–0.20 nats per transition, scaffold-free, not tracking output.
- **Rank condition.** A single agent's binary on/off chain is a tree, so σ_hk ≡ 0. Housekeeping needs ≥ 3 states or joint states.
- **Limit of merging invariance.** σ_ex is blind to whether the scheduler or the agent made a jump. The split separates net change from cycling; it doesn't attribute cause.

## Candidate hypotheses
- **K1: kickoff excess.** Observable: σ_ex/σ on v3 ensemble fluxes, in 30-min active bins.
  - *Prediction:* ≥ 0.3 in the first 2 active hours, decaying with a time constant within ×2 of H48's 4.5 h and H54's ≈ 5 h. ≤ 0.1 mid-period on trimmed windows. σ stays flat (H14-R1).
  - *Null:* random mid-period onsets.
  - *Impostor:* the scheduler field. The kickoff excess must be ≥ 2× that of ordinary day starts.
- **K2: the day cycle is excess.** Observable: the split on untrimmed vs DQ8-trimmed grids.
  - *Prediction:* ≥ 60% of the day's σ_ex falls in the first and last 30 min of the schedule (H38's edge share is 0.68–0.72). Trimming removes ≥ 70% of σ_ex and < 20% of σ_hk. Under NE43, σ_hk stays inside the placebo range.
  - *Impostor:* the scheduler field. This split is its per-period gauge.
- **K3: speed limit on re-allocation.** Observables: W (TV distance between DQ4 allocations before the kickoff and after settling), Ā (repo switches per agent per active hour), and the settling time.
  - *Prediction:* T ≥ W/Ā in every period; a violation flags non-Markov dynamics. The slack T/(W/Ā) is ≥ 3 in ≥ 2/3 of periods, i.e. settling is field-limited, not activity-limited. Under NE20, settling elasticity to cadence is ≤ 0.3. Across periods, log Σ_ex vs log(W²/ĀT) has slope 0.7–1.3.
  - *Impostor:* the kickoff field. Activity-limited settling would give slack ≤ 2 and τ ∝ 1/cadence.
- **K4: shared relaxation, from additivity.** Observable: r = σ_ex(all) / Σ_g σ_ex(group g), which is 1 iff the groups share φ*.
  - *Prediction:* r ≥ 0.8 across model families (they differ in style only, H13); r ≤ 0.6 across rooms with different goals (#44, #best/#rest).
  - *Impostor:* shared model priors. A family r < 0.6 would be a real family effect.

## Caveats
- **No temperature.** σ is statistical irreversibility in nats, with meaning via large deviations. **Tokens are not heat:** they have no LDB link to ln(j/j̃), are paid in both directions, and look like housekeeping per call.
- **One long trajectory.** Excess can't be time-averaged. The copies are only N = 4–32 agents, or same-type events within a period; use hierarchical pooling, never full pooling.
- **Coarse-graining dependence.** v3 lumping, 5-min bins and soft labels all lower σ and can shift the shares. Report coarse and fine side by side.
- **Non-Markov agents** (context memory; H56): bounds can fail, and failures are diagnostics. Mask the holdout and respect the regime boundaries.
