# H75: A thermodynamic speed limit on re-allocation

**Status:** exploratory round 1 **done (2026-10-04): a kickoff that names the target re-allocates the swarm at the speed limit (an instant freeze); a free-choice kickoff settles 5–40× slower with 5–15 switches per net move.** Card, observables and predictions written ~19:10 UTC before any real-data statistic; amendment A1 after the synthetic.
- **Replication (G39, G40, G41, G51):** in 3/4 periods the allocation freezes within 15–30 active min (T_e 0.25–0.5 h) with slack S = ĀT/W of 1.00–1.40: almost every switch moves an agent onto its settled repo, so the re-allocation sits on the Wasserstein bound. G41 (novel research, no shared target) settles in 9.5 h with S 5.1 [1.4, 11.2]. The tail (T_90 2.8–6.3 h) is churn (S_90 4–6) in 3/4.
- **P1 (S ≥ 3) failed 1/4, P3 (T_e in 2.5–10 h) failed 1/4:** the instant-freeze rival R2 wins. HH323's kill condition ("T saturates the bound") is met in 3/4, but the saturation comes from the field naming the target, not from limited switching. The bound itself (P0) holds by construction (no violations).
- **Native G44 (supported):** on the same days and at the same switch rate (3.3 vs 3.4 per agent-hour), the room with a named shared target settles in 0.75 h (S 2.5) and the free-choice room in 4.25 h (S 14.5): ×5.7, against ×0.98 from the activity-limited rival.
- **Native NE38 (mixed):** 11 newcomers settle onto their role repo in a median 0.28 active h (range 0.01–2.5 h); NE38's reassigned agent takes 2.0 h. The cadence elasticity is not measurable (ε +1.3 ± 1.3).
- **P4 cadence elasticity: inconclusive** (pooled ε −0.12 [−2.8, 2.6]; the synthetic showed ε is biased and weakly identified at N ≤ 25). Scorecard A1 B1 C1 D1 E1 F1 G1 H1 I1. `confirm.py` (NE20 DiD; transfer to #45–#47) written and frozen; **not run**.
**Fields:** stat mech, thermodynamics (stochastic), dynamics
**Literature:** [Kolchinsky, Dechant, Yoshimura & Ito 2026](../../literature/kolchinsky-2026-generalized-free-energy-excess-housekeeping.md) (excess EP, Wasserstein speed limits, Eq. "T ≥ (W/Ā) coth(Σ_ex/2W) ≥ W/Ā"); [Aguilera, Ito & Kolchinsky 2026](../../literature/aguilera-2026-entropy-production-nonequilibrium-maxent.md) (EP as statistical irreversibility, no heat bath).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Population N(t) (variant *committing population*, below); Regime; Driving / external field (the kickoff); Agent state, variant *categorical* (here the repo allocation, below); Entropy production / irreversibility (only through the speed-limit inequality). New named variants proposed for DEFINITIONS.md (not edited there; defined under "Operational definitions"): **repo allocation p(t)**, **allocation distance W**, **switch activity Ā**, **settling time T_e / T_90**, **speed-limit slack S**, **activity ratio R**, **agent settling time t_i**.
**From:** HH323 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` ("From the thermodynamics and origins-of-life notes") · **Models:** `physics-models/02-nonequilibrium-ising/`, `physics-models/05-replicator-dissipation/`
**Data inputs (shared tables first):** DQ4 `work_commits` (agent work filter), `calendar` (active windows), `period_units`, `roster`, `call_windows` (call rates), `ground_truth_labels` (#44 room assignment), `embeddings/goals.parquet` (kickoff `win_start`). No text.

## Source HH (verbatim from the HH list)
A thermodynamic speed limit on re-allocation after a goal change. The Wasserstein bound T ≥ W/Ā has three inputs. W is the DQ4 allocation distance between pre-kickoff and settled allocations. Ā is the activity: repo switches per agent per active hour. T is the settling time.
  - *Prediction:* the bound holds in every period, with ≥ 3× slack in ≥ 2/3 of periods. That means settling is limited by the kickoff field (H54 ≈ 5 h, H48 4.5 h), not by how fast agents can switch.
  - *Native:* NE20's cadence change; elasticity of T to call rate ≤ 0.3.
  - *Kill:* T saturates the bound, so settling is activity-limited and cadence would speed it up.
  - *Models:* 02, 05 · *Builds on:* H54, H48, H40 · *Literature:* Kolchinsky et al. 2026

## Question
After a goal change, the agents move their work to new repositories. Is the time this move takes set by how fast agents can switch repos (activity-limited, near the Wasserstein speed limit), or by the kickoff field, with most switches spent on churn (field-limited, far from the limit)?

## Design: two layers (Vivian, 2026-10-04; `infra/data-quality/QUEUE.md`)
- **Replication:** one common estimator on the kickoff of four non-holdout goal periods: G39, G40, G41 (consecutive weekly goals at a fixed roster of 15, regime III, dense git, all with a non-holdout previous week) and G51 (32 agents; its previous week #50 is held out, so only the from-scratch variant W_∅ is available). Period README role: `replication`.
- **Natives (2):** G44 (two rooms with different fields on the same days) and G51 newcomers plus NE38 (single-agent re-allocations from scratch; the exploratory stand-in for NE20). Role: `native`.
- **Confirmation:** NE20 (#45, 06-03) is in the locked holdout; its DiD is written into `analysis/confirm.py` and not run.

## Model
**From:** `physics-models/02-nonequilibrium-ising` (a kinetic, Markov jump process for categorical agent states) and `physics-models/05-replicator-dissipation` (the allocation as a population distribution over strategies that is driven by an external field).

**H75 variant: a mean-field master equation on repos with a Wasserstein speed limit.** Each agent of a period is one copy of a Markov jump process on the set of repos plus a null state ∅ (no work commit yet). The ensemble occupancy p(t) (the share of agents whose current repo is x) obeys ṗ = ∇ᵀj with one-way fluxes j_{x→y}. At the kickoff (t = 0) the field changes and p relaxes from p(0) to a settled allocation p∞. Kolchinsky et al. (2026) give, for any such process,
- **activity** A(t) = Σ_ρ j_ρ (switches per agent per unit time), with 𝒜 = ∫₀ᵀ A dt and Ā = 𝒜/T;
- **Wasserstein distance** W(p(0), p(T)); on a complete graph (any repo can follow any repo) W = TV = ½‖p(T) − p(0)‖₁;
- **finite-time speed limit:** Σ_ex(T) ≥ 2W tanh⁻¹(W/𝒜), hence **T ≥ (W/Ā)·coth(Σ_ex/2W) ≥ W/Ā**.

**What the bound means here (stated before the run).** On the empirical ensemble, with W and Ā measured on the same state sequences, the inequality ĀT ≥ W is a counting identity: to move a share W of the agents, at least NW agents must switch at least once. It can fail only through measurement mismatch (agents entering or leaving the ensemble, states that change without a recorded switch). So "the bound holds" is a consistency check of the scheme, not a test of the physics. The physics is in the **slack** S = ĀT/W:
- **Activity-limited (rival R1, HH323's kill):** every switch moves the allocation toward the target; S ≈ 1–2, and settling time scales as 1/(switch rate), so a faster cadence settles faster (T ∝ r^−1).
- **Field-limited (H75):** agents switch often but mostly in cycles (churn between their own and shared repos, i.e. housekeeping-like currents that carry no net change). S ≥ 3, and T is set by the kickoff field's relaxation time (H54: kickoff excess τ ≈ 5 active h; H48: content settling 4.5 active h), not by cadence.
- **Instant freeze (rival R2):** the kickoff names the artifact (H54: frozen projects), and agents jump to it at their first work commit; T ≈ the first-commit delay (≤ 1 active h), and S is set by churn only after settling.

The thermodynamic content is the implied **minimum excess EP of re-allocation**, Σ_ex,min = 2W tanh⁻¹(W/𝒜) (nats per agent), reported per period. A large S means the swarm pays its re-allocation with little excess irreversibility relative to its switching activity.

## Data scheme (`scheme/build.py`)
- **Inputs:** `work_commits` with the DQ4 agent-work filter (`canonical & ~imported & author_kind == "agent" & ~automated`), `calendar` (`win_start`, `win_end`, `holdout`), `goals.parquet` (`kind == "kickoff"`, `win_start`), `period_units`, `roster`, `call_windows` (`t_call`, agent; summary calls dropped), `ground_truth_labels` (`room_assignment`, #44, `preferred & ~holdout`).
- **Transform:**
  1. **Active time.** Concatenate the period's calendar windows [win_start, win_end] (non-holdout days only); t = 0 at the kickoff `win_start`. A commit outside a window is placed at the nearest window edge (`in_window` false for ≤ 15 min; others dropped and counted).
  2. **Horizon.** The first 20 active hours after the kickoff (5 days × 4 h in G39–G41; 2.5 days × 8 h in G51, before the NE32 joins of 07-09). Same horizon in every period, so periods are comparable phase-diagram points.
  3. **Committing population.** Agents with ≥ 1 agent-work commit in the horizon. Fixed for the horizon (agents absent from the horizon are not in the ensemble).
  4. **Agent state.** s_i(t) = repo of i's latest agent-work commit at or before t. Two initial conditions: **W_pre**: look back into the last 2 active days before the kickoff (only where those days are non-holdout); an agent with no commit there starts at ∅. **W_∅**: every agent starts at ∅ at t = 0 (re-allocation from scratch; available in every period).
  5. **Switch.** A change of s_i between consecutive commits (∅ → repo counts as one switch).
  6. **Occupancy grid.** p(t) on a 15-active-minute grid.
- **Output:** `data/processed/H75-reallocation-speed-limit/<G..>/` with `states.parquet` (agent, t_active, repo code; no repo names), `occupancy.parquet`, `agents.parquet` (t_i, call rate, commit rate), `results.json`; plus `synthetic/` and `_provenance.json`. Expected size < 5 MB.
- **Regimes covered:** regime III only (dense git from #30 on; DQ4 notes that earlier zeros are ambiguous).

## Operational definitions (written 2026-10-04, before any real-data run)
- **Settled allocation** p∞ = mean of p(t) over the last 4 active hours of the horizon ([16, 20] h). **Floor** D_f = median of TV(p(t), p∞) over the same 4 h (fluctuation level of a settled allocation).
- **Distance to settled** D(t) = TV(p(t), p∞).
- **Settling time T_e** = the first grid time with D(t) − D_f ≤ (D(0) − D_f)/e; **T_90** with 0.1 in place of 1/e. Undefined (censored at 20 h) if never reached.
- **Allocation distance** W = TV(p(0), p(T)) at T = T_e (primary) and T_90.
- **Switch activity** Ā = (switches in (0, T]) / (N T), per agent per active hour. **Stationary activity** Ā_ss = the same over [16, 20] h.
- **Speed-limit slack** S = ĀT/W (≥ 1 by construction); **activity ratio** R = Ā_ss T / W (how many times longer the settling takes than if the stationary switching were all directed at the target).
- **Implied minimum excess EP** Σ_ex,min = 2W tanh⁻¹(W/(ĀT)) (nats per agent; infinite when S = 1).
- **Agent settling time** t_i = active time from the kickoff to i's first commit on its settled repo (the repo it occupies for the longest time in [16, 20] h); agents whose settled repo equals their start state (no move needed) or whose settled state is ∅ are excluded. **Call rate** r_i = i's ledger calls per active hour in the horizon; **commit rate** c_i = i's work commits per active hour in the horizon.
- **Cadence elasticity** ε = slope of log t_i on log r_i (OLS, HC1 SE) per period, with log c_i as a control in a sensitivity fit (commits are the only observation of the state, so slow committers look slow to settle). Pooled across replication periods by a random-effects mean (exception (d)), reported next to the per-period slopes.

## Observables
1. Per period: N, W, Ā, T_e, T_90, S, R, Σ_ex,min, D(t) curve, for W_pre and W_∅.
2. The bound check ĀT ≥ W (count of violations; expected 0).
3. Per-agent t_i, r_i, c_i and the elasticity ε.
4. Native statistics (below).

## Null / baseline
- **Activity-limited rival (R1):** S ≈ 1–2, R ≈ 1, ε ≈ −1.
- **Instant-freeze rival (R2):** T_e ≤ 1 active h and t_i ≈ i's first-commit delay.
- **Observation null for ε:** under a field-limited synthetic with commit-observed states (below), the slope of log t_i on log r_i that commit timing alone creates. ε is read against it.
- **Agent bootstrap:** CIs for W, Ā, T, S by resampling agents (B = 200; the agents are the ensemble copies), percentile intervals.

## Native tests (each with its own observable, null and prediction)
- **N1 · G44 (two fields on the same days).** #best (4 agents) is told to fine-tune a leader (one named, shared target); #rest (12) picks its own goals (no shared target). Previous week #43 is held out, so W_∅ only. Observable: T_e, S and Ā per room (room from DQ6 `room_assignment`). #44 has only 16.2 active hours, so its horizon is the whole period (settled window = its last 4 active hours). The activity-limited rival predicts T_rest / T_best = Ā_best / Ā_rest; the field-limited reading predicts that the room with the named target settles at least as fast, whatever its switch rate.
- **N2 · G51 newcomers + NE38 (single-agent re-allocations from scratch).** Each non-holdout newcomer (joins 07-09 … 09-04) starts at ∅ at its first ledger call; t_i = active time from that call to its first commit on its settled repo (modal repo over its first 12 active hours, censored at 09-04). NE38 (07-29): Claude Opus 5's role is reassigned; t = active time from the reassignment to its first commit on its new settled repo. Observable: ε across newcomers (cadence differs by model), median t_i, and NE38's t against the newcomer range. This is the exploratory analogue of the NE20 test (a cadence-only change), which stays in the holdout.
- **Considered and not used:** NE20 (#45; holdout: `confirm.py`); G38 (its kickoff day coincides with NE36 and per-agent goal overrides, so p∞ is agent-specific); NE42 (the merge is goal-confounded; G40 is in the replication layer already).

## Synthetic validation plan (axis F; `analysis/synthetic.py`)
Agents on repos, sampled like the village: N = 15 and 25; a 20-active-hour horizon on 15-min grids; call rates lognormal with SD 0.8 in log units (H40's G51 spread); commits Poisson at rate c_i ∝ r_i^0.5 (median 4 per active hour); the state is observed only at commits. Pre-kickoff: agents on their own old repos plus one shared repo. Scenarios:
- **F (field-limited):** each agent moves to its target at hazard 1/τ_f, τ_f = 5 h, independent of cadence; churn at rate a_i ∝ r_i between the current repo and a side repo (visits of mean 20 min).
- **A (activity-limited):** the same churn, but each switch lands on the target with probability q, so the target hazard is q·a_i (τ ≈ 5 h at median cadence).
- **Z (instant freeze):** every agent moves to its target at its first commit.
Pass criteria: no bound violation in any replicate; S and R separate F from A (median S under F ≥ 2× median S under A); ε recovered within ±0.3 of the truth (0 under F, −1 under A) after the commit-rate control, with ≥ 0.8 power to reject ε = −1 under F at N = 15. If the commit-rate observation makes ε biased by more than 0.3 under F, the real-data ε is read against the synthetic null instead of 0.

## Synthetic validation results (2026-10-04 ~20:00 UTC; `analysis/synthetic.py`, `data/processed/H75-reallocation-speed-limit/synthetic/summary.parquet`)
100 replicates per scenario and size; 20-h horizon; commit-observed states.

| Scenario | N | violations of ĀT ≥ W | T_e (h) | S_e median [q10] | P(S_e ≥ 3) | R_e | ε (t_i) mean ± SD | ε with commit control |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| F field-limited (τ_f 5 h) | 15 / 25 | 0 / 0 | 4.0 / 4.0 | 4.4 [3.0] / 4.8 [3.2] | 0.90 / 0.92 | 4.3 / 4.4 | −0.51 ± 0.43 / −0.56 ± 0.32 | −0.37 ± 0.60 / −0.43 ± 0.38 |
| A activity-limited | 15 / 25 | 0 / 0 | 3.8 / 3.5 | 4.6 [3.0] / 4.6 [3.1] | 0.90 / 0.91 | 4.1 / 4.3 | −0.84 ± 0.42 / −0.88 ± 0.36 | −0.77 ± 0.59 / −0.76 ± 0.47 |
| Z instant freeze | 15 / 25 | 0 / 0 | 0.5 / 0.5 | 1.15 [1.0] / 1.15 [1.0] | 0 / 0 | 0.44 / 0.45 | −0.15 ± 0.54 / −0.11 ± 0.37 | +0.38 / +0.39 |

- **Bound:** no violation in 600 replicates, as expected for a counting identity.
- **Slack does not discriminate field from activity limitation** (pre-set criterion "median S under F ≥ 2× under A" **failed**: 4.4–4.8 vs 4.6). With churn present, both give S ≈ 4.5. S and R separate churn-dominated settling (F, A) from an instant freeze (Z: S ≈ 1.15, T_e ≈ 0.5 h).
- **Cadence elasticity is biased and weakly identified** (criterion "recovered within ±0.3 after the commit control, power ≥ 0.8 to reject −1 under F" **failed**: bias −0.4 to −0.5, power 0.19–0.36). Churn that scales with cadence makes fast agents reach a side repo early, and slow committers are seen late. The control and an interval-midpoint settling time (`t_mid`) do not remove it.

## Amendments (dated; what had been seen)
- **A1 (2026-10-04 ~20:05 UTC, after the synthetic run, before any real-data statistic).** (i) P1 and P2 are read as tests of churn-dominated settling against the instant-freeze rival R2 only; they cannot separate field from activity limitation. (ii) P4 is read against the synthetic means, not against 0: *field-like* if the random-effects 95% CI of ε (t_i, no control) excludes −0.86 (the A mean); *activity-like* if it excludes −0.53 (the F mean); *inconclusive* otherwise. The commit-control fit and `t_mid` are sensitivity checks. (iii) The synthetic commit rates carry a lognormal scatter (SD 0.5) at fixed cadence; without it the commit control is collinear with log r. (iv) The per-period verdict rule is unchanged, but "supported" now means "churn-dominated, not instant freeze".

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R1 activity-limited settling (S ≈ 1–2, T ∝ 1/cadence); R2 instant freeze at the first commit (H54 frozen projects).
**Locked holdout used for confirmation:** none yet. `analysis/confirm.py` (NE20 DiD #44 → #46/#47; transfer to #45–#47) is written and frozen; not run.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Allocation = repo of each agent's latest DQ4 agent-work commit; W = TV on the complete graph; Ā from recorded switches; active hours from calendar windows. The state is observed only at commits, and a W_∅ start counts every first commit as a move (upper bound on W). Regime III only. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Markov jump on repos and exchangeable agents assumed; the speed limit is exact for the empirical ensemble (a counting identity), so no Markov test is needed for P0. Settling times are grid-limited at 0.25 h in the freeze periods. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | S and T separate the instant-freeze rival from churn-dominated settling (synthetic Z vs F/A); the real periods fall on both sides (S 1.0–1.4 vs 5.1). No held-out data: one kickoff per period. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | P1 and P3 failed in 3/4 periods (R2 instant freeze); the churn tail (S_90 ≥ 4 in 3/4) and the room contrast in G44 (×5.7 at equal Ā) were predicted by the field-limited reading. P4 not identifiable. |
| E interventional | predicts the change across a natural experiment | 1 | G44: two fields on the same days (quasi-intervention) consistent with field-limited settling. Newcomers and NE38: single-agent quenches, fast. NE20 (cadence) is held out (`confirm.py`). |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Synthetic at village sampling: no bound violations in 600 replicates; S identifies freeze vs churn but not field vs activity (both ≈ 4.5); ε biased (−0.5 under the field-limited truth) with power 0.2–0.4. |
| G ground truth | agrees with known structure | 1 | Consistent with H54 (kickoffs freeze onto the projects they name; 9/13 frozen projects). DQ6 room assignment for G44; DQ6 role rows date NE38. |
| H comparative | beats the named rivals | 1 | R2 (instant freeze) beats the field-limited model in 3/4 replication periods; the activity-limited rival R1 fails the G44 contrast (×0.98 predicted vs ×5.7 observed) but is not separable from the field-limited model on S alone. |
| I transfer | holds in other same-mode periods, including the holdout | 1 | Four regime-III kickoffs and two natives; freeze in 3/4. Holdout not run. |

## Prediction
*Written 2026-10-04 ~19:10 UTC, before running the analysis on real data. What I had seen: per-goal counts of work commits, repos and committing agents (structure only); the round-1 cards of H40, H48, H54 and H14. No allocation, switch or settling statistic.*
- **P0 (scheme check).** ĀT ≥ W in every period and variant. A violation is a scheme error, not physics.
- **P1 (slack; replication, primary).** S(T_e) ≥ 3 in ≥ 2/3 of the replication periods, for W_pre where available (G39–G41) and W_∅ in G51. *Against:* S ≤ 2 in ≥ 2/3 (activity-limited). Credence 0.6.
- **P2 (activity ratio).** R ≥ 3 in ≥ 2/3 of periods: the stationary switching would carry the move in a third of the observed time. *Against:* R ≤ 1.5. Credence 0.5.
- **P3 (time scale).** T_e lies in [2.5, 10] active h (within ×2 of H54's 5 h) in ≥ 2/3 of periods. *Against (R2):* T_e ≤ 1 h in ≥ 2/3. Credence 0.35: repos may freeze at the first commit (H54: 9/13 frozen projects carry the goal's words).
- **P4 (cadence elasticity; replication).** Random-effects mean ε (with the commit-rate control) has its 95% CI inside [−0.3, 0.3] read against the synthetic observation null, and excludes −1. *Against:* CI includes −1 and excludes 0. Credence 0.55.
- **N1 (G44).** T_e(#best) ≤ T_e(#rest), and the activity-limited prediction T_rest/T_best = Ā_best/Ā_rest misses by ≥ ×2 or has the wrong sign. Weak (4 agents in #best). Credence 0.45.
- **N2 (G51 newcomers + NE38).** ε across newcomers has |ε| ≤ 0.3 at the point estimate (CI expected wide, n ≈ 10); median newcomer t_i ≤ 10 active h; NE38's t inside the newcomer range [min, max]. Credence 0.4.
- **Per-period verdict rule (replication):** *supported* if S ≥ 3 and the agent-bootstrap 95% lower bound of S ≥ 2; *failed* if S ≤ 2; *mixed* otherwise; *n/a* if T_e is censored or N < 5.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | failed | N 14; T_e 0.25 h; W 0.79; S 1.00 [1.00, 1.00]; T_90 2.75 h, S_90 1.15 (instant freeze) |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | failed | N 13; T_e 0.5 h; S 1.25 [1.0, 12.7]; T_90 4.5 h, S_90 5.9 (freeze, churn tail) |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | mixed | N 13; T_e 9.5 h; S 5.1 [1.4, 11.2]; R 6.9; T_90 16.5 h, S_90 8.9 (churn) |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication | failed | N 16 (W_∅); T_e 0.5 h; S 1.40 [1.0, 3.9]; T_90 6.25 h, S_90 4.0 |
| [G44](goalperiod-subhypotheses/G44/README.md) | native | supported | #best T_e 0.75 h, S 2.5 vs #rest 4.25 h, S 14.5 at Ā 3.3 vs 3.4/h; activity rival ×0.98, observed ×5.7 |
| [NE38](goalperiod-subhypotheses/NE38/README.md) | native | mixed | 11 newcomers: median t_i 0.28 h (0.01–2.5); ε +1.3 ± 1.3; NE38 agent 2.0 h (inside range) |

## Results
### Exploratory round 1 (2026-10-04; `scheme/build.py`, `analysis/run.py`, `analysis/synthetic.py`)
Numbers: `data/processed/H75-reallocation-speed-limit/results/summary.json`, `G<NN>/results_*.json`, `synthetic/summary.parquet`. Figures: `figures/summary_obs.pdf` (relaxation curves; slack vs settling time), `figures/synthetic_compact.pdf`.

**Outcome vs prediction**
| Prediction | Observed | Verdict |
| --- | --- | --- |
| P0 ĀT ≥ W | no violation in any period or variant (counting identity) | holds (scheme check) |
| P1 S(T_e) ≥ 3 in ≥ 2/3 | 1.00, 1.25, 5.09, 1.40 (1/4) | **failed**: instant freeze |
| P2 R ≥ 3 in ≥ 2/3 | 0.01, 0.00, 6.9, 0.31 (1/4) | failed |
| P3 T_e in [2.5, 10] h in ≥ 2/3 | 0.25, 0.5, 9.5, 0.5 h (1/4) | **failed**: R2 (T_e ≤ 1 h) in 3/4 |
| P4 pooled ε vs synthetic F/A | −0.12 [−2.83, 2.59] (τ 2.0) | inconclusive |
| N1 G44 named-target room settles faster at equal Ā | ×5.7 vs activity rival ×0.98 | supported (4 agents in #best) |
| N2 newcomers \|ε\| ≤ 0.3; median ≤ 10 h; NE38 in range | ε +1.32; 0.28 h; 2.03 h in [0.01, 2.46] | mixed |

**What it means.**
1. *The speed limit is saturated, but by the field.* When the kickoff names an artifact (G39 "build your world", G40 "connect your worlds", G51 private roles, G44 #best), each agent's first post-kickoff commit lands on its settled repo. The move costs one switch per moved agent (S = 1.0–1.4), so the re-allocation runs at the Wasserstein bound T = W/Ā, and the implied minimum excess EP 2W tanh⁻¹(1/S) diverges as S → 1: the move is absolutely irreversible. T_e is then the first-commit delay (15–30 active min), far below H54's 5-h content settling.
2. *Without a named target the swarm churns.* G41 and G44 #rest settle in 4–10 active h with 5–15 switches per net move: cyclic, housekeeping-like currents between repos. This is the field-limited regime that HH323 expected everywhere.
3. *The slack is a gauge of field specificity, not of activity limits.* At equal switch rates (G44) the settling time differs ×5.7 between the rooms. The synthetic shows S cannot tell field from activity limitation once churn exists; the G44 contrast can.
4. *Cadence:* not testable with these ensembles (ε SE 0.7–4.6). NE20 in the holdout is the test.

## Confirmatory predictions (C-*): for the locked holdout, frozen 2026-10-04 after round 1, not run (`analysis/confirm.py`)
- **C1 (NE20 first stage):** |DiD in mean log call rate| (Anthropic − others, kickoff #44 → kickoffs #46, #47) ≥ 0.10; otherwise C2 is not scored.
- **C2:** cadence elasticity ε = DiD log t_i / DiD log r_i has |ε| ≤ 0.3 and the DiD log t_i CI contains 0. Kill: ε ≤ −0.7 with the CI excluding 0 (activity-limited).
- **C3 (transfer, #45, #46, #47, W_pre):** S_e ≤ 2 with T_e ≤ 1 h (instant freeze) in ≥ 2 of 3, and S_90 ≥ 3 (churn tail) in ≥ 2 of 3.
- Reuse: #45–#47 are planned or used by H04, H30, H35, H40 (H40 uses the same NE20 first stage with a reply outcome). H75's outcome (DQ4 commits) is a different statistic and modality; `confirm.py` calls `holdout_ledger.check` and requires a clean git state.

## Round 2 redirects
**What the direction is really after:** an operator rule for how fast a swarm can be re-pointed, and whether the limit is the field, the agents' switching, or their cadence.
- **H75-R1. Kickoff text vs slack across all regime-III kickoffs.** Score each kickoff for a named artifact (H54's specificity or a DQ4 repo named in the kickoff) and test S and T_e against it (here: 4 named → 3 freezes; 2 free → 2 churn).
- **H75-R2. A denser allocation channel.** Use `artifact_mentions` (actions touching repos, ~25× denser than commits) to resolve T_e below 15 min and to measure ε with less observation lag.
- **H75-R3. Excess EP of re-allocation.** Estimate Σ_ex of the repo process directly (H76's estimator on the top-k repos plus "other") and test Σ_ex ≥ 2W tanh⁻¹(W/𝒜) as an inequality on measured quantities, not only as an implied bound.
- **H75-R4. Run confirm.py** (NE20 DiD and transfer).

## Notes
- 2026-10-04: compute limits: ≤ 2 threads per process, no sub-agents, no network. The full run takes ~4 s.
- 2026-10-04: no H75 script reads `activity_bins`; the DQ8 event-drop bug does not apply. Commits outside a day's window ± 15 min: none in the four periods.
- 2026-10-04: G39's W_pre and W_∅ results are identical: no pre-kickoff repo survives into the settled allocation, so the TV distance is the same from "old repos" as from ∅.
- 2026-10-04: the native named "NE38" in the period table holds both the G51 newcomer quenches and the NE38 reassignment (one native test).
- 2026-10-04: processed data 0.3 MB.
