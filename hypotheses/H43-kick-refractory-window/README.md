# H43: Kicks leave a refractory window

**Status:** round 2 done (2026-10-05, exploratory): one read is one kick (a second directed item in the same call adds 0.11 [0.01, 0.21] of the first in #51, provider- and timing-robust); re-fired nudges are not better than first ones at matched trap state; the NE43 drop is a cadence change from the one-room week, not the nudger. Round 1 (2026-10-04): no refractory window. Second kicks read by a later call keep 80–130% of the first's effect; only kicks read in the same call are wasted. Reserved data not used.
Design, nulls and predictions P1–P10 were written before any real-data outcome; synthetic validation (axis F) came first; 35 non-holdout goal periods (replication) and 3 native tests (NE43, G38, G04).
**Headline: there is no refractory window.** A second kick read by a later model call keeps 80–130% of the first kick's effect at every spacing measured, from 1 min to 4 h:
- **Mentions:** a shallow dip, pooled R(δ ≤ 15 min) = 0.78 [0.67, 0.89] over 15 periods, recovering by about 1 h.
- **Human messages** (G04): R(δ ≤ 2 min) = 1.46.
- **Nudge re-fires:** R(15–60 min) = 1.28 when a glance counts as escape.

The only near-zero marginal effect is for a kick read *in the same call* as another (R ≈ 0.2–0.4). Read-out batching, not the task episode, is the refractory unit. The episode-lock signature (in-episode R ≈ 0.2 vs ≈ 1 otherwise, recovered in the synthetic) is absent (0.65–0.69 vs 0.81–0.84).

Side finding: a first nudge after a quiet spell makes idle agents glance (×1.75) but does not start sustained work (lnHR 0.07, n.s.). `analysis/confirm.py` is written and dry-run on stand-ins; **not run**.
**Fields:** dynamics, stat mech (renewal / refractory point processes), sociophysics (operator levers)
**Literature:** none of the notes in `literature/` covers refractory point processes; references in `physics-models/09-hawkes/` (Hawkes 1971†; Bacry, Mastromatteo & Muzy 2015† for nonlinear/inhibitory kernels). Refractory renewal processes are textbook (Cox, *Renewal Theory*, 1962†; Gerstner & Kistler, *Spiking Neuron Models*, 2002†, ch. 5 on refractoriness and the SRM₀ recovery function).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime; Action; Agent state (categorical: action class, H14's `lump4` scheme on the minute grid) for task episodes; Driving / external field (nudges, human messages); Interaction (addressed) for @-mentions; **Lever episode** (H39: isolated kick, controls eligible on past information only, both arms cut at the next kick). New named terms proposed for DEFINITIONS.md (owner to add): **"receiving call"**, **"kick spacing (read-out)"**, **"launched episode"**, **"refractory ratio R(δ)"** (defined below).
**From:** HH177 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/09-hawkes/` (refractory / renewal variant), `physics-models/03-contagion/` (SIRS-like refractory compartment)
**Data inputs (shared tables first):** `kicks_classified`, `states_min` (behavior states), `period_units`, DQ1 context ledger (`call_windows`, `context_ledger_turns`, `context_ledger_items`), DQ4 work ledger (`work_commits`, `work_api_writes`) for writes, `calendar`.

## Standards (2026-10-04)
*Documentation pass against `STANDARDS.md`. No analysis was re-run. H43 has no round-1b section; round 1 already ran on the corrected inputs.*

**Question served:** Q5. The deliverable is a kick-spacing rule for operators. Q1 second: the read-out call, not the task episode, is the unit of coupling.

| Impostor | Relevant? | How it was handled | Status |
| --- | --- | --- | --- |
| Scheduler field | partly | Outcomes run from the receiving call. Matched strata include day third and a swarm-activity tercile (Observables). No synchrony statistic. | removed |
| Exogenous field (kickoff/goal/operator) | partly | A 30-min quiet rule for primers; other-class kicks in the previous 10 min are a stratum; both arms cut at the next kick. The nudger's text trigger is unobserved, so nudge facilitation may be selection (Caveats). | partly |
| Shared model priors | no | Same-agent controls where a stratum has ≥ 5; no family or content claim. | n/a |
| Contemporaneous convergence | no | The refractory ratio compares read kicks; no copying or influence claim. | n/a |

**Inputs:** round 1 uses the context ledger, DQ4 work ledger and shared `states_min`; it never reads `activity_bins` (Caveats). Still old: nudge kicks are ledger items with the `ment` flag, which also counts agents named second; the leading-@ target is not applied. Embeddings and failures are not inputs.

**Two layers:** 33 replication folders (12 testable class × period cells, none passed). Native tests: 3 (`G04` and `NE43` failed; `G38` untestable).

**Confirm script:** `analysis/confirm.py` exists, dry-run only, built on the ledger and work ledger. No re-freeze for activity or visibility. Apply the leading-@ target to C4's nudges before any holdout run (STANDARDS §2).

## Question
After an effective kick (nudge, named message, human message), is the recipient refractory for about the length of the task episode the kick launched, so that a second kick inside that window has near-zero marginal effect? Operator payoff: a minimum kick-spacing rule per kick type.

## Design: two layers (Vivian, 2026-10-04; see `infra/data-quality/QUEUE.md`)
- **Replication:** the common estimator (below) on every eligible non-holdout goal period. Period README role: `replication`; the per-period prediction is templated and labelled as such.
- **Period-native tests:** three designs that only one period (or NE) allows, each with its own observable, null and dated prediction. Role: `native`.
  - **NE43** (#51 before vs after 2026-08-21): the nudger re-fires before (the dose-spacing data) and is silent after. Tests: the nudge spacing curve; a swarm-level prediction of the nudger-off change from the per-kick curve (refractory vs additive accounting); invariance of the mention curve across the switch.
  - **G38 pause gates** (H16): regime-III agents read kicks only when their own PAUSE timer expires, so every kick is read at a gate. Tests: gate escape after a directed kick vs time since the agent's previous effective kick; the batched-dose limit (two kicks read at the same gate).
  - **G04** (regime I, human-driven, 4 agents, 25 days, public human chat): chat-mode calls are *scheduled, not message-triggered* (DQ1: median cadence 74 s; 45% of calls carry no new message), so whether a human message lands in this call or the next is set by the scheduler's phase. Tests: human-message trains, second-message effect vs spacing.

## Model
**From:** `physics-models/09-hawkes/` (nonlinear Hawkes with an inhibitory self-kernel, i.e. a renewal process with a recovery function) and `03-contagion/` (an SIRS-like refractory compartment: a kicked-and-responding agent is "R", not susceptible to a new kick until it returns to S).

**H43 variant: a kicked renewal agent (SRM₀-type).** An agent alternates between idle and active (task) episodes. A kick read at time t (the *receiving call*, below) multiplies the agent's escape hazard out of idle by a transient gain:

  λ_esc(t) = λ₀(a(t)) · [1 + g_c · κ(t − t_read) · r(t − t_last)],

with λ₀(a) the baseline escape hazard at idle age a (aging, H16), g_c the gain of kick class c, κ the response kernel (H04/H08: dead time ≈ 5 min, plateau to ~15–30 min), and **r(·) the recovery function** measured from the previous effective kick's read-out t_last: r = 0 inside the refractory window, r → 1 after it.
- **R-episode (H43's claim):** r = 0 while the agent is inside the task episode the previous effective kick launched, 1 after it ends. The refractory time is the launched episode length L (a random variable per kick).
- **R-time (habituation rival):** r(δ) = 1 − a·e^{−δ/τ}, a clock that runs regardless of what the agent is doing.
- **R-null (no refractoriness):** r ≡ 1; every kick has the same gain given the agent's current state (state dependence only: a busy agent may respond differently from an idle one, but not because of an earlier kick).
- **R-batch (read-out absorption):** two kicks that arrive before the same receiving call are read together (one context assembly), so the second can only add through dose. This is mechanical (DQ1 visibility rule) and is the δ = 0 limit of any refractory curve; H16 found a saturating dose law (one kick is what matters).

**Rivals that mimic refractoriness** (built into the nulls):
- **Frailty / selection on non-response:** the nudger re-fires on agents that did not respond (H04), so second kicks land on agents selected for being stuck. Matching on the past (state, idle age, response to the first kick) balances this between arms; the synthetic frailty null tests that it does.
- **Future conditioning:** controls that must stay kick-free afterwards fake an effect (H39 synthetic lesson). Controls are eligible on past information only; both arms are cut at the next kick.

## Data scheme (`scheme/`)
`scheme/build.py` builds `data/processed/H43-kick-refractory-window/` from shared tables only (non-holdout rows; `holdout_mask` re-checked):
- **Calls (the clock):** one row per model call from `call_windows` (non-summary calls; `ctx_mode != "summary"`), with `t_call`, `t_end`, kind, talk flag, `gap_kind`, first-of-day flag, unit id (`period_units`; #51's unit 51g split at NE43 = 2026-08-21, which `period_units` predates).
  - **Idle call:** kind ∈ {pause, wait} and not talking. **Active call:** any other non-summary call.
  - **Idle at read:** the previous call of the same agent-day is idle, or ≥ 180 s passed between its end and this call's start.
  - **Idle age:** time since the end of the agent's last active call.
- **Kicks, read at the receiving call:** from `context_ledger_items` (each (message, recipient) pair is assigned to the first call that could see it). Per call, counts of new items by class:
  - **N** nudge naming the recipient (`kind == "nudge"` & `ment`);
  - **H** human message (any; `H_men` = naming the recipient, reported where powered);
  - **A** agent message naming the recipient (@-mention).
  - Pause/resume bookends are not kicks. **Kick spacing (read-out)** δ = t_call(this receiving call) − t_call(the previous receiving call with a class-c kick); δ = 0 means two kicks read by the same call (batched).
- **Behavior states:** shared `states_min` (`lump4`: work / chat / idle / consolidate; `in_span` trimmed), for the **launched episode** and the swarm-activity covariate.
- **Writes:** DQ4 work ledger: agent-attributed, turn-backed, non-automated commits (`work_commits`) plus successful API writes (`work_api_writes`). Regime III only in practice (regime I has ~3k writes in total); write outcomes are reported only where a period has ≥ 1 write per agent-day.
- **Output:** `calls.parquet` (per call: ids, times as epoch s, kind code, flags, kick counts by class), `writes.parquet` (agent, t), per-period `G<NN>/results.json`, `native/` (NE43, G38, G04), `synthetic/`, `confirm_dryrun/`; `_provenance.json`. Budget ≤ 200 MB.
- **Regimes covered:** I, II, III; all non-holdout goal periods with ledger calls (35 periods). Nudges exist only from 2026-02-13 (G30 onward); human messages are dense only in regime I (G03–G08) and #51.

## Observables
All per goal period (units of `period_units` are matching strata inside the period; no cross-unit comparisons), per kick class c ∈ {N, H, A}.

**Outcomes, measured from the receiving call** (time 0 = its `t_call`; both arms cut at the next receiving call carrying a kick of class c, N or H; agent-day end censors):
- **O1 escape** (idle-at-read calls only): a *sustained* active run (≥ 3 consecutive active calls, so a glance does not count) starts within W = 15 min. Discrete-time hazard on 1-min bins, F(W) = 1 − Π(1 − h_j). Also the **dead time** (time to the run start) for escapers.
- **O2 next action = talk:** the agent talks (any call with the talk flag) within 5 min.
- **O3 next write:** a write event within 30 min (regime III only).

**Primers and the first-kick effect E1.** A primer is a receiving call with ≥ 1 class-c kick and no N/H/A kick read in the previous 30 min (H39's lever-episode quiet rule). Controls: calls with no N/H/A kick read now or in the previous 30 min. E1 = F_kick − F_ctrl (matched).

**Second kicks and E2(δ).** A second kick is the next receiving call with a class-c kick after a primer (same agent-day, within 240 min), at spacing δ. Controls: calls after a primer with no class-c kick yet and no kick at this call, in the same δ bin. E2(δ) = F_kick − F_ctrl. δ bins (min): (0, 2], (2, 5], (5, 15], (15, 30], (30, 60], (60, 120], (120, 240]. **Batched** (δ = 0): primers carrying ≥ 2 class-c kicks vs exactly 1 (marginal effect of the second kick read at once).

**Matching (past information only).** Exact strata: unit × idle-at-read × idle-age bin (< 3, 3–10, 10–30, ≥ 30 min) or active-run age bin (< 3, 3–15, ≥ 15 min) × talked in the previous 5 min × day third × swarm-activity tercile (share of other present agents non-idle in the previous minute) × any other-class kick read in the previous 10 min; for E2 also × δ bin × primer effective (O1 escape after the primer, known by now) × launched-episode status. Same agent when the stratum has ≥ 5 controls, else pooled within the unit. Up to 10 controls per treated call, drawn with replacement, total weight 1 per treated call.

**Refractory ratio** R(δ) = E2(δ) / E1, with E1 restricted to the same read-state (idle-at-read for O1). Reported only where E1 > 0 with its day-bootstrap 95% CI excluding 0; otherwise "no first-kick effect: refractoriness undefined".

**Recovery fit.** E2(δ) = E1·(1 − a·e^{−δ/τ}) by weighted least squares on the bins (a ∈ [0, 1], τ ∈ [0.5, 480] min); **refractory window** δ½ = τ ln(2a) if a > ½, else "< shortest populated bin". Bootstrap: 300 day-block resamples (E1 and E2 from the same draw), refit per draw.

**Launched episode** (behavior states). For an effective primer read while idle: the episode starts at the escape minute and runs over non-idle `lump4` minutes, bridging idle gaps < 3 min, until the first idle run ≥ 3 min (or span end). L̃ = median L per class and period. At a second kick, the recipient is **in-episode** (still inside it), **post-episode** (it ended) or **never escaped**.

**Episode test.** At matched δ: R for post-episode second kicks (O1, idle again) vs in-episode second kicks (O2/O3; E1 counterpart = primers read while active).

**Operator rule.** Minimum spacing per class = upper 80% bootstrap bound of δ½ (or the nudger's 15-min floor if δ½ is below it). **Reliability:** split-half (odd vs even days) agreement within one δ bin; bootstrap share of draws in the modal δ½ bin; synthetic recovery rate.

## Null / baseline
- **N1 synthetic nulls (axis F):** R-null and a frailty null (agent-day heterogeneity in responsiveness, nudger re-firing on non-responders, no refractoriness) through the identical estimator; R(δ) must stay ≈ 1 (CI including 1 in ≥ 90% of bins × replicates).
- **N2 placebo kicks:** pseudo-second-kicks at control calls drawn with the real δ and stratum mix; E2_placebo ≈ 0 gives the bias floor of E2 (200 draws).
- **N3 day-block bootstrap** (300 draws) for every CI.
- **Rivals:** R-null (state dependence only), R-time (habituation clock), R-batch (read-out absorption only), frailty/selection.

## Prediction
*Written 2026-10-04 (UTC), before running any analysis on real data and before the synthetic validation.* What had been seen: the round-1 cards of H04, H16, H39, H08; structural counts only (kick-receiving calls per class per period: N 970 in G51, 120 in G38, 71 in G41, ≤ 45 elsewhere; no call ever receives two nudges; nudge re-fire spacing has a hard floor at ~15 min, median ~30 min; mention and human-message spacings have medians of 0.4–4.5 min; write coverage by regime). No H43 outcome had been computed.

- **P1 (a window exists).** For every class with E1 > 0 in a powered period (≥ 20 primers, ≥ 20 second kicks), R at the shortest populated non-batched δ bin ≤ 0.5 with the 95% CI upper bound < 1, and R rises with δ (bin-level Spearman > 0) to ≥ 0.7 by the longest populated bin. Nudges: shortest bin (15, 30] min (nudger floor). Counts against: R CI including 1 at the shortest bin (no refractoriness at the resolution we have).
- **P2 (window ≈ launched episode).** δ½ within a factor 2 of L̃ (same class and period). Across powered class × period cells (if ≥ 4), δ½ and L̃ are positively rank-correlated. Counts against: δ½ outside [L̃/2, 2L̃], or a window when L̃ is short (time-locked).
- **P3 (episode-locked, not time-locked).** At matched δ, post-episode second kicks have R ≥ 0.7 and in-episode second kicks R ≤ 0.3. Counts against: R the same in and after the episode (time-locked habituation) or ≈ 1 in both (no refractoriness).
- **P4 (batched limit).** A second kick read in the same call adds ≤ 0.3 × E1 (mentions, human messages; nudges are never batched). Expected from R-batch and H16's saturating dose; it does not by itself support H43.
- **P5 (synthetic, axis F).** At G51 scale the estimator recovers a planted R-time window (τ = 30 min) with δ½ within a factor 1.5 in ≥ 80% of replicates, separates R-episode from R-time with the episode test, and gives R CIs including 1 in ≥ 90% of bins under R-null and the frailty null.
- **P6 (NE43, native, nudges).** Before 08-21, the nudge curve satisfies P1 (R(15–30 min) ≤ 0.5). The per-kick curve predicts the swarm-level nudger-off change in sustained escape per idle-at-read call: the refractory accounting (re-fires contribute E2(δ)) is closer to the observed day-matched change than the additive accounting (every nudge contributes E1). Expectation stated in advance: both predictions are far smaller than H39's −13% idle-escape drop, i.e. the nudger's direct per-kick effects do not explain the swarm drop.
- **P7 (NE43, native, invariance).** The mention (A) curve on O2 is unchanged across 08-21 (|ΔR| < 0.3 in every powered bin): refractoriness is a property of the recipient, not of the nudger.
- **P8 (G38, native, gates).** Directed kicks (N or A or H naming the agent) read at a pause gate within L̃ of the agent's previous effective kick raise sustained escape by ≤ 0.5 × the effect at gates with no effective kick in the previous 60 min (fresh gates). Batched dose 2+ adds ≤ 0.3 × the dose-1 effect.
- **P9 (G04, native, human trains).** Human messages have E1 > 0 on O1 and O2. R ≤ 0.3 at δ ≤ 5 min and ≥ 0.7 for δ > 30 min; δ½ within a factor 2 of L̃.
- **P10 (operator rule).** Each class with a measurable window yields a minimum spacing whose split-half estimates agree within one δ bin, with ≥ 60% of bootstrap draws in the modal bin.
- **Replication layer (templated):** in each eligible period, every powered class with E1 > 0 has R(short) < R(long), and δ½ within a factor 2 of L̃.

**What would count against H43 as a whole:** R ≈ 1 at the shortest observable spacing for every powered class (second kicks work as well as first ones), or windows that do not track the launched episode (P2 and P3 both failing).

### Amendments (2026-10-04, before any real-data outcome was computed)
- **A1 (from the synthetic validation).** The first estimator failed its own nulls, so five changes were made:
  - **Effect scale:** a pooled log hazard ratio over the window (lnHR; the risk difference is still reported). Second nudges land on older, slower idle spells than primers, and a risk-difference ratio drifts with the baseline (null R ≈ 0.6).
  - **Controls:** every call in the treated call's stratum, the treated call's weight 1 spread over all of them, with a two-way day bootstrap (control rows carry their own day). Ten random draws from thin strata gave anti-conservative CIs.
  - **E1 reference:** standardized to each second-kick set's stratum mix (read state × idle/active age bin).
  - **Outcomes separated by read state:** O1 on idle-at-read rows only; O2, O2c and O3 on active-at-read rows only. Mixing read states gave mentions a spurious null R ≈ 0.4–0.7, because for an idle recipient "talk" requires escaping first.
  - **Planted clocks** are class-specific: habituation to the same kick type.
  - **New outcome O2c:** the receiving call itself talks (the immediate next action; W = 1 call).
- **A2 (from structural counts in G04).** Human chat in G04 is continuous: a 30-min quiet rule leaves 32 primers, only 2% of calls are idle, and there are 7 idle quiet controls. The G04 native test therefore uses:
  - a 5-min quiet rule (265 primers);
  - outcomes O2 and O2c (O1 is not estimable there).

  **P9 amended:** E1 > 0 on O2/O2c; R ≤ 0.3 at δ ≤ 2 min and R ≥ 0.7 for δ in (5, 30] min. There are almost no second messages beyond 30 min.
- **A3 (P8 operationalized).** An agent at a pause gate is idle, so its launched episode has already ended, and "a kick within L̃ of the previous effective kick" cannot land at a gate. P8 is therefore tested as: directed kicks (class D = nudge, named human message or @-mention) read at a gate after an effective directed primer whose episode has ended (status `post`, δ ≤ 120 min), against fresh gates (E1). This tests whether refractoriness outlasts the episode, which is R-time against R-episode. The batched D dose is unchanged.
- **A5 (P3 operationalized, from the synthetic).** Busy recipients after an *ended* launched episode are rare, so P3's in-episode vs post-episode contrast is scored on two pairs, both at matched spacing (pooled δ ≤ 240 min):
  - **busy recipients:** `in` (inside the episode a primer launched) vs `act` (primer read while busy, so no launched episode). In the synthetic this pair separates R-episode (in ≈ 0.2, act ≈ 1), R-time (both low) and the null (both ≈ 1).
  - **idle recipients:** `post` vs `noeff`, on O1.

  P3 passes if R_in ≤ 0.3 and R_act ≥ 0.7 (mentions, the identifiable class).
- **A4 (power, from the synthetic).** Nudge R per δ bin is not resolvable at G51's size (302 primers, 196 second nudges): planted windows are recovered only for mentions (thousands of second kicks). Nudge results are therefore read as a pooled R over δ ∈ (15, 60] min, against the null band from the synthetic.

## Synthetic validation (axis F)
`analysis/synthetic.py` simulates a call-level kicked renewal agent.
- **Agent:** busy-loop task episodes (lognormal, median 12 min) alternate with PAUSE chains (median 4 min). Gate escape is logistic with aging (H16), plus β_c for kicks read in the last 15 min. A kick read by a busy agent raises the chance that this call talks by γ_c.
- **Kick schedules, at village sampling:**
  - nudges come from a policy with the real floor: idle ≥ 10 min, ≥ 15 min apart, 0.012/min;
  - mentions and human messages replay real G51 (or G38) receipt times and counts from a random real agent-day;
  - a replay mode re-uses real G51 nudge times.
- **Planted variants:** null; `time` (clock from the last effective kick of the class, τ = 30 min); `time_any` (habituation, every kick of the class resets a τ = 30 min clock); `episode` (r = 0 inside an episode launched by an effective kick); `frailty` (agent-day responsiveness 0.15 or 1.85, baseline shift, nudger re-firing on non-responders).
- **Runs:** 64 runs (G51 scale × 6, G38 × 4, a big 4×-G51 scale × 3, replay × 2), through the identical estimator (`h43lib.analyze_class`).
- **Outputs:** `data/processed/H43-kick-refractory-window/synthetic/synthetic_results.json` and `synthetic_summary.json`; figure `figures/synthetic_validation.pdf`.

**Results (2026-10-04, before any real-data run).** Medians over replicates; "size" is the share of bins (≥ 10 second kicks) whose 95% CI for R excludes 1 under a no-refractoriness world.

| Check | Mentions (A, O2, busy) | Nudges (N, O1, idle) | Human (H) |
| --- | --- | --- | --- |
| E1 detected (G51 scale) | 6/6 | 6/6 | 0/6 (too few primers) |
| Size, null (G51 / big) | 0.07 / 0.06 | 0.00 / 0.07 | – |
| Size, frailty null (G51 / big) | 0.16 / 0.06 | 0.15 / 0.13 | – |
| Null R by spacing | 1.08, 1.11, 1.22, 1.23, 0.92 (0–2 … 30–60 min) | R(15–60) 0.77 (range 0.53–1.10) | – |
| Planted habituation clock (truth: R rises from ~0 to 1; δ½ ≈ 18 min) | −0.14, 0.11, 0.49, 0.69, 1.11; δ½ 15.4 min; within ×1.5 of truth in 2/6 (G51), 2/3 (big); CI covers truth 6/6 | R(15–60) 0.44 (range −0.23–0.89); δ½ 26 min, CI covers truth 4/6 | not identifiable |
| Episode test: R in-episode vs busy without a launched episode | episode lock 0.19 vs 1.04; clock 0.31 vs 0.04; null 1.20 vs 0.92 | – (nudges reach idle agents) | – |
| Frailty (selection on non-response) | R biased *up* (median 1.2–1.6) | short bins biased down (R(0–15) 0.44) | – |
| G38 scale | size 0.30; nothing resolvable | nothing resolvable | – |

What this means for the real-data reading:
- **Mention curves are identifiable at G51 size.**
  - A habituation clock gives R ≈ 0 at δ ≤ 5 min, rising to 1 by ~30–60 min.
  - The **episode test separates the three worlds:**
    - R-episode: in-episode R ≈ 0.2, busy-without-episode R ≈ 1;
    - R-time: both low;
    - null: both ≈ 1.
  - δ½ is recovered to within a factor ~1.5–2 (P5's ×1.5 in ≥ 80% is **not met**: 33% at G51, 67% at 4×).
- **Nudge curves are at the edge of identifiability.**
  - Per-bin R is uninformative.
  - Pooled R(15–60) has a null band of about 0.5–1.1, so only a real value below ~0.5 counts as refractoriness. The planted clock gives 0.44, i.e. a coin flip at G51 size, and the synthetic G51 has ~2× the real nudge count.
  - Frailty can push the rare shortest nudge bins down, so R(0–15) for nudges is not interpreted.
- **Human-message curves are not identifiable at G51 size** (primers ≈ 100–250 per period); G04's 5-min-quiet design is the only human test with power, and it is read as descriptive if E1 fails.
- **Null coverage:** P5 asked for CIs including 1 in ≥ 90% of null and frailty bins. Met for the null (93–100%); missed for frailty (84–85% at G51 scale). Read single-bin rejections with that size in mind (~0.15).
- **P5 verdict: mixed.** Nulls are clean, the episode test and mention windows are recovered, but window recovery within ×1.5 and frailty coverage miss their thresholds.

## Candidate goal periods
- **Replication:** all 35 non-holdout goal periods with ledger calls (G02–G08, G10–G13, G16–G21, G23–G27, G30, G31, G33, G35–G42, G44, G51 non-holdout days). Expected powered cells: A in most periods; H in G03–G08 and G51; N in G51 (and perhaps G38, G41).
- **Native:** NE43 (G51 split at 08-21), G38 (17 days, pause gates), G04 (units 4a and 4c).
- **Not used:** the locked holdout (#1, #9, #14, #15, #22, #28, #29, #32, #34, #43, #45–#50, NE12, NE21+NE23, NE30, the #51 tail from 09-07).
- **Exceptions to "one model per period":** (c) the NE43 tests compare the two sides of the switch inside #51. The recovery function r(δ) is fitted per period; cross-period comparisons are of fitted δ½ only.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness". Scored after round 1 (2026-10-04).
**Rival models:** R-null (state dependence only), R-time (habituation clock), R-batch (read-out absorption), frailty / selection on non-response.
**Locked holdout used for confirmation:** none. `analysis/confirm.py` (C1–C5 on the #51 tail, #45–#50 and the regime-I holdout periods #1, #9, #14, #15) is written and dry-run on stand-ins; **not run**.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Kicks are timed at the DQ1 receiving call (`context_ledger_items`), outcomes come from `call_windows` and the work ledger, and episodes from shared `states_min`; assumptions listed. Not invariant: "idle" means pause gates in regime III and wait calls or schedule gaps in regime I, and the nudge first-kick effect flips with the escape definition (sustained run: none; any activity: ×1.75) |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Past-only matching with both arms cut at the next kick (sequential ignorability, untestable). Aging is handled by idle-age strata, not a Markov fit. Call starts are estimated for non-Gemini agents (~10% of items one call off), which blurs "same call" vs "next call" at δ < 1–2 min. Within-period stationarity not tested |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | The refractory-window model loses to R-null everywhere. The descriptive "shallow dip" beats R = 1 for mentions (pooled 0.78 [0.67, 0.89]; G51 0.79 [0.64, 0.94]; split halves 0.77 / 0.83). Two-way day-block bootstrap throughout; no held-out-day prediction |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | H43's signatures fail: R ≈ 0 inside the window (P1), window ≈ launched episode (P2), episode lock (P3), human trains (P9b). Only P4 (batched second kick ≈ 0) and P7 (invariance) hold, and neither is specific to H43 |
| E interventional | predicts the change across a natural experiment | 1 | NE43: the per-kick estimates correctly predicted that losing the nudger's direct effects would barely move swarm escape (−0.5% predicted; observed −17%, at the edge of the placebo band). The mention curve is unchanged across the switch. The refractory-vs-additive contrast went the predicted way for the opposite reason (re-fires add *more*) |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Mention windows are recovered at G51 size (δ½ 15 vs 18 min; within ×1.5 in 2/6), and the episode test separates R-episode, R-time and null. Null size 0.07; frailty size 0.15. Nudge windows are marginal and human and G38-scale windows not identifiable (P5 mixed). The first estimator failed its nulls and was fixed before real data (A1) |
| G ground truth | agrees with known structure | 1 | Agrees with H16 (one kick per read is what matters: batched R 0.18–0.37), H39 (nudge escape ×1.5 once glances count; mentions steer, not activate) and DQ1 (78–96% of escapers start at the receiving call itself) |
| H comparative | beats the named rivals | 1 | R-null beats R-episode and R-time for every powered class. R-batch is the only refractoriness supported. Frailty is excluded for mentions (it would push R *up*), not for the nudge facilitation |
| I transfer | holds in other same-mode periods, including the holdout | 1 | The mention dip is consistent across 15 periods (I² ≈ 0, wide CIs). "No window" holds in regime I (G04 humans) and III (G51 mentions, nudges). Holdout not used |

## Results by goal period
Replication verdicts are templated (card, "Replication layer"): a testable class needs ≥ 20 primers and ≥ 20 second kicks in its primary read state and E1 > 0. It passes only if R(short) < R(long) and δ½ lies in [L̃/2, 2L̃]. 12 class × period cells were testable (mentions in 11 periods, human messages in G51); none passed. Native folders carry their own predictions.

| Period | Role | Verdict | Key numbers (lnHR effects; R = E2/E1) |
| --- | --- | --- | --- |
| [G02](goalperiod-subhypotheses/G02/README.md) | replication | descriptive | no testable class (primers: A 5) |
| [G03](goalperiod-subhypotheses/G03/README.md) | replication | descriptive | no testable class (primers: H 1, A 2) |
| [G04](goalperiod-subhypotheses/G04/README.md) | native | failed | human E1 (reply) 0.73 [0.33, 0.94]; R(δ ≤ 2 min) 1.46 [0.78, 2.51]; R(5–30) 0.60; δ½ = 0 vs L̃ 24 min |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | descriptive | no testable class |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | descriptive | no testable class (primers: H 23, A 18) |
| [G07](goalperiod-subhypotheses/G07/README.md) | replication | descriptive | no testable class (primers: H 1, A 2) |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | failed | A: E1 0.29, R(0–15) 1.24, δ½ 0 vs L̃ 12 |
| [G10](goalperiod-subhypotheses/G10/README.md) | replication | descriptive | no testable class (primers: H 15, A 9) |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | descriptive | no testable class (primers: H 10, A 35) |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication | descriptive | no testable class (primers: A 25) |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | descriptive | no testable class (primers: H 29, A 45) |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | descriptive | no testable class (primers: H 4, A 33) |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | descriptive | no testable class (primers: H 15, A 28) |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | descriptive | no testable class (primers: H 9, A 85) |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | descriptive | no testable class (primers: H 5, A 107) |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | descriptive | no testable class (primers: H 12, A 132) |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | descriptive | no testable class (primers: A 59) |
| [G23](goalperiod-subhypotheses/G23/README.md) | replication | failed | A: E1 0.35, R(0–15) 1.19, δ½ 0 vs L̃ 14 |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | failed | A: E1 0.62, R(0–15) 0.59, δ½ 3 vs L̃ 44 |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | descriptive | no testable class (primers: H 1, A 51) |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | descriptive | no testable class (primers: H 5, A 51) |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | failed | A: E1 0.65, R(0–15) 0.48, δ½ 88 vs L̃ 5 |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | descriptive | no testable class (primers: H 9, A 83) |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | failed | A: E1 0.68, R(0–15) 0.04, δ½ 333 vs L̃ 14 |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | descriptive | no testable class (primers: A 32) |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | descriptive | no testable class (primers: H 4, A 111) |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | failed | A: E1 0.48, R(0–15) 0.64, δ½ 2 vs L̃ 32 |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | descriptive | no testable class (primers: N 5, A 42) |
| [G38](goalperiod-subhypotheses/G38/README.md) | native | mixed | round 2 (after-PAUSE wakes): fresh directed reads 26/26 escape vs re-kicked 0.78 (baseline 0.49–0.53); R_w 0.22 [0.05, 0.39] (ceiling, post hoc prior). Round 1: untestable (8 re-kicked) |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | descriptive | no testable class (primers: N 1, H 7, A 106) |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | descriptive | no testable class (primers: N 2, A 78) |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | failed | A: E1 0.73, R(0–15) 0.35, δ½ 7 vs L̃ 18 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | failed | A: E1 0.59, R(0–15) 1.27, δ½ 0 vs L̃ 56 |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | failed | A: E1 0.59, R(0–15) 0.35, δ½ 2 vs L̃ 18 |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication | failed | H: E1 0.62, R(0–15) 0.49, δ½ 133 vs L̃ 31; A: E1 0.74, R(0–15) 0.76, δ½ 0 vs L̃ 20 |
| [NE43](goalperiod-subhypotheses/NE43/README.md) | native | failed | nudge E1 (sustained) 0.07 [−0.13, 0.27]; post hoc R(15–60) = 1.28 [0.66, 1.94]; switch-off −17% (placebo band −19% to +10%), per-kick prediction −0.5%; mention curve invariant |

## Results
### Exploratory round 1 (2026-10-04; non-holdout only)
- **Scripts:**
  - `scheme/build.py`: calls and writes;
  - `analysis/h43lib.py`: the estimator;
  - `analysis/synthetic.py` and `synthetic_summary.py`: synthetic validation;
  - `analysis/run_period.py`: replication;
  - `analysis/run_native.py`: NE43, G38, G04;
  - `analysis/rule.py`: the operator rule and its reliability;
  - `analysis/summarize.py`: cross-period meta-analysis;
  - `analysis/figures.py`;
  - `analysis/write_period_folders.py`;
  - `analysis/confirm.py`.
- **Numbers:** `data/processed/H43-kick-refractory-window/`: `G<NN>/results.json`, `native/{NE43,G38,G04}.json`, `rule.json`, `summary.json`, `synthetic/`, `confirm_dryrun/` (33 MB).
- **Figures:**
  - `figures/summary_obs.pdf`: R vs read-out spacing per class, and mention R per period;
  - `figures/cross_period.pdf`;
  - `figures/synthetic_validation.pdf`.

### What a second kick does
Effects are pooled log hazard ratios (lnHR) over the outcome window; R = E2/E1 (second kick vs post-primer calls without one, at the same spacing; first kick vs matched quiet calls).

| Kick class (best setting) | First-kick effect E1 | Same call (batched) | δ ≤ 15 min | 15–60 min | 60–240 min | Launched episode L̃ |
| --- | --- | --- | --- | --- | --- | --- |
| @-mention to a busy agent, reply at the receiving call (G51) | 1.44 [1.27, 1.57] (reply 16% vs 4%) | 0.18 [−0.16, 0.50] | 0.79 [0.64, 0.94] | 0.81 [0.61, 1.05] | 0.97 [0.64, 1.36] | 20 min |
| same, talks within 5 min (G51) | 0.74 [0.62, 0.84] | 0.31 [−0.13, 0.79] | 0.76 [0.60, 1.00] | 0.92 [0.64, 1.33] | 0.89 [0.43, 1.40] | 20 min |
| mentions pooled over periods (reply; random effects) | – | – | 0.78 [0.67, 0.89] (k = 15) | 0.87 [0.66, 1.07] (k = 9) | – | – |
| human message, reply (G04, 5-min quiet) | 0.73 [0.38, 0.98] | 0.40 [−0.22, 1.35] | 1.14 [0.81, 1.85]; δ ≤ 2: 1.46 | (5–30) 0.60 [0.27, 1.64] | – | 24 min |
| nudge to an idle agent, any activity (G51 before 08-21; post hoc O1a) | 0.56 [0.36, 0.72] (×1.75) | never batched | – (floor ~15 min) | 1.28 [0.69, 1.98] | 1.09 [0.55, 1.93] | 7 min |
| nudge, sustained work (pre-registered O1) | 0.07 [−0.19, 0.28] | – | – | E2 0.45 [−0.04, 0.94] | E2 0.36 [−0.06, 0.93] | 7 min |

- **No window.**
  - The recovery fit gives δ½ = 0 for every class with E1 > 0: the dip never reaches half depth.
  - The bootstrap puts δ½ below 2 min (the shortest bin, i.e. within one read-out) in 98–100% of draws for mentions and humans, and in 77% for nudges.
  - The templated replication test therefore fails in all 12 testable cells: R does not rise from a low value, and δ½ is nowhere near L̃ (5–56 min).
- **The episode does not gate the response (P3 fails).** Busy recipients inside the episode a primer launched have R = 0.65–0.69 (G51, O2/O2c), against 0.81–0.84 for busy recipients without a launched episode. In the synthetic, an episode lock gives 0.2 vs 1.0. A small episode-related reduction may exist; refractoriness does not.
- **The read-out is the refractory unit (P4 holds).** Two mentions read by the same call act almost like one: R = 0.18 on the reply, 0.31 on talk within 5 min. This is H16's saturating dose seen from the ledger. Everything that arrives before the recipient's next model call is one kick.
- **Nudges: glance, not work; re-fires do not lose effect.**
  - A first nudge after a 30-min quiet spell raises "any activity within 15 min" ×1.75 (H39's ×1.5) but not a sustained run of ≥ 3 active calls (lnHR 0.07, n.s.). Of 259 idle nudged agents, 42% started sustained work within 15 min, against 38% of matched controls.
  - Re-fires 15–240 min later keep the glance effect (R 1.09–1.28) and show more sustained escape than first nudges (E2 0.36–0.45 vs E1 0.07; status "no effect yet" R = 4.3 [1.2, 19]). Read this as facilitation **or** as selection by the nudger's text trigger, which matching cannot see (frailty biased short nudge bins *down* in the synthetic, so frailty does not explain it).
- **Dead time is read-out (post hoc).** From the receiving call, 78–96% of escapers start at that call (median 0 min). Nudges wait a median 122 s (q90 356 s) in the inbox until the agent's next call. H04's ~5-min dead time is mostly this read-out delay plus a low response rate, not a slow reaction (cross-note for H04, H08, H50).

### NE43 (native)
The nudger switch-off coincides with a −17% [−25, −9] change in sustained escapes per idle minute (day-matched 11 vs 11 days). That is at the edge of the within-#51 placebo band (−19% to +10%). The per-kick estimates predict only −0.2% (additive) to −0.5% (refractory accounting): the nudger's direct effects explain 1–6% of the change. The rest comes with the room change (08-24), roster growth and the loss of the daily bookends. The mention curve is the same on both sides (P7).

### Operator rule (deliverable)
**Space kicks by one read-out, not by an episode.**
- A kick that lands before the recipient's next model call (during its PAUSE, or in the same chat-mode cycle) adds little, about 20–40% of a fresh kick. Deliver it later or merge it into the first message.
- A kick read by a later call works about as well as the first: 80% for mentions within 15 min, 100% or more for human messages and nudge re-fires. No minimum spacing beyond that is supported at any measured spacing (1 min to 4 h).
- The nudger's 15-min floor is already past any refractoriness. What limits nudges is that they produce glances rather than sustained work, not that re-fires are wasted.

| Kick type | Minimum spacing (upper 80% bound of δ½) | Reliability |
| --- | --- | --- |
| @-mention | one receiving call (δ½ = 0; p80 0–0.8 min) | bootstrap: δ½ < 2 min in 98–100% of draws; split halves R(≤ 15 min) 0.77 / 0.83 (reply), 0.93 / 0.68 (talk); batched R 0.12 / 0.16 in both halves |
| human message | one receiving call (δ½ = 0) | δ½ < 2 min in 97–99% of draws; split halves R(≤ 15) 0.97 / 1.23 (reply); talk outcome unstable (0.46 / 5.9) |
| nudge | the existing 15-min floor (δ½ ≤ 3.9 min at p80) | δ½ < 2 min in 77% of draws; split halves R(15–60) 2.16 / 0.95 (O1a). Weakest evidence: synthetic power is marginal for nudges |

### Outcome vs prediction
| Prediction | Outcome | Verdict |
| --- | --- | --- |
| P1 window exists: R(shortest) ≤ 0.5, CI < 1, rising to ≥ 0.7 | Mentions G51: R(0–2 min) 0.57–0.72, R ≈ 0.8 up to 1 h, then ≈ 1; humans R ≥ 1; nudges untestable on O1, R ≥ 1 on O1a | **failed** |
| P2 window ≈ launched episode (×2) | δ½ = 0 everywhere vs L̃ 5–56 min | **failed** |
| P3 episode-locked: R_in ≤ 0.3, R_act/post ≥ 0.7 | R_in 0.65–0.69 vs R_act 0.81–0.84 (G51 mentions) | **failed** |
| P4 batched second kick ≤ 0.3 × E1 | mentions 0.18 (reply) / 0.31 (talk); humans 0.40 (wide) | **supported** (mechanical, not specific to H43) |
| P5 synthetic recovery and clean nulls | nulls clean (size 0.07), frailty 0.15; mention windows recovered within ×2 (×1.5 in 33%); episode test separates worlds; nudge and human windows not identifiable | **mixed** |
| P6 NE43: nudge window; refractory accounting closer; both ≪ observed drop | no first-nudge effect on O1 (untestable), R(15–60) 1.28 on O1a; "refractory" closer only because re-fires add more; both predictions are 1–6% of the observed −17% | **failed** (P6a); P6b met by the letter only |
| P7 mention curve invariant across NE43 | ΔR = +0.16 / −0.16 | **supported** (low power after) |
| P8 G38 gates: re-kick R ≤ 0.5; batched ≤ 0.3 | E1 at fresh gates n.s.; 8 re-kicked gates; 12 batched | **untestable** |
| P9 G04 human trains: E1 > 0; R ≤ 0.3 at δ ≤ 2; ≥ 0.7 at 5–30 | E1 0.47 / 0.73 ✓; R(≤ 2) 1.38 / 1.46 ✗; R(5–30) 0.44 / 0.60 | **failed** (P9a ✓) |
| P10 operator rule reliable (split halves agree; ≥ 60% of draws in the modal bin) | the rule is "no window": 98–100% of draws (mentions, humans), 77% (nudges); split halves agree for mentions and the human reply | **supported** (for the null rule) |
| Replication (templated) | 0/12 testable cells pass; 10 periods failed, 23 descriptive | **failed** |

### Caveats
- **Definition sensitivity.** The nudge first-kick effect exists for "any activity" (O1a, added post hoc to reconcile with H39) and not for a sustained run (pre-registered O1). R is undefined wherever E1 ≈ 0.
- **Power.** Only mention curves are identifiable at G51 size. Human messages are testable only in G04 (5-min quiet, amended before outcomes), and nudges marginally in G51. G38 resolves nothing. Ratios of two noisy lnHRs have wide, skewed CIs; the meta-analysis weights are dominated by G51.
- **Selection.** Matching is on the past only (state, idle/active age, swarm activity, talk, other kicks, spacing bin, primer effectiveness, episode status). The nudger's text trigger is not observed, so the nudge facilitation may be selection. Frailty biased mention R *up* in the synthetic, so the shallow mention dip is, if anything, an underestimate of its depth.
- **Read-out timing.** Call starts are estimated for non-Gemini agents (~10% of items one call off, DQ1). Some "same call" vs "next call" kicks are misclassified, which pulls R(0–2 min) toward the batched value: the true short-spacing R may be closer to 1.
- **Episodes** come from minute-grid runs (`lump4`, idle gaps < 3 min bridged), not task content. A content-defined episode could gate differently.
- **Multiplicity:** 35 periods × 3 classes × 5 outcomes. Replication verdicts are templated and not independent; the inference rests on G51 mentions, the pooled meta-analysis, G04 and NE43.
- **Design choices after seeing data:** O1a (post hoc); the dead-time note (post hoc). A1–A5 were made before any real-data outcome.
- **Data bugs:** H43 does not use `activity_bins` (silently drops ~half the events; coordinator notice 2026-10-04), `outages` or `stall_minutes`, so nothing changes.

## Confirmatory plan (frozen 2026-10-04; `analysis/confirm.py`, not run)
The round-1 findings, stated as confirmable claims about held-out data:
- **C1** (#51 tail, mentions, reply at the receiving call): E1 > 0; R(0, 15] point in [0.5, 1.1] with lower CI > 0.3 (a shallow dip, not a window); R(60, 240] ≥ 0.7; δ½ < 2 min in ≥ 80% of draws.
- **C2** (#51 tail): a second mention read in the same call adds little: batched R ≤ 0.5.
- **C3** (#51 tail): no episode lock: R_in ≥ 0.4.
- **C4** (#45–#50, nudges): E1 on any activity > 0, E1 on sustained work < 0.3, re-fire R(15, 60] ≥ 0.7. n/a if < 50 idle primers.
- **C5** (regime-I holdout #1, #9, #14, #15, humans, 5-min quiet): E1 > 0 and R(0, 2] ≥ 0.7. n/a if < 50 busy primers.

"No refractory window beyond the read-out" is confirmed if C1, C2 and C4 or C5 pass, and no scored C fails.
- **Reuse:** #45 (H02) and #46–#50 (NE21+NE23, H04) were used by other confirmatory runs, with different statistics. Disclose in those cards and LOG.md before running.
- **Dry run on non-holdout stand-ins:** C1, C2, C3 and C5 pass; C4 n/a, because the stand-ins have 38 idle nudge primers. Output: `data/processed/H43-kick-refractory-window/confirm_dryrun/confirm_results.json`. The stand-ins are in-sample, so this checks only that the pipeline runs.

## Round 2 redirects
**What the direction is really after:** the unit of operator attention. Round 1 says it is the recipient's read-out (one model call), not its task episode; round 2 should confirm that on the holdout and price the k-th kick inside one read.
- **H43-R1. Run the confirmatory script.** Run `analysis/confirm.py` after commit: C1–C3 on the #51 tail, C4 nudges on #45–#50 (possibly n/a), C5 humans on #1/#9/#14/#15. Disclose holdout reuse in the H02 and H04 cards and LOG.md first.
- **H43-R2. Nudge facilitation or nudger selection?** Re-fired nudges show more sustained escape than first nudges (lnHR 0.36–0.45 vs 0.07). Test against the nudger's trigger using H35's nudge classes or text-free trigger proxies, and within-agent re-fire vs first-nudge comparisons at matched idle age.
- **H43-R3. Read-out batching as the object.** Estimate the marginal value of the k-th kick in one read. Run per-provider sensitivity using Gemini's logged starts, the ledger's `uncertain` flag and the `t_call_lo`/`t_call_hi` bounds.
- **H43-R4. Content-defined episodes and a content outcome.** Use project states or Jev behavior labels for episodes, and ask whether a second mention moves *what* the agent says (H39 O6 drift) when it no longer changes whether it talks.
- **H43-R5. Pooled gate test.** Run G38-style gate tests over all regime-III periods with partial pooling, restricted to after-PAUSE gates (49% of idle reads in G38 follow long tool calls instead).
- **H43-R6. Decompose the NE43 swarm drop.** Separate the room change (08-24), roster growth and the loss of the daily bookends (H38's day-edge drive); the nudger's direct effects explain only 1–6% of it.

## Round 2 (2026-10-05): nudger selection, the k-th kick in one read, pooled timer wakes, the NE43 drop
*Predictions, nulls and kill rules written 2026-10-05 ~04:00 UTC, before any round-2 statistic on real data. Exploratory; non-reserved days only (`holdout_mask`; #51 up to 09-04). Serves Q5 (what a kick buys, and when) and Q1 (the read-out call as the unit of coupling). Items R2, R3, R5 and R6 of the redirects. R1 (reserved data) and R4 are not run. Code: `analysis/r2lib.py`, `analysis/synthetic_r2.py`, `analysis/run_r2.py`, `analysis/estimates_r2.py`, `analysis/figure_r2.py`. Numbers: `data/processed/H43-kick-refractory-window/r2/`. Round-1 code paths are not changed.*

**What I had seen first.**
- This card's round 1; H16 round 2 (forced erasure 0.47 → 0.84 at the next timer wake; address, not dilution, +0.45; a second directed message adds about a third; per-trap frailty fakes wake-clock aging unless ln k is in the model; 45–58% of regime-III TS1r spells are consolidation latency); H50 round 2 (call-indexed profiles are biased when the outcome depends on call length); H35 rounds 1/1b (the nudger reads trap age; 1.4 bits per nudge; glances, not work); H38 round 1b (NE43 is two steps; start spread widens at the nudger stop); H59 (a ~30-call nudge tail that is likely nudger selection).
- Structural counts with no round-2 outcome:
  - Shared `idle_gates` (call clock, after an idle call): 36.5k wakes, 28.6k after a PAUSE; regime III non-reserved: G36 35, G37 250, G38 1,628, G39 67, G40 205, G41 316, G42 97, G44 429, G51 25,477.
  - G51 before 08-21, after-PAUSE wakes: 19,061, of which 557 read a nudge aimed at the agent (leading @). Of those, 186 have no nudge to the agent in the previous 240 min ("first"), 115 are re-fires inside the same trap (median wake index k 33, trap age 3.1 h, 25 min after the previous nudge) and 256 re-fires after a sustained run (new trap; median k 7, 43 min after the previous nudge). A context reset lies between the two nudges in about half of the re-fires (197 of 371).
  - **The nudger is a village-wide clock.** Successive nudges to anyone are a median 18.9 min apart (10th percentile 15.6 min; 0.3% under 1 min); minute-of-hour is flat. It sends one nudge per ~15–20 min to one agent.
  - One outcome-level count was printed during the structural pass: the kind of the wake call that reads a nudge (172 pause vs 357 active). That is the glance outcome already known from round 1 (×1.75); no sustained-escape number, first vs re-fire, was looked at.
  - Directed items per receiving call (mention, named human message or targeted nudge): G51 has 27,881 calls with one, 3,408 with two and 1,676 with three or more; regime-I periods G12, G18–G21 have 400–1,800 calls with two or more. Gemini calls carry logged starts (19–27% of calls from #24 on; 551 dose-2+ calls in G51).
  - #51 windows of the round-1 NE43 test: before = 08-06 … 08-20 (11 days), after = 08-21 … 09-04 (11 days). **Both windows come after the last bookend (08-05)**, and #focus is open on every before day. After the switch: #focus empties by 08-24 (08-21 is the only two-room day without nudges); agents join on 08-28, 09-01, 09-03 (two, NE33) and 09-04.

### R2 · Nudge facilitation or nudger selection?
**Model.** Each timer wake w of agent a in trap j is a binary escape trial (y_sus: the wake call and the next two calls are active):
logit P(y_sus) = α_a + β_k ln k + β_t ln(trap age) + θ_s + Σ_c γ_c 1[nudge read at w, class c] + nuisance,
with s ∈ {no nudge in 240 min, previous nudge in the same trap, previous nudge before the last sustained run} the *prior-nudge state* and c ∈ {first, re-fire same trap, re-fire new trap} the class of the nudge read now. θ_s absorbs "agents the nudger has already chosen are different" (selection on non-response, agent-day frailty): each re-fire is compared with un-nudged wakes in the same prior-nudge state. Nuisance: ln declared pause, hours into the day (bins), others' activity (10 min), log(1 + undirected peer items read), any other directed item read.
- **Facilitation contrast** Δ_F = γ_refire − γ_first (re-fire classes pooled; each also reported).
- **Facilitation (H43 reading):** the earlier nudge, still in the context, primes the agent; Δ_F > 0 at matched state.
- **Selection on the trigger (rival):** re-fires land on trap states where nudges work better (wake index, trap age, recent activity). Then Δ_F shrinks to 0 once the nudge effect may vary with the trigger proxies (γ × ln k, γ × ln trap age, γ × recent sustained run) or is compared within agent-day.
- **Baseline artifact (rival):** round 1 measured E1 against quiet calls and E2 against post-primer calls; the two baselines differ. Then Δ_F ≈ 0 in the unified model even without proxies.
- **Context partition (mechanism check):** facilitation through the context predicts that the re-fire advantage needs the first nudge still in the context. Re-fires with a reset between the two nudges (forced or voluntary consolidation) vs without, with the reset itself as a main effect (H16: a reset raises escape).

| # | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| R2-P1 | **No facilitation at matched state.** In G51 (before 08-21), Δ_F has a 95% day-bootstrap CI that includes 0, and |Δ_F| < 0.3 | Δ_F > 0 with CI > 0 | 0.6 |
| R2-P2 | **Trigger proxies change little.** Adding the γ × proxy interactions moves Δ_F by < 0.15 | the round-1 gap (≈ 0.3–0.4) appears only without the proxies | 0.55 |
| R2-P3 | **Agent-day fixed effects agree.** Δ_F with agent-day FE lies within 0.2 of the agent-FE value | — | 0.6 |
| R2-P4 | **No context dependence.** Re-fire advantage with a reset between nudges minus without: CI includes 0 (read only at synthetic power ≥ 0.8; else descriptive) | CI < 0 (the advantage needs the first nudge in context) | 0.5 |
| R2-P5 | Glance outcome (y_any, the wake call is active): first and re-fire nudges both > 0, Δ_F CI includes 0 (round 1: R 1.1–1.3) | — | 0.6 |

**Kill rule (R2).** If R2-P1 fails (Δ_F > 0, CI > 0) and the gap survives the proxies and agent-day FE (P2, P3 hold), the card adopts "re-fired nudges facilitate sustained escape" for #51. If Δ_F's CI includes 0 at synthetic power ≥ 0.8 for Δ_F = 0.4, round 1's re-fire advantage is withdrawn as a baseline or selection artifact. Otherwise: inconclusive.

### R3 · The k-th kick in one read
**Model.** For each receiving call with dose d (directed items newly read at that call: @-mention, named human message, nudge with the recipient as leading @):
logit P(talk at the receiving call) = α_a + u_unit + Σ_{d=1,2,3+} f_d 1[dose = d] + β_w ln(window) + β_u log(1 + undirected agent items) + β_h log(1 + undirected human items) + β_p 1[previous call talked] + day third.
- **Window** = t_call − t_call of the agent's previous call (the time over which items piled up). H50 round 2: the dose is length-biased, and talk can depend on call length, so the window term is required.
- **Marginal value of the k-th kick:** m₁ = f₁, m₂ = f₂ − f₁, m₃ = f₃₊ − f₂; **batching ratio** ρ₂ = m₂ / m₁.
- **Rows:** active-at-read calls (round-1 A1: talk outcomes only where the recipient is not idle at read); regime III also gets the timer-wake version (y_sus at after-PAUSE wakes, with the R5 nuisance).
- **Scope:** every non-reserved period with ≥ 30 receiving calls at dose ≥ 2 in the read state; per-period estimates plus DerSimonian–Laird random-effects pooling of f₁ and m₂ (exception (d) for the small periods; G51 is reported on its own).
- **Per-provider sensitivity** (G51 and pooled): S1 all calls; S2 Gemini calls with logged starts only; S3 calls whose items and the previous call's items carry no `uncertain` flag; S4 doses recounted with the call boundaries moved to `t_call_lo` and to `t_call_hi`.
- **Read-out unit check:** round-1 short-spacing ratio for mentions (second kick read by the *next* call, δ ≤ 2 min, reply at the receiving call), recomputed on Gemini recipients only with the round-1 estimator. Round 1 warned that start misplacement pulls R(0–2) toward the batched value.

| # | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| R3-P1 | **A second kick in the same read adds a third or less.** G51: ρ₂ ∈ [0, 0.5] with the upper CI < 0.8 | ρ₂ CI includes 1 (additive kicks) | 0.7 |
| R3-P2 | **Saturation continues.** m₃ ≤ m₂ (point), G51 | m₃ > m₂ with CI > 0 | 0.6 |
| R3-P3 | **Provider- and timing-robust.** ρ₂ in S2, S3 and both S4 recounts lies within 0.2 of S1 | a shift > 0.3 in S2 (Gemini) | 0.55 |
| R3-P4 | **Pooled over periods** (random effects): ρ₂ ≤ 0.5, upper CI < 1; between-period τ on m₂ small (I² < 0.5) | pooled ρ₂ CI includes 1 | 0.6 |
| R3-P5 | **The next read restores the kick.** Gemini-only R(δ ≤ 2 min) on the reply ≥ 0.7 (round 1, all agents: 0.57–0.72). Read only if the CI width ≤ 1; else inconclusive | R ≤ 0.4 with upper CI < 0.7 | 0.45 |
| R3-P6 | Timer-wake version (regime III): ρ₂ ∈ [0, 0.6] on y_sus (H16: dose 2+ adds about a third) | — | 0.6 |

**Kill rule (R3).** If ρ₂'s CI includes 1 in S1 and S2, "one read is one kick" is withdrawn for that read state. If S2 moves ρ₂ by > 0.3 from S1, the all-agent value is reported as timing-contaminated and S2 is primary.

### R5 · Pooled timer-wake test
**Design.** All regime-III non-reserved periods (G36–G42, G44, G51), after-PAUSE wakes only (shared `idle_gates`, `prev_kind == "pause"`). Classes of the wake by its directed-read history:
- **fresh:** no directed item read by the agent in the previous 60 min;
- **re-kicked:** an earlier directed read within 120 min was *effective* (a sustained run started within 15 min of it) and that run has ended (the agent is back at a timer wake); this is round-1 A3's `post` state;
- **other:** everything else (directed read within 60 min, not effective or still running).

Model: logit P(y_sus) = α_a + β_k ln k + β_t ln(trap age) + θ_class + β_fresh·D·1[fresh] + β_re·D·1[re-kicked] + β_oth·D·1[other] + nuisance (as R2), with D = a directed item read at this wake.
- **Refractory ratio at the wake:** R_w = β_re / β_fresh; difference Δ_w = β_re − β_fresh.
- **Pooling:** per-period estimates (periods with ≥ 10 re-kicked wakes with D); DerSimonian–Laird random effects on β_fresh, β_re and Δ_w; empirical-Bayes shrunk per-period values next to the raw ones. Exception (d): too little data per period outside G51; no complete pooling.

| # | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| R5-P1 | **No refractoriness at the timer wake.** Pooled Δ_w CI includes 0 and pooled R_w ≥ 0.7 | pooled R_w ≤ 0.5 with Δ_w CI < 0 | 0.65 |
| R5-P2 | β_fresh > 0 (CI > 0) pooled and in G51 (H16: +0.69 for a directed read) | — | 0.9 |
| R5-P3 | Heterogeneity is small: I² on Δ_w < 0.5 | — | 0.5 |
| R5-P4 | G38 alone (round 1: untestable, 8 re-kicked wakes) stays untestable after the after-PAUSE restriction (< 10 re-kicked wakes with D) | — | 0.7 |

**Kill rule (R5).** A pooled R_w ≤ 0.5 with Δ_w CI < 0 (at synthetic power ≥ 0.8 for R_w = 0.3) would revive a refractory window that outlasts the episode at timer wakes (R-time). A pooled Δ_w CI including 0 with R_w ≥ 0.7 extends round 1's "no window" to every regime-III period.

### R6 · Decompose the NE43 drop
Statistic: round 1's sustained escapes per idle agent-minute, R = E/M, before (08-06 … 08-20) vs after (08-21 … 09-04); observed −17.3% [−24.5, −8.8]. Exception (c): the transition is the object. Four accountings, each with a day-block bootstrap within window:
1. **Mechanical split.** E = G·p with G the idle-at-read calls and p the share of them that start a sustained run, so Δ ln R = Δ ln p + Δ ln(G/M) exactly. G/M is the read cadence (pause lengths); p is the per-read escape.
2. **Roster (shift-share).** R = Σ_a w_a r_a with w_a = M_a/M. Δ R = within-incumbent change (Σ w̄ Δr) + reweighting among incumbents (Σ r̄ Δw) + newcomers − leavers. Incumbents = agents with idle minutes on ≥ 3 days in each window.
3. **Channels (Oaxaca on incumbents' wakes).** The R6 wake model (agent FE, ln k, ln trap age, ln declared pause, hours-into-day bins, first wake of the day, others' activity, ln present agents, log(1 + undirected peer items), any directed read, nudge read, #focus room) is fitted on the before window. Explained Δ logit p̄ = Σ_j β_j,pre Δx̄_j, grouped as **nudger** (nudge reads), **room** (room indicator, peer items, present agents), **day edge** (hours into day, first wake of the day), **trap state** (k, trap age, declared pause) and **activity** (others' activity, directed reads); the rest is the unexplained within-agent step.
4. **Date profile.** Agent-FE-adjusted per-read escape and cadence by segment: S1 08-21 (nudger off, two rooms), S2 08-24 … 08-27 (one room, no new agents), S3 08-28 … 09-02 (two joins), S4 09-03 … 09-04 (three joins, NE33), each against the before window. Placebo: the same segment contrast at every 11-day split inside #51 before 08-21.
- **Bookends:** both windows come after the last bookend (08-05), so their loss enters this comparison only through a lagged effect. It is tested separately as the 08-05 step (11 days before vs after, same statistic, placebo band) and is not a component of the −17%.

| # | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| R6-P1 | **Per-read escape carries most of the drop:** Δ ln p is ≥ 50% of Δ ln R | cadence (G/M) carries > 50% | 0.5 |
| R6-P2 | **Roster growth explains < 1/3:** newcomers + reweighting < 1/3 of Δ R; S2 (before any join) already shows ≥ half the drop | the incumbent within-agent change is ≈ 0 | 0.6 |
| R6-P3 | **Named channels explain < 1/2:** nudger + room + day edge (Oaxaca) together < 1/2 of Δ logit p̄; the nudger group alone < 10% | the explained share ≥ 2/3 | 0.55 |
| R6-P4 | **The bookend step (08-05) is inside its placebo band** | outside the band, same sign as the 08-21 drop | 0.6 |
| R6-P5 | **The 08-21 change is not a clean step:** the after-window segments differ (S1 vs S2–S4), or the drop lies inside the placebo band once agent FE are applied | a single step at 08-21 of ≈ −17% in every segment, outside the band | 0.5 |

**Kill rule (R6).** No hypothesis rests on R6; it is an accounting. Where an accounting term's CI includes 0 it is reported as "not distinguishable from 0", not as explained.

### Nulls and validation plan (before any real-data round-2 statistic)
`analysis/synthetic_r2.py` on the real skeletons (rows, agents, days, reads and covariates are real; outcomes are simulated):
- **R2:** G51 before 08-21, after-PAUSE wakes, simulated sequentially inside traps (stop at the first escape; the real nudge placements at later wakes then drop out, which reproduces re-firing on non-responders). W0: nudge effect +0.3, aging −0.4 per ln k, per-trap frailty SD 1.0, no facilitation. W1: W0 + facilitation +0.5 for re-fires. W2: nudge effect falling with k (0.6 − 0.2 ln k), no facilitation (selection on the trigger proxy). Pass: size ≤ 0.10 for Δ_F in W0 and in W2 with the proxy model; power ≥ 0.8 in W1.
- **R3:** G51 active-at-read receiving calls. W0: no dose effect. W1: saturating f = (0.8, 1.07, 1.15), ρ₂ = 1/3. W2: additive, ρ₂ = 1. W3: no dose effect; talk depends on ln window (+0.5) (H50's length-bias world). W4: W1 with 10% of directed items moved to the neighbouring call (the non-Gemini start error). Pass: |bias of ρ₂| ≤ 0.15 in W1/W2, size ≤ 0.10 for f₁ and m₂ in W0 and W3; W4 reports the misassignment bias.
- **R5:** all regime-III after-PAUSE wakes. W0: β_re = β_fresh = 0.6 (no refractoriness). W1: β_re = 0.3·β_fresh. W2: W0 with agent-day responsiveness heterogeneity (directed effect × (0.3 or 1.7)), the frailty that biased mention R upward in round 1. Pass: size ≤ 0.10 for Δ_w in W0, power ≥ 0.8 in W1 (pooled); W2 reports the bias of R_w.
- **R6:** G51 wakes in both windows from the before-window fit. W0: only covariates shift (β unchanged). W1: W0 + a step of −0.2 in logit after 08-21. Pass: unexplained step within ±0.05 of truth in both.
- A statistic that fails its pass line is reported as inconclusive (dated amendment before the real run).

### Round-2 synthetic validation (run 2026-10-05 ~04:20–04:45 UTC, before any round-2 outcome statistic)
`analysis/synthetic_r2.py`; outputs `r2/synthetic/{r2,r3,r5,r6}.json`. Rejection rates are Wald tests at 5%. "seq" = sequential inside traps (re-firing on non-responders; drops ~40% of rows), "ind" = every real row kept (real counts).

| Statistic | Null world (size) | Planted world (power, estimate vs truth) | Notes |
| --- | --- | --- | --- |
| R2 Δ_F, base model | W0: 0.05 seq, 0.03 ind | W1 (+0.5): 0.23 seq, **0.52 ind**; estimate +0.38–0.46 | **W2 (effect falls with k): −0.18, size 0.13 (ind)** |
| R2 Δ_F, proxy model | W0: 0.07 / 0.05; W2: 0.02 / 0.08 | W1: 0.20 / 0.48 | the proxies remove the W2 bias |
| R2 reset partition | W0: 0.02 | W3: 0.12 seq, 0.42 ind | not powered |
| R2 SE check | analytic 0.33–0.35 vs day bootstrap 0.33–0.39 | — | analytic SE is close |
| R3 f₁, m₂ (G51) | W0: 0.05 / 0.00; W3 (window): 0.10 / 0.10 | W1: ρ₂ 0.37 (truth 0.34); W2: 1.02 (truth 1.00); power 1.00 | without the window term, W3 gives a spurious f₁ +0.21 (rejection 1.00) |
| R3 misassignment (W4) | — | f₁ 0.74 (truth 0.80), ρ₂ 0.36 (truth 0.34) | a 10% start error attenuates f₁ by ~8% and leaves ρ₂ almost unchanged |
| R5 Δ_w, G51 | W0: 0.03–0.05 | W1 (R 0.3): **0.65 seq, 0.87 ind**; Δ_w −0.35 (truth −0.42) | — |
| R5 Δ_w, pooled (DL, k = 3–4) | W0: 0.00–0.03 | W1: 0.47 seq, 0.60 ind; pooled R 0.31–0.37 | small periods add heterogeneity, not power |
| R5 frailty (W2) | Δ_w size 0.03–0.07; R_w 1.02–1.35 (W0 1.12–1.16) | — | agent-day responsiveness does not fake refractoriness |
| R6 unexplained step | W0: +0.004 (truth 0) | W1: −0.206 (truth −0.2) | passes |

### Round-2 amendments (2026-10-05 ~04:45 UTC, after the synthetic validation and structural counts, before any round-2 outcome statistic)
- **A2-1 · R5 re-kicked class made strict.** The pre-registered class covers 54–85% of wakes in every period: in regime III almost any directed read is followed by a sustained run within 15 min by chance. The primary class now requires an *isolated* effective primer (no directed read in the 30 min before it), as round-1 primers were. The loose class is a sensitivity. Per-period fits need ≥ 5 directed wakes in both the fresh and the re-kicked class (G37, G38, G41, G51 qualify).
- **A2-2 · R2 primary model is the proxy model.** Without the γ × proxy terms a k-dependent nudge effect biases Δ_F (−0.18, size 0.13); with them the size is 0.02–0.08. R2-P2 still compares the two.
- **A2-3 · R2 is underpowered for a null.** Power for Δ_F = 0.5 is 0.48–0.52 at real counts. R2-P1 is therefore read as an interval: an upper 95% bound below 0.3 excludes a re-fire advantage of the round-1 size (≈ 0.3–0.4); otherwise "inconclusive". R2-P4 (reset partition, power 0.42) is descriptive.
- **A2-4 · R5-P1 is decided on G51** (power 0.87 for R_w = 0.3). The pooled estimate (power 0.60) is reported with its per-period and shrunk values and read as descriptive where its CI includes 0.

### Round-2 results (run 2026-10-05 ~04:50–06:10 UTC; exploratory, non-reserved)
*Scripts: `analysis/run_r2.py --only r2|r3|r3p5|r5|r6`, `analysis/posthoc_r2.py` (post hoc P1–P3), `analysis/estimates_r2.py`, `analysis/figure_r2.py` → `figures/r2_summary.pdf`. Numbers: `r2/results_{r2,r3,r3p5,r5,r6}.json`, `r2/posthoc_r2.json`. CIs: day-block bootstrap (200 draws; 300 for R3-P5). Compute: one local process at a time, ≤ 2 threads; R3 took 35 min, everything else < 1 min each.*

**R2 · nudge facilitation or nudger selection** (G51 before 08-21: 19,009 after-PAUSE wakes, 182 first nudges, 212 re-fires inside the same trap, 162 re-fires after a sustained run; 34 days)

| # | Prediction | Observed | Outcome |
| --- | --- | --- | --- |
| R2-P1 | Δ_F CI includes 0, \|Δ_F\| < 0.3; interval reading (A2-3): upper bound < 0.3 | proxy model **Δ_F −0.06 [−0.84, +0.61]** (analytic SE 0.28) | **inconclusive** (A2-3): no re-fire advantage, but the interval cannot exclude one of round-1 size |
| R2-P2 | proxies move Δ_F by < 0.15 | base +0.08 [−0.54, +0.74] → proxy −0.06 (shift 0.14) | **holds** |
| R2-P3 | agent-day FE within 0.2 | −0.24 [−0.88, +0.45] (shift 0.18) | **holds** |
| R2-P4 | reset partition, descriptive | re-fire × reset between +0.30 [−0.41, +1.18]: re-fires after an erasure do no worse | descriptive; the sign is opposite to facilitation through the context |
| R2-P5 | glance: both > 0, Δ_F ∋ 0 | first +1.19 [0.48, 1.86], re-fire +1.29 [0.47, 1.94]; Δ_F +0.10 [−0.66, +0.70] | **holds** |

The re-fire classes differ sharply (proxy model, split):
- **Re-fire after a sustained run (new trap):** +1.59 [1.00, 2.17]; minus first +0.28 [−0.36, +0.85]. A nudge to an agent that has worked and stopped again works like a first nudge.
- **Re-fire inside the same unbroken trap:** −0.10 [−1.21, +0.80]; minus first **−1.42 [−2.60, −0.37]**. Raw, at matched wake index (post hoc P2): k 10–29, first nudges 0.28 escape vs 0.07 un-nudged; same-trap re-fires 0.05 vs 0.03. A second nudge into a trap that ignored the first one does almost nothing.
- **This is not identified as refractoriness.** A trap that survived a first nudge is selected for non-response (per-trap responsiveness). The synthetic W0 had frailty in the baseline only, not in the nudge response, so it cannot separate the two readings.

Post hoc P1 (why round 1 saw no first-nudge effect on sustained work): on the same wakes, with round 1's outcome (a sustained run within 15 min), first-nudged wakes escape 0.71 against 0.74 for wakes with no nudge in 4 h, the round-1 picture. With the wake index and trap age in the model the first-nudge effect is +1.05 [0.63, 1.49] (base) and +0.47 [−0.25, +1.03] (proxy). On the sustained escape at the wake it is +1.70 [1.27, 2.29] (base) and +0.99 [0.28, 1.53] (proxy). **The nudger fires into deep traps** (median k 3 for first nudges, 33 for same-trap re-fires), where the un-nudged escape is low. Round 1 matched on idle age, not wake index, so it compared nudged deep traps with shallow quiet ones. This reverses round 1's "glance, not work" at the wake. It is post hoc and model-dependent (the proxy model halves it), and it disagrees with H35 round 1b's minute-level DiD.

**R3 · the k-th kick in one read** (active-at-read receiving calls; outcome: the call talks)

| # | Prediction | Observed | Outcome |
| --- | --- | --- | --- |
| R3-P1 | G51 ρ₂ ∈ [0, 0.5], upper CI < 0.8 | f₁ +1.40 [1.30, 1.49]; m₂ +0.16 [0.01, 0.30]; **ρ₂ 0.11 [0.01, 0.21]** (22,656 / 1,931 / 629 calls at dose 1 / 2 / 3+; talk 0.04 / 0.19 / 0.24 / 0.22) | **holds** |
| R3-P2 | m₃ ≤ m₂ | m₃ −0.19 [−0.45, +0.03] | **holds** |
| R3-P3 | S2, S3, S4 within 0.2 of S1 | Gemini logged starts 0.08 [−0.10, 0.32]; calibrated starts 0.13 [0.03, 0.23]; no uncertain items 0.07 [−0.05, 0.17]; boundaries at t_call_lo 0.08 [0.01, 0.18], at t_call_hi 0.30 [0.12, 0.47] | **holds** (largest shift +0.19, t_call_hi) |
| R3-P4 | pooled ρ₂ ≤ 0.5, upper CI < 1; I² < 0.5 | 31 periods: pooled f₁ +0.35, m₂ −0.05, ρ₂ −0.15 [−0.93, +0.54]; **I² 0.95** on m₂ | **partly**: ρ₂ is small, but periods disagree; in 15 of 31 periods f₁'s CI includes 0 (talk at the call is not a read-out outcome in chat mode), and 10 of the 16 periods with f₁ > 0 have ρ₂ < 0 |
| R3-P5 | Gemini-only R(δ ≤ 2 min) ≥ 0.7 | 0.68 [0.26, 1.14] (below) | not met as worded; not contradicted |
| R3-P6 | timer-wake ρ₂ ∈ [0, 0.6] | G51 0.35 [−0.13, 0.92] (f₁ +0.47 [0.35, 0.59], m₂ +0.16); G38 −0.21 [−1.26, 1.24] | **holds** (G51; matches H16's "about a third") |

- The H50 length bias is real but small here: without the window term ρ₂ is 0.15 (vs 0.11) and f₁ 1.45 (vs 1.40).
- Gemini recipients (measured starts) respond more strongly to a first directed item (f₁ 2.26 vs 1.29) but batch the same way (ρ₂ 0.08 vs 0.13). Start misplacement does not create the batching.

**R3-P5 · the next read restores the kick** (round-1 estimator, G51 mentions, reply at the receiving call; Gemini recipients = agents 6, 22, 27, 44, whose starts are logged): Gemini R(δ ≤ 2 min) **0.68 [0.26, 1.14]** (55 second kicks; first-kick E1 2.64 [2.27, 3.17]; batched R 0.12 [−0.27, 0.61], 18 calls) against 0.75 [0.53, 0.95] for the other recipients (415). The CI width is 0.88, so the test is read: the point misses 0.7 by 0.02 and nothing counts against (the "against" line was R ≤ 0.4 with upper CI < 0.7). **Outcome: not met as worded, not contradicted.** Measured starts do not remove the shallow short-spacing dip, so round 1's caveat (start misplacement pulls R(0–2) down) is not the cause. A kick read by the next call keeps about 70% of a first kick; one read in the same call keeps about 10%.

**R5 · pooled timer-wake test** (after-PAUSE wakes; strict re-kicked class, A2-1)

| Period | directed wakes fresh / re-kicked | log OR fresh | log OR re-kicked | re-kicked − fresh | R_w |
| --- | --- | --- | --- | --- | --- |
| G51 (45 days) | 492 / 1,735 | +0.62 [0.41, 0.87] | +0.40 [0.26, 0.55] | **−0.22 [−0.47, +0.04]** | **0.64 [0.38, 1.08]** |
| G38 (17 days)* | 26 / 96 | +4.08 [3.19, 4.86] (26/26 escape) | +0.90 [0.19, 1.73] | −3.18 [−4.12, −2.23] | 0.22 [0.05, 0.39] |
| G37 (3 days)* | 7 / 29 | +2.48 [1.57, 3.44] | +0.68 [0.08, 3.07] | −1.81 [−3.25, +1.12] | 0.27 |
| G41 (5 days)* | 9 / 32 | +0.95 [−0.61, 3.47] | +0.88 [−0.08, 2.04] | −0.08 [−2.94, +2.09] | 0.92 |
| pooled (DL, k = 4)* | | +2.07 [0.20, 3.93] | +0.43 [0.29, 0.57] | −1.40 [−3.25, +0.45], I² 0.93 | 0.21 [0.09, 1.03] |

\* Post hoc: an N(0, 2.5²) prior on the three directed-read terms. Without it the small periods separate (G38: every fresh directed wake escapes) and the unpenalized pooled estimate is meaningless (−4.9, CI ±10). Loose class (pre-registered): G51 −0.22 [−0.52, +0.08], R_w 0.67.

| # | Prediction | Outcome |
| --- | --- | --- |
| R5-P1 | Δ_w CI ∋ 0 and R_w ≥ 0.7 (decided on G51, A2-4) | **partly**: Δ_w's CI includes 0, but R_w's point is 0.64; the kill line (R_w ≤ 0.5 with Δ_w < 0) is not crossed. A shallow dip at the wake, the size of round 1's mention dip (0.78) |
| R5-P2 | β_fresh > 0 (G51 and pooled) | **holds**: +0.62 [0.41, 0.87]; pooled +2.07 [0.20, 3.93] |
| R5-P3 | I² < 0.5 | **failed**: I² 0.93; G38 and G37 show large reductions, G41 and G51 small ones |
| R5-P4 | G38 stays untestable | **failed**: 96 re-kicked directed wakes; G38 shows a ceiling-limited reduction (risk difference +0.51 fresh vs +0.25 re-kicked) |

**R6 · the NE43 drop** (details in `goalperiod-subhypotheses/NE43/README.md`)

| # | Prediction | Observed | Outcome |
| --- | --- | --- | --- |
| R6-P1 | per-read escape ≥ 50% of Δ ln R | Δ ln R −0.190 [−0.300, −0.106] = cadence −0.132 [−0.262, −0.024] (69%) + per-read escape −0.058 [−0.155, +0.031] (31%) | **failed**: the drop is a cadence change |
| R6-P2 | roster < 1/3; ≥ half of the drop before any join | newcomers and leavers **+24%** of the change (they raise the rate); within incumbents 73%, reweighting 52%; 08-24…27 (no joins) −23.6% | **holds** |
| R6-P3 | nudger + room + day edge < 1/2; nudger < 10% | nudge reads 4% [1%, 8%]; room ≈ 0 (CI ±0.03, i.e. ±60% of the per-wake change); day edge ≈ 0 | **holds** (room uncertain) |
| R6-P4 | bookend step (08-05) inside its band | +4.8%, band [−18.8%, +10.4%] | **holds** |
| R6-P5 | not a clean 08-21 step | 08-21: −2.9% (cadence −4%, per read +1%); 08-24…27: −23.6% (all cadence); 08-28…09-02: −16%; 09-03…04: −15% (per read −24%, NE33 batch join); wake-model step −0.22 sits at the edge of its placebo band (1 of 13 splits more negative) | **holds** |

Post hoc P3: the cadence drop is longer declared pauses. The median declared pause rises from 240 s to 300 s on 08-21 and 08-24…27, and the share of pauses ≥ 10 min doubles in the one-room week (0.17 → 0.34; agent-FE ln pause +0.10 to +0.14).

### Findings (round 2)
1. **A re-fired nudge is not better than a first one at matched trap state.** Round 1's re-fire advantage came from different baselines. The unified wake model gives Δ_F −0.06 [−0.84, +0.61]; the interval is wide (power 0.5), so the null is not established either.
2. **What matters is whether the trap was broken in between.** A re-fire after the agent has worked again acts like a first nudge (+1.59). A re-fire into the same unbroken trap does almost nothing (−1.42 vs first). Refractoriness and selection of non-responsive traps give the same pattern here.
3. **One read is one kick, robustly, in #51.** A second directed item in the same call adds 11% of the first (ρ₂ 0.11 [0.01, 0.21]); a third adds nothing. Gemini's measured starts, the uncertain flag and both start bounds give 0.07–0.30. A kick read by the *next* call keeps about 70% (Gemini recipients 0.68 [0.26, 1.14]). At a timer wake the second item adds about a third (0.35). Outside #51 the talk-at-the-call outcome does not carry the read-out (I² 0.95).
4. **At timer wakes, a directed read after an effective primer works about two thirds as well** in #51 (R_w 0.64 [0.38, 1.08]), and much less in the long-pause period G38 (a ceiling-limited 0.22). That is a shallow dip, not a window, in the powered period.
5. **The NE43 drop is not the nudger.** It starts with the one-room week (08-24), not with the nudger stop (08-21: −3%). It is a cadence change: longer declared pauses, so fewer timer wakes per idle minute. Newcomers raise the rate, and the bookend stop (08-05) left no step.

### Impostors (round 2)
| Impostor | Relevant? | Handling | Status |
| --- | --- | --- | --- |
| Scheduler field | yes | Call clock (timer wakes, receiving calls); hours-into-day bins and others' activity in every wake model; the read window term for dose (H50); the NE43 date profile separates the day schedule from the steps | removed |
| Exogenous field | yes | The nudger's trigger: prior-nudge state, wake index, trap age, recent run and agent-day FE (R2); the nudge, room and day-edge channels named in R6 | partly (unobserved per-trap responsiveness remains for same-trap re-fires) |
| Shared model priors | partly | Agent FE everywhere; per-provider split for batching (Gemini vs calibrated starts) | removed for the claims made |
| Contemporaneous convergence | no | No copying claim; kicks are timed at the receiving call | n/a |

### Scorecard (round 2; round 1 in brackets)
A 1 [1] · B 1 [1] · C 1 [1] · D 1 [0] · E 1 [1] · F 2 [1] · G 1 [1] · H 1 [1] · I 1 [1].
- **D 1:** read-out batching predicted in advance (ρ₂ ≤ 0.5, m₃ ≤ m₂, provider-robust) holds in #51; the episode window signatures still fail.
- **E 1:** NE43 decomposed: the nudger-off day is flat, and the drop arrives with the room merge as a cadence change. This is an accounting, not a clean intervention.
- **F 2:** every round-2 estimator was validated on the real skeletons before the run; the validation changed two designs (A2-1, A2-2) and flagged R2 and the pooled R5 as underpowered.
- **H 1:** facilitation is not supported; "re-fires are better" (round 1) loses to the baseline-artifact rival; refractoriness vs selection of non-responsive traps is not separated.

### Old → new
| Number | Round 1 | Round 2 |
| --- | --- | --- |
| first nudge, sustained escape | lnHR 0.07 [−0.19, 0.28] (matched on idle age) | wake model, wake index matched: lnOR +0.99 [0.28, 1.53] (proxy), +1.70 (base); post hoc |
| re-fired vs first nudge | E2 0.36–0.45 vs E1 0.07 | Δ_F −0.06 [−0.84, +0.61]; same trap −1.42 [−2.60, −0.37]; new trap +0.28 [−0.36, +0.85] |
| second mention in the same call | R 0.18 (reply), 0.31 (talk) | ρ₂ 0.11 [0.01, 0.21] (G51); Gemini starts 0.08 |
| G38 timer wakes | 8 re-kicked: untestable | 26 fresh / 96 re-kicked directed wakes; R_w 0.22 (ceiling, post hoc prior) |
| NE43 drop | −17%, 1–6% nudger, rest "room, roster, bookends" | 69% cadence (longer pauses), from 08-24; nudger 4%; newcomers +24%; bookends 0 |

**Operator reading.** Do not stack kicks before the recipient's next call: in #51 a second directed message in the same read adds about a tenth of the first. Do not re-nudge an agent that ignored a nudge and is still in the same pause chain: it raises escape from 0.03 to about 0.05. Wait until it has worked and stopped again; then a nudge works like a first one.

**Claim that stands:** in #51, one read is one kick: a second directed item read in the same call adds 0.11 [0.01, 0.21] of the first item's effect on talking at that call, robust to measured (Gemini) starts, the uncertain flag and both start bounds (0.07–0.30), while a kick read by the next call keeps about 0.7 (Gemini recipients 0.68 [0.26, 1.14]). Excluded: nudge facilitation (Δ_F −0.06 [−0.84, +0.61], underpowered); the same-trap re-fire loss as refractoriness (not separated from selection of non-responsive traps); the first-nudge effect at the wake (post hoc, model-dependent); the pooled timer-wake and batching estimates outside #51 (I² 0.93–0.95; post hoc prior for small periods); G38's wake reduction (ceiling, post hoc prior); and the NE43 cadence decomposition (an accounting; the link from the room merge to longer pauses is not identified).

## Notes
- 2026-10-04: round 1 started. Resumed after an API session limit; the DQ1 context ledger landed in the meantime, so every kick is timed at its receiving call from the start (coordinator instruction), not as a later refinement.
- 2026-10-04: no other hypothesis's code is imported (read-only or otherwise). Shared tables only: `call_windows`, `context_ledger_items`, `period_units`, `states_min`, `calendar`, `work_commits`, `work_api_writes`, `kicks_classified` (structural counts only).
- 2026-10-04: `period_units` predates NE43, so unit 51g is split at 2026-08-21 here (51g1/51g2). Proposed for the shared rule.
- 2026-10-04: coordinator notice about `activity_bins` (join-key bug): not used by H43, no change.
- 2026-10-04, holdout disclosure: an early structural probe of `kicks_classified` printed nudge counts per goal period without filtering held-out periods (counts of nudge messages for #32, #34, #47–#50; no states, outcomes or timing). No held-out outcome was computed; every exploratory loader asserts non-holdout days.
