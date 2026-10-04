# H19: One curve for all periods: per-period loop gains collapse onto a function of an operational control parameter

**Status:** running. **Round 1b (2026-10-04, corrected `activity_bins`, DQ8 trim, H38 conditioning): P1 still fails, but round 1's channel opposition is withdrawn: the rising activity gain was the operator's day edges (slope on x_att +0.18 raw → −0.03 trimmed; regime III − I +0.17 → −0.03; NE14 adjusted Δ < 0). Day-edge-adjusted, all six re-estimated methods rise with messages per LLM step (post hoc). H04/H05 inputs dropped until their owners re-run them.** Round 1: **Exploratory round 1 done (2026-10-04): the pre-registered collapse P1 FAILED**, with no common curve: equal-time activity gains rise with x_att while Hawkes talk gains fall, and the regime-only rival wins out of sample. Within the talk channel, the Hawkes and equal-time gains agree with each other and with the derived mapping (P3 supported). A post-hoc talk-channel collapse on k_llm is frozen for confirmation (`analysis/confirm.py`, amended, not run). Not promoted. Predictions were written 2026-10-04 00:03 UTC, before any control parameter was related to any loop gain; not blind to other hypotheses' per-period numbers (disclosed).
**Fields:** stat mech, sociophysics
**Origin:** HH100 (`../hypohypotheses/HYPOHYPOTHESES.md`; `../promotion-shortlist.md`)
**Definitions used:** Population N(t); Regime; Interaction (broadcast; the shared `exposure` room rule); Action (turn-merged). **New here, proposed for `physics-models/DEFINITIONS.md`** (not edited, outside H19's scope): *loop gain (equal-time)*, *loop gain (Hawkes)*, *attention load k̄* and *agent turn (village)*, defined under Model and Observables.

## Question
Every hypothesis now produces per-goal-period coupling estimates: H02 Curie–Weiss βJ₀, H03 branching ratio n̂ and fast cross-triggering, H04 loop gain K, H05 J_in/J_out, and soon H10–H18. Do they collapse onto a single function of an operational control parameter, such as N, messages per agent-turn, hours per day, rooms, or the coupling mode of the goal? A collapse would be the swarm's phase diagram and would predict coupling from operating conditions. Practical payoff: forecasting a swarm's collective regime from its configuration.

## Model
**From:** `physics-models/01-inverse-ising` and `09-hawkes` (mean-field loop gain βJ₀(1−m²), branching ratio n), `02-nonequilibrium-ising`. Finite-size scaling and data-collapse methodology. Hierarchical (partial-pooling) meta-regression across periods is the allowed exception (d) of the per-period rule: every period keeps its own estimate, and the meta-regression only relates those estimates to the period's control parameters.

### Which "loop gains" are the same quantity (derived 2026-10-03)
All of these are the gain of the linear feedback loop of the collective mode in mean-field theory, but with different normalizations and timescales.

1. **Curie–Weiss (H02, MF-a).** The fluctuation relation N Var(m) = q / (1 − βJ₀q) gives g_CW ≡ βJ₀q = 1 − 1/VR, where VR = Var(Σᵢ sᵢ) / Σᵢ Var(sᵢ) is pooled within (day, 30-min block). H02 stores βJ₀; the loop gain is βJ₀·q.
2. **Mean-field Glauber (H04-MF).** τ = τ₀/(1 − K) with K ≡ βJ₀(1 − m²) = 1 − 1/VR (heterogeneous single-agent fields). This is **the same functional as (1)**. Only the field removal differs: H04 subtracts a 61-min centered moving average, H02 subtracts 30-min block means.
3. **Two-block mean field (H05-MF).** g = v̄ Σⱼ Jᵢⱼ, with J from naive inversion of the block-averaged excess-correlation matrix (cross-day surrogate subtracted). For one block with uniform excess correlation r: v Σⱼ Jᵢⱼ = (N−1)r / (1 + (N−1)r) = 1 − 1/VR_excess. So **H05's g is again 1 − 1/VR**, on standardized excess correlations of the room-labelled agents, generalized to two blocks.
4. **Hawkes (H03, H04).** n = spectral radius of the branching matrix = the endogenous fraction; long-window collective susceptibility 1/(1 − n)² (count Fano factor). To first order in the kernel, counts in bins of width Δ have
   Cov(Nᵢ, Nⱼ)_Δ = λⱼΔ ∫ φᵢⱼ(τ)(1 − τ/Δ)₊ dτ + (i ↔ j), so
   **VR_Δ = 1 + 2 n_x(Δ) / (1 + 2 n_s(Δ))** and **K_Δ = 1 − 1/VR_Δ = 2n_x(Δ) / (1 + 2n_x(Δ) + 2n_s(Δ))**,
   where n_x(Δ) = n_x·w and n_s(Δ) = n_s·w are the cross- and self-offspring per event that land in the same bin. For an exponential kernel with timescale τ_k, w(Δ/τ_k) = 1 − (τ_k/Δ)(1 − e^{−Δ/τ_k}); with H03's fast kernels (τ ≈ 10–30 s) and Δ = 60 s, w ≈ 0.6–0.85 (0.75 at 15 s).

**Consequences.**
- {H02 g_CW, H04 K, H05 g, H19's own g_eq} are one estimand (1 − 1/VR) under different detrending, spin and population choices. They should agree up to affine maps.
- Equal-time gains see only the **fast cross part** of the Hawkes branching matrix. H03's fast n_x maps onto g_eq through the formula above; this is an unfitted cross-method prediction (P3).
- Hawkes total n̂ = n_s + n_x + slow parts is a different normalization (offspring per event, all lags, including self-excitation). It tracks the equal-time gains only if n_s and the slow parts are constant across periods.
- The formula is for counts. For binary spins it holds when the per-bin occupancy is low (talk spins). For active spins (occupancy 0.5–0.8), saturation shrinks the gain and common fields faster than the detrending window add to it.

### The collapse model: attention dilution (H18 / HH99)
Each agent, at each **turn** (the moment it next sees the room, the shared `exposure` convention), finds k unread agent messages. It has a fixed response budget b per turn and spreads it over them, so a given message gets a response from a given recipient with probability b/(1 + k). Summing over the N_room − 1 recipients:

  n_x = b · x_att, with **x_att = (N_room − 1) / (1 + k̄)**, the number of attended partners per unit attention.

Then n̂ = (n_s + n_slow) + b·x_att and, for small gains, g_eq ≈ 2w·b·x_att + (common fast fields). With k̄ ≈ (N_room − 1)·m (m = messages per agent-turn from each partner), x_att → 1/m at large k̄: **per-message loop gain is inversely proportional to messages per agent-turn**. The model predicts that every loop gain is affine-increasing in x_att, with method-specific intercepts (self and slow parts, common fields) and positive method-specific scales (w, binary-spin saturation, normalization). That is the "one curve": after per-method affine maps, all methods fall on g ∝ x_att.

## Data scheme (`scheme/`)
Three scripts; all exploratory work masks the locked holdout (`calendar.holdout` and `infra/shared/common.py: holdout_mask`; asserted in code).
- **`scheme/build_controls.py`** → `controls.parquet`, `controls_days.parquet`: per-period control parameters from shared tables (`calendar`, `roster`, `events_core`, `actions`, `chat_core`, `exposure`) and the mode codes of `../hypohypotheses/goal-periods.md`.
- **`scheme/build_estimates.py`** → `estimates_window.parquet` (one row per estimate window: chunk, week, room window) and `estimates.parquet` (one row per period × method; windows inside a period combined by inverse-variance weighting). Sources:
  - H02 `mf_cw.parquet` (g = βJ₀·q per chunk; SE = surrogate SD × q);
  - H03 `period_table.parquet` (n̂ TALK and ALL under B2 with day-bootstrap or profile CI; fast n_x, n_s, per-pair n_x);
  - H04 `explore_placebo_switch.json` (Hawkes n and detrended K per ISO week; weeks with ≥ 80% of their days in one period; SE from the adjacent same-hours week-to-week spread, an upper bound);
  - H05 `mf_blocks.json` (two-block loop gain, talk and active), with day-bootstrap SEs recomputed by calling H05's own `block_J` read-only on its `pair_day_bin1.parquet`;
  - **H19's own equal-time estimator g_eq** (H02's Curie–Weiss VR on 30-min blocks, H02's chunking and population rules) for every non-holdout period, active and talk spins, day-bootstrap SE. It reproduces H02's chunks exactly (validation) and fills the 20 periods H02 did not fit.
  - **Ingest hook for H10–H18:** any `data/processed/H*/per_period_estimates.parquet` in the proposed shared schema (see Notes) is picked up automatically.
- **Output:** `data/processed/H19-loop-gain-collapse/` (`controls*.parquet`, `estimates*.parquet`, `results/*.json`, `synthetic/*.parquet`, one `G<NN>/` per period with that period's inputs and residuals), with `_provenance.json`.

## Candidate goal periods
All 35 non-holdout periods (282 days): #2–8, 10–13, 16–21, 23–27, 30, 31, 33, 35–42, 44, 51 (#51 without its held-out tail). Held-out periods are the out-of-sample test (confirmatory, not run); see "Confirmatory design".

## Links to other hypotheses
Synthesizes H02–H05 now, and H10–H18 as they report. Overlaps with the phase-diagram ideas in `../hypohypotheses/phase-diagrams.md`. P4 is H18's mechanism tested at the period level.

## Observables
*Written 2026-10-04 00:03 UTC.*
- **O1. Per-period loop gains** y_pm ± s_pm, for methods m in two families:
  - equal-time (E): **E1 `H19.geq_active`** (primary E; all 35 periods), E2 `H19.geq_talk`, E3 `H04.K_week`, E4 `H05.g2b_talk`, E5 `H05.g2b_active`; `H02.gcw_active` is the same estimator as E1 and is used only to validate it;
  - triggering (T): **T1 `H03.n_talk`** (primary T; B2 baseline, 35 periods), T2 `H03.n_all`, T3 `H03.nx_fast` (fast cross-agent offspring per event), T4 `H04.n_week`.
- **O2. Control parameters** per period (definitions in `scheme/build_controls.py`):
  - N_roster, N_active, N_room (room size a message reaches), n_rooms;
  - messages per agent-turn m_turn (two turn definitions: *village* = agent events in `events_core` other than session start/stop, merged within 1 s, the `exposure` notion of "next turn"; *LLM step* = also every `actions` row), messages per agent-hour m_hour;
  - **attention load k̄** = agent messages delivered to a roster agent (room rule) per turn;
  - documented and empirical hours/day; regime (I/II/III, majority of days); coupling mode (C/I/K/M/F, goal-periods.md); share of humans (and of the `automated` bot) in chat; calendar date;
  - **x_att = (N_room − 1)/(1 + k̄_village)** (primary), x_att with LLM-step turns (secondary).
- **O3. Collapse statistics** per candidate control x: REML random-effects meta-regression per method (slope c_m with 95% CI, residual heterogeneity τ²_m, R²_het = 1 − τ²(x)/τ²(intercept only)); a joint model across methods (per-method affine maps plus a shared period random effect u_p); **leave-one-period-out (LOPO) expected log predictive density (ELPD)** of every model; the collapse quality Q = mean squared standardized residual around the master curve after per-method affine maps.
- **O4. Cross-method concordance:** Spearman ρ between methods' period-level estimates on shared periods, raw and after x.
- **O5. Mapping check (unfitted):** g_eq,talk vs ĝ_map = 2w n_x/(1 + 2w(n_x + n_s)) from H03's fast n_x and n_s, w = 0.75 (band 0.6–0.85).

## Null / baseline
*Written 2026-10-04 00:03 UTC, before fitting.* Every rival keeps per-method intercepts and the same likelihood (Gaussian with each estimate's SE plus a per-method τ²), so the comparison is about the period structure only.
- **N0, no period structure:** per-method constants.
- **N1, regime-only step functions:** per-method intercepts for regimes I / II / III. *Strong rival:* x_att is higher in regime III by construction of the scaffold, so only within-regime variation separates N1 from the collapse.
- **N2, era trend:** per-method linear trend in calendar date.
- **N3, size only:** per-method slope on log N_roster (H03's empirical correlate, ρ = −0.53).
- **N4, no common curve (method-specific):** each method gets its own slope sign, or its own best control parameter. Evidence for N4: slopes of opposite sign across methods, or different winning control parameters per method.
- **Synthetic nulls (axis F):** the whole decision procedure re-run on data simulated with the real design (periods, methods, SEs, controls) under N1, N2 and N4.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** regime-only step functions (N1); era trend (N2); size-only (N3); no common curve / method-specific curves (N4).
**Locked holdout used for confirmation:** none. Eligible cells listed under "Confirmatory design"; script amended 2026-10-04 (see Notes).
**Level:** below "descriptive" (C = 0). P1 refuted in exploration; not promoted.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Every loop gain and control is defined from shared tables. The Hawkes ↔ Curie–Weiss ↔ two-block mapping is derived (Model), and H19's own estimator reproduces H02 exactly (max diff 4×10⁻¹⁶). **Not invariant:** turn-based controls change meaning with the scaffold (LLM steps per message rise sharply in regime III), and the activity and talk channels move in opposite directions across regimes. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Gaussian REML meta-regression with Knapp–Hartung CIs; per-period SEs from day bootstraps, H03 profile/bootstrap CIs (floor 0.02) and H04 week-to-week spread (an upper bound). Within-period stationarity is inherited from the source hypotheses, not re-audited. Methods share raw events, so summing LOPO ELPD over methods over-counts evidence. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 0 | LOPO (period-blocked) ELPD summed over 9 methods: the collapse beats only the constant (+5.3 nats) and loses to regime-only (−11.5), era (−10.3) and log N (−7.4). |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | **P3 (unfitted cross-method mapping) passes:** g_eq,talk tracks the Hawkes-mapped gain from H03's fast n_x and n_s (ρ = 0.44, p = 0.009), and exceeds it in 91% of periods (median ratio 2.3: common fast fields). The primary collapse signature (one sign) fails. |
| E interventional | predicts the change across a natural experiment | 1 (round 1b; round 1: 0) | Round 1: not attempted. **Round 1b:** NE43's dated prediction held (the day-edge part of the activity gain does not follow the bookend messages); NE42 (room A-B-A) and NE14 (regime II → III) did not support the round-1 readings. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 | The P1 rule on 150 synthetic data sets per truth, with the real periods, SEs and controls: false "supported" ≤ 0.01 under null, regime, era, log N, opposite-sign and different-control truths; power 0.87 at R² = 0.5 (1.00 at 0.75, 0.23 at 0.25). "Mixed" is uninformative (rivals give it 49–59% of the time). The real verdict is robust to dropping G51, dropping periods under 4 days, and LLM-step turns. |
| G ground truth | agrees with known structure | 1 | **Round 1b:** the scaffold switch remains the main structure for the talk/Hawkes gains, but the activity rise was day edges (adjusted regime III − I −0.03). Round 1: The 2026-03-24 scaffold switch shows up as the main structure. Regime III − I: talk gains fall (n̂ −0.22 [−0.38, −0.06], fast n_x −0.06 [−0.10, −0.03]) while activity co-activation rises (g_eq active +0.11 [+0.05, +0.18], H04 K +0.10 [+0.01, +0.20]), consistent with H02, H03 and H04 separately. |
| H comparative | beats the named rivals | 0 | Loses to N1, N2 and N3. The N4 signature (opposite-sign slopes) is present. Nested per-method selection of the best control (N4 as a predictive model) does not win either (ELPD 124.4 vs 147.8 for common x_att and 157.8 for regime-only): selection overfits at 8–35 periods. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Not tested; the holdout was not used. |

## Prediction
*Written 2026-10-04 00:03 UTC, after building the control-parameter table (`controls.parquet`) and after reading the other hypotheses' published per-period numbers, but **before any control parameter was correlated, plotted or fitted against any loop gain**.*

**Disclosure (not blind).** I had read: H03's per-period n̂ (falls with N, ρ = −0.53; lower in regime III); H02's βJ₀ (higher in regime-III mode-C chunks); H04's K(I) = 0.11 < K(III) = 0.26 and its holdout NE21 result (n higher on 8 h days); H05's talk loop gains 0.06–0.25. From the controls table I had seen that x_att(village) is higher in regime III (≈1.1–2.2) than in regime I (≈0.8–1.2). The predictions follow the theory above, not these impressions; my credences (in brackets) do use them.

- **P1 (primary: the collapse), on x_att = (N_room − 1)/(1 + k̄_village).** All of:
  - **(a) sign:** the meta-regression slope c_m > 0 for both primary methods (T1 `H03.n_talk`, E1 `H19.geq_active`), with 95% CIs excluding 0, and no method among E2–E5, T2–T4 with a slope significantly < 0;
  - **(b) heterogeneity explained:** R²_het ≥ 0.25 for both primary methods;
  - **(c) beats the rivals out of sample:** the joint collapse model's LOPO ELPD exceeds N0, N1, N2 and N3 by > 2 nats, and, with regime intercepts added, the x_att slope stays > 0 in both primary methods (within-regime collapse; this is what separates it from N1).

  Verdict: **supported** if (a), (b) and (c) hold; **mixed** if (a) holds with one of (b) or (c); **failed** otherwise. *Against it:* opposite-sign slopes between the families (the N4 signature), R²_het < 0.1, or N1/N2/N3 winning the LOPO comparison. [credence 0.2]
- **P2 (within-family concordance).** Within each family, methods agree on which periods are high: Spearman ρ ≥ 0.4 between every pair of methods with ≥ 8 shared periods, and between each method and its family's primary. Fails if any pair with ≥ 8 shared periods has ρ ≤ 0. [E: 0.5; T: 0.4]
- **P3 (cross-family mapping, unfitted).** Across periods, g_eq,talk (E2) and the Hawkes-mapped ĝ_map from H03's fast n_x and n_s co-vary (Spearman ρ > 0.3), and g_eq,talk ≥ ĝ_map(w = 0.6) in ≥ 2/3 of periods (equal-time gains add common fast fields to the triggering). Fails if ρ ≤ 0 or g_eq,talk < ĝ_map(w = 0.85) in most periods. [0.45]
- **P4 (dilution exponent, H18 at the period level).** The per-pair fast cross-triggering n_x/(N_active − 1) (H03 `n_c_pair_fast`) scales as (1 + k̄_village)^−α with α ∈ [0.5, 1.5] (95% CI overlapping 1), and log(1 + k̄) beats log(N_active − 1) as the predictor in LOPO ELPD. [0.35]
- **P5 (no mode effect beyond x).** With x_att in the model, adding coupling mode (C vs. others) does not improve LOPO ELPD for either primary method, and the mode-C coefficient's 95% CI includes 0. [0.7]
- **Scan (exploratory, labelled).** All control parameters in O2 are ranked by LOPO ELPD, per method and jointly. Holm correction over the slope tests; only P1–P5 carry verdicts.

**Confirmatory design (`analysis/confirm.py`, written, NOT run).** It freezes the exploratory collapse model (coefficients, τ², method maps) to `data/processed/H19-loop-gain-collapse/results/frozen_model.json`. With `--confirm --i-understand-this-uses-the-locked-holdout` it:
1. computes the control parameters of the held-out periods (same code);
2. writes sealed predictions with 90% prediction intervals and a SHA-256 hash, before any loop gain is estimated there;
3. estimates E1/E2 (H19's own g_eq) on the held-out periods and scores them. Hawkes predictions (T1) are scored only when a per-period n̂ appears in the shared schema from H03's own confirmatory run.

Pass rule: ≥ 70% of eligible held-out estimates inside their 90% intervals **and** the collapse model's held-out RMSE below the regime-step rival's. Eligible = held-out periods whose loop gains nobody has estimated: #1, #9, #14, #15, #22, #28, #29, #32, #34, #43 and the #51 tail; #45 for Hawkes only (H02 already computed #45's Curie–Weiss gain); #46–#50 excluded (H04 computed n and K on the NE21 segments).

## Results by goal period
Per-period verdict rule (written in each G card before the fit): the collapse model fitted without the period must put both primary estimates inside their 90% LOPO intervals (i) and predict the period at least as well as the regime-only rival (ii). **12 supported, 19 mixed, 4 failed (G02, G11, G40, G51).** Per-period intervals are wide, so most periods cannot reject the curve on their own; the cross-period tests below carry the weight. In the 9 regime-III periods (all with x_att above the median), n̂ TALK sits *below* its cross-period median in 8 and g_eq active sits *above* its median in all 9: the opposite-sign pattern, period by period.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G02](goalperiod-subhypotheses/G02/README.md) | exploratory | failed | x_att 0.81, k_llm 0.94; n̂ TALK 0.72 (LOPO pred 0.43); g_eq active 0.23 (LOPO pred 0.07); log density vs regime-only -0.46 |
| [G03](goalperiod-subhypotheses/G03/README.md) | exploratory | mixed | x_att 0.85, k_llm 1.44; n̂ TALK 0.66 (LOPO pred 0.43); g_eq active 0.02 (LOPO pred 0.09); log density vs regime-only -0.22 |
| [G04](goalperiod-subhypotheses/G04/README.md) | exploratory | mixed | x_att 0.80, k_llm 0.62; n̂ TALK 0.55 (LOPO pred 0.45); g_eq active 0.10 (LOPO pred 0.08); log density vs regime-only -0.66 |
| [G05](goalperiod-subhypotheses/G05/README.md) | exploratory | supported | x_att 0.78, k_llm 0.53; n̂ TALK 0.15 (LOPO pred 0.47); g_eq active -0.07 (LOPO pred 0.08); log density vs regime-only +0.36 |
| [G06](goalperiod-subhypotheses/G06/README.md) | exploratory | supported | x_att 0.81, k_llm 0.32; n̂ TALK 0.65 (LOPO pred 0.44); g_eq active 0.00 (LOPO pred 0.09); log density vs regime-only +1.71 |
| [G07](goalperiod-subhypotheses/G07/README.md) | exploratory | mixed | x_att 0.83, k_llm 0.36; n̂ TALK 0.47 (LOPO pred 0.45); g_eq active 0.08 (LOPO pred 0.08); log density vs regime-only -0.18 |
| [G08](goalperiod-subhypotheses/G08/README.md) | exploratory | supported | x_att 0.82, k_llm 0.28; n̂ TALK 0.27 (LOPO pred 0.46); g_eq active 0.03 (LOPO pred 0.09); log density vs regime-only +1.52 |
| [G10](goalperiod-subhypotheses/G10/README.md) | exploratory | mixed | x_att 0.78, k_llm 0.68; n̂ TALK 0.22 (LOPO pred 0.47); g_eq active 0.29 (LOPO pred 0.07); log density vs regime-only -0.91 |
| [G11](goalperiod-subhypotheses/G11/README.md) | exploratory | failed | x_att 0.92, k_llm 1.06; n̂ TALK 0.61 (LOPO pred 0.43); g_eq active 0.30 (LOPO pred 0.09); log density vs regime-only -0.45 |
| [G12](goalperiod-subhypotheses/G12/README.md) | exploratory | mixed | x_att 0.97, k_llm 1.69; n̂ TALK 0.63 (LOPO pred 0.42); g_eq active 0.17 (LOPO pred 0.10); log density vs regime-only -0.53 |
| [G13](goalperiod-subhypotheses/G13/README.md) | exploratory | supported | x_att 0.85, k_llm 0.93; n̂ TALK 0.57 (LOPO pred 0.44); g_eq active 0.03 (LOPO pred 0.09); log density vs regime-only +0.05 |
| [G16](goalperiod-subhypotheses/G16/README.md) | exploratory | mixed | x_att 0.97, k_llm 0.85; n̂ TALK 0.59 (LOPO pred 0.42); g_eq active 0.28 (LOPO pred 0.10); log density vs regime-only -0.31 |
| [G17](goalperiod-subhypotheses/G17/README.md) | exploratory | mixed | x_att 1.22, k_llm 1.16; n̂ TALK 0.48 (LOPO pred 0.38); g_eq active 0.12 (LOPO pred 0.13); log density vs regime-only -1.48 |
| [G18](goalperiod-subhypotheses/G18/README.md) | exploratory | mixed | x_att 1.02, k_llm 1.48; n̂ TALK 0.70 (LOPO pred 0.41); g_eq active 0.08 (LOPO pred 0.11); log density vs regime-only -1.07 |
| [G19](goalperiod-subhypotheses/G19/README.md) | exploratory | mixed | x_att 0.97, k_llm 0.99; n̂ TALK 0.69 (LOPO pred 0.41); g_eq active 0.11 (LOPO pred 0.10); log density vs regime-only -1.02 |
| [G20](goalperiod-subhypotheses/G20/README.md) | exploratory | mixed | x_att 1.00, k_llm 0.84; n̂ TALK 0.62 (LOPO pred 0.41); g_eq active 0.04 (LOPO pred 0.11); log density vs regime-only -0.86 |
| [G21](goalperiod-subhypotheses/G21/README.md) | exploratory | mixed | x_att 1.08, k_llm 0.98; n̂ TALK 0.68 (LOPO pred 0.40); g_eq active 0.09 (LOPO pred 0.12); log density vs regime-only -0.28 |
| [G23](goalperiod-subhypotheses/G23/README.md) | exploratory | supported | x_att 0.93, k_llm 0.53; n̂ TALK 0.10 (LOPO pred 0.44); g_eq active 0.04 (LOPO pred 0.10); log density vs regime-only +0.54 |
| [G24](goalperiod-subhypotheses/G24/README.md) | exploratory | supported | x_att 0.94, k_llm 0.51; n̂ TALK 0.13 (LOPO pred 0.44); g_eq active -0.00 (LOPO pred 0.10); log density vs regime-only +0.49 |
| [G25](goalperiod-subhypotheses/G25/README.md) | exploratory | mixed | x_att 0.99, k_llm 1.06; n̂ TALK 0.38 (LOPO pred 0.42); g_eq active 0.05 (LOPO pred 0.11); log density vs regime-only -0.30 |
| [G26](goalperiod-subhypotheses/G26/README.md) | exploratory | supported | x_att 0.96, k_llm 1.21; n̂ TALK 0.56 (LOPO pred 0.42); g_eq active 0.21 (LOPO pred 0.10); log density vs regime-only +0.65 |
| [G27](goalperiod-subhypotheses/G27/README.md) | exploratory | supported | x_att 0.94, k_llm 0.62; n̂ TALK 0.41 (LOPO pred 0.43); g_eq active 0.14 (LOPO pred 0.10); log density vs regime-only +1.49 |
| [G30](goalperiod-subhypotheses/G30/README.md) | exploratory | mixed | x_att 0.89, k_llm 0.84; n̂ TALK 0.28 (LOPO pred 0.45); g_eq active 0.10 (LOPO pred 0.09); log density vs regime-only -0.04 |
| [G31](goalperiod-subhypotheses/G31/README.md) | exploratory | supported | x_att 0.85, k_llm 0.93; n̂ TALK 0.07 (LOPO pred 0.45); g_eq active 0.07 (LOPO pred 0.09); log density vs regime-only +0.60 |
| [G33](goalperiod-subhypotheses/G33/README.md) | exploratory | supported | x_att 0.82, k_llm 1.21; n̂ TALK 0.76 (LOPO pred 0.44); g_eq active 0.11 (LOPO pred 0.08); log density vs regime-only +1.98 |
| [G35](goalperiod-subhypotheses/G35/README.md) | exploratory | mixed | x_att 0.84, k_llm 0.32; n̂ TALK 0.08 (LOPO pred 0.47); g_eq active 0.10 (LOPO pred 0.08); log density vs regime-only +2.08 |
| [G36](goalperiod-subhypotheses/G36/README.md) | exploratory | mixed | x_att 1.13, k_llm 0.24; n̂ TALK 0.29 (LOPO pred 0.40); g_eq active 0.17 (LOPO pred 0.12); log density vs regime-only -0.47 |
| [G37](goalperiod-subhypotheses/G37/README.md) | exploratory | mixed | x_att 1.74, k_llm 0.20; n̂ TALK 0.30 (LOPO pred 0.30); g_eq active 0.32 (LOPO pred 0.19); log density vs regime-only -5.95 |
| [G38](goalperiod-subhypotheses/G38/README.md) | exploratory | supported | x_att 1.53, k_llm 0.20; n̂ TALK 0.32 (LOPO pred 0.34); g_eq active 0.12 (LOPO pred 0.18); log density vs regime-only +1.18 |
| [G39](goalperiod-subhypotheses/G39/README.md) | exploratory | mixed | x_att 1.82, k_llm 0.20; n̂ TALK 0.10 (LOPO pred 0.32); g_eq active 0.19 (LOPO pred 0.21); log density vs regime-only -1.22 |
| [G40](goalperiod-subhypotheses/G40/README.md) | exploratory | failed | x_att 1.56, k_llm 0.51; n̂ TALK 0.00 (LOPO pred 0.36); g_eq active 0.35 (LOPO pred 0.16); log density vs regime-only -3.93 |
| [G41](goalperiod-subhypotheses/G41/README.md) | exploratory | supported | x_att 1.40, k_llm 0.49; n̂ TALK 0.31 (LOPO pred 0.36); g_eq active 0.13 (LOPO pred 0.16); log density vs regime-only +0.27 |
| [G42](goalperiod-subhypotheses/G42/README.md) | exploratory | mixed | x_att 1.75, k_llm 0.24; n̂ TALK 0.20 (LOPO pred 0.31); g_eq active 0.11 (LOPO pred 0.22); log density vs regime-only -0.90 |
| [G44](goalperiod-subhypotheses/G44/README.md) | exploratory | mixed | x_att 1.59, k_llm 0.60; n̂ TALK 0.25 (LOPO pred 0.33); g_eq active 0.36 (LOPO pred 0.18); log density vs regime-only -0.09 |
| [G51](goalperiod-subhypotheses/G51/README.md) | exploratory | failed | x_att 2.24, k_llm 0.98; n̂ TALK 0.54 (LOPO pred 0.07); g_eq active 0.24 (LOPO pred 0.28); log density vs regime-only -3.07 |

## Results
*Exploratory round 1, 2026-10-04. Non-holdout data only (35 periods, 282 days); nothing here is confirmatory. Numbers come from `data/processed/H19-loop-gain-collapse/results/explore.json` (`analysis/explore.py`), `synthetic/summary.json` (`analysis/synthetic.py`) and `results/posthoc_channels.json` (`analysis/posthoc_channels.py`). One-page summary: `figures/summary.pdf`.*

### Assembled table
Nine methods over 35 periods: 244 period-level estimates (all SEs > 0), plus H02's 15 periods (21 chunks), used only to validate E1.

| Method | Family | Periods | Median | Range | Median SE |
| --- | --- | --- | --- | --- | --- |
| E1 `H19.geq_active` (primary E) | equal-time | 35 | 0.11 | −0.07 to 0.36 | 0.039 |
| E2 `H19.geq_talk` | equal-time | 34 | 0.15 | −0.07 to 0.38 | 0.035 |
| E3 `H04.K_week` | equal-time | 28 | 0.13 | −0.03 to 0.35 | 0.063 |
| E4 `H05.g2b_talk` | equal-time | 8 | 0.11 | 0.04 to 0.25 | 0.079 |
| E5 `H05.g2b_active` | equal-time | 8 | 0.09 | 0.05 to 0.40 | 0.078 |
| T1 `H03.n_talk` (primary T) | Hawkes | 35 | 0.41 | 0 to 0.76 | 0.077 |
| T2 `H03.n_all` | Hawkes | 35 | 0.43 | 0 to 0.72 | 0.059 |
| T3 `H03.nx_fast` | Hawkes | 33 | 0.07 | 0 to 0.21 | 0.020 |
| T4 `H04.n_week` | Hawkes | 28 | 0.42 | 0.14 to 0.98 | 0.129 |
| `H02.gcw_active` (validation) | equal-time | 15 | 0.12 | 0 to 0.36 | 0.045 |

- **Validation.** H19's own estimator reproduces H02's 21 chunks to 4×10⁻¹⁶; its day-bootstrap SE is 1.19× H02's surrogate SD (median). H05's loop gains, recomputed with H05's own code, equal the published ones; the day-bootstrap SEs are new.
- **Controls** (`controls.parquet`).
  - x_att(village) is 0.78–1.22 in regime I and 1.13–2.24 in regime III: nearly a regime indicator.
  - k_llm (agent messages delivered per LLM step) is 0.28–1.69 in regime I and 0.20–0.98 in regime III.
  - The human share of chat is < 1% except in early regime I (up to 44% in G05).

### P1, the pre-registered collapse on x_att: FAILED
| Method | Slope on x_att [95% KH CI] | R²_het |
| --- | --- | --- |
| E1 g_eq active | **+0.127 [+0.055, +0.198]** | 0.41 |
| E2 g_eq talk | −0.042 [−0.125, +0.040] | 0.00 |
| E3 H04 K | **+0.120 [+0.021, +0.219]** | 0.28 |
| E4 H05 g talk | +0.127 [−0.042, +0.297] | 1.00 (τ² → 0 at 8 periods; not meaningful) |
| E5 H05 g active | +0.069 [−0.240, +0.378] | 0.00 |
| T1 n̂ TALK | −0.160 [−0.365, +0.045] | 0.05 |
| T2 n̂ ALL | −0.164 [−0.358, +0.031] | 0.05 |
| T3 fast n_x | **−0.059 [−0.101, −0.017]** | 0.24 |
| T4 H04 n | −0.052 [−0.254, +0.149] | 0.00 |

- **(a) fails:** T1's slope is negative (CI includes 0) and T3's is significantly negative.
- **(b) fails:** T1's R²_het is 0.05.
- **(c) fails:** LOPO ELPD summed over methods: constant 141.0, x_att 146.3, regime 157.8, era 156.5, log N 153.7, regime + x_att 163.2. With regime intercepts, the x_att slopes of both primaries are positive (T1 +0.24 [−0.17, +0.64]; E1 +0.07 [−0.09, +0.22]), but the ELPD margins fail.
- **Robustness:** the verdict is unchanged without G51, with periods ≥ 4 days only, and with LLM-step turns (x_att_llm).
- **Reading.** The "loop gains" do not share a curve because they do not share a sign: the swarm's activity co-activation and its talk triggering moved in opposite directions across the regime-III scaffold switch.

### P2 (within-family concordance)
- **Hawkes family: supported.** Pairwise Spearman ρ is 0.40–0.72 over 28–35 shared periods (n̂ TALK–ALL 0.67, n̂ TALK–H04 n 0.64, fast n_x–n̂ 0.45).
- **Equal-time family: failed.**
  - g_eq active vs H04 K: ρ = 0.94 (28 periods); they are one quantity.
  - g_eq active vs g_eq talk: ρ = 0.15. H04 K vs g_eq talk: 0.09.
  - H05 active vs H05 talk: −0.48 (8 periods).
- **The real partition is the spin channel, not the estimator family:**
  - g_eq talk tracks the Hawkes gains: ρ = 0.55 with fast n_x, 0.63 with H04 n, 0.49 with n̂ ALL.
  - g_eq active is unrelated to them, or opposite: −0.37 with fast n_x, −0.04 with n̂ TALK.
  - The same split holds for residuals after x_att.

### P3 (cross-family mapping, unfitted): SUPPORTED
- g_eq,talk (equal-time, 1-min talk spins) co-varies with the Hawkes-mapped gain ĝ_map = 2w n_x/(1 + 2w(n_x + n_s)) from H03's fast kernels: ρ = 0.44 (p = 0.009); ρ = 0.59 with fast n_x directly.
- g_eq,talk ≥ ĝ_map in 91% (w = 0.6) and 88% (w = 0.85) of periods, with median ratio 2.3. About 40% of the equal-time talk gain is fast cross-triggering; the rest is common fast fields (the lulls H02 found).
- This is the one unfitted cross-method prediction, and it holds. Hawkes and Ising talk gains measure the same fast coupling, with different normalizations.

### P4 (dilution exponent): FAILED
Per-pair fast n_x scales with the **number of partners**, not with message traffic:
- n_pair ∝ (N_active − 1)^−1.02 [0.62, 1.43], ρ = −0.69;
- vs (1 + k̄)^−0.20 [−0.61, 1.24], ρ = −0.02;
- ΔELPD(k̄ − N) = −2.4 ± 9.3.

Total cross-triggering per message is roughly conserved as N grows (each message's ~0.07 offspring are shared among the partners). That is a fixed budget per *message* rather than per *turn*. Relevant to H18 and HH90.

### P5 (no mode effect beyond x): SUPPORTED
Mode-C coefficient:
- T1: −0.07 [−0.22, +0.09];
- E1: +0.003 [−0.05, +0.06].

Adding mode lowers LOPO ELPD for both (−0.7, −1.2).

### Scan (exploratory; Holm over the primaries' slope tests)
- **Joint ΔELPD vs constant:** k_llm +22.8 (7 positive / 2 negative slopes); date +15.2; n_rooms +14.3; log N +12.5; m_hour +11.9; … x_att +4.3; x_att_llm −10.4.
- **Strongest single slopes:**
  - n̂ TALK on k_llm: +0.38 [+0.24, +0.52], R²_het 0.53, p_Holm = 2×10⁻⁴;
  - n̂ TALK on m_turn_llm: p_Holm = 4×10⁻⁴;
  - g_eq active on x_att: p_Holm = 0.03.
- No control gives one sign across all 9 methods.

### Post hoc (labelled; selected after P1 failed): a talk-channel collapse
- **Talk channel** (n̂ TALK, n̂ ALL, fast n_x, H04 n, g_eq talk) **on k_llm** = agent messages delivered per LLM step:
  - 5/5 slopes positive and significant;
  - ΔELPD vs regime-only +25.4; adding k_llm to regime intercepts +17.0;
  - within-regime slopes all positive (+0.34, +0.25, +0.04, +0.33, +0.09).
  - Talk-triggering loop gains rise with chat exposure per model call, the opposite of the per-turn dilution direction in the card's model.
- **Activity channel** (g_eq active, H04 K, H05 active): no control beats regime-only. x_att is same-sign (2/3 significant) but −7.4 vs regime.
- **Caveats.**
  - k_llm was picked from 16 controls after the channel split was seen.
  - LLM steps per message depend on the scaffold (GUI vs bash).
  - m_turn_llm (share of model calls that are chat) may be mechanically tied to Hawkes clustering of talk.
- Figure: `figures/fig6_posthoc_channels.pdf`. The confirmatory script now tests this channel model (amendment below).

### Synthetic validation (axis F; `figures/fig4_synthetic.pdf`)
150 data sets per truth, simulated with the real design (periods, SEs, controls; the x_att–regime collinearity built in).

| Truth | supported | mixed | failed |
| --- | --- | --- | --- |
| null | 0.00 | 0.00 | 1.00 |
| collapse, R² = 0.25 | 0.23 | 0.31 | 0.46 |
| collapse, R² = 0.5 | **0.87** | 0.13 | 0.00 |
| collapse, R² = 0.75 | **1.00** | 0 | 0 |
| opposite signs | 0.01 | 0.00 | 0.99 |
| different controls per method | 0.00 | 0.01 | 0.99 |
| regime step | 0.01 | 0.59 | 0.40 |
| era trend | 0.01 | 0.49 | 0.50 |
| log N | 0.01 | 0.50 | 0.49 |

- The rule separates a true collapse of moderate size from method-specific scatter and from every rival.
- "Mixed" is not evidence (correlated rivals produce it about half the time).
- A weak collapse (R² ≈ 0.25) would often be missed.
- The real outcome matches no single truth exactly. The slopes split by channel; the primaries' R²_het is 0.41 vs 0.05; regime-only wins. It is closest to the channel-specific truths ("opposite signs", "different controls"), for which the rule returns *failed* 99% of the time. The opposite-sign truth averages 3.5 significantly negative slopes per data set; the real data have 1 (fast n_x).

### Outcome vs. prediction
| # | Prediction | Observed | Outcome |
| --- | --- | --- | --- |
| P1 | one curve on x_att: (a) primaries' slopes > 0, (b) R²_het ≥ 0.25, (c) beats rivals by > 2 nats and within-regime slope > 0 | E1 +0.13*, T1 −0.16, T3 −0.06*; R²_het 0.41 / 0.05; ΔELPD vs const +5.3, regime −11.5, era −10.3, log N −7.4 | **failed** (credence was 0.2) |
| P2 | within-family ρ ≥ 0.4 | Hawkes 0.40–0.72; equal-time min −0.48 (activity vs talk spins) | **supported (T), failed (E)** |
| P3 | g_eq,talk tracks the Hawkes-mapped gain, ρ > 0.3, ≥ 2/3 above ĝ_map(0.6) | ρ = 0.44, 91% above, ratio 2.3 | **supported** |
| P4 | per-pair n_x ∝ (1 + k̄)^−α, α ∈ [0.5, 1.5], k̄ beats N | α_k = 0.20, α_N = 1.02; ΔELPD(k̄ − N) = −2.4 ± 9.3 | **failed** |
| P5 | no mode-C effect beyond x | CIs include 0; ELPD falls with mode | **supported** |
| per period | inside LOPO 90% PI and ≥ regime-only | 12 supported, 19 mixed, 4 failed | low power per period |

(* = 95% CI excludes 0.)

### Caveats
- Few periods per method (8 for H05), heterogeneous estimators, and SE constructions that differ by method. H04's weekly SEs are upper bounds; H03's SEs are CI-derived with a 0.02 floor at the n ≥ 0 boundary.
- x_att is close to a regime indicator; most of the information is between regimes, and regime II has 2 periods.
- Methods share raw events (H03 and H04 Hawkes fits; H19 and H04 equal-time fits), so summed ELPD over-counts independent evidence. The P1 failure does not depend on that: the slopes have opposite signs.
- G51 (the only 8 h period, N = 26) is influential: n̂ TALK 0.54 vs collapse prediction 0.07. The verdict is unchanged without it.
- Not blind. The post-hoc channel collapse is a hypothesis for round 2, not a result.

### Figures
- `figures/fig1_collapse.pdf`: the collapse plot and the per-method panels.
- `fig2_scan.pdf`: control scan.
- `fig3_concordance.pdf`.
- `fig4_synthetic.pdf`.
- `fig5_mapping_dilution.pdf`: P3, P4.
- `fig6_posthoc_channels.pdf`.
- **`summary.pdf`** (one page).
- Per period: `G<NN>/figures/G<NN>_residuals.png`.

## Round 1b (improved data, 2026-10-04)
*Re-evaluation on the corrected tables (re-evaluation agent RE-A2; exploratory, holdout untouched; `confirm.py` not run). Switches keep round 1 runnable: `H19_DATA=r1b` (inputs and outputs under `data/processed/H19-loop-gain-collapse/r1b/`), `H19_E1=raw|trim|scaf` (which version of H19's own gains enters P1 as E1/E2; results in `r1b/results`, `results_trim`, `results_scaf`). New code: `scheme/geq_r1b.py`, `analysis/r1b_ne14.py`, `r1b_native.py`, `r1b_period_lines.py`.*

**What changed.**
- **H19's own gains (E1, E2)** re-estimated on `activity_bins_fixed` (the old table dropped about half of all events), each in three versions: **raw** (the pre-registered definition, whole-day grid), **DQ8 trim** (all-present window, explained joint silences removed; 77% of regime-III minutes kept, 91% of regime-I) and **H38-conditioned** (agent-state conditioning of day edges, infra errors and consolidations). Validation: the raw estimator still reproduces H02's round-1b chunks exactly (3×10⁻¹⁶).
- **Other methods:** H02 and H03 from their round-1b runs (H03 changes little: median |Δn̂| 0.007). H04's `K_week` and H05's two-block gains were built on the buggy table and are not yet re-run by their owners, so they are **dropped** (6 methods instead of 9; `--stale keep` restores them); H04's Hawkes `n_week` reads chat and is kept.
- **Nulls (DQ8):** per-chunk surrogate z of the raw gain against N1 on the whole grid ("round-1 null") vs N1 after trim + mask ("corrected null"): regime-III activity chunks significant 19/19 → **7/19**; regime I 27/38 → 18/38; talk gains barely move (17/19 → 15/19 in regime III).
- **Not re-run:** the synthetic validation of the P1 rule (same design; the method set shrank from 9 to 6).

**Old vs new.**

| | Round 1 | Round 1b, raw E1 (pre-registered) | **Round 1b, day-edge-adjusted E1 (DQ8 trim)** | H38-conditioned E1 |
| --- | --- | --- | --- | --- |
| E1 g_eq active, median | 0.11 | 0.18 | **0.08** | 0.12 |
| E1 slope on x_att | **+0.127 [+0.055, +0.198]** | **+0.181 [+0.085, +0.277]** | **−0.030 [−0.105, +0.045]** | −0.004 [−0.106, +0.097] |
| E1 regime III − I | **+0.113 [+0.049, +0.177]** | **+0.174 [+0.096, +0.253]** | **−0.034 [−0.101, +0.032]** | −0.018 [−0.106, +0.071] |
| E2 g_eq talk, regime III − I | **−0.073 [−0.141, −0.005]** | −0.043 [−0.125, +0.038] | −0.040 [−0.117, +0.037] | −0.064 |
| T1 n̂ TALK slope on x_att | −0.160 [−0.365, +0.045] | −0.153 [−0.352, +0.045] | same | same |
| T3 fast n_x slope on x_att | **−0.059 [−0.101, −0.017]** | **−0.065 [−0.106, −0.023]** | same | same |
| P1 verdict | failed | **failed** | failed | failed |
| LOPO ELPD: x_att − regime-only | −11.5 | −8.7 | −7.3 | −7.4 |
| P2 within-family (E) | failed (min ρ −0.48) | mixed (0.21) | mixed (0.28) | **supported (0.44)** |
| ρ(E1, H03 n̂ ALL / n̂ TALK / H04 n) | −0.01 / −0.04 / 0.07 | 0.01 / −0.00 / 0.01 | **0.43 / 0.35 / 0.42** | 0.49 / 0.41 / 0.45 |
| P3 mapping ρ (≥ ĝ_map share) | 0.44 (91%) | 0.37 (94%) | 0.33 (89%) | 0.41 (94%) |
| P4 per-pair n_x exponent: on k̄ / on N | 0.20 / 1.02 | 0.26 / 1.03 | same | same |
| P5 mode-C effect | none | none | none | none |
| scan: control with one sign for all methods | none | none (k_llm 5+/1−) | **k_llm, 6/6 positive and significant** (ΔELPD vs constant +34.9) | k_llm 6/6 (+39.4) |
| per-period verdicts (supported / mixed / failed) | 12 / 19 / 4 | 9 / 23 / 3 | 11 / 23 / 1 | 9 / 24 / 2 |

**Reading.**
1. **P1 still fails** on corrected data and under every version of E1: no positive common slope on x_att, and the regime-only rival wins out of sample.
2. **The round-1 headline ("activity and talk channels move in opposite directions") is withdrawn.** The rising activity gain was the operator's day edges. With them removed, the activity gain is flat in x_att and across regimes, the N4 opposite-sign signature disappears, and the activity gain *agrees* with the Hawkes gains across periods (ρ 0.35–0.49 instead of ≈ 0). NE14 confirms it at the boundary itself (below). Cross-hypothesis: H38 (f_scaffold) and H50 (activity co-movement is mostly the scheduler's field; per-pair activity correlation 0.005 inside the regime-III window) say the same.
3. **The post-hoc k_llm collapse grows from 5 to 6 methods.** With day-edge-adjusted activity gains, every method's slope on messages delivered per LLM step is positive and significant (activity +0.10 [+0.05, +0.16]). This is still post hoc (k_llm was picked in round 1 from 16 controls after the channel split), H04/H05 are missing, and inside #51 the k_llm relation does not hold (G51 below). **The frozen confirmatory channel model (`results/frozen_channel_model.json`, activity on x_att, fitted on the buggy table) is stale and should be re-frozen from round 1b before any confirmatory run.**

**NE14 (regime II → III) with and without the day-edge adjustment** ([NE14](goalperiod-subhypotheses/NE14/README.md); H38's design, E = g − N1 surrogate mean, ΔE ± 1.96 day-bootstrap SE):

| Activity gain | Old tables | Fixed tables |
| --- | --- | --- |
| raw | **+0.145 ± 0.083** | +0.112 ± 0.177 |
| DQ8 trim | −0.024 ± 0.117 | −0.080 ± 0.214 |
| H38-conditioned | −0.062 ± 0.132 | −0.140 ± 0.280 |
| talk, raw / trim | −0.033 / −0.022 | +0.061 / +0.084 (± 0.09–0.11) |

H38's round-1 result reproduces on the old tables. On the fixed tables the raw rise no longer excludes 0 and the adjusted gain falls across the switch. Round 1's "+0.11 regime III − I" becomes +0.17 raw and **−0.03** adjusted in the meta-regression (row above).

**Period-native layer** (predictions dated in the folders before the runs):

| Folder | Design | Prediction | Result | Verdict |
| --- | --- | --- | --- | --- |
| [G51](goalperiod-subhypotheses/G51/README.md) | #51 N sweep 21 → 32 (12 shared units) | per-pair fast n_c ∝ (N−1)^−1 (P4 inside one period); trimmed activity gain not rising with N | n_c falls far faster (α at the grid edge, 3.0 [2.5, 3.0]; total n_x → 0 from N = 28); trimmed g rises +0.025/agent (consistent with a fixed per-pair r ≈ 0.005) | failed |
| [NE42](goalperiod-subhypotheses/NE42/README.md) | A-B-A room merge at N = 15 | talk n_x in #40 0.67–1.5× its neighbours; trimmed activity gain within ±0.07 | talk triggering vanishes in the merged week (n_x, n̂ TALK, g_eq talk ≈ 0); trim +0.11 vs conditioned −0.09 | failed |
| [NE43](goalperiod-subhypotheses/NE43/README.md) | bookend messages stop (08-05), nudger stops (08-21), #51 at N = 27 | day-edge part of the activity gain unchanged (< 0.05) when the bookends stop | −0.037 ± 0.043; edges are ~¾ of the raw gain on every side | supported |
| [NE14](goalperiod-subhypotheses/NE14/README.md) | regime II → III, raw vs adjusted | H38: rise vanishes under adjustment | yes (old and fixed tables); adjusted Δ < 0 | failed (for the round-1 reading) |

**Verdict changes.** Card: P1 failed (unchanged); P2 E-family failed → mixed (raw/trim) or supported (conditioned), T-family supported → mixed (minimum ρ 0.40 → 0.37); the channel-opposition reading and the "activity rises in regime III" structure (axis G) are withdrawn. Periods (`**Verdict (1b):**` lines, pre-registered E1 / adjusted E1): with the pre-registered E1, 6 of 35 change (G07 mixed → supported, G11 failed → mixed; G13, G26, G38, G41 supported → mixed); with the adjusted E1, G02 and G40 also move failed → mixed and only G51 stays failed. New native folders G51 (section), NE42, NE43, NE14.

**Scorecard updates (round 1b).** A 1 → 1 (the channel non-invariance of round 1 was partly the day-edge artifact; turn-based controls still change meaning with the scaffold). B 1. C 0 (still loses to regime-only). D 1 (P3 holds: ρ 0.33–0.41). **E 0 → 1** (natural experiments now attempted: NE43's dated prediction held; NE42 and NE14 did not support the dilution models). F 2 (synthetic not re-run; same rule). **G 1 → 1** with a different reason: the scaffold switch is the main structure for the talk/Hawkes gains (n̂ regime III − I −0.21), but no longer for activity. H 0. I 0.

## Notes
- **Round 1b (2026-10-04):** H38's note below is confirmed on the fixed tables (regime III − I +0.17 raw → −0.03 trimmed). `results/frozen_channel_model.json` (round-1 data, activity on x_att) is stale; re-freeze from `r1b/` before any confirmatory run. **From H50 (cross-hypothesis):** activity co-movement is mostly the scheduler's field; talk is a real read-out-gated coupling (J₁ 0.034 / 0.019 in regimes I / III).
- **From H38 (2026-10-04):** the regime-III rise in activity g_eq is mostly a day-edge artifact: +0.125 → +0.017 across periods after agent-state conditioning (H19 reported +0.11). The channel split should be re-run on stall-adjusted gains.
- 2026-10-03: promoted from HH100.
- 2026-10-04: round 1 started. Control-parameter table built first, then the card's mapping, observables, nulls and predictions (00:03 UTC), then the estimates assembly, synthetic validation and the real-data fit.
- 2026-10-04: round 1 run.
  - Synthetic validation: `analysis/synthetic.py`, 2 workers, about 20 CPU-minutes.
  - `analysis/explore.py`, then `analysis/posthoc_channels.py`.
  - `write_period_folders.py --results`, then `figures.py`.
  - `confirm.py --dry-run` (non-holdout stand-ins G24 and G41; code-path check only; numbers meaningless).
- **Decisions taken before fitting** (implementation, not outcome-driven):
  - windows inside a period are combined by inverse-variance weighting;
  - SE floor 0.02 for CI-derived SEs;
  - an H04 ISO week is assigned to a period if ≥ 80% of its days are in it;
  - the per-period "summed log density" sums over methods both models can predict;
  - rank-deficient designs (H05 methods have no regime-I period) are reduced to full rank, so regime-only cannot predict G35 for H05 methods.
- **Amendment 1 (2026-10-04, after the exploratory P1 failed, BEFORE any holdout data was touched):**
  - `analysis/confirm.py`'s primary model is now the post-hoc **channel model** (`results/frozen_channel_model.json`): talk-channel gains on k_llm, activity-channel gains on x_att.
  - The pre-registered P1 model (`results/frozen_model.json`) is sealed and scored as a secondary.
  - Pass rule unchanged: ≥ 70% inside 90% PIs AND RMSE below the regime-only rival on the same cells.
  - Scoring of the Hawkes methods needs H03 (and H04) to export held-out per-period estimates in the shared schema (`confirmatory = true`). Without them, only g_eq talk (talk channel) and g_eq active (activity channel) are scorable by H19 alone.
  - Eligible cells as listed under "Confirmatory design".
- **Proposed shared schema** (for H10–H18; the ingest hook is in `scheme/build_estimates.py`): `data/processed/H<NN>-*/per_period_estimates.parquet`.
  - Required: `goal_no`, `window`, `method`, `family` (E / T / O), `estimand`, `loop_gain` (bool), `value`, `se`.
  - Recommended: `lo`, `hi`, `ci_kind`, `n_days`, `N`, `spin_or_events` (talk / active / …: the channel turned out to matter more than the estimator), `bin_s`, `detrend`, `confirmatory` (bool), `built_by`, `notes`.
- **Proposed DEFINITIONS.md entries** (not edited; outside H19's scope): loop gain (equal-time, 1 − 1/VR; channel-specific); loop gain (Hawkes n; fast cross n_x); attention load k̄ (per village turn, per LLM step); agent turn (village; LLM step).

## Round 2 redirects (2026-10-04)
*From the round-1 reflection (`writeup/round1-reflection/round1-reflection.pdf`).*
- **Where round 1 went sideways:** Collapsing heterogeneous estimators failed because they measure different channels.
- **What the direction is really after:** The swarm has two order parameters, talk and work, that trade off.
- **H19-R1.** Talk and work anticorrelate: periods and agents sit in talky or worky phases on a (talk, work) phase diagram.
- **H19-R2.** Goal type (shared vs individual) moves the swarm between the two phases.
- **H19-R3.** Messages per LLM step is the control parameter; pre-register the post-hoc collapse.
