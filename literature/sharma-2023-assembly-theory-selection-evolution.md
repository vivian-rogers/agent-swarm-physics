# Assembly theory explains and quantifies selection and evolution

**Citation:** Abhishek Sharma, Dániel Czégel, Michael Lachmann, Christopher P. Kempes, Sara I. Walker and Leroy Cronin, *Nature* 622, 321–328 (2023). arXiv:2206.02279 (preprint title: "Assembly Theory Explains and Quantifies the Emergence of Selection and Evolution").
**File:** sharma-2023-assembly-theory-selection-evolution.pdf
**Fields:** origins of life, complexity, info theory

## Summary
Assembly theory (AT) defines an object by the set of histories that could have built it. Its **assembly index** a is the length of the shortest recursive construction pathway from elementary blocks, where anything already built may be reused. The claim is that a complex object (high a) found in many copies (high n) is evidence of selection: without a selected mechanism with memory, the chance of finding two identical high-a objects falls super-exponentially with a. The **Assembly** A of an ensemble combines a and n into one number for "how much selection was needed". A forward model with a selectivity exponent α and two timescales (discovery and production) shows that high-A ensembles need restricted selectivity (α < 1) and comparable timescales. Note: this is the preprint, read in place of the Nature text; figures and wording may differ.

## Key formalism
- Assembly equation: A = Σ_{i=1}^{N} e^{a_i} (n_i − 1)/N_T, with N unique objects (copy number n_i > 1) and N_T total objects. A single copy contributes nothing.
- Discovery dynamics: P_a ∝ N_a^α, dN_{a+1}/dt = k_d N_a^α. α = 1 is history without selection (boundary of "Assembly Possible"); 0 ≤ α < 1 is "Assembly Contingent" (selection). The signature of selection is growth of unique objects slower than exponential.
- Production: k_p(a) = k_f β^a, so making objects gets slower with a.
- Regimes:
  - k_d/k_p ≫ 1: many unique objects with low copy number ("tar", formose).
  - k_d/k_p ≪ 1: many copies of low-a objects.
  - Only τ_d ≈ τ_p gives high-A ensembles. Emergence of selection = a crossover from k_p < k_d to k_d < k_p.
- Sweep α = 0.01, 0.2, 0.5, 0.8, 1.0 up to dimensionless time 10^9 and a ≤ 25. A falls over time for α ≈ 1, stays high for intermediate α, and is low for α ≈ 0 (few objects, low a). So A is non-monotone in selectivity.
- Polymer toy (10^4 steps, 25 runs): directed construction (newest polymer always reused) gives a lower **exploration ratio** (observed nodes / nodes in the joint assembly space) and a higher mean maximum a (≈ log₂ length) than random combination.
- Detection threshold: an object counts only above a copy threshold (10 in the simulation; ~10^4 molecules for mass spectrometry).
- AT claims (contested; see `abrahao-2024-assembly-theory-lz-compression-critique.md`) that a is not an algorithmic-complexity measure, because it counts only physically allowed joining operations.

## Mapping to agent swarms
- **Objects = command or code motifs.** Use token sequences from `artifact_commands_text` (shell commands, tool-call sequences) and recurring file/commit structures in DQ4 `work_commits`. **Blocks** = tokens or tool primitives; **joins** = concatenation with reuse. a = smallest-grammar size (strings make a computable through grammar compression; see the critique).
- **Copy number** = occurrences across agents and sessions within one goal period. **A per period** gives a selection index to place periods on a phase diagram (unit of analysis: one goal period).
- **Selectivity α:** regress the rate of first appearance of motifs at index a + 1 on the count at a, per period. **Timescales:** τ_d = time to first appearance, τ_p = time from first appearance to the copy threshold.
- **H80 test:** AT's signature (high a × high n) vs compression baselines for separating automated from agent commits. H79: executed artifacts with high a and high n are candidate catalysts.
- **Impostors.**
  - *Shared model priors* (the main one): LLMs emit identical long motifs (common shell idioms, boilerplate) with no in-village selection. High a × high n on an agent's first day, across families, is prior, not selection (H80 predicts ≥ 70%).
  - *Scheduler:* cron jobs and HH244 automata replay one script, giving exact copies of a high-a object. That is one selected mechanism, so count copies per independent producer.
  - *Kickoff field:* kickoff-named templates seed copies; exclude motifs present in kickoff or operator text.
  - *Contemporaneous convergence:* identical motifs in isolated forks (H07). Require a logged read before the copy for "transmitted".

## Candidate hypotheses
- **Selection index by period.** A (copies counted per independent agent, first-day motifs removed) is higher in build-heavy periods than in chat/debate periods, and α < 0.8 only where repos persist ≥ 1 week. *Kill:* A ranks periods the same as plain motif counts or gzip ratio (Spearman ≥ 0.9). Then AT adds nothing at the period level.
- **Prior-dominated assembly.** ≥ 70% of motifs with a ≥ 10 and n ≥ 5 appear on an agent's first active day and in ≥ 2 families (H80's prediction).
- **Exploration ratio drops at settling.** After kickoff, the motif exploration ratio falls as the period settles, on the H48 settling timescale; this links to Mathis-type kickoff decoupling.

## Caveats
- A is ensemble-normalized and exponential in a. One very long boilerplate block dominates A, so report the distribution, not only A.
- a is NP-hard in general. For token strings use a grammar-compression upper bound, and say so.
- Copy number needs an identity notion (exact text, normalized whitespace or variables). That choice sets A.
- "Selection" in AT includes any biased generator: an operator's template, a model prior or a cron job all count. AT cannot by itself say whose selection it is; the impostor controls carry the inference.
- The selection claim is under active dispute (circularity and compression equivalence; see the critique). Use AT as one feature against compression baselines, not as a selection meter.
