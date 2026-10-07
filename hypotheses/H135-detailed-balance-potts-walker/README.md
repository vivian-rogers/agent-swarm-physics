# H135: Max-ent allocation as the steady state of a detailed-balance Potts walker: hop-rate ratios from max-ent occupancies

**Status:** round 1 in progress (2026-10-07): scheme built and cross-checked, structural counts and synthetic validation done, Amendment A1 written before any real-data outcome. Pre-registered 2026-10-07 from HH378 (approved by Vivian 2026-10-07).
**Question (GOALS.md):** **Q6** (thermodynamics and selection: is the project walk reversible, so that its steady state is the max-ent allocation?). Second: **Q2** (field vs coupling: are hop rates set by a static field, the max-ent prices, or by a flux toward crowded projects?).
**Fields:** stochastic thermodynamics (detailed balance, pair flux, Kolmogorov criterion), stat mech (kinetic Potts walker, heat-bath and Metropolis rates), info theory (max-ent allocation)
**Literature:** [Kolchinsky, Dechant, Yoshimura & Ito 2026](../../literature/kolchinsky-2026-generalized-free-energy-excess-housekeeping.md) (excess vs housekeeping; a reversible walker has neither cycle currents nor a net pair flux at steady state); [Aguilera, Ito & Kolchinsky 2026](../../literature/aguilera-2026-entropy-production-nonequilibrium-maxent.md) (EP as statistical irreversibility). Cited from memory (†): Kelly, *Reversibility and Stochastic Networks* (1979)† (detailed balance, Kolmogorov's criterion); Jaynes, *Phys. Rev.* 106, 620 (1957)† (max-ent).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime; **Agent state (categorical, project, work ledger)** (H11 round 1b) as carried by **Host (work ledger, call-clock expiry)** (H77, H78; W = 30, E = 100); **Agent state (categorical, project/artifact strict)** (H11; attention channel); **Entropy production / irreversibility**; **Birth** (H77, H78). From H129 (proposed there): **project hop (H129)**, **project age rank (H129)**, **net age flux m_2 (H129)**, **dwell (own calls, H129)**. From H94 (proposed there): **work quantum (H94)**, **owner (H94)**, **ownership price λ_own (H94)**. New named variants proposed for DEFINITIONS.md (not edited there; defined under Data scheme and Observables): **max-ent occupancy π (H94 model, per unit and per agent)**, **max-ent occupancy π (attention variant)**, **co-alive pair**, **pair hop rate k_ab (own-call clock)**, **net max-ent flux m_π**, **heat-bath destination slope ψ**.
**From:** HH378 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/10-potts/` (kinetic Potts walker; the max-ent model of categorical marginals), `physics-models/15-stochastic-thermodynamics-selection/` (detailed balance, pair flux, excess vs housekeeping)

## Source HH (verbatim from the HH list)
- **HH378 · Max-ent allocation is the steady state of a detailed-balance Potts walker: predict hop rates from occupancies.** H94 found allocation is max-ent given activity, sizes, ownership and rooms, and H129 found no cycle currents. Together these say the project walk is a reversible kinetic Potts process. Detailed balance then fixes the ratio of the two hop rates between any pair of projects.
  - *Prediction:* for each pair (a, b), k_ab / k_ba = π_b / π_a, where π is the H94 max-ent marginal. This ratio is not fitted from the hops. It holds within ×1.5 for most pairs.
  - *Check:* H94 marginals; H129 hop counts per pair per period.
  - *Kill:* the log rate ratio and the log occupancy ratio are uncorrelated, or their slope is outside [0.5, 2].
  - *Impostors:* project birth and death create one-way hops. Restrict to pairs where both projects live through the window.
  - *Models:* 10, 15 · *Builds on:* H94, H129, H93

## What this card builds on (latest round of each cited card)
- **H94 (round 1, 2026-10-04):** work episodes are allocated at maximum entropy given agent activity, repo sizes, ownership and rooms. The residual is ≤ 0.13 of I(agent; repo) in 23/24 units (0.23 in #36c), and inside the persistence floor's 95% band in 12/24. The ownership price λ_own has median 2.2 nats in shared weeks and 7.8 in own-role units (Mann–Whitney p = 0.0007). Repo-episode concentration κ ≥ 1 in 7/7 shared units. At NE42 (G40) λ_own falls from ≥ 20 to 12.9, κ rises 0.16 → 3.61, and a named hub takes 73%.
- **H129 (round 1, 2026-10-04):** the rotation-summed triple cycle affinity exceeds a calibrated age walker in 0/9 shared unit-channels (synthetic power 0.55–0.97 for a 2-nat cycle). Net flow to newer projects is small but consistent (m_2 > 0 in 30/37 unit-channels, 0.03–0.21; a post hoc sign test). The Hodge curl is not identified. Dwell hazards age (γ < 0 in 32/39). Work hops number 2–120 per period outside #51; the synthetic skeletons had 59–265 hops over 21–74 projects. In G44 the assigned #best room's hop graph is a tree.
- **H93 (round 1, 2026-10-04):** habit is the dominant field in project choice (b_own ≈ 2.5–6 nats). The share coefficient βĴ is +2 to +6 in shared weeks and −6 to −12 in own-role weeks, but fast repo bursts give the same values, so J is not identified. Every period sits below the Brock–Durlauf multiplicity boundary.
- **H11 (round 2, 2026-10-05):** joins follow a sublinear, time-symmetric co-arrival kernel (lag − lead ≈ 0); a project's output grows as n^0.70 with the agents on it.

**Two facts fixed before data.**
1. A reversible walker gives k_ab / k_ba = π_b / π_a with π its own stationary occupancy. Write k_ab = n_ab / T_a, with T_a the own calls spent on a. Then ln(k_ab / k_ba) = ln(n_ab / n_ba) + ln(T_b / T_a). H94's max-ent marginals reproduce the observed repo sizes by construction (M1 matches the column sums). So the HH's slope is near 1 whenever the observed occupancy T tracks the quanta occupancy, whatever the walk does. The physics is in the first term: the **pair flux** n_ab − n_ba. Detailed balance means zero net flux on every pair at steady state.
2. A single agent's trajectory has, at every project, entries minus exits in {−1, 0, +1}. A net pair flux therefore comes from cycles (H129: none detected) or from paths between start and end states (births, ends, drift). The co-alive restriction removes most path terms.

## Question
Between two projects that both live through the window, do agents hop as often from a to b as from b to a (zero net flux)? And are the rates' ratio and the destination of each hop set by the max-ent occupancies of H94, as in a reversible heat-bath Potts walker?

**Practical payoff:** if the walk is reversible, the max-ent prices (ownership, rooms) are the whole control: an operator who moves a price moves the steady allocation, and the walk has no hidden flux toward crowded projects that would need a separate brake.

## Model
**From:** `physics-models/10-potts/` (kinetic Potts walker) and `physics-models/15-stochastic-thermodynamics-selection/` (detailed balance, excess vs housekeeping).

**H135 variant: a reversible kinetic Potts walker with H94's max-ent field.** Agent i walks on the unit's available projects. Its field on project j is h_i(j) = ln π_i(j), where π_i(j) = P_K(j | i) is the agent-conditional of H94's max-ent model (M2: activity, repo sizes, ownership; M3 adds rooms in two-room units). At each own call the agent leaves with probability r_i(a, d) (dwell d allowed, as H129 found aging) and picks a destination.
- **Heat-bath (Glauber) destination law:** P(dest = b | leave a) = π_i(b) / (1 − π_i(a)). The rates obey detailed balance with stationary π_i, and the destination does not depend on the origin.
- **Metropolis variant:** k_ab ∝ min(1, π_i(b)/π_i(a)). Also reversible; different rates; the same ratio.
- **H135 says:** among co-alive pairs, the net flux is zero (m_π = 0, m_2 = 0), the rate ratio follows the max-ent ratio, and the destination follows π_i (heat-bath).

**Rivals.**
- **R-age drift (strongest rival; H129's calibrated age walker):** agents favor newer projects among the available ones. Flux runs old → new even between co-alive projects (m_2 > 0). Irreversible excess, no cycles.
- **R-sink (herding; H11, H93, H94 κ ≥ 1):** hops run into crowded projects faster than out (m_π > 0), a one-way flux that a static field cannot give.
- **R-habit (H93):** returns to previously held projects dominate destinations beyond π_i (habit coefficient > 0, origin-dependent destinations).
- **R-cycle (H129's W3):** a cyclic force; already rejected at κ = 2 by H129.

## Data scheme (`scheme/`)
`scheme/build.py` writes `data/processed/H135-detailed-balance-potts-walker/` from shared tables only. Hops are rebuilt with H129's rules through the shared builders; π is refitted with H94's rules. No code is imported from either card's folder (STANDARDS §8); the H94 max-ent fit (IPF on margins and feature partitions) is a candidate for `infra/shared/` if a third card needs it.
- **Inputs:** DQ4 `work_commits` through `infra/shared/replicator_hosts.py` (host replay, W = 30, E = 100; agent-work filter `canonical & ~imported & author_kind == agent & ~automated`); `project_states` (W = 30, sources all, raw `project`; attention channel); `call_windows` (own-call clock); `rooms_timeline`, `calendar`, `period_units`, `roster`; `ground_truth_labels` (`room_assignment`, #44); `infra/shared/kickoff_naming.py` (named flags). Read-only cross-checks: H129 `G<NN>/hops_*.parquet` and H94 `G<NN>/quanta.parquet` (the rebuilt tables must match them; mismatches are reported).
- **Hops (work, primary for π fidelity; attention, secondary for counts):** H129's project hop: a change between consecutive distinct labels of one agent; hop time = arrival time.
- **Occupancy time T^i_a:** agent i's own calls (`call_windows`) carrying label a, until a hop, expiry, leave or the unit's end.
- **Max-ent occupancy π (proposed variant):** per unit, H94's M2 (M3 in two-room units) fitted by IPF on the unit's work quanta. Unit marginal π(j) = Σ_i P_K(i, j); agent conditional π_i(j) = P_K(j | i). **Attention variant:** the same fit on attention quanta (agent × project × 30-min window from `project_states`), with H94's owner where the project is a DQ4 repo and the agent with the earliest strict mention otherwise.
- **Cross-fit variant:** π from odd active days, hops and T from even days, and the reverse.
- **Co-alive pair (proposed variant):** projects a and b both available (first label ≤ the unit's first active day + 1 active hour, last label ≥ the unit's last active day − 1 active hour) through the unit. Variant: both alive for ≥ 80% of the unit's active hours.
- **Output:** `G<NN>/hops_<channel>.parquet` (unit, agent, t, from, to: hashed; co-alive flag), `G<NN>/occupancy_<channel>.parquet` (agent, project hash, T, π_i, π), `results/`, `synthetic/`, `_provenance.json`. Expected < 20 MB.
- **Regimes covered:** I (#30, #31), II (#33, #35, #36a), III (#36b–#44, #51a–l), as in H94 and H129. Reserved rows are dropped with the shared reserved-row mask in `infra/shared/common.py` and the `project_states` reserved flag.

**Structural precondition (counted before any outcome):** a unit-channel is testable if it has ≥ 60 hops among co-alive pairs and ≥ 8 co-alive pairs with n_ab + n_ba ≥ 4. Only counts are printed.

## Observables
- **O1 · HH-literal rate test:** over co-alive pairs with n_ab + n_ba ≥ 4, the Deming slope and the Pearson r of ln(k_ab / k_ba) (pseudo-count ½ on n) on ln(π_b / π_a) (unit marginal), with pair-bootstrap CIs (1,000 draws). Also the share of pairs with n_ab ≥ 3 and n_ba ≥ 3 whose ratio lies within ×1.5 of π_b / π_a. Reported with the decomposition into ln(n_ab / n_ba) and ln(T_b / T_a).
- **O2 · Net max-ent flux m_π (primary for detailed balance):** m_π = Σ_pairs (n_ab − n_ba) · sign(ln π_b − ln π_a) / Σ_pairs (n_ab + n_ba), over co-alive pairs, oriented so that positive means toward the higher-π project. Also the conditional-binomial fit n_ab | N_ab ~ Bin(N_ab, q_ab), logit q_ab = θ + β_π ln(π_b / π_a): detailed balance gives θ = 0 and β_π = 0.
- **O3 · Co-alive age flux m_2^co:** H129's m_2 restricted to co-alive pairs. Detailed balance gives 0.
- **O4 · Heat-bath destination slope ψ:** conditional logit over destinations b ≠ a of each hop: u_b = ψ ln π_i(b) + ρ [i held b before] + ω_ab (an origin × destination interaction tested by likelihood ratio). Heat-bath gives ψ = 1, ρ = 0 and no interaction.
- **O5 · Per-agent ownership check (descriptive):** for hops between an agent's owned repo and others, the observed rate ratio against e^{λ_own} times the size ratio.

## Null / baseline
- **N1 · Pair-flip null for O2 and O3:** each co-alive pair's N_ab hops split Binomial(½), 2,000 draws. Because finite walks start on real initial projects, this null is liberal (H129 A1: its binomial detailed-balance null rejected in 0.10–0.82 of reversible runs). It is reported, and the synthetic W0 band is the decision null.
- **N2 · Reversible-walker band (decision null):** the distribution of O1–O4 in W0 and W0M (below) on the unit's real skeleton.
- **Strongest rival:** R-age drift, calibrated to the unit's observed m_2 as H129's W1*.

## Impostors (STANDARDS §1)
| Impostor | Relevant? | How it is handled | Status |
| --- | --- | --- | --- |
| Scheduler field | partly | Rates are per own call (H129's dwell clock), not per wall hour. Nights add no calls and no hops. | planned (removed) |
| Exogenous field (kickoff, goal, operator) | yes | A kickoff is a potential: it makes flux into the named repo at the start (excess). Co-alive pairs exclude repos born at the kickoff; a variant drops the first 4 active hours after each kickoff. Ownership and rooms are fields inside π (H94). | planned (partly) |
| Shared model priors | partly | A shared genre order of work (build → test → document) would give the same flux in every agent. Projects are repos, not types; the lab mix of the hops on the pairs with the largest |n_ab − n_ba| is reported. | planned (partly) |
| Contemporaneous convergence | n/a | The statistics are within-agent hop orders and pair counts, not co-movement between agents. | n/a |
| (HH impostor) Birth and death | yes | Co-alive pairs only; H129's age walker as the rival band; the cross-fit variant for drift in π. | planned |
| (card impostor) Counting identity | yes | O1's slope is near 1 when T tracks π, whatever the flux (fact 1). The synthetic sizes this before data; O2 carries the detailed-balance claim. | planned |

## Design: two layers (STANDARDS §4)
**Unit of analysis:** one goal period, split at `period_units`; #51 units 51a–51l separately. Per-unit statistics are phase-diagram points. A random-effects mean of m_π and β_π across testable unit-channels is reported next to the per-unit values (exception (d): few hops per unit). No complete pooling.
- **Replication (role `replication`):** every non-reserved unit-channel in H94's and H129's sets that meets the precondition: G30, G31, G33, G35, G36, G37, G38, G39, G40, G41, G42, G44, 51a–51l; work and attention channels.
- **Natives (role `native`):**
  - **N1 · G38 (17 days; births throughout).** The most co-alive pairs among long-lived repos, and H129's strongest age drift (work m_2 0.17, p 0.027). The test of detailed balance once births are cut away.
  - **N2 · G44 rooms (same days).** #best works to an assigned target (H129: hop graph a tree; H94: λ_own 10.2) and #rest chooses freely (λ_own 4.1). An assigned field gives a one-way flux (m_π > 0) in #best; free choice keeps detailed balance in #rest.
  - **N3 · G40 (NE42 merge; a herding sink).** A named hub took 73% of work (H94). On the first two active days the flux into the hub should be one-way (R-sink); after the hub fills, the co-alive pairs should balance.
- **Reserved (confirmation only; never read in exploration):** #45, #46, #47, #50 and the #51 tail (2026-09-07 → 09-21), which are H94's and H129's confirmation targets, and #43, #48, #49. A frozen `analysis/confirm.py` (m_π CI ∋ 0 among co-alive pairs; ψ) is written after round 1 and runs only with Vivian's sign-off. Families `project_potts`, `entropy_production`, `artifact_lineage`; disclose reuse with H93, H94, H129, H77/H78 and H75.

## Synthetic validation plan (axis F; run before any real-data statistic)
`analysis/synthetic.py` on the real skeletons of G31, G38, G41, G44 and 51c (work) and G38 (attention): real agents, call clocks, project availability windows and first labels; π from the unit's own H94 fit. 200 runs per world.
- **W0 heat-bath:** reversible walker with stationary π_i; dwell aging as observed (γ = −0.3).
- **W0M Metropolis:** reversible, different rates.
- **W1 age drift:** H129's W2 (recency λ = 1.5, habit b = 2).
- **W2 sink:** destinations ∝ current share^1.5 (H94's beyond-neutral herding world S3).
- **W3 cycle:** H129's W3s (κ = 2).
- **W4 habit:** H129's W0h (b = 2 on previously held projects).
- **Read:** the O1 pass rate (slope in [0.5, 2] with r > 0) in every world; the size of O2 and O3 in W0 and W0M; their power in W1, W2 and W3; ψ recovery in W0 (1) and its value in W0M and W4.
- **Pass rules:** O1 counts as a detailed-balance test only if it passes in ≥ 0.8 of W0 runs and in ≤ 0.2 of W1–W3 runs. O2 and O3 count where their size in W0 and W0M is ≤ 0.10 and their power in W1 or W2 is ≥ 0.8. A statistic that fails is descriptive, by a dated amendment written before any real-data statistic. **Declared now:** I expect O1 to fail its pass rule (fact 1), so O2 is the primary test.

## Prediction
*Written 2026-10-07, before any H135 statistic on real data. What I had seen: the cards of H94, H129, H93 and H11 at their latest rounds (numbers above). No co-alive pair, pair count, rate ratio or flux had been computed.*

| ID | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| S1 | O1 fails its synthetic pass rule: it passes in > 0.2 of irreversible-world runs (W1–W3) | O1 discriminates (≤ 0.2) | 0.7 |
| P1 (HH) | **Rate ratios follow π.** O1 slope in [0.5, 2] with r > 0 (p < 0.05) in ≥ 2/3 of testable unit-channels | slope outside [0.5, 2] or r CI ∋ 0 in > 1/3 | 0.75 |
| P1b (HH) | Within ×1.5 for most pairs: ≥ 1/2 of the pairs with ≥ 3 hops each way | < 1/3 | 0.4 |
| P2 | **Zero net flux (detailed balance).** m_π inside the W0 band in ≥ 2/3 of testable unit-channels, and the random-effects mean CI ∋ 0 | mean CI excludes 0 | 0.4 |
| P3 | **No age flux between co-alive projects.** m_2^co inside the W0 band in ≥ 2/3 of testable unit-channels | m_2^co > 0 beyond the W0 band in > 1/3 (R-age drift) | 0.4 |
| P4 | **Heat-bath destinations.** ψ CI ∋ 1, ρ CI ∋ 0 and no origin × destination interaction (LR p ≥ 0.05) in ≥ 1/2 of testable unit-channels | ρ > 0 with CI > 0 (H93 habit) in > 1/2 | 0.2 |
| N1 | G38: m_π and m_2^co inside the W0 band (both channels) | either beyond the band | 0.35 |
| N2 | G44: #best m_π > 0 beyond its W0 band; #rest inside its band | #best inside, or #rest beyond | 0.35 |
| N3 | G40: flux into the hub on the first two active days is beyond the W0 band (one-way); co-alive pairs on later days are inside | no excess flux into the hub | 0.5 |

**Kill rules (from the HH, sharpened).**
- **Kill A (HH):** in ≥ 1/2 of testable unit-channels, ln(k_ab / k_ba) and ln(π_b / π_a) are uncorrelated (r CI ∋ 0) or the slope lies outside [0.5, 2]. This is scored as written. If S1 holds, a pass of Kill A's test is read as "consistent", not as support.
- **Kill B (detailed balance):** the random-effects mean of m_π (or of m_2^co) has a CI excluding 0 and lies beyond the W0 band. The walk then carries a net flux, and the max-ent allocation is not the steady state of a reversible walker.

**Verdict rule.** *Supported:* P2 and P3 hold, and P1 holds (P1 alone never supports if S1 holds). *Narrowed ("reversible on co-alive pairs; destinations not heat-bath"):* P2 and P3 hold, P4 fails. *Failed:* Kill A or Kill B fires. *Inconclusive:* < 3 testable unit-channels, or O2 unpowered (power < 0.8 against W1 and W2).

**My credence before data:** supported 0.15; narrowed 0.2; failed 0.35; inconclusive 0.3. The main reasons for doubt: H129's age drift (m_2 > 0 in 30/37) and H94's concentration above neutral (κ ≥ 1 in 7/7 shared units) both point to a net flux. Few co-alive pairs carry enough hops.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R-age drift (H129 calibrated age walker), R-sink (herding flux; H11, H93, H94), R-habit (H93), R-cycle (H129 W3).
**Reserved periods used for confirmation:** none yet. Planned: #45, #46, #47, #50 and the #51 tail (frozen after round 1; not run).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 0 | not run |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 0 | not run |
| C adequacy | beats the null hierarchy, day-blocked out-of-sample data | 0 | not run |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | not run |
| E interventional | predicts the change across a natural experiment | 0 | not run |
| F identifiability | synthetic recovery with village sampling; survives preprocessing variants | 0 | not run |
| G ground truth | agrees with known structure | 0 | not run |
| H comparative | beats the named rivals | 0 | not run |
| I transfer | holds in other same-mode periods, including the reserved periods | 0 | not run |

## Results by goal period
No period has been run. Period folders (`goalperiod-subhypotheses/G<NN>/`) are created with their dated predictions before each run. `goalperiod-subhypotheses/GNN/` is the unfilled template.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| replication unit-channels (precondition list) | replication | pending | not run |
| G38 | native N1 | pending | not run |
| G44 | native N2 | pending | not run |
| G40 | native N3 | pending | not run |

## Results
## Round 1 (2026-10-07)

### R1.0 Build, cross-check and structural counts (before any outcome)
- **Code:** `scheme/build.py` (hops, occupancy T, π, availability, co-alive flags, age ranks), `analysis/h135lib.py` (statistics, nulls, walker), `analysis/synthetic.py`, `analysis/run.py`.
- **Data:** `data/processed/H135-detailed-balance-potts-walker/` (7 MB; names hashed).
- **Cross-check (read-only):** the rebuilt hops equal H129's files in every period and both channels (same multisets of agent, origin, destination; whole-period units outside #51). The rebuilt work quanta equal H94's in every period. **Owner deviation:** I take the owner from non-reserved commits only (the reserved-row rule). H94 used all DQ4 rows. The owner differs for 37 repos (G31 11, G33 1, G35 1, G37 1, G38 18, G51 5).
- **Implementation choices fixed before any outcome:**
  1. Units are the `period_units` units, as the card says (H129 used whole periods outside #51).
  2. O1 enters each pair in both orientations, so the Deming slope (δ = 1) and r are fitted through the origin. y = ln[(n_ab + ½)/(n_ba + ½)] + ln(T_b/T_a). Pass = slope in [0.5, 2], r > 0 and p < 0.05 (t test, k − 1 df; pair bootstrap CIs on real data).
  3. O2's binomial fit orients each pair from the older to the newer project. θ is then the age flux and β_π the max-ent flux, fitted together.
  4. O4's choice set is every project available at the hop time except the origin. ln π_i is clipped at −15 (capped λ_own cells). ρ = destination held before by the agent in the unit. ω has one parameter per ordered pair with ≥ 3 hops; the LR test has that many degrees of freedom.
  5. The W0 band is the 2.5–97.5% range of 200 W0 runs on the unit's skeleton. **Kill B** fires if the DerSimonian–Laird mean of m_π (or m_2^co) has a CI excluding 0 **and** the same mean of the W0-centred value (observed − W0 median) has a CI excluding 0. Per-unit SEs come from a 1,000-draw pair bootstrap.
  6. Occupancy T: work = own calls inside each host visit; attention = own calls inside the agent's 30-min windows labelled with the project.
- **Structural precondition (counts only; per-period tables in the G folders):**
  - **Primary co-alive rule: 0 of 62 unit-channels pass.** The largest co-alive hop counts are 86 (51g attention, 6 pairs ≥ 4) and 73 (30b attention, 1 pair). By the card's verdict rule (< 3 testable unit-channels), **H135 is inconclusive on its primary definition.** This is declared before any outcome.
  - **Card's 80% co-alive variant: 5 unit-channels pass**, all #51 attention: 51a, 51c, 51f, 51g, 51h (105–406 co-alive hops, 10–27 pairs ≥ 4). The work channel passes nowhere (best: 51g 118 hops but 7 pairs). The variant is run as the card defines it. Its result is scoped to own-role #51 attention units.
  - **Natives:** N1 (G38) and N2 (G44) are untestable under both rules. N3's first part (hub flux on days 1–2, G40) does not use co-alive pairs and is run; its later-day part is untestable (co-alive hops 7 work, 5 attention).
  - **Disclosure (N3):** while counting G40 hub hops, I printed the in/out split before the W0 band existed (days 1–2: work 5/5, attention 12/11). N3's result is marked "seen before the band".

### R1.1 Synthetic validation (axis F; before any real-data outcome)
*Run 2026-10-07 (`analysis/synthetic.py`, `analysis/synth_summary.py`; summary in `data/processed/H135-detailed-balance-potts-walker/synthetic/summary.json`).* Thirteen real skeletons: the card's six (31a, 38a, 41, 44a, 51c work; 38a attention), the five variant-testable units (51a, 51c, 51f, 51g, 51h attention) and G40 (both channels, for N3). Real agents, own-call clocks, availability windows and first labels; π from each unit's own fit. 200 runs per world. All worlds share the field ln π_i; W1–W4 add their force on top (W1: age z, λ 1.5, habit 2; W2: sink, (occupants + 1)^1.5; W3: cycle κ 2, habit 2; W4: habit 2). Dwell hazard logistic(c + γ ln d), γ = −0.3, c calibrated per world to the unit's hop count. "Beyond the band" = outside the 2.5–97.5% range of W0 runs 0–99; the size in W0 is read on runs 100–199.

**Variant rule (80% co-alive), the five testable skeletons:**

| Statistic | W0 | W0M | W1 age | W2 sink | W3 cycle | W4 habit | Pass rule |
| --- | --- | --- | --- | --- | --- | --- | --- |
| O1 pass rate | 0.31–0.99 | — | 0.00–0.61 | 0.01–0.40 | 0.47–1.00 | — | ≥ 0.8 in W0 and ≤ 0.2 in W1–W3: **fails on 5/5** |
| m_π beyond the W0 band | 0.03–0.09 | 0.06–0.18 | 0.01–0.12 | 0.01–0.13 | 0.00–0.10 | — | size ≤ 0.10, power ≥ 0.8: **fails on 5/5** (power ≤ 0.13) |
| m_2^co beyond the W0 band | 0.02–0.07 | 0.08–0.15 | 0.04–0.29 | 0.01–0.07 | 0.04–0.44 | — | **fails on 5/5** (power ≤ 0.29) |
| pair-flip null N1, rejection | 0.00 | — | — | — | — | — | conservative, not liberal |
| ψ (mean ± sd) | 1.00 ± 0.03–0.08 | 0.39–0.47 | 0.50–0.70 | — | — | 1.00–1.02 | W0 CI coverage of 1: 0.92–1.00 |
| ρ (mean) | −0.02 to 0.02 | 0.09–0.17 | 1.9–3.2 | — | — | 1.93–2.01 | recovers the planted 0 and 2 |
| LR interaction, χ² p < 0.05 | **0.76–1.00** (100 runs) | — | — | — | — | — | invalid as χ² |

**Card's six skeletons, primary rule:** co-alive hops per run are 0–41 (38a work 0; 41 work 1.3; 44a work 2.7; 51c work 12.5; 31a work 24.6; 38a attention 40.9). O1 passes in ≤ 0.34 of W0 runs, and O2 and O3 have no power. This matches the structural count: the primary test cannot be run.

**N3 (G40):** the W0 band of the day-1–2 hub flux is [0.20, 1.00] (work) and [−0.02, 0.29] (attention). The sink world W2 exceeds the upper edge in 0/200 runs on both channels. In the always-hop worlds the hub flux is lower than in W0, because a heat-bath update can keep an agent on the hub.

**What the synthetic shows.**
1. **O1 is a near-identity (S1 holds in synthetic).** It passes in up to 1.00 of cycle-world runs (W3 on 51g) and 0.61 of age-world runs (51c). The occupancy term ln(T_b/T_a) carries the slope, as fact 1 said.
2. **Zero net flux cannot tell the card's rivals from W0.** A fixed age preference among co-alive projects is one more static field. Destinations drawn ∝ w(b) among b ≠ a, with a state-independent leave hazard, give an embedded jump chain with ν(a) ∝ w(a)(W − w(a)), and ν(a)P(a→b) ∝ w(a)w(b) is symmetric. A symmetric occupancy (herding) term is a reversible Potts coupling. So W1 and W2 carry almost no flux between co-alive projects; only the cycle force W3 does (m_2^co power 0.04–0.44). Fact 2 adds a bound: one agent's net flow through a project is −1, 0 or +1, so the pair flux grows with agents, not hops. H129's m_2 > 0 must come from births, which the co-alive rule removes.
3. **O4 is the one valid test.** ψ and ρ are recovered without bias, and they separate heat-bath (ψ 1, ρ 0) from Metropolis (ψ ≈ 0.4), habit (ρ ≈ 2) and age drift (ψ 0.5–0.7, ρ 2–3).
4. **The LR interaction test is invalid with a χ² reference.** I gave ω a parameter for each ordered pair with ≥ 3 hops; that choice uses the outcome and inflates the statistic.

### Amendment A1 (2026-10-07, after the synthetic, before any real-data outcome)
*What I had seen:* the synthetic summaries above and the structural counts. No real m_π, m_2^co, slope, ψ or LR value.
1. **O1 is descriptive.** It fails its pass rule on every testable skeleton. Kill A is scored as written; a pass reads "consistent", never support.
2. **O2 and O3 are descriptive; H135's primary test is unpowered.** Power against W1 and W2 is ≤ 0.29 on every testable skeleton (rule: ≥ 0.8). By the card's verdict rule ("O2 unpowered"), **H135 is inconclusive in round 1 whatever the data show.** m_π and m_2^co are still reported against the W0 band, and Kill B is scored as written. Kill B cannot fire on a null-only band with this power, and a non-firing Kill B is not evidence of detailed balance.
3. **O4's LR test is recalibrated:** the observed χ² p is ranked among the χ² p values of 100 W0 runs on the same skeleton (`synthetic/lrnull_<unit>_attention.parquet`); calibrated p = (1 + #W0 runs with p ≤ observed)/(101). P4 becomes: ψ CI ∋ 1, ρ CI ∋ 0 and calibrated LR p ≥ 0.05, in ≥ 1/2 of testable unit-channels. **O4 (with P4) is the only test that can decide anything in round 1.**
4. **N3 is unpowered** (W2 exceeds the W0 band in 0/200 runs) and is reported descriptively.
5. Not amended: units, co-alive rules, precondition, thresholds, credences, the verdict rule.

## Notes
- 2026-10-07: card written from HH378 (approved by Vivian 2026-10-07). Round-1 order: rebuild hops and π, check against H129 and H94 files → structural counts → period READMEs with dated predictions → synthetic → dated amendments → replication and natives → estimates rows (`h135_rate_ratio_slope`, `h135_net_maxent_flux`, `h135_coalive_age_flux`, `h135_heatbath_psi`) → frozen `confirm.py` (dry run only).
- The HH's "π_b / π_a not fitted from the hops" is true: π comes from work quanta. But H94's marginals equal the observed repo sizes, so the HH's ratio test shares the occupancy term with the rates (fact 1). This is stated before data.
- Compute: ≤ 2 threads, one heavy job at a time (STANDARDS §9).
