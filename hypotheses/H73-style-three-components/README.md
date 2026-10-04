# H73: Style = weights + context + register

**Status:** **exploratory round 1 done (2026-10-04, non-holdout only). Mixed: the three components explain most systematic style variance (F3 median 0.72, 34/34 periods), but nearly all of it is the agent constant, and removing the context component does not raise attribution.**
- **Agent constant dominates:** largest unique share in 34/34 periods (median 0.55 of the non-day systematic variance). Per message, about three quarters of style is noise (ceiling κ 0.27).
- **Context component is small** (median 0.08; 0.011 in regime III) and in regime III follows received chat more than own fill. Attribution gain −0.007 [−0.017, +0.003] (P3 fails).
- **Erasure jump is mostly directionless:** the fitted drift predicts 1.7% of it (β 0.27 [0.12, 0.36]); T_s 0.567 as in H46.
- **Registers:** #12 judging is a shared register (cos +0.78, p 0.001); #51 roles share none (p 0.56), and the Prankster's shift is an onset transient (post hoc).
- Card and predictions written 2026-10-04 19:13 UTC before any real-data statistic. `analysis/confirm.py` written and dry-run, **not run**.
**Question (GOALS.md):** **Q2** (what is field and what is coupling): it splits an agent's style into a substrate constant, a context-held state and an assigned-register field. It also serves Q7 (attribution signatures computable from public logs).
**Fields:** stat mech, info theory
**Literature:** none beyond the predecessors' notes (H46, H13; the Kolchinsky–Wolpert framing is not used here).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime; Driving / external field (the day field); **Context fill** (`context_ledger_turns.ctx_pos`, receiving calls since the last reset); H46's **agent state (style, chat agent-day)**, used here at message level as the named variant *agent state (style, message)* (proposed for DEFINITIONS.md, see Observables); *assigned register* (proposed, see Model).
**From:** HH265 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` ("Making the faithful ones better"); H46 round-2 redirects H46-R1, R2 and R4 · **Models:** `physics-models/11-vector-spins/` (primary), `physics-models/04-semantic-information/` (not used: see Notes)
**Data inputs (shared tables first):** `text_features` (H13's 20 style features), DQ5 `statement_flags` (dedupe), DQ1 `context_ledger_turns` (`ctx_pos`, `k_ctx`, reset flags, `ctx_mode`), `calendar` (day window), `period_units`, DQ6 `ground_truth_labels` (#12 judges and teams, #51 roles), DQ2 `reply_pairs` (`parent`, genre control), `chat_mentions_clean` (genre control), `roster`.

## Question
Does a three-component model (agent constant + context-fill drift + assigned-register shift) explain most style variance, with attribution accuracy improving once the context component is removed?

## Design: two layers (Vivian, 2026-10-04; see `infra/data-quality/QUEUE.md`)
- **Replication:** the common estimator (decomposition O1, attribution O2, dispersion O3) on every eligible goal period. Period README role: `replication`.
- **Period-native tests:** NE41 (exogenous context erasure), G12 (#12 judges: a within-agent assigned register), G51 (#51 private roles: assigned registers at the persona onset), G44 (fine-tuned leader: a weights swap on a known base). Each has its own dated prediction. Period README role: `native`.
- **Faithfulness lever:** HH265 was written to raise H46's axes B (Markov order: the agent alone is not the state) and H (rival R1, style as state, beat H46). The scorecard says whether it did.

## Model
**From:** `physics-models/11-vector-spins/` (agent states as vectors; agent fields vs day fields).

**H73 variant: a three-component style field.** Message m of agent i on day d in goal period P has a 17-d style vector x_m (below). Its context state s_m is the chat mode (regimes I/II chat calls, which rebuild the prompt from recent chat) or the context fill p_m = `ctx_pos` of the call that posted it (computer-use mode). r_m is its assigned register (judge in #12; none elsewhere inside a period).

  x_m = g_d + τ(h_m) + q_i + c(s_m) + b_i·z(s_m) + ρ_{r_m} + η_{i,d} + ε_m

- g_d: the **day field** (topic, goal, kickoff, operator; common to every agent present that day). τ(h): a time-of-day term (hours since the day's first agent event, piecewise linear). Both are nuisance fields.
- q_i: the **agent constant** (the weights, plus anything fixed for the agent in the period).
- c(s) + b_i·z(s): the **context component**. c(s) is a common profile over context bins {chat mode, p ∈ 0–1, 2–3, 4–7, 8–15, 16–31, ≥ 32}. b_i is an agent-specific drift direction on z = log2(1 + p) (centred within the period; z = 0 in chat mode).
- ρ_r: the **assigned-register shift**, common to all agents holding register r.
- η_{i,d}: agent-day jitter (not modelled: it is what the three components fail to explain). ε_m: message noise.

The claim "style = weights + context + register" is that q, c, b and ρ carry most of the systematic (non-ε) variance that the day field leaves, so η is small.

**Rivals.**
- **R1, agent-day state (η dominates):** style follows the day's task and topic per agent (H46's digit and uppercase shift at goal switches); context fill adds little.
- **R2, genre, not context:** the position profile is speech-act mix (status updates right after a reset, replies later). Controlled by reply and mention flags and by dropping p ≤ 1 (sensitivity).
- **R3, clock, not context:** drift follows hours into the day. Separated because resets restart p within a day; τ(h) is in the base model.
- **R4, accommodation, not own context:** drift follows the other agents' messages that fill the context (received items, `k_ctx`), i.e. contemporaneous convergence to the room's register. Separated by fitting z on own calls (p) and on received items (log2(1 + k_ctx)) together (regime III).
- **R5, excitation without direction:** context fill raises dispersion around q_i (a random excursion, H46-R2) but has no fixed direction, so no mean profile can be removed and attribution cannot gain from detrending.

**Assigned register (proposed DEFINITIONS.md term):** a speech role given to the agent from outside (by the operator, the goal text or a draw), not chosen in context: #12 judge vs debater; #51 private roles. Model swaps (G44 leader; NE30 in the holdout) change the weights component, not the register.

## Data scheme (`scheme/`)
Script: `scheme/build.py` (shared tables only; no text read or written; holdout rows dropped by `calendar` `holdout` and `common.holdout_mask`, asserted).
- **Inputs:** `text_features` (20 `f_*` features), `embeddings/statements` + `chat_index` (row map to `statement_flags`), `statement_flags` (`self_repeat_both`, `self_repeat_bge`, `self_repeat_gte`), `context_ledger_turns` (talk calls: `t_first`, `ctx_mode`, `ctx_pos`, `k_ctx`, `turn_id`), `calendar` (`win_start`), `period_units`, `ground_truth_labels` (`preferred & ~holdout`), `reply_pairs` (`parent`), `chat_mentions_clean` (`mentions_roster`), `roster`.
- **Transform:**
  1. Non-holdout agent chat messages; Claude Code agent (19) and the two fine-tuned leaders (28, 30) are excluded from the common estimator (28 only in the G44 native).
  2. Style: winsorize the 20 features at the non-holdout 0.1% / 99.9% quantiles; z-score globally (shared ruler, exception (a)). Type control within regime: regress the 17 features other than `log_chars`, `backticks`, `urls` on a `log_chars` spline (quartile knots), `has_code`, `has_url`; residuals = **type-controlled style** (primary, 17-d). This is H46's construction, re-implemented here (no import from H46).
  3. Each message joins its producing talk call (`context_ledger_turns`, same agent, nearest `t_first` within 3 s): `ctx_mode`, `ctx_pos`, `k_ctx`. Unmatched messages are dropped (they have no context state).
  4. Hours since the day's calendar `win_start`; unit from `period_units` (as-of on time); DQ6 register labels (#12 judge windows; #51 role and role class); `is_reply` (DQ2 `parent` row exists with `pair_set = cand`), `has_mention` (`mentions_roster` non-empty).
  5. Dedupe flags kept: `copy` = `self_repeat_both` (primary drop), `restate` = `self_repeat_bge | self_repeat_gte` (sensitivity drop).
- **Output:** `data/processed/H73-style-three-components/` (`messages.parquet`: keys, unit, regime, context state, hours, register, genre flags, dedupe flags, `tc_*` 17 features, `s_*` 20 standardized features; `style_standardization.json`; analysis outputs in `replication/`, `natives/`, `synthetic/`; `_provenance.json`).
- **Regimes covered:** I, II, III (non-holdout days). The context component in regimes I/II rests on computer-use chat (9–59% of chat per period) plus the chat-mode level.

## Eligible goal periods
Replication: every non-holdout goal period with ≥ 3 agents having ≥ 30 eligible messages, and ≥ 100 eligible computer-use messages. Natives: NE41 (regime-III units, turn level), G12, G51 (with #36–#44 regime-III history), G44.

## Observables
*Written 2026-10-04 19:13 UTC. Sampling facts already seen: message counts per goal period, the share of chat that is in computer-use mode, the ctx_pos range of talk calls (median 19–25, q90 36–42), the message→call join rate (≥ 99% within 2 s), #12 team and judge windows, #51 roles. No style statistic has been computed.*

**Eligible message:** non-holdout agent chat, matched to a talk call, not a copy (`self_repeat_both`), agent not 19/28/30.

**O1. Variance decomposition (per goal period).** Multivariate OLS on the 17-d type-controlled style (trace R², degrees-of-freedom adjusted). Nested blocks: G = day FE + τ(h); A = agent FE; C = context (common bin profile + agent slopes b_i); R = register dummies (where defined).
- Ceiling κ = adjusted R² of the cell-means model with cells (agent × day × context bin × register): the systematic share of style variance at the model's own resolution.
- **F3 = [R²(G+A+C+R) − R²(G)] / [κ − R²(G)]**: the share of the non-day-field systematic variance that the three components explain. The remainder is agent-day jitter η and interactions.
- Unique shares (drop-one, divided by κ − R²(G)): u_A, u_C, u_R.
- Null for u_C: permute context states among the messages of each agent-day (200 draws); report p and the null-corrected u_C.

**O2. Attribution before and after removing the context component (per goal period).** Leave-one-day-out. Each day's messages are centred on that day's label-free mean (all eligible messages of the day). Candidates: agents with ≥ 10 training messages. Test units: blocks of k = 5 consecutive eligible messages of one agent on the held-out day (k = 1 reported). Nearest-centroid classification scaled by the pooled within-agent SD. Balanced accuracy over agents.
- (a) **blind:** centroid = agent training mean.
- (b) **detrended (common):** subtract the training-fitted common profile ĉ(bin) from every message, then classify. Uses only the observable context state.
- (c) **agent-specific context:** score candidate j by the distance to q̂_j + ĉ(bin) + b̂_j z (b̂_j ridge-shrunk, λ = 20 messages).
- **Gain Δ_b = acc(b) − acc(a), Δ_c = acc(c) − acc(a).**

**O3. Context-held dispersion (R5).** Slope of the residual squared norm ‖x − x̂_{G+A+C}‖² on z within computer-use messages, per period (agent-clustered SE).

**O4. Impostor and rival controls (pooled per regime, period-level fits).** u_C after adding is_reply and has_mention (R2), after dropping p ≤ 1 (R2), and the unique shares of own fill z(p) vs received fill log2(1 + k_ctx) in regime III (R4).

**O5. Natives.**
- **NE41 (forced erasures, regime III, turn level):** consecutive eligible messages (m, m′) of an agent on one PT day, labelled forced / voluntary / within (H46's rule: exactly one reset of that kind between them, or none). The context profile ĉ, b̂_i is fitted on *within* pairs only, by regressing Δx on Δ[bin dummies] and Δz per agent (time-of-day difference included). For forced pairs the model predicts Δx̂ = ĉ(s′) − ĉ(s) + b̂_i (z′ − z). Statistics: projection β = Σ⟨Δx, Δx̂⟩ / Σ‖Δx̂‖² over forced pairs (agent-cluster bootstrap CI), and the gap-matched excess percentile T_s of forced pairs among same-agent within pairs at matched log time gap (0.05-decade bins; H46 Amendment A2) before and after subtracting Δx̂.
- **G12 (#12 debates, regime I):** register = judge (inside a debate window where the agent is the judge), debater (inside a window where it has a team), outside. (i) u_R in O1 with these registers; permutation null: shuffle the judge label over the agent's debate windows. (ii) Shared judge direction: for each judge, the cosine between its own judge shift (judge mean − debater mean, after G, A, C) and the leave-this-agent-out mean shift of the other judges; mean cosine against the label permutation. (iii) Attribution of judge-window blocks with centroids trained on non-judge messages, without vs with the leave-agent-out judge shift added to every candidate centroid.
- **G51 (#51 private roles, regime III):** incumbents with ≥ 20 eligible messages in #36–#44 non-holdout and in #51 07-06..07-24. Model fitted jointly on #36–#44 + #51 (exception (c): the transition is the object): day FE, τ, agent FE, context, plus an agent-specific #51 shift R_i (the register). (i) The Prankster's (agent 10) ‖R_i‖ percentile against its own placebo shifts (the same contrast at 3-week calendar splits inside #36–#44 and inside #51 that do not straddle 07-06), before and after removing the context component. (ii) Role-class coherence: mean pairwise cosine of R_i among the 4 incumbent media agents (12, 16, 18, 22) vs all other incumbent pairs; label-permutation p.
- **G44 (model swap: fine-tuned Kimi leader, agent 28):** rank of base Kimi K2.6 (agent 25) among regime-III centroids (#36–#44, leader excluded) for the leader's messages, blind vs context-detrended (all its eligible messages as one block).

**Multiplicity.** Card-level verdicts use the pooled replication counts (P1–P4) and the four natives. Per-period points are templated, labelled `replication`, and not independent tests.

## Null / baseline
*Written 2026-10-04 19:13 UTC, before any real-data style statistic.*
- **Context null:** permutation of context states within agent-day (keeps agent, day and day-mix structure; destroys the position link). Its size is checked on synthetic data at real counts.
- **Attribution null:** under no context profile, Δ_b and Δ_c are ≈ 0 (synthetic check); the card-level test is a sign test over periods plus the period-weighted mean with a bootstrap over periods.
- **Register nulls:** judge-label permutation within agent (#12); role-class label permutation (#51); placebo calendar splits (#51 Prankster).
- **NE41:** β = 0 under no context effect; gap-matched within pairs as the placebo for T_s.
- **Baseline model:** G + A (day field + agent constant). F3 compares the three-component model with it at the ceiling κ.

## Impostor table (STANDARDS.md §1)
| Impostor | How it could fake this result | How H73 removes it | Residual risk |
| --- | --- | --- | --- |
| Scheduler field | p rises through the day, so a time-of-day drift (fatigue of the day's thread, end-of-day wrap-up messages) would look like context drift | τ(h) is in the base block G; resets restart p within the day, so C is identified from within-day resets; NE41 uses scaffold-timed erasures | regime I/II computer-use sessions start at scheduled times |
| Exogenous field (goal, kickoff, operator) | the day's topic sets digit, uppercase and colon rates; a goal kickoff day shifts everyone | day FE g_d in G; attribution centres each held-out day on its label-free mean; registers are exogenous by design (the effect, not an impostor) | within-day operator messages are not modelled (rare in regime III) |
| Shared model priors (family, style) | q_i is the prior; the impostor is calling a family-shared drift agent-specific, or a family offset a register | agent FE absorb family offsets; b_i is estimated per agent; #51 register coherence is compared with a lab-matched check (media vs non-media within the same lab where possible) | 4 media incumbents only |
| Contemporaneous convergence | context fills with other agents' messages, so drift could be accommodation to the room's current register | R4: own fill z(p) vs received fill log2(1 + k_ctx) fitted together (regime III); NE41 erasure removes own context but not the room | k_ctx and p correlate within a segment |

## Prediction
*Written 2026-10-04 19:13 UTC, before running the analysis on real data.*

**Replication (card level; verdict rules fixed now).**
- **P1 "most" (the headline):** F3 ≥ 0.5 in ≥ 2/3 of eligible periods and the median F3 ≥ 0.5. *Against:* median F3 < 0.5 (agent-day jitter η carries most of the systematic variance: R1 wins). My prior: 55% that P1 passes; H46's goal-switch shift says η is not small.
- **P2 ordering:** the agent constant has the largest unique share (u_A > u_C and u_A > u_R) in ≥ 80% of periods; the context share is positive (null p < 0.05) in ≥ 2/3 of periods with ≥ 500 computer-use messages. *Against:* u_C null in more than 1/3 of those periods.
- **P3 attribution (the HH's second clause):** context removal raises attribution. Pass if Δ_b or Δ_c (pre-registered primary: Δ_c, the agent-specific context model; Δ_b secondary) at k = 5 is > 0 in ≥ 2/3 of periods, the sign test p < 0.05, and the period-mean gain ≥ +0.01 with a bootstrap CI above 0. *Against:* period-mean Δ_c ≤ 0 or CI including 0. My prior: 50%; H46's in-context drift is a growing *distance*, which may be mostly R5 (no fixed direction).
- **P4 dispersion (R5 signature):** the residual squared norm rises with z (slope > 0, p < 0.05) in ≥ 2/3 of periods with ≥ 500 computer-use messages. P4 passing with P3 failing means the context component is an excitation, not a drift: the HH's attribution claim fails for a reason the model names.
- **P5 rivals:** u_C keeps ≥ 50% of its size after the genre controls (R2) and after dropping p ≤ 1; in regime III the unique share of own fill z(p) exceeds that of received fill (R4).

**Natives (dated predictions also in each folder).**
- **N1 NE41:** the within-segment profile predicts the erasure jump: β ∈ [0.3, 1.5] with the cluster CI excluding 0, and subtracting Δx̂ lowers the forced-erasure T_s by ≥ half of its excess over ½. *Against:* β CI including 0 (the erasure effect is not the reversal of the fitted drift).
- **N2 G12:** judging is a shared register: mean leave-agent-out cosine > 0 with permutation p < 0.05, u_R > 0 (p < 0.05), and register-corrected attribution of judge blocks beats uncorrected by ≥ 0.05. *Against:* cosine ≤ 0 (each judge moves its own way: register is agent-specific, not assigned).
- **N3 G51:** (i) the Prankster's register shift stays beyond its placebo shifts (percentile ≥ 0.95) after context removal: the persona is register, not context. (ii) Media incumbents share a register direction (mean pairwise cosine above other pairs, permutation p < 0.05). *Against:* (i) percentile < 0.9 after detrending; (ii) p ≥ 0.05 (registers are role-specific or agent-specific, not class-shared). Prior for (ii): 40%.
- **N4 G44 (descriptive):** base Kimi K2.6 ranks ≤ 2 among ~17 regime-III centroids for the leader, blind and detrended; detrending does not lower its rank.

**Overall reading (fixed now).** H73 is **supported** if P1 and P3 pass and at least one register native (N2 or N3) passes. **Mixed** if exactly one of P1 and P3 passes. **Refuted** if both fail. P4 decides whether a P3 failure is a directionless excitation (R5) or no context effect at all.

## Synthetic validation (axis F; run 2026-10-04 19:19–19:27 UTC, before any real-data decomposition, attribution or NE41 statistic)
`analysis/synthetic.py` → `data/processed/H73-style-three-components/synthetic/synthetic.json`. Village sampling: the real eligible-message schedule of G12, G18 (regime I, 21% and 13% computer-use chat), G38, G41 and G51 (regime III, 2,058–40,069 messages): agent, day, hours, context bin and fill, register. Message noise is each agent's own real style vectors with its mean removed, permuted within agent (day, context and register structure destroyed), unit SD per feature. Planted parts in noise-SD units: agent constant SD 0.4, agent-day jitter SD 0.2, day field SD 0.15; S1 drift: bin profile and agent slopes SD 0.15 per unit z; S2 excitation: a random direction per context segment, SD 0.6, growing as p/40. 30 replicates per period (10 for G51), 49 permutations.

| Check | Result |
| --- | --- |
| Context null size (S0; reject u_C at p < 0.05) | 0.03 / 0.03 / 0.07 / 0.13 / – (G12 / G18 / G38 / G41; G51 run without permutations) |
| Context power (S1, u_C 0.05–0.21) | 1.00 in every period |
| u_C under S2 (excitation, no mean profile) | ≈ 0 (−0.001 to 0.006): the decomposition cannot see R5 |
| Attribution gain Δ_c under S0 | −0.006 to −0.023 (biased *down*: agent slopes add estimation noise); Δ_b ≈ 0 |
| Δ_c under S1 | +0.002 (G18) to +0.063 (G51); positive in 63–100% of replicates |
| Δ_b under S1 | ≈ 0 (−0.001 to +0.004): a common profile shifts every candidate alike, so only agent-specific drift can help attribution |
| Dispersion slope detected (CI > 0), S0 / S2 | G12 0.17 / 0.30; G18 0.20 / 0.60; G38 0.03 / 0.90; G41 0.13 / 0.97; G51 0.10 / 1.00 |
| F3 bias (estimate − planted), sd_η 0.05 / 0.2 / 0.4 | G12 −0.09 / −0.02 / +0.06; G18 −0.06 / −0.01 / +0.06; G38 −0.09 / −0.05 / +0.01; G41 −0.03 / 0.00 / +0.07; G51 +0.10 / +0.08 / +0.04 |
| NE41 β (forced), first version: S0 / S1 / S2 | 0.29 (CI > 0 in 90%) / 0.96 / 0.26: **biased** (shared endpoints) |
| NE41 β after day cross-fitting: S0 / S1 / S2 | −0.03 (CI > 0 in 0%) / 0.88 (100%) / −0.02 (0%) |
| NE41 T_s forced, raw → corrected: S0 / S1 / S2 | 0.500 → 0.502 / 0.512 → 0.500 / **0.556** → 0.558 |

Readings: (1) the context null holds size near nominal (G41's 4/30 is within binomial noise). (2) A directionless excursion (S2) reproduces H46's forced-erasure style move (T_s 0.556 vs H46's real 0.564) with β ≈ 0 and no attribution gain, while a directed drift (S1) gives β ≈ 0.9 with a small T_s. So β, not T_s, separates drift from excursion. (3) The dispersion test has power and size only where computer-use chat is dense.

## Amendments (2026-10-04 19:27 UTC, after the synthetic validation, before any real-data statistic)
- **A1 (NE41 cross-fitting).** The within-pair profile is fitted on the days of one parity and evaluated on the other (2-fold by PT day). The first version leaked message noise through endpoints shared by within and crossing pairs (β 0.29 under the null).
- **A2 (F3 margin).** F3 overestimates by up to +0.07 near F3 ≈ 0.55 (and up to +0.10 in G51 at high F3). P1 counts a period as "most" only if F3 ≥ 0.57; the median rule uses the same threshold. Raw F3 is reported.
- **A3 (dispersion scope).** P4 is judged on periods with ≥ 2,000 computer-use messages (G04, G13, G38, G41, G51), where size ≤ 0.13 and power ≥ 0.9. Elsewhere the slope is descriptive.
- **A4 (attribution primary).** Δ_c (agent-specific context) stays primary; Δ_b is reported but cannot gain by construction (S1). The negative null bias of Δ_c makes P3 conservative.

## Results by goal period
Roles: `replication` = templated layer-1 point (not an independent test); `native` = period-specific design. G12, G44 and G51 carry the replication estimator inside their native READMEs; their verdict here is the native one.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G03](goalperiod-subhypotheses/G03/README.md) | replication | mixed | F3 1.03 [0.47, 1.59]; u_A 0.73, u_C 0.177 (p 0.005); Δ_c -0.040 |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | mixed | F3 0.64 [0.59, 0.69]; u_A 0.55, u_C 0.072 (p 0.005); Δ_c -0.003 |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | mixed | F3 0.64 [0.52, 0.76]; u_A 0.55, u_C 0.041 (p 0.005); Δ_c -0.010 |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | supported | F3 0.60 [0.54, 0.67]; u_A 0.47, u_C 0.025 (p 0.005); Δ_c +0.007 |
| [G07](goalperiod-subhypotheses/G07/README.md) | replication | mixed | F3 0.87 [0.80, 0.95]; u_A 0.67, u_C 0.134 (p 0.005); Δ_c -0.054 |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | supported | F3 0.62 [0.57, 0.68]; u_A 0.46, u_C 0.078 (p 0.005); Δ_c +0.011 |
| [G10](goalperiod-subhypotheses/G10/README.md) | replication | supported | F3 0.78 [0.68, 0.88]; u_A 0.60, u_C 0.079 (p 0.005); Δ_c +0.009 |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | supported | F3 0.67 [0.54, 0.81]; u_A 0.44, u_C 0.104 (p 0.005); Δ_c +0.020 |
| [G12](goalperiod-subhypotheses/G12/README.md) | native | mixed | judge register: u_R 0.056 (p 0.001), shared direction cos +0.78 (p 0.001); attribution gain +0.01 (fail). Replication: F3 0.67 [0.58, 0.76]; u_A 0.43, u_C 0.071 (p 0.005); Δ_c +0.061 |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | supported | F3 0.73 [0.69, 0.77]; u_A 0.48, u_C 0.074 (p 0.005); Δ_c +0.029 |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | supported | F3 0.66 [0.59, 0.72]; u_A 0.47, u_C 0.112 (p 0.005); Δ_c +0.044 |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | supported | F3 0.67 [0.59, 0.75]; u_A 0.51, u_C 0.059 (p 0.005); Δ_c +0.037 |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | mixed | F3 0.58 [0.52, 0.64]; u_A 0.46, u_C 0.085 (p 0.005); Δ_c -0.014 |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | supported | F3 0.60 [0.53, 0.67]; u_A 0.47, u_C 0.098 (p 0.005); Δ_c +0.021 |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | supported | F3 0.60 [0.53, 0.66]; u_A 0.49, u_C 0.092 (p 0.005); Δ_c +0.006 |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | mixed | F3 0.76 [0.61, 0.90]; u_A 0.57, u_C 0.148 (p 0.005); Δ_c -0.028 |
| [G23](goalperiod-subhypotheses/G23/README.md) | replication | mixed | F3 0.65 [0.47, 0.83]; u_A 0.39, u_C 0.110 (p 0.005); Δ_c -0.007 |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | mixed | F3 0.73 [0.60, 0.85]; u_A 0.54, u_C 0.093 (p 0.005); Δ_c -0.011 |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | supported | F3 0.66 [0.60, 0.73]; u_A 0.39, u_C 0.120 (p 0.005); Δ_c +0.011 |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | mixed | F3 0.68 [0.60, 0.75]; u_A 0.45, u_C 0.121 (p 0.005); Δ_c -0.030 |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | supported | F3 0.62 [0.51, 0.72]; u_A 0.45, u_C 0.088 (p 0.005); Δ_c +0.008 |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | supported | F3 0.83 [0.81, 0.85]; u_A 0.57, u_C 0.125 (p 0.005); Δ_c +0.007 |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | mixed | F3 0.76 [0.70, 0.82]; u_A 0.56, u_C 0.125 (p 0.005); Δ_c -0.019 |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | mixed | F3 0.80 [0.75, 0.86]; u_A 0.60, u_C 0.129 (p 0.005); Δ_c -0.032 |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | mixed | F3 0.76 [0.69, 0.83]; u_A 0.52, u_C 0.144 (p 0.005); Δ_c -0.053 |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | mixed | F3 0.66 [0.45, 0.88]; u_A 0.57, u_C 0.041 (p 0.005); Δ_c -0.007 |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | mixed | F3 0.87 [0.27, 1.48]; u_A 0.79, u_C 0.005 (p 0.303); Δ_c -0.071 |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | supported | F3 0.77 [0.65, 0.90]; u_A 0.76, u_C 0.006 (p 0.005); Δ_c +0.005 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | mixed | F3 0.99 [0.80, 1.17]; u_A 0.99, u_C 0.000 (p 0.100); Δ_c -0.038 |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | mixed | F3 0.76 [0.65, 0.87]; u_A 0.74, u_C -0.000 (p 0.174); Δ_c -0.031 |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | supported | F3 0.84 [0.72, 0.96]; u_A 0.78, u_C 0.025 (p 0.005); Δ_c +0.003 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | mixed | F3 0.99 [0.82, 1.16]; u_A 0.91, u_C 0.061 (p 0.005); Δ_c -0.061 |
| [G44](goalperiod-subhypotheses/G44/README.md) | native | descriptive | leader → Kimi K2.6 rank 3 blind, 3 detrended, 1 agent-specific context (20 messages). Replication: F3 0.82 [0.61, 1.03]; u_A 0.77, u_C 0.019 (p 0.010); Δ_c +0.008 |
| [G51](goalperiod-subhypotheses/G51/README.md) | native | failed | Prankster era shift percentile 0.60 (with and without C); media coherence cos −0.11 (p 0.56); post hoc onset blocks 1.00. Replication: F3 0.71 [0.68, 0.75]; u_A 0.66, u_C 0.015 (p 0.010); Δ_c -0.002 |
| [NE41](goalperiod-subhypotheses/NE41/README.md) | native | mixed | forced β 0.27 [0.12, 0.36]; predicted/observed jump 0.017; T_s 0.567 → 0.568 after removing the drift |

## Outcome vs prediction
*Run 2026-10-04 19:29–19:46 UTC (`analysis/replication.py`, `analysis/natives.py`). All non-holdout; copies (`self_repeat_both`) removed.*

| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 most: F3 ≥ 0.57 in ≥ 2/3 of periods, median ≥ 0.57 | 34/34 periods; median F3 0.72 (IQR 0.65–0.80); agent-day ceiling (post hoc): median 0.82 | **pass** |
| P2 ordering: u_A largest in ≥ 80%; u_C p < 0.05 in ≥ 2/3 of periods with ≥ 500 computer-use messages | u_A largest in 34/34 (median 0.55); u_C p < 0.05 in 23/26 (median u_C 0.08) | **pass** |
| P3 attribution: Δ_c > 0 in ≥ 2/3, sign p < 0.05, mean ≥ +0.01 with CI > 0 | 16/34 positive (sign p 0.70); mean Δ_c −0.007 [−0.017, +0.003]; Δ_b +0.001; k = 1: +0.001 | **fail** |
| P4 dispersion rises with fill (≥ 2/3 of the 5 dense periods) | CI > 0 in 1/5 (G41); G51 slope negative (CI [−0.48, −0.02]) | **fail** |
| P5 rivals: u_C keeps ≥ 50% under genre controls and without p ≤ 1; own fill > received fill (regime III) | retention 1.04 (genre) and 0.97 (p ≤ 1 dropped): pass. Received fill beats own fill in 6/8 regime-III periods: fail | **partial** |
| N1 NE41: β ∈ [0.3, 1.5], CI > 0; T_s excess at least halved | β 0.27 [0.12, 0.36]; predicted jump 1.7% of the observed; T_s 0.567 → 0.568 | **mixed** (β > 0, drift explains almost none of the jump) |
| N2 G12: u_R > 0; shared judge direction; attribution gain ≥ 0.05 | u_R 0.056 (p 0.001); cos +0.78 (5/5 judges +0.65 to +0.83; p 0.001); gain +0.01 | **mixed** (register real and shared; attribution clause fails) |
| N3 G51: Prankster ≥ 0.95 after detrending; media share a direction | Prankster 0.60 (era design); media cos −0.11 vs −0.06 (p 0.56) | **failed** |
| N4 G44 (descriptive): Kimi rank ≤ 2, detrending does not lower it | rank 3 blind and common-detrended, 1 with agent-specific context (20 messages) | not met (descriptive) |

**Overall (pre-registered reading):** P1 passes and P3 fails, so H73 is **mixed**. The three-component model explains most of the systematic style variance, but almost all of that is the agent constant. Removing the context component does not raise attribution, because the context component is small and mostly shared by agents. P4 fails too, so the P3 failure is not a hidden directionless excitation measured by fill. One assigned register (judging) passes its shared-direction test (N2); the #51 roles fail theirs (N3).

## Results
**1. A message's style is mostly noise; the systematic part is mostly the agent.** The cell ceiling κ (agent × day × context bin × register) is 0.27 [0.16, 0.49] of the per-message style variance, so about three quarters of a single message's style is message noise. The day field takes 14% of κ (median). Of the rest, the agent constant has the largest unique share in all 34 periods (median u_A 0.55). The three components together explain F3 = 0.72 (IQR 0.65–0.80). At agent-day resolution (post hoc PH1), agent-day jitter η keeps 0.18 (IQR 0.15–0.26) of the non-day systematic variance, so R1 is a minority term.

**2. The context component is small, and most of it is not own context length.** The median unique context share is 0.08, significant in 23/26 dense periods. It differs by regime: 0.093 in regime I, 0.129 in regime II, 0.011 in regime III. In regimes I/II about half of it is the level difference between chat-mode and computer-use messages (post hoc PH2: 0.095 → 0.041 without the mode level). In regime III the received-item fill (`k_ctx`) carries more unique share than own fill (6/8 periods; e.g. G41 0.060 vs 0.017). So what the context window does to style follows the conversation that fills it (R4), not the agent's own context length. Genre controls (reply, mention) and dropping the first two calls after a reset leave u_C unchanged (retention 1.04 and 0.97), so R2 is not the carrier.

**3. Attribution does not gain from context removal.** Leave-one-day-out balanced accuracy on blocks of five messages has median 0.63 (chance 0.10). The agent-specific context model changes it by −0.007 [−0.017, +0.003] on average (16/34 periods positive). The synthetic planted drift (u_C 0.05–0.21) gives +0.002 to +0.063 and the null gives −0.006 to −0.023. The real gains sit at the null. A common profile cannot help by construction (Δ_b +0.001).

**4. Erasure: the style jump is not the reversal of a directed drift.** At forced erasures the out-of-fold drift projection is β = 0.27 [0.12, 0.36] (CI > 0), but the predicted jump is 1.7% of the observed squared jump. The style percentile T_s is 0.567 [0.533, 0.595], as in H46 (0.564), and stays 0.568 after removing the predicted jump. Synthetic S2 (a random context excursion with no fixed direction) gives T_s 0.556 with β ≈ 0. The real erasure looks like S2 plus a small directed drift. The residual dispersion does not rise with log fill, though (P4 fails; G51 falls). So the excursion is not a simple function of fill (see caveats).

**5. Assigned registers: one shared, one not.** In #12, judging shifts style in one direction shared by all five judges (leave-agent-out cos +0.78, p 0.001; u_R 0.056, p 0.001). The shift does not help attribution: a shift common to all candidates barely changes the ranking (post hoc reading of N2 iii). In #51, the four media incumbents (three labs) share no register direction (cos −0.11, p 0.56). The Prankster's three-week era shift sits at percentile 0.60 of its placebo shifts. With H46's 3-day onset blocks (post hoc PH3) it is 1.00 among 42 pairs, with and without the context component. The persona shift is real at onset, is not context, and does not persist as a constant three-week offset.

**6. Model swap (G44, 20 messages).** The fine-tuned leader's style is nearest to base Kimi K2.6 only under the agent-specific context model (rank 1); blind and common-detrended it is rank 3 behind two Anthropic agents. One block of 20 messages: descriptive.

Figures: `figures/summary_obs.pdf` (variance shares and attribution gain per period), `figures/summary_obsb.pdf` (NE41 β and T_s against synthetic scenarios; #12 judge cosines). Data: `data/processed/H73-style-three-components/` (`replication/replication.json`, `natives/natives.json`, `synthetic/synthetic.json`, `confirm/confirm_dryrun.json`). Estimates: 183 rows in `per_period_estimates` (hypothesis H73).

## Faithfulness scorecard
*Round 1, 2026-10-04.*
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed.
**Rival models:** R1 agent-day state, R2 genre, R3 clock, R4 accommodation (received fill), R5 directionless excitation.
**Locked holdout used for confirmation:** none yet (`analysis/confirm.py`, dry-run only).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Style, fill, mode, register and genre flags all come from shared tables (`text_features`, DQ1 ledger, DQ6, DQ2). The context term is not regime-invariant: in regimes I/II half of it is the chat/computer-use mode level, in regime III it is 0.011. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Agent + context + register leaves agent-day jitter at 0.18 of the systematic variance, so the state is nearly but not fully Markov in these variables. Time of day is controlled. H46's axis-B failure (style depends on position) is quantified: the position term is small. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Beats G + A (context permutation p < 0.05 in 23/26; F3 ≥ 0.57 in 34/34). F3 is an in-sample adjusted R² with a synthetic bias of up to +0.07; the held-out-day test (attribution) shows no gain from the context term. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | NE41 β is out of fold (0.27, CI > 0); the predicted erasure jump is 1.7% of the observed. Attribution is leave-one-day-out: no gain. |
| E interventional | predicts the change across a natural experiment | 1 | Forced erasures (exogenous): the drift predicts the sign, not the size. #12 judge draw: a shared register (cos 0.78). #51 roles: no class register, onset transient only (post hoc). |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 | Synthetic at real counts in five periods: size and power of the context null, F3 bias, attribution null bias, NE41 leakage found and fixed (A1). Variants agree: raw 20-d style (median F3 0.74), restatements removed (0.72, Δ_c −0.005), genre controls, p ≤ 1 dropped, agent-day ceiling (0.82). |
| G ground truth | agrees with known structure | 1 | DQ6 judges and roles define registers; judges share a direction. The leader's base model is recovered only under the agent-specific context model (rank 1; blind rank 3). |
| H comparative | beats the named rivals | 1 | Beats R1 (η 0.18), R2 (retention 1.04) and R3 (controlled). Loses to R4 in regime III (received fill > own fill in 6/8). R5 fits the erasure (T_s 0.567 with a 1.7% drift) but its fill signature (P4) fails. |
| I transfer | holds in other same-mode periods, including the holdout | 1 | F3 ≥ 0.57 and u_A largest in all 34 periods across three regimes; the context share does not transfer across regimes. Holdout not run. |

**Faithfulness lever (HH265 aimed at H46's B and H).** Partly raised. H46's B failure (position matters) is now a measured, small term (u_C 0.08; 0.011 in regime III), and H46's losing rival R1 (style as state) is bounded: state-like parts (context, register, agent-day jitter) together hold about a quarter of the systematic variance.

## Confirmatory predictions (written 2026-10-04 19:50 UTC after round 1, before any holdout use; `analysis/confirm.py`, dry-run only, **not run**)
Targets: held-out goal periods (#1, #9, #14, #15, #22, #28, #29, #32, #34, #43, #45–#50), the #51 tail, NE41 on held-out regime-III days, NE30.
- **C1:** F3 ≥ 0.57 in ≥ 2/3 of eligible held-out periods and median ≥ 0.57.
- **C2:** u_A largest in ≥ 80%; u_C p < 0.05 in ≥ 2/3 of periods with ≥ 500 computer-use messages.
- **C3:** no material attribution gain: mean Δ_c < +0.02 and fewer than 2/3 of periods positive.
- **C4:** NE41 forced β < 0.6 with predicted jump < 5% of observed, and T_s ≥ 0.53 with CI lower bound > 0.5.
- **C5:** regime III: median (u_recv − u_own) > 0. **C6 (NE30, descriptive):** Gemini 3 Pro among the 2 nearest style centroids of Gemini 3.1 Pro.
- **Overall:** confirmed if C1–C4 pass. Dry run on stand-ins (G13, G38, G41; #51 07-06 → 08-31): C1, C2, C4, C5 pass; C3 fails because all three stand-ins have small positive Δ_c (+0.003 to +0.029). C3 is a genuine risk with few held-out periods.
- **Reuse disclosure:** the #51 tail is targeted by unrun scripts of H14, H18, H20, H22, H34 and H46. H46's C3 (NE41 gap-matched T_s) is the same estimator family as H73's C4 T_s clause and must be disclosed if both run. #45: H02 (run, activity timing), H23 (unrun, content).

## Caveats
- **What "style" is.** H13's 20 features with length, code and links controlled. Digits, uppercase and colons are topic-adjacent (H46). A function-word stylometry was not tried.
- **F3 depends on the ceiling.** The cell ceiling is noisy where cells are small; F3 exceeds 1 in G03 and is near 1 in G39 and G42. The synthetic bias reaches +0.10 in G51 at high F3. The agent-day ceiling (post hoc) gives the same ranking.
- **Context in regimes I/II** mixes the chat/computer-use mode level with fill. Chat-mode calls have no `ctx_pos`.
- **The fill variable is calls since the last reset**, not chat messages since the reset (H46 PH3) and not prompt tokens. The excursion at erasure (T_s 0.567) may follow a variable that fill does not track.
- **Agent slopes are pooled over regime III** in NE41 (an agent-level property, exception (b)), not checked for invariance across periods.
- **Small natives.** Five judges in #12; four media incumbents; one Prankster; 20 leader messages.
- **Post hoc labels.** PH1 (agent-day ceiling), PH2 (mode-free context share), PH3 (H46's onset blocks) and the reading of N2 (iii) were added after the pre-registered results were seen.

## Round 2 redirects (2026-10-04)
*Proposed by the round-1 agent; the coordinator may revise.*
- **Where round 1 went sideways:** "context" was operationalized as own calls since the reset, but in regime III style follows what others post into the context (received fill), and the erasure jump has no fixed direction.
- **What the direction is really after:** which parts of an agent's style a monitor can trust as identity, and which parts the conversation writes.
- **H73-R1.** Conversation-state model: replace fill with received items, pending @-mentions and thread depth (DQ2), and test accommodation with H57's in-flight placebo (posted-but-unread at matched lag).
- **H73-R2.** Register as a transient: a daily event study of the #51 onset and NE38 (decay time of the persona shift), and the #12 judge shift by minute within a debate.
- **H73-R3.** Excursion model: an Ornstein–Uhlenbeck process within a context segment on message position (H46-R2), with its direction random per segment; fit its variance growth and test it at NE41.
- **H73-R4.** Model swaps: the NE30 test in the holdout (frozen as C6); in round 2 a larger leader sample (#45 is held out).

## Notes
- 2026-10-04 19:13 UTC: card written by the round-1 agent before any real-data style statistic. The Kolchinsky–Wolpert model (04) is listed on the stub but not tested: H46 already ran it, and HH265 does not ask for it.
- 2026-10-04: the first drafts of the card and period READMEs carried hand-written timestamps (19:15, 19:30–19:50, 19:55, 19:58 UTC) that ran ahead of the clock. They were corrected from file modification times at 19:38 UTC. The order (card → synthetic → amendments → period predictions → real runs) is unchanged and is confirmed by the file times: messages.parquet 19:14, synthetic.json 19:27, period READMEs 19:28, replication.json 19:33.
- 2026-10-04: the F3 interval was first a day bootstrap (skewed: duplicated days raise F3). It was replaced by a delete-one-day jackknife before any verdict depended on it. The verdict rules do not use the interval.
- 2026-10-04: runs used ≤ 4 worker processes, then ≤ 2 after the coordinator's load note. Data: `data/processed/H73-style-three-components/` (~15 MB) with `_provenance.json`. No code is imported from another hypothesis; H46's style construction is re-implemented in `scheme/build.py`.
