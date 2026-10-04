# H25: A distance-to-criticality dial, T/T_c, per window and per channel

**Status:** running. **Exploratory round 1 done (2026-10-04); round 1b on the corrected activity table done (2026-10-04, section below):** activity and talk stay subcritical on every day but read higher (median g 0.16 / 0.16, was 0.10 / 0.12); the dial now reproduces H19's estimator on the same table (P3a passes) and tracks H03's n̂ (P4a passes, ρ 0.46); under the DQ8-calibrated null only 24% of activity days beat the independent-agent ceiling (54% on the whole-day grid); native: drive withdrawal (NE43) leaves the dial unchanged, as it should; talk co-activation vanishes when 15 agents share one room (NE42). The dial works as a calibrated instrument for fast activity and talk feedback: every one of 279 days is subcritical (median g 0.10 activity, 0.12 talk; T/T_c ≈ 8–10). The headline prediction P1 **failed on content**: the O(32) content dial reads 0.70 (162 days with lower bound > 0.5). Post hoc, that reading is mostly swarm size times a constant per-pair correlation (field-like), not a coupling near threshold. Daily values carry little beyond the period mean (P5 failed); the 1-min dial is blind to coupling delayed by minutes (S3 failed). Confirmatory `analysis/confirm.py` frozen and dry-run, not run. Not promoted. Predictions were written 2026-10-04 ~01:30 UTC, before any dial was computed on real data.
**Fields:** stat mech, sociophysics, info theory
**Origin:** HH107 (`../hypohypotheses/HYPOHYPOTHESES.md`; `../promotion-shortlist.md`); tests HH108 on the way.
**Definitions used:** Population N(t) (active-population variant, per day; thresholds below); Regime; Driving / external field; Agent state (vector), *whitened statement mean* (H01 named variant), here per 30-min window. **New named variants, proposed for `physics-models/DEFINITIONS.md`** (not edited; outside H25's scope): *loop gain (equal-time, daily dial)*, *platform stall (null-calibrated joint silence)*, *content soft spin (30-min window)*, all defined under Model.

## Question
Curie–Weiss gives χ = β(1−m²)/(1 − βJ₀(1−m²)). The ratio of the observed susceptibility (variance of the collective mode, for activity *and* content separately) to the independent-agent value gives the loop gain g, and T/T_c ≈ 1/g. Report it per day as a dial: how close the swarm is to runaway cascades. *Check:* per-day g vs H03's n̂ and H19's per-period table; calibrate on simulated swarms; held-out days.

Practical aim (usefulness-first batch): produce a number or rule an operator of an LLM agent swarm could compute from logs and act on.

## Model
**From:** `physics-models/01-inverse-ising` ("Susceptibility", "Mean-field forward version"), `09-hawkes` (loop gain as branching ratio; pitfalls), `11-vector-spins` (mean-field O(n) for content). The variant is a **mean-field Curie–Weiss fluctuation–susceptibility dial**, one per channel and village day.

### The Curie–Weiss logic, step by step
1. **Spins and energy.** Each agent i carries a spin s_i. The swarm's energy is H = −(J₀/2N)(Σ_i s_i)² − Σ_i h_i(t) s_i. J₀ is the mean-field coupling (every agent feels the average of the others), h_i(t) the agent's private, time-varying field (its schedule, its goal, its habits).
2. **Self-consistency.** In mean field, m_i = tanh(β h_i + β J₀ m̄). An agent leans the way its field and the swarm's average push it.
3. **Linear response.** Push agent j a little (δh_j). Its spin moves by q_j β δh_j, with q_j = 1 − m_j² (an agent pinned hard by its field barely responds). That shifts m̄, which pushes everyone, which shifts m̄ again: δM = Σ_j q_j β δh_j · (1 + g + g² + …) = Σ_j q_j β δh_j / (1 − g), with the **loop gain g = βJ₀ q̄** (q̄ the mean of q_i).
4. **Fluctuation–dissipation.** The same feedback amplifies spontaneous fluctuations: Var(Σ_i s_i) = Σ_i q_i / (1 − g). The independent-agent value is Σ_i Var(s_i) = Σ_i q_i. So the **variance ratio** VR = Var(Σ_i s_i) / Σ_i Var(s_i) = 1/(1 − g), i.e. **g = 1 − 1/VR**. VR is the observed collective susceptibility divided by the independent-agent susceptibility; it needs no N×N inference.
5. **Criticality.** g → 1 makes VR (the susceptibility) diverge: one agent's nudge is amplified without bound and the swarm can lock in either direction. With no fields (m = 0, q = 1), g = βJ₀ = T_c/T, so **T/T_c = 1/g**. With fields, 1/g = T/(J₀ q̄) is an *effective* T/T_c: strong fields lower q̄ and push the swarm away from criticality even at fixed coupling and noise.
6. **Reading the dial.** g is the fraction of collective fluctuation produced by feedback among agents; 1/(1 − g) = VR is the amplification of a push (the mean cascade size of a branching process with ratio g). g = 0.1 means a 1.11× amplification and T/T_c = 10, far from runaway; g = 0.5 means 2×, T/T_c = 2; g = 0.9 means 10×, T/T_c ≈ 1.1.
7. **What the dial is not.** g = 1 − 1/VR is exact for equilibrium Curie–Weiss with heterogeneous fields. For other dynamics (kinetic Ising with delays, Hawkes triggering, linear feedback) VR still diverges at the same instability, so g → 1 still means criticality, but values below 1 map onto the model's own coupling through a model-dependent curve. The synthetic validation measures that curve for the swarms we simulate. Equal-time 1-min statistics see only the *fast* part of the feedback (H19's derivation): couplings acting with delays of many minutes (context read at the next turn, H04) are partly invisible.

### Channels (never pooled; H19)
- **Activity:** s_i(t) = +1 if agent i acted or talked in minute t (`activity_bins.state ≥ 3`), else −1.
- **Talk:** s_i(t) = +1 if agent i sent a chat message in minute t (`state == 4`), else −1.
- **Content (mean-field O(n)):** s_i(w) = mean, over agent i's own chat messages in 30-min window w, of the per-regime whitened (n = 32, `common.load_whitener`) and re-normalized bge statement vector. Self near-copies (cosine > 0.95 to an earlier message of the same agent that day, H12) are dropped. VR is the trace ratio tr Cov(Σ_i s_i) / Σ_i tr Cov(s_i). For unit O(n) spins the mean-field critical point is βJ₀ = n, so g = βJ₀/n here (the quantity H01's P9 reported).

### Removing drives (fields) and stalls
- **Daily schedule (activity, talk):** within each day, the mean of every spin is removed in 30-min blocks (the H02/H19 convention): any field slower than 30 min drops out. Sensitivity: 15- and 60-min blocks; and a schedule-only removal (each agent's time-of-day profile cross-fitted from the other days of the period), which keeps slow within-day co-fluctuation.
- **Content goal field, multi-direction (the H24 lesson):** (F1) each agent's day mean is removed in all 32 directions, which removes the day's goal field and the agent's own field however many directions they span; (F2, primary) F1 plus projecting out, per day, the span of the exogenous messages (human and `automated` speakers) posted that day (at most 5 principal directions), which removes within-day field changes such as kickoffs and operator corrections; (F3, conservative) F2 plus the 3 leading directions of the collective content trajectory cross-fitted on the *other* days of the same period, which also removes habitual co-movement (coupling along those directions included), giving a lower bound. Statement-sampling noise is removed from the independent-agent term by split halves (H01's P9 device): each agent's signal variance is the covariance between the means of its odd and even messages in the window.
- **Platform stalls:** a stall is a run of minutes in which *no* agent of the day's population emits any event (all `state == 1`), longer than the 95th percentile of the longest such run in 50 within-block circular-shift surrogates of that day (minimum 3 min). Stall minutes are masked before the block means are taken. Coupled silences usually still contain idle/pause events (state 2), so they are not masked. If H38's shared `data/processed/H38-platform-stalls/outages.parquet` exists at run time, it is used as a second mask; otherwise H12's lull filter (drop minutes with ≤ 1 active agent) is the fallback variant, with its truncation bias measured in the synthetic runs.

### Uncertainty and nulls per day
- **Error bars:** bootstrap over 10-min segments of the block-centered data (sufficient statistics are additive over segments), 300 resamples; 90% percentile interval; content resamples 30-min windows.
- **Null band:** 100 surrogates in which each agent's spins are circularly shifted within each 30-min block (content: each agent's window sequence circularly shifted within the day). The surrogate g's 95th percentile is the day's "independent-agent" ceiling.

## Data scheme (`scheme/`)
- **`scheme/build.py`** → `data/processed/H25-criticality-dial/inputs/`: per-day minute spins (non-holdout days only, asserted), the day's population per channel, whitened 32-d content vectors of agent chat statements with the dedupe flag (float16, no text), exogenous message vectors per day, and the H19/H03 per-period reference values. `_provenance.json` alongside.
- **`analysis/dial.py`**: the reusable dial (`compute_dial`, `spins_from_events`), with no project imports, documented to run on another swarm's logs.
- **Output:** `data/processed/H25-criticality-dial/` (`dial_daily.parquet`, `dial_period.parquet`, `events.parquet`, `synthetic/`, one `G<NN>/` per period with that period's daily dial).

## Candidate goal periods
All 35 non-holdout periods (282 days): #2–8, 10–13, 16–21, 23–27, 30, 31, 33, 35–42, 44, 51 (#51 without its held-out tail). Daily resolution. Per-period folders in `goalperiod-subhypotheses/G<NN>/`.

## Observables
*Written 2026-10-04 ~01:30 UTC.*
- **O1. Daily dial** per day d and channel c ∈ {activity, talk, content}: g_dc, its 90% interval, VR_dc (amplification), T/T_c = 1/g (shown only when the interval excludes 0), the null ceiling, population N and minutes T, stall fraction.
- **O2. Variants** (sensitivity, not verdicts): stalls kept / stall mask / H12 lull filter / H38 outages (if present); block 15/30/60 min; schedule-only removal; content F1/F2/F3.
- **O3. Period aggregates:** inverse-variance (fixed-effect) mean and random-effects mean of the daily dial per period; between-day heterogeneity (Cochran's Q, I²).
- **O4. Agreement:** with H19's per-period g_eq (active, talk; same estimator pooled over 5-day chunks with stalls kept), and with H03's n̂ TALK and fast n_x, n_s (different method): Spearman ρ, the unfitted H19 mapping ĝ_map = 2w n_x/(1 + 2w(n_x + n_s)) (w = 0.6–0.85), and a leave-one-period-out (LOPO) affine map from the period talk dial to n̂ TALK.
- **O5. Events:** step Δ = mean dial after − before at (a) the 2026-03-24 scaffold switch (regime II days of #35–#36 vs regime III days of #36–#37); (b) goal changes between adjacent non-holdout periods (last 2 days vs first 2 days); exploratory subsets: empirical hours switches (07-18, 10-20), the 05-04 room merge and 05-11 split, #51 batch joins (07-09, 09-03). Placebo: the same statistic at every within-period day boundary with ≥ 2 days each side.

## Null / baseline
*Written 2026-10-04 ~01:30 UTC.*
- **Independent agents (per day):** within-block circular shifts (activity, talk), within-day window shifts (content). Under this null g ≈ 0 with the day's sampling noise.
- **Common drive:** the dial is only meaningful after field removal; the field-only rival is tested synthetically (schedules, stalls, multi-direction content fields at J = 0 must give g ≈ 0) and on real data through the variant ladder (F1 → F2 → F3; stalls kept → masked).
- **Rivals for the period-level comparison:** a constant across periods and a regime-only step (H19's strongest rival), for the LOPO map to n̂.
- **Placebo dates** for the event tests (O5).

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** field-only (no coupling; schedules, stalls, exogenous content fields); regime-only step for the period-level gains; kinetic/delayed coupling (fast equal-time dial under-reads the DC gain).
**Locked holdout used for confirmation:** none. `analysis/confirm.py` (Stage A content on #1, #9, #14, #15, #22, #43; Stage B gated on H19's confirmatory run) is frozen (`results/frozen_confirm.json`, SHA-256) and dry-run on stand-ins #23, #24, #27, #41, #42; not run.
**Level:** below descriptive (C = 1). Not promoted.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Every spin, field and mask is defined from shared tables; the Curie–Weiss → VR → g chain is derived above and coded once (`dial.py`). **Not invariant:** g rises mechanically with N at fixed per-pair correlation (PH1), activity spins change meaning across the scaffold switch, and content depends on one embedding model. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Equal-time fluctuation–dissipation audited on synthetic kinetic swarms: holds for equilibrium and asynchronous Glauber, fails for delayed reads (S3). Within-day stationarity handled by 30-min blocks (block 15/60 change the median by ≤ 0.02). Bootstrap SEs needed a calibrated ×1.5 widening; small-N days (3–4 agents) still get optimistic SEs. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Above the per-day independent-agent ceiling on 38% (activity), 47% (talk), 84% (content) of days. The field-only rival is excluded for activity/talk stalls (S2) but not for content (S4; F1 ≈ F2 ≈ F3 ≈ F2tod). No held-out likelihood comparison. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | Talk dial exceeds the unfitted Hawkes mapping from H03's fast kernels in 80% of periods (ratio 2.3, as H19 found); LOPO map talk dial → H03 n̂ beats constant and regime-only (small margin), but ρ(talk dial, n̂) = 0.25 misses 0.3; ρ with fast n_x = 0.37. Mean-field size signature (PH1): talk follows J₀/N scaling, content does not. |
| E interventional | predicts the change across a natural experiment | 1 (1b; round 1: 0) | Scaffold switch 03-24: right signs (activity +0.08, talk −0.06) but 90% intervals include 0 (P7a failed). No movement at goal changes (as predicted; a null). Room merge/split, hours switches, #51 joins: no significant steps. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Real design days (N, minutes, schedules, statement counts): equilibrium CW recovered within 0.04 for g ≤ 0.4 (S1 mixed); stall mask = oracle (S2); fast Hawkes recovered, delayed coupling invisible (S3 failed); content field removal partial (S4 failed). Activity dial halves with H38's scheduled-off mask (PH3): preprocessing-sensitive. |
| G ground truth | agrees with known structure | 1 | Reproduces H19's estimator per period (activity ρ 0.94; talk 0.69 fixed-effect, 0.84 random-effects). Regime III − I: activity up, talk down (H19, H38), but the activity difference is mostly N (per-pair ρ̄ 0.011 vs 0.009). Masked stalls drop the activity dial by 0.10 on the 50 stall days. |
| H comparative | beats the named rivals | 1 | For talk, Curie–Weiss J₀/N scaling beats the field model out of sample (LOPO SSE 0.21 vs 0.30); for content the field model wins (0.81 vs 1.42), so the CW reading of the content dial is not faithful. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Holdout not used. Across non-holdout periods: activity/talk subcritical in all 35; content verdicts split by N. |

## Prediction
*Written 2026-10-04 ~01:30 UTC, before computing the dial on any real day.* **Disclosure (not blind):** I had read H19's per-period table (g_eq active 0.11 median, talk 0.15; H03 n̂ TALK 0.41), H01's P9 (content βJ₀/n median 0.74, an upper bound), H12's lull and market-mode results and H04's NE21 result, and I had looked at design facts only (per-day N, minutes per day, statements per agent-window). Credences in brackets use that knowledge.

**Synthetic (axis F), before real data.**
- **S1.** Static Curie–Weiss with a real daily schedule, real N and day lengths: per-day g recovered with |median bias| ≤ 0.03 for true g ∈ [0, 0.6]; 90% bootstrap intervals cover the truth in 80–95% of days; at g = 0, ≤ 10% of days have a lower bound > 0. [0.7]
- **S2.** Unmasked stalls inflate g; the stall mask removes ≥ 80% of the inflation and biases g by ≤ 0.03 when there are no stalls; H12's lull filter biases g downward by ≥ 0.05 at N ≤ 6. [0.6]
- **S3.** Kinetic swarms (asynchronous Glauber with delayed reads; Hawkes talk with exponential kernels): the 1-min dial is monotone in the true DC loop gain but reads below it, by a factor of 0.3–0.8 for low-occupancy talk-like spins and 0.6–1.0 for persistent activity spins. [0.5]
- **S4.** Content: with no coupling but a multi-direction, time-varying exogenous field, F1 alone reads g > 0.1 and F2 brings it to |g| ≤ 0.05; with coupling, the split-half correction recovers g within 0.05 for g ≤ 0.6. [0.55]

**Real data (exploratory, non-holdout).**
- **P1 (subcritical every day).** Activity and talk: the upper 90% bound is < 0.8 on ≥ 95% of estimable days and no day has a lower bound > 0.5. Content (F2): upper bound < 0.8 on ≥ 90% of days. *Against:* more days near criticality, or any confidently near-critical activity/talk day. [activity/talk 0.8; content 0.55]
- **P2 (levels).** Median daily dial with stalls masked: activity in [0.03, 0.20]; talk in [0.03, 0.25]. [0.65]
- **P3 (consistency with H19).** (a) The per-period fixed-effect mean of the daily activity dial *with stalls kept* reproduces H19's g_eq active: Spearman ρ ≥ 0.8 and median |difference| ≤ 0.03; talk ρ ≥ 0.7. [0.8] (b) Masking stalls lowers the activity dial (median per-day change < 0 among days with stalls), more where stalls are longer (ρ(stall fraction, drop) > 0.3). [0.6]
- **P4 (H03, out of sample).** (a) Period talk dial vs H03 n̂ TALK: ρ ≥ 0.3 [0.55]; (b) |ρ(activity dial, n̂ TALK)| < 0.3 (channel split) [0.6]; (c) a LOPO affine map from the talk dial predicts each period's n̂ TALK with lower squared error, summed over periods, than the LOPO constant [0.45]; (d) the talk dial exceeds the unfitted ĝ_map(w = 0.6) from H03's fast n_x, n_s in ≥ 2/3 of periods [0.75].
- **P5 (a daily dial carries information).** Between-day heterogeneity of the activity dial beyond sampling noise (Cochran's Q, p < 0.05) in ≥ 50% of periods with ≥ 5 estimable days. *Against:* day-to-day variation consistent with noise, so a period or weekly dial would do. [0.5]
- **P6 (content vs activity, HH108).** (a) The content dial (F2) exceeds the activity dial (period medians) in ≥ 70% of periods with both [0.55]; (b) the overall median daily content dial (F2) lies in [0.15, 0.6] [0.5] and below H01's 0.74 [0.75]; (c) F2 lowers the content dial relative to F1 (median per-day change < 0) [0.7].
- **P7 (events).** (a) **Scaffold switch 2026-03-24:** the activity dial steps up and the talk dial steps down (90% intervals of Δ exclude 0), as H19's regime contrast implies at period level [0.45]. (b) **Goal changes:** the mean |z| of the step at goal boundaries is *not* above the placebo 95th percentile, for activity and talk: the dial tracks scaffold and roster, not the goal [0.6]. (c) Exploratory, no verdict: hours switches, the room merge and split, #51 batch joins, and the content dial on kickoff days (expected higher under F1, less so under F2).

**Per-period verdict rule** (copied into each G card before its run): *supported* if (i) every day is subcritical in all estimable channels (upper 90% bound < 0.8, content F2 included), (ii) the period's activity and talk dials with stalls kept reproduce H19's g_eq within max(0.05, 2 SE), and (iii) the period's median content dial (F2) is < 0.74; *failed* if any day is confidently near-critical (lower 90% bound > 0.8) in any channel, or (ii) and (iii) both fail; *mixed* otherwise.

**Amendment 1 (2026-10-04 01:58 UTC, after the synthetic validation and before any real-data dial; implementation only, predictions unchanged).**
- **Content noise correction:** the independent-agent term now uses a method-of-moments correction (each agent's window-mean variance minus its pooled within-window statement scatter divided by the statement count), not split halves. It uses every statement; the split-half version is kept as the `F2split` variant. Days with VR ≤ 0 (noise) are floored at VR = 0.05 rather than dropped: in the first synthetic pass, dropping them selected positive-g days (+0.25 bias at g = 0).
- **Interval calibration:** bootstrap intervals over 10-min segments were too narrow at village sample sizes (synthetic z-SD 1.3–1.5; resampling whole 30-min blocks did not help). Intervals and SEs are widened ×1.5 (`dial.SE_INFLATE`), which restores ~0.9 coverage on equilibrium Curie–Weiss and fast-Hawkes swarms (in-sample calibration; an independent synthetic set gives z-SD 1.3–1.5).
- **H38 masks:** H38's `outages.parquet` lists joint-silence runs (≤ 1 active agent), which is K-dependent like H12's lull filter. H25 instead uses H38's per-minute `stall_minutes.parquet` as two external variants: `h38_sched` (village scheduled off) and `h38_exo` (scheduled or an infrastructure-error burst; H38's K-independent mask).
- **Multi-scale diagnostic** (`dial.vr_scale`, 5- and 10-min coarse-graining in 60-min blocks): reported, not a dial (field leakage of 0.1–0.36 at g = 0 in the synthetic runs).
- **Synthetic verdicts** (axis F, scored before real data): S1 mixed, S2 supported, S3 failed, S4 failed. Details under Results. Consequence for reading the real dial: activity/talk dials are lower bounds on the DC loop gain (blind to coupling delayed by minutes); content dials are upper bounds on coupling (time-varying fields are only partly removed).

**Multiplicity.** Verdicts come only from S1–S4 and P1–P7(b). Variants, per-day p-values and the exploratory events are descriptive. 35 periods, 3 channels, 4 stall variants and 3 content variants make many numbers; no per-day "significant" day is claimed as a finding.

## Confirmatory design (`analysis/confirm.py`, written, NOT run)
The holdout is crowded, so the design follows the reuse policy (`../holdout.md`):
- **H19's planned confirmation** computes g_eq active and talk (the period means of the same estimator) on #1, #9, #14, #15, #22, #28, #29, #32, #34, #43 and the #51 tail. H25 must not compute activity or talk dials there first, or H19's statistic would be examined. **H12's** confirmation claims content and activity collective-mode statistics on #28, #29, #32, #34, #45–#50 and the #51 tail.
- **Stage A (content, runnable now once committed):** the daily content dial (F2) on #1, #9, #14, #15, #22 (and #43 if estimable). Nobody computes a within-day content co-fluctuation statistic there (H20 uses day-to-day aging on #1, H24 forecast numbers on #14, H12's C7 a participation ratio on #22: different statistics, disclosed). Predictions frozen from this round's exploratory distribution.
- **CA4 (added at the freeze, from post hoc PH1):** each held-out period's median content dial predicted from its content population alone, g = (N−1)ρ̄/(1 + (N−1)ρ̄) with the exploratory per-pair ρ̄ = 0.281; pass if ≥ 4 periods fall within ±0.15 and the model beats the constant 0.71. This is the confirmatory test of the post hoc size-scaling reading.
- **Stage B (activity and talk day-level statistics), gated:** runs only after H19's confirmatory results exist, and then tests only statistics H19 does not compute (within-period heterogeneity, the subcriticality rule per day), disclosed as reuse.
- **H03 agreement on the holdout** is scored only if H03 exports held-out n̂ in H19's shared schema (`confirmatory = true`); H25 never fits Hawkes models on held-out data.

## Results by goal period
Per-period verdict rule (card, copied into each G card at 02:00 UTC before the run). **0 supported, 22 mixed, 13 failed** (round 1b: 1 / 21 / 13; only G07 changes). Check (i) fails in every period because content upper bounds are wide (only 22.5% of content days have an upper bound < 0.8); all 13 failures are content days with a lower bound > 0.8, concentrated in periods with N ≥ 10 (regime I from #18 on, regime II–III). Activity and talk are subcritical on every day of every period. "activity" = stalls masked (fixed-effect mean of days); "kept" = stalls kept (the H19 comparison); RE = random-effects mean.

| Period | Role | Verdict | Verdict (1b) | Key numbers (round 1; 1b numbers in each folder) |
| --- | --- | --- | --- | --- |
| [G02](goalperiod-subhypotheses/G02/README.md) | exploratory | mixed | mixed | activity 0.22 (kept 0.22; H19 0.23), talk 0.34 (RE 0.31; H19 0.28), content median 0.64; 2 days |
| [G03](goalperiod-subhypotheses/G03/README.md) | exploratory | mixed | mixed | activity 0.02 (kept 0.02; H19 0.02), talk 0.08 (RE 0.08; H19 0.10), content median 0.59; 3 days |
| [G04](goalperiod-subhypotheses/G04/README.md) | exploratory | mixed | mixed | activity 0.11 (kept 0.11; H19 0.10), talk 0.27 (RE 0.24; H19 0.27), content median 0.42; 25 days |
| [G05](goalperiod-subhypotheses/G05/README.md) | exploratory | mixed | mixed | activity -0.13 (kept -0.12; H19 -0.07), talk 0.09 (RE 0.09; H19 0.10), content median 0.55; 5 days |
| [G06](goalperiod-subhypotheses/G06/README.md) | exploratory | mixed | mixed | activity 0.01 (kept 0.01; H19 0.00), talk 0.13 (RE 0.10; H19 -0.07), content median 0.16; 13 days; stalls-kept dial off H19 |
| [G07](goalperiod-subhypotheses/G07/README.md) | exploratory | mixed | supported | activity 0.10 (kept 0.10; H19 0.08), talk 0.17 (RE 0.17; H19 –), content median 0.53; 2 days |
| [G08](goalperiod-subhypotheses/G08/README.md) | exploratory | mixed | mixed | activity 0.02 (kept 0.04; H19 0.03), talk -0.03 (RE -0.03; H19 -0.01), content median 0.30; 18 days |
| [G10](goalperiod-subhypotheses/G10/README.md) | exploratory | mixed | mixed | activity 0.24 (kept 0.31; H19 0.29), talk 0.13 (RE 0.13; H19 0.15), content median 0.19; 5 days |
| [G11](goalperiod-subhypotheses/G11/README.md) | exploratory | mixed | mixed | activity 0.19 (kept 0.23; H19 0.30), talk 0.18 (RE 0.18; H19 0.22), content median 0.56; 5 days |
| [G12](goalperiod-subhypotheses/G12/README.md) | exploratory | mixed | mixed | activity 0.17 (kept 0.17; H19 0.17), talk 0.18 (RE 0.18; H19 0.18), content median 0.70; 5 days |
| [G13](goalperiod-subhypotheses/G13/README.md) | exploratory | mixed | mixed | activity 0.01 (kept 0.01; H19 0.03), talk 0.11 (RE 0.11; H19 0.12), content median 0.49; 10 days |
| [G16](goalperiod-subhypotheses/G16/README.md) | exploratory | mixed | mixed | activity 0.23 (kept 0.26; H19 0.28), talk 0.26 (RE 0.26; H19 0.25), content median 0.49; 4 days |
| [G17](goalperiod-subhypotheses/G17/README.md) | exploratory | mixed | mixed | activity 0.16 (kept 0.17; H19 0.12), talk 0.36 (RE 0.31; H19 0.38), content median 0.69; 5 days |
| [G18](goalperiod-subhypotheses/G18/README.md) | exploratory | failed | failed | activity 0.09 (kept 0.10; H19 0.08), talk 0.27 (RE 0.26; H19 0.24), content median 0.78; 10 days; content day(s) with lower bound > 0.8, content median ≥ 0.74 |
| [G19](goalperiod-subhypotheses/G19/README.md) | exploratory | mixed | mixed | activity 0.06 (kept 0.11; H19 0.11), talk 0.25 (RE 0.24; H19 0.26), content median 0.75; 10 days; content median ≥ 0.74 |
| [G20](goalperiod-subhypotheses/G20/README.md) | exploratory | mixed | mixed | activity 0.03 (kept 0.03; H19 0.04), talk 0.15 (RE 0.15; H19 0.17), content median 0.75; 10 days; content median ≥ 0.74 |
| [G21](goalperiod-subhypotheses/G21/README.md) | exploratory | mixed | mixed | activity 0.07 (kept 0.05; H19 0.09), talk 0.18 (RE 0.18; H19 0.17), content median 0.71; 5 days |
| [G23](goalperiod-subhypotheses/G23/README.md) | exploratory | mixed | mixed | activity -0.00 (kept 0.01; H19 0.04), talk 0.23 (RE 0.23; H19 0.20), content median 0.68; 5 days |
| [G24](goalperiod-subhypotheses/G24/README.md) | exploratory | mixed | mixed | activity -0.02 (kept -0.02; H19 -0.00), talk 0.19 (RE 0.19; H19 0.20), content median 0.65; 5 days |
| [G25](goalperiod-subhypotheses/G25/README.md) | exploratory | failed | failed | activity 0.04 (kept 0.05; H19 0.05), talk 0.10 (RE 0.10; H19 0.13), content median 0.77; 5 days; content day(s) with lower bound > 0.8, content median ≥ 0.74 |
| [G26](goalperiod-subhypotheses/G26/README.md) | exploratory | failed | failed | activity 0.01 (kept 0.10; H19 0.21), talk -0.05 (RE 0.08; H19 0.24), content median 0.83; 5 days; content day(s) with lower bound > 0.8, stalls-kept dial off H19, content median ≥ 0.74 |
| [G27](goalperiod-subhypotheses/G27/README.md) | exploratory | mixed | mixed | activity 0.13 (kept 0.13; H19 0.14), talk 0.15 (RE 0.15; H19 0.12), content median 0.71; 10 days |
| [G30](goalperiod-subhypotheses/G30/README.md) | exploratory | failed | failed | activity 0.05 (kept 0.07; H19 0.10), talk -0.07 (RE 0.12; H19 0.21), content median 0.85; 5 days; content day(s) with lower bound > 0.8, stalls-kept dial off H19, content median ≥ 0.74 |
| [G31](goalperiod-subhypotheses/G31/README.md) | exploratory | failed | failed | activity 0.05 (kept 0.05; H19 0.07), talk 0.14 (RE 0.14; H19 0.13), content median 0.81; 5 days; content day(s) with lower bound > 0.8, content median ≥ 0.74 |
| [G33](goalperiod-subhypotheses/G33/README.md) | exploratory | failed | failed | activity 0.11 (kept 0.11; H19 0.11), talk 0.07 (RE 0.07; H19 0.07), content median 0.86; 3 days; content day(s) with lower bound > 0.8, content median ≥ 0.74 |
| [G35](goalperiod-subhypotheses/G35/README.md) | exploratory | failed | failed | activity 0.07 (kept 0.09; H19 0.10), talk 0.21 (RE 0.21; H19 0.17), content median 0.84; 5 days; content day(s) with lower bound > 0.8, content median ≥ 0.74 |
| [G36](goalperiod-subhypotheses/G36/README.md) | exploratory | mixed | mixed | activity 0.08 (kept 0.13; H19 0.17), talk 0.10 (RE 0.10; H19 0.08), content median 0.74; 5 days; content median ≥ 0.74 |
| [G37](goalperiod-subhypotheses/G37/README.md) | exploratory | failed | failed | activity 0.24 (kept 0.34; H19 0.32), talk 0.19 (RE 0.19; H19 0.16), content median 0.77; 3 days; content day(s) with lower bound > 0.8, content median ≥ 0.74 |
| [G38](goalperiod-subhypotheses/G38/README.md) | exploratory | failed | failed | activity 0.10 (kept 0.12; H19 0.12), talk -0.03 (RE 0.02; H19 0.04), content median 0.71; 17 days; content day(s) with lower bound > 0.8, stalls-kept dial off H19 |
| [G39](goalperiod-subhypotheses/G39/README.md) | exploratory | mixed | mixed | activity 0.16 (kept 0.17; H19 0.19), talk 0.13 (RE 0.13; H19 0.12), content median 0.29; 5 days |
| [G40](goalperiod-subhypotheses/G40/README.md) | native (1b) · replication | mixed | mixed (native NE42: mixed) | activity 0.28 (kept 0.31; H19 0.35), talk 0.03 (RE 0.03; H19 0.02), content median 0.72; 5 days |
| [G41](goalperiod-subhypotheses/G41/README.md) | exploratory | failed | failed | activity 0.07 (kept 0.09; H19 0.13), talk 0.11 (RE 0.11; H19 0.08), content median 0.80; 5 days; content day(s) with lower bound > 0.8, content median ≥ 0.74 |
| [G42](goalperiod-subhypotheses/G42/README.md) | exploratory | failed | failed | activity 0.11 (kept 0.11; H19 0.11), talk 0.11 (RE 0.11; H19 0.08), content median 0.81; 5 days; content day(s) with lower bound > 0.8, content median ≥ 0.74 |
| [G44](goalperiod-subhypotheses/G44/README.md) | exploratory | failed | failed | activity 0.28 (kept 0.30; H19 0.36), talk -0.01 (RE 0.05; H19 0.15), content median 0.79; 4 days; content day(s) with lower bound > 0.8, stalls-kept dial off H19, content median ≥ 0.74 |
| [G51](goalperiod-subhypotheses/G51/README.md) | native (1b) · replication | failed | failed (native size law: failed) | activity 0.17 (kept 0.20; H19 0.24), talk 0.06 (RE 0.09; H19 0.11), content median 0.76; 45 days; content day(s) with lower bound > 0.8, stalls-kept dial off H19, content median ≥ 0.74 |
| [NE43](goalperiod-subhypotheses/NE43/README.md) | native (1b) | – | supported | bookends stop / nudger stop inside #51: activity z −0.78 / +0.43, talk −1.47 / +0.24, all inside the placebo band (q95 1.04, 1.57) |

## Results
*Exploratory round 1, 2026-10-04, non-holdout only (35 periods, 282 days; 279 activity, 261 talk, 280 content day-dials). Numbers from `data/processed/H25-criticality-dial/results/{explore,posthoc,synthetic_verdicts}.json`; scripts `analysis/explore.py`, `posthoc.py`, `synthetic.py`, `synthetic_verdicts.py`; figures in `figures/`.*

### Headline
- **Activity and talk are far from criticality on every day.** Median daily g = 0.096 (activity, stalls masked) and 0.122 (talk), i.e. T/T_c ≈ 10 and 8 and a push amplification 1/(1 − g) ≈ 1.1. No day's upper 90% bound reaches 0.8 (maxima 0.76 and 0.66). With H38's scheduled-off minutes also masked, the activity dial halves to 0.050 (T/T_c ≈ 20); agent-level edge trimming leaves it at 0.058.
- **The content dial reads near-critical, but it is a size effect.** Median 0.70 (F2), lower bound > 0.5 on 162 of 280 days, > 0.8 on 33. Removing exogenous message directions (F2), habitual directions (F3) or a cross-fitted time-of-day content profile (F2tod, post hoc) changes nothing (0.68–0.72). Post hoc (PH1), the per-pair correlation of within-day content fluctuations is flat in N (ρ̄ ≈ 0.28, exponent α = −0.06 [−0.50, 0.27]), so g = (N−1)ρ̄/(1+(N−1)ρ̄) climbs with N (ρ(g, N) = 0.76 across periods). That is the signature of a shared field or of constant per-pair coupling, not of Curie–Weiss coupling normalized by N (α = 1), which loses out of sample (LOPO SSE 1.42 vs 0.81).
- **Talk is the one channel that behaves like mean-field coupling:** its per-pair correlation falls with N (α = 0.69 [−0.38, 1.71]), and J₀/N scaling predicts period-level talk gains best (LOPO SSE 0.21 vs 0.30 for the field model). That matches H19's per-message budget.
- **A daily dial is mostly noise at this sample size.** Between-day heterogeneity beyond sampling error in 2 of 28 periods for activity (median I² = 0); 32% with the unwidened SEs. A period or weekly dial carries the information.

### Outcome vs prediction
| # | Prediction | Observed | Outcome |
| --- | --- | --- | --- |
| S1 | static CW recovered, \|bias\| ≤ 0.03 for g ≤ 0.6, coverage 0.8–0.95, ≤ 10% false positives | bias ≤ 0.04 for g ≤ 0.4, −0.06 to −0.08 near g = 0.5; raw coverage 0.55–0.9 (≈ 0.9 after ×1.5); false positives 7.5–12.5% | mixed |
| S2 | stalls inflate g; mask removes ≥ 80%; lull filter biased ≥ 0.05 at N ≤ 6 | unmasked +0.15; mask catches 98% of outage minutes (0.07% false minutes), bias +0.006 = oracle; lull −0.37 at N ≤ 6 | supported |
| S3 | kinetic: monotone, factor 0.3–0.8 (talk), 0.6–1.0 (activity) | delayed reads: dial ≈ 0 at every coupling; slow Hawkes (τ = 3 min) factor 0.2–0.3; fast Hawkes ≈ 1 | failed |
| S4 | content: F1 leak > 0.1, F2 \|g\| ≤ 0.05; recovery within 0.05 | F1 leak 0.26–0.30, F2 still 0.20–0.26; recovery within ≈ 0.09 | failed |
| P1 | all days subcritical (activity/talk ≥ 95%, content ≥ 90%) | activity, talk 100%; content 22.5% (33 days lower bound > 0.8) | **failed (content)** |
| P2 | median activity in [0.03, 0.20], talk in [0.03, 0.25] | 0.096, 0.122 | supported |
| P3a | period means reproduce H19: activity ρ ≥ 0.8 & \|Δ\| ≤ 0.03; talk ρ ≥ 0.7 | activity 0.94, 0.019; talk 0.685 (random-effects means, post hoc: 0.84) | failed (narrowly, talk) |
| P3b | masking stalls lowers activity; drop grows with stall share (ρ > 0.3) | −0.095 median on 50 stall days; ρ 0.21 (period) | failed (second half) |
| P4a | ρ(talk dial, H03 n̂) ≥ 0.3 | 0.25 (with fast n_x: 0.37) | failed |
| P4b | \|ρ(activity dial, n̂)\| < 0.3 | 0.04 | supported |
| P4c | LOPO map talk dial → n̂ beats constant | SSE 1.78 vs 1.86 (regime-only 2.32) | supported (small margin) |
| P4d | talk dial > ĝ_map(0.6) in ≥ 2/3 of periods | 80%, median ratio 2.3 | supported |
| P5 | Cochran Q p < 0.05 in ≥ 50% of periods (activity) | 7% (2/28) | failed |
| P6a | content > activity in ≥ 70% of periods | 100% (35/35) | supported |
| P6b | content median in [0.15, 0.6] and < 0.74 | 0.70 | failed / supported |
| P6c | F2 < F1 | median Δ = +0.0001 | failed |
| P7a | 03-24 switch: activity up, talk down, intervals exclude 0 | +0.08 [−0.05, 0.20], −0.06 [−0.18, 0.06] | failed (right signs) |
| P7b | no step at goal changes beyond placebo (activity, talk) | mean \|z\| 0.66 vs placebo q95 0.83 (p 0.55); talk 0.88 vs 0.89 (p 0.06) | supported (talk borderline) |
| per period | supported / mixed / failed | 0 / 22 / 13 | content drives every failure |

### Synthetic validation (axis F; `figures/fig_synthetic.png`)
Design: 120 real non-holdout days (real N, minutes, per-agent 2-h schedules, real statement structure), 40 days per cell; stalls in half the days; idle events on 30% of inactive minutes (0% as a check).
- **Equilibrium swarms are recovered** (Gibbs and asynchronous Glauber): bias ≤ 0.04 for g ≤ 0.4; the dial under-reads by 0.06–0.08 near g = 0.5. The 30-min block choice is the compromise: 15-min blocks under-read (−0.07 to −0.13 at g ≈ 0.35–0.45), 60-min blocks leak the schedule (+0.05 to +0.09 at g = 0). A fast (31-min) real-drive field leaks only +0.03.
- **Stalls:** a single 5–45 min outage inflates g by about 0.15; the null-calibrated stall mask equals the oracle mask. H12's lull filter is biased low (−0.37 at g = 0 for N ≤ 6) and erratic.
- **Blind spot:** when agents respond to others' state with a 2–8 min delay (context read at the next turn, H04/H08), the equal-time 1-min dial stays at 0 even at true g = 0.45; a coarse 10-min variance ratio sees part of it (0.08 → 0.32) but leaks fields (0.08–0.36 at g = 0). For Hawkes talk swarms the dial tracks the DC cross gain n_x/(1−n_s) for 20-s kernels and misses most of it for 3-min kernels.
- **Content:** with no time-varying field the moment-corrected estimator recovers g within ≈ 0.09 (the uncorrected one under-reads by up to 0.36); a 3-direction exogenous field seen only through noisy messages leaks 0.26–0.30, and F2 removes at most a fifth of it.
- **Intervals:** bootstrap z-SD 1.3–1.5; widened ×1.5 they cover ≈ 0.90 (in-sample calibration).

### Agreement with H19 and H03 (`figures/fig_agreement.png`)
- **H19 (same estimator, pooled over 5-day chunks):** activity ρ = 0.94, median |Δ| = 0.019; talk ρ = 0.69 (fixed-effect means; days with 3–4 talkers have small, optimistic SEs and pull the mean), 0.84 with random-effects means and 0.91 with day medians (post hoc). Mismatches: G06, G26, G30, G38, G44, G51 (talk), G26 and G36 (activity after masking).
- **H03 (Hawkes, different method):** the talk dial correlates with fast cross-offspring n_x (0.37) more than with total n̂ (0.25). It sits above the unfitted Hawkes-mapped gain in 80% of periods (ratio 2.3). The synthetic fast-Hawkes runs read ≈ n_x/(1−n_s), which is about 1.5–1.7× ĝ_map, so part of H19's "excess over the mapping" is the mapping's first-order approximation, not only common fast fields. The activity dial is unrelated to n̂ (0.04), as the channel split predicts.

### Variants (`figures/fig_variants.png`)
Medians of daily g. Activity: none 0.109, auto 0.096, h38_sched 0.056, h38_exo 0.065, auto + h38_sched 0.050, + edge trimming 0.058, lull −0.02 (biased), blocks 15/60 0.085/0.107, schedule-only centering 0.43 (most co-activation sits at > 30-min scales inside days; slow drives and slow coupling cannot be separated there). Talk: 0.108–0.133 across masks and blocks; schedule-only 0.23. Content: F1 0.70, F2 0.70, F3 0.68, F2tod 0.72, no dedupe 0.67, split-half 0.65.

### Events (`data/processed/H25-criticality-dial/events.parquet`)
- Scaffold switch (regime II days of #35–#36 vs regime III days of #36–#37): activity +0.08 [−0.05, 0.20], talk −0.06 [−0.18, 0.06].
- Goal changes (25 boundaries) vs 178 within-period placebo boundaries: activity and talk dials do not step (p = 0.55, 0.06); content steps slightly more than placebo (p = 0.049, exploratory).
- Hours 2 → 3 h (07-18) and 3 → 4 h (10-20), room merge (05-04) and split (05-11), #51 batch joins (07-09, 09-03): all |z| < 1.9. The two #51 joins raise talk by +0.17 and +0.14 (z 1.8, 1.5), in the direction of more agents.

### Post hoc (labelled; after seeing round-1 results)
- **PH1 size scaling** (above): per-pair ρ̄ = 0.011 (activity), 0.019 (talk), 0.28 (content). For an operator, ρ̄ is the size-free number; g follows from it and N.
- **PH2:** with unwidened SEs, day-level heterogeneity is significant in 32% (activity), 45% (talk), 21% (content) of periods.
- **PH3/PH4:** masking H38's scheduled-off minutes halves the activity dial (0.096 → 0.050); agent-level edge trimming adds little (0.058; regime III 0.077, I 0.040). Talk unchanged (0.118–0.125).
- **F2tod** (time-of-day content profile, added after a 3-day smoke test): no effect (0.72).

### Caveats
- **The equal-time dial is a lower bound** on the DC loop gain: coupling that acts through the next turn's context, minutes later, is invisible (S3). The village's coupling is largely of that kind (H04, H08), so "subcritical" here means "no fast runaway", not "no slow herding".
- **The content dial is an upper bound on coupling:** time-varying shared fields are only partly removed (S4), and the flat per-pair correlation is what a shared field produces. Its high reading should not be read as "ideas are about to cascade" (HH108); it says agents' within-day topics move together at ρ̄ ≈ 0.28 per pair, as in any shared conversation.
- **g grows with N** at fixed per-pair correlation (activity, content), so cross-period differences in g (including H19's regime III − I contrast in activity) are partly roster size.
- Daily values are mostly noise (2–8 h days, ~10 agents); the ×1.5 interval widening is calibrated on synthetic village days and makes the daily dial conservative. Days with ≤ 4 agents have optimistic SEs and biased g (−0.05 to −0.07 at small N in synthetic runs).
- One embedding model (bge-small); content windows of 30 min; the H38 masks were built by a concurrently running hypothesis.
- Not blind: H19's and H03's per-period values were known when predictions were written. Many variants: only P1–P7(b) and S1–S4 carry verdicts.

## Round 1b (improved data, 2026-10-04)
*Re-run of the round-1 pipeline on the corrected activity table, the DQ8 null-size correction, and three period-native tests. Predictions S1–S4, P1–P7 and the per-period rule are unchanged; native predictions were written in the NE43, G51 and G40 folders at 06:34 UTC, before their runs.*

**What changed in the inputs.**
- `activity_bins` dropped about half of all events (DQ8). Round 1b rebuilds the activity-derived inputs from `activity_bins_fixed` (`scheme/build.py --data-version fixed` → `inputs_r1b/`): spins, the H38 masks from the shared `outages_fixed/stall_minutes`, and an **H19 reference on the fixed table** (H19's g_eq estimator as computed by H38's round-1b pipeline, which reproduces H19 exactly on the old table). The round-1 H19 values in `refs.parquet` are stale for the activity and talk channels. Statements and exogenous messages do not depend on the activity table; content point estimates are identical (intervals differ by bootstrap draws).
- **Null sizes (DQ8).** The per-day null (each agent circularly shifted within 30-min blocks) on whole-day grids rejects 28–34% of independent swarms; after trimming each day to the all-present window it rejects 2–4%. Round 1b adds the variant `trim` (auto stall mask plus all-present window, applied before the null is drawn) and reports the share of days above the null ceiling under both designs. H12's lull filter, which H25 found biased (−0.37 at N ≤ 6), stays a non-primary variant.
- Code: `--data-version fixed` in `scheme/build.py`, `analysis/explore.py`, `analysis/posthoc.py` (the old path still runs); new `analysis/r1b_native.py`, `r1b_periods.py`, `r1b_figures.py`. Outputs in `data/processed/H25-criticality-dial/r1b/`.

**Old vs new (282 non-holdout days, 35 periods).**

| Statistic | Round 1 (old table) | Round 1b (fixed table) |
| --- | --- | --- |
| P1 activity / talk days with upper bound < 0.8 (max upper bound) | 100% / 100% (0.76 / 0.66) | 100% / 100% (0.77 / 0.68) |
| P1 content days with upper bound < 0.8 · lower bound > 0.8 | 22.5% · 33 | 23.9% · 34 (same point estimates) |
| P2 median daily dial, activity · talk | 0.096 · 0.122 | **0.159 · 0.162** |
| activity medians by mask: none · auto · + H38 scheduled · + edges · **DQ8 trim** | 0.109 · 0.096 · 0.050 · 0.058 · – | 0.185 · 0.159 · 0.096 · 0.086 · **0.067** |
| days above the per-day null q95: activity · talk · content (round-1 design) | 38% · 47% · 84% | 54% · 61% · 84% |
| **DQ8 null:** days above the null q95 after trimming, activity · talk | – | **24% · 53%** |
| P3a vs H19 (stalls kept), activity ρ, \|Δ\| · talk ρ | 0.94, 0.019 · 0.69 | vs round-1 H19 (stale): 0.84, 0.058 · 0.71; **vs H19 on the fixed table: 0.94, 0.021 · 0.97** |
| P3b stall days · median drop · ρ(stall share, drop) | 50 · −0.095 · 0.21 | 30 · −0.153 · −0.09 |
| P4a ρ(talk dial, H03 n̂ TALK) · with fast n_x | 0.25 · 0.37 | **0.46 · 0.60** |
| P4b ρ(activity dial, n̂) | 0.04 | −0.07 |
| P4c LOPO SSE map · constant · regime-only | 1.78 · 1.86 · 2.32 | 1.46 · 1.86 · 2.32 |
| P4d talk dial above the Hawkes map (w = 0.6), median ratio | 80%, 2.3 | 97%, 3.3 |
| P5 periods with between-day heterogeneity (activity) | 2/28 | 4/29 |
| P6 content (unchanged inputs) | a ✓ · b 0.70 · c no change | identical |
| P7a 03-24 switch, activity · talk [90%] | +0.08 [−0.05, 0.20] · −0.06 [−0.18, 0.06] | **+0.16 [+0.02, +0.29]** · +0.05 [−0.05, +0.16] |
| P7b goal changes vs placebo, activity p · talk p | 0.55 · 0.06 | 0.46 · 0.25 |
| PH1 (post hoc) talk α [90%] · LOPO SSE CW vs field | 0.69 [−0.38, 1.71] · 0.21 vs 0.30 | **1.25 [0.77, 1.77]** · 0.37 vs 0.57 |
| PH1 activity α · ρ̄ · best LOPO model | 0.50 · 0.011 · field | 0.45 [0.05, 0.84] · 0.020 · field (0.29; dilution 0.31; CW 0.38) |
| per-period verdicts (supported / mixed / failed) | 0 / 22 / 13 | 1 / 21 / 13 |

**Which verdicts change.**
- **P3a: failed → supported.** Against H19's estimator on the same (fixed) table the dial agrees closely (activity ρ 0.94, |Δ| 0.021; talk ρ 0.97). Round 1's narrow talk failure (0.69) was the event-drop bug acting differently on per-day and pooled-chunk statistics.
- **P4a: failed → supported** (ρ 0.46 with H03's n̂, 0.60 with fast n_x). The talk dial is now a credible cross-method gauge (H03 fits event times, which the bug did not touch).
- **P7a still fails, differently:** the activity step at the 03-24 switch now clears its 90% interval (+0.16), but the talk dial rises too (+0.05) instead of falling.
- P1, P5, P6b/c and P3b still fail; P2, P4b–d, P6a, P7b still pass. Per period only G07 changes (mixed → supported).
- **Corrected null:** with each day trimmed to the common running window, only 24% of activity days exceed the independent-agent ceiling (54% without trimming) and the median activity dial is 0.067 (T/T_c ≈ 15). Talk barely moves (53%; 0.143). Much of the apparent activity feedback is day-edge synchrony (H38), not coupling.
- **Native tests:** **NE43 supported**: neither the bookend stop (08-05) nor the nudger stop (08-21) moves the activity or talk dial beyond within-#51 placebo boundaries (|z| ≤ 1.47 vs q95 1.04–1.57), so the dial measures feedback, not these drives. **G51 size law failed (uninformative)**: over N = 21 → 32 constant-ρ̄ and constant-g models differ by 2–4% in leave-one-day-out error. **G40 / NE42 mixed**: talk co-activation vanishes in the merged 15-agent room (g 0.13 → 0.003 → 0.18; Δ −0.15 [−0.27, −0.03]), which neither size reading predicted; activity rises (+0.17, interval spans 0); content does not double.

**Cross-hypothesis corroboration (H50, 2026-10-04; built from `call_windows`).** H50's transfer-function analysis finds activity co-movement to be mostly the scheduler's daily start/stop (0.62–0.67 of it) and per-pair activity correlation inside the all-present window of only 0.056 (regime I) / 0.005 (regime III), in line with the trimmed activity dial (median 0.067, 24% of days above the ceiling); talk co-movement is a coupling at one read-out call (pooled J₁ 0.034 / 0.019), in line with the talk dial surviving trimming and following J₀/N. The 1-min equal-time dial sees that hop-1 coupling only partly (S3).

**Scorecard after 1b.** A 1; B 1; C 1 (calibrated null: activity above the ceiling on 24% of trimmed days, talk 53%, content 84%); D 1 (P4a now passes; talk follows J₀/N with α 1.25); **E 0 → 1** (NE43: drive withdrawal predicted not to move the dial, and it does not; P7a right sign for activity only; NE42 talk collapse unpredicted); F 1; G 1 (reproduces H19 on the same table, ρ 0.94 / 0.97); H 1 (talk: CW beats the field model out of sample, 0.37 vs 0.57); I 0.

## The operator-facing dial
**Definition (per day, per channel).** Minute spins s_i(t) = ±1 (activity: any event; talk: a message posted). Mask platform stalls (runs in which nobody logs any event, longer than chance; `dial.find_stalls`) and any known scheduled-off minutes. Remove each agent's mean in 30-min blocks. Then VR = Σ_t(Σ_i X_it)² / Σ_t Σ_i X_it², **g = 1 − 1/VR**, amplification = VR, **T/T_c = 1/g**, and **per-pair correlation ρ̄ = (VR − 1)/(N − 1)**. 90% intervals: bootstrap over 10-min segments, widened ×1.5. Content: the same ratio on 30-min window means of whitened, unit-normalized message embeddings, after removing each agent's day mean and the span of operator/human messages, with statement noise removed by a method-of-moments correction.

**How to compute it on another swarm's logs.**
```python
import polars as pl, dial                                  # hypotheses/H25-criticality-dial/analysis/dial.py
spins = dial.spins_from_events(events, agent="agent", t="t", is_talk="is_talk")   # one row per agent event
W = dial.fit_whitener(train_vectors, dim=32)               # optional content channel
out = dial.compute_dial(spins, statements=msgs, statement_vectors=W(msg_vectors),
                        exo_statements=ops, exo_vectors=W(op_vectors))
week = dial.aggregate_days(out.filter(pl.col("channel") == "talk")["g"], out.filter(pl.col("channel") == "talk")["se"])
```
Log idle or heartbeat events as non-talk events if the platform has them: they make the stall detector specific. Recalibrate `SE_INFLATE` with `synthetic.py`-style simulations that share your logs' day length and N.

**How to read it.**
- Act on weekly or period random-effects means, not single days.
- Bands use the upper 90% bound: green < 1/3 (amplification < 1.5), amber < 2/3, red ≥ 2/3.
- Track ρ̄ as well as g. For a fixed ρ̄, g(N) = (N−1)ρ̄/(1 + (N−1)ρ̄), so adding agents raises g mechanically. A jump in ρ̄, not in g, signals a change in coupling or shared drive.
- In this village, crossing g = 0.5 would take about 90 agents for activity (ρ̄ = 0.011); talk is size-independent at about 0.12.
- **Blind spot:** a green dial does not rule out slow, context-mediated herding (S3).

## Round 2 redirects
- **What the direction is really after:** a trustworthy number for how much the swarm amplifies a push; it must be lag-aware and size-aware, with per-pair correlation as the transferable quantity.
- **H25-R1. A lagged (DC) dial** from 1–15 min cross-covariances, validated on the delayed-coupling swarms where the 1-min dial reads 0.
- **H25-R2. Agent-level availability masks** from H38's scaffold states (consolidation, day edges, infra errors).
- **H25-R3. Content fields from real anchors** (goal and kickoff embeddings, artifact events) plus an embedding swap; coordinate with H26.
- **H25-R4. Test the size law** g(N) = (N−1)ρ̄/(1+(N−1)ρ̄) at roster changes and on the holdout (CA4).
- **H25-R5. A weekly dial with change-point detection**, at least 5 agents per day.

## Figures
- `figures/fig_synthetic.png`: recovery on simulated swarms (activity CW and kinetic, Hawkes talk, O(32) content).
- `figures/fig_timeline.png`: the daily dial over all 282 non-holdout days, three channels, period means.
- `figures/fig_agreement.png`: vs H19 g_eq, vs H03 n̂, vs the unfitted Hawkes mapping.
- `figures/fig_variants.png`: sensitivity ladder (masks, blocks, field removal).
- `figures/summary_obs.png`, `summary_obs2.png`: summary-page panels. Per period: `goalperiod-subhypotheses/G<NN>/figures/G<NN>_dial.png`.

## Notes
- 2026-10-04: promoted from HH107 by Vivian (usefulness-first batch); wave 1.
- 2026-10-04 ~01:30 UTC: round 1 started. Model variant, observables, nulls and predictions written before any real-data dial. Edit scope: this folder and `data/processed/H25-criticality-dial/` only; shared changes are proposed in the hand-back.
- 2026-10-04 01:33–01:58 UTC: synthetic validation (`analysis/synthetic.py`, 2 workers, ~5 min); Amendment 1 written before any real-data dial.
- 2026-10-04 02:00 UTC: 35 period cards written with dated predictions (`write_period_folders.py --predict`).
- 2026-10-04 02:01 UTC: a 3-day smoke test on real data (2025-06-02, 2026-04-08, 2026-08-12) preceded the full run; after it, the post hoc content variant F2tod was added (labelled). Full run 02:02–02:05; re-run 02:08–02:12 after making the stall threshold deterministic (seeded from the data, so `compute_dial` and the exploration agree exactly) and capping upper bounds at 1. Results unchanged except 3 activity days.
- 2026-10-04: `confirm.py --freeze` (CA1–CA4, CB1–CB2 frozen with SHA-256) and `--dry-run` on non-holdout stand-ins. The holdout has not been touched.
- Disk: `data/processed/H25-criticality-dial/` 13 MB.
- Concurrency: H38's `stall_minutes.parquet` (built 2026-10-04 by the running H38 agent) supplies the `h38_*` masks; H26 (HH108) is testing the content-near-critical idea in parallel.
- 2026-10-04: round 1b (corrected activity table, DQ8 trim variant, H19 reference on the fixed table, native NE43 / #51 size law / NE42); ~10 min of compute on ≤ 2 processes; +3 MB in `data/processed/H25-criticality-dial/r1b/` and `inputs_r1b/`.
