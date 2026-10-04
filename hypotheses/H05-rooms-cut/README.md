# H05: Cutting the cross-room channel lowers entropy production, and rooms become coupled blocks

**Status:** **confirmatory run on the locked holdout (2026-10-03): INCONCLUSIVE by the pre-registered rule.** The primary pair DiD at the 03-16 split (C1) **passed**: separated pairs lost talk coupling relative to pairs that stayed together. The MF J_out criterion passed. The pooled TWFE (C3) had the right sign but was not significant (z = 1.4). The 02-25 placebo behaved: no separation, no change. Exploratory round 1 had found rooms to be coupled blocks for talk; EP is not detectable at this sampling.
**Fields:** stat mech, thermodynamics, dynamics, info theory
**Literature:** [Aguilera, Ito & Kolchinsky 2026](../../literature/aguilera-2026-entropy-production-nonequilibrium-maxent.md) (the estimator)
**Origin:** shortlist S4 ([`../promotion-shortlist.md`](../promotion-shortlist.md)); idea HH33; feeds H01 D1.1.a (rooms are superagents), D3.2 and D9.2 ([`../H01-emergent-superagents-exist/subhypotheses.md`](../H01-emergent-superagents-exist/subhypotheses.md)).
**Definitions used** (`physics-models/DEFINITIONS.md`): Regime; Population; Interaction (broadcast: co-located = same current room); Entropy production / irreversibility, in a named variant proposed here, **"entropy production (pairwise AIK bound on activity spins)"** (defined under Observables; to be added to DEFINITIONS.md by whoever owns that file).

## Question
When the chat channel between two groups of agents is cut (they are put in different rooms and see only their own room), does the coupling between the groups vanish while coupling inside each group holds, and does the swarm's statistical irreversibility (entropy production) fall? Equivalently: do rooms behave as coupled blocks, i.e. candidate superagents?

## Model
**From:** `physics-models/02-nonequilibrium-ising/` (primary), with `01-inverse-ising` (symmetric couplings) and `09-hawkes` (rival/complement, not fitted in round 1).
- Agents are binary spins on 1-min bins, s_i(t) = +1 if the agent acted or talked in the bin (`activity_bins.state ≥ 3`), else −1. Secondary spin: talk only (`state = 4`).
- Kinetic Ising with parallel updates, P(s_i(t+1) | s(t)) ∝ exp(s_i(t+1) H_i(t)), H_i = h_i(t) + Σ_j J_ij s_j(t). The field h_i(t) carries the daily schedule; J_ij is the coupling.
- **Room-structured couplings:** J_ij = J^in_ij if i and j share a room at t, J^out_ij otherwise. The hypothesis is J^out ≈ 0 (channel cut) while J^in is unchanged. Since σ = Σ_{i<j} (J_ij − J_ji) ⟨s_i(t+1)s_j(t) − s_i(t)s_j(t+1)⟩, removing J^out removes the cross-room part of the entropy production.
- The model is a coarse one: the village's update order is state-dependent (see model 02), and the 1-min parallel form is an approximation.

## Data scheme (`scheme/`)
- **Script:** `scheme/build_panel.py`.
- **Inputs (shared tables only):** `activity_bins` (state per agent × 1-min bin of each PT day's active window), `calendar` (window start, goal, regime, holdout flag), `rooms_timeline` (agent, room, t_start, t_end), `roster`, `rooms`.
- **Transform:** for every non-holdout day, attach each agent's current room to each bin (as-of join on `rooms_timeline.t_start` at the bin's UTC time); flag a day-level room for each agent (modal room, purity).
- **Output:** `data/processed/H05-rooms-cut/` (`panel.parquet`: pt_date, minute, agent, active, talk, room; `agent_day.parquet`: day-level room and activity; `_provenance.json`).
- **Regimes covered:** III (2026-03-24 →), non-holdout days only; regime II #35/#36 used only as a labeled side check.
- The Claude Code agent is excluded (it is not in `activity_bins`).

## Observables
1. **Entropy production (pairwise AIK bound on activity spins), Σ_g.** Observables g_ij(t) = s_i(t+1)s_j(t) − s_i(t)s_j(t+1) for i < j (antisymmetric under time reversal; parallel form). Σ_g = max_θ θ·⟨g⟩ − ln⟨e^{−θ·g}⟩ (forward samples only, since g is antisymmetric). θ is fitted on training days and Σ_g is **evaluated on held-out days** (day-blocked K-fold, nested λ choice for an L2 penalty). Reported per bin, **per agent-hour** (×60/N) and per pair-hour (×60/#pairs). Only transitions within a day are used. *Companion (added in round 1):* the **cross-fitted Newton-step bound** Σ_N = 2·mean_{a≠b} ḡ_aᵀK⁻¹ḡ_b over day folds, which has a much lower noise floor (~√(2d)/T vs. d/T).
2. **Inferred antisymmetric couplings** θ_ij ≈ J_ij − J_ji (from the same fit).
3. **Pair irreversibility** Σ_ij: the same bound for a single pair. Pair-day version: block cross-fitted Gaussian (Newton-step) form 2·mean_{a≠b}(ḡ_a ḡ_b)/s² over 4 contiguous within-day blocks. *(Changed during round 1: the first version, 2(ḡ² − s²/T)/s² with an iid correction, was biased negative because within-day flicker anti-correlates g.)*
4. **Symmetric lagged coupling** κ_ij = ½[corr(s_i(t+1), s_j(t)) + corr(s_j(t+1), s_i(t))], per pair-day or pair-window; contemporaneous correlation c_ij as a side statistic. In window comparisons, minus a **cross-day surrogate** (agent i's day d paired with agent j's day d′ ≠ d, aligned by minute of the day's window), which keeps the shared daily schedule and removes real interaction.
5. **Kinetic Ising couplings** J_ij (L2 logistic regression of s_i(t+1) on s(t), with self-coupling and a time-of-day field).
6. **Block index:** mean within-room minus mean cross-room coupling, against random partitions with the same room sizes.
7. **Pair difference-in-differences** at room events: Δ(treated pairs) − Δ(pairs co-located throughout); and a pooled **two-way fixed-effects** panel, y_{ij,d} = α_ij + γ_d + β·coloc_{ij,d}, where the day effect γ_d absorbs goal changes and operator resets.

## Null / baseline
- **Estimator nulls:** time-reversed data (θ must flip sign); configuration shuffles and independent per-agent circular shifts within days (Σ_g → 0 on held-out data).
- **Shared-field null:** the cross-day surrogate (common daily schedule, no interaction).
- **Room-label null:** random partitions of the same agents with the same room sizes (is the actual partition special?).
- **Assignment null for events:** re-draw which agents moved (same design sizes) and recompute the DiD.
- **Placebo events:** goal changes without room changes (same DiD machinery).
- **Rival:** room membership doesn't matter because agents couple through shared artifacts (repos, documents) and shared goals; then within ≈ cross and the DiD ≈ 0.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** shared-field / artifact coupling (no room effect); Hawkes (model 09) for directed influence.
**Locked holdout used for confirmation:** NE12 window (2026-02-23 → 03-02), #34 (incl. #voted-out room, 03-05 → 03-13), NE30 window; before-window of NE15. Script: `analysis/confirm_ne12.py` (not run).

Scored for round 1 (exploratory, non-holdout), mapping = 1-min binned spins, regime III two-room windows and room events.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Spins from `activity_bins.state`, rooms from `rooms_timeline` (as-of join per bin); assumptions listed above. Not checked for invariance: "active" means computer-use turns in regime III but discrete sessions in regime II. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Daily schedule handled by the cross-day surrogate. V2: nonstationarity with symmetric J gives no spurious EP. But heterogeneous misaligned profiles do (circular-shift null > 0 on real data). No update-order audit; parallel form assumed. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Talk couplings beat the shared-field (cross-day) null and the room-label null (X2 pooled p < 1e-3). Whole-swarm EP does **not** beat the cross-day null. No held-out likelihood comparison of a room-structured vs. unstructured kinetic Ising. |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | Not attempted. The MF loop gain (0.05–0.4) is computed but no forward prediction was tested. |
| E interventional | predicts the change across a natural experiment | 1 | Non-holdout room events: pooled TWFE for talk β > 0 (1 min: κ_x z = 2.6, c0_x z = 2.6; 5 min: c0_x z = 2.5, κ_x z = 1.7, and z = 2.7 in the two-room era). Single events have the right sign for talk but are underpowered (V4 power 23–63%). Active spins: mixed or wrong sign. EP change not detectable. **Holdout (2026-10-03):** C1 pair DiD at NE15 passed (sign + significance; size not pre-registered, so E stays 1); pooled C3 not significant. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | V1: θ vs. J − Jᵀ r = 0.89–0.95. V3: a cut is recovered by pair DiD (20/20) and by the Newton EP bound. V4: low power at village coupling. MF estimator recovers J_out ≈ 0 after a cut. Talk results robust from 1 to 5 min; active results are not. |
| G ground truth | agrees with known structure | 1 | Talk couplings follow the room partition in 6/6 regime III two-room windows (J_sym and MF J_in > J_out). Blind partition recovery was not tried, and room-specific goals/kickoffs (a room field) are only partly removed by the surrogate. |
| H comparative | beats the named rivals | 0 | Rivals (shared artifacts/goals; Hawkes) not compared by held-out likelihood. Active-spin coupling being room-independent is what the artifact/task rival predicts. |
| I transfer | holds in other same-mode periods, including the holdout | 1 | Talk block structure holds across 6 regime III windows and in #35 (regime II), not in #36 or #39. Holdout used 2026-10-03: the talk cut effect transfers to the NE15 split (C1), and J_out → 0 (C5); J_in rose instead of staying put. |

## Prediction
*Written 2026-10-03, before running any analysis on real data. At this point only the room assignments (treatment structure, from `rooms_timeline`/`events_core.room`) had been looked at, no activity statistics.*

**Structural facts found while designing (treatment assignment only):**
- At NE12 itself (2026-02-25) **no pair was separated**: every agent stayed in #general until #voted-out appeared on 03-05/06 (inside #34, holdout) and the #best/#rest split on 03-16 (NE15). NE12 introduced room-scoped visibility, but the channel was only cut when a second room was populated. The confirmatory test must therefore use actual pair separation, and 02-25 is a placebo date for the channel (it still carries the NE35 operator reset).
- Non-holdout regime III contains several room events: 04-02 (Sonnet 4.6 #rest → #best), 04-27 (Opus 4.6, Sonnet 4.6, GPT-5.4 #best → #rest; GPT-5.5 joins #best), **05-04 merge** of #best and #rest into #universe-coordination **except GPT-5, left alone in #rest**, **05-11 split** back to the same partition (an A-B-A), 05-25 (Gemini 3.1 Pro #best → #rest; #43 held out, so #42 vs. #44), 06-22 merge into #general (#48, holdout), 07-09/10 GPT-5.6 triplet isolation then merge, **08-05 → 08-24 #focus** (Gemini 2.5 Pro and Opus 4.8 leave #general, then return).

**Predictions.**
- **P1 (estimator, synthetic).** On kinetic Ising data with known asymmetric couplings, village-like sampling (days of ~240 bins, 20–60 days, N ≈ 16, mean activity 0.3–0.7): held-out Σ_g > 0, Σ_g ≤ true Σ, Σ_g ≥ 0.5 Σ; corr(θ, J − Jᵀ) ≥ 0.8; time reversal flips θ (corr ≤ −0.8) and leaves Σ_g > 0; configuration shuffles and independent circular shifts give held-out Σ_g within 2 SE of 0. A synthetic cut (cross-room J → 0) lowers Σ_g, and the pair DiD recovers the cut with the right sign. *Falsifier:* recovery below these thresholds, or shuffles giving Σ_g > 0.
- **P2 (rooms as blocks, regime III two-room windows #37–#39, #41, #42, #44).** Within-room pairs couple more than cross-room pairs: excess κ (over the cross-day surrogate) within/cross ≥ 1.5, and the room partition beats random partitions of the same sizes (p < 0.05). Same direction for pair irreversibility Σ_ij and kinetic-Ising J. Cross-room coupling is small but not zero (shared artifacts and goals). The effect is larger for talk spins than for active spins. *Falsifier:* within ≤ cross, or the partition is not special (p > 0.2).
- **P3 (room events, pair DiD).**
  - 05-04 merge: DiD(best×rest pairs vs. always co-located) > 0 for κ and Σ_ij; GPT-5's pairs with #rest agents (cut that week) DiD < 0.
  - 05-11 split (a cut): DiD < 0, the mirror image; cross coupling returns toward its #39 level (A-B-A).
  - 04-27 transfer: cut pairs DiD < 0, added pairs DiD > 0.
  - #focus (08-05 → 08-24): pairs of {Gemini 2.5 Pro, Opus 4.8} with everyone else DiD < 0, recovering after the return.
  - GPT-5.6 triplet: newcomer–incumbent coupling lower while isolated than after the merge (low power; direction only).
  - Pooled two-way FE over all non-holdout regime III pair-days: β(co-location) > 0 for κ and for Σ_ij, 95% CI excluding 0.
  - EP: the cross-pair part of Σ_g (fitted on cross-pair observables only, per pair) rises in the merged week relative to the within-pair part, and falls again at the split. Whole-system Σ_g per agent-hour moves with the number of co-located pairs (higher when merged), but goal changes confound this, so only the decomposition counts as evidence.
  - *Falsifier:* pooled β ≤ 0 or CI including 0, together with DiD signs at the clean events (merge, split, #focus) not matching.

### Sub-hypothesis H05-MF: two-block (R-block) mean field (HH82)
*Added 2026-10-03 at Vivian's request (relayed by the coordinator), after round-1 X2/X3 had been run. Predictions written before any MF code was run.*
- **Model** (`physics-models/01-inverse-ising`, "Mean-field forward version"): rooms are sublattices. Couplings are J_ij = J_ab for i in room a, j in room b (i ≠ j): J_in = J_aa, J_out = J_ab, plus fields. **No N×N inference:** the only inputs are block-averaged excess equal-time correlations r_ab = ⟨c0 − c0_surrogate⟩ over the pairs of each block (the cross-day surrogate removes schedule-locked fields), and the mean variances v = 1 − m². Naive mean-field inversion on the block-homogeneous correlation matrix: J = D^{-1/2}(I − R̂^{-1})D^{-1/2}, block-averaged. Uncertainty: day bootstrap. Null: room-label permutations.
- **Caveat on blindness:** the inputs are block averages of `c0_x`, which X2/X3 had already reported (talk: within > cross in 6/6 two-room windows; merge-week add-arm c0_x DiD +0.035). MF1–MF3 are therefore **not blind**. MF-C (holdout) is.
- **MF1 (regime III two-room windows #37–#39, #41, #42, #44).** Talk spins: J_in > J_out in ≥ 5/6 windows, and J_out's day-bootstrap 95% CI includes 0 in ≥ 4/6. Active spins: J_in > J_out in ≥ 4/6, with J_out > 0 (shared work and artifacts couple activity across rooms).
- **MF2 (merge, #39 → #40 → #41, sublattices = the #best/#rest partition; GPT-5 excluded).** Talk: J_out − J_in rises in #40 (merged) relative to #39 and #41, i.e. the two sublattices fuse while they share a room. Active: same direction, weaker.
- **MF3 (#focus, sublattices = {Gemini 2.5 Pro, Opus 4.8} vs. #general).** J_out falls during #focus (08-06 → 08-21) relative to before (07-27 → 08-04) and recovers after (08-25 → 09-04); J_in(#general) changes by less than ±50%.
- **MF4 (GPT-5.6 isolated rooms, 07-09).** No prediction: each isolated room held one agent for ~1.5 h, so J_in is undefined and J_out would rest on ~100 bins of one interval with no cross-day surrogate. Recorded as not estimable.
- **MF-C (confirmatory, NE12/NE15 on the holdout; in `analysis/confirm_ne12.py`).** Sublattices = the 03-16 #best/#rest partition. **J_out → 0 after rooms arrive** (J_out in #35 within 2 bootstrap SE of 0, and below its pre-split value), **with J_in unchanged** (post − pre day-bootstrap 95% CI includes 0; *amended 2026-10-03 before any holdout use from "post/pre ratio CI includes 1", which a non-holdout dry run showed is unstable when J_in(pre) ≈ 0*), for talk spins. At 02-25 itself (no pair separated) J_out does not drop (placebo). Active spins: same direction, reported, not decisive.

### Confirmatory predictions for the holdout (NE12 / #voted-out / NE15)
*Written 2026-10-03 after exploratory round 1, before any holdout outcome was computed. Machine-readable and applied mechanically in `analysis/confirm_ne12.py` (`PREDICTIONS`, `verdicts`).*
- **C1 (primary).** NE15 cut arm (#best × #rest pairs) vs. pairs co-located throughout:
  - the DiD of talk c0_x **and** talk κ_x is < 0;
  - for at least one of them, the day-bootstrap 95% CI excludes 0 and the assignment-permutation p < 0.05.
- **C2.** Same for active spins: direction only. Not decisive, given the exploration.
- **C3 (primary).** Pooled TWFE over 02-09 → 03-20, talk κ_x: β(co-location) > 0, two-way clustered z > 1.96. Expected size ≈ +0.008.
- **C4.** Class-restricted EP DiD < 0 (direction only). Whole-swarm EP per agent-hour does **not** fall at 02-25. Low power; a null is uninformative.
- **C5 = MF-C** (above).
- **C6.** No pair is separated on 02-25 (asserted).
- **Overall.**
  - **Confirmed** if C1, C3 and C5's J_out criterion all pass.
  - **Refuted** if C1 and C3 both have the wrong sign, or CIs centred on 0 with |effect| below half the exploratory effect.
  - Otherwise **inconclusive**.

## Results by goal period
One folder per goal period (`G<NN>/`) or spanning natural experiment (`NE<NN>/`), each with its verdict; the cross-hypothesis table is [../OVERVIEW.md](../OVERVIEW.md). Round-1 periods were scored against P2 after the fact (`analysis/write_period_folders.py`). Of the six P2 windows, talk κ_x passes in G38, G41 and G44, is mixed in G37 and G42, and fails in G39. That is more sobering than the pooled "6/6 within > cross", which used direction only. NE15 is the confirmatory test.

## Results
### Exploratory round 1 (2026-10-03; non-holdout only: 99 days, #35–#42, #44 and #51 up to 09-04; holdout asserted absent)
**Labeled exploratory.** Many statistics were computed (two spins, two bin widths, about 10 events, several outcomes), so single p-values are descriptive. The pre-specified primary tests are the X2 pooled comparison and the pooled TWFE (P2, P3). Scripts: `scheme/build_panel.py`, `analysis/{ep,pairs,validate_synthetic,validate_mf,explore_rooms,mf_blocks,figure_summary}.py`. Numbers: `data/processed/H05-rooms-cut/{synthetic_validation,validate_mf,explore_bin1,explore_bin5,mf_blocks}.json`. Figures: `figures/summary_round1.pdf` (overview), `x2_within_cross*.pdf`, `x3_events*.pdf`, `mf_blocks.pdf`, `synthetic_validation.pdf`.

**Estimator validation (synthetic, P1).**
- **Held-out AIK bound.** Kinetic Ising, N = 16, 20–40 days × 240 bins, strong asymmetry (exact Σ = 0.68–1.41 nats/bin). The held-out ML bound recovers 69–85% of Σ (in-sample 98%). θ vs. J − Jᵀ: r = 0.89–0.95. Time reversal flips θ exactly (r = −1.00); Σ_g is unchanged, by construction of the forward-only form, so reversal tests θ, not Σ.
- **Null behavior.** Configuration shuffles and circular shifts give a held-out ML bound slightly **below** 0 (−0.003 to −0.025): conservative, not "within 2 SE". The **cross-fitted Newton-step bound** (added here: 2 ḡ_aᵀK⁻¹ḡ_b across day folds) recovers 72–75% of Σ with 3–5× smaller SE and sits at ≈ 0 (|·| < 0.01) under shuffles. It is the more useful estimator at village sample sizes.
- **V2: nonstationarity with symmetric J** (Σ = 0: cold daily restarts, a shared schedule field) gives no spurious EP with either estimator.
- **V3: a synthetic room cut.** With activity held at ~0.47 by the dynamics, the cut sends cross-pair EP to 0, leaves within-pair EP unchanged and halves total EP (20/20 reps; the Newton bound tracks the exact values). In a near-absorbing parameter set (activity 0.03), the same cut **raised** total EP by moving agents off the absorbing state. So "a cut lowers EP" holds only if the cut does not shift the operating point. The robust signature is the cross-pair EP and coupling going to 0.
- **V4: village-matched power.** 15 agents in rooms of 4 + 11, 5 + 5 days. A full cut of couplings giving κ ≈ 0.014 (the size seen in the data) is detected by the single-event pair DiD (permutation p < 0.05) in only 23% of reps; κ ≈ 0.036 gives 63%. The permutation test has the right size (3% at α = 0.05 over 60 null reps). The day-bootstrap CIs are anti-conservative with 5 days (7–30% false positives), so permutation p is the primary inference.
- **MF estimator** (`validate_mf.py`): recovers J ≈ 1.2–1.3 μ, J_out ≈ 0 (SD 0.006) after a cut, and J_in ≈ J_out without one.

**Outcome vs. prediction**

| | Prediction | Outcome | Verdict |
| --- | --- | --- | --- |
| P1 | held-out Σ_g > 0, ≤ Σ, ≥ 0.5 Σ; r(θ, J−Jᵀ) ≥ 0.8; reversal flips θ; shuffles ≈ 0; cut recovered | 69–85% of Σ; r = 0.89–0.95; θ flips exactly; shuffles slightly negative (ML), ≈ 0 (Newton); cut recovered when activity is fixed | **passed**, with two qualifiers: ML bound biased low under the null, and low power at village coupling (V4) |
| P2 talk | within > cross, ratio ≥ 1.5, partition special (p < 0.05) | kinetic-Ising J_sym within > cross in **6/6** regime III windows (Fisher p < 1e-4). Cross-room talk J ≈ 0 in #38, #41, #44 (0.002, 0.002, 0.012 vs. within 0.06–0.11). Excess c0 6/6 (p = 0.001), κ_x 5/6 (p = 2e-4). Survives 5-min bins (c0_x 6/6, J 6/6) | **supported** |
| P2 active | same, weaker | κ_x 4/6 (p = 0.01), J_sym 4/6 (p = 0.03), ratio ≈ 1.2–1.4. **Vanishes at 5-min bins** (3/6, p = 0.35) | **not robust** |
| P2 EP | pair irreversibility within > cross | pair EP (block cross-fit) within > cross: active 5/6 at 1 min (p = 0.02), 3/6 at 5 min; talk 3/6. Class-restricted Newton EP per pair-hour: 4/6 (active), 2/6 (talk), n.s. | **not supported** (noise level) |
| P3 merge 05-04 | DiD > 0 for added pairs | talk c0_x **+0.035** (perm p = 0.03), talk κ_x +0.002 (n.s.); active κ_x **−0.020** (p = 0.12, wrong sign) | talk partial; active **against** |
| P3 split 05-11 | DiD < 0 for cut pairs | talk c0_x −0.025 (p = 0.12), κ_x −0.008 (p = 0.5); active κ_x −0.013 (p = 0.17). 5 min: talk −0.040 / −0.032 (n.s.) | right sign, **n.s.** |
| P3 A-B-A | #41 cross coupling back to #39 level | cross pairs' κ_x fell relative to within from #39 to #41 (talk −0.024, p = 0.05; active −0.030, p = 0.009): #39 had **no** block structure, #41 had it | **not as predicted** |
| P3 04-27 transfer | cut < 0, add > 0 | active cut arm **+0.040** (p = 0.06, wrong sign); talk cut −0.008 (n.s.); add ≈ 0 | **against / n.s.** |
| P3 04-02, 05-25 transfers | cut < 0, add > 0 | talk cut κ_x −0.078 (p = 0.07) and −0.041 (p = 0.25); active add arm −0.083 (3 pairs, p = 0.04, wrong sign) | mixed, tiny arms |
| P3 #focus | cut arm < 0 during, recovers after | talk −0.003 then +0.008; active −0.007 then +0.004: right signs, all n.s. | right sign, **n.s.** |
| P3 GPT-5.6 triplet | lower coupling while isolated | isolation lasted ~118 min mid-session. Active DiD +0.10 [0.03, 0.16], but driven by an incumbent burst during the isolation interval; talk ≈ 0. Grok 4.5 (07-10) and Opus 5 (07-24) similar and n.s. | **uninterpretable** |
| P3 pooled TWFE | β(co-location) > 0, CI excludes 0 | talk: κ_x **+0.0076 (z = 2.6)**, c0_x **+0.011 (z = 2.6)**, raw κ +0.0097 (z = 3.7). 5 min: c0_x z = 2.5; #37–#44 κ_x z = 2.7. Driven by the two-room era; #51 (#focus only) ≈ 0. Active: β ≈ 0 (z = 0.05). Pair EP: z ≤ 1.9 | **supported for talk**; not for activity or EP |
| P3 EP | cross-pair EP rises when merged, falls at split | whole-swarm Newton EP per agent-hour: #39 0.045, #40 0.081, #41 −0.075. Direction as predicted, but excess over the cross-day null is −0.04, +0.05, −0.07 (null sd 0.07–0.11). Class-restricted EP DiDs have mixed signs | **not detectable** |
| Placebos | ≈ 0 | 1 min: 1 of 8 placebo tests p < 0.05. 5 min: 3 of 8 p < 0.05 (κ_x with ~48 transitions per pair-day is noisy) | single-event tests unreliable at 5 min |

**Entropy production per agent-hour (X5, active spins).** The held-out ML bound is negative in every window: its noise floor is d/T with d = N(N−1)/2 = 66–378 and T ≈ 1–4 × 10³. The cross-fitted Newton bound ranges from −0.14 to +0.29 nats per agent-hour (≈ −0.01 to +0.04 per pair-hour). It lies within ~2 null SD of the **cross-day surrogate** (each agent's own days, aligned by minute) in 15/18 windows. Exceptions: #42 (+0.24) and #51 W28 (+0.09); W31–W32 and W35 are borderline at about +0.05.

**Conclusion.** At pairwise order and 1-min resolution, the swarm's activity is statistically indistinguishable from the shared-schedule null. The within-day circular-shift null is **not** a valid null on real data: it misaligns heterogeneous daily profiles and creates spurious irreversibility.

**H05-MF (two-block mean field)**

| | Prediction | Outcome | Verdict |
| --- | --- | --- | --- |
| MF1 talk | J_in > J_out ≥ 5/6; J_out CI ∋ 0 ≥ 4/6 | J_in > J_out **6/6**. J_out CI includes 0 in **6/6**. J_in 0.03–0.27, J_out −0.08–0.11. Loop gain 0.06–0.25, far from mean-field criticality (1) | **supported** (not blind; see caveat above) |
| MF1 active | J_in > J_out ≥ 4/6, J_out > 0 | J_in > J_out 4/6, one of them a tie (#38: 0.027 vs. 0.026). #37 reversed (J_out 0.059 > J_in 0.014). J_out > 0 in 5/6 | **borderline** |
| MF2 merge (talk) | J_out − J_in rises in #40 vs. #39 and #41 | +0.28 [0.10, 0.46] vs. #39; −0.075 [−0.13, +0.08] from #40 to #41. But #39 → #41 is also +0.20, because #39 had J_out < 0 | **partial** (driven by an odd #39) |
| MF2 merge (active) | same direction, weaker | −0.026 [−0.059, −0.001] | **against** |
| MF3 #focus | J_out falls, then recovers; J_in(general) within ±50% | J_out right signs, all n.s. J_in(general) changed by −71% (active) and +45% (talk) | **not supported** (no room-specific signal) |
| MF4 triplet | (none) | not estimable (single-agent rooms, ~1.5 h) | n/a |

**What this means.**
1. **Rooms do act as coupled blocks for the chat channel.** Agents in the same room have correlated talk activity beyond the shared schedule. Cross-room talk coupling is ≈ 0, and moving pairs into or out of a room shifts their talk coupling in the predicted direction (pooled β ≈ +0.01 in correlation units, z ≈ 2.6).
2. **Overall activity is not room-structured** in any robust way. Agents' computer-use activity is coupled about as much across rooms as within. This is consistent with the rival view that work is driven by individual tasks, shared artifacts and the schedule, not by room chat.
3. **The thermodynamic half of S4 can't be tested at this resolution.** Pairwise EP on 1-min activity is at the null level, and the synthetic results show that even a real cut moves EP only if it doesn't shift activity levels. A better test needs a higher-signal state (talk/reply events, action classes as in H09 E2) or event time.

**Bin-width robustness.** Talk results hold at 5-min bins; active-spin room effects do not. `explore_bin5.json`.

### Confirmatory (locked holdout; run 2026-10-03 23:13 UTC, signed off by Vivian; pre-registration commit e9bf2f7)
`confirm_ne12.py --confirm` was run once, card prediction hash 9df7b66d2a2a3d69. Output: `data/processed/H05-rooms-cut/confirm/confirm_ne12.json`.

| Prediction | Result | Verdict |
| --- | --- | --- |
| C6: no pair separated on 02-25 | 0 separated pair-days before or after | ✓ (asserted) |
| **C1 (primary): NE15 cut-arm DiD < 0, talk** | κ_x DiD = **−0.022** [−0.038, −0.008], p_perm = **0.021**; c0_x DiD = **−0.037** [−0.065, −0.004], p_perm = **0.016** (18 cut pairs, 37 stay; pre = 10 days, post = 5) | **PASS** |
| C2: same, active spins (direction only) | κ_x −0.015 [−0.038, 0.007], p = 0.34; c0_x +0.007, p = 0.82 | mixed, n.s. (as expected) |
| **C3 (primary): pooled TWFE 02-09 → 03-20, talk κ_x, β > 0 at z > 1.96** | β = +0.013 (larger than the expected +0.008), two-way SE 0.0093, **z = 1.40**. c0_x: β = +0.029, z = 1.98 (not the pre-registered measure) | **FAIL** (right sign, not significant) |
| C4: no whole-swarm EP drop at 02-25 | post − pre CI includes 0 (talk and active) | ✓ (a null; low power) |
| C5 (MF-C): J_out → 0 after the split | J_out: +0.032 [−0.011, 0.082] (pre) → **−0.033 [−0.092, 0.025]** (#35) | **PASS** |
| C5 (MF-C): J_in unchanged | J_in: +0.023 [−0.013, 0.059] → **+0.139 [0.06, 0.35]** | **FAIL: J_in rose** |
| 02-25 placebo (talk) | κ_x post − pre −0.004 [−0.012, 0.005]; c0_x +0.002 [−0.009, 0.012] | ✓ no change |

**Overall (pre-registered rule): INCONCLUSIVE.** "Confirmed" needed C1, C3 and C5-J_out; C3 missed. Not refuted, since C1 passed.

**Reading:**
- Cutting the channel did what the block model says to the cross-room pairs: their chat coupling dropped to about zero, and the drop is detectable at the pair level on held-out data.
- The pooled design across 02-09 → 03-20 is noisier than the single-cut DiD.
- **New, unpredicted:** within-room coupling *rose* after the split, roughly ×6, with a CI excluding 0. Possibly the attention that cross-room partners had received was redirected to room-mates (a conserved attention budget?), or the #35 forks raised in-room coordination. Worth its own HH; check against #35's fork activity (H07).
- Under the project's per-goal-period rule (adopted after this pre-registration), C1 is the natural design: one cut, compared across the boundary. C3's pooled TWFE is exactly the kind of cross-period pooling the rule discourages.

## Notes
- 2026-10-03: card opened (one of five parallel agents). Holdout masked via `calendar.holdout` and `holdout.json`.
- 2026-10-03: **NE12 premise.** No pair was separated on 02-25: all agents stayed in #general until #voted-out (03-05/06) and #best/#rest (03-16). The confirmatory script treats 02-25 as a placebo for the channel (C6) and tests actual separations (#voted-out; NE15). It asserts the premise from `rooms_timeline` before analysing.
- 2026-10-03: **Exploratory design changes made after seeing data, before any holdout use.**
  - The pair-day Gaussian EP with an iid correction was replaced by a block cross-fitted version: within-day flicker makes g anti-correlated, and the iid version was biased negative (talk ≈ −0.007/bin).
  - The whole-swarm EP null was changed from circular shifts to the cross-day surrogate.
  - The cross-fitted Newton bound was added.
- 2026-10-03: **Confirm-script amendments after a non-holdout dry run**, recorded in the script's `PREDICTIONS`:
  - the C4 EP CI uses a delete-one-day jackknife (a day bootstrap duplicates days across folds);
  - the C5 "J_in unchanged" criterion became a difference CI including 0 (the ratio is unstable when J_in(pre) ≈ 0).
  - The script stores a hash of this card's prediction sections with its results.
- 2026-10-03: **Power warning for confirmation.** The NE15 window has ~27 cut pairs and 5 post days, and V4 suggests ≈ 25–60% power for a single-event test. The pooled TWFE (C3) is the better-powered test. C4 (EP) is effectively uninformative at this sampling.
- **Next steps.**
  1. Sign off and run `confirm_ne12.py --confirm`.
  2. Raise signal: event-time reply observables (Hawkes, model 09) and the shared `exposure` table (who could see whom) instead of 1-min activity.
  3. Run EP on action-class or talk-reply states, pooled over longer windows.
  4. Blind partition recovery (community detection on talk J) for G = 2.
  5. Add per-room time-of-day fields to separate room-specific goals/kickoffs from coupling.
  6. Same-lab vs. same-room pairs (D9.2).
  7. Find out why added pairs' *activity* coupling fell in the shared-objective merge week (#40).
- Proposed DEFINITIONS.md variant (not added; shared file): **Entropy production (pairwise AIK bound on activity spins):** Σ_g from g_ij = s_i(t+1)s_j(t) − s_i(t)s_j(t+1) on 1-min ±1 activity spins, cross-fitted or held-out by day, per agent-hour; null = cross-day surrogate.

## Round 2 redirects (2026-10-04)
*From the round-1 reflection (`writeup/round1-reflection/round1-reflection.pdf`).*
- **Where round 1 went sideways:** "Rooms decouple chat" is close to the scaffold's definition of a room, and entropy production on 1-min spins measured nothing.
- **What the direction is really after:** Through which channels does information actually move?
- **H05-R1.** Rooms matter only insofar as they also split artifacts: cross-room pairs sharing a repo stay coupled through edits (E3).
- **H05-R2.** The ×6 rise in within-room coupling after the split is attention reallocation, predicted in size by N_room^-0.6 (E5).
- **H05-R3.** Information leaks across rooms through history search and artifacts at a measurable rate (a leak conductance).
