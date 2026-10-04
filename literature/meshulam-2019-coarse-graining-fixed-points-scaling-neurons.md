# Coarse-graining, fixed points, and scaling in a large population of neurons

**Citation:** Leenoy Meshulam, Jeffrey L. Gauthier, Carlos D. Brody, David W. Tank and William Bialek, *Phys. Rev. Lett.* 123, 178103 (2019). arXiv:1809.08461 (PDF is arXiv v1, the only arXiv version).
**File:** meshulam-2019-coarse-graining-fixed-points-scaling-neurons.pdf
**Fields:** stat mech (renormalization group), biophysics

**Version note.** The local PDF (v1) reports β̃, μ and z̃ but **not** the variance exponent α̃. α̃ ≈ 1.4 and the three-mouse table come from the long companion paper: Meshulam et al., arXiv:1812.11904, "Coarse-graining and hints of scaling in a population of 1000+ neurons". I read it once for these notes and did not add it to `literature/`. I did not check whether the published PRL text matches v1 or the long paper. Values marked [L] are from the long paper. Cite the PRL for the method; cite arXiv:1812.11904 for α̃ and the field-only null.

## Summary
A phenomenological real-space RG for data without a lattice. Correlation stands in for spatial proximity. The procedure:
1. Merge the most correlated pair, then the next most correlated pair among the remaining variables, greedily, until all are paired.
2. Sum each pair and renormalize.
3. Repeat, giving clusters of size $K=2^k$.

The data are ~1,485 CA1 neurons (2-photon calcium, 30 Hz) in a mouse running a virtual track. Under coarse-graining:
- the distribution of cluster activity approaches a fixed, **non-Gaussian** (exponential-tailed) form;
- the variance, the probability of silence, the within-cluster covariance spectrum and the correlation time all scale as power laws across about two decades.

The exponents reproduce across three mice. An independent place-cell model, with neurons independent given the animal's position, does not scale. The authors read this as a non-trivial RG fixed point.

## Key formalism
- **Normalization:** each variable is scaled so the mean of its *nonzero* values is 1. This keeps true zeros (silence). It is restored after every merge.
- **Merge step:** $x^{(k+1)}_i=Z_i\,(x^{(k)}_i+x^{(k)}_{j^*(i)})$, where $j^*$ is the most correlated unpaired partner of $c_{ij}=\langle\delta x_i\delta x_j\rangle/\sqrt{\cdot}$.
- **Distribution:** $P_K(x)=P_0(K)\delta(x)+[1-P_0(K)]Q_K(x)$, with $\int Q_K x\,dx=1$. $Q_K$ barely changes from $K$ = 1 to 256 and is not driven toward a Gaussian.
- **Variance [L]:** $M_2(K)\propto K^{\tilde\alpha}$.
  - Independent variables: α̃ = 1. Perfectly correlated: α̃ = 2.
  - Mouse 1: α̃ = 1.4 ± 0.06. Three mice: 1.40, 1.56, 1.73, i.e. 1.56 ± 0.07 ± 0.16. The least reproducible exponent; the spread is twice the error bars.
- **Silence ("free energy"):** $F(K)=-\ln P_0(K)=aK^{\tilde\beta}$.
  - Independent variables: β̃ = 1 (extensive).
  - v1: β̃ = 0.87 ± 0.03. [L]: 0.88 ± 0.01, with the three mice at 0.88, 0.89, 0.86. The most precise exponent; the meaningful quantity is $1-\tilde\beta$ (±10%).
  - Fits from $K\ge32$ give the same β̃.
- **Spectrum inside clusters:** a fixed point with propagator $G(k)=A/k^{2-\eta}$ gives $\lambda=B\,(K/\text{rank})^{\mu}$, with $\mu=(2-\eta)/d$. The spectrum collapses as a function of rank/$K$.
  - μ = 0.71 ± 0.15 (v1). [L]: 0.71 ± 0.06; pooled over mice 0.76 ± 0.05 ± 0.06.
  - Spectra only for $K\le128$, where samples exceed dimensions by more than 10×.
- **Dynamic scaling:** $C_K(t)$ collapses under $t\to t/\tau_c(K)$, with $\tau_c=\tau_1K^{\tilde z}$.
  - z̃ = 0.11 ± 0.01 (v1). [L]: 0.16 ± 0.02, pooled 0.22 ± 0.08 ± 0.10.
  - "Momentum-space" version [L]: $\tau_c\propto\lambda^{-z'}$ with z′ = 0.37 ± 0.04, and z′/z̃ is within error of μ.
- **Momentum-space RG [L]:** inside a cluster (or the whole population), project activity onto the top $\hat K$ eigenmodes of the covariance (keep $N/16$ down to $N/128$). The distribution of the projected variable stays fixed and non-Gaussian.
- **Errors:** standard deviation across random *connected quarters* of the recording, which respects temporal correlation. Log–log slopes are fitted per quarter.
- **Effective samples [L]:** time-shifted surrogates give a correlation noise floor δC = 0.03, i.e. only a few thousand independent samples. Merging on the strongest correlations is meant to be robust to that noise.
- **Field-only null (independent place cells) [L]:**
  - Each cell fires with $p_i(x(t))$ along the real trajectory. Cells are correlated only through the shared variable $x(t)$.
  - The variance wanders around the best power law with **α̃ = 1.78 ± 0.03**.
  - $P_0$ does not follow $K^{\tilde\beta}$.
  - $\tau_c$ does not scale with eigenvalue.
  - The shared field has a characteristic size $K_c\approx18$ (place-field width / spacing), where the curves kink.
  - A real fixed point shows no such scale.
  - Binarized data give the same exponents within errors.

## Mapping to agent swarms
- **Variables:** usage time series of hashed H34 markers per unit (counts per 15- or 30-min bin, or per call). Thousands of terms exist, so $K$ can reach 2⁸–2¹⁰. Agents (4–32) are too few: at most five merge steps, no scaling range.
- **Time samples:**
  - A unit lasts about 4 days (283 days / 71 units), i.e. $T\approx200$–400 fifteen-minute bins.
  - Most terms are zero in most bins, so the noise floor is δC ≈ $1/\sqrt{T}$ ≈ 0.05–0.07, near typical term–term correlations.
  - The spectral test needs $T>10K$, so $K\le32$ within a unit.
  - The silence exponent β̃ only needs $P_0(K)$ and is the most robust choice. Silence is also natural here: a cluster of terms unused in a bin.
- **Identifiability:**
  - Restrict to terms with ≥ 20 uses in the unit.
  - Report β̃ and α̃ with connected-quarter errors (quarters of the unit's active time).
  - Expect error bars ~3× those of the mouse data.
  - Within-unit only. A corpus-wide RG would pool periods and absorb the regime changes.
- **Shared-field corrections (the analogue of the place-cell model):**
  - Build a **conditionally independent term model**. Each term is used with probability $p_i(\text{field state}(t))$, where the field state is:
    - the scheduler activity level (messages per bin, from `activity_bins_fixed` with DQ8 trims);
    - time since kickoff;
    - the kickoff/goal projection (`goal_fields`).
  - Simulate, coarse-grain identically, and compare α̃, β̃, the shape of $P_0(K)$ and $\tau_c$ scaling.
  - Do not residualize counts. Residuals have no exact zeros, so $P_0$ and the non-Gaussian $Q_K$ lose their meaning.
  - Shared model priors: hash and merge per family, or include agent-family usage rates in $p_i$.
  - Contemporaneous convergence: terms co-used in the same bin without a read are part of the field model, not coupling.

## Candidate hypotheses
- **HH317 sharpened: β̃, not α̃, separates field from fixed point.**
  - *Observable:* α̃, β̃ and the curvature of $\log M_2$ vs $\log K$ (residual from the power law, as in the place-cell figure), per unit.
  - *Null:* the conditionally independent term model above.
  - *Prediction:*
    - raw α̃ ∈ [1.6, 1.85] in both data and null;
    - the null's $\log M_2$ curves (kink at $K_c$ ≈ the number of terms one kickoff seeds);
    - β̃(data) − β̃(null) ≤ −0.05 only in long free periods (#38, #51), and |difference| < 0.05 elsewhere.
  - *Kill:* data indistinguishable from the null on all three statistics in every unit.
  - *Impostor:* the kickoff/goal field.
- **No dynamic scaling in the dialect.**
  - *Observable:* $\tau_c(K)$ from cluster autocorrelations.
  - *Prediction:* z̃ consistent with 0 (no slowing with cluster size) once time-since-kickoff is in the null, because content dynamics are field-driven (H10, H54).
  - *Impostor:* the scheduler. Bins must be in active windows.
- **Behavior windows are below the scaling regime.**
  - *Observable:* the same RG on the 11-state `p_*` series of agents × states (as variables) per unit.
  - *Prediction:* α̃ < 1.2 and no $Q_K$ convergence after removing the all-present schedule mask.
  - *Impostor:* the scheduler field (H38: 70–80% of regime-III co-activation).

## Caveats
- A fixed point under this procedure is suggestive, not proof of criticality. Shared fields (place fields, kickoffs) give near-power laws over limited ranges. Two decades is the minimum.
- Greedy pairing on noisy correlations can create structure. Rerun on time-shifted surrogates; the exponents should go to 1.
- Normalization choices (mean of nonzero values = 1) matter for counts with heavy tails. Report binarized results too, as the paper did.
- α̃ alone varies 1.4–1.73 across mice. Do not treat a single α̃ value as a fixed point or a field signature.
- Fit within units, never pooled. Mask the holdout.
