# H03: Swarm activity is self-exciting, and its criticality is set by the goal's coupling mode

**Status:** running (exploratory round 1). Opened 2026-10-03 from shortlist entry S2 (ideas HH30, HH32).
**Fields:** dynamics, stat mech, sociophysics
**Literature:** model references in [`physics-models/09-hawkes/README.md`](../../physics-models/09-hawkes/README.md) (Hawkes 1971; Crane & Sornette 2008; Hardiman, Bercot & Bouchaud 2013; Filimonov & Sornette 2015; Bacry, Mastromatteo & Muzy 2015). No notes files exist yet in `literature/` for these.
**Definitions used:** Action; Regime; Driving / external field; Population N(t) (variant: *active population*, agents with ≥ 1 event in the realization); Clock time (fits use clock seconds since the day's window start). Village day: one PT day's active window from `calendar` (`win_start`, `win_end`) is one independent realization.

## Question
How much of the swarm's activity is self-generated (triggered by earlier agent events) rather than driven by the schedule, goal kickoffs and humans? Is the branching ratio n set by the goal's coupling mode (shared objective vs. free/holiday, etc.), and does the long private-role era (#51) drift toward criticality (n → 1) as the roster grows?

## Model
**From:** `physics-models/09-hawkes/` (primary), `physics-models/02-nonequilibrium-ising/` (directed-influence reading of the cross-agent kernel).

Each realization is one village day d, with time t ∈ [0, T_d] in seconds since `win_start`. Excitation never carries across days.

**M1 (primary, univariate pooled):** all agents' events pooled into one stream,

λ(t) = μ_B(t) + Σ_{x<t} Σ_r γ_r δ_r e^{−δ_r (t−x)} + Σ_{t_j<t} α β e^{−β(t−t_j)},  n = α.

- **Baseline μ_B (the Filimonov–Sornette guard).** Fits use a ladder, from weakest to strongest:
  - B0: one constant per period. This is the naive baseline, expected to fake criticality.
  - B1: one constant per day.
  - **B2 (primary):** per-day level × a within-day shape, piecewise constant in 30-min bins of time since window start and shared across the period's days, plus a kickoff bump on the goal's first day. The bump is Σ_k κ_k e^{−t/τ_k} with τ_k = 20 min and 2 h; every kickoff falls before that day's window opens.
  - B3: a free constant per (day, 30-min bin) cell. This is the most flexible baseline and gives a lower-bound-ish n.
- **Exogenous drive.** Human and automated (nudger) `USER_TALK` events x act on the swarm through a fixed-rate basis, δ_r⁻¹ ∈ {2, 10, 60} min, with amplitudes γ_r ≥ 0. Messages up to 1 h before the window opens count. This term is on in the primary fit, and a no-exogenous variant is reported.
- **Kernel.** Single exponential, with α and β fitted by maximum likelihood.
- **M2 (kernel shape):** a sum of exponentials on a fixed grid, τ_m ∈ {10 s, 30 s, 100 s, 300 s, 1000 s, 3000 s}, with free weights α_m ≥ 0 and n = Σ α_m. A power-law variant constrains α_m ∝ τ_m^{−θ}, a two-parameter approximation of φ ∝ τ^{−(1+θ)}.
- **M3 (self vs. cross):** each agent has its own intensity λ_a(t) = c_{a,d} s_b + exo + Σ_own φ_s + Σ_others φ_c, on the same fixed grid. The branching matrix is n_s I + n_c (J − I) over the m_d active agents, with spectral radius ρ = n_s + (m_d − 1) n_c. The social part is n_x = (m̄ − 1) n_c. M3 separates an agent's own action loop (a scheduler effect) from social triggering.

## Data scheme (`scheme/`)
- **Inputs:** the shared tables in `data/processed/shared/`:
  - `events_core`: t, pt_date, goal_no, actor_kind, agent, action_type;
  - `calendar`: win_start, win_end, goal_no, holdout;
  - `kicks`: goal_kickoff;
  - `roster`.
  No raw rescans.
- **Transform:** `scheme/build.py`:
  - keeps non-holdout days only, using `calendar.holdout` and `holdout_mask(pt_date, goal_no)`;
  - converts event times to seconds since `win_start`;
  - marks two event sets: **TALK** (`AGENT_TALK`) and **ALL** (every `actor_kind = agent` event);
  - collects exogenous `USER_TALK` events (human + automated) from 1 h before `win_start` to `win_end`.
- **Output:** `data/processed/H03-self-excited-criticality/`:
  - `events.parquet`: day_id, t_s, agent, talk;
  - `exo.parquet`: day_id, t_s, kind;
  - `days.parquet`: day_id, pt_date, goal_no, T_s, first_day, n_active, mode, regime;
  - fit outputs from `analysis/`.
- **Regimes covered:** I, II and III, fitted per goal period. No fit pools across the 2026-03-24 boundary except #51 rolling windows, which lie entirely in III.

## Observables
- **Branching ratio and timescale:** n (M1, B2) per non-holdout goal period, for TALK and ALL, with a day-level bootstrap 95% CI; kernel timescale 1/β.
- **Baseline ladder:** n under B0 → B3. Spurious criticality shows up as n falling as the baseline gets more flexible.
- **Kernel shape:** the M2 weight profile; power-law θ; how much of n sits at τ ≤ 300 s.
- **Self vs. social:** M3 n_s, n_x and ρ.
- **Phase diagram #1:** n over (mean active agents per day × median window hours), colored by coupling mode C/K/M/I/F/P.
- **#51 drift:** rolling 5-day windows through 2026-09-04. #51's tail from 09-07 is held out.
- **Cascades:** reconstructed cascade-size distributions (sampled branching trees), compared with Borel(n) and with s^(−3/2). A model-free burst-size distribution (gap threshold) is compared between data, Hawkes simulations and Poisson simulations.
- **Diagnostics:**
  - time-rescaling KS D, Hawkes vs. Poisson baseline;
  - day-blocked held-out log-likelihood, Hawkes vs. inhomogeneous Poisson with the same baseline;
  - synthetic recovery at n = 0 and n = 0.6, with village sampling.

## Null / baseline
- **Inhomogeneous Poisson** with the same B2 baseline and exogenous drive, n = 0. Hawkes must beat it on held-out days.
- **Synthetic guard:**
  - Poisson data simulated from each period's fitted baseline must return n̂ ≈ 0 under the full pipeline.
  - Fitting the same data with B0 shows the Filimonov–Sornette inflation.
  - A finer (10-min) baseline that B2 cannot represent probes misspecification.
- **Scheduler null (via M3):** if n is mostly self-excitation (n_s) and the social part n_x does not move with mode, an agent's own loop is what drives activity, not social coupling.

## Faithfulness scorecard
Scored per model, mapping and window: 0 = not done or failed, 1 = partial, 2 = passed. The scheme and promotion thresholds are in `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** inhomogeneous Poisson (pure schedule/exogenous drive); scheduler-only self-excitation (M3 with n_c = 0); model 03 contagion (same branching object, discrete-time).
**Locked holdout used for confirmation:** none yet. Candidates are C #15, #28, #45; F #9, #22; I #14, #43; K #29; #51 tail.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | | |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | | |
| C adequacy | beats the null hierarchy, day-blocked held-out data | | |
| D unfitted predictions | unfitted statistics and the model's signature | | |
| E interventional | predicts the change across a natural experiment | | |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | | |
| G ground truth | agrees with known structure | | |
| H comparative | beats the named rivals | | |
| I transfer | holds in other same-mode periods, including the holdout | | |

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
*Exploratory, non-holdout data only. Filled in below once the analysis is run.*

## Notes
- 2026-10-03: Card and predictions written before fitting. Holdout masked via `calendar.holdout` and `infra/shared/common.py: holdout_mask`. Every kickoff lands before its day's window opens (checked from `kicks` vs. `calendar`), so the kickoff bump starts at `win_start` of each goal's first day.
