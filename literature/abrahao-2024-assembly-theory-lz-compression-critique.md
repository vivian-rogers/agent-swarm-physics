# Assembly theory is an approximation to algorithmic complexity based on LZ compression that does not explain selection or evolution

**Citation:** Felipe S. Abrahão, Santiago Hernández-Orozco, Narsis A. Kiani, Jesper Tegnér and Hector Zenil, arXiv:2403.06629 (v6, 2024-04-01). Preprint; critique of Sharma et al. 2023.
**File:** abrahao-2024-assembly-theory-lz-compression-critique.pdf
**Fields:** algorithmic information theory, complexity, info theory

## Summary
The authors argue that the assembly index is a compression scheme of the Lempel–Ziv family, and not a new physical quantity. The minimum rooted assembly space of an object is equivalent to a context-free grammar (CFG) that generates it, and the assembly index equals that grammar's size less the basis. The number of LZ factors is therefore bounded by the assembly index, and compression rates are bounded by Shannon entropy. Assembly index and assembly number are thus loose upper bounds on resource-bounded approximations to Kolmogorov complexity K. The paper also argues that:
- AT's selection argument is circular (assume selective joining, observe it differs from random joining, conclude selection);
- AT treats objects as built sequentially, which does not hold for parallel chemical or genetic processes;
- AT lacked controls against existing measures, which match or beat it on AT's own data.

## Key formalism
- Theorem 7 / Corollary 8 (Sup. Inf. A): for an object x built by a minimum rooted assembly space Γ*_x with basis B_Γ, there is a CFG G with
  - c_Γ(x) = |G*| − |B_Γ| (assembly index = non-basis rules of the minimal grammar);
  - LZ(x) ≤ c_Γ(x) + |B_Γ| (LZ factor count bounded by the assembly index plus a constant).
- Theorem 9: the assembling process is itself an LZ scheme. Its compressibility is set by the shortest pathway length and how far the space departs from a single linear thread.
- Consequence: low assembly index ⇔ high LZ compressibility ⇔ low entropy rate for i.i.d. or stationary ergodic sources. High index ⇔ low compressibility ⇔ high entropy. The direction of AT's "complexity" is the direction of entropy.
- "Template Program A": the program class AT implicitly uses, namely "print the repetitions N times, then print the rest". Any compressor that captures identical repeats (RLE, Huffman, LZ77/78/LZW) matches or beats it in the cited benchmarks (their ref. [4]). An organic/inorganic separation was earlier achieved on > 15,000 compounds with LZ and Block Decomposition Method (BDM) measures (their ref. [5]).
- Lemmas 1/3 and Corollaries 2/4: for any formal theory there are infinitely many objects or ensembles whose assembly index (or number) overestimates algorithmic complexity by an arbitrary margin. The index is a loose bound.
- Claimed contrast: statistical compression captures correlation. Algorithmic measures (CTM, BDM) with perturbation analysis can capture causal generative rules that LZ misses: objects with low LZ compressibility that a short non-repetitive rule generates.
- Counter-position, not read here: Cronin and co-authors argue the assembly index is NP-complete and differs quantitatively from LZW (arXiv:2406.12176, "Assembly theory and its relationship with computational complexity"). The dispute is open.

## Mapping to agent swarms
- **H80 baseline set.** For each command or commit sequence (`artifact_commands_text`, DQ4 `work_commits`), compute in increasing sophistication:
  1. per-token entropy rate;
  2. LZ76 complexity and LZ78/LZW factor counts;
  3. gzip/zstd ratio;
  4. smallest-grammar size (e.g. Re-Pair), which is the assembly index up to the basis by Corollary 8;
  5. optionally BDM.

  H80's question becomes whether the grammar term (≈ assembly index) adds AUC beyond the LZ factors and entropy. By Corollary 8 the expected answer is no: an added AUC < 0.02.
- **Timing baseline.** Inter-commit intervals alone, as the scheduler baseline H80 already names. Automated commits are periodic, so timing may beat every sequence measure.
- **The critique sharpens the shared-prior impostor.** Compressibility measures how repetitive the generator is. LLM agents share a strongly repetitive prior over shell idioms, so high compressibility and high copy number mostly reflect the model, not village selection. Compute compressibility *conditional on a reference corpus*: normalized compression distance to first-day motifs, or to motifs pooled from other periods (a shared instrument). This measures village-specific structure.
- **Other impostors.**
  - *Scheduler:* periodic automata produce the most compressible logs.
  - *Kickoff field:* templates pasted from goal text raise compressibility; remove kickoff and operator n-grams first.
  - *Contemporaneous convergence:* the same idiom produced independently; compression cannot tell it from copying. Use the context ledger for that.

## Candidate hypotheses
- **AT ≈ LZ in the village.** Across sequences, Spearman(assembly-index proxy, LZ78 factors) ≥ 0.9, and the AUC gain from the assembly proxy over {entropy, LZ, gzip} is < 0.02 in every period with ≥ 50 automated commits. *Kill:* gain ≥ 0.05 (H80's kill), which would favour AT's independence claim.
- **Village-specific compressibility exists.** Normalized compression distance from a period's motifs to the first-day reference falls over the period (structure accumulates). The fall is steeper in periods with long-lived shared repos (H11, H58). *Kill:* NCD flat, so all structure is prior.
- **Algorithmic beyond statistical.** BDM or CTM separates agent from automated commits where LZ fails. These would be short non-repetitive generated sequences, such as templated loops with incrementing counters. Exploratory only.

## Caveats
- The authors are a party to the dispute, and the tone is polemical; separate the proofs (Sup. Inf. A) from the rhetoric.
- The equivalence holds for strings and grammar-like assembly. For molecular graphs and mass-spectrometry estimates of the index, the correspondence is argued but less tight, and AT's authors contest it.
- Bounds of the form LZ(x) ≤ c(x) + |B| do not imply equal ranking on short sequences. Commands are short, so check the empirical correlation rather than assume it.
- Kolmogorov complexity is uncomputable. BDM/CTM are approximations with their own assumptions (small-machine enumeration), and are costly on long logs.
- Nothing here addresses copy number. The critique concerns a; whether n_i > 1 indicates selection remains a separate, testable claim.
