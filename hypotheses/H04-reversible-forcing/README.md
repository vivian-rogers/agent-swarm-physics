# H04: External forcing reshapes the response kernel, reversibly

**Status:** specified; exploratory round 1 in progress (2026-10-03). Confirmatory script written, **not run** (NE21/NE23 are in the locked holdout).
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
2. **Event-level Hawkes (model 09 view).** Village-level talk events (AGENT_TALK), binned at 10 s within each day's window:
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
- **Matched controls:** agent-minutes with no message kick (human or nudge) reaching that agent (room or mention) in [m − 30, m + 60], from non-holdout days of the same regime. Strata: regime × agent × state at m − 1 × active minutes in [m − 15, m − 1] (0, 1–3, 4–9, 10–15) × idle minutes in [m − 15, m − 1] (0, 1–7, 8–15) × tercile of the day window. A treated cell whose stratum has < 20 controls falls back to the same stratum without agent identity; the fallback share is reported. Placebo: G over τ ∈ [−30, −16] (outside the matched pre-window) must be ≈ 0.
- **Output:** `data/processed/H04-reversible-forcing/` (kernels, test results, Hawkes fits; JSON and parquet, a few MB) with `_provenance.json`.
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
  - **Onsager regression (selection-robust check).** Align on the responder's first activation within 10 min after a kick, vs. spontaneous activations (no kick in [−30, +60]) with matched pre-history; ratio of the integrated activity over the next 30 min, kicked / spontaneous. Ratio 1 = the kick only times the activation (a pure field on the next step); > 1 = the kick changes the agent's state (persistent); < 1 = more transient than a spontaneous activation.
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
- **Known confounds (stated before running):** every switch coincides with a goal change (#46, #47, #50); 06-11 changes the default pause from 12 h to 5 min and caps unseen events (NE22) inside B1; 06-03 disables parallel tool use (inside A1); 06-29 migrates GitHub → GitLab (NE24) at the B2 switch; 06-13 is a Saturday evening with only #best agents and a special event. The script reports B1 split at 06-11 as a sensitivity check.

## Results
<Filled in after analysis. Link to analysis/ and figures/.>

## Notes
- 2026-10-03: opened from shortlist S3. Card and predictions written before any response was computed.
