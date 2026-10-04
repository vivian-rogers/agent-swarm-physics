# H51: One dial: an effective coupling collapses the phase diagram

**Status:** **exploratory round 1 done (2026-10-04, non-holdout only). Failed: the read-out coupling g_lag does not collapse the phase diagram; regime labels and N carry the information.**
- **No one-dial collapse.** g_lag collapses 0/4 unfitted observables (settling, herding, branching, loops) across 33 periods. Its within-regime permutation p = 0.07 (synthetic power 0.89 at the effect that matters).
- **Regime and N win.** Best leave-one-period-out R²: herding 0.38 (log N), loops 0.32 (regime), branching 0.19 (regime + log N), settling ≈ 0 (nothing). log N adds within-regime information (permutation p = 0.002); the best single index is ≈ log N (weight 0.86–0.95).
- **Mean-field bound.** Every unit is subcritical, so χ = 1/(1 − g) ≤ 1.31, while observables vary ×3 to ×127 across periods.
- **Natives:** NE14 mixed (switching the coupling on at fixed goal barely moves loops), NE42 failed for the dial (#40 follows room size on 4/4 signs, the dial on 1/4), G51 failed for the dial (R̂ rises with N, ρ 0.83, at flat g_lag).
- Scorecard A1 B1 C1 D1 E0 F2 G0 H1 I0. `analysis/confirm.py` frozen, guarded and dry-run; **not run**.
**Question (GOALS.md):** **Q2** (what is field and what is coupling?), with the phase-diagram deliverable ("every period placed by its fitted parameters; axes field strength, coupling and N") as the product.
**Fields:** stat mech (data collapse, mean-field scaling), sociophysics
**Literature:** model references in [`physics-models/10-potts/README.md`](../../physics-models/10-potts/README.md) (mean-field Potts: order vs βJ and h) and [`physics-models/02-nonequilibrium-ising/README.md`](../../physics-models/02-nonequilibrium-ising/README.md) (kinetic Ising: field and coupling as separate control parameters). Data collapse and scaling functions (Stanley 1999†; Bhattacharjee & Seno 2001†) are quoted from memory († = not in `literature/`).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Population N(t), variant *active population* (H85); Regime; Driving / external field; H25's **loop gain (equal-time, daily dial)**; H34's **branching ratio (content)**; H11's **agent state (categorical, project)**; H48's **kickoff remanence at active-hour resolution**. Variants proposed by other cards and used here as defined there: H67 **read-out loop gain g_lag**; H86 **shared-field coefficient c_×** and **shared share φ**; H54 **kickoff specificity S_text**. New named variants proposed for DEFINITIONS.md (not edited there; defined under Observables): **phase-diagram axes (h, K, N)**, **one-dial collapse**, **loop rate (restatement share)**.
**From:** HH178 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/10-potts/` (primary), `physics-models/02-nonequilibrium-ising/` (secondary), `physics-models/14-scaling-and-fluctuations/` (tool: data collapse)
**Data inputs (shared tables first):** `per_period_estimates` (H67 `readout_loop_gain_g_lag`; H86 `taylor_c_shared` / `taylor_phi_shared`, `activity_trim`; H85 `active_population_N`, `pending_set_k_talk`; H38 `f_scaffold`; H48 `tau_settle_S1_active_h`; H11 `cowork_excess`; H31 `consensus_time_gradual_median_h`), `period_units`, `statement_flags` + `embeddings/statements` (loop rate), H34's ledger first-use tables (`data/processed/H34-idea-cascades/r1b/G*/first_uses.parquet`; read only), H54's `kickoffs.parquet` (S_text; read only), H67's `results/{units,periods}.parquet` (period pools, call interval; read only). No text.

## Source HH (verbatim from the HH list)
**HH178 · One dial: an effective coupling K collapses the phase diagram.** Combine read-out, naming, dilution and rooms into one number per period: K = ν_read × (f_named·pull_named + (1 − f_named)·pull_broadcast) / k^0.6, with k counted within a room. Prediction: herding strength (H11), consensus time (H31), loop prevalence (H12) and stall-adjusted co-activation (H38) collapse onto K across periods, unlike the generic loop-gain curve that failed (HH100, H19). *Check:* K per period from shared tables; data collapse of each outcome vs K, holdout periods reserved.

## Question
Does one per-period number, an effective coupling built from the measured coupling, field and size axes, put unfitted swarm observables (settling time, herding share, idea branching, loop rate) on one curve across goal periods, better than regime labels alone or N alone?

**Why now.** The ingredients of HH178's K now exist as calibrated per-unit estimates. H67's read-out loop gain g_lag = m̄ r̄ J₁* *is* HH178's K: readers per message (ν_read, rooms), a per-read jump that is address-gated (naming-weighted pull) and that falls with N (dilution). H86 supplies a field gauge (c_×), H54 a kickoff field (S_text), H85 the active N. H51 asks whether these axes compress the phase diagram to one dial.

## Design: two layers (Vivian, 2026-10-04)
- **Replication (layer 1):** every non-holdout goal period with the axes and at least one observable is one point. Axes are pooled over the period's units (H67's random-effects pool for g_lag; day-weighted means for c_×, φ, N). The collapse is a comparison of periods as points on a phase diagram (CLAUDE.md: compare periods by their fitted parameters; no model is fitted to pooled events). Each period README reports the point and its residuals; role `replication`.
- **Period-native tests (layer 2), each with its own dated prediction in its folder:**
  - **NE14** (#36: 36a regime II → 36b/36c regime III; fixed goal, fixed roster N ≈ 12). g_lag switches on (H67: −0.06 → 0.12). The dial predicts each observable's shift from the across-period slope; the scaffold change is a rival explanation.
  - **NE42** (#39 → #40 → #41: rooms merged for one week, A-B-A). g_lag collapses in the merged week (0.144 → 0.003 → 0.189) while room N doubles. The dial predicts an A-B-A in the K direction; N alone predicts the opposite direction in #40.
  - **G51** (roster growth 21 → 32 agents in one room, sub-units 51a–51l). g_lag is flat (H67: 0.14). The dial predicts flat observables; N alone predicts trends.

## Model
**From:** `physics-models/10-potts/` (mean-field Potts / Curie–Weiss with a field), `physics-models/02-nonequilibrium-ising/` (field and coupling as separate control parameters).

**H51 variant: linear response around a subcritical mean-field state.** Each agent's state (project, idea, talk) relaxes toward the local field h_i = h_ext + K·m, with m the population order parameter. In mean field,

  m = h_ext·χ,  χ = 1/(1 − K),  τ_relax = τ₀/(1 − K),

so every collective observable is a function Y = F(h_ext, K, N). **One-dial collapse** means there is a single combination u = u(h, K, N) with Y_j = F_j(u) for every observable j, the same u for all j. HH178's version: u = K, the read-out coupling.

**What the measured axes imply before any fit (physics prior).** Every unit is subcritical (H67: g_lag ≤ 0.39 upper bound; regime-III median 0.13, regime I ≈ 0). Mean-field amplification χ = 1/(1 − K) therefore spans 1.00–1.30 across all periods. A coupling dial can move a field-driven observable by at most ≈ ×1.3. If observables vary ×3 or more across periods, most of that variation must come from the field and the goal, not from K. This is the reason the prediction below is negative.

**Axes (phase-diagram coordinates; inputs, never fitted here):**
- **K, coupling:** g_lag (H67), period random-effects pool, with SE.
- **h, shared field in the all-present window:** c_× on trimmed 15-min activity (H86 `taylor_c_shared`, `activity_trim`), day-weighted over units; φ (`taylor_phi_shared`) as a variant. **h_kick, kickoff field:** H54's S_text (text-only specificity of the kickoff). **f_sched** (H38 `f_scaffold`): descriptor only.
- **N:** H85 active population (hour-weighted), day-weighted over units; log N in all fits.
- Equal-time dial g_eq (H67's same-data value; H25's construction) is a *rival dial* (it reads fields as gain).

**Dials compared (each a single number per period):**
- **D1 = g_lag** (HH178's K; primary).
- **D2 = single index u = w·z**, z = standardized (g_lag, log c_×, S_text, log N), |w| = 1, one w shared by all observables. For observable j, w is fitted on the *other* observables only (leave-one-observable-out), so Y_j is unfitted when it is scored.
- **Rivals:** R0 intercept; **R1 regime labels** (I / II / III); **R2 log N**; R3 field only (log c_×, S_text); R4 equal-time dial g_eq.

## Data scheme (`scheme/`)
- **Inputs:** listed above. All axis and observable rows are non-holdout (the shared writer refuses held-out rows; every script also applies `holdout_mask` and asserts no held-out goal enters).
- **Transform:** (1) map estimate rows to goal periods (rows keyed `G<NN>` or an unsplit unit `NN` are whole periods; split units are pooled day-weighted); (2) pool axes per period; (3) build observables per period: H48 τ_settle (bge; gte variant), H11 cowork excess (project; work variant), R̂ recomputed with H34's formula on its ledger (r1b) first-use tables (H34's published table values as variant), loop rate from `statement_flags`; (4) native sub-unit observables: R̂ and loop rate cut at the `period_units` boundaries of #36 and #51 (H11's existing sub-unit rows for herding in #51).
- **Output:** `data/processed/H51-one-dial-collapse/` — `axes_periods.parquet`, `axes_units.parquet`, `observables_periods.parquet`, `natives_units.parquet`, `results/*.json|parquet`, `synthetic/`, `_provenance.json`.
- **Regimes covered:** I, II, III (non-holdout periods #2–#51 head).

## Observables
Unfitted outputs; none enters any axis.
- **Y1 settling time:** log τ_settle (H48 S1, active hours, bge; gte variant). **Call-clock variant (H40):** τ in calls = τ_h × 3600 / (median call interval, H67 units).
- **Y2 herding share:** H11 `cowork_excess` (project): share of labelled agents sharing their project with ≥ 1 block-mate, minus the circular-shift null mean.
- **Y3 idea branching:** R̂ = first uses with an agent parent ÷ all agent first uses (H34 rule, ledger visibility); logit.
- **Y4 loop rate (restatement share):** share of an agent's chat statements flagged as a self-repeat by either embedding model (DQ5 `statement_flags.self_repeat`; `self_repeat_both` variant); logit.
- **Y5 (secondary, report only):** H31 gradual consensus time (log active hours).
- **Collapse score per observable and dial:** leave-one-period-out cross-validated R² (CV-R²) of Y_j on the dial (linear; quadratic variant), and the same for every rival. **Collapse residual:** CV-R²(dial + regime) − CV-R²(dial).

## Null / baseline
- **Within-regime permutation null:** permute the dial among periods of the same regime (2,000 draws). It keeps everything regime labels explain and destroys only the within-regime information of the dial. Statistic: Σ_j [CV-R²(dial + regime) − CV-R²(regime)].
- **Rivals R0–R4** (above) as the baseline hierarchy.
- **Synthetic calibration** at the real axis values and real period counts (see Prediction S1–S3) sets size and power.

## Impostors (STANDARDS §1)
| Impostor | How H51 removes it | Status |
| --- | --- | --- |
| **Scheduler field** | The coupling axis g_lag is computed on the all-present window with the in-flight placebo (H67); the field axis c_× is the trimmed value (H86). The scheduler share f_sched is carried as a descriptor and as a variant covariate. Observables: R̂ and loop rate are per statement, not activity synchrony; τ_settle is in active hours. | partly (observable-level scheduler effects not removed) |
| **Exogenous field** (kickoff, goal, operator) | The kickoff field S_text and the in-window shared field c_× are explicit axes and a rival (R3). τ_settle is measured relative to the kickoff. Goal content differences between periods remain. | partly |
| **Shared model priors** | Not removed at period level: roster composition differs across periods, and loop rate depends on model family (DQ5). G51's within-period N sweep holds the era fixed. | open |
| **Contemporaneous convergence** | The coupling axis uses the matched-lag in-flight placebo (removed for K). R̂ counts exposure-parented first uses, about half of which is convergence (H34); herding share is not placebo-corrected. | partly |

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** regime labels alone; N alone (H85 allometry); field only (c_×, S_text); equal-time dial (H25/H26 reading fields as gain).
**Locked holdout used for confirmation:** none yet. `analysis/confirm.py` (frozen, guarded, not run) targets the held-out goal periods that have all axes.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Axes are other cards' calibrated per-unit estimates (H67, H86, H85, H54); observables are built from shared tables with H11/H34 rules re-implemented and checked (ρ 0.93, 0.96). Not invariant: g_lag is ≈ 0 in regimes I/II, so across regimes it is half a regime label. Shared priors (roster composition) are not removed at period level. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Period = one point (its units pooled). Results hold under seven observable/axis variants (gte settling, call-clock settling, H11 herding, both-model loops, φ for c_×, H34 table R̂): D1 collapses 0/4 in all. No stationarity test within periods. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | The dial fails to beat the null hierarchy: D1 CV-R² ≤ 0.22 and below regime labels on herding (−0.27) and loops (−0.10); within-regime permutation p 0.07 (size 4%). The rivals do beat M0: log N (herding 0.38), regime (loops 0.32), regime + log N (branching 0.19). |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | The model's own signature (one curve for all observables) fails. The physics prior passes: subcritical gains bound the dial's effect at χ ≤ 1.31, and P5 (no critical speed-up of settling, ρ 0.05) and P7 (the equal-time dial does no better) hold. G51: the dial predicts flat observables; R̂ rises with N (ρ 0.83). |
| E interventional | predicts the change across a natural experiment | 0 | NE14: the K step leaves loops at 13× less than D1 predicts; NE42: D1 sign 1/4 vs N 4/4. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 | At the real axis values and counts (100 runs per world): size 3–4%; permutation power 0.73 / 0.89 / 0.99 at ρ²_K 0.15 / 0.30 / 0.50; index direction recovered (|cos| ≥ 0.8 in 98%). The 3/4 collapse-count rule is underpowered (18% at 0.30) and was demoted before real data (A1). |
| G ground truth | agrees with known structure | 0 | No ground truth exists for a phase-diagram collapse. |
| H comparative | beats the named rivals | 1 | The named rivals beat the dial: regime (loops, consensus), log N (herding; within-regime p 0.002), regime + log N (branching). The equal-time dial and the field-only rival do worse than both. Scored 1 because the comparison is decisive, not because the dial wins. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | No holdout run. |

## Prediction
*Written 2026-10-04 20:40 UTC, before any collapse statistic. Seen beforehand: table schemas and row counts; the published per-period values and headlines of H67 (g_lag by period), H86 (c_× medians), H85, H54, H48, H34, H11, H38; H34's R̂ for G36/G38/G40/G51 (to check the formula). Not seen: any correlation between an axis and an observable, any H51 statistic.*

**Synthetic (axis F), before real data.** Observables simulated at the real periods' axis values and counts (g_lag drawn with its own SE as measurement error), in four worlds: W0 regime offsets only; W1 one dial (Y = regime offsets + b·g_lag + noise, partial R² of g_lag within regime ρ²_K ∈ {0.15, 0.3, 0.5}); W2 log N only; W3 single index on (g_lag, c_×, S_text, N).
- **S1 size:** in W0 and W2, the within-regime permutation test rejects in ≤ 10% and the per-observable collapse rule fires in ≤ 10%.
- **S2 power:** in W1 at ρ²_K = 0.3 (the effect that matters: the dial explains 30% of within-regime variance), the permutation test rejects in ≥ 80% at the real sample sizes. If not, a negative result is reported as inconclusive at that size.
- **S3 recovery:** in W3 the leave-one-observable-out index direction has |cos(ŵ, w)| ≥ 0.8 in ≥ 80% of runs.

**Real data (exploratory, non-holdout).** Unit: goal period. "Collapses" for observable j and dial D: CV-R²(D) ≥ 0.15, CV-R²(D) ≥ max(CV-R²(regime), CV-R²(log N)) + 0.05, and CV-R²(D + regime) − CV-R²(D) ≤ 0.05.

| # | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| P1 | **HH claim fails for D1.** g_lag collapses at most 1 of the 4 observable families (Y1–Y4), and the within-regime permutation p ≥ 0.05. | g_lag collapses ≥ 3/4 with permutation p < 0.05 (that would support HH178) | 0.75 |
| P2 | **No single index collapses either.** D2 collapses at most 2/4 families. | D2 collapses ≥ 3/4 and beats every rival on them | 0.7 |
| P3 | **g_lag is a regime indicator at period level.** |CV-R²(g_lag) − CV-R²(regime)| ≤ 0.05 on ≥ 3/4 observables. | g_lag beats regime by > 0.05 on ≥ 2 observables | 0.6 |
| P4 | **Branching follows the read-out coupling.** R̂ is the observable most tied to K: within regime III, Spearman ρ(R̂, g_lag) > 0. | ρ ≤ −0.3 | 0.5 |
| P5 | **No critical speed-up.** τ_settle does not fall with K (Spearman ρ ≥ −0.2 across periods); mean field predicts a slight rise (τ ∝ 1/(1 − K)). | ρ < −0.4 | 0.6 |
| P6 | **Fields beat the coupling dial.** The field-only rival R3 has a higher CV-R² than D1 on ≥ 2/4 observables. | R3 below D1 on all four | 0.45 |
| P7 | **The equal-time dial does no better.** CV-R²(g_eq) ≤ CV-R²(g_lag) + 0.05 on ≥ 3/4 observables (a field-contaminated dial gains nothing as a collapse variable). | g_eq beats g_lag by > 0.05 on ≥ 2 observables (fields, not coupling, carry the observables) | 0.5 |

**Amendment A0 (2026-10-04 20:55 UTC, after the scheme build, before any axis–observable statistic).** H11's `cowork_excess` covers only 12 non-holdout periods. The scheme re-implements H11's definition (raw project, blocks = day × 30-min window × room, circular shift within agent-day, 20 draws) on `project_states` (`sources = all`) for all 35 periods. It reproduces H11 on the 12-period overlap (Spearman 0.93, Pearson 0.92). **Y2 is now this re-implementation (`herd_own`); H11's values are the variant.** Instrument checks seen at the same time (no axis involved): R̂ on the ledger first-use tables vs H34's table values, Spearman 0.96 (32 periods); τ_settle bge vs gte, Spearman 0.56 (27 periods: a noisy observable); loop rate either-model vs both-model flags, 0.98.

**Amendment A1 (2026-10-04 ~21:55 UTC, after the synthetic validation, before any real axis–observable statistic).** 100 runs per world at the real axis values (common sample: 32 periods; n per observable 26 / 27 / 31 / 32), 199 permutations per run (`data/processed/H51-one-dial-collapse/synthetic/summary.json`).
- **S1 size: passed.** Regime-only world: permutation rejects 4%, the per-observable D1 rule fires 2.8%; N-only world: 3% and 0%.
- **S2 power: passed for the permutation test, not for the 3/4 rule.** At ρ²_K = 0.30 the within-regime permutation test rejects in 89% (0.15: 73%; 0.50: 99%). The per-observable rule fires in only 41% of observables, and "≥ 3/4 and p < 0.05" in 18% (0.50: 46%).
- **S3 recovery: passed.** |cos(ŵ, w)| ≥ 0.8 in 98% (median 0.97). The index rule "≥ 3/4" fires in 53% of index worlds.
- **Consequence (stated before real data):** the **within-regime permutation test is the powered instrument** for the dial claim. A negative verdict needs p ≥ 0.05 there (power 0.89 at the effect that matters, so "the dial adds ≥ 30% of within-regime variance" is ruled out at that power). The count of collapsing observables is reported but cannot refute alone. P1–P3 are scored as written.

**What counts against the card's negative reading (i.e. for HH178):** P1 failing in the stated way. A collapse that survives the within-regime permutation and the regime residual would make g_lag the phase diagram's one dial.

**Per-period verdict rule (replication):** a period is *supported* if its residual from the D1 fit (leave-one-period-out) is within the 80% prediction band for ≥ 3/4 of its available observables *and* the D1 fit beats regime for those observables overall (the card-level collapse holds); *failed* if the card-level collapse does not hold for D1 and the period has ≥ 2 observables; *descriptive* if the period has < 2 observables (placed on the diagram only).

Native predictions are in `goalperiod-subhypotheses/NE14/`, `NE42/` and `G51/` (written before those runs).

## Results by goal period
Per-period rule (card). **0 supported, 32 failed, 1 descriptive** (33 non-holdout periods with all four axes; #2 and #23 lack a kickoff score). Every period with ≥ 2 observables fails because the card-level D1 collapse fails; the residual columns show where each period sits relative to the (flat) D1 fit. Key numbers: regime, N, axes, then D1 leave-one-period-out residual z for settling / herding / branching / loops.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G03](goalperiod-subhypotheses/G03/README.md) | replication | descriptive | regime I, N 4.0: g_lag 0.017 · c_× 0.1372 · S_text -0.57 · z(D1) – / – / – / 0.9 |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | failed | regime I, N 4.0: g_lag 0.011 · c_× 0.0081 · S_text 0.69 · z(D1) -0.3 / 0.9 / – / 0.4 |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | failed | regime I, N 4.0: g_lag 0.052 · c_× 0.0093 · S_text 0.43 · z(D1) -1.1 / – / 0.1 / -0.6 |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | failed | regime I, N 4.0: g_lag -0.008 · c_× 0.4375 · S_text -0.29 · z(D1) 0.8 / – / -1.7 / -0.2 |
| [G07](goalperiod-subhypotheses/G07/README.md) | replication | failed | regime I, N 4.0: g_lag 0.035 · c_× 0.0067 · S_text 0.63 · z(D1) – / – / -1.8 / -0.3 |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | failed | regime I, N 4.0: g_lag 0.005 · c_× 0.0171 · S_text -0.14 · z(D1) -1.1 / 1.2 / -1.3 / -0.4 |
| [G10](goalperiod-subhypotheses/G10/README.md) | replication | failed | regime I, N 7.0: g_lag 0.002 · c_× 0.1269 · S_text 0.06 · z(D1) -0.5 / – / -0.5 / 0.9 |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | failed | regime I, N 7.0: g_lag 0.027 · c_× 0.0142 · S_text -0.05 · z(D1) 1.7 / 3.3 / -0.1 / 1.1 |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication | failed | regime I, N 7.0: g_lag 0.039 · c_× 0.0364 · S_text 0.24 · z(D1) 1.6 / 1.8 / 0.7 / 0.8 |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | failed | regime I, N 6.0: g_lag -0.002 · c_× 0.0045 · S_text -0.15 · z(D1) -0.8 / 0.3 / -1.0 / 0.3 |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | failed | regime I, N 7.0: g_lag 0.031 · c_× 0.0125 · S_text -0.25 · z(D1) 1.3 / -0.0 / -1.8 / 0.5 |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | failed | regime I, N 7.0: g_lag 0.038 · c_× 0.0693 · S_text -0.50 · z(D1) -1.4 / 0.4 / 0.3 / 0.8 |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | failed | regime I, N 7.5: g_lag 0.048 · c_× 0.0301 · S_text -0.07 · z(D1) -0.5 / 0.6 / 1.2 / 1.5 |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | failed | regime I, N 7.1: g_lag -0.003 · c_× 0.0174 · S_text 0.02 · z(D1) -0.6 / -0.5 / 0.1 / 0.8 |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | failed | regime I, N 9.2: g_lag -0.020 · c_× 0.0237 · S_text -0.42 · z(D1) 0.4 / -0.6 / 0.6 / 0.0 |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | failed | regime I, N 8.4: g_lag -0.018 · c_× 0.0840 · S_text -0.46 · z(D1) 0.4 / 0.2 / -0.1 / 1.0 |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | failed | regime I, N 10.0: g_lag 0.009 · c_× 0.0038 · S_text 0.78 · z(D1) 1.9 / -0.5 / -1.0 / -0.2 |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | failed | regime I, N 9.8: g_lag 0.012 · c_× 0.0214 · S_text -0.68 · z(D1) -1.2 / 0.1 / -0.1 / 0.4 |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | failed | regime I, N 10.0: g_lag 0.012 · c_× 0.0317 · S_text 0.52 · z(D1) -0.3 / 1.0 / 0.4 / -0.1 |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | failed | regime I, N 10.0: g_lag 0.006 · c_× 0.0187 · S_text 0.86 · z(D1) 0.4 / -0.9 / 1.7 / -0.9 |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | failed | regime I, N 11.0: g_lag -0.005 · c_× 0.0033 · S_text -0.01 · z(D1) -0.8 / -1.0 / 1.2 / -0.8 |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | failed | regime I, N 11.2: g_lag -0.035 · c_× 0.0009 · S_text 1.25 · z(D1) 0.6 / -0.6 / 0.7 / -1.3 |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | failed | regime II, N 11.0: g_lag -0.029 · c_× 0.0190 · S_text -0.13 · z(D1) – / -1.2 / 1.2 / -1.9 |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | failed | regime II, N 12.0: g_lag 0.046 · c_× 0.0068 · S_text 0.32 · z(D1) -0.9 / -0.9 / 1.2 / -1.1 |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication (+ NE14 native) | failed | regime II, N 12.0: g_lag 0.068 · c_× 0.0065 · S_text -0.56 · z(D1) – / -0.6 / 0.2 / -2.3 |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | failed | regime III, N 12.0: g_lag 0.220 · c_× 0.0010 · S_text -0.57 · z(D1) – / 0.3 / 0.6 / -1.7 |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | failed | regime III, N 12.4: g_lag 0.066 · c_× 0.0019 · S_text 0.05 · z(D1) -1.5 / -0.8 / 0.6 / 1.0 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication (+ NE42 native) | failed | regime III, N 14.8: g_lag 0.144 · c_× -0.0055 · S_text -0.64 · z(D1) 0.1 / -0.6 / -1.9 / 1.9 |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication (+ NE42 native) | failed | regime III, N 15.0: g_lag 0.003 · c_× 0.0084 · S_text -0.18 · z(D1) 1.1 / -1.1 / 0.1 / -0.3 |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication (+ NE42 native) | failed | regime III, N 15.0: g_lag 0.189 · c_× 0.0785 · S_text 0.04 · z(D1) 0.1 / -0.3 / 0.8 / 1.0 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | failed | regime III, N 15.6: g_lag 0.154 · c_× 0.0025 · S_text -0.33 · z(D1) -0.0 / -0.6 / -0.9 / -0.7 |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | failed | regime III, N 16.8: g_lag 0.234 · c_× -0.0030 · S_text 0.03 · z(D1) – / 0.4 / 0.4 / -0.2 |
| [G51](goalperiod-subhypotheses/G51/README.md) | native + replication | failed | regime III, N 26.5: g_lag 0.142 · c_× 0.0105 · S_text 0.08 · z(D1) 1.1 / -0.5 / 0.4 / -0.4 |
| [NE14](goalperiod-subhypotheses/NE14/README.md) | native | mixed | ΔK +0.18 at fixed goal: loop Δ −0.12 [−4.4, 0.7] logit vs D1 −1.53; R̂ Δ −0.18 vs D1 −0.24, but no-step placebo +0.41 [0.15, 0.65] |
| [NE42](goalperiod-subhypotheses/NE42/README.md) | native | failed | g_lag 0.144 → 0.003 → 0.189; #40 deviations follow D1 sign 1/4, room-size sign 4/4 |

## Results
*Exploratory round 1, 2026-10-04: 33 non-holdout goal periods (regime I 22, II 3, III 8). Numbers from `data/processed/H51-one-dial-collapse/results/{collapse,perm,tests}.json`, `phase_points.parquet`, `natives/*.json`, `synthetic/summary.json`. Code: `scheme/build.py`, `analysis/h51lib.py`, `synthetic.py`, `collapse.py`, `natives.py`, `figures.py`, `write_period_folders.py`, `write_estimates.py`, `confirm.py`.*

### Headline
**No single dial collapses the phase diagram.** The read-out coupling g_lag (HH178's K, calibrated by H67) predicts none of the four unfitted observables better than regime labels or log N. Leave-one-period-out CV-R² for g_lag is −0.00 (settling), 0.03 (herding), −0.01 (branching) and 0.22 (loops). The within-regime permutation p is 0.07. The reason is physical. Every unit is subcritical (period g_lag ≤ 0.23), so mean-field amplification χ = 1/(1 − g) is at most 1.31, while observables vary ×3 (herding, branching) to ×13 (loops) and ×127 (settling) across periods. What carries information is the **scaffold regime** (loops, consensus time) and **N** (herding, branching; within-regime permutation p = 0.002).

### Outcome vs prediction
| # | Prediction | Observed | Outcome |
| --- | --- | --- | --- |
| S1 | size ≤ 10% | permutation 4% (regime world), 3% (N world); D1 rule 2.8% / 0% | passed |
| S2 | power ≥ 80% at ρ²_K 0.3 | permutation 89%; 3/4-count rule 18% (demoted, A1) | passed (permutation) |
| S3 | index recovery | \|cos\| ≥ 0.8 in 98% | passed |
| P1 | g_lag collapses ≤ 1/4, permutation p ≥ 0.05 | 0/4; p = 0.073 | **supported** (HH178 fails) |
| P2 | single index collapses ≤ 2/4 | 0/4 (index ≈ log N; CV-R² ≤ 0.24); index permutation p = 0.044 | **supported** |
| P3 | g_lag within ±0.05 of regime on ≥ 3/4 | 2/4; g_lag is *worse* than regime on herding (−0.27) and loops (−0.10) | failed |
| P4 | ρ(R̂, g_lag) > 0 within regime III | −0.40 [−0.86, 0.42] (n 8); all periods −0.22 | failed |
| P5 | settling does not fall with K (ρ ≥ −0.2) | +0.05 [−0.34, 0.42] (n 27) | **supported** |
| P6 | field-only rival beats g_lag on ≥ 2/4 | 1/4 (herding); field CV-R² ≤ 0.06 everywhere | failed |
| P7 | equal-time dial no better than g_lag | 4/4 (g_eq ≤ g_lag + 0.05) | **supported** |

### Findings
1. **The coupling axis is not a collapse variable.** Adding g_lag to regime labels changes CV-R² by −0.13 (settling), +0.03 (herding), +0.00 (branching) and +0.10 (loops). The quadratic term does not help (K²: ≤ 0.20).
2. **N is the informative axis beyond regime.** log N alone gives CV-R² 0.38 for herding (bigger swarms herd less: ρ −0.75), and regime + log N gives 0.19 for branching. The fitted single index puts weight 0.86–0.95 on log N in every leave-one-observable-out fit. It still fails the collapse rule, because no index fits loops (regime) and herding (N) at the same time.
3. **The field gauges add nothing at period level.** c_× (trimmed) and the kickoff specificity S_text give CV-R² ≤ 0.06 (field rival), and φ in place of c_× changes nothing. Trimmed c_× is small (median 0.012) and does not separate periods.
4. **Settling time is unpredicted by every axis** (best CV-R² 0.02). τ_settle is noisy: bge vs gte agree only at ρ 0.56.
5. **Loops are an era variable, not a coupling response.** The loop rate falls from 17% (regime I median) to 3–5% (II, III). The across-period D1 slope (−8.3 logits per unit g) predicts a −1.5 logit drop at NE14's coupling switch-on; the observed drop at fixed goal and roster is −0.12.
6. **Natives agree.** NE42: where coupling falls and room size doubles, the observables follow room size (4/4 signs). G51: at flat g_lag, R̂ rises with N (ρ 0.83 [0.50, 0.95]) and herding falls (ρ −0.51).

### Proposed phase-diagram axes (for the dashboard and GOALS.md)
- **x = N** (H85 active population, log scale): the only continuous axis with within-regime predictive value.
- **y = g_lag** (H67): keep it as the coupling coordinate. It is calibrated and field-free, but it is ≈ 0 outside regime III, so it does not order periods within regime I.
- **marker = regime** (scaffold): carries the largest share of loop and consensus variation.
- **field:** report c_× (H86, trimmed) as an impostor gauge per unit, not as a phase axis (no predictive value here). Kickoff S_text likewise.
- Figure: `figures/phase_diagram.pdf` (N vs g_lag; c_× vs g_lag).

### Post hoc (labelled; after the first real-data pass)
- **Within regime III (8 periods), herding rises with g_lag** (ρ +0.83, p 0.01; the equal-time dial +0.74) and loops fall with it (ρ −0.71, p 0.05). These are 2 of 48 rank tests (6 axes × 4 observables × 2 scopes), so about 2 would pass at p < 0.05 by chance. Lead for round 2: a regime-III-only collapse with more units (sub-units of #38 and #51).
- The single index's within-regime permutation p is 0.044 (dominated by log N); the index still collapses 0/4 observables by the card's rule.

### Caveats
- Units are periods (n 27–33 per observable, 8 in regime III). The 3/4-count rule is underpowered; the negative rests on the permutation test (power 0.89 at ρ²_K 0.30) and on CV-R² point values.
- Synthetic runs used the 32-period sample built before the #4 NaN fix; the real run has 33 periods.
- Observables are not impostor-clean at period level: herding share is not placebo-corrected for convergence; loop rate depends on model family (shared priors); roster composition differs across periods.
- g_lag in regime I is measured on the wrong clock for talk (H67 caveat), so "K ≈ 0 in regime I" means "no hop-1 read-out coupling".
- G51's N sweep is confounded with calendar time.
- Not blind: the H67, H86, H85, H54, H48, H34 and H11 headlines were known before the predictions.

## Round 2 redirects
- **What the direction is really after:** a low-dimensional phase diagram an operator can read. Round 1 says two coordinates (scaffold regime, N) carry what is predictable; coupling is a small correction.
- **H51-R1. Regime-III collapse with sub-units.** Use the units of #38, #44 and #51 (and the holdout's #43, #45–#50 at confirmation) to test the post hoc herding–g_lag relation with ≥ 20 points.
- **H51-R2. Size law per observable.** Fit Y = Y₀ N^β within regime with H85's machinery (herding, branching), and test whether β is the same across regimes (a two-axis scaling form F(regime, N)).
- **H51-R3. Impostor-clean observables.** Rebuild herding with an in-flight (posted-but-unread) control and loops with `style_resid` / family controls before any further collapse test.

## Notes
- 2026-10-04 20:40 UTC: card and predictions written before any collapse statistic. 20:45: native predictions written. 20:55: A0 (herding re-implementation). ~21:55: A1 after the synthetic run (100 runs × 6 worlds, ~10 min, 2 workers). ~22:00: real run (collapse ~1 min). ~22:05: #4 NaN pooling fix (H86's 4b gauge is NaN), rebuilt; results changed by ≤ 0.03 in CV-R².
- Data: `data/processed/H51-one-dial-collapse/` (240 kB).
- `confirm.py` frozen (`results/frozen_model.json`, SHA-256 of the script) and dry-run on in-sample stand-ins (#24, #27, #42, #44; scratch output; C1/C2 "fail" there because the stand-ins are in the fit). It needs H67's confirmatory g_lag rows first.
- Proposed for `physics-models/DEFINITIONS.md` (not edited): *phase-diagram axes (h, K, N)*, *one-dial collapse* (LOPO CV-R² rule and within-regime permutation null), *loop rate (restatement share)*.
- 2026-10-04 20:40 UTC: round 1 started. Compute: local, polars/BLAS capped at 2 threads, pool ≤ 2 workers, one job at a time (STANDARDS §9).
- 2026-10-04 (coordinator, before the card): H86's Taylor c_T and b are not field gauges; use c_× (`taylor_c_shared`, `activity_trim`) and φ. H85: talk is sublinear in N (β_msg 0.33; regime III 0.77); addressing per message rises with N (slope 0.79).
