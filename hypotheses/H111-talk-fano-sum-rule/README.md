# H111: A fluctuation–response sum rule for talk: Fano factor = 1/(1 − g)²

**Status:** exploratory round 1 done (2026-10-04; non-holdout only). **The sum rule holds in regime III with no free parameter; regimes I and II carry an excess the read-out loop does not explain.**
- **Regime III closes:** the collective Fano ratio of talk at 10-min windows matches Φ_pred = 1/(1 − g_lag)² (room-adjusted) from H67's read-out gain: pooled r_F = Φ_obs/Φ_pred = **1.01 [0.94, 1.09]** over 18 units (between-unit τ² = 0; wall clock 1.04 [0.96, 1.12]). r_F lies in [0.8, 1.2] in 14/18 units (P1 supported) and is never ≥ 2 (HH kill not met). Φ − 1 tracks g_lag across regime-III units (ρ 0.60, p 0.008).
- **Hop 1 is the whole gain:** H67's hop-1–3 gain g_lag,3 over-predicts (median r_F 0.66); the heterogeneous spectral radius agrees (0.95).
- **Regimes I/II show an excess:** pooled r_F 1.34 [1.18, 1.52] in regime I where g_lag ≈ 0; Φ(10) > 1.2 in 13/21 units (P4 missed its 2/3 bar narrowly). The excess is fast (no significant rise of Φ(T) from 5 to 30 min in 16/17 excess units), so it is a fast field or a coupling the hop-1 clock misses, not a slow drive.
- **Collective variance lives inside rooms:** cross-room pair correlation ≈ 0 in all 12 two-room units (within > cross in 10/12).
- Natives: NE43 supported (the operator's bookends added untrimmed variance that vanished when they stopped; trimmed Φ unchanged at both steps), NE42 failed (Φ does not drop in #40 where g_lag ≈ 0), NE14 descriptive (one regime-II day).
- Scorecard A1 B1 C1 D2 E1 F1 G1 H1 I0. `analysis/confirm.py` frozen, guarded and dry-run; **not run**.
**Question (GOALS.md):** **Q2** (what is field and what is coupling?): does H67's read-out loop gain account, with no free parameter, for all the collective clustering of talk, so that any excess is a field? **Q3** second: a closure test of the subcritical-swarm reading (H67, H51).
**Fields:** stat mech (fluctuation–response relations), point processes, dynamics
**Literature:** no note in `literature/` covers linear point processes. Cited from memory (†, not in `literature/`): Hawkes, *Biometrika* 58, 83 (1971)†; Hawkes & Oakes, *J. Appl. Prob.* 11, 493 (1974)† (cluster representation; long-window variance of a linear Hawkes process = (1 − n)⁻² × mean); Bacry, Dayri & Muzy, *EPJ B* 85, 157 (2012)† (multivariate long-window covariance (I − K)⁻¹ Σ (I − K)⁻ᵀ). Model references: [`physics-models/09-hawkes/README.md`](../../physics-models/09-hawkes/README.md), [`physics-models/14-scaling-and-fluctuations/README.md`](../../physics-models/14-scaling-and-fluctuations/README.md).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Population N(t) (active population); Regime; Driving / external field; **Read-out loop gain g_lag** (H67; variants g_lag,3 and g_lag,het); **Loop gain (equal-time, daily dial)** (H25, comparison only); **Taylor field gauge c_×** and **within-day shared coefficient c_×w** (H86); DQ8's **all-present window**; **Call clock** (H40); **Swarm call clock τ** (H77/H78). **New named variants proposed for DEFINITIONS.md** (not edited here), defined under Model: *collective Fano ratio Φ(T)*, *sum-rule prediction Φ_pred*, *sum-rule excess Δ_F*.
**From:** HH342 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/09-hawkes/` (primary), `physics-models/14-scaling-and-fluctuations/` (fluctuation scaling, tool)
**Data inputs (shared tables first):** DQ1 `call_windows`, `context_ledger_turns`; `chat_core` (agent talk messages), `kicks_classified` (human messages, kickoffs), `calendar`, `period_units`, `roster`. Comparison only (read, never recomputed): H67's per-unit g_lag, g_lag,3, g_lag,het, g_eq (`data/processed/H67-lagged-criticality-dial/results/units.parquet`); H86's `taylor_c_shared` rows in `per_period_estimates`.

## Source HH (verbatim from the HH list, including refinements)
- **HH342 · A fluctuation–response sum rule for talk: Fano factor = 1/(1 − g)².** In a branching process with gain g, the variance of counts in long windows exceeds Poisson by exactly 1/(1 − g)². H67 measured g from read-out responses (regime III median 0.13, maximum 0.39). If the read-out loop is the only source of talk clustering, the spontaneous Fano factor of trimmed talk counts must equal 1/(1 − g_lag)² with no free parameter. Any excess is a field.
  - *Prediction:* after DQ8 trimming and removal of c_×, the long-window Fano factor of per-unit talk matches 1/(1 − g_lag)² within 20% in ≥ 2/3 of regime-III units. Untrimmed, it exceeds the prediction: that excess is the scheduler field (H38).
  - *Check:* per-unit talk counts in windows ≫ t_read; compare with H67's per-unit g; block-shift null for the field part.
  - *Kill:* trimmed Fano still exceeds the prediction by ≥ 2× in most units. Talk then clusters by a hidden field or coupling that the read-out loop misses.
  - *Impostors:* scheduler: trimming plus c_×. Exogenous: human and kickoff windows excluded. Priors: n/a (count statistic). Convergence: g comes from read-gated responses only.
  - *Models:* 09, 14 · *Builds on:* H67, H86, H38, H03

## Question
Does the read-out loop gain g_lag that H67 measured from responses predict, with no free parameter, the long-window collective variance of talk counts? Or does talk cluster more than the read-out loop allows, so that a field or an unmeasured coupling carries the excess?

## Design: two layers (STANDARDS §4)
- **Replication (layer 1, role `replication`).** The common estimator (below) on every non-holdout period unit for which H67 has a g_lag (66 units, 35 periods; H67's eligibility rule: ≥ 3 calling agents, ≥ 100 agent messages, ≥ 200 trimmed receiving calls). One README per goal period. Units of a split period are reported separately and pooled by a random-effects mean (CLAUDE.md exception (d), named: some units have 1–2 days).
- **Natives (layer 2, role `native`),** each with its own dated prediction in its folder:
  - **NE42** (#39 → #40 → #41, room merge and split at a fixed roster): H67's g_lag goes 0.144 → 0.003 → 0.189. The sum rule predicts the collective Fano ratio falls in #40 and returns in #41.
  - **NE14** (#36: 36a regime II → 36b ∪ 36c regime III): g_lag goes −0.06 → 0.12. The sum rule predicts a rise of the ratio across the boundary.
  - **NE43** (#51: 51f with operator bookends → 51g without them (08-05) → 51h without nudges (after 08-20)): a synchronizing scheduler drive is removed at fixed g. The trimmed ratio should not move; the untrimmed ratio should fall.

## Model
**From:** `physics-models/09-hawkes` (linear multivariate Hawkes process; cluster representation), with `physics-models/14-scaling-and-fluctuations` for the variance decomposition.

**H111 variant: linear response of talk counts on the call clock.** Agent i's talk count in window w of length T is n_i(w). Each agent has a private stochastic process (its call clock, its own bursts, its messages per talk call; any distribution, clocked or bursty). Agents excite each other through reading with a cross-response matrix K (zero diagonal). For windows long compared with the response time, linear response gives the count covariance

  C(T)/T → (I − K)⁻¹ Σ (I − K)⁻ᵀ,

with Σ = diag(σ_i²) the private noise (Poisson: σ_i² = rate; a clocked agent less; a bursty agent more).

**Collective Fano ratio (proposed named variant).** Φ(T) = Var(Σ_i n_i) / Σ_i Var(n_i) on the same windows. It divides out every private noise level, so the clocks of clocked agents (H86: b < 1) and own bursts cancel. Φ = 1 for independent agents. Φ − 1 = Σ_{i≠j} Cov(n_i, n_j) / Σ_i Var(n_i), the pair covariance in units of private variance (H86's c_× on the same windows, renormalized).

**Sum-rule prediction (proposed named variant).** In mean field, K has eigenvalue g on each room's collective mode and −g/(n_b − 1) on the n_b − 1 transverse modes of room b. For equal private noise:

  Φ_pred(g) = [N/(1 − g)²] / Σ_b [1/(1 − g)² + (n_b − 1)/(1 + g/(n_b − 1))²] ≈ 1/(1 − g)²,

with N agents in B rooms of sizes n_b. Inputs: H67's per-unit g = g_lag (primary) and the unit's present-agent count and rooms. Nothing is fitted. g_lag counts first-generation offspring at hop 1, so the full branching ratio lies between g_lag and g_lag,3 (hops 1–3, not placebo-corrected); Φ_pred(g_lag,3) is the upper bracket. g_lag = 0.13 gives Φ_pred ≈ 1.32; g = 0 gives 1.

**The HH-literal Fano.** F(T) = Var(Σ_i n_i)/E(Σ_i n_i). With Poisson private noise, F → 1/(1 − g)². For clocked agents the private part is not Poisson, so F alone mixes private noise with coupling. The per-agent block-shift null keeps every agent's private series and destroys cross-covariance, so F/F_shift = Φ. Φ is the HH's Fano after the block-shift normalization.

**What the excess means.** Sum-rule excess Δ_F = Φ_obs − Φ_pred (proposed named variant). Δ_F > 0 is a shared field (common drive) or a coupling the hop-1 read-out loop misses. The time-scale signature separates them in part: a coupling with a kernel of a few minutes gives a plateau in Φ(T) for T ≫ t_read (≈ 2 min); a shared field with correlation time τ_f makes Φ(T) keep rising until T ≈ τ_f.

**Rivals (named).**
- **R1 pure read-out loop (the HH):** Φ_obs ≈ Φ_pred(g_lag), plateau in T.
- **R2 hidden slow field** (H99: the collective talk mode keeps memory single agents lack; a slow common drive is not excluded): Φ_obs > Φ_pred, Φ(T) rising with T.
- **R3 hidden fast coupling or fast field** (H67: the equal-time dial reads 0.10–0.31 from fast fields; H26 room talk gain 0.64 at 30 min): Φ_obs > Φ_pred with a plateau.
- **R4 scheduler field** (H38): the excess sits in the untrimmed data and vanishes on trimming.

## Data scheme (`scheme/`)
`scheme/build.py` reads shared tables only and asserts the holdout twice (`calendar.holdout` and `common.holdout_mask`). Codes and times only (no text).
- **Units:** non-holdout `period_units` units with an H67 g_lag (H67 `results/units.parquet`, `ok`).
- **All-present window (DQ8, H67's rule):** per day, over agents with ≥ 20 receiving calls (`ctx_mode != summary`) that day: [max_i first t_call, min_i last t_call]. Present agents = those agents. Days whose window is shorter than 60 min are dropped.
- **Talk counts:** agent messages from `chat_core` (`speaker_kind == agent`, Claude Code agent excluded as in H67's recipients) by present agents, binned into windows of T minutes from the window start: T ∈ {1, 2, 5, 10, 15, 20, 30}. Variant: talk calls (`call_windows.talk`) instead of messages.
- **Field removal (primary):** counts are demeaned within (agent, day, 60-min block) before any variance. Blocks are cut from the window start; a block with fewer than 2 windows is dropped. This removes fields slower than an hour (day level, hour-to-hour drift).
- **Exogenous exclusion (primary):** drop windows that overlap [t_h − 0, t_h + 15 min) for any human message t_h in the unit's rooms (`kicks_classified` kind `human_message`), and the first 60 min of a goal's kickoff day. Variant: keep them.
- **Untrimmed variant:** the calendar day window (`win_start`..`win_end`), agents with ≥ 20 calls, same demeaning.
- **Raw variant:** untrimmed, demeaned within agent-day only (no 60-min blocks).
- **Call-clock variant (H40, H77/H78):** windows of a fixed number of receiving calls by present agents (the swarm call clock), sized so the mean window is 15 min in each unit.
- **Output:** `data/processed/H111-talk-fano-sum-rule/` (`counts/<unit>.npz` count arrays per T, `windows/<unit>.parquet`, `unit_meta.parquet`, `results/`, `synthetic/`, `_provenance.json`). Budget ≤ 50 MB.
- **Regimes covered:** I, II, III (non-holdout units). Fits are within unit.

## Observables
Per unit (and per period by random-effects pooling):
1. **Φ(T)** for T ∈ {1, 2, 5, 10, 15, 20, 30} min; **primary T* = 15 min** (≫ t_read ≈ 2 min; ≥ 4 windows per hour block). CI: hour-block bootstrap (resample (day, 60-min block) cells; 500 draws). Per H67, day blocks with ≤ 5 days are anti-conservative.
2. **Φ_pred(g_lag)**, **Φ_pred(g_lag,3)** (upper bracket), Φ_pred(g_lag,het) (variant), with g's CI propagated.
3. **Ratio r_F = Φ_obs/Φ_pred(g_lag)**; **excess ratio E_F = (Φ_obs − 1)/(Φ_pred − 1)** (defined when Φ_pred − 1 ≥ 0.05); **Δ_F = Φ_obs − Φ_pred**.
4. **Shape:** s_F = ln Φ(30)/Φ(5) ÷ ln 6 (log-slope of Φ in T between 5 and 30 min); a plateau gives s_F ≈ 0.
5. **Scheduler part:** Φ_untrim(T*) − Φ_trim(T*), and the raw variant.
6. **HH-literal:** F(T*) and F_shift(T*) (per-agent circular block shift within each day's window, offsets ≥ 60 min, 49 surrogates); F/F_shift.
7. **Call-clock** Φ_cc(T* equivalent), **talk-call** Φ, **with-exogenous** Φ.
8. **Talk c_×w** on the same windows (H86's within-day shared coefficient on talk; comparison).

## Null / baseline
- **Coupling-only prediction** Φ_pred(g_lag) is the main baseline: no free parameter.
- **Independent agents:** per-agent circular block-shift surrogates (offsets ≥ 60 min within each day's trimmed window, 49 per unit) give Φ_null ≈ 1 and the size of "Φ > 1" calls.
- **Field-only synthetic worlds** (axis F, below): shared OU rate fields with no coupling show what a field does to Φ(T).
- **Partition contrast (STANDARDS §3):** a coupling acts through reading inside a room. In two-room units, the cross-room part of Φ (pairs in different rooms) is a field-only reference: Φ_cross − 1 should be ≈ 0 under R1 and > 0 under a shared field.

## Impostors (STANDARDS §1)
| Impostor | How H111 removes it | Status |
| --- | --- | --- |
| **Scheduler field** | DQ8 all-present window; 60-min block demeaning; call-clock variant; untrimmed and raw variants measure what trimming removes; block-shift null | removed (primary), measured (variants) |
| **Exogenous field** (kickoff, goal, operator) | Windows within 15 min after a human message and the kickoff day's first hour excluded; goal fields are constant within a unit and fall out with the block means; with-exogenous variant reported | partly (nudges kept: they target single idle agents, a private input) |
| **Shared model priors** | A count statistic: priors set private rates, which Φ divides out. Same-family agents reacting together would show as covariance, so the cross-family share of Φ − 1 is reported | partly |
| **Contemporaneous convergence** | g_lag comes from H67's read-gated responses with a matched-lag in-flight placebo. Φ itself is an equal-window statistic and counts convergence as excess; that is the point of the test (excess = whatever the read-out loop misses) | n/a for Φ (it is the residual); removed in g_lag |

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R2 hidden slow field; R3 hidden fast coupling or fast field; R4 scheduler field; the equal-time Curie–Weiss reading (VR = 1/(1 − g), H25).
**Locked holdout used for confirmation:** none yet. `analysis/confirm.py` (frozen 2026-10-04, guarded, dry-run on stand-ins 27, 24, 42b, 51h; **not run**) targets H67's confirm units: #22, #28 (regime I), #43 and the #51 tail (regime III). It refuses until H67's confirmatory g_lag exists. Frozen C1 (regime-III pooled r_F in [0.80, 1.25], CI including 1), C2 (no regime-III unit r_F ≥ 2), C3 (post hoc, flagged: regime-I pooled r_F > 1.10), C4 (wall-clock pooled r_F in [0.80, 1.25]).
**Scorecard plan:** A from the mapping (Φ from counts on the trimmed grid; g from H67). B from the plateau test and the clock variants. C from Φ vs the block-shift null and the cross-room partition. D: the sum rule is itself an unfitted prediction. E from NE42, NE14, NE43. F from the synthetic recovery on real call grids. G from the cross-room part (rooms are known structure). H from R1 vs R2–R4. I from the holdout (not run).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Φ from talk messages of present agents on DQ8 windows; Φ_pred from H67's g_lag, present N and rooms; nothing fitted. Assumptions listed (linear response, equal private noise, mean-field rooms). Not invariant: the rule closes in regime III and leaves a 1.34× excess in regime I. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Plateau: regime-III Φ(T) flat between 5 and 30 min (median s_F −0.06); in regime III the wall clock reads 0.06 above the per-call clock and the swarm call clock 0.10 below it. The HH-literal identity F/F_shift = Φ fails (within 10% in 49%): the circular shift changes private variance when talk per call drifts within a day. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Φ exceeds the block-shift null's 95th percentile in 21/41 units (null median 1.04). Per-unit CIs are wide (±0.3–0.5 at 10 min); the pooled regime-III ratio is tight (±0.08). No held-out run. |
| D unfitted predictions | unfitted statistics and the model's signature | 2 | A parameter-free prediction from a different estimator (H67's call-level read-out jump) matches a different statistic (windowed count covariance): pooled r_F 1.01 [0.94, 1.09], τ² = 0, and the rank across units (ρ 0.60). |
| E interventional | predicts the change across a natural experiment | 1 | NE43 supported (untrimmed excess +0.23 → −0.05 when the bookends stop; trimmed Φ moves −0.01 and +0.08). NE42 failed (predicted drop 0.41, observed −0.04). NE14 uninformative. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Real call grids: g = 0.15 recovered within −3% to +1% (coverage 0.9); g = 0.30 reads 5–20% low; no-coupling CI includes 1 in 70–100%; a slow field is flagged (Φ 2.3–2.8). A fast field cannot be told from coupling by shape; 2-day units are imprecise. Amendment A1 (per-call clock) was forced by a call-grid field (unit 41). |
| G ground truth | agrees with known structure | 1 | Rooms are known structure: the collective covariance is within rooms (median per-pair ρ 0.031) and zero across rooms (−0.004; 0/12 cross-room > 0), as coupling through reading requires. |
| H comparative | beats the named rivals | 1 | Beats R2 (slow field) and R4 (scheduler) in regime III: no rise with T, trimming and exogenous exclusion change Φ by ≤ 0.03. R3 (fast field or missed coupling) is not excluded and is the best reading of the regime-I excess. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Holds in 5/5 resolved regime-III periods (#38, #39, #41, #42, #51 supported; #40 mixed); no holdout run. |

## Prediction
*Written 2026-10-04 21:28 UTC, before any real-data statistic. Seen beforehand: table schemas; the period-unit list; H67's published card (per-period g_lag, g_eq, g3 regime-III median 0.28); H25's, H26's (talk room gain ≈ 0.64 at 30 min), H86's (talk shared share φ 0.21) and H99's (collective talk memory excess +0.077) published results. Not seen: any H111 statistic, any windowed talk-count variance.*

**Synthetic (axis F), before real data.** Talk simulated on the real call grids of four units (27 regime I; 41, 44b, 51e regime III), with each agent's real receiving calls as its clock, linear read-out coupling at the next call (H67's model), messages per talk call drawn from the unit's distribution, and real days. Worlds: coupling g_true ∈ {0, 0.15, 0.30}; private self-persistence; a shared OU field (τ_f = 5 min and 30 min) with no coupling.
- **S1 recovery:** with coupling only, Φ(15) lies within ±20% of Φ_pred(g_true) (median over 8 replicates per cell) and the bootstrap CI covers Φ_pred(g_true) in ≥ 80%. [0.6]
- **S2 null:** g = 0, no field: the CI of Φ(15) includes 1 in ≥ 85% of replicates; private self-persistence alone does not move Φ (|Φ − 1| < 0.05). [0.75]
- **S3 slow field:** τ_f = 30 min, g = 0: Φ(15) > 1.2 and s_F > 0 (CI excluding 0) in ≥ 80% of replicates. [0.6]
- **S4 fast field:** τ_f = 5 min, g = 0: reported, not scored. Expectation: Φ > 1 with a near plateau, so a fast field can pass as coupling (R3 not separable by shape).
- **S5 power for the kill:** at real counts, Φ_obs = 2 Φ_pred is distinguished from Φ_pred (CI excluding Φ_pred) in ≥ 80% of regime-III units. [0.7]

**Real data (exploratory, non-holdout).**

| # | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| P1 | **The sum rule (HH).** In regime III, the trimmed Φ(15) lies within ±20% of Φ_pred(g_lag) (r_F ∈ [0.8, 1.2]) in ≥ 2/3 of units. | r_F outside [0.8, 1.2] in > 1/3 of regime-III units | 0.20 |
| P1b | **Excess scale.** In regime III, the median E_F lies in [0.5, 2]. | median E_F > 2 or < 0.5 | 0.25 |
| P2 | **Scheduler part (HH).** Untrimmed Φ(15) > trimmed Φ(15) in ≥ 2/3 of regime-III units. | untrimmed ≤ trimmed in ≥ 1/2 | 0.6 |
| K | **Kill (HH).** Trimmed Φ(15) ≥ 2 Φ_pred(g_lag) in > 1/2 of regime-III units (talk clusters by a hidden field or coupling). Credence that the kill is met: 0.35. | — | (0.35) |
| P3 | **Shape.** Φ(T) rises with T between 5 and 30 min (s_F > 0, CI excluding 0) in ≥ 2/3 of units with excess (r_F > 1.2): the excess is a slow field (R2), not a missed fast coupling (R3). | s_F ≤ 0 in ≥ 1/2 of excess units | 0.55 |
| P4 | **Regime I.** g_lag ≈ 0, so Φ_pred ≈ 1.0; the observed Φ(15) > 1.2 in ≥ 2/3 of regime-I units (the field H67 saw as g_eq − g_lag ≈ 0.17). | Φ(15) ≤ 1.2 in ≥ 1/2 of regime-I units | 0.6 |
| P5 | **Rank.** Across units, Spearman ρ(Φ_obs(15) − 1, g_lag) ≥ 0.3. | ρ < 0.1 | 0.5 |
| P6 | **Partition contrast.** In two-room units, the within-room pair covariance exceeds the cross-room one (Φ_within − 1 > Φ_cross − 1) in ≥ 2/3 of units; the cross-room part is > 0 (a field) in ≥ 1/2. | within ≤ cross in ≥ 1/2 | 0.6 |
| P7 | **Call clock.** The call-clock Φ is lower than the wall-clock Φ in ≥ 2/3 of regime-III units (cadence modulation is part of the field). | Φ_cc ≥ Φ_wall in ≥ 1/2 | 0.45 |
| P8 | **HH-literal Fano.** F(15)/F_shift(15) agrees with Φ(15) within 10% in ≥ 90% of units (the identity behind the normalization). | disagreement > 10% in > 1/3 | 0.8 |

**Amendment A1 (2026-10-04 21:40 UTC, after the synthetic validation, before any real-data statistic).** Seen: only synthetic runs on the real call grids of units 27, 41, 44b and 51e (7 worlds × 8–10 replicates, three estimator settings; `synthetic/summary_v0_wall_msg15.json`, `summary_wall_s10.json`, `summary_final.json`). Three changes; none is post hoc with respect to real data.
- **Primary clock: per-call residual ("percall").** Before the variance, each agent's count in a window is replaced by its residual on its own receiving calls in that window: x_iw = n_iw − p̂_{i,b} c_iw, with p̂ the agent's talk per call in the 60-min block. Reason: the real call grid carries a shared modulation of call density. On unit 41, talk simulated with no coupling and no field gave Φ(15) = 1.28 on the wall clock, rising with T; on the per-call clock it gives 0.96. Coupling acts on the talk probability per call (H40, H67), so the per-call residual keeps it (g = 0.15 recovered within −3% to +0.5%). The wall-clock Φ (the HH-literal statistic) is kept as variant `wall`. A field in call cadence (agents pausing together) is removed by the primary and appears in `wall − percall`.
- **Primary T* = 10 min** (was 15). It keeps ≥ 6 windows per hour block, recovers g as well as 15 min, and 2-day units keep usable windows. T = 15 is reported.
- **Exogenous rule: human sessions.** Human messages merged into sessions (gaps ≤ 10 min); windows overlapping [first message, last message + 10 min) are dropped. The old rule (any window overlapping 15 min after any human message) deleted every 15-min window of unit 44b (48 human messages in 2 days).
- **Synthetic verdicts (final setting, units 27, 41, 51e; 44b, a 2-day unit, reported separately):** **S1 partly passed:** at g = 0.15 the median Φ(10) is within −3% to +1% of Φ_pred, coverage 0.9; at g = 0.30 it reads 5–20% low, coverage 0.5–0.7 (the estimator is conservative for an excess). **S2 partly passed:** with no coupling the CI includes 1 in 70–100% of replicates; private persistence moves Φ by −2% to −7% (criterion 5%). **S3 partly passed:** a 30-min shared field gives Φ(10) = 2.3–2.8 (> 1.2 in 100%) but s_F > 0 is significant in only 60–90% (criterion 80%). **S4:** a 5-min field gives Φ(10) = 2.3–2.9 with s_F significant in 10–50%: a fast field cannot be told from a missed coupling by shape. **S5 passed:** with truth r_F = 1 the CI upper bound of r_F is below 2 in 100% of replicates; in field worlds (r_F ≈ 2.3–2.8) never. **2-day units (44b)** are imprecise (CI width 0.5–1.9; a 30-min field is absorbed by the hour blocks); their verdicts will mostly be descriptive.
- **Consequences stated before real data.** P3 (shape) has power 0.6–0.9 against a slow field and none against a fast one, so a P3 failure does not separate R2 from R3. A per-unit r_F within ±20% cannot be resolved (CI width 0.4–0.8 at T = 10); P1 is scored on unit counts as written, and the pooled regime-III r_F is reported next to it.

**Per-period verdict rule (replication):** on the period's random-effects pooled r_F at T = T* (10 min after A1; 15 min as written): **supported** if r_F ∈ [0.8, 1.2]; **failed** if r_F ≥ 2 or r_F ≤ 0.5; **mixed** otherwise; **descriptive** if the period has fewer than 40 usable windows or the CI of Φ(15) is wider than 1.0.

Native predictions are in `goalperiod-subhypotheses/NE42/`, `NE14/` and `NE43/` (written before those runs).

## Results by goal period
Per-period rule (card, T = 10 min after A1). **12 supported, 10 mixed, 13 descriptive, 0 failed** (35 periods, 66 units). Regime-III periods with resolution are all supported except #40 (mixed); regime-I/II excesses give the mixed verdicts; early regime I is descriptive (public-chat human sessions remove most windows).

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G02](goalperiod-subhypotheses/G02/README.md) | replication | descriptive | I: Φ(10) 0.62 [0.42, 0.81] · Φ_pred 1.04 · r_F 0.59 [0.43, 0.82] · 11 windows |
| [G03](goalperiod-subhypotheses/G03/README.md) | replication | descriptive | I: Φ(10) 1.78 [1.78, 1.78] · Φ_pred 1.03 · r_F 1.73 [1.43, 2.08] · 3 windows |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | descriptive | I: Φ(10) – [–, –] · Φ_pred 1.01 · r_F – [–, –] · 0 windows |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | descriptive | I: Φ(10) – [–, –] · Φ_pred – · r_F – [–, –] · 0 windows |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | supported | I: Φ(10) 1.00 [0.67, 1.32] · Φ_pred 0.99 · r_F 1.03 [0.73, 1.45] · 173 windows |
| [G07](goalperiod-subhypotheses/G07/README.md) | replication | descriptive | I: Φ(10) – [–, –] · Φ_pred 1.07 · r_F 0.51 [0.45, 0.57] · 3 windows |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | supported | I: Φ(10) 0.82 [0.65, 0.99] · Φ_pred 1.01 · r_F 0.81 [0.66, 1.00] · 199 windows |
| [G10](goalperiod-subhypotheses/G10/README.md) | replication | mixed | I: Φ(10) 0.70 [0.47, 0.92] · Φ_pred 1.00 · r_F 0.76 [0.52, 1.12] · 41 windows |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | descriptive | I: Φ(10) 1.32 [0.67, 1.98] · Φ_pred 1.06 · r_F 1.25 [0.74, 2.13] · 56 windows |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication | descriptive | I: Φ(10) 2.01 [1.40, 2.62] · Φ_pred 1.08 · r_F 1.85 [1.32, 2.60] · 47 windows |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | supported | I: Φ(10) 1.19 [0.90, 1.48] · Φ_pred 1.00 · r_F 1.20 [0.93, 1.54] · 111 windows |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | descriptive | I: Φ(10) 1.71 [1.12, 2.31] · Φ_pred 1.06 · r_F 1.61 [1.08, 2.41] · 60 windows |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | supported | I: Φ(10) 1.02 [0.75, 1.29] · Φ_pred 1.08 · r_F 0.95 [0.66, 1.36] · 68 windows |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | mixed | I: Φ(10) 1.69 [1.35, 2.03] · Φ_pred 1.09 · r_F 1.66 [1.33, 2.07] · 179 windows |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | mixed | I: Φ(10) 1.53 [1.29, 1.76] · Φ_pred 1.00 · r_F 1.55 [1.31, 1.84] · 205 windows |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | mixed | I: Φ(10) 1.56 [1.11, 2.01] · Φ_pred 0.99 · r_F 1.62 [1.21, 2.16] · 177 windows |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | supported | I: Φ(10) 1.14 [0.86, 1.42] · Φ_pred 0.97 · r_F 1.20 [0.93, 1.55] · 108 windows |
| [G23](goalperiod-subhypotheses/G23/README.md) | replication | descriptive | I: Φ(10) 1.74 [1.15, 2.33] · Φ_pred 0.93 · r_F 1.88 [1.30, 2.71] · 96 windows |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | mixed | I: Φ(10) 1.24 [0.90, 1.58] · Φ_pred 1.02 · r_F 1.22 [0.92, 1.62] · 82 windows |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | mixed | I: Φ(10) 1.38 [1.00, 1.76] · Φ_pred 1.02 · r_F 1.34 [0.99, 1.82] · 86 windows |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | descriptive | I: Φ(10) 2.07 [1.25, 2.89] · Φ_pred 1.02 · r_F 2.02 [1.30, 3.12] · 63 windows |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | supported | I: Φ(10) 1.06 [0.89, 1.23] · Φ_pred 1.01 · r_F 1.05 [0.88, 1.25] · 214 windows |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | mixed | I: Φ(10) 1.86 [1.53, 2.19] · Φ_pred 0.99 · r_F 1.84 [1.48, 2.27] · 93 windows |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | mixed | I: Φ(10) 1.44 [1.26, 1.61] · Φ_pred 0.94 · r_F 1.65 [1.41, 1.93] · 99 windows |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | mixed | II: Φ(10) 1.80 [1.37, 2.22] · Φ_pred 0.94 · r_F 1.90 [1.37, 2.65] · 50 windows |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | descriptive | II: Φ(10) 2.03 [0.80, 3.27] · Φ_pred 1.10 · r_F 1.86 [0.93, 3.71] · 101 windows |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication + NE14 | supported | II: Φ(10) 1.43 [1.10, 1.76] · Φ_pred 1.22 · r_F 1.15 [0.90, 1.47] · 103 windows |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | descriptive | III: Φ(10) 1.74 [1.17, 2.31] · Φ_pred 1.58 · r_F 1.10 [0.74, 1.64] · 49 windows |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | supported | III: Φ(10) 1.02 [0.77, 1.27] · Φ_pred 1.15 · r_F 0.92 [0.75, 1.14] · 281 windows |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication + NE42 | supported | III: Φ(10) 1.12 [0.71, 1.53] · Φ_pred 1.35 · r_F 0.83 [0.54, 1.27] · 66 windows |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication + NE42 | mixed | III: Φ(10) 1.24 [0.88, 1.61] · Φ_pred 1.01 · r_F 1.24 [0.84, 1.82] · 106 windows |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication + NE42 | supported | III: Φ(10) 1.28 [0.91, 1.66] · Φ_pred 1.49 · r_F 0.86 [0.60, 1.23] · 82 windows |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | supported | III: Φ(10) 1.16 [0.89, 1.44] · Φ_pred 1.36 · r_F 0.87 [0.66, 1.15] · 87 windows |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | descriptive | III: Φ(10) 1.53 [0.17, 2.89] · Φ_pred 1.65 · r_F 0.92 [0.02, 36.92] · 5 windows |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication + NE43 | supported | III: Φ(10) 1.40 [1.30, 1.50] · Φ_pred 1.39 · r_F 1.03 [0.94, 1.14] · 1441 windows |
| [NE42](goalperiod-subhypotheses/NE42/README.md) | native | failed | Φ(10) 1.12 → 1.24 → 1.28 (#39 → #40 → #41) against Φ_pred 1.35 → 1.01 → 1.49 |
| [NE14](goalperiod-subhypotheses/NE14/README.md) | native | descriptive | 36a Φ 1.36 [0.74, 2.30] (one day) → 36b ∪ 36c 1.42 [0.99, 1.85]; predicted rise 0.40 |
| [NE43](goalperiod-subhypotheses/NE43/README.md) | native | supported | trimmed Φ 1.46 → 1.45 → 1.53 (51f → 51g → 51h); untrimmed − trimmed (wall) +0.23 → −0.05 |

## Results
*Exploratory round 1, 2026-10-04: 66 non-holdout units in 35 periods; 41 units with ≥ 40 usable 10-min windows. Numbers from `data/processed/H111-talk-fano-sum-rule/results/{units,units_wall,periods}.parquet` and `summary.json`; synthetic from `synthetic/summary_final.json`. Code: `scheme/build.py`, `analysis/h111lib.py`, `synthetic.py`, `run_units.py`, `summarize.py`, `write_period_folders.py`, `confirm.py`.*

### Headline
Talk in regime III obeys a fluctuation–response sum rule with no free parameter. The collective Fano ratio of 10-min talk counts, Φ = Var(Σ n_i)/Σ Var(n_i), equals 1/(1 − g_lag)² computed from H67's read-out loop gain: **pooled r_F = 1.01 [0.94, 1.09]** over 18 regime-III units, with no between-unit spread. The read-out loop explains all collective talk clustering there; no field is left at 10–30 min. In regimes I and II, where g_lag ≈ 0, talk co-varies 1.34× [1.18, 1.52] more than the loop allows. That excess is fast and stays inside rooms.

### Outcome vs prediction
| # | Prediction | Observed | Outcome |
| --- | --- | --- | --- |
| S1 | coupling-only Φ(15) within ±20%, coverage ≥ 80% | final setting: g = 0.15 −3% to +1% (coverage 0.9); g = 0.30 −5% to −20% (0.5–0.7) | partly passed (A1) |
| S2 | no coupling: CI includes 1 in ≥ 85%; private persistence < 5% | 70–100%; −2% to −7% | partly passed |
| S3 | slow field: Φ > 1.2 and s_F > 0 in ≥ 80% | Φ > 1.2 in 100%; s_F significant 60–90% | partly passed |
| S5 | power: r_F = 2 distinguishable from 1 | CI upper < 2 in 100% when r_F = 1 | passed |
| P1 | regime III r_F ∈ [0.8, 1.2] in ≥ 2/3 of units | 14/18 (78%) with ≥ 40 windows; 18/25 (72%) of all finite; pooled 1.01 [0.94, 1.09] | **supported** |
| P1b | median E_F in [0.5, 2] | 0.77 (IQR 0.50–1.27; 17 units) | **supported** |
| P2 | untrimmed > trimmed in ≥ 2/3 (regime III) | 11/18 (61%); median gap +0.03; wall 9/18. Raw (day-demeaned, untrimmed) − trimmed: +0.22 | **failed** (the hour-block demeaning already removes the scheduler part) |
| K | kill: trimmed Φ ≥ 2 Φ_pred in > 1/2 (regime III) | 0/18 | **not met** |
| P3 | excess units: Φ(T) rises with T in ≥ 2/3 | 1/17 (median s_F 0.06) | **failed** (excess is fast; power vs a 30-min field 0.6–0.9, none vs a 5-min field) |
| P4 | regime I: Φ(10) > 1.2 in ≥ 2/3 | 13/21 (62%); pooled r_F 1.34 [1.18, 1.52] | **failed narrowly** |
| P5 | ρ(Φ − 1, g_lag) ≥ 0.3 across units | all regimes 0.09 (n 41); regime III 0.60 (p 0.008) | **failed** as written (regime-I field noise); holds in regime III |
| P6 | two-room units: within > cross in ≥ 2/3; cross > 0 in ≥ 1/2 | 10/12; cross > 0 (CI) in 0/12 | **mixed** (no cross-room field) |
| P7 | swarm call clock lowers Φ in ≥ 2/3 (regime III) | 13/18 (72%); median wall − per-call +0.06 | **supported** |
| P8 | F/F_shift within 10% of Φ in ≥ 90% | 20/41 (per-call), 21/41 (wall) | **failed** |
| N42a/b | NE42: Φ drops in #40 | −0.04 vs predicted 0.41; Δ_F +0.46 | **failed** |
| N14a/b | NE14 | 36a one day, CI 0.74–2.30 | uninformative |
| N43a/b | NE43: trimmed Φ flat; untrimmed excess falls | −0.01, +0.08; +0.23 → −0.05 (wall) | **supported** |

### Findings
1. **The sum rule closes in regime III.** Φ_pred has no free parameter: it uses H67's g_lag (a call-level read-out jump against an in-flight placebo) and the unit's present agents and rooms. The windowed count covariance matches it in pooled size (1.01 ± 0.08) and in rank across units (ρ 0.60). Two estimators of different statistics agree.
2. **The gain is first-generation, hop-1.** Using H67's hops 1–3 (not placebo-corrected) over-predicts Φ by a third (median r_F 0.66). The extra hops add no collective variance, so they are not causal offspring.
3. **Regimes I and II carry an excess of 0.3–0.9.** Median Φ(10) is 1.32 (I) and 1.92 (II) where Φ_pred ≈ 1. It does not grow from 5 to 30 min, so it is not a slow drive. H67 noted that regime-I talk runs on scheduled chat calls, so a hop-1 estimator may miss a later-hop coupling there; a fast field (conversation bursts) fits as well.
4. **No shared field across rooms.** In the 12 two-room units, agents in different rooms co-vary at ρ ≈ 0, within rooms at 0.03. A global field (schedule, outage, goal) would show across rooms.
5. **The scheduler excess is day- and hour-scale.** Trimming adds +0.03 on top of hour-block demeaning; removing the blocks adds +0.22. The operator's bookends were a visible field (NE43: +0.23 untrimmed in 51f, gone in 51g).
6. **Clocks.** On the real call grid, call density co-varies across agents (unit 41's synthetic Φ = 1.28 with no coupling on the wall clock). The per-call residual removes it; in real regime-III data the per-call Φ is 0.06 below the wall-clock Φ.

### Caveats
- Per-unit CIs are ±0.3–0.5 at 10 min, so the HH's ±20% per unit cannot be resolved one unit at a time; the pooled regime-III ratio carries the evidence.
- The estimator reads 5–20% low at g = 0.30 (synthetic); regime-III gains are 0.03–0.29, where the bias is ≤ 5%.
- A fast shared field (τ ≤ 5 min) and a missed coupling look alike in Φ(T). The regime-III match means neither is present beyond g_lag there, unless they cancel the small low bias.
- Early regime-I units (#2–#7) lose most windows to public-chat human sessions; they are descriptive.
- Predictions were written knowing H67's per-period g_lag and H25/H26/H86/H99 results.

**Claim that stands:** In regime III the 10-min collective Fano ratio of talk equals the parameter-free sum-rule prediction from H67's read-out gain, pooled r_F = 1.01 [0.94, 1.09] over 18 units with no between-unit spread (and Φ − 1 tracks g_lag, ρ 0.60), with zero cross-room covariance. *Excluded:* the regime-I/II excess (P4 failed narrowly; its cause, fast field vs missed coupling, is unidentified), NE42 (failed), the shape test (unpowered against fast fields), the HH-literal F/F_shift identity (failed), per-unit ±20% verdicts (unresolvable).

## Round 2 redirects
- **What the direction is really after:** a closure test that says, per period, how much collective talk variance the measured coupling explains and how much is field.
- **H111-R1. Regime-I clock.** Recompute Φ_pred with H67-R1's next-chat-call gain; if the excess closes, regime-I coupling sits at a later hop.
- **H111-R2. Fast-field separation.** Use the in-flight placebo at the window level (Φ of messages that could not be read vs those read) to split the regime-I excess into fast field and coupling.
- **H111-R3. NE42 #40.** Test whether #40's shared objective is the excess (goal-field regression on 10-min content) or a hidden named-message coupling (H67: named J₁* 0.04 in #40).
- **H111-R4. Holdout.** Run `confirm.py` after H67's confirm (C1–C4).


## Notes
- 2026-10-04 21:28 UTC: round 1 started; card filled before any real-data statistic. Compute: local, ≤ 2 workers, one heavy job at a time.
- 2026-10-04 21:31–21:40 UTC: scheme built (66 units, 24 MB; all-present windows identical to H67's on 4 checked units); synthetic validation; Amendment A1.
- 2026-10-04 21:41 UTC: period predictions written (35 folders); ~21:43–21:47 replication run (per-call and wall clocks, ~1 min each). A bug in the first summary compared untrimmed Φ at 10 min with trimmed Φ at 15 min (P2, NE14, NE43 gaps); fixed before any verdict was written. The shift null first left calls in place while moving messages (fixed: calls move with messages).
- Data: `data/processed/H111-talk-fano-sum-rule/` (≈ 25 MB). Estimates: 256 rows in `per_period_estimates` (statistics `collective_fano_ratio` on `talk_percall` and `talk_wall`, `sum_rule_ratio`, `sum_rule_prediction`, 4 native rows).
- Proposed for `physics-models/DEFINITIONS.md` (not edited): *collective Fano ratio Φ(T)*, *sum-rule prediction Φ_pred*, *sum-rule excess Δ_F*, *per-call residual clock*.
- Not computed as listed under Observables: item 8 (talk c_×w on the same windows); Φ − 1 is the same pair covariance in units of private variance, so it was not duplicated.
