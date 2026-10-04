# H54: The kickoff text is the quench target

**Status:** exploratory round 1 done (2026-10-04, UTC). **Main finding: the kickoff text sets the day-1 target; how specific the text is does not set the spread.**
- **Target (P1, supported).** The day-1 content centroid picks out its own kickoff among 33: median percentile 1.0, top-1 in 18/33, ≥ 0.9 in 26/33 (p = 3e-6). The day-1 move points at the new kickoff (median 0.91; jump > 0 in 92%). Failures are the kickoffs that name no shared target: free weeks #3 and #16, #51's private goals, #44's half-free week.
- **Private goals (G51, native, supported).** In #51 each agent lands on its *own* goal text (role-swap accuracy 0.95, p = 0.0002), with no decay over 9 weeks. A human reassignment moves an agent onto its new goal within a day (NE38, DiD +0.61 [0.56, 0.66]).
- **Frozen projects (P2, mixed by the rule).** 9 of 13 kickoff-frozen projects carry the goal text's words (base rate 0.22, enrichment 3.2, stratified p = 0.006), and only 1/13 pre-existed (the carry-over rival is rejected). P2 counts as mixed because its pre-registered "any naming" enrichment is 1.95.
- **Specificity (P3, failed).** The pre-registered text specificity score does not predict spread. Embedding distinctiveness does weakly, mostly in regime III. Inside #44, the vague room is more spread out than the specific one.
- Design, observables, nulls and dated predictions were written before any real-data statistic, and the synthetic validation came first (Amendment 1). The confirmatory script is written and dry-run on stand-ins; **not run**. Promoted 2026-10-04 from HH169.
**Fields:** stat mech, sociophysics, info theory
**Literature:** none new; builds on round-1 results of H10, H12, H20, H24, H31, H39, H13 (cards linked below)
**Definitions used:** Agent; Population N(t); Regime (whitening per regime, no pooling across); Driving / external field (goal text, kickoff, human messages, #51 private goals); Agent state, variant *vector*, in H01's named form **agent state (vector), whitened statement mean** (unit-normalized mean of regime-whitened, unit statement vectors, d = 32); H01's **goal field ĝ** (here split into its kickoff and goal-text parts, from the shared `goal_fields`); H11's **agent state (categorical, project/artifact strict)**; H31's **consensus event (project share)** with its frozen / instant / gradual split; H08's **exposure (turn read-out)** via the shared context ledger. New named variants proposed for DEFINITIONS.md: **quench target (kickoff)**, **kickoff specificity score**, **quench depth**, **own-target percentile (swap null)**, **re-quench amplitude**, **kickoff remanence** (definitions under Observables).
**From:** HH169 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md`, with variants HH179–HH184 · **Models:** `physics-models/11-vector-spins/`, `physics-models/10-potts/`
**Data inputs (shared tables first):** `goal_fields` (shared goal/kickoff vectors; fixes H01's #38 swap), `project_states`, statement embeddings + per-regime whiteners, `statements_style_resid_period32` (DQ5), `artifact_mentions` / `artifacts`, `kicks_classified`, `text_features`, `context_ledger_items` / `call_windows`, `ground_truth_labels` (DQ6: #26 phases, #44 rooms, #51 roles), `period_units`, and H31's consensus events (read-only).

## Standards (2026-10-04)
*Documentation pass against `STANDARDS.md`. No analysis was re-run. H54 has no round-1b section; every entry rests on round 1.*

**Question served:** Q2. The card measures the kickoff field directly: day-1 content lands on the kickoff text. Q5 second: a kickoff is a steering instrument whose target is readable from its text.

| Impostor | Relevant? | How it was handled | Status |
| --- | --- | --- | --- |
| Scheduler field | no | Day-level content centroids; no activity or timing statistic. | n/a |
| Exogenous field (kickoff/goal/operator) | yes | The impostor is the object. The kickoff-swap null with a genericness correction, neighbour and within-regime decoys and the displacement test separate the target from genre (R2) and inertia (R1). | removed |
| Shared model priors | yes | Rival R4: `style_resid` vectors keep top-1 at 0.52; lab effect on susceptibility p 0.66 (P7). | removed |
| Contemporaneous convergence | partly | The main claim is a field claim. The first-plan centrality (P6) and human re-quench (P4) are influence claims with no read vs unread contrast. Close with the ledger tests in R2 and R3 (§1, row 4). | open |

**Inputs:** round 1 uses shared `goal_fields`, deterministic `project_states`, DQ5 `style_resid`, the context ledger (receptive fraction) and DQ6 labels. Activity bins, work and failures are not inputs. Still old: content uses bge only (gte was not built; R5); H31's frozen events (read-only) use H11's original labels, though the own-rule check on shared labels agrees.

**Two layers:** 30 replication folders (29 periods plus the `NE34` cross-kickoff folder). Native tests: 4 (`G51` supported; `G26` and `G44` mixed; `G38` failed).

**Confirm script:** `analysis/confirm.py` exists, dry-run only. It uses no activity table and no visibility rule, so no re-freeze is required (holdout.md item 8). A gte sensitivity before the run would close the one-model gap.

## Question
Are the projects agents freeze onto at a kickoff the ones the goal text or kickoff names, and does the day-1 content centroid land on the kickoff embedding, with spread set by how specific the kickoff is?

**Vivian (2026-10-04): really likes this one.** Variants folded in: HH179 (specificity sets quench depth), HH180 (human messages as partial re-quenches), HH181 (first concrete plan completes the target), HH182 (kickoff remanence), HH183 (conflicting cues → two domains), HH184 (family-specific kickoff susceptibility).

**Practical payoff:** what you name in a kickoff is what agents herd onto. If true, a kickoff is a steering instrument whose effect can be predicted from its text.

## Design: two layers (Vivian, 2026-10-04; see `infra/data-quality/QUEUE.md`)
- **Replication (layer 1):** the common estimators on every eligible kickoff (33 non-holdout goal periods; #23 excluded, see below). Period README role: `replication` (templated prediction, labelled as such).
- **Period-native tests (layer 2):** four designs that only these periods allow. Period README role: `native`.
  - **G51, private goals:** each agent has its own `agent_goal` text. Does each agent land on its *own* target rather than the shared kickoff? Plus **NE38** (07-29, a human reassigns Claude Opus 5's role): a single-agent re-quench.
  - **G44, two instructions:** #best is told to fine-tune a leader (a long, specific kickoff); #rest is told to pick its own goals (a 219-character kickoff). Room kickoffs have cosine 0.39. HH183's two domains, and HH179 within one period.
  - **G38, two room kickoffs:** the two rooms got different kickoff texts (cosine 0.60). HH183's room-swap design on a weaker contrast.
  - **G26, procedure kickoff:** the kickoff names a decision procedure (elect a leader who picks the goal). The elected leader's goal announcement on day 1 (DQ6 ground truth: result at 19:35 UTC on 01-05) is an agent-authored second target. HH181 and HH180 in their cleanest form.
- **Cross-kickoff design (exception (c)):** `goalperiod-subhypotheses/NE34/` holds the across-kickoff tests (swap null, specificity regressions, remanence across goals, family susceptibility), because the transition is the object.

## Model
**From:** `physics-models/11-vector-spins` (mean-field O(n) with a field), with `physics-models/10-potts` for the project labels.

**H54 variant: a quench toward a text-specified target.** Each agent's content state is a unit vector s_i ∈ S^{31} (whitened statement mean). Before the kickoff the swarm sits near the previous goal's state. At the kickoff the field switches to h = h_p t̂_p, where t̂_p is the *target direction* the instruction specifies, and agents relax into it:

s_i(day 1) ∝ λ_p t̂_p + a_i + J m + η_i,

with λ_p the **quench depth** (how far toward the target), a_i the agent's persistent offset (style, family prior, previous project), J m the herding pull toward the swarm mean, and η_i noise. The claim of H54 is that **t̂_p is readable from the kickoff text**: t̂_p ≈ k̂_p, the embedding of the kickoff message(s) in the same whitened basis, up to a proxy mismatch (a human instruction is not written like agent chat). The Potts version: the kickoff applies a field h_a > 0 to the projects a it names; projects with h_a ≫ J are **frozen** at the kickoff (already shared in the first window), the others must nucleate (instant waves or gradual consensus; H31).
- **HH179:** λ_p and the residual spread are set by the kickoff's specificity (named artifacts, numbers, deadlines, roles): specific → deeper quench, smaller spread, more frozen projects. Vague → exploration (H12's "anti-quench").
- **HH180:** a mid-period human message m is a partial re-quench: a short field pulse along ê_m, amplitude set by its specificity and by the share of agents whose next call read it, relaxing on H20/H31's time scale (hours).
- **HH181:** when the kickoff is ambiguous, the first concrete agent plan completes the target: t̂_p ≈ k̂_p + ê_plan.
- **HH182:** the kickoff field is persistent (remanence): overlap of the daily centroid with k̂_p decays slowly to a plateau; human-message pulses decay fast.
- **HH183:** two conflicting cues (different room instructions) quench into two domains with a wall at the room boundary.
- **HH184:** each family f has its own susceptibility χ_f: how far its agents move toward k̂_p on day 1.

**Rivals (what else could set day-1 positions and frozen projects):**
- **R0 no target:** day-1 content is unrelated to the kickoff text (own kickoff ranks like any other).
- **R1 inertia / remanence of the old state:** day-1 content stays near the previous period's state; frozen projects are carry-overs from the previous period (infrastructure already in use).
- **R2 generic kickoff genre:** the centroid matches *any* kickoff-like text (announcement register); long, multi-chunk kickoff vectors look like everything. The swap null with genericness correction separates this from R0 and H54.
- **R3 agent-authored target:** the first concrete plan (HH181), or a leader, sets the target; the kickoff only starts the clock.
- **R4 family / style field (H13):** day-1 positions are family style; movement toward the kickoff is not family-specific beyond style.

## Data scheme (`scheme/`)
`scheme/build.py` builds `data/processed/H54-kickoff-quench-target/` from shared tables only, plus raw `village_goals` / `agent_goals` and kickoff, human-message and plan texts held **in memory only** (specificity counts and name-token matches; no text stored anywhere).
- **Inputs:** `embeddings/goals.parquet` + `goal_vectors.npy` (kinds `goal`, `kickoff`, `kickoff_room`, `agent_goal`); `embeddings/statements.parquet` with raw `chat_bge_small.npy` / `intentions_bge_small.npy` (whitened here with the target period's regime whitener, so cross-period comparisons share one basis); `statements_style_resid_period32_bge_small.npy` (DQ5 style control); `chat_core` + `chat_text` (kickoff, human and plan texts, in memory); `artifact_mentions` + `artifacts`; `project_states` (W = 30, sources = all); H31 `events_ep_w30.parquet` and per-period `states_project_w30.parquet` (read-only, for the label → project map); `kicks_classified`; `context_ledger_items` + `call_windows` (who read a message, when); `text_features` (plan detection); `ground_truth_labels`; `calendar`, `roster`, `rooms_timeline`, `period_units`.
- **Kickoff messages:** re-derived with `infra/shared/goal_fields.kickoff_messages` (imported read-only), so message ids match the shared vectors.
- **Holdout:** every row passes `common.holdout_mask`; held-out goal periods and NE windows are dropped before anything is computed. Held-out kickoffs are not even used as decoys. `--allow-holdout` exists only for `analysis/confirm.py`.
- **#23 is excluded** although it is not in `holdout.json`: H10 keeps #23 blind for its confirmatory #22 → #23 pair, and a day-1 alignment of #23 with its own kickoff would leak into it. #24's "previous period" is therefore unavailable.
- **Output** (`data/processed/H54-kickoff-quench-target/`, ≤ 200 MB, `_provenance.json`):
  - `kickoffs.parquet`: one row per (period, room or all): goal_no, room, gid, kickoff time, n_msgs, words, specificity counts (numbers, named entities, artifacts/URLs, agent/role names, deadline terms), S_text, S_count, S_emb, fallback flag;
  - `kick_msgs.parquet`: message_id, goal_no, room, t (codes only);
  - `stmt.parquet` + `stmt_z.npy` / `stmt_zs.npy` (as built; replaces the planned `day_agents` table): every statement H54 uses (target period, active-day index with 0 = the previous period's last day, agent, kind, time, room, pre-kickoff flag), with its whitened 32-d vector in the target period's regime basis and a DQ5 style-residualized copy. Agent and day vectors are formed on the fly;
  - `projects.parquet`: one row per H31 (block, project) and per day-1 dominant project (own rule), with artifact id codes and flags: named (strict / loose, kickoff / goal text), carry-over, first-plan-named, human-introduced on day 1;
  - `human_msgs.parquet` (HH180), `first_plans.parquet` (HH181), `g26_leader.json`, per-period `G<NN>/results.json`, `NE34/` cross-kickoff tables, `synthetic/`.
- **Regimes covered:** I, II, III; every comparison is made in the target period's regime basis.

## Eligible kickoffs
Non-holdout goal periods with a shared kickoff (`goal_fields`): #3–#8, #10–#13, #16–#21, #24–#27, #30, #31, #33, #35–#42, #44, #51 (33 periods). #2 has no kickoff; #23 excluded (above). Fallback kickoffs (#4, #24) are kept and flagged. Two-room periods use the combined kickoff for replication and the room kickoffs for natives. #51 uses the 07-06 day; its private goals are native only.

## Observables
*Specified 2026-10-04, before any real-data statistic along a kickoff, goal or plan direction.* Notation: W_r is the regime whitener (d = 32) of the **target** period p. Statement vectors z = unit(W_r e). Kickoff k̂_p = unit(W_r k_p^raw); goal text ĝ_p likewise.
- **Agent day vector** v_i: unit mean of agent i's statement vectors (chat + intentions; chat-only variant) in a segment. Day 1 = statements after the first kickoff message on the period's first active day. ≥ 3 statements required; Claude Code agent excluded.
- **Swarm centroid** m_p = mean_i v_i; direction m̂_p.
- **Target score** S_pq = cos(m̂_p, k̂_q^{(r_p)}) for every eligible kickoff q, mapped into p's basis.
- **Genericness correction:** Ŝ_pq = S_pq − mean_{p′≠q} S_{p′q} (a kickoff that resembles every centroid gets no credit).
- **Own-target percentile** π_p: the share of decoy kickoffs q ≠ p with Ŝ_pq < Ŝ_pp (decoys: the other 32 eligible kickoffs; within-regime and adjacent-period variants).
- **Displacement alignment** T_pq = cos(m_p(day 1) − m_{p−1}(last day), k̂_q): does the *move* point at the new kickoff? Own percentile as above. Previous period must be eligible and non-holdout.
- **Jump** J_p = cos(m̂_p(day 1), k̂_p) − cos(m̂_{p−1}(last day), k̂_p).
- **Quench depth** D_p = mean_i cos(v_i, k̂_p) − mean_{q≠p} mean_i cos(v_i, k̂_q) (excess over decoys).
- **Residual spread** σ_p = 1 − q_p, with q_p the mean pairwise cosine of agent day-1 vectors, each rarefied to 5 statements (50 draws). The pairwise form is N-unbiased; rarefaction removes statement-count effects.
- **Kickoff specificity** (text held in memory): counts of numbers, named entities (capitalized non-initial tokens other than agent names), artifacts/URLs, agent/role/room names, deadline/time terms. **S_text** = mean z-score (over eligible kickoffs) of log(1 + count per 100 words) across the five classes (primary). **S_count**: the same with absolute counts. **S_emb** = 1 − mean_q cos(k̂_p, k̂_q) (distinctiveness).
- **Projects (Potts layer):** H31's E-P events (144 (block, project) rows, 20 periods): frozen / instant / gradual / no consensus. **Named** = the project's artifact, or a file/site under it, is mentioned in a kickoff message (`artifact_mentions`, human chat, strict `how`), **or** a distinctive token of its canonical name (owner and generic words dropped) appears in the kickoff or goal text (loose). **Carry-over** = strict agent mentions of the project on the previous period's last two active days. **Precision** = P(named | frozen), **recall** = P(frozen | named), **base rate** = P(named | all projects).
- **First concrete plan (HH181):** the first agent chat message after the kickoff on day 1 with a strict artifact mention, or ≥ 60 words with ≥ 3 lines of list structure (`text_features`). **Plan centrality** Δ_P = cos(m̂′, ê_P) − mean cos(m̂′, ê_decoy), where m̂′ is the centroid of the other agents after the plan on day 1, and decoys are the other agent messages of ≥ 40 words posted on day 1 before the plan or in the hour after the kickoff.
- **Re-quench amplitude (HH180):** for a mid-period human message m (≥ 250 characters, not a kickoff, not in day 1's first 2 h): a_m = cos(m̂_after, ê_m) − cos(m̂_before, ê_m), with room centroids of agents' statements in the 60 min before and after; decoy amplitudes use other human messages' vectors (same regime, length-matched) on the same windows; Δ_m = a_m − mean a_decoy. **Receptive fraction:** share of the room's agents whose receiving call includes m within 30 min (`context_ledger_items`).
- **Remanence (HH182):** daily kickoff excess A_ex(d) = mean_i cos(v_i,d, k̂_p) − mean_{q≠p} mean_i cos(v_i,d, k̂_q), fitted per period (≥ 5 active days) as A_ex(d) = A_∞ + (A_1 − A_∞) e^{−(d−1)/τ_K}; human-message pulses fitted the same way in hours; previous-kickoff remanence = day-1 excess toward k̂_{p−1}.
- **Family susceptibility (HH184):** χ_ip = cos(v_i(day 1), k̂_p) − cos(v_i(previous period's last day), k̂_p), a within-agent move that cancels constant style; style-residualized variant from DQ5's per-period vectors.

## Null / baseline
- **N0, kickoff-swap null** (R0, R2): own kickoff vs the 32 other eligible kickoffs, with genericness correction; under R0, π_p is uniform. Within-regime and adjacent-period decoys are the strict versions (era topics).
- **N1, inertia** (R1): the previous period's last-day centroid and the previous kickoff as rivals (J_p, displacement test, previous-kickoff remanence); carry-over as the rival explanation of frozen projects.
- **N2, base rate** for frozen-project naming: P(named) over all H31 projects; Fisher exact and a period-stratified permutation (frozen flags shuffled within period).
- **N3, decoy messages** for plans (other early agent messages) and human re-quenches (other human messages; placebo times).
- **N4, role-swap / room-swap / axis-swap nulls** for the natives (other agents' goals; the other room's kickoff; other kickoff-difference axes).
- **N5, synthetic truths** (axis F): vector-spin swarms with and without a text-readable target, at village sampling, through the same pipeline.
- **Known confounds:** text-embedding proxy for the field (a human instruction is not agent chat); agents restate and quote the kickoff (that *is* the mechanism at the shortest scale, but inflates day-1 alignment); kickoff length and chunk count (generic vectors); statement counts; regime and N co-vary with era; projects measured by artifact mentions (attention, not work); style (H13).

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R0 no target; R1 inertia / carry-over; R2 generic kickoff genre; R3 agent-authored target (first plan, leader); R4 family style field.
**Locked holdout used for confirmation:** none yet (`analysis/confirm.py` written, not run).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Statements, kickoff messages (the shared `goal_fields` rule), artifact mentions, DQ6 roles and rooms are all dataset fields; assumptions are listed. Results hold with DQ5 style-residualized vectors, chat only, and in regimes I and III. But the target is a text-embedding proxy, and "named" relies on name-token matching (heuristic, with false positives). |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | No dynamics are fitted. Statement-count invariance of the spread is verified (synthetic ρ ≈ −0.05). Day 1 is a transient (excess 0.24 → plateau 0.11 by day 3), so day-1 and plateau statistics are reported separately. The echo-removal audit shows target identification is not just quoting. Herding makes spread depend on N (handled as a covariate). |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 2 | Parameter-free tests, so every period is out of sample. P1 beats the kickoff-swap null with genericness correction, within-regime and neighbouring-era decoys, the previous period's state (displacement), echo removal, and style residualization. #51 beats the role-permutation null (p = 0.0002). Holdout not run. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | Passed: the move direction, neighbour decoys, goal-text naming of frozen projects (rejecting carry-over), the remanence plateau, NE38. Failed: the specificity → spread link (P3), family susceptibility (P7), the plan-vagueness moderator, previous-kickoff remanence, and two domains (#44, #38). |
| E interventional | predicts the change across a natural experiment | 1 | NE34: each kickoff is a step, and the predicted target is identified in 29/33 (π ≥ 0.75) with the predicted move sign in 92%. NE38: the predicted sign of a single-agent reassignment is confirmed, with a large effect and tight CI. Failed: the #26 leader's announcement did not re-quench. Sizes were not predicted in advance. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Synthetic validation with real counts and geometry: P1 is calibrated (0/200 under R0 and R1) and powered when the text proxy is faithful (≥ 0.5). P2 and N2 are underpowered (power stated). The counting artifact was found and the analysis corrected. Robust to style residualization, echo removal and chat-only. **The embedding-model swap is not done** (DQ5's second model was not built yet). |
| G ground truth | agrees with known structure | 2 | Agents' positions recover #51's assigned goal texts (DQ6 roles; 0.95) and Opus 5's documented 07-29 reassignment (NE38). #44 room assignments (DQ6) reproduce the instruction split in the #best room. H31's frozen events are matched to the goal texts. |
| H comparative | beats the named rivals | 1 | R0 (no target) and R1 (inertia, carry-over) are rejected. R2 (genre) is controlled by the genericness correction, though synthetic shows that correction is incomplete. R3 (first plan) is only partly separated: plans are central (70%) but name no frozen project and are not used more after vague kickoffs. R4 (family) shows no susceptibility differences. |
| I transfer | holds in other same-mode periods, including the holdout | 1 | Holds across regimes I (top-1 0.59), II and III (0.50) and across all goal modes except free choice. The holdout is not run (`confirm.py`: 14 held-out kickoffs, the #51 tail, held-out projects and human messages). |

## Prediction
*Written 2026-10-04 (UTC), before running the analysis on real data.*

**What I had seen when writing this:**
- Round-1 results of H10 (goals are quenches toward a common target; variance along ĝ ×2–8), H31 (13 of 63 consensus events frozen at kickoffs; their per-period counts; content alignment highest at kickoffs, relaxing over ~4 h), H20 (#38's ~4-day kickoff relaxation), H12 (day 1 is the *most diverse* day in 13/16 periods), H24 (aligned from the first hour), H39 (kickoffs tilt content only in regime III), H13 (family alignment is style), H22 (#51 private roles pin positions; same-role pairs share a field).
- Structure only: kickoff message counts, character counts and fallback flags per period; the cosine between room kickoffs in two-room periods (#38 0.60, #44 0.39, all others 1.00); the number of day-1 agents and statements per period; #26's DQ6 phase times. No alignment, spread or project-naming statistic.

**Primary predictions** (Holm across the three):

| ID | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| **P1** (b) target | Day-1 centroids identify their own kickoff: median own-target percentile π_p ≥ 0.90 (genericness-corrected, 32 decoys), own kickoff top-1 in ≥ 50% of periods, one-sided Wilcoxon p < 0.001 | median π_p < 0.75, or top-1 < 25% | 0.75 |
| **P2** (a) frozen = named | Kickoff-frozen projects are the named ones: precision ≥ 0.6 with enrichment ≥ 2× the base rate, Fisher one-sided p < 0.05 | precision ≤ 1.5× base rate, or most frozen projects are unnamed carry-overs | 0.35 |
| **P3** (c) specificity (HH179) | More specific kickoffs leave less day-1 spread: Spearman(S_text, σ_p) ≤ −0.35, one-sided p < 0.05, n ≈ 33 | ρ ≥ 0 | 0.30 |

**Secondary predictions:**

| ID | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| P1b | Adjacent decoys: Ŝ_pp exceeds both neighbours' kickoffs in ≥ 80% of periods | ≤ 60% | 0.7 |
| P1c | The *move* points at the kickoff: median displacement percentile ≥ 0.85; J_p > 0 in ≥ 80% of periods | median < 0.7 | 0.7 |
| P1d | The kickoff is a better target than the goal text: Ŝ_pp(kickoff) > Ŝ_pp(goal text) in ≥ 60% of periods | ≤ 40% | 0.55 |
| P2b | Rival R1: ≥ half of frozen projects are carry-overs | < 30% | 0.5 |
| P2c | Robustness: the same precision/enrichment pattern on own-rule day-1 dominant projects (shared deterministic labels) | opposite pattern | 0.4 |
| P3b | Spearman(S_text, D_p) ≥ +0.35 (deeper quench) | ≤ 0 | 0.3 |
| P3c | Frozen fraction rises with S_text (Spearman ≥ 0.35, n = 20 periods; and per project, P(frozen) rises with S_text in a logistic model with n_named as a covariate) | ≤ 0 | 0.25 |
| P4 (HH180) | Human messages re-quench: median Δ_m > 0 (sign test p < 0.05); Spearman(Δ_m, message specificity) > 0 and Spearman(Δ_m, receptive fraction) > 0 | median ≤ 0 | 0.6 / 0.3 / 0.35 |
| P5 (HH182) | Remanence: A_ex(last day) > 0 in ≥ 70% of periods with ≥ 5 days; median τ_K ≥ 3× the human-pulse τ_H (in active hours); previous-kickoff excess on day 1 > 0 across periods (one-sided p < 0.05) | A_ex decays to 0; τ_K ≈ τ_H | 0.6 / 0.55 / 0.4 |
| P6 (HH181) | First plans are central: Δ_P > 0 in ≥ 60% of periods; Spearman(Δ_P, S_text) < 0 (vague kickoffs lean on the plan); frozen projects named by the kickoff *or* the first plan reach precision ≥ 0.7 | Δ_P ≤ 0 in most periods | 0.55 / 0.3 / 0.3 |
| P7 (HH184) | Family susceptibility: family effect on χ (within-period permutation of family labels, p < 0.05); agent split-half r ≥ 0.3 across kickoffs; survives the style-residualized variant | p ≥ 0.2; r ≈ 0 | 0.3 |

**Native predictions** (each also in its period README):

| ID | Period | Prediction | Counts against | Credence |
| --- | --- | --- | --- | --- |
| N1 | G51 | Each agent lands on its own private goal: role-swap pair accuracy ≥ 0.75 (pairs of agents with different roles; permutation p < 0.01); centered alignment cos(v_i − m, ĝ_i − mean ĝ) > 0 on average; the own-goal signal persists over the head's weeks (accuracy ≥ 0.65 in the last pre-tail week) | accuracy ≤ 0.6 | 0.75 / 0.6 |
| N1b | NE38 (G51) | Claude Opus 5's alignment with its *new* goal rises after 07-29 by more than the other agents' alignment with that goal (difference-in-differences > 0, day-bootstrap CI excluding 0) | no rise | 0.6 |
| N2 | G44 | Two domains: each agent closer to its own room's kickoff (room-swap accuracy ≥ 0.8); the rooms separate along u = k̂_best − k̂_rest more than along other kickoff-difference axes (axis-swap percentile ≥ 0.95) | accuracy ≤ 0.6 | 0.65 |
| N2b | G44 | HH179 within one day: the vague #rest kickoff leaves more spread than the specific #best kickoff (σ_rest > σ_best) and a lower own-kickoff depth | σ_rest ≤ σ_best | 0.6 |
| N3 | G38 | Room-swap accuracy ≥ 0.7 along the weaker contrast (cosine 0.60) | ≤ 0.5 | 0.4 |
| N4 | G26 | The day-1 centroid identifies the election kickoff (π ≥ 0.9); after the leader's goal announcement, the other agents' centroid moves toward the announcement's vector by more than toward decoy agent messages of the same hour (excess a > 0, decoy percentile ≥ 0.9); the frozen/instant projects after it are ones the announcement names | no move beyond decoys | 0.6 |

**Multiplicity and power.** Three primaries, Holm. Secondary and native tests are reported with their own nulls; with 33 kickoffs, a Spearman of 0.35 has about 55% power at one-sided α = 0.05, so P3 can fail from power alone (the synthetic run states the realized power). Per-period verdicts are descriptive (replication) or single-period tests (native).

### Synthetic validation plan (axis F), run before real data
`analysis/synthetic.py`: vector-spin swarms in d = 32 with the real day-1 agent and statement counts; persistent agent offsets a_i; herding J; statement noise calibrated on non-kickoff structure (within-agent-day statement resultant and between-agent spread on later days, no kickoff direction used); a kickoff text vector k̂ = unit(t̂ + proxy noise) with cos(k̂, t̂) ∈ {0.3, 0.5, 0.7}; and kickoff genericness that grows with chunk count. Checks:
- **S1:** P1's statistics recover the target at realistic depth (power ≥ 0.8) and are calibrated under R0 (false-positive rate ≤ 0.07); the genericness artifact appears without correction and is removed with it.
- **S2:** σ_p is unbiased in N and statement count; under no specificity effect, Spearman(S, σ) has the nominal false-positive rate; power at n = 33 for a true effect is reported.
- **S3:** Potts project layer with a kickoff field on named projects: precision/recall recover the truth; per-period frozen fraction correlates with the number of named artifacts *mechanically* even when specificity does nothing, while the per-project model with n_named does not (so specificity effects are not counting artifacts).
- **S4:** #51 role-swap accuracy and N2 room-swap power at the real N.

### Synthetic validation (axis F): results
*Run 2026-10-04, after the predictions above and before any real-data statistic along a kickoff, goal or plan direction.* Script `analysis/synthetic.py` (calibration `analysis/calibrate.py`: within-agent-day statement resultant 0.47–0.63, later-day pairwise agent alignment 0.46 / 0.37 / 0.05 and agent persistence 0.68 / 0.62 / 0.82 in regimes I / II / III, per-regime covariance with effective dimension 13–26; no kickoff direction used). Output `data/processed/H54-kickoff-quench-target/synthetic/results.json`. 200 replicates of all 33 eligible periods per cell, real day-1 agent and statement counts, real kickoff chunk counts.
- **S1, P1 is specific.** Under R0 (no target) and R1 (inertia), P1 passes 0/200 times: median π 0.50–0.59, top-1 3–6%. Under H54 the median-π clause is met at every setting (0.88–1.0), but the **top-1 clause needs a faithful text proxy**: at proxy fidelity cos(k̂, t̂) = 0.3, top-1 is 21–30% and P1 never passes. At 0.5 the pass rate is 6% / 74% / 94% for day-1 target shares f = 0.05 / 0.15 / 0.30; at 0.7 it is 82–100%. The displacement percentile behaves the same way, slightly weaker.
- **Genericness artifact.** When long kickoffs are generic, the raw own score correlates with chunk count even under R0 (median ρ 0.19, 90th percentile 0.40). Column-centering reduces this but does not remove it (0.12 / 0.35).
- **S2, spread.** Rarefied spread does not depend on statement count (ρ ≈ −0.05). It does depend on N once herding acts on a finite swarm (ρ ≈ 0.25–0.38 at J = 0.3, 0 at J = 0). The P3 test has false-positive rate 0.035–0.08 (nominal 0.05). Power at n = 33: 0.64 when the true ρ ≈ −0.35, and 0.97 when ρ ≈ −0.53.
- **S3, Potts naming layer** (frozen probability 0.35 for named projects vs 0.05 otherwise; loose naming has 15% false positives; frozen detection sensitivity 0.8). Under no naming effect, P2 passes 1.5% and Fisher 3% (calibrated). Under a true naming effect, precision has a median of 0.56: measurement false positives pull it below the 0.6 threshold. **P2 passes in only 33% (48% with a specificity interaction), so P2 is underpowered.** **The counting artifact is real:** with no specificity effect, the per-period frozen fraction correlates with specificity (median ρ 0.20, significant in 22% of runs, 4× nominal), because specific kickoffs name more projects. The per-project test is less inflated (12%), and detects a true interaction 68% of the time.
- **S4, #51 role swap** (21 agents, 16 roles). Under no private field, accuracy is 0.47–0.50 and p < 0.01 in 0–2% of runs. Power is 0.84 at a private share of 0.10 with goal-text fidelity 0.5, and 0.46 at 0.05.
- **S5, #44 room swap** (4 + 12 agents). Under no target, accuracy is 0.50. At f = 0.15, the median accuracy is 0.75 and only 48% of runs reach ≥ 0.8. The axis percentile reaches ≥ 0.95 in 40% of runs. **N2 is underpowered unless the room quench is deep (f ≈ 0.3: 82%).**

**Amendment 1** (2026-10-04, after the synthetic run, before any real-data statistic along a kickoff, goal or plan direction):
1. P1 is reported against the calibrated benchmark: a top-1 rate tells how faithful the text proxy is, given that median π ≥ 0.9.
2. P3 and P3b partial correlations add log(kickoff chunks) to the covariates (regime, log N, log words).
3. P3c's primary form is the per-project logistic model (frozen ~ named + S_text + n_named). The per-period frozen-fraction correlation is reported but flagged as count-inflated.
4. P2's verdict is reported literally and with its power (≈ 0.3–0.5). A "mixed" result with enrichment ≥ 1.5 is the expected outcome under a true but noisy effect.
5. N2 and N3 are reported with their power. A failure at accuracy 0.6–0.75 is not informative against a shallow room quench.

## Results by goal period
Replication verdict rule (templated): supported if the own-kickoff percentile π ≥ 0.90, failed if π < 0.75, mixed otherwise. Native verdicts follow each period's own prediction (N1–N4).

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [NE34](goalperiod-subhypotheses/NE34/README.md) | replication (cross-kickoff) | mixed | P1 supported (median π 1.0, top-1 18/33, p 3e-6); P2 mixed (9/13 frozen named by the goal text, enrichment 3.2); P3 failed (S_text ρ +0.17) |
| [G03](goalperiod-subhypotheses/G03/README.md) | replication | failed | π 0.00 (rank 33; free week); move π 0.25 |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | supported | π 1.00 (rank 1); move π 1.00, jump 0.30 |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | mixed | π 0.75 (rank 9; free week); move π 0.88 |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | supported | π 0.91 (rank 4); jump −0.11 |
| [G07](goalperiod-subhypotheses/G07/README.md) | replication | supported | π 1.00 (rank 1; free week) |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | supported | π 1.00 (rank 1); jump 0.44 |
| [G10](goalperiod-subhypotheses/G10/README.md) | replication | supported | π 1.00 (rank 1) |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | mixed | π 0.81 (rank 7; free week); spread 0.90 |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication | supported | π 1.00 (rank 1); jump 0.88; spread 0.49 |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | supported | π 0.91 (rank 4); jump 0.41 |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | failed | π 0.12 (rank 29; free week); spread 0.87 |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | supported | π 1.00 (rank 1); jump 0.27 |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | supported | π 1.00 (rank 1); jump 0.33 |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | supported | π 0.91 (rank 4); frozen build repo named by the goal text |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | supported | π 1.00 (rank 1); jump 0.33 |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | supported | π 1.00 (rank 1); jump 0.50 |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | supported | π 1.00 (rank 1; fallback kickoff) |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | supported | π 0.94 (rank 3) |
| [G26](goalperiod-subhypotheses/G26/README.md) | native | mixed | π 0.97 (rank 2); no pull toward the leader's announcement (decoy percentile 0.48); the announcement names no project |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | supported | π 1.00 (rank 1); jump 1.04 |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | supported | π 1.00 (rank 1); frozen park project named |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | supported | π 1.00 (rank 1; free week with a shared farewell) |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | supported | π 0.97 (rank 2) |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | supported | π 0.97 (rank 2); both rooms' frozen fork repos named |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | supported | π 1.00 (rank 1); jump 0.68 |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | mixed | π 0.88 (rank 5; free week) |
| [G38](goalperiod-subhypotheses/G38/README.md) | native | failed | room swap 0.58 (p 0.57; underpowered); #best tight, #rest on neither room text; π 0.91 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | supported | π 1.00 (rank 1); jump 0.56 |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | supported | π 1.00 (rank 1); frozen hub named |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | supported | π 1.00 (rank 1); both rooms' frozen projects named |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | supported | π 1.00 (rank 1); jump 0.59 |
| [G44](goalperiod-subhypotheses/G44/README.md) | native | mixed | room swap 0.31 (two domains failed); #rest spread 0.80 vs #best 0.50, depth −0.25 vs 0.37 (HH179 within the period); π 0.47 |
| [G51](goalperiod-subhypotheses/G51/README.md) | native | supported | own private goal: role swap 0.95 (p 0.0002), flat over 9 weeks; NE38 DiD +0.61 [0.56, 0.66]; shared-kickoff π 0.25 |

## Results
*Exploratory round 1, 2026-10-04 (UTC); non-holdout periods only, #23 excluded.*
- **Code:** `scheme/build.py`; `analysis/h54lib.py`, `h54est.py`, `calibrate.py`, `synthetic.py`, `explore.py`, `native.py`, `robustness.py` (post hoc), `figures.py`, `period_folders.py`, `confirm.py` (not run).
- **Data:** `data/processed/H54-kickoff-quench-target/` (26 MB): `kickoffs.parquet`, `kick_msgs.parquet`, `stmt.parquet` + `stmt_z.npy` / `stmt_zs.npy`, `projects.parquet`, `human_msgs.parquet`, `first_plans.parquet`, `g26_leader.json`, `NE34/` (cross-kickoff tables, `results.json`, `robustness.json`), `G<NN>/results.json` and `native.json`, `synthetic/`, `confirm_dryrun.json`.
- **Figures:** [`figures/summary_obs.pdf`](figures/summary_obs.pdf) (P1 per period; frozen-project naming), [`figures/summary_obs_b.pdf`](figures/summary_obs_b.pdf) (G51 weekly role swap; NE38), [`figures/remanence.pdf`](figures/remanence.pdf) (HH182, HH180), [`figures/synthetic_validation.pdf`](figures/synthetic_validation.pdf).

**Outcome vs prediction**

| Prediction | Credence | Outcome | Verdict |
| --- | --- | --- | --- |
| **P1** day-1 centroid identifies its own kickoff (median π ≥ 0.9, top-1 ≥ 50%, p < 0.001) | 0.75 | median π 1.0, top-1 18/33 (within regime 23/33), p = 3e-6; raw (uncorrected) the same; chat-only top-1 0.52; style-residualized 0.52 | **supported** |
| P1b beats both neighbouring kickoffs in ≥ 80% | 0.7 | 28/33 (0.85) | supported |
| P1c the move points at the kickoff (median ≥ 0.85; jump > 0 in ≥ 80%) | 0.7 | 0.91 (n = 25); 23/25 (median jump 0.33) | supported |
| P1d kickoff beats the goal text in ≥ 60% | 0.55 | 0.55 (centered score); goal text alone also identifies (median π 1.0, top-1 0.52) | failed (equally good) |
| **P2** frozen = named: precision ≥ 0.6, enrichment ≥ 2, Fisher p < 0.05 | 0.35 | precision 9/13 = 0.69, base 0.35, enrichment 1.95, p = 0.010 (stratified 0.08). Goal-text naming: base 0.22, enrichment 3.2, p = 1e-4 (stratified 0.006; leave-one-period-out ≥ 2.97). No kickoff URL resolves to any of these projects | **mixed** (literal); strong for goal-text naming |
| P2b ≥ half of frozen projects are carry-overs (rival R1) | 0.5 | 1/13 pre-existing; 1/9 carry-over where known; as a predictor, pre-existence has enrichment 0.36 | failed (R1 rejected) |
| P2c same pattern on own-rule day-1 dominant projects | 0.4 | 19 dominant of 418: any naming enrichment 2.7 (p = 0.001); goal text 4.4 (p = 1e-5, stratified 0.002) | holds |
| **P3** Spearman(S_text, spread) ≤ −0.35 | 0.30 | +0.17 (partial +0.29); S_count −0.08 | **failed** |
| P3b Spearman(S_text, depth) ≥ 0.35 | 0.3 | +0.12 (S_count +0.23). S_emb +0.58 is partly mechanical (depth and S_emb share the decoy term) | failed |
| P3c frozen share rises with S_text (per-project, Amendment 1) | 0.25 | coefficient 0.59 ± 0.56 (n.s.); per-period ρ 0.39 (p = 0.046), which is the count-inflated form | failed |
| P4 (HH180) human messages re-quench: median Δ > 0; rises with specificity and receptive fraction | 0.6 / 0.3 / 0.35 | median Δ 0.04 (57% positive, sign p = 0.03, n = 171; regime III 0.10, regime I 0.02); vs specificity ρ 0.02; vs receptivity ρ −0.16 (75% of messages read by everyone within 30 min, per the context ledger) | holds / failed / failed |
| P5 (HH182) remanence: last-day excess > 0 in ≥ 70%; τ_K ≥ 3 τ_H; previous-kickoff excess on day 1 > 0 | 0.6 / 0.55 / 0.4 | 25/28 (0.89); kickoff excess 0.24 on day 1 → plateau 0.11 (τ ≈ 1.2 active days ≈ 5 active h) vs a human pulse < 1 h; previous kickoff median 0.01 (p = 0.34) | holds / holds / failed |
| P6 (HH181) first plans central in ≥ 60%; more so after vague kickoffs; kickoff ∪ plan precision ≥ 0.7 | 0.55 / 0.3 / 0.3 | 23/33 (median percentile 0.69, p = 0.003); vs S_text ρ +0.14 (wrong sign); plans name none of the frozen projects (precision unchanged at 0.69) | holds / failed / failed |
| P7 (HH184) family susceptibility | 0.3 | lab effect p = 0.66 (style-residualized 0.72); agent split-half r = 0.09 (0.27); agents individually move toward the kickoff in 87% of agent-kickoffs (median χ 0.28) | failed |
| N1 (G51) own private goal: swap ≥ 0.75; centered alignment > 0; last week ≥ 0.65 | 0.75 / 0.6 | 0.95 (p = 0.0002); 0.36 (p = 0.0002); weekly 0.90–0.96. Chat only 0.95, style-residualized 0.91 | **supported** |
| N1b (NE38) Opus 5 moves onto its new goal | 0.6 | DiD +0.61 [0.56, 0.66]; away from the old goal −0.29 [−0.38, −0.22] | **supported** |
| N2 (G44) two domains: room swap ≥ 0.8; axis percentile ≥ 0.95 | 0.65 | 0.31 (p = 0.76); 0.65 | failed |
| N2b (G44) vague room more spread, shallower | 0.6 | spread 0.80 vs 0.50; depth −0.25 vs +0.37 | supported |
| N3 (G38) room swap ≥ 0.7 | 0.4 | 0.58 (p = 0.57) | failed (underpowered) |
| N4 (G26) election kickoff identified; leader's announcement re-quenches; it names the new projects | 0.6 | π 0.97 (rank 2); no move beyond decoys (percentile 0.48; 0.39 at 1–3 h); names no artifact | mixed (2 of 3 failed) |

**Synthesis**
1. **The text is the target, at the level the embedding can see.** A day-1 centroid sits closer to its own kickoff than to the 32 others in 26/33 periods, and its displacement from the previous period points at the new text. Rival R1 (inertia) and genre (R2) do not explain this. Removing statements that echo the kickoff weakens top-1 identification (0.55 → 0.45 at 9% removed; 0.30 at 28%), but the median π stays ≥ 0.9. Quoting is part of the mechanism, not all of it. Per synthetic S1, a top-1 rate of 0.55 corresponds to a text proxy that is moderately faithful (≈ 0.5) at a day-1 target share ≈ 0.15–0.3.
2. **No shared target, no shared quench.** All four replication failures are kickoffs that name no shared object: free weeks #3 and #16 (π 0.0, 0.13), #51 (private goals), #44 (one room chooses its own goals). Free-mode median π is 0.81 vs 1.0 elsewhere (post hoc, p = 0.02). The natives show the other side: where every agent has its own text (#51), each lands on its own (0.95), and the shared centroid points at no one's goal. A text reassignment re-targets an agent within a day (NE38).
3. **Frozen projects carry the goal's name.** 9/13 kickoff-frozen projects match the goal text's words; only 1/13 pre-existed. The agents probably name the repo after the goal, so "named" partly means "created for the goal". Still, only 9 of the 31 goal-named projects froze (recall 0.29), so naming alone does not freeze a project. The kickoff message itself almost never links an artifact.
4. **Specificity does not work as a dial.** The pre-registered text-specificity score predicts neither spread, nor depth, nor frozen share once the counting artifact is controlled (synthetic S3). Distinctiveness of the kickoff in embedding space correlates with tighter day-1 content (ρ −0.47; partial −0.36, p = 0.06), but mostly through regime III (8 periods). The clean within-period contrasts (#44 pre-registered, #38 post hoc) both have the more specific room tighter, confounded with room size and model strength.
5. **Remanence within a goal, erasure across goals.** Kickoff alignment drops from 0.24 to a plateau of 0.11 within about 1–2 active days and stays positive to the last day in 25/28 periods. The previous kickoff leaves no trace on the new day 1. Human messages are a small (Δ 0.04, ≈ 1/8 of a kickoff jump), short (< 1 h) pulse. Private goals in #51 show no decay over 9 weeks.
6. **Agent-authored targets.** First concrete plans are more central than other day-1 messages, but no more so after vague kickoffs, and they name none of the frozen projects. In #26 the elected leader's goal announcement did not pull the other agents' content toward its text. Across round 1, human text sets targets and agent text does not.
7. **No family susceptibility** (HH184): agents move toward the kickoff in 87% of cases, but neither lab nor agent identity predicts how far.

**Caveats**
- The target is a text-embedding proxy (bge-small, one model). The second embedding (DQ5 gte) was not built yet. Quoting the kickoff is part of the measured effect.
- "Named" uses name-token matching of canonical artifact names against the goal or kickoff text. Agents name repos after goals, so the naming direction is ambiguous. Strict URL naming never occurs.
- H31's events (read-only) use H11's original labels; the own-rule check on deterministic labels agrees.
- 33 kickoffs, 22 in regime I. P2 and the natives N2 and N3 are underpowered (stated). Specificity and moderator analyses are low-n. Mode moderation and the S_emb–spread link are post hoc.
- #23 was excluded to keep H10's confirmation blind. Previous-period comparisons are missing where the previous period is held out (8 periods).
- The #26 announcement was found by a text rule, checked once in-session; no text is stored.
- The human-message receptive fraction is near 1 for most messages, so it cannot moderate anything.

## Confirmatory test (written 2026-10-04 after exploration; NOT run)
`analysis/confirm.py` refuses to run without `--confirm --i-understand-this-uses-the-locked-holdout`. `--dry-run` runs the identical code on stand-ins (14 exploration kickoffs; the #51 head's last three weeks for the tail): C1 median π 1.0, top-1 0.57, p = 0.0008; C2 0.95; C3 enrichment 7.8; C4 median 0.09, p = 0.04 (`data/processed/H54-kickoff-quench-target/confirm_dryrun.json`). Predictions are frozen in the script header:
- **C1 (primary):** P1 on the held-out kickoffs {#1, #9, #14, #15, #28, #29, #34, #43, #45, #46, #47, #48, #49, #50} (median π ≥ 0.9, top-1 ≥ 50%, p < 0.01). C1b: the non-free targets reach π ≥ 0.9 in ≥ 75%.
- **C2:** the #51 tail (09-07 → 09-20) role-swap accuracy ≥ 0.80, p < 0.01.
- **C3:** own-rule day-1 dominant projects are goal-text-named with enrichment ≥ 2 (primary periods exclude H11's and H31's project targets).
- **C4:** held-out human messages re-quench (median > 0, sign p < 0.05).
- **C5 (secondary):** S_emb–spread ρ < 0.
- **Reuse disclosure:** #22, #32 and #23 are excluded (H10's directions). #34 is targeted by H01/H05/H07/H12/H19/H21. #45 by H02 (activity) and H23 (message content). #28 and #45 by H11 (projects). #29, #46, #47 and #50 by H31 (E-P), #49 by H31 (E-C). H54's statistics (own-kickoff percentile among decoy kickoffs, goal-text naming of day-1 dominant projects, re-quench excess) are different statistics. The policy in `hypotheses/holdout.md` applies; record in `LOG.md` when run.

## Round 2 redirects (2026-10-04)
- **Where round 1 went sideways:** the specificity half (HH179) used a regex count of numbers, names and deadlines. The two-domain test (HH183) assumed both rooms got a concrete target, but in #44 and #38 one room's instruction was vague.
- **What the direction is really after:** whether a human-written instruction sets where an LLM swarm goes, how strongly, for how long, and which features of the text control that.
- **H54-R1. Two concrete targets (HH183 redesigned).** Use #12's debate motions and multi-option kickoffs as native tests of two-domain quenching, instead of one concrete and one vague room.
- **H54-R2. Causal first-plan test (HH181).** With the context ledger, ask whether agents whose call has read the first concrete plan move toward it more than matched agents who have not yet read it. For #26, measure the leader's goal in the project layer, not in text.
- **H54-R3. Per-agent read-out re-quench (HH180).** Compare each agent's first statement after its read-out turn of a human message with its last statement before. The 30-min receptive fraction is near 1 everywhere.
- **H54-R4. A better specificity measure (HH179).** Use LLM-rated (Jev) kickoff specificity and settling time (H20, H31 τ_C) as the outcome, and retest embedding distinctiveness on the holdout (C5).
- **H54-R5. Embedding swap.** Rerun P1, G51 and NE38 on DQ5's second model (gte-modernbert), and HH184 with per-agent read-out timing.
- **H54-R6. Remanence mechanism (HH182).** Why does the previous kickoff leave no trace on the new day 1? Test memory consolidation at goal changes, and link the within-goal plateau (0.11) to H20's day-to-day correlation and H31's τ_C.

## Notes
- 2026-10-04: promoted from HH169 (Vivian). Round 1 started; card design and predictions written before any real-data statistic.
- 2026-10-04: one scorer fix before any outcome statistic: agent names (and their model version numbers) are masked before counting numbers and named entities in the specificity score.
- 2026-10-04: round 1 run (synthetic → Amendment 1 → replication → natives → robustness). Post hoc analyses are labelled: mode moderation, echo removal, style residualization, chat-only #51, S_emb mechanics, P2 leave-one-period-out.
- Proposed DEFINITIONS.md variants (H54): **quench target (kickoff)** = unit(W_r · kickoff embedding) of the period's kickoff messages (shared `goal_fields` rule); **own-target percentile** = genericness-corrected percentile of a day-1 centroid's cosine with its own kickoff among the other eligible kickoffs; **quench depth** = mean agent alignment with the own kickoff minus mean alignment with decoy kickoffs; **kickoff specificity score** (S_text, S_count, S_emb as defined above); **re-quench amplitude** = Δ_m above; **kickoff remanence** = A_ex(d) above.
