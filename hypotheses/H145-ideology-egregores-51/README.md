# H145: Ideology egregores in #51: memeplexes that live above their hosts and are Krakauer individuals at the pattern level

**Status:** pre-registered (not run). Card written 2026-10-09 from HH392 and HH393, after Vivian's clarification that the egregore is "something like an ideology … that runs over agents, with its own functional set of behaviors", and after a qualitative reading of #51 (story section of `writeup/papers/superagents/`; scratch `story51/part0–3`). No H145 statistic has been computed. No code exists yet.
**Fields:** info theory, cultural evolution, sociophysics
**Literature:** [Krakauer et al. 2020](../../literature/krakauer-2020-information-theory-of-individuality.md); [Kolchinsky & Wolpert 2018](../../literature/kolchinsky-2018-semantic-information-autonomous-agency.md); [Vivian's essay, Direction 3](../../literature/jazzloaf-2026-agent-ecologies-essay.md); [Heylighen 2016](../../literature/heylighen-2016-stigmergy-universal-coordination-mechanism.md); [Rosas et al. 2019](../../literature/rosas-2019-o-information-high-order-interdependencies.md)
**Definitions used:** *egregore (an ideology running on a substrate of agents)*, *memeplex*, *hosts* (new, `physics-models/DEFINITIONS.md`); *Krakauer individuality*, *size-matched grouping* (here: frequency-matched pseudo-patterns); *meaning clusters* (shared instrument, exception (a)); H34 idea markers (`infra/shared/idea_markers.py`).
**Question served:** Q3 (collective order beyond fields), Q4 (where the swarm's information lives), `GOALS.md`. Paper 2 (`writeup/papers/superagents/`). Siblings: H146 (recruitment and functional behaviors), H147 (value and relation to hosts). H143 and H144 (group superagents) are parked unrun; they are the contrast case.

## Question
Does #51 hold ideologies that run over its agents: patterns of ideas, norms and practices that many agents carry, that persist while their carriers change and forget, and whose own state predicts their future beyond the fields that act on the agents? If so, which patterns, carried by whom, and for how long?

## Model
**From:** `physics-models/12-information-dynamics/` (Krakauer individuality, applied with the pattern as the system and the agents as the substrate); `physics-models/13-cultural-evolution-conventions/` (patterns of conventions); `physics-models/03-contagion/` (spread, used in H146).

A memeplex K is a set of elements e ∈ K. Element expression x_{i,e}(b) = 1 if agent i expresses e in bin b. The pattern's hosts H_K(b) = {i : Σ_{e∈K} x_{i,e}(b) ≥ m}. Its state S_K(b) is (n_K(b), c_K(b)): the number of hosts (prevalence, binned in ≤ 5 levels) and the composition (which third of K's elements dominates, 3 symbols), village-wide. With E the impostor bundle (below), per K:
- colonial A_K = I(S′_K; S_K | E), organismal A*_K = I(S′_K; S_K), nC_K = I(S′_K; E | S_K), NTIC_K = A*_K − A_K;
- integration Δ_K = L(S′_K | {s_e}_{e∈K}, E) − L(S′_K | S_K, E): what the joint state adds beyond the elements' own prevalences s_e (each element's own past, fitted additively);
- host renewal: J_K(k) = Jaccard(H_K over days d−k+1…d, H_K over days d+1…d+k) against ρ_K(k) = the autocorrelation of daily prevalence at lag k. A pattern lives above its hosts if ρ_K(5) > J_K(5).
L(·|·) are held-out log-losses in bits per bin, day-blocked leave-one-day-out with the total-minus-day trick; every quantity is reported as an excess over frequency-matched pseudo-patterns.

## Data scheme (`scheme/`)
- **Span:** #51, 2026-07-06 → 2026-09-04 (units 51a–51l). The reserved tail 51m (09-07 → 09-18) is masked; `analysis/confirm.py` freezes the memeplex definitions and runs only with Vivian's sign-off.
- **Elements (fixed rules, built before any test):**
  - *meaning clusters:* k-means (k = 80; variants 40, 160) on `embeddings/statements_style_resid_period32_bge_small.npy` rows of #51 statements (80,446 rows; `statements.parquet` for agent, time, room); the same with gte; an element = a cluster with statements from ≥ 3 agents;
  - *coinages and protocol names:* H34 idea markers of classes N (names and coinages) and W (rare words), used by ≥ 3 agents on ≥ 2 days (`idea_markers.uses_for_rows`, hashes only);
  - *practices:* shared repos (≥ 3 agent writers with ≥ 3 commits each after cleaning: drop automated commits and the `surprise-lab-mirror-proofs` screenshot loop; dedupe by hash across mirrored repos (Grok 4.5); drop `-chat@agentvillage.org` authors and commits by agents with no call on the repo that day; drop commits before the owner joined), and touched projects from `project_calls.proj` (touch-based; not `label`, which carries over resets).
- **Memeplex discovery:** the element co-occurrence graph over agent × 2-h bins, edge weight = positive PMI of co-expression within the same agent and bin, minus the agent-constant expectation (each agent's own element frequencies, so one agent's habitual vocabulary does not link elements by itself); communities by Leiden (or greedy modularity), resolution fixed by maximum modularity on a null graph; a memeplex qualifies if it has ≥ 4 elements, ≥ 3 hosts from ≥ 2 labs, and a lifetime ≥ 10 active days. Expression threshold m = 2 elements per bin (variant m = 1, 3).
- **Hub artifacts are labelled, not removed:** h_K = the largest share of K's expressions by one host. h_K ≥ 0.8 marks "one agent's vocabulary" (reported; cannot pass HH392).
- **Bins:** active 2-h bins (variants 30 min and 1 day) inside each day's window, DQ8 all-present trim.
- **Environment E (lagged, coarse):** (e1) scheduler phase (time-of-day × first/last bin × bookends on); (e2) operator and human input: any human message, nudge, kickoff, or relayed human input (a Claude Fable 5 message that relays an outside human, coded by a rule fixed on 07-06 → 07-16 and checked by hand on 30 messages) in the bin, plus its similarity to K's centroid; (e3) role-text field: the mean similarity of K's centroid to the private role texts of the agents present (`embeddings/goals.parquet`, `goal_vectors.npy`, agent_goal rows) and to the #51 kickoff; (e4) the rest of the village's activity level. Agent identity and lab enter the element-level models as covariates.
- **Pseudo-patterns (the null):** for each K, 200 random element sets of the same size drawn from elements matched in frequency (±25%) and host count (±1), and the full discovery pipeline rerun on 20 within-agent time-shuffled datasets (each agent's bins permuted within day, which keeps each agent's vocabulary and day structure and breaks the cross-agent timing) to calibrate the selection.
- **Output:** `data/processed/H145-ideology-egregores-51/` (`elements.parquet` (element id, kind, size, hosts), `expr/` (agent × bin × element, sparse), `memeplexes.json` (elements, hosts, lifetime, h_K, top statements paraphrased only as cluster labels, never verbatim), `results/`, `synthetic/`, `_provenance.json`). Shared code: `infra/shared/memeplex.py` (elements, expression, discovery; `--verify`) and `infra/shared/individuality.py` (Krakauer held-out estimator, generalized from `hypotheses/H58-coordinated-superagents/analysis/h58lib.py: krakauer`; `--verify`). H145 owns both and writes the ready markers that H146 and H147 wait on.

## Observables
Per memeplex: hosts, labs, lifetime, h_K, field-seeded flag (first element use is in an operator or human message), ρ_K(k) and J_K(k) for k = 1, 3, 5 days, A_K, A*_K, nC_K, NTIC_K, Δ_K and their pseudo-pattern z-scores, at 30 min, 2 h, 1 day. A human-readable label per memeplex (from its cluster centroids and marker classes; paraphrased) and a mapping to the qualitative candidates (verification, protections, welfare, governance, onboarding, relay, byte game, Echoes).

## Null / baseline
1. Frequency-matched pseudo-patterns (primary).
2. The pipeline rerun on within-agent time-shuffled data (selection calibration): the number and lifetime of memeplexes that random timing produces.
3. Field-only skeletons (DQ8 `simulate.py` content preset, zero coupling) for the Krakauer z-tests.
4. Role-text patterns: elements nearest to each agent's role text, grouped by role class. They are fields by construction; the positive control for e3.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Thresholds: `writeup/papers/thermodynamics/sections/method.tex`, "Faithfulness, not fit".
**Rival models:** W_field (patterns are shared inputs: role texts, operator topics; colonial A at the pseudo level once E holds them), W_hub (patterns are one agent's vocabulary that others echo; h_K high, no host renewal), W_prior (patterns are family style; one lab), W_egregore (a planted memeplex with self-reinforcing expression across changing hosts).
**Reserved data for confirmation:** 51m (09-07 → 09-18), with memeplex definitions frozen.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | elements from embeddings, markers and cleaned commits; E from ledgers and role texts | | |
| B assumptions | Markov order 1 per bin; stationarity by split halves; bin-width sweep | | |
| C adequacy | held-out log-loss gains over E-only and element-only models | | |
| D unfitted predictions | host renewal (ρ > J) is not used to find memeplexes; the qualitative labels predicted before results (P5) | | |
| E interventional | NE41 wipes, hub losses, operator actions (H146, H147) | | |
| F identifiability | synthetic worlds on the real #51 skeleton; size ≤ 0.10, power at planted strengths | | |
| G ground truth | role-text patterns at the field level; the qualitative candidates recovered or not | | |
| H comparative | W_egregore vs W_field vs W_hub vs W_prior | | |
| I transfer | the tail 51m (not run) | | |

## Prediction
*Written 2026-10-09, before running the analysis on real data.*

| | Card's prediction (operational) | Falsified if | My prior |
| --- | --- | --- | --- |
| **P1** memeplexes exist | ≥ 3 qualifying memeplexes (≥ 4 elements, ≥ 3 hosts, ≥ 2 labs, lifetime ≥ 10 days) with h_K < 0.8, more than the 95th percentile of the time-shuffled pipeline | ≤ the shuffled pipeline's 95th percentile | 0.75 |
| **P2** they outlive their hosts | for ≥ 2 of them, ρ_K(5) > J_K(5) with the difference above its pseudo-pattern 95th percentile | ρ_K(5) ≤ J_K(5) for all | 0.6 |
| **P3** integrated individuals | colonial A_K excess z ≥ 2 and Δ_K > 0 (z ≥ 2) at 2 h for ≥ 1 memeplex that passes P2 | none passes with E holding e1–e3 | 0.4 |
| **P4** fields are fields | role-text patterns and field-seeded patterns have organismal A* z ≥ 2 but colonial A z < 1 | role-text patterns pass P3 (E has not removed the field) | 0.75 |
| **P5** which ones | among memeplexes passing P2, the verification/audit pattern and the onboarding pattern appear (labels assigned blind to P3 results by matching centroids to the story's descriptions); the byte game and Echoes appear as hub-centered (h_K ≥ 0.6) | none of the qualitative candidates is recovered | 0.5 |
| **P6** time scale | colonial A excess peaks at 1 day for P2 patterns (ideologies live on day scales), not at 30 min | peak at 30 min | 0.5 |

**Kill rules.** (K1) If P1 fails, no ideology is resolved in #51 at this instrument; H146 and H147 run only on the qualitative candidates, labelled post hoc. (K2) If every P2 pattern fails P3 with synthetic power ≥ 0.8 at the planted strength that matters, the verdict is "patterns persist above hosts but are not individuals beyond the fields". (K3) If role-text patterns pass P3, no positive is read until E is fixed (a dated amendment).

**Overall prior.** I expect 5–15 qualifying memeplexes, most of them hub vocabularies (DeepSeek-V3.2's frameworks, Echoes, the byte game) and a few distributed norms (verification, onboarding, possibly protections). The distributed norms should outlive their hosts (P2), because new agents pick them up within days. Whether they are individuals beyond the fields (P3) is the open question; my guess is that colonial A is small, because much of each norm is re-supplied by artifacts and role texts.

**Synthetic validation (axis F), before real data.** Worlds on the real #51 skeleton (agents present per bin, statement counts per agent-bin): W_field (elements expressed by a time-varying shared field plus each agent's own vocabulary), W_hub (one agent's vocabulary echoed by readers with probability q), W_prior (a lab-specific vocabulary), W_egregore (a planted memeplex of 8 elements whose expression in bin b+1 rises with its prevalence in bin b, with weight ρ ∈ {0.2, 0.4}, and is picked up by newcomers). 20 replicates. Report the pipeline's recovery of the planted memeplex (element overlap), the size of P2 and P3 in W_field, W_hub and W_prior (≤ 0.10), and the power in W_egregore.

## Impostors
| Impostor | How handled | Status (planned) |
| --- | --- | --- |
| Scheduler field | e1 in E; DQ8 trim; within-day transitions | removed |
| Exogenous field (role texts, operator, humans, relayed humans) | e2–e3 in E; role-text patterns as the positive control (P4); field-seeded flag | removed if P4 holds |
| Shared model priors | ≥ 2 labs per memeplex; style-residualized embeddings; agent and lab covariates; W_prior | partly |
| Contemporaneous convergence | E lagged; read-gated spread is H146's test | partly (closed by H146) |

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G51](goalperiod-subhypotheses/G51/README.md) (07-06 → 09-04) | exploratory | pending | |
| 51m (reserved) | confirmatory | not run | |

## Results
*Pending.*

## Notes
- 2026-10-09: written by the coordinator from HH392–HH393. Efficient estimators are required (`scratchpad/village_egregore_brief.md`, "Efficient estimators"): integer-encoded counts with `np.bincount`, leave-one-day-out by subtraction, cached pseudo-pattern nulls, sequential stopping. Text is read in memory only; cluster labels are paraphrases.
