# H76: Excess vs housekeeping irreversibility

**Status:** exploratory round 1 **done (2026-10-04): behavioral excess irreversibility is the scheduler's day end; kickoffs and housekeeping are below the detection floor.** Card, observables and predictions written ~19:20 UTC before any real-data statistic; amendments A1 (after the synthetic) and A2 (after the first real-data pass) dated below.
- **Edges (P2, 3/3 periods):** 80–100% of the debiased excess EP of the behavior mix falls in the day's first and last 30 min (G51 0.80 [0.73, 0.90], G38 0.94 [0.82, 1.07], G40 1.00 [0.97, 1.06]) against a 12–25% time share. The final block alone carries 72–100%; the start block carries 0–8%. The runner starts agents together; they stop at staggered times.
- **Trimming (P3a, 3/3):** the DQ8 all-present trim removes 81–100% of the excess. **P3b failed:** it also removes 57–64% of the housekeeping (vs 28–30% of the agent-steps), but every housekeeping CI spans 0.
- **Kickoff (P1, 0/3):** the kickoff's 2-h excess is not above the ordinary day starts (rank 0.06, 0.85, 0.33). The synthetic had shown this is the model's expected outcome: excess scales as 1/T, and a 5-h field relaxation adds less excess per step than the scheduler's day-start transient.
- **Housekeeping (P4):** not separable from the block-flip floor at N 12–27 with soft labels (synthetic attenuation ×0.19).
- **Natives:** NE41 mixed (forced erasure = a one-window excess pulse ×12 [6, 27] in G51 and ×5 [3, 10] in G38, mostly the consolidation gap read as "absent"); NE43 failed (edge excess ×0.34 in the week after the bookends stop, below the placebo range, recovering the next week).
- Replication verdicts: 3 mixed (P2 and P3a hold, P3b fails). Scorecard A1 B1 C1 D1 E1 F1 G1 H1 I1. `confirm.py` (transfer to #45–#47, NE21 hours ABAB) written and frozen; **not run**.
**Fields:** thermodynamics (stochastic), stat mech, info theory
**Literature:** [Kolchinsky, Dechant, Yoshimura & Ito 2026](../../literature/kolchinsky-2026-generalized-free-energy-excess-housekeeping.md) (excess/housekeeping decomposition, Eq. 38; speed limits; copies at fixed time); [Aguilera, Ito & Kolchinsky 2026](../../literature/aguilera-2026-entropy-production-nonequilibrium-maxent.md) (EP as statistical irreversibility of observables).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Population N(t) (variant *active population*: agents with v3 rows that day); Regime; Driving / external field (kickoff; the scheduler's day edges); Agent state, variant *categorical* (Jev v3 behavior states, soft); Entropy production / irreversibility, in a new named variant **entropy production (ensemble flux, plug-in)**; H38's scheduler trimming in its DQ8 form (`nulls.all_present_window`). New named variants proposed for DEFINITIONS.md (not edited there; defined under "Operational definitions"): **ensemble flux j_xy**, **excess EP σ_ex (Kolchinsky gradient part)**, **housekeeping EP σ_hk**, **excess share**, **edge share**, **trim removal**.
**From:** HH324 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` ("From the thermodynamics and origins-of-life notes") · **Models:** `physics-models/02-nonequilibrium-ising/`, `physics-models/05-replicator-dissipation/`
**Data inputs (shared tables first):** DQ3 `behavior_states_v3` (soft vectors `p_*`, `active`, `in_span`, `labeled`, `holdout`), `calendar`, `period_units`, `embeddings/goals.parquet` (kickoff `win_start`), `context_ledger_turns` (`reset_forced`, `reset_consol`), `kicks_classified` (bookend dates, check only), `infra/shared/nulls.py: all_present_window`. No text.

## Source HH (verbatim from the HH list)
Excess/housekeeping split of behavioral irreversibility. Use ensemble fluxes over the 4–32 agents of a period on `behavior_states_v3` (≥ 3 states). Excess is net occupancy change, estimable from short-time increments without a steady state.
  - *Predictions:*
    - Kickoffs: excess share ≥ 0.3 in the first 2 active hours, decaying on the H48/H54 timescale. Ordinary day starts are the placebo.
    - Day edges: ≥ 60% of a day's excess falls in the schedule's first and last 30 min.
    - DQ8 trimming removes ≥ 70% of excess but < 20% of housekeeping.
    - Housekeeping is ≈ the stationary work cycle, consistent with H14.
  - *Use:* a per-period gauge of the scheduler field, alongside HH310's Taylor c.
  - *Kill:* the split does not respond to kickoffs or trimming.
  - *Models:* 02, 05 · *Builds on:* H14, H38, H54, HH310 · *Literature:* Kolchinsky et al. 2026, Aguilera et al. 2026

## Question
How much of the swarm's behavioral irreversibility is net change of the behavior mix (excess: kickoffs, the scheduler's day edges) and how much is stationary cycling with no net change (housekeeping: the per-call work cycle)? Does the split respond to the drives that should move it?

## Design: two layers
- **Replication:** the common estimator on G51 (45 non-holdout days, N 21–32, 8-h days), G38 (17 days, N 12–14, two rooms) and G40 (5 days, N 15, one room). Period README role: `replication`.
- **Natives (2):** NE43 (G51, the operator bookends stop after 08-04: a change in the day-edge drive) and NE41 (forced context erasures at the 41-turn cap, scaffold-timed: event-aligned copies). Role: `native`.
- **Confirmation:** `analysis/confirm.py` (NE21 hours ABAB, transfer to #45–#47); written and frozen, not run.

## Model
**From:** `physics-models/02-nonequilibrium-ising` (kinetic Markov jump process on categorical agent states; mean-field over exchangeable agents) and `physics-models/05-replicator-dissipation` (a driven population distribution and its dissipation).

**H76 variant: Kolchinsky's excess/housekeeping split on a mean-field master equation of behavior states.** The agents of one period are exchangeable copies of a Markov chain on behavior states x (5-min windows). The ensemble flux in a time block b is j_xy = (1/(N_b K_b)) Σ_{i,t∈b} p_{i,t}(x) p_{i,t+1}(y), the soft transition count per agent-step, and ṗ_x = Σ_y (j_yx − j_xy). Then (Kolchinsky et al. 2026, Eqs. 38 ff.):
- **total EP** σ = Σ_{x<y} (j_xy − j_yx) ln(j_xy / j_yx);
- **excess EP** σ_ex = max_φ [ −Σ_x φ_x ṗ_x − Σ_{x≠y} j_xy (e^{φ_y − φ_x} − 1) ]: the irreversibility of the net occupancy change alone (0 iff ṗ = 0); in linear response σ_ex ≈ ṗᵀH⁺ṗ with H = ½∇ᵀdiag(j)∇;
- **housekeeping EP** σ_hk = σ − σ_ex ≥ 0: carried by cyclic currents that change nothing; it needs ≥ 3 states (a cycle).

Units: nats per agent per 5-min step (× 12 = per agent-hour). No temperature and no heat: σ is statistical irreversibility. Tokens are not heat.

**Village mapping (from the literature note, which corrects HH324's framing):**
- **Kickoff** = a field quench: the behavior mix shifts (planning, coordination) and relaxes over hours. That shift is excess.
- **Scheduler day edges** = excess, not housekeeping: at the runner's start and stop, agents switch between absent and active within seconds. That is a net occupancy change. Only trimming to the all-present window removes it.
- **Per-call work cycle** (execute → verify → research → …) = housekeeping: stationary cyclic currents.
- **Copies.** Excess cannot be time-averaged on one trajectory. The copies are the agents of a period at a fixed time (or the same-type events of NE41).

**State spaces (fixed before the run).**
- **Coarse (primary, 5 states):** absent (no record in the window, in or out of the agent's daily span) · work {execute_task, debug_recover, verify_report} · explore {research_browse} · coord {plan_coordinate, communicate_external, social, meta} · wait {monitor_wait, idle, self_maintenance}. Soft vector = sums of the v3 `p_*` within each group.
- **Fine (secondary, 12 states):** the 11 v3 states plus absent.
Lumping states is not covered by Kolchinsky's merging invariance; it lowers σ. Both are reported.

## Data scheme (`scheme/build.py`)
- **Inputs:** `behavior_states_v3` (non-holdout rows; all windows of each agent-day grid, w = 0 … n−1 from the day's `win_start`), `calendar`, `goals.parquet`, `context_ledger_turns`.
- **Transform:**
  1. Per agent-day, the window sequence of soft state vectors (absent = one-hot when `active` is false or `labeled` is false).
  2. Transitions w → w+1 within a day only (no overnight transitions).
  3. **Trimmed grid:** windows inside `nulls.all_present_window` (every agent present that day is within its daily span); a transition is kept if both windows are inside.
  4. **Blocks:** 30-min blocks (6 steps) aligned to the day start; the last block of the day is aligned to the day end (the edge blocks are the first and last 6 steps); the remainder sits in the middle. For the kickoff statistic, one 2-active-hour block (24 steps).
  5. Per block: the summed soft flux matrix; pseudocount α = 0.1 per directed edge per block (sensitivity α = 0.5).
- **Output:** `data/processed/H76-excess-housekeeping-split/<G..>/blocks.parquet` (block id, day, grid, state space, steps, N, σ, σ_ex, σ_hk, surrogate floors), `results.json`; `synthetic/`; `_provenance.json`. Expected < 20 MB.
- **Regimes covered:** regime III (G38, G40, G51 head). No pooling across periods.

## Operational definitions (written 2026-10-04, before any real-data run)
- **Estimator.** σ, σ_ex (Eq. 38 by Newton's method on φ, φ_absent = 0) and σ_hk on each block's mean flux. Block averaging is a coarse-graining in time: by joint convexity, the block's σ_ex is a lower bound on the mean of per-step σ_ex.
- **Reversible-surrogate floor.** Within a block, each agent-step's outer product p_t ⊗ p_{t+1} is transposed with probability ½ (20 surrogates). The surrogate keeps the symmetric part and the activity and has ṗ = 0 and σ = 0 in expectation. **Debiased** σ, σ_ex, σ_hk = raw minus the surrogate mean (not clipped, so noise averages out across blocks).
- **Excess share** = Σ_b σ_ex,b K_b / Σ_b σ_b K_b over the blocks of a window (debiased numerator and denominator).
- **Kickoff excess** = debiased σ_ex of the first 2 active hours of the kickoff day, trimmed grid, as one block. **Day-start placebo** = the same on every other non-holdout day of the period.
- **Kickoff decay.** Debiased σ_ex in 1-active-hour blocks (trimmed grid) from the kickoff through 20 active hours, fitted by σ_ex(t) = c + A e^{−t/τ} (τ in active hours).
- **Edge share** (per non-kickoff day, untrimmed grid) = (σ_ex of the first and last 6 steps) / σ_ex of the whole day, all debiased. The edge blocks are 12 of the day's ~48 (4-h) or ~96 (8-h) steps.
- **Trim removal** (per non-kickoff day) = 1 − (day total on the trimmed grid) / (day total on the untrimmed grid), for σ_ex and for σ_hk; totals = Σ_b σ_b K_b.
- **Housekeeping share** = σ_hk/σ on the trimmed grid of non-kickoff days.
- **Uncertainty:** agent bootstrap (B = 100; agents are the copies), percentile intervals; day-level statistics as medians over days with a bootstrap over days.

## Observables
1. Kickoff excess and excess share (first 2 h), the day-start placebo distribution, the decay τ.
2. Per-day edge share of σ_ex (untrimmed).
3. Per-day trim removal for σ_ex and σ_hk.
4. Housekeeping share and level on trimmed non-kickoff days; comparison with H14's pooled v3 EP (G38 0.0069, G40 0.0026, G51 0.0118 nats per transition; a Newton lower bound on the fine states).
5. Native statistics (below).

## Null / baseline
- **Reversible surrogate** (per block, above): the floor for every EP number.
- **Day-start placebo** for the kickoff (the scheduler field acts at every day start).
- **Uniform-time baseline** for the edge share: the edge steps' share of the day's steps (≈ 0.25 at 4 h, 0.125 at 8 h).
- **Synthetic calibration** (axis F, below).

## Native tests
- **N1 · NE43 (G51; the operator's daily pause/resume bookends stop after 2026-08-04 PT).** Design as H14's NE43 native: the active days within 7 calendar days before the boundary (07-29 … 08-04) vs within 7 calendar days after it (08-05 … 08-11); placebo boundaries 07-13, 07-20, 07-27, 08-12 with the same windows (none straddles 08-05 or the 08-21 nudger-off step). Observables: change in the daily edge σ_ex (untrimmed) and in daily σ_hk (trimmed), each as after/before ratio of medians. H49 found the edge-induced activity excess persists at ×0.77 after the bookends stop (the drive is the runner's schedule).
- **N2 · NE41 (forced erasures; G51 and G38, each period separately).** Copies = forced erasures (`context_ledger_turns.reset_forced`, non-holdout) not within 3 windows of another reset and not in the first or last 3 windows of a day. For each, the window e containing the reset; ensemble fluxes at relative steps (e−2 → e−1), (e−1 → e), (e → e+1), (e+1 → e+2) across all copies. Placebo copies: the same agents at windows ≥ 6 windows from any reset (forced or voluntary), matched on day and time of day (one placebo per copy, nearest eligible window). Known issues 66 and 71: v3 labels post-reset windows as more executing, and a window-level burn-in manufactures irreversibility; this design uses no burn-in.
- **Considered and not used:** NE21 hours ABAB and NE23 nudger off/on (holdout; `confirm.py`); G44's room split (4 agents in #best: copies too few for a 5-state flux per block).

## Synthetic validation plan (axis F; `analysis/synthetic.py`)
A 5-state mean-field master equation sampled like the village: N = 15 (5 days × 48 steps) and N = 25 (10 days × 96 steps); soft labels drawn with v3's confidence distribution (median 0.75; absent observed exactly). Dynamics: a stationary rate matrix with a driven cycle work → explore → coord → work (housekeeping); mid-day pauses (absent); day edges with agents starting and stopping within the first and last windows (staggered, mean 4 min); a kickoff field that shifts occupancy toward coord and relaxes with τ = 5 active h; three scenarios with the kickoff amplitude set to 0, moderate and large. Truth = the same estimator on N = 3,000 agents with hard labels. Pass: (i) the debiased excess share, edge share and trim removal recovered within ±0.1 (absolute) of truth; (ii) σ_hk recovered with a stated attenuation factor from soft labels; (iii) under zero kickoff amplitude, the kickoff/day-start ratio exceeds 2 in ≤ 10% of replicates (size); (iv) the power to detect the moderate kickoff (ratio ≥ 2) is reported. The predictions below are read against what the synthetic says is detectable.

## Synthetic validation results (2026-10-04 ~20:00 UTC; `analysis/synthetic.py`, `data/processed/H76-excess-housekeeping-split/synthetic/summary.parquet`)
Two designs: N 15 × 5 days × 4 h (30 replicates, G40-like) and N 25 × 10 days × 8 h (12 replicates, a quarter of G51). Three kickoff scenarios: null (h = 0), slow (h = 2, τ = 5 h) and fast (h = 2, τ = 30 min). "Population" = N = 3,000, hard labels, no late starters. Coarse states, debiased, pooled over days.

| Statistic | Population | N 25 × 10 d, soft (mean ± SD) | N 15 × 5 d, soft |
| --- | --- | --- | --- |
| kickoff/day-start σ_ex ratio: null · slow · fast | 1.08 · 0.65–0.73 · 1.6–1.7 | (median ≈ 0 after debiasing: ratio undefined) | same |
| kickoff excess share (2 h): null · slow · fast | 0.05 · 0.02 · 0.07 | 0.00 ± 0.23 · −0.05 ± 0.40 · 0.12 ± 0.23 | −0.15 ± 0.58 · 0.01 ± 0.15 · 0.02 ± 0.16 |
| P(kickoff above every day start and share ≥ 0.3): null · fast | — | 0.00 · 0.17 | 0.10 · 0.17 |
| decay τ (h) | 0.25 (grid floor) | 15–23 ± 18 | 14–18 ± 19 |
| edge share of σ_ex (untrimmed) | 1.00 | 1.11 ± 0.50 | 1.5 ± 2.8 |
| trim removal σ_ex | — (no late starters) | 1.05 ± 0.64 (hard 1.13 ± 0.59) | 1.35 ± 4.9 |
| trim removal σ_hk (steps removed) | — | 0.21 ± 0.20 (hard 0.11 ± 0.19; steps 0.13) | −1.2 ± 7.7 (steps 0.21) |
| housekeeping share σ_hk/σ (trimmed) | 0.95 | 1.01 ± 0.14 | 0.53 ± 1.26 |
| σ_hk per agent-step (nats) | 0.029 | 0.0054 ± 0.0015 (hard 0.034) | 0.0029 ± 0.0046 |

- **Kickoff (P1, P1b) is not identifiable under this model.** Excess scales as 1/T under slow driving: a 5-h relaxation adds less excess per step than the scheduler's own day-start transient (population ratio 0.65–0.73). Even a 30-min quench gives a population ratio of only 1.6, and the test detects it in 17% of replicates. The decay time is not recoverable.
- **Edges and trimming (P2, P3) are recoverable at G51 scale and not at G40 scale.** The population puts all excess in the edge blocks; at N 25 × 10 days the pooled edge share is 1.11 ± 0.50 and the excess removal is ≈ 1. At N 15 × 5 days the SD exceeds 2.
- **Housekeeping (P4).** The share σ_hk/σ ≈ 1 is recovered at G51 scale. Soft labels attenuate the housekeeping level by ×0.19 (0.0054 vs 0.029), so absolute levels are lower bounds. Trimming lowers σ_hk by about the share of steps it removes.
- **Pass criteria:** (i) shares within ±0.1: **failed** at both sizes for single replicates (SD 0.2–0.5 at N 25 × 10 d); (ii) σ_hk attenuation stated: ×0.19; (iii) size of the kickoff test ≤ 0.10: passed (0.00–0.10); (iv) power for the moderate (slow) kickoff: 0.0–0.07.

## Amendments (dated; what had been seen)
- **A1 (2026-10-04 ~20:05 UTC, after the synthetic run, before any real-data statistic).**
  1. The reversible surrogate is a **per-agent block flip** (each agent's whole block flux is transposed with probability ½), not a per-step transposition. The per-step version broke each agent's telescoping net change and overstated the excess floor (debiased σ_ex came out negative in the first synthetic run).
  2. Day-level ratios are **pooled over days** (Σ numerators / Σ denominators over the period's non-kickoff days) as the primary statistic; per-day medians are secondary. Debiased day totals sit near 0 on many days, so per-day ratios are unstable.
  3. **Kickoff test:** the kickoff's 2-h σ_ex lies above every day-start placebo of the period (rank test; size 1/(days)), with share ≥ 0.3. The ratio to the median day start is reported but not used, because the debiased median is ≈ 0.
  4. **Identification:** P1 and P1b are not identifiable at village N under the model (above). A failed P1 is the model's expected outcome and does not count against the decomposition; the verdict rule's "P1 undetectable" branch applies. G40's P2/P3 are scored n/a unless its agent-bootstrap CI excludes the opposite verdict.
  5. P3's σ_hk criterion is read against the share of steps that trimming removes (σ_hk removal ≤ steps removed + 0.1 counts as "housekeeping kept").
- **A2 (2026-10-04 ~20:45 UTC, after the first real-data pass on G51, G38, G40; predictions unchanged).** (i) **Bootstrap floor bug fixed:** the agent bootstrap reused the full-sample surrogate floor; duplicated agents raise the plug-in bias, so the floor under-corrected and the CIs missed their own point estimates (G51 edge share 0.87 with CI [0.46, 0.64]). Each bootstrap replicate now recomputes the block-flip floor on its weighted sample (5 surrogates). (ii) Days whose all-present window is empty (11 of 44 in G51) were dropped from every day statistic; they now enter the untrimmed statistics (edge share, NE43) and are excluded only from the paired trimmed/untrimmed ratios. (iii) Each period gets its own random seed: the surrogate Monte Carlo noise moved G38's σ_hk removal from 0.74 to 0.58 between runs, which shows that housekeeping sits at the noise floor. (iv) **NE41 placebo:** the first placebo (windows ≥ 6 from any reset) was 79% "absent" windows, i.e. idle agents. Placebos must now have the agent present at p−2 … p+2. The exclusion radius is 3 windows, because a working agent is almost never 30 min from a reset (G51 107 placebos at radius 6, G38 0). (v) NE43's housekeeping uses the trimmed grid as planned; the untrimmed version is reported as secondary.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R1 scheduler-only (all excess sits at the day edges; kickoffs add nothing beyond a day start); R2 Hatano–Sasa reading (excess = lag behind an instantaneous steady state; not estimable here; noted, not fitted); R3 label noise (soft-label noise produces symmetric flux only and no structure).
**Locked holdout used for confirmation:** none yet. `analysis/confirm.py` (transfer to #45–#47, NE21 hours ABAB) written and frozen; not run.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | States from the shared v3 labels (soft vectors; absent = no record), copies = the agents present that day, 5-min Markov steps within a day; assumptions listed (exchangeable copies, even state variables, soft-label independence). One labeller only (Jev v3): "absent" also catches the consolidation gap (NE41), so the mapping is not scaffold-invariant. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Markov at 5 min and stationarity within 30-min blocks assumed, not tested; block averaging lower-bounds σ_ex (joint convexity). Pseudocount α 0.1 vs 0.5 changes the edge and excess-trim shares by ≤ 0.02; housekeeping numbers move by up to 0.2 (G38 σ_hk removal 0.57 → 0.38), at the noise level. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Excess at the edges beats the block-flip reversible surrogate in 3/3 periods (edge-share CIs exclude the uniform-time share); housekeeping and the kickoff do not beat it. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | P2 and P3a held as written (3/3); the end-of-day concentration (72–100% in the final block) was not predicted. P1 failed, as the synthetic said it would; P3b and P4 failed or were unresolved. |
| E interventional | predicts the change across a natural experiment | 1 | NE41 (scaffold-timed erasure): predicted one-window excess pulse, found (×5–12), but it is mostly the consolidation gap. NE43: failed its pre-set rule (a one-week dip in edge excess). Holdout NE21 not run. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Synthetic 5-state master equation at village sampling: edges and trimming recoverable at G51 scale (SD ≈ 0.5 at 10 days) but not at G40 scale; kickoff not identifiable (population ratio < 2 even for a 30-min quench); housekeeping attenuated ×0.19 by soft labels and noisy. Estimator checks: 2-state σ_ex = σ, pure cycle σ_ex = 0, linear-response limit matched. |
| G ground truth | agrees with known structure | 1 | Agrees with H38/H50 (scheduler edges carry the activity co-movement) and H44 (the forced erasure is a multi-minute gap). No direct ground truth for behavior irreversibility. |
| H comparative | beats the named rivals | 1 | R3 (label noise only) is rejected for the excess, not for housekeeping. R1 (scheduler only) is not rejected: kickoffs add nothing beyond day starts. R2 (Hatano–Sasa) not estimable. |
| I transfer | holds in other same-mode periods, including the holdout | 1 | Edge and trim results hold in 3/3 regime-III periods of different size (N 12–27, 4-h and 8-h days). Holdout not run. |

## Prediction
*Written 2026-10-04 ~19:20 UTC, before running the analysis on real data. What I had seen: per-goal window counts of `behavior_states_v3`, its column semantics and confidence distribution (structure only); H14's v3 pooled EP table; H38/H49 edge results. No flux or EP number.*
- **P1 (kickoff, primary).** In each replication period, the kickoff's debiased excess share in the first 2 active hours (trimmed, coarse) is ≥ 0.3, and the kickoff σ_ex is ≥ 2× the median day-start placebo. *Against:* the ratio is inside the placebo range. Credence 0.35 (the synthetic may show that a 5-h relaxation carries too little excess per step to see at N ≈ 15).
- **P1b (decay).** Where P1 holds, the fitted τ lies in [2.5, 10] active h. Credence 0.3.
- **P2 (edges, primary).** The median non-kickoff day has ≥ 60% of its debiased σ_ex (untrimmed, coarse) in the first and last 30 min, in every replication period. *Against:* edge share ≤ 2× the edge steps' time share. Credence 0.7.
- **P3 (trimming, primary).** Trimming removes ≥ 70% of the day's σ_ex and < 20% of its σ_hk (median day, coarse), in every replication period. *Against:* σ_ex removal < 50%, or σ_hk removal > 40%. Credence 0.5 (trimming also removes time, so σ_hk falls with the trimmed share of the day).
- **P4 (housekeeping).** On trimmed non-kickoff days, σ_hk/σ ≥ 0.7, and the fine-state σ_hk per transition is within ×[0.3, 10] of H14's pooled v3 EP for the period. Credence 0.5.
- **N1 (NE43).** The after/before ratio of the daily edge σ_ex and of the daily σ_hk both lie inside the placebo range (min–max). *Against:* edge σ_ex falls below the placebo minimum (the bookends were the edge drive). Credence 0.6.
- **N2 (NE41).** At the reset steps (e−1 → e and e → e+1), σ_ex of the event-aligned ensemble is ≥ 2× the placebo copies' σ_ex, while σ_hk is within ×[0.5, 2] of the placebo's. Credence 0.45.
- **Per-period verdict rule (replication):** supported if P2 and P3 hold and P1 holds or is shown undetectable by the synthetic (then "mixed" if P1 fails while detectable); failed if P2 and P3 both fail; mixed otherwise.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | mixed | N 12, 16 days; edge share 0.94 [0.82, 1.07] (end block 0.93); trim removes σ_ex 1.00, σ_hk 0.57 (steps 0.28); kickoff rank 0.85 |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | mixed | N 15, 4 days; edge share 1.00 [0.97, 1.06]; trim removes σ_ex 1.00, σ_hk 0.64 (steps 0.28); kickoff rank 0.33 |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication | mixed | N 27, 44 days; edge share 0.80 [0.73, 0.90] (end 0.72, start 0.08); trim removes σ_ex 0.81 [0.69, 0.90], σ_hk 0.60 (steps 0.30); kickoff rank 0.06 |
| [NE41](goalperiod-subhypotheses/NE41/README.md) | native | mixed | forced erasure: σ_ex ×12.1 [6.2, 27] (G51, 2,989 copies), ×5.2 [2.8, 10] (G38); σ_hk ×1.31 / ×0.38; pulse = consolidation gap, gone one window later |
| [NE43](goalperiod-subhypotheses/NE43/README.md) | native | failed | edge σ_ex ×0.34 after 08-05 (placebo 0.73–2.51), recovers the next week; σ_hk ×1.44 (placebo 0.47–1.54) |

## Results
### Exploratory round 1 (2026-10-04; `scheme/build.py`, `analysis/run.py`, `analysis/synthetic.py`)
Numbers: `data/processed/H76-excess-housekeeping-split/results/summary.json`, `G<NN>/results.json`, `NE41/`, `NE43/`, `synthetic/summary.parquet`. Figures: `figures/summary_obs.pdf` (excess and housekeeping along the day; shares with CIs), `figures/synthetic_ne41.pdf` (synthetic recovery; NE41 pulse).

**Outcome vs prediction**
| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 kickoff above every day start, share ≥ 0.3 | rank 0.06 (G51), 0.85 (G38), 0.33 (G40); share n/a, 0.21, n/a | failed (expected: not identifiable, A1) |
| P1b decay τ in [2.5, 10] h | point τ 4.7, 4.5, 2.2 h; bootstrap spans the grid (0.25–40 h) | not identified |
| P2 edge share ≥ 0.6 | 0.80 [0.73, 0.90], 0.94 [0.82, 1.07], 1.00 [0.97, 1.06]; time share 0.12–0.25 | **supported (3/3)** |
| P3a trim removes ≥ 70% of σ_ex | 0.81 [0.69, 0.90], 1.00 [0.90, 1.09], 1.00 [0.93, 1.06] | **supported (3/3)** |
| P3b σ_hk removal ≤ steps removed + 0.1 | 0.60 / 0.57 / 0.64 vs steps 0.30 / 0.28 / 0.28; CIs span [−3, 15] | failed (unresolved) |
| P4 σ_hk/σ ≥ 0.7; fine σ_hk within ×[0.3, 10] of H14 | coarse 0.33 / 0.94 / 1.07 (CIs span 0); fine ×0.24 / ×0.04 / < 0 | failed (unresolved) |
| N1 NE43 inside the placebo range | edge ×0.34 (range 0.73–2.51); σ_hk ×1.44 (0.47–1.54) | failed |
| N2 NE41 σ_ex ≥ 2× placebo, σ_hk within ×[0.5, 2] | G51 ×12 and ×1.31 (pass); G38 ×5.2 and ×0.38 (fail) | mixed |

**What it means.**
1. *The scheduler's day end is the swarm's excess irreversibility.* In the Kolchinsky split, the net change of the behavior mix in an ordinary day is the shutdown: agents stop at staggered times and the "absent" occupancy rises in the last 30 min (72–100% of the excess sits in the final block, 7–12× its share of the day's steps). The start is synchronized to within the first window, so it carries little (0–8%). This is the behavioral counterpart of H38/H50's finding that day edges carry the activity co-movement.
2. *Trimming is the right correction for excess, not for everything.* The all-present trim removes 81–100% of the excess. It also removes about 60% of the debiased housekeeping, twice its share of agent-steps, but that number is at the noise floor.
3. *Kickoffs are invisible to the excess.* Excess scales as (thermodynamic length)²/T. A field relaxation over ~5 active hours (H54) adds about 10⁻⁴ nats per agent-step, which is below both the day-start transient and the floor. The synthetic showed this before the run. A quench is visible in content (H54) and repo allocation (H75: an instant freeze) but not in the 5-min behavior mix.
4. *Housekeeping needs more copies or harder labels.* The cyclic part of behavioral irreversibility (the per-call work cycle) is real in single-agent fine-action chains (H14) but does not separate from a reversible surrogate in 30-min ensemble blocks of 12–27 agents with soft labels.
5. *Forced erasures are a one-window excess pulse.* It is mostly the consolidation gap: v3 has no record in that window and labels it "absent". The behavior mix is back at baseline one window later.

## Confirmatory predictions (C-*): for the locked holdout, frozen 2026-10-04 after round 1, not run (`analysis/confirm.py`)
- **C1:** pooled edge share of σ_ex ≥ 0.6 in each of #45, #46, #47.
- **C2:** trimming removes ≥ 70% of σ_ex in each.
- **C3:** the final 30-min block holds ≥ 50% of the day's σ_ex in ≥ 2 of 3.
- **C4:** the kickoff's 2-h σ_ex is not above every day start in ≥ 2 of 3 (the expected null).
- **C5 (NE21 hours ABAB, inside the NE21+NE23 window):** the median daily edge excess per agent on 8-h days / 4-h days lies in [0.5, 2]. The edge excess is a per-day cost, not a per-hour one.
- Reuse: H14's planned confirm uses pooled v3 EP on the same targets (same estimator family, `entropy_production`); the script calls `holdout_ledger.check` and stops on a same-family conflict. The coordinator decides.

## Round 2 redirects
**What the direction is really after:** a per-period gauge of the scheduler's field, and a measured split of behavioral irreversibility into net change of the behavior mix and stationary cycling.
- **H76-R1. Excess on the stop schedule.** Regress each day's end-block excess on the spread of agents' last-call times (`call_windows`), to show the excess is the staggered shutdown and to give operators a number (nats per minute of stop spread).
- **H76-R2. Housekeeping with hard states.** Repeat on the fine action classes of H14 (turn-level, shell sub-classes), where single-agent arrows are 0.04–0.15 nats per transition, with ensemble fluxes per 30 min. The soft-label attenuation (×0.19) is the main obstacle here.
- **H76-R3. Kickoff excess at turn resolution.** Repeat P1 at 1-min steps on H75's repo allocation or on project labels, where a quench is fast (minutes), not on 5-min behavior mixes.
- **H76-R4. Remove the consolidation gap.** Mark consolidation windows as their own state (not "absent") and rerun NE41. This tests whether any behavioral pulse remains after a forced erasure.
- **H76-R5. Run confirm.py** after the coordinator settles the H14 overlap.

## Notes
- 2026-10-04: compute limits: ≤ 2 threads per process, no sub-agents, no network. The full run takes ~70 s (agent bootstrap with per-replicate floors).
- 2026-10-04: `activity_bins` is not used. v3 windows come from DQ3 (built on raw events), and the trim uses v3's own `in_span`. So the DQ8 event-drop bug does not affect H76; the DQ8 trimming rule is applied as `nulls.all_present_window` semantics on v3 spans.
- 2026-10-04: processed data 0.4 MB.
