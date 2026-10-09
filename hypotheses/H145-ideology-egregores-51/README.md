# H145: Ideology egregores in #51: memeplexes that live above their hosts and are Krakauer individuals at the pattern level

**Status:** round 1 done (2026-10-09), exploratory, mixed. 15 cross-lab memeplexes are found beyond the null (P1 supported); 2–3 renew their hosts (P2 amended, fragile); one broad topical memeplex (K03) is a colonial individual beyond E at 2 h (P3a, z 2.96, fragile); the field control is uninformative (P4 failed), the qualitative labels are not recovered as predicted (P5 failed), and the time scale is 30 min, not 1 day (P6 failed, exploratory). P2 as written and Δ are untestable (A4, A5). Reserved 51m not run. Card written 2026-10-09 from HH392 and HH393, after Vivian's clarification that the egregore is "something like an ideology … that runs over agents, with its own functional set of behaviors", and after a qualitative reading of #51.
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
| A mapping | elements from embeddings, markers and cleaned commits; E from ledgers and role texts | 1 | elements from embeddings, markers, cleaned commits, projects; E coarse (tertiles); Round 1 |
| B assumptions | Markov order 1 per bin; stationarity by split halves; bin-width sweep | 1 | bin-width sweep done (P6); K03 not stationary across halves |
| C adequacy | held-out log-loss gains over E-only and element-only models | 1 | held-out gains measured; A* z ≥ 2 for 3/15 memeplexes at 2 h |
| D unfitted predictions | host renewal (ρ > J) is not used to find memeplexes; the qualitative labels predicted before results (P5) | 1 | renewal not used in discovery; labels fixed before outcomes; P5, P6 failed |
| E interventional | NE41 wipes, hub losses, operator actions (H146, H147) | 0 | not done (H146, H147) |
| F identifiability | synthetic worlds on the real #51 skeleton; size ≤ 0.10, power at planted strengths | 1 | 8 synthetic worlds × 20 reps: P1, P2 (A4), P3a calibrated; Δ and P2 as written untestable |
| G ground truth | role-text patterns at the field level; the qualitative candidates recovered or not | 0 | role-text controls show no A*; story candidates not recovered as predicted |
| H comparative | W_egregore vs W_field vs W_hub vs W_prior | 1 | rival worlds separated on synthetic; K03 not separable from a leaked field on real data |
| I transfer | the tail 51m (not run) | 0 | 51m not run |

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
| [G51](goalperiod-subhypotheses/G51/README.md) (07-06 → 09-04) | exploratory | mixed | 15 memeplexes (null q95 6); P2 3/15; P3a 1 (K03, z 2.96); P4–P6 failed |
| 51m (reserved) | confirmatory | not run | `analysis/confirm.py` dry-run only |

## Results
See Round 1.

## Round 1 (2026-10-09)
Run by the H145 agent (resumed after an accidental stop). Code: `scheme/build.py` (elements, panels, discovery, labels), `analysis/h145lib.py`, `analysis/synthetic.py`, `analysis/summarize_synthetic.py`, `analysis/run_real.py`. Shared: `infra/shared/memeplex.py`, `infra/shared/individuality.py` (H145 owns both). Data: `data/processed/H145-ideology-egregores-51/` (`synthetic/`, `results/`).

### What was seen before this section (disclosure)
- The first H145 agent built the elements with the old commit cleaner and ran discovery by the card's rules on real data (agent-constant PPMI, per-pair p < 0.01, resolution by the Q-gap rule). It got 5 qualifying communities of 175–768 elements, each with 28–32 hosts and a 45-day lifetime. No test statistic was computed.
- This agent rebuilt the elements with the fixed cleaner (`memeplex.clean_commits` at 4f6ab2e: 48,093 work commits → 44,349 kept; 15 shared repos, 112 projects, 80 clusters, 1,804 N/W markers; 2,011 elements). During profiling it saw only edge counts of the real 2-h graph under candidate rules: 14,221 (card), 7,502 (activity-adjusted, p < 0.01), 4,516 (activity-adjusted, BH q 0.05), 2,292 (BH q 0.01). It saw no community, count or test outcome under the amended rules before the amendments below were fixed.
- Reserved data: #51m (09-07 → 09-18) is masked in every build (`holdout_mask`). Reserved #45–#50 are not used at all (vocabulary exposure, see Notes).

### Measured cost (one window, 2-h bins, 2,011 elements; single thread)
- A1 graph: 0.1 s. Louvain (5 seeds): 1.3 s. One discovery with 20 null pipelines: 6.8 s per synthetic world.
- One pattern-level Krakauer evaluation (A, A*, nC, Δ; 4 + 1 ridge-logit fits, leave-one-day-out over 45 days, 135 transitions): 0.25–0.34 s. A pseudo-pattern test with Besag–Clifford (h 10, n_max 200) costs ≤ 70 s per memeplex.
- Pseudo-pattern P2 test (200 draws): ~2 s per memeplex.

### Synthetic validation of discovery (axis F; 2026-10-09, before real discovery under the amended rules)
Worlds on the real #51 skeleton (2-h bins): real presence (32 agents × 180 bins), every real element expressed independently at its agent's real rate times the real agent-bin activity factor (CV of activity 1.04), plus planted elements. W0 = no coupling. W_field = a shared day-scale field drives hosting. W_hub = one hub with a persistent on/off state, echoed with probability 0.05. W_prior = one lab's constant vocabulary. W_sticky = five fixed hosts from ≥ 2 labs. W_egr(ρ) = three planted memeplexes of 8 elements with self-reinforcing recruitment (ε 0.005 + ρ × previous host share; stay 0.85 per bin; newcomers recruited). 20 replicates per world.

| world | card rules: hub-free qualifying (mean) | card rules: max community size | card rules: planted Jaccard | A1 rules: hub-free qualifying | A1: planted recovered (J ≥ 0.5, qualifies) | P1 pass (A1 + A2 null) |
| --- | --- | --- | --- | --- | --- | --- |
| W0 | 23.8 | 106 | — | 0.0 | — | 0/20 |
| W_field | 23.6 | 125 | 0.30 | 1.0 | 20/20 | 0/20 |
| W_field (noisy E) | 23.5 | 119 | 0.30 | 1.0 | 20/20 | 0/20 |
| W_hub | 24.6 | 97 | 0.46 | 0.1 | 1/20 | 0/20 |
| W_prior | 23.4 | 91 | — | 0.0 | 0/20 | 0/20 |
| W_sticky | 25.3 | 102 | 0.46 | 0.1 | 2/20 | 0/20 |
| W_egr ρ 0.2 | 24.6 | 111 | 0.29 | 3.0 | 60/60 | 20/20 |
| W_egr ρ 0.4 | 25.3 | 105 | 0.36 | 3.0 | 60/60 | 20/20 |

Findings: (i) Under the card's rules, a no-coupling world gives 24 qualifying "memeplexes" of up to ~100 elements. Busy agent-bins link every element (activity is not in the agent-constant expectation), and ~1% chance edges pass the per-pair filter. The planted memeplex is merged into a large community (Jaccard ≤ 0.36). (ii) The card's P1 null (each agent's bins permuted within day) leaves the discovery graph exactly unchanged (checked in every world: O and E are sums over agent-bins), so P1 could never pass. (iii) The Q-gap resolution rule picked γ = 0.5 or 2 at random across worlds (Q_null ≈ Q_real on sparse graphs). (iv) A within-day rotation null keeps a planted memeplex intact (3.0 of 3 found in the null), because hosts stay hosts for whole days at 4 bins per day.

### Amendment A1 (2026-10-09, from the synthetic check, before real discovery): the discovery graph
The PPMI expectation also holds agent-bin activity: E_ef = Σ_i w_i c_ie c_if with w_i = Σ_b a_ib² / (Σ_b a_ib)², where a_ib is the number of distinct elements agent i expresses in bin b (independence model P(x_ieb) = c_ie a_ib / A_i; with constant activity this is the card's expectation). Edges are kept by Benjamini–Hochberg at q = 0.05 over all pairs with O_ef ≥ 3. Reason: finding (i). Effect: 0 qualifying communities in W0, W_prior; the planted memeplexes recovered exactly in W_egr (60/60) and W_field (20/20). Code: `memeplex.ppmi_graph(activity=True, fdr=0.05)`. A busy bin no longer links elements by itself; this is the card's rule ("one agent's habitual vocabulary does not link elements") extended to activity.

### Amendment A2 (2026-10-09, before real data): the P1 selection null
P1's null pipeline shifts each element's series circularly within the agent's whole sequence of present bins (an independent offset per agent and element; `memeplex.rotate_elements(scope="agent")`). It keeps each agent's vocabulary and presence and breaks the timing of co-expression. 20 reruns of the A1 pipeline. Reason: finding (ii) and (iv). Synthetic: size 0/120 in the six non-egregore worlds; power 40/40 in W_egr. The within-day rotation is reported as a descriptive variant.

### Amendment A3 (2026-10-09, before real data): resolution
γ = 1 (standard modularity), fixed. γ = 0.5 and 2 are reported as variants. Reason: finding (iii).

### Synthetic validation of P2 and P3 (2026-10-09, before any real P2/P3 outcome)
Same worlds, 20 replicates (60 planted memeplexes per W_egr world). P2 against 200 frequency- and host-count-matched pseudo-patterns. P3 against pseudo-patterns with Besag–Clifford (h 10, n_max 60, ≥ 30 draws), E = phase (bin-in-day × bookends) + the field tertile (W_field; "noisy" adds observation noise of sd 0.7 to it) + rest-of-village activity tertile, 2-h bins, 135 within-day transitions. "Instrument" = the planted set itself; "end-to-end" = the discovered match (a planted set counts only if discovery recovers it).

| world | P2 as written (ρ−J) | P2 D_K(5) (A4) | P2 φ host memory | P3 A z ≥ 2 | P3 Δ z ≥ 2 | P3 both (as written) |
| --- | --- | --- | --- | --- | --- | --- |
| W_egr ρ 0.2 (power) | 0.20 | **0.82** | 0.87 | **0.87** | 0.02 | 0.00 |
| W_egr ρ 0.4 (power) | 0.02 | **0.85** | 0.30 | 0.42 | 0.10 | 0.03 |
| W0 (instrument) | 0.00 | — | — | 0.05 | 0.20 | 0.00 |
| W_field (instrument) | 0.00 | 0.80 | 1.00 | 0.05 | 0.00 | 0.00 |
| W_field, noisy E (instrument) | 0.00 | 0.55 | 1.00 | **0.20** | 0.00 | 0.00 |
| W_prior (instrument) | 0.00 | 0.00 | 0.00 | 0.00 | 0.60 | 0.00 |
| W_sticky instrument / end-to-end | 0.00 / 0.00 | 0.40 / **0.05** | 0.50 / 0.05 | 1.00 / 0.05 | 0.40 / 0.00 | 0.40 / 0.00 |
| W_hub instrument / end-to-end | 0.00 / 0.00 | 0.00 / **0.05** | 0.05 / 0.00 | 0.80 / 0.00 | 0.10 / 0.05 | 0.10 / 0.00 |

Findings: (v) P2 as written has power 0.20 and 0.02: a self-sustaining pattern has nearly stationary prevalence (ρ_K(5) ≈ 0), and over 5 days nearly every agent hosts once (J_K(5) ≈ 1). (vi) Δ has no power (0.02–0.10) and wrong size (0.60 under W_prior, 0.20 under W0). The planted dynamics are additive in the elements, so the parts model predicts as well as the joint state; with 135 transitions the parts model (8+ standardized prevalences) is noisy. (vii) Colonial A has power 0.87 at ρ 0.2 and 0.42 at ρ 0.4 (prevalence saturates at ~0.5–0.75 host share, so the state barely moves). Size is 0.05 when E holds the field exactly and 0.20 when E holds a noisy copy. (viii) Sticky hosts and hubs pass the instrument tests often (A is the persistence of the hub's or the sticky hosts' state), but discovery's agent-constant expectation removes them first (end-to-end size ≤ 0.05).

### Amendment A4 (2026-10-09, before real P2): host renewal
P2 as written (ρ_K(5) > J_K(5), difference above the pseudo-pattern 95th percentile) is **untestable** (power 0.20 / 0.02 < 0.8). It is reported but not used for the verdict. P2 is amended to the renewal contrast D_K(5) = S_K(5) − S_H(5): S_K(5) = share of days with ≥ 1 host whose day + 5 also has ≥ 1 host (the pattern survives); S_H(5) = share of (host, day) pairs, with the host present on day + 5, in which the host hosts again on day + 5 (the host returns). Pass: D_K(5) above the 95th percentile of 200 frequency- and host-count-matched pseudo-patterns. Power 0.82 / 0.85; end-to-end size ≤ 0.05 (W_sticky, W_hub). Limit: D does not separate a field from an egregore (W_field 0.80); P3 and P4 do that. φ (host memory) is reported as a variant (power 0.30 at ρ 0.4). P2 still needs ≥ 2 passing memeplexes.

### Amendment A5 (2026-10-09, before real P3): integration Δ untestable
Δ_K is **untestable** at this instrument (finding vi). It is not computed on real data. P3 is judged on its first half only: **P3a** = colonial A_K excess z ≥ 2 over pseudo-patterns at 2 h with E holding e1–e4, for ≥ 1 P2 memeplex. P3 as written (A and Δ) is untestable. Power of P3a: 0.87 at ρ 0.2, 0.42 at ρ 0.4; so K2 ("power ≥ 0.8 at the planted strength that matters") holds only for unsaturated patterns (ρ 0.2). The field-leak size 0.20 under a noisy E means a P3a pass is read only together with P4 (role-text patterns must fail P3a, K3). P6 (time scale) uses the same A test at 30 min and 1 day; it is not validated on synthetic data at those widths and is reported as exploratory.

### Sanity-check expectations (named before outcomes; never a tuning target)
From `scratchpad/story51/part4_ideology_genealogy.md` §8–9 (qualitative reading of #51): verify-and-correct is the strongest candidate (≥ 8 hosts, ≥ 5 labs, rotating hosts); consent/protection ("aggregate-only", born 07-09) is a candidate; governance is mostly a field (its ban sub-family persists); dictate-and-build is a practice, visible only with commits; host-the-newcomer is a ritual; DeepSeek-V3.2's frameworks are one hub's program, not an egregore; cross-promotion and the byte-guess game are field or hub controls. The card's P5 encodes the testable part. Labels are assigned by a token rule fixed in `scheme/build.py` (`FAMILIES`, `label_rule`) before any test outcome.

### Frozen memeplexes (2026-10-09, `memeplexes.json`, before any test outcome)
Real A1 graph: 4,516 edges over 2,011 elements; 65 communities of ≥ 2 elements; **15 qualify, all hub-free** (h_K 0.13–0.56). Fourteen are large topical communities: 31–187 elements (mostly markers), 15–31 hosts, 7–8 labs, alive on 37–45 of 45 days. K14 is small (4 markers, 3 hosts, 2 labs, 10 days). The most frequent top host is DeepSeek-V3.2 (12 of 15; Echoes K05: Gemini 2.5 Pro). Labels by the fixed token rule: verify K01, K02; governance K03; echoes K05; frameworks K06, K07, K11, K15; welfare K12; unlabelled K04, K08, K09, K10, K13, K14. Field-seeded: K11 only. Variants of the count: γ 0.5 → 13, γ 2 → 26, m 1 → 15, m 3 → 14, 30-min bins → 14, 1-day bins → 10; the card's original rules → 11 (largest 304 elements). `scratchpad/H145.READY` was written at this point.

### Results (exploration data; reserved data untouched)
| | Prediction | Observed (CI / null) | Verdict by the rule |
| --- | --- | --- | --- |
| P1 | ≥ 3 qualifying hub-free memeplexes, above the null pipeline's 95th pct | **15** vs A2 null mean 3.4, 95th pct 6 (20 pipelines; range 1–6). Within-day rotation (descriptive): 15–17 | **supported** |
| P2 (as written) | ρ_K(5) > J_K(5), above pseudo 95th pct, for ≥ 2 | 1/15 (K08) | **untestable** (power 0.20; A4), reported only |
| P2 (A4) | D_K(5) above pseudo 95th pct for ≥ 2 | **3/15**: K03 0.289 vs 0.262; K07 0.530 vs 0.491; K14 0.208 vs 0.000 (degenerate null: its pseudo-patterns are almost never alive) | **supported, fragile** (margins 0.03–0.04; K14 not counted as evidence) |
| P3 (as written) | A z ≥ 2 and Δ z ≥ 2 for ≥ 1 P2 memeplex | Δ not computed | **untestable** (A5) |
| P3a (A5) | colonial A excess z ≥ 2 at 2 h, E = e1–e4, for ≥ 1 P2 memeplex | **K03: A = 0.206 bits/transition, excess 0.197 [0.067, 0.326], z 2.96, p 0.010** (200 draws; a rerun gives z 2.67). K07 z 0.25; K14 z −0.39. (Not P2: K05 z 2.83, K08 z 2.68.) | **supported, fragile** (one memeplex; 3 tested, Bonferroni p 0.03) |
| P4 | role-text and field-seeded patterns: A* z ≥ 2 and A z < 1 | R0–R5: A* z −0.06 to 1.02; A z −0.02 to 1.37 (R1 1.06, R2 1.37, R3 1.09). Field-seeded K11: A* z −0.85, A z −1.56 | **failed** (no field pattern shows A*; K3 does not fire: none has A z ≥ 2) |
| P5 | verify and onboarding among P2 patterns; byte game and Echoes hub-centered (h_K ≥ 0.6) | P2 patterns are governance (K03), frameworks (K07), unlabelled (K14). Verify K01/K02 fail P2; no onboarding memeplex; Echoes K05 h_K 0.14; no byte-game memeplex | **failed** (the falsification rule "none recovered" is not met: governance and frameworks are candidates) |
| P6 | colonial A excess peaks at 1 day for P2 patterns | K03 z 5.59 (30 min), 2.67 (2 h), −0.90 (1 day); K07 4.31, 0.07, 0.46; K14 −8.8, −0.56, 4.14 (degenerate) | **failed** (peaks at 30 min); exploratory (not synthetic-validated at 30 min or 1 day) |

Kill rules: K1 does not fire (P1 holds). K2 does not fire (K03 passes P3a; power 0.87 at ρ 0.2). K3 does not fire (no role-text pattern passes P3a), but P4 cannot show that E removes a field, because no field pattern has organismal A* to remove.

**Post hoc** (`analysis/posthoc.py`, after the outcomes): K03's P3a lives in the second half of the span (days 1–22: z 0.35; days 23–45: z 3.66, p 0.010). It depends on the host threshold (m 1: z 1.47; m 3: z 4.29). Exogenous messages (mostly operator nudges) fall in 94% of 2-h bins, so a no-exogenous-bin check is not computable.

**Sanity check against the qualitative reading** (named above, before outcomes): verify memeplexes exist with 22–30 hosts from 7–8 labs, as expected, but they do not renew hosts faster than matched patterns, so the "rotating hosts" expectation is not reproduced. The frameworks memeplex K07 renews its hosts but is not an individual (P3a z 0.25), consistent with "not an egregore". K03 (labelled governance by 6 of 187 tokens; mostly external-engagement, papers and validation-toolkit work) passes P3a, which is in tension with "governance is mostly a field"; K03 is a broad topic community, not the governance memeplex the story describes. No consent ("aggregate-only") or onboarding memeplex is resolved as its own community at this instrument.

### Impostors (round 1)
| Impostor | How handled | Status |
| --- | --- | --- |
| Scheduler field | e1 (bin-in-day × bookends) in E; DQ8 presence; within-day transitions; activity in the discovery expectation (A1) | partly (K03's peak at 30 min may still carry within-day rhythm) |
| Exogenous field (role texts, operator, humans, relayed humans) | e2–e3 in E; role-text controls R0–R5; field-seeded flag | partly (P4 uninformative; 94% of bins carry exogenous input; field-leak size 0.20 with a noisy E in synthetic) |
| Shared model priors | ≥ 2 labs (all 15 have 7–8 labs, except K14 with 2); style-residualized clusters; W_prior not discovered (0/20) | removed for discovery; partly for P3a |
| Contemporaneous convergence | E lagged one bin; read-gating not tested here (H146) | open |

### Scorecard (round 1)
| Axis | Score | Evidence |
| --- | --- | --- |
| A mapping | 1 | elements from embeddings, markers, cleaned commits, projects; E from ledgers and role texts, but coarse (tertiles) |
| B assumptions | 1 | bin-width sweep done (P6); K03 not stationary across halves |
| C adequacy | 1 | held-out log-loss gains measured; A* z ≥ 2 only for K05, K08, K12 (2 h) |
| D unfitted predictions | 1 | renewal not used in discovery; labels fixed before outcomes; P5 and P6 failed |
| E interventional | 0 | not done (H146, H147) |
| F identifiability | 1 | P1 size 0/120, power 40/40; P2 (A4) power 0.82–0.85, end-to-end size ≤ 0.05; P3a power 0.87/0.42, size 0.05 (0.20 noisy E); Δ and P2 as written failed |
| G ground truth | 0 | role-text controls show no A*; qualitative candidates not recovered as predicted |
| H comparative | 1 | W_egregore vs W_field/W_hub/W_prior/W_sticky separated on synthetic; on real data K03 cannot be told from a leaked field |
| I transfer | 0 | 51m not run (confirm.py dry-run only) |

### Confirmatory design (frozen in `analysis/confirm.py`, dry-run only, NOT RUN)
On 51m with the frozen memeplexes (md5 9b899c34…), no rediscovery: C1 D_K(3) above pseudo 95th pct for K03, K07, K14; C2 K03 colonial A excess z ≥ 2 at 2 h; C3 R0–R5 colonial A z < 1. The reserved-day panel builder is not written; the script refuses a real run.

**Claim that stands:** In #51 (45 non-reserved days, 2-h bins), activity-corrected co-expression finds 15 cross-lab memeplexes, more than chance timing gives (null 95th pct 6). Only one, K03, a broad engagement-and-papers topic community, carries state information beyond the coded fields: colonial A excess 0.20 bits/transition [0.07, 0.33], z 2.96. **Exclusions:** P2 as written and Δ (untestable); P2 (A4) passes as fragile margins; the field control (P4) is uninformative, so K03 may be a leaked field; K03's effect is post hoc confined to the second half and to m ≥ 2; P5 labels and P6 time scale failed; K14 rests on a degenerate null.

## Round 2 redirects (2026-10-09)
- **H145-R1. Field control with A*.** Build operator-topic patterns from nudge and human-message text, so P4 can show that E removes a field that has organismal A*.
- **H145-R2. Resolve the story families.** Split the large communities (hierarchical discovery or a size cap) so verify, consent and onboarding can resolve as their own memeplexes.
- **H145-R3. Test K03 causally.** Read-gate K03's host recruitment (H146) and test its persistence under host wipes (H147, NE41).

## Notes
- 2026-10-09 (coordinator): **reserved-data exposure, disclosed** (`hypotheses/holdout.md`, last item): a qualitative helper read chat in #45–#50 (reserved) for vocabulary baselines. Those periods cannot confirm any vocabulary-based memeplex claim of this card. The #51 tail is untouched. Also: `infra/shared/memeplex.py: clean_commits` drops single-file streams > 200/day, which deletes real Echoes chapter commits (Gemini 2.5 Pro 4,192 → 1,788); fix before any statistic (drop automated-flagged commits and the `surprise-lab-mirror-proofs` loop only).
- 2026-10-09: written by the coordinator from HH392–HH393. Efficient estimators are required (`scratchpad/village_egregore_brief.md`, "Efficient estimators"): integer-encoded counts with `np.bincount`, leave-one-day-out by subtraction, cached pseudo-pattern nulls, sequential stopping. Text is read in memory only; cluster labels are paraphrases.
