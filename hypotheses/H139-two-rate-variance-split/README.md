# H139: A fast read kick on a slow private well predicts how content variance splits between the two

**Status:** exploratory round 1 done (2026-10-07; non-reserved only). **Inconclusive (below resolution).** The synthetic check (S1) fired in all 15 testable units before real data: the read-driven fast amplitude that H130's kick predicts is 90 to > 2,000 times smaller than the smallest fast amplitude the own autocovariance resolves (7 to > 1,000 times on the real noise scale, post hoc). P1 (the HH382 test) and P2 are untestable; the kill cannot fire. P3 and P5 pass but are non-diagnostic; P4 fails. N1 (NE41) is untestable; the slow part passes forced erasures (R_slow 1.06 [0.98, 1.14], descriptive). Post hoc: the drive-corrected fast amplitude is negative (pooled −0.058 [−0.099, −0.017]), because the lag-1 covariance sits below the lag-2 covariance in 14/15 units. Scorecard A1 B1 C0 D0 E1 F1 G0 H0 I0.
*Pre-registration: card, observables, nulls and predictions written 2026-10-07 09:15–10:00 UTC, before any H139 statistic on real data.*
**Question (GOALS.md):** **Q2** (what is field and what is coupling: how much of an agent's content variance is the read channel, and how much is its own well?). Second: **Q1** (does the read kick measured from doses also show up, with the predicted size, in the agent's own fluctuations?).
**Fields:** stat mech (two-rate Langevin relaxation, Ornstein–Uhlenbeck processes, fluctuation–response consistency), stochastic processes (shot noise with exponential memory)
**Literature:** none in `literature/` covers OU processes. Cited from memory (†): Uhlenbeck & Ornstein, *Phys. Rev.* 36, 823 (1930)†; Kubo, *Rep. Prog. Phys.* 29, 255 (1966)† (for a linear Langevin system the impulse response and the autocorrelation decay at one rate); Campbell's theorem for shot noise (Rice, *Bell Syst. Tech. J.* 23, 282 (1944)†): the variance of a sum of decaying kicks is rate × kick² × memory. Model references: [`physics-models/16-langevin-relaxation/README.md`](../../physics-models/16-langevin-relaxation/README.md) (section 4, "two-rate form: a fast kick on a slow well"), [`physics-models/11-vector-spins/README.md`](../../physics-models/11-vector-spins/README.md).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime (III only); Agent state, **variant vector** (32-d whitened statement vectors, `style_resid_period`); Exposure (turn read-out) and **Interaction (ledger-visible exposure)** (RE-D1) with its **unread (in-flight) exposure placebo**; H67's **in-flight placebo (matched-lag)**; H40's **call clock**; **Context fill** and its note (`ctx_pos` counts receiving calls since any reset). Used as defined in H130 (proposed there, not yet in DEFINITIONS.md): *private well centre h_i (leave-day-out)*, *well relaxation rate γ_auto (drive-corrected)*, *read jump J_K*, *sender-specific kick decay γ_kick*, *rate ratio ρ_γ*. **New named variants proposed for DEFINITIONS.md** (not edited there; defined under Observables): **read rate per call r̄ (H139)**, **fast amplitude A_k and slow amplitude A_s (H139)**, **predicted fast amplitude A_k^pred (H139, shot-noise form)**, **fast share f_k (H139)**, **erasure ratio of the fast part R_fast (H139)**.
**From:** HH382 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/16-langevin-relaxation/` (primary: the two-rate form x = s + k), `physics-models/11-vector-spins/` (secondary: linear vector dynamics on the call clock)
**Data inputs (shared tables first):** DQ5 `embeddings/statements.parquet` with `statements_{style_resid_period32,white32}_{bge_small,gte_modernbert}.npy`; `statement_flags` (exact repeats); `chat_core`; `producing_calls`; DQ1 `call_windows` (call clock), `context_ledger_items` (reads per call), `context_ledger_turns` (`reset_forced`, `reset_consol`, `reset_session`, room); `rooms_timeline`; `period_units`; `calendar`; `roster`. Read only: H130's `results/units.parquet` (per-unit J_K, γ_kick, γ_auto) for #51. No text is read.

## Source HH (verbatim from the HH list)
- **HH382 · Content is a fast kick on a slow well: the two-timescale vector spin predicts its own variance split.** H130 found the read kick decays about 15 times faster than the goal well. A vector spin with a slow private well (the style and goal constant) plus a fast read-driven deviation predicts how content variance divides between the two.
  - *Prediction:* the fraction of each agent's content variance at lags of 1 call or less equals (read rate × kick size²) / (total variance), using kick size from H130 and read rate from the ledger, within ×1.5. The slow part matches the H46/H73 agent constant.
  - *Check:* H130 kick and well rates; per-agent content embeddings (O(32) basis); read counts per call.
  - *Kill:* the predicted fast share is off by more than ×2 in most agents.
  - *Impostors:* topic changes inside a goal look like fast variance. Remove the room and goal field per hour first.
  - *Models:* 11, 16 (proposed Langevin) · *Builds on:* H130, H97, H46, H73

## Standards (STANDARDS.md)
**Question served:** Q2 (second: Q1).

| Impostor | Relevant? | How it is handled (planned) | Status |
| --- | --- | --- | --- |
| Scheduler field | partly | Content statistics on the per-call clock (H40); lags only within a PT day, so nights and day edges never enter a lag. | removed |
| Exogenous field (kickoff, goal, operator) | yes (the HH's impostor) | Drive correction as in H130 A1: the agent's own autocovariance minus the cross-agent covariance at the same wall lag, per room class. Variant: room × hour means subtracted first (the HH's wording). Wells (leave-day-out) remove static fields. Round 1: in the synthetic, a strong 5-min drive still gives a false Â_k > 0 in 5–27% of replicates. On real data the correction also subtracts pair co-movement at short wall lags (post hoc reading of the negative Â_k). | partly |
| Shared model priors (family, style) | yes | `style_resid_period` vectors; wells absorb each agent's prior; `white32` and gte variants give the same signs. | removed |
| Contemporaneous convergence | yes | The kick inputs (J_K, γ_kick) come from H130's read-minus-in-flight estimator (re-run here for #37–#42). The autocovariance side is own-agent only. The P1 comparison it would protect is untestable (S1). | partly (moot for P1) |

**Inputs:** current tables only (DQ1 ledger, DQ5 vectors with both embedding models, `statement_flags` dedupe).

**Two layers:**
- *Replication* (role `replication`): the variance split (O1–O4) on every non-reserved regime-III unit with ≥ 3 days: units of #38, #39, #40, #41, #42, #44 (#37 has 3 days and is included if its units pass the counts) and 51a–51l. In the shared-goal weeks the kick inputs (J_K, γ_kick) are first re-estimated with H130's A1 estimators in H139's own code (H130-R4's transfer). Units with < 3 days are descriptive.
- *Natives* (role `native`): **NE41** (forced erasures at the 41-turn cap: does the fast part die at an erasure while the slow part survives?), **G51** (the primary replication, where H130's inputs were measured, plus the cross-agent dose test of the read rate). Each has a dated prediction in its folder.

**Unit-of-analysis exceptions (named):** (b) **agent-level property**: the well centre h_i is estimated leave-day-out within a period; P4 tests whether the slow share is an agent constant across units before treating it as one. (d) short units enter only through a random-effects pool reported next to the per-unit values.

**Regimes I and II are not used:** chat-mode calls rebuild the prompt from recent chat and post few statements per call, so the per-call clock and the per-call read count are not comparable (H130 used regime III only). Declared before any statistic.

## Question
H130 found that in #51 a read kicks the reader's content (J_K 0.044 [0.038, 0.050]), the kick fades in about 7 calls (γ_kick ≈ 0.13–0.17 per call), and the agent's own content relaxes to its private well in about 100 calls (γ_auto 0.0094 [0.0076, 0.0115]). If content is the sum of a fast read-driven part and a slow well-held part, the fast part's variance is fixed by the read rate, the kick size and the kick memory, with no new fit. Does the agent's own autocovariance show a fast component of exactly that size?

**Practical payoff:** the fast share says how much of what an agent writes at any moment is an echo of what it just read. An operator who wants an agent's output to reflect its own task rather than the chat can read that share off two numbers: reads per call and kick size.

## Model
**From:** `physics-models/16-langevin-relaxation/` (two-rate form) on the call clock of H40.

**H139 variant: shot-noise kicks on an OU well.** Agent i's content state x_i(n) ∈ ℝ³² (deviation from its leave-day-out well centre h_i) at its own call n is x = s + k:
- slow part: s(n+1) = (1 − γ_s) s(n) + ξ(n) (the well; γ_s ≈ γ_auto);
- fast part: k(n+1) = (1 − γ_k) k(n) + Σ_{m read at n} J_m û_m (each read m adds a kick J_m along its idiosyncratic direction û_m, as in H130);
- a statement emitted at call n is z_B = h_i + s(n) + k(n) + ε_B (statement noise ε enters only at lag 0).

**Consequences (unfitted).** For lags τ ≥ 1 call within a day, the own autocovariance is

  C(τ) = A_k (1 − γ_k)^τ + A_s (1 − γ_s)^τ + B,

with B a plateau for slow well drift within a day (H98: day-level project drift). Kick directions from different reads are independent, so Campbell's theorem gives the fast amplitude with no free parameter:

  **A_k^pred = r̄ ⟨J²⟩ / [1 − (1 − γ_k)²]**,

with r̄ the agent's mean number of agent messages newly read per call (DQ1 ledger), ⟨J²⟩ the mean squared kick per read, and γ_k the kick decay. The factor 1/[1 − (1 − γ_k)²] is the kick memory in calls: 3.2–4.1 for γ_k 0.13–0.17. The HH's ratio "(read rate × kick size²)/(total variance)" omits this factor; it is kept as the HH-literal variant, and it is 3–4× smaller than A_k^pred by construction.

**Order of magnitude (derived before data, from H130's rounded numbers).** H130 states that one read's jump is ≈ 0.13 of the per-direction spread of x. If that spread means √(E|x|²/32), then ⟨J²⟩ ≈ 0.017 E|x|²/32 and the predicted fast share is f_k^pred ≈ 0.017 × 3.6 / 32 ≈ 0.002 per read per call. The predicted fast part is therefore small: about 0.2% of the dynamic content variance for each agent message read per call. The synthetic must show whether a component of that size can be resolved at the real statement counts (below).

**Rivals (named):**
- **R-innovation (own fast noise):** the fast variance comes mainly from the agent's own sub-task switches and tool outputs, not reads. Â_k ≫ A_k^pred.
- **R-one-rate:** the autocovariance has no fast component at all (Â_k CI includes 0, and a one-exponential fit is not worse out of fold). The kick then lives only in the next statement (H130 finding 1: "a short echo in the next statement or two").
- **R-segment-offset (H46 for style):** a per-segment offset redrawn at each erasure. For content H46 found no move at erasures (T 0.51), so this rival predicts no fast drop across an erasure.
- **R-drive (the HH's impostor):** topic changes inside a goal add a common fast component. The drive correction removes it; the raw autocovariance keeps it.

## Data scheme (`scheme/`)
`scheme/build.py --period G<NN>` writes `data/processed/H139-two-rate-variance-split/G<NN>/` from shared tables only (codes and row ids; no text). Reserved days and periods are dropped twice (`calendar` flags and the shared reserved-data mask in `infra/shared/common.py`). Budget ≤ 100 MB.
- **Statements:** DQ5 chat statements of agent speakers, non-reserved, joined to `chat_core` and `producing_calls`; exact self-repeats (`statement_flags.exact_self_repeat`) and fallback producing calls dropped (H130's rules).
- **Call clock:** each agent's `call_windows` rows per PT day, numbered n = 0, 1, 2, … (all call kinds; H130).
- **Reads per call:** `context_ledger_items` rows of kind `agent` with sender ≠ reader, per receiving call. **Read rate r̄ (H139):** the mean of this count over the agent's calls in the unit (variant: over talk calls only).
- **Resets:** `context_ledger_turns.reset_forced` (NE41) and `reset_consol | reset_session` per call; each statement pair is marked "crosses a forced reset" or not.
- **Wells:** h_i = mean of agent i's statement vectors over its non-reserved days in the period except the statement's own day (H130). Agents need ≥ 2 days.
- **Output:** `G<NN>/statements.parquet` (agent, day, call index n, row id, reset counters), `G<NN>/reads.parquet` (reader, call, count, sender), `G<NN>/calls.parquet`, `_provenance.json`; `results/`, `synthetic/`.
- **Regimes covered:** III only.

## Observables
*Specified 2026-10-07 09:15–10:00 UTC, before any H139 statistic.* Primary vectors: `style_resid_period` × bge_small; variants `white32` and gte_modernbert. Products are unnormalized dot products (H130's convention).
- **O1 own autocovariance at 1-call resolution.** C_i(τ) = mean x_B · x_B′ over pairs of agent i's statements on one PT day with call lag τ ≥ 1, in bins {1}, {2}, {3}, {4–5}, {6–7}, {8–11}, {12–15}, {16–23}, {24–31}, {32–63}, {64–127}, {128–255}, {256–511}, {512–1023}. **Drive-corrected** (primary): minus the cross-agent covariance at the same wall lag (H130 A1 point 3). **Variant:** room × hour means subtracted from every vector first.
- **O2 two-rate fit.** Weighted nonlinear least squares of C(τ) = A_k (1 − γ_k)^τ + A_s (1 − γ_s)^τ + B on the bins (weights 1/bootstrap variance). **Primary (constrained):** γ_k fixed at the unit's read-dose estimate (H130's sender-specific distributed lag, A1 point 2); A_k, A_s, γ_s, B free. **Variant (free):** all five free. **Comparison:** the one-rate fit A e^{−γτ} + B, by day-blocked out-of-fold squared error. Uncertainty: agent-day block bootstrap within unit (200 draws), the same draws for every quantity.
- **O3 predicted fast amplitude.** A_k^pred = r̄ ⟨J²⟩ / [1 − (1 − γ̂_k)²], per unit and per agent-unit. ⟨J²⟩: primary J_K² (the squared mean jump, a lower bound of the second moment); variant κ̂² ⟨|(z_m − h_i)_⊥|²⟩ with κ̂ the read-minus-in-flight slope on the offset size. **Consistency ratio** Q_k = Â_k / A_k^pred (the HH's test). **Fast share** f_k = Â_k / (Â_k + Â_s + B̂); predicted f_k^pred = A_k^pred / (Â_k + Â_s + B̂).
- **O4 slow share and its constancy.** f_s = (Â_s + B̂)/(Â_k + Â_s + B̂) per agent-unit. Split-unit Spearman of f_s across agents (odd vs even units of #51; first vs second half of days elsewhere), with an agent-label permutation null (2,000 draws).
- **O5 erasure ratio of the fast part R_fast (native NE41).** Pairs at lags 1–7 calls that cross a forced reset vs pairs that do not, matched on lag bin and agent-day: R_fast = [C_cross − Ĉ_slow] / [C_within − Ĉ_slow], with Ĉ_slow = the fitted slow part at that lag. R_slow uses lags 32–255 (as H130's R_C).
- **O6 dose test across agents.** Within units, across agents: slope of ln Â_k,i on ln r̄_i (agent-units with ≥ 3 days and Â_k,i > 0 in ≥ 90% of bootstrap draws; Tobit-type handling otherwise).

**Estimates rows** (`per_period_estimates`, hypothesis H139): `h139_fast_amp`, `h139_fast_amp_pred`, `h139_fast_ratio_Qk`, `h139_fast_share`, `h139_slow_share`, `h139_read_rate`, `h139_erasure_fast_ratio`, per unit and model.

## Null / baseline
- **N0 one-rate OU:** A_k = 0; the one-rate fit is the baseline for O2.
- **N1 cross-day surrogate:** each statement pair re-paired with the same agent's statements at the same call lag on another day (removes day-locked drives; a check of the drive correction).
- **N2 synthetic worlds on the real skeleton** (below), which size every estimator and give the minimal detectable fast amplitude.

## Synthetic validation plan (axis F; runs before any real-data statistic)
Worlds keep each unit's real statements, producing calls, call clock, reads and resets (units 51c, 51d, 51g and the #38 and #41 units). Parameters from H130 A1's synthetic: statement noise 0.6, well 0.25, OU state 0.2 per dimension; room drive 0.05–0.2 per dimension with time scales 5 min–3 h; 100 replicates per world.
- **W1 two-rate (H139):** γ_s = 0.01, γ_k = 0.15, kicks J = 0.044 along idiosyncratic message directions at the real reads.
- **W1×5 and W1×20:** fast amplitude raised 5× and 20× by own fast innovations (R-innovation).
- **W0 one-rate:** no fast part.
- **W-ctx:** the fast part is erased at forced resets (context-held kick, H130's R1 world).
- **Decision rules fixed now:** (i) the minimal detectable fast amplitude A_min = the smallest A_k with Â_k CI above 0 in ≥ 80% of W1-type replicates. If A_min > 2 A_k^pred, P1 is **untestable**: the card reports an upper bound on Â_k and the verdict is "inconclusive (below resolution)", not "supported" or "failed". (ii) Q_k is unbiased within ±30% in W1×5 and W1×20. (iii) The constrained fit's false Â_k > 0 rate ≤ 0.10 in W0. (iv) R_fast separates W-ctx (< 0.3) from W1 (> 0.7) in ≥ 80% of replicates; else N1 is descriptive.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R-innovation (own fast noise), R-one-rate (no fast part), R-segment-offset (H46-type), R-drive (common topic drift).
**Reserved periods used for confirmation:** none. Planned: the #51 tail (2026-09-07 → 09-21) and #45–#47, ledger families `kick_response` and `content_alignment`. Overlaps to disclose: H130 (#51 tail, same families), H54, H97, H100, H102, H107, H108, H109 on #45–#47 content. A frozen, guarded confirm script is written only after exploration and runs only with Vivian's sign-off.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Read rate from the ledger; wells, clock and autocovariance from DQ5 and `call_windows`. Same signs with bge, gte and white32. Regime III only. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | The slow part behaves (γ_s 0.0075–0.023/call in #51, H130 γ_auto 0.0094). The fast form A_k (1−γ_k)^τ ≥ 0 is contradicted at τ = 1: lag-1 covariance < lag-2 covariance in 14/15 units (post hoc). |
| C adequacy | beats the null hierarchy, day-blocked out-of-fold data | 0 | Two-rate beats one-rate out of fold in 9/15 units; the W0 size of that comparison is 34–58%. |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | The unfitted prediction (A_k^pred) is below resolution in every unit (S1). |
| E interventional | predicts the change across a natural experiment | 1 | NE41: the slow part passes forced erasures (R_slow 1.06 [0.98, 1.14], 15 units). The fast part is untestable (S1, S3). Descriptive. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | 11,600 replicates on 15 real skeletons: Â_k unbiased (L3 bias −11% to +7%), W0 false rate ≤ 0.08. But the target amplitude is 90 to > 2,000× below A_min, and the synthetic noise scale exceeded the real one (post hoc). |
| G ground truth | agrees with known structure | 0 | No known structure tested. |
| H comparative | beats the named rivals | 0 | H139, R-one-rate and R-segment-offset are indistinguishable at this resolution. Post hoc: no positive fast part above +0.07 in 14/15 units, which bounds R-innovation only in absolute terms. |
| I transfer | holds in other same-mode periods, including the reserved periods | 0 | Nothing resolved to transfer; reserved periods not used. |

## Prediction
*Written 2026-10-07 09:15–10:00 UTC, before running the analysis on real data.*

**What I had seen when writing this:** H130's full card (J_K 0.044 [0.038, 0.050] bge, 0.049 gte; γ_auto 0.0094 [0.0076, 0.0115] per call with I² 0 over 12 units; γ_kick ≈ 0.13–0.17; ρ_γ 14.8 [7.2, 30.4]; R_C 1.03 [0.95, 1.10] at NE41; R_K undefined because the kick had decayed before lag 4; the jump is ≈ 0.13 of the per-direction spread of x; median 761 calls and 20 chat statements per agent-day in #51); H46 (content does not move at forced erasures, T 0.51 in both models; style carries a per-segment offset); H73 (the agent constant has the largest unique share of style in 34/34 periods, median 0.55; about three quarters of a message's style is noise); H97 (the kickoff well is stiffer along k̂); H44 (after a wipe, content pull toward new items does not rise, D −0.026 [−0.064, 0.012]); model 16's combined result. **Not seen:** any read count per call, any autocovariance at 1-call resolution, and any shared-week kick estimate.

**Synthetic (axis F).**

| # | Prediction | Counts against |
| --- | --- | --- |
| S1 | A_min > 2 A_k^pred in #51 units at r̄ ≤ 2 reads per call: the HH's ×1.5 band cannot be resolved there | A_min ≤ A_k^pred |
| S2 | Q_k is unbiased within ±30% in W1×5 and W1×20 | bias > 30% |
| S3 | R_fast separates W-ctx from W1 in ≥ 80% of replicates | < 80% |

**Replication layer.**

| # | Prediction [credence] | Counts against |
| --- | --- | --- |
| **P1** (primary, HH) | **Fast amplitude as predicted.** The random-effects pool of ln Q_k over testable units lies in [ln ⅔, ln 1.5], with its 90% CI inside [ln 0.5, ln 2] [0.10] | pooled Q_k outside [0.5, 2] with CI excluding 1 (**kill**) |
| P2 | **The fast part scales with reading.** Across agents within units, the slope of ln Â_k,i on ln r̄_i lies in [0.5, 1.5] with CI above 0 (pooled over units) [0.25] | slope CI includes 0 |
| P3 | **Slow dominates.** f_s ≥ 0.8 in ≥ 2/3 of testable units [0.65] | f_s < 0.8 in > 1/3 |
| P4 | **The slow share is an agent constant.** Split-unit Spearman of f_s ≥ 0.3 with permutation p < 0.05 (#51) [0.35] | p ≥ 0.05 |
| P5 (secondary) | **Two rates beat one.** The constrained two-rate fit beats the one-rate fit out of fold in ≥ 1/2 of testable units [0.4] | one-rate wins in > 1/2 |

**Native layer** (each repeated in its folder).

| # | Unit | Prediction [credence] | Counts against |
| --- | --- | --- | --- |
| N1 | NE41 | The fast part dies at a forced erasure and the slow part survives: R_fast < 0.5 and R_slow ≥ 0.8 [0.3] | R_fast ≥ 0.8 (the fast part is not context-held) |
| N2 | G51 | #51 replicates P1–P4 on H130's own units, with H130's γ_kick and J_K as inputs [as P1–P4] | as P1 |

**Kill rule (HH382).** The kill fires if the predicted fast amplitude is off by more than ×2 in most agents: Q_k,i outside [0.5, 2] in > 1/2 of agent-units with a resolved Â_k,i, *and* the pooled Q_k 90% CI excludes [0.5, 2]. If S1 holds (A_min > 2 A_k^pred), the kill cannot fire in that unit; only a lower bound Q_k ≥ A_min/A_k^pred is reported there.

**Hypothesis-level verdict rule.** *Supported* if P1 and P2 pass. *Narrowed* ("the read channel sets only part of the fast variance") if P1 fails high (Q_k > 2) but P2 passes. *Failed* if the kill fires and P2 fails. *Inconclusive* if the fast amplitude is below resolution in most units (S1).

**My credence before data:** supported 0.1; narrowed 0.15; failed 0.35; inconclusive (below resolution) 0.4. The most likely failure mode is R-innovation: a fast component much larger than the read channel explains.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
Primary variant `style_resid_period` × bge, drive-corrected. "n/a (inconclusive)" = S1 fired before real data, so the registered test is untestable there.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication (1 unit, 3 days) | n/a (inconclusive: below resolution) | A_k^pred 0.019; Â_k −0.043 [−0.142, 0.033]; A_min/A_k^pred > 150 (8.6 real scale) |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication (38a, 38b, 38e testable) | n/a (inconclusive: below resolution) | A_k^pred 0.0004–0.0051; Â_k −0.22 to +0.22, CIs span 0 except 38b (below 0) |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication (1 unit) | n/a (inconclusive: below resolution) | A_k^pred 0.0019; Â_k −0.066 [−0.323, 0.062] |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication (1 unit) | n/a (inconclusive: below resolution) | A_k^pred 0.0020; Â_k 0.035 [−0.031, 0.072] |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication (1 unit) | n/a (inconclusive: below resolution) | J_K 0.003 [−0.02, 0.02]; A_k^pred 0.00002; Â_k −0.247 [−0.331, −0.150] |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication (42b testable) | n/a (inconclusive: below resolution) | A_k^pred 0.0038; Â_k −0.038 [−0.200, 0.018] |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication (2 units < 3 days) | descriptive | no unit ≥ 3 days |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication (51a–51l) + native N2 | n/a (inconclusive: below resolution) | A_k^pred 0.003–0.018; pooled Â_k −0.053 [−0.093, −0.012]; P4 ρ −0.20, p 0.81 |
| [NE41](goalperiod-subhypotheses/NE41/README.md) | native N1 (forced erasures, regime III) | descriptive | R_slow 1.06 [0.98, 1.14]; R_fast 1.28 [0.58, 1.98] (untestable) |

The folders G37, G39–G42 and G44 were created after the run (the card's note asked for them before it). Their predictions are the card's registered P1, P3 and P5, copied with that disclosure.

## Results
See Round 1 below.

## Round 1 (2026-10-07)
*Exploratory, non-reserved data only. Code: `scheme/build.py`, `analysis/{h139lib,synthetic,summarize_synthetic,run_units,summarize}.py`. Data: `data/processed/H139-two-rate-variance-split/` (`G37…G51/{statements,reads,calls}.parquet`, `synthetic/`, `results/`; 28 MB before results).*

### Synthetic validation (axis F; run 2026-10-07 08:38–09:44 UTC, before any real-data statistic)
**Design.** Real skeletons: each unit's real statements, producing calls, per-call clock, ledger reads and forced resets. Only the 32-d vectors are synthetic: z = h + s + k + o + D + ε (well 0.25, slow OU 0.2 at γ_s 0.01, statement noise 0.6 per dimension; room drive 0.05 per dimension at 30 min unless stated). Read kicks k: J = 0.044 along a random unit direction per read message (the same direction for every reader of that message), γ_k = 0.15. Own fast innovations o: AR(1) at γ_k. The estimator is the registered one: drive-corrected O1 in 14 lag bins, constrained two-rate WLS with γ_k fixed at the planted value, 200 agent-day bootstrap draws. Detection = Â_k 95% CI above 0.
- Registered units (51c, 51d, 51g, 38a, 38b, 38e, 41): 100 replicates of W0, W1, W1×5, W1×20, Wctx; plus (added here, not registered) Wdrive (R-drive: no fast part, drive 0.2 per dimension at 5 min), Wslow (W1 under a 3-h drive), a ladder L0.1–L3 (W1 plus own fast innovations, total fast amplitude A = 0.1, 0.3, 0.5, 1, 2, 3 in units of |x|²), and Lctx3 (L3 with the whole fast part erased at forced resets).
- Other testable units (51a, 51e, 51f, 51h, 37, 39, 40, 42b; added): 50 replicates of W0, W1 and the ladder, so S1 is checked in every unit with ≥ 3 days.
- Read rate r̄ (ledger, all calls of the unit's agents on their statement days): 0.74–1.20 per call in #51 units, 0.19–0.55 in #37–#42. **A_k^pred = r̄ J² /[1 − (1 − γ_k)²] = 0.0013–0.0084** (in |x|² units; dynamic |x|² ≈ 6–7).

| Rule / prediction | Result (per unit) | Outcome |
| --- | --- | --- |
| (i) / **S1** A_min > 2 A_k^pred | A_min (80% detection) 0.59 (51g) – 2.9 (38b); not reached at A = 3 in 37, 38e, 39, 42b. **A_min / A_k^pred = 92 (51g, 90% CI rule) to > 2,000.** SE of Â_k in W1 0.17 (51g) – 1.17 (38e). | **S1 fires in 15/15 testable units** (95% and 90% CI rules) |
| J needed for testability, J* = √(A_min / (2 r̄ · 3.6)) | 0.31 (51d) – 1.37 (38b); ≥ 7× H130's J_K 0.044 in every unit | — |
| (ii) / **S2** Q_k unbiased ±30% in W1×5, W1×20 | W1×20 bias −108% to +1,116%; W1×5 −1,215% to +4,057% (Monte Carlo SE of the mean Â_k 0.02–0.12 vs true 0.03–0.17). At resolvable amplitudes the estimator is unbiased: L3 bias −11% to +7% (all 15 units), L1 −37% to +10%; 95% coverage 0.74–0.98. | **S2 fails** (bias not resolvable at the registered amplitudes) |
| (iii) false Â_k > 0 in W0 ≤ 0.10 | 0.00–0.08 | passes |
| (iv) / **S3** R_fast separates Wctx (< 0.3) from W1 (> 0.7) in ≥ 80% | Wctx < 0.3: 0.41–0.53; W1 > 0.7: 0.37–0.59. Added check at A = 3: Lctx3 < 0.3 in 0.58–0.89, L3 > 0.7 in 0.55–0.80 (both ≥ 0.8 only in 51g). | **S3 fails** → N1 descriptive |
| R-drive (added) | Strong 5-min drive, no fast part: false Â_k > 0 in 5–27% of replicates (corrected); the raw estimator reads Â_k ≈ 4.4–5.2. | the drive correction removes most, not all, of a fast drive |
| P3 size (added) | f_s ≥ 0.8 in 91–100% of W1 replicates (and of W0) | P3 cannot fail when the fast part is at A_k^pred |
| P5 size (added) | two-rate beats one-rate out of fold in 34–58% of W0 replicates; 84–100% at A ≥ 2 | P5 is a coin flip when the fast part is unresolved |
| Free-rate fit (added) | γ̂_k 0.13–0.19 at A = 2–3 in #51 units (planted 0.15) | recovers γ_k when resolvable |

Data: `synthetic/runs_<unit>.parquet` (15 units, 11,600 replicates), `synthetic/summary.json`.

**Amendment A1 (2026-10-07 14:31 UTC, after the synthetic, before any real-data statistic).**
1. **P1 is untestable (S1 fires in every testable unit).** The resolvable fast amplitude is 92 to > 2,000 times the predicted one. By decision rule (i) the HH382 kill cannot fire, and P1 reports only an upper bound on Â_k (and Q_k). If a unit's Â_k is resolved, the report is the lower bound Q_k ≥ A_min / A_k^pred, as the card says. **By the hypothesis-level rule the verdict is "inconclusive (below resolution)"**, fixed now, before real data.
2. **Shared-week kick inputs.** J_K is re-estimated with H130's read-jump estimator (copied into `h139lib`). γ_kick is not re-estimated in shared weeks; 0.15 (H130's pooled value) is used. S1 stays fired in a shared-week unit unless its J_K ≥ J* (0.65–1.37 there). For #51, H130's per-unit γ_kick (0.07–0.51, all inside [0.03, 1]) and J_K are used, as registered.
3. **P2 is untestable.** Per-agent fits use a subset of the unit's pairs, so the agent-level resolution is coarser than the unit-level one, which is already ≥ 90× too coarse. The registered criterion (Â_k,i > 0 in ≥ 90% of draws) has power near its size at A_k^pred. P2 is not computed.
4. **N1 is untestable and descriptive.** S1 fires in every NE41 unit, and S3 fails. R_fast and R_slow are reported descriptively.
5. **P3 and P5 are non-diagnostic** at this resolution (sizes above). They are computed as registered and labelled non-diagnostic. P4 is computed as registered (its permutation null sizes it).
6. A resolved Â_k on real data is read as "fast variance of some origin", not as R-innovation, unless the room × hour variant agrees: a fast drive leaks into the corrected Â_k in 5–27% of replicates.


### Real data (run 2026-10-07 14:32 UTC, after the commit of the synthetic and A1)
15 testable units (≥ 3 days: 37, 38a, 38b, 38e, 39, 40, 41, 42b, 51a, 51c–51h) plus 11 short units (descriptive). 8 periods, 3 vector variants, 3 autocovariance modes (drive-corrected, raw, room × hour). Data: `results/{units,agents}_G<NN>.parquet`, `inputs_G<NN>.json`, `summary.json`. Figures: `figures/summary_obs_col.pdf`, `figures/synthetic_col.pdf`. Estimates: 475 rows in `per_period_estimates` (`hypothesis == "H139"`).

**Headline.** The test HH382 asks for cannot be done at this data size. The read-driven fast part that H130's kick predicts is A_k^pred = 0.0004–0.019 |x|² units (median 0.0044), 0.01–22% of the dynamic content variance (median 2.5%; A_s + B ≈ 0.09–0.31). The smallest fast amplitude the autocovariance resolves is 7 to > 1,000 times larger in every unit. So the verdict is inconclusive (below resolution), as fixed in A1 before real data. What the data do show (post hoc): no positive fast component above +0.07 in 14/15 units, and a lag-1 dip that the model cannot express.

**Kick inputs.** #51: H130's per-unit J_K (0.043–0.055) and γ_kick (0.07–0.52). #37–#42 (re-estimated, H130's read jump): J_K 0.003 (41) to 0.166 (37); every upper 95% bound (≤ 0.22) lies below the J* needed for testability (0.65–1.49). S1 therefore holds with the real inputs in all 15 units. Read rate r̄: 0.74–1.20 per call (#51), 0.19–0.55 (#37–#42); talk calls only 0.7–1.3 (#51).

**Resolution check on the real noise scale (post hoc).** The synthetic noise level was larger than the real one: the bootstrap SE of Â_k is 0.02–0.07 on real data vs 0.17–1.17 in W1. Scaling A_min by the real SE (A_min ≈ 3.4 SE, from the synthetic) gives A_min = 0.075–0.50 and A_min / A_k^pred = 6.8 (51d) to 9,993 (41). S1 still holds (> 2) in 15/15 units.

| # | Prediction | Result (primary; variants) | Verdict by the rule |
| --- | --- | --- | --- |
| S1 | A_min > 2 A_k^pred in #51 units | fires in 15/15 units (synthetic; real inputs; real noise scale) | **supported** (as predicted) |
| S2 | Q_k unbiased ±30% in W1×5, W1×20 | bias not resolvable (−108% to +4,057%); unbiased at A ≥ 1 | failed |
| S3 | R_fast separates Wctx from W1 in ≥ 80% | 37–59% | failed (N1 descriptive) |
| **P1** (HH, kill) | pooled Q_k in [⅔, 1.5], 90% CI inside [0.5, 2] | **untestable (S1, A1.1).** Bound only: pooled Â_k −0.058 [−0.099, −0.017] (I² 0.72, 15 units); A_k^pred median 0.0044. Per-unit 95% upper bounds ≤ +0.072 except 38e (+0.30). gte −0.041 [−0.081, −0.001]; white32 −0.042 [−0.077, −0.008]; raw +0.024 [−0.005, 0.054]; room × hour −0.006 [−0.046, 0.034]. No unit has Â_k resolved above 0 (primary). | **untestable → inconclusive (below resolution)**; kill cannot fire |
| P2 | slope of ln Â_k,i on ln r̄_i in [0.5, 1.5] | not computed (A1.3) | untestable |
| P3 | f_s ≥ 0.8 in ≥ 2/3 of units | 13/15 (f_s > 1 in 11 units because Â_k < 0) | passes; non-diagnostic (A1.5) |
| P4 | split-unit Spearman of f_s ≥ 0.3, p < 0.05 (#51) | ρ −0.20 [−0.61, 0.27], permutation p 0.81, 23 agents; agent-level f_s unstable (median 0.12, IQR 0.00–0.78) | failed |
| P5 | two-rate beats one-rate out of fold in ≥ 1/2 | 9/15 (W0 size 34–58%) | passes; non-diagnostic (A1.5) |
| N1 (NE41) | R_fast < 0.5 and R_slow ≥ 0.8 | R_fast 1.28 [0.58, 1.98] (pooled; per unit −38 to +3.3); R_slow 1.06 [0.98, 1.14] (I² 0.12) | untestable (S1); descriptive |
| N2 (G51) | #51 replicates P1–P4 | P1, P2 untestable; P3 passes (non-diagnostic); P4 failed. Pooled #51 Â_k −0.053 [−0.093, −0.012], 7 units | n/a (inconclusive) |

**Hypothesis-level verdict (rule fixed in the card and A1): inconclusive (below resolution).** The kill did not fire and could not fire.

**Post hoc findings (labelled; not tests of the card).**
1. **Lag-1 dip.** The own covariance at a 1-call lag is lower than at a 2-call lag in 14/15 units, in all three modes (e.g. 51g raw: 0.22 at τ = 1, 0.24 at τ = 2, 0.29 at τ = 3). Statements on consecutive calls are less alike than statements 2–7 calls apart. A fast part made of decaying kicks (A_k ≥ 0) cannot give this. Candidates: alternation between replies and own-task statements, or producing-call attribution errors at 1-call lags. This is why the constrained Â_k is negative in 7/15 units (CI below 0).
2. **The drive correction cuts short-lag covariance.** Corrected minus raw is −0.10 to −0.15 at lags 1–3 in #51 units, vs about −0.03 at the longest lags: the cross-agent covariance at short wall lags (conversation, H130's pair co-movement) is subtracted from own-agent pairs. The synthetic had no such pair co-movement, so it did not show this bias.
3. **Slow part.** In #51 the fitted slow rate is γ_s 0.0075–0.023 per call (median 0.013), close to H130's γ_auto 0.0094. The slow part survives forced erasures (R_slow 1.06), as H130's R_C 1.03 did.
4. **Fast-share scale.** The predicted fast share is 1.1–8.1% of the dynamic variance in #51 units (0.01–22% over all 15) (not 0.2% per read, as the card's estimate from H130's rounded numbers said): the dynamic content variance (A_s + B ≈ 0.2) is far smaller than the synthetic assumed (6.4).

### Impostors (round 1)
| Impostor | Status | Note |
| --- | --- | --- |
| Scheduler field | removed | per-call clock; within-day lags only |
| Exogenous field | partly | drive correction leaves 5–27% false Â_k > 0 under a 5-min drive (synthetic); it over-subtracts conversation at short wall lags on real data (post hoc) |
| Shared model priors | removed | style_resid, leave-day-out wells; gte and white32 agree in sign |
| Contemporaneous convergence | partly (moot) | kick inputs are read-minus-in-flight; P1, which it protects, is untestable |

**Scorecard (round 1):** A1 B1 C0 D0 E1 F1 G0 H0 I0 (table above).

**Claim that stands:** in regime-III units (#37–#42 and #51; 15 units with ≥ 3 days), the fast content variance that H130's read kick predicts (A_k^pred median 0.0044 |x|² units, median 2.5% of the dynamic variance) lies 7 to > 1,000 times below the smallest fast amplitude the own autocovariance resolves, so HH382's variance-split test is untestable at this data size. Exclusions: P1 and P2 (untestable; verdict inconclusive), N1 (untestable; R_fast descriptive), P3 and P5 (pass but non-diagnostic), P4 (failed; agent-level shares unstable), the negative Â_k and the lag-1 dip (post hoc), R_slow 1.06 (descriptive).

### Round 2 redirects
- **What the direction is really after:** how much of an agent's moment-to-moment content is the echo of what it read.
- **H139-R1. Measure the echo where it is large.** Use H130's dose design (projection on the sender direction) instead of the total autocovariance: it isolates the read channel and has the power the variance split lacks.
- **H139-R2. The lag-1 dip.** Split τ = 1 pairs by call kind (talk vs work), by reply status (DQ2) and by producing-call confidence, to tell alternation from attribution error.
- **H139-R3. Drive correction without conversation.** Subtract the cross-agent covariance only from pairs of agents that did not read each other in the window (an unread-partner correction), and re-run the synthetic with pair co-movement planted.
- **H139-R4. Calibrate the synthetic noise scale** to the real |x|² and dynamic variance before any new power claim.

## Notes
- 2026-10-07 09:15 UTC: card written from HH382 (approved by Vivian 2026-10-07).
- 2026-10-07 08:38–09:44 UTC (system clock UTC): synthetic validation on 15 real skeletons. An API session limit then paused the work; on resume the on-disk outputs were checked and nothing was re-run.
- 2026-10-07 14:31 UTC: Amendment A1 written; 14:32 UTC: scheme, code, synthetic and A1 committed (84664aa) before any real-data statistic. 14:32 UTC: real-data run. A dry run on random vectors tested the pipeline first.
- The HH says the slow part "matches the H46/H73 agent constant". H46 and H73 measure *style* (17-d text features), not content. H139 tests the content analog: whether the slow share is an agent constant (P4). The style numbers are not used as a target.
- The HH's "variance at lags of 1 call or less" is sharpened to the fitted fast component A_k: at lag 1 the slow part still holds most of the covariance, so a lag-1 cut would mix the two.
- **Risk flagged before data:** by H130's rounded numbers the predicted fast share is ≈ 0.2% of dynamic content variance per read per call. If the synthetic shows this is below resolution (S1), HH382's numeric test is untestable at this data size, and only an upper or lower bound is reported.
- **Proposed DEFINITIONS.md variants (H139):** *read rate per call r̄ (H139)* = mean count of other agents' chat items newly entering an agent's context per call (DQ1 ledger, kind `agent`); *fast and slow amplitudes A_k, A_s (H139)* = amplitudes of the two exponentials in the drive-corrected own autocovariance on the call clock; *predicted fast amplitude A_k^pred (H139, shot-noise form)* = r̄ ⟨J²⟩ / [1 − (1 − γ_k)²]; *fast share f_k (H139)* = A_k / (A_k + A_s + B); *erasure ratio of the fast part R_fast (H139)* = lag-1–7 covariance above the slow fit across a forced reset over the same within a segment.
