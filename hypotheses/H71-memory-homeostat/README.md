# H71: Memory is a first-order homeostat

**Status:** **round 1 done (2026-10-04; exploratory, non-holdout; 37 period units, 4 natives).** **Homeostat yes, first order no, overshoot no.** Post-compression memory size reverts toward an agent set point in every period (φ⁺ pooled 0.67 [0.63, 0.71] per compression cycle; CI excludes 1 in 37/37; AR(1) beats a random walk out of sample for 69% of 353 agent-periods). H09's "overshoot" is a sampling artifact: each regime-III consolidation writes an append snapshot then a compress snapshot, so the mixed series has φ < 0 in 10/10 periods while φ⁺ > 0; φ⁺ after forced erasures equals φ⁺ after voluntary ones (|F − V| < 0.15 in 9/10). The loop is not first order: AR(2) > 0 (median +0.19; |φ₂| < 0.1 in only 5/37) and ρ₂ > ρ₁² in 28/37. Post hoc, a fast near-deadbeat compression around a slowly drifting set point (ρ_s ≈ 0.82 per cycle, slow share ≈ 0.79) reproduces the mixed-series φ in 7/8 regime-III periods. The gain is an agent property (across-period r 0.52 vs null p95 0.33); the set point is mostly agent (η² 0.91) and lab (0.41). Natives: NE14 mixed (set point +17–31%, gain +0.12), NE04 failed (φ⁺ rose), NE16 supported (negative control), NE32 mixed (newcomers relax at the slow rate). `confirm.py` written, **not run**.
**Question (GOALS.md):** **Q4**, where does the swarm's information live, and what is it worth? H71 asks how the memory store is *maintained*: whether its size is held by a first-order control loop with a per-agent gain, so that memory is a regulated store whose capacity, not content, the scaffold and the agent set.
**Fields:** control theory and physics of life (homeostasis, relaxation to a set point), stochastic processes (AR / Ornstein–Uhlenbeck, Onsager regression), information theory (the store's size as a capacity)
**Literature:** [Kolchinsky & Wolpert 2018](../../literature/kolchinsky-2018-semantic-information-autonomous-agency.md) (maintained nonequilibrium states, viability); [Bartlett et al. 2025](../../literature/bartlett-2025-physics-of-life-information-roadmap.md) (homeostasis as regulated information import); [Sowinski et al. 2023](../../literature/sowinski-2023-semantic-information-resource-gathering-agents.md) (a store's size vs its value).
**Definitions used** (`physics-models/DEFINITIONS.md`): Regime; Memory state; Context segment (H45). New named variants defined below and proposed for DEFINITIONS.md: **memory snapshot phase (append / compress)**, **compression cycle**, **post-compression size x⁺**, **pre-compression peak y**, **per-cycle gain g = 1 − φ**.
**From:** HH269 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` ("Making the faithful ones better") · **Models:** `physics-models/04-semantic-information/`, `physics-models/05-replicator-dissipation/` (import vs degradation bookkeeping: lines added vs removed per cycle)
**Data inputs (shared tables first):** `memory_stats` (size, hashed-line diffs; no text), DQ1 context ledger (`context_ledger_turns`: `reset_forced`, `reset_consol`), `events_core` (CONSOLIDATE, START/STOP_USING_COMPUTER), `roster`, `calendar`, `period_units`. H09 round 1b and H45 numbers are quoted from their cards; no code is imported from them.

## Question
Do deviations of memory size from its set point relax at a fixed per-agent rate, with overshoot after consolidations and erasures and a gain change at NE41, so that a first-order control model beats a random walk?

**Starting point.** H09 round 1b (N3) fit AR(1) to each agent's regime-III snapshot series and found median φ = −0.10, φ = −0.22 after forced erasures, and AR(1) beating a random walk out of sample for 79% of agents. It read the negative φ as overshoot. **A structural fact checked before this card (counts only):** every regime-III consolidation writes two memory snapshots. The first, about 1–2 min before the CONSOLIDATE event, only *appends* lines (lines_removed = 0, size up; 38,670 non-holdout rows); the second, at the event, *compresses* (lines_removed > 0, size down; 36,106 rows). Regime I/II memory grows through several appends per session and is compressed at session ends (73k appends, 23k compressions in regime I). A series that mixes the two phases alternates peak, trough, peak, trough, so its lag-1 autocorrelation is negative even without overshoot. H71 separates the phases before fitting.

## Design: two layers (Vivian, 2026-10-04; see `infra/data-quality/QUEUE.md`)
- **Replication:** the common estimator on every eligible non-holdout goal period (35 periods with ≥ 4 agents and ≥ 15 compression cycles per agent for at least 3 agents). Period README role: `replication`.
- **Period-native tests:** NE14/NE41 (the regime II → III boundary inside #36 and across #33/#35 → #37/#38: the gain change HH269 names), NE04 (2025-09-05, chain-of-thought consolidation, #12a → #12b/#13), NE16 (2026-03-26, "never update memory" fix, #36b → #36c; negative control), and newcomer relaxation from empty memory (Onsager regression, every non-holdout join with ≥ 10 cycles). Period README role: `native`.
- **Faithfulness lever:** HH269 was written to raise **D** (the relaxation law as an unfitted prediction) and **E** (NE41). H71 adds an Onsager-regression test (D), a clock test (B) and a sampling-artifact check (A).

## Model
**From:** `physics-models/04-semantic-information/` (a store maintained against degradation) and `05-replicator-dissipation/` (import vs removal bookkeeping).

**Two-phase homeostat.** For agent i, compression cycle n (one consolidation in regime III; one compressed session in regimes I/II), with sizes in log characters:
- growth (import) phase: y_n = x_{n−1} + Δ_n, with Δ_n = d_i + c (x_{n−1} − μ_i) + ξ_n (c < 0: the agent appends less when memory is large);
- compression (degradation) phase: x_n = a_i + b y_n + ζ_n (b < 1: compression pulls toward a set point);
- combined: x_n − μ_i = φ (x_{n−1} − μ_i) + ε_n with **φ = b(1 + c)**; per-cycle gain g = 1 − φ; relaxation time τ = −1/ln φ cycles (φ > 0).

**Classes it separates:**
| | φ on x⁺ | AR(2) term | relaxation after a large displacement |
| --- | --- | --- | --- |
| first-order homeostat (HH269) | 0 < φ < 1 | ≈ 0 | geometric, φⁿ (the same φ as small fluctuations: Onsager regression) |
| random walk (rival) | ≈ 1 | ≈ 0 | none |
| deadbeat template (rival: memory rewritten to a target length every cycle) | ≈ 0 | ≈ 0 | one cycle |
| over-correcting controller (HH269's overshoot) | < 0 | ≈ 0 | alternating |
| second-order / delayed controller | any | ≠ 0 | damped oscillation |

**Clock.** If the controller acts at consolidations (event clock), φ does not depend on the wall-clock length of the cycle. If memory relaxes in continuous time, φ = exp(−k Δt) falls with Δt.

**Sampling artifact model.** On a series that interleaves append (peak) and compress (trough) snapshots, lag-1 autocorrelation is ≈ −(peak−trough variance share) even when φ on x⁺ is positive. The synthetic (axis F) reproduces H09's mixed-series φ from planted x⁺ dynamics.

## Data scheme (`scheme/`)
- **Script:** `scheme/build.py`.
- **Inputs:** `memory_stats` (t, agent, n_chars, n_lines, lines_kept/added/removed, jaccard_prev), `context_ledger_turns` (reset flags; consolidations), `events_core` (CONSOLIDATE event times), `calendar` (pt_date → goal_no, regime, holdout), `period_units`, `roster`.
- **Transform:**
  1. Non-holdout snapshots only (`holdout_mask` on PT date and goal; held-out counts never printed). The Claude Code agent has no memory rows.
  2. Phase: **compress** if lines_removed > 0, **append** if lines_removed = 0 and lines_added > 0, **same** otherwise (dropped).
  3. Cycle n of agent i: compress snapshot n; x⁺_n = ln n_chars at that snapshot; y_n = ln n_chars of the last snapshot before it (the pre-compression peak; = x⁺_{n−1} when no append came between); Δt_n = time since the previous compress snapshot; n_appends; lines added and removed.
  4. Cycle type (regime III): **forced** if a `reset_forced` call follows the compress snapshot within 10 min, **voluntary** if a `reset_consol & ~reset_forced` call does; regimes I/II: **session**.
  5. Period and unit from the calendar; the memory-relevant splits are NE04 (#12a | #12b), NE14/NE41 (#36a | #36b), NE16 (#36b | #36c). Roster joins are not splits for an agent's own memory dynamics (named exception to `period_units`; units are reported for traceability).
- **Output:** `data/processed/H71-memory-homeostat/cycles.parquet` (one row per compression cycle; codes and sizes only), `snapshots.parquet` (phase-labelled snapshot series), `_provenance.json`; results in `results/`.
- **Regimes covered:** I, II, III, non-holdout.

## Observables
- **O1 φ⁺** per period: within-agent AR(1) of x⁺ (agent-demeaned, pooled over agents in the period; Nickell-corrected by the synthetic), cluster bootstrap over agents (500). Per agent: φ⁺_i for agents with ≥ 15 cycles.
- **O2 model comparison:** one-step out-of-sample prediction of x⁺ on the last 30% of each agent's cycles in the period: random walk (x̂ = x_{n−1}), white noise around the training mean (deadbeat), AR(1), AR(2). Share of agents for which AR(1) beats RW (MSE ratio < 1) and beats the deadbeat.
- **O3 mixed-series φ** (all snapshots in time order, H09's statistic) next to φ⁺, and the synthetic sawtooth's prediction.
- **O4 decomposition:** b (compression map slope of x⁺_n on y_n) and c (growth slope of Δ_n on x⁺_{n−1}), within agent; check φ ≈ b(1 + c).
- **O5 overshoot after erasures:** φ⁺ for cycles ending in forced vs voluntary consolidations (regime III); the sign of x⁺_{n+1} − μ after the deepest compressions.
- **O6 clock:** φ⁺ within terciles of Δt_n (wall-clock cycle length); slope of φ on log Δt.
- **O7 agent heterogeneity and invariance:** random-effects τ of φ⁺_i within period; across-period correlation of φ⁺_i for agents in ≥ 2 periods (exception (b): agent-level property, invariance checked first).
- **O8 Onsager regression (native N4):** newcomers' x⁺ trajectories from their first cycle vs μ_i + φ⁺_iⁿ (x⁺_0 − μ_i) with φ⁺_i and μ_i fitted on their later cycles only.

## Null / baseline
- **Random walk** (φ = 1) and **deadbeat** (φ = 0) as model-comparison nulls (O2).
- **Within-agent shuffled x⁺** (φ ≈ −1/T, the finite-sample floor) and the **synthetic two-phase sawtooth** (planted b, c at real cycle counts and real append counts per cycle) for estimator bias, size and power: power to detect φ⁺ < 0 (overshoot) and to separate AR(1) from RW at each period's real counts.
- **DQ8:** no null-size entry covers AR(1) on per-agent snapshot series; sizes come from the synthetic (STANDARDS §3).

## Impostors (STANDARDS §1)
| Impostor | How it could fake a homeostat | How H71 removes it |
| --- | --- | --- |
| Scheduler field | The 41-call cap and session ends set when compressions happen; mixing scaffold-timed append and compress snapshots fakes overshoot | Phases separated (O3); forced vs voluntary cycles (O5); clock test (O6); day-edge cycles (first of day) reported separately |
| Exogenous field (goal, prompt) | A goal change or a memory-prompt change shifts every agent's set point at once, which looks like relaxation | Fits within goal periods with agent means μ_i per period; step changes split (NE04, NE14, NE16) |
| Shared model priors | Model families write memories of typical lengths; family set points look like control | Agent fixed effects; across-period invariance of φ⁺_i (O7); lab share of set-point variance reported |
| Contemporaneous convergence | Not applicable: the variable is one agent's own store; inflow from other agents was tested by H09 (N2, elasticity 0.02) | — |

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** random walk; deadbeat template; over-correcting controller; second-order controller; continuous-time relaxation (wall clock).
**Locked holdout used for confirmation:** none yet. Planned in `analysis/confirm.py` (frozen, guarded, **not run**): #43 ("Improve your memory", the one period whose goal acts on the store: a set-point and gain change), the regime-III held-out periods #45–#50 and the #51 tail (P1, P2, P5 replication).

Round 1 scores (2026-10-04; details in "Round 1 results"):

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 2 | phases from hashed-line diffs; the same estimator in all three regimes; the snapshot-phase artifact removed |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | event clock holds (29/37); the first-order Markov assumption fails (AR(2) > 0 in 25/37) |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | beats RW (37/37 CIs < 1; 69% one-step) and deadbeat (88%); AR(2) beats AR(1) for 61% |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | mixed-phase sign 10/10 and clock 29/37 as predicted; Onsager relaxation only for the slow mode (post hoc) |
| E interventional | predicts the change across a natural experiment | 1 | NE14 moves the set point; NE16 negative control holds; NE04 opposite to prediction |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 | unbiased φ⁺, overshoot power 1.0, RW and wall clock identified at real counts (6 skeletons) |
| G ground truth | agrees with known structure | 1 | the 41-call cap visible as cycle type; forced = voluntary as expected for a scaffold-timed cut |
| H comparative | beats the named rivals | 1 | RW, deadbeat, overshoot rejected; the single loop loses to the two-timescale model (post hoc) |
| I transfer | holds in other same-mode periods, including the holdout | 1 | same sign in 37/37 units and all regimes; holdout not run |

## Prediction
*Written 2026-10-04 19:25 UTC, before computing any φ, b, c or model comparison on real data. Seen before: the phase counts above, cycles per period (35 non-holdout periods, 62 to 26,713 compressions), the fraction of lines removed per compression (median 0.50–0.64 by regime), and H09's mixed-series numbers.*

| # | Prediction | Counts against |
| --- | --- | --- |
| P1 | **First-order relaxation on the compressed series.** φ⁺ ∈ (0, 0.9) with the CI excluding 0 and 1 in ≥ 2/3 of eligible periods; φ⁺ < 0 (overshoot) in ≤ 1/6. | φ⁺ ≥ 0.9 (random walk) or ≤ 0 in ≥ 1/3 of periods |
| P2 | **AR(1) beats both nulls out of sample:** MSE(AR1) < MSE(RW) for ≥ 70% of agents pooled and MSE(AR1) < MSE(deadbeat) for ≥ 60%. | AR(1) loses to RW for > 50% of agents |
| P3 | **H09's overshoot is the two-phase sampling.** The mixed series gives φ < 0 in ≥ 2/3 of regime-III periods while φ⁺ > 0 in the same periods, and the synthetic sawtooth with the fitted φ⁺ reproduces the mixed φ within ±0.15. | mixed φ ≥ 0, or the synthetic misses by > 0.15 in most periods |
| P4 | **No overshoot after erasures:** in regime III, φ⁺ after forced consolidations ≥ 0 and within 0.15 of φ⁺ after voluntary ones (HH269 predicted overshoot). | φ⁺(forced) < 0 with the CI below 0 |
| P5 | **First order is enough:** \|AR(2) coefficient\| < 0.1 in ≥ 2/3 of periods. | \|φ₂\| ≥ 0.1 with the CI excluding 0 in ≥ 1/3 |
| P6 | **Event clock:** the slope of φ⁺ on log Δt is within ±0.1 per e-fold (the controller acts at consolidations, not in wall time). | slope < −0.1 with the CI excluding 0 (continuous relaxation) |
| P7 | **Fixed per-agent rate:** agent φ⁺_i differ (random-effects τ > 0.1) and are stable across periods (correlation ≥ 0.3 for agents in ≥ 2 periods). | τ ≈ 0 (one swarm-wide gain) or across-period correlation < 0.1 |
| P8 | **Decomposition:** b ∈ (0, 1) (compression regulates) and c < 0 (growth regulates); φ⁺ within ±0.1 of b(1 + c). | b ≥ 1 (no compression regulation) |
| N1–N4 | see `goalperiod-subhypotheses/{NE14,NE04,NE16,NE32}/README.md` | |

**Verdict rule (per period, replication):** *supported* if φ⁺ ∈ (0, 0.9) with the CI excluding 0 and 1 and AR(1) beats RW for ≥ 60% of the period's agents; *failed* if φ⁺'s CI includes 1 or lies below 0, or AR(1) beats RW for < 40%; *mixed* otherwise; *descriptive* if fewer than 3 agents have ≥ 15 cycles.

## Results by goal period
Replication verdicts follow the card's rule (reversion: φ⁺ in (0, 0.9) with the CI excluding 0 and 1, and AR(1) beating RW for ≥ 60% of agents). The first-order clause (P5) is scored across periods below, not in the per-period verdict.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G03](goalperiod-subhypotheses/G03/README.md) | replication | supported | φ⁺ 0.73 [0.54, 0.88]; AR1>RW 0.67; AR(2) +0.19; ρ₂−ρ₁² +0.11 |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | supported | φ⁺ 0.82 [0.43, 0.87]; AR1>RW 0.60; AR(2) +0.22; ρ₂−ρ₁² +0.09 |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | supported | φ⁺ 0.64 [0.12, 0.76]; AR1>RW 0.67; AR(2) +0.28; ρ₂−ρ₁² +0.20 |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | mixed | φ⁺ 0.55 [0.47, 0.64]; AR1>RW 0.50; AR(2) +0.09; ρ₂−ρ₁² +0.07 |
| [G07](goalperiod-subhypotheses/G07/README.md) | replication | supported | φ⁺ 0.62 [0.47, 0.80]; AR1>RW 1.00; AR(2) +0.19; ρ₂−ρ₁² +0.18 |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | supported | φ⁺ 0.58 [0.15, 0.64]; AR1>RW 1.00; AR(2) +0.17; ρ₂−ρ₁² +0.13 |
| [G10](goalperiod-subhypotheses/G10/README.md) | replication | mixed | φ⁺ 0.30 [-0.14, 0.42]; AR1>RW 0.50; AR(2) +0.11; ρ₂−ρ₁² +0.10 |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | supported | φ⁺ 0.62 [0.50, 0.71]; AR1>RW 0.67; AR(2) +0.17; ρ₂−ρ₁² +0.10 |
| [G12a](goalperiod-subhypotheses/G12a/README.md) | replication | supported | φ⁺ 0.49 [0.29, 0.58]; AR1>RW 1.00; AR(2) -0.00; ρ₂−ρ₁² -0.00 |
| [G12b](goalperiod-subhypotheses/G12b/README.md) | replication | mixed | φ⁺ 0.37 [-0.07, 0.80]; AR1>RW 0.67; AR(2) -0.01; ρ₂−ρ₁² +0.06 |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | supported | φ⁺ 0.75 [0.51, 0.86]; AR1>RW 1.00; AR(2) +0.14; ρ₂−ρ₁² +0.07 |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | failed | φ⁺ 0.81 [0.68, 0.91]; AR1>RW 0.33; AR(2) +0.19; ρ₂−ρ₁² +0.09 |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | mixed | φ⁺ 0.76 [0.46, 0.95]; AR1>RW 0.50; AR(2) +0.33; ρ₂−ρ₁² +0.18 |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | supported | φ⁺ 0.57 [0.45, 0.69]; AR1>RW 1.00; AR(2) +0.24; ρ₂−ρ₁² +0.17 |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | supported | φ⁺ 0.49 [0.32, 0.67]; AR1>RW 1.00; AR(2) +0.23; ρ₂−ρ₁² +0.19 |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | supported | φ⁺ 0.58 [0.53, 0.62]; AR1>RW 0.80; AR(2) +0.24; ρ₂−ρ₁² +0.17 |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | supported | φ⁺ 0.49 [0.39, 0.59]; AR1>RW 0.89; AR(2) +0.22; ρ₂−ρ₁² +0.17 |
| [G23](goalperiod-subhypotheses/G23/README.md) | replication | supported | φ⁺ 0.53 [0.39, 0.66]; AR1>RW 0.70; AR(2) +0.17; ρ₂−ρ₁² +0.13 |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | supported | φ⁺ 0.51 [0.38, 0.64]; AR1>RW 0.70; AR(2) +0.13; ρ₂−ρ₁² +0.10 |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | mixed | φ⁺ 0.67 [0.48, 0.88]; AR1>RW 0.50; AR(2) +0.21; ρ₂−ρ₁² +0.14 |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | supported | φ⁺ 0.58 [0.24, 0.82]; AR1>RW 0.60; AR(2) +0.22; ρ₂−ρ₁² +0.16 |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | supported | φ⁺ 0.70 [0.54, 0.85]; AR1>RW 0.80; AR(2) +0.26; ρ₂−ρ₁² +0.15 |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | supported | φ⁺ 0.75 [0.47, 0.87]; AR1>RW 0.92; AR(2) +0.20; ρ₂−ρ₁² +0.11 |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | mixed | φ⁺ 0.80 [0.42, 0.88]; AR1>RW 0.54; AR(2) +0.22; ρ₂−ρ₁² +0.10 |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | mixed | φ⁺ 0.80 [0.44, 0.85]; AR1>RW 0.58; AR(2) +0.11; ρ₂−ρ₁² +0.04 |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | supported | φ⁺ 0.77 [0.51, 0.86]; AR1>RW 0.69; AR(2) +0.11; ρ₂−ρ₁² +0.05 |
| [G36a](goalperiod-subhypotheses/G36a/README.md) | replication | failed | φ⁺ 0.70 [0.46, 0.87]; AR1>RW 0.33; AR(2) +0.15; ρ₂−ρ₁² +0.09 |
| [G36b](goalperiod-subhypotheses/G36b/README.md) | replication | supported | φ⁺ 0.86 [0.47, 0.88]; AR1>RW 0.83; AR(2) -0.08; ρ₂−ρ₁² -0.01; mixed -0.03; F−V -0.08 |
| [G36c](goalperiod-subhypotheses/G36c/README.md) | replication | supported | φ⁺ 0.70 [0.45, 0.73]; AR1>RW 0.77; AR(2) +0.00; ρ₂−ρ₁² -0.00; mixed -0.26; F−V +0.03 |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | mixed | φ⁺ 0.76 [0.49, 0.96]; AR1>RW 0.55; AR(2) +0.20; ρ₂−ρ₁² +0.11; mixed -0.51; F−V -0.16 |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | mixed | φ⁺ 0.77 [0.70, 0.83]; AR1>RW 0.43; AR(2) +0.19; ρ₂−ρ₁² +0.09; mixed -0.57; F−V +0.02 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | supported | φ⁺ 0.73 [0.51, 0.88]; AR1>RW 0.60; AR(2) +0.10; ρ₂−ρ₁² +0.06; mixed -0.55; F−V +0.14 |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | supported | φ⁺ 0.72 [0.61, 0.82]; AR1>RW 0.73; AR(2) +0.15; ρ₂−ρ₁² +0.09; mixed -0.54; F−V -0.00 |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | supported | φ⁺ 0.74 [0.52, 0.91]; AR1>RW 0.67; AR(2) +0.16; ρ₂−ρ₁² +0.09; mixed -0.42; F−V -0.11 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | mixed | φ⁺ 0.81 [0.62, 0.97]; AR1>RW 0.50; AR(2) +0.20; ρ₂−ρ₁² +0.10; mixed -0.49; F−V +0.03 |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | supported | φ⁺ 0.73 [0.49, 0.92]; AR1>RW 0.80; AR(2) +0.12; ρ₂−ρ₁² +0.07; mixed -0.50; F−V -0.09 |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication | supported | φ⁺ 0.81 [0.75, 0.88]; AR1>RW 0.80; AR(2) +0.20; ρ₂−ρ₁² +0.07; mixed -0.12; F−V -0.02 |
| [NE14](goalperiod-subhypotheses/NE14/README.md) | native | mixed | set point +17% [7, 27] (wide), +31% within #36; Δφ⁺ +0.12 [0.05, 0.20] (wide), +0.03 within #36 |
| [NE04](goalperiod-subhypotheses/NE04/README.md) | native | failed | Δφ⁺ +0.15 [0.04, 0.34] (predicted fall); removal share 0.52 → 0.50 |
| [NE16](goalperiod-subhypotheses/NE16/README.md) | native | supported | negative control: Δφ⁺ −0.03 [−0.13, 0.08], Δ ln μ +0.10 [−0.01, 0.30] |
| [NE32](goalperiod-subhypotheses/NE32/README.md) | native | mixed | 28 newcomers: φ_relax within ±0.2 of φ_i for 0.68; halving within 3 cycles 0.32 |

## Round 1 results (2026-10-04, exploratory, non-holdout)
*Scripts: `scheme/build.py`; `analysis/{h71lib, synthetic, run, posthoc, period_folders, figures, estimates_rows, confirm}.py`. Numbers: `data/processed/H71-memory-homeostat/results/{periods, cross, natives, posthoc}.json`, `synthetic/synthetic.json`. Figures: `figures/summary_obs.pdf`, `figures/summary_synthetic.pdf`. 62,302 non-holdout compression cycles; 181,838 snapshots.*

### Synthetic validation (axis F, before real outcomes)
On the real cycle skeletons of G51, G38, G37, G30, G12a and G36b (real agents, times, appends per cycle, cycle types), with planted single-loop dynamics (noise 0.15 per phase, 20 replicates; 6–7 for G51):
- the half-panel-jackknife φ⁺ is unbiased (|bias| ≤ 0.02 for planted −0.3 … 1.0); the agent-bootstrap CI covers the planted value in 75–100%;
- an overshoot of −0.3 has its CI below 0 in 100% of replicates in every skeleton; a random walk's CI includes 1 in 85–100%;
- the clock slope is 0.00 ± 0.03 under an event clock and −0.20 to −0.26 under wall-clock relaxation (detected);
- the mixed-phase φ on regime-III skeletons is −0.51 (deadbeat), −0.39 (φ⁺ 0.3), −0.12 to −0.17 (φ⁺ 0.6): one append per cycle makes the mixed series negative without any overshoot. Regime-I skeletons (several appends per cycle) give positive mixed φ.

### Outcome vs prediction
| # | Prediction (locked 19:25 UTC) | Observed | Verdict |
| --- | --- | --- | --- |
| P1 | φ⁺ in (0, 0.9), CI excl. 0 and 1, ≥ 2/3 periods; overshoot ≤ 1/6 | 35/37 (the other two: CI touches 0 in small G10, G12b); overshoot 0/37; pooled 0.67 [0.63, 0.71] (I 0.61, II 0.76, III 0.77) | **supported** |
| P2 | AR(1) < RW MSE for ≥ 70% of agents; < deadbeat for ≥ 60% | 69% of 353 agent-periods (median MSE ratio 0.89); 88% beat the deadbeat | **narrowly failed** (RW clause), deadbeat clause met |
| P3 | mixed φ < 0 while φ⁺ > 0 in ≥ 2/3 regime-III periods; single-loop synthetic within ±0.15 | sign clause 10/10 (mixed −0.03 to −0.57); single-loop synthetic within 0.15 in 0/10 | **mixed** (artifact confirmed; single loop cannot reproduce its size) |
| P4 | φ⁺(forced) ≥ 0 and within 0.15 of voluntary | φ⁺ forced 0.49–0.79, CI > 0 in 10/10; \|F − V\| < 0.15 in 9/10, CI includes 0 in 10/10 | **supported** (no overshoot; HH269's overshoot refuted) |
| P5 | \|AR(2)\| < 0.1 in ≥ 2/3 | 5/37; median +0.19; CI > 0 and ≥ 0.1 in 25/37 | **failed** (not first order) |
| P6 | event clock, \|slope\| ≤ 0.1 | 29/37; slope < −0.1 with CI < 0 in 3/37 | **supported** |
| P7 | τ > 0.1 and across-period r ≥ 0.3 | τ median 0.16 (0–0.39); r 0.52 vs permutation null mean 0.22, p95 0.33 (24 agents in ≥ 2 periods) | **supported** |
| P8 | b ∈ (0, 1), c < 0, φ⁺ ≈ b(1 + c) ± 0.1 | b ∈ (0, 1) 34/37, c < 0 37/37; but b(1 + c) median 0.13 vs φ⁺ 0.67 (within 0.1 in 1/37) | **failed** (the one-step maps miss most of the persistence) |
| N1–N4 | natives | NE14 mixed, NE04 failed, NE16 supported, NE32 mixed | see table above |

### Post hoc (labelled; `analysis/posthoc.py`, written after P5 and P8 failed)
**Two-timescale homeostat.** x⁺_n = m_n + e_n: a slowly drifting set point m_n (AR(1), persistence ρ_s) plus fast compression noise e_n. It predicts ρ_k = r ρ_sᵏ, so ρ₂ > ρ₁².
- ρ₂ − ρ₁² > 0 with the CI above 0 in 28/37 periods; ρ_s median 0.82 per cycle; slow-variance share r median 0.79.
- With fitted r, ρ_s and growth, a two-timescale sawtooth reproduces the observed mixed-phase φ within 0.15 in 7/8 regime-III periods (single loop: 0/10).
- Out of sample, exponential smoothing (the drift-plus-noise predictor) beats AR(1) for 50% of agents (median): the two are tied as predictors.
- Newcomers (NE32) relax from their first compression with factor ≈ 0.9 per cycle, the slow mode, not the fast φ⁺.

**Reading.** Each compression nearly resets memory size to the agent's *current* target (one-step regression b ≈ 0.12 in regime I, 0.46 in regime III), and growth refills toward a ceiling (c ≈ −0.72 / −0.20). The persistence lives in the target, which drifts with ≈ 0.82 per-cycle persistence. In wall time: regime III cycles last a median 14.5 min, so φ⁺ 0.77 is a relaxation time of ≈ 3.8 cycles ≈ 55 min of active time; the slow target drifts on ≈ 5 cycles. Regime I: φ⁺ 0.61 per 6-min cycle, τ ≈ 2 cycles ≈ 12 min.

### Answer to the question
Memory size is regulated: deviations revert toward an agent-specific set point at an agent-specific rate, on the consolidation clock, with no overshoot after forced or voluntary consolidations. It is not a *first-order* homeostat: a fast near-deadbeat compression tracks a slowly drifting target, so the random walk loses mainly at long horizons and AR(1) wins only 69% of one-step forecasts. NE41/NE14 changes the set point (+17–31%), not the per-cycle gain. H09's "overshoot" was the two-phase sampling of the snapshot table.

### Scorecard (round 1)
| Axis | Score | Evidence |
| --- | --- | --- |
| A mapping | 2 | Phases from hashed-line diffs (97–99.7% of compress rows are size drops); the same estimator runs in all three regimes; the snapshot-phase artifact found and removed |
| B assumptions | 1 | Clock test passes (29/37 event clock); stationarity within periods assumed; the first-order (Markov-1) assumption fails (AR(2), ρ₂ > ρ₁²) |
| C adequacy | 1 | Beats RW (37/37 CIs < 1; 69% one-step) and deadbeat (88%), but AR(1) is not the best model (AR(2) beats AR(1) for 61%) |
| D unfitted predictions | 1 | Mixed-phase sign (10/10) and clock (29/37) predicted and held; Onsager regression holds only for the slow mode (post hoc) |
| E interventional | 1 | NE14 moves the set point, NE16 negative control holds; NE04 opposite to prediction |
| F identifiability | 2 | Unbiased φ⁺, power 1.0 for overshoot, RW identified, clock identified, at real counts in 6 skeletons |
| G ground truth | 1 | The 41-call cap appears as cycle type; forced vs voluntary agree as expected for a scaffold-timed cut |
| H comparative | 1 | RW, deadbeat and overshoot rejected; the single loop loses to the two-timescale model (post hoc) |
| I transfer | 1 | Same sign in 37/37 units and all three regimes; holdout not run |

**Scorecard: A2 B1 C1 D1 E1 F2 G1 H1 I1.** The faithfulness lever (D, E) rose to 1 each; D did not reach 2 because the pre-registered unfitted relaxation (single loop) failed.

## Confirmatory design (written 2026-10-04 after round 1; `analysis/confirm.py`, frozen, guarded, NOT RUN)
Targets: #43 ("Improve your memory"), the held-out regime-III periods #45–#50, the #51 tail. Frozen predictions: C1 φ⁺ ∈ (0, 0.95) with the CI < 1 in every target with ≥ 3 eligible agents [0.9]; C2 mixed-phase φ < 0 while φ⁺ > 0 in ≥ 2/3 of regime-III targets [0.85]; C3 \|φ⁺(forced) − φ⁺(voluntary)\| < 0.15 pooled, with φ⁺(forced) CI > 0 [0.8]; C4 ρ₂ − ρ₁² > 0 pooled over targets (CI > 0) [0.75]; C5 #43: the set point of agents present in #42/#44 and #43 rises (Δ ln μ > 0, paired CI > 0) [0.6]. Guards: refuses without `--confirm --i-understand-this-uses-the-locked-holdout`, refuses with uncommitted H71 files, calls `holdout_ledger.check()` per target; `--dry-run` on stand-ins (#41, #42, #44, #51 08-24 → 09-04).

## Round 2 redirects (2026-10-04)
- **H71-R1.** Fit the two-timescale model directly (state-space Kalman fit per agent) and test the set point's drift against task covariates: does the target follow the agent's active repo count or its role (DQ4, DQ6)?
- **H71-R2.** Set point vs viability: do agents whose memory is above its set point at a forced erasure recover output faster (H44 re-acquisition, H15 dip)? This links store size to value (Q4).
- **H71-R3.** Run `confirm.py` (#43 is the one goal that acts on the store) after disclosures.
- **H71-R4.** Content turnover: the hashed-line Jaccard per cycle as a second order parameter (what is kept, not how much).

## Notes
- 2026-10-04 19:25 UTC: card written before any outcome statistic. Holdout masked in every script with `holdout_mask`; held-out counts never printed.
- 2026-10-04 ~19:45 UTC: synthetic validation (axis F) run before real outcomes; noise fixed at 0.15 per phase, not fitted.
- 2026-10-04 ~20:30 UTC: real run. Two periods fail the verdict rule on the out-of-sample clause only (G16, G36a: AR(1) beats RW for 2 of 6 agents).
- 2026-10-04 ~21:00 UTC, **post hoc (labelled):** the two-timescale model was added after P5 and P8 failed; it is a description, not a tested prediction.
- Data findings for shared files (not edited; in the report): every regime-III consolidation writes two `memory_stats` rows (append ~1–2 min before the CONSOLIDATE event, compress at it); any AR fit on the raw series mixes phases (bears on H09 N3c and H15's set-point rule).
- Read-only inputs: shared tables only; H09/H45/H15 numbers quoted from their cards; no code imported from other hypothesis folders.
