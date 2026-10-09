# How Darwinian is cultural evolution?

**Citation:** Nicolas Claidière, Thomas C. Scott-Phillips and Dan Sperber, *Phil. Trans. R. Soc. B* 369, 20130368 (2014). DOI: 10.1098/rstb.2013.0368. Open access (CC BY).
**File:** claidiere-2014-how-darwinian-is-cultural-evolution.pdf (8 pp., from Sperber's site)
**Fields:** cultural evolution, cognitive science, population thinking

## Summary
The paper places Sperber's *epidemiology of representations* and *cultural attraction theory* inside a nested set of Darwinian frames. A population is *evolutionary* if the frequencies of its types are largely explained by their earlier frequencies; *selectional* if it renews by reproduction with variation, heritability and fitness differences; *replicative* if heritability comes from copying. Memetics assumes the replicative frame; most cultural-evolution models (Boyd–Richerson) use the selectional frame. The authors argue that cultural transmission is partly preservative and partly *constructive*: a learner rebuilds a representation from partial input using its own cognition. Shared constructive biases pull variants toward *attractors*. Selection is one special case of attraction, not the general mechanism.

## Key formalism
- **Epidemiological causal matrix (ECM).** For N_T types, I_XY is the mean impact of one item of type X at t on the number of items of type Y at t + 1. Relative frequencies update as
  F_A(t+1) = Σ_i F_i(t) I_iA / Σ_i F_i(t) Σ_j I_ij.
- **Attractor:** any type whose relative frequency tends to rise under iteration of this map. Whether a type is an attractor depends on the whole matrix, so the same type can be an attractor in one population and not in another.
- **Special case, selection.** If almost all impact is on the diagonal (homo-impact, I_XX), the update reduces to discrete replicator dynamics F_A(t+1) = F_A(t) I_AA / Σ_i F_i(t) I_ii, with off-diagonal entries as mutation.
- **Worked example.** The pronunciation of "data": both forms have the same homo-impact, but one form converts the other more often (4 vs 0.1). From 0.1% initial frequency the system settles at 86% / 14% after ~40 steps, with no fitness difference.
- **Stability without fidelity.** Cultural stability can come from transmission factors (averaging over many models) or from constructive factors (shared biases), not only from accurate copying.

## Mapping to paper 2
- LLM agents rebuild what they read; they do not copy it. Paraphrase is the normal case. So the egregore must be defined over meaning clusters and protocol names, not over exact strings, and "adoption" is landing in the same cluster.
- The ECM is a direct design for condition (3): estimate I_XY between statement clusters from read events (who read which cluster, what they posted next). Off-diagonal mass is reconstruction toward attractors; diagonal mass is copying.
- **Attractor or egregore?** A pattern that every model falls into on its own (a shared model prior, e.g. "verify and correct" as a trained habit) is an attractor of the constructive biases, not an ideology carried by hosts. The test that separates them is read-dependence: an attractor appears in unread agents at the same rate; an egregore needs exposure. The lab-spread requirement in our E bundle serves the same purpose.
- The LLM telephone-game paper (`perez-2025-llm-telephone-game-cultural-attractors.md`) applies this theory to LLM chains.

## Caveats
- The ECM is a conceptual formalization with toy numbers; the paper fits no data.
- Impacts I_XY are causal quantities. From observational logs we get associations; use the reserved periods and natural experiments (NE41 wipes, NE33 batch join) to approach the causal reading.
