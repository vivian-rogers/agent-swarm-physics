# H09: Agent swarms have an effective thermodynamics

**Status:** running: exploratory round 1 done (E1–E5); round 2 in progress. Opened 2026-10-03 at Vivian's request.
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

## Notes
- 2026-10-03: opened at Vivian's request ("a whole new hypothesis for the general thermodynamics framing"). Predictions for E1–E5 written before data. Holdout locked first.
- 2026-10-03: round-2 predictions (E6–E8) written before running them. Structural checks first found two things:
  - `actions.tok_in` follows two accounting conventions. For Anthropic it excludes cache reads (tok_in < tok_cache_read in most turns); for Gemini it includes them. OpenAI, DeepSeek, Kimi, GLM and Grok agents report no tokens.
  - Before 2026-06-11, a PAUSE without a duration defaulted to 12 h.
