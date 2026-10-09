# H143: Egregores in #51 are Krakauer individuals on the substrate, held by no single member

**Status:** pre-registered (not run). Card, candidates, observables, nulls, predictions and kill rules written 2026-10-09 from HH386 and HH387 (Vivian's request, 2026-10-09: "identify egregores in GP51 using the individuality info dynamics and the Kolchinsky stuff"), before any H143 statistic on real data. No scheme, synthetic or analysis code exists yet.
**Fields:** info theory, complex systems, sociophysics
**Literature:** [Krakauer et al. 2020](../../literature/krakauer-2020-information-theory-of-individuality.md); [Kolchinsky & Wolpert 2018](../../literature/kolchinsky-2018-semantic-information-autonomous-agency.md); [Vivian's essay, Direction 3](../../literature/jazzloaf-2026-agent-ecologies-essay.md); [Rosas et al. 2020](../../literature/rosas-2020-reconciling-emergences-causal-emergence.md) (Ψ as a secondary check)
**Definitions used:** *egregore (effective superagent on a substrate)*, *environment E (impostor bundle)*, *candidate families* (new, `physics-models/DEFINITIONS.md`); *Krakauer individuality (organismal A\*, colonial A)*, *size-matched grouping*, *unit macro-state (allocation)*, *agent + own artifact (null unit)* (H58 variants); *in-flight placebo (matched-lag)* (H67). Names follow the published Krakauer paper: I(x′;x) is organismal A\*, I(x′;x|E) is colonial A, I(x′;E|x) is nC.
**Question served:** Q3 (collective order beyond fields) and Q4 (where the swarm's information lives), `GOALS.md`.
**Paper:** `writeup/papers/superagents/` (paper 2). Sibling card: H144 (the value of the candidates this card finds).

## Standards (2026-10-09)
Follows `STANDARDS.md`: impostor table below; two layers (replication over the #51 windows, natives NE43 and the #focus split); predictions and nulls before real data; reserved data masked (`holdout_mask`; the #51 tail 51m, 09-07 → 09-18, is the confirmation window); estimates rows via `write_estimates`; ≤ 2 workers per process; no import from another hypothesis folder (H58's Krakauer estimator is moved to `infra/shared/individuality.py` with `--verify`).

## Question
Does #51 contain a group of agents that behaves as one individual on top of its members: a group whose own state predicts its future beyond the external fields and beyond random groups of the same size, and whose information is held by no single member? If so, which groups, on which state channel, and at which time scale?

## What H01 and H58 established (read before designing)
- No candidate unit (crews, synchrony, co-allocation, reply communities, rooms, labs) beat size-matched groups on timing individuality; but that test measured a binary activity state and had ≤ 7% validated power (H01 R4, A1.1). The negative is not evidence of absence.
- The persistent unit is the agent + its own artifact (H01 R4d; H58 R3: 0.083 bits of next-file information survive a wipe; κ = 0.77 commits per bit for re-reading its own files).
- Attraction crews exist in #51b–c (H58 R1): 6–8 agents move onto each other's current repo 4–8× their own-artifact expectation, beyond rotations and activity-matched outsiders. They were defined in sample, are 5–35 joins, GPT-5.2 is in 9 of 16 qualifiers, and the joins are not separated from chat steering. H58 asked for out-of-sample crews (R6) and read-gated joins (R5).
- H01 and H58 put only the rest of the swarm's activity and human/automated messages in E; the scheduler, kickoff and prior fields were not explicit components (Krakauer notes, "Gap"). Both printed the Krakauer names swapped; the estimators were right.

## Model
**From:** `physics-models/12-information-dynamics/` (Krakauer individuality; Ψ as a secondary check). `physics-models/04-semantic-information/` supplies the agent criterion that H144 tests.

For a candidate G with group state x_G(b) at bin b and environment E(b):
- organismal A\* = I(x′; x) = L(x′) − L(x′ | x);
- colonial A = I(x′; x | E) = L(x′ | E) − L(x′ | x, E);
- environmental determination nC = I(x′; E | x) = L(x′ | x) − L(x′ | x, E);
- environmental coding NTIC = A\* − A;
- group-held information Δ_i = L(x′_G | x_i, a_i, E) − L(x′_G | x_G, E) for each member i (what the group's past adds beyond member i's own state x_i and own artifact a_i); Δ_min = min_i Δ_i.

L(·|·) are held-out log-losses (bits per bin) from day-blocked cross-validation (leave-one-day-out within the window), with H58's estimator family: a stay/popularity mixture for discrete states and a ridge-regularized multinomial or Gaussian for 1-d content. All quantities are reported as excesses over size-matched random groups: z = (value − mean_null) / sd_null over 300 draws. A and A\* never fall as a group grows (Krakauer), so the excess is the only meaningful number.

**Boundary expansion (the paper's discovery rule, HH300):** from a seed S, add the agent ΔS that most raises colonial A while lowering nC; stop when the next addition does not lower nC. Membership from the first half of the window's days; the final set is scored on the second half.

## Data scheme (`scheme/`)
- **Inputs (processed only, never `data/raw/`):** `project_calls.parquet` (per-call project labels, 827k labelled calls in #51), `work_commits.parquet` and `work_repos.parquet` (DQ4), `embeddings/agent_win30.parquet` + `agent_win30_style_resid_period_{bge_small,gte_modernbert}.npy` (30-min content residuals), `behavior_states_v3.parquet`, `context_ledger_turns.parquet` (bin presence, resets), `rooms_timeline.parquet`, `kicks_classified.parquet` (human messages, nudges), `pair_day_reads.parquet` (read graph), `ground_truth_labels.parquet` (#51 roles, rival and opposed pairs, room assignment), `roster.parquet`, `period_units.parquet`, `calendar.parquet`.
- **Windows (exception (d), named):** the #51 units differ only by roster size except at NE38 (one agent's role), 08-05 (#focus + bookends stop) and 08-20 (nudges stop). Consecutive units separated only by a roster join are merged so that a window has ≥ 5 days: A = 51a+51b+51c (07-06 → 07-16, 9 days, 21 → 25 agents), B = 51d+51e (07-17 → 07-28, 8 days), C = 51f (07-29 → 08-04, 5 days), D = 51g (08-05 → 08-21, 13 days; rooms #general/#focus; nudges stop 08-20 as a covariate), E = 51h+51i+51j+51k+51l (08-24 → 09-04, 10 days, 27 → 32 agents). Candidate membership within a window is restricted to agents present on every day of the window. Per-window estimates are primary; a #51-wide fit with window fixed effects is reported as the partially pooled reference, flagged.
- **Bins:** active 30-min bins inside each day's empirical window (`calendar.win_start` → `win_end`), DQ8 all-present trim; variants 2 h and 1 day (HH321). Transitions within a day only.
- **State channels per candidate G:**
  - *allocation* x^P_G: the modal project label of G's members' calls in the bin (`project_calls.label`), alphabet = G's top-6 projects over the window + other + none (≤ 8 symbols); member state x_i = the member's own label; own artifact a_i = the repo of the member's last work commit;
  - *content* x^C_G: the mean of members' 30-min style residuals (bge; gte as the second model), projected on G's first principal direction fitted on the first half of the window's days (out of sample), as a 1-d Gaussian variable; also a 3-symbol tercile version;
  - *behavior* x^B_G: the share of members in execute-type states (p_execute_task + p_debug_recover + p_verify_report) in the bin, 1-d.
- **Environment E (strictly lagged, ≤ 3 coarse features):** (e1) scheduler phase: time-of-day bin (4 levels) × first/last-30-min flag × bookends-on flag; (e2) the rest of the village's state on the same channel (non-members' modal project; non-members' content projection; non-members' execute share), at b; (e3) exogenous input in b: any human message, nudge or kickoff to a member. Agent identity (private goals, priors) enters as a covariate of the member models, not as E.
- **Candidate families (fixed before any statistic):**
  - K_crew: H58's #51b–c attraction crews and search sets, read from `data/processed/H58-coordinated-superagents/results/units/*.json` and `r2/r1_results.json` (membership only);
  - K_repo: for each repo with ≥ 3 writers of ≥ 3 agent work commits in the window's first half, its writers;
  - K_focus: agents with ≥ 1 h in room 15 (#focus) in window D's first half (room 15 occupancy from `rooms_timeline`);
  - K_read: communities (greedy modularity) of the symmetrized read graph (`pair_day_reads`) over the window's first half, size 3–10;
  - K_expand: Krakauer boundary-expansion sets from each agent + own artifact as the seed, on the allocation channel, first-half days, max size 8;
  - K_role: the #51 rival pairs and opposed pairs (the assigned-field control) and the role classes (media, support);
  - K_lab: agents by lab (the shared-prior control);
  - K_vil: all agents present (the village).
  - Null: 300 size-matched random groups per candidate, drawn from the window's present agents, matched on activity (total labelled calls within ±50%).
- **Output:** `data/processed/H143-egregore-search-51/` (`panels/<window>.parquet`: agent × bin states; `candidates.json`; `results/<window>.json`; `synthetic/`; `_provenance.json`). Bytes: ≲ 100 MB.
- **Regimes covered:** III only (#51). Reserved: 51m masked everywhere; `analysis/confirm.py` frozen and guarded, dry-run only.

## Observables
Per window, candidate and channel: colonial A, A\*, nC, NTIC, Δ_min and their size-matched z-scores; the within-day rotation z (timing null); the boundary-expansion path (A, nC per step) for K_expand; Ψ of the group centroid against the field-only skeleton (secondary). Summary per window: the number of candidates that pass (i) and (i)+(ii) out of sample; which families they come from; the bin width at which z peaks.

## Null / baseline
1. **Size-matched random groups** (primary): same size, same window, activity-matched; 300 draws; z-scores for every quantity.
2. **Within-day rotation** of each member's series (timing null; H58's `rotate_rows`): removes coordination while keeping each member's marginal and the day structure.
3. **Field-only skeletons** (DQ8 `simulate.py`, preset with global, room, time-of-day and day fields, zero coupling) on window D's real schedule: the reference for Ψ and for the size of the z-tests.
4. **Agent + own artifact** (the H58 null unit) as the per-member comparator: the group must beat its best member (Δ_min > 0).
5. **Assigned role pairs** (K_role): the positive control for the field impostor. They share a private goal text; after agent identity is in the model and e2–e3 in E, their colonial A excess should sit at the null.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/papers/thermodynamics/sections/method.tex`, "Faithfulness, not fit".
**Rival models:** W_field (agents respond to shared fields; colonial A at the null after E), W_hub (one member drives the rest; (i) passes, (ii) fails), W_own (agent + own artifact; the null unit), W_egregore (a planted group store: members' next project depends on the group's current project with weight ρ, beyond their own artifact).
**Reserved data for confirmation:** the #51 tail (51m, 09-07 → 09-18): candidates and thresholds frozen from the exploration; `analysis/confirm.py`.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | states from `project_calls`, win30 residuals, `behavior_states_v3`; E from the ledger, rooms, kicks; candidates from named tables | | |
| B assumptions | first-order Markov per bin; within-day transitions; stationarity by split halves; bin-width sweep | | |
| C adequacy | held-out log-loss gains over the null hierarchy (marginal → E → x → x, E) | | |
| D unfitted predictions | the family ordering (crews, repo sets > read communities > labs ≈ role pairs); the hub test; the bin width of the peak | | |
| E interventional | NE43 (bookends 08-05, nudges 08-20) and the #focus split as E changes (native tests) | | |
| F identifiability | synthetic worlds W_field, W_hub, W_own, W_egregore on the real #51 skeletons at real counts; size ≤ 0.10, power at ρ ∈ {0.2, 0.35, 0.5} | | |
| G ground truth | rival pairs and labs at the null; H58's 51c crew recovered by K_expand if it is real | | |
| H comparative | W_egregore vs W_hub vs W_field by held-out log-loss | | |
| I transfer | confirmation on the #51 tail (not run) | | |

## Prediction
*Written 2026-10-09, before running the analysis on real data.*

| | Card's prediction (operational) | Falsified if | My prior |
| --- | --- | --- | --- |
| **P1** candidates exist | ≥ 1 candidate in ≥ 1 window passes (i): colonial A excess z ≥ 2 out of sample on the allocation channel at 30 min or 2 h, with the rotation z ≥ 2 as well | no candidate passes in any window at any bin width | 0.6 (the H58 crews in window A) |
| **P2** family ordering | among candidates with ≥ 3 members, the median z of K_crew and K_repo exceeds that of K_read, which exceeds K_lab and K_role (each where defined), in ≥ 3 of 5 windows | K_role or K_lab has the highest median z in ≥ 3 windows | 0.7 |
| **P3** the field control | K_role pairs have median colonial A excess z < 1 once agent identity and e2–e3 are in the model; their organismal A\* excess is > 2 (they share a field) | rival pairs pass (i) with z ≥ 2 | 0.75 |
| **P4** group-held | ≥ 1 candidate that passes (i) also passes (ii): Δ_min > 0 with z ≥ 2 | every (i)-passing candidate has a member with Δ_i ≤ 0 (a hub) | 0.3 |
| **P5** time scale | the colonial A excess of passing candidates peaks at 2 h, not 30 min and not 1 day (HH321) | the peak is at 30 min (call-scale co-arrival) or at 1 day (the goal field) | 0.5 |
| **P6** channel | allocation carries the excess; content passes only in window D (#focus) and only with both embedding models; behavior never passes | content passes in ≥ 3 windows, or behavior passes anywhere | 0.6 |
| **P7** expansion | the Krakauer boundary from an agent + own artifact seed closes at size 1 for ≥ 2/3 of seeds (HH300); the seeds that expand recover ≥ 50% of a K_crew or K_repo set | ≥ 1/2 of seeds expand to ≥ 4 members | 0.7 |
| **N1** NE43 (native) | village nC falls across 08-20 (nudges stop) by ≥ 0.02 bits per bin with the operator variables in E; colonial A of the village is unchanged (z within ±1) | nC unchanged across 08-20 | 0.5 |
| **N2** the #focus split (native) | K_focus passes (i) on the content channel in window D and not in window C or E (the room is the egregore's channel while it exists) | K_focus at the null in D | 0.4 |

**Kill rules.** (K1) If no candidate passes (i) in any window and the synthetic power at ρ = 0.35 is ≥ 0.8 in that window, the verdict is "no candidate egregore in #51 at this power". (K2) If (i) passes only for candidates that fail (ii), the verdict is "hubs, not egregores". (K3) If K_role pairs pass (i) at the same rate as K_crew, the estimator has not removed the field, and no positive is read until E is fixed (an amendment, dated).

**Overall prior.** I expect P1 to pass in window A through the H58 crews (the allocation channel), P4 to fail (GPT-5.2 and one or two repo owners are hubs), and content to pass only in #focus. The likely verdict is "hubs and shared containers, no egregore", which is what paper 1's picture predicts: fields and a few named couplings, no group-level individual. A pass of P4 out of sample would be the first evidence for an egregore in the village.

**Synthetic validation (axis F), before real data.** Four worlds on the real #51 window skeletons (presence masks, call counts, project alphabets from the first half): W_own (each agent stays on its own project with its own persistence), W_field (W_own plus a shared project popularity field and a time-of-day field), W_hub (one planted hub whose project the others follow with weight ρ), W_egregore (a planted group of 6 whose members' next project depends on the group's modal project with weight ρ, beyond their own artifact; ρ ∈ {0.2, 0.35, 0.5}). 20 replicates per world and window. Report the size of the z ≥ 2 rule for (i) and (ii) in W_own and W_field (must be ≤ 0.10) and the power in W_egregore; the hub test must reject W_hub's planted group on (ii) in ≥ 0.8 of replicates. Any threshold change after the synthetic is a dated amendment before real data.

## Impostors
| Impostor | How handled | Status (planned) |
| --- | --- | --- |
| Scheduler field | DQ8 all-present trim; scheduler phase in E (e1); within-day transitions only; rotation null | removed |
| Exogenous field (private goals, humans, nudges) | agent identity as a covariate (private goals are constant per agent per window); e3 in E; K_role as the positive control; NE38 splits window C from B | removed if P3 holds, else open |
| Shared model priors | agent identity covariate; K_lab as the control; cross-lab vs same-lab candidates reported | partly |
| Contemporaneous convergence | E strictly lagged; the read-gated test is H144's (HH389); at 30 min co-arrival is not separated, which is why P5 predicts the 2-h peak | partly (closed by H144) |

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G51](goalperiod-subhypotheses/G51/README.md) (windows A–E) | exploratory | pending | |
| [NE43](goalperiod-subhypotheses/NE43/README.md) (08-05, 08-20) | native | pending | |
| 51m (reserved) | confirmatory | not run | |

## Results
*Pending.*

## Notes
- 2026-10-09: card written by the coordinator from HH386 and HH387 at Vivian's request. Prior work read: H01 (round 2), H58 (rounds 1–2), the Krakauer and Kolchinsky notes, `physics-models/12-information-dynamics/README.md`. The Krakauer estimator of H58 (`h58lib.krakauer`) is to be moved to `infra/shared/individuality.py` and generalized to the three channels and the E bundle, with `--verify`.
- Known traps to respect (`infra/README.md`): day-cluster bootstraps under-cover in 5-day windows (resample 1-h blocks within a day); NaN comparisons in polars; no `|` inside card table cells; `estimates.py` rejects `local:` rows that span reserved days.
