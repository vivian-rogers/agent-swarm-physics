# H33: The diversity–productivity curve is an inverted U: the swarm's operating point

**Status:** **round 1b done (2026-10-04, improved data):** on DQ4 work commits (#30+, 12 units, 1,290 agent-days), fixed activity bins and both embedding models the null stands (b₁ +0.032, p 0.17; b₂ −0.040, p 0.31; curvature worsens CV). A right-side drop in some bge specs is a #51 tail effect. Natives: G51 mixed (rival pairs null; 4-agent support class concave), G39 and G42 support the null reading. Round 1 (exploratory) done 2026-10-04: **not supported.** No inverted U between agent-day content diversity (PR10, self-repeats removed) and write output in 17 non-holdout periods; the null wins (pre-registered rule label: mixed). No operating point. `analysis/confirm.py` written and dry-run, not run. Low priority (Vivian): lean test.
**Fields:** stat mech, sociophysics, info theory
**Origin:** HH119 (`../hypohypotheses/HYPOHYPOTHESES.md`; `../promotion-shortlist.md`); companions HH105 (loops, not consensus, collapse dimensionality) and HH113 (stuckness predicts output collapse).
**Definitions used:** Agent; Regime (whitening is per regime; never pooled across 2026-03-24 without a unit split); Agent state, variant *vector* (whitened statement vectors, d = 32); Driving / external field (absorbed by day fixed effects). New named variant proposed for `DEFINITIONS.md` (H33 may not edit it): **"effective dimensionality (agent-day, self-deduplicated, rarefied PR)"**, defined under Observables; it is H12's bias-corrected participation ratio applied to one agent's day after H12's self-repeat removal.

## Question
Daily content diversity (participation ratio, self-repeats removed) vs output: too little (loops) and too much (unfocused) both underperform, with an optimum in between. *Check:* PR vs artifact output per agent-day across periods, with period fixed effects; locate the peak.

Practical aim (usefulness-first batch): produce a number or rule an operator of an LLM agent swarm could compute from logs and act on: "keep each agent's daily content PR near x*", or, failing that, an honest statement that no such operating point exists in these data.

## Model
**From:** `physics-models/11-vector-spins` (primary), `physics-models/06-neutral-cooperative-dynamics` (swarm-level reading).
- **Model 11 reading.** Agent i's chat statements on day d are unit vectors s ∈ S^{31} after per-regime whitening. The PR of their covariance, PR = (tr Σ)²/tr Σ², counts the directions the agent's content occupies: PR → 1 is a frozen spin (the agent restates one thing: a loop), PR → d is an isotropic, "paramagnetic" agent (content spread over everything the regime talks about). H33 is the claim that output is maximal at an intermediate effective temperature: Φ(PR) has an interior maximum at PR*.
- **Model 06 reading (swarm level, secondary).** Neutral cooperative replication proceeds at a rate ∝ 1 − λ (the chance two random individuals hold different "species", here topics), which rises monotonically with diversity, while too much innovation (large μ) prevents a cooperator core from forming. Model 06 by itself therefore predicts the *monotone* rival at the swarm level unless the core-dissolution side is reached; it is used only to name the swarm-day test.
- **Variant used here:** a phenomenological response curve, y = α_{i,u} + δ_d + f(PR_{id}) + γ·controls + ε, with f estimated by a quadratic, a natural cubic spline and Simonsohn's two-lines test. No dynamics are fitted.

## Data scheme (`scheme/`)
`scheme/build.py` builds `data/processed/H33-diversity-productivity/` (agent-day and swarm-day tables, one subfolder per goal period, `_provenance.json`) from shared tables only: `embeddings/statements.parquet`, `embeddings/chat_bge_small.npy`, the per-regime whiteners (`common.load_whitener`), `artifact_mentions` (+ `artifact_commands_text` error flags), `artifacts` (file → repo parent), `activity_bins`, `actions`, `calendar`, `roster`. Imports (never modifies) H12 (`h12lib.pr_rarefied`, `h12lib.pr_balanced`, `posthoc.dedup_rows`) and H15 (`h15common.WRITE_VERBS`).
- **Days:** non-holdout only (calendar flag and `holdout_mask`, plus a guard that aborts if a holdout day appears). Claude Code agent excluded.
- **Analysis unit:** goal period; #36 is split at the 2026-03-24 regime boundary (36a/36b) because the whitener changes.

## Candidate goal periods
All non-holdout periods. **Eligibility rule (pre-registered; applied mechanically once):** a period enters the per-period test if (a) it has ≥ 30 agent-days with PR10 defined, (b) ≥ 4 agents with ≥ 3 such days, and (c) write turns > 0 on ≥ 20% of those agent-days (write verbs are essentially absent before 2025-10, H15, so the output measure is degenerate there). Ineligible periods are listed with the reason. Per-period folders go in `goalperiod-subhypotheses/G<NN>/`.

## Observables
Per agent-day (i, d), eligible periods, non-holdout:
1. **x = PR10 (primary diversity):** take agent i's chat statements on day d; remove self-repeats with H12's rule (`posthoc.dedup_rows`: drop a statement whose raw bge cosine to an *earlier* statement by the same agent that day exceeds 0.95); whiten with the regime's whitener (d = 32); rarefy to n = 10 statements, compute H12's bias-corrected PR (Wishart-unbiased â/b̂), ratio of means over 20 draws. Agent-days with < 10 deduplicated statements are missing. Robustness: PR6, PR15; TV10 (semantic spread, tr S: "size" rather than "shape").
2. **Self-repetition share** = 1 − n_dedup/n_raw (the HH105 loop rate).
3. **Output** (H15's write verbs: `git push`, `git commit`, `deploy`, PR/MR create or merge, repo/project create):
   - **Primary (pre-registered): y = log(1 + write turns)**, a write turn being a distinct (agent, time) computer-use turn carrying a write verb (identical to H15's V_out numerator).
   - Secondary: commits (`git commit` turns), deploys (`deploy` turns), distinct artifacts advanced (distinct repos or sites receiving a write verb; files mapped to their parent repo), clean writes (write turns without an error flag). Each as log(1 + count).
4. **Controls (primary spec):** log(n_raw chat statements), log(1 + engaged minutes) (activity_bins state ∈ {act, talk}). Fixed effects: agent × unit and day.
5. **Half-day split (reverse causation):** the day's calendar window is cut at its midpoint; PR6 (rarefied n = 6) and write turns are computed per half.
6. **Swarm-day:** PRday_dedup (H12's agent-balanced estimator on deduplicated statements: 5 agents × 10 statements, 50 draws) vs log(1 + write turns per active agent).

**Tests.**
- **T1 shape (primary, pooled within-unit):** y = α_{i,u} + δ_d + f(x) + γ·controls. (a) Quadratic: β₂ and the vertex x_v. (b) Natural cubic spline (4 df, knots at x quantiles): location of the maximum and the flat region {x: f(x_max) − f(x) ≤ SE[f(x_max) − f(x)]}. (c) **Two-lines test** (Simonsohn 2018) with the Robin Hood breakpoint: initial breakpoint = median of the flat region; re-set to the 100·|z₂|/(|z₁|+|z₂|) percentile of the flat region; slopes b₁ (x < x_c) and b₂ (x ≥ x_c) with SEs clustered by agent × unit.
- **T2 per period:** the same model within each eligible period (agent and day FE), two-lines at the pooled breakpoint, CR1 SEs clustered by agent with t(G−1) reference; random-effects (DerSimonian–Laird) meta-analysis of b₁ and b₂ across periods (partial-pooling exception (d)).
- **T3 out-of-sample adequacy:** 5-fold day-blocked cross-validation (whole days held out, within-unit FE re-estimated on training days) of FE+controls vs + linear vs + quadratic vs + spline.
- **T4 reverse causation (half-day cross-lag):** β_fwd: PR6_am → log(1+writes_pm) | log(1+writes_am); β_rev: log(1+writes_am) → PR6_pm | PR6_am; same FE and controls.
- **T5 common cause (engagement):** T1 with and without the activity controls.
- **T6 loops (HH113, contemporaneous):** self-repetition share → y, within unit, same FE and controls.
- **T7 swarm-day:** two-lines and quadratic of swarm-day y on PRday_dedup with unit FE (expected underpowered).

## Null / baseline
- **Null (flat):** f ≡ 0 within agent × unit after day FE and controls: diversity carries no information about output.
- **Rival R1, monotone (more diversity is better, or worse):** f monotone over the observed range; in particular a concave, saturating f, which a quadratic test misreads as an inverted U (the reason the two-lines test is primary).
- **Rival R2, reverse causation:** shipping changes what agents talk about (reporting variety after a push or deploy), so output → diversity, not diversity → output.
- **Rival R3, common cause:** engaged agents both talk more varied and write more; the x–y association disappears under activity controls.
- **Shared-field null:** day FE remove goal kickoffs (day 1 is the most diverse day, H12), outages and schedule; agent × unit FE remove family style (H13: family alignment is mostly style) and agent-level verbosity.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R1 monotone (incl. saturating), R2 reverse causation, R3 engagement common cause.
**Locked holdout used for confirmation:** `analysis/confirm.py` (written 2026-10-04, dry-run on non-holdout stand-ins, **not run**): held-out #22, #28, #29, #32a/b, #34, #45–#50 and the #51 tail, filtered by the card's eligibility rule; sensitivity without #34 and #45 (reuse policy; see "Confirmatory plan").

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | PR10 from bge chat embeddings (H12 dedup and estimator, per-regime whitening), output from logged write verbs in computer-use turns (H15). Not invariant: write verbs are absent before 2025-10 (17 of 34 non-holdout units ineligible), the GitLab era (#51) writes partly through `glab api` (not counted), and PR is relative to each regime's corpus. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Measurement audit: within-agent split-half reliability of PR10 0.55 (TV10 0.78), built into the synthetic. Leave-one-period-out stable (no drop makes P1 pass; min p 0.24). No time-scale audit below one day. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 0 | Day-blocked CV (5 folds × 5 seeds): FE + controls 0.9467; + linear PR10 0.9447 (−0.2%); + quadratic 0.9471; + spline 0.9521. Curved terms lose to linear in 5/5 seeds; PR10 adds almost nothing. |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | Signature (interior peak with both sides significant) absent; self-repetition → output (HH113, P6) null (p 0.84); swarm-day pattern absent (P7). |
| E interventional | predicts the change across a natural experiment | 0 | Not attempted (no NE gives exogenous variation in content diversity). |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Real design, real residual noise, measured reliability: two-lines rule false-positive 0% (null), 4–7% (plateau rival; quadratic test 25–46%); power 22/82/100% at 0.2/0.4/0.8 residual SD; peak recovered (13.0–13.2 vs 13.2). Robust to PR6, TV10, outcome choice; PR15 differs (a #51 tail effect). No embedding swap. |
| G ground truth | agrees with known structure | 0 | No known operating point to compare against. |
| H comparative | beats the named rivals | 0 | H33 does not beat the null or R1 (monotone). R2 (reverse causation) and R3 (engagement) are not distinguishable: nothing to explain. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | 0/14 estimable periods supported (3 mixed, 11 failed, 3 n/a); holdout not run. |

**Scorecard: A1 B1 C0 D0 E0 F1 G0 H0 I0.**

## Prediction
*Written 2026-10-04 (UTC), before running the analysis on real data. Nothing relating diversity to output had been computed. Looked at beforehand (design only): the list of write-like verbs in `artifact_mentions`, and the distribution of raw chat statements per agent-day (median 30; 80% of non-holdout agent-days have ≥ 10).*

**What H33 predicts (the hypothesis as stated):**

| # | Prediction | Counts against |
| --- | --- | --- |
| P1 | **Inverted U (primary, T1):** spline maximum interior (between the 10th and 90th percentiles of PR10); two-lines b₁ > 0 and b₂ < 0, each p < 0.05 (two-sided, clustered). | either slope not significant or of the wrong sign; maximum at the edge of the support |
| P2 | **Per period (T2):** the random-effects meta-estimates of b₁ and b₂ both have the inverted-U signs, and ≥ half of eligible periods show the sign pattern b₁ > 0, b₂ < 0 (significance per period not required: underpowered). | meta signs wrong, or < half of periods with the pattern |
| P3 | **Adequacy (T3):** quadratic or spline beats linear in day-blocked CV MSE. | linear ≤ both |
| P4 | **Not reverse-causal (T4):** β_fwd (nonlinear forward term) at least as strong as β_rev; β_rev not significant alone. | β_rev significant with β_fwd ≈ 0 |
| P5 | **Not engagement (T5):** b₁ and \|b₂\| shrink by < 50% when activity controls are added. | shrink ≥ 50% |
| P6 | **Loops cost output (T6, HH113 contemporaneous):** self-repetition share has a negative within-agent slope on y (p < 0.05). | slope ≥ 0 or n.s. |
| P7 | **Swarm-day (T7):** same sign pattern as P1 at swarm-day level (no significance required; underpowered). | opposite pattern |

**Operating point:** if P1 holds, report x* (the Robin Hood breakpoint and the spline maximum, cluster-bootstrap 90% CI), its percentile among agent-days, and the share of agent-days on each side.

**Verdict rule.** **Supported** if P1 and P2 hold and P4 and P5 do not fail. **Failed** if P1 fails and the spline maximum is at the edge of the support, or b₂ ≥ 0. **Mixed** otherwise. The rival winning is named: R1 (b₁ significant, b₂ n.s. or same sign; linear as good as curved in CV), R2 (P4 fails), R3 (P5 fails), null (no slope significant). Per period: **supported** if b₁ > 0 and b₂ < 0 with at least one significant; **failed** if both slopes share a sign or the spline maximum is at an edge; **mixed** otherwise.

**Calibrated prior (written down so the outcome can be scored against it):** inverted U supported ≈ 20%; monotone increasing or saturating (R1) ≈ 35%; flat ≈ 35%; monotone decreasing ≈ 10%. My point prediction is that **P1 fails**: the low-diversity (loop) side underperforms (b₁ > 0) but the high-diversity side does not (b₂ n.s.), so the curve saturates rather than turns over, and the operator-facing result is a low-side threshold, not an optimum. P6 more likely than not holds (≈ 60%). Power will be the main limitation: agent-day PR at n = 10 is noisy, and errors in x attenuate curvature more than slope.

## Results by goal period
**Round 1b (2026-10-04):** each folder has a `**Verdict (1b):**` line on work commits (summary in "Round 1b" below); G39, G42, G51 also carry native tests (`**Role:** native`). The table keeps round 1. Exploratory, non-holdout, eligible units only. b₁ / b₂: two-lines slopes below / above the pooled breakpoint x_c = 15.97 (log(1 + write turns) per PR10 unit; agent and day FE plus activity controls; CR1 by agent, t(G − 1)). Figures in each folder.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G17](goalperiod-subhypotheses/G17/README.md) | exploratory | n/a | 32 agent-days; 1 above x_c |
| [G18](goalperiod-subhypotheses/G18/README.md) | exploratory | failed | b₁ −0.056 (p 0.56), b₂ −0.27 (p 0.43); spline max at edge |
| [G19](goalperiod-subhypotheses/G19/README.md) | exploratory | failed | b₁ −0.008, b₂ −0.56 (p 0.23): both negative |
| [G20](goalperiod-subhypotheses/G20/README.md) | exploratory | failed | U-shaped signs (b₁ −0.007, b₂ +0.18); max at edge |
| [G25](goalperiod-subhypotheses/G25/README.md) | exploratory | mixed | U-shaped signs (b₁ −0.033, b₂ +0.013), interior max |
| [G30](goalperiod-subhypotheses/G30/README.md) | exploratory | failed | both positive (b₁ +0.116, p 0.064; b₂ +0.109); linear +0.093 (p 0.028) |
| [G31](goalperiod-subhypotheses/G31/README.md) | exploratory | failed | both positive (b₂ +0.110, p 0.075); self-repetition −2.6 (p 0.022) |
| [G33](goalperiod-subhypotheses/G33/README.md) | exploratory | failed | b₁ −0.076 (p 0.012), b₂ +0.165; max at edge |
| [G35](goalperiod-subhypotheses/G35/README.md) | exploratory | failed | both negative; self-repetition −4.6 (p 0.010) |
| [G36](goalperiod-subhypotheses/G36/README.md) (36b) | exploratory | failed | max at edge (PR10 21.2); b₁ +0.036, b₂ −0.009 |
| [G38](goalperiod-subhypotheses/G38/README.md) | exploratory | mixed | inverted-U signs, n.s. (b₁ +0.122, p 0.28; b₂ −0.059, p 0.26) |
| [G39](goalperiod-subhypotheses/G39/README.md) | exploratory | n/a | 3 agent-days above x_c |
| [G40](goalperiod-subhypotheses/G40/README.md) | exploratory | n/a | 2 agent-days above x_c |
| [G41](goalperiod-subhypotheses/G41/README.md) | exploratory | failed | both positive (b₂ +0.194, p 0.10) |
| [G42](goalperiod-subhypotheses/G42/README.md) | exploratory | failed | U-shaped signs (b₂ +0.305, p 0.092); max at edge |
| [G44](goalperiod-subhypotheses/G44/README.md) | exploratory | failed | both positive, n.s. |
| [G51](goalperiod-subhypotheses/G51/README.md) | exploratory | mixed | 746 agent-days (47% of the pool): inverted-U signs, n.s. (b₁ +0.052, p 0.30; b₂ −0.097, p 0.076) |

Ineligible under the pre-registered rule (listed, not tested): #2–#8, #10–#13, #16, #21, #23, #24, #26, #27 (write turns on < 20% of agent-days; write verbs are essentially absent before 2025-10), #36a (1 day), #37 (20 agent-days with PR10).

## Results
*Run 2026-10-04 (`analysis/evaluate.py`; numbers in `data/processed/H33-diversity-productivity/results.json`). Figure summary: [`figures/H33_summary.pdf`](figures/H33_summary.pdf); pooled curve [`figures/curve_pooled.pdf`](figures/curve_pooled.pdf); synthetic [`figures/synthetic_validation.pdf`](figures/synthetic_validation.pdf).*

**Headline.** Within an agent and period, after day fixed effects and activity controls, the day's content diversity carries no detectable information about its write output. No inverted U: both two-lines slopes have the inverted-U signs but neither is significant (b₁ = +0.035, p 0.26; b₂ = −0.035, p 0.35, at x_c = 15.97), and the spline's "flat region" spans PR10 13.9–29.2, the whole upper half of the data. There is no operating point to report.

**Sample.** 17 eligible units, 1,592 agent-days with PR10 (of 2,348 agent-days in those units; days with < 10 deduplicated chat statements are excluded and write less: 19 vs 31 write turns on average), 208 agent × unit clusters. #51 is 47% of the pool. PR10 quantiles 8.6 / 13.2 / 17.8 (10/50/90%); within-agent SD 2.5; within-agent reliability 0.55.

**Synthetic validation (axis F, before real data).** Real design and real residual noise (permuted within unit), signal planted on a latent PR with the measured reliability, 200 replicates per condition:
- False "inverted U" verdicts (P1 rule): null 0%, linear 0–1%, log 1–3%, plateau (rise then flat) 4–7%. The quadratic test calls the plateau an inverted U 25–46% of the time, which is why two-lines is primary.
- Power of the P1 rule for a symmetric inverted U (peak at the median): 22%, 82%, 100% for peak-to-edge drops of 0.2, 0.4, 0.8 residual SD (≈ 16%, 30%, 50% fewer write turns). Peak location recovered (median 13.0–13.2 vs true 13.2). An asymmetric inverted U (peak at the 75th percentile) is mostly read as monotone (P1 power 5–26%).
- P2 (per-period sign rule without significance) has a 10% false-positive rate under the null and 76% power at 0.4 SD.

**Outcome vs prediction.**

| # | Prediction | Observed | Verdict |
| --- | --- | --- | --- |
| P1 | interior spline max; two-lines b₁ > 0, b₂ < 0, both p < 0.05 | max interior (16.4; bootstrap 90% CI 11.1–19.2, interior in 71%); b₁ +0.035 (p 0.26), b₂ −0.035 (p 0.35); quadratic β₂ −0.0026 (p 0.27), vertex 18.3 (outside the 10–90% range) | **failed** |
| P2 | meta signs b₁ > 0, b₂ < 0; ≥ half of periods with the pattern | meta b₁ +0.010 ± 0.018 (p 0.59), **b₂ +0.028 ± 0.035 (wrong sign)**; pattern in 3/14 (21%; null expectation ≈ 25%) | **failed** |
| P3 | curved beats linear in day-blocked CV | linear 0.9447 < quadratic 0.9471 < spline 0.9521 (5/5 seeds); linear beats FE + controls (0.9467) by only 0.2% | **failed** |
| P4 | not reverse-causal: β_rev not significant alone | half-day cross-lag (1,258 agent-days): PR6_am → writes_pm std +0.023 (p 0.36; quadratic term p 0.23); writes_am → PR6_pm std +0.031 (p 0.30) | not failed, uninformative (nothing to orient) |
| P5 | b₁, \|b₂\| shrink < 50% with activity controls | without controls b₁ +0.042 (p 0.17), b₂ −0.015 (p 0.69); with controls b₁ shrinks 18% | not failed, moot (n.s. either way) |
| P6 | self-repetition share → y slope < 0, p < 0.05 | +0.17 ± 0.83 (p 0.84); per-period meta −0.56 ± 0.57 (p 0.33, I² 0.72): negative in #31 (p 0.022) and #35 (p 0.010), positive in #51 (p 0.066) | **failed** |
| P7 | swarm-day: same sign pattern | 141 days: b₁ −0.22 (p 0.025, only 10 days below x_c = 10.7), b₂ −0.010 (p 0.66); quadratic β₂ +0.006 (p 0.22) | **failed** (pattern absent; the low side has the opposite sign on 10 days) |

**Verdict.** By the pre-registered rule the label is **mixed** (P1 failed, but the spline maximum is interior and b₂ < 0, which the rule does not count as a failure). Substantively H33 is **not supported** and the named winner is the **null**: no slope is significant, curvature hurts out of sample, the per-period meta-analysis has b₂ of the wrong sign, and nothing transfers across periods. My calibrated point prediction (P1 fails through a saturating curve, b₁ > 0 significant, b₂ n.s.) was half right: P1 failed and there is no right-side drop, but the low-side ("loop") shortfall is not significant either.

**Effect-size bounds (spline contrasts, residual SD 0.86).** From the best PR10 (16.4) to the 90th percentile (17.8): +0.02 SD, 95% upper bound 0.10 SD (≈ 9% fewer write turns). Within the observed range, high diversity does not cost output. From the 10th percentile (8.6) to the peak: +0.32 SD, CI −0.09 to +0.73 (biased upward by choosing the peak). A low-side shortfall of up to ~0.7 SD in the bottom decile is not excluded.

**Robustness** (11 specs; none passes P1):
- Outcomes: commits b₁ +0.040 (p 0.074); deploys flat; clean writes flat; **distinct artifacts advanced b₁ +0.023 (p 0.014), b₂ −0.007 (p 0.70)**, a plateau shape. That is one of 11 specs, so not Bonferroni-significant.
- x variants: TV10 flat; PR6 b₁ +0.035 (p 0.12); **PR15 b₂ −0.135 (p 3.5 × 10⁻⁵, 128 agent-days above x_c = 17.8)**. Post hoc (`analysis/posthoc.py`) shows this is a #51 tail effect: #51 alone gives b₂ −0.137 (p 0.037); without #51 the breakpoint moves to 11.1 and b₂ turns positive; PR10 on the same rows shows no right-side drop. A lead for confirmatory test C5, not a result.
- Without #51 the curve is flat (spline max at the edge; b₁ −0.019, b₂ +0.007). Regime I is flat; regime III has weak inverted-U signs (b₁ +0.047, p 0.25; b₂ −0.041, p 0.31).

**Reading.** Day-level content diversity, measured from chat, is a poor handle on output in this swarm: within-agent PR10 is half noise (reliability 0.55), and the part that is signal does not move write output. The self-repetition result (HH113) is heterogeneous: loops cost output in two shared-objective regime-II/III weeks (#31, #35) but not overall. Whatever H12's loop weeks (#38–#40) cost, it does not show up as same-day write turns at agent-day level.

## Caveats
- **Power and measurement.** Agent-day PR10 has within-agent reliability 0.55. The test detects a symmetric inverted U of ≥ 0.4 residual SD about 80% of the time, but not 0.2 SD (22%), and it reads an inverted U peaking at the 75th percentile as monotone.
- **Output is write turns, not value** (H15). Repeated pushes count; GitLab-era API writes (`glab api`) are not counted; deploy and commit counts follow tooling conventions that change across regimes.
- **Selection.** 32% of agent-days in eligible units lack PR10 (< 10 deduplicated chat statements), and those days write less. The curve describes chatty days only.
- **Time scale.** Diversity and output may couple within hours, not days. The half-day test is underpowered (PR6 is noisier).
- **#51 dominates the pool** (47%); the only right-side signals (#51 b₂ p 0.076; PR15) come from it.
- **Multiplicity.** 7 predictions, 11 robustness specs, 17 periods. One robustness spec at p = 0.014 and two per-period self-repetition slopes at p < 0.05 are about what chance produces.
- Day fixed effects remove swarm-level co-variation by design; the swarm-day test (141 days) is the only swarm-level check and is weak. Agent narration and Jev scores were not used.
- #36b's self-repetition slope (+10.9) is degenerate: almost no self-repeats in that unit.

## Round 1b (improved data, 2026-10-04)

### What changed
Behind `H33_ROUND=r1b` (`scheme/h33common.py`); the default path reproduces round 1. Outputs in `data/processed/H33-diversity-productivity/r1b/` (`results.json`, `native.json`, per-period tables, `eligibility.parquet`); figures in `figures/r1b/` and `G<NN>/figures/*_r1b.pdf`. Scripts: `scheme/build.py` (`build_r1b`), `analysis/evaluate.py` (switched), `analysis/r1b_native.py` (new).
- **Productivity = log(1 + DQ4 agent work commits)** (`canonical & ~imported & author_kind == "agent" & ~automated`; 112k automated agent-identity commits excluded). Secondary: distinct files, lines changed without bulk commits (line stats cover 56%), and the round-1 write turns on the same rows. Half-day split on commit times.
- **Units from #30 on** (the ledger is dense from #30; earlier zeros are ambiguous). The eligibility rule is unchanged except that the "output > 0 on ≥ 20% of agent-days" clause uses work commits: **12 eligible units** (#30, #31, #33, #35, #36b, #38–#42, #44, #51; 1,290 agent-days with PR10) instead of 17 (1,592). #17–#20 and #25 drop out; work commits and write turns correlate 0.77 on the rows kept.
- **Engaged-minute control from `activity_bins_fixed`** (ρ 0.75 with the buggy table).
- **Diversity under both embedding models and three dedups** (DQ5 `statements_white32_<model>`, `statement_flags`): H12's rule per model (`self_repeat_bge` / `self_repeat_gte`), copies only (`self_repeat_both`), restatements (either flag). PR10 under bge (DQ5 white32) correlates 0.93 with round 1's PR10, and 0.77–0.79 with gte. The round-1 PR columns (statements and embeddings unchanged) are carried over.

### Round 1 vs round 1b
| | Prediction | Round 1 (write turns, 17 units) | Round 1b (work commits, 12 units) | Verdict (1b) |
| --- | --- | --- | --- | --- |
| P1 | inverted U: b₁ > 0, b₂ < 0, both p < 0.05, interior max | b₁ +0.035 (p 0.26), b₂ −0.035 (p 0.35), x_c 15.97; max 16.4 | b₁ +0.032 (p 0.17), b₂ −0.040 (p 0.31), x_c 17.66; spline max 17.3 (interior), flat region 16.1–29.2; quadratic vertex 25.9 | **failed** |
| P2 | meta signs and ≥ half of periods with the pattern | meta b₂ +0.028 (wrong sign); 3/14 | meta b₁ +0.003 (p 0.89), **b₂ +0.017 (wrong sign)**; pattern 4/8; verdicts 1 supported (#38), 3 mixed, 4 failed, 4 n/a | **failed** |
| P3 | curved beats linear in day-blocked CV | linear 0.9447 < quad 0.9471 < spline 0.9521; linear vs FE −0.2% | linear 0.9503 < quad 0.9529 < spline 0.9554 (5/5 seeds); linear vs FE −0.4% | **failed** |
| P4 | β_rev not significant alone | fwd +0.023 std (p 0.36), rev +0.031 (p 0.30) | fwd +0.022 (p 0.42), rev +0.045 (p 0.22) | not failed, uninformative |
| P5 | slopes shrink < 50% with activity controls | b₁ shrinks 18% | b₁ +0.032 → +0.032 (no shrink) | not failed, moot |
| P6 | self-repetition → output < 0 (p < 0.05) | +0.17 (p 0.84) | +0.97 (p 0.48); per-period meta −1.50 ± 0.98 (p 0.13): negative in #31 (p 0.003), #35 (p 0.0005), #42 (p 0.03) | **failed** (heterogeneous) |
| P7 | swarm-day same pattern | b₁ −0.22 (p 0.025) | b₁ −0.25 (p < 0.001, 101 days), b₂ +0.01 | **failed** |

**Robustness (13 specs; P1 rule):**
- Outcomes: distinct files b₁ +0.033 (p 0.19), b₂ −0.047 (p 0.24); lines (no bulk) linear +0.054 (p 0.017), no curvature; write turns on the same rows b₁ +0.051 (p 0.20). No outcome passes P1.
- **Diversity variants:** every variant has b₂ < 0. It is significant for bge with H12's dedup on DQ5 vectors (−0.119, p 0.034), bge without restatements (−0.142, p 0.003) and PR15 (−0.139, p 0.001; PR15 passes P1 with b₁ +0.053, p 0.033). Under gte it is not significant (−0.048 to −0.138, p 0.06–0.28). **Post hoc (`r1b_native.py`): without #51 every right-side slope vanishes** (bge restate +0.014, PR15 −0.005, bge H12 +0.013), while dropping #38 leaves them; this is the round-1 "#51 tail" lead (C5), now seen in more specs, not a swarm-wide high-diversity penalty, and it is model-dependent.
- Without #51 the curve is flat (b₁ +0.018, b₂ −0.008); regime III alone b₁ +0.033 (p 0.19), b₂ −0.055 (p 0.22).

**Natives (predictions dated before the run, in the folders):**
- **G51** (DQ6 roles): **mixed.** Same-role rival pairs on the same day show no diversity–output relation (87 pair-days, 8 pairs: linear p 0.21, quadratic p 0.58), but the 4-agent "support" role class is concave (quadratic −0.0047, p 0.0005, vertex PR10 ≈ 12.5; t(3) reference, one of three classes).
- **G39** (one world per agent): **supported** (null reading): ρ(mean PR10, work commits) +0.10, with files +0.19 (10 agents), within-agent slope p 0.83.
- **G42** (videos per agent, link-based): **supported** (null reading): ρ(mean PR10, videos first linked) +0.10 (p 0.76).

**Verdict changes.** Card-level: still **not supported**, the null wins (pre-registered label: mixed, as before). Per period (round 1 → 1b): #38 mixed → **supported** (b₂ −0.166, p 0.0005); #36b failed → mixed; #44 failed → mixed; #51 mixed → mixed; #33, #35, #41, #42 failed → failed; #30, #31 failed → n/a (too few agent-days above the new breakpoint); #39, #40 n/a → n/a; #17 n/a, #18–#20 failed, #25 mixed → n/a (pre-#30). One supported period out of 8 estimable is about what the per-period rule gives by chance (null false-positive rate of the sign rule ≈ 10% per period).

**Scorecard (1b): A1 B1 C0 D0 E0 F1 G0 H0 I0** (unchanged). F gains the embedding swap that round 1 lacked (agent-day PR is moderately model-dependent, ρ 0.77; the null is not), but no new synthetic. Ratings (suggested): completeness 40 → 50, faithfulness 0.5, usefulness 1.5.

### What the work ledger changes about "productivity"
Write turns counted repeated pushes and missed GitLab API writes; the ledger counts commits that landed, without the 112k automated ones. On the rows both measures cover they correlate 0.77, and every round-1 conclusion survives: content diversity carries no usable information about committed output (CV gain 0.4% for a linear term, curvature hurts). The ledger shrinks the sample to the git-dense era (#30+) and makes the one apparent signal (a high-diversity penalty in some bge specs) visibly a #51 property. Productivity now also has an attributable, period-native check (G39: own worlds; G42: own videos), and both agree with the null.

## Amendments
1. **2026-10-04, before any outcome was examined.** (a) The first eligibility count included NaN PR values stored as non-null; fixed in `scheme/build.py` (NaN → null) and eligibility recomputed. Same rule, same 17 units. (b) Measured the within-agent split-half reliability of PR10 (0.55) and TV10 (0.78) (`analysis/reliability.py`, x side only) and used it in the synthetic. (c) Synthetic shapes: replaced an unbounded exponential "saturating" curve with a bounded plateau and a log curve, and clipped x to its 2nd–98th percentile inside every shape, so tails can't dominate. (d) The per-period "spline maximum" check uses a 3-df spline; stated in each G folder's prediction before the run.
2. **2026-10-04, after the exploratory run, in `analysis/confirm.py` only (no holdout data read).** C2 made one-sided (overfitting that worsens CV MSE is consistent with "no usable information") and C3's threshold set to 0.30 SD. Both changes came after the non-holdout dry run (559 stand-in agent-days gave curved terms 1–3% worse, and a C3 upper bound of 0.30).

## Confirmatory plan (written, not run)
`analysis/confirm.py` refuses to run without `--confirm --i-understand-this-uses-the-locked-holdout` and refuses again unless this card and the script are committed (reuse policy, item 1). `--dry-run` runs the identical pipeline on non-holdout stand-ins (#30, #31, #35, #38, #41, #42, #44, and #51's last two non-holdout weeks as a "51t"); it ran clean 2026-10-04 (reading: "round-1 null reading confirmed").
- **C1** H33 as stated (the P1 rule) on the pooled held-out units. Predicted to **fail** (credence it passes 0.10).
- **C2** No PR10 term improves day-blocked CV MSE by ≥ 1%. Predicted to hold (0.75).
- **C3** The penalty from the best PR10 to the 90th percentile has 95% upper bound < 0.30 SD. Predicted to hold (0.65).
- **C4** Low-side lead: b₁ > 0, one-sided p < 0.05 (0.25).
- **C5** Post hoc #51 lead: PR15 b₂ < 0, p < 0.05 in the #51 tail (0.20).
- **Reading.** H33 is confirmed only if C1 passes. The null reading is confirmed if C1 fails and C2 and C3 hold.
- **Reuse.** H02 has used #45 (activity timing). Unrun scripts target #34 (six hypotheses) and, for H12, swarm-day content PR on most held-out periods. H33's observable (the PR–output relation) is unexamined everywhere. If H12 runs first, the overlap in x must be disclosed in both cards and in `LOG.md`.

## Notes
- 2026-10-04: promoted from HH119 by Vivian (usefulness-first batch); wave 2.
- 2026-10-04: pre-registration written (observables, nulls, rivals, P1–P7, verdict rule, eligibility rule, calibrated prior) before any real-data run.
- 2026-10-04: synthetic validation (200 reps × 32 conditions), real-data run, per-period folders, post hoc checks, confirm script (dry-run only), summary page.
