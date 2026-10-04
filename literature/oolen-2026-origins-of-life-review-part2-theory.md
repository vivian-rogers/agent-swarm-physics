# What it takes to solve the origins of life: An integrated review. Part 2: Theoretical methods and emerging trends

**Citation:** OoLEN (Origin of Life Early-Career Network), S. Asche, C. Bautista, C. Blanco, D. Boulesteix, A. Champagne-Ruel, C. Mathis, O. Markovitch, Z. Peng, A. V. Dass, et al., *Cell Reports Physical Science* 7, 103211 (2026). DOI: 10.1016/j.xcrp.2026.103211
**File:** oolen-2026-origins-of-life-review-part2-theory.pdf
**Fields:** dynamics, info theory, thermodynamics, stat mech

## Summary
This is a textbook-style survey of the theory used in origins-of-life (OoL) research: quantum chemistry and molecular dynamics, chemical kinetics and reaction networks (CRNs), network autocatalysis, replicator, agent-based and whole-cell models, information theory and phylogenetics. It also covers emerging trends: omics, lab automation, protocells and evolution experiments. It is a map with few equations and no new results. **Not in this paper:** assembly theory, open-ended-evolution (OEE) measures, agnostic biosignatures and any quantitative "lifeness" score. The error threshold appears only via citations (Schuster & Swetina 1988; Takeuchi & Hogeweg 2007). Items marked *(std)* below are standard definitions from the cited primary sources, not the paper's content.

## Key formalism
- **CRN kinetics.**
  - Flux: $J=k^+\prod[X_i]^{\nu_i}-k^-\prod[X_i]^{\gamma_i}$, with $d[X_i]/dt=\sum_r(\gamma_{ir}-\nu_{ir})J_r$.
  - Affinity: $A=RT\ln(J^+/J^-)$.
  - A non-equilibrium steady state (NESS) has $J_r\neq0$; equilibrium has $J_r=0$.
  - The CSTR (a flow reactor with dilution) is the canonical open boundary.
  - *Network expansion* iterates "add all products of the current set" until closure.
- **Network autocatalysis (Table 2).** The models split on whether every node must be catalysed:
  - yes: (M,R) systems, hypercycles, RAF;
  - no: COT, stoichiometric autocatalytic motifs, GARD (which has compositional heredity).
- *(std)* **RAF** (Hordijk–Steel). $\mathcal R'$ is a RAF on food set $F$ if every reactant is in $\mathrm{cl}_{\mathcal R'}(F)$ and every reaction is catalysed by a member of that closure. The maxRAF is found by polynomial-time pruning; irrRAFs are its minimal sub-RAFs.
- *(std)* **COT** (Dittrich). A set $O$ is an organization if it is closed (it produces nothing new) and self-maintaining: some flux $v>0$ within $O$ gives $Sv\ge0$.
- **Replicator order.** $\dot x=c\,x^p$:
  - $p=1$: exponential growth;
  - $p=2$: hyperbolic growth, which underlies hypercycles, bistability and patterning;
  - $p=1/2$: parabolic growth, with coexistence.

  Mutation–selection dynamics are $\dot x=(QW-\phi)x$. *Survival of the flattest:* at high mutation rates, robust variants beat fast ones.
- *(std)* **Error threshold** (Eigen). A master sequence of length $L$, per-site fidelity $q$ and superiority $\sigma$ persists if $q^L\sigma>1$, so $L_{\max}\approx\ln\sigma/(1-q)$. The hypercycle was proposed to beat this without an error-correcting enzyme. It is parasite-prone, and compartments or space (the stochastic corrector) rescue it.
- **Information.**
  - $H$, $I(X;Y)$ and $D_{KL}$;
  - selection as information gain (Kimura);
  - functional information *(std)*, $I(E_x)=-\log_2F(E_x)$ (Szostak);
  - maintainable information scaling with $N,\mu$ (Hledík et al.);
  - the transition from non-life to life as a **first-order phase transition in replicator–environment mutual information** (Mathis et al. 2017). This is the only lifeness-like order parameter in the paper.
- **Phylogenetics and experiments.**
  - Homology vs homoplasy (convergence); lateral transfer breaks trees and clocks.
  - Spiegelman: selection for replication speed shortens the replicator.
  - Foote et al. 2023 discuss false positives for signatures of evolution.
- *(std, absent from the paper)* **Assembly theory.**
  - Assembly index $a(x)$: the minimal number of joins to build $x$, reusing intermediates.
  - Ensemble assembly: $A=\sum_i e^{a_i}(n_i-1)/N_T$, with copy number $n_i$.
  - For strings, $a$ is close to the smallest straight-line grammar, and is upper-bounded by Re-Pair/LZ-style grammar compression.

## Mapping to agent swarms
- **Network.**
  - Species: `artifacts` (repo, site, file).
  - Reactions: agent-session × repo write episodes (DQ4 `work_commits`, joined via `artifact_commands_text.out_hashes`).
  - Reactants: artifacts read or cloned in the session (`artifact_mentions` with `how ∈ {url, output, bare}`).
  - Catalysts: artifacts whose code is *executed*, i.e. HH244's automata (`work_commits.automated`, 112k of 192k agent-identity commits) and tool repos that were cloned and run.
  - Food set: external platforms, kickoff-named and pre-period artifacts.
- **The catch.** Agents are food *and* catalyst, both supplied by the operator (`roster`). A RAF that counts agents as catalysts is therefore trivial. Only *artifact-only* catalysis is informative.
- **HH244 is mostly first-order self-catalysis.** A cron job committing to its own repo is a one-member irrRAF, e.g. the 81.6k-commit GPT-5 stream. A collective set needs cross-artifact cycles: tool A builds B, and B's CI updates A.
- **COT fits HH302.** Self-maintenance means each long-lived infrastructure artifact gets commit flux at least as large as its decay (failing builds, link rot via `work_repos.has_site`, staleness).
- **The error threshold never binds.**
  - Git copies exactly ($q\approx1$).
  - H07's divergence is editing (about 0.0013 per file-touch) plus convergent repair, which is homoplasy rather than copying error.
  - Chat-borne ideas are subcritical (H34: R̂ 0.06–0.39, about 0.2 typical; expected depth $1/(1-\hat R)\approx1.25$ generations). They die for lack of reproduction, not from mutation.
  - The artifact store plays Eigen's missing error-correcting master: agents re-read originals (H44, H58), which resets fidelity each generation.
- **Assembly index.**
  - Inputs: windows of `actions_bash_head_fixed.bash_head_fixed` per session, and per-repo commit sequences (file sets, gaps).
  - Scripts are cheap to assemble ($a\sim\log n$ for a loop) with high copy number.
  - AT's rule "high $a$ × high copy ⇒ selection" is fooled by **shared model priors**: every LLM emits the same git idioms on day 1.
- **Egregore lifeness checklist (HH290–HH306).** Each criterion, with the data that would show it:
  - catalytic closure: an artifact-only RAF, or repos recruiting hosts (HH301);
  - self-maintenance: a COT organization with compensation after `roster` exits (HH302);
  - heredity with selection: inheritance at splits (HH304), survival across turnover (HH291);
  - environment coupling (Mathis's MI jump): HH296;
  - boundary: HH300;
  - open-endedness: a novelty rate that does not decay across seasons.

  The binding constraint is food. Hosts, compute and schedule come from operators (NE43), so at best an egregore is a symbiont of operator-supplied hosts (HH305).

## Candidate hypotheses
1. **The artifact RAF is small and mostly self-loops.**
   - *Observable:* maxRAF and irrRAF sizes per non-holdout period (#30+) under artifact-only catalysis; the share of work commits inside the maxRAF.
   - *Null:* catalysis edges rewired, preserving read counts; and a time-reversed null.
   - *Impostors:* kickoff (named artifacts go in the food set); scheduler (cron self-loops counted separately).
   - *Prediction:* maxRAF ≤ 20% of work commits; irrRAFs of size ≥ 3 in ≤ 1/3 of periods, not above the null.
2. **Replicator order separates herding from labor division.**
   - *Observable:* fit $\dot n_j=c\,n_j^p$ to contributors or work commits per repo on the per-call clock (H40).
   - *Null:* $p=1$, with goal-named repos as inflow.
   - *Impostors:* kickoff naming (H54); pre-read adoptions (H53).
   - *Prediction:* $p$ of 1.2–1.5 in the shared-artifact herding weeks (H11); $p\le0.7$ in own-artifact weeks.
3. **Artifact anchoring evades the error threshold.**
   - *Observable:* survival across full carrier turnover of HH291 conventions, anchored (hardcoded in an artifact) vs chat-only.
   - *Null:* matched on initial use rate.
   - *Impostors:* shared priors (re-invention in isolated forks); an in-flight placebo for convergence.
   - *Prediction:* anchored items survive ≥ 3× as often; chat-only lineages have median depth ≤ 2.
4. **Assembly index adds nothing over compression.**
   - *Observable:* AUC for DQ4 automated vs agent commits from sequence features only (LZ76 vs grammar $a$).
   - *Impostor:* the scheduler (report timing-only AUC).
   - *Prediction:* compression AUC ≥ 0.9; $a$ adds < 0.02.
   - *Second prediction:* ≥ 70% of high-$a$, high-copy bash motifs appear on an agent's first day and across families, which identifies them as the prior, not selection.
5. **The infrastructure core is a COT organization that outlives its makers.**
   - *Observable:* the maximal closed, self-maintaining long-lived artifact set per period, followed across boundaries.
   - *Null:* size- and rate-matched random sets.
   - *Impostor:* kickoff (exclude goal-named repos).
   - *Prediction:* ≥ 30% of post-exit maintenance comes from non-founders within 2 weeks; persistence beyond the null at ≥ 2/3 of boundaries.

## Caveats
- The review is broad and shallow. Its primary sources (Hordijk–Steel, Dittrich, Eigen–Schuster, Mathis 2017, Szostak) are not in `literature/`, and the *(std)* formulas need checking against them.
- Assembly theory, OEE, agnostic biosignatures and lifeness need their own notes: Sharma et al. 2023 and Marshall et al. 2021, AT's "≈ compression" critics, Dolson et al. 2019 (MODES), and Foote et al. 2023.
- The reaction network is inferred from commands. `cwd` precision is 0.89, git is dense only from #30, and session turns must be time-sorted.
- "Closure" is always relative to an operator-supplied food set.
- Mass action, deficiency theory and affinity have no token-level physics. Use them as structure only.
