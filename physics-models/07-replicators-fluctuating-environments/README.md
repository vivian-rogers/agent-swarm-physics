# 07 · Replicators in fluctuating environments (information bounds productivity)

**Fields:** info theory, dynamics, stat mech
**References:** Piñero et al., "Information bounds production in replicator systems", *Commun. Phys.* 9, 120 (2026) (in `literature/`); Kelly, "A new interpretation of information rate", *Bell Syst. Tech. J.* 35, 917 (1956)†.

## The model

Several replicator types compete in a flow reactor. The environment ε switches between active phases. In each environment one type grows fastest and wins (competitive exclusion). Between active phases the types partially re-equilibrate, which sets the starting proportions q_i for the next phase. Those starting proportions are the system's **bet** on which environment comes next, made without any sensor or controller.

Productivity P is the output flow of replicators averaged over a phase. Averaged over environments, it decomposes as

$$\langle P\rangle = \langle P^*\rangle - \gamma - \Omega\Big[\underbrace{H_\pi(R)}_{\text{uncertainty}} - \underbrace{I_\pi(R;Y)}_{\text{side information}} + \underbrace{D(\pi_{R|Y}\,\|\,q_{R|Y})}_{\text{mismatch}}\Big]$$

- R is which type wins, and Y is side information: a memory of the previous environment carried by the starting proportions.
- Ω acts like an effective temperature that converts nats into productivity.
- The optimal strategy is q = π_{R|Y}: bet in proportion to the probability of winning (Kelly betting), with a bias toward slow-growing winners because they need a head start.
- The value of memory is exactly bounded: P̄ − P̄₀ = Ω · I(R;Y).

## Interesting behavior

- **Kelly gambling without a gambler.** Passive relaxation between phases implements proportional betting. The inactive phase is placing the bet; the active phase is the race.
- **Memory has an optimal timescale.** If successive environments are correlated, an intermediate memory time is best: keep some of the last winner's head start, but not all of it. If environments are uncorrelated or anticorrelated, the best memory is none at all (full re-equilibration).
- **Information is worth a definite amount.** The gain from side information is Ω times the mutual information, a clean exchange rate between bits and output. In the paper's photochemical example the gain is only a few percent.

## Mapping to the village

- **Environment ε:** the current village goal type (`village_goals`), or task class.
- **Replicator types:** competing approaches, project types or model families. The winner is whichever is most productive under that goal.
- **Active and inactive phases:** village hours versus nights and weekends; or work stretches versus `CONSOLIDATE` events, when memory is rewritten.
- **Strategy q:** how effort is split across approaches at the start of a goal period (shares of the first session goals).
- **Side information Y:** what memory carries over from the previous goal period (`agent_memories`).
- **Productivity:** the hard part; there is no canonical output. Options include artifacts per active hour mined from `computer_use_turns` (commits, deploys, documents) or completed goals.

## How to measure

1. Classify goal periods by type; estimate the correlation between consecutive types.
2. Measure initial effort shares q at each goal start, and the eventual winning approach.
3. Estimate the mismatch D(π‖q) and the ramp-up shortfall. The model predicts that the shortfall scales with ln(1/q_winner).

## Pitfalls

- Only about 46 goal transitions, so I(R;Y) estimates have little statistical power. Use sub-periods or rooms as replicates.
- Agents rewrite memory deliberately; it is not passive relaxation.
- Productivity has no natural unit, so conclusions depend on the metric chosen.

## Hypothesis seeds

- Initial effort allocation carries information about the previous goal only when consecutive goals are correlated, and the swarm "over-remembers" when they are not.
- The ramp-up shortfall after a goal switch scales with ln(1/q), where q is the initial share of the approach that ends up winning.
- Consolidation frequency acts as the memory timescale; the 2026-03-24 change (consolidating every ~40 actions) shifted the swarm's effective bet.
