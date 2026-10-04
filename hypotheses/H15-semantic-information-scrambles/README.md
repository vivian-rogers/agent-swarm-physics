# H15: Semantic information through natural scrambles: which information keeps agents and the swarm viable

**Status:** **round 1b done (2026-10-04, improved data; see "Round 1b" below):** on the work ledger, real failures and the context ledger the day-scale nulls stand (memory loss +0.29 SD on V*, newcomers +0.20, artifact switches −0.00 on work commits), and the forced-erasure cost is now an output number: −39% work commits for ten calls (7/9 periods), about 10% of a forced segment's work, unaffected by what the agent saves to memory (NE41 native, supported). D2.6 re-chose V* (I: V_eng, III: V_rel); V_files (distinct files per hour, outside the pre-registered pool) is the first homeostatic candidate. Natives: NE41 supported, NE16 mixed, NE29 supported. **Exploratory round 1 done (2026-10-03, non-holdout only).** The pre-registered "memory is load-bearing" predictions failed: no detectable day-scale viability cost of losing up to ~80% of memory (P1) or of starting with an empty memory (P4); the rewrite control behaved (P3). The pre-registered context test (P5) came out significantly opposite because of a task-phase confound; a post-hoc estimate that uses only the exogenous timing of forced consolidations finds that erasing the context window cuts write output by 33–53% for ~10 turns in 8/9 regime III periods. D2.6 (choosing V) was inconclusive in both regimes. Confirmatory script `analysis/confirm_ne30.py` written, dry-run only, **not run**. Pre-registration (mapping, viability-choice procedure, observables, null, predictions) was written **before any outcome around a scramble event was computed**; amendments are dated in Notes.
**Fields:** info theory, thermodynamics
**Origin:** HH43 → H01 D4.1.b (shortlist 2, item 9); Kolchinsky–Wolpert semantic information (`../hypohypotheses/HYPOHYPOTHESES.md`; `../promotion-shortlist.md`)
**Literature:** [Kolchinsky & Wolpert 2018](../../literature/kolchinsky-2018-semantic-information-autonomous-agency.md) (the framework); Sowinski et al. 2023 (plateau-then-collapse; via `physics-models/04-semantic-information`).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime; Memory state; Interaction (broadcast; exposure as in `exposure`); Action; Entropy (of behavior); **Semantic information (Kolchinsky–Wolpert)**, in a named variant proposed here, **"semantic information (natural-scramble variant)"** (defined under Model; to be added to DEFINITIONS.md by whoever owns that file).

## Standards (2026-10-04)
**Question served:** Q4 (which information is load-bearing: context, memory or artifacts).

| Impostor | Relevant? | How it was handled | Status |
| --- | --- | --- | --- |
| Scheduler field | partly | Same-day differencing against other agents and matched placebo days of the same agent (Null / baseline). The erasure dip compares calls within one segment. | removed |
| Exogenous field (kickoff/goal/operator) | yes | Same-day differencing removes common day fields; forced-erasure timing is set by the 41-turn cap. Artifact switches fall on goal-change days (118/172), and P5 carries a task-phase confound (Round 1b). | partly |
| Shared model priors | no | Within-agent event designs. | n/a |
| Contemporaneous convergence | no | No influence claim; chat-cut events (CC) number 3. | n/a |

**Inputs:** round 1b uses DQ4 work commits, `turn_outcomes.failed` and `error_class`, `activity_bins_fixed` and ledger resets. Still old: chat-cut detection uses the `exposure` table; V_out is undefined before #30.

**Two layers:** 30 replication folders. Natives: 3 (NE41 supported, NE16 mixed, NE29 supported).

**Confirm script:** `confirm_ne30.py` (NE30, NE33 tail, regime-III holdout), dry-run only. Re-freeze: yes; it was frozen on round-1 viability measures (stderr reliability, write turns) (round-1b synthesis, decision 2).

## Question
Kolchinsky–Wolpert: information is semantic, or load-bearing, if scrambling it lowers the system's viability. We can't run new swarms or replay agents, but the logs contain natural scrambles: memory loss and resets, a change in consolidation rate (NE14), newcomers with empty memories, room cuts that remove chat exposure, and widened history search (NE18). Which removals lower viability, by how much, and what fraction of the available information is load-bearing (η)? Practical payoff: which context actually keeps a swarm working.

## Model
**From:** `physics-models/04-semantic-information` (ΔV under scrambling, η = load-bearing fraction), with H01's `architecture.md` (viability candidates, D2.6 homeostasis rule for choosing V) and `notes/kolchinsky-qa-transcript.md`.

### Mapping onto Kolchinsky–Wolpert (KW)
- **System X:** one agent. Its state has three parts with different lifetimes:
  - long-term memory M (`agent_memories`; summarized without text in `memory_stats`), carried across sessions and days;
  - the in-context window C (the current session's turns and unread events), erased at every session end: at every `CONSOLIDATE` in regime III (≈ every 41 turns), at `STOP_USING_COMPUTER` before;
  - its own computer and workspace (files, clones), which we treat as part of the environment because other agents can't see it either way and we can't measure it.
- **Environment Y:** the rest of the village: other agents and their messages, the goal, the artifacts (repos, sites), operators.
- **Horizon τ:** one to three village days (day-level V), or ten computer-use turns (turn-level V, context scrambles only).
- **Stored semantic information** (KW Sec. 4) is carried by the correlation I(X₀;Y₀) at the start of the horizon. Memory is the store at the day scale; the context window is the store at the session scale.
- **Observed semantic information** (KW Sec. 5) is carried by the transfer Y → X during the horizon: the room's chat and events reaching the agent (`exposure`). H04 found that messages act through the agent's unread context with a delayed read-out, so the chat channel feeds C, which feeds M at consolidation.
- **What the natural scrambles actually do**, relative to KW's interventions:

| Scramble | What it removes | KW reading | Departure from KW's scramble |
| --- | --- | --- | --- |
| Memory loss (ML), newcomer (MN) | part or all of M | stored-information intervention at t₀ | an **erasure**: x₀ is replaced by a blank or truncated state, not redrawn from p(x₀). The marginal of X changes too (shorter memory, less to read), so ΔV_erasure = ΔV_scramble + (effect of the changed marginal). |
| Memory rewrite (MR) | line identities (hashes), size kept | a re-encoding | if the content is paraphrased, no correlation is removed: a **negative control** for the hashed-line measure of information. |
| Context erasure at consolidation (CF/CV) | C, keeping what the agent writes to M | KW's **coarse-graining intervention** p̂ᶠ(x₀\|y₀) = p(x₀\|f(y₀)), where the agent itself chooses f (what to save) | forced consolidations (the 41-turn cap) fix the *time* exogenously; the agent fixes *f*. If the agent's f were KW-optimal (least information that keeps viability), V would not drop. |
| Chat cut (CC: isolation, #focus, room splits) | part of the Y → X channel | observed-information (dynamic) intervention on p(x_{t+1}\|x_t, y_t) | a channel **cut**, not a shuffle: the agent gets fewer messages, not randomized ones. Less distraction is part of the effect, so negative value is possible. |
| NE18 history-search widening | nothing; it **adds** capacity from the village's stored past into X | anti-scramble | predicted sign opposite to a scramble. |
| NE14 consolidation-rate change | changes the erasure rate of C | dynamic intervention on the erasure schedule | bundled with the regime III switch (perma-computer-use, pause tool): **not identifiable**; catalogued only. |
| Artifacts (repos, sites) | — | environment-side (stigmergic) store | no non-holdout artifact scramble found (NE24 GitHub → GitLab is inside the NE21+NE23 holdout window). Artifacts enter as the functional viability V_out. |

- **Semantic information (natural-scramble variant)**, proposed for DEFINITIONS.md. For a natural scramble that removes a dose δ ∈ (0, 1] of a store or channel (fraction of memory size lost; fraction of exposure share lost; full erasure δ = 1), with viability V measured per agent-day:
  - **ΔV** = the difference between V after the scramble and its counterfactual without it, estimated by the AR-counterfactual difference-in-differences below. It is KW's value of information for an *erasure* (or cut) intervention, not for their marginal-preserving scramble.
  - **κ** = ΔV/δ, the viability cost per unit fraction removed (KW's "bang-per-bit" with δ in place of bits).
  - **η upper bound.** KW: S = the least information an intervention can keep while matching actual viability; η = S/I. Natural scrambles are not optimal interventions, so S is not point-identified. Two upper bounds are: (i) if V is flat for doses up to δ* (plateau-then-collapse), at most a fraction 1 − δ* of the store was needed, η ≤ 1 − δ*; (ii) if agent-chosen consolidations keep V, η ≤ the fraction they retain. A *lower* bound would need knowledge of which lines were removed, which the hashed-line data doesn't give.
  - "Information" here is a syntactic proxy: characters and distinct hashed lines of memory, and the share of the swarm's messages an agent is exposed to. It is not Shannon I(X;Y).

## Data scheme (`scheme/`)
- **Script:** `scheme/build.py` (all scramble detection uses scramble variables only, never outcomes).
- **Inputs (shared tables):** `memory_stats` (size, hashed-line diffs), `events_core` (CONSOLIDATE, SEARCH_HISTORY), `actions` (turns, errors), `artifact_mentions` (write verbs), `activity_bins` (engaged minutes), `exposure` + `chat_core` (chat channel), `rooms_timeline`, `roster`, `calendar`, `intentions` + `embeddings/intentions_bge_small.npy` (plan coherence). (H09's `consolidation_inflow.parquet` was planned as a cross-check but not used; consolidation segments come from our own turn counts between `CONSOLIDATE` events.)
- **Output:** `data/processed/H15-semantic-information-scrambles/`:
  - `agent_day.parquet`: one row per agent × non-holdout active day: the viability candidates, exposure share, memory summary, goal, regime, room;
  - `scramble_catalog.parquet`: one row per scramble event (type, agent, time, period, dose, flags);
  - `consolidations.parquet`: regime III consolidation segments with turn-level outcomes before and after (CF/CV); `consolidation_profile.parquet` (mean write/error rate by turn offset);
  - `v_choice.json` (D2.6), `synthetic.json` (axis F), `results.json` (all estimates), `confirm_dryrun.json`, `summary_lines.json`;
  - `_provenance.json`; per-period result JSONs in `G<NN>/`. Total 3.1 MB.
- **Holdout:** every row on a holdout day (`calendar.holdout` OR `holdout_mask`) is dropped before detection. Holdout scrambles (NE30, NE33 after 09-06, NE22, NE24) are listed from documentation only and go to the confirmatory script.
- The Claude Code agent (separate scaffold) is excluded.

## Viability: candidates and the pre-registered choice (D2.6)
*Written 2026-10-03, before computing any candidate.*

**Candidates** (agent-day, inside the day's active window):

| Code | D2 class | Definition |
| --- | --- | --- |
| V_out | functional (D2.3.a) | turns carrying a write verb (`git commit`, `git push`, `deploy`, PR/MR create or merge, repo create) per window hour, from `artifact_mentions` (source = action) |
| V_eng | structural persistence (D2.1) | fraction of the agent's window minutes in `activity_bins.state` ∈ {act, talk}: the agent keeps acting rather than sitting silent or idle (H09's traps) |
| V_rel | functional reliability | 1 − error fraction of the agent's computer-use turns (≥ 20 turns, else missing) |
| V_ord | informational order (KW's literal V = −S) | −(Miller–Madow entropy) of the agent's action-type mix that day (computer-use action ∪ event type; ≥ 20 actions) |
| V_coh | informational order of the plan | mean cosine similarity of consecutive intentions (session goal / nextSessionGoal embeddings) within the day (≥ 3) |

**Excluded** because they are mechanically functions of the scrambled variables: memory size or its set point (H09's most homeostatic variable), chat volume, exposure, context size.

**Choice procedure (D2.6: pick the V the agent visibly restores after shocks).** Run separately in regime I and regime III (II is too short); shocks are **not** H15 scrambles, so the choice can't be tuned to the tested effects.
1. Shocks: every boundary between two consecutive non-holdout goal periods in the same regime (NE34 quenches). Agents active on the two days before and on days 0 and 3 after (active-day indexing).
2. Per agent-shock: D₀ = V(day 0) − mean V(days −2, −1); D₃ = V(day 3) − same mean.
3. Displacement δ_V = median|D₀|; recovery R_V = 1 − median|D₃| / median|D₀|.
4. Placebo: 200 draws of pseudo-boundaries at random mid-period days (≥ 3 active days from a real boundary), same computation.
5. Eligible: defined and non-degenerate (≥ 50% of agent-days non-missing and non-zero) in ≥ 80% of the regime's non-holdout periods.
6. **Homeostatic:** δ_V > placebo p95 and R_V > placebo p95 and R_V ≥ 0.5. Choose V* = the homeostatic candidate with the largest R_V − median(R_placebo). If none passes, choose the largest R_V − median(R_placebo), declare D2.6 **inconclusive** for that regime, and give the other candidates equal weight in the results.
7. All H15 effects are reported for every candidate (D4.4 sensitivity); V* is primary.

## Scramble catalog: detection rules (pre-registered)
Non-holdout days only. Set point SP = trailing median of the agent's last 30 *compressed* snapshots (n_chars below the previous snapshot), needing ≥ 10.
- **ML, memory loss beyond normal consolidation:** n_chars < 0.5·SP, jaccard_prev < 0.3, tenure ≥ 3 days, and **persistent**: median n_chars of the next 5 snapshots < 0.7·SP. One event per agent-day (the first). Dose δ = 1 − n_chars/SP.
- **MG, glitch:** as ML but not persistent. Catalogued; secondary.
- **MR, rewrite:** jaccard_prev < 0.05 with 0.7 ≤ n_chars/previous ≤ 1.4, tenure ≥ 3, no ML within ±1 day. Negative control.
- **MN, newcomer (full erasure, δ = 1):** the agent's first active day, if tenure days 1–3 and a reference window (tenure active days 6–12, ≥ 3 days) are non-holdout.
- **CF / CV, context erasure:** regime III `CONSOLIDATE` events; the segment before it is counted in computer-use turns. CF = forced (segment of 41–42 turns, the cap); CV = voluntary (10–38 turns). Dose of stored transfer = lines_added / n_lines of the memory snapshot written at that consolidation (nearest `memory_stats` row within 180 s).
- **CC, chat cut:** an agent-day where the agent's exposure share s (messages by other agents it is exposed to / all messages by other agents that day) falls below 0.3× its median over the previous 5 active days *and* the agent is not in the most populated room; sustained ≥ 2 active days. Dose δ = 1 − s/s_pre. Known instances to check: GPT-5 alone in #rest 05-04 → 05-11 (#40); #focus 08-05 → 08-24 (#51).
- **NE18:** 2026-04-20, inside #38. Dose = the agent's SEARCH_HISTORY rate per window hour in #38 before 04-20.
- **NE14:** catalogued only (bundle; pre side partly in the holdout).

## Observables
All in units of V's within-period residual SD. Residual u_ad = V_ad − mean of the other agents' V on the same day (removes the shared field: goal, schedule, outages), z-scored by the period's residual SD.
- **O1 ΔV per ML / MG / MR event (AR-counterfactual DiD).** Pre = the 5 active days before the event day; post = the 2 active days after it (event day excluded; post truncated at the period boundary; event dropped if no post day). Counterfactual: û_post = μ_a + ρ^k (u_last pre − μ_a), with μ_a the agent's mean on non-event days of the period and ρ the regime's pooled AR(1) coefficient of u (exception (d), partial pooling). ΔV = mean(u_post − û_post). Companion: plain DiD (mean u_post − mean u_pre) and the event-study curve, days −5 … +5.
- **O2 dose response and η.** Across ML events (and MN at δ = 1), regress ΔV on δ; compare linear vs. hockey-stick (flat to δ*, then linear) by AIC. Report κ = ΔV/δ and, if the hockey-stick wins, η ≤ 1 − δ*.
- **O3 newcomer deficit (MN).** ΔV = mean u(tenure active days 1–3) − mean u(tenure active days 6–12). Exception (c): the join is the object; same-day differencing in u absorbs goal changes when the windows straddle a period boundary. Recovery: day at which u reaches the reference mean.
- **O4 context erasure (CF vs CV).** Turn-level V: write turn (V_out's verbs) and error turn (V_rel). dip = mean over the first 10 turns after the consolidation − mean over the last 10 turns before it. Report dip_CF, dip_CV, dip_CF − dip_CV (agent-day cluster bootstrap), and Spearman ρ(stored-transfer dose, dip) within CF.
- **O5 chat cut (CC).** ΔV as O1 over the cut days (≤ 5), dose δ from exposure share; return effect (first 3 days after s recovers) for reversals.
- **O6 NE18 (add).** Within #38, Δu = mean u(04-20 → 04-24) − mean u(04-02 → 04-17) per agent, regressed on pre-period search rate.
- **O7 summary of the information value of each store and channel:** per type, mean δ, ΔV, κ, η bound.
- **O8 swarm-level spillover.** Raw V (period z-scored) of incumbents on days 1–3 after a newcomer joins vs. days −3 … −1, against placebo dates in the same period.

## Null / baseline
- **Same agent, matched non-scramble days:** for each event, the same estimator at placebo days of the same agent in the same period with no catalogued event within ±3 active days (all placebo days; ≥ 3 needed). Event z = (ΔV − mean_placebo)/sd_placebo. Period statistic: mean ΔV over the period's events vs. 2,000 draws of one placebo per event (permutation p).
- **Other agents on the same day:** built into u (same-day differencing).
- **Selection null (main pitfall):** the pre-trend (OLS slope of u over days −5 … −1) of event agents vs. placebo pre-trends. A negative pre-trend means resets happen when agents are already failing; the AR counterfactual is primary because synthetic tests (below) show it removes regression-to-the-mean bias under AR(1) selection, while plain pre/post and plain DiD do not.
- **Cross-period:** random-effects (DerSimonian–Laird) meta-analysis of period means; never a pooled fit (exception (c): each event is a transition object; (d): ρ pooled within regime).
- **Rival models:**
  - **R1 "memory is decorative":** agents rebuild what they need from the environment (repos, chat, history search) within the post window, so ΔV_ML ≈ 0 (η_mem ≈ 0 at the day scale).
  - **R2 "chat is the carrier"** (H08 context-is-the-coupling, H04): the chat channel carries the load-bearing information, so |κ_chat| > |κ_mem|.
  - **R3 "selection only":** apparent ΔV comes from resets happening on bad days (pre-trend), not from the information lost.

## Prediction
*Written 2026-10-03, before running any outcome analysis on real data (D2.6 not yet run; V* unknown; statements apply to V* unless a candidate is named).*

| | Prediction | Falsified if |
| --- | --- | --- |
| P1 | **Memory is load-bearing.** ΔV_ML < 0: meta-analytic mean ≤ −0.25 SD with z ≤ −2; negative in ≥ 60% of periods with ≥ 2 events. | meta z > −2, or mean > −0.1 SD |
| P2 | **Dose response with a plateau.** \|ΔV\| rises with δ; hockey-stick beats linear (ΔAIC ≥ 2) with δ* ≥ 0.6, i.e. η_mem ≤ 0.4. Low confidence: doses are truncated at δ ≥ 0.5 by the ML rule. | slope ≥ 0, or linear wins with a CI on δ* reaching 0.5 |
| P3 | **Rewrites are free (negative control).** \|meta ΔV_MR\| < 0.15 SD, \|z\| < 2. | \|z\| ≥ 2 (then hashed-line turnover is not a neutral measure, or rewrites lose content) |
| P4 | **Newcomers pay for empty memory.** MN deficit ≤ −0.3 SD on V* and V_out (meta z ≤ −2), recovering within ~5 active days. On V_eng the deficit may be ≈ 0 or positive (novelty). | meta z > −2 on V* |
| P5 | **Context is load-bearing; the agent's own coarse-graining is not optimal.** dip_CF − dip_CV < 0 for write turns (95% CI excludes 0) in ≥ 2/3 of regime III periods; within CF, more stored transfer → smaller dip (ρ(dose, dip) > 0 for writes). | CI includes 0 in most periods, or the sign is reversed |
| P6 | **Chat has low value for individual viability.** \|ΔV_CC\| < 0.3 SD on V_out and V_rel; on V_eng ΔV_CC < 0 (chat triggers activity, H04/H09). | V_out ΔV_CC ≤ −0.3 SD with z ≤ −2 |
| P7 | **Adding access helps the heavy searchers (NE18).** Slope of Δu on pre-search rate > 0; expected n.s. (one period, ~13 agents). | slope < 0 with p < 0.05 |
| P8 | **Stored bits carry more viability than observed bits:** \|κ_mem\| > \|κ_chat\| (rival R2 predicts the reverse). | \|κ_chat\| > \|κ_mem\| with non-overlapping CIs |
| P9 | **Selection is present (R3 partially true).** Pooled pre-trend of ML events < placebo, z ≤ −1.5; the AR-counterfactual ΔV is less negative than the plain pre/post ΔV. | pre-trend z > −1.5 (then selection is not a problem here) |
| P10 | **No swarm-level spillover from newcomers.** Incumbent V* change after a join within the placebo 95% band. | outside the band |

Per-period predictions are in each `G<NN>/README.md`, written from the catalog (scramble variables only) before that period's outcomes were computed.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R1 memory decorative; R2 chat is the carrier (H08); R3 selection only.
**Locked holdout used for confirmation:** none yet. Planned (`analysis/confirm_ne30.py`, written, dry-run only, **not run**; criteria in `NE30/README.md`): NE30 (Gemini 3 Pro → 3.1 Pro, 03-05 → 03-16), NE33 tail, and the holdout regime III periods #43, #45–#50, #51 tail (forced-consolidation dip C3, memory losses C4).

Scored for round 1 (exploratory, non-holdout). Mapping = agent-level KW with erasure/cut interventions; windows = goal periods.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Every scramble and viability candidate comes from logged fields (memory sizes and hashed lines, roster, exposure, consolidation turn counts, write verbs, errors, action mix, intention embeddings). Departures from KW listed (erasure ≠ marginal-preserving scramble; "information" is a syntactic proxy). Not invariant: V_out is degenerate before 2025-10 (no write verbs), error flags differ by provider (bash vs GUI), D2.6 picks different V in regimes I and III. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | AR(1)+noise for the same-day residual checked with pooled autocovariances: regime I/II u is white (r₁ ≈ 0), regime III r₁ = 0.23 (V_eng), 0.46 (V_rel) with r₂/r₁ ≈ ρ. Stationarity within a period assumed, not tested; no Markov-order test. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Nulls: same-day differencing (shared field), unit-pooled placebo days (calibrated, A1), selection pre-trends. Only the context-erasure dip (post-hoc) clears them decisively; no memory scramble does. No day-blocked held-out likelihood. |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | The KW signature (plateau-then-collapse, P2) is untestable here: ML doses are truncated at 0.5, n = 12, and the synthetic power to prefer a hockey stick is 9%. |
| E interventional | predicts the change across a natural experiment | 1 | **Round 1b (2026-10-04): 0 → 1.** NE41 native: the forced-erasure work dip (−0.39, 7/9 periods) and its independence from the memory dose held as dated predictions on the DQ1 ledger and DQ4 work commits; NE29 accounting null held. Round 1: pre-registered interventional predictions failed: P1 (memory loss), P4 (newcomers), P5 (forced vs voluntary, significantly opposite). The post-hoc forced-consolidation estimate (an exogenous intervention: the 41-turn cap) is consistent across 8/9 periods but was not predicted; it becomes E evidence only if C3 confirms it. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Synthetic on the real skeleton (150 reps): null calibrated (5%), bias and coverage per counterfactual, power 41% (ML, −0.41 SD), 35% (MN), 17% (CC); a transient slump around a reset is not identifiable (bias −0.57; pre-trend catches ~30%); plateau unidentifiable. Results agree across kal / ar1 / did. |
| G ground truth | agrees with known structure | 1 | The rewrite negative control is null (P3). The forced cap appears as the 41-turn spike and the write-rate collapse at every consolidation. The D2.6 procedure found no homeostatic V, so it has not been validated against a known homeostatic variable. |
| H comparative | beats the named rivals | 1 | R1 ("memory decorative at the day scale") beats the memory variant (P1, P4). R2 (chat carrier) vs memory can't be decided (3 usable chat cuts; P8 point estimates favor R2, CIs overlap). R3 (selection) partly present (pre-trend z −1.4). The context variant beats R1 at the 10-turn scale (post-hoc). |
| I transfer | holds in other same-mode periods, including the holdout | 1 | The context-erasure dip holds in 8/9 regime III periods; the memory nulls hold across periods with events. Holdout not used. |

## Results by goal period
**Round 1b (2026-10-04):** each folder now has a `**Verdict (1b):**` line (same rule on the re-chosen V*; summary in "Round 1b" below); the table keeps the round-1 verdicts. Verdicts follow the pre-registered rule in each folder (V* only). Most regime III "failed" verdicts come from P5 (the forced-minus-voluntary contrast, significantly opposite); the post-hoc forced-erasure dip is shown alongside. Periods marked n/a had catalogued events that could not be estimated (first days of a period, < 4 non-event days, too few agents).

| Period | Role | Verdict | Key numbers (V*, effect in SD vs unit-pooled placebo; z) |
| --- | --- | --- | --- |
| [G03](goalperiod-subhypotheses/G03/README.md) | exploratory | n/a | no event estimable |
| [G04](goalperiod-subhypotheses/G04/README.md) | exploratory | mixed | V* = V_rel; MR -0.53 (z -1.2, n 1); MN +0.21 (z +0.4, n 1) |
| [G06](goalperiod-subhypotheses/G06/README.md) | exploratory | descriptive | V* = V_rel; MR +0.55 (z +1.3, n 1) |
| [G08](goalperiod-subhypotheses/G08/README.md) | exploratory | descriptive | V* = V_rel; MR +0.06 (z +0.1, n 1) |
| [G10](goalperiod-subhypotheses/G10/README.md) | exploratory | supported | V* = V_rel; MN -0.17 (z -2.1, n 3) |
| [G13](goalperiod-subhypotheses/G13/README.md) | exploratory | supported | V* = V_rel; ML -1.17 (z -10.5, n 2); MR -0.14 (z -1.3, n 2) |
| [G17](goalperiod-subhypotheses/G17/README.md) | exploratory | n/a | no event estimable |
| [G18](goalperiod-subhypotheses/G18/README.md) | exploratory | supported | V* = V_rel; MN -0.11 (z -0.2, n 1) |
| [G19](goalperiod-subhypotheses/G19/README.md) | exploratory | failed | V* = V_rel; MR +0.08 (z +0.2, n 1); MN +1.76 (z +3.0, n 1) |
| [G20](goalperiod-subhypotheses/G20/README.md) | exploratory | mixed | V* = V_rel; MR +0.21 (z +0.6, n 3); MN +0.22 (z +0.8, n 2) |
| [G21](goalperiod-subhypotheses/G21/README.md) | exploratory | n/a | no event estimable |
| [G23](goalperiod-subhypotheses/G23/README.md) | exploratory | n/a | no event estimable |
| [G24](goalperiod-subhypotheses/G24/README.md) | exploratory | n/a | no event estimable |
| [G25](goalperiod-subhypotheses/G25/README.md) | exploratory | n/a | no event estimable |
| [G26](goalperiod-subhypotheses/G26/README.md) | exploratory | n/a | no event estimable |
| [G27](goalperiod-subhypotheses/G27/README.md) | exploratory | descriptive | V* = V_rel; MR +0.70 (z +1.1, n 1) |
| [G30](goalperiod-subhypotheses/G30/README.md) | exploratory | n/a | no event estimable |
| [G31](goalperiod-subhypotheses/G31/README.md) | exploratory | mixed | V* = V_rel; MN +0.03 (z +0.1, n 1) |
| [G33](goalperiod-subhypotheses/G33/README.md) | exploratory | n/a | no event estimable |
| [G35](goalperiod-subhypotheses/G35/README.md) | exploratory | supported | V* = V_rel; MN -0.93 (z -1.5, n 1) |
| [G36a](goalperiod-subhypotheses/G36a/README.md) | exploratory | n/a | no event estimable |
| [G36b](goalperiod-subhypotheses/G36b/README.md) | exploratory | failed | V* = V_eng; CF−CV +0.0192 [+0.0090, +0.0302]; post-hoc CF dip -0.35 [-0.58, -0.08] |
| [G37](goalperiod-subhypotheses/G37/README.md) | exploratory | failed | V* = V_eng; CF−CV +0.0095 [+0.0026, +0.0164]; post-hoc CF dip -0.19 [-0.53, +0.34] |
| [G38](goalperiod-subhypotheses/G38/README.md) | exploratory | failed | V* = V_eng; MR -0.14 (z -0.3, n 2); CC -0.74 (z -1.2, n 1); MN -0.36 (z -0.5, n 2); CF−CV +0.0059 [+0.0005, +0.0113]; post-hoc CF dip -0.47 [-0.61, -0.27]; NE18 slope V* −0.15 (p 0.80) |
| [G39](goalperiod-subhypotheses/G39/README.md) | exploratory | failed | V* = V_eng; MN +1.28 (z +2.2, n 1); CF−CV +0.0228 [+0.0005, +0.0480]; post-hoc CF dip -0.33 [-0.46, -0.21] |
| [G40](goalperiod-subhypotheses/G40/README.md) | exploratory | mixed | V* = V_eng; CF−CV +0.0080 [-0.0133, +0.0301]; post-hoc CF dip -0.38 [-0.47, -0.29] |
| [G41](goalperiod-subhypotheses/G41/README.md) | exploratory | mixed | V* = V_eng; CF−CV +0.0016 [-0.0182, +0.0211]; post-hoc CF dip -0.53 [-0.61, -0.44] |
| [G42](goalperiod-subhypotheses/G42/README.md) | exploratory | failed | V* = V_eng; MN +0.20 (z +0.2, n 1); CF−CV +0.0147 [+0.0022, +0.0264]; post-hoc CF dip -0.48 [-0.58, -0.38] |
| [G44](goalperiod-subhypotheses/G44/README.md) | exploratory | supported | V* = V_eng; CF−CV -0.0096 [-0.0265, +0.0084]; post-hoc CF dip -0.48 [-0.64, -0.28] |
| [G51](goalperiod-subhypotheses/G51/README.md) | exploratory | failed | V* = V_eng; ML +0.08 (z +0.5, n 10); MG +0.31 (z +2.3, n 15); MR -0.26 (z -1.1, n 5); CC -0.12 (z -0.4, n 2); MN +0.18 (z +0.8, n 6); CF−CV +0.0104 [+0.0071, +0.0137]; post-hoc CF dip -0.45 [-0.49, -0.41] |
| [NE14](goalperiod-subhypotheses/NE14/README.md) | exploratory | n/a | catalogued only (bundle with regime II→III) |
| [NE18](goalperiod-subhypotheses/NE18/README.md) | exploratory | not supported | slope of Δu on pre-search rate: V* −0.15 (p 0.80), V_out +0.21 (p 0.40), n 12 |
| [NE27](goalperiod-subhypotheses/NE27/README.md) | exploratory | supported on V* (fragile) | 3 newcomers, V_rel deficit −0.17 (z −2.1; tight 4-incumbent null); V_eng +0.35 (z +1.1) |
| [NE30](goalperiod-subhypotheses/NE30/README.md) | confirmatory (locked holdout) | pending (confirmatory, not run) | criteria C1–C5 in `NE30/README.md`; dry run passes on stand-ins |
| [NE41](goalperiod-subhypotheses/NE41/README.md) | **native** (round 1b) | supported | forced-erasure work dip −0.39 [−0.42, −0.35] (7/9); ρ(stored memory dose, dip) +0.01; high − low dose tercile −0.05 [−0.10, +0.01] |
| [NE16](goalperiod-subhypotheses/NE16/README.md) | **native** (round 1b) | mixed | memory written at 99% of forced consolidations before and after the fix (manipulation negligible); 36c − 36b write-evidence dip −0.19 [−0.43, +0.12] |
| [NE29](goalperiod-subhypotheses/NE29/README.md) | **native** (round 1b) | supported | incumbents' work commits on the retirement day z +0.13; retiree made 2.3% of #30–#31 commits |

## Results
*Exploratory round 1, 2026-10-03, non-holdout days only (282 active days; 3,173 agent-days). Scripts: `scheme/build.py`, `analysis/choose_v.py`, `analysis/synthetic.py`, `analysis/run_scrambles.py`, `analysis/write_period_folders.py`, `analysis/figures.py`. Numbers: `data/processed/H15-semantic-information-scrambles/{v_choice,synthetic,results}.json`. Figures: `figures/F0_summary.pdf` (one page), F1 synthetic, F2 viability choice, F3 event studies, F4 context erasure, F5 value by store.*

### Scramble catalog (non-holdout)
| Type | What is scrambled | KW reading | n catalogued | n estimable on V* | Periods |
| --- | --- | --- | --- | --- | --- |
| ML memory loss (< 0.5 × set point, persistent) | memory | stored, erasure | 16 (7 GLM-5.2) | 12 | #13, #26, #38, #42, #44, #51 |
| MG memory glitch (restored within 5 snapshots) | memory | stored, transient | 22 | 15 | #30, #31, #37, #51 |
| MR rewrite (line Jaccard < 0.05, size kept) | line identities only | control | 84 | 17 | 26 periods |
| MN newcomer (empty memory) | memory, full (δ = 1) | stored, erasure | 20 | 20 | #4, #10 (NE27), #18–#20, #31, #35, #38, #39, #42, #51 |
| CC chat cut (exposure share < 0.3 × own baseline) | chat context | observed, cut | 10 | 3 | #35, #38–#41, #51 (#focus) |
| CF / CV context erasure at consolidation | context window (memory kept) | stored at session scale; agent-chosen coarse-graining | 18,611 / 12,216 | all | #36b–#51 |
| NE18 history-search widening | adds access to stored past | anti-scramble | 1 (dose = search rate) | 12 agents | #38 |
| NE14 consolidation-rate change | erasure schedule | dynamic | 1 | not identifiable | #35 → #36b |
| Artifact scrambles | — | environment store | none non-holdout (NE24 is in the holdout) | — | — |

3 of 16 memory losses fall exactly on the first day of a goal period (#38, #42, #44), where they can't be estimated within the period; that is itself a hint that agents rewrite memory when the goal changes.

### Viability choice (D2.6)
No candidate is both displaced by goal changes beyond placebo and restored by day 3 (R ≥ 0.5) in either regime (`figures/F2_viability_choice.pdf`).
- Regime I (17 goal-change shocks): only V_rel is displaced beyond placebo (0.37 vs p95 0.36); no candidate recovers (R between −0.49 and −0.08).
- Regime III (5 shocks): V_out, V_rel and V_ord are displaced (0.52, 0.63, 0.87 vs p95 0.26, 0.37, 0.51) but stay displaced (R −0.30, −0.33, −0.07): **goal changes move functional set points; nothing is restored within 3 days.**
- Fallback rule: V*(I and II) = V_rel (reliability), V*(III) = V_eng (engagement); D2.6 **inconclusive**, so all candidates are reported with equal weight.
- Reading: at the day scale, with goal changes as shocks, the swarm shows no homeostatic viability in KW's sense; what the agent "maintains" is goal-relative. The one clear restoration found in this round is at the turn scale: write output recovers within ~15 turns after a context erasure (F4).

### Synthetic validation (axis F)
150 replicates on the real skeleton (agents present per day, period boundaries, real event positions and doses); only V is simulated (AR(1) health + day noise + shared field).
- Null calibrated after amendment A1: false-positive rate 5% (ML), 4% (MN), 1–3% (CC); coverage 0.93 (kal).
- Power: ML 41% for −0.41 SD, 19% for −0.21 SD; MN 35% for −0.34 SD; CC 17% for ±0.45 SD.
- Selection (resets more likely when the agent is already failing, β = 1.5): kal −0.10, ar1 −0.12, did +0.14 → **kal chosen as primary** by the pre-set rule.
- Unidentifiable confound: a transient slump that causes the reset and depresses V for 2 days either side gives kal −0.57 (53% false rejections), did −0.31; the pre-trend flags it in only ~30% of replicates.
- Plateau (P2): with doses in (0.5, 0.8) and 12 events, a true hockey stick is preferred in 9% of replicates: P2 can't be tested here.
- Context erasure: comparing post with the *pre-window* is biased (+0.054 writes/turn under no effect) because voluntary consolidations follow writes; comparing with the agent-day base is nearly unbiased (+0.003) → base contrast chosen. The synthetic model had no task-phase structure *after* a consolidation, which is the confound the real data then showed.

### Outcome vs prediction
| | Prediction | Outcome (V* by regime unless stated; kal; SD of same-day residual) | Verdict |
| --- | --- | --- | --- |
| P1 | ΔV_ML ≤ −0.25, meta z ≤ −2 | −0.55 [−1.78, +0.68], z −0.9, 2 periods, heterogeneous: #13 (Grok 4, V_rel) −1.17 (2 events, error spike); #51 (V_eng) +0.08 (10 events). V_eng alone +0.09 [−0.19, +0.37]; V_out +0.12 [−0.26, +0.49] | **failed** (underpowered; the larger period is null) |
| P2 | hockey stick, δ* ≥ 0.6 | V_eng: linear slope +0.17, hockey ΔAIC 0.8 < 2; V_out slope −0.30, ΔAIC 0.1 | **untestable** (synthetic power 9%) |
| P3 | \|ΔV_MR\| < 0.15, \|z\| < 2 | −0.10 [−0.27, +0.07], z −1.1 (9 periods) | **holds** |
| P4 | newcomer deficit ≤ −0.3, z ≤ −2 | +0.15 [−0.18, +0.47]; V_eng +0.32 [+0.05, +0.59], z +2.3 (newcomers more engaged early); V_out −0.06 [−0.77, +0.64]; NE27 alone −0.17 on V_rel (z −2.1, fragile) | **failed** |
| P5 | dip_CF − dip_CV < 0 (writes); ρ(stored dose, dip) > 0 | +0.0096 [+0.0058, +0.0134] writes/turn, z +5.0 (positive in 8/9 periods, CI above 0 in 6/9); pooled ρ −0.06 | **failed, significantly opposite** (task-phase confound, see below) |
| P5′ (post-hoc) | — | forced erasure: writes in turns +1…+10 vs −20…−11 fall 33–53% in 8/9 periods (CI below 0), #37 n.s. (meta −0.44 [−0.49, −0.39]); voluntary −50…−74% | exploratory finding → C3 |
| P6 | \|ΔV_CC\| < 0.3 on V_out, V_rel; < 0 on V_eng | V_out −0.72 [−1.30, −0.14], z −2.4; V_rel +0.40 (n.s.); V_eng −0.22 (n.s.); 3 usable events (GPT-5.4 #38, #focus pair #51), the largest from Gemini 2.5 Pro whose output was already falling (pre-trend −1.6) | **falsified on V_out by rule**, but 3 events and selection-prone |
| P7 | NE18 slope > 0 | V* −0.15 (p 0.80); V_out +0.21 (p 0.40); n 12 | **not supported** (n.s.) |
| P8 | \|κ_mem\| > \|κ_chat\| | V_eng κ_mem +0.16 vs κ_chat −0.39; V_out +0.21 vs −0.91 | **not supported** (point estimates favor R2; CIs overlap) |
| P9 | ML pre-trend z ≤ −1.5 | −0.18 [−0.44, +0.08], z −1.4 | **not met** (borderline) |
| P10 | no newcomer spillover on V* | +0.01 [−0.20, +0.22]; V_ord +0.23, z +3.8 (incumbents' action mix gets more ordered after a join) | **holds** on V* |

### What it means in Kolchinsky–Wolpert terms
- **Day-scale memory carries little semantic information for these viability measures.** Full erasure (newcomers, δ = 1) and partial erasure (ML, δ ≈ 0.5–0.8) leave engagement, reliability, output, order and plan coherence within noise of the counterfactual a day or two later; newcomers are *more* engaged. In KW's notation ΔV(full scramble of M) ≈ 0 at τ = 1–3 days, so S_mem ≈ 0 and η_mem ≈ 0 at that horizon, within power (engagement CI excludes deficits beyond −0.2 SD for ML; newcomer engagement CI is entirely positive; output CIs are wide). The information that matters is re-acquired from the environment (repos, chat, the goal prompt, history search) faster than a day. This is rival R1.
- **The context window does carry it, at the 10-turn scale.** Erasing the context while keeping memory (forced consolidation, exogenous timing) cuts write output by about 45% for ~10 turns, after which it recovers: a viability drop and a visible restoration, which is what D2.6 looked for and did not find at the day scale. How much the agent writes to memory at that consolidation does not change the dip (ρ ≈ 0), so the agent's own coarse-graining f (what it saves) does not preserve the load-bearing part: in KW terms the self-chosen intervention is far from viability-preserving at this horizon, and memory is not where the session's semantic information is kept. Part of the dip may be fixed restart overhead (the first turn after a consolidation almost never writes); without text we can't split overhead from re-acquisition.
- **Stored vs observed.** The KW split maps onto the village like this: memory is the day-scale store (stored semantic information, intervened on by ML/MN); the context window is the session-scale store, filled by the observed channel (chat and events, H04's unread context). Round 1 says the semantic information sits in the short store fed by the observed channel, not in the long store. The direct test of the observed channel (chat cuts) has 3 usable events and can't carry weight.
- **Thermodynamic multiplier.** κ (ΔV per unit fraction removed) ≈ 0 for memory at the day scale; for the context window, ≈ −0.45 relative output per full erasure over 10 turns. No Landauer reading is claimed.

### Caveats
- Power is low for every day-level scramble (synthetic 17–41%); "no effect" means "no effect larger than the CIs above".
- 7 of 16 memory losses are one agent (GLM-5.2); the only strongly negative ML period (#13) is one agent (Grok 4) with two events and a reliability (error-rate) spike.
- Selection: the slump confound (failure causes the reset) is not identifiable; the pre-trend is weakly negative (z −1.4).
- 4 of 16 memory losses and most chat cuts fall on a period's first day or in 5-day periods, where the unit-of-analysis rule leaves no pre window. The estimable sample is therefore biased toward long periods (#51).
- The forced-vs-voluntary contrast is confounded by task phase: voluntary consolidations follow write bursts (visible in the pre-window, F4) and start new tasks. The post-hoc exogenous-timing comparison was chosen after seeing this; it needs the holdout (C3).
- V_out counts write *turns*, not their value; V_eng counts acting, not achieving; Jev progress scores were not used (draft only). Agent narration was not used.
- Memory "information" is a hashed-line and size proxy. Paraphrase looks like loss to the line hash (the rewrite control suggests that's harmless here).

## Round 1b (improved data, 2026-10-04)

### Pre-registered additions (written 2026-10-04, before running them)
*Written after the round-1b rerun of the round-1 pipeline (`H15_ROUND=r1b`: `build.py`, `choose_v.py`, `run_scrambles.py`) and before computing any artifact-switch outcome or any native-test statistic. The round-1 predictions P1–P10 are unchanged.*
- **AS, artifact-store scramble (HH261).** Detection from repo identity only: an agent's commit day where ≥ 50% of its DQ4 work commits go to repos it did not commit to in the previous 14 days, after ≥ 2 commit days in its previous 5 active days (172 events, #30 on). Matched control: commit days with all commits in already-used repos (CONT, 998), so both arms are conditioned on committing that day. Estimator as O1 (kal counterfactual over the 5 pre days, post = days +1, +2, event day excluded), effect = mean(AS) − mean(CONT) per period, DerSimonian–Laird across periods.
  - **P11 (HH261):** ΔV_AS < 0 on V_out (work commits per hour) and V_files, meta z ≤ −2; and |κ_AS| > |κ_ML| on V_out (losing the artifact context costs more than losing memory).
  - Counts against: meta z > −1 on V_out, or ΔV_AS ≥ ΔV_ML.
  - Caveat written now: switches are chosen by the agent (like voluntary consolidations), so a negative ΔV can also mean that agents switch when a task ends, and a positive one that they switch toward productive work. There is no non-holdout involuntary artifact scramble (NE24 is held out).
- **Native tests:** `goalperiod-subhypotheses/NE41/` (does the memory written at the wipe moderate the work dip?), `NE16/` (erasure with memory updates blocked vs allowed), `NE29/` (the longest memory lineage retired). Predictions are in those folders, dated before their runs.

### What changed
Everything runs behind `H15_ROUND=r1b` (`scheme/h15common.py`); the default `r1` path reproduces round 1 unchanged. Outputs: `data/processed/H15-semantic-information-scrambles/r1b/` (`results.json`, `v_choice.json`, `r1b_extra.json`, `calls.parquet`, `artifact_switches.parquet`); figures in `figures/r1b/`. Scripts: `scheme/build.py`, `analysis/choose_v.py`, `analysis/run_scrambles.py` (all switched), `analysis/r1b_extra.py` (new).
- **V_out = DQ4 agent work commits per window hour** (`canonical & ~imported & author_kind == "agent" & ~automated`), null before #30 (earlier zeros are ambiguous). Write turns are kept as `V_out_turns` (ρ 0.80 with work commits from #30 on). New: **V_files** (distinct files per hour) and **V_prog** (mean Jev v3 `progress_score`), reported but not in the pre-registered D2.6 pool.
- **V_rel = 1 − real-failure fraction** (DQ3 `turn_outcomes.failed` on bash/type turns; `error_class` platform failures on GUI turns). Round 1 counted `actions.error`, which is stderr (mean "reliability" 0.92–0.96 → 0.96–0.98).
- **V_eng on `activity_bins_fixed`** (ρ 0.73 with the buggy table; regime-III engagement 0.41 → 0.56).
- **Context erasure on the DQ1 ledger:** `reset_forced` (21,165 events, exactly the ledger count) vs `reset_consol & ~reset_forced` with ≥ 10 pre calls (12,950); outcomes per call (work commits mapped forward ≤ 10 min, 60,129 of 60,151 mapped; real failures; write evidence). Round 1 used its own turn counts and write turns.
- Scramble catalog unchanged (ML 16, MG 22, MR 84, MN 20, CC 10: detection uses memory, roster and exposure only). New AS catalog (172 switches, 998 continuation days).

### D2.6 rerun (viability choice)
| Regime | Round 1 V* | Round 1b V* | Notes |
| --- | --- | --- | --- |
| I (17 shocks) | V_rel (stderr), inconclusive | **V_eng**, inconclusive | V_out (work) ineligible: only #30–#31 have dense git |
| III (5 shocks) | V_eng, inconclusive | **V_rel (real failures)**, inconclusive | V_rel displaced 1.00 (p95 0.49) and recovers R +0.38 (p95 +0.01) but < 0.5 |

Out of the pre-registered pool, **V_files is homeostatic in regime III** (displacement 0.20 > p95 0.19; recovery R +0.66 > p95 +0.02 and ≥ 0.5): after a goal change the number of distinct files an agent touches per hour moves and is restored by day 3. It is the first variable in this project that passes D2.6, on 5 shocks, and it was added after round 1, so it is a lead, not a result.

### Round 1 vs round 1b (same estimators, non-holdout)
| | Prediction | Round 1 | Round 1b | Verdict (1b) |
| --- | --- | --- | --- | --- |
| P1 | ΔV_ML ≤ −0.25, meta z ≤ −2 (V*) | −0.55 [−1.78, +0.68], z −0.9 | **+0.29** [−0.05, +0.63], z +1.7 | failed (unchanged) |
| | ML on work output | +0.12 [−0.26, +0.50] (write turns) | +0.13 [−0.25, +0.50] (work commits) | |
| P2 | hockey stick | untestable | untestable (doses unchanged) | untestable |
| P3 | \|ΔV_MR\| < 0.15, \|z\| < 2 | −0.10, z −1.1 | +0.21 [−0.06, +0.49], z +1.5 | holds by the falsifier (\|z\| < 2); point now outside the 0.15 band |
| P4 | MN deficit ≤ −0.3 | +0.15 [−0.18, +0.47] | +0.20 [−0.13, +0.54]; work −0.13 [−0.63, +0.38]; V_prog **+0.31** [+0.06, +0.56] | failed (newcomers progress *more*) |
| P5 | CF − CV < 0 (writes) | +0.0097 [+0.0058, +0.0134], z +4.9 | work commits/call +0.0066 [+0.0011, +0.0121], z +2.3 (CI > 0 in 2/9) | failed, opposite (task-phase confound, weaker) |
| P5′ | (post hoc) forced dip | writes −0.44 [−0.49, −0.39], 8/9 | **work commits −0.39 [−0.42, −0.35], 7/9**; write evidence −0.26 [−0.30, −0.23], 8/9; real failures +0.27 [+0.12, +0.42] | replicated on independent timing and output data (NE41 N3, dated) |
| P6 | \|ΔV_CC\| < 0.3 on V_out | −0.72 [−1.28, −0.16], z −2.4 | −0.59 [−1.10, −0.09], z −2.3 (3 events) | falsified by rule (3 events) |
| P7 | NE18 slope > 0 | V* −0.15 (p 0.80) | V* −0.003 (p 0.99); V_out −0.02 (p 0.95) | not supported |
| P8 | \|κ_mem\| > \|κ_chat\| (V_out) | +0.21 vs −0.91 | +0.22 vs −0.74 | not supported (favours R2; CIs overlap) |
| P9 | ML pre-trend z ≤ −1.5 | −0.18, z −1.4 | −0.02, z −0.3 | not met (no selection visible) |
| P10 | no newcomer spillover (V*) | +0.01 [−0.20, +0.22] | +0.02 [−0.06, +0.11]; on work +0.22 [+0.04, +0.40] (k 2) | holds on V* |
| P11 | ΔV_AS < 0, z ≤ −2; \|κ_AS\| > \|κ_ML\| (new) | — | V_out **−0.00** [−0.17, +0.17] (k 2); V_files +0.15 (n.s.); κ_AS ≈ 0 vs κ_ML 0.22 | **failed** |

- **Artifact switches (P11).** 118 of the 172 switches fall on a goal period's first day (a new goal means a new repo), where the within-period estimator has no pre window and the goal change confounds them; only #38 and #51 have mid-period switches (54 estimable). Those cost nothing measurable against continuation days (#51: −0.01 SD, z −0.1; #38 +0.06). Losing the repo you were working in does not cost more than losing memory, at least when the agent chooses the switch.
- **Context erasure is the one robust scramble.** On the ledger's per-call timing and the git ledger's output, a forced wipe costs −39% work commits for ten calls, −26% write-evidence calls, and raises real failures +27%; the lost work is 2.5–13% of a forced segment's output (median ≈ 10%), matching H44 (4–11%). Memory written at the wipe does nothing (NE41: ρ +0.01; high- vs low-dose tercile −0.05 [−0.10, +0.01]).
- **Natives:** NE41 **supported** (N1–N3), NE16 **mixed** (the "never update memory" instruction had not stopped memory writes: 99% of forced consolidations wrote memory before and after; the dip did not shrink after the fix, −0.19 [−0.43, +0.12]), NE29 **supported** (losing the longest memory lineage: incumbents' work z +0.13; the retiree made 2.3% of commits).
- **Period verdicts (replication; V* re-chosen):** supported 5 → 2, failed 7 → 3, mixed 5 → 13, descriptive 3 → 3. The changes come from the re-chosen V* (regime III now V_rel, regime I V_eng) and from the forced-minus-voluntary contrast losing significance on work commits in 7/9 periods; they are replications, not new evidence.

### Scorecard (round 1b)
| Axis | Round 1 | Round 1b | Why |
| --- | --- | --- | --- |
| A | 1 | 1 | corrected measures (work ledger, real failures); V_out still undefined before #30, V* still regime-dependent |
| B | 1 | 1 | unchanged |
| C | 1 | 1 | the erasure dip clears the nulls; no memory or artifact scramble does |
| D | 0 | 0 | KW signature (plateau, η) still untestable |
| E | 0 | **1** | NE41 native: the forced-erasure dip and the no-buffering dose result hold with dated predictions on independent timing (ledger) and output (git) data; NE29 accounting null holds. Not 2: post hoc in origin, holdout not run |
| F | 1 | 1 | no new synthetic (round-1 design choices reused) |
| G | 1 | 1 | the 21,165 forced count reproduces the ledger; cap cost matches H44 |
| H | 1 | 1 | R1 (memory decorative) wins again; HH261's artifact-store rival fails |
| I | 1 | 1 | dip on work commits in 7/9, write evidence 8/9 periods |

**Scorecard (1b): A1 B1 C1 D0 E1 F1 G1 H1 I1.** Ratings (suggested): completeness 40 → 55, faithfulness 1.5 → 1.5, usefulness 2.5 → 2.5.

### What the work ledger changes about "viability"
Round 1's functional V counted write *turns*; on #30+ days work commits correlate 0.80 with them, so day-scale conclusions barely move (memory loss +0.12 → +0.13 SD on output). What changes is the reliability candidate (stderr → real failures) and therefore V* in both regimes, and the erasure numbers become output numbers: the 41-turn cap costs about a tenth of each agent's committed work, and the memory file written at the wipe does not recover it. The one homeostatic variable found so far (V_files) is an artifact-side output, which points the same way as H01 round 2: what an agent maintains is its artifact's growth, not its memory or its chat.

## Links to other hypotheses
Takes over H01 D4 (D4.1.b first); H01 D2.6 chooses the viability function; H08 (context is the coupling) supplies the mechanism; H09 (memory set point, `consolidation_inflow`); H04 (messages act through unread context); H05 (room events).

## Notes
- **From H44 (2026-10-04):** the erasure write dip replicates (−26% writes, −38% work commits; recovery τ ≈ 3 calls, within a 40-call sawtooth). The memory written at the wipe carries no measurable effect; restoration runs through re-reading artifacts.
- **Planned holdout reuse (2026-10-04):** H01 round 2's `confirm_r2.py` (not run) targets NE30 for crew-level continuity, a different statistic from this card's. It must be disclosed when either confirmatory run happens.
- 2026-10-03: promoted from shortlist 2 (HH43 → H01 D4.1.b (shortlist 2, item 9); Kolchinsky–Wolpert semantic information).
- 2026-10-03: **what had been looked at before this pre-registration** (all non-outcome or aggregate): memory-size time series of 18 agents (to design the ML rule; the sawtooth of normal consolidation is visible in every agent); counts of candidate ML events under two draft rules; the distribution of computer-use turns between consolidations (spike at 41 = the forced cap, ~28k of ~52k); room timelines of agents 6, 10, 29; monthly counts of write verbs and error rates (write verbs are essentially absent before 2025-10, so V_out is degenerate in most of regime I). No outcome was computed around any scramble event.
- 2026-10-03, **estimator refinement before the synthetic run and before any real-data outcome:** while coding O1 it became clear that a last-value AR forecast over-regresses when resets are selected on the *persistent* part of an agent's state (AR(1) + day noise). Three counterfactuals are therefore implemented in `analysis/h15lib.py`: `ar1` (the pre-registered form, with pooled lag-s autocorrelations r_s, identical to ρ^s under AR(1)), `kal` (AR(1)+noise state space, Kalman-filtered over the 5 pre days), `did`. **Rule fixed now:** the primary counterfactual for the real data is the one with the smallest |bias| in the synthetic selection scenario (β = 1.5, ρ_h = 0.6) among those with ≥ 90% placebo-null coverage under no effect; ties go to `ar1`. The other two are reported.
- 2026-10-03, **amendment A1 (after a synthetic smoke test, before any real-data outcome): placebo pool.** The pre-registered null used placebo days of the *same agent* only. On the synthetic village skeleton that pool has 10–35 overlapping days per event, its mean has its own sampling error that the period test ignores, and the two-sided false-positive rate under no effect was 17% (30 reps). The null now pools placebo days of **all agents in the same unit** (each with its own μ_a, windows near that agent's events excluded): false-positive rate 3–7%. Same-agent-only nulls are reported as a robustness column.
- 2026-10-03, **regime II rule (before D2.6 runs):** regime II units (#33, #35, #36a) use the regime I choice of V* (both have discrete sessions; II is too short for its own D2.6).
- 2026-10-03, the catalog was built (scramble variables only): ML 16, MG 22, MR 84, MN 20, CC 10 non-holdout events; 18,611 CF and 12,216 CV consolidations in regime III.
- 2026-10-03, **D2.6 run** (`choose_v.py`): inconclusive in both regimes; V*(I/II) = V_rel, V*(III) = V_eng by the fallback rule. Per-period predictions were then generated (`write_period_folders.py --predict`) from the catalog, V* and the synthetic primary, before `run_scrambles.py` touched real outcomes. The predict phase was re-run once later with identical inputs (catalog, `v_choice.json`, primary = kal), to add the "not estimable" bookkeeping; the prediction text is deterministic and unchanged.
- 2026-10-03, **synthetic run** (150 reps): primary counterfactual = `kal`, primary turn contrast = agent-day base (both by the rules fixed above). The first full run had a bug in the pre-trend null (NaN placebo pre-trends); fixed and re-run; the choice did not change.
- 2026-10-03, **bug fix after the first real run:** the memory snapshot written at a consolidation is logged microseconds *before* the CONSOLIDATE event, so the forward join left the stored-transfer dose missing for 95% of consolidations (the first ρ values had n ≤ 159). Fixed to a nearest-within-180 s join (coverage 99.9%). What I had seen: the first, nearly empty ρ values and the CF−CV contrast (unchanged by the fix).
- 2026-10-03, **post-hoc analysis** (after seeing P5 significantly opposite and the turn profile): forced-consolidation write dip, turns +1…+10 vs −20…−11 (`posthoc_rd` in results; labelled post-hoc everywhere). It is the basis of confirmatory criterion C3.
- 2026-10-03, **confirmatory script** `confirm_ne30.py` written after exploration, dry-run only. C1/C2 were made refutation-only after the dry run (stand-in values −0.93 and −0.20 SD showed effect-size thresholds are noise-dominated with 1–3 events); no holdout data was read.

## Round 2 redirects (2026-10-04)
*From the round-1 reflection (`writeup/round1-reflection/round1-reflection.pdf`).*
- **Where round 1 went sideways:** Memory turned out to be irrelevant at day scale; the context carries the load.
- **What the direction is really after:** Where does the swarm keep its knowledge? In artifacts and history, not in agents.
- **H15-R1.** Stigmergic memory: after a memory loss, agents re-acquire state from artifacts (file reads, history search) within a few turns; richer artifact trails mean faster recovery (E3).
- **H15-R2.** Semantic information is concentrated in the few items read first after a reset (the goal and the last messages).
- **H15-R3.** Memory notes are performative: their content rarely reappears in later actions.
