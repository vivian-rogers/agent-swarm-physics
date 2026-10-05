# H46: Style is a conserved charge

**Status:** **exploratory round 1 done (2026-10-04, non-holdout only). Refuted as stated; the fingerprint part holds.**
- **Style is not a conserved charge.** It moves beyond its own day-to-day band at goal switches (T_s = 0.69 vs content 0.86; 21/24 switches), across forced context erasures (0.56, while content does not move), for the #51 Prankster (percentile 1.00) and for #12 judges (3/4 at 1.00, content in band). It stays put where content also stays put (roster, scaffold) and after the nudger switch-off.
- **Style is a strong identity fingerprint.** Trained before and tested after a goal switch, style identifies agents at 0.76 (chance 0.15), content at 0.51; style wins at 22/24 switches.
- **Post hoc mechanism:** style drifts away from the agent's own mean as its context fills and snaps back after an erasure. That is a substrate charge plus a context-held excitation.
- **Kolchinsky–Wolpert:** style and content carry similar, small information about next-day output in #51, and both vanish once today's output is known.
- Predictions and nulls were written 2026-10-04 05:40 UTC, before any real-data statistic. Confirmatory script `analysis/confirm.py` written and dry-run, **not run**.
**Fields:** info theory, stat mech, sociophysics
**Literature:** [Kolchinsky & Wolpert 2018](../../literature/kolchinsky-2018-semantic-information-autonomous-agency.md) (semantic information, viability, scrambling); [Sowinski et al. 2023](../../literature/sowinski-2023-semantic-information-resource-gathering-agents.md) (plateau-then-collapse, low semantic efficiency).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime; Driving / external field (goal and day field); Agent state, **variant vector** (H13's *agent state (vector, chat agent-day, whitened)*); Semantic information (Kolchinsky–Wolpert), in H15's **natural-scramble variant**. Two named variants are proposed here (see Observables): **agent state (style, chat agent-day)** and **agent state (vector, chat agent-day, style-residualized)**.
**From:** HH170 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/04-semantic-information/`, `physics-models/11-vector-spins/`
**Data inputs (shared tables first):** `text_features` (H13's 20 style features), `embeddings/statements` + DQ5 `statements_style_resid32_bge_small.npy` / `statements_white32_bge_small.npy` / `chat_bge_small.npy`, DQ5 `statement_flags` (`self_repeat`), `period_units`, NE catalog, DQ1 `context_ledger_turns` (`reset_forced`, `reset_consol`, `reset_session`), DQ4 `work_daily` (agent work), DQ6 `ground_truth_labels` (#51 roles, #12 teams and judges), `roster`, `rooms_timeline`.

## Standards (2026-10-04)
*Documentation pass against `STANDARDS.md`. No analysis was re-run. H46 has no round-1b section; round 1 already ran on most corrected inputs.*

**Question served:** Q2. The card separates the agent's substrate (style, a model prior) from its state (content). Q4 second: the Kolchinsky–Wolpert test asks what information style carries about output.

| Impostor | Relevant? | How it was handled | Status |
| --- | --- | --- | --- |
| Scheduler field | no | Day-level displacement against the agent's own placebo transitions; no activity statistic. A post hoc gap-matched placebo removes the weekend gap. | n/a |
| Exogenous field (kickoff/goal/operator) | yes | Goal switches are the intervention. The day-demeaned variant removes the goal/day field but is not used for verdicts (O1). The goal-switch style shift sits in topic-adjacent features (PH2). Close by residualizing style on `goal_fields` topic directions (§1, row 2). | partly |
| Shared model priors | yes | The impostor is the object. Content uses DQ5 `style_resid`; the fingerprint is also tested within Anthropic agents (P7). Lab-dependent style susceptibility is post hoc (PH5). | removed |
| Contemporaneous convergence | no | No copying or influence claim. | n/a |

**Inputs:** round 1 uses DQ5 `style_resid` and `statement_flags`, ledger reset flags, the DQ4 work ledger and DQ6 ground truth. Activity, failures and leading-@ are not inputs. Still old: content uses bge only; gte was not run (axis F).

**Two layers:** 37 replication folders (32 periods plus 5 class folders: NE34, NE42, NE43, NE32, NE14). Native tests: 4 (`G12`, `G51` and `NE41` failed; `G44` descriptive).

**Confirm script:** `analysis/confirm.py` exists, dry-run only, built on the corrected inputs (C1–C7). No re-freeze needed. Adding gte as a sensitivity before the run would close the model-dependence gap.

## Question
Is an agent's style vector invariant under every natural experiment (context erasure, room cuts and merges, goal switches, roster changes, scaffold steps, nudger off) while its content is not, so that style belongs to the substrate, carries no semantic information about viability, and works as an identity fingerprint?

## Design: two layers (Vivian, 2026-10-04; see `infra/data-quality/QUEUE.md`)
- **Replication:** the common estimator on every eligible goal period (comparable phase-diagram points). Period README role: `replication`.
- **Period-native tests:** 2–4 goal periods (or NEs) whose setup gives special leverage for this question, each with its own observable, null, ground truth or intervention, its own dated prediction, and period-specific tooling where needed. Period README role: `native`.

## Model
**From:** `physics-models/11-vector-spins/` (agent states as vectors; agent fields vs day fields) and `physics-models/04-semantic-information/` (Kolchinsky–Wolpert value of information under scrambles).

**H46 variant: a two-channel agent state with a conserved charge.** Each chat message m of agent i on day d carries two vectors:
- a **style vector** x_m ∈ R^17 (H13's 20 features, type-controlled, below),
- a **content vector** y_m ∈ S^31 (regime-whitened bge embedding with the linear style part removed, DQ5).

The model is
  x_m = q_i + η_{i,d} + ε_m,      y_m ∝ c_{i,d} + ξ_m,
where q_i is the agent's **style charge** (a constant of the substrate: the weights), η_{i,d} is ordinary day-to-day style jitter, and c_{i,d} is the content **state**, driven by the goal field g_{u,d}, the room, the agent's context window and its role. A natural experiment b at time t_b is an operator on the environment (goal, room, context, roster, scaffold, drive). The hypothesis is that every such operator commutes with q_i:
  q_i(after b) = q_i(before b)   for every NE class,   while c_{i,·} jumps.
"Conserved" is operational: the boundary displacement of x is drawn from the same distribution as the agent's ordinary day-to-day displacement (the placebo band), while the boundary displacement of y is not.

**Kolchinsky–Wolpert reading.** System X = one agent; environment Y = the rest of the village. Viability V = the agent's own output on the next active day (DQ4 agent work). The claim "style is substrate, not state" means: the agent's day-to-day style fluctuations carry no information about its next-day V beyond its identity (scrambling style across the agent's own days leaves V's predictability unchanged), whereas content fluctuations do. Between agents, style can still correlate with V through identity (syntactic, not semantic information). This is the observational bound version: we cannot intervene, so we estimate cross-validated predictive information and compare with the within-agent scramble null.

**Rivals.**
- **R1, style is a state too (style accommodation / in-context self-imitation):** style moves at boundaries that change the context (erasures, room merges) or the register asked for (personas, debates, judging), by about as much as content.
- **R2, task leakage:** style "moves" at goal switches only through message-type mix (length, code blocks, URLs); after the type control it is conserved. This rival is folded into the primary statistic (type-controlled style).
- **R3, nothing moves:** content does not move beyond day-to-day variability either, so the boundary is not a perturbation and conservation is untestable there.

## Data scheme (`scheme/`)
Script: `scheme/build.py` (shared tables only; drops every holdout row via `calendar.holdout` and `common.holdout_mask`; no text read or written).
- **Inputs:** `text_features` (20 style features), `embeddings/statements` (row map), `statement_flags` (`self_repeat`, bge rule: cosine > 0.95 to the same agent's earlier statement that PT day), `period_units`, `roster`, `context_ledger_turns` (reset flags), `work_daily` (agent level), `ground_truth_labels` (`preferred & ~holdout`), `rooms_timeline`.
- **Transform:**
  1. Messages: agent chat rows of `text_features` with `holdout == False` and `holdout_mask == False`; Claude Code agent (19) and the two fine-tuned leaders (28, 30) excluded from the common estimator (28 is used only in the G44 native test). Joined to their `statements` row (srow) for content vectors.
  2. Style standardization: each feature winsorized at its 0.1 % / 99.9 % non-holdout quantiles and z-scored on non-holdout messages (one global scale, so periods and regimes share a ruler: exception (a)).
  3. **Type control** (the message-type-mix null, R2): within each regime, the 17 features other than `log_chars`, `backticks`, `urls` are regressed (OLS, non-holdout) on message-type covariates: a piecewise-linear spline of `log_chars` (knots at the quartiles), `has_code` (backticks > 0), `has_url` (urls > 0). The residuals (17-d) are the **type-controlled style** (primary). The raw 20-d standardized vector is the secondary style.
  4. Unit ids from `period_units`; NE43 (2026-08-21) added as an extra split inside #51 (it is not a `period_units` boundary).
  5. Boundary catalog (below) and NE41 message-pair table (consecutive deduplicated chat messages of an agent on one PT day, labelled by the resets that fall between them in `context_ledger_turns`).
- **Output:** `data/processed/H46-style-conserved-charge/` (`messages.parquet`, `boundaries.parquet`, `ne41_pairs.parquet`, `_provenance.json`, and analysis outputs in `G<NN>/`, `NE<NN>/`, `synthetic/`). Content vectors are not copied: analysis reads them from the shared `.npy` files by `srow`.
- **Regimes covered:** I, II, III (non-holdout days). Content comparisons stay within a regime's whitening basis; the one cross-regime boundary (NE14, 36a → 36b) uses unit-normalized raw 384-d bge vectors for content.

## Candidate goal periods and boundary classes
**NE classes (common estimator, day level):**

| Class (folder) | Boundaries (non-holdout both sides) |
| --- | --- |
| Goal switches (NE34) | adjacent non-holdout goal transitions: 2→3 … 7→8, 10→11, 11→12, 12→13, 16→17 … 20→21, 23→24 … 26→27, 30→31, 35→36, 36→37, 37→38, 38→39, 41→42 (24). Sensitivity: transitions that skip one held-out goal and no NE window (8→10, 21→23, 42→44). 39→40 and 40→41 go to the rooms class. |
| Rooms (NE42) | NE42 merge (39→40, 05-04) and split (40→41, 05-11); #51 `#focus` opened (51f→51g, 08-05) and closed (51g→51h, 08-24). NE15 (03-16) is excluded (its pre-side is held out). |
| Nudger off (NE43) | 2026-08-20 → 08-21 inside #51. |
| Roster (NE32) | within-period roster joins/leaves with no other step change (4a→4b, 4b→4c, 18a→18b, 18b→18c, 19a→19b, 20a→20b, 31a→31b, 31b→31c (NE29), 38b→38c, 38d→38e, 42a→42b, 44a→44b, 51a→51b (NE32), 51b→51c, 51c→51d, 51d→51e, 51h→51i, 51i→51j, 51j→51k (NE33), 51k→51l (NE33)); incumbents only. |
| Scaffold (NE14) | NE02 (6a→6b), NE03 (10a→10b), NE04 (12a→12b), NE06 (20b→20c; 20c→20d with a join), NE07 (21a→21b with a join), NE10 (30a→30b), NE11 (31c→31d), **NE14** (36a→36b, regime II→III), NE16 (36b→36c), NE17 (38a→38b), NE18 (38c→38d). |
| Context erasure (NE41) | turn level, native (below). |

**Native tests:** NE41 (forced erasures, turn level), G51 (#51 private roles: the Prankster and the media roles; NE38 role reassignment of Claude Opus 5), G12 (#12 debates: assigned sides, rotating judge), G44 (the H23 distilled leader).

**Replication:** every non-holdout goal period with ≥ 3 agents having ≥ 2 eligible agent-days (G12, G44 and G51 carry the replication estimator inside their native READMEs).

## Observables
*Written 2026-10-04 05:40 UTC, before any real-data style or content statistic. Sampling-design facts seen: message counts per agent-day and period, reset counts, roster, role names, #12 team/judge windows, the leader's message count (27 rows for agent 28).*

**Eligible statements:** non-holdout agent chat messages, not `self_repeat`. **Eligible agent-day:** ≥ 3 eligible messages.

**O1. Boundary displacement, scaled by the agent's own day-to-day variability (conservation test, day level).**
- Day means x̄_{i,d}, ȳ_{i,d} and their sampling variances v_{i,d} = tr(S_{i,d})/n_{i,d} (S = within-day scatter).
- Unbiased squared displacement between two days: D(d, d′) = ‖x̄_d − x̄_{d′}‖² − v_d − v_{d′} (removes message-sampling noise, so days with few messages do not look like jumps).
- **Boundary transition** of agent i at boundary b: its last eligible day before b and its first eligible day after b (adjacent active days in agent time). Block variant (sensitivity): up to 3 eligible days on each side, pooled.
- **Placebo transitions** ("matched times"): the agent's adjacent eligible-day pairs within one unit (no step change between), not straddling NE43, within ±21 calendar days of b (widened to ±42 if fewer than 4), in the same content basis.
- **Percentile** r_{i,b} = (#{D_p < D_b} + ½ #{D_p = D_b}) / n_p. Under exchangeability E[r] = ½.
- **Class statistic** T = mean of r over (agent, boundary) pairs, separately for style (type-controlled, primary; raw, secondary) and content (style-residualized, primary; raw whitened, secondary).
- **Day-demeaned variant:** x̄ and ȳ minus the equal-weight mean over agents present that day (removes the goal/day field: agent-specific displacement only). Reported, not used for verdicts.

**O2. Fingerprint across boundaries.** For each day-level boundary with ≥ 3 agents eligible on both sides: day-demeaned agent-day vectors; train a nearest-centroid classifier (diagonal scaling by the pooled within-agent SD) on up to 3 pre-boundary days per agent, test on up to 3 post-boundary days. Balanced accuracy vs chance 1/N. Ceiling: leave-one-day-out accuracy within the pre side. Retention = cross / ceiling. Same for content. Within-family variant: Anthropic agents only (the largest family), chance 1/N_A. Message-level style accuracy reported descriptively.

**O3. Kolchinsky–Wolpert information about viability.**
- V_{i,d} = log(1 + commits + API content writes + API MR/PR writes) from DQ4 `work_daily` (agent level: canonical, not imported, agent-authored, not automated). Periods #30 onward (dense ledger).
- Target: V on the agent's next active day in the same unit. Predictors: the agent-day style mean (type-controlled) or content mean, both **two-way demeaned** within the period (agent mean and day mean removed; V likewise).
- Ridge regression (penalty by generalized cross-validation), leave-one-day-out cross-validated R²; information I = −½ log₂(1 − max(R², 0)) bits (Gaussian approximation).
- **Scramble null** (KW's intervention, observational version): permute each agent's predictor days among themselves (V fixed), 200 draws; p = share of draws with R² ≥ observed.
- **Identity (syntactic) channel:** agent-mean style vs agent-mean V across agents, leave-one-agent-out ridge R², reported separately.

**O4. NE41 (turn level, native).** Consecutive eligible chat messages (m, m′) of one agent on one PT day. Label: *forced* (exactly one reset between them, a forced consolidation), *voluntary* (exactly one, a voluntary consolidation), *within* (no reset of any kind between them: same context). Pairs with session resets or several resets are dropped.
- Distances: style ‖x_m − x_{m′}‖²; content 1 − cos(y_m, y_{m′}).
- Strata: agent × log₁₀ time-gap bins (0.25 decades). Each crossing pair gets its percentile among same-stratum *within* pairs (≥ 5; otherwise agent-free gap bin within the unit).
- T_forced, T_voluntary = mean percentile, per regime-III unit and overall. The time gap is the recency confound (H29), and the stratification removes it.

**O5. Native observables.**
- **G51 personas.** Incumbents with regime-III non-holdout data before #51 (agents 6, 10, 12, 13, 14, 16, 17, 18, 20–27, 29). Block displacement: the last ≤ 3 eligible days of the agent before #45 vs the first ≤ 3 eligible days in #51 (07-06 → 07-08), against placebo block pairs from #36–#44 and #51 non-holdout with a matched calendar gap (≥ 21 days apart). Groups (fixed now from DQ6 role names and `role_class`): **Prankster** (agent 10, GPT-5; the one role whose description asks the agent to act on others for effect), **media** (`role_class == media` among incumbents: 12, 16, 18, 22), **other** roles. Style percentile per agent; group contrast (Mann–Whitney).
- **NE38 (07-29), Claude Opus 5 (agent 40) reassigned game dev → mathematician.** Single-agent day-level and 3-day-block displacement across 07-29 vs its own placebo transitions in #51. Content should jump; style should stay.
- **G12 debates.** Agent × debate message sets within the DQ6 debate windows (10 debates, 7 agents).
  - (a) Fingerprint: train on debates 1–5, test on 6–10 (style vs content).
  - (b) Debate switch: displacement between an agent's consecutive debates vs its own within-debate split halves (placebo).
  - (c) Assigned role: Claude Opus 4.1 (agent 9) judged 6 debates and argued in 4. Leave-one-debate-out judge/debater classification from its style vs from its content; for the four one-time judges, the percentile of the judge window's distance to their own debater centroid.
  - (d) Assigned side: within-agent permutation test of side (gov/opp) on style displacement.
- **G44 leader.** The fine-tuned leader's (agent 28) chat messages in #44: nearest-centroid agent (style, then content) among agents with regime-III non-holdout data (#38–#44 centroids, leader window excluded), and the rank of base Kimi K2.6 (agent 25).

**Multiplicity.** Verdicts are per NE class (6 classes; Holm across classes, separately for style and content), per native test, and per replication period (templated, labelled as such). The class statistics are the confirmatory-style numbers; per-boundary and per-period values are descriptive points.

## Null / baseline
*Written 2026-10-04 05:40 UTC, before any real-data style or content statistic.*
- **Placebo boundaries at matched times** (primary): the agent's own adjacent-day transitions inside units near the boundary (O1); within-debate halves (G12); within-context message pairs at matched time gap (NE41); matched-gap block pairs (G51).
- **Randomization test** for T: each (agent, boundary) rank replaced by an independent uniform rank in {0 … n_p}; 20,000 draws, one-sided. **Boundary-level test** (conservative, shared shocks): Wilcoxon signed-rank of per-boundary mean r against ½ (classes with ≥ 5 boundaries). Bootstrap CI over boundaries, then agents.
- **Message-type mix (R2):** type-controlled style is primary; raw style is reported next to it. Genre is held fixed (chat only; intentions are a different genre and are not used).
- **Self-repetition:** DQ5 `self_repeat` dropped (H12's rule); all-message sensitivity for NE41.
- **Fingerprint chance:** 1/N (balanced accuracy); label-permutation null for G12 and G44.
- **KW scramble null:** within-agent permutation of predictor days (O3).
- **Rivals:** R1 (style is a state), R2 (task leakage), R3 (nothing moves).

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R1 style-as-state (accommodation, in-context self-imitation), R2 task leakage, R3 nothing moves.
**Locked holdout used for confirmation:** none yet (planned: NE15 room split, NE30 same-family succession, NE21+NE23 nudger off/on, #51 tail; script `analysis/confirm.py`, not run).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Style = H13's 20 features (`text_features`), type-controlled per regime; content = DQ5 style-residualized whitened bge; placebo = own within-unit day transitions; all listed under Observables. **Not family-invariant:** style susceptibility differs by lab (PH5: non-Anthropic agents moved into #51, Anthropic did not; p = 0.04, post hoc). The 20 features mix formatting, punctuation, pronouns and content-adjacent rates (digits, uppercase), so "style" is partly topic. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Day-level stationarity is built into the placebo (within-unit transitions), and roster and scaffold boundaries sit at ½ for both channels. **Markov order fails at turn level:** style depends on position in the context window (PH3: monotone drift from −2.3 to +1.1, reset at erasure), so the agent alone is not the state. No time-rescaling audit. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | The estimator holds size on synthetic data at village sampling and on the real roster and scaffold classes. The *conservation* model fails its main test: style moves in 2 of 4 informative classes (goal switches, erasures). The fingerprint beats chance at every goal switch and beats content at 92% of them. No held-out-day likelihood comparison. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | Unfitted fingerprint: style 0.76 vs content 0.51 across goal switches (retention 0.91 vs 0.72). Leader (G44): base model Kimi K2.6 is rank 2 by type-controlled style and rank 1 by raw style (power-limited, 16–20 messages). Failed: the KW signature (style ≈ content information in #51; between-agent identity channel R² > 0 in only 2/11 periods). |
| E interventional | predicts the change across a natural experiment | 1 | Six NE classes, the #51 persona onset, NE38 and the #12 judge assignment were used as interventions. The predicted invariance failed at goal switches, at forced erasures (exogenous timing), for the Prankster and for judges. It held at nudger-off, where equivalence could not be established with one boundary. The failures are informative: style responds to context and register. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | `analysis/synthetic.py`: size and power at real counts (a style shift of 0.5 day-jitter SD is detected at 100% of goal-switch replicates). It found and fixed two flaws before the real run: the equivalence rule is underpowered in small classes (A1), and coarse gap strata leave a recency confound at NE41 (A2). Preprocessing variants: raw vs type-controlled style, residualized vs raw content, day-demeaned, dedup vs all messages, all agreeing. Not done: second embedding model, alternative style feature set. |
| G ground truth | agrees with known structure | 1 | DQ6 roles, judges and teams (#51, #12); the leader's known base model (G44); families are separable by style (consistent with H13). |
| H comparative | beats the named rivals | 0 | R1 (style is partly a state that follows context and register) beats H46 at erasures, judging and personas. R2 (task leakage through length, code, links) does not explain the goal-switch shift (type control leaves T_s at 0.69); the excess sits in digit and uppercase shares, a broader leakage that R2 as defined does not cover. R3 (nothing moves) holds for roster and scaffold. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Not run on the holdout. Across periods, conservation fails consistently: the style shift at goal switches has the same sign at 21/24 boundaries. The replication layer gives 7 supported, 11 failed, 9 mixed and 5 descriptive points (templated thresholds, 4–15 agents each). The identity fingerprint transfers everywhere. |

## Prediction
*Written 2026-10-04 05:40 UTC, before running the analysis on real data.*

**Verdict rules per class (fixed now).** *content moves*: T_c > ½ with randomization p < 0.05 (Holm over classes) and, with ≥ 5 boundaries, boundary-level Wilcoxon p < 0.05. *style moves*: the same for type-controlled style. **Conserved** = content moves, style does not, (T_s − ½) ≤ (T_c − ½)/3, and the upper 95% CI of T_s ≤ ½ + m (m = 0.10 day level, 0.05 turn level). **Broken** = style moves and (T_s − ½) > (T_c − ½)/3. **Uninformative** = content does not move. Anything else is **partial**.

- **P1 goal switches (NE34):** content moves strongly (T_c ≥ 0.70); style conserved (type-controlled T_s ≤ 0.60). Raw style may leak (T_s,raw up to 0.65), and the type control removes most of it (R2). *Falsifier:* type-controlled style broken.
- **P2 erasures (NE41, forced):** content moves beyond gap-matched within-context pairs (T_c in 0.53–0.65); style conserved (|T_s − ½| ≤ 0.03). Voluntary consolidations shift content more than forced ones (agent-chosen task boundaries). *Falsifier:* T_s ≥ 0.55 with p < 0.05 (in-context self-imitation: R1).
- **P3 rooms (NE42):** content moves (T_c ≥ 0.65); style conserved.
- **P4 nudger off (NE43):** content barely moves (T_c ≤ 0.6, likely uninformative); style conserved (T_s within band).
- **P5 roster:** incumbents' content moves little (T_c ≈ 0.55, possibly uninformative); style conserved.
- **P6 scaffold:** style conserved at the small steps. **NE14** (regime II→III: chat now written from inside continuous computer use) is where the hypothesis is most at risk; the hypothesis predicts conservation there too. My prior: about 40% that NE14 breaks it.
- **P7 fingerprint:** style balanced accuracy across goal switches ≥ 3× chance at ≥ 80% of boundaries, retention ≥ 0.8; content retention ≤ 0.6; style cross-boundary accuracy > content's at ≥ 2/3 of goal switches. Within-family (Anthropic only) style accuracy above chance at ≥ 2/3 of boundaries. *Falsifier:* style retention < 0.6 at goal switches.
- **P8 Kolchinsky–Wolpert:** within-agent style fluctuations carry ≈ 0 information about next-day output (scramble-null p ≥ 0.05 in ≥ 80% of periods; pooled I_style < 0.02 bits); content carries more (pooled I_content > I_style, and > 0 at p < 0.05 by Stouffer combination). Between agents, style predicts output through identity (leave-one-agent-out R² > 0 in at least half of the periods): syntactic, not semantic. *Falsifier:* I_style significant in ≥ 1/3 of periods.
- **P9 #51 personas (native, sharpest test):** the hypothesis predicts the Prankster's and the media roles' style displacement into #51 within the matched-gap placebo band (percentile < 0.9) and no group difference (Mann–Whitney p ≥ 0.05). *Falsifier:* Prankster percentile ≥ 0.95, or media > other at p < 0.05. My prior: about 50% that the Prankster breaks it.
- **P10 NE38 (Opus 5 reassigned):** content percentile ≥ 0.9 against its own placebo; style percentile < 0.9.
- **P11 #12 debates:** (a) style fingerprint across debate halves ≥ 3× chance and above content's; (b) debate-switch T_c > T_s, with T_s ≤ 0.6; (c) agent 9's role (judge vs debater) is classified from content (≥ 0.8) but not from style (≤ 0.7); (d) side does not move style (p ≥ 0.05).
- **P12 G44 leader (descriptive):** the leader's style nearest centroid is Kimi K2.6 (rank 1, or rank 2 behind another fine-tune-adjacent agent); its content nearest centroid is not specifically Kimi.
- **Replication (templated, labelled):** per period, entry-boundary T_s ≤ 0.6 with T_c ≥ T_s + 0.1, and cross-boundary style accuracy > content's and ≥ 2× chance → supported; T_s > 0.6 and T_s ≥ T_c − 0.1, or style accuracy ≤ 1.5× chance → failed; otherwise mixed; no entry boundary → descriptive (within-period numbers only).

**Overall reading (fixed now).** H46 is supported if P1, P2, P7 and P8 pass and no class is broken. It is refuted if style is broken in ≥ 2 classes or in P9/P11c (assigned registers move style as much as content). A single broken class makes it "conserved except under X", which is the useful operational map.

## Synthetic validation (axis F; run 2026-10-04 05:45–06:00 UTC, before any real-data boundary statistic)
`analysis/synthetic.py` → `data/processed/H46-style-conserved-charge/synthetic/synthetic.json`, `figures/synthetic_validation.pdf`. Village sampling: the real eligible-message schedule (111,234 messages, 2,803 agent-days), the real boundary catalog (645 agent × boundary rows), the real NE41 pair schedule (7,312 forced, 7,214 voluntary, 32,055 within pairs) and real agent-day output schedules. Message noise is resampled from each agent's real within-day residuals (day structure destroyed); day jitter has variance 5% of the message variance; shifts δ are in units of the day-jitter SD (δ = 1 doubles the expected squared displacement of a boundary). Everything downstream of the feature vectors is the real pipeline (`h46lib`).

| Scenario (100 reps) | style moves (goal / rooms / nudger / roster / scaffold) | content moves | "conserved" verdict | mean T_s, T_c (goal) |
| --- | --- | --- | --- | --- |
| S0 null | 0.00 / 0.02 / 0.00 / 0.04 / 0.00 | ≤ 0.02 | ≤ 0.02 | 0.502, 0.500 |
| S1 content δ = 1, style fixed | ≤ 0.04 | 1.00 everywhere | 0.91 / 0.66 / 0.27 / 0.97 / 0.77 | 0.506, 0.894 |
| S1 content δ = 2, style fixed | ≤ 0.02 | 1.00 | 0.97 / 0.59 / 0.35 / 0.98 / 0.69 | 0.502, 0.990 |
| S2 style δ = 0.5 | 1.00 / 0.65 / 0.31 / 0.99 / 0.83 | 1.00 | ≤ 0.02 | 0.610, 0.991 |
| S2 style δ = 1 | 1.00 | 1.00 | 0 | 0.823, 0.991 |

- **Size and power:** nominal size for both channels; a style shift of half a day-jitter SD is detected at 100% of goal-switch and 99% of roster replicates, 83% scaffold, 65% rooms, 31% for the single nudger boundary. T_s ≈ 0.60 corresponds to δ_s ≈ 0.5, so the card's "T_s ≤ 0.60" means "the style charge moves by less than half its ordinary day-to-day jitter".
- **Equivalence is underpowered in small classes:** with style truly fixed, the "conserved" verdict is reached in only 27–35% (nudger, 1 boundary) and 59–66% (rooms, 4 boundaries) of replicates, because the CI of T_s from 1–4 boundaries is wide → Amendment 1.
- **Fingerprint (goal switches, 20 reps):** with style fixed, style cross-boundary accuracy 0.87 at chance 0.15 (retention 1.05); content retention falls from 1.17 (no shift) to 0.66 (δ_c = 1) and 0.38 (δ_c = 2). Style retention drops to 0.96 / 0.75 / 0.47 at δ_s = 0.5 / 1 / 2: the P7 threshold (retention ≥ 0.8) corresponds to δ_s ≲ 0.8.
- **NE41 recency confound (40 reps; OU content process, τ = 20 min, no jump):** the gap-unmatched percentile is 0.71 (pure confound). Gap-matched with 0.25-decade bins it is 0.509 and "content moves" fires in 58–70% of null replicates (crossing pairs sit at the long end of each bin). With 0.1-decade bins: 0.502 (10% false detections); with 0.05-decade bins: 0.499 (0/30), while a real jump of 0.1 is still recovered (T_c 0.554, 30/30) → Amendment 2. Style: size ≈ nominal (3–10% at 30–40 reps), a style jump of 0.3 gives T_s 0.61 (40/40).
- **KW information:** the within-agent scramble null holds size (7%, 10%, 7% at #38, #41, #51). Power for a true within-agent R² of 0.15: 80% at #38 (166 agent-days), 23% at #41 (67), 100% at #51 (962); for R² 0.05 only #51 detects (100%). Cross-validated R² is biased upward at small n (null mean 0.056 at #41) → Amendment 3.

## Amendments (2026-10-04 06:02 UTC, after the synthetic validation, before any real-data boundary statistic)
- **A1 (small classes).** When content moves, style does not move, and (T_s − ½) ≤ (T_c − ½)/3, but the CI upper bound of T_s exceeds ½ + m, the class verdict is **"conserved (equivalence not established)"**, shown as `mixed` in the period overview. This affects the rooms (4 boundaries) and nudger (1 boundary) classes, where the synthetic shows the equivalence rule cannot be met reliably.
- **A2 (NE41 gap strata).** Gap bins are 0.05 decades (not 0.25). "Moves" at NE41 requires the randomization p < 0.05 (Holm) **and** an agent-cluster bootstrap lower bound > ½.
- **A3 (KW).** Information is reported null-corrected (R² minus the median scramble-null R², then bits). Because per-period power is low except in #51, P8 is judged on the Stouffer combination over periods and on #51; the "≥ 80% of periods" clause is reported but not used for the verdict.

## Results by goal period
Roles: `replication` = templated layer-1 point (not an independent test); `native` = period-specific design; class folders (NE34, NE42, NE43, NE32, NE14) hold the common estimator pooled over a natural-experiment class.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G02](goalperiod-subhypotheses/G02/README.md) | replication | descriptive | no entry boundary; split-half fingerprint style 0.33 / content 1.00 (chance 0.33) |
| [G03](goalperiod-subhypotheses/G03/README.md) | replication | mixed | entry 2->3: T_s 0.80, T_c 1.00; fingerprint style 0.83 / content 0.83 (chance 0.25) |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | failed | entry 3->4: T_s 0.66, T_c 0.66; fingerprint style 0.83 / content 1.00 (chance 0.25) |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | mixed | entry 4->5: T_s 0.52, T_c 0.37; fingerprint style 0.92 / content 0.42 (chance 0.25) |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | mixed | entry 5->6: T_s 0.66, T_c 0.88; fingerprint style 0.83 / content 0.25 (chance 0.25) |
| [G07](goalperiod-subhypotheses/G07/README.md) | replication | failed | entry 6->7: T_s 0.74, T_c 0.77; fingerprint style 0.88 / content 0.62 (chance 0.25) |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | supported | entry 7->8: T_s 0.55, T_c 0.92; fingerprint style 1.00 / content 0.75 (chance 0.25) |
| [G10](goalperiod-subhypotheses/G10/README.md) | replication | failed | entry 8->10: T_s 0.90, T_c 1.00; fingerprint style 1.00 / content 0.42 (chance 0.25) |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | mixed | entry 10->11: T_s 0.60, T_c 0.56; fingerprint style 0.90 / content 0.81 (chance 0.14) |
| [G12](goalperiod-subhypotheses/G12/README.md) | native | failed | judging moves style, not content (agent 9: style 0.80/0.90 vs content 0.60; one-time judges 3/4 at 1.00 vs content 0.40–0.67); side: no effect; debate switches move neither |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | failed | entry 12->13: T_s 0.69, T_c 0.75; fingerprint style 0.94 / content 0.89 (chance 0.17) |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | descriptive | no entry boundary; split-half fingerprint style 0.57 / content 0.67 (chance 0.14) |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | supported | entry 16->17: T_s 0.41, T_c 0.57; fingerprint style 0.76 / content 0.62 (chance 0.14) |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | mixed | entry 17->18: T_s 0.80, T_c 0.96; fingerprint style 0.76 / content 0.57 (chance 0.14) |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | failed | entry 18->19: T_s 0.65, T_c 0.70; fingerprint style 0.90 / content 0.81 (chance 0.14) |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | failed | entry 19->20: T_s 0.81, T_c 0.70; fingerprint style 0.83 / content 0.46 (chance 0.12) |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | supported | entry 20->21: T_s 0.48, T_c 0.94; fingerprint style 0.88 / content 0.54 (chance 0.12) |
| [G23](goalperiod-subhypotheses/G23/README.md) | replication | mixed | entry 21->23: T_s 0.85, T_c 1.00; fingerprint style 0.81 / content 0.26 (chance 0.11) |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | failed | entry 23->24: T_s 0.91, T_c 0.99; fingerprint style 0.63 / content 0.23 (chance 0.10) |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | supported | entry 24->25: T_s 0.43, T_c 0.94; fingerprint style 0.63 / content 0.13 (chance 0.10) |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | supported | entry 25->26: T_s 0.60, T_c 0.97; fingerprint style 0.60 / content 0.47 (chance 0.10) |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | mixed | entry 26->27: T_s 0.74, T_c 0.96; fingerprint style 0.67 / content 0.30 (chance 0.10) |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | descriptive | no entry boundary; split-half fingerprint style 0.94 / content 0.73 (chance 0.09) |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | failed | entry 30->31: T_s 0.91, T_c 1.00; fingerprint style 0.88 / content 0.64 (chance 0.09) |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | descriptive | no entry boundary; split-half fingerprint style 0.82 / content 0.41 (chance 0.09) |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | descriptive | no entry boundary; split-half fingerprint style 0.89 / content 0.61 (chance 0.08) |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | supported | entry 35->36: T_s 0.56, T_c 0.88; fingerprint style 0.67 / content 0.12 (chance 0.09) |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | mixed | entry 36->37: T_s 0.72, T_c 0.83; fingerprint style 0.57 / content 0.38 (chance 0.10) |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | supported | entry 37->38: T_s 0.53, T_c 0.81; fingerprint style 0.63 / content 0.23 (chance 0.10) |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | failed | entry 38->39: T_s 0.92, T_c 0.98; fingerprint style 0.42 / content 0.22 (chance 0.08) |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | failed | entry 39->40: T_s 0.66, T_c 0.76; fingerprint style 0.54 / content 0.41 (chance 0.08) |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | mixed | entry 40->41: T_s 0.78, T_c 0.97; fingerprint style 0.36 / content 0.26 (chance 0.07) |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | failed | entry 41->42: T_s 0.89, T_c 0.91; fingerprint style 0.55 / content 0.29 (chance 0.07) |
| [G44](goalperiod-subhypotheses/G44/README.md) | native | descriptive | leader style: base Kimi K2.6 rank 2 (raw style: rank 1) of 17; content also rank 2; power-limited |
| [G51](goalperiod-subhypotheses/G51/README.md) | native | failed | Prankster style percentile 1.00 (falsifier hit); 5/17 incumbents ≥ 0.9, mostly non-Anthropic (post hoc); NE38: day level as predicted, 3-day blocks style moved too |
| [NE34](goalperiod-subhypotheses/NE34/README.md) | replication (class) | failed | goal switches: T_s 0.69 [0.61, 0.77] vs T_c 0.86; style broken; fingerprint style 0.76 vs content 0.51 (chance 0.15) |
| [NE42](goalperiod-subhypotheses/NE42/README.md) | replication (class) | mixed | rooms: T_c 0.61 (Holm p 0.004), T_s 0.57 (Holm p 0.09); partial |
| [NE43](goalperiod-subhypotheses/NE43/README.md) | replication (class) | mixed | nudger off: T_c 0.72, T_s 0.55 (p 0.24); conserved, equivalence not established (1 boundary) |
| [NE32](goalperiod-subhypotheses/NE32/README.md) | replication (class) | n/a | roster: T_s 0.49, T_c 0.49; nothing moves |
| [NE14](goalperiod-subhypotheses/NE14/README.md) | replication (class) | n/a | scaffold: T_s 0.49, T_c 0.51; nothing moves (NE14 alone: T_s 0.67, T_c 0.75, descriptive) |
| [NE41](goalperiod-subhypotheses/NE41/README.md) | native | failed | forced erasures: T_s 0.564 [0.513, 0.609], T_c 0.515 [0.486, 0.538]; style moves, content does not |

## Outcome vs prediction
| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 goal switches: T_c ≥ 0.70; type-controlled T_s ≤ 0.60 | T_c 0.858 [0.80, 0.91]; T_s 0.694 [0.61, 0.77] (raw 0.677); style excess 0.19 > a third of content's 0.36 | **failed** (broken) |
| P2 forced erasures: T_c 0.53–0.65; \|T_s − ½\| ≤ 0.03 | T_s 0.564 [0.513, 0.609]; T_c 0.515 [0.486, 0.538]; voluntary: style 0.535, content 0.512 | **failed** (falsifier hit; reversed: style moves, content does not) |
| P3 rooms: T_c ≥ 0.65; style conserved | T_c 0.612 (Holm p 0.004); T_s 0.572 (Holm p 0.09); ratio rule fails | partial |
| P4 nudger off: content ≤ 0.6 (likely uninformative); style in band | T_c 0.721 (Holm p 0.004); T_s 0.551 (p 0.24), CI to 0.69 | conserved, equivalence not established (A1) |
| P5 roster: T_c ≈ 0.55; style conserved | T_c 0.488, T_s 0.490 | uninformative (nothing moves) |
| P6 scaffold: conserved; NE14 at risk | class T_c 0.511, T_s 0.491; NE14 alone T_s 0.673 (p 0.03), T_c 0.747 | uninformative; NE14 style shift (descriptive) |
| P7 fingerprint: style ≥ 3× chance at ≥ 80% of goal switches, retention ≥ 0.8; content retention ≤ 0.6; style > content at ≥ 2/3; Anthropic-only above chance | style 0.76 (≥ 3× chance at 100%), retention 0.91; content 0.51, retention 0.72; style > content at 92%; Anthropic-only style 0.66 vs chance 0.25 | **passed** except content retention (0.72 > 0.6) |
| P8 KW: I_style ≈ 0; I_content > I_style; identity channel R² > 0 in ≥ half | #51: style R² 0.060 (null-corrected; p 0.01) ≈ content 0.058 (p 0.005); Stouffer style p 0.12, content p 0.003; both add nothing beyond today's output (PH4); identity channel R² > 0 in 2/11 | **failed** (style ≈ content where powered) |
| P9 #51 personas: Prankster < 0.9; media = other | Prankster 1.00 (ratio 5.3× median placebo); media 0.32, 0.32, 0.94, 1.00 (MW p 0.36); 5/17 at ≥ 0.9 | **failed** (falsifier hit) |
| P10 NE38: content ≥ 0.9, style < 0.9 | day level: content 0.91, style 0.82; 3-day blocks: both 1.00 (newcomer-confounded) | mixed |
| P11 #12: (a) style ≥ 3× chance and > content; (b) T_c > T_s, T_s ≤ 0.6; (c) role from content ≥ 0.8, style ≤ 0.7; (d) side no effect | (a) style 0.67, content 0.72 (chance 0.14); (b) T_s 0.44, T_c 0.41; (c) style 0.80/0.90 (raw p 0.03), content 0.60; one-time judges style 3/4 at 1.00; (d) p 0.80 | (a) half, (b) uninformative, **(c) failed (reversed)**, (d) passed |
| P12 G44 leader: Kimi rank 1–2 by style; content not Kimi-specific | style rank 2 (raw rank 1); content rank 2 | style passed, content not met (descriptive) |

**Overall (pre-registered reading):** H46 is **refuted** as stated. Style is broken in two classes (goal switches, erasures) and under both assigned-register tests (P9, P11c). The operational map that remains is "conserved where content is also conserved (roster, scaffold) and under nudger-off; not conserved under goal quenches, context erasure or assigned registers". Separately, style is a better identity fingerprint than content across goal switches.

## Results
**1. Style moves, but much less than it differs between agents.** In units of the agent's own placebo spread, goal switches move style by a median z of 0.37 and content by 1.82. The boundary percentile is ordinal and flags the style shift (T_s 0.69), but the shift is small next to between-agent distances (agent share of day-demeaned variance: style 0.59–0.71 vs content 0.51–0.56 in #38 and #51). That is why the fingerprint survives a goal quench (style 0.76 vs content 0.51, chance 0.15) while the conservation test fails. *Post hoc:* the shift is not the kickoff day (second post day: T_s 0.63), not the wrap-up day (0.62), and not the weekend gap (gap-matched placebo: 0.68, with content 0.71). It sits in content-adjacent features: digit share 17%, uppercase 14%, colons 10% of the excess (PH2). Part of "style" is topic.

**2. Style lives partly in the context window (NE41, the cleanest intervention).** Across an exogenously timed forced erasure, style moves (T_s 0.56; 18/23 units > ½) while content does not (0.52, CI includes ½; content moves in #36–#42 but not in #51). *Post hoc (PH3):* within long segments, a message's style distance to the agent's own mean rises monotonically with its position since the last reset, from −2.3 ± 0.6 to +1.1 ± 0.4. So erasure returns style to the agent's mean. The carriers are conversational-register features (@-addressing, em-dashes, emoji, ?/!, bullets). The picture that fits is a **substrate charge q_i plus a context-held excitation** that accumulates with context length (self-imitation, or the arc of a conversation) and is erased with the context. Strictly, q_i itself is conserved and its context-held dressing is not.

**3. Assigned registers move style.** The Prankster's style moved beyond every one of its 15 matched-gap placebo pairs (5.3× the median placebo displacement); so did two media roles and two non-persona Gemini agents. Role group does not separate movers (p 0.36); lab does (post hoc, p 0.04: non-Anthropic agents moved, Anthropic agents did not). At #12, judging changes style and not content: the judge writes verdicts about the same debate in a different register. Assigned *sides* do not move style.

**4. Kolchinsky–Wolpert.** Only #38 (112 agent-days) and #51 (654) have power. In #51, within-agent style and content fluctuations carry similar small information about next-day output (null-corrected R² 0.060 vs 0.058, ≈ 0.04 bits each). Style adds a little beyond content (ΔR² 0.012, p 0.025), but neither adds anything beyond today's output (PH4). Observationally, style is no less "semantic" than content at the day scale: both are readouts of today's work state. The KW claim that style is substrate and content is state is not supported by this bound.

**5. Where nothing happens.** Roster changes and scaffold steps move neither channel (T ≈ 0.49–0.51). Conservation cannot be tested there (R3). The regime II→III step (NE14) alone moves both (style 0.67, content 0.75; 11 agents).

Figures: `figures/summary_obs.pdf` (conservation map; fingerprint across boundaries), `figures/summary_obsb.pdf` (in-context drift and reset; #51 personas and #12 judges), `figures/synthetic_validation.pdf`. Data: `data/processed/H46-style-conserved-charge/` (`conservation.json`, `fingerprint.parquet`, `NE41/ne41.json`, `kw_info.json`, `G51|G12|G44/native.json`, `posthoc.json`, `replication.json`, `summary.json`).

## Caveats
- **What "style" is.** H13's 20 features are mostly formatting and punctuation, plus pronoun rates and content-adjacent rates (digits, uppercase, colons). The goal-switch shift is carried by the content-adjacent ones. A function-word stylometric vector might be more conserved; it was not tested.
- **Genre is not controlled.** The type control removes length, code blocks and links only. The erasure and judge effects may be speech-act genre (a status update after a reset, a verdict) rather than self-imitation. PH3's drift continuing from position 2 to 7+ argues against a pure first-message effect, but does not rule out the arc of a conversation.
- **Small classes and n = 1 tests.** Rooms has 4 boundaries and nudger 1; the Prankster and NE38 are single agents. NE38's pre-block is the agent's first three days in the village.
- **The persona comparison spans five weeks** with held-out windows (NE21–NE26) in between, including an Anthropic-only scaffold change (NE20, one tool call per turn), so lab-specific drift cannot be separated from role.
- **Replication points are templated** (4–15 agents per boundary, thresholds fixed in advance). They are not 32 independent tests.
- **KW is observational** and powered only in #51 and #38. Per-period cross-validated R² is inflated at small n (Amendment 3).
- **Post hoc labels.** PH1–PH5 were run after the pre-registered results were seen.

## Confirmatory predictions (written 2026-10-04 06:20 UTC after round 1, before any holdout use; `analysis/confirm.py`, dry-run only, **not run**)
These test the round-1 picture (a quasi-conserved charge with a context-held excitation), not the refuted strict conservation:
- **C1 (#51 tail):** style fingerprint (train on each agent's last ≤ 3 days before 09-07, test on the first ≤ 3 tail days) ≥ 5× chance.
- **C2 (19 held-out goal switches, 8→9 … 50→51):** style moves (T_s in [0.55, 0.85], p < 0.05), content moves more (T_c ≥ T_s + 0.10), and style out-identifies content at ≥ 2/3 of switches.
- **C3 (NE41 on held-out regime-III days):** forced-erasure T_s ≥ 0.53 with cluster CI > ½, and T_s − T_c ≥ 0.02.
- **C4 (in-context drift):** within segments of ≥ 7 messages, style excess at positions 7+ minus position 1 > 0 (CI excludes 0).
- **C5 (NE15, NE12 rooms):** T_c > 0.60 and T_s < T_c. **C6 (NE30, descriptive):** Gemini 3 Pro among the 3 nearest style centroids of Gemini 3.1 Pro. **C7 (NE23 nudger off):** T_s ≤ 0.62.
- **Overall:** confirmed if C1–C4 pass. The dry run on stand-ins (#51 before/after 08-24, four round-1 goal switches, 51h–51l) passes C1, C2, C4 and C7, and fails C3 and C5. In late #51 the erasure style effect is weaker (0.45–0.57), so C3 is a genuine risk.
- **Reuse disclosure:** the #51 tail is also targeted by the unrun scripts of H14, H18, H20, H22 and H34; #45 by H02 (activity timing, run) and H23 (leader content copying, unrun); #34 by six scripts. H46's statistics (per-agent style displacement against own placebo transitions; gap-matched erasure pairs) differ from all of them.

## Round 2 redirects (2026-10-04)
*Proposed by the round-1 agent; the coordinator may revise.*
- **Where round 1 went sideways:** "style" was operationalized with formatting-heavy features that also encode genre and topic, and "conserved" was tested at the level of the dressed style rather than the agent's charge.
- **What the direction is really after:** is there a part of an agent's output that belongs to the weights, survives every intervention and identifies the model, and how is it separated from context-held and register-driven variation?
- **H46-R1.** Genre-controlled style: residualize style on speech-act type (status update, reply, announcement, verdict; DQ2 reply threading) and on context position, then retest NE41, #12 judges and the Prankster.
- **H46-R2.** Fit the drift-and-reset model (an Ornstein–Uhlenbeck excursion around q_i, growing with context position and reset at erasure). Estimate its relaxation scale per lab, and test self-imitation directly (distance to the agent's own recent messages vs to its long-run mean).
- **H46-R3.** Function-word stylometry (closed-class word frequencies, a second embedding model from DQ5) as an alternative charge, to check that digits and uppercase are what moves at goal switches.
- **H46-R4.** Fingerprint as a monitor: an attribution ROC for 5/10/20 messages, combining style, content and a context-position correction, across goal switches and on the leader and NE30 successions.
- **H46-R5.** Lab-dependent susceptibility (PH5): pre-register a Gemini/GPT vs Anthropic difference in register response for the #51 tail and NE30.

## Round 2 (2026-10-05): genre control, drift-and-reset model, function-word charge
*Scope: the coordinator's H46-R1, R2 and R3. Non-reserved data only; no confirm run; no paid labels. R4 and R5 are not run.*

### Pre-registration (written 2026-10-05 02:50 UTC, before any round-2 statistic on real data)
*Facts seen before writing (sampling design only, no style, word or content statistic): `scheme/build_r2.py` gives 111,234 eligible messages (identical to round 1). Coverage of the genre covariates per regime I / II / III: DQ2 reply parent 38% / 48% / 55%; roster mention 51% / 54% / 61%; DQ3 window label 90% / 96% / 90%; ≥ 10 word tokens 99.4% / 99.9% / 99.6%. Regime III has 20,090 agent context segments (10,378 opened by a forced erasure, 9,532 voluntary, 160 session); 924 hold ≥ 8 eligible messages (DeepSeek 483, Anthropic 164, OpenAI 140, Google 104, other 33). #12 has 2,898 eligible messages.*

**Inputs (new, behind a switch: round-1 scripts are untouched and reproduce exactly).** `scheme/build_r2.py` → `data/processed/H46-style-conserved-charge/r2/messages_r2.parquet` from the shared `style_messages` (H46's population; `main & ~holdout & ~holdout_mask`). Per message: DQ2 reply parent (`pair_set = cand`, `parent`), the parent's speaker kind and the parent pair's stance probabilities, the maximum candidate `p_reply`; roster mentions; a leading-@ flag; the 13 DQ3 window probabilities (11 states, `p_addresses_participant`, `p_blocked`); `ctx_mode`, `ctx_pos`, `k_ctx`; the regime-III context segment (cut at `reset_consol | reset_session`; `first_of_day` is not a reset) and the message's position k in it (eligible messages since the reset); counts of 128 closed-class words. No text is stored.

**Style variants (fixed now).**
- `tc`: round 1's type-controlled style (17-d).
- `g` (**genre-controlled**): `tc` residualized within regime on the genre block G = {is_reply; parent is human; parent is automated; parent-pair p_supports, p_opposes, p_asks (zero without a parent); max candidate p_reply; has_mention; log(1 + n_mentions); leading @; the 13 DQ3 probabilities minus `p_execute_task` (reference), zero-filled, plus a DQ3-missing flag}. Coefficients are fitted with agent fixed effects (OLS on agent-demeaned data), and only the covariate part is removed: x̃ = x − (G − Ḡ_regime)B̂. The agent constant is kept.
- `gp` (**genre- and position-controlled**): the same with the position block P added: computer-use vs chat mode vs unmatched; log2(1 + ctx_pos) and log2(1 + k_ctx) (0 in chat mode); in regime III log2(k) and 1[k = 1]. This removes any *common directed* position profile; a random-direction excursion survives it (H73 synthetic S2).
- `fw` (**function-word charge**): the 50 most frequent of the 128 closed-class words in non-reserved eligible messages; per message sqrt(count / n_tok) for messages with ≥ 10 tokens; winsorized and z-scored globally; type-controlled within regime exactly as `tc` (log-length spline, has_code, has_url). `fw_g`: `fw` with the genre block removed as above.
- `core`: `tc` without the topic-adjacent `digit_share`, `upper_share`, `colon` (14-d).
- Content: round 1's style-residualized bge (primary); **gte** style-residualized (`statements_style_resid32_gte_modernbert`) as the second-model check.

**R1. Genre-controlled style (retests of round 1's moves).** Same estimators as round 1 (NE41 gap-matched percentiles with 0.05-decade bins and agent-cluster CI; G12 and G51 native code; O1 class test and O2 fingerprint), run on `g` and `gp`.
- **R1-P1 NE41 (forced erasures, regime III).** Prediction: the erasure effect survives: T_s(gp) ≥ 0.54 with agent-cluster CI lower bound > ½. Second design: genre-matched strata (each crossing pair ranked only among within pairs whose two messages fall in the same reply × mention cells). *Kill (genre explains it):* T_s(gp) CI includes ½ and T_s(gp) − ½ ≤ ½ (T_s(tc) − ½). Prior 65% for the prediction.
- **R1-P2 #12 judges.** Prediction: the judge register survives: agent 9's judge-vs-debater leave-one-debate-out accuracy from `gp` ≥ 0.7 and above content's, and ≥ 2 of the 4 one-time judges at percentile ≥ 0.9. *Kill:* accuracy < 0.6 and ≤ 1 one-time judge at ≥ 0.9. Prior 55%.
- **R1-P3 #51 Prankster.** Prediction: its onset displacement (round-1 block design) stays at percentile ≥ 0.95 under `gp`. *Kill:* < 0.9. Prior 70%.
- **R1-P4 goal switches (secondary).** Prediction: T_s(g) ≥ 0.60 and T_s(gp) ≥ 0.60 (the goal-switch shift is topic, not speech act); fingerprint accuracy under `gp` ≥ 0.9 × its `tc` value (genre control does not remove identity).
- **R1 reading.** "Round 1's moves are speech-act genre" if ≥ 2 of P1–P3 hit their kill; "register and context act beyond genre" if ≥ 2 of P1–P3 pass.

**R2. Drift-and-reset model (first real test of round 1's post hoc PH3).** *Form fixed now.* In a regime-III context segment of agent i, the k-th eligible message is
  x_k = q_i + η_{i,d} + e_k + ε_k,  e_k = φ e_{k−1} + σ ξ_k,  e_0 = 0 at the reset,
with ξ isotropic in the 17-d style space, so Var e_k = s²(1 − φ^{2k}), s² = σ²/(1 − φ²), relaxation scale τ = −1/ln φ (messages). Primary variant `gp` (the excursion is directionless by construction); `tc` secondary. Lab groups: Anthropic, OpenAI, Google, DeepSeek, other.
- **O-R2a variance growth.** d_k = ‖x_k − q̂_{i,u}‖² (agent × unit mean). Within each segment, Δ_k = d_k − d_1 for k = 2…8 (segments with ≥ k eligible messages; each segment is its own baseline). Model E[Δ_k] = s²(φ² − φ^{2k}); fit (s², φ) by weighted least squares on the seven position means; agent-cluster bootstrap (500) for CIs; per lab and pooled.
- **O-R2b reset (cross-products).** c = ⟨x_j − q̂, x_{j+l} − q̂⟩ for message pairs of one agent on one PT day at message lag l = 1…4: *within* (no reset between) vs *across* (exactly one forced erasure between). Within pairs are reweighted to the across pairs' time-gap distribution (0.1-decade bins). ΔC(l) = C_within(l) − C_across(l). The model predicts ΔC(l) = V̄ φ^l (day jitter and the agent constant cancel in the contrast). φ_C from a log-linear fit of ΔC(l) is an *unfitted* check of φ from O-R2a.
- **O-R2c self-imitation (direct test).** For message k ≥ 2, r̄ = mean of the agent's previous ≤ 3 eligible messages. The pull coefficient ρ = Σ⟨x_k − q̂, r̄ − q̂⟩ / Σ‖r̄ − q̂‖² (17-d, pooled). ρ = 0: the message is drawn around the long-run mean; ρ > 0: it follows the agent's own recent messages. ρ_within: r̄ in the same segment (in context); ρ_across: r̄ from before a forced erasure (erased), with k among the first three messages after it; within observations reweighted to the across time-gap distribution (gap from r̄'s last message to k). Rival control (contemporaneous convergence to the room's register): ρ refitted with a second regressor, the mean deviation (x_j − q̂_j) of other agents' eligible messages in the same room in the 10 min before k.
- **R2-P1.** E[Δ_k] rises with k (slope over k = 2…8 > 0, cluster CI > 0, pooled and in ≥ 2 lab groups); the pooled fit gives τ ∈ [1, 20] messages with bootstrap upper bound < 50.
- **R2-P2.** ΔC(1) > 0 (cluster CI > 0), and φ_C lies inside the 95% CI of φ from R2-P1.
- **R2-P3.** ρ_within > 0 (CI > 0), ρ_within − ρ_across > 0 (CI > 0) and ρ_across < ρ_within / 2; ρ_within stays > 0 with the room term.
- **R2-P4 (descriptive).** s² and τ per lab with CIs; round 1's PH5 (non-Anthropic more susceptible) predicts larger s² outside Anthropic.
- *Kill (the drift-and-reset model fails):* the R2-P1 slope CI includes 0, **or** ΔC(1) CI includes 0, **or** ρ_across ≥ ρ_within. Prior that the model survives all three: 45% (H73 found no dispersion rise with call fill).

**R3. Function-word charge.** Population: eligible messages with ≥ 10 tokens; every R3 comparison recomputes `tc` on the same population.
- **R3-P1 goal switches (NE34, 24 switches; O1).** T_fw ≤ 0.60 and T_fw ≤ T_s(tc) − 0.05. Prior 40%.
- **R3-P2 NE41 forced.** T_fw ≤ 0.53 or its cluster CI includes ½. Prior 45%.
- **R3-P3 identity (O2 across goal switches).** fw balanced accuracy ≥ 3× chance at ≥ 80% of switches and above content's at ≥ 2/3; fw vs `tc` accuracy reported. Prior 65%.
- **R3-P4 topic-adjacent features.** T_s(core) ≤ T_s(tc) − 0.03 at goal switches. Prior 60%.
- **R3 reading.** Function words are "a better charge" if P1, P2 and P3 pass; "no better" if T_fw ≥ T_s(tc) at goal switches and at NE41.
- **Content, second model.** T_c with gte at goal switches and NE41 reported next to bge (no verdict).

**Synthetic validation first** (`analysis/r2_synthetic.py`, on the real message, pair and segment schedules; vectors built from resampled real agent residuals with planted structure): residualization must hold size under a genre-only world and keep power for a random-direction erasure jump; the R2 estimators must recover planted (s², φ), give ΔC(1) ≈ 0 without a reset and ρ_across ≈ ρ_within for a clock-time drift; the `fw` class test must hold size. Any estimator change after the synthetic run is a dated amendment.

**Estimates.** Per-unit rows go to `per_period_estimates` (hypothesis H46, `post_hoc = False`, role `native` or `replication`, notes "round 2").

### Synthetic validation (run 2026-10-05 02:52–03:00 UTC, before any round-2 statistic on real data)
`analysis/r2_synthetic.py` → `data/processed/H46-style-conserved-charge/r2/synthetic.json`. Real schedules (111,234 messages, 46,260 NE41 pairs, 20,090 segments, 24 goal switches); vectors from each agent's resampled real residuals (day and context structure destroyed) plus day jitter (5% of message variance) and planted structure. Shares are of the per-message variance trace.

| Block | World | Result |
| --- | --- | --- |
| R1 (20 reps) | S0 null | NE41 forced T 0.506 (tc, g, gp alike); goal T 0.505; "moves" 0/20 |
| R1 | SG common genre + position effects (5%), no jump | goal T: tc 0.522 → g 0.507 (genre mix leaks into raw style at goal switches; `g` removes it); NE41 0.508–0.511 |
| R1 | SJ random-direction offset per segment (4%) | NE41 T 0.538 in tc, g and gp alike (a directionless excursion survives the control); but "moves" (CI > ½) 1/20 with round-1 unscaled strata |
| R1b (10 reps, after A5) | S0 / SJ, scaled distances | null T 0.500 (tc, gp), 0.502 (fw), moves 0/10, 0/10, 1/10; SJ T 0.534 / 0.545, moves 10/10 in every channel. Unscaled null: tc 0.507, **fw 0.530** |
| R2 (10 reps) | S0 none | Δ̄ CI > 0: 0/10; ΔC(1) CI > 0: 1/10; ρ_within − ρ_forced CI > 0: 0/10 (ρ ≈ 0.07 in both: day jitter) |
| R2 | S1a OU reset, φ 0.7 | Δ̄ 10/10; ΔC(1) 10/10; pull contrast 10/10 (ρ 0.15 vs 0.06); φ_C 0.73; implied-growth ratio 1.08, in [0.5, 2] 10/10; growth slope CI > 0 only 4/10 |
| R2 | S1b OU reset, φ 0.9 | Δ̄ 10/10; ΔC(1) 10/10; pull 10/10; φ_C 0.96; growth-fit φ 0.89 ± 0.07; ratio 1.31, in band 7/10 |
| R2 | S2 OU without reset (day chain) | Δ̄ 1/10; ΔC(1) 1/10; pull contrast 3/10 (ρ 0.22 vs 0.20) |
| R2 | S3 clock-time OU (τ 30 min), no reset | Δ̄ 0/10; ΔC(1) 0/10; pull 0/10 (ρ 0.177 vs 0.176: gap matching works) |
| R3 (20 reps) | S0 / fw unit shift 0.5 | goal T 0.501 (moves 1/20) / 0.679 (20/20) |

Readings. (1) Genre residualization holds size and removes planted genre leakage at goal switches. It cannot remove a random-direction erasure excursion, which is the point of `gp`. (2) Round-1 NE41 strata are thin: with 0.05-decade gap bins only 15% of forced pairs find ≥ 5 same-agent within pairs, so most are ranked in agent-free strata. Agents with noisier vectors then bias T up (0.507 for style, 0.530 for function words under the null). (3) The squared-distance growth is heavy-tailed (SD of d ≈ 20); clipping each centred dimension at ±3 cuts it to ≈ 7. The growth *slope* has little power for fast relaxation; the mean rise Δ̄ has full power. The growth fit does not bound φ (CIs reach 0.99–1.0); the cross-product decay does. (4) ΔC(1) and the pull contrast separate reset from no-reset and clock-drift worlds. The pull contrast has size up to 0.3 in a no-reset chain, so ΔC(1) is the decisive reset test.

### Amendments (2026-10-05 03:00 UTC, after the synthetic validation, before any round-2 statistic on real data)
- **R2-A1 (clip).** R2 distances and cross-products use unit-centred vectors clipped at ±3 per dimension.
- **R2-A2 (growth statistic).** R2-P1's growth test is Δ̄ (n-weighted mean of Δ_k over k = 2…8) with cluster CI > 0, in the pool and in ≥ 2 lab groups; the slope is reported. The τ clause (τ ∈ [1, 20], upper bound < 50) applies to τ_C = −1/ln φ_C from the cross-product decay; the growth-fit τ is reported.
- **R2-A3 (unfitted check).** R2-P2's consistency check is the covariance-implied growth: s²_C = ΔC(1) / (φ_C · mean_j(1 − φ_C^{2j})) predicts Δ̄; pass if Δ̄_obs / Δ̄_pred ∈ [0.5, 2]. "φ_C inside the growth-fit φ CI" is reported but is weak (wide CI).
- **R2-A4 (pull).** Within observations are reweighted to the forced observations' joint (time-gap bin × number of reference messages) distribution; r̄'s noise depends on the number of reference messages.
- **R2-A5 (NE41 scaling, all channels).** Each NE41 pair distance is divided by the median within-pair distance of its agent × unit before ranking (pairs without a scale are dropped). Unscaled values (round-1 method) are reported next to it. This applies to R1-P1, R3-P2 and the content checks.

## Notes
- 2026-10-04: promoted from HH170 by Vivian. The first round-1 session stalled during an API outage before writing any file; resumed 05:33 UTC.
- 2026-10-04 05:40 UTC: card, observables, nulls, verdict rules and predictions written before any real-data style or content statistic. 05:45 UTC: period and NE READMEs with dated predictions (`analysis/write_period_cards.py --phase predict`).
- 2026-10-04 05:45–06:00 UTC: synthetic validation; Amendments A1–A3 at 06:02 UTC.
- 2026-10-04 06:05–06:12 UTC: real runs (`conservation.py`, `ne41.py`, `kw_info.py`, `native.py`, `replication.py`), then post-hoc diagnostics (`posthoc.py`, PH1–PH5), `summarize.py`, `figures.py`, READMEs (`--phase results`). `confirm.py` dry-run only.
- Read-only imports: H15's processed data and H13/H23 code were **not** imported. All inputs are shared tables; H13's feature definitions are used through `text_features`.
- Data: `data/processed/H46-style-conserved-charge/` (13 MB) with `_provenance.json`.
