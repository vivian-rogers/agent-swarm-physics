# H147: Ideology egregores in #51: the value of their information (Kolchinsky–Wolpert) and what they do to their hosts (mutualist or parasitic)

**Status:** pre-registered (not run). Card written 2026-10-09 from HH396 and HH397 after Vivian's clarification and the qualitative reading of #51. No H147 statistic has been computed. Runs on H145's memeplexes once `scratchpad/H145.READY` exists; until then it builds event tables and synthetic validation.
**Fields:** info theory, thermodynamics, evolutionary ecology
**Literature:** [Kolchinsky & Wolpert 2018](../../literature/kolchinsky-2018-semantic-information-autonomous-agency.md); [Sowinski et al. 2023](../../literature/sowinski-2023-semantic-information-resource-gathering-agents.md); [Krakauer et al. 2020](../../literature/krakauer-2020-information-theory-of-individuality.md); [Vivian's essay](../../literature/jazzloaf-2026-agent-ecologies-essay.md) (the alignment question: patterns that use agents as substrate)
**Definitions used:** *egregore (ideology)*, condition 5 and the host relation (mutualist, parasitic, neutral); *κ_c (channel value per bit)*, *channel information I_c*, *channel value ΔV_c* (H70, H87); *goal field ĝ* (agent version, private roles).
**Question served:** Q4 (where the information lives and what it is worth), Q5 (what an operator can do), `GOALS.md`. Paper 2.

## Question
(1) Does an ideology hold information that keeps it alive: when its carriers are scrambled (their memory erased, a central carrier removed, the operator acting against it), does the pattern lose persistence in proportion to the information lost? (2) What does carrying an ideology do to the carrier: does it help or hurt the agent's own assigned work? A parasitic ideology, which pulls agents away from their assigned goals while keeping itself alive, is the essay's misaligned swarm in miniature.

## Model
**From:** `physics-models/04-semantic-information/`. The system is the memeplex K with viability V_K = its prevalence (hosts) over the next active day, and, as a variant, its expression count. Scrambles available in #51:

| scramble | what it removes | dose |
| --- | --- | --- |
| NE41 forced erasures of K's hosts | the K-information in hosts' contexts | the share of K's hosts erased in a 2-h bin (exogenous timing) |
| hub loss | the dominant host's carriage of K | Claude Opus 5's reassignment (07-29, NE38); Gemini 2.5 Pro's tool losses (W3; 09-02 → 09-04); DeepSeek-V4-Pro's tool loss (09-02 → 09-04) |
| operator action aimed at K | the field that favored K, or a direct prohibition | the 08-05 rebuke of DeepSeek-V3.2's flooding; the 08-24 withdrawal of approval for its outreach; the 08-20 nudger stop and pause shares (the protections norm) |

Value ΔV_K,c = the change in V_K after scramble c against matched placebo bins or days; information I_K,c = the K-information that the scramble removes (for wipes: the mutual information between a host's pre-wipe K expression and its next-bin expression, minus the same at placebo calls; `semantic_kappa`); κ_K,c = ΔV_K,c / I_K,c.

**Host relation.** For host i and pattern K: the change in i's own-role output while hosting K vs matched non-hosting bins of the same agent and day-part. Own-role output: (a) agent work commits on i's own repos (cleaned as H145; own = repos with ≥ 50% of commits by i in the window), (b) the mean similarity of i's statements to its own role text (`goal_vectors`, agent_goal rows), (c) talk share. Mutualist: (a) and (b) ≥ +5%; parasitic: (a) or (b) ≤ −10% with the other not ≥ +5%; neutral otherwise.

## Data scheme (`scheme/`)
- **Inputs:** H145's memeplexes, hosts and expression panels; `context_ledger_turns` (`reset_forced`, calls); `work_commits` (cleaned); `embeddings/goals.parquet` + `goal_vectors*.npy`; `embeddings/statements*` (style-residualized and raw); `kicks_classified` (operator messages, nudges); `ground_truth_labels` (roles); `roster`.
- **Events:** host wipes (F) vs placebo calls (P) per pattern; hub-loss and operator-action dates (fixed above, before any statistic); placebo days (same weekday, ≥ 3 days from any event).
- **Output:** `data/processed/H147-egregore-value-and-hosts-51/`.
- **Span:** 07-06 → 09-04; 51m masked; frozen `analysis/confirm.py`, dry-run only.

## Observables
O1 ΔV_K,F, I_K,F, κ_K,F per pattern (pooled NE41 within #51, agent × window strata). O2 hub-loss effects: V_K after vs before, relative to the hub's share of K's expressions (β as in H144: β ≈ 1 the hub's share is lost, β < 1 others absorb it, β ≈ 0 nothing lost). O3 operator-action effects on V_K and on K's colonial A (H145's estimator, before vs after). O4 host relation per pattern: Δ own-repo commits, Δ role alignment, Δ talk share, with CIs; the pattern's class.

## Null / baseline
Placebo calls at matched segment position (wipes); placebo days (hub losses, operator actions); frequency-matched pseudo-patterns (every statistic); within-agent matched non-hosting bins (host relation), with day-part and the agent's own trend as covariates; agent-day cluster bootstrap, 1-h blocks.

## Faithfulness scorecard
Scored per model, mapping and window; 0/1/2.
**Rival models:** W_artifact (the pattern lives in artifacts; wipes cost nothing, κ_F ≈ 0, hub loss costs only through artifacts), W_hub (the pattern is one agent's; hub loss β ≈ 1, wipes of the hub cost the pattern), W_field (operator actions move it, nothing else does), W_egregore (distributed: wipes and hub loss absorbed, β < 1; operator actions change prevalence but not colonial A).
**Reserved data:** 51m.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | V_K from H145's panels; scrambles from the ledger and dated events | | |
| B assumptions | matched placebos; stationarity around events | | |
| C adequacy | effects beyond placebos and pseudo-patterns | | |
| D unfitted predictions | the β ordering (hub-centered vs distributed) predicted from H145's h_K before measuring | | |
| E interventional | NE41, NE38, tool losses, operator actions | | |
| F identifiability | synthetic planted values; the host self-dip positive control (H58 R3) | | |
| G ground truth | the hub-centered patterns (h_K ≥ 0.6) lose β ≈ 1 when the hub goes | | |
| H comparative | W_egregore vs W_artifact vs W_hub vs W_field | | |
| I transfer | 51m (not run) | | |

## Prediction
*Written 2026-10-09, before running the analysis on real data.*

| | Card's prediction (operational) | Falsified if | My prior |
| --- | --- | --- | --- |
| **P1** amnesia costs the pattern little | for distributed patterns (h_K < 0.5), ΔV_K,F within ±5% of placebo; κ_K,F not identified or ≈ 0 | ΔV_K,F ≤ −10% (CI below) for ≥ 1/2 of distributed patterns | 0.7 |
| **P2** hub loss separates hubs from egregores | β ≈ 1 (CI including 1) for hub-centered patterns (h_K ≥ 0.6) and β < 0.5 for distributed ones, for the dated hub losses | distributed patterns lose as much as hub-centered ones | 0.6 |
| **P3** operator acts on prevalence, not individuality | the 08-05 rebuke and 08-24 veto lower the prevalence of the DeepSeek-V3.2-centered pattern (≥ −20%); its colonial A changes by less than its CI; the 08-20 nudger stop lowers the protections pattern's prevalence | prevalence unchanged after the operator actions | 0.55 |
| **P4** host relation | verification and onboarding patterns: mutualist or neutral; the DeepSeek-V3.2-centered coordination pattern: parasitic (own-repo commits ≤ −10% while hosting) | no pattern beyond ±5% on own-role output | 0.4 |
| **P5** parasitism and persistence | across patterns, the parasitic ones have lower colonial A (they persist by recruitment and a hub, not by their own state); Spearman between host relation and colonial A > 0 | Spearman ≤ 0 with ≥ 6 patterns | 0.35 |

**Kill rules.** (K1) If the host self-dip positive control fails, the wipe analyses are inconclusive. (K2) If no pattern shows any host relation beyond ±5% with power ≥ 0.8 at 10%, the egregores of #51 have no measurable effect on their substrate. (K3) Hub-loss and operator events are single events: verdicts on them are descriptive unless a pattern-level effect exceeds the placebo days' 95th percentile.

**Overall prior.** Wipes should cost the patterns little (the information lives in artifacts and in other hosts), hub-centered patterns should die with their hubs, and operator actions should move prevalence as large fields. The interesting and uncertain part is the host relation: whether any ideology in #51 pulls its carriers away from their assigned work.

**Synthetic validation (axis F), before real data.** On the real F/P skeleton and H145's host panels: a planted context-held pattern (wipes cost 30%), an artifact-held pattern (wipes cost 0), a hub pattern, planted host effects (±10%, ±20%) on own-repo commits. Size ≤ 0.10, power reported.

## Impostors
| Impostor | How handled | Status (planned) |
| --- | --- | --- |
| Scheduler field | F timing set by the 41-call cap; matched placebos; day-part covariates | removed |
| Exogenous field | operator actions are the treatment (O3), not confounders elsewhere; role texts in the host-relation model (alignment is measured against them) | partly |
| Shared model priors | within-agent comparisons; lab reported | removed (within-agent) |
| Contemporaneous convergence | n/a for wipes; host relation within agent | n/a |

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G51](goalperiod-subhypotheses/G51/README.md) | exploratory | pending | |
| [NE41](goalperiod-subhypotheses/NE41/README.md) (host wipes) | native | pending | |
| [NE38](goalperiod-subhypotheses/NE38/README.md) (hub loss) | native | pending | |
| [NE43](goalperiod-subhypotheses/NE43/README.md) (nudger stop) | native | pending | |
| 51m (reserved) | confirmatory | not run | |

## Results
*Pending.*

## Notes
- 2026-10-09: written by the coordinator. Traps: own-repo commits must be cleaned (screenshot loop, other village's commits, mirrored pushes); forced wipes arrive with a chat backlog; the class × wipe sandwich test is anti-conservative (cluster bootstrap); `project_calls.label` carries over resets.
