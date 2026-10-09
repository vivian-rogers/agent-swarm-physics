# The information theory of individuality

**Citation:** David Krakauer, Nils Bertschinger, Eckehard Olbrich, Jessica C. Flack and Nihat Ay, *Theory Biosci.* 139, 209–223 (2020), doi:10.1007/s12064-020-00313-7. arXiv:1412.2447.
**File:** krakauer-2020-information-theory-of-individuality.pdf (published version, added 2026-10-09); krakauer-2020-information-theory-of-individuality-arxiv-v1.pdf (arXiv v1, 2014, which these notes were first written from).
**Fields:** info theory, complex systems, biology of individuality

## Summary
The paper treats an individual as a system–environment partition that carries information from its own past into its own future. Individuals are discovered, not assumed. The authors split the predictive information $I(S_{n+1};S_n,E_n)$ by the two orders of the chain rule. Each order assigns the shared part to the system or to the environment, and each gives a kind of individuality. Individuality is continuous and can be nested, and a colony can be an individual whose members are individuals. A boundary is found by moving variables from the environment into the system while individuality rises and non-closure falls. The paper is a formal proposal with a toy model. It reports no empirical estimates.

**Warning on names (arXiv v1 vs published).**
- arXiv v1 says "genomic determination" and "environmental determination". The published version says organismal and colonial individuality.
- The symbols are the same in both: $A^*=I(S_{n+1};S_n)$ and $A=I(S_{n+1};S_n|E_n)$.
- Published names (checked on PMC7244620; the local PDF predates them):
  - **organismal** = $A^*$;
  - **colonial** = $A$;
  - **environmental determination** = $nC$;
  - **environmental coding** = NTIC.

## Key formalism
- **Two chain-rule orders.** $I(S_{n+1};S_n,E_n)=I(S_{n+1};S_n)+I(S_{n+1};E_n|S_n)=I(S_{n+1};E_n)+I(S_{n+1};S_n|E_n)$.
- **Organismal individuality:** $A^*=I(S_{n+1};S_n)=\mathrm{SI}+\mathrm{UI}_S$.
  - All self-predictability, including what is shared with the environment (SI).
  - High when "the system is in control of its environment" or has internalized it by adaptation.
- **Colonial individuality:** $A=I(S_{n+1};S_n|E_n)=\mathrm{CI}+\mathrm{UI}_S$.
  - Self-predictability beyond the environment: unique information plus complementary (synergistic) information with the environment.
  - High for systems that share little with their environment (microbes, colonies).
  - The arXiv text says "each organism will obtain a high value of A whereas the community or colony will obtain a high value of A* − A".
- **Environmental determination (non-closure):** $nC=I(S_{n+1};E_n|S_n)=\mathrm{CI}+\mathrm{UI}_E$.
  - $nC=0$ is informational closure. It implies sufficiency $I(S_{n+1};S_{n-1}|S_n)=0$, but not the converse.
- **Identity:** $A^*+nC=A+I(S_{n+1};E_n)$.
- **Environmental coding (non-trivial informational closure):** $\mathrm{NTIC}=A^*-A=I(S_{n+1};E_n)-nC=\mathrm{SI}-\mathrm{CI}$.
  - $A^*<A$ is possible: the complementary (XOR) case.
  - The PID atoms (SI shared, UI unique, CI complementary) need a chosen redundancy measure. The paper cites Williams–Beer and Bertschinger et al. and fixes none.
- **Longer histories:** the same relations hold with blocks $S^n_{n-l}$, $E^n_{n-k}$. Non-sufficiency $I(S_{n+1};S^{n-1}_{n-l}|S_n)$ appears as an extra term.
- **Boundary expansion** (system $S$ grows by $\Delta S$; remaining environment $E'$):
  - $nC'=nC-I(S_{n+1};\Delta S_n|S_n)+I(\Delta S_{n+1};E'_n|\Delta S_n,S_{n+1},S_n)$: the internalized flow minus the newly exposed flow.
  - $A^{*\prime}=A^*+I(\Delta S_{n+1};S_n|S_{n+1})+I(S_{n+1}\Delta S_{n+1};\Delta S_n|S_n)$.
  - $A'=A+I(S_{n+1};\Delta S_n|E'_n)+I(\Delta S_{n+1};S_n\Delta S_n|E'_n,S_{n+1})$.
  - **Both $A$ and $A^*$ never decrease when the system grows.** The rule is to keep enlarging while individuality rises *and* $nC$ falls, and to stop when an addition does not improve prediction.
- **Toy model (published version, via PMC):**
  - Binary $s,e\in\{\pm1\}$ with logistic (Glauber-type) updates: self-coupling α, cross-coupling β, interaction γ (an $s_n e_n$ term).
  - Random environment: both kinds of individuality are high at large $\alpha_S$, $\beta_S$ when $\gamma_S$ = 0.
  - Correlated environment: high $A^*$ with low $A$ and low $nC$ at large $|\beta_S|$ and small $\gamma_S$, i.e. the environment is internalized.
- **Stated caveats:** the time scale is "instrumentally critical"; the partition must be searched for; robustness and homeostasis are not modelled.

## Did H01 and H58 apply it correctly?
- **The formulas are right. H58's estimator is good.**
  - H58 computes the three conditional mutual informations as held-out log-loss differences:
    - $I(x';x)=L(x')-L(x'|x)$;
    - $I(x';x|y)=L(x'|y)-L(x'|x,y)$;
    - $I(x';y|x)=L(x'|x)-L(x'|x,y)$.
  - This is a sound, regularized estimator. Transfer entropy is a log-likelihood ratio.
  - H01's $P_G=A^*_G+I(x';y)$ is the correct chain rule. Its $E_G$ is the paper's $nC$, and "environmental determination" is the right name.
- **The names and the star are swapped.**
  - H01 calls $I(x';x|y)$ "$A^*$, self-determined, organismal". H58 calls $I(x';x)$ "colonial $A$" and $I(x';x|y)$ "organismal $A^*$".
  - In the paper, $I(x';x)$ is **organismal $A^*$** and $I(x';x|y)$ is **colonial $A$**.
  - So H58's "median colonial 0.05–0.28 bits per bin" for agent + own artifact is organismal $A^*$. H58's $\iota_G$ and P4 ("organismal ι") use colonial $A$.
- **What this does to the conclusions.**
  - The tests ran on the right quantity. Self-prediction beyond the environment is the colonial measure, which is what an "individual beyond the field" claim needs.
  - The sentence "co-allocation is environmentally determined, not organismal" should read: crews have low colonial $A$ relative to size-matched groups. Their self-prediction is mostly shared with the field ($A^*$ high, NTIC = SI − CI > 0, i.e. environmental coding), and $nC$ is large.
  - In the paper's terms a well-adapted unit sharing information with its environment is *more* organismal, not less. So "not organismal" is wrong as worded.
- **Additions that are not in the paper (fine, but they should be labelled as project choices):**
  - the normalization $\iota=A/H(x')$ or $A/L(x')$;
  - the composition and member-shift z-scores.
  - The size-matched composition null is *required* by the monotonicity result: raw $A$ and $A^*$ always favour the bigger unit. H01 handled this correctly.
  - H01's one-member add/remove local-maximum search is a reasonable discrete version of the paper's boundary rule. It used z rather than raw increments, and it did not track $nC$ as the paper asks.
- **Gap.** $y$ in H01 and H58 was the rest of the swarm's activity plus human and automated messages. The paper insists that the environment be defined rigorously. The scheduler, kickoff and prior fields were not explicit components of $E$, so colonial $A$ may still contain field-driven persistence.

## Mapping to agent swarms
- **$S$ candidates:**
  - agent;
  - agent + own artifact (allocation state from DQ4);
  - repo + contributors;
  - room;
  - the culture residual (HH293, DQ5 `style_resid_period` agent-day vectors).
- **$E$:** bundle the impostors into ≤ 3 coarse features:
  - scheduler phase (`call_windows.gap_kind`, all-present mask);
  - kickoff/goal projection (`goal_fields`);
  - the rest of the swarm's allocation or content state.
  The agent prior enters as a covariate of the model, not as part of $E$, because it is constant within a unit.
- **Sizes and identifiability:**
  - Allocation alphabets ≤ 7 symbols (H58), 30-min bins, $T\sim10^2$–$10^3$ agent-bins per unit.
  - Plug-in tables over $(S',S,E)$ with 7·7·27 cells are not identifiable. Use held-out parametric log-loss models (H58's stay/popularity mixture) and day-blocked cross-validation.
  - Expect held-out estimates to *fall* when variables are added (overfitting). That is the opposite of the theoretical monotonicity, so a "boundary" can be set by estimator variance. Check boundaries on synthetic skeletons.
- **Shared-field corrections:**
  - Colonial $A$ removes the field only if the field is in $E$.
  - Organismal $A^*$ includes the field by construction, so report NTIC and never use $A^*$ alone for an egregore claim.
  - Contemporaneous convergence enters through $E_n$ at the same step: keep $E$ strictly lagged.
  - Operator messages that react to idleness are endogenous; do not put them in $E$.

## Candidate hypotheses
- **HH321 sharpened: colonial individuality vs bin width, not vs lag.**
  - *Observable:* $A(\Delta)$ and $A(\Delta)/I(S';S,E)$ with bins $\Delta$ ∈ {30 min, 2 h, 1 day}, for agent + artifact, repo-centered units and the culture residual. Each is reported as a z-score against size-matched random units.
  - *Prediction:* agent + artifact z peaks at Δ = 2 h–1 day. Repo units peak at ≥ 1 day. The culture residual has no Δ with z ≥ 2 inside units.
  - *Impostor:* the kickoff field. It must be in $E$.
- **Crews are environmental coders.**
  - *Observable:* NTIC/$A^*$ for H58 crews vs agent + own artifact.
  - *Prediction:* crews ≥ 0.5, agent + artifact ≤ 0.3. Most of a crew's self-prediction is shared with popular-artifact and goal fields.
  - *Impostor:* shared model priors. Same result in cross-family crews.
- **Boundary expansion stops at the artifact.**
  - *Observable:* the paper's increments. Start from the agent; add its own artifact (ΔS), then the repo's other contributors.
  - *Prediction:* the first step lowers $nC$ by ≥ 0.05 bits per bin. The second step raises $nC'$ (new exposed flow), so the boundary closes at agent + artifact (HH300).
  - *Impostor:* the scheduler. Use within-active-window bins only.
- **NE43 amputation.**
  - *Observable:* village-scale $nC$ with and without operator/scheduler variables in $S$, before and after nudger-off.
  - *Prediction:* including the operator lowers village $nC$ before NE43 by more than after it (HH305).

## Caveats
- The paper gives definitions, not estimators, null models or data. Every number in the project's tests comes from project choices.
- PID-based readings (SI, CI) depend on the redundancy measure. Report only chain-rule quantities unless BROJA and $I_{ccs}$ agree.
- Results depend on time scale and partition. State both, and fit within goal periods.
- Mask the holdout.
