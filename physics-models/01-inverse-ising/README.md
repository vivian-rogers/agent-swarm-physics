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

## Pitfalls

- This is an **equilibrium** model: it only sees equal-time correlations, which are symmetric. Directed influence (i talks, then j replies) is invisible here. That is what model 02 is for.
- Small N and short windows give noisy J. Regularize (L1 or L2) and report uncertainty by bootstrapping over days.
- A heat-capacity peak can be a finite-size or sampling artifact. Compare against the same analysis on shuffled data.

## Hypothesis seeds

- Pairwise sufficiency is high (> 0.9) for active/silent spins: the swarm's activity patterns are explained by pairwise "who works with whom".
- The inferred J has block structure aligned with model family (Claude, GPT, Gemini) even after controlling for common drive.
- Collaborative goals pull the swarm toward criticality (C(T) peak near T = 1); "pick your own goal" periods sit in the disordered phase (peak at T > 1).
