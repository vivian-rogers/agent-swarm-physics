# H09: Agent swarms have an effective thermodynamics

**Status:** **Round 1b (2026-10-04, fixed bins, context ledger):**
- E1's regime-III excess is day edges (trimmed VR 1.22);
- the timer gate is context-read: chatter keeps agents paused (OR 0.50), an @-mention releases them (OR 3.1), and NE43 leaves the gate unchanged;
- memory is a homeostat with overshoot (φ −0.22 after forced erasures; HH269), and it does not follow read inflow.

Round 1: exploratory rounds 1 (E1–E5) and 2 (E6–E8) done, light. Observable tables built (`idle_runs`, `consolidation_inflow`). Not promoted. Opened 2026-10-03 at Vivian's request.
**Fields:** stat mech, thermodynamics, dynamics, info theory
**Literature:** [Aguilera, Ito & Kolchinsky 2026](../../literature/aguilera-2026-entropy-production-nonequilibrium-maxent.md) (entropy production); [Kolchinsky 2024](../../literature/kolchinsky-2024-dissipation-does-not-bound-replicator-rates.md) (caution on dissipation bounds); [Piñero et al. 2025](../../literature/pinero-2025-neutral-theory-cooperative-dynamics.md), [2026](../../literature/pinero-2026-information-bounds-replicator-production.md)
**Definitions used:** Regime; Action; Activity time; Agent state (categorical); see [`../hypohypotheses/statmech-primitives.md`](../hypohypotheses/statmech-primitives.md).

## Question
Can the swarm be described with the working parts of thermodynamics:
- free-energy landscapes over states;
- temperature-like and field-like control parameters, with susceptibilities;
- chemical potentials;
- metastable traps and activation barriers;
- probability currents and entropy production;
- work done by operators, and an equation of state for memory?

And do those descriptions predict anything that simpler statistics don't?

## Sub-hypotheses (from the idea pool; HH numbers are permanent)
| | Claim | Ideas |
| --- | --- | --- |
| T1 | Stationary occupancies define a free-energy landscape with basins and barriers; enthalpic vs. entropic favorability can be separated | HH47, HH48, HH54, HH59 |
| T2 | Goals act as Legendre-conjugate fields: free weeks give F, goal weeks follow G = F − h·m; susceptibility measurable | HH49, susceptibility sections of models 01, 02, 11 |
| T3 | Rooms and projects have chemical potentials; rooms are grand-canonical subsystems | HH50, HH60 |
| T4 | Goals couple uphill work to a drive (ATP analogy); some interventions are catalysts (rates), others fields (occupancies) | HH51, HH52 |
| T5 | Idle loops and spirals are metastable traps with barrier-controlled escape; restarts show aging | HH53, HH02 |
| T6 | Action cycles carry probability currents; irreversibility is collective | HH56, HH67, HH19, HH45 |
| T7 | Agents are non-ergodic; timescale separation permits coarse-graining | HH55, HH61 |
| T8 | Goal switches do work; fast switches dissipate more | HH63, HH07 |
| T9 | Memory has an equation of state (volume vs. information pressure) | HH57, HH12 |
| T10 | An effective temperature exists (fluctuation–dissipation ratio) and differs by regime and family | models 01 and 02, H08 |

## Mean-field-forward variants (added 2026-10-03)
- **T1/T2-MF:** the Curie–Weiss free energy f(m) = −J₀m²/2 − hm − T s(m), with βJ₀ from the two-moment inversion. It predicts a double well iff βJ₀ > 1, and hysteresis under field reversal. Compare with the Boltzmann-inverted landscapes (E1). The goal field then tilts f: fit on field-free periods, predict fielded ones (HH86, HH49).
- **T5-MF:** timer-gated idling (round 2): the escape probability at the timer gate is a mean-field function of directed kicks (mentions); 1–2 parameters per regime.

## Model
**From:** models 01, 02 (entropy production, response), 09 (kinetics), 10 (occupancy over categorical states), 06/07 (built-in free energies). The framing is model-agnostic; each T needs its own model choice when promoted.

## Data scheme (`scheme/`)
Uses the shared Phase 0 tables (`infra/shared/` → `data/processed/shared/`): `events_core`, `activity_bins`, `calendar`, `kicks`. H09-specific scripts in `analysis/`. Exploratory work **excludes the locked holdout** ([`../holdout.md`](../holdout.md)).

## Exploratory measurements
These are descriptive and exploratory: they calibrate ideas, they don't confirm them. Confirmation happens later, on the holdout.

| | Measurement | Ideas served |
| --- | --- | --- |
| E1 | Activity landscape: G(K) = −ln P(K) over the number of active agents per 1-min bin, per regime, vs. an independent-agent (binomial) null | T1, HH47 |
| E2 | Action-class currents: per-agent Markov chains over action classes; entropy production per transition; dominant cycles; regime I vs. III | T6, HH56 |
| E3 | Ergodicity breaking: per-agent time-averaged action mix vs. the population; between- vs. within-agent variance; family clustering | T7, HH55 |
| E4 | Idle traps: dwell times of WAIT/PAUSE runs; tail shape; escape rate vs. kicks; the nudger switching on (NE10) as catalyst vs. field | T4, T5, HH52, HH53 |
| E5 | Daily restarts: relaxation of activity after each day's start vs. the preceding idle gap (overnight vs. weekend) | T5, HH02 |

## Prediction (exploratory)
*Written 2026-10-03, before any of these measurements were run.*
- **E1:** P(K) is wider than the binomial null: variance ratio Var(K)/Var_binomial > 1.5, with excess weight at both high and low K. That means collective co-activation, not independent agents.
- **E2:** every agent with enough data has entropy production per transition significantly > 0 against time-reversal (shuffled-order surrogates). Regime III has a dominant cycle through consolidation.
- **E3:** between-agent variance of the action mix exceeds within-agent (across-window) variance by ≥ 2×, i.e. non-ergodic. Model family explains a significant share of the between-agent variance.
- **E4:** idle dwell times are heavy-tailed (coefficient of variation > 1, not exponential). After the nudger switches on, the mean dwell time shortens more than the idle fraction does: a catalyst signature.
- **E5:** the activity relaxation time after a restart is longer after weekends than after overnight gaps.

### Round 2 (E6–E8)
*Written 2026-10-03, before any E6–E8 measurement was run.* Only structural checks came first: schemas, row counts, which fields are non-null by regime, token-accounting conventions, the roster and rooms of the E7 window. All on non-holdout days.

**E6 · Idle traps, done properly (T5, HH53).**
- **Definitions.**
  - *Idle spell:* a maximal run of one agent's consecutive idle events (WAIT or PAUSE). It ends at the agent's next non-idle action: any other `events_core` agent event, or any computer-use turn in `actions`. A spell still open at the end of the day's window is right-censored.
  - *Data by regime:* regime III has PAUSE spells with declared durations (`pause_s`); regime I has WAIT spells.
  - *Kicks during a spell:* messages by others in the agent's room (`exposure`), split into agent, human and automated (nudger) messages, and messages that @-mention the agent.
- **E6a · tail.** Realized dwell is heavy-tailed (CV > 1) in both regimes. Fits by censored maximum likelihood above a common x_min (the median), comparing exponential, power law, lognormal and stretched exponential (Weibull):
  - lognormal or stretched exponential wins by AIC, with ΔAIC > 10 over the power law;
  - so there is no scale-free trap.
- **E6b · declared vs. realized.**
  - At least 50% of declared PAUSE durations are whole minutes.
  - At least 25% of pauses end more than 30 s before their declared expiry, so escape is not set by the agent's own timer alone.
- **E6c · Kramers kicks.**
  - *Hazard ratio.* Fit a discrete-time hazard per minute at risk, stratified by elapsed dwell and position in the day (Mantel–Haenszel). The escape hazard is higher in minutes with a room message than in minutes without: HR ≥ 1.5 in both regimes.
  - *Null.* The HR beats the 95th percentile of a null that replaces each agent's kick timeline with the same agent's timeline from a random other day of the same regime, at the same clock offset. This keeps the schedule-level kick density.
  - *By kick type.* @-mentions have a larger HR than undirected room messages, and nudger messages have HR > 1.
  - *Rate curve.* With spells binned by kick rate, the escape rate rises monotonically and has a positive intercept: Kramers-like k = k₀ + c·r.
- **E6d · family.** Lab explains ≥ 30% of the between-agent variance of log median realized dwell (regime III).

**E7 · Is irreversibility collective? (T6, HH67).**
- **Window.** 2026-07-24 → 08-28 (end exclusive): 25 days, all goal #51, non-holdout; 27 agents, effectively all in #general.
- **States.** From `activity_bins`: silent / idle / act / talk, using minutes 10–469 of each day so start and stop ramps drop out.
- **Estimator.** The MaxEnt EP lower bound of Aguilera et al., in its forward-sample dual form (antisymmetric observables, stationarity assumed).
  - Fitted by L-BFGS with an L2 penalty, chosen by inner CV.
  - Evaluated on held-out days, with 5-fold blocks of whole days.
- **Observables.**
  - *Single agent:* antisymmetrized one-step transition indicators of the 4-state chain (6 per agent).
  - *Pairwise:* antisymmetrized lagged cross-products x_{i,t+1}x_{j,t} − x_{i,t}x_{j,t+1} of activity (state ≥ 3) and of talk (2 per pair; 702 in all).
- **Quantities.**
  - Σ₁ = the sum of the per-agent held-out bounds.
  - Σ₁₊₂ = the joint held-out bound with all observables.
  - ΔΣ = Σ₁₊₂ − Σ₁ is the collective term.
- **Nulls.**
  - (i) *Day mismatch:* each agent's series is taken from a different day. This keeps single-agent dynamics and the daily schedule and destroys cross-agent timing.
  - (ii) Minute-shuffled test data, for single agents.
  - (iii) Time-reversed test data: the fitted θ should give a negative bound.
- **Predictions.**
  - **E7a:** ≥ 80% of agents have a held-out Σ_i > 0 that beats the minute-shuffle null.
  - **E7b:** ΔΣ > 0 on held-out days, above the 95th percentile of null (i). Collective irreversibility exists: the weak form of HH67.
  - **E7c:** the strong form fails, ΔΣ < Σ₁. The collective term is smaller than the sum of single-agent terms; ΔΣ/Σ₁ is expected between 0.1 and 0.5.
  - **E7d:** the per-pair collective term ΔΣ_ij (pair fitted alone) rises with how often the two agents @-mention each other in the window: Spearman ρ > 0.2.
  - **E7e:** the collective term per agent, ΔΣ/N, rises with the size N of random agent subsets (N = 4 → 27), so total EP is superlinear in N.

**E8 · Memory equation of state (T9, HH57).**
- **Unit.** One memory snapshot: a `memory_stats` row on a non-holdout day whose previous snapshot (same agent) is on the same PT day.
- **Volume.** V = n_chars (n_lines as a check).
- **Inflow over the interval (t_prev, t].**
  - P_msg: messages by others in the agent's room (`exposure`).
  - P_tok: uncached input tokens. For Anthropic-style accounting, tok_in already excludes cache reads, so P_tok = tok_in + tok_cache_write. For Gemini-style inclusive accounting, P_tok = tok_in − tok_cache_read. Only Claude and Gemini agents report tokens.
- **Turnover.** lines_removed, and 1 − jaccard_prev.
- **E8a · no simple equation of state at the snapshot level.**
  - The within-agent elasticity d ln V / d ln P is small (|b| < 0.1) for both inflow measures, with agent × goal-period fixed effects.
  - Between-agent differences dominate: agent identity explains > 70% of the variance of ln V in regime III, and lab > 30%.
- **E8b · saturation.** For ≥ 60% of agents with ≥ 200 regime-III snapshots, ln V grows less than 20% as much over the last third of tenure as over the first third.
- **E8c · compression under pressure.** Within agent × goal:
  - Spearman ρ(P_msg, 1 − jaccard_prev) > 0.1;
  - ρ(V_prev, lines_removed) > 0.2;
  - ΔV = βP − γV_prev + FE has γ > 0 and β > 0, i.e. an equilibrium volume V* that rises with inflow.
- **E8d · NE14 jump.**
  - *Windows:* before is 03-16 → 03-23, the non-holdout end of regime II. After is 03-24 → 04-01.
  - *Prediction:* for a majority of agents present on both sides, snapshot rate per active hour, median V and median turnover each change by ≥ 25% (|Δ ln| > 0.22). Expected directions: fewer snapshots per hour, larger V, more turnover per snapshot.
  - *Confound:* NE16 (03-26, the "never update memory" fix) falls inside the after window, so 03-24–25 and 03-26 → 04-01 are reported separately.

## Faithfulness scorecard
Exploratory phase: not scored yet. Each T gets its own card and scorecard when promoted.

## Results
### Exploratory round 1 (2026-10-03; non-holdout days only: 282 used, 107 excluded)
Script: `analysis/explore_e1_e5.py`. Numbers: `data/processed/H09-swarm-thermodynamics/explore_e1_e5.json`. Figures: `figures/`. Scored against the predictions written above.

| | Prediction | Outcome | Verdict |
| --- | --- | --- | --- |
| E1 | variance ratio Var(K)/independent > 1.5 | median VR 1.25 (regime I, 180 days), 1.22 (II, 9 days), **1.61 (III, 93 days)**; days with VR > 1.5: 22%, 22%, 59% | **holds in regime III only** |
| E1 | landscape shape | at the modal N (I: 4 agents; III: 27), G(K) in III has two wells (quiet; ~40% active), but the time-varying independent null **reproduces them**. The wells come from the schedule; co-activation appears only below ~30 min | the field explains the landscape |
| E2 | entropy production > null for every agent | 47 of 60 agent × regime cells (78%) above the shuffled-null 95th percentile. Median per step: I 0.10, II 0.71 (few cells), **III 0.0075** nats | mostly; event-level irreversibility **collapses after perma-computer-use** |
| E2 | a dominant cycle through consolidation in III | net fluxes form a closed cycle **consolidate → search → talk → pause → consolidate** (631, 405, 279, 446 net transitions) | **supported** |
| E3 | between/within ≥ 2 (non-ergodic) | ratios 0.3–1.8 for all classes (talk 1.1; pause 0.3 in I, 1.8 in III) | **not supported** at the day scale |
| E3 | model family explains between-agent variance | lab share: pause 77% (I); talk 46%, consolidate 41%, search 48% (III) | **supported** |
| E4 | heavy-tailed idle dwell | CV 3.8; tail far above an exponential with the same mean | **supported** (but median dwell 0 s: many WAITs are followed at once by another event; use declared pause durations next) |
| E4 | nudger as catalyst (NE10) | inconclusive: most of the 2-week window before it is in the holdout (#28, #29), leaving 81 runs | **untestable in exploration** |
| E5 | slower relaxation after weekends | the plateau is reached within the first minute after both overnight and weekend gaps (k ≈ 0.52 vs. 0.56) | **not supported** at 1-min resolution; the scheduler starts everyone at once |

**Caveats.**
- In regime III most activity moved into computer-use turns, so event-level sequences are a coarser view; the drop in entropy production may be partly a coarse-graining effect.
- Regime II is mostly in the holdout (9 days).

**Next.** Declared-duration idle traps; joint vs. single-agent entropy production from activity bins (HH67); memory equation of state (HH57) from `memory_stats` plus token inflow.

### Exploratory round 2 (2026-10-03; non-holdout days only; light pass)
Scope was cut mid-round to "observables first, quick descriptive numbers, no heavy fitting":
- E6 ran as planned.
- E7 got one quick plug-in pass. The held-out MaxEnt estimator is deferred until H05's EP estimator is available.
- E8 is descriptive.

Everything here is **exploratory**.
- **Scripts** (in `analysis/`): `build_observables.py` (tables), `explore_e6_idle_traps.py`, `explore_e7_e8.py`.
- **Numbers:** `explore_e6_idle_traps.json` and `explore_e7_e8.json` in `data/processed/H09-swarm-thermodynamics/`.
- **Figures:** `figures/E6_idle_traps.pdf`, `E7_pairwise_irreversibility.pdf`, `E8_memory_eos.pdf`.

**Two definitional findings came first.**
1. **Regime-I WAIT is logged at the end of the gap, not its start.** In 82% of WAIT runs the WAIT event is logged < 1 s before the agent's next action. So a regime-I idle spell is measured as the gap from the previous non-idle action to the next one.
   - Gaps containing a WAIT: median 51 s.
   - Gaps without one: median 44 s, and the without-WAIT gaps have the longer tail (p90 498 s vs. 178 s).
   - So regime-I WAIT is a turn-scale event, not a trap.
2. **`actions` has a `pause` turn mirroring every PAUSE event**, about 0.1 s before it. It must be dropped, or each pause "ends" immediately.

| | Prediction | Outcome | Verdict |
| --- | --- | --- | --- |
| E6a | heavy tail, CV > 1; lognormal or stretched exp beats power law by ΔAIC > 10 | CV 1.47 (I), 2.48 (III). Above the median dwell, lognormal wins in both regimes; the power law is +478 (I) and +850 (III). Above p90: in I the power law (α ≈ 3.0), lognormal and stretched exp are tied within ΔAIC 2.2; in III stretched exp wins (β ≈ 0.18) and the power law is +20 | **holds**, except in regime I's deep tail, where the fits can't be told apart |
| E6b | ≥ 50% of declared pauses are whole minutes | 65% (modes 300, 60, 120, 30, 600 s; median 180 s); the 12-h default appears in 0.004% | **holds** |
| E6b | ≥ 25% of pauses end > 30 s early | **0.22%**. A pause ends at its declared expiry plus a median 14 s turn latency (realized/declared 1.07). The 61 early wakes have a room message in the prior 60 s about as often as the day-swap null (77% vs. null p95 75%) | **refuted**: a regime-III pause is a timer that messages don't interrupt |
| E6c | HR (room message in the prior 60 s) ≥ 1.5 in both regimes, above the day-swap null | **I: 3.06** (CI 2.68–3.49; null median 0.91, p95 0.96). III: **0.93** (CI 0.88–0.98; null p95 0.99) | **regime I only** |
| E6c | @-mentions > undirected messages; nudger HR > 1 | III: mention **1.52** (CI 1.37–1.65; null p95 1.26) vs. undirected 0.90; nudger 1.02 (n.s.). I: mention 1.05 < undirected 2.45; nudger 2.15 (null p95 1.41; only 0.2% of bins) | **split**: in III only directed kicks work, and they act at the timer-expiry decision (stay paused or act) |
| E6c | Kramers-like escape rate k = k₀ + c·r, rising with kick rate | I: rises, k₀ 0.40 /min, c 0.11 per (msg/min), ρ = 0.22. III: **falls** (ρ = −0.13). The peri-escape message density in regime I spikes in the ~20 s before escape (2.0× the null); flat in III | **regime I only** |
| E6d | lab explains ≥ 30% of between-agent variance of log median dwell | 0.41 (III; 27 agents, 8 labs), 0.46 (I); but chance under label permutation is 0.26 and 0.23 (p = 0.12, 0.17). Large lab gaps exist: Moonshot median 1,625 s vs. Google and DeepSeek ~80 s | **not above chance** |
| E7a | ≥ 80% of agents have single-agent EP above the minute-shuffle null | 85% (23/27). Median 0.0098 nats/min for the 4-state chain; OpenAI highest (0.020), Google lowest (0.003) | **holds** (plug-in, not held-out) |
| E7b | collective term > 0, above the day-mismatch null | Pair excess ΔS_ij − null: median +0.0002 nats/min; **15%** of 351 pairs are above the null p95 (5% expected) | **weakly holds** (plug-in) |
| E7c | collective term < Σ single (ratio 0.1–0.5) | Σ over pairs of excess / Σ_i S_i = **0.21** | **holds** (a crude pairwise-additive proxy, not a joint bound) |
| E7d | pair excess vs. mutual @-mentions, ρ > 0.2 | ρ = 0.13 (p = 0.016) | **positive but below the threshold** |
| E7e | per-agent collective EP rises with N | not run | **deferred** |
| E8a | within-agent elasticity \|b\| < 0.1 | ln V vs. ln(1+P_msg): **0.16**. ln V vs. ln(1+P_tok): 0.024. But P_msg tracks interval length (ρ = 0.84) | **mixed**: holds for tokens, fails for messages, and P_msg is mostly a clock |
| E8a | agent identity > 70% of var(ln V); lab > 30% | η²(agent) = 0.699; lab share 0.58 vs. permutation 0.24 (p = 0.005) | **holds** (agent share at the threshold) |
| E8b | ≥ 60% of agents saturate (last-third growth < 0.2 × first-third) | 19%, but because there is no growth phase: median ln V growth is 0.016 in the first third and 0.052 in the last | **refuted as posed**: V is stationary around an agent-specific set point |
| E8c | ρ(P_msg, turnover) > 0.1 | **−0.47**. Turnover also falls with own turns (−0.62) and with interval length (−0.57); it rises only with uncached tokens (+0.17) | **refuted** for messages; weak support for tokens |
| E8c | ρ(V_prev, lines removed) > 0.2; ΔV = βP − γV_prev with β, γ > 0 | ρ = 0.61. β = +138 chars per exposed message; γ = 0.87 per snapshot (relaxation ≈ 1.2 snapshots) | **holds**, but γ ≈ 1 means each consolidation resets V to a set point, and the set point moves little with inflow (~+0.5% per message) |
| E8d | NE14: ≥ 25% change for most agents in snapshot rate, V and turnover (fewer snapshots, larger V, more turnover) | 13 agents on both sides. Snapshots 15.9 → 5.1 per hour (all 13 down, all past the threshold). V 17.1k → 21.6k chars (85% up, but only 38% past the threshold). Turnover 0.23 → 0.38 (85% up, 69% past). Lines removed 0 → 9.5 median. The shifts already appear on 03-24/25, before NE16 | **holds** for rate and turnover; V has the right direction but is below the threshold |

**Reading.**
- *Idle dynamics changed character at the regime boundary.*
  - In regime I, escape is message-triggered: the hazard triples after a room message, and messages spike just before escape.
  - In regime III, the agent sets a timer, and the pause ends on schedule. The only outside influence is an @-mention, which raises the chance of acting rather than re-pausing at expiry (×1.5).
  - So the regime-III "trap" is self-scheduled sleep with a stochastic gate, not barrier crossing driven by kicks. The heavy tail comes from the chosen durations and re-pause chains.
  - For T5, Kramers escape fits regime I only. For T4 / HH52, directed messages act at a gate rather than as a field.
- *Memory size is a set point.* It is agent- and lab-specific, restored at each consolidation, and moves little with message inflow. NE14 raised it about 20% and doubled per-snapshot turnover.
- *Collective irreversibility (E7)* is present but small in this crude pass. It needs the held-out MaxEnt estimator before any claim.

**Caveats.**
- Kick labels are coincidences in time.
- The day-swap null keeps the daily schedule but not within-day bursts. Part of the regime-I hazard ratio may be shared burstiness; the pre-escape spike is the stronger evidence.
- E7 uses plug-in estimators: the raw 16-state ΔS_ij is biased negative (median −0.0047 observed, −0.0051 null), so only the null-subtracted excess means anything. There were 20 null draws, and no held-out days.
- Tokens exist only for Claude and Gemini agents (20% of regime-III snapshots).
- Snapshot semantics differ by regime: in regime I, memory snapshots come every ~49 s and are not consolidations.
- NE14 is a bundle of changes (consolidate tool, pause tool, perma-computer-use), and only 13 agents are present on both sides.

#### Observable tables (reusable; `data/processed/H09-swarm-thermodynamics/`)
Both cover **all days** and carry a `holdout` flag. Exploratory users must filter `holdout == False`. Built by `analysis/build_observables.py` in about 2 s.

- **`idle_runs.parquet`**: one row per idle spell (57k rows).
  - *Identity:* agent, pt_date, regime, goal_no, holdout, idle_kind (WAIT / PAUSE).
  - *Times:*
    - t_prev_action: the previous non-idle row, the right start for regime-I WAIT.
    - t_start: the first idle event.
    - t_last_idle.
    - t_end: the escape, or the window end if censored.
  - *Durations:*
    - censored.
    - dwell_s = t_end − t_start, the right measure for PAUSE.
    - gap_dwell_s = t_end − t_prev_action, the right measure for regime-I WAIT.
    - n_idle_events.
    - declared_first_s and declared_last_s (PAUSE).
    - timer_expired: escape ≥ last declared expiry − 30 s.
  - *Escape:*
    - escape_kind: the first non-idle row, e.g. `AGENT_TALK` or `turn:bash`.
    - **escape_cause** ∈ {censored, timer, mention, nudge, human, room_msg, none}. Assigned in priority order, from the kicks in the 60 s before escape. It is a **proximate, coincidence-based label, not causal**: base rates and nulls are in `explore_e6_idle_traps.json`.
  - *Kick counts during the spell:* n_msgs / n_agent_msgs / n_human_msgs / n_nudges / n_mentions_during.
  - *Kick flags in the 60 s before escape:* kick_msgs / mentions / nudges / human_msgs_60s.
  - *Rules:* `pause` tool turns are dropped (mirrors); at equal timestamps, non-idle rows come first.
- **`consolidation_inflow.parquet`**: one row per `memory_stats` snapshot (246k rows).
  - *Identity:* agent, t, pt_date, regime, goal_no, holdout.
  - *Interval:* t_prev, dt_s, same_day_prev.
  - *Memory (copied from `memory_stats`):* n_chars, n_lines, n_headers, lines_kept / added / removed, jaccard_prev.
  - *Size change:* d_chars and d_lines, relative to the previous snapshot.
  - *Inflow in (t_prev, t]:*
    - messages: n_exposed, n_exposed_agent / _human / _nudge / _mention;
    - turns: n_turns, n_turns_tok;
    - tokens: tok_acct, tok_uncached, tok_out, tok_context_last.
  - *Flag:* consolidate_event_120s (true for 83% of regime-III snapshots).
  - *Token accounting* is provider-aware (`tok_acct`):
    - 'exclusive' (Anthropic): uncached = tok_in + tok_cache_write, context = tok_in + tok_cache_read + tok_cache_write.
    - 'inclusive' (Gemini): uncached = tok_in − tok_cache_read, context = tok_in.
    - Null for providers without token data.
  - Use `same_day_prev` to drop intervals that span a night.

## Round 1b (improved data, 2026-10-04)

### Round-1b predictions for the new tests
*Written 2026-10-04 08:40 UTC, before any of these tests was run. The only things looked at first were structural counts: 27,895 regime-III non-holdout calls follow a timer pause; 7,723 of them are re-pauses. The round-1 and round-2 predictions (E1–E8) are unchanged and are re-scored on the corrected inputs.*
- **G1 (the timer gate on the context ledger; replication of E6c in regime III).** The unit is a regime-III model call that follows a timer pause (`call_windows.after_pause`). The outcome is whether the agent acts (any call kind other than pause or wait) or re-pauses. Covariates are the chat items that newly entered that call (`context_ledger_turns`: @-mentions of the agent, nudges naming it, human and agent messages).
  - (a) A new @-mention raises P(act at the gate): Mantel–Haenszel OR ≥ 1.5 over agent strata.
  - (b) New unaddressed agent messages do not (OR in [0.8, 1.25]).
  - (c) Nudges raise it (OR > 1).
  - (d) Pauses rarely end early (`wake_early` < 1% of post-pause calls).
- **N1 (NE43, native: the drive is withdrawn inside #51).** The bookends stop after 08-04 and the nudger after 08-20. Windows are day-matched: 07-27 → 08-04 vs 08-06 → 08-20 vs 08-21 → 09-04.
  - (a) For gates with no new chat item, P(act) changes by less than 20% (|log ratio| < 0.18) across each step. The timer gate is internal.
  - (b) After the nudger stops, the overall P(act) at gates falls by no more than the pre-step accounting bound: the share of gates with a nudge × (P(act | nudge) − P(act | none)), + 0.02.
- **N2 (#51 roster sweep, native: memory set point vs inflow).** Over #51's non-holdout weeks, N grows from 21 to 32 and ledger inflow per call grows with it.
  - (a) The within-agent elasticity of weekly median memory size V on weekly mean new chat items per call has |b| < 0.1. The set point does not track read inflow.
  - (b) Its elasticity on N has |b| < 0.2.
- **N3 (HH269, memory as a first-order homeostat; regime III, non-holdout).** The series is each agent's ln V over successive same-day consolidation snapshots.
  - (a) The AR(1) coefficient toward an agent mean lies in [0, 0.5] for ≥ 80% of agents with ≥ 100 snapshots.
  - (b) AR(1) beats a random walk out of sample (last 30% of each agent's series) for ≥ 80% of those agents.
  - (c) There is no overshoot: after forced resets (`reset_forced`, the 41-turn cap) φ ≥ 0, and it is not lower than after voluntary consolidations by more than 0.1. HH269 predicts overshoot; I predict none, from round 2's γ ≈ 0.87.

### What changed
- **E1, E5.** Now on `activity_bins_fixed`, plus a trimmed E1: each day is cut to its all-present window (DQ8 / H38).
- **E6.**
  - Spells come from the shared `outages.idle_spells()`, asserted identical to `idle_runs`.
  - @-mentions come from `chat_mentions_clean`. Only 2.4k of 86.7k regime-I exposure-mentions change (o1's), and every E6 number is identical to 3 decimals.
- **New gate test (G1).** A context-ledger version of the timer gate (`analysis/r1b_gate.py`): new items at the post-pause call, not coincidence in time.
- **E8.** Re-run on ledger reads, with reset types from `reset_forced` / `reset_consol` (`analysis/r1b_memory.py`).
- **Tokens.** Round 2 already used `actions` with cache fields, not the uncached-only `events_core.tokens_in`. Its context size matches H45's per-call prompt size P (Spearman 0.998, median ratio 1.00, n 19,127), so nothing changes.
- **Failures.** No H09 statistic read `actions.error`, so the stderr issue does not touch H09.
- **Not re-run.** E7 (plug-in pair EP on bins, a light pass) was not re-run, to save compute. Its activity input changed, so treat E7b as superseded until it is.
- **Switches and outputs.** `H09_DATA=r1b` was added to `explore_e1_e5.py` and `explore_e6_idle_traps.py`; outputs go to `data/processed/H09-swarm-thermodynamics/r1b/`. 90 estimate rows were written (`analysis/r1b_estimates.py`).

### Old vs new
| Statistic | Round 1/2 | Round 1b |
| --- | --- | --- |
| E1 variance ratio, regime III (median day) | 1.61; 59% of days > 1.5 | fixed bins **1.85**, 86%; **trimmed 1.22, 23%** |
| E1, regime I | 1.25; 22% | 1.35, 36%; trimmed 1.23, 19% |
| E5 restart half-time | 1 min (overnight and weekend alike) | 1 min; plateau 0.68 vs 0.74 |
| E6c regime III, HR of @-mention (coincidence, 60 s) | 1.52 [1.37, 1.65] | identical (clean mentions change nothing) |
| E6c regime I, any room message | 3.06 | identical |
| E8a elasticity ln V on inflow | 0.16 (exposure count) | **0.14 on ledger reads**; reads track interval length just as much (ρ 0.87 vs 0.84) |
| E8c ρ(inflow, turnover) | −0.47 | −0.56 |
| E8c γ (relaxation per snapshot) | 0.87 | 0.85 (0.83–1.21 across goal periods) |

### New tests
| Test | Result | Verdict |
| --- | --- | --- |
| G1a: new @-mention at the gate, OR ≥ 1.5 | MH OR **3.09 [1.95, 4.50]** (agent × goal strata 3.22); P(act) 0.85 vs 0.70 | pass |
| G1b: unaddressed agent messages, OR in [0.8, 1.25] vs no new item | **0.50 [0.23, 0.95]**: P(act) 0.65 vs 0.85 | **fail**: chatter keeps agents paused |
| G1a′ (post hoc): @-mention vs no new item | 1.20 [0.76, 1.87] | a mention restores the no-news rate; it does not raise it |
| G1c: nudges, OR > 1 | vs rest 4.54 [3.17, 7.72]; vs no new item 0.69 [0.41, 4.9] | pass vs rest; n.s. vs no news |
| G1d: early wakes < 1% | 0.20% | pass |
| N1a (NE43): P(act | no new item) is stable across both steps | bookends off: log ratio −0.011 [−0.08, 0.05]; nudger off: −0.047 [−0.12, 0.01] (13 and 16 matched agents) | **pass** |
| N1b (NE43): the P(act) drop after the nudger stops is within the nudge-accounting bound | drop 0.036 vs bound 0.013 | **fail**: mentions also fell (share 0.15 → 0.12) |
| N2a (#51): elasticity of V on reads per call, \|b\| < 0.1 | 0.019 [−0.02, 0.06] (246 agent-weeks, N 25–32; reads per call ∝ N^1.9) | pass |
| N2b: elasticity of V on N, \|b\| < 0.2 | **0.33 [0.03, 0.64]** | fail (confounded with tenure) |
| N3a (HH269): φ in [0, 0.5] for ≥ 80% of agents | median φ **−0.10** (IQR −0.32 to 0.37); 36% in range | fail |
| N3b: AR(1) beats a random walk out of sample for ≥ 80% | 79% (median MSE ratio 0.63) | fail (borderline) |
| N3c: no overshoot after forced resets | φ after forced **−0.22 [−0.23, −0.20]**; after voluntary −0.10 [−0.12, −0.09] | **fail: overshoot, as HH269 predicted** |

**Reading.**
1. **The timer gate.** In regime III the gate reads the context it is handed:
   - with nothing new, the agent acts 85% of the time;
   - unaddressed chatter lowers that to 65%: agents who see others talking go back to sleep;
   - an @-mention cancels that, but does not push above the no-news baseline.

   So round 2's "only @-mentions get through" becomes "chatter holds agents at the gate; a mention releases them". This is consistent with H08's read-out gating. The gate is internal: it does not move when the bookends or the nudger stop (N1a).
2. **E1.** The regime-III co-activation excess was underestimated on the buggy table (1.61 → 1.85) and is mostly day edges: trimmed, it falls to 1.22, the regime-I level. This agrees with H38, H50 and RE-A1.
3. **Memory.**
   - Memory size does not follow read inflow. Within agents the elasticity is 0.02 at #51's roster steps, and the snapshot-level 0.14 is mostly the clock.
   - It does grow with N in #51, but N rises with time, so tenure is a confound.
   - Its dynamics are mean-reverting, but with *negative* lag-1 correlation, strongest after forced erasures (φ −0.22): a sawtooth / overshoot around the set point. HH269 predicted this overshoot; my own N3c prediction was wrong.
   - The negative φ holds for intervals > 60 s and > 300 s (−0.08, −0.18), so it is not a pairing artifact of near-simultaneous snapshots.

### Verdict changes
- **E1:** "holds in regime III only" becomes "holds untrimmed; after the day-edge trim, no regime-III excess".
- **E6:** unchanged.
- **T5 (timer-gated idling):** refined. Chatter suppresses acting at the gate, a mention releases it, and the gate is unaffected by drive withdrawal.
- **T9:** "memory is a set point" becomes "a set point with overshoot (a first-order homeostat with negative lag-1 gain, larger after forced erasures)".
- **E7b:** superseded (not re-run).

### Scorecard (first scoring, round 1b; H09 had none)
| Axis | Score | Evidence |
| --- | --- | --- |
| A mapping | 1 | Ledger-defined gate and inflow, fixed bins; no invariance check across families. |
| B assumptions | 1 | Day-edge trim; within-agent strata; stationarity not tested. |
| C adequacy | 1 | The gate effect beats the agent-stratified reference; AR(1) beats a random walk in 79% of agents. |
| D unfitted predictions | 1 | N1a and N2a passed as predicted; G1b and N3c failed. |
| E interventional | 1 | NE43 (both steps) leaves the gate unchanged. |
| F identifiability | 0 | No synthetic recovery. |
| G ground truth | 1 | Scaffold structure recovered: timer expiry (0.2% early wakes), the 41-turn reset in the memory dynamics. |
| H comparative | 1 | Random walk vs AR(1); "only mentions matter" vs "chatter suppresses". |
| I transfer | 1 | The gate effect holds in #38, #41, #44 and #51 (OR 1.6–3.3). |

Ratings suggestion: completeness 40, faithfulness 1.5, usefulness 2.5. The operator rule: to wake a timer-paused agent, address it; room chatter alone keeps it asleep.

## Notes
- 2026-10-03: opened at Vivian's request ("a whole new hypothesis for the general thermodynamics framing"). Predictions for E1–E5 written before data. Holdout locked first.
- 2026-10-03: round-2 predictions (E6–E8) written before running them. Structural checks first found two things:
  - `actions.tok_in` follows two accounting conventions. For Anthropic it excludes cache reads (tok_in < tok_cache_read in most turns); for Gemini it includes them. OpenAI, DeepSeek, Kimi, GLM and Grok agents report no tokens.
  - Before 2026-06-11, a PAUSE without a duration defaulted to 12 h.
- 2026-10-03: round 2 done as a light pass, after a scope change to "observables first".
  - Built `idle_runs` and `consolidation_inflow` for reuse.
  - E7 was a plug-in pass only; held-out MaxEnt EP is deferred to H05's estimator.
  - Promotion candidates:
    - T5, reframed: timer-gated idling with directed kicks acting at the gate. Natural experiments: NE14 (non-holdout) and NE22/NE23 (holdout).
    - T9, reframed: memory size as an agent set point.

## Round 2 redirects (2026-10-04)
*From the round-1 reflection (`writeup/round1-reflection/round1-reflection.pdf`).*
- **Where round 1 went sideways:** Thermodynamic words were mapped onto scheduler mechanics (timers, consolidation). Energy was never defined in agent terms.
- **What the direction is really after:** Tokens are the energy, progress is the work, and context resets are the heat.
- **H09-R1.** Token thermodynamics: power = tokens per hour; efficiency = progress (work ledger) per token; loops waste tokens at zero efficiency.
- **H09-R2.** Consolidation is Landauer-like erasure: tokens spent consolidating vs information kept.
- **H09-R3.** The swarm is a driven-dissipative steady state whose throughput is limited by attention, not compute (E5).
