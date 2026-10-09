# H147: Ideology egregores in #51: the value of their information (Kolchinsky–Wolpert) and what they do to their hosts (mutualist or parasitic)

**Status:** round 1 in progress (2026-10-09): scheme built, synthetic validation done and Amendments A1–A3 written before any real-data outcome; the real-data run waits for H145's frozen memeplexes. Card written 2026-10-09 from HH396 and HH397 after Vivian's clarification and the qualitative reading of #51.
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

## Round 1 (2026-10-09)

### Scheme (built before any statistic)
`scheme/build.py` → `data/processed/H147-egregore-value-and-hosts-51/` (≈ 5 MB). Inputs: `work_commits` cleaned by `memeplex.clean_commits` (shared rules after the fix in 4f6ab2e), `calls`, `context_ledger_turns`, `chat_core`, `embeddings/statements` and `goals`, `calendar`, `period_units`, `call_windows` (presence). 51m is masked with `holdout_mask` and asserted absent.
- **Bins:** H145's 2-h bins (`memeplex.make_bins`: 16:00 UTC anchor, 4 bins per day, 45 days, 180 bins) and H145's DQ8 presence trim, so H147's host matrices are H145's.
- **Commits:** 48,093 #51 agent work commits → 1,519 in the `surprise-lab-mirror-proofs` repo dropped → 2,225 with no touching call on the repo that day dropped → 0 hash duplicates → 0 before the author joined → 1 `-chat@agentvillage.org` author (raw git emails) → **44,348 kept**. Busy single-file streams are kept (the Echoes pair's chapter commits). Own repo = ≥ 50% of the H143 window's cleaned commits on the repo slug.
- **Role alignment:** cosine of each statement to its author's current private role text (`agent_goal` rows; Claude Opus 5's 07-24 → 07-29 game-dev text), regime-III whitened 32-d basis, bge and gte; 68,895 statements.
- **F / P events:** 14,593 forced erasures (F, `reset_forced`) and 15,100 placebo calls (P, call 21 of a segment of ≥ 40 calls; the H70 rule), with windows of calls −20…−1 and 1…20.
- **Dated events** (fixed in `scheme/build.py` before any statistic): HL1 Claude Opus 5 reassigned (07-29 16:50 UTC); HL2 Gemini 2.5 Pro's tool-loss week W3 (08-10 → 08-14); HL3 Gemini 2.5 Pro's bash failure (09-02 → 09-04 17:14 UTC); HL4 DeepSeek-V4-Pro's tool loss (09-02 → 09-04; HL4b 09-03 → 09-04); OP1 the 08-05 rebuke of DeepSeek-V3.2; OP2 the 08-24 withdrawal of approval; OP3 the 08-20 nudger stop (16:45 → 17:51 UTC). Point events use 2 active days before and after. Placebo days: same weekday, ≥ 3 days from every event day (2–4 per event); variant: any weekday (13–15 per event).

### Synthetic validation (axis F), before real data
`analysis/synthetic.py` on the real skeleton: the real 69,048 statements (agent, time, bin), the real F / P events and windows, the real agent × bin panel (presence, own-repo commits, role alignment) and the real dated events. Planted patterns: 8 elements carried by 5, 8 or 12 random active agents with a latent carry state (persistence, recruitment by prevalence, a day factor). 20 replicates per world; 20 pseudo-patterns (unplanted, fresh hosts) per replicate; agent-day cluster bootstrap, B = 100. Output: `data/processed/H147-.../synthetic/{wipes,hosts,hubs,ops}.json`.

**Cost per candidate (profiled first):** one pattern or pseudo-pattern costs 0.09 s for the wipe block (hit counts by binary search on sorted times, Poisson fixed-effects IRLS with the strata profiled out, Miller–Madow MI) and ≈ 3 ms per host-relation fit. With 100 pseudo-patterns and B = 200 per pattern, a memeplex costs ≈ 1–2 min single-threaded.

**O1 wipes.** The card's count forms fail. After a forced erasure the wiped agent makes 0.70 statements in calls 1…20, against 1.47 after a placebo call (real skeleton). So a pattern's count drops by about half in every world, also when the wipe costs it nothing: raw ΔV = −0.46 (all hits, dose form) and −0.51 (own hits) in the artifact-held world. Pseudo-pattern subtraction removes the mean but leaves sd 0.20 per pattern and a CI-excludes-0 rate of 0.20–0.40 in the null world.

| world (planted ΔV) | rate form A1: mean excess (sd) | P1 falsifier rate (A1, bootstrap CI) | card dose form: mean excess (sd) | I_K identified |
| --- | --- | --- | --- | --- |
| W_art (0) | +0.026 (0.075) | **0.00** (CI excludes 0: 0.10) | −0.05 (0.21) | 0.05 |
| W_ctx (−0.10) | −0.083 (0.071) | 0.30 | −0.09 (0.21) | 0.05 |
| W_ctx (−0.20) | −0.188 (0.072) | 0.75 | −0.14 (0.21) | 0.05 |
| W_ctx (−0.30) | −0.296 (0.071) | **0.90** | −0.18 (0.19) | 0.10 |
| W_reset (wipe resets the host's carry state) | −0.24 (0.18) | 0.45 | +0.31 (0.35) | 0.75 |

Bias of the rate form ≤ 0.03; the bootstrap CI form has size 0.00 for the falsifier and 0.10 for "CI excludes 0"; the combined form (bootstrap and pseudo spread) has power 0.40 at −20%, the pseudo-quantile form size 0.20. The others' response (b_oth) has no planted effect: mean −0.05 (sd 0.12); size 0.05 with the combined CI, 0.15 with the bootstrap CI. "Within ±5%" holds in only 40% of null-world replicates (sd 0.075), so P1's support side cannot be shown pattern by pattern; only its falsifier is powered. I_K is identified in 5–10% of the context-held worlds (random deletion does not change the pre-to-post MI) and in 75% of the reset world; κ_F is therefore mostly not identified, as P1 allows.

**O4 host relation.** Planted effect on own-repo commits and on role alignment together, by binomial thinning (exact relative truth).

| planted | A2 (activity held) commits: mean (sd) | A2 class rates (CI rule) | card form commits: mean (sd) | card form CI excludes 0 |
| --- | --- | --- | --- | --- |
| −0.20 | −0.236 (0.104) | parasitic 1.00 | −0.091 (0.124) | 0.30 |
| −0.10 | −0.140 (0.115) | parasitic 0.85 | +0.021 (0.137) | 0.15 |
| 0 | −0.041 (0.124) | **neutral 0.95**, parasitic 0.05 (commits CI excludes 0: 0.10) | +0.136 (0.149) | **0.35** |
| +0.10 | +0.057 (0.135) | neutral 1.00 | +0.251 (0.161) | 0.70 |
| +0.20 | +0.155 (0.146) | mutualist 0.35 | +0.365 (0.173) | 0.90 |

The card's form is biased by +0.14 at zero effect: hosting needs statements, and statements co-vary with commits within an agent. Holding activity removes most of it (bias −0.04). Alignment is unbiased in both forms (A2 mean +0.002 at zero). Power for the parasitic class is 0.85 at −10% and 1.00 at −20%; power for the mutualist class is 0.35 at +20% (both components must exceed +5% with CIs above 0).

**O2 hub losses and O3 operator actions** (single dated events; β = (L − mean placebo L) / s, with s the lost agent's share of the pattern's hits before).

| event | window | null world: "exceeds placebo 95th pct" (same weekday / any weekday) | hub world: β mean, exceeds (any weekday) | distributed world: β mean |
| --- | --- | --- | --- | --- |
| HL1 | 2 active days | 0.15 / 0.00 | 1.03, 0.00 | −0.73 |
| HL2 | 5 days (W3 vs W2) | 0.85 / **0.00** | 1.24, **0.95** | 0.33 (exceeds 0.00) |
| HL3 | 2 days | 0.60 / 0.10 | 0.79, 0.35 | −0.77 |
| HL4 (HL4b) | 2 (1) days | 0.80 / 0.55 (0.90 / 0.30) | 0.76, 0.35 (1.09, 0.15) | −0.50 (0.04) |
| OP1, OP2, OP3 (prevalence −20% planted) | 2 days | 0.35–0.70 / 0.05 | net −0.22 to +0.07; exceeds 0.00–0.15 (any weekday); net ≤ −20%: 0.05–0.45 | |

With 2–4 same-weekday placebo days the 95th-percentile rule has size 0.15–0.85. With 13–15 any-weekday days its size is ≤ 0.10 except HL4 (0.55) and HL4b (0.30), but its power is ≥ 0.8 only for HL2 (0.95). Day-to-day variation of a pattern (±30%) divided by the hub share s gives β a per-event sd of 0.3–2.

### Amendments (2026-10-09, before any real-data outcome)
- **A1 (O1, P1).** V_K is measured as K's share of expression events, not as a count. Primary statistic: ΔV_K,F = exp(b_rate) − 1, where b_rate is the F effect in a Poisson fixed-effects model (stratum agent | unit) of the wiped host's own K hits in calls 1…20, with offset log(the host's element events in calls 1…20) and the host's own K share in calls −20…−1 as covariate. With all hosts wiped and others unchanged, this is the pattern's relative loss. The others' response (b_oth, per unit dose π) is reported beside it with the combined CI. The CI is the agent-day bootstrap shifted by the pseudo-pattern median. The card's count forms are variants. P1's falsifier is read as written ("ΔV ≤ −10% with the CI below 0"), with "CI below 0" required of both the bootstrap CI and the pseudo-quantile band [b − q97.5, b − q2.5] of 100 frequency-matched pseudo-patterns. The bootstrap alone ignores real differences between element sets after a wipe (re-orientation statements), which synthetic patterns lack; this was seen on a code check with random element sets, not on a memeplex. Joint rule in the synthetic worlds: size 0.00 (falsifier) and 0.05 (CI excludes 0); power 0.65 at −20% and 0.90 at −30%. P1's support side ("within ±5%") is read on the median over distributed patterns, because single patterns cannot show it. Reason: the segment-position activity dip after a wipe halves every pattern's count (synthetic above).
- **A2 (O4, P4, K2).** The host relation is estimated at matched activity: log1p(statements) and log1p(non-pause calls) in the bin enter as covariates, beside the agent × day-part fixed effects and agent trends. A component counts toward a class only if its cluster-bootstrap CI excludes 0 in its direction. The card's form and the pseudo-pattern excess are variants. K2 is applied in the parasitic direction only (power 0.85 at −10%); a "no mutualist" result is inconclusive (power 0.35 at +20%).
- **A3 (O2, O3, P2, P3, K3).** Placebo days for the dated events use any weekday (13–15 days; the same-weekday set of 2–4 days is a variant). Untestable as tests (synthetic size > 0.10 or power < 0.8): HL1, HL3, HL4, HL4b, OP1, OP2 and OP3 prevalence. They are reported as descriptive numbers. HL2 is the one testable hub loss (size 0.00, power 0.95). P2 is therefore read on HL2 only; P3's prevalence part is descriptive. P3's colonial-A part (A before vs after, day-block bootstrap CI) is computed as written.

### Targets (fixed 2026-10-09 from H145's frozen memeplexes, before any H147 outcome on them)
H145 froze 15 qualifying memeplexes K01–K15 (`memeplexes.json`, md5 9b899c34…; all hub-free, h_K 0.13–0.56; 12 of 15 have DeepSeek-V3.2 as top host) and six role-text controls R0–R5. Labels are H145's fixed token rule. The card's targets map as follows:
- **Distributed** (h_K < 0.5): K01–K13, K15 (14 patterns). **Hub-centred** (h_K ≥ 0.6): none. K14 (h_K 0.56; 4 markers, 3 hosts) is neither.
- **P2:** no hub-centred pattern exists, so P2's contrast is untestable. β is reported for patterns in which the lost agent held ≥ 5% of the hits before the event (HL2 is the only testable event, A3).
- **P3:** "the DeepSeek-V3.2-centred pattern" = the memeplexes with top host DeepSeek-V3.2 (12). No memeplex carries the protections label, so OP3 has no target (n/a).
- **P4:** "the DeepSeek-V3.2-centred coordination pattern" = memeplexes with top host DeepSeek-V3.2 and label frameworks or governance (K03, K06, K07, K11, K15); the prediction holds for it if ≥ half of them are parasitic by the A2 rule. Verification = K01, K02 (must not be parasitic); no onboarding memeplex exists.
- **P5:** Spearman over the 15 memeplexes between the A2 commit effect and colonial A (excess over pseudo-patterns; H147's coarse E, see `analysis/run.py`).
- Role-text controls R0–R5 are run through the same pipeline and reported beside the memeplexes.

## Results
*Pending (real-data run waits for H145's memeplexes).*

## Notes
- 2026-10-09: written by the coordinator. Traps: own-repo commits must be cleaned (screenshot loop, other village's commits, mirrored pushes); forced wipes arrive with a chat backlog; the class × wipe sandwich test is anti-conservative (cluster bootstrap); `project_calls.label` carries over resets.
