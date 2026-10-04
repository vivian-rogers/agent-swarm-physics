# H60: An index policy beats the nudger

**Status:** exploratory round 1 done (2026-10-04): **failed.** An index does not beat H35's once-early rule. Card, design and predictions were written before any outcome; synthetic validation first (A1 before real data). Replication on G51 (nudger-on days) and G38; natives NE43 and NE44. `analysis/confirm.py` is frozen and dry-run on stand-ins; **not run**.
**Headline (G51, active calls in 30 min, cross-fitted):** a nudge read at an idle gate adds 7.2 [5.0, 9.8] active calls. The logged nudger picks gates *worse than random*: random gate choice ×1.46 [1.22, 1.67], once-early (second gate of a trap) ×1.55 [1.25, 1.81]. The myopic index ×1.08 [−0.30, 3.44] and the Gittins-style one-per-trap index ×1.49 [0.46, 3.42] do not beat once-early (×0.69, ×0.96). The read-out clock r adds nothing (×0.98). On sustained escape the index reaches ×2.36 [1.07, 2.99] over logged but not over once-early (×1.77 [0.84, 2.11]), and the synthetic shows that nudger selection can fake such a gain (S3). The NE43 check on nudger-free days finds no selection signature in the untreated arm (calibration ratio 0.90 [0.71, 1.09]).
**Fields:** sociophysics (operator levers), info theory (value of information, feedback control), stat mech (escape kinetics)
**Literature:** none of the notes in `literature/` covers index policies. Textbook references: Gittins, *J. R. Stat. Soc. B* 41, 148 (1979)† (the index theorem); Whittle, *J. Appl. Prob.* 25A, 287 (1988)† (restless bandits, the subsidy index); Dudík, Langford & Li, *ICML* (2011)† (direct and doubly robust off-policy evaluation). The value-of-information bookkeeping is H35's (Kolchinsky–Wolpert, `physics-models/04-semantic-information/`). † = not in `literature/`.
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime; Action; Driving / external field (automated nudges); Interaction (addressed) for @-mentions; Semantic information (Kolchinsky–Wolpert) with work in place of viability (H35's proposed variant "Semantic efficiency of a controller"). New named variants proposed (not edited into DEFINITIONS.md): **"idle gate"**, **"trap age a (call clock)"** and **"input starvation s"** (H72's, from the shared gate table), **"time since last read-out r"** (= H72's directed starvation s_dir) and **"nudge index ν(x)"**.
**From:** HH252 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` ("Making the faithful ones better") · **Models:** `physics-models/04-semantic-information/` (primary), `physics-models/09-hawkes/` (kick response)
**Data inputs (shared tables first):** new shared builder `infra/shared/idle_gates.py` → `data/processed/shared/idle_gates/idle_gates.parquet` (DQ1 ledger; nudge target = leading @), `period_units`, `calendar`. Round-1b numbers from H35, H43, H16 and H04 enter only as predictions and ground truth.

**Question served:** Q5 (what can an operator do?). The deliverable is a nudging rule with a number attached.

## Question
Does a Gittins-style index, computed from an agent's trap age and its time since its last read-out, choose whom to nudge better than the logged nudger and better than H35's once-early rule, by more than H35's ×2.3?

## Design: two layers (Vivian, 2026-10-04)
- **Replication:** the common policy evaluation on every eligible period (≥ 500 idle gates and ≥ 50 gates that read a nudge to the agent): G51 (nudger on, 07-06 → 08-20) and G38. Role `replication`. G41 (18 nudged gates), G44 (11) and G37 (10) are counted only.
- **Natives:** NE43 (the nudger stops inside #51: a selection check on the untreated arm) and NE44 (the pause default changes 12 h → 5 min: the index's shape should flip). Role `native`.
- **Faithfulness lever:** HH252 targets **E** (a policy counterfactual) and **I** (the holdout). The scorecard says whether it moved them.

## Model
**From:** `physics-models/04-semantic-information/` (a controller that acts on measured state; the value of its information is the work it buys beyond a random controller with the same budget) and `physics-models/09-hawkes/` (a kick read at the receiving call changes the agent's response).

**H60 variant: a restless-bandit nudger on idle gates.**
- **Degrees of freedom.** Each agent in a trap meets a sequence of idle gates (H72's definition: a call that follows an idle call). At a gate the agent acts or idles again. A nudge posted during the pause is read at the gate (DQ1 receiving call).
- **State** x_g = (a, k, r): trap age a (minutes since the end of the agent's last active call), gate index k inside the trap, and **time since last read-out** r (minutes since the agent last read a directed item: a nudge to it, an @-mention or a named human message; r = H72's s_dir).
- **Response surface.** For outcome Y and nudge indicator M_g,

  μ(M, x, z) = α_i + b(x, z) + M·(θ₀ + θ_a ln a + θ_k ln k + θ_r ln r),   ĝ(x) = μ(1, x, z) − μ(0, x, z),

  with agent fixed effects α_i and nuisance z (current non-nudge reads, declared duration of the previous pause, hours since the window start, swarm activity, length of the last active run). Linear for active calls; logistic for binary escapes.
- **Nudge index** ν(x) = ĝ(x): the expected work a nudge read at this gate buys. Under a fixed budget and no refractoriness beyond one read-out (H43), a nudge is worth sending where ν is highest. That is the myopic (Whittle-subsidy) index.
- **Gittins-style index with one nudge per trap.** On a discretized state (a bin × r bin), with escape and transition probabilities from un-nudged gates, nudge at the first gate where ν(x) − λ ≥ C(x), the value of waiting for a later gate of the same trap; λ (a price per nudge) is set to spend the logged budget. This is an optimal stopping index.
- **Policies at the logged budget B** (number of gates that read a nudge to the agent): *logged*; *random* (B gates uniformly); *once-early* (H35: the second gate of each trap, k = 2); *index-myopic* (the B gates with the highest ν); *index-once* (Gittins-style, ≤ 1 nudge per trap); *index-a,k* (ν without r: does the read-out clock add?).
- **Policy value** V(π) = mean ĝ over the gates π selects (direct method). **Cross-fitting:** days are split into two interleaved halves; the selection model is fitted on one half and the evaluation model on the other, then swapped. Selection noise and evaluation noise are therefore independent, and the index cannot win by fitting noise.
- **Rivals.**
  - **R0 flat response:** ĝ does not depend on x; every policy has the same value per nudge.
  - **R1 the logged nudger is near-optimal:** V(index)/V(logged) ≈ 1.
  - **R2 once-early is already the optimum:** V(index)/V(once-early) ≈ 1.
  - **R3 selection artifact:** the nudger fires on agents in unobserved low-escape states, so ĝ is biased and the policy ranking is not causal.

## Data scheme
- **Input:** the shared gate table (`infra/shared/idle_gates.py`; definitions in H72's card and in the module docstring; `--verify` passed, 720 gates, 0 mismatches). Nudge target = leading @ (Known issue); M_g = 1 if the gate read ≥ 1 nudge whose leading @ is the agent.
- **Outcomes:** **y_calls30** (primary): active calls in [t_call, t_call + 30 min), censored at the calendar window end (the call-clock analog of H35's active minutes, so the ×2.3 bar is comparable); **y_sus** (a run of ≥ 3 active calls starts at the gate); **y_any** (the gate call is active: a glance).
- `scheme/build.py` writes `data/processed/H60-index-nudge-policy/gates.parquet` (eligible periods and native windows; codes and numbers only), plus `G<NN>/results.json`, `native/`, `synthetic/`, `confirm_dryrun/`, `_provenance.json`.
- **Regimes covered:** III only (nudges reach idle gates only in regime III in any number).

**Structural counts seen before the predictions (no outcomes):** gates / gates that read a nudge to the agent: G51 19,061 / 557 before 08-21 and 6,416 / 0 after; G38 1,628 / 58; G41 316 / 18; G44 429 / 11; G37 250 / 10; regime I/II ≤ 4.

## Observables (per period; agent FE; day-block bootstrap, 200 draws)
- **O1 mean nudge effect** at gates, per outcome (the average of ĝ over nudged gates).
- **O2 heterogeneity** (against R0): Wald test of θ_a = θ_k = θ_r = 0.
- **O3 policy values** per nudge and the ratios V(index-myopic)/V(logged), V(index-myopic)/V(once-early), V(index-once)/V(logged), V(index)/V(index-a,k), V(random)/V(logged).
- **O4 value of the nudger's information** (H35): ΔV = V(logged) − V(random), and the index's ΔV.
- **Not done:** inverse-propensity and doubly robust estimates. The nudge propensity at gates is about 3% and zero in many states, so weights are unstable; the direct method on cross-fitted models is primary, as in H35.

**Per-period verdict rule (replication, primary outcome).** *Supported:* V(index-myopic)/V(logged) ≥ 2.3 with the bootstrap 95% CI lower bound > 1, and V(index-myopic)/V(once-early) > 1 with CI lower bound > 1. *Failed:* the index/logged CI includes 1 or its point is < 1.5. *Mixed:* otherwise. *Descriptive:* the period is not eligible.

## Null / baseline
- **N1 synthetic (axis F):** the real G51 design (gates, states, nudge assignment) with planted outcomes: (S1) a state-dependent nudge effect (falling with k and r, known true index ratio); (S2) a flat effect (R0); (S3) a selection world, where the nudger's choice correlates with an unobserved low-escape state. Read: recovery of the ratios, the size of "index/logged > 1 with CI > 1" under S2, and the bias under S3.
- **N2 day-block bootstrap** inside each half (200 draws) for every CI.
- **N3 random policy** (the Kolchinsky full scramble at gate level) as the zero of the value of information.

## Impostors
| Impostor | Relevant? | How it is handled | Status (after round 1) |
| --- | --- | --- | --- |
| Scheduler field | yes | Hours-since-window-start bins and swarm activity in the outcome model; calls are the clock; outcomes censored at the window end | removed |
| Exogenous field (kickoff, goal, operator) | partly | Human messages and mentions read at the gate are nuisance terms; the nudge is the only treatment | removed |
| Shared model priors | partly | Agent fixed effects in every outcome model; the index uses no agent identity | removed |
| Contemporaneous convergence | no | The claim is a policy value for a directed kick, not copying; the nudge is read at a known call (ledger) | n/a |
| Selection on unobserved state (lever-specific) | yes | Past-only covariates, future kicks in both arms. Synthetic S3: a nudger that picks deep, stuck agents fakes ×2.6 (90% false rejections). NE43: the untreated model predicts nudger-free days equally well in targeted and other states (0.90 [0.71, 1.09]) | partly (NE43 passes; the estimator cannot exclude it) |

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness". Scored after round 1 (2026-10-04).
**Rival models:** R0 flat response, R1 logged near-optimal, R2 once-early optimal, R3 selection artifact.
**Locked holdout used for confirmation:** none. HH252's "#51 tail before 08-20" does not exist: the held-out tail starts 09-07, after the nudger stopped. Planned targets (frozen in `analysis/confirm.py`, not run): #47–#50 (short pauses, nudger on) and #45 (long pauses).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | State (a_sus, k_sus, r), treatment (leading-@ nudge read at the gate) and outcomes from the DQ1 ledger; assumptions listed. Regime-dependent: long-pause G38 has few multi-gate traps |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Selection on observables with agent FE; S3 shows it is not testable from the estimator itself. The NE43 calibration supports it for the untreated arm. Linear interactions extrapolate outside the nudger's support (random > logged) |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Policy values are cross-fitted on held-out day halves. The response is state-dependent (Wald p = 0.0004), but the index's selection does not transfer between halves (index CI [−2.2, 25.0] calls) |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | Held: NE43 accounting (logged nudges buy 0.19% [−0.03, 0.40]% of active calls) and untreated-arm calibration. Failed: the index signature (≥ ×2.3 over logged and > once-early), the read-out clock, the NE44 sign flip |
| E interventional | predicts the change across a natural experiment | 1 | NE43 used as a selection-free check (passes); NE44 shape flip fails (θ_k −3.0 before, −1.7 after; both CIs span 0) |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | On the real G51 design: a planted ×2.9 is recovered as ×2.6 (12% low; power 0.8; coverage 0.9); a flat response never rejects (0/16). A selection world fakes ×2.6. Not identifiable at ≤ 60 nudged gates (5-day stand-ins swing from ×0.04 to ×3.9) |
| G ground truth | agrees with known structure | 1 | Reproduces H35: the nudger is worse than random among gates and once-early beats it (×1.55 here vs ×1.55–2.0 in H35's gate models); the logged nudges' share of output (0.19% of calls) matches the lever table's "≈ 0.4% of commits" order |
| H comparative | beats the named rivals | 1 | R1 rejected (random and once-early beat logged); R0 rejected for active calls; R2 not rejected (index ≤ once-early); R3 not excluded for the binary outcomes |
| I transfer | holds in other same-mode periods, including the holdout | 0 | The claim fails in G51 and G38 (G38 index/logged 0.55 [−1.9, 7.5]). Holdout not used |

**Faithfulness lever (HH252 aimed at E and I):** E reached 1 through the NE43 selection check; I stays 0 (the claim fails in both eligible periods).

## Prediction
*Written 2026-10-04 (UTC), before any H60 outcome statistic on real data and before the synthetic validation.*

**What I had seen:** H35 (round 1: once-early ×2.3 [1.7, 5.2] in active minutes; nudge × ln k −0.32 ± 0.13 in G51, +1.18 in G38; round 1b: glance ×0.92, sustained ×1.03, work ×1.29 with CI spanning 0), H43 (no refractory window beyond one read-out; first nudge ×1.75 on a glance, lnHR 0.07 on sustained work), H16, H04, H30, H39, H59 round-1b headlines, the lever table, Known issues and the structural counts above. I had computed no outcome, no nudge effect and no policy value.

**Card-level predictions (credences in brackets).**
- **P1 (G51, active calls).** V(index-myopic)/V(logged) ≥ 2.3 with CI lower bound > 1 [0.3].
- **P2 (G51, active calls).** V(index-myopic)/V(once-early) > 1 with CI lower bound > 1 [0.35].
- **P3 (G51, sustained escape).** The mean nudge effect on sustained escape has a CI including 0, or V(index)/V(logged) has a CI including 1 [0.6].
- **P4 (G51, glance).** V(index)/V(logged) ≤ 1.2 for the glance outcome [0.5] (H35 round 1b: deep traps glance most).
- **P5 (G51, read-out clock).** V(index)/V(index-a,k) ≥ 1.1 on active calls [0.3].
- **P6 (G51, R0).** The heterogeneity test rejects a flat response for active calls at p < 0.05 [0.55].
- **P7 (G51, Gittins-style).** V(index-once) ≥ V(once-early) on active calls [0.5].
- **P8 (G38).** V(index)/V(logged) has a CI including 1 on active calls [0.6] (long pauses: a nudge wakes agents at any trap age, H35).

**What would count for H60:** P1 and P2 both pass in G51.
**What would count against it:** the index/logged CI includes 1 in G51, or the gain over once-early is ≤ 1.

**Natives (dated 2026-10-04, before running).**
- **N1, NE43 (selection check on the untreated arm).** The untreated outcome model μ(0, x, z) fitted on G51 days 08-07 → 08-20 (nudger on) is applied to 08-21 → 09-02 (nudger off, no selection). (a) The calibration ratio (observed / predicted active calls) differs by < 15% between states the nudger targets (k ≥ 4) and the rest [0.5]. A larger gap is the R3 signature: the nudger's targets differ in ways the model does not see. (b) The loss of the logged nudges, Σĝ over 08-07 → 08-20 nudges, is ≤ 1% of that window's active calls [0.8].
- **N2, NE44 (pause default 12 h → 5 min on 06-11).** Exception (c): the transition is the object. The nudge × ln k slope θ_k on active calls is ≥ 0 in the long-pause regime-III periods (G37–G44 pooled, period fixed effects) and < 0 in G51 [0.45]. If so, the index has to be re-fitted after a scaffold change, and a fixed "once-early" rule does not transfer.

### Amendment A1 (2026-10-04, before any real-data outcome; from structural chain counts)
- **What I had seen:** with the glance-sensitive clock (a, k from the last active call), G51's 25,477 gates form 17,538 chains, so most chains end at their first gate, and "k = 2" would not mean H35's k = 2. H35's once-early rule is defined on TS2r chains, where a glance followed by a re-pause does not end the chain.
- **Change:** the state uses the glance-robust clock from the shared table: a = a_sus (minutes since the end of the last sustained active run, ≥ 3 calls), k = k_sus (gate index since then), and a chain restarts at k_sus = 1. Once-early = the gate with k_sus = 2. Gates before the agent's first sustained run of the day (no a_sus) are dropped. The logged budget becomes the nudged gates that remain (G51 nudger-on days: 429; G38: 58).
- Predictions, outcomes and the verdict rule are unchanged.

## Results by goal period
| Period | Role | Verdict | Key numbers (active calls in 30 min; ratios to the logged nudger) |
| --- | --- | --- | --- |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication | failed | 404 nudged gates; effect 7.2 [5.0, 9.8] calls; index ×1.08 [−0.30, 3.44]; once-early ×1.55 [1.25, 1.81]; random ×1.46 [1.22, 1.67]; Gittins ×1.49 [0.46, 3.42]; sustained: index ×2.36 [1.07, 2.99], index/once-early 1.77 [0.84, 2.11] |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | failed | 49 nudged gates; effect 10.7 [2.6, 19.3] calls; index ×0.55 [−1.94, 7.46]; once-early ×1.11 [0.37, 3.38]; heterogeneity p = 0.43 |
| [G37](goalperiod-subhypotheses/G37/README.md), [G41](goalperiod-subhypotheses/G41/README.md), [G44](goalperiod-subhypotheses/G44/README.md) | replication | descriptive | 9, 17, 11 nudged gates: not eligible |
| [NE43](goalperiod-subhypotheses/NE43/README.md) | native | supported | untreated-arm calibration targeted / other 0.90 [0.71, 1.09]; logged nudges bought 0.19% of active calls |
| [NE44](goalperiod-subhypotheses/NE44/README.md) | native | failed | θ_k −2.96 [−10.7, 5.6] before 06-11, −1.71 [−6.2, 3.1] in G51: no sign flip |

## Results
### Exploratory round 1 (2026-10-04; non-holdout)
- **Scripts:** shared `infra/shared/idle_gates.py` and `infra/shared/hazard_fe.py`; `scheme/build.py`; `analysis/h60lib.py`, `synthetic.py`, `run_period.py`, `native.py`, `figures.py`, `write_outputs.py` (period folders, 30 estimate rows), `confirm.py` (frozen, dry run only).
- **Numbers:** `data/processed/H60-index-nudge-policy/` (`G<NN>/results.json`, `native/native.json`, `synthetic/synthetic_results.json`, `confirm_dryrun/`; ≈ 2 MB).
- **Figures:** `figures/summary_obs.pdf` (policy values per nudge, three outcomes), `figures/synthetic_validation.pdf`.

**Synthetic validation (axis F; real G51 design, planted outcomes).** S1 heterogeneous response: true index/logged 2.91, estimated 2.56 ± 0.39 (cross-fitting attenuates by 12%); CI lower bound > 1 in 8/10; CI covers truth 9/10. S2 flat response: estimated 0.92 ± 0.56; CI lower bound > 1 in 0/16. S3 selection (flat true effect, nudged deep gates have lower unobserved baseline): estimated 2.62, true 1.0; CI lower bound > 1 in 9/10. The estimator recovers real heterogeneity and is clean under a flat response, but it cannot tell state-dependent response from state-dependent selection.

**Outcome vs prediction.**

| Prediction | Outcome | Verdict |
| --- | --- | --- |
| P1 index/logged ≥ 2.3, CI > 1 (G51, active calls) | ×1.08 [−0.30, 3.44] | fails |
| P2 index/once-early > 1, CI > 1 | ×0.69 [−0.22, 2.12] | fails |
| P3 sustained: effect ∋ 0 or index/logged ∋ 1 | effect +0.24 [0.20, 0.31]; ×2.36 [1.07, 2.99] | fails |
| P4 glance: index/logged ≤ 1.2 | ×2.26 [1.23, 2.49] | fails |
| P5 read-out clock adds ≥ 10% | index/index(a,k) ×0.98 [0.51, 3.24] | fails |
| P6 response not flat (p < 0.05) | Wald p = 0.0004 | holds |
| P7 Gittins one-per-trap ≥ once-early | ×0.96 [0.31, 2.11] | fails (tie) |
| P8 G38: index/logged ∋ 1 | ×0.55 [−1.94, 7.46] | holds |
| N1 NE43 calibration, accounting | 0.90 [0.71, 1.09]; 0.19% of calls | holds |
| N2 NE44 shape flip | θ_k < 0 on both sides, CIs span 0 | fails |

**Reading.**
1. **A nudge read at an idle gate works.** It adds 7.2 [5.0, 9.8] active calls in the next 30 min (mean 37) and raises the chance of a sustained run by 0.24. Summed over the logged nudges, that is 0.19% of the swarm's active calls (NE43): a real per-agent lever with a negligible swarm-level stake.
2. **The logged nudger chooses badly; a simple rule fixes most of it.** Choosing gates at random beats it ×1.46, and nudging each trap once at its second gate beats it ×1.55. The nudger spends its budget on deep traps, where the response is lowest (H35).
3. **An index adds nothing reliable beyond once-early.** The response surface is state-dependent (p = 0.0004), but a surface fitted on half the days does not pick better gates on the other half for active calls. The read-out clock r carries no targeting value.
4. **For sustained escape and glances the index looks better** (×2.3–2.4 over logged), but the synthetic S3 world produces the same gain from nudger selection alone. NE43 finds no selection signature in the untreated arm, which makes selection less likely but does not exclude it for the treated arm.
5. **Long pauses (G38) resolve nothing:** 49 nudged gates, flat response (p = 0.43).

**Caveats.**
- Direct-method values extrapolate the response into states the nudger never visits (random > logged rests partly on that).
- Two cross-fit halves of about 17 days each; ratio CIs are wide, and denominators near 0 make some bootstrap ratios unstable.
- Selection on observables is assumed; S3 shows the cost if it fails.
- The work ledger (commits) is not an outcome here; H35 round 1b found nudges buy ≈ 0 commits.
- A1 (glance-robust clock) was made before outcomes; no post-hoc change.

## Round 2 redirects (2026-10-04)
- **H60-R1. Ship the simple rule, test it as an intervention.** Once-early (second gate of a trap) beats the logged nudger ×1.55 here and in H35; an A/B on a live scaffold (or the holdout via `confirm.py`) is the decisive test, not a better index.
- **H60-R2. Separate response from selection.** Use @-mentions read at gates as a second treatment with a different sender rule; if the sustained-escape index ranking agrees across senders, the gain is response, not nudger selection.
- **H60-R3. Price the work.** Re-run the policy values with DQ4 work commits in 60 min as the outcome; if the effect is ≈ 0 (H35), no targeting rule matters for output.

## Notes
- 2026-10-04: round 1 started. The gate table is shared with H72 (`infra/shared/idle_gates.py`).
- 2026-10-04: round 1 done. Compute: local, ≤ 4 threads until the coordinator's load notice, then ≤ 2 threads and one job at a time; ≈ 30 min CPU. Disk ≈ 2 MB.
- 2026-10-04: holdout. Exploratory loads use the shared gate table (held-out days excluded); the scheme asserts it. HH252's "#51 tail before 08-20" does not exist; the frozen confirm targets are #47–#50 and #45. The 5-day stand-ins show that ratio statistics at ~50–60 nudged gates per period are noisy (×0.04 to ×3.9), so the confirmatory test has low power.
