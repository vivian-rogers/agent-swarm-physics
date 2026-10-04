# H43: Kicks leave a refractory window

**Status:** exploratory round 1 done (2026-10-04): no refractory window. Second kicks read by a later call keep 80–130% of the first's effect; only kicks read in the same call are wasted. Holdout not run.
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
| [G38](goalperiod-subhypotheses/G38/README.md) | native | descriptive | native: directed E1 at fresh gates 0.28 (n.s.), 8 re-kicked gates → untestable; replication: mention R(0–15) 1.80 [0.46, 13.7] |
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

## Notes
- 2026-10-04: round 1 started. Resumed after an API session limit; the DQ1 context ledger landed in the meantime, so every kick is timed at its receiving call from the start (coordinator instruction), not as a later refinement.
- 2026-10-04: no other hypothesis's code is imported (read-only or otherwise). Shared tables only: `call_windows`, `context_ledger_items`, `period_units`, `states_min`, `calendar`, `work_commits`, `work_api_writes`, `kicks_classified` (structural counts only).
- 2026-10-04: `period_units` predates NE43, so unit 51g is split at 2026-08-21 here (51g1/51g2). Proposed for the shared rule.
- 2026-10-04: coordinator notice about `activity_bins` (join-key bug): not used by H43, no change.
- 2026-10-04, holdout disclosure: an early structural probe of `kicks_classified` printed nudge counts per goal period without filtering held-out periods (counts of nudge messages for #32, #34, #47–#50; no states, outcomes or timing). No held-out outcome was computed; every exploratory loader asserts non-holdout days.
