# H38: Joint silences are platform stalls

**Status:** exploratory round 1 done (2026-10-04); **round 1b on the corrected tables done (2026-10-04, section below)**; confirmatory script written, not run. Predictions written 2026-10-04 01:25 UTC, before any real-data run (see Prediction). **Headline: mostly refuted as posed, but with a regime-specific yes.**
- **Joint silences are not mostly platform stalls.** Their rate is what independent agents with their own half-hour on/off rates produce (median excess over independence 0.008 of minutes). Infrastructure errors don't precede them: an error burst makes a joint silence *less* likely (median log odds −0.43). Scaffold states sit in them at roughly chance level. What is real: village-off gaps are 84% operator-scheduled.
- **In the always-on regime III, about two thirds of the collective co-activation is infrastructure.** Median f_scaffold = 0.68 over 8 significant periods. The main cause is agents starting and stopping together at the operator's daily resume and pause. The regime-III rise in co-activation (H19: +0.11) disappears once those minutes are conditioned on: +0.15 → +0.01 across NE14; +0.125 → +0.017 across periods.
- **In regime I, co-activation is not infrastructure** (f_scaffold 0.11). Talk co-activation survives everywhere.
- **Operator rule:** before reading any swarm synchrony statistic, drop off-schedule minutes and condition on not-started / finished / consolidating agent-minutes (`analysis/h38lib.py`).
- **Round 1b (corrected tables):** joint silences fall from 14.3% to 5.3% of non-holdout minutes and are now 78% operator-scheduled; the regime-III share of co-activation that is day-edge synchrony holds (f_scaffold 0.68 → 0.72; f_trim 0.83), and under the DQ8-calibrated null (trim, then block shift) only 3 of 8 regime-III periods keep a significant excess (#44, #51 and, marginally, #37) against 16 of 18 in regime I. Native test NE43: the day-edge share does **not** drop when the operator's pause/resume messages stop (08-05), so the edges are the runner's schedule, not the announcement.
**Fields:** stat mech, sociophysics, info theory
**Origin:** HH94 (`../hypohypotheses/HYPOHYPOTHESES.md`; `../promotion-shortlist.md`)
**Definitions used:** Agent; Population N(t) (variants: *present population* (H02 rule, per chunk/unit) and *day-present population*, below); Regime; Driving / external field. **New named variants proposed for `physics-models/DEFINITIONS.md`** (not edited here; outside H38's scope): *joint silence*, *village-off gap*, *stall (explained joint silence)*, *silence reason*, defined under Data scheme.

## Standards (2026-10-04)
*Documentation pass against `STANDARDS.md`. No analysis was re-run. Every entry rests on this card and its round-1b section.*

**Question served:** Q2. The card measures how much activity co-activation is a scheduler field and how much is coupling.

| Impostor | Relevant? | How it was handled | Status |
| --- | --- | --- | --- |
| Scheduler field | yes | The impostor is the object. Scaffold conditioning (Amendment 2), then the DQ8 trim and block-shift null (round 1b). Regime III keeps a significant excess in 3/8 periods after trimming; NE43 places the edges in the runner's schedule. | removed |
| Exogenous field (kickoff/goal/operator) | partly | A 30-min block field h_i(b) absorbs slow drives. Operator pause/resume messages define `scheduled`. NE14 is confounded with a goal change (Caveats). The #44 and #51 residuals are not tested against kickoff or operator messages. | partly |
| Shared model priors | partly | Not handled. Lab-correlated (provider) silences are a named rival that was not tested (axis H; Caveats). Close with a per-provider silence test and a cross-family control (§1, row 3). | open |
| Contemporaneous convergence | no | The card removes co-activation; it makes no copying or influence claim. | n/a |

**Inputs:** round 1b uses `activity_bins_fixed` and `outages_fixed`. Still old: the `infra_err` reason comes from H38's own scan of error categories in `computer_use_turns`, not from `turn_outcomes.failed`. The context ledger is not used (H50 supplies the ledger-based cross-check). Embeddings, work and leading-@ are not inputs.

**Two layers:** no folder has role `replication`. The common estimator runs on 35 period folders under role `exploratory`. Native tests: 3 (`NE14` supported; `NE43` failed; `G04` #4d failed).

**Confirm script:** `analysis/confirm.py` exists, dry-run only. It reads the old table and lacks the trimmed variants (holdout.md item 8). **Re-freeze on `activity_bins_fixed` with `trim` and `trim_scaffold` before any holdout run.**

## Question
H02's collective co-activation is partly everyone going quiet together. That is a common field (API outages, scaffold restarts), not coupling. *Check:* joint-silence bins vs simultaneous errors or latency spikes across agents in `actions`. Does Curie–Weiss βJ₀ vanish after conditioning on them?

Practical aim (usefulness-first batch): produce a number or rule an operator of an LLM agent swarm could compute from logs and act on. Here: a **stall detector** and a **stall-adjusted collective statistic**, plus a verdict on whether apparent collective behavior is mostly infrastructure.

## Model
**From:** `physics-models/01-inverse-ising/` (Curie–Weiss / mean-field view, primary) and `physics-models/09-hawkes/` (common multiplicative shutdown of intensities, rival reading).

- **Spin.** s_i(t) = +1 if agent i is active in 1-min bin t (`activity_bins.state ≥ 3`), else −1 (H02's spin).
- **Curie–Weiss with a two-component field (H38-CW).**
  P(s) ∝ exp[(βJ₀/2N) M² + Σ_i (h_i(b) + Δ_i z(t)) s_i], M = Σ_i s_i,
  with h_i(b) the per-agent field in (day, 30-min block) b (H02's block field) and z(t) ∈ {0, 1} a **stall indicator** (platform or scaffold state that switches agents off: Δ_i → −∞ for the affected agents).
- **Why stalls fake coupling.** H02/H19 estimate βJ₀ from the within-block variance ratio VR = Σ_b n_b Var_b(M) / Σ_b n_b Σ_i Var_b(s_i), βJ₀ = (1 − 1/VR)/q, g = 1 − 1/VR. If z is ignored, Var_b(M) = E[Var(M|z)] + Var(E[M|z]), and the second term inflates VR even at J₀ = 0. For N independent agents with on-rate p, switched off together a fraction π of the time:
  Cov(x_i, x_j) = π(1 − π)p², so VR − 1 ≈ (N − 1)πp / (1 − (1 − π)p) and the **stall-induced spurious gain** g_stall = 1 − 1/VR.
  Example: N = 12, p = 0.5, π = 0.05 gives g_stall ≈ 0.34, the size of the largest gain H02 measured.
- **Hawkes reading (09).** λ_i(t) = (1 − z(t)) [μ_i(t) + Σ_j φ_ij ∗ dN_j(t)]: a common multiplicative shutdown produces equal-time correlation with φ_ij = 0, and no lagged cross-triggering.
- **Rival (coupling) reading.** Joint silences are coupled lulls: agents go quiet *because* others are quiet (message-starved waiting, H09 regime I). Then joint silences are not marked by scaffold states more than chance, and removing marked stalls leaves the excess gain intact.

## Data scheme (`scheme/`)
Inputs (read-only): shared `activity_bins`, `calendar`, `events_core`, `actions`, `chat_core` + `chat_text` (automated messages only, classified by regex; no text kept), `roster`; H09's `idle_runs.parquet` (wait/pause spells with the regime-I end-of-gap logging handled); one raw pass over `computer_use_turns` for error *categories* (`scheme/scan_turn_errors.py`; no text kept).

- **Day-present population** n_d: roster agents (Claude Code excluded) with ≥ 1 active minute that PT day.
- **K_t:** number of day-present agents active (state ≥ 3) in minute t of the day's `activity_bins` window.
- **Joint silence (JS):** a minute with K_t ≤ 1 on a day with n_d ≥ 3 (H02's "lull", day-present version).
- **Village-off gap:** a run of ≥ 10 consecutive minutes with K_t = 0 (H16's rule).
- **Silence reason** of a silent (state ≤ 2) present agent in minute t, first match in this order:
  1. `pre` / `post`: before the agent's first / after its last active minute of the day (not started / done);
  2. `infra_err`: inside a gap adjacent to (just before or just after) one of its turns whose error category is infrastructure (timeout, VM/display, resource, network; `scan_turn_errors.py`), gaps capped at 15 min;
  3. `consol`: between its last turn and a CONSOLIDATE event (CONSOLIDATE is logged at completion), capped at 15 min;
  4. `pause`: inside a declared wait/pause spell (H09 `idle_runs`; regime I/II WAIT covers the gap it closes, regime III PAUSE runs from the call to the next action);
  5. `none`: no recorded reason (mid-LLM-call, long tool call, or unlogged).
- **Village-level marker** `scheduled`: the minute lies outside the day's scheduled run, i.e. after the operator's daily "pausing the village" message or before the "resume the village" message (automated speaker, regex), or, on days without both messages, outside the period's median start/end time of day ±5 min.
- **Stall (explained joint silence):** a JS minute that is `scheduled`, or in which at least half of the silent present agents have a recorded reason (`pre`, `post`, `infra_err`, `consol`, `pause`). Strict variant: all silent agents but one have a reason.
- **Primary cause** of a JS minute: `scheduled` if scheduled; else, if explained, the reason class covering the most silent agents among `edge` (pre + post), `infra_error`, `pause` (reported as `timer_pause` in regime III and `wait` in regimes I–II), `consolidation`, ties broken in that order; else `unexplained`.
- **Infra burst** (HH94's "simultaneous errors" marker): ≥ 2 distinct present agents with an infrastructure-error turn in [t − 5 min, t].

**Outputs:** `data/processed/H38-platform-stalls/` with `_provenance.json`:
- `outages.parquet`: **the shared table** (all days, holdout flagged; schema below);
- `stall_minutes.parquet`: one row per (day, minute) of every window, all days, holdout flagged;
- `turn_errors.parquet`, `sessions.parquet` (scan outputs, codes only);
- per-period results in `G<NN>/`.

### Shared table: `outages.parquet` (one row per joint-silence run)
| Column | Type | Meaning |
| --- | --- | --- |
| `outage_id` | int32 | sequential id |
| `pt_date`, `goal_no`, `regime`, `holdout` | str, int8, str, bool | day, goal period, regime; `holdout` = locked holdout day (exploratory users must drop these rows) |
| `t_start`, `t_end` | datetime UTC | start of the first and end of the last JS minute (end exclusive) |
| `m_start`, `m_end` | int32 | `activity_bins.minute` of the first JS minute and one past the last |
| `dur_min` | int32 | length in minutes |
| `n_present` | int8 | day-present agents n_d |
| `k_max`, `k0_min` | int8, int32 | max K inside the run (0 or 1); minutes with K = 0 |
| `village_off` | bool | contains a K = 0 run of ≥ 10 min (H16's outage) |
| `at_day_edge` | bool | touches the first or last minute of the day's window |
| `cause` | str | majority primary cause over the run's minutes |
| `frac_scheduled`, `frac_edge`, `frac_infra_error`, `frac_pause`, `frac_consolidation`, `frac_unexplained` | float32 | share of the run's minutes by primary cause |
| `explained` | bool | ≥ half of the run's minutes are stalls (explained JS) |
| `infra_burst` | bool | any minute of the run has an infra burst |
| `n_infra_err_agents` | int8 | distinct present agents with an infrastructure-error turn inside the run or 5 min before it |

`stall_minutes.parquet`: `pt_date, goal_no, regime, holdout, minute, t, n_present, K, js, scheduled, n_pre, n_post, n_infra_err, n_consol, n_pause, n_none, explained, cause, infra_burst, outage_id`.

## Candidate goal periods
All 35 non-holdout goal periods (the H19 coverage), split where H12 splits them (#36 at the 2026-03-24 regime boundary; #38, #51 sub-units for λ₁ only). H02's 21 chunks (modes I and C) carry the βJ₀ significance counts. Regime-III periods (#37–#42, #44, #51 head) are where timer-gated pauses and consolidation can synchronize. Per-period folders go in `goalperiod-subhypotheses/G<NN>/`; the regime-boundary test goes in `goalperiod-subhypotheses/NE14/`.

## Observables
Per goal period (one pipeline, `analysis/run_period.py --period G<NN>`):
- **O1. Prevalence.** JS share (JS minutes / window minutes with n_d ≥ 3); village-off gaps (count, minutes); expected JS share under independence (per-block Poisson–binomial of the agents' block rates) and the excess.
- **O2. Causes.** Share of JS minutes by primary cause; explained share; explained share in N1 surrogates (chance-level alignment of scaffold states).
- **O3. Marker enrichment (HH94's check).** Odds ratio of JS given an infra burst vs not; null: burst times circularly shifted within day.
- **O4. Stall-adjusted equal-time gain (H02 βJ₀ / H19 g_eq).** On the H02/H19 present population, 5-day chunks, 30-min blocks:
  - g_raw; g_lull (drop all JS minutes, H02's filter); g_stall (drop explained JS minutes only); g_field (stall indicator as an extra field: blocks split into stall / non-stall minutes); g_exo (drop scheduled minutes and infra-burst minutes, a K-independent mask).
  - Each against N1 block-shift surrogates (each agent's state *and reason* series shifted within (day, block), rule recomputed): excess E = g − mean(g_null), z.
  - **Infrastructure fraction** f_infra = 1 − E_stall / E_raw; f_lull = 1 − E_lull / E_raw; f_field likewise. Per-cause leave-one-in decomposition: drop only minutes of one primary cause.
  - Talk spin (state = 4) as a secondary, with the same activity-defined stall mask.
- **O5. Stall-adjusted market mode (H12 λ₁).** On H12's units and present population: λ₁/edge vs the cross-day surrogate edge, raw / lull-filtered / stall-filtered (surrogates filtered identically).
- **O6. Unfitted stall prediction.** Predicted Δg from the two-state field formula, using only the measured stall indicator and the agents' on-rates outside stalls per block (no fit to the variance): ΔVR_pred = Σ_b n_b Σ_{i≠j} π_b(1 − π_b) p_ib p_jb ·4 / Σ_b n_b Σ_i Var_b(s_i). Compare with the observed g_raw − g_stall.
- **O7. Cross-method agreement.** Spearman across periods between g_eq active (raw / stall-adjusted) and H03's fast cross-triggering n_x (`data/processed/H19-loop-gain-collapse/estimates.parquet`, method `H03.nx_fast`).
- **O8. Regime boundary (NE14, transition exception c).** Raw and stall-adjusted g_eq active on the last regime-II days (#35, #36a) vs the first regime-III days (#36b, #37).

## Null / baseline
- **Independent agents with a block field** (Poisson–binomial per block) for JS prevalence.
- **N1 block shift** (H02): each agent's (state, reason) series circularly shifted within (day, 30-min block), with every filter recomputed on the surrogate. Keeps each agent's half-hour rates and own reason process; destroys alignment.
- **Cross-day surrogate** (H12) for λ₁.
- **Marker-shift null** for O3: infra-error times circularly shifted within the day.
- **Rival (coupling) reading:** explained share no higher than its N1 surrogate level, and f_infra < 0.25.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** pure coupling (Curie–Weiss with a block field only, H02-MF); coupled lulls (message-starved waiting, H09 regime I); provider-level outages (lab-correlated silences rather than village-wide stalls).
**Locked holdout used for confirmation:** goal periods #1, #15, #28 (regime I, mode C), #29 (K), #14 (I) and #45 (III, C); the NE21+NE23 window (the 06-11 pause-default change 12 h → 5 min, and nudger off/on). `analysis/confirm.py`, not run. #45 reuse: H02 used its activity βJ₀; H38's observable (cause composition of joint silences and the stall-adjusted excess) is a different statistic; disclosed per the reuse policy.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Spins, K, joint silence, silence reasons and `scheduled` are all built from logged fields (`activity_bins`, `events_core`, `actions`, H09 `idle_runs`, operator messages, turn-error categories); assumptions listed in Data scheme. Not invariant across regimes: CONSOLIDATE exists only in regime III, WAIT means "wait for messages" in regime I but PAUSE is a timer in III, and "explained" depends on the half-of-silent rule (median explained share 0.51 under it vs 0.16 under the strict rule). |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Within-block stationarity is built into the N1 null (rates kept per 30-min block), and every filter is recomputed on the surrogates, which handles truncation bias. The O6 variance-decomposition check holds in 72% of periods (P7, a consistency check only). No Markov-order or time-rescaling test. The surrogate test of "explained share" is weak for stalls aligned with block edges (Caveats). |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Raw gain beats N1 in 25/35 periods. After conditioning on scaffold states it beats N1 in 16/35: regime III 4/9, regimes I–II 12/26. Scaffold reasons in joint silences beat their surrogate level in 23/35 periods but beat its 95% quantile in only 8/35. No day-blocked held-out likelihood. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | P6 holds: the regime III − I contrast in g_eq shrinks 67% (stall filter) to 86% (scaffold conditioning). P5's unfitted rank relation holds: ρ = 0.89 between a unit's stall share and its λ₁ drop. P8 failed: the correlation with H03's fast n_x moves from −0.38 to +0.05 but not above 0.3. P7 is an accounting identity (Amendment 1), not counted. |
| E interventional | predicts the change across a natural experiment | 1 | NE14 (regime II → III) as predicted: the raw jump of +0.15 [0.07, 0.23] becomes +0.01 (stall filter) and −0.06 (scaffold conditioning). Robust to dropping the 513-min gap day (+0.12 → +0.003). Day-edge conditioning alone removes it. One boundary, exploratory, confounded with a goal change. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | `analysis/synthetic.py` (50 replicates × 24 conditions):<br>• planted stalls alone make raw g significant in 98–100% of replicates;<br>• the pre-registered stall filter still gives 20% (marker recall r = 1) and 60% (r = 0.7) false "coupling" (SP1 failed);<br>• agent-state conditioning gives 6% and 36%, and recovers planted coupling within −5% to +23% at r = 1 (SP3);<br>• partial stalls defeat every JS-based filter (stall filter 42% false positives) but not conditioning (6%).<br>Sensitive to the explained-rule threshold. |
| G ground truth | agrees with known structure | 1 | Raw g reproduces H02/H19 exactly (G40 0.349955; H02 chunks 13/21 significant raw, 5/21 lull-filtered, as H02 reported). Every H16 village-off gap is found (03-31 513 min, 04-16 213 min, #51 days) and classified as inside the operator's pause → resume interval (84% of village-off minutes). This is partly by construction (operator messages define `scheduled`). |
| H comparative | beats the named rivals | 1 | The stall field beats pure coupling in regime III: 6/9 periods have f_scaffold ≥ 0.5. Pure coupling wins in regime I (f_scaffold median 0.11). There the coupled-lull rival (message-triggered WAITs) accounts for what removing pauses takes out (f_all 0.52). Provider-level outages not tested. |
| I transfer | holds in other same-mode periods, including the holdout | 1 | Holds in most regime-III periods (f_scaffold ≥ 0.5 in 6/9; exceptions #44 and #51 keep their full excess, and #39 is borderline at 0.48). Does not transfer to regime I. Holdout not run (`confirm.py`). |

## Prediction
*Written 2026-10-04 01:25 UTC, before running the analysis on real data. Real data seen so far: table schemas; per-period day counts and median window lengths (`calendar`); the category counts of the turn-error scan (timeout 16.6k, VM 6.4k, resource 0.9k, network 0.6k turns over all time); the two daily operator-message templates (pause / resume, 331 and 327 messages). Not blind to H02, H12, H16 and H19 round-1 numbers (disclosed).*

**Synthetic (axis F; `analysis/synthetic.py`).** Kinetic-Ising swarms with village sampling (N = 12, 240 min/day, 5 days, block field), planted uniform coupling J₀ ∈ {0, 0.15, 0.3}, planted stalls (fraction π ∈ {0, 0.05, 0.15} of minutes, all agents but at most one forced off), stall marker recall r ∈ {1, 0.7}, independent agent pauses as a reason background.
- **SP1.** Stalls alone (J₀ = 0, π = 0.05) make raw g significant (z > 2 vs N1) in ≥ 80% of replicates; g_stall and g_field are significant in ≤ 10% at r = 1 and ≤ 25% at r = 0.7.
- **SP2.** Coupling alone (π = 0): g_stall keeps ≥ 80% of the raw excess (it rarely fires without markers); the lull filter keeps ≤ 70% (it removes coupled lulls too).
- **SP3.** Both: g_stall's excess is within ±30% of the coupling-only excess at r = 1.
- **SP4.** The O6 formula predicts the stall-induced Δg within ±30% (median) at r = 1.

**Real data (exploratory, non-holdout; per-period predictions are restated in each G folder).**
- **P1 (prevalence).** Median JS share across the 35 periods in [0.05, 0.30]; JS share exceeds the per-block independent expectation in ≥ 2/3 of periods. Village-off gaps appear in ≤ 6 periods.
- **P2 (causes).**
  - (a) Median explained share of JS minutes ≥ 0.5, and above its N1-surrogate level in ≥ 2/3 of periods.
  - (b) Regime III: `timer_pause` is the largest primary cause in ≥ 2/3 of regime-III periods. Regimes I–II: `edge` or `wait` is the largest in ≥ 2/3.
  - (c) `infra_error` is the primary cause of < 10% of JS minutes in every period.
  - (d) ≥ 80% of village-off-gap minutes are `scheduled`.
- **P3 (HH94 marker check).** Odds ratio of JS given an infra burst > 1 in ≥ 2/3 of periods with ≥ 20 burst minutes, beating the marker-shift null at p < 0.05 in at least half of them.
- **P4 (HH94 core, H02/H19 gain).** Among periods with significant raw g (z > 2 vs N1), median f_infra ≥ 0.5, and the count of significant periods at least halves under g_stall. f_lull ≥ f_infra in ≥ 2/3 of periods. On H02's 21 chunks: significant βJ₀ falls from H02's 13 to ≤ 7 under g_stall.
- **P5 (H12 market mode).** In units with a raw market mode, the λ₁/edge drop under the stall filter is ≥ 50% of the lull-filter drop (median), and Spearman(explained-JS share, relative λ₁/edge drop) ≥ 0.6.
- **P6 (regime contrast).** The regime III − I difference in g_eq active (H19: +0.11) shrinks by at least half after stall adjustment.
- **P7 (unfitted, D).** The O6 formula predicts the observed g_raw − g_stall within a factor of 2 in ≥ 2/3 of periods with a raw excess ≥ 0.05.
- **P8 (cross-method, D).** Spearman(g_eq active, H03 fast n_x) is higher after stall adjustment than before, and > 0.3.
- **P9 (NE14, E).** Across the regime II → III boundary, raw g_eq active rises (Δ_raw > 0) and the stall-adjusted rise is ≤ half of it.

**What counts against H38.** Median f_infra < 0.25 (stalls carry little of the co-activation); or explained share at its surrogate level (scaffold states are not synchronized more than chance); or SP1 failing (the method can't separate planted stalls from coupling). If f_infra is high but the residual excess also vanishes under the lull filter only, the remaining collective co-activation sits in *unexplained* joint silences, which neither confirms nor refutes coupling.

### Amendment 1 (2026-10-04 01:33 UTC, before any real-data analysis of O4–O8; the outages table had been built and its per-period cause shares looked at)
- **P7 demoted to a consistency check.** Writing the code showed that the O6 formula is, up to the K = 1 minutes inside stalls, the law of total variance applied to stall / non-stall minutes. It checks the arithmetic of the decomposition, not the physics, so it no longer counts toward axis D. D rests on P8 (cross-method) and on the synthetic separation (SP1–SP3).
- **P3 marker made strictly prior.** An infrastructure-error turn is itself an action, so a burst in [t − 5, t] is mechanically tied to activity at t. The enrichment test uses bursts in [t − 10, t − 1] and a within-block (30-min) circular shift of the burst series as the null, which keeps the block's activity level.
- **Seen before this amendment** (measurement, not outcomes of O4–O8): per-period JS shares and primary-cause shares from `outages` / `stall_minutes`. Disclosed: regime-III joint silences carry few `pause` reasons (P2b is likely to fail as written); consolidation and `scheduled` dominate there, and the "explained" share in regime III is sensitive to the half-of-silent rule (strict rule 0.1–0.4). Predictions P1–P2 stand as written and are scored as written.

### Amendment 2 (2026-10-04 01:40 UTC, after synthetic smoke runs, before any real-data O4–O8 analysis)
- **What the synthetic showed first** (6-replicate smoke runs of `analysis/synthetic.py`): staggered day starts alone create a spurious excess gain (≈ 0.18, significant in every replicate) that the JS-based stall filter only partly removes, because a common field that switches off a *subset* of agents also acts in minutes with K ≥ 2. Each planted stall also leaves a recovery transient (agents restart from the forced-off state), which no marker covers.
- **Added estimator: agent-state conditioning ("mask").** Scheduled minutes are dropped; agent-minutes whose silence has a recorded reason are treated as unavailable and set to the agent's mean spin over its available minutes of the same block (zero deviation), so a synchronized scaffold state contributes no covariance. Sets: `mask_edge` (pre/post), `mask_infra` (+ infra_err), `mask_scaffold` (+ consol), `mask_all` (+ pause). Surrogates impute the same way after the joint shift. This works whatever K is, so it also handles partial stalls.
- **Real-data reporting.** P4 is scored as written on g_stall. The **headline infrastructure fraction** becomes f_scaffold = 1 − E_mask_scaffold / E_raw (scaffold-imposed silences: not started / done, infrastructure errors, consolidation, village off). f_all (adds self-scheduled pauses) is reported as the upper bound; P4's thresholds are applied to f_scaffold as a secondary score. The λ₁ analysis (O5) gets the same `mask_scaffold` variant.
- SP2 as written ("coupling alone") is scored on the pauses-only condition (background pauses, no edges, no stalls); a `clean` condition (no edges, pauses or stalls) defines the coupling truth for SP3, and a `partial` condition (stalls hitting half the agents) tests the subset case.

## Results by goal period
| Period | Role | Verdict | Verdict (1b) | Key numbers (round 1; 1b numbers in each folder) |
| --- | --- | --- | --- | --- |
| [G02](goalperiod-subhypotheses/G02/README.md) | exploratory | failed | failed | JS 0.474 (indep 0.390); explained 0.97 vs surr 0.96; top cause pause; raw g 0.23 z 2.3; f_stall -1.10, f_scaffold 0.01 |
| [G03](goalperiod-subhypotheses/G03/README.md) | exploratory | supported | mixed | JS 0.444 (indep 0.425); explained 0.79 vs surr 0.79; top cause pause; raw g 0.02 z 0.4 |
| [G04](goalperiod-subhypotheses/G04/README.md) | native (1b) | mixed | failed (native #4d: failed) | JS 0.230 (indep 0.219); explained 0.76 vs surr 0.74; top cause scheduled; raw g 0.12 z 4.5; f_stall 0.45, f_scaffold 0.11 |
| [G05](goalperiod-subhypotheses/G05/README.md) | exploratory | failed | supported | JS 0.119 (indep 0.133); explained 0.18 vs surr 0.23; top cause unexplained; raw g -0.07 z -1.3 |
| [G06](goalperiod-subhypotheses/G06/README.md) | exploratory | supported | supported | JS 0.498 (indep 0.496); explained 0.74 vs surr 0.73; top cause scheduled; raw g 0.07 z 2.1; f_stall 1.21, f_scaffold 0.74 |
| [G07](goalperiod-subhypotheses/G07/README.md) | exploratory | failed | failed | JS 0.375 (indep 0.375); explained 0.17 vs surr 0.19; top cause unexplained; raw g 0.08 z 1.2 |
| [G08](goalperiod-subhypotheses/G08/README.md) | exploratory | mixed | failed | JS 0.092 (indep 0.090); explained 0.27 vs surr 0.26; top cause unexplained; raw g 0.08 z 3.0; f_stall 0.36, f_scaffold 0.11 |
| [G10](goalperiod-subhypotheses/G10/README.md) | exploratory | failed | failed | JS 0.078 (indep 0.050); explained 0.13 vs surr 0.01; top cause unexplained; raw g 0.29 z 5.7; f_stall 0.15, f_scaffold 0.11 |
| [G11](goalperiod-subhypotheses/G11/README.md) | exploratory | failed | failed | JS 0.078 (indep 0.056); explained 0.54 vs surr 0.44; top cause unexplained; raw g 0.30 z 5.7; f_stall 0.17, f_scaffold 0.26 |
| [G12](goalperiod-subhypotheses/G12/README.md) | exploratory | failed | mixed | JS 0.072 (indep 0.055); explained 0.49 vs surr 0.56; top cause unexplained; raw g 0.17 z 3.8; f_stall -0.12, f_scaffold -0.02 |
| [G13](goalperiod-subhypotheses/G13/README.md) | exploratory | mixed | mixed | JS 0.042 (indep 0.038); explained 0.24 vs surr 0.18; top cause unexplained; raw g 0.01 z 0.6 |
| [G16](goalperiod-subhypotheses/G16/README.md) | exploratory | failed | failed | JS 0.218 (indep 0.200); explained 0.38 vs surr 0.42; top cause unexplained; raw g 0.28 z 5.0; f_stall -0.01, f_scaffold -0.05 |
| [G17](goalperiod-subhypotheses/G17/README.md) | exploratory | failed | failed | JS 0.190 (indep 0.169); explained 0.71 vs surr 0.70; top cause pause; raw g 0.12 z 2.7; f_stall -0.25, f_scaffold -0.16 |
| [G18](goalperiod-subhypotheses/G18/README.md) | exploratory | mixed | failed | JS 0.165 (indep 0.156); explained 0.52 vs surr 0.49; top cause unexplained; raw g 0.12 z 3.6; f_stall 0.31, f_scaffold -0.09 |
| [G19](goalperiod-subhypotheses/G19/README.md) | exploratory | failed | failed | JS 0.152 (indep 0.145); explained 0.58 vs surr 0.57; top cause unexplained; raw g 0.12 z 4.2; f_stall 0.05, f_scaffold 0.16 |
| [G20](goalperiod-subhypotheses/G20/README.md) | exploratory | failed | supported | JS 0.078 (indep 0.073); explained 0.40 vs surr 0.43; top cause unexplained; raw g 0.04 z 1.2 |
| [G21](goalperiod-subhypotheses/G21/README.md) | exploratory | mixed | failed | JS 0.201 (indep 0.196); explained 0.22 vs surr 0.22; top cause unexplained; raw g 0.09 z 1.9 |
| [G23](goalperiod-subhypotheses/G23/README.md) | exploratory | failed | failed | JS 0.200 (indep 0.197); explained 0.15 vs surr 0.18; top cause unexplained; raw g 0.04 z 1.1 |
| [G24](goalperiod-subhypotheses/G24/README.md) | exploratory | supported | supported | JS 0.001 (indep 0.000); explained 1.00 vs surr 0.00; top cause scheduled; raw g -0.00 z -0.1 |
| [G25](goalperiod-subhypotheses/G25/README.md) | exploratory | mixed | supported | JS 0.096 (indep 0.096); explained 0.26 vs surr 0.23; top cause unexplained; raw g 0.05 z 1.1 |
| [G26](goalperiod-subhypotheses/G26/README.md) | exploratory | failed | failed | JS 0.391 (indep 0.383); explained 0.43 vs surr 0.43; top cause unexplained; raw g 0.21 z 3.8; f_stall -0.10, f_scaffold -0.15 |
| [G27](goalperiod-subhypotheses/G27/README.md) | exploratory | failed | mixed | JS 0.025 (indep 0.022); explained 0.28 vs surr 0.11; top cause unexplained; raw g 0.13 z 4.6; f_stall 0.19, f_scaffold 0.36 |
| [G30](goalperiod-subhypotheses/G30/README.md) | exploratory | mixed | mixed | JS 0.110 (indep 0.108); explained 0.11 vs surr 0.08; top cause unexplained; raw g 0.10 z 2.4; f_stall 0.25, f_scaffold 0.31 |
| [G31](goalperiod-subhypotheses/G31/README.md) | exploratory | failed | failed | JS 0.147 (indep 0.145); explained 0.09 vs surr 0.11; top cause unexplained; raw g 0.07 z 1.6 |
| [G33](goalperiod-subhypotheses/G33/README.md) | exploratory | failed | failed | JS 0.003 (indep 0.001); explained 1.00 vs surr 0.07; top cause scheduled; raw g 0.11 z 2.2; f_stall 0.18, f_scaffold 0.12 |
| [G35](goalperiod-subhypotheses/G35/README.md) | exploratory | failed | failed | JS 0.037 (indep 0.040); explained 0.07 vs surr 0.04; top cause unexplained; raw g 0.10 z 2.2; f_stall -0.01, f_scaffold 0.45 |
| [G36](goalperiod-subhypotheses/G36/README.md) | exploratory | supported | mixed | JS 0.076 (indep 0.062); explained 0.63 vs surr 0.59; top cause consolidation; raw g 0.17 z 4.0; f_stall 0.61, f_scaffold 1.06 |
| [G37](goalperiod-subhypotheses/G37/README.md) | exploratory | failed | failed | JS 0.421 (indep 0.411); explained 1.00 vs surr 1.00; top cause scheduled; raw g 0.32 z 5.1; f_stall 0.54, f_scaffold 0.78 |
| [G38](goalperiod-subhypotheses/G38/README.md) | exploratory | failed | failed | JS 0.091 (indep 0.081); explained 0.88 vs surr 0.88; top cause scheduled; raw g 0.15 z 6.1; f_stall 0.76, f_scaffold 0.89 |
| [G39](goalperiod-subhypotheses/G39/README.md) | exploratory | supported | supported | JS 0.015 (indep 0.002); explained 0.83 vs surr 0.43; top cause scheduled; raw g 0.19 z 4.9; f_stall 0.68, f_scaffold 0.48 |
| [G40](goalperiod-subhypotheses/G40/README.md) | exploratory | supported | supported | JS 0.045 (indep 0.026); explained 0.67 vs surr 0.52; top cause scheduled; raw g 0.35 z 7.5; f_stall 0.58, f_scaffold 0.69 |
| [G41](goalperiod-subhypotheses/G41/README.md) | exploratory | supported | supported | JS 0.079 (indep 0.081); explained 0.66 vs surr 0.62; top cause unexplained; raw g 0.13 z 2.9; f_stall 0.77, f_scaffold 0.66 |
| [G42](goalperiod-subhypotheses/G42/README.md) | exploratory | supported | supported | JS 0.103 (indep 0.089); explained 0.51 vs surr 0.48; top cause unexplained; raw g 0.11 z 2.4; f_stall 1.16, f_scaffold 0.87 |
| [G44](goalperiod-subhypotheses/G44/README.md) | exploratory | failed | mixed | JS 0.084 (indep 0.061); explained 0.34 vs surr 0.35; top cause unexplained; raw g 0.36 z 7.1; f_stall 0.16, f_scaffold -0.03 |
| [G51](goalperiod-subhypotheses/G51/README.md) | exploratory | failed | failed | JS 0.136 (indep 0.125); explained 0.95 vs surr 0.97; top cause scheduled; raw g 0.28 z 25.1; f_stall 0.36, f_scaffold 0.14 |
| [NE14](goalperiod-subhypotheses/NE14/README.md) | native (1b) | supported | supported | Δ excess gain II → III: raw +0.150 [+0.070, +0.230]; stall +0.012; edge-conditioned +0.005; scaffold-conditioned -0.060 |
| [NE43](goalperiod-subhypotheses/NE43/README.md) | native (1b) | – | failed | bookends stop 08-05: day-edge share 0.189 → 0.135 (p 0.08), start spread narrower; nudger stop 08-21: no edge change, start spread +22.6 min (post hoc) |

## Results
Scripts:
- pipeline: `analysis/run_period.py` (per period), `analysis/ne14.py` (NE14 boundary), `analysis/summarize.py` (cross-period scoring and figures);
- method check: `analysis/synthetic.py`;
- shared table: `scheme/build_outages.py`.

Outputs: per-period JSON in `data/processed/H38-platform-stalls/G<NN>/`; cross-period tables in `period_table.parquet`, `unit_table.parquet`, `chunk_table.parquet` and `outcomes.json`. Joint silences use the day-present population. Gains use H02/H19's chunks and present population. All 35 non-holdout periods were run, with 200 joint N1 surrogates each (100 for the O2/O3 day-level surrogates).

**1. What joint silences are (O1–O3).**
- **Prevalence.** Joint silences cover a median 10.3% of window minutes (0.1–50%). Half of all runs last 1 minute; the 90th percentile is 6 minutes.
- **Mostly chance.** The JS share exceeds the per-block independent expectation in 32/35 periods, but only barely: median excess 0.008 of minutes, ratio 1.07. Most joint silences are what independent agents with their own half-hour activity rates produce by chance.
- **Village-off gaps** (K = 0 for ≥ 10 min): 28 non-holdout gaps in 9 periods, 2,979 minutes. 84% of their minutes fall inside the operator's pause → resume interval. The rest are short (10–15 min) unexplained K = 0 runs.
- **Causes, pooled over non-holdout JS minutes:** unexplained 31%, scheduled 30%, pause/wait 17%, edge (not started / done) 16%, consolidation 6%, infrastructure error 0.7%.
  - Regime III: scheduled 42%, edge 18%, pause 16% (almost all #51), consolidation 14%, unexplained 9%.
  - Regimes I–II: unexplained 48%.
- **Scaffold states are barely synchronized beyond chance.** The explained share (median 0.51; strict rule 0.16) beats its N1 surrogate level in 23/35 periods but its 95% quantile in only 8/35.
- **The HH94 marker check fails in reverse.** An infrastructure-error burst in the previous 10 minutes makes a joint silence *less* likely: median log OR −0.43; positive in 9/30 periods; never significantly positive against a within-block shift. Errors are logged on turns, so they mark busy minutes. LLM API failures leave no log line at all (Caveats).

**2. How much collective co-activation is infrastructure (O4).**

Among the 25 periods with a significant raw gain, f is the share of the excess gain (over the N1 null) that each adjustment removes:

| f (median) | stall filter (drop explained JS minutes) | lull filter (drop all K ≤ 1) | scaffold conditioning (headline) | + pauses |
| --- | --- | --- | --- | --- |
| all 25 | 0.25 | 0.46 | 0.16 | 0.60 |
| regime III (8) | 0.63 | 0.60 | 0.68 | 0.85 |
| regime I (14) | 0.16 | 0.30 | 0.11 | 0.52 |

- Significant periods: 25 raw → 16 under the stall filter, 13 under the lull filter, 16 under scaffold conditioning, 10 when pauses are also conditioned on. On H02's 21 chunks: 13 → 8 (stall), 5 (lull, reproducing H02), 9 (scaffold).
- **Regime III: two thirds is infrastructure, mostly day edges.** In regime III, day-edge conditioning alone (dropping off-schedule minutes and imputing not-started / finished agent-minutes) removes most of the excess: G38 0.149 → 0.026, G41 → −0.007, G42 → −0.011. That is agents starting and stopping together at the operator's daily resume and pause, which the 30-min block field cannot absorb.
  - Consolidation and pause synchrony add little. Dropping JS minutes of one cause shows the same thing: only `scheduled` matters (median f 0.16; G38 0.73).
  - Two regime-III periods keep their full excess under every adjustment: #44 (f_scaffold −0.03) and the #51 head (0.14, z ≈ 23). Those are the candidates for genuine collective coupling.
- **Regime I: co-activation is not infrastructure.** It survives edge and error conditioning. Only conditioning on WAITs removes half, but WAIT is message-triggered there (H09), so that removes a coupling channel, not a stall.
- **Talk spins: no stall component anywhere.** Talk excess keeps ~100% under every scaffold adjustment.
- The pre-registered P4 is scored on the stall filter and fails (median f 0.25). The JS-based filters also turn out to be the weaker estimators: they miss partial stalls and edge ramps (synthetic), and they remove coupled minutes that scaffold conditioning keeps.

**3. Market mode (O5, H12's λ₁).**
- 37/41 H12 units have a raw mode above the cross-day edge (median λ₁/edge 1.56). Under the stall filter 31 keep it (1.25), under the lull filter 19 (1.03), under scaffold conditioning 34 (1.41).
- The stall filter's drop is 48% of the lull filter's (P5 needed 50%). Across units it tracks the stall share (ρ = 0.89; H12 found 0.97 for the lull share).
- Units that lose the mode under the stall filter contain the long scheduled gaps: 37, 38b, 51a.
- H12's market mode is computed over whole units, not within blocks. So it mixes the daily schedule with co-activation, and scaffold conditioning barely moves it.

**4. Regime contrast and boundary (P6, P9).**
- **Across periods (P6).** Mean regime III − I g_eq active is +0.125 [0.05, 0.20] raw. It is +0.041 [−0.03, 0.12] under the stall filter and +0.017 [−0.06, 0.11] under scaffold conditioning. The lull filter *raises* it to +0.195.
- **Across the boundary (NE14, P9).** The raw jump is +0.150 [0.070, 0.230]. It becomes +0.012 under the stall filter, +0.005 under day-edge conditioning and −0.060 under scaffold conditioning, with or without the 513-min gap day. H19's "activity co-activation rises in regime III" is a scaffold artifact: agents start and stop together when computer use is always on.
- **Cross-method (P8).** Spearman with H03's fast cross-triggering n_x goes from −0.38 (raw) to +0.05 (scaffold-conditioned). The anti-correlation between the activity channel and the talk channel is mostly infrastructure; no positive agreement appears.

**5. Synthetic validation (axis F; `figures/synthetic.png`, `data/processed/H38-platform-stalls/synthetic/`).** 50 replicates × 24 conditions × 100 surrogates; N = 12, 5 days × 240 min.
- **Spurious gains.** Planted stalls (5% of minutes, J₀ = 0) produce a spurious excess of 0.31, significant in 98% of replicates. Staggered day starts alone give 0.16 (82%).
- **Filters.** The stall filter leaves 0.077 (20% significant at full marker recall). Agent-state conditioning leaves 0.027 (6%). Both degrade when 30% of stalls are unmarked (60% and 36%).
- **Planted coupling** (J₀ = 0.75, 1.5) is recovered by agent-state conditioning within −5% to +23% of the clean truth at full recall. The stall filter is off by +3% to +56%.
- **Partial stalls** (half the agents) leave 0.12 after the stall filter but 0.025 after conditioning.
- **The lull filter does not remove planted coupling.** It keeps 103–121% (SP2's expectation was wrong).

### Outcome vs prediction
| Prediction | Observed | Verdict |
| --- | --- | --- |
| SP1 stalls alone: raw significant ≥ 80%; stall / field filter ≤ 10% (r = 1), ≤ 25% (r = 0.7) | raw 98–100%; stall 20% / 60%, field 22% / 64% (conditioning: 6% / 36%) | ✗ for the filters as written |
| SP2 coupling alone: stall keeps ≥ 80%, lull keeps ≤ 70% | stall 100%; lull 103–121% | partial |
| SP3 both: stall within ±30% of coupling-only (r = 1) | 3/4 conditions (1.03, 1.11, 1.23; 1.56 fails); conditioning 4/4 | partial |
| SP4 O6 formula within ±30% (r = 1) | median ratio 1.06–1.12 | ✓ (consistency) |
| P1 median JS in [0.05, 0.30]; above independence in ≥ 2/3; village-off in ≤ 6 periods | 0.103; 32/35 (but excess 0.008); 9 periods | ✗ (village-off count) |
| P2a explained ≥ 0.5 and above surrogate in ≥ 2/3 | median 0.51 (strict 0.16); 23/35 above mean, 8/35 above q95 | ✗ (narrowly) |
| P2b regime III top cause timer pause; regimes I–II edge or wait | III: scheduled 5/9, unexplained 3/9, pause 0/9; I–II: unexplained 19/27, edge or wait 3/27 | ✗ |
| P2c infra_error < 10% in every period | max 6.6% | ✓ |
| P2d ≥ 80% of village-off minutes scheduled | 84% | ✓ |
| P3 OR(JS given infra burst) > 1 in ≥ 2/3; p < 0.05 in ≥ half | 9/30 positive; 0/30 significant; median log OR −0.43 | ✗ (reversed) |
| P4 median f_stall ≥ 0.5; significant periods halve; f_lull ≥ f_stall in ≥ 2/3; H02 chunks ≤ 7 | 0.25; 25 → 16; 52%; 13 → 8 | ✗ (✓ in regime III: 0.63) |
| P4 secondary, f_scaffold (Amendment 2) | 0.16 overall; 0.68 regime III; 0.11 regime I | ✗ overall, ✓ regime III |
| P5 stall/lull λ₁ drop ≥ 0.5; ρ(stall share, drop) ≥ 0.6 | 0.48; ρ = 0.89 | partial |
| P6 regime III − I contrast shrinks ≥ half | 67% (stall), 86% (scaffold) | ✓ |
| P7 O6 within 2× in ≥ 2/3 | 72% | ✓ (consistency only) |
| P8 ρ(g, H03 n_x) rises and > 0.3 | −0.38 → −0.26 (stall), +0.05 (scaffold) | ✗ |
| P9 NE14: Δ_raw > 0, Δ_adj ≤ Δ_raw / 2 | +0.150 → +0.012 (stall), −0.060 (scaffold) | ✓ |

**Per-period verdicts** (pre-registered rule): 8 supported, 7 mixed, 20 failed. By regime: III 4 supported (G39–G42) and 4 failed (G37, G38, G44, G51); the boundary period G36 supported; regimes I–II 3 supported, 7 mixed, 16 failed. The rule demands both (i) scaffold reasons above their surrogate level and (ii) f_stall ≥ 0.5.
- G37 and G38 fail on (i) even though most of their excess goes (f_scaffold 0.78, 0.89). Their stalls are operator-scheduled day edges, which the N1 null partly reproduces at the block level (Caveats).
- G44 and G51 fail on (ii): their excess is real by every adjustment.

### The operator rule (and how to compute it on another swarm)
1. **Stall detector (per minute).** A minute is a stall if at most one present agent acted in it and either (a) the swarm was outside its scheduled run (after the operator's pause, before the resume), or (b) at least half of the silent agents were in a logged scaffold state: not yet started that day, already finished, consolidating memory (last turn → consolidation event), within 15 min of an infrastructure-error turn (timeouts, VM/display, resource, network), or in a declared pause. Code: `scheme/build_outages.py`; shared table `outages.parquet`.
2. **Stall-adjusted co-activation.**
   - Compute the Curie–Weiss variance ratio VR on 1-min active spins in 30-min blocks.
   - First drop off-schedule minutes, and replace each agent's not-started, finished, consolidating and infra-error minutes by that agent's block mean.
   - Compare with block-shift surrogates processed the same way.
   - Report f = 1 − E_adj / E_raw. Code: `h38lib.gains(..., masks_on=True)`, variant `mask_scaffold`.
3. **Decision.** If the adjusted excess has z < 2, the apparent collective behavior is infrastructure: don't read it as coordination. Short version for always-on swarms: **trim every day to the window in which all agents are running before computing any synchrony statistic**. In this village that one step (day-edge conditioning) removes about 60–100% of the regime-III co-activation.
- **Inputs another swarm needs:** per-agent turn timestamps, the operator's start/stop log, consolidation (context-reset) events, error strings, and pause/wait calls. All are standard in agent-runner logs.
- **Not useful for:** detecting LLM-provider outages, which leave no log line. And it adds nothing for message-driven swarms (regime I), where co-activation is not infrastructure.

### Confirmatory predictions (frozen 2026-10-04, `analysis/confirm.py`, not run)
- **C1, regime III.** On held-out regime-III periods (#45, #46, #47, #49, #50) with significant raw gain: median f_scaffold ≥ 0.5, and day-edge conditioning alone removes ≥ 0.4 of the excess.
- **C2, regime I.** On held-out regime-I periods (#1, #9, #14, #15, #22, #28, #29): median f_scaffold < 0.35.
- **C3.** The held-out regime III − I difference in mean g_eq shrinks ≥ 50% under scaffold conditioning.
- **C4.** Median log OR(JS | prior infra burst) < 0.
- **C5.** Talk f_scaffold < 0.3.
- **C6, NE21 hours reversal.** The edge-induced excess (E_raw − E_mask_edge) is smaller in each 8-h week than in the adjacent 4-h weeks.
- The script refuses to run without `--confirm --i-understand-this-uses-the-locked-holdout`. Its dry run on stand-ins (#39–#41, #10, #17, #18, #35) completes.
- **#45 reuse disclosure:** H02 used #45's activity βJ₀ and H23 its message content. H38's statistics (joint-silence cause composition, stall-adjusted excess) are different, and nobody has looked at them for #45.

### Caveats
- **API failures are invisible.** An LLM call that fails or hangs produces no turn and no error string, so provider outages can't be told apart from long thinking. They sit in the `none` reason and in `unexplained` joint silences (31% of JS minutes). The `infra_error` class only sees VM- and tool-level failures. A per-provider silence test (all agents of one lab silent while the others act) is the next step.
- **The "explained above chance" test is weak for scheduled stalls.** The N1 null keeps each agent's 30-min rates, so operator-scheduled edges partly survive in the surrogates. G37 and G38 therefore fail criterion (i) even though their excess gain is mostly scaffold. The conditioning estimators don't have this problem.
- **The headline estimator was added after the synthetic smoke runs** (Amendment 2, before any real-data O4 run). P4 as pre-registered (stall filter) fails.
- **What counts as infrastructure is a choice.** Pauses in regime I are message-triggered waits (a coupling channel), so f_all overstates the infrastructure share there. In regime III pauses add little.
- **Thresholds matter.** The half-of-silent rule versus the strict rule changes the explained share threefold. Reasons are assigned at minute resolution with 15-min caps; the consolidation gap is inferred (logged at completion).
- **Schedule fallback.** Days without operator messages (early 2025, the 06-13 Saturday session) fall back to a median schedule. That mislabels some active minutes as scheduled, mostly on holdout days.
- **Small periods.** G02, G03, G07 and G33 have 2–3 days, and their z and f are noisy.
- **#36 and the boundary.** #36 is computed as one H19 chunk across the 03-24 boundary. NE14's regime-III side also includes #37, a free week with a goal change.

### Figure summary
- `figures/summary_obs.png`:
  - (a) raw vs scaffold-conditioned excess gain per period. Regime-III points fall to the half-removed line or below; regime I stays on the identity line; #44 and #51 stay up.
  - (b) causes of joint silences by regime: unexplained dominates regime I; scheduled, edge and consolidation dominate regime III.
- `figures/decomposition.png`: excess gain per period under raw, lull, stall and scaffold-conditioned variants, with significance stars.
- `figures/causes.png`: cause composition of joint silences per period, with the JS share against its independent expectation.
- `figures/synthetic.png`: planted stalls / edges vs planted coupling, and false-coupling rates of each filter.

## Round 1b (improved data, 2026-10-04)
*Re-run of the round-1 pipeline on corrected inputs, plus the DQ8 null-size correction and three period-native tests. Predictions P1–P9 and the per-period rule are unchanged; native predictions were written in the folders before each run (NE43 06:31, G04 and NE14 06:32 UTC).*

**What changed in the inputs.**
- `activity_bins` dropped about half of all events (DQ8 join-key bug). Round 1b reads `activity_bins_fixed` and the shared `outages_fixed/{outages,stall_minutes,reasons}` sidecar (H38's own outage rule rebuilt on the fixed table by `infra/shared/outages.py --fixed`). Joint silences fall from 14.3% to 5.3% of non-holdout minutes; non-holdout runs from 2,650 to 429.
- **Null sizes (DQ8).** H38's N1 null (block shift within day × 30-min block) on whole-day grids rejects 28–34% of independent swarms; after trimming each day to the all-present window it rejects 2–4%. Round 1b adds `trim`, `trim_stall` and `trim_scaffold`, with rows removed *before* the surrogates are drawn. For λ₁ (O5), the cross-day edge has size 0.62 on whole-day grids and 0.19 on trimmed grids, so round 1b adds `trim_bs` (trimmed rows, block-shift edge; size 0.05).
- NE43 is two steps (bookends end after 08-04 PT, nudges after 08-20). The day-edge mechanism is tested at the bookend stop.
- Code: `analysis/run_period.py`, `ne14.py`, `summarize.py --data-version fixed` (the old path still runs by default and reproduces round 1 exactly, e.g. G40 g_raw 0.349955); new `analysis/r1b_native.py`, `analysis/r1b_periods.py`. Outputs in `data/processed/H38-platform-stalls/r1b/`.

**Old vs new (non-holdout, 35 periods).**

| Statistic | Round 1 (old tables) | Round 1b (fixed tables) |
| --- | --- | --- |
| joint-silence share, pooled minutes · median over periods | 14.3% · 0.103 | 5.3% · 0.009 |
| above the independent expectation (median excess) | 32/35 (0.008) | 32/35 (0.007) |
| causes of JS minutes (pooled) | unexplained 31%, scheduled 30%, pause 17%, edge 16%, consolidation 6%, infra 0.7% | **scheduled 78%**, unexplained 8%, pause 8%, edge 7%, consolidation 0%, infra 0.1% |
| explained share, median (strict) · above surrogate mean / q95 | 0.51 (0.16) · 23 / 8 | 0.88 (0.67) · 24 / 12 |
| village-off gaps | 28 in 9 periods, 84% scheduled | 15 in 7 periods, 94% scheduled |
| P3 log OR(JS ∣ prior infra burst), median · positive · significant > 0 | −0.43 · 9/30 · 0/30 | −0.96 · 8/30 · 1/30 |
| raw g_eq active significant (N1, whole-day grid) | 25/35 | 29/35 |
| median f (significant periods): stall · lull · scaffold · + pauses | 0.25 · 0.46 · 0.16 · 0.60 | 0.26 · 0.48 · 0.14 · 0.59 |
| f_scaffold regime III (8) · regime I | 0.68 · 0.11 | **0.72** · 0.11 |
| significant after stall · lull · scaffold · + pauses | 16 · 13 · 16 · 10 | 28 · 27 · 24 · 13 |
| H02 chunks significant: raw → stall / lull / scaffold | 13 → 8 / 5 / 9 | 16 → 13 / 12 / 9 |
| **DQ8 null:** significant after trimming (trim · trim_stall · trim_scaffold) | not computed | **20 · 16 · 21 of 35**; regime III **3/8**, regime I 16/18 |
| **DQ8 null:** median f_trim (III · I) | – | 0.27 (0.83 · 0.11) |
| talk spins significant raw → trimmed; median talk f_trim | – | 31 → 29 of 35; 0.03 |
| λ₁ units above edge: raw · stall · lull · scaffold (cross-day edge) | 37 · 31 · 19 · 34 of 41 | 31 · 18 · 15 · 24 of 41 |
| **DQ8 null:** λ₁ above the trimmed block-shift edge (trim · trim_stall) | – | **19 · 18 of 41** (median ratio 1.00) |
| P5: stall drop / lull drop · ρ(stall share, drop) | 0.48 · 0.89 | 1.00 · 0.87 |
| P6: regime III − I, raw → stall → scaffold (→ trim) | +0.125 → +0.041 → +0.017 | +0.155 → +0.051 → −0.006 (→ −0.059) |
| P8: ρ with H03 fast n_x, raw → scaffold (→ trim) | −0.38 → +0.05 | −0.33 → +0.19 (→ +0.20) |
| P9 NE14: Δ raw → stall → scaffold (→ trim) | +0.150 [0.07, 0.23] → +0.012 → −0.060 | +0.116 [−0.04, 0.27] → −0.046 → −0.135 (→ −0.076) |
| per-period verdicts (supported / mixed / failed) | 8 / 7 / 20 | 9 / 7 / 19 |

**Which verdicts change.**
- **Card level:** P2a now passes (explained 0.88, above the surrogate mean in 24/35 ≥ 2/3), but only because most joint silences are now operator-scheduled minutes; P5 now passes (stall/lull drop 1.00, ρ 0.87). P1 fails more clearly (median JS share 0.009, outside [0.05, 0.30]). P2b, P3, P4 (as written) and P8 still fail; P2c, P2d, P6, P7 (consistency) and P9 still pass. **Headline unchanged in direction and sharpened:** joint silences are rare and almost all scheduled; in regime III most co-activation is day-edge synchrony; in regime I it is not.
- **Under the corrected null** the regime-III verdict is stronger: after trimming, only 3 of 8 regime-III periods keep a significant excess (#37 at z 2.0, #44 z 3.4, #51 z 8.5), and with scaffold conditioning on top only #44 and #51 do (G38–G42 lose it), so the "#44 and #51 residuals" are the only regime-III candidates for coupling. In regime I the excess survives trimming in 16/18 periods.
- **Per period (12 changes, all regime I except G36 and G44):** G05, G20, G25 failed/mixed → supported; G12, G27 failed → mixed; G44 failed → mixed; G03, G36 supported → mixed; G04, G08, G18, G21 mixed → failed. They follow from much smaller joint-silence counts (explained shares rest on a handful of minutes in most regime-I periods), not from a change in the gains.
- **Native tests:** NE14 (re-run with the DQ8 null and the #36-only pair) **supported**, with a smaller raw jump whose interval now includes 0; **NE43 failed**: the day-edge component does not drop when the bookend messages stop (0.189 → 0.135, p = 0.08) and agents start *more* tightly together (start spread 15.3 → 3.8 min), so the edges come from the runner's schedule, not the operator's announcement (post hoc: the start spread widens at the nudger stop, +22.6 min, p = 0.010); **G04 #4d failed**: the 300-min operator stop on 2025-06-18 is detected (299 min, 99% scheduled) and the restart is perfectly synchronized (all agents within 1 min), but it leaves no trace in the block-detrended gain (E_raw 0.022, below the other days' median 0.191): whole-block stalls are harmless to the 30-min-block estimator.

**Scorecard after 1b** (unchanged scores, updated evidence): A 1 (the `scheduled` flag depends on operator messages and empties after 08-05; agent-level trimming does not); B 1; C 1 (DQ8 null: 20/35 periods significant after trimming; scaffold reasons above surrogate q95 in 12/35); D 1 (P5 and P6 pass, P8 fails at ρ 0.19); E 1 (NE14 supported but weaker; NE43 refutes the message mechanism and supports the runner mechanism; #4d no inflation); F 1; G 1 (village-off minutes 94% scheduled; synchronized restart on 06-18); H 1; I 1.

**Cross-hypothesis corroboration (H50, 2026-10-04; `data/processed/H50-field-vs-coupling-transfer-lag/`, built from `call_windows`, not `activity_bins`).** H50 finds activity co-movement to be a scheduler field: the daily start/stop alone explains 0.62 (regime I) / 0.67 (regime III) of it, agents start within ~9–22 s of each other, and inside the all-present window per-pair activity correlation nearly vanishes (0.056 / 0.005). After 08-04 (no bookends) agents still start within ~22 s and the day-start step keeps its size: an independent measurement of the same NE43 result (the runner starts the agents, not the message). It also finds talk co-movement to be a genuine coupling gated at one read-out call (J₁ > 0 in 45/71 units), consistent with H38's talk excess surviving every scaffold adjustment and trimming (29/35).

**Operator rule, revised.** Trim each day to the window in which every agent that runs that day is between its first and last action, *then* draw surrogates. Do not rely on operator start/stop messages to find the edges: the runner's schedule makes the edges whether or not it is announced.

## Notes
- 2026-10-04: promoted from HH94 by Vivian (usefulness-first batch); wave 1.
- 2026-10-04 01:21 UTC: ran `scheme/scan_turn_errors.py` (37 s, one raw pass, categories only) before writing predictions; its output only fixed the error categories, which are design.
- 2026-10-04: shared `outages.parquet` / `stall_minutes.parquet` built for all 389 days (holdout flagged, 3,590 joint-silence runs, 2,650 non-holdout). Consumers (H25, H26, H36) should filter `holdout == False` and decide whether to drop `explained` runs, `village_off` runs or only `cause == "scheduled"` minutes.
- 2026-10-04: round 1 done; disk 4.6 MB in `data/processed/H38-platform-stalls/`.
- 2026-10-04: round 1b on the corrected tables (`activity_bins_fixed`, `outages_fixed`), DQ8 null correction, native tests NE43 / G04 #4d / NE14; ~7 min of compute on ≤ 2 processes; disk +1.5 MB in `data/processed/H38-platform-stalls/r1b/`.
