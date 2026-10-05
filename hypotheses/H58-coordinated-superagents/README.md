# H58: Effective superagents are coordinated agents plus their artifacts

**Status:** **exploratory round 1 done (2026-10-04, non-holdout only; scope reduced to G51 + G38 replication and three natives, A2.6): no effective superagent beats agent + own artifact.** A new which-artifact unit state, validated on real schedules (power 0.60–0.75 in #51b–d at store strength ρ = 0.5, vs ≤ 5% for H01's binary state; false positives 0.5%), finds no qualifying coordinated unit in the powered #51 units. The one qualifier (#51e) is mutual avoidance, not a store. The #best team of #44 is not a unit. After forced erasures, members return to their *own* artifact (61% vs 54% at placebo calls; joining the group's artifact 1.1% vs 1.2%; first commit, 11,093 erasures), mostly after re-reading it. Confirmatory `analysis/confirm.py` (NE41 re-acquisition, #51 tail, NE24) written and dry-run, **not run**. Level: hypothesis. (Promoted 2026-10-04 from HH176 by Vivian Rogers.)
**Fields:** information theory, statistical mechanics (individuality and autonomy of coarse-grainings), sociophysics (coordination, stigmergy)
**Literature:** [Kolchinsky & Wolpert 2018](../../literature/kolchinsky-2018-semantic-information-autonomous-agency.md) (semantic information, stored vs observed, viability); Krakauer, Bertschinger, Olbrich, Flack & Ay 2020, "The information theory of individuality" (*Theory Biosci.*) and Bertschinger, Olbrich, Ay & Jost 2008, "Autonomy: an information-theoretic perspective" (*BioSystems*): **no notes in `literature/` yet**; their decomposition is used as H01 round 2 states it (F7a), marked † where it matters. Physics model: `physics-models/04-semantic-information`.
**Definitions used** (`physics-models/DEFINITIONS.md`): *superagent (effective, Kolchinsky–Wolpert)* and *allocation continuity ΔC* (H01 round-2 variants); *semantic information (natural-scramble variant)* (H15); *regime*; *agent state*. **New named variants proposed here** (text below, to be added to DEFINITIONS.md by its owner): *unit macro-state (allocation)*, *coordination gain g*, *agent + own artifact (null unit)*, *re-acquisition path*.
**From:** HH176 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` (with HH205, HH222–HH228 as the simulation-side programme) · **Models:** `physics-models/04-semantic-information/`
**Data inputs (shared tables first):** DQ4 work ledger (`work_commits`, agent work only), DQ1 context ledger (`call_windows`, `context_ledger_turns`, `context_ledger_items`), DQ2 `reply_pairs`, DQ3 `behavior_states_v3`, DQ5 `agent_win30_style_resid_period_bge_small`, H34 idea markers (read-only), `artifact_mentions` (re-acquisition reads, intentions), `kicks_classified`, `rooms_timeline`, `ground_truth_labels`, `period_units`, `calendar`. **Not used:** `activity_bins` and `outages` (the activity_bins join bug, coordinator notice 2026-10-04).

## Standards (2026-10-04)
*Documentation pass against `STANDARDS.md`. No analysis was re-run. H58 has no round-1b section; round 1 already ran on the corrected inputs.*

**Question served:** Q3. The card searches for a coordinated unit that beats agent + own artifact, and finds none where it has power. Q4 second: after an erasure the information that survives lives in the agent's own artifact.

| Impostor | Relevant? | How it was handled | Status |
| --- | --- | --- | --- |
| Scheduler field | partly | The gain g scores which artifact, not timing (F5a); L_sync uses H38's edge trim (F7). The unit-recovery dip (P7, β 3.6) is attributed to shared busy timing but not controlled. | partly |
| Exogenous field (kickoff/goal/operator) | yes | Common-field world W_env; activity-matched outside reference and specificity criterion (A1b–A1d); size 0.5% under W_env. The Krakauer environment y omits scheduler, kickoff and prior fields (Erratum). Close by adding `goal_fields` and kickoff inputs to y (§1, row 2). | partly |
| Shared model priors | partly | Labs are a baseline partition (communities beat labs in 0/9 units); the content state uses DQ5 `style_resid`. y omits prior fields (Erratum). | partly |
| Contemporaneous convergence | yes | Same-bin co-allocation may be convergence (A2.6); the outside reference and specificity remove it from the decision rule. Re-acquisition sources have no matched not-yet-read placebo (F9 caveat); the null result does not need one. | partly |

**Inputs:** round 1 uses the DQ4 work ledger, context ledger, DQ2 replies, DQ3 `behavior_states_v3`, DQ5 `style_resid` and H34's markers; it never reads `activity_bins` or `outages`. Still old: the content state uses bge only (no gte). Failures and leading-@ are not inputs.

**Two layers:** 2 replication folders (G51, G38; scope reduced by A2.6). Native tests: 3 (`NE42` mixed by the letter; `G44` failed; `G51g` descriptive).

**Confirm script:** `analysis/confirm.py` exists, dry-run only, built on the corrected inputs (C1–C4). No re-freeze needed. The Krakauer label swap (Erratum) affects names, not estimators.

## Question
Which composite of agents and artifacts best predicts its own future (information-theoretic individuality and autonomy), and is it a set of behaviorally coordinated agents together with the artifact they work on?

**Vivian's scope (2026-10-04):** superagents should be identified by *coordinated behavior*, not by room. Candidate composites come from coordination (behavior-state synchrony, co-adoption, joint work on the same artifact, reply/stance structure), possibly spanning rooms; rooms are only one baseline partition. Builds on H01 round 2 (R4–R8).

**Starting point from H01 round 2 (2026-10-04):** no effective superagent was found among coordination-defined units (crews, synchrony, co-allocation and reply communities; rooms and labs as baselines). Allocation persists across nights and memory loss through artifacts, but single agents with their own artifacts out-persist every grouping (15/18 units), and no unit carries measurable KW semantic information or repairs itself beyond aggregation. The binary "advanced or not" macro-state had ≤ 7% power to see a group store. H58 should (i) use a unit state that encodes *which* artifact is worked on, (ii) search coordination-first over behavior states, co-adoption, reply threads (DQ2) and artifacts together, (iii) treat "agent + own artifact" as the null unit to beat, and (iv) use the context ledger's re-acquisition path after erasures to separate artifact-held from prompt-held information.

## Design: two layers (Vivian, 2026-10-04; see `infra/data-quality/QUEUE.md`)

- **Replication:** the common estimator on every eligible goal period (comparable phase-diagram points). Period README role: `replication`.
- **Period-native tests:** 2–4 goal periods (or NEs) whose setup gives special leverage for this question, each with its own observable, null, ground truth or intervention, its own dated prediction, and period-specific tooling where needed. Period README role: `native`.

## Formal setup (written 2026-10-04, before any real-data outcome)
*What I had seen when writing this (scheme-level counts only, no outcome of any test below):* H01's card and round-2 results; DQ4 agent-work commit counts per H01 unit (182–22,127 commits, 12–27 committing agents, 2–92 repos; 16–63% of agent × 30-min bins contain a commit; 1.0–1.65 repos per committing agent-bin); the top repos and their writer counts in #39–#41 and #44 (in #40 one shared repo has 12 writers and 1,701 commits; in #44 a fine-tuning repo has 5 writers); the file-level distribution of commits in #40's shared repo (one hub file is touched far more than the per-agent landmark files); `behavior_states_v3` coverage (5-min windows, 75–90% labelled per period); the H34 marker table format; the #44 ground-truth kinds (room assignment, checkpoints, leader). No coordination gain, individuality, community, search, re-acquisition or scramble statistic had been computed on real data.

**F0. Claim in Kolchinsky–Wolpert (KW) and Krakauer et al. terms.** A unit G is a set of agents A_G with the artifacts R_G they work on. It is an *effective superagent* if (i) its own state carries information about its members' next moves that each member's own state (including its own artifact) does not (the unit acts on its parts: a group store), specifically for that set of agents (not for any group under a common drive); (ii) as a whole it predicts its own future beyond the environment better than its parts do (organismal individuality†); and (iii) its group-level information is load-bearing under natural scrambles: it survives scrambles of single members (erasures, departures) and the night, and is lost under scrambles of the unit's channel, store or relevance. The **null unit** is H01's persistent individual: **agent + own artifact**, a member whose next artifact is predicted by its own last artifact (carried across bins, erasures and nights) and by artifact popularity. H58 asks whether any coordination-defined composite beats it.

**F1. Time base and units of analysis.** Active 30-min bins of each day's calendar window (variants 15 and 60 min); transitions within a day; the night is a scramble (F8). Units of analysis: H01 round 2's 19 non-holdout units with a work ledger (#30, #31, #33, #35, #36b, #37, #38a–c, #39, #40, #41, #42, #44, #51a–e; ≥ 2 days, ≥ 100 agent work commits, ≥ 4 committing agents). This differs from `period_units` (which splits at every roster join and gives 1-day units): the H01 split is kept for direct comparison with H01's results and because night designs and leave-one-day-out estimation need ≥ 2 days; joins inside a unit are handled by presence masks. Exceptions used: (a) the content clustering is a shared ruler (per regime); (c) NE42, the #focus cut, NE41 and goal boundaries are transition objects; (d) none (no pooling of g across units).

**F2. Primitives.**
- *Work:* DQ4 agent work commits (`canonical & ~imported & author_kind == "agent" & ~automated`), at author time; **artifact = repo**. In native test N1 the artifact is also refined to the file (read-only `git log --name-only` on the bare clones in `data/raw/repos/`; nothing written).
- *Member allocation state* s_i(b): the repo with most of i's commits in bin b (ties: the latest commit), ∅ if none. *Own artifact* ℓ_i(b): i's most recent artifact before bin b + 1, carried across bins, erasures and nights (the artifact-held own state of the null unit).
- *Content state* c_i(b) ∈ {1..6}: k-means cluster (k = 6, per regime, fitted on non-holdout windows) of i's `agent_win30_style_resid_period_bge_small` vector in that 30-min window; none if i wrote no statement.
- *Presence:* any model call (`call_windows.t_call`) in the bin. *Exogenous input* y^h(b): a nudge, human message or goal kickoff (`kicks_classified`) in the bin.
- *Rooms:* `rooms_timeline` (room at bin midpoint); labs from `roster`.

**F3. Candidate units G = (A_G, R_G).** R_G = repos with ≥ 50% of their period commits by members of A_G and ≥ 3 commits (H01's rule, one rule for every coarse-graining). Coarse-grainings:
- **K_sub (the null unit): agent + own artifact**, singletons.
- **K_ml: communities of the multi-layer coordination graph** (F7), plus each layer's own communities (K_sync, K_coad, K_reply, K_coart) for comparison.
- **K_search: direct information-theoretic subset search** (F6).
- Baselines: K_room (time-weighted modal room, ≥ 2 members), K_lab (≥ 2 members), K_vil (all committing agents); random activity-matched groups as the null.

**F4. Unit state (new; "unit macro-state (allocation)").**
- Allocation vector a_G(b) = members' commits per artifact of R_G in bin b, plus "outside R_G".
- Categorical unit state x_G(b) = the artifact of R_G with most member commits (ties: most members), alphabet = R_G's top 4 artifacts + "other R_G" + "outside" + ∅.
- From member i's point of view: o_i(b) = the dominant artifact among the *other* members' commits in bin b (∅ if none): the unit's current allocation as it bears on i.
- Content summary: c_G(b) = modal content cluster of active members; o^c_i(b) likewise from the others.
- Environment y_G(b) = (any non-member commit, a non-member commit on R_G, exogenous input y^h) ∈ {0,1}³.

**F5. Estimators.** All information quantities are **held-out log-loss differences** (bits), leave-one-day-out, from Dirichlet(½)-smoothed count tables fitted on the training days, so alphabet size is paid for out of sample instead of inflating the estimate.
- **(a) Coordination gain g_G (primary; "does the unit beat agent + own artifact?").** For member i's working transitions (s_i(b+1) = k ≠ ∅; transitions into ∅ carry no "which" information and are scored identically by both models):
  - M0 (agent + own artifact): p₀(k) = w_s(c) 1[k = ℓ_i] + (1 − w_s(c)) π^{−ℓ}(k), context c = (ℓ defined; ℓ from today or carried over the night);
  - M1 (unit): p₁(k) = w_s(c, r) 1[k = ℓ_i] + w_j(c, r) 1[k = o_i] + (1 − w_s − w_j) π^{−ℓ,−o}(k), with r = relation of o_i(b) to ℓ_i ∈ {none, same, different};
  - π = training-day artifact frequencies among members' working bins (alphabet R_G ∪ {outside}), renormalized without ℓ (and o); weights from training counts of stay / join / other outcomes per context; pooled over members (relational encoding, so the model size does not grow with the unit).
  - g_G = mean over held-out working member-transitions of log₂ p₁(k)/p₀(k), in bits per working member-bin. It is the transfer entropy from the rest of the unit to member i about *which artifact* i works on next, beyond i's own artifact-held state. Timing is excluded on purpose (H01 tested it). **Content gain** g^c_G: the same model on content clusters (secondary).
  - Night version **g_night**: the first working bin of a day, with o_i = the others' dominant artifact over the previous day's last 2 h, against M0 with ℓ carried over the night.
- **(b) Krakauer decomposition† on the unit state x_G:** colonial A_G = L(x′) − L(x′ | x), organismal A*_G = L(x′ | y) − L(x′ | x, y), environmental E_G = L(x′ | x) − L(x′ | x, y) (held-out log-losses; the "which" part uses the stay/popularity mixture of (a), the ∅ part a table on (x = ∅, y)); individuality ι_G = A*_G / L(x′). Singletons: the same on s_i over own artifacts.
- **(c) Nulls.** (i) *Composition:* 200 random groups of the same size from the unit's committing agents with total commits within ±50% (fallback: the 100 nearest in activity), R recomputed by the same rule: z_comp. (ii) *Member shift:* each member's allocation series rotated within each day by an independent random offset (keeps each member's own artifacts, persistence and daily composition; breaks cross-member alignment), ℓ recomputed, R fixed, 100 draws: z_shift. Under a common environmental drive every group shows a gain, so z_shift alone cannot separate a group store from a common field; z_comp can.
- **Decision rule (per candidate unit):** an *effective-superagent candidate* iff ≥ 2 members, g_G > 0, z_comp ≥ 2 and z_shift ≥ 2. A search result must also pass the search calibration (F6).

**F6. Subset search (bounded).** Objective J(A) = g_A − mean of 20 member-shift surrogates (the coordination excess over each member's own persistence). Greedy forward search from the 10 pairs with the largest J, adding the agent that most raises J, to size ≤ 8; then simulated annealing from the greedy best (add / remove / swap one agent; 400 steps; temperature 0.05 → 0.001 geometric; 3 restarts). **Bounds:** sizes 2–8; at most 20 candidate agents (the most active by commits); at most 3,000 objective evaluations per unit; R_G recomputed for every set. **Selection calibration:** the identical search on 10 surrogate datasets in which every agent's series is rotated within days gives the null distribution of the maximum J; search p = rank of the observed maximum. The final set then gets full nulls (200 composition, 100 shift draws).

**F7. Multi-layer coordination graph (per unit; agents as nodes).**
- **L_sync (behavior-state synchrony):** Pearson correlation of agents' 5-min "working" indicators (`behavior_states_v3.behavior` ∈ {execute_task, debug_recover, verify_report}) after subtracting the cross-agent mean at each 5-min step, inside each day's window where all present agents are running (H38's edge trim); positive part.
- **L_coad (co-adoption):** H34 idea markers used by both agents within the unit (markers used by 2 to N/2 agents), normalized by √(n_i n_j).
- **L_reply (reply threads):** Σ p_reply over DQ2 `reply_pairs` with `pair_set == "cand"` between the two agents, symmetrized, normalized by √(messages_i messages_j).
- **L_coart (joint work):** Jaccard overlap of the two agents' (repo, day) commit sets.
- Each layer scaled to unit total weight; the multi-layer graph is their mean (equal weights); communities by greedy modularity (`r2lib.greedy_modularity`, imported read-only). Rooms spanned by each community are recorded.

**F8. Natural scrambles (KW semantic information, natural-scramble variant) and what each scrambles.**

| scramble | scrambles | level | observable |
| --- | --- | --- | --- |
| NE41 forced erasure of member i (41-turn cap, exogenous timing) | i's session store | member | re-acquisition path (F9); others' compensation; unit coherence |
| memory loss (H15 ML/MG) | i's long-term store | member | descriptive (n small) |
| departure / join (newcomer with an empty store) | one member removed / added | member | newcomer's first artifact = the unit's current one vs popularity |
| night (all members' contexts erased; repos, memory, chat kept) | every member's session store | unit-wide (substrate) | g_night vs g within the day |
| #focus cut (08-05 → 08-24, #51) | the channel between members | unit channel | native N3 |
| NE42 merge (05-04) and split (05-11) | the channel (added, removed) and the store (15 artifacts joined into one) | unit channel + store | native N1 |
| goal change (NE34) | relevance of the unit's state to the environment | unit–environment | does the member set keep its g in the next period? |
| artifact migration (NE24) | the unit's artifact store | unit store | **holdout only** → confirmatory script |

KW proper needs marginal-preserving scrambles; these are erasures, cuts and redraws (H15's departures from KW apply). The value is reported as the change in g (the unit-level information) or in the unit's allocation coherence, never as a KW S or η.

**F9. Re-acquisition path after member erasures (context ledger).** Regime III only (NE41 forced erasures, `context_ledger_turns.reset_forced`). For each forced erasure of member i of a candidate unit at t (the first receiving call after the consolidation), with k_pre = i's last committed artifact in the 60 min before and k_G = the other members' dominant artifact in the 60 min before:
- *Sources in the first 10 calls (≤ 20 min) after the erasure, before i's first commit:* **memory/prompt-held**: the consolidation's own intention (`artifact_mentions` source = intention, nearest as-of join to the CONSOLIDATE) names k_pre (or k_G); **artifact-held**: an executed command reads the artifact (non-write `artifact_mentions` on the repo, any `how`) before the first commit; **peer-held**: a new chat item from a unit member arrives (`context_ledger_items`), or a chat item naming k_pre / k_G (chat `artifact_mentions` by message id).
- *Outcome:* i's first commit within 60 min: on k_pre ("own"), on k_G ≠ k_pre ("group"), or elsewhere.
- *Placebo:* the same agent at mid-segment calls (position ≥ 15 in a context segment, no reset within ±15 min), same definitions. The erasure effect is the difference in P(group) and P(own) between erasures and placebos, by agent-day stratum (Mantel–Haenszel log-OR).
- *Unit recovery:* member i's commits in turns +1…+10 after the erasure vs its agent-day base (H15's dip), and the other members' commits on R_G in [t, t + 15 min] vs placebo times. Buffering β = unit dip / (π_i × member dip); β < 1 means others absorb the loss.

**F10. Rival worlds (synthetic validation and interpretation).** All three are simulated on each unit's **real schedule** (the real agent × bin commit-activity mask), so only *which* artifact is simulated and timing is real:
- **W_store (planted group store):** a group P of m = 3–4 agents shares a persistent store Z(b) over 3 shared artifacts (switch probability 0.15 per bin, kept overnight); an active member of P works on Z(b) with probability ρ, otherwise on its own last artifact. Others as W_own. ρ ∈ {0.2, 0.35, 0.5, 0.7}.
- **W_own (agent + own artifact only):** each agent keeps its last artifact with probability 0.85, otherwise picks among its own 1–2 artifacts, visiting a shared artifact at rate 0.05.
- **W_env (environment-driven allocation):** a common field F(b) over the shared artifacts (same dynamics as Z, partly announced by y^h); every active agent follows it with probability ρ_env = 0.5, otherwise own persistence.

## Model
**From:** `physics-models/04-semantic-information`. The unit is KW's system X with a categorical allocation state (which artifact), the environment is everything outside A_G ∪ R_G; individuality and autonomy are Krakauer et al.'s and Bertschinger et al.'s conditional mutual informations† estimated as held-out log-loss differences; the group store is the coordination gain g (a transfer entropy from the unit's allocation to its members' next allocation beyond their own artifact-held state). Natural scrambles stand in for KW's interventions.

## Data scheme (`scheme/`)
- **Script:** `scheme/build.py` (non-holdout days only; holdout asserted absent in every table).
- **Inputs:** listed in the header.
- **Output:** `data/processed/H58-coordinated-superagents/`: `units.json`, `bins.parquet`, `alloc.parquet` (unit, bin, agent, repo, commits), `presence.parquet`, `content.parquet`, `layers.parquet` (per unit and agent pair: four layer weights), `rooms.parquet`, `erasures.parquet` (forced erasures and placebo calls with their re-acquisition features), `files40.parquet` (N1), `_provenance.json`; results in `results/`.
- **Regimes covered:** I (#30, #31), II (#33, #35), III (#36b–#51e). No forced erasures before 2026-03-24, so F9 is regime III only.

## Observables
g_G, g^c_G, g_night (F5a); A_G, A*_G, E_G, ι_G (F5b); z_comp, z_shift, search p (F5c, F6); communities and rooms spanned (F7); re-acquisition shares and erasure-vs-placebo log-ORs, β (F9); scramble table (F8).

## Null / baseline
The null unit agent + own artifact (M0); composition (random activity-matched groups) and member-shift surrogates; surrogate searches for the selection effect; placebo calls for erasures; W_own and W_env in the synthetic.

## Prediction
*Written 2026-10-04, before running any estimator on real data. The synthetic validation may add a dated amendment before real data.*

| | Card's prediction (operational) | Falsified if | My prior |
| --- | --- | --- | --- |
| **S0** (axis F, synthetic) | On real schedules at real counts: g detects a planted group store (ρ = 0.5, m = 3–4) with power ≥ 0.8 in units with ≥ 40 bins (z_comp ≥ 2 and z_shift ≥ 2); false-positive rate ≤ 0.10 in W_own and W_env; the search recovers the planted members (Jaccard ≥ 0.5) in ≥ 70% of replicates at ρ ≥ 0.5; H01's binary composition z has power ≤ 0.15 on the same worlds | power < 0.5 or size > 0.2 → amend before real data | passes at ρ ≥ 0.5 in the big units; marginal in 3-day units |
| **P1** replication | In ≥ 2/3 of eligible units at least one coordination-defined unit (multi-layer community or search result) is an effective-superagent candidate (F5 decision rule; search p < 0.05 for search results) | ≤ 1/3 of units | fails: candidates in ≤ 1/3 of units, concentrated in shared-artifact weeks (#40, #44, #51) |
| **P2** coordination beats rooms and labs | The multi-layer communities' median z_comp exceeds that of rooms and of labs in ≥ 2/3 of units where both exist | a room or lab partition has the highest median z_comp in ≥ 1/2 | passes against labs, coin flip against rooms |
| **P3** units span rooms | ≥ 1/3 of qualifying candidates in rooms-era units include members of ≥ 2 rooms | < 1/3 | too few candidates to test |
| **P4** the whole beats its parts (Krakauer) | A qualifying unit's organismal ι_G ≥ the commit-weighted mean ι of its members as agent + own artifact, in ≥ 2/3 of qualifying units | < 1/2 | fails: single agents with their own artifacts are more self-determined (H01 R4d) |
| **P5** night | The best unit's g_night > 0 with z_comp ≥ 2 in ≥ 1/2 of units: the unit's allocation information survives every member's session erasure beyond their own artifacts | ≤ 1/4 | fails: nights preserve own artifacts, not group allocation |
| **P6** re-acquisition (NE41) | After forced erasures with k_pre ≠ k_G, the erasure raises P(group) relative to placebo (pooled MH log-OR > 0, z ≥ 2): members re-acquire allocation from the unit | log-OR ≤ 0 or z < 2 | fails: members return to k_pre (artifact- or memory-held); the erasure raises "elsewhere", not "group" |
| **P7** unit recovery | Others' commits on R_G rise after a member's forced erasure (compensation, Stouffer z ≥ 2) and β < 1 (95% CI) | compensation ≤ 0 | fails: β ≈ 1, members don't notice each other's erasures |
| **P8** identity across goal changes | The member sets of qualifying units keep z_comp ≥ 2 on the next period's data in ≥ 1/2 of cases | < 1/4 | fails: goals set coordination (H01: goal change −0.39) |
| **N1** NE42 (#39 → #40 → #41) | The #40 search result has ≥ 4 members and qualifies; no qualifying unit of size ≥ 4 in #39 or #41. At file granularity inside #40's shared repo, g > 0 with z_shift ≥ 2 | #40 has no qualifying unit of size ≥ 4 | #40 qualifies weakly; at file level members mostly keep to their own landmark file (own sub-artifact) |
| **N2** #44 | The search (no room or team labels) returns a set with Jaccard ≥ 0.5 to the #best team (DQ6 room assignment) that qualifies and whose R_G holds the fine-tuning repo; no qualifying unit of size ≥ 3 in #rest | Jaccard < 0.5 or not qualifying | team recovered (co-artifact), qualifies on composition but not shift |
| **N3** #51 #focus cut | Pair coordination gain DiD across the cut (pairs split by the cut vs kept together, 51b → 51c) ≥ −0.5 × the pre-cut mean (coordination is artifact-held and survives a channel cut); qualifying 51c units include both #focus and #general members | DiD < −0.5 × pre mean with CI below | little coordination to lose; DiD ≈ 0, uninformative |

### Amendment A1 (2026-10-04, during the synthetic validation, before any real-data run of g, the search, the Krakauer decomposition or the re-acquisition analysis)
*What I had seen: only synthetic results on real schedules (`analysis/synthetic.py`; the first full run is kept as `results/synthetic_v1.json`) and the scheme-level counts listed in the formal setup, plus the erasure table's counts (events per type; share with a pre-erasure commit, 53–60%; share with a commit in a 10-call window, 16–28%; median 10-call window 2.4 min). No real-data outcome.* Each change below fixed a failure the synthetic exposed:
1. **M1 is join-only.** It keeps M0's stay weight; the unit's allocation enters only through how a member's non-stay move splits between the others' artifact o and everything else. (First version: conditioning the stay weight on the unit's state picked up timing correlations of the real activity mask; W_own crews showed g ≈ +0.015–0.02.)
2. **M0 has member-specific popularity** (each member's own artifact frequencies, shrunk toward the pooled ones with weight 2). With pooled popularity, knowing a co-member's artifact told a member where it would *not* go (the co-member's own repo): a spurious gain under W_own. The null unit is now literally agent + own artifacts.
3. **o is the others' allocation in bins b and b + 1** (co-allocation window, primary). A store read by all members at once moves them in the same bin, which the strictly lagged version misses (power fell at ρ = 0.7). The lagged version (a transfer entropy) is reported as `g_lag`.
4. **Composition null redefined (A1b):** random activity-matched groups of *non-members* evaluated on the *test unit's* R_G, at the matched size k = min(n, active non-members), against the unit's own gain on k-subsets. The original null (random groups with their own R) let a common field through (W_env z_comp 11–26), because random groups rarely own the shared artifacts.
5. **Specificity criterion added:** matched in/out gains, with "others" = k random other members vs k random non-members on the same artifacts; the decision rule requires 1 − g_out,k / g_in,k ≥ 0.5. Unmatched, the search in W_env found village-scale sets (8 of 12–17 agents) whose few remaining outsiders looked weaker, and 32.5% of W_env searches qualified.
6. z_comp (now "z_spec") uses sd = max(sd_comp, sd_shift), because the composition null concentrates at 0 when outsiders never touch R_G.
6b. **(A1c, after the second synthetic run, `results/synthetic_v2.json`)** The search in W_env still qualified in 27.5% of replicates: the found sets were the 7–8 most active agents, and the few remaining outsiders were rarely working, so their "others' artifact" was rarely defined. z_spec and the specificity are therefore computed on the **gain per join-context transition** (g divided by the share of transitions in which the others sit on an artifact different from the member's own), which removes the others' activity from the comparison.
6c. **(A1d)** A unit is **testable** against a common field only if an activity-matched outside reference exists: ≥ 30 activity-matched outsider draws (total commits within ±50% of the unit's, scaled to the matched size) and ≥ 30 distinct outsider groups. Otherwise it cannot qualify ("village-scale: not identifiable against a common field"). This removed the remaining W_env false positives in spot checks; the third run (`results/synthetic.json`) is the one reported below.
7. **Search objective = total held-out bits** (g × transitions, the unit model's log-likelihood gain over the product of agent + own artifact models). Per-transition g selected noisy pairs (winner's curse). Seeds: joint-work crews, multi-layer communities and the 10 best pairs; local add/remove search from each seed, then annealing (temperature in bits). Members with a non-positive held-out contribution are pruned when that costs ≤ max(1 bit, 2%). The shift excess was dropped from the objective for compute; the final set gets both nulls. 19 surrogate searches on real data (p ≤ 0.05 iff the maximum beats all 19); 5 in the synthetic.
8. **P4 as written (ι_G ≥ members' ι) is not specific:** it passes in 60% of W_own and 89% of W_env replicates (aggregation smooths the unit state, H01's problem). It is amended to ι_G above its aggregation baseline (member-shift surrogates, z ≥ 2); both are reported.
9. **P6 outcome window:** until the agent's next reset (≤ 30 min), with the statistic conditional on a commit in the window, since an erasure opens a ~41-call segment while a placebo sits mid-segment. The pre-registered 10-call window (median 2.4 min; a commit in only 16–28% of events) is kept as a variant. Sources are read in the first 10 calls.

### Amendment A2 (2026-10-04, after the synthetic validation, before the replication and native runs)
*What I had seen: the final synthetic run (`results/synthetic.json`, `synthetic_summary.json`; 20 replicates × 6 worlds × 19 unit skeletons, plus 5 search replicates × 3 worlds × 8 units) and the real-data re-acquisition results (`results/reacq.json`; F9 ran under A1 item 9 before this amendment). No coordination gain, community, search or Krakauer statistic on real data.*

**S0 outcome (synthetic, real schedules).** On the same planted worlds the decision rule detects the planted group store, and H01's binary state does not:

| world | g rule qualifies (all / ≥ 40 bins) | H01 binary composition z ≥ 2 | ι above aggregation (z ≥ 2) | night gain z ≥ 2 |
| --- | --- | --- | --- | --- |
| W_own | 0.005 / 0.003 | 0.02 | 0.12 | 0.005 |
| W_env | 0.003 / 0.003 | 0.09 | 0.09 | 0.05 |
| W_store ρ = 0.2 / 0.35 / 0.5 / 0.7 | 0.01 / 0.08 / 0.25 / 0.37 | 0.03 / 0.03 / 0.05 / 0.02 | 0.10 / 0.11 / 0.16 / 0.13 | 0.02 / 0.06 / 0.09 / 0.13 |

Power at ρ = 0.5 depends on the unit's size: 0.60–0.75 in #51b–d (119–335 bins, 26–27 agents), 0.40 in #51a, 0.00–0.35 in the 4–5-day units (36–71 bins); at ρ = 0.7 it is 0.95–1.00 in #51b–d and 0.10–0.45 elsewhere. The calibrated search recovers the planted members (Jaccard ≥ 0.5) in 80% of ρ = 0.5 replicates (median Jaccard 0.67). Its full qualification rate is 25% in W_store, 10% in W_env (4/40) and 5% in W_own (2/40), so a qualifying *search* result alone is weak evidence (A2.4). **S0 as written fails** (power < 0.8 at ρ = 0.5; the size criterion passes easily), so per S0 the following is fixed before real data:
- **A2.1 Powered units.** Verdicts that rest on "no candidate" count as *refuting* only in units with synthetic power ≥ 0.5 at ρ = 0.5 (#51b, #51c, #51d). Elsewhere a null is "not identifiable at this sampling" (as in H01 A1.1), and a pass needs a strong store (ρ ≳ 0.5–0.7). P1's counts are reported over all units and over the powered ones. The false-positive rate per unit is ≈ 0.5% (W_own, W_env), so across ~19 units × ~10 candidates about one chance qualifier is expected; any candidate is checked against the 15/60-min variants.
- **A2.2 P4 and P5 are not identifiable.** The aggregation-baseline individuality test fires in 16% of W_store vs 12% of W_own replicates, and the night gain in 9–13% vs 0.5–5%. They are run and reported but carry no verdict ("not identifiable").
- **A2.3 P4 as written** (ι_G ≥ members' ι) passes in 60–89% of null replicates. It is reported and labelled non-specific.
- **A2.4 Search:** the search result counts only if it also qualifies under the full nulls; the search p (19 surrogates) and recovery are reported. Because the search qualifies in 10% of W_env replicates, a search-only candidate must also qualify in at least one bin-width variant (15 or 60 min) to count.
- **A2.5 (after a one-unit smoke test of the pipeline on #38b, which showed only that half-village communities were untestable; no gain or z was read):** the matched outsider size is the largest k ≤ min(n, outsiders) with ≥ 10 distinct outsider groups (was: k = min(n, outsiders) with ≥ 30 groups, which made a 6-member community in a 12-agent unit untestable). The synthetic was rerun with this rule (`results/synthetic.json`, v4; v3 kept): the decision-rule rates above are unchanged to two decimals except W_env search 0% → 10%.
- **A2.6 Scope (coordinator, 2026-10-04, compute scarce):** replication is run on **G51** (51a–e; the only powered period) and **G38** (38a–c; the best-powered 5-plus-day non-#51 period, 0.35 in 38a); natives NE42 (#39–#41), G44 and G51g. The other H01 units (#30–#37, #42) are not run in this round. Read-out lesson from round 1b (`writeup/round1b-synthesis`): co-allocation in the same bin can be convergence on a shared field rather than coupling; the outside-reference null and specificity are the controls for that here, and the re-acquisition sources are interpreted with the in-flight caveat (a peer item read before a switch is not evidence of copying without a matched not-yet-read placebo).

**Overall prior (2026-10-04).** The richer state will show *some* coordination where agents share an artifact (#40, #44, #51's shared infrastructure), mostly as co-allocation driven by the goal and the shared artifact's popularity, which random groups in the same week partly share. I expect the agent + own artifact null to remain hard to beat: members re-acquire their own last artifact after erasures and nights, and the unit adds little. If a candidate appears, I expect it in #44's #best team or #40.

**Multiplicity.** The verdicts are S0, P1–P8 and N1–N3. Per-unit p-values, layer-specific communities, variants (15/60-min bins, attention state, content gain) are descriptive. About 19 units × several candidates are tested; the synthetic W_own false-positive rate per unit is reported next to the counts.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness". Mapping: units = agents + the repos they own (≥ 50% of commits); state = which repo each member advances per 30-min bin; windows = G51 (51a–e), G38 (38a–c), and the natives (#39–#41, #44, #51 #focus).
**Rival models:** W_own (agent + own artifact), W_env (environment-driven allocation), W_store (group store); rooms and labs as baseline partitions.
**Locked holdout used for confirmation:** none yet. Planned: `analysis/confirm.py` (C1–C4: NE41 re-acquisition in #45–#50 and the #51 tail, replication in the holdout units, NE24 artifact migration). Written and dry-run, not run.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | State, units, layers, erasures and sources all come from logged fields (DQ4 commits, DQ1 ledger, DQ2 replies, DQ3 states, H34 markers). Repo granularity hides within-repo division of labour (the file-level variant exists only for #40). The ledger counts commits, not value. Regimes I/II not run this round. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Leave-one-day-out held-out log-loss guards against overfitting. First-order relational kernel; within-unit stationarity is assumed, not tested. 15/60-min bin variants agree for the only qualifier. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Day-blocked held-out gains against the agent + own artifact model, member-shift surrogates, an outside reference and specificity. Large search sets beat the shift null and show attraction (joins 1.8–4.5× expected) but not the outside reference: a shared field. No unit beats every null in the powered units. |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | The superagent signatures (unit individuality above aggregation, night gain) are not identifiable at this sampling (A2.2). The attraction diagnostic is post hoc (A3). |
| E interventional | predicts the change across a natural experiment | 1 | NE41 (exogenous erasure timing): erasure raises the return to the member's own artifact (MH log-OR +0.25, z 8.0, unconditional) and not the move to the group's (+0.19, z 1.5). NE42 and the #focus cut show no unit on either side (nothing to move). |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Real-schedule synthetic (2,400 replicates): size 0.5%; power 0.60–0.75 in #51b–d at ρ = 0.5, ≤ 0.35 elsewhere; the search recovers planted members (Jaccard ≥ 0.5) in 80%. H01's binary state: ≤ 5%. Missed: the gain also rewards avoidance (found on real data; A3). |
| G ground truth | agrees with known structure | 1 | Synthetic planted groups recovered. The known #44 team is not a unit in its allocation (each member keeps to its own memory and fine-tuning repos), which may be the truth rather than a miss. |
| H comparative | beats the named rivals | 1 | W_own wins in the powered units. W_env-like attraction (shared field) explains the large-set co-allocation. W_store is not needed anywhere. |
| I transfer | holds in other same-mode periods, including the holdout | 1 | Same picture in all eight replication units and three natives; re-acquisition holds in every regime-III unit with events. Holdout not used. |

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication | mixed (by the letter; substantively failed) | powered 51b–d: 0 qualifying units; 51e qualifier is avoidance (0 joins); forced erasures: own 0.63–0.78, group ≤ 0.02 |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | n/a | no qualifying multi-layer or search unit; power ≤ 0.35 (not identifiable) |
| [NE42](goalperiod-subhypotheses/NE42/README.md) | native | mixed (by the letter) | no qualifying unit in #39, #40 or #41; #40 file level: the hub file takes 55% of working bins, agents keep 75% on their own file |
| [G44](goalperiod-subhypotheses/G44/README.md) | native | failed | #best team g −0.053 (z_spec −2.3); search Jaccard with the team 0.12; a #rest crew qualifies |
| [G51g](goalperiod-subhypotheses/G51g/README.md) | native | descriptive | split pairs had no coordination to lose (pre −0.008); DiD −0.008 [−0.029, +0.013] |

## Results
*Exploratory round 1, 2026-10-04, non-holdout only. Scripts: `scheme/build.py`; `analysis/{h58lib,h58data,synthetic,summarize_synth,run,summarize_real,attraction,reacq,natives,period_folders,figures,estimates_rows,confirm}.py`. Numbers: `data/processed/H58-coordinated-superagents/results/` (`synthetic*.json`, `units/*.json`, `replication.json`, `attraction.json`, `reacq.json`, `reacq_events.parquet`, `natives.json`, `period_verdicts.json`, `confirm_dryrun.json`). Shared estimates: 37 rows, `per_period_estimates.parquet` (hypothesis H58). Figures: `figures/synthetic_validation.pdf`, `replication.pdf`, `reacq.pdf`, `summary_obs.pdf`, `summary_synthetic.pdf`.*

**Headline.** With a unit state that encodes *which* artifact each member advances, the null unit **agent + own artifact** is still not beaten.
- In the units where the method has power (#51b–d), no coordination-defined composite (multi-layer communities, single-layer communities, joint-work crews or the calibrated search) is an effective superagent.
- Agents do co-allocate in large sets: the 8-member search sets join each other's artifacts 1.8–4.5× more often than their own histories predict. Outsiders on the same artifacts do it as much, though, so this is a shared field or convergence, not a group store.
- The single qualifier (#51e) is three agents who *avoid* each other's repos.
- After an exogenous context erasure, members go back to their own artifact more often than at placebo calls, usually after re-reading it. They do not move to where the group is.

**Synthetic validation (axis F; A2).** On each unit's real activity mask, with only *which* repo simulated, the decision rule:
- detects a planted group store with power 0.01 / 0.08 / 0.25 / 0.37 at ρ = 0.2 / 0.35 / 0.5 / 0.7 overall, and 0.60–0.75 (ρ = 0.5) and 0.95–1.00 (ρ = 0.7) in #51b–d;
- has false-positive rates of 0.5% in W_own and 0.5% in W_env;
- compares with 2–5% for H01's binary-state composition z on the same worlds, i.e. no power.

The search recovers ≥ half of the planted members in 80% of ρ = 0.5 replicates, but its full qualification rate is only 25% there, against 10% in W_env and 5% in W_own. The unit-individuality and night tests are not identifiable (16% vs 12%; 9–13% vs 0.5–5%). It took four synthetic rounds (A1, A1b–d, A2.5) to remove common-field false positives.

**Outcome vs prediction**

| | Prediction (locked; A1–A2) | Outcome | Verdict |
| --- | --- | --- | --- |
| S0 | power ≥ 0.8 at ρ = 0.5 in units ≥ 40 bins; size ≤ 0.10; search Jaccard ≥ 0.5 in ≥ 70%; binary ≤ 0.15 | power 0.25 overall, 0.60–0.75 in #51b–d; size 0.005; Jaccard ≥ 0.5 in 80%; binary 0.02–0.05 | **failed as written** (power); amended A2.1 |
| P1 | a candidate in ≥ 2/3 of units | 1/12 units run (8 replication units: 1/8; powered 0/3); the one (#51e) is avoidance (A3) | **failed** |
| P2 | multi-layer communities above rooms and labs in ≥ 2/3 | above rooms in 3/6 units, above labs in 0/9 | **failed** |
| P3 | candidates span rooms | no qualifying multi-room-era candidate | untestable |
| P4 | ι_G ≥ members' ι (amended: above aggregation) | 0/1 and 0/1 | not identifiable (A2.2) |
| P5 | night gain of the best unit | 0/6 | not identifiable (A2.2) |
| P6 | erasure raises P(group) vs placebo (z ≥ 2) | conditional MH log-OR +0.19 (z 1.5; 6,382 vs 8,520 events); own −0.03 (z −0.5); unconditional own +0.25 (z 8.0) | **failed** (members return to their own artifact) |
| P7 | others compensate (z ≥ 2), β < 1 | others' commits on R_G −0.60 per 15 min (−5.7%, z −5.9); member −0.23 (−13%); β 3.6 [2.8, 4.4] | **failed** (others dip too) |
| P8 | qualifying sets keep their gain next period | no evaluable set (#51e has no next period) | untestable |
| N1 NE42 | #40 unit of ≥ 4 qualifies, none in #39/#41; file-level g > 0, z_shift ≥ 2 | no unit anywhere; file-level search g +0.13, z_shift 2.5, but untestable against outsiders, specificity −0.98, search p 0.55 | **mixed by the letter**, substantively failed |
| N2 #44 | search ≈ #best team (Jaccard ≥ 0.5) and qualifies; nothing in #rest | Jaccard 0.12; team g −0.053 (z_spec −2.3); a 5-agent #rest crew qualifies (4 joins vs 1.4 expected) | **failed** |
| N3 #focus | DiD ≥ −0.5 × pre mean | pre mean of split pairs −0.008 (nothing to lose); DiD −0.008 [−0.029, +0.013] | **descriptive** |

**Candidate units vs agent + own artifact.** Medians of the composition z of the multi-layer communities are *negative* in 9/10 units where defined (−0.5 to −3.0): coordination-defined communities co-allocate *less* than activity-matched outsiders on the same artifacts. The large search sets (8 members in #41 and #51b–d; 5 in #38a–c and #44) collect the agents who share popular artifacts. They beat the member-shift null (z_shift 3–8) and show real attraction (A3). They fail the outside reference or specificity, i.e. outsiders on those artifacts co-move just as much. Single agents with their own artifacts have positive self-persistence (median colonial 0.05–0.28 bits per bin in #38 and #51).

**Kolchinsky–Wolpert semantic information by scramble type (natural-scramble variant; no KW S or η is claimed).**

| scramble | level | what happened to the unit's allocation information |
| --- | --- | --- |
| NE41 forced erasure of one member (21,043 events) | member session store | the member returns to its own artifact (P(own) up, log-OR +0.25, z 8); P(group) unchanged; its commits −13% for 15 min; others on its unit's artifacts also −5.7% (shared timing, not a cost passed on) |
| voluntary consolidation (15,812) | member, self-timed | own +0.22 (z 3.2, conditional); group −0.07 (z −0.6) |
| night (all members) | substrate-wide | night gain of the best unit > 0 with z ≥ 2 in 0/6; not identifiable (A2.2); H01's own-artifact continuity stands |
| departures / joins | member | not run separately this round. The NE33 newcomer GPT-6 Astra sits in the #51e avoidance set (it keeps to its own new repo) |
| #focus cut | unit channel | nothing to lose (pre −0.008); DiD −0.008 [−0.029, +0.013] |
| NE42 merge / split | channel + store | no unit on either side; in the merged store agents keep 75% of their work on their own file |
| goal change | relevance | P8 untestable (no unit to carry over) |
| artifact migration NE24 | unit store | holdout only → `confirm.py` C4 |

So the unit-level semantic information is ≈ 0 for every scramble we can see. The information that survives a member's erasure is in that member's own artifact (and, less often, its own intention note), not in the group.

**Re-acquisition path after member erasures (F9; 11,093 forced erasures with a pre-erasure artifact).**
- **Where they go.** First commits before the next reset go to the member's own artifact in 61% of forced erasures (placebo 54%), to the group's artifact in 1.1% (1.2%), elsewhere in 6% (10%), and none in 32% (35%).
- **What precedes a return to its own artifact.** The member touches that artifact in an executed command before its first commit in 50% of cases (placebo 33%). Its consolidation intention names it in 15% (14%). A chat item naming it arrives in 4% (2%).
- **Conditional return rates.** Returning is more likely when the artifact was re-read (0.96 vs 0.85 without) or named in the intention (0.96 vs 0.89), and not when a peer named it (0.89 vs 0.90) or a member's message arrived (0.89 vs 0.92).
- **The rare moves to the group's artifact** are preceded by reading that artifact (51%), not by peer chat (12%).
- **Reading:** allocation after an erasure is **artifact-held** (re-read) and partly **prompt- or memory-held** (the intention note). It is not **peer-held**.
- **In-flight caveat (round 1b, lesson 3).** A member's message arriving in the first post-reset calls is common (80%, vs 48% at placebo calls). This is the consolidation backlog (known issue), and it predicts nothing; no matched not-yet-read placebo was needed for a null.
- **Unit recovery.** The member's dip (−13% commits in 15 min) is not absorbed by the others: their commits on the unit's artifacts also fall (−5.7%, β 3.6). The likely cause is shared timing, since forced erasures fall in busy stretches for everyone. It is not compensation.

**What it means.** The richer state removes H01's main excuse (≤ 7% power): where the method can see a group store of moderate strength, there is none. In KW and Krakauer terms, the self-determined unit in the village is the agent plus its own artifact. That artifact is a stigmergic memory the agent re-reads after each erasure. Above it, co-allocation is environmentally determined (a shared field over popular artifacts), not organismal. Teams with a known shared artifact (#44) still work in their own repos. **These are not effective superagents; at most they are agents that happen to share a workspace.**

**Caveats.**
- Power exists only in #51b–d (8-h days, 25+ agents). Elsewhere a store of ρ ≲ 0.5 would be missed, and natives NE42 and #44 are underpowered (0.15–0.35).
- The gain g rewards avoidance as well as attraction (found after the run; A3 diagnostic post hoc). Round 2 should require attraction in the decision rule.
- Artifact = repo. Division of labour inside one repo (files) is visible only in #40.
- Commits are attempts, not value; non-git work is invisible.
- Erasure outcome windows end at the next reset (erasures open a fresh ~41-call segment, placebos sit mid-segment). The conditional statistic is primary for that reason; the unconditional own effect partly reflects the longer window.
- "Reads" are artifact mentions in executed commands (any `how`, including `cwd`, 0.81–0.89 precision), not file-level reads.
- Scope was reduced (A2.6): #30–#37 and #42 were not run.
- Many candidates were tested per unit; the per-unit rate of chance qualifiers is ≈ 0.5% (synthetic).

## Confirmatory design (written 2026-10-04 after exploration; frozen in `analysis/confirm.py`, dry-run only, NOT RUN)
- **C1** NE41 re-acquisition in the holdout regime-III units (#45–#50, #51 tail): the group MH log-OR z < 2 and the own log-OR > −0.2.
- **C2** Others' commits after a member's forced erasure: estimate ≤ 0, z < 2.
- **C3** Replication: units with a candidate ≤ 1/3, counted as refuting only in units with ≥ 100 bins (#51 tail).
- **C4** NE24 (GitHub → GitLab, #50): ≥ 50% of agents continue their own repo's name stem on GitLab within 3 active days, and no pre-migration community qualifies afterwards.

Reuse: H01 `confirm_r2.py` targets NE24 with crew re-formation, a different statistic. The run must be disclosed in both cards and LOG.md, the script committed first, and `holdout_ledger.check()` called (the script does this).

## Round 2 redirects (2026-10-04)
- **H58-R1. Attraction, not gain.** Make the decision rule require attraction (joins above the agent + own artifact expectation) and model avoidance explicitly: territoriality (members partitioning artifacts) is itself a coordinated state, and possibly the village's real division-of-labour signature (H11's Potts labour vs herding).
- **H58-R2. Within-repo allocation.** File-level states from the bare clones for every shared repo (#40 shows "own file in a shared container"). A store could live at file or issue level.
- **H58-R3. The agent + own artifact pair as the KW agent.** Its stored semantic information about the goal and other agents, from erasure re-acquisition (which file is re-read) with an in-flight placebo at matched lag.
- **H58-R4. Run the powered holdout** (#51 tail) through `confirm.py`.

- **Egregore revamp (coordinator, 2026-10-04):** the null for coordination-defined superagents moves the search to the stigmergic layer and to culture. See HH290–HH306 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` ("Egregores and collective information dynamics"), especially HH293 (culture beyond composition), HH290 (remanence), HH296 (autonomy across scales with the round-1b impostors as environment) and HH301 (repos recruit hosts).

## Round 2 (2026-10-05): attraction vs territoriality, file-level allocation, the pair as the KW agent
*Scope: H58-R1, R2 and R3. R4 (reserved data) is not part of this round. Non-reserved data only (`holdout_mask`, asserted in every script). Round-1 scripts and outputs are unchanged. Round 2 lives in new scripts (`scheme/build_r2.py`, `analysis/r2lib58.py`, `analysis/r2_synthetic.py`, `analysis/r2_run.py`, `analysis/r2_reacq.py`, `analysis/r2_rows.py`, `analysis/r2_figures.py`) and writes to `data/processed/H58-coordinated-superagents/r2/`. New code imports nothing from another hypothesis folder (round-1 `h58lib` still imports H01's `r2lib`; round 2 does not use it). Shared code: `infra/shared/semantic_kappa.py`, `infra/shared/estimates.py`, `infra/shared/common.py`.*

### Round 2 design, predictions and kill rules
*Written 2026-10-05 04:25 UTC, before any round-2 statistic on real data.* What I had seen: every round-1 result, including the post hoc attraction diagnostic (A3: search sets join 1.8–4.5× their expectation; #51e has 0 joins in 3 moves), so P-R1a is informed by round 1. New scheme-level facts (no outcome): shared repos (≥ 2 agent writers with ≥ 3 commits each) per unit: 38a 5, 38b 2, 38c 2, 39 0, 40 1, 41 9, 44 8, 51a 4, 51b 16, 51c 12, 51d 9, 51e 4, all with bare clones; over the 73 shared repos with ≥ 30 commits (40,988 agent work commits), 9.1% of commit subjects reference an issue, the median commit touches 1 file (54% exactly one, 3.5% more than 20); every round-1 erasure row maps to a `calls` row; `turn_outcomes.cmd` holds the command text of 900,968 regime-III action rows. Round-2 context from other cards (read only): H11 R2 (herding is chat-steered same-hour co-arrival; a shared project grows as n^0.7), H44 R2 and H15 R2 (re-reading after a wipe is working-set habit; first reads carry ~4% of the dip), H05 R2 (rooms partition artifacts).

**Units.** R1 and R2: the round-1 replication units (38a–c, 51a–e) and native units (39, 40, 41, 44). R3: every regime-III unit with erasures (36b, 37, 38a–c, 39–42, 44, 51a–e), grouped by goal period for reporting. Fits stay within units (CLAUDE.md); NE41 pooled fits use agent × unit strata (exception (c), each erasure is a transition object).

**R1. Attraction, not gain; territoriality modelled.**
- *Candidates.* Every round-1 candidate set of the 12 units (multi-layer and single-layer communities, joint-work crews, the calibrated search set, rooms, labs), read from `results/units/<u>.json`. No new search (compute; the round-1 search already maximised co-allocation bits).
- *Attraction Λ (new; "occupied-set attraction").* Member j's moves: within-day transitions b → b+1 with s_j(b+1) = k ≥ 0, own last artifact ℓ_j defined (carried across bins and nights) and k ≠ ℓ_j. Reference set Q (co-members, or outsiders): O_j(b) = artifacts on which some agent of Q works in bin b or b+1, minus ℓ_j. A move is in join context if O_j(b) ≠ ∅; a join if k ∈ O_j(b). Expected join probability under the null unit (agent + own artifacts): Σ_{o∈O} π_j(o) / (1 − π_j(ℓ_j)), with π_j member j's leave-one-day-out artifact frequencies on the unit's full repo alphabet, shrunk toward the pooled frequencies of all the unit's agents (weight 2). Λ = Σ joins / Σ expected. Λ > 1 is attraction; Λ < 1 is avoidance.
- *A-rule (replaces round 1's g rule).* A unit is an **attraction candidate** iff n ≥ 2, ≥ 10 join-context moves, Λ_in > 1 (Q = co-members), z_shift ≥ 2 (Λ_in against 100 within-day rotations of each member's row), and an outside reference exists and is beaten. Outside reference: for each member, Q = k random co-members (Λ_in,k) vs k random activity-matched outsiders (Λ_out,k; total commits within ±50%, ≥ 30 matched draws, else "untestable"), k = min(n − 1, outsiders); z_out = (Λ_in,k − mean Λ_out,k) / sd ≥ 2 (sd floor: the shift sd) and specificity 1 − (Λ_out,k − 1)/(Λ_in,k − 1) ≥ 0.5.
- *Territoriality T (new; "exclusion on shared artifacts").* For a set of agents: eligible pair-bins = two agents both working in bin b who both worked on some common artifact that day. C = share of eligible pair-bins in which the two are on the same artifact. T = 1 − C_obs / mean C_rot, with C_rot from 100 within-day rotations of every member's row (matched activity: each agent keeps its own bins' count and its daily artifact set). T > 0: members keep off the artifact a co-member is on (exclusion, turn-taking). T < 0: they co-work.
- *T-rule.* A unit is a **territorial candidate** iff T > 0, z_rot ≥ 2 (C_obs below the rotation distribution), ≥ 30 eligible pair-bins, and T beats the **random-partition reference**: T of random groups of the same size drawn from the unit's committing agents with total commits within ±50% (≥ 30 draws), z_part ≥ 2. If random groups exclude each other as much, the exclusion is a village property, not a group state.
- *Village level.* Λ_V (each agent's moves onto artifacts any other agent occupies) and T_V (all committing agents), each against rotations: one point per unit on a herding (Λ_V > 1, T_V < 0) vs territorial axis.
- *Static partition (descriptive).* The share of each agent's commits on repos it holds ≥ 50% of, against a random partition (agents keep their commit counts and number of distinct repos; repos drawn by pooled popularity). The synthetic W_own is expected to pass this test, so it marks the null unit, not coordination.
- **P-R1a (no attraction store; prior 0.8):** no candidate in the powered units (#51b–d) passes the A-rule. The large search sets show Λ_in > 1 with z_shift ≥ 2 and fail the outside reference. *Against:* ≥ 1 candidate in 51b–d passes the A-rule and also in a 15- or 60-min variant. The negative counts only at the store strength ρ where the A-rule's synthetic power is ≥ 0.8 in that unit.
- **P-R1b (village herding; prior 0.6):** Λ_V > 1 and T_V < 0, both with |z_rot| ≥ 2, in ≥ 2/3 of the 12 units (co-allocation onto shared artifacts beyond rotation, as H11 R2 found for arrivals). *Against:* T_V ≥ 0 or Λ_V ≤ 1 in ≥ 1/2 of units.
- **P-R1c (territoriality is a group state; prior 0.25):** ≥ 1 territorial candidate in ≥ 2 of the 3 powered units. **Kill** ("territoriality is not a coordinated group state"): no territorial candidate in 51b–d, with T-rule synthetic power ≥ 0.8 at exclusion strength θ = 0.9.
- **P-R1d (#51e; prior 0.4):** round 1's #51e qualifier (3 agents) is a territorial candidate and not an attraction candidate. Two days of data; reported, not decisive.

**R2. Within-repo (file-level) allocation.**
- *Objects.* Each (unit, shared repo) with ≥ 2 writers of ≥ 3 commits and ≥ 30 agent work commits in the unit (units as in R1). File lists from read-only `git log --all --name-only` on the bare clones; file key = full path; commits touching > 20 files are dropped (bulk). Writer-bin state = the file with most touches in the writer's commits to that repo in the bin (ties: the latest commit); −1 when the writer does not commit to the repo in that bin.
- *R2a static partition.* Exclusivity E = share of file-touches on files with one writer; own-file share = share of a writer's touches on files where it has the most touches. Random partition at matched activity: each writer keeps its touch count and number of distinct files, files drawn by the repo's file popularity without replacement within writer (200 draws): z_E.
- *R2b file-level store.* Λ_file (the attraction statistic with files as artifacts and the repo's writers as members) against rotations; T_file (exclusion) against rotations. A **file-level co-allocation repo** has Λ_file > 1 with z_shift ≥ 2. There is no outside reference at file level (outsiders do not touch the repo's files), so a positive reads "store or file-level field". Pooled: Stouffer of the per-repo z_shift, weighted by √(join-context moves).
- *Issue level.* Only repos with ≥ 30% issue-referenced commit subjects (issue numbers parsed in memory, never stored with text); expected: none qualify ("not measurable").
- **P-R2a (own file in a shared container; prior 0.8):** E above the random partition (z_E ≥ 2) in ≥ 2/3 of eligible repos. This describes structure; independent file owners pass it too (checked in the synthetic).
- **P-R2b (no file-level store; prior 0.6):** Λ_file z_shift < 2 in ≥ 2/3 of eligible repos and pooled Stouffer z < 2. *Against:* ≥ 1/3 of repos with Λ_file > 1 and z_shift ≥ 2, or pooled z ≥ 2. The negative needs pooled synthetic power ≥ 0.8 at a planted file store of ρ = 0.5.
- **P-R2c (file-level exclusion; prior 0.4):** T_file > 0 with z_rot ≥ 2 in ≥ 1/3 of eligible repos (writers keep off the file a co-writer edits in the same bin).

**R3. The agent + own-artifact pair as the Kolchinsky–Wolpert agent.**
- *Events.* Round 1's erasure table: forced erasures F (NE41) and placebo calls P (call 20 of a segment, no reset in the next 10 calls); voluntary consolidations as a variant. Own artifact A = k_pre (the repo of the last work commit ≤ 60 min before). Calls 1–10 / 1–20 = the event call and the next 9 / 19 calls of the agent-day (`calls.seq`), truncated at the next reset.
- *File codes (agent-relative, 8 symbols).* From A's git history up to the event: r1, r2, r3 = the files of A the agent committed most recently, first to third; r45 = fourth or fifth; own-old = an older file the agent committed; oth = a file of A the agent never committed (others' files); xrepo = another repo; none.
- *Re-read pointer S.* The code of the first file of A read in calls 1–10. Read = an action row of a read verb (cat, head, tail, less, more, sed -n, grep/rg, wc, diff, git show/diff/log/blame, ls, find) without write evidence (`turn_outcomes` file_write, commit_ok, push_ok), mapped to the agent's latest call at or before it. Tokens = path-like strings in `cmd`, matched to A's files by their last two path components, else by a unique basename. Nothing but codes is stored.
- *Outcome X.* The code of the agent's first work commit in calls 1–20 (≤ 30 min): its touched file with the smallest code; xrepo if on another repo; none. V = work commits in calls 1–20 (`calls.n_work`); V_pre = calls −20…−1.
- *Channel classes:* open_own = S ∈ {r1…own-old} (re-read its own files), open_oth = S = oth (re-read others' files in its artifact), open_goal = a read in calls 1–10 of a goal or coordination document in any repo (basename contains readme, todo, task, plan, roadmap, status, handoff, goal, agenda, backlog, contributing, coordination, claim or assign).
- *κ rows* (`semantic_kappa.kappa_row`; cluster = agent-day, stratum = agent × unit): one row per class, S = the event's S if the class holds, else none; X as above. Report I, I_ci, the jackknife interval, `identified`, `I_sparse`, dV_rel, κ. Pooled (NE41) and per goal period.
- *In-flight placebo at matched lag.* (a) I_P = I(X; S) on placebo events, re-weighted (resampled within agent × unit) to the forced events' distribution of first-read call (1–2, 3–5, 6–10, none); ΔI = I_F − I_P, agent-day cluster bootstrap (B = 200). (b) Read vs posted-but-unread: Y = 1[X = r1] among events with a commit. The last-written file r1 sits in the artifact whether or not the agent reads it. Interaction = log-OR(read r1 vs r1 unread | F) − the same | P, each Mantel–Haenszel over agents, CI from the agent-day cluster bootstrap. A positive interaction means the erasure makes the read predictive (re-acquisition); zero means the read is the ordinary working loop (habit).
- *Stored allocation information of the pair.* I_store = Σ_x p(x) log₂ p(x)/p̃(x), with p the code distribution of X on F events and p̃ the distribution when X is coded against the same agent's artifact state from a different event ≥ 1 day earlier or later in the same unit (a time-shifted artifact; the natural scramble of the artifact state). The same on P events. I_store(F) is the "which file" information that survives the loss of the context because it sits in the pair's artifact.
- **P-R3a (the artifact holds it; prior 0.7):** I_store(F) > 0.1 bits with CI > 0, and I_store(F) / I_store(P) ≥ 0.8. *Against:* ratio < 0.5 (the context, not the artifact, held the allocation).
- **P-R3b (re-reading re-acquires; the redirect's claim; prior 0.3):** read × F interaction > 0 (CI > 0). **Kill:** CI includes 0 with synthetic power ≥ 0.8 at an interaction of log-OR 0.5: re-reading is habit, not re-acquisition.
- **P-R3c (in-flight; prior 0.6):** ΔI at matched lag has a CI that includes 0: the re-read file tells no more about the next file after an erasure than mid-segment.
- **P-R3d (κ; prior 0.5 own, 0.7 others/goal):** the own-file row is identified with dV_rel > 0 (CI); the others' file and goal-document rows are not identified or have dV CIs that include 0. The pair holds identifiable semantic information about its own task state, not about other agents or the goal.

**Synthetic validation first (axis F).** R1 on each unit's real activity mask (as round 1): W_own, W_env (ρ_env 0.5), W_store (ρ 0.35, 0.5, 0.7) and a new **W_terr**: a planted group P (m = 3, or 4 in units with ≥ 15 agents) shares a pool of 3 artifacts; an active member works on the pool with probability 0.7 (else own persistence), stays on its pool artifact with probability 0.6, and a choice that lands on an artifact another P member holds in that bin is redrawn among free pool artifacts with probability θ ∈ {0.5, 0.9} (agents processed in random order within a bin). 20 replicates per world and unit; test group as round 1 (P where planted). Round 1's g rule is run on W_terr too, to measure its avoidance leak. R2 on each shared repo's real writer × bin mask: own-file persistence, a planted file store (ρ_file 0.5) and planted file exclusion. R3 on the real F/P skeleton: X permuted within stratum (null), X := S with probability q ∈ {0.05, 0.1, 0.2}, a planted read × F interaction (log-OR 0.5, 1.0) on Y, planted dV_rel 0.15. A statistic is read only where its synthetic size is ≤ 0.10; every negative carries its power.

**Impostors (round 2).** Scheduler field: Λ, T and their nulls condition on co-presence (join context, eligible pair-bins) and rotate within days; F timing is set by the 41-call cap and P sits in the same segments with agent × unit strata. Exogenous field: the outside reference (A-rule) and the random-partition reference (T-rule) carry any field that acts on all agents; the R2 file-level positive cannot separate a field from a store (stated). Shared priors: member-specific popularity holds each agent's own preferences; agent strata in R3. Convergence: the A-rule compares co-members with outsiders at matched size (partition contrast); R3 uses the in-flight placebo at matched lag and the read vs posted-but-unread contrast.

**Estimates.** Rows `r2_*` per unit via `write_estimates` (period_unit `local:H01-<unit>`), role `replication` for 38a–c and 51a–e and `native` for 39–41 and 44; R3 per goal period (`native` for the NE41 pooled rows).

### Round 2 synthetic validation and amendments (2026-10-05 04:33–05:00 UTC, before the round-2 real-data run)
*Scripts: `analysis/r2_synthetic.py` (R1: 1,680 replicates, 12 units × 7 worlds × 20, plus 120 round-1 g-rule replicates on W_terr; R2: 57 eligible repos × 3 worlds × 20), `analysis/r2_reacq.py --synthetic` (R3: 30 replicates on the real event skeleton). Summaries: `r2/synthetic_summary.json`, `r2/r3_synthetic.json`.*

**R1 (detection rates; 20 replicates per unit and world).**

| world | A-rule, all units | A-rule 51b / 51c / 51d | T-rule 51b / 51c / 51d | village herding (z_Λ ≥ 2, z_T ≤ −2) | village exclusion (z_T ≥ 2) |
| --- | --- | --- | --- | --- | --- |
| W_own | 0.021 (≤ 0.05 per unit) | 0.05 / 0.05 / 0 | 0 / 0 / 0 | 0.013 | 0.004 |
| W_env | 0.008 | 0 / 0 / 0 | 0 / 0 / 0 | 0.88 | 0 |
| W_store ρ 0.35 / 0.5 / 0.7 | 0.44 / 0.53 / 0.60 | 1.0 / 0.95 / 0.85 · 1.0 / 1.0 / 0.85 · 1.0 / 1.0 / 0.95 | 0 | 0.38 / 0.54 / 0.62 | 0 |
| W_terr θ 0.5 / 0.9 | 0 / 0 | 0 | 0.40 / 0.30 / 0.10 · 0.50 / 0.45 / 0.20 | 0 | 0.40 / 0.72 |

Round 1's g rule on W_terr (θ 0.9): **7.5%** of replicates qualify (its size under W_own was 0.5%), and g > 0 with z_shift ≥ 2 in 33%. That is the avoidance leak found post hoc in round 1 (A3), now measured. The A-rule qualifies in 0%.

- **R2-A1 (estimator form, for compute).** Λ is computed in pairwise-additive form: each (member, reference agent) pair counts its own joins and expectation, so an artifact held by two reference agents counts twice in both. All groups, outsider references and rotations are then sums over one set of pair matrices (`r2lib58.make_draws`).
- **R2-A2 (T-rule reference; changed after two smoke tests on W_terr, before real data).** (i) Random activity-matched groups from *all* agents, kept only with ≥ 30 eligible pair-bins, were enriched for the planted members (only they share artifacts), so the reference excluded as much as the planted group. (ii) A within-minus-cross contrast had a reference sd too large to detect anything. Final: a reference draw is a block of random activity-matched groups of size k = min(n, outsiders) drawn from the agents **outside** the tested group (the other blocks of a random partition), pooled until its eligible pair-bins match the group's (accepted at ≥ min(group's, 30)); T_ref is computed on the pooled counts, so it has the group's sampling noise and no small-count ratio bias.
- **R2-A3 (R1 power consequences).** The A-rule has power ≥ 0.85 in 51b–d already at ρ = 0.35 (51a 0.80), against 0.60–0.75 at ρ = 0.5 for round 1's rule. **P-R1a's negative therefore counts for ρ ≥ 0.35 in 51b–d.** Elsewhere it is "not identifiable" below ρ ≈ 0.7 (38a–c ≤ 0.4 at ρ 0.7; natives 0.35–0.8). The T-rule has size 0 but power ≤ 0.50 even at θ = 0.9, so **P-R1c's kill cannot fire**: a null is "inconclusive"; a positive still counts. The village tests are calibrated (sizes ≤ 0.10 per unit) and powered (herding ≥ 0.85 in every unit except 38b, 38c; exclusion ≥ 0.85 in 51a–e, 40, 44; 0.70–0.75 in 39, 41; ≤ 0.4 in 38a–c). P-R1b stands; 38b and 38c count as "not identifiable" if they fail.
- **R2-A4 (R2 consequences).** Per-repo Λ_file: size 0.009, power 0.27 at ρ_file = 0.5 (≥ 0.8 in 5 of 57 repos), so per-repo negatives are not identifiable and P-R2b is decided on the pooled test. The pooled Stouffer at z ≥ 2 has size 0.15 under file-own persistence (few repos have defined Λ_file; 95th percentile 2.3). **The pooled threshold is raised to z ≥ 3** (power 1.0 under the planted file store, whose 5th percentile is 10.5). The same threshold decides P-R2c on the pooled T_file (null 95th percentile 0.6; planted exclusion 5th percentile 8.9); per-repo T_file (power 0.17) is descriptive. Exclusivity against the random partition fires in 69% of file-own replicates, so P-R2a describes structure and says nothing about coordination (as anticipated).
- **R2-A5 (R3).** I(X; S): mean −0.0004 bits and `identified` in 0/30 under the null; identified in 0/30 at a planted q = 0.05 (I ≈ 0.016 bits), 27/30 at q = 0.1 (I ≈ 0.039) and 30/30 at q = 0.2 (I ≈ 0.097). The minimal identifiable I is about 0.04 bits. ΔI under the null: mean −0.002, CI excludes 0 in 0/10. Read × erasure interaction: size 0.067 (z ≥ 1.96), power 1.0 at log-OR 0.5 and 1.0, mean estimates 0.47 and 1.02 (unbiased): **P-R3b's kill can fire.** I_store's noise floor is analytic, (K − 1)/(2N ln 2) ≈ 0.0005 bits at N ≈ 10⁴ forced events. Code fix found while writing this (before the real run): V is NaN, not null, for windows shorter than 10 calls; the κ rows now drop NaN.
- **R2-A6 (disclosure).** At about 04:50 UTC a loader and timing check printed real village-level values for 38a, 51c and 44 before this validation: Λ_V / rotation 1.12 (z 0.8), 1.29 (z 3.5), 1.27 (z 2.1); T_V −0.05 (z −1.0), −0.07 (z −0.9), −0.38 (z −3.4); static own share above the random partition in 51c and 44 (z 3.0, 2.8). They bear on P-R1b. No prediction or rule was changed after seeing them; R2-A2 and R2-A3 follow from synthetic replicates only.

## Notes
- **Erratum (coordinator, 2026-10-04): Krakauer labels swapped.** I(x′;x) is *organismal* A* and I(x′;x|y) is *colonial* A (`literature/krakauer-2020-information-theory-of-individuality.md`). This card has them reversed, so "median colonial 0.05–0.28 bits/bin" is organismal A*. "Environmentally determined, not organismal" should read: crews have low colonial A relative to size-matched groups, high environmental coding (NTIC = A* − A) and large nC. The estimators (held-out log-loss differences) are correct. Gap: y omits the scheduler, kickoff and prior fields.
- 2026-10-04: round 1 started (exploratory, non-holdout, local, ≤ 2 threads, no sub-agents). Formal setup and predictions written first. `activity_bins` / `outages` deliberately unused (coordinator's data-bug notice).
- 2026-10-04: an API session limit interrupted the round after the synthetic validation and the re-acquisition run; resumed from disk (nothing rerun except unfinished steps). At the coordinator's request (compute scarce) replication was cut to G51 plus G38 (A2.6), with the round-1b lessons applied (scheduler synchrony, reading-gated coupling, convergence).
- 2026-10-04, **Amendment A3 (post hoc, after the replication results; disclosed):** the qualifying #51e set had zero joins. The attraction diagnostic (`analysis/attraction.py`, observed joins vs the agent + own artifact expectation) was added after seeing this. It changes no verdict but is the basis of the substantive readings above.
- 2026-10-04: period folders: predictions written by `period_folders.py --predict` before the run, results by `--results`; reading notes added by hand.
