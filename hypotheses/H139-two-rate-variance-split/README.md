# H139: A fast read kick on a slow private well predicts how content variance splits between the two

**Status:** pre-registered (not run). Card, observables, nulls and predictions written 2026-10-07 09:15–10:00 UTC, before any H139 statistic on real data. No scheme, synthetic or analysis code has run.
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
| Scheduler field | partly | Content statistics on the per-call clock (H40); lags only within a PT day, so nights and day edges never enter a lag. | removed (planned) |
| Exogenous field (kickoff, goal, operator) | yes (the HH's impostor) | Drive correction as in H130 A1: the agent's own autocovariance minus the cross-agent covariance at the same wall lag (a common topic drift is shared by all agents). Variant: room × hour means subtracted first (the HH's wording). Wells (leave-day-out) remove static fields. | removed (planned) |
| Shared model priors (family, style) | yes | `style_resid_period` vectors; wells absorb each agent's prior; `white32` and gte variants. | removed (planned) |
| Contemporaneous convergence | yes | The kick inputs (J_K, γ_kick) come from H130's read-minus-in-flight estimators, so convergence is not counted as a kick. The autocovariance side is own-agent only; the drive correction removes shared time-local fields. | removed (planned) |

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
**Reserved periods used for confirmation:** none (not run). Planned: the #51 tail (2026-09-07 → 09-21) and #45–#47, ledger families `kick_response` and `content_alignment`. Overlaps to disclose: H130 (#51 tail, same families), H54, H97, H100, H102, H107, H108, H109 on #45–#47 content. A frozen, guarded confirm script is written only after exploration and runs only with Vivian's sign-off.

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
| [G38](goalperiod-subhypotheses/G38/README.md) | replication (transfer to a shared-goal week) | pending | — |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication (51a–51l) + native N2 | pending | — |
| [NE41](goalperiod-subhypotheses/NE41/README.md) | native N1 (forced erasures, regime III) | pending | — |

Other testable units (#39–#42, #44) get their period folders, with the replication predictions copied and dated, before the run.

## Results
Not run.

## Notes
- 2026-10-07 09:15 UTC: card written from HH382 (approved by Vivian 2026-10-07).
- The HH says the slow part "matches the H46/H73 agent constant". H46 and H73 measure *style* (17-d text features), not content. H139 tests the content analog: whether the slow share is an agent constant (P4). The style numbers are not used as a target.
- The HH's "variance at lags of 1 call or less" is sharpened to the fitted fast component A_k: at lag 1 the slow part still holds most of the covariance, so a lag-1 cut would mix the two.
- **Risk flagged before data:** by H130's rounded numbers the predicted fast share is ≈ 0.2% of dynamic content variance per read per call. If the synthetic shows this is below resolution (S1), HH382's numeric test is untestable at this data size, and only an upper or lower bound is reported.
- **Proposed DEFINITIONS.md variants (H139):** *read rate per call r̄ (H139)* = mean count of other agents' chat items newly entering an agent's context per call (DQ1 ledger, kind `agent`); *fast and slow amplitudes A_k, A_s (H139)* = amplitudes of the two exponentials in the drive-corrected own autocovariance on the call clock; *predicted fast amplitude A_k^pred (H139, shot-noise form)* = r̄ ⟨J²⟩ / [1 − (1 − γ_k)²]; *fast share f_k (H139)* = A_k / (A_k + A_s + B); *erasure ratio of the fast part R_fast (H139)* = lag-1–7 covariance above the slow fit across a forced reset over the same within a segment.
