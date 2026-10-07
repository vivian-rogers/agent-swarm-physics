# H134: A Pólya-urn self-field holds an agent on its project: the leave odds fall as the project's share of the agent's own context rises

**Status:** pre-registered (not run). Card, observables, nulls, predictions and kill rules written 2026-10-07 from HH377 (approved by Vivian 2026-10-07), before any H134 statistic on real data. No scheme, synthetic or analysis code exists yet.
**Question (GOALS.md):** **Q4** (where does the swarm's information live: is project stickiness held by the context window, as idle traps are?). Second: **Q5** (operator lever: does a context reset release an agent from a project it is stuck on?).
**Fields:** stat mech (kinetic Potts with a self-field; Pólya urn; aging), dynamics (renewal hazards, discrete-time survival), info theory (which store holds the state)
**Literature:** none in `literature/` covers urn-driven aging. Cited from memory (†): Pólya & Eggenberger (1923)† (urn reinforcement); Bouchaud, *J. Phys. I France* 2, 1705 (1992)† (trap model, aging); Allison (1982)† (discrete-time hazards with time-varying covariates).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime; **Context segment** with its **boundary rule** (H69: cut at `reset_consol | reset_session`); **Context fill** (`ctx_pos`); **Idle self-share f_call; urn rulers** and **Pólya urn (escape)** (H16, H72), whose form this card transfers from idle traps to projects; **Absorbed aging share ρ_urn** (H16); **Exposure (ledger receiving call)**; **Agent state (categorical, project/artifact strict)** (H11) as the project map. From H133 (proposed there): **agent state (categorical, project per call)** and **project hop (call)**. New named variants proposed for DEFINITIONS.md (not edited there; defined under Data scheme and Observables): **project visit (call)**, **dwell d (own calls)**, **project self-share f_proj (segment)**, **urn leave law β_F**, **aging share ε(F) (project)**, **reset step Δ_reset (visit)**, **dwell-tail calibration**.
**From:** HH377 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/10-potts/` (kinetic Potts walker with a context-held self-field), `physics-models/02-nonequilibrium-ising/` (single-spin escape kinetics, aging), `physics-models/08-copying-vs-transformation/` (the agent copies its own recent context)

## Source HH (verbatim from the HH list)
- **HH377 · A Pólya-urn self-field explains project stickiness: an agent's stay probability equals its own share of its recent context.** H72 round 2 found that the context self-share carries 65% of trap aging. The kinetic Potts version: the field toward the current project is the fraction of the agent's own recent context about that project.
  - *Prediction:* P(stay | call) is a rising function of own-context share for the current project, with slope near 1 on the logit scale. The dwell-time distribution that this rule predicts (heavy-tailed, aging) matches the observed one without fitting the tail.
  - *Check:* H72's self-share; project labels per call; simulate dwell times from the fitted per-call rule.
  - *Kill:* the predicted dwell tail misses the observed tail by more than its CI, or self-share adds nothing beyond the agent's time on the project.
  - *Impostors:* long projects fill the context and also last long. Use within-dwell variation of self-share, for example after a wipe (H44).
  - *Models:* 10, 02, 08 · *Builds on:* H72, H16, H44, H69

**Reading of "slope near 1 on the logit scale" (fixed now).** H16 and H72 write the urn as P(escape) = c_i (1 − f), i.e. logit or cloglog P(escape) = α_i + β_urn ln(1 − f) with β_urn = 1. Here "escape" is leaving the current project, and f is the project self-share. The HH's slope is β_F, the coefficient on ln(1 − f_proj); the urn predicts β_F = 1. The literal "P(stay) = f" is reported as a calibration curve only, because a per-call stay probability near 1 cannot equal a share near 0.2.

## What this card builds on (latest round of each cited card)
- **H72 (round 2, 2026-10-05):** in #51, the idle self-share of the context makes 65% [59, 71] of the aging clocks' cross-validated information redundant. Directed-input starvation explains −1%, chatter 22%; intrinsic-aging and frailty worlds give ≤ 22%. The urn coefficient is 1.09 [0.81, 1.33]. G38's self-share slope predicts G51 as well as G51's own fit (+19.8 nats per 1,000 wakes each). 31% of the aging information stays unexplained.
- **H16 (round 2, 2026-10-05):** a forced context erasure inside a pause chain lifts sustained escape at the next wake from 0.47 to 0.84 (log OR +2.68 [2.31, 3.16]), 4.6× the urn's dilution prediction. The urn matches the wake-clock aging exponent (−0.36 vs −0.35) and absorbs about half of it (ρ 0.47), but not the wall-clock exponent (−0.08 vs −0.77). Urn coefficient 1.05.
- **H44 (round 2, 2026-10-05):** a forced wipe triggers a one-call re-reading spike with an about-8-call tail (Θ_c +0.106 [0.089, 0.122], 9/9 regime-III periods). Post-reset reads re-open the working set at the mid-segment rate (habit, no targeted restoration).
- **H69 (round 2, 2026-10-05):** restatements copy what is still in the context (in-context enrichment OR 3.38 [2.56, 4.46], 4/4 scorable periods). The self-share trigger failed (pooled coefficient 0.53 [−0.12, 1.19]). An erasure ends loops as a step, not a dose (1.26 [0.95, 1.69] per log unit of own tokens removed).
- **H70 (round 1):** across a forced erasure the agent returns to its own repo for 89% of first commits (placebo 87%). The artifact store holds where an agent works.
- **H129 (round 1):** the project hop hazard falls with dwell in 32/39 unit-channels (work γ ≈ −0.2 to −0.4, attention −0.5 to −1.6 per e-fold of dwell). Dwell is not geometric. This is the observed aging the urn must reproduce.

## Question
At each call, do an agent's odds of leaving its current project fall in proportion to (1 − f), where f is the share of the agent's own calls in the current context segment that touched that project? And does that per-call rule, run forward, reproduce the observed aging of project dwell times without being fitted to them?

**Practical payoff:** if the context holds the project, a forced reset frees a stuck agent at a predictable rate. If the artifact store holds it (H70), a reset changes nothing and the operator must change the work itself.

## Model
**From:** `physics-models/10-potts/` (kinetic Potts walker), `physics-models/02-nonequilibrium-ising/` (escape kinetics), `physics-models/08-copying-vs-transformation/` (self-copying).

**H134 variant: a kinetic Potts walker with a Pólya-urn self-field.** Agent i holds project a during a visit. At each own call c inside the visit,
logit P(leave at c) = α_i + β_F · ln(1 − f_proj(c)) + β_d · ln d(c) + γ_R · ln(1 + N^nam_other(c)) + z_c,
with
- f_proj(c) the project self-share of the current context segment (below);
- d(c) the dwell in own calls since arrival;
- N^nam_other(c) named reads about other projects at c (H133's count; a kick term);
- z_c nuisance terms (hour-of-day bins, kind of the previous call, reset at c, day's first call).

The Potts field toward the current project is h_a(c) = −ln(1 − f_proj(c)), so the self-field grows as the agent's own calls fill its context with project a. A forced reset sets f_proj to 0 and the field to 0, at fixed dwell d.

**H134 says:** β_F = 1 (the urn), and β_d = 0 once f_proj is in. Aging in the marginal dwell hazard is then the growth of f_proj during a segment.

**Rivals.**
- **R-store (strongest rival; H70, H44):** the artifact store and the working-set habit hold the project. A reset does not raise leaving (H70: 89% vs 87% return). β_F absorbs dwell only because f_proj grows with d inside a segment.
- **R-intrinsic aging:** the leave hazard falls with dwell d by itself (β_d < 0, β_F = 0), for example because commitment builds.
- **R-frailty:** visits differ in a fixed leave rate. Long visits are the low-rate ones, so the marginal hazard ages with no per-visit aging.
- **R-geometric (H129's sticky walker):** constant per-call leave probability; no aging. H129 already rejects it in 32/39 unit-channels.

## Data scheme (`scheme/`)
Per-call project labels come from the shared builder `infra/shared/project_calls.py` proposed by H133 (one builder for both cards, STANDARDS §8). H134's `scheme/build.py` writes `data/processed/H134-polya-urn-project-stickiness/`.
- **Inputs:** `project_calls.parquet` (H133's per-call labels and hop flags); DQ1 `call_windows` (t_call, kind, talk, ctx_mode, gap_kind), `context_ledger_turns` (`ctx_pos`, `reset_consol`, `reset_forced`, `reset_session`, `k_ctx`, room), `context_ledger_items` (reads, `ment`); `infra/shared/copying.py: project_messages` (reads about projects); `calendar`, `period_units`, `roster`. No message text.
- **Project visit (call) (proposed variant):** a run of an agent's calls with one carried project label (H133's label, E = 100 own-call expiry). It ends at a hop (completed), at label expiry, roster leave or the unit's end (right-censored).
- **Dwell d (own calls):** the number of the agent's own calls from the visit's first call to call c, counting calls with no project touch. Variant: active hours.
- **Project self-share f_proj (segment) (proposed variant; primary ruler):** at call c in a visit on project a, f_proj(c) = n_a / n_own, with n_a = the agent's own earlier calls in the current context segment that touched a (strict mention in the call window), and n_own = all its own earlier calls in the segment. Segments are cut at `reset_consol | reset_session` (H69's rule). With a pseudo-count, 1 − f_proj = (n_own − n_a + ½)/(n_own + 1). Variants, fixed now: **f_lab** (denominator = own calls that touched any project); **f_entry** (adds room items in context: (n_a + k_a)/(n_own + k), with k_a the read items that link a); **f_rec** (share among the last 10 own calls in the segment).
- **Reset inside a visit:** a call with `reset_forced` (NE41's forced consolidation at the 41-call cap) whose agent is in a visit with d ≥ 10 at that call. Voluntary consolidations are reported only (their timing is the agent's choice and may follow project ends).
- **Regimes covered:** regime III only. Regime-I and II chat-mode calls have no context segment (H72), so f_proj is undefined there.
- **Output:** `visits.parquet` (unit, agent, project hash, arrival call, dwell, completed or censored), `calls.parquet` (visit id, call id, d, f_proj and variants, reset flags, nuisance terms, leave flag), `results/`, `synthetic/`, `_provenance.json`. Expected < 60 MB.
- **Reserved rows** are dropped with the shared reserved-row mask in `infra/shared/common.py` and the ledger's reserved flag (asserted).

**Structural precondition (counted before any outcome):** a unit is testable if it has ≥ 100 visits with ≥ 50 completed. The reset native needs ≥ 50 forced resets inside visits with d ≥ 10.

## Observables
- **O1 · Urn leave law β_F (primary):** agent-effects logit of leaving on ln(1 − f_proj) with the base terms, (a) without ln d, (b) with ln d. Day-block bootstrap CIs (200 draws).
- **O2 · Aging share ε(F) (project):** H72's reconcile metric. With day-blocked 5-fold cross-validation, G(A) = LL(B + ln d) − LL(B) is the dwell clock's information; ε(F) = 1 − [LL(B + F + ln d) − LL(B + F)] / G(A). Read only when G(A) > 0 with CI above 0 (H72's rule).
- **O3 · Dwell-tail calibration (the HH's unfitted test):** fit model B + F (no ln d) per unit. Run it forward on the unit's real call and reset skeleton from each real visit's arrival, 200 simulated copies per visit, with real censoring. Compare the simulated and observed (i) dwell hazard slope γ (H129's O5: logit h(d) = a + γ ln d), (ii) Kaplan–Meier survival at d = 10, 30, 100 and 300 calls, (iii) the 90th percentile of completed dwell. The tail is never in the fit.
- **O4 · Reset step Δ_reset (visit):** at the first call after a forced reset inside a visit, the observed change in leave log-odds against matched non-reset calls (same agent, same dwell decile, same f_proj decile before the reset). Urn prediction for each reset: Δ_pred = −β_F ln(1 − f_pre). Report observed/predicted. **Pseudo-reset placebo** (H44): the same contrast at the call 20 own calls before each forced reset.
- **O5 · Calibration curve (descriptive, HH-literal):** the observed per-call stay probability by f_proj decile.

## Null / baseline
- **N1 · Geometric walker:** constant per-visit-agent leave probability (H129 R-geometric). γ = 0.
- **N2 · Proxy worlds (synthetic):** intrinsic aging and frailty worlds give the ε(F) that a dwell proxy alone produces. Their 97.5th percentile is the band ε(F) must beat (H72's RC-P4 rule).
- **N3 · Pseudo-reset placebo** for O4.
- **Strongest rival:** R-store (H70, H44). It predicts β_F > 0 from the d–f collinearity inside segments, ε(F) inside the proxy band, and Δ_reset ≈ 0.

## Impostors (STANDARDS §1)
| Impostor | Relevant? | How it is handled | Status |
| --- | --- | --- | --- |
| Scheduler field | partly | The clock is the agent's own calls. Hour-of-day bins and the day's first call enter z_c. Nights do not create calls or hops. | planned (removed) |
| Exogenous field (kickoff, goal, operator) | yes | A kickoff or a human message can end visits for everyone. Variants drop the first 4 active hours after each kickoff and calls that read a human message. Named reads about other projects enter as a kick term (γ_R). | planned (partly) |
| Shared model priors | partly | Agent effects absorb stable stickiness. β_F is reported by lab; the urn coefficient should not depend on the lab if it is a context law (H72 found it portable across regime-III periods). | planned (partly) |
| Contemporaneous convergence | n/a | The statistic is within-agent persistence, not co-movement between agents. | n/a |
| (HH impostor) Long projects fill the context and last long | yes | Within-visit variation of f_proj at fixed dwell from forced resets (O4) and from the call-kind mix; ε(F) against the proxy band (O2); the dwell tail is not fitted (O3). | planned |

## Design: two layers (STANDARDS §4)
**Unit of analysis:** one goal period, split at `period_units`; #51 units separately. β_F across units is a phase-diagram comparison; a random-effects mean is reported next to the per-unit values (exception (d)). Regime III only.
- **Replication (role `replication`):** every non-reserved regime-III unit that meets the precondition. Candidates: G36 (regime-III units), G37, G38, G39, G40, G41, G42, G44, 51a–51l.
- **Natives (role `native`):**
  - **N1 · NE41 forced resets inside a visit (G51 primary, G38 second).** The 41-call cap times the reset, not the agent (NE41: ~18.6k forced vs ~12.2k voluntary non-reserved events). The urn predicts a leave step of −β_F ln(1 − f_pre); R-store predicts none.
  - **N2 · Urn constant across goal types.** Own-role weeks (G39, G42; H94 ownership price at or near the cap) vs shared-goal weeks (G37, G38, G41). A context law gives the same β_F; a goal field gives different ones.
  - **N3 · Bridge to H129.** In G38, compare the simulated hazard slope from O3 with H129's work and attention dwell slopes on the same days (descriptive).
- **Reserved (confirmation only; never read in exploration):** #43, #45–#50 and the #51 tail (2026-09-07 → 09-21); regime-I and II reserved periods are out of scope (no segments). A frozen `analysis/confirm.py` (β_F CI ∋ 1 and O3 calibration on #45–#47 and the #51 tail) is written after round 1 and runs only with Vivian's sign-off. Family: `project_potts`; disclose reuse with H72 (#51 tail, `behavior_states`), H129 and H133.

## Synthetic validation plan (axis F; run before any real-data statistic)
`analysis/synthetic.py` on the real G51 (two units) and G38 skeletons: real calls, real forced and voluntary resets, real touch patterns (which calls touch a project). Outcomes are simulated sequentially within visits, with real censoring. Agent intercepts SD 0.5. 200 runs per world.
- **W0 geometric:** constant leave probability.
- **W1 urn (H134):** β_F = 1, β_d = 0.
- **W2 intrinsic aging:** β_d = −0.4 per ln d, β_F = 0.
- **W3 frailty:** per-visit intercept SD 1.5, nothing else.
- **W4 store (R-store):** leave odds fall with the visit's cumulative touches (resets do not change them).
- **W5 mixture:** W1 with β_F = 0.5 plus W2 with β_d = −0.2.
- **Read:** bias and size of β_F in W0, W2, W3, W4 (with and without ln d); power to reject β_F = 0 and to include 1 in W1; the ε(F) band from W2, W3 and W4 (the proxy band); size and power of the reset step O4 (W4 vs W1); the size of the O3 calibration test when the fitted model is right (W1) and its power when it is wrong (W2, W3).
- **Pass rule:** size ≤ 0.10 and power ≥ 0.8 at the planted value on the G51 skeleton. A statistic that fails is descriptive, by a dated amendment written before any real-data statistic. If W4 gives β_F CI ∋ 1 in > 10% of runs, O1 alone cannot support H134 and O4 becomes the primary test.

## Prediction
*Written 2026-10-07, before any H134 statistic on real data. What I had seen: the cards of H72, H16, H44, H69, H70 and H129 at their latest rounds (numbers above); the `context_ledger_turns` schema (reset flags, `ctx_pos`). No per-call project label, visit, self-share or dwell count had been computed.*

| ID | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| P1 (HH) | **Self-share holds the project.** β_F > 0 with CI > 0 in model (b) in ≥ 2/3 of testable units | CI includes 0 in > 1/3 at power ≥ 0.8 | 0.55 |
| P2 (HH) | **The urn's slope.** β_F's CI contains 1 in model (b) in ≥ 1/2 of testable units, and the random-effects mean CI contains 1 | mean CI excludes 1 | 0.35 |
| P3 (HH) | **More than time on the project.** ε(F) above the proxy band (N2) in G51 | ε(F) inside the band | 0.35 |
| P4 (HH) | **The dwell tail follows.** In ≥ 1/2 of testable units, the observed γ and the survival at d = 100 and 300 calls lie inside the 95% bands simulated from model B + F | outside the band in > 1/2 | 0.3 |
| P5 | Aging is left over: β_d < 0 with CI < 0 in model (b) in G51 | β_d CI includes 0 | 0.6 |
| N1 | **Reset step (NE41).** G51: observed Δ_reset > 0 with CI > 0, and observed/predicted in [0.5, 2]; pseudo-reset placebo CI ∋ 0 | Δ_reset CI ∋ 0 at power ≥ 0.8 (R-store) | 0.25 |
| N2 | β_F in own-role and shared-goal weeks differs by < 0.3 (CIs overlap) | difference CI excludes 0 | 0.4 |
| N3 | Descriptive: the simulated γ lies between H129's work (−0.2 to −0.4) and attention (−0.5 to −1.6) values | none (descriptive) | none |

**Kill rules (from the HH, sharpened).**
- **Kill A (tail):** in ≥ 1/2 of testable units, the observed dwell hazard slope γ or the survival at d = 100 lies outside the 95% band simulated from the fitted per-call rule (O3), at a synthetic power ≥ 0.8 for that test.
- **Kill B (proxy):** in G51, ε(F) lies inside the proxy band from W2, W3 and W4. Self-share then adds nothing beyond the agent's time on the project.
- **Kill C (reset):** in G51, Δ_reset has a CI including 0 at power ≥ 0.8 for the urn's predicted step. The context then does not hold the project.

**Verdict rule.** *Supported:* P1, P2, P3, P4 and N1 hold. *Narrowed ("self-share is the best proxy for project aging, not its cause"):* P1 and P3 hold, N1 fails. *Failed:* Kill A, B or C fires with P1 failing, or two kills fire. *Inconclusive:* the precondition leaves < 3 testable units, or the identifying tests are unpowered.

**My credence before data:** supported 0.1; narrowed 0.3; failed 0.4; inconclusive 0.2. The main reason for doubt: H70's 89% vs 87% return across a forced erasure says the store, not the context, holds where an agent works. H69's self-share trigger also failed for loops (0.53 [−0.12, 1.19]).

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R-store (H70, H44 working-set habit), R-intrinsic aging, R-frailty, R-geometric (H129 sticky walker).
**Reserved periods used for confirmation:** none yet. Planned: #45–#47 and the #51 tail (frozen after round 1; not run).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 0 | not run |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 0 | not run |
| C adequacy | beats the null hierarchy, day-blocked out-of-sample data | 0 | not run |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | not run |
| E interventional | predicts the change across a natural experiment | 0 | not run |
| F identifiability | synthetic recovery with village sampling; survives preprocessing variants | 0 | not run |
| G ground truth | agrees with known structure | 0 | not run |
| H comparative | beats the named rivals | 0 | not run |
| I transfer | holds in other same-mode periods, including the reserved periods | 0 | not run |

## Results by goal period
No period has been run. Period folders (`goalperiod-subhypotheses/G<NN>/`, `NE41/`) are created with their dated predictions before each run. `goalperiod-subhypotheses/GNN/` is the unfilled template.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| regime-III replication units (precondition list) | replication | pending | not run |
| NE41 (G51, G38) | native N1 | pending | not run |
| G39, G42 vs G37, G38, G41 | native N2 | pending | not run |
| G38 | native N3 (descriptive) | pending | not run |

## Results
Not run.

## Notes
- 2026-10-07: card written from HH377 (approved by Vivian 2026-10-07). Round-1 order: structural counts → period READMEs with dated predictions → synthetic → dated amendments → replication and natives → estimates rows (`h134_beta_urn`, `h134_eps_selfshare`, `h134_reset_step`, `h134_tail_calibration`) → frozen `confirm.py` (dry run only).
- Depends on H133's shared per-call project builder (`infra/shared/project_calls.py`). Whichever card runs first writes it, with `--verify`.
- The project self-share is not H16/H72's idle self-share f_call and not H69's chat self-share s_t. It counts the agent's own calls that touched the current project.
- Compute: ≤ 2 threads, one heavy job at a time (STANDARDS §9).
