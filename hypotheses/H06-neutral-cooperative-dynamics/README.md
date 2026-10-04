# H06: Free weeks show neutral cooperative dynamics with a cooperator core

**Status:** exploratory round 1 done (2026-10-04). **Neutral cooperative dynamics (NCD) is refuted for free weeks:** P1 failed in 4/5 free weeks and mixed in 1 (card-level rule: failed). The reason is clean and holds in every period tested, free, shared-goal and #51 alike. Project abundances from self-written goals are far more fragmented than *any* exchangeable copying model allows (NCD, Hubbell, or herding). Singletons make up 0.79–0.91 of projects, only 0.23–0.53 of switches go to a project another agent holds (every copying model predicts ≈ 1), and all three models fail the joint posterior-predictive check in 27/30 free-week label sets. Copying adds only a small excess over independent agents. No cooperator core: μ̂ never falls below μ_B. A frozen confirmatory test on #22 is written, not run. Predictions were written 2026-10-04, before any real-data run.
**Fields:** stat mech, sociophysics
**Origin:** HH42 + HH16 (`../hypohypotheses/HYPOHYPOTHESES.md`; shortlist S6 in `../promotion-shortlist.md`)
**Definitions used:** "Agent state (categorical)" with two named variants: **agent state (categorical, project/artifact strict)** (H11's, imported) and a new **agent state (categorical, intention cluster)** (defined under Data scheme; proposed for DEFINITIONS.md). "Population N(t)", active-population variant (agent slots with a label in a window). "Regime" (each period sits inside one regime). "Interaction (broadcast)" is implicit in the model's well-mixed pairing (one room per scope).

## Question
In "pick your own goal" weeks, agents choose and abandon projects freely. Do project abundances follow *neutral cooperative dynamics* (Piñero-style: species, here projects, are equivalent, but joining is frequency-dependent and cooperative)? Signatures: bimodal abundances with a persistent cooperator core, Simpson concentration λ near the predicted λ*(μ, N), and boundaries μ_B (bimodal) and μ_L (log-series) in the novelty rate μ. Or does plain Hubbell neutral drift (log-series, no cooperation) explain them? Practical payoff: whether a free swarm concentrates its effort on a few shared projects by a predictable law, and what sets how many projects survive.

## Model
**From:** `physics-models/06-neutral-cooperative-dynamics` (read its README for the rules, λ*, μ_B, μ_L and the finite-N simulation), with `physics-models/10-potts` as the categorical-state view. H11 found strong herding (ferromagnetic Potts coupling) on project labels in 11/14 periods, including free weeks #31 and #37. That is the cooperative ingredient this model formalizes.

## Data scheme (`scheme/`)
`scheme/build.py` builds `data/processed/H06-neutral-cooperative-dynamics/G<NN>/` per goal period on a 30-min window grid counted from each day's empirical active-window start (H11's `load_calendar` / `window_table`, imported, not modified). It refuses holdout periods and days unless `--allow-holdout` (only `analysis/confirm_holdout.py`).

**Individuals** are agent slots: each labelled agent holds one current project in a window. With intention labels the slot is updated once per session goal (a "session" in regime I, a `CONSOLIDATE` goal in regime III), so sessions are the replacement events. **Species** are projects. Two label sources:
- **agent state (categorical, project/artifact strict)**, `art`: H11's strict artifact state, imported from `hypotheses/H11-potts-labor-vs-herding/scheme/build.py` (`build_project`): the raw (unmerged) project an agent mentions most in the window, strict mentions only (`how ∈ {url, output, bare}`). H06 adds a **carry-forward**: a slot keeps its last project for up to 3 further windows (2 h) of the same day when it has no new strict mention. Sensitivity: no carry-forward (H11's original).
- **agent state (categorical, intention cluster)**, `int`: self-written goals (`intentions`: session goals before 2026-03-24, `CONSOLIDATE` `nextSessionGoal` after). bge-small embeddings (`statements.parquet`, kind `intent`) are whitened per regime with `common.load_whitener` (32 dims), unit-normalized, and clustered within the period. **Clustering ladder, fixed a priori** by the mean cluster size m ∈ {8, 24, 64} intentions: k-means (`km8`, `km24`, `km64`; scipy `kmeans2`, k-means++ seeds) and Ward linkage (`wd8`, `wd24`, `wd64`), K = round(n_intents / m). **Primary: `km24`.** Ward is skipped for #51 (28k intentions; k-means only). A slot's label in a window is the cluster of its latest intention at or before the window end, the same day, written at most 3 windows earlier.
- **Scopes:** one room per scope. #44 uses only the #rest room (room 3), where agents picked their own goals; #37 has the #best/#rest rooms but one free goal (pooled, flagged). #51 uses its non-holdout part (2026-07-06 → 09-04).
- **Batch joins** (NE27, NE33) are pulses of new arrivals with empty memories; their first choices are tested in `NE<NN>/`.
- **Output:** `windows.parquet`, `labels_art.parquet` (gwin, agent, project_id, carried_age), `labels_int.parquet` (gwin, agent, age, one column per clustering), `intents.parquet` (one row per intention: agent, window, cluster ids; no text), `scope.json`, and `_provenance.json`. No text and no project names leave the shared tables except H11's project id map (`projects_art.parquet`, gitignored data only).
- **Regimes covered:** #8–#31 regime I (one room), #37–#51 regime III. No scope crosses 2026-03-24.

## Candidate goal periods
Free weeks #11, #16, #31, #37 (#22 🔒 held out), #44 #rest; #51 as a check (private goals, not free). Shared-objective weeks as contrasts.

## Links to other hypotheses
H11 (herding on project labels), H01 D7.1 (condensation vs leaders), H12 (dimensionality), HH16 (cooperator core), HH71 (rich club).

## Observables
*Written 2026-10-04, before any real-data run.* All per goal period (scope), per label set, computed by `analysis/ncd_core.py` identically on data and on simulations.

**Simulation layer (exact finite-N rules, village sampling).** Each candidate model is simulated with N = the number of agent slots in the scope, snapshotted once per real 30-min window (real windows per day, one window's worth of steps overnight), with **the real label mask applied** (an unlabelled agent-window is hidden in the simulation too). Between windows k·N model steps run. Each model gets its own (μ, k), fitted on a (μ, k) grid by matching **two moments only**:
- c, the change rate: label changes per observed within-day transition (agent labelled in consecutive windows);
- f_nov, the novelty fraction: the share of changes that go to a species never observed before in the period.

Everything below is an **unfitted** prediction of each fitted model (400 simulated replicates at the fitted point).

- **O1 novelty rate.** μ̂ per model step under NCD (and under each rival), and the raw f_nov ("new projects per replacement"). Placed against μ_B(N) = e^{−2}/√(2πN) (bimodal below) and μ_L(N) = √(2/(πN)) (log-series above).
- **O2 Simpson λ vs λ\*.** λ̄ = mean over windows (≥ 2 labelled slots) of Σ_i (n_i/n_obs)². Compared with the finite-N simulated λ under NCD at μ̂_NCD (the test) and with the asymptotic λ\*(μ̂, N) from the paper's self-consistency (reported; the synthetic work shows it overstates finite-N λ at low μ).
- **O3 abundance distribution P_n.** Pooled histogram over windows of species abundances n (agents per project). Summaries: singleton fraction, mean dominant share x_max, richness per labelled slot; "bimodal" = an interior mode at n ≥ 2. Compared with each model's predictive P_n.
- **O4 residence time vs maximum abundance.** One point per species: windows from first to last appearance, and peak abundance. Statistics: ΔBIC (1 vs 2 diagonal Gaussian clusters on the logs; > 0 favours two clusters) and the infiltration fraction (share of species born inside the period that reach the core abundance m_core = max(2, round(¼ median n_obs))).
- **O5 frequency dependence.** For every non-novel label change at t → t+1, the choice among projects held by the other labelled slots at t, fitted by conditional logit P(i) ∝ x_i e^{β x_i} (MAP, weak N(0, 5²) prior). Hubbell copying gives β ≈ 0, NCD (rare projects recruit more per capita) β < 0, herding β > 0; the exact expectation under each model at village sampling comes from the simulations.
- **O6 model comparison.** Gaussian synthetic log-likelihood (Wood 2010) of the 7 unfitted statistics (λ̄, x_max, singleton fraction, richness, β, infiltration, ΔBIC) under each fitted model. LLR_NH = ℓ_NCD − ℓ_Hubbell and LLR_NC = ℓ_NCD − ℓ_conformist.
- **O7 adequacy.** Two-sided posterior-predictive p-value of each statistic under each fitted model; a model is **adequate** if no statistic has p < 0.05/7 (amended before the real-data run: 0.05/9 over the 9 fitted statistics, plus a joint Mahalanobis PPC p ≥ 0.01; amendments 1 and 3).
- **O8 mapping audit.** copy-consistency (share of non-novel changes whose new project is held by another labelled slot at the previous window; the models make every non-novel change a copy) and λ̄ split-half stationarity (first vs second half of the period).
- **O9 newcomer kernel (NE folders).** For agents arriving in a batch join, each non-novel choice on their first active day, against the projects then held by incumbents: the likelihood of the single-step kernels w(x) = x(1−x) (NCD), x (Hubbell), x·[x + 0.2(1−x)] (conformist).

## Null / baseline
- **Rival R1: Hubbell neutral drift** (named in S6): C copies a random A; log-series abundances; no frequency dependence. Same two fitted moments.
- **Rival R2: conformist herding** (added because H11 found ferromagnetic project coupling in 11/14 weeks, including free weeks #31 and #37): C copies A with probability 1 if A and B agree, else 0.2. Per-capita recruitment rises about 5× with share. Same two fitted moments. (Pure "copy only on agreement" is absorbing from singletons, hence the 0.2 leak.)
- **N-ind: independent agents (day-shift).** Each agent's label sequence is moved by a random whole number of days (cyclic, within-day window index kept), 200 draws. Keeps each agent's own repertoire and persistence, destroys cross-agent co-occurrence. Applied to λ̄, copy-consistency and β. A copying model of any kind needs λ̄ and copy-consistency above this null.
- **Known confounds:** stable agent specialization (fields) makes species agent-bound, which no copying model contains (H11's own-artifact weeks); common time-varying drive (announcements) makes everyone move together, which reads as herding; labels are attention (art) or stated plans (int), not work.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** (R1) Hubbell neutral drift (copy a random individual; log-series); (R2) conformist herding (copy favoured by agreement; H11's ferromagnetic coupling in kinetic form); null N-ind, independent agents (day-shift).
**Locked holdout used for confirmation:** none yet. Target #22 (`analysis/confirm_holdout.py`, frozen after round 1; not run).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Individuals = agent slots and species = projects, from two field-defined label sources: H11's strict artifact state, and whitened intention clusters with a fixed 6-clustering ladder. Same rules in regimes I and III. But an intention means a session goal in regime I and a `CONSOLIDATE` goal in regime III, and artifact labels are attention, not work. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | **Stationarity:** split-half λ̄ similar in most periods. **Mapping audit failed:** the models make every non-novel switch a copy of a currently held project, but only 0.23–0.53 of free-week switches are (O8). **Not audited:** update order and Markov order. The window-to-step mapping is a fitted nuisance (k). |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 0 | NCD is adequate (joint PPC p ≥ 0.01) in 0/5 free weeks on the primary labels and 2/30 free-week label sets overall. It is beaten by a rival in 4/5. Only #37's artifact labels are fitted adequately (p 0.06), at μ̂ near μ_L, where NCD and Hubbell coincide. |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | λ̄ is below NCD's 95% interval in 26/30 free-week label sets; P3 holds only in #16, trivially, at μ̂ ≥ μ_L. Negative frequency dependence (P2) appears in 1/5 free weeks. The signature (a cooperator core, bimodality at μ < μ_B) is never in range: μ̂ lies between μ_B and μ_L or above it everywhere. |
| E interventional | predicts the change across a natural experiment | 0 | NE27 and NE33: every model fitted before the batch join predicts a post-join λ̄ far above the observation (PPC p 0.005). Newcomers mostly start projects nobody holds, so the kernel test has 4 + 1 choices (uninformative). |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Exact finite-N simulation with the real label mask. The P1 rule separates NCD from both rivals with power ≈ 0.9 and false support ≤ 0.08 at N ≥ 12, μ ≤ 0.05. Power is weaker at N = 7 (30% false 'failed' at μ = 0.01), and support is impossible near μ_L by design. μ is recovered within about 2×. Verdicts agree across the 6 clusterings, both artifact variants, and H11's labels vs the deterministic shared `project_states` labels (99.4–99.8% pair agreement, same verdicts). Agent-bound projects were not simulated, and the embedding model was not varied. |
| G ground truth | agrees with known structure | 1 | #31's narrated convergence gives the most concentrated free-week artifact abundances (λ̄ 0.37). #51's private assigned roles give the most fragmented ones (λ̄ ≈ 1/N, singletons 0.97, copy-consistency 0.08). #44 #rest ("each chose creative work") is fragmented (λ̄ 0.13). |
| H comparative | beats the named rivals | 0 | On km24, NCD beats Hubbell by ≥ 2 only in #31 and loses to the conformist rival in all 5 free weeks. All three rivals are also inadequate, so these likelihood ratios rank wrong models: the conformist "wins" mostly because its predictive spread is wide. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Holdout not run. What transfers is the failure pattern: all models inadequate, with excess singletons and low copy-consistency, in all 12 non-holdout periods, across regimes I and III and modes F, C and P. |

## Prediction
*Written 2026-10-04, before running the analysis on real data.*

**What I had seen when writing this:**
- H11's card and results: herding (βJ_CW > 0, z_N2 ≥ 2) on artifact labels in #31 and #37; #11 and #16 had too few artifact labels (3 and 5 room blocks); #31 "herding waves onto successive shared repos";
- structural counts only: intentions per period (≈ 10–20 per agent-day; #11 362, #16 351, #31 1,291, #37 551, #44 769, #51 28,090 non-holdout), agents per period, and H11's labelled agent-windows per window (#11 0.7, #16 1.2, #31 10.1, #37 4.6, #44 11.3 incl. #best);
- the synthetic validation (calibration notes appended below, dated).

I had **not** seen any abundance, Simpson index, novelty rate, switching rate, recruitment or residence statistic of any period.

**Periods.** Free weeks (the test): #11, #16, #31, #37, #44 (#rest room). #51 non-holdout part: check (private assigned goals). Shared-objective contrasts: #19, #25, #30, #38. Spanning tests: NE27 (2025-08-18, +3 agents, #8 → #10) and NE33 (2026-09-03/04, +3 agents inside #51; only 1–2 non-holdout days after it). #22 is the locked confirmation target.

**Testability rule.** A label set is tested in a period only if it has ≥ 3 labelled slots per window on average and ≥ 20 observed label changes; otherwise "n/a (insufficient labels)". (By H11's counts, artifact labels will be n/a in #11 and #16, so intention clusters are primary everywhere.)

- **P1 (primary, O6 + O7). NCD beats both rivals in free weeks.** Primary label set: intention clusters `km24`.
  - **Per period:**
    - **supported** if LLR_NH ≥ 2 and LLR_NC ≥ 2, the same signs hold in ≥ 4 of the 6 intention clusterings, and NCD is adequate (no statistic with PPC p < 0.05/7; amended to 0.05/9 plus a joint PPC, see amendments 1 and 3 below);
    - **failed** if a rival beats NCD by ≥ 2 (LLR_NH ≤ −2 or LLR_NC ≤ −2) on `km24` and in ≥ 4 of 6 clusterings;
    - **mixed** otherwise.
  - **Card level, over the 5 free weeks:** supported if ≥ 3 supported and none failed; failed if ≥ 3 failed; mixed otherwise.
- **P2 (O5). Negative frequency dependence:** in free weeks, β̂ is below the Hubbell predictive median and inside the NCD 95% predictive interval. Counts against: β̂ above the Hubbell 97.5% point (herding).
- **P3 (O2). λ̄ sits at the NCD value:** λ̄ inside NCD's 95% predictive interval, and (where μ̂_NCD < μ_L) below Hubbell's 2.5% point. Counts against: λ̄ far from λ_NCD(μ̂, N), in either direction.
- **P4 (O3, O4). Signatures, conditional on μ̂_NCD:**
  - μ̂ < μ_B: P_n has an interior mode (a cooperator core), ΔBIC > 0 (two classes), infiltration inside NCD's interval;
  - μ_B ≤ μ̂ < μ_L: NCD and Hubbell still differ in λ and β (P2, P3), but no bimodality is required;
  - μ̂ ≥ μ_L: both reduce to log-series; P4 is n/a.
  - **Falsifier (S6):** in a week with μ̂ < μ_L, a log-series P_n that Hubbell predicts better than NCD, together with no negative frequency dependence and λ̄ outside the NCD interval.
- **P5 (secondary label set). Artifact labels** where testable (#31, #37, #44): same rule as P1. **My expectation, from H11:** the conformist rival beats NCD on artifact labels in #31 and #37 (LLR_NC ≤ −2).
- **P6 (contrasts).** Shared-objective weeks #19, #25, #30, #38: herding, not cooperation. LLR_NC ≤ −2 (conformist beats NCD) on intention `km24`, and λ̄ above the NCD 97.5% point. A shared goal is a field that concentrates effort.
- **P7 (#51 check).** Private assigned goals make projects agent-bound: copy-consistency is low, λ̄ is not above the N-ind day-shift null, and NCD is not adequate. **The check passes if #51 is not "supported" under P1's rule.** If #51 also came out "supported", the pipeline would not distinguish fields from cooperative copying, and free-week support would be discounted.
- **P8 (N-ind). Some copying exists in free weeks:** λ̄ and copy-consistency above the day-shift independent-agents null (one-sided p < 0.05) in ≥ 3/5 free weeks. Without that, no copying model (NCD, Hubbell or herding) is needed.
- **P9 (NE27, NE33, O9). Newcomer kernel:** newcomers' first-day non-novel choices favour the NCD kernel x(1−x) over x (Hubbell) and over the conformist kernel (log-likelihood ratio > 0 against both, pooled over both joins). Expected to be weak: 3 newcomers per join, and NE27 coincides with the #10 goal change (games week, individual objectives).

**Calibration notes and amendments from the synthetic validation** (appended 2026-10-04, after `analysis/synthetic.py` finished and **before any real-data run**; data in `data/processed/H06-neutral-cooperative-dynamics/synthetic/`). Configurations: N = 7 (5 days × 6 windows, as in #11/#16), N = 13 (5 × 8, #31; label-observation probability 0.85 or 0.5) and N = 12 (3 × 8, #37/#44); true μ ∈ {0.01, 0.05, 0.2}, k = 1; 60 datasets per true model.
- **Finite N matters.** At N = 13, μ = 0.003 the asymptotic λ\* is 0.75 but the simulated NCD λ is 0.52; at μ = 0.1, 0.33 vs 0.29. The asymptotic formula overstates λ at low μ, so the test uses simulated λ.
- **Amendment 1 (fitting).** Fitting (μ, k) on the two moments alone is weakly identified: under Hubbell, lower μ lowers diversity, so the novelty fraction stays flat and the fit slides along a μ–k ridge. Hubbell data at μ = 0.2 were then misread as NCD in 47–78% of runs. **Each model is now fitted by profile synthetic likelihood over its (μ, k) grid (20 × 14 cells, 80 replicates per cell) using all 9 statistics (c, f_nov and the 7 above)**. LLRs are computed from 400 fresh replicates at each model's best cell, so the grid's winner's curse does not enter. λ and β are no longer strictly unfitted (2 parameters on 9 statistics); the moment-only λ prediction is still reported as a secondary, flagged as weakly identified. PPC thresholds become 0.05/9.
- **Amendment 2 (high μ).** Near μ_L the two models converge (synthetic, μ = 0.2: Hubbell data read as P1-"supported" in 7–27% of runs, NCD data in 47–60%). **A P1 "supported" with μ̂_NCD ≥ μ_L/2 is downgraded to "mixed".**
- **Amendment 3 (adequacy).** With 200–400 replicates, a single-statistic p < 0.05/9 is nearly unreachable (adequacy was 1.0 in every configuration). **"Adequate" now also needs a joint Mahalanobis posterior-predictive p ≥ 0.01.** Under the true model p_joint < 0.01 occurred in 0/240 runs. At N = 13 it rejects NCD for Hubbell or conformist data in 48–100% of runs (N = 7: 0–35%).
- **Power of the P1 rule (one clustering; amendments 1–2 applied):**

| True model | μ | N = 7 (#11, #16) | N = 13, p_obs 0.85 (#31 int) | N = 13, p_obs 0.5 (#31 art) | N = 12, 3 days (#37, #44) |
| --- | --- | --- | --- | --- | --- |
| NCD: supported / failed | 0.01 | 0.50 / 0.30 | 0.95 / 0.00 | 0.98 / 0.02 | 0.93 / 0.02 |
| NCD: supported / failed | 0.05 | 0.90 / 0.03 | 0.97 / 0.00 | 0.88 / 0.00 | 0.55 / 0.05 |
| NCD: supported / failed | 0.2 | 0.00 / 0.03 (downgraded) | 0.00 / 0.03 | 0.00 / 0.02 | 0.00 / 0.00 |
| Hubbell: supported / failed | 0.01 | 0.00 / 0.97 | 0.00 / 1.00 | 0.00 / 0.98 | 0.03 / 0.97 |
| Hubbell: supported / failed | 0.05 | 0.12 / 0.78 | 0.02 / 0.95 | 0.08 / 0.90 | 0.05 / 0.92 |
| Hubbell: supported / failed | 0.2 | 0.00 / 0.55 | 0.00 / 0.42 | 0.00 / 0.35 | 0.00 / 0.35 |
| Conformist: supported / failed | 0.01–0.05 | 0.00 / ≥ 0.98 | 0.00 / 1.00 | 0.00 / 1.00 | 0.00 / 1.00 |
| Conformist: supported / failed | 0.2 | 0.00 / 0.55 | 0.00 / 0.73 | 0.00 / 0.60 | 0.00 / 0.53 |

  So at N ≥ 12 and μ ≤ 0.05 the rule tells NCD from both rivals with power ≈ 0.9 and false support ≤ 0.08. At N = 7 and very low μ, NCD data are falsely "failed" 30% of the time, which matters for #11 and #16. At μ ≈ 0.2 no support is possible by construction (amendment 2), and rival data are "failed" only 35–73% of the time.
- **μ recovery (NCD data, profile fit):** median μ̂ 0.005–0.013 for true 0.01; 0.032–0.059 for 0.05; 0.20 for 0.2.
- **Frequency dependence calibrates as expected:** median β̂ for NCD data is −1.2 to −1.7 (μ ≤ 0.05) and −0.6 to −1.4 (μ = 0.2); for Hubbell data −0.6 to +1.1; for conformist data +1.9 to +2.8. Window aggregation shifts β by up to ±1, which is why it is judged against simulations, not against 0.
- **Not simulated:** agent-bound projects (fields), common drive, and the robustness rule across 6 clusterings.

**Credences** (mine, before running):
| Prediction | Credence | Why |
| --- | --- | --- |
| P1 card-level supported | 0.15 | H11's herding on artifact labels points the other way (to R2); intention clusters may be agent-bound (fields), which none of the models contain |
| P1 card-level failed | 0.45 | |
| P2 | 0.2 | Herding (H11) predicts β > 0 |
| P3 | 0.3 | |
| P5 (conformist beats NCD on art in #31 and #37) | 0.6 | |
| P6 | 0.5 | |
| P7 check passes | 0.7 | |
| P8 | 0.7 | |
| P9 | 0.15 | |

## Results by goal period
All run 2026-10-04 on non-holdout data; predictions written before the run (card and each period README). Key numbers are for intention clusters km24 unless stated: λ̄ observed vs NCD's predicted mean; singleton fraction; copy-consistency (cc); LLR_NH and LLR_NC (NCD minus Hubbell, minus conformist).

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G11](goalperiod-subhypotheses/G11/README.md) | free, N = 7 | failed (P1); all models inadequate | λ̄ 0.21 vs 0.34; singletons 0.91; cc 0.23 (null 0.21); LLR −3.9 / −7.0; art n/a |
| [G16](goalperiod-subhypotheses/G16/README.md) | free, N = 7 | mixed (P1); all models inadequate | λ̄ 0.21 vs 0.26 (μ̂ 0.38 ≥ μ_L); singletons 0.86; cc 0.53; LLR −0.8 / −8.8; β̂ +5.0 (herding direction); art n/a |
| [G31](goalperiod-subhypotheses/G31/README.md) | free, N = 13 | failed (P1); P2 supported; all inadequate | λ̄ 0.15 vs 0.23; singletons 0.79; cc 0.34 (null 0.22); LLR +22.0 / −34.9; β̂ −0.78; art: failed (Hubbell best), λ̄ 0.37, β̂ −1.73 |
| [G37](goalperiod-subhypotheses/G37/README.md) | free, N = 12, 2 rooms | failed (P1); all inadequate | λ̄ 0.14 vs 0.26 (below the independent null 0.21); cc 0.37; LLR −3.0 / −16.3; art: mixed, NCD best and adequate (p 0.06) but μ̂ ≈ μ_L |
| [G44](goalperiod-subhypotheses/G44/README.md) | free (#rest), N = 12 | failed (P1); all inadequate | λ̄ 0.13 vs 0.24; singletons 0.86; cc 0.33; LLR −1.4 / −18.6; art failed (β̂ +4.2; +2.0 on shared labels) |
| [G19](goalperiod-subhypotheses/G19/README.md) | contrast (shared) | mixed (P6) | conformist ≫ NCD (LLR_NC −29) but λ̄ 0.26 below NCD 0.43; cc 0.34 |
| [G25](goalperiod-subhypotheses/G25/README.md) | contrast (shared) | mixed (P6) | LLR_NC −30; λ̄ 0.20 vs 0.43; cc 0.45 |
| [G30](goalperiod-subhypotheses/G30/README.md) | contrast (shared) | mixed (P6) | LLR_NC −66; λ̄ 0.14 vs 0.26; cc 0.36; art λ̄ 0.61 (one dominant repo) |
| [G38](goalperiod-subhypotheses/G38/README.md) | contrast (shared, 17 days) | mixed (P6) | LLR_NC −151; λ̄ 0.09 vs 0.19; singletons 0.94; cc 0.15 |
| [G51](goalperiod-subhypotheses/G51/README.md) | check (private goals), 3 blocks | P7 passes (0/3 supported), uninformative | λ̄ 0.05–0.06 (≈ 1/N); singletons 0.95–0.97; cc 0.08–0.10 (lowest of all periods) |
| [NE27](goalperiod-subhypotheses/NE27/README.md) | spanning (#8 → #10) | failed | pre-fit models predict post λ̄ 0.46–0.58, observed 0.20; newcomer kernel: 4 choices, tied |
| [NE33](goalperiod-subhypotheses/NE33/README.md) | spanning (inside #51) | failed | NCD predicts post λ̄ 0.12 [0.09, 0.15], observed 0.042; newcomers: 1 copy choice in 19 changes |
| [G22](goalperiod-subhypotheses/G22/README.md) | confirmatory (holdout) | pending (not run) | frozen in `analysis/confirm_holdout.py` |

## Results
*Exploratory round 1, 2026-10-04.*
- **Code:** `scheme/build.py`; `analysis/ncd_core.py` (simulators, statistics, fits); `synthetic.py`; `explore.py`; `ne_tests.py`; `period_folders.py`; `assemble.py`; `robust_shared_labels.py`; `figures.py`; `summary_figure.py`; `confirm_holdout.py` (not run).
- **Data:** `data/processed/H06-neutral-cooperative-dynamics/`: `G<NN>/round1_<scope>.json`, `results_round1.parquet`, `cross_period_round1.json`, `NE27_round1.json`, `NE33_round1.json`, `robust_shared_labels.json`, `synthetic/`.

**Outcome vs prediction**

| Prediction | Outcome | Verdict |
| --- | --- | --- |
| P1 NCD beats Hubbell and herding in free weeks (primary) | **Free weeks:** failed in #11, #31, #37, #44; mixed in #16. NCD beats both rivals by ≥ 2 in 1 of 30 free-week clustering fits. All three models fail the joint PPC in 27/30 | **Failed** (card-level rule: ≥ 3 failed) |
| P2 negative frequency dependence | Intention labels: 1/5 (#31, β̂ −0.78). β̂ is in the herding direction in #16 (+5.0) and #11 (+4.0, 10 events). Artifact labels: #31 (−1.73) and #37 (−0.70) supported, #44 failed (+4.2). β̂ has no consistent sign across periods (SE ≈ 1–2) | **Failed** (inconclusive sign) |
| P3 λ̄ at the NCD value | 1/5 (#16, at μ̂ ≥ μ_L, where it is uninformative). λ̄ is below NCD's 95% interval in 26/30 free-week label sets, and below all three models' intervals in 25/30. Asymptotic λ\* overstates λ even more | **Failed**: λ is too *low* for every copying model |
| P4 core signatures when μ̂ < μ_B | μ̂_NCD < μ_B in no free week (only #30's artifact labels, a contrast). No bimodality claim can be tested | **n/a** |
| P5 artifact labels (expected: herding beats NCD in #31 and #37) | #31: Hubbell best, conformist beats NCD (LLR_NC −3.9). #37: NCD best (+2.3 / +9.2) and the only adequate fit, but μ̂ ≈ μ_L. #44: Hubbell best. Unchanged on the shared deterministic labels | **Failed** for NCD; my herding expectation holds in #31 only |
| P6 shared-goal contrasts: herding and λ̄ above NCD | Conformist ≫ NCD in 4/4 (LLR_NC −29 to −151), but λ̄ is *below* NCD's interval in 4/4. Shared-goal weeks are not more concentrated in stated goals than free weeks (λ̄ 0.09–0.26 vs 0.13–0.21) | **Mixed** 4/4 |
| P7 #51 check not supported | 0/3 blocks supported. It is uninformative, since the free weeks fail too. But copy-consistency is lowest in #51 (0.08–0.10), as private roles imply | **Passes** (weak) |
| P8 copying above independent agents | λ̄ above the day-shift null in 4/5 free weeks; copy-consistency above it in 3/5; both in 2/5 (#16, #31). The excess is small (#31: λ̄ 0.149 vs 0.117; cc 0.34 vs 0.22) | **Failed** by the ≥ 3/5 rule; a small copying excess exists |
| P9 newcomer kernel | NE27: 4 multi-option choices, kernels tied within 0.03 nats. NE33: 1 choice. Newcomers mostly start projects nobody holds (2/6 and 18/19 changes) | **n/a** (no power) |
| NE (a) fit before, predict after | Every model over-predicts post-join λ̄ (NE27: 0.46–0.58 vs 0.20; NE33: NCD 0.12 vs 0.042) | **Failed** |

**Synthesis**
1. **The project ecology of a free LLM swarm is not a neutral community of exchangeable copiers.** Exchangeability is the assumption every model here shares (NCD, Hubbell, herding). Agents mostly carry their own projects: 79–91% of project occurrences in free weeks are singletons (one agent), against NCD's predicted 0.45–0.68 at the fitted μ (km24). Only a quarter to half of switches land on a project someone else currently holds. The rest are returns to an agent's own earlier project or fresh starts. That is the field (agent-specific repertoire) structure H11 found as "specialization" in own-artifact weeks. It appears here in *stated goals* in every week, free or not.
2. **Copying exists but is a small perturbation.** Over the day-shift independent-agents null, λ̄ rises by 0.01–0.03 and copy-consistency by 0.02–0.15 in most periods. H11's strong equal-time herding on artifact links (βJ ≈ +2 to +5) is thus compatible with a project ecology dominated by private projects: herding is about *where agents look* (shared repos) more than *what they say they are doing*.
3. **Frequency dependence has no consistent sign.** β̂ (rare-project advantage if negative) ranges from −5.8 to +5.0 across periods and label sets, with SE 1–2. The NCD rare-species advantage is neither confirmed nor excluded. The large values come from few events (10–30 per period on intention labels).
4. **Mode does not matter much.** Shared-goal weeks look like free weeks in stated-goal abundances (λ̄ overlaps). #51 (private roles) is the most fragmented and least copy-consistent, the one ordering the statistics get right.
5. **Model-comparison caveat.** With all models rejected, "best by likelihood" mostly tracks predictive spread. The conformist's broad predictive distribution "wins" 20/30 free-week fits, which is not evidence for herding.
6. **Robustness.**
   - Verdicts agree across the six clusterings: P1 "failed" needs ≥ 4/6; #31 6/6, #37 5/6, #11 4/6, #44 4/6, #16 3/6 (mixed).
   - Artifact verdicts are unchanged on the deterministic shared labels (`robust_shared_labels.json`): #31 LLR −15.7/−3.9 → −9.8/−7.2; #37 +2.3/+9.2 → +5.8/+9.3; #44 −7.2/−6.0 → −8.4/−8.2.
   - The headline statistic (adequacy) does not depend on H11's labels at all; it comes from intention clusters.

**Figures**
- [`figures/summary_obs.pdf`](figures/summary_obs.pdf) (summary page);
- [`figures/lambda_copy_by_period.pdf`](figures/lambda_copy_by_period.pdf) (λ̄, singletons, β̂, copy-consistency vs predictions);
- [`figures/llr_by_period.pdf`](figures/llr_by_period.pdf);
- [`figures/pn_residence_free.pdf`](figures/pn_residence_free.pdf) (P_n and residence vs maximum abundance);
- [`figures/synthetic_validation.pdf`](figures/synthetic_validation.pdf);
- per-period `goalperiod-subhypotheses/G<NN>/figures/pn_<scope>.pdf`;
- one-page summary: [`summary/summary.pdf`](summary/summary.pdf).

**Confirmatory prediction for #22** (frozen 2026-10-04 after round 1, before any #22 data was read; `analysis/confirm_holdout.py`; same pipeline and seeds):
- **C1**, the original P1 rule: NCD "supported" on km24. **Round 1 predicts that C1 fails.**
- **C2**, agent-bound projects (the round-1 pattern). Needs (a) joint PPC p < 0.01 for both NCD and Hubbell, and at least one of: (b) copy-consistency < 0.8 and outside NCD's 95% interval; (c) singleton fraction above NCD's 97.5% point. Refuted if NCD is adequate and (b) and (c) both fail.
- **C3:** β̂ not below the Hubbell predictive median.
- **C4:** λ̄ above the day-shift null (p < 0.05).

Dry run on stand-ins #11 and #16 (`confirm_dryrun.json`): C1 not confirmed, C2 confirmed on both. It needs `--confirm --i-understand-this-uses-the-locked-holdout` and Vivian's sign-off. H11 also targets #22, with a different statistic (Potts coupling on artifact labels). Under the reuse policy, the second run must disclose the first.

**Caveats**
- **Labels.** Intention clusters are stated plans, embedded with one model (bge-small) and clustered within each period, so a cluster is a *topic*, not necessarily a shared project. Two agents writing about the same repo in different words can land in different clusters, which inflates singletons. The ladder (m = 8–64) and the artifact labels, which name the actual repo, mitigate this. But artifact labels are also fragmented in most periods (cc 0.27–0.90), and they also fail adequacy except in #37 and #25.
- **Exchangeability is the shared assumption that fails.** The natural next model is NCD (or Hubbell) with agent-specific innovation fields. That is a different hypothesis, not a rescue of this one.
- **Window-to-step mapping.** k (model steps per window) is a fitted nuisance. Window aggregation blurs per-step frequency dependence; the simulations calibrate this, but it costs power.
- **Small samples and multiplicity.**
  - 5 free weeks, 6 clusterings, 2 artifact variants, about 9 statistics each.
  - The decisive result (joint PPC p at the simulation floor, 0.002–0.003, in 27/30 free-week fits) survives any correction.
  - The β̂ and P8 tallies do not.
- **#37 and #38 pool two rooms**, which breaks well-mixing; their per-room analysis is not done. #44 uses the #rest room only.
- **NE tests are weak.** NE27 coincides with the #8 → #10 goal change. NE33 has 2 non-holdout post days.
- **Amendments,** with what I had seen when making them:
  - (1) profile synthetic-likelihood fit (instead of moment-only), (2) high-μ downgrade, (3) joint PPC in adequacy. All three were made after the synthetic validation and before any real-data run.
  - (4) The robustness rule became "≥ 2/3 of available clusterings", so that #51 counts with k-means only; made before running #51.
  - (5) #51 is clustered per block rather than whole-period; for runtime, before any #51 result.
  - (6) Post hoc and flagged: the "statistics reproduced" counts and the confirmatory C2 claim, both written after seeing round 1.
  - Before the predictions I had seen H11's results and structural counts only (listed under Prediction).

**Next steps**
1. Add agent fields to the model: NCD and Hubbell with agent-specific innovation, where each agent returns to its own repertoire at rate ρ. This tests whether a small cooperative-copying term remains once private projects are modelled.
2. Merge intention clusters with the artifact a statement names (repo-anchored species), to separate topic fragmentation from project fragmentation.
3. Analyse #37 and #38 per room.
4. Swap in a second embedding model (the planned e5-large-v2 job).
5. Run the frozen #22 test after sign-off.

## Notes
- 2026-10-04: created and launched (S6, HH42; approved 2026-10-03, started 2026-10-04).
- 2026-10-04: observables, nulls and predictions written before any real-data run; synthetic validation and amendments 1–3 appended before the run; exploratory round 1 run on 12 non-holdout periods (+ NE27, NE33 sides) and assembled. Period folders live in `goalperiod-subhypotheses/` (moved there mid-round at Vivian's request).
- 2026-10-04: robustness check on the deterministic shared project labels (`data/processed/shared/project_states.parquet`, requested by the coordinator after H11's tie-breaking was found nondeterministic): same artifact-label verdicts in #31, #37, #44 (window-pair agreement 99.4–99.8%).
