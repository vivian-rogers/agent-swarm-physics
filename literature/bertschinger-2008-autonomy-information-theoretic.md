# Autonomy: an information theoretic perspective

**Citation:** Nils Bertschinger, Eckehard Olbrich, Nihat Ay and Jürgen Jost, *BioSystems* 91(2), 331–345 (2008). DOI: 10.1016/j.biosystems.2007.05.018. PMID 17897774.
**File:** none. Notes from abstract/secondary sources, PDF not in repo (no open-access copy found; abstract from Europe PMC; definitions as reported by Krakauer et al. 2020 and Biehl's 2017 thesis, arXiv:1704.02716).
**Fields:** information theory, artificial life, complex systems

## Summary
The paper proposes a quantitative measure of autonomy, starting from a given split into system S and environment E. The first measure is the conditional mutual information between consecutive system states given the history of the environment: how much the system's present tells about its next state beyond what the environment's past already tells. This works when the system cannot influence the environment and the two do not interact synergistically. When the system fully controls its environment, the environment's history should be ignored, and the plain mutual information between consecutive system states is the right measure. With mutual interaction it is ambiguous whether system or environment caused the observed correlations; if the interaction structure is known, a "causal" autonomy measure resolves this. Synergistic interaction still blocks attribution. The measures are evaluated on simple automata, an agent moving in space, gliders in the Game of Life, and Varela's tessellation automaton for autopoiesis.

## Key formalism
- **Autonomy (environment-conditioned):** A_m = I(S_{n+1}; S_n | E_{n−m..n}), the information the system's state carries about its next state given m steps of environment history. This is the direct precursor of Krakauer et al.'s colonial individuality A = I(S_{n+1}; S_n | E_n).
- **Self-determination when the system controls E:** I(S_{n+1}; S_n), the precursor of Krakauer's organismal A*.
- **Non-heteronomy:** H(S_{n+1} | E-history) > 0, the system is not determined by the environment's history (term as used by Biehl 2017).
- **Informational closure** (Bertschinger et al. 2006): I(S_{n+1}; E_n | S_n) = 0, the system can be described without reference to its environment. Closure and autonomy are different: a closed system need not be autonomous.
- **Memory.** Autonomy requires that the system's own state carry information forward, so it is tied to the system's memory.

## Mapping to paper 2
- This is the measurement our condition (1) uses, in Krakauer's later form. The paper's caveats are ours:
  - *Who controls E?* Hosts write the chat that is part of a pattern's environment. If a pattern drives the chat, conditioning on chat removes the pattern's own effect. So E must hold only the exogenous fields (scheduler, operator and human messages, role texts), strictly lagged, as our E bundle does.
  - *Synergy.* A pattern that is jointly carried by hosts and by the operator's field (an operator-raised topic that agents elaborate) cannot be attributed to either. Report it as unresolved, not as an egregore.
- Their test cases (gliders, autopoietic automata) are moving, self-maintaining patterns on a substrate, the same kind of object as an ideology on agents.

## Caveats
- The measure presumes a fixed system–environment split. A pattern whose elements change over time (cultural drift) violates this; Biehl et al. 2016 address it with spatiotemporal patterns.
- Estimation with long environment histories needs data the village does not have per period; use held-out log-loss estimators, as in H58.
