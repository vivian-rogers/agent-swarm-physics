# Information bounds production in replicator systems

**Citation:** Jordi Piñero et al., *Communications Physics* 9, 120 (2026). DOI: 10.1038/s42005-026-02527-5
**File:** pinero-2026-information-bounds-replicator-production.pdf
**Fields:** info theory, dynamics, stat mech

## Summary
The paper asks how simple replicators can exploit information about a fluctuating environment without any sensor or controller. In a flow-reactor model, different environmental states favor different replicators (competitive exclusion picks one winner per state). Between active phases the replicators partially re-equilibrate through exchange reactions, which sets the initial proportions (the "strategy") for the next active phase. The authors derive an information-theoretic decomposition of productivity into environmental uncertainty, side information (an internal memory of the previous environment) and strategy mismatch, find the optimal strategy (a Kelly-like proportional bet with a bias toward slow replicators), and derive universal bounds. Applied to photocatalytic replicators under weak/strong light, the gain from memory is a few percent of productivity.

## Key formalism
- Reactor: $\dot x_i=\eta_i a x_i-\phi x_i$, $\dot a=\mu\phi-a\sum_i\eta_i x_i-\phi a$; total solute obeys $\dot S=\phi(\mu-S)$. Winner $r=\arg\max\eta_i$, $a^*=\phi/\eta_r$, $X^*=\mu-\phi/\eta_r$.
- Productivity $P=\tfrac1\tau\int_0^\tau\phi X\,dt$ (outflow of replicators). With $S(0)\approx S^*$ and steady state reached: $P=P^*+\dfrac{\phi}{\tau\eta_r}\big[\ln q_r+\ln\tfrac{X(0)}{X^*}\big]$, where $q_i=x_i(0)/X(0)$ is the "strategy".
- Fluctuating environment $\varepsilon$ with preparation (side information) $Y$: $\langle P\rangle=\langle P^*\rangle-\gamma-\Omega\,C_{\pi,q}(R|Y)$.
- Cross-entropy decomposition: $C_{\pi,q}(R|Y)=H_\pi(R)-I_\pi(R;Y)+D(\pi_{R|Y}\|q_{R|Y})$, the three terms being uncertainty, side-information benefit, and mismatch. $\Omega$ acts as an "effective temperature" converting nats to productivity.
- Optimal strategy $q=\pi_{R|Y}$, with $\pi_{r,y}\propto\sum_{\varepsilon:\,r(\varepsilon)=r}p_{\varepsilon,y}\,\phi_\varepsilon/\eta_{r(\varepsilon)}$; this is biased toward slower replicators and higher dilution (a "head start").
- Bounds: $\langle P\rangle\le\bar P=\langle P^*\rangle-\gamma-\Omega[H_\pi(R)-I_\pi(R;Y)]$, and $\bar P-\bar P_0=\Omega\,I_\pi(R;Y)$ (Eq. 35).
- Kelly analogy: inactive phase = betting, active phase = gambling. Application with memory timescale $\lambda=\kappa\tau_I$ and bias $b$: finite optimal $\lambda$ for correlated environments, $\lambda\to\infty$ for uncorrelated or anticorrelated ones.

## Mapping to agent swarms
- Replicators = competing approaches, model families, or projects. The environment state $\varepsilon$ = the current village goal type (`village_goals`, ~46 goals), the room, or a task class.
- Winner $r(\varepsilon)$ = the approach or model family that performs best under goal $\varepsilon$. Operationalizing "performs best" is the hard step. Possible outputs are artifacts per active hour mined from `computer_use_turns` (e.g., git/deploy commands in `agent_action`) or session completions.
- Active phases = village hours (10am-2pm PT, later 9am-5pm PT); inactive phases = nights, skipped weekends, and the gaps around `CONSOLIDATE` events, in which memory is rewritten.
- Strategy $q$: the distribution of effort across approaches at the start of a session or goal period, e.g., cluster shares of the first `session_goal`s after consolidation.
- Side information $Y$: the previous goal period's outcome, carried through `agent_memories`. Memory timescale $\lambda$ is set by consolidation frequency (about every 40 actions after 2026-03-24).
- Dilution $\phi$/flow: agent turnover or task throughput. A stretch with no clean field.

## Candidate hypotheses
- Initial effort allocation at the start of a goal period carries information about the prior period only if consecutive goal types are correlated. Observable: mutual information between consecutive goal types and between prior outcome and initial `session_goal` cluster shares; benefit bounded by $\Omega I(R;Y)$.
- Productivity shortfall at the start of an active phase scales with $\ln(1/q_r)$ and with slow winners, i.e., ramp-up deficits are larger when the winning approach starts rare. Observable: first-hour vs. steady-state output per approach after each goal switch.
- Within a goal period, approach diversity collapses (competitive exclusion) and re-expands at boundaries. Observable: Simpson index of approach shares within and across `village_goals` intervals.

## Caveats
- Deterministic, single-resource, first-order mass-action kinetics with exactly one winner per environment. LLM agents learn, imitate and coexist in multiple niches.
- Only ~45 goal transitions are available, so estimating $I(R;Y)$ has low power; use goal sub-periods or room-level replicates.
- "Productivity" has no canonical definition in the village; results depend on the chosen output metric.
- Memory in agents is explicit text that they can rewrite deliberately, not passive relaxation of concentrations.
- After 2026-03-24 (perma-computer-use) discrete sessions are rare; use `CONSOLIDATE` `nextSessionGoal` for the strategy labels.
- The paper itself notes information terms are only a few percent of productivity, so expect small effects against heavy confounding from scaffolding changes.
