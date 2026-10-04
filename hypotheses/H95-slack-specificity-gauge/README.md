# H95: Speed-limit slack as a kickoff-specificity gauge

**Status:** exploratory round 1 **done (2026-10-04): the pre-registered gauge failed as a measurement, and the slack still splits the kickoffs cleanly by goal type (post hoc).** Card, observables and predictions written ~20:25 UTC before any new real-data statistic; amendment A1 after the synthetic, A2 (post hoc) after the run. Approved by Vivian 2026-10-04 from HH329.
- **P1 (primary): no relation.** ρ(S, x) = −0.01 over nine regime-III kickoff units (exact one-sided p = 0.50). The HH's kill (|ρ| < 0.3) is met, but the synthetic power at n = 9 is 0.29, so the test is inconclusive by its own pre-set reading (A1).
- **The x gauge does not measure specificity.** H54's name-token flags give the free "novel research" kickoff x = 0.74 and "build your own world" x = 0; the strict flag matches no repo in any period. P4 (G39 has high x) failed for this reason.
- **Post hoc (A2):** coding each goal by whether it assigns a concrete artifact separates the units perfectly: assigned S 1.0–2.5, T_e 0.25–0.75 h (G39, G40, G42, G44 #best, G51); open or objective-only S 3.0–14.5, T_e 4–13 h (G37, G38, G41, G44 #rest); exact Mann–Whitney p = 0.008 (0.004 with G36).
- **Natives:** N1 G44 supported (x 0.69 vs 0.17; slack ×5.8); N2 G38 failed (both rooms x ≈ 0, no contrast to test; the 4-agent room settles in 1.25 h vs 10.25 h).
- Per-unit verdicts: 4 supported, 2 mixed, 3 failed. Scorecard A0 B1 C0 D1 E1 F1 G1 H1 I1. `confirm.py` (#45, #46, #47, #49; the A2 code frozen) written; **not run**.
**Fields:** stat mech, thermodynamics (stochastic), sociophysics
**Literature:** [Kolchinsky, Dechant, Yoshimura & Ito 2026](../../literature/kolchinsky-2026-generalized-free-energy-excess-housekeeping.md) (Wasserstein speed limit T ≥ (W/Ā) coth(Σ_ex/2W) ≥ W/Ā; the slack as the content of the bound); [Aguilera, Ito & Kolchinsky 2026](../../literature/aguilera-2026-entropy-production-nonequilibrium-maxent.md) (EP as statistical irreversibility, no heat bath).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Population N(t) (H75 variant *committing population*); Regime; Driving / external field (the kickoff); Agent state, variant *categorical* (H75's **repo allocation p(t)**); H75's proposed variants **allocation distance W**, **switch activity Ā**, **settling time T_e / T_90**, **speed-limit slack S**; H54's **quench target (kickoff)** and named-project flags. New named variants proposed for DEFINITIONS.md (not edited there; defined under "Operational definitions"): **kickoff specificity x (day-1 named share)**, **churn-normalized slack S/S₀**.
**Question served:** Q5 (what can an operator do?), with Q2 (field vs coupling: the kickoff field's strength) second.
**From:** HH329 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/15-stochastic-thermodynamics-selection/` (item 3, speed limits), `physics-models/11-vector-spins/` (the kickoff as a field on agents' positions; H54)
**Data inputs (shared tables first):** DQ4 `work_commits` (agent-work filter as H75), `work_repos` (`artifacts` list: repo ↔ artifact ids), `calendar`, `embeddings/goals.parquet` (kickoff `win_start`), `period_units`, `roster`, `rooms_timeline` (G38 native), `ground_truth_labels` (`room_assignment`, #44), and H54's processed `projects.parquet` (named flags per artifact and goal; read-only data dependency) and `kickoffs.parquet` (S_text, rival). No text.

## Source HH (verbatim from the HH list, including literature refinements)
Speed-limit slack as a kickoff-specificity gauge. H75 found that kickoffs naming their target settle at the speed limit (S ≈ 1.0–1.4) while free-choice goals churn (S 5–15). Prediction: across all regime-III kickoffs, S falls monotonically with kickoff specificity, i.e. the fraction of day-1 work on kickoff-named repos (H54). This would make S a one-number gauge of how much a goal statement constrains allocation. *Check:* S and T_e per kickoff vs specificity; size-matched null on agent switch rates. *Kill:* no monotone relation (Spearman |ρ| < 0.3).
  *Models:* 15, 11 · *Builds on:* H75, H54, H48

## Standards (2026-10-04)
**Question served:** Q5, then Q2.

| Impostor | Relevant? | How it is handled | Status |
| --- | --- | --- | --- |
| Scheduler field | partly | S is built from commit order in active hours (calendar windows), so day edges change only the clock, not the switch count. Commits are not activity bins (the DQ8 event-drop bug does not apply). | n/a for S; removed for T_e by the active-hour clock |
| Exogenous field (kickoff, goal, operator) | yes | The kickoff field is the object. Its *strength* is measured twice: x from commits on kickoff-named repos (H54 flags), and S_text from the kickoff text alone (H54; a rival gauge). Operator messages inside the horizon are not removed (noted per period). | n/a (object of study) |
| Shared model priors | partly | Day-1 work on a named repo could reflect what every LLM builds first for a goal genre. The design code (artifact named vs not) and H54's frozen-project carry-over check address genre only partly. Lab mix is reported per kickoff. | partly |
| Contemporaneous convergence | partly | A named repo can gain day-1 commits by copying from early movers rather than from the text. The day-1 share counts both. H54's own-target percentile (text → content) is the field evidence; no read vs unread contrast here. | open |

**Circularity (stated before the run).** x and S come from the same commits. Churn on side repos lowers x and raises S at once. The *churn-rate null* (below) sizes how much negative ρ this coupling makes when the field strength is fixed.

**Inputs:** DQ4 `work_commits` (agent-work filter), not activity bins. H54's named flags are a read-only data dependency (they turned out not to measure specificity; see Results).

**Two layers:** nine replication kickoff units in eight periods; natives N1 (G44 rooms) and N2 (G38 rooms).

**Confirm script:** `analysis/confirm.py`, frozen and guarded; not run.

## Question
Does the speed-limit slack of the post-kickoff re-allocation fall monotonically with how specific the kickoff is, measured as the share of day-1 work on kickoff-named repos? If it does, S is a one-number gauge of how strongly a goal statement constrains where agents work.

## Design: two layers (Vivian, 2026-10-04)
- **Replication:** H75's slack estimator on every non-holdout regime-III kickoff, as one point per kickoff unit: G37, G38, G39, G40, G41, G42, G44 (#best and #rest rooms as two kickoff units; the room kickoffs differ), G51. Nine kickoff units in eight goal periods. The across-kickoff relation is a comparison of per-period fitted parameters (phase-diagram points), not a pooled fit. Period README role: `replication`. G36 (kickoff on the last regime-II day) is a sensitivity point only.
- **Natives (2):** N1 G44 (two room kickoffs on the same days: x and S per room); N2 G38 (two rooms with different kickoff texts and per-agent goal overrides). Role: `native`.
- **Confirmation:** `analysis/confirm.py` (held-out regime-III kickoffs #45, #46, #47, #49, #50), frozen, guarded, **not run**.

## Model
**From:** `physics-models/15-stochastic-thermodynamics-selection` (item 3) and `physics-models/11-vector-spins` (kickoff field).

**H95 variant: a two-population relaxation on repos.** Each committing agent is a copy of a jump process on repos plus the null state ∅. After the kickoff a fraction q of agents is *captured* by the field: their first post-kickoff commit lands on their settled (named) target and they stay. The rest *search*: they churn between their current repo and side repos at switch rate a before reaching a settled repo with hazard 1/τ (H75's field-limited scenario F). With W the total-variation distance between the allocation at t = 0⁻ and at T_e, Ā the switches per agent per active hour up to T_e,

  T_e ≥ W/Ā (counting identity, H75),  S = ĀT_e/W ≈ [q + (1 − q)(1 + aτ_s)] / [q + (1 − q)·m],

where τ_s is the searchers' time to settle and m ≤ 1 the share of searchers that have moved by T_e. S → 1 as q → 1 (instant freeze, H75 rival R2) and rises with (1 − q)·aτ. The model predicts S to fall monotonically in q. The observable proxy for q is the kickoff specificity x (the day-1 share of work on named repos).

**Rivals.**
- **R1 churn rate, not field (switch-rate null):** S is set by how often agents switch (lab mix, cadence, task granularity), and x correlates with S only through the shared commits.
- **R2 concentration:** S tracks how concentrated day-1 work is (one shared repo), not whether the repo was named. G39 (each agent builds its own named-type world) is the discriminating case: named but not concentrated.
- **R3 text specificity (H54 S_text):** the kickoff text's own specificity score sets S. H54 found S_text does not set day-1 content spread.

## Data scheme (`scheme/build.py`)
- **Inputs:** `work_commits` with H75's agent-work filter (`canonical & ~imported & author_kind == "agent" & ~automated`); `work_repos.artifacts`; H54 `projects.parquet` (`goal_no`, `artifact`, `named`, `named_strict`, `named_loose_kick`, `named_goal`); `calendar`; `goals.parquet` (kickoff `win_start`); `ground_truth_labels` (`room_assignment`, #44); `rooms_timeline` (#38 rooms).
- **Transform:**
  1. **Active clock and ensembles:** H75's `clock` and `ensemble` (copied into `scheme/build.py` with attribution): t = 0 at the kickoff, active hours from calendar windows, non-holdout days only.
  2. **Horizon:** H = min(20, total active hours of the period's non-holdout days), floored to 0.25 h; settled window = the last 4 active hours of the horizon (G37: H = 12; G44: H ≈ 16).
  3. **Initial condition:** W_∅ (every agent starts at ∅) in every unit (primary, comparable across units); W_pre where the two pre-kickoff days are non-holdout (secondary).
  4. **Named repos:** a DQ4 repo is *kickoff-named* for goal g if any artifact in its `work_repos.artifacts` list is flagged `named` for goal g in H54's `projects.parquet`. Variant *strict*: only `named_strict` artifacts.
  5. **Room units:** #44 rooms from DQ6 `room_assignment`; #38 rooms from `rooms_timeline` (majority room over the first 4 active hours; null `t_end` → +∞).
- **Output:** `data/processed/H95-slack-specificity-gauge/<G..>/` with `states.parquet` (agent, t_active, repo code), `named.parquet` (repo code, named flags; no repo names), `results.json`; `results/across.json`; `synthetic/`; `_provenance.json`. Expected < 5 MB.
- **Regimes covered:** regime III (G37–G51 head).

## Operational definitions (written 2026-10-04 ~20:25 UTC, before any new real-data statistic)
- **Kickoff specificity x (primary, HH):** among agent-work commits by the unit's committing agents in the first 4 active hours after the kickoff, the share on kickoff-named repos. Sensitivity: the whole kickoff day; the strict naming flag; agent-weighted (mean over agents of each agent's share).
- **Slack S** = Ā T_e / W at T_e (H75 definitions, W_∅), with H75's agent bootstrap (B = 200).
- **Churn-normalized slack S/S₀:** S₀ = median S over 200 surrogates in which each agent's commit repo labels are permuted among its own commits in the horizon (keeps commit times, each agent's repo multiset and its number of commits; destroys directed movement). A switch-rate-matched baseline for each unit.
- **Size-matched slack S₁₂:** median S over 50 random subsets of 12 committing agents (units with N ≥ 12), so kickoffs of different N compare on equal footing.
- **Concentration (R2):** c = 1 − H(day-1 repo shares)/ln(n_repos) on the same day-1 commits (0 = spread, 1 = one repo); also the top-repo share.
- **Text specificity (R3):** H54 `S_text` of the unit's kickoff (room kickoff where one exists).
- **Monotone relation:** Spearman ρ(S, x) over the nine kickoff units, one-sided exact permutation p (9! orderings); also ρ(T_e, x) and ρ(S/S₀, x).

## Observables
1. Per kickoff unit: N, x (and variants), W, Ā, T_e, T_90, S, S/S₀, S₁₂, c, S_text.
2. Across units: ρ(S, x), ρ(T_e, x), ρ(S/S₀, x); partial ρ(S, x | c); ρ(S, S_text).
3. Natives (below).

## Null / baseline
- **Churn-rate null (the HH's "size-matched null on agent switch rates"; synthetic, before the run):** worlds where the field strength q is the same for every kickoff and only the churn rate a varies across kickoffs (0.5–8 switches per active hour). The Spearman ρ(S, x_measured) these worlds produce is the mechanical coupling of x and S; the observed ρ is read against its distribution.
- **Permutation null** for ρ across kickoff units (exact).
- **Within-unit baseline S₀** (label permutation within agent).
- **Agent bootstrap** CIs (H75).

## Native tests (each with its own prediction, below)
- **N1 · G44 (two room kickoffs on the same days).** #best is told to fine-tune a named leader; #rest picks its own goals. Same days, same scaffold, switch rates 3.3 vs 3.4 per agent-hour (H75). Observable: x and S per room; the slack ratio S_rest/S_best against the x difference. *Already seen:* H75's S per room (2.5 and 14.5). New: x per room and S/S₀.
- **N2 · G38 (two rooms, different room kickoffs, per-agent goal overrides).** H54's room kickoffs differ in S_text (0.40 vs −0.85). Observable: x, S, T_e per room over the same horizon. Every #38 number is new.
- **Considered and not used:** G51 newcomers (single-agent re-allocations: x is undefined for one agent's own target); NE38 (one agent); held-out #45–#50 (confirm.py).

## Synthetic validation plan (axis F; `analysis/synthetic.py`)
H75's synthetic agents (commit-observed states, lognormal call rates, Poisson commits at median 4 per active hour, 20-h horizon), extended with a captured fraction q: captured agents move to their named target at their first commit; searchers follow H75's scenario F (target hazard 1/τ, τ = 5 h; churn to side repos at rate a, visits of mean 20 min). Targets: one shared named repo (concentrated) or one own named repo per agent (G39-like, deconcentrated). Sizes N ∈ {4, 12, 15, 27}; q ∈ {0, 0.1, …, 1}; 50 replicates each.
- **(i) Gauge curve:** median S and x_measured vs q; monotone in q?
- **(ii) Churn-rate null:** 9 kickoffs with q fixed (0.5) and a drawn log-uniform in [0.5, 8] per kickoff; distribution of ρ(S, x_measured) over 500 draws (its 5th percentile is the threshold the real ρ must beat).
- **(iii) Power:** 9 kickoffs with q spread uniformly on [0.05, 0.95] and a log-uniform in [0.5, 8] (and N drawn from the real unit sizes); P(ρ ≤ −0.5 and ρ below the churn-null 5th percentile).
- **Pass:** S monotone (non-increasing) in q at N ≥ 12; power ≥ 0.8 at n = 9; the churn null's median ρ reported. If the churn null alone gives median ρ ≤ −0.3, the HH's kill threshold is not informative and the primary test becomes S/S₀ and the churn-null percentile.

## Synthetic validation results (2026-10-04 ~21:05 UTC; `analysis/synthetic.py`, `data/processed/H95-slack-specificity-gauge/synthetic/`)
H75's commit-observed agents with a captured fraction q; 30 replicates per (target, N, q); 500 churn-null draws and 300 power draws of nine kickoff units (sizes 4–16); `--norm`: 200 + 200 draws with S/S₀.

| q (captured) | 0 | 0.2 | 0.4 | 0.6 | 0.8 | 1.0 |
| --- | --- | --- | --- | --- | --- | --- |
| median S, shared target, N 15 | 4.03 | 2.67 | 1.90 | 1.41 | 1.21 | 1.10 |
| median S, own targets, N 15 | 3.55 | 3.13 | 2.27 | 1.53 | 1.28 | 1.15 |
| median x (measured), shared, N 15 | 0.21 | 0.31 | 0.37 | 0.53 | 0.59 | 0.66 |

- **The gauge curve is monotone** in q at every size and for shared and own targets (S non-increasing within ±0.15 in 8/8 curves). Churn caps the measured x at ≈ 0.66–0.71 even at q = 1.
- **The churn-rate null is calibrated:** with q fixed (0.5) and a 16× range of churn rates across kickoffs, median ρ(S, x) = −0.10, and ρ ≤ ρ_crit(9) = −0.583 in 6.4% of draws (8.5% in the `--norm` run). The shared commits do not make a strong negative ρ by themselves.
- **Power at n = 9 is low: 0.29** (P(ρ ≤ −0.583) with q uniform on [0.05, 0.95] and the 16× churn range; median ρ(S, x) = −0.40, median ρ(S, q) = −0.57). **S/S₀ does not help** (power 0.245, null size 0.105). ρ(T_e, x) is weaker (power 0.10–0.16).
- **The HH's kill condition is not a valid kill at n = 9:** |ρ| < 0.3 occurs in 39% of worlds where the gauge is true (53% under the churn null).
- **Pass criteria:** monotone gauge, passed; power ≥ 0.8 at n = 9, **failed**; churn-null median ρ = −0.10 (> −0.3), so the HH's threshold is not dominated by the circularity.

## Amendments (dated; what had been seen)
- **A1 (2026-10-04 ~21:05 UTC, after the synthetic, before any new real-data statistic).**
  1. P1 keeps its rule (ρ(S, x) ≤ −0.5, exact one-sided p < 0.05, below the churn-null 5th percentile −0.63). Its power is 0.29, so **a miss is "inconclusive", not a kill**; the HH's kill (|ρ| < 0.3) is reported but not used as a kill (it fires in 39% of true-gauge worlds).
  2. P3 (S/S₀) is demoted to descriptive: the synthetic shows no gain over S.
  3. A per-kickoff check is added because the across-unit test is weak: each unit's (x, S) point is compared with the synthetic gauge band at its N (the 10–90% S range at the q whose median x is nearest the observed x). The count of units inside their band is reported (descriptive).
  4. The across-kickoff switch rate in the settled window (Ā_ss) is reported per unit, to show how much churn heterogeneity the real kickoffs have compared with the synthetic 16× range.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R1 churn rate (switch-rate null); R2 concentration; R3 text specificity (H54 S_text).
**Locked holdout used for confirmation:** none yet. `analysis/confirm.py` (held-out kickoffs #45, #46, #47, #49, #50) written and frozen; not run.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 0 | S is well defined (H75). The pre-registered x is defined from fields but fails validity: H54's loose flags give a free kickoff x = 0.74 and an assigned one x = 0; the strict flag matches no repo. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | H75's assumptions (commit-observed states, exchangeable agents, active-hour clock). G37's 03-31 window is 12.6 h long (an early-start record), so its 20-h horizon covers 3 days. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 0 | ρ(S, x) sits at the permutation null (p 0.50) and inside the churn null. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | The gauge's signature (S falls with captured fraction) appears against the post-hoc design code (perfect separation, p 0.008), not against x. |
| E interventional | predicts the change across a natural experiment | 1 | G44 rooms (two kickoffs on the same days): supported. G38 rooms: no x contrast. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Gauge curve monotone at all sizes; churn null calibrated; power 0.29 at n = 9 (the test cannot reject reliably). |
| G ground truth | agrees with known structure | 1 | DQ6 room assignment (G44); the goal titles' assigned artifacts agree with the freeze/churn split (H75, H54 frozen projects). |
| H comparative | beats the named rivals | 1 | R3 (text specificity) has the wrong sign (+0.63); R2 (concentration) ρ +0.18; R1 (churn) cannot be separated from x at n = 9. The post-hoc code beats all three. |
| I transfer | holds in other same-mode periods, including the holdout | 1 | Nine kickoff units in eight periods; holdout not run. |

## Prediction
*Written 2026-10-04 ~20:25 UTC, before running the analysis on real data. What I had seen: H75's card and results (W_pre S_e: G39 1.00, G40 1.25, G41 5.09; W_∅ S_e: G51 1.40; G44 rooms #best 2.5, #rest 14.5; T_e 0.25–9.5 h); H54's card (9/13 frozen projects named; S_text fails for content spread; per-goal counts of H31 projects and of named flags, e.g. G39 6/19, G41 11/22, G51 4/134); goal titles and modes (#37 free, #38 charity with per-agent overrides, #39 own world, #40 connect worlds, #41 novel research, #42 own YouTube channel, #44 fine-tune leader / free, #51 private assigned goals). Not seen: any x, any W_∅ slack for G37–G42 or G44 as one unit, any S for G38 rooms.*
- **P1 (monotone gauge, primary).** ρ(S, x) ≤ −0.5 over the nine kickoff units, with one-sided exact p < 0.05, and below the churn-null 5th percentile. *Kill (HH):* |ρ| < 0.3. Credence 0.4. *Risk stated before the run:* G51's targets are named in private per-agent goals, not in the kickoff, so H54 flags few G51 repos (4/134 projects); G51 may sit at low x with low S and break monotonicity.
- **P2 (settling time).** ρ(T_e, x) ≤ −0.5. Credence 0.4.
- **P3 (churn removed).** ρ(S/S₀, x) ≤ −0.3 (the relation survives the within-unit switch-rate baseline). Credence 0.35.
- **P4 (naming, not concentration; R2).** The partial ρ(S, x | c) ≤ −0.3, and G39 (expected: high x, low c) has S ≤ 2. Credence 0.4.
- **P5 (text rival R3).** |ρ(S, S_text)| < |ρ(S, x)|. Credence 0.6.
- **N1 (G44).** x_best − x_rest ≥ 0.3 and S_rest/S_best ≥ 2. Credence 0.55 (S already seen: the S half is known to hold; the x half is new).
- **N2 (G38).** The room with the higher x has the lower S and T_e; |Δx| ≥ 0.2. Credence 0.35 (#38's charity goal names an objective, not an artifact; per-agent overrides may scramble rooms).
- **Per-period verdict rule (replication, per kickoff unit):** the unit is *supported* if it lies on the predicted side of the across-unit trend: S ≤ 2 when x ≥ 0.5, or S ≥ 3 when x < 0.5; *failed* if S ≥ 3 with x ≥ 0.5 or S ≤ 2 with x < 0.3; *mixed* otherwise (2 < S < 3, or 0.3 ≤ x < 0.5 with S ≤ 2); *n/a* if T_e is censored or N < 4. These cut-offs follow H75's freeze/churn split (S ≈ 1.15 vs 4.5 in its synthetic).

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | supported | N 12; x 0.00; S 3.00 [1.12, 4.50]; T_e 13.3 h |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication + native | supported (N2 failed) | N 12; x 0.01; S 4.82 [1.75, 25.1]; T_e 4.0 h; rooms: x 0.02 vs 0.00, S 4.9 vs 3.0, T_e 10.3 vs 1.3 h |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | failed | N 14; x 0.00 (no H54-named repo); S 1.00 [1.00, 1.00]; T_e 0.25 h |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | mixed | N 13; x 0.44; S 1.64 [1.36, 4.64]; T_e 0.5 h |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | failed | N 13; x 0.74 (loose token match); S 3.69 [1.42, 7.70]; T_e 9.0 h |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | supported | N 14; x 0.79; S 1.22 [1.00, 2.56]; T_e 0.5 h |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication + native | mixed (#best mixed, #rest supported; N1 supported) | #best N 4, x 0.69, S 2.50; #rest N 10, x 0.17, S 14.5 [5.2, 22.0]; ratio ×5.8 |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication | failed | N 16; x 0.13; S 1.40 [1.00, 3.73]; T_e 0.5 h (private goals name the target; the kickoff does not) |

## Results
### Exploratory round 1 (2026-10-04; `scheme/build.py`, `analysis/run.py`, `analysis/synthetic.py`, `analysis/posthoc.py`, `analysis/figures.py`)
Numbers: `data/processed/H95-slack-specificity-gauge/results/{across,natives,posthoc_design_code}.json`, `G<NN>/results*.json`, `synthetic/`. Figures: `figures/summary_obs.pdf` (S vs x with goal type; T_e by goal type), `figures/synthetic_compact.pdf` (gauge curve; ρ under the churn null vs a true gauge). Estimates: `per_period_estimates` (H95; 18 replication rows, 2 native rows). Run time < 2 min.

**Outcome vs prediction**
| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 ρ(S, x) ≤ −0.5, p < 0.05, below churn-null q05 (−0.63) | ρ = −0.01, p = 0.50 (n = 9); without G51 −0.07 | inconclusive by A1 (power 0.29); kill met |
| P2 ρ(T_e, x) ≤ −0.5 | −0.02 (p 0.49) | failed |
| P3 ρ(S/S₀, x) ≤ −0.3 (descriptive after A1) | +0.60 | failed |
| P4 partial ρ(S, x \| c) ≤ −0.3; G39 has S ≤ 2 with high x | partial −0.09; G39 S 1.00 but x 0.00 | failed (measurement) |
| P5 \|ρ(S, S_text)\| < \|ρ(S, x)\| | ρ(S, S_text) = +0.63 (more "specific" text, more slack) | failed (the text rival is worse, with the wrong sign) |
| N1 G44: Δx ≥ 0.3 and S ratio ≥ 2 | Δx +0.52; ×5.8 | supported |
| N2 G38: higher-x room has lower S, \|Δx\| ≥ 0.2 | Δx 0.02; S 4.9 vs 3.0 | failed (no contrast) |
| A1 check: units inside the synthetic gauge band at their x | 4/9 | descriptive |
| A1 check: switch rate in the settled window Ā_ss | 0.00–1.62 per agent-hour (all units), i.e. a wider spread than the synthetic's 16× churn range | descriptive |

**What it means.**
1. *The slack is a good gauge of goal type; the HH's x is a bad gauge of specificity.* S and T_e separate assigned-artifact goals from open goals with no overlap (post hoc). The day-1 share on H54-flagged repos tracks word overlap between repo names and the goal text, not whether the goal fixes a target.
2. *Per-agent targets count.* G39 (own world) and G51 (private goals) freeze instantly although the kickoff names no shared repo. Specificity must be measured per agent (does each agent's first post-kickoff commit land on its settled repo?), which is what S already measures.
3. *This is H75's result restated with more kickoffs.* S ≤ 2.5 for every assigned-artifact goal (5/5) and S ≥ 3 for every open goal (4/4), now including G37, G38 and G42, which H75 did not run.
4. *S is not a cost.* The bound is a counting identity; S counts switches per net move. The thermodynamic language adds nothing operational beyond "how many repo switches per agent that ends up somewhere new".

## Amendments (post hoc)
- **A2 (2026-10-04 ~21:45 UTC, after the replication run; post hoc, labelled).** Design code d from the goal titles (listed in the card's "what I had seen" before the run, but not pre-registered as a predictor): d = 1 if the goal assigns a concrete artifact to build or run (#39, #40, #42, #44 #best, #51), d = 0 otherwise (#37, #38, #41, #44 #rest; #36 as sensitivity). Exact one-sided Mann–Whitney on S: U = 20/20, p = 0.008 (with G36, S 2.64: p = 0.004); on T_e the same. Frozen for the holdout in `confirm.py` (C2).

## Confirmatory predictions (C-*): for the locked holdout, frozen 2026-10-04 after round 1, not run (`analysis/confirm.py`)
- **C1 (pre-registered gauge):** ρ(S, x) ≤ −0.5 over #45, #46, #47, #49 (expected to fail; reported for completeness).
- **C2 (post-hoc design code, frozen now):** all four held-out kickoffs are coded d = 0 from their titles (#45 follow your leader; #46 organise an event / surprise each other; #47 reduce global suffering / play games; #49 beat the hardest game you can). Prediction: S ≥ 2.5 or T_e ≥ 2 active h in ≥ 3 of the 4. #50 is excluded (code hosting moved to GitLab, CHANGELOG I).
- **Disclosure:** while coding I read the catalog setup lines for #45–#50 in `goal-periods.md`; they say #47 #best had a Help Kit live within 11 minutes, which hints at a fast freeze in that room.
- Reuse: H75's `confirm.py` uses the same slack estimator on #45–#47 (NE20 DiD and transfer). The ledger has no slack family; `confirm.py` passes `other`. The coordinator must order or merge the two runs.

## Round 2 redirects
**What the direction is really after:** a one-number, log-computable gauge of how strongly a goal statement constrains where agents work.
- **H95-R1. A per-agent specificity.** Score each agent's kickoff instruction (village goal plus any private goal) for a named artifact, and use the share of agents whose first post-kickoff commit lands on their settled repo as the field strength. Test S against it with the H54 text flags as a rival.
- **H95-R2. More kickoffs.** Extend to regime II and late regime I kickoffs with git activity (DQ4 notes earlier zeros are ambiguous), to raise n beyond 9.
- **H95-R3. Merge with H75.** H95's estimator is H75's; move `settle_stats`/`bootstrap` to `infra/shared/` and report S per kickoff once, as a constant per goal type.
- **H95-R4. Run confirm.py** (C2 is the informative test).

## Notes
- 2026-10-04: compute limits (STANDARDS §9): ≤ 2 threads, no pools, one job at a time.
- 2026-10-04: processed data 0.25 MB.
- 2026-10-04: H75's estimator (`h75lib.settle_stats`, `bootstrap`, `agent_settling`) and scheme (`clock`, `ensemble`) are copied with attribution into `analysis/h95lib.py` and `scheme/build.py`; nothing is imported across hypothesis folders. A move of the slack estimator to `infra/shared/` is proposed in the report (H75, H95 and H75-R3 use it).
