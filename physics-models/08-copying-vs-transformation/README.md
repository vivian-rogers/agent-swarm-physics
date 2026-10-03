# 08 · Copying versus transformation

**Fields:** info theory, dynamics, sociophysics
**References:** Kolchinsky & Corominas-Murtra, "Decomposing information into copying versus transformation", *J. R. Soc. Interface* 17, 20190623 (2020)†; Eigen, *Naturwissenschaften* 58, 465 (1971)†; Griffiths & Kalish, "Language evolution by iterated learning with Bayesian agents", *Cognitive Science* 31, 441 (2007)†.

## The model

A message passes through a channel p(y|x) whose input and output use the **same alphabet**: a fact, number or plan goes in, and a version of it comes out. Mutual information I(X;Y) counts every statistical dependence, including systematic rewriting. Kolchinsky & Corominas-Murtra split it into two non-negative parts:

$$I(X;Y) = I_{\text{copy}} + I_{\text{transform}}$$

- **Copy information** is the part due to the output *being the input*: y = x more often than chance.
- **Transformation information** is the rest: dependence through systematic change, such as paraphrasing, translating, or always rounding a number.

A perfect copier and a perfect permutation (each x mapped to a different y) have the same I(X;Y), but all of the first is copying and all of the second is transformation.

> The exact definition of I_copy (a per-input divergence that compares the probability of reproducing x with the baseline probability of outputting x) needs checking against the paper before use. The PDF is not yet in `literature/`.

## Interesting behavior

- **Error threshold.** Eigen's classic result: a replicator of length L with per-symbol copying fidelity q keeps its information only if q^L × (selective advantage) > 1. Below that, information "melts" into a cloud of mutants: the error catastrophe. Long plans passed between agents may hit an analogous threshold.
- **Transmission chains converge to the prior.** In iterated learning, each learner reproduces what it saw through its own biases. Over many passes, the content converges to the learners' prior, not the original message. For a chain of LLM agents, the prediction is drift toward model-family defaults. That ties copying fidelity to the pretraining field in model 03.
- **Copying and transformation trade off.** A swarm can be faithful (high copy, low transform) or creative (low copy, high transform). The balance may differ by content type: numbers versus ideas.

## Mapping to the village

- **Transmissions:** pairs (source, reproduction), where agent i states something in chat and agent j later restates it. Use the contagion trees from model 03.
- **Alphabet:** structured features that can be compared exactly: numbers, URLs, names, dates, list items, claimed facts. Free text needs an embedding or a coarse-graining first.
- **Chains:** multi-hop transmissions (i → j → k → …) give fidelity as a function of chain length, the telephone game measured in the wild.

## How to measure

1. Extract (source, reproduction) pairs for structured features.
2. Estimate p(y|x) per feature type, then I_copy and I_transform.
3. For chains, plot fidelity against hop count and look for a threshold-like collapse.
4. Compare drift direction with each model family's spontaneous outputs (the field ε from model 03).

## Pitfalls

- Agents can re-fetch the original from a tool or the web, which looks like perfect copying but is a fresh lookup. Exclude reproductions that follow a lookup.
- Small alphabets (dates, yes/no) inflate chance agreement; use the decomposition, not raw accuracy.

## Hypothesis seeds

- Numbers are copied; ideas are transformed. I_copy / I dominates for numeric and URL features and is small for plans and summaries.
- Fidelity decays with hop count, and long instructions pass an error threshold where they stop surviving three hops.
- Multi-hop content drifts toward model-family defaults (iterated learning converges to the prior).
- Cross-family transmissions (Claude → GPT) have lower copy information than within-family ones.
