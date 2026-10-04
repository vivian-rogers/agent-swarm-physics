# The emergence of life as a first-order phase transition

**Citation:** Cole Mathis, Tanmoy Bhattacharya and Sara Imari Walker, *Astrobiology* 17(3), 266–276 (2017). arXiv:1503.02776.
**File:** mathis-2017-emergence-of-life-first-order-transition.pdf
**Fields:** stat mech, info theory, origins of life

## Summary
A kinetic Monte Carlo model of polymers from two monomer types in a **closed** system (finite resources, recycling through degradation) shows a spontaneous, abrupt switch from "non-life" (polymer mass set by polymerization) to "life" (mass set by selection on replicators). No rate is tuned externally: the transition is driven by feedback between replicators and the free-monomer environment. Replicators exist in both phases. What defines life is that selection on replicator properties redistributes the resources. The mutual information between replicator composition and environment composition, I(R;E), tracks the transition like an order parameter. Waiting times are exponential, there are many frustrated (aborted) transitions, and the replicators that nucleate the transition are usually not the ones finally selected.

## Key formalism
- Monomers '0' and '1', 500 each, no inflow. Rates k_p = 0.0005 (polymerization), k_d = 0.5 (degradation at a uniform random bond), k_r = 0.005 (replication). Sequences with L ≥ r = 7 replicate. No mutation: novelty enters only through degradation and re-polymerization.
- Static fitness: replication rate × α_r = 1 + f(n) ∈ [1.5, 2]; degradation rate × α_s = 1 − f(m) ∈ [0, 0.5], with a replication–stability trade-off. Landscapes I–III differ in how well the fittest sequences match the bulk composition. Landscape IV (all L ≥ 7 equal) is the no-selection control.
- Dynamic (environmental) fitness: replication weighted by β(x_i) = Σ_n y_{n} y_{n+1}, where y_n is the free abundance of the monomer at position n. Fitness therefore depends on how well a sequence matches current free resources.
- Order parameter: I(R;E) between the (#0, #1) composition of replicators and of free monomers. For landscape I, I(R;E) ≈ 3.0 in non-life and ≈ 0.25 in life (Fig. 4). It falls when selected replicators differ from the bulk (LI, LII) and rises when they match (LIII).
- First-order signatures: waiting times to completion are exponential (KS test, 256 runs); there are frustrated trials; nucleating replicators are heterogeneous (~50/50) while the selected ones are homogeneous; formation/degradation ≈ 1 in both phases.
- Through the transition the exploration rate of new sequences is **2 orders of magnitude** higher, and 75% higher in the life phase than in non-life. The transition is degradation-dominated: mass must be freed before it can be re-allocated.
- Transition time (completion = 75% of replicating mass in fit sequences) is non-monotone in k_r. At k_d = 5 it is independent of k_r. At k_d = 0.5–1 it is fastest at **low** k_r, because fast replication locks resources in unfit sequences. Moderate recycling is most conducive.

## Mapping to agent swarms
- **Monomers = agent attention**, which is finite and closed within a goal period (fixed roster × call budget). **Replicators = projects/repos** that recruit agent calls (DQ4 `work_commits`, `work_repos`). **Degradation = abandonment**: an agent leaving a repo frees calls.
- **Environment composition E** = the kickoff/goal field over topics (H54 goal fields), or the topic mix of unallocated calls. **Replicator composition R** = topic mix of active projects (DQ5 cluster labels of their commits, both models).
- **Non-life phase** = allocation mirrors the kickoff (high I(R;E); H54's day-1 centroid picks its own kickoff top-1 in 18/33). **Life phase** = allocation set by the projects' own properties (H77–H79's replicator and autocatalytic readings), with I(R;E) dropping abruptly.
- **Nucleus ≠ winner** maps to H53 (announcement nucleation) and H28 (link-driven herding). The first project to recruit is often not the one that dominates.
- **Exploration burst** = the rate of new repos/new command motifs (`artifact_commands_text`) during re-allocation. This is where H80's high-index motifs would first appear.
- **Impostors.**
  - *Kickoff field:* E is the exogenous field itself, so the test is decoupling from it, not alignment with it.
  - *Scheduler:* day edges produce abrupt allocation jumps. Measure waiting times on the per-call clock with day edges trimmed (DQ8).
  - *Shared priors:* families converging on the same project mimic selection. Require the decoupling within families.
  - *Contemporaneous convergence:* a first-order nucleation spreads from a nucleus through reads (context ledger). Simultaneous switching without reads is a field.

## Candidate hypotheses
- **Kickoff decoupling is abrupt.** Within free goal periods, I(project topics; kickoff field) drops in a step, not a ramp. Waiting times from kickoff to the step are exponential across periods (KS test). Several periods show frustrated herds (a project recruits ≥ 3 agents then collapses) before the step. *Kill:* smooth decay on the H48/H54 settling timescale (≈ 4.5–5 h) in every period.
- **The nucleating project is not the winner** in ≥ 1/2 of periods with a dominant project (H53/H11 herding weeks).
- **Novelty burst at the transition.** New-repo and new-motif rates peak at the step, ≥ 10× the period baseline per active call. This links H79 (artifact network forming) and H80 (assembly index of new motifs).
- **Fast recruitment can frustrate.** Periods with higher per-call recruitment (H78 growth order p > 1) take longer to settle on high-output projects. This is the k_r non-monotonicity; a test for H77's resolution bound.

## Caveats
- A two-letter toy with closed mass and no mutation. "First-order" is shown only by exponential waiting times, abruptness and frustrated trials, with no finite-size scaling.
- I(R;E) can go up or down through the transition depending on the landscape, so it is an order parameter only once the sign is fixed by the fitness landscape.
- Operators re-inject attention (nudges, roster changes, new goals), so the village is not closed. Fit only within goal periods and split at step changes.
- Composition is a coarse-graining. The topic or cluster basis must be a shared instrument fixed before the test.
- Few goal periods per mode give few waiting times; an exponential fit needs pooling with hierarchical shrinkage, reported next to per-period values.
