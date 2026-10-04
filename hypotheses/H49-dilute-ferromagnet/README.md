# H49: Edge-trimmed regime III is a dilute ferromagnet

**Status:** exploratory round 1 done (2026-10-04); confirmatory script frozen and dry-run, not run. Predictions written 2026-10-04 05:50 UTC, before any real-data coupling statistic. **Headline: refuted as posed. After day-edge trimming, regime III has no small coupled clusters: its bonds are at the false-positive floor, and the surviving excess is a weak, structureless shift shared by all pairs (a dense / shared-field mode, not a dilute ferromagnet).**
- **Bonds at the floor.** After H38's day-edge trimming, the 23 regime-III units hold 38 significant positive bonds over 4,318 pairs, against ≈ 23 expected false (1 per unit by construction); before trimming there are 99. The bond graph is below percolation everywhere. That is trivial for the small units, but not for #51, where the synthetic shows that strong bonds and percolation would have been detected.
- **The surviving excess is spread, not concentrated.** It is significant in 10/23 units, including #44 and the #51 head. There, every pair is shifted a little (mean bond z +0.14 to +0.49) and the top 10% of pairs carry a median 11% of it (CV-C10; planted dilute swarms give 0.44 / 0.31 / 0.65, planted dense ones 0.16 / 0.11 / 0.13). Bond z has no split-half reliability (r ≈ 0), and bonds don't recur between adjacent #51 units (r 0.02). The dense rival is favored over the dilute model by a summed log-likelihood ratio of +22.5.
- **Ground truth doesn't light up.** #44's fine-tuning team is not a bond cluster in activity (label-set p 0.26). It is one in talk (p 0.013). No same-lab (provider-outage rival), rival-role or opposed-pair enrichment.
- **NE43 corrected and used.** The daily bookend messages stop after 08-04, not 08-21. The edge-induced excess persists without them (×0.77, then ×0.93 after the nudges stop too): H38's day-edge drive is the operator's start/stop schedule, not the announcement.
- **Regime-I contrast as predicted:** trimming removes a median 17% of bonds there vs 67% in regime III. Post hoc, regime III's per-pair excess does not fall with headcount, which is H25's shared-field signature.
- **Pair structure, where it exists, is in talk:** 71 significant talk bonds vs ≈ 23 expected in regime III, partly reproducible across #51 units (r 0.14).
**Fields:** stat mech (inverse Ising, percolation), sociophysics, network science
**Literature:** none in `literature/`. Standard references (cited, not stored): Aurell & Ekeberg, *PRL* 108, 090201 (2012) (pseudolikelihood inverse Ising); Nguyen, Zecchina & Berg, *Adv. Phys.* 66, 197 (2017); Molloy & Reed, *Random Struct. Alg.* 6, 161 (1995) (giant component of the configuration model).
**Definitions used:** Agent; Population N(t), variant *present population* (H02 rule, per unit); Regime; Driving / external field; **Agent-state conditioning** (H38 named variant, set `mask_scaffold`); Per-pair correlation ρ̄ (H25 named variant). New named variants proposed for `physics-models/DEFINITIONS.md` (not edited here; outside H49's scope): *conditioned pseudolikelihood bond*, *significant-bond graph*, *excess-covariance concentration (CV-C10)*, defined under Model.
**From:** HH159 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` (related: HH73) · **Models:** `physics-models/01-inverse-ising/`
**Data inputs (shared tables first):** `activity_bins_fixed`, `outages_fixed/reasons`, `outages_fixed/stall_minutes` (Amendment 2; the original `activity_bins` / `reasons` / `stall_minutes` were used in a superseded first pass), `period_units`, `calendar`, `roster`, `ground_truth_labels`, `kicks_classified` (all `data/processed/shared/`). Read-only imports: H02 `h02lib.block_ids` (30-min blocks) and H38 `h38lib` (`MASK_SETS`, `impute`, `block_suff`, `cw`, used to verify that the conditioned covariance reproduces H38's `mask_scaffold` gain).

## Question
Once day-edge co-activation is removed, is the remaining regime-III coupling concentrated in a few strong pairs, with a significant-bond graph below percolation: small coupled clusters in a paramagnet?

## Design: two layers (Vivian, 2026-10-04; see `infra/data-quality/QUEUE.md`)
- **Replication:** the common estimator on every eligible period unit of regime III (the hypothesis) and regime I (the contrast). Period README role: `replication`. Templated predictions, labelled as such.
- **Period-native tests:** four tests whose setup gives special leverage, each with its own observable, null, ground truth or intervention and its own dated prediction. Period README role: `native`.
  - **NE43** (inside #51): a test of H38's adjustment itself.
  - **#44**: the `#best` fine-tuning team (ground truth) and the leader checkpoints.
  - **#51 head**: where the strong bonds should live; rival pairs, rooms and labs as ground truth.
  - **NE14** (regime II → III): do the bonds persist across the scaffold change?

## Model
**From:** `physics-models/01-inverse-ising/` (pairwise maximum entropy, pseudolikelihood inference), with a percolation reading of the inferred bond graph.

- **Spin.** s_i(t) = +1 if agent i is active in 1-min bin t (`activity_bins.state ≥ 3`), else −1 (H02's spin). Talk spin (state = 4) is a secondary.
- **Equilibrium model per unit.** P(s(t) | b) ∝ exp[Σ_i δ_i(b) s_i + Σ_{i<j} J_ij s_i s_j], with δ_i(b) a per-agent field in each (day, 30-min block) b (H02's block field, which absorbs schedule, goal kickoffs and rate drift).
- **Conditioned pseudolikelihood bond (primary, "PL-c").** H38's agent-state conditioning carried into the pseudolikelihood:
  1. drop off-schedule minutes (`stall_minutes.scheduled`);
  2. an agent-minute is *unavailable* if the agent is silent with a scaffold reason (`reasons`: not started, finished, infrastructure-error gap, consolidating; H38's `mask_scaffold`);
  3. predictors are block-centered spins, x_j(t) = s_j(t) − m_j(b) if available, else 0 (the block mean over available minutes, i.e. H38's imputation);
  4. agent i's conditional likelihood uses only its available minutes in blocks where it is not constant:
     logit P(s_i(t) = +1 | rest) = 2[δ_i(b) + Σ_{j≠i} J_ij x_j(t)].
  - Fit per agent by L2-penalized logistic regression (λ = 1 on 2J, H02's convention), δ_i(b) unpenalized, by block-coordinate Newton. Symmetrized bond J_ij = (J_ij + J_ji)/2.
  - Equal-time, so undirected: the object is H38's equal-time co-activation and an undirected bond graph for percolation. Kinetic Ising is not used; H02 found lagged pairwise couplings at null level, and the hypothesis is about the equal-time excess H38 measured.
- **Variants.** PL-r (raw: no minutes dropped, no conditioning; = H02's EQ-PL with block field); PL-e (edge only: scheduled dropped, not-started / finished unavailable).
- **Conditioned covariance (link to H38).** C̄_ij = Σ_t x_i(t) x_j(t) / Σ_b n_b over blocks with ≥ 5 kept minutes. Then VR = Σ_ij C̄_ij / Σ_i C̄_ii is exactly H38's `mask_scaffold` variance ratio, and VR − 1 = Σ_{i≠j} C̄_ij / Σ_i C̄_ii decomposes the collective co-activation over pairs.
- **What "dilute ferromagnet" predicts.**
  - Most excess bonds ΔJ_ij ≈ 0; a few large and positive.
  - The excess covariance is concentrated on those few pairs.
  - The graph of significant positive bonds has mean degree < 1 and Molloy–Reed κ = ⟨k²⟩/⟨k⟩ < 2: no giant component in a configuration model with the same degrees.
  - The swarm is a set of small clusters (pairs, triangles) in a paramagnet.
- **Rival models.**
  - **R1, dense weak ferromagnet (Curie–Weiss / shared field; H02-MF, H25).** Every pair carries a small excess: the z distribution shifts as a whole, no heavy tail, the concentration index sits near its uniform value (0.1).
  - **R2, provider field.** Agents of the same lab stall together when their provider is slow (H38's untested rival; API failures leave no log line). Bonds would be same-lab pairs: infrastructure, not coupling.
  - **R3, percolating ferromagnet.** Many moderate bonds, a giant component.
  - **R4, pure paramagnet.** No bonds beyond the false-positive count.

## Data scheme (`scheme/`)
- **Inputs:** shared `activity_bins_fixed` (pt_date, minute, agent, state; the DQ8 join fix, Amendment 2), `outages_fixed/reasons` (silence reason codes: 0 none, 1 pre, 2 post, 3 infra_err, 4 consol, 5 pause; H38's rule rebuilt from the fixed bins), `outages_fixed/stall_minutes` (scheduled), `period_units`, `calendar` (holdout), `roster` (lab), `ground_truth_labels` (#44 rooms and checkpoints; #51 rival / opposed pairs, rooms), `kicks_classified` (nudge targets).
- **Transform:** `scheme/build_units.py`.
  - Eligible units: non-holdout `period_units` with ≥ 2 days, regime III (hypothesis) or I (contrast), and ≥ 6 present agents. The holdout is masked twice (`calendar.holdout` and `infra/shared/common.py: holdout_mask`), with assertions.
  - Present population (H02 rule): an activity-bins row on every day of the unit and ≥ 30 active minutes.
  - Dense per-unit matrices, in (day, minute) order: activity spin, talk spin, reason code, day index, minute, scheduled flag.
  - Native windows (fixed populations): NE43 W1/W2/W3, #44 merged, NE14 sides.
- **Output:** `data/processed/H49-dilute-ferromagnet/`:
  - `units.parquet`;
  - `mats/<unit>.npz` (int8 matrices);
  - per-unit results in `<group>/<unit>.json` + `bonds/<unit>.parquet` (one row per pair, variant and channel);
  - `unit_table.parquet`, `outcomes.json`;
  - `unit_table_buggybins.parquet` + `units_buggybins.parquet` (the superseded run on the original bins, kept for comparison);
  - `synthetic/`, `native/`;
  - `_provenance.json`.
- **Regimes covered:** III (2026-03-24 → 2026-09-06, non-holdout) and I. Regime II only inside NE14.

## Observables
Per unit, for PL-c (and PL-r, PL-e; talk as a secondary):
- **O1. Bond z-scores.** z_ij = (J_ij − mean_null) / sd_null over B = 200 block-shift surrogates. Excess bond ΔJ_ij = J_ij − mean_null.
- **O2. Significant bonds against a calibrated null.** Each surrogate's pairs are z-scored against the other surrogates (leave-one-out). Pooled over pairs and surrogates, they give the null distribution of z and empirical one-sided p-values.
  - A positive bond is significant if p < 1/n_pairs, i.e. ≈ 1 expected false bond per unit; negative bonds use the other tail.
  - Secondary: BH q = 0.1 on the same empirical p-values.
  - Calibration (size) is checked on synthetic swarms (axis F).
- **O3. Bond distribution.**
  - Mean z (dense shift), skewness and excess kurtosis of z, each against its surrogate distribution;
  - π₁ = 1 − π₀ (Storey, λ = 0.5);
  - **CV-C10:** the share of the excess covariance Σ_{i<j} ΔC̄_ij carried by the top 10% of pairs. Pairs are ranked on even 30-min blocks and the share is measured on odd blocks, and vice versa; the two are averaged. Cross-validation removes the selection bias of ranking and measuring on the same noise. Uniform coupling gives ≈ 0.1. Scored only where the conditioned collective excess is significant.
- **O4. Percolation.** On the significant positive-bond graph:
  - mean degree ⟨k⟩ (ER threshold 1);
  - Molloy–Reed κ = ⟨k²⟩/⟨k⟩ (configuration-model threshold 2);
  - largest-component fraction S₁ = |LCC|/N vs its configuration-model expectation (same degrees);
  - component sizes.
- **O5. Collective context (H38 link).** g = 1 − 1/VR raw / edge / conditioned, excess E over the same surrogates; raw → conditioned loss of significant bonds.
- **O6. Day-block bootstrap** (200 replicates; whole days when the unit has ≥ 4 days, half-day blocks otherwise): CIs for bonds, κ, S₁, CV-C10, mean z. Bootstrap z uses the original null mean and sd.

## Null / baseline
- **N1 joint block shift** (H02/H38): each agent's (spin, reason) series is circularly shifted within each (day, 30-min block), the same shift for both, and every step (scheduled drop, availability, centering, fit) is recomputed. This keeps each agent's half-hour rates, autocorrelation and own scaffold-state process, and destroys cross-agent alignment.
- **Calibration:** the size of the bond test is measured on synthetic swarms with real schedules and real scaffold masks. H37 found sign-shuffle and FDR nulls anti-conservative, so the per-pair threshold comes from the pooled surrogate z distribution, not from a normal approximation.
- **Dense-weak rival (R1)** and **pure paramagnet (R4)** are simulated in the synthetic validation, at village sampling.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R1 dense weak ferromagnet (Curie–Weiss / shared field); R2 provider field (same-lab stalls); R3 percolating ferromagnet; R4 pure paramagnet.
**Locked holdout used for confirmation:** units 45a, 45b, 47, 49 and 51m (the #51 tail, 09-07 →) for regime III; 14, 15b, 22a, 22b for regime I. `analysis/confirm.py`, frozen and dry-run, not run.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Spins, availability masks, off-schedule minutes and pair labels all come from logged fields (fixed activity bins, scaffold reasons, operator messages, ground-truth labels); assumptions listed under Model. Not invariant across regimes: consolidation masks exist only in regime III, and "active" means different things under sessions (I) and perma-computer-use (III). |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Within-block stationarity and each agent's autocorrelation are built into the joint block-shift null, which recomputes every step. Equal-time pseudolikelihood assumes stationarity within blocks and ignores delays (the main blind spot, Caveats). No Markov-order or time-rescaling test. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | The bond test is calibrated (synthetic size 0.054–0.062; ≈ 1 false bond per unit, also internally). Regime-III conditioned bonds pooled are 38 vs ≈ 23 expected, but they don't recur across units. What beats the null is a uniform shift (mean bond z significant in 13/23 units), i.e. the rival. No held-out likelihood. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | Unfitted signatures tested: CV-C10, z skewness, split-half bond reliability, cross-unit recurrence, team share. The dilute signature is absent (P2, N44c, N51a failed). P5 (trimming removes bonds in III, not I) held. |
| E interventional | predicts the change across a natural experiment | 1 | NE43: correctly predicted that the edge drive survives the end of the bookend messages (schedule, not message), which supports H38's mask; the bond-invariance prediction was not evaluable (no reliable bonds). NE14: the raw jump is a uniform shift, not new bonds (N14a failed as written). |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Calibrated at the real schedules and masks, including 70% marker recall. Dense vs dilute separates when the excess is significant. But individual bonds need J ≳ 0.5 and ≥ 5 days (recall 0.47 / 0.34 / 0.89), and percolation of moderate bonds is not identifiable (SP4: 0.13 / 0.00 / 0.77). Robust to the data-bug rebuild (no verdict changed). |
| G ground truth | agrees with known structure | 0 | The known #44 fine-tuning team is not a bond cluster in activity (p 0.26; 0 bonds). It is one in talk (p 0.013), outside the model's spin. No rival, opposed or same-lab enrichment in #51. (Instrument check: H38's G40 gain was reproduced exactly on the old bins.) |
| H comparative | beats the named rivals | 0 | Loses to R1 (dense / shared field): CV-C10 bands give a summed log-likelihood ratio of +22.5 for dense over dilute, and pair reliability ≈ 0. R2 (provider field) rejected (same-lab OR 0.50–0.62). R3 not supported. R4 (pure paramagnet) describes the 13 units without excess. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Bonds don't transfer between adjacent units of the same period (#51 r 0.02; NE43 windows r ≤ 0.11; NE14 r −0.03). Holdout not run (`confirm.py` frozen). |

## Prediction
*Written 2026-10-04 05:50 UTC, before running the analysis on real data.*
- **Real data seen so far:** table schemas; the `period_units` list (days, roster sizes); `ground_truth_labels` kinds for #44 and #51; the counts of nudge targets in #51; and the dates of the automated messages.
  - The 28-character daily pause/resume bookend messages stop after **2026-08-04**, not 08-21 as NE43 states. Nudges stop on 08-20.
  - The day windows still run about 16:01 → 00:05 UTC every day after both dates (`stall_minutes` first and last minute per day).
- **Not blind to:** H02 (pairwise J at null level; collective mean-field coupling in regime-III mode C), H38 (f_scaffold 0.68 in regime III, 0.11 in regime I; #44 and #51 keep their excess), H25 (ρ̄ flat in N for content).

**Synthetic (axis F; `analysis/synthetic.py`).** Glauber (heat-bath) swarms at the real schedules of three units (#40, #44b, #51d: real day lengths, block fields fitted to real rates, real scaffold masks forced off, real off-schedule minutes). Planted structures: none (R4), dilute strong bonds (3–6 pairs or triangles at J = 0.25–0.5), dense weak uniform J (R1), percolating Erdős–Rényi (mean degree 3, J = 0.3; R3). Marker recall 1 and 0.7.
- **SP1 (calibration).** With no bonds, the PL-c positive-tail rejection rate at per-pair α = 0.05 is in [0.03, 0.07]. False bonds at the graph threshold average ≤ 1.5 per unit. The percolation verdict is "below" in ≥ 95% of replicates. PL-r on the same data has a rejection rate ≥ 0.10 (the edge drive fakes bonds).
- **SP2 (dilute recovery).** Planted strong bonds are recovered at the graph threshold with recall ≥ 0.8 and precision ≥ 0.8 (at J = 0.5; reported for 0.25). CV-C10 ≥ 0.5. Verdict "below percolation" in ≥ 90%.
- **SP3 (dense rival).** Dense weak coupling gives CV-C10 ≤ 0.25 and a significant mean-z shift. "Heavy tail" (skewness above the null's 95% quantile and CV-C10 ≥ 0.4) in ≤ 10% of replicates. Expected limitation, stated now: the significant-bond graph of a dense weak ferromagnet also looks sub-percolating (bonds individually undetectable). That is why the verdict needs O3, not O4 alone.
- **SP4 (percolating).** κ ≥ 2 and S₁ ≥ 0.5 detected in ≥ 80% of replicates.
- **SP5 (recall 0.7).** SP1's PL-c rejection rate stays ≤ 0.10.

**Real data, replication layer (templated; per-unit verdicts in the G folders).** Eligible regime-III units (PL-c, activity):
- **P1 (dilute).** Median fraction of pairs with a significant positive bond ≤ 5%, and mean degree ⟨k⟩ < 1 in ≥ 2/3 of units.
- **P2 (heavy tail).** In units whose conditioned collective excess is significant (z > 2), CV-C10 ≥ 0.4 in ≥ 2/3, and z skewness above its null's 95% quantile in ≥ 1/2.
- **P3 (below percolation).** κ < 2 and S₁ ≤ 0.3 in ≥ 2/3 of units. Clusters are mostly pairs and triangles (≥ 80% of non-singleton components have ≤ 3 agents).
- **P4 (where).** #44 and #51 units have per-pair significant-bond rates above the regime-III median.
- **P5 (trimming removes bonds in III, not in I).** Raw → conditioned, the count of significant positive bonds falls by ≥ 50% (median over regime-III units) and by ≤ 25% in regime I.
- **P6 (regime I, descriptive).** Regime-I graphs are also below percolation (H02: pairwise bonds at null level). Reported, not scored.
- **Per-unit verdict rule (fixed now):**
  - **supported:** at least 4 significant positive bonds (P(≥ 4 | 1 expected) ≈ 0.02), κ < 2, S₁ ≤ 0.3, and, where the conditioned excess is significant, CV-C10 ≥ 0.4.
  - **failed:** κ ≥ 2 or S₁ > 0.3 (percolating), or a significant conditioned excess with CV-C10 ≤ 0.2 (dense).
  - **mixed:** otherwise. This includes a pure paramagnet (≤ 3 positive bonds): sub-percolating, but without the coupled clusters H49 claims.
  - A period's verdict is the majority over its units; a tie is mixed.

**Native layer (own predictions, restated in each folder).**
- **NE43 (#51, schedule vs message).** Fixed population over W1 = 07-27 → 08-04 (bookends on, nudges on), W2 = 08-05 → 08-20 (bookend messages off, nudges on), W3 = 08-21 → 09-04 (both off). The operator's start/stop continues, so H38's day-edge drive should persist.
  - **N43a.** The edge-induced excess E_raw − E_edge in W2 and W3 is ≥ 0.5 × its W1 value. The message-drive reading (the brief's premise) predicts < 0.3×.
  - **N43b.** Conditioned bonds unchanged: the disattenuated W1 ↔ W3 correlation of bond z is ≥ 0.5, and the per-pair significant rates are within a factor of 2.
  - **N43c (co-kicks).** Pairs named together in a nudge have higher conditioned bond z than other pairs while the nudger runs (Δz ≥ 0.3), and the gap halves after 08-21. A spurious common-kick bond would weaken the coupling reading.
- **#44 (team ground truth).** Fixed population over the 4 days; the leader agent is excluded.
  - **N44a.** The six `#best`-team pairs have mean conditioned z ≥ 2, above #rest pairs (label-permutation p < 0.05), and ≥ 2 of them are significant bonds.
  - **N44b.** The team forms one connected cluster of the significant graph while #rest is mostly isolated (S₁ ≤ 0.3 overall).
  - **N44c.** The six team pairs carry ≥ 30% of the conditioned excess covariance (they are 5% of pairs).
  - **N44d.** Dropping ±30 min around the five checkpoint starts lowers the team's mean z by < 50% (ongoing coordination, not a checkpoint-event field).
- **#51 head (where the bonds live).**
  - **N51a.** Bonds are pair properties: across adjacent #51 units, the median correlation of bond z over common pairs is ≥ 0.3. A significant bond has z > 1 in the next unit ≥ 60% of the time.
  - **N51b (coupling vs provider field).** H49's coupling reading predicts significant bonds enriched on rival (same-role) and same-room pairs. R2 predicts same-lab enrichment (OR > 2) that the role and room labels don't explain. Stated expectation: R2 wins (same lab, OR > 2).
  - **N51c.** #51 units are below percolation (κ < 2) despite N = 21–32.
- **NE14 (regime II → III; transition exception c).** II side = #35 + #36a; III side = #36b + #36c + #37 (as in H38's NE14); fixed population.
  - **N14a.** Raw significant bonds rise across the boundary; conditioned bonds rise by ≤ half as much.
  - **N14b.** Conditioned bonds persist: disattenuated cross-boundary correlation of z ≥ 0.5, and ≥ 50% of significant bonds on either side have z > 1 and the same sign on the other.

**What counts against H49.**
- A percolating conditioned bond graph.
- Or a significant conditioned excess spread uniformly over pairs (CV-C10 ≤ 0.2: R1).
- Or no bonds beyond the false-positive count anywhere, including #44 and #51 (R4: H38's surviving excess would then be collective, not pairwise).
- Or strong bonds that are same-lab stalls (R2).

### Amendment 1 (2026-10-04, after the first real-data run of all 52 units; disclosed)
- **CV-C10 is computed as a pooled ratio:** (Σ top-decile excess, both directions) / (Σ total excess, both directions), instead of the mean of the two per-direction ratios.
- **Why:** the per-direction ratio blows up when one half's total excess is near zero. G44_all read −4.3 in one direction even though its excess has z = 8.
- **Effect:** the original definition is kept as `cv_c10_orig` and reported. Of the regime-III units with a significant excess, none reaches 0.4 under either definition, so P2's verdict does not depend on the change. Synthetic results use the pooled form.

### Amendment 2 (2026-10-04, data bug, DQ8)
- **The bug:** `activity_bins` silently dropped about half of all events (a join-key mismatch), and `reasons` / `stall_minutes` were built from it.
- **The fix:** everything was rebuilt from `activity_bins_fixed` and the rebuilt `outages_fixed/{reasons,stall_minutes}` (same H38 rule), and rerun: units, synthetic templates, native tests.
- **Old vs new (replication units):**
  - regime III: 26 → 38 significant positive conditioned bonds; raw 77 → 99; units with a significant excess 11 → 10;
  - CV-C10 median in those units 0.11 → 0.11, none ≥ 0.4 either way;
  - regime-I bonds 62 → 84; the regime-I loss under trimming 0 → 17%;
  - 7 of 46 replication-unit verdicts changed (13, 21a, 30b, 39, 40, 44b, 51h; also the native window NE14_II); z of the conditioned excess correlates 0.87 old vs new.
  - The largest single change: G40's conditioned excess goes from 0.107 (z 2.4) to 0.020 (z 0.6). On the fixed bins all of G40's excess is day edge.
- **No prediction's verdict changed.** The native tests were run only on the fixed bins.
- **Lost check:** H38's G40 gain was reproduced exactly on the old bins (raw 0.349955, edge 0.136883; scaffold within 4e-4, because H38's block means include off-schedule minutes). On the fixed bins, H38's own numbers will change (DQ7).

### Amendment 3 (2026-10-04, before the synthetic battery and before any real-data run)
- The dense rival's synthetic coupling was set to J = 1.2/N. That gives a conditioned g of 0.25–0.38, the range H38 reported for the units with surviving excess (#44, #51).
- J = 0.4/N (the first smoke-test value) gave an excess too small to be significant.

## Results by goal period
<!-- PERIOD_TABLE -->
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [NE14](goalperiod-subhypotheses/NE14/README.md) | native | mixed | raw excess gain rises II → III (0.20 → 0.32) but raw significant bonds don't (6 → 4); conditioned excess falls (0.19 → 0.05); bond z has no split-half reliability on either side (r −0.05, −0.10) and no cross-boundary correlation (r −0.03) |
| [NE43](goalperiod-subhypotheses/NE43/README.md) | native | mixed | edge-induced excess W1 0.169 → W2 0.130 (×0.77 [0.49, 1.40]) → W3 0.157 (×0.93): the drive is the schedule, not the message; split-half bond reliability ≈ 0 in every window (no pair structure to persist); co-nudged pairs Δz +0.58 (p 0.0005) while nudges run, +0.20 after |
| [G44](goalperiod-subhypotheses/G44/README.md) | native | failed | #best team pairs mean conditioned z 0.76 (label-set p 0.26), 0 significant team bonds, share of excess 10% for 5% of pairs; the whole swarm is shifted (#rest–#rest pairs 0.56; g 0.47, z 8.0); the team shows up only in talk (p 0.013) |
| [G51](goalperiod-subhypotheses/G51/README.md) | native | failed | 9 units: 24 significant + bonds / 3,023 pairs (≈ 9 false expected), κ ≤ 1.6 everywhere; conditioned excess z 2.7–10 in 7 units but CV-C10 0.08–0.22 (dense); bonds don't recur (adjacent-unit r median 0.02); no same-lab, rival or opposed enrichment |
| [G10](goalperiod-subhypotheses/G10/README.md) | replication | mixed | 10a: 6/21 bonds, κ 2.0, z_g 5.1; 10b: 1/21 bonds, κ 1.0, z_g -0.3 |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | failed | 11: 5/21 bonds, κ 1.8, z_g 5.1 |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication | failed | 12a: 5/21 bonds, κ 1.8, z_g 4.5 |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | failed | 13: 5/15 bonds, κ 2.2, z_g 2.5 |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | failed | 16: 8/21 bonds, κ 2.8, z_g 5.8 |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | failed | 17: 7/21 bonds, κ 3.1, z_g 3.9 |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | failed | 18a: 7/21 bonds, κ 2.7, z_g 3.6; 18b: 4/28 bonds, κ 1.2, z_g 4.3; 18c: 3/21 bonds, κ 2.0, z_g 1.6 |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | failed | 19a: 4/21 bonds, κ 2.0, z_g 4.3 |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | mixed | 20a: 1/28 bonds, κ 1.0, z_g -0.1; 20c: 0/36 bonds, κ 0.0, z_g -0.1; 20d: 0/45 bonds, κ 0.0, z_g 1.5 |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | failed | 21a: 2/28 bonds, κ 1.5, z_g -0.6; 21b: 6/36 bonds, κ 2.3, z_g 4.0 |
| [G23](goalperiod-subhypotheses/G23/README.md) | replication | mixed | 23: 1/45 bonds, κ 1.0, z_g -0.5 |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | mixed | 24: 1/45 bonds, κ 1.0, z_g -1.3 |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | mixed | 25: 1/45 bonds, κ 1.0, z_g 1.2 |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | failed | 26: 8/45 bonds, κ 2.5, z_g 8.2 |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | failed | 27: 4/45 bonds, κ 2.5, z_g 2.0 |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | supported | 30b: 4/55 bonds, κ 1.2, z_g 1.7 |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | mixed | 31a: 1/55 bonds, κ 1.0, z_g 1.8 |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | mixed | 36b: 1/66 bonds, κ 1.0, z_g -0.1; 36c: 0/66 bonds, κ 0.0, z_g 0.5 |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | mixed | 37: 1/66 bonds, κ 1.0, z_g 1.0 |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | mixed | 38a: 0/66 bonds, κ 0.0, z_g 0.8; 38b: 1/66 bonds, κ 1.0, z_g 0.8; 38d: 1/78 bonds, κ 1.0, z_g -0.2; 38e: 2/91 bonds, κ 1.0, z_g 5.0 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | mixed | 39: 1/105 bonds, κ 1.0, z_g 1.7 |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | mixed | 40: 3/105 bonds, κ 1.3, z_g 0.6 |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | mixed | 41: 1/105 bonds, κ 1.0, z_g 2.8 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | mixed | 42a: 0/105 bonds, κ 0.0, z_g 1.4; 42b: 1/120 bonds, κ 1.0, z_g 0.9 |
<!-- /PERIOD_TABLE -->

## Results
Scripts:
- scheme: `scheme/build_units.py`;
- pipeline: `analysis/h49lib.py` (fitter, surrogates, statistics), `analysis/run_unit.py` (per unit), `analysis/native.py` (the four native tests), `analysis/summarize.py` (scoring, figures), `analysis/figures_native.py`, `analysis/write_period_folders.py`;
- method check: `analysis/synthetic.py`;
- holdout: `analysis/confirm.py` (not run).

Data: `data/processed/H49-dilute-ferromagnet/` (`unit_table.parquet`, `outcomes.json`, `bonds/`, `native/`, `synthetic/`).

Every unit got 200 joint block-shift surrogates and 200 day-block bootstraps; all numbers use the fixed bins (Amendment 2).

**1. Synthetic validation (axis F; `figures/synthetic.png`).** 30 replicates × 7 conditions × 3 real schedules (#40: N 15, 5 days × 4 h; #44b: N 17, 2 days; #51d: N 26, 5 days × 8 h), 100 surrogates each.
- **Calibrated null.**
  - With no bonds, the conditioned per-pair positive-tail rejection rate at α = 0.05 is 0.054–0.062 (target 0.03–0.07).
  - The graph threshold leaves 1.200–1.333 false bonds per unit, and the verdict is "below percolation" in 0.967–1.000 of replicates.
  - The same holds at 70% marker recall (0.055–0.061).
  - Without conditioning, the day edges fake bonds: raw rejection rate 0.085–0.170, and 1.667–5.600 raw "bonds" per unit vs 1.200–1.333 conditioned.
- **Power is the limit.**
  - Planted strong bonds (J = 0.5) are recovered with recall 0.47 / 0.34 / 0.89 and precision 0.69 / 0.64 / 0.87 (by template: #40 / #44b / #51d). J = 0.25 bonds are nearly invisible (recall 0.17 / 0.03 / 0.33).
  - A percolating graph (mean degree 3, J = 0.3) reads as percolating in only 0.13 / 0.00 / 0.77 of replicates.
  - So a sub-percolating significant-bond graph is weak evidence on its own (SP4 failed).
  - **The exception is #51's own sampling** (template 51d: N 26, 5 × 8 h). There recall is 0.89 and a percolating graph is detected in 77% of replicates. So the absence of bonds and of percolation in the #51 units is not a power failure.
- **Dense vs dilute is identifiable when the excess is significant.**
  - CV-C10 has median 0.16 / 0.11 / 0.13 for dense coupling (J = 1.2/N; "concentrated" in 0.00 / 0.00 / 0.00 of replicates) and 0.44 / 0.31 / 0.65 for dilute J = 0.5.
  - A dense weak ferromagnet also looks sub-percolating bond-by-bond (0.90 / 1.00 / 0.97 "below"), as stated in advance.

**2. Bond distribution and percolation, regime III (P1–P4).** 23 units, 4,318 pairs.
- **Bonds at the floor (P1 ✓).**
  - 38 significant positive and 14 significant negative conditioned bonds; ≈ 23 positive are expected false (1 per unit by construction; the internal surrogate check gives 0.995 per unit).
  - Median fraction of pairs significant 0.95%; ⟨k⟩ < 1 in every unit.
  - BH (q = 0.1) on the same p-values finds 5 positive bonds in all of regime III (3 units), vs 35 in regime I (12 units).
- **Not heavy-tailed (P2 ✗).**
  - The conditioned collective excess is significant (z > 2) in 10 units: 38e, 41, 44b, 51d–51j. The mean bond z is significantly positive in 13.
  - In the 10, CV-C10 is −0.01 to 0.37 (median 0.11), and z skewness exceeds its null's 95% quantile in 1/10.
  - This is the dense pattern (synthetic dense 0.16 / 0.11 / 0.13, dilute 0.44 / 0.31 / 0.65): summed log-likelihood ratio dense vs dilute +22.5 over the 10 units.
- **Below percolation, trivially (P3 ✓, power-limited).**
  - κ < 2 and S₁ ≤ 0.3 in 23/23 units, and 97% of the 34 non-singleton components are pairs or triangles.
  - With bonds at the false floor this is what a paramagnet with a few false edges looks like. The synthetic shows it is also what a dense weak ferromagnet and a moderately bonded percolating graph look like.
- **#44 / #51 not special per pair (P4 ✗).**
  - 4 of their 11 units are above the regime-III median per-pair rate. They hold 68% of all regime-III bonds only because they have more pairs.

- **Corroboration (coordinator, 2026-10-04):** the re-evaluation agents RE-A1 / RE-A2 independently found regime-III co-activation to be 70–92% runner day edges, with only #44 and #51 keeping coupling under the trimmed block-shift null. That matches H49's excess units (38e, 41, 44b, 51d–51j). H49 adds that what #44 and #51 keep is a uniform shift, not pairs.

**3. Edge trimming removes bonds in regime III, not in regime I (P5 ✓).**
- Raw → conditioned, significant positive bonds fall by a median 67% per regime-III unit (99 → 38 in total; edge masking alone gives 43). In regime I they fall by 17% (108 → 84).
- The raw regime-III "bonds" are mostly day-edge artifacts, which matches H38's f_scaffold at the level of individual pairs.

**4. Regime I contrast (P6, descriptive).**
- Regime-I units (N = 6–11) carry 84 significant positive bonds over 740 pairs: 3.7× the false count.
- Their graphs percolate in 14/23 units (κ ≥ 2 or S₁ > 0.3; small N makes S₁ > 0.3 easy).
- The excess is significant in 12/23, with CV-C10 median 0.19 (two units 0.43): dense as well, but with larger per-pair excess (ρ̄_ex 0.007–0.21 vs 0.004–0.09 in regime III's excess units).
- Post hoc: per-pair excess falls with N in regime I (log–log slope −2.7 ± 1.1) and does not in regime III (+0.7 ± 0.8; E rises with N, Spearman 0.61). Flat ρ̄ in N is H25's shared-field signature. This is confounded with #51 being the only large-N period.

**5. Native tests.**

| Test | Key result | Verdict |
| --- | --- | --- |
| [NE43](goalperiod-subhypotheses/NE43/README.md) schedule vs message | edge-induced excess ×0.77 [0.49, 1.40] after the bookend messages stop, ×0.93 after the nudges stop too; bond z has no split-half reliability (r −0.06 to 0.08), so persistence is not evaluable; co-nudged pairs Δz +0.58 (p 0.0005) while nudges run, +0.20 after | mixed |
| [G44](goalperiod-subhypotheses/G44/README.md) team ground truth | `#best` team mean z 0.76 (label-set p 0.26), 0 significant team bonds, 10% of the excess for 5% of pairs; whole swarm shifted (g 0.47, z 8.0); team visible in talk (p 0.013) | failed |
| [G51](goalperiod-subhypotheses/G51/README.md) where bonds live | 24 bonds / 3,023 pairs; adjacent-unit bond-z r median 0.02, recurrence 26%; no same-lab (OR 0.50), rival or opposed enrichment; all κ < 2 | failed |
| [NE14](goalperiod-subhypotheses/NE14/README.md) regime boundary | raw gain jumps (0.20 → 0.32) as a uniform shift (raw mean z 0.54 → 0.92), raw bond count doesn't (6 → 4); no split-half reliability on either side | mixed |

**6. Talk channel (secondary).**
- Regime III: 71 significant positive talk bonds over 2,128 talk pairs vs ≈ 23 expected (3.1×). Their z-vectors partly recur across adjacent #51 units (median r 0.14 vs 0.02 for activity).
- Regime I: 135 over 675 pairs (5.9×), percolating in most units.
- Whatever pairwise structure the swarm has at 1-min resolution is in who talks in the same minutes, not in who works in the same minutes.

**7. Bootstrap.** Day-block bootstraps put mean bond z away from 0 in the units with excess. Bootstrap counts and κ are biased upward: each replicate re-adds sampling noise on top of the fit, so null pairs cross the threshold more often. They are reported in the unit tables but not used for verdicts.

### Outcome vs prediction
| Prediction | Observed | Verdict |
| --- | --- | --- |
| SP1 null: size 0.03–0.07; ≤ 1.5 false bonds; "below" ≥ 95%; raw rejection ≥ 0.10 | 0.054–0.062; 1.200–1.333; 0.967–1.000; raw 0.085–0.170 | ✓ (raw ≥ 0.10 only in 40/51d) |
| SP2 dilute J = 0.5: recall and precision ≥ 0.8; CV-C10 ≥ 0.5; "below" ≥ 90% | recall 0.47 / 0.34 / 0.89; precision 0.69 / 0.64 / 0.87; CV 0.44 / 0.31 / 0.65 | partial (recall ≥ 0.8 only in 51d) |
| SP3 dense: CV ≤ 0.25; mean-z shift; "concentrated" ≤ 10% | CV 0.16 / 0.11 / 0.13; mean-z significant 1.00 / 1.00 / 1.00; 0.00 / 0.00 / 0.00 | ✓ |
| SP4 percolating: κ ≥ 2 and S₁ ≥ 0.5 in ≥ 80% | 0.13 / 0.00 / 0.77 | ✗ (power-limited) |
| SP5 recall 0.7: size ≤ 0.10 | 0.055–0.061 | ✓ |
| P1 median frac significant ≤ 5%; ⟨k⟩ < 1 in ≥ 2/3 | 0.95%; 23/23 | ✓ |
| P2 excess units: CV-C10 ≥ 0.4 in ≥ 2/3; skew > q95 in ≥ 1/2 | 0/10; 1/10 | ✗ (dense) |
| P3 κ < 2 and S₁ ≤ 0.3 in ≥ 2/3; clusters ≤ 3 | 23/23; 97% | ✓ (trivially; power-limited) |
| P4 #44 / #51 above the regime-III median per pair | 4/11 | ✗ |
| P5 trimming loss ≥ 50% in III, ≤ 25% in I | 67% vs 17% | ✓ |
| N43a edge excess ≥ 0.5 × W1 after bookends stop | 0.77, 0.93 | ✓ |
| N43b bonds persist (disattenuated r ≥ 0.5) | split-half reliability ≈ 0 | not evaluable |
| N43c co-nudged Δz ≥ 0.3, halves after | W2 +0.58, W3 +0.20; W1 +0.13 | partial |
| N44a–d team cluster, ≥ 30% of excess, checkpoint-robust | p 0.26; 0 bonds; 10%; −55% | ✗ |
| N51a bonds recur (r ≥ 0.3, ≥ 60%) | r 0.02; 26% | ✗ |
| N51b same-lab OR > 2 (R2, stated expectation) or coupling enrichment | OR 0.50; no rival / opposed enrichment | ✗ (both) |
| N51c κ < 2 in every #51 unit | 9/9 | ✓ (trivially) |
| N14a raw bonds rise, conditioned ≤ half | raw 6 → 4 (gain rises, bonds don't) | ✗ |
| N14b bonds persist across II → III | reliability ≈ 0 | not evaluable |

**Per-unit verdicts** (frozen rule): regime III 0 supported, 15 mixed (paramagnet: ≤ 3 bonds and no significant excess, or between thresholds), 8 failed (dense: significant excess with CV-C10 ≤ 0.2). Regime I: 1 supported (30b), 8 mixed, 14 failed. Per period: see the table above.

### Confirmatory predictions (frozen 2026-10-04, `analysis/confirm.py`, not run)
Holdout units: regime III 45a, 45b, 47, 49, 51m (the #51 tail); regime I 14, 15b, 22a, 22b. Same pipeline. The predictions confirm round 1's findings, not H49's refuted claims:
- **C1 (bonds at the floor).** Median share of pairs with a significant positive conditioned bond ≤ 0.03; pooled positive bonds ≤ 3 per unit (≈ 1 false expected).
- **C2 (trimming).** Raw → conditioned bond loss median ≥ 0.5 in regime III; regime I's median loss is smaller.
- **C3 (dense, not dilute).** Among regime-III holdout units with conditioned excess z > 2, ≥ 2/3 have CV-C10 ≤ 0.25, and none ≥ 0.5.
- **C4 (power-limited).** κ < 2 in ≥ 2/3 of regime-III units.
- **C5 (no stable pairs).** |r| < 0.15 between the #51 tail's bond z and the head's (51h–51j mean).
- **C6 (no provider field).** Same-lab Mantel–Haenszel OR of significant bonds < 2.

The script refuses to run without `--confirm --i-understand-this-uses-the-locked-holdout`. Its dry run on stand-ins (III: 39, 41, 42b, 51h; I: 17, 23, 26) completes.
- **Reuse:** H02 used #45's activity couplings (KI-1 leader influence, EQ-PL hub rank, i.e. our raw variant at hub level); H23 used #45's content. Nobody has looked at #45's conditioned bond distribution, bond graph or concentration.

### Caveats
- **Equal-time only.** The pseudolikelihood sees co-activation within the same minute. Coupling that acts with a delay of 2–8 min (read-out gating, H08; nudges answered after ≈ 5 min, H04) is invisible. "No dilute bonds" means no strong *equal-time* bonds.
- **Dense coupling vs a fast shared field.** Equal-time statistics can't tell a weak all-to-all coupling J₀/N from a common drive faster than the 30-min block field (human messages, nudges, chat bursts, provider latency). The post-hoc size law favors a shared field in regime III, but it rests on cross-period variation in N.
- **Power.** At village sampling, individual bonds need J ≳ 0.5 and ≥ 5 days to be found reliably, and percolation of moderate bonds is not identifiable. The verdict rests on the concentration index, the mean-z shift and pair reliability, which the synthetic shows are identifiable when the excess is significant.
- **CV-C10 was redefined** after the first real-data pass (Amendment 1); the verdict doesn't depend on it.
- **The scaffold reasons and scheduled flags come from the `outages_fixed` sidecar** (H38's rule on the fixed bins). DQ7 will rebuild the official tables; small differences are possible.
- **Multiplicity.** 46 replication units are not 46 independent tests: units of one period share agents, and the pooled bond count is the honest summary. Per-unit verdicts are descriptive.
- **Regime-I S₁ is size-sensitive.** With N = 6–11, S₁ > 0.3 needs only 2–3 bonds, so "percolating" in regime I partly reflects small N.
- **NE43's 08-05 boundary bundles** the bookend messages' disappearance with the #general / #focus split. The #51 room labels are too lopsided (2 of 27 agents mostly in #focus) to test room structure.
- **No held-out likelihood comparison** (pairwise vs field-only model on held-out days) was run.

## Round 2 redirects
- **What the direction is really after:** whether an agent swarm's collective co-activation is carried by a few identifiable pairs (targetable) or by a swarm-wide mode (steer the field, not the pairs). For regime-III activity the answer is the mode.
- **H49-R1. Lagged bonds.** Kinetic Ising or Hawkes cross-kernels at the read-out lag (1–10 min, using DQ1's call windows), on the same conditioned spins. Delayed pairwise coupling is what equal-time statistics can't see.
- **H49-R2. Identify the shared field.** Regress the residual common mode on candidate fast drives (human messages, nudges, chat bursts, per-provider latency). Test ρ̄ flat-in-N at roster joins *within* #51 (H25's size law), which avoids the cross-period confound.
- **H49-R3. Talk bonds.** The talk channel has 3× the false count and recurring pairs. Map them against reply threading and the DQ1 context ledger (`k_new` as an input-load covariate). Test whether talk clusters are dilute (CV-C10, reliability), using #44's team as ground truth.
- **H49-R4. Power-corrected percolation.** A model-based (ABC) comparison of dilute / dense / percolating structures at each unit's own schedule, instead of thresholded significant-bond graphs.
- **H49-R5.** Run `confirm.py` (C1–C6).

## Figures
- `figures/summary_obs.pdf|png`:
  - (a) CV-C10 vs mean bond z for units with a significant conditioned excess, against planted dense and dilute swarms;
  - (b) regime-III significant positive bonds per unit, raw vs conditioned, against the ≈ 1 false bond per unit.
- `figures/synthetic.pdf|png`: calibration, concentration and percolation calls per planted structure.
- Per period: `goalperiod-subhypotheses/{NE43,G44,G51,NE14}/figures/`.

## Notes
- 2026-10-04: promoted from HH159 by Vivian. Round 1 started 05:30 UTC; card and predictions at 05:50 UTC.
- 2026-10-04: **Data finding (before any statistic):** the automated daily pause/resume bookends stop after 2026-08-04 (last pair 08-04 15:59 / 08-05 00:00 UTC). From 08-05 the automated speaker sends only nudges, until 08-20. NE43's catalog entry ("no daily pause/resume bookends from 08-21") is off by 16 days for the bookends. The village window (≈ 16:01 → 00:05 UTC) is unchanged after both dates, so the operator's start/stop continues without its announcement. 08-05 also starts the #general / #focus room split (bundle).
- 2026-10-04: synthetic battery and all 52 units first run on the original `activity_bins`. Rerun on `activity_bins_fixed` + `outages_fixed` after the DQ8 notice (Amendment 2); old-bin outputs kept as `unit_table_buggybins.parquet`, `units_buggybins.parquet` and `synthetic/*_buggybins_preamend.*`.
- 2026-10-04: seeds made deterministic (CRC32 of unit / condition names) before the final runs; Python's salted `hash()` had been used in a first synthetic pass, which was discarded.
- 2026-10-04: the DQ1 context ledger (`call_windows`, `context_ledger_turns.k_new`) was available but not used in round 1. It is the natural covariate for H49-R1 and H49-R3.
- **Suggested shared-file changes** (outside H49's edit scope):
  - `hypotheses/natural-experiments.md` NE43: the daily bookend messages stop after 2026-08-04 (last pair 08-04 15:59 / 08-05 00:00 UTC), and nudges after 08-20. The village window is unchanged, and H49 finds the day-edge excess persists (×0.77 / ×0.93). 08-05 bundles the #general / #focus split.
  - `physics-models/01-inverse-ising/README.md` pitfalls: "Significant-bond graphs are power-limited: at village sampling a percolating graph of J = 0.3 bonds reads as sub-percolating in most replicates, and a dense weak ferromagnet looks like a paramagnet bond by bond. Use excess concentration (CV-C10), split-half bond reliability and the mean-z shift before reading a bond graph (H49)."
  - `physics-models/DEFINITIONS.md`, new H49 named variants:
    - *conditioned pseudolikelihood bond* (Model);
    - *significant-bond graph* (one-sided empirical p < 1/n_pairs against pooled leave-one-out block-shift z);
    - *excess-covariance concentration CV-C10* (pooled, cross-validated over even / odd 30-min blocks).
