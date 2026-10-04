# H04: External forcing reshapes the response kernel, reversibly

**Status:** **confirmatory run on the locked holdout (2026-10-03): C1 FALSIFIED, in the opposite direction.** The branching ratio n is *higher* on 8 h days at all three hours switches; the ABAB contrast is at the edge of week-to-week noise. C2 is inconclusive, C3 untestable, C4 (NE23) partial with a failed manipulation check, and MF-C indistinguishable from week-to-week variation. Exploratory round 1 (non-holdout) found real but delayed nudge responses (Results). See [NE21/README.md](goalperiod-subhypotheses/NE21/README.md).
**Fields:** dynamics, stat mech, sociophysics
**Literature:** none of the notes in `literature/` covers linear response; the references are in the model folders: Cugliandolo, Kurchan & Peliti, *PRE* 55, 3898 (1997)† (`physics-models/02-nonequilibrium-ising`, effective temperature); Crane & Sornette 2008† and Filimonov & Sornette 2015† (`physics-models/09-hawkes`).
**Definitions used:** Regime; Driving / external field; Activity time (here: minutes since the day's empirical window start); Action; Interaction (broadcast) for bystanders; Population N(t). New operational terms are defined below (activity n, kick, Green's function G, FD ratio X).
**Shortlist / ideas:** S3 (`../promotion-shortlist.md`); HH46 (hours and Hawkes), HH31 (nudger reversal), with HH14 (humans as bath) and HH18 (nudger and the FD ratio) as side readings.

## Question
Do outside kicks (nudger messages, human messages, goal kickoffs) act on the swarm through a well-defined linear response kernel G(τ)? If they do, does changing the forcing regime (hours 4 → 8 → 4 → 8 h, NE21; nudger off/on, NE23) reshape that kernel and the swarm's branching ratio **reversibly**, and how far is the swarm from equilibrium by the fluctuation–dissipation (FD) yardstick?

## Model
**From:** `physics-models/02-nonequilibrium-ising/` (response function, susceptibility, FD ratio and effective temperature) and `physics-models/09-hawkes/` (exogenous and endogenous kernels, branching ratio n).

Two views of the same propagator:
1. **Minute-binned response (model 02 view).** Agent i's activity n_i(m) ∈ {0, 1} per minute; a kick at minute m₀ is a field pulse. G(τ) = E[n_i(m₀+τ) | kick] − E[n_i(m₀+τ) | matched no-kick control]. G is the response function R up to the kick's (unknown) strength; the kick strength is calibrated in **log-odds units** (the kinetic-Ising field): h = logit p_kick(τ=1) − logit p_ctrl(τ=1).
2. **Event-level Hawkes (model 09 view).** Village-level agent chat messages (`chat_core`, speaker_kind = agent, which includes the Claude Code agent's chat), binned at 10 s within each day's window:
   λ(t) = μ_d · b(tod) + Σ_talk φ_endo(t − t_k) + Σ_{c ∈ {human, nudge}} η_c Σ_{kicks of class c} γ_c e^{−γ_c (t − t_j)},
   with φ_endo a sum of two normalized exponentials, n = ∫φ_endo (branching ratio), μ_d per day, b(tod) a 4-step daily profile (mean 1). η_c = expected talk events directly triggered by one kick. Fitted by maximum likelihood (profiled μ_d).

## Data scheme (`scheme/`, `analysis/`)
Uses the shared tables only (`data/processed/shared/`); no raw rescans.
- **Inputs:** `activity_bins` (state per agent-minute), `chat_core` (speaker kind, mentions), `kicks` (goal kickoffs), `exposure` (room recipients per message), `events_core` (AGENT_TALK times), `calendar` (windows, regime, documented hours, holdout), `roster`.
- **Mapping (checked on non-holdout structure before any response was computed):**
  - **Activity:** n = 1 if `activity_bins.state` ∈ {3 act, 4 talk}, else 0 (silent or idle, idle including declared pauses). Secondary: talk only (state 4).
  - **Nudge:** an `automated` message that names ≥ 1 agent on that day's roster. `automated` also carries the daily "pausing / resuming the village for today" bookends (no valid mentions); these are excluded. **The mention parser adds a spurious `o1` (left 2025-04-16) to every nudge**, so targets are the mentions restricted to the day's roster. Nudge text format: "@Target — based on your recent activity … *This is an automated nudge triggered by: [repeated-idling]*".
  - **Targets / bystanders:** targets = valid mentions; bystanders = the message's `exposure` recipients (room occupants) minus targets.
  - **Human message:** `speaker_kind == human`. Responders = `exposure` recipients, split into mentioned vs. unmentioned.
  - **Goal kickoff:** goal start time. All 51 kickoffs fall *before* the day's window opens, so a kickoff is a step applied to everyone at day start; its response is measured against matched non-kickoff days (step response), not within the day.
  - Only kicks inside a day's window are used; the response window is τ ∈ [−30, +60] min, τ = 0 being the kick minute (partly post-kick; excluded from amplitudes).
- **Matched controls:** agent-minutes with no message kick (human or nudge) reaching that agent (room or mention) in [m − 30, m + 60], from non-holdout days of the same regime. Strata: regime × agent × state at m − 1 × active minutes in [m − 15, m − 1] (0, 1–3, 4–9, 10–15) × idle minutes in [m − 15, m − 1] (0, 1–7, 8–15) × tercile of the day window. A treated cell whose stratum has < 20 controls falls back to the same stratum without agent identity; the fallback share is reported. Placebo: G over τ ∈ [−30, −16] (outside the matched pre-window) must be ≈ 0. *[Revised during exploration, before any holdout use: eligibility and isolation are on direct kicks only, and the bystander-exposure count is a matching stratum; see Results, "Design changes".]*
- **Output:** `data/processed/H04-reversible-forcing/` (`explore_*.json`: kernels with curves, linearity, FD, MF, kickoffs, Hawkes, NE10, placebo switches; `dryrun_ne21_ne23.json`; 1.6 MB in total) with `_provenance.json`.
- **Regimes covered:** I, II, III (`calendar.regime`), non-holdout days only (`calendar.holdout == False`); within III, 4 h vs. 8 h days as an exploratory proxy for NE21.

## Observables
- **G(τ)** per kick type × responder group × regime; amplitude A30 = Σ_{τ=1}^{30} G(τ) (excess active minutes per responder per kick), A60, peak lag, 1/e relaxation time; day-block bootstrap CIs (treated resampled by day; control means fixed).
- **Linearity tests** (verdict rules fixed here):
  - **Dose:** clusters of n kicks within 2 min (near-simultaneous) vs. single isolated kicks: r(n) = A(n) / (n · A(1)).
  - **Superposition:** a second kick 3–20 min after the first (repeat nudges to the same target; pairs of human messages in a room): S = A_obs / A_pred, with A_pred from G₁(τ) + G₁(τ − δ).
  - **Time translation:** A30 for kicks in the first vs. last third of the day window, and Monday vs. Tue–Thu vs. Friday.
  - **Rule for each ratio:** *pass* if the point estimate is in [0.67, 1.5] and its 95% CI contains 1; *fail* if the whole CI lies outside [0.67, 1.5]; otherwise *inconclusive*. **G is a valid description** of a kick type if no test fails and at least two pass.
- **Fluctuation vs. response:**
  - **CKP form (primary T_eff).** χ(τ) = Σ_{s=1}^{τ} G(s)/h against C(0) − C(τ), where C is the connected autocorrelation of n for the same responder agents (per agent-day centering, kick-free minutes). Convention: with logistic pulse fields, a reversible two-state (first-order Markov) agent gives χ(τ) = (1 + λ)[C(0) − C(τ)], λ = C(1)/C(0). Hence X(τ) = χ(τ) / [(1 + λ)(C(0) − C(τ))], with X ≡ 1 for that reversible reference, and **T_eff = 1/X**. Reported: X_fast = X(1) and X_slow = least-squares slope of χ vs. (1 + λ)[C(0) − C(τ)] over τ ∈ [5, 30].
  - **Onsager regression (selection-robust check).** Align on the responder's first activation within 10 min after a kick, vs. spontaneous activations (no kick in [−30, +60]) with matched pre-history; ratio of the integrated activity over the next 30 min, kicked / spontaneous. Ratio 1 = the kick only times the activation (a pure field on the next step); > 1 = the kick changes the agent's state (persistent); < 1 = more transient than a spontaneous activation. *[Reported in exploration in its excess form X(τ) = Σ(E_kick − E0)/Σ(E1 − E0), with E0 the matched no-activation baseline (so X = 1 for a pure one-step field), plus the raw ratio; T_eff = 1/X(30).]*
- **Hawkes:** n, η_human, η_nudge and their decay times per regime (and per 4 h / 8 h class in III); day-blocked CV against an inhomogeneous Poisson null (same μ_d · b(tod)); time-rescaling KS; synthetic recovery.
- **NE10 (nudger switch-on, 2026-02-10), exploratory:** idle fraction, idle-run escape hazard, active fraction, n before vs. after. Pre-period available: #27 (2026-01-12 → 01-23) and 2026-02-09 (#30 day 1); #28 and #29 are held out. Post: 02-10 → 02-20 (#30, #31).

## Null / baseline
- **Matched no-kick controls** (above) for every G; placebo pre-window.
- **Hawkes:** inhomogeneous Poisson with the same per-day level and daily profile (the time-varying-field null); Hawkes without exogenous kernels.
- **FD:** the reversible first-order Markov reference (X ≡ 1).
- **Reversal (confirmatory):** monotone drift across the four NE21 segments (the falsifier in S3).

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** (a) no-kernel time-varying field (kicks are epiphenomenal; activity follows the schedule); (b) pure exogenous Poisson (n = 0); (c) state-reset / threshold response (kicks flip agents out of idle traps nonlinearly: no dose linearity, no superposition).
**Locked holdout used for confirmation:** NE21 + NE23 window (2026-06-08 → 07-06; #46–#50) and #45 (as the pre-switch 4 h segment). Not used yet.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Kick mapping checked on structure (bookends, spurious `o1`, targets always in the room). The kinetic-Ising mapping "kick = field on activity" **fails** (h ≈ 0 at τ = 1; FDT shape). Family invariance not tested |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Hawkes time-rescaling KS 0.008–0.020 vs. Poisson 0.037–0.071 (improved, still formally rejected at N ≈ 10⁴–10⁵). Time translation: weak pass for nudges. The one-step (Markov) field assumption fails; week-to-week nonstationarity of n is large (placebo \|Δn\| median 0.12) |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Hawkes beats the time-varying-field Poisson null in day-blocked 5-fold CV (I: +0.050, III: +0.066 nats/event, 5/5 folds). Matched G beats the no-kick null for nudges (III) and human messages (I) with clean placebo windows. Family-field and autocorrelation-preserving nulls not run |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | MF forward prediction of the kernel decay **fails** (5–26×); FDT signature absent. MF self-consistency (τ_m vs. τ₀/(1−K)) holds. Hawkes η_nudge decay (~12 min) independently matches the delayed G |
| E interventional | predicts the change across a natural experiment | 0 | NE10 exploratory: thin, not supported. **NE21 holdout (2026-10-03): predicted sign falsified** (n higher on 8 h days at 3/3 switches); NE23 manipulation check failed |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Hawkes recovery: n biased low by 0.03–0.06, η_nudge wide. G robust to isolation window, strict isolation and matching fallback (nudge A30 0.97–1.54, all > 0). K is detrending-sensitive (×2) |
| G ground truth | agrees with known structure | 1 | Nudge responses sit on the named target, not on bystanders; mentioned agents respond immediately. The first non-holdout nudge is on 02-13, three days after the CHANGELOG's 02-10 |
| H comparative | beats the named rivals | 1 | Beats rivals (a) no-kernel field and (b) n = 0. Does **not** beat (c) state-reset / hidden-state: delayed responses and Onsager X > 1 favor (c) over a field |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Holdout used for NE21/NE23: kernel comparisons inconclusive (wide CIs); T_eff untestable |

## Prediction
*Written 2026-10-03, before any response, kernel, autocorrelation or Hawkes fit was computed on real data.* What had been looked at: kick counts by kind/regime/holdout, the template of non-holdout automated messages (8 nudge texts read in full to check the target mapping; one of them says the agent "took one action but then settled back into low-noise mode", which nudges my prior toward transient nudge responses), roster dates, and calendar metadata (dates, documented hours, goal numbers) for the NE21/NE23 design.

### Exploratory (non-holdout), round 1
- **P1 nudge → target.** G_target > 0: A60 has a 95% CI excluding 0; peak lag ≤ 5 min; 1/e relaxation time between 3 and 30 min (a transient burst, not a lasting change).
- **P2 nudge → bystanders.** Small spillover: 0 ≤ A60(bystander) / A60(target) ≤ 0.2.
- **P3 human messages.** G > 0 for room occupants (A60 CI excludes 0); mentioned agents respond at least 2× more than unmentioned occupants; per-responder A60 larger in regime I than in III (in III agents are almost always busy, so a message has less headroom).
- **P4 goal kickoff (step).** Kickoff days show more activity than matched non-kickoff weekdays in the first 60 min of the window (≥ 10% relative excess), with no significant difference after 2 h.
- **P5 linearity.**
  - Dose: sublinear, r(n ≥ 3) < 0.67 for human messages (fail); r(2) within [0.5, 1.0].
  - Superposition: sub-additive, S between 0.5 and 0.9 for human-message pairs and for repeat nudges (habituation to the second nudge).
  - Time translation: passes for nudges and human messages (early/late and weekday ratios in [0.67, 1.5]).
  - **Verdict predicted:** G is a valid description for isolated nudges and isolated human messages (low dose) but not for bursts; for goal kickoffs only the step response is defined (dose and superposition untestable).
- **P6 FD.** FDT is violated for every kick type with enough data (X_slow 95% CI excludes 1). For nudges, X_slow < 1 (T_eff > 1: the response decays faster than spontaneous fluctuations) and the Onsager ratio < 1 (nudge-triggered activations are more transient than spontaneous ones). For human messages, the Onsager ratio ≥ 1 and T_eff is closer to 1 than for nudges. T_eff differs between regimes I and III beyond its CI (direction not predicted).
- **P7 Hawkes.** In each regime, the Hawkes model beats the inhomogeneous Poisson null on held-out days (day-blocked CV, Δ log-likelihood > 0 per event); 0.3 < n < 0.9; 0.3 ≤ η_nudge ≤ 3 talk events per nudge; η_human ≥ η_nudge. Synthetic recovery of n within ±0.05.
- **P8 hours proxy (regime III, non-holdout; HH46).** n on 8 h days is lower than on 4 h days by ≥ 0.05. Confounded by era and roster (4 h days are Mar–May 2026, 8 h days are Jul–Aug 2026); exploratory only.
- **P9 NE10 (exploratory).** After switch-on, the escape hazard from idle runs ≥ 10 min rises by ≥ 20% and the idle fraction falls, while the active fraction changes by < 10% relative and n changes by < 0.1 (the nudger acts as a field on the idle tail, not as a coupling). An "untestable" outcome is acceptable given the thin pre-period.

### Confirmatory (locked holdout; `analysis/confirm_ne21_ne23.py`, not run)
Segments by documented hours: **A1** = 4 h, #44–#45 (2026-05-26 → 06-05); **B1** = 8 h, 06-08 → 06-12 (weekdays); **A2** = 4 h, 06-15 → 06-26; **B2** = 8 h, 06-29 → 07-03. NE23: **off** = the 06-13 Saturday-evening session (#best agents only, nudger disabled), against **on** = B1 and A2 for the same agents.
- **C1 (HH46, reversal of n).** n(B1) < n(A1), n(B1) < n(A2), n(B2) < n(A2): the sign of Δn flips at every switch, each |Δn| ≥ 0.05. **Falsifier:** a monotone drift in n across A1, B1, A2, B2 (S3's "no reversal"), or fewer than two of the three switches with the predicted sign.
- **C2 (kernel per kick is invariant to hours).** A30 per responder for nudge targets and for human-message occupants agrees between 4 h and 8 h segments within ±30%; the hours change the baseline and n, not the per-kick propagator.
- **C3 (T_eff reverses).** The sign of ΔT_eff (X_slow-based, for nudges and for human messages) alternates across the three switches (direction not predicted). A monotone trend falsifies reversibility.
- **C4 (NE23, nudger off/on).** Manipulation check: zero nudges on 06-13. For #best agents, the idle fraction and the mean idle-run length are higher in the off session than in B1 and A2; on resumption, G_target's A30 in A2 is within ±30% of B1's; |n(off) − n(B1)| < 0.1 (the nudger is a field, not a coupling).
- **Amendment (2026-10-03, after exploratory round 1, before any holdout data was touched):** exploration showed the CKP T_eff is not identifiable here (the log-odds field h at τ = 1 is consistent with 0 in every suite, because responses are delayed by ~5–20 min). **C3 therefore uses the Onsager T_eff = 1/X(30)** (first-activation-aligned, see Observables), with the same reversal rule; the CKP numbers are still reported. C2 and C4 compare A30 (not A60). The script also reports H04-MF per segment (MF-C below).
- **Amendment 2 (2026-10-03, after the placebo-switch analysis on non-holdout data, before any holdout data was touched):**
  - **The noise floor.** Between *adjacent same-hours non-holdout weeks*, the Hawkes n moves a lot (`analysis/placebo_switch.py` → `explore_placebo_switch.json`): |Δn| median 0.12, 90th percentile 0.43 (III, 17 pairs). Over runs of four adjacent same-hours weeks (32 runs, 13 in III), the *ABAB contrast* D = (w1 + w3)/2 − (w2 + w4)/2 has |D| 95th percentile **0.42 for n, 0.20 for a₁ (fast part), 0.12 for K**. The original |Δn| ≥ 0.05 threshold is far inside this noise.
  - **C1 is therefore judged on the ABAB contrast:**
    - *supported* if D_n = (n_A1 + n_A2)/2 − (n_B1 + n_B2)/2 > 0.42 and ≥ 2 of the 3 switches have the predicted sign;
    - *falsified* if fewer than 2 switches have the predicted sign or n drifts monotonically across A1, B1, A2, B2;
    - otherwise *not distinguishable from week-to-week variation*;
    - the same is reported for a₁ (threshold 0.20) as a secondary.
  - **MF-C** uses the same rule with D_K and threshold 0.12.
  - **Power note.** Detecting an hours effect on n needs a contrast ≳ 0.4, i.e. a change of more than half of n itself. A null C1 result will mostly mean "underpowered", not "no effect". C3 may be untestable: the 4 h segments are expected to hold only ~15–20 isolated nudge targets, below the 10-activation floor.
  - Exploration also hints at the opposite of MF-P4 / C1 (n and K slightly *higher* on 8 h days, era-confounded). The confirmatory predictions are left as written (they are S3/HH46's hypotheses).
- **Known confounds (stated before running):** every switch coincides with a goal change (#46, #47, #50); 06-11 changes the default pause from 12 h to 5 min and caps unseen events (NE22) inside B1; 06-03 disables parallel tool use (inside A1); 06-29 migrates GitHub → GitLab (NE24) at the B2 switch; 06-13 is a Saturday evening with only #best agents and a special event. The script reports B1 split at 06-11 as a sensitivity check.

## Sub-hypothesis H04-MF: mean-field Glauber predicts the response decay (HH81)
Added 2026-10-03 at the user's request (via the coordinator), after exploratory round 1 of the main card had been run (see the disclosure below). Light, forward-only; no J matrix. Model: `physics-models/02-nonequilibrium-ising/`, "Mean-field forward version"; fluctuation inversion as in HH80.

**Model.** Spins s_i = 2n_i − 1 per agent-minute. Mean-field Glauber, τ₀ dm/dt = −m + tanh(β(J₀m + h)), linearized: τ = τ₀ / (1 − K), with the loop gain K ≡ βJ₀(1 − m²). Curie–Weiss inversion from fluctuations, with heterogeneous single-agent fields (the independent-agent baseline is Σ_i Var(s_i), not N(1 − m̄²)):
  VR = Var(Σ_i s_i) / Σ_i Var(s_i) = 1 / (1 − K)  ⇒  K = 1 − 1/VR.

**Operational definitions (fixed before computing).**
- **Detrending (the time-varying field):** each agent's s_i(t) minus its centered 61-min moving average within the day (removes the schedule and other fields slower than ~1 h; H09 E1 showed the raw landscape is schedule-driven). Sensitivities: per agent-day centering only; the homogeneous form N·Var(m)/(1 − m̄²).
- **τ₀:** 1/e time (linear interpolation) of the pooled single-agent autocorrelation of the detrended s_i. Secondary: integrated time Σ_{τ=0}^{30} c(τ)/c(0) − ½.
- **τ_m:** the same 1/e time for the collective X(t) = Σ_i x_i(t).
- **Measured kernel decay τ_G:** 1/e relaxation time after the (3-point smoothed) peak of G(τ); secondary: effective width A60 / peak. Day-bootstrap CIs. Kernels: human message → room (human_all_iso, a field on all occupants: the collective mode), nudge → target (nudge_target_iso, a single-spin field), human message → mentioned agent.
- **Verdict rule:** MF "predicts" a decay time if the 95% CI of τ_G / τ_pred overlaps [0.5, 2]; fails if the CI lies entirely outside.

**Disclosure.** When these predictions were written I already knew from the main round that the single-agent C(1)/C(0) ≈ 0.3–0.4 (so τ₀ ≈ 1 min), that the G curves peak at ~10–20 min and relax over ~5–30 min, and (from H09 E1) the raw, undetrended variance ratios 1.25 (I) and 1.61 (III). The MF-P2 outcome is therefore largely anticipated; the test's value is in quantifying the gap and in MF-P3, which uses quantities not yet computed.

**Predictions (written 2026-10-03, before any K, τ₀, τ_m or τ_G was computed):**
- **MF-P1.** Detrended K lies in [0.05, 0.5] in regimes I and III (subcritical; 1/(1 − K) ≤ 2). K in III exceeds K in I.
- **MF-P2 (the forward test).** τ_pred = τ₀/(1 − K) *underpredicts* the measured kernel decay by a factor ≥ 3 for every kick type with a significant response, in every regime: mean-field Glauber with fluctuation-inferred coupling does not predict the kernels (the responses are delayed and slow, consistent with a hidden channel). A ratio CI overlapping [0.5, 2] would count against this prediction and for HH81.
- **MF-P3 (fluctuation-only self-consistency).** τ_m / τ₀ agrees with 1/(1 − K) within a factor 2 in regimes I and III.
- **MF-P4 (hours proxy).** In regime III, K on 8 h days < K on 4 h days (activity spreads out; HH46 in mean-field form).
- **Confirmatory (in `confirm_ne21_ne23.py`, not run).** K, τ₀, τ_pred and τ_G per NE21 segment; the sign of ΔK flips at each switch (lower on 8 h segments), and MF-P2's gap persists in every segment.

## Results by goal period
One folder per goal period (`G<NN>/`) or spanning natural experiment (`NE<NN>/`), each with its verdict; the cross-hypothesis table is [../OVERVIEW.md](../OVERVIEW.md). Round 1 pooled by regime; per-period kernels and n are a round-2 task (per-goal-period rule). NE21 is the confirmatory test.

## Results
### Exploratory round 1 (2026-10-03; non-holdout days only; EXPLORATORY, not confirmation)
Code: `analysis/h04lib.py` (machinery), `analysis/explore.py` (G, linearity, FD, MF, kickoffs), `analysis/hawkes.py` + `analysis/hawkes_explore.py` (Hawkes), `analysis/ne10.py`, `analysis/figures.py`. Numbers: `data/processed/H04-reversible-forcing/explore_*.json`. Figures: `figures/kernels.pdf`, `fd.pdf`, `kickoff_step.pdf`, `mf_forward.pdf`, `hawkes.pdf`. Suites: I (180 days, 2025-05-10 → 2026-02-20), II (9 days), III (93 days; 48 at 4 h, 45 at 8 h). CIs are 95% day-block bootstraps (1,000 resamples for kernels; 40 day-resampled refits for Hawkes).

**Design changes made during exploration (all before any holdout data):**
1. *Isolation on direct kicks.* Strict isolation (no message of any kind reaching the agent in [−30, +60]) left 39 nudge targets in III. Non-isolated kicks failed the placebo window (G over [−30, −16] = +0.28 [0.08, 0.48]). The main design therefore isolates on *direct* kicks (nudges to the agent, human messages in its room) and adds the count of bystander nudge exposures in the window (0, 1–2, 3+) to the matching strata. Strict isolation is kept as a robustness variant.
2. *FD.* The pre-registered CKP calibration is unidentifiable (below), so two h-free comparisons were added: the FDT shape test and the Onsager ratio in its excess form.
3. *Sensitivity:* an isolation window of [−30, +30] (`explore_kernels_iso30.json`) changes no conclusion.

**Green's functions (A30 / A60 = excess active minutes per responder over 30 / 60 min).**

| kick → responder | regime | n cells (kicks) | A30 | A60 | placebo [−30,−16] | peak lag | 1/e relax |
| --- | --- | --- | --- | --- | --- | --- | --- |
| nudge → target | III | 381 (349) | **1.54 [0.80, 2.29]** | **2.74 [1.06, 4.39]** | 0.21 [−0.14, 0.60] | ~15 min | ~15 min |
| nudge → target (strict isolation) | III | 39 (38) | 2.47 [0.45, 4.75] | 5.84 [1.76, 9.84] | −0.26 [−1.10, 0.66] | — | — |
| nudge → target | III 4 h / 8 h | 78 / 303 | 1.37 [−0.64, 3.04] / 1.66 [0.86, 2.44] | 2.19 [−1.86, 5.83] / 3.15 [1.26, 4.93] | ok | 15 / 16 | — |
| nudge → target | I / II | 9 / 13 | too few (I: 37 nudges, all Feb 2026) | | | | |
| nudge → bystanders | III | 13,832 (773) | −0.06 [−0.47, 0.38] | −0.18 [−1.06, 0.79] | −0.07 [−0.29, 0.15] | — | — |
| nudge → bystanders (strict) | III | 236 (43) | 1.17 [0.22, 2.06] | 2.32 [0.28, 4.12] | 0.33 [−0.22, 0.90] | ~46 | — |
| human → room occupants | I | 175 (22) | **1.85 [0.51, 3.23]** | **4.06 [1.50, 6.78]** | 0.37 [−0.54, 1.23] | — | ~5 |
| human → room occupants | III | 447 (24) | 1.14 [−0.35, 2.49] | 2.08 [−0.41, 4.47] | 0.22 [−0.41, 0.86] | — | ~17 |
| human → mentioned agent | I / III | 13 / 21 | 6.68 [1.49, 12.10] / **5.59 [1.84, 9.39]** | 15.0 [5.4, 25.6] / 10.6 [4.1, 17.1] | ok | **G(1) ≈ 0.2–0.35: immediate** | — |

- **Shape.** Nudge responses are *delayed*: G ≈ 0 for τ = 1–4 min, rising to a plateau at 10–30 min (`figures/kernels.pdf`). Mentioned agents respond at once.
- **Activation and talk.** A nudge raises the target's P(activation within 10 min) from 0.73 to 0.86 (+0.13 [0.09, 0.16]), and talk-only A30 = 0.45 [0.21, 0.72]. Human messages leave the activation probability unchanged (+0.00).
- **Robustness of the nudge kernel to the matching fallback.** A30 = 1.49 with ≥ 50 controls per stratum; 0.97 [0.19, 1.67] when the 25% of cells that need the coarse (agent-free) stratum are dropped. The mentioned-human kernel loses significance without the fallback (n = 16).
- **Goal kickoffs (step):** no step in the activity *level*. First-hour relative excess vs. matched non-kickoff days: −0.5% [−16%, +14%] (I, 24 kickoff days) and −9% [−37%, +19%] (III, 9); whole day −0.1% and −10%; no relaxation pattern over days 1–5 of a goal.

**Linearity tests** (rule from Observables; full list in `explore_kernels.json → linearity`):

| kick type | dose | superposition | time translation | G valid? |
| --- | --- | --- | --- | --- |
| nudge → target (III) | **untestable**: no two nudges to one agent within 2 min (0 cases) | S = 0.08 [−0.78, 0.82], inconclusive; iso30 variant 0.41 [−0.12, 1.09], n = 111. **Confounded:** the nudger re-fires on agents that did not respond, so pairs are selected on non-response | late/early 0.70 [0.16, 2.10] pass; Fri/midweek 0.76 [−0.28, 2.91] pass; mid/early 0.59, Mon/midweek 0.60 inconclusive; no fail | **not established**: only time translation tested (weak pass). A usable *averaged* kernel, not a validated linear one |
| human → room (I) | r(2) = −0.17 [−1.57, 1.08], inconclusive (n = 34); n ≥ 3 too few | S = 1.03 [0.26, 3.56] **pass** (n = 52); iso30: 0.45 [−0.31, 1.80] inconclusive | all inconclusive (reference response not significant in sub-splits) | **not established** (one pass, the rest underpowered) |
| human → room (III) | inconclusive (reference response not significant) | inconclusive | inconclusive | no (no significant reference response) |
| human → mentioned | too few for any test | too few | too few | no (n ≤ 21) |
| goal kickoff | untestable | untestable | — | no step response in activity at all |

**Fluctuation vs. response.**
- **CKP (pre-registered convention): not identifiable.** The log-odds field at τ = 1 is consistent with 0 for every kick type: nudge (III) h = −0.01 [−0.21, 0.21]; human (I) 0.15 [−0.16, 0.46]; human (III) 0.16 [−0.02, 0.31]. The kicks do not act as one-step fields on activity, so χ = ΣG/h is undefined and the CKP T_eff is not reported as a number.
- **h-free FDT shape test (decisive).** Under FDT the impulse response ∝ −dC/dτ, so the share of the 30-min response falling after τ = 5 must equal the share of the correlation drop after τ = 5. Measured response shares: **0.99 [0.90, 1.12]** (nudge, III), 0.84 [0.65, 1.08] (human, III), 0.78 [0.51, 0.88] (human, I). Correlation shares: 0.03, 0.00 and 0.04. The single-agent C(τ) drops by ~65% within 1 min (λ = C(1)/C(0) ≈ 0.28–0.41) and has a small bump at 10–15 min in III (a quasi-periodic pause/act cycle), while the responses live almost entirely after 5 min. **FDT is violated.** The most economical reading: the message couples to a *hidden* variable (the agent's unread context), not to activity, and is read out at the agent's next scheduled turn. FDT on activity alone is then not an equilibrium test, but a demonstration that the kinetic-Ising "field on n" mapping is wrong for kicks.
- **Onsager regression (excess form).** Aligned on the responder's first activation ≤ 10 min after the kick, against matched spontaneous activations and non-activations. X(30) = Σ(E_kick − E0)/Σ(E1 − E0):

  | kick | regime | activations | X(30) | T_eff = 1/X |
  | --- | --- | --- | --- | --- |
  | nudge → target | III | 286 | **1.54 [1.19, 1.93]** | **0.65 [0.52, 0.84]** |
  | | III 4 h / 8 h | 45 / 221 | 0.97 [−0.26, 2.08] / 1.77 [1.30, 2.25] | 1.03 [−6.7, 10] / 0.57 [0.44, 0.77] |
  | human → room | I | 133 | 1.51 [0.76, 2.13] | 0.66 [0.47, 1.32] |
  | | III | 308 | 1.74 [1.00, 2.43] | 0.58 [0.41, 1.01] |

  Kick-triggered activations are followed by *more* activity than spontaneous activations with the same history (X > 1, "cold" relative to the reversible reference): the kick changes the agent's state, not only the timing of its next action.

**Hawkes (agent chat messages, 10 s bins).**

| suite | events | n | fast / slow kernel | η_human (τ) | η_nudge (τ) | CV Δll/event vs Poisson (folds won) | exo vs no-exo | KS: Hawkes / Poisson |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| I | 68,372 | **0.59 [0.52, 0.63]** | 0.42 @ 81 s / 0.16 @ 10 min (bound) | 0.29 [0.24, 0.39] (15 s) | 0.50 (37 nudges) | **+0.050 (5/5)** | +0.002 (5/5) | 0.020 / 0.048 |
| II | 4,819 | 0.19 [0.09, 0.27] | | | | — | | 0.023 / 0.015 |
| III | 55,167 | **0.72 [0.62, 0.78]** | 0.30 @ 48 s / 0.42 @ 12 min | 0.45 [0.16, 0.72] (33 s) | 1.44 [0.00, 3.09] (12 min) | **+0.066 (5/5)** | +0.0003 (3/5) | 0.008 / 0.060 |
| III 4 h | 14,209 | 0.68 [0.24, 0.87] | | 0.37 | 0.73 [0, 7.4] | +0.022 (4/5) | −0.0004 (2/5) | 0.019 / 0.037 |
| III 8 h | 40,958 | 0.75 [0.62, 0.81] | | 0.59 | 2.17 [0.42, 3.79] (13 min) | +0.080 (5/5) | +0.0005 (4/5) | 0.008 / 0.071 |

- Synthetic recovery (3 replicates, village sampling): n = 0.717 → 0.68–0.69 (III), 0.587 → 0.53 (I): biased low by 0.03–0.06; η_nudge spreads 1.2–2.1 (III).
- The nudge's exogenous Hawkes kernel decays in ~12 min, consistent with the delayed G. The human-message kernel is fast (~30 s).
- Exogenous kernels are real but carry almost no likelihood: kicks are a small fraction of what drives chat.
- **Caveat on n:** in III the slow component (τ ≈ 12 min) carries 0.42 of n. It can absorb within-day field variation beyond the 4-step profile (Filimonov–Sornette), so n is an upper-side estimate. In I the slow time sits on its lower bound (600 s).

**NE10 (nudger switch-on), exploratory and thin.**
- Pre = #27 + 02-09 (11 days); post = 02-10 → 02-20 (9 days); 11 common agents.
- **The first non-holdout nudges appear on 02-13** (37 nudges in total), so 02-10 → 02-12 are nudge-free.
- Idle (state 2) is almost absent in regime I (0.15% of agent-minutes), so inactivity is used.
- Escape hazard from inactive runs > 10 min: −31% [−63%, −4%] (data-onset variant −36% [−69%, +5%]): *down*, not up.
- Active fraction +0.6% [−32%, +30%]; idle fraction n.s.; mean inactive run +24% [−21%, +95%].
- Hawkes n: 0.15 [0.00, 0.39] → 0.22 [0.14, 0.32] (Hawkes does not beat Poisson in the pre window).
- Confounds: goal changes (#30 on 02-09, #31 on 02-16), Opus 4.6 joining 02-06, Sonnet 4.6 joining 02-18.

**H04-MF (HH81).**

| suite | K (detrended) | K (day-centered / homogeneous) | τ₀ (min) | τ_m (min) | τ_m/τ₀ vs 1/(1−K) | τ_pred (min) | τ_G / τ_pred: relax (width) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| I | 0.11 [0.09, 0.14] | 0.19 / 0.12 | 0.81 | 0.84 | 1.04 vs 1.13 | 0.92 | human: 5.4 [2.3, 18.2] (39 [17, 44]) |
| III | 0.26 [0.21, 0.31] | 0.55 / 0.45 | 0.90 | 1.29 | 1.44 vs 1.35 | 1.21 | nudge: 12.3 [1.7, 27.7] (23 [11.5, 29.8]); human: 13.9 [1.6, 23.4]; mentioned: 19.4 [1.7, 21.2] |
| III 4 h | 0.21 [0.16, 0.25] | 0.40 / 0.35 | 0.88 | 1.04 | 1.18 vs 1.26 | 1.11 | nudge: 1.3 [0.7, 5.9] |
| III 8 h | 0.28 [0.22, 0.34] | 0.58 / 0.50 | 0.90 | 1.38 | 1.53 vs 1.39 | 1.25 | nudge: 26 [1.6, 28] (25 [13, 30]) |

- Mean-field Glauber with fluctuation-inferred coupling is **self-consistent on fluctuations** (MF-P3: (τ_m/τ₀)(1−K) = 0.92–1.10).
- It **does not predict the kernels.** The predicted response time is ~1 min, and the measured decay is 5–26× longer (point estimates). The model's response would also peak at τ = 0+, whereas nudge responses peak at ~15 min.
- K is detrending-sensitive: day-centering doubles it in III, because slow within-day fields count as coupling.

**Outcome vs. prediction (exploratory):**

| | Prediction | Outcome | Verdict |
| --- | --- | --- | --- |
| P1 | nudge → target: A60 CI excludes 0; peak ≤ 5 min; 1/e relax 3–30 min | A60 = 2.74 [1.06, 4.39] (III); **peak ~15 min**; relax ~15 min (CI 2–34) | **partly**: response real, but delayed, not prompt. I and II too few |
| P2 | bystander/target A60 ∈ [0, 0.2] | −0.07 [−0.76, 0.25]; bystander A60 −0.18 [−1.06, 0.79]; strict subset (43 nudges) +2.3 [0.3, 4.1] | **supported** in the main design (no spillover); the strict subset disagrees |
| P3 | human: A60 > 0; mentioned ≥ 2× unmentioned; I > III | A60 I 4.06 [1.50, 6.78] yes, III 2.08 [−0.41, 4.47] no; mentioned/unmentioned I 4.7 [1.1, 20.5]; I > III in point only | **mostly supported** (weak in III) |
| P4 | kickoff: ≥ +10% first hour | −0.5% [−16, +14] (I); −9% [−37, +19] (III) | **not supported** |
| P5 | dose sublinear; superposition 0.5–0.9; time translation passes; G valid for isolated low-dose kicks | dose untestable/inconclusive; superposition 1.03 (human I, pass) and 0.08 (nudge, confounded); time translation weak pass for nudges | **untested / not established** (power; nudger selection) |
| P6 | FDT violated; nudges X < 1 (T_eff > 1), Onsager < 1; humans nearer 1; T_eff differs I vs III | FDT violated in shape (decisive); CKP unidentifiable; **nudge X(30) = 1.54 [1.19, 1.93], T_eff = 0.65**; humans X ≈ 1.5–1.7; I vs III not different | **FDT violation supported; direction refuted** (kicks are *more* persistent, not transient) |
| P7 | Hawkes beats Poisson on CV; 0.3 < n < 0.9; 0.3 ≤ η_nudge ≤ 3; η_human ≥ η_nudge; recovery ±0.05 | CV +0.05 / +0.07 nats/event, 5/5 folds; n 0.59 (I), 0.72 (III), but 0.19 in II; η_nudge 0.5 / 1.4; **η_human < η_nudge**; recovery −0.03 (III), −0.06 (I) | **mostly supported**; η ordering refuted; recovery marginal in I |
| P8 | n(8 h) < n(4 h) − 0.05 (III) | 0.75 [0.62, 0.81] vs 0.68 [0.24, 0.87] | **not supported** (opposite sign, n.s.; era-confounded) |
| P9 | NE10: escape hazard ≥ +20%, idle ↓, active Δ < 10%, Δn < 0.1 | hazard −31% [−63, −4]; idle n.s.; active +0.6% [−32, +30]; Δn +0.07 | **not supported** (thin, confounded) |
| MF-P1 | K ∈ [0.05, 0.5]; K(III) > K(I) | 0.11 vs 0.26 | **supported** |
| MF-P2 | τ_pred underpredicts τ_G by ≥ 3× everywhere | point ratios 5–26× (I, III, III 8 h); by the pre-set CI rule MF is excluded for I humans (CI > 2) and, with the width estimator, for III nudges and mentioned humans; relax-estimator CIs in III reach down to ~1.6. III 4 h nudge: 1.3 [0.7, 5.9] | **supported in direction; formally excluded in I and with the width estimator only** |
| MF-P3 | τ_m/τ₀ ≈ 1/(1−K) within 2× | ratio 0.92–1.10 | **supported** |
| MF-P4 | K(8 h) < K(4 h) | 0.28 vs 0.21 (CIs overlap) | **not supported** (opposite sign) |

**Which kick types admit a Green's-function description?**
- **Nudges → target (regime III):** a reproducible *averaged* kernel exists (delayed, ~15 min, with a plateau to ~30 min). It is time-translation-consistent (weak), but dose linearity is untestable and superposition is confounded by the nudger's own selection. Use it as a phenomenological response function, not a validated linear propagator.
- **Human messages:** a kernel exists for room occupants in regime I and for mentioned agents. Linearity cannot be established with the available isolated kicks.
- **Bystanders:** G ≈ 0 (no propagation through the room at this resolution).
- **Goal kickoffs:** no measurable step response in activity. A goal change is a field on *what* agents do, not on *how much*.
- In every case the kernel is **not** a kinetic-Ising field response: the FDT shape violation, the h ≈ 0 at τ = 1, and the mean-field failure all point to a hidden-state (unread-context) channel.

**Caveats.**
- Small numbers of isolated human messages (22–24 kicks per regime).
- Regime I has only 37 non-holdout nudges.
- 4 h vs. 8 h is era-confounded (Mar–May vs. Jul–Sep 2026).
- 25% of nudge-target cells use coarse strata.
- Matching uses binned history; residual selection by the nudger's text-based trigger ("waiting for directions") cannot be matched without text.
- Activity bins are 1 min; computer-use turns dominate "act" in III.
- The Onsager comparison conditions on activation within 10 min (75% of nudged targets).
- The Hawkes slow component may absorb nonstationarity.

### Confirmatory (locked holdout; run 2026-10-03 23:13–23:27 UTC, signed off by Vivian; pre-registration commit e9bf2f7)
`confirm_ne21_ne23.py --confirm --i-understand-this-uses-the-locked-holdout` was run once. Output: `data/processed/H04-reversible-forcing/confirm_ne21_ne23.json`. Full table in [NE21/README.md](goalperiod-subhypotheses/NE21/README.md).

| Prediction | Result | Verdict |
| --- | --- | --- |
| **C1: n lower on 8 h days, flipping at every switch** | n: A1 (4 h) 0.31 → B1 (8 h) **0.67** → A2 (4 h) 0.46 → B2 (8 h) **0.89**. 0/3 switches with the predicted sign; all 3 flip the *other* way. ABAB contrast (4 h − 8 h) −0.39 [−0.46, −0.20]; placebo noise |p95| = 0.42 | **FALSIFIED** (reverse direction, at the noise edge) |
| C1 secondary: fast part a₁ | 0.31 / 0.36 / 0.37 / 0.32 | indistinguishable from weekly variation |
| C2: kernel invariant across hours | A30 ratio 8 h / 4 h: nudge 1.5 [−9.3, 13.0], human 4.6 [−37, 44] | inconclusive |
| C3: Onsager T_eff reverses | < 10 kicked activations in some segment | untestable |
| C4: NE23 nudger off (06-13) | **manipulation check failed: 9 "nudges" in the off session** (possibly pause/resume messages misclassified as nudges, see infra Known issues). Idle fraction and inactive-run length higher when off ✓; n unchanged ✓; kernel return ✗ | partial |
| MF-C: loop gain K tracks hours | K: 0.32 / 0.17 / 0.25 / 0.27; ABAB 0.06 [−0.05, 0.21] vs placebo 0.12; decay gap ≥ 3× not in every segment | indistinguishable |

**Reading:**
- The pre-registered HH46 claim, that longer days spread activity out and lower n, is wrong in sign.
- Longer days come with *more* self-excitation, reversibly at each switch. This is what exploration had hinted at ("n and K slightly higher on 8 h days, era-confounded").
- The size is at the 95th percentile of the non-holdout week-to-week placebo, so the reverse effect is suggestive, not established.
- A possible mechanism: longer sessions leave agents more unread context to react to (H08), so more activity is triggered by other activity. Recorded as a new idea, not a finding.

## Notes
- 2026-10-04: **H04-R1 tested in H08: not supported for nudges.** Read-out is fast (median 104 s), but the response starts at ~5 min; about half of H04's dead time is scheduler read-out and half something slower.
- 2026-10-03: opened from shortlist S3. Card and predictions written before any response was computed.
- 2026-10-03: exploratory round 1 run (non-holdout only); design changes listed under Results. H04-MF added at the user's request, with predictions written first.
- 2026-10-03: the confirmatory script was dry-run on **non-holdout surrogate segments** (`--dry-run` → `dryrun_ne21_ne23.json`) to check the code path; those numbers have no bearing on the hypothesis. The dry run exposed that 5–10-day segment n varies by ±0.3 between same-hours weeks, which led to the placebo-switch analysis and the C1 / MF-C amendment. The real run needs `--confirm --i-understand-this-uses-the-locked-holdout`.
- Scheme: no separate build step. The mapping (nudge / bookend classification, targets, bystanders, direct-kick isolation) lives in `analysis/h04lib.py` (`load_messages`, `responder_rows`, `attach_hits`, `build_sets`); outputs are small JSON files in `data/processed/H04-reversible-forcing/`. If H03 (Hawkes) or H02 need the nudge/target mapping, move `load_messages` into `infra/`.

## Round 2 redirects (2026-10-04)
*From the round-1 reflection (`writeup/round1-reflection/round1-reflection.pdf`).*
- **Where round 1 went sideways:** Messages were treated as fields on activity and searched for linear kernels; the kernel turned out to be the turn schedule.
- **What the direction is really after:** The scaffold is the propagator: the response to any input is when the agent next looks, times whether it attends.
- **H04-R1.** The response kernel equals the turn-interval survival function convolved with an uptake probability, with no free parameters (HH92, tested in H08).
- **H04-R2.** The steering knob is the scheduler: shortening turn cadence raises susceptibility more than rewording or repeating a message (E1).
- **H04-R3.** A salience law: uptake rises with mention, position and novelty in context and falls with backlog (E5).
