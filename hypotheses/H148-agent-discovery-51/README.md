# H148: Autonomous agent discovery in #51: the systems that are individuals, found by search at every scale and nested

**Status:** pre-registered (not run). Card written 2026-10-09 from HH398 (Vivian: "any way you can develop your info dynamics framework to autonomously identify agents in the system?"). No H148 statistic has been computed. Uses H145's elements and the shared estimator `infra/shared/individuality.py` (H145 builds both and writes `scratchpad/H145_modules.READY` and `scratchpad/H145.READY`); until then it builds the search code and its synthetic validation.
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
Scored per model, mapping and window; 0/1/2. Thresholds: `writeup/papers/thermodynamics/sections/method.tex`.
**Rival models:** W_atoms (only single agents are individuals; nothing grows), W_field (the search grows systems along shared fields; they fail out of sample once E holds the fields), W_nested (planted nested individuals: an agent with its artifact inside a memeplex).
**Reserved data:** 51m.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | atoms and states from named tables; E as H145 | | |
| B assumptions | Markov order 1; split-half stationarity; bin sweep | | |
| C adequacy | local maxima beat matched random systems out of sample | | |
| D unfitted predictions | the nesting structure and the κ of discovered individuals are not used by the search | | |
| E interventional | NE41, hub losses, operator actions, #focus (κ) | | |
| F identifiability | planted nested individuals recovered on the real skeleton; false discoveries in W_atoms and W_field | | |
| G ground truth | each agent found; agent + own artifact found for most agents (H58); role texts not found | | |
| H comparative | W_nested vs W_atoms vs W_field | | |
| I transfer | 51m (not run) | | |

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
| [G51](goalperiod-subhypotheses/G51/README.md) | exploratory | pending | |
| 51m (reserved) | confirmatory | not run | |

## Results
*Pending.*

## Notes
- 2026-10-09: written by the coordinator. The estimator design note of the stopped H143 run (`scratchpad/village_H143/individuality_design.txt`) applies: H58's key names map to the published Krakauer names as H58 "colonial" = organismal A*, H58 "organismal" = colonial A, H58 "environmental" = nC; `project_calls.label` values are URLs and hosts and need a mapping to repo slugs; match nulls on non-pause calls (Terra and Luna made 61–83% of their calls as pauses).
