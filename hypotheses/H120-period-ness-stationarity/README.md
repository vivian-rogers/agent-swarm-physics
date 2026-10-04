# H120: Is a goal period a stationary NESS? Within-period drift of J and EP (#38, #51 main)

**Status:** exploratory round 1 done (2026-10-04, non-holdout only): **failed (the HH kill fires).** #38 is not a stationary NESS: its first and second halves differ about twice as much as random day halves in the kinetic Ising fit of 1-min activity (drift ratio R 1.95, p 0.002; trend R 2.22, p 0.001) and talk (R 2.18; 2.60), Holm ≤ 0.008, surviving weekday-stratified splits and dropping the kickoff day. The drift is gradual, not a step: NE17 ranks 0.36 (activity) / 0.21 (talk) among #38's 14 day boundaries. The 8-day unit 38a shows no drift (R 1.28, p 0.13; activity power 0.85). #51's main body drifts as predicted (R 2.17 / 2.14, p 0.001); its 08-05 room and bookend boundary ranks in the top 13% (activity). Replication: drift in 4 of 8 long units (8 talk, 19a, 27, 51g); no rejection in 4c, 6b and 13 (all underpowered) and 38a. Entropy production shows no drift where testable, but the EP test has power ≤ 0.30. Card and predictions written 2026-10-04 22:03–22:05 UTC; Amendment 1 at 22:59 UTC after the synthetic, before real data; post hoc checks labelled. `analysis/confirm.py` frozen (SHA-256 23:08 UTC) and dry-run, not run. Approved by Vivian in the dashboard vetting panel 2026-10-04 from HH360.
**Question (GOALS.md):** **Q2** (what is field and what is coupling: a field that drifts inside a period is read as coupling or as noise by every within-period fit), and the project's unit-of-analysis rule itself (CLAUDE.md: "fit models within a period"). Secondary: **Q6** (is the entropy production of a period a property of a steady state?).
**Fields:** stat mech (kinetic Ising inference; nonequilibrium steady states), stochastic thermodynamics (entropy production of a stationary vs a drifting process), statistics (score tests for parameter drift; permutation calibration)
**Literature:** `physics-models/02-nonequilibrium-ising/README.md` (kinetic Ising; σ = Σ(J_ij − J_ji)D_ij); [Aguilera, Ito & Kolchinsky 2026](../../literature/aguilera-2026-entropy-production-nonequilibrium-maxent.md) (Newton-step EP bound); Roudi & Hertz, *PRL* 106, 048702 (2011)† (kinetic Ising inference); Nyblom, *JASA* 84, 223 (1989)† and Hansen, *J. Policy Model.* 14, 517 (1992)† (score tests for parameter constancy). († = cited from memory.) Project cards: H90 (collective talk EP needs G51-size data; corrected Newton estimator), H14/H76 (behavior EP; trimming), H91 (content modes rotate about 1 SD a day more than a stationary swarm), H92 (tomorrow's content matrix is forecastable from today's), H108 (#38 room direction pinned out to six days), H50/H38 (activity co-movement is the scheduler; trim first).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent (Claude Code excluded); Population N(t) (variant *day-present*, H36); Regime; Driving / external field; Agent state, variant *binary spin* (1-min activity: state ≥ 3; 1-min talk: talk > 0; H90); Entropy production / irreversibility, named variant **"entropy production (AIK cross-agent bound)"** (H14/H90) with the corrected held-out Newton estimator. New named variants proposed here (defined under Observables; DEFINITIONS.md not edited): **core agent set**, **drift score W**, **drift ratio R**, **EP drift ΔΣ**, **boundary rank**.
**From:** HH360 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/02-nonequilibrium-ising/`
**Data inputs (shared tables first):** `activity_bins_fixed` (never the old `activity_bins`), `calendar` (weekday, active window), `period_units`, `roster`, `hypotheses/holdout.json` via `holdout_mask`; shared code `infra/shared/nulls.all_present_window` (DQ8 trim) and `infra/shared/ep_newton.newton_heldout_from_folds` (corrected estimator; compare only with nulls from the same estimator, infra Known issues). No text.

## Source HH (verbatim from the HH list, including refinements)
- **HH360 · Is a goal period a stationary NESS? Within-period drift of J and EP (#38, #51 main).** The project fits models within a period, which assumes a stationary state inside it. The 17-day charity drive (#38) and the long #51 main body test that assumption.
  - *Prediction:* weekly J matrices and EP agree within bootstrap CIs inside #38; #51 drifts slowly (H91: about 1 SD a day in content modes).
  - *Check:* rolling kinetic Ising fits with fixed hyperparameters; compare drift with split-half placebo noise.
  - *Kill (of stationarity):* drift beyond placebo noise in #38. Then the period, not the step change, is the wrong unit.
  - *Impostors:* weekday and session-length fields removed first.
  - *Models:* 02 · *Builds on:* H91, H92, the unit-of-analysis rule

## Question
Every hypothesis in this project fits its model inside one goal period (split at step changes) and treats the fit as one point on a phase diagram. That assumes the period is a stationary nonequilibrium steady state: the same couplings J, fields h and entropy production σ on every day. Inside the long periods (#38: 17 days; the #51 main body: 45 days; and every other unit of ≥ 8 days), do J and σ stay within day-to-day placebo noise, or do they drift?

## Design: two layers (STANDARDS §4)
- **Natives** (role `native`), each with its own dated prediction:
  - **G38 whole period** (17 days, 04-02 → 04-24): the HH's test and kill. It crosses NE17 (04-14 outreach approval), NE18 (04-20 history search) and two roster joins (04-17, 04-22); the core agent set excludes the joiners.
  - **38a** (8 days, 04-02 → 04-13, no step change inside): within-unit stationarity, so the kill can be read as "period wrong, unit right" or "unit wrong too".
  - **#51 main body** (non-holdout units 51a–51l, 07-06 → 09-04, 45 days): the HH predicts drift. Core agents only.
  - **Step vs trend at unit boundaries (#38 and #51 main):** the change across each step-change boundary (38a|38b at NE17; 51f|51g at 08-05, room split and bookend stop; 51g|51h at 08-24, rooms merged and nudges stopped after 08-20) ranked against every other day boundary of the same period (empirical boundary placebo, physics-models/11 pitfall on fitted nulls at boundaries).
- **Replication** (role `replication`): the same estimator on every non-holdout period unit with ≥ 8 active days: **4c, 6b, 8, 13, 19a, 27, 38a, 51g** (38a doubles as a native).
- **Exception (CLAUDE.md (c)):** the whole-#38 and #51-main tests deliberately span step changes, because the unit boundary is the object: the HH asks whether the period or the unit is the right stationary window. Their fits are reported next to the per-unit fits; neither replaces them.

## Model
**From:** `physics-models/02-nonequilibrium-ising/` (kinetic Ising, logistic Glauber updates on a 1-min grid).

Core agent i's spin s_i(t) ∈ {0, 1} at minute t of a day's all-present window updates as

  logit P(s_i(t+1) = 1 | s(t)) = h_i + Σ_j J_ij s_j(t) + Σ_w φ_{i,w} WD_w(day) + ψ_i L(day)

with J_ii the self-coupling (persistence), WD the weekday dummies (Monday reference) and L the standardized length of the day's trimmed window (the session-length field). Fixed hyperparameters across every window and period: ridge λ_J = 1 on J (unpenalized h, φ, ψ), 1-min steps, the DQ8 trim.
- **Stationary NESS (R-stat):** θ_i = (h_i, J_i·) is the same on every day; days are exchangeable given the weekday and session-length fields. Day-level noise (overdispersion) is allowed: it is exchangeable.
- **Slow drift (R-drift):** θ_i(d) = θ_i + τ_d δ_i with τ_d the day rank (a trend) or a smooth change.
- **Steps (R-step):** θ constant within period units, changing at step-change boundaries.
- **Entropy production.** With asymmetric J the steady state is a NESS with σ = Σ_ij (J_ij − J_ji) D_ij > 0. σ is estimated model-free (AIK Newton bound) on the antisymmetric observables g_ij(t) = s_i(t+1)s_j(t) − s_j(t+1)s_i(t) (i < j, the pair block) and u_i = 1[001] − 1[100], v_i = 1[011] − 1[110] over (t, t+1, t+2) (the single-agent block; H90).

**Rivals.** R-stat (HH for #38), R-drift (HH for #51), R-step (the current unit rule is right), R-weekday (weekday or session-length fields alone make halves differ; removed by design).

## Data scheme (`scheme/`)
`scheme/build.py` → `data/processed/H120-period-ness-stationarity/` (≤ 30 MB, `_provenance.json`). Non-holdout days only (asserted with `holdout_mask` and `calendar.holdout`).
- **Windows** (`windows.parquet`): one row per analysed window W (each replication unit; G38; 38a; #51 main): days, core agents, dropped days.
- **Core agent set:** agents (Claude Code excluded) with an activity record (state ≥ 2) on ≥ 90% of W's days. Days on which a core agent has no record are dropped from W (counted). Non-core agents are ignored (they act as an unmodelled field).
- **Spin grids** (`grids/<W>_<channel>.npz`, uint8): per kept day, the 1-min spins of the core agents on that day's all-present window (shared `nulls.all_present_window` over the core agents: minutes where every core agent is between its first and last record). Channels: activity (state ≥ 3), talk (talk > 0). Per day: weekday, trimmed length.
- **Regimes covered:** I (4c, 6b, 8, 13, 19a, 27) and III (38a, 51g, G38, #51 main).

## Observables
*Written 2026-10-04 ~22:04 UTC, before any H120 statistic on real data.*
- **Pooled fit.** Per core agent, penalized logistic MLE of θ_i = (h_i, J_i·, φ_i, ψ_i) on all kept transitions of W (Newton–IRLS).
- **Per-day score and information.** At the pooled θ̂: per-day gradient g_{i,d} and Hessian H_{i,d} of the unpenalized log-likelihood.
- **Drift score W(τ)** for a day contrast τ (Σ_d τ_d = 0) on the drift parameters (h_i, J_i·): U_i = Σ_d τ_d P g_{i,d}; efficient information V_i = Σ τ_d² P H_d P − (Σ τ_d P H_d)(Σ H_d + λR)⁻¹(Σ τ_d H_d P); **W = Σ_i U_iᵀ V_i⁻¹ U_i** (a score test; under a correctly specified stationary model it is χ² with N(N+1) degrees of freedom, but day-level overdispersion inflates it, so it is calibrated by permutation only).
  - **T1 split:** τ = first ⌊n/2⌋ days vs the rest (contiguous halves).
  - **T2 trend:** τ_d = centred day rank.
  - **Drift ratio R = W_obs / mean(W_null)**; R ≈ 1 under R-stat.
  - **One-step drift** δ̂_i = V_i⁻¹U_i; reported as ‖δ̂_J‖_F (logits) over the contiguous split and over the null.
- **T3 EP drift ΔΣ = Σ̂(second half) − Σ̂(first half)**, Σ̂ = corrected held-out Newton bound (`ep_newton.newton_heldout_from_folds`, blocks single/pair, c = 1) on the observables above, nats per minute (system step); folds = days merged by rank mod min(5, days in the half). Also Σ̂ of the whole window and per calendar week.
- **Weekly profile (descriptive; the HH's "weekly J matrices"):** per calendar week, the one-step weekly θ_w = θ̂ + (H_w + λR)⁻¹(g_w − λRθ̂) with a day bootstrap (200) for 95% intervals; share of J entries whose weekly intervals all overlap.
- **Boundary rank (natives):** W(τ_b) for the split at boundary b (days before vs after), ranked among the splits at every other day boundary with ≥ 2 days on each side.
- **Per-day drift in placebo units:** z_W = (W_obs − mean W_null)/sd W_null, divided by the number of days, for comparison with H91's "about 1 SD a day".

## Null / baseline
- **N1 Random day splits (the HH's "split-half placebo noise").** 1,000 random balanced partitions of W's days (unstratified; weekday is a nuisance field in the fit). p = (1 + #{W_null ≥ W_obs}) / (1 + 1,000). A weekday-stratified version is reported where ≥ 20 distinct stratified splits exist.
- **N2 Day-order permutations** for T2 (1,000).
- **N3 The same random splits for ΔΣ** (two-sided), same estimator (corrected Newton) on both halves.
- **N4 Synthetic worlds (axis F; run first)** on the real skeletons (core agents × trimmed minutes × kept days) of G38, 38a, #51 main and the replication units: (S0) stationary kinetic Ising with day-level field noise (h_{i,d} = h_i + N(0, 0.3²)); (S1) S0 plus weekday fields (±0.3 logits) and a session-length field; (S2) linear drift of J: ΔJ over the window with element SD = 1 × the SD of the generating off-diagonal J (σ_J = 0.3), the "drift that matters"; (S3) half that drift; (S4) a step at the unit boundary of the same total size. Generating h_i from each agent's marginal rate (a skeleton descriptive), J_ii = 2.0 (activity) / 0.5 (talk), off-diagonal J ~ N(0, 0.3²). 100 worlds per setting.
- **Holm** across the two channels × three tests (T1, T2, T3) within a window.

## Impostors (STANDARDS §1)
| Impostor | Relevant? | How it is handled | Status |
| --- | --- | --- | --- |
| Scheduler field | yes | DQ8 all-present trim over core agents; weekday and session-length fields in every fit (the HH's named fields); days are the permutation unit, so exchangeable day-level schedule noise cannot fake drift. A schedule that trends inside a period (e.g. NE43's bookend stop in #51) is a real drive change and is separated by the boundary test, not removed. | removed (day-level); partly (#51 drive steps) |
| Exogenous field (kickoff/goal/operator) | yes | One goal per window; the kickoff day is kept, so a kickoff transient can make the contiguous split differ. Checked by a robustness run that drops each window's first day. Operator and nudger changes inside #51 (NE43) are tested as boundaries. | partly |
| Shared model priors (family, style) | no | Each agent's own h_i and J_i· are free; the claim is about constancy in time, not about agent differences. Roster turnover is excluded by the core set. | n/a |
| Contemporaneous convergence | no | No coupling claim: J here is a fitted lagged dependence whose constancy is tested, whatever it measures (H50: activity J is mostly the scheduler, talk J is gated reading). | n/a |

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R-stat, R-drift, R-step, R-weekday (above).
**Locked holdout used for confirmation:** none run. `analysis/confirm.py` (frozen 2026-10-04 23:08 UTC; guarded by `--confirm`, `H120_CONFIRM=1`, a SHA-256 freeze of `confirm.py` and `h120lib.py`, and the holdout ledger with family `kinetic_ising_couplings`) targets the #51 tail (2026-09-07 → 09-18) and unit 1a (#1, 2025-04-02 → 04-14): C1 the tail's activity drifts at Holm 0.05 [0.4]; C2 its activity R_split ≥ 1.3 [0.4]; C3 1a shows no drift [0.5]. Credences for C1/C2 were lowered after the dry run (the last 10 non-holdout #51 days gave R 1.12, Holm 0.18). Dry run on stand-ins (last 10 days of 51main; #27): fail/fail/fail, as the stand-ins imply. The earlier plan to include #47 (5 days) was dropped: 5 days cannot split.

| Axis | Test (plan) | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | spins, trim, core set and fields from dataset fields | 1 | see Round 1 scorecard |
| B assumptions | this card tests B (stationarity) for every other card; Markov order 1 assumed | 1 | stationarity fails |
| C adequacy | permutation-calibrated drift tests; EP against the same estimator | 2 | size ≤ 0.12; robust to stratification and day-1 drop |
| D unfitted predictions | drift ratios and boundary ranks are not fitted | 1 | #38 failed, #51 supported |
| E interventional | step-change boundaries vs ordinary day boundaries | 1 | NE17 not special; 08-05 top 13% |
| F identifiability | real-skeleton synthetic: size under day noise and weekday fields; power at the drift that matters | 2 | power 1.00 (G38, #51 activity); EP unpowered |
| G ground truth | known steps (NE43, 08-05/08-21) should rank high in #51 | 1 | 08-05 yes, 08-24 no |
| H comparative | R-stat vs R-drift vs R-step | 1 | R-drift wins; R-step not at NE17 |
| I transfer | 8 replication units; holdout | 1 | 4/8 units drift; holdout not run |

## Prediction
*Written 2026-10-04 ~22:04 UTC, before the synthetic validation and before any H120 statistic on real data.*

**What I had seen when writing this (so these are not blind):** H90's card (G38 talk power 0.45 for collective EP; G51 talk EP on named partners), H76 (behavioral excess EP is the day end; trimming removes it), H91 (content rotates about 1 SD a day more than a stationary swarm), H92, H108 (#38 room direction pinned out to six days), H50 (activity J is scheduler-dominated). Skeleton facts only: the calendar windows (#38: 4-h days, one 7.6-h window on 04-16; #51: 8-h days with long windows on 07-07, 07-10, 07-28; regime-I units 2–4 h), period-unit boundaries and roster joins. No H120 fit, drift statistic or EP had been computed.

- **P0, synthetic (axis F; run first).** On the real skeletons: (a) T1, T2 and T3 have size ≤ 0.07 in S0 and S1 (day noise, weekday and session-length fields) [0.7]; (b) power ≥ 0.8 for T1 or T2 (activity) at the drift that matters (S2) in G38 and #51 main [0.6]; in units of 8–10 days power may fall below 0.8, and there a non-rejection is "inconclusive" (STANDARDS §3); (c) the boundary rank puts a planted step (S4) in the top 10% of boundaries in ≥ 70% of worlds [0.5].
- **P1, G38 whole (HH: stationary).** No drift test (T1, T2, T3; both channels) rejects at Holm 0.05 [0.4]. *HH kill:* any rejection. Then the period is the wrong unit.
- **P2, 38a (within unit).** No test rejects [0.6].
- **P3, #51 main (HH: drifts).** T1 or T2 rejects in activity [0.7] and in talk [0.5]; R_split ≥ 1.5 in activity [0.6].
- **P4, boundaries.** NE17 (04-14) ranks in the top 20% of #38's boundaries [0.3]; in #51, the 08-05 or 08-24 boundary ranks in the top 20% [0.55].
- **P5, replication units (4c, 6b, 8, 13, 19a, 27, 38a, 51g).** No rejection in ≥ 6/8 [0.55]; units with power < 0.8 are reported as inconclusive, not stationary.
- **P6, EP.** Σ̂ per half agrees within the split null (T3) in G38 [0.65] and drifts in #51 main [0.4].

**Verdict rules (per window, both channels).**
- **supported** (stationary NESS) if no test rejects at Holm 0.05 and T1/T2 power ≥ 0.8 at S2 for that window's skeleton; **failed** if T1 or T2 rejects in either channel (drift beyond placebo noise); **mixed** if only T3 rejects; **inconclusive** (written as mixed with the reason) if nothing rejects but power < 0.8.
- *For #51 main the HH predicts drift:* the native is **supported** if T1 or T2 rejects, **failed** if nothing rejects with power ≥ 0.8.
- *Hypothesis level (HH360):* **supported** if G38 is stationary (supported) and #51 main drifts; **failed** if G38 drifts (the kill); **mixed** otherwise. The 38a and boundary natives say which unit is right: R-step if 38a is stationary while G38 drifts and NE17 ranks in the top 20%.

### Amendment 1 (after the synthetic validation, before any H120 fit on real data)
*2026-10-04 22:59 UTC.* `analysis/synthetic.py`: 60 worlds per setting (20 for the 25–27-agent windows 51main and 51g), 200 permutations (100 for the big windows), 100 EP permutations (40). Output: `data/processed/H120-period-ness-stationarity/synthetic/summary.json`. Rejection rates at p < 0.05:

| Window (N core, days) | size S0 / S1, act (T1 or T2) | size S0 / S1, talk | power S2 act (T1 or T2) | power S2 talk | power S2 T3 (EP) act | step S4 in top 10% of boundaries |
| --- | --- | --- | --- | --- | --- | --- |
| G38 (11, 17) | 0.05 / 0.07 | 0.10 / 0.07 | **1.00** | 0.43 | 0.23 | act 1.00, talk 0.67 |
| 38a (12, 8) | 0.05 / 0.13 | 0.03 / 0.07 | **0.85** | 0.18 | 0.12 | – |
| 51main (25, 41) | 0.10 / 0.05 | 0.00 / 0.10 | **1.00** | **1.00** | 0.30 | act 1.00, talk 1.00 |
| 51g (27, 13) | 0.00 / 0.10 | 0.15 / 0.00 | **1.00** | **0.80** | 0.05 | – |
| 27 (10, 10) | 0.03 / 0.10 | 0.07 / 0.10 | **0.93** | 0.42 | 0.10 | – |
| 19a (7, 9) | 0.10 / 0.17 | 0.07 / 0.12 | 0.77 | 0.45 | 0.10 | – |
| 13 (6, 10) | 0.10 / 0.10 | 0.03 / 0.08 | 0.45 | 0.43 | 0.07 | – |
| 8 (4, 18) | 0.05 / 0.03 | 0.10 / 0.03 | 0.55 | 0.33 | 0.13 | – |
| 4c (4, 18) | 0.03 / 0.08 | 0.03 / 0.08 | 0.65 | 0.53 | 0.12 | – |
| 6b (4, 9) | 0.12 / 0.13 | 0.07 / 0.12 | 0.15 | 0.30 | 0.03 | – |

- **P0(a)** passes for single tests within Monte-Carlo error (T1, T2, T3 each ≤ 0.12 with 20–60 worlds, under day noise, weekday and session-length fields). The unadjusted union "T1 or T2" reaches 0.17 (19a, S1), so verdicts use Holm across the six tests of a window, as the card already specifies (Holm-3 per channel ≤ 0.10 in every window and setting).
- **P0(b)** passes for activity in G38 (1.00), 51main (1.00), 51g (1.00), 38a (0.85) and 27 (0.93); talk is powered only in 51main (1.00) and 51g (0.80). Regime-I units with 4–7 agents (4c, 6b, 8, 13, 19a) are below 0.8 in both channels, so a non-rejection there is **inconclusive**.
- **EP drift (T3) is underpowered everywhere** (power 0.03–0.30 at the drift that matters). A T3 non-rejection is inconclusive; the EP clause (P6) can only fail by a rejection.
- **P0(c)** passes: a planted step of the S2 size ranks in the top 10% of day boundaries in 100% of activity worlds (G38, 51main) and 67–100% of talk worlds.
- **Clarification of the verdict rule (not a change of threshold):** power is judged per channel. A window is **supported** (stationary) if no test rejects at Holm 0.05 and its activity channel has power ≥ 0.8; the talk channel is reported as inconclusive where its power is < 0.8. A window whose activity power is < 0.8 and with no rejection is **inconclusive** (written as mixed).
- No prediction changes.

## Results by goal period
R = drift score W over the mean placebo W (1,000 random day splits for T1, day-order permutations for T2); p permutation; Holm over the six tests of a window. Activity first, talk second.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication (unit 4c) | mixed (inconclusive) | 4 agents, 18 d: R 1.01 / 1.40, p 0.45 / 0.14; power 0.65 / 0.53 |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication (unit 6b) | mixed (inconclusive) | 4 agents, 9 d: trend R 2.31, p 0.01 (Holm 0.06); power 0.15 / 0.30 |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | failed (talk drift) | 4 agents, 18 d: activity R 0.99; talk trend R 2.27, p 0.008 (Holm 0.048); talk power 0.33 |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | mixed (inconclusive) | 6 agents, 10 d: R 1.07 / 0.99; power 0.45 / 0.43 |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication (unit 19a) | failed (drift) | 7 agents, 9 d: trend R 1.76, p 0.001 (Holm 0.006); split R 1.66 / 1.64 |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | failed (drift) | 10 agents, 10 d: trend R 1.71, p 0.005 (Holm 0.03); activity power 0.93 |
| [G38](goalperiod-subhypotheses/G38/README.md) | native (whole period; 38a; NE17) + replication (38a) | failed (HH kill) | whole: R 1.95 / 2.18, trend 2.22 / 2.60, Holm ≤ 0.008; 38a: R 1.28 / 1.22, Holm ≥ 0.16 (stationary, power 0.85); NE17 rank 0.36 / 0.21 |
| [G51](goalperiod-subhypotheses/G51/README.md) | native (main body; boundaries) + replication (51g) | supported (drift, as predicted) | main: R 2.17 / 2.14, trend 2.26 / 2.28, p 0.001; 08-05 rank 0.13 / 0.21; 51g: R 1.53 / 1.68, Holm ≤ 0.015 |

## Results
### Exploratory round 1 (2026-10-04; non-holdout only)
- **Scheme:** 10 windows; core agents 4–27; 1,034–18,023 trimmed minutes per window. Dropped days: 4c 05-29 (a core agent absent); 51main 07-06 → 07-09 (agents that joined on 07-09 are core but absent before), so 51main runs 07-10 → 09-04 (41 days). 0.4 MB in `data/processed/H120-period-ness-stationarity/`. Code: `scheme/build.py`, `analysis/{h120lib,synthetic,run,posthoc,write_estimates,figures,confirm}.py`. Runtime ≈ 3 min (real data), ≈ 25 min (synthetic).

**Drift tests (pre-registered).**
| Window | N, days | T1 split R (p), act / talk | T2 trend R (p), act / talk | min Holm | weekday-stratified T1 p | drop day 1: T1 p | z per day (act) |
| --- | --- | --- | --- | --- | --- | --- | --- |
| G38 | 11, 17 | 1.95 (0.002) / 2.18 (0.002) | 2.22 (0.001) / 2.60 (0.001) | 0.006 | 0.004 / 0.002 | 0.003 / 0.017 | 0.23 |
| 38a | 12, 8 | 1.28 (0.13) / 1.22 (0.027) | 1.22 (0.16) / 1.08 (0.17) | 0.16 | – (8 splits) | 0.26 / 0.03 | 0.15 |
| 51main | 25, 41 | 2.17 (0.001) / 2.14 (0.001) | 2.26 (0.001) / 2.28 (0.001) | 0.006 | < 0.001 | 0.003 / 0.003 | 0.23 |
| 51g | 27, 13 | 1.53 (0.001) / 1.68 (0.005) | 1.52 (0.001) / 1.62 (0.002) | 0.006 | 0.018 / 0.028 | 0.007 / 0.003 | 0.38 |
| 27 | 10, 10 | 1.55 (0.014) / 1.45 (0.10) | 1.71 (0.005) / 1.26 (0.18) | 0.03 | 0.09 / 0.15 | 0.04 / 0.17 | 0.26 |
| 19a | 7, 9 | 1.66 (0.015) / 1.64 (0.013) | 1.76 (0.001) / 1.49 (0.043) | 0.006 | – | 0.03 / 0.12 | 0.30 |
| 13 | 6, 10 | 1.07 (0.42) / 0.99 (0.45) | 1.03 (0.40) / 0.96 (0.49) | 0.26 | 0.46 / 0.46 | 0.42 / 0.42 | 0.02 |
| 8 | 4, 18 | 0.99 (0.48) / 1.63 (0.09) | 0.98 (0.49) / 2.27 (0.008) | 0.048 | 0.49 / 0.07 | 0.62 / 0.13 | 0.00 |
| 6b | 4, 9 | 2.07 (0.06) / 1.34 (0.22) | 2.31 (0.01) / 1.91 (0.047) | 0.06 | – | 0.57 / 0.15 | 0.20 |
| 4c | 4, 18 | 1.01 (0.45) / 1.40 (0.14) | 1.62 (0.13) / 1.60 (0.12) | 0.56 | 0.46 / 0.08 | 0.56 / 0.16 | 0.00 |

**Entropy production (corrected held-out Newton bound, nats per minute; same-estimator nulls only).** Σ̂ is indistinguishable from 0 in activity everywhere (e.g. G38 −0.9×10⁻⁵ [−4.3, 5.0]×10⁻³). Talk Σ̂ is positive only in #51 main: 1.0×10⁻² [0.24, 1.3]×10⁻² (G38 0.87×10⁻² [−0.36, 1.8]×10⁻²). EP drift (T3): no rejection except 51g activity (p 0.02, Holm 0.04), where both halves' bounds are below zero (−0.5 and −1.8 ×10⁻²), which signals estimator bias with 405 observables rather than an arrow of time. T3 power is ≤ 0.30, so "no EP drift" is inconclusive.

**Weekly profile (descriptive; the HH's "weekly J agree within bootstrap CIs").** The share of J entries whose weekly day-bootstrap intervals all overlap is 0.53 / 0.56 in G38 (4 weeks) and 0.45 / 0.32 in #51 main (8 weeks), against 0.79 / 0.75 in 38a (2 weeks) and 0.88–0.95 in two-week regime-I periods (13, 19a, 27). Mean |J_offdiag| and mean J_ii move little week to week (G38 activity 0.21 → 0.15; J_ii 1.4–1.8): the drift is in the pattern of J, not its scale.

**Boundaries (native; step vs trend).** Share of day boundaries whose split score is at least as large (smaller = more step-like):
| Window | boundary | activity | talk |
| --- | --- | --- | --- |
| G38 (14 boundaries) | NE17 04-14 | 0.36 | 0.21 |
| | join Opus 4.7 04-17 | 0.50 | 0.50 |
| | NE18 04-20 | 0.64 | 0.36 |
| | join Kimi K2.6 04-22 | 0.79 | 0.71 |
| 51main (38 boundaries) | 08-05 #focus room, bookends stop | **0.13** | 0.21 |
| | 08-24 merge (nudges stopped after 08-20) | 0.74 | 0.55 |
| | 07-17 / 07-24 joins | 0.55 / 0.45 | 0.87 / 0.58 |
| | 07-29 NE38 | 0.39 | 0.42 |
| | 09-03 NE33 | 1.00 | 0.97 |
In both periods the trend statistic exceeds the best single split, and no step change except 08-05 ranks high. The drift is a gradual walk with at most one step.

**Post hoc checks (labelled; `analysis/posthoc.py`, run after the results).**
- J-only drift (h held fixed): G38 R 1.99 (p 0.001) / 1.75 (p 0.002); 51main 2.18 / 1.46 (p 0.001); 51g, 19a, 27 also p ≤ 0.04; 38a and #8 no. The drift is in the couplings themselves, not only in base rates.
- h-only drift: #51 main R 4.6 / 4.9 (p 0.001): base rates move most there; G38 activity p 0.053, talk p 0.006.
- G38 before the first roster join (04-02 → 04-16, 11 days, crossing NE17): talk drifts (T1 p 0.008, T2 p 0.002), activity borderline (p 0.048 / 0.061). Joiners outside the core are not the cause.

**Prediction verdicts.**
| Prediction | Observed | Verdict |
| --- | --- | --- |
| P0 synthetic (a) size, (b) power, (c) step rank | (a) ≤ 0.12 per test, Holm-3 ≤ 0.10; (b) activity ≥ 0.85 in 5/10 windows, talk in 2/10, EP ≤ 0.30 everywhere; (c) 1.00 | passed for the activity J tests; EP unpowered |
| P1 G38 stationary (HH) | drift in both channels, Holm ≤ 0.008 | **failed (kill fires)** |
| P2 38a stationary | no rejection, activity power 0.85 | supported |
| P3 #51 main drifts; R ≥ 1.5 | R 2.17 / 2.14, p 0.001 | supported |
| P4 NE17 top 20%; #51 08-05 or 08-24 top 20% | NE17 0.36 / 0.21; 08-05 0.13 (activity) | failed / supported |
| P5 replication: no rejection in ≥ 6/8 | 4/8 (three of them unpowered) | failed |
| P6 EP: G38 stable; #51 drifts | G38 no EP drift; #51 none (power ≤ 0.30) | inconclusive |
| HH360 | #38 drifts (kill); #51 drifts; no step at NE17 | **failed** |

**What this means for the unit rule.** The period is not a stationary window. The step-change unit helps only because units are short: the one long regime-III unit without a step inside (51g, 13 days) drifts too, and the 8-day unit 38a does not. Every period-level fit in this project is an average over a state that moves about 0.2–0.4 placebo SD per day in the kinetic Ising parameters.

**Scorecard (round 1).**
| Axis | Score | Evidence |
| --- | --- | --- |
| A mapping | 1 | Spins, DQ8 trim, core set and fields from dataset fields; non-core agents are an unmodelled field. |
| B assumptions | 1 | This card tests B for the project: stationarity fails in G38, #51 main and 4/8 units. First-order Markov dynamics on a 1-min grid is assumed, not audited. |
| C adequacy | 2 | Permutation-calibrated score tests (synthetic size ≤ 0.12, Holm-3 ≤ 0.10 under day noise, weekday and session-length fields); G38's rejection survives weekday-stratified splits and dropping the kickoff day; EP compared only with same-estimator nulls. |
| D unfitted predictions | 1 | Drift ratios and boundary ranks are not fitted. HH predictions: #38 failed, #51 supported; boundary 1/2. |
| E interventional | 1 | Step-change boundaries tested as interventions: NE17 is not special; 08-05 ranks in the top 13% (activity). |
| F identifiability | 2 | Real-skeleton synthetic run first: power 1.00 at the drift that matters for G38 and #51 activity, 0.85 for 38a; a planted step ranks in the top 10% in 100% of activity worlds. The EP test is unpowered (stated). |
| G ground truth | 1 | One known step (08-05) ranks high; the other (08-24) does not. |
| H comparative | 1 | R-drift beats R-stat in G38 and #51 main; R-step is not supported at NE17; R-weekday removed by design and stratification. |
| I transfer | 1 | Drift replicates in 4/8 units (three non-rejections unpowered); holdout not run. |

**Claim that stands:** Inside long goal periods the kinetic Ising parameters of 1-min activity and talk drift beyond day-split placebo noise: #38's halves differ about twice as much as random day halves (R 1.95 activity, 2.18 talk, Holm ≤ 0.008) and #51's main body likewise (R 2.17, 2.14), with no step at NE17 (rank 0.36), while the 8-day unit 38a shows no drift (R 1.28, p 0.13; power 0.85). *Exclusions:* EP drift and stability (power ≤ 0.30); the 51g EP rejection (negative bounds); regime-I units with 4–6 agents (power < 0.8); the J-only, h-only and pre-join checks (post hoc).

### Round 2 redirects (suggested, 2026-10-04)
- **What the direction is really after:** how fast a swarm's dynamical parameters walk inside a period, and what window a stationary fit can use.
- **H120-R1.** Time-varying parameters: fit J(t) with a random-walk prior (Kalman or GP over days), report the drift rate per day with an interval, and place periods on the phase diagram as trajectories.
- **H120-R2.** Stationary window length: estimate the longest window whose split test passes, per regime (38a passes at 8 days; 51g fails at 13).
- **H120-R3.** Drivers of the walk: regress the weekly one-step δJ on roster share outside the core, operator message volume and project churn (DQ4).
- **H120-R4.** Content analog: the same score test on H91's content modes, to tie the two "about 1 SD a day" drifts.

## Notes
- 2026-10-04 22:03 UTC: card opened. The HH's "rolling fits with fixed hyperparameters" is implemented as one pooled fit plus per-day scores (a score test for drift), so every split and permutation uses the same hyperparameters without refitting; the weekly fits are one-step updates from the pooled fit.
- 2026-10-04 22:59 UTC: Amendment 1 (synthetic): power judged per channel; EP drift declared unpowered; regime-I 4–6-agent units inconclusive unless they reject.
- 2026-10-04 ~23:02 UTC: real-data run (1,000 permutations; 300 EP permutations, 100 in the big windows); post hoc J-only, h-only and pre-join checks run after the results and labelled.
- 2026-10-04 23:08 UTC: `analysis/confirm.py` frozen; dry run on stand-ins only. Never run with `--confirm`.
