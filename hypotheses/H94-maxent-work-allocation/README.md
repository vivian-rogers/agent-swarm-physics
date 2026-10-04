# H94: Work allocation as a max-entropy equilibrium

**Status:** exploratory round 1 done (2026-10-04, non-holdout only). **Supported in a refined form: work episodes are allocated at maximum entropy given agent activity, repo sizes, ownership and rooms.** In 24 testable units (#31–#51), the information left after those constraints, above the run-persistence floor, is ≤ 0.13 of I(agent; repo) in 23 units (0.23 in #36c) and within the floor's 95% band in 12. Ownership is the decisive constraint and acts as a goal-set price: λ_own median 2.2 nats in shared weeks vs 7.8 in own-role units (Mann–Whitney p = 0.0007); it carries 0.79–1.00 of the 2.7–4.1 bits per quantum in own-role units and 0.14–0.43 in shared weeks (0.97 in #40, where a hub sits beside own worlds). In two shared weeks (#31a, #33) plain max-ent with margins already sits at the floor. Agents do not specialize beyond ownership (breadth at the null in 23/24). Repo-episode concentration κ is ≥ 1 in all 7 shared units, but kickoff-named repos explain it in only 2 of 6, and in own-role units κ tracks agent activity, not herding. The NE42 merge (G40) moves the price and the concentration as predicted. `analysis/confirm.py` is frozen and dry-run, not run. Card and predictions written 2026-10-04 before any real-data statistic; amendments A1 (pre-data) and A2 (post hoc) below. Approved by Vivian in the dashboard vetting panel 2026-10-04 from HH285.
**Fields:** stat mech (maximum entropy, Bose–Einstein vs Maxwell–Boltzmann counting), info theory (KL divergence, constraint hierarchies), econophysics (Foley's statistical equilibrium)
**Literature:** no paper in `literature/` covers Foley or Jaynes directly. Classical background named, not filed (†): Jaynes, "Information theory and statistical mechanics", *Phys. Rev.* 106, 620 (1957)†; Foley, "A statistical equilibrium theory of markets", *J. Econ. Theory* 62, 321 (1994)†; Schneidman, Still, Berry & Bialek, "Network information and connected correlations", *PRL* 91, 238701 (2003)† (constraint hierarchies); Patefield, "An efficient method of generating random R × C tables with given row and column totals", *Appl. Stat.* 30, 91 (1981)†. Nearest filed note: [Piñero 2025, neutral cooperative dynamics](../../literature/pinero-2025-neutral-theory-cooperative-dynamics.md).
**Definitions used** (`physics-models/DEFINITIONS.md`): *Agent state (categorical, project, work ledger)* (H11 round 1b); *Entropy* (here of the allocation, not of behavior: named variant below); *Mutual information between agents* (here agent × repo); *Regime*; *Population N(t)*. New named variants proposed here (not edited into DEFINITIONS.md): **work quantum (H94)**, **owner (H94)**, **allocation KL D_k (H94)**, **ownership price λ_own (H94)**, **concentration index κ (H94)**, defined under Data scheme and Observables.
**From:** HH285 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` (econ-style free energy family) · **Models:** `physics-models/05-replicator-dissipation/` (repo sizes as replicator abundances; formation vs copying), `physics-models/10-potts/` (allocation as a categorical state; the generalized Potts model is the max-ent model of one- and two-point marginals)
**Sibling:** H93 (Brock–Durlauf choice) uses the same work ledger and ownership.
**Question served:** Q4 (where the swarm's information lives: bits of allocation structure beyond the constraints) and Q2 (field vs coupling: ownership and rooms are fields; herding is excess concentration).

## Source HH (verbatim from the HH list, including literature refinements)
Work allocation is a maximum-entropy statistical equilibrium. Given constraints (commits per agent, repo sizes, ownership), the observed allocation of agent work across repos should be the maximum-entropy distribution (Foley's statistical equilibrium). Deviations measure planning (lower entropy) or herding (excess concentration). A principled null for H06 and H11. *Check:* max-ent fit with constraints on DQ4 allocations; KL divergence per period; which constraint explains H06's private projects.
  *Models:* 05, 10 · *Builds on:* H06, H11, DQ4

## Question
Given how much each agent works, how big each repo is and who owns which repo, is the agent × repo allocation of work the least-structured (max-entropy) one? If not, how many bits per unit of work does the allocation carry beyond those constraints, and is the excess specialization (planning) or concentration (herding)?

## Model
**From:** `physics-models/10-potts/` (max-ent models of categorical marginals) and `physics-models/05-replicator-dissipation/` (repo abundances).

**Max-ent allocation hierarchy (Jaynes; Foley's statistical equilibrium).** Work quanta are distributed over agent × repo cells. With constraints f_k on the table, the max-ent distribution is the exponential family
P_K(i, j) ∝ exp(Σ_k λ_k f_k(i, j)),
fitted by matching the constraint expectations to the observed ones (iterative scaling; equals the Poisson log-linear MLE).
- **M0:** total only → uniform over the agent × repo cells.
- **M1 (HH285's constraints):** row sums r_i (quanta per agent) and column sums c_j (repo sizes) → independence, P_1(i, j) = r_i c_j / N².
- **M2:** + ownership: Σ own_ij n_ij, own_ij = 1 if i owns j → P_2 ∝ a_i b_j e^{λ_own own_ij}. λ_own is the **ownership price** (a chemical potential, in nats): the log-odds bonus of a quantum landing on its owner's repo.
- **M3:** + room: Σ room_ij n_ij, room_ij = 1 if agent i and j's owner share a room (two-room periods) → price λ_room.
- **Allocation KL D_k = KL(P̂ ‖ P_k)** in bits per quantum. D_1 = I(agent; repo). By the Pythagorean identity of exponential families, D_{k−1} − D_k = KL(P_k ‖ P_{k−1}) is the information carried by constraint k.

**Herding vs planning.** Max-ent at fixed margins can only be *less* structured than the data, so the sign of the deviation is read from two further statistics:
- **Concentration of the repo-size margin (κ).** With K repos and N quanta, Maxwell–Boltzmann counting (distinguishable quanta, independent uniform choices) gives max-ent shares near 1/K. Bose–Einstein counting (every size vector equally likely) gives a geometric size law; it is the stationary law of neutral Pólya copying (H06's Hubbell limit). κ = (H_MB − H_obs)/(H_MB − H_BE) with H the entropy of repo shares: κ ≈ 0 even (assigned or planned), κ ≈ 1 neutral copying, κ > 1 concentration beyond neutral (herding).
- **Unfitted cell signatures under M2:** agent breadth (distinct repos per agent) and repo reach (distinct agents per repo) predicted by multinomial sampling from P_2 at the observed r_i, vs observed. Breadth and reach both below prediction = specialization (planning-like); reach above prediction on the top repos = herding.

**What would make HH285 true:** after M2 (M3 in two-room periods) the residual D is near its finite-sample floor (≤ 20% of D_1, or ≤ 0.1 bit per quantum above the floor), and the unfitted signatures are inside their M2 prediction bands.

## Data scheme (`scheme/`)
`scheme/build.py` writes `data/processed/H94-maxent-work-allocation/G<NN>/` from shared tables only (repo names hashed; no text).
- **Inputs:** DQ4 `work_commits` (default agent-work filter: `canonical & ~imported & author_kind == agent & ~automated`; Claude Code agent excluded), all-time for ownership; `calendar`, `period_units`, `rooms_timeline`, `roster`; H54's naming rule via `infra/shared/replicator_hosts.kickoff_named` (text in memory only) for the named flag of each repo.
- **Work quantum (H94):** one (agent, 30-min window from the day's `win_start`, repo) with ≥ 1 agent work commit. Variants: raw commits; (agent, day, repo).
- **Owner (H94):** the agent with the earliest agent work commit to the repo in all of DQ4 (author time, default filter). Variant: earliest commit inside the period. A repo whose first agent work commit predates the period is "carried over".
- **Room:** the agent's room at the quantum's window midpoint (`rooms_timeline`, open rooms' null `t_end` filled with +∞); room_ij = 1 if agent i's modal room in the unit equals the owner's modal room.
- **Output:** `G<NN>/quanta.parquet` (unit, agent, day, win, repo hash, n_commits, owner, named, room), `G<NN>/tables_<unit>.npz` (agent × repo counts and indicator matrices), `results/G<NN>.json`, `_provenance.json`.
- **Regimes covered:** #30, #31 (I); #33, #35, #36a (II); #36b–#44, #51a–l (III). Holdout days and periods dropped with `holdout_mask`.
- **Unit of analysis:** goal period split at `period_units`. D_k, λ_own and κ are computed per unit; the period value is the quantum-weighted mean of units, reported next to the per-unit values (exception (d) does not apply: these are descriptive information quantities, not one model fitted to pooled data). Units with < 100 quanta, < 3 agents or < 3 repos are descriptive.

## Observables
1. D_0, D_1, D_2, D_3 (bits per quantum) and their floors (expected plug-in KL when the data are drawn from P_k itself at the same N: Patefield tables for M1, parametric multinomial bootstrap with refit for M2–M3; 200 draws).
2. The explained shares: ownership (D_1 − D_2)/D_1, room (D_2 − D_3)/D_1, residual D_3/D_1 (floor-corrected).
3. λ_own and λ_room (nats) with bootstrap CIs (agent-block bootstrap: resample agents with all their quanta; 200 draws).
4. κ with the BE and MB references at the unit's K and N (exact BE mean entropy by simulation; 500 draws each).
5. Signatures under M2: breadth ratio and reach ratio (observed / predicted), and the singleton-repo count (repos with one committer: H06's "private projects") observed vs predicted by M1 and by M2.

## Null / baseline
- **Max-ent itself is the null:** HH285 says the data are a draw from P_K. The floors give the KL a pure draw would show at the same N.
- **Quanta are clumped in time** (an agent works on one repo for hours). A draw from P_K has no clumping. A block null, re-sampling each agent's day as a block of quanta under P_K (a whole agent-day goes to one repo drawn from P_K(j | i)), gives a second, larger floor; it is reported as the "persistence floor". Residual D above the persistence floor cannot be blamed on within-day persistence alone.
- **Synthetic checks (axis F):** worlds with known structure on each unit's real (agent, window) skeleton: (S0) draws from P_1, (S1) draws from P_2 with λ_own = 3, (S2) neutral Pólya copying (agents join repos ∝ current size; BE), (S3) herding beyond neutral (∝ size^1.5), (S4) planned assignment (agents fixed to repos in teams). The estimator must return D ≈ floor in S0–S1, λ̂_own ≈ 3 in S1, κ ≈ 1 in S2, κ > 1 in S3 and κ < 0.5 in S4.

## Rivals and impostors
- **Rivals:** (R1) neutral copying (H06's Hubbell limit, BE counting: κ ≈ 1); (R2) herding on kickoff-named repos (H54: concentration set by the field); (R3) agent + own artifact (H58: ownership explains everything).

| Impostor | Relevant? | How it is handled | Status |
| --- | --- | --- | --- |
| Scheduler field | partly | Quanta are 30-min agent-windows with work, so agents' hours enter only through r_i (a constraint). No time-correlation statistic is claimed. | removed |
| Exogenous field (kickoff/goal/operator) | yes | Kickoff-named repos flagged; κ recomputed without named repos (κ falls below 1 in 2/6 shared units); room constraint M3 for room-specific kickoffs and assignments (#35 0.61, #38 0.12, #41 0.27 of D_1). Ownership is itself a goal-set field (λ_own tracks the goal type). | partly |
| Shared model priors | partly | A lab constraint (same-lab owner) is computed as a variant (M2b, `D2_lab`, `lam_lab` in the results); it is not part of the reported hierarchy. | partly |
| Contemporaneous convergence | no | No influence or copying claim; the hypothesis is about the static allocation. | n/a |

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** neutral copying (R1), field-made herding (R2), agent + own artifact (R3).
**Locked holdout used for confirmation:** #45, #46, #47, #50 and the #51 tail (51m); frozen in `analysis/confirm.py`, dry-run on stand-ins only, not run.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Quanta, owners, rooms and named flags are DQ4, rooms_timeline and H54 fields. Limits: "owner" = first agent work commit in DQ4 (pre-DQ4 history and private repos unseen); H54's token rule is noisy; a quantum is a 30-min window, so the commit variant weights bulk committers more. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Max-ent assumes exchangeable episodes within a unit; the run-preserving null keeps each agent-day's run structure (A1). Units split at step changes; within-unit stationarity is not tested. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Max-ent with margins + ownership (+ rooms) leaves ≤ 0.2 · D_1 above the persistence floor in 23/24 units and is inside the floor's 95% band in 12/24; #51 units keep 0.1–0.3 bit of significant structure. No held-out-day test. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | Unfitted signatures under M2 with runs kept: agent breadth at the null (0.72–1.23); singleton repos 54–95% recovered (M1: 15–45%) but within ±25% only in 9/24. |
| E interventional | predicts the change across a natural experiment | 1 | NE42 (#39 → #40): λ_own falls ≥ 7 nats, κ 0.16 → 3.61, a named hub takes 73% (all predicted). #35's room assignment appears as a room price (0.61 of D_1). #44's planned arm goes the other way (stronger ownership). |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | λ_own recovered (planted 3 → 3.1–3.3, CI coverage 0.80–1.00); the persistence floor holds a true max-ent world in 75–95% of runs; κ separates neutral, beyond-neutral and planned worlds on average but varies ±0.5 per unit. The Patefield floor is 0.2–1.2 bits too low (A1). |
| G ground truth | agrees with known structure | 2 | Own worlds (#39: λ_own at the cap), individual channels (#42), forks per room (#35: room price), the named hub (#40: 73%), private roles (#51: ownership 0.79–0.95) all match the known structure. |
| H comparative | beats the named rivals | 1 | Ownership (R3) is the decisive constraint, not a rival. Neutral copying (R1, BE) fits κ in 5/24 units; field-made herding (R2) explains κ in 2/6 shared units. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Holdout not run. The pattern holds across regimes I–III and 24 units. |

## Prediction
*Written 2026-10-04, before running the analysis on real data.*

**What I had seen when writing this:** the cards of H06, H11 (round 1b: in shared weeks 25–67% of work repos have one committer, yet 71–100% of work agent-windows go to repos with ≥ 2 committers; ownership index 0.00–0.29 in shared weeks, 0.73–1.00 in own-artifact weeks), H54, H58 (return to the own artifact), H77 and H78 (formation makes 76–100% of arrivals; 66% of recruitments are returns); per-period work-commit counts from the period-affordance catalog. No allocation table, KL, price or κ had been computed.

**Periods and roles.** Replication (`replication`): #30, #31, #33, #36, #37, #38, #39, #41, #42, #51 (units 51a–51l). Natives (`native`): **G35** (each room evolves its own fork: the room constraint should carry the allocation), **G44** (assigned #best vs self-chosen #rest on the same days: planned vs free arm), **G40** (NE42 merge: the same agents one week after #39 connect their own worlds into one universe; ownership price should fall and concentration rise).

**Own-artifact units** (fixed now, from H11's ownership index ≥ 0.5 and the goal text): #39, #42, #44, #51 units. **Shared units:** #30, #31, #33, #35, #36, #37, #38, #40, #41.

| ID | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| P1 | Plain max-ent fails: D_1 − floor_1 ≥ 0.5 bit per quantum in every testable unit | any testable unit with D_1 within 0.5 bit of its floor | 0.85 |
| P2 | Ownership explains private work: ownership share (D_1 − D_2)/D_1 ≥ 0.5 in ≥ 2/3 of own-artifact units, and < 0.5 in ≥ 2/3 of shared units | the reverse in either group | 0.55 |
| P3 (HH285's claim) | Statistical equilibrium given the constraints: residual D_2 (D_3 in two-room units) minus floor ≤ 0.2 · D_1 in ≥ 1/2 of testable units | residual > 0.2 · D_1 in > 1/2 | 0.30 |
| P4 | The ownership price is a field set by the goal: λ_own higher in own-artifact than in shared units (Mann–Whitney p < 0.05 over units) | p ≥ 0.05 or the reverse | 0.70 |
| P5 | Herding is excess concentration: κ ≥ 1 in ≥ 2/3 of shared units and κ < 1 in ≥ 2/3 of own-artifact units | the reverse in either group | 0.45 |
| P6 | Herding is field-made: dropping kickoff-named repos lowers κ below 1 in ≥ 1/2 of the shared units with κ ≥ 1 | κ stays ≥ 1 without named repos | 0.50 |
| P7 (H06's private projects) | M2 predicts the singleton-repo count within ±25% in ≥ 1/2 of testable units, and M1 misses it by more | M2 also misses by > 25% in most units | 0.40 |
| P8 (planning signature) | Agent breadth is below the M2 prediction (ratio < 0.8) in ≥ 2/3 of testable units: agents specialize beyond ownership | ratio ≥ 0.8 in > 1/3 | 0.65 |
| Kill (HH285) | Residual after all constraints > 0.5 · D_1 in every testable unit | — | P(kill) 0.35 |

Per-period predictions are in each `goalperiod-subhypotheses/G<NN>/README.md`, written before that period is run.

**Amendment A1 (2026-10-04, after the synthetic checks, before any real-data run).** What I had seen: the synthetic summary on units 31a, 39, 41 and 51d (20 runs per world, 50 null draws each). **Disclosure:** worlds S0 and S1 draw runs from max-ent tables fitted to the real margins, so their κ tracks the real repo-size margin: S0 κ on episodes was 1.64 (31a), 0.49 (39), 1.99 (41), 0.84 (51d). I saw these after the period predictions were written; the predictions stand as written.
- **Floors.** In S0, a true max-ent allocation of work episodes, D_1 sits 0.2–1.2 bits above the Patefield floor (0.78 vs 0.59 in 31a; 1.55 vs 0.36 in 39), because quanta come in runs. The run-preserving persistence floor matches it (D_1 inside the null's 95% in 75–95% of runs). **P1 and P3 are scored against the persistence floor**; the Patefield and parametric floors are reported only.
- **Prices.** λ_own is recovered: planted 3, estimates 3.1–3.3, agent-bootstrap CI coverage 0.80–1.00.
- **Concentration.** κ on episodes (runs per repo) is now primary; κ on quanta is a variant (clumped quanta inflate it). Neutral Pólya copying gives κ = 0.89–1.10 (unit 10–90% range ≈ 0.5–1.4), herding beyond neutral 1.76–2.91, planned teams ≈ 0. P5 is also scored by the BE band (κ above or below the 95% band of BE draws).
- **Breadth.** Under S0 the analytic breadth ratio is already 0.43–0.80: clumping reads as specialization. **P8 and P7 are scored against the run-preserving null** (breadth and singleton counts simulated with runs kept).
- Not amended: the hierarchy, the periods, the roles, the credences.

**Amendment A2 (2026-10-04, post hoc, after the first real run; disclosed).**
- **Solver.** The first run's alternating Newton solver did not converge for two-feature models (M3) in 6 units: D_3 came out above D_2, which is impossible for nested exponential families. The solver is now iterative proportional fitting on the margins and on each feature's partition, warm-started from the nested model; λ is read off log μ by least squares. M1 and M2 values are unchanged; M3 and the floors that refit M3 are from the new solver.
- **κ on distinct agents per repo** (each agent counts once per repo) is reported as a variant in the period READMEs, added after seeing κ ≫ 1 in own-role units, where repo sizes mirror agent activity.
- **Within-band count**: D_final ≤ the persistence floor's 95% quantile is reported next to P3's 0.2 · D_1 rule.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | descriptive | 2 repos per unit; D_1 0.19–0.27 bit |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | mixed | 31a: D_1 0.84 at the persistence floor 0.80; ownership 0.17; κ 1.81 → 0.88 without named repos |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | mixed | D_1 0.29 below the floor 0.36; κ 3.07 (not named-driven) |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | mixed | 36c: residual 0.23 · D_1 (the only unit above 0.2); room 0.00 |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | descriptive | 94 quanta; ownership 0.22 |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | mixed | 38a: room 0.12, ownership 0.22, residual 0.13; κ 4.08 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | supported | ownership 0.99, λ_own at the cap, κ 0.15 below BE |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | supported | ownership 0.43, room 0.27, residual 0.04; κ 1.78 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | mixed | ownership 0.93–1.00, λ_own 17; κ 0.82–1.00 (BE band) |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication | mixed | 12 units: ownership 0.79–0.95, residual 0.04–0.13 · D_1 but above the floor's 95% in 10; λ_own 5.5–18 (CV 0.47) |
| [G35](goalperiod-subhypotheses/G35/README.md) | native | mixed | room price carries 0.61 of D_1; residual 0.10; κ 1.35 (BE band) |
| [G44](goalperiod-subhypotheses/G44/README.md) | native | failed | planned #best arm: λ_own 10.2 > free #rest 4.1 (predicted reverse); top share 0.27 vs 0.10 |
| [G40](goalperiod-subhypotheses/G40/README.md) | native | supported | NE42 merge: λ_own ≥ 20 → 12.9, κ 0.16 → 3.61, named hub 73% |

## Results
*Exploratory round 1, 2026-10-04, non-holdout days only.*
- **Code:** `scheme/build.py` (work quanta, owners, rooms, named flags); `analysis/h94lib.py` (max-ent hierarchy by IPF, KL, Patefield / parametric / run-preserving floors, agent-block bootstrap, κ, signatures), `run.py` (per period; `--native g44|g40`), `synthetic.py` (S0–S4), `score.py` (P1–P8, estimates rows), `figures.py`, `confirm.py` (frozen, dry-run only).
- **Data:** `data/processed/H94-maxent-work-allocation/` (`G<NN>/quanta.parquet`, `results/`, `synthetic/`, `confirm_dryrun/`, `_provenance.json`; 0.5 MB).
- **Figures:** [`figures/summary_obs.pdf`](figures/summary_obs.pdf) (bits per quantum by constraint), [`figures/summary_kappa.pdf`](figures/summary_kappa.pdf) (κ vs the BE band).
- **Estimates:** 142 rows in `per_period_estimates` (`maxent_alloc_D1_bits`, `maxent_alloc_resid_bits`, `maxent_ownership_share`, `maxent_lambda_own_nats`, `maxent_kappa_concentration`).

**Outcome vs prediction** (24 testable units: 7 shared, 17 own-artifact)

| Prediction | Outcome | Verdict |
| --- | --- | --- |
| P1 D_1 − persistence floor ≥ 0.5 bit in every unit | 20/24; fails in #31a (0.04), #33 (−0.07), #36c (0.39), #38a (0.46) | failed |
| P2 ownership ≥ 0.5 in own units, < 0.5 in shared | 17/17 own; 6/7 shared (#40 0.97) | supported |
| P3 residual ≤ 0.2 · D_1 in ≥ 1/2 (HH285) | 23/24 (within the floor's 95% band: 12/24) | supported |
| P4 λ_own higher in own units | median 7.8 vs 2.2 nats, p = 0.0007 | supported |
| P5 κ ≥ 1 shared, < 1 own | 7/7 shared; 4/17 own | mixed |
| P6 named repos carry the concentration | κ < 1 without them in 2/6 (#31a, #40) | failed |
| P7 M2 predicts singleton repos ±25%, better than M1 | ±25% in 9/24; better than M1 in 24/24 | failed |
| P8 agents specialize beyond ownership (breadth < 0.8) | 1/24 (#35 0.72) | failed |
| Kill: residual > 0.5 · D_1 everywhere | 0/24 | not met |

**Synthesis.**
1. **Statistical equilibrium holds for work episodes.** Once each agent's activity, each repo's size, ownership and rooms are fixed, the allocation of work episodes carries ≤ 0.13 of its agent–repo information beyond what a max-ent draw with the same run structure gives, in 23 of 24 units. HH285's form is right; the unit is the episode, not the commit (A1).
2. **Ownership is a chemical potential set by the goal.** λ_own is 1.2–3.3 nats in shared weeks (12.9 in #40's hub-plus-own-worlds week) and 4.8–20 (several at the separation cap) in own-role units. In own-role units ownership alone removes 79–100% of 2.7–4.1 bits per quantum.
3. **No planning beyond ownership.** Agents touch as many repos as the max-ent null with runs predicts (breadth 0.72–1.23). The #44 planned team divides its task into owned repos; that is ownership, not extra structure.
4. **Herding is concentration of episodes, at or above neutral.** Shared weeks have κ ≥ 1 (1.35–4.08); 5 of 7 sit above the BE band (#31a, #33, #38a, #40, #41). Removing kickoff-named repos removes it only in #31a and #40. In own-role units κ ≫ 1 reflects unequal agent activity; on distinct agents per repo it falls inside the BE band in 9/12 #51 units.
5. **Private roles keep a little structure.** In 10 of 12 #51 units the residual (0.1–0.3 bit) exceeds the floor's 95% band. Rival or team pairs (DQ6) are the natural fourth constraint.

**Claim that stands.** Work episodes are allocated at maximum entropy given agent activity, repo sizes, ownership and rooms (residual ≤ 0.13 of I(agent; repo) in 23/24 units), and the ownership price is a goal-set field (median 2.2 nats in shared weeks, 7.8 in own-role units).

## Confirmatory design (frozen 2026-10-04 in `analysis/confirm.py`; dry-run on stand-ins only, NOT RUN)
Targets: all units of #45, #46, #47, #50 and the #51 tail (51m); #48, #49 reported, not scored. C1: residual above the persistence floor ≤ 0.2 · D_1 in ≥ 2/3 of testable target units. C2: #51-tail λ_own ≥ 4 nats with bootstrap 2.5% bound ≥ 2. C3: #51-tail ownership share ≥ 0.5. C4: breadth over the persistence null ≥ 0.8 in ≥ 2/3 of testable units. C5: M2 predicts singleton counts better than M1 in every testable unit. Dry run (stand-ins #38, #41, units 51h–51l; 7 testable units): C1–C5 pass, a pipeline check, not evidence. Guard: `--confirm --i-understand-this-uses-the-locked-holdout`, a committed H94 folder, `holdout_ledger.check()` (families `artifact_lineage`, `work_output`). Reuse: H11, H58, H77, H78 plan #45–#51-tail uses with work-commit statistics; disclose per the reuse policy.

## Round 2 redirects (proposed by the round-1 agent, 2026-10-04)
- **H94-R1. A herding index free of activity heterogeneity.** Max-ent for the agents-per-repo (reach) distribution at fixed agent breadth, with BE vs MB counting at the agent level.
- **H94-R2. Close the #51 residual.** Add DQ6 rival and opposed pairs and team roles as a fourth constraint; test whether the 0.1–0.3 bit gap closes.
- **H94-R3. The ownership price as a phase-diagram axis.** λ_own per day vs kickoff wording ("your own"), and against H93's per-choice habit field b_own (same physics at two scales).

## Notes
- 2026-10-04: round-1 agent (H94 together with H93). Card written before any allocation statistic; A1 after the synthetic, before the real run; A2 post hoc (disclosed).
- Compute: ≤ 2 threads, one heavy job at a time, no LLM labels. Floors and bootstraps use 200 draws per unit (50 in the synthetic).
