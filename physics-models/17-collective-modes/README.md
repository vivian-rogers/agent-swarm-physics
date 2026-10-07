# 17 · Collective modes: random-matrix spectra, spiked modes and mode lifetimes

**Fields:** stat mech, random-matrix theory, dynamics, statistics
**References** (none in `../../literature/`; all cited from memory, †): Marchenko & Pastur, *Math. USSR Sb.* 1, 457 (1967)†; Baik, Ben Arous & Péché, *Ann. Probab.* 33, 1643 (2005)† (the spiked-covariance transition); Paul, *Statistica Sinica* 17, 1617 (2007)† (eigenvector overlap above the transition); Laloux, Cizeau, Bouchaud & Potters, *PRL* 83, 1467 (1999)† (eigenvalue clipping); Bun, Bouchaud & Potters, *Phys. Rep.* 666, 1 (2017)† (cleaning large correlation matrices); Allez & Bouchaud, *PRE* 86, 046202 (2012)† (eigenvector dynamics); Ledoit & Wolf, *J. Multivar. Anal.* 88, 365 (2004)† (shrinkage); Schmid, *J. Fluid Mech.* 656, 5 (2010)† (dynamic mode decomposition); Williams, Kevrekidis & Rowley, *J. Nonlinear Sci.* 25, 1307 (2015)† (extended DMD and the Koopman operator).

Added 2026-10-07 (Vivian). Before that date random-matrix theory was listed under "Candidates not yet written up" and used as a tool inside models 01, 11 and 14. The cards below keep their recorded models and verdicts.

## The model

The object is the set of collective modes of the swarm: directions in agent space along which agents move together. A mode is static (an eigenvector of the correlation matrix in one window) or dynamic (an eigenvector of the drift matrix, with a lifetime).

**1. Static modes and the Marchenko–Pastur null.** Take N agents and T samples in a window (minutes of activity or talk spins; windows of content). C is the N × N agent correlation matrix, with eigenvalues λ₁ ≥ … ≥ λ_N and eigenvectors u_k.
- If the agents are independent and the samples are i.i.d., the eigenvalues fill the Marchenko–Pastur bulk [(1 − √γ)², (1 + √γ)²], with γ = N/T.
- An eigenvalue above the edge is a candidate mode.
- **Calibrated edge.** Real series are autocorrelated and share a daily schedule, so the naive edge is wrong. Use the 95th percentile of λ₁ under surrogates that keep each agent's own series and schedule but break cross-agent alignment. H12 and H92 use the trimmed 30-min block shift for spins (size 0.05 for λ₁) and independent within-day circular shifts for content (49 surrogates in H92). H91 uses a finite-T pooled-split null for eigenvectors. See "RMT-cleaned correlation, calibrated edge" in `../DEFINITIONS.md`.

**2. The spiked-covariance transition (Baik–Ben Arous–Péché) as the model.** Let the population covariance be I + ℓ v vᵀ: one collective mode v of strength ℓ on top of independent noise.
- **Detection threshold.** The mode is detectable only if ℓ > √γ. Below the threshold λ₁ sticks to the bulk edge (1 + √γ)², and the sample eigenvector carries no information about v.
- **Eigenvalue above the threshold:** λ₁ = (1 + ℓ)(1 + γ/ℓ).
- **Eigenvector overlap above the threshold:** |⟨u₁, v⟩|² = (1 − γ/ℓ²) / (1 + γ/ℓ).
- These give falsifiable predictions for any claimed mode:
  - Invert the measured λ₁ for ℓ̂. Then predict λ₁ at other window lengths T (for example on half the data), with no new fit.
  - Predict the overlap. Two independent halves of the data each estimate v, so to leading order their eigenvectors overlap as the product of their two overlaps with v. A split-half overlap far below that product means the mode moves or is not one mode.
  - A mode that sits near ℓ = √γ is at the edge of detection. Its direction is mostly noise even when λ₁ passes the edge.
- The formulas assume i.i.d. Gaussian samples. Autocorrelation shrinks T to an effective T_eff (H12's Bartlett T_eff), and a correlation matrix (unit diagonal) is only approximately a covariance spike. Check both on synthetic data at the real N, T and schedule.

**3. Mode structure.**
- **Participation ratio of the spectrum:** PR = (Σλ)² / Σλ². It counts effective dimensions (H12).
- **Inverse participation ratio of a mode:** IPR_k = Σ_i u_{k,i}⁴. It is 1/N for a uniform mode and 1 for a mode on one agent.
- **The uniform ("market") mode is a shared field.** Every agent loads with the same sign. A common drive (the scheduler, a goal, an operator message) produces exactly this mode with no coupling. This is the eigenvalue view of the fields-beat-couplings result in models 01 and 11.
- **Eigenvector stability.** Track the subspace angle between the above-edge eigenvectors of consecutive windows. The stationary null is finite-T sampling noise (Dyson / Allez–Bouchaud diffusion; H91's pooled-split null). Rotation beyond the null means the modes change.

**4. Dynamic modes and lifetimes.** Fit a VAR(1), x(t + 1) = A x(t) + ε, or a multivariate OU process, ẋ = −Γ x + ξ, with A = e^(−Γ Δt).
- Each eigenvalue μ_k of A gives a mode lifetime τ_k = −Δt / ln|μ_k|. A complex pair gives an oscillation.
- Each mode is one OU process of [16](../16-langevin-relaxation/).
- If Γ is not symmetric, the dynamic modes are not the eigenvectors of the correlation matrix. Static modes say what moves together; dynamic modes say what persists.
- **Estimators:** dynamic mode decomposition (DMD) estimates A from snapshot pairs through a truncated SVD. The Koopman (extended DMD) form applies the same idea to nonlinear observables.
- **Example:** H81's regime-I content slow mode, an OU mode with τ_u ≈ 23–28 days.
- **Mode lifetime vs the read kick.** In #51 a read kicks the reader for about 7 calls, and the agent's own well relaxes in about 100 calls (H130). A collective mode made only of read echoes should die at the kick rate. A mode that outlives the agents' own wells needs a field or a long-lived carrier.

## Interesting behavior

- **A sharp detection transition.** A real mode below √γ is invisible, not just noisy. At village sizes (N ≈ 4–21, short windows) many weak modes are below it.
- **Eigenvalue and eigenvector are tied.** Above the threshold λ₁ fixes the expected overlap. A claimed mode whose split-half overlap is far below the prediction fails.
- **One uniform mode is the default.** A shared drive makes one large uniform mode and leaves the rest in the bulk. Localized modes (high IPR) point to groups: rooms, labs, teams.
- **Static order vs persistence.** A large λ₁ can come from a mode that lives minutes (a common schedule) or weeks (culture). Only the dynamic fit separates them.

## Mapping to the village

- **Agents × samples.** Agents present in the window (Claude Code excluded) × 1-min activity or talk spins (trimmed to the all-present window), or × content windows (regime-whitened statement vectors, d = 32, both embedding models).
- **Modes.** The uniform mode is the scheduler or goal field. Room modes separate rooms. Lab modes are mostly style (model 11 pitfall).
- **Dynamic modes.** A day-scale or week-scale VAR on agent content (agent-day vectors); a call-scale VAR on content around reads.
- **Natural experiments.** Kickoffs, the NE42 room merge, the #12 debate motions and the #26 votes change the field and should change the spectrum.

## How to fit

1. Trim spins to the all-present window. Remove the day-level rate per agent.
2. Compute C, its spectrum, PR and IPR per window.
3. Build the calibrated edge from block-shift (spins) or within-day circular-shift (content) surrogates. Count modes above it.
4. For each mode above the edge, invert λ₁ for ℓ̂ with T_eff. Predict λ₁ at T/2 and the split-half overlap. Compare.
5. Track eigenvector rotation against the pooled-split null.
6. Fit a VAR(1) or DMD on the same windows. Report the lifetimes τ_k and compare them with the read kick and the agents' own wells (model 16).
7. Fit per goal period. Compare periods by their fitted ℓ̂, k and τ_k.

## Cards that test it

None of these cards names folder 17. Their recorded models are 01, 11 and 14. Numbers are from each card's latest round.

| Card | What it tests | Latest verdict | Key numbers |
| --- | --- | --- | --- |
| [H12](../../hypotheses/H12-groupthink-dimensional-collapse/README.md) | collective modes above an RMT edge; PR collapse at consensus | mixed (round 1b) | activity market mode above the calibrated edge in 7/24 units (round 1: 22/24, an artifact of the event-drop bug); talk mode 21/24; content mode 24/24 in both embedding models (λ₁/edge ρ bge–gte 0.99); uniform shape 16/18; talk modes separate rooms in 7/10 two-room units. PR: kickoffs do not collapse it; a #12 debate motion lowers it (−25%, 7/9 debates, p 0.010); the lowest-PR weeks are restatement loops |
| [H91](../../hypotheses/H91-eigenvector-rotation-signal/README.md) | eigenvector rotation as a reorganization signal | failed | rotation alarm AUC 0.56 [0.40, 0.71] on 23 kickoffs vs the centroid alarm 0.96 [0.92, 0.99]; between events 86% of placebo pairs lie within the finite-T null, but every day rotates about 1 SD more than a stationary synthetic swarm (median z 1.0); NE42 below z ≥ 2 (talk 1.97); no kickoff in the powered range (W ≥ 16 or N ≥ 16) |
| [H92](../../hypotheses/H92-rmt-cleaned-forecast/README.md) | clipping at a calibrated edge to forecast tomorrow's content matrix | mixed | clipping beats the raw matrix in 26/32 (bge) and 27/32 (gte) periods (gain 0.10 [0.03, 0.16]); the gain grows with q = N/T (Spearman 0.45–0.65); it ties constant-correlation Ledoit–Wolf within 1–2% of MSE (beats the better Ledoit–Wolf in 17/32); talk pair structure is not forecastable beyond its mean (skill 0.05); cleaning erases the #38 talk room block |
| [H81](../../hypotheses/H81-culture-beyond-composition/README.md) | a slow collective content mode beyond composition | supported in regime I (round 2) | τ_u ≈ 23–28 d; contrast 0.237 / 0.208 vs composition-null 95th percentile 0.081 / 0.089; the artifact record does not carry it; one OU τ fits H82 too (joint 20.9 ± 2.8 / 15.5 ± 2.2 d); not seen in regime III; inside #51 the common mode lives about 3 active days; the clock is not identifiable |
| [H106](../../hypotheses/H106-slow-mode-finite-size/README.md) | the slow mode's decay rate vs N (finite-magnet 1/N) | inconclusive | α_k +0.40 [−1.62, 2.41] (bge), +1.22 [−1.45, 3.88] (gte); power 0.00 against α = −1 (oracle SD 0.45); post hoc: near-lag similarity falls from 0.25–0.28 (N < 8) to 0.00–0.11 (N ≥ 8) |
| [H108](../../hypotheses/H108-goldstone-room-wandering/README.md) | persistence of the room content direction (Goldstone wandering vs pinning) | supported by rule, fragile | day-to-day persistence P(1) 0.69–0.95 in 6/8 periods; R_D 4.7 [2.1, 5.9] (gte 5.2 [2.1, 6.4]); without #38 R_D 1.4 (bge); confounded with split size |
| [H101](../../hypotheses/H101-pairwise-vs-multi-information/README.md) | pairs vs higher order in co-usage; the share carried by a uniform field | pairs plus fields; no group term resolved | field-removed pairwise sufficiency ρ_F median 0.91 over 71 units; the uniform item field carries 0.71 of the multi-information in regime I and 0.26 in regime III; higher-order remainder 0.03–0.05 of I_N, field-sized |
| [H36](../../hypotheses/H36-reorganization-alarm/README.md) | susceptibility and multi-information (spectral) alarm vs a topic-shift (first-moment) alarm | physics alarm failed; topic-shift alarm supported (round 2) | physics alarm fails random dates in every variant (p 0.12–0.25); topic-shift alarm AUC 0.92–0.94, firing in the first 30 min of talk on 82–85% of kickoffs |

**Combined result.** Talk and content carry real collective modes against a calibrated edge. The activity mode is mostly the scheduler. The dominant mode is uniform, so it reads as a shared field. Cleaning helps forecasts but ties plain shrinkage. Eigenvector rotation and second-moment alarms lose to a first-moment (centroid) detector at reorganizations. One slow mode (weeks) exists in regime I. No card has tested the spiked-covariance predictions (λ₁ at other T, split-half overlap).

**Status:** partly useful. The spectrum is a good gauge of how many modes there are and how uniform they are. The spiked-mode predictions are untested.

## Nulls and controls

- **Calibrated edge** from surrogates that keep each agent's own series (block shift, within-day circular shift). Never the naive MP edge alone.
- **Finite-T eigenvector null** (pooled split, H91) for rotation.
- **Shrinkage rivals:** Ledoit–Wolf to the identity and to constant correlation (H92).
- **Composition null** for slow modes: who is present, not what they share (H81; size-matched subsets from model 14).
- **Synthetic worlds** at the real N, T and schedule, with and without a planted mode, and with a planted field.

## Pitfalls

- **The field mode masquerades as coupling.** A uniform top mode is what a common drive gives with no coupling. Activity co-movement is mostly the scheduler: daily start/stop explains 0.62 / 0.67 of it in regimes I / III (H50, quoted in H12). A heterogeneous field leaves a larger higher-order remainder than a 4-agent group term (H101). Drives saturate whole-swarm βJ₀ (H26, model 11). Remove the field, then read what is left.
- **Day-edge scheduler co-activation.** Whole-day grids put the day's start and stop into every pair. The cross-day edge has size 0.62 on whole-day grids and 0.19 on trimmed grids; the trimmed block-shift edge has 0.05 (H12 round 1b, DQ8). Trim to the all-present window and use the block-shift edge.
- **Naive and partly corrected edges find false modes.** With no planted mode, naive MP finds one in 50–90% of synthetic runs (autocorrelation). T_eff-MP finds one in 98% under heterogeneous daily profiles, and within-day circular shifts in 70% (H12 synthetic).
- **A day-level data loss is a field** (RE-A1): the activity_bins bug dropped a day-specific share of every agent's events and made a collective mode against cross-day nulls.
- **Non-stationarity.** Kinetic Ising parameters drift inside long periods (H120: #38 drift ratio R 1.95 activity, 2.18 talk; #51 main body 2.17 / 2.14), while the 8-day unit 38a does not drift. A drifting field adds a slow spurious mode and rotates eigenvectors; content modes rotate about 1 SD a day more than a stationary swarm (H91). Use windows shorter than the drift and compare halves.
- **Ledoit–Wolf vs clipping.** With one dominant uniform mode, shrinkage to constant correlation already captures it, and clipping only ties it (H92). Report shrinkage as the strongest rival. Clipping also deletes real structure below the edge (the #38 talk room block).
- **Small N and T.** With γ = N/T large, the threshold √γ is high and only one or two modes can pass. H91 had no kickoff in its powered range. A size law across periods compares segments of one trajectory (H106).
- **Content fluctuates in few dimensions.** Isotropic surrogates are 2–3× too narrow for embedding statistics; content uses about 5–12 of 32 whitened dimensions (H20, model 11). Build nulls from the empirical covariance.
- **A second-moment alarm loses to a first-moment one** (H36, H91): at a reorganization the mean moves before the covariance does. Compare any spectral alarm with the centroid shift.

## Hypothesis seeds

- **Spiked-mode test for the content mode:** invert λ₁ for ℓ̂ in each period (H12's content mode), predict λ₁ at T/2 and the split-half eigenvector overlap, and test both.
- **Field removal before the spectrum:** remove the measured scheduler, goal and operator fields, then count modes. A mode that survives is a coupling candidate.
- **Dynamic modes on the call clock:** a DMD or VAR(1) on #51 content around reads. Test whether the collective lifetimes match the read kick (≈ 7 calls) or the wells (≈ 100 calls).
- **Localized modes as rooms and labs:** test whether high-IPR modes match DQ6 rooms, and whether lab modes vanish after style residualization.
