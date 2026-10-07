# H138: Glauber escape from a project grows with the number of open options

**Status:** pre-registered (not run). Card, observables, nulls and predictions written 2026-10-07 08:15–09:10 UTC, before any H138 statistic on real data. No scheme, synthetic or analysis code has run.
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
| Scheduler field | partly | Exposure is the agent's own calls per window (the Glauber attempt clock, H40), not wall time. Agent fixed effects absorb each agent's hop propensity; a spline in active time absorbs within-unit drift. Windows never span a night. Active minutes as exposure is a variant. | removed (planned) |
| Exogenous field (kickoff, goal, operator) | yes (central) | Within a unit the goal field is fixed, so the primary test uses within-unit variation of q. Kickoff-named projects are counted apart (q_named, q_free; `replicator_hosts.kickoff_named`). Operator messages that name a project enter as a window dummy (variant). Across units: goal mode, H54's own-target percentile and log N as covariates. | removed within units; partly across |
| Shared model priors (family, style) | partly | Agent fixed effects absorb each agent's hop propensity. A same-lab vs other-lab split of ε_q is a variant. | partly |
| Contemporaneous convergence | yes | H11 round 2 found joins are time-symmetric co-arrival. Lead placebo: options that appear in the 2 active hours *after* the leave (q_lead) enter beside the lagged count. Read variant: q_read counts only options the agent could have read (DQ1 ledger). | removed (planned, by the lead placebo) |

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
**Reserved periods used for confirmation:** none (not run). Planned: the reserved weeks #45, #46, #47 (shared goals) and the #51 tail (2026-09-07 → 09-21), work and attention channels, ledger family `project_potts`. A frozen, guarded confirm script is written only after exploration, and it runs only with Vivian's sign-off. Overlaps to disclose: H93, H94, H129, H77/H78 and H104 plan project statistics on the same targets.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 0 | not run |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 0 | not run |
| C adequacy | beats the null hierarchy, day-blocked out-of-fold data | 0 | not run |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | not run |
| E interventional | predicts the change across a natural experiment | 0 | not run |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 0 | not run |
| G ground truth | agrees with known structure | 0 | not run |
| H comparative | beats the named rivals | 0 | not run |
| I transfer | holds in other same-mode periods, including the reserved periods | 0 | not run |

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
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication (regime I free week; most work switches outside #51) | pending | — |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication + native N1 (births all week) | pending | — |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication + native N2 (two rooms, two prices) | pending | — |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication (51a–51l) + native N3 (own-role) | pending | — |

Other testable units get their period folders, with the replication prediction copied and dated, before the run.

## Results
Not run.

## Notes
- 2026-10-07 08:15 UTC: card written from HH381 (approved by Vivian 2026-10-07). Protocol for round 1: card → period predictions → synthetic on the real skeleton → dated amendments → replication and natives → estimates → frozen confirm script (not run) → summary.
- The rooms variant of HH381 is declared untestable above (one within-period hopper in #35–#44; two fixed rooms in #51).
- Sibling cards from the same HH batch use the same labels: H133 (HH376, read-out Glauber Potts), H134 (HH377, context self-field and stickiness), H135 (HH378, detailed balance from H94's occupancies), H137 (HH380, nonreciprocal hops). H138 does not use their outputs.
- **Proposed DEFINITIONS.md variants (H138):** *open-option count q_live (H138)* = distinct projects other than the agent's current one with ≥ 1 labelled window by another agent in the previous 4 windows (2 active hours); *lead option count q_lead (H138)* = projects whose first labelled window falls in the next 4 windows; *Glauber alternative sum Z_alt (H138)* = Σ exp(û_b) over H11's choice set with cross-fitted conditional-logit utilities; *leave hazard per own call h_leave (H138)* = direct label changes per own call (call clock), expiry censored; *option elasticity ε_q (H138)* = ∂ ln h_leave / ∂ ln q_live within a unit at fixed stay covariates.
