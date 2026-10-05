# H57: Copying beats transformation when the backlog is large

**Status:** round 1 done (2026-10-04): **refuted as stated.**
- **Pre-registered slopes:** read-set echo vs backlog is negative in 31/35 non-holdout periods (pooled −0.013 per doubling of k, bge). But this is an artifact: agents posting at the same moment write near-identical messages without reading each other (*contemporaneous convergence*), which the pre-registered chance correction mishandles.
- **Upper bound:** the most generous estimator, the raw read-set echo, rises by at most +0.0016 [0.0009, 0.0022] per doubling (bge; gte +0.0012). That is ≈ 5% of the synthetic H57 effect and mostly or wholly chance growth.
- **No copy share to rise:** at the message level, agents almost never near-copy the message they address (0.1–2%), so the Kolchinsky copy share of addressed transmission is ≈ 0 at every backlog (T = 0; Stouffer p 1.0).
- **Native tests** (NE42 merge/split, NE41 erasures, #51 N sweep) all fail.
- Scorecard A1 B1 C0 D0 E0 F1 G1 H0 I0. `analysis/confirm.py` written and dry-run, not run.

**Fields:** info theory, sociophysics, dynamics
**Literature:** Kolchinsky & Corominas-Murtra 2020 (copy vs transformation information; PDF not in `literature/`, definition used through `physics-models/08-copying-vs-transformation/` and `infra/shared/copy_info.py`, unverified against the paper); [Kolchinsky 2024](../../literature/kolchinsky-2024-dissipation-does-not-bound-replicator-rates.md) (a warning against assuming thermodynamic bounds on copying, relevant to the "copying is cheap" reading).
**Definitions used:** Copy information (fork variant), in a new named variant *Copy information (read-set channel, message-level coding)*; Exposure (turn read-out) via the context ledger; Regime; Agent; Interaction (broadcast), with the reply control as *Interaction (addressed)* = B names the author of an item it read. New named variants proposed for `physics-models/DEFINITIONS.md` (not edited; outside H57's scope), defined under Observables: *Backlog (in-context read set)*, *Mutually invisible (in-flight) set*, *Echo (read-set near-copy)*, *Copy information (read-set channel, message-level coding)*, *Contemporaneous convergence*.
**From:** HH171 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/08-copying-vs-transformation/`, `physics-models/03-contagion/`
**Data inputs (shared tables first):** DQ1 context ledger (`context_ledger_turns`, `context_ledger_items`), DQ5 (`statement_flags`, bge-small and gte-modernbert embeddings, regime whiteners), H34 hashed markers (read-only), DQ2 `reply_pairs` (`parent`, `n_pool`), `chat_mentions_clean`, `copy_info.py`, `period_units`, `goals` (kickoff vectors).

## Standards (2026-10-04)
*Documentation pass against `STANDARDS.md`. No analysis was re-run. H57 has no round-1b section; round 1 already ran on the corrected inputs.*

**Question served:** Q2. The card separates copying through reading from contemporaneous convergence, and finds most near-duplication is convergence. Q1 second: verbatim reuse of read content is the real, small copying channel.

| Impostor | Relevant? | How it was handled | Status |
| --- | --- | --- | --- |
| Scheduler field | partly | Within-period slopes with agent × unit fixed effects; day fixed effects and an early × log k term (rival a). No activity statistic. | removed |
| Exogenous field (kickoff/goal/operator) | yes | Rival b (shared source): templated statements, kickoff-echo statements and common markers are dropped; the #18 positive turns negative when filtered. | removed |
| Shared model priors | partly | Agent × unit fixed effects; both embedding models agree; family slopes in #51 are all small (axis A). | removed |
| Contemporaneous convergence | yes | The impostor is the object. The mutually invisible (in-flight) set is the chance baseline; lag profiles compare read with unread pairs at matched lag (Amendment 2). The lag-matched estimator is post hoc. | removed |

**Inputs:** round 1 uses the context ledger, DQ5 `statement_flags` and both embeddings, H34's markers and DQ2 (descriptive only). Activity bins, work and failures are not inputs. Still old: the `addressed` control uses `chat_mentions_clean`, not the leading-@ target.

**Two layers:** 34 replication folders. Native tests: 3 (`G51`, `NE42` and `NE41`), all failed.

**Confirm script:** `analysis/confirm.py` exists, dry-run only, built on ledger inputs. It freezes the refutation and the post hoc bounds (C1 raw echo, C3 in-flight vs read at < 15 s, C4 lag-matched), not the invalid pre-registered estimator. No re-freeze needed.

## Question
Does the copy-to-transformation information ratio between agents rise with backlog, so that agents echo rather than transform under load?

## Design: two layers (Vivian, 2026-10-04; see `infra/data-quality/QUEUE.md`)
- **Replication (layer 1):** the common estimator on all 34 eligible non-holdout goal periods (#2–#44; ≥ 200 statements with k ≥ 1 by ≥ 3 agents). Folders `G<NN>/`, role `replication`, templated predictions.
- **Period-native tests (layer 2):** **NE42** (#39 → #40 → #41 merge/split A-B-A at a fixed roster: the backlog jumps and falls), **NE41** (forced erasures reset the context load at scaffold-set times; 9 regime-III periods), **#51** (N sweep 21 → 32 at a fixed goal; the high-k tail; 34k statements). NE32 (three newcomers isolated for one day) was dropped: isolated rooms hold no agent messages to copy, so the channel is undefined on the low-backlog side.

## Model
**From:** `physics-models/08-copying-vs-transformation/` (primary), `physics-models/03-contagion/` (copying as transmission).
- **Channel (H57 variant).** A statement B by agent i is the output of a channel whose input is what i read since it last spoke, the read set R(B), with backlog k = |R(B)|. B either copies an item A ∈ R (reproduces it), transforms one (answers, extends or reacts: B depends on A but differs systematically), or ignores R. Kolchinsky & Corominas-Murtra split the information B carries about its source: I(X;Y) = I_copy + I_transform, with X and Y codes of source and output on one alphabet. I_copy = Σ_x p(x)·d(p(Y=x|X=x) ‖ p_Y(x)) for p(Y=x|X=x) > p_Y(x) (H07's reading), I_transform = I − I_copy.
- **Load-dependent copy probability.** P(B copies some A ∈ R | k) = π(k), with H57: π increasing in k (a speed–accuracy tradeoff; HH153: copying is cheap). Null: π constant. Rival (a): π depends on task phase and k co-varies with phase. Rival (b): apparent copying is shared-source overlap (templates, kickoff quoting) that grows with the number of items read. Rival (c), added after the real data: *contemporaneous convergence*, i.e. near-copies from simultaneous responses to the same moment, independent of reading. Attention dilution (H18: uptake ∝ k^−0.6) changes the amount of uptake, not the mode; the estimators are built to be flat in k under a constant π.
- **Alphabet.** At cluster level (k-means on whitened embeddings), copy information is topic coherence: 58% of synthetic transformations land in their source's cluster. H57 therefore codes copying at the message level: Y = X only when B is a near-copy of its source (Amendment 1b).

## Data scheme (`scheme/`)
- **Inputs:** `chat_core`, `context_ledger_turns` + `context_ledger_items`, raw chat embeddings `chat_{bge_small,gte_modernbert}.npy` (rows of `chat_index`), regime whiteners (32-d), H34 `markers/uses.parquet` (read-only), DQ5 `statement_flags`, DQ2 `reply_pairs` (`parent`, `n_pool`), `chat_mentions_clean`, `goals` + goal vectors (kickoff), `period_units`, `roster` (lab = family), `calendar` + `holdout_mask`.
- **Transform** (`scheme/h57core.py`, `scheme/build.py skeleton|outcomes`, per goal period, non-holdout days only):
  1. **Statements.** Each agent chat message B is matched to its talk call (nearest `t_first` within 3 s; chat rows precede the call's first record by ~40 ms).
  2. **Read set R(B)** (*Backlog (in-context read set)*): agent-authored ledger items received by i's calls after its previous talk call through B's call, same PT day, and in computer-use calls only after the last context reset. k = |R|; also `k_since_talk`, `k_ctx`, `ctx_pos`, reset positions.
  3. **Comparison sets.**
     - **Mutually invisible (in-flight) set I(B):** other agents' statements in B's room posted after B's call started whose own call started before B was posted. Neither could have read the other.
     - **Time-mirrored placebo F(B)**, descriptive only: the next k messages after B's call. It is contaminated by others copying B (Amendment 1).
     - **DQ2 parent**, descriptive.
     - **Addressed source:** the read item by an agent B names (`addr_n` = that author's read items; the channel uses `addr_n = 1`).
  4. **Per-statement outcomes:**
     - near-copy flags (raw cosine ≥ 0.95 bge / 0.938 gte, DQ5 thresholds) for R, F, I, parent and addressed source, with counts per lag bin;
     - marker near-copy (Jaccard ≥ 0.5, ≥ 3 markers), with and without common markers (≥ 2% of the period's messages or ≥ 3 agents on day 1);
     - k-means codes (K = 16/32/64) of B and its sources;
     - controls: log₂ length, `addressed`, `early` (the period's first active day), day position, unit, family; DQ5 `cross_echo` / `templated`; kickoff cosine.
- **Output:** `data/processed/H57-copy-under-backlog/` (29 MB): `skeleton/G<NN>_{S,P}.parquet`, `statements.parquet` (codes and numbers only), `results/` (per-period JSON, `pooled.json`, `summary.parquet`, `native_*.json`, `lag_diag.parquet`), `synthetic/` (runs, `summary.json`, `calibration.json`), `confirm_dryrun/`, `_provenance.json`.
- **Regimes covered:** 35 non-holdout goal periods, regimes I–III. The unit is the goal period, with step changes absorbed by agent × unit fixed effects. Periods are compared by their fitted slopes (random-effects pooling), never fitted jointly.

## Observables
*Original list written 2026-10-04 06:45 UTC; amended before real data (Amendments 1, 1b, 1c) and post hoc (Amendment 2).*
- **Primary (pre-registered as amended):**
  - **e_m:** chance-corrected read-set echo, echo(R) − [1 − (1 − q̂)^k], with q̂ from non-sibling in-flight pairs (m = bge, gte, both);
  - **mkn:** the same for marker near-copies;
  - **T:** copy-share trend on the near-coded addressed channel, s(top) − s(bottom) of within-period k terciles, s = I_copy / I (Miller–Madow), with an agent-stratified permutation test (500 draws);
  - pointwise copy and transformation information c, t (cross-fitted by day).
  - Each is a within-period slope on log₂(1 + k), with agent × unit FE, controls, CR1 SEs by agent-day and calibrated p (z/κ).
- **Crude:** DQ5 `cross_echo` slope (P7).
- **Post hoc (Amendment 2):** er (raw read-set echo; upper bound), elc (lag-matched count), lag profiles (near-copy rate per pair vs lag, read vs in-flight), the cluster-coded copy share (topic coherence).
- **Side (HH153):** within-agent length difference of echo vs non-echo statements.

## Null / baseline
- **Constant-π synthetic worlds** on the real read-out schedules of #20, #40 and #51 (unit 51c), with templates, kickoff quoting and (post hoc) contemporaneous convergence: the size and power of every estimator (`analysis/synth.py`, `synthetic/summary.json`).
- **Mutually invisible pairs** as the no-reading baseline; shuffle null for MI; agent-stratified permutation of k for T.
- **Rival (a):** day fixed effects, early × log k interaction, early/late subsets. **Rival (b):** drop `templated` (either model) and kickoff-echo statements and common markers. **Rival (c):** lag profiles and the lag-matched estimator.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** constant copy probability (π₀); phase-driven copying (rival a); shared-source overlap (rival b); contemporaneous convergence (rival c, post hoc); attention dilution without a mode change (H18).
**Locked holdout used for confirmation:** #51 tail (unit 51m, primary), #43 and #45 (secondary). `analysis/confirm.py` written and dry-run on stand-ins (#51 units 51h–51l, #44, #42); not run. Ledger check: all allowed; disclosure needed (the #51 tail and #43 have planned content uses by others; #45 was used by H02/H04 for activity timing, a different modality).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Read sets come from the validated context ledger, and every comparison set is defined from ledger times. Near-copy thresholds are DQ5's (not validated against human judgement). Family slopes in #51 are all small (−0.0003 to +0.0019). The 256-token truncation and alphabet dependence are listed. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Four assumptions were audited and rejected:<br>- lag-independent chance (Amendment 2);<br>- independent chance events across read items (convergence is statement-level);<br>- DQ2 `is_reply` as a neutral control (it is a collider: +0.013 to +0.016 bias in synthetic worlds);<br>- agent-day SEs (κ 1.14–1.21 from between-world variance). |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 0 | The load model does not beat the constant-π null: pre-registered slopes ≤ 0 in 31/35 periods; the upper bound is +0.0016 per doubling; T = 0. |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | P1–P4 failed. The signature (copy share rising with k) is absent; the copy share is ≈ 0 at every k. |
| E interventional | predicts the change across a natural experiment | 0 | NE42 moved the backlog (+0.59 log₂ units) without a dose-dependent copying change. NE41 erasures leave copying unchanged at fixed k. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | 196 synthetic runs on real schedules exposed seven estimator failures before or after the real run. The final pre-real estimators recover the planted effect at 80–95% (echo, marker) and T at 60–75%. Real data contained a structure (convergence) missing from the first synthetic world. The post hoc lag-matched estimator is validated only post hoc. Both embedding models agree. |
| G ground truth | agrees with known structure | 1 | Read pairs exceed unread pairs at 15–60 s lags (0.34–0.42% vs 0.12–0.16%; few unread hits) and in verbatim marker near-copies at < 15 s in most periods, so copying exists where expected. Shared-source (templated) periods #18 and #21 carry the largest raw slopes, as rival (b) predicts. |
| H comparative | beats the named rivals | 0 | Constant π is not beaten. Where a positive slope appears (#18), rival (b) explains it. Rival (c) explains the pre-registered negatives. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Fails in all 35 explored periods. Holdout not run. |

## Prediction
*Written 2026-10-04 06:45 UTC, before running the analysis on real data. Known at this point: statement counts and backlog distributions per period (median k 1–10; #51 has 40k statements and a k tail to q90 ≈ 43), nothing about any copy outcome.*

**Synthetic validation (axis F), run before real data.** Agents on the real read-out schedules of #40, #20 and #51 (unit 51c) write synthetic embedding and marker content with copy probability (i) rising with log k, (ii) constant, (iii) higher on the first active day of the unit (phase). Templates (3% of statements) and kickoff quoting (15% on day 1, decaying) are on. Pass criteria: under (ii), the β_echo, β_mk and T tests reject at ≤ 10% (α = 0.05, two-sided) over seeds; under (iii), ≤ 10% with the phase controls; under (i), β_echo and β_mk detect the planted trend (≥ 80% in the #51 skeleton) with the right sign. If a criterion fails, the estimator is amended (and the amendment dated) before the real-data run.

**Primary predictions (real data, non-holdout).**
- **P1 (semantic echo rises with backlog):** the random-effects mean of β_echo over eligible periods is > 0 with a 95% CI excluding 0, in *both* embedding models; ≥ 60% of eligible periods have β_echo > 0.
- **P2 (verbatim reuse rises with backlog):** random-effects mean β_mk > 0, 95% CI excluding 0.
- **P3 (the Kolchinsky ratio rises):** the copy share s = I_copy / I of the read-set channel rises from the bottom to the top k tercile beyond the placebo (T > 0); Stouffer-combined agent-stratified permutation p < 0.05 in both models (K = 32).
- **P4 (transformation falls or stays flat):** β_t ≤ 0 (pointwise transformation information, real minus placebo), while β_c > 0.
- **P5 (rival a):** the P1 pooled slope keeps ≥ 50% of its size with day fixed effects, and its sign within early and within late statements.
- **P6 (rival b):** the P1 and P2 pooled slopes keep ≥ 50% of their size after dropping templated and kickoff-echo statements and common markers.
- **P7 (crude flag):** DQ5 `cross_echo` (bge) rises with log k (pooled slope > 0).

**Native predictions** (details in the folders, written before running them):
- **NE42:** the excess echo and marker reuse rise from #39 to #40 (merged room, larger backlog) and fall again in #41 (DiD > 0), and across agents the change in copying tracks the change in log k (Spearman > 0).
- **NE41:** at fixed backlog k, statements in the first three receiving calls after a forced erasure (context load k_ctx near 0) show *less* excess echo than statements in the last three calls before it. A higher post-erasure echo would favour a reorientation reading (agents echo recent messages to catch up) over load.
- **#51:** across the 12 non-holdout units (N 21 → 32), the unit's mean excess echo rises with its median log k (Spearman > 0), and the within-agent slope in #51 is positive in both models.

**Verdict rule.** *Supported:* at least two of P1–P3 hold and P5 and P6 hold. *Failed:* P1–P3 all have pooled point estimates ≤ 0, or all have CIs including 0 with |β| below one third of the synthetic (i) effect. *Mixed:* otherwise. Per period (replication): *supported* if β_echo (both models) and β_mk are > 0 with at least one one-sided p < 0.05 and none significantly negative; *failed* if any primary slope is significantly negative or all are ≤ 0; *mixed* otherwise (most single periods are underpowered; this is said in each folder).

**Against H57:** flat or falling excess echo and verbatim reuse with k; a copy share that does not rise; or slopes that vanish under phase controls (rival a) or after removing templates and kickoff echoes (rival b).

### Amendment 1 (2026-10-04 ≈ 06:55 UTC, after a synthetic pilot, before any real-data outcome)
A pilot on the #40 and #20 schedules (6 seeds × constant / load worlds) failed the pre-registered pass criterion for two estimators:
- **The time-mirrored placebo F is contaminated by copying of B.** Messages after B read B and copy it, and the max over k of them rises with k. Under a *constant* copy probability its echo rate rises 0.017–0.019 per doubling of k, so echo(R) − echo(F) has a slope of −0.007 to −0.020 under the null. Under the load world it absorbs most of the planted effect (true slope 0.029–0.034; corrected slope 0.007–0.010).
- **The marker share has a built-in set-size slope:** the more items read, the more of B's vocabulary appears in them (+0.02–0.03 per doubling under the constant world).
- **A content-free source (newest read item) gives a Kolchinsky ratio dominated by topic co-occurrence**, with no power for the planted trend (copy share 0.60 → 0.56 bottom to top tercile under the load world). A most-similar source is blind to transformation by construction.

Amended estimators (replacing O1–O3b; the synthetic validation is rerun on them before real data):
- **Chance set:** the *mutually invisible (in-flight) set* I(B) = other agents' statements in B's room posted after B's call started, whose own call started before B was posted. Neither could have read the other. Per-pair chance near-copy rate q̂ per period and author (shrunk to the period rate with 100 pseudo-pairs).
- **O1′ excess echo:** e_B = echo(R) − [1 − (1 − q̂)^k], per model and both (pairwise agreement for "both").
- **O2′ excess verbatim near-copy:** m_B = mk_near(R) − [1 − (1 − q̂_mk)^k] (B's markers ≥ 3; marker Jaccard ≥ 0.5 with one read item), with and without common markers. The marker share stays descriptive only.
- **O3′ Kolchinsky ratio on the reply channel:** pairs (code(parent), code(B)) for statements with a DQ2 reply parent (an identified source, so both copying and transformation are visible). T = s(top) − s(bottom) with s = I_copy / I, tested by permuting k within agent × candidate-pool stratum (DQ2 ranks candidates partly by bge cosine, so the parent's similarity depends on the pool size; the pool is capped at 40 and saturated in most statements). Also the reply near-copy rate near(parent, B) against log k.
- **O3b′ pointwise copy and transformation information** on the same reply pairs (cross-fitted by day).
- **P1–P4 and the verdict rule are unchanged, applied to O1′–O3b′.** The mirrored-placebo outputs are kept as descriptive columns.

### Amendment 1b (2026-10-04 07:08 UTC, after the second synthetic pilot, before any real-data outcome)
Four further failures on synthetic worlds, each fixed before real data:
1. **Siblings inflate the in-flight chance rate.** Contemporaneous agents copy the same recent item, so in-flight near-copies are partly common-source copying. Counting them as chance over-corrects at high k (51c constant world: slope −0.018, p 1e-4 in one seed; −0.010 to −0.015 on average, 40–50% false rejections). Fix: in-flight near-copy pairs whose near-copy is explained by a shared near-copied read item are excluded from q̂ (`nnear_*_Ins`). The sibling-inclusive version is reported as `es_*`.
2. **DQ2 `is_reply` is a bad control.** Copies are labelled replies more easily, so conditioning on it biases the slope by +0.013 to +0.016 under the null. Fix: reply vs broadcast is now `addressed` (B names the author of an item it read; chat_mentions_clean). The DQ2-controlled spec is reported as a sensitivity.
3. **DQ2 parents are selected by cosine plus a "new item" bonus**, so the reply channel's near-copy rate rises with k under the null (+0.04 to +0.06 per doubling). Fix: the source channel uses the **addressed source** (the read item by the named author), restricted to statements where that author has exactly one read item (`addr_n = 1`, unambiguous; otherwise dilution biases the channel negative). DQ2 parents stay descriptive.
4. **At the cluster level, copy information is topic coherence.** 58% of synthetic *transformations* land in their source's cluster (K = 32), so the cluster-coded copy share has no power for the planted mode change. Fix: **message-level copy coding.** Y = X only if B is a near-copy of its source (model threshold); a same-cluster non-copy becomes a distinct "same topic, changed" symbol, which counts as transformation. In synthetic worlds this recovers the planted trend (copy share 0.01–0.02 → 0.05–0.07 bottom to top tercile under load; flat under constant).

P3's statistic is now T on the near-coded addressed channel. P4 is the pointwise c and t on the same pairs.

### Amendment 1c (2026-10-04 07:19 UTC, after the full synthetic validation, before any real-data outcome)
Over the constant-π worlds (52 seeds on three real schedules), the z-scores of the chance-corrected slopes have RMS κ = 1.21 (echo, either model), 1.14 (echo, both) and 1.16 (marker near-copy). The reason is between-world variance: each world's random structure gives it a slightly nonzero null slope, under any clustering choice. **Per-period p-values for these outcomes use z/κ** (`synthetic/calibration.json`). The cross-period random-effects pool absorbs the same variance as τ² and is reported both raw and κ-inflated. The near-coded T, pointwise c/t and addressed near-copy have κ ≈ 1.0 and are not adjusted.

### Amendment 2 (2026-10-04 ≈ 07:25–08:30 UTC, POST HOC: after the first real-data run)
The pre-registered (amended) estimators gave negative slopes in almost every period. Diagnosis on non-holdout data (`analysis/lag_diag.py`): **near-copies are driven by simultaneity.** Per pair, the near-copy rate falls steeply with the time lag for read and unread pairs alike. At lags < 15 s, mutually invisible (unread) pairs are near-copies as often as read pairs (pooled over 11 periods: 0.55% vs 0.44% per pair, both models). Agents posting at the same moment converge on near-identical text without reading each other. A chance rate taken from in-flight pairs (almost all < 15 s) and applied to every read item regardless of age over-corrects more as k grows, and treating chance near-copies as independent across items over-corrects further (convergence is a statement-level event). Reproduced in synthetic worlds with contemporaneous convergence (8% of messages adopt their room's 30-s "moment"): the pre-registered estimator gives −0.019 per doubling under the constant-π null (58–75% false rejections). Post hoc estimators, all labelled as such:
- **er (raw read-set echo, no chance correction):** unbiased in every synthetic world, with or without convergence. In real data it also counts chance near-copies that grow with k, so it is an **upper bound** on the slope of copying from what was read.
- **elc (lag-matched count excess):** near-copied read items minus Σ_b n_R,b·q̂_b over lag bins [0, 15), [15, 30), [30, 60), 60+ s, with q̂_b from non-sibling in-flight pairs (shrunk to the period rate). Linear, so valid when chance near-copies are correlated. In convergence worlds: null −0.003 / +0.001, load +0.029 / +0.034 (true ≈ 0.032). κ ≈ 1.6. On real data the long-lag bin is weakly identified (few in-flight pairs older than 60 s).
- **els (short-lag version, read items < 60 s only):** failed its synthetic check (null −0.011, no power). Reported, not used.

## Outcome vs prediction (round 1, non-holdout)
| Prediction | Observed | Verdict |
| --- | --- | --- |
| Synthetic validation (axis F) | Amended estimators: null rejections 5–20% raw (≈ 5% after κ), load detected 80–100% (T 60–75%). Seven estimator failures found and fixed or dropped (mirrored placebo, marker share, cluster-coded and content-free sources, DQ2-parent selection, `is_reply` collider, sibling-inflated chance), plus convergence post hoc | passed after amendment; incomplete (no convergence in the pre-real world) |
| P1 echo rises with k (both models, RE CI > 0, ≥ 60% periods > 0) | bge −0.0133 [−0.0151, −0.0115], 4/35 > 0, 31 sig. < 0; gte −0.0117 [−0.0135, −0.0099]. Biased by convergence | failed (artifact; uninformative about load) |
| P2 verbatim near-copy rises with k | −0.063 [−0.076, −0.051], 1/35 > 0 | failed (same artifact) |
| P3 Kolchinsky copy share rises (T > 0, Stouffer p < 0.05, both models) | T ≈ 0 in 31/33 periods (the near-coded copy share is ≈ 0 at every k); Stouffer p 1.0 (bge, gte). Cluster-coded share (topic coherence): median T −0.008, Stouffer p 0.74 / 0.98 | failed |
| P4 β_t ≤ 0 and β_c > 0 | β_c +0.00003 (bge), β_t −0.003 [−0.035, +0.029] | failed (no signal) |
| P5 rival a: survives day FE; sign within early / late | day FE −0.0129; early −0.0057, late −0.0114; early × log k −0.0001 (p 0.61) | n/a (no positive slope to protect); phase is not the driver |
| P6 rival b: survives filtering | filtered −0.0101 (bge); the #18 post hoc positive (+0.061) turns −0.020 when filtered | n/a; explains the one positive period |
| P7 DQ5 cross_echo rises | +0.0011 [+0.0005, +0.0017] (28/33 > 0) | tiny (a k-agnostic flag including chance growth) |
| Post hoc upper bound (raw read-set echo) | bge +0.0016 [+0.0009, +0.0022] (28/33 > 0, 10 sig. > 0, 0 sig. < 0); gte +0.0012 [+0.0006, +0.0018]. ≈ 5% of the synthetic plant (+0.03) | H57 effect ≤ 0.2 points per doubling |
| Post hoc lag-matched count | bge −0.0082 [−0.0098, −0.0066]; gte −0.0056; both −0.0044 | no rise (long-lag chance weakly identified) |
| NE42 | backlog up (Δ log₂ +0.59, p 0.003); echo DiD bge −0.004, gte +0.011, marker +0.025; dose ρ −0.36 / −0.01 / −0.15; merged effect grows when log k is controlled | failed |
| NE41 | after-forced-erasure coefficient +0.0002 (bge, p 0.19); k_ctx slope −0.0005 / −0.0007 | failed (null) |
| #51 | pre-registered slopes negative; raw echo +0.0007 per doubling; N sweep ρ 0.19 (bge), 0.41 (gte, p 0.09); T ≈ 0 | failed |
| HH153 side: echoes are shorter (cheaper) | within-agent log-length difference 0.000 | not supported |

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G02](goalperiod-subhypotheses/G02/README.md) | replication | failed | n 426, k̃ 2; β_echo -0.0038; raw upper bound -0.0005; lag-matched -0.0068; T 0 |
| [G03](goalperiod-subhypotheses/G03/README.md) | replication | failed | n 1194, k̃ 2; β_echo -0.0046; raw upper bound +0.0012; lag-matched -0.0045; T 0 |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | failed | n 5930, k̃ 2; β_echo -0.0055; raw upper bound +0.0012; lag-matched -0.0014; T 0 |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | failed | n 864, k̃ 2; β_echo -0.0081; raw upper bound +0.0014; lag-matched -0.0070; T 0 |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | failed | n 1696, k̃ 2; β_echo -0.0011; raw upper bound +0.0000; lag-matched -0.0030; T 0 |
| [G07](goalperiod-subhypotheses/G07/README.md) | replication | failed | n 256, k̃ 2; β_echo -0.0087; raw upper bound +0.0000; lag-matched -0.0125; T 0 |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | failed | n 2095, k̃ 2; β_echo -0.0018; raw upper bound -0.0005; lag-matched -0.0036; T 0 |
| [G10](goalperiod-subhypotheses/G10/README.md) | replication | failed | n 956, k̃ 3; β_echo -0.0092; raw upper bound +0.0028; lag-matched -0.0047; T 0 |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | failed | n 2146, k̃ 3; β_echo -0.0664; raw upper bound -0.0017; lag-matched -0.0081; T 0 |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication | failed | n 3317, k̃ 3; β_echo -0.0175; raw upper bound +0.0067; lag-matched +0.0039; T 0 |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | failed | n 3741, k̃ 2; β_echo +0.0006; raw upper bound +0.0007; lag-matched +0.0009; T 0 |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | failed | n 1675, k̃ 3; β_echo -0.0203; raw upper bound +0.0071; lag-matched +0.0043; T 0 |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | failed | n 1832, k̃ 2; β_echo -0.0327; raw upper bound +0.0057; lag-matched -0.0015; T 0 |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | failed | n 6681, k̃ 3; β_echo -0.0873; raw upper bound +0.0283; lag-matched +0.0607; T 0 |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | failed | n 5151, k̃ 3; β_echo -0.0441; raw upper bound +0.0127; lag-matched +0.0041; T 0 |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | failed | n 4356, k̃ 4; β_echo -0.0297; raw upper bound +0.0030; lag-matched -0.0241; T 0 |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | failed | n 2356, k̃ 3; β_echo -0.0995; raw upper bound +0.0122; lag-matched -0.1336; T 0 |
| [G23](goalperiod-subhypotheses/G23/README.md) | replication | failed | n 1672, k̃ 5; β_echo +0.0048; raw upper bound +0.0061; lag-matched +0.0043; T 0 |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | failed | n 1501, k̃ 5; β_echo +0.0002; raw upper bound +0.0021; lag-matched -0.0012; T 0 |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | failed | n 2446, k̃ 4; β_echo -0.0479; raw upper bound +0.0062; lag-matched -0.0356; T 0 |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | failed | n 2051, k̃ 4; β_echo -0.0419; raw upper bound +0.0077; lag-matched -0.0452; T 0 |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | failed | n 3555, k̃ 5; β_echo -0.0094; raw upper bound +0.0018; lag-matched -0.0095; T 0 |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | failed | n 2289, k̃ 5; β_echo -0.0136; raw upper bound +0.0025; lag-matched -0.0153; T 0 |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | failed | n 2697, k̃ 6; β_echo -0.0045; raw upper bound +0.0013; lag-matched -0.0045; T 0 |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | failed | n 1671, k̃ 6; β_echo -0.0173; raw upper bound +0.0025; lag-matched -0.0122; T 0 |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | failed | n 1768, k̃ 4; β_echo -0.0136; raw upper bound +0.0029; lag-matched -0.0135; T 0 |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | failed | n 1169, k̃ 3; β_echo +0.0002; raw upper bound +0.0043; lag-matched -0.0009; T 0 |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | failed | n 513, k̃ 2; β_echo -0.0160; raw upper bound +0.0007; lag-matched -0.0184; T 0 |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | failed | n 3146, k̃ 2; β_echo -0.0510; raw upper bound +0.0052; lag-matched -0.0276; T 0 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | failed | n 684, k̃ 3; β_echo -0.0109; raw upper bound -0.0001; lag-matched -0.0105; T 0 |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | failed | n 1575, k̃ 5; β_echo -0.0102; raw upper bound +0.0015; lag-matched -0.0043; T 0 |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | failed | n 1800, k̃ 4; β_echo -0.0103; raw upper bound +0.0023; lag-matched -0.0483; T 0 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | failed | n 940, k̃ 3; β_echo -0.0036; raw upper bound +0.0008; lag-matched -0.0032; T 0 |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | failed | n 1328, k̃ 3; β_echo -0.0023; raw upper bound -0.0003; lag-matched -0.0011; T 0 |
| [G51](goalperiod-subhypotheses/G51/README.md) | native | failed | n 33745, k̃ 5; β_echo -0.0023; raw upper bound +0.0007; lag-matched -0.0055; T 0 |
| [NE42](goalperiod-subhypotheses/NE42/README.md) | native | failed | Δ log₂k +0.59 (p 0.003); echo DiD bge −0.004 / gte +0.011; dose ρ ≤ 0 |
| [NE41](goalperiod-subhypotheses/NE41/README.md) | native | failed | after-erasure +0.0002 (bge, p 0.19); k_ctx slope −0.0005 |

The overview counts 34 replication folders as one estimator applied 34 times; the three native tests are the independent designs.

## Results
*Exploratory round 1, non-holdout, 2026-10-04. Code: `scheme/build.py`, `analysis/run_period.py`, `analysis/native.py`, `analysis/lag_diag.py`, `analysis/synth.py`, `analysis/synth_summary.py`, `analysis/figures.py`. Figures: `figures/summary_obs.pdf` (lag profile; per-period slopes), `figures/summary_obs2.pdf` (synthetic validation), `figures/phase_diagram_er_slope.pdf`.*

1. **Agents do not echo more under load.** The most generous estimate (raw read-set echo, which also counts chance near-copies) rises by 0.16 percentage points per doubling of the backlog, pooled over 33 periods; it is +0.07 in #51, which carries most of the data. The synthetic H57 world plants +3 points. The phase-diagram points (`figures/phase_diagram_er_slope.pdf`) show no trend with the period's median backlog or regime. The largest raw slopes (#18, #19, #21; regime I, template-heavy periods) disappear when templated and kickoff-echo statements are removed.
2. **Most semantic near-duplication is contemporaneous convergence, not copying.** Near-copy rates fall steeply with lag for read and unread pairs alike. Below 15 s, unread (mutually invisible) pairs are near-copies as often as read ones (0.55% vs 0.44% per pair). Only at 15–60 s do read pairs exceed unread ones (≈ 2.5×, with few unread hits). Marker (verbatim token) near-copies are more frequent for read pairs at short lags in most periods. Verbatim reuse of read content (links, names, numbers) is the real copying channel, and it is small.
3. **Addressed transmission is transformation.** When an agent names the author of a message it read, its statement is a near-copy of that message in only 0.1–2% of cases. The message-level copy share of the channel is ≈ 0 at every backlog. At cluster level the "copy share" is large but measures topic coherence, and it does not rise with k either.
4. **Load proxies don't matter.**
   - Context load (k_ctx) has no positive slope at fixed backlog.
   - Forced erasures leave copying unchanged.
   - The NE42 merge raised every agent's backlog (k ≈ 3.0 → 5.8 → 4.1) without a dose-dependent change in copying.
5. **What failed in the method, and why it matters beyond H57.** The pre-registered chance correction assumed lag-independent, independent chance near-copies. The data violate both: convergence is simultaneous and statement-level. This also bears on DQ5's `cross_echo` (any room, 2-h window) and on H12's and H07's readings: near-duplicates are not evidence of copying unless compared with unread messages at the same lag.

### Caveats
- **Threshold and representation.** Near-copy flags use DQ5's thresholds on two contrastive encoders with 256-token truncation; restatement below the threshold counts as transformation, not copying. The marker channel uses H34's hashed markers.
- **The pre-registered estimator is invalid on these data**, so the verdict rests on the post hoc upper bound and the lag profiles. The lag-matched estimator's long-lag chance rate rests on few in-flight pairs older than 60 s, and its negative slopes are not interpreted.
- **Visibility.** The read set is the backlog since the last talk call. Older in-context items can also be copied (they count toward k_ctx, which shows nothing either). About 10% of items may sit one call off (ledger validation).
- **Multiplicity and power.** 35 replication periods with one estimator; the 34 folders are not independent tests. Per-period power is low outside #51 and the large regime-I periods.
- **Causality.** Backlog is observational; NE42 is goal-confounded; NE41 changes context, not backlog.
- **Synthetic worlds** are stylised: copying from read sets only, fixed rotation transforms, convergence as 30-s moments.

## Notes
- 2026-10-04 06:45 UTC: card written before any real-data outcome.
- 2026-10-04 ≈ 06:55–07:19 UTC: Amendments 1, 1b, 1c after synthetic pilots, before real data. Period-folder predictions written 07:09 UTC.
- 2026-10-04 ≈ 07:25 UTC: first real-data run; Amendment 2 (post hoc) after diagnosing contemporaneous convergence; convergence worlds added to the synthetic validation.
- `infra/shared/simulate.py` was checked: its content model works per 30-min window without per-message read sets, so H57 uses its own per-message generator on the real ledger schedule (`analysis/synth.py`), reusing the simulator's anisotropic noise shape (`aniso_shape`).
- Read-only imports: `infra/shared/{common,copy_info,embed_models,holdout_ledger,simulate}.py`; H34's `scheme/markers.py` (imported only by `scheme/h57core.holdout_markers`, i.e. by `confirm.py` under its guard).

## Round 2 redirects (2026-10-04)
- **Where round 1 went sideways:** The estimator assumed chance near-copies are lag-independent and independent across read items. Real near-duplication is simultaneous convergence, and it swamped the copy signal.
- **What the direction is really after:** Does a swarm's verbatim reuse of read content (links, names, numbers, claims) depend on load, once simultaneous convergence is separated from copying by comparing read and unread messages at matched lag?
- **H57-R1.** Verbatim reuse of read markers (artifacts, numbers, names) exceeds the unread baseline at matched lag, and the excess per read item is independent of backlog.
- **H57-R2.** Contemporaneous convergence (unread near-copies within 15 s) is a swarm-level order parameter: it is highest in template-heavy regime-I weeks and predicts H12's dimensional collapse better than echo does.
- **H57-R3.** A lag-resolved chance model (continuous q(lag) fitted on mutually invisible and cross-room pairs) replaces DQ5's 2-h cross_echo flag as the shared copying instrument.

## Round 2 (2026-10-05): read-marker reuse vs backlog, a lag-resolved chance model, convergence as an order parameter
*Items H57-R1, R3 and R2. Predictions, nulls and kill rules written 2026-10-05 04:47 UTC, before any round-2 statistic on real data. Reserved data are masked with `holdout_mask` and `calendar.holdout` in every script (the round-1 skeleton already excludes them). Round-1 code and outputs are unchanged. Round-2 code is in new files (`scheme/build_r2.py`, `analysis/r2_*.py`); outputs go to `data/processed/H57-copy-under-backlog/r2/`.*

**Seen before writing:** everything on this card; the round-2 sections of H41, H34, H08 and H54; H12's card and its per-day PRday tables (`r1b/dq5/prday_*.parquet`, values already published in H12); the number of rooms per non-reserved period (multi-room: #35–#42, #44, #51; every regime-I period has one room); H34's marker table schema (classes U artifact, D number, N name, W rare word). No round-2 pair, rate or contrast had been computed.

### Common design
- **Statements B:** the round-1 skeleton (`skeleton/G<NN>_S.parquet`): agent chat messages matched to their talk call, Claude Code excluded as author, 35 non-reserved periods.
- **Pairs (B, A):** A is another agent's chat message on the same PT day with 0 < t_B − t_A ≤ 2 h, any room, non-reserved. Classes, from the context ledger:
  - *read:* B's author received A at a call no later than B's talk call, with no computer-use context reset in between;
  - *in flight:* same room, posted at or after B's call start (t_A ≥ t_call(B)), so B could not read it;
  - *unread, same room:* same room, posted before t_call(B), never received by B's author (absent, joined later, or omitted);
  - *cross-room:* another room, never received by B's author;
  - *read, erased* (a reset between receipt and B's call): excluded.
- **Outcomes per pair:**
  - *rare-marker reuse* by class c ∈ {U artifacts, D numbers, N names}: B and A share at least one class-c marker that is not common in the period (round-1 rule: ≥ 2% of the period's agent messages, or ≥ 3 agents on its first day). It is defined on pairs where both messages hold ≥ 1 rare class-c marker. *Any-class* = U ∪ D ∪ N.
  - *embedding near-copy:* raw cosine ≥ 0.95 (bge), ≥ 0.938 (gte), and both.
- **Strata (all contrasts):**
  - period;
  - lag bin [0, 15), [15, 30), [30, 60), [60, 120), [120, 300) s;
  - before-message age (time since B's author's previous chat message that day): < 60 s, 60–300 s, 300–1800 s, ≥ 1800 s or none (H54 r2);
  - received-message density (other agents' same-room messages in the 300 s before B): 0–1, 2–3, 4–7, 8+ (H08 r2);
  - marker-count bins of B and of A for the rare class-c markers: 1, 2–3, 4+. For the embedding outcomes, within-period length terciles of B and A are used instead.

  The marker-count and length strata are the call-length guard (H41 r2): at a matched lag, in-flight pairs come from long calls and read pairs from short ones, and long calls write long messages.
- **Pooling and errors:** pooled numbers are Mantel–Haenszel (MH) combinations over these strata, with period always a stratum (exception (d) in `CLAUDE.md`: per-period ratios on ≤ 5 events mislead). They are reported next to per-regime and per-period values. CIs: 95% percentile bootstrap over 1-h blocks of t_B within PT days (Poisson multiplier weights), 200 draws (100 in synthetic runs).

### R1. Verbatim reuse of read markers vs backlog
**Estimators.**
- **D_MH:** the MH risk difference of rare-marker reuse, read − in flight, with weights w = n_r·n_u / (n_r + n_u). **RR_MH:** the MH risk ratio.
- **Excess per read item by backlog:** D_j in the k bins {1}, {2–3}, {4–7}, {8–15}, {16+} (k = |R(B)|, round-1 definition), each with the same strata. The read and in-flight pairs of one bin share k.
  - Fit D_j = θ·(k̄_j / 4)^b by weighted least squares (weights 1/var_j from the bootstrap; k̄_j = mean k of the bin's read pairs). This gives **b, the backlog exponent of the per-item excess.** The bootstrap refits b in each draw.
  - Reference values: b = 0 means a constant per-item excess (H57-R1 as written). b ≈ −0.45 is H18's per-sender dilution transferred to copying. b = −1 means a constant per-statement copy probability. b > 0 means copying under load (the original H57).
- *Scope:* the excess is identified only at lags < 300 s, where in-flight pairs exist. These are the newest items of the read set. Older items need R3's model (secondary).

**Synthetic validation first** (real skeletons and real pair tables of #20 (regime I), #38 (regime III, two rooms) and #51 unit 51c; synthetic markers with classes in the real proportions and synthetic two-model embeddings; 4 seeds per world and skeleton):
- *Z0:* topic field only (room topics drift in 10-min bins). No copying, no convergence.
- *Zc:* pure convergence. With probability p_conv = 0.05, a message adopts its room's current 30-s "moment" (markers and vector). A village-wide moment, shared across rooms, has one third of that probability. No copying.
- *ZL:* call-length world. A message's marker count and its topic adherence rise with its call latency (talk depends on call length). No copying, no convergence.
- *Zk(b):* per-item copying. Each read item a is copied with probability θ·(k/4)^b·exp(−lag_a / 600 s), keeping 80% of its markers, at most one copy per statement. b ∈ {−1, −0.45, 0, +0.35}, with Zc convergence and the ZL length effect on. θ is set so that the any-class read/in-flight risk ratio is about 2 at lags < 300 s.
- *Pass:*
  - D_MH lower CI > 0 in ≤ 10% of Z0, Zc and ZL runs (size), and in ≥ 80% of Zk(0) runs (power);
  - b's CI excludes 0 in ≤ 10% of Zk(0) runs;
  - b upper CI < 0 in ≥ 80% of Zk(−0.45) runs, and b lower CI > 0 in ≥ 80% of Zk(+0.35) runs;
  - median b̂ within ±0.2 of the truth in every Zk world.

**Predictions.**
- **P-R1a (excess exists):** pooled D_MH > 0 with lower CI > 0 for names (N), for numbers (D) and for any-class, and RR_MH > 1. Prior 0.8 (H41 r2: regime-III read-out jumps J_mh,D 3.2, J_mh,N 4.8).
- **P-R1b (the copy channel is verbatim, not semantic):** RR_MH for any-class markers exceeds RR_MH for bge and for gte near-copies. The embedding RR_MH CI includes 1 or lies below it, because embedding near-copies at a matched lag are convergence-dominated (round 1; H34 r2). Prior 0.55.
- **P-R1c (backlog exponent):** b < 0 with upper CI < 0, and point estimate in [−0.9, −0.1] (dilution). Prior 0.5.
- **P-R1d (regimes):** D_MH (any-class) lower CI > 0 in each regime with ≥ 1,000 read pairs. Prior 0.6.

**Kill rules.**
- (i) Size > 0.10 in Z0, Zc or ZL: D_MH is not interpretable, and P-R1a and P-R1d are not scored.
- (ii) D_MH CI includes 0 or lies below it, with Zk(0) power ≥ 0.8: "verbatim reuse of read markers does not exceed the unread baseline at matched lag and before-message age".
- (iii) Backlog exponent b:
  - CI includes 0 with Zk(−0.45) power ≥ 0.8: "the per-item excess does not depend on backlog" (H57-R1 as written stands);
  - upper CI < 0: dilution (H57-R1 as written fails; H18 transfers to copying);
  - lower CI > 0: copying under load (the original H57 revives, for verbatim reuse);
  - power < 0.8: inconclusive.

### R3. A lag-resolved chance model q(lag)
**Model.** It is fitted on unread pairs only (in flight ∪ unread same room ∪ cross-room), separately for the embedding near-copy (per model) and any-class marker reuse:

logit q = s(ln lag) + δ·same_room + α_period + γ_B·ln n_B + γ_A·ln n_A,

where s is a natural cubic spline with knots at ln(10, 30, 120, 600, 3600 s), and n is the message length (embeddings) or the rare-marker count (markers).
- Multi-room periods (#35–#42, #44, #51): one fit per regime (II, III), using all lags up to 2 h.
- Single-room periods (all of regime I, and regime II before #35): s is fitted on in-flight pairs only. q is not identified beyond the longest in-flight lag there; this is stated, not extrapolated.

**Uses.**
- *Model excess* of a statement: (number of read items it near-copies) − Σ q(lag_a) over its read items within 2 h. This is linear, so it stays valid when chance near-copies are correlated (round-1 lesson).
- *Candidate shared flag:* `echo_excess` replaces DQ5's `cross_echo` (any room, 2-h window, no reading).

**Validation.**
- *V1, lag invariance of the room offset:* in multi-room periods, δ is fitted separately for lags < 60 s and 60–900 s. Pass if |δ_short − δ_long| < 0.5 log-odds and the interaction CI includes 0. If V1 fails, same-room chance at long lags is not identified.
- *V2, calibration, cross-fitted by day:* fit on the other days and predict the held-back day's unread pairs. Pass if observed/predicted lies in [0.75, 1.33] in ≥ 8 of 10 lag deciles and the calibration slope lies in [0.8, 1.25], in ≥ 2/3 of eligible periods (≥ 30 unread near-copy events).
- *V3, synthetic:* in Zc and ZL the model excess over read pairs has lower CI > 0 in ≤ 10% of runs. In Zk(0) the estimated excess count lies within 0.8–1.2× the planted copies in ≥ 80% of runs (multi-room skeleton #38 for long lags).
- *V4, replacement audit (real):* among statements that DQ5-style `cross_echo` flags (bge, any room, 2 h; recomputed on these pairs), the share whose near partners are all unread, and the share Σ q predicts.

**Predictions.**
- **P-R3a (shape):** unread near-copy rate falls with lag: q(10 s)/q(1 h) ≥ 5 (bge, regimes II–III), and q(10 s)/q(120 s) ≥ 2 in single-room periods. Prior 0.75.
- **P-R3b:** V1 passes. Prior 0.4.
- **P-R3c:** V2 passes. Prior 0.6.
- **P-R3d:** in multi-room periods, ≥ 50% of DQ5 `cross_echo` (bge) flags have no read near partner. Prior 0.5.

**Adoption rule and kill rule.**
- q(lag) is recommended as the shared copying instrument only if V1, V2 and V3 pass.
- Otherwise the recommendation is the R1 design (read vs in flight at matched lag and before-message age), plus a "read partner" restriction of `cross_echo`.
- V3 size > 0.10: R3 is not validated.

### R2. Contemporaneous convergence as an order parameter
**Observables.**
- **C15:** per-pair near-copy rate (bge primary; gte and both reported) among same-room in-flight pairs at lag < 15 s. Pairs whose near-copy is explained by a read item that both messages near-copy (siblings, round-1 rule) are excluded.
  - *Period value:* the pooled rate with its block-bootstrap CI, for periods with ≥ 300 such pairs.
  - *Day value:* the beta-binomial empirical-Bayes rate, shrunk to the regime mean (method of moments).
- **E (echo):** the share of statements that near-copy a read item within 2 h (round-1 `er`, bge). The crude comparator is the DQ5 `cross_echo` share.
- **T (template share):** the DQ5 `templated_bge` share of statements per period.
- **Dimensional collapse:** H12's agent-balanced PRday (r1b `prday_bge`; `prday_gte` as a check). Low PRday = collapse.
- **Reference predictor:** the DQ5 `self_repeat_bge` share (H12 r1b: Spearman −0.75 with PRday on regime-III days).

**Predictions.**
- **P-R2a (where convergence lives):** two parts. Prior 0.45.
  - Across eligible periods, Spearman ρ(C15, T) > 0.4 in both models.
  - Regime-I template-heavy periods (regime I, T above the regime-I median) have higher C15 than the other eligible periods (one-sided Mann–Whitney p < 0.05).
- **P-R2b (C15 beats echo):** test by leave-one-period-out prediction of day-level PRday with the model PRday ~ regime + x, for x ∈ {C15_day, E_day, cross_echo_day, self_repeat_day}. The C15 model has a lower out-of-period mean squared error than the echo model. The paired period-bootstrap 95% CI of ΔMSE (echo − C15) excludes 0. Prior 0.3.
- **P-R2c (reference):** the self-repetition model beats both. Prior 0.8.

**Synthetic check.**
- In Zc at p_conv ∈ {0.02, 0.05, 0.10}, C15 rises monotonically with p_conv on every skeleton.
- In ZL, and in Zk(0) without convergence, C15 stays within 25% of its Z0 value (the sibling exclusion works).
- Otherwise C15 is not an order parameter, and P-R2a and P-R2b are not scored.

**Kill rules.**
- ΔMSE CI includes 0 or favours echo: "convergence does not predict dimensional collapse better than echo".
- The C15 model does no better than the regime-only model: "C15 carries no PRday information".

**Impostors (round 2).**
- *Scheduler field:* pairs are within a room-day, and the strata hold lag, before-message age and density.
- *Exogenous field:* common markers are dropped. A shared stimulus raises in-flight and read pairs alike, so the contrast removes it. T and C15 separate templates from convergence.
- *Shared priors:* the same agents appear on both sides. A cross-family check splits D_MH by same-lab vs cross-lab pairs (descriptive).
- *Convergence:* this is the object. Read vs in flight at matched lag and before-message age, siblings excluded.
