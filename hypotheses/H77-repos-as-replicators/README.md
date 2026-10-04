# H77: Repos as replicators: the selection-resolution bound

**Status:** exploratory round 1 done (2026-10-04, non-holdout only). **Failed as posed: σ* does not separate herding from own-artifact weeks, and the selection-resolution bound is untestable at village counts.** The top repo's recruitment/departure affinity is σ* = 0.89, 1.58 and 1.00 nats in the herding weeks #31, #33, #41 and 0.55 in #42 (#39 and #51 untestable): the herding − own difference is 0.61 ± 1.23 nats, so HH325's kill condition is met. Every value lies inside the 95% band of a neutral copying world run on the same call schedule. σ* is a measurement convention, not a state variable: its sign flips with the host-expiry rule (#41: 3.22 at E = 50, −0.51 at E = 300). In every herding week the top repo is kickoff-named and receives no formation-free recruitment, so the rare-phase fitness of the winner is zero and the bound cannot be evaluated; the permutation test has size 0 and power 0 in the synthetic. Secondary: the uncopying order q is < 1 in herding weeks (#31 0.59 [0.24, 0.95]) and > 1 in own-artifact #51 (1.46 [1.22, 1.70]). `analysis/confirm.py` is frozen and dry-run on stand-ins, not run. Card and predictions written 2026-10-04 before any outcome statistic; amendments A0–A1 dated below.
**Fields:** thermodynamics (stochastic, nonequilibrium), stat mech, sociophysics (herding)
**Literature:** [Kolchinsky 2025, thermodynamics of Darwinian selection](../../literature/kolchinsky-2025-thermodynamics-darwinian-selection-replicators.md) (affinity σ, fitness f, the bound s ≥ e^{−σ*}); [Kolchinsky 2024, dissipation does not bound replicator rates](../../literature/kolchinsky-2024-dissipation-does-not-bound-replicator-rates.md) (uncopying vs degradation; order of decay); [OoLEN 2026 review, part 2](../../literature/oolen-2026-origins-of-life-review-part2-theory.md) (growth order ẋ = c x^p, coexistence vs selection).
**Definitions used** (`physics-models/DEFINITIONS.md`): *Regime*; *Population N(t)*; *Agent state (categorical, project, work ledger)* (H11 round-1b variant, with H06's carry-forward); *Exposure (turn read-out)* via the DQ1 context ledger; *call clock* (H40 variant, here summed over the swarm). New named variants proposed (not edited into DEFINITIONS.md): **host (work ledger, call-clock expiry)**, **recruitment / departure (uncopying) / expiry (dilution) / birth (formation)**, **swarm call clock**, **operational affinity σ (recruitment/departure)**, **rare-phase fitness f**, all defined under Data scheme and Observables.
**From:** HH325 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` ("From the thermodynamics and origins-of-life notes") · **Models:** `physics-models/05-replicator-dissipation/` (primary), `physics-models/06-neutral-cooperative-dynamics/` (neutral null)
**Sibling:** H78 (growth order p) shares the scheme (`infra/shared/replicator_hosts.py`) and the step-1 order estimate.

## Source HH (verbatim from the HH list)
Repos as replicators: recruitment order and the selection-resolution bound.
  - First, fit the order of recruitment: does per-host recruitment rise with project share (conformist, H53) or is it first-order (Kolchinsky's class)?
  - Then test the resolution bound: rivals that die have fitness gap s ≥ e^{−σ*}, with σ* = ln(recruitments/departures) for the top project on its plateau.
  - *Predictions:* σ* ≥ 1 nat in herding weeks and ≤ 0.3 in fragmented free weeks. At ≤ 0.3, H06's near-neutral coexistence is a near-equilibrium regime: selection can't resolve small differences, so everything coexists.
  - *Kill:* σ* is the same in herding and free weeks.
  - *Models:* 05, 06 · *Builds on:* H06, H11, H53, HH301 · *Literature:* Kolchinsky 2025

## Question
Treat each repo as a replicator whose copies are the agents working on it. Is the top repo's recruitment/departure irreversibility σ* (nats per net copy) high in herding weeks and near zero in own-artifact weeks? And do the rivals that die have a fitness gap at least e^{−σ*}, as Kolchinsky's selection-resolution bound requires?

## Model
**From:** `physics-models/05-replicator-dissipation/` with Kolchinsky (2025)'s flow-reactor selection theory; `physics-models/06-neutral-cooperative-dynamics/` supplies the neutral null.

**Mapping (H77 variant).**
- **Replicator X_j:** repo j. **Copy number n_j(t):** the number of agents whose current host label is j.
- **Substrate A:** agents that do not host j. A copy step is a recruitment (A → X_j, catalysed by the n_j hosts).
- **Reverse step (uncopying), flux J⁻_j:** a host switches its label from j to another repo. This is the reaction run backwards (a copy returns to the pool by being re-used elsewhere).
- **Dilution / degradation ϕ:** a host's label expires (no commit to j for E of its own calls; E = 300 as first written, E = 100 since A1), or the agent leaves the roster. This loss does not depend on j (X → W).
- **Formation (excluded by the theory):** a birth (the first host of a repo), a recruitment into a repo the kickoff names (H54 field), and a recruitment made after a link to j was posted but before the recruit could read it (H28 blind window; in-flight convergence).
- **Clock:** the swarm call clock τ, i.e. the count of model calls by present agents (H40: agents update per call, not per minute). All rates are per 1,000 swarm calls.

**Quantities (Kolchinsky 2025 in village units).**
- Operational affinity per copy of the top repo T on its plateau: σ* = ln(J⁺_T / J⁻_T), from counts of recruitments J⁺ and switch-outs J⁻ in the plateau bins.
- Rare-phase fitness f_j = recruitments per host per 1,000 free calls while n_j ≤ 2 (invasion growth rate).
- Selection coefficient of rival k: s_k = 1 − f_k / f_T.
- **Bound (selection resolution):** if T persists and k goes extinct, then σ* ≥ −ln s_k, i.e. s_k ≥ e^{−σ*}.
- **Step 1 (order of recruitment):** J⁺_j ∝ C^free · n_j^p; elasticity e = p − 1 of per-host recruitment. e = 0 is Kolchinsky's first-order class. Estimated with H78's estimator (same code, same data).
- **Order of uncopying (Kolchinsky 2024):** J⁻_j ∝ C^host · n_j^{q−1}. q = 1 is degradation-like; q = 2 is chemical uncopying (crowding pushes hosts out).

**What the model predicts.** High σ* means copying is far from reversible, so selection resolves small fitness gaps and one repo wins (herding). σ* near 0 means near-equilibrium, where small gaps are unresolved and repos coexist (H06's fragmentation). The deterministic theory has no fluctuations; at n ≤ 30 drift is large, so every comparison is against a simulated finite-N null.

## Data scheme (`scheme/`)
`scheme/build.py` calls the shared builder `infra/shared/replicator_hosts.py` (shared with H78) and writes `data/processed/H77-repos-as-replicators/`.
- **Inputs:** DQ4 `work_commits` (default work filter `canonical & ~imported & author_kind == agent & ~automated`, author time `t`); DQ1 `call_windows` (`agent`, `t_call`, `turn_id`) and `context_ledger_items` (`turn_id`, `message_id`); `artifact_mentions` (strict chat links `source = chat`, `how ∈ {url, bare}`; strict self-mentions `how ∈ {url, output, bare}`) through `project_states.project_map`; `chat_core` (link senders and times); `roster` (lab; the Claude Code agent is excluded, as in the ledger); `period_units`; `calendar`; H54's kickoff-naming rule (kickoff messages from `goal_fields.kickoff_messages`, goal text from `common.load_goals`, H54's `name_tokens`/`tok_match`, text in memory only).
- **Host label (host (work ledger, call-clock expiry)):** per agent and W = 30-min window (from the day's `win_start`), the repo with the most work commits; ties go to the most recent commit. The label carries forward over windows without commits (H06). It **expires** after E of the agent's own calls with no commit to the labelled repo: E = 300 as first written, **E = 100 since amendment A1** (variants E = 50, 150, 300, ∞). Roster leave also ends the label.
- **Events:** a label change i: j → k at the time of i's first commit to k in that window gives a departure from j (switch-out) and an arrival into k. The arrival is a **recruitment** if n_k ≥ 1 just before, else a **birth**. An expiry is a dilution event.
- **Recruitment class** (impostor tags): *known* (i mentioned k or hosted it before), *read* (a chat link to k from another sender entered one of i's calls before the recruitment, per the ledger), *blind* (a link to k was posted before the recruitment but i had not read it: H28's blind window), *none* (no link posted). *named*: k is kickoff-named (H54 rule).
- **Clock bins:** the period's non-holdout calls sorted by `t_call`, cut into bins of B = 200 swarm calls (variant B = 100, 400; wall-clock 30-min bins as the H40 contrast). Per (repo, bin): n at bin start, recruitments by class, births, switch-outs, expiries, free calls C^free (calls by non-hosts of j), host calls C^host.
- **Output:** `data/processed/H77-repos-as-replicators/G<NN>/` (`events.parquet`, `bins.parquet`, `repos.parquet`: codes only, repo names hashed), plus `synthetic/`, `results/`, `_provenance.json`. No message text.
- **Regimes covered:** #31, #33 (regime I/II), #39–#44 and #51 (regime III). Each period sits inside one regime.
- **Unit of analysis:** the goal period, split at `period_units` step changes. The host state runs through the whole period (a repo's trajectory crosses roster joins), and every statistic is computed per unit. Period values use random-effects partial pooling over units (exception (d): one-day units such as #31a–d have too few events), reported next to per-unit values.

## Observables
1. **σ\*** of the top repo T (largest call-clock-averaged n over the period). Plateau = bins after n_T first reaches ⌈0.8·max n_T⌉ in which n_T ≥ 0.5·max n_T. σ* = ln[(J⁺ + ½)/(J⁻ + ½)] with a parametric CI from the Poisson log-ratio variance. Testable if J⁺ + J⁻ ≥ 8. Variants: formation-free J⁺ (no blind, no named), E = 150 / ∞, B = 100 / 400, and σ_all with dilution counted as loss (≈ 0 on a plateau by flux balance; a consistency check).
2. **Resolution test (literature D3).** Testable rivals: repos k ≠ T with ≥ 1 recruitment while n_k ≤ 2. Extinct: n_k = 0 over the last 20% of the period's bins while n_T ≥ 1. Statistic: the fraction of testable extinct rivals with ŝ_k ≥ e^{−σ̂*}. Null: f permuted among all testable repos of the period (999 draws).
3. **Order of recruitment, step 1:** e = p̂ − 1 from H78's primary estimator.
4. **Order of uncopying q:** Poisson GLM of switch-outs on log n with offset log C^host (n ≥ 1 bins).
5. **Flux balance on the plateau:** J⁺ − J⁻ − D (D = expiries) vs Δn (a closure check).

## Null / baseline
- **Neutral (H06, Hubbell-type) null:** on each period's real call schedule, agents switch at the period's measured per-call switch rate and choose a repo ∝ n (no fitness differences, s = 0), with births and expiries at the measured rates. Measurement runs through the same label builder. It gives the finite-N distribution of σ*, the size of the D3 test, and q.
- **Kill (HH325):** σ* in herding weeks minus σ* in own-artifact weeks ≤ 0.3 nat, or its CI includes 0.
- **Permutation null** for D3 (fitness labels shuffled within period).

## Rivals and impostors
- **Kickoff field (H54):** a named repo is formed by the field, not copied. Removed by excluding named repos' recruitments from the formation-free variant and by reporting named tops separately.
- **In-flight convergence (H28 blind window, H57):** recruitments made after a link was posted but before it was read. Excluded in the formation-free variant.
- **Shared model priors:** agents of one lab converge on the same repo without copying. Checked through H78's cross-lab order estimate (p from hosts of other labs only); σ* is a count ratio and has no lab term.
- **Scheduler field:** day starts and pauses. Removed by the swarm call clock and by carrying labels over nights (a day start makes no recruitment).
- **Drift:** at n ≤ 30 extinction is stochastic; the neutral null sets the floor.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** neutral copying (model 06, Hubbell limit), conformist copying (H53 share), kickoff field (H54).
**Locked holdout used for confirmation:** targets #46, #47, #50 and the #51 tail (51m); #45, #48, #49 reported, not scored; frozen in `analysis/confirm.py`, not run.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Copies, recruitments, switch-outs (uncopying) and expiries (dilution) are DQ4 commit labels. The split between uncopying and dilution is set by the expiry rule E, which the theory does not fix (A1). |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 0 | The flow-reactor steady state is rare: plateaus are short and #51 has none with flux at E = 100. σ*'s sign depends on E (#31: 1.73 → −0.55 from E = 50 to 300). |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 0 | σ* lies inside the neutral world's 95% band in 6/6 testable periods (the neutral median is 1.71 in #33). |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | The bound is untestable (f_T = 0 in every herding week; 0/7 extinct #51 rivals satisfy it, all fitter than the top). q contrast (< 1 herding, > 1 #51) is post hoc. |
| E interventional | predicts the change across a natural experiment | 0 | NE42: σ*(#40 merge) 1.64 > #41 1.00, as predicted, but inside the neutral band and with every hub arrival field-tagged. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 0 | At E = 100 σ̂* tracks true σ* with bias −1.2 to +0.4 (coverage 0.27–1.0); E = 300 and E = 50 bias it by up to ±2 nats. The resolution test has size 0 and power 0. |
| G ground truth | agrees with known structure | 1 | The herding repo is the kickoff-named one in 7/8 units (H54); #39 shows no copying at all (H11: all work private); #44 #best works in its own repos (H58). |
| H comparative | beats the named rivals | 0 | Neither neutral copying nor the kickoff field is beaten. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Holdout not run. |

## Prediction
*Written 2026-10-04, before running the analysis on real data.*

**What I had seen when writing this:** H06, H11, H53, H58, H54, H28 and H40 cards (round 1 and 1b); per-period counts of DQ4 agent work commits, repos and committing agents for #29–#51 (e.g. #31 1,391 commits / 37 repos / 13 agents; #33 632 / 7; #39 2,232; #41 1,812 / 26; #42 1,615 / 13; #44 1,491 / 52; #51 48,093 / 157); that work_commits repo names match `project_map` names in #31; median calls per agent-day (#31 612, #41 460, #51 678). I had computed no host label, recruitment, departure, σ, fitness or order statistic.

**Periods and roles.**
- Replication (same estimator everywhere): shared-artifact herding weeks **#31, #33, #41** (H11 round 1b: work herds, z_N2 ≥ 2); own-artifact weeks **#39, #42**; and **#51** (own-artifact, private roles; units 51a–51l).
- Natives: **G44** (two arms on the same days: assigned #best vs free #rest) and **NE42** (#39 → #40 → #41: rooms merged into one hub room, then split back).

| ID | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| P1 | σ* ≥ 1 nat in ≥ 2/3 of the testable herding weeks (#31, #33, #41) | σ* < 1 in ≥ 2 of them | 0.40 |
| P2 | σ* ≤ 0.3 in ≥ 2/3 of the testable own-artifact points (#39, #42, #51 pooled over units) | σ* > 0.3 in ≥ 2 of them | 0.35 |
| P3 (kill test) | mean σ*(herding) − mean σ*(own) > 0.3 nat with a 95% CI above 0 | difference ≤ 0.3 or CI includes 0 (HH325's kill) | 0.40 |
| P4 (bound) | pooled over herding weeks, ≥ 90% of testable extinct rivals have ŝ ≥ e^{−σ̂*}, and the fraction beats the fitness-permutation null (p < 0.05) | < 90%, or not above the null | 0.25 |
| P5 (step 1, order) | per-host recruitment rises with n in herding weeks: e = p̂ − 1 ∈ [+0.2, +0.5] (H78's band), and |e| < 0.3 in own-artifact weeks | e ≤ 0 in herding weeks | 0.30 |
| P6 (uncopying order) | switch-outs are first-order: |q̂ − 1| < 0.3 (degradation-like; Kolchinsky 2024's second-order uncopying absent) | q̂ ≥ 1.5 with CI above 1.3 | 0.45 |
| P7 (null) | real σ* in herding weeks lies above the 95th percentile of the neutral null at that period's counts | inside the neutral band | 0.35 |
| P8 (synthetic, axis F) | at real counts the σ* estimator has |bias| ≤ 0.3 nat for a planted σ* ∈ {0, 1, 2}, and the D3 test has size ≤ 0.10 under the neutral null | larger bias or size | 0.50 |

Per-period predictions are in each `goalperiod-subhypotheses/G<NN>/README.md` (and `NE42/`), written before running that period.

**Amendment A0 (2026-10-04, at the coordinator's request; written after the predictions above and before any real-data statistic): Mathis et al. 2017** ([note](../../literature/mathis-2017-emergence-of-life-first-order-transition.md)). The step-decoupling test (order parameter: share of hosts on kickoff-named repos; step vs a 4.5-h ramp) is specified and run in H78's card (A0). H77 reports the two selection signatures on its own events: **M2** nucleus ≠ winner (the first repo with a formation-free recruitment is not the top repo T) in ≥ 1/2 of herding weeks (credence 0.40); **M3** ≥ 1 frustrated herd (a repo that reached ≥ 3 hosts and then went extinct while T persisted) in a herding week (0.45). Read together with the bound: a frustrated herd that died with ŝ < e^{−σ*} violates the deterministic bound and counts as drift or field.

**Amendment A1 (2026-10-04, after the synthetic validation, before any real-data outcome statistic).** What I had seen: as in H78's A1 (synthetic runs on the real schedules; expiry sweep; real aggregate counts at E = 100). No real σ*, fitness or bound statistic.
- **The label expiry sets σ̂*.** At E = 300 a host that goes idle and later joins another repo is measured as a switch-out (uncopying), so dilution leaks into J⁻ and σ̂* is biased low (−0.3 to −2.5; conformist coverage 0–0.36). At E = 100 the bias is −0.35 to +0.13 in #31 and #41 (coverage 0.85–1.0); #33 stays noisy (+0.6 at 24 recruitments). E = 50 biases σ̂* up by 0.7–2. **Primary E = 100**; E = 50, 150, 300, ∞ are variants.
- **The resolution test (P4) has no power at village counts.** Under the neutral world the permutation p-value is never < 0.05 (size 0), and under the conformist world it also never is (power 0). The fraction ≥ 0.9 occurs in 42% of neutral #33 runs, so the 90% criterion alone is not specific. P4 is reported as written but marked *not identifiable*; it cannot support or refute the bound.
- **The neutral null band for σ*** is now the E = 100 neutral world on each period's schedule (95th percentile; P7).
- Not amended: σ*'s definition, the plateau rule, periods, testability.

**Testability rule (fixed now).** σ* needs J⁺ + J⁻ ≥ 8 on the plateau; D3 needs ≥ 3 testable extinct rivals; q needs ≥ 15 switch-outs. Below that, the period is *descriptive*.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication (herding) | failed | σ* 0.89 [−0.36, 2.13] (J⁺ 8, J⁻ 3); neutral 95th 1.10; q 0.59 [0.24, 0.95]; 3 frustrated herds |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication (herding) | mixed | σ* 1.58 [0.73, 2.42] (31, 6); neutral median 1.71, 95th 3.43 |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication (herding) | failed | σ* 1.00 [−0.23, 2.22] (9, 3); neutral 95th 1.96 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication (own) | descriptive | 0 recruitments, 67 births |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication (own) | failed | σ* 0.55 [−0.50, 1.60] (9, 5); q 1.90 [1.04, 2.76] |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication (own) | descriptive | top plateau J⁺ 0, J⁻ 4 (untestable); q 1.46 [1.22, 1.70]; 0/7 extinct rivals satisfy the bound |
| [G44](goalperiod-subhypotheses/G44/README.md) | native | descriptive | both arms untestable (J⁺ + J⁻ = 6 and 4) |
| [NE42](goalperiod-subhypotheses/NE42/README.md) | native | supported | σ*(#40) 1.64 [0.80, 2.48] > #41 1.00; 49/49 hub arrivals field-tagged; no extinct rival |

## Results
*Exploratory round 1, 2026-10-04, non-holdout days only.*
- **Code:** shared `infra/shared/replicator_hosts.py`, `replicator_fit.py`, `replicator_sim.py` (with H78); `scheme/build.py`; `analysis/run.py` (per period, `--period`, `--arm`), `figures.py`, `estimates_rows.py`, `confirm.py` (frozen, dry-run only). Synthetic runs come from H78's `analysis/synthetic.py` (same worlds; σ* columns written to this data folder).
- **Data:** `data/processed/H77-repos-as-replicators/` (`G<NN>/` tables, `results/`, `synthetic/`, `confirm/confirm_dryrun.json`, `_provenance.json`; 5 MB).
- **Figures:** [`figures/summary_obs.pdf`](figures/summary_obs.pdf) (σ̂* per period with the neutral 95th percentile), [`figures/summary_synth.pdf`](figures/summary_synth.pdf) (measured vs true σ* in the synthetic worlds).
- **Estimates:** 19 rows in `per_period_estimates` (`replicator_sigma_star`, `replicator_uncopying_order_q`).

**Outcome vs prediction**

| Prediction | Outcome | Verdict |
| --- | --- | --- |
| P1 σ* ≥ 1 in ≥ 2/3 herding weeks | #31 0.89, #33 1.58, #41 0.998 | **failed** (1/3) |
| P2 σ* ≤ 0.3 in ≥ 2/3 own points | #42 0.55; #39, #51 untestable | **failed** (0/1 testable) |
| P3 Δσ* (herding − own) > 0.3, CI > 0 | 0.61 ± 1.23 | **failed: HH325's kill condition is met** |
| P4 resolution bound (≥ 90%, beats permutation) | untestable in herding weeks (winner's rare-phase fitness 0); #51 0/7 | **not identifiable** (A1: size 0, power 0) |
| P5 step-1 order e = p − 1 ∈ [0.2, 0.5] herding | e = −0.27 (#31), +0.05 (#41); #51 +0.94 | **failed** (see H78: order not identified) |
| P6 |q − 1| < 0.3 | #31 0.59, #33 0.09, #41 0.27, #42 1.90, #51 1.46, #40 0.36 | **failed** (0/6 within; 1/7 with #44 at 1.12; neutral-world q̂ 0.78–0.96) |
| P7 real σ* above the neutral 95th pct (herding) | 0/3 | **failed** |
| P8 synthetic |bias| ≤ 0.3, D3 size ≤ 0.1 | bias −1.2 to +0.4; size 0 but power 0 | **failed** (mixed by the letter) |
| A0 M2 nucleus ≠ winner (≥ 1/2 herding) | 3/3, but mechanical (the winner is named, the nucleus formation-free) | supported, uninformative |
| A0 M3 a frustrated herd in a herding week | #31: 3 repos reached ≥ 3 hosts and died (no calibrated step in #31) | supported by the letter |

**Synthesis.**
1. **σ* measures the bookkeeping of loss, not selection.** On a plateau J⁺ ≈ J⁻ + dilution. Whether a host who stops committing and later works elsewhere counts as uncopying (J⁻) or dilution depends on the expiry rule, so σ* moves by 2.0–3.7 nats between E = 50 and E = 300 in 4/5 testable periods and changes sign in 2/5 (#31, #41). The theory's σ is defined by microscopic reversibility, which commit logs do not resolve.
2. **The neutral world produces the same σ*.** Copying ∝ n with no fitness differences, run on each period's real call schedule, gives σ* up to 1.1–3.4 nats (95th pct). No observed value exceeds it.
3. **Herding is field-named.** The top repo is kickoff-named in 7/8 units, and none of its arrivals is formation-free. In Kolchinsky's terms the winner is *formed* by the field, which the theory excludes; its rare-phase fitness from copying is zero, so s and the bound are undefined.
4. **#51 rivals are fitter than the winner.** All 7 extinct testable rivals have higher rare-phase fitness than the top repo (ŝ < 0). The top repo in a private-role era wins by persistence of its own host, not by recruitment.
5. **Order of uncopying (Kolchinsky 2024).** Per-host switch-out rate falls with n in herding weeks (q < 1: big shared repos hold hosts) and rises with n in #51 and #42 (q > 1: crowded repos shed hosts, as chemical uncopying would). The neutral synthetic gives q̂ ≈ 0.8–0.96, so only #51's q > 1 is clearly beyond measurement bias. Post hoc.

**Claim that stands.** On DQ4 commit labels, the recruitment/departure affinity σ* of the top repo is a measurement convention (its size, and in 2/5 periods its sign, follows the host-expiry rule), lies inside a neutral copying null in every testable period, and does not separate herding from own-artifact weeks; the selection-resolution bound cannot be tested because the winning repos are formed by the kickoff field.

## Confirmatory design (frozen 2026-10-04 in `analysis/confirm.py`; dry-run on stand-ins only, NOT RUN)
Targets #46, #47, #50 and the #51 tail (51m); #45, #48, #49 reported, not scored. C1: σ*(E = 50) − σ*(E = 300) ≥ 1 nat in ≥ 1/2 of testable targets. C2: σ*(E = 100) at or below the neutral world's 95th percentile on the target's own schedule in ≥ 2/3. C3: the top repo is kickoff-named in ≥ 2/3. C4: #51-tail q has a CI above 1. Guard: `--confirm --i-understand-this-uses-the-locked-holdout`, a committed H77 folder, `holdout_ledger.check()`. Dry run (#38; units 51h–51l): C1, C2 pass; C3, C4 fail (the stand-in tail's top is not named; q 1.36 [0.78, 1.93]). Pipeline check, not evidence.

## Round 2 redirects (proposed by the round-1 agent, 2026-10-04)
- **H77-R1. Measure reversibility directly.** Classify each loss event from the agent's own trace (an explicit move to another repo inside one context segment vs going idle or an erasure), so uncopying and dilution are observed, not inferred from an expiry rule.
- **H77-R2. Bound with a field term.** Extend the selection bound to replicators with formation (κ > 0) before testing it on field-named repos, or test it only on unnamed repos in long periods (#51 units, #38).
- **H77-R3. q as the usable signature.** Test q < 1 (shared) vs q > 1 (own) on the holdout and against the neutral q̂ ≈ 0.8–0.96 measurement floor.

## Notes
- 2026-10-04: round-1 agent (H77 + H78 together). Card written before any statistic on host labels.
- 2026-10-04: A0 (Mathis) added at the coordinator's request before any real-data statistic; A1 after the synthetic. H78's A2 (fitness-spread worlds, touch class, AR(1) step null) is shared; H77's verdicts do not use it.
- Compute: ≤ 2 threads, no sub-agents, no LLM labels.
