# H117: J should not move when the rules do: the mid-goal reset in #32 (NE35)

**Status:** exploratory round 1 **done (2026-10-04): mixed.** Card and predictions 22:03 UTC; Amendments 0–1 (structural, synthetic) 22:43 UTC; real-data run 22:43–22:44 UTC. `analysis/confirm.py` frozen and dry-run, **not run**.
- **J stays put at field steps, but the field rarely moves beyond day-to-day changes.** At 8 of 9 non-holdout steps the talk-spin coupling matrix (KI-5, block fields) moves no more than across placebo day boundaries (Q placebo p 0.07–0.96). The exception is NE17 (outreach approval; 6 agents, 7 pairs: Q 1.54, p 0.037), where talk rates did not shift, so it is not the field-artifact signature.
- **The one clean field step is the #41 → #42 goal switch (G42):** F p 0.037, Q 0.51 (p 0.74). This rules out rewiring of ±1.2 logistic units on half the pairs (synthetic power 0.85), not smaller changes.
- **Natives:** NE38 supported (the reassigned agent's field moves most, Δh̄ z −5.6, rank 1/19, while its couplings rank 5/19); #focus positive control weak (switched-pair Q 0.93 vs fixed 0.61; placebo p 0.11); NE36 mixed (mover not eligible).
- **J is stationary day to day at this resolution:** placebo Q medians (0.60–0.70) equal the synthetic no-change null (0.63–0.73), so R-drift is not seen.
- Kill rule (Q p < 0.05 at ≥ 2 of 7 replication steps) does not fire; "supported" needs ≥ 3 steps with a first stage, and only G42 has one.
**Question (GOALS.md):** **Q2** (what is field and what is coupling: does a fitted kinetic-Ising J stay put when only the field moves?) and **Q1** second (is J a property of who reads whom).
**Fields:** stat mech (kinetic Ising inference, field vs coupling identifiability), dynamics (event study across a field step)
**Literature:** [Aguilera, Ito & Kolchinsky 2026](../../literature/aguilera-2026-entropy-production-nonequilibrium-maxent.md) (directed couplings from lagged statistics). Kinetic-Ising inference by per-spin logistic regression (Roudi & Hertz, PRL 106, 048702, 2011)† is cited in `physics-models/02-nonequilibrium-ising/`. Project cards: H02 (talk-spin couplings transfer across days in regime-III shared weeks; block fields), H38 (scheduler field), H50 (talk is a coupling gated at the recipient's next call), H08 (read-out gating), H40 (call clock in regimes II–III), H90 (common drives with agent-specific lags beat block-shift nulls), H96 (goal switch = quench).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent (Claude Code agent excluded); Regime; Driving / external field; **Interaction (ledger-visible exposure)** and **Unread (in-flight) exposure placebo** (RE-D1); **Exposure (ledger receiving call)**. New named variants proposed (defined under Observables; DEFINITIONS.md not edited): **talk spin (trimmed minute)**, **KI-5 block coupling J^B**, **read-gated call coupling J^R / in-flight coupling J^U**, **coupling-shift statistic Q**, **field-shift statistic F**, **fixed / switched pairs**.
**From:** HH355 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/02-nonequilibrium-ising/` (primary: kinetic Ising on talk spins), `physics-models/01-inverse-ising/` (secondary: the symmetric part of J, as in the HH)
**Data inputs (shared tables first):** `activity_bins_fixed` (talk spins), `calendar`, `period_units`, `roster`, `rooms_timeline` via `infra/shared/rooms_asof.py` (co-location of every pair at every minute), DQ1 `context_ledger_turns` + `call_windows` (call clock, latency) and `chat_core` (message times and rooms; no text), `holdout.json` via `common.holdout_mask`. Shared helpers: `day_matrices.trim_rows` (DQ8 all-present trim), `estimates.write_estimates`. No text is read.

## Source HH (verbatim from the HH list, including refinements)
- **HH355 · J should not move when the rules do: the mid-goal reset in #32 (NE35).** The operator reset a gamed challenge format mid-goal. That changes the field (what agents are trying to do), not who reads whom.
  - *Prediction:* the fitted symmetric J on talk spins agrees across NE35 within its bootstrap CI, while h_i shifts. A fitted J that jumps at a pure field change is a field artifact, not a coupling.
  - *Check:* fit before and after NE35 on matched hours; compare J matrices (Frobenius distance against a split-in-time placebo on other days of #32).
  - *Kill:* J changes more across NE35 than across placebo splits.
  - *Impostors:* this is a direct test of the field impostor for the J estimator itself.
  - *Models:* 02, 01 · *Builds on:* H38, H02

## Question
When only the field changes (a rule reset, a tool or prompt change, a goal switch), does the fitted kinetic-Ising coupling matrix on talk spins stay inside its sampling noise while the fields h_i move? If J moves as much as h, the estimator confuses field with coupling.

## Design: two layers (STANDARDS §4)
**The target, NE35, is held out.** #32 is a locked-holdout goal period and 02-25 lies inside the NE12 window. Exploration therefore never touches it; NE35 is the confirmatory target (`analysis/confirm.py`, frozen, not run). Exploration uses the same estimator on every other documented mid-goal field step with fixed room structure (named exception (c): the transition is the object; each step is fitted on its own two sides).
- **Replication** (role `replication`): the common estimator at every eligible non-holdout mid-goal step (k = 2 active days each side, the two sides in one goal period):
  | Step | Folder | Before | After | What changed | Regime |
  | --- | --- | --- | --- | --- | --- |
  | NE06 | `NE06/` | 2025-11-18, 11-19 | 11-20, 11-21 | Gemini one tool call per turn; village-wide actions per turn halve (RE-C2) | I |
  | NE07 | `NE07/` | 12-02, 12-03 | 12-04, 12-05 | prompt "don't do nothing" (DeepSeek joins 12-04; its pairs drop out by eligibility) | I |
  | NE16 | `NE16/` | 2026-03-24, 03-25 | 03-26, 03-27 | memory-instruction fix (#36) | III |
  | NE17 | `NE17/` | 04-10, 04-13 | 04-14, 04-15 | outreach approval system (#38) | III |
  | NE38 | `NE38/` | 07-27, 07-28 | 07-29, 07-30 | one agent's role reassigned (#51) | III |
  | NE43a | `NE43/` | 08-03, 08-04 | 08-05, 08-06 | daily pause/resume bookends stop (#51); #focus opens the same day | III |
  | NE43b | `NE43/` | 08-18, 08-19 | 08-21, 08-24 | nudger off after 08-20 (#51); #focus closes 08-24 | III |
- **Natives** (role `native`), each with its own dated prediction in its folder:
  - **NE36 / G38** (#37 → #38, 03-31, 04-01 | 04-02, 04-03): the operator correction that opened #38, the closest non-holdout analog of NE35 (an operator correction plus a new task), with one room move on the same day (Claude Sonnet 4.6 #rest → #best). The mover's pairs are a built-in positive control: their adjacency switches while every other pair's does not.
  - **G42** (#41 → #42, 05-14, 05-15 | 05-18, 05-19): a goal switch with fixed rooms and roster, the largest pure field step in the non-holdout data.
  - **NE38 single-agent** (G51): the reassigned agent's own row and column of J against every other agent's.
  - **NE43a #focus** (G51): Gemini 2.5 Pro and Claude Opus 4.8 leave #general on 08-05; their pairs with #general are cut while the field step hits everyone.
- **Placebo pool (the null):** every split at an active-day boundary inside one `period_units` unit of the same regime (no documented step inside the 2k-day window), non-holdout, k = 2, same eligibility rules. Regime I and regime III pools are kept apart.

## Model
**From:** `physics-models/02-nonequilibrium-ising/` (kinetic Ising, parallel update, logistic likelihood), read through its symmetric part (`physics-models/01-inverse-ising/`).
- **E1, KI-5 block (primary; the J that people fit).** Talk spin s_i(t) = +1 if agent i posted chat in minute t (`activity_bins_fixed.state == 4`), else −1, on each day's DQ8 all-present window. For recipient i:
  logit P(s_i(t+1) = +1) = 2[ h_i + δ_i(b) + K_i s_i(t) + K′_i m_i(t) + Σ_{j≠i} J_ij m_j(t) ],
  with m_j(t) the 5-min boxcar mean of s_j over t−4…t (H02's KI-5, matching the ~4-min read-out lag), δ_i(b) a per-agent field for each (day, 30-min block) b, L2 penalty λ = 1 on J, K, K′ and δ (H02's settings; h_i unpenalized). Coefficients are reported in logistic units (2J), as in H02. **Field** of agent i on a side: h̄_i = logit of its talk-minute rate on the trimmed grid (the mean of h_i + δ_i). **Symmetric coupling** J^s_ij = (J_ij + J_ji)/2.
- **E1-naive (secondary).** The same without block fields (constant h_i per side): the estimator most exposed to fields.
- **E2, read-gated call coupling (secondary; per-call clock, H40/H50).** One row per ledger call c of agent i (`context_ledger_turns`, regime II–III): y_c = the call posts chat. Window length L_c = latency_s of the call (call start → first record, H72's rule). R_cj = messages by j in i's room posted in [t_call − L_c, t_call) (visible, in context); U_cj = messages by j posted in [t_call, t_call + L_c) (posted but not yet read when the call's output is produced). logit P(y_c) = δ_i(b) + a_i y_{c−1} + Σ_j [J^R_ij log(1+R_cj) + J^U_ij log(1+U_cj)]. Per-recipient inflow J^R_i = the coefficient on Σ_j log(1+R_cj) (pooled over senders); same for J^U_i.
- **What the model predicts here.** Under a pure field step, h̄_i shifts while J^B, J^s and J^R stay within their sampling noise. Pairs whose adjacency switches (movers, #focus) are the positive control: their J must move.

**Rivals.**
- **R-leak (field artifact):** the fitted J absorbs part of a field change, so J moves with h (predicted for E1-naive; the HH's failure mode).
- **R-task (task-dependent coupling):** coupling strength depends on the task (attention allocated to peers), so J moves at goal switches (NE36, G42) but not at tool or rule changes. Predicts Q(kickoff) > Q(rule step).
- **R-drift:** J drifts day to day, so every split moves; Q at steps ≈ Q at placebos but both ≫ 1. Indistinguishable from invariance by the placebo test; flagged by the Q calibration level.
- **R-dilution (H05, H18):** J depends on room size and attention budget; it moves only when the number of co-located agents changes.

## Data scheme (`scheme/`)
- **Inputs:** listed in the header. Held-out days are dropped with `holdout_mask` and a hard assertion (`calendar.holdout` must agree); the confirm-only switch `ALLOW_HOLDOUT` is set only inside `analysis/confirm.py`.
- **Transform:** `scheme/ki_talk.py` (library: spins, co-location, designs, fitter, statistics) and `scheme/build.py` (per-window tables).
  - Per window day: minute grid = calendar window; trimmed to the all-present window (`day_matrices.trim_rows`, presence = between first and last active minute); talk spin from `activity_bins_fixed`.
  - Eligible agents of a split: present (any activity) on all 2k days, ≥ 10 talk minutes on each side, Claude Code excluded.
  - Co-location a_ij(t) from `rooms_asof` at every minute. **Fixed pair:** co-located in ≥ 95% of kept minutes on both sides. **Switched pair:** co-located ≥ 95% on one side and ≤ 5% on the other. Other pairs are dropped from Q.
  - E2 rows from `context_ledger_turns` ⨝ `call_windows` (latency_s in (0, 600] s) and `chat_core` agent messages.
- **Output:** `data/processed/H117-coupling-invariant-rule-reset/` (`splits.parquet`: one row per step or placebo with Q, D_F, F and counts; `J_<split>.npz`: J, SE, h̄ per side; `synthetic/*.parquet`; `_provenance.json`). Small (< 20 MB).
- **Regimes covered:** I (NE06, NE07, placebos) and III (all other steps, placebos). Regime II has no eligible non-holdout step.

## Observables
1. **Coupling-shift statistic Q** (primary): Q = mean over fixed pairs of (J^s_after − J^s_before)² / (se²_after + se²_before), with cluster-robust (day × 30-min block) SEs from the penalized fit. Q ≈ 1 if J is unchanged and the SEs are right; the placebo pool calibrates it.
2. **Frobenius distance D_F** (the HH's statistic): ‖J^s_after − J^s_before‖_F over fixed pairs, divided by √(number of pairs).
3. **Field-shift statistic F** (first stage): mean over eligible agents of (h̄_after − h̄_before)² / (se²_a + se²_b) (binomial SE of the logit rate, inflated by the block design effect).
4. **Q-naive** (E1-naive) and **Q_R** (E2 per-recipient J^R_i).
5. **Switched-pair Q** (positive control) where switched pairs exist (NE36 mover, NE43a #focus).
6. **Row Q** (NE38 native): Q over the pairs that involve agent k, for each k.

## Null / baseline
- **Placebo splits** (primary): Q, D_F and F at every eligible within-unit day boundary of the same regime and k (pool sizes reported). p = (1 + #{placebo ≥ observed}) / (1 + n_placebo).
- **Same-period placebos** (secondary, the HH's "other days of #32" design): the placebo splits of the step's own goal period, where there are any.
- **Synthetic** (axis F): the real skeleton of each step with planted J and fields (Prediction P0).

## Impostor table (STANDARDS §1)
| Impostor | Relevant? | How it is handled | Status |
| --- | --- | --- | --- |
| Scheduler field | yes | DQ8 all-present trim; per-(day, 30-min block) agent fields δ_i(b); placebo splits share the daily schedule. | removed |
| Exogenous field (goal, operator, rule) | yes: it is the object | The field step is the treatment; block fields absorb it within a side, and the test asks whether J moves when it does. F reports the size of the field step. | removed (by design) |
| Shared model priors (family, style) | weakly | The same agents on both sides; agent constants sit in h_i and cancel in ΔJ. Family-wide responses to a family-specific rule (NE06 hits Gemini) would show as row shifts. | removed |
| Contemporaneous convergence | yes for E1 | E1 uses lagged minutes only, so co-movement from a common drive can enter J. E2 separates read (J^R) from posted-but-unread (J^U) at matched window length; averaging both directions of a pair cancels agent-specific lags (H90). | partly |

## Prediction
*Written 2026-10-04 22:03 UTC, before the synthetic validation and before any H117 statistic on real data.*

**What I had seen when writing this (so these are not blind):** H02 round 1b (talk-spin KI-1 couplings significant in 9.7% of pairs in III-C; held-out transfer in 3/5 III-C chunks), H50 (J₁ > 0 in 45/71 units), H05 (NE42 stay pairs decouple when merged), H96 (goal switches quench content), the `period_units` table, the room-membership timeline for #37–#44 and #51 (who moved when), and the calendar. No talk-spin fit, Q, D_F or F had been computed on any window.

- **P0, synthetic (axis F; run first, real skeletons of NE17, NE38 and NE06).** (a) Under a planted field step (agent-specific Δh ~ N(0, 0.5²) plus a common −0.3, J fixed), the block-estimator Q test at α = 0.05 against the placebo-calibrated threshold rejects in ≤ 10% of worlds [0.6]. (b) Under a planted J step (the symmetric J of 50% of pairs changes by ±0.6 logistic units) power ≥ 0.8 in the #51 skeleton [0.6] and ≥ 0.5 in the #38 and regime-I skeletons [0.45]. (c) E1-naive rejects more often than E1 under the field step when a within-side common drive differs between sides [0.5]. If (b) fails at a skeleton, a non-rejection there is reported as inconclusive.
- **P1, replication: J invariance.** At each of the 7 replication steps, Q has placebo p > 0.05 [0.7 each]; ≥ 6/7 steps pass [0.6].
- **P2, first stage.** F has placebo p < 0.10 in ≥ 4/7 steps [0.5] (talk rate shifts at rule changes are not guaranteed; a step without a first stage is "mixed", not support).
- **P3, D_F (HH statistic).** D_F at each step is ≤ its placebo 95th percentile in ≥ 6/7 steps [0.6].
- **P4, E2.** Q_R (per-recipient read-gated inflow) has placebo p > 0.05 at the regime-III steps [0.65], and J^R_i > J^U_i on average on both sides (read-gated coupling present) [0.6].
- **P5, R-task contrast.** Median Q at the two goal-switch natives (NE36 fixed pairs, G42) exceeds median Q at the rule steps [0.45] (credence for R-task's direction; P1 still requires p > 0.05 at the rule steps).
- **Natives (details in the folders).** NE36: fixed-pair Q p > 0.05 [0.5]; switched-pair Q exceeds fixed-pair Q [0.55]. G42: Q p > 0.05 [0.5]; F p < 0.10 [0.7]. NE38: the reassigned agent's row Q is not in the top 20% of agents [0.65] while its |Δh̄| ranks in the top 3 [0.45]. NE43a: #focus switched-pair Q exceeds fixed-pair Q [0.45]; fixed pairs p > 0.05 [0.65].

**Verdict rules.**
- *Per step:* **supported** if Q p > 0.05 and F p < 0.10; **failed** if Q p < 0.05 (J moved more than placebo splits: the HH kill); **mixed** if Q p > 0.05 but F p ≥ 0.10 (no field step to test against); **inconclusive** wording inside "mixed" if P0(b) power < 0.5 at that skeleton.
- *Hypothesis level (HH kill):* **failed** if Q p < 0.05 at ≥ 2 of the 7 replication steps, or (confirmatory) at NE35. **Supported** if ≥ 5/7 steps are not failed and ≥ 3 have a first stage. **Mixed** otherwise.
- *Multiplicity:* 7 replication steps × 3 estimators; only the E1 block Q counts for the kill. E1-naive, D_F and E2 are secondary.

### Amendment 0 (structural; 2026-10-04 22:43 UTC, before any H117 statistic on real data)
Found while building the skeletons. What I saw: per-day kept-minute counts and per-agent talk-minute counts on a few window days, and the eligible-agent lists of the synthetic skeletons (6 agents at NE17, 19 at NE38, 8 at NE06). No J, Q, D_F or F on real data.
1. **Trim.** The DQ8 all-present window collapses on days with a briefly present agent (05-26: 20 kept minutes, 05-27: 1). The trim is now computed over the day's agents with ≥ 60 active minutes (`ki_talk.TRIM = "core60"`; "dq8" kept as an option). Most days are unchanged.
2. **Co-location thresholds.** Fixed pair: co-located ≥ 90% of kept minutes on both sides; switched: ≥ 90% on one side, ≤ 20% on the other (was 95% / 5%). The stricter rule dropped movers whose move happens during the first day.
3. **SE floor.** Each coupling SE is max(cluster-robust, model-based). Without it the sandwich SE collapses for sparse agents and the null Q has a 95th percentile of 167 in the #51 skeleton.

### Amendment 1 (after the synthetic validation; 2026-10-04 22:43 UTC, before any H117 statistic on real data; not post hoc on outcomes)
P0 (`analysis/synthetic.py`, `data/processed/H117-coupling-invariant-rule-reset/synthetic/p0_summary.json`; 80 null worlds and 40 worlds per alternative per skeleton; rate-calibrated; core60 trim). Rejection = Q above the skeleton's null-world 95th percentile.

| Skeleton (N) | Field step | Field + drive change | J step ±0.6 (half the pairs) | J step ±1.2 | All J × 0 | All J × 2 |
| --- | --- | --- | --- | --- | --- | --- |
| NE17, #38 (6) | 0.00 | 0.05 | 0.25 | 0.85 | 0.28 | 0.15 |
| NE06, regime I (8) | 0.03 | 0.13 | 0.70 | 0.88 | 0.58 | 0.08 |
| NE38, #51, k = 2 (19) | 0.00 | 0.15 | 0.50 | 0.68 | 0.45 | 0.00 |
| NE38, #51, k = 3 (22) | 0.03 | 0.18 | 0.78 | 0.63 | 0.43 | 0.00 |

- **P0(a) size:** passes for a pure field step (≤ 0.03); partly for a field step that also changes the common drive's amplitude (0.05–0.18).
- **P0(b) power:** fails as written. At ±0.6, power is 0.25 (#38), 0.50 (#51, k = 2) and 0.78 (#51, k = 3); only regime I passes (0.70 ≥ 0.5). At ±1.2, power is 0.63–0.88. Q is nearly blind to a global rescaling of all couplings (× 2: 0.00–0.15).
- **P0(c):** fails. E1-naive is not more fragile than E1 under a field step (0.00–0.25 vs 0.00–0.18), because each side is fitted separately and the step falls between them. R-leak is therefore not separable by this design, and P3's naive comparison is demoted to descriptive.
- λ = 0.1 was tried on two skeletons (`p0_summary_lam0.1.json`) and is worse; λ = 1 is kept.
- **Mean-field coupling Q_MF** (one coefficient per recipient on the summed partner input; `ki_talk.fit_e1_mf`): it detects global rescaling in #51 (× 2: 0.50–0.73) and J steps (0.80–0.93), but its size under field steps is 0.05–0.13 (#51 field + drive 0.13). It is reported as a secondary with that caveat.

**Consequences (binding for the real run).**
1. The primary test is unchanged: E1 block Q over fixed pairs against the same-regime placebo pool (k = 2).
2. **Wording of a pass:** "no rewiring of size ≥ 1.2 logistic units on half the pairs" at #38-type and regime-I steps (power 0.85–0.88). A pass at ±0.6 scale is claimed only for regime I. At #51 steps a non-rejection is "inconclusive" for ±0.6 changes.
3. #51 steps (NE38, NE43a) get a declared **k = 3 sensitivity** (NE38: 07-24, 07-27, 07-28 | 07-29, 07-30, 07-31; NE43a: 07-31, 08-03, 08-04 | 08-05, 08-06, 08-07), each with a k = 3 regime-III placebo pool.
4. The kill rule is unchanged (Q p < 0.05 at ≥ 2 of 7 replication steps).

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R-leak, R-task, R-drift, R-dilution (above).
**Locked holdout used for confirmation:** none run. `analysis/confirm.py` targets NE35 (#32: 02-23, 02-24 | 02-26, 02-27; the step day 02-25 is skipped because the reset's clock time is not known without opening held-out data) and NE44 (#46: 06-09, 06-10 | 06-11, 06-12). Written and dry-run on non-holdout stand-ins; not run.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | see round 1 |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | see round 1 |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | see round 1 |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | see round 1 |
| E interventional | predicts the change across a natural experiment | 1 | see round 1 |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | see round 1 |
| G ground truth | agrees with known structure | 1 | see round 1 |
| H comparative | beats the named rivals | 1 | see round 1 |
| I transfer | holds in other same-mode periods, including the holdout | 0 | holdout not run |

*Scorecard plan:* A from the mapping audit (regime I vs III talk spins); B from day-to-day stationarity of J (placebo Q level); C from the placebo pool; D from E2's read vs in-flight signature (unfitted by E1); E from the steps and switched-pair positive controls; F from P0; G from the movers and #focus (known adjacency switches); H from R-leak (E1-naive) and R-task (P5); I from regime I vs III and the confirm targets.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [NE06](goalperiod-subhypotheses/NE06/README.md) | replication | mixed | regime I, 8 agents: Q 0.82 (p 0.38); F p 0.38 |
| [NE07](goalperiod-subhypotheses/NE07/README.md) | replication | mixed | regime I, 8 agents: Q 1.37 (p 0.071); F p 0.52 |
| [NE16](goalperiod-subhypotheses/NE16/README.md) | replication | mixed | 9 agents: Q 0.37 (p 0.96); F p 0.85 |
| [NE17](goalperiod-subhypotheses/NE17/README.md) | replication | failed | 6 agents, 7 pairs: Q 1.54 (p 0.037); F p 0.70 |
| [NE38](goalperiod-subhypotheses/NE38/README.md) | replication + native | mixed (native supported) | 19 agents: Q 0.59 (p 0.52); reassigned agent Δh̄ rank 1, row Q rank 5/19 |
| [NE43](goalperiod-subhypotheses/NE43/README.md) | replication + native | mixed | NE43a Q 0.61 (p 0.41), NE43b Q 0.86 (p 0.11); #focus switched Q 0.93 vs fixed 0.61 |
| [NE36](goalperiod-subhypotheses/NE36/README.md) | native | mixed | Q 0.48 (p 0.78); F p 0.19; mover not eligible |
| [G42](goalperiod-subhypotheses/G42/README.md) | native | supported | Q 0.51 (p 0.74); F 8.0 (p 0.037) |

## Results
### Exploratory round 1 (2026-10-04, non-holdout; run 22:43–22:44 UTC, after Amendments 0–1)
**Headline.** A pure field change does not move the fitted talk-spin coupling matrix beyond its day-to-day noise, where a field change can be seen at all. Across 9 steps, J moved beyond the placebo pool once (NE17), with no field shift there. At the only step whose field moved beyond day-to-day changes (G42), J stayed at the placebo level.

**Synthetic validation (axis F):** Amendment 1. Size 0.00–0.03 under a pure field step; power 0.85–0.88 at ±1.2 (#38-type and regime I), 0.63–0.68 in #51; at ±0.6 only regime I has power ≥ 0.5.

**Outcome vs prediction**
| Prediction | Observed | Verdict |
| --- | --- | --- |
| P0 synthetic | size passes; power fails at ±0.6 except regime I; naive not more fragile | partly |
| P1 Q p > 0.05 at each of 7 steps (≥ 6/7) | 6/7 (NE17 p 0.037) | supported |
| P2 F p < 0.10 at ≥ 4/7 | 0/7 (F p 0.37–0.85); placebo F 90th pct 5.5–6.6 | failed |
| P3 D_F ≤ placebo 95th pct at ≥ 6/7 | 6/7 (NE17 p 0.037) | supported |
| P4 Q_R p > 0.05 (regime III) | 5/5 steps (p 0.11–0.93); J^R − J^U > 0 on both sides at 9/10 sides (0.16–0.98) | supported |
| P5 R-task: Q(goal switches) > Q(rule steps) | medians 0.50 vs 0.82 | failed (against R-task) |
| NE38 native | Δh̄ rank 1/19 (z −5.6); row Q rank 5/19 | supported |
| NE36 native | Q p 0.78; F p 0.19; positive control n/a | mixed |
| G42 native | Q p 0.74; F p 0.037 | supported |
| NE43a #focus native | switched 0.93 > fixed 0.61; vs placebo p 0.11 | weak support |
| HH kill (≥ 2/7 steps with Q p < 0.05) | 1/7 | not fired |

**What this means.** The fitted J is not a field artifact at the size the data can resolve: field changes (G42, NE38's single agent) leave it at its placebo level. The test is weak in two ways. Most documented rule changes do not move talk fields more than an ordinary night does, so they are not field steps in the data. And pairwise J at two days per side resolves only large rewiring. E2's read-minus-in-flight contrast is positive at every regime-III step and placebo (pool mean 0.26–0.30), the read-out signature of H08/H50; the absolute J^R and J^U are both negative and confounded with call length (the window length is the call's latency, which differs between talk and work calls).

**Operator-facing conclusion.** A goal or rule change does not rewire who responds to whom in talk timing (no change ≥ 1.2 logistic units on half the pairs at #38-type sizes). Expect the swarm's talk couplings to carry over a reset; only room moves change them, and those changes are small (switched-pair Q 0.93 vs 0.61).

**Caveats.** 4–19 eligible agents per step; NE17's 7 pairs make its failure fragile (one of 9 tests at p 0.037). The regime-III k = 2 placebo pool has 26 splits (p resolution 0.037), k = 3 only 9. F's null is wide (day-to-day talk-rate shifts). E1-naive is no more fragile than E1 here, so R-leak is untested rather than rejected. Regime I steps are chat-mode; NE35 sits on the regime I → II boundary.

**Scorecard (round 1).**
| Axis | Score | Evidence |
| --- | --- | --- |
| A mapping | 1 | Talk spins from `activity_bins_fixed`, rooms from `rooms_asof`, ledger calls; regime I and III both mapped; eligibility drops low-talk agents (movers). |
| B assumptions | 1 | Day-to-day stationarity of J holds (placebo Q at the synthetic null level); no Markov-order or update-order audit. |
| C adequacy | 1 | Placebo pools of 83 / 26 / 9 splits calibrate Q; no held-out-day likelihood. |
| D unfitted predictions | 1 | E2 read > in-flight at every regime-III step (not fitted by E1). |
| E interventional | 1 | Two field steps with a first stage (G42 village-wide, NE38 single agent) leave J at the null; the switched-pair positive control is weak. |
| F identifiability | 1 | Real-skeleton synthetic: size ≤ 0.03, power 0.85–0.88 at ±1.2; underpowered at ±0.6 and for global rescaling. |
| G ground truth | 1 | Known adjacency cut (#focus) shows only weakly (p 0.11). |
| H comparative | 1 | Against R-task (goal switches move J less, not more) and R-drift; R-leak not separable. |
| I transfer | 0 | Holdout not run. |

**Claim that stands:** at the one non-holdout step whose talk fields moved beyond day-to-day changes (the #41 → #42 goal switch, F placebo p 0.037), the KI-5 talk-spin coupling matrix stayed at its placebo level (Q 0.51, p 0.74; 39 pairs), excluding rewiring of ±1.2 logistic units on half the pairs (power 0.85). Excluded: the 7 rule steps (no first stage), NE17's failure (7 pairs, p 0.037, no field shift), changes smaller than ±1.2, global rescaling, R-leak (unpowered).

### Confirmatory design (written 2026-10-04 after exploration; not run)
`analysis/confirm.py` (frozen thresholds: Q95 1.4253 regime I, 0.9532 regime III; F90 6.5926 / 5.5455). C1 NE35 (#32: 02-23, 02-24 | 02-26, 02-27; the step day skipped; one-room assertion), C2 NE44 (#46: 06-09, 06-10 | 06-11, 06-12). Dry run on NE07 / NE17 stand-ins passes, with no held-out row loaded. Ledger: allowed; disclosure needed (H05 on #32, H04 on #46).

## Round 2 redirects
- **What the direction is really after:** is a fitted coupling a property of the read path or of the task? Settle it with steps that move fields far beyond nightly changes (goal switches with fixed rooms: #41 → #42, #39 → #40 within classes) and with more days per side.
- Add log(call latency) to E2 so J^R and J^U are interpretable on their own; keep R − U as the primary statistic.
- Pool steps hierarchically (partial pooling of Q across goal switches) rather than adding single-step tests.

## Notes
- 2026-10-04 22:03 UTC: card written. NE35 is held out (#32 in the goal-period holdout, 02-25 inside NE12's window): exploration uses other steps only. NE35 falls on the Rooms-v1 day (CHANGELOG 02-25) and the regime I → II boundary, but `period_units` lists one room for unit 32b, so the adjacency is unchanged there (to be asserted by the confirm script). NE36 in the catalog is not mid-goal: it opened #38 on its first day, so it is a native (goal switch with an operator correction), not a replication.
