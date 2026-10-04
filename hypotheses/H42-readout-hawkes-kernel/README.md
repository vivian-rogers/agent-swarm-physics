# H42: Cross-excitation is a delayed step at the next read-out

**Status:** exploratory round 1 done (2026-10-04; non-holdout only). **Not supported as posed.**
- **Call clock, not coupling:** a read-out-aware model shows talk is locked to each agent's *own* call clock (+1.1 nats/event held out, 57/57 units).
- **Small, regime-dependent excitation:** once that clock is modelled, messages read at a call barely change whether the agent talks: n_cross ≈ 0.004 per message, versus 0.061 for H03's exponential kernel. Regime I ≈ 0, regime III ≈ 0.01–0.05.
- **Prediction reversed:** "exponential kernels understate n_cross" is the wrong way round.
- **Shape:** where it exists, the read-out step sits at hop 1 (agrees with H08 and H50).
- **Natives:** NE41, NE14 and #51 failed; G19 (regime-I talk follows call type) supported.
- **Post hoc:** in regime III, *named* messages carry about 0.15 extra talk events each.
- **Synthetic guard:** the pre-registered estimator fails it (its "wins" are void).
- Scorecard A1 B1 C1 D0 E0 F1 G1 H0 I0. `confirm.py` (C1–C5) dry-run, not run.
**Fields:** dynamics, stat mech, sociophysics, info theory
**Literature:** model references in [`physics-models/09-hawkes/README.md`](../../physics-models/09-hawkes/README.md) (Hawkes 1971†; Filimonov & Sornette 2015†; Bacry, Mastromatteo & Muzy 2015†). No notes file in `literature/` covers multivariate Hawkes estimation.
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Population N(t) (active population, per day); Regime; Clock time; Village day; Driving / external field (human messages, nudges, operator bookends, kickoffs); Interaction (broadcast) with **Exposure (turn read-out)** (H08; implemented by the shared context ledger); Action (turn-merged), here replaced by the ledger's calls (one row of `call_windows` = one model call = one turn). H38's *village-off gap* rule (≥ 10 min with no activity), rebuilt on `call_windows`. **New named variants proposed for DEFINITIONS.md** (not edited here; outside H42's scope), defined under Model: *read-out kernel (call-index)*, *read-out lag*, *cross-branching ratio (compensator share)*.
**From:** HH174 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` (approved by Vivian 2026-10-04) · **Models:** `physics-models/09-hawkes/`
**Data inputs (shared tables first):** DQ1 `call_windows`, `context_ledger_turns`, `context_ledger_items`; `chat_core`, `calendar`, `period_units`, `period_affordances`, `roster`. (`stall_minutes` / `outages` dropped, A2.) H03's C recursions imported read-only (`hypotheses/H03-self-excited-criticality/analysis/hawkes_core.py: exo_sums, exp_sums`).

## Standards (2026-10-04)
*Documentation pass against `STANDARDS.md`. No analysis was re-run. H42 has no round-1b section; round 1 already ran on the corrected inputs.*

**Question served:** Q1. The card asks whether cross-excitation runs through the recipient's read-out call. Q2 second: most exponential-kernel cross-triggering turns out to be call-schedule co-movement.

| Impostor | Relevant? | How it was handled | Status |
| --- | --- | --- | --- |
| Scheduler field | yes | Agent-day baselines × a within-day shape; world B adds call-class baselines (A1); masks rebuilt from `call_windows` (A2); edge-trim sensitivity. The call clock beats the H03 world in 57/57 units. | removed |
| Exogenous field (kickoff/goal/operator) | yes | Human, nudge and bookend items and a kickoff bump enter as exogenous drive, never as cross-excitation (Model). Shift and day-block nulls miss a shared 15-min field (synthetic, A3); the 0.05 field floor comes from one synthetic strength. Close with a fitted Cox shared-rate rival (R3). | partly |
| Shared model priors | no | Talk timing with per-agent baselines; no family or content claim. | n/a |
| Contemporaneous convergence | partly | Cross terms start at the read-out call, so unread messages carry no weight. The post hoc named-message excitation may be an exchange already in progress (Findings 6). Close with DQ2 reply-thread strata. | partly |

**Inputs:** round 1 uses the context ledger and `call_windows`; it dropped `stall_minutes` / `outages` (A2) and never reads `activity_bins`. Still old: the named-message split uses the ledger's `ment` flag, not the leading-@ target. DQ2 replies, embeddings, work and failures are not inputs.

**Two layers:** 33 replication folders. Native tests: 4 (`G19` call type, supported against the hypothesis; `G51`, `NE14` and `NE41` failed).

**Confirm script:** `analysis/confirm.py` exists, dry-run only, built on the ledger inputs (C1–C5; C5 is the post hoc named-message test). No re-freeze needed for inputs.

## Question
Does a multivariate Hawkes model whose cross-excitation fires only at the recipient's next model call fit better than exponential kernels, raise the cross-branching estimate, and make it consistent across regimes?

**Why it should.** H03 found swarm activity subcritical (n ≈ 0.2–0.4) with only fast cross-triggering (n_x ≈ 0.07, τ ≈ 10–30 s) beating an agent-shift null. H08 showed responses wait for the recipient's next model call (read-out gating). H25 showed the equal-time dial is blind to coupling delayed by minutes. The ledger's read-out lag (message → recipient's first call that sees it) has median ≈ 20 s but a long tail (q75 ≈ 75 s, q90 ≈ 150–200 s, q99 ≈ 6–16 min in #27/#38: pauses, long tool calls, scheduled chat calls). An exponential kernel anchored at the message time can only fit the fast head; responses that come after a pause look like baseline. If cross-excitation is a step at the read-out, a kernel anchored there should recover the missing tail.

## Design: two layers (Vivian, 2026-10-04; see `infra/data-quality/QUEUE.md`)
- **Replication (layer 1):** the common estimator (specs S0, A, A_H03, A_g, B, B_t, C below; TALK and ACTIVITY channels) on every non-holdout period unit (`period_units`) with ≥ 3 calling agents and ≥ 50 agent messages; day-blocked held-out likelihood needs ≥ 2 days. One README per goal period (`G<NN>/`), role `replication`; the prediction there is templated from this card and labelled as such.
- **Period-native tests (layer 2):** four tests whose setup gives leverage no other unit has (each with its own observable, null and dated prediction; role `native`):
  - **NE41** (regime III, forced consolidation at the 41-turn cap): a quasi-random context erasure *inside* the read-out kernel's tail. If the tail lives in the recipient's context, a forced reset between the read-out call and a later call must cut it.
  - **NE14 at #35/#36** (regime II → III, 2026-03-24): the call clock changes from scheduled chat-mode calls (~74 s cadence) to chained computer-use calls (~13 s) with timer pauses. The read-out kernel's time base changes; its per-item weight should not, while the exponential kernel's timescale and n_cross should shift.
  - **#51** (11 non-holdout segments, N 21 → 32, many messages): consistency of n_cross across segments as headcount grows, and per-pair scaling (H03/H18: attention-limited coupling).
  - **#27** (regime I, 10 days, N = 10): chat-mode calls are *scheduled*, not message-triggered (45% of chat calls have no new message; DQ1), so the read-out gate is an exogenous clock. Tests whether A's fitted timescale is just a smeared read-out lag.

  **NE20 and NE44 (suggested in the brief) cannot be used in round 1.** NE20 (2026-06-03) lies inside #45 and NE44 (2026-06-11) inside the NE21+NE23 window, both locked holdout. Under the reuse policy they are also blocked for H42's confirmation: H04 already ran Hawkes branching on #45–#50 (`holdout_ledger.check` → not allowed, same estimator family). A non-holdout before/after comparison (#44 vs #51a) would be confounded by NE22, NE24, NE26 and the roster, so it is not run. Listed for Vivian as an override decision.

## Model
**From:** `physics-models/09-hawkes/` (multivariate, fixed-timescale kernel grids, H03's M3 parameterization: homogeneous self and cross weights, agent-day baselines).

Each realization is one (unit, village day); t is seconds since the day's window start (clipped to the unit's start/end where a day is split). Excitation never carries across days. Agent i is at risk only inside its **span** (its first call start to its last call end that day), minus **masked** time: village-off gaps, ≥ 10 min with no agent call in progress, rebuilt from `call_windows` (A2; originally H38's stall minutes, dropped because they derive from the buggy `activity_bins`). Events inside masked time are dropped.

  λ_i(t) = c_{i,d} s_{b(t)} + E_i(t) + Σ_q a_q β_q Σ_{t_k^i<t} e^{−β_q (t − t_k^i)} + X_i(t)

- **Baseline:** agent-day level c_{i,d} × a shared within-day shape s_b in 30-min bins (H03's B2a). Absorbs co-modulation slower than ~30 min and day-level headcount.
- **Exogenous drive E_i (all specs, never counted as cross-excitation):** human messages and automated messages (nudges, pause/resume bookends) read by i (ledger items of kind human / nudge / pause_resume), each as a read-out-anchored exponential basis with τ ∈ {2, 10, 60} min and free amplitudes ≥ 0; a goal-kickoff bump e^{−t/τ}, τ ∈ {20 min, 2 h}, on the goal's first day. **TALK only:** the *own call clock*, a pulse γ f_i(t − c_{k*(t)}) after each of i's receiving calls (k*(t) = i's latest call start ≤ t; f_i = log-normal density of i's talk delay after its call start, fitted per agent and unit; the pulse ends at the next call start). Talk can only be logged shortly after a call starts; without this term any kernel anchored at a call start would gain likelihood for free.
- **Self-excitation (all specs):** i's own events, grid τ_q ∈ {10, 30, 100, 300, 1000, 3000} s. ACTIVITY adds a second self family for "wake" calls (gap kind pause / first-of-day / marker / session start), so the chain that follows a wake is not credited to the messages read at it.
- **Cross-excitation X_i (the object), sources = other agents' chat messages m read by i on the same day** (ledger items of kind agent; posting time s_m; read-out call k1(m) with start r_m = t_call; read-out lag r_m − s_m):
  - **S0:** none (scheduler + exogenous + self only).
  - **A (exponential from arrival; H03's shape, room-aware pairs):** Σ_m Σ_q a^x_q β_q e^{−β_q (t − s_m)}, τ_q ∈ {10, 30, 100, 300} s (H03's "fast" range).
  - **A_H03 (secondary, continuity):** the same kernel, room-blind: sources are all messages by every other agent present that day (H03's M3 at-risk set).
  - **A_g (exponential from arrival, gated at i's calls):** at time t after call k*, f_i(t − c_{k*}) Σ_{m: s_m < c_{k*}} e^{−β_q (c_{k*} − s_m)}, same τ grid. Wall-clock decay since arrival, but only expressed at i's calls: the rival that isolates *call index since read-out* from *time since arrival*.
  - **B (read-out kernel, call-index tail; primary):** f_i(t − c_{k*}) Σ_b (w_b / M_b) Σ_{m: k* − k1(m) ∈ bin b} 1, with call-index bins b ∈ {0}, {1}, {2–3}, {4–7}, {8–15} (M_b calls per bin). Each read message adds a pulse at i's read-out call and a weight-decaying pulse at each of i's next 15 calls. w_b is the expected number of extra talk events per read message from calls in bin b. *(Read-out kernel (call-index), proposed variant.)*
  - **B_t (read-out onset, wall-clock tail):** Σ_m Σ_q a_q β_q e^{−β_q (t − r_m)} 1[t ≥ r_m], τ grid as A.
  - **C (hybrid):** A + B, all components free.
  - **ACTIVITY channel** (events = i's call records, `t_first`): the pulse construction does not apply (every call record follows its own call start). Specs S0, A, B_t, C = A + B_t with two source families: **visible** = other agents' messages read by i (B_t onset at the read-out call's record, so the read-out call itself, whose timing was fixed before it read anything, is not an offspring); **invisible** = other agents' non-talk calls (never in i's context; B_t onset at i's next call record after them). Under read-out gating the invisible family should carry nothing beyond co-modulation.
- **Branching ratios (cross-branching ratio, compensator share; proposed variant):** for a fitted spec, n_cross = (Σ_i ∫ X_i dt)/N_events, n_self likewise, n_tot = n_self + n_cross (+ n_exo reported separately). Equals H03's (m̄ − 1)·Σ weights when kernels are not truncated; it counts truncation by day ends and spans automatically, so specs with different shapes are comparable. Per-pair weight = n_cross / (mean recipients per message).
- **Fit:** all kernel timescales are fixed grids, so λ is linear in every amplitude and bilinear in (c, s); maximum likelihood by L-BFGS-B in log-parameter space with analytic gradients (as H03), amplitudes ≥ 0. Day-blocked held-out log-likelihood: train on the other days, refit only the agent-day levels c on the test days (H03's convention).

**What each spec predicts here.** B: cross mass concentrated at bins 0–1, held-out likelihood above A, n_cross(B) > n_cross(A) because responses read after pauses and long calls (read-out lag ≫ 300 s) are captured. A: if cross-excitation were an ungated reaction to arrival (or a shared drive), A and A_g would match or beat B and C would load on A.

## Data scheme (`scheme/`)
- **Inputs:** `call_windows` (turn_id, agent, pt_date, goal_no, holdout, kind, talk, ctx_mode, t_call, t_call_lo, t_call_hi, start_conf, t_first, t_end, gap_kind, first_of_day), `context_ledger_turns` (reset_forced, reset_consol, reset_session, k_new), `context_ledger_items` (turn_id, message_id, sender, kind, ment, uncertain), `chat_core` (message time, room, speaker), `calendar` (windows), `period_units` (units, start/end). The Claude Code agent (no `call_windows` rows) is a source, never a recipient, as in the ledger.
- **Transform (`scheme/build.py`):** per non-holdout period unit (holdout asserted twice: `calendar.holdout` and `infra/shared/common.py: holdout_mask`), per unit-day:
  1. calls of every non-Claude-Code agent (times in seconds since the window start; receiving = `ctx_mode != summary`; wake flag; forced-reset flag of the *next* receiving call);
  2. agent chat messages, each mapped to its talk call (as-of join on agent; 100% matched in #38);
  3. same-day ledger items (recipient, sender, kind, posting time, receiving call), agent and exogenous;
  4. masked intervals (village-off gaps ≥ 10 min outside the union of all agents' call intervals);
  5. per-agent spans.

  My own read-out rule (first receiving call with t_call > s) reproduces the ledger's assignment 100% in #27 and #38, so null surrogates and the t_call_lo / t_call_hi sensitivity recompute read-outs with the same rule.
- **Output:** `data/processed/H42-readout-hawkes-kernel/G<NN>/` (`days`, `calls`, `talk`, `items`, `mask` parquet; per-unit fit results), `synthetic/`, cross-unit result tables, `_provenance.json`. Budget ≤ 200 MB.
- **Regimes covered:** I, II, III (non-holdout only); every fit is within one unit.

## Observables
Per unit and channel:
1. **Held-out log-likelihood** per event (day-blocked: leave-one-day-out for ≤ 6 days, 5 folds otherwise) for S0, A, A_H03, A_g, B, B_t, C; Δℓ(B − A), Δℓ(C − A), Δℓ(B − A_g), Δℓ(B − B_t).
2. **Branching ratios** n_self, n_cross, n_tot per spec; per-pair cross weight.
3. **Kernel shapes:** B's call-index weights (share of cross mass in bins 0, 1, 2–3, 4–7, 8–15); A's and B_t's τ-weights and mean timescale; C's split of cross mass between A and B components.
4. **Read-out lag** distribution per unit (median, q90) and A's fitted mean timescale against it.
5. **Consistency:** n_cross per spec across units: medians by regime, the max/min ratio of regime medians, the CV of log n_cross across units, I² across periods; within-period random-effects (DerSimonian–Laird) pooling of unit estimates for split periods (exception d), reported next to the raw unit estimates.
6. **Sensitivity:** read-outs and pulse anchors recomputed with t_call_lo and t_call_hi; edge-trimmed spans (drop each agent's first and last 10 min, H38's day-edge concern).

## Null / baseline
- **S0** (scheduler + exogenous + self, no cross) on held-out days: every cross spec must beat it.
- **Shift null (cross streams):** each sender's messages circularly shifted within the day window by an independent offset ±U(5, 30) min; read-outs recomputed on the recipients' real call grids with the same rule; self streams, baselines, exogenous inputs and recipients' call clocks unchanged. 5 surrogates per unit (A, B, C refit in sample; 2 surrogates also through the held-out pipeline for Δℓ(B − A)). This null keeps any call-locking advantage of B (shifted messages are still read at real calls), so B's real-minus-null gain isolates timing information.
- **Day-block null:** recipient i's day d paired with the source messages of another day of the same unit (aligned by time since window start), read-outs recomputed on day d's call grid. Up to 3 surrogates per unit with ≥ 2 days.
- **Synthetic guard (axis F, before real data):** talk processes simulated on the real call schedules, spans, stalls and day edges of real units, with planted (i) read-out-gated cross-excitation (B-truth), (ii) exponential cross-excitation from arrival, not gated (A-truth), (iii) none, plus a shared 10–30-min rate modulation in every arm; fits use the estimated t_call while the simulation uses call starts redrawn inside [t_call_lo, t_call_hi].

## Prediction
*Written 2026-10-04 06:40 UTC, before any real-data fit. Seen beforehand: table schemas and counts, the message → talk-call mapping, and the read-out lag quantiles of #27 and #38 (quoted above, from the ledger validation). Not seen: any likelihood, kernel weight or branching ratio from these data. Not blind to H03's, H08's, H19's and H25's published per-period numbers.*

Primary channel TALK (H03's primary; the read-out mechanism acts on what an agent says at a call, and the synthetic validation covers it). ACTIVITY is secondary: in regime III a message cannot trigger a call (wakes are timer-gated, DQ1), only change what the read-out call does, and H38 showed most regime-III activity co-activation is scaffold. CV-eligible units: ≥ 2 days, ≥ 3 calling agents, ≥ 50 agent messages.

| # | Prediction | Counts against |
| --- | --- | --- |
| P1 | **Fit.** B beats A on day-blocked held-out log-likelihood in ≥ 70% of CV-eligible units (median Δℓ(B − A) > 0); ≥ 80% in regimes II/III; ≥ 50% in regime I (tempered: H08's read-out jump failed on talk in every regime-I/II period under the old call-start rule) | ≤ 50% of units, or median Δℓ ≤ 0 |
| P2 | **Not a call-locking artifact.** The in-sample advantage of B over A (Δℓ_B − Δℓ_A, each vs S0) exceeds the 95th percentile of its shift-null surrogates in ≥ 60% of units | ≤ 30% |
| P3 | **Exponential kernels understate n_cross.** n_cross(B) > n_cross(A) in ≥ 70% of units; median ratio n_cross(B)/n_cross(A) ≥ 1.3 | median ratio ≤ 1 |
| P4 | **More consistent across regimes.** The max/min ratio of regime medians of n_cross, and the across-unit CV of log n_cross, are both smaller for B than for A | either is larger for B |
| P5 | **Shape: a delayed step, short in call units.** ≥ 60% of B's cross mass in bins 0–1 (median over units); in C, ≥ 70% of the cross mass on the B components (median) | C puts the majority on A |
| P6 | **Beats the nulls.** n_cross(B) exceeds the shift-null 95th percentile in ≥ 70% of units, and the day-block null mean in ≥ 70% of units with ≥ 2 days | ≤ 40% |
| P7 | **Call clock, not wall clock, after read-out.** B ≥ B_t on held-out likelihood in ≥ 60% of units | ≤ 40% |
| P8 | **Call index since read-out, not time since arrival.** B ≥ A_g on held-out likelihood in ≥ 60% of units | ≤ 40% |
| P9 | **ACTIVITY (secondary).** Visible-source B_t beats A on held-out likelihood in ≥ 60% of units; the invisible family's n_cross under B_t is inside the shift-null band (≤ q95) in ≥ 70% of units | B_t ≤ A in > 50%; invisible B_t above its null in > 50% |
| G1 | **Guard (synthetic).** B-truth: B or C selected (held-out) in ≥ 80% of replicates and n_cross(B) within ±25% of truth; A-truth: B not selected over A in ≥ 80%; null-truth: n_cross(B) and n_cross(A) inside the shift-null band in ≥ 90% | any fails → the real-data comparison is not interpretable as stated |

**Replication verdict rule (per goal period, over its CV-eligible units, TALK):** *supported* if summed held-out Δℓ(B − A) > 0, n_cross(B) > n_cross(A) and n_cross(B) > its shift-null q95; *failed* if Δℓ(B − A) ≤ 0 and n_cross(B) ≤ n_cross(A); *mixed* otherwise; *descriptive* where no unit is CV-eligible (in-sample fits only).

Native predictions are in the `NE41/`, `NE14/`, `G51/` and `G27/` READMEs (written before those runs).

## Amendments
- **2026-10-04 07:20 UTC · A1, two coherent "worlds" for TALK (after smoke-test fits on #38a, #27 and #51c only; no other unit fitted).**
  - **What the smoke tests showed.** With the own call-clock pulse in every spec (the pre-registered design), every continuous-time kernel is driven to exactly zero: A, A_H03, B_t, and even continuous self-excitation (n_self = 0). Talk can only be logged a few seconds after a call starts, so a kernel that spreads mass between calls gains nothing. Under the pre-registered design, A vs B therefore tests "is talk call-locked?" (trivially yes) more than kernel shape. The informative pre-registered comparisons are B vs A_g (P8) and B vs the nulls (P2, P6).
  - **Second confound.** In #27 (regime I) B's item count tracks the call type: scheduled chat-mode calls accumulate more messages per call *and* talk far more often than computer-use calls; wake calls likewise. With a single global pulse weight, B absorbed that (n_cross 0.67).
  - **Amendment.** The pre-registered design ("world pr") is run unchanged and scored against P1–P9 as written. Two internally coherent worlds are added and reported next to it:
    - **World A (H03 world):** no call clock; continuous baseline c_{i,d}s_b, continuous self, exogenous items from posting time, kickoff; cross specs A, A_H03, B_t. This is the fair home of the exponential kernel.
    - **World B (call-clock world):** everything is expressed as pulses at i's receiving calls, λ_i(t) = f_i(t − c_{k*})·[c_{i,d,κ} s_b + Σ gated terms], with **separate baseline levels per call class κ ∈ {chat, computer-use} × {wake, other}** (all known before the call reads anything), gated self-excitation (own past messages, wall-clock decay evaluated at call starts) and gated exogenous terms. Cross specs: B (call index since read-out), A_g, C = B + continuous A, C_g = B + A_g. The pulse is a mixture: 95% log-normal talk delay, 5% exponential with a 120-s mean, so long tool calls do not get near-zero density.
  - **How the predictions map.** P1 and P3 are scored in world pr (as written) and, as amended readings, by comparing each world's own cross spec: held-out cross gain Δℓ(cross − S0) per event and n_cross of world A's A vs world B's B. P2/P6 use each world's own shift and day-block nulls. Effect of the class baseline on #27 (disclosed): S0 improves by about 4,000 nats and B goes to 0.
- **2026-10-04 · A2, masks.** The coordinator flagged that `stall_minutes` / `outages` derive from the buggy `activity_bins` (joint silences over-counted; 6% of talk events fell inside the "explained stall" mask). Masks are now village-off gaps rebuilt from `call_windows` (≥ 10 min with no agent call in progress); no shared stall table is used.

- **2026-10-04 08:25 UTC · A3, calibration from the synthetic validation (G1 failed as written; details under Results).** The pre-registered estimator (world pr) inflates n_cross by about 70% and returns 0.12–0.47 with no cross-excitation. World A's exponential returns 0.03–0.17 under a shared 15-min field. World B recovers planted read-out excitation (median error +6%) but still returns up to 0.046 from the shared field alone, above both empirical nulls, and absorbs about two thirds of planted *ungated* excitation (CV prefers A_g in 6/8 such runs). Consequences, fixed before the full real-data results were read (8 small units, all ≤ 2 days, seen while debugging `summarize.py`):
  - **amended period verdict:** *supported* only if world B's read-out gain over S0 is positive and exceeds world A's exponential gain, n_cross(B) beats both world-B nulls, and the event-weighted n_cross(B) exceeds the **field floor 0.05**; *failed* if the gain is ≤ 0 or the nulls are not beaten; *mixed* otherwise;
  - world-pr and world-A branching ratios are reported but not interpreted as cross-excitation;
  - "B beats A_g" is weak evidence for gating, because B also absorbs ungated excitation.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness". Scores are for the read-out cross kernel B on TALK, non-holdout units (exploratory).
**Rival models:** exponential cross-kernel from arrival (A, H03); the same kernel gated at the recipient's calls (A_g); read-out onset with a wall-clock tail (B_t); scheduler-only (S0); shared modulation (the shift and day-block nulls, the synthetic shared field).
**Locked holdout used for confirmation:** none yet. `analysis/confirm.py` (dry-run on stand-ins) targets #51 tail, #28, #22, #29a, #43 (all allowed by `holdout_ledger.check`); NE20 and NE44 are blocked (H04's Hawkes run on #45–#50).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | **From fields:** events, read-outs and spans come from the ledger. My read-out rule reproduces `context_ledger_items` 100% (#27, #38). **Assumptions listed:** call starts are calibrated, not measured, for non-Gemini agents. **Not invariant:** the kernel's weight changes with regime (I ≈ 0, III ≈ 0.01–0.05) and across NE14. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | **Audits passed:** update order (message → call mapping 100%; read-out assignment 100%). **Sensitivity:** robust to t_call_lo / t_call_hi and to 10-min edge trims (median n_x ratio 1.0). **Not done:** time-rescaling KS. **Stationarity:** handled by agent-day (× call-class) baselines only. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | **Call clock:** the call-clock world beats the H03 world on held-out likelihood in 57/57 units (median +1.10 nats/event). **Read-out cross term in that world:** beats S0 in only 42% of units (61% in regime III) and its shift null in 42%; it is below the synthetic shared-field floor in all but one period. |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | **Failed:** NE41 tail cut (R_forced = 3.1 ± 2.5) and G51 consistency. **Shape:** the hop-1 shape (100% of B's mass at calls 0–1 where B ≠ 0) is fitted, not predicted. |
| E interventional | predicts the change across a natural experiment | 0 | NE41 (quasi-random erasure) and NE14 (call-clock change) both failed. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | **Recovers:** world B recovers planted read-out excitation (within ±25% in 15/16, median +6%; B or C_g selected 16/16). **Fails:** the pre-registered world inflates n_x by about 70% and returns 0.12–0.47 with none planted; a shared 15-min field gives up to 0.05 (world B) and 0.17 (exponential), above both empirical nulls; B absorbs about two thirds of planted ungated excitation. G1 failed as written. |
| G ground truth | agrees with known structure | 1 | **Agrees with known structure:** the hop-1 concentration matches H08's read-out jump and H50's "gated at exactly hop 1"; world A's exponential n_x (median 0.061) replicates H03's fast n_x ≈ 0.07 (0.074 in H03's round 1b). **Not checked:** the Claude Code input stream, which would be a talk-level ground truth. |
| H comparative | beats the named rivals | 0 | **Loses to rivals:** in a coherent comparison the exponential world's cross gain exceeds the read-out cross gain in 2/3 of units; B ≥ A_g in only 40%; S0 is as good as B in 58% of units. The pre-registered wins over A are call-locking artifacts (G1). |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Regime-dependent (absent in regime I/II); no holdout run. |

## Results by goal period
Verdicts: the *amended* reading (A1/A3) is primary; the pre-registered rule's verdict is listed beside it but is void (G1 failed: world pr reports cross-excitation where none is planted). Key numbers: event-weighted n_x of world B's read-out kernel and world A's exponential kernel; summed held-out cross gains (nats) over the period's multi-day units.

| Period | Role | Verdict (amended; pre-registered) | Key numbers: world-B n_x(B) · world-A n_x(A) · read-out gain vs exponential gain (nats, held out) |
| --- | --- | --- | --- |
| [G02](goalperiod-subhypotheses/G02/README.md) | replication | failed; pr supported | 0.022 · 0.166 · -3.9 vs -42.3 |
| [G03](goalperiod-subhypotheses/G03/README.md) | replication | failed; pr supported | 0.067 · 0.141 · +0.0 vs -175.5 |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | failed; pr supported | 0.030 · 0.121 · +4.9 vs +72.6 |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | failed; pr mixed | 0.026 · 0.087 · +0.8 vs +2.7 |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | failed; pr mixed | 0.000 · 0.129 · -918.4 vs +133.8 |
| [G07](goalperiod-subhypotheses/G07/README.md) | replication | failed; pr mixed | 0.000 · 0.126 · -0.3 vs +4.1 |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | failed; pr mixed | 0.000 · 0.016 · -0.0 vs -0.9 |
| [G10](goalperiod-subhypotheses/G10/README.md) | replication | failed; pr mixed | 0.010 · 0.078 · -1.1 vs +0.5 |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | mixed; pr supported | 0.013 · 0.071 · +1.9 vs +4.1 |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication | failed; pr supported | 0.006 · 0.099 · -0.8 vs +10.8 |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | failed; pr supported | 0.000 · 0.040 · -0.0 vs +4.2 |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | failed; pr supported | 0.011 · 0.076 · -3.5 vs +7.4 |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | failed; pr supported | 0.000 · 0.133 · -0.0 vs +15.4 |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | failed; pr supported | 0.002 · 0.085 · -1.3 vs +43.2 |
| [G19](goalperiod-subhypotheses/G19/README.md) | native + replication | native N4b supported (against the hypothesis); replication failed; pr supported | 0.000 · 0.101 · -0.4 vs +29.7 |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | failed; pr mixed | 0.002 · 0.089 · -0.9 vs -206.5 |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | failed; pr mixed | 0.002 · 0.046 · -1.5 vs +9.7 |
| [G23](goalperiod-subhypotheses/G23/README.md) | replication | failed; pr supported | 0.000 · 0.060 · +0.0 vs +9.5 |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | failed; pr supported | 0.002 · 0.124 · -1.0 vs +9.9 |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | failed; pr supported | 0.009 · 0.112 · -2.3 vs +19.2 |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | failed; pr supported | 0.030 · 0.223 · -0.5 vs +46.1 |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | failed; pr supported | 0.000 · 0.071 · -0.0 vs -1.5 |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | mixed; pr supported | 0.000 · 0.111 · +0.1 vs +12.1 |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | failed; pr supported | 0.000 · 0.070 · +0.0 vs +4.1 |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | failed; pr supported | 0.000 · 0.094 · -1.2 vs +1.1 |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | failed; pr supported | 0.010 · 0.091 · -0.9 vs +7.9 |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | mixed; pr mixed | 0.031 · 0.040 · +8.2 vs +10.3 |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | mixed; pr supported | 0.027 · 0.032 · +3.3 vs +3.4 |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | mixed; pr supported | 0.036 · 0.031 · +11.0 vs +1.3 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | supported; pr supported | 0.072 · 0.081 · +14.8 vs +6.6 |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | failed; pr mixed | 0.004 · 0.000 · +0.2 vs -0.8 |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | mixed; pr supported | 0.014 · 0.045 · +3.3 vs +0.8 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | mixed; pr supported | 0.047 · 0.034 · +3.8 vs -2.6 |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | failed; pr supported | 0.000 · 0.005 · -0.0 vs -0.9 |
| [G51](goalperiod-subhypotheses/G51/README.md) | native + replication | native failed; replication mixed; pr supported | 0.016 · 0.024 · +36.4 vs +72.3 |
| [NE14](goalperiod-subhypotheses/NE14/README.md) | native | failed | world-B n_x 0.007 → 0.027 across the boundary (A 0.045 → 0.032); A's τ 81 → 30 s while read-out lag 43 → 108 s |
| [NE41](goalperiod-subhypotheses/NE41/README.md) | native | failed | R_forced = 3.1 ± 2.5 (predicted ≤ 0.5); 27 regime-III units |

## Results
*Exploratory round 1 (2026-10-04): 71 non-holdout period units (57 with ≥ 2 days) in 35 goal periods, ~127k agent messages, 1.89M calls. No holdout touched. Numbers from `data/processed/H42-readout-hawkes-kernel/scores.json`, `native_summary.json`, `synthetic/synthetic_summary.json`, `NE41/ne41_summary.json`, `posthoc_mention.parquet`. Code: `analysis/run_units.py` (fits, CV, nulls, sensitivity), `summarize.py`, `native_ne41.py`, `native_summary.py`, `posthoc_mention.py`, `synthetic.py`, `synth_report.py`, `figures.py`.*

### Headline
**Not supported as posed.** Modelling the read-out does not raise cross-excitation; it removes most of it. What a read-out-aware model shows is that talk is locked to each agent's *own* call clock. Once that clock (and the call type) is in the baseline, messages read at a call barely change whether the agent talks: median n_cross ≈ 0.004 per message (regime I ≈ 0, II 0.005, III 0.013), against 0.061 for H03's exponential kernel. "Exponential kernels understate n_cross" is reversed: they overstate it, by attributing call-schedule co-movement to triggering. The one place a read-out kernel carries real talk excitation is post hoc and confined to regime III: **messages that name the recipient** (about 0.15 extra talk events per named message, beating the shift null in 25/27 units); unnamed messages carry ≈ 0.

### Synthetic validation (axis F; G1 failed as written, A3)
32 simulations on the real call grids, spans and masks of #27, #33, #40 and #51c (2 reps × 4 truths), with call starts redrawn inside their bounds and a shared 15-min rate field in every arm:

| truth | world pr (pre-registered) | world A (H03 world) | world B (call-clock world) |
| --- | --- | --- | --- |
| read-out (n_x 0.15, 0.30) | B or C selected 15/16, but n_x +69% (within ±25%: 1/16) | B_t selected 16/16 (call-locking); A's n_x +19% | B or C_g selected 16/16; n_x within ±25% 15/16 (median +6%); 73% of B's mass at calls 0–1 |
| exponential, ungated (0.30) | A beats B 8/8 | A selected 8/8 (n_x +22%) | A_g beats B 6/8; B absorbs 68% |
| none (shared field only) | n_x(B) 0.12–0.47; never inside its nulls | n_x(A) 0.03–0.17; never inside its nulls | n_x(B) 0.00–0.046; inside the shift band 2/8 |

- **The shift and day-block nulls do not control a shared 15-min field.** Every estimator beats them with no cross-excitation planted. Hence the field floor of 0.05 in the amended verdict rule.
- **The pre-registered world mistakes "talk happens at calls, and chat-mode calls both talk more and read more" for cross-excitation.** This is the regime-I call-type confound (#27: n_x 0.67).

### Outcome vs prediction
"pr" = scored as written (world pr); "amended" = the coherent-world reading (A1, A3).

| # | Prediction | Observed | Outcome |
| --- | --- | --- | --- |
| P1 | B beats A held out in ≥ 70% (II/III ≥ 80%, I ≥ 50%) | pr: 89% (I 100%, II 100%, III 74%), median +0.08 nats/event. Amended: read-out gain > exponential gain in 33% (III 52%); median gains −0.001 vs +2.3 mnats/event | pr met but **void** (G1); amended **failed** |
| P2 | B's advantage over A beats its shift null in ≥ 60% | pr in sample 83%, held out 89%; world B (B vs A_g, held out) 49% | pr met but void (the nulls miss call-type and shared-field structure); amended **failed** |
| P3 | n_x(B) > n_x(A) in ≥ 70%, median ratio ≥ 1.3 | pr: 99%, B 0.41 vs A 0 (every continuous kernel is driven to 0). Amended: 20%, ratio 0.22; world B 0.004 vs world A 0.061 | pr void; amended **failed (reversed)** |
| P4 | more consistent across regimes | regime medians, world B: I 0.0000, II 0.005, III 0.013 (max/min 13.5); world A: 0.084 / 0.091 / 0.018 (4.9); pr B 0.57 / 0.32 / 0.08 (6.9) | **failed** |
| P5 | ≥ 60% of B's mass at calls 0–1; C ≥ 70% on B | world B (34 units with n_x > 0.005): 100% at calls 0–1, 73% at the read-out call. C on B: pr 1.00, but world B 0.00 (C's continuous A substitutes for the missing continuous baseline) | shape **supported**; hybrid split uninformative |
| P6 | n_x(B) above its shift q95 / day-block mean in ≥ 70% | pr 75% / 96% (void); world B 42% / 63% (day-block max 54%) | amended **failed** |
| P7 | B ≥ B_t held out in ≥ 60% | pr 84% (B_t is pulled to 0 by the pulse) | met, uninformative |
| P8 | B ≥ A_g held out in ≥ 60% | pr 82%; world B 40% (median −0.12 mnats/event) | amended **failed** |
| P9 | activity: visible B_t > A in ≥ 60%; invisible B_t within its null in ≥ 70% | B > A in 60% (30/50), median +0.16 mnats/event, but the gain sits in the *invisible* family (n_Bi 0.0017 vs n_Bv ≈ 0); invisible within null 58% | **failed** (call-clock structure again) |
| G1 | synthetic guard | fails on the null clause in every world | **failed** → A3 field floor |

### Findings
1. **The call clock is the kernel shape that matters, and it is the recipient's own.**
   - **Likelihood:** a model in which talk can only follow the recipient's call starts, with baseline levels per call class, beats the H03 world by 1.10 nats/event (57/57 units). S0 alone beats it by 1.18, and it beats the pre-registered design by 0.58 (56/57).
   - **What this means:** this is self/scheduler structure, not coupling.
   - **Within the H03 world,** the read-out-onset kernel B_t wins in 54/57 units (n_x 0.29). It wins equally under no cross-excitation in synthetics (call-locking).
2. **Message-driven talk excitation is small and regime-dependent.**
   - **World B:** n_x(B) median 0.004; beats S0 held out in 42% of units (I 31%, II 0/3, III 61%).
   - **Periods:** only G39 clears the amended rule (*supported*). 8 are *mixed*: #11 and #30 (regime I), #36, and #37, #38, #41, #42, #51 (regime III), mostly above the nulls but below the field floor. 26 *failed*: every other regime-I/II period, plus #40 and #44. Native G19 shows the regime-I mechanism: talk follows call type, not reading (the pre-registered n_x 0.89 is equalled by its shift null, 0.88).
3. **H03's fast cross-triggering replicates in the H03 world and reads as co-modulation in the call-clock world.**
   - **Replication:** world A's exponential n_x is 0.061 median (room-blind 0.061), above its shift null in 73% of units, close to H03's 0.07–0.074.
   - **Reinterpretation:** most of it disappears when the recipient's call schedule and call class are modelled. Others' messages and the recipient's talk-capable calls co-move in time, but reading more messages does not make a call more likely to talk.
   - **Caveat:** world B conditions on call times and classes, so excitation acting through them is excluded. The activity channel looked for that pathway and found little (visible n_Bv ≈ 0).
4. **The read-out step has the predicted shape where it exists.** Where n_x(B) > 0.005, B's mass is 100% at calls 0–1 (73% at the read-out call), consistent with H08's read-out jump and H50's "gated at exactly hop 1". But B does not beat the gated wall-clock rival A_g (40%), and in synthetics B also absorbs ungated excitation. So the shape is not a discriminating test of gating.
5. **No consistency gain, no interventional support.**
   - **#51:** n_x collapses to 0 from 51h (08-24) on, in both kernels (Spearman with N: −0.78 for B, −0.71 for A), as read-out lags grow (median 19 s → 78–87 s).
   - **NE14:** across the boundary, the call-clock weight moves more than the exponential one.
   - **NE41:** a forced erasure does not measurably cut the tail (R_forced 3.1 ± 2.5; poorly identified).
6. **Post hoc (exploratory; frozen as C5 in `confirm.py`): named messages carry the read-out excitation.**
   - **Design:** world B with B split by the ledger's `ment` flag.
   - **Regime III:** named messages give 0.145 extra talk events each (median over 27 units), above the shift-null maximum in 25/27 units. Unnamed messages give ≈ 0 (above null in 8/27). The split model beats unsplit B held out in 91% of regime-III units (median +37 mnats/event). Named items are only about 7% of items, so pooling dilutes their effect to ~0 (#51h–51l: pooled B = 0, named 0.09–0.22 per message).
   - **Regime I:** 0.010 per named message; split beats S0 in 19%.
   - **Strongest rival:** recipients already mid-exchange (H08/H18) name and talk regardless; this needs DQ2's reply threads to separate.
7. **Activity channel.** The read-out-placed families carry almost nothing for visible messages (n_Bv ≈ 0, above null in 30%). The held-out edge of B over A (60%) comes from others' *non-talk* calls placed after the recipient's next call, which carry no information by construction: call-clock structure again.
8. **Robustness.** t_call_lo / t_call_hi and 10-min edge trims leave world-B n_x unchanged (median ratio 1.0; gain positive in 37–40% vs 42%). Masks come from `call_windows` (A2).

### Figures (`figures/`)
- `summary_obs.pdf`: (a) held-out read-out gain (world B) vs exponential gain (world A) per unit; (b) n_cross by regime for world A's A, world pr's B and world B's B, with shift-null levels.
- `synthetic_compact.pdf`: estimated vs planted n_x for each world's own cross spec.
- `kernels.pdf`: B's call-index shape (world B); A's mean timescale vs read-out lag.
- `ncross_vs_N.pdf`: per-pair weight vs N.
- `activity.pdf`: activity families, real vs shift null.

### Caveats
- **Conditioning on the call clock.** World B treats call times and call classes as given. If messages change *when* agents call or *which kind* of call they make (e.g. ending a computer-use session in regime I), world B rules that out by construction; the activity channel is only a partial check.
- **Calibrated call starts.** Starts are measured only for Gemini (19%); regime-I chat-mode starts are latency-placed (low confidence). Bounds sensitivity changed nothing, but a systematic start bias would.
- **Nulls are weak.** Shift and day-block surrogates do not control a shared 15-min field (synthetic). The 0.05 field floor comes from one synthetic field strength.
- **Amendments.** Three, all dated: A1 after smoke fits on 3 units; A3 after the synthetic run and 8 small units seen while debugging. The pre-registered verdicts are reported and voided, not hidden.
- **Multiplicity.** 7 TALK specs × 3 worlds plus activity, nulls and sensitivity. Period verdicts use one rule; the named-message finding is post hoc.
- **Held-out blow-up.** One fold in #6a (B weight learned on training days, a heavy-message test day) gives −0.93 nats/event; medians are used throughout.
- **Activity CV.** Skipped for units with > 60k calls (#38a, #51 large segments), for cost.
- **Mapping.** One-day units (14) are in-sample only. Rooms are respected through ledger pairs (world A's room-blind A_H03 is the continuity check).

### Next steps
1. Run `confirm.py` on the holdout (C1–C5). C5 tests the post-hoc named-message finding.
2. Separate named-message triggering from ongoing exchanges with DQ2 `reply_pairs` (is the named message a reply to the recipient?) and a mid-exchange stratum.
3. A two-layer point process (call times as their own process, talk as a mark) to test whether messages move call timing or class.
4. A Cox baseline with a latent shared 5–15-min rate, to set the field floor from data.

## Round 2 redirects (2026-10-04)
*From round 1 (H42 agent).*
- **Where round 1 went sideways:** A branching ratio of talk timing mostly measures each agent's own call clock; any kernel anchored at a recipient's call start wins for free, and shift nulls do not catch it.
- **What the direction is really after:** Whether, and through which messages, what an agent reads changes what it does next, measured on the recipient's call clock.
- **H42-R1. Named messages as the coupling carrier.** Confirm the regime-III named-message read-out excitation (0.15 extra talk per named message) with reply-thread controls (DQ2) and per-agent weights; compare with H29's naming pull and H08's addressing jump.
- **H42-R2. Two-layer point process.** Model call times (busy chains, timer pauses, chat-mode schedules) as their own process and talk as a mark, then test whether messages shift call timing or call class.
- **H42-R3. Shared-field control.** A Cox-process rival with a latent common rate (H03's next step), so cross terms are judged against a fitted field, not shift surrogates.

## Notes
- 2026-10-04: The brief asked for activity turns first and talk second; TALK is primary here for the reason given under Prediction (decided before any fit).
- 2026-10-04: A is fitted on the same (message, recipient) pairs as B (room-aware ledger pairs) so that A vs B compares kernel shapes only; A_H03 keeps H03's room-blind at-risk set for continuity (it gives the same median n_x, 0.061).
- 2026-10-04: Overlap with H50: H50 estimates a hop-indexed read-out jump with a logistic call-level model and found talk coupling gated at exactly hop 1; H42's world-B B (100% of mass at calls 0–1) agrees. H42 adds that the per-message size of that jump is ≈ 0 for unnamed messages.
- 2026-10-04: World B's hybrid C (B + continuous A) is the best world-B spec in 39/57 units with its mass on A. In world pr, which has a continuous baseline, A gets exactly 0, so this A is a stand-in for world B's missing continuous baseline (pulse misspecification), not ungated excitation.
- 2026-10-04: Compute: local, 2 processes × 1–2 threads; the full replication run took ~70 min wall; synthetic ~45 min.
