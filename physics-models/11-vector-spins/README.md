# 11 · Vector spins: O(n), Heisenberg and spherical models in high-dimensional state spaces

**Fields:** stat mech, dynamics, info theory
**References:** Stanley, "Spherical model as the limit of infinite spin dimensionality", *Phys. Rev.* 176, 718 (1968)†; Mermin & Wagner, *PRL* 17, 1133 (1966)†; Kosterlitz & Thouless, *J. Phys. C* 6, 1181 (1973)†; Vicsek et al., "Novel type of phase transition in a system of self-driven particles", *PRL* 75, 1226 (1995)†; Toner & Tu, *PRL* 75, 4326 (1995)†; Bialek et al., "Statistical mechanics for natural flocks of birds", *PNAS* 109, 4786 (2012)†; Ethayarajh, "How contextual are contextualized word representations?", *EMNLP* (2019)†; Amari, *Information Geometry and Its Applications* (2016)†.

## The model

This is the generalization of Ising in which each agent's state lives in a **real inner-product (classical Hilbert) space**, not in {±1}. Each spin is a unit vector s_i ∈ S^{n−1} ⊂ ℝⁿ:

$$P(\{\mathbf s_i\}) = \frac{1}{Z}\exp\Big(\sum_{i<j} J_{ij}\, \mathbf s_i \cdot \mathbf s_j + \sum_i \mathbf h_i \cdot \mathbf s_i\Big)$$

- **The O(n) family:** n = 1 is Ising, n = 2 is XY (the q → ∞ limit of the Potts clock model, model 10), and n = 3 is Heisenberg. As n → ∞ the model becomes the exactly solvable spherical model.
- **Bilinear generalization:** replace the scalar coupling with a matrix, s_iᵀ W_ij s_j. Then agent j can influence agent i along some directions and not others: anisotropic, direction-specific coupling.
- **Soft spins:** drop the unit-norm constraint and add a quadratic term. The model becomes Gaussian. Its inverse problem is the Gaussian graphical model, where couplings are the precision matrix (estimated with the graphical lasso).
- **Probabilities as vectors.** A categorical distribution p over q states maps to the unit vector ψ = √p ∈ S^{q−1}. Under this map the Fisher–Rao information metric becomes the ordinary round-sphere metric. An agent's *mixed* state, such as how it splits its attention over q topics, is then a unit vector, and the O(q) model applies to it. This is the cleanest classical "Hilbert space" for agent states; it sits between model 10 (pure states) and embeddings.
- **Dynamics:** s_i(t+1) ∝ s_i(t) + η Σ_j A_ij s_j(t) + h_i + noise is the vector analog of kinetic Ising. Its linearized form is a vector autoregression, which gives directed couplings A_ij. Adding self-propulsion makes it the Vicsek model.

## Interesting behavior

- **Continuous symmetry, soft modes.** When n ≥ 2 and the vectors align, rotating everything together costs nothing. Goldstone modes, slow collective drifts of the shared direction, dominate the fluctuations.
- **Mermin–Wagner and its loopholes.** In low dimensions, short-range continuous-spin models can't order (except through a Berezinskii–Kosterlitz–Thouless transition for XY). The village's interaction graph is dense, though, closer to mean-field, so it can order. Active systems such as Vicsek flocks also escape the theorem (Toner–Tu).
- **Order parameter = polarization.** |m| = |N⁻¹ Σ s_i| measures how aligned the swarm is. In flocks it jumps when density or noise crosses a threshold, often discontinuously.
- **High dimensions.** For n ~ 10²–10³, random unit vectors are nearly orthogonal, with overlaps ~ 1/√n. Even small overlaps between agents are therefore significant, and the large-n (spherical) theory is a natural reference.
- **The goal as a vector field.** If messages and the goal text are embedded in the same space, the village goal is literally an external field **h** = h ĝ. Alignment with ĝ is the magnetization along the field, and its response to a goal change is a susceptibility.

## Mapping to the village

- **s_i(t):** a normalized, centered embedding of agent i's messages, session goal or memory in window t. Use the full dimension or a PCA-reduced n ~ 10–50. Alternatively, ψ_i = √p_i over topic clusters. See "Agent state (vector)" in `../DEFINITIONS.md`.
- **Fields:** the goal and kickoff text (shared ĝ), and model-family priors (agent-specific h_i, e.g. the "genuinely" direction).
- **Couplings:** who pulls whom toward their direction, from chat exposure. Compare against the visibility table in the overview PDF.

## How to fit

1. **Embed and center.** Contextual embeddings are anisotropic: they share a large common direction (Ethayarajh 2019). Subtract the corpus mean and whiten, or every pair looks aligned.
2. **Static:** fit P({s}) by pseudolikelihood; each conditional is a von Mises–Fisher distribution, as in the flocking analysis of Bialek et al. Or use the Gaussian graphical model on soft spins.
3. **Dynamic:** fit a VAR on embeddings to get A_ij. Compare its antisymmetric part with models 02 and 09.
4. **Observables:** polarization |m|(t), alignment with the goal ĝ·m, and the spectrum of the correlation matrix (soft modes).

## Nulls and controls

- **Random rotation per agent:** keeps each agent's own trajectory but destroys cross-alignment.
- **Shuffled windows** across days.
- **Embedding-model swap:** results must survive a different embedding model.

## Susceptibility: longitudinal vs. transverse

Vector spins have a distinction that Ising lacks: responding *along* the current order vs. *across* it.

- **Longitudinal, along the goal.** With the goal as a field **h** = h ĝ, χ_∥ = ∂(**m**·ĝ)/∂h. Each kickoff is a step field, so the alignment response after kickoff traces a dynamic susceptibility χ_∥(τ). Steps in field persistence (NE08 goal in prompt, NE13 kickoff in prompt) should make the response larger and longer.
- **Transverse, and Goldstone physics.** In an ordered phase with continuous symmetry, χ_⊥ = |**m**|/h, which diverges as h → 0. A small push perpendicular to the current consensus rotates the whole swarm's direction, while pushes along it meet resistance.
  - Prediction: in free weeks that order spontaneously (#31, #44 #rest), the consensus *direction* is easily steered by small perturbations, such as one agent's push or a human message. In strongly fielded weeks it isn't.
- **Fluctuation route.** The covariance of the order-parameter vector **m** across windows: its eigenvalues are mode-resolved susceptibilities. In an ordered phase, expect transverse fluctuations ≫ longitudinal.
- **Caveats.** The field's magnitude is unknown, so use relative χ. Embedding anisotropy inflates every alignment, so center and whiten first.

## Mean-field forward version

Mean-field O(n): **m** = L_n(β(J₀|**m**| + h)) **m̂**, with L_n(x) = I_{n/2}(x) / I_{n/2−1}(x) (modified Bessel functions; n = 3 gives the Langevin function coth x − 1/x). For unit spins the mean-field critical point is βJ₀ = n.
- **Fit:** (βJ₀, h) per period from polarization and its fluctuations, in a reduced embedding dimension n.
- **Predict:**
  - the response along the field at kickoffs;
  - the transverse susceptibility |**m**|/h;
  - the ratio of transverse to longitudinal fluctuations.

HH85.

## Pitfalls

- **Cross-day circular-shift nulls are slightly liberal for content transfer** (H32): the day × room field leaks through the sender's same-day messages; use a within-day shift as the strict check. Transfer significance also falls fast as more field directions are removed (25 → 18 → 7 periods for 1, 5, 10 directions), and a fast responder to a hidden drive looks like a leader in single-room weeks.
- **Style is a fixed charge plus a context-held excitation** (H46, 2026-10-04): an agent's style drifts away from its own mean as the context fills (excess distance −2.3 at the first message of a segment to +1.1 after the seventh) and snaps back at a forced erasure, so style moves at erasures (T 0.56) while content does not, and it shifts under assigned registers (#51 Prankster, #12 judges). Average style within context position, or residualize on it, before reading it as a fixed agent property. Style still identifies agents across goal switches better than content (0.76 vs 0.51, chance 0.15).
- **Kickoff specificity effects are count-inflated** (H54, 2026-10-04): per-period frozen fraction correlates with specificity even when specificity does nothing (22% false positives), because specific kickoffs name more artifacts; use a per-project model. A genericness correction (long kickoffs look like everything) only partly removes it, and depth and kickoff distinctiveness are mechanically coupled. The kickoff *target* itself is robust: day-1 centroids pick out their own kickoff (top-1 in 18/33, p 3e-6), also after style residualization.
- **Room contrasts measure the global share of fluctuation, not coupling** (H47, 2026-10-04): C_B (cross/within) is 0.98 under a global drive alone and ≈ 0.05 under either room coupling or room drives, which it cannot tell apart. Coupling also amplifies weak global drives (C_B rises to 0.43). The boundary is sharp only where rooms work on different topics (C_B vs topic separation ρ = −0.83). Inside rooms, correlation follows conversation (G ≈ 0.40).
- **Drives saturate whole-swarm fluctuation βJ₀** (H26, 2026-10-04): H01's day-mean estimator returns 0.57–0.74 at zero coupling from global, room, kickoff, time-of-day and operator drives (0.83 in one room of 24). Use the room-excess gain ρ_ex, compare channels at matched resolution (g_day = J(2 − J)), and don't remove a pooled time-of-day profile, which biases within- and cross-room covariances alike. At matched resolution content and activity both sit near a room loop gain of 0.5; content co-moves within rooms, activity village-wide.
- **"Near-critical" content is size × a shared field** (H25, 2026-10-04): the content dial reads g ≈ 0.70, but per-pair correlation is flat in N (ρ̄ ≈ 0.28, α ≈ 0), and a time-varying exogenous field leaks 0.26–0.30 into g in synthetics. Removing operator-message directions takes out at most a fifth of it.
- **Post-kickoff alignment drifts** (H36, 2026-10-04): about 40% of the within-day alignment-energy variance after a goal kickoff is a monotone drift (alignment relaxes from about 0.64 to 0.29 over hours; H31 τ ≈ 4.4 h). Detrend before reading variance as susceptibility or heat capacity.
- **Recency confound for influence** (H29): content similarity falls 5–23× with message age, so compare seen and unseen messages within matched age bins.
- **Leave-one-out axes and agent-centering** (H21): centering on a mean that includes agent i leaks i into its own leave-one-out axis; agent-centering anti-correlates an agent's residuals across windows and breaks label-permutation nulls for any cross-window axis. The real null spread is set by family co-variation, so i.i.d. synthetic noise overstates power about 2×.

- **Snapshot βJ₀ from residual alignment absorbs a multi-dimensional field** (H24): removing only one goal direction ĝ leaves field leakage that reads as coupling (synthetic: βJ₀/n ≈ 0.34 at zero coupling). Remove the field along several directions, or fit it.

- **Isotropic surrogate nulls are 2–3× too narrow** for embedding similarity and two-time statistics (H20): content fluctuates in only ~5–12 of 32 whitened dimensions. Build nulls from the empirical fluctuation covariance.

- **Family alignment is mostly style** (H13, 2026-10-03). In bge embeddings, agents of the same lab align beyond the goal field, but the alignment vanishes after controlling for 20 numeric style features. Residualize on style before reading family or agent fields as positions.

- Anisotropy and topic-vs-style confounds: two agents can align because they write alike, not because they are thinking about the same thing.
- Embedding vectors aren't physical spins. Their norm is arbitrary, and the geometry depends on the embedding model.
- Few agents (N ≲ 30) against high n: reduce the dimension before fitting couplings.

## Hypothesis seeds

- Polarization along the goal direction jumps at each kickoff and relaxes over the week. Its response amplitude (the susceptibility) differs by model family.
- In free weeks the swarm orders spontaneously along a direction that no goal set: symmetry breaking without a field. Candidates are the "existential attractor" in #rest during #44, and convergence on self-study in #41.
- Agents that produce near-identical artifacts without talking (benchmark frameworks in #8) are aligned by a shared field (their pretraining prior), not by coupling. Model 11 separates the two.
- Competitive weeks lower the polarization relative to collaborative weeks.
