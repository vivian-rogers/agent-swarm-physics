# H20: Aging: day-to-day content autocorrelation depends on time since kickoff, not just the lag

**Status:** exploratory round 1 done (2026-10-03), mixed, leaning refuted. There is no aging in 29 non-holdout goal periods. The one strong age effect (#38) is a kickoff relaxation lasting about 4 active days, after which content is stationary. Observables, null and predictions were written before any real-data run; Amendment 1 after the synthetic, Amendment 2 (calibrated null) after the real-data calibration check. Holdout not run.
**Fields:** stat mech, dynamics
**Origin:** HH101 (`../hypohypotheses/HYPOHYPOTHESES.md`; `../promotion-shortlist.md`)
**Definitions used:** agent (the Claude Code agent excluded); regime (whitening per regime; no analyzed period crosses a regime boundary, so #36 is excluded); driving / external field (the village goal ĝ, and in #51 each agent's assigned goal ĝ_i); agent state, variant *vector (for model 11)*, operationalized at day resolution as the **agent-day statement mean** below (proposed as a named variant, see Notes); activity time, operationalized as the **active-day clock** (days of the period with village activity; weekends and holidays don't count). Goal period as the unit of analysis; named exceptions: (c) for rejuvenation at step changes inside #38/#51, (d) for the short-period contrast (partial pooling of a matched-window statistic), (a) for the shared embedding basis and ĝ.

## Question
Agents restart every day with memory, which is like field cooling. Does the similarity of what an agent (or the swarm) says on day t_w and day t_w + τ depend on the waiting time t_w since the goal's kickoff, as in spin-glass aging (C(t_w + τ, t_w) decays more slowly for larger t_w)? Or only on τ (stationary)? Do longer goals age more? Practical payoff: how fast a long-running swarm 'forgets' or locks in, and whether old swarms become rigid.

## Model
**From:** `physics-models/01-inverse-ising` (SK / glassy dynamics, aging and two-time correlation functions; fluctuation–dissipation violations), `11-vector-spins` (content as vector spins; center and whiten). Rivals: stationary exponential relaxation; simple drift toward a fixed goal direction (field-driven relaxation with no aging).

**Hypothesis-specific variant.** Each agent's day state is a vector spin in the regime's whitened n = 32 basis. Aging is parametrized by a time change of an Ornstein–Uhlenbeck relaxation (the "Box-Cox clock"): C(t_w + τ, t_w) = q + (c0 − q) exp(−[s_μ(t_w + τ) − s_μ(t_w)]/τ0), with s_μ(t) = (t^{1−μ} − 1)/(1 − μ) (log t at μ = 1). μ = 0 is stationary relaxation; μ = 1 is simple (full) aging, C = f(τ/t_w), as in the trap model and coarsening; 0 < μ < 1 is sub-aging, with an effective relaxation time τ_R(t_w) ≈ τ0 t_w^μ; μ < 0 means the dynamics speed up with age. q is the plateau (persistent agent style + goal content), c0 the short-lag ceiling (c0 < 1: day-to-day "nugget" variation).

## Data scheme (`scheme/`)
Shared tables in `data/processed/shared/` (see `infra/README.md`): `embeddings/statements.parquet` + `chat_bge_small.npy` / `intentions_bge_small.npy` (each agent's own chat messages and self-written intentions), `whitening_<regime>.npz` via `common.load_whitener`, `calendar`, `memory_stats`, `roster`. Goal vectors: H01's raw bge embeddings of goal and kickoff texts (`data/processed/H01-emergent-superagents-exist/goals.parquet` + `goals_raw.npy`, read only), whitened here in the shared regime basis (a shared instrument; proposed to move into `infra/`).
- **Transform (`scheme/build.py`):** non-holdout statements of non-holdout periods only (holdout masked with `holdout_mask`), Claude Code agent excluded. Each statement → whitened 64-d coordinates in its regime basis (the first n columns give the n-d basis; normalized downstream). Each statement gets its active-day index d within its goal period (d = 1 is the kickoff day) and its calendar-day offset. Goal directions per period: ĝ = unit(unit(W·goal) + unit(W·kickoff)) (kickoffs averaged over rooms), and per-agent assigned-goal directions in #51.
- **Output:** `data/processed/H20-content-aging/`: `statements.parquet` (kind, agent, t, pt_date, goal_no, regime, d, d_cal; no text), `stmt_w64.npy` (fp16), `days.parquet` (period × active day: d, d_cal, gap_before_s, weekend flag), `goal_dirs.npz`, per-period results in `G<NN>/`, synthetic results in `synthetic/`, and `_provenance.json`.

## Candidate goal periods
Long goals (primary): #4 (25 days, regime I), #8 (18, I), #38 (17, III), #51 (45 non-holdout days, III). Medium (secondary aging tests, transfer within exploration): #6 (15 days), #13, #18, #19, #20, #27 (10 days each). Short (stationary contrast, ≥ 4 days): #5, #10, #11, #12, #16, #17, #21, #23, #24, #25, #26, #30, #31, #35, #39, #40, #41, #42, #44. Not analyzable: #2, #3, #7, #33, #37 (≤ 3 days), #36 (crosses the 03-24 regime boundary on its day 2). Holdout periods for confirmation (see Prediction).

## Links to other hypotheses
H01 D3.3 (phase behavior: quench at goal changes, hysteresis), H10 (field response), H17 (mixing times). H01 P3 (room order stability day to day) and P9 (mean-field polarization) and H10 (cumulants along ĝ, one tilt per week) use the same embeddings at the same or finer resolution; H20 does not re-test them. H20's observable is the *two-time* function of each agent's own day state, which neither computes.

## Observables
*Specified 2026-10-03, before any real-data run.*

- **O1 Agent-day states.** For agent i on active day d of period P, take its statements k, whiten them in the regime basis at n = 32 and unit-normalize: ẑ_k. Sufficient statistics per agent-day: count n_id, mean x̄_id, noise variance of the mean v_id = (Σ_k |ẑ_k|² − n|x̄_id|²)/(n(n−1)), and the noise-corrected self-overlap S_id = |x̄_id|² − v_id (unbiased for |μ_id|², μ_id the agent-day's expected statement vector). Agent-days with n_id < 8 are dropped.
- **O2 Two-time correlation (agent-averaged).** For days d ≠ d′: C(d, d′) = Σ_{i∈I} x̄_id · x̄_id′ / √(Σ_{i∈I} S_id · Σ_{i∈I} S_id′), with I = I(d, d′) the agents valid on both days (ratio of sums, so noisy denominators stay stable). t_w = d, τ = d′ − d. Each entry uses only days d and d′, so leave-one-day-out cross-validation is clean. Per-agent version C_i(d, d′) = x̄_id·x̄_id′ / √(S_id S_id′) for agent-level replication.
- **O3 Swarm-mean correlation.** m_d = mean of x̄_id over agents valid on day d; S_m,d = |m_d|² − Σ_i v_id / N_d²; C_m(d, d′) = m_d·m_d′ / √(S_m,d S_m,d′). Roster-stable variant: only agents valid on ≥ 80% of the period's days.
- **O4 Variants, same estimator.**
  - **V-g, field removed:** every ẑ_k projected off the goal subspace (span{ĝ}; in #51 span{ĝ, ĝ_i}) before averaging.
  - **V-c, common removed:** x̃_id = x̄_id − mean_{j≠i} x̄_jd (leave-one-out swarm day mean), with the noise correction for both terms. Removes every swarm-common component (goal field, shared sub-task schedule, day effects).
  - **Robustness:** n = 16 and 64; chat-only statements; rarefied to 8 statements per agent-day (10 draws); calendar-day clock instead of the active-day clock.
  - **No within-period time-mean centering.** Subtracting a period's own time average creates a spurious t_w dependence in a stationary process (edges vs middle; shown in the synthetic). Centering is by the regime mean only (the whitener); persistent agent and goal content shows up as the plateau q.
- **O5 Aging slope A (primary statistic).** Weighted least squares of C(t_w, t_w + τ) on τ fixed effects + log t_w + n_wk (the number of gaps > 36 h between consecutive active days crossed by the pair), over entries with t_w ≥ 2 and 1 ≤ τ ≤ τ_max = ⌊(T − 1)/2⌋, weights |I(d, d′)|. A > 0 means older states decorrelate more slowly at a fixed lag; units: C per e-fold of t_w. The same statistic on C_m (A_m), V-g (A_g), V-c (A_c), and per agent (A_i, agents with ≥ 6 valid days).
  - **A_early:** the same regression on the matched window t_w ∈ {2, 3, 4}, τ ∈ {1, 2}, identical in every period (the short-vs-long comparison).
  - **A_late:** entries with t_w ≥ the median t_w of the period's entries (saturation test).
  - **Kickoff transient K:** mean over τ = 1…3 of C(2, 2 + τ) − C(1, 1 + τ). The kickoff day is the quench; it is excluded from A and reported here.
- **O6 Model fits** (WLS on all entries with t_w ≥ 2, τ ≥ 1, weights |I|):
  - **M0 stationary:** C = q + (c0 − q) e^{−τ/τ0}.
  - **MQ quench + stationary ("interrupted aging"):** M0 plus a kickoff-specific component of relative weight b² that decays as e^{−(t−1)/τ_q}: C = [q + (c0 − q)e^{−τ/τ0} + b² e^{−(t_w + t_w′ − 2)/τ_q}] / √((1 + b² e^{−2(t_w−1)/τ_q})(1 + b² e^{−2(t_w′−1)/τ_q})), t_w′ = t_w + τ.
  - **M1 aging (Box-Cox clock, see Model):** μ free.
  - Leave-one-day-out CV error of each model (drop every entry involving day d, fit, predict those entries; summed over d); μ̂ with a 90% parametric-bootstrap CI.
- **O7 Secondary and descriptive.**
  - weekend coefficient β_wk from O5 (cold restarts);
  - active-day vs calendar-day clock (CV error of M1 under each);
  - own-join clock vs kickoff clock for #51's late joiners (A_i and M1 CV per joiner, t_w from the agent's first day vs the kickoff);
  - rejuvenation at step changes: mean M1 residual of pairs straddling 04-14 / 04-20 (#38) and 07-09 / 08-05 / 08-25 (#51) vs pairs on one side at equal τ;
  - memory stabilization: agent-day mean `memory_stats.jaccard_prev` regressed on log t_w with agent fixed effects;
  - scaling collapse: C plotted against s_μ̂(t_w + τ) − s_μ̂(t_w).

## Null / baseline
*Specified 2026-10-03, before any real-data run.*

- **Primary null: stationarity, C depends on τ only.** Parametric bootstrap from the period's fitted M0. Latent agent-day states μ_id = a_i[√q h_i + √(c0 − q) u_i(d) + √(1 − c0) η_id]: u_i a 32-d stationary OU process with correlation e^{−τ/τ0} in active-day time, η iid per day, h_i static (agent style + goal content), a_i² = the agent's mean S_id. Statements z = μ_id + ε with E|ε|² = 1 − a_i², using the period's real agent-day presence and statement counts n_id. 500 draws give the null distribution of A (and of A_g, A_c, A_m, each with its own fitted M0); one-sided p = P(A_null ≥ A_obs). Because the surrogates use the real counts, any estimator bias tied to sampling (e.g. statement counts trending over the period) is inside the null.
- **Agent-level null:** median A_i = 0 (Wilcoxon signed rank over agents with ≥ 6 valid days). Robust to the parametric form, but treats agents as independent, which they are not fully.
- **Rivals:**

| Rival | Mechanism | Predicts |
| --- | --- | --- |
| R0 stationary relaxation | content relaxes (OU) around a fixed field | A = 0; μ̂ = 0; M0 best in CV |
| R1 quench then stationary ("interrupted aging") | the kickoff sets an atypical state that relaxes within τ_q | K > 0; A > 0 only from early t_w, A_late ≈ 0; MQ beats M1 in CV |
| R2 field-driven drift toward ĝ, no aging | the agents' mean moves along ĝ during the period | A > 0 on raw C, A_g ≈ 0 |
| R3 common drift / shared schedule | the swarm moves together through sub-tasks | A_c ≈ 0 while A > 0; A_m large |
| R4 agent turnover | roster changes move the swarm mean | A_m ≠ 0 with all agents, ≈ 0 on the roster-stable set; per-agent A unaffected |
| R5 sampling and style artifacts | statement counts, chat/intention mix, message length trend over the period | reproduced by the parametric null; absent in the chat-only and rarefied variants |
| R6 cold restarts | weekends and daily restarts reset content | β_wk < 0; the calendar clock fits as well as the active-day clock |
| **H20 aging** | the relaxation time grows with age (trap / glassy dynamics) | A > 0 for t_w ≥ 2; A_late > 0; A_g > 0; M1 best in CV with μ̂ > 0 |

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R0–R6 in "Null / baseline" (stationary relaxation; quench then stationary; drift toward ĝ; common drift; turnover; sampling artifacts; cold restarts).
**Locked holdout used for confirmation:** none. Planned: #1 (30 days, regime I), the #51 tail (09-07 → 09-18), short holdout periods (`analysis/confirm_h20.py`, written and dry-run on stand-ins, not run; rules under "Confirmatory predictions").

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Agent-day states from own chat + intentions, whitened per regime, noise-corrected; assumptions listed. Not checked: embedding-model swap, family invariance. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Stationarity is the object. The pre-registered isotropic null failed on real data (fluctuations live in ~5–12 of 32 dimensions) and was replaced (Amendment 2). Holiday days and phased weeks break stationarity in short periods. Clocks compared (calendar vs active day, S2). |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Beats the calibrated stationary null only in #38 (A, A_c, A_g p = 0.002). Random-effects A over 10 long + medium goals +0.021 ± 0.021. LODO-CV computed but uninformative at this sampling (Amendment 1). |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | The aging signatures fail: no late slowing (A_late RE −0.07 ± 0.08), no scaling collapse with 0 < μ ≤ 1 except #51's weak μ̂ = 0.22, which is not robust to chat-only. |
| E interventional | predicts the change across a natural experiment | 0 | No rejuvenation at NE17/NE18 (#38) or #51's joins and #focus room. Holidays (unplanned perturbations) break correlations, as any model with an external field would predict. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Full-pipeline size 0.03–0.07 and power 0.37–0.42 (μ = 0.5) / 0.68–0.88 (μ = 1) at real sampling. μ̂ recovered with a large SD. Pitfalls quantified (centering, counts, ĝ drift). Real-data miscalibration diagnosed, fix validated on low-rank synthetic data (size 0.05–0.12 long; 0.17 short). Robust to n = 16/64, chat-only, rarefaction in #38. |
| G ground truth | agrees with known structure | 1 | #38's transient starts with the operator's Year-1 correction (NE36). The large negative slopes sit on Thanksgiving (#20) and Christmas (#24); the debate week (#12) is phased by design. |
| H comparative | beats the named rivals | 0 | Where any t_w dependence exists (#38), the quench rival R1 wins: front-loaded, A_late ≤ 0, MQ best in CV by 2×. R2 (ĝ drift) and R4 (turnover) are ruled out as explanations of #38. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | No aging to transfer. #38's kickoff relaxation does not appear in the regime-I long goals (#4, #8). Holdout not run. |

## Prediction
*Written 2026-10-03, before running any analysis on real data.*

**What I had seen when writing this:** the `LOG.md` entries of 2026-10-03 (H02/H03/H04/H05/H07/H09 round-1 results; H09 E5 "no aging at 1-min resolution" in activity; H09: memory size is a per-agent set point restored at each consolidation), H01's card through Amendment 3 and H10's card (predictions only; I did not open their results files), and *counts only* for the candidate periods: active days, agents, and statements per agent-day (medians 29–140; ≥ 91% of agent-days have ≥ 8 statements). No embedding similarity, correlation, alignment or goal-vector statistic had been computed or read.

**Primary predictions (long periods #4, #8, #38, #51; per period, then summarized across periods by random effects, never pooled):**
- **P1, kickoff transient.** K > 0 in ≥ 3 of 4 long periods: the kickoff day's content is atypical (reading and planning the goal). Expected under both R1 and H20, so it is a check of the instrument, not of aging. Credence 0.8.
- **P2, aging slope.** A > 0 with parametric-bootstrap p < 0.05 in ≥ 2 of 4 long periods. Credence 0.5. I expect agents to settle into routines in long goals (outreach, maintenance, repeated reporting), so consecutive days become more alike late in the period.
- **P3, not field drift.** Where P2 holds, A_g > 0 (p < 0.10): the slowing is not just the mean settling along ĝ. Credence 0.8 given P2 (ĝ is one direction of 32).
- **P4, aging beats interrupted aging.** Where P2 holds, M1 has the lowest leave-one-day-out CV error of M0, MQ and M1, μ̂'s 90% CI excludes 0, and A_late > 0 (point estimate). Credence 0.4 given P2. With 17–45 days, saturation within the window (R1) is a real competitor.
- **P5, exponent.** Where aging is found, sub-aging: 0 < μ̂ ≤ 1; the random-effects summary of μ̂ over the long and medium periods lies in 0.2–0.8. Credence 0.5.
- **P6, individual vs collective (direction only).** A_c > 0 in at least one period where P2 holds (individual agents age beyond the shared schedule), credence 0.5; A_m and A have the same sign, credence 0.7.
- **P7, short vs long goals in the same window (exception (d)).** The random-effects mean of A_early over the short periods and over the long + medium periods do not differ (90% CI of the difference contains 0): the kickoff clock is universal and long goals don't age faster in their first days. Credence 0.55. The alternative "long goals age more" predicts long > short.
- **#51 specifically** (private, stable individual roles, HH102 predicts glassy dynamics): a high plateau q and A > 0; credence 0.5. Joins and the #focus room may rejuvenate.

**Secondary (reported, not counted in the verdict):**
- **S1 cold restarts:** β_wk < 0 in ≥ 3 of 4 long periods (0.6).
- **S2 clock:** the active-day clock has lower M1 CV error than the calendar clock in ≥ 3 of 4 long periods (0.6).
- **S3 robustness:** where P2 holds, A has the same sign at n = 16 and 64, chat-only and rarefied (0.7).
- **S4 joiner clock (#51):** descriptive; weak expectation that the agent's own clock fits joiners at least as well as the kickoff clock (0.5).
- **S5 rejuvenation at step changes (#38, #51):** descriptive.
- **S6 memory:** agent-day `jaccard_prev` flat in log t_w (0.6, per H09's set-point result).
- **Medium periods (#6, #13, #18, #19, #20, #27):** the same per-period rule as the long periods; they enter the random-effects summaries (transfer within exploration).

**Per-period verdict rule (long and medium periods):**
- **supported:** A > 0 (p_boot < 0.05), A_g > 0 (p_boot < 0.10), M1 beats M0 and MQ in leave-one-day-out CV with μ̂'s 90% CI > 0, and A > 0 in the chat-only variant and in the median A_i.
- **failed:** p_boot ≥ 0.05 with design power ≥ 0.8 against the μ = 0.5 reference (Box-Cox clock at the period's fitted nuisance parameters q, c0, τ0, S̄, and real sampling); or A < 0 with one-sided p < 0.05 (dynamics speeding up with age).
- **mixed:** anything else, labelled by cause: "interrupted aging" (A > 0 but MQ wins CV or A_late ≤ 0), "field drift" (A > 0, A_g not), "underpowered" (not significant, power < 0.8).
- **Short periods:** role "stationary contrast", verdict **descriptive**; they enter P7 only.

**Card-level verdict (round 1):** **supported** (exploratory) if ≥ 2 of the 4 long periods are supported, none fails, and the random-effects summary of A over the long + medium periods is > 0 (p < 0.05). **Failed** if ≥ 3 of 4 long periods fail, or the random-effects summary of A is ≤ 0. **Mixed** otherwise. Multiplicity: P2's "≥ 2 of 4 at 0.05" has a family-wise false-positive rate ≈ 0.014 under the global null; everything else is descriptive.

**Overall credences:** supported 0.25, mixed 0.45, failed 0.3.

**What counts against H20:** a well-powered A ≈ 0 for t_w ≥ 2 (stationary relaxation), or a positive A that is fully explained by the kickoff transient (MQ, A_late ≈ 0), by drift along ĝ (A_g ≈ 0), or by the shared schedule and turnover (A_c ≈ 0 with A_m ≫ A).

**Amendment 1 (2026-10-03, after the synthetic validation, before any real-data run).** The numbers behind each change are in "Synthetic validation" under Results.
1. **P2 gets a co-primary statistic, A_c** (swarm-common removed). P2 holds if A > 0 or A_c > 0 at one-sided p < 0.025 (Bonferroni over the two). The original "A at p < 0.05" is reported alongside.
   - Why: in large swarms the shared stationary components add correlated noise to A. A_c removes them and has twice the power for individual aging in #51 (0.91 vs 0.44 at μ = 0.5).
   - A_c is blind to shared-only aging (rejection 0.02–0.09), which A still catches.
   - P3 is applied to whichever route passed: A_g, or A_c on the field-removed states.
2. **P4: leave-one-day-out CV is demoted to descriptive.** At village sampling it barely separates the models: M1 beats M0 and MQ in 25–45% of stationary datasets and in 35–55% of aging datasets, and M1 vs MQ is close to a coin flip.
   - P4 becomes: μ̂'s 90% CI excludes 0, and A_late > 0.
   - A_late is the statistic the kickoff transient does not reach: rejection 0.04–0.06 under MQ vs 0.14–0.52 under aging.
3. **"Failed" also covers rejected aging.** A period also fails when neither A nor A_c is significant and both lie below the 5th percentile of their μ = 0.5 alternative distributions at the fitted nuisance parameters.
   - Why: design power against μ = 0.5 is only 0.33–0.44 in the long periods at a² = 0.15, so "power ≥ 0.8" alone would make "failed" unreachable.
   - The power criterion now uses the co-primary test.
4. **P7 is reinterpreted; its rule is unchanged.** In the matched window, A_early is dominated by the tail of the kickoff transient: an uncorrelated transient with τ_q = 1.5 d shifts A_early by +0.05 to +0.13, as much as μ = 0.5 aging. P7 therefore compares the kickoff relaxation of short and long goals, not aging proper.
5. **O4's centering claim, made precise.** Per-agent time-mean centering manufactures aging in short periods (A = +0.16 in a 5-day week and +0.04 in a 10-day goal, on stationary data) and gives a slightly negative A in long ones.
6. **The μ = 0.5 reference depends on the fitted relaxation.** It rescales the fitted stationary relaxation. If the fitted relaxing component is small, or faster than a day, aging is invisible at day resolution and the design power is low by construction. This is reported per period.

**Amendment 2 (2026-10-03, post hoc: after the first real-data run, prompted by a calibration failure).**
- **What failed.** Under the pre-registered (isotropic) null, z-scores of A across the 29 periods have robust SD 2.07 (1 expected), and 31% have |z| > 2 in both directions. The same holds for A_c (3.1) and for K (3.0), which is not an aging statistic.
- **Why.** The null draws latent day-to-day fluctuations isotropically in the 32 whitened dimensions. Real content fluctuates in far fewer: participation ratio 8–12 for agents' day-to-day deviations, 4–9 for the swarm-common part (#51: 25 and 9). Var(C entries) scales like 1/n_eff, which inflates the SD of A by roughly √(32/n_eff) ≈ 2–3.
- **Fix.** The same stationary swarm model, but its shared and private latent components are drawn with covariance shapes estimated from the period's own day-to-day deviations (noise-subtracted, 5% shrinkage to isotropic). The synthetic check (`synthetic/aniso_*.json`), on low-rank stationary data (n_eff 9/5):
  - the isotropic null rejects 17–40% (one-sided, α = 0.05);
  - the estimated-shape null rejects 5–12% in long goals and 17% in a 5-day week;
  - power against μ = 0.5 drops to 0.10–0.30.
- **Real data under the fix:** robust z-SD 1.07; heterogeneity I² (long + medium) falls from 0.87 to 0.45.
- **Which verdict counts.** Per-period verdicts are reported under both nulls. The headline uses the calibrated (Amendment 2) null, and the G folders show both. No verdict became "supported" through the change: #6 lost its pre-registered "supported", and #19 went from "failed" to "mixed".

**Confirmatory predictions (written 2026-10-03 after round 1, before any holdout run; `analysis/confirm_h20.py`, Amendment-2 null).**
- **C1, #1** (30 days, regime I, the same charity goal as #38), interrupted aging rather than aging:
  - (a) no late slowing: A_late is not significantly > 0 (credence 0.75);
  - (b) the kickoff relaxation recurs: A_early > 0 with p < 0.05 (credence 0.4, because the regime-I long goals #4 and #8 showed none).
  - C1 passes if both hold.
- **C2, #51 tail** (09-07 → 09-18, d = 46–55): fitted on d ≤ 45, M1 predicts the tail's C entries with lower weighted MSE than M0 and the free-lag MT. This tests whether the weak late slowing (μ̂ 0.22) extrapolates. Credence 0.4.
- **C3, short holdout periods:** the Amendment-2 null stays calibrated on new data (robust z-SD of A ≤ 1.5). Credence 0.35: the stand-in dry run gave 1.83, driven by phased and holiday weeks.
- **Dry run on stand-ins** (#4 for #1, #51 days 36–45, nine short periods): C1 false (no kickoff relaxation in #4), C2 false (M0 predicts better), C3 false (1.83). The script refuses the holdout without `--confirm --i-understand-this-uses-the-locked-holdout`.

## Results by goal period
| Period | Role | Verdict (Amendment-2 null) | Key numbers (p one-sided, Amendment-2 null; power = co-primary vs μ = 0.5) |
| --- | --- | --- | --- |
| [G04](goalperiod-subhypotheses/G04/README.md) | long, T = 25, N = 6 | mixed: underpowered: not significant, μ = 0.5 aging not rejected (pre-registered null: mixed) | A +0.021 (p 0.385); A_c +0.052 (p 0.240); A_late +0.028; K -0.078; μ̂ +0.30; power 0.11 |
| [G08](goalperiod-subhypotheses/G08/README.md) | long, T = 18, N = 4 | mixed: underpowered: not significant, μ = 0.5 aging not rejected (pre-registered null: mixed) | A -0.001 (p 0.511); A_c +0.080 (p 0.110); A_late -0.177; K +0.092; μ̂ -0.30; power 0.20 |
| [G38](goalperiod-subhypotheses/G38/README.md) | long, T = 17, N = 14 | mixed: interrupted aging: no late slowing (pre-registered null: mixed) | A +0.102 (p 0.002); A_c +0.072 (p 0.002); A_late -0.043; K +0.117; μ̂ +1.36; power 0.48 |
| [G51](goalperiod-subhypotheses/G51/README.md) | long, T = 45, N = 32 | failed: stationary within power: μ = 0.5 aging rejected (pre-registered null: mixed) | A +0.012 (p 0.078); A_c +0.009 (p 0.146); A_late +0.111; K +0.060; μ̂ +0.22; power 1.00 |
| [G06](goalperiod-subhypotheses/G06/README.md) | medium, T = 15, N = 4 | mixed: underpowered: not significant, μ = 0.5 aging not rejected (pre-registered null: supported) | A +0.071 (p 0.120); A_c +0.063 (p 0.202); A_late +0.040; K +0.014; μ̂ +1.38; power 0.20 |
| [G13](goalperiod-subhypotheses/G13/README.md) | medium, T = 10, N = 6 | mixed: underpowered: not significant, μ = 0.5 aging not rejected (pre-registered null: mixed) | A -0.002 (p 0.473); A_c +0.040 (p 0.208); A_late -0.825; K -0.047; μ̂ -0.13; power 0.19 |
| [G18](goalperiod-subhypotheses/G18/README.md) | medium, T = 10, N = 8 | mixed: underpowered: not significant, μ = 0.5 aging not rejected (pre-registered null: mixed) | A -0.038 (p 0.611); A_c -0.118 (p 0.928); A_late +0.784; K -0.003; μ̂ -0.05; power 0.18 |
| [G19](goalperiod-subhypotheses/G19/README.md) | medium, T = 10, N = 8 | mixed: underpowered: not significant, μ = 0.5 aging not rejected (pre-registered null: failed) | A -0.060 (p 0.661); A_c -0.087 (p 0.916); A_late -0.001; K -0.092; μ̂ -0.43; power 0.12 |
| [G20](goalperiod-subhypotheses/G20/README.md) | medium, T = 10, N = 10 | failed: dynamics speed up with age, A < 0 (pre-registered null: failed) | A -0.214 (p 0.982); A_c -0.109 (p 0.930); A_late -0.863; K +0.192; μ̂ -1.46; power 0.27 |
| [G27](goalperiod-subhypotheses/G27/README.md) | medium, T = 10, N = 10 | mixed: underpowered: not significant, μ = 0.5 aging not rejected (pre-registered null: mixed) | A -0.002 (p 0.511); A_c -0.099 (p 0.964); A_late +0.104; K +0.049; μ̂ -0.14; power 0.15 |
| [G05](goalperiod-subhypotheses/G05/README.md) | short, T = 5, N = 4 | descriptive: stationary contrast (pre-registered null: descriptive) | A +0.357 (p 0.287); A_c +0.420 (p 0.323); A_late +0.474; K +0.214; power 0.08 |
| [G10](goalperiod-subhypotheses/G10/README.md) | short, T = 5, N = 7 | descriptive: stationary contrast (pre-registered null: descriptive) | A +0.103 (p 0.072); A_c +0.166 (p 0.006); A_late -0.207; K -0.000; power 0.13 |
| [G11](goalperiod-subhypotheses/G11/README.md) | short, T = 5, N = 7 | descriptive: stationary contrast (pre-registered null: descriptive) | A -0.193 (p 0.778); A_c -0.134 (p 0.707); A_late -0.086; K -0.170; power 0.18 |
| [G12](goalperiod-subhypotheses/G12/README.md) | short, T = 5, N = 7 | descriptive: stationary contrast (pre-registered null: descriptive) | A -0.834 (p 1.000); A_c -0.552 (p 1.000); A_late -1.844; K -0.081; power 0.12 |
| [G16](goalperiod-subhypotheses/G16/README.md) | short, T = 5, N = 7 | descriptive: stationary contrast (pre-registered null: descriptive) | A +0.122 (p 0.271); A_c -0.049 (p 0.625); A_late +0.149; K -0.161; power 0.07 |
| [G17](goalperiod-subhypotheses/G17/README.md) | short, T = 5, N = 7 | descriptive: stationary contrast (pre-registered null: descriptive) | A +0.172 (p 0.208); A_c +0.353 (p 0.046); A_late -0.074; K -0.033; power 0.07 |
| [G21](goalperiod-subhypotheses/G21/README.md) | short, T = 5, N = 9 | descriptive: stationary contrast (pre-registered null: descriptive) | A +0.354 (p 0.012); A_c +0.011 (p 0.385); A_late +0.310; K +0.021; power 0.16 |
| [G23](goalperiod-subhypotheses/G23/README.md) | short, T = 5, N = 10 | descriptive: stationary contrast (pre-registered null: descriptive) | A -0.044 (p 0.790); A_c +0.094 (p 0.016); A_late -0.125; K +0.051; power 0.08 |
| [G24](goalperiod-subhypotheses/G24/README.md) | short, T = 5, N = 10 | descriptive: stationary contrast (pre-registered null: descriptive) | A -0.600 (p 1.000); A_c -0.623 (p 1.000); A_late -1.507; K -0.076; power 0.17 |
| [G25](goalperiod-subhypotheses/G25/README.md) | short, T = 5, N = 10 | descriptive: stationary contrast (pre-registered null: descriptive) | A +0.330 (p 0.018); A_c +0.148 (p 0.002); A_late +0.281; K -0.099; power 0.13 |
| [G26](goalperiod-subhypotheses/G26/README.md) | short, T = 5, N = 10 | descriptive: stationary contrast (pre-registered null: descriptive) | A -0.125 (p 0.661); A_c +0.105 (p 0.317); A_late -0.860; K +0.002; power 0.04 |
| [G30](goalperiod-subhypotheses/G30/README.md) | short, T = 5, N = 11 | descriptive: stationary contrast (pre-registered null: descriptive) | A +0.153 (p 0.226); A_c +0.106 (p 0.134); A_late +0.174; K -0.082; power 0.07 |
| [G31](goalperiod-subhypotheses/G31/README.md) | short, T = 5, N = 12 | descriptive: stationary contrast (pre-registered null: descriptive) | A +0.006 (p 0.443); A_c +0.068 (p 0.317); A_late +0.072; K -0.047; power 0.14 |
| [G35](goalperiod-subhypotheses/G35/README.md) | short, T = 5, N = 12 | descriptive: stationary contrast (pre-registered null: descriptive) | A +0.136 (p 0.309); A_c +0.200 (p 0.070); A_late +0.236; K -0.158; power 0.06 |
| [G39](goalperiod-subhypotheses/G39/README.md) | short, T = 5, N = 15 | descriptive: stationary contrast (pre-registered null: descriptive) | A -0.035 (p 0.754); A_c -0.048 (p 0.806); A_late +0.010; K +0.039; power 0.24 |
| [G40](goalperiod-subhypotheses/G40/README.md) | short, T = 5, N = 15 | descriptive: stationary contrast (pre-registered null: descriptive) | A -0.061 (p 0.749); A_c -0.067 (p 0.806); A_late +0.116; K -0.033; power 0.18 |
| [G41](goalperiod-subhypotheses/G41/README.md) | short, T = 5, N = 15 | descriptive: stationary contrast (pre-registered null: descriptive) | A +0.240 (p 0.034); A_c +0.205 (p 0.010); A_late +0.126; K -0.044; power 0.14 |
| [G42](goalperiod-subhypotheses/G42/README.md) | short, T = 5, N = 16 | descriptive: stationary contrast (pre-registered null: descriptive) | A +0.035 (p 0.204); A_c +0.071 (p 0.100); A_late +0.042; K +0.036; power 0.06 |
| [G44](goalperiod-subhypotheses/G44/README.md) | short, T = 4, N = 18 | descriptive: stationary contrast (pre-registered null: descriptive) | A +0.081 (p 0.253); A_c +0.081 (p 0.224); A_late –; K -0.021; power 0.07 |

## Results
*Exploratory round 1: 29 non-holdout goal periods (4 long, 6 medium, 19 short); no holdout row read. Numbers come from `data/processed/H20-content-aging/summary.json` (`analysis/summarize.py`); per-period detail is in the G folders; pipeline `analysis/run_periods.py` (`--null iso` pre-registered, `--null aniso` Amendment 2). Figures: [`figures/H20_summary.pdf`](figures/H20_summary.pdf) (one page), [`figures/forest_A.pdf`](figures/forest_A.pdf), [`figures/mu_and_power.pdf`](figures/mu_and_power.pdf), [`figures/synthetic_validation.pdf`](figures/synthetic_validation.pdf), [`figures/summary_obs.pdf`](figures/summary_obs.pdf), and `G<NN>/figures/aging_G<NN>.pdf`.*

**Headline.** We found no aging. Across the 10 long and medium goals, the random-effects aging slope is A = +0.021 ± 0.021 (C per e-fold of t_w; I² = 0.45) under the calibrated null; under the pre-registered null it is −0.000 ± 0.021 (I² = 0.87).
- **Card verdict:** **mixed** under the calibrated null: no long period is supported, one fails (#51), and the RE mean is > 0 but not significant. Under the pre-registered null the literal rule gives **failed** (RE mean ≤ 0).
- **The one strong age effect, #38, is a kickoff relaxation.** Lag-1 correlation rises 0.66 → 0.72 → 0.78 → 0.87 over the first four active days, then stays at ≈ 0.90 for 12 days. Day-to-day content does not lock in further as the goal gets older.
- **#51:** aging as strong as μ = 0.5 is rejected (A = +0.012; μ = 0.5 would give ≈ +0.034, p = 0.003 for an A this small). A weak late slowing remains (A_late = +0.11, μ̂ = 0.22 [0.07, 0.41]), but it vanishes in chat-only statements (A = −0.001), so it lives in the intention stream (CONSOLIDATE plans).

**Synthetic validation (axis F; `synthetic/*.json`, `figures/synthetic_validation.pdf`).** All runs use real counts and an assumed signal grid.
- **Size and power of the A test:**
  - size 0.04–0.07 against stationary OU nulls with one or two timescales; the full pipeline with a refitted null gives 0.03–0.07;
  - power against Box-Cox aging μ = 0.5: 0.33–0.44 (long goals), 0.23–0.38 (medium), 0.04–0.16 (5-day weeks);
  - against μ = 1: 0.65–0.88; against the Bouchaud trap model x = 0.5: 0.47–0.96.
  - Power hardly depends on the signal-to-noise level (a² = 0.05–0.30): it is limited by days and agents, not statements.
- **Rivals:**
  - the kickoff transient leaks into A modestly (rejection 0.11–0.25) but not into A_late (0.04–0.06); K detects it (0.61–0.94);
  - drift toward ĝ makes raw A reject 0.54–0.88, and V-g removes it (0.04–0.08);
  - A_c is blind to shared-only aging (0.02–0.09) but has the most power for private aging in big swarms (#51: 0.91–0.98 vs 0.32–0.88 for A).
- **Pitfalls:**
  - statement counts falling from 60 to 8 over the period do not bias A (0.03–0.07);
  - per-agent time-mean centering manufactures aging in short periods (+0.16 in a 5-day week, on stationary data).
- **LODO-CV model ranking is close to chance:** M1 beats M0 and MQ in 25–45% of stationary and 35–55% of aging datasets. μ̂ is recovered with SD 0.24–0.5 (#38, #8 sampling), biased low at μ = 0.5 in #38 (0.29). Hence Amendment 1.

**Calibration on real data (Amendment 2).** The pre-registered null was anti-conservative on real data (robust z-SD 2.07). Content fluctuations are low-dimensional (participation ratio 4–12 out of 32). The estimated-shape null brings the robust z-SD to 1.07. The remaining outliers are short, phased or holiday weeks: #12 (z −7.1), #24 (−6.9), #25 (+2.8), #21 (+2.7). Only #38 (+3.6) among the long goals, and #20 (−2.1).

**Outcome vs prediction** (calibrated null unless stated):

| Prediction | Expected | Observed | Outcome |
| --- | --- | --- | --- |
| P1 kickoff transient K > 0 in ≥ 3/4 long | 0.8 | K > 0 in 3/4 (#8, #38, #51; significant in #38, #51); #4 −0.08. RE over all 29 periods +0.012 ± 0.014 | holds (point estimates) |
| P2 aging slope A or A_c > 0, p < 0.025, in ≥ 2/4 long | 0.5 | 1/4 (#38). Pre-registered null also 1/4 via A (#38); #8 passed via A_c only (p 0.020), not under the calibrated null (0.110) | **fails** |
| P3 not field drift (where P2 holds) | 0.8 | #38: A_g = +0.111 (p 0.002) ≥ A | holds |
| P4 μ̂ CI > 0 and A_late > 0 (where P2 holds) | 0.4 | #38: μ̂ = 1.36 [0.86, 1.84] but A_late = −0.043; the t_w dependence is all in days 1–5 | **fails** (interrupted aging, R1) |
| P5 0 < μ̂ ≤ 1; RE μ̂ in 0.2–0.8 | 0.5 | RE μ̂ = +0.30 ± 0.31 (I² 0.58), CI includes 0; no period with aging. #38's μ̂ = 1.36 fits the transient, not aging | **fails** (no aging to measure) |
| P6 A_m same sign as A | 0.7 | 7/10 long + medium (exceptions: A ≈ 0 in #4, #8, #27) | holds |
| P7 A_early, short vs long + medium (no difference) | 0.55 | short −0.015 ± 0.072, long + medium +0.035; difference +0.05 [−0.08, +0.18] | holds, uninformative (the CI is wide; A_early mostly reflects kickoff residue) |
| #51 high plateau and A > 0 | 0.5 | Plateau q = 0.50 (highest with #6); A = +0.012 (p 0.08); μ = 0.5 aging rejected | half: plateau yes, aging no |
| S1 β_wk < 0 in ≥ 3/4 long | 0.6 | 3/4 negative (#4 −0.04, #8 −0.04, #38 −0.003), none significant; #51 +0.006 | holds weakly |
| S2 active-day clock beats calendar clock in ≥ 3/4 long | 0.6 | 1/4 (#51). The calendar clock has slightly lower M1 CV error in #4, #8, #38 (differences ≤ 0.5 × 10⁻³ except #38: 1.94 vs 2.45) | **fails** |
| S3 robustness signs where P2 holds | 0.7 | #38: A > 0 at n = 16 (+0.07), 64 (+0.10), chat-only (+0.15), rarefied (+0.10), calendar clock (+0.09) | holds |
| S4 joiner clock (#51) | descriptive | 6 joiners: median A_i +0.045 on the kickoff clock, −0.010 on their own clock; no aging on either | no evidence for agent-own aging |
| S5 rejuvenation at step changes | descriptive | none: straddling-pair M1 residual +0.012 (#38) and +0.007 (#51), above the null mean | none |
| S6 memory `jaccard_prev` flat in log t_w | 0.6 | flat in #4 (−0.004 ± 0.006); falls in #8 (−0.023 ± 0.007); **rises in regime III** (#38 +0.026 ± 0.004, #51 +0.007 ± 0.002) | mixed: regime-III memories stabilize over a goal while chat content does not age |

**Heterogeneity and phase diagram.**
- **By regime:** RE A in regime I (8 long + medium) is −0.003 ± 0.025 (I² = 0); in regime III (#38, #51) it is +0.053 ± 0.045 (I² = 0.90).
- **By goal length:** the long goals' RE A is +0.039 ± 0.029, the short weeks' −0.015 ± 0.072 (I² 0.85).
- **The pattern across periods** is "settle quickly, then stationary". The settling is visible only where the kickoff was a big content quench (#38, which began with an operator correction). Regime-I goals show no kickoff transient.
- **Fitted stationary timescales** of the relaxing part: τ ≈ 2 days (#6, #8, #20) to 9–11 days (#51, #38). Plateau q = 0.17–0.50.

**Caveats.**
- **Calibration:** the headline uses a null chosen after seeing the real-data z-distribution (Amendment 2). It was validated on synthetic data, but it is still a post-hoc choice. It is conservative relative to the pre-registered one. It remains anti-conservative in 5-day weeks (synthetic size 0.17), so short-period p-values are not trustworthy.
- **Power:** against moderate aging (μ = 0.5) it is 0.11–0.48 under the calibrated null, except in #51 (1.00). "No aging" is a firm statement only for #51 (μ = 0.5 rejected) and for strong aging (μ ≈ 1) in the long goals. Weak sub-aging (μ ≲ 0.3) cannot be excluded anywhere.
- **Day resolution:** aging at sub-day scales (within a session, between consolidations) is invisible. H09 found none at 1-min resolution in activity.
- **Instrument:** a single embedding model (bge-small) and whitening basis. Style and topic are not separated beyond ĝ removal and common removal; agent style is part of the plateau q. No embedding-model swap yet.
- **Statement mix:** intentions (session goals, CONSOLIDATE plans) carry #51's weak late slowing. Chat-only results differ in #51.
- **Phases and holidays:** in short periods, structured weeks and holidays dominate A. They are external fields on specific days, not age effects.
- **Unit choice:** #38 and #51 were kept whole across their step changes (exception (c)), and no rejuvenation was seen. A per-sub-unit analysis would have only 4–8 days.

**Next steps.**
1. Run the holdout (C1–C3) once Vivian signs off.
2. Embedding-model swap and a topic-only representation (meaning clusters, ψ = √p).
3. Sub-day two-time functions (30-min windows, `agent_win30`), with t_w in hours since kickoff and since each consolidation.
4. A null with explicit phase switches (renewal) for structured weeks.
5. A link to H17 (mixing times) and H01 D3.3.a (relaxation after a goal change): #38's τ_q ≈ 2 active days is a direct measurement of D3.3.a's relaxation time.

## Notes
- 2026-10-03: promoted from HH101.
- 2026-10-03: observables, null, rivals and predictions written before any real-data run. Proposed named variant for `physics-models/DEFINITIONS.md` ("Agent state (vector), agent-day statement mean"): the mean of an agent's unit-normalized whitened statement vectors over one active day, with the noise-corrected self-overlap S = |x̄|² − v; and "activity time (active-day clock)": days of the period with village activity, weekends and holidays not counted.
- 2026-10-03: synthetic validation run (`analysis/synthetic.py`); Amendment 1 written before real data. Per-period predictions written (`analysis/write_period_cards.py --predict`) before `run_periods.py` ran on any period.
- 2026-10-03: real-data calibration failure found after the first run (z-overdispersion; low-dimensional fluctuations); Amendment 2 written and validated on synthetic data; both nulls reported.
- 2026-10-03: confirmatory rules fixed in `analysis/confirm_h20.py` (not run; dry run on stand-ins only).
- Proposed shared changes (not made): move the goal/kickoff embedding vectors (H01's `goals_raw.npy` + `goals.parquet`) into `infra/shared/embeddings/`; add the two named variants above and an "anisotropic null" pitfall to `physics-models/11-vector-spins` (embedding two-time and overlap statistics need nulls with the empirical fluctuation shape; isotropic surrogates are 2–3× too narrow).

## Round 2 redirects (2026-10-04)
*From the round-1 reflection (`writeup/round1-reflection/round1-reflection.pdf`).*
- **Where round 1 went sideways:** No aging appeared: content dynamics are Markov.
- **What the direction is really after:** The swarm has no long-term internal memory; all persistence is stored outside the agents.
- **H20-R1.** Persistent content order is explained entirely by persistent fields (goal prompt, artifacts); without them content decorrelates within a day (E3, E4).
- **H20-R2.** The ~2–4 day kickoff relaxation is set by artifact build-up, not agent memory.
