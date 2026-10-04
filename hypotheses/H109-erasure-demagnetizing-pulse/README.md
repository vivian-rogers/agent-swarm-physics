# H109: The forced erasure is a demagnetizing pulse: where is the room's order stored?

**Status:** **exploratory round 1 done (2026-10-04, non-holdout only): failed by HH339's kill rule.** A forced context erasure does not demagnetize an agent's room alignment. Over 3,477 forced erasures in 8 regime-III two-room periods, the gap-matched drop of alignment with the room's spontaneous axis is δ_F −0.08 [−0.23, 0.07] (random effects, bge; gte −0.07 [−0.18, 0.04]). That excludes HH339's 30% drop at synthetic power 1.00. If anything, alignment rises after an erasure (direct pooled −0.12 [−0.21, −0.03]; #38 −0.26 [−0.38, −0.07]; post hoc). The kickoff alignment does not move (δ_K 0.08 [−0.12, 0.28]). Voluntary consolidations agree (δ_V −0.04). Reading the room has a small positive pull (κ_R 0.019 [0.003, 0.034] per e-fold of items read, beyond posted-unread), but there is no drop for it to repair. The room's order lives in what the erasure does not touch: the agent's work, prompt and memory. Card, predictions and Amendment 1 written 21:27–21:44 UTC before any real-data statistic. `analysis/confirm.py` frozen and dry-run, **not run**. Approved by Vivian in the dashboard vetting panel 2026-10-04 from HH339.
**Question (GOALS.md):** **Q4** (where does the swarm's information live: is a room's content order held in the context window or in the agent's own work) and **Q1** (what couples agents: is room alignment maintained by reading the room).
**Fields:** stat mech (a demagnetizing pulse on one spin of an ordered domain; remanence vs re-magnetization by the local field), information theory (Kolchinsky–Wolpert natural scramble of one channel), dynamics (event study and relaxation after a pulse)
**Literature:** [Kolchinsky & Wolpert 2018](../../literature/kolchinsky-2018-semantic-information-autonomous-agency.md) (value of information under a scramble of one store); `physics-models/11-vector-spins/README.md` (soft-spin O(n) in a domain); `physics-models/04-semantic-information/README.md`. Project cards: H100 (spontaneous room order, Q_spont 1.8–5.7), H102 (content follows the room the agent speaks in), H70/H87 (only the context window carries value per bit; own artifact κ ≈ 0; 89% return to own repo), H15/H44 (erasure costs; re-acquisition burst; coupling to pre-erasure items falls to 0.60), H46/H73 (content does not move at erasures; style does), H69 (restatements copy context), H45 (backlog lands on the first post-reset call), H08 (erasure cuts coupling to pre-erasure senders by 18%).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime; Driving / external field (kickoff, room kickoffs, operator messages); Exposure (turn read-out) through the DQ1 context ledger; *Context segment* (H45); *Pseudo-erasure* (H44, here a within-segment statement boundary); *Room of a statement* and *Day-centred agent vector* (H100, H102); *Agent constant â_i (leave-period-out)*, *Field share* directions u_f, u_op and *Spontaneous share* (H100); *Loop episode (restatement / copy)* (H55; DQ5 flags); *Semantic information (natural-scramble variant)* (H15). New named variants proposed (defined under Observables; DEFINITIONS.md not edited): **room alignment a_t (spontaneous, leave-agent-out)**, **erasure drop fraction δ_F (gap-matched)**, **kickoff-alignment drop δ_K**, **re-read slopes κ_R, κ_U (post-erasure)**.
**From:** HH339 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/11-vector-spins/` (primary), `physics-models/04-semantic-information/` (secondary: a natural scramble of the context channel)
**Data inputs (shared tables first):** `style_messages` (chat statements: msg, srow, agent, t, room, unit, DQ5 `restate`/`copy` flags), `producing_calls` (the call that produced each message), DQ1 `context_ledger_turns` (reset flags `reset_forced`, `reset_consol`, `reset_session`; `n_agent` new items per call), `chat_core` (room messages for the posted-unread placebo), `embeddings/statements_style_resid32_{bge_small,gte_modernbert}.npy` (both models; `statements_white32_*` variant), `culture_vectors.directions` (whitened kickoff, room-kickoff and goal directions), `chat_index` + `chat_<model>.npy` (operator messages per room), `period_units`, `holdout.json` via `holdout_mask`. No text is read.

## Source HH (verbatim from the HH list, including refinements)
- **HH339 · The forced erasure is a demagnetizing pulse: where is the room's order stored?** NE41 wipes an agent's context at a time set by the scaffold (about 18.6k forced events, regime III). If the room's spontaneous order is held by coupling through the context (H08; H102: content follows the room you speak in), the agent's alignment with its room's direction should drop right after a forced erasure, then recover as it re-reads the room. If the order is held by a self-made field (its own repo, H70: 89% return), alignment should not drop. This is a Kolchinsky scramble of one channel.
  - *Prediction:* alignment with the room direction Δ_spont falls by ≥ 30% in the first 3 post-erasure statements and recovers in proportion to room items re-read (ledger). Alignment with the kickoff target, which is held in the prompt since NE13, does not fall.
  - *Check:* statement-level projections around forced erasures vs matched placebo calls (same agent, same day, no erasure); voluntary erasures as a second contrast. Use H100's identical-kickoff periods and #51g (#focus). Both models.
  - *Kill (context-held order):* no drop, with power ≥ 0.8 at a 30% drop. The spontaneous share is then held in artifacts or memory, not by coupling.
  - *Impostors:* scheduler: the timing is set by the scaffold, so the design is quasi-random. Exogenous: the kickoff-alignment control. Priors: agent fixed effects. Convergence: the recovery is regressed on items read vs posted-unread at matched age.
  - *Models:* 11, 04 · *Builds on:* H100, H102, H15, H69, H70

## Question
When the scaffold erases an agent's context (NE41, the 41-call cap), does the agent's content lose its alignment with the direction that separates its room from the other room, and does it regain it as it reads the room again? A drop means the room's order lives in the context window (coupling). No drop means it lives in something the erasure does not touch: the agent's own work, memory or prior.

## Design: two layers (STANDARDS §4)
- **Scope.** Regime III (NE41 exists only there), non-holdout, goal periods with two structural rooms: **G36** (units 36b, 36c), **G37**, **G38** (38a–e), **G39**, **G41**, **G42** (42a, 42b), **G44** (44a, 44b), and **G51** restricted to unit **51g** (#general vs #focus). #40 is one merged room; #43 and #45–#50 are held out. Statement boundaries with ≥ 1 statement on each side (sampling fact seen before writing): forced 93–517 per unit, 222 (G36) to 1,040 (G38) per period; 1,489 in 51g.
- **Replication** (role `replication`): the common estimator (O1–O3) in every period: G36, G37, G39, G42 carry the replication verdict.
- **Natives** (role `native`), each with its own dated prediction:
  - **G41** (identical kickoffs; the strongest field-free room split in H100, Q_spont 4.23): the cleanest test that *spontaneous* order is context-held.
  - **G38, G44** (room-specific kickoffs held in the prompt): the room-kickoff alignment must not fall while the spontaneous axis may (the prompt-held field vs the context-held order, in one period).
  - **G51** (51g, #general vs #focus): the largest read volumes, so the recovery dose–response (κ_R vs posted-unread κ_U) has its power here.
  - **NE41** (folder `NE41/`): forced vs voluntary erasures as the second contrast, and the random-effects summary of δ_F over periods (named exception (d): per-period CIs are wide; partial pooling reported next to the per-period estimates).
- **Exceptions (CLAUDE.md).** (a) The room axis is a per-period ruler built from other agents. (b) Agent constants â_i come from other regime-III periods (H100's invariance check passed: r 0.49 vs null 0.14). (c) The erasure boundary is the object. (d) NE41 pooling, as above.

## Model
**From:** `physics-models/11-vector-spins/` (soft-spin O(32) content vector in a two-domain room system) with the erasure as a natural scramble of one channel (`physics-models/04-semantic-information/`).

Statement t of agent i, day d, room r(t) (day-centred, 32-d style-residualized):

  x̃_t = â_i + σ_r m_r(t) u_P + η_t,  m_r(t) = m_∞ [1 − δ g(c_t)]

- u_P: the period's spontaneous room axis (H100's Δ_spont direction), σ_r = ±1 for the two rooms.
- â_i: the agent constant (prior, family), removed before projection.
- **Context-held order (HH339, R-ctx):** the room component is maintained by what is in the context window. g(c) = 1 just after an erasure and decays as room items are read: g = exp(−R/R₀), with R the room items received since the erasure. Prediction: δ ≥ 0.3 for the first 3 statements, recovery ∝ log R.
- **Self-made field (R-art, H70/H58):** the room component is set by the agent's own work (its repo, its task), which the erasure does not touch (89% return to the own repo). δ = 0.
- **Prompt-held field:** the kickoff (and the room kickoff in #38/#44) sits in the prompt since NE13; its alignment b_t must not fall in either model. A fall of b_t would mean the erasure moves content generally (a confound, not context-held order).
- **Fast restoring field (R-fast, H45):** the first post-reset call receives the backlog (≈ 5.8 items), so any drop is confined to statements produced before any room item is read (R = 0).
- **Self-copy (R-loop, H69):** a drop that comes only from losing in-context restatements (pre-erasure statements copy earlier aligned ones). Removed by the dedupe (primary) and read from the dedupe contrast.
- In Kolchinsky–Wolpert terms the erasure scrambles the context channel C and keeps memory, prompt and artifacts. ΔV_room = the room order lost per scramble; δ_F is its relative size.

## Data scheme (`scheme/`)
`scheme/build.py` → `data/processed/H109-erasure-demagnetizing-pulse/` (≲ 20 MB, `_provenance.json`). Non-holdout rows only, asserted with `holdout_mask` and the table flags.
- **Statements** (`statements.parquet`): regime-III chat statements of main agents (not 19, 28, 30) in the scoped units, with srow (row into DQ5 arrays), msg, agent, t, PT day, goal, unit, room, `restate`, `copy`, producing call (`turn_id_prod`, `t_call_prod`), the cumulative reset counters at the producing call (forced, voluntary, session), position in the agent-day sequence.
- **Boundaries** (`boundaries.parquet`): every pair of consecutive statements (k, k+1) of an agent within a PT day with different producing calls, labelled **F** (exactly one forced reset between the two producing calls, nothing else), **V** (one voluntary consolidation), **W** (none: the pseudo-erasure placebo), **O** (other). Columns: gap (s), segment-clean pre/post windows (up to 3 statements each, no other reset inside), reset call (F/V), dedupe variants.
- **Reads** (`reads.parquet`): per post-erasure statement k = 1..10 of each F and V event: R_k = Σ `n_agent` over the agent's ledger calls from the first post-reset call through the producing call (room items read since the erasure); U_k = agent messages posted by others in the agent's room in (t_call_prod, t_call_prod + (t_call_prod − t_reset)] (posted-unread of equal duration, unreadable by the statement).
- **Axes** (`axes_<model>.npz`, `axes.parquet`): per period and agent, the leave-agent-out room axis û_i, the agent constant â_i, the kickoff direction k̂_r per room. Day means for centring.
- **Regimes covered:** III only.

## Observables
*Written 2026-10-04 21:27–21:29 UTC, before any H109 statistic on real data. All vectors: DQ5 32-d style_resid statement vectors (unit), bge primary, gte in parallel.*
- **O0 Day centring.** x̃_t = x_t − d̄_d, with d̄_d the mean over agents present on day d (both rooms) of their day-mean statement vector.
- **O1 Room alignment a_t.** Stayers of period P: agents with ≥ 80% of their P statements in one room. x̄_j = mean over j's home-room statements of x̃ minus â_j. â_j = mean over other regime-III non-holdout periods (#36–#51, excluding P) of j's period-mean x̃ (0 if j has no other period). For agent i: Δ^(−i) = mean over stayers j ≠ i of room A − the same over room B; project out u_f (unit whitened difference of the two room kickoffs, where their cosine < 0.95: #38, #44) and u_op (unit difference of the rooms' mean operator-message vectors, ≥ 3 human messages per room); û_i = unit(P⊥ Δ^(−i)). **a_t = σ_{r(t)} ⟨x̃_t − â_i, û_i⟩**, σ = +1 for room A (#best, #general), −1 for B (#rest, #focus), with r(t) the room the statement is posted in. Variant without â (composition kept).
- **O2 Erasure drop fraction δ_F.** For each boundary b: pre window = up to 3 statements before b, after the previous reset of any kind and on the same day; post window = up to 3 statements after b, before the next reset; ≥ 1 on each side. D_b = ā_post − ā_pre. Stratum s = agent × 0.05-decade bin of the gap (first post − last pre; H46 pitfall). Excess **Δ_F = Σ_s n_F,s (D̄_F,s − D̄_W,s) / Σ_s n_F,s** over strata holding both F and W boundaries. **δ_F = −Δ_F / Ā_pre,F** (Ā_pre,F = mean ā_pre over matched F events). δ_F = 0.3 is a 30% drop. CI: cluster bootstrap over agent-days (1,000 draws; strata fixed, H70 trap); agent clusters as robustness. Companion: the regression D_b = β_F F + β_V V + spline(log gap) + agent fixed effects (δ_F^reg = −β_F/Ā_pre,F). **Identified** only if Ā_pre,F's CI is above 0.
- **O3 Kickoff-alignment drop δ_K.** b_t = ⟨x_t, k̂_r⟩ on the un-centred unit vector, k̂_r = the room kickoff of the statement's room where one exists, else the shared kickoff (whitened, `culture_vectors.directions`). δ_K from O2's estimator with b in place of a. Identified only if B̄_pre,F's CI is above 0.
- **O4 Recovery (re-read) slopes.** For F events, post statements k = 1..10: y_k = a_k − ā_pre(b). WLS with event fixed effects: y_k = κ_R log(1 + R_k) + κ_U log(1 + U_k) + γ log k + FE_b. κ_R > 0 and κ_R > κ_U is reading-driven recovery; κ_U ≈ κ_R is a common drift (convergence impostor). Pooled over periods with period fixed effects (exception (d)), per-period values reported.
- **O5 R-fast split.** δ_F recomputed with the post window restricted to statements whose producing call has R_k = 0 (nothing read yet) vs R_k > 0.
- **O6 Voluntary contrast (NE41 native).** δ_V from O2 with V in place of F.
- **O7 Robustness.** Both models; dedupe variants: primary drops statements flagged `restate` (either model), variants keep all or drop `copy` only; window k = 1 (first statement only) and k = 5; variant without â; white32 vectors.

## Null / baseline
*Written 2026-10-04 21:27–21:29 UTC, before any real-data statistic.*
- **N1 Within-segment pseudo-erasures (W boundaries).** Same agent, same day, gap-matched (0.05 decade): the change in alignment across a boundary with no erasure. This is HH339's "matched placebo call" and removes time-of-day, recency and drift.
- **N2 Kickoff control (O3).** The prompt-held field should not move.
- **N3 Posted-unread placebo (O4).** Room messages of equal duration that the statement could not have read.
- **N4 Synthetic worlds (axis F), run first** on the real skeleton (statements, times, rooms, boundaries, producing calls, ledger reads): null (no drop), context-held 30% and 50% drops with recovery in R, erasure noise (post-erasure variance ×1.5, no drop), segment ramp (alignment builds with context position, context-held), and a common slow drive (room amplitude drifts in time for all agents, no erasure effect). Room separation calibrated to H100's Q_spont per period; statement noise from the real day-centred statement dispersion (an instrument, not an outcome).

## Impostors (STANDARDS §1)
| Impostor | Relevant? | How it is handled | Status |
| --- | --- | --- | --- |
| Scheduler field | yes (erasures come in dense activity) | The 41-call cap sets the erasure time, not the agent. Comparison is within agent and day, gap-matched (0.05 decade) to W boundaries; day centring removes day-level shifts. | removed |
| Exogenous field (kickoff, goal, operator) | yes | Day centring removes the common goal/kickoff field; room-kickoff and operator-message directions are projected out of the axis; the kickoff-alignment control (O3) must stay flat. Unrecorded room drives (shared repos) stay inside the axis. | partly |
| Shared model priors (family, style) | yes | DQ5 `style_resid` vectors; agent constant â_i removed; strata are within agent. | removed |
| Contemporaneous convergence | for the recovery only | The drop is one agent's change at an exogenous moment, not co-movement. The recovery is regressed on items read vs posted-unread of equal duration (O4). | partly |

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R-ctx (HH339: context-held coupling), R-art (self-made field: own work), R-fast (restored by the first-call backlog), R-loop (self-copy loss), R-prior (agent constant only).
**Locked holdout used for confirmation:** none run. `analysis/confirm.py` (frozen, dry-run only) targets forced erasures in the held-out regime-III two-room periods #45, #46 (46a–c), #47 and #50; the #51 tail is single-room and not used.

| Axis | Test (plan) | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | room axis, alignment and erasure labels from shared fields; both models; invariant across rooms and periods | 1 | Shared tables only; leave-agent-out axis with field directions removed; both models agree in every pooled number. Invariance of the axis across rooms not tested separately. |
| B assumptions | quasi-random erasure timing (gap and position audit); stationarity of alignment within segments | 1 | Timing set by the 41-call cap; gap-matched coverage 0.30–0.82 of forced events; median 2 statements per segment limits the window (A1). Within-segment stationarity is not met (post hoc profile). |
| C adequacy | δ_F against the W-boundary placebo and the kickoff control | 1 | The W-placebo comparison is calibrated (size 0.00) and the kickoff control is flat; no likelihood comparison. |
| D unfitted predictions | recovery slope κ_R and the R-fast split are not fitted | 1 | κ_R is unfitted and positive (small); R-fast split null. HH339's signature (drop then read-driven recovery) absent. |
| E interventional | NE41 forced erasures (exogenous); voluntary contrast | 1 | 3,477 exogenous erasures: the context-held prediction fails; voluntary erasures agree. |
| F identifiability | real-skeleton synthetic: size, power at δ = 0.3, recovery identification | 2 | Size 0.00 pooled; power 1.00 pooled in both models at δ = 0.30; estimand recalibration (A1); recovery identified (0.97), with a liberal test fixed by null quantiles. Per-period power low outside G38 and 51g. |
| G ground truth | rooms from the ledger; room kickoffs known (#38, #44) | 1 | Rooms from chat; room kickoffs from `goal_fields`; the room-kickoff pre level is not identified in #44. |
| H comparative | R-ctx vs R-art vs R-fast vs R-loop vs R-prior | 1 | R-art/R-prior (no drop) beat R-ctx; R-fast and R-loop moot; R-art vs R-prior not separated. |
| I transfer | same result across 8 periods and both models; holdout not run | 1 | Same sign in 7/7 identified periods' pooled estimate, both models; holdout not run. |

**Scorecard: A1 B1 C1 D1 E1 F2 G1 H1 I1.**

## Prediction
*Written 2026-10-04 21:27–21:29 UTC, before the synthetic validation and before any H109 statistic on real data.*

**What I had seen when writing this (so these are not blind):** the H100, H102, H44, H46, H69, H70, H87 and H96 cards; boundary counts per unit (above). H46 reports that content does not move beyond its day-to-day band at forced erasures (T 0.86), and H102 that a hopper's content follows the room it speaks in. No H109 estimator has been computed.

My expectation: **no drop.** H46's content stability across erasures, H70's own-repo return and H102's situational room content all point to order held by the agent's work and the room it speaks in, not by the erased context. Prior on HH339's ≥ 30% drop: about 0.2.

- **P0, synthetic (axis F; run first).** On the real skeleton: (a) size of the "δ_F > 0" test ≤ 0.07 in the null, erasure-noise and common-drive worlds [0.7]; (b) power ≥ 0.8 at δ = 0.3 for the pooled NE41 estimate, and in ≥ 4 of 8 periods [0.6]; (c) κ_R recovered with the right sign in the context-held world and κ_U ≈ 0 [0.5]. If (b) fails for a period, that period's negative is "inconclusive".
- **P1, context-held order (HH339's core; the test).** Pooled δ_F ≥ 0.30 with its 95% CI above 0, and per period δ_F > 0 (CI) in ≥ half of the identified periods, both models. **Kill:** pooled δ_F's CI upper bound < 0.30 with P0(b) power ≥ 0.8. I predict the kill fires [0.75].
- **P2, kickoff control.** |δ_K| < 0.15 pooled (prompt-held field does not fall) [0.75].
- **P3, recovery by reading.** If P1 holds: κ_R > 0 and κ_R − κ_U > 0 (CIs) [0.5 conditional]. If P1 fails: κ_R's CI includes 0 (nothing to recover) [0.7].
- **P4, R-fast.** If any drop appears, it is concentrated in statements produced before any room item was read (δ_F(R = 0) > δ_F(R > 0)) [0.5].
- **P5, voluntary.** δ_V within 0.15 of δ_F (both erase the same channel) [0.5].
- **P6, self-copy.** δ_F without dedupe − δ_F with dedupe ≥ 0 (losing in-context restatements adds an apparent drop; H69) [0.6].

**Verdict rules.**
- *Period:* **supported** if δ_F ≥ 0.30 with CI lower > 0 and |δ_K| < 0.15; **failed** if δ_F's CI upper < 0.30 and that period's synthetic power ≥ 0.8; **descriptive** if Ā_pre,F is not identified (CI includes 0); **mixed** otherwise (labelled inconclusive when power < 0.8).
- *Natives:* G41 as a period, and supported only with bge and gte agreeing in sign. G38/G44 add P2 per period (room-kickoff alignment). G51 supported if P1 holds there and P3's κ_R − κ_U > 0. NE41 carries the pooled P1, P5 and the random-effects summary.
- *Hypothesis:* **supported** if P1 passes (both models) and P2 holds; **failed (killed)** if P1's kill fires with power ≥ 0.8; **mixed** otherwise.
- *Multiplicity:* 8 periods × 2 models × 3 dedupe variants; only the rules above count. Per-period p-values are descriptive.

### Amendment 1 (2026-10-04 21:44 UTC, after the synthetic validation, before any H109 statistic on real data)
`analysis/synthetic.py` on the real skeleton (all regime-III non-holdout chat statements, real rooms, reset segments, boundaries and ledger reads). bge: 30 replicates per world; gte: 20. Calibration (instruments): statement noise = the real day-centred, agent-goal-demeaned covariance; agent constants τ² = 0.0014 (H100); room half-separation m_P = √S_spont/2 from H100 (bge; 0.12–0.31; 51g gets the median).

| World (bge) | noise-free estimand δ_F (pooled) | pooled RE δ_F median | pooled CI > 0 | kill fires (CI upper < 0.30) | per-period power (CI > 0) |
| --- | --- | --- | --- | --- | --- |
| null | 0 | 0.01 | 0.00 | 1.00 | 0.00–0.10 |
| erasure noise | 0 | 0.00 | 0.00 | 1.00 | 0.00–0.03 |
| common drive | 0 | 0.00 | 0.00 | 1.00 | 0.00–0.07 |
| HH literal (30% for k ≤ 3) | 0.12 | 0.17 | 0.67 | 0.57 | 0.00–0.37 |
| read30 (1 − 0.6 e^{−R/15}) | 0.29 | 0.38 | 1.00 | 0.00 | G38 0.87, G51 0.97, G41 0.40, G44 0.43, others ≤ 0.07 |
| read50 (1 − 0.8 e^{−R/15}) | 0.48 | 0.63 | 1.00 | 0.00 | G38 0.97, G51 0.93, G44 0.70, G41 0.53 |
| ramp (context build-up) | 0.10 | 0.13 | 0.63 | 0.80 | ≤ 0.40 |

gte (20 replicates): null pooled 0/20, read30 pooled 20/20 (HH pass 0.85; G38 0.85, G51 1.00, G41 0.55, G44 0.25).

Changes forced by the synthetic (none to the predictions):
1. **The effect size is read on the estimand scale.** Scoped statements are sparse: median 2 per reset segment. So the pre-erasure statements are themselves early in their segment, and HH339's literal "30% lower for the first 3 statements" world gives an estimand of only 0.12. "Falls by ≥ 30%" now means δ_F = 0.30 as the noise-free value of the estimator. The power world is read30: a statement made before any room item is read loses 60% of its room component, with an e-fold of 15 items read.
2. **Power.** P0(a) passes (size 0.00 pooled; ≤ 0.10 per period). P0(b) passes pooled (power 1.00 in both models) but fails per period (≥ 0.8 only in G38 and G51). By the card rule, a negative in G36, G37, G39, G41, G42 or G44 is *inconclusive*; only G38, G51 and the pooled estimate can fail.
3. **Pooled RE bias.** The random-effects mean of per-period ratios is biased upward near 0.3 (median 0.38 at estimand 0.29): each period's denominator Ā_pre is noisy. It is centred under the null (0.01). The kill rule (CI upper < 0.30) fires in 100% of null worlds and 0% of read30 worlds, so it keeps its meaning. The direct pooled estimator (one stratified estimate over all periods) is reported beside it.
4. **Recovery test is liberal.** Under the null, κ_R − κ_U is centred at +0.007, and "CI > 0" rejects in 10% (bge) and 20% (gte) of replicates. New rule for P3: κ_R and κ_R − κ_U must exceed the null 95th percentiles (bge 0.014 and 0.020; gte 0.018 and 0.023), as well as their CIs exceeding 0. read30 gives κ_R ≈ 0.032 (CI > 0 in 0.97).
5. The synthetic uses random room axes, so it does not project field directions; the real run does.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | descriptive | δ_F −0.12 [−3.15, 2.63]; pre level not identified (bge); gte 0.28 [−1.60, 2.16]; power 0.00 |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | mixed | δ_F 0.23 [−0.25, 0.50] (gte −0.04 [−1.08, 0.29]); power 0.03: inconclusive |
| [G38](goalperiod-subhypotheses/G38/README.md) | native | failed | δ_F −0.26 [−0.38, −0.07] (gte −0.19 [−0.31, −0.04]): alignment rises; power 0.87; δ_K 0.04 [−0.29, 0.35] |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | mixed | δ_F −0.24 [−2.29, 0.43]; gte pre not identified; power 0.07: inconclusive |
| [G41](goalperiod-subhypotheses/G41/README.md) | native | mixed | δ_F −0.20 [−0.57, 0.05] (gte −0.22 [−0.47, 0.05]); both models a rise; power 0.40: inconclusive |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | mixed | δ_F −0.32 [−1.17, 0.64] (gte −0.10); power 0.03: inconclusive |
| [G44](goalperiod-subhypotheses/G44/README.md) | native | mixed | δ_F −0.08 [−0.40, 0.13] (gte −0.00 [−0.24, 0.14]); power 0.43; room-kickoff pre level not identified |
| [G51](goalperiod-subhypotheses/G51/README.md) | native | failed | 51g: δ_F 0.05 [−0.13, 0.19] (gte 0.07 [−0.09, 0.21]); power 0.97; κ_R 0.031 [0.008, 0.055], κ_R − κ_U 0.045 |
| [NE41](goalperiod-subhypotheses/NE41/README.md) | native | failed | RE δ_F −0.08 [−0.23, 0.07]; δ_V −0.04 [−0.13, 0.06]; δ_K 0.08 [−0.12, 0.28]; pooled power 1.00 |

## Results
### Exploratory round 1 (2026-10-04; non-holdout only, asserted in the scheme)
- **Scheme:** 55,006 regime-III non-holdout chat statements (24,052 in the scoped rooms); boundaries per dedupe variant (restate: 3,477 forced, 2,559 voluntary, 13,538 within); post-erasure reads for k ≤ 10. 4 MB in `data/processed/H109-erasure-demagnetizing-pulse/`.
- **Code:** `scheme/build.py`; `analysis/{h109lib,synthetic,run,report,confirm}.py`.
- **Numbers:** `results/results.json`; `synthetic/synthetic_summary_{bge_small,gte_modernbert}{,_recovery,_recnull}.json`. Estimates: 64 rows in `per_period_estimates` (hypothesis H109).
- **Figures:** `figures/summary_obs.pdf` (δ_F per period, both models; synthetic power), `figures/summary_obsb.pdf` (pooled event profile).

**Headline.**
1. **No demagnetizing pulse.** Room alignment does not fall after a forced erasure. Random-effects mean over the 7 periods with an identified pre level: δ_F −0.08 [−0.23, 0.07] (bge), −0.07 [−0.18, 0.04] (gte). The CI upper bound is far below 0.30 in both models, where pooled synthetic power is 1.00. HH339's kill fires.
2. **It is the same in every powered period and every variant.** 51g (#general/#focus, 1,430 forced erasures): 0.05 [−0.13, 0.19]. Without dedupe −0.08, copies dropped −0.07, first statement only −0.08, no agent constant −0.08, white32 vectors −0.07 (all bge RE). The agent-cluster bootstrap agrees.
3. **The prompt-held field does not move either.** Kickoff alignment δ_K 0.08 [−0.12, 0.28] (bge, 6 identified periods), 0.00 [−0.18, 0.19] (gte). So the erasure is not a general content jump.
4. **Voluntary consolidations agree.** δ_V −0.04 [−0.13, 0.06] (bge), −0.08 [−0.19, 0.02] (gte).
5. **Reading the room pulls a little.** After a forced erasure, alignment grows with the room items read, beyond the posted-unread placebo: κ_R 0.019 [0.003, 0.034] per e-fold of items, κ_R − κ_U 0.025 [0.003, 0.046] (bge; above the null 95th percentiles 0.014 and 0.020). gte 0.017 [0.001, 0.033] sits at its null 95th percentile (0.018). The pull is concentrated in 51g (0.031 [0.008, 0.055]; gte 0.037). It is about a tenth of the alignment level (0.07–0.28) per e-fold, too small to leave a drop after an erasure.
6. **Post hoc: alignment rises after an erasure.** The direct pooled estimator gives −0.12 [−0.21, −0.03] (bge), −0.08 [−0.16, −0.005] (gte); #38 alone −0.26 [−0.38, −0.07] (gte −0.19). The event profile falls slightly over the last pre-erasure statements (1.08 → 0.95 of the pre mean) and climbs after the erasure. Read with care: later post-erasure positions come only from long segments.

**Synthetic validation (axis F):** Amendment 1 (size 0.00 pooled; power 1.00 pooled at δ = 0.30; per-period power ≥ 0.8 only in G38 and 51g).

**Outcome vs prediction**

| | Prediction (locked) | Outcome | Verdict |
| --- | --- | --- | --- |
| P0 | (a) size ≤ 0.07; (b) power ≥ 0.8 pooled and in ≥ 4/8 periods; (c) κ_R recovered | (a) 0.00 pooled, ≤ 0.10 per period; (b) 1.00 pooled, 2/8 periods; (c) 0.97 | (a), (c) passed; (b) pooled only |
| P1 | δ_F ≥ 0.30, CI > 0 (HH339); kill if CI upper < 0.30 with power ≥ 0.8 | −0.08 [−0.23, 0.07] / −0.07 [−0.18, 0.04]; 0/7 periods with δ_F > 0 (CI) | **killed** (as I predicted) |
| P2 | \|δ_K\| < 0.15 | 0.08 [−0.12, 0.28] / 0.00 [−0.18, 0.19] | holds (wide CI) |
| P3 | no drop: κ_R CI includes 0 | κ_R 0.019 [0.003, 0.034] / 0.017 [0.001, 0.033] | **failed** (small pull without a drop) |
| P4 | a drop concentrates at R = 0 | no drop; R = 0: −0.10 [−0.24, 0.02] (300), R > 0: −0.11 | moot |
| P5 | δ_V within 0.15 of δ_F | −0.04 vs −0.08 (gte −0.08 vs −0.07) | holds |
| P6 | no-dedupe δ_F − dedupe δ_F ≥ 0 | +0.005 (bge), −0.03 (gte) | ≈ 0, not supported |
| HH339 | drop ≥ 30%, recovery ∝ reads | no drop; a small read pull | **failed** |

**What this means.**
1. In magnet terms, the erasure pulse does not demagnetize the spin. The room's spontaneous order is not held in the context window. It is held by fields the erasure leaves in place: the agent's own work (H70: 89% return to the own repo), the prompt and memory, and the room the agent posts in (H102).
2. Coupling through reading exists but is weak (κ_R ≈ 0.02 per e-fold of items). This agrees with H48's small pull per read and H102's zero hopper dose.
3. In Kolchinsky–Wolpert terms, the context channel carries ≈ 0 of the room-order information. H87 found the same channel carries most of the output value. So the context window carries *work* value (H70, H87: κ_C ≈ 5 commits per 20 calls per bit), not *identity*.

**Operator-facing conclusion.** Resetting an agent's context does not erase its room's content identity: alignment stays within −7% to +23% of its pre-erasure level (pooled 95% CI). Use erasures to break loops or clear clutter (H44, H69) without worrying about room differentiation. To change what a room talks about, change its work or its instructions, not its members' context.

**Caveats.**
- Per-period power is low outside G38 and 51g; those six per-period negatives are inconclusive.
- The room axis is a period-level ruler from other agents' means (H100's Δ_spont direction). A drop along some other, faster room-specific direction would not be seen.
- The context-held world is a model (read30: 60% loss at R = 0, e-fold 15 items). A drop that recovers within the first post-erasure call (before the first statement) is invisible here. R = 0 statements (300 events) show no drop either.
- Post hoc: the post-erasure rise and the profile shape.

**Claim that stands:** across 3,477 forced erasures in 8 non-holdout regime-III two-room periods, an agent's alignment with its room's spontaneous content axis does not drop: δ_F −0.08 [−0.23, 0.07] (bge; gte −0.07 [−0.18, 0.04]), excluding a 30% drop at synthetic power 1.00. Excluded: the per-period negatives outside G38 and 51g (unpowered), the post-erasure rise (post hoc), and the reading pull κ_R ≈ 0.02 (borderline in gte).

### Confirmatory design (written 2026-10-04 after exploration; not run)
`analysis/confirm.py`, frozen (sha256 of `h109lib.py`, `scheme/build.py` and itself in `analysis/confirm.sha256`), predictions in its header:
- **C1 (kill holds):** RE δ_F over the held-out two-room periods #45, #46 (46a–c), #47, #50 has CI upper < 0.30 [0.8].
- **C2 (no drop):** RE δ_F point ≤ 0.05 [0.7].
- **C3 (prompt-held field):** |RE δ_K| < 0.15 where identified in ≥ 2 targets [0.6].
- **Guards:** `--confirm` plus `H109_CONFIRM=1`; refuses if the frozen hashes changed; `holdout_ledger.check()` per target (family `content_alignment`). `--dry-run` uses #38, #41, #44 and asserts no held-out row; it passed (output in `data/processed/H109-erasure-demagnetizing-pulse/confirm_dryrun/`).
- **Reuse disclosure:** #45–#47 and #50 content is planned by many hypotheses (H23, H26, H47, H81–H83, H100, H102). H109's statistic is new; the modality is shared. Disclose before running.

## Round 2 redirects
- **H109-R1. What holds the order?** Split post-erasure alignment by whether the agent's first post-erasure action re-opens its own repo (H70 pointer) vs reads the room. If the repo holds the order, alignment should track the repo, not the reads.
- **H109-R2. The post-erasure rise.** Test pre-registered: does room alignment fall with context fill (k_ctx, received items) inside a segment? If so, context *dilutes* room order and the erasure restores it (an anti-demagnetizing pulse).
- **H109-R3. A call-clock version.** Measure alignment at the call level (talk calls only) in the first 1–3 calls after an erasure, to see a drop that recovers before the first statement.
- **H109-R4. Confirm** on #45–#47, #50 after Vivian's sign-off and the ledger disclosure.

## Notes
- 2026-10-04 21:27 UTC: round-1 agent started; read CLAUDE.md, GOALS.md, STANDARDS.md, DEFINITIONS.md, swarm-constants, holdout, infra README and the cards listed above.
- 21:27–21:29 UTC: card filled (question, model, scheme, observables, nulls, impostors, predictions) before any H109 statistic. Only sampling facts seen: forced/voluntary/within boundary counts per unit.
- 21:31 UTC: period folders with dated predictions. 21:32–21:44 UTC: scheme build and synthetic validation; Amendment 1 at 21:44 UTC.
- 21:44–21:46 UTC: real-data run (both models), report, estimates.
- One reporting change after seeing results (labelled, no verdict change): the pooled RE means of δ_F and δ_K are reported over periods with an identified pre level (the card's O2/O3 rule); including all 8 periods gives −0.08 [−0.23, 0.06] and 0.08 [−0.12, 0.28].
- Suggested shared changes (not made; outside edit scope): a shared `rooms_asof.py` / statement-room helper (H100, H102 and now H109 use the statement room); a DEFINITIONS entry for *room alignment a_t*, *erasure drop fraction δ_F*, *re-read slopes κ_R, κ_U*; an infra Known issue: "erasure event studies at statement level are attenuated (median 2 statements per reset segment); calibrate effect sizes on the estimand scale"; NE41 catalog note (no room-alignment drop; read pull κ_R ≈ 0.02).
