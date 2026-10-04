# H66: Shared platform latency is a common-noise field

**Status:** exploratory round 1 done (2026-10-04). **Refuted as posed.** Card, observables, nulls and predictions written 19:15 UTC before any real-data statistic; Amendment 1 (~20:05 UTC) after the synthetic study, before real data; Amendment 2 (~21:20 UTC) post hoc. `analysis/confirm.py` frozen, guarded and dry-run; **not run**.
- **Little to explain.** After the all-present trim, residual co-activation beats the block-shift null in 4/29 units (44a, 51f, 51g, 51l; pair correlation 0.003–0.039); the median unit has E = 0.0007.
- **A platform latency field exists, but it is not a provider field and not a driver.** Call turnaround co-moves across agents in 11/29 units, all in #44 and #51, and rises with N (ρ̄_lat ≈ 0 at N ≤ 16; 0.02–0.10 at N 17–28; 0.18–0.22 at N 30). Same-lab and cross-lab pairs co-move alike (medians 0.080 vs 0.062). Gemini's own server time does not co-move between agents; the shared part is the harness and execution part of a call.
- **The field is load, not drive (post hoc sign test).** The field rises with the number of active agents in 28/29 units (median corr(L, K) = +0.11). A field that silences agents gives −0.34 to −0.66 (synthetic W2). A congestion world (W6) reproduces the positive sign and returns Δf ≈ 1.1–1.6. The pre-registered rule gives *mixed* (median Δf 0.39 over the 4 units with a residual, CI > 0 in 2/4), but that Δf measures load.
- Natives: G51 (server time; room split) failed as H66; G44 (fine-tuned leader on its own stack, loading −0.11 vs others' median 0.14) consistent with an in-harness load field (descriptive).
**Question served:** **Q2** (what is field and what is coupling?). Secondary: Q6 (the platform as a heat bath).
**Fields:** stat mech, sociophysics, info theory
**Literature:** no note in `literature/` covers common-noise decomposition. Method references from the model folders: `physics-models/01-inverse-ising` (Curie–Weiss variance ratio, fields vs couplings), `physics-models/02-nonequilibrium-ising` (equal-time vs lagged response). Cited from memory (†): Schneidman et al., *Nature* 440, 1007 (2006)† (pairwise correlations from shared inputs); Ma et al. / "common input" partial-correlation corrections in neural data†.
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Population N(t), **day-present variant** (H36: ≥ 10 active minutes that day); Regime; Driving / external field; Action (turn-merged) via the ledger's calls; H38's *all-present window* (agent-state conditioning, trim variant); H50's *field excess (shifted-input null)*. **New named variants proposed** (not edited into DEFINITIONS.md; outside this card's scope): *call turnaround*, *latency field*, *latency field share*, defined under Model.
**From:** HH256 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` ("Making the faithful ones better") · **Models:** `physics-models/01-inverse-ising/` (primary: equal-time co-activation with a common field), `physics-models/02-nonequilibrium-ising/` (secondary: lag structure of field vs coupling)
**Data inputs (shared tables first):** DQ1 `call_windows` (t_first, t_prev_end, t_log, gap_kind, ctx_mode, kind, `dur_api_s` for Gemini), `turn_errors` (infrastructure error categories), `period_units`, `rooms_timeline`, `roster` (lab), `calendar`. No raw rescans. Comparison numbers from H38 round 1b and H50 (cards only).

## Question
After trimming each day to the all-present window, is the residual regime-III co-activation explained by platform-wide API latency (a common field acting at zero lag) rather than by coupling?

**Faithfulness lever (HH256):** axis H (field vs coupling rival) and axis B (the update-order and timing assumptions behind every co-activation statistic). The scorecard says whether it moved them.

## Design: two layers (Vivian, 2026-10-04)
- **Replication (role `replication`):** the common estimator on every eligible non-holdout unit of the computer-use scaffold (regimes II–III; 30 `period_units` units in 11 goal periods). The primary verdict uses the regime-III units. One `G<NN>/` folder per goal period.
- **Period-native tests (role `native`), each with its own dated prediction in its folder:**
  - **G51 (units 51a–51l): measured server time and the room split.** (i) Three Gemini agents log the API's own server time (`dur_api_s`), the only direct platform-latency measurement in regime III; it validates the turnaround proxy and separates a provider field from a village-wide field. (ii) In unit 51g (2026-08-05 → 08-21) the swarm splits into #general and #focus. A platform field ignores rooms; a reading coupling does not. Cross-room pairs are the control.
  - **G44 (units 44a, 44b): the fine-tuned leader on a separate serving stack.** The fine-tuned Kimi leader (2026-05-28 → 05-29 in 44b) is served outside the frontier APIs. A harness-side field reaches it; a provider-API field does not. G44 is also one of the two regime-III periods whose co-activation survived H38's trim and scaffold conditioning.

## Model
**From:** `physics-models/01-inverse-ising` (primary) with the lag reading of `physics-models/02-nonequilibrium-ising`.

**Degrees of freedom.** Agent i in minute m of the all-present window:
- **activity spin** a_i(m) ∈ {0, 1}: 1 if i logs an act call (kind ∉ {pause, wait, consolidate, session_start, session_stop}) whose first record falls in m (H50's definition, built from the ledger's calls);
- **intensity** n_i(m): the number of such calls in m (secondary);
- **call turnaround** τ_c = t_first(c) − t_end(c − 1) for chained computer-use calls (`gap_kind == busy`, `ctx_mode == cu`, 0 < τ < 600 s): the scaffold overhead, the model's generation time and the tool's execution time. For Gemini calls the ledger also has the server's own time `dur_api_s`.
- **latency spin** ℓ_i(m) = median of log τ over i's chained calls starting in m, standardized within agent-day (median and MAD scale). Missing when i makes no chained call in m.

**H66 model: Curie–Weiss with a measured common field.**
  P(a(m)) ∝ exp[ Σ_i (h_i(b) + γ_i L(m) + κ_i u(m)) a_i + (J₀/2N) (Σ_i a_i)² ],
with h_i(b) the agent's field in its (day, 30-min block) b, L(m) the **latency field** (the cross-agent mean of ℓ_j(m)), u(m) the **infrastructure-error field** (number of present agents with a timeout, VM, resource or network error turn in m; H38's categories) and J₀ the residual coupling. A slow platform lengthens every agent's calls together. A call longer than the minute leaves an empty minute, and slow calls can push agents into pauses. So a latency field makes agents fall silent together at zero lag, with J₀ = 0.

**Decomposition.** Block-demeaned activity e_i(m) = a_i(m) − ⟨a_i⟩_b. The equal-time co-activation is ρ̄ = mean over pairs of corr(e_i, e_j) on all-present minutes. The **latency field share** is
  f_lat = 1 − E_adj / E,  E = ρ̄ − ⟨ρ̄⟩_null,  E_adj = ρ̄_adj − ⟨ρ̄_adj⟩_null,
where ρ̄_adj uses, for each pair (i, j), the residuals of e_i and e_j after regression on the third-party field L_{−ij}(m) (the mean of ℓ_k over agents k ≠ i, j; block-demeaned) and on u_{−ij}(m). Using third parties only removes the mechanical link between an agent's own turnaround and its own activity. The null for E is the block shift (each agent's activity circularly shifted within its day × 30-min block; DQ8 size 2–4% on trimmed grids). **Field excess** Δf = f_lat − ⟨f_lat⟩_shifted, where the shifted control circularly shifts L and u within the day by ≥ 30 min (H50's shifted-input null): it removes the share that any slow series with the same autocorrelation would absorb.

**Field strength.** ρ̄_lat = mean pairwise correlation of block-demeaned ℓ_i(m), ℓ_j(m) (minutes where both have calls), split into same-lab and cross-lab pairs. A village-wide platform field (harness, VMs, network) gives ρ̄_lat(cross-lab) ≈ ρ̄_lat(same-lab) > 0. A provider-API field gives ρ̄_lat(same-lab) > 0 and cross-lab ≈ 0.

**Lag reading (model 02).** A field acts at zero lag: the cross-correlation of e_i(m) with L_{−i}(m + k) peaks at k = 0 and is symmetric. A reading coupling lags by at least one call cycle and is room-gated (H50, RE-R1).

**Rivals.**
- **R1 coupling through reading** (H50, H05 RE-R1): the residual co-activation is talk-driven coupling at the read-out call. Signature: same-room pairs carry more residual than cross-room pairs, and L removes nothing beyond the shifted control.
- **R2 provider field:** latency co-moves only within a lab (separate APIs). Then the field is real but is not platform-wide, and it can explain only same-lab co-activation.
- **R3 shared workload:** agents run heavy tool work at the same moments (builds, deploys), which lengthens turnaround through execution time, not the platform. Signature: the Gemini server-time field (no execution time) is weaker than the turnaround field.
- **R4 scheduler residue:** what survives the trim is still day-edge or timer-gate synchrony (H38, H09 RE-R1). Signature: E concentrated in the first and last 30 min of the all-present window.

## Data scheme (`scheme/build.py`)
- **Inputs:** `call_windows` (non-holdout rows; `holdout_mask` asserted to agree), `turn_errors`, `roster`, `rooms_timeline`, `period_units`, `calendar`.
- **Transform, per eligible unit:**
  1. Calls of roster agents (Claude Code agent excluded) on the unit's days; act calls as above; chained calls for turnaround.
  2. Minute grid per unit-day, from the first to the last minute in which any agent has a call. Per agent: a_i, n_i, ℓ_i, the Gemini server-time spin ℓ_i^api (Gemini agents only), the infrastructure-error count, the day span (first to last act call), the room at the minute (`rooms_timeline`) and the lab.
  3. Day-present agents: ≥ 10 act minutes that day. All-present window: minutes in which every day-present agent is inside its span (`infra/shared/nulls.all_present_window`).
- **Output:** `data/processed/H66-platform-latency-field/` with `grid/<unit>.parquet` (unit × day × minute × agent: a, n, ℓ, ℓ^api, err, room, in_span, present; codes only), `units.parquet`, results in `replication/`, `native/`, `synthetic/`, `confirm_dryrun/`, and `_provenance.json`. Budget ≤ 100 MB.
- **Eligible units:** non-holdout units of regimes II–III with ≥ 4 day-present agents and ≥ 120 all-present minutes with a defined field (≥ 3 contributing agents per minute). The primary verdict uses regime III.
- **Regimes covered:** II and III (chained computer-use calls; regime-I chat-mode calls are scheduled, so turnaround is not defined there).

## Observables
Per unit (replication), with day-block bootstrap CIs (B = 200; minute blocks of 30 min for units with < 3 days):
1. **E** (residual trimmed co-activation, binary spin) and its block-shift z (99 surrogates).
2. **Field strength** ρ̄_lat: all pairs, same-lab, cross-lab; block-shift z. Per-agent loading g_i = corr(ℓ_i, L_{−i}).
3. **f_lat, Δf** on the binary spin (primary) and on intensity n_i (secondary). Variants: field = turnaround only, errors only, both (primary); window = all-present (primary), pair spans (secondary).
4. **Lag profile** C(k) = mean_i corr(e_i(m), L_{−i}(m + k)) for k = −5…+5 min, and C_ℓ(k) for the latency spins themselves.
5. **Room split** (units with ≥ 2 structural rooms): E and ρ̄_lat for same-room vs cross-room pairs.
6. **Edge concentration (R4):** E on the first and last 30 min of the all-present window vs the middle.
7. **Gemini server time** (where ≥ 2 Gemini agents): within-call corr(log τ, log dur_api_s); ρ̄ of the API spin between Google agents; corr of the Google API field with the non-Google turnaround field.

## Null / baseline
- **N1 block shift** (activity or latency series shifted within day × 30-min block, after trimming): independent agents with the same half-hour rates. DQ8 size 2–4% on trimmed grids for the gain; own size check in the synthetic study for ρ̄_lat and f_lat.
- **N2 shifted field** (L and u circularly shifted within the day by 30 min to the day length minus 30 min): the share any slow series removes. Δf is measured against it.
- **N3 synthetic worlds** at real counts (below): no field, latency field without activity effect, latency field acting on activity, room coupling, provider-only field.

## Impostor table (STANDARDS §1)
| Impostor | How H66 removes it, or why it does not apply |
| --- | --- |
| Scheduler field | Every statistic is computed on the all-present window, with block-demeaning per 30-min block and the block-shift null drawn after trimming (DQ8). Edge concentration (observable 6) checks the residue. The latency field is itself a candidate field, so it is the object, not a nuisance. |
| Exogenous field (kickoff, goal, operator) | Block fields h_i(b) absorb slow drives. Variant: drop minutes within 10 min after a human message, nudge or bookend (`kicks_classified`). Kickoffs precede the day's window (H04), so they act on day means, which block-demeaning removes. |
| Shared model priors (family, style) | Latency correlation is split into same-lab and cross-lab pairs: a lab field is named as rival R2, not counted as platform-wide. Activity co-activation is reported for cross-lab pairs as a variant. |
| Contemporaneous convergence | Not a content claim. The analogous timing risk is two agents answering the same input at the same moment: block fields and the kick-exclusion variant remove the common inputs, and the room split separates read-coupled from unread pairs. |

## Synthetic validation (axis F; `analysis/synthetic.py`; before any real-data statistic)
Minute-level swarms with the skeleton of real units (N, days, all-present lengths of 44b, 39 and 51c). Each agent alternates work runs and timer pauses (two-state Markov, regime-III dwell times); while working it makes chained calls with lognormal turnaround (median 12 s); a minute is active if a call's first record lands in it. Scenarios (20 seeds each):
- **W0** independent agents (no field, no coupling);
- **W1** latency field without activity effect (common OU field on log τ; σ chosen so ρ̄_lat ≈ 0.05; calls just get slower);
- **W2** latency field acting on activity (the same field also raises the pause hazard: γ such that the field causes a known share of co-activation);
- **W3** room coupling only (a talk event in the room raises the pause-exit hazard of room-mates at the next minute);
- **W4** W2 + W3;
- **W5** provider-only field (one field per lab).
Planted truth f_true = 1 − E(world without the field)/E(world) with matched seeds.
Checks: size of the block-shift test for E and ρ̄_lat in W0–W1 (≤ 0.07); |Δf| < 0.05 in W1 and W3; Δf within ±0.15 of f_true in W2 and W4; power ≥ 0.8 for ρ̄_lat at 0.05 (51c scale) and for Δf ≥ 0.3; W5 same-lab ≫ cross-lab.

## Amendment 1 (2026-10-04 ~20:05 UTC; after the synthetic study, before any real-data statistic)
1. **Field kernel.** The first synthetic run (concurrent field only) recovered Δf ≈ 0.24–0.30 in W2, whose true share is ≈ 1.0: the field acts through the pause state, which has memory. The field regressors are now L_{−ij}(m − k) and u_{−ij}(m − k) for k = 0…5 min (a causal response kernel). The lag-0-only estimator is still reported (`binary_lag0`). "Zero lag" in the card refers to the agent–agent co-timing of a field (C_ℓ(k) peak), not to the field's response kernel.
2. **Bias of Δf (synthetic, 8 seeds × 2 skeletons; `synthetic/summary.json`).** Δf is a **lower bound**: W2 (weakly measured field, ρ̄_lat 0.04) 0.73–0.75 vs true ≈ 1.0; W2s (ρ̄_lat 0.5) 0.83–0.85 vs 1.0; W4 (field + coupling) 0.41–0.48 vs 0.84–0.91. It does not attribute coupling to the field: W3 −0.30 ± 0.61 (44b, E not significant in 5/8 seeds) and 0.005 ± 0.025 (51c); W1 (field measured, not acting) 0.03–0.06. The worst observed attenuation is ×0.45. A Spearman–Brown reliability correction overshoots (1.7–2.5 in W2) and is dropped.
3. **Decision rule restated on this basis (P2).** Supported if median Δf ≥ 0.35 with Δf > 0 at 95% in ≥ 2/3 of units with a significant E (a true share ≥ ~0.4); **failed if median Δf < 0.10** (a true share < ~0.22 even at the worst attenuation); mixed otherwise. The per-unit README rule uses the same cut-offs (supported ≥ 0.35 with CI > 0; failed < 0.10 or CI including 0 with point < 0.10).
4. **Sizes.** Block-shift test of E: 0/16 rejections in W0 and 0/16 in W1 (95% upper bound 0.17). ρ̄_lat test: 1/16 in W0. Power for ρ̄_lat at 0.04–0.05: 32/32. W5 (provider field): same-lab ρ̄_lat 0.08 vs cross-lab 0.00, as designed. A pure mechanical slowdown (W1b) creates no significant binary co-activation (E ≈ 0).
5. P0 as written ("within ±0.15") **failed** for W2 and W4; per P0 the real Δf is read as a lower bound, not a point estimate.

## What I had seen (disclosure)
Before writing this card I read H38 round 1b (after the trim only #37, #44 and #51 keep a significant regime-III excess; #44 and #51 survive scaffold conditioning), H50 (activity co-movement is a schedule field; inside the all-present window per-pair activity correlation is 0.005 in regime III; talk is a gated coupling), H40, H56 and the infra Known issues. I computed design facts only: non-holdout regime-III calls 1.24M, of which 278k carry `dur_api_s` (all Google); median busy turnaround 12.3 s (q90 30.6 s); median server time 5.0 s; median turnaround by lab 9.4–16.7 s. I have computed no latency correlation and no co-activation statistic.

## Prediction
*Written 2026-10-04 19:15 UTC, before running the synthetic study or any real-data statistic. Credences in brackets.*
- **P0 (synthetic, F).** The checks above pass [0.7]. If W2 is not recovered within ±0.15, real Δf is uninterpretable.
- **P1 (a field exists, but it is a provider field).** ρ̄_lat > 0 beyond N1 (p < 0.05) in ≥ 2/3 of regime-III units [0.6], with median ρ̄_lat ≤ 0.05 [0.6], and same-lab ρ̄_lat ≥ 2× cross-lab in ≥ 2/3 of units [0.55].
- **P2 (primary; H66 core).** In regime-III units with a significant E (block-shift p < 0.05), the latency field explains a minority of the residual: median Δf < 0.25 [0.75]. **H66 supported** if median Δf ≥ 0.5 and Δf > 0 at 95% in ≥ 2/3 of those units. **Failed** if median Δf < 0.2. Mixed otherwise. [Credence supported: 0.12.]
- **P3 (zero lag).** Where ρ̄_lat is significant, the lag profile C_ℓ(k) peaks at |k| ≤ 1 min and is symmetric within its CI [0.65].
- **P4 (intensity vs spin).** Δf on intensity exceeds Δf on the binary spin in ≥ 2/3 of units [0.7] (slow calls mechanically mean fewer calls per minute).
- **P5 (coupling rival R1).** In two-room units, residual E is larger for same-room than for cross-room pairs in ≥ 2/3 of units [0.55].
- **P6 (scheduler residue R4).** E per minute in the first and last 30 min of the all-present window is ≥ 1.5× the middle in ≥ half of units [0.45].
- **Against H66 as posed:** P2 failing (Δf < 0.2) with P0 passing. **Against my reading** (provider field, coupling residual): cross-lab ρ̄_lat ≈ same-lab, or same-room E ≤ cross-room E.
- **Replication rule for a unit's period README:** *supported* if E is significant and Δf > 0.5 with CI > 0; *failed* if E is significant and Δf < 0.2 (or CI includes 0); *mixed* otherwise; *descriptive* if E is not significant (nothing to explain), with ρ̄_lat reported.

## Amendment 2 (2026-10-04 ~21:20 UTC; post hoc, after the real-data replication)
1. **Sign test.** The card's model says a slow platform makes agents fall silent together, so the latency field L and the number of active agents K must anti-correlate. In synthetic W2/W2s the block-demeaned corr(L, K) is −0.34 to −0.66, and agents' activity anti-correlates with the third-party field (C_act(0) −0.14 to −0.29). In the real data corr(L, K) is positive in 28/29 units (median +0.11; beyond 2 null SD in 17/29) and C_act(0) is positive in 27/29. This was not a pre-registered test; it is promoted to the frozen C1 of `confirm.py`.
2. **Congestion world W6** (post hoc synthetic; `synthetic/w6_posthoc.json`): latency rises with the active count, a slow common drive moves activity, latency does not act on activity. The estimator returns E significant in 8/8 runs and Δf 1.05–1.60 with corr(L, K) +0.54 to +0.72. **The third-party-field regression cannot separate a field that drives co-activation from a load meter that co-activation drives.** Only the sign separates them.
3. Consequence: the per-unit pre-registered rule is reported, and the period verdicts are set after this amendment (failed where a residual exists, descriptive elsewhere).

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | descriptive | E n.s.; ρ̄_lat 0.03 (n.s.) |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | descriptive | E n.s.; ρ̄_lat 0.01 |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | descriptive | 3 units; E n.s.; ρ̄_lat ≤ 0.02 |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | descriptive | E n.s. (H38's marginal #37 residual does not survive the call-based spin) |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | descriptive | 5 units; E n.s.; ρ̄_lat −0.02 to 0.01 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | descriptive | E n.s.; ρ̄_lat 0.006 |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | descriptive | E n.s. |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | descriptive | E n.s. |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | descriptive | 2 units; E n.s. |
| [G44](goalperiod-subhypotheses/G44/README.md) | native | failed | 44a: E 0.039 (z 3.2), Δf 0.74 [0.08, 1.88], ρ̄_lat 0.10, corr(L, K) +0.23; leader loading −0.11 |
| [G51](goalperiod-subhypotheses/G51/README.md) | native | failed | E sig. in 51f, 51g, 51l; Δf 0.36 [0.25, 0.61], 0.17, 0.42; ρ̄_lat to 0.22 at N 30; server time r 0.49 with turnaround, no cross-agent co-movement |

## Results
*Round 1, 2026-10-04; non-holdout only; 29 eligible units (26 regime III, 3 regime II; 51b ineligible: no all-present minutes with a defined field). Scripts: `scheme/build.py`, `analysis/h66lib.py`, `synthetic.py`, `replication.py`, `native.py`, `summarize.py`, `confirm.py`. Numbers: `data/processed/H66-platform-latency-field/{synthetic,replication,native,confirm_dryrun}/`. Figures: `figures/summary_obs.pdf`, `figures/synthetic.pdf`.*

**Outcome vs prediction.**
| Prediction | Observed | Verdict |
| --- | --- | --- |
| P0 synthetic: size ≤ 0.07; Δf within ±0.15 of truth | sizes 0/16 (E), 1/16 (ρ̄_lat); Δf a lower bound (W2 0.73–0.75 vs 1.0; W4 0.41–0.48 vs 0.84–0.91); no false attribution in W1/W3 | partly (lower bound; Amendment 1) |
| P1 field exists in ≥ 2/3 of regime-III units; median ≤ 0.05; same-lab ≥ 2× cross-lab | 11/26; median 0.010; same ≥ 2× cross in 1/11 (medians 0.080 vs 0.062) | failed (rarer than predicted, and village-wide, not provider) |
| P2 Δf < 0.25 median where E is significant (rule: failed < 0.10, supported ≥ 0.35 + CI) | E sig. in 4/29; Δf 0.74, 0.36, 0.17, 0.42 (median 0.39; CI > 0 in 2/4) | rule: mixed; after Amendment 2: the Δf is load, H66 refuted |
| P3 zero-lag peak of C_ℓ(k) | median C_ℓ(0) 0.023 vs C_ℓ(±1) 0.017; sharp lag-0 peak in every unit with a significant field | held |
| P4 Δf on intensity > binary in ≥ 2/3 | 14/29 | failed |
| P5 same-room E > cross-room E in ≥ 2/3 of two-room units | 5/18 (E ≈ 0 in most) | failed (no residual to gate) |
| P6 edge concentration ≥ 1.5× in ≥ half | 3/4 units with significant E (44a 2.3×, 51f 6.1×, 51g 2.0×, 51l 0.9×) | held |
| Native G51 (server time, rooms) | server time r 0.49 with turnaround (0.44 of it); no co-movement of server time across agents; turnaround co-moves across providers (0.01–0.69, rising in late #51); cross-room ρ̄_lat ≥ same-room | failed as H66 |
| Native G44 (fine-tuned leader) | loading −0.11 vs others' median 0.14 (70 min) | descriptive |

**What it means.**
1. **The residual is small and lives at the edges.** On the call-based spin, the all-present trim leaves significant co-activation in 4 of 29 units. In 3 of those 4 it is ≥ 2× denser in the first and last 30 minutes of the window. This agrees with H38 round 1b and H50 (residual 0.005 per pair in regime III).
2. **The platform does have a common latency field, and it is the harness.** Turnaround co-moves at zero lag across providers. Gemini's server time is 44% of a call's turnaround and does not co-move across agents. The shared part is tool execution and scaffold overhead on the village's own infrastructure. Its strength grows with N: about 0.2 at N = 30.
3. **That field is an effect of activity, not a cause.** It rises when more agents are active (28/29 units), which is what congestion or shared heavy work produces. A driving field would do the opposite. A regression on a third-party field absorbs co-activation whichever way the arrow points (W6), so field shares from such regressions need the sign test.
4. **Operator reading.** Platform latency does not make agents co-act. A rising cross-agent latency correlation is a load meter: it reached 0.2 at N = 30 in late #51.

**Caveats.**
- The sign test and W6 are post hoc (Amendment 2). They reverse the reading of a pre-registered rule that would have said *mixed*.
- Turnaround is a proxy: generation, tool execution and overhead together. Only Gemini calls have server time.
- Few units carry a residual (4). Δf CIs are wide (day or 30-min block bootstrap, 1–13 days).
- Load could be congestion or shared heavy work at the same moments (R3); the data do not separate them.
- The fine-tuned-leader test has 70 minutes.
- Regime II has 3 units. The holdout is not run.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R1 coupling through reading; R2 provider field; R3 shared workload; R4 scheduler residue; post hoc: congestion (load-driven latency).
**Locked holdout used for confirmation:** none yet (`analysis/confirm.py` frozen and dry-run on non-holdout stand-ins: C1–C4 pass; targets #43, #45–#50, #51 tail).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Spins, turnaround and server time come from DQ1 calls; the same rules in regimes II and III. Turnaround mixes generation, execution and overhead; server time exists only for Gemini. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Block fields absorb slow drift. **The causal-direction audit (sign test) decided the reading**: the field follows activity. Not pre-registered. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | E beats the trimmed block-shift null in 4/29 units; the field beats its null in 11/29. No held-out-day prediction. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | Zero-lag peak held; the model's signature (negative field–activity relation) failed in 28/29 units. |
| E interventional | predicts the change across a natural experiment | 0 | No NE used; the room split (51g) and the separately served leader (44b) are weak contrasts. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Δf is a lower bound for a driving field and ≈ 1 for a load meter (W6): **not identified without the sign**. Sizes calibrated (0/16, 1/16). |
| G ground truth | agrees with known structure | 1 | Gemini server time validates the proxy (r 0.49) and shows the API part does not co-move. |
| H comparative | beats the named rivals | 1 | Provider field rejected (cross-lab ≈ same-lab); the load reading beats H66's drive reading on sign; coupling (R1) is not needed for the 4 residual units but is not tested by a gate here. |
| I transfer | holds in other same-mode periods, including the holdout | 1 | Same pattern in #44 and #51 (all units with a field); holdout not run. |

**Faithfulness lever (HH256):** H moved: the field-vs-coupling rival became a field-vs-load test, which the field lost. B moved: the update-order audit found the direction of causation.

## Round 2 redirects
**What the direction is really after:** separating exogenous platform fields from swarm-made fields in the residual co-activation.
- **H66-R1. Congestion as an order parameter.** Fit latency vs active count per unit (a load curve) and its slope vs N; test whether ρ̄_lat ∝ N at fixed load. A capacity number for operators.
- **H66-R2. An exogenous platform probe.** Use infrastructure-error bursts that start in one provider's harness, or the outage days (H38), as instruments: shocks that are not caused by load.
- **H66-R3. Separate execution from generation** with the Anthropic and OpenAI token counts (output tokens per second) where usage is logged.
- **H66-R4. Holdout.** Run `confirm.py` (C1 load sign, C2 not a provider field) after sign-off.

## Notes
- 2026-10-04 19:15 UTC: card written before any statistic (see disclosure).
- 2026-10-04 ~19:30–20:05: synthetic study in two passes (first: concurrent field only; second: 0–5 min kernel), Amendment 1.
- 2026-10-04 ~20:45–21:20: real-data replication (29 units, 2 workers, ~6 min), natives, sign test and W6 (Amendment 2).
- Compute and disk: local, ≤ 4 processes (2 after the coordinator's load notice), ≈ 40 CPU-min; `data/processed/H66-platform-latency-field/` ≈ 3 MB.
- **Proposed shared-file changes** (not made): DEFINITIONS.md named variants *call turnaround* (t_first − previous t_end of a chained call), *latency field* (cross-agent mean of within-agent standardized log turnaround), *load sign* (block-demeaned corr of the latency field with the active count); infra Known issue: third-party field regressions absorb co-activation from load meters (W6), so report the sign of the field–activity relation with any field share.
