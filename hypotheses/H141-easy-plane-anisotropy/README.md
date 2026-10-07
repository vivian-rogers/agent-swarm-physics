# H141: Content moves on an easy plane set by the goal and room texts: slow along it, fast across it

**Status:** pre-registered (not run). Card, observables, nulls and predictions written 2026-10-07 10:55–11:40 UTC, before any H141 statistic on real data. No scheme, synthetic or analysis code has run.
**Question (GOALS.md):** **Q2** (what is field and what is coupling: do the operator's goal and room texts set the directions in which agent content is soft and slow, an anisotropic well?). Second: **Q3** (are the slow directions of content set by fields, or are they content's own collective modes?).
**Fields:** stat mech (anisotropic Langevin relaxation, easy-plane and hard-axis anisotropy in vector spins, fluctuation–dissipation), dynamics (mode lifetimes)
**Literature:** none in `literature/` covers anisotropic OU processes. Cited from memory (†): Uhlenbeck & Ornstein, *Phys. Rev.* 36, 823 (1930)† (vector OU with a stiffness matrix); Chaikin & Lubensky, *Principles of Condensed Matter Physics* (1995)† (easy-plane anisotropy; soft modes). Model references: [`physics-models/16-langevin-relaxation/README.md`](../../physics-models/16-langevin-relaxation/README.md) (vector form ẋ = −Γ(x − c) + ξ), [`physics-models/11-vector-spins/README.md`](../../physics-models/11-vector-spins/README.md) (anisotropy; "transverse, and Goldstone physics"), [`physics-models/17-collective-modes/README.md`](../../physics-models/17-collective-modes/README.md) (dynamic modes as eigenmodes of Γ; content uses about 5–12 of 32 whitened dimensions).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime (III only); Driving / external field (goal text, kickoff, room kickoffs, #51 private goals); Agent state, **variant vector** (32-d whitened statement vectors, `style_resid_period`); H01's **goal field ĝ** (per-room and per-agent versions); H54's **quench target (kickoff)**; H40's **call clock**; **Interaction (ledger-visible exposure)** (RE-D1) and H67's **in-flight placebo (matched-lag)** (kick part). Used as defined in their cards: H130's *private well centre h_i (leave-day-out)*, *well relaxation rate γ_auto (drive-corrected)* and *sender-specific kick decay γ_kick*; H108's *room direction m̂(d)* and *direction persistence P(ℓ)*; H97's *kickoff memory* split along k̂ and transverse. **New named variants proposed for DEFINITIONS.md** (not edited there; defined under Observables): **text plane E (H141)**, **subspace autocorrelation C_P(τ) (H141)**, **anisotropy ratio ρ_A (H141)**, **subspace variance ratio V_A (H141)**, **random-plane band (H141)**.
**From:** HH384 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/16-langevin-relaxation/` (primary: anisotropic well with stiffness matrix Γ), `physics-models/11-vector-spins/` (easy-plane anisotropy), `physics-models/17-collective-modes/` (benchmark: data-defined slow modes)
**Data inputs (shared tables first):** DQ5 `embeddings/statements.parquet` with `statements_{style_resid_period32,white32}_{bge_small,gte_modernbert}.npy`; `statement_flags`; `embeddings/goals.parquet` + `goal_vectors{,_gte_modernbert}.npy` (kinds goal, kickoff, kickoff_room, agent_goal) whitened per regime and model; `chat_core`; `producing_calls`; DQ1 `call_windows`, `context_ledger_items`, `context_ledger_turns`; `rooms_timeline` (null `t_end` → +∞); `period_units`, `calendar`, `roster`; DQ6 `ground_truth_labels` (#51 roles, NE38 date). No text is read.

## Source HH (verbatim from the HH list)
- **HH384 · Content moves on an easy plane: fluctuations across it are fast white noise, fluctuations along it are slow.** If the goal and room axes define a low-dimensional easy plane, a vector spin with anisotropy relaxes slowly along the plane and fast across it.
  - *Prediction:* the autocorrelation time of content projected on the goal+room plane is ≥ 10 times the time across it. Read kicks across the plane decay within one call.
  - *Check:* per-period goal and room axes (H54, H100); content embeddings per call; autocorrelation by projection.
  - *Kill:* the two autocorrelation times are within ×3.
  - *Impostors:* a plane defined from the same data overfits slow directions. Define the axes from kickoff and room texts only, not from agent content.
  - *Models:* 11, 16 (proposed Langevin) · *Builds on:* H108, H97, H130, H100

## Standards (STANDARDS.md)
**Question served:** Q2 (second: Q3).

| Impostor | Relevant? | How it is handled (planned) | Status |
| --- | --- | --- | --- |
| Scheduler field | partly | Per-call clock (H40); lags only within a PT day for the call-scale test; the day-scale test uses noise-corrected day-to-day persistence of agent-day means (H108's method), which has no within-day timing. | removed (planned) |
| Exogenous field (kickoff, goal, operator) | yes (central) | The plane is the field. The HH's impostor (a plane fit to the same data) is removed by building E from goal, kickoff and room-kickoff texts only. A common goal-phase drift along E would fake slowness, so the primary autocovariance subtracts the cross-agent covariance at the same wall lag (H130 A1 point 3); the raw version is a variant. | removed (planned) |
| Shared model priors (family, style) | yes | `style_resid_period` vectors; wells (leave-day-out) absorb each agent's prior; `white32` and gte variants. | removed (planned) |
| Contemporaneous convergence | partly | Only the kick part (P4) is an influence claim; it uses H130's read-minus-in-flight design at matched posting age. The autocorrelation part is own-agent only. | removed (planned) |

**Inputs:** current tables only (DQ5 vectors in both models, shared goal vectors, DQ1 ledger).

**Two layers:**
- *Replication* (role `replication`): O1–O4 on every non-reserved regime-III unit with ≥ 3 days and ≥ 4 agents: units of #37, #38, #39, #40, #41, #42, #44, with E = the period's text plane; and 51a–51l with each agent's own plane.
- *Natives* (role `native`): **G38** and **G44** (room-specific kickoffs give a third and fourth text axis; H108 measured the data room direction there), **G51** (each agent has its own private goal text, so each agent has its own plane), **NE38** (2026-07-29: a human reassigns Claude Opus 5's role, so that agent's plane rotates at a dated step). Each has a dated prediction in its folder.

**Unit-of-analysis exceptions (named):** (a) **shared instrument**: the regime-III whitener and the shared goal vectors are common rulers. (b) **agent-level property**: wells h_i are leave-day-out within a period. (d) short units enter only through a random-effects pool, reported next to per-unit values.

**Regimes I and II are not used:** chat-mode calls post few statements per call, so the call-scale autocorrelation is not comparable; declared before any statistic.

## Question
Is an agent's content soft and slow along the directions the operator's texts name (the goal, the kickoff, the room kickoffs, the agent's own goal) and stiff and fast across them? HH384 puts the ratio of autocorrelation times at ≥ 10. The strongest prior evidence points the other way: H97 found the kickoff erases content 2–3× more along k̂ than across it, which is a hard axis, not an easy one.

**Practical payoff:** if content is slow along the goal plane, an operator's goal text sets what persists in agent output, and off-goal content is transient. If the goal axis is a hard axis (H97), the goal text is quickly obeyed and then left alone, and persistence lives elsewhere.

## Model
**From:** `physics-models/16-langevin-relaxation/` (vector form) with the anisotropy language of `physics-models/11-vector-spins/`.

**H141 variant: an anisotropic OU well on the call clock.** Agent i's content deviation from its well, x_i(n) = z − h_i, follows

  x(n+1) = (I − Γ) x(n) + kicks + ξ(n),  Γ = γ_∥ P_E + γ_⊥ (I − P_E),

with P_E the projector on the text plane E and ξ isotropic noise. **Easy plane:** γ_∥ ≪ γ_⊥. HH384: γ_⊥ / γ_∥ ≥ 10.

**Consequences (unfitted relations).**
1. Per-dimension autocorrelation along E decays at γ_∥, across E at γ_⊥.
2. **Fluctuation–dissipation:** with isotropic noise, the stationary variance per dimension is D/γ, so the variance ratio V_A = σ²_∥/σ²_⊥ equals the rate ratio ρ_A = γ_⊥/γ_∥.
3. A read kick decays at the rate of the subspace it lands in: the across-plane part of a kick decays within about 1/γ_⊥ calls.

**Prior arithmetic (stated before data).** In #51 the agent's own content memory over all 32 dimensions is about 100 calls (H130: γ_auto 0.0094). If most variance lies across E, then ρ_A ≥ 10 needs along-plane memory ≥ ~1,000 calls, longer than a median #51 agent-day (761 calls). So the call-scale fit may show the along-plane part only as a within-day plateau. The design adds a day-scale test (O3) for that case.

**Rivals (named):**
- **R-hard-axis (H97):** the goal direction is stiff. Along k̂ the kickoff erases 0.63 of the position vs 0.25 transverse (scale-free Δρ, all variants). Predicts ρ_A < 1.
- **R-iso (the HH's kill):** ρ_A within [⅓, 3].
- **R-modes (model 17):** content fluctuates in about 5–12 of 32 whitened dimensions (H20, quoted in model 17). The slow directions are content's own principal modes, and the text plane is no slower than a random plane of the same dimension once those modes are counted.
- **R-drive:** content is slow along E only because the whole swarm drifts through goal phases (a common field); the drive correction removes it.
- **R-text-room (H100):** the room-kickoff texts do not point where the rooms differ (field share #38 0.18 vs null 0.16; #44 0.08 vs 0.03), so a text room axis is no slower than a random axis, while the data room direction is slow (H108: P(1) 0.95 in #38).

## Data scheme (`scheme/`)
`scheme/build.py --period G<NN>` writes `data/processed/H141-easy-plane-anisotropy/G<NN>/` from shared tables only (codes, row ids and projected coordinates; no text). Reserved days and periods are dropped with `calendar` flags and the shared reserved-data mask (`infra/shared/common.py`). Budget ≤ 100 MB.
- **Statements, call clock, wells, reads:** as H130's scheme (agent chat statements, exact self-repeats and fallback calls dropped; per-agent call index n per PT day; leave-day-out wells; ledger reads of kind `agent`).
- **Text plane E (H141):** the Gram–Schmidt basis of the period's whitened goal-text vector and kickoff vector (`goals.parquet` kinds goal and kickoff), plus the room-kickoff vectors where they exist (#38, #44). d_E = 2 (most periods) to 4 (#38, #44). In #51 each agent's plane is its private goal vector (kind `agent_goal`, the role in force on the statement's day) plus the village goal vector (d_E = 2). Built from texts only, before any statement enters.
- **Variants of the plane:** k̂ only (d = 1); E plus H108's data room direction m̂ cross-fitted on other days (leave-day-out); the room-kickoff difference axis alone.
- **Benchmarks:** 200 random d_E-dimensional planes per unit (Haar draws in the 32-d whitened space) give the **random-plane band**; the top-d_E principal subspace of the unit's content deviations, cross-fitted on other days, gives the R-modes benchmark.
- **Output:** `G<NN>/statements.parquet` (agent, day, n, row id, room, reset counters), `G<NN>/planes.npz` (bases), `G<NN>/reads.parquet`, `_provenance.json`; `results/`, `synthetic/`.
- **Regimes covered:** III only.

## Observables
*Specified 2026-10-07 10:55–11:40 UTC, before any H141 statistic.* Primary: `style_resid_period` × bge_small; variants `white32` and gte_modernbert. Unnormalized dot products.
- **O1 subspace autocorrelation (call scale).** For a subspace with projector P and dimension d_P: C_P(τ) = mean ⟨P x_B, P x_B′⟩ / d_P over same-agent, same-day statement pairs at call lag τ ≥ 1 (bins as H130: 1–3, 4–7, 8–15, 16–31, 32–63, 64–127, 128–255, 256–511). Drive-corrected (primary): minus the cross-agent covariance at the same wall lag, per subspace. Fit A_P e^{−γ_P τ} + B_P (weighted NLS; agent-day block bootstrap, 200 draws, the same draws for all subspaces).
- **O2 anisotropy ratio ρ_A = γ_⊥ / γ_∥** (E vs its complement), per unit, with a random-effects pool of ln ρ_A over units. Also the plateau shares B_P/(A_P + B_P).
- **O3 day-scale persistence.** Noise-corrected day-to-day persistence of agent-day mean projections per subspace (H108's split-half correction, applied per dimension and averaged): P_∥(1) vs P_⊥(1). Slow along E means P_∥(1) > P_⊥(1).
- **O4 variance ratio V_A** = (E|P_E x|²/d_E) / (E|(I − P_E) x|²/(32 − d_E)), the unfitted partner of ρ_A.
- **O5 kick by subspace (HH's second clause).** H130's sender-specific distributed lag (A1 point 2) with the response projected on E and on its complement, lag bins {0, 1, 2–3, 4–7, 8–15}. Across-plane decay: the lag-1 coefficient over the lag-0 coefficient.
- **O6 random-plane percentile** of each unit's ρ_A and P_∥(1) − P_⊥(1); R-modes benchmark ρ_A of the cross-fitted principal subspace.

**Estimates rows** (`per_period_estimates`, hypothesis H141): `h141_anisotropy_rhoA`, `h141_variance_ratio_VA`, `h141_day_persistence_par`, `h141_day_persistence_perp`, `h141_random_plane_pct`, `h141_kick_lag1_ratio_perp`, per unit and model.

## Null / baseline
- **N0 isotropy:** ρ_A = 1 (ln ρ_A = 0).
- **N1 random-plane band:** the distribution of ρ_A, V_A and P_∥ − P_⊥ over 200 random planes of the same dimension in the same unit. It removes the effect of content's low dimension on any fixed plane.
- **N2 cross-day surrogate** for O1 (pairs re-matched across days at the same call lag): checks the drive correction.
- **N3 synthetic worlds** (below).

## Synthetic validation plan (axis F; runs before any real-data statistic)
Worlds keep the real statements, call clock, reads and resets of units 51c and 51g and of #38 and #41; content is synthetic, calibrated to H130 A1's per-dimension scales (statement noise 0.6, well 0.25, OU state 0.2) and to a low-rank content covariance with 8 active dimensions. 100 replicates per world.
- **W-easy (HH384):** γ_∥ = 0.001, γ_⊥ = 0.01 per call along the real text plane.
- **W-iso:** γ = 0.01 everywhere.
- **W-hard (H97):** γ_∥ = 0.03, γ_⊥ = 0.01.
- **W-modes:** slow along 3 random active directions not aligned with E; isotropic elsewhere.
- **W-drive:** isotropic agents plus a common goal-phase drift along E (time scale 1–6 h).
- **Decision rules fixed now:** O2 must place ln ρ_A within ±0.5 of truth in W-easy, W-iso and W-hard; the drive-corrected O2 must keep W-drive's ρ_A within [⅓, 3] in ≥ 90% of replicates; the random-plane percentile must not exceed 0.95 in W-modes in more than 10% of replicates. If γ_∥ = 0.001 is not resolved on the call clock (along-plane memory beyond a day), O3 becomes the primary test of the along-plane slowness, as a dated amendment before real data.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R-hard-axis (H97), R-iso, R-modes (model 17), R-drive, R-text-room (H100).
**Reserved periods used for confirmation:** none (not run). Planned: the reserved weeks #45–#47 (shared goals; #45 has room-level structure through NE19) and the #51 tail, ledger family `content_alignment`. Overlaps to disclose: H97 and H54 on reserved kickoffs; H100, H102, H107, H108, H109 on #45–#48 content; H130 on the #51 tail. A frozen, guarded confirm script is written only after exploration and runs only with Vivian's sign-off.

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
*Written 2026-10-07 10:55–11:40 UTC, before running the analysis on real data.*

**What I had seen when writing this:** H97 (extra forgetting at kickoffs Δρ +0.26 ± 0.04 over 18 kickoffs; along k̂ 0.63 vs transverse 0.25 in the scale-free estimator; IV isotropy passes only in the raw variant); H108 (noise-corrected day-to-day persistence of the room direction 0.69–0.95 in 6/8 periods; #38 P(1) 0.95 with P(ℓ) ≈ 0.85 out to six days; #44 0.78); H100 (room-kickoff text directions carry a chance share of the room separation: #38 0.18 vs null 0.16, #44 0.08 vs 0.03; the room difference is mostly spontaneous, f_spont 0.58–0.91); H130 (#51 own memory ≈ 100 calls, kick ≈ 7 calls, median 761 calls per agent-day); H54 (#51 agents sit on their own goal text, role-swap accuracy 0.95; NE38 DiD +0.61 [0.56, 0.66] within a day); model 17's note that content uses about 5–12 of 32 whitened dimensions. **Not seen:** any projection of statements on the text planes, any subspace autocorrelation and any variance ratio.

**Synthetic (axis F).**

| # | Prediction | Counts against |
| --- | --- | --- |
| S1 | O2 recovers ln ρ_A within ±0.5 in W-easy, W-iso, W-hard | bias > 0.5 |
| S2 | Without the drive correction, W-drive gives ρ_A > 3 in > 50% of replicates; with it, < 10% | correction fails |
| S3 | The random-plane percentile controls W-modes (false > 0.95 in ≤ 10%) | > 10% |

**Replication layer.**

| # | Prediction [credence] | Counts against |
| --- | --- | --- |
| **P1** (primary, HH) | **Easy plane.** Pooled ρ_A ≥ 10 with the lower 90% bound ≥ 3 [0.1] | pooled ρ_A 90% CI inside [⅓, 3] (**kill**) |
| P2 | **The texts matter.** The text plane's ρ_A is above the random-plane 95th percentile in ≥ 1/2 of testable units [0.25] | ≤ 1/4 of units |
| P3 | **Fluctuation–dissipation.** V_A within ×2 of ρ̂_A in ≥ 1/2 of units [0.3] | outside ×2 in > 1/2 |
| P4 (HH second clause) | **Fast kicks across the plane.** The across-plane kick coefficient at lag 1 is ≤ ¼ of its lag-0 value (pooled CI), and the along-plane kick decays more slowly [0.2] | across-plane lag-1 ratio ≥ ½ |
| P5 | **Day scale.** P_∥(1) > P_⊥(1) with CI in ≥ 1/2 of units [0.4] | P_∥(1) ≤ P_⊥(1) in > 1/2 |

**Native layer** (each repeated in its folder).

| # | Unit | Prediction [credence] | Counts against |
| --- | --- | --- | --- |
| N1 | G38, G44 | The text room axis is **not** slower than random (R-text-room, below the 90th percentile), while the cross-fitted data room direction m̂ is (above the 95th percentile, ρ_A(m̂) ≥ 3) [0.45] | text room axis above the 95th percentile |
| N2 | G51 | Each agent's own goal plane is slow: pooled over agents and units, ρ_A ≥ 3 and above the random-plane 95th percentile [0.25] | pooled ρ_A within [⅓, 3] |
| N3 | NE38 | Claude Opus 5's slow direction rotates with its role: after 07-29 the day-scale persistence along the new goal axis exceeds that along the old one, and before 07-29 the reverse (one agent: descriptive) [0.3] | no change in the order |

**Kill rule (HH384).** The kill fires if the pooled ρ_A 90% CI lies inside [⅓, 3] (the two times within ×3). **Reverse kill (R-hard-axis):** pooled ρ_A < ⅓ with the upper 90% bound < 1: the text plane is a hard plane.

**Hypothesis-level verdict rule.** *Supported* if P1 and P2 pass. *Narrowed* ("content has slow directions, but they are content's own modes, not the text plane") if pooled ρ_A ≥ 3 for the cross-fitted principal subspace while P2 fails. *Failed* if the kill or the reverse kill fires. *Inconclusive* otherwise.

**My credence before data:** supported 0.1; narrowed 0.25; failed 0.4 (of which reverse kill 0.15); inconclusive 0.25.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication + native N1 (room-kickoff axes) | pending | — |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication + native N1 (room-kickoff axes) | pending | — |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication (51a–51l) + native N2 (per-agent planes) | pending | — |
| [NE38](goalperiod-subhypotheses/NE38/README.md) | native N3 (one agent's plane rotates) | pending | — |

Other testable units (#37, #39–#42) get their period folders, with the replication predictions copied and dated, before the run.

## Results
Not run.

## Notes
- 2026-10-07 10:55 UTC: card written from HH384 (approved by Vivian 2026-10-07).
- HH384 also relates to model 17: E is a field-defined candidate for the slow eigenmodes of Γ; the cross-fitted principal subspace is the data-defined one.
- The HH's "fast white noise" across the plane is not testable at lag 0 (statement noise enters only there); P4 tests the kick part, O1 the lag ≥ 1 part.
- **Proposed DEFINITIONS.md variants (H141):** *text plane E (H141)* = Gram–Schmidt span of the period's whitened goal-text and kickoff vectors (plus room-kickoff vectors where they exist; in #51, the agent's goal vector plus the village goal), built from texts only; *subspace autocorrelation C_P(τ) (H141)* = per-dimension own autocovariance of content projected by P on the call clock, drive-corrected; *anisotropy ratio ρ_A (H141)* = γ_⊥ / γ_∥ from C_P fits; *subspace variance ratio V_A (H141)* = per-dimension content variance along E over across E; *random-plane band (H141)* = the distribution of a subspace statistic over Haar-random planes of the same dimension in the same unit.
