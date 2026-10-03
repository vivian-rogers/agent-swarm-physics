# H03: Swarm activity is self-exciting, and its criticality is set by the goal's coupling mode

**Status:** running. Exploratory round 1 is complete (2026-10-03, non-holdout data only).
- **The mode/criticality claims fail.** S2's predictions P1–P5 are not supported: no period is near critical, n̂ does not depend on coupling mode, and #51 drifts away from criticality, not toward it.
- **n̂ is not identified.** Pooled n̂ (≈ 0.4) is subcritical in every period but depends on the baseline, and these tests cannot distinguish it from slow rate modulation.
- **Robust positive result:** fast cross-agent triggering, n_x ≈ 0.07–0.08 at τ ≈ 10–30 s. That is about 4× an agent-shift null, independent of mode, with per-pair strength falling with N.
- **Not promoted.** C = 1, so the hypothesis is below "descriptive".

**Fields:** dynamics, stat mech, sociophysics
**Literature:** model references in [`physics-models/09-hawkes/README.md`](../../physics-models/09-hawkes/README.md) (Hawkes 1971; Crane & Sornette 2008; Hardiman, Bercot & Bouchaud 2013; Filimonov & Sornette 2015; Bacry, Mastromatteo & Muzy 2015). No notes files exist yet in `literature/` for these.
**Definitions used:**
- Action;
- Regime;
- Driving / external field;
- Population N(t), variant *active population*: agents with ≥ 1 event in the realization;
- Clock time: fits use clock seconds since the day's window start;
- Village day: one PT day's active window from `calendar` (`win_start`, `win_end`) is one independent realization.

**Proposed DEFINITIONS variant (not yet added there):** *Action (turn-merged)*: an agent's `events` within 1 s of its own previous event count as one compound turn.

## Question
How much of the swarm's activity is self-generated (triggered by earlier agent events) rather than driven by the schedule, goal kickoffs and humans? Is the branching ratio n set by the goal's coupling mode (shared objective vs. free/holiday, etc.), and does the long private-role era (#51) drift toward criticality (n → 1) as the roster grows?

## Model
**From:** `physics-models/09-hawkes/` (primary), `physics-models/02-nonequilibrium-ising/` (directed-influence reading of the cross-agent kernel).

Each realization is one village day d, with t ∈ [0, T_d] in seconds since `win_start`. Excitation never carries across days.

**M1 (primary, univariate pooled):**

λ(t) = μ_B(t) + Σ_{x<t} Σ_r γ_r δ_r e^{−δ_r (t−x)} + Σ_{t_j<t} α β e^{−β(t−t_j)},  n = α.

- **Baseline μ_B (the Filimonov–Sornette guard)** is fitted on a ladder:
  - B0: one constant per period;
  - B1: one constant per day;
  - **B2 (primary):** per-day level × a 30-min within-day shape, plus a kickoff bump Σ_k κ_k e^{−t/τ_k} with τ_k = 20 min and 2 h on the goal's first day;
  - B3-2h: per-day 2-h cells;
  - B3-30m: per-day 30-min cells.
- **Exogenous drive.** Human and nudger `USER_TALK` events act through a fixed-rate basis, δ_r⁻¹ ∈ {2, 10, 60} min, with amplitudes ≥ 0.
- **Kernel.** Exponential, with α and β by maximum likelihood. The timescale is bounded to 1 s ≤ τ ≤ 20000 s; the variant `M1_B2_t30` uses τ ≤ 30 min.

**M2:**
- *Sum of exponentials:* fixed grid τ_m ∈ {10, 30, 100, 300, 1000, 3000} s with free weights.
- *Power-law variant:* α_m = n·w_m(θ), w_m ∝ τ_m^{−θ}.

**M3 (self vs. cross):**
- Each agent has its own intensity c_{a,d} s_b + exo + own-kernel + cross-kernel, on the M2 grid.
- The at-risk set is the agents active that day.
- n_self = Σ own weights; n_cross = (m̄ − 1) Σ per-pair cross weights.
- The **fast** parts (τ ≤ 300 s) are the reported ones, because slow components mimic co-modulation (see Notes).

All fits use L-BFGS-B in log-parameter space with analytic gradients. O(n) exponential recursions run in a small C helper (`analysis/hawkes_core.py`, compiled on first use).

## Data scheme (`scheme/`)
- **Inputs:** shared tables only:
  - `events_core`: t, pt_date, goal_no, actor_kind, agent, action_type;
  - `calendar`: windows and holdout;
  - `kicks`, inspected for timing;
  - `roster`.
- **Transform:** `scheme/build.py`:
  - keeps the 282 non-holdout days (`calendar.holdout` | `holdout_mask`);
  - converts event times to seconds since `win_start`;
  - defines **TALK** = `AGENT_TALK` and **ALL** = agent *turns* (every agent event, with same-agent repeats within 1 s merged; 93% of pooled gaps < 0.1 s were same-agent compound logging);
  - collects exogenous `USER_TALK` from 1 h before `win_start` to `win_end`.
- **Output:** `data/processed/H03-self-excited-criticality/`:
  - `days`, `events`, `exo`;
  - cross-period result tables;
  - one `G<NN>/` folder per goal period, with that period's extracts and `fits/`.
- **Regimes covered:** I, II, III, each fitted within a goal period. Nothing is pooled across periods.

## Observables
- n̂ and τ̂ per period, segment and event set, with a day-level bootstrap or profile CI;
- the baseline ladder;
- M2 kernel weights and power-law θ;
- M3 fast n_self and n_cross;
- the phase diagram (n̂ over N × hours, by mode);
- #51 segments and rolling windows;
- reconstructed cascade sizes and model-free burst sizes;
- time-rescaling KS;
- day-blocked held-out log-likelihood;
- synthetic recovery;
- surrogate tests: 10-min/2-min jitter and the agent-shift null;
- heterogeneity: Cochran Q and I².

## Null / baseline
- **Inhomogeneous Poisson** with the same baseline and exogenous drive (n = 0), with the B1, B2, B3-2h and B3-30m baselines.
- **Synthetic guard:**
  - n = 0 data generated from each period's fitted baseline must return n̂ ≈ 0;
  - B0 shows the Filimonov–Sornette inflation;
  - n = 0.6 and n = 0.9 must be recovered.
- **Scheduler-only rival:** M3 with cross weights fixed at 0.
- **Agent-shift null:** each agent's events circularly shifted by ±5–30 min, independently, breaking cross-agent timing while keeping each agent's autocorrelation.
- **10-min jitter null:** *added and then found to be powerless* (see results).

## Amendments
- **2026-10-03 · A1, unit of analysis (project rule).** The goal period is the unit, split at every step change inside it.
  - **Segments.** Step changes are every dated entry in `natural-experiments.md`, roster join/leave dates, and "Scaffold changes inside" dates in `goal-periods.md`. This splits 15 periods into 69 segments in total (`analysis/segments.py`). Each segment is fitted on its own.
  - **Partial pooling.** DerSimonian–Laird random effects within a period are reported **next to** the raw segment estimates (exception d: 14 segments are single days).
  - **Comparisons.** Periods are compared only through their fitted parameters (phase diagram; Mann–Whitney and regression on per-period points).
  - **Retained, secondary.** The original whole-period fits are kept: identical to the segment fits where there is no split, a secondary result where there is. The #51 rolling 5-day windows straddle roster joins and are secondary as well.
  - **Heterogeneity** is reported across periods, across adjacent periods and within periods.
- **2026-10-03 · A2, folder convention.** One `G<NN>/` folder per goal period with a verdict, role, prediction, result and per-period figure. Cross-period summaries stay in this card and in `figures/`. Every analysis script accepts `--period G38`, which writes to `data/processed/H03-self-excited-criticality/G38/`.

## Deviations from the written plan (all dated 2026-10-03; listed so nothing is hidden)
1. **ALL = turn-merged.** Decided from a structural tie audit before any fit.
2. **Added after seeing slow-kernel fits** (several τ̂ ≥ 30 min, i.e. the kernel mimicking the baseline): `M1_B2_t30` (τ ≤ 30 min) and the B3-2h rung. The pre-specified primary (M1_B2, τ ≤ 20000 s) is unchanged, and the predictions are scored on it. The variants give the same verdicts.
3. **Bug fixes found in diagnostics.**
   - Censored profile-likelihood upper bounds are now reported as ∞ rather than as the search cap.
   - In held-out evaluation, within-day shape bins never seen in training get the median shape value, and the transferred shape is floored at median/20. Six long-window days (two sessions with a gap) had produced absurd CV values, e.g. 7.4 nats/event for #37.
4. **Surrogate tests added after the synthetic guard** showed that B2 can be fooled by 10-min modulation:
   - 10-min and 2-min jitter of the pooled stream;
   - the agent-shift null for the cross kernel;
   - a power calibration of the jitter test (`jitter_power.py`), which **reversed** my first reading of the jitter result (see Results, finding 4).
5. **Fast-cross focus.** M3 is reported on its fast (τ ≤ 300 s) components, after the shift null showed that the slow (3000 s) cross component appears in shifted data too.
6. **Bootstrap size.**
   - Day-level bootstrap B = 100 (M1) and 50 (M2, M3) per period; the plan said 200.
   - The #51 whole period is capped at 33/16 replicates because of cost.
   - Segment bootstraps use B = 50 for segments of ≥ 3 days; shorter segments use profile CIs.

## Faithfulness scorecard
Scored per model, mapping and window: 0 = not done or failed, 1 = partial, 2 = passed. The scheme and thresholds are in `writeup/paper.tex`, Sec. "Assessing model faithfulness". Scores are for M1/M3 on non-holdout periods (exploratory).
**Rival models:** inhomogeneous Poisson (pure schedule/exogenous drive); scheduler-only self-excitation (M3 with n_c = 0); model 03 contagion (same branching object, discrete-time; not yet compared).
**Locked holdout used for confirmation:** none yet. Candidates are C #15, #28, #45; F #9, #22; I #14, #43; K #29; #51 tail.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Event times, windows, roster and exogenous messages all come from shared tables, and assumptions are listed. Not invariant: in regime III `events_core` lacks computer-use turns, so ALL changes meaning. The M3 at-risk set ignores rooms (after 2026-02-25). |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | **Time-rescaling:** Hawkes KS D is below Poisson's in 69% (TALK) / 71% (ALL) of periods, but Exp(1) is still rejected (p < 0.05) in 60% / 91%, with a heavy QQ tail (long silences). **Stationarity:** within-period stationarity fails: segment I² has median 0.43 / 0.61, and day-bootstrap CIs are much wider than profile CIs. **Scheduler audit:** sub-second compound logging was found and merged. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | **Same-baseline Poisson:** Hawkes beats it on day-blocked held-out data in 88% / 91% of periods (median Δℓ = 0.019 / 0.028 nats per event). **B3 30-min baseline:** median ≈ 0 for TALK (58% positive); 0.009 for ALL (85% positive). **Strongest null:** no powered test against a Poisson process modulated at 10–30 min (the jitter test has no power). |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | **Model-free bursts:** the tail of 60-s bursts is closer to the Hawkes simulation than to the Poisson one in 71% / 83% of periods, but the pooled differences are tiny. **Signature:** no s^(−3/2) anywhere, consistent with all n̂ being subcritical (reconstructed tail exponents 2.1–4.2). |
| E interventional | predicts the change across a natural experiment | 0 | Not attempted. NE21/NE23 are held out; NE10 (nudger on, inside #30) is the next step. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | **Recovery** with real windows and exogenous times: n = 0 → 0.00 (q90 0.024); 0.6 → 0.55; 0.9 → 0.86. **Filimonov–Sornette** reproduced: B0 gives 0.49 on n = 0 data. **Not robust:** to the baseline (median TALK n̂ is 0.61 under B0 and 0.16 under B3), and the pooled stream cannot separate excitation from 10-min modulation (jitter calibration). |
| G ground truth | agrees with known structure | 0 | Not done. |
| H comparative | beats the named rivals | 1 | **Poisson:** beaten, as above. **Scheduler-only rival:** cross-excitation improves held-out likelihood in 70% / 88% of periods, and fast n_cross exceeds the agent-shift null (Wilcoxon p = 2×10⁻⁹ / 4×10⁻⁸). **Contagion (model 03):** not compared. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | The mode-dependence claim fails already in exploration; I² within modes is 0.85–0.97. No holdout used. |

## Prediction
*Written 2026-10-03, before running any fit on real data. The schema and calendar/kickoff timing were inspected; no event dynamics were.*

Primary statistic: n̂ from M1 with baseline B2 + exogenous drive, on **TALK**, per non-holdout period. Non-holdout periods by mode:
- F: #2, 3, 5, 7, 11, 16, 31, 37
- C: #4, 8, 13, 18, 19, 24, 25, 26, 30, 33, 35, 36, 38, 40, 44
- I: #10, 17, 20, 21, 39, 41, 42
- K: #6, 23, 27
- M: #12
- P: #51, minus its tail

| # | Prediction | Counts against |
| --- | --- | --- |
| P1 | (HH30) Free/holiday periods are subcritical: median n̂_F < 0.5, and at most 2 of 8 F periods have n̂ ≥ 0.5 | median n̂_F ≥ 0.5, or ≥ 3 F periods with n̂ ≥ 0.5 |
| P2 | (S2) Shared-objective periods are more self-exciting than free ones: median n̂_C > median n̂_F, one-sided Mann–Whitney p < 0.05 | median n̂_C ≤ median n̂_F |
| P3 | (HH30, strong form) Shared-objective periods run near critical: median n̂_C ≥ 0.7 | median n̂_C < 0.7 |
| P4 | Mode, not just size and schedule: the C–F gap survives a regression of n̂ on log N_active, hours/day and regime | the C–F coefficient vanishes (|t| < 1) once N and hours are controlled → the scheduler drives activity |
| P5 | (HH32) #51 drifts toward criticality: n̂ rises with N_active across rolling 5-day windows (Spearman ρ > 0, p < 0.05), with n̂ ≥ 0.9 in the last non-holdout windows | ρ ≤ 0, or n̂ flat well below 0.9 |
| P6 | The social part follows mode: M3 cross-agent n_x is higher in C than in F (median) | n_x(C) ≤ n_x(F) |
| P7 | ALL-actions n̂ exceeds TALK n̂ in most periods, because an agent's own action loop self-excites (a scheduler effect, not social) | n̂_ALL ≤ n̂_TALK in most periods |
| P8 | Signature: only periods with n̂ > 0.8 show a cascade-size tail close to s^(−3/2) out to s ≳ 20; subcritical periods cut off exponentially | s^(−3/2) tails in clearly subcritical periods (the reconstruction would then be suspect), or no heavy tail anywhere despite n̂ > 0.8 |
| G1 | Guard: on n = 0 Poisson synthetics with the fitted baselines, the pipeline returns median n̂ < 0.05; B0 returns clearly larger n̂; n = 0.6 is recovered within ±0.1 | guard fails → no real-data n̂ is interpretable |

## Results
*Exploratory: 35 non-holdout goal periods (282 days), no holdout touched. Numbers come from `data/processed/H03-self-excited-criticality/summary.json` (`analysis/summarize.py`). Per-period detail is in the G folders.*

### Results by goal period
Primary n̂ is for TALK (M1, B2 + exogenous drive). The CI is the day-level bootstrap, or the profile likelihood for periods under 3 days. n_cross is the fast (τ ≤ 300 s) cross-agent part from M3. "Splits" counts the step changes inside the period. Verdict rules are stated in each G card: F → P1, C → P3, #51 → P5, I/K/M → descriptive.

| G | mode | regime | N | h/day | n̂ TALK [95% CI] | n̂ ALL | n_cross ≤300 s (TALK) | splits | verdict |
|---|---|---|---|---|---|---|---|---|---|
| [G02](G02/README.md) | F | I | 3.5 | 2 | 0.72 [0.61, 0.84] | 0.72 | 0.161 | 0 | failed |
| [G03](G03/README.md) | F | I | 4.0 | 2 | 0.66 [0.40, 0.72] | 0.70 | 0.070 | 0 | mixed |
| [G04](G04/README.md) | C | I | 4.0 | 2 | 0.55 [0.41, 0.63] | 0.56 | 0.085 | 2 | failed |
| [G05](G05/README.md) | F | I | 4.0 | 2 | 0.15 [0.00, 0.38] | 0.27 | 0.072 | 0 | supported |
| [G06](G06/README.md) | K | I | 4.0 | 2 | 0.65 [0.17, 0.81] | 0.46 | 0.122 | 1 | descriptive |
| [G07](G07/README.md) | F | I | 4.0 | 2 | 0.47 [0.29, 0.67] | 0.53 | 0.118 | 0 | mixed |
| [G08](G08/README.md) | C | I | 4.0 | 3 | 0.27 [0.10, 0.42] | 0.40 | 0.000 | 0 | failed |
| [G10](G10/README.md) | I | I | 7.0 | 3 | 0.22 [0.17, 0.59] | 0.48 | 0.069 | 1 | descriptive |
| [G11](G11/README.md) | F | I | 7.0 | 3 | 0.61 [0.36, 0.68] | 0.63 | 0.067 | 0 | mixed |
| [G12](G12/README.md) | M | I | 7.0 | 3 | 0.63 [0.39, 0.68] | 0.65 | 0.102 | 1 | descriptive |
| [G13](G13/README.md) | C | I | 6.0 | 3 | 0.57 [0.50, 0.61] | 0.52 | 0.024 | 0 | failed |
| [G16](G16/README.md) | F | I | 7.0 | 3 | 0.59 [0.20, 0.69] | 0.45 | 0.075 | 0 | mixed |
| [G17](G17/README.md) | I | I | 7.0 | 3 | 0.48 [0.25, 0.59] | 0.57 | 0.130 | 0 | descriptive |
| [G18](G18/README.md) | C | I | 7.5 | 4 | 0.70 [0.51, 0.80] | 0.70 | 0.075 | 2 | mixed |
| [G19](G19/README.md) | C | I | 7.1 | 4 | 0.69 [0.54, 0.74] | 0.66 | 0.107 | 1 | mixed |
| [G20](G20/README.md) | I | I | 9.2 | 4 | 0.62 [0.37, 0.71] | 0.42 | 0.112 | 3 | descriptive |
| [G21](G21/README.md) | I | I | 8.4 | 4 | 0.68 [0.09, 1.01] | 0.31 | 0.070 | 2 | descriptive |
| [G23](G23/README.md) | K | I | 10.0 | 4 | 0.10 [0.00, 0.23] | 0.26 | 0.062 | 0 | descriptive |
| [G24](G24/README.md) | C | I | 10.0 | 4 | 0.13 [0.00, 0.23] | 0.34 | 0.113 | 0 | failed |
| [G25](G25/README.md) | C | I | 9.8 | 4 | 0.38 [0.05, 0.45] | 0.37 | 0.107 | 0 | failed |
| [G26](G26/README.md) | C | I | 10.0 | 4 | 0.56 [0.42, 0.75] | 0.58 | 0.211 | 0 | mixed |
| [G27](G27/README.md) | K | I | 10.0 | 4 | 0.41 [0.00, 0.98] | 0.21 | 0.010 | 0 | descriptive |
| [G30](G30/README.md) | C | I | 12.0 | 4 | 0.28 [0.07, 0.36] | 0.43 | 0.099 | 1 | failed |
| [G31](G31/README.md) | F | I | 12.2 | 4 | 0.07 [0.00, 0.77] | 0.25 | 0.066 | 3 | mixed |
| [G33](G33/README.md) | C | II | 12.0 | 4 | 0.76 [0.00, 0.84] | 0.28 | 0.081 | 0 | mixed |
| [G35](G35/README.md) | C | II | 13.0 | 4 | 0.08 [0.00, 0.24] | 0.30 | 0.070 | 0 | failed |
| [G36](G36/README.md) | C | II/III | 13.0 | 4 | 0.29 [0.14, 0.37] | 0.18 | 0.008 | 2 | failed |
| [G37](G37/README.md) | F | III | 12.3 | 4 | 0.30 [0.25, 0.32] | 0.19 | 0.000 | 0 | supported |
| [G38](G38/README.md) | C | III | 12.4 | 4 | 0.32 [0.08, 0.61] | 0.57 | 0.020 | 4 | failed |
| [G39](G39/README.md) | I | III | 14.8 | 4 | 0.10 [0.00, 0.20] | 0.00 | 0.009 | 0 | descriptive |
| [G40](G40/README.md) | C | III | 15.0 | 4 | 0.00 [0.00, 0.07] | 0.00 | 0.000 | 0 | failed |
| [G41](G41/README.md) | I | III | 15.0 | 4 | 0.31 [0.12, 0.38] | 0.20 | 0.040 | 0 | descriptive |
| [G42](G42/README.md) | I | III | 15.6 | 4 | 0.20 [0.05, 0.27] | 0.02 | 0.053 | 1 | descriptive |
| [G44](G44/README.md) | C | III | 16.5 | 4 | 0.25 [0.00, 0.30] | 0.51 | 0.009 | 1 | failed |
| [G51](G51/README.md) | P | III | 26.5 | 8 | 0.54 [0.44, 0.61] | 0.59 | 0.026 | 9 | failed |

Verdict count: C 11 failed, 4 mixed; F 2 supported, 5 mixed, 1 failed; I/K/M 11 descriptive; P (#51) failed.

### Outcome vs. prediction

| # | Prediction | Observed (TALK primary; ALL in brackets) | Outcome |
| --- | --- | --- | --- |
| P1 | F subcritical: median n̂_F < 0.5, ≤ 2 of 8 ≥ 0.5 | median n̂_F = 0.53 [0.49]; 4 of 8 F periods ≥ 0.5 [4] | **not supported** (counts-against met) |
| P2 | C > F, Mann–Whitney p < 0.05 | median C 0.32 vs. F 0.53 [0.43 vs. 0.49]; p = 0.75 [0.68]. Segment points: C 0.28 vs. F 0.30, p = 0.65 | **not supported** (direction reversed) |
| P3 | median n̂_C ≥ 0.7 | 0.32 [0.43]; highest C period #33 = 0.76 (τ̂ = 2276 s, baseline-confounded) | **not supported** |
| P4 | C–F gap survives log N, hours, regime | mode_C coefficient −0.02 (t = −0.19) [+0.06, t = 0.74]; log N −0.53 (t = −2.06) [−0.26, t = −1.31]; R² = 0.37 [0.52] | **not supported** (counts-against met: \|t\| < 1). n̂ falls with N: ρ = −0.53 [−0.63] |
| P5 | #51: n̂ rises with N, ≥ 0.9 at the end | Segments between roster changes: ρ(n̂, N) = −0.64, p = 0.044 [−0.64, 0.044]; WLS slope −0.033 [−0.054] per agent; last segments 0.18–0.31. Non-overlapping 5-day blocks: ρ = −0.46, p = 0.21; last blocks 0.42–0.44 | **not supported** (opposite sign) |
| P6 | fast n_cross: C > F | 0.075 vs. 0.071, p = 0.59 [0.078 vs. 0.087, p = 0.64]; segments: 0.033 vs. 0.072 | **not supported** (null) |
| P7 | n̂_ALL > n̂_TALK in most periods | 54% of periods (B2); 57% (τ ≤ 30 min); 60% (M2 fast) | **inconclusive** (weak) |
| P8 | s^(−3/2) only where n̂ > 0.8 | no period has n̂ > 0.8. Reconstructed cascade tails are steep (exponent α̂ = 2.1–3.0 at s_min = 2, 2.6–4.2 at s_min = 5), with exponential cutoffs | **vacuous**: consistent, but untestable without a near-critical period |
| G1 | guard | n = 0 → B2 median 0.000 (q90 0.024); B0 → 0.49; n = 0.6 → 0.55 (74% of fits within ±0.1); n = 0.9 → 0.86 | **passes in-class**; B2 is not robust to finer modulation (see 4) |

### Findings
1. **Subcritical everywhere, far from critical.**
   - **Pooled n̂:** median 0.41 (TALK) and 0.43 (ALL), range 0–0.76. Kernel timescale τ̂: median 109 s (TALK) and 63 s (ALL).
   - **B3 lower bound:** B3 (30-min cells) gives medians 0.16 / 0.26. Synthetic recovery shows B3 is biased low (true 0.6 → 0.41 / 0.47), so the B3 bound corresponds to roughly n ≈ 0.2–0.3.
   - **Bracket:** n is roughly 0.2–0.4. No period sits near n = 1 under any baseline except the naive B0.
2. **Coupling mode does not set n̂; size and era do.**
   - **Mode:** median n̂ by mode for TALK is F 0.53, M 0.63, K 0.41, C 0.32, I 0.31. The mode coefficients are null once log N, hours and regime are controlled.
   - **Size:** n̂ falls with N (ρ = −0.53 / −0.63) and with hours/day, which are collinear with the calendar.
   - **Confound:** the early F weeks were small (N = 4–7), so mode is confounded with N and era across the non-holdout set.
   - **S2's implication:** if n doesn't depend on mode, the scheduler and roster, not social interaction, set the level.
3. **#51 moves away from criticality as it grows.** From 21 to 32 agents, n̂ declines across the segments between roster changes. The naive B0 baseline reaches n̂ ≈ 0.99 in some rolling windows, so a constant-baseline analysis would have "confirmed" HH32.
4. **Does the baseline defeat spurious criticality? Partly.**
   - **The gross artifact is removed:**
     - on n = 0 synthetic data with the schedule alone, B0 fakes n ≈ 0.49 and B2 returns 0;
     - on real data the median moves B0 0.61 → B1 0.52 → B2 0.41 → B3-2h 0.37 → B3 0.16 (TALK).
   - **The residual is not identified:**
     - a Poisson process whose rate follows the real 10-min counts gives B2 n̂ ≈ 0.48;
     - the 10-min jitter test, which seemed to say most of n̂ was such modulation (real minus jittered = +0.03 for TALK, p = 0.006; ≈ 0 for ALL, p = 0.33), **has no power**: jittering a synthetic n = 0.6 Hawkes process lowers n̂ by only 0.025 (`jitter_power.parquet`).
   - **Conclusion:**
     - the remaining n̂ is consistent with genuine triggering at n ≈ 0.4 and also with 10–30-min rate modulation;
     - these data and tests can't tell them apart in the pooled stream;
     - read B2 n̂ as an upper value and B3 as a biased lower bound;
     - the qualitative findings (subcritical; no mode effect; no #51 drift up) hold at both ends.
5. **Who triggers whom: mostly the agent itself; a small, real social coupling.**
   - **Own loop:** M3's fast n_self has median 0.11 (TALK) / 0.30 (ALL).
   - **Social coupling:**
     - fast cross-agent excitation n_x: median 0.070 / 0.081, against 0.017 / 0.024 under the agent-shift null;
     - real exceeds all 5 surrogates in 80% / 74% of periods (Wilcoxon p = 2×10⁻⁹ / 4×10⁻⁸);
     - the cross weight sits at τ ≈ 10–30 s, i.e. a reply, or a scheduler wake-up on a new message (the data cannot yet tell which);
     - n_x does not depend on mode;
     - per-pair strength falls steeply with N (ρ = −0.73 / −0.69), so total social triggering per event stays at ~0.05–0.1 or declines: attention-limited coupling.
   - **#51:** fast TALK cross-excitation falls toward 0 by late August (block ρ with N = −0.90). Caveat: the at-risk set ignores rooms.
6. **Humans and the nudger drive little directly.** Exogenous messages account for a median 1.5% of agent events (up to 10–13% in a few early periods), and kickoffs for 0.4%. The baseline (schedule) accounts for about half, and triggering for the rest (model-based shares).
7. **Kernel shape.**
   - The single exponential is adequate: the six-weight sum-of-exponentials grid is not better (median ΔAIC +8; held-out ≈ 0).
   - The power-law-constrained kernel fits worse than the exponential in 94% / 89% of periods (median Δℓ −10 / −16).
   - There is no long-memory kernel signature.
8. **Heterogeneity is large (consistent with H04).**
   - **Across periods:** I² = 0.95 (τ = 0.25 in n), and 0.85–0.97 within each mode.
   - **Adjacent periods:** 27% / 30% of pairs differ at |z| > 1.96; median |Δn̂| = 0.13.
   - **Within split periods:** median I² across segments 0.43 / 0.61; 23% / 46% have Cochran p < 0.05. #51: I² = 0.86 / 0.94.
   - **Interpretation:** n̂ is a per-period quantity. A single "swarm branching ratio" would be meaningless.

### Figures (`figures/`)
- `phase_diagram.pdf`: n̂ vs. N (size = hours/day; #51 blocks as ★) and the N × hours plane filled by n̂; color and marker = mode.
- `segments_phase.pdf`: segment estimates (open) next to the partially pooled ones (filled); #51 segments vs. N.
- `baseline_ladder_and_guard.pdf`: per-period n̂ across baselines, and synthetic recovery per baseline.
- `rolling51.pdf`: #51 rolling windows (secondary) with the naive B0 overlay; fast self/cross; N.
- `self_vs_cross.pdf`: fast own-loop vs. social excitation per period.
- `kernels.pdf`: M2 weights by mode.
- `cascades.pdf`: reconstructed cascade CCDFs vs. Borel(n̄); model-free burst CCDFs (data / Hawkes / Poisson).
- `diagnostics.pdf`: KS distances; day-blocked CV.
- Per period: `G<NN>/figures/diagnostics.pdf`.

### Caveats
- **Identifiability.** Pooled n̂ is not identified against 10–30-min rate modulation. Only the M3 fast cross term has a null it clearly beats.
- **Regime III mapping.** `events_core` has no computer-use turns, so ALL means something different there. The `actions` table would be needed.
- **Rooms.** The M3 at-risk set includes agents in other rooms after 2026-02-25, which dilutes the per-pair n_c.
- **Long-window days.** Six days are long windows (two sessions with a gap). They distort the B2 shape and CV. Splitting days at long silences is the fix.
- **Short segments.** Segments of 1–2 days rely on profile CIs, which ignore day-to-day variability.
- **Bootstrap.** Day-bootstrap CIs are often bimodal, with mass at 0. The #51 whole-period bootstrap is small.
- **Mode confounding.** Mode is confounded with N and era; F weeks are early and small.
- **Multiplicity.** Many models and variants were tried (all listed above).
- **Cascades.** Reconstructed cascades are model-conditioned.
- **Modes.** Mode codes are our own coding, from `goal-periods.md`.

### Next steps
1. Split days at silences longer than 1 h (scheme fix), then rerun.
2. Make M3 room-aware, using `exposure` / `rooms_timeline` for the at-risk set; then test whether n_x is a reply effect (mention or addressed messages) or a scheduler wake-up (lag distribution against the 10–30 s scheduler cadence).
3. Get a powered test of event-locked vs. modulated activity:
   - per-agent jitter at short scales (own loop), with power calibrated on synthetic data;
   - a Cox-process rival with a latent 10-min rate fitted directly (H comparative).
4. Use the `actions` table for regime III turns, and fit a nonlinear/inhibitory Hawkes (PAUSE/WAIT; agents can't act while waiting on a model call).
5. Run E on non-holdout NE10 (nudger on, inside #30): does the exogenous kernel for automated messages appear?
6. Write confirmatory predictions for the holdout before touching it:
   - fast n_x is 0.03–0.12 above the shift null, independent of mode, in #15, #28, #45, #9, #22, #14, #43, #29;
   - n̂ (B2) < 0.8 in every held-out period;
   - the #51 tail continues n̂ ≤ 0.45.
7. Propose for `physics-models/09-hawkes/README.md` (pitfalls):
   - an unpowered jitter test;
   - slow cross kernels mimic co-modulation;
   - day windows with gaps.

## Notes
- 2026-10-03: Card and predictions written before fitting. Holdout masked via `calendar.holdout` and `infra/shared/common.py: holdout_mask`. Every kickoff lands before its day's window opens (checked from `kicks` vs. `calendar`), so the kickoff bump starts at `win_start` of each goal's first day.
- 2026-10-03: Slow kernels (τ̂ ≥ 30 min) appeared in 2 (TALK) / 3 (ALL) periods, e.g. #33 TALK τ̂ = 2276 s and #37 ALL 17086 s. They are confounded with the baseline, hence the τ ≤ 30 min variant (same verdicts).
- 2026-10-03: In M3, slow cross components (τ = 3000 s) appear at similar size in agent-shifted surrogates (#30). They are co-modulation, not triggering. Fast components (10–30 s) vanish under shifting (#18: 0.075 → 0.015).
- 2026-10-03: The jitter test was first read as "most of n̂ is ≥ 10-min modulation". The power calibration (`analysis/jitter_power.py`) shows a true n = 0.6 process also loses only 0.025 under 10-min jitter, so that reading was withdrawn before writing results.
- 2026-10-03: Code map:
  - `scheme/build.py`;
  - `analysis/hawkes_core.py` (model, C recursions, simulation, KS, cascades);
  - `fit_periods.py` (fits, KS, CV; `--cv-only`);
  - `bootstrap.py`, `synthetic_guard.py`, `rolling51.py`, `segments.py`, `jitter_test.py`, `jitter_power.py`, `cascades.py`, `attribution.py`;
  - `summarize.py`, `figures.py`, `figures_period.py`, `split_by_period.py`, `write_period_cards.py`, `card_tables.py`;
  - `test_core.py` (unit tests).

  Every multi-period script accepts `--period G<NN>`.
