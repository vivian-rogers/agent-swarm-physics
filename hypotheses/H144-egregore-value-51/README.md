# H144: The egregore's information outlives its members' memory and its channel has value (Kolchinsky–Wolpert, #51)

**Status:** pre-registered (not run). Card, observables, nulls, predictions and kill rules written 2026-10-09 from HH388, HH389, HH390 and HH391 (Vivian's request, 2026-10-09), before any H144 statistic on real data. No scheme, synthetic or analysis code exists yet. Depends on H143 only for its list of candidates; it runs first on the fixed families.
**Fields:** info theory, thermodynamics, sociophysics
**Literature:** [Kolchinsky & Wolpert 2018](../../literature/kolchinsky-2018-semantic-information-autonomous-agency.md); [Krakauer et al. 2020](../../literature/krakauer-2020-information-theory-of-individuality.md); [Sowinski et al. 2023](../../literature/sowinski-2023-semantic-information-resource-gathering-agents.md); [Vivian's essay, Direction 3](../../literature/jazzloaf-2026-agent-ecologies-essay.md)
**Definitions used:** *egregore* conditions (iii) and (iv) (new, `physics-models/DEFINITIONS.md`); *κ_c (channel value per bit)*, *channel information I_c*, *channel value ΔV_c (open-channel DiD)* (H70, H87); *in-flight placebo (matched-lag)* (H67); *re-acquisition path* (H58); *unit macro-state (allocation)* (H58).
**Question served:** Q4 (where the swarm's information lives and what it is worth) and Q5 (what an operator can do), `GOALS.md`.
**Paper:** `writeup/papers/superagents/` (paper 2). Sibling card: H143 (which candidates).

## Standards (2026-10-09)
As H143. Shared estimators: `infra/shared/semantic_kappa.py` (κ rows, DiD, jackknife), `infra/shared/individuality.py` (new, from H143), `infra/shared/nulls.py`. No import from H58 or H01 folders; their event tables are rebuilt from shared inputs.

## Question
For the candidate egregores of #51 (the fixed families and H143's passing candidates): does the group's state survive the erasure of a member's context, does what co-members post carry information about a member's next move beyond what an unread message at the same lag carries, and does cutting that channel cost the group output? In Kolchinsky–Wolpert terms: is there group-level semantic information, and what is its value per bit?

## Model
**From:** `physics-models/04-semantic-information/`. The system is the candidate group G with state x_G (allocation, as H143). Its viability V_G is the group's work output: agent work commits by members on the group's shared repos per bin (`work_commits`, attempts; lines changed without bulk commits as the variant). Three channels, each with a natural scramble available in #51:

| channel | information I_c | natural scramble | what a value means |
| --- | --- | --- | --- |
| member context (C_i) | the member's context about the group's next state (H58: 0.19 bits about the member's own next file) | NE41 forced erasure of member i (exogenous timing; placebo = call 20 of a segment, as H58 R3) | if the group's continuity falls with one member's wipe, the group's information lives in that member |
| co-member channel (M) | what a read co-member item tells about the member's next project beyond its own artifact, minus the in-flight placebo at matched lag | the #focus room split (08-05 → 08-24): cross-room reads fall 95% for groups split across rooms; the in-flight placebo is the call-scale scramble | if cutting the channel lowers V_G, the channel is semantic for the group |
| group artifact (A_G) | the group's next project coded against the group's artifact state from another day (H58's time-shifted I_store, at the group level) | none exogenous in #51 (NE24 is elsewhere); reported as stored information only | stored, not valued |

κ_G,c = ΔV_c / I_c in commits per 20 calls per bit (`semantic_kappa.kappa_row`), identified when I_c ≥ 0.02 bits with its jackknife interval above 0.

## Data scheme (`scheme/`)
- **Inputs:** H143's panels and candidate list (`data/processed/H143-egregore-search-51/`), `context_ledger_turns` (`reset_forced`, `t_call`, `k_ctx`), `context_ledger_items` (read vs in-flight co-member items; `uncertain` reported with and without), `project_calls`, `work_commits`, `rooms_timeline`, `kicks_classified`, `pair_day_reads`, `embeddings/agent_win30*` (for N2), `roster`, `calendar`.
- **Candidates:** the fixed families K_crew, K_repo, K_focus, K_role (control) from H143's `candidates.json`; plus H143's (i)-passing candidates when `scratchpad/H143.READY` exists (membership only; H144 does not wait for H143's verdicts).
- **Events:** forced erasures F and placebo calls P of each member (H58 R3's rule, rebuilt from the shared ledger: F = `reset_forced` calls; P = call 20 of a segment with no reset in the next 10 calls; agent × window strata); read events = co-member items in the member's read-out call; in-flight = co-member items posted in (t_call, t_call + d_c], d_c clipped to [1, 120] s (H67).
- **Output:** `data/processed/H144-egregore-value-51/` (`events/`, `results/`, `synthetic/`, `_provenance.json`). ≲ 100 MB.
- **Regimes covered:** III (#51). Reserved 51m masked; `analysis/confirm.py` frozen, dry-run only.

## Observables
- **O1 continuity ratio** r_G = C(F) / C(P): the probability that the group's modal project in the 30-min bin after the event equals its project in the bin before, after a member's forced erasure (F) vs placebo (P); also the member-only continuity for comparison (H58 R3 found 0.94 for the pair).
- **O2 group dip** β_G = ΔV_G(F) / (π_i ΔV_i(F)): the group's output change after member i's wipe relative to the member's own dip times the member's share π_i of the group's output; β ≈ 1 additive, β < 1 the others absorb, β > 1 the member is a hub (H01 R6a's β, at call resolution).
- **O3 read-gated channel information** I_M = I(next project of member; project named by a read co-member item) − the same for in-flight items at matched lag (Miller–Madow, within agent × window strata; `semantic_kappa.mi_corrected`); and the join rate toward the group's current project after read vs in-flight co-member items (the H58-R5 redirect).
- **O4 room-cut value** ΔV_M: DiD of V_G and of continuity for candidates split across #general/#focus vs candidates kept together, window D vs windows C and E (H01 R5d's design, at the group level with the ledger's read counts as the dose).
- **O5 κ_G,M** = ΔV_M / I_M; **κ_G,C** = ΔV_C / I_C from O1–O2.
- **O6 stored artifact information** I_A: the group's next project against the group's artifact state from another day.
- **N1 (NE43)** village nC with and without operator variables, before and after 08-20 (shared with H143's N1; H144 reports the κ side: output change after the nudges stop).
- **N2 (NE33)** newcomer absorption: the day-1 → day-2 content move of each 09-03/04 newcomer toward the centroid of the candidate it reads most vs toward the village centroid (bge and gte), read vs in-flight.

## Null / baseline
Placebo calls P at matched segment position (O1, O2); in-flight items at matched lag with before-message age stratification (O3; H54 R2-1 trap); unsplit candidates and the pre/post windows (O4); agent × window strata and within-stratum permutations for every I (200 permutations); agent-day cluster bootstrap with 1-h blocks within a day (CIs); size-matched random groups for O1 and O6 (a random group's "continuity" is the baseline for a group that is not a unit).

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Thresholds: `writeup/papers/thermodynamics/sections/method.tex`, "Faithfulness, not fit".
**Rival models:** W_context (the group's information lives in members' contexts: r_G < 0.7), W_steer (the joins are chat steering by a field: read = in-flight), W_artifact (the information lives in the shared repo: r_G ≈ 1, I_A > 0, κ_M ≈ 0), W_egregore (r_G ≈ 1, I_M > 0, κ_M > 0).
**Reserved data for confirmation:** the #51 tail (51m).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | F/P events from the ledger; read vs in-flight from the ledger; V_G from DQ4 commits | | |
| B assumptions | matched segment positions; matched lag and before-age; stationarity within windows | | |
| C adequacy | O1–O3 against their placebos and size-matched groups | | |
| D unfitted predictions | the channel ordering κ_C(member) > κ_M(group) > κ_A ≈ 0; β_G ≈ 1 | | |
| E interventional | NE41 wipes (member scramble), the #focus split (channel cut), NE43 nudges stop, NE33 joins | | |
| F identifiability | synthetic F/P skeletons with planted group store, planted read effects, planted room-cut cost; size ≤ 0.10, power ≥ 0.8 | | |
| G ground truth | the member's own self-dip reproduced (H58 R3 positive control); K_role pairs show no channel value | | |
| H comparative | W_egregore vs W_artifact vs W_steer vs W_context | | |
| I transfer | confirmation on the #51 tail (not run) | | |

## Prediction
*Written 2026-10-09, before running the analysis on real data.*

| | Card's prediction (operational) | Falsified if | My prior |
| --- | --- | --- | --- |
| **P1** continuity | for K_crew and K_repo candidates, r_G ≥ 0.9 (CI above 0.8): the group's project survives one member's wipe | r_G < 0.7 for ≥ 1/2 of candidates | 0.8 (the artifact holds it; H58 R3) |
| **P2** additivity | β_G within [0.8, 1.2] (pooled CI) for K_crew and K_repo; no candidate has β_G < 0.5 (absorption) | β_G < 0.5 with CI below 0.8 for ≥ 1 candidate (the group buffers the member) | 0.75 that additivity holds (no buffering) |
| **P3** channel information | I_M > 0.02 bits (jackknife CI above 0) for ≥ 1 candidate; read > in-flight for the join rate (log-OR > 0, CI above 0) | read = in-flight for every candidate (W_steer by convergence) | 0.45 |
| **P4** room-cut value | ΔV_M ≤ 0 (split candidates lose output or continuity against unsplit ones), DiD CI excluding 0 for ≥ 1 split candidate | DiD CI includes 0 for every split candidate with ≥ 3 members (H01 R5d found +0.02) | 0.3 |
| **P5** κ ordering | κ_C(member, own output) > κ_G,M > κ_G,A ≈ 0; κ_G,M identified only where P3 and P4 both hold | κ_G,M identified and larger than the member's κ_C | 0.7 |
| **P6** the field control | K_role pairs: I_M at the null and r_G at the random-group level | rival pairs show channel information | 0.75 |
| **N1** NE43 | after 08-20 (nudges stop) the village's output per active hour changes by less than 5% while nC falls (H143 N1): the operator carried closure, not value | output falls ≥ 10% | 0.6 |
| **N2** NE33 | newcomers' day-1 → day-2 content move points at the village centroid, not at any candidate (no absorption by an egregore; the village field dominates), in both embedding models | the move points at the centroid of the candidate the newcomer reads most, read > in-flight | 0.6 that it points at the village |

**Kill rules.** (K1) If P1 and P2 hold but P3 and P4 both fail, the verdict is "the information lives in shared artifacts, and the channel has no value": a stigmergic container, not an egregore (W_artifact). (K2) If P3 holds and P4 fails with power ≥ 0.8 at a planted room-cut cost of 10%, the channel is informative but worthless: a pattern, not an agent. (K3) If the member self-dip positive control fails at call resolution, O1–O2 are inconclusive (as H01 R6a).

**Overall prior.** I expect the artifact reading: the group's project survives wipes because it sits in the repo, the joins show some read excess over in-flight (H11 R2 found chat-steered co-arrival), and the room cut costs nothing measurable. That is W_artifact with a small W_steer term. A positive P4 with P3 would be the first value measurement of a group channel in the village.

**Synthetic validation (axis F), before real data.** On the real F/P skeletons of #51 (as H58 R3): a planted group store (members return to the group's project with weight ρ), a planted read effect (read co-member items raise the join log-OR by 0.5 and 1.0; in-flight no effect), a planted room-cut cost (split candidates lose 10% and 20% of output in window D), a planted buffering world (β = 0.5) and the three null worlds. Size ≤ 0.10, power at each planted size reported. The member self-dip must be reproduced before O1–O2 are read.

### Amendment A0 (2026-10-09, after the qualitative reading of #51 and before any H144 statistic)
*What I had seen:* the four story reports (07-06 → 09-06). No H144 estimator has run.
- **A0.1** As H143 A0.1–A0.5 (H58 unit labels by date; relayed human input via Claude Fable 5 in E; mention-based communities in one room; commit deduplication by hash and dropping inherited commits; K_story as a labelled post hoc family).
- **A0.2 The #focus cut is not the cut the card assumed.** The reading shows #focus held one dyad (Gemini 2.5 Pro and Claude Opus 4.8, the Echoes pair) for 08-05 → 08-24, with short visits by others; the dyad's channel got stronger, not weaker. O4 is kept as written, but the read is: for the Echoes pair #focus is a *private channel*, not a cut; the cut applies to groups split by the move (e.g. the pair vs. the agents who helped Echoes from #general).
- **A0.3 Natural channel switches of the Echoes pair added as native events (labelled, dates fixed now):** inbox folder (07-10), email (date from chat), `echoes-inbox` repo (07-22), #focus (08-05), back to inbox files (08-24), direct commits (08-28), chat paste with Opus 4.8 alone while Gemini's tools failed (09-02 → 09-04). Observable: the pair's output and continuity in the 2 active days before vs after each switch, against placebo days. A pair whose output survives every switch of its channel holds its state outside any one channel.
- **A0.4 Hub-loss events added (labelled):** Claude Opus 5's reassignment on 07-29 (NE38: the KEYSTONE circle loses its hub); the operator's 08-05 rebuke of DeepSeek-V3.2 and its 08-24 outreach veto (the coalition's hub is shocked); Gemini 2.5 Pro's tool losses (W3, 09-02 → 09-04). Observable: the group's output on its shared artifact after the event, relative to the hub's share of that output (β as in O2).

## Impostors
| Impostor | How handled | Status (planned) |
| --- | --- | --- |
| Scheduler field | F timing set by the 41-call cap; P at matched segment position; agent × window strata; room cut compared within the same days (DiD) | removed |
| Exogenous field | K_role control; human-message and nudge bins flagged; NE38 and NE43 as window boundaries or covariates | partly |
| Shared model priors | agent strata; same-lab vs cross-lab candidates reported | partly |
| Contemporaneous convergence | in-flight placebo at matched lag with before-age strata (O3); room-cut DiD does not depend on reads being causal | removed (O3), n/a (O4) |

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G51](goalperiod-subhypotheses/G51/README.md) (windows A–E) | exploratory | pending | |
| [NE41](goalperiod-subhypotheses/NE41/README.md) (member wipes, pooled over #51) | native | pending | |
| [NE43](goalperiod-subhypotheses/NE43/README.md) (#focus split; nudges stop) | native | pending | |
| [NE33](goalperiod-subhypotheses/NE33/README.md) (newcomers, 51k–51l) | native | pending | |
| 51m (reserved) | confirmatory | not run | |

## Results
*Pending.*

## Notes
- 2026-10-09: card written by the coordinator from HH388–HH391 at Vivian's request, next to H143. Traps to respect (`infra/README.md`): forced wipes arrive with a chat backlog (88% receive chat at call 1 vs 45% at pseudo-erasures), so message-class contrasts at the wipe are partly confounded; the sandwich test of class × wipe is anti-conservative (use the agent-day cluster bootstrap); read vs in-flight contrasts must match the before-message age; `agent_memories` text is read in memory only.
