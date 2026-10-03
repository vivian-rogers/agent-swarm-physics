# H02: Inferred couplings reflect real influence

**Status:** running (exploratory round 1). Confirmation on #45 is written but not run.
**Fields:** stat mech, dynamics, info theory
**Literature:** [Aguilera, Ito & Kolchinsky 2026](../../literature/aguilera-2026-entropy-production-nonequilibrium-maxent.md) (directed couplings from lagged statistics). Kinetic-Ising inference by per-spin logistic regression (Roudi & Hertz 2011) and equilibrium pseudolikelihood (Aurell & Ekeberg 2012) are cited in the model folders.
**Definitions used:** Agent; Population, N(t) (variant: *present population*, below); Regime; Driving / external field; Interaction (broadcast). Spin = "active" (below).
**Shortlist entry:** S1 (`hypotheses/promotion-shortlist.md`).

## Question
When we fit Ising couplings to the village's binned activity, do they measure who influences whom? Or are they artifacts of the schedule, the scheduler, shared model family and finite data?

Concretely:
- (a) Can the pipeline recover planted couplings and a planted leader from data sampled like the village?
- (b) Do individual-objective (mode I) weeks couple less than shared-objective (mode C) weeks, once the strongest nulls are applied?
- (c) Does the known leader (#45, held out) come out as the top influencer?

## Model
**From:** `physics-models/02-nonequilibrium-ising/` (primary) and `physics-models/01-inverse-ising/` (rival / equal-time view).

- **Spin.** s_i(t) = +1 if agent i is *active* in 1-min bin t (`activity_bins.state ≥ 3`: act or talk), else −1.
- **KI-1, kinetic Ising (primary).** Parallel update, lag one bin:
  P(s_i(t+1) = +1 | s(t)) = σ(2 H_i), with H_i = h_i + δ_i(b(t+1)) + J_ii s_i(t) + Σ_{j≠i} J_ij s_j(t).
  - J_ij is the influence of j (at t) on i (at t+1).
  - δ_i(b) is a per-agent field for each (day, 30-min block): the **block field**, which absorbs the schedule, kickoffs and rate drift.
  - Fit per agent by L2-regularized logistic regression: λ = 1 on all J (including J_ii) and on the δ_i(b); h_i unpenalized; logistic-coefficient units, i.e. on 2J.
  - Transitions never cross days.
- **KI-1-naive.** Same, without block fields (constant h_i). Used to show what the common drive does.
- **KI-5 (secondary, delayed influence).** The cross covariates are 5-min boxcar means of s_j over bins t−4…t (median exposure lag is 248 s, `exposure`). Self terms are s_i(t) and its boxcar.
- **EQ-PL (rival, equilibrium).** Pseudolikelihood: logit P(s_i(t) = +1 | s_{−i}(t)) = 2(h_i + δ_i(b) + Σ_j J_ij s_j(t)), with the same λ. Symmetrized J^eq_ij = (J_ij + J_ji)/2. Equal-time only, so it has no direction.
- **Net outgoing influence** of agent k: I_k = Σ_{j≠k} (J_jk − J_kj), from the kinetic fit. The leader should have the largest I_k. For EQ-PL, the analog is the hub strength Σ_j |J^eq_kj|.

## Data scheme (`scheme/`)
- **Inputs:**
  - `data/processed/shared/activity_bins.parquet` (pt_date, minute, agent, state);
  - `calendar.parquet` (goal_no, regime, window_s, holdout);
  - `roster.parquet` (lab);
  - `events_core.parquet` (scheduler audit only).
  No raw tables.
- **Transform:** `scheme/build_spins.py`.
  - Select the analysis goal periods; drop every holdout day (`calendar.holdout`), with a hard assertion.
  - Split periods longer than 5 active days into consecutive 5-day **chunks**; keep a trailing chunk if it has ≥ 3 days.
  - **Present population** per chunk: agents with an `activity_bins` row on every day of the chunk *and* ≥ 30 active bins in it.
  - Spins are int8 ±1.
- **Output:** `data/processed/H02-couplings-are-real/`:
  - `spins.parquet` (goal_no, chunk, pt_date, minute, agent, s);
  - fit and null results (`*.parquet`, `*.json`);
  - `_provenance.json`.
- **Regimes covered:** I and III. Mode I has no regime-II weeks, so regime II is not compared.
- **Weeks.**
  - Mode I: #10, #17, #20, #39, #41, #42.
  - Mode C, matched by regime: #13, #18, #19, #24, #25, #26 (I) and #38, #40, #44 (III).

## Observables
1. **Synthetic recovery (axis F)**, with village sampling: N = 18, 241 one-min bins/day, D ∈ {1, 2, 3, 5, 10, 20} days.
   - Background couplings: each directed pair is nonzero with probability 0.15; |J| ~ U[0.05, 0.25]; 70% positive.
   - Planted leader with outgoing J_L ∈ {0.1, 0.2, 0.3, 0.5} to K_L = 5 followers; leader activity typical or low (~10% active).
   - Self-couplings and fields are calibrated from non-holdout regime-III fits of the independent model, and include a common time-varying (block) drive.
   - Reported per condition:
     - AUC for coupling existence (directed for KI, undirected for EQ-PL);
     - P(leader ranks #1 by I_k) for KI, or by hub strength for EQ-PL;
     - the leader's median rank.
   - Misspecification: influence delayed by a 5-min boxcar, fitted with KI-1 vs KI-5.
   - Null calibration: false-positive rate with zero cross-couplings.
2. **Null hierarchy on real data.** Per-coupling z-scores against surrogate distributions (100 surrogates per chunk):
   - **N0, day shift:** each agent's series circularly shifted by an independent random lag within each day. Keeps each agent's autocorrelation and daily count; destroys alignment, including alignment with the common drive.
   - **N1, block shift:** each agent shifted independently within each (day, 30-min block). Keeps each agent's half-hour rates, so the time-varying field (schedule, kickoffs) survives in the null.
   - **N2, model-family field:** a held-out comparison. Within each chunk, leave one day out; on the held-out day, refit only the block fields, with couplings fixed from the training days. Models:
     - M1: block fields + self-coupling;
     - M2: M1 + family/global mean fields (each agent couples to the mean spin of its own lab and of other labs; 2 parameters per agent);
     - M3: M1 + full pairwise J.

     ΔLL on held-out days tells whether pairwise couplings carry information beyond a family field. Family enrichment is also measured among significant couplings.

   Reported:
   - fraction of directed couplings with |z| > 1.96 (5% expected under the null) and the BH-FDR (q = 0.1) count;
   - excess magnitude, mean |J| − mean null |J|;
   - sign split.
3. **Scheduler / turn-taking audit.**
   - Sign distribution of significant equal-time EQ-PL couplings: mutual exclusion would give a surplus of negative J.
   - Event-level gaps between consecutive events of *different* agents vs. a label-shuffled baseline: a scheduler would leave a refractory hole.
4. **#26 (elected leader, exploratory):** DeepSeek-V3.2 (agent 17), its rank and z-score by I_k.
5. **#45 (confirmation; script only, not run):** rank and z of the Fine-Tuned Leader (agent 30) by I_k.

## Null / baseline
Null hierarchy, weakest to strongest:
- independent agents (N0);
- a time-varying field shared through the schedule (N1, plus block fields in the fit);
- a model-family field (M2 vs. M3 on held-out days; lab enrichment);
- scheduler exclusion (sign audit; event-gap audit).

Couplings are "real" only if they beat N1 and add held-out likelihood beyond M2.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** equilibrium Ising (01), whose couplings are symmetric, equal-time and undirected. Common-drive-only, i.e. independent agents with a time-varying field. Family-field-only.
**Locked holdout used for confirmation:** #45 (leader, ground truth). #14 and #49 (mode-I null weeks) are the natural transfer set for axis I; not run.

(Filled after the analysis; see Results.)

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | | |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | | |
| C adequacy | beats the null hierarchy, day-blocked held-out data | | |
| D unfitted predictions | unfitted statistics and the model's signature | | |
| E interventional | predicts the change across a natural experiment | | |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | | |
| G ground truth | agrees with known structure | | |
| H comparative | beats the named rivals | | |
| I transfer | holds in other same-mode periods, including the holdout | | |

## Prediction
*Written 2026-10-03, before running any analysis on real data. The only real data seen so far: table schemas, the roster, and per-period day counts and window lengths from `calendar` (sampling design).*

**Synthetic recovery (F).**
- **SP1.** KI-1 (block fields) recovers background-coupling existence with AUC ≥ 0.75 at D = 5, rising to ≥ 0.9 at D = 20.
- **SP2.** With typical leader activity, the leader ranks #1 by I_k:
  - in ≥ 90% of replicates at D = 5 when J_L ≥ 0.3;
  - in < 50% when J_L = 0.1.
  - Low leader activity costs about a factor of 2 in required days.
- **SP3.** EQ-PL ranks the leader #1 by hub strength less often than KI-1 ranks it #1 by I_k, at every D. It cannot give direction, and it creates follower–follower couplings from common input.
- **SP4.** With 5-min-delayed influence, KI-1's leader-recovery rate at D = 5 drops by ≥ 30 points; KI-5 restores most of it.
- **SP5.** Null calibration with zero cross-couplings but a common drive:
  - KI-1 with block fields vs. N1 gives 3–8% "significant" couplings;
  - KI-1-naive vs. N0 gives > 15%, because the common drive is mistaken for coupling.

**Real data (exploratory, non-holdout).**
- **RP1.** Fraction of significant couplings (KI-1 + block fields vs. N1):
  - mode-I chunks: median 8–20%, above the 5% floor (agents still share chat);
  - mode-C chunks: median ≥ 1.5× the mode-I median within the same regime.
- **RP2.** KI-1-naive vs. N0 gives ≥ 2× the significant fraction of the block-field fit vs. N1, in both modes: most raw coupling is common drive.
- **RP3.** Excess mean |J| over null is larger in mode C than in mode I within each regime.
- **RP4.** Held-out days (N2):
  - M3 beats M1 on a majority of held-out days in both modes;
  - the per-bin gain is larger in mode C;
  - M2 captures less than half of M3's gain.
- **RP5.** Scheduler: < 30% of significant equal-time (EQ-PL) couplings are negative, with no regime-wide negative block. Event gaps between different agents show no refractory hole beyond the label-shuffled baseline.
- **RP6.** Family: same-lab pairs are over-represented among significant KI-1 couplings by a factor ≥ 1.3 relative to their share of pairs.
- **RP7 (#26, low confidence).** DeepSeek-V3.2 ranks in the top 3 of the present agents by I_k.

**What counts against H02.**
- Couplings are not real influence measures if:
  - mode-I chunks couple as strongly as mode-C chunks (RP1/RP3 ratio ≤ 1.1);
  - or significant couplings vanish against N1 (fraction ≤ 7% in mode C);
  - or they are explained by the family field (M2 ≥ M3).
- The pipeline is not identifiable at the #45 scale if SP2 fails at J_L = 0.3, D = 5.

**#45 confirmation (holdout; `analysis/confirm_45.py`, not run).**
- The Fine-Tuned Leader (agent 30) ranks #1 of the present population by I_k.
- Its I_k z-score vs. the N1 surrogate distribution of I_k is ≥ 2.
- The estimator (KI-1 or KI-5) and all settings are frozen in the script before it is run.

## Results
(Exploratory; filled after analysis. Links to `analysis/` and `figures/`.)

## Notes
- 2026-10-03: card and predictions written before any real-data analysis. #45 calendar windows (5 days, ~241 bins) and roster (N = 18) were read as sampling design only.
