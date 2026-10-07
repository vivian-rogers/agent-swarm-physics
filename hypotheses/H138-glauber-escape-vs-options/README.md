# H138: Glauber escape from a project grows with the number of open options

**Status:** round 1 done (2026-10-07, exploration units only): **inconclusive** by the card's rule; the literal Glauber law ε_q = 1 is rejected (added bound A3). Pooled option elasticity −0.66 [−1.64, 0.32] (work, 13 units; power 0.43 at ε_q = 0.5, so the HH381 kill cannot fire) and −0.28 [−0.42, −0.15] (attention, 31 units). Card, observables, nulls and predictions written 2026-10-07 08:15–09:10 UTC before any real-data statistic; synthetic and Amendments A1–A4 committed (3fb2a8b) before the real-data run. Reserved periods not run; no confirm script yet.
**Question (GOALS.md):** **Q2** (what is field and what is coupling: is an agent pulled off its project by the options on offer, as a Glauber Potts walker in a field predicts, or pushed off by an internal clock: finishing and trap aging?). Second: **Q5** (does an operator who opens more parallel projects raise the churn per call?).
**Fields:** stat mech (kinetic Potts, heat-bath and Metropolis single-spin updates, escape rates), stochastic processes (discrete-time hazards with time-varying covariates)
**Literature:** none in `literature/` covers kinetic Potts escape rates. Cited from memory (†): Glauber, *J. Math. Phys.* 4, 294 (1963)† (single-spin-flip kinetics; the attempt clock sets the rate); Wu, *Rev. Mod. Phys.* 54, 235 (1982)† (the Potts model); Allison (1982)† (discrete-time hazards). Model reference: [`physics-models/10-potts/README.md`](../../physics-models/10-potts/README.md).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime; Population N(t), *active population* (H85); Driving / external field; *Agent state (categorical, project, work ledger)* (H11 round 1b) as carried by *Host (work ledger, call-clock expiry)* (H77/H78, W = 30, E = 100); *Agent state (categorical, project/artifact strict)* (H11) for the attention channel; *Call clock* (H40); H54's *own-target percentile (swap null)*; H94's *owner (H94)* and *ownership price λ_own (H94)*. Used as defined in their cards (not yet in DEFINITIONS.md): H129's *project hop* and *dwell (own calls)*; H11 round 2's *choice set C(i, w)*. **New named variants proposed for DEFINITIONS.md** (not edited there; defined under Observables): **open-option count q_live (H138)**, **Glauber alternative sum Z_alt (H138)**, **leave hazard per own call h_leave (H138)**, **option elasticity ε_q (H138)**, **lead option count q_lead (H138)**.
**From:** HH381 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/10-potts/` (primary: kinetic Potts walker with Glauber updates on each agent's call clock), `physics-models/02-nonequilibrium-ising/` (secondary: single-spin-flip kinetics and the attempt clock)
**Data inputs (shared tables first):** DQ4 `work_commits` through `infra/shared/replicator_hosts.py` (work channel host labels, W = 30, E = 100; `kickoff_named` flag); `project_states` (attention channel, W = 30, strict mentions, raw project); DQ1 `call_windows` (own calls per window), `context_ledger_items` with `project_mentions_chat` (read options, variant); `activity_bins_fixed` (active-minutes variant); `rooms_timeline`; `calendar`, `period_units`, `roster`; `per_period_estimates` (H85 `active_population_N`); H54 `kickoffs.parquet` and per-kickoff results (read only); H94 per-unit `lam_own` (read only). No text is read.

## Source HH (verbatim from the HH list)
- **HH381 · The Potts escape rate grows with the number of open options as Glauber predicts.** In a Glauber Potts model at a fixed field, the rate of leaving the current state rises with the number q of available alternatives, roughly as (q − 1) e^{−βΔ}.
  - *Prediction:* across periods, the per-call leave rate rises with the number of live projects (or rooms) with slope near 1 on a log–log plot of rate vs q − 1, after controlling for the goal field.
  - *Check:* per-period q from the project and room ledgers; per-call leave rates.
  - *Kill:* the leave rate is flat in q, or falls.
  - *Impostors:* periods with many projects are also more open goals (a weaker field). Include the goal type and the kickoff-target strength (H54) as covariates.
  - *Models:* 10 · *Builds on:* H11, H94, H51

## Standards (STANDARDS.md)
**Question served:** Q2 (second: Q5).

| Impostor | Relevant? | How it is handled (planned) | Status |
| --- | --- | --- | --- |
| Scheduler field | partly | Exposure is the agent's own calls per window (the Glauber attempt clock, H40), not wall time. Agent fixed effects absorb each agent's hop propensity; a spline in active time absorbs within-unit drift. Windows never span a night. Active minutes as exposure is a variant. | removed (round 1: window-of-day and ln N_active checks leave ε̂_q unchanged) |
| Exogenous field (kickoff, goal, operator) | yes (central) | Within a unit the goal field is fixed, so the primary test uses within-unit variation of q. Kickoff-named projects are counted apart (q_named, q_free; `replicator_hosts.kickoff_named`). Operator messages that name a project enter as a window dummy (variant). Across units: goal mode, H54's own-target percentile and log N as covariates. | removed within units; partly across |
| Shared model priors (family, style) | partly | Agent fixed effects absorb each agent's hop propensity. A same-lab vs other-lab split of ε_q is a variant. | partly |
| Contemporaneous convergence | yes | H11 round 2 found joins are time-symmetric co-arrival. Lead placebo: options that appear in the 2 active hours *after* the leave (q_lead) enter beside the lagged count. Read variant: q_read counts only options the agent could have read (DQ1 ledger). | partly (round 1: the work lead placebo is unpowered, 0.42 at ε 0.5) |

**Inputs:** current shared tables only (DQ4 work ledger, deterministic `project_states`, DQ1 ledger, `activity_bins_fixed`). No old activity table.

**Two layers:**
- *Replication* (role `replication`): the within-unit option elasticity ε_q (O1) on every non-reserved unit with ≥ 25 leaves in the channel. Work channel (primary, DQ4 dense from #30): units of #30, #31, #33, #35, #36, #37, #38, #39, #40, #41, #42, #44 and 51a–51l. Attention channel (secondary): units of #18–#21, #23–#27, #30, #31, #33, #35–#42, #44 and 51a–51l. Testability (≥ 25 leaves) is decided from structural counts before any hazard statistic.
- *Natives* (role `native`): **G38** (births all through a 17-day week: the largest within-period swing in q), **G44** (two rooms in the same days with different kickoffs and different ownership prices: a cross-room contrast at fixed calendar), **G51** (12 own-role units: the H94 ownership price as the stay field Δ). Each has a dated prediction in its folder.

**Unit-of-analysis exceptions (named):** (d) **too little data per unit** for the per-unit ε_q in short units: per-unit estimates are reported next to a DerSimonian–Laird pool, never a pooled fit. The cross-period slope (O4, the HH-literal test) compares units as points on a phase diagram; it fits no model to pooled windows.

**Channels not testable on this data (declared before any statistic):** rooms. In #35–#44 the rooms are fixed for whole goal periods, and the only within-period hopper is one agent (H102: DeepSeek-V3.2, #36–#37). In #51 the room count is two throughout. So q_rooms does not vary at fixed agents, and the HH's room variant cannot be tested.

## Question
When an agent works on project a, does its chance of leaving a at each of its own calls grow in proportion to the number of other projects open at that moment, as single-spin Glauber dynamics in a q-state Potts model predicts? Or is leaving set by the agent's own clock (finishing the task, trap aging), with the options on offer only a passive menu?

**Practical payoff:** if escape scales with open options, every project an operator opens raises the per-call churn of all agents by a known factor. If not, churn is set by task length, and opening projects does not pull agents off their current work.

## Model
**From:** `physics-models/10-potts/` (kinetic Potts) with the attempt clock of `physics-models/02-nonequilibrium-ising/`.

**H138 variant: a heat-bath Potts walker in project fields, updated at the agent's own calls.** Agent i on project a at its own call c moves to project b ∈ O(c) (the open options other than a) with probability

  P(a → b at c) = ν · e^{u_b(c)} / [e^{u_a(c)} + Σ_{b′ ∈ O(c)} e^{u_{b′}(c)}],

with u_a the stay field (habit, ownership, the agent's own commits on a) and u_b the attraction of b (others' recent activity, cumulative size, habit of return). ν ≤ 1 is the attempt probability per call. When leaving is rare (H129: about 0.11–0.12 hops per 100 own calls),

  h_leave(c) ≈ ν e^{−u_a(c)} Z_alt(c),  Z_alt(c) = Σ_{b ∈ O(c)} e^{u_b(c)}.

- **Equal attractions:** Z_alt = (q − 1) e^{u}, so h_leave ∝ (q − 1) e^{−βΔ} with βΔ = u_a − u. This is HH381's law. The **option elasticity** ε_q = ∂ ln h_leave / ∂ ln(q − 1) equals 1 at a fixed stay field.
- **Unequal attractions:** the elasticity to Z_alt is 1. The elasticity to the raw count (q − 1) falls below 1 when added options are weak (for example projects with no recent activity).
- **Metropolis** updates give the same (q − 1) factor at small rates. The test does not separate heat-bath from Metropolis.
- **Stay field from H94:** if the allocation is the steady state of this walker (H94: max-ent given activity, sizes, ownership and rooms), the leave hazard from an owned repo is lower than from a non-owned one by the factor e^{−λ_own}, with λ_own H94's per-unit ownership price.

**Rivals (named):**
- **R-finish (renewal clock):** an agent leaves when its task on a ends. The hazard depends on dwell (H129: hazards age, γ < 0 in 32/39 unit-channels) and on the agent's own activity on a, not on the menu. ε_q ≈ 0. H128 found free weeks lose projects by finishing, not merging.
- **R-coarrival (H11 round 2):** leaves and new options appear in the same burst. The lagged count predicts leaves no better than the count of options that appear after the leave (ε_lag ≈ ε_lead).
- **R-field (the HH's impostor):** periods with many projects have weaker goal fields. A cross-period slope then reflects the field, not q. Within a unit the field is fixed.
- **R-capacity (bounded menu):** an agent considers only a few options (cf. H18's dilution, H113's sublinear read-out). ε_q is positive but well below 1 and falls as q grows.
- **R-label-noise (attention channel):** with more projects, mention-based labels switch spuriously more often. The work channel with call-clock expiry is the primary channel for this reason.

## Data scheme (`scheme/`)
`scheme/build.py --period G<NN> --channel {work,attention}` writes `data/processed/H138-glauber-escape-vs-options/G<NN>/` from shared tables only. Reserved days and periods are dropped with the shared reserved-data mask (`infra/shared/common.py`) and the reserved-day flags of the work ledger and `project_states`. Project names are hashed. Budget ≤ 50 MB.
- **Labels:** work channel = `replicator_hosts` host per agent and 30-min window (W = 30, E = 100); attention channel = `project_states` (W = 30, strict, raw project). The Claude Code agent is excluded.
- **Visit and leave (H129 hop, direct form):** a visit is a run of one label for one agent. A **leave** is a window in which the label changes from a to b ≠ a with no expiry in between. A visit that ends by expiry, roster exit or the unit's end is right-censored. Variant: H129's hop definition (expiry then arrival counts, hop time = arrival window).
- **Exposure:** own calls of agent i in window w (`call_windows`, all call kinds) while i holds label a. Variant: active minutes (`activity_bins_fixed`).
- **Open-option count q_live(i, w) (H138):** the number of distinct projects other than a with ≥ 1 labelled window by an agent other than i in the 4 windows before w (2 active hours; H11 round 2's lookback L). q = q_live + 1. Variants: **q_cum** = |C(i, w)| (H11 round 2's choice set: every project labelled earlier in the unit); **q_room** = options with a labelled agent in i's current room; **q_read** = distinct projects strictly mentioned (`project_mentions_chat`) in agent chat items that entered i's context (DQ1 ledger) in the 2 active hours before w; **q_named / q_free** = options split by the kickoff-named flag.
- **Lead option count q_lead(i, w) (H138):** distinct projects other than a whose first labelled window in the unit falls in (w, w + 4].
- **Glauber alternative sum Z_alt(i, w) (H138):** Σ_{b ∈ C(i, w)} exp(û_b), with û_b from H11 round 2's conditional-logit join model (α log a_b · [a_b > 0] + β₀ [a_b = 0] + γ log(1 + s_b) + η h_b). H138 refits that model in its own code, cross-fitted by day folds (the joins of day d never enter the utilities used on day d). H11's code is not imported; if a shared builder is needed, it moves to `infra/shared/` first (STANDARDS §8).
- **Stay-side covariates:** ln dwell (own calls since arrival; H129's dwell), ln(1 + a_a) (others' labelled windows on a in the last 2 active hours), own work commit on a in w − 1 (0/1), owner flag (H94 owner rule: i made the earliest agent work commit to a in DQ4).
- **Unit covariates (cross-period layer):** regime; goal mode (`goal-periods.md`); log N_active (H85); H54's own-target percentile of the unit's kickoff (missing for kickoffs with no shared target); own-role flag (H94's grouping: #39, #42, #44, #51 units); per-unit λ_own (H94).
- **Output:** `G<NN>/windows_<channel>.parquet` (agent, window, label hash, visit id, leave, calls, active minutes, q_live, q_cum, q_room, q_read, q_named, q_free, q_lead, Z_alt, dwell, a_a, own commit, owner), `G<NN>/counts.json`, `_provenance.json`; `results/`, `synthetic/`.
- **Regimes covered:** I (#18–#31), II (#33–#36), III (#37–#44, #51a–l). No unit crosses the 2026-03-24 boundary (#36 is split by `period_units`).

## Observables
*Specified 2026-10-07 08:15–09:10 UTC, before any H138 statistic.*
- **O1 option elasticity ε_q (primary, within unit).** Poisson regression of leaves per (agent, window) with log(own calls) as offset (equivalently a complementary log-log hazard per own call): ln h_leave = θ_i + s(t) + ε_q ln q_live(i, w) + γ_d ln dwell + β_a ln(1 + a_a) + β_c own commit + β_own owner. θ_i: agent fixed effects; s(t): natural spline in the unit's active time (3 df). Windows with q_live = 0 enter with an indicator and ln q_live set to 0. Cluster-sandwich SE by agent, t(G − 1) critical values (G = agents; H11 A1). Per-unit ε̂_q with 95% CI; a DerSimonian–Laird pool over testable units beside them.
- **O2 alternative-sum elasticity ε_Z:** O1 with ln Z_alt in place of ln q_live. Model comparison: day-blocked out-of-fold log score per leave, Z_alt model vs q_live model.
- **O3 lead placebo:** O1 with ln(1 + q_lead) added. The contrast ε_q − ε_lead (paired agent-cluster bootstrap, 500 draws).
- **O4 cross-period slope b_q (the HH-literal test):** per unit, r̂_u = the fitted leave rate per 100 own calls at reference covariates (dwell 100 calls, a_a = 0, no own commit, non-owner). Weighted least squares of ln r̂_u on ln(q̄_u − 1), with log N_active and the own-role flag as covariates (variant: plus H54's own-target percentile, on the units that have it). Bootstrap over units. Each unit is one point on the phase diagram; no window-level pooling.
- **O5 ownership stay field:** within units that have both owner and non-owner visits, β̂_own (the log hazard ratio owner vs non-owner) against −λ̂_own (H94, same unit). Ratio R_own = β̂_own / (−λ̂_own).
- **O6 descriptive:** leave rate per 100 own calls by unit and channel; q̄_u; the share of leaves to newborn options (b born in the 2 h before the leave).

**Estimates rows** (`per_period_estimates`, hypothesis H138): `h138_option_elasticity`, `h138_altsum_elasticity`, `h138_lead_placebo_diff`, `h138_leave_rate_ref`, `h138_owner_log_ratio`, per unit and channel, with n units and CI kind.

## Null / baseline
- **N0:** ε_q = 0 (Wald with cluster sandwich).
- **N1 within-agent day permutation of the q_live series:** keeps each agent's leave times and q marginal, breaks their alignment within a day; 1,000 draws (size check of O1).
- **N2 synthetic worlds on each unit's real skeleton** (axis F; below). They size O1 and O3 and give the power that a negative needs (STANDARDS §3).
- **Baseline for O4:** a flat line (b_q = 0) with the same covariates.

## Synthetic validation plan (axis F; runs before any real-data statistic)
Worlds keep each testable unit's real agents, windows, own-call counts, project births and expiries; only leave times and targets are redrawn. 200 replicates per world on the skeletons of #31, #38, #41, #44 and units 51c, 51g (work), and #19, #38, 51d (attention).
- **W0 renewal walker (R-finish):** discrete-time hazard per own call with H129-type aging (γ_d = −0.3 per e-fold of dwell), ε_q = 0.
- **W1 Glauber walker:** W0's aging and stay field, ε_q = 1 (and 0.5).
- **W2 co-arrival bursts (R-coarrival):** leaves cluster with other agents' arrivals at new projects in the same window; no lagged-q effect (H11 A1's burst world).
- **W3 finishing with births:** expiries trigger leaves, and births rise with the number of active agents (q and leaves share a drive).
- **W4 label noise (attention only):** spurious one-window switches at a rate ∝ q.
- **Decision rules fixed now:** O1 counts as a test only if |bias| ≤ 0.2 in W1 (both values), size ≤ 0.10 in W0 and W3, and pooled power ≥ 0.8 at ε_q = 0.5. The lead-placebo rule (O3) must hold W2's false "lag > lead" rate ≤ 0.10. If O4's power at b_q = 1 is < 0.5 on the real unit count, O4 is reported as descriptive. Estimator changes after the synthetic are dated amendments, made before real data.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R-finish (renewal clock), R-coarrival (co-arrival bursts), R-field (goal field across periods), R-capacity (bounded menu), R-label-noise (attention channel).
**Reserved periods used for confirmation:** none (round 1 used exploration units only). Planned: the reserved weeks #45, #46, #47 (shared goals) and the #51 tail (2026-09-07 → 09-21), work and attention channels, ledger family `project_potts`. A frozen, guarded confirm script is written only after exploration, and it runs only with Vivian's sign-off. Overlaps to disclose: H93, H94, H129, H77/H78 and H104 plan project statistics on the same targets.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Round 1: leave, exposure, q_live, Z_alt, owner from DQ4, project_states, call_windows, DQ1; two channels, regimes I–III; family invariance not tested |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Round 1: per-call cloglog with agent effects and a time spline; dwell measured (work γ_d +0.27, attention −0.09); no Markov-order audit |
| C adequacy | beats the null hierarchy, day-blocked out-of-fold data | 0 | Round 1: the Glauber term does not beat ε_q = 0; out-of-fold Z_alt vs q_live unstable |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | Round 1: signature ε_q = 1 rejected (A3); G38 tercile ratio 2.89 (outside ×1.5); R_own 0/13 |
| E interventional | predicts the change across a natural experiment | 0 | Round 1: no NE; G44 cross-room contrast descriptive |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Round 1: unbiased, size 0.04–0.06; power 0.89 at ε 1, 0.43 at ε 0.5 (work); attention positives < 0.3 not identified (W4) |
| G ground truth | agrees with known structure | 1 | Round 1: owners leave less (attention −0.70 [−1.02, −0.38]), as H94 in sign |
| H comparative | beats the named rivals | 0 | Round 1: does not beat R-finish (ε_q ≈ 0 or below); R-coarrival not separable in work |
| I transfer | holds in other same-mode periods, including the reserved periods | 0 | Reserved periods not run |

## Prediction
*Written 2026-10-07 08:15–09:10 UTC, before running the analysis on real data.*

**What I had seen when writing this:** the cards of H11 (round 2: work label switches per period #31 130, #38 87, #41 59, #44 67, #51 930, others 2–53; attention 14–257 per period, #51 3,604; join kernel α 0.68 [0.38, 0.98] work, 0.52 [0.36, 0.67] attention; lag − lead ≈ 0, so joins are co-arrival), H129 (hop rate 0.11 vs 0.12 per 100 own calls in own-role vs shared units; dwell hazards age, γ < 0 in 32/39; net flow to newer projects m_2 0.03–0.21), H94 (λ_own median 2.2 nats in shared weeks vs 7.8 in own-role units; G44 #best 10.2 vs #rest 4.1; G51 5.5–18), H93 (habit b_own ≈ 2.5–6 nats), H128 (free weeks lose projects by finishing), H51 (log N is the best single index; regime and N carry the phase diagram) and H54 (own-target percentiles). **Not seen:** any q count, any per-window leave count beyond the switch totals above, and any hazard or elasticity of this design.

**Synthetic (axis F).**

| # | Prediction | Counts against |
| --- | --- | --- |
| S1 | O1 recovers ε_q = 1 and 0.5 within ±0.2 in W1 and has size ≤ 0.10 in W0 | bias > 0.2 or size > 0.10 |
| S2 | O1 alone is fooled by W2 (ε̂_q > 0 in > 30% of runs); O3 separates W2 from W1 | O3's false rate > 0.10 |
| S3 | O4 has power < 0.5 at b_q = 1 with the real unit counts (a descriptive layer) | power ≥ 0.8 |

**Replication layer (work channel primary; attention reported).**

| # | Prediction [credence] | Counts against |
| --- | --- | --- |
| **P1** (primary) | **Escape rises with open options.** ε̂_q > 0 with CI above 0 in ≥ 2/3 of testable work units, and the pooled ε_q CI includes 1 and excludes 0 [0.25] | pooled CI includes 0 or lies below 0 |
| P2 | **Glauber weighting.** Pooled ε_Z ∈ [0.5, 1.5], and the Z_alt model beats the q_live model on the out-of-fold log score in ≥ 1/2 of testable units [0.2] | ε_Z CI outside [0.5, 1.5], or q_live wins in > 1/2 |
| P3 | **Escape toward options, not co-arrival.** Pooled ε_q − ε_lead > 0 with CI above 0 [0.3] | CI includes 0 or ε_lead > ε_q (R-coarrival) |
| P4 (secondary) | **H94's price is the stay field.** R_own ∈ [0.5, 2] in ≥ 1/2 of units with both owner and non-owner visits [0.2] | R_own < 0.5 in > 1/2 |
| P5 (secondary, HH-literal) | **Across units.** b̂_q ∈ [0.5, 1.5] with CI above 0 (work units) [0.2] | b̂_q ≤ 0 |

**Native layer** (each repeated in its period README).

| # | Unit | Prediction [credence] | Counts against |
| --- | --- | --- | --- |
| N1 | G38 | Inside one 17-day goal, the leave hazard per own call tracks q_live: ε̂_q CI above 0, and the q_live tercile ratio of hazards matches (q ratio)^ε̂ within ×1.5 [0.3] | ε̂_q CI includes 0 |
| N2 | G44 | Same days, two rooms: at matched owner status, the per-call hazard ratio #rest/#best equals (q̄_room,rest − 1)/(q̄_room,best − 1) within ×2. H94's prices (#best 10.2, #rest 4.1 nats) predict a higher owner stay field in #best, so owner visits are compared only within a room [0.2] | ratio outside ×2, or the sign is reversed |
| N3 | G51 | Own-role units: pooled ε_q CI above 0 over 51a–51l, and owner visits leave less than non-owner visits (β̂_own < 0, CI) [0.35] | pooled ε_q CI includes 0 |

**Kill rule (HH381).** The kill fires if the pooled within-unit ε_q CI includes 0 or lies below 0 *and* the synthetic power at ε_q = 0.5 is ≥ 0.8 (a powered flat or falling escape rate). The cross-period slope b̂_q ≤ 0 also counts against, but alone it cannot fire the kill (S3: low power).

**Hypothesis-level verdict rule.** *Supported* if P1 and P3 pass and the kill does not fire. *Narrowed* ("leaving co-occurs with more open options, but as co-arrival, not escape toward them") if P1 passes and P3 fails. *Failed* if the kill fires. *Inconclusive* otherwise, including any unpowered negative.

**My credence before data:** supported 0.15; narrowed 0.2; failed 0.4; inconclusive 0.25. Reason for the low prior: H129's own-role and shared units have about the same hop rate per call although their ownership prices differ by about 5.6 nats (H94), and H11 found co-arrival with no arrow of time.

## Results by goal period
Round 1 (2026-10-07). ε̂_q with 95% CI; W = work (host labels), A = attention. Period verdicts: supported (P1 and P3 pass), failed (CI below 0, or a powered null), descriptive (unpowered or < 25 leaves).

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication (A) | descriptive | A 0.26 [−0.29, 0.82]; power 0.52 |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication (A) | descriptive | A −0.14 [−0.61, 0.33]; power 0.71 |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication (A) | descriptive | A −0.26 [−1.07, 0.56] |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication (A) | descriptive | A −0.91 [−2.35, 0.53] |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication (A) | descriptive | A −0.32 [−1.09, 0.44] |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication (A) | descriptive | A −0.42 [−1.34, 0.51] |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication (A) | descriptive | A −0.69 [−2.06, 0.67]; permutation p 0.026 |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication (A; W 17 leaves) | failed | A −0.38 [−0.69, −0.07] (sign reversed) |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication (W, A) | descriptive | W −0.07 [−1.23, 1.09] (unpowered, 0.14); A (secondary) −0.36 [−0.67, −0.05] |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication (A; W 16 leaves) | descriptive | A 0.97 [−1.53, 3.47] |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication (A: 36a, 36bc) | descriptive | A 36a −4.53 [−9.41, 0.35]; 36bc −0.31 [−0.87, 0.24] |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication (A) | descriptive | A −0.68 [−1.99, 0.64] |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication + native N1 | descriptive | W −0.73 [−1.76, 0.30]; N1 tercile ratio 2.89 (outside ×1.5), unpowered |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication (A) | descriptive | A 1.81 [−2.20, 5.82] |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication (A) | descriptive | A 0.43 [−3.14, 3.99] |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication (W, A) | supported | W 1.86 [0.25, 3.47], lead placebo 1.80 [0.33, 4.29]; A −0.51 [−1.28, 0.25] |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication (A) | descriptive | A −0.95 [−2.57, 0.67] |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication + native N2 | descriptive | W 0.27 [−5.21, 5.74]; N2 HR 1.97 [0.41, 9.53] vs 3.32 (#best 15 leaves) |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication (51a–51l) + native N3 | failed | W pooled −1.83 [−3.19, −0.46]; A pooled −0.33 [−0.78, 0.12] |

Not testable in either channel (< 25 leaves): #23, #27, #35; work-only < 25: #30, #33, #36, #37, #39, #40, #42, 51b, 51k, 51l.

## Round 1 (2026-10-07)

### Scheme and structural counts (no outcome statistic)
`scheme/build.py` builds one row per (agent, 30-min window, visit) at risk: 19,398 work rows (952 leaves) and 26,019 attention rows (5,279 leaves) over 13 work periods (#36 split at 2026-03-24; #51 as 51a–51l) and 22 attention periods. Leaves (direct label changes) per unit-channel, from `counts.json`, decide testability (≥ 25):
- **Work (13 testable):** #31 69, #38 44, #41 35, #44 58; 51a 38, 51c 46, 51d 47, 51e 25, 51f 88, 51g 282, 51h 44, 51i 31, 51j 27. Not testable: #30 17, #33 16, #35 0, 36a 4, 36bc 13, #37 8, #39 4, #40 12, #42 13, 51b 13, 51k 7, 51l 11.
- **Attention (31 testable):** every unit except #23 (7), #27 (16) and #35 (11).
- The work leave rate is about 0.12 per 100 own calls (#38: 44 leaves in 36,897 calls at risk), as H129 found.
- The cross-fitted join model behind Z_alt is stable after a damped Newton fix (habit η 2.5–4.8 nats in the #51 units, as in H93). The first build's undamped solver diverged in #51; that build was never used for a statistic.

### Synthetic validation (axis F), before real data
`analysis/synthetic.py`: 200 replicates per world on the real skeleton of **every** testable unit-channel (13 work, 31 attention). The card's named skeletons (#31, #38, #41, #44, 51c, 51g work; #19, #38, 51d attention) are reported separately. Only leave outcomes are redrawn; rows, own calls, q series, births and actives are real. Base rates are calibrated to the real leave counts. Agent frailty θ_i ~ N(0, 0.5); aging γ_d = −0.3. Output: `data/processed/H138-glauber-escape-vs-options/synthetic/summary.json`.

| World | Truth | Work: pooled mean ε̂_q · rejection of ε_q = 0 (13 units) | Card skeletons (6) | Attention: pooled mean · rejection (31 units) |
| --- | --- | --- | --- | --- |
| W0 renewal (R-finish) | 0 | 0.02 · **0.055** | −0.03 · 0.060 | −0.04 · 0.095 |
| W1 Glauber | 1 | 1.07 · **0.89** | 1.05 · 0.90 | 1.08 · 1.00 |
| W1 Glauber | 0.5 | 0.54 · **0.43** | 0.51 · 0.41 | 0.53 · 1.00 |
| W2 co-arrival bursts | 0 | 0.43 · 0.105 | 0.39 · 0.050 | 0.21 · 0.385 |
| W3 shared drive (N_active) | 0 | −0.05 · 0.040 | −0.04 · 0.075 | −0.03 · 0.060 |
| W4 label noise (30% of leaves) | 0 | — | — | 0.29 · **0.855** |

- **Bias and coverage (S1).** Pooled bias +0.07 (ε = 1) and +0.04 (ε = 0.5) in the work channel; per skeleton −0.19 to +0.22, inside Monte-Carlo error (per-unit SD 0.42–2.1). Per-unit 95% coverage 0.90–0.95. **S1 passes.**
- **Size.** W0 0.055 and W3 0.040 (work, pooled); per skeleton 0.04–0.10. **Passes (≤ 0.10).**
- **Power at ε_q = 0.5 (pooled, work): 0.43** on all 13 testable units (0.41 on the card's 6). **Below the card's 0.8.** At ε_q = 1 the power is 0.89. Per-unit power at ε = 1 is 0.10–0.63, so the 2/3-of-units clause of P1 cannot pass even if ε_q = 1.
- **Lead placebo (S2).** O1 alone is fooled by W2 in some skeletons (51g 0.59, #44 0.20; pooled point estimate > 0 in 0.90 of replicates, pooled rejection 0.105). O3's false "lag > lead" rate in W2 is **0.100** pooled (0.040 on the card skeletons): at the card's limit of 0.10. O3's power at ε = 1 is 0.86 (work) and at ε = 0.5 is 0.42 (work), 0.995 (attention). **S2 passes, at the limit.**
- **Attention label noise.** W4 (spurious switches at a rate ∝ q_live) gives pooled ε̂_q 0.29 and rejects ε_q = 0 in 0.855 of replicates. A positive attention ε̂_q of about 0.3 cannot be told from label noise.
- **O4 power (S3).** At b_q = 1 with the 13 real work units, WLS with ln N_active and the own-role flag, and between-unit scatter τ = 0.5 (0.25): power 0.12 (0.28). **S3 passes: O4 is descriptive.**
- **A test the data can make (found in the synthetic):** the pooled work CI's upper limit falls below 1 in 0.815 of W0 replicates (truth 0) and in 0.010 of W1 replicates (truth 1). So the HH-literal value ε_q = 1 can be rejected with power 0.82 and size 0.01, although ε_q = 0.5 cannot be told from 0.

### Amendments (dated 2026-10-07, after the synthetic, before any real-data hazard statistic)
- **A1 (estimator).** O1–O3 use the binary complementary log-log hazard per window with offset ln(own calls), which the card names as equivalent to the Poisson form. In a pilot (40 replicates, #31, #38, 51g) the Poisson form was attenuated by 0.1–0.2 at ε_q = 1, because a 30-min window holds about 45 own calls and the leave indicator saturates. The cloglog form is unbiased (table above). O4's reference rate r̂_u is the cloglog intercept of a model with the stay covariates only (no agent effects, no q terms) on all at-risk rows, at dwell 100 calls, a_a = 0, no own mark, non-owner; WLS weights are 1/(se² + τ²) with τ = 0.5. N1 (G38) uses q_live terciles among rows with q_live ≥ 1. N2 (G44) fits a pooled cloglog with a room term, owner, the stay covariates and an agent-cluster sandwich (agents are nested in rooms). The O3 per-unit CI is the paired agent-cluster bootstrap (500 draws); the synthetic used the sandwich SE of the same contrast. The Poisson form is kept as a variant. In the attention channel, "own mark in w − 1" is an own labelled window on a (there is no commit).
- **A2 (untestability, declared before any outcome).** The card's rule: "O1 counts as a test only if … pooled power ≥ 0.8 at ε_q = 0.5". Work power is 0.43, so **the work O1 is not a valid test of ε_q = 0.5, and the HH381 kill cannot fire on the work channel** (it needs power ≥ 0.8). A work pooled CI that includes 0 is **inconclusive**. The attention channel has power 1.00 at ε_q = 0.5, but W4 shows that its positives below about 0.3 can be label noise; attention stays secondary, and an attention positive counts only if its pooled CI lower limit exceeds 0.29 (the W4 mean).
- **A3 (added test, pre-data).** **Glauber-literal bound:** if the pooled work ε̂_q has its 95% CI upper limit below 1, the literal HH381 law (ε_q = 1 at fixed field) is rejected (synthetic power 0.82 at ε_q = 0, size 0.01). This is an added test, not the card's kill; it is reported beside the verdict rule.
- **A4 (variants not run in round 1).** Active minutes as exposure, H129's expiry-then-arrival hop, the operator-message dummy and the same-lab split are not run (time). Room channel: untestable, as declared in the card.

### Real data (exploration units only; run 2026-10-07 after commit 3fb2a8b)
`analysis/run.py` (O1–O6, N1–N3, N1 permutation null with 1,000 draws, O3 bootstrap with 500 draws, variants) → `results/results.json`; `analysis/posthoc.py` → `results/posthoc.json` (post hoc). Scheme note: a "labelled window" of another agent is a window in which that agent holds the label (the host label carried forward until expiry), in both channels. Every estimate below is per unit, then pooled by DerSimonian–Laird (exception (d)); "[ ]" is a 95% CI.

**Prediction vs result**

| # | Prediction | Result | Verdict by the rule |
| --- | --- | --- | --- |
| S1 | O1 unbiased (±0.2) in W1; size ≤ 0.10 in W0 | bias +0.07 / +0.04; size 0.055 (W0), 0.040 (W3) | passed |
| S2 | O1 fooled by W2; O3 false rate ≤ 0.10 | O1 pooled rejection 0.105 (51g 0.59); O3 false rate 0.100 | passed (at the limit) |
| S3 | O4 power < 0.5 at b_q = 1 | 0.12 (τ 0.5), 0.28 (τ 0.25) | passed: O4 descriptive |
| **P1** (primary, work) | ε̂_q CI > 0 in ≥ 2/3 of units; pooled CI includes 1, excludes 0 | **1/13 units CI > 0** (#41: 1.86 [0.25, 3.47]); 1/13 CI < 0 (51g: −2.07 [−3.72, −0.41]); **pooled ε_q −0.66 [−1.64, 0.32]** (τ² 1.19) | **counts against**; unpowered (power 0.43, A2), so not a kill |
| A3 (added) | Glauber-literal bound: pooled work CI upper < 1 rejects ε_q = 1 | upper limit **0.32** | **ε_q = 1 rejected** (power 0.82, size 0.01) |
| P2 | pooled ε_Z ∈ [0.5, 1.5]; Z_alt wins the out-of-fold score in ≥ 1/2 units | ε_Z 0.22 [−0.12, 0.55]; Z_alt wins in 8/13 | not passed (ε_Z below 0.5); not counted against (CI reaches 0.55) |
| P3 | pooled ε_q − ε_lead > 0, CI above 0 | −0.51 [−1.47, 0.45] | failed (unpowered: 0.42 at ε 0.5) |
| P4 | R_own ∈ [0.5, 2] in ≥ 1/2 of units with both visit kinds | 0/13 (R_own −0.72 to 0.43); pooled β̂_own −0.48 [−1.32, 0.36] | failed |
| P5 (HH-literal, descriptive) | b̂_q ∈ [0.5, 1.5], CI > 0 | b̂_q −0.32 [−4.52, 5.34] (13 units); with H54's π −0.19 [−6.06, 5.87] | descriptive; sign counts against |
| N1 (G38) | ε̂_q CI > 0; tercile hazard ratio = (q ratio)^ε̂ within ×1.5 | ε̂_q −0.73 [−1.76, 0.30] (permutation p 0.18); top/bottom tercile hazard 1.20 (0.184 vs 0.153 per 100 calls at q̄ 5.2 vs 1.6); predicted 0.41; ratio 2.89 | counts against; unpowered (unit power 0.29) |
| N2 (G44) | room hazard ratio #rest/#best = q_room ratio within ×2 | #best has 15 leaves (< 25): **descriptive**. HR 1.97 [0.41, 9.53]; predicted 3.32 (q_room 10.4 vs 3.1); ratio 0.59 | descriptive (inside ×2, same sign) |
| N3 (G51) | pooled ε_q over 51a–51l CI > 0; β̂_own < 0 with CI | **ε_q −1.83 [−3.19, −0.46]** (12 units; testable 9: −1.83 [−2.86, −0.79], τ² 0); β̂_own −1.63 [−3.27, 0.00] | **failed** (sign reversed) |
| Kill (HH381, work) | pooled CI includes or lies below 0 *and* power ≥ 0.8 | CI includes 0; power 0.43 | **does not fire** (untestable, A2) |
| Attention (secondary) | same as P1 | 0/31 units CI > 0; 3/31 CI < 0; **pooled −0.28 [−0.42, −0.15]**; power 1.00 at ε 0.5; P3 −0.36 [−0.51, −0.20] (lead > lag) | the kill rule, applied to this channel, would fire |

**Hypothesis-level verdict by the card's rule: inconclusive.** P1 fails and P3 fails, but the work kill is unpowered (A2). Beside the rule: the added bound A3 rejects the literal law ε_q = 1 in the work channel (upper limit 0.32), and the secondary attention channel gives a powered negative (−0.28 [−0.42, −0.15]).

**Variants named in the card (pooled; work · attention).**
- q_cum (H11's choice set): −0.05 [−2.42, 2.32] · −0.41 [−0.86, 0.04].
- q_room (options in the agent's own room): −0.09 [−0.91, 0.73] · −0.14 [−0.27, −0.00].
- q_read (options read in the DQ1 ledger in the last 2 active hours): −0.10 [−0.68, 0.47] · −0.02 [−0.14, 0.09].
- q_named / q_free (fitted together): named +0.23 [−0.09, 0.55] (7 units) · **+0.17 [+0.03, +0.31]** (22 units); free −0.49 [−1.20, 0.23] · **−0.22 [−0.40, −0.04]**. The attention named term is below the W4 label-noise level (0.29), so by A2 it does not count as a positive.
- Poisson form (the card's first form): −0.68 [−1.53, 0.17] · −0.21 [−0.31, −0.11].
- N1 permutation null (within agent and day): p < 0.05 in 1/13 work units (#41, p 0.010) and 6/31 attention units (both signs). Every #51 work unit has p ≥ 0.095, so the Wald CIs of the #51 negatives may be too narrow.

**Stay-side terms (O1 covariates; descriptive).**
- Dwell: work γ̂_d **+0.27 [+0.19, +0.34]** (13/13 units positive): the direct-leave hazard rises with own calls on the repo. Attention γ̂_d −0.09 [−0.12, −0.05] (aging, as H129). The work sign differs from H129's aging; H129's hop includes expiry-then-arrival, which this direct-leave design censors.
- Owner: attention β̂_own **−0.70 [−1.02, −0.38]** (owners leave less, as H94's price predicts in sign); work −0.48 [−1.32, 0.36]. Both are about 1/10 of λ_own or less (R_own −0.42 to 0.25 in attention, 0/22 in [0.5, 2]).

**O6 descriptive.** Leaves per 100 own calls: work 0.06–0.31 in testable units (0.12 in #38); attention 0.12–0.87. Mean open options q̄: work 3.0 (#38) to 20.9 (51j); attention 2.2–25.2. Share of leaves that go to a project born in the 2 h before: work 0.09–0.69 (#41 0.69, #38 0.52, #51 units 0.09–0.45); attention 0.03–0.58.

**Post hoc (not pre-registered; labelled post hoc).**
- *Covariate ladder* (pooled ε̂_q, work · attention): agent effects only −0.17 [−1.02, 0.67] · +0.18 [−0.02, 0.38]; plus the active-time spline −0.40 [−1.35, 0.54] · −0.20 [−0.40, 0.00]; O1 (plus stay terms) −0.66 · −0.28; plus first/second-window-of-day dummies −0.80 [−1.82, 0.21] · −0.30 [−0.47, −0.13]; O1 without agent effects −1.87 [−3.11, −0.62] · −0.30 [−0.42, −0.19]. The attention sign turns negative when the within-unit time trend is removed; no specification gives a positive pooled elasticity.
- *Co-activity:* adding ln N_active(w) leaves ε̂_q unchanged (work −0.60 [−1.51, 0.32]; attention −0.36 [−0.53, −0.19]; #51 work −1.73 [−2.81, −0.66]); corr(ln q, ln N) is −0.10 (work) and 0.02 (attention). A shared activity drive does not make the negative.

### Impostors (STANDARDS §1), as handled in round 1

| Impostor | Relevant? | How it was handled | Status |
| --- | --- | --- | --- |
| Scheduler field | partly | Exposure = own calls (call clock); agent effects; 3-df spline in active time; windows inside days. Post hoc: window-of-day dummies and ln N_active leave ε̂_q unchanged. Active minutes as exposure not run (A4). | removed |
| Exogenous field (kickoff, goal, operator) | yes | Within a unit the goal is fixed. Named vs free options split (attention: named +0.17, free −0.22). Across units, O4 with ln N, own-role and H54's π is descriptive (power 0.12). Operator dummy not run. | removed within units; partly across |
| Shared model priors | partly | Agent effects absorb each agent's hop propensity; same-lab split not run. | partly |
| Contemporaneous convergence | yes | Lead placebo O3 (work −0.51 [−1.47, 0.45], unpowered; attention lead > lag, −0.36 [−0.51, −0.20]); q_read variant (DQ1 ledger) ≈ 0. | partly |

### Scorecard (round 1)

| Axis | Score | Evidence |
| --- | --- | --- |
| A mapping | 1 | Leave, exposure, q_live, Z_alt and owner defined from DQ4, project_states, call_windows and the DQ1 ledger; two channels, regimes I–III. Invariance across families not tested. |
| B assumptions | 1 | Per-call cloglog hazard with agent effects and a time spline; dwell structure measured (work γ_d > 0, attention < 0). No Markov-order or update-order audit. |
| C adequacy | 0 | The Glauber term does not beat ε_q = 0 (work CI includes 0; attention CI below 0). Out-of-fold Z_alt vs q_live score is unstable (|Δ| up to 18 nats per leave in small units). |
| D unfitted predictions | 1 | Unfitted checks run: G38 tercile ratio (2.89, outside ×1.5), O4 slope (descriptive), ownership ratio R_own (0/13). The model's signature ε_q = 1 is rejected. |
| E interventional | 0 | No natural experiment used; G44's cross-room contrast is descriptive (15 #best leaves). |
| F identifiability | 1 | Real-skeleton synthetic: unbiased (≤ 0.07 pooled), size 0.04–0.06; power 0.89 at ε 1 but 0.43 at ε 0.5 (work). Attention positives below 0.3 are not identified (W4). |
| G ground truth | 1 | Owners leave less in the attention channel (−0.70 [−1.02, −0.38]), agreeing in sign with H94's ownership structure; magnitude about 1/10 of λ_own. |
| H comparative | 0 | Glauber does not beat R-finish (ε_q ≈ 0 or below); the lead placebo cannot separate R-coarrival in the work channel. |
| I transfer | 0 | Reserved periods not run. No positive elasticity in regimes I–III or in either channel (exploration only). |

**Claim that stands:** Within goal periods, an agent's per-call chance of leaving its project does not rise with the number of other open projects: the pooled option elasticity is −0.66 [−1.64, 0.32] in the work channel (13 units) and −0.28 [−0.42, −0.15] in the attention channel (31 units), so HH381's Glauber law ε_q = 1 is rejected (work upper limit 0.32; power 0.82, size 0.01). *Exclusions:* the HH381 kill (ε_q = 0 vs 0.5) is untestable in the work channel (power 0.43); the attention negative is secondary and depends on the active-time spline (post hoc ladder); G51's negative (−1.83) rests on Wald CIs with permutation p ≥ 0.095 per unit; #41's single positive unit (1/13); P2's out-of-fold scores (unstable); O4 and N2 (descriptive); the named-option term (below the label-noise level).

### Round 2 redirects
- **H138-R1. Move to the call clock.** One row per own call (not per 30-min window) raises the work power and lets the lead placebo work at the read-out scale (Known issue: 30-min lead placebos cannot separate co-arrival).
- **H138-R2. Explain the negative elasticity.** Test whether q_live rises inside a unit while leaving falls (project accumulation vs settling) with a same-time cross-agent q shuffle, and whether the #51 negative survives a permutation-calibrated pool.
- **H138-R3. Named vs free options.** The attention split (named +0.17, free −0.22) suggests that only kickoff-named options pull. Test it with H54's targets on the call clock.
- **H138-R4. Reconcile dwell.** Direct-leave hazards rise with dwell in the work channel (+0.27) while H129's hops age; fit both definitions on the same rows.
- **H138-R5. Confirmation.** Freeze `confirm.py` for #45–#47 and the #51 tail (not written in round 1).

## Results
**Round 1 (2026-10-07): inconclusive by the card's rule; the Glauber law ε_q = 1 is rejected.** Within goal periods the per-call leave hazard does not rise with the number of open projects: pooled ε_q −0.66 [−1.64, 0.32] (work, 13 units) and −0.28 [−0.42, −0.15] (attention, 31 units). The work kill is unpowered (0.43 at ε_q = 0.5), so the card's verdict is inconclusive; the added bound A3 rejects ε_q = 1 (upper limit 0.32). Own-role #51 units give a negative elasticity (−1.83 [−3.19, −0.46]). Details: Round 1 above.

## Notes
- 2026-10-07 08:15 UTC: card written from HH381 (approved by Vivian 2026-10-07). Protocol for round 1: card → period predictions → synthetic on the real skeleton → dated amendments → replication and natives → estimates → frozen confirm script (not run) → summary.
- The rooms variant of HH381 is declared untestable above (one within-period hopper in #35–#44; two fixed rooms in #51).
- Sibling cards from the same HH batch use the same labels: H133 (HH376, read-out Glauber Potts), H134 (HH377, context self-field and stickiness), H135 (HH378, detailed balance from H94's occupancies), H137 (HH380, nonreciprocal hops). H138 does not use their outputs.
- **Proposed DEFINITIONS.md variants (H138):** *open-option count q_live (H138)* = distinct projects other than the agent's current one with ≥ 1 labelled window by another agent in the previous 4 windows (2 active hours); *lead option count q_lead (H138)* = projects whose first labelled window falls in the next 4 windows; *Glauber alternative sum Z_alt (H138)* = Σ exp(û_b) over H11's choice set with cross-fitted conditional-logit utilities; *leave hazard per own call h_leave (H138)* = direct label changes per own call (call clock), expiry censored; *option elasticity ε_q (H138)* = ∂ ln h_leave / ∂ ln q_live within a unit at fixed stay covariates.
