# H10: Goals are Legendre pushes: a swarm's response to an assigned goal is predictable from its unforced fluctuations

**Status:** round 1 done (2026-10-03): **failed** in exploration. Goals are not small Legendre pushes in the village: free-week fluctuations do not predict who follows the goal, and the variance moves the wrong way. **Round 1b (improved data, 2026-10-04): still failed, in both embedding models.** P1 fails in all 8 input configurations (bge and gte-modernbert × base / restatement-deduped / style-residualized; Stouffer p 0.84–0.96); the shared goal vectors change nothing (H10's own matched them). Natives: #26's agent-set goal moves agents about 1 SD but P1 is wrong-signed again (failed); NE38's single-agent reassignment is a quench 10–20 SDs deep that no tilt can reach (mixed by the control rule); #44's assigned room moves along its own kickoff and the self-chosen room does not (mixed, model-dependent). Confirmatory script written, not run.
**Fields:** stat mech, info theory
**Origin:** HH49 + HH85 (shortlist 2, item 1) (`../hypohypotheses/HYPOHYPOTHESES.md`; `../promotion-shortlist.md`)
**Definitions used:** agent; regime (never pooled across; every pair lies inside one regime); driving / external field (the village goal, here as a *linear* field along ĝ); agent state, variant *vector (for model 11)*, operationalized as the **statement-mean projection** below (proposed as a named variant, see Notes); goal period as the unit of analysis, with exception (c) for the free → assigned transitions.

## Standards (2026-10-04)
**Question served:** Q2 (the goal as a field: does it act as a linear push) and Q5 (forecasting steerability).

| Impostor | Relevant? | How it was handled | Status |
| --- | --- | --- | --- |
| Scheduler field | no | Content projections along ĝ; no timing statistic. | n/a |
| Exogenous field (kickoff/goal/operator) | yes | The goal field is the object. Shared `goal_fields`, transverse-direction null (Null / baseline), per-room kickoff in G44. In NE38 the incumbent control drifted −3.1 SD. Other operator messages are not regressed out (§1). | partly |
| Shared model priors | yes | `statements_style_resid_period32` in both models (Round 1b); P1 fails in every configuration. | removed |
| Contemporaneous convergence | no | No agent-to-agent influence claim; R2 (common target) is a form of field response. | n/a |

**Inputs:** all current: shared goal fields, gte, DQ5 dedupe, `style_resid`. Activity not used.

**Two layers:** 7 replication folders (pairs #11→#12a, #16→#17, #37→#38a). Natives: 3 (G26 failed, NE38 mixed, G44 mixed).

**Confirm script:** `confirm.py` (#22b→#23, #31a→#32), written, not run. Re-freeze: no for the data fixes (bge numbers reproduce exactly); a gte arm would meet STANDARDS §2. #32 was consumed by H05's executed NE12 run, so the card's reuse note is stale (holdout item 4).

## Question
Estimate the free energy F(m) of the swarm's alignment m from its fluctuations in field-free (pick-your-own-goal) weeks. Can it predict how the swarm lines up behind an assigned goal, by tilting G = F − h·m, without refitting? Practical payoff: forecasting how steerable a swarm is from how it behaves when nobody steers it.

## Model
**From:** `physics-models/11-vector-spins` (mean-field O(n): **m** = L_n(β(J₀|**m**| + h)) **m̂**; susceptibility χ = N·var(m)), with `physics-models/01-inverse-ising` for the scalar Curie–Weiss analogue. One field parameter h per assigned week is fitted to the mean shift; the variance and higher cumulants under the field are then *predicted* (an unfitted test, axis D).

## Data scheme (`scheme/`)
Shared tables in `data/processed/shared/` (see `infra/README.md`), including the new embedding-derived agent states (`embeddings/agent_day*`, `agent_win30*`, `statements.parquet`, per-regime whitening via `common.load_whitener`). Goal direction ĝ: embed the goal and kickoff texts (`common.load_goals`) with the same model (bge-small).
- **Inputs:** `embeddings/statements.parquet` + `chat_bge_small.npy` / `intentions_bge_small.npy` (each agent's own chat messages and self-written intentions); `whitening_<regime>.npz`; `calendar`, `roster`, `chat_core` + `chat_text` (kickoff texts only, held in memory, never stored); raw `village_goals`.
- **Transform (`scheme/build.py`):** non-holdout statements only, the Claude Code agent excluded (separate scaffolding). Each statement → whitened n = 32 coordinates in its regime basis, unit-normalized: ẑ_k. Goal vectors per goal period: the goal text and the kickoff (human messages ≥ 250 chars within [window start − 10 min, + 45 min] of the period's first active day, previous-goal boilerplate stripped; the same rule as H01's scheme), each embedded with bge-small, whitened in the period's regime basis; ĝ = unit(unit(W·goal) + unit(W·kickoff)). Variants stored: goal-text only, kickoff only, n = 16 and 64.
- **Output:** `data/processed/H10-goals-are-legendre-pushes/`: `statements.parquet` (agent, t, pt_date, goal_no, regime, win30, kind; no text) with `stmt_w64.npy` (fp16 whitened, the first 32 columns are the primary n = 32; normalized downstream), `goals.parquet` + `goal_vecs.npz`, per-analysis outputs in `G<NN>/` and `NE34/` (data side; the READMEs live in `goalperiod-subhypotheses/`), and `_provenance.json`.
- **Regimes covered:** I (pairs #11→#12, #16→#17; free week #31) and III (#37→#38). No pair crosses a regime boundary.

## Candidate goal periods
Field-free weeks #11, #16, #31, #37 (#22 🔒 held out) → the assigned weeks after them (#12, #17, #32 🔒, #38; #23 after #22 🔒). Kickoff responses at goal changes (NE34, non-holdout transitions). A spanning test (free week → next week) is the named exception (c).
- **Folder choice:** a single `goalperiod-subhypotheses/NE34/` folder holds the three free → assigned pair tests and the kickoff event study as tables (the overview builder reads only `G<NN>` and `NE<NN>` folder names). Each period also has its own `goalperiod-subhypotheses/G<NN>/` folder with its per-period prediction and descriptive statistics.
- **#23 is not held out in `holdout.json`, but it is kept untouched** in round 1 (not used as a pre- or post-period anywhere), so that the confirmatory #22 → #23 pair stays blind on both sides.
- **#31 → #32:** #31 is explored as a free week (its F(m) along ĝ₃₂ is *not* computed in round 1, because ĝ₃₂ is the confirmatory direction; #31 is described along the other assigned weeks' ĝ only).

## Links to other hypotheses
Shares the embedding pipeline with H01 D3 (D3-MF, P9) and H12. Doesn't duplicate H01's per-period polarization fit; uses it as an input where available.

## Observables
*Specified 2026-10-03, before any real-data run.* All in the whitened n = 32 basis of the pair's regime; ĝ = ĝ_A, the direction of the **assigned** week A, is used in both the free week F and in A.

- **Statement alignment** y_k = ẑ_k · ĝ ∈ [−1, 1].
- **Agent-window alignment** x_{i,t} = mean of y_k over agent i's statements in 30-min window t (`win30` of the shared tables); eligible if n_{i,t} ≥ 2 statements. The vector version **x**_{i,t} ∈ ℝ³² is the mean of ẑ_k.
- **Per-agent cumulants in a segment** (equal weight per window; statement-sampling noise removed by method-of-moments, as in a one-way ANOVA):
  - mean μ_i;
  - signal variance κ2_i = var_t(x_{i,t}) − mean_t(s²_{i,t}/n_{i,t}), with s² the within-window variance of y;
  - third cumulant κ3_i = third central moment of x_{i,t} − mean_t(m3_{i,t}/n²_{i,t});
  - pooled shape per segment: γ = Σ_i κ3_i / Σ_i κ2_i^{3/2} (one skewness per segment, shared by its agents) and, likewise, one excess kurtosis.
  - the 32 × 32 matrix version C_i = Cov_t(**x**_{i,t}) − mean_t(S_{i,t}/n_{i,t}); C = mean_i C_i.
- **Swarm order parameter (fluctuation part)** δm(t) = mean over eligible agents of (x_{i,t} − μ_i), in windows with ≥ half the segment's agents eligible. Swarm signal variance V = var_t(δm) − mean_t[N_t⁻² Σ_i s²_{i,t}/n_{i,t}].
- **Collective enhancement and mean-field loop gain along ĝ:** R = V / V_indep, with V_indep = mean_t[N_t⁻² Σ_{i∈t} κ2_i] (what independent agents would give); g = 1 − 1/R. In mean-field O(n) linear response, χ_swarm = χ₀/(1 − βJ₀χ₀), so g = βJ₀χ₀ is the loop gain (the content-level analogue of H02/H05's loop gains).
- **Free energy** F̂(m) = −ln P̂(m), kernel estimates of the noise-deconvolved per-agent and swarm deviations (for figures; the tests use cumulants).
- **The push.** Per agent present in both segments, Δ_i = μ_i^A − μ_i^F; the pair's mean shift Δ̄ = mean_i Δ_i; the 32-d response Δ**μ** = mean_i (**μ**_i^A − **μ**_i^F).
- **The one fitted parameter** per pair: the tilt λ = βh (effective field in units of the projection) solving Δ̄ = λ·κ̄2 + (λ²/2)·κ̄3, with κ̄2 = mean_i κ2_i^F and κ̄3 = mean_i γ_F (κ2_i^F)^{3/2} (the root continuous with Δ̄/κ̄2). The size of the push in free-week standard deviations, ε = λ·√κ̄2, says how far outside linear response the pair is.
- **Segments.** F = all active days of the free week. A = the first unit of the assigned week (up to its first catalogued step change), **days 2+** (day 1 is the kickoff transient, analyzed in the kickoff event study). #12 ends at 2025-09-05 (scaffold change C), so A = 09-02 … 09-04; #17: 10-14 … 10-17; #38: 04-03 … 04-13 (before NE17). Agents: ≥ 6 eligible windows in both segments; the Claude Code agent excluded.
- **Kickoff event study (NE34):** at every non-holdout goal change inside one regime (both neighbours non-holdout; #23 excluded), the jump Δm_k = mean over shared agents of (mean on the first new day − mean on the last old day) along ĝ_new, and the pre-period fluctuation v̄_k = mean_i κ2_i along ĝ_new over the last ≤ 5 active days of the old period.

## Null / baseline
*Specified 2026-10-03, before any real-data run.* The Legendre push is the claim that the goal enters the agents' "Hamiltonian" only as a linear term λ·Σ y and changes nothing else. Then P_A(state) ∝ P_F(state)·e^{λ·Σ y} *exactly* (an exponential tilt), whatever F is, so every cumulant under the field follows from F's cumulants and one λ: κ_n^A = K_F^{(n)}(λ). The rivals each break one part of this:

| Rival | What the goal does | Predicts |
| --- | --- | --- |
| R0 no response | nothing | Δ̄ = 0 |
| R1 uniform translation | shifts every agent by the same amount | Δ_i = Δ̄ for all i (P1 fails); variance unchanged |
| R2 common target (convergence) | pulls every agent to the same alignment | μ_i^A = c for all i; Δ_i = c − μ_i^F (slope −1 on μ_i^F) |
| R3 confinement / cooling | adds a restoring (quadratic) term: focus | variance under the field *below* the tilt prediction |
| R4 quench / dispersal | re-randomizes; transients, sub-tasks | variance *above* the tilt prediction; drift within A |
| R5 coupling change | changes J₀ as well as h (collaborative goals couple agents) | loop gain g changes across the step |
| R6 agent-specific receptivity | each agent has its own λ_i | Δ_i uncorrelated with κ2_i^F (P1 fails) |

Statistical nulls: exact permutation of κ2_i^F across agents (P1); day-block bootstrap within each segment (all CIs); Haar-random rotations of C's eigenvectors, keeping its eigenvalues (P4); cross-week placebo C from another free week of the same regime (P4, regime I only); the transverse-direction null for the variance tests (the same statistics along 50 random unit directions orthogonal to ĝ, which no goal pushes).

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R0–R6 in "Null / baseline" (no response; uniform translation; common target; confinement/cooling; quench/dispersal; coupling change; agent-specific receptivity).
**Locked holdout used for confirmation:** none yet. Planned: #22 → #23 and #31 → #32 (`analysis/confirm.py`, written, not run).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Order parameter from dataset fields: statement-mean projection on ĝ (goal + kickoff text) in the per-regime whitened bge basis, statement noise removed by ANOVA. Assumptions listed (linear field, unchanged F). Not checked for invariance across families; no embedding-model swap; at n = 16 the #16 → #17 push vanishes. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Audited: stationarity fails in 3 of 7 segments (#11 drifts; #12a still relaxing; #38a ramps for ten days). The equilibrium reading of a week is doubtful. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 0 | The tilt does not beat uniform translation (R1): its leave-one-agent-out error is 1.4–2.4× translation's in all three pairs. It beats only R0 (no push). |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | P1 (who moves) failed: r = −0.37, −0.69, +0.20, Stouffer p = 0.89. The cross-transition version failed with the opposite sign (Spearman −0.56, p = 0.015, n = 18). The variance moved opposite to the tilt (descriptive). |
| E interventional | predicts the change across a natural experiment | 0 | Goal changes (NE34) are the intervention. The tilt fails to predict them. A push appears at 19/19 changes into assigned goals but is not tilt-shaped. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Synthetic mean-field O(32) at village sampling (3,060 replicates): P1 identifiable (95% combined power at ε ≈ 2); P2 only for ε ≤ 0.34; P3, P4 not identifiable (demoted, Amendment 1). |
| G ground truth | agrees with known structure | 1 | Instrument level only: the order parameter jumps at every change into an assigned goal and not into free weeks. No ground truth for the tilt itself. |
| H comparative | beats the named rivals | 0 | Loses to R1 (translation) on prediction error. The common-target rival R2 describes #11 → #12a better (slope of Δᵢ on μᵢ^F = −1.41). |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Fails in 2/3 pairs, inconclusive in the third; holdout not run. |

## Prediction
*Written 2026-10-03, before running any analysis on real data.*

**What I had seen when writing this:** the round-1 results in `LOG.md` (H02 pairwise activity couplings at the noise floor; H04 nudges act through unread context with a delay, kickoffs don't change activity level; H05 rooms are coupled blocks for talk; mean-field loop gains 0.06–0.4), H01's card through Amendment 3 (its P9 predicts βJ₀ < 0.5·n in every period; agent fields are not stable across periods in regimes II/III), and *counts only* for the candidate periods: days, agents, statements and statements per agent-window (regime I: medians 8–16 per 30-min agent-window, 30 windows per week; #37: median 3, 27 windows; #38: median 4). No embedding, alignment, goal-vector or fluctuation statistic had been computed.

**Primary tests** (the three exploratory pairs #11→#12, #16→#17, #37→#38; per pair, then combined across pairs by meta-analysis, never by pooling the fits):

- **P1, fluctuations predict who moves (per-agent fluctuation–dissipation).** With one shared λ, the tilt predicts Δ_i ≈ λ·κ2_i^F: agents that fluctuate more along ĝ in the free week move further toward the goal. Per pair: Pearson r(Δ_i, κ2_i^F) > 0 (exact permutation p) **and** the tilt's leave-one-agent-out error is below that of uniform translation (R1, also one parameter). **Supported** if r > 0 in ≥ 2/3 pairs and the Stouffer combination of the per-pair one-sided permutation p-values is < 0.05. **Fails** if the combined r is ≤ 0 or r ≤ 0 in ≥ 2/3 pairs (R1 or R6). Rival R2 is checked on cross-split data (μ_i^F from odd windows, Δ_i from even windows), because a noisy μ_i^F would otherwise fake convergence.
- **P2, the variance under the field is predicted without refitting.** (a) Along ĝ: κ2_i^{A,pred} = κ2_i^F + λ·γ_F (κ2_i^F)^{3/2}; statistic ρ = ln(Σ_i κ2_i^{A,obs} / Σ_i κ2_i^{A,pred}) with a 90% day-block bootstrap CI. (b) Transverse: the same ratio along 50 random unit directions ⟂ ĝ, where a pure field along ĝ predicts no change (ρ_⊥ ≈ 0). Per pair: **supported** if the CI of ρ contains 0 and |ρ̂| < ln 1.5; **failed** if the CI excludes 0 and |ρ̂| ≥ ln 1.5 (ρ < 0 = R3 cooling, ρ > 0 = R4 dispersal); otherwise inconclusive. Combined: the majority verdict over pairs. If ρ fails but ρ_⊥ fails with the same sign and size, the variance change is not field-specific (a whole-state "temperature" change), which still counts against H10.
- **P3, the goal changes h, not J₀ (mean-field O(n) χ–fluctuation relation).** g_F and g_A along ĝ; Δg = g_A − g_F with 90% CI. **Supported** if the CI contains 0; **failed** if it excludes 0 and |Δg| ≥ 0.2. Rival R5 predicts g rises into collaborative weeks (#38, mode C), falls into individual-objective weeks (#17, mode I), and for #12 (teams debating, mode M) I expect no clear sign. I expect g < 0.5 everywhere (H01 P9, H02, H05), which makes P3 easy to pass; its power against a realistic J₀ step is reported from the synthetic before it is read.
- **P4, the response follows the soft modes (matrix fluctuation–dissipation).** The tilt predicts the whole 32-d response, not just its projection: Δ**μ** ∝ C^F ĝ. Statistic D = cos(Δ**μ**, C^F ĝ) − cos(Δ**μ**, ĝ). Per pair: **supported** if D's 90% bootstrap CI is above 0 **and** cos(Δ**μ**, C^F ĝ) exceeds the 95th percentile of the eigenvector-rotation null. Regime I pairs also report the cross-week placebo (C from the other regime-I free weeks), which should do worse than the pair's own C if the soft modes are this swarm's and not generic embedding geometry. Combined: supported in ≥ 2/3 pairs. P4 fails if D ≤ 0 in ≥ 2/3 pairs.

**Secondary and descriptive** (reported, not counted in the verdict):
- **Higher cumulants:** the first-order tilt of the third cumulant, κ3^{A,pred} = κ3^F + λ·κ4^F, against the observed; expected to be badly underpowered at 20–60 windows per segment.
- **Swarm-level P2:** V^{A,pred} = R^F·V_indep^{A,pred} (mean field with g unchanged) against the observed V^A.
- **P5, kickoffs (NE34):** at each non-holdout within-regime goal change, Δm_k > 0 for ≥ 80% of transitions into operator- or agent-designed goals (modes C, I, K, M, D), and Spearman(Δm_k, v̄_k) > 0 across transitions within regime I (the cross-transition fluctuation–dissipation). The old goal's field is removed at the same time, so this is only a loose check.
- **Secondary pairs** (N = 4, regime I): #3→#4 and #5→#6, for P2–P4 only (P1 needs more agents). #7→#8 is skipped (2 free days).
- **Robustness:** n = 16 and 64; goal-text-only and kickoff-only ĝ; A including day 1; 60-min windows.

**Overall verdict rule (round 1):** H10 is **supported** (exploratory) if P1 and P2 are supported and none of P1–P4 fails; **failed** if P1 fails, or P2 fails in the same direction in ≥ 2/3 pairs; **mixed** otherwise. Multiplicity: four combined tests, each at one-sided or 90% two-sided level, so the family-wise false-positive rate is up to ~0.2; per-pair numbers are descriptive.

**What I expect (credences):** Δ̄ > 0 in every pair (0.9); a big push, ε > 2 free-week SDs (0.7), which puts the pairs outside linear response, so a Gaussian F predicts essentially "same variance, shifted"; P1 supported (0.35; low power at N = 7–13); P2 fails toward R4, variance above prediction, because goals make agents alternate between on-goal and off-goal content (0.45), supported (0.3); P3 passes (0.7) but mostly from low power; P4 supported (0.35). Overall supported ≈ 0.15, mixed ≈ 0.5, failed ≈ 0.35.

**What counts against H10:** an assigned week whose alignment distribution is not the exponential tilt of the free week's: responses not ordered by free-week fluctuations (P1), a variance change beyond the tilt (P2, especially if transverse variances change too: the goal changed the "temperature", not the field), a change in the loop gain (P3), or a response direction no closer to C^F ĝ than to ĝ (P4).

**Amendment 1 (2026-10-03, after calibration and the synthetic validation, before any real-data statistic along any goal direction).**
*What I had seen:* (i) calibration statistics of the embedding instrument along *random* directions in non-test periods (regime I #8, #10, #13, #18–#21, #24–#27, #30; regime III #39–#42, #44): statement-level variance ≈ 0.027 per direction; per-agent window signal variance ≈ 30% (I) / 22% (III) of it; between-agent spread of means 8% / 28%; window resultant a² ≈ 0.48 / 0.54; lag-1 autocorrelation ≈ 0.35; collective enhancement R ≈ 3.8 (I) / 2.6 (III), so a window-level loop gain g ≈ 0.74 / 0.62 along random directions. The g < 0.5 predictions F2/A3 are therefore likely to fail; they stay as written. (ii) The synthetic validation (`analysis/synthetic.py`, below). No statistic along any goal direction had been computed.
- **P2 is testable only in the perturbative range.** In the synthetic, even when the tilt is exact (Gibbs world), the first-order cumulant prediction is badly biased once the push exceeds about one free-week SD: saturation of bounded spins, and the field pinning the collective soft mode, shrink the variance in ways that 20–60 free-week windows cannot reveal. Rule (fixed in code before the synthetic summary was read): ε_max = the largest median ε among the H and exact-tilt cells, sorted by ε, before the first cell with |median ρ| ≥ 0.15 or with CI coverage of 0 below 80%. P2 gets a verdict only for pairs with ε ≤ ε_max; otherwise it is "n/a (non-perturbative)" and ρ is reported against the synthetic H distribution at matched ε. Consequence: a strong push makes "variance fell" *compatible* with a Legendre push, so R3 cannot be told apart from the tilt there.
- **P3 and P4 are demoted to descriptive (not counted in the verdict).** In the synthetic, P3 has no power against a coupling step (R5 in either direction: same pass rate as H) and a 5–30% false-failure rate under H. P4 is never supported (0–3%) and D is biased *negative* under H: the shrunk 32 × 32 free-week covariance carries estimation noise that only pulls the predicted direction away from the response. So P4's "fails if D ≤ 0" rule would fire under H. Both are still computed and reported.
- **P4 estimator:** Ledoit–Wolf shrinkage of C^F toward (tr C/n)·I (intensity from the pooled within-agent window deviations); the rotation null uses the shrunk eigenvalues.
- **Overall rule, restated:** **supported** if P1 is supported and P2 is supported in at least one testable pair and fails in none; **failed** if P1 fails, or P2 fails in the same direction in ≥ 2/3 of the testable pairs; **mixed** otherwise (including "P2 untestable everywhere").
- **Kurtosis noise correction** (descriptive only) uses each agent's pooled within-window variance.
- **Power, stated before the real run** (synthetic, 3,060 replicates; details in "Synthetic validation"):
  - **ε_max = 0.34** by the rule above. It was set by CI under-coverage (72%) in the 3-day #37 design, where a day-block bootstrap has only three blocks, not by bias: the first-order prediction stays unbiased (|median ρ| < 0.1) up to ε ≈ 1.2 and is biased from ε ≈ 1.5. The rule stands. Pairs with 0.34 < ε ≤ 1.2 get a P2 value labelled "would-be, not counted".
  - **P1 (combined)** is supported in 52% / 63% / 95% of H triples at ε ≈ 0.3–0.8 / 0.6–1.5 / 1.7–3.5; in 10% under uniform translation (R1) and 30% under agent-specific receptivity (R6); it falsely *fails* under H in 23% / 8% / 0%. Per pair, r > 0 has good power at N = 12 (95% of H replicates at ε ≈ 0.8) and weak power at N = 7 (60–75%).
  - **The "tilt beats translation" part of P1** often fails under H even when r is large, because an exogenous common drive adds a shared, field-blind part to every agent's free-week variance (Δᵢ ∝ κ2ᵢ − d rather than κ2ᵢ). So a per-pair "mixed" with r > 0 reads as "ordered but not proportional". This is an interpretation note, not a rule change.
  - **Overall "supported" is nearly unreachable even if H10 is true** (≤ 17% of H triples), because P2 is untestable at realistic pushes; "mixed" is the typical outcome under the truth. "Failed" under H: 28% at the smallest push, ≤ 10% otherwise.
  - The convergence signature (Δᵢ falling with μᵢ^F, rival R2) appears under H at large ε too (saturation; median slope −0.2 to −0.6), so R2 is not separable from the tilt there.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [NE34](goalperiod-subhypotheses/NE34/README.md) (pairs + kickoffs) | exploratory | **failed** | P1 r = −0.37 / −0.69 / +0.20, Stouffer p = 0.89; ε = 3.1 / 1.4 / 1.9 (P2 untestable); variance along ĝ ×7.7 / ×2.8 / ×1.9, transverse unchanged; kickoffs: jump > 0 at 19/19, Spearman(jump, pre-fluctuation) = −0.56 (p = 0.015) |
| [G11](goalperiod-subhypotheses/G11/README.md) (free) | exploratory | descriptive | along ĝ₁₂: γ = −0.51, 2-component by BIC, g = 0.55, drifts down |
| [G12](goalperiod-subhypotheses/G12/README.md) (12a) | exploratory | failed | Δ̄ = 0.20, ε = 3.06, r = −0.37, convergence slope −1.41, g 0.55 → 0.79 |
| [G16](goalperiod-subhypotheses/G16/README.md) (free) | exploratory | descriptive | along ĝ₁₇: γ = −0.30, g = 0.51, stationary |
| [G17](goalperiod-subhypotheses/G17/README.md) | exploratory | failed | Δ̄ = 0.13, ε = 1.42, r = −0.69 (all 6 variants < 0), variance ×2.8 |
| [G31](goalperiod-subhypotheses/G31/README.md) (31a, free) | exploratory | descriptive | along ĝ₁₂/ĝ₁₇ only (ĝ₃₂ kept blind): g = 0.71 / 0.55, R⊥ = 3.9 |
| [G37](goalperiod-subhypotheses/G37/README.md) (free) | exploratory | descriptive | along ĝ₃₈: γ = −0.11, unimodal, g = 0.62 |
| [G38](goalperiod-subhypotheses/G38/README.md) (38a) | exploratory | mixed | Δ̄ = 0.11, ε = 1.92, r = +0.20 (p = 0.27; sign unstable), ramps for 10 days |
| [G44](goalperiod-subhypotheses/G44/README.md) (#42 → #44, per room) | native (1b) | mixed | #best along its own kickoff Δ̄ +0.18 (bge) / +0.24 (gte), ε 0.97 / 1.55; #rest along its own kickoff ≈ 0; room difference +0.17 [+0.11, +0.23] in both; no dispersal |
| [NE38](goalperiod-subhypotheses/NE38/README.md) (Opus 5 reassigned) | native (1b) | mixed | ε 10.2 (bge) / 20.3 (gte); post mean beyond every pre window (no tilt reaches it); other agents ≈ 0; one incumbent drifted −3.1 / −1.0 SD |
| [G26](goalperiod-subhypotheses/G26/README.md) (#25 → #26, leader's goal) | native (1b) | failed | push along the leader's announcement ε 1.06 / 0.93; P1 r −0.14 / −0.63 |

*Round 1b verdicts* (`**Verdict (1b):**` in each folder): NE34 failed, G12 failed, G17 failed (both models); G38 mixed (bge mixed, gte failed); G11, G16, G31, G37 descriptive.

## Outcome vs prediction
| Prediction (2026-10-03, + Amendment 1) | Credence before | Outcome | Verdict |
| --- | --- | --- | --- |
| Δ̄ > 0 in every pair | 0.9 | 0.20, 0.13, 0.11, all CIs > 0; jump > 0 at 19/19 changes into assigned goals | ✓ |
| Push ε > 2 free-week SDs | 0.7 | 3.06, 1.42, 1.92 (kickoffs: median ≈ 2.5, range 1–9) | ~ (1/3 above 2, all > 1) |
| **P1** fluctuations predict who moves | 0.35 | r > 0 in 1/3 pairs; Stouffer p = 0.89; negative and robust in both regime-I pairs | **✗ failed** |
| **P2** variance by the tilt | supported 0.3, fails to R4 0.45 | untestable (all ε > ε_max = 0.34). Descriptively ×1.9–7.7 along ĝ, transverse unchanged: field-specific dispersal (R4-like), opposite to the tilt's large-push shrinkage | n/a (descriptively ✗) |
| **P3** g unchanged (descriptive after Amendment 1) | 0.7 | Δg CIs contain 0 in 2/3; #11 → #12a rose by 0.25 [0.15, 0.57]; R5's sign predictions wrong for #17 and #38 | not counted |
| **P4** response along Ĉĝ (descriptive after Amendment 1) | 0.35 | D < 0 in all pairs (as the synthetic predicted even under H) | not counted |
| P5 jump > 0 into assigned goals | – | 19/19 | ✓ |
| P5 Spearman(jump, pre-fluctuation) > 0 | – | −0.56 (p = 0.015, n = 18, regime I) | ✗ (opposite sign) |
| F1 free-week single well, \|γ\| < 1 | – | \|γ\| < 1 everywhere; BIC prefers 2 components in #11, #16 | mixed |
| F2/A3 g < 0.5 | (seen after: calibration g ≈ 0.6–0.75) | g = 0.51–0.79 everywhere | ✗ |
| F3/A2 stationarity | – | holds in #16, #37, #17, #31a; fails in #11, #12a, #38a | mixed |
| Overall | supported 0.15 / mixed 0.5 / failed 0.35 | **failed** | |

## Synthetic validation (axis F)
`analysis/synthetic.py`; summary `data/processed/H10-goals-are-legendre-pushes/synthetic_summary.json`; figure [`figures/synthetic.pdf`](figures/synthetic.pdf). Mean-field O(32) unit spins with quenched agent directions, heterogeneous concentrations, a mean-field coupling and (calibrated world) an exogenous common drive, observed through vMF-noisy statements with the real periods' statement counts and window structure. Calibrated to the instrument along random directions in non-test periods (statement variance, signal fraction 0.30–0.37, between-agent spread, window resultant 0.48, R ≈ 3.7). 3,060 replicates (60 per cell, 60 bootstrap draws each), analyzed with the real pipeline (`h10lib.analyze_pair`).

| Scenario (λ) | median ε | P1 combined supported | P1 combined failed | P2 testable | H10 supported / failed |
| --- | --- | --- | --- | --- | --- |
| H, calibrated (10) | 0.3–0.8 | 0.52 | 0.23 | 63% of triples | 0.17 / 0.28 |
| H, calibrated (20) | 0.6–1.5 | 0.63 | 0.08 | 35% | 0.15 / 0.10 |
| H, calibrated (60) | 1.7–3.5 | **0.95** | 0.00 | 0% | 0 / 0 |
| H, exact tilt (2 / 6 / 15) | 0.5–3.1 | 0.27 / 0.60 / 0.82 | 0.17 / 0.05 / 0.02 | | |
| H, field misaligned with ĝ (cos 0.5) | 0.3–0.8 | 0.32 | 0.15 | | |
| R1 uniform translation | 1.0–1.3 | 0.10 | 0.57 | | 0 / 0.57 |
| R6 agent-specific receptivity | 0.6–1.6 | 0.30 | 0.20 | | |
| R3 cooling / R4 dispersal / R5 coupling ×1.6, ×0.4 | | 0.65 / 0.52 / 0.57 / 0.77 | | | |

- P1's per-pair r > 0 has 95% power at N = 12 but only 60–75% at N = 7; combined power is high only for pushes ≳ 1.5 SDs, which is what the real pairs had (so the real P1 failure is informative: the false-failure rate under H at ε ≈ 1.5–3 is 0–8%).
- P2: unbiased to ε ≈ 1.2, biased negative beyond (the field pins the soft mode and saturates the spins, so the variance *shrinks*); CI coverage 0.72–0.83 against the nominal 0.90 (few days per segment). ε_max = 0.34 by the pre-set rule.
- P3 has no power against coupling steps (R5) and a 5–30% false-failure rate; P4 is never supported and D is biased negative. Both demoted (Amendment 1).

## Results
**Headline.** In the three exploratory free → assigned pairs, the swarm's alignment with the assigned goal rose by 1.4–3.1 free-week SDs, far outside linear response. Who moved was not predicted by free-week fluctuations: r(Δᵢ, κ2ᵢ^F) = −0.37 and −0.69 in the two regime-I pairs (negative in 11 of 12 robustness variants) and +0.20 (sign unstable) in regime III. The variance along the goal grew 2–8× while transverse variance stayed put. A tilt of a bounded free-week landscape predicts the opposite at these pushes. Across 18 regime-I goal changes, the jump along the new goal *fell* with the pre-period fluctuation along it (Spearman −0.56, p = 0.015). By the pre-registered rule H10 **failed** (P1 failed; P2 untestable).

**What goals look like instead (descriptive, not pre-registered).**
1. **A new state, not a tilted old one.** The free-week distributions along the next goal are left-skewed with no on-goal tail. The assigned week populates content the free week never visited, with larger window-to-window swings along ĝ (agents switch between on-goal and off-goal windows). That is a quench into a basin that is absent from F(m), so no tilt of F can reach it. A two-state (on/off-goal) order parameter is the natural re-mapping (model 01/10 with occupancy p(t)): there, variance grows with the tilt while p < ½, as observed.
2. **A common target.** In #11 → #12a every agent ends near the same alignment (slope of Δᵢ on μᵢ^F = −1.41, cross-split). Across kickoffs, the jump also falls with the pre-period level. Goals act more like a constraint ("be here") than a soft field.
3. **Collective switching.** Along ĝ, mean pairwise signal correlation rose 0.20 → 0.64 and 0.17 → 0.40 in the regime-I assigned weeks: agents go on-goal together (debate rounds, shared deadlines). Window-level loop gains are 0.5–0.8 along ĝ and ≈ 0.74 along random directions. This is mostly common drive, and higher than the activity-based loop gains of H02/H05 (0.06–0.4). Compare with H01 P9 (period-level βJ₀) once it reports. This is a different estimator on a different timescale.
4. **Not a step response.** #12a still relaxes on days 2–4; #38a ramps for ten days. A static equilibrium tilt cannot describe either. The relaxation time is a separate observable, closer to H04's delayed context channel.

**Heterogeneity.** Regime I (N = 7, #general only) fails clearly; regime III (#37 → #38a, N = 12, two rooms, sparse statements, three-day free week) is inconclusive. Secondary N = 4 pairs split (#3 → #4a r = +0.82 at the only small push, ε = 0.53; #5 → #6a r = −0.63). The tilt might hold for small pushes; the village almost never delivers them (kickoff pushes have median ≈ 2.5 SDs).

**Caveats.**
- ĝ is a text-embedding proxy for the field direction. In the synthetic, a misaligned field (cos 0.5) weakens P1 but does not reverse its sign; a reversed sign needs a different mechanism.
- Statement-noise and style confounds are handled by within-agent differences and ANOVA noise removal. Topic switches inflate window variance in every direction, but the transverse control shows the growth is ĝ-specific.
- N = 7 agents in regime I. The negative-r p-values (Stouffer ≈ 0.03 for r < 0 over the regime-I pairs) are post hoc. The kickoff Spearman includes the #11 → #12 and #16 → #17 transitions, so it is not independent of P1.
- "Free" weeks are not field-free: the instruction and each agent's self-chosen project act as fields.
- **Amendment 1** was made after calibration and the synthetic, before any statistic along a goal direction. It restricted P2 to ε ≤ 0.34 (rule fixed in code beforehand; coverage-limited) and demoted P3/P4 to descriptive. Under the original rules the verdict would also be "failed" (P1 failed).
- #23 kept untouched; nothing along ĝ₃₂ computed.
- Embedding-model swap not done.

**Figures.** [`figures/summary.pdf`](figures/summary.pdf) (one-page summary), [`figures/synthetic.pdf`](figures/synthetic.pdf), [`figures/summary_obs.pdf`](figures/summary_obs.pdf) (the summary-page figure), per pair `goalperiod-subhypotheses/NE34/figures/pair_*.pdf`, kickoffs `goalperiod-subhypotheses/NE34/figures/kickoffs.pdf`, per period `goalperiod-subhypotheses/G*/figures/shape_and_drift.pdf`.

**Code.** `scheme/build.py` (statements, whitened vectors, goal and kickoff embeddings); `analysis/h10lib.py` (estimators, tilt, verdict rules), `h10data.py`, `calibrate.py`, `synthetic.py`, `run_pairs.py`, `periods.py`, `kickoffs.py`, `figures.py`, `report.py`, `confirm.py`.

## Confirmatory test (written 2026-10-03 after exploration; NOT run)
*What I had seen:* every exploratory result above. `analysis/confirm.py` refuses to run without `--confirm --i-understand-this-uses-the-locked-holdout`; `--dry-run` runs the identical pipeline on #16 → #17 and #11 → #12a and reproduces the exploratory numbers exactly.
- **Pairs.** C1: F = #22b (2025-12-10 … 12-12, after NE08 put the goal in the prompt, so it has the same scaffold as #23) → A = #23 days 2+ (12-16 … 12-19). C2: F = #31a (02-16 … 02-19) → A = #32 days 2+ (02-24 … 02-27). C2 spans 02-25 (rooms, which separated no pair per H05, and the NE35 format reset); variant A = 02-24 only.
- **CH10 (the hypothesis as stated):** r(Δᵢ, κ2ᵢ^F) > 0 in both pairs and Stouffer p < 0.05. Expected to fail (credence it passes: 0.1).
- **CX1 (the exploratory counter-finding):** Stouffer of the one-sided p for r < 0 is < 0.05 (credence 0.4; N ≈ 9–12 per pair).
- **CX2 (field-specific dispersal):** ln(var_A / var_F) along ĝ > ln 1.5 in both pairs and \|ρ⊥\| < ln 1.5 in both (credence 0.55).
- **CX3:** Δ̄ > 0 with 90% CI above 0 in both (credence 0.9).
- P2 gets a tilt verdict only if ε ≤ 0.34 (expected n/a).
- Reuse policy: #22 and #32 have not been used for confirmation by any hypothesis that I know of; if one has, the reuse rule in `holdout.md` applies (different statistic; disclose in both cards and `LOG.md`).

## Notes
- **Correction (coordinator, 2026-10-04):** #32 is not unused. H05's executed holdout run used it (holdout ledger item 4).
- 2026-10-03: promoted from shortlist 2 (HH49 + HH85 (shortlist 2, item 1)).
- 2026-10-03: predictions written (P1–P5, F1–F3, A1–A3) before any real-data statistic. Scheme built (180k non-holdout statements, 34 goal vectors; 27 MB data folder in total).
- 2026-10-03: calibration (random directions, non-test periods) and synthetic validation; Amendment 1 (P2 perturbative range, P3/P4 descriptive, P4 shrinkage) before any real-data statistic along a goal direction.
- 2026-10-03: exploratory round 1 run: **failed**. Confirmatory script written, dry-run checked, not run. Period folders moved to `goalperiod-subhypotheses/` (coordinator's request).
- Proposed for DEFINITIONS.md: "agent state (vector, statement-mean projection)", "goal field direction ĝ", "push size ε", "loop gain (window-level, along a direction)". Text is in the round-1 hand-back.
- 2026-10-04: round 1b (re-evaluation agent RE-C1): corrected inputs in 8 configurations, natives G44 / NE38 / G26 (predictions dated in the folders before running), per-period estimates; verdict unchanged (failed). Section "Round 1b" above.

## Round 1b (improved data, 2026-10-04)
*Re-evaluation wave (Vivian's priority 2), two-layer design (`infra/data-quality/QUEUE.md`). Replication: the round-1 estimators rerun unchanged on corrected inputs; native: three new period-specific tests (DQ9 cross-index), predictions dated in their folders before running. Holdout untouched: #23 still unused on either side, nothing along ĝ₃₂, `confirm.py` not run.*

**What changed.**
- **Goal vectors:** the shared goal fields (`infra/shared/goal_fields.py`, `embeddings/goals.parquet`). H10 built its own goal and kickoff vectors with the same rule; they match the shared ones to cos ≥ 0.9999999 in every period (`r1b/check.json`), so every bge number reproduces exactly (pairs, robustness, kickoffs, period descriptives). The H01 #38 room swap never touched H10 (its kickoff vector pools all rooms).
- **Second embedding model:** gte-modernbert (DQ5), whitened per regime in its own basis (64-d, nested), with its own goal vectors.
- **Dedupe (DQ5 `statement_flags`):** copies (`self_repeat_both`, 10.5% of H10's statements) and restatements (either model's flag, ~15%).
- **Style:** `statements_style_resid_period32` for both models, because P1 is a per-agent statistic and agent style enters μᵢ and κ2ᵢ.
- **Activity:** not used by H10 (no change from the `activity_bins` fix).
- Code: `scheme/build_r1b.py`; `analysis/h10data.py: configure()` (defaults reproduce round 1); `run_pairs.py`, `kickoffs.py`, `periods.py` take `--emb --goals --dedupe --style`; natives `analysis/natives_r1b.py`; `analysis/r1b_figures.py`, `analysis/r1b_estimates.py`.

**Replication, old vs new** (pairs #11 → #12a, #16 → #17, #37 → #38a):

| Statistic | Round 1 (bge) | 1b bge-small | 1b gte-modernbert | 1b deduped (bge / gte) | 1b style-resid (bge / gte) |
| --- | --- | --- | --- | --- | --- |
| P1 r | −0.37, −0.69, +0.20 | same | −0.53, −0.49, −0.09 | −0.32, −0.69, +0.15 / −0.56, −0.40, −0.16 | −0.66, −0.60, +0.33 / −0.05, −0.81, +0.26 |
| P1 combined | Stouffer 0.89, **failed** | 0.89, failed | 0.96, failed | 0.90 / 0.93, failed | 0.87 / 0.84, failed |
| push ε | 3.06, 1.42, 1.92 | same | 3.00, 2.03, 0.69 | 3.46, 1.43, 1.45 / 3.26, 1.41, 0.66 | 3.62, 1.78, 1.28 / 3.21, 2.38, 0.70 |
| ρ along ĝ (ρ⊥) | +2.04, +1.03, +0.66 (≈ −0.13) | same | +1.67, +1.26, +0.09 (−0.02 to −0.22) | +2.23, +0.87, +0.35 / +1.81, +1.14, +0.02 | +1.96, +0.78, +0.84 / +1.59, +0.94, −0.03 |
| convergence slope (#11 → #12a) | −1.41 | same | −1.25 | −1.33 / −1.16 | −1.51 / −0.97 |
| kickoffs: jump > 0 | 19/19 | 19/19 | 19/19 | 19/19 / 19/19 | 19/19 / 19/19 |
| kickoffs: Spearman (regime I) | −0.56 (p 0.015) | −0.56 | −0.59 (p 0.010) | −0.61 / −0.48 | −0.55 / −0.30 (p 0.23) |

- **Verdict: unchanged, failed.** P1 fails in every configuration, negative in both regime-I pairs throughout (regime-I robustness variants with r < 0: 11/12 bge, 10/12 gte).
- **Model-dependent:** (i) the #37 → #38a push is small in gte (ε 0.69 vs 1.92) and its would-be variance test passes there (ρ −0.18, not counted under Amendment 1), so the regime-III variance is tilt-compatible under gte while P1 still fails; (ii) the free-week shape and drift (#11 two-component and drifting under bge, single-well and stationary under gte); (iii) window-level loop gains along ĝ run lower in gte (free weeks 0.37–0.48 vs 0.51–0.62).
- **Robust:** field-specific dispersal in both regime-I pairs (ρ 0.8–2.2 along ĝ, transverse ≈ 0), the common-target convergence in #11 → #12a, a push at every change into an assigned goal, and the wrong-signed cross-transition fluctuation–response (except under gte + style).

**Native layer** (new in 1b; predictions in the folders, written before the runs):

| Native test | Design | bge-small | gte-modernbert | Verdict |
| --- | --- | --- | --- | --- |
| [G44](goalperiod-subhypotheses/G44/README.md) assigned vs self-chosen room | #42 → #44 days 2+, each room along its own room kickoff | #best Δ̄ +0.18 [+0.13, +0.24], ε 0.97; #rest −0.05; room difference +0.17 [+0.11, +0.23] | #best +0.24, ε 1.55; #rest +0.02; difference +0.17 [+0.11, +0.24] | mixed (bge misses ε > 1 by 0.03) |
| [NE38](goalperiod-subhypotheses/NE38/README.md) one agent's goal reassigned | Opus 5's window distribution along its new goal, before vs after; tilt check | ε 10.2; post mean 0.47 > every pre window (max 0.17): unreachable by any tilt | ε 20.3; unreachable | mixed (the incumbent control drifted −3.1 / −1.0 SD) |
| [G26](goalperiod-subhypotheses/G26/README.md) agent-set goal | #25 → #26 along the elected leader's announcement | ε 1.06; P1 r −0.14 | ε 0.93; r −0.63 | failed |

- **What the natives add.** A single agent's goal change is the cleanest Legendre test in the record, and it fails in the strongest way: the post-change content lies outside the support of the pre-change distribution, so P_A ∝ P_F e^{λy} cannot hold for any λ. An agent-written goal does act as a field over days (≈ 1 SD, similar to the operator's election kickoff), but who moves is again not ordered by unforced fluctuations. #44 shows the field is room-specific and needs an operator-written target: the room told to pick its own goal shows no push along its instruction.
- **Not reproduced:** the round-1 dispersal signature in #44's assigned room (its variance along ĝ fell at ε ≈ 1).

**Scorecard after 1b** (changes only): A stays 1 (embedding-model swap and style residualization done and P1 robust to both, but invariance across families is not established); E stays 0 (NE38 is a natural experiment the tilt fails, not a partial pass); G stays 1 (#44: the field follows the assigned room, an instrument-level check). Other axes unchanged. Ratings: complete 40 → 50 (round 1b with both models and three natives), faithfulness 1.0 (unchanged), usefulness 1.5 (unchanged).

**Per-period estimates:** 36 rows written with `write_estimates` (`loop_gain_g_along_goal`, `goal_alignment_mean`, `fluct_kappa2_along_goal` for the six pair segments, channels `content_bge_small` and `content_gte_modernbert`, role replication). The pair, kickoff and native statistics span two segments, which the per-period schema excludes.

## Round 2 redirects (2026-10-04)
*From the round-1 reflection (`writeup/round1-reflection/round1-reflection.pdf`).*
- **Where round 1 went sideways:** A small-push, linear-response picture was tested on continuous alignment, but goals are large quenches.
- **What the direction is really after:** How does a new goal propagate: as a field acting on everyone at once, or as contagion from early adopters?
- **H10-R1.** Adoption onsets after a kickoff: a field predicts simultaneous onsets; contagion predicts onsets ordered by exposure to early adopters.
- **H10-R2.** Goals act on a two-state on-goal/off-goal occupancy (HH130).
- **H10-R3.** During the week, goal-specific content relaxes back toward family-prior directions (E4).
