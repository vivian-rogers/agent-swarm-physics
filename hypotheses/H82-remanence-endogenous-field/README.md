# H82: Remanence: the endogenous part of the mean field

**Status:** **exploratory round 1 done (2026-10-04, non-holdout only). Mixed: the previous period leaves a trace on day 1 (Δγ₁ ≈ 0.15, 3× the null 95th percentile, both models), but it does not decay within 5 days and it is carried by each agent's own previous content, not by the village record.**
- **Remanence exists:** day-1 loading on the previous village centroid beyond kickoff, operator, prior and placebo centroids: 0.158 / 0.153 (S0 q95 0.055 / 0.063), 25 boundaries; not the old goal's wrap-up.
- **Asymmetric but persistent:** γ[P−1] 0.16 vs γ[P+1] 0.07; no decay over days 1–5 (P3 fails); half of it looks like H81's slow mode.
- **Members, not the record:** adding the agent's own previous content removes it (−0.02 / −0.06; post hoc). Newcomers are too few to test (inconclusive). Reading carries part of it (NE15, one model).
- Card and predictions written 2026-10-04 20:07 UTC before any real-data statistic; synthetic validation came first (Amendments A1–A3). `analysis/confirm.py` written and dry-run, **not run**.
**Question (GOALS.md):** **Q3** (collective order beyond fields: hysteresis of the village mean field) and **Q2** (what is field and what is coupling at a goal boundary: quench vs remanence).
**Fields:** stat mech (vector spins, hysteresis, quench), info theory, sociophysics
**Literature:** [Kolchinsky & Wolpert 2018](../../literature/kolchinsky-2018-semantic-information-autonomous-agency.md) (egregore framing); [Heylighen 2016](../../literature/heylighen-2016-stigmergy-universal-coordination-mechanism.md) (the record as the carrier of a trace). No literature refinement was attached to HH290.
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime (whitening per regime; every boundary lies inside one regime); Driving / external field (goal text, kickoff, room kickoffs, human messages, #51 agent goals); Agent state, variant *vector*, in H01's named form **agent state (vector), whitened statement mean** (DQ5 `style_resid`); H54's **quench target (kickoff)** and **kickoff remanence**; H08's **exposure (turn read-out)** via the context ledger. New named variants proposed for DEFINITIONS.md (defined under Observables): **endogenous field (previous centroid)**, **remanence coefficient γ_d**, **remanence excess Δγ_d**, **newcomer (boundary)**.
**From:** HH290 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` (egregore section) · **Models:** `physics-models/11-vector-spins/` (primary: mean field with an exogenous and an endogenous part), `physics-models/04-semantic-information/` (framing: the record as the store), `physics-models/12-information-dynamics/` (tool: in-flight placebo for the read-out channel)
**Data inputs (shared tables first):** DQ5 `embeddings/agent_day_{style_resid,white32,style_resid_period}_{bge_small,gte_modernbert}.npy` + `agent_day.parquet`; DQ5 statement vectors `statements_style_resid32_<model>.npy` + `statements.parquet` + `chat_index` (N3 only); shared `goal_fields`; `kicks_classified` (human messages); DQ1 context ledger (`context_ledger_items`, `context_ledger_turns`; N3); `roster` (tenure); `rooms_timeline`; `period_units`; `calendar`; `holdout_mask`.

## Source HH (verbatim from the HH list, including literature refinements)
Remanence: the egregore is the endogenous part of the mean field. Decompose each agent-day content vector into an exogenous field (kickoff and operator directions), a prior field (the agent's leave-period-out mean, which carries family and style), and an endogenous field (the previous period's village centroid and older village history). Prediction: on day 1 of a new goal there is a remanent alignment with the previous period's centroid beyond the new kickoff and the agent's own prior, decaying with τ of days. This is hysteresis, not quench (H10, H54). It is also carried by agents who never saw the previous period, so it lives in the record, not in members. *Check:* regression on `goal_fields`, leave-period-out agent means and lagged centroids (DQ5 vectors, both models, style residuals); in-flight placebo at matched lag; newcomers vs veterans at each boundary. *Kill:* the endogenous coefficient ≈ 0 after removing the exogenous and prior fields, or it is carried only by veterans (individual memory, not an egregore).
  *Models:* 04, 11 · *Revamps:* H01, H10, H54 · *Periods:* every goal boundary; NE32 newcomers

## Question
On the first days of a new goal, does an agent's content still point at the previous period's village centroid, beyond the new kickoff, the operator's messages and the agent's own prior? If so, how fast does that remanence decay, and do agents who never saw the previous period carry it too?

## Design: two layers (Vivian, 2026-10-04)
- **Replication** (role `replication`): the remanence regression at every eligible goal boundary (P−1 → P, both non-holdout, same regime). The per-boundary row belongs to the new period P (`G<P>` folder). The boundary is the object (named exception (c)); each boundary is fitted on its own.
- **Natives** (role `native`): **NE27** (batch join of three agents with empty memories at the #10 kickoff: newcomers vs veterans on the same day), **NE32** (three newcomers in isolated rooms on 07-09: do agents that never saw regime-III history carry it?), **NE15** (rooms: read vs posted-but-unread previous-period content at matched posting time, the in-flight placebo for the read-out channel).

## Model
**From:** `physics-models/11-vector-spins/`. The mean field acting on agent i on day d of period P has three parts:

  v_{i,d} = α_P·X_ex(P, d, i) + β_P p_i + γ_{P,d} e_{P−1}^{(−i)} + δ_P k_{P−1} + ε_{i,d}

- v_{i,d}: the agent-day spin (DQ5 regime-whitened, style-residualized statement mean, unit-normalized; 32-d).
- X_ex: the **exogenous field** directions (unit vectors in the same space): kickoff k_P, goal text g_P, the agent's room kickoff (where rooms have their own), the human-message centroid of day d, and the agent's own `agent_goal` in #51.
- p_i: the agent's **prior field**, the unit mean of its eligible agent-days in other periods of the same regime, leaving out P−1 and P (so it cannot contain the previous centroid). Needs ≥ 3 days.
- e_{P−1}^{(−i)}: the **endogenous field (previous centroid)**, the unit mean of all eligible agent-days of P−1, leaving agent i out.
- k_{P−1}: the previous kickoff, so that γ measures the village centroid beyond H54's (null) kickoff remanence.
- γ_{P,d}: the **remanence coefficient**. The HH predicts γ_{P,1} > 0 and γ_{P,d} ≈ γ_{P,1} e^{−(d−1)/τ_R}.

Quench (H54) is α: the jump onto the new target. Hysteresis is γ: the old state's trace. A slow collective mode (H81) would give γ > 0 too, but symmetric in time; hysteresis is asymmetric.

**Rivals.**
- **R1, generic village content:** any period's centroid shares a village-wide direction, so γ > 0 for every centroid. Removed by placebo centroids (O2).
- **R2, slow mode (H81):** content drifts slowly, so P−1 and P+1 are both close to P. Separated by the future placebo γ(P+1) (O3).
- **R3, individual memory:** only veterans carry the trace (memory, carried-over context). Separated by newcomers (O4; kill clause 2).
- **R4, composition carry-over:** the same members write similar things in both periods. Removed by the leave-out prior p_i and the leave-i-out centroid; residual risk from room-mates' priors (N3 residualizes senders' priors).
- **R5, themed goal runs:** consecutive kickoffs resemble each other. k_P and k_{P−1} are regressors; goal similarity is a covariate across boundaries.

## Data scheme (`scheme/`)
Script: `scheme/build.py` (shared tables only; no text read or written; holdout rows dropped with `common.holdout_mask` and asserted).
- **Inputs:** as listed above.
- **Transform:**
  1. Eligible agent-days: non-holdout, n_chat + n_intent ≥ 5, agent not 19 (Claude Code), 28 or 30 (fine-tuned leaders). Unit-normalize.
  2. Boundaries: consecutive goal numbers (P−1, P), both non-holdout, every eligible day of P−1 and the first 5 active days of P in one regime. P's active-day index d counts eligible PT days from the goal's first day.
  3. Directions (regime whitener of the same model, unit): kickoff, goal text, room kickoffs, human-message centroid per PT day, #51 agent goals.
  4. Priors (leave P−1 and P out), centroids (leave-i-out), placebo centroids (every other non-holdout period Q of the regime with |Q − P| ≥ 2) and the future centroid (P+1 if non-holdout and same regime).
  5. **Newcomer (boundary):** an agent with no eligible day in P−1 that is present on day d ≤ 5 of P; veteran: present in P−1.
- **Output:** `data/processed/H82-remanence-endogenous-field/` (`boundaries.parquet`; per-model `design_<model>_<variant>.npz` with vectors and keys; `replication/`, `natives/`, `synthetic/`; `_provenance.json`).
- **Regimes covered:** I, II (one boundary, 35 → 36 on 03-23) and III (#36 regime-III days onward), non-holdout.

## Observables
*Written 2026-10-04 20:07 UTC. Sampling facts already seen: eligible agent-day counts per regime, the roster table, non-holdout period units, the goal-field kinds. No content statistic has been computed.*

**O1. Remanence coefficient (per boundary, per day d = 1…5).** OLS of the stacked 32 coordinates of v_{i,d} (agents present on day d of P) on the regressors above (no intercept; regressors unit vectors). γ_{P,d} is the coefficient of e_{P−1}^{(−i)}. Agent-cluster bootstrap (500 draws) for the CI.

**O2. Remanence excess (primary).** Δγ_{P,d} = γ_{P,d}[e_{P−1}] − median_Q γ_{P,d}[e_Q], refitting with each placebo centroid e_Q in place of e_{P−1} (all else equal). Card level: DerSimonian–Laird random-effects mean of Δγ_{P,1} over boundaries (SE from the bootstrap), sign count, per regime and pooled across regimes as a meta-analysis of per-boundary estimates (no pooled fit).

**O3. Time asymmetry.** A_P = γ_{P,1}[e_{P−1}] − γ_{P,1}[e_{P+1}] where P+1 is eligible. Hysteresis: A > 0. Slow mode: A ≈ 0.

**O4. Decay.** RE mean of Δγ_{P,d} for d = 1…5; τ_R from a fit of Δγ_d = Δγ_1 e^{−(d−1)/τ_R} to the RE means (descriptive; per-boundary values reported).

**O5. Newcomers vs veterans.** At each boundary with ≥ 1 newcomer on days 1–5: the regression with a newcomer interaction (γ_vet, γ_new; same placebo correction). Card level: RE mean of Δγ_new and Δγ_vet over boundaries with newcomers; ratio Δγ_new / Δγ_vet.

**O6. Robustness.** Both embedding models; variants white32 and style_resid_period; without the human-message direction; prior leaving out P−2 … P+1 (wider gap); with the current-period room-mates' prior mean as an extra regressor (R4).

**O7. Natives.**
- **NE27 (2025-08-18, #10 kickoff; #9 is held out).** Endogenous field = the #8 centroid (older village history, about 1 week back). Newcomers 9, 10, 11 (empty memories) vs veterans on days 1–3 of #10: Δγ_new, Δγ_vet against placebo centroids of regime I.
- **NE32 (2026-07-09).** Newcomers 35, 36, 37 (isolated rooms on 07-09, merged 07-10) and 38 (joined 07-10, onboarding room), days 1–5 of their tenure. Endogenous field = the regime-III history centroid (all non-holdout days of #36–#44; none of them saw it), leave-nothing-out (they are not in it). Exogenous: #51 kickoff, room kickoffs, own `agent_goal`, human messages of the day. Prior: their **family prior** (mean of same-lab agents' regime-III priors; they have no other non-holdout period). Statistic: Δγ_hist = γ[history centroid] − median γ[placebo], placebo = the centroid of one held-in regime-III period at a time (#36 … #44, each leaving that period out of the history centroid is not possible without emptying it, so the placebo set is the single-period centroids, and the history coefficient is compared with their median). Reference: incumbents (present in #44) on the same days, same regressors (their own prior in place of the family prior).
- **NE15 (rooms #best/#rest; read vs posted-but-unread).** Regime-III boundaries where P−1 had ≥ 2 active rooms (37→38, 38→39, 39→40, 41→42). For each veteran on day 1 of P: e_read = unit mean of P−1 statements from the last two active days of P−1 that entered the agent's context (context ledger items at its calls), and e_unread = unit mean of P−1 statements of the same days and hours that never entered its context (other room). Both are built from statement vectors residualized on each sender's prior (sender p_j subtracted) and exclude the agent's own statements. Statistic: γ_read − γ_unread (one regression with both). Matched posting time: both sets restricted to the hours where both exist.

## Null / baseline
*Written 2026-10-04 20:07 UTC, before any real-data content statistic.*
- **Placebo centroids (O2):** the same regression with the centroid of a non-adjacent period of the same regime. Kills R1.
- **Future placebo (O3):** centroid of P+1. Kills R2 for the hysteresis reading.
- **Synthetic S0 (no remanence) on the real boundaries:** real presence, real exogenous directions and priors, planted v = unit(α k_P + β p_i + noise) with noise drawn from real within-period agent-day residuals (permuted across agents and days); the full pipeline runs unchanged (size of O2, O5). S1: planted γ_1 ∈ {0.05, 0.1, 0.2} relative to the kickoff loading, decaying with τ_R = 1 active day, for all agents. S2: the same for veterans only. 200 replicates.
- **In-flight placebo (N3):** posted-but-unread statements at matched posting hours.

## Impostor table (STANDARDS.md §1)
| Impostor | How it could fake this result | How H82 removes it | Status |
| --- | --- | --- | --- |
| Scheduler field | day-1 content is shaped by the day's schedule (short kickoff days, first-of-day re-reads) | one vector per agent-day; regressors are content directions, not timing; placebo centroids share the same day-1 schedule | removed |
| Exogenous field (goal, kickoff, operator) | the new kickoff or operator messages resemble the old period's content (themed runs) | k_P, g_P, room kickoffs, the day's human-message centroid, #51 agent goals and k_{P−1} are regressors; placebo centroids; goal similarity covariate | partly (directions miss part of the topic field) |
| Shared model priors (family, style) | the same members write alike in both periods | DQ5 `style_resid`; the prior p_i leaves P−1 and P out; leave-i-out centroid; room-mates' prior variant; family prior for NE32 newcomers | removed (agent level); partly for NE32 (family prior) |
| Contemporaneous convergence | agents at the same boundary drift the same way without reading the old content | the regressor is the previous period's content, not equal-time content; placebo and future centroids; NE15 compares read vs posted-but-unread previous-period content at matched posting hours | partly (NE15 only covers regime-III room boundaries) |

## Prediction
*Written 2026-10-04 20:07 UTC, before running the analysis on real data.*

The HH predicts remanence carried by newcomers too. My prior on that full claim is low (about 0.15). H54 found no previous-kickoff remanence on day 1 (median 0.01, p 0.34) and a fast quench onto the new kickoff (day-1 top-1 in 18/33). H15 found ≈ 0 day-scale semantic information in memory. A veteran-only trace (context carried over the night in regime III) is more plausible (about 0.4).

- **P1 remanence (headline):** the RE mean of Δγ_{P,1} > 0 with the 95% CI excluding 0, Δγ_{P,1} > 0 in ≥ 2/3 of boundaries, in both embedding models. *Against:* the RE CI includes 0 (or the mean is ≤ 0): no endogenous field beyond the exogenous and prior fields (kill clause 1).
- **P2 hysteresis, not slow mode:** the RE mean of A_P > 0 (one-sided p < 0.05). *Against:* A ≈ 0 with P1 passing: the trace is a slow mode (H81), not remanence.
- **P3 decay:** Δγ_5 < ½ Δγ_1, with τ_R between 0.5 and 5 active days. *Against:* no decay (a persistent offset is composition or slow mode).
- **P4 the record, not members:** Δγ_new > 0 and Δγ_new ≥ ½ Δγ_vet (RE over boundaries with newcomers). *Against:* Δγ_new ≈ 0 while Δγ_vet > 0 (kill clause 2: individual memory). If the synthetic power for Δγ_new at the S1 effect is < 0.8, P4 is **inconclusive**.
- **Effect that matters:** Δγ_1 = 0.05 (one fifth of H54's day-1 kickoff excess 0.24). A negative P1 counts as failed only if the synthetic power at that size is ≥ 0.8.
- **Overall reading (fixed now).** **Supported:** P1, P2 and P4 pass. **Mixed:** P1 passes and P2 or P4 fails (a veteran-only trace is "individual memory", the HH's second kill, recorded as mixed because an endogenous field exists). **Failed:** P1 fails with power ≥ 0.8.

**Natives (dated predictions also in each folder).**
- **N1 NE27:** Δγ_vet > 0 and Δγ_new ≥ ½ Δγ_vet on days 1–3 of #10. *Against:* Δγ_new ≤ 0. Prior 0.2.
- **N2 NE32:** newcomers' history loading Δγ (against a random-direction null and the incumbents on the same days) > 0, at least ½ of the incumbents'. *Against:* ≤ 0. Prior 0.2.
- **N3 NE15:** γ_read − γ_unread > 0 (agent-cluster bootstrap CI excluding 0, pooled over the room boundaries as a meta-analysis). *Against:* CI includes 0: whatever remanence exists is not carried by reading the old content. Prior 0.4.

## Synthetic validation (axis F; run 2026-10-04 20:12–20:20 UTC, before any real-data remanence statistic)
`analysis/synthetic.py` → `data/processed/H82-remanence-endogenous-field/synthetic/synthetic_<model>.json`. Village sampling: the 25 real boundaries (19 regime I, 6 regime III), the real agents present on days 1–5 of each new period, their real priors, centroids and exogenous directions. Planted vectors: the regime's null fit (exogenous + prior loadings, a sampling fact) plus real residuals of that fit permuted across agents and days. S1 adds γ e_{P−1}^{(−i)} decaying with τ_R = 1 active day for every agent; S2 for veterans only. 200 S0 and 100 other replicates per model. The statistic is the pooled unweighted mean of Δγ over boundaries.

| Statistic | S0 mean (bge / gte) | S0 q95 | S1 γ = 0.05 | S1 γ = 0.1 | S1 γ = 0.2 | S2 γ = 0.1 (veterans) |
| --- | --- | --- | --- | --- | --- | --- |
| mean Δγ_1, all boundaries | +0.022 / +0.033 | 0.055 / 0.063 | **0.83 / 0.92** | 1.00 / 1.00 | 1.00 / 1.00 | 1.00 / 1.00 |
| mean Δγ_1, regime I (19) | +0.014 / +0.024 | 0.053 / 0.062 | 0.70 / 0.76 | 1.00 / 0.99 | 1.00 / 1.00 | 1.00 / 1.00 |
| mean Δγ_1, regime III (6) | +0.050 / +0.061 | 0.105 / 0.120 | 0.35 / 0.33 | 0.85 / 0.82 | 1.00 / 1.00 | 0.90 / 0.84 |
| mean asymmetry A_1 | −0.007 / +0.003 | 0.036 / 0.052 | 0.57 / 0.48 | 0.96 / 0.98 | 1.00 / 1.00 | 1.00 / 1.00 |
| mean Δγ_new (days 1–5) | +0.029 / +0.037 | 0.129 / 0.120 | 0.15 / 0.06 | 0.10 / 0.11 | 0.06 / 0.18 | 0.05 / 0.08 |

Readings: (1) the placebo-corrected excess is **biased upward under the null** (+0.022 / +0.033): the prior leaves out P and X, so its fit differs between the P−1 design and the placebo designs. The RE confidence interval against 0 would therefore be liberal. (2) The pooled test has power ≥ 0.8 at the effect that matters (γ = 0.05) in both models; regime III alone does not (0.33–0.35). (3) The newcomer term has no power (≤ 0.18 even at γ = 0.2), because newcomers on days 1–5 are few. (4) Veteran-only remanence (S2) and all-agent remanence (S1) look the same in the pooled statistic; only the newcomer split separates them.

## Amendments (2026-10-04 20:25 UTC, after the synthetic validation, before any real-data remanence statistic)
- **A1 (P1 decision rule).** P1 passes if the pooled unweighted mean Δγ_1 exceeds the S0 95th percentile in both models (0.055 bge, 0.063 gte). The RE mean is reported after subtracting the S0 mean bias; its raw CI against 0 is not used. Same rule for P2 (asymmetry q95 0.036 / 0.052).
- **A2 (P4 is unpowered).** By the card's rule P4 is **inconclusive** whatever the point estimate (power ≤ 0.18). Newcomer estimates are reported descriptively; NE27 and NE32 remain dated natives with the same caveat.
- **A3 (regime scope).** A negative is "failed" for γ ≥ 0.05 only for the pooled test; regime III alone can reject only γ ≥ 0.1 (power 0.82–0.85).

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G03](goalperiod-subhypotheses/G03/README.md) | replication | failed | #2 → #3, regime I, N 4: Δγ₁ -0.07 [-0.14, -0.01] / -0.05 [-0.11, +0.01]; asymmetry -0.27 / -0.10 |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | mixed | #3 → #4, regime I, N 3: Δγ₁ +0.25 [-0.03, +0.44] / +0.25 [+0.04, +0.55]; asymmetry +0.07 / +0.03 |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | supported | #4 → #5, regime I, N 4: Δγ₁ +0.60 [+0.41, +0.74] / +0.53 [+0.46, +0.62]; asymmetry +0.47 / +0.73 |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | mixed | #5 → #6, regime I, N 4: Δγ₁ +0.18 [+0.03, +0.42] / -0.24 [-0.37, -0.13]; asymmetry -0.20 / -0.75 |
| [G07](goalperiod-subhypotheses/G07/README.md) | replication | supported | #6 → #7, regime I, N 4: Δγ₁ +0.53 [+0.42, +0.67] / +0.63 [+0.43, +0.75]; asymmetry +0.39 / +0.56 |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | mixed | #7 → #8, regime I, N 4: Δγ₁ -0.08 [-0.13, +0.00] / -0.05 [-0.12, +0.09]; asymmetry n/a / n/a |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | mixed | #10 → #11, regime I, N 7: Δγ₁ +0.29 [+0.11, +0.48] / +0.27 [-0.01, +0.59]; asymmetry +0.24 / +0.27 |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication | mixed | #11 → #12, regime I, N 7: Δγ₁ +0.08 [+0.00, +0.20] / +0.13 [+0.10, +0.18]; asymmetry +0.15 / +0.03 |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | supported | #12 → #13, regime I, N 6: Δγ₁ +0.39 [+0.22, +0.56] / +0.35 [+0.20, +0.52]; asymmetry n/a / n/a |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | mixed | #16 → #17, regime I, N 7: Δγ₁ +0.11 [+0.03, +0.21] / -0.00 [-0.09, +0.09]; asymmetry +0.01 / -0.17 |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | failed | #17 → #18, regime I, N 7: Δγ₁ -0.05 [-0.12, +0.06] / -0.01 [-0.10, +0.08]; asymmetry +0.15 / +0.06 |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | supported | #18 → #19, regime I, N 7: Δγ₁ +0.46 [+0.29, +0.60] / +0.40 [+0.33, +0.46]; asymmetry +0.06 / +0.20 |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | mixed | #19 → #20, regime I, N 8: Δγ₁ -0.00 [-0.06, +0.04] / +0.17 [+0.11, +0.24]; asymmetry -0.29 / -0.06 |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | mixed | #20 → #21, regime I, N 8: Δγ₁ -0.01 [-0.08, +0.06] / +0.07 [-0.02, +0.14]; asymmetry n/a / n/a |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | mixed | #23 → #24, regime I, N 10: Δγ₁ +0.18 [+0.02, +0.31] / -0.03 [-0.10, +0.05]; asymmetry +0.31 / -0.01 |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | failed | #24 → #25, regime I, N 10: Δγ₁ -0.01 [-0.06, +0.05] / -0.18 [-0.22, -0.13]; asymmetry -0.13 / -0.21 |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | supported | #25 → #26, regime I, N 10: Δγ₁ +0.23 [+0.13, +0.32] / +0.21 [+0.12, +0.35]; asymmetry +0.37 / +0.43 |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | mixed | #26 → #27, regime I, N 10: Δγ₁ +0.09 [+0.02, +0.15] / -0.17 [-0.22, -0.13]; asymmetry n/a / n/a |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | supported | #30 → #31, regime I, N 10: Δγ₁ +0.21 [+0.10, +0.27] / +0.31 [+0.21, +0.42]; asymmetry n/a / n/a |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | supported | #36 → #37, regime III, N 12: Δγ₁ +0.22 [+0.05, +0.38] / +0.25 [+0.13, +0.36]; asymmetry +0.28 / +0.23 |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | mixed | #37 → #38, regime III, N 12: Δγ₁ +0.01 [-0.09, +0.08] / +0.15 [+0.06, +0.28]; asymmetry +0.18 / +0.32 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | failed | #38 → #39, regime III, N 14: Δγ₁ -0.15 [-0.23, -0.05] / -0.01 [-0.06, +0.07]; asymmetry -0.31 / -0.19 |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | supported | #39 → #40, regime III, N 15: Δγ₁ +0.35 [+0.28, +0.41] / +0.55 [+0.45, +0.63]; asymmetry +0.31 / +0.50 |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | mixed | #40 → #41, regime III, N 15: Δγ₁ -0.04 [-0.14, +0.07] / +0.03 [-0.06, +0.13]; asymmetry -0.01 / +0.11 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | supported | #41 → #42, regime III, N 15: Δγ₁ +0.18 [+0.12, +0.23] / +0.24 [+0.19, +0.30]; asymmetry n/a / n/a |
| [NE27](goalperiod-subhypotheses/NE27/README.md) | native | failed | #8 → #10 (held-out #9 between): Δγ_vet −0.035 / +0.025, Δγ_new +0.005 / +0.049 (days 1–3; CIs span 0) |
| [NE32](goalperiod-subhypotheses/NE32/README.md) | native | mixed | isolated newcomers' history loading +0.036 [0.006, 0.081] / +0.010 [−0.020, 0.039]; incumbents −0.036 / −0.033 |
| [NE15](goalperiod-subhypotheses/NE15/README.md) | native | mixed | γ_read − γ_unread +0.071 [−0.007, 0.148] / +0.106 [0.039, 0.174] over 4 room boundaries |

## Outcome vs prediction
*Run 2026-10-04 20:27–20:36 UTC (`analysis/replication.py`, `analysis/natives.py`, `analysis/posthoc.py`). Non-holdout only. Decision rules of Amendments A1–A3 (pooled mean against the S0 95th percentile).*

| Prediction | Observed (bge / gte) | Verdict |
| --- | --- | --- |
| P1 remanence: pooled mean Δγ₁ > S0 q95, both models | **0.158 / 0.153** (q95 0.055 / 0.063; S0 bias 0.022 / 0.033); RE 0.146 [0.080, 0.213] / 0.147 [0.059, 0.235]; positive at 17/25 and 16/25 boundaries | **pass** |
| P1 by regime | regime I (19) 0.178 / 0.137 (q95 0.053 / 0.062); regime III (6) 0.095 / 0.202 (q95 0.105 / 0.120) | regime I pass; III model-dependent |
| P2 hysteresis: mean asymmetry γ[P−1] − γ[P+1] > S0 q95 | 0.093 / 0.104 (q95 0.036 / 0.052); γ[P−1] 0.158 / 0.151, γ[P+1] 0.076 / 0.060, γ[placebo] 0.000 / −0.001; RE 0.088 [−0.021, 0.196] / 0.111 [−0.006, 0.227] | **pass** (by A1; RE CI touches 0) |
| P3 decay: Δγ₅ < ½ Δγ₁, τ_R 0.5–5 d | RE Δγ_d, d = 1…5: 0.15, 0.15, 0.11, 0.13, 0.13 / 0.15, 0.13, 0.12, 0.13, 0.14 (bias not subtracted); no decay | **fail** |
| P4 newcomers carry it (Δγ_new ≥ ½ Δγ_vet) | 5 boundaries with one newcomer each (#18, #20, #21, #39, #42); days 1–5 mean Δγ_new 0.20 / 0.18 (S0 q95 0.13 / 0.12); day 1 at one boundary only (−0.20 / −0.15) | **inconclusive** (A2: power ≤ 0.18) |
| N1 NE27: Δγ_vet > 0, Δγ_new ≥ ½ Δγ_vet | veterans −0.035 / +0.025, newcomers +0.005 / +0.049 (days 1–3; RE CIs span 0) | **failed** (no trace of #8 across the held-out week for anyone) |
| N2 NE32: newcomers' history loading > 0, ≥ ½ incumbents' | newcomers +0.036 [0.006, 0.081] / +0.010 [−0.020, 0.039]; incumbents −0.036 / −0.033 (CIs span 0) | **mixed** (bge only; 17 agent-days) |
| N3 NE15: γ_read − γ_unread > 0 | fixed effect +0.071 [−0.007, 0.148] / +0.106 [0.039, 0.174]; positive at 3/4 boundaries; 37 → 38: +0.38 / +0.32 | **mixed** (gte CI > 0, bge touches 0) |

**Overall (pre-registered reading):** P1 and P2 pass, P4 is inconclusive (unpowered), and P3 fails. By the card's rule this is **mixed**. The post hoc check PH2 below shows the trace is the agents' own previous content, which is the HH's second kill clause (individual memory) in substance.

## Post hoc checks (labelled; written after the replication result, `analysis/posthoc.py`)
- **PH1, wrap-up vs remanence.** Day-1 vectors rebuilt from statements posted ≥ 1 h after the kickoff window start (70% of day-1 statements) give Δγ₁ 0.152 / 0.156 (positive at 20/25 and 18/25). The trace is not the morning wrap-up of the old goal.
- **PH2, own past vs village.** Adding the agent's own previous-period mean as a regressor takes Δγ₁ to −0.024 / −0.060 (positive at 9/25 and 8/25). The village centroid adds nothing beyond each agent's own previous content.
- **Geometry of the asymmetry.** Day 1 of P lies about 4–5 days after the middle of P−1 and about 9–10 days before the middle of P+1. An OU slow mode with H81's τ_u ≈ 25 d predicts γ[P+1]/γ[P−1] ≈ 0.8; the observed ratio is 0.48 / 0.40. Part of P2 is the slow mode's lag geometry; the rest is hysteresis.

## Results
**1. The previous period leaves a trace.** On day 1 of a new goal, an agent's content loads on the previous period's village centroid by Δγ₁ ≈ 0.15 beyond the median placebo centroid (both models; 25 boundaries; S0 95th percentile 0.055–0.063). The new kickoff, goal text, previous kickoff, the day's operator messages, room kickoffs and the agent's leave-out prior are all in the regression. The trace survives every preprocessing variant (0.14–0.24), dropping Gemini 2.5 Pro (0.14 / 0.15), a wider prior gap and the co-present agents' prior. It is not the old goal's wrap-up (PH1). For scale, H54's day-1 kickoff excess (a cosine, not a regression coefficient) is 0.24.

**2. It is persistent, not a decaying remanence.** Δγ_d stays at 0.11–0.15 through day 5. The future centroid also loads (γ[P+1] ≈ 0.06–0.08, about half of γ[P−1]). This is the signature of H81's slow mode seen from a boundary, plus an asymmetric part larger than the slow mode's lag geometry predicts. The HH's "decay with τ of days" (P3) fails.

**3. It is carried by members' own content.** With the agent's own previous-period mean as a regressor, the village centroid loads −0.02 / −0.06 (PH2). Each veteran continues its own previous themes; the village average carries no extra information. Newcomers (one per boundary at five boundaries) load positively on days 1–5, but the test has no power (A2). NE27's three empty-memory newcomers and their veterans show no trace of #8 across the held-out #9 week; NE32's isolated newcomers load weakly on regime-III history in one model only.

**4. Reading carries part of it.** At regime-III room boundaries, previous-period statements that entered an agent's context predict its day-1 content more than same-hour statements from the other room (+0.07 / +0.11; one model's CI excludes 0). The largest case is #37 → #38 (+0.38 / +0.32).

**Reading.** The goal change is a quench onto the new kickoff (H54) on top of a persistent individual offset: agents keep their previous themes for at least five days, partly through what they read. There is no evidence that the trace lives in the village record rather than in members.

Figures: `figures/summary_obs.pdf` (Δγ₁ per boundary; day profile), `figures/summary_obsb.pdf` (past vs future vs placebo centroids; synthetic power). Data: `data/processed/H82-remanence-endogenous-field/` (`replication/`, `natives/`, `posthoc/`, `synthetic/`, `confirm/confirm_dryrun.json`). Estimates: 60 rows in `per_period_estimates` (hypothesis H82).

## Faithfulness scorecard
*Round 1, 2026-10-04.*
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed.
**Rival models:** R1 generic village content; R2 slow mode (H81); R3 individual memory; R4 composition carry-over; R5 themed goal runs.
**Locked holdout used for confirmation:** none yet (`analysis/confirm.py`, dry-run only).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Exogenous, prior and endogenous fields from shared tables; regime I clear, regime III model-dependent. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 0 | The decaying-remanence form fails: no decay over 5 days; the trace needs the agent's own past (higher Markov order in the member, not the village). |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 2 | Beats placebo centroids and the synthetic S0 (3× the 95th percentile), both models. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | Time asymmetry passes; the decay signature fails. |
| E interventional | predicts the change across a natural experiment | 1 | NE15 read > unread (one model); NE27 none; NE32 weak. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 | Null bias found and calibrated (A1); power 0.83–0.92 at γ = 0.05; 12 variants agree; newcomer term shown unpowered. |
| G ground truth | agrees with known structure | 1 | Consistent with H54 (quench onto the kickoff, no kickoff remanence) and H81 (slow mode). |
| H comparative | beats the named rivals | 1 | Beats R1, R4, R5; R2 explains part (γ[P+1] > 0); R3 (individual memory) wins PH2. |
| I transfer | holds in other same-mode periods, including the holdout | 1 | Regime I and (gte) regime III; holdout not run. |

## Confirmatory predictions (written 2026-10-04 20:40 UTC after round 1, before any holdout use; `analysis/confirm.py`, dry-run only, **not run**)
Targets: goal boundaries with a held-out side (8→9, 9→10, 13→14, 14→15, 15→16, 21→22, 22→23, 27→28, 28→29, 29→30, 42→43, 43→44, 44→45 … 50→51).
- **C1:** pooled mean Δγ₁ > S0 q95 (re-simulated on those boundaries) in both models.
- **C2:** with the agent's own previous-period mean as a regressor, the pooled mean Δγ₁ < 0.05 in both models (individual carry-over).
- Dry run on stand-ins (8 boundaries around #11, #18, #25, #39): C1 passes in bge, at the threshold in gte; C2 passes in both.
- **Reuse disclosure:** H54 (kickoff remanence) and H20 target held-out goal starts with related day-1 content statistics.

## Caveats
- **Regression on unit vectors in 32 dimensions** with N = 3–15 agents per day; regime-I boundaries rest on 3–4 agents.
- **Placebo correction is biased upward under the null** (+0.02 / +0.03); decisions use the S0 percentile.
- **Newcomers are too few** to test the HH's central claim (one per boundary, five boundaries).
- **PH2 is post hoc**, and the own-past regressor also contains the village state as the agent experienced it, so "individual" vs "village" is a statement about which regressor wins, not about mechanism.
- **The asymmetry is partly lag geometry**, not hysteresis.
- Boundary 35 → 36 (regime II) is excluded: #36's first day is the only regime-II day of #36.

## Round 2 redirects (2026-10-04)
*Proposed by the round-1 agent; the coordinator may revise.*
- **Where round 1 went sideways:** the HH expected a day-scale decaying remanence; the trace is a persistent individual offset plus a slow village mode, and newcomers are too rare at boundaries to test the record.
- **What the direction is really after:** whether a goal change resets the village or only re-points members who keep their own threads.
- **H82-R1. Individual carry-over model.** Fit v_{i,d} = quench(k_P) + persistence × own previous content with a decay over the whole period (not 5 days), per agent, and compare with H81's village τ_u.
- **H82-R2. The record channel.** Extend NE15's read vs unread design to memory and history-search reads (context ledger), and to regime I where chat-mode prompts rebuild from recent chat.
- **H82-R3. Newcomer power.** Pool newcomers' first five days over all joins (not only boundary days) against same-day veterans, with the previous goal's centroid; check power synthetically first.

## Notes
- 2026-10-04: H54's "previous-kickoff remanence" (day-1 excess toward k̂_{P−1}, median 0.01, p 0.34) is the kickoff part of this test. H82 adds the village centroid, the agent prior and the newcomer contrast. The kickoff part stays ≈ 0 here too (k_{P−1} is a regressor).
- 2026-10-04: all timestamps are from the clock and file modification times (card 20:07, synthetic 20:12–20:20, amendments 20:25, replication 20:27–20:34, natives and post hoc 20:35–20:36 UTC).
- 2026-10-04: runs used one process with numpy and polars at 2 threads. Data in `data/processed/H82-remanence-endogenous-field/` (~4 MB) with `_provenance.json`. The agent-day and direction code is a copy of H81's scheme (no cross-hypothesis import).
