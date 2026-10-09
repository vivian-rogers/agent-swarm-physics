# When LLMs play the telephone game: cultural attractors as conceptual tools to evaluate LLMs in multi-turn settings

**Citation:** Jérémy Perez, Grgur Kovač, Corentin Léger, Cédric Colas, Gaia Molinaro, Maxime Derex, Pierre-Yves Oudeyer and Clément Moulin-Frier, *ICLR 2025* (International Conference on Learning Representations). arXiv:2407.04503 (first titled "When LLMs play the telephone game: cumulative changes and attractors in iterated cultural transmissions").
**File:** perez-2025-llm-telephone-game-cultural-attractors.pdf (arXiv v4, 40 pp. with appendices)
**Fields:** cultural evolution, LLM evaluation, complex systems

## Summary
The paper applies the transmission-chain design of human cultural-evolution experiments to LLMs. The first agent in a chain receives a human-written text and a task ("rephrase", "take inspiration from", "continue"); each later agent receives the previous agent's output and the same task; chains run for 50 steps. The authors track four text properties (toxicity, positivity, difficulty, length) and ask whether small single-turn biases accumulate into attractors, in the sense of Sperber's cultural attraction theory. They do: multi-turn distributions differ from single-turn ones (Kolmogorov–Smirnov tests), and every condition has an attractor. Less constrained tasks give stronger attraction; toxicity has stronger attractors than length; models differ in attractor position and strength; fine-tuning shifts attractor position.

## Key formalism
- **Chain:** text_{i+1} = LLM(task, text_i), i = 0..49; 6 models (GPT-4o-mini, GPT-3.5-turbo, Llama3-8B and 70B, Mistral-7B, Mixtral-8x7B), 3 tasks, 20 initial texts, 5 seeds per condition.
- **Attractor position and strength.** Fit property(gen 50) = I + s · property(gen 0) across chains. Iterating the fitted map gives a linear recurrence with fixed point l = I / (1 − s) if |s| < 1; *strength* = 1 − s ∈ [0, 1] (0 = no attraction, 1 = every chain lands on l in one block). Positions predicted from the first 10 generations match the observed 50th generation.
- **Effects:** task Continue > Take inspiration > Rephrase in strength; toxicity strongest; Llama3-70B and GPT-4o-mini weaker attractors than GPT-3.5, Llama3-8B, Mixtral; positivity bimodal for Llama3 models; length drifts down for GPT-3.5 and Llama3-8B, up for Mixtral and GPT-4o-mini. Higher temperature strengthens attractors in constrained tasks only.
- **Contrast with iterated Bayesian learning:** attraction is a fixed point of a recurrence, not convergence to a prior; this avoids assuming that LLMs have priors.

## Mapping to paper 2
- It gives a clean null for our recruitment test: a property that drifts toward a model-specific attractor in isolated chains is a constructive bias, not an ideology. A village pattern whose prevalence among unread agents rises to the same level is an attractor; an egregore must need exposure.
- Model dependence of attractors is our "shared model prior" impostor. The village mixes labs, so a pattern that is an attractor for one family only will show up as a family effect; our E bundle requires spread across labs.
- Their strength 1 − s is a convenient summary we can compute for statement clusters across context-erasure "generations" of one agent (what survives the agent's own rewrite of its notes).

## Caveats
- Linear chains with one designed task differ from the village's broadcast rooms, where each agent reads many sources and also writes its own memory. In-context transmission among many senders is closer to the Centola–Baronchelli and Ashery designs.
- Text properties are measured by off-the-shelf classifiers (toxicity, VADER sentiment, Gunning-Fog), which are themselves biased.
