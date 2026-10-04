# H129: Project hopping carries cycle currents: the sticky Potts walker breaks detailed balance

**Status:** exploratory round 1 **done (2026-10-04, non-holdout only): HH370 fails. Project hopping carries no circulation beyond the drift from older to newer projects, and dwell times are not geometric (hazards age).** Card and predictions written 22:16–22:19 UTC before any real-data statistic; Amendment A1 (23:10 UTC) after the synthetic, before real data; A2 post hoc. Approved by Vivian in the dashboard vetting panel 2026-10-04 from HH370.
- **HH370's kill test (P1) met:** the age-signed triple affinity A_3 beats the per-agent reversal null in 3/9 testable shared-goal unit-channels (G31 work 1.13, G31 attention 0.50, G44 attention 1.17); 6/9 sit inside it.
- **No circulation beyond age (P2):** the rotation-summed triple cycle affinity 𝒜_cyc exceeds both the reversal null and the calibrated age walker in 0/9 (synthetic power 0.55–0.97 for a planted cycle of κ = 2 nats). The Hodge curl is not identified at these counts (A1).
- **Age drift is small but consistent (post hoc sign test, A2):** net flow to newer projects m_2 > 0 in 30/37 testable unit-channels (binomial p = 0.0002; 0.03–0.21), significant alone in 8/34 (P4 failed as written).
- **Dwell (P5a failed):** the hop hazard falls with dwell in 32/39 unit-channels (work γ ≈ −0.2 to −0.4, attention −0.5 to −1.6 per e-fold): trap aging, not a geometric sticky walker. Hop rate vs H93's habit: ρ −0.29 (p 0.53, 7 periods).
- **Natives:** G38 (births throughout) supported on work: m_2 0.17 (p 0.027) with 𝒜_cyc inside the age walker; G44 rooms mixed; G35 (fixed set) untestable, all statistics inside their nulls.
- Scorecard A1 B1 C1 D1 E0 F1 G1 H1 I0. `analysis/confirm.py` (#45–#47) frozen and dry-run; **not run**.
**Question (GOALS.md):** **Q6** (thermodynamics and selection: is project hopping a housekeeping cycle current or only the excess of births?), with **Q2** second (field vs dynamics: is the arrow of project hopping set by project age, a drift field, or by a cyclic force).
**Fields:** stochastic thermodynamics (detailed balance, Kolmogorov criterion, Schnakenberg cycle affinities, excess vs housekeeping), stat mech (kinetic Potts walker with a habit field), dynamics (dwell-time distributions, hazards)
**Literature:** [Kolchinsky, Dechant, Yoshimura & Ito 2026](../../literature/kolchinsky-2026-generalized-free-energy-excess-housekeeping.md) (housekeeping EP needs a cycle; excess is net occupancy change); [Aguilera, Ito & Kolchinsky 2026](../../literature/aguilera-2026-entropy-production-nonequilibrium-maxent.md) (EP as statistical irreversibility, no heat bath; path-level bounds). Background named, not filed (†): Schnakenberg, "Network theory of microscopic and macroscopic behavior of master equation systems", *Rev. Mod. Phys.* 48, 571 (1976)†; Kolmogorov's criterion for reversibility (Kelly, *Reversibility and Stochastic Networks*, 1979)†; Jiang, Lim, Yao & Ye, "Statistical ranking and combinatorial Hodge theory", *Math. Program.* 127, 203 (2011)† (gradient vs curl split of a net flow on a graph).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime; *Agent state (categorical, project, work ledger)* (H11 round 1b) as carried by *Host (work ledger, call-clock expiry)* (H77/H78, W = 30, E = 100); *Agent state (categorical, project/artifact strict)* (H11; attention channel, raw project); *Birth*, *Departure*, *Expiry* (H77/H78); *Housekeeping EP σ_hk* and *Excess EP σ_ex* (H76: housekeeping needs a cycle of ≥ 3 states); *Entropy production / irreversibility* (here a path-count affinity, not a rate). New named variants proposed (defined under Observables; DEFINITIONS.md not edited): **project hop (H129)**, **project age rank (H129)**, **age-signed triple affinity A_3 (H129)**, **triple cycle affinity 𝒜_cyc (H129)**, **net age flux m_2 (H129)**, **Hodge curl magnitude C_2 (H129)**, **dwell (own calls, H129)**.
**From:** HH370 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/02-nonequilibrium-ising/` (broken detailed balance; time-reversal null), `physics-models/10-potts/` (kinetic Potts walker with habit), `physics-models/15-stochastic-thermodynamics-selection/` (excess vs housekeeping; cycles)
**Builds on:** H93 (habit b_own 2.5–6 nats; share coefficient not identified as J), H94 (ownership), H56 (cycle affinities and potential parts of action chains), HH56 (work cycles carry currents), H76 (excess vs housekeeping split), H77/H78 (host replay; 66% of recruitments are returns), H72 (trap aging in idle gates: decreasing escape hazard).
**Data inputs (shared tables first):** DQ4 `work_commits` through `infra/shared/replicator_hosts.py` (host replay; agent-work filter), `call_windows` (own-call clock for dwell and expiry), `project_states` (attention channel; W = 30, sources all, raw `project`, non-holdout rows), `calendar`, `period_units`, `roster`, `ground_truth_labels` (`room_assignment`, #44). H93's per-period habit coefficient b_own is read from `data/processed/H93-brock-durlauf-project-choice/results/G<NN>.json` (read-only data dependency, no code import). No message text; repo and project names hashed on output.

## Source HH (verbatim from the HH list, including refinements)
- **HH370 · Project hopping carries cycle currents: the sticky Potts walker breaks detailed balance.** H93 found habit dominates project choice (b_own 2.5–6 nats). A kinetic Potts walker with a habit field hops rarely. If hopping only followed a fixed attractiveness, the flows A→B and B→A would balance. Projects being born, finished and abandoned instead drive a net circulation (A→B→C→A).
  - *Prediction:* on agent project-transition triples, the cycle affinity ln(P_ABC/P_CBA) is nonzero in shared-goal weeks, with the circulation running from older to newer projects. Dwell times are geometric with a rate that falls with habit.
  - *Check:* transitions between projects per agent in H93's choice table; cycle affinities with a time-reversal null.
  - *Kill:* cycle affinities within the reversal null.
  - *Impostors:* project age is a drift field by construction; that is the claimed mechanism, so the test is whether the circulation exceeds what age-ordering alone gives in a synthetic walker.
  - *Models:* 02, 10, 15 · *Builds on:* H93, H94, H56, HH56

## Question
When an agent leaves one project for another, are the hops balanced, as for a walker on a fixed landscape of project attractiveness? Or do they carry a net circulation A → B → C → A? And is any such circulation more than the drift from older to newer projects that births create by themselves?

## Design: two layers (STANDARDS §4)
- **Replication** (role `replication`), both channels (work primary, attention second): G30, G31, G33, G35, G36, G37, G38, G39, G40, G41, G42, G44 (whole period) and the #51 units 51a–51l (non-holdout). Unit of analysis: the period unit of `period_units` for #51; the whole goal period elsewhere (hops are too few per sub-unit). #51 is pooled over units by DerSimonian–Laird random effects next to the per-unit values (exception (d)).
- **Natives** (role `native`):
  - **N1 · G35 (fixed set).** "Test your game": a few repos of one inherited game, almost no births. The fixed-attractiveness case: no age drift and no circulation expected.
  - **N2 · G38 (births throughout).** Seventeen days, the most repos and births of any shared week: the strongest age drift. The test of whether circulation exceeds age-ordering.
  - **N3 · G44 rooms.** #best (assigned team, named leader) vs #rest (free), same days: does an assigned field turn hops into a one-way flow (excess) while free choice keeps cycles?
- **Confirmation:** held-out shared-goal weeks #45–#47 and #50 (planned; see Confirmatory design). Not run.

## Model
**From:** `physics-models/10-potts/` (kinetic Potts: softmax choice), `physics-models/02-nonequilibrium-ising/` (detailed balance and its breaking), `physics-models/15-stochastic-thermodynamics-selection/` (item 2: housekeeping needs a cycle; excess is net occupancy change).

**H129 variant: a sticky Potts walker with births.** Each agent i is a walker on the set of projects available at time t (born, not yet ended).
- **Sticky dwell:** per own call, the agent leaves its project with probability r. Dwell is geometric with mean 1/r calls. In a softmax walker with habit field b, r falls as b rises.
- **Hop:** the agent picks project j ≠ current with P(j) ∝ exp(α_j(t) + b [i held j before] + βJ s_j).
- **Fixed attractiveness** (α_j constant, no births or deaths, no memory): the walker is a reversible Markov chain. Every cycle affinity A_cyc = ln(P_ab P_bc P_ca / P_ac P_cb P_ba) is 0 (Kolmogorov), and pair flows balance in steady state.
- **Age drift** (births at real times; newer projects available later, possibly more attractive): flows run from older to newer projects. The path ratio of a potential (gradient) walker is set by its end points: ln P(abc)/P(cba) = φ_c − φ_a. So age-monotone triples are asymmetric, yet the sum over the three rotations of a triangle cancels. That drift is excess, not housekeeping.
- **Cycle current (HH370):** a cyclic force adds κ to hops along a rotation a → b → c → a. The rotation-summed triple log ratio equals 2A_cyc ≠ 0. That is housekeeping, and it survives any potential.

**Identity used (Markov chain, stationary):** P(abc)P(bca)P(cab) / [P(cba)P(acb)P(bac)] = exp(2A_cyc). For a non-stationary gradient walker it holds approximately. The real-skeleton age walker sizes the residual.

## Data scheme (`scheme/build.py`)
- **Work channel (primary):** `replicator_hosts` host replay per goal period on non-holdout days (W = 30, E = 100). An agent's label sequence within a unit is collapsed to its runs of distinct labels. A **project hop** is a change between consecutive distinct labels of one agent, whether through a direct departure or through an expiry followed by a later arrival (variant: direct departures only). Hop time is the arrival time.
- **Attention channel:** `project_states` (W = 30, sources all, raw `project`, non-holdout rows). Per agent and unit, consecutive labelled windows with different projects (gaps allowed; variant: gap ≤ 4 windows).
- **Project age rank:** the time of the project's first appearance in the channel's non-holdout record over all periods (first agent work commit for work; first labelled window for attention). Ties broken by hashed name. Older = earlier.
- **Dwell (own calls):** for each visit (a run of one label), the number of the agent's own calls (`call_windows`) from its arrival to its hop. A visit ended by expiry, roster leave or the unit's end is right-censored at that point.
- **Output:** `data/processed/H129-project-cycle-currents/G<NN>/hops_<channel>.parquet` (unit, agent, t, from, to: hashed; age ranks), `visits_<channel>.parquet` (agent, project hash, arrival, dwell_calls, censored), `avail_<channel>.parquet` (project availability windows for the walker), `results.json`; `synthetic/`, `results/`, `_provenance.json`. Expected < 20 MB.
- **Regimes covered:** I (#30, #31), II (#33, #35, #36), III (#37–#44, #51a–l). Holdout masked by `replicator_hosts.period_days` and the `holdout` column of `project_states`.

## Observables
Triples are consecutive hop pairs (a → b, b → c) of one agent within a unit with a, b, c all distinct. Label the three projects of a triple by age: o (oldest), m, n (newest).
- **O1 · Age-signed triple affinity A_3 (HH-literal, primary for the kill):** A_3 = ln[(N(omn) + ½)/(N(nmo) + ½)]: agent paths that run old → middle → new against the reverse.
- **O2 · Triple cycle affinity 𝒜_cyc (primary for "beyond age"):** 𝒜_cyc = L_1 + L_2 + L_3 with L_1 = A_3, L_2 = ln[(N(m n o) + ½)/(N(o n m) + ½)], L_3 = ln[(N(n o m) + ½)/(N(m o n) + ½)]: the three rotations of o → m → n → o against their reverses. The counts sum over all triples of the unit. Positive 𝒜_cyc = a net rotation old → middle → new → old. ≈ 0 for any potential walker.
- **O3 · Net age flux m_2** = (n_up − n_down)/(n_up + n_down) over hops, up = to a newer project. The excess (gradient) part.
- **O4 · Hodge curl magnitude C_2:** on the unit's pooled hop graph (edges with n_ab + n_ba ≥ 1), F_ab = n_ab − n_ba; φ = argmin Σ_edges (F_ab − (φ_b − φ_a))²; C_2 = ‖F − ∇φ‖² (the net flow no potential explains), and the cycle share κ_c = C_2/‖F‖².
- **O5 · Dwell shape:** discrete-time hazard of a hop by own-call dwell d, logit h(d) = a + γ ln d on visits (censoring respected); γ = 0 is geometric, γ < 0 is aging. Plus the CV of completed dwells and the hop rate r = hops per 100 own calls per agent.
- **O6 · Hop rate vs habit:** across units, Spearman ρ between the unit's hop rate r and H93's work-channel habit b_own (M4 `prev` coefficient) where H93 identified it.

## Null / baseline
- **Time-reversal null (the HH's kill):** reverse each agent's whole hop sequence in a unit with probability ½ (per-agent block flips, as H76 found per-step surrogates biased), recompute A_3, 𝒜_cyc and m_2; 2,000 draws; one-sided p.
- **Detailed-balance null (C_2):** each pair's n_ab + n_ba hops split Binomial(½); 2,000 draws.
- **Age-ordering reference walker (the HH's impostor bar):** the sticky walker W1* on the unit's real skeleton (real agents, real hop times, real project availability windows, real first labels), choices ∝ exp(α_j + b·held + λ z_j(t)) with z_j the standardized age rank among available projects (newer larger). λ is calibrated so that the walker's mean m_2 matches the observed m_2; then 400 runs give the reference distribution of 𝒜_cyc, A_3 and C_2. "Beyond age-ordering" means above the reference's 95th percentile.

## Impostors (STANDARDS §1)
| Impostor | Relevant? | How it is handled | Status |
| --- | --- | --- | --- |
| Scheduler field | partly | Hops are ordered label changes, not activity bins; nights do not create hops (labels carry over; expiry runs on the own-call clock). Dwell is counted in own calls, not wall time. | removed |
| Exogenous field (kickoff, goal, operator) | yes | Project age is a drift field by construction (HH). It is removed by (i) 𝒜_cyc, which cancels any potential, and (ii) the age walker calibrated to the unit's net age flux. Kickoff and assignment fields act as potentials (one-way flow into a target) and enter the same way; N3 tests an assigned field. | removed for potentials; partly for time-varying fields |
| Shared model priors | partly | A shared genre order of work (build → test → document) would make every agent run the same cycle of project types. Projects here are repos, not types, so a shared cycle needs the same repos; reported: lab mix of the hops carrying the top triples. | partly |
| Contemporaneous convergence | n/a | The statistic is within-agent sequence order, not co-movement between agents. | n/a |

## Synthetic validation (axis F; before any real-data statistic)
`analysis/synthetic.py`, on the real skeleton of G31, G38, G41, G44 and 51c (work channel) and G38 (attention). Worlds (200 runs each):
- **W0 fixed, Markov:** all projects available throughout, α_j ~ N(0, 1), no habit. Reversible.
- **W0h fixed with habit:** W0 plus b = 2 for previously held projects (a non-Markov memory).
- **W1 age, no recency:** real availability windows, α_j ~ N(0, 1), habit b = 2, λ = 0.
- **W2 age, recency:** W1 with λ = 1.5 (newer favored).
- **W3 cycle κ = 1 and W3s κ = 2:** W1 plus a bonus κ for hops to the successor of the current project in a fixed age-oriented rotation (o → m → n → o over consecutive age ranks, wrapping within each window of three adjacent ranks).
For each world: the size of the reversal-null tests (A_3, 𝒜_cyc), of the DB null (C_2), and of the "beyond age" decision against the recalibrated walker W1*; and the power of each in W3/W3s.
**Decision rule fixed now:** a statistic counts as a test of a cycle current beyond age-ordering if its false-positive rate against W1* is ≤ 0.10 in W0h, W1 and W2 and its power at κ = 2 is ≥ 0.5 on at least the G38 skeleton. A_3 against the reversal null is scored as written (it is the HH's kill test), but it is read as "irreversible", not "circulating", unless 𝒜_cyc passes.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** (R1) reversible walker on a fixed landscape (W0); (R2) age-drift walker (a potential set by project age; W1*/W2): irreversible but no circulation; (R3) habit-memory walker (W0h): returns to held projects create apparent loops.
**Locked holdout used for confirmation:** #45, #46, #47, #50 (planned; see Confirmatory design).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Hops from the shared host replay (work) and project labels (attention); age = first non-holdout appearance. Attention labels are mentions, not work; work hops are few (2–120 per period outside #51). |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | The sticky walker assumes geometric dwell; real hazards age in 32/39 unit-channels. Habit memory makes the walker non-Markov; W1* includes it (b̂ calibrated to the return share). |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | The age walker calibrated to (m_2, return share) reproduces 𝒜_cyc in 9/9 shared unit-channels; no cycle force is needed. No day-blocked held-out likelihood. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | The circulation signature is absent (0/9). The dwell shape, unfitted by the triple statistics, contradicts the geometric prediction. |
| E interventional | predicts the change across a natural experiment | 0 | No NE design; the G44 room contrast is a same-days comparison with too few #best hops. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | 𝒜_cyc + W1* valid on 5/6 skeletons (false positives ≤ 0.075; power 0.55–0.97 at κ = 2, 0.07–0.57 at κ = 1); calibration recovers (λ, b). A_3 is confounded by drift (rejects in 0.38–0.95 of no-cycle recency runs); C_2 not identified. |
| G ground truth | agrees with known structure | 1 | The fixed-set week (G35) shows no irreversibility (untestable); the assigned #44 #best room's hop graph is a tree (all gradient). |
| H comparative | beats the named rivals | 1 | R2 (age-drift walker) fits; R1 (reversible) loses only on the sign of m_2 (30/37 positive); R3 (habit memory) is inside W1*. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Holdout not run. |

## Prediction
*Written 2026-10-04 22:16–22:19 UTC, before running any H129 statistic on real data.*

**What I had seen when writing this:** the cards of H93, H94, H56, H76, H77, H78 and H72 and their headline numbers (H93: habit 2.5–6 nats, choice events per period 48–1,477 work and 57–4,089 attention, repos 2–133; H78: 66% of recruitments are returns; H72: idle-gate escape hazards age). H93's G38 results file (its structure, to locate b_own; I saw its M0/M1 share coefficients for 38a). No hop sequence, triple count, flux or dwell had been computed.

**Shared-goal code (fixed now):** shared-goal weeks are those whose goal gives the agents one common objective: #30, #31, #33, #35, #36, #37, #38, #40, #41, #44 (both rooms). Own-role weeks: #39 (own world), #42 (own channel), #51 (private goals).

**Testability rule (fixed now):** a unit-channel is testable for O1/O2 if it has ≥ 20 age-ordered triples (N(omn) + N(nmo) ≥ 10 and all six rotation counts sum ≥ 20), and for O4 if it has ≥ 30 hops among ≥ 4 projects with cycle rank ≥ 2. Dwell (O5) needs ≥ 30 visits with ≥ 15 completed.

| ID | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| P1 (HH, kill test) | A_3 > 0 with one-sided reversal-null p < 0.05 in ≥ 2/3 of testable shared-goal unit-channels | p ≥ 0.05 in > 1/3 (HH370's kill: within the reversal null) | 0.45 |
| P2 (HH, beyond age) | 𝒜_cyc > 0, above the reversal null (p < 0.05) and above W1*'s 95th percentile, in ≥ 1/2 of testable shared-goal unit-channels | 𝒜_cyc inside W1*'s band in > 1/2 | 0.15 |
| P3 (Kolmogorov) | C_2 above both the DB null and W1*'s 95th percentile in ≥ 1/2 of testable shared-goal units (work) | inside either band in > 1/2 | 0.15 |
| P4 (excess) | m_2 > 0 (net flow to newer projects) with reversal-null p < 0.05 in ≥ 2/3 of testable units, both channels | m_2 ≤ 0 or null-compatible in > 1/3 | 0.65 |
| P5a (geometric dwell) | the dwell hazard slope γ has a 95% CI containing 0 in ≥ 2/3 of testable unit-channels | γ < 0 (aging) with CI < 0 in > 1/3 | 0.30 |
| P5b (habit) | hop rate falls with H93's b_own across units: Spearman ρ < 0 (work) | ρ ≥ 0 | 0.55 |
| P6 (own-role contrast) | own-role units have smaller |𝒜_cyc| and lower hop rates than shared-goal units (median comparison) | the reverse | 0.50 |
| Kill (HH370) | A_3 and 𝒜_cyc within the reversal null in > 1/3 of testable shared-goal unit-channels (P1 fails), or 𝒜_cyc never exceeds W1* | — | P(kill as circulation) 0.8 |

**Natives (role `native`; predictions per folder).**
- **N1 G35:** A_3, 𝒜_cyc and m_2 inside the reversal null; C_2 inside the DB null (or untestable for lack of cycles). Credence 0.7.
- **N2 G38:** m_2 > 0 (reversal p < 0.05); 𝒜_cyc inside W1*'s band. Credence 0.5.
- **N3 G44:** #best's hops are dominated by the excess (m_2 or flow into the assigned repo, κ_c below #rest's); #rest has the higher κ_c. Credence 0.4.

**My expectation, stated before data.** Births make hops irreversible by construction (P4). A genuine rotation needs agents to return to older projects in a cyclic order. Habit returns (66% of recruitments) may create apparent loops, which is why W0h is in the synthetic. I expect HH370's circulation to fail against the age walker.

Per-period predictions are in each `goalperiod-subhypotheses/G<NN>/README.md`, written before that period is run.

### Amendment A1 (2026-10-04 23:10 UTC, after the synthetic validation, before any H129 statistic on real data)
*What I had seen:* the synthetic summaries (`data/processed/H129-project-cycle-currents/synthetic/summary.json`; 40 synthetic datasets per world on 6 skeletons: G31, G38, G41, G44, 51c work and G38 attention) and the skeleton sizes (59–265 hops, 21–74 projects per skeleton). No real A_3, 𝒜_cyc, m_2, C_2 or dwell statistic.
1. **𝒜_cyc against both the reversal null and W1* is a valid circulation test on 5 of 6 skeletons.** False-positive rate ≤ 0.075 in W0h, W1 and W2; power at κ = 2: 0.55 (51c), 0.57 (G44), 0.62 (G31), 0.80 (G41), 0.93 (G38 work), 0.97 (G38 attention). At κ = 1 power is 0.07–0.57. The G41 skeleton fails the false-positive bar (0.125 in the habit world W0h); G41's 𝒜_cyc verdict carries that flag. A null 𝒜_cyc is a powered negative (≥ 0.8) only for strong cycles (κ = 2) on G38 and G41-sized units; elsewhere it is "inconclusive" for weak cycles.
2. **The calibration recovers the walker's parameters:** in W2 (λ = 1.5, b = 2) the median calibrated (λ̂, b̂) is (1.5, 2) on every skeleton.
3. **A_3 against the reversal null measures age drift, not circulation.** It rejects in 0.38–0.95 of runs of the recency walker W2, which has no cycle. P1 is scored as written (HH370's kill test), and a pass is read as "irreversible", as the card already says.
4. **C_2 is not identified.** The detailed-balance binomial null rejects in 0.10–0.82 of runs of the reversible fixed-landscape world W0: walkers start on real initial projects, so finite-time flows are not balanced. Against W1*, C_2 has power ≤ 0.45 at κ = 2 on 5/6 skeletons (0.75 on G38 attention). P3 is reported, scored "not identified" except on unit-channels with ≥ 150 hops (the G38-attention size).
5. **m_2's reversal null is slightly liberal** (rejects 0.10–0.20 in W0); P4 is scored as written with this caveat.
Not amended: the periods, roles, testability rule, P1/P2/P4–P6 thresholds, the kill, credences.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | descriptive | work 2 repos (no triples); attention < 10 age-monotone triples |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | mixed | A_3 work 1.13 (p 0.002), attention 0.50 (p 0.007); 𝒜_cyc inside W1* (p 0.26, 0.45); m_2 0.17 / 0.10 |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | descriptive | 24 / 32 hops; too few triples |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication + native N1 | descriptive | 2 work hops, 15 attention hops; all inside their nulls |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | failed | attention A_3 0.50 (p 0.085); 𝒜_cyc −0.67 |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | failed | attention A_3 1.05 (p 0.18) |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication + native N2 | failed | A_3 0.66 (p 0.10); m_2 0.17 (p 0.027); 𝒜_cyc inside W1* (N2 holds) |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | descriptive | own-role; 8 work hops |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | descriptive | 15 / 50 hops; < 10 monotone triples |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | failed | attention A_3 0.21 (p 0.44); work untestable (G41 skeleton flagged, A1) |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | descriptive | own-role; 14 work hops |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication + native N3 | failed | work A_3 1.10 (p 0.07); attention 1.17 (p 0.006); 𝒜_cyc inside W1*; #best hop graph a tree |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication (units 51a–l) | descriptive | own-role; pooled attention 𝒜_cyc 0.16 [−0.32, 0.64]; 2/14 own-role tests pass both nulls (≈ chance) |

## Results
### Exploratory round 1 (2026-10-04; non-holdout only)
- **Code:** `analysis/h129lib.py` (hops, ages, triple affinities, Hodge split, nulls, sticky walker, calibration), `analysis/synthetic.py`, `scheme/build.py`, `analysis/run.py`, `analysis/figures.py`, `analysis/confirm.py` (frozen, dry-run only).
- **Data:** `data/processed/H129-project-cycle-currents/` (`G<NN>/hops_*.parquet`, `visits_*.parquet` hashed with age ranks; `synthetic/`; `results/`; `confirm_dryrun/`; `_provenance.json`; < 5 MB).
- **Figures:** [`figures/summary_obs.pdf`](figures/summary_obs.pdf) (A_3 and 𝒜_cyc per testable unit-channel with bootstrap CIs, reversal-null significance and W1*'s 95th percentile), [`figures/summary_synth.pdf`](figures/summary_synth.pdf) (rejection rates by synthetic world).
- **Estimates:** 245 rows in `per_period_estimates` (`h129_age_triple_affinity_A3`, `h129_triple_cycle_affinity_Acyc`, `h129_net_age_flux_m2`, `h129_hodge_cycle_share`, `h129_dwell_hazard_slope`).

**Outcome vs prediction**

| Prediction | Outcome | Verdict |
| --- | --- | --- |
| P1 A_3 > 0 beyond the reversal null in ≥ 2/3 of shared unit-channels | 3/9 | failed: HH370's kill met |
| P2 𝒜_cyc beyond the reversal null and W1* in ≥ 1/2 | 0/9 (power 0.55–0.97 at κ = 2) | failed |
| P3 C_2 beyond the DB null and W1* in ≥ 1/2 | 0/5 work units; not identified (A1) | not identified |
| P4 m_2 > 0 with reversal p < 0.05 in ≥ 2/3 | 8/34; sign positive in 30/37 (post hoc, p 0.0002) | failed as written |
| P5a geometric dwell (γ CI ∋ 0) in ≥ 2/3 | 6/39; γ < 0 (aging) in 32/39 | failed |
| P5b hop rate falls with H93's habit | ρ −0.29 (p 0.53, 7 periods) | holds by sign, not significant |
| P6 own-role units smaller |𝒜_cyc| and hop rate | |𝒜_cyc| 1.16 vs 0.53 (2 vs 3 work units); rate 0.11 vs 0.12 per 100 calls | failed |
| N1 G35 inside the nulls | inside, but untestable | descriptive |
| N2 G38 m_2 > 0, 𝒜_cyc inside W1* | work: m_2 0.17 (p 0.027), 𝒜_cyc p 0.27 | supported (work) |
| N3 G44 #best κ_c < #rest | work 0.00 vs 0.51; attention 0.81 vs 0.83 | mixed (few #best hops) |

**Synthesis.**
1. *Hops are mildly irreversible through age, not through cycles.* Agents move to newer projects slightly more than back (m_2 0.03–0.21, positive in 30/37), which is the excess a stream of births creates. The rotation-summed cycle affinity, which cancels any potential, never beats a walker with an age bias and habit calibrated to each unit.
2. *HH370's literal test (A_3 against the reversal null) mostly fails* (6/9 inside), and where it passes (G31, G44 attention) the calibrated age walker explains it.
3. *Dwell is not geometric.* The longer an agent has stayed on a project, the less likely it is to leave in the next call or window (γ < 0 in 32/39). That is the trap aging H72 found in idle gates, now in project choice. The sticky Potts walker's memoryless dwell is wrong.
4. *Thermodynamic reading.* Project hopping is excess (net occupancy change toward new projects), not housekeeping. No cycle current over projects is detectable at these counts.

**Claim that stands.** Agents' project hops carry no circulation beyond age drift: the rotation-summed triple cycle affinity exceeds a calibrated age walker in 0/9 shared-goal unit-channels (synthetic power 0.55–0.97 for a 2-nat cycle). Net flow to newer projects is small but consistent (m_2 > 0 in 30/37, 0.03–0.21), and dwell hazards age rather than stay geometric (γ < 0 in 32/39). *Excluded:* the Hodge curl (not identified), the habit correlation P5b (n.s.), the #51 attention hits (2/14, multiple testing), the m_2 sign test (post hoc, A2).

### Confirmatory design (frozen 2026-10-04 in `analysis/confirm.py`; dry-run on stand-ins only, NOT RUN)
Targets: shared-goal held-out weeks #45, #46, #47 (from titles), both channels; #50 (own-role from the title) reported. C1: 𝒜_cyc beyond both nulls in ≤ 1 testable target unit-channel. C2: m_2 > 0 in ≥ 2/3. C3: dwell slope γ < 0 with CI < 0 in ≥ 2/3. C0: A_3 inside the reversal null in ≥ 1/2. Dry run (stand-ins #31, #38, #44; own-role #42): C0–C3 pass; a pipeline check, not evidence. Guards: `--confirm` plus `H129_CONFIRM=1`, sha256 freeze of `h129lib.py`, `run.py`, `confirm.py`; `holdout_ledger.check()` (families `entropy_production`, `project_potts`). Disclosure: H93/H75/H77/H78/H94/H95 plan #45–#47 project statistics; H95 read #47 setup lines.

## Round 2 redirects (proposed by the round-1 agent, 2026-10-04)
- **H129-R1. Aging dwell as a model.** Fit a renewal walker with a decreasing hazard (Weibull or power-law trap) and test whether the aging exponent tracks habit (H93 b_own) or H72's gate aging.
- **H129-R2. Pool cycle tests across #51's private-goal units on the work channel** once more units pass the triple floor (only 2/12 now); use the 12 attention units as a replica test of the two hits (51c, 51l).
- **H129-R3. Excess bound.** Report the minimum excess EP of the net age flow per hop (Kolchinsky 2026 dual) and compare with H75's re-allocation Σ_ex,min.

## Notes
- 2026-10-04 22:16 UTC: round-1 agent (H129 together with H128). Card written before any H129 statistic. Compute: ≤ 2 threads, one heavy job at a time; no LLM labels.
- 2026-10-04 23:10 UTC: Amendment A1 after the synthetic (before real data). 23:12–23:15 UTC: real run, estimates, figures. 23:16 UTC: confirm.py frozen and dry-run (guards tested: refuses without the freeze and without H129_CONFIRM=1).
