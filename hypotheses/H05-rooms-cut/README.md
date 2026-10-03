# H05: Cutting the cross-room channel lowers entropy production, and rooms become coupled blocks

**Status:** specified; exploratory round 1 (non-holdout) below. Confirmatory NE12/NE15 script written, **not run**.
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
1. **Entropy production (pairwise AIK bound on activity spins), Σ_g.** Observables g_ij(t) = s_i(t+1)s_j(t) − s_i(t)s_j(t+1) for i < j (antisymmetric under time reversal; parallel form). Σ_g = max_θ θ·⟨g⟩ − ln⟨e^{−θ·g}⟩ (forward samples only, since g is antisymmetric). θ is fitted on training days and Σ_g is **evaluated on held-out days** (day-blocked K-fold, nested λ choice for an L2 penalty). Reported per bin, **per agent-hour** (×60/N) and per pair-hour (×60/#pairs). Only transitions within a day are used.
2. **Inferred antisymmetric couplings** θ_ij ≈ J_ij − J_ji (from the same fit).
3. **Pair irreversibility** Σ_ij: the same bound for a single pair. Pair-day version: the bias-corrected Gaussian (Newton-step) form 2(ḡ² − s²/T)/s².
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

(Filled after round 1; see Results.)

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

## Results
(Filled after analysis.)

## Notes
- 2026-10-03: card opened (one of five parallel agents). Holdout masked via `calendar.holdout` and `holdout.json`.
