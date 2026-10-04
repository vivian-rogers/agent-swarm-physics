# H27: Critical slowing down warns of herding waves hours ahead

**Status:** exploratory round 1 done (2026-10-04); **round 1b on improved data done (2026-10-04): the negative stands** (shared deterministic labels give the same 21 onsets and AUC 0.62; work-commit onsets coincide with attention onsets; #40's pile-on runs in minutes, below the design's resolution). **Negative: critical slowing down does not warn of herding onsets.** 21 onsets in 14 non-holdout periods (15-min windows); only 8 are evaluable (6 h of well-observed history, starting from a low share). The composite trend (τ_AR1 + τ_SD) separates them from placebo segments weakly and fragilely (AUC 0.62 [0.51, 0.76] at 15 min; 0.44 at 30 min). Autocorrelation never rises, which is the defining sign of slowing down. The frozen alarm hits 5/21 onsets at 5.3 false alarms per active day, no better than a rate-matched random alarm (p = 0.07) or a naive share alarm. Synthetic validation shows that even a true fold is barely detectable at village size (AUC ≈ 0.6). Post hoc: onsets follow a chat link to the project (11/21 within 30 min; within-period p = 0.0005), consistent with announcement-driven pile-ons (H28). Predictions were written 2026-10-04 before the synthetic and real-data runs; the frozen holdout test is written, not run.
**Fields:** stat mech, sociophysics, info theory
**Origin:** HH109 (`../hypohypotheses/HYPOHYPOTHESES.md`; `../promotion-shortlist.md`). Related: HH114 (H28, links as the contagion vector, running in parallel), HH126 (reorganization alarm).
**Definitions used:** "Agent state (categorical)" in H11's named variant **agent state (categorical, project/artifact strict)** (H11 card, Data scheme; proposed there for DEFINITIONS.md); "Population N(t)", active-population variant (**n(w)** = agents with any project label in window w); "Regime" (every period used sits inside one regime; #36, which crosses 2026-03-24, is excluded); active time as in `infra/README.md` (village-on clock time, overnight and weekend gaps removed). New named variant proposed for DEFINITIONS.md: **herding onset (H27, project-share step)**, defined under Observables (O1).

## Question
Before H11's pile-ons (#31's time-capsule repo reaching 11 agents; #18's last-day convergence), the dominant project share's autocorrelation and variance should rise. *Check:* lag-1 autocorrelation and variance of the dominant share in rolling windows before vs after onsets, against placebo windows; lead time.

Practical aim (usefulness-first batch): produce a number or rule an operator of an LLM agent swarm could compute from logs and act on. Deliverable: an alarm rule with measured hit rate, false-alarm rate and lead time, or a clear negative.

## Model
**From:** `physics-models/10-potts` (kinetic, mean-field form) and `physics-models/01-inverse-ising` (mean-field susceptibility χ ∝ 1/(1 − slope), the fluctuation side of the same mean field).

**H27 variant: kinetic Curie–Weiss Potts with a neutral state and a slowly varying field.** Same state space as H11: σ_i ∈ {0, 1..q}, 0 = "other" (rare projects; uncoupled), 1..q = real projects. Each agent reconsiders at rate γ and picks

P(σ_i → a) ∝ exp( h_a(t) + βJ · k_a^(−i) / (N − 1) ) for a ≥ 1, ∝ 1 for a = 0,

with k_a^(−i) the number of other agents on a. The mean-field flow is dx_a/dt = γ (softmax_a(h(t) + βJ x) − x_a), with the neutral state carrying weight e^0.
- **Saddle-node (fold) route.** For βJ ≳ 4 (q = 5, others' fields −1) the share x_A of one project is bistable over a range of h_A. As h_A drifts up slowly, the low branch disappears at a fold; just before it, the leading eigenvalue of the linearized flow → 0 (critical slowing down). In mean field at βJ = 4.5, h_others = −1: fold at h_A ≈ −0.90, with the pre-jump share x_A ≈ 0.24 jumping to ≈ 0.90. Classic early-warning theory (Scheffer et al. 2009; Dakos et al. 2012) predicts rising lag-1 autocorrelation and variance, and skewness toward the new state, in the approach.
- **Routes with no warning by construction.** (i) *Noise-induced flips*: fixed parameters in the bistable range; at N ≈ 12 the swarm escapes the metastable state by a fluctuation, with no parameter drift and no slowing down. (ii) *Field steps*: an exogenous push (a repo link posted, a human or operator message, a day-start kickoff) shifts h_A abruptly. H11 could not separate fast common drive from coupling, so (ii) is a live rival.
- **Finite-N caveat.** At N ≈ 12 the barrier near the fold is a few units of noise, so even a fold-driven transition is partly noise-induced and happens before the deterministic fold. This is the main reason the indicators may fail at village size even if the mechanism is right.

## Data scheme (`scheme/`)
`scheme/build.py` builds `data/processed/H27-herding-early-warning/G<NN>/series_w{15,30}.parquet` from H11's processed project labels (`data/processed/H11-potts-labor-vs-herding/G<NN>/labels_project_w*.parquet`, `windows_w*.parquet`; imported via H11's `scheme/h11common.py`, never modified). For #44 and #51 (not built by H11) it calls H11's own builder functions (`load_calendar`, `window_table`, `build_project`, `label_projects`) into H27's data folder; #51 loses its locked tail (09-07 → 09-21) through `holdout_mask`.
- **Per window w** (global active-time index across the period's days; overnight gaps removed): n(w) labeled agents (any label, including "other"), k_a(w) agents on real project a (a = 1..q, H11's merged labels, q ≤ 8, ≥ 2% share), day, window-in-day.
- **Share series:** x_a(w) = k_a(w) / n(w); **unobserved** (NaN) if n(w) < 3.
- **Swarm level:** all rooms pooled (the operator watches the whole swarm). Rooms are not blocked here (unlike H11).
- **Window:** W = 15 min primary (16 windows per 4-h day, 32 per 8-h day); W = 30 min robustness arm.
- **Holdout:** every period is checked against `holdout.json` (`h11common.assert_not_holdout`, `common.holdout_mask`); the builder refuses holdout periods without `--allow-holdout`, which only `analysis/confirm_holdout.py` passes.
- **Output:** a few MB of parquet, `_provenance.json`.

## Candidate goal periods
Card candidates: #18, #31, #37, #41. **Pre-registered period set (coverage rule):** every non-holdout single-regime period with H11 labels (#2–#44, plus #51 outside its locked tail) in which ≥ 50% of W = 15 windows have n(w) ≥ 3. Periods failing at W = 15 but passing at W = 30 enter the W = 30 arm only. Periods with no onsets still contribute placebo segments, so they measure the false-alarm rate. Per-period folders: `goalperiod-subhypotheses/G<NN>/`.

## Observables
All per goal period at W = 15 unless stated; S, L, ℓ in windows.
- **O1, herding onset (pre-registered rule; "herding onset (H27, project-share step)").** Project a has an onset at window w0 if:
  1. x_a(w0) ≥ 0.5, k_a(w0) ≥ 3 and n(w0) ≥ 4;
  2. **step from a low baseline:** the mean of observed x_a over [w0 − 4, w0 − 1] is ≤ 0.25, with at least 2 of those 4 windows observed;
  3. **persistence (a wave, not a spike):** the mean of observed x_a over [w0, w0 + 3] is ≥ 0.4;
  4. **first crossing:** the earliest window satisfying 1–3; the same project can onset again only after condition 2 holds again.

  Flags: *day-start* (w0 in the first 2 windows of a day), *last day*. Swarm onsets = the union over projects.
- **O2, early-warning indicators** on the segment of x_a ending at t_e = w0 − ℓ, of length S = 24 (6 h of active time), lead offset ℓ = 4 (1 h) primary, also ℓ = 1, 2, 8:
  - detrend with a NaN-aware Gaussian kernel smoother (σ = 4 windows) → residuals r;
  - rolling windows of L = 12 inside the segment (13 values), each needing ≥ 9 observed windows:
    - **AR1**: lag-1 autocorrelation of r (≥ 6 observed consecutive pairs);
    - **SD**: standard deviation of r (the variance indicator);
    - **skew**: skewness of r;
    - **flicker**: up-crossings of x_a = 0.3 (transient visits toward the herded state);
  - **trend** of each indicator: Kendall τ_b against time over the rolling values (≥ 8 defined values; otherwise τ = 0, "no trend");
  - **composite** C = τ_AR1 + τ_SD (the conventional "both rising" score);
  - **levels:** flicker count in the whole segment.
  - **Matching condition** (both onset and placebo segments): the project is low at t_e, i.e. the mean of observed x_a over [t_e − 3, t_e] ≤ 0.3. Segments need ≥ 75% observed windows. Onsets failing these at a lead are *not evaluable at that lead* (reported).
- **O3, placebo segments:** for every real project a, segment ends t_e on a grid of every 2 windows, with the same S, the same matching condition, no onset of a inside the segment and none in (t_e, t_e + ℓ + 8].
- **O4, discrimination:** AUC (Mann–Whitney) of each indicator for onset vs placebo segments, pooled over periods; 95% CI from a period-cluster bootstrap (2,000 draws). Per-period AUCs where a period has ≥ 2 evaluable onsets.
- **O5, operator alarm (prospective; frozen before real data from the synthetic null).** At every window t with S windows of history, for every project a that is low at t (matching condition): alarm on a if τ_AR1 > τ* **and** τ_SD > τ*, with τ* the value giving a 5% alarm rate per (project, window) on the synthetic stationary null S0 at village sampling.
  - **Hit:** an onset of a at w0 is hit if the alarm on a is on at some t ∈ [w0 − 12, w0 − 1] (3 h horizon). **Lead time** = w0 − the earliest such t, in hours of active time.
  - **False alarm:** an alarm on a at t with no onset of a in (t, t + 12].
  - Reported: hit rate, false-alarm rate per (project, window), false alarms per active day, precision (PPV), median lead. Swarm-level version: OR over projects, hit = any onset within 12 windows.
- **O6, rival indicators (baselines an operator would use anyway):**
  - **naive level alarm:** x_a(t) ≥ 0.3 (a third of labeled agents already on a);
  - **naive momentum alarm:** k_a(t) − k_a(t − 2) ≥ 2;
  - **mean-rise control:** SD of binomially standardized residuals r / √(x̃(1 − x̃)/n) with x̃ ≥ 0.05 (removes variance that rises only because the share's mean rises);
  - the mean share over the segment's last 4 windows, as an AUC baseline.
- **O7, project-agnostic indicator (secondary):** the same O2 trends on the Simpson concentration C(w) = Σ_a x_a(w)², for segments before swarm onsets vs placebo segments with no onset of any project in (t_e, t_e + ℓ + 8] and max_a x_a(t_e) < 0.5.
- **O8, robustness:** W = 30 (S = 16, L = 8, horizon 6 windows); S/L = 16/8 and 32/16 at W = 15; σ = 2 and 8 detrending; leads ℓ = 1, 2, 8.

## Null / baseline
- **N1, placebo segments (primary)**: indicators in matched low-state segments not followed by an onset (O3). If critical slowing down does not precede onsets, AUC ≈ 0.5.
- **N2, rate-matched random alarm** (for O5): each project's alarm series circularly shifted within the period (500 shifts); the EWS hit rate must beat its distribution (p < 0.05).
- **N3, naive level and momentum alarms** (O6): EWS is useful only if it adds lead time or precision over just watching the share rise.
- **N4, mean-rise control** (O6): a variance "warning" that disappears after binomial standardization is a rising mean, not slowing down.
- **Synthetic nulls** (axis F): stationary kinetic Potts (S0), the same with slowly drifting fields (S0-drift), field steps (SS) and noise-induced flips (SN), all at village sampling. Indicators must be at chance where theory says they must be, and above chance in a fold scenario, before any real-data claim means anything.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** (R1) field-step onsets (exogenous push, no slowing down); (R2) noise-induced flips in a bistable Potts swarm (no parameter drift, no slowing down); (R3) rising-mean artifact (variance and flickering rise only because the share is already rising); (R4) naive level / momentum alarms.
**Locked holdout used for confirmation:** none yet. Targets and the frozen rule C1–C5 are under Results ("Confirmatory prediction"); `analysis/confirm_holdout.py` is written and dry-run, not run.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | States are H11's strict artifact mentions (attention, not necessarily work); onsets, shares and indicators are defined from fields and pre-registered. Coverage passes in 14 periods at 15 min (56–100% of windows observed), regime-I labels are sparse (≈ 3 per window in #18, #19). The same mapping runs in regimes I–III. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 0 | The fold mechanism needs a slow parameter drift. Instead 4/21 onsets land on projects never mentioned before and 11/21 follow a chat link to that project within 30 min (post hoc): fast pushes. **Time-rescaling fails:** the composite AUC is 0.62 at 15 min and 0.44 at 30 min. Markov order and update order not audited. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 0 | The composite beats placebo segments only at 15 min, barely (0.62 [0.51, 0.76], 8 onsets) and not at 30 min (0.44 [0.32, 0.60]). The frozen alarm does not beat a rate-matched random alarm at the pre-registered α (5 vs 3.1 hits, p = 0.07). |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | The critical-slowing-down signature (AR1 *and* variance rising together) is absent: τ_AR1 AUC 0.42 [0.29, 0.51], below chance, while τ_SD is 0.70 [0.50, 0.89]. Rising variance with falling autocorrelation is the mark of transient excursions, not slowing down. |
| E interventional | predicts the change across a natural experiment | 0 | Not attempted: there are too few onsets to compare across an NE. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Nine synthetic scenarios at village sampling (200 runs each). Null calibrated (0.46); noise-induced and field-step routes at chance, as theory says; a true fold at N = 12 gives only 0.58–0.62 even with perfect sampling; a clean N = 200 fold gives 0.75. So critical slowing down is barely identifiable at village size. Real-data AUC is stable across S/L and σ (0.59–0.69) but not across W. |
| G ground truth | agrees with known structure | 1 | Onsets reproduce H11's #31 waves (guardrails, time-capsule, operations handbook, event log), #30's shared site and #38's campaign repos. #18's last-day convergence is *not* an onset (no low baseline). #41's strong herding (H11) has no majority steps. |
| H comparative | beats the named rivals | 0 | R1 (fast pushes) fits better: 4/21 onsets have no precursor and 11/21 follow a link announcement (within-period p = 0.0005). R4: the naive level alarm matches the EWS hits (5/21) with 2.6× fewer alarms (1.4% vs 3.5% of watched windows). |
| I transfer | holds in other same-mode periods, including the holdout | 0 | The 15-min signal does not transfer to 30 min. Per period, only #31 (2 evaluable onsets) is high. Holdout not run. |

## Prediction
*Written 2026-10-04, before the synthetic validation and before running anything on real data.*

**What I had seen when writing this:**
- H11's round-1 results (card, G31/G18/G26 folders): #31 is a sequence of herding waves (the time-capsule repo peaked at 11 agents in one window), #18 converges on one repo on its last day, #26's runoff vote jumped within one window; H11's persistence P(same project next window) is 0.5–0.9 at 30 min.
- Structural sampling counts only: days, windows per day, and the mean number of labeled agents per window for H11's periods (e.g. #31 ≈ 9 per 15-min window; #18 ≈ 3; #38–#42 ≈ 7–11; regime-I periods before #17 < 1.7). No shares, onsets or time courses.

**My prior.** Critical slowing down needs a slow parameter drift toward a fold, a long enough record, and small enough noise. The village gives ~12 agents, ~9 labeled per 15-min window, 4-h days, and pile-ons that H11 found to be fast and possibly field-driven (a repo link or an announcement). Generic indicators are known to give many false alarms in short, noisy, non-stationary series. I expect a negative.

- **P0 (onset counts).** 10–25 onsets at W = 15 across the period set, concentrated in #31, #30, #38, #41, #42; ≥ 3 in #31; 0–1 in #18 (its last-day convergence may fail the coverage or baseline condition). About half evaluable at ℓ = 4 (enough history, low at t_e).
- **P1 (primary).** Pooled AUC of the composite C = τ_AR1 + τ_SD at ℓ = 4, W = 15.
  - **Supported** if AUC ≥ 0.70, the period-cluster 95% CI excludes 0.5, and AUC > 0.5 in ≥ 2/3 of periods with ≥ 2 evaluable onsets.
  - **Failed** if the CI includes 0.5 or AUC < 0.6.
  - **Mixed** otherwise.
  - **My call:** failed (AUC 0.45–0.62). Credence supported: 0.15.
- **P2 (which indicator, and why).** τ_SD and flickering will discriminate better than τ_AR1 (AUC_SD > AUC_AR1), because a share that is already creeping up has larger binomial variance and crosses 0.3 more often (R3). After binomial standardization (N4) the SD advantage shrinks to within 0.05 of 0.5. Skewness at chance.
- **P3 (operator rule, O5).** At the frozen τ*:
  - hit rate ≤ 0.4;
  - the real false-alarm rate per (project, window) exceeds the synthetic 5% (non-stationarity: day starts, drift);
  - it does not beat the rate-matched random alarm (N2, p ≥ 0.05);
  - it gives no more lead time than the naive level alarm.
  
  **Usefulness criterion (pre-registered):** the EWS alarm is useful only if, at a real false-alarm rate ≤ 5% per (project, window), its hit rate is ≥ 0.5, its median lead is ≥ 1 h, it beats N2 (p < 0.05), and its median lead exceeds the naive level alarm's by ≥ 30 min. Credence it passes: 0.10.
- **P4 (synthetic, axis F).**
  - Large-N positive control (N = 200, clean sampling, slow fold ramp): AUC of C ≥ 0.8.
  - Village sampling (N = 12, 15-min windows, p_obs 0.75, 10% mislabels), slow fold: AUC 0.55–0.70.
  - Noise-induced flips and field steps: AUC within 0.5 ± 0.07.
  - Drifting-field null: alarm rate above the stationary 5% (generic false alarms).
- **P5 (lead time).** If hits occur, median lead ≤ 1 h, not "hours ahead".
- **P6 (project-agnostic, O7).** The concentration series does no better than the project series (AUC within ±0.05 of P1's).

**Calibration notes from the synthetic validation** (appended 2026-10-04, after `analysis/synthetic.py` finished and before any real-data run; P0–P6 above are unchanged). 200 runs per scenario (100 for N = 200), N = 12, q = 5, γ = 2 h⁻¹, W = 15 min, 5 × 4-h days, p_obs = 0.75, 10% mislabels unless stated. Lead ℓ = 4 (1 h); AUC with run-cluster bootstrap 95% CI.
- **Frozen threshold:** τ* = 0.538 (5% alarm rate per watched (project, window) on S0; realized 4.7%).
- **Null calibration holds.** S0: composite AUC 0.46 [0.40, 0.51]. Drifting fields (S0-drift) do **not** raise the alarm rate (4.8% vs 4.7%): the Gaussian detrending absorbs day-scale drift. So P4's drift clause is already false in synthetic data, which is good news for the indicators.
- **A true fold at village size is barely detectable.** Slow fold: composite AUC 0.58 [0.53, 0.63]; fast fold 0.62 [0.57, 0.66]; fold with competing projects 0.62 [0.57, 0.67]. With *perfect* sampling at N = 12 it is still 0.58: the limit is finite-N noise and the 6-h record, not label sparsity. Detected onsets come a median ≈ 2 h *after* the mean-field fold (bottleneck plus noise).
- **No-warning routes are at chance, as theory says:** noise-induced flips 0.52 [0.45, 0.60]; field steps 0.55 [0.50, 0.59].
- **Positive control (N = 200, clean sampling) is weaker than I predicted.** The pre-registered O1 step rule catches only 1 of 100 large-N fold transitions, because a deterministic fold rises slowly (≈ 1.5 h from 0.25 to 0.5) through the bottleneck. Under the O1-slow variant (Amendment 1) the composite AUC is 0.75 [0.69, 0.80] (τ_SD 0.80, τ_AR1 only 0.59), below my ≥ 0.8.
- **The level carries more information than the trends.** The mean share over the last hour has AUC 0.75–0.81 in every fold scenario, versus 0.58–0.65 for the composite: R3/R4 dominate.
- **Operator view at τ\*** (fold scenarios, N = 12):
  - the EWS alarm hits 30–37% of onsets, median lead ≈ 2 h, PPV 5–9%, ≈ 2 false alarms per active day;
  - the naive level alarm hits 62–75%, lead 0.5 h, false-alarm rate 1–1.4%;
  - the momentum alarm hits 82–93%, lead 1–1.25 h, false-alarm rate 2.5–3.3% (10–12% on the S0 null).
  - On S0, where onsets are pure noise, the EWS alarm still "hits" 12%: that is the chance hit rate of an alarm on ~5% of windows.
- **Power consequence (stated before real data):** even if every village onset were a genuine fold, the expected composite AUC is ≈ 0.6. P1's "supported" bar (AUC ≥ 0.70) is above what a true village-size fold produces, so P1 will almost surely "fail" whatever the mechanism. A pooled AUC near 0.6 with a CI excluding 0.5 would be the most H27 could show here. I keep P1 as written and will report this reading alongside it.

**Amendment 1 (2026-10-04, after a 10-run synthetic pilot and before any real data; disclosed):**
- (a) The pilot fold (βJ = 4.5, competitor fields −1) let the four competitor projects order spontaneously at N = 12, swamping the fold. The main fold scenarios now use βJ = 6 with competitor fields −3.5 (MF fold at h_A = −2.46, pre-fold share 0.19 → 0.96, bistable range −3.28 … −2.46). The pilot setting is kept as "fold + competitors". The noise-induced scenario was moved to h_A = −2.75 (inside the bistable range) so that escapes happen within 5 days.
- (b) A secondary onset rule, **O1-slow**, takes the baseline 1 h earlier ([w0 − 8, w0 − 5] instead of [w0 − 4, w0 − 1]), so rises spread over up to ≈ 2 h still count. It is reported on real data as a secondary arm; O1 stays primary.

**Per-period expectations** are in each `goalperiod-subhypotheses/G<NN>/README.md`, written before running that period.

**What would count against my negative prior (i.e. for H27):** P1 supported, plus P3's usefulness criterion met. A positive AUC driven only by τ_SD or flickering that vanishes under N4, or that the naive level alarm matches, counts as R3, not critical slowing down.

**Holdout confirmation targets** (chosen now from `holdout.json`, before any real-data run; same coverage rule applied inside the script): #22 (free week, regime I, like #31), #28, #29, #32 (regime I), #34 (regime II), #45, #46, #47, #49, #50 (regime III), and the #51 tail (09-07 → 09-21). #43 and #48 are single days (no S-window history) and are skipped. Reuse disclosure: H11 has named #22, #28, #45 for its coupling-sign test (not run). H27's observable (onset timing and early-warning trends) is a different statistic that nobody has examined on those periods; reuse follows the policy in `../holdout.md`, and will be disclosed in both cards and LOG.md when run. The confirmatory rule is frozen after round 1 in `analysis/confirm_holdout.py`.

## Results by goal period
All periods were run on 2026-10-04, after each `G<NN>/README.md` prediction was written. Arm W = 15 min unless marked. "Evaluable" = enough history (24 windows) and low at the segment end, at lead 1 h. EWS = frozen alarm (τ_AR1 > τ* and τ_SD > τ*).

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G18](goalperiod-subhypotheses/G18/README.md) | candidate | descriptive (1 evaluable onset, percentile 0.46) | 4 onsets (prior 0–1), 3 onto projects never mentioned before; EWS 0/4; 30 min: AUC 0.37 |
| [G19](goalperiod-subhypotheses/G19/README.md) | transfer | descriptive (1 evaluable, 0.59) | 3 onsets; EWS 0/3 |
| [G30](goalperiod-subhypotheses/G30/README.md) | transfer | mixed (AUC 0.57, 2/4 hit) | 4 returns of the shared site repo; EWS and level alarm both warn the 2 late ones |
| [G31](goalperiod-subhypotheses/G31/README.md) | candidate | mixed (AUC 0.91 on 2 onsets, 1/4 hit) | 4 onsets = H11's waves; τ_SD up, τ_AR1 down; 2 onsets too early to evaluate |
| [G33](goalperiod-subhypotheses/G33/README.md) | transfer | descriptive (1 evaluable, no placebos) | 2 last-day handover onsets; EWS 2/2 but 17% false alarms |
| [G35](goalperiod-subhypotheses/G35/README.md) | transfer | descriptive | 0 onsets (prior 1–2) |
| [G37](goalperiod-subhypotheses/G37/README.md) | candidate | descriptive | 1 onset on day 1 (no history) |
| [G38](goalperiod-subhypotheses/G38/README.md) | transfer | descriptive (1 evaluable, 0.86) | 3 onsets in 17 days; EWS 0/3, level alarm 2/3 |
| [G39](goalperiod-subhypotheses/G39/README.md), [G40](goalperiod-subhypotheses/G40/README.md), [G42](goalperiod-subhypotheses/G42/README.md), [G44](goalperiod-subhypotheses/G44/README.md) | transfer / false-alarm | descriptive | 0 onsets each; EWS false alarms 1.0–3.3 per day |
| [G41](goalperiod-subhypotheses/G41/README.md) | candidate | descriptive | 0 onsets (prior 1–3): herding (H11 βJ +4.3) without majority steps |
| [G51](goalperiod-subhypotheses/G51/README.md) | false-alarm (tail held out) | descriptive | 0 onsets in 45 days; 462 EWS false alarms (≈ 10 per 8-h day) |
| [G17](goalperiod-subhypotheses/G17/README.md), [G20](goalperiod-subhypotheses/G20/README.md), [G24](goalperiod-subhypotheses/G24/README.md), [G25](goalperiod-subhypotheses/G25/README.md), [G26](goalperiod-subhypotheses/G26/README.md) | 30-min arm only | descriptive | onsets 0, 1, 0, 3, 1; one evaluable (#25, percentile 0.82); EWS 0 hits |

**Round 1b (2026-10-04):** every period folder has a `**Verdict (1b):**` line (shared labels; work-commit series from #30). No per-period verdict changes. Native: G31 (the wave in work; mixed), G40 (the hub wave at the minute clock; mixed).

## Results
*Exploratory round 1, 2026-10-04.*
- **Code:** `scheme/build.py`; `analysis/ews_core.py` (onset rule, indicators, placebo segments, operator scoring); `analysis/synthetic.py`; `analysis/explore.py`; `analysis/assemble.py` (base rates, rate-matched nulls for every rule, precursor counts; post hoc parts flagged); `analysis/period_folders.py`; `analysis/figures.py`; `analysis/confirm_holdout.py` (frozen, not run).
- **Data:** `data/processed/H27-herding-early-warning/` (`G<NN>/series_w*.parquet`, `G<NN>/round1_w*.json`, `results_round1.json`, `assemble_round1.json`, `segments_round1.parquet`, `onsets_round1.parquet`, `synthetic/`, `confirm_dryrun.json`). 6.5 MB.
- **Figures:** [`figures/H27_round1_summary.pdf`](figures/H27_round1_summary.pdf) (one-page figure summary); [`figures/synthetic_validation.pdf`](figures/synthetic_validation.pdf); [`figures/real_onsets.pdf`](figures/real_onsets.pdf); [`figures/summary_obs.pdf`](figures/summary_obs.pdf).

**Outcome vs prediction** (W = 15 min, lead ℓ = 1 h, unless stated)

| Prediction | Outcome | Verdict |
| --- | --- | --- |
| P0 onsets: 10–25; ≥ 3 in #31; 0–1 in #18; about half evaluable | 21 onsets in 7 of 14 periods; #31: 4; #18: 4; 8/21 evaluable (13 not: 6 too early, 5 too sparsely observed, 2 not low) | **Mostly as predicted** (#18, #19, #30 above their priors; #35, #41 below) |
| P1 composite AUC ≥ 0.70 with CI > 0.5 (supported) / CI includes 0.5 or AUC < 0.6 (failed) | 0.62 [0.51, 0.76], n = 8; both periods with ≥ 2 evaluable onsets > 0.5. 30-min arm: 0.44 [0.32, 0.60]. O1-slow: 0.73 [0.63, 0.81] (n = 10) | **Mixed by the rule** (my call was failed). Not robust to the window length |
| P2 τ_SD and flickering beat τ_AR1; SD advantage gone after binomial standardization; skew at chance | τ_SD 0.70, flicker 0.68, τ_AR1 0.42; binomial τ_SD 0.69; skew 0.55 | **Partly:** the ordering holds, but the SD signal survives standardization, so it is not just a rising mean |
| P3 alarm: hit rate ≤ 0.4; false-alarm rate above 5%; does not beat the rate-matched null; no more lead than the level alarm | 5/21 hits (5/12 watchable); 3.5% of watched (project, window) pairs; 5.3 false alarms per active day; PPV 1.4% (base rate 0.54%); rate-matched null 3.1 hits, p = 0.07; level alarm 5/21 at 1.4%; 30 min: 0/21 | **As predicted except the false-alarm rate** (3.5% < 5%). Usefulness criterion **fails** |
| P4 synthetic: N = 200 fold ≥ 0.8; village fold 0.55–0.70; noise / step within 0.5 ± 0.07; drift raises alarms | 0.75 (O1-slow; O1 cannot see slow rises); 0.58 (slow), 0.62 (fast); 0.52, 0.55; drift 4.8% vs 4.7% | **2 of 4 clauses** |
| P5 median lead ≤ 1 h | 1.25 h for EWS hits; 2.5 h for the level alarm (the earliest alarm in a 3-h horizon, so leads are inflated for any noisy alarm) | **Failed as written, uninformative** |
| P6 concentration series no better than project series | 2 evaluable swarm onsets; AUC 0.44 | **Untestable** |

**Synthesis.**
1. **No critical slowing down before herding onsets.** Where the 15-min composite separates onsets from placebos, it does so through variance and flickering while lag-1 autocorrelation *falls* (τ_AR1 AUC 0.42; 0.29 in #31, 0.12 in #38). Slowing down raises both. Rising variance with falling memory is what transient excursions look like: a few agents visiting a project before the crowd arrives. The signal is also fragile: 8 evaluable onsets, a CI lower bound of 0.506, and chance at 30 min (0.44).
2. **Most onsets cannot be warned by any share-based indicator.**
   - 13 of 21 were not evaluable: 6 came in the first 1.5 days, before 6 h of record exists; 5 had too sparse a record (regime-I labels); 2 did not start from a low share.
   - 4 landed on projects nobody had mentioned before in the period (3–8 agents in the first window): #18 ×3, #19 ×1.
   - The pile-ons the village shows are mostly fast pushes, not slow approaches to a fold.
3. **What precedes onsets (post hoc).**
   - **Links:** 11/21 onsets were preceded within 30 min by a chat link to that project, vs 2.7 expected from same-period placebo windows (Mantel–Haenszel OR 11.6, permutation p = 0.0005).
   - **Human messages:** no excess (2 vs 2.1).
   - **Automated messages:** no excess within periods.

   This favours rival R1 (announcement-driven onsets) and is H28's mechanism (links as the contagion vector).
4. **The synthetic validation explains why a negative was likely whatever the mechanism.** At N = 12, a genuine fold gives composite AUC ≈ 0.58–0.62, even with perfect sampling. Noise-induced flips and field steps give chance, as theory says. Only a clean N = 200 swarm reaches 0.75, and it needs the slow-rise onset rule. In every fold scenario the share *level* in the last hour (AUC 0.75–0.81) beats the trends.
5. **Operating characteristics** (15-min arm, 3-h horizon, 104 active days, 15,911 watched (project, window) pairs):

   | Alarm | Hits | Alarm rate | PPV | False alarms per day | Timing beyond a rate-matched shift |
   | --- | --- | --- | --- | --- | --- |
   | EWS (frozen τ* = 0.538) | 5/21 | 3.5% | 1.4% | 5.3 | 5 vs 3.1 (p = 0.07; 0.048 on a re-draw) |
   | Share ≥ 0.3 (level) | 5/21 | 1.4% | 4.1% | 2.0 | 5 vs 5.1 (p = 0.66) |
   | +2 agents in 30 min (momentum) | 6/21 | 2.2% | 2.9% | 3.2 | 6 vs 5.4 (p = 0.43) |

   The base rate is 0.54% (an onset of the watched project within 3 h). The naive alarms carry project information (lift 5–8 over the base rate) but no timing information. The EWS alarm carries at most marginal timing information and 2.6× more false alarms.
6. **Heterogeneity.** Onsets concentrate in regime I and in shared-artifact weeks (#18, #19, #30, #31, #33, #38). Own-artifact weeks (#39, #40, #42), the free week #37 after day 1, #41 and all of #51 have none. #51's 45 days produce 462 EWS false alarms and no onset.

**Operator-facing alarm rule (deliverable): a clear negative.**
- **Measured, frozen rule.** "Alarm on project a when, over the last 6 h of 15-min windows, both the rolling lag-1 autocorrelation and the rolling SD of a's detrended share trend up (Kendall τ > 0.538), while a is still below 30%."
  - On 14 village periods it warns 5 of 21 pile-ons, median lead 1.25 h.
  - It raises 5.3 false alarms per active day; 1 alarm in 70 is followed by a pile-on.
  - It is not reliably better than random alarms at the same rate, and it fails entirely at 30-min resolution.
- **Do not deploy it.** A naive "a third of active agents are already on it" alarm gets the same hits with fewer false alarms, and neither predicts *when*.
- **What did precede pile-ons** (post hoc, to be confirmed on the holdout and in H28) is a link to the project posted in chat in the previous half hour. That is a lead of at most 30 min, and links are posted far more often than pile-ons follow (≈ 4× within-period lift).

**Caveats.**
- **Power.** 21 onsets, 8 evaluable; the per-period AUCs rest on 1–2 onsets. The CIs are wide and the 15-min vs 30-min disagreement is within noise.
- **Multiplicity.** 8 indicators × 4 leads × 2 arms × 2 onset rules, plus robustness variants. Only P1 (the composite at 1 h, 15 min) was primary. The O1-slow 0.73 and the τ_SD 0.70 are secondary.
- **Labels are attention, not work** (H11): strict artifact mentions. Regime-I labels are sparse (≈ 3 per window in #18, #19), so k ≥ 3 onsets there are noisy.
- **The onset rule detects steps, not slow rises.** The synthetic N = 200 fold shows that O1 misses deterministic fold transitions. O1-slow was added (Amendment 1) and gives a higher but still fragile AUC (0.73 at 15 min, 0.50 at 30 min).
- **"Never seen before" means within the period's H11 labels** (top-8 projects, ≥ 2% share; the rest are "other"). A project could have been worked on under a different artifact name.
- **The link association is post hoc and partly mechanical.** A chat link by an agent also labels that agent for the project, though the onset rule requires a low baseline over the previous hour.
- **Placebos are dominated by #51** (5,658 of 7,854 segments at 1 h). The period-cluster bootstrap resamples periods, but the false-alarm rate is #51-weighted (#51 alone: 462 of 555 false alarms).
- Leads are measured from the earliest alarm in the 3-h horizon, which inflates the lead of any noisy alarm.

**Amendments, with what I had seen when making them:**
- **Amendment 1** (after the synthetic pilot, before any real data): the fold scenario parameters, and the O1-slow secondary rule. See the calibration notes under Prediction.
- **Amendment 2** (post hoc, after the round-1 run):
  - `analysis/assemble.py` adds base rates and lift, rate-matched nulls for the level and momentum alarms, the precursor counts (never seen before, no agents in the previous 1 h or 6 h), and the trigger check (human, automated and chat-link events in the previous 30 min vs same-period placebo windows, with a Mantel–Haenszel OR and a within-period permutation).
  - Google Docs / Drive ids are masked in figures and period folders.
  - The per-period notes were written after the run.
- **Not amended:** the onset rule, indicators, τ*, horizons and verdict rules are as pre-registered.

**Confirmatory prediction** (frozen 2026-10-04 after round 1, before any holdout data was read; `analysis/confirm_holdout.py`).
- **Targets:** #22, #28, #29, #32, #34, #45, #46, #47, #49, #50 and the #51 tail, under the same coverage rule. Same pipeline, W = 15 min, lead 1 h, frozen τ* = 0.538.
- **C1 (H27 as hypothesized):** composite AUC ≥ 0.70 with CI lower bound > 0.5. **Round 1 predicts not confirmed.**
- **C2 (the round-1 negative replicates):** composite AUC < 0.60 or CI includes 0.5.
- **C3 (no slowing down):** τ_AR1 AUC ≤ 0.55.
- **C4 (no operator value):** EWS hits do not beat the rate-matched null (p ≥ 0.05), or the naive level alarm hits at least as many onsets.
- **C5 (announcement precursor; post hoc in round 1):** chat link to the onset project in the previous 30 min, Mantel–Haenszel OR > 2 and within-period permutation p < 0.05.
- **Power rules:** C1–C3 need ≥ 5 evaluable onsets and C5 ≥ 5 onsets; otherwise "inconclusive (underpowered)".
- **Dry run** on non-holdout stand-ins #30, #31, #38 (chosen because they have onsets, so biased toward signal; a pipeline check, not evidence): C1 confirmed (0.74, n = 5), C2 not confirmed, C3 confirmed (τ_AR1 0.31), C4 confirmed, C5 confirmed (7/11; OR 10.0).
- **Safety:** the script refuses to run without `--confirm --i-understand-this-uses-the-locked-holdout` and without the card and code committed.
- **Reuse disclosure:**
  - #32 and #46–#50 lie inside windows H05 and H04 already used for confirmation (activity statistics);
  - #45 was used by H02 and H23;
  - #22, #28 and #45 are H11 targets.

  H27's statistics (project-label onset timing, early-warning trends, link precursors) are different and unexamined. To be disclosed in LOG.md and the other cards when run.

## Round 1b (improved data, 2026-10-04)

### What changed in the inputs
- **Project labels:** the shared deterministic `project_states` (through H11's round-1b files, `data/processed/H11-potts-labor-vs-herding/r1b/`) instead of H11's nondeterministic labels; 8.1% of W = 30 labels change (111 tie re-picks, 499 renumberings, 52 in or out of "other"). #51 labels now come from the same shared build.
- **New, work space:** onsets and indicators on **agent state (categorical, project, work ledger)** (H11's round-1b work labels: the repo with the most agent work commits per agent-window; DQ4 default filter), periods #30 onward.
- **Link precursor:** H28 and H53 reinterpret round 1's post-hoc link precursor (a project's *first* link seeds a wave; for known projects links mark bursts). The precursor count is re-run on the new onsets and split by first vs later link.
- **Code:** `scheme/build.py --labels shared --out data/processed/H27-herding-early-warning/r1b` (default keeps the round-1 path); `analysis/explore.py` reads `H27_DATA` (default: round 1's folder); `analysis/round1b.py` adds the work space and the native tests.

### Predictions for the new round-1b analyses
*Written 2026-10-04 07:28 UTC, before rebuilding anything for H27.* The pre-registered round-1 predictions are unchanged and are re-scored as written.

**What I had seen:** the round-1 results; the label-change counts; H28's and H53's headline results; H11's round-1b work-label row counts and #31's work-project table (top repos committed to by 11, 9 and 8 agents over the week).

- **R1b-1 (replication on shared labels).** P1 stays not supported (AUC < 0.70 or CI includes 0.5); τ_AR1 AUC ≤ 0.55; the onset count stays within 21 ± 4; the frozen alarm still does not beat the rate-matched null (p ≥ 0.05) or the naive level alarm matches its hits. Credence 0.8.
- **R1b-2 (work space, #30 onward).** Work labels give fewer onsets than attention on the same periods; too few are evaluable (≤ 4) for a work AUC, so P1 in work is untestable; where a project has onsets in both spaces, the work onset comes at or after the attention onset (median lag ≥ 1 window at W = 15).
- **R1b-3 (link precursor, re-run).** ≥ 40% of attention onsets follow a chat link to the project within 30 min (round 1: 11/21), and onsets after a project's *first* link are a minority of those (most are links to known projects, H28's "marks a burst").
- **R1b-4 (#31 work wave; native, `G31/`)** and **R1b-5 (#40 hub at the minute clock; native, `G40/`).** Predictions in those READMEs.

### Results (round 1b, run 2026-10-04)
Code: `scheme/build.py --labels shared --out …/r1b`, `analysis/explore.py` + `assemble.py` (`H27_DATA`, `H27_STATE`), `analysis/round1b.py` (`replicate`, `work`, `compare`, `estimates`), `analysis/figures_r1b.py`. Data: `data/processed/H27-herding-early-warning/r1b/` (`results_round1{,_work}.json`, `assemble_round1{,_work}.json`, `onsets_round1{,_work}.parquet`, `compare_r1b.json`). Per-period estimates in `per_period_estimates` (H27). The frozen τ* = 0.538 is reused unchanged.

**Layer 1, replication on shared labels (old → new).**

| Statistic | Round 1 | Round 1b |
| --- | --- | --- |
| Onsets W = 15 (evaluable at 1 h) | 21 (8) | 21 (8), the same per period |
| Composite AUC, W = 15 (P1) | 0.62 [0.51, 0.76] | 0.62 [0.50, 0.76] → **mixed by the rule, unchanged** |
| Composite AUC, W = 30 | 0.44 [0.32, 0.60] (21 onsets) | 0.50 [0.34, 0.65] (22 onsets) |
| τ_AR1 / τ_SD / binomial τ_SD AUC | 0.42 / 0.70 / 0.69 | 0.41 / 0.71 / 0.69 |
| O1-slow composite | 0.73 (n = 10) | 0.74 (n = 9) |
| Frozen alarm: hits, alarm rate, false alarms / day, PPV | 5/21, 3.5%, 5.3, 1.4% | 5/21, 3.3%, 5.1, 1.7% |
| Alarm vs rate-matched shift (N2) | p = 0.07 (0.048 on a re-draw) | **p = 0.038 (0.040 on a re-draw)** |
| Level alarm / momentum alarm | 5/21 at 1.4% / 6/21 at 2.2% | 5/21 at 1.4% / 6/21 at 2.2% |
| Onsets onto never-mentioned projects | 4/21 | 4/21 |
| Link to the project within 30 min before the onset | 11/21, OR 11.6, p 0.0005 | 11/21, OR 10.0, p 0.0005 |
| … of which the project's first-ever chat link / a link to a known project | – | 2/21 (OR 9.3, p 0.07) / 9/21 (OR 7.6, p 0.0005) |

- **R1b-1: supported.** P1 stays short of the bar, autocorrelation never rises (0.41), counts are identical. One sub-clause moves: the frozen alarm now beats its rate-matched shift at p = 0.038 (0.040 on a re-draw; round 1: 0.07 / 0.048). It is a borderline timing signal either way, and the naive level alarm still matches its 5 hits with 2.4× fewer alarms, so the operator verdict (do not deploy) and C4's "or" clause stand. P3's "does not beat the rate-matched null" clause, read literally, now fails narrowly.
- **R1b-3: supported.** 52% of onsets follow a link within 30 min, and 9 of those 11 are links to projects already known: H28's "links mark bursts" reading. Only 2 onsets follow a project's first link (H53's seed).

**Work space (#30 onward; R1b-2).**

| Labels | Onsets W = 15 (periods) | Evaluable | Composite AUC | Frozen alarm hits | Level alarm hits | Link within 30 min |
| --- | --- | --- | --- | --- | --- | --- |
| Attention, #30 onward | 14 (#30 4, #31 4, #33 2, #37 1, #38 3) | 4 | – | – | – | – |
| Work commits | 8 (#30 1, #31 2, #33 2, #41 2, #44 1) | 4 | 0.58 [0.13, 0.99] | 1/8 | 3/8 | 2/8 (OR 1.6, p 0.44) |

- **R1b-2: mostly supported.** Fewer work onsets (8 vs 14) and too few evaluable (4) for a work AUC (P1 untestable in work). For the 4 projects with onsets in both spaces, the work onset comes in the same 15-min window (3) or the next one (1): never before attention, median lag 0 (predicted ≥ 1 window). Work pile-ons are the same events as attention pile-ons, seen in commits. The link precursor does not carry over to work onsets (2/8).
- New work-only onsets: #41 `research-2026-05` (twice) and #44 `kimi-leader-finetune`: herding in commits that the attention rule did not flag (attention labels there are spread over more artifacts).

**Native layer.**
- **#31 (`G31/`; mixed):** 2 work onsets (time capsule, event log), each at lag 0 or +1 window from its attention onset; the frozen alarm misses both.
- **#40 (`G40/`; mixed):** at the minute clock the hub wave runs in minutes: first touch 1.9 min after the kickoff, first chat link 2.4 min, half the room 1.5 min after the link, half the room committing by 18.6 min (13/14 agents committed to it). No 15-min onset exists, so the early-warning design is structurally blind to it; work followed within ≈ 15 min (predicted ≥ 1 h).

**Verdict changes.** None at the card level: P1 mixed by the rule (failed in substance: no slowing-down signature), P2 partly, P3 as predicted except the false-alarm rate and, now, the narrow N2 clause; usefulness criterion fails. Per-period verdicts unchanged (#30 AUC 0.57 → 0.55, still mixed).

**Scorecard changes (round 1b):** none. G stays 1 (#31's work onsets reproduce two of its attention waves; the #40 kickoff wave is confirmed at the minute clock); C stays 0 (the alarm's N2 p = 0.038 is borderline and the level alarm matches it); H stays 0 (the field-step / announcement rival still fits better; links mostly mark bursts of known projects). Ratings suggested: complete 40 → 50, faithfulness 1.0, usefulness 2.0 (unchanged: the negative stands; the minute-clock result restates H53's operator rule: watch announcements, not trends).

## Round 2 redirects (proposed by the round-1 agent, 2026-10-04)
- **What the direction is really after:** Can an operator see a pile-on coming early enough to act, and from what signal?
- **H27-R1.** Model onsets as announcement-triggered cascades: hazard of a majority pile-on after a link post, by poster, room size and the project's prior share; joint with H28.
- **H27-R2.** Use a finer clock: per-turn project states from `actions` (minutes, not 15-min windows) so 6 h of history is not needed and the first 1.5 days become evaluable.
- **H27-R3.** Test the one regime where the theory says warnings can work: long, large swarms with slowly drifting incentives (#51 roles, if any shared project ever rises), with the slow-rise onset rule.

## Notes
- **2026-10-04, round 1b:** re-evaluated on the shared deterministic labels and the DQ4 work ledger (section "Round 1b" above). No verdict or scorecard changes; the alarm-vs-shift p moved from 0.07 to 0.038 (borderline).
- **From H28 (2026-10-04):** the post-hoc link precursor (11/21 onsets after a link) fits bursts *marked* by announcements: H28 finds links posted in the next hour predict switches better than past links (10/11 herding weeks), with a 3.3× pre-trend before first exposure. Links don't, by themselves, trigger onsets. H28's design excludes the "link labels its poster" artifact (posters' links count as their switch, recipients must be off X).
- 2026-10-04: promoted from HH109 by Vivian (usefulness-first batch); wave 1.
- 2026-10-04: model variant, scheme, observables, nulls and predictions written before the synthetic validation and before any real-data run.
- 2026-10-04: synthetic validation run; calibration notes and Amendment 1 appended before any real data.
- 2026-10-04: per-period predictions written (`goalperiod-subhypotheses/G<NN>/`), then round 1 run on 19 non-holdout periods (14 at 15 min, 5 more at 30 min only). Post hoc analyses (Amendment 2) flagged above.
- 2026-10-04: `analysis/confirm_holdout.py` frozen and dry-run on stand-ins; not run on the holdout.
