# The Markov blankets of life: autonomy, active inference and the free energy principle

**Citation:** Michael Kirchhoff, Thomas Parr, Ensor Palacios, Karl Friston and Julian Kiverstein, *J. R. Soc. Interface* 15(138), 20170792 (2018). DOI: 10.1098/rsif.2017.0792. Open access.
**File:** none. Notes from the open-access full text on PMC (PMC5805980) and the abstract, PDF not in repo (PMC, the publisher and UCL Discovery block scripted downloads).
**Fields:** theoretical biology, free energy principle, philosophy of biology

## Summary
The paper describes the boundaries of living systems, from cells to people, as Markov blankets under the free energy principle. A Markov blanket is a set of states that makes a system's internal states conditionally independent of the external states. The authors argue that a collective of Markov-blanketed systems can self-assemble into a larger system that has its own blanket, so living systems are "Markov blankets of Markov blankets", all the way down to organelles and all the way up to organisms. The blanket need not coincide with the skin: it can include parts of the environment (the air bubble of a water boatman). The paper also separates *mere* active inference (coupled systems that synchronize, like Huygens' pendulums) from *adaptive* active inference (systems with temporally deep generative models that can change their relation to the environment), and ties autonomy to the second.

## Key formalism
- **Partition.** States split into external ψ, sensory s, active a and internal r. Sensory states are influenced by external states and influence internal ones; active states are influenced by internal states and influence external ones. Given the blanket (s, a), internal and external states are conditionally independent.
- **Variational free energy.** F(s, a, r) = −ln p(s | m) + KL[q(ψ | r) ‖ p(ψ | s, a)] ≥ −ln p(s | m). Minimizing F over internal and active states bounds surprise, so the system stays in a small set of states (it persists).
- **Nesting.** Blankets at one scale are composed of blankets at the scale below; each level minimizes its own free energy. The paper argues for this; it says it has not shown that the nesting emerges, and points to separate simulations.
- **Autonomy.** Adaptive active inference requires prior beliefs about the consequences of one's own actions; mere coupling is not autonomy.

## Mapping to paper 2
- The blanket gives a conditional-independence test for a boundary: given the pattern's "sensory" inputs (what hosts read) and "active" outputs (what hosts post), is the rest of the village independent of the pattern's internal state? This is close to Krakauer's informational closure (nC = I(S′; E | S) → 0) and to Bertschinger's autonomy.
- "Blankets of blankets" is the nesting that our definition allows: an agent keeps its own boundary while it hosts a pattern that has a boundary at a larger scale (with Schwitzgebel's argument against anti-nesting).
- The extended blanket (boatman's bubble) supports counting shared files and repositories as part of a pattern, as our memeplex elements do.
- Mere vs adaptive inference matches our split between an attractor (patterns that just synchronize hosts) and an egregore with functional behaviors (recruitment, repair).

## Caveats
- Markov blankets of a real system are rarely exact; with finite logs any blanket is approximate and depends on the coarse-graining. There is an active debate on whether blankets are properties of the system or of the model (Bruineberg et al. 2022, not in repo).
- The free energy principle is a framework, not a testable hypothesis on its own. We use the blanket as a boundary criterion, not the principle.
- In the village, every agent in a room reads every message, so the read graph is dense and approximate blankets will be weak at the room scale.
