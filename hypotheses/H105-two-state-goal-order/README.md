# H105: Goals act on a two-state order parameter

**Status:** **exploratory round 1 done (2026-10-04): inconclusive by design. The two-state picture describes the data, but the tilt test it was meant to enable is not identifiable at village sampling.**
- **Synthetic first (Amendment 1):** with a true tilt, the variance test (P1) passes in 30% of pairs and fails in 43%; under a coupling change (R5) it passes in 40%. The free week's coupling cannot be measured at p_F ≈ 0.03 with 24–30 windows, and statement misclassification dilutes the measured loop gain. P1 and P3 were demoted to descriptive before real data; P2 got a calibrated rule.
- **Descriptive (robust):** on-goal occupancy rises from the decoy floor (0.02–0.05) in free weeks to 0.23–0.44 in assigned weeks (always < ½); its variance grows ×2–40 while transverse occupancy stays at the floor (P4 supported). Across 16 kickoffs, observed variance growth follows the two-state p(1 − p) prediction (Spearman 0.86, p 0.0003), but only 7/16 fall within ×1.5 (P6 part 1 failed).
- **P2 (who moves) inconclusive in 3/3 pairs** (calibrated); #12a's slope is negative (common target, as H10).
- **Collective switching** in #12a: g₂ 0.10 → 0.74 in both models; under gte half of the excess variance is the DQ6 debate schedule (native G12).
- **Natives:** G51 mixed (private goals: own-goal g₂ ≈ 0 under bge, +0.19 under gte); NE38 mixed (one-spin quench 0 → 0.96; no transfer to others under bge, +0.05 under gte).
- Card and predictions ~20:27 UTC before any real-data statistic; Amendment 1 ~20:51 UTC after the synthetic. `analysis/confirm.py` frozen and dry-run; **not run**.
**Question (GOALS.md):** **Q2** (field vs coupling: is the goal a field on a binary on-goal spin, and does it leave the coupling unchanged?). Second: **Q5** (forecasting steerability from unforced fluctuations, H10's question in the right variables).
**Fields:** stat mech, info theory
**Literature:** none new; builds on H10 (continuous Legendre test, failed) and H54, H75 (cards linked below).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Population N(t); Regime (decoy thresholds and whitening per regime); Driving / external field (goal text + kickoff as a field on the on-goal spin); Agent state, variant *categorical* (q = 2: on-goal / off-goal per agent-window, defined below); H10's goal field direction ĝ (proposed by H10). New named variants proposed for DEFINITIONS.md (not edited there; defined under Observables): **on-goal statement (decoy-threshold)**, **agent-window goal spin σ_i,t**, **goal occupancy p(t)**, **two-state loop gain g₂ and coupling J₂**, **tilt variance ratio ρ_V**.
**From:** HH130 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/01-inverse-ising/` (primary: mean-field Curie–Weiss with heterogeneous fields), `physics-models/11-vector-spins/` (the continuous version H10 refuted; rival)

## Source HH (verbatim from the HH list, including refinements)
Goals act on a two-state order parameter (on-goal vs off-goal), not a continuous alignment. H10 found goals are quenches: variance along ĝ grows while transverse variance is flat, and agents switch on-goal together. For the occupancy p(t) of on-goal statements, a Legendre tilt *does* predict variance growth while p < ½. That gives the free-energy idea a fair second test in the right variables. *Check:* classify statements on-goal or off-goal; fit a two-state (Ising-like) mean field to p(t) through kickoffs; predict the variance trajectory from free-week fluctuations of p.
  *Models:* 01, 10 · *Periods:* free → assigned pairs (#11→#12, #16→#17, #37→#38); kickoffs (NE34)

## Standards (2026-10-04)
**Question served:** Q2 and Q5.

| Impostor | Relevant? | How it is handled | Status |
| --- | --- | --- | --- |
| Scheduler field | partly | Occupancy is a per-window fraction over present agents, with composition-adjusted deviations (each window's expected occupancy from its present agents is subtracted). Activity bursts change N_t, not p_t; windows need N_t ≥ max(3, half the segment's agents). A within-day variant removes day means. | partly |
| Exogenous field (kickoff/goal/operator) | yes | The goal field is the object. A time-varying drive inside the week (debate rounds, deadlines) inflates the variance as coupling would; native G12 regresses the DQ6 debate-phase schedule out; the within-day variant removes slow drives. Transverse directions are the field-free control. | partly |
| Shared model priors | yes | Agent heterogeneity is modelled as agent fields h_i; the P2 slope is within-agent (logit shift). Style variant: `statements_style_resid_period32`. | removed (by the variant) |
| Contemporaneous convergence | partly | J₂ is an equal-time loop gain; it does not separate copying from a common drive or simultaneous response. No influence claim is made; NE38's one-agent field tests transfer to others. | open |

**Inputs:** shared `goal_fields` (goal and kickoff vectors, both models), DQ5 statements in bge-small and gte-modernbert (`statements_white32_*`, `statements_style_resid_period32_*`), `statement_flags` (dedupe), `period_units`, `ground_truth_labels` (#12 phases, #51 roles), DQ4 `work_commits` + `work_repos` with H54's goal-naming tags (`projects.parquet`, read-only) for the on-goal work variant. No activity table.

**Two layers:** replication on the free → assigned pairs and every eligible kickoff transition (role `replication`); natives G51, G12, NE38 (role `native`).

**Confirm script:** `analysis/confirm.py`, frozen and guarded, not run.

## Question
If the goal is treated as a field on a binary spin (each agent-window is on-goal or off-goal), does an exponential tilt of the free week's two-state statistics predict the assigned week's variance of on-goal occupancy, and who moves, with one fitted field and an unchanged coupling?

**Practical payoff:** if the tilt works in two-state variables, a free week's on/off fluctuations forecast how strongly and how synchronously a swarm will take up an assigned goal.

## Model
**From:** `physics-models/01-inverse-ising` (mean-field forward version: Curie–Weiss with heterogeneous fields), in 0/1 spins.

**H105 variant: heterogeneous Curie–Weiss on goal spins.** σ_i,t ∈ {0, 1} (agent i on-goal in 30-min window t). With n_t = Σ_i σ_i,t over the N_t present agents,

P(σ) ∝ exp( Σ_i h_i σ_i + (J₂ / 2N_t) n_t² ).

- Agent fields h_i set each agent's on-goal rate p_i; J₂ is the coupling.
- In the paramagnetic phase (random-phase approximation), Var(n_t) = S_t / (1 − J₂ q̄_t), with S_t = Σ_i p_i(1 − p_i) and q̄_t = S_t / N_t. The two-state loop gain is g₂ = J₂ q̄. Criticality is at g₂ = 1 (q̄ ≤ ¼, so J₂c ≥ 4).
- **The tilt (the Legendre push):** the goal adds λ to every h_i and changes nothing else. Then logit p_i^A = logit p_i^F + λ_eff (uniform logit shift; the coupling's mean-field term is common to all agents), and J₂ is unchanged.
- **Variance prediction (unfitted):** with λ fitted to the assigned week's mean occupancy, V_A^pred = mean_t S_t^pred / (N_t² (1 − J₂^F q̄_t^pred)). It grows with p while p < ½ through both p(1 − p) and the loop gain. If J₂^F q̄^pred ≥ 1, the tilt predicts a bistable, synchronized occupancy (capped at the full-synchrony variance p̄(1 − p̄); flagged).

**Rivals:**
- **R0 continuous Legendre (H10):** the variance along ĝ follows a tilt of the continuous alignment (already refuted by H10; not re-tested).
- **R2 common target (H10's R2):** every agent ends at the same on-goal rate: the slope of logit p_i^A on logit p_i^F is 0, not 1.
- **R5 coupling change (collective switching):** the goal raises J₂ (agents go on-goal together): V_A ≫ V_A^pred, J₂^A > J₂^F.
- **R5′ scheduled drive:** a time-varying exogenous field inside the assigned week (debate rounds, deadlines) inflates V_A like coupling; removing the schedule (G12) or day means removes it.
- **R3 confinement:** V_A < V_A^pred (agents locked on-goal).
- **R6 agent-specific receptivity:** logit shifts vary across agents beyond noise, uncorrelated with logit p_i^F.

## Data scheme (`scheme/`)
`scheme/build.py` builds `data/processed/H105-two-state-goal-order/` from shared tables only. No text is read.
- **Inputs:** `embeddings/statements.parquet` + `statements_white32_*` and `statements_style_resid_period32_*` (both models), `statement_flags.parquet`, `embeddings/goals.parquet` + `goal_vectors*.npy` + whiteners, `period_units`, `ground_truth_labels`, `work_commits`, `work_repos`; H54 `projects.parquet` (read-only).
- **Transform:** every statement passes `common.holdout_mask`; the Claude Code agent (19) is excluded; #23 is excluded (H10's confirmatory pair). Goal direction ĝ_A = unit(unit(W·goal_A) + unit(W·kickoff_A)) in the regime basis of each model (H10's construction from shared vectors). For each design the scheme stores the statement rows, the segment (F / A), the agent, the window (`win30`) and the projection y = ⟨z, ĝ_A⟩, plus y along 50 fixed random unit directions ⊥ ĝ_A, and the decoy thresholds.
- **Decoy threshold:** θ(ĝ) = 95th percentile of ⟨z, ĝ⟩ over decoy statements: all non-holdout statements of the same regime outside goal periods {A − 1, A, A + 1} and #23 (10,000-statement random subsample, seed fixed). A statement is on-goal if y > θ. Variants at the 90th and 98th percentiles.
- **Designs:** (i) free → assigned pairs #11 → #12a, #16 → #17, #37 → #38a (F = all active days of the free week; A = the first `period_units` unit of the assigned week, days 2+); secondary #3 → #4a and #5 → #6a (N = 4). (ii) Kickoff transitions: every non-holdout p with non-holdout p − 1 in the same regime; F = the last ≤ 5 active days of p − 1, A = the first unit of p, days 2+ (≥ 2 days). (iii) Natives (below).
- **Output:** `designs.parquet`, `stmt_<design>.parquet` (codes and projections only), `thresholds.parquet`, per-design results in `G<NN>/`, `NE34/`, `natives/`, `synthetic/`, and `_provenance.json`.
- **Regimes covered:** I, II, III (no design crosses a regime boundary).

## Observables
*Specified 2026-10-04, before any real-data statistic along a goal direction.*
- **On-goal statement:** b_k = 1[⟨z_k, ĝ⟩ > θ(ĝ)].
- **Agent-window goal spin:** σ_i,t = 1 if at least half of agent i's statements in window t are on-goal; eligible if n_i,t ≥ 2. (Statement-level occupancy is a variant.)
- **Agents:** those with ≥ 6 eligible windows in both F and A (H10's rule). **Windows:** N_t ≥ max(3, ⌈half the segment's agents⌉).
- **Occupancy** p_t = N_t⁻¹ Σ_i σ_i,t. Agent rate p_i = mean_t σ_i,t in the segment. Expected occupancy μ_t = N_t⁻¹ Σ_{i∈t} p_i.
- **Variance** V = mean_t (p_t − μ_t)² (composition-adjusted). **Independent baseline** V_ind = mean_t N_t⁻² Σ_{i∈t} p_i(1 − p_i). **Ratio** R = V / V_ind; **loop gain** g₂ = 1 − 1/R; **coupling** J₂ = g₂ / mean_t q̄_t.
- **The tilt fit:** p_i^F smoothed as (k + ½)/(n + 1). λ solves mean_t μ_t^pred(λ) = p̄_A^obs, with p_i^pred = σ(logit p_i^F + λ). **Predicted variance** V_A^pred from J₂^F and p_i^pred on A's window structure. **Tilt variance ratio** ρ_V = ln(V_A^obs / V_A^pred). Also ρ_V′ using the observed p_i^A (isolates the coupling part).
- **Who moves (P2):** statement-level agent rates f_i (smoothed) in F and A. Slope s of logit f_i^A on logit f_i^F by split-window IV: s = cov(L_i^A, L_i^{F,odd}) / cov(L_i^{F,even}, L_i^{F,odd}). Tilt: s = 1. Common target: s = 0.
- **Coupling change (P3):** ΔJ₂ = J₂^A − J₂^F; Δg₂.
- **Transverse control (P4):** the same pipeline along the 50 random directions ⊥ ĝ with their own decoy thresholds: p̄⊥, ρ_V⊥.
- **Trajectory (P5):** day-level V_d against V_d^pred within A.
- **On-goal work (variant, regime III, DQ4):** σ^work_i,t = 1 if agent i commits in window t to a repo whose artifacts H54 tags as named by the goal or kickoff (`projects.named`); occupancy and g₂ in A only (free weeks have no goal repo, so the tilt is not defined there). Descriptive.
- **CIs:** moving-block bootstrap over windows within days (block = 4 windows, 1,000 draws), and an agent bootstrap for P2. Coverage is calibrated in the synthetic.

## Null / baseline
- **N0 transverse directions** (no goal pushes them): ρ_V⊥, p̄⊥.
- **N1 independent agents** (J₂ = 0): R = 1.
- **N2 synthetic truths** (axis F): heterogeneous Curie–Weiss Glauber dynamics on the real F and A window structure, observed through statements with the real n_i,t and a two-state emission (on: P(b = 1) = q₁; off: q₀ = 0.05), under H (tilt), R2, R5, R5′ (scheduled drive), R6. Same pipeline.
- **Known confounds:** the threshold makes "on-goal" a text-embedding proxy; free weeks are not field-free (each agent's own project is a field); statement counts per window differ between F and A (misclassification of σ changes with n); the kickoff transitions' F is the previous goal's tail, which carries its own field.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R0 continuous Legendre (H10); R2 common target; R5 coupling change; R5′ scheduled drive; R3 confinement; R6 agent-specific receptivity.
**Locked holdout used for confirmation:** none yet. Planned: held-out kickoffs #9, #14, #15, #28, #29, #34, #43, #45–#50 and the #51 tail (`analysis/confirm.py`, frozen, not run).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Spins from DQ5 statements and shared goal vectors with a decoy threshold; both models; style and threshold variants. Model-dependent signs in #12a and the natives. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 0 | The agent-window spin is a noisy measurement (2–4 statements); free weeks are not field-free; within-week drives (debate rounds) are not stationary. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Transverse null passed; variance growth follows p(1 − p) across 16 kickoffs; the tilt itself cannot be tested against R5. |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | The unfitted variance prediction is not identifiable (synthetic); P2 inconclusive. |
| E interventional | predicts the change across a natural experiment | 1 | NE38: one-spin quench 0 → 0.96 in both models; transfer to others model-dependent. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 | Synthetic at the real window structure showed P1/P3 not identifiable and P2 biased before real data (Amendment 1); a matched parametric bootstrap calibrates every pair. |
| G ground truth | agrees with known structure | 1 | DQ6 debate phases track #12a's occupancy; #51 private roles give steady own-goal occupancy. |
| H comparative | beats the named rivals | 0 | R5 and R5′ are not separable from the tilt with these data. |
| I transfer | holds in other same-mode periods, including the holdout | 1 | The descriptive two-state scaling holds across 16 kickoffs in regimes I and III; holdout not run. |

## Prediction
*Written 2026-10-04 ~20:27 UTC, before running the analysis on real data.*

**What I had seen when writing this:** H10's card in full (continuous alignment: push ε 1.4–3.1 SDs; variance along ĝ ×1.9–7.7 with transverse flat; P1 r < 0 in both regime-I pairs; common-target slope −1.41 in #11 → #12a; pairwise signal correlation along ĝ 0.20 → 0.64 and 0.17 → 0.40; window loop gains 0.5–0.8 along ĝ and ≈ 0.74 along random directions; #38a ramps for ten days), H54 (day-1 target, remanence plateau 0.11), H75 (named targets settle within 0.5 h). Counts only for H105 (H10's published per-pair agent and window counts). No on-goal classification, threshold or occupancy statistic computed.

**Primary predictions** (three exploratory pairs; per pair, then combined by majority or Stouffer, never by pooling fits):

| ID | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| **P1** tilt predicts the variance | Per pair: 90% block-bootstrap CI of ρ_V contains 0 and \|ρ̂_V\| < ln 1.5 (supported); CI excludes 0 and \|ρ̂_V\| ≥ ln 1.5 (failed); else inconclusive. Combined: supported in ≥ 2/3 testable pairs and failed in none. Descriptively, V_A > V_F wherever p̄_A < ½ | failed in ≥ 2/3 pairs in one direction (ρ_V > 0: R5/R5′; ρ_V < 0: R3) | supported 0.3; fails toward R5/R5′ 0.45 |
| **P2** uniform logit shift (who moves) | IV slope s of logit f_i^A on logit f_i^F: 90% agent-bootstrap CI contains 1 and excludes 0 in ≥ 2/3 pairs | s CI excludes 1 with s < 0.5 in ≥ 2/3 pairs (R2) | 0.25 |

**Secondary:**

| ID | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| P3 | Coupling unchanged: Δg₂ 90% CI contains 0 in ≥ 2/3 pairs | Δg₂ > 0 with CI above 0 in ≥ 2/3 (R5) | 0.3 |
| P4 | Transverse control: p̄⊥ within 0.03 of the decoy rate in F and A, and \|ρ_V⊥\| < ln 1.5 | transverse occupancy or variance moves like the goal's | 0.7 |
| P5 | Trajectory: within A, Spearman(V_d, V_d^pred) > 0 pooled over the pairs' days | ≤ 0 | 0.4 |
| P6 | Kickoff replication: ρ_V within ±ln 1.5 in ≥ half of the eligible transitions; Spearman(observed variance growth ln(V_A/V_F), predicted growth) > 0 across transitions | < ⅓ inside; Spearman ≤ 0 | 0.35 / 0.55 |
| P7 | Within-day variant (day means removed) moves ρ_V toward 0 by ≥ ln 1.2 in the pairs where P1 fails toward R5 | no change | 0.4 |
| W | On-goal work (regime III, descriptive): g₂ on work spins in A is lower than g₂ on content spins | — | — |

**Native predictions** (each also in its folder README):

| ID | Unit | Prediction | Counts against | Credence |
| --- | --- | --- | --- | --- |
| N1 | G51 (private goals, head 51a–51l) | Own-goal occupancy (each agent's spin along its own `agent_goal`, own decoy threshold) shows no collective switching: R_own 90% CI contains 1 (g₂ < 0.2) and g₂,own < g₂ along the shared #51 kickoff | g₂,own ≥ 0.3 with CI above 0 | 0.55 |
| N2 | G12 (#12a, debate phases, DQ6) | The debate-phase schedule is a scheduled field: regressing p_t on each window's debate-phase share removes ≥ 30% of the excess variance V_A − V_A^pred | < 10% removed | 0.4 |
| N3 | NE38 (#51, 07-29) | A field on one spin does not transfer: the other agents' occupancy along Opus 5's new goal changes by less than 0.02 (DiD against the other agents' own-goal directions, before vs after), while Opus 5's own occupancy rises by > 0.3 | others' change > 0.03 with CI excluding 0 | 0.65 |

**Amendment 1** (2026-10-04 ~20:51 UTC, after the synthetic run, before any real-data statistic along a goal direction). Synthetic: `analysis/synthetic.py`, 30 replicates × 6 scenarios at the real window structure of the three primary pairs (`synthetic/results.json`). Latent heterogeneous Curie–Weiss spins (Glauber, partial updates), observed through statements with emission q₁ = 0.6 (on) and q₀ = 0.05 (off), then the majority rule, as in the real pipeline.
1. **P1 is not identifiable at village sampling.** Under the true tilt (H) P1 is supported in 30% of pairs and fails in 43%; under the coupling rival R5 (J ×2.5) it is supported in 40%. The ρ_V distributions of H (10–90%: −1.35 to +0.98) and R5 (−0.88 to +0.81) overlap almost entirely. Two causes: J₂^F is unidentifiable at p_F ≈ 0.1 with 24–30 windows, and statement misclassification dilutes the measured loop gain more at low p than at high p. **P1 is demoted to descriptive.** It is still computed, and reported against a matched parametric bootstrap (`analysis/calibrated.py`: latent base rate and J matched to the real p_F and g_F, tilt matched to the real p_A; 200 simulations under H and under R5).
2. **P3 (Δg₂) is not identifiable either** (passes in 54% under H and in 59% under R5). It is demoted to descriptive.
3. **P2 is biased but discriminating.** Under H the slope s has median 0.31 (not 1: misclassification compresses logits); under R2 the median is 0.06, under R5 0.02. The pre-registered rule (CI containing 1) is kept and reported. **The verdict uses a calibrated rule:** P2 is supported if the real s lies inside the matched H band (5–95%) and above the matched R2 band (> 95th percentile); failed if s lies below H's 5th percentile and inside R2's band; inconclusive otherwise.
4. **Overall rule, restated:** P1 untestable ⇒ the card's rule gives at most **mixed**. **Failed** if the calibrated P2 fails in ≥ 2/3 pairs; **mixed** if it is supported in ≥ 2/3; **inconclusive** otherwise.
5. Not run: the statement-level occupancy variant (the agent-window spin is the pre-registered unit; the synthetic shows the measurement layer, not the unit, is the problem).

**Overall verdict rule (original):** **supported** if P1 is supported and P2 does not fail; **failed** if P1 fails in ≥ 2/3 testable pairs in the same direction; **mixed** otherwise (including P1 untestable). Per-transition replication rule (templated): supported if the ρ_V CI contains 0 and |ρ̂_V| < ln 1.5; failed if the CI excludes 0 and |ρ̂_V| ≥ ln 1.5; mixed otherwise.

## Results by goal period
After Amendment 1 the replication folders are descriptive; each reports the templated P1 rule outcome. bge-small.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [NE34](goalperiod-subhypotheses/NE34/README.md) (pairs + 16 kickoffs) | replication (cross-kickoff) | mixed | P1/P3 not identifiable; P2 inconclusive 3/3; P4 transverse flat; P6 Spearman(growth) 0.86 (p 0.0003), 7/16 within ×1.5 |
| [G04](goalperiod-subhypotheses/G04/README.md) (#3 → #4a) | replication | descriptive | p 0.02 → 0.10; ρ_V +0.89; N 4 |
| [G06](goalperiod-subhypotheses/G06/README.md) (#5 → #6a) | replication | descriptive | p 0.03 → 0.51; ρ_V +1.06; N 4 |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | descriptive | p 0.03 → 0.24; ρ_V −0.19 (inconclusive) |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | descriptive | p 0.27 → 0.04 (into a free week); ρ_V −0.27 |
| [G12](goalperiod-subhypotheses/G12/README.md) (#11 → #12a) | native (+ primary pair) | mixed | p 0.02 → 0.44; g₂ 0.10 → 0.74; ρ_V −0.71 (bge) / +1.28 (gte); s −0.60; debate schedule removes 50% of excess (gte), no excess (bge) |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | descriptive | p 0.00 → 0.14; ρ_V +0.11 (supported by rule) |
| [G17](goalperiod-subhypotheses/G17/README.md) (#16 → #17) | replication | descriptive | p 0.03 → 0.27; g₂ −0.04 → 0.22; ρ_V +0.53 [0.21, 0.92]; s +0.38 |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | descriptive | p 0.00 → 0.05; ρ_V +0.27 |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | descriptive | p 0.10 → 0.29; g₂ A 0.66; ρ_V +0.42 |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | descriptive | p 0.01 → 0.43; g₂ A 0.71; ρ_V −1.08 |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | descriptive | p 0.00 → 0.13; g₂ A 0.77; ρ_V +1.48 |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | descriptive | p 0.00 → 0.82 (crosses ½); ρ_V +0.37 |
| [G38](goalperiod-subhypotheses/G38/README.md) (#37 → #38a) | replication | descriptive | p 0.05 → 0.23; g₂ 0.22 → 0.24; ρ_V −2.45 (tilt predicts a critical, synchronized occupancy; none seen) |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | descriptive | p 0.01 → 0.21; ρ_V −0.41 |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | descriptive | p 0.40 → 0.64; ρ_V −0.01 (supported by rule) |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | descriptive | p 0.06 → 0.04; ρ_V +0.17 (supported by rule) |
| [G51](goalperiod-subhypotheses/G51/README.md) | native | mixed | own-goal p ≈ 0.27 steady; median g₂,own −0.08 (bge) / +0.19 (gte); shared-direction p ≈ 0.02 |
| [NE38](goalperiod-subhypotheses/NE38/README.md) | native | mixed | Opus 5 0.00 → 0.96; others' DiD +0.01 [−0.01, +0.03] (bge) / +0.05 [+0.04, +0.07] (gte) |

## Results
**Headline.** Read as a two-state system, a goal kickoff moves the on-goal occupancy from the decoy floor (≈ 0.03) to 0.2–0.45 and grows its variance as p(1 − p) predicts, with no change transverse to the goal. That much of HH130 holds. The quantitative tilt test it promised is not identifiable with 24–56 windows and 4–12 agents: the free week contains too few on-goal windows to measure the coupling. Round 1 is therefore inconclusive on the Legendre question.

**Outcome vs prediction**

| Prediction | Credence | Outcome | Verdict |
| --- | --- | --- | --- |
| P1 tilt predicts V_A (per pair) | 0.3 (fail toward R5: 0.45) | ρ_V −0.71 / +0.53 / −2.45 (bge); signs flip in gte for #12a; calibrated quantiles in H 0.25 / 0.57 / 0.00 | not identifiable (Amendment 1); #38a far below the tilt |
| P2 uniform logit shift | 0.25 | s −0.60 / +0.38 / +2.53; calibrated: inconclusive 3/3 | inconclusive |
| P3 coupling unchanged | 0.3 | Δg₂ +0.64 / +0.26 / +0.03; #12a's rise sits at the 0.92 quantile of H | not identifiable |
| P4 transverse control | 0.7 | p⊥ ≈ 0.02 in F and A; ρ_V⊥ median −0.07 to +0.04 | supported |
| P5 trajectory | 0.4 | per-day ratios scatter (#17 above, #12a and #38a below) | failed |
| P6 kickoffs (½ inside; Spearman > 0) | 0.35 / 0.55 | 7/16 inside; Spearman 0.86 (p 0.0003) | failed / supported |
| P7 day-mean removal moves ρ_V toward 0 | 0.4 | moves it away (#12a −0.71 → +3.17) | failed |
| N1 G51 private fields, no collective switching | 0.55 | bge yes (−0.08 < shared +0.13); gte no (+0.19 > +0.03) | mixed |
| N2 G12 debate schedule removes ≥ 30% of excess | 0.4 | gte 50%; bge has no excess | mixed |
| N3 NE38 no transfer to others | 0.65 | bge +0.01 (yes); gte +0.05 (no) | mixed |
| **Overall (Amendment 1 rule)** | | calibrated P2 inconclusive in 3/3 | **inconclusive** |

**What the data say, descriptively.**
1. **Two states fit the field's footprint.** Free weeks sit at the decoy floor along the next goal; assigned weeks occupy 0.2–0.45 (0.82 in #27, the only crossing of ½). The goal moves only the goal coordinate (transverse floor unchanged), as H10 found in continuous variables.
2. **Variance grows as p(1 − p).** Across 16 kickoffs, the log variance growth tracks the two-state prediction (ρ_s 0.86); this follows from any binary occupancy and does not test the tilt.
3. **Collective switching is real in #12a and mostly scheduled.** g₂ jumps to 0.74 in both models; the DQ6 debate phases explain the occupancy rise (+0.9 per unit phase share).
4. **#38a is confined, not critical.** The free week's apparent coupling (g₂ 0.22 at p 0.045) implies a near-critical, synchronized assigned week; the observed variance is ×10 lower. Read as: the free-week g₂ is drive, not coupling.
5. **Private goals do not synchronize** (bge): own-goal occupancy holds at ≈ 0.27 for nine weeks with g₂ ≈ 0, except the role-onset unit 51a.

**Caveats.** Thresholds are text-embedding proxies (95th decoy percentile); the 90/98% variants move p but not the conclusions. Agent-window spins with 2–4 statements are misclassified often (the reason for non-identifiability). bge and gte disagree on the sign of ρ_V in #12a and on both natives' second clauses. The on-goal work variant (DQ4 commits to goal-named repos) was not run.

**Code.** `scheme/build.py`; `analysis/h105lib.py`, `synthetic.py`, `calibrated.py`, `run.py`, `natives.py`, `figures.py`, `period_folders.py`, `write_rows.py`, `confirm.py` (not run). **Data:** `data/processed/H105-two-state-goal-order/` (≈ 75 MB, mostly #51 projections). **Figures:** `figures/summary_obs.pdf`, `figures/synthetic_compact.pdf`.

**Per-period estimates:** 88 rows (`goal_occupancy_assigned`, `two_state_loop_gain_assigned`, `tilt_variance_log_ratio`, `logit_shift_slope`; natives `two_state_loop_gain_own_goal` per #51 unit, `ne38_others_occupancy_did`).

## Confirmatory test (written 2026-10-04 after exploration; NOT run)
`analysis/confirm.py` (guard: both flags, clean git state, ledger check). `--dry-run` on stand-ins (#12, #17, #21, #25, #39–#41; unit 51g) reproduces the exploratory numbers (51g g₂,own −0.155). Frozen predictions (only measurable quantities, after Amendment 1):
- **C1:** across held-out kickoff transitions (#9, #14, #15, #28, #29, #34, #43, #45–#50 where eligible), Spearman(observed, tilt-predicted variance growth) > 0, p < 0.05 (credence 0.8).
- **C2:** transverse occupancy flat (|Δp⊥| ≤ 0.03) in ≥ 2/3 (credence 0.85).
- **C3:** #51 tail (51m): own-goal g₂ < 0.2, bge (credence 0.6).
- Excluded: #22/#23 and #32 (H10). Reuse: H54 (same kickoffs, different statistic); H22/H98 (#51-tail content). Disclose when run.

## Round 2 redirects (2026-10-04)
- **H105-R1. Fix the instrument, not the model.** Use an LLM on-goal classifier (Jev) or a calibrated statement classifier with a measured confusion matrix, then deconvolve misclassification; re-run the synthetic to show identifiability before any tilt test.
- **H105-R2. Pool the free-week coupling hierarchically** (exception (d)) across the free weeks of one regime to measure J₂ at all, then predict each assigned week.
- **H105-R3. Separate drive from coupling in #12** with the DQ6 debate schedule as an explicit time-dependent field and a read-out (ledger) lag test for the residual.

## Notes
- 2026-10-04: promoted from HH130 (Vivian). Card and predictions written before any real-data statistic.
- #23 is excluded although it is not in `holdout.json` (H10's confirmatory pair #22 → #23 must stay blind).
- 2026-10-04: synthetic → Amendment 1 → replication (5 pairs × 8 configurations, 16 kickoffs) → calibrated bootstrap → natives → estimates → confirm.py frozen and dry-run.
- Proposed DEFINITIONS.md variants (H105): **on-goal statement (decoy threshold)** = projection on ĝ above the 95th percentile of same-regime decoy statements outside goals A−1…A+1; **agent-window goal spin σ_i,t** = majority of the agent's ≥ 2 statements in a 30-min window on-goal; **goal occupancy p(t)** = mean σ over present agents; **two-state loop gain g₂** = 1 − V_ind/V of the composition-adjusted occupancy; **tilt variance ratio ρ_V** = ln(V_A observed / V_A predicted by a uniform logit tilt of the free week with its J₂).
