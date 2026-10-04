# 13 · Cultural evolution and conventions: naming games, drift, selection and stigmergy

**Fields:** sociophysics, cultural evolution, stat mech, dynamics
**References** (notes in `../../literature/`):
- Centola & Baronchelli 2015, human naming game on networks: `centola-2015-spontaneous-emergence-of-conventions.md`.
- Ashery, Aiello & Baronchelli 2025, LLM naming game, collective bias, committed minorities: `ashery-2025-emergent-social-conventions-llm-populations.md`.
- Heylighen 2016, stigmergy Part I: `heylighen-2016-stigmergy-universal-coordination-mechanism.md`.
- Kolchinsky 2025, selection resolution (used here for the "arbitrary conventions cost −ln s" argument): `kolchinsky-2025-thermodynamics-darwinian-selection-replicators.md`.
- Piñero et al. 2025, neutral cooperative dynamics: `pinero-2025-neutral-theory-cooperative-dynamics.md` (model 06).
- From memory, not in `literature/`: Baronchelli et al. 2006 (minimal naming game, t_conv ∝ N^1.5)†; Xie et al. 2011 (committed minority ≈ 10%)†; Centola et al. 2018 (human tipping ≈ 25%)†; Ewens 1972 (sampling formula)†; Hahn & Bentley 2003 and Bentley et al. 2004/2007 (neutral drift, turnover law)†; Price 1970 (Price equation)†; Boyd & Richerson 1985 (conformist bias)†; Candia et al. 2019 (collective memory decay)†; Deneubourg et al. 1990 (choice function)†; Grassé 1959 (stigmergy)†; Heylighen 2016 Part II (typology)†.

**Related models:** `../06-neutral-cooperative-dynamics/` (species abundances; the neutral null), `../10-potts/` (winner-take-all fixation for q ≥ 3 names), `../03-contagion/` (adoption cascades; complex contagion), `../05-replicator-dissipation/` and `../15-stochastic-thermodynamics-selection/` (selection on repos and terms).

## The model

The degrees of freedom are **cultural traits** carried by agents and by the record: a name for a referent, a file or report convention, a project nickname, a procedure, or a projection of the culture vector. Traits are copied through reads, invented, forgotten and stored in artifacts. Five sub-models describe different aspects.

**1. Naming game (Baronchelli et al. 2006†).** Each agent holds an inventory of names for one referent. At each interaction a speaker utters a name (or invents one if its inventory is empty). On success, both collapse their inventories to that name. On failure, the hearer adds it.
- Mean-field (complete graph): consensus time t_conv ∝ N^1.5 pairwise interactions, i.e. ∝ N^0.5 rounds per agent†. Peak total inventory ∝ N^1.5†.
- 1-D lattice: coarsening with t ∝ N³†. Small worlds behave close to mean-field†.
- Consensus is absorbing (Ashery 2025, fig. S7).
- **Committed minority:** a fraction p of agents always utter name B. Above p_c the population flips from A to B through a saddle-node fold, with hysteresis. Theory gives p_c ≈ 0.10 (binary model†). The human experiment gives ≈ 0.25†. LLM populations give 0.02–0.67 by model, and 0 for a weak incumbent under Llama-3.1 (Ashery 2025).
- **Collective bias:** the population favors one name although first moves are unbiased. The bias lives in the history-conditional response, not in the marginal prior (Ashery 2025: P(M | M,Q; Q,M) = 0.848 vs P(Q | Q,M; M,Q) = 0.451).

**2. Neutral drift with turnover (Hahn & Bentley†).** Each of N carriers copies a random existing trait with probability 1 − μ, or invents a new one with probability μ. Carriers enter and leave.
- Trait popularity follows a power law. The expected number of distinct traits in a sample of n is E[K] = Σ_{i=0}^{n−1} θ/(θ + i), with θ = 2Nμ (Ewens†).
- Turnover of the top-y list per step: z ≈ y√μ (Bentley†; **not checked against the primary source**, see HH314).
- **Conformist bias** (Boyd & Richerson†): Δp = D p(1 − p)(2p − 1). D > 0 lowers turnover below the neutral band. Anti-conformity (D < 0) raises it.

**3. Price equation (Price 1970†).** For a trait z with fitness w (here: the number of agents that adopt from carrier i inside the logged light cone):

$$\bar w\,\Delta\bar z=\mathrm{Cov}(w_i,z_i)+\mathrm{E}(w_i\,\Delta z_i)\;+\;\text{migration}$$

- The covariance term is selection (differential influence). The expectation term is transmission bias (drift of the trait between carrier and copy). The migration term is the roster in/out flow (a project extension; it is not in Price's original form).
- It is an identity. It always holds. The content is in the partition and in which term dominates.

**4. Collective memory decay (Candia et al. 2019†).** Attention to a past period's artifacts and terms has two components. Communicative memory u decays at rate p and transfers to cultural memory v at rate r. Cultural memory decays at rate q:

$$S(t)=u+v,\quad u=N e^{-(p+r)t},\quad v=\frac{Nr}{p+r-q}\Big(e^{-qt}-e^{-(p+r)t}\Big)$$

The result is a biexponential with a fast τ₁ = 1/(p + r) and a slow τ₂ = 1/q. The form is quoted from memory (HH316 refinement).

**5. Stigmergy (Heylighen 2016).** Action → trace → medium → stimulated action. Coordination runs through traces in a shared medium, with no planning, memory or direct communication.
- **Stimulation lift:** λ_ij = P(a_ij | trace of j perceived) / P(a_ij | not perceived). Split into self (own trace) and allo (others' traces).
- **Medium:** an object that ≥ 2 agents both read and wrote.
- **Positive feedback:** recruitment hazard h_j ∝ n_j^β in trace amount; β > 1 is winner-take-all.
- **Choice function** (Deneubourg†): P_A = (k + A)^m / [(k + A)^m + (k + B)^m]. m > 1 gives symmetry breaking and lock-in (a nonlinear Pólya urn).
- **Marker vs work traces** (Part II†): markers are intentional signs (chat links, handoff files). Work traces are the work itself (commits, broken builds). Quantitative traces act by amount; qualitative traces act by state.

### Order and control parameters
| Sub-model | Order parameter | Control parameters in the village |
| --- | --- | --- |
| Naming game | leading-name share m per referent (within room, village-wide); success rate | mixing (cross-room read rate; NE15, NE42, #focus), N, committed share p of reads, memory/context length |
| Neutral drift | top-y turnover z; Ewens K; popularity exponent | innovation rate μ (H34 novel-marker rate per use), carrier turnover (roster) |
| Price | share of Δz̄ from selection vs transmission vs migration | named vs unnamed messages (H29, H50), roster flow |
| Memory decay | τ₁, τ₂, r/(p + r) | veterans present, artifact anchoring, history search access (HH294) |
| Stigmergy | λ_allo / λ_self; loop gain; choice exponent m | artifact-read share of coordinating reads; rooms; goal naming |

## Interesting behavior

- **Well-mixed populations reach one convention; sparse ones freeze.** Humans reach a universal convention by rounds 20–22 in mixed populations (dominant share 96%). Degree-4 networks stall at 30–33% (Centola 2015).
- **LLMs converge in about 15 rounds per agent** with near-deterministic win-stay (99.4%) and lose-shift (97.3%) (Ashery 2025).
- **Collective bias without individual bias.** A population of individually unbiased agents fixes the "strong" name far more often than 50%.
- **Tipping is a fold.** Below p_c the population stays mixed. Above it, the whole population flips. Recovery needs a different threshold (hysteresis).
- **Arbitrary conventions cannot be selected by fitness.** With s → 0, resolving them costs −ln s → ∞ per copy (Kolchinsky 2025). Fixation must come from drift (s ≲ 1/N ≈ 0.03–0.25 here), a field or conformist recruitment.
- **Culture outlives carriers through the record.** Stigmergic traces and the slow memory component persist across full turnover. Only one of the four June 2025 agents remains in September 2026 (HH291).
- **A single agent coordinates with itself.** Re-reading one's own artifact is stigmergy with the medium as external memory (H44, H58).

## Mapping to the village

- **Referents and names:**
  - an artifact (`artifact_mentions.artifact`, DQ4 `work_commits` repo) and the H34 N-class markers (hashed; no text) that co-occur with its URL in `chat_core`;
  - a role, procedure or file convention and its competing labels;
  - village-coined terms: hashed markers with no occurrence in early logs, kickoff text or operator text.
- **Interaction:** the village is broadcast, not pairwise. One call reads every new item in its room (`context_ledger_items` at `call_windows.t_call`). A **population round** is one read of a name-bearing item per agent. Count rounds in per-capita reads, not in days.
- **Success:** a reply (`reply_pairs.parent`, p_reply ≥ 0.5) that reuses the parent's name for the same referent.
- **Population:** N(t) from `roster` and `rooms_timeline`. A room is a well-mixed population; across rooms H41 measures a near-cage (cross-room hazard ≈ 0.001× within-room in #38).
- **Committed sources:** operator and human messages that repeat a term (`kicks_classified`), names hardcoded in an artifact that agents re-read, and the one continuous carrier (Gemini 2.5 Pro, present since 2025-04-24).
- **Culture vector:** DQ5 agent-day vectors (both models, `style_resid_period`); the village centroid minus the composition null (HH293).
- **Price fitness w_i:** adopters inside the logged light cone (H41) whose entry call follows i's use.
- **Memory decay:** references, reads (`artifact_mentions` read verbs) and DQ4 commits to a closed period's artifacts, by veterans vs newcomers of that period.
- **Stigmergy:**
  - medium: `artifacts` (repos, sites, files), chat rooms, history search, HH244's automata;
  - traces: DQ4 agent work commits (work traces), chat links (`artifact_mentions.source == "chat"`) and handoff files (markers);
  - perception: `context_ledger_items` for chat; `artifact_mentions` read verbs and `artifact_commands_text` for artifacts (screens are not logged);
  - actions: next commits, `behavior_states_v3`, `turn_outcomes.failed` for broken states.
- **Natural experiments:** NE15 (#best/#rest split), NE42 (merge then re-split, an A-B-A in topology), #focus (split with hoppers), NE32 (isolated newcomers merged next day), NE29 and other roster exits (carrier loss), the 2026-03-31/04-01 history-search outage (HH294). Identical-kickoff rooms (#36, #37, #39, #40, #42) give field-free divergence tests.

## Identifiability at village sizes

- **N per room is 4–32,** close to the experiments (Centola 24–96; Ashery 24–200). Within a unit, rooms are small and well mixed.
- **Consensus-time exponent across units.** N spans about one decade over 71 units. With a log-scale residual SD of 0.5 per unit and SD(ln N) ≈ 0.6, the slope SE is ≈ 0.5 / (0.6 √71) ≈ 0.10 (a design estimate, not a measurement). That separates 1.5 from 0.5 but not 0.5 from 0.
- **Few clean referents per period.** A naming-game curve needs a referent with ≥ 2 competing names and ≥ 10–20 per-capita reads. Expect a handful per period; use hierarchical partial pooling across referents within a period, and across periods only with shrinkage (exception (d)).
- **Committed-minority thresholds need many flips.** Fit a breakpoint per period. Thresholds range 2–67% for LLMs, so no universal p_c is expected.
- **Neutral drift needs many traits.** H34 markers give thousands of terms per unit, which is enough for turnover and popularity curves within a unit.
- **Memory decay needs long follow-up.** A biexponential needs ≥ 2 decades in time. Periods last about 4 days, and the tail crosses later periods. Held-out days must be masked, which censors the tail; treat masked days as censored, not as zero attention.
- **Price terms:** w_i counts are small (H34 R̂ median 0.22). Report the Price partition with bootstrap over carriers.

## How to fit (or measure)

1. Build a referent × name × call table from hashed markers and `artifact_mentions`, per unit. Drop names that appear in kickoff, goal or operator text.
2. Order uses on the per-call clock. Keep only adoptions inside the logged light cone (entry call ≤ use).
3. **Naming game:** leading-name share vs cumulative per-capita reads; fit an S-curve vs a voter-model null. Consensus time vs N per unit, compared across units on a phase diagram.
4. **Tipping:** agent-level use vs the committed share of exposures; breakpoint vs linear fit.
5. **Drift:** μ from the novel-marker rate per use; turnover z of the top-y list per active day; compare with the neutral band from Wright–Fisher simulation at the real N and μ.
6. **Price:** per carrier, w_i and Δz_i over a window; partition Δz̄; bootstrap.
7. **Memory decay:** single vs biexponential fit by likelihood with censoring; veterans vs newcomers.
8. **Stigmergy:** discrete-time hazard of agent i's first agent-work commit to repo j, with covariates for j's work traces read by i, chat links to j in i's ledger, current share and goal naming.

## Nulls and controls

- **Voter model on the real read sequence:** no acceleration, fixation ∝ N reads. This separates naming-game dynamics from random copying.
- **Neutral (Wright–Fisher) drift** at the measured μ and N: the null for HH314 and HH291.
- **In-flight placebo:** adoptions after a posted-but-unread item at matched lag. Real transmission is read minus in-flight.
- **Room-label permutation** within a period, sizes kept, for regional-dialect claims.
- **Family-matched rooms in other periods** for coinages: rooms with the same family mix coin the same names without contact.
- **Trace covariates permuted across repos within a goal-day** for stigmergy lift.
- **Matched placebo dates** for every event study (carrier loss, outage, merge). Use every same-type boundary of the period.
- **Composition null** for the culture vector: presence-weighted members' personal vectors estimated from other periods (HH293).

## Pitfalls

**The four impostors** (`../../STANDARDS.md` §1):
- **Scheduler field.** Uses burst at day edges because everyone starts together. Count rounds in per-capita reads and use DQ8 trims, or day starts look like adoption waves. Cron jobs replay one script, which is one mechanism, not many adopters.
- **Exogenous field.** Kickoff-named terms show conformist-looking low turnover during their period and collapse at the boundary. Operator messages that repeat a term act as a committed source, but they also respond to agents (H35), so they are not cleanly exogenous. Day-1 content lands on the kickoff (H54: top-1 in 18/33).
- **Shared model priors.** Families coin the same names independently (H07: identical innovations in isolated forks). Ashery's collective bias is a conditional prior: a flat first-use rate does not rule it out, so H13/H46's style-only result cannot settle family effects on conventions. Use first-day and cross-family controls.
- **Contemporaneous convergence.** 75–100% of cross-room adoptions fall outside the logged cone in caged periods (H41). In-flight messages carry a third to a half of exposure effects (H32, H34). Every adoption must sit inside the cone.

**Mapping traps:**
- **A hardcoded artifact name is a committed agent,** not a clean kill for culture. It is re-read on every visit. Test it as a committed-minority effect (HH291 refinement).
- **The continuous carrier.** Gemini 2.5 Pro spans the whole record. Rerun every persistence result without its uses.
- **Rounds are not wall time.** Convert to per-capita reads of name-bearing items before comparing with "15 rounds" or "20–22 rounds".
- **Referents change weekly.** A convention may die because its referent died. Condition survival on the referent's continued use.
- **Chat is a medium too** by Heylighen's definition. "Stigmergy vs communication" rests on the trace classification (work vs marker), not on the channel.
- **Automated commits.** 112k of 192k agent-identity commits are automated (DQ4). Filter them for agent-level stigmergy.
- **Shared repos did not carry cross-room ideas** (H41 lift 1.04). Whether they carry work is open.
- **Narration is a claim.** An agent saying "I adopted X from Y" is not evidence of transmission.

## Hypothesis seeds

- **HH291 · A dialect outlives its coiners.** Survival after the coiner leaves depends on how close the term was to consensus among carriers, not on who coined it. Hardcoded terms tested separately as committed sources.
- **HH303 · Minimum viable carrier population.** Control variable: the share of reads carrying the term vs a rival or a committed source. Fit a saddle-node with hysteresis per period.
- **HH304 · Splits inherit, merges fix.** Regional dialects after NE15 and #focus. Winner-take-all at the NE42 merge, with the winner kept in both rooms after the 05-11 re-split (absorbing state). Report whether the larger room's name (neutral) or the strong family name (collective bias) wins.
- **HH313 · Price equation for village culture.** Style: migration dominates. Content: transmission bias dominates. Selection ≤ 20% of Δz̄, carried by named messages.
- **HH314 · Neutral drift as the dialect null.** Coined terms within the neutral turnover band; kickoff-named terms below it during their period.
- **HH315 · Consensus time vs room size.** Exponent ≤ 0.5 with settling in a few read-out cycles. Kill: an exponent near 1.5.
- **HH316 · Biexponential collective memory.** Fast τ₁ (days) carried by veterans; slow τ₂ (weeks) carried by the record; newcomers contribute only to τ₂.
- **HH301 · Repos recruit hosts by their work traces,** beyond share, chat links and goal naming (Heylighen's quantitative vs work-trace split).
- **HH302 · Maintenance without commitment.** Takeover hazard after a maintainer exits vs matched repos whose maintainers stayed.
- **HH290, HH292, HH293 · Remanence, enculturation, culture beyond composition.** The culture-vector entries; their dynamics belong here, their geometry in model 11.
- **Qualitative stigmergy is repair** (Heylighen notes): P(another agent fixes j within k calls | it read j's broken state) > P(… | it read j in a working state).

**Hypotheses that use this model:** H31 (consensus time vs N; the naming game is a rival scaling), H53 and H28 (nucleation and link-driven herding: marker stigmergy and conformist recruitment), H06 (neutral null), H11 (winner-take-all vs division of labor), H34 and H41 (marker adoption and the light cone that gates transmission), H44, H58 and H70 (single-agent stigmergy: return to one's own artifact), H13 and H46 (shared-prior controls for family conventions).
