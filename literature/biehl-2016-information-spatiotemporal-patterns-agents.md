# Towards information based spatiotemporal patterns as a foundation for agent representation in dynamical systems

**Citation:** Martin Biehl, Takashi Ikegami and Daniel Polani, *Proceedings of the Artificial Life Conference 2016* (ALIFE XV), MIT Press, pp. 722–729, doi:10.7551/978-0-262-33936-0-ch115. arXiv:1605.05676.
**File:** biehl-2016-information-spatiotemporal-patterns-agents.pdf (arXiv v1, 8 pp.)
**Fields:** artificial life, information theory, dynamical systems

## Summary
The paper asks how to represent agents inside a dynamical system so that the representation can follow living things. Three features of life break representations that fix a set of variables as "the agent": *metabolism* (the particles that make up a bacterium change), *motility* (a moving organism occupies different field cells over time) and *counterfactual variation* (in different histories the agent occupies different degrees of freedom, or does not exist). Krakauer et al.'s boundary algorithm handles the first two, but fails the third: it averages over all trajectories, so it fixes one agent–environment partition for every history. The authors propose instead to define entities as *integrated spatiotemporal patterns*: sets of variable–value pairs, spread over space and time, that occur together more often than any partition of them would predict. They test the idea on the Game of Life (gliders).

## Key formalism
- **Setting:** a dynamical Bayesian network with time slices V_t; a spatiotemporal pattern x_O is a set of nodes O with fixed values; it *occurs* in a trajectory if it is a subset of it.
- **Evidence for integration** of x_O under a partition π of O: the local (pointwise) multi-information
  mi_π(x_O) = log [ p_O(x_O) / Π_{b∈π} p_b(x_b) ].
- **Integrated pattern:** mi_π(x_O) > 0 for every partition π. In the thesis version (arXiv:1704.02716) this becomes *complete local integration* and the patterns are called ι-entities.
- **Intuition:** a rock or a glider at one time makes the "same" rock or glider at the next time likely; parts of an integrated pattern rarely occur without the rest.
- **Relation to other work:** localizes multi-information the way Lizier's framework localizes transfer entropy; related to IIT's partition-based integration, but over time as well as space.

## Mapping to paper 2
- This is the closest formal match to an egregore: an entity defined as a pattern of values that moves across the variables of a substrate, not as a fixed set of variables. An ideology moves across hosts as a glider moves across cells.
- It supports defining the memeplex by pointwise co-occurrence of elements across hosts and time, with integration tested against every split of its elements, not only against single elements.
- It names the flaw our design must handle: Krakauer's A is an average over trajectories with a fixed partition. We work around it by making the pattern's state (which elements are expressed village-wide) the system variable, so the hosts can change while the variable stays fixed.

## Caveats
- The paper is a position statement with preliminary Game-of-Life results; it gives no estimator for real data. Pointwise probabilities of high-dimensional patterns need a model of the full trajectory distribution, which we do not have.
- Integration alone does not make an agent; the paper says perception, action and goal-directedness must be added (Biehl's thesis defines entity action and perception).
