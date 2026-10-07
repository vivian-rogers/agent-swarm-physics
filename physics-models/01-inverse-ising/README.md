# 01 · Inverse Ising (pairwise maximum entropy)

**Fields:** stat mech, info theory
**References:** Schneidman, Berry, Segev & Bialek, *Nature* 440, 1007 (2006)†; Mora & Bialek, *J. Stat. Phys.* 144, 268 (2011)†; Bialek et al., "Statistical mechanics for natural flocks of birds", *PNAS* 109, 4786 (2012)†; Nguyen, Zecchina & Berg, "Inverse statistical problems", *Adv. Phys.* 66, 197 (2017)†; Aurell & Ekeberg, *PRL* 108, 090201 (2012)†.

## The model

Each agent i is a binary spin s_i ∈ {−1, +1}. The pairwise maximum-entropy model is the least-structured distribution that reproduces every mean ⟨s_i⟩ and every pairwise correlation ⟨s_i s_j⟩:

$$P(\mathbf s) = \frac{1}{Z}\exp\Big(\sum_i h_i s_i + \sum_{i<j} J_{ij} s_i s_j\Big)$$

The fields h_i and couplings J_ij are **inferred** from data, not assumed. J_ij > 0 means i and j tend to be in the same state beyond what their individual rates explain; J_ij < 0 means they tend to be opposite.

**Inference options**, in rough order of accuracy versus cost:
- **Exact (Boltzmann learning):** gradient ascent on the likelihood, computing Z by enumerating all 2^N states. Feasible for N ≲ 20, which covers most windows of the village.
- **Pseudolikelihood:** fit each spin's conditional P(s_i | s_{−i}) by logistic regression. Consistent, fast, scales to large N.
- **Mean-field and TAP inversion:** J ≈ −(C⁻¹)_ij from the connected correlation matrix C. Instant, but biased when couplings are strong.

## Interesting behavior

- **Weak pairwise couplings, strong collective states.** Small J_ij can still make some joint states (everyone active, everyone silent) far more likely than an independent model predicts. That is the main finding of Schneidman et al. 2006 for retinal neurons.
- **Pairwise sufficiency.** The multi-information I_N = Σ S(s_i) − S(**s**) measures total correlation. The fraction (S_1 − S_2)/(S_1 − S_N) says how much of it pairwise couplings explain. Here S_1 is the entropy of the independent model, S_2 of the pairwise model and S_N the true entropy. Values near 1 mean higher-order interactions are unnecessary.
- **Signatures of criticality.** Add a fictitious temperature, P_T ∝ P^{1/T}. If the heat capacity C(T) peaks near T = 1, the real system sits close to a critical point. A related signature is Zipf's law: the rank-frequency plot of joint states has slope ≈ −1. Neurons and flocks show both (Mora & Bialek 2011).
- **Frustration and an energy landscape.** Negative couplings around a triangle (J_ij J_jk J_ki < 0) mean no configuration satisfies all three. Frustrated systems have many local energy minima. Each minimum is a metastable collective state, a candidate "faction" or "mode" of the swarm.
- **Collective modes.** The leading eigenvectors of J show which groups of agents switch together.

## Mapping to the village

- **Spin:** a binary state per agent per time bin. Natural choices:
  - **active / silent:** emitted any event, or any `AGENT_TALK`, in the bin
  - **on-topic / off-topic:** working on the current village goal or not
  - **agree / disagree:** stance on a contested proposal
- **Ensemble:** time bins inside one stationary window are treated as samples. For example, 1-minute bins over a month of village hours give roughly 10⁴ samples, which is enough for N ≈ 10–15.
- **Population:** only agents present for the whole window (see Population in `../DEFINITIONS.md`). The roster changes, so each window has its own N.

## How to fit

1. Choose the spin definition, bin width Δt and window. Check stationarity within the window: rates should not drift.
2. Fit the independent model (h only) and the pairwise model. Compare their log-likelihoods on held-out bins.
3. Report pairwise sufficiency, the J matrix, its eigenvectors, frustrated triangles and C(T).
4. Redo with several bin widths. Couplings that change sign with Δt are not trustworthy.

## Nulls and controls

- **Circular shift:** shift each agent's time series by a random lag. This keeps each agent's own statistics but destroys cross-correlations. J should drop to near zero.
- **Common drive:** goal changes, human messages and time of day push everyone together, which looks like J > 0. Use time-dependent fields h_i(t), or condition on the drive, and see what survives.
- **Scheduler artifacts:** check how `villages.turn_id` and `active_agent_id` work. If the scaffolding lets only one agent act at a time, mutual exclusion forces J_ij < 0 everywhere. That would be a property of the software, not of the agents.

## Susceptibility

How strongly the swarm responds to a push. Two routes; this model gives the first, model 02 the second.

- **From fluctuations (exact within the model).** For the max-ent form, with temperature absorbed into J and h:

  $$\chi_{ij} \equiv \frac{\partial\langle s_i\rangle}{\partial h_j} = \langle s_i s_j\rangle - \langle s_i\rangle\langle s_j\rangle = C_{ij}, \qquad \chi = \frac{1}{N}\sum_{ij} C_{ij} = N\,\mathrm{Var}(m)$$

- **Mode-resolved.** Diagonalize C. The top eigenvalue λ_max is the susceptibility of the softest collective mode, and its eigenvector says which agents move together when the swarm is pushed. In mean field χ ∝ (1 − J)⁻¹, which diverges as J's top eigenvalue → 1.
- **Distance to criticality.** Rescale the fitted model by a fictitious inverse temperature, P_β ∝ P^β. Compute χ(β) and the heat capacity C(β) by Monte Carlo, or by exact enumeration for N ≲ 20. A peak near β = 1 means the real swarm sits near a critical point.
- **Per goal period** these are the cheapest summaries available: binned activity only, no order parameter needed. See `hypotheses/hypohypotheses/phase-diagrams.md` (entry 2b).
- **Caveat.** χ = C is the fluctuation–dissipation theorem, which assumes equilibrium. In the village it's an equal-time summary, not a guaranteed response. Compare it with measured responses (model 02); the mismatch is informative.

## Mean-field forward version (no N×N inference)

At N ≲ 30 with short windows, inferring every J_ij is data-hungry and fragile. The forward alternative: posit a few-parameter mean-field model, estimate it from macroscopic moments, and test its predictions on observables not used in the fit.
- **Curie–Weiss with a time-varying field:** m = tanh(β(J₀ m + h(t))). The fluctuation relation χ = N Var(m) = β(1−m²) / (1 − βJ₀(1−m²)) gives βJ₀ from the observed mean and variance (a two-moment inversion). βJ₀ → 1 is criticality. HH80.
- **Free energy:** f(m) = −J₀m²/2 − hm − T s(m) is a double well for βJ₀ > 1, giving bistability and hysteresis. HH86.
- **Block models:**
  - rooms as sublattices (J_in, J_out), HH82;
  - model families as K mean-field populations with a K×K coupling matrix, HH89.
- **Spin-glass placement by moment matching:** the mean and spread of couplings from the correlation matrix's first two moments, placed on the Sherrington–Kirkpatrick diagram without full inference. HH87. Tested as the SK spin-glass and aging variant (H20, H22): rejected. See "Named variants".
- **Trade-off:** you give up agent-level heterogeneity, and gain robustness and *forward* falsifiability (faithfulness axis D). A good default before (or instead of) the full inverse problem.

## Pitfalls

- **Significant-bond graphs are power-limited** (H49, 2026-10-04): at village sampling J = 0.5 bonds are recovered with recall 0.34–0.89 and percolation is rarely detectable; check CV-C10 (dense vs dilute), split-half bond reliability and the mean-z shift of all pairs before reading a bond graph. Regime-III activity excess after day-edge trimming is a weak uniform shift (dense or shared field), not sparse strong bonds; pairwise structure exists in talk.
- **A day-level common data loss inflates whole-unit λ₁ against cross-day nulls** (RE-A1, 2026-10-04): the activity_bins bug dropped a day-specific share of every agent's events, which acts as a shared day field; cross-day surrogates destroy it and report a collective mode. Trim to the all-present window and use a block-shift edge.
- **Compare channels at matched time resolution** (H26): an equal-time gain J measured on day means reads J(2 − J), so a 1-min activity gain and a day-mean content gain are not comparable. HH108's "content near-critical, activity subcritical" gap came from exactly this mismatch plus drives.
- **Equal-time gains grow with N and miss delayed coupling** (H25, 2026-10-04): at fixed pair correlation ρ̄, g = 1 − 1/VR rises with headcount, so a bigger swarm looks closer to criticality with no change in coupling; compare ρ̄. The equal-time variance ratio reads ≈ 0 when agents react 2–8 min later (read-out gating, H08), so use lagged or Hawkes estimators for slow coupling.
- **Signed bonds from ordinal labels** (H37, 2026-10-04): stance labels map onto bond signs J_ij (support ferromagnetic, oppose antiferromagnetic). After removing speaker/target fields, sign-shuffle and FDR nulls are anti-conservative (10–28% false camps); calibrate against a parametric agent-field null. Stance recovered assigned #12 debate teams (7/10 exact) but found no camps where no protocol assigns sides.
- **Coupling scales as N^−0.6, not J/N** (H18, 2026-10-03): per-pair uptake falls sub-linearly with room size. Mean-field fits that assume J/N normalization will mis-scale across periods of different size.
- **The equal-time dial reads fields as gain** (H67, 2026-10-04): on real call grids g = 1 − 1/VR is not blind to hop-1 coupling, and it counts fast shared fields as coupling. In regime I it reads ≈ 0.16 where read-out coupling is ≈ 0 (g_eq − g_lag median +0.17). Use the read-out loop gain g_lag with the matched-lag in-flight placebo; report g_eq − g_lag as field contamination.

- This is an **equilibrium** model: it only sees equal-time correlations, which are symmetric. Directed influence (i talks, then j replies) is invisible here. That is what model 02 is for.
- Small N and short windows give noisy J. Regularize (L1 or L2) and report uncertainty by bootstrapping over days.
- A heat-capacity peak can be a finite-size or sampling artifact. Compare against the same analysis on shuffled data.
- **Multi-information at swarm rates (H101):** raw I₂/I_N stays near 1 (0.89–0.95) even with a planted group term, so it is uninformative. Subset marginalization creates real subset-level higher order (17–33% false positives in pairwise worlds). A heterogeneous shared field leaves a larger remainder than a 4-agent group term. First-order bias corrections fail; use parametric bootstraps.
- **Agent-level content disorder in shared-goal weeks is mostly style** (H98): the random-field contrast with #51 appears only after style residualization (raw disorder ratios 0.74–0.79 in contrast weeks).

## Collective modes

The eigenmodes of the agent correlation matrix (random-matrix edges, the uniform "market" mode, spiked-mode detection, mode lifetimes) have their own folder: [17 · Collective modes](../17-collective-modes/). H12, H91 and H92 used them under this model.

## Named variants

Added 2026-10-07. Each entry: what the variant changes, the cards and the latest verdict.

- **Random-field Ising / O(n)** (H98): each agent has a static random field (its role, project or prior); pair couplings are weak. In #51 the random-field share is R 0.67–0.73, against 0.24–0.53 in shared-goal weeks #38–#41 (after style removal). **Verdict:** failed as posed; the static random field holds, but the dynamics are not independent of it (the niche acts through reads and replies).
- **Barkhausen avalanches / zero-temperature random-field Ising** (H104): a stepped field should release bursts of switches with a crackling-noise tail. In #51, switching after a human message is ×1.09 [0.84, 1.32] (work) and ×1.07 [0.97, 1.18] (attention) the time-shuffle null; a planted τ = 3/2 avalanche gives ×1.87 and ×1.25. **Verdict:** failed (powered); the tail is not identifiable.
- **Sherrington–Kirkpatrick spin glass and aging** (H20, H22; see "Spin-glass placement" above): H20 finds no content aging in 29 periods (random-effects A +0.020 bge, +0.022 gte), only a kickoff relaxation of about 4 active days. H22 finds no spin glass in #51: rivals co-move (read pull Γ +0.19 [+0.07, +0.31]). **Verdict:** rejected.
- **Dilute ferromagnet / percolation** (H49): after day-edge trimming, regime III has 38 significant positive bonds over 4,318 pairs against ≈ 23 expected false ones. The bond graph is below percolation; the excess is a weak shift shared by all pairs. **Verdict:** refuted (a dense shared mode, not clusters).
- **Exchange bias / hysteresis** (H110): an agent's own artifact pins its old goal state. Pinned agents keep more of the old state on day 1 (difference 0.30 [−0.01, 0.57] bge), but the effect is gone by day 2, is not tied to continued commits, and reverses under the any-repo definition. **Verdict:** mixed; the exchange-bias signature fails.

## Hypothesis seeds

- Pairwise sufficiency is high (> 0.9) for active/silent spins: the swarm's activity patterns are explained by pairwise "who works with whom".
- The inferred J has block structure aligned with model family (Claude, GPT, Gemini) even after controlling for common drive.
- Collaborative goals pull the swarm toward criticality (C(T) peak near T = 1); "pick your own goal" periods sit in the disordered phase (peak at T > 1).
