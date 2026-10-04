# A framework for the local information dynamics of distributed computation in complex systems

**Citation:** Joseph T. Lizier, Mikhail Prokopenko and Albert Y. Zomaya, arXiv:0811.2690 [nlin.CG] (v2, 2013; book chapter in *Guided Self-Organization: Inception*, Springer 2014). Stand-in for Lizier, *The Local Information Dynamics of Distributed Computation in Complex Systems* (Springer Theses, 2012/2013), which is not on arXiv.
**File:** lizier-2008-framework-local-information-dynamics.pdf
**Fields:** info theory, complex systems (distributed computation)

## Summary
The chapter reviews Lizier's framework, which splits distributed computation into three operations, each measured *locally* (at every space-time point) and *on average*:
- **information storage:** excess entropy and active information storage;
- **information transfer:** apparent, conditional and complete local transfer entropy;
- **information modification:** local separable information.

Applied to elementary cellular automata (rules 54, 110, 18, 22 and the φ_par density classifier), it gives the first quantitative support for three conjectures: blinkers and domains store, gliders and domain walls transfer, and collisions modify. Local values can be negative ("misinformative"). Collisions show up as points where separately inspected storage and transfer sources together mislead. Complex rules (110, 54) show *coherent* local structure. Chaotic rules (30) and rule 22 do not, although rule 22 shows structure in the joint (a, t) state space. The chapter says separable information is a heuristic that double-counts (Flecker et al. 2011) and points to PID for a proper measure of modification.

## Key formalism
- **History:** $x^{(k)}_n=(x_{n-k+1}..x_n)$. "Local" means the pointwise log-ratio; averages are expectations over all observations.
- **Excess entropy** (total storage): $E_X=\lim_k I(X^{(k)}_n;X^{(k^+)}_{n+1})$. Local: $e_X(n+1)=\log_2\frac{p(x^{(k)}_n,x^{(k^+)}_{n+1})}{p(x^{(k)}_n)p(x^{(k^+)}_{n+1})}$.
- **Active information storage** (storage in use now):
  - $A_X=\lim_k I(X^{(k)}_n;X_{n+1})$;
  - $a_X(n+1)=\log_2\frac{p(x_{n+1}|x^{(k)}_n)}{p(x_{n+1})}$.
  - The average is ≥ 0 and ≤ $\log_2 b$. Local values can exceed $\log_2 b$ or be negative.
- **Transfer entropy** (Schreiber):
  - $T_{Y\to X}(k,l)=\langle\log_2\frac{p(x_{n+1}|x^{(k)}_n,y^{(l)}_n)}{p(x_{n+1}|x^{(k)}_n)}\rangle$;
  - local: $t_{Y\to X}(n+1)$, the same log-ratio at one point.
  - Conditioning on the destination's past removes storage from transfer. The correct form is $k\to\infty$: a short $k$ lets self-memory beyond $k$ steps be counted as transfer, and misses synergies with older destination states. Use $l$ = 1 when $y_n$ is the direct cause. Match the source–destination delay to the causal delay.
- **Conditional TE:** $t_{Y\to X|Z}=\log_2\frac{p(x_{n+1}|x^{(k)}_n,y_n,z_n)}{p(x_{n+1}|x^{(k)}_n,z_n)}$.
  - **Complete TE** conditions on all other causal sources $V_X\setminus Y$. In deterministic systems it is ≥ 0 locally.
  - Apparent TE (no other conditioning) can be locally negative.
  - Neither is "more correct": complete TE catches transfer that is synergistic with $Z$, and apparent TE does not.
- **Information budget (one destination):**
  - $h_X(n+1)=a_X(n+1,k)+h_{\mu X}(n+1,k)$, with local entropy rate $h_\mu=-\log_2p(x_{n+1}|x^{(k)}_n)$.
  - In deterministic systems $h_\mu$ equals the **collective TE** from all sources.
  - For ECAs: $h(i,n+1)=a+t(j{=}-1)+t^c(j{=}1)$, a chain of incremental conditioning. It is *not* $a$ + the sum of apparent TEs.
- **Local separable information** (modification): $s_X(n)=a_X(n)+\sum_{Y\in V_X,Y\neq X}t_{Y\to X}(n)$.
  - $s>0$: trivial computation (sources separately informative).
  - $s<0$: non-trivial modification (sources mislead when inspected separately).
- **Numbers (rule 54, $k$ = 16, bits):**
  - Glider transfer: $p(x_{n+1}|\text{past},\text{source})$ = 1.00 vs 0.25 without the source, so $t$ = 2.02 bits.
  - Just before a collision: $a$ = −1.09, $t_{\pm1}$ = 2.02 each, $s$ = +2.95 (still separable).
  - At the modification point (one step after apparent contact): $a$ = −3.00, $t$ = 0.91 and 0.90, so $s$ = −1.19.
  - Weaker $s<0$ points recur every second step along travelling gliders ("virtual collisions"). In rule 110, modification is delayed further after complex collisions. Absorption by a blinker shows no modification.
- **Estimation:**
  - PDFs are pooled over every space-time point of homogeneous cells: 10,000 cells × 600 transient steps ($6\times10^6$ samples; φ_par: 30,000 × 200), periodic boundaries, JIDT.
  - $k$ must exceed the period of background domains. $k<4$ found no modification points, and $k<8$ missed some.
- **Coherence:** complex computation shows spatially and temporally coherent local profiles. Scatter plots of $(a,t)$ show structure for rules 110, 54 and 22, not for 30.

## Mapping to agent swarms
- **Destination $X$:** one agent's next allocation (DQ4 repo, ≤ 7 symbols incl. ∅) or next `behavior_states_v3` state (sampled from `p_*`; 11 states).
- **Sources:**
  - own past (storage);
  - items read at the call (`context_ledger_items`), as transfer;
  - the field bundle (scheduler `call_windows.gap_kind`, kickoff `goal_fields`), as a conditioning source $Z$ (conditional TE).
- **Sizes and identifiability:**
  - Lizier had $6\times10^6$ pooled samples with $k$ = 16 binary ($2^{16}$ histories).
  - We have ~$10^3$–$10^4$ agent-steps per unit (behavior: ~2.9k labelled agent-windows per unit on average; allocation: tens to hundreds of active 30-min bins per agent). Plug-in estimates allow $k$ = 1 with ≤ 7 symbols.
  - A long $k$ is not available, so **replace $x^{(k)}$ with a constructed sufficient state.** Use the agent's own artifact $\ell_i$, carried across bins, nights and erasures, as in H58's M0, plus time since its last commit. Otherwise storage beyond one bin (re-reading one's artifact after an erasure; H44) is counted as transfer from whoever was correlated.
- **Pooling:**
  - The framework pools over homogeneous variables. Agents differ (style, cadence).
  - Pool within a unit only.
  - Include agent identity, or the agent's leave-period-out base rates (DQ5 prior), in the conditioning. Otherwise heterogeneous marginals produce spurious negative local AIS.
- **Local values:**
  - In stochastic systems a single negative local TE or $s$ is noise more often than modification.
  - Threshold local values against source-shuffled surrogates (within-agent, within-day) and call an event only when the surrogate exceedance has $p<0.01$.
- **Shared-field corrections:**
  - **Scheduler:** steps exist only in active windows (DQ8 trims). First-of-day calls re-read their artifacts, which inflates storage at day starts; flag them.
  - **Kickoff:** condition TE on $Z$ = kickoff projection. A source that tracks the field better than the destination gets positive apparent TE without any reading.
  - **Priors:** conditioning on agent identity or prior removes family style.
  - **Contemporaneous convergence:** compute TE from posted-but-unread (in-flight) items at the same lag as a placebo source. Real transfer is TE(read) − TE(in-flight).

## Candidate hypotheses
- **HH299 sharpened: storage dominates, transfer is gated.**
  - *Observable:* per unit, $A$ (own artifact state → next allocation), $T_{\text{read}\to X|Z}$ and $T_{\text{in-flight}\to X|Z}$, in bits per active 30-min bin.
  - *Prediction:* $A/H(X')\ge0.3$ in ≥ 2/3 of units with ≥ 40 bins. $T_{\text{read}}-T_{\text{in-flight}}\le0.02$ bits outside shared-repo weeks.
  - *Impostor:* the kickoff field ($Z$ included).
- **Modification events cluster at merges, with a lag.**
  - *Observable:* local $s<0$ events (surrogate-thresholded) for allocation and for H34 marker adoption around NE42 (merge/split), #26 election rounds, and opposing-stance DQ2 `reply_pairs`.
  - *Prediction:* the $s<0$ rate is ≥ 2× the unit baseline in the 1–3 calls *after* the event (rule-54-like delay), not at the event.
  - *Null:* DQ8 `simulate.py` copy-only dynamics (Potts herding, DeGroot) on the real schedules.
  - *Impostor:* contemporaneous convergence (in-flight source placebo).
- **Erasure is a storage scramble.**
  - *Observable:* local $a$ at the first post-reset bin (`context_ledger_turns.reset_forced`, NE41) vs placebo bins, with the own-artifact state vs a memory-only state.
  - *Prediction:* local $a$ stays high with the artifact state and drops below 0 with memory only. Storage is held by the artifact (H15, H44).
  - *Impostor:* the scheduler (forced resets fall in busy stretches). Use time-of-day-matched placebos.
- **Coherence separates rooms from agents.**
  - *Observable:* $(a,t)$ scatter structure (mutual information between local $a$ and local $t$ across points) per unit.
  - *Prediction:* MI(a; t) is higher within read cones than across rooms. The village is "ordered" (storage-dominated), not "complex" (coherent transfer structures).

## Caveats
- Separable information is a heuristic. Prefer PID-based modification (synergy between own state and read source; Williams–Beer notes, BROJA/$I_{ccs}$) and use $s$ only to locate candidate events.
- TE is not causation (Lizier & Prokopenko 2010†). Observational TE with hidden drivers (operator, platform) can be positive with no channel.
- Finite $k$ underestimates storage and overestimates transfer. Report the history construction.
- Behavior windows (5 min) are coarser than calls, and 21% of ledger items are `uncertain`. Measure sources at `t_call`.
- Fit within units, never pooled. Mask the holdout.
