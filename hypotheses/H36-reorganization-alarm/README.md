# H36: A reorganization alarm: susceptibility and multi-information peak at transitions

**Status:** exploratory round 1 done (agent, 2026-10-04): **mixed**. The physics alarm sees goal changes weakly (hit 0.30, AUC 0.68), entirely through content, and loses to a plain content-centroid detector (AUC 0.95). `analysis/confirm.py` written and dry-run, not run. Observables, nulls, the alarm rule and the predictions below were written 2026-10-04 ~01:40 UTC, before the synthetic validation and before any statistic was computed on real data.
**Fields:** stat mech, sociophysics, info theory
**Origin:** HH126, merging HH65 (`../hypohypotheses/HYPOHYPOTHESES.md`; `../promotion-shortlist.md`). Related: H27 (herding early warning, HH109) and H25 (criticality dial), running in parallel; H38 (platform stalls) supplies the outage mask.
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Population N(t), **day-present variant** (roster agents, Claude Code excluded, with ≥ 10 active minutes, `activity_bins.state ≥ 3`, on that PT day; H38 uses ≥ 1 minute); Regime (alarm baselines cross regime boundaries on purpose, because the boundary is a transition to detect; this is the card's named exception (c), transitions as the object); Agent state, **categorical variant = the 4-state activity class** of `activity_bins` (silent / idle / act / talk; the regime-invariant action class); Agent state, **vector variant = whitened statement mean per agent × 30-min window** (`embeddings/agent_win30`, regime whitener, n = 32, unit-normalized; H01's "whitened statement mean" at window instead of day resolution); Mutual information between agents. **New named variants proposed** (not edited into DEFINITIONS.md; outside this card's scope): *multi-information (Gaussian, activity spins)*, *multi-information (pairwise expansion, behavior states)*, *content multi-information (overlap)*, *heat-capacity analogue (alignment-energy variance)*, *joint silence / village-off gap* (H38's definitions, reused as the outage mask).

## Question
The total correlation among agents' states and the heat-capacity analogue (variance of the alignment energy) should spike when the swarm reorganizes: goal changes, room events, scaffold changes. One alarm for "something structural is happening" (merges HH65). *Check:* peak detection against known transitions; false-alarm rate on placebo days.

Practical aim (usefulness-first batch): produce a number or rule an operator of an LLM agent swarm could compute from logs and act on. **Deliverable:** an alarm rule with measured hit rate, false-alarm rate and lead or lag, or a clear negative.

## Model
**From:** `physics-models/01-inverse-ising` (activity spins; susceptibility, heat capacity, multi-information) and `physics-models/11-vector-spins` (content vectors; polarization, alignment energy). The H36 variant:

- **Activity spins.** s_i(t) = +1 if agent i is active (state ≥ 3) in 1-min bin t, else −1; day-present agents only; outage minutes masked.
- **Pairwise max-ent reference.** P(s) ∝ exp(Σ_i h_i s_i + Σ_{i<j} J_ij s_i s_j). We never fit J_ij (H02: individual couplings are not recoverable from 1-min activity). We use the fluctuation relations that hold for any J:
  - susceptibility of the uniform mode χ = (1/n) Σ_ij C_ij = n Var(m), normalized as the **variance ratio** VR = Var(M) / Σ_i Var(s_i) (VR = 1 for independent agents; in Curie–Weiss VR ≈ 1/(1 − βJ₀(1 − m²)));
  - **heat-capacity analogue** c = Var(E)/n with the uniform alignment energy E(t) = −(1/n) Σ_{i<j} s_i(t) s_j(t) (the max-ent C = β² Var(E)/n at β = 1, with J_ij replaced by the uniform mean-field coupling, since the true J is not identifiable);
  - **multi-information** I_N = Σ_i S(s_i) − S(**s**). Not estimable directly from ~120–480 bins per day at n ≈ 4–18, so two approximations: the Gaussian form I_G = −½ log det R (R = correlation matrix of the spins; I_G ≈ ½ Σ_{i<j} ρ_ij² for weak correlation), and the pairwise expansion I_2 = Σ_{i<j} MI(σ_i; σ_j) on the 4-state behavior class.
- **Content vector spins** (model 11). ŝ_i(w) ∈ S³¹ per agent and 30-min window w. Alignment energy per window e(w) = −mean_{i<j} ŝ_i·ŝ_j; content multi-information from the agent-centered overlap matrix Q_ij (H12's overlap form); content variance ratio VR_c = 1ᵀQ1 / tr Q.
- **Why these should peak at reorganizations (the hypothesis).** In mean field χ ∝ (1 − βJ₀)⁻¹ and C, I_N grow with the coupling; a reorganization that passes the swarm through, or near, a coupled collective state (everyone re-coordinating on a new goal or a new room) should raise all three for a while, as in flocks at collective turns.
- **Why they may not (the mechanism-level rival, pre-stated).** A goal change that acts as a *field step between days* (kickoffs precede the day's window, H04) changes h, not J. Within-day fluctuation statistics then change only through the (1 − m²) factors: no alarm. A *mid-day* step adds within-day non-stationarity, which inflates every variance statistic (an alarm, but for a trivial reason). And a platform stall (all agents silenced together, H38) inflates χ, C and I_G at zero coupling. The synthetic validation tests all three routes.

## Data scheme (`scheme/`)
`scheme/build.py` builds `data/processed/H36-reorganization-alarm/` from shared tables only (no text), non-holdout days only, with a hard holdout assertion and `_provenance.json`:
- **Inputs:** `activity_bins` (1-min states), `calendar`, `roster`, `kicks` (goal kickoffs, NE dates, roster joins/leaves), `rooms` + `rooms_timeline` (room creations, deletions, moves), `embeddings/agent_win30` + `agent_day` (+ regime whiteners). H38's `outages.parquet` if it exists at build time; otherwise the fallback outage mask below.
- **Outage mask (fallback, H38/H12 definitions):** village-off gaps (runs of ≥ 10 consecutive minutes with K_t = 0, K_t = number of day-present agents active) are dropped as stalls. **Lull variant** (robustness): drop every joint-silence minute (K_t ≤ 1), H12's lull filter.
- **`day_stats.parquet`:** one row per non-holdout active day with n_d ≥ 3: n, minutes kept, outage minutes, each statistic (observed, surrogate mean and SD), the rival statistics. Per-period copies in `G<NN>/day_stats.parquet`.
- **`events.parquet`:** the transition catalog (below), with day 0, class, confound flags and holdout status. **`placebos.parquet`:** placebo days and their Monday flag.

## Observables
All per non-holdout active day d (the village runs 2–8 h a day; every goal kickoff precedes the day's window, so a day is the natural alarm step).

**Physics statistics (the alarm's inputs).** Each is reported as an *excess* over S = 30 surrogates of the same day, observed − surrogate mean, so that day length and n don't set the noise floor:
| Family | Activity channel (1-min) | Content channel (30-min windows) |
| --- | --- | --- |
| multi-information | **I_act** = I_G per pair; **I_beh** = I_2 (4-state, plug-in MI with Miller–Madow correction) per pair | **I_cont** = −½ log det Q̃ per pair (Q̃ = normalized overlap of agent-centered window vectors; missing windows 0; agents with ≥ 3 windows) |
| susceptibility | **χ_act** = VR | **χ_cont** = VR_c |
| heat capacity | **C_act** = Var_t(E)/n | **C_cont** = Var_w(e(w)) × mean number of pairs (windows with ≥ 2 agents) |

- Activity surrogates: independent within-day circular shifts of each agent's masked series (keeps each agent's rate and autocorrelation, destroys alignment). Content surrogates: each agent's windows permuted within the day.
- Content statistics need ≥ 3 agents with ≥ 3 windows that day; otherwise missing (the family z then uses the activity channel only).

**Alarm scores.** For each statistic X: z(d) = (X(d) − median of X over the previous B = 10 non-holdout active days) / (SD of those 10 days after dropping their max and min), computed only when ≥ 5 baseline days exist. Family scores Z_I = mean(z_I_act, z_I_beh, z_I_cont), Z_χ = mean(z_χ_act, z_χ_cont), Z_C = mean(z_C_act, z_C_cont) over available members, and **Z_phys(d) = mean(Z_I, Z_χ, Z_C)**.

**Pre-registered alarm rule (primary):** the alarm fires on day d if **Z_phys(d) ≥ 2.0** (one-sided: a peak). Secondary rules, reported but not used for the verdict: OR rule (any family Z ≥ 3.0); two-sided |Z_phys| ≥ 2.0; per-family and per-statistic alarms.

**Transitions** (catalog from `kicks`, `rooms`, `rooms_timeline`; day 0 = the first non-holdout active day at or after the event time, or the day containing it if the event is mid-window):
- **T-goal (NE34):** every goal kickoff whose day 0 is non-holdout. The primary class.
- **T-room:** room events that move ≥ 2 established agents: 03-16 #best/#rest split (NE15), 05-04 merge into #universe-coordination and 05-11/12 split back (NE42), 07-09 newcomer isolation rooms (NE32), 08-05 #focus. Three of five coincide with goal kickoffs (flagged *goal-confounded*).
- **T-scaffold:** NE02–NE04, NE06, NE07, NE09–NE11, NE14 (scored at the 03-24 regime boundary, inside #36; the 03-11 start is held out), NE16–NE18, NE38, and roster batch events NE27–NE29, NE31, NE33. Events coinciding with a goal kickoff are flagged.
- Events whose day 0 is held out are excluded from exploration and listed for the confirmatory script.
- **Amendment 0 (2026-10-04 ~01:43 UTC, design facts only, before any statistic):** (a) offsets (day −1, +1, the ≥ 3-day placebo distance) count *calendar* active days; held-out days have no statistics and are simply missing from a window, and trailing baselines skip them. (b) NE32's rooms each held one newcomer, so by the ≥ 2-established-agents rule NE32 is a roster event, not T-room; the 07-24 side-room (2 agents, 4 h) qualifies as a minor T-room event. (c) NE10 is scored at the first observed nudge, 02-13 (H04), not the catalog's 02-10. (d) If H38's `outages.parquet` exists at build time, the stall mask is its runs with `village_off`, or `cause` ∈ {scheduled, infra_error}, or `infra_burst`; otherwise the fallback (K = 0 runs ≥ 10 min). (e) R1 is computed on raw 384-d agent-day vectors centered on the non-holdout mean (regime whiteners would create a fake jump at 03-24), and is missing when the previous active day is held out.

**Evaluation.**
- **Hit:** an alarm on any of days −1, 0, +1 (relative to day 0; offsets in non-holdout active days). **Hit rate** per class.
- **Placebo days:** non-holdout active days ≥ 3 active days from every catalogued event (goal kickoffs, NEs, roster joins/leaves, room creations/deletions), with a full baseline. **Per-day false-alarm rate (FAR)** = alarm share on placebo days. **Window FAR** = share of 3-day placebo windows (centered on placebo days whose neighbours are also ≥ 2 days from events) with any alarm; the hit rate is compared with this.
- **Monday placebos** (strongest null): placebo days that are the first active day after a ≥ 2-calendar-day gap. Goal kickoffs are mostly Mondays, so a Monday effect would masquerade as a transition effect.
- **AUC** of Z_phys on day 0 of T-goal vs placebo days (threshold-free), with a bootstrap CI over events and placebo days; same for each family and rival.
- **Timing:** offset in [−3, +3] of each transition's max Z_phys; offset of the earliest alarm in [−1, +1]. Lead = day −1; lag = day 0 or +1.
- **Random-date null for the hit rate:** transition days reassigned at random among eligible non-holdout days (same regime), 2,000 draws; p = share of draws with hit rate ≥ observed.
- **Stall null:** among placebo days, FAR on the top-decile days by outage minutes, with the outage mask on (primary) and off (no mask), to measure whether stalls trigger false alarms.

**Rivals (axis H).**
- **R1, content centroid shift** (first moment, the obvious detector): D(d) = 1 − cos(m̄_d, m̄_{d−1}), m̄_d = mean over day-present agents of the whitened unit agent-day vectors; z against the same trailing baseline; one-sided.
- **R2, activity level:** mean active fraction of day-present agents; two-sided |z|.
- **R3, content polarization** |m̄_d|; two-sided |z|.
- Comparison: AUC(Z_phys) vs AUC(R1) on T-goal day 0 (paired bootstrap), and whether Z_phys adds to R1 (alarm on R1 or Z_phys vs R1 alone: hit gain against FAR cost).

## Null / baseline
1. **Independent agents with the same rates and autocorrelation** (surrogates, built into every statistic as the excess).
2. **Trailing baseline** of the swarm's own last 10 active days (the alarm is a deviation detector).
3. **Placebo days and placebo windows** far from every catalogued event; **Monday placebos** (weekend gap, the strongest null for goal kickoffs).
4. **Random event dates** (hit-rate permutation null).
5. **Stalls** (H38): outage-heavy placebo days, masked and unmasked.
6. **Rival detectors** R1–R3 (first-moment change).

## Synthetic validation (axis F, before real data)
`analysis/synthetic.py`: kinetic Ising swarms at village sampling (n ∈ {7, 12, 15}; day lengths 120–480 min drawn like the real calendar; synchronous 1-min Glauber updates with self-persistence, a daily start-up ramp and a shared slow 30-min field so that day-to-day variance is realistic), 4-state behavior from the activity spin, and content vector spins in d = 32 with anisotropic, low-dimensional fluctuations (H20: 5–12 effective dims), agents speaking in ~60% of windows. 40-day runs, switches on days 10, 20, 30, 20 runs per scenario. Scenarios, each with its expected outcome under the model:
- **S1 coupling up** (βJ₀ 0.2 → 0.7, day boundary): χ, C, I rise → expect hits ≥ 0.8.
- **S2 coupling down** (0.7 → 0.2): the one-sided alarm should miss (≤ window FAR); two-sided should hit.
- **S3 field step at a day boundary** (common rate shift plus a reshuffle of who is active): expect ≤ window FAR + 0.1 (no alarm); R2 should hit.
- **S4 content goal switch at a day boundary** (new goal direction ĝ): R1 should hit ≈ 1; content physics statistics ≤ window FAR + 0.1.
- **S5 mid-day field step** (the S3 change inside a day): expect ≥ 0.6 (non-stationarity inflates variances).
- **S6 content coupling up** (shared window-level drift amplitude ×3): content family hits ≥ 0.7.
- **S7 stalls only** (joint silences ≈ 5% of minutes in 3–20-min runs on 30% of days, plus 60–120-min village-off gaps on 15% of days; no structural change): FAR with the fallback mask ≤ 0.1; without any mask, FAR on stall days > 0.2.
- **S0 nothing:** per-day FAR at Z_phys ≥ 2.0 in [0.01, 0.10].

## Prediction
*Written 2026-10-04 ~01:40 UTC, before running the synthetic validation and before computing any statistic on real data.* **Disclosure (not blind):** I have read the round-1 results of H02, H04, H12, H17, H20 and H38's card (kickoffs don't change activity level; the market mode is partly synchronized lulls; kickoffs raise content diversity; content settles ~4 days after a big kickoff; joint silences inflate collective statistics). I have looked only at table schemas and the event catalog (dates), no statistic. Credences in brackets.

- **P0 (synthetic, F):** the S0–S7 expectations above hold [0.75]. If S1 (coupling up) is not detected at ≥ 0.8, the pipeline is underpowered and the real-data verdict is "uninformative", not "failed".
- **P1 (primary, T-goal):** the physics alarm (Z_phys ≥ 2.0) hits **≤ 40%** of goal changes, with window FAR ≈ 15–30%, and AUC(Z_phys, day 0) **< 0.65** [0.65]. Reason: goal changes are day-boundary field steps (H04, H20), which fluctuation statistics don't see. **H36 is supported on goal changes only if** hit rate ≥ 0.6, window FAR ≤ 0.25, AUC ≥ 0.70 with CI excluding 0.5, the random-date p < 0.05, and it survives Monday placebos (Monday FAR ≤ 0.25). **Failed if** AUC ≤ 0.60 or random-date p > 0.10. Mixed otherwise. [Credence supported: 0.2.]
- **P2 (channel):** content statistics respond more than activity statistics at goal changes (AUC of the content members > AUC of the activity members) [0.6]. Direction: C_cont and χ_cont up on day 0 (a within-day relaxation after the kickoff, H20; H12's diversity rise on day 1) [0.5]; activity members at chance [0.7].
- **P3 (rival):** R1 (content centroid shift) has AUC ≥ 0.8 on goal changes [0.75] and beats Z_phys [0.8]. Adding Z_phys to R1 raises the hit rate by < 0.1 [0.7].
- **P4 (rooms, descriptive; 5 events, 3 goal-confounded):** the 05-04 merge raises activity χ/I (z ≥ 2 on day 0) [0.35]; the 03-16 and 05-11 splits lower them (z ≤ −1) [0.4 each]. No inference from n = 5.
- **P5 (scaffold):** the 03-24 regime boundary (NE14, perma-computer-use) fires the alarm within ±1 day [0.6] (the activity grammar changes completely). The remaining scaffold and roster events: hit rate within ±0.15 of window FAR [0.7].
- **P6 (stalls):** with the outage mask off, ≥ 1/3 of placebo false alarms fall on top-decile outage days, and the mask lowers placebo FAR [0.55].
- **P7 (FAR):** per-day placebo FAR at Z_phys ≥ 2.0 is in [0.03, 0.12] [0.6]; Monday placebos have a higher FAR than other placebos [0.55].
- **P8 (timing):** hits, where they occur, peak on day 0 or +1, not day −1; no early warning above chance on day −1 [0.7].

### Amendment 1 (2026-10-04 ~01:50 UTC, after the first synthetic run, before any real-data statistic)
1. **z-scale fix.** The trailing scale (SD of the baseline after dropping max and min) is biased low: for k Gaussian draws its mean is 0.52σ (k = 5) to 0.70σ (k = 10). Uncorrected, every z was inflated ~1.4× and the synthetic per-day FAR at 2.0 was 7–12% instead of the intended few percent. The scale is now divided by that consistency factor (`h36lib.TRIM_C`). Threshold (2.0), baseline length and families are unchanged.
2. **Synthetic content recalibrated.** The first generator's window drift and noise were ~30× the goal field (pairwise cosine ≈ 0.02 across windows), which no real period resembles; the content variance is now normalized so the pairwise cosine is ≈ 0.26–0.36, the round-1 level (H24 A_res 0.33; H01). Only the synthetic generator changed.
3. **Added (secondary, not for the verdict):** threshold-free AUC for every score; hit rate at a matched per-day FAR of 5% (thresholds from synthetic S0); a channel-max score Z_chan = max(Z_act, Z_cont); a moderate-coupling scenario S8 (βJ₀ 0.2 → 0.45).

### Synthetic validation result (after Amendment 1; `analysis/synthetic.py`, 30 runs per scenario, `data/processed/H36-reorganization-alarm/synthetic/summary.json`)
| Scenario | Z_phys hit | window FAR | AUC [95% CI] | best member | R1 / R2 hit (AUC) | Expected | Met? |
| --- | --- | --- | --- | --- | --- | --- | --- |
| S0 nothing | 0.03 | 0.05 | 0.55 | – | 0.20 / 0.13 | per-day FAR 0.01–0.10 | yes (0.022) |
| S1 coupling up 0.2 → 0.7 | **0.40** | 0.16 | 0.77 [0.68, 0.86] | Z_act 0.70 hit, AUC 0.76 | 0.37 / 0.40 | ≥ 0.8 | **no** |
| S8 coupling up 0.2 → 0.45 | 0.23 | 0.08 | 0.63 [0.51, 0.74] | Z_act AUC 0.65 | 0.30 / 0.27 | (power curve) | – |
| S2 coupling down | 0.07 | 0.06 | 0.41 | – (two-sided 0.07) | 0.37 / 0.27 | miss one-sided; two-sided hits | half (two-sided also misses) |
| S3 field step, day boundary | 0.17 | 0.06 | 0.61 | – | 0.20 / **0.90 (0.86)** | ≤ FAR + 0.1; R2 hits | yes |
| S4 content goal switch, day boundary | 0.07 | 0.10 | 0.47 | – | **1.00 (1.00)** / 0.30 | content physics ≤ FAR + 0.1; R1 ≈ 1 | yes |
| S5 mid-day field step | 0.13 | 0.06 | 0.72 | Z_act 0.43 | 0.30 / **0.87 (0.85)** | ≥ 0.6 | **no** |
| S6 content coupling ×3 | **0.73** | 0.08 | **0.93** [0.88, 0.97] | Z_cont 0.97, AUC 0.99 | 0.97 / 0.30 | content family ≥ 0.7 | yes |
| S7 stalls only | 0.03 | 0.10 | 0.46 | – | 0.43 / 0.27 | masked FAR ≤ 0.1; unmasked stall-day FAR > 0.2 | half: masked 0.04 vs clean 0.03; unmasked stall days 0.05 vs clean 0.02 |

**Reading (written before real data).** The pre-registered alarm is conservative (per-day FAR 2–5%, window FAR 5–16%) and **identifies content-coupling reorganizations well (S6) but activity-coupling ones only partly (S1: AUC 0.77, hit 0.40)**, because day-to-day activity noise (start-up ramp, shared slow field, varying n) is large. It is blind, as designed, to day-boundary field steps (S3, S4), which the first-moment rivals catch (R2, R1 at AUC 0.86 and 1.00). Stalls of the simulated size barely move it. **Consequence for the verdict (per P0):** a real-data miss on goal changes rules out S6-sized content reorganizations but is *uninformative* about S1-sized activity reorganizations; AUC, not the 2.0 hit rate, is the more powerful readout for the activity channel.

**Deliverable either way:** the measured operating characteristics (hit rate per class, per-day and window FAR, AUC, timing) for the physics alarm and for R1, so an operator can see which one to run.

## Confirmatory predictions (frozen for `analysis/confirm.py`; written 2026-10-04, before any holdout access)
Targets: the 15 goal kickoffs whose day 0 is held out (#9, #14, #15, #22, #28, #29, #32, #34, #43, #45–#50); placebos: held-out days ≥ 3 active days from every catalogued event. Statistics and rules are frozen as in round 1; in confirm mode the trailing baseline runs over all active days in time order.
- **C1 (primary, the pre-registered alarm):** AUC(Z_phys, day 0 vs placebo) ≥ 0.60 and hit rate > placebo window FAR [0.55].
- **C2 (content channel):** AUC(Z_cont, day 0) ≥ 0.65 with the 95% CI above 0.5 [0.5].
- **C3 (post hoc operator rule):** R1 ≥ 3.0 or Z_cont ≥ 2.0 on days −1..+1: hit ≥ 0.40 and window FAR ≤ 0.10 [0.45].
- **C4 (rival ordering):** AUC(R1) > AUC(Z_phys) [0.85].
- **C5 (activity null):** AUC(Z_act) ≤ 0.65 [0.7].
- **C6:** descriptive alarm table for the held-out NEs (NE12/NE35, #voted-out, NE30, NE13, NE14 start, NE19–NE26, NE37, NE01, NE05, NE08).
- **Overall:** CONFIRMED if C1 and C2 pass; PARTIAL if one does; NOT CONFIRMED otherwise.
- **Reuse disclosure (policy in `../holdout.md`):** #34 is targeted by the unrun confirm scripts of H01, H05, H07, H12, H19 and H21; #45 was used by H02 (activity couplings) and is planned by H23 (message content); #14, #15, #22, #28 and #43 appear in other confirm scripts (H13, H20, H24 and others). H36's statistics (within-day surrogate-excess co-fluctuation, trailing-z alarm) are new. **R1 (day-to-day centroid shift) is close to H20's two-time content correlation and H12's participation ratio**, so the reuse must be disclosed in both cards and in LOG.md, and the card and script committed, before the run.
- Dry run on non-holdout stand-ins (`data/processed/H36-reorganization-alarm/confirm_dryrun/confirm.json`) reproduces the exploratory numbers (AUC Z_phys 0.68, Z_cont 0.77, Z_act 0.55, R1 0.95; C3 hit 0.58, window FAR 0.02).

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** first-moment change detectors (R1 content centroid shift, R2 activity level, R3 polarization); field-step (h-only) transitions; stalls as a common field (H38).
**Locked holdout used for confirmation:** none yet (`analysis/confirm.py` written and dry-run, not run).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | All statistics from `activity_bins`, `agent_win30`/`agent_day` and the event catalog; assumptions listed. Not invariant: activity alarms are twice as frequent on days when n, day length or the gap to the previous day changes (15% vs 7%, PH3); content uses regime whiteners. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | The trailing-baseline null is calibrated: real per-day placebo FAR 0.033 matches the synthetic 0.02–0.05 after the Amendment 1 scale fix. No Markov or update-order audit (equal-time statistics only). |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Goal changes: beats placebo days (AUC 0.68 [0.56, 0.79]) and random dates (p 0.03); weaker against Monday placebos (AUC 0.62); hit rate 0.30, below the 0.6 bar. |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | The coupling signature (activity and content χ, C, I rising together, synthetic S1/S6) is absent: the activity channel is at chance (AUC 0.55; 0.47 without sampling changes); the content rise is ~40% a within-day linear drift (PH2). |
| E interventional | predicts the change across a natural experiment | 0 | Room events show no coupling sign pattern (05-04 merge: activity z −0.6); NE14 (03-24) missed; scaffold events at chance (1/13 vs window FAR 0.10). |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Synthetic at village sampling: content coupling recovered (S6 AUC 0.93), activity coupling only partly (S1 AUC 0.77, hit 0.40); blind to day-boundary field steps as designed. Real AUC robust to bin width and mask (0.68–0.75). No embedding swap. |
| G ground truth | agrees with known structure | 1 | Detects catalogued goal changes above chance; misses scaffold changes; roster batches 3/6 (n small, confounded). |
| H comparative | beats the named rivals | 0 | Loses to R1 by ΔAUC −0.26 [−0.39, −0.13]. Post hoc, the content channel is complementary to R1 (same hit rate at a tenth of the false alarms), but in-sample. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Holdout not run; kickoff hits in 10 of 33 scored periods. |

## Results by goal period
Each G folder holds that period's kickoff (day 0 = its first active day) and its placebo days. Verdict rule: supported = kickoff window alarms and placebo FAR ≤ 0.10; failed = kickoff window scored and silent.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [NE34](goalperiod-subhypotheses/NE34/README.md) | exploratory, spanning #2–#51 | mixed | 33 scored kickoffs: Z_phys hit 0.30, window FAR 0.10, AUC 0.68 [0.56, 0.79], random-date p 0.03; Z_cont AUC 0.77; R1 AUC 0.95 |
| [NE15](goalperiod-subhypotheses/NE15/README.md) | exploratory | descriptive | 03-16 split (with #35): Z_phys −0.75; activity χ/I slightly down; no alarm |
| [NE42](goalperiod-subhypotheses/NE42/README.md) | exploratory | descriptive | merge 05-04: no alarm (Z_act −0.6, Z_cont 2.8); split 05-11: alarm on day +1 (Z_act −3.0, Z_cont 3.2); R1 5.2 / 9.0 |
| [NE14](goalperiod-subhypotheses/NE14/README.md) | exploratory | failed | 03-24 regime boundary: Z_phys −0.78 (predicted alarm) |
| [NE17](goalperiod-subhypotheses/NE17/README.md) | exploratory | failed | no alarm (Z_phys −1.18), as predicted |
| [NE18](goalperiod-subhypotheses/NE18/README.md) | exploratory | failed | no alarm (Z_phys 0.73), as predicted |
| [NE41](goalperiod-subhypotheses/NE41/README.md) | exploratory | n/a | consolidations vs Z_phys on regime-III placebo days ρ −0.31 (p 0.26, n 15) |
| [G02](goalperiod-subhypotheses/G02/README.md) | exploratory | n/a | kickoff not scored |
| [G03](goalperiod-subhypotheses/G03/README.md) | exploratory | n/a | kickoff not scored |
| [G04](goalperiod-subhypotheses/G04/README.md) | exploratory | failed | kickoff Z_phys –/−1.8/1.6 (d−1/0/+1), Z_cont d0 −2.8; placebo 1/14 |
| [G05](goalperiod-subhypotheses/G05/README.md) | exploratory | failed | 0.4/0.2/1.1, Z_cont d0 0.9, R1 d0 0.7 |
| [G06](goalperiod-subhypotheses/G06/README.md) | exploratory | failed | 1.0/0.3/−1.0, Z_cont 0.0, R1 2.8; placebo 0/5 |
| [G07](goalperiod-subhypotheses/G07/README.md) | exploratory | failed | –/1.9/1.2, Z_cont 4.2, R1 2.7 |
| [G08](goalperiod-subhypotheses/G08/README.md) | exploratory | supported | 1.2/6.5/0.1 (day length 2→3 h), Z_cont 2.5, R1 5.5; placebo 1/13 |
| [G10](goalperiod-subhypotheses/G10/README.md) | exploratory | supported | –/8.8/2.9, Z_cont 4.3; with NE27 (N 4→7) |
| [G11](goalperiod-subhypotheses/G11/README.md) | exploratory | failed | −0.0/−0.1/0.7, Z_cont −0.1 |
| [G12](goalperiod-subhypotheses/G12/README.md) | exploratory | supported | 2.6/1.5/0.9 (alarm on day −1), Z_cont 3.3, R1 3.6 |
| [G13](goalperiod-subhypotheses/G13/README.md) | exploratory | failed | −0.2/−0.3/−1.0; placebo 0/5 |
| [G16](goalperiod-subhypotheses/G16/README.md) | exploratory | supported | –/4.4/−0.3 (activity; after held-out #14–#15), Z_cont 0.3 |
| [G17](goalperiod-subhypotheses/G17/README.md) | exploratory | failed | 0.2/0.8/−0.7, Z_cont 2.2 |
| [G18](goalperiod-subhypotheses/G18/README.md) | exploratory | supported | 0.8/2.8/−0.0, Z_cont 3.0, R1 2.3 |
| [G19](goalperiod-subhypotheses/G19/README.md) | exploratory | failed | 0.2/−0.1/0.7; placebo 0/4 |
| [G20](goalperiod-subhypotheses/G20/README.md) | exploratory | failed | 0.5/0.1/−0.1, R1 5.2 |
| [G21](goalperiod-subhypotheses/G21/README.md) | exploratory | supported | 2.3/0.6/1.2 (alarm on day −1, Thanksgiving Friday); with NE28 |
| [G23](goalperiod-subhypotheses/G23/README.md) | exploratory | failed | –/−0.2/−0.7 |
| [G24](goalperiod-subhypotheses/G24/README.md) | exploratory | failed | −0.7/0.0/−0.4, R1 2.3; with NE09 |
| [G25](goalperiod-subhypotheses/G25/README.md) | exploratory | failed | 1.0/0.6/1.2, Z_cont 2.0, R1 3.2 |
| [G26](goalperiod-subhypotheses/G26/README.md) | exploratory | supported | 0.4/4.4/−0.1, Z_cont 7.9 (C_cont 10.3) |
| [G27](goalperiod-subhypotheses/G27/README.md) | exploratory | failed | 1.5/0.0/−0.2, R1 2.2; placebo 0/5 |
| [G30](goalperiod-subhypotheses/G30/README.md) | exploratory | supported | –/2.9/−0.4, Z_cont 5.4 |
| [G31](goalperiod-subhypotheses/G31/README.md) | exploratory | failed | 0.1/0.0/−1.0, R1 5.3 |
| [G33](goalperiod-subhypotheses/G33/README.md) | exploratory | failed | –/1.4/0.9, Z_cont 2.0 |
| [G35](goalperiod-subhypotheses/G35/README.md) | exploratory | failed | –/−0.7/−0.1; with NE15 |
| [G36](goalperiod-subhypotheses/G36/README.md) | exploratory | failed | 0.2/0.3/−0.8, R1 5.8 |
| [G37](goalperiod-subhypotheses/G37/README.md) | exploratory | failed | −1.3/0.1/0.3, R1 2.6 |
| [G38](goalperiod-subhypotheses/G38/README.md) | exploratory | failed | 0.4/−0.6/−0.2, R1 2.4; placebo 0/3 |
| [G39](goalperiod-subhypotheses/G39/README.md) | exploratory | supported | 2.5/3.5/0.6 (activity; a join that day), R1 28.8 |
| [G40](goalperiod-subhypotheses/G40/README.md) | exploratory | failed | −0.1/0.8/−0.2, Z_cont 2.8, R1 5.2; with NE42a |
| [G41](goalperiod-subhypotheses/G41/README.md) | exploratory | supported | 0.5/−0.7/2.4, Z_cont 3.2, R1 9.0; with NE42b |
| [G42](goalperiod-subhypotheses/G42/README.md) | exploratory | failed | −0.5/0.5/−1.3, R1 6.7 |
| [G44](goalperiod-subhypotheses/G44/README.md) | exploratory | failed | –/−0.1/−1.0; with NE31 |
| [G51](goalperiod-subhypotheses/G51/README.md) | exploratory | failed | –/1.9/−0.2, Z_cont 1.6; placebo 0/12 |

## Results
*Round 1, 2026-10-04; non-holdout only; 279 days (177 regime I, 9 II, 93 III), 61 placebo days (11 Monday placebos). Scripts: `scheme/build.py`, `analysis/evaluate.py`, `analysis/posthoc.py`, `analysis/figures.py`; outputs in `data/processed/H36-reorganization-alarm/` (`results.json`, `event_table.parquet`, `scores.parquet`, `posthoc.json`).*

**Headline.** The pre-registered physics alarm (multi-information, susceptibility and heat capacity, averaged over activity and content) **sees goal changes only weakly**: it fires within a day of 30% of them (10/33) at a 10% placebo-window false-alarm rate (3.3% per day), AUC 0.68 [0.56, 0.79], better than random dates (p 0.03). By the card's rule this is **mixed**. **All of the signal is in the content channel** (Z_cont AUC 0.77, no placebo false alarms; activity channel AUC 0.55, at chance). **The obvious first-moment detector beats it easily:** the day-to-day shift of the swarm's mean content vector (R1) has AUC 0.95. Scaffold changes are not detected (1/13, chance); room events 1/5; roster batches 3/6.

**Operating characteristics** (goal kickoffs, hit = alarm on day −1, 0 or +1; FAR on placebo days and 3-day placebo windows):

| Alarm | hit | window FAR | per-day FAR | AUC day 0 | Monday-placebo day FAR |
| --- | --- | --- | --- | --- | --- |
| **Z_phys ≥ 2.0 (pre-registered)** | 0.30 | 0.10 | 0.033 | 0.68 [0.56, 0.79] | 0.09 (1/11) |
| Z_cont ≥ 2.0 (content members) | 0.42 | 0.00 | 0.000 | 0.77 [0.67, 0.86] | 0.00 |
| Z_act ≥ 2.0 (activity members) | 0.27 | 0.11 | 0.033 | 0.55 [0.41, 0.66] | 0.09 |
| R1 ≥ 2.0 (centroid shift, rival) | 0.58 | 0.21 | 0.066 | **0.95** [0.90, 0.98] | 0.00 |
| R2 ≥ 2.0 (activity level, rival) | 0.45 | 0.23 | 0.082 | 0.59 | 0.09 |
| *post hoc:* R1 ≥ 3.0 or Z_cont ≥ 2.0 | 0.58 | 0.02 | 0.000 | – | – |

**What the content signal is.** The heat-capacity member C_cont (within-day variance of the swarm's content alignment) carries most of it (AUC 0.79 alone): on a kickoff day the agents' mutual alignment moves within the day. Post hoc (PH2), removing a linear within-day trend lowers Z_cont's AUC from 0.77 to 0.66 [0.54, 0.79], so about 40% of the above-chance signal is a monotone drift: the post-kickoff ordering H12 and H20 described (field-driven relaxation), not a coupling change. The rest is non-monotone co-fluctuation that the model cannot attribute.

**The activity channel.** Its kickoff hits (#8, #10, #16, #39) coincide with a day-length change (2 → 3 h), a roster batch join (N 4 → 7), a return from a held-out gap and a same-day join. On the 18 kickoffs without such sampling changes its AUC is 0.47 (PH3). Activity fluctuation statistics react to *who and how long*, not to *what*. This agrees with H04 (kickoffs don't change activity level) and the synthetic result that day-boundary field steps are invisible to them.

**Timing.** Of the 10 Z_phys hits, 6 fire first on day 0, 1 on day +1 and 3 on day −1. Post hoc (PH1), day −1 is weakly elevated against both placebos (AUC 0.69) and Friday placebos (0.68): a goal's last day shows some content co-movement (wrap-up). Alarms there are rare (13%), so this is a hint of a lead, not a usable early warning. The event-locked mean returns to baseline by day +1 (`figures/event_locked.pdf`).

**Stalls.** With H38's mask, the most stall-heavy placebo days (top decile of joint-silence share, n = 7) raised no false alarms, masked or unmasked. The unmasked score correlates weakly with joint-silence share (ρ 0.22, p 0.09); the masked one does not (0.02). The surrogate-excess, per-pair design already absorbs most of the stall effect at day resolution. Robustness: AUC 0.70 without the mask, 0.72 with H12's lull filter, 0.75 with 5-min bins.

**Rooms and scaffold.** The 05-04 merge did not raise activity coupling statistics (z −0.6), and the 05-11 split lowered them (z −3.0), but both steps were caught by content and R1 because they coincide with kickoffs. The 03-24 regime boundary (NE14), the largest scaffold change, produced no alarm, probably because the rollout was staggered from 03-11 (held out). NE17 and NE18 were silent, as predicted.

**Outcome vs prediction.**
| Prediction | Outcome | Verdict |
| --- | --- | --- |
| P0 synthetic expectations | S0, S3, S4, S6 met; S1 (0.40 < 0.8) and S5 (0.13 < 0.6) missed; S2 and S7 half | partly held |
| P1 goal hit ≤ 40%, window FAR 15–30%, AUC < 0.65 | hit 0.30; window FAR 0.10; AUC 0.68 | mostly held (the alarm is slightly better and quieter than predicted); card rule: **mixed** |
| P2 content > activity; C_cont, χ_cont up; activity at chance | 0.77 vs 0.55; mean day-0 z 2.2 and 1.1; activity 0.55 (0.47 clean) | held |
| P3 R1 AUC ≥ 0.8, beats Z_phys; adding Z_phys gains < 0.1 | 0.95; ΔAUC −0.26 [−0.39, −0.13]; R1 ∪ Z_phys gains +0.15 hit at +0.10 window FAR | first two held; third failed |
| P4 merge raises, splits lower activity χ/I | merge −0.6 (failed); 05-11 split −3.0 (held); 03-16 split −0.8 to −1.1 (partly) | mostly failed (n = 3) |
| P5 NE14 fires; other scaffold at chance | NE14 silent; 1/13 vs window FAR 0.10 | first failed, second held |
| P6 unmasked stalls cause ≥ 1/3 of false alarms; the mask lowers FAR | no unmasked false alarms at all on placebo days | failed |
| P7 per-day FAR in [0.03, 0.12]; Monday higher | 0.033; Monday 0.09 vs 0.02 (n = 11) | held (weakly) |
| P8 hits on day 0/+1, no day −1 signal | 7/10 on day 0/+1; day −1 AUC 0.69 (post hoc) | partly held |

**For an operator (the deliverable).** Measured, pre-registered: the physics alarm catches about a third of goal changes within a day, at roughly one false alarm per 30 quiet days, and none of the scaffold changes. As a "something structural is happening" alarm it is weak. What works (in-sample, post hoc; frozen as C3 for the holdout):
- Each day, compare the swarm's mean content vector with yesterday's (R1).
- Separately, measure how much the agents' content alignment moves within the day against a window-shuffled null (Z_cont).
- Alarm if R1 ≥ 3 trailing SDs, or Z_cont ≥ 2.

This caught 58% of goal changes at 1 false alarm in 61 placebo windows. The physics statistic earns its place here as the false-alarm filter: R1 alone needs a threshold of 2 to reach the same hit rate, and then it has 13× the false alarms (window FAR 0.21).

**Caveats.**
- **Resolution.** The test is daily only: lead and lag are in days, and mid-day room events can't be timed.
- **Few placebo days.** There are 61, from regime I (46) and III (15), and none from regime II. Zero false alarms in 61 bounds the per-day FAR at about 5% (95%).
- **Multiplicity.** 16 scores × 5 classes are reported, but only one primary test: Z_phys on goal changes. The operator rule was chosen post hoc among 7 candidates.
- **Confounds.** Goal kickoffs are mostly Mondays, and there are only 11 Monday placebos. 7 of 33 kickoffs coincide with room, roster or scaffold events.
- **R1 missing** on days after held-out days (#10, #16, #23, #30, #33, #35, #44, #51); a live operator would have yesterday's data.
- **Single embedding model** (bge-small); no swap yet.
- **H38's outage table** was used as built at 01:30 UTC, while H38 was still running.
- **"Behavior states"** here are the 4-state activity classes, not the Jev labels.
- **The synthetic generator is a toy.** Its power numbers depend on its day-to-day noise.

**Figures** (one-page summary: `figures/summary_obs.pdf`):
- `figures/event_locked.pdf`: mean z by day around kickoffs.
- `figures/roc_goal.pdf`: hit rate vs window false-alarm rate across thresholds.
- `figures/timeline.pdf`: daily Z_phys and Z_cont with all events marked.
- `figures/synthetic.pdf`: AUC per synthetic scenario.

## Round 2 redirects
**What the direction is really after:** a cheap, log-computable alarm for structural change in a swarm (goal, roster, room, scaffold) with known hit and false-alarm rates; round 1 says content carries it, activity fluctuations don't, and a first-moment topic-shift detector beats the physics statistics.
- **H36-R1. Holdout confirmation.** Run `analysis/confirm.py` (C1–C5) after committing the card and script and disclosing reuse in LOG.md and the affected cards.
- **H36-R2. Intraday alarm.** 30–60-min windows to time mid-day room events (05-04 16:07, 08-05) and to resolve lead vs lag within a kickoff day.
- **H36-R3. Sampling-invariant activity statistics.** Fixed-n agent subsamples and fixed-length windows, so day-length and roster changes stop firing the activity channel; otherwise drop activity from the alarm.
- **H36-R4. Embedding swap.** Recompute Z_cont and R1 with a second embedding model (e5-large) before trusting the operator rule.
- **H36-R5. Scaffold detector.** Change points in the action mix (tool, bash grammar, consolidation rate), since no daily swarm statistic here sees scaffold changes.

## Notes
- 2026-10-04: promoted from HH126 by Vivian (usefulness-first batch); wave 2.
- 2026-10-04 ~01:40 UTC: observables, nulls, alarm rule, synthetic plan and predictions P0–P8 written before any computation. ~01:50 UTC: Amendment 1 after the synthetic run. 01:51 UTC: G/NE prediction folders written, before any real-data statistic.
- 2026-10-04 ~01:52–02:15 UTC: real-data build, evaluation, post hoc PH1–PH4, confirm script (dry run only), figures, summary page.
