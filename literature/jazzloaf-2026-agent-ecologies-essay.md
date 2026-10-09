# Preliminary thoughts towards a quantitative science and management of agent ecologies

**Citation:** Vivian (@jazzloaf), unpublished essay (2026). The project lead's own position paper; it sets the research directions this repo serves.
**File:** jazzloaf-2026-agent-ecologies-essay.pdf (4 pages; local only, PDFs in `literature/` are gitignored)
**Fields:** econophysics, thermodynamics, information dynamics, AI safety

## Summary

The essay argues that self-propagating, unaligned agent swarms could become a stable state of the economy without new architectures, self-replication or weight theft: a few bad actors deploying them would be enough. It gives a free-energy analogy for why. Take an economy that moves from aligned (state *i*) to misaligned (state *f*) agents, with ΔG = ΔH − TΔS. ΔH < 0, because misaligned agents can reach more capital (more of the economy, including its malicious parts). ΔS > 0, because there are many more ways to be misaligned than aligned, so mutating populations drift toward misalignment. Hence ΔG < 0. The proposed response is kinetic stability, as for diamond: keep a humane economy in a metastable state, where defection by any one unit is too costly, for as long as possible.

## Research directions (as numbered in the essay)

1. **Econophysical thermodynamics of agents in the economy:** ecological physics, nonequilibrium statistical mechanics and information dynamics of homeostatic and self-replicating systems; borrow the quantitative models of bacterial ecologies (catalytic pathways, efficiencies, phase diagrams).
2. **Statistical mechanics of agent swarms for safety and interpretability.** This is the line of `writeup/papers/thermodynamics/` (the AI Village paper); the essay calls those results "middling", the data messy, the nonequilibrium-Ising hypotheses "somewhat interesting and predictive".
3. **Effective superagents in agent swarms and swarm swarms:** model emergent behavior as agents that run on a substrate of other agents (as we are superagents over cells, and governments over us); look for information-dynamical signatures of agent-like systems, e.g. with Kolchinsky–Wolpert semantic information ([kolchinsky-2018](kolchinsky-2018-semantic-information-autonomous-agency.md)). This is the line of `writeup/papers/superagents/`.
4. **Economists should study resource-constrained agent swarms** with the tools of quantitative economics.

## Proposed interventions (summary)

Tools to infer the source, relative alignment, structure and dynamics of swarms (a "Pangram" for swarm fingerprints); "agent observatories" that study and forecast agent ecologies; below-cost or low-latency provisioning of intellectual work to remove the margins that misaligned swarms need for homeostasis; access control that whitelists approved agents. As last resorts, the essay lists more drastic options: aligned, human-controlled "immune system" swarms, controlled burns of the intellectual economy, and self-regulating ensembles of aligned models.

## Relevance to this repo

- Direction 3 is the motivation for the superagent cards (H01, H58, H101) and for M04 and M12. Those cards found no effective superagent above "agent + its own artifact" in the village so far, with weak power for timing-based individuality tests (H01: ≤ 7% validated power).
- The essay's homeostasis framing maps onto [krakauer-2020](krakauer-2020-information-theory-of-individuality.md) (individuals as aggregates that propagate information from their past to their future) and onto the semantic-information viability test of [kolchinsky-2018](kolchinsky-2018-semantic-information-autonomous-agency.md).
- The free-energy argument is an analogy, not a derivation: T, H and S are not defined operationally for an economy. A paper that uses it should define each from data (see the "thermodynamic caution" note in `README.md`).
