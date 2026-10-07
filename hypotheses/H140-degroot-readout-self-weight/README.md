# H140: DeGroot at the read-out call: the self-weight of a content step equals the agent's own share of its context

**Status:** pre-registered (not run). Card, observables, nulls and predictions written 2026-10-07 10:05–10:50 UTC, before any H140 statistic on real data. No scheme, synthetic or analysis code has run.
**Question (GOALS.md):** **Q1** (what couples agents: is the read-out update a weighted mean of what the agent wrote and what it read, with weights set by what fills its context?). Second: **Q4** (where the swarm's information lives: in the context window, or in a well that the context does not hold?).
**Fields:** sociophysics (DeGroot and Friedkin–Johnsen opinion dynamics), stat mech (linear vector-spin update), information theory (read-out channel capacity)
**Literature:** none in `literature/` covers DeGroot averaging. Cited from memory (†): DeGroot, *J. Am. Stat. Assoc.* 69, 118 (1974)†; Friedkin & Johnsen, *J. Math. Sociol.* 15, 193 (1990)† (averaging with an anchor to an initial position). Filed notes used through H113: [Barrett 2015](../../literature/barrett-2015-synergy-redundancy-gaussian-systems.md) (Gaussian information of a linear channel). Model references: [`physics-models/11-vector-spins/README.md`](../../physics-models/11-vector-spins/README.md), [`physics-models/02-nonequilibrium-ising/README.md`](../../physics-models/02-nonequilibrium-ising/README.md), [`physics-models/04-semantic-information/README.md`](../../physics-models/04-semantic-information/README.md).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime (III primary); Agent state, **variant vector** (32-d whitened statement vectors, `style_resid32`); **Context fill** and its note (`ctx_pos` counts receiving calls since any reset; null in chat mode); Exposure (turn read-out) and **Interaction (ledger-visible exposure)** (RE-D1) with the **unread (in-flight) exposure placebo**; H67's **in-flight placebo (matched-lag)**; H18's *pending set (talk-call backlog, ledger k)* (RE-V1, shared `pending_sets.py`); **Influence coupling (content pull)** (H29), here as a per-message DeGroot weight; H40's **call clock**. Used as defined in H113 (proposed there): *per-message uptake slope γ(k)*, *total uptake U(k) and capacity exponent a_U*. **New named variants proposed for DEFINITIONS.md** (not edited there; defined under Observables): **context self-share s_self (content, call-entry form) (H140)**, **DeGroot self-weight w_self (H140)**, **summed read weight W_read(k) (H140)**, **anchor weight w_anchor (H140)**, **call gap Δn (H140)**.
**From:** HH383 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/11-vector-spins/` (primary: linear vector update at the read-out call), `physics-models/02-nonequilibrium-ising/` (kinetic update on each agent's calls), `physics-models/04-semantic-information/` (the read-out channel's capacity, as in H113)
**Data inputs (shared tables first):** `pending_sets/G<NN>/` (talks, pending; wakes, wake_pending for #51's timer wakes); `chat_core`; `embeddings/statements.parquet` + `chat_index.parquet`; `statements_{style_resid32,white32}_{bge_small,gte_modernbert}.npy`; `goal_vectors_<model>.npy` + `goals.parquet` (goal, kickoff, kickoff_room) whitened per regime; `producing_calls`; DQ1 `call_windows`, `context_ledger_items`, `context_ledger_turns` (`ctx_pos`, `k_ctx`, `reset_forced`, `reset_consol`, `reset_session`); `chat_mentions_clean` (named items); `statement_flags`; `period_units`, `calendar`, `roster`. No text is read.

## Source HH (verbatim from the HH list)
- **HH383 · DeGroot at the read-out call: the content step is a weighted mean of what was read, with the self-weight set by the context share.** A linear vector-spin update: new content = w_self × own recent content + Σ w_j × read message j. Here w_self is the agent's own share of its context, and the w_j fall with the batch size (H18 dilution).
  - *Prediction:* the fitted w_self rises with own-context share (slope near 1). The summed read weight per call scales as k^0.34 in the batch size k (H18/HH345), not as k.
  - *Check:* content embeddings per call; DQ1 context ledger for the read messages and the context share.
  - *Kill:* w_self is unrelated to the context share, or the read weight grows linearly in k.
  - *Impostors:* simultaneous convergence (H57) makes read and written content similar without any copying. Use the in-flight placebo: messages posted but not yet read.
  - *Models:* 11, 02, 04 · *Builds on:* H48, H18, H113, H44, H57

## Standards (STANDARDS.md)
**Question served:** Q1 (second: Q4).

| Impostor | Relevant? | How it is handled (planned) | Status |
| --- | --- | --- | --- |
| Scheduler field | n/a | Call-level design: one row per talk call; no time-binned synchrony statistic. The call gap Δn enters as a covariate. | n/a |
| Exogenous field (kickoff, goal, operator) | yes | Goal, kickoff and room-kickoff directions and the out-of-batch window field f_c are projected out of every vector (H113's P_c, without the own-content direction). Human and nudge items are excluded from the batch. | removed (planned) |
| Shared model priors (family, style) | yes | `style_resid32` vectors in both models. The agent's own recent content is a regressor, so each agent's prior enters through it. Same-lab vs other-lab read weights as a variant. | partly (planned) |
| Contemporaneous convergence | yes (the HH's impostor) | The in-flight set F_c (others' messages posted after the call's `t_call` and before the statement: unreadable) enters with its own weight γ_F. Read weights are reported net of it, and only units where the read − in-flight contrast is positive are scored (H113 A1's rule). | removed (planned) |

**Inputs:** current tables only (ledger pending sets, DQ5 vectors in both embedding models, ledger visibility).

**Two layers:**
- *Replication* (role `replication`): O1–O3 on every non-reserved regime-III unit with ≥ 300 scored talk calls: units of #37, #38, #39, #40, #41, #42, #44 and 51a–51l. The self-share needs a context segment, which exists only in computer-use mode, so regimes I and II enter only the read-weight test (O2), on H113's field-identified periods #13, #36 (bge) and #16, #35 (gte), as a descriptive check.
- *Natives* (role `native`): **NE41** (a forced erasure drops the self-share to near 0 at a time set by the scaffold), **G51** (timer-wake batches, where k is set by others while the reader sleeps: H18's design D2). Each has a dated prediction in its folder.

**Unit-of-analysis exception (named):** (d) units with < 300 scored talk calls enter only through a random-effects pool, reported next to the per-unit values.

## Question
When an agent reads a batch of k messages and then writes, is its new content a weighted mean of its own recent content and the batch, with the self-weight equal to its own share of the context window and the read weights diluted by k? Or does the agent's content persistence come from a well that the context does not hold (H130, H46), so that the self-weight is set by time since its last statement, not by what fills its context?

**Practical payoff:** if w_self follows the context share, an operator can raise or lower how much an agent listens by changing what fills its context (for example by the cap at which context is erased). If it does not, the context is not the lever.

## Model
**From:** `physics-models/11-vector-spins/` (linear update at the read-out call).

**H140 variant: Friedkin–Johnsen DeGroot on the call clock.** At talk call c, agent i writes y_c:

  y_c = w_self(c) p_c + Σ_{m ∈ B_c} w_m(k_c) x_m + γ_F Σ_{m ∈ F_c} x_m + w_anchor h_i + ε_c,

with all vectors projected by P_c (fields removed) and measured as deviations from the period mean.
- p_c: own recent content = the mean of i's last two statements in the current context segment (variant: the last one).
- B_c: the batch (H18's ledger pending set since the previous talk call), k_c = |B_c|. Per-message weight w_m(k) = γ₁ k^{−b} (H113); **summed read weight W_read(k) = k γ₁ k^{−b} ∝ k^{a}**, a = 1 − b.
- h_i: the agent's leave-day-out well centre (H130). w_anchor is the pull toward it (Friedkin–Johnsen).
- **HH383's rule:** w_self(c) = s_self(c), the agent's own share of its context.
- **Closure (literal DeGroot):** w_self + W_read + w_anchor = 1.

**Rivals (named):**
- **R-well (H130):** content persistence lives in a well, not in the context. Between two statements Δn calls apart, w_self = (1 − γ_auto)^{Δn} with γ_auto ≈ 0.0094 per call (H130), independent of s_self. Supporting evidence seen before writing: content does not move at forced erasures (H46: T 0.51), own content memory survives an erasure (H130: R_C 1.03 [0.95, 1.10]), and pull toward new items does not rise after a wipe (H44: D −0.026 [−0.064, 0.012]).
- **R-linear (no bottleneck):** W_read ∝ k (a = 1). The HH's second kill.
- **R-capacity (one read per call):** W_read flat in k (a = 0; H59's dose result).
- **R-convergence (H57):** read and written content are similar because agents respond to the same moment. Then γ_F ≈ γ₁ and the read − in-flight contrast is 0.

## Data scheme (`scheme/`)
`scheme/build.py --period G<NN>` writes `data/processed/H140-degroot-readout-self-weight/G<NN>/` from shared tables only (projected coordinates as float16; no raw text embeddings beyond the shared arrays; no text). Reserved days are already absent from `pending_sets`; every other table passes the shared reserved-data mask (`infra/shared/common.py`). Budget ≤ 100 MB.
- **Rows:** one per scored talk call c (pending-set `talks`) with a statement by the reader at c and ≥ 2 earlier statements by the reader in the same context segment (segments cut at `reset_consol | reset_session`; the ledger's `first_of_day` is not a reset in regime III, infra Known issues).
- **Context self-share s_self(c) (H140, call-entry form):** ctx_pos(c) / (ctx_pos(c) + k_ctx(c)): the agent's own receiving calls in the segment against the other agents' items received in it (`context_ledger_turns`). Variant (chat form): n_own_chat / (n_own_chat + k_ctx), own chat statements in the segment.
- **Call gap Δn (H140):** own calls between the producing calls of p_c's latest statement and of y_c.
- **Batch and in-flight sums:** s_c = Σ_{m∈B_c} P_c x_m, s^F_c = Σ_{m∈F_c} P_c x_m (H113's definitions, built in H140's own code from `pending_sets`).
- **Instrument for p_c:** the mean of the reader's third- and fourth-last statements in the same segment (errors-in-variables: statement noise in p_c would bias w_self toward 0).
- **Wells:** h_i leave-day-out (H130's rule).
- **Output:** `G<NN>/calls_<model>.parquet` (call id, agent, day, room, k, k_F, s_self, s_self_chat, ctx_pos, k_ctx, Δn, projected inner products needed for the fits), `counts.json`, `_provenance.json`; `results/`, `synthetic/`.
- **Regimes covered:** III (primary); I and II for O2 only.

## Observables
*Specified 2026-10-07 10:05–10:50 UTC, before any H140 statistic.* Primary vectors: `style_resid32` × bge_small; variant gte_modernbert and `white32`.
- **O1 self-weight law (primary).** Two-stage least squares over the 32 coordinates of y_c (one scalar weight per term), p_c instrumented as above: w_self(c) = w₀ + w₁ s_self(c) + w₂ (1 − γ̂_auto)^{Δn} (γ̂_auto from H130 in #51; re-estimated with H130's drive-corrected estimator elsewhere), plus γ(k) s_c (profile over b), γ_F s^F_c and w_anchor h_i. Agent-day cluster bootstrap (300 draws). **w₁** is the HH's slope. Variants: without the Δn term (the HH's form); s_self in chat form; s_self in deciles (shape).
- **O2 read-weight exponent.** â = 1 − b̂ from the profile fit of O1 (H113's estimator with p_c as a regressor rather than projected out). Testable only where the read − in-flight contrast is positive (H113 A1).
- **O3 closure.** Σ̂ = ŵ_self + Ŵ_read(k) + ŵ_anchor, per k bin {1, 2, 3–4, 5–8, 9–16, ≥ 17}.
- **O4 convergence check.** γ̂_F / γ̂₁ and the matched-age read − in-flight contrast (H113's O5).
- **O5 erasure step (native NE41).** At each agent's first talk call after a forced reset vs its talk calls at segment position ≥ 5: Δs_self and Δŵ_self (O1 fitted with a first-call indicator interacting with p_c, where p_c is the agent's last pre-reset content, which is no longer in the context).

**Estimates rows** (`per_period_estimates`, hypothesis H140): `h140_selfweight_slope_w1`, `h140_selfweight_callgap_w2`, `h140_readweight_exponent`, `h140_closure_sum`, `h140_inflight_ratio`, `h140_erasure_selfweight_step`, per unit and model.

## Null / baseline
- **N0:** w₁ = 0 (Wald with agent-day cluster bootstrap).
- **N1 cross-day surrogate batch** (H113): each call's batch replaced by a batch of the same k from another day of the unit; gives the null of γ(k) and of a.
- **N2 within-agent-day permutation of s_self** across talk calls (keeps its distribution, breaks its link to the step): the size of O1's w₁.
- **N3 synthetic worlds** (below).

## Synthetic validation plan (axis F; runs before any real-data statistic)
Worlds on the real skeletons of units 51c and 51g and of #38 and #41: every scored talk call with its real k, k_F, ctx_pos, k_ctx, Δn, batch membership and resets; synthetic 32-d vectors calibrated to the real |y⊥|² (no real y·s product is used). 100 replicates per world.
- **W-DG (HH383):** w_self = s_self, read weights γ₁ k^{−0.75}, small anchor.
- **W-well (R-well):** OU content per call with γ = 0.0094 (H130), read kicks J = 0.044 decaying at 0.15 per call; no context dependence.
- **W-field:** a time-local room topic field (τ = 30 min), no reading (H113's W1).
- **W-lin:** linear superposition (b = 0).
- **Decision rules fixed now:** O1 must recover w₁ = 1 within ±0.2 in W-DG; its false w₁ > 0 rate must be ≤ 0.10 in W-well *with* the Δn term (if not, the Δn term alone cannot separate the two, and P1 is read only together with the NE41 native); power ≥ 0.8 at w₁ = 0.5 is needed for the kill's first clause. O2 must keep H113's coverage (≥ 0.8) with p_c as a regressor. Estimator changes after the synthetic are dated amendments, made before real data.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R-well (H130's call-gap self-weight), R-linear (no bottleneck), R-capacity (one read per call), R-convergence (H57).
**Reserved periods used for confirmation:** none (not run). Planned: talk calls of #43, #45–#47 and the #51 tail (talk calls and timer wakes), ledger family `readout_capacity` (shared with H113: disclose; H18 and H68 `dilution_addressing` plan the same targets). A frozen, guarded confirm script is written only after exploration and runs only with Vivian's sign-off.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 0 | not run |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 0 | not run |
| C adequacy | beats the null hierarchy, day-blocked out-of-fold data | 0 | not run |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | not run |
| E interventional | predicts the change across a natural experiment | 0 | not run |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 0 | not run |
| G ground truth | agrees with known structure | 0 | not run |
| H comparative | beats the named rivals | 0 | not run |
| I transfer | holds in other same-mode periods, including the reserved periods | 0 | not run |

## Prediction
*Written 2026-10-07 10:05–10:50 UTC, before running the analysis on real data.*

**What I had seen when writing this:** H113's card (a_U 0.31 [0.25, 0.37] on #51 timer wakes, 0.23 [0.16, 0.31] pooled over 6 field-identified talk-call periods, bge; gte agrees; HH345's 0.34 excluded by the talk-call pool; H18's corrected 0.50 excluded; γ_F/γ₁ median 0.31; read − in-flight contrast +0.014 [0.006, 0.022]; newest item taken up more, +0.034; a topic field alone gives b̂ ≈ 0.8, so only 6–7 of 34 periods are scored); H18 (ledger pending-set exponent 0.66 ± 0.02; #51 timer-wake D2 0.50 [0.45, 0.56]); H29 (per-message pull in #51: named 0.03–0.09 of the gap, unnamed 0.009–0.021); H48 (if read-out drives settling, each read moves an agent by about 1/250); H130 (γ_auto 0.0094 per call; R_C 1.03 at NE41); H46 (content T 0.51 at erasures); H44 (after a wipe, D −0.026 [−0.064, 0.012], G51 −0.027 [−0.047, −0.007]); H57 (near-copies of read items are rare, 0.1–2%; most near-duplication is convergence); H72 (an idle-call self-share of the context carries 65% [59, 71] of trap aging in #51, coefficient 1.09 [0.81, 1.33]). **Not seen:** any s_self value, any self-weight, and any H140 fit.

**Synthetic (axis F).**

| # | Prediction | Counts against |
| --- | --- | --- |
| S1 | O1 recovers w₁ = 1 ± 0.2 in W-DG; false w₁ > 0 ≤ 0.10 in W-well with the Δn term | bias > 0.2 or false rate > 0.10 |
| S2 | Power for w₁ = 0.5 ≥ 0.8 in the pool of #51 units | < 0.8 (then the kill's first clause cannot fire) |

**Replication layer (regime III).**

| # | Prediction [credence] | Counts against |
| --- | --- | --- |
| **P1** (primary, HH) | **Self-weight follows the context share.** Pooled ŵ₁ ∈ [0.5, 1.5] with CI above 0, and ŵ₁ > 0 (CI) in ≥ 1/2 of testable units [0.15] | pooled ŵ₁ CI includes 0 with power ≥ 0.8 (**kill, clause 1**) |
| **P2** (HH) | **Sublinear read weight.** Pooled â ∈ [0.15, 0.40] with CI excluding 1 and below 0.7 (H113's range, not HH345's exact 0.34) [0.65] | â CI includes 1 or â ≥ 0.7 (**kill, clause 2**) |
| P3 | **R-well holds the persistence.** The call-gap term ŵ₂ > 0 (CI) and adding it lowers ŵ₁ by ≥ 50% [0.55] | ŵ₂ CI includes 0 |
| P4 | **Not convergence.** γ̂_F / γ̂₁ ≤ 0.5 and the read − in-flight contrast > 0 (CI) pooled [0.7] | γ̂_F / γ̂₁ > 0.5 |
| P5 (secondary) | **Closure.** Σ̂ ∈ [0.8, 1.2] in ≥ 2/3 of k bins (literal DeGroot) [0.3] | outside in > 1/3 |

**Native layer** (each repeated in its folder).

| # | Unit | Prediction [credence] | Counts against |
| --- | --- | --- | --- |
| N1 | NE41 | HH383 at an erasure: Δŵ_self ≈ Δs_self (the self-weight on pre-reset content falls with the self-share; ratio Δŵ_self / Δs_self ∈ [0.5, 1.5]) [0.1] | Δŵ_self CI includes 0 while Δs_self is large (R-well) |
| N2 | G51 | On timer-wake batches (k set by others), the same w₁ as on talk calls (|Δw₁| < 0.3) and â in [0.15, 0.45] [0.35] | |Δw₁| ≥ 0.3 or â outside |

**Kill rule (HH383).** Clause 1 fires if the pooled ŵ₁ CI includes 0 and the synthetic power at w₁ = 0.5 is ≥ 0.8. Clause 2 fires if the read weight grows linearly in k (â CI includes 1, or â ≥ 0.7). Either clause kills HH383 as posed.

**Hypothesis-level verdict rule.** *Supported* if P1 and P2 pass and neither kill clause fires. *Failed* if either clause fires (if only clause 1 fires and P2 passes, the card states "the read channel is sublinear as in H113, but the self-weight is not the context share"). *Inconclusive* otherwise, including clause 1 untestable for power.

**My credence before data:** supported 0.1; failed 0.6 (mostly clause 1, with R-well); inconclusive 0.3.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication (two rooms, regime III) | pending | — |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication (51a–51l) + native N2 (timer wakes) | pending | — |
| [NE41](goalperiod-subhypotheses/NE41/README.md) | native N1 (forced erasures) | pending | — |

Other testable units (#37, #39–#42, #44; regime I/II O2 periods) get their period folders, with the predictions copied and dated, before the run.

## Results
Not run.

## Notes
- 2026-10-07 10:05 UTC: card written from HH383 (approved by Vivian 2026-10-07).
- The HH's exponent "k^0.34 (H18/HH345)" is sharpened to H113's measured range: HH345's 0.34 was excluded by H113's talk-call pool (0.23 [0.16, 0.31]) while the timer-wake value (0.31 [0.25, 0.37]) contains it. P2 therefore tests the band [0.15, 0.40], with the HH's "not linear" as the kill.
- The self-share here is the call-entry form (own receiving calls vs received items). H72's idle self-share (own idle calls among own calls) is a different ratio; both are context-held shares, and H140 reports their correlation as descriptive.
- **Proposed DEFINITIONS.md variants (H140):** *context self-share s_self (content, call-entry form) (H140)* = ctx_pos / (ctx_pos + k_ctx) at a call in computer-use mode, with a chat form n_own_chat / (n_own_chat + k_ctx); *DeGroot self-weight w_self (H140)* = the IV weight of the agent's own recent content (last two statements in the segment) in its next statement, fields projected out; *summed read weight W_read(k) (H140)* = k γ(k), the total weight of a k-message batch; *anchor weight w_anchor (H140)* = the weight on the leave-day-out well centre; *call gap Δn (H140)* = own calls between the latest own statement and the current one.
