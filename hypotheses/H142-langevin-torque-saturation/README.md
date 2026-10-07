# H142: The content response to aligned reads saturates as a Langevin-function torque

**Status:** round 1 done (2026-10-07, exploration data only): **failed by the pre-set kill.** At fixed batch size and hot topic, the step toward a direction does not grow with the number of aligned reads (pooled ΔLL(Langevin − line) −9.0 [−17.2, −2.2] nats, bge; f̂(1) 0.000 [−0.002, 0.002] on #51); only the newest item pulls. Amendments A1–A4 (before scored data). Card, observables, nulls and predictions written 2026-10-07 11:45–12:30 UTC, before any H142 statistic on real data.
**Question (GOALS.md):** **Q1** (what couples agents: how does the read-out pull toward one direction grow with the number of reads that point that way in one call?). Second: **Q5** (how many aligned messages does an operator need to send in one batch to move an agent most of the way?).
**Fields:** stat mech (mean-field vector spins: the Langevin function as the n = 3 equation of state, saturation of the magnetization), information theory (read-out channel capacity)
**Literature:** none in `literature/` covers the Langevin function. Cited from memory (†): Langevin, *J. Phys. Theor. Appl.* 4, 678 (1905)† (paramagnetism of classical moments, L(x) = coth x − 1/x); Stanley, *Phys. Rev.* 176, 718 (1968)† (n-vector models). Model reference: [`physics-models/11-vector-spins/README.md`](../../physics-models/11-vector-spins/README.md) (mean-field section). Name clash: this is the static Langevin *function*, not the Langevin *dynamics* of [`physics-models/16-langevin-relaxation/`](../../physics-models/16-langevin-relaxation/README.md).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime; Agent state, **variant vector** (32-d whitened statement vectors, `style_resid32`); H18's *pending set (talk-call backlog, ledger k)* (RE-V1, shared `pending_sets.py`); **Exposure (turn read-out)** and **Interaction (ledger-visible exposure)** (RE-D1) with the **unread (in-flight) exposure placebo**; H67's **in-flight placebo (matched-lag)**; **Influence coupling (content pull)** (H29); **Interaction (addressed)** for named items. Used as defined in H113 (proposed there): *per-message uptake slope γ(k)*, *capacity exponent a_U*. **New named variants proposed for DEFINITIONS.md** (not edited there; defined under Observables): **content direction u (H142, period clusters)**, **aligned-read count n_u (H142)**, **directional step y_{c,u} (H142)**, **saturation scale n_sat (H142)**, **curvature contrast Δ_curv (H142)**.
**From:** HH385 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/11-vector-spins/` (primary: the Langevin function as the response of a classical moment to a field), `physics-models/04-semantic-information/` (secondary: H113's read-out channel as the linear rival)
**Data inputs (shared tables first):** `pending_sets/G<NN>/` (talks, pending; wakes, wake_pending for #51); `chat_core`; `embeddings/statements.parquet` + `chat_index.parquet`; `statements_{style_resid32,white32}_{bge_small,gte_modernbert}.npy`; `goal_vectors_<model>.npy` + `goals.parquet` (goal, kickoff, kickoff_room) whitened per regime; `producing_calls`; DQ1 `call_windows`, `context_ledger_items`; `chat_mentions_clean` (named items); `statement_flags`; `rooms_timeline`; `period_units`, `calendar`, `roster`. No text is read.

## Source HH (from the HH list; one word changed to follow the house style)
- **HH385 · The content response to aligned reads saturates: a Langevin-function torque, not a linear one.** A vector spin driven by a field of strength h aligns as L(h), the Langevin function, which saturates. If each aligned read adds to h, the content step toward a direction saturates with the number of aligned reads in one call.
  - *Prediction:* the content step toward direction u rises with the number of reads aligned with u and flattens by about 3 aligned reads. The curve fits L(c·n) better than a line, by [out-of-fold] likelihood.
  - *Check:* content embeddings per call; read sets per call (DQ1 ledger); the alignment of each read to u.
  - *Kill:* the step is linear in n up to the largest n observed, or a line fits as well on [out-of-fold] data.
  - *Impostors:* calls with many aligned reads come from hot topics (a field). Compare within-hour, across calls with different numbers of aligned reads.
  - *Models:* 11 · *Builds on:* H18, H48, H113, HH345

## Standards (STANDARDS.md)
**Question served:** Q1 (second: Q5).

| Impostor | Relevant? | How it is handled (planned) | Status |
| --- | --- | --- | --- |
| Scheduler field | n/a | Call-level design: rows are (call, direction) pairs; no time-binned synchrony statistic. | n/a |
| Exogenous field (kickoff, goal, operator) | yes (the HH's impostor: hot topics) | Goal, kickoff and room-kickoff directions and the out-of-batch window field are projected out (H113's P_c). Direction × room × hour fixed effects absorb a hot topic: the shape is identified from calls in the same hour and room with different aligned counts. Human and nudge items are excluded from the batch. | removed (planned) |
| Shared model priors (family, style) | yes | `style_resid32` vectors in both models; call fixed effects absorb the reader's state at that call. | removed (planned) |
| Contemporaneous convergence | yes | The in-flight aligned count n_F,u (messages aligned with u, posted during the call, unreadable) enters with its own curve. Only units where the read − in-flight contrast is positive are scored (H113 A1's rule). | removed (planned) |

**Inputs:** current tables only (ledger pending sets, DQ5 vectors in both models).

**Two layers:**
- *Replication* (role `replication`): the shape test (O1–O3) on every non-reserved period that passes H113's field identification and has ≥ 200 call-direction rows with n_u ≥ 4. H113's field-identified periods are #13, #36, #37, #38, #39 and #51 (bge) and #13, #16, #35, #36, #37, #38, #51 (gte); other testable periods are reported as descriptive. The n_u ≥ 4 count is a structural count, made before any outcome.
- *Natives* (role `native`): **G51** (timer-wake batches: k and the batch are set by others while the reader sleeps, H18's design D2), **NE42** (the 2026-05-04 room merge raised batch sizes about ×1.5 at fixed agents, H113 N3: the saturation scale should not move). Each has a dated prediction in its folder.

**Unit-of-analysis exception (named):** (a) **shared instrument**: the content directions u are k-means clusters fitted per period on other days' statements (a ruler, not a model). (d) periods with few n_u ≥ 4 rows enter only a random-effects pool of the shape parameters, reported next to per-period values.

## Question
When one call's batch holds n messages that point the same way u, does the agent's next statement move toward u in proportion to n (a linear channel, H113's form at fixed batch size), or does the step saturate within a few aligned reads, as a classical moment saturates in a growing field (the Langevin function)?

**Practical payoff:** if the response saturates by about 3 aligned reads, an operator gains nothing by sending a fourth message on the same point in one batch. If it is linear at fixed batch size, every extra aligned message adds the same pull.

## Model
**From:** `physics-models/11-vector-spins/` (mean-field equation of state).

**H142 variant: a Langevin torque per call.** For reader i at talk call c, each direction u (a content cluster centroid) has an aligned count n_{c,u}. The step of i's statement toward u is

  E[y_{c,u}] = α_c + δ_{u,room,hour} + f(n_{c,u}) + g(n^F_{c,u}) + β_new · newest_{c,u} + β_name · n^name_{c,u},

with the Langevin form f(n) = f_∞ L(c n), L(x) = coth x − 1/x. L rises as x/3 near 0 and saturates at 1, so the initial slope is f_∞ c / 3 and the **saturation scale** is n_sat = 3/c (where the initial-slope line reaches f_∞). HH385: n_sat ≈ 3 (c ≈ 1).

**Shape signatures at c = 1** (L(1) 0.313, L(2) 0.537, L(3) 0.672, L(6) 0.833): f(2)/f(1) = 1.72 and f(6)/f(3) = 1.24. A power law n^p gives the same ratio at both ends (2^p), and a line gives 2 at both. So the **curvature contrast** Δ_curv = ln[f(2)/f(1)] − ln[f(6+)/f(3)] is 0 for any power law or line and ≈ 0.33 for L at c = 1.

**Rivals (named):**
- **R-linear (H113's channel at fixed k):** y⊥ = γ(k) Σ x⊥_m. At fixed k (absorbed by α_c) the step toward u is linear in n_u. The HH's kill.
- **R-select (H113-R2):** the reader picks one item; at fixed k, P(the pick is aligned with u) = n_u/k, again linear in n_u.
- **R-power (scale-free concavity):** f = a n^p with p < 1 (a dilution-like curve from the first read). Δ_curv ≈ 0.
- **R-recency (H113 P7):** the newest item counts more (+0.034 [0.025, 0.043] bge). A "saturation" can come from whether the newest item is aligned. Handled by the newest_{c,u} indicator.
- **R-named (H29):** items that name the reader pull 3–6× more (#51: 0.03–0.09 vs 0.009–0.021 of the gap per message). Handled by the named count n^name_{c,u}.
- **R-field (the HH's impostor):** hot topics give many aligned reads and a common pull. Handled by direction × room × hour effects and the in-flight curve g.

## Data scheme (`scheme/`)
`scheme/build.py --period G<NN>` writes `data/processed/H142-langevin-torque-saturation/G<NN>/` from shared tables only (projected coordinates as float16, cluster labels; no text). Reserved days are absent from `pending_sets`; every other table passes the shared reserved-data mask (`infra/shared/common.py`). Budget ≤ 100 MB.
- **Talk calls and batches:** H113's unit rows: every scored talk call with a statement by the reader and a previous same-day statement; batch B_c = agent-kind pending items with a statement vector (ledger k); in-flight set F_c = others' messages in the reader's room posted after the call's `t_call` and before the statement. Built in H142's own code from `pending_sets` (H113's code is not imported).
- **Projection P_c:** removes the reader's previous statement, the period's goal, kickoff and room-kickoff directions, and the out-of-batch window field (H113's definition).
- **Content directions u (H142):** K = 8 k-means centroids (H113's discrete-check K) of projected statement vectors, fitted per period with day folds: the clusters used on day d are fitted on the other days. Variant K = 12. Each batch and in-flight message is assigned to its nearest centroid if its cosine to it is ≥ 0.3, else to none.
- **Rows:** one per (call c, direction u): y_{c,u} = (P_c y_c) · û_u; n_{c,u}, n^F_{c,u}, newest_{c,u} (the newest batch item is assigned to u), n^name_{c,u} (aligned items that name the reader, `chat_mentions_clean`), k_c, room, hour.
- **Output:** `G<NN>/rows_<model>.parquet`, `G<NN>/centroids_<model>.npz`, `counts.json` (structural: rows by n_u), `_provenance.json`; `results/`, `synthetic/`.
- **Regimes covered:** I, II, III (each period within one regime; regime whitener per period).

## Observables
*Specified 2026-10-07 11:45–12:30 UTC, before any H142 statistic.* Primary: `style_resid32` × bge_small; variant gte_modernbert.
- **O1 model-free step curve.** f̂(n) for n = 1, 2, 3, 4–5, 6+ as dummy coefficients in the fixed-effects model above (call effects α_c; direction × room × hour effects δ), with the in-flight dummies for n^F. Agent-day cluster bootstrap (300 draws).
- **O2 curvature contrast** Δ_curv = ln[f̂(2)/f̂(1)] − ln[f̂(6+)/f̂(3)] (bootstrap CI; defined when f̂(1) > 0 with CI).
- **O3 shape comparison.** Day-blocked out-of-fold log-likelihood (Gaussian) per row of four shapes for f: linear, power n^p, Langevin f_∞ L(c n), and the free dummies. ΔLL(Langevin − linear) and ΔLL(Langevin − power) per period, paired bootstrap over day folds. Fitted ĉ and n̂_sat.
- **O4 convergence check.** The in-flight curve ĝ(n) vs f̂(n): ĝ(1)/f̂(1) and the read − in-flight contrast at n = 1.
- **O5 range check (structural):** the largest n with ≥ 50 rows, per period.

**Estimates rows** (`per_period_estimates`, hypothesis H142): `h142_step_curve_n1`…`n6p`, `h142_curvature_contrast`, `h142_langevin_c`, `h142_nsat`, `h142_dll_langevin_linear`, `h142_dll_langevin_power`, `h142_inflight_ratio`, per period and model.

## Null / baseline
- **N0 linear at fixed k:** f(n) = a n (R-linear and R-select both give it).
- **N1 cross-day surrogate batches** (H113): each call's batch replaced by a batch of the same k from another day; gives the null of the whole curve.
- **N2 within-hour permutation of aligned counts** across calls of the same room and hour (keeps the field, breaks the link to the reader's step).
- **N3 synthetic worlds** (below).

## Synthetic validation plan (axis F; runs before any real-data statistic)
Worlds on the real skeletons of #13, #38 and #51 (every scored talk call with its real k, batch, in-flight set, cluster labels and rooms); synthetic statement vectors calibrated so |y⊥|² matches the data (no real y·x product is used). 100 replicates per world.
- **W-lin:** linear channel γ(k) Σ x⊥ with b = 0.75 (H113's range).
- **W-sel:** one item selected per call.
- **W-L1, W-L3:** Langevin torque with n_sat = 1 and 3.
- **W-pow:** f = a n^{0.3}.
- **W-field:** a hot-topic field (room × topic random walk, τ = 30 min) with no read uptake.
- **W-recent:** only the newest item counts.
- **Decision rules fixed now:** O3 must prefer the Langevin shape over linear in ≥ 80% of W-L3 replicates and in ≤ 10% of W-lin and W-sel replicates; Δ_curv's false "> 0" rate must be ≤ 0.10 in W-pow, W-lin and W-recent (with the newest indicator in the model); W-field must give f̂(n) CI including 0 at every n in ≥ 90% of replicates. Power is computed at the real per-period counts of n_u ≥ 4; a period with power < 0.8 against W-L3 vs W-lin reports a descriptive shape only.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R-linear (H113 at fixed k), R-select (H113-R2), R-power, R-recency, R-named, R-field.
**Reserved periods used for confirmation:** none (not run). Planned: talk calls of #43, #45–#47 and the #51 tail (talk calls and timer wakes), ledger family `readout_capacity` (shared with H113 and H140: disclose; H18 and H68 `dilution_addressing` plan the same targets). A frozen, guarded confirm script is written only after exploration and runs only with Vivian's sign-off.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Ledger rows, DQ5 vectors, fold centroids; both models agree; regime invariance not tested |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | A1: call FE do not fix the per-read slope; k-bin amplitudes fix it |
| C adequacy | beats the null hierarchy, day-blocked out-of-fold data | 0 | Langevin does not beat the line out of fold (bge pool −9.0 [−17.2, −2.2]) |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | Δ_curv undefined; n̂_sat on grid edges |
| E interventional | predicts the change across a natural experiment | 0 | NE42 descriptive; N1 fails |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 | n̂_sat recovered; sizes ≤ 0.03; power ≥ 0.87 on scored units; flat result survives K = 12, dedupe, raw projection, day cells |
| G ground truth | agrees with known structure | 0 | n/a |
| H comparative | beats the named rivals | 0 | beats neither line nor power law; the newest item (R-recency) is the only pull |
| I transfer | holds in other same-mode periods, including the reserved periods | 0 | reserved periods not run |

## Prediction
*Written 2026-10-07 11:45–12:30 UTC, before running the analysis on real data.*

**What I had seen when writing this:** H113's card (per-message uptake falls as k^−b with b ≈ 0.7 on #51 wakes and ≈ 0.8 pooled on talk calls; total uptake ∝ k^0.2–0.3; information per call rises from k = 1 to k ≈ 5–8 and then flattens or falls, e.g. #38 1.07 → 1.70 → 1.13 bits, #51 0.59 → 0.10 bits at k ≥ 17; newest item +0.034; γ_F/γ₁ median 0.31; a topic field alone gives b̂ ≈ 0.8, so only 6–7 of 34 periods are scored; NE42 |Δb̂| ≤ 0.09 while k rises ×1.5); H18 (dilution 0.66 ± 0.02 on ledger pending sets; saturating 1/(k₀ + k) with k₀ ≈ 2–8; #51 timer wakes 0.50 [0.45, 0.56]); H29 (named pull 0.03–0.09 vs unnamed 0.009–0.021 of the gap per message in #51); H48 (each read would move an agent by about 1/250 if read-out drove settling). **Not seen:** any aligned count, any cluster assignment of batch items, and any directional step.

**Synthetic (axis F).**

| # | Prediction | Counts against |
| --- | --- | --- |
| S1 | O3 separates W-L3 from W-lin and W-sel at the real #51 counts (power ≥ 0.8) | power < 0.8 |
| S2 | Δ_curv has false-positive rate ≤ 0.10 in W-pow, W-lin and W-recent | > 0.10 |
| S3 | Fewer than half of H113's identified periods have power ≥ 0.8 (few n_u ≥ 4 rows outside #51 and #38) | ≥ 1/2 powered |

**Replication layer.**

| # | Prediction [credence] | Counts against |
| --- | --- | --- |
| **P1** (primary, HH) | **Langevin beats a line.** Pooled ΔLL(Langevin − linear) > 0 with CI above 0, and > 0 in ≥ 2/3 of powered periods [0.35] | pooled CI includes 0 or below (**kill**, with power) |
| P2 | **Saturation, not scale-free concavity.** Pooled Δ_curv > 0 with CI above 0 [0.25] | Δ_curv CI includes 0 (R-power or R-linear) |
| P3 | **Flattens by about 3.** Pooled n̂_sat ∈ [1.5, 6] [0.3] | n̂_sat > 6 or not identified |
| P4 | **Not convergence.** ĝ(1)/f̂(1) ≤ 0.5 and the read − in-flight contrast at n = 1 > 0 (CI), pooled [0.65] | ĝ(1)/f̂(1) > 0.5 |

**Native layer** (each repeated in its folder).

| # | Unit | Prediction [credence] | Counts against |
| --- | --- | --- | --- |
| N1 | G51 | On timer-wake batches the same shape holds: ΔLL(Langevin − linear) > 0 (CI) and n̂_sat within ×1.5 of the talk-call value [0.3] | wake curve linear (CI) |
| N2 | NE42 | The saturation scale is a reader property: |ln n̂_sat(#40) − ln n̂_sat(#39)| < ln 1.5 while k rises about ×1.5 (H113 N3) [0.3] | the change ≥ ln 1.5 with CI excluding 0 |

**Kill rule (HH385).** The kill fires if the step is linear in n up to the largest n observed (f̂(6+)/f̂(3) CI contains 2 and Δ_curv CI contains 0) *or* the line fits as well out of fold (pooled ΔLL(Langevin − linear) CI includes 0 or lies below it), in each case only where the synthetic power against W-L3 is ≥ 0.8. Without that power the verdict is inconclusive.

**Hypothesis-level verdict rule.** *Supported* if P1 and P2 pass. *Narrowed* ("the step saturates, but the Langevin form is not singled out") if P1 passes and P2 fails while the power curve also beats the line. *Failed* if the kill fires. *Inconclusive* otherwise.

**My credence before data:** supported 0.2; narrowed 0.2; failed 0.3; inconclusive 0.3. H113's information curve flattens by k ≈ 5–8, which leans toward saturation; H113's linear channel fitted per k leans the other way.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication (scored, both models) | failed | ΔLL(L − line) −3.2 [−8.1, 0.3] bge, −1.3 [−3.1, 0.0] gte; f̂ flat |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication (scored gte only) | failed | gte +8.4 [3.9, 14.3] but no positive f̂ bin (kill clause a); bge −1.1 (unscored) |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication (unpowered) | descriptive | rising f̂ with in-flight as large (field signature) |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication (< 200 rows) | descriptive | f̂(1) 0.017 [0.005, 0.030] bge; no shape |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication (< 200 rows) | descriptive | f̂(1) 0.020 [0.000, 0.039] bge; no shape |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication (scored, both models) | failed | −5.1 [−12.1, 0.9] bge, −6.8 [−10.9, −2.9] gte; newest +0.019 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication (unpowered) | descriptive | n̂_sat on grid edge |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication + native N1 | failed | −0.7 [−2.0, 0.5] bge, +5.7 [−1.8, 11.7] gte; f̂(1) 0.000; wakes N1 fail |
| [NE42](goalperiod-subhypotheses/NE42/README.md) | native N2 | descriptive | n̂_sat unidentified on all sides |

The other 24 non-reserved periods were run as descriptive rows only (`results/periods.json`, estimates table).

## Results
See "Round 1 (2026-10-07)" below.

## Round 1 (2026-10-07)
*Round-1 agent, exploration data only. Reserved goal periods and windows are masked by construction (`pending_sets` drops them; every other table passes `holdout_mask`). Code: `scheme/build.py`, `scheme/h142scheme.py`, `analysis/h142lib.py`, `analysis/synthetic.py`, `analysis/run.py`, `analysis/write_estimates.py`, `analysis/figures.py`. Data: `data/processed/H142-langevin-torque-saturation/` (122 MB; #51 batch vectors are most of it).*

### Step 1: structural count (before any outcome, 2026-10-07 ~10:40 UTC)
`scheme/build.py --all` built the (call, direction) rows for 34 non-reserved periods in both models. Rows with n_u ≥ 4 (`counts.json`; no step was read):

| Period | H113-identified | rows n_u ≥ 4, bge / gte | largest n with ≥ 50 rows (O5), bge / gte | ≥ 200 rows |
| --- | --- | --- | --- | --- |
| #13 | bge, gte | 909 / 1051 | 9 / 8 | both |
| #16 | gte | 383 / 380 | 5 / 5 | both |
| #35 | gte | 387 / 405 | 5 / 6 | both |
| #36 | bge, gte | 153 / 159 | 4 / 4 | neither |
| #37 | bge, gte | 76 / 64 | 2 / 2 | neither |
| #38 | bge, gte | 552 / 578 | 6 / 6 | both |
| #39 | bge | 210 / 164 | 4 / 4 | bge only |
| #40 | none | 771 / 712 | 7 / 6 | both |
| #41 | none | 467 / 493 | 5 / 6 | both |
| #51 talk calls | bge, gte | 30,758 / 28,953 | 36 / 35 | both |
| #51 timer wakes | (native) | 2,193 / 2,035 | 11 / 11 | both |

About 67–71% of batch items reach cos ≥ 0.3 with a fold centroid. #36 and #37 fail the 200-row rule and are descriptive.

### Step 2: synthetic validation (axis F; before any real step statistic)
`analysis/synthetic.py` on the real skeletons of #13, #38 and #51 (bge; 100 runs per world; W-L3 at ×3 amplitude, 50 runs). Only y is synthetic: real calls, batches, in-flight sets, aligned counts, newest and named flags, rooms, hours, day-fold centroids and projected batch vectors. The real step is never read; only the period mean of |y⊥|² sets the noise. Every world except W0 has the same directional signal energy as W-lin with γ₁ = 0.15, b = 0.75 (H113's measured range); W-field has ×4 (strong) and W-field1 ×1. W-field is a hot-topic field with no reading: a two-sided exponential (τ = 30 min) rate of the room's own statements per direction, plus an independent room × topic OU walk.

**Finding that forced Amendment A1.** With the card's form (call effects and one amplitude for f), the linear channel W-lin is called "Langevin beats the line" in 70% (#13), 61% (#38) and 100% (#51) of runs, and W-sel in 80%, 40% and 100%. The call effect α_c fixes the level, not the slope. The slope γ(k) falls with k, and n_u rises with k (corr 0.82 on #51), so a linear channel gives a concave pooled curve.

Decision rates under the amended design (A1 with A4's bin merging; rerun 2026-10-07 after A4, same seeds):

| World | Langevin beats line (ΔLL CI > 0), #13 / #38 / #51 | Δ_curv CI > 0 | all f̂ CIs include 0 | read − in-flight CI > 0 at n = 1 | n̂_sat median [IQR] (#51) |
| --- | --- | --- | --- | --- | --- |
| W0 no coupling | 0.02 / 0.01 / 0.00 | 0.00 / 0.00 / 0.00 | 0.78 / 0.80 / 0.77 | 0.05 / 0.05 / 0.04 | — |
| W-lin | 0.00 / 0.00 / 0.02 | 0.00 / 0.01 / 0.00 | 0 | 1.00 / 0.60 / 1.00 | 150 (grid edge) |
| W-sel | 0.01 / 0.00 / 0.00 | 0.01 / 0.00 / 0.00 | 0 | 0.93 / 0.29 / 1.00 | 50 |
| W-recent | 0.02 / 0.00 / 0.00 | 0.01 / 0.00 / 0.00 | 0.53 / 0.67 / 0.78 | 0.02 / 0.00 / 0.00 | — |
| W-pow (p = 0.3) | 1.00 / 0.98 / 1.00 | 0.01 / 0.00 / 0.00 | 0 | 1.00 | 1.46 [1.29, 1.46] |
| W-field1 (×1) | 0.03 / 0.02 / 0.00 | 0.00 / 0.00 / 0.00 | 0.74 / 0.68 / 0.57 | 0.03 / 0.04 / 0.03 | — |
| W-field (×4) | 0.01 / 0.02 / 0.01 | 0.01 / 0.00 / 0.00 | 0.58 / 0.73 / 0.18 | 0.00 / 0.02 / 0.00 | — |
| W-L1 (n_sat 1) | 1.00 / 1.00 / 1.00 | 0.35 / 0.15 / 0.99 | 0 | 1.00 | 0.90 [0.90, 1.01] |
| W-L3 (n_sat 3) | 1.00 / 0.99 / 1.00 | 0.82 / 0.54 / 1.00 | 0 | 1.00 | 3.04 [2.69, 3.04] |
| W-L3 ×3 | 1.00 / 1.00 / 1.00 | 1.00 / 1.00 / 1.00 | 0 | 1.00 | 3.04 |

Langevin beats the power law (ΔLL(L − pow) CI > 0) in W-L3 in 0.63 / 0.43 / 1.00 of runs and in W-pow in 0.00 / 0.00 / 0.00. n̂_sat is recovered within the grid step (bias ≤ 0.1 at n_sat 1 and 3). The agent-day cluster bootstrap of f̂ is calibrated: in W0, 77–80% of runs have all five CIs covering 0, against 0.95⁵ = 0.774 at nominal coverage. A day-cluster bootstrap covers less (58–71%), so the card's agent-day clusters stay.

**Power at each period's real counts** (W-L3 pass rate on the period's own skeleton, 100 runs, after A4; `summary_power.json`; bge / gte): #13 1.00 / 1.00; #16 0.91 / 0.87; #35 0.67 / 0.61; #36 0.40 / 0.40; #37 0.40 / 0.24; #38 0.99 / 0.93; #39 0.47 / 0.64; #40 0.62 / 0.70; #41 0.63 / 0.68; #51 talk 1.00 / 1.00; #51 wakes 0.99 / 1.00. W-lin size on these skeletons (bge) is 0.00–0.16 (#16: 0.12, #37: 0.16; both above 0.10). At ×3 amplitude every skeleton reaches ≥ 0.92. Before A4 the small skeletons had lower power (e.g. #35 0.30, #41 0.35), because sparse bins broke folds.

**Scored units (identified by H113, ≥ 200 rows, power ≥ 0.8), fixed before any outcome:** bge #13, #38, #51; gte #13, #16, #38, #51; natives: #51 wakes (both models). Every other period, including all three NE42 sides, is descriptive.

| # | Prediction | Result | Verdict |
| --- | --- | --- | --- |
| S1 | O3 separates W-L3 from W-lin and W-sel at #51 (power ≥ 0.8) | power 1.00; size 0.02 (W-lin), 0.00 (W-sel), after A1/A4. Card form: size 1.00 | supported (after A1); failed as written |
| S2 | Δ_curv false "> 0" ≤ 0.10 in W-pow, W-lin, W-recent | ≤ 0.01 on all three skeletons | supported |
| S3 | fewer than half of H113's identified periods powered | bge 3/6, gte 4/7 (not fewer than half) | failed |

**Amendment A1 (2026-10-07 ~11:15 UTC, after the synthetic check, before any real step statistic; not post hoc).** The card's design cannot separate the Langevin form from H113's linear channel: the call effect holds the level fixed, not the per-read slope γ(k). Change: each shape's amplitude is free per batch-size bin (26 log-spaced k bins, edge ratio ≤ 1.25 above k = 8): f(n; k) = a_b · h(n), with h linear, n^p or L(c n) and c, p shared. O3, P1, P3 and the kill use this form. The card's one-amplitude form is reported as the variant "pooled amplitude". O1, O2 and O4 keep the card's dummies (pooled over k): their false rates in W-lin, W-pow and W-recent are ≤ 0.01. Test marked **amended**.

**Amendment A2 (same time; not post hoc).** The card's W-field rule ("f̂ CI includes 0 at every n in ≥ 90% of runs") cannot be met by any calibrated estimator: with five 95% CIs it holds in 77% of no-coupling runs. The field does leak into f̂ levels on #51 (18% with the strong field vs 77% in W0). It does not leak into the shape decisions: false "Langevin beats line" ≤ 0.02 and false Δ_curv > 0 ≤ 0.01 under both field strengths. Change: the shape tests (O2, O3) need false rates ≤ 0.10 under W-field (met). A level f̂(n) counts as read uptake only where the read − in-flight contrast at n = 1 has CI > 0 (false rate ≤ 0.04 under the field, H113 A1's rule). Rule marked **amended**.

**Amendment A3 (same time).** The card does not set the CI method for ĉ and n̂_sat. They use a day bootstrap (300 draws) of the profile fit. O1, O2 and O4 keep the card's agent-day cluster bootstrap (300 draws); ΔLL uses the paired day-fold bootstrap (1000 draws).

**Amendment A4 (2026-10-07 ~12:20 UTC; triggered by real data on descriptive periods only; not a change of hypothesis).** The first real-data pass (`run.py`, stopped after #2–#12, all descriptive, and an earlier test on #37, descriptive) gave ΔLL(L − line) = −7,443 nats on #11 (gte). One day fold held all rows of three high-k bins, so its amplitudes had no training support. Change: sparse batch-size bins merge (top down) until each amplitude bin has ≥ 100 rows with n ≥ 1 on ≥ 3 days (`h142lib.Design._merge_kbins`). #51 keeps all 26 bins; #13 and #38 merge to 15. The synthetic sets were rerun with A4 (tables above). Seen before A4: only the ΔLL, n̂_sat and verdict lines of #2–#12 and #37 (all unscored). No scored period was run before A4.

**Not run:** N1 cross-day surrogate batches. Direction labels come from day-fold centroids, so u on one day does not match u on another day; a surrogate batch would need a cross-day centroid match, which the card does not define. N2 (within room × hour permutation of the aligned-count vectors) is run on the eligible bge periods.


### Step 3: exploration data (2026-10-07, after A1–A4)
`analysis/run.py --perms 50` on all 34 non-reserved periods in both models (`results/periods.json`, `pooled.json`, `natives.json`, `nulls.json`). Scored units: bge #13, #38, #51; gte #13, #16, #38, #51. Pools follow exception (d): ΔLL summed over scored periods with per-period day bootstraps; f̂ and ln n̂_sat pooled by DerSimonian–Laird random effects.

**What the data show.** On every scored period the step toward a direction does not rise with the number of aligned reads. f̂(n) sits at 0 within ±0.01 and turns slightly negative at n ≥ 3 on #13 and #51 (bge). The newest batch item carries the only directional pull: +0.0103 [0.0074, 0.0137] on #51 (bge), +0.0127 [0.0096, 0.0158] (gte), +0.019 [0.008, 0.031] on #38 (bge). For scale, the H113-calibrated linear channel gives f̂(1) ≈ 0.02 on the #51 skeleton; the observed #51 f̂(1) is 0.0000 [−0.0022, 0.0023] (bge).

| # | Prediction | Result (bge; gte) | Verdict by the rule |
| --- | --- | --- | --- |
| **P1** (primary) | pooled ΔLL(L − line) > 0 with CI > 0, and > 0 in ≥ 2/3 of powered periods | −9.0 [−17.2, −2.2] nats, 0/3 positive; +6.1 [−4.1, 15.7], 2/4 positive | **failed (kill)** |
| P2 | pooled Δ_curv > 0 with CI > 0 | undefined: pooled f̂(3) −0.0075 [−0.0117, −0.0033] (bge), f̂(6+) −0.012 [−0.017, −0.007] (gte) | failed |
| P3 | pooled n̂_sat ∈ [1.5, 6] | 37 [3.4, 407] (bge, RE pool, 3 periods); 12 [1.8, 77] (gte) | failed |
| P4 | ĝ(1)/f̂(1) ≤ 0.5 and read − in-flight at n = 1 > 0 | contrast −0.0025 [−0.0078, 0.0029]; −0.0007 [−0.012, 0.010]; ratio undefined (f̂(1) CI includes 0) | failed |
| N1 | #51 wakes: ΔLL CI > 0 and n̂_sat within ×1.5 of talk | −5.3 [−13.3, 1.0]; −7.4 [−18.7, 0.1]; n̂_sat at the grid edges | failed |
| N2 | NE42: |Δ ln n̂_sat| < ln 1.5 | n̂_sat on grid edges (0.1 or 150) on most sides; Δ CIs span the grid | descriptive (folder rule: #40 unidentified, sides unpowered) |
| Kill | linear curve, or line as good out of fold, with power ≥ 0.8 | fires in every scored unit (both clauses in 6 of 7; #16 gte by clause (a) only) | **fires** |

Per scored unit, ΔLL(L − line) out of fold: #13 −3.2 [−8.1, 0.3] / −1.3 [−3.1, 0.0]; #38 −5.1 [−12.1, 0.9] / −6.8 [−10.9, −2.9]; #51 −0.7 [−2.0, 0.5] / +5.7 [−1.8, 11.7]; #16 (gte) +8.4 [3.9, 14.3]. The #16 gte value is the only CI above 0. Its f̂(n) has no positive bin and its power law fits as well (ΔLL(L − pow) 0.9 [−0.7, 2.6]); bge #16 gives −1.1 [−5.7, 3.3].

**Nulls.** The within room × hour permutation of the aligned-count vectors (N2-null; 50 permutations, 25 on #51) brackets every observed bge value: ΔLL(L − line) 95% bands #13 [−7.2, 10.0], #38 [−6.4, 4.2], #51 [−14.9, 4.8]; the observed f̂(1) lies inside its band on #38 and #51 and at the top edge on #13 (0.0056 vs [−0.0068, 0.0056]). N1 (cross-day surrogates) not run (see Step 2).

**Sensitivity (bge, eligible periods).** K = 12 directions: ΔLL(L − line) #13 −1.5 [−3.9, 0.1], #38 −0.8 [−2.4, 0.0], #51 −4.1 [−9.9, 0.1]. Responses flagged as self-repeat, cross-echo or template removed: #13 −2.2 [−5.2, 0.1], #38 −1.8 [−5.5, 1.2], #51 −0.7 [−2.0, 0.5]. The card's pooled-amplitude form (pre-A1) gives the same picture on real data: #13 0.0, #38 −1.9 [−4.4, −0.4], #51 +2.5 [−7.0, 11.2] (bge).

**Post hoc (2026-10-07, after the run; `analysis/posthoc.py`, `results/posthoc.json`).** Question: does the projection or the FE choice erase the curve? Variants on #13, #38, #51 (bge) and #51 (gte): the raw projection (no window field, H113 A1's primary), direction × room × day cells, and both. f̂(1) stays within [−0.004, 0.010] in all 16 fits. The newest-item pull stays at 0.008–0.021 with CI > 0 on #38 and #51. ΔLL(L − line) has CI above 0 in 1 of 16 fits (#38 raw + day: +8.4 [0.2, 18.2]). So the flat curve is not an artifact of the window-field projection or of hour cells.

**Descriptive periods.** No unscored period shows a Langevin curve. The two gte-identified but unpowered periods differ: #35 has a monotone rising f̂ (gte 0.022 → 0.073 at 6+; bge 0.022 → 0.058) with ĝ(1) as large as f̂(1) (bge ĝ(1)/f̂(1) 2.6 [1.4, 4.7]), the field signature; #36 and #37 have f̂(1) 0.016–0.036 with CI > 0 and too few rows for a shape.

### Impostor table (round 1)
| Impostor | Relevant? | How it was handled | Status |
| --- | --- | --- | --- |
| Scheduler field | n/a | Call-level rows; no time-binned synchrony statistic. | n/a |
| Exogenous field (kickoff, goal, operator; hot topics) | yes | Goal, kickoff, room-kickoff and window-field directions projected out; direction × room × hour FE; human and nudge items excluded. Synthetic W-field (×1, ×4) gives false "Langevin beats line" ≤ 0.03 and false Δ_curv > 0 ≤ 0.01. The permutation null brackets the observed values. #35 shows the field signature and is unscored. | removed |
| Shared model priors | yes | `style_resid32` in both models; call FE absorb the reader's state; both models agree on the flat curve. | removed |
| Contemporaneous convergence | yes | In-flight count dummies in every fit. The read and in-flight curves are both flat on scored periods (read − in-flight at n = 1: −0.0025 [−0.0078, 0.0029], bge pool), so no convergence effect needs removing. | removed |

### Scorecard (A–I, round 1)
| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; invariant across families and regimes | 1 | Rows built from ledger pending sets, DQ5 vectors and fold centroids; both models agree; variants proposed for DEFINITIONS.md (not added). Every scored period lies in one regime; invariance across regimes is not tested. |
| B assumptions | stationarity, update order | 1 | A1 found that call FE do not hold the per-read slope fixed; the k-bin amplitudes fix it. Day-fold stability not tested beyond the leave-one-day-out fits. |
| C adequacy | beats the null hierarchy out of fold | 0 | The Langevin form does not beat the line out of fold (bge pool −9.0 [−17.2, −2.2]). |
| D unfitted predictions | signature statistics | 0 | Δ_curv undefined (no positive curve); n̂_sat on grid edges. |
| E interventional | NE prediction | 0 | NE42 descriptive; N1 (#51 wakes) fails. |
| F identifiability | synthetic recovery at village sampling | 2 | n̂_sat recovered within the grid step (n_sat 1 and 3); size ≤ 0.03 for W-lin, W-sel, W-recent, W-field on the main skeletons; power ≥ 0.87 on every scored unit; A1–A4 written before scored data. |
| G ground truth | known structure | 0 | No ground-truth labels apply. |
| H comparative | beats named rivals | 0 | Beats neither R-linear nor R-power; R-recency (the newest item) is the only measured pull. |
| I transfer | other periods, reserved data | 0 | Reserved periods not run. |

**Hypothesis verdict (card rule): failed.** The kill fires in both models with power ≥ 0.8 in every scored unit. Status set below.

**New constants (round 1).**
- f̂(1) (step toward u per one aligned, non-newest read, fixed k and hot topic): #51 0.0000 [−0.0022, 0.0023] (bge), 0.0002 [−0.0022, 0.0023] (gte); bge pool of #13, #38, #51: 0.0012 [−0.0018, 0.0043]. Units: projection of the reader's projected `style_resid32` statement on a unit centroid.
- β_new (newest batch item aligned with u): #51 0.0103 [0.0074, 0.0137] (bge), 0.0127 [0.0096, 0.0158] (gte); #38 0.019 [0.008, 0.031] (bge); #16 0.027 [0.014, 0.039] (gte).

**Claim that stands:** At fixed batch size and fixed hot topic, the content step toward a direction does not grow with the number of aligned reads in the batch: on the powered, field-identified periods (bge #13, #38, #51; gte adds #16) a line fits as well as the Langevin form out of fold (pooled ΔLL(L − line) −9.0 [−17.2, −2.2] nats, bge) and f̂(1) = 0.000 [−0.002, 0.002] on #51, while only the newest item pulls (+0.010 [0.007, 0.014], #51 bge). Exclusions: P2 and P3 undefined (no positive curve to shape); NE42 descriptive (unpowered, #40 unidentified); #16 gte's positive ΔLL is single-model and unreplicated; #35's rising curve is field-type (unscored); post hoc variants are diagnostics only; the gte pool (+6.1 [−4.1, 15.7]) does not exclude 0.

## Round 2 redirects (proposed by the round-1 agent, 2026-10-07)
- **H142-R1. Newest-item channel.** Fit the directional pull of the newest item against its age and rank at fixed k (H113 P7 recast per direction); test whether "send it last" has a measurable saturation in repeats.
- **H142-R2. Named aligned items.** On #51, H29's named pull should appear per direction; the named-count slope here is 0.0026 [−0.0007, 0.0060] (bge) and 0.0107 [0.0077, 0.0140] (gte). Resolve the model split.
- **H142-R3. Where does H113's uptake go?** H113 sees uptake along the batch sum; this card sees none along cluster directions beyond the newest item. Decompose H113's y·s into newest, aligned-cluster and off-cluster parts on the same calls.

## Notes
- 2026-10-07 11:45 UTC: card written from HH385 (approved by Vivian 2026-10-07). In the source HH quote, the HH list's word for out-of-sample data is written as "[out-of-fold]" to follow the house style; the meaning is unchanged.
- The key design choice: call fixed effects hold k fixed, so H113's linear channel (and H113-R2's selection) both predict a straight line in n_u. Saturation at fixed k is new information beyond H113.
- **Proposed DEFINITIONS.md variants (H142):** *content direction u (H142, period clusters)* = one of K = 8 day-fold k-means centroids of projected statement vectors in a period; *aligned-read count n_u (H142)* = batch items (ledger pending set) assigned to u (cosine ≥ 0.3); *directional step y_{c,u} (H142)* = the reader's projected statement at call c dotted with û; *saturation scale n_sat (H142)* = 3/c in f_∞ L(c n); *curvature contrast Δ_curv (H142)* = ln[f(2)/f(1)] − ln[f(6+)/f(3)], zero for any power law or line.
