# Thermodynamics of Darwinian selection in molecular replicators

**Citation:** Artemy Kolchinsky, "Thermodynamics of Darwinian selection in molecular replicators", arXiv:2112.02809v5 [q-bio.PE] (2025).
**File:** kolchinsky-2025-thermodynamics-darwinian-selection-replicators.pdf
**Fields:** thermodynamics, stat mech, dynamics (evolution)

## Summary
The paper asks what thermodynamics costs Darwinian selection among autocatalytic replicators in a well-mixed reactor. Fitness is defined operationally as the invasion growth rate, which is also the critical dilution rate and the maximum replication rate. A bound links the affinity σ (free energy dissipated per copy), the replication rate ρ and the fitness f. In a steady-state flow reactor it gives a resolution limit on selection: **s ≥ e^{−σ*}**. Telling apart a relative fitness difference s costs at least −ln s per copy. At equilibrium every replicator coexists; at infinite affinity only the fittest survives. The bounds cover elementary and multistep replicators, polymer templates and uniform cross-catalytic cycles, and they survive degradation. Examples: Rebek's dimer, and the Schuster–Sigmund chemostat, where each extinction is a second-order nonequilibrium transition.

## Key formalism
*Notation clash with the PRR note:* here σ is the **affinity per copy** (not an EP rate), and ϕ is the **dilution rate**.
- **Setup.** X + Σα_iA_i ⇌ 2X + Σβ_iA_i. The dynamics are ẋ = J − ϕx = (ρ − ϕ)x, with ρ = J/x. The affinity is σ = −ln x + Σ(α_i − β_i) ln a_i − ΔG°/RT, in k_BT per copy. Assumptions: no spontaneous (uncatalyzed) formation, and replicators interact only through shared substrates.
- **Elementary replicator:** J = rx − r⁻x², with flux–force relation σ = ln(rx / r⁻x²).
- **Multistep replicator** (m-step mechanism, intermediate ratios y_k/x constant): J = r(ρ)x − r⁻(ρ)x², where r is decreasing and convex in ρ and r⁻ is increasing and concave. Then σ = ln[r(0) / (x r⁻(0))].
- **Fitness, defined implicitly by f = r(f).** It has three equivalent readings:
  1. the invasion growth rate, x(t) ≈ x(0)e^{(f−ϕ)t};
  2. the critical (washout) dilution rate;
  3. a ceiling, since ρ ≤ f always.

  The selection coefficient is s = 1 − f′/f.
- **Bound 1:** **σ ≥ −ln(1 − ρ/f)**, i.e. ρ ≤ f(1 − e^{−σ}).
  - It is an equality for elementary replicators, and tighter near ρ → 0 and ρ → f.
  - In a steady-state flow reactor it becomes σ* ≥ −ln(1 − ϕ/f).
- **Bound 2 (selection).** If the fitter X is present (f > ϕ) and X′ is extinct (f′ ≤ ϕ), then σ* ≥ −ln s.
  - It is independent of the mechanism, of the number of replicators and of the competition structure.
  - It complements the drift limit (s ≫ 1/N_e) and the error threshold (s > μ).
  - It becomes trivial for σ ≳ 20 (about one ATP).
- **Numbers.**
  - Resolution for real replicators: prion σ* ≈ 3.5 → s ≥ 3%; RNA ligase σ* ≈ 5 → s ≥ 0.6%; peptide σ* ≈ 5.9 → s ≥ 0.3%.
  - Rebek's dimer: f ≈ 0.14. The bound's efficiency −ln(1 − ρ/f)/σ is ≈ 0.5 in the closed reactor and ≈ 0.65 at critical dilution.
- **Chemostat model** (k = 4, 3, 2, 1; −ΔG°/RT = 1, 2, 3, 2.5; feed γ = 1).
  - Replicators wash out in order of k. Each X_i dies when σ₁* crosses −ln(1 − k_i/k₁) = 0.29, 0.69 and 1.39 nats.
  - Near equilibrium, abundance follows ΔG°, not fitness.
  - EP rate Σ̇ = ϕ Σ x_i*[ln(a*/x_i*) − ΔG°_i/RT]. It is kinked at each extinction.
- **Cross-catalytic cycles** of n members: Σ_j σ^(j) ≥ −n ln(1 − ρ/f), so cost grows linearly with cycle length.
- **Not covered:** fluctuations, mutation (expected to raise the cost), spontaneous formation.
- **Versus Kolchinsky 2024:** England's bound ties σ to growth and *decay* (and fails); this one ties σ to growth and *fitness*.

## Mapping to agent swarms
- **Repos as replicators (HH301).**
  - X is project j, and x = n_j is its host count (DQ4 `work_commits`, `project_states`). The substrate A is uncommitted agents.
  - Copying is a host recruiting a free agent: link, then read, then adopt. Read-out gating (H08, H53) adds intermediate steps, so the mechanism is *multistep*.
  - The reverse ("uncopying") is a host leaving. In chemistry it is ∝ x², so it is worth testing whether departures grow with n ("someone else is on it").
- **Operational affinity:** σ_j = ln(J⁺_j / J⁻_j), recruitments vs departures, in nats per net copy. This is flux–force irreversibility, not heat.
- **Dilution ϕ:** project-independent host loss, from roster exits, goal resets and unrecovered erasures. Erasure is weak dilution: P(return to own artifact) is 0.96 with a re-read (H58).
- **Fitness f:** the per-host recruitment rate while the project is rare (n ≤ 2 after its first link). Anchor: adoptions jump ≈ 20× at the first link (H53: 22.5; 33 for new projects vs 3.8 for carried-over ones).
- **Herding vs fragmentation.**
  - Winner-take-all weeks (H11: herding in 11/14) correspond to a high σ* for the winner.
  - Fragmented free weeks correspond to near-equilibrium coexistence. Evidence: singletons are 0.79–0.91 of projects, and only 0.23–0.53 of switches go to a held project (H06).
  - In that regime, the paper says abundance tracks ΔG°. Here the analogue of ΔG° is preference set by the field and priors (kickoff naming, H54; model priors), not fitness.
- **The impostors sit inside the model.** Field-made hosts, independent invention from shared priors, and in-flight convergence are all *spontaneous formation*, which the theory excludes. A field-formed project neither grows first-order nor goes extinct.
- **Ideas as replicators.** H34's branching ratio (median 0.22; 0.06–0.39) means f < ϕ: ideas don't sustain themselves (mean cascade size 1/(1 − R) ≈ 1.3). A persistent idea must be fed by formation, i.e. artifact re-reads or kickoffs.
- **Conventions and herding cost.** Arbitrary conventions have s → 0, so selecting one by fitness would cost −ln s → ∞. Fixation must therefore come from one of:
  - drift, which dominates when s ≲ 1/N ≈ 0.03–0.25;
  - a field;
  - conformist (superlinear) recruitment, which is outside this first-order class. H53's finding that share is the only predictor of herding (AUC 0.72) points this way.
- **Agent + own artifact as a two-member cross-catalytic cycle** (H44, H58): the artifact restores the agent after erasure.
- **Tokens or calls as dissipation.** The analogy breaks: there is no local detailed balance linking spend to ln(J⁺/J⁻), departures cost tokens too, spend is set per call by cadence, and prices change across regimes. Use σ in nats as the main measure, and tokens only as an expected-null secondary.

## Candidate hypotheses
- **D1: Order of recruitment (do this first).** Observable: per-host recruitment hazard vs project share (DQ4, gated on ledger reads).
  - Prediction: elasticity +0.3 to +0.7 in shared-artifact weeks; |e| < 0.15 in own-artifact weeks.
  - Null: e = 0 (first-order, the paper's class).
  - Impostors: kickoff field (condition on naming); contemporaneous convergence (in-flight placebo, H53 baseline 1.5%).
- **D2: Flux–force consistency.** Observable: efficiency −ln(1 − ρ/f)/σ for projects with ≥ 5 hosts, in plateau windows.
  - Prediction: median ≈ 0.6, within [0.4, 1] (Rebek: 0.5–0.65), lower in regime III where read-out gating adds steps.
  - Violations ρ > f(1 − e^{−σ}) mean the field is forming hosts directly: predict ≥ 2× more on kickoff-named projects.
  - Impostor: kickoff field.
- **D3: Selection resolution.** Observable: σ* of the top project on its plateau; s for each project that died after its first link.
  - Prediction: ≥ 90% of extinct rivals have s ≥ e^{−σ*}. Median σ* ≥ 1 nat in herding weeks (resolution ≤ 0.37); ≤ 0.3 in free weeks (resolution ≥ 0.74, near-neutral coexistence as in H06).
  - Null: fitness labels permuted within period.
  - Impostor: shared model priors.
- **D4: Equilibrium-to-selection crossover** (each period is a point on the phase diagram). Observable: Spearman of abundance with fitness vs with kickoff naming, against host turnover ϕ, across the 71 units.
  - Prediction: correlation with fitness rises with ϕ (one-sided p < 0.05); naming dominates in the lowest-ϕ third (ρ ≥ 0.5).
  - Impostor: kickoff field.
- **D5: Ideas need formation, and tokens don't price selection.** Observable: dn/dt = κ_form + (f − ϕ)n fitted to H34 items.
  - Prediction: f < ϕ for ≥ 90% of items. In multi-period survivors, κ_form carries ≥ 70% of uses, at artifact reads.
  - Tokens per adoption vs σ: |ρ| < 0.15.
  - Impostors: shared priors; contemporaneous convergence.

## Caveats
- **No temperature or ΔG°.** σ is only ln(J⁺/J⁻). For elementary kinetics that makes Bound 1 near-tautological; its value is as a test of mechanism, plus the steady-state selection bound. Tokens are not heat.
- **Small numbers.** The theory is deterministic, but n ≤ 32 hosts, so extinction is stochastic and drift swamps s ≲ 1/n.
- **Steady state is rare.** Periods are about a week and start with a quench. Use plateau windows, one trajectory per period, with hierarchical pooling.
- **Formation (the shared field) dominates,** which violates a core assumption. Measure it; don't assume it away.
- **Coarse graining.** Project and host definitions (DQ4 forks, automated commits) shift every number. Projects also mutate (H07), and the paper expects mutation to raise costs.
