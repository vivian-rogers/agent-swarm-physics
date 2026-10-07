# H134: A Pólya-urn self-field holds an agent on its project: the leave odds fall as the project's share of the agent's own context rises

**Status:** failed (round 1, 2026-10-07). Kill A fires (the self-share rule misses dwell aging in 25/25 units) and P1 fails (urn slope +0.07 [−0.05, +0.19]). A forced reset still releases agents (+0.40 [+0.25, +0.54] in G51), as a step 24× the urn's size. Card, observables, nulls, predictions and kill rules written 2026-10-07 from HH377 (approved by Vivian 2026-10-07), before any H134 statistic on real data. No scheme, synthetic or analysis code exists yet.
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
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | round 1: f_proj, d, visits from `project_calls` + ledger; ruler amended (A1); 27% flicker hops |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | round 1: censoring audited in synthetic; forward O3 replaced (A6); hazard depends on dwell |
| C adequacy | beats the null hierarchy, day-blocked out-of-sample data | 0 | round 1: G(F) −0.03 [−0.18, +0.09] held out in G51 |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | round 1: dwell slope outside the O3-pp band in 25/25 units |
| E interventional | predicts the change across a natural experiment | 1 | round 1: NE41 step +0.40 [+0.25, +0.54], right sign, 24× the urn's size |
| F identifiability | synthetic recovery with village sampling; survives preprocessing variants | 1 | round 1: β_F, β_d, O3-pp pass; ε(F) and the step's null side unpowered |
| G ground truth | agrees with known structure | 0 | none available |
| H comparative | beats the named rivals | 0 | round 1: intrinsic aging (β_d −0.6) beats the urn |
| I transfer | holds in other same-mode periods, including the reserved periods | 0 | round 1: β_F differs by goal type (N2 +0.84 [+0.31, +1.37]) |

## Results by goal period
Round 1 (2026-10-07), exploration units only. Each folder holds its dated prediction (written before the run) and its results. `goalperiod-subhypotheses/GNN/` is the unfilled template.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G36](goalperiod-subhypotheses/G36/) (36b, 36c) | replication | failed | β_F +0.20, −0.26; γ outside band 2/2 |
| [G37](goalperiod-subhypotheses/G37/) | replication, N2 shared | failed | β_F −0.67 [−0.96, −0.14]; γ −0.74 vs band [−0.41, −0.22] |
| [G38](goalperiod-subhypotheses/G38/) (38a, 38b, 38e) | replication, N2 shared, N3 | failed | β_F −0.19 to +0.09; γ −0.69 to −0.92 outside 3/3 |
| [G39](goalperiod-subhypotheses/G39/) | replication, N2 own-role | failed | β_F +0.61 [−0.01, +1.25]; γ outside |
| [G40](goalperiod-subhypotheses/G40/) | replication | mixed | β_F +1.26 [+0.70, +2.09] (urn-sized); γ −0.90 vs band [−0.30, −0.13] |
| [G41](goalperiod-subhypotheses/G41/) | replication, N2 shared | failed | β_F −0.35 [−0.63, +0.19]; γ outside |
| [G42](goalperiod-subhypotheses/G42/) (42a, 42b) | replication, N2 own-role | failed | β_F +0.57, +0.31 (wide CIs); γ outside 2/2 |
| [G44](goalperiod-subhypotheses/G44/) (44a, 44b) | replication | failed | β_F +0.44, −0.12; γ outside 2/2 |
| [G51](goalperiod-subhypotheses/G51/) (51a–51l) | replication | failed | β_F RE +0.13 [+0.03, +0.23]; β_d RE −0.58 [−0.62, −0.55]; γ outside 12/12 |
| [NE41](goalperiod-subhypotheses/NE41/) (G51, G38) | native N1 | failed | Δ_reset G51 +0.40 [+0.25, +0.54] vs urn +0.016; placebo −0.02 |
| G39, G42 vs G37, G38, G41 | native N2 | failed | difference +0.84 [+0.31, +1.37] |

## Results
See "Round 1 (2026-10-07)" below the scorecard: failed. Not run on reserved data.

## Round 1 (2026-10-07)

### Structural counts (before any outcome statistic)
Built by `scheme/build.py` from the shared per-call labels (`infra/shared/project_calls.py`, commit 18e52ee) and the DQ1 ledger, regime III, reserved rows dropped and asserted. 989,450 risk calls in 58,043 project visits (call). Mean project self-share f_proj 0.04 (G42) to 0.20 (G40); 61% of risk calls have f_proj > 0. Context segments are short: a forced reset comes at the 41-call cap. **Precondition:** 25 of 27 non-reserved regime-III units are testable (≥ 100 visits, ≥ 50 completed); 38c (59 visits) and 38d (76) are not. Forced resets inside visits with d ≥ 10: G51 7,777 (all 12 units ≥ 50), G38 1,179.

### Synthetic validation (axis F)
`analysis/synthetic.py` on the real visit and touch paths of 51c, 51h (G51) and 38a (G38): real calls, resets, touch patterns, f_proj and d. Only the leave outcome is simulated (first hit along each real path, censored at the real end). Agent intercepts SD 0.5; base rate −2.4 on the logit scale (near the counted completed-visit-per-call ratio). 200 runs per world (O3 variants: 100 runs on 51c and 51h). Intervals are agent-day cluster 95% intervals. Numbers: `data/processed/H134-polya-urn-project-stickiness/synthetic/summary.json`, `o3_*.json`, `o4pool_*.json`.

| Test | Size (null worlds) | Power / bias at the planted value | Pass rule (G51) |
| --- | --- | --- | --- |
| O1 β_F > 0, model (b) | W0 0.04 / 0.03; W2 0.06 / 0.04; W3 0.04 / 0.01 (51c / 51h) | W1: β̂_F 1.01 / 1.01 (SD 0.14 / 0.15), power 1.00 / 1.00; 38a 0.99 | pass |
| O1 β_F CI ∋ 1, model (b) | W4 (R-store) 0.00 / 0.00; W5 (β_F 0.5) 0.01 / 0.01 | W1 coverage 0.92 / 0.94 (38a 0.93) | pass |
| **R-store fakes β_F > 0** | W4: β̂_F +0.22 / +0.26, CI > 0 in 0.61 / 0.68 (38a 0.47) | — | P1 is not specific; P2 carries the store test |
| O1 model (a), no ln d | W3 frailty bias −0.08 / −0.19 (38a −0.40) | W1 unbiased | model (b) is primary (as the card says) |
| β_d < 0, model (b) | W1 0.01 / 0.01 | W2 power 1.00 / 1.00, β̂_d −0.39 / −0.39 | pass |
| O2 ε(F) above the proxy band | band (97.5% of W2–W4) 0.019 / 0.055 (38a 0.065) | W1: G(A) > 0 in only 0.13 / 0.27 of runs; ε above band 0.45 / 0.65; W5 0.00 / 0.05 | **fails (power)** |
| O3 card design (forward from arrival), Kill A rule | W0 0.27 / 0.19; W1 0.22 / 0.23 | W2 0.99 / 0.98, W3 1.00 / 1.00, W4 0.62 / 0.28 | **fails (size)** |
| O3 P90 of completed dwell | outside the band in 100% of runs in every world | — | biased: descriptive |
| O3 with coefficient draws (forward) | W0 0.14 / 0.16; W1 0.20 / 0.14 | — | fails (size) |
| **O3-pp** (posterior-predictive on the observed risk rows, coefficient draws) | W0 0.03 / 0.03; W1 0.02 / 0.02 | W2 1.00 / 1.00, W3 1.00 / 1.00, W4 1.00 / 1.00, W5 1.00 / 0.99 | pass |
| O4 reset step, G51 pooled (7,760 resets, independent rows) | W0 0.03; W4 0.04 | W1: Δ̂ +0.086 vs predicted +0.101, power **0.52**; W5 0.27 | positive test valid; **negative unpowered** |
| O4 reset step, G38 pooled (1,179) | W0 0.04; W4 0.03 | W1 power 0.23 | unpowered |
| O4 pseudo-reset placebo (per unit) | 0.01–0.06 (two-sided) | — | pass |

**What the synthetic shows about the design.** On the real skeleton, an urn with β_F = 1 makes almost no dwell aging. The self-share lives in segments of at most 41 calls, so it does not grow with dwell; G(A) > 0 in only 13–27% of W1 runs. The urn therefore cannot be the cause of strong observed aging, and ε(F) has nothing to absorb. O3-pp tests exactly this: does the fitted per-call rule without ln d reproduce the observed dwell slope.

### Amendments (dated 2026-10-07, written before any real-data statistic)
- **A1 (ruler).** f_proj = n_a / (n_own + ½), so 1 − f = (n_own − n_a + ½)/(n_own + ½). The card's pseudo-count (n_a + ½)/(n_own + 1) gives f = ½ at a segment start, which contradicts "a forced reset sets f_proj to 0". Variants use the same pseudo-count.
- **A2 (CIs).** Agent-day block bootstrap (200 draws) replaces the day-block bootstrap. Units have 2–13 days, so day blocks are too few. Agent-day cluster SEs have size 0.01–0.06 in the null worlds.
- **A3 (units).** A visit that crosses a unit boundary is split. Its rows keep their true dwell d (left truncation); the hazard by d handles late entry.
- **A4 (kick term, exogenous variants).** K = ln(1 + N^nam_other) counts agent messages read at the call (ledger items, not omitted) that name the reader (`ment`) and link another project (`project_mentions_chat`). H133's read table is card-local, so H134 rebuilds the count. The kickoff variant drops the first 4 hours after the goal period's first day window opens.
- **A5 (reset prediction).** Δ_pred = −β_F ln(1 − f_pre) with β_F from model (b) and f_post = 0 (A1). Δ_reset is the Mantel–Haenszel log odds ratio with the Robins–Breslow–Greenland SE; G51 and G38 pool unit log ORs by inverse variance.
- **A6 (O3 primary).** The card's forward design fails size (0.14–0.27 with the true model). The primary O3 test is O3-pp: fit B + F + K (no ln d), draw coefficients from N(β̂, V_cluster), draw one Bernoulli leave per observed risk row, and compare the observed dwell slope γ and KM survival at d = 100, 300 with the 95% bands of 200 copies. The forward design is reported as descriptive. P90 of completed dwell is descriptive (biased in every world).
- **A7 (untestable parts, declared before any outcome).** P3 and Kill B: power 0.45–0.65 < 0.8, so ε(F) is reported but cannot support or kill. N1's negative side and Kill C: power 0.52 in G51 (0.23 in G38) at the urn's predicted step, so a null reset step cannot kill H134; a positive step with CI > 0 still counts (size 0.03).
- **A8 (P1 reading).** R-store makes β_F > 0 in 47–68% of runs, so P1 alone does not separate the urn from the store. P2 (CI ∋ 1) does: W4 gives CI ∋ 1 in 0–4% of runs (below the card's 10% switch, so O1 stays primary for P2).
- Synthetic code saw the real visit paths and the structural counts. It computed no real-data outcome statistic.

### Results on exploration data (2026-10-07)
`analysis/run.py` per unit, `analysis/summarize.py` across units; post hoc `analysis/posthoc.py`. 25 testable regime-III units, 989,450 risk calls. Numbers: `data/processed/H134-polya-urn-project-stickiness/results/summary.json`. Figure: `figures/round1_summary.pdf`.

| ID | Prediction | Result [95% CI] | Verdict by the rule |
| --- | --- | --- | --- |
| P1 | β_F > 0 (CI > 0), model (b), in ≥ 2/3 of units | 3/25 (G40, 51a, 51c); one unit below 0 (G37 −0.67 [−0.96, −0.14]) | **fails** |
| P2 | β_F CI ∋ 1 in ≥ 1/2, and RE mean CI ∋ 1 | 6/25; RE mean +0.07 [−0.05, +0.19] (τ² 0.05) | **fails** |
| P3 | ε(F) above the proxy band in G51 | ε(F) +0.001 [−0.005, +0.008] vs band 0.055; G(A) 13.2 [11.0, 15.8] nats per 1,000 risk calls | untestable (A7); inside the band |
| P4 | γ and KM(100), KM(300) inside the O3-pp bands in ≥ 1/2 | γ inside 0/25; KM(100) 7/25; KM(300) 1/25 | **fails** |
| Kill A | γ or KM(100) outside in ≥ 1/2 (power ≥ 0.99) | 25/25 outside | **fires** |
| Kill B | ε(F) inside the band | inside, but unpowered (A7) | not applied |
| P5 | β_d < 0 (CI < 0) in G51 | RE mean −0.58 [−0.62, −0.55]; 12/12 G51 units; all 25 units −0.26 to −0.83 | **holds** |
| N1 | G51 Δ_reset > 0 (CI > 0), obs/pred in [0.5, 2], placebo ∋ 0 | +0.40 [+0.25, +0.54] vs urn +0.016 (ratio 24); placebo −0.02 [−0.19, +0.14] | **fails** (step 24× the urn's) |
| Kill C | Δ_reset CI ∋ 0 | CI > 0 | does not fire |
| N2 | own-role vs shared-goal β_F differ by < 0.3 | own-role +0.54 [+0.06, +1.03], shared −0.30 [−0.50, −0.09]; difference +0.84 [+0.31, +1.37] | **fails** |
| N3 | G38 simulated γ between H129's work and attention values | fitted rule −0.04 to −0.43 (O3-pp), −0.29 to −0.62 (forward); observed −0.69 to −0.92 | descriptive: the rule sits in the work range, the data in the attention range |

**Descriptive and variant results.**
- The card's forward O3 design (failed size, A6): γ inside 8/25 (mostly G51, where the double censoring pulls the simulated slope down), KM(100) inside 3/25, both inside 0/25. Kill A would fire under it too.
- Self-share variants, model (b): f_lab and f_rec stay within −0.5 to +0.9. f_entry, which adds the room's read items about the project, gives larger slopes in G51 (+0.5 to +1.4). That variant mixes the agent's own share with others' messages; it is reported, not tested.
- Kick term (A4): named reads about another project raise leaving, K +0.58 to +1.22 with CI > 0 in 6/12 G51 units (also 36b). This agrees with H133's read-out coupling; it is not one of this card's predictions.
- O5 (HH-literal calibration curve, raw, no adjustment): the stay probability per call is 0.95–0.99 at f_proj = 0. In G51 it falls to 0.77–0.89 in the top decile (f_proj ≈ 0.46); in G38–G42 it stays flat (0.92–0.99). It never tracks f_proj itself, so "P(stay) = f" fails literally, as the card expected. The raw fall is the opposite of the urn's direction; model (b) adjusts it for dwell and agent.
- **Post hoc (after the O4 result):** 26.7% of completed visits end in a flicker (A → B → A within 5 calls). With flickers counted as stays, the reset step is +0.46 [+0.30, +0.62] in G51 and +0.59 [+0.07, +1.11] in G38; placebos +0.05 [−0.14, +0.23] and +0.05 [−0.57, +0.67]. The step is a sustained release, not a flicker.

**Reading.** Project stickiness ages strongly (β_d about −0.6 per e-fold of dwell, CI < 0 in 25/25 units). The project self-share does not carry it: its slope is near 0 (RE +0.07), it explains none of the dwell clock's held-out information (G(F) −0.03 [−0.18, +0.09]), and a rule built on it misses the dwell slope in every unit. The synthetic shows why. Segments last at most 41 calls, so the self-share cannot grow with a dwell of hundreds of calls. The context still matters: a forced reset releases the agent (+0.40 log-odds) at fixed dwell and self-share decile. That is a step, not the urn's dose, as H69 found for loops and H16 for idle traps (4.6× the urn). R-store's "no step" is rejected; R-intrinsic aging (or frailty) carries the dwell aging.

**Verdict: failed.** Kill A fires and P1 fails (card's verdict rule). N1's step is real but 24× the urn's prediction, so the "narrowed" reading also fails (P1 and P3 do not hold).

### Impostor table (round 1)
| Impostor | Relevant? | How it was handled | Status |
| --- | --- | --- | --- |
| Scheduler field | partly | Own-call clock; hour-since-window bins, previous call kind and first call of the day in z. The reset contrast compares calls of the same agent at the same dwell and self-share decile. No wall-clock test was run. | partly |
| Exogenous field (kickoff, goal, operator) | yes | Kick term K in every model. Variants: drop the first 4 h of each goal period (β_F moves by ≤ 0.3 except G40, +1.26 → +1.94, and 42a, +0.57 → −0.51, both with wide CIs), drop calls that read a human message (β_F moves by ≤ 0.2). N2 shows β_F differs by goal type, so a goal field shapes the slope. | partly |
| Shared model priors | partly | Agent fixed effects. The lab split of β_F was not run (β_F ≈ 0 left nothing to split). | partly |
| Contemporaneous convergence | n/a | Within-agent persistence, not co-movement. | n/a |
| (HH) long projects fill the context and last long | yes | Moot for β_F, which is near 0. The reset step is measured at fixed dwell decile and self-share decile, with a pseudo-reset placebo near 0. | removed (for O4) |

### Scorecard (round 1)
| Axis | Score | Evidence |
| --- | --- | --- |
| A mapping | 1 | f_proj, d and visits are defined from `project_calls` and the ledger; the ruler was amended (A1); 27% of hops are flickers. |
| B assumptions | 1 | Segment cut and censoring audited in synthetic; the forward O3 design failed size and was replaced (A6). The leave hazard is not Markov in self-share (dwell dependence). |
| C adequacy | 0 | Self-share adds no held-out information in G51 (G(F) −0.03 [−0.18, +0.09]). |
| D unfitted predictions | 0 | The dwell slope lies outside the O3-pp band in 25/25 units. |
| E interventional | 1 | NE41: the reset step has the predicted sign and survives the placebo, but it is 24× the urn's size. |
| F identifiability | 1 | β_F, β_d and O3-pp pass size and power; ε(F) and the reset step's null side are unpowered (A7). |
| G ground truth | 0 | none available. |
| H comparative | 0 | R-intrinsic aging (β_d −0.6) beats the urn; R-store's no-step prediction fails, but so does the urn's size. |
| I transfer | 0 | β_F differs between own-role and shared-goal weeks (+0.84 [+0.31, +1.37]); reserved periods not used. |

**Claim that stands:** In 25 regime-III units, an agent's project self-share in its context does not set its leave odds (urn slope random-effects mean +0.07 [−0.05, +0.19], urn value 1), and a per-call rule built on it misses the observed dwell aging in 25/25 units; the context acts as a step instead: a forced reset raises leaving by +0.40 [+0.25, +0.54] log-odds in G51 (24× the urn's prediction, placebo −0.02). *Excluded:* ε(F) and Kill B (unpowered, A7); the card's forward O3 design (failed size) and P90 (biased); the sustained-leave reset step (post hoc); the f_entry variant and the kick term K (descriptive); G38's reset step (unpowered, CI ∋ 0).

## Round 2 redirects
**What the direction is really after:** where an agent's project commitment is stored, and which operator action releases it; round 1 says the context acts as a reset step, not as a self-share dose.
- **H134-R1. Reset as a step clock.** Model the reset as a step in the leave hazard (own calls since the last forced reset) and measure its decay over the next calls (H44's 8-call tail).
- **H134-R2. Aging vs frailty.** Separate intrinsic dwell aging from per-visit frailty with repeat visits to the same project.
- **H134-R3. Goal-type slope.** Explain N2: why the self-share slope is positive in own-role weeks and negative in shared-goal weeks.
- **H134-R4. Sustained hops.** Re-run with a minimum-dwell label (no A → B → A flickers) as the primary hop definition.

## Notes
- 2026-10-07: card written from HH377 (approved by Vivian 2026-10-07). Round-1 order: structural counts → period READMEs with dated predictions → synthetic → dated amendments → replication and natives → estimates rows (`h134_beta_urn`, `h134_eps_selfshare`, `h134_reset_step`, `h134_tail_calibration`) → frozen `confirm.py` (dry run only).
- Depends on H133's shared per-call project builder (`infra/shared/project_calls.py`). Whichever card runs first writes it, with `--verify`.
- The project self-share is not H16/H72's idle self-share f_call and not H69's chat self-share s_t. It counts the agent's own calls that touched the current project.
- Compute: ≤ 2 threads, one heavy job at a time (STANDARDS §9).
