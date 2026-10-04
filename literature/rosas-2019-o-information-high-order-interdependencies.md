# Quantifying high-order interdependencies via multivariate extensions of the mutual information

**Citation:** Fernando E. Rosas, Pedro A. M. Mediano, Michael Gastpar and Henrik J. Jensen, *Phys. Rev. E* 100, 032305 (2019). arXiv:1902.11239 (PDF is arXiv v1).
**File:** rosas-2019-o-information-high-order-interdependencies.pdf
**Fields:** info theory, stat mech (high-order interactions)

## Summary
The paper defines the O-information Ω, a symmetric, target-free measure of whether a set of $n$ variables is dominated by redundancy (Ω > 0) or synergy (Ω < 0). It starts from two views of interdependence. Total correlation (TC) measures collective constraints. Dual total correlation (DTC, "binding entropy") measures shared randomness. Ω is their difference. For $n$ = 3 it equals the interaction (co-)information. For larger $n$ it stays interpretable, unlike co-information. The $n$-bit copy and the $n$-bit XOR are its unique extremes. Ω is a sum of three-set interaction-information terms, and it costs only $O(n)$ entropies. Applications: random spin Hamiltonians (higher-order couplings make Ω more negative), TSE complexity (which tracks TC + DTC and cannot tell synergy from redundancy), and Baroque scores (Bach chorales are synergistic, Corelli is redundant).

## Key formalism
- **Total correlation:** $C(X^n)=\sum_j H(X_j)-H(X^n)$, the collective constraints.
- **Dual total correlation:** $B(X^n)=H(X^n)-\sum_j H(X_j|X^n_{-j})$, the shared randomness. $\sum_j H(X_j|X_{-j})$ is the residual (erasure) entropy.
- **O-information (Def. 1):** $\Omega(X^n)=C-B=(n-2)H(X^n)+\sum_{j}\big[H(X_j)-H(X^n_{-j})\big]$.
- **Lemma 1:** Ω is symmetric in the variables. $\Omega(X_1,X_2)=0$. $\Omega(X_1,X_2,X_3)=I(X_1;X_2;X_3)=$ Rdn − Syn (Williams–Beer co-information, sign as in the Williams notes).
- **Def. 2:** Ω > 0 is redundancy-dominated. Ω < 0 is synergy-dominated.
- **Bounds (Lemma 3):** $(n-2)\log|\mathcal X|\ge\Omega\ge(2-n)\log|\mathcal X|$. Also $0\le C,B\le(n-1)\log|\mathcal X|$.
- **Prop. 2:** Ω = $n-2$ bits iff $n$-bit copy. Ω = $2-n$ iff $n$-bit XOR. Co-information instead oscillates $(-1)^{n+1}$ for XOR.
- **Decompositions (Prop. 1, Cor. 1):**
  - Every path in the partition lattice gives Ω as a sum of interaction-information terms.
  - Assembly path: $\Omega(X^n)=\sum_{k=2}^{n-1}I(X_k;X^{k-1};X^n_{k+1})$.
  - For $n$ = 4: $\Omega=I(X_i;X_j;X_kX_l)+I(X_k;X_l;X_iX_j)$.
- **Local O-information:** $\omega_{ij}=I(X_i;X_j;X^n_{-ij})$. It can have the opposite sign to the global Ω.
- **Scale constraints (Prop. 3, Cor. 3–4):**
  - Large positive Ω forces every subset of size $m$ to be correlated once $\Omega\ge(n-m-1)\log|\mathcal X|$.
  - Large negative Ω upper-bounds the correlation of small subsets.
  - A strong pair (large $C(X^\gamma)$) prevents Ω from reaching its lower bound.
- **Superposition (Lemma 4, Cor. 5):**
  - Ω is additive over independent blocks, so redundant and synergistic sub-blocks cancel.
  - Disjoint pairwise structure gives exactly Ω = 0.
  - Overlapping pairwise (max-ent) models can have either sign.
- **Spin ensembles:** $n$ = 5, random Gaussian $J_\gamma$ up to order $k$, β = 0.1. Ω ≈ 0 at $k$ = 2 and becomes more negative as $k$ grows.
- **TSE:** TSE $\propto C+B$ (correlation > 0.97 on random distributions). TSE is identical for the 3-bit copy and the 3-bit XOR.
- **Music (13-symbol alphabets, "muts"):**
  - Bach chorales: Ω < 0; all six $\omega_{ij}$ between −0.02 and −0.05.
  - Corelli: Ω > 0, driven by viola–cello ($\omega$ = +0.17; both play the basso continuo). The two violins stay synergistic ($\omega$ = −0.04).

## Mapping to agent swarms
- **Variables:** one variable per agent in a unit. Candidates:
  - a 1-d content projection per 30-min window (DQ5 `agent_win30_style_resid_period`, unit PC1, both models);
  - a `behavior_states_v3` contrast (e.g. $p_{\text{execute}}$ − $p_{\text{communicate}}$) per 5-min window;
  - a binary "commits to the unit's top repo in this bin" from DQ4.
- **Gaussian estimator:** $H=\tfrac12\log\det(2\pi e\Sigma)$, so Ω needs $n$ + 1 log-determinants. Use the analytic Gaussian entropy bias correction or a shuffle null.
- **Sizes and identifiability:**
  - $n$ = 4–32 agents and $T\sim10^2$ (30-min) to $10^2$–$10^3$ (5-min) steps per unit.
  - Keep $T\ge10n$. Above $n$ ≈ 16, use random 8–12 agent subsets and report the distribution.
  - Discrete plug-in Ω on 11 Jev states is only identifiable for triplets ($11^3$ = 1331 cells needs $T\gg10^3$). Binary states allow $n\le6$–8.
  - Autocorrelation lowers the effective $T$. Use block bootstrap for errors, as in the paper (circular blocks).
- **Shared-field corrections:**
  - **Scheduler, kickoff, priors:** a common driver makes every agent a noisy copy. That is the Corelli bass line: Ω > 0. Residualize on exogenous fields (schedule masks, `goal_fields` kickoff vector, the agent's leave-period-out mean) before computing Ω. Then compare with the same Ω on `simulate.py` field-only skeletons.
  - **Hard constraints are an impostor for synergy.** A fixed budget is a collective constraint, i.e. a pure-TC structure. In the Gaussian limit $X_n=-\sum_{i<n}X_i$, Ω → −∞. Ω < 0 then appears with no integration. Examples:
    - shares that sum to 1 across agents;
    - a fixed number of concurrent call slots;
    - turn-taking imposed by the runner.
    So never use within-unit shares as variables. Check how the runner allocates slots in each regime before trusting Ω < 0 on activity.
  - **Contemporaneous convergence:** same-step responses to the same field are redundancy. Lagged (cross-time) versions need the dynamic O-information (Stramaglia et al. 2021†), not in this paper.
- **Local terms:** the $\omega_{ij}$ (and the gradient of Ω, Scagliarini et al. 2023†) locate which pairs carry the synergy. Read-out-cone pairs (H41) vs across-room pairs are the natural contrast.

## Candidate hypotheses
- **HH298 sharpened: residual synergy inside read cones.**
  - *Observable:* Gaussian Ω and the $\omega_{ij}$ on residualized 1-d content per 30-min window, within rooms vs across rooms, per unit.
  - *Null:* field-only `simulate.py`, plus block-shifted agents (DQ8 trims).
  - *Prediction:* raw Ω > 0 in ≥ 90% of units. After residualization, the median Ω/(n−2) is in [−0.02, +0.02] nats. Negative $\omega_{ij}$ is enriched by ≥ 1.5× among pairs with mutual reads in the window, relative to unread pairs.
  - *Impostor:* contemporaneous convergence. In-flight pairs must not show the same enrichment.
- **Copy duplicates look like Corelli.**
  - *Observable:* $\omega_{ij}$ for pairs flagged by DQ5 `cross_echo_both` vs unflagged pairs.
  - *Prediction:* echo pairs have the largest positive $\omega_{ij}$, but the global Ω sign does not change when they are removed.
  - *Impostor:* shared model priors. Same-family pairs should not explain it after `style_resid_period`.
- **Behavior is pairwise (links HH322).**
  - *Observable:* plug-in Ω over all triplets of binary execute/communicate states (5-min, DQ8-trimmed), vs a pairwise max-ent fit.
  - *Prediction:* the observed Ω minus the pairwise-model Ω lies within ±0.01 bits for ≥ 90% of triplets. Activity has no higher-order structure beyond the scheduler.
  - *Impostor:* the scheduler field. Use trimmed windows, and residualize on the all-present mask.
- **Synergy at division of labor, if any, is not budget closure.**
  - *Observable:* Ω on binary "works on repo r" indicators per agent in #40, #44, #51.
  - *Prediction:* negative Ω appears only in periods with an explicit task split (`has_roles`, `has_teams` in `period_affordances`). It disappears in a surrogate that keeps each agent's marginals and the per-bin count of busy agents.
  - *Impostor:* the hard constraint itself, i.e. the number of active slots.

## Caveats
- Ω reports only the balance. Ω ≥ 0 does not rule out synergy, and Ω ≈ 0 can hide redundancy and synergy cancelling (Lemma 4). Always report the $\omega_{ij}$ or subset values, and PID atoms where a target exists (Williams–Beer notes).
- Ω is zero-lag. It says nothing about dynamics or causation.
- The bounds scale with $n$. Normalize (e.g. Ω/(n−2)) before placing units of different $N$ on a phase diagram.
- Gaussian Ω on non-Gaussian, bounded, compositional data (probability vectors, shares) is unreliable. Transform first (log-ratio, rank-Gaussianization) or use discrete estimators.
- Within-unit only. Never pool periods.
