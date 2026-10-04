# H81: Culture beyond composition: the emergent slow mode

**Status:** **exploratory round 1 done (2026-10-04, non-holdout only). Supported in regime I: the village content carries a slow collective mode (τ_u ≈ 23–28 days) beyond composition and the measured goal fields, carried across member turnover; not seen in regime III or inside #51, and it does not jump at roster events.**
- **Slow mode:** cross-goal culture residuals ≤ 14 d apart align (s̄ 0.17 / 0.14) and decay over 3–4 goal periods; contrast D_adjg 0.237 / 0.208 vs S0 95th percentile 0.081 / 0.089 (bge / gte).
- **Not members:** the overlap-adjusted contrast (0.166 / 0.170) and the size-matched turnover-disjoint contrast pass; without Gemini 2.5 Pro ×1.06.
- **Not measured fields:** survives three exogenous covariates and the scaffold-segment restriction (post hoc); unmeasured slow outside drift remains open.
- **Fails:** roster events (percentile 0.08 / 0.14), #51 within-period slow mode (common mode τ ≈ 3 active days), NE33 batch joins.
- Card and predictions written 2026-10-04 20:05 UTC before any real-data statistic; synthetic validation found that the HH's literal null manufactures a slow mode (Amendment A1). `analysis/confirm.py` written and dry-run, **not run**.
**Question (GOALS.md):** **Q3** (is there collective order beyond fields?). It is the composition test of the egregore programme: does the village content vector carry a slow component that its members' personal vectors and the goal fields do not explain?
**Fields:** stat mech (vector spins, slow modes), info theory, sociophysics (cultural evolution)
**Literature:** [Kolchinsky & Wolpert 2018](../../literature/kolchinsky-2018-semantic-information-autonomous-agency.md) (the egregore framing of model 04); [Krakauer et al. 2020](../../literature/krakauer-2020-information-theory-of-individuality.md) (individuality favors the bigger unit, hence size-matched comparisons); [Heylighen 2016](../../literature/heylighen-2016-stigmergy-universal-coordination-mechanism.md) (the record as the carrier). No literature refinement was attached to HH293.
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Population N(t) (day-present); Regime (whitening per regime, never pooled across); Driving / external field (goal text, kickoff, room kickoffs, #51 agent goals, human messages); Agent state, variant *vector*, in H01's named form **agent state (vector), whitened statement mean** (here on DQ5 `style_resid` vectors); **Exogenous drive direction** (removed by projection). New named variants proposed for DEFINITIONS.md (defined under Observables): **personal vector (leave-goal-out)**, **culture residual (composition null)**, **collective share κ (equal-time)**, **slow-mode contrast D_near**, **turnover-disjoint similarity**.
**From:** HH293 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` (egregore section) · **Models:** `physics-models/11-vector-spins/` (primary: slow collective modes of a vector order parameter), `physics-models/14-scaling-and-fluctuations/` (size-matched fluctuation floor), `physics-models/04-semantic-information/` (framing only; no viability function is fitted)
**Data inputs (shared tables first):** DQ5 `embeddings/agent_day_{style_resid,white32,style_resid_period}_{bge_small,gte_modernbert}.npy` + `agent_day.parquet`; shared `goal_fields` (`embeddings/goals.parquet`, `goal_vectors*.npy`, whitened with `embed_models.load_whitener`); `kicks_classified` (human messages) + `embeddings/chat_*.npy` / `chat_index`; `roster` (tenure); `rooms_timeline`; `period_units`; `calendar`; `holdout_mask`.

## Source HH (verbatim from the HH list, including literature refinements)
Culture beyond composition: the emergent slow mode. The cleanest egregore test. Composition null: the village culture vector at time t equals the presence-weighted average of its members' period-invariant personal vectors, each estimated from other periods. Whatever the null misses is collective. Prediction: the residual has a slow mode (weeks to months) that is autocorrelated across goal boundaries and across near-complete turnover, and that shifts at roster events more than composition alone predicts. *Check:* agent-day vectors (DQ5, both models, style residuals); composition-null residual per day; spectral or dynamic-mode analysis of the residual after removing goal-period means; similarity of distant epochs beyond the null. *Kill:* residual variance at the null floor; the village is the sum of its members.
  *Models:* 11, 04 · *Builds on:* H46, H13, H20 · *Periods:* whole span

## Question
After the members' own personal vectors (from other goal periods) and the goal fields are removed, does the village content vector keep a component that is slow (weeks to months), crosses goal boundaries, survives member turnover, and jumps at roster events?

## Design: two layers (Vivian, 2026-10-04)
- **Replication** (role `replication`): the common estimator on every eligible goal period (equal-time collective share κ, O1) and the cross-boundary slow-mode statistics per regime (O2–O4). The slow mode is a cross-period object: the **named exception (c)** applies (the boundary pairs are the object). Each period's culture residual is a per-period estimate; no dynamical model is fitted to pooled periods.
- **Natives** (role `native`): **G51** (a two-month period with private goals: a within-period slow mode with each agent's own goal removed) and **NE33** (with NE32: batch joins inside #51; does the incumbents' residual jump when newcomers arrive?).
- **Robustness required by the brief:** Gemini 2.5 Pro (agent 6) is the only continuous carrier (2025-04-24 → today); every cross-boundary statistic is re-run without it. Size-matched groupings (random m = 4 agent subsets) make regime I (N = 4–12) and regime III (N = 12–32) comparable.

## Model
**From:** `physics-models/11-vector-spins/`.
Agent i's content on PT day d is a vector spin v_{i,d} ∈ ℝ³² (DQ5 regime-whitened, style-residualized statement mean, unit-normalized). The H81 variant is a composition model with a collective slow field:

  v_{i,d} = a_i + h_{G(d)} + w_{b(d)} + u_{b(d)} + e_{i,d}

- a_i: the agent's **personal vector** (weights, family, style leakage; H73's agent constant, u_A 0.55). Period-invariant by assumption (exception (b)).
- h_G: the **exogenous field** of goal period G (goal text, kickoff, room kickoffs, #51 agent goals, human messages). Removed by projection on its measured directions.
- w_b: a period-specific shared topic that the measured directions miss (exchangeable across periods: no memory). This is the field leakage that makes equal-time statistics positive (H25, H24).
- u_b: the **collective slow mode** (culture). An Ornstein–Uhlenbeck vector with correlation time τ_u (weeks), common to whoever is present, independent of who carries it.
- e_{i,d}: agent-day noise, and any individual drift (agent memory, tenure ageing; rival R2).

Order parameter: the **culture residual** u_b, the block mean of the members' residuals. Control parameters: lag Δt between blocks, member overlap J, goal similarity.

**Composition null (HH293):** u_b = 0 and w_b exchangeable. The village vector is then the presence-weighted mean of a_i plus the period field, and the residual has no memory across goal boundaries.

**Rivals.**
- **R1, exogenous slow drift:** consecutive goals resemble each other (operators set themed runs), or the human-message mix drifts. Removed by projecting goal and human-message directions and by adjusting pair similarity for goal similarity.
- **R2, individual drift:** each agent drifts along its own direction over its tenure (memory, H46's context excitation). This makes per-agent residuals slow, but not shared across disjoint members. Separated by the turnover-disjoint statistic (O3).
- **R3, estimator-induced memory:** leave-goal-out personal vectors share their estimation error across all blocks where the agent is present, which correlates residuals of blocks with shared members (more at short lags, where overlap is high). Calibrated by the synthetic S0 null on the real panel.
- **R4, slow scaffold change:** a regime-internal change of prompts or tools shifts everyone's content. Partly removed by staying within regimes; the natural-experiment dates are listed for the reader.

## Data scheme (`scheme/`)
Script: `scheme/build.py` (shared tables only; no text read or written; holdout rows dropped with `common.holdout_mask` and asserted).
- **Inputs:** DQ5 agent-day vectors (three variants × two models), `agent_day.parquet`; `goals.parquet` + goal vectors; `kicks_classified` (`kind == human_message`, `message_id`) → `chat_index` row → raw chat embedding of each model; `roster`; `rooms_timeline`; `period_units`; `calendar`.
- **Transform:**
  1. Eligible agent-days: non-holdout, regime I or III, n_chat + n_intent ≥ 5, agent not 19 (Claude Code), 28 or 30 (fine-tuned leaders, whose weights were trained on village data). Unit-normalize each vector.
  2. **Blocks:** goal period × ISO calendar week (Monday start). Most goals are one week; long goals (#4, #8, #13, #27, #38, #51) split into weeks. A block needs ≥ 3 eligible agents.
  3. **Exogenous directions per goal period G** (regime-whitened with the same model's whitener, unit): kickoff, goal text, each room kickoff, the human-message centroid of G; in #51 also the agent's own `agent_goal` (valid on the day). Orthonormal basis Q_G (QR). Π_G = I − Q_G Q_Gᵀ.
  4. **Personal vector (leave-goal-out):** μ_i^{(−G)} = mean over agent i's eligible days in other goal periods G′ ≠ G of the same regime of Π_{G′} v_{i,d′}. Needs ≥ 3 such days, else agent i is dropped from G's blocks (both from the culture vector and from the null).
  5. **Per-agent residual:** r_{i,b} = Π_G (v̄_{i,b} − μ_i^{(−G)}), v̄_{i,b} the mean of i's eligible days in block b.
- **Output:** `data/processed/H81-culture-beyond-composition/` (`blocks.parquet`: block id, goal, regime, week, mid-date, N, members; `residuals_<model>_<variant>.npz`: r_{i,b} with keys; `directions.npz`; analysis outputs in `replication/`, `natives/`, `synthetic/`; `_provenance.json`).
- **Regimes covered:** I (2025-05-10 → 2026-02-20, non-holdout) and III (2026-03-24 → 2026-09-04, non-holdout). Regime II (3 short periods) is too short for a slow-mode test and is excluded.

## Observables
*Written 2026-10-04 20:05 UTC. Sampling facts already seen: eligible agent-day counts per regime (I 1,214, III 1,858 non-holdout agent-days; median 59 and 36 statements), the roster table with tenures, the non-holdout period units. No content statistic has been computed.*

**O1. Equal-time collective share (per goal period; replication).** κ_G = mean over blocks b ∈ G of Σ_{i≠j} r_{i,b}·r_{j,b} / [(N_b − 1) Σ_i |r_{i,b}|²]: the mean pairwise alignment of the members' residuals, which is 0 when the village vector is its members' sum plus independent noise (the HH's "null floor"). Size-free. Null band: 95% interval of κ under random sign flips of whole agent residuals (destroys alignment, keeps magnitudes). **κ_G mixes field leakage w_b, contemporaneous convergence and culture; it is reported as the upper bound of equal-time collective order, not as culture.** The excess variance ratio X_G = |u_b|² / floor_b (floor_b = Σ_i |r_{i,b}|² / N_b²) is reported too.

**O2. Slow mode across goal boundaries (per regime; card-level).** u_b = mean_i r_{i,b}. For every pair of blocks (b, b′) of the same regime in different goal periods: s(b, b′) = cos(u_b, u_b′); Δt = |mid_b − mid_b′| (calendar days).
- **Slow-mode contrast D_near** = mean s over pairs with Δt ≤ 14 d − mean s over pairs with Δt ≥ 42 d.
- **Adjusted D_near:** the coefficient of the near indicator in OLS of s on [1, near (Δt ≤ 14), mid (14 < Δt < 42), goal similarity cos(k̂_G, k̂_G′), member overlap J(b, b′)] over all cross-goal pairs.
- Profile s̄(Δt) in bins 0–14, 15–28, 29–56, 57–112, > 112 d; descriptive τ_u from s̄(Δt) = A e^{−Δt/τ_u} + s_∞.
- **Primary null:** the synthetic S0 replicate distribution of adjusted D_near on the real panel (handles R3). **Secondary null:** permutation of the blocks' time positions within regime (liberal; ignores R3).

**O3. Across turnover (card-level).** For each cross-goal pair, **turnover-disjoint similarity** s_⊥(b, b′) = cos(ū_{b∖b′}, ū_{b′∖b}), where ū_{b∖b′} averages r_{i,b} over members of b absent from b′ (≥ 2 on each side). D_near^⊥ as in O2 on s_⊥. Under R2 (individual drift) D_near^⊥ ≈ 0; under culture D_near^⊥ ≈ D_near. Also the **distant-epoch similarity**: mean s and s_⊥ over pairs with Δt ≥ 90 d against the S0 null mean.

**O4. Shifts at roster events (card-level, within goals).** Day-level residual R_d = mean_i Π_G(v_{i,d} − μ_i^{(−G)}) over the day's eligible agents. At every within-goal day boundary (d−1 → d, same goal, both days eligible) the jump J_d = |R_d − R_{d−1}| scaled by its noise floor √(floor_d + floor_{d−1}). Roster boundaries: a roster join or leave (roster table; Claude Code excluded) between the two days. Placebos: all other within-goal day boundaries of the same regime. ρ_roster = median scaled jump at roster boundaries / median at placebos; percentile of the roster median among 2,000 placebo draws of the same size.

**O5. Robustness.** O2–O3 (a) without Gemini 2.5 Pro (agent 6 dropped everywhere); (b) size-matched: u_b from random 4-agent subsets (50 draws, statistic averaged); (c) both embedding models; (d) variants white32 (no style removal) and style_resid_period; (e) agent-day weights by statement count.

**O6. Natives.**
- **G51 (within-period slow mode, private goals).** #51 non-holdout days (07-06 → 09-04). Each agent's residual is r_{i,d} = Π_{51,i}(v_{i,d} − m_i), m_i the agent's own #51 mean (exception: newcomers have no other non-holdout period; within-period demeaning keeps each agent's own drift but removes its level). Cross-agent lagged alignment L(k) = mean over i ≠ j and day pairs at lag k active days of r_{i,d}·r_{j,d+k}, normalized by the mean |r|². **L_slow** = mean L(k) for k = 5–15 active days. Null: each agent's day series circularly shifted by an independent offset of ≥ 5 active days (DQ8 block-shift idea at day resolution; 1,000 draws). Equal-time L(0) is reported but is not culture (day fields, convergence).
- **NE33 (+NE32).** Incumbents only (agents present ≥ 3 eligible days before the join). Incumbent residual centroid jump at the batch-join day boundary (NE32: 07-08 → 07-09 and 07-09 → 07-10; NE33: 09-02 → 09-03 and 09-03 → 09-04), scaled as in O4, as a percentile among all other #51 within-period day boundaries (placebo). Composition alone predicts no incumbent jump.

**Multiplicity.** The card verdict uses P2–P5 on regime I and III separately; per-period κ_G rows are replication points, not independent tests.

## Null / baseline
*Written 2026-10-04 20:05 UTC, before any real-data content statistic.*
- **Composition null (the HH's):** u_b = 0, exchangeable period fields w_b. Implemented as the synthetic S0 on the real panel: real presence pattern (agents × blocks × days), planted personal vectors, goal-level and block-level fields at the real equal-time scale, real noise scale; the full pipeline (personal vectors, projections, statistics) runs unchanged. 200 replicates per regime.
- **Individual-drift rival (S2):** no common mode; each agent drifts linearly along its own random direction over its tenure, with the same slow variance as S1.
- **Planted culture (S1):** an OU slow mode u_b with τ_u = 28 d and variance share s ∈ {0.1, 0.25, 0.5} of the block-field variance.
- **Permutation null (secondary, liberal):** block time positions permuted within regime.
- **κ null:** sign flips of whole agent residuals within block.
- **Roster null:** placebo within-goal day boundaries (empirical; H20's lesson that fitted stationary nulls are too narrow at boundaries).

## Impostor table (STANDARDS.md §1)
| Impostor | How it could fake this result | How H81 removes it | Status |
| --- | --- | --- | --- |
| Scheduler field | day length and activity change the chat/intention mix and statement counts, which moves day-level means | agent-day means of unit statement vectors (each agent counts once per day); eligibility ≥ 5 statements; O2/O3 compare blocks weeks apart, so day-edge synchrony cannot carry a lagged cross-goal similarity; weighting variant (O5e) | removed for O2–O3; partly for O1/O4 (day-level) |
| Exogenous field (goal, kickoff, operator) | consecutive goals in themed runs make adjacent blocks similar | projection on kickoff, goal text, room kickoffs, #51 agent goals and the human-message centroid of each period; pair regression adjusts for goal similarity; S0 carries period fields at the real scale | partly (directions miss part of the topic field; H25: at most a fifth removed by operator directions) |
| Shared model priors (family, style) | members with similar priors make the village look coherent; a changing family mix fakes a slow drift | DQ5 `style_resid`; leave-goal-out personal vectors remove each agent's own prior, including family; composition changes enter the null; turnover-disjoint statistic; variant without style removal reported | removed (agent-level); family-level drift partly (a family can drift as a whole) |
| Contemporaneous convergence | agents answering the same situation write alike without reading each other | O2/O3 never compare equal-time vectors across agents within one block; lagged cross-goal similarity cannot come from co-generation; O1 κ (equal-time) is labelled as including it | removed for O2/O3/G51 lagged; open for O1 |

## Prediction
*Written 2026-10-04 20:05 UTC, before running the analysis on real data.*

The HH predicts a slow mode. My prior is low (about 0.25): H20 found content stationary after a 4-day kickoff relaxation, H54 found no trace of the previous kickoff on day 1, H15 found ≈ 0 day-scale semantic information in memory, and H01/H58 found no collective unit.

- **P1 equal-time share (descriptive, replication):** κ_G > its sign-flip band in ≥ 80% of eligible periods (field leakage plus convergence). This is not a culture claim. *Against:* κ_G within the band in > 20% of periods, which would mean the members' residuals are independent even at equal time.
- **P2 slow mode (headline):** adjusted D_near exceeds the S0 95th percentile in regime I or III, in both embedding models, and s̄(Δt) falls with Δt over 2–8 weeks (descriptive τ_u ≥ 14 d). *Against:* adjusted D_near inside the S0 band in both regimes and both models: no slow mode beyond composition and goal fields.
- **P3 across turnover:** in each regime where P2 passes, D_near^⊥ exceeds the S0 95th percentile and is ≥ ½ D_near. *Against:* D_near^⊥ ≈ 0 while D_near > 0: the slow mode is carried by members (R2), not by the village.
- **P4 roster events:** ρ_roster ≥ 1.5 with placebo percentile ≥ 0.95 (regime I and III pooled over events, each regime also reported). *Against:* percentile < 0.9.
- **P5 Gemini-free and size-matched:** adjusted D_near keeps ≥ 50% of its value without agent 6 and in the size-matched variant.
- **Kill (HH):** P2 fails with synthetic power ≥ 0.8 at the S1 share that matters (s = 0.25) in the regime(s) tested. Without that power the verdict is **inconclusive**, not failed.
- **Overall reading (fixed now).** **Supported:** P2 and P3 pass in at least one regime with both models, and P5 holds. **Mixed:** P2 passes but P3 or P5 fails, or only one model passes. **Failed:** P2 fails with power ≥ 0.8. P1 and P4 are reported but do not decide the verdict.

**Natives (dated predictions also in each folder).**
- **N1 G51:** L_slow above the circular-shift 95th percentile. *Against:* inside the band. Prior 0.3.
- **N2 NE33 (+NE32):** the incumbents' residual jump at the batch-join boundaries sits at placebo percentile ≥ 0.95 (at least one of the two events, the other ≥ 0.8). *Against:* both < 0.9. Prior 0.35.

## Synthetic validation (axis F; run 2026-10-04 20:10–20:15 UTC, before any real-data content statistic)
`analysis/synthetic.py` → `data/processed/H81-culture-beyond-composition/synthetic/synthetic_<model>.json`. Village sampling: the real eligible agent-day panel of each regime (who is present on which day, block structure, goal boundaries, real exogenous directions). Planted parts use the real covariances of the projected vectors (agent, goal and block parts; anisotropic, H20's pitfall) and real agent-day residuals permuted across rows. S0: i.i.d. goal and block fields. S1: an OU slow mode with τ_u = 28 d taking a share s of the goal-field covariance. S2: individual linear drift over each agent's tenure (share s), no common mode. 200 S0 and 100 other replicates per regime and model.

**First run, literal HH null (plain leave-goal-out means, block-equal centering, block-pair weights):** under S0 the regime-III D_near was **+0.37** and the far-epoch similarity −0.36. The cause: #51 holds ~40% of regime-III agent-days, so every non-#51 personal vector is mostly the #51 village state, and the residuals of all non-#51 blocks share −c₅₁. The literal composition null manufactures a slow mode. This led to Amendments A1–A2.

**After A1–A3 (both models; S0 95th percentiles and pass rates):**

| Regime | Statistic | S0 q95 (bge / gte) | S1 s = 0.1 | S1 s = 0.25 | S1 s = 0.5 | S2 s = 0.25 | S2 s = 0.5 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| I | D_adjg (goal-adjusted) | 0.081 / 0.089 | 0.20 / 0.22 | 0.69 / 0.67 | **0.99 / 0.96** | 0.42 / 0.32 | 0.74 / 0.79 |
| I | D_adj (goal + overlap) | 0.100 / 0.099 | 0.14 / 0.15 | 0.32 / 0.43 | **0.78 / 0.82** | 0.13 / 0.03 | 0.03 / 0.06 |
| I | D_near⊥ (turnover-disjoint) | 0.247 / 0.241 | 0.03 / 0.10 | 0.21 / 0.17 | 0.40 / 0.31 | 0.04 / 0.11 | 0.09 / 0.04 |
| III | D_adjg | 0.245 / 0.250 | 0.11 / 0.04 | 0.14 / 0.23 | 0.42 / 0.37 | 0.03 / 0.01 | 0.08 / 0.11 |
| III | D_adj | 0.270 / 0.304 | 0.12 / 0.06 | 0.17 / 0.11 | 0.30 / 0.24 | 0.05 / 0.04 | 0.10 / 0.07 |

Readings: (1) after A1 the S0 bias is ≈ 0 (regime I D_adjg mean 0.001 / 0.003; regime III 0.023 / 0.010). (2) Regime I has power ≥ 0.8 for a slow mode carrying half the period-field variance (s = 0.5), not for s = 0.25 (0.67–0.69). (3) Individual drift (S2) passes D_adjg (0.32–0.79) but not the overlap-adjusted D_adj (≤ 0.13): adjusting for member overlap separates a shared slow mode from member-carried drift. (4) The turnover-disjoint statistic has little power (≤ 0.40). (5) Regime III (9 goals) has power ≤ 0.42 at s = 0.5: it cannot support a negative.

## Amendments (2026-10-04 20:17 UTC, after the synthetic validation, before any real-data content statistic)
- **A1 (composition null estimator).** Personal vectors come from a two-way fixed-effects fit (agent + goal effects, weights = agent-days) on the agent's other goals of the regime, not from plain means; block culture vectors are centered on their goal-equal-weight mean; every goal pair carries total weight 1 in the pair statistics. The literal HH null is kept as `METHOD = "mean"` and reported as a sensitivity. Reason: the S0 artifact above.
- **A2 (turnover-disjoint similarity, one-sided).** s_⊥ compares one block with the members of the other block who are absent from the first (≥ 2), averaged over both directions. Regime III has almost no two-sided disjoint pairs.
- **A3 (primary statistics).** P2 uses **D_adjg** (adjusted for goal similarity only). **P3 uses D_adj** (adjusted for goal similarity and member overlap J), which keeps power 0.78–0.82 at s = 0.5 while rejecting individual drift (≤ 0.13). D_near⊥ is reported, not decisive (power ≤ 0.40).
- **A4 (power and the kill).** The effect that matters becomes s = 0.5 in regime I (power 0.96–0.99), because s = 0.25 has power 0.67–0.69. A negative P2 in regime I is "failed" for slow modes with s ≥ 0.5 and "inconclusive" below. Regime III results are descriptive for negatives (power ≤ 0.42).

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G02](goalperiod-subhypotheses/G02/README.md) | replication | descriptive | regime I, N 4: κ 0.51 / 0.65 (bge / gte; null 97.5% 0.51); excess ratio 2.5. |
| [G03](goalperiod-subhypotheses/G03/README.md) | replication | descriptive | regime I, N 4: κ 0.58 / 0.57 (bge / gte; null 97.5% 0.58); excess ratio 2.7. |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | descriptive | regime I, N 5: κ 0.56 / 0.66 (bge / gte; null 97.5% 0.20); excess ratio 2.8. |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | descriptive | regime I, N 4: κ 0.39 / 0.41 (bge / gte; null 97.5% 0.33); excess ratio 2.2. |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | descriptive | regime I, N 4: κ 0.52 / 0.60 (bge / gte; null 97.5% 0.26); excess ratio 2.6. |
| [G07](goalperiod-subhypotheses/G07/README.md) | replication | descriptive | regime I, N 4: κ 0.56 / 0.67 (bge / gte; null 97.5% 0.56); excess ratio 2.7. |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | descriptive | regime I, N 4: κ 0.56 / 0.55 (bge / gte; null 97.5% 0.25); excess ratio 2.7. |
| [G10](goalperiod-subhypotheses/G10/README.md) | replication | descriptive | regime I, N 7: κ 0.40 / 0.37 (bge / gte; null 97.5% 0.40); excess ratio 3.4. |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | descriptive | regime I, N 7: κ 0.32 / 0.33 (bge / gte; null 97.5% 0.17); excess ratio 2.9. |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication | descriptive | regime I, N 7: κ 0.54 / 0.66 (bge / gte; null 97.5% 0.31); excess ratio 4.2. |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | descriptive | regime I, N 6: κ 0.29 / 0.32 (bge / gte; null 97.5% 0.17); excess ratio 2.5. |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | descriptive | regime I, N 7: κ 0.36 / 0.41 (bge / gte; null 97.5% 0.30); excess ratio 3.2. |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | descriptive | regime I, N 7: κ 0.52 / 0.53 (bge / gte; null 97.5% 0.35); excess ratio 4.1. |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | descriptive | regime I, N 8: κ 0.56 / 0.60 (bge / gte; null 97.5% 0.19); excess ratio 5.0. |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | descriptive | regime I, N 8: κ 0.64 / 0.63 (bge / gte; null 97.5% 0.30); excess ratio 5.2. |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | descriptive | regime I, N 10: κ 0.43 / 0.52 (bge / gte; null 97.5% 0.13); excess ratio 4.6. |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | descriptive | regime I, N 9: κ 0.61 / 0.61 (bge / gte; null 97.5% 0.30); excess ratio 5.9. |
| [G23](goalperiod-subhypotheses/G23/README.md) | replication | descriptive | regime I, N 10: κ 0.52 / 0.66 (bge / gte; null 97.5% 0.27); excess ratio 5.7. |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | descriptive | regime I, N 10: κ 0.44 / 0.41 (bge / gte; null 97.5% 0.21); excess ratio 5.0. |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | descriptive | regime I, N 10: κ 0.77 / 0.82 (bge / gte; null 97.5% 0.29); excess ratio 7.9. |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | descriptive | regime I, N 10: κ 0.67 / 0.72 (bge / gte; null 97.5% 0.22); excess ratio 7.0. |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | descriptive | regime I, N 10: κ 0.72 / 0.78 (bge / gte; null 97.5% 0.19); excess ratio 7.4. |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | descriptive | regime I, N 11: κ 0.72 / 0.79 (bge / gte; null 97.5% 0.27); excess ratio 8.2. |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | descriptive | regime I, N 11: κ 0.64 / 0.61 (bge / gte; null 97.5% 0.29); excess ratio 7.4. |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | descriptive | regime III, N 12: κ 0.43 / 0.40 (bge / gte; null 97.5% 0.17); excess ratio 5.7. |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | descriptive | regime III, N 12: κ 0.25 / 0.23 (bge / gte; null 97.5% 0.11); excess ratio 3.7. |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | descriptive | regime III, N 14: κ 0.17 / 0.17 (bge / gte; null 97.5% 0.06); excess ratio 3.0. |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | descriptive | regime III, N 15: κ 0.25 / 0.28 (bge / gte; null 97.5% 0.08); excess ratio 4.5. |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | descriptive | regime III, N 15: κ 0.38 / 0.41 (bge / gte; null 97.5% 0.15); excess ratio 6.3. |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | descriptive | regime III, N 15: κ 0.26 / 0.16 (bge / gte; null 97.5% 0.09); excess ratio 4.7. |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | descriptive | regime III, N 16: κ 0.42 / 0.45 (bge / gte; null 97.5% 0.13); excess ratio 7.2. |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | descriptive | regime III, N 17: κ 0.15 / 0.15 (bge / gte; null 97.5% 0.08); excess ratio 3.4. |
| [G51](goalperiod-subhypotheses/G51/README.md) | native | failed | regime III, N 16: κ 0.09 / 0.07 (bge / gte; null 97.5% 0.01); excess ratio 2.3. Native: L_slow −0.005 / −0.004 (null 95th +0.001); common mode τ ≈ 2 active days |
| [NE33](goalperiod-subhypotheses/NE33/README.md) | native | failed | stayer-jump percentiles 0.86 / 0.78 (07-09), 0.89 / 0.72 (07-10), 0.83 / 0.53 (09-03), 0.17 / 0.14 (09-04) |
| local: regime I span | replication | supported | D_adjg 0.237 / 0.208 (S0 q95 0.081 / 0.089); D_adj 0.166 / 0.170; τ_u 28 / 23 d |
| local: regime III span | replication | mixed | D_adjg 0.256 / 0.275 (q95 0.245 / 0.250); size-matched fails |

## Outcome vs prediction
*Run 2026-10-04 20:24–20:35 UTC (`analysis/replication.py`, `analysis/natives.py`, `analysis/posthoc.py`). Non-holdout only. Thresholds are the S0 95th percentiles of Amendments A1–A4.*

| Prediction | Observed (bge / gte) | Verdict |
| --- | --- | --- |
| P1 κ above the sign-flip band in ≥ 80% of periods (descriptive) | 29/33 and 31/33 periods; median κ 0.51 / 0.53 (regime I 0.55 / 0.60, regime III 0.25 / 0.23); every miss is a 4-agent period, where the sign-flip null cannot reach p < 1/16 | **pass** (not a culture claim) |
| P2 slow mode: D_adjg > S0 q95 in regime I or III, both models | regime I **0.237 / 0.208** (q95 0.081 / 0.089; S0 mean 0.001 / 0.003; permutation p ≤ 0.001); regime III 0.256 / 0.275 (q95 0.245 / 0.250) | **pass** (regime I; regime III marginal) |
| P2 shape: s̄(Δt) falls over 2–8 weeks, τ_u ≥ 14 d | s̄ = 0.17 / 0.14 at 0–14 d, 0.04 / 0.03 at 14–28 d, ≈ 0 at 28–56 d, −0.06 to −0.09 beyond; τ_u = 28 ± 5 / 23 ± 4 d | **pass** |
| P3 across turnover (A3: overlap-adjusted D_adj > S0 q95) | regime I **0.166 / 0.170** (q95 0.100 / 0.099); regime III 0.260 / 0.332 (q95 0.271 / 0.305); turnover-disjoint D_near⊥ 0.115 / 0.075 (q95 0.25, power ≤ 0.4) but 0.188 / 0.156 size-matched (q95 0.078 / 0.054) | **pass** (regime I) |
| P4 roster events: ρ ≥ 1.5, placebo percentile ≥ 0.95 | 22 within-goal events: ρ 0.90 / 0.94, percentile 0.08 / 0.14 (regime I alone: ρ 1.35 / 1.22, 0.98 / 0.91) | **fail** |
| P5 Gemini-free and size-matched keep ≥ 50% | regime I without Gemini 2.5 Pro: 0.251 / 0.220 (×1.06); size-matched m = 4: 0.213 / 0.200 (×0.90 / 0.96); all pass their own S0 | **pass** |
| N1 G51: L_slow above the circular-shift band | −0.005 / −0.004 (band 95th +0.001); post hoc power: a τ = 20 d mode with share 0.05 gives +0.002 | **failed** |
| N2 NE33 (+NE32): stayer jump percentile ≥ 0.95 | 0.86 / 0.78 (07-09), 0.89 / 0.72 (07-10), 0.83 / 0.53 (09-03), 0.17 / 0.14 (09-04) | **failed** |

**Overall (pre-registered reading, amended rules A3–A4):** P2 and P3 pass in regime I with both models, and P5 holds, so H81 is **supported in regime I**. Regime III is marginal and fails size-matched (inconclusive by A4). The roster and #51 tests fail: the slow mode does not jump at roster events and does not appear inside #51.

## Post hoc checks (labelled; written after the replication result, `analysis/posthoc.py`)
- **PH1, scaffold steps (R4).** Within scaffold segments (split at NE04 2025-09-05 and NE08 2025-12-10; 299 pairs) the slow mode stays: D_adjg 0.157 / 0.154 (own S0 q95 0.077 / 0.078); D_adj 0.141 / 0.144 (q95 0.121 / 0.089). At matched lag (14–56 d), pairs inside a segment are more similar than pairs across a step by 0.075 / 0.088 (S0 q95 0.086 / 0.105): the steps account for at most about a third of the contrast.
- **PH2, exogenous slow drift (R1).** With three exogenous similarity covariates (kickoff, goal text, human-message centroid) D_adjg stays 0.237 / 0.209 (S0 q95 0.071 / 0.066). Measured exogenous directions do not explain it.
- **PH3, G51 native power.** On the real #51 panel, a common OU mode with τ = 20 active days and 5% of the residual variance gives L_slow +0.002 (5–95%: −0.001 to +0.004); a τ = 3 d mode with 5% gives L_slow −0.0035 and L(1–4) 0.016. The real values (L_slow −0.005, L(1–4) 0.015) match the τ = 3 d case. Inside #51, the common mode lives about 3 active days; a slow component of ≥ 5% is excluded.
- **Literal HH null (sensitivity).** With plain leave-goal-out means (the HH's wording) regime I D_adjg is 0.110 / 0.099 against an S0 q95 of −0.009 / −0.002: same sign, half the size, because the plain means fold other goals' village states into the personal vectors.

## Results
**1. Equal time: the village is more than the sum of its members, but that is mostly field.** After the members' leave-goal-out personal vectors and the measured exogenous directions are removed, members' residuals still align: κ = 0.55 / 0.60 in regime I and 0.25 / 0.23 in regime III, and the village residual is about 4 times its independent-agent floor. This equal-time order includes topic fields that the kickoff, goal and human-message directions miss and contemporaneous convergence (H25, H57). It is not evidence for culture by itself.

**2. A slow collective mode exists in regime I.** Culture residuals of blocks in different goal periods are similar when the blocks are ≤ 14 days apart (s̄ = 0.17 / 0.14) and not when they are ≥ 4 weeks apart. The decay time is τ_u = 28 ± 5 d (bge) and 23 ± 4 d (gte), i.e. 3–4 goal periods. The contrast is 3× the S0 95th percentile and matches the planted s = 0.5 scenario (D_adjg 0.225), i.e. a slow mode carrying about half of the between-period residual variance. It survives the second embedding model, style removal at either level, no style removal, n_stat weighting, removing the human-message direction, three exogenous covariates, the scaffold-segment restriction and dropping Gemini 2.5 Pro (×1.06).

**3. It is not member-carried drift.** Individual drift (S2) passes the goal-adjusted contrast but not the overlap-adjusted one (pass rate ≤ 0.13). The real overlap-adjusted contrast passes (0.166 / 0.170), and the size-matched turnover-disjoint contrast, which compares agents absent from the other block, passes as well (0.188 / 0.156, q95 0.078 / 0.054). The mode is carried across member turnover.

**4. It does not jump at roster events, and it is not visible inside #51 or in regime III.** Within-goal roster joins and leaves move the residual no more than ordinary day boundaries (pooled percentile 0.08 / 0.14). Inside #51 the cross-agent common mode decays within ≈ 3 active days, with a slow component excluded at 5% of the variance. Regime III (9 goals) passes P2 only at the threshold and fails size-matched. The slow mode is therefore a regime-I (chat-era, 4–12 agents, May 2025 → Feb 2026) property, or regime III lacks the goals to show it (power ≤ 0.42).

**5. What it is not, and what it may be.** The slow mode is not the measured goal field, the human messages, the scaffold steps, Gemini 2.5 Pro or member drift. It is consistent with a shared, slowly changing record (village sites, repos, history documents, running jokes) that every member reads, which is the HH's stigmergic reading. It is equally consistent with an unmeasured slow exogenous drift (operator style, the outside world, tool and model releases discussed in chat). The observational data cannot separate these.

Figures: `figures/summary_obs.pdf` (profile s̄(Δt) with the S0 band; D_adjg real vs null and planted), `figures/summary_obsb.pdf` (synthetic pass rates for culture vs drift; κ per period). Data: `data/processed/H81-culture-beyond-composition/` (`replication/`, `natives/`, `posthoc/`, `synthetic/`, `confirm/confirm_dryrun.json`). Estimates: 88 rows in `per_period_estimates` (hypothesis H81).

## Faithfulness scorecard
*Round 1, 2026-10-04.*
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R1 exogenous slow drift; R2 individual drift; R3 estimator-induced memory; R4 scaffold drift.
**Locked holdout used for confirmation:** none yet (`analysis/confirm.py`, dry-run only).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Agent-day DQ5 vectors, shared goal fields, human messages, roster; personal vectors assume period invariance (exception (b), not tested per agent). Holds in regime I only; regime III marginal. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | OU slow mode fits the profile shape (τ_u 23–28 d; far-epoch similarity −0.08 as in planted s = 0.5). Stationarity within regime I assumed; steps account for ≤ 1/3. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 2 | Beats S0 (composition + exchangeable fields, real panel) by 3×, the permutation null (p ≤ 0.001) and the literal HH null; both models. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | Decay shape and the negative far-epoch similarity match the planted OU; the roster-jump signature fails. |
| E interventional | predicts the change across a natural experiment | 0 | Roster events (22) and NE32/NE33 batch joins show no jump. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 | Synthetic at real counts found the literal-null artifact (+0.37) and fixed it (A1); power 0.96–0.99 at s = 0.5; 7 preprocessing variants agree. |
| G ground truth | agrees with known structure | 1 | Scaffold steps and Gemini removal leave it; no labelled "culture" ground truth exists. |
| H comparative | beats the named rivals | 1 | Beats R2 (overlap-adjusted and size-matched disjoint), R3 (S0), R4 (within segments), measured R1; unmeasured exogenous drift remains. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Regime III marginal, #51 none; holdout not run. |

## Confirmatory predictions (written 2026-10-04 20:38 UTC after round 1, before any holdout use; `analysis/confirm.py`, dry-run only, **not run**)
Targets: held-out goal periods inside regime I (#9, #14, #15, #22, #28, #29) and regime III (#43, #45–#50), as blocks paired with every other block (new pairs only).
- **C1:** regime I D_adjg > S0 q95 in both models. **C2:** regime I D_adj (overlap-adjusted) > S0 q95 in both models. **C3 (descriptive):** regime III as in round 1 (marginal).
- Dry run on stand-ins (I: #16, #23, #30; III: #39, #44): code paths run; C1 passes in bge and not in gte with 3 stand-in blocks, which shows that few held-out blocks give a weak test.
- **Reuse disclosure:** H20 and H54 target the same regime-I held-out goals with day-level content statistics (different estimator family).

## Caveats
- **Exogenous drift is not excluded.** Only measured directions (kickoff, goal text, human messages) and scaffold steps are controlled. A slow outside drive that all agents read (news, model releases, operator mood) would look the same.
- **The literal HH null is biased** (it manufactured +0.37 in regime III synthetics). The two-way FE fix assumes additive agent and goal effects.
- **Regime I has 4–12 agents**; κ cannot be tested at N = 4 with sign flips.
- **Turnover-disjoint statistics have low power** unless size-matched; P3 rests on the overlap-adjusted contrast.
- **τ_u is descriptive** (one fit per regime; goal-pair weights).
- The roster test pools joins and leaves of very different agents.

## Round 2 redirects (2026-10-04)
*Proposed by the round-1 agent; the coordinator may revise.*
- **Where round 1 went sideways:** the HH's literal composition null manufactures a slow mode when one goal period dominates an agent's history; the two-way FE estimator is the fix every composition test should use.
- **What the direction is really after:** a village-level state variable that persists for weeks and survives turnover, and what carries it.
- **H81-R1. Name the carrier.** Regress the culture residual on the content of long-lived artifacts (village sites, history documents, repos) read in the context ledger, vs posted-but-unread artifact content (in-flight placebo). A record-borne mode should follow what was read.
- **H81-R2. Exogenous drift probe.** Project the slow mode onto calendar-dated outside topics (model names, release events) and onto operator-message style beyond the centroid direction.
- **H81-R3. Regime III with more units.** Use weekly blocks inside #38 and #51 with agent-goal removal and the held-out #45–#50 at confirmation; check whether the τ ≈ 3 d common mode of #51 is the regime-III form of the same object.
- **H81-R4. Link to H82.** Fit one OU model to the boundary remanence (H82) and the block similarity profile together.

## Notes
- 2026-10-04: a static village identity (a culture vector constant over a regime) is absorbed by the leave-goal-out personal vectors and by the regime whitening center, so H81 can detect only a time-varying culture. A static village identity is H83's (HH292) question.
- 2026-10-04: the first drafts carried hand-written timestamps (20:20–21:15 UTC) that ran ahead of the clock. They were corrected at 20:24 UTC from file modification times: card 20:05, synthetic 20:10–20:15, amendments 20:17, native folders 20:18, replication 20:24–20:27.
- 2026-10-04: runs used one process with numpy and polars at 2 threads. Data in `data/processed/H81-culture-beyond-composition/` (~3 MB) with `_provenance.json`. No code is imported from another hypothesis.
- 2026-10-04: **Correction (2026-10-04, blind-rater check).** The summary telos said "half of the period-to-period content variance beyond the goal fields is this slow mode". That share is not measured. It is inferred because the observed regime-I contrast (D_adjg 0.237 / 0.208) matches the planted S1 scenario with s = 0.5 (Results 2: "matches the planted s = 0.5 scenario … i.e. a slow mode carrying about half"). The telos now states it as an inference. No result changes.
