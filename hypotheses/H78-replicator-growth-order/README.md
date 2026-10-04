# H78: Replicator growth order: herding vs division of labor

**Status:** exploratory round 1 done (2026-10-04, non-holdout only). **Failed as posed: the growth order does not separate herding from division of labour, and it is not identifiable at village counts.** Formation-free recruitment gives p̂ = 0.73 [−0.08, 1.54] (#31) and 1.05 [0.00, 2.09] (#41) in herding weeks, and 1.94 [1.22, 2.67] in the own-artifact #51 (271 recruitments), the opposite of the prediction. A synthetic world with plain first-order copying (p = 1) and repo fitness spread reproduces every value (σ_A = 0.5–1.0 gives 1.3–2.7), and a planted p = 0.5 is read as ≈ 1.0. Most arrivals are formation (births and kickoff-named repos, 76–100%); the H28 blind window is negligible at commit level (4 of 601 recruitments); 66% of recruitments are returns to a repo the agent hosted before. Mathis A0: a calibrated decoupling step from the kickoff field in #41 and #51 only. `analysis/confirm.py` is frozen and dry-run on stand-ins, not run. Card and predictions written 2026-10-04 before any outcome statistic; amendments A0–A2 dated below.
**Fields:** stat mech, dynamics (replicator kinetics), sociophysics (herding, preferential attachment)
**Literature:** [OoLEN 2026 review, part 2](../../literature/oolen-2026-origins-of-life-review-part2-theory.md) (ẋ = c x^p: p = ½ parabolic and coexisting, p = 1 exponential, p > 1 hyperbolic and winner-take-all); [Kolchinsky 2025](../../literature/kolchinsky-2025-thermodynamics-darwinian-selection-replicators.md) (first-order class, formation excluded); [Kolchinsky 2024](../../literature/kolchinsky-2024-dissipation-does-not-bound-replicator-rates.md).
**Definitions used** (`physics-models/DEFINITIONS.md`): *Regime*; *Population N(t)*; *Agent state (categorical, project, work ledger)* (H11 round-1b variant, H06 carry-forward); *Exposure (turn read-out)* via the DQ1 ledger; *call clock* (H40). New named variants (proposed, defined in H77's card and used identically here): **host (work ledger, call-clock expiry)**, **recruitment / birth / departure / expiry**, **swarm call clock**, plus **growth order p** and **cross-lab growth order p_x** (below).
**From:** HH326 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` ("From the thermodynamics and origins-of-life notes") · **Models:** `physics-models/05-replicator-dissipation/` (primary), `physics-models/06-neutral-cooperative-dynamics/` (neutral null, p = 1)
**Sibling:** H77 (selection-resolution bound) shares the scheme (`infra/shared/replicator_hosts.py`); H77's step 1 uses this card's p.

## Source HH (verbatim from the HH list)
Replicator growth order separates herding from division of labor. Fit ṅ_j = c n_j^p to contributors or work commits per repo on the per-call clock. Condition on kickoff naming (H54) and on adoptions made before the link is read (H28 blind window).
  - *Prediction:* p = 1.2–1.5 (hyperbolic, winner-take-all) in H11's shared-artifact herding weeks; p ≤ 0.7 (parabolic, coexistence) in own-artifact weeks.
  - *Kill:* p ≈ 1 everywhere, so growth is plain exponential with no interaction.
  - *Models:* 05, 06 · *Builds on:* H11, H53, H28 · *Literature:* OoLEN 2026

## Question
How does a repo's recruitment flux scale with its current number of hosts, measured on the swarm call clock and with field-made adoptions removed? Superlinear (p > 1) would make herding a hyperbolic, winner-take-all growth law; sublinear (p < 1) would make own-artifact weeks a parabolic regime where repos coexist.

## Model
**From:** `physics-models/05-replicator-dissipation/` (replicator kinetics); `physics-models/06-neutral-cooperative-dynamics/` (neutral copying gives p = 1).

**H78 variant: mass-action replicator with a formation term, on the swarm call clock.**
dn_j^+/dτ = κ_j + c · (C^free/C) · n_j^p, with τ the swarm call count, C^free the calls by agents not hosting j, κ_j formation (births, field-made joins).
- **p = 1:** each host recruits at a constant rate (exponential; neutral copying, Hubbell limit; Kolchinsky's first-order class).
- **p > 1:** hosts recruit more per capita when the repo is big (conformist; hyperbolic growth; one repo takes all).
- **p < 1:** per-capita recruitment falls with size (parabolic; template-inhibited; NCD's rare-species advantage; coexistence).
- **p ≈ 0 with κ > 0:** growth does not depend on n (a field forms hosts directly).

**Estimator (primary, fixed now).** Per (repo j, call-clock bin b) with n_jb ≥ 1: R_jb ~ Poisson(μ_jb), log μ_jb = log C^free_jb + α + p · log n_jb, fitted by maximum likelihood, quasi-Poisson SE. R counts **formation-free recruitments**: not a birth, not into a kickoff-named repo, not in the H28 blind window. Repos named by the kickoff enter as a separate stratum.
**Variants:** (v1) all recruitments; (v2) read-only (class *read* or *known*); (v3) repo fixed effects (within-repo identification, removes fitness heterogeneity); (v4) conditional-logit choice form (bin fixed effects: which repo a recruit picks given current n; absorbs the swarm-wide switching rate); (v5) cumulative contributors as n (HH326's "contributors"); (v6) wall-clock 30-min bins (H40 contrast); (v7) cross-lab order p_x, using only hosts of a different lab than the recruit as n, with same-lab hosts as a control (shared model priors).

## Data scheme (`scheme/`)
Identical to H77's (same shared builder, same parameters): `scheme/build.py` calls `infra/shared/replicator_hosts.py` and writes `data/processed/H78-replicator-growth-order/G<NN>/`.
- **Inputs:** DQ4 `work_commits` (default work filter), DQ1 `call_windows` + `context_ledger_items`, `artifact_mentions` + `project_map`, `chat_core`, `roster` (lab), `period_units`, `calendar`, H54's kickoff-naming rule (text in memory only).
- **Transform:** host labels (W = 30 modal work repo, carry-forward, expiry after E own calls: E = 300 as first written, E = 100 since A1); events (recruitment, birth, switch-out, expiry) with impostor tags (known / read / blind / none; named); swarm call-clock bins (B = 200); per (repo, bin): n, recruitments by class, free and host calls, lab-split host counts.
- **Output:** `G<NN>/bins.parquet`, `events.parquet`, `repos.parquet` (repo names hashed), `synthetic/`, `results/`, `_provenance.json`.
- **Regimes covered:** #31, #33 (I/II); #39–#44, #51 (III).
- **Unit of analysis:** goal period split at `period_units`; p per unit where testable, period p by random-effects partial pooling over units (exception (d)), reported next to the per-unit values.

## Observables
1. **p̂** (primary estimator) per unit and period, with 95% CI.
2. p̂ under variants v1–v7; the change from removing impostors (v1 − primary).
3. Formation share: births + named + blind recruitments over all arrivals.
4. Herding-vs-own contrast Δp = mean p̂(herding) − mean p̂(own), random-effects over periods.

## Null / baseline
- **Neutral copying (H06/Hubbell limit):** p = 1. The kill is p ≈ 1 everywhere.
- **Synthetic recovery** on each period's real call schedule: planted p ∈ {0.5, 1, 1.5} with repo fitness heterogeneity, formation and expiry; the same label builder and estimator. Bias and coverage at real counts decide whether the primary estimator stands (an amendment before real data if it does not).
- **Field-only world:** p = 0 with κ > 0 (all growth formed by a field); the estimator must return p̂ ≈ 0 there.

## Rivals and impostors
- **Kickoff field (H54):** named repos are formed, not copied (separate stratum).
- **In-flight convergence (H28 blind window):** excluded from the primary R.
- **Shared model priors:** v7 cross-lab order.
- **Scheduler (H40):** the swarm call clock; v6 shows what wall-clock bins would give.
- **Fitness heterogeneity (preferential attachment vs fitness):** big repos may be big because they are attractive, which inflates pooled p. v3 (repo FE) removes it; the synthetic measures the size of both biases.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** neutral copying (p = 1), field formation (p = 0), conformist herding (p > 1).
**Locked holdout used for confirmation:** targets #46, #47, #50 and the #51 tail (51m); #45, #48, #49 reported, not scored; frozen in `analysis/confirm.py`, not run.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Hosts, recruitments, births, switch-outs and expiries are DQ4 commit labels; impostor tags come from the ledger and H54's rule. Limits: the label expiry E sets the measured flux (A1); H54's name-token rule tags 46–100% of recruitments as field-made, partly because agents name repos after the goal. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Swarm call clock (H40) used; wall-clock bins give the same p (#31 0.73 vs 0.73; #51 2.13 vs 1.94). Stationarity within periods is not tested; #51 units are heterogeneous (τ² = 0.69). |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 0 | The observed p̂ lies inside the neutral (#31, #41) or fitness-spread (#51) synthetic bands in every testable period. |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | The predicted herding/own contrast has the wrong sign (Δp = −1.05). A0 found calibrated decoupling steps in 2/6 replication periods (post hoc null). |
| E interventional | predicts the change across a natural experiment | 0 | G40 (field-made hub): named-stratum p̂ 1.62 [1.10, 2.13], not the predicted formation-like ≤ 0.5. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | At E = 100, p = 1 is recovered (bias −0.02 to +0.21, coverage 0.82–1.0) and p = 1.4 gives 1.44–1.72. p = 0.5 and p = 0 are not separable from 1 when repos differ in fitness (A1, A2). Estimates are stable across E, B and clock variants. |
| G ground truth | agrees with known structure | 1 | The herding repos of #31, #33, #41 and the #40 hub are kickoff-named (H54); #39 has no recruitment at all (H11: all work private). |
| H comparative | beats the named rivals | 0 | Neither the neutral nor the fitness-spread rival is beaten; the conformist reading cannot be separated from fitness spread. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Holdout not run. |

## Prediction
*Written 2026-10-04, before running the analysis on real data.*

**What I had seen when writing this:** as in H77's card (predecessor cards; per-period work-commit, repo and agent counts; repo-name match; calls per agent-day). No host label, recruitment or order statistic computed.

**Periods and roles.** Replication: herding weeks **#31, #33, #41**; own-artifact weeks **#39, #42**; **#51** (units 51a–51l). Natives: **G40** (one hub named by the kickoff in one merged room: field-made growth) and **G44** (assigned #best vs free #rest on the same days).

| ID | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| P1 | p̂ ∈ [1.2, 1.5] (point; CI overlapping the band) in ≥ 2/3 of testable herding weeks | p̂ < 1.2 with CI below 1.2, in ≥ 2 of them | 0.25 |
| P2 | p̂ ≤ 0.7 in ≥ 2/3 of testable own-artifact points | p̂ > 0.7 with CI above 0.7 in ≥ 2 | 0.30 |
| P3 | Δp(herding − own) > 0, 95% CI above 0 | CI includes 0 or Δp < 0 | 0.35 |
| Kill | (HH326) every testable period has a CI containing 1 and the random-effects pooled |p̂ − 1| < 0.2 | — | (P(kill) 0.35) |
| P4 (impostors) | removing blind and named recruitments moves p̂ by < 0.2 in ≥ 2/3 of herding weeks (they are rare in commit data) | larger shifts | 0.50 |
| P5 (priors) | cross-lab p̂_x within 0.3 of p̂ in herding weeks | |p̂_x − p̂| ≥ 0.3 with p̂_x nearer 1 | 0.50 |
| P6 (fitness confound) | the repo-FE p̂ (v3) is lower than the pooled p̂ in herding weeks | v3 ≥ pooled | 0.60 |
| P7 (synthetic, axis F) | primary estimator |bias| ≤ 0.15 and 95% coverage ≥ 0.85 for p ∈ {0.5, 1, 1.5} at real counts; p̂ ≈ 0 (≤ 0.3) in a field-only world | larger bias or under-coverage | 0.45 |

Per-period predictions are in each `goalperiod-subhypotheses/G<NN>/README.md`, written before running that period.

**Amendment A0 (2026-10-04, at the coordinator's request; written after the predictions above and before any real-data statistic): Mathis et al. 2017 secondary test** ([note](../../literature/mathis-2017-emergence-of-life-first-order-transition.md)). Selection on replicators may switch on in a step, like a first-order transition. Operationalized with this card's data only (no topic clusters of commits exist without new labelling, which is out of scope):
- **Order parameter m(τ):** the share of hosted agents whose repo is kickoff-named (H54 rule), per swarm call-clock bin. It is the alignment of allocation with the kickoff field, a one-bit proxy for I(project; kickoff field). I also report I(label; named) in bits per bin.
- **Step vs ramp:** per period, fit (a) a single change-point step in m and (b) an exponential relaxation m(t) = m_∞ + (m_0 − m_∞)e^{−t/τ} with τ fixed at H48's 4.5 active h; compare by BIC on bins (Gaussian errors). Step = ΔBIC ≥ 6 for (a).
- **Signatures, if a step exists:** the waiting time to the step on the call clock (across periods: KS test against an exponential, descriptive with ≤ 8 periods); frustrated herds (a repo that reached ≥ 3 hosts and went extinct before the step); nucleus ≠ winner (the first repo with a formation-free recruitment is not the top repo); a birth-rate peak (new repos per 1,000 calls) in the step bin ± 1 bin, ≥ 3× the period median.
- **Predictions (credences):** M1 a step (ΔBIC ≥ 6) in ≥ 1/2 of the replication periods with a named repo: 0.20. M2 nucleus ≠ winner in ≥ 1/2 of herding weeks: 0.40. M3 ≥ 1 frustrated herd before the step in a herding week: 0.45. M4 birth-rate peak at the step in ≥ 1/2 of step periods: 0.30.
- **Kill (Mathis reading):** m decays smoothly, with the τ = 4.5 h ramp preferred (ΔBIC ≤ −2) or no step in every testable period.
- H77 reports M2 and M3 next to its selection statistics (same events).

**Amendment A1 (2026-10-04, after the synthetic validation, before any real-data outcome statistic).** What I had seen: the synthetic runs on the real schedules of #31, #33, #40, #41, #42, #44 (E = 300, 40 replicates per world) and an expiry sweep (E = 100, 50; #31, #33, #41; 20 replicates); the real aggregate event counts at E = 100 (e.g. #31 83 recruitments, #33 55, #41 64, #42 36, #51 299). No real p, σ* or step statistic.
- **Ghost hosts.** At E = 300 an idle agent keeps its label for ~300 of its own calls. Ghost hosts make small repos look unproductive and inflate p̂ (neutral bias +0.2 in #31, +0.32 in #51 with 0% coverage). At E = 100 the neutral bias is 0.00–0.12 with coverage 0.9–1.0, and conformist p = 1.4 is recovered at 1.25–1.66. E = 50 over-corrects σ* (bias +0.7 to +2). **The primary expiry is now E = 100** (in `infra/shared/replicator_hosts.py`); E = 50, 150, 300 and ∞ are variants.
- **Parabolic order is not identifiable from p = 1 when repos differ in fitness.** With fitness spread σ_A = 0.5, a planted p = 0.5 gives p̂ ≈ 0.95–1.02 and a field-only world (p = 0) gives 0.47–0.69. Big repos are big because they are fit, and that mimics autocatalysis. The repo fixed-effects variant (v3) is biased the other way (−0.3 to −0.6) and is dropped as a test; it is reported only. **Consequence:** P2 (p̂ ≤ 0.7) and the kill (p ≈ 1 everywhere) cannot separate "no interaction" from "sublinear growth plus fitness heterogeneity". Only the superlinear direction (P1, P3) is identified. P2 and the kill are still scored as written, with this caveat attached.
- **New variant v8:** first-time recruits only (re-joins of a repo the agent hosted earlier are dropped; H58's return-to-own-artifact effect).
- Not amended: the estimator, the impostor rules, the bands, the periods and the testability rule.

**Testability rule (fixed now).** p needs ≥ 15 formation-free recruitments into repos with n ≥ 1 and ≥ 2 distinct values of n among bins with recruitments; else *descriptive*.

**Amendment A2 (2026-10-04, post hoc, after the first real run; disclosed).** Three additions, none changing the primary estimator or any verdict rule:
- **Fitness-spread null worlds** (p = 1, repo fitness A ~ lognormal(0, σ_A), σ_A = 0.5, 1.0, 1.5) on each period's schedule. Added after seeing #51's p̂ = 1.94, because the planned worlds did not isolate fitness spread without interaction.
- **Touch-based impostor class.** The pre-registered tags classify 98% of recruitments as *known* (agents touch a repo in their own commands before committing), which leaves the H28 blind window unobservable. A second class is computed relative to the agent's first touch of the repo: read / blind / return / self. Variant v9 drops touch-blind recruitments.
- **AR(1) surrogate null for the A0 step test.** The iid-error BIC comparison is anti-conservative on autocorrelated bins (lag-1 ρ 0.66–0.96); 200 surrogates of the ramp fit plus AR(1) residuals calibrate ΔBIC.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication (herding) | failed | p̂ 0.73 [−0.08, 1.54], 36 recruitments; all recruitments 1.54; fitness-spread null 1.41–2.04 |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication (herding) | descriptive | 9 formation-free recruitments (46/55 into named repos); p̂ 1.41 [0.40, 2.42] |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication (herding) | failed | p̂ 1.05 [0.00, 2.09], 19; calibrated A0 step 0.85 → 0.44 at 8.6 h |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication (own) | descriptive | 0 recruitments, 67 births: formation only |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication (own) | descriptive | 2 formation-free recruitments; 34/36 into named repos |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication (own) | failed | p̂ 1.94 [1.22, 2.67], 271, 8 units; fitness-spread null 1.54–2.73; FE 0.18 |
| [G40](goalperiod-subhypotheses/G40/README.md) | native | mixed | 48/48 recruitments into the named hub; named-stratum p̂ 1.62 [1.10, 2.13]; step up at 4.5 h |
| [G44](goalperiod-subhypotheses/G44/README.md) | native | descriptive | 8 formation-free recruitments (#best arm 0); 80 births |

## Results
*Exploratory round 1, 2026-10-04, non-holdout days only.*
- **Code:** shared `infra/shared/replicator_hosts.py` (labels, events, bins), `replicator_fit.py` (estimators), `replicator_sim.py` (synthetic worlds); `scheme/build.py`; `analysis/run.py` (per period, `--period`, `--arm`), `synthetic.py`, `synth_summary.py`, `figures.py`, `estimates_rows.py`, `confirm.py` (frozen, dry-run only).
- **Data:** `data/processed/H78-replicator-growth-order/` (`G<NN>/` tables, `results/G<NN>.json`, `synthetic/` runs and summaries, `confirm/confirm_dryrun.json`, `_provenance.json`; 5 MB).
- **Figures:** [`figures/summary_obs.pdf`](figures/summary_obs.pdf) (p̂ per period vs the bands and the fitness-spread null), [`figures/summary_synth.pdf`](figures/summary_synth.pdf) (recovery by world).
- **Estimates:** 25 rows in `per_period_estimates` (`replicator_growth_order_p`, `replicator_formation_share`).

**Outcome vs prediction**

| Prediction | Outcome | Verdict |
| --- | --- | --- |
| P1 p̂ ∈ [1.2, 1.5] in ≥ 2/3 herding weeks | #31 0.73, #41 1.05; #33 untestable (9) | **failed** (no CI excludes the band) |
| P2 p̂ ≤ 0.7 in ≥ 2/3 own points | #51 1.94 [1.22, 2.67]; #39, #42 untestable | **failed** |
| P3 Δp(herding − own) > 0 | −1.05 (0.89 vs 1.94) | **failed** (wrong sign) |
| Kill: CIs contain 1 everywhere and pooled |p̂ − 1| < 0.2 | #51 CI excludes 1 | not met by the letter; but p = 1 with fitness spread reproduces #51 (A2) |
| P4 impostor removal moves p̂ < 0.2 | #31 0.81, #33 0.33, #41 0.05 | **failed** (named repos carry the herding) |
| P5 cross-lab p̂_x within 0.3 | #31 0.42 vs 0.73, #41 −0.72 vs 1.05, #51 2.43 vs 1.94 | **failed** (wide CIs; #51 cross-lab is *higher*) |
| P6 repo-FE p̂ below pooled | #31 0.33 < 0.73; #41 −0.42 < 1.05; #51 0.18 < 1.94 | supported, but FE is biased −0.3 to −0.9 by construction (synthetic) |
| P7 synthetic recovery for p ∈ {0.5, 1, 1.5}, field ≤ 0.3 | p = 1 and 1.4 recovered; 0.5 → 0.88–1.16; field 0 → 0.5–1.1 | **failed** (parabolic and field not identifiable) |
| A0 M1 step in ≥ 1/2 periods with a named repo | ΔBIC ≥ 6 in 5/6, but calibrated (AR(1) surrogates) in 2/6 (#41, #51) | **failed** after calibration |
| A0 M4 new-repo burst at the step | 3.9× the period mean in #41 and #51 (median baseline is 0) | supported (2/2) |
| A0 kill (smooth ramp everywhere) | calibrated steps in #41, #51, #40, #44 | not met |

**Synthesis.**
1. **Order is not identified between repos.** With first-order copying, repos that differ in attractiveness produce p̂ well above 1 (σ_A = 0.5: 1.3–1.5; σ_A = 1.0: 1.2–2.7). A sublinear order with the same spread reads as ≈ 1. Within-repo (fixed-effects) estimates fix the confound but are biased low by 0.3–0.9. At 20–300 recruitments per period no estimator here separates p = 0.5, 1 and 1.4 once fitness varies.
2. **Herding is a field-named repo, not a growth law.** In #31, #33, #41 and #40 the top repo is the kickoff-named one, and it receives *no* formation-free recruitment: every arrival is in the named stratum. Removing named repos removes the herding. What is left recruits at p̂ ≈ 0.7–1.05.
3. **Own-artifact #51 is superlinear between repos** (1.94, stable across E, B, clock, choice form and cross-lab). The repos that recruit are the few shared ones; 72% of #51 recruitments are returns to a repo the agent hosted before (H58's return to the own artifact).
4. **Impostors.** The H28 blind window is negligible at commit level: 4 of 601 recruitments (0.7%). Read-mediated recruitment is 28% and "self" (no link involved) 5%. Kickoff naming is the dominant impostor, and it is entangled with agents naming repos after the goal.
5. **Mathis A0.** Allocation decouples from the kickoff field in a calibrated step in #41 (8.6 active h) and #51 (38 h), with a 3.9× new-repo burst; in #40 and #44 the field share steps *up* (4.5 h, 10.2 h). #31 and #33 decouple but not beyond the AR(1) null. The #40 step time equals H48's 4.5-h settling time.

**Claim that stands.** On DQ4 commit labels the replicator growth order of repos is not identifiable: first-order copying with repo fitness spread reproduces every observed p̂ (0.7–1.9), herding concentrates on kickoff-named repos rather than on a superlinear law, and own-artifact #51 is superlinear between repos for the same reason.

## Confirmatory design (frozen 2026-10-04 in `analysis/confirm.py`; dry-run on stand-ins only, NOT RUN)
Targets #46, #47, #50 and the #51 tail (51m); #45, #48, #49 reported, not scored. C1: #51-tail p̂ CI above 1. C2: #51-tail p̂ inside the fitness-spread band (σ_A 0.5–1.0, p = 1, simulated on the tail's schedule). C3: formation share ≥ 0.6 in ≥ 2/3 of targets. C4: touch-blind recruitments ≤ 5% pooled. C5: returns ≥ 40% of #51-tail recruitments. C6: a calibrated A0 step in ≥ 1/2 of testable targets. Guard: `--confirm --i-understand-this-uses-the-locked-holdout`, a committed H78 folder, `holdout_ledger.check()` (families `project_potts`, `artifact_lineage`). Dry run (#38, units 51h–51l): C1, C3–C6 pass, C2 fails (stand-in p̂ 2.75 above the band's 2.33): a pipeline check, not evidence. Reuse: H11, H53, H58 plan #46–#51 tail uses with other statistics; disclose per the reuse policy.

## Round 2 redirects (proposed by the round-1 agent, 2026-10-04)
- **H78-R1. Separate order from fitness.** Use within-repo designs with an unbiased dynamic-panel estimator (first-differenced recruitment on lagged n, or a conditional likelihood), validated on the fitness worlds, or repo covariates (README size, recent commits; HH301) as fitness proxies.
- **H78-R2. Model returns explicitly.** 66% of recruitments are returns. A replicator with an agent-specific memory term (agent + own artifact, H58) is the right null for #51.
- **H78-R3. A better naming instrument.** Separate "the kickoff names the repo" from "the agents named the repo after the goal" (repo creation time vs kickoff; first namer).

## Notes
- 2026-10-04: round-1 agent (H77 + H78 together). Card written before any statistic on host labels.
- 2026-10-04: A0 (Mathis) added at the coordinator's request before any real-data statistic; A1 after the synthetic; A2 post hoc (disclosed above).
- Compute: ≤ 2 threads, no sub-agents, no LLM labels. Synthetic: 40 replicates per world for the 5-day periods, 10 for #51 (8 for the A2 fitness worlds).
