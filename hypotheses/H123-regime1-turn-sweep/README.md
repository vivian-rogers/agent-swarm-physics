# H123: Regime I's turn order is a sweep: equilibrium-looking statistics with nonzero entropy production

**Status:** exploratory round 1 **done (2026-10-04): refuted as posed. Regime I's turn order is not a sweep; it is self-clocked asynchronous, and the order alone makes no entropy production.** Approved by Vivian in the dashboard vetting panel 2026-10-04 from HH364. Card, observables, nulls and predictions written 2026-10-04 21:58–22:05 UTC, before any real-data statistic; the scheduler audit ran first (22:06 UTC), before any EP statistic; amendment A1 (after the synthetic, before real EP) dated below.
- **Audit (41 non-holdout regime-I units):** 41/41 self-clocked asynchronous; 0 sweep, 0 random sequential, 0 state-dependent. Calls overlap (κ_par median 0.997); order predictability η_ord median 0.04 (max 0.125; sweep needs ≥ 0.5); return gaps burstier than random (CV 1.39 vs 1.08 shuffled; a sweep gives 0); being named lifts the next call only ×1.13 (max 1.32).
- **EP:** a symmetric-J kinetic Ising driven by the real order makes no EP: σ_sweep − σ_rand median 2×10⁻⁵ nats per call (31 units). Measured cross-agent talk EP is at the floor in 29/31 units; the 2 exceptions (21a, 24) are asymmetric (lag 1 too), at the chance rate.
- **Snapshots:** model 01 fits regime-I snapshots as well as regime III (ρ₂ 0.87 vs 0.88, N = 4 subsets; descriptive).
- **Natives:** NE14 class unchanged (supported); NE09 coupling step unresolved (mixed); G27 chat-mode calls not a sweep (N3, HH failed). Scorecard A1 B2 C1 D1 E1 F2 G1 H2 I1. `confirm.py` frozen and guarded (#9, #14, #15, #22, #28, #29); dry-run only, **not run**.
**Fields:** stat mech (kinetic Ising, update rules), stochastic thermodynamics (entropy production), scheduling
**Literature:** [Aguilera, Ito & Kolchinsky 2026](../../literature/aguilera-2026-entropy-production-nonequilibrium-maxent.md) (max-ent EP bound Σ_g, Newton step, multipartite observables). Cited, not stored: Manousiouthakis & Deem, *J. Chem. Phys.* 110, 2753 (1999)† (sweeps keep Boltzmann without detailed balance); Suwa & Todo, *PRL* 105, 120603 (2010)†.
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Population N(t) (active variant); Regime; Action; Agent state (binary variant, below); Entropy production / irreversibility, as the AIK bound with held-out θ (`infra/shared/ep_newton.py`, corrected estimator). **New named variants proposed** (not edited into DEFINITIONS.md; defined under Model): *update step (call)*, *next-actor audit statistics*, *event-time talk spin*, *event-time mode spin*, *cross-agent EP at lag L σ_×(L)*, *sweep EP σ_sweep*.
**Question served:** **Q6** (thermodynamics: how much of the swarm's irreversibility is the scheduler's own?), with **Q2** second (scheduler as field vs coupling).
**From:** HH364 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/02-nonequilibrium-ising/` (update-rule table, multipartite form), `physics-models/15-stochastic-thermodynamics-selection/` (EP inference)
**Data inputs (shared tables only):** `call_windows` (one row per model call: agent, `t_call`, `t_log`, `kind`, `talk`, `ctx_mode`, `turn_id`), `chat_core` + `chat_mentions_clean` (who named whom, state-dependence test), `period_units`, `calendar`, `roster`, `activity_bins_fixed` (model-01 snapshot check only). No text. Every row passes `holdout_mask` and `~holdout`.

## Source HH (verbatim from the HH list, including refinements)
- **HH364 · Regime I's turn order is a sweep: equilibrium-looking statistics with nonzero entropy production.** Model 02's subtle case: a fixed-order sweep keeps the Boltzmann distribution but breaks detailed balance. If regime I's turn pointer (`villages.turn_id`) cycles in a fixed order, the snapshots look like equilibrium while the dynamics is not.
  - *Prediction:* the next-actor distribution in regime I is closer to round-robin than random (count first); model 01 fits snapshots as well as in regime III; and the EP bound is positive even with the antisymmetric J set to 0, matching the value the sweep alone predicts.
  - *Check:* scheduler audit of next actor given the current state; simulate a symmetric-J kinetic Ising with the real turn order and compare its EP with the measured bound.
  - *Kill:* turn order is random sequential, or the measured EP far exceeds the sweep prediction (then real asymmetric coupling is present, which is also informative).
  - *Impostors:* this measures the scheduler's own share of irreversibility.
  - *Models:* 02, 15 · *Builds on:* H14, H56, H76, HH45

## Data fact found while specifying (2026-10-04 ~21:50 UTC, structure only, no statistic)
- `villages.jsonl.gz` has **one row**, the export-time snapshot: `turn_id` is null and `active_agent_id` is one agent. **There is no logged history of the turn pointer.** The update order must be reconstructed from the call log (`call_windows`, ordered by `t_call`, ties by `turn_id`).
- Regime-I calls are of two context modes: chat-mode calls (scheduled, `ctx_mode = chat`) and computer-use calls (`ctx_mode = cu`, chained within a session). Sessions of different agents run at the same time on one day inspected (2025-05-27), so calls of different agents can overlap in time. A literal one-at-a-time pointer is therefore not guaranteed; the audit tests it.

## Standards (2026-10-04)
**Question served:** Q6, then Q2.

| Impostor | Relevant? | How it is handled | Status |
| --- | --- | --- | --- |
| Scheduler field | **it is the object** | The hypothesis measures the scheduler's own share of irreversibility: σ_sweep (symmetric J with the real order) minus σ under a rate-matched random order. Day edges are cut: each day's first and last 10% of calls are dropped in the EP fits (H76: edges carry the excess); sensitivity without the cut. | the object; edges removed |
| Exogenous field (kickoff, goal, operator) | yes | A common drive with agent-specific lags makes lagged cross-agent asymmetry (H90 A1). It enters the fitted J as apparent coupling. Removed in part: the first active day of each period is dropped as a sensitivity, and the comparison is real σ_× vs the same J simulated; a field-driven σ_× exceeds σ_sweep, so it counts against the sweep reading, not for it. | partly |
| Shared model priors | partly | Family style gives agents similar own arrows (single-agent EP), not a lagged cross-agent asymmetry. Cross-agent EP is reported beyond the single-agent bound (nested sets). | n/a for σ_×; partly for J |
| Contemporaneous convergence | partly | Equal-time co-movement gives no antisymmetric signal by construction. A lag-1 multipartite observable is the read-out channel; no read vs posted-but-unread placebo (the ledger's unread partition is empty in one-room regime I, Known issues). | partly |

**Inputs:** ledger `call_windows` (current), `chat_mentions_clean`; never the old `activity_bins` or `exposure`.
**Two layers:** replication on every non-holdout regime-I unit with ≥ 2 days (audit on all units); natives N1 (NE14, regime II → III), N2 (NE09, chat into the computer-use context), N3 (chat-mode sub-sequence in G27: the turn pointer's own domain).
**Confirm script:** `analysis/confirm.py`, frozen and guarded; not run.

## Question
Who acts next in regime I: a fixed sweep, a random pick, or the state of the village? And how much of regime I's cross-agent entropy production is made by that order alone, with symmetric couplings?

## Model
**From:** `physics-models/02-nonequilibrium-ising` (update-rule table; multipartite form), `physics-models/15-stochastic-thermodynamics-selection` (AIK bound).

**H123 variant: event-time asynchronous kinetic Ising driven by the logged order.**
- **Update step (call):** one `call_windows` row. Steps are ordered by `t_call` (ties by `turn_id`) within one day of one period unit. The actor of step t is a(t).
- **Spins** (±1, one per agent, held between its calls):
  - *event-time talk spin* s_i = +1 if agent i's latest call produced chat (`talk`), else −1 (primary);
  - *event-time mode spin* m_i = +1 if i's latest call is computer-use (`ctx_mode = cu`), −1 for chat mode (secondary).
- **Dynamics:** at step t only a = a(t) updates, by heat bath: P(s_a' = +1 | s) = 1/(1 + e^{−2(h_a + Σ_{j≠a} J_aj s_j)}). No self-coupling (J_aa = 0), so with symmetric J and a random order the chain obeys detailed balance with respect to the Boltzmann distribution (model 02 table, row 1).
- **Update rules compared** (model 02 table): random sequential (DB, σ = 0); fixed sweep (Boltzmann kept, DB broken, σ > 0 at second order in J); state-dependent order (neither). A fourth rule is named here because the call log suggests it: **self-clocked asynchronous** updates (each agent on its own call clock, sessions overlapping). Its event order is random-like when clocks are incommensurate and sweep-like when clocks are equal and phase-locked.
- **Signature of a sweep (unfitted, axis D).** Each single update obeys detailed balance on its own, and the sweep keeps the Boltzmann distribution, so one-step statistics are reversible: the lag-1 multipartite observables vanish under a sweep with symmetric J. The order shows only at lag ≥ 2. Asymmetric couplings show already at lag 1. So: **sweep ⇒ σ_×(1) ≈ 0 < σ_×(L ≥ 2); asymmetric J ⇒ σ_×(1) > 0.**

## Data scheme (`scheme/build.py`)
- **Inputs:** `call_windows` (non-holdout regime-I/II/III rows of the units below), `chat_core` (agent messages: t, agent) with `chat_mentions_clean` (named roster agents), `period_units`, `roster`.
- **Transform:**
  1. Per unit × day: calls sorted by (`t_call`, `turn_id`); roster agents only (Claude Code agent excluded); keep `agent`, `t_call`, `t_log`, `kind`, `talk`, `ctx_mode`.
  2. Day-present agents: agents with ≥ 5 calls that day.
  3. Event-time spins: forward-fill each agent's latest talk and mode values over the day's step sequence. Steps before every day-present agent has called once are dropped (no missing spins).
  4. Naming for the state-dependence test: for each step t, the set of agents named in the latest agent chat message posted before `t_call(t)` (within 10 min).
- **Output:** `data/processed/H123-regime1-turn-sweep/` with `steps/<unit>.parquet` (day, step, actor, talk, mode, t_call, named-set flags; int8/bool), `audit.parquet`, `ep.parquet`, `synthetic/`, `results/`, `_provenance.json`. Expected < 40 MB.
- **Regimes covered:** regime I (2025-04-02 → 2026-02-24, one room), plus regime II/III units for N1.

## Observables
**O1 · Scheduler audit (first; per unit, all calls and chat-mode calls separately).** p_i = agent i's share of steps.
- *Repeat rate* r = P(a(t+1) = a(t)); references: round robin 0; rate-matched random r₀ = Σp_i².
- *Return-gap regularity* CV_gap: for each agent, the number of other-agent steps between its consecutive steps; coefficient of variation pooled over agents. Round robin: 0 (gap N−1). Rate-matched random: ≈ √(1 − p_i) (geometric).
- *Order predictability* η_ord = 1 − H(a(t+1) | a(t)) / H(a(t+1)) (plug-in, compared with a within-day shuffle of actors, 50 reps). Round robin 1; random 0.
- *Modal-successor share* q_succ: fraction of transitions i → j going to i's most frequent successor j ≠ i. Round robin 1; random ≈ max_j p_j/(1 − p_i).
- *Concurrency* κ_par: fraction of steps whose `t_call` falls inside another agent's in-flight call [t_call, t_log]. One-at-a-time pointer: 0.
- *State dependence* L_name: P(a(t+1) = j | j named in the latest agent message) / P(a(t+1) = j), pooled over j (Mantel–Haenszel over agents), with a within-day shuffle of the naming sets as null.
- **Classification (pre-registered):** *sweep* if η_ord ≥ 0.5, CV_gap ≤ 0.5 and r ≤ 0.5 r₀. *Random sequential* if η_ord ≤ 0.1, CV_gap within ±20% of the rate-matched shuffle value, r within ±20% of r₀, and L_name CI inside [0.8, 1.25]. *State-dependent* if L_name ≥ 1.5 with CI above 1.2. *Self-clocked asynchronous* if κ_par ≥ 0.3 and neither sweep nor state-dependent. Otherwise *mixed*.

**O2 · Model-01 snapshot sufficiency (HH clause 2).** On 1-min activity and talk spins (`activity_bins_fixed`), size-matched N = 4 random agent subsets (20 per unit): ρ₂ = I₂/I_N (pairwise max-ent captures what share of the multi-information), regime I vs regime III units. Reported, not central (Roudi 2009: ρ₂ is trivially high at small N and low rates).

**O3 · EP bound (after O1).** Held-out Newton bound (`newton_subsets_heldout`, day folds, per-column ridge c = 1, blocks = observable families) on event-time steps:
- *single*: for each agent, over its own call subsequence, the antisymmetric 3-step patterns 1[−−+] − 1[+−−] and 1[−++] − 1[++−] (2 per agent);
- *cross at lag L*: g^L_ij(t) = s_i(t+L) s_j(t) − s_i(t) s_j(t+L) for pairs i < j (L ∈ {1, 2, 4});
- **σ_×(L) = Σ̂(single ∪ cross_L) − Σ̂(single)**, nats per step; per agent-hour = σ × steps per hour / N̄.
- Floor: per-agent block flips (each agent's spin path reversed in 30-step blocks with probability ½); 30 reps.

**O4 · Sweep prediction.** Fit J and h by exact logistic ML (each row a: s_a at a's calls on the others' current spins; L2 1e-3). Then simulate, on the real day-by-day actor sequence (same steps, same day folds):
- **σ_sweep(L):** symmetric J_s = (J + Jᵀ)/2 with the real order;
- **σ_rand(L):** J_s with the actor sequence shuffled within day (rate-matched random sequential; should be ≈ 0);
- **σ_full(L):** fitted J (asymmetric) with the real order.
Each from 20 simulated replicates, estimated with the **same estimator** as the real data (Known issues: compare only same-estimator values). Scheduler share **φ_sched = (σ_sweep − σ_rand) / σ_×(real)**, reported only where σ_×(real) beats the floor.

## Null / baseline
- **Audit:** within-day actor shuffle (keeps each agent's step count; destroys order) and a rate-matched Poisson-clock surrogate (each agent's calls re-drawn as a Poisson process at its own rate on the day's span).
- **EP:** per-agent block flips (floor); σ_rand (random order with the same J); the cross-day pairing null for σ_× (agent paths from different days paired; 20 reps) as a check.
- **Synthetic** (axis F, below).

## Synthetic validation plan (axis F; `analysis/synthetic.py`; before real EP)
Symmetric-J heat-bath kinetic Ising on (i) an exact round-robin order, (ii) a random sequential order, (iii) the real G27 actor sequence (order only, structure; no states), at G27's step counts and day folds, N = 10, J_s entries N(0, (J₀/√N)²) with J₀ ∈ {0, 0.5, 1, 2}, h_i matched to a 30% talk rate. Plus an asymmetric world (J antisymmetric part of the same size) on a random order.
- **Pass:** (a) random order: σ_×(L) above the floor's 95th percentile in ≤ 10% of replicates at every J₀; (b) round robin: σ_×(1) at the floor and σ_×(2) above it at J₀ ≥ 1 (the signature); (c) asymmetric world: σ_×(1) above the floor (power reported per J₀); (d) the J fit + simulate pipeline returns σ_sweep within ±30% of the true-J σ at J₀ = 1.
- If (b) fails at the real step counts, the sweep clause is unidentifiable at that size and its verdict is "inconclusive".

## Prediction
*Written 2026-10-04 ~22:00 UTC, before the audit and before any real-data EP number. Credences are mine; the HH predicts the opposite of P1 and P3.*

| # | Statistic | HH prediction (tested) | My expectation and credence | Kill / counts against |
| --- | --- | --- | --- | --- |
| P1 | O1 class, regime I units (all calls) | sweep: η_ord ≥ 0.5, CV_gap ≤ 0.5 ("closer to round robin than random") | **not a sweep** (credence 0.80): self-clocked asynchronous (κ_par ≥ 0.3, η_ord < 0.2) in ≥ 2/3 of units; sweep in none | HH killed if the class is random sequential in ≥ 2/3 of units; HH supported if sweep in ≥ 2/3 |
| P1b | O1 on chat-mode calls only (turn pointer's domain) | sweep | closer to round robin than all calls (η_ord higher, CV_gap lower) but not a sweep (0.6) | — |
| P1c | L_name | (not stated) | ≤ 1.25 in most units (0.6): being named does not pull the next call in event order | L_name ≥ 1.5 in ≥ 1/2 of units → state-dependent order |
| P2 | O2 ρ₂ (N = 4 subsets), regime I vs III | equal ("model 01 fits snapshots as well") | abs(Δ median ρ₂) ≤ 0.05 (0.6) | regime I ρ₂ lower by > 0.05 |
| P3 | σ_× (talk) vs σ_sweep | σ_× > 0 with σ_× ≈ σ_sweep (within ×2) | σ_sweep ≈ σ_rand ≈ 0 (< 10⁻⁴ nats/step) because regime-I couplings are weak (H67 g_lag ≈ 0.005) (0.75); σ_× at the floor in ≥ 2/3 of units (0.6) | **Kill (HH):** σ_× > 3 σ_sweep with CI excluding σ_sweep (asymmetric coupling or lagged field) |
| P4 | Sweep signature | σ_×(1) ≈ 0 < σ_×(2) | not seen on real data (follows from P1) | σ_×(1) > floor wherever σ_× > floor → not the sweep |

**Replication rule:** the card-level verdict on P1 is "supported" if ≥ 2/3 of eligible regime-I units are classified sweep, "failed" if ≥ 2/3 are random sequential or self-clocked (the named alternative), else "mixed".

## Audit result (2026-10-04 22:06 UTC; run before any EP statistic; `analysis/audit.py`)
All 41 non-holdout regime-I units classify as **self-clocked asynchronous**; none is a sweep, none random sequential, none state-dependent. Details in Results.

## Amendment A1 (2026-10-04 22:10 UTC; after the synthetic, before any real-data EP number)
- **Synthetic** (`analysis/synthetic.py`, N = 10 at G27's step counts, 20 worlds per cell): the sweep signature is real and identifiable: on an exact round robin σ_×(1) stays at the floor while σ_×(4) beats it in 95–100% of worlds at J₀ ≥ 0.5 (σ_×(2) in 35–85%). The asymmetric world beats the floor at every lag in 100%. **With the real G27 order a symmetric J makes no EP at any J₀ ≤ 2** (indistinguishable from the random order). The J fit plus simulation pipeline recovers σ_sweep within +25% (lag 2) and +7% (lag 4) of the true-J value (J error 0.09–0.10).
- **Change:** the 15-flip block-flip floor was too narrow (random-order false-positive rate 0.00–0.25 per cell). A real σ_×(L) now counts as above the floor only if it exceeds both the block-flip q95 (30 flips) and the q95 of σ_rand (20 simulations of the fitted symmetric J on a within-day shuffled order). Coded into `run.py` before its first real run (22:11 UTC).

## Native tests (each with its own prediction, written 2026-10-04 ~22:00 UTC)
- **N1 · NE14 (regime II → III; perma computer use, 2026-03-11 → 03-24).** Units #33, #35, #36a (regime II, non-holdout) vs #36b+, #37 (first regime-III units). The update loop changes (sessions → continuous computer use with a pause tool). *Prediction:* the class is self-clocked asynchronous on both sides (0.6); κ_par rises in regime III (more agents calling continuously) (0.6); σ_sweep ≈ 0 on both sides. *Against:* a sweep or state-dependent class on either side.
- **N2 · NE09 (2025-12-20, chat interleaved into computer-use context; G23 → G24, N = 10 both).** Computer-use calls can now read chat, so talk couplings for cu agents should rise. *Prediction:* the audit class is unchanged (0.8); the fitted |J_s| (RMS) rises by ≥ 20% (0.4); σ_sweep stays < 10⁻⁴ nats/step (0.7). *Against:* an audit class change at NE09 (the scheduler changed, not the coupling).
- **N3 · G27 chat-mode sub-sequence (the turn pointer's domain; regime I/II only).** If the export's `active_agent_id` pointer cycles chat-mode turns, the chat-mode-only actor sequence is a sweep even if the full sequence is not. *Prediction:* not a sweep (η_ord < 0.3) (0.6). *Supports the HH:* η_ord ≥ 0.5 and CV_gap ≤ 0.5 on chat-mode calls.

## Rivals
- **R0 random sequential** (detailed balance with symmetric J): σ_sweep = σ_rand = 0.
- **R1 fixed sweep** (the HH): Boltzmann snapshots, σ_× > 0 only at lag ≥ 2, σ_× ≈ σ_sweep.
- **R2 state-dependent order** (model 02 seed: the named agent acts next): L_name ≫ 1; snapshots not Boltzmann.
- **R3 self-clocked asynchronous** (named alternative): high concurrency, random-like event order, regular own gaps; σ_sweep ≈ σ_rand.
- **R4 asymmetric coupling or lagged field:** σ_×(1) > 0 and σ_× ≫ σ_sweep.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R0–R4 above.
**Locked holdout used for confirmation:** regime-I held-out goal periods #9, #14, #15, #22, #28, #29 (audit and EP, frozen in `analysis/confirm.py`).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Steps = `call_windows` rows ordered by (`t_call`, `turn_id`); spins = talk at the latest call, and cu vs chat mode. Regimes I, II, III audited with one rule. Family invariance not checked; the pointer history the HH names does not exist in the export. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 2 | The update-order audit is the main result: 41/41 units self-clocked asynchronous (concurrency, order predictability, return gaps, repeats, naming lift, each against a within-day shuffle). Lag structure tested at 1, 2, 4 calls; day edges cut, with sensitivity. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Held-out-by-day Newton bound; real σ× compared with the block-flip floor and with σ_rand (same estimator). At the floor in 29/31 units (talk) and 26/31 (mode): nothing to beat. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | The sweep signature (σ×(1) ≈ 0 < σ×(L ≥ 2)) is absent; the unfitted prediction "σ_sweep ≈ σ_rand" holds in every unit (median 2×10⁻⁵ nats/call). |
| E interventional | predicts the change across a natural experiment | 1 | NE14: the class is invariant across the regime II → III change, as predicted; κ_par rise not testable (ceiling). NE09: the coupling step is not resolved. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 | At G27's step counts: round robin gives σ×(4) above the floor in 95–100% of worlds (J₀ ≥ 0.5), lag 1 at the floor; asymmetric J detected in 100%; the real order gives nothing at J₀ ≤ 2; the fit + simulate pipeline recovers σ_sweep within +7 to +25%. Floor size fixed in A1 before real EP. |
| G ground truth | agrees with known structure | 1 | Agrees with the known scaffold: chained computer-use calls and scheduled chat-mode calls run per agent (H40 call clock; H63 chained calls). No logged pointer to check against. |
| H comparative | beats the named rivals | 2 | R1 sweep rejected (η_ord ≤ 0.125, CV_gap > shuffle); R0 random sequential rejected (η_ord, CV_gap, r/r₀ all outside the shuffle range); R2 state-dependent rejected (L_name ≤ 1.32 < 1.5); R3 self-clocked asynchronous supported; R4 only in 2/31 units, at the chance rate. |
| I transfer | holds in other same-mode periods, including the holdout | 1 | Same class in 41 regime-I units, 3 regime-II and 3 regime-III units. Holdout not run. |

**Scorecard plan:** A from the spin and step definitions and family invariance of the audit; B is the audit itself (update order) plus a lag-structure check; C from the held-out bound vs floor and σ_rand; D from the lag-1 vs lag-≥2 signature; E from N1/N2; F from the synthetic; G from known scheduler facts (H40 call clock, H63 chained calls); H from R0–R4; I from replication across regime-I units.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G02](goalperiod-subhypotheses/G02/README.md) | exploratory (replication) | failed | self-clocked 1/1; η_ord ≤ 0.015; L_name ≤ 1.11; σ× talk not estimated (< 2 usable days) |
| [G03](goalperiod-subhypotheses/G03/README.md) | exploratory (replication) | failed | self-clocked 1/1; η_ord ≤ 0.022; L_name ≤ 1.12; σ× talk at floor |
| [G04](goalperiod-subhypotheses/G04/README.md) | exploratory (replication) | failed | self-clocked 4/4; η_ord ≤ 0.068; L_name ≤ 1.23; σ× talk at floor |
| [G05](goalperiod-subhypotheses/G05/README.md) | exploratory (replication) | failed | self-clocked 1/1; η_ord ≤ 0.064; L_name ≤ 1.12; σ× talk at floor |
| [G06](goalperiod-subhypotheses/G06/README.md) | exploratory (replication) | failed | self-clocked 2/2; η_ord ≤ 0.082; L_name ≤ 1.16; σ× talk at floor |
| [G07](goalperiod-subhypotheses/G07/README.md) | exploratory (replication) | failed | self-clocked 1/1; η_ord ≤ 0.125; L_name ≤ 1.16; σ× talk at floor |
| [G08](goalperiod-subhypotheses/G08/README.md) | exploratory (replication) | failed | self-clocked 1/1; η_ord ≤ 0.060; L_name ≤ 1.03; σ× talk at floor |
| [G10](goalperiod-subhypotheses/G10/README.md) | exploratory (replication) | failed | self-clocked 2/2; η_ord ≤ 0.069; L_name ≤ 1.03; σ× talk at floor |
| [G11](goalperiod-subhypotheses/G11/README.md) | exploratory (replication) | failed | self-clocked 1/1; η_ord ≤ 0.036; L_name ≤ 1.24; σ× talk at floor |
| [G12](goalperiod-subhypotheses/G12/README.md) | exploratory (replication) | failed | self-clocked 2/2; η_ord ≤ 0.043; L_name ≤ 1.09; σ× talk at floor |
| [G13](goalperiod-subhypotheses/G13/README.md) | exploratory (replication) | failed | self-clocked 1/1; η_ord ≤ 0.043; L_name ≤ 1.16; σ× talk at floor |
| [G16](goalperiod-subhypotheses/G16/README.md) | exploratory (replication) | failed | self-clocked 1/1; η_ord ≤ 0.049; L_name ≤ 1.11; σ× talk at floor |
| [G17](goalperiod-subhypotheses/G17/README.md) | exploratory (replication) | failed | self-clocked 1/1; η_ord ≤ 0.028; L_name ≤ 1.26; σ× talk at floor |
| [G18](goalperiod-subhypotheses/G18/README.md) | exploratory (replication) | failed | self-clocked 3/3; η_ord ≤ 0.052; L_name ≤ 1.31; σ× talk at floor |
| [G19](goalperiod-subhypotheses/G19/README.md) | exploratory (replication) | failed | self-clocked 2/2; η_ord ≤ 0.052; L_name ≤ 1.32; σ× talk at floor |
| [G20](goalperiod-subhypotheses/G20/README.md) | exploratory (replication) | failed | self-clocked 4/4; η_ord ≤ 0.055; L_name ≤ 1.20; σ× talk at floor |
| [G21](goalperiod-subhypotheses/G21/README.md) | exploratory (replication) | failed | self-clocked 2/2; η_ord ≤ 0.045; L_name ≤ 1.19; σ× talk above floor in 21a |
| [G23](goalperiod-subhypotheses/G23/README.md) | exploratory (replication) | failed | self-clocked 1/1; η_ord ≤ 0.039; L_name ≤ 1.11; σ× talk at floor |
| [G24](goalperiod-subhypotheses/G24/README.md) | exploratory (replication) | failed | self-clocked 1/1; η_ord ≤ 0.041; L_name ≤ 1.03; σ× talk above floor in 24 |
| [G25](goalperiod-subhypotheses/G25/README.md) | exploratory (replication) | failed | self-clocked 1/1; η_ord ≤ 0.032; L_name ≤ 1.14; σ× talk at floor |
| [G26](goalperiod-subhypotheses/G26/README.md) | exploratory (replication) | failed | self-clocked 1/1; η_ord ≤ 0.019; L_name ≤ 1.19; σ× talk at floor |
| [G27](goalperiod-subhypotheses/G27/README.md) | exploratory (primary + N3) | failed (N3 failed) | self-clocked 1/1; η_ord ≤ 0.017; L_name ≤ 0.98; σ× talk at floor |
| [G30](goalperiod-subhypotheses/G30/README.md) | exploratory (replication) | failed | self-clocked 2/2; η_ord ≤ 0.033; L_name ≤ 1.13; σ× talk at floor |
| [G31](goalperiod-subhypotheses/G31/README.md) | exploratory (replication) | failed | self-clocked 4/4; η_ord ≤ 0.026; L_name ≤ 1.13; σ× talk at floor |
| [NE14](goalperiod-subhypotheses/NE14/README.md) | exploratory (native N1) | failed (HH); class invariance supported | 6/6 units self-clocked both sides; κ_par 1.00 both sides (ceiling); L_name 0.85–0.98 after; σ× at floor |
| [NE09](goalperiod-subhypotheses/NE09/README.md) | exploratory (native N2) | mixed | class unchanged; RMS J_s 0.064 → 0.085 (intervals overlap); G24 talk σ× above floor at all lags |

## Results
### Exploratory round 1 (2026-10-04; `scheme/build.py`, `analysis/audit.py`, `analysis/synthetic.py`, `analysis/run.py`, `analysis/snapshot.py`, `analysis/summarize.py`; data `data/processed/H123-regime1-turn-sweep/`)
Old → new: this is round 1 (no earlier numbers). Figures: `figures/audit.pdf`, `figures/ep_talk.pdf`, `figures/synthetic.pdf`.

**O1 · Scheduler audit (run first, 22:06 UTC).** 41 non-holdout regime-I units (24 goal periods), all calls.

| Statistic | Round robin (sweep) | Random sequential (shuffle) | Observed: median [range] over 41 units |
| --- | --- | --- | --- |
| Order predictability η_ord | 1 | 0.001 | 0.041 [0.015, 0.125] |
| Return-gap CV | 0 | 1.08 | 1.39 [0.91, 2.08] |
| Repeat ratio r/r₀ | 0 | 1 | 0.29 [0.03, 0.96] |
| Concurrency κ_par | 0 (one at a time) | — | 0.997 [0.67, 1.00] |
| Named-next lift L_name | 1 | 1 | 1.13 [0.98, 1.32]; CI above 1 in 32/41, ≥ 1.5 in 0/41 |
| Class (pre-registered rule) | — | — | self-clocked asynchronous 41/41 |

Reading: each agent calls on its own clock, and calls of different agents overlap almost always. The event order carries little memory (η_ord ≈ 0.04): fewer immediate repeats than random (an agent's own call takes time), burstier return gaps than random (streaks of own calls). Chat-mode calls alone (the turn pointer's domain): 36 mixed, 5 random sequential, 0 sweep (η_ord ≤ 0.095). The weak naming lift (×1.13) is a small state dependence; it vanishes after NE14.

**O2 · Model-01 snapshot sufficiency.** ρ₂ = I₂/I_N on N = 4 subsets of 1-min spins: regime I 0.871 (activity, 15 units) and 0.874 (talk, 19); regime III 0.876 (14) and 0.879 (4). |Δ| ≤ 0.006: P2 holds, descriptively (Roudi 2009: ρ₂ is high at N = 4 regardless).

**O3/O4 · EP (after the audit and the synthetic; A1 floor).** 31 regime-I units with ≥ 2 usable days, talk and mode spins, nats per call step.

| Quantity | Talk | Mode |
| --- | --- | --- |
| Units with σ×(1) / σ×(2) / σ×(4) above the floor | 2 / 2 / 2 of 31 | 3 / 5 / 5 of 31 |
| σ_sweep − σ_rand, median [range], lag 2 | 2×10⁻⁵ [−1.0, +1.6]×10⁻³ | 0.5×10⁻⁵ [−0.8, +1.1]×10⁻³ |
| σ_sweep − σ_rand, median [range], lag 4 | 2×10⁻⁵ [−1.9, +1.5]×10⁻³ | 4×10⁻⁵ [−1.4, +0.8]×10⁻³ |
| RMS symmetric coupling J_s (median) | 0.090 | 0.109 |
| Units above the floor | 21a, 24 (lag 1 also above) | 3, 16, 18b, 19a, 21a (lag 1 above in 3, 18b, 21a) |

Every above-floor unit shows positive σ× at lag 1 and σ× ≥ 5× |σ_sweep − σ_rand|: asymmetric coupling or a lagged field, not the sweep. With a per-test floor size of 0.10–0.25 (synthetic), 2–5 hits in 31 are at the chance rate. G27 (primary): all lags at the floor, robust to no edge cut and to dropping the first day.

**Predictions vs results.**

| # | Prediction | Result | Verdict |
| --- | --- | --- | --- |
| P1 (HH) | sweep in ≥ 2/3 of units | 0/41 sweep; 41/41 self-clocked (the named alternative) | **failed** (my P1 supported) |
| P1b | chat-mode calls closer to round robin than all calls, not a sweep | not a sweep (36 mixed, 5 random); not closer to round robin (η_ord median 0.03, CV_gap 1.0–1.9) | half: not a sweep supported; closer failed |
| P1c | L_name ≤ 1.25 in most units | 36/41 ≤ 1.25 (max 1.32, units 17–19b) | supported |
| P2 (HH) | model 01 fits snapshots as well as in regime III | ρ₂ 0.87 vs 0.88 | supported (descriptive) |
| P3 (HH) | σ× > 0 with σ× ≈ σ_sweep | σ_sweep ≈ σ_rand ≈ 0; σ× at the floor in 29/31 | **failed**; my P3 supported |
| P4 | sweep signature | absent | supported (as implied by P1) |

**Natives.** N1 NE14: class invariant across regime II → III (6/6 units), κ_par saturated at 1.00 on both sides, σ× at the floor; the naming lift drops below 1 after NE14 (descriptive). N2 NE09: scheduler unchanged; the J_s rise (+33%) is not resolved; G24 talk σ× clears the floor at every lag (one unit, at chance rate; round-2 lead). N3 G27 chat-mode calls: not a sweep.

**Impostors.** The scheduler field is the object here, and it makes no EP through the order. Lagged exogenous fields would appear as σ× > σ_sweep; they do not appear beyond chance. Convergence and shared priors give no antisymmetric lagged signal by construction.

**Claim that stands:** regime I's update order is self-clocked asynchronous, not a sweep (41/41 non-holdout units; η_ord median 0.04 vs ≥ 0.5 for a sweep), so the order alone makes no entropy production (σ_sweep − σ_rand median 2×10⁻⁵ nats per call; synthetic power 0.95–1.0 to see a real sweep at G27's size). Excluded: the 2/31 above-floor talk units (chance rate), the NE09 coupling step (unresolved), the snapshot clause (descriptive; trivially high at N = 4), the NE14 concurrency rise (ceiling).

## Confirmatory predictions (C-*): for the locked holdout, frozen 2026-10-04 after round 1, not run (`analysis/confirm.py`)
Targets: held-out regime-I periods #9, #14, #15, #22, #28, #29 (all their units for C1–C2; units with ≥ 2 days for C3–C4).
- **C1:** no unit is a sweep, and ≥ 2/3 are self-clocked asynchronous (η_ord < 0.2, κ_par ≥ 0.3).
- **C2:** L_name < 1.5 in every unit.
- **C3:** |σ_sweep − σ_rand| < 10⁻³ nats/call at lags 2 and 4 (talk) in every EP unit (3×10⁻³ for units with < 7,000 steps).
- **C4:** σ×(talk) above the A1 floor in ≤ 25% of EP units at every lag.
- Dry run on two stand-in units (relabelled) passed the pipeline. Ledger family `entropy_production` plus a new `scheduler_order` statistic; regime-I targets are planned by H81, H99, H101, H67 and H51 (disclose).

## Round 2 redirects
**What the direction is really after:** whether the scaffold's scheduling, rather than the agents, creates any of the swarm's irreversibility; round 1 says the order does not, so the open part is the small state-dependent wake-up and the one possible coupling step.
- **H123-R1. NE09 event study.** σ×(talk) and the read-in coupling of agents in session before and after 2025-12-20, with placebo boundaries at other regime-I week edges; G24 is the only lead.
- **H123-R2. Use the event clock without a sweep correction.** Large-N EP and coupling fits in regime I can treat the order as random sequential with agent-specific clocks.
- **H123-R3. Named-next lift.** Test whether the ×1.13 regime-I lift lives in chat-mode wake-ups, and why it falls below 1 after NE14 (H40's per-call clock).
- **H123-R4. Family invariance.** Repeat the audit by lab (axis A).

## Notes
- 2026-10-04 ~21:50 UTC: the villages table has no pointer history (above). The audit uses the call log.
- 2026-10-04: unit 2 (2 days) has too few warm steps after edge cuts on one day; it is in the audit, not in the EP fits. Single-day units (4b, 4d, 12b, 19b, 20b, 30a, 31b–d, 36a) are audit-only.
- 2026-10-04: the poisson-clock surrogate named under Null is equivalent in distribution to the within-day shuffle for order statistics (a superposition of independent Poisson clocks gives i.i.d. actor labels), so only the shuffle was run.
- Estimates: 744 rows in `per_period_estimates` (audit statistics, σ×(L), σ_sweep − σ_rand, RMS J_s, ρ₂).
