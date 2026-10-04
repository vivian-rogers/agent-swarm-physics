# H93: Project choice as a Brock–Durlauf equilibrium

**Status:** exploratory round 1 done (2026-10-04, non-holdout only). **Failed as posed: no multiple equilibria, and the share coupling is a real coefficient but is not identified as J.** On 13 periods and two channels, the validated estimator (M4: share + kickoff naming + habit + cumulative size) gives βĴ > 0 with CI > 0 in 5 of 10 identified work replication periods (+1.9 to +5.8: #31, #33, #36, #38, #41) and below 0 in the own-role weeks (#42 −5.9, #51 −11.7: agents avoid occupied repos). The coefficient survives the kickoff-free placebo, the cross-lab split and the read split, but a post hoc synthetic (A2) shows that fast common repo bursts with no coupling produce the same values. Every period sits below the Brock–Durlauf multiplicity boundary at its point estimate (βĴ/γ_c ≤ 0.86), and the fitted fixed point m* ranks the observed concentration across periods (Spearman 0.77). No same-field replica lands in a second state (G37 rooms p = 0.50; no herded unit among 12 #51 units). Habit is the dominant field (b_own ≈ 2.5–6 nats). `analysis/confirm.py` is frozen and dry-run, not run. Card and predictions written 2026-10-04 before any real fit; amendments A1 (pre-data) and A2 (post hoc) below. Approved by Vivian in the dashboard vetting panel 2026-10-04 from HH283.
**Fields:** sociophysics (social-interaction discrete choice), stat mech (mean-field Potts, multiple equilibria), econometrics (conditional logit, reflection problem)
**Literature:** no paper in `literature/` covers Brock–Durlauf directly. Classical background named, not filed (†): Brock & Durlauf, "Discrete choice with social interactions", *Rev. Econ. Stud.* 68, 235 (2001)†; Blume, "The statistical mechanics of strategic interaction", *Games Econ. Behav.* 5, 387 (1993)† (logit dynamics); Manski, "Identification of endogenous social effects: the reflection problem", *Rev. Econ. Stud.* 60, 531 (1993)†; McFadden (1974)† (conditional logit). Nearest filed note: [Piñero 2025, neutral cooperative dynamics](../../literature/pinero-2025-neutral-theory-cooperative-dynamics.md) (frequency-dependent joining).
**Definitions used** (`physics-models/DEFINITIONS.md`): *Agent state (categorical, project, work ledger)* (H11 round 1b) as carried by *host (work ledger, call-clock expiry)* (H77/H78 variant, shared `infra/shared/replicator_hosts.py`, E = 100); *Agent state (categorical, project/artifact strict)* (H11) for the attention channel; *Exposure (turn read-out)* via the DQ1 context ledger; *Regime*; *Population N(t)*. New named variants proposed here (not edited into DEFINITIONS.md): **choice event (H93)**, **share field s_j (H93)**, **social coupling βJ (H93)**, **BD equilibrium count (H93)**, defined under Data scheme and Observables.
**From:** HH283 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` (econ-style free energy family) · **Models:** `physics-models/10-potts/` (primary: mean-field / kinetic Potts = logit choice with share coupling), `physics-models/05-replicator-dissipation/` (repo fitness and formation, H78's confound)
**Sibling:** H94 (max-ent allocation) uses the same DQ4 work ledger and ownership; the two scheme codes are separate (see report: suggestion to move a shared allocation builder into `infra/shared/`).
**Question served:** Q2 (what is field and what is coupling) and Q3 (collective order beyond fields: multiple equilibria would be collective order that a field cannot set).

## Source HH (verbatim from the HH list, including literature refinements)
Project choice is a Brock–Durlauf social-interaction equilibrium. P(project j) ∝ exp(β[U_j + J·share_j]), the econ form of Curie–Weiss/Potts herding. Multiple equilibria exist when βJ is large. Prediction: periods with the same goal type can land in different equilibria (herded vs dispersed), and H53's "current share predicts pile-ons" is the J term. *Check:* fit β and J per period on project choices (attention and work); test for multiple equilibria (bimodal outcomes) across same-type periods.
  *Models:* 10 · *Builds on:* H11, H53, H06, H63

## Question
When an agent picks a project, does the share of other agents already on it raise the pick probability beyond the project's own pull (kickoff naming, the agent's own history, repo fitness)? If it does, is the coupling βJ strong enough that the same field can support more than one stable allocation, so that same-type weeks land in different states?

## Model
**From:** `physics-models/10-potts/` (mean-field Potts; "Mean-field forward version"; kinetic Potts = per-agent softmax). Brock–Durlauf (BD) is the mean-field Potts model written as a discrete-choice model.

**H93 variant: kinetic BD (logit dynamics) with fields and a share coupling.** At a choice event e, agent i picks option j from the choice set C_e with
P(j | e) = exp(v_ej) / Σ_{k∈C_e} exp(v_ek), v_ej = h_j + h_ij + βJ · s_j(t_e⁻),
- **s_j:** the share of the other active agents whose current label is j, just before the choice.
- **h_j = βU_j, the repo field:** a kickoff-naming term b_named · named_j (H54 rule), a constant α_new for the "new repo" option, and repo fitness α_j (unobserved; repo fixed effects in the FE variants).
- **h_ij, the agent field:** a habit term b_own · prev_ij (i held j earlier in the period; H58's return to the own artifact).
- **βJ, the social coupling** (dimensionless). β and J are not separately identified in a logit: only βU and βJ are. The card reports βJ, and β in one stated utility unit (one kickoff naming: β ≡ b_named with U_named = 1, so J = βJ / b_named in kickoff units) where b_named is well determined.

**Equilibrium.** The stationary state of logit dynamics at large N is the BD fixed point m_j = ⟨softmax_j(h + βJ m)⟩_agents. For q symmetric options the mean-field Potts transition is first-order with βJ_c = 2(q−1) ln(q−1)/(q−2) (q = 3: 2.77; the Potts card's normalization, which H11 uses); the disordered state loses stability at βJ = q. With heterogeneous fields the count of stable fixed points is computed numerically. **Multiple equilibria** = ≥ 2 stable fixed points at the fitted (h, βJ).

**What would make HH283 true:** βĴ > 0 after the fields and habit are removed, above the multiplicity threshold in at least some periods, and same-field replicas (rooms with identical kickoff text, same-type weeks) landing in different stable states.

## Data scheme (`scheme/`)
`scheme/build.py` writes `data/processed/H93-brock-durlauf-project-choice/G<NN>/` from shared tables only (no message text stored; repo and project names hashed on output).
- **Inputs:** DQ4 `work_commits` via `infra/shared/replicator_hosts.py` (host labels W = 30, expiry E = 100, arrival tags `cls`, `cls_touch`, H54 `named`); shared `project_states` (W = 30, sources all; attention channel); DQ1 `context_ledger_items` + `call_windows` and `artifact_mentions` (chat links read before the choice); `rooms_timeline` (chooser and host rooms); `roster` (lab); `period_units`; `calendar`; raw goal and kickoff text through `goal_fields.kickoff_messages` in memory only (H54 rule, inside `replicator_hosts.kickoff_named`).
- **Choice event (H93):** *work:* an arrival (recruit or birth) in the host replay; *attention:* a labelled agent-window whose project differs from the agent's last labelled project in the period (the first label of an agent in the period counts).
- **Choice set C_e:** every option active in the period before t_e (hosted now or dormant), minus the chooser's current label, plus one "new" option (a repo or project not yet seen in the period). Events with < 2 alternatives are dropped.
- **Covariates per (event, option):** s_j (work: current hosts of j other than i over active hosts other than i; attention: labelled agents on j in the previous window over labelled agents, chooser excluded); named_j; prev_ij; log(1 + cumulative quanta of j before t_e) (fitness proxy, variant); s_j split by room (chooser's room vs other), by lab (same vs other lab), and by reading (seen_ij: the chooser read a chat link to j, or mentioned j itself, before t_e).
- **Output:** `G<NN>/events_<channel>.parquet` (one row per choice event: unit, agent, day, t, chosen option, tags), `G<NN>/long_<channel>.parquet` (event × option rows with covariates; options hashed), `G<NN>/occupancy_<channel>.parquet` (per bin: host counts by option; for the order parameter), `_provenance.json`.
- **Regimes covered:** #30, #31 (I); #33, #35, #36a (II); #36b–#44, #51a–l (III). Holdout days and periods are dropped with `holdout_mask` (via `replicator_hosts.period_days` and a `holdout_mask` filter on `project_states`).
- **Unit of analysis:** goal period split at `period_units`. βJ is fitted per unit where the unit is testable and pooled over units by DerSimonian–Laird random effects (exception (d)); the per-unit values are reported next to the pool. Where no unit of a period is testable alone, the period fit with unit-specific α_new is reported and flagged.

## Observables
1. **βĴ (primary, M2):** conditional-logit MLE with s_j, named_j, prev_ij and α_new (per unit); 95% Wald CI (observed information).
2. **βĴ under estimators:** M0 (s_j and α_new only: H53's "current share"), M1 (+ named), M2 (+ habit: primary), M3 (+ cross-fitted repo fitness: leave-one-day-out repo FE as an offset), M4 (+ log cumulative size). Shrinkage ratio βĴ(M2)/βĴ(M0).
3. **Impostor splits:** in-room vs other-room share; same-lab vs cross-lab share; seen vs unseen share; blind arrivals dropped.
4. **BD equilibrium count:** stable fixed points of m = ⟨softmax(h + βJ m)⟩ at the fitted M2 parameters (options = the period's top 8 by quanta plus "other"), from 200 random and 9 corner starts; parametric-bootstrap probability P_multi that ≥ 2 stable fixed points exist (200 draws from the estimate's sampling distribution).
5. **Order parameter m:** the time-averaged largest-option share of hosted agents (work) or labelled agents (attention), per unit and per room; and the BD prediction m* (the fixed point reached from the period's first-day occupancy).
6. **Phase-diagram coordinates:** (field spread σ_h of the fitted h_j over the top options, βĴ, N) per period.

## Null / baseline
- **No social coupling (βJ = 0):** the fields-only model (named, habit, α_new, repo fitness). The synthetic worlds (below) on each period's real event schedule give the βĴ distribution when βJ = 0 but repos differ in fitness (σ_A = 0, 0.5, 1.0) and a kickoff field acts.
- **H78's confound:** first-order copying with repo fitness spread reads as superlinear growth; here fitness spread reads as βJ > 0 in M0–M2. M3 (cross-fitted FE) is the remedy if the synthetic shows it is unbiased; else the card says βJ is not identified.
- **Multiplicity null:** a unique equilibrium at the fitted parameters; replica outcomes (rooms, units) inside the spread of the fitted model's simulated outcomes from the same start.

## Rivals and impostors
- **Rivals:** (R1) fields only: a kickoff field and repo fitness set choices, βJ = 0 (H54, H78); (R2) habit only: agents return to their own repos (H58); (R3) neutral copying (H06/Hubbell): choice ∝ current hosts, i.e. βJ > 0 but linear in counts rather than exponential in share (variant: log(n_j) in place of s_j, compared by held-out log-likelihood).

| Impostor | Relevant? | How it is handled | Status |
| --- | --- | --- | --- |
| Scheduler field | partly | The model conditions on the choice moment and fits only *which* option is chosen; when an agent chooses is not modelled. Shares are counted among active agents only. | removed |
| Exogenous field (kickoff/goal/operator) | yes | `named_j` (H54 rule) in M1–M4; βJ refitted on choice sets with named options dropped (kickoff-free placebo: βĴ kept in 5/6 periods where it was positive); rooms with identical kickoff text as replicas (G37). No `goal_fields` direction regression: choices are categorical and the kickoff field enters as the naming indicator. **Round 1:** an unmodelled assignment field (#44 #best team) is absorbed into βĴ (+13.9) and fakes BD multiplicity (P_multi 0.97); fast repo bursts (time-varying fields) produce βĴ ≈ 1–3 (A2). | partly |
| Shared model priors | yes | Share split into same-lab and cross-lab hosts; agent habit term. Round 1: cross-lab βĴ > 0 with CI > 0 in 6 of 9 identified periods (+1.8 to +4.4); same-lab is larger in #31, #33, #37 and smaller in #38. | removed |
| Contemporaneous convergence | yes | Blind-window arrivals (`cls == blind`) dropped (2 periods have any); "seen" share (A1 definition) is uninformative because it includes self-mentions (agents touch a repo before committing); post hoc read split (A2): share counted only on options with a ledger-read link from another agent carries all of βĴ, unread options are never chosen. Not a matched-lag read vs posted-but-unread design. | partly |

## Synthetic validation (axis F; done before any real-data fit)
Simulator `analysis/synthetic.py`: the period's real event skeleton (choosers, event times, departure and expiry times, unit and day of each event, number of kickoff-named repos) with synthetic choices drawn from the H93 model. Worlds: W0 (βJ = 0, σ_A = 0), W1 (βJ = 0, σ_A = 0.5), W2 (βJ = 0, σ_A = 1.0), W3 (βJ = 3, σ_A = 0), W4 (βJ = 3, σ_A = 1.0), W5 (βJ = 6, σ_A = 0.5), each with b_named = 1.5, b_own = 2, α_new calibrated to the real birth share. Report bias, 95% coverage and the false-positive rate (CI > 0 when βJ = 0) for M0–M4. **Decision rule fixed now:** an estimator counts as a test of βJ only if its false-positive rate is ≤ 0.10 in W1 and W2 and its coverage is ≥ 0.80 in W3–W5. If no estimator passes, P1–P3 are scored as written but the card's verdict on βJ is "not identified".

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** fields only (R1), habit only (R2), neutral copying (R3).
**Locked holdout used for confirmation:** #45, #46, #47, #50 and the #51 tail (51m); frozen in `analysis/confirm.py`, dry-run on stand-ins only, not run.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Choices are DQ4 host-label arrivals and `project_states` label switches; shares, habit and cumulative size are counts. Limits: H54's token rule tags 31–100% of chosen options as named (agents name repos after the goal), so the kickoff field is measured poorly; attention labels cover only labelled windows. The same mapping runs in regimes I–III. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Logit (IIA) choice with myopic current share; fields constant within a unit. The A2 synthetic shows the constant-field assumption is the weak point: fast repo bursts violate it and inflate βĴ. Fixed-point stability uses logit (best-response) dynamics. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | M4 beats the fields-only null in 5/10 identified work periods (and 7 attention fits), with false-positive rate ≤ 0.10 under static fitness spread on all 13 skeletons. It does not beat the fast-burst null (false positives 0.12–1.00, A2). No day-blocked held-out likelihood. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | The BD fixed point m* computed from choice-level fits ranks the observed time-averaged concentration m across 10 periods (Spearman 0.77). The model's signature, a second stable state, is absent: no replica split (G37, G51). |
| E interventional | predicts the change across a natural experiment | 0 | #44's assigned-vs-free contrast moves βĴ the wrong way: the assigned arm's team field is absorbed as coupling (+13.9). No NE designed for βJ. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | M4 recovers βJ = 3 and 6 with coverage 0.72–1.00 and false positives ≤ 0.10 under static fitness spread on 13 real skeletons (power at βJ = 3: 0.25–1.00). M0–M3 fail (A1). Fast repo bursts are not separable (A2). |
| G ground truth | agrees with known structure | 1 | Fields match known structure: #35 forks per room (habit 4.8), #39 own worlds (no occupied-repo choice), #40 hub (m 0.71), #44 assigned team (m 0.65). |
| H comparative | beats the named rivals | 1 | Beats R1 (fields only) and R2 (habit only) in the static-field sense above. Ties R3 (neutral, log(1 + n)) within 0.02 nats per event in 8/11 periods; R3 is better in #37, #38, #41 (0.06–0.09). |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Holdout not run. The sign pattern (positive in shared weeks, negative in own-role weeks) is post hoc. |

## Prediction
*Written 2026-10-04, before running the analysis on real data.*

**What I had seen when writing this:** the cards of H06, H11, H53, H54, H58, H77 and H78 (their headline numbers: herding onto shared repos in 11/14 weeks in attention and 4/6 in work; current share is H53's best wave predictor, +62 nats; kickoff-named repos take every arrival in the herding weeks; 66% of recruitments are returns; fitness spread reproduces superlinear growth), the period-affordance catalog (rooms had identical kickoff text in #36, #37, #39, #40, #42), and per-period work-commit and recruitment counts quoted in those cards. No choice-set, share or logit statistic had been computed.

**Periods and roles.** Replication (`replication`), both channels: #30, #31, #33, #35, #36, #38, #39, #40, #41, #42, #51 (units 51a–51l). Natives (`native`): **G37** (two free rooms with identical kickoff text: same-field replicas), **G44** (assigned #best vs self-chosen #rest on the same days), **G51** (twelve same-goal units: the best set of same-type replicas for a multiple-equilibria test; its replication fit is also reported).

**Testability rule (fixed now).** A unit is testable in a channel if it has ≥ 30 choice events with ≥ 2 alternatives, of which ≥ 10 choose an existing option. Otherwise descriptive.

| ID | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| P1 | H53's term exists: βĴ(M0) > 0 with CI > 0 in ≥ 2/3 of testable work periods | CI includes 0 or βĴ < 0 in > 1/3 | 0.80 |
| P2 | Fields and habit carry most of it: βĴ(M2) ≤ 0.5 · βĴ(M0) in ≥ 2/3 of periods where P1 holds | ratio > 0.5 in > 1/3 | 0.55 |
| P3 | Fitness carries the rest: with a validated fitness control (M3), βĴ CI includes 0 in ≥ 1/2 of testable periods | βĴ(M3) > 0 with CI > 0 in > 1/2 | 0.45 |
| P4 | No multiple equilibria: P_multi < 0.5 in every testable period at the M2 fit | P_multi ≥ 0.5 in ≥ 1 period with a validated estimator | 0.75 |
| P5 | Same-type weeks differ by field, not by equilibrium: across the replication periods, the BD fixed point m* from the fitted fields ranks the observed order parameter m (Spearman ρ ≥ 0.6), and same-mode pairs that differ in m (e.g. #41 vs #39, #42) differ in their fitted fields (named share or habit) | ρ < 0.3, or a same-mode pair with equal fields and opposite m | 0.45 |
| P6 | Attention and work agree: βĴ(M2) has the same sign in both channels in ≥ 2/3 of periods testable in both | opposite signs in > 1/3 | 0.65 |
| P7 (impostors) | Read-mediated: βĴ on seen share > βĴ on unseen share in ≥ 2/3 of testable work periods; in-room share > other-room share in two-room periods; cross-lab βĴ within ±1 of same-lab | the reverse | 0.55 |
| P8 (rival R3) | Exponential-in-share (BD) and linear-in-count (neutral) forms tie: |ΔLL| per event < 0.02 nats in ≥ 1/2 of periods | one form wins by ≥ 0.02 nats/event in most periods | 0.50 |
| Kill (HH283) | βĴ after fields, habit and fitness is ≈ 0 (CI includes 0) everywhere, or P_multi < 0.5 everywhere and no replica pair splits | — | P(kill) 0.65 |

Per-period predictions are in each `goalperiod-subhypotheses/G<NN>/README.md`, written before that period is run.

**Amendment A1 (2026-10-04, after the synthetic validation, before any real-data fit).** What I had seen: the synthetic summaries on the skeletons of #31, #38, #41, #44 (40 runs per world) and #51 (15 runs per world); the real per-period counts of choice events, options and named options (scheme `counts.json`). No real βJ, P_multi or m.
- **Validated estimator: M4** (share + named + habit + log(1 + cumulative arrivals) as the fitness control). It is the only estimator that passes the fixed rule in all five skeletons: false-positive rate 0.00–0.10 in W1 and W2, coverage 0.85–1.00 in W3–W5, median bias −1.4 to +0.8. M2 (the card's "primary") fails: under fitness spread σ_A = 1 it calls βJ > 0 in 30–93% of runs. M3a (cross-fitted FE) fails in #51 (false positives 0.73 at σ_A = 1); M3b (in-sample FE) under-covers (0.58 in #31 W3). M0 calls βJ > 0 in 100% of #51 runs even with no fitness spread (habit returns masquerade as share).
- **Consequences:** M4 is now the primary estimator for P1–P8 and the kill, P3 is scored on M4, the BD equilibrium count (P4) uses the M4 fit with log cumulative size as a field, and the impostor splits (P7) and the neutral rival R3 (P8) use the M4 base (log cumulative size added). P1 and P2 stay as written on M0 and M2: they now describe what the naive estimators show, not βJ.
- **Power (M4, CI > 0 at βJ = 3):** #38 0.95, #51 1.00, #41 0.70, #31 0.50, #44 0.25; at βJ = 6: 0.70–1.00. Negative claims on βJ are powered (≥ 0.8) only where the period's own synthetic says so; elsewhere a null βJ is "inconclusive".
- Not amended: the testability rule, the periods, the roles, the credences.

**Amendment A2 (2026-10-04, post hoc, after the first real run; disclosed).** Three additions, none changing M4, the periods or the verdict rules:
- **Burst worlds** (W6–W9): repo fitness follows an Ornstein–Uhlenbeck process on the arrival clock (σ = 1 or 2, correlation time 20 or 100 arrivals), with βJ = 0 (W6–W8) or 3 (W9), on the skeletons of #31, #37, #38, #41 (40 runs each). Added after seeing βĴ(M4) > 0 in most shared weeks, because H28 found that links, chat and work rise together in bursts. **Result:** fast bursts make M4 call βJ > 0 in 12–100% of runs (median bias +0.9 to +3.4); slow bursts (τ = 100) in 5–15%. A positive βĴ of 2–4 is therefore not identified as social coupling.
- **Read split** (`SPLIT_read`): the share counted only on options for which the chooser had read (DQ1 ledger) a chat link posted by another agent, vs the rest. The A1 "seen" split was uninformative, because it counted the chooser's own earlier mentions (agents touch a repo before committing to it).
- **Stability criterion fixed** before the reported run: fixed points are stable when the eigenvalues of dF/dm have real part < 1 (logit dynamics), not modulus < 1; damping now shrinks with |βJ|. The first run had counted no stable fixed point in strongly negative-βJ #51 units. Checked against mean-field Potts: q = 3 gives one state at βJ = 2.6, four at 2.9 and three ordered states at 3.5, as theory says.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | supported | one park repo; βĴ(M4) work −1.31 [−2.92, 0.30], attention +0.33 [−0.91, 1.58]; m 0.77 |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | mixed | βĴ(M4) work +2.44 [1.08, 3.80], attention +2.30 [0.63, 3.97]; P_multi ≤ 0.47; βĴ/γ_c 0.55 |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | mixed | work +2.48 [0.80, 4.17]; m 0.86; βĴ/γ_c 0.83 |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | supported | work +1.55 [−1.38, 4.47]; habit 4.8; m 0.66 (forks per room) |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | mixed | work +1.89 [0.36, 3.42], attention +1.54 [−2.61, 5.69] |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | mixed | work +2.22 [1.36, 3.07] (power 0.95), attention +0.55 [−2.29, 3.38]; P_multi 0 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | supported | work not identified (births and returns only); attention −7.19 [−15.6, 1.22]; m 0.10 |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | mixed | work +3.63 [−0.51, 7.77], attention +3.14 [0.76, 5.52]; hub m 0.71 |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | mixed | work +3.94 [2.20, 5.67], attention +4.52 [2.54, 6.49]; kickoff-free +5.89; βĴ/γ_c 0.66–0.75 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | mixed | work −5.89 [−11.64, −0.13] (avoidance); attention +1.10 [−4.62, 6.81] |
| [G37](goalperiod-subhypotheses/G37/README.md) | native | mixed | rooms with identical kickoff: Δm +0.22 inside the one-equilibrium band (p = 0.50); pooled P_multi ≤ 0.47; #rest room fit alone 0.88 |
| [G44](goalperiod-subhypotheses/G44/README.md) | native | mixed | free arm βĴ ≈ 2 (CI ∋ 0), P_multi ≤ 0.02; assigned arm βĴ +13.9 [5.4, 22.4], P_multi 0.97: the assignment field is absorbed as coupling |
| [G51](goalperiod-subhypotheses/G51/README.md) | native (also replication) | mixed | work −11.7 [−19.0, −4.4] (AF, 10 units); attention +0.84 [−1.90, 3.57]; no herded unit (m ≤ 0.21); P_multi ≥ 0.5 in 2/22 unit-channels |

## Results
*Exploratory round 1, 2026-10-04, non-holdout days only.*
- **Code:** `scheme/h93scheme.py` (streams, long tables), `scheme/build.py`; `analysis/h93lib.py` (conditional logit, DL pool, BD fixed points, P_multi), `run.py` (per period), `natives.py` (G37, G44, G51), `phase.py` (γ_c), `synthetic.py`, `score.py` (P1–P8, estimates rows), `figures.py`, `confirm.py` (frozen, dry-run only).
- **Data:** `data/processed/H93-brock-durlauf-project-choice/` (`G<NN>/` events, long tables and occupancy per channel; `results/`; `synthetic/`; `confirm_dryrun/`; `_provenance.json`; 3 MB).
- **Figures:** [`figures/summary_obs.pdf`](figures/summary_obs.pdf) (βĴ per period with γ_c), [`figures/summary_synth.pdf`](figures/summary_synth.pdf) (identification by world).
- **Estimates:** 179 rows in `per_period_estimates` (`bd_share_coupling_betaJ`, `bd_share_coupling_betaJ_naive`, `bd_p_multi_equilibria`, `bd_order_parameter_m`).

**Outcome vs prediction**

| Prediction | Outcome | Verdict |
| --- | --- | --- |
| P1 M0 > 0 (CI > 0) in ≥ 2/3 of work periods | 8/10 (#30, #31, #33, #35, #36, #38, #40, #41) | supported |
| P2 M2 ≤ 0.5 · M0 where P1 holds | 0/8 (ratios 0.58–2.81) | failed |
| P3 M4 CI includes 0 in ≥ 1/2 | 3/10 (#30, #35, #40); positive in 5, negative in 2 (#42, #51) | failed |
| P4 P_multi < 0.5 everywhere | 51/54 identified unit-channel fits; 44b work 0.78, 51j attention 0.50, 51l attention 0.83 | failed (by the letter) |
| P5 m* ranks m (ρ ≥ 0.6) | Spearman 0.77 over 10 periods | supported |
| P6 work and attention agree in sign in ≥ 2/3 | 7/11 (0.64) | failed (narrowly) |
| P7 read > unread; in-room > other-room; cross-lab ≈ same-lab | 11/11 (A2 read split); 6/7; within ±1 in 2/9, cross-lab CI > 0 in 6/9 | mixed |
| P8 BD and neutral forms tie (\|ΔLL\| < 0.02) in ≥ 1/2 | 8/11; neutral better in #37, #38, #41 | supported |
| Kill: βĴ ≈ 0 everywhere, or P_multi < 0.5 everywhere and no replica split | βĴ ≠ 0 in 7 periods; no replica split; P_multi ≥ 0.5 only in 3 small units | multiplicity part met in substance |

**Synthesis.**
1. **The share term exists as a coefficient.** After kickoff naming, habit and cumulative size, a project's share of the active agents raises the pick odds by e^{βĴ·Δs}: βĴ ≈ +2 to +6 per unit share in shared-goal weeks. Moving from 0 to a third of the agents multiplies the odds by 2–7. It survives the kickoff-free placebo, the cross-lab split and the read split. H53's "current share predicts pile-ons" is this term.
2. **It is not identified as social coupling J.** Fast common repo bursts with no coupling give the same coefficient (A2). So does an unmodelled assignment field (#44 #best: +13.9). Read-gating is suggestive (unread options are never picked), but links mark bursts (H28), so it does not separate the two.
3. **Habit is the dominant field.** b_own ≈ 2.5–6 nats: an agent returns to a repo it held at 12–400× the odds of another option. The kickoff-naming field is small and noisy (H54's token rule).
4. **Every period is subcritical at its point estimate.** βĴ/γ_c = 0.07–0.86 for the positive fits, where γ_c is the coupling at which the fitted fields first support a second stable state. The 95% upper bound crosses γ_c in 7 of 25 identified fits (#33 work, #36 attention, #37 both channels, #41 attention, #44 both channels). Habit pins agents, so even a larger J would not create multiple equilibria at these fields. Since βĴ may include burst fields, it is an upper bound on βJ, which makes the subcritical reading conservative.
5. **No multiple equilibria in replicas.** Rooms with identical kickoff text (G37) land within the one-equilibrium band. Twelve same-goal #51 units all sit in the dispersed state (m ≤ 0.21). Across periods the fitted fields reproduce the order of concentration (P5). Same-type weeks differ because their fields differ (#41's research topic vs #39/#42's own artifacts), not because they fell into different wells.
6. **Private roles are antiferromagnetic.** In #51 (and #42) agents avoid repos others are working on (βĴ −11.7 [−19.0, −4.4], 10 units). This is the AF Potts sign H11 predicted for division of labour and could not see with βJ_CW (#51 work PL ill-determined).

**Claim that stands.** Project choice has a share coefficient βĴ ≈ +2 to +6 in shared-goal weeks and ≈ −6 to −12 in own-role weeks after kickoff naming, habit and static fitness, but fast repo bursts produce the same coefficient, so J is not identified. At the fitted fields every period is below the Brock–Durlauf multiplicity boundary, and no same-field replica lands in a second state.

## Confirmatory design (frozen 2026-10-04 in `analysis/confirm.py`; dry-run on stand-ins only, NOT RUN)
Targets #45, #46, #47, #50 and the #51 tail (51m); #48, #49 reported, not scored. C1: M4 βĴ > 0 with CI > 0 in work or attention in ≥ 1/2 of testable targets. C2: P_multi < 0.5 in ≥ 90% of identified unit-channel fits (SE of βĴ ≤ 5) over all targets. C3: #51 tail work βĴ < 0 with CI < 0. C4: cross-lab coefficient > 0 in ≥ 2/3 of the target-channels where C1's CI is > 0. Fixed caveat: C1 confirms a share coefficient, not J (A2). Dry run (stand-ins #38, #41, units 51h–51l): C1 and C4 pass; C2 fails (10/12 fits; the two small attention units 51j, 51l) and C3 fails (stand-in pooled −18.3 [−49.1, 12.5]): a pipeline check, not evidence. Guard: `--confirm --i-understand-this-uses-the-locked-holdout`, a committed H93 folder, `holdout_ledger.check()` (family `project_potts`). Reuse: H11, H53, H78 plan #45–#51-tail uses with other statistics; disclose per the reuse policy.

## Round 2 redirects (proposed by the round-1 agent, 2026-10-04)
- **H93-R1. Separate J from bursts.** Use an in-flight design: share among hosts whose arrival the chooser could not yet have read (arrival after its last receiving call) vs read hosts at a matched lag. Or use exogenous share shocks (expiries, roster exits, outages) as instruments for s_j.
- **H93-R2. Put assignment fields in the model.** Add DQ6 room and team assignments and the leader's module assignments as field terms; re-test #44 #best and #45.
- **H93-R3. Habit as an agent constant.** b_own ≈ 4 nats in most periods: test it as an agent-level property (exception (b)) and relate it to H58's return to the own artifact.

## Notes
- 2026-10-04: round-1 agent (H93 together with H94). Card written before any choice statistic; A1 after the synthetic, before any real fit; A2 post hoc (disclosed).
- Compute: ≤ 2 threads, one heavy job at a time, no LLM labels. P_multi uses 200 parametric draws (100 for #51).
