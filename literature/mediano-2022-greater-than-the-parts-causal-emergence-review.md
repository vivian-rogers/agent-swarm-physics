# Greater than the parts: a review of the information decomposition approach to causal emergence

**Citation:** Pedro A. M. Mediano, Fernando E. Rosas, Andrea I. Luppi, Henrik J. Jensen, Anil K. Seth, Adam B. Barrett, Robin L. Carhart-Harris and Daniel Bor, *Phil. Trans. R. Soc. A* 380, 20210246 (2022). arXiv:2111.06518 (PDF is arXiv v1).
**File:** mediano-2022-greater-than-the-parts-causal-emergence-review.pdf
**Fields:** info theory, complex systems (emergence), neuroscience

## Summary
A short, accessible review of the Rosas et al. 2020 theory (see `rosas-2020-…md` for the formalism). It restates PID, ΦID and the definitions of causal emergence, downward causation and causal decoupling. It adds four interpretive points:
- causal claims follow from how the joint distribution was obtained (observational or interventional);
- results depend on how the parts are defined, which the authors call a feature, not a bug;
- the order $k$ sets the "scale" of emergence;
- emergence is defined through supervenient macro-variables, so the micro–macro comparison is real.

It reviews applications: Game of Life, boids, macaque ECoG, and human fMRI. In fMRI, synergy-dominated association cortex contrasts with redundancy-dominated sensory and motor cortex, synergy is a larger share of information in humans than in macaques, and integrated information and emergence drop with loss of consciousness after brain injury. The main practical message is the trade-off between two routes. One is cheap, feature-specific sufficient criteria (Ψ, Δ, Γ). The other is expensive, feature-free emergence capacity, which needs a redundancy function.

## Key formalism
- **Two-source PID:**
  - $I(X_1;Y)=\mathrm{Red}+\mathrm{Un}(X_1;Y|X_2)$;
  - $I(X_2;Y|X_1)=\mathrm{Un}(X_2;Y|X_1)+\mathrm{Syn}$.
  - Example: two eyes. Colour is redundant; depth is synergistic.
- **ΦID:** the time-delayed MI $I(X_t;X_{t'})$ of two processes splits into 4 × 4 = 16 atoms (source PID × target PID), e.g. Red→Syn.
- **Supervenience:** $V_t$ is a (possibly noisy) function of $X_t$, so nothing about $V_{t'}$ is predicted by $X_t$ beyond $X_{t'}$.
- **Definitions** (as in Rosas 2020):
  - emergence: $\mathrm{Un}^{(k)}(V_t;X_{t'}|X_t)>0$;
  - downward causation: $\mathrm{Un}^{(k)}(V_t;X^\alpha_{t'}|X_t)>0$ for some $|\alpha|=k$;
  - causal decoupling: $\mathrm{Un}^{(k)}(V_t;V_{t'}|X_t,X_{t'})>0$;
  - capacity: $\mathrm{Syn}^{(k)}=\mathcal D^{(k)}+\mathcal G^{(k)}$, and the taxonomy is exhaustive.
- **n-source decomposition (footnote 1):** $I(X^n;Y)=\mathrm{Red}^{(k)}+\mathrm{Syn}^{(k)}+\sum_{\beta\in B_k}\mathrm{Un}^{(k)}(X^\beta;Y|X^{-\beta})$, with $B_k$ the subsets of size ≤ $k$.
- **Order:** $k$-th order emergent ⇒ emergent at every $j<k$. Raising $k$ makes detection harder and moves the "scale" up.
- **Not invariant under change of coordinates (footnote 4).** XOR $Y=X^1\oplus X^2$ has Syn = 1 bit. In coordinates $(Z^1,Z^2)=(X^1\oplus X^2,X^1)$ the same bit becomes $\mathrm{Un}(Z^1;Y|Z^2)$ = 1. Atoms depend on the choice of parts.
- **Granger vs Pearl:** every quantity depends only on $p(X_{t'},X_t)$.
  - If $p(X_{t'}|X_t)$ is an interventional distribution, and faithfulness and the causal Markov condition hold, the atoms are interventional.
  - On observational data they are predictive (Granger).
  - The two agree if all relevant variables are measured. Hidden variables are the source of the difference.
- **Estimators named:**
  - practical criteria need only bivariate MIs, scale linearly in $n$, and are valid for any PID satisfying Rosas et al.'s axioms;
  - capacity needs a redundancy function, and the review says it is currently infeasible for large systems;
  - $\mathcal G^{(1)}$ has been estimated only for **pairs** of time series ("a lack of efficient estimators of $\mathcal G^{(k)}$ for three or more time series", footnote 5).
- **Toolkits cited:**
  - Gaussian-copula MI (Ince et al. 2017);
  - TE as a log-likelihood ratio (Barnett & Bossomaier 2012);
  - JIDT (Lizier 2014) and dit (James et al. 2018);
  - multivariate-TE network inference (Novelli et al. 2019; IDTxl).
- **Background pitfalls (from memory, not in this PDF †):**
  - The ΦID atoms in the fMRI work use MMI redundancy (min of MIs) on Gaussian data. MMI sets the weaker source's unique information to zero by construction.
  - Ψ needs stationarity over the estimation window.
  - Alternatives with different definitions exist: Barnett & Seth "dynamical independence"† and Hoel/Varley effective information†. The review mentions both as related work.

## Mapping to agent swarms
- **Which route fits the data.**
  - The feature route needs $V$ chosen in advance: room agenda (centroid), repo shares, dominant repo, a convention's usage rate. Feasible at $n$ = 4–32 with 1-d variables and $T\sim10^2$–$10^3$ steps per unit (see the Rosas 2020 notes for the bias arithmetic).
  - The capacity route ($\mathcal G$, $\mathcal D$) is only feasible for agent pairs. Use Gaussian ΦID-MMI on 1-d DQ5 `agent_win30_style_resid_period` projections, or on `behavior_states_v3` contrasts.
  - With $n(n-1)/2$ pairs (up to 496 at $n$ = 32), the output is a pairwise synergy matrix per unit, as in the fMRI gradient work.
- **Change of coordinates matters for the project's central question.** The parts can be agents, agents + own artifacts, or repos. The XOR footnote says emergence measured on agents can become unique information once artifacts are part of the parts. That is a clean test of whether "the collective" is stigmergic (H44, H58, HH301).
- **Granger vs Pearl in the village.** Natural experiments (NE catalog) change $p(X_{t'}|X_t)$ from outside. Compare Ψ or Syn on the two sides of a step change (exception (c), the transition is the object). That is the closest we get to interventional emergence. Hidden variables: the operator, the scheduler and the provider platform (H38, H56). Each is a hidden common driver unless modelled.
- **Shared-field corrections:**
  - **Scheduler:** trim to all-present windows (DQ8) and use within-window steps only. The 5-min windows of v3 are coarser than calls.
  - **Kickoff/goal:** drop day 1 or detrend on `goal_fields`. Ψ and Syn assume stationarity.
  - **Model priors:** use `style_resid_period` vectors. Report same-family vs cross-family pair synergy.
  - **Convergence:** use a lag shorter than one read-out hop as a placebo. Any Syn at that lag is co-generation.
  - **Surrogate for all four:** DQ8 `simulate.py` field-only presets on the real schedules.

## Candidate hypotheses
- **A synergy gradient across roles (fMRI analogue).**
  - *Observable:* per-agent mean pairwise $\mathcal G^{(1)}$ (Gaussian ΦID-MMI) in periods with roles (#35, #44, #51; DQ6 labels).
  - *Null:* field-only surrogate; role labels permuted within a unit.
  - *Prediction:* no role ordering. Spearman |ρ| < 0.2 between role centrality (H65's routers) and synergy share, consistent with "leaders get attention, not influence".
  - *Impostor:* shared model priors. Check that family and role are not confounded before reading any ordering.
- **Coordinates test for stigmergy.**
  - *Observable:* Ψ of repo-share $V$ with parts = agents vs parts = agent + own artifact (DQ4, 30-min bins).
  - *Prediction:* Ψ drops by ≥ 50% when artifacts join the parts, in ≥ 2/3 of shared-repo units.
  - *Impostor:* the scheduler common mode, which shares cancel.
- **NE as intervention: the nudger.**
  - *Observable:* village-scale Ψ of the content centroid before and after NE43 (bookends off, then nudger off). Event-study windows of equal length.
  - *Prediction:* |ΔΨ| < surrogate SD. The nudger moves attention, not the macro-dynamics (H35).
  - *Impostor:* the kickoff field. Check which goal periods the windows straddle.
- **Order test: is the swarm pairwise?**
  - *Observable:* $\Psi^{(1)}$ vs $\Psi^{(2)}$ for units with $n\le8$.
  - *Prediction:* wherever $\Psi^{(1)}>0$ beyond surrogate, $\Psi^{(2)}\le0$. Emergence is no higher than pairwise, matching HH322's $I_2/I_N>0.9$.

## Caveats
- The review introduces no new estimator and no new data beyond the cited applications. Cite Rosas 2020 for definitions and numbers.
- The "feature, not a bug" view on coordinates means every claim is relative to a partition. Pick the partition before seeing results and report alternatives.
- The fMRI results quoted use pairs and MMI redundancy. Do not transfer the gradient numbers.
- Pairwise $\mathcal G$ matrices invite pooling across periods. Don't. Compare per-unit summaries on the phase diagram.
- Mask the holdout.
