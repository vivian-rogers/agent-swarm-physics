# Reconciling emergences: an information-theoretic approach to identify causal emergence in multivariate data

**Citation:** Fernando E. Rosas, Pedro A. M. Mediano, Henrik J. Jensen, Anil K. Seth, Adam B. Barrett, Robin L. Carhart-Harris and Daniel Bor, *PLOS Comput. Biol.* 16, e1008289 (2020). arXiv:2004.08220 (PDF is arXiv v1).
**File:** rosas-2020-reconciling-emergences-causal-emergence.pdf
**Fields:** info theory, complex systems, stat mech (emergence, coarse-graining)

## Summary
The paper defines causal emergence with partial information decomposition (PID) and its two-time extension, ΦID. A supervenient macro-feature $V_t$ (a function of the parts, possibly noisy) is emergent if it predicts the system's future in a way that no part, or no group of $k$ parts, does on its own. A system can have such a feature if and only if its parts are dynamically synergistic about their own future. ΦID splits this emergence capacity into **downward causation** (the whole predicts specific parts) and **causal decoupling** (the whole predicts its own macro-future, beyond any part). The full atoms need a redundancy function and much data. The paper also gives three cheap, PID-free sufficient criteria, Ψ, Δ and Γ, which use only pairwise mutual informations. Test cases: Game of Life particles, Reynolds boids, macaque ECoG → wrist position. "Causal" here means Granger-type prediction on observational data. It means do-calculus only when the joint distribution comes from interventions.

## Key formalism
- Parts $X_t=(X^1_t..X^n_t)$; feature $V_t$ supervenient: $V_t - X_t - X_{t'}$ is a Markov chain for all $t'>t$.
- $k$-th order synergy $\mathrm{Syn}^{(k)}(X_t;X_{t'})$: the sum of PID atoms whose every collection has more than $k$ sources. $k$-th order unique information $\mathrm{Un}^{(k)}(V_t;X_{t'}|X_t)$: what $V$ carries that no group of ≤ $k$ parts has.
- **Def. 1:** $V$ is causally emergent of order $k$ iff $\mathrm{Un}^{(k)}(V_t;X_{t'}|X_t)>0$. **Lemma 1:** this requires $n\ge2$ and $V\neq g(X^j)$ for every single part.
- **Theorem 1:** an emergent feature exists iff $\mathrm{Syn}^{(k)}(X_t;X_{t'})>0$. **Corollary 1:** $\mathrm{Un}^{(k)}(V_t;X_{t'}|X_t)\le \mathrm{Syn}^{(k)}$, so this synergy is the "emergence capacity".
- **Taxonomy (ΦID):** $\mathrm{Syn}^{(k)}=\mathcal G^{(k)}+\mathcal D^{(k)}$.
  - $\mathcal D$ (downward causation): synergistic sources → targets of size ≤ $k$. Def. 2: $\mathrm{Un}^{(k)}(V_t;X^\alpha_{t'}|X_t)>0$ for some $|\alpha|=k$.
  - $\mathcal G$ (causal decoupling): synergistic → synergistic. Def. 3: $\mathrm{Un}^{(k)}(V_t;V_{t'}|X_t,X_{t'})>0$. "Pure" decoupling: no effect on any part (Example 1, conserved parity).
- **Practical criteria ($k=1$; Eq. 10):**
  - $\Psi_{t,t'}(V)=I(V_t;V_{t'})-\sum_j I(X^j_t;V_{t'})$
  - $\Delta_{t,t'}(V)=\max_j\big[I(V_t;X^j_{t'})-\sum_i I(X^i_t;X^j_{t'})\big]$
  - $\Gamma_{t,t'}(V)=\max_j I(V_t;X^j_{t'})$
  - **Prop. 1:** Ψ > 0 ⇒ $V$ is emergent. Δ > 0 ⇒ downward causation. Ψ > 0 with Γ = 0 ⇒ causal decoupling. In practice the paper reads Γ ≪ Ψ as "suggests decoupling".
  - Order $k$ (App. D): the sums run over all $k$-plets $\alpha$, i.e. $\binom nk$ terms.
- **Direction of error:** these are whole-minus-sum measures. They count redundancy up to $n$ times. Redundancy pushes Ψ and Δ down, so the criteria give false negatives, not false positives. **Ψ < 0 is inconclusive.**
- **Exact route (Sec. III B):** synergistic channels $V\perp X^\alpha\ \forall|\alpha|=k$. $\mathrm{Syn}^{(k)}_\star=\sup I(V;X_{t'})$, $\mathcal G_\star$ uses channels at both ends, $\mathcal D_\star=\mathrm{Syn}_\star-\mathcal G_\star\ge0$. Prop. 2: for stationary $X$, every autocorrelated synergistic observable is emergent. Feasible only for small systems.
- **Numbers (arXiv v1):**
  - GoL, 15×15 board, $5\times10^4$ collider runs, particle-type $V$, quasi-Bayesian MI estimator: Ψ = 0.58 ± 0.02, $I(V_t;V_{t'})$ = 0.99, Γ = 0.009.
  - Boids, $N$ = 10: Ψ > 0 only at intermediate avoidance $a_2$. At low $a_2$, $\sum_i I(X^i;V')$ exceeds $I(V;V')$ (redundancy). At high $a_2$, $I(V;V')$ is small.
  - ECoG, 64 channels → 3-d wrist decoder (PLS + SVM, trained on a training set, Ψ computed on held-out data with JIDT): Ψ = 1.275 at lag 8 ms, Γ = 0.049. Ψ > 0 up to lag ≈ 0.2 s.

## Mapping to agent swarms
- **Parts $X^i_t$:** agent $i$'s state per step. Candidates:
  - its content projection: DQ5 `agent_win30_style_resid_period` (30-min windows) reduced to the unit's top 1–3 PCs, both embedding models;
  - its `behavior_states_v3` probability vector `p_*` (5-min windows), reduced to one or two contrasts;
  - its DQ4 allocation (which repo, from agent `work_commits` in 30-min bins).
- **Macro $V_t$:** the room or village agenda (content centroid, HH297), the repo-share vector, or the unit's dominant repo. $V$ must be fixed in advance or fitted on other days (the ECoG decoder was fitted on training data). A PCA fitted on the test window overfits and inflates $I(V_t;V_{t'})$.
- **Sizes:**
  - $n$ = 4–32 agents per unit; 71 non-holdout units; 283 days, i.e. about 4 days per unit on average.
  - Agent-day vectors give $T\approx4$ per unit, which is useless for Ψ within a unit.
  - 30-min windows give $T\sim10^2$. Five-minute behavior windows give $T\sim10^2$–$10^3$: 203k labelled agent-windows over the corpus, about 2.9k per unit.
- **Identifiability:**
  - Gaussian MI bias is ≈ $pq/2T$ nats per term. With 1-d $V$ and 1-d parts, $n$ = 16 and $T$ = 100, the sum carries ≈ 0.08 nats of upward bias, which pushes Ψ down by about that much. With 3-d parts the bias is ≈ 0.7 nats, larger than any plausible signal.
  - So: use 1-d parts, $T\ge100$, $n\le16$ (or random subsets of 16), and a shuffle or analytic bias correction.
  - Order $k$ = 2 needs $\binom n2$ terms, so only units with $n\le8$.
  - The exact ΦID route ($\mathcal G$, $\mathcal D$) only works on pairs of agents.
- **Shared-field corrections (the four impostors):**
  - A *slow common field* (kickoff/goal, shared model priors) is redundancy counted $n$ times. It pushes Ψ **down** and masks emergence. In a one-factor Gaussian model $X^i=F+\epsilon_i$ with AR(1) $F$, Ψ ≤ 0 at every noise level (my calculation; check it on `simulate.py`).
  - A *fast common-mode nuisance* that $V$ cancels pushes Ψ **up** without integration. Example: the scheduler's start/stop field, if $V$ is a share, a contrast or a per-step-normalized centroid. Each part is dominated by the nuisance, while $V$ is clean.
  - So the sign of the bias depends on the field and on $V$. Raw Ψ is not simply "inflated".
  - Correction: compute the same Ψ on DQ8 `simulate.py` skeletons with field-only presets (rate-matched independent agents plus global, room, time-of-day and day fields, on the real schedule). Report Ψ − (surrogate 95th percentile).
  - *Contemporaneous convergence:* use a lag $t'-t$ shorter than the read-out hop (H41: one hop per 1.5–5 talk calls) as a placebo lag.
  - Condition only on exogenous variables: the kickoff vector (`goal_fields`) and the schedule masks. Operator nudges respond to agents (H35), so conditioning on them can create synergy.

## Candidate hypotheses
- **HH297 sharpened: the agenda is not emergent beyond the field.**
  - *Observable:* $\Psi^{(1)}$ of the room centroid (1-d projection, 30-min steps, lag of one step) per unit, minus the field-only surrogate. Report Γ.
  - *Null:* `simulate.py` global/room/day-field presets on the real schedules.
  - *Prediction:* surrogate-corrected Ψ ≤ 0 in ≥ 80% of non-holdout units. Any exceptions are long, talk-coupled free periods (#38, #51) with Ψ − surrogate ≤ 0.05 bits.
  - *Impostor:* the scheduler field. $V$ must not be a share or a normalized quantity, or a common-mode term must be added to the surrogate.
- **Downward causation at the read-out hop.**
  - *Observable:* Δ with $V$ = the room centroid and targets = individual agents' next-window content. Compare windows where the agent read the room (`context_ledger_items`) with windows where it did not.
  - *Null:* the same Δ at in-flight (posted, unread) windows at matched lag.
  - *Prediction:* Δ ≤ 0 everywhere. "One read = one kick" (H59) is unique transfer, not whole → part.
  - *Impostor:* contemporaneous convergence.
- **Repo shares are decoupled from the agents (stigmergic macro-variable).**
  - *Observable:* Ψ and Γ for $V$ = the repo-share vector of agent work commits (DQ4, 30-min bins). Parts are agents, then agent + own artifact.
  - *Prediction:* Ψ > 0 for agents-as-parts in shared-repo weeks (#40, #44, #51), but ≤ 0 once each part includes its own artifact. That would mean the "emergent" persistence is held by artifacts (H58).
  - *Impostor:* the scheduler common mode. Shares cancel it, so the surrogate must keep it.
- **Emergence capacity rises in the absence of a strong kickoff.**
  - *Observable:* $\mathrm{Syn}^{(1)}$ by ΦID-MMI (Gaussian) on agent pairs.
  - *Prediction:* the median over pairs is higher in free or self-directed periods than in assigned-goal weeks, by ≥ 0.02 bits per step.
  - *Impostor:* shared model priors. Use same-family vs cross-family pairs.

## Caveats
- Granger, not Pearl: observational $p(X_{t'}|X_t)$ with hidden drivers (the operator, the platform) can show spurious unique information. NEs are the nearest thing to interventions.
- Results depend on the partition into parts (agents vs agents + artifacts vs embedding dimensions). Report the partition.
- Ψ scales with $n$: more parts mean more redundancy subtracted. Compare units of different $N$ only against size-matched surrogates, as points on the phase diagram, never pooled.
- Stationarity within the window is assumed. Kickoff transients violate it, so drop the first day or detrend with the exogenous field.
- Supervenience fails for anything not computed from the parts (e.g. operator text). Such a $V$ is not a valid feature.
- Mask the holdout. Never quote agent text when building $V$.
