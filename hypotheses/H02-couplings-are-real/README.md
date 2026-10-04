# H02: Inferred couplings reflect real influence

**Status:** **#45 confirmation FAILED (locked holdout, run 2026-10-03):** the Fine-Tuned Leader ranks 4th of 18 by net outgoing influence (z = 0.76; the rule needed rank 1 and z ≥ 2). Before that, exploratory round 1 found:
- The pipeline is identifiable at village sampling for a strong leader.
- Pairwise couplings in non-holdout weeks are at null level.
- A weak equal-time collective coupling exists, concentrated in regime-III shared-objective weeks.

The #45 confirmation is written (`analysis/confirm_45.py`) but not run.
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

Scored 2026-10-03 after exploratory round 1 (non-holdout only), for the pairwise kinetic Ising (KI-1), the active spin, 1-min bins and the non-holdout chunks. Mean-field (H02-MF) scores are in brackets.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Spin = `activity_bins.state ≥ 3`; assumptions listed. Not invariant across regimes: in regime III, "active" is mostly computer-use turns, and the talk spin gives a different picture (Results 2e). |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Update-order audit: no refractory hole at 0–2 s; consolidations not synchronized (Results 2c). Stationarity handled by block fields. Markov order explored only synthetically (lag 1 vs 5-min boxcar). No time-rescaling test. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 0 [MF: 1] | Pairwise J: fraction significant vs N1 is at the calibrated false-positive rate. Leave-one-day-out M3 beats its N1 null (p = 0.048) in only 2/21 chunks. [The mean-field M2 beats N1 in 5/21 chunks, 3 of them regime-III mode C. CW βJ₀ survives matched lull exclusion in 5/21 chunks.] |
| D unfitted predictions | unfitted statistics and the model's signature | 0 [MF: 0] | CW forward P(K) fails: TVD improves in only 5/13 significant chunks, the low tail is underpredicted 2–5× in 3/13, and the observed kurtosis is higher than CW predicts. |
| E interventional | predicts the change across a natural experiment | 0 | Not attempted. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Synthetic (N = 18, 241 bins/day, calibrated fields, block drive): edge AUC 0.94 at 5 days; leader top-1 = 1.00 at J_L ≥ 0.3; null false-positive rate 5.8–7.6%. Robustness to preprocessing is weak: only 19% of significant couplings stay significant at 2-min bins, and a lag misspecification costs 25–50 points of leader recovery. |
| G ground truth | agrees with known structure | 0 | #26's elected leader not detected (rank 8/10). **#45 (locked holdout, 2026-10-03): failed**: the assigned leader ranks 4/18, z = 0.76 (Results 5). |
| H comparative | beats the named rivals | 0 [MF: 1] | Synthetic: KI-1 beats EQ-PL decisively on leader recovery. Real: pairwise J does not beat the common-drive-only or family/mean-field rivals on held-out days. [The mean field beats independence in regime-III mode C.] |
| I transfer | holds in other same-mode periods, including the holdout | 0 | #45 holdout run: no leader signal (Results 5). #14/#49 transfer not run. |

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

## Sub-hypothesis H02-MF: mean-field forward models (added 2026-10-03 at the user's request)
**Question.** Does a few-parameter mean-field model capture the village's coupling where N×N inference struggles, and does it *forward-predict* a statistic it was not fitted to?
**Models:**
- `physics-models/01-inverse-ising`, "Mean-field forward version" (HH80);
- `physics-models/02-nonequilibrium-ising`, "Mean-field forward version" (HH83).

- **MF-a, Curie–Weiss inversion (HH80).** Equal-time, uniform coupling βJ₀ with a time-varying field.
  - Within each (day, 30-min block), take the observed variance of M(t) = Σ_i s_i(t) and the independent expectation Σ_i var(s_i). Their pooled ratio is the variance ratio VR.
  - The mean-field fluctuation relation N Var(m) = q / (1 − βJ₀ q), with q = mean single-spin variance (≈ 1 − m²), gives βJ₀ = (1 − 1/VR) / q. Criticality is βJ₀ q → 1.
  - Null: N1 block-shift surrogates (100), which keep each agent's within-block variance exactly.
- **MF-a forward test.** The unfitted statistic is the shape of P(K), K = number of active agents per bin.
  - Per block, the CW prediction is the Poisson-binomial of the agents' block rates, tilted by exp(βJ₀ M²/2N + δM). δ is set so the block's mean K is matched.
  - Compare pooled observed P(K) with the CW and independent predictions, by total-variation distance (TVD), tail masses (K ≤ 1 and K ≥ N−1) and kurtosis. The variance is fitted; the tails and kurtosis are not.
- **MF-b, leader–follower mean field (HH83).** For candidate leader k, the follower model is
  logit P(s_f(t+1) = +1) = η_f(t) + 2 J_ff m_{F∖f}(t) + 2 J_lf σ_k(t),
  where η_f is the follower's own M1 predictor (block fields + self-coupling), used as an offset. The leader's reverse coupling J_fl comes from σ_k(t+1) on m_F(t). Statistics:
  - per agent k: J_lf(k) and the asymmetry A(k) = J_lf − J_fl, with z vs. 50 N1 surrogates;
  - computed in all non-holdout chunks ("ordinary weeks") and for #26.
  - The #45 version is written into `analysis/confirm_45.py` and not run.

**Predictions** *(written 2026-10-03, before any H02-MF statistic was computed. Not blind: informed by H09 E1's per-day VR of 1.25 in regime I and 1.61 in regime III, by this card's exploratory round 1 (equal-time EQ-PL couplings at null level, lagged mean-field M2 significant in 3/5 regime-III mode-C chunks), and by DeepSeek-V3.2's KI-1 rank in #26.)*
- **MF-P1.** βJ₀ is small everywhere: βJ₀·q < 0.5 (VR < 2) in every chunk, far from criticality.
- **MF-P2.** βJ₀ is consistent with 0 (|z| < 2 vs. N1) in ≥ 2/3 of mode-I chunks, and significantly > 0 in ≥ 3/5 regime-III mode-C chunks. The median βJ₀ for mode C exceeds the mode-I median in each regime.
- **MF-P3 (forward).** Where βJ₀ is significant, CW lowers the TVD of P(K) relative to the independent prediction. The unfitted tail masses agree with observation within a factor of 2.
- **MF-P4 (HH83, #26).** DeepSeek-V3.2's J_lf is not significantly > 0 (z < 2) and it is not the top agent by J_lf.
- **MF-P5 (ordinary weeks).** At most ~5% of agent × chunk J_lf values exceed z = 2 beyond the null. If the mean-field coupling of MF-P2 is real, it shows up as J_ff > 0, not as a single leader.
- **MF-P6 (#45, holdout, not run).** The Fine-Tuned Leader has the largest J_lf − J_fl of all agents and z ≥ 2 (secondary, not decisive).

## Results by goal period
One folder per goal period (`G<NN>/`) or spanning natural experiment (`NE<NN>/`), each with its verdict; the cross-hypothesis table is [../OVERVIEW.md](../OVERVIEW.md). Round-1 periods were scored against RP1 after the fact (`analysis/write_period_folders.py`): pairwise couplings reach the RP1 threshold in only G17 and G42; most periods sit at the null floor. G45 is the confirmatory failure.

## Results
**Exploratory round 1, 2026-10-03. Non-holdout data only; nothing here is confirmatory.**
- 21 chunks of ≤ 5 days: mode I = #10, #17, #20 (×2), #39, #41, #42; mode C = #13 (×2), #18 (×2), #19 (×2), #24, #25, #26, #38 (×3), #40, #44.
- Code is in `analysis/`; numbers are in `data/processed/H02-couplings-are-real/` (`results_summary.json` and the parquet files listed in `_provenance.json`).
- Figures: `figures/fig1_recovery.pdf` (synthetic), `fig2_nulls.pdf` (per-coupling nulls), `fig3_heldout.pdf` (held-out test), `fig4_g26.pdf` (#26), `fig5_meanfield.pdf` (H02-MF).

### 1. Synthetic recovery (axis F): `analysis/harness.py`, `validate_heldout.py`
Setup:
- village sampling: N = 18, 241 one-min bins/day (the #45 windows);
- per-agent (h, J_ii) drawn from non-holdout regime-III fits (median J_ii = 0.33, active fraction ≈ 0.5);
- common + agent block drive (SD 0.29 / 0.27);
- background couplings: density 0.15, |J| ∈ [0.05, 0.25];
- leader → 5 followers at J_L;
- 40 replicates per cell.

| D = 5 days | J_L = 0.1 | 0.2 | 0.3 | 0.5 |
| --- | --- | --- | --- | --- |
| KI-1: P(leader ranked #1 by I_k) | 0.25 | 0.68 | **1.00** | 1.00 |
| KI-1, low-activity leader (~15% active) | 0.18 | 0.60 | 0.98 | 1.00 |
| EQ-PL: P(leader = top hub) | 0.10 | 0.05 | 0.12 | 0.08 |
| P(planted leader is the *true* top influencer) | 0.33 | 0.78 | 0.99 | 1.00 |
| KI-1 rank #1 given true top (typical leader) | 0.64 | 0.80 | 1.00 | 1.00 |
| Confirmatory rule (rank 1 and z(I_k) ≥ 2 vs N1), 30 reps | – | 0.80 | 0.90 | 1.00 |

- **Days needed.** At J_L = 0.3, P(rank #1) is 0.72 at 1 day, 0.88 at 2 and 1.00 at 5. The J_L ≤ 0.2 curves plateau with more data, because background agents then *truly* rival the leader: a definitional limit, not an estimation one.
- **Edge recovery.** KI-1 AUC is 0.79 (1 day), 0.95 (5) and 0.99 (20). EQ-PL AUC is 0.54–0.73, and it creates follower–follower couplings from common input (+0.05 at J_L = 0.3).
- **Lag misspecification (D = 5, J_L = 0.3).**
  - With 5-min-delayed truth: KI-1 0.50, KI-5 0.73.
  - With lag-1 truth: KI-1 0.90, KI-5 0.63.
  - Whichever estimator is wrong loses 25–50 points.
- **Null calibration (D = 5).**
  - The per-coupling false-positive rate of KI-1 + block fields vs N1 is 5.8–7.6% (nominal 5%, slightly liberal). Naive vs N0 is 8.7–9.5%.
  - Power for |J| ∈ [0.05, 0.25] is 0.80–0.84.
  - With no leader, agent 0 tops I_k in 4.3–4.7% of 300 replicates (exchangeable). The confirmatory rule's false-positive rate is therefore ≤ 1/18.
- **Held-out machinery (N2, N = 15).** ΔLL(M3 − M1) is +92 millinats/bin with planted couplings (M3 wins 4.5/5 days), −93 with weak couplings (|J| ≤ 0.08) and −115 with none. So the raw ΔLL is negative under the null, and the calibrated version (vs surrogates) is needed.
- **Calibration and margins.** Bias is calibrated by the nulls. A uniform common-drive bias in J (+0.015 to +0.02) cancels in I_k.

**Are ~5 days enough for #45?**
- **Yes for a strong leader:** ≥ 5 followers at J ≳ 0.3 (Ising units), i.e. ΣJ_out ≳ 1.5, with the leader on lag-1 dynamics. P(pass) is ≈ 0.9–1.0, even if the leader is active only ~15% of the time.
- **Marginal at ΣJ_out ≈ 1** (P ≈ 0.7–0.8).
- **No for ΣJ_out ≲ 0.5**, at any length.
- **If influence is delayed by minutes,** KI-1 loses roughly half its power.

**Real-data context.** No non-holdout chunk contains an agent remotely like that:
- the top I_k is 0.07–0.49;
- its margin over the second agent is ≤ 0.25;
- the top z(I_k) is 0.6–2.8, which is what the maximum of N null z's gives.

### 2. Null hierarchy, mode I vs mode C: `analysis/nulls_real.py`, `heldout_null.py`, `scheduler_audit.py`, `binwidth.py`
**a. Per-coupling significance.** Median fraction of directed couplings with |z| > 1.96 (expected under the null ≈ 6–7% from §1), and pooled BH (q = 0.1) discoveries:

| regime / mode (chunks) | naive vs N0 | naive vs N1 | **KI-1 block vs N1** | KI-5 block vs N1 | EQ-PL block vs N1 | BH discoveries (KI-1) |
| --- | --- | --- | --- | --- | --- | --- |
| I / C (9) | 6.7% | 7.1% | 7.8% | 4.8% | 6.7% | 4 |
| I / I (4) | 10.5% | 7.5% | 8.4% | 2.6% | 9.9% | 1 |
| III / C (5) | 5.4% | 6.1% | 6.1% | 6.2% | 5.7% | 1 |
| III / I (3) | 6.2% | 6.2% | 5.7% | 7.1% | 6.7% | 2 |

- Mode C / mode I ratio: 0.92 in regime I (Mann–Whitney p = 0.70) and 1.06 in regime III.
- Excess mean |J| over null is 0.001–0.007 in every cell.
- **Pairwise lagged couplings in non-holdout weeks are indistinguishable from the block-shift null, in both modes.** This is not for lack of power: the same pipeline detects 80% of |J| ≥ 0.05 couplings synthetically.
- The common drive does not inflate the per-coupling test much: naive vs N0 ≈ block vs N1.

**b. Held-out days (N2), calibrated against 20 N1 surrogates** (`heldout_null.py`, fig3):
- **Raw.** M3 (pairwise) beats M1 on only 11 of 104 held-out days.
- **M3 vs N1.** p = 0.048 (the minimum) in 2/21 chunks (#38.1, #40), both regime-III mode C.
- **M2 vs N1** (lagged family + global mean field). p = 0.048 in 5/21: #38.1, #40, #44 (III-C), #42 (III-I) and #26 (I-C).
  - Median z21: III-C 5.2, III-I 1.6, I-C 0.35, I-I 0.41.
  - With 10-min blocks (stricter field), III-C still has 3/5 and III-I 1/3 (#42), with median z21 2.65 vs 0.2.
- **Reading.** The only transferable lagged coupling is *collective* (mean-field), at < 10-min timescales. It is concentrated in regime-III shared-objective weeks. It is not pairwise structure.

**c. Scheduler / turn-taking.**
- Event-level nearest-other-agent gaps vs per-agent circular shifts: ratio 0.99–1.07 at 0–2 s in both regimes, so no exclusion hole. For talk in regime I there is a 1.25× excess at < 1 s, i.e. co-triggering.
- Of significant equal-time EQ-PL couplings, 18% are negative (68 total), so there is no mutual-exclusion signature.
- CONSOLIDATE events are not synchronized across agents (ratio ≈ 1).

**d. Family.**
- Same-lab pairs: 7.6% significant vs 6.6% cross-lab, an enrichment of 1.11. Mean z is +0.26 vs +0.07.
- So there is at most a weak family field.

**e. Post-hoc mapping: talk spin (state = 4; agents with ≥ 30 talk bins).**
- Regime I: KI-1 significant fraction is 8.9% (C) vs 4.7% (I); BH discoveries 9 vs 1; held-out M3 vs N1 p < 0.05 in 2/9 vs 1/4.
- This is the only place a mode-C > mode-I difference appears at the pairwise level. It is post hoc and modest.
- In regime III, too few agents talk to say anything (N = 4–11).

**f. Bin width (not pre-registered).**
- Of 149 significant 1-min couplings, 78% keep their sign at 2-min bins, but only 19% stay significant.
- Median J correlation across bin widths is 0.43.

### 3. #26, elected leader (exploratory): `confirm_45.py --dry-run-goal 26 --leader 17`, 200 surrogates
- **DeepSeek-V3.2 (agent 17), by I_k:** rank 8/10 with KI-1 (z = −0.70); rank 7/10 with KI-5 (z = +0.30).
- **Other views:** rank 10/10 by EQ-PL hub strength; rank 2/7 by talk spin (z = 0.62); rank 10/10 by J_lf (z = −1.7).
- **No agent has z(I_k) ≥ 2.** The top one is Gemini 2.5 Pro (z = 1.95).
- **Caveat:** #26's leader only picked the goal, and the week mixes the election with the game, so it is weak ground truth.

### 4. H02-MF: `analysis/mf.py`, fig5
- **Curie–Weiss βJ₀ (equal-time, within 30-min blocks).**
  - Range −0.01 to 0.55; VR ≤ 1.57; βJ₀·q ≤ 0.36, far from criticality.
  - Significant vs N1 (z > 2) in 13/21 chunks: III-C 5/5, III-I 3/3, I-C 3/9, I-I 2/4.
  - Medians: III-C 0.28 vs III-I 0.19; I-C 0.10 vs I-I 0.12.
- **Lulls drive much of it.** Excluding bins with K ≤ 1 (global lulls), with surrogates filtered identically, leaves 5/21 significant:
  - #40 (z = 3.2) and #44 (3.6), both III-C;
  - #18.0, #19.0 (I-C) and #17 (I-I).
  - III-I drops to 0/3.
- **Forward P(K) fails** (the unfitted test):
  - CW lowers the TVD vs independent in only 5/13 significant chunks;
  - P(K ≤ 1) is underpredicted 2–5× in #38.0, #38.1 and #39;
  - the observed kurtosis exceeds both predictions where it matters (e.g. #39: 3.35 vs 2.76).
  - The excess co-activation looks like **synchronized lulls**: a fluctuating common field at < 30 min, such as platform-wide stalls. That is not what a ferromagnetic coupling predicts.
- **Leader–follower mean field (HH83).**
  - The follower–follower J_ff is significant in regime III (median z_ff 3.5 for C, 2.35 for I) but not in regime I (0.3–0.5).
  - z_lf > 2 for 9% of regime-III agent-chunks. This is inflated by the real J_ff, which surrogates destroy.
  - The directed asymmetry z_A > 2 holds for only 0–2.9% of agents. No ordinary week has a leader.

### 5. Confirmatory: #45, locked holdout (run 2026-10-03 23:13 UTC, signed off by Vivian; pre-registration commit e9bf2f7)
`confirm_45.py --confirm-holdout` was run once, with settings frozen as committed. Output: `data/processed/H02-couplings-are-real/confirm_45.json`; days 06-01 to 06-05, N = 18, leader = agent 30.

| Test | Result | Rule | Verdict |
| --- | --- | --- | --- |
| **Primary** (KI-1 block, active spin) | leader ranks **4/18**, I = 0.19, **z = 0.76**; top agent 18 has z = 1.90 | rank 1 and z ≥ 2 | **FAIL** |
| KI-5 block | rank 16/18, z = −0.91 | secondary | — |
| #best room only (N = 6) | **rank 1**, z = 1.28 | secondary | below z = 2 |
| Talk spin (N = 12) | rank 5, z = 0.41 | secondary | — |
| Held-out mean-field test | z21 = 1.26 (p = 0.10) | card predicted z21 ≥ 2 | fail |
| H02-MF leader–follower (MF-P6) | asymmetry A ranks 1st but z = 0.27; J_lf ranks 9th | MF-P6 | fail |
| Curie–Weiss | βJ₀ = 0.41, variance ratio 1.45, z = 6.5 | descriptive | strong collective co-activation in #45 |

**Reading:**
- The leader that the operators fine-tuned and installed is not visible as directed influence in 1-minute activity timing. Not across the whole village, and not robustly within its own #best room, where it ranks first but at z = 1.3.
- This matches the round-1 conclusion: activity-timing couplings carry collective co-activation, not pairwise influence. Whatever leadership #45 had has to show up in message content or replies (H01 D3.2, Hawkes on talk), not in when agents are active.
- The pre-registered credence was ~25% pass.

### Outcome vs prediction
| ID | Prediction | Outcome | Verdict |
| --- | --- | --- | --- |
| SP1 | KI-1 AUC ≥ 0.75 at 5 d, ≥ 0.9 at 20 d | 0.95 / 0.99 | ✓ |
| SP2 | leader top-1 ≥ 90% at J_L ≥ 0.3, 5 d; < 50% at 0.1; low activity costs ~2× days | 1.00; 0.25; low activity costs little (0.98) | ✓ / ✓ / ✗ |
| SP3 | EQ-PL hub < KI-1 at every D | typical leader: 0.02–0.15 vs 0.15–1.00 at every D. Low-activity leader at J_L = 0.1: EQ ties or beats KI (both ≤ 0.32) | ✓ (except the weakest, low-activity cell) |
| SP4 | delayed influence: KI-1 drops ≥ 30 pts; KI-5 restores most | −50 pts; KI-5 restores to 73% (of 100) | ✓ (partial restore) |
| SP5 | block vs N1 false positives 3–8%; naive vs N0 > 15% | 5.8–7.6%; 8.7–9.5% | ✓ / ✗ |
| RP1 | mode I 8–20% significant; C ≥ 1.5× I | I: 8.4% (reg I), 5.7% (III); C/I = 0.92, 1.06 | ✗: at the null floor; **S1 falsifier "null weeks couple as strongly" is met, trivially (neither mode couples pairwise)** |
| RP2 | naive vs N0 ≥ 2× block vs N1 | ≈ equal | ✗ |
| RP3 | excess \|J\| larger in C | 0.0008 vs 0.0067 (reg I); equal (reg III) | ✗ |
| RP4 | M3 > M1 on most held-out days; M2 < ½ of M3's gain | M3 wins 11/104 days; the mean field M2 carries *more* than M3 | ✗ (the collective, not the pairwise part, transfers; III-C only) |
| RP5 | < 30% negative among significant EQ couplings; no refractory hole | 18%; none | ✓ |
| RP6 | same-lab enrichment ≥ 1.3 | 1.11 | ✗ |
| RP7 | DeepSeek-V3.2 in the top 3 in #26 | 8/10 | ✗ |
| MF-P1 | βJ₀·q < 0.5 everywhere | max 0.36 | ✓ |
| MF-P2 | mode I ≈ 0 in ≥ 2/3 of chunks; III-C significant in ≥ 3/5; C > I | mode I significant in 5/7 (raw), 1/7 lull-excluded; III-C 5/5 raw, 2/5 lull-excluded; C > I in regime III only | ✗ raw / partial after lull exclusion |
| MF-P3 | CW improves P(K); tails within 2× | improves in 5/13; tails off 2–5× in 3/13 | ✗ |
| MF-P4 | DeepSeek-V3.2 J_lf not significant, not top | z = −1.7, rank 10/10 | ✓ |
| MF-P5 | ≤ ~5% z_lf > 2; collective coupling appears as J_ff | 9% (reg III; inflated by J_ff); z_A ≤ 2.9%; J_ff significant in regime III | partial ✓ |
| #45 / MF-P6 | Fine-Tuned Leader top by I_k with z ≥ 2 | **not run** (holdout) | pending |

**Bottom line (exploratory).**
- At 1-min activity resolution, the inverse-Ising couplings of non-holdout weeks are not interpretable as pairwise influence. They are at the null floor in both modes, they do not transfer across days, and they are weakly bin-width-stable.
- The pipeline itself is identifiable (synthetic), so this is a property of the data, not of the estimator.
- What *is* there is a weak collective co-activation, partly synchronized lulls. Beyond lulls and 10-min fields it survives mainly in regime-III shared-objective weeks (#40, #44). That is the S1 mode contrast, but at the mean-field level.
- Implication for H01 and others: do not read individual J_ij from activity spins. Use mean-field or block statistics, or a talk/mention mapping.

## Notes
- 2026-10-04: **#45 will be reused by H23** for confirmation on message content, a different modality from H02's activity timing, under the holdout reuse policy (`../holdout.md`).
- 2026-10-03: card and predictions written before any real-data analysis. #45 calendar windows (5 days, ~241 bins) and roster (N = 18) were read as sampling design only.
- 2026-10-03: H02-MF added at the user's request. Its predictions were written before any MF statistic was computed (informed by round-1 results, as stated).
- **2026-10-03, #45 confirm script frozen** (`analysis/confirm_45.py`; not run).
  - Primary: KI-1 + block fields, active spin, rank 1 and z ≥ 2 vs 200 N1 surrogates, as pre-registered. KI-1 was kept over KI-5 because each loses 25–50 points when misspecified, and the real data give no basis to prefer the delay model.
  - Secondaries, added before any holdout read: KI-5, KI-1 naive, EQ-PL hub, #best-room subset, talk spin, held-out M2/M3 vs N1, and H02-MF (CW βJ₀ and the leader–follower A = J_lf − J_fl).
  - The script refuses holdout goals unless `--confirm-holdout` is given. It was verified with a dry run on #26 and a refused dry run on #45.
- **Updated expectation for #45** (not a change to the pre-registered prediction): given that no non-holdout week has any agent with an influence margin > 0.25, #45 passes only if the Fine-Tuned Leader shifts followers' minute-level activity far more than any agent seen so far. My credence is ~25%. A pass would be striking; a fail would be uninformative about leadership via *content*.
- **Next steps:**
  - Hawkes vs Ising influence agreement (S1 observable) on talk events.
  - Kick covariates (`kicks`: human/automated messages) as an explicit fast field, to test whether the lulls and the mean-field coupling are platform stalls or nudges.
  - A mention-based "addressed interaction" spin.
  - HH81: does βJ₀ predict response decay?
  - Run the transfer set (#14, #49) once the project unlocks confirmation.
- Lull finding, relevant to H09 E1: the excess low tail of P(K) (everyone quiet together) is not reproduced by a Curie–Weiss coupling. It is better described as a fluctuating common field.

## Round 2 redirects (2026-10-04)
*From the round-1 reflection (`writeup/round1-reflection/round1-reflection.pdf`).*
- **Where round 1 went sideways:** Influence was inferred from when agents are active, but the turn scheduler sets activity timing, so the couplings measured scheduling, not influence.
- **What the direction is really after:** Who changes whose mind?
- **H02-R1.** Influence is the change in j's next decision when i's message is in j's context (context ledger), compared with matched turns where it is not.
- **H02-R2.** The #45 leader influenced plans, not activity: assignment-acceptance events (Jev-labeled) show its authority.
- **H02-R3.** Influence follows authority markers (operator endorsement, titles, a leader role), not model family.
