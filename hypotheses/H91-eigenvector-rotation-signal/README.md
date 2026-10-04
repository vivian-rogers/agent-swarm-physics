# H91: Eigenvector rotation as a reorganization signal

**Status:** round 1 done (2026-10-04): **failed** as a kickoff alarm. The content rotation alarm A_C has AUC 0.56 [0.40, 0.71] on 23 kickoffs against R1's 0.96 [0.92, 0.99] (ΔAUC −0.41 [−0.56, −0.27]) and catches none of R1's 13 misses. No scored kickoff is in the powered range (W ≥ 16 or N ≥ 16), so the test is uninformative about strong regroupings at kickoffs. Between events the content eigenvectors stay within the finite-T (Dyson) null on 86% of placebo pairs (s_sig 0.14; bge 0.20, gte 0.08), but every day rotates about 1 SD more than a stationary synthetic swarm (median z_boot 1.0 vs 0.1–0.75) with no spikes at events. The NE42 merge rotates talk and content (p_boot 0.005–0.01) but stays below the pre-registered z ≥ 2 (talk 1.97). Card, predictions and the impostor table were written 2026-10-04 ~20:10 UTC before real data; Amendment 1 (~20:26 UTC) changed the null after the synthetic study, before real data. `analysis/confirm.py` frozen and dry-run, not run.
**Question served:** **Q5** (a monitor with measured hit and false-alarm rates; a direct rival to H36's topic shift R1 and to H74's fused detector). Secondary: **Q3** (is the co-movement structure of the collective modes stable between events, as a stationary random-matrix ensemble would be?).
**Fields:** stat mech (random-matrix theory), sociophysics, info theory
**Literature** (none of the notes in `literature/` covers random matrices; cited from memory, †): Dyson, *J. Math. Phys.* 3, 1191 (1962)† (Brownian motion of eigenvalues); Allez & Bouchaud, *PRE* 86, 046202 (2012)† (eigenvector dynamics of sample correlation matrices); Bun, Bouchaud & Potters, *PRE* 98, 052145 (2018)† (overlaps between eigenvectors of two independent sample matrices); Laloux, Cizeau, Bouchaud & Potters, *PRL* 83, 1467 (1999)†; Marchenko & Pastur (1967)†.
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent (Claude Code excluded); Population N(t), **day-present variant** (H36); Regime (rotation compares consecutive active days and so crosses goal and regime boundaries on purpose: the transition is the object, exception (c)); Agent state, **vector variant** (centered, regime-whitened statement vectors, d = 32, both embedding models); **Content centroid shift (R1)** (H36 named variant, the rival). **New named variants proposed** (not edited into DEFINITIONS.md; outside this card's scope): *day overlap matrix (content)*, *eigenvector rotation (subspace distance)*, *pooled-split null*, *rotation excess*, defined under Model. H12's proposed *collective eigenmode (random-matrix)* is used in its sense.
**From:** HH272 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/01-inverse-ising/` (equal-time correlation matrix, χ = C, its eigenmodes), `physics-models/14-scaling-and-fluctuations/` (finite-N, finite-T scaling of fluctuations; the null exponents). The HH's "model 11 (RMT)" label points at the random-matrix tool, which in this repo lives in model 01's "Collective modes" and H12; `physics-models/11-vector-spins/` supplies the content spins.

## Source HH (verbatim from the HH list, including literature refinements)
Eigenvector rotation is a reorganization signal. Track the top content eigenvectors in rolling windows; their rotation speed should spike at goal changes and room events and otherwise follow a Dyson-Brownian-motion null. A spectral complement to H36's topic shift. *Check:* subspace angle between consecutive windows' above-edge eigenvectors; event study at kickoffs and NE42; comparison with R1; null from resampled windows.
  *Models:* 11 (RMT) · *Builds on:* H36, H12 1b, H47

## Question
Does the *direction* of the swarm's collective modes (which agents co-move with which, window by window) change faster than finite-sample noise allows at goal changes and room events, and stay put between them? If yes, it is a reorganization alarm that sees something R1 (the day-mean topic shift) cannot.

## Standards (2026-10-04)
**Question served:** Q5 first, Q3 second.

| Impostor | Relevant? | How it is handled | Status |
| --- | --- | --- | --- |
| Scheduler field | yes (talk) / partly (content) | Talk spins are trimmed to the all-present window (DQ8) before any matrix or surrogate; the rotation null splits whole 30-min blocks; day-level rates are removed by per-day standardization. Content windows are agent-day centered, so window presence carries no mean. A time-of-day content field is common to both days and cancels in the rotation. | removed (talk) / partly (content): the time-of-day content field is not regressed out |
| Exogenous field (kickoff, goal, operator) | yes | Agent-day and kind centering remove each agent's day mean, so a uniform goal step (R1's signal) cannot rotate eigenvectors by construction (synthetic S2 checks this). A goal that splits agents into sub-teams *is* a reorganization and is the target. No `goal_fields` regression (the field is removed by centering, not by projection). Synthetic S2 (a mid-day uniform step) is rejected at ≤ 0.07. | removed (step) / n/a (target) |
| Shared model priors (family, style) | partly | Agent-day centering removes each agent's style level (H73: style is an agent constant). Variant: `style_resid_period` vectors. Family co-movement would be a stable mode and does not rotate. The style-resid variant moves the kickoff AUC by +0.09 (0.65 [0.51, 0.78]): the prior field adds noise to the rotation, not signal. | partly |
| Contemporaneous convergence | no | Rotation makes no influence or copying claim; equal-time co-movement is the object, and its stability is what is tested. | n/a |

**Inputs:** DQ5 statement vectors, both models (`statements_white32_{bge_small,gte_modernbert}.npy`; variant `statements_style_resid_period32_*`), `statement_flags` (restatement dedupe variant), `activity_bins_fixed` (talk spins, DQ8 trim), `calendar`, `roster`, `period_units`. Evaluation design: H36 round 1b catalog and placebo days (`data/processed/H36-reorganization-alarm/r1b/fixed_bge_none/{events,scores}.parquet`, read as data) and R1 scores from `r1b/fixed_bge_none` (bge) and `r1b/fixed_gte_restate` (gte). H74's `scores.parquet` is read for the fused-detector comparison if it is complete at analysis time.

**Two layers:** replication = the common estimator on every eligible non-holdout goal period (`G<NN>`, role `replication`); natives = NE42 (A-B-A room merge/split) and G51 (dense baseline, #focus room), each with its own dated prediction (role `native`).

**Confirm script:** `analysis/confirm.py`, frozen and guarded, not run.

## Model
**From:** `physics-models/01-inverse-ising` (χ = C; eigenmodes of the equal-time correlation matrix) with random-matrix theory, and `physics-models/14-scaling-and-fluctuations` (finite-size fluctuation nulls).

**Degrees of freedom.**
- **Content spins (model 11 states).** For agent i, active day d and 30-min window w: x_i(w) = mean over i's statements in w of (u − μ_{i,d,kind}), with u the regime-whitened, unit-normalized 32-d statement vector and μ_{i,d,kind} agent i's mean on day d for that statement kind (chat or intention). Missing windows are 0. Each agent's day series is scaled to unit mean square. This is H12's construction at day resolution with day centering in place of unit centering.
- **Talk spins (model 01 states).** s_i(t) = +1 if `activity_bins_fixed.state == 4` in minute t, else −1, inside the day's all-present window; standardized per agent and day.

**Day matrix.** The *day overlap matrix* Q_d (content; Q_ij = ⟨z_i·z_j⟩_{w}/d) or the talk correlation matrix C_d, over agents eligible on day d. Its eigenvectors v_1, v_2, … are the day's collective modes; v_1 is H12's uniform "market" mode.

**Rotation.** For consecutive active days a → b and the agents A eligible on both (|A| ≥ 4), restrict both matrices to A and take the top-k eigenvectors V_a, V_b (|A| × k). The *eigenvector rotation* is the subspace (chordal) distance
δ_k(a, b) = [1 − ‖V_aᵀ V_b‖²_F / k]^{1/2} ∈ [0, 1].
Primary k = 2 (the market mode plus the leading structural mode); k = 1 and k = 3 are variants.

**Stationary null (finite-T Dyson/Allez–Bouchaud diffusion).** If the population matrix does not change between a and b, the two sample matrices are two finite-T draws of one matrix, and δ_k is pure sampling noise. Its size depends on N, T and the eigenvalue gaps (perturbatively E[δ₁²] ≈ (2/T) Σ_{j>1} λ₁λ_j/(λ₁ − λ_j)²). The *pooled-split null* estimates this without a parametric model: pool the windows (content) or 30-min blocks (talk) of a and b, each still centered on its own day, split them at random into pseudo-days of the real sizes, and recompute δ_k (R = 199). The *rotation excess* is z_rot = (δ_obs − mean_null)/sd_null, with p_rot = (1 + #{null ≥ obs})/(R + 1).

**Alarm.** A_rot(d) = H36's trailing robust z of z_rot (B = 10 previous non-holdout active days, ≥ 5 required, SD after dropping max and min, divided by the consistency factor), one-sided. The content alarm averages the two embedding models, A_C = mean(A_bge, A_gte). Threshold 2.

**What the model predicts.** Between events the population matrix is stationary up to a slow drift, so p_rot is close to uniform and A_rot sits near 0. A reorganization (agents regroup: new teams, a room merge or split, a new sub-task split) changes the eigenvectors, so δ exceeds the split null. A uniform topic step (R1's signal) changes day means, which centering removes, and does not rotate the eigenvectors.

## Data scheme (`scheme/`)
- **Inputs:** listed under Standards. No raw tables and no text.
- **Transform** (`scheme/build.py` + `scheme/daymat.py`): non-holdout days only (`holdout_mask` plus a hard assertion that `calendar.holdout` agrees); Claude Code excluded.
  - Content, per model and variant: kind-centered statement vectors → window means per agent → per-day arrays (N_d × W_d × 32, float16). Window count W_d = ⌈window_s / 1800⌉ (H12). Eligible agent-day: statements in ≥ max(2, ⌈W_d/4⌉) windows. Eligible day: W_d ≥ 4 and ≥ 4 eligible agents.
  - Talk: minute states per agent-day → activity spins → all-present window (H12's `trim_rows`, DQ8) → talk spins on kept minutes. Eligible agent-day: ≥ 5 talk minutes in the kept window. Eligible day: ≥ 60 kept minutes and ≥ 4 eligible agents.
- **Output:** `data/processed/H91-eigenvector-rotation-signal/`: `content_<model>[_<variant>].npz` and `talk.npz` (per-day arrays, agent codes, dates), `days.parquet`, `rotation.parquet` (one row per day × channel × variant: |A|, δ_k, null mean/sd, z_rot, p_rot, A_rot), `eval/` (AUCs, hits, FAR, rival comparison), `periods.parquet`, `synthetic/`, `native/`, `_provenance.json`. Budget ≤ 30 MB.
- **Regimes covered:** all non-holdout active days, I → III, in time order.

## Observables
1. **Per day pair and channel:** δ_k, z_rot, p_rot, A_rot (k = 1, 2, 3; content bge, gte, style-resid variant; talk).
2. **Event study (primary):** AUC of A_C on day 0 of non-holdout goal kickoffs (H36's r1b catalog, class `goal`) vs H36's placebo days (≥ 3 active days from every catalogued event), with a bootstrap CI over events and placebos; hit rate (A ≥ 2 on day −1, 0 or +1); per-day placebo FAR; random-date null for the mean event-day score (2,000 draws within regime).
3. **Rival comparison:** paired ΔAUC(A_C − R1) on the common days; the combined score (A_C + R1)/√2 vs R1 alone; the share of R1 misses (R1 < 2 on days −1..+1) that A_C catches; Spearman(A_C, R1) over all days. H74's fused score, if available.
4. **Stationarity between events ("otherwise DBM"):** the share s_sig of placebo day pairs with p_rot < 0.05, per channel (nominal 0.05).
5. **Rooms:** z_rot and A_rot at H36's room events (NE42a 05-04, NE42b 05-11, the 07-24 side room, #focus 08-05); *room-reassignment days* (≥ 2 common agents change modal room, from `statements.room`) vs other days.
6. **Per period (replication):** s_sig on the period's within-period pairs that are ≥ 2 active days from any catalogued event; median z_rot with a bootstrap CI; the kickoff pair's z_rot and A_C.

## Null / baseline
Weakest to strongest:
1. **Marchenko–Pastur / naive noise:** δ_k between two independent Gaussian matrices of the same N, T (synthetic only; ignores autocorrelation and gaps).
2. **Pooled-split null (primary, per pair):** stationary population matrix across the two days; keeps the window or block as a unit, so within-window co-movement is kept and only the day label is exchanged.
3. **Trailing baseline:** the swarm's own last 10 active days (absorbs slow drift and any anti-conservatism of 2 from within-day autocorrelation).
4. **Placebo days and random dates** (H36's design), within regime.
5. **Rival detectors:** R1 (content centroid shift; AUC 0.95 in H36), H74's fused detector, and R0 = |A| change alone (composition).

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R1 content centroid shift (a field step, no rotation); stationary finite-T sampling (Dyson null); composition change (who is present).
**Locked holdout used for confirmation:** none. `analysis/confirm.py` (frozen 2026-10-04, guarded by `--confirm` + `H91_CONFIRM=1` + the holdout ledger) targets held-out goal kickoffs (#28, #29, #45–#50) and the #51 tail; its dry run on non-holdout stand-ins gives C1–C4 pass (A_C 0.57, R1 0.96).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Content and talk spins come from DQ5 vectors (both models) and `activity_bins_fixed`; agent-day centering removes the topic step by construction. Eigenvectors are compared only on the agents present on both days, so roster churn shrinks the sample. Per-day z agrees only weakly between models (Spearman 0.33). |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | P2 tests stationarity of the co-movement structure between events: content passes narrowly (s_sig 0.14 on 51 placebo pairs; bge 0.20, gte 0.08), talk fails where it is sized (0.17, n 6; #51 0.40). Every channel sits at median z_boot ≈ 1.0: a slow drift. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 0 | Kickoff AUC 0.56 [0.40, 0.71] vs placebo days; random-date p 0.34; hit 0.11 at a per-day FAR of 0.02. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | The k = 1 control (the uniform mode never rotates under regrouping) holds: k = 1 AUC 0.47. The rotation is not a composition effect (Spearman with the agent-count change 0.01–0.05). The regrouping signature (k = 2 rotates) appears only at the NE42 merge. |
| E interventional | predicts the change across a natural experiment | 1 | NE42 merge: talk p_boot 0.005, content 0.005/0.01, A_C 2.4; split: talk p 0.025, content n.s.; #focus (08-05) silent (talk z 1.35, p 0.08). Below the pre-registered z ≥ 2 on both NE42 steps. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Synthetic at N 4–32, W 4–16 found two flaws in the first null (fixed in Amendment 1 before real data). The final null is sized (content ≤ 0.05; talk ≤ 0.07 at N ≥ 16) and recovers a strong regrouping at W = 16 or N = 32 (power 0.85–1.0), but only 0.2–0.4 at the real median (N 10, W 8). |
| G ground truth | agrees with known structure | 1 | Days on which ≥ 2 agents change modal room have higher talk rotation (mean z 1.60 vs 1.07, p 0.03, n = 3); content does not (p 0.43). |
| H comparative | beats the named rivals | 0 | Loses to R1 by 0.41 AUC and to H74's fused detector by 0.25 [0.06, 0.42]; the combined score (A_C + R1)/√2 is not better than R1 (ΔAUC −0.05 [−0.14, +0.01]). |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Holdout not run. 27/35 periods have < 3 quiet pairs (descriptive); of the 8 scored, s_sig ≤ 0.15 in 5. |

## Synthetic validation (axis F, before real data; `analysis/synthetic.py`)
Village-skeleton days at real counts: N ∈ {4, 8, 16, 32}, W ∈ {4, 8, 16} windows of d = 32, agent-window fill 0.6–0.9, talk days of 120–480 kept minutes with talk rates 0.05–0.15. Content: x_i(w) = a·f₀(w) + b·f_{r(i)}(w) + noise, with a market factor f₀, room factors f_r (two rooms), AR(1) window persistence ρ_w ∈ {0, 0.5}. Talk: thresholded latent Gaussians with the same factor structure and minute persistence. Scenarios, 200 day pairs each:
- **S0 stationary:** same loadings on both days → size of p_rot < 0.05 and per-day FAR of A_rot ≥ 2.
- **S1 regrouping:** half of the agents swap rooms at day b → power of z_rot ≥ 2 and AUC vs S0.
- **S2 topic step:** every agent's day mean jumps to a new direction (R1's signal) → rotation must stay at the S0 level.
- **S3 mode strength:** a 0.3 → 0.5 with fixed eigenvectors → rotation must stay near S0.
**Pass rules:** S0 size ≤ 0.10 at ρ_w = 0 (report it at 0.5); S2 and S3 rejection within 0.05 of S0; S1 power ≥ 0.8 at N ≥ 8 and W ≥ 8. If S1 power < 0.8 at real counts, real-data misses are "underpowered", not "failed".

## Amendment 1 (2026-10-04 ~20:26 UTC; after the synthetic study, before any real-data rotation statistic)
The synthetic study (`analysis/synthetic.py`, 60 pairs per cell, R = 99; `data/processed/H91-eigenvector-rotation-signal/synthetic/summary.parquet`) found two flaws in the pooled-split null as first written and one power limit. Changes, all made before real data:
1. **Re-centering.** Pseudo-days are re-centered per agent on their present windows, as real days are. Without it the split null had size 0.2–0.43 at N = 16–32 (it compared centered days with uncentered pseudo-days). With it, size ≤ 0.12 except N = 32, W = 16, ρ_w = 0.5 (0.27).
2. **Primary null: the same-day block bootstrap.** Under a real regrouping, the pooled split mixes the two days' structures, so its own δ distribution widens and z falls: S1 AUC was 0.30–0.85 (often below the raw δ). The new null draws two independent moving-block bootstrap resamples (block = 2 windows; talk: 30-min blocks) of the *same* day, for day a and day b alternately (R = 199). It estimates the finite-T eigenvector diffusion of each day without mixing them. The primary score is **z_boot (k = 2)** and the per-pair p is **p_boot**. The split null stays as a secondary, conservative check.
3. **Synthetic operating characteristics of the primary score** (strong regrouping: half of each room swaps, room loading 0.4):
   - size of p_boot < 0.05 on stationary pairs: content 0–0.05 in every cell (conservative); talk 0.13–0.28 at N ≤ 8 with L ≤ 240 kept minutes, ≤ 0.07 at N ≥ 16 and L ≥ 240;
   - power (p_boot < 0.05) at N = 8–16, W = 8: 0.23–0.43; at W = 16 or N = 32, W ≥ 8: 0.85–1.0; AUC(z_boot, S1 vs S0) 0.92–1.0 for N ≥ 8, W ≥ 8; 0.61–0.94 for weak rooms (loading 0.25);
   - trailing alarm A ≥ 2: FAR 0.01–0.09; hit 0.2–0.48 at N = 8, W = 8; 0.92–1.0 at N ≥ 16, W ≥ 8;
   - specificity: a mid-day uniform topic step (S2) and a market-mode strength change (S3) are rejected at ≤ 0.07 (content); k = 1 never detects a regrouping (AUC 0.39–0.55), as the uniform mode does not move.
4. **Consequences for the predictions (rules unchanged, scope narrowed).** At the median real day (N ≈ 10, W ≈ 8) a strong regrouping is detected per pair with probability ≈ 0.3. P1 misses are therefore informative only for kickoffs with W ≥ 16 or N ≥ 16; those are reported separately. P2 in talk uses only pairs with N ≥ 16 and ≥ 240 kept minutes on both days (where p_boot is sized); content uses all pairs. P0's power rule ("≥ 0.8 at N ≥ 8 and W ≥ 8") **fails** at N = 8–16, W = 8 and passes at W = 16 or N = 32.

## What I had seen (disclosure)
I read the H12, H36, H74 (card only; round 1 running), H25 and H26 cards. Known to me before writing: R1 has AUC 0.95 on day 0 of 33 non-holdout kickoffs (both models); H36's content physics alarm reaches AUC 0.77, and ~40% of it is a within-day drift; content modes exist in 24/24 units and survive agent-day centering; the top content mode is uniform (sign share 1.0); talk modes are real in 21/24 units and separate rooms in 7/10 two-room units; NE42's merge week has 15 agents in one room and no talk co-activation (H25 native); content room gains are ~0.5 (H26). Sampling-design counts only: 282 non-holdout content days, median 10 agents and 8 windows per day. I have computed no rotation, eigenvector or overlap statistic on real data.

## Prediction
*Written 2026-10-04 ~20:10 UTC, before the synthetic study and before any rotation statistic on real data. Credences in brackets.*
- **P0 (synthetic, F).** The pass rules above hold [0.6]. At N = 4 the pooled-split null is too coarse; I expect S1 power < 0.5 there [0.7].
- **P1 (primary, goal kickoffs).** AUC(A_C, day 0 vs placebo) ≈ 0.62 (range 0.50–0.75) [0.6]; hit rate ≤ 0.40 [0.6]; it loses to R1 by ≥ 0.15 AUC [0.8]. *Reason:* most kickoffs are uniform topic steps between days, which centering removes; only kickoffs that regroup agents should rotate.
  - **Supported** if AUC ≥ 0.70 with the CI above 0.5, random-date p < 0.05, **and** either ΔAUC(A_C − R1) has a CI that includes 0 or the combined score beats R1 alone (paired ΔAUC CI above 0). **Failed** if AUC ≤ 0.60 or its CI includes 0.5. **Mixed** otherwise. [Credence supported: 0.15.]
- **P2 (stationarity between events, "otherwise DBM").** On placebo day pairs, s_sig ≤ 0.15 in content and in talk [0.35]. I expect it to fail: agents switch sub-tasks from day to day, so the co-movement structure drifts faster than finite-T noise. **Counts against the HH's "otherwise Dyson" clause** if s_sig > 0.15 in both channels.
- **P3 (rooms, talk channel).** Talk z_rot ≥ 2 at NE42a [0.5] and NE42b [0.5]; mean talk z_rot on room-reassignment days > on other days (Mann–Whitney p < 0.05) [0.5].
- **P4 (complement, not copy).** Spearman(A_C, R1) over all scored days < 0.3 [0.7].
- **P5 (instrument robustness).** Spearman of z_rot between bge and gte across days ≥ 0.6 [0.6]; P1's AUC moves by ≤ 0.05 under the style-resid variant [0.6].
- **P6 (composition rival R0).** z_rot is not explained by the change in |A|: Spearman(z_rot, |ΔN|) < 0.3 [0.7].
- **Multiplicity.** Primary: P1 (one AUC, one rival contrast). P2 and P3 are the HH's two named clauses; everything else is descriptive.
- **Replication rule (period README):** *supported* if s_sig ≤ 0.15 on the period's non-event pairs **and** the kickoff pair has A_C ≥ 2; *failed* if s_sig > 0.15 and the kickoff pair (if scorable) has A_C < 2; *mixed* otherwise; *descriptive* if the period has < 3 scorable non-event pairs. Content channel, models averaged (s_sig is the mean of the two models' shares).

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [NE42](goalperiod-subhypotheses/NE42/README.md) | native | mixed | merge 05-04: talk z 1.97 (p 0.005), content z 2.09/1.72 (p ≤ 0.01), A_C 2.42; split 05-11: talk z 1.47 (p 0.025), A_C −1.60 |
| [G02](goalperiod-subhypotheses/G02/README.md) | replication | descriptive | s_sig – (n 0); median z –; kickoff A_C –, R1 – |
| [G03](goalperiod-subhypotheses/G03/README.md) | replication | descriptive | s_sig – (n 0); median z –; kickoff A_C –, R1 – |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | failed | s_sig 0.21 (n 14); median z 0.93; kickoff A_C –, R1 – |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | descriptive | s_sig 0.00 (n 2); median z 1.53; kickoff A_C –, R1 – |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | mixed | s_sig 0.00 (n 6); median z 0.91; kickoff A_C 1.61, R1 3.55 |
| [G07](goalperiod-subhypotheses/G07/README.md) | replication | descriptive | s_sig – (n 0); median z –; kickoff A_C -0.10, R1 3.30 |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | failed | s_sig 0.27 (n 15); median z 0.63; kickoff A_C 0.47, R1 5.98 |
| [G10](goalperiod-subhypotheses/G10/README.md) | replication | descriptive | s_sig – (n 0); median z –; kickoff A_C –, R1 – |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | descriptive | s_sig 0.00 (n 2); median z 1.25; kickoff A_C 0.38, R1 0.66 |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication | descriptive | s_sig 0.00 (n 1); median z 0.34; kickoff A_C 2.92, R1 3.72 |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | failed | s_sig 0.21 (n 7); median z 1.20; kickoff A_C -0.26, R1 1.19 |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | descriptive | s_sig 0.50 (n 2); median z 1.34; kickoff A_C –, R1 – |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | descriptive | s_sig 0.25 (n 2); median z 0.93; kickoff A_C -0.23, R1 1.24 |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | descriptive | s_sig 0.00 (n 2); median z 0.00; kickoff A_C -5.10, R1 2.16 |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | mixed | s_sig 0.00 (n 6); median z 1.04; kickoff A_C 0.36, R1 0.78 |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | descriptive | s_sig 0.50 (n 1); median z 1.30; kickoff A_C -0.15, R1 5.22 |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | descriptive | s_sig – (n 0); median z –; kickoff A_C -0.78, R1 1.66 |
| [G23](goalperiod-subhypotheses/G23/README.md) | replication | descriptive | s_sig 0.00 (n 2); median z 0.66; kickoff A_C –, R1 – |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | descriptive | s_sig 0.00 (n 2); median z 1.23; kickoff A_C -1.05, R1 2.36 |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | descriptive | s_sig 0.50 (n 2); median z 1.03; kickoff A_C -0.71, R1 3.02 |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | descriptive | s_sig 0.00 (n 1); median z 0.95; kickoff A_C 0.25, R1 1.90 |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | mixed | s_sig 0.14 (n 7); median z 0.78; kickoff A_C -0.44, R1 2.24 |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | descriptive | s_sig 0.50 (n 1); median z 1.14; kickoff A_C –, R1 – |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | descriptive | s_sig – (n 0); median z –; kickoff A_C 0.68, R1 5.15 |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | descriptive | s_sig – (n 0); median z –; kickoff A_C –, R1 – |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | descriptive | s_sig 0.00 (n 2); median z 0.45; kickoff A_C –, R1 – |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | descriptive | s_sig – (n 0); median z –; kickoff A_C -0.94, R1 6.72 |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | descriptive | s_sig – (n 0); median z –; kickoff A_C 0.86, R1 2.92 |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | mixed | s_sig 0.00 (n 5); median z 0.66; kickoff A_C 1.16, R1 2.06 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | descriptive | s_sig 0.50 (n 2); median z 1.29; kickoff A_C -0.75, R1 31.92 |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | descriptive | s_sig 0.25 (n 2); median z 1.11; kickoff A_C 2.42, R1 3.55 |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | descriptive | s_sig 0.00 (n 1); median z 0.69; kickoff A_C -1.60, R1 9.72 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | descriptive | s_sig – (n 0); median z –; kickoff A_C -0.06, R1 6.48 |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | descriptive | s_sig – (n 0); median z –; kickoff A_C –, R1 – |
| [G51](goalperiod-subhypotheses/G51/README.md) | native | mixed | s_sig 0.12 (n 16); median z 1.09; kickoff A_C –, R1 – |


## Results
*Round 1, 2026-10-04, non-holdout only. Code: `scheme/{daymat,build}.py`, `analysis/{h91lib,synthetic,run_rotation,evaluate,natives,write_period_folders,figures,confirm}.py`. Data: `data/processed/H91-eigenvector-rotation-signal/` (12 MB). Figures: `figures/summary_obs.pdf`, `figures/summary_obsb.pdf`.*

**Headline.** Day-to-day eigenvector rotation of the agent content matrix is not a reorganization alarm. It does not separate goal kickoffs from quiet days (AUC 0.56 [0.40, 0.71]), and R1, a plain centroid shift, does (0.96). The two are nearly independent (Spearman 0.21), but adding rotation to R1 does not help. Between events the content eigenvectors drift slowly: each day pair rotates about 1 SD above finite-T noise, events or not.

**Outcome vs prediction.**

| Prediction | Rule | Observed | Verdict |
| --- | --- | --- | --- |
| P0 synthetic | size ≤ 0.10; S2, S3 within 0.05 of S0; power ≥ 0.8 at N ≥ 8, W ≥ 8 | size ≤ 0.05 (content); S2/S3 ≤ 0.07; power 0.2–0.4 at N 8–16, W 8; ≥ 0.85 at W 16 or N 32 | partly (power fails at real counts) |
| P1 kickoffs (primary) | AUC ≥ 0.70, CI > 0.5, random-date p < 0.05, and not worse than R1 or adds to it | AUC 0.56 [0.40, 0.71], p 0.34, hit 0.11, FAR 0.02/day; ΔAUC vs R1 −0.41 [−0.56, −0.27]; combined −0.05 [−0.14, +0.01]; 0/13 R1 misses caught; 0 kickoffs in the powered range | **failed** (uninformative about strong regroupings) |
| P2 Dyson between events | s_sig ≤ 0.15 in content and talk | content 0.14 (bge 0.20 [0.11, 0.32], gte 0.08 [0.03, 0.19]); all pairs 0.15–0.18; talk 0.17 (n 6, sized pairs) | content pass (narrow, model-dependent); talk fail |
| P3 rooms (talk) | z ≥ 2 at NE42a and NE42b; reassignment days higher | 1.97 (p 0.005) and 1.47 (p 0.025); reassignment days 1.60 vs 1.07 (p 0.03, n = 3) | fail by threshold; direction holds |
| P4 complement | Spearman(A_C, R1) < 0.3 | 0.21 | pass |
| P5 instruments | bge–gte z Spearman ≥ 0.6; AUC shift ≤ 0.05 | 0.33; style +0.09, restate +0.07 | fail |
| P6 composition | Spearman(z, abs ΔN) < 0.3 | 0.01–0.05 | pass |

**What the rotation measures instead.** The rotation excess sits at a median z_boot of 1.0 in every channel and variant (content bge 1.02, gte 1.02, style-resid 1.03–1.05, restate 1.00–1.04, talk 1.13). Stationary synthetic swarms at the same counts give 0.1–0.75. So the co-movement pattern changes a little every day, and the change does not concentrate at goal changes, roster joins or scaffold steps (#51 roster joins 1.12 vs quiet days 1.09 ± 0.19). Within regime III this is consistent with agents switching sub-tasks daily (H06: intention clusters are sub-task topics). The pooled-split null (secondary) gives a better kickoff AUC (0.66 [0.52, 0.80], p 0.05), but it is the null that loses power under real regroupings in the synthetic study; it is reported, not promoted.

**Natives.** NE42 (mixed): the merge is the only event in the record where both talk and content rotate beyond the bootstrap (p ≤ 0.01), and NE42's mean talk alarm exceeds 85% of goal-only kickoffs; the split back is weaker. G51 (mixed): content stays within the Dyson null between events (s_sig 0.125, n 16), talk does not (0.40, n 10); #focus is not seen; roster joins do not rotate.

**Per period.** 27/35 periods have fewer than 3 quiet within-period pairs and are descriptive. Of the 8 scored: 3 failed (#4, #8, #13: s_sig 0.21–0.27, no kickoff alarm), 5 mixed (#6, #19, #27, #38 and the #51 native), 0 supported. No kickoff pair in any period reached A_C ≥ 2 except #12 (2.92) and #40 (2.42, the NE42 merge).


## Notes
- 2026-10-04 ~20:10 UTC: card written before any real-data rotation statistic (see disclosure).
- 2026-10-04 ~20:26 UTC: Amendment 1 after the synthetic study (re-centered split null; same-day block bootstrap as the primary null), before real data.
- 2026-10-04 ~20:12 UTC: native predictions (NE42, G51) written, before the runs (run ~20:30 UTC).
- Compute: scheme 3 s; synthetic ~6.5 min (one process, BLAS 2 threads); real-data rotation ~2 min for 7 channels; disk 12 MB.
- `scheme/daymat.py` is an identical copy of H92's (STANDARDS §8 forbids cross-hypothesis imports); suggested home `infra/shared/day_matrices.py`.

## Round 2 redirects (2026-10-04)
- **What the direction is really after:** whether the swarm's co-movement structure has events at all, or only a slow daily drift that a monitor must treat as its baseline.
- **H91-R1.** Test rotation where it is powered: operator room assignments (DQ6) and 8-h, N ≥ 16 periods (#51 era, held-out #45–#50), not goal kickoffs.
- **H91-R2.** Time the NE42 merge rotation with within-day halves, to see whether the modes turn at the merge hour.
- **H91-R3.** Fit the daily drift (z ≈ 1) as a rotational diffusion constant per period and use it as a phase-diagram coordinate.
