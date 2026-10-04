# H92: RMT-cleaned matrices forecast tomorrow's alignment

**Status:** round 1 done (2026-10-04): **mixed**. RMT clipping at a calibrated edge forecasts tomorrow's agent content correlation matrix better than the raw matrix in 26/32 (bge) and 27/32 (gte) periods (mean gain 0.10 [0.03, 0.16] / 0.11 [0.04, 0.16]), and the gain grows with q = N/T (Spearman 0.45–0.65 in every channel). It does not beat Ledoit–Wolf shrinkage: it beats the better of the two Ledoit–Wolf estimators in 17/32 periods and ties constant-correlation shrinkage within 1–2% of MSE. Talk pair structure is not forecastable beyond its mean (best skill 0.05), and cleaning erases the #38 talk room block. Card, predictions and the impostor table were written ~20:15 UTC before real data; Amendment 1 (~20:36 UTC) narrowed scope after the synthetic study, before real data. `analysis/confirm.py` frozen and dry-run, not run.
**Question served:** **Q5** (a practical monitor: who will co-move with whom tomorrow, with a measured error). Secondary: **Q3** (how much of the agent correlation matrix is signal: if only the above-edge modes forecast, the collective structure is low-rank).
**Fields:** stat mech (random-matrix theory), statistics (covariance estimation)
**Literature** (none of the notes in `literature/` covers random matrices or shrinkage; cited from memory, †): Laloux, Cizeau, Bouchaud & Potters, *PRL* 83, 1467 (1999)† (eigenvalue clipping); Plerou et al., *PRE* 65, 066126 (2002)†; Bun, Bouchaud & Potters, *Phys. Rep.* 666, 1 (2017)† (cleaning large correlation matrices; rotationally invariant estimators); Ledoit & Wolf, *J. Multivar. Anal.* 88, 365 (2004)† (shrinkage to the identity); Ledoit & Wolf, *J. Empir. Finance* 10, 603 (2003)† (shrinkage to constant correlation); Marchenko & Pastur (1967)†.
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent (Claude Code excluded); Population N(t), day-present variant (H36); Regime; Agent state, vector variant (regime-whitened statement vectors, both models). **New named variants proposed** (not edited into DEFINITIONS.md): *day overlap matrix (content)* (shared with H91), *RMT-clipped correlation (calibrated edge)*, *next-day alignment forecast error*, defined under Model.
**From:** HH277 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/01-inverse-ising/` (equal-time correlation matrix and its modes), `physics-models/11-vector-spins/` (content spins). The random-matrix edge is the tool (H12).

## Source HH (verbatim from the HH list, including literature refinements)
RMT-cleaned matrices forecast tomorrow's alignment. Eigenvalue-clipped (RMT-cleaned) agent content correlation matrices should predict next-day pairwise alignment better than raw or shrinkage estimates: a practical monitoring tool. *Check:* out-of-sample next-day pair correlation forecast error for raw, Ledoit–Wolf and RMT-clipped estimators, per period.
  *Models:* 11 (RMT) · *Builds on:* H12 1b, H20, H48

## Question
Given the agent correlation matrix measured up to today, which estimator best predicts tomorrow's realized pairwise correlations: the raw sample matrix, a Ledoit–Wolf shrinkage, or a random-matrix-cleaned matrix that keeps only the eigenmodes above the noise edge? The answer says how much of the measured pair structure is persistent signal.

## Standards (2026-10-04)
**Question served:** Q5 first, Q3 second.

| Impostor | Relevant? | How it is handled | Status |
| --- | --- | --- | --- |
| Scheduler field | yes (talk, activity) | Spins are trimmed to the all-present window before any matrix; the calibrated edge is the trimmed 30-min block-shift null (DQ8, size 0.05 for λ₁). Per-day standardization removes day-level rates. | removed |
| Exogenous field (kickoff, goal, operator) | partly | Agent-day centering removes each agent's day mean (the goal step). A shared within-day content drift remains in Q and is part of what is forecast. Forecasts never cross a unit boundary (`period_units`), so kickoffs are not forecast across. | partly |
| Shared model priors (family, style) | partly | Agent-day centering removes style levels; `style_resid_period` variant. A stable family mode would be forecastable signal; H92 makes no claim about its origin. The style-resid variant keeps P1 (shares 0.78 / 0.88) and does not rescue P2 (0.50 / 0.63). | partly |
| Contemporaneous convergence | no | The forecast is of equal-time co-movement; no influence claim is made. | n/a |

**Inputs:** the same per-day matrices as H91 (content with both DQ5 models; talk and activity spins from `activity_bins_fixed` with the DQ8 trim), `period_units`, `calendar`, `roster`, `statements.room` (room labels for the G38 native).

**Two layers:** replication = the common forecast comparison on every eligible non-holdout unit, reported per goal period (`G<NN>`, role `replication`); natives = G51 (long units: the advantage should shrink as training grows) and G38 (two rooms: does cleaning keep the room block?), each with its own dated prediction (role `native`).

**Confirm script:** `analysis/confirm.py`, frozen and guarded, not run.

## Model
**From:** `physics-models/01-inverse-ising` (equal-time correlation matrix C; χ = C; its eigenmodes) with random-matrix cleaning.

**Degrees of freedom.** As in H91: content spins x_i(w) (agent-day and kind centered, regime-whitened, d = 32, 30-min windows, missing = 0, unit mean square per agent-day); talk spins and activity spins (±1 per minute in the all-present window, standardized per agent-day).

**Matrices.** The day overlap matrix Q_d (content) or correlation matrix C_d (spins). The *target* is the realized matrix on day t+1, restricted to the agents eligible on day t+1 and on at least half of the training days (N ≥ 4). The *training matrix* is built from all earlier days of the same unit (expanding window; variant: the previous day only), concatenated in time.

**Estimators** (each returns a unit-diagonal matrix Ĉ; forecast = its off-diagonal):
- **E0 zero:** Ĉ = I (no co-movement).
- **E1 mean field:** every pair gets the training mean ρ̄ (a single uniform mode).
- **E2 raw:** the training sample matrix S.
- **E3 LW-I:** Ledoit–Wolf (2004) shrinkage of S toward μI with the analytic intensity, rescaled to unit diagonal.
- **E4 LW-CC:** Ledoit–Wolf (2003) shrinkage toward the constant-correlation target with the analytic intensity.
- **E5 RMT-clip (calibrated edge), the HH's estimator:** eigenvalues of S at or below λ₊^cal are replaced by their mean (trace kept), the matrix is rebuilt and rescaled to unit diagonal. λ₊^cal is the 95th percentile of the top eigenvalue of the training data under a null that breaks cross-agent alignment and keeps each agent's series: independent circular shifts of each agent's window sequence within each day (content), the trimmed 30-min block shift (spins). 49 surrogates.
- **E6 RMT-clip (MP edge):** the same with λ₊ = (1 + √(N/T))², T = number of samples (W·d for content, minutes for spins). Variant; it ignores autocorrelation and the correlation of the 32 coordinates.

**Score.** Off-diagonal mean squared error MSE_k(t+1) = mean_{i<j} (Ĉ_ij − Q_ij(t+1))². The relative gain of clipping over estimator k is r_k = 1 − MSE_5/MSE_k (positive = clipping is better). The target's own sampling noise adds the same constant to every estimator, so differences are unbiased; skill against E0 is reported as 1 − MSE_k/MSE_0.

**What random-matrix theory predicts.** With N agents and T effective samples, a raw pair correlation carries noise of variance ≈ (1 − ρ²)²/T. If the population matrix is low-rank plus identity and stationary, clipping removes most of that noise and keeps the signal, so E5 beats E2, and it beats E4 when there is more than one signal mode (a uniform mode is all E1 and E4 can represent). The gain grows with q = N/T. If real structure sits below the edge (weak, many-mode co-movement), clipping deletes it and E2 or E3 win. If day-to-day drift dominates, every estimator converges to E1.

## Data scheme (`scheme/`)
- **Inputs:** listed under Standards. No raw tables and no text.
- **Transform** (`scheme/build.py` + `scheme/daymat.py`, an identical copy of H91's builder; suggested for `infra/shared/`): per-day content arrays (both models; style-resid variant), talk and activity spins in the all-present window; non-holdout days only (`holdout_mask` plus a hard assertion); Claude Code excluded. Eligibility as in H91. Units from `period_units` (holdout units dropped).
- **Output:** `data/processed/H92-rmt-cleaned-forecast/`: `content_<model>[_<variant>].npz`, `talk.npz`, `activity.npz`, `days.parquet`, `forecasts.parquet` (one row per unit × target day × channel × variant × estimator: N, T, q, k above edge, MSE, skill), `periods.parquet`, `synthetic/`, `native/`, `_provenance.json`. Budget ≤ 30 MB.
- **Regimes covered:** all non-holdout units, I → III; forecasts never cross a unit boundary.

## Observables
1. Per unit and target day: MSE for E0–E6; r_raw, r_LWI, r_LWCC; k above λ₊^cal and above the MP edge; q = N/T.
2. Per goal period: the mean r_k over target days (day-bootstrap CI when ≥ 3 target days); the number of target days on which E5 has the lowest MSE.
3. Across periods (periods as points, not pooled data): the share of periods with mean r_raw > 0 and with mean r_best-LW > 0; the mean of period means with a period-bootstrap CI; channel ordering.
4. Spearman(r_raw, q) across target days, per channel (the RMT scaling signature).
5. Natives: r_raw vs training length in G51; the predicted vs realized room contrast (mean within-room minus between-room pair correlation) in G38.

## Null / baseline
- **E0 and E1** are the floor: no structure, or a single uniform mode.
- **E2 raw** is the HH's first rival; **E3/E4 Ledoit–Wolf** the second. The strongest of E1–E4 on each period is the bar E5 has to clear.
- **The calibrated edge** is itself sized on synthetic data (S0 below) so that clipping keeps ≤ 5% spurious modes.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** raw sample matrix (all structure is signal); Ledoit–Wolf shrinkage to identity or constant correlation (signal is a uniform mode); mean field E1.
**Locked holdout used for confirmation:** none. `analysis/confirm.py` (frozen 2026-10-04, guarded by `--confirm` + `H92_CONFIRM=1` + the holdout ledger) targets held-out units of #28, #29, #45–#50 and the #51 tail; the dry run on non-holdout stand-ins passes C1–C3.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Content (both DQ5 models), talk and activity spins (DQ8 trim) come from shared tables; forecasts stay inside `period_units` units. Training matrices zero-fill absent agent-days, which slightly mixes presence into the sample. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | P6: with the raw matrix, more history helps (expanding beats previous-day in 79–92% of forecasts); after cleaning, more history hurts (−7% to −12% MSE). The cleaned structure drifts from day to day. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Out-of-sample next-day forecasts: clipping beats raw (26–27/32 periods, CI above 0), the identity forecast and mean field (23/32); it ties Ledoit–Wolf constant correlation, the strongest rival. |
| D unfitted predictions | unfitted statistics and the model's signature | 2 | The random-matrix signature, not fitted: the cleaning gain grows with q = N/T (Spearman 0.45–0.65 in content, talk and activity) and falls with training length in #51 (−0.69 / −0.90). |
| E interventional | predicts the change across a natural experiment | 0 | No natural experiment was used; forecasts never cross a step change. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Synthetic units at N 4–32, W 4–16: the expected ordering holds, but the calibrated edge keeps a spurious mode in up to 17% of noise fits, and a real room mode is cut at N ≤ 8. Robust to the embedding model and the style-resid variant. |
| G ground truth | agrees with known structure | 1 | #38 content: the clipped forecast of the room contrast (0.069) matches the realized one (0.067) where raw overshoots (0.100). #38 talk: clipping erases the room block (median 0% of raw's contrast kept). |
| H comparative | beats the named rivals | 1 | Beats raw, Ledoit–Wolf to identity (19–20/32) and mean field; ties Ledoit–Wolf constant correlation (mean gain −0.020 / −0.008). |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Holdout not run (confirm dry run passes C1–C3 on stand-ins). |

## Synthetic validation (axis F, before real data; `analysis/synthetic.py`)
Units of 5 days at real counts, N ∈ {4, 8, 16, 32}, W ∈ {4, 8, 16} (content) or 120–480 kept minutes (spins), with the H91 generator. Structures: **(a)** one uniform mode; **(b)** uniform + room mode; **(c)** many weak modes (random pair couplings below the edge); **(d)** (b) with day-to-day loading drift. Each estimator is scored against the true next-day matrix and against the realized next-day matrix.
- **S0:** pure noise → the calibrated edge keeps a spurious mode in ≤ 5–10% of fits.
- **Expected ordering:** (a) E4 ≈ E5 > E2; (b) E5 > E4 > E2; (c) E2/E3 ≥ E5; (d) all shrink toward E1. If (b) does not order as expected at real counts, a real-data E5 loss to E4 is "underpowered".

## Amendment 1 (2026-10-04 ~20:36 UTC; after the synthetic study, before any real-data forecast)
The synthetic study (`analysis/synthetic.py`, 16 units of 5 days per cell; `data/processed/H92-rmt-cleaned-forecast/synthetic/summary*.parquet`) leaves the estimators and rules unchanged. It records what each outcome can mean:
1. **Edge size (S0, pure noise).** The calibrated edge keeps a spurious mode in 3–17% of content fits and 2–13% of talk fits.
2. **Clip vs raw.** Against the realized next day, E5 beats E2 in every structure at N ≥ 8 (mean r_raw +0.04 to +0.26), except a two-room structure at N ≤ 8, where the room mode sits near the edge and clipping deletes it (r_raw −0.02 to −0.49).
3. **Clip vs Ledoit–Wolf constant correlation.** With one uniform mode, E4 and E1 beat E5 by 3–23%. With a real room mode, E5 beats E4 only at N ≥ 16 and W ≥ 8 (E5 best in 39–98% of fits); at N ≤ 8 it loses by 9–32%. With many weak modes or day-to-day drift, E4/E1 win almost everywhere.
4. **Consequence for P2 (scope narrowed, rule unchanged).** A P2 loss in units with N < 16 or W < 8 is expected even if the swarm has a real second mode, so it is uninformative there. P2 is also reported on the **powered units** (median N ≥ 16 and W ≥ 8: regime III #38–#51).
5. **MP edge.** The MP edge keeps more modes than the calibrated edge (k_MP ≥ k_cal) and is slightly better when the second mode sits near the edge (two rooms, N = 8, W = 16: E6 beats E5 by 25%). P5's direction is therefore uncertain at small N.

## What I had seen (disclosure)
As in H91: the H12, H25, H26, H36 and H74 cards. Known to me: content modes exist in 24/24 units (one in 21, two in 3) and are uniform in sign; talk modes in 21/24, separating rooms in 7/10 two-room units; the activity mode is mostly the scheduler (7/24 under the calibrated null); per-pair content correlation is ≈ 0.28 on day means and flat in N (H25); activity per-pair correlation inside the all-present window is 0.005 (H50). Sampling-design counts only: 282 non-holdout content days, median 10 agents and 8 windows per day. No forecast or matrix statistic has been computed on real data.

## Prediction
*Written 2026-10-04 ~20:15 UTC, before the synthetic study and before any forecast on real data. Credences in brackets.*
- **P0 (synthetic, F).** The S0 and ordering checks hold [0.6].
- **P1 (clip beats raw, content).** In both embedding models, mean r_raw > 0 in ≥ 2/3 of eligible periods, and the mean of period means is > 0 with a period-bootstrap CI above 0 [0.8]. Size: r_raw ≈ 0.05–0.25 [0.5].
- **P2 (clip beats the best shrinkage, content; the HH's real claim).** E5 has a lower mean MSE than both E3 and E4 in ≥ 2/3 of eligible periods [0.3]. I expect E4 (constant correlation) to tie E5 within ±2% of MSE, because the content signal is mostly one uniform mode [0.55].
  - **Supported** if P1 and P2 both pass in both models. **Failed** if E5 loses to raw (P1 fails) or loses to E4 in ≥ 2/3 of periods. **Mixed** otherwise.
- **P3 (channels).** Talk: r_raw > 0 in ≥ 2/3 of periods [0.7]; E5 beats E4 in talk more often than in content (talk has room modes) [0.5]. Activity (no real mode after the trim): E5 ≈ E1 ≈ E0 and all beat E2 [0.6].
- **P4 (RMT signature, unfitted).** Spearman(r_raw, q) > 0.3 across target days, per channel [0.55].
- **P5 (edge).** The MP edge keeps more modes than the calibrated edge for content (k_MP > k_cal on ≥ 2/3 of fits), and E5 beats E6 [0.55].
- **P6 (training length).** The expanding window beats the previous-day window for E2 [0.7] and the gap is smaller for E5 [0.5].
- **Multiplicity.** Primary: P1 and P2 (content). P3–P6 are descriptive.
- **Replication rule (period README):** *supported* if E5 has the lowest mean MSE among E2–E5 in the content channel with both models; *failed* if E5's mean MSE exceeds E2's in both models; *mixed* otherwise; *descriptive* if the period has < 2 target days.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G03](goalperiod-subhypotheses/G03/README.md) | replication | mixed | 2 days, N 4; gain vs raw +0.34/+0.41, vs LW-CC -0.01/+0.07 (bge/gte); best E4_lwcc/E1_mean |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | supported | 19 days, N 4; gain vs raw +0.09/+0.12, vs LW-CC +0.05/+0.05 (bge/gte); best E1_mean/E1_mean |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | mixed | 4 days, N 4; gain vs raw +0.02/+0.18, vs LW-CC -0.15/+0.01 (bge/gte); best E1_mean/E1_mean |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | supported (aggregation-sensitive; see Correction 2026-10-04) | 12 days, N 4; gain vs raw +0.19/-0.07, vs LW-CC +0.07/-0.19 (bge/gte; mean of per-day gains); mean MSE E5 lowest in both; best E1_mean/E6_clip_mp |
| [G07](goalperiod-subhypotheses/G07/README.md) | replication | descriptive | 1 days, N 4; gain vs raw +0.25/+0.19, vs LW-CC +0.16/+0.12 (bge/gte); best E5_clip/E1_mean |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | mixed | 16 days, N 4; gain vs raw -0.01/+0.07, vs LW-CC -0.01/+0.04 (bge/gte); best E3_lwi/E3_lwi |
| [G10](goalperiod-subhypotheses/G10/README.md) | replication | mixed | 3 days, N 7; gain vs raw +0.31/+0.28, vs LW-CC +0.04/-0.08 (bge/gte); best E3_lwi/E3_lwi |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | mixed | 4 days, N 7; gain vs raw +0.03/+0.05, vs LW-CC -0.06/-0.07 (bge/gte); best E4_lwcc/E4_lwcc |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication | failed | 3 days, N 7; gain vs raw -0.69/-0.55, vs LW-CC -0.71/-0.55 (bge/gte); best E4_lwcc/E4_lwcc |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | mixed | 9 days, N 6; gain vs raw -0.07/-0.03, vs LW-CC -0.06/-0.05 (bge/gte); best E3_lwi/E3_lwi |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | supported | 4 days, N 7; gain vs raw +0.08/+0.10, vs LW-CC -0.00/+0.03 (bge/gte); best E1_mean/E5_clip |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | supported | 4 days, N 7; gain vs raw +0.04/+0.07, vs LW-CC +0.01/+0.06 (bge/gte); best E5_clip/E5_clip |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | supported | 7 days, N 8; gain vs raw +0.15/+0.14, vs LW-CC +0.09/+0.11 (bge/gte); best E5_clip/E5_clip |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | failed | 8 days, N 7; gain vs raw -0.16/-0.13, vs LW-CC -0.17/-0.14 (bge/gte); best E4_lwcc/E3_lwi |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | mixed | 6 days, N 10; gain vs raw +0.09/+0.06, vs LW-CC +0.03/+0.01 (bge/gte); best E5_clip/E4_lwcc |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | failed | 3 days, N 8; gain vs raw -0.02/+0.02, vs LW-CC -0.03/-0.01 (bge/gte); best E3_lwi/E3_lwi |
| [G23](goalperiod-subhypotheses/G23/README.md) | replication | supported | 4 days, N 10; gain vs raw +0.19/+0.19, vs LW-CC +0.09/+0.12 (bge/gte); best E5_clip/E5_clip |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | supported | 4 days, N 10; gain vs raw +0.22/+0.21, vs LW-CC +0.10/+0.12 (bge/gte); best E1_mean/E5_clip |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | supported | 4 days, N 10; gain vs raw +0.17/+0.12, vs LW-CC +0.12/+0.09 (bge/gte); best E5_clip/E5_clip |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | supported | 3 days, N 10; gain vs raw +0.04/+0.05, vs LW-CC -0.00/+0.01 (bge/gte); best E5_clip/E5_clip |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | supported | 9 days, N 10; gain vs raw +0.09/+0.08, vs LW-CC +0.04/+0.03 (bge/gte); best E5_clip/E5_clip |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | mixed | 3 days, N 11; gain vs raw +0.03/+0.08, vs LW-CC +0.01/+0.04 (bge/gte); best E5_clip/E3_lwi |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | descriptive | 1 days, N 11; gain vs raw +0.11/+0.17, vs LW-CC +0.07/+0.02 (bge/gte); best E5_clip/E1_mean |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | supported | 2 days, N 11; gain vs raw +0.15/+0.19, vs LW-CC +0.04/+0.08 (bge/gte); best E5_clip/E5_clip |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | mixed | 4 days, N 12; gain vs raw -0.03/-0.04, vs LW-CC -0.06/-0.07 (bge/gte); best E6_clip_mp/E6_clip_mp |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | mixed | 2 days, N 12; gain vs raw +0.33/+0.31, vs LW-CC -0.03/+0.04 (bge/gte); best E1_mean/E1_mean |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | mixed | 2 days, N 12; gain vs raw +0.15/+0.21, vs LW-CC -0.04/+0.05 (bge/gte); best E3_lwi/E5_clip |
| [G38](goalperiod-subhypotheses/G38/README.md) | native | failed | 12 days, N 12; gain vs raw +0.18/+0.17, vs LW-CC -0.01/-0.00 (bge/gte); best E3_lwi/E3_lwi |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | mixed | 4 days, N 15; gain vs raw +0.26/+0.23, vs LW-CC -0.07/-0.04 (bge/gte); best E1_mean/E1_mean |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | supported | 4 days, N 15; gain vs raw +0.20/+0.19, vs LW-CC +0.07/+0.07 (bge/gte); best E5_clip/E5_clip |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | mixed | 4 days, N 15; gain vs raw +0.12/+0.07, vs LW-CC +0.04/-0.02 (bge/gte); best E6_clip_mp/E6_clip_mp |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | mixed | 3 days, N 16; gain vs raw +0.31/+0.23, vs LW-CC -0.07/-0.10 (bge/gte); best E1_mean/E1_mean |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | supported | 2 days, N 16; gain vs raw +0.16/+0.20, vs LW-CC +0.04/+0.04 (bge/gte); best E6_clip_mp/E5_clip |
| [G51](goalperiod-subhypotheses/G51/README.md) | native | mixed | 33 days, N 24; gain vs raw +0.20/+0.19, vs LW-CC +0.01/+0.02 (bge/gte); best E5_clip/E5_clip |


## Results
*Round 1, 2026-10-04, non-holdout only. Code: `scheme/{daymat,build}.py`, `analysis/{h92lib,synthetic,run_forecast,evaluate,write_period_folders,figures,confirm}.py`. Data: `data/processed/H92-rmt-cleaned-forecast/` (≈ 12 MB). Figures: `figures/summary_obs.pdf`, `figures/summary_obsb.pdf`.*

**Headline.** Most of a day's agent content correlation matrix is sampling noise. Keeping only the eigenmodes above the calibrated edge (one mode in 84% of fits) forecasts tomorrow's pair correlations 10% better than the raw matrix, and the gain scales with N/T as random-matrix theory predicts. Ledoit–Wolf shrinkage to constant correlation does as well: the persistent structure is one uniform mode. Talk pairs carry no forecastable structure beyond their mean.

**Outcome vs prediction.**

| Prediction | Rule | Observed | Verdict |
| --- | --- | --- | --- |
| P0 synthetic | edge keeps ≤ 5–10% spurious modes; expected orderings | spurious modes 3–17%; orderings hold, two-room advantage only at N ≥ 16, W ≥ 8 | partly |
| P1 clip beats raw (content) | mean gain > 0 in ≥ 2/3 periods, both models; period-mean CI > 0 | 26/32 and 27/32; 0.098 [0.029, 0.156] and 0.106 [0.043, 0.156] | **pass** |
| P2 clip beats best shrinkage | in ≥ 2/3 periods, both models | 17/32 both; vs constant correlation 20/32 and 21/32, mean gain −0.020 and −0.008; powered periods (#42, #51) 1/2 | **fail** (tie within 2%, as predicted) |
| P3 channels | talk gain > 0 in ≥ 2/3; clip beats LW-CC more often in talk; activity: clip ≈ mean ≈ zero, all beat raw | talk 27/30 (0.17 [0.13, 0.23]); clip beats LW-CC in 10/30 talk vs 20/32 content; activity skill of clip 0.00, raw −0.39 | pass / fail / pass |
| P4 RMT signature | Spearman(gain, q) > 0.3 | content 0.46 / 0.45, talk 0.47, activity 0.65 | **pass** |
| P5 edges | k_MP > k_cal in ≥ 2/3; clip(cal) beats clip(MP) | 20–22% (k_MP ≥ k_cal always); mean gain over MP −0.015 / +0.000 | fail |
| P6 training length | expanding beats previous day for raw; smaller gap for clip | raw 79–92% (gain 0.12–0.28); clip −0.08 / −0.09 (content) | pass (the gap reverses) |

Card rule: P1 passes, P2 fails, and clipping does not lose to constant-correlation shrinkage in ≥ 2/3 of periods, so the verdict is **mixed**.

**How much is forecastable.** Median skill against the identity forecast (all pair correlations zero) is 0.29–0.30 for clipping in content, 0.22–0.30 for Ledoit–Wolf, 0.13–0.23 for raw. In talk it is ≤ 0.05 for every estimator and −0.12 for raw; in activity it is ≤ 0 (the activity mode is the scheduler, removed by the trim). The calibrated edge keeps 1 content mode in 84% of fits, 2 in 10–12%; talk keeps none in 40% of fits.

**Natives.** G51 (mixed): the cleaning gain falls as the training window grows (Spearman −0.69 bge, −0.90 gte over 51c/51d/51g), as the 1/T noise law predicts; clipping beats constant-correlation shrinkage in 4/7 and 5/7 #51 units. G38 (failed): in talk, clipping erases the room contrast (kept ≥ 50% on 2/10 days) and loses to shrinkage on 7/10; in content it keeps 78–89% of the contrast and matches the realized room contrast (0.069 vs 0.067) while raw overshoots (0.100).

**Per period.** Replication rule over 34 periods: 14 supported (including #51), 15 mixed (including #38), 3 failed (#12, #19, #21: few agents and few targets), 2 descriptive. The #38 and #51 folders carry their native verdicts (failed, mixed). Mean field E1 or a Ledoit–Wolf estimator is the best single estimator in about half of the periods; clipping is best in 11/32 (bge) and 13/32 (gte).


## Notes
- 2026-10-04 ~20:15 UTC: card written before any real-data forecast (see disclosure). Native predictions (G51, G38) written ~20:12 UTC.
- 2026-10-04 ~20:36 UTC: Amendment 1 after the synthetic study (scope only), before real data.
- Compute: synthetic ~2 min, real forecasts 36 s for 6 channels (one process, BLAS 2 threads).
- `scheme/daymat.py` is an identical copy of H91's (no cross-hypothesis imports); suggested home `infra/shared/day_matrices.py`.
- **Correction (2026-10-04, blind-rater check of G06).** The period verdicts apply the replication rule to *period-mean MSE* (`evaluate.py: E5_lowest_E2_E5`, `E5_beats_raw`). The "gain" columns in the period table and the period READMEs are *means of per-day relative gains* r. The two can disagree in sign when a few high-MSE days dominate the mean MSE. G06 is the clearest case: mean MSE puts E5 lowest in both models, so the verdict is supported, but the gte per-day gains are −0.07 vs raw and −0.19 vs LW-CC. No verdict changes. Sensitivity: judged on the mean per-day gains instead, 7 of 34 period verdicts move: G06, G16, G26 supported → mixed; G20 mixed → supported; G13, G35 mixed → failed; G21 failed → mixed. The count would be 12 supported instead of 14. P1 uses the per-day gains r_raw; P2 and the constant-correlation share use period-mean MSE (`evaluate.py`). Neither changes here.

## Round 2 redirects (2026-10-04)
- **What the direction is really after:** how many persistent collective modes the swarm has once sampling noise is removed; the tie with constant-correlation shrinkage says one.
- **H92-R1.** Add the rotationally invariant estimator (Ledoit–Péché / Bun–Bouchaud–Potters) and a one-mode-plus-rooms factor model.
- **H92-R2.** Forecast with an exponentially weighted training window: cleaned structure drifts, so recency should beat the expanding window.
- **H92-R3.** Use the cleaned top mode as the per-period coupling coordinate on the phase diagram.
