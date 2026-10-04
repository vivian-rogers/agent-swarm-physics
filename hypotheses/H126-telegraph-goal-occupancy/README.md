# H126: Goal occupancy is a telegraph process: dwell times predict the occupancy

**Status:** exploratory round 1 **done (2026-10-04): failed by the pre-registered (Amendment A1) rule.** A goal kickoff does not act on k_on alone: it also lowers k_off.
- **Kickoffs:** in 15 of 17 testable kickoff transitions, Δln k_off has a 90% CI below 0; only 2/17 (#40, #41) show the HH's "k_on up, k_off unchanged".
- **#12 debates:** the debate schedule behaves the same way (Δln k_on +1.27 [+0.89, +2.04], Δln k_off −1.37 [−2.28, −0.35]).
- **Telegraph instrument:** recovers rates on the real skeleton (synthetic τ ratio 0.97–1.10). The decoy-threshold classifier has sensitivity q̂₁ ≈ 0.67 and false-positive rate q̂₀ ≈ 0.045 (median of 39 units).
- **Not identifiable (synthetic):** the dwell shape (power 5–10% against CV 2.8) and the occupancy prediction (passes under every world).
- **Descriptive:** occupancy from dwells is within 20% on held-out days in 28/39 units, and the P2 kill does not fire (5/39). The call clock beats the wall clock in 9/11 regime-III units. Per-agent private-goal rates in #51 persist across units (median Spearman 0.61).
- **Timing:** card written 22:16–22:22 UTC and Amendment A1 ~22:51 UTC, both before any real-data statistic (see the A1 disclosure). `analysis/confirm.py` is frozen and dry-run, **not run**.
**Question (GOALS.md):** **Q2** (field vs coupling: does an assigned goal act as a field on one rate of a two-state switch, k_on, and leave k_off alone?). Second: **Q5** (how long agents stay on an assigned goal, and what an operator's kickoff changes).
**Fields:** stat mech (kinetic two-state models), stochastic processes (telegraph / hidden Markov), info theory (misclassification)
**Literature:** none in `literature/` covers telegraph processes or hidden Markov models. Cited from memory (†, not in `literature/`): Rabiner, *Proc. IEEE* 77, 257 (1989)† (hidden Markov models, forward–backward); Colquhoun & Hawkes, *Proc. R. Soc. B* 211, 205 (1981)† (dwell-time distributions of aggregated Markov ion channels; hidden sub-states make dwell distributions sums of exponentials); Kampen, *Stochastic Processes in Physics and Chemistry* (1992)† (the random telegraph signal).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime; Driving / external field (goal text + kickoff); Agent state, variant categorical (q = 2); H105's **on-goal statement (decoy threshold)**, **goal spin σ_i,t (agent-window)** and **goal occupancy p_g(t)**, used exactly as defined there; Exposure (turn read-out) for the call clock. New named variants proposed for DEFINITIONS.md (not edited there; defined under Observables): **latent goal state s_i,c (call clock)**, **telegraph rates k_on, k_off (per call)**, **dwell time (latent, calls)**, **dwell-predicted occupancy p_dw**, **raw run (observed)**.
**From:** HH367 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/10-potts/` (q = 2 kinetic Potts = kinetic Ising on a goal spin; primary), `physics-models/02-nonequilibrium-ising/` (single-spin Glauber dynamics with a field; the rates' dependence on the field)

## Source HH (verbatim from the HH list, including refinements)
- **HH367 · Goal occupancy is a telegraph process: dwell times predict the occupancy.** H105 found on-goal occupancy p 0.23–0.44 with binomial variance. The simplest kinetic model is a two-state switch per agent with rates k_on (set by the goal field) and k_off: p = k_on/(k_on + k_off).
  - *Prediction:* on- and off-goal dwell times (in calls) are each roughly exponential, and p predicted from the two mean dwells matches the measured occupancy within 20% in each assigned week. A kickoff raises k_on, not k_off.
  - *Check:* per-statement on/off-goal labels (H105's decoy threshold; calibrate first, as H105 asked); dwell distributions per agent and week.
  - *Kill:* dwell distributions far from exponential (strongly heavy-tailed), or predicted p off by more than 30%.
  - *Impostors:* misclassified statements shorten dwells; run the synthetic misclassification correction from H105 first.
  - *Models:* 10, 02 · *Builds on:* H105, H10

## Standards (2026-10-04)
**Question served:** Q2 (second: Q5).

| Impostor | Relevant? | How it is handled | Status |
| --- | --- | --- | --- |
| Scheduler field | yes | Time is the agent's own ledger call count, so idle nights and pauses do not count as dwell. Statements are observed only at talk or intent calls; the hidden-Markov likelihood conditions on the real observation times (gaps in calls), so sampling density does not bias the rates. A wall-clock fit is the rival clock (P5). | removed (call clock; observation times conditioned on) |
| Exogenous field (kickoff, goal, operator) | yes: the goal is the object | The claim is a field claim: the goal sets k_on. Within-week drives (debate rounds in #12, deadlines, operator messages) make the rates time-dependent and are the main rival to stationary telegraph dynamics: held-out-day prediction (P2) fails under a drift; native G12 models the DQ6 debate schedule as a time-dependent field. | addressed by design (P2, N1) |
| Shared model priors (family, style) | partly | Agent fields enter as agent-specific rates (k_on,i, k_off,i), so a family's prior for the goal topic is an agent field, not a dwell-shape effect. Style-residual statement vectors are a variant. Self-repeated statements (restatements) would fake long dwells: copies are dropped (`statement_flags.self_repeat_both`) in the primary input. | partly (agent rates; dedupe; style variant) |
| Contemporaneous convergence | no (no coupling claim) | The model is a single-agent switch; no influence between agents is claimed. Collective switching (H105's g₂ in #12a) violates independence; it shows up as a failed held-out-day prediction or a time-dependent rate, not as a coupling estimate. | n/a |

**Inputs:** DQ5 statements (`embeddings/statements.parquet`, `statements_white32_{bge_small,gte_modernbert}.npy`, `statements_style_resid_period32_*` as a variant), `statement_flags` (dedupe), shared `goal_fields` vectors (`embeddings/goals.parquet`, `goal_vectors*`, regime whiteners via `embed_models`), `period_units`, `period_affordances` (mode), DQ1 `call_windows` (the call clock), DQ6 `ground_truth_labels` (#12 debate phases). No activity table, no text.

**Two layers:** replication on every eligible assigned unit and every eligible kickoff transition (role `replication`); natives **G12** (scheduled field), **G51** (private fields, own-goal directions), **NE38** (one-agent field step) (role `native`).

**Unit-of-analysis exceptions (named):** (c) **the transition is the object** in the kickoff designs (P3) and NE38: each compares the two sides of one boundary with the same instrument. (a) **shared instrument**: the decoy-threshold on-goal classifier and the regime whiteners are a common ruler. Every rate is fitted within one period unit; periods are compared only through their fitted rates (P4).

## Question
Does an agent's on-goal / off-goal state switch like a random telegraph signal, with memoryless (exponential) dwells on the agent's own call clock? If so, do the two dwell means predict how much of the time agents spend on goal, and does an assigned goal (its kickoff) raise the on-switching rate k_on while leaving the off-switching rate k_off unchanged?

**Practical payoff:** if goal occupancy is telegraph, two numbers per agent (mean on-dwell and off-dwell, in calls) forecast occupancy, and an operator lever can be classed by which rate it moves: a kickoff that raises k_on recruits agents faster but does not keep them on goal longer.

## Model
**From:** `physics-models/10-potts/` (kinetic Potts with q = 2 on a goal spin) with `physics-models/02-nonequilibrium-ising/` (single-spin kinetics in a field).

**H126 variant: telegraph goal spin on the call clock, read through a noisy statement channel (a two-state hidden Markov model).**
- Latent state s_i,c ∈ {off, on} for agent i at its ledger call c (the agent's own call count; `call_windows`).
- Per-call switching: P(off → on) = a_i (k_on), P(on → off) = b_i (k_off). Stationary occupancy p_i = a_i / (a_i + b_i). Relaxation factor λ_i = 1 − a_i − b_i per call. Over a gap of Δ calls, P^Δ = Π_i + λ_i^Δ (I − Π_i) (closed form; Δ = 0 for two statements in one call).
- Mean latent dwells (geometric, in calls): τ_on,i = 1/b_i, τ_off,i = 1/a_i. **Dwell-predicted occupancy** p_dw,i = τ_on,i / (τ_on,i + τ_off,i) = a_i / (a_i + b_i).
- Emission (the instrument): each statement k at call c_k is labelled on-goal (b_k = 1) by H105's decoy-threshold rule with P(b = 1 | on) = q₁ (sensitivity) and P(b = 1 | off) = q₀ (false-positive rate; ≈ 0.05 by the decoy construction if off-goal statements look like decoys). q₀ and q₁ are shared by the unit's agents.
- **Field reading (HH367):** in kinetic Ising with a field h on the on-state, a_i ∝ e^{h} and b_i ∝ e^{−h} under symmetric Glauber rates; the HH's stronger form is that the goal enters only k_on (the "attempt" rate), so a kickoff multiplies a_i and leaves b_i. That is a **one-rate field**, the hypothesis tested in P3, N1 and N3.
- **Misclassification correction:** the HMM's likelihood includes the emission layer, so (a_i, b_i) are latent rates, not raw run rates. Raw on/off runs in the label sequence are shortened by misclassification (HH367's impostor); the synthetic (axis F) measures how much and whether the HMM recovers the latent rates.

**Rivals.**
- **R-HT heavy-tailed dwells (aging / stickiness):** each macro-state contains a fast and a slow hidden sub-state (a 4-state aggregated Markov chain, Colquhoun–Hawkes): dwells are mixtures of two geometrics with coefficient of variation CV > 1. Strongly heavy-tailed = CV ≥ 2.
- **R-het agent heterogeneity:** each agent is exponential, but rates differ across agents; pooled dwells look heavy-tailed. Agent-specific rates (M2a) absorb it.
- **R-drift nonstationary field:** rates change within the week (debate rounds, deadlines, a ramp). Fitted stationary rates then fail to predict held-out days (P2).
- **R-sym symmetric field (Glauber):** the goal field moves both rates (a up, b down) in proportion; a kickoff changes ln a and ln b by equal and opposite amounts.
- **R-off off-rate field:** the goal keeps agents on (lowers k_off) rather than recruiting them (raises k_on).
- **R-wall wall clock:** switching runs on wall time, not on the call clock (rival to the call clock of H40; P5).

## Data scheme (`scheme/`)
`scheme/build.py` builds `data/processed/H126-telegraph-goal-occupancy/` from shared tables only. No text is read.
- **Inputs:** listed above.
- **Transform:**
  1. Statements pass `common.holdout_mask` (PT date and goal); the Claude Code agent (19) is dropped; #23 is dropped (H10's confirmatory pair, as H105); statements with null `win30` are dropped.
  2. **Dedupe (primary):** drop statements with `statement_flags.self_repeat_both` (copies). Variant: keep all.
  3. **Goal direction:** ĝ = unit(unit(W·goal) + unit(W·kickoff)) in each model's regime basis (H105's construction, re-implemented, not imported). **Decoy threshold θ** = 95th percentile of ⟨z, ĝ⟩ over 10,000 random non-holdout same-regime statements outside goals {g − 1, g, g + 1} and #23 (seed 20261004). b_k = 1[⟨z_k, ĝ⟩ > θ]. Model **bge_small primary** (as H105); gte_modernbert and the style-residual vectors are variants.
  4. **Call clock:** for each statement, c_k = the number of the agent's ledger calls (`call_windows`, all kinds) with t_call < t_k; Δ_k = c_k − c_{k−1} within (agent, unit). Wall-clock gaps (minutes) are kept for P5.
  5. **Units:** every non-holdout `period_units` unit whose period is assigned (`period_affordances.mode` ≠ F), excluding #23 and #51 (natives only); eligible agents have ≥ 30 statements in the unit; eligible units have ≥ 3 eligible agents.
  6. **Kickoff designs (P3):** every non-holdout period g with non-holdout g − 1 in the same regime and a kickoff vector (H105's design list rule): segment F = the last ≤ 5 active days of g − 1, segment A = the first unit of g (all its days). Both segments are labelled along ĝ_g with g's threshold. Agents need ≥ 20 statements in each segment.
  7. **Natives:** G12 (#12a and #12b with the DQ6 debate windows `pre`/`deb` as "debate on"); G51 (units 51a–51l, each agent along its own `agent_goal` direction with its own decoy threshold); NE38 (agent 40, Opus 5, along its 07-29 goal direction, 07-24 → 08-04, split at 2026-07-29 16:51 UTC).
- **Output:** `stmts.parquet` (row, agent, unit, design, seg, t, c, Δ, gap_min, win30, b_bge, b_gte, b_style, dedupe flag; codes only), `thresholds.parquet`, `units.parquet`, `_provenance.json`; results under `results/`, `synthetic/`, `natives/`.
- **Regimes covered:** I, II, III (no unit or design crosses a regime boundary).

## Observables
*Specified 2026-10-04 22:16–22:22 UTC, before any on-goal label was computed.*
- **Raw run (observed):** a maximal run of equal labels b in an agent's statement sequence within a unit. Raw on- and off-run lengths in calls (call index of the first statement of the next run minus that of the run's first statement); edge runs are censored and reported separately.
- **Fits per unit (maximum likelihood, call clock):**
  - **M2a** (primary): per-agent (a_i, b_i), shared (q₀, q₁), q₁ > q₀; initial state at stationarity.
  - **M2s:** shared (a, b) and (q₀, q₁).
  - **M4s** (R-HT): on = {on-fast, on-slow}, off = {off-fast, off-slow}; entries into a macro-state go to its fast sub-state with probability w; exits at rates (b_f, b_s) and (a_f, a_s); shared emissions. Dwell CV per macro-state from the hyperexponential mixture.
  - **M2a-wall** (R-wall): the same as M2a with continuous-time rates per minute and gaps in wall minutes.
- **Held-out log-likelihood:** two-fold day split within the unit (odd vs even active days, by PT date); fit on one fold, score the other; ΔLL per statement.
- **Dwell-predicted occupancy p_dw** = mean_i a_i/(a_i + b_i) weighted by each agent's statement count; **measured occupancy p_win** = H105's agent-window occupancy (σ_i,t = 1 if ≥ half of the agent's ≥ 2 statements in the 30-min window are on-goal; p_win = mean σ over eligible agent-windows).
- **Predicted window occupancy p_win^pred:** from M2a fitted on one fold, simulate the latent chain and the emissions on the other fold's real statement times (200 simulations), apply the same majority rule, and average. **Occupancy ratio** ρ_p = ln(p_win^obs / p_win^pred), averaged over the two folds.
- **Kickoff rates (P3):** M2s with segment-specific (a_F, b_F, a_A, b_A) and shared emissions: Δln k_on = ln a_A − ln a_F, Δln k_off = ln b_A − ln b_F. CIs by an agent-cluster bootstrap (200 draws, refit).
- **Phase-diagram rates (P4):** per unit, the M2s rates (ln a, ln b) and logit p_dw.
- **Clock comparison (P5):** held-out ΔLL (call − wall) per statement.
- **Emissions (descriptive):** q̂₀, q̂₁ per unit (the calibration H105 asked for, from the dynamics themselves).
- **CIs:** agent-cluster bootstrap within units (200 draws) for rates and ρ_p; parametric bootstrap (fitted M2a simulated on the real skeleton, 50 draws) for the shape test.

## Null / baseline
- **N0 parametric bootstrap under the telegraph truth:** M2a fitted to the unit, simulated on the unit's real statement call times with the fitted emissions; the same pipeline gives the null distribution of ΔLL_held(M4s − M2a) and of raw run-length statistics. This sizes the shape test (P1) at the unit's own counts.
- **N1 synthetic worlds (axis F), run first:** telegraph (exponential) with misclassification; heavy-tailed dwells (CV 3); agent heterogeneity only; within-week drift; kickoff on k_on only vs on k_off only; wall-clock vs call-clock switching. All on the real skeleton of 6 units and 3 kickoff designs.
- **N2 label-shuffle within agent-unit:** destroys all persistence (λ = 0); the HMM must find λ ≈ 0 (no spurious dwell).
- **Known confounds:** the on-goal label is a text-embedding proxy; free-week segments are not field-free; statement counts per call differ by regime (regime I has several statements per call 4–36% of the time, regime III never).

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R-HT heavy-tailed (4-state aggregated Markov), R-het agent heterogeneity, R-drift nonstationary field, R-sym symmetric Glauber field, R-off off-rate field, R-wall wall clock.
**Locked holdout used for confirmation:** none yet. Planned: held-out assigned periods #1, #14, #15, #28, #29, #32, #34, #43, #45–#50 (units and kickoff transitions; `analysis/confirm.py`, frozen, not run).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Latent goal state from H105's decoy-threshold labels on the ledger call clock; emissions estimated (q̂₀ 0.045, q̂₁ 0.67); bge primary, gte/style/no-dedupe variants shift the shape statistic (CV ≥ 2 in 11 → 18 / 6 / 12 units) |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Call clock beats wall clock in regime III (9/11); stationarity checked by held-out days (28/39 within 20%); Markov order not identifiable (shape test power ≤ 0.1) |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Held-out-day occupancy consistent (P2 kill 5/39), but P2 passes under every synthetic rival |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | The HH's signatures (exponential dwells, p from dwells) are not identifiable; the one-rate kickoff prediction failed (2/17) |
| E interventional | predicts the change across a natural experiment | 1 | 17 kickoffs and the #12 debate schedule: k_off falls with the field (15/17); NE38 point estimates agree (Δln k_off −5.1, CI reaches +0.2) |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 | Synthetic on the real skeletons before data: rates recovered; P1 and P2 shown non-identifiable; P3 and P5 discriminating (A1) |
| G ground truth | agrees with known structure | 1 | DQ6 debate windows raise the on-rate (N1); #51 private goals give persistent per-agent rates |
| H comparative | beats the named rivals | 1 | R-off / R-sym beat the one-rate field on kickoffs; R-wall loses in regime III; R-HT vs exponential undecidable |
| I transfer | holds in other same-mode periods, including the holdout | 1 | k_off falls in regimes I and III kickoffs alike; holdout not run |

## Prediction
*Written 2026-10-04 22:16–22:22 UTC, before running the analysis on real data.*

**What I had seen when writing this:** H105's card in full (occupancy 0.23–0.44 in assigned weeks, decoy floor 0.02–0.05 in free weeks; g₂ 0.10 → 0.74 in #12a, half of it the debate schedule under gte; #51 own-goal occupancy ≈ 0.27 steady; NE38 Opus 5 0.00 → 0.96; agent-window spins unidentifiable from 2–4 statements), H10's and H64's status lines. **Structural counts only for H126:** statements per unit (355–19,456), the share of consecutive statements in the same call (regime I/II 2–36%, regime III ≈ 0), and median call gaps between statements (1–4 calls in regimes I/II, 5–17 in regime III). No on-goal label, run, dwell or occupancy statistic was computed for H126.

**Primary predictions** (replication layer; per unit, then counted across units, never pooled):

| ID | Prediction | Counts against (kill in bold) | Credence |
| --- | --- | --- | --- |
| **P1** exponential dwells | Per unit: ΔLL_held(M4s − M2a) per statement ≤ the 95th percentile of its N0 parametric-bootstrap distribution, **or** M4s's fitted dwell CV < 2 in both macro-states. Supported if this holds in ≥ 2/3 of eligible units | **heavy-tailed (ΔLL above the N0 95th percentile and CV ≥ 2 in either state) in > ½ of units** | 0.45 |
| **P2** dwells predict occupancy | Per unit: \|ρ_p\| ≤ ln 1.2 (held-out-day prediction within 20%). Supported if in ≥ 2/3 of eligible units | **\|ρ_p\| > ln 1.3 in > ½ of units** | 0.5 |
| **P3** kickoff raises k_on, not k_off | Per kickoff design: Δln k_on 90% CI above 0 and Δln k_off 90% CI containing 0. Supported if in ≥ 2/3 of testable designs (testable = both segments with ≥ 3 eligible agents and finite CIs) | Δln k_off CI excluding 0 with \|Δln k_off\| ≥ Δln k_on in ≥ ½ of testable designs (R-off / R-sym) | 0.25 |

**Secondary:**

| ID | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| P4 | Across assigned units, occupancy differences are carried by k_on: Spearman(ln a, logit p_dw) ≥ 0.5 and \|Spearman(ln b, logit p_dw)\| < 0.3 (M2s rates) | ln b carries as much as ln a | 0.35 |
| P5 | The call clock beats the wall clock on held-out days (ΔLL > 0) in ≥ 2/3 of regime-III units; regime I: no prediction (H40's η ≈ 0.5) | wall wins in ≥ ½ of regime-III units | 0.5 |
| P6 | Misclassification is large: the median raw on-run (calls) is < ½ of the fitted latent τ_on in ≥ 2/3 of units, and q̂₀ lies in [0.02, 0.10] | raw runs ≈ latent dwells | 0.6 |
| P7 | The literal renewal identity holds for raw labels: raw-run p (mean raw on-run / (on + off), calls) within 20% of the raw on-goal statement fraction in ≥ 2/3 units (descriptive; an identity up to censoring and call weighting) | — | — |

**Native predictions** (each repeated in its folder README):

| ID | Unit | Prediction | Counts against | Credence |
| --- | --- | --- | --- | --- |
| N1 | G12 (#12a, #12b) | The debate schedule is a one-rate field: with M2s rates split by DQ6 debate windows (pre/deb = on; elsewhere = off), Δln k_on (debate − outside) has a 90% CI above 0 and Δln k_off a CI containing 0 | Δln k_off CI below 0 with \|Δln k_off\| ≥ Δln k_on | 0.3 |
| N2 | G51 (51a–51l, own-goal directions) | Private fields give stationary telegraph dynamics: P1's exponential rule holds in ≥ 2/3 of the 12 units, and per-agent ln k_on is stable across consecutive units (median Spearman across agents ≥ 0.3) | heavy-tailed in > ½ of units, or median Spearman ≤ 0 | 0.35 |
| N3 | NE38 (Opus 5, 07-24 → 08-04) | A one-agent field step raises k_on and leaves k_off: Δln k_on 90% CI above 0, Δln k_off CI containing 0 | Δln k_off CI below 0 (the field holds the agent on goal) | 0.2 |

**Overall verdict rule.** **Supported:** P1 and P2 supported and P3 not failed. **Failed:** either kill fires (P1 heavy-tailed in > ½ of units, or P2 off by > 30% in > ½ of units). **Mixed:** otherwise (including P3 failed with P1 and P2 supported). The synthetic may demote a prediction to descriptive before real data (dated amendment).

**Per-unit replication verdict (G folders):** supported if P1 and P2 both hold in the unit; failed if the unit is heavy-tailed or \|ρ_p\| > ln 1.3; mixed otherwise.


### Amendment A1 (2026-10-04 ~22:51 UTC; after the synthetic, before any real-data statistic)
Synthetic: `analysis/synthetic.py` → `data/processed/H126-telegraph-goal-occupancy/synthetic/` (`units.parquet`, `segments.parquet`, `summary.json`). Six real unit skeletons (U12a, U17, U25, U35, U38a, U41) × 4 worlds × 10 replicates, each fitted twice (emissions free / two-stage); four segment skeletons (K12, K17, K38, N12_12a) plus NE38 × 4 worlds × 10 replicates. Emissions q₀ 0.05, q₁ 0.6 throughout. The real labels were never loaded (the synthetic reads skeleton columns only).

| Finding | Number | Consequence |
| --- | --- | --- |
| Telegraph rates are recovered | W1: median fitted τ_on / true 0.97–1.10, p_dw / true 0.90–0.98; q̂₁ 0.59–0.63, q̂₀ 0.05–0.06 | M2a is a usable instrument (axis F) |
| **P1 has no power** | heavy-tailed truth (W2, dwell CV ≈ 2.8): flagged heavy in 5–10% of replicates (size under W1: 0%); fitted CV median 1.0–1.09. The two-state fit absorbs the tails as ×7–9 longer dwells | **P1 demoted to descriptive.** The shape kill cannot be evaluated: "exponential" findings are uninformative |
| **P2 does not discriminate** | within 20% in 78–95% (W1), 85–100% (W4 drift), 90–100% (W2 heavy) | **P2 demoted to a consistency check.** Its kill (off by > 30% in > ½ of units) is kept: it almost never fires in any world, so a firing would be informative |
| P6 is false under the truth | raw median on-run / latent τ_on 0.84–0.95 in W1 (calls include the gaps) | P6 demoted to descriptive |
| P5 discriminates clocks | call clock wins 85–95% under a call-clock truth, 10–25% under a wall-clock truth | P5 stays (secondary) |
| P3 discriminates | K designs: k_on-only world → "k_on" 80%; k_off-only → "k_off" 90–100%; no change → false "k_on" 0–10%; symmetric world → "k_off" 40–80%, "k_on" 10–20% | **P3 becomes the primary test** |
| N1 (G12 debate split) discriminates | k_on world 80%, k_off world 90% | N1 unchanged |
| N3 (NE38) is weak | k_on world → "k_on" 30%; k_off world → "k_off" 70% | N3 kept; its "supported" is low-power, a "failed" is informative |

**Pre-data changes:**
1. **Emission fit:** the card's M2a (per-agent rates, shared emissions fitted jointly; `qmode = free`) stays primary. It recovered rates as well as or better than the two-stage variant (W4 regime III τ ratio 1.08 vs 1.74). An earlier single-replicate worry (q̂₁ 0.95 in one U38a draw) did not hold on average. The two-stage fit is not used.
2. **P1** is implemented with a *profile* M4 (per-agent M2 rates × shared scales, plus a shared hyperexponential shape and free emissions). It nests M2a and is fairer than a fully shared M4, which would lose on agent heterogeneity alone. P1 is now descriptive.
3. **P3 is restricted to assigned destinations** (mode ≠ F). Kickoffs into free weeks (K03, K05, K07, K11, K31) are not run.
4. P2 and P6 are descriptive (P2's kill is kept). P4, P5 and P7 are unchanged.
5. **Overall verdict rule (replaces the original):**
   - **Mixed ("the goal field acts on k_on; dwell shape not identifiable")** if P3 is supported (k_on in ≥ 2/3 of testable designs) and the P2 kill does not fire.
   - **Failed** if P3 fails (k_off carries the change, or symmetric, in ≥ ½ of testable designs) or the P2 kill fires.
   - **Inconclusive** otherwise.
   - "Supported" is no longer reachable in round 1, because the shape clause is not identifiable at village sampling.
6. **Per-unit replication verdict** (G folders): descriptive. The P2 kill is reported per unit.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | failed | ρ_p -0.06, -0.06; τ_on/τ_off 52/216, 69/123; kickoff Δln k_on -1.48 [-2.17, -0.40], Δln k_off -1.56 [-2.15, -0.38] |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | failed | ρ_p -0.07, -0.12; τ_on/τ_off 98/64, 276/112; kickoff Δln k_on -0.40 [-1.41, +2.44], Δln k_off -3.56 [-3.88, -1.99] |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | failed | ρ_p -0.07; τ_on/τ_off 97/439; kickoff Δln k_on +1.67 [+1.18, +10.77], Δln k_off -1.45 [-5.24, -1.19] |
| [G10](goalperiod-subhypotheses/G10/README.md) | replication | descriptive | ρ_p +0.01, +0.03; τ_on/τ_off 23/11, 23/5 |
| [G12](goalperiod-subhypotheses/G12/README.md) | native + replication | failed | ρ_p +0.21; τ_on/τ_off 77/52; kickoff Δln k_on +2.39 [+1.55, +3.46], Δln k_off -2.25 [-4.37, -1.64]; N1 debate Δln k_on +1.27, Δln k_off -1.37 [-2.28, -0.35] |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | failed | ρ_p +0.11; τ_on/τ_off 109/170; kickoff Δln k_on +0.19 [-0.91, +10.18], Δln k_off -3.33 [-4.94, -0.47] |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | failed | ρ_p -0.19; τ_on/τ_off 147/84; kickoff Δln k_on +1.93 [+0.68, +9.76], Δln k_off -0.60 [-4.79, -0.08] |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | failed | ρ_p -0.22, -0.49, -0.27; τ_on/τ_off 113/106, 50/167, 42/265; kickoff Δln k_on +2.46 [+0.98, +4.13], Δln k_off -0.85 [-2.58, -0.02] |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | failed | ρ_p +0.10; τ_on/τ_off 96/267; kickoff Δln k_on +3.49 [+2.28, +13.13], Δln k_off -0.44 [-4.51, -0.31] |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | failed | ρ_p -0.19, -0.10, +0.18; τ_on/τ_off 327/333, 51/249, 17/131; kickoff Δln k_on -0.78 [-2.41, +0.47], Δln k_off -2.55 [-4.23, -1.62] |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | failed | ρ_p -0.14, +0.18; τ_on/τ_off 141/127, 121/476; kickoff Δln k_on +0.89 [+0.37, +1.47], Δln k_off -0.81 [-1.45, -0.29] |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | descriptive | ρ_p -0.19; τ_on/τ_off 43/235 |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | failed | ρ_p -0.13; τ_on/τ_off 135/96; kickoff Δln k_on +2.88 [+0.90, +10.95], Δln k_off -4.97 [-5.45, -1.22] |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | failed | ρ_p -0.47; τ_on/τ_off 79/273; kickoff Δln k_on +1.77 [+0.70, +12.16], Δln k_off -3.87 [-4.74, -3.55] |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | failed | ρ_p -0.00; τ_on/τ_off 132/69; kickoff Δln k_on +13.37 [+9.78, +16.85], Δln k_off -3.53 [-6.12, -2.77] |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | descriptive | ρ_p +0.00; τ_on/τ_off 124/110 |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | descriptive | ρ_p +0.24; τ_on/τ_off 73/232 |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | descriptive | ρ_p -0.10; τ_on/τ_off 19/58 |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | descriptive | ρ_p +0.02, +0.00; τ_on/τ_off 4/20, 6/11 |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | failed | ρ_p -0.06, -0.12, +1.83, -0.15; τ_on/τ_off 78/393, 3/1678, 6/272, 3/38; kickoff Δln k_on +0.75 [-3.98, +6.90], Δln k_off -1.74 [-7.60, -0.81] |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | descriptive | ρ_p -0.17; τ_on/τ_off 111/452 |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | supported | ρ_p -0.02; τ_on/τ_off 218/130; kickoff Δln k_on +1.44 [+0.66, +2.35], Δln k_off -0.15 [-0.97, +0.58] |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | failed | ρ_p -0.32; τ_on/τ_off 114/269; kickoff Δln k_on +1.03 [+0.07, +2.63], Δln k_off +0.33 [-0.73, +1.85] |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | failed | ρ_p -0.01, -0.01; τ_on/τ_off 248/37, 244/2; kickoff Δln k_on +4.03 [+2.08, +9.43], Δln k_off -2.96 [-6.01, -1.52] |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | descriptive | ρ_p -0.17, -0.01; τ_on/τ_off 7/124, 8/73 |
| [G51](goalperiod-subhypotheses/G51/README.md) | native | supported | own-goal k_on persistence median ρ 0.61 (8 unit pairs); heavy by P1 rule 6/9 (descriptive) |
| [NE38](goalperiod-subhypotheses/NE38/README.md) | native | supported | Opus 5 raw on-goal 0.06 → 0.89; Δln k_on +3.18 [+1.09, +13.05], Δln k_off -5.05 [-12.91, +0.19] (low power) |

## Results
*Round 1, 2026-10-04 (UTC). Code: `scheme/build.py`; `analysis/{h126lib,synthetic,synth_summary,run,period_folders,write_rows,figures,confirm}.py` (numba via `uv run --with numba`). Data: `data/processed/H126-telegraph-goal-occupancy/` (`stmts.parquet`, `synthetic/`, `results/{units,kick,natives}.json`; 3.5 MB). Figure: `figures/h126_obs.pdf`. Estimates: 293 rows in `per_period_estimates` (39 replication units; natives #12a and the #51 units). Kickoffs and NE38 are transitions, so they get no rows.*

**Headline.** Read through a noisy two-state telegraph model on each agent's call clock, an assigned goal raises the on-goal switching rate and also lowers the off-goal rate. The goal holds agents on goal as well as recruiting them. HH367's "a kickoff raises k_on, not k_off" fails in 15 of 17 kickoffs. Its other two clauses (exponential dwells; occupancy from dwells within 20%) cannot be tested at village sampling, because the synthetic shows the shape test is blind and the occupancy check passes under every rival.

### Outcome vs prediction
| Prediction | Credence | Observed | Verdict |
| --- | --- | --- | --- |
| P1 exponential dwells (descriptive after A1) | 0.45 | "heavy" in 6/39 units (synthetic size 0%, power 5–10%); CV ≥ 2 in 11/39 (gte 18, style 6) | not identifiable; 6 heavy calls are more than chance |
| P2 occupancy from dwells within 20% (descriptive; kill kept) | 0.5 | within 20% in 28/39; off by > 30% in 5/39 | kill not fired; non-discriminating |
| **P3 kickoff raises k_on, not k_off** | 0.25 | k_on-only 2/17; Δln k_off CI below 0 in 15/17 (k_off-dominant 7, both rates 8); 1 design failed numerically (K39) | **failed** |
| P4 occupancy carried by k_on | 0.35 | Spearman(ln k_on, logit p) +0.37; Spearman(ln k_off, logit p) −0.50 (39 units) | failed |
| P5 call clock beats wall clock (regime III) | 0.5 | 9/11 regime-III units (regimes I/II: 14/28) | supported |
| P6 raw runs < ½ latent dwell (descriptive) | 0.6 | 27/39; q̂₀ in [0.02, 0.10] in 20/39 | descriptive |
| P7 raw renewal identity (descriptive) | — | within 20% in 15/39 | descriptive |
| N1 G12 debates: one-rate field | 0.3 | Δln k_on +1.27 [+0.89, +2.04]; Δln k_off −1.37 [−2.28, −0.35] | **failed** |
| N2 G51 private goals: stable per-agent rates | 0.35 | ln k_on persistence median ρ 0.61 (8/8 unit pairs ≥ 0.26); ln k_off 0.58; P1 "heavy" in 6/9 units | supported (persistence); shape descriptive |
| N3 NE38 one-agent step raises k_on only | 0.2 | raw on-goal 0.06 → 0.89; Δln k_on +3.18 [+1.09, +13.1]; Δln k_off −5.05 [−12.9, +0.19] | supported by the rule (CI touches 0); point estimate says k_off fell |
| **Overall (A1 rule)** | | P3 fails toward k_off / both rates | **failed** |

### What the data say
1. **The goal field acts on both rates.** Across 17 kickoffs, k_on rises by a median ×5.3 and k_off falls by a median ×5.7, both per call. In Glauber terms this is a symmetric field (rates ∝ e^{±h}), not an attempt-rate field. The same holds for the #12 debate schedule and, by point estimate, for Opus 5's reassignment.
2. **Dwell times are long on the call clock.** Median latent on-dwell is 78 calls and off-dwell 127 calls (39 units). Regime-III units with sparse statements (36b, 38b–e, 44a/b) give unstable short on-dwells (3–8 calls) with q̂₀ ≈ 0.
3. **The decoy classifier is now calibrated from the dynamics.** Sensitivity is q̂₁ ≈ 0.67 and false-positive rate q̂₀ ≈ 0.045. Latent occupancy is ×1.4 H105's agent-window occupancy (median).
4. **Private goals in #51 give agent-level constants:** each agent's k_on and k_off rank-persist across units (ρ ≈ 0.6). Most #51 units look heavier-tailed than exponential (6/9), although the test has little power. This is a post hoc lead.

### Caveats
1. In the kickoffs' F segment (the previous goal's tail), occupancy along the next goal sits at the decoy floor (median p_F 0.04), so the F-segment k_off rests on few latent on-dwells. The synthetic showed no false "k_off" calls under a true k_on-only change (0/30), which bounds this bias.
2. The shape test's power is ≤ 0.1, so "exponential" calls carry no weight.
3. All labels are a text-embedding proxy (bge decoy threshold). gte doubles the CV ≥ 2 count.
4. Kickoff designs include day 1 (the transient).
5. **Disclosure:** a smoke test of the kickoff code printed K38's result (k_off) at ~23:00 UTC, after Amendment A1 and before the full run. Nothing was changed afterwards.

### Confirmatory test (frozen 2026-10-04 after round 1; `analysis/confirm.py`, **not run**)
- **Guards:** `--confirm`, `H126_CONFIRM=1`, a SHA-256 match (`analysis/confirm.sha256`) and `holdout_ledger.check`. The held-out build goes only to `data/processed/H126-telegraph-goal-occupancy/confirm/`; decoys and thresholds always come from non-holdout statements.
- **Dry run:** on stand-ins #13, #25, #27, #41 (units and kickoffs), written to `$TMPDIR/h126_confirm_dry/`.
- **Targets:** #1, #14, #15, #28, #29, #32, #34, #43, #45–#50.
- **Frozen predictions:**
  - **C1 (primary):** Δln k_off 90% CI below 0 in ≥ 2/3 of testable held-out kickoffs (credence 0.75).
  - **C2:** "k_on only" in < ⅓ (0.75).
  - **C3:** call clock wins in ≥ 2/3 of regime-III units (0.65).
  - **C4:** P2 kill in ≤ ½ of units (0.85).
- **Ledger:** families content_alignment / behavior_states on content. Overlaps H105's kickoff C1 (same kickoffs, different statistic) and H54/H97 on held-out kickoffs (disclose).

**Claim that stands:** On each agent's call clock, an assigned goal kickoff lowers the off-goal switching rate as well as raising the on-goal rate (Δln k_off 90% CI below 0 in 15/17 kickoffs; #12 debate schedule Δln k_off −1.37 [−2.28, −0.35]), so the goal acts as a symmetric field, not an attempt-rate field. Exclusions: dwell shape and occupancy-from-dwells (not identifiable, A1); #51 heavy tails (post hoc, low power); NE38 (low power).

## Round 2 redirects
- **H126-R1. A calibrated classifier.** Jev on-goal labels on a sample give an external (q₀, q₁). Re-run the shape test with emissions fixed, which the synthetic suggests may restore power.
- **H126-R2. A semi-Markov fit for #51.** Use own-goal sequences with many statements per agent and fit dwell hazards directly (aging vs constant).
- **H126-R3. Kickoff time course.** Fit time-dependent rates through day 1–2 to see whether the k_off drop is immediate (field) or builds (commitment).


## Notes
- 2026-10-04 22:16 UTC: card written from HH367 (Vivian approved in the dashboard). Round-1 protocol: card → G-folder predictions → synthetic on the real skeleton → amendments → replication + natives → estimates → confirm.py frozen (dry-run only) → summary.
- H105-R1 asked for a calibrated on-goal classifier. No new labels are bought in round 1. The emission rates (q₀, q₁) are instead estimated from the dynamics (the HMM), and the synthetic checks whether that calibration is identifiable.
- 2026-10-04 22:41 UTC: the first synthetic run crashed (a singular 4×4 solve in the 4-state stationary distribution) before writing anything. It was replaced by the closed-form flux-balance stationary distribution and re-run (22:46–22:50 UTC). No real-data statistic was computed in between.
- 2026-10-04 ~22:51 UTC: Amendment A1 (above). ~23:00 UTC: smoke tests of the run code on K38, N12_12b, U17 and 51l; K38's P3 result was seen (disclosed under Caveats). 23:08 UTC: the full run crashed (a likelihood underflow in M4) and was re-run with guards (23:09–23:18 UTC); the guards change only degenerate evaluations.
- 2026-10-04 ~23:20–23:30 UTC: period folders filled, 293 estimates rows written, `confirm.py` rewritten to the round-1 findings (C1–C4), dry-run on stand-ins #13/#25/#27/#41 (stand-in numbers identical to round 1, e.g. K27, K41), frozen (`analysis/confirm.sha256`). **Not run.**
- #51 units 51b, 51k and 51l are single-day units and have no day folds, so 9/12 units are eligible for N2.
- Storage: `data/processed/H126-telegraph-goal-occupancy/` 3.5 MB.
- Proposed DEFINITIONS.md variants (H126): **latent goal state s_i,c (call clock)** = hidden on/off goal state of agent i at its ledger call c, read through H105's on-goal statement label with sensitivity q₁ and false-positive rate q₀; **telegraph rates k_on, k_off (per call)** = P(off → on) and P(on → off) per call in the two-state HMM; **dwell time (latent, calls)** = 1/k_off (on) and 1/k_on (off); **dwell-predicted occupancy p_dw** = k_on/(k_on + k_off); **raw run (observed)** = a maximal run of equal on-goal labels in an agent's statement sequence, in calls.
