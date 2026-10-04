# Exploration of synergistic and redundant information sharing in static and dynamical Gaussian systems

**Citation:** Adam B. Barrett, *Phys. Rev. E* 91, 052802 (2015). arXiv:1411.2832 (v2, 2015-04-30).
**File:** barrett-2015-synergy-redundancy-gaussian-systems.pdf
**Fields:** info theory, dynamical systems, neuroscience methods

## Summary
This is the first partial information decomposition (PID) study of continuous Gaussian variables. Net synergy (whole minus sum) is common in linear Gaussian systems, even when the two sources are uncorrelated. The key result: for a jointly Gaussian system with a **univariate target** and sources of any dimension, every PID in which redundancy and unique information depend only on the (target, source) pairwise marginals reduces to one decomposition, **MMI**. That class includes Williams–Beer I_min, Griffith/Bertschinger (BROJA) and Harder. In MMI, redundancy is the smaller of the two mutual informations. The paper then works out PIDs for VAR processes and shows what they mean for transfer entropy, Granger causality, causal density and integrated-information measures.

## Key formalism
- PID of I(X;Y,Z) = U_Y + U_Z + R + S, with I(X;Y) = U_Y + R and I(X;Z) = U_Z + R. Net synergy WMS = I(X;Y,Z) − I(X;Y) − I(X;Z) = S − R.
- Trivariate unit-variance Gaussian with corr(X,Y) = a, corr(Y,Z) = b, corr(X,Z) = c:
  - WMS = ½ log[(1−a²)(1−b²)(1−c²) / (1 − a² − b² − c² + 2abc)].
  - For three variables, co-information and O-information Ω equal −WMS = R − S.
  - Uncorrelated sources (b = 0) with a = c give WMS = ½ log[(1−a²)²/(1−2a²)] > 0. At a = 0.5 this is 0.059 nats.
  - The positive synergy comes from the concavity of log. With information measured as variance reduction, WMS_Σ = [(a²+c²)b² − 2abc]/(1−b²), which is 0 at b = 0.
- **MMI PID:** R = min{I(X;Y), I(X;Z)}. The weaker source has zero unique information. S = the extra information the weaker source adds once the stronger is known; for |a| ≤ |c|, S = ½ log[(1−b²)(1−c²)/(1 − a² − b² − c² + 2abc)]. Redundancy does not depend on the source–source correlation b. S = 0 at b = a/c and diverges at the singular limits. MMI is **not** unique for a multivariate target.
- Dynamics (VAR(1)): one-lag pasts can carry net synergy that vanishes for infinite pasts (Ex. 1). Ex. 2 has R = S = 0 at one lag. In Ex. 3 (two independent sources driving X), S grows with the weaker coupling: ≈ α⁴/2 for small α, net synergy ≈ log(α/√2) for large α, and WMS/I ≈ 0.1 at α = 0.5.
- **Transfer entropy** T_{Y→X} = U(X_t; Y_{t−1}|X_{t−1}) + S(X_t; X_{t−1}, Y_{t−1}), while lagged MI I(X_t; Y_{t−1}) = U + R. TE can exceed lagged MI, and conditional TE can exceed unconditional TE. Linear Granger causality = 2 × TE for Gaussians.
- Causal density counts synergy twice and ignores redundancy. Global TE weights all atoms equally and grows with source correlation. The paper proposes a synergistic complexity measure without an application.

## Mapping to agent swarms
- **Estimators for HH298 (O-information).** Gaussian Ω on agent-day content vectors: DQ5 `agent_day_white32_*` or style residuals (both models), projected to a few principal components, or one scalar per agent. For triplets, Barrett's closed form gives Ω = −WMS directly. A **shared field** gives Ω > 0: equicorrelated r = 0.5 gives Ω = +0.085 nats per triplet.
- **Residualization artifact (new, from these formulas).** Removing the field by subtracting the **leave-in** village mean induces pairwise correlations −1/(N−1) among residuals:
  - triplet Ω = −0.085 nats at N = 4, −0.0038 at N = 8 and −0.0003 at N = 16 (computed from the formula above);
  - the full-set covariance becomes singular, so full-set Gaussian Ω → −∞.

  That is spurious synergy, exactly the HH298 egregore-positive sign. Regress on exogenous fields (kickoff, operator, scheduler) and leave-one-out means only.
- **Estimators for HH319 (two reads → next content).** The target is the recipient's next content direction. If it is univariate (projection on one axis), BROJA, I_min and Harder all equal MMI, so a second redundancy measure from that class is not a check. Use a multivariate target (where MMI is not unique), or a measure outside the class (e.g. I_ccs or dependency-constraint PID; not in this paper). Report WMS_Σ (variance-reduction net synergy) too: it is 0 for uncorrelated reads, so a positive WMS with WMS_Σ ≈ 0 is the log-concavity effect, not integration.
- **Consequence for HH299.** With Gaussian MMI and the agent's own past as the stronger source (the expected case: high storage, H58), the read has zero unique information and **all** transfer entropy is synergy. MMI would label every transfer "modification" by construction. Use discrete states (`behavior_states_v3`, DQ4 which-repo) with BROJA, where it differs from MMI, or Kolchinsky's copy measure.
- **Impostors.**
  - *Scheduler:* common on/off makes every pair correlated (Ω > 0). Use DQ8 trimmed windows and the per-call clock.
  - *Kickoff field and shared priors:* the redundancy source; condition on them as exogenous regressors, not via the village mean.
  - *Contemporaneous convergence:* two unread messages correlated with the target give R > 0. Add the in-flight placebo pair at matched lag as a third "source" baseline.

## Candidate hypotheses
- **Field-removed Ω is near zero, not negative.** After regressing on exogenous fields with leave-one-out means, triplet Ω within rooms lies in [−0.005, +0.01] nats per triplet, and the leave-in version is more negative by ≈ the N-dependent artifact above. *Kill for HH298:* Ω < 0 survives the leave-one-out construction and a block-shift null.
- **Reads are redundant.** In HH319, MMI synergy from two reads ≤ 10% of I(target; both reads), and WMS_Σ ≈ 0, consistent with H59's "one read = one kick". *Kill for the null:* WMS_Σ > 0 beyond a shuffled-pair null.
- **TE exceeds lagged MI only at read-out hops.** Where T_{Y→X} > I(X_t; Y_{t−1}) (net synergy between own past and the read) is evidence of state-dependent transfer. It should appear at named-message read-outs (H50's J₁) and not across rooms.

## Caveats
- Everything here assumes joint Gaussianity. Content projections are roughly Gaussian; behavior states are discrete and need discrete estimators.
- MMI's uniqueness needs a univariate target. With vector targets, PID choices diverge again.
- Gaussian log-information gives synergy from concavity alone. Barrett suggests variance-based information as a cleaner check, but it is not symmetric.
- Infinite-past and one-lag decompositions differ (Ex. 1). Fix the lag by the read-out structure (one call), and report sensitivity.
- Small N per period (4–32 agents) makes high-dimensional Ω unstable; work with triplets or low-rank projections and bootstrap by day blocks.
