# H148: Autonomous agent discovery in #51: the systems that are individuals, found by search at every scale and nested

**Status:** round 1 done (2026-10-09): **failed** (P1 failed; P7 failed, so K1 fired) with P2 untestable and P3–P4 not identifiable. No system larger than one atom holds out of sample in #51 at 30 min. Card written 2026-10-09 from HH398 (Vivian: "any way you can develop your info dynamics framework to autonomously identify agents in the system?"). No H148 statistic has been computed. Uses H145's elements and the shared estimator `infra/shared/individuality.py` (H145 builds both and writes `scratchpad/H145_modules.READY` and `scratchpad/H145.READY`); until then it builds the search code and its synthetic validation.
**Fields:** info theory, complex systems, philosophy of individuality
**Literature:** [Krakauer et al. 2020](../../literature/krakauer-2020-information-theory-of-individuality.md) (boundary expansion); [Kolchinsky & Wolpert 2018](../../literature/kolchinsky-2018-semantic-information-autonomous-agency.md) (Sec. 6: agents as maximizers of semantic information over system–environment splits); [Schwitzgebel 2015](../../literature/schwitzgebel-2015-united-states-probably-conscious.md) (no anti-nesting principle); [Vivian's essay](../../literature/jazzloaf-2026-agent-ecologies-essay.md) (agent observatories; fingerprints of agent-like systems)
**Definitions used:** *egregore (ideology)* and *group superagent* (`physics-models/DEFINITIONS.md`); *Krakauer individuality*; *κ_c*; *environment E (impostor bundle)* as in H145.
**Question served:** Q3, Q4, `GOALS.md`. Paper 2. Siblings: H145 (memeplexes), H146, H147.

## Question
Without naming candidate groups or patterns in advance, which systems in #51 behave as individuals: their own state predicts their future beyond everything outside them, and that information has value for their persistence? At which scales (one agent, an agent with its files, a few agents, an ideology over changing agents, a room, the village), and how do they nest?

## Model
**From:** `physics-models/12-information-dynamics/` (Krakauer individuality and boundary expansion) and `physics-models/04-semantic-information/` (Kolchinsky–Wolpert value).

**Building blocks** (the atoms a system can contain), all from #51 07-06 → 09-04:
- agents (up to 32): state = the agent's touched project (`project_calls.proj`) and its content cluster per bin;
- artifacts: shared repos after cleaning (H145's rules) and each agent's own repos; state = written or not per bin, and by whom;
- elements: H145's meaning clusters and coinages; state = expressed or not, and by how many agents;
- rooms (#general, #focus): state = occupancy and talk volume.

**A system** X is a set of atoms; its state x is the tuple of its atoms' states, coarse-grained to ≤ 8 symbols by the system's own leading composition (first-half days) or, for 1-d content, a Gaussian variable. The environment is everything else plus E (H145's bundle: scheduler phase, operator and human input including relayed input, role-text and kickoff projections), lagged.

**Search (Krakauer's rule, greedy with a beam):** from every single-atom seed, add the atom ΔX that most increases colonial A = I(x′; x | E′) while decreasing nC = I(x′; E′ | x) (E′ = the environment without ΔX); keep the best 3 extensions per step (beam 3); stop when no addition both raises A's excess and lowers nC; cap 10 atoms. Every visited system is scored by its excess over size- and composition-matched random systems (same numbers of agents, artifacts and elements, matched in activity). A **discovered individual** is a local maximum: no single addition or removal raises its excess, its excess z ≥ 2, and it holds out of sample (search on odd active days, score on even days, and the reverse; both must agree).

**No exclusion postulate.** Nested individuals are all kept: an agent, the agent with its files, and an ideology that runs over that agent can all be individuals. The output is a nesting graph (system X contains system Y), not one best level.

**Semantic value (KW).** For each discovered individual, the natural scrambles that touch it (NE41 wipes of its agents; hub loss; operator actions; the #focus split) give ΔV for its persistence (V = the probability that its state stays in its own top symbol set the next active day) and κ = ΔV / I, as H147. A *discovered agent* is an individual with identified, positive κ for at least one scramble.

## Data scheme (`scheme/`)
- **Inputs:** H145's `elements.parquet` and `expr/`; `project_calls` (`proj`), `work_commits` (cleaned), `rooms_timeline`, `context_ledger_turns` (resets), `kicks_classified`, embeddings and goal vectors for E; `roster`.
- **Bins:** active 2-h bins (variants 30 min, 1 day), DQ8 trim.
- **Output:** `data/processed/H148-agent-discovery-51/` (`atoms.parquet`, `search/` (visited systems with scores), `individuals.json` (local maxima, members, nesting), `results/`, `synthetic/`, `_provenance.json`).
- **Span:** 07-06 → 09-04; 51m masked; frozen `analysis/confirm.py` (re-score the discovered individuals on the tail), dry-run only.
- **Efficiency (required):** incremental count updates when an atom is added; one set of tables per step for all candidate additions; null systems cached by composition and activity band with sequential stopping; seeds processed in one pass with shared caches; profile one seed first and record the cost.

## Observables
The list of discovered individuals with their atoms, scale (agent, agent + artifact, agents, memeplex, mixed), colonial A excess, nC, Δ (integration over parts), out-of-sample agreement, κ by scramble; the nesting graph; per agent, the smallest and the largest individual that contains it.

## Null / baseline
Size- and composition-matched random systems (primary); the search rerun on within-atom time-shuffled data (calibrates how many local maxima a search finds by chance); field-only skeletons (DQ8 `simulate.py`); role-text and operator-topic systems as the field control.

## Faithfulness scorecard
Scored per model, mapping and window; 0/1/2. Thresholds: `writeup/papers/thermodynamics/sections/method.tex`. Round 1 scores: see "Scorecard (round 1)" below.
**Rival models:** W_atoms (only single agents are individuals; nothing grows), W_field (the search grows systems along shared fields; they fail out of sample once E holds the fields), W_nested (planted nested individuals: an agent with its artifact inside a memeplex).
**Reserved data:** 51m.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | atoms and states from named tables; E as H145 | 1 | named tables and H145 elements; content dropped from the agent state (A3); no role-text projections in E |
| B assumptions | Markov order 1; split-half stationarity; bin sweep | 1 | odd/even split used; one width (30 min); day-level persistence sits in the single-atom null |
| C adequacy | local maxima beat matched random systems out of sample | 0 | rotated data give as many maxima (0.83, 0.96); 0 real maxima hold in both directions |
| D unfitted predictions | the nesting structure and the κ of discovered individuals are not used by the search | 0 | nothing discovered |
| E interventional | NE41, hub losses, operator actions, #focus (κ) | 0 | no candidate |
| F identifiability | planted nested individuals recovered on the real skeleton; false discoveries in W_atoms and W_field | 1 | size ≤ 0.10 per world; recovery 0.40 (ρ 0.7), 0.65 (ρ 0.9), memeplex 0/3 |
| G ground truth | each agent found; agent + own artifact found for most agents (H58); role texts not found | 0 | 1/27 agents; 0/25 own-repo systems (untestable) |
| H comparative | W_nested vs W_atoms vs W_field | 0 | real data distinguish none (no growth) |
| I transfer | 51m (not run) | 0 | confirm.py frozen, dry-run only |

## Prediction
*Written 2026-10-09, before running the analysis on real data.*

| | Card's prediction (operational) | Falsified if | My prior |
| --- | --- | --- | --- |
| **P1** agents are found | ≥ 90% of agents present ≥ 10 days are discovered individuals (as single atoms or with their own artifacts) | < 50% | 0.8 |
| **P2** agent + artifact | for ≥ 2/3 of agents with an own repo, the local maximum that contains the agent includes its own repo and stops there | the boundary closes at the bare agent for most agents | 0.65 |
| **P3** above the agents | ≥ 1 discovered individual with ≥ 3 agents' worth of atoms, out of sample | none | 0.4 |
| **P4** ideologies | ≥ 1 discovered individual is a memeplex (element atoms with changing host agents), nested over agents that are themselves individuals | none | 0.4 |
| **P5** fields are not found | no discovered individual is a role-text or operator-topic system | ≥ 1 is | 0.75 |
| **P6** discovered agents | at least one multi-agent or memeplex individual has identified κ > 0 under some scramble | none | 0.25 |
| **P7** calibration | the search on time-shuffled data finds ≤ 10% as many multi-atom local maxima as on real data | ≥ 50% | 0.6 |

**Kill rules.** (K1) If P7 fails (the search finds as many maxima in shuffled data), no discovery is read. (K2) If P5 fails, E is wrong; no discovery is read until a dated amendment fixes it. (K3) If the synthetic recovery of planted nested individuals is < 0.8, the verdict on P3–P4 is "not identifiable".

**Overall prior.** I expect the search to recover the agents and most agent + artifact pairs, the Echoes pair as the one multi-agent individual, perhaps one or two norm-like memeplexes, and nothing at the village level beyond the fields. The value of the card is the method: an agent observatory that runs on logs, in the sense of the essay's interventions.

**Synthetic validation (axis F), before real data.** On the real #51 skeleton: W_atoms (independent agents with own artifacts), W_field (agents and elements driven by shared role-text and time fields), W_nested (a planted pair that acts as one, inside a planted memeplex that recruits over changing hosts). 20 replicates. Report the recovery rate of planted individuals and their nesting, and the false-discovery count in W_atoms and W_field.

## Impostors
| Impostor | How handled | Status (planned) |
| --- | --- | --- |
| Scheduler field | e1 in E; trim; within-day transitions | removed |
| Exogenous field | e2–e3 in E; P5 as the control | removed if P5 holds |
| Shared model priors | lab and agent covariates in atom models; matched random systems keep agents' activity | partly |
| Contemporaneous convergence | E lagged; out-of-sample split | partly |

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G51](goalperiod-subhypotheses/G51/README.md) | exploratory | failed | P1 1/27 agents; 0 discoveries (agents, elements); P7 ratio 0.83 / 0.96 (K1) |
| 51m (reserved) | confirmatory | not run | |

## Results
See Round 1 below (2026-10-09). In short: no system larger than one atom holds out of sample in #51 at 30-min resolution; agents' self-information is day-level (1/27 pre-registered; 20/27 with a post hoc cross-day null); P2 untestable, P3–P4 not identifiable, K1 fired.

## Round 1 (2026-10-09)

Agent: H148 round-1 agent (resumed run). Data: #51 07-06 → 09-04 (45 non-reserved active days; 51m masked with `holdout_mask`; #45–#50 not read). Code: `scheme/build.py`, `analysis/h148lib.py`, `analysis/synthetic.py`, `analysis/synth_summary.py`, `analysis/run.py`, `analysis/elements.py`, `analysis/confirm.py` (frozen, dry-run only). Derived data: `data/processed/H148-agent-discovery-51/`.

### Inputs and atoms (built 2026-10-09)
- Bins: `memeplex.make_bins` (16:00 UTC anchor, 8 h per day, DQ8 per-agent presence), the same bins as H145's expression panels. 30-min bins: 720 bins, 16 per day; 345 / 330 within-day transitions on the odd / even days.
- Atoms (67 at the agent level): 32 panel agents (state: absent / present without a project touch / own top project / second project / other; `project_calls.proj` mapped with `memeplex.slug`), 33 artifacts (the own repos of 30 agents, 26 distinct repos (most-committed repo, ≥ 10 commits), and 15 shared repos (≥ 3 writers with ≥ 3 commits each), overlapping; state: not written / owner only / a non-owner; owner = top author), #general and #focus (none / low / high agent talk). Element atoms (A7): 80 H145 clusters + the 60 markers with the most events.
- Commits: `memeplex.clean_commits` at 4f6ab2e (48,093 → 44,349 kept; the mirror-loop repo dropped by name; Echoes chapter streams kept). The draft built before 4f6ab2e was rebuilt.
- E (lagged, source bin): phase (first / middle / last bin of the day) × exogenous input (none / automated operator only / human or relayed human input, from H145's `exo.parquet`) × rest-of-village presence above or below its day mean (the system's own agents removed) = 18 cells.

### Amendments (dated 2026-10-09, before any real-data outcome; reasons from the synthetic worlds on the real skeleton)
- **A1 Search score.** The card scores growth by colonial A's excess over size- and composition-matched random systems. On the skeleton this fails two ways. (i) A child inherits its parent's selected excess, so z rises with every greedy step: from every seed the search reached the cap of 10 atoms (one seed: z 1.8 → 13.2 over 9 additions, out-of-sample A falling). (ii) Joint colonial A misses coupling through a shared latent: two agents that track one latent carry less joint self-information than two independent agents (planted pair: A 0.50 vs null 0.41 bits, z 1.1; A* 0.55 vs 0.57). Replacement, Krakauer's boundary step in its nC form: the coupling of atom a to system X is τ(a, X) = T(a→X) + T(X→a), with T(a→X) = L(x′|x,E) − L(x′|x,a,E) = I(x′; a | x, E), the part of X's nC that a carries while it sits in the environment (held-out, leave-one-day-out, Dirichlet back-off as `individuality.krakauer_discrete`). Null: a's days permuted within blocks of 6 same-parity days (keeps a's within-day dynamics, phase alignment and alphabet use; breaks its same-day alignment with X). z from 40 draws (two stages: 8 draws for every candidate, 32 more when z ≥ 1). Add an atom when z ≥ 3; beam 3; cap 10. A terminal of ≥ 2 atoms is a local maximum when every member couples to the rest with z ≥ 2. It holds out of sample when, on the other half with the search half's codebook, the members' mean z ≥ 2 and every member's z ≥ 1. Single atoms: colonial A against within-(day, E) permutations of the source state (Besag–Clifford, h = 10, ≤ 300 draws), p ≤ 0.025 on both halves. The card's matched random systems stay as a secondary z for every discovered individual, and a partition contrast (each member vs every same-kind outside atom as partner of the same rest) is reported (STANDARDS 3).
- **A2 Agreement of the two directions.** "Both must agree" = a held local maximum of the odd-day search is matched by a held local maximum of the even-day search with Jaccard ≥ 0.5; the reported atoms are their intersection. Exact matches are counted too.
- **A3 Agent state.** The content cluster is dropped from the agent atom (5 × 80 symbols cannot be coded in 8). Content enters as element atoms.
- **A4 nC rule.** Built into τ (T(a→X) is the drop in X's nC when a moves from E into X); no separate nC condition. Reason: E holds no atoms here, so a literal "nC falls" test on growing joint codes measures estimator variance (H145_modules note).
- **A5 Trim and eligibility.** DQ8 presence trim on the system's agents; a candidate's absence is its state 0, so the real row and its null rows use the same transitions. An atom enters a half's search only with ≥ 20 bins outside its modal state and ≥ 4 span days there. Without these, real presence co-patterns and near-constant atoms gave null z up to 9 (P(z ≥ 3) = 0.012 per candidate); with them P(z ≥ 3) = 0.0017 (normal: 0.0013).
- **A6 Bin width.** 30-min bins are primary (card: 2-h; 2-h and 1-day are not run in round 1). Reason: 8-h days give 3 within-day transitions per day at 2 h (≈ 66 per half). On the 2-h skeleton the planted pair reached z ≥ 3 in 0/8 tests (30 min: 6/8), own links in 6% (30 min: 16%), and the null tail was heavier (P(z ≥ 3) = 0.0073 vs 0.0017).
- **A7 Element atoms and field classes** (`analysis/elements.py`, fixed before any element data were read for H148): 80 clusters + the 60 markers with most events (not chosen by H145's memeplexes); state 0 / 1 / ≥ 2 present agents expressing. Role-text elements = elements of H145's role patterns R0–R5; operator-topic elements = clusters in the top 10% of cosine to the mean automated operator message. A system is a role-text (operator-topic) system when ≥ half its element atoms are role-text (operator-topic) elements.
- **A8 Exogenous input.** Three levels from H145's E table (`exo.parquet`: human, relayed human input, automated operator), since automated messages fall in 75% of 30-min bins and would otherwise mask human input.

### Disclosure (2026-10-09)
While calibrating the synthetic artifact model, a diagnostic script also computed plug-in lagged information between the 12 real agent–own-repo pairs (median I(art′; agent | art) + I(agent′; art | agent) = 0.047 bits, vs 0.10 bits in the synthetic world). No H148 test was computed. The synthetic effect sizes were set before and not changed after. Consequence: the synthetic power for agent + own-repo links is likely optimistic for the real data.
- **A9 Scramble value (P6), fixed before real data.** Only for a discovered multi-agent or memeplex individual. Scramble = a forced context reset (NE41 wipe) of a member agent in bin b; placebo = the same agent's bins of the same phase without a reset. V = 1 when the individual's next-bin coarse state lies in its top symbol set (the fewest symbols covering ≥ 50% of its valid bins). ΔV from `semantic_kappa.scramble_cost` (agent × phase strata); I = Miller–Madow MI(x_b; x_b+1) at placebo bins minus at scramble bins; κ = ΔV / I, identified only when I's lower CI bound exceeds 0.02 bits (H87 A1).

### Synthetic validation (axis F; 2026-10-09, before any real-data outcome)
Worlds on the real #51 skeleton (bins, days, phase, exogenous-input bins, each agent's presence and project marginals, artifact owners and non-owner write rates; `analysis/synthetic.py`): **W_atoms** (independent Markov agents, persistence 0.75, each artifact written from its owner's state), **W_field** (W_atoms plus a common topic pull in and after human-input bins and a start-of-day orientation, both held by E), **W_nested** (W_atoms plus a planted pair: two agents follow a shared latent with probability ρ and write one shared artifact; at the element level, also a 6-element memeplex driven by its own prevalence and the pair). A discovery is false when it has ≥ 2 agents' worth of atoms (or ≥ 2 elements, or a room) and does not sit inside one true coupling component (an agent with the artifacts its state drives; the planted pair with its shared artifact, own artifacts and memeplex). Summary: `synthetic/summary.json`; figure `figures/synthetic.pdf`.

Agent level (67 atoms, 30-min bins, Z_ADD = 3; 20 replicates each):

| World | Worlds with a false multi-atom discovery | Planted pair recovered (both directions) | P1 share (all agents are individuals by construction) | P2 own-link closure |
| --- | --- | --- | --- | --- |
| W_atoms | 1/20, 0.05 [0.01, 0.24] | — | 0.92 (min 0.82) | 0.05 |
| W_field | 1/20, 0.05 [0.01, 0.24] | — | 0.75 (min 0.70) | 0.01 |
| W_nested, ρ 0.7 | 0/20, 0 [0, 0.16] | 0.40 [0.22, 0.61] | 0.85 (min 0.78) | 0.08 |
| W_nested, ρ 0.9 | 2/20, 0.10 [0.03, 0.30] | 0.65 [0.43, 0.82] | 0.90 (min 0.78) | 0.06 |

- Variant "held in one direction only" (not used): recovery 0.80 (ρ 0.7) and 0.95 (ρ 0.9), but a false multi-atom system in 35–75% of worlds. The card's two-direction rule is the one with size.
- Single-atom test (10 replicates per world, agents present ≥ 10 days): power 0.83 (range 0.70–0.96) for persistent agents; size 0/320 for agents whose states were shuffled within day. Agents with one dominant project carry little variation and fail.
- Coupling null (A5): P(z ≥ 3) = 0.0017 per candidate, P(z ≥ 2) = 0.037, over 2,357 non-coupled candidate pairs in W_atoms and W_nested; W_field 0.0053 and 0.037 over 1,512.
- Own-artifact links (planted median lagged information 0.10 bits): z ≥ 3 in 16% of links on one half, z ≥ 2 out of sample in 42%.
- Cost (profile, one seed then a full world): one search step over 66 candidates (8 + 32 day-permutation draws, two stages) takes ≈ 0.4 s; 0.46 ms per scored row (≈ 340 transitions); a full agent-level discovery (both directions, local maxima, out-of-sample tests) takes 60–95 s and ≈ 200k row evaluations. The element level (≈ 207 atoms) costs ≈ 3× per step and ≈ 3× more steps.

**Consequences, declared before real data.**
- **P2 is untestable** (recovery of the agent + own-repo closure 0.01–0.08 ≪ 0.8). Its outcome is reported as descriptive only.
- **K3 fires: P3 and P4 are "not identifiable"** (planted nested individual recovered at 0.40 for ρ 0.7 and 0.65 for ρ 0.9, both < 0.8). A discovery would still be reported (size ≤ 0.10 per world), but an absence means nothing.
- **P1:** the ≥ 90% bar sits at the method's ceiling (0.75–0.92 when every agent is an individual); the falsifier (< 50%) has margin (minimum 0.70). P1 is read on its falsifier; "supported" needs ≥ 90% as written.
- **P7** is computed as written (the rotated-data search is the calibrator; in W_atoms the two-direction rule gives 0.05 false multi-atom systems per world).
- **P5** needs the element level; its size check is the element-level W_field run (in progress at this commit; recorded before the element-level real run).
- Not completed: an element-level run is in progress (5 replicates per world, 140 element atoms); a Z_ADD = 2.5 variant was stopped after 5 W_atoms replicates (0 false; slower, 147 s per world) and is not used.

### Element level: amendment A10 and synthetic check (2026-10-09, before the element-level real run)
- **A10 Element-level search** (fixed before the element synthetic results): atoms = the 140 element atoms only (agents enter P4 through hosts, not as atoms); cap 8 atoms (the run brief's cap); add threshold z ≥ 3.2, which keeps the per-step false-add rate of 66 candidates at z 3 for 140 candidates. Reason: with all 207 atoms one world took > 20 min (in-sample growth over 193 candidates per step; profile: 263 search steps for 40 seeds, 90% of the time in held-out count tables).
- Synthetic (140 element atoms, 3 replicates per world; 4.3–6.2 min per world): no discovery in any world (W_atoms 0/3, W_field 0/3, W_nested 0/3). The planted 6-element memeplex was recovered in 0/3 worlds (held local maxima: 0–3 per half). W_field: 0 field-element systems (0/3, Wilson [0, 0.56]).
- **Consequences.** P4 stays "not identifiable" (K3; memeplex recovery 0/3). P5 is computed, but its size check rests on 3 worlds, and a search that finds nothing makes P5 hold by default; P5 is read as "no field system found", not as evidence that E removes fields.

### Results: agent level (2026-10-09, after the synthetic commit 765f6d4; non-reserved data only)
Run: `analysis/run.py --level agents --shuffle-reps 3` (67 atoms; 345 / 330 transitions; 145 s). Output: `results/agents_w30.json`, `search/agents_w30.json`, `individuals_agents.json`.

| | Statistic (95% CI) | Rule | Verdict |
| --- | --- | --- | --- |
| P1 agents found | 1 of 27 agents present ≥ 10 days is a single-atom individual on both halves (DeepSeek-V3.2); no agent + own-repo system is discovered: 0.04 [0.01, 0.18] (Wilson) | ≥ 0.9 supported; < 0.5 falsified | **failed** |
| P1 post hoc | permutation across the half's days within E cells (the day's state counts as the atom's own): 20 / 27 = 0.74 [0.55, 0.87]; artifacts 25 / 33; rooms 2 / 2 | — | post hoc, not a test |
| P2 agent + artifact | 0 of 25 agents with an own repo sit in a discovered system | untestable (A1 power ≤ 0.08) | **untestable** (descriptive 0 / 25) |
| P3 above the agents | 0 multi-atom systems discovered; 0 of 16 local maxima (8 odd-day, 8 even-day searches) hold out of sample | K3: recovery 0.40 < 0.8 | **not identifiable** |
| P6 discovered agents | no multi-agent or memeplex individual to score | — | **not testable** |
| P7 calibration | within-day rotated data: 16, 12, 12 local maxima (mean 13.3) vs 16 on real data, ratio 0.83; held out of sample: 0.33 vs 0 | ≤ 0.1 supported; ≥ 0.5 falsified | **failed → K1** |

- **K1 fires.** The in-sample local maxima of the real search are as many as on rotated data. No discovery is read (there is none to read: no maximum holds out of sample).
- **What the single-atom result says.** At 30 min, an agent's state (which project it touches) carries information about its next state mainly through the day's state: a within-day shuffle of its own states keeps the held-out colonial A (median 0.18 bits per transition on odd days, 28 agents with ≥ 40 transitions) for 26 of 27 agents. Agents hold one project for most of a day. Self-information lives at the day scale. The synthetic agents had no day-level persistence, so the synthetic check did not anticipate this; the pre-registered null is conservative for day-scale individuality.
- The two rooms are single-atom individuals under both nulls (talk volume persists within the day).

### Results: element level (2026-10-09, after commit b9e4a38; non-reserved data only)
Run: `analysis/run.py --level elements --shuffle-reps 2` (140 element atoms: 80 clusters, 60 markers; 25 role-text and 8 operator-topic elements; 18 min). Output: `results/elements_w30.json`, `search/elements_w30.json`, `individuals_elements.json`.

| | Statistic | Rule | Verdict |
| --- | --- | --- | --- |
| P4 ideologies | 0 memeplex systems discovered; 72 local maxima (56 pairs, 15 triples, 1 quadruple), 1 holds out of sample in one direction (two elements, mean z 2.1) and is not matched by the other direction | K3: planted memeplex recovered 0/3 | **not identifiable** |
| P5 fields not found | 0 discovered element systems, so 0 role-text or operator-topic systems | ≥ 1 field system falsifies | **supported (vacuous)**: nothing was discovered |
| P7 calibration | rotated data: 64 and 74 local maxima (mean 69.0) vs 72 on real data, ratio 0.96; held: 2.0 vs 1 | ≤ 0.1 / ≥ 0.5 | **failed → K1** |
| single elements | 1 / 140 elements beat the within-day permutation on both halves; post hoc cross-day null: 49 / 140 | — | descriptive |

### Impostors (filled)
| Impostor | How handled | Status |
| --- | --- | --- |
| Scheduler field | phase in E; DQ8 presence trim on the system's agents; day-permutation nulls keep each atom's phase; eligibility rule (A5); rotated-data calibrator (P7) | removed (synthetic null P(z ≥ 3) = 0.0017 with the trim vs 0.012 without) |
| Exogenous field | exogenous input in E with relayed human input (A8); W_field size 1/20 (agent level), 0/3 (element level); P5 | partly (P5 is vacuous: nothing was discovered) |
| Shared model priors | not modelled (no lab covariates); moot for a null result | open |
| Contemporaneous convergence | coupling uses lagged transfer terms only; E lagged; odd/even split | partly |

### Scorecard (round 1)
| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | atoms from named tables (`project_calls.proj`, cleaned commits, chat rooms, H145 elements); E with relayed input | 1 | content dropped from the agent state (A3); role-text projections not in E |
| B assumptions | Markov order 1; odd/even split; bin sweep | 1 | one width (30 min); day-level persistence sits in the single-atom null |
| C adequacy | local maxima beat rotated data out of sample | 0 | ratio 0.83 (agents), 0.96 (elements); 0 held real maxima |
| D unfitted predictions | nesting and κ of discovered individuals | 0 | nothing discovered |
| E interventional | NE41, hub loss, operator actions (κ) | 0 | not run: no candidate |
| F identifiability | planted recovery; false discoveries | 1 | size ≤ 0.10 per world; recovery 0.40 (ρ 0.7), 0.65 (ρ 0.9), memeplex 0/3, own link ≤ 0.08 |
| G ground truth | agents found; agent + own repo; role texts not found | 0 | 1/27 agents (pre-registered); 0/25 own-repo systems (untestable) |
| H comparative | W_nested vs W_atoms vs W_field on real data | 0 | real data match none: no growth |
| I transfer | 51m | 0 | not run (`analysis/confirm.py` dry-run only) |

**Claim that stands:** In #51 (07-06 → 09-04, 30-min bins, odd/even day split), an autonomous Krakauer boundary search over 32 agents, 33 repos, 2 rooms and 140 meaning elements finds no system larger than one atom that holds out of sample in both directions (0 of 16 agent-level and 1 of 72 element-level local maxima hold in one direction; rotated data give as many maxima, ratio 0.83 and 0.96), and only 1 of 27 agents beats a within-day permutation of its own states. Exclusions: P2 untestable (power ≤ 0.08); P3 and P4 not identifiable (K3: planted pair 0.40 at ρ 0.7, memeplex 0/3); P5 vacuous; P6 not testable; the cross-day single-atom result (20/27 agents) is post hoc; K1 fired, so no discovery would have been read.

## Notes
- 2026-10-09: written by the coordinator. The estimator design note of the stopped H143 run (`scratchpad/village_H143/individuality_design.txt`) applies: H58's key names map to the published Krakauer names as H58 "colonial" = organismal A*, H58 "organismal" = colonial A, H58 "environmental" = nC; `project_calls.label` values are URLs and hosts and need a mapping to repo slugs; match nulls on non-pause calls (Terra and Luna made 61–83% of their calls as pauses).
- 2026-10-09 (round 1, H148 agent): the run resumed a stopped draft; the draft's commit table (built before 4f6ab2e) was rebuilt with `memeplex.clean_commits`. Shared modules used: `memeplex.make_bins`, `memeplex.clean_commits`, `memeplex.slug`, `individuality.krakauer_discrete` (the batched evaluator in `h148lib.py` reproduces it exactly; `h148lib.verify()`), `individuality.transitions`, `individuality.delta_integration`, `individuality.rotate_within_day`, `individuality.onehot`. H145's frozen elements, expression panel, role patterns and exo table (memeplexes.json md5 9b899c34) were read only after `H145.READY`. `individuality.boundary_expand` was not used: its nC-only rule grows by estimator variance on joint codes (H145 note), and A1 replaces it with the transfer-term coupling.
- Round 2 candidates: a day-scale search (1-day states with a day-level null, over several goal periods since one period gives 22 transitions per half); H145 memeplex states as atoms; a reserved-day commit cleaner so `confirm.py` can run.

