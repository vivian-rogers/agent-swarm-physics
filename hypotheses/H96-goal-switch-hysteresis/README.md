# H96: Goal switches show hysteresis: a coercive field

**Status:** exploratory round 1 **done (2026-10-04): a goal switch is a quench, not a hysteresis loop; the order-dependent coercivity is inconclusive (power 0.50) and points the wrong way.**
- **Quench (P1, supported, both models).** On day 1 the old state's field-orthogonal remanence is R₁ = 0.27 (bge) / 0.18 (gte) of its pre-switch level, against 0.85–0.89 across an ordinary night (146 pseudo-switches): ΔR₁ −0.62 [−0.78, −0.45] / −0.72 [−0.88, −0.56], below the night reference in 20/23 / 21/24 transitions.
- **Order dependence (P2′, inconclusive).** ρ(q, ln τ_sw) = −0.75 / −0.52 over the 12 transitions with a measurable residual (HH123 predicts > +0.29). Synthetic power 0.50 at a doubling over the IQR, so the negative is not a refutation.
- **Natives:** NE38 (single-agent reassignment) quenches faster than all 22 same-day placebos (as predicted); G39 mixed (room memory survives at 0.15–0.26 of its pre level; the more ordered room keeps less, carried by agents who moved rooms).
- Card, predictions and synthetic came first; Amendment 1 (τ_sw) after the synthetic, before real data. `confirm.py` written, dry-run on stand-ins, **not run**. Scorecard A1 B1 C2 D1 E1 F1 G1 H1 I1.
**Question (GOALS.md):** **Q2** (what is field and what is coupling at a goal boundary: a quench that erases the old state, or a lag set by the old state's order) and **Q3** (hysteresis is a collective-order signature beyond fields). Q5 second: whether to "clear" a swarm before reassigning it.
**Fields:** stat mech (vector spins, hysteresis, coercivity), dynamics (relaxation after a field step)
**Literature:** none in `literature/` covers hysteresis or coercivity in social systems. Background from memory: Sethna et al., return-point memory and hysteresis in the random-field Ising model (PRL 70, 3347, 1993)†; Bertotti, *Hysteresis in Magnetism* (1998)†.
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent (Claude Code agent 19 and fine-tuned leaders 28, 30 excluded); Regime (whitening per regime; every transition lies inside one regime); Driving / external field (kickoff, goal text, room kickoffs, #51 `agent_goal`); Agent state, variant *vector*, in H01's named form **agent state (vector), whitened statement mean** (DQ5 `style_resid32`); H54's **quench target (kickoff)** and **quench depth**; H20's **active-day clock**. New named variants proposed for DEFINITIONS.md (defined under Observables): **old-state direction ê_old**, **field-orthogonal remanence M_exc**, **persistence ratio R₁**, **inertia time τ_old**, **old-state order q**, **pseudo-switch (ordinary day boundary)**.
**From:** HH123 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/11-vector-spins/` (primary: O(32) content spins under a stepped field), `physics-models/15-stochastic-thermodynamics-selection/` (tool: H75's instant-freeze vs field-limited re-allocation as the rival reading of the switch speed)
**Data inputs (shared tables first):** DQ5 `embeddings/statements.parquet` + `statements_{style_resid32,white32,style_resid_period32}_{bge_small,gte_modernbert}.npy`; shared `embeddings/goals.parquet` + `goal_vectors[_gte_modernbert].npy` (`goal_fields`); `whitening_*` (via `embed_models.load_whitener`); `calendar`; `roster`; `ground_truth_labels` (DQ6: #38/#39 room assignments, #51 roles); `holdout_mask`.
**Relation to H82 (running in parallel, no outputs yet when this card was written):** H82 asks *whether* the previous centroid has a day-1 regression coefficient γ beyond the exogenous and prior fields. H96 asks *how long* the old state survives after the switch (inertia time on the active-hour clock) and whether that time grows with the old state's order. No H82 code or data is used.

## Source HH (verbatim from the HH list, including refinements)
Goal switches show hysteresis: a measurable coercive field. After a goal change, alignment with the *old* goal decays with a lag that grows with how ordered the old state was (H20 saw settling within ~4 days). That gives a coercive field and an inertia time. Practical: whether to "clear" a swarm before reassigning it. *Check:* old-goal alignment decay vs prior order across non-holdout transitions.
  *Models:* 01 (hysteresis), 11 · *Periods:* goal transitions (NE34)

## Question
After a goal change, how long does the swarm's content stay aligned with the state it had at the end of the old goal, beyond the new field? Does that inertia time grow with how ordered the old state was, as coercivity in a magnet grows with domain order?

## Design: two layers (Vivian, 2026-10-04)
- **Replication** (role `replication`): the common estimator at every eligible transition P−1 → P (both non-holdout, one regime). The row belongs to the new period P (`G<P>` folder). The transition is the object (named exception (c)); each transition is fitted on its own. Order dependence is a comparison of per-transition parameters across transitions (phase-diagram comparison, no pooled fit).
- **Natives** (role `native`): **G39** (two #38 rooms with different old states meet one new field: the cleanest within-transition contrast of old order) and **NE38** (G51, 2026-07-29: one agent's role is reassigned while 20+ others keep theirs: a single-spin field step with a same-day placebo).

## Model
**From:** `physics-models/11-vector-spins/`. Each agent i is a unit vector s_i ∈ S^{31} (style-residualized, regime-whitened statement mean). Up to the kickoff time t₀ the field is h_{P−1}; after t₀ it is h_P. The old state is the swarm direction ê_old at the end of P−1. The new field spans F_P = span{k̂_P, ĝ_P, room kickoffs of P}.

  M_old(t) = ⟨ s_i(t) · P⊥_F ê_old^{(−i)} ⟩_i − median_Q ⟨ s_i(t) · P⊥_F ê_Q ⟩_i ,    M_old(t) ≈ M_pre · exp(−h(t)/τ_old)

- P⊥_F projects out the new field, so a new kickoff that resembles the old state does not count as remanence.
- ê_Q are placebo old states (late centroids of non-adjacent periods of the same regime): they remove generic village content.
- h(t) is active hours since t₀ (calendar activity windows).
- **Hysteresis (HH123):** τ_old is finite but long, and grows with the old state's order q_{P−1}, like a coercive field that grows with domain order: log τ_old = a + b·q, b > 0.
- **Quench (rival R1, H54/H10/H75):** the new field erases the old state within the first active hours, faster than an ordinary night erases a day's state; τ_old is short and does not depend on q.
- **Ordinary drift (rival R2, H20):** the old state decays at a switch exactly as it does at an ordinary day boundary inside a period. The switch adds nothing; any "lag" is the period's normal content drift.
- **Themed runs (rival R3):** consecutive goals share topics; removed by P⊥_F and by placebo old states.
- **Composition (rival R4):** the same agents write alike before and after; reduced by the leave-agent-out old state and style residualization; the placebo old states share the composition only partly, so it remains a named residual risk.

**Coercive field (descriptive).** In a magnet, the coercive field is the reverse field at which the old magnetization vanishes. Here the new field is not antiparallel to the old state, so H96 reports a proxy: the new-kickoff quench depth A_K reached at h = τ_old (H54's decoy-corrected alignment with k̂_P).

## Data scheme (`scheme/`)
Script: `scheme/build.py` (shared tables only; no text read or written; holdout rows dropped with `common.holdout_mask` and asserted).
- **Inputs:** listed above.
- **Transform:**
  1. Statements of eligible agents (not 19, 28, 30), non-holdout, with their 32-d vectors (both models; variants style_resid32 [primary], white32, style_resid_period32), unit-normalized.
  2. Transitions (P−1, P): consecutive goal numbers, both non-holdout, both in one regime over the windows used; #23 excluded entirely (H10 keeps #23 blind for its confirmatory #22 → #23 pair; H54 did the same). Kickoff time t₀ = `goals.parquet` kickoff `win_start` (the calendar start of P's first day where P has no kickoff).
  3. Old-state window: P−1's last active day L is the **pre** window (plus any statements of P's first day before t₀). The old-state direction ê_old is built from days L−3 … L−1 (up to 3 days; ≥ 1), so the pre level is out of sample in time. Agent-day vectors: unit mean of ≥ 3 statements. ê_old^{(−i)} = unit mean of the other agents' agent-day vectors.
  4. Post bins on the active-hour clock h since t₀: [0, 0.5), [0.5, 1), [1, 2), [2, 4), [4, 8), [8, 16), [16, 32) h, within P's first 3 active days. Agent-bin vector: unit mean of ≥ 2 statements. "Day 1" = all of the agent's post-t₀ statements on P's first active day.
  5. Field span F_P: shared kickoff, goal text and room kickoffs of P, whitened with the same model's regime whitener, orthonormalized.
  6. Placebo old states ê_Q: periods Q of the same regime, non-holdout, Q ∉ {P−2, …, P+1}, Q ≠ 23: unit mean of Q's agent-days over its last 3 active days. At least 3 placebos are needed (this drops regime II, where only #33 qualifies).
  7. Pseudo-switches (rival R2): every ordinary day boundary b inside a non-holdout period of the same regime with ≥ 3 active days before b and ≥ 1 after (b not a goal boundary). The same pipeline with "pre" = the day before b, ê_old from up to 3 days before that, and the period's own field span.
- **Output:** `data/processed/H96-goal-switch-hysteresis/` (`transitions.parquet`; `series_<model>_<variant>.parquet` with per-bin M_old, placebo median, n agents; `pseudo_<model>_<variant>.parquet`; `replication/`, `natives/`, `synthetic/`; `_provenance.json`).
- **Regimes covered:** I and III, non-holdout (regime II has < 3 placebo old states).

## Observables
*Written 2026-10-04 20:35 UTC. Sampling facts already seen: eligible statement and 30-min window counts per period, the roster flags, #38/#39 room assignments (DQ6), #51 role-change rows (one real reassignment, agent 40 on 07-29), period units. No content statistic has been computed.*

**O1. Remanence at the switch.** M_pre = M_exc on the pre window; M_1 = M_exc on day 1; persistence ratio **R₁ = M_1 / M_pre** (defined when M_pre's agent-bootstrap CI excludes 0). Agent-cluster bootstrap, 300 draws.

**O2. Inertia time τ_old.** Weighted least-squares fit of M_exc(h_b) = M_pre·exp(−h_b/τ) over the post bins (bin centres h_b; weights = agents in bin; M_pre fixed), log-grid τ ∈ [0.05, 500] active h. CI from the agent bootstrap. t½ (first bin centre with M_exc < ½ M_pre) is reported as a model-free companion.

**O3. Old-state order q_{P−1}.** Mean cosine between different agents' agent-day vectors on the same day, over the ê_old days (N-unbiased pairwise form). Companion: the old kickoff's quench depth on those days (H54's decoy-corrected A_K).

**O4. Order dependence (HH123's check).** Across transitions: Spearman ρ(q, log τ_old) and ρ(q, R₁), per model; partial version controlling for N, regime, kickoff similarity cos(k̂_{P−1}, k̂_P) and the new quench depth A_K(day 1).

**O5. Switch vs ordinary night (rival R2).** ΔR₁ = R₁(switch) − median R₁(pseudo-switches of the same regime); random-effects mean over transitions.

**O6. Old-kickoff variant.** O1–O2 with ê_old replaced by the old kickoff k̂_{P−1} (HH123's literal "old goal"; H54 measured its day-1 level as ≈ 0).

**O7. Coercive-field proxy (descriptive).** A_K(h = τ_old): the new kickoff's decoy-corrected alignment when the old state has fallen by 1/e.

**O8. Robustness.** Both embedding models; variants white32 and style_resid_period32; ê_old from the last 2 instead of 3 days.

**O9. Natives.**
- **G39 (38 → 39, two old rooms, one new field).** Veterans of #38's #best (agents 20–23) and #rest (6, 10, 12–14, 16–18) rooms (DQ6). For each veteran: own-room old state vs other-room old state, both leave-i-out and orthogonal to #39's field span (kickoff, goal, both room kickoffs). Domain memory Δ(bin) = ⟨s·ê_own⊥ − s·ê_other⊥⟩. Statistics: Δ_pre, Δ_1, Δ_1/Δ_pre per room of origin, and room order q_room (O3 within each room). Movers (20, 21, 23 go from #best to #rest) are reported separately.
- **NE38 (G51, 2026-07-29 16:50 UTC).** Agent 40's old role state = unit mean of its statements on the two active days before the reassignment. Field span: the #51 kickoff and agent 40's (post-switch) `agent_goal` vector. Pre = 07-29 statements before the switch (else the previous active day). Placebo: every other #51 agent present on the same days, with its own old state and own `agent_goal` and a pseudo-switch at the same time. Statistics: R₁ and τ_old of agent 40, and its percentile among the placebo agents.

## Null / baseline
*Written 2026-10-04 20:35 UTC, before any real-data content statistic.*
- **Placebo old states** (O1): non-adjacent same-regime late centroids, orthogonalized the same way. Kills generic content (R3 in part).
- **Pseudo-switches** (O5): ordinary day boundaries inside periods (the H20 round-1b rule: use an empirical placebo over boundaries for event studies on two-time content statistics, because fitted stationary nulls are too narrow).
- **Order-permutation null** (O4): Spearman's exact permutation p over transitions.
- **Synthetic** (axis F, before real outcomes): planted statement vectors at the real statement times, agents and transitions: s = unit(α_P(t) k̂_P + m_old(t) ê_old + p_i + σξ) with ξ drawn from the empirical within-period residual covariance; m_old(t) = m₀ exp(−h/τ_old) with log τ_old = log τ₀ + β z(q). Scenarios: S0 quench (τ_old = 0.1 h, β = 0), S1 lag without order dependence (τ_old = 8 h, β = 0), S2 hysteresis (τ_old = 8 h at median q, doubling across the interquartile range of q: β = ln 2 / IQR_z). 100 replicates. Outputs: bias and coverage of τ_old and R₁, size of ρ(q, log τ) under S0/S1, and its power under S2.

## Impostor table (STANDARDS.md §1)
| Impostor | How it could fake hysteresis | How H96 removes it | Status |
| --- | --- | --- | --- |
| Scheduler field | Day-1 content shares the morning re-orientation with the last old day, so any day boundary looks like "persistence" | the pseudo-switch null runs the same statistic over ordinary nights; one vector per agent-bin; active-hour clock | removed |
| Exogenous field (goal, kickoff, operator) | the new kickoff resembles the old state (themed runs), so old-state alignment persists because the new field points there | the new field span (kickoff, goal, room kickoffs) is projected out of both the old state and the agents; placebo old states; kickoff similarity as a covariate (O4); operator messages are not regressed | partly (directions miss part of the topic field; human messages not removed) |
| Shared model priors (family, style) | the same agents write alike before and after, so their content stays near the old centroid | DQ5 `style_resid32`; leave-agent-out old state; placebo old states contain the same agents in regime III | partly (composition carry-over is a named residual, R4) |
| Contemporaneous convergence | agents drift together after the switch without any memory of the old state | the regressor is the old state built days before the switch, not equal-time content; placebo and pseudo-switch nulls; no copying claim is made | n/a for the order claim; partly for the G39 movers |

## Prediction
*Written 2026-10-04 20:35 UTC, before running the analysis on real data.*

What I expect: H54 measured no day-1 remanence of the previous kickoff (median 0.01, p 0.34) and a fast quench onto the new one; H75 found named-target kickoffs freeze the allocation within 15–30 active min; H20 saw a ~4-day settling only in #38, inside a goal. I expect a quench: most of the old state is gone on day 1, faster than at an ordinary night, with no order dependence. My prior on HH123's full claim (order-dependent lag) is about 0.2.

- **P1 quench, not lag (rival R1):** RE mean ΔR₁ < 0 (switch erases more of the old state than an ordinary night) with the 95% CI excluding 0, and R₁(switch) < median R₁(pseudo) in ≥ 2/3 of transitions with an identified old state, in both models. *Against:* ΔR₁ CI includes 0 or is > 0 (the switch is no faster than an ordinary night: R2 or hysteresis).
- **P2 order dependence (HH123's core, the test):** Spearman ρ(q, log τ_old) > 0 with one-sided p < 0.05 in both models. *Against:* ρ ≤ 0 or p ≥ 0.05. A negative P2 counts as **failed** only if the S2 synthetic power is ≥ 0.8; otherwise **inconclusive**. I predict P2 fails (prior 0.2).
- **P3 short inertia:** median τ_old < 8 active h (one regime-III day) across transitions. *Against:* median τ_old ≥ 8 h.
- **P4 old kickoff (O6):** the old-kickoff R₁ is ≤ the old-state R₁ (the old *goal text* leaves less trace than the old *state*). *Against:* old-kickoff R₁ > old-state R₁ in ≥ 2/3.
- **Effect that matters:** τ_old doubling across the interquartile range of q (S2).
- **Per-transition verdict (replication):** *supported* (lag) if M_pre's CI > 0, M_1's CI > 0 and R₁ ≥ the median pseudo-switch R₁; *failed* (quench) if M_pre's CI > 0 and either M_1's CI includes 0 or R₁ < the median pseudo-switch R₁ with the ΔR₁ CI below 0; *mixed* otherwise; *descriptive* if M_pre's CI includes 0 (no identified old state).
- **Overall reading (fixed now):** **Supported:** P2 passes and P1 fails. **Failed:** P1 passes and P2 fails with power ≥ 0.8. **Mixed:** any other combination. **Inconclusive** replaces "failed" if P2's power is < 0.8.

**Natives (dated predictions also in each folder).**
- **N1 G39:** Δ_pre > 0 (CI) [0.85]; Δ_1 > 0 (CI) [0.5]; Δ_1/Δ_pre < 0.5 [0.6]; the room with the higher q_room keeps the larger fraction (HH123) [0.5]. *Supported* if Δ_1 > 0 and the more ordered room keeps more; *failed* if Δ_pre > 0 and Δ_1's CI includes 0; *mixed* otherwise.
- **N2 NE38:** agent 40's R₁ lies below the 10th percentile of the placebo agents (its old role is erased faster than other agents' states drift) [0.7]; τ_old < 8 active h [0.6]. HH123's lag reading (R₁ inside the placebo band) [0.3]. *Supported (lag)* if R₁ is inside the band; *failed (quench)* if below the 10th percentile; *descriptive* if the old state is not identified.

### Amendment 1 (2026-10-04 ~22:20 UTC, after the synthetic, before any real-data run; not post hoc on outcomes)
The synthetic (`analysis/synthetic.py`; real skeletons of all 24 transitions; real residual noise) showed that the pre-registered P2 test is invalid:
- **τ_old (O2) is biased and its order test is mis-sized.** Each statement is a unit vector, so the cosine with the old state decays more slowly when the old state's amplitude is larger. Planted τ_old is recovered at ≈ 0.35× (log bias −1.04 at τ 8 h; CI coverage 0.19). Under no order dependence, ρ(q, log τ_old) has median +0.30 to +0.37 and the one-sided test rejects in 35–57% of replicates (S1, S3); 10% under the quench S0. Under planted hysteresis (S2) it rejects in 70–80%: no separation.
- **Replacement (P2′):** the switching time **τ_sw**, from a weighted fit of ln(M_old(h)/M_new(h)) = L₀ − h/τ_sw over the post bins where both are > 0 (≥ 3 bins). M_new is the same field-orthogonal, placebo-corrected projection on the new state ê_new (leave-agent-out centroid of P's days after the post window; P's last day where P has ≤ 3 days, flagged). The unit norm cancels in the ratio. Synthetic: log bias +0.06 to +0.08 (S1–S3), median |error| 0.50; identified in 98% of lag transitions and 53% under the quench (where τ_sw is meaningless and runs to the 500 h cap).
- **P2′ test:** Spearman ρ(q, ln τ_sw) over transitions with M_pre > 0 and τ_sw < 500 h, against the synthetic null (S1 and S3 replicates): pass if ρ exceeds the null's 95th percentile (+0.29). **Power at the planted doubling over the IQR of q (S2): 0.50.** A negative P2′ is therefore **inconclusive**, not failed, by the card's rule.
- τ_old stays in the tables as a descriptive cosine-scale time. P1 (R₁ vs pseudo-switches) is unchanged: the synthetic separates quench from lag cleanly (R₁ 0.03 under S0, 0.51 under S1, pseudo-switches 1.00).

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R1 quench (H54, H10, H75); R2 ordinary drift (H20); R3 themed runs; R4 composition carry-over.
**Locked holdout used for confirmation:** none yet. `analysis/confirm.py` (frozen, guarded, **not run**) targets the 20 transitions with a held-out side (8→9 … 50→51; #22→#23 and #23→#24 stay excluded).

Round 1 scores (2026-10-04; details in "Round 1 results"):

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | old state, new field and placebos from shared tables; same estimator in regimes I and III and both models; the cosine scale of τ_old depends on the old amplitude (synthetic) |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | single-exponential decay is not adequate: most of the old state goes in the first half hour, a residual decays over ~1 active day (τ_old vs τ_sw) |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 2 | the switch erases the old state beyond ordinary nights (ΔR₁ RE −0.62 bge, −0.72 gte, CIs below 0) and beyond placebo old states (M_pre > 0 in 23–24/24) |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | R₁, the pseudo-switch contrast and NE38 are unfitted and as predicted; HH123's signature (order dependence) is not seen, sign reversed |
| E interventional | predicts the change across a natural experiment | 1 | NE38's single-agent reassignment: predicted quench confirmed (percentile 0 of 22 placebo agents, both models); G39 mixed |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | the synthetic found the τ_old bias and its mis-sized order test (A1); τ_sw is unbiased (log bias +0.06) but the order test has power 0.50 at a doubling over the IQR |
| G ground truth | agrees with known structure | 1 | DQ6 switch time (NE38) and room assignments (G39) |
| H comparative | beats the named rivals | 1 | R1 (quench) beats R2 (ordinary drift) and the hysteresis lag; R3 handled by projection; R4 composition only partly |
| I transfer | holds in other same-mode periods, including the holdout | 1 | quench in regimes I and III and in both models; holdout not run |

**Scorecard: A1 B1 C2 D1 E1 F1 G1 H1 I1.**

## Results by goal period
Replication folders give each transition's verdict under the card rule: *failed* means the switch is a quench (no lag); *supported* means the old state persisted at least as much as across an ordinary night.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G03](goalperiod-subhypotheses/G03/README.md) | replication | failed | #2→#3: R₁ -0.27 [-1.13, -0.11] (nights 0.85); q 0.48; τ_sw – |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | failed | #3→#4: R₁ 0.28 [-0.50, 0.61] (nights 0.85); q 0.69; τ_sw 16.5 h |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | mixed | #4→#5: R₁ 0.70 [0.43, 0.91] (nights 0.85); q 0.50; τ_sw 2.4 h |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | failed | #5→#6: R₁ -0.16 [-0.75, 0.32] (nights 0.85); q 0.33; τ_sw – |
| [G07](goalperiod-subhypotheses/G07/README.md) | replication | supported | #6→#7: R₁ 0.95 [0.77, 1.29] (nights 0.85); q 0.49; τ_sw 6.7 h |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | failed | #7→#8: R₁ -0.28 [-0.45, -0.24] (nights 0.85); q 0.64; τ_sw – |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | failed | #10→#11: R₁ 0.40 [0.17, 0.72] (nights 0.85); q 0.35; τ_sw 13.6 h |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication | mixed | #11→#12: R₁ 0.44 [0.19, 0.85] (nights 0.85); q 0.26; τ_sw 42.5 h |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | descriptive | #12→#13: R₁ 4.64 [1.41, 43.25] (nights 0.85); q 0.45; τ_sw 7.4 h |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | failed | #16→#17: R₁ 0.04 [-0.38, 0.26] (nights 0.85); q 0.31; τ_sw 8.1 h |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | failed | #17→#18: R₁ -0.08 [-0.21, 0.09] (nights 0.85); q 0.38; τ_sw no decline |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | supported | #18→#19: R₁ 0.89 [0.69, 1.20] (nights 0.85); q 0.48; τ_sw no decline |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | failed | #19→#20: R₁ 0.01 [-0.12, 0.16] (nights 0.85); q 0.39; τ_sw no decline |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | failed | #20→#21: R₁ -3.08 [-12.67, -1.00] (nights 0.85); q 0.43; τ_sw – |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | failed | #24→#25: R₁ -0.14 [-0.32, 0.03] (nights 0.85); q 0.35; τ_sw – |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | failed | #25→#26: R₁ 0.30 [0.21, 0.39] (nights 0.85); q 0.70; τ_sw 4.0 h |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | failed | #26→#27: R₁ 0.29 [-0.03, 0.62] (nights 0.85); q 0.54; τ_sw 8.1 h |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | failed | #30→#31: R₁ 0.26 [0.14, 0.45] (nights 0.85); q 0.66; τ_sw no decline |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | failed | #36→#37: R₁ 0.28 [0.02, 0.60] (nights 0.89); q 0.46; τ_sw 38.1 h |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | failed | #37→#38: R₁ 0.11 [-0.08, 0.73] (nights 0.89); q 0.28; τ_sw 26.5 h |
| [G39](goalperiod-subhypotheses/G39/README.md) | native | mixed | #38→#39: R₁ -0.34 [-0.86, -0.02] (nights 0.89); q 0.16; τ_sw – |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | supported | #39→#40: R₁ 1.43 [1.03, 1.92] (nights 0.89); q 0.22; τ_sw 55.4 h |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | failed | #40→#41: R₁ -0.28 [-0.53, -0.08] (nights 0.89); q 0.42; τ_sw – |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | failed | #41→#42: R₁ 0.48 [0.26, 0.72] (nights 0.89); q 0.25; τ_sw 91.0 h |
| [NE38](goalperiod-subhypotheses/NE38/README.md) | native | failed | agent 40 R₁ 0.36 [0.27, 0.47] vs placebo median 1.02 (percentile 0/22) |

## Round 1 results (2026-10-04, exploratory, non-holdout)
*Scripts: `scheme/build.py`; `analysis/{h96lib, synthetic, run, natives, period_folders, figures, estimates_rows, confirm}.py`. Numbers: `data/processed/H96-goal-switch-hysteresis/results/{card.json, transitions_*.json, pseudo_*.json}`, `natives/natives_*.json`, `synthetic/synthetic.json` (+ `synthetic_v1_original_estimator.log`). Figures: `figures/summary_obs.pdf`, `figures/summary_synthetic.pdf`. 24 transitions (18 regime I, 6 regime III), 146 pseudo-switches, both embedding models, DQ5 `style_resid32`.*

### Synthetic validation (axis F, before real outcomes)
On the real statement skeletons of all 24 transitions, with planted topics, real kickoff vectors, agent priors and real residual noise (20–30 replicates per scenario):
- R₁ separates a quench (S0: median 0.03) from an 8-h lag (S1: 0.51) and from ordinary nights (pseudo-switches: 1.00). P1 is identified.
- τ_old (cosine scale) is biased low ×0.35 at τ = 8 h and its order test is mis-sized (rejects 35–57% under no order dependence). This led to Amendment 1 (τ_sw).
- τ_sw is unbiased (log bias +0.06 to +0.08; median |error| 0.50) and its order test is centred (null median ρ −0.04, 95th percentile +0.29). Power at a planted doubling over the IQR of q: **0.50**.

### Outcome vs prediction
| # | Prediction (locked 20:35 UTC; P2′ from A1) | Observed (bge / gte) | Verdict |
| --- | --- | --- | --- |
| P1 | quench: RE ΔR₁ < 0, R₁ below ordinary nights in ≥ 2/3 | ΔR₁ −0.62 [−0.78, −0.45] / −0.72 [−0.88, −0.56]; below in 20/23 / 21/24; R₁ median 0.27 / 0.18 vs ordinary nights 0.85 (I), 0.89 (III) | **supported** |
| P2′ | ρ(q, ln τ_sw) > +0.29 (HH123) | −0.75 (n 12) / −0.52 (n 12): below all 40 null replicates; power 0.50 | **not supported; inconclusive by the power rule; sign reversed** |
| P3 | median τ_old < 8 active h | 0.16 / 0.15 h (cosine scale; ≈ 0.4 h after the synthetic bias correction) | **supported** |
| P4 | old-kickoff R₁ ≤ old-state R₁ | in 10/15 / 10/19 (transitions where the old kickoff has a positive pre level); old-kickoff R₁ median 0.18 / 0.06 | **holds (weak)** |
| N1 G39 | Δ_1 > 0 and the more ordered room keeps more | Δ_pre 0.61 → Δ_1 0.09, ratio 0.15 [0.03, 0.32] / 0.26 [0.12, 0.42]; the more ordered #best (q 0.55 vs 0.37) keeps less (−0.04 vs 0.27), carried by its 3 movers (−0.08); stayers 0.25 | **mixed** |
| N2 NE38 | agent 40's R₁ below the placebo 10th percentile | R₁ 0.36 [0.27, 0.47] / 0.22 [0.08, 0.35]; placebo median 1.02, p10 0.62; percentile 0 of 22; τ_old 1.7 / 0.65 h | **failed for HH123 (quench, as predicted)** |

**Robustness (O8, bge).** white32 (no style residualization): ΔR₁ −0.58 [−0.76, −0.41], below nights in 0.86, ρ(q, ln τ_sw) −0.71 (n 10). style_resid_period32: ΔR₁ −0.63 [−0.76, −0.51], below in 0.92, ρ −0.20 (n 13). The quench survives every variant; the order trend's size does not (−0.20 to −0.75), consistent with its low power.

Per-transition verdicts (bge): 18 quench (*failed*), 3 lag (*supported*: #6→#7, #18→#19, #39→#40), 2 mixed, 1 descriptive. gte: 19 / 3 / 2 / 0.

**Overall reading (rule fixed before data):** P1 passes and P2′ is negative with power 0.50, so the card verdict is **inconclusive** for HH123's order-dependent coercivity. The headline is a quench: a goal switch erases 70–80% of the old state's field-orthogonal remanence by day 1, about 3× more than an ordinary night does.

### Post hoc (labelled)
- **Two-stage switch.** τ_old (first half hour) and τ_sw (residual) disagree by ~100×: most of the old state is gone within the first active half hour, and in 12/24 transitions a small residual old-state share then decays relative to the new state with τ_sw ≈ 7–15 active h (median; IQR 4–51 h). 4 transitions show no decline of the residual.
- **Anti-coercivity.** Among those 12, more ordered old states switch faster (ρ −0.75 / −0.52). The sample is selected (lag transitions only) and the power rule applies; read it as a hypothesis for round 2, not a finding.
- **Model dependence.** bge and gte agree on the card-level numbers but not on every transition (e.g. #19→#20: R₁ 0.01 vs 0.45).

### Answer to the question
A goal switch acts as a quench on the content state. On day 1 the old state's field-orthogonal remanence is 0.18–0.27 of its pre-switch level, against 0.85–0.89 across an ordinary night, and a reassigned single agent loses its old role state faster than any of 22 same-day placebos. There is no sign that more ordered old states resist longer; the measured trend points the other way but the test has power 0.50. In practice there is nothing to "clear" before reassigning a swarm: the new kickoff does it within the first active hour.

## Round 2 redirects (2026-10-04)
- **H96-R1.** Raise power for the order test: pool transitions with H82's boundary rows (same transitions, different estimator) as robustness, and add the held-out transitions in the confirm run (20 targets).
- **H96-R2.** Two-stage model: fit a fast quench fraction plus a slow residual (two exponentials, or a ratio model with a quench offset) and test whether the residual is veterans' context carry-over (regime III) or record-borne (newcomers; H82 N1/N2).
- **H96-R3.** Explain anti-coercivity: are ordered old states the ones whose new kickoff is most specific (H54's quench depth)? Partial correlation on A_K(day 1) with more transitions.
- **H96-R4.** Run `confirm.py` after Vivian's sign-off and the ledger disclosure (H82, H54, H10 plan the same targets).

## Notes
- 2026-10-04 20:35 UTC: card written before any content statistic. Holdout masked with `holdout_mask`; held-out counts never printed. #23 excluded (H10's blind pair).
- 2026-10-04 ~22:20 UTC: Amendment 1 after the synthetic, before real data (τ_sw replaces τ_old for P2).
- 2026-10-04 ~22:40 UTC: real run (both models), natives, period folders. The G39 folder carries the native verdict; its replication verdict (#38→#39: quench) is inside it.
- H82 had no outputs when this ran; no H82 code or data was used. The old-state construction follows H82's card (leave-agent-out centroid, placebo centroids) so the two can be compared later.
- Synthetic finding for shared files: any cosine-based decay time on unit statement vectors depends on the decaying component's amplitude, so cross-period comparisons of cosine "relaxation times" against an order parameter are biased (bears on H20, H48, H54 τ_K). Use ratio estimators.
