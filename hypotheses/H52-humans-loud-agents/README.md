# H52: Humans are just loud agents

**Status:** exploratory round 1 **done (2026-10-04, UTC): mixed. Humans are not just loud agents in replies; the premium is small, plan-congruent, and shared by agent leaders.** Design, nulls and predictions were written ~06:10 UTC before any outcome; Amendment A1 (synthetic-based) ~09:30 UTC, also before any outcome. 17 replication periods + 4 native tests (G04, G51, NE43, G26/G35/G44).
- **Replies:** matched on naming, read-out age, novelty, length, recipient state and room size, a human message is answered more often than a comparable agent message: pooled +0.030 [0.019, 0.042] (17 periods; CI > 0 in 8, none below 0), about **2× the matched agent rate** (G51 +0.029 on 0.028) but a quarter of the effect of being named (+0.13). Matching flips the regime-I sign (naive −0.03): viewers rarely name agents.
- **Content:** a small positive premium. G51 +0.014 [0.008, 0.021], robust across five statistics and in 5/5 #51 segments; about half the naming effect under H30's statistic. In regime I, H29's boundary design gives +0.05 [0.03, 0.07] (G04) and +0.09 (G05); the DiD statistic reads ≈ 0 there but carries a known −0.024 bias.
- **Activity ≈ 0** (regime I pooled −0.09 [−0.35, 0.18]; regime III +0.41 [0.05, 0.77], per-period CIs include 0). **Stance:** replies to humans are more supportive (+0.16 [0.10, 0.23], mostly regime I; the labeller knew the author was human).
- **Not deference against the plan (N2, #51 roles):** the reply premium is +0.037 for messages aligned with the recipient's private role, +0.007 off-role, −0.007 for the most role-conflicting third (difference +0.035 [0.012, 0.062]).
- **Authority by role, not species (N4):** an elected (G26) and operator-appointed (G35) agent leader get the same reply premium (+0.028, +0.029; CI > 0) and no content premium; a weak fine-tuned leader (G44) gets none.
- **The bot is a rebuffed agent:** given read-out, nudges move content, replies and the target's activity like matched agent messages (pooled over 12 periods), but replies to them push back (stance −0.97 in G51).
- **NE43:** content premium unchanged across the nudger stop; the reply premium vanished after it (−0.039 [−0.072, −0.005], 16 human messages after).
- **Method:** H30's orthogonalized χ_con is biased by shared topic (synthetic −0.02 to −0.03) and the DiD χ's naming effect is negative (reply-quoting regression to the mean), so content verdicts rest on agreement across statistics with opposite biases. The placebo-class null is anti-conservative.
- **Formal verdict (pre-registered rule): mixed.** Content is beyond the margin (0.0073) in G51 and the regime-III pool but not in ≥ half the powered periods (1/3); replies show a positive premium inside their margin (0.064); content and activity are not both equivalent to 0. (The content margin used the absolute DiD naming effect, which came out negative; see P8.)
- Scorecard A1 B1 C1 D1 E1 F1 G1 H1 I1. `analysis/confirm.py` (#51 tail, #46–#50, #45) written and dry-run on stand-ins, **not run**.
**Fields:** sociophysics, stat mech, info theory
**Literature:** none of the notes in `literature/` covers social influence or deference. Cited from memory (†, not in `literature/`): Friedkin & Johnsen, *J. Math. Sociol.* 15, 193 (1990)† (influence with susceptibility to outside fields); French, *Psychol. Rev.* 63, 181 (1956)† (social power); Sharma et al., "Towards understanding sycophancy in language models", arXiv:2310.13548 (2023)† (deference to users); Iacus, King & Porro, *Political Analysis* 20, 1 (2012)† (coarsened exact matching).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime; Driving / external field (human messages; automated nudges); Exposure (turn read-out) as implemented by the context ledger (DQ1); Agent state, vector variant (whitened statement embedding, 32-d, unit-normalized; bge-small primary, gte-modernbert second model; style-residualized-per-period variant for robustness); Interaction (addressed) for named recipients and Interaction (broadcast) for unnamed room-mates; H29's *influence coupling (content pull)* and *visibility jump (boundary test)*; H30's *operator kick classes* and *content susceptibility χ_con (orthogonalized placebo)*; H30's *activity susceptibility* (here with a day and recipient fixed effect, past-only controls); H39's *field effect* reading of the premium. New terms, defined below and proposed for the shared file: **sender class**, **salience covariates**, **authority premium π** (per channel).
**From:** HH164 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/02-nonequilibrium-ising/` (linear response to fields; fields vs couplings)
**Data inputs (shared tables first):** DQ1 context ledger (`context_ledger_items`, `call_windows`, `context_ledger_turns`); DQ2 `reply_pairs` (`pair_set = cand`) and `reply_threading/candidates_ledger`; `kicks_classified`; `chat_core`, `chat_mentions_clean`; DQ5 embeddings (bge-small and gte-modernbert, regime whiteners; `statements_style_resid_period32`), `statement_flags`; `activity_bins_fixed`; DQ6 `ground_truth_labels`; `period_units`, `calendar`, `roster`. `chat_text` is read in memory only to find a nudge's leading @ (H35's rule); no text is written.

## Question
On the read-out-gated, name-gated channel (H08: a response waits for the recipient's next model call; H29: a message that names its recipient pulls it 3–6× more than an unnamed one), does a human message move its recipient as much as an agent message with the same naming, read-out timing, content novelty, length, recipient state and room size? Or is there an **authority premium**, a deference term beyond salience?

Alignment relevance: a premium ≈ 0 means human authority in the swarm works only through being named and being new; a large positive premium means a distinct deference channel; a negative premium means humans are discounted. The operator's bot (automated nudges) is a third sender class: is it treated like a human, like an agent, or like neither?

## Design: two layers (Vivian, 2026-10-04; see `infra/data-quality/QUEUE.md`)
- **Replication:** the common estimator on every eligible goal period (comparable phase-diagram points). Period README role: `replication`. The replication prediction is templated and labelled as such.
- **Period-native tests:** four tests whose setup gives special leverage, each with its own observable, null or ground truth, and its own dated prediction. Period README role: `native`.

## Model
**From:** `physics-models/02-nonequilibrium-ising/` (linear response of a spin to a field; a message is an impulsive field on its recipients).

**H52 variant: salience-gated linear response with a sender-class field.** A message m reaches recipient j at j's receiving call c (DQ1 ledger). Let s_m = (named, age at c, novelty, length, recipient state, room size) be the **salience covariates**. Each channel responds as

- content (vector spin x_j, whitened statement embedding): E[x_j(after c) · û⊥_m] − E[same for a same-class placebo] = g_con(s_m) + π_con[cls(m)];
- reply: P(m becomes the parent of one of j's next messages) = g_rep(s_m) + π_rep[cls(m)];
- activity (binary spin n_j(t)): E[Σ_{τ=1..30 min} n_j(t_c + τ) | past] = g_act(s_m, past) + π_act[cls(m)];
- stance (among replies to m): E[P(supports) − P(opposes)] = g_st(s_m) + π_st[cls(m)];

with π[agent] ≡ 0 (reference), π[human] the **authority premium** and π[bot] the bot's premium. û⊥_m is the message direction with the recipient's last ≤ 8 statements (2 h) projected out (H30's orthogonalization), so the content channel measures movement toward what the message *adds*. In Ising language, a message is a field h_m = a(s_m) û_m on j's content spin, with a coupling a set by salience alone; the premium is a separate field term π û_m that only human (or bot) messages carry. The salience function g is common to all sender classes (the scaffold's read-out gate and naming gate act on any message).

**H52 (HH164):** π_human = 0 in every channel: a human is a loud agent whose larger raw effect comes from salience (being named, new, read at a good time).

**Rivals.**
- **R1 deference:** π_human > 0 in content and replies (and more support in stance). Expected from LLM post-training toward following users (Sharma et al.†).
- **R2 discount / out-group:** π_human < 0: human messages (e.g. the 2025 public viewers) are treated as noise.
- **R3 salience-only (H52):** π_human = 0; the naive human − agent contrast is explained by s_m.
- **For the bot:** B1 *like a human* (π_bot ≈ π_human); B2 *like an agent* (π_bot ≈ 0); B3 *neither* (an activity field with no content or reply uptake; expected from H30 and H39).

**Theory notes, written before the data.**
1. *Why matching is necessary.* With strong salience effects (named/unnamed 3–6×; pull decays 5–23× with age), any difference in how often humans name, how new their content is, or when their messages are read biases the naive human − agent contrast by far more than a plausible premium. The estimand is therefore an ATT over human messages: the human row's response minus the mean response of agent rows in the same salience stratum.
2. *Unit of comparison.* The receiving call (ledger) fixes timing: a message posted while j's call was being generated is read only at the next call, so `age_s` is the read-out age, not the posting gap. All four outcomes are aligned to the receiving call.
3. *Premium as a field term.* The premium is identified only relative to agent messages with the same salience. If no agent messages exist in a stratum (e.g. very long goal kickoffs), the premium is not identified there; such rows are reported as unmatched, never extrapolated.
4. *What the premium is not.* Humans differ from agents in what they say (requests, questions, instructions). Matching on novelty and length does not remove speech-act differences; a positive premium therefore bounds "deference to humans *or* to the kind of thing humans say". Native test N2 (#51 roles) and N4 (appointed agent leaders) separate parts of this.

## Data scheme (`scheme/`)
`scheme/build.py --period G<NN>` reads shared tables only and writes, per period, `data/processed/H52-humans-loud-agents/G<NN>/` (zstd parquet, numbers and codes only; no text, no vectors) plus `_provenance.json`:
- **`rows.parquet`**, one row per (message m, recipient j) from `context_ledger_items` (non-holdout days of the period; `omitted` items dropped; kinds agent / human / nudge):
  - identity: `item`, `message_id`, `msg`, `turn_id` (receiving call), `recv`, `sender` (agent code; −1 human, −2 bot), `cls` (0 agent, 1 human, 2 bot), `kickoff` (human goal kickoff, from `kicks_classified.subkind`), `day_idx`, `pt_date`, `t_m`, `t_call`;
  - salience covariates: `named` (agents and humans: `context_ledger_items.ment`, i.e. `chat_mentions_clean.mentions_roster` names j; bot: j is the nudge's **leading @**, H35's rule), `age_s`, `uncertain`, `nov` (novelty ‖P⊥û_m‖ ∈ [0, 1] relative to j's last ≤ 8 statements in the previous 2 h; null if none), `len` (characters), `idle` (receiving call follows a pause, first call of the day or session start, per `call_windows.gap_kind`), `n_recv` (distinct ledger recipients of m: room size), `k_new` (new items at c), `pre15` (j's active minutes in the 15 min before t_call), `since_act`;
  - outcomes: `chi` (content, below), `q_true`, `q_pl`, `n_pre`, `n_post`, `chi_gte` (second embedding model), `chi_sr` (recipient statements style-residualized per period); `rep` (m is the DQ2 `parent` of one of j's messages, `pair_set = cand`), `rep_soft` (max labelled p_reply of a (m, j-message) candidate pair), `rep_lab` (any labelled candidate pair exists), `rep_nf_risk` (bias diagnostic, below); `st` (soft stance P(supports) − P(opposes) of the parent pair), `st_opp`, `st_ask`; `y30` (j's active minutes in (t_call, t_call + 30 min], `activity_bins_fixed` states 3–4), `y30_ok` (horizon inside the day's window).
- **`boundary.parquet`**, H29's boundary design on the ledger: one row per (talk call c of j, message m) with m posted < 30 s before c's talk statement, visible (arrived before `t_call(c)`) or truly invisible (arrived during c, with c's window `t_log − t_call` ≤ 30 s). Columns `yu`, `uu`, `yu_x`, `uu_x` (H29's pull sums with a cross-day placebo partner: same sender for agents, same class otherwise), `vis`, `dt_talk`, `c`, `day_idx`, `kind` (0/1/2), `named`.
- **Content statistic `chi`** (H30's orthogonalized placebo, re-timed to the ledger): pre statements = j's statements (chat + intentions) before `t_call` (P = mean of the last ≤ 5 within 60 min; basis = last ≤ 8 within 2 h); post = j's statements at or after `t_call` (Q = mean of the first ≤ 5 within 60 min). chi = Q·unit(P⊥û_m) − mean over 30 seeded same-class other-day placebo messages of Q·unit(P⊥û_p). Bot placebos are nudges naming the same agent when ≥ 10 exist (H30). The vectorized implementation is checked against `h30lib.content_scores` (`chi_orth`) on a sample with the same pool.
- **Reply bias diagnostic.** DQ2's candidate score adds +0.20 when B names A's author, which can only happen for agent authors. `rep_nf_risk` marks (m, j) rows where m (human or bot) would be j's top candidate under the score without that term but is not under the real score (from the full ledger pools in `candidates_ledger`); its rate bounds the bias against humans.
- **Regimes covered:** I and III (II has too few human messages); goal periods split only by day fixed effects (see exception below).

**Unit-of-analysis exception (named, per CLAUDE.md):** (d) too little data per unit. The premium is a within-day contrast between sender classes, and all estimators include a day fixed effect or day-block resampling, so within-period step changes (roster joins, room changes, all at day boundaries) are absorbed. Splitting #51 into its 12 `period_units` would leave < 100 human rows in most units. Per-period estimates are reported next to a random-effects pooled estimate per regime (partial pooling); periods are never pooled completely. #51 segment estimates (H29's five segments) are reported as a check.

## Observables
Per period (the estimand is always the ATT over human or bot rows):
- **O1 content premium π_con** (χ_con units, cosine in the whitened space): human − matched agent; bot − matched agent. Named and unnamed rows also reported separately.
- **O1b boundary premium:** H29's visibility jump (named like-for-like and unnamed like-for-like) for humans minus agents, with a joint day bootstrap; H29's `rd_kappa` is imported for the per-class jumps.
- **O2 reply premium π_rep** (probability).
- **O3 activity premium π_act** (active minutes in 30 min after the receiving call), on outcomes residualized on day and recipient fixed effects; strata add `pre15` and `k_new` bins (past-only).
- **O4 stance premium π_st** (soft P(supports) − P(opposes), aggregate only, among parent replies).
- **O5 naive contrast** (raw human − agent means) next to the matched premium: how much of the raw difference is salience.
- **O6 premium in units of the naming effect:** π / (matched named − unnamed agent effect).
- **O7 robustness:** gte-modernbert content; style-residualized recipient statements; excluding `uncertain` ledger rows; regression adjustment; including goal kickoffs.

**Estimator (pre-registered; synthetic validation decides between two):**
- **CEM (coarsened exact matching):** strata = named (2) × read-out age (0–30 s, 30–120 s, 2–10 min, 10–30 min, > 30 min) × novelty (none, within-period terciles) × length (within-period quartiles of log characters) × recipient state (idle/active) × room size (1–3, 4–7, 8–15, ≥ 16); activity adds `pre15` (0, 1–5, 6–10, 11–15) × `k_new` (1, 2–3, 4–7, ≥ 8). π = Σ_s n_h,s (Ȳ_h,s − Ȳ_a,s) / Σ_s n_h,s over strata with ≥ 1 agent row; unmatched human rows are counted and dropped.
- **Regression adjustment:** OLS of Y on class × named indicators plus all covariate bins as main effects, a day fixed effect and a recipient fixed effect.
- **Uncertainty:** day-block bootstrap (1000 draws) in periods with ≥ 6 days carrying the class; message-cluster bootstrap otherwise (both classes resampled by message), labelled low power.
- **Primary rule:** the estimator with the lower RMSE over the synthetic null and planted-premium scenarios is primary; ties (relative difference < 10%) go to CEM.
- **Goal kickoffs** are excluded from the primary analysis (a kickoff is a step field on everyone with no agent analog of its length; H39 and H54 treat it as its own lever); included as a sensitivity.

## Null / baseline
- **N1 matched agent messages:** the comparison itself (H52's null is π = 0 against them).
- **N2 placebo class:** agent rows drawn to reproduce the human rows' stratum counts are relabelled "human" and the premium is recomputed against the remaining agent rows (200 draws): the null distribution of π under within-period dependence; its 95% band gives the size check.
- **N3 same-class placebo** inside χ_con (other-day messages of the same class), as in H30; **N3b** H29's truly-invisible placebo in the boundary design.
- **N4 synthetic:** agents on the real read-out schedule with planted π = 0 and π > 0 and realistic confounders (below).

## Eligible periods and native tests
**Replication** (non-holdout goal periods with ≥ 100 non-kickoff human (m, j) rows on ≥ 3 days with human messages): G03, G04, G05, G06, G08, G10, G12, G13, G16, G17, G18, G20, G23, G30, G38, G44, G51 (17). **Powered** (pre-registered): ≥ 300 matched human content rows and ≥ 6 days with human messages; expected G04, G06, G51 (G05 has 5 days and 1,090 human messages: reported as powered-by-messages with the message-cluster bootstrap). Bot class: every period with nudges (G30–G44 and G51 before 08-21).

| Test | Folder | Leverage | Observable |
| --- | --- | --- | --- |
| N1 within-call contrast | `G04` (native) | Regime-I public chat: 2,495 receiving calls contain both a human and an agent message, so timing, recipient, state and room are identical by construction | paired difference in content pull toward the human vs the agent message of the same call (adjusted for novelty, length, recency rank); reply choice between them (conditional logit) |
| N2 role conflict + bot | `G51` (native) | #51 private roles (DQ6 `role`, `goals.parquet` agent-goal vectors): a message aligned with the recipient's role vs one that pulls away from it (conflicts with its plan) | premium in off-role vs on-role messages; bot (leading @) as a third class |
| N3 nudger stop | `NE43` (native) | the bot falls silent after 2026-08-20 (pause/resume bookends after 08-05) | human premium before vs after (difference in differences against agent messages); bot premium in the before window |
| N4 authority without humanness | `G35`, `G44` (native), `G26` (native, descriptive) | operator-appointed agent leaders (#35 lead designers per day; #44 temporary fine-tuned leader) and an elected leader (#26) | leader premium: leader-sent vs matched other-agent messages, next to the human premium |

Not testable in round 1: "direct human instructions that conflict with the agents' plan" from DQ6 operator-intervention rows. DQ6 has operator room assignments (compliance median 1.00, scaffold-assisted) and one role reassignment (NE38), not a set of conflicting instructions; N2's off-role contrast is the closest available design.

**Holdout** (locked; `analysis/confirm.py` only): #45 (Fine-Tuned Leader: N4's confirmation), #46–#50 (human messages), #51 tail. Reuse disclosure: #45 was used by H02 (activity timing) and H23 (leader message wording planned); #46–#50 by H04 (nudge activity); the #51 tail is targeted by unrun scripts of H12, H13, H22, H29, H30 and H39 (content and nudge statistics). H52's statistic (sender-class premium matched on salience) has been computed by none of them.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R1 deference (π > 0), R2 discount (π < 0), R3 salience-only (H52); bot B1/B2/B3.
**Locked holdout used for confirmation:** none yet (`analysis/confirm.py` targets #45, #46–#50, #51 tail; not run).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Every row is a context-ledger item (DQ1 visibility), with DQ2 reply labels, DQ5 embeddings and DQ6 roles and leaders; no text written. Not invariant: "human" means public viewers in regime I and mostly staff in regime III; the content statistic's naming effect changes sign with the statistic (reply-quoting regression to the mean); speech acts (requests, questions) are not controlled |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Read-out gate (H08) built in; additivity within strata; co-arrival spillover and shared topic audited in synthetic. Stationarity checked over the five #51 segments (content stable, reply not). No Markov audit |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Reply premium beats the matched-agent null (pooled CI > 0; 8/17 periods), content in G51 (day-block CI > 0 under every statistic). The placebo-class null is anti-conservative (S3 failed); no held-out-day prediction |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | The H29 boundary design, an independent statistic, agrees in sign (6/6 estimable periods, CI > 0 in 3). The role-conditional reply premium (N2) came out as expected. P8 failed for the primary content statistic (negative naming effect) |
| E interventional | predicts the change across a natural experiment | 1 | NE43: content and activity premia unchanged as predicted; the reply premium dropped (2.3 SE, 16 messages after), against the prediction |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Synthetic on the real read-out schedules: reply, activity (bias-corrected) and stance recovered with coverage ≥ 0.8. Content recovered in the regime-III cell only (regime-I bias −0.024). H30's orthogonalized χ rejected (bias −0.02 to −0.03). Robust to the second embedding model, style residualization, uncertain ledger rows, clean controls and kickoffs |
| G ground truth | agrees with known structure | 1 | Agents' naming effect on replies (+0.13, 17/17 positive) and H29's 5.4× named/unnamed content ratio in G51 reproduced. DQ6 roles and leader labels used for N2/N4. No ground truth for deference itself |
| H comparative | beats the named rivals | 1 | R3 (salience-only, H52) rejected for replies (pooled) and G51 content. R1 deference in its strong form (premium off-role ≥ on-role) rejected. R2 (discount) rejected (no negative premium with CI below 0 in replies). Bot: B2 (like an agent) beats B1 and B3 except for stance |
| I transfer | holds in other same-mode periods, including the holdout | 1 | Reply premium positive across eras (regime I pooled +0.032; regime III +0.025, wide CI); content positive in all #51 segments; leader reply premium in two leader periods. Holdout not run |

## Prediction
*Written 2026-10-04 ~06:10 UTC, before running any outcome statistic on real data.*

**What I had seen.** Round-1 results of H08, H29, H30, H35, H37, H39 and DQ1/DQ2 (cards and LOG). Structural counts only: ledger items by period and sender kind; the share of items naming the recipient (humans name the recipient *less* often than agents in most periods, e.g. G04 5% vs 19%, G51 4.3% vs 4.4%); read-out age quantiles by class (similar in regime I, e.g. G04 median 12 s for both; humans read later in G38/G44, medians 41–49 s vs 18–22 s); idle-state shares; receiving calls containing both a human and an agent item; human messages per period and kickoff counts. No content, reply, activity or stance outcome had been computed.

**Decision rules.** Per period: "premium" if the 95% CI excludes 0; "equivalent" if the CI lies inside ±δ; otherwise "inconclusive". Margins δ: content 0.5 × the pooled matched agent naming effect (named − unnamed χ_con); reply 0.5 × the pooled agent naming effect on `rep`; activity 0.5 min; stance 0.05. Pooled = random-effects (DerSimonian–Laird) over replication periods within a regime. With 17 periods × 4 outcomes × 3 classes, single-period hits are expected by chance; only powered periods and pooled estimates carry weight.

**Synthetic (axis F, run first).**

| # | Prediction | Counts against |
| --- | --- | --- |
| S1 | With π = 0 and confounders (humans name more, post more novel and longer content, are read at different ages and more often by idle recipients), the naive contrast is biased beyond 2 SE in ≥ 80% of replicates, and the CEM 95% CI covers 0 in ≥ 90% | CEM coverage < 80% |
| S2 | With a planted premium (content +0.03, reply +0.05, activity +1.0 min, stance +0.10), CEM recovers it with median relative error ≤ 30% and CI excluding 0 in ≥ 80% of replicates at G51 and G04 sampling | median error > 50% |
| S3 | The placebo-class null (N2) rejects at ≤ 7% | > 15% |
| S4 | Primary estimator chosen by RMSE (CEM vs regression adjustment) | |

**Real data: replication layer (templated across periods).**

| # | Prediction | Counts against |
| --- | --- | --- |
| P1 | **Content (H52's core):** H52 predicts the pooled π_con equivalent to 0 (CI inside ±δ). *My expectation (credence 0.55):* π_con > 0 in regime III (operator messages; CI > 0 in G51) and ≤ 0 in regime I (public viewers; pooled CI includes or is below 0), i.e. the sign depends on who the humans are | For H52: a pooled CI outside ±δ in either regime, or CI > 0 in ≥ half the powered periods |
| P2 | **Reply:** π_rep > 0 (agents answer humans more often than matched agent messages) with CI > 0 in ≥ half the powered periods (credence 0.65). The candidate rule biases against humans, so this is conservative | π_rep ≤ 0 in all powered periods (then H52 holds for replies) |
| P3 | **Activity:** π_act equivalent to 0 or inconclusive (CI includes 0) in ≥ 2/3 of periods (H30: human messages do not move activity) | CI > 0.5 min in ≥ 2 powered periods |
| P4 | **Stance:** pooled π_st > 0 (more support, fewer "opposes" toward humans), ≥ +0.05 (credence 0.5; Jev knows the sender is human, so labeller bias is possible) | pooled π_st ≤ 0 with CI excluding +0.05 |
| P5 | **Bot = neither (B3):** in G51 (07-06 → 08-20) and pooled G30–G44: π_act(bot, named) > 0 (≈ 0.5–1.5 min, H30), π_con(bot) ≤ 0, π_rep(bot) < 0 | bot content or reply premium ≥ the human premium with CI excluding 0 (then B1) |
| P6 | **Salience matters:** the naive human − agent contrast differs from the matched premium by more than its own bootstrap SE in ≥ half the powered periods | naive ≈ matched everywhere (then matching was unnecessary) |
| P7 | **Boundary design (H29):** per-class visibility jumps estimable for agents; the human − agent jump difference has a CI including 0 in every unit (underpowered; report only) | |
| P8 | **Naming effect replicates:** matched named − unnamed agent χ_con > 0 in ≥ 2/3 of periods (H29/H30) | ≤ 1/3 (then the salience model itself is in doubt) |

**Real data: native layer** (each period README repeats its own prediction).
- **N1 (G04 within-call):** among receiving calls with both a human and an agent message of the same named status, the recipient's content pull toward the human message minus toward the agent message (regression-adjusted for novelty, length and recency rank) is ≤ 0: in public chat, agents' work follows agents (credence 0.6). In the same calls, the reply choice favours the human message (adjusted odds > 1; credence 0.55): *humans get answers, not influence*. H52 predicts both contrasts ≈ 0. Counts against my expectation: content difference > 0 with CI excluding 0.
- **N2 (G51 roles):** among messages to recipients with a #51 role, split at the period median of cos(û_m, recipient's role vector): R1 deference predicts π_con(off-role) ≥ π_con(on-role) > 0; H52 predicts both ≈ 0. *My expectation (credence 0.4):* π_con(on-role) > π_con(off-role) ≈ 0 (agents follow humans when it fits their plan). Bot: P5.
- **N3 (NE43):** the human premium (content, reply, activity) does not change across the 08-21 nudger stop: |Δπ| < 2 × its SE (H52 and R1 both predict no change; an attention-competition reading predicts a larger human activity premium once nudges stop). Bot premium estimable only before.
- **N4 (G35, G44; G26 descriptive):** messages from operator-appointed or elected agent leaders get no premium over matched other-agent messages (CI includes 0; credence 0.6), while human messages in the same periods have π ≥ the leader's π. Counts against: leader π_con or π_rep > 0 with CI excluding 0 in both G35 and G44 (authority by role, not by species).

**What would count against H52 overall:** a positive (or negative) premium in content or replies whose pooled CI excludes ±δ and which appears in ≥ half the powered periods. H52 is **supported** if content and activity premia are equivalent to 0 in the pooled estimates and in ≥ 2/3 of powered periods; **failed** if the content or reply premium is outside ±δ with CI in pooled and in ≥ half the powered periods; **mixed** otherwise.

### Synthetic validation (axis F; done 2026-10-04 before any real-data outcome)
`analysis/synthetic.py` → `data/processed/H52-humans-loud-agents/synthetic/` (10 replicates per cell; skeletons G51 and G04 with their real read-out schedule, naming, ages, states, room sizes and statement availability; labels either the real human/bot rows or a **confounded** relabelling of agent messages selected on naming, recipient idleness, length and age; humans generated more novel; agent replies quote their addressee's last statement). Truth for content by common random numbers. Bias = estimate − truth (mean over replicates); cov = 95% CI coverage.

| Outcome / estimator | G51 real labels: null bias · planted bias (truth) · cov · power | G51 confounded | G04 real labels | G04 confounded |
| --- | --- | --- | --- | --- |
| content, H30 orthogonalized χ (card's original) | −0.019 · −0.018 (0.022) · 0.1/0.0 | −0.025 · −0.023 · 0.2/0.0 | −0.033 · −0.033 · 0.0/0.2 | −0.025 · −0.036 · 0.6/0.4 |
| content, DiD χ (A1), CEM | −0.006 · −0.003 (0.022) · 1.0/0.9 · 0.8 | −0.006 · −0.006 · 0.8/1.0 · 0.4 | **−0.024 · −0.022 (0.024)** · 0.1/0.4 · 0.1 | +0.003 · −0.003 · 1.0/0.7 · 0.1 |
| reply, CEM | 0.000 · 0.000 (0.027) · 0.9/0.8 · 1.0 | +0.003 · −0.002 · 1.0/0.9 · 0.9 | −0.004 · −0.006 (0.043) · 0.8/0.7 · 0.9 | −0.004 · −0.029 (0.061) · 0.9/0.7 · 0.6 |
| activity, CEM raw | −0.50 · −0.68 (1.0) | −0.12 · −0.24 | +0.12 · −0.05 | +0.79 · +0.82 |
| activity, bias-corrected CEM (A1) | −0.11 · −0.18 · 0.9/0.8 · 1.0 | −0.06 · −0.23 · 0.8/0.1 · 1.0 | +0.04 · −0.04 · 1.0/1.0 · 1.0 | +0.06 · +0.10 · 1.0/1.0 · 1.0 |
| stance, CEM (coarse strata) | +0.002 · −0.013 (0.10) · 1.0/1.0 · 0.8 | +0.001 · +0.014 · 1.0/1.0 · 1.0 | +0.002 · −0.019 · 0.9/0.7 · 1.0 | −0.058 · −0.018 · 0.9/0.9 · 0.4 |
| naive contrast, content (DiD) | −0.016 · −0.014 | −0.023 · −0.022 | +0.020 · +0.018 | −0.017 · −0.018 |
| bot content (DiD), truth 0 | −0.024 | −0.024 | (no bot) | (no bot) |

- **S1 partly passed.** The naive content contrast is off by more than 2 SE in 50–100% of replicates; the naive activity contrast in 0–100%, reply in 10–100%, depending on the cell. Matched estimators cover 0 at ≥ 0.8 except the two failures below.
- **S2 passed for reply, activity (bias-corrected) and stance; content only in the G51-like regime-III cell.** Content power at +0.022 is 0.4–0.8 in regime III. In dense regime-I chat with real labels, the DiD premium is biased by about −0.024, so a true premium of that size reads as 0. Cause: human (viewer) messages arrive in bursts and are less topical; topical agent messages gain alignment from co-arriving agent messages that move the shared post-call statement (co-arrival spillover).
- **S3 failed:** the placebo-class null (N2) rejects in 10–20% of null replicates (anti-conservative: it ignores that one human message reaches many recipients). It is reported only descriptively; inference uses the cluster bootstrap.
- **S4:** CEM beats regression adjustment in the quick runs (regression bias up to −0.03 in content), so CEM is primary (tie rule); for activity the bias-corrected CEM has the lowest RMSE in every cell.
- **The H30 orthogonalized χ_con is biased by shared topic** (null bias −0.019 to −0.033, coverage ≤ 0.6): the recipient's next statement shares the room's current topic, which a basis of ≤ 8 noisy recent statements removes only partly, so less topical senders look less influential. This also means H30's absolute χ_con levels partly measure same-day topic sharing (suggested note for H30).
- **The bot's content premium is not identifiable:** templated nudges share no topic with co-arriving messages, giving −0.024 at zero truth.

### Amendment A1 (synthetic-based; written 2026-10-04 ~09:30 UTC, before any real-data outcome statistic)
1. **Content statistic:** primary = **DiD χ** (`chi_dd`): (Q − P_last)·û⊥′ minus the same for 30 same-class other-day placebos, with û⊥′ orthogonal to the recipient's older recent statements (all but the most recent) and P_last = its last statement before the receiving call. H30's orthogonalized χ is reported for comparability only. Sensitivities: gte-modernbert, style-residualized recipient statements, and a **joint per-call deconvolution** (`chi_jd`, ridge regression of the shared displacement on all co-arriving messages; quick synthetic on G04 real labels: bias +0.004 null and planted, but +0.04 under strong naming selection with reply-quoting).
2. **Bias bounds used in verdicts:** regime-III content premium null bias −0.006; regime-I content premium null bias up to −0.024 (negative regime-I content premia down to about −0.024 are consistent with no premium; positive ones are conservative); bot content premium not interpreted unless below −0.024.
3. **Room size** = recipients + 1 for agent senders (a human or bot message reaches everyone present; an agent message everyone but its author). The first draft compared 3 with 4 in regime I and matched 10% of human rows.
4. **Controls:** all agent rows (primary); "clean" controls (agent rows at calls without any human or bot item) as a sensitivity; they are selected on `k_new` where humans are a large share of items.
5. **Activity:** bias-corrected CEM (outcome residualized on log age, novelty, log length, log room size, named, idle, `pre15`, log `k_new`, since-active bins, and day and recipient fixed effects, fitted on agent rows), with finer `pre15` (6) and `k_new` (9) bins.
6. **Reply sample:** rows whose recipient posted ≥ 1 chat message in the 60 min after the receiving call (`n_chat_post ≥ 1`); otherwise a reply is impossible by construction.
7. **Stance strata:** coarse (named × age × room size), since replies are few.
8. **Placebo-class null:** descriptive only (S3 failed).
Predictions P1–P8 and N1–N4 are unchanged; the content verdicts use the bias bounds in item 2.

## Results by goal period
Verdict rule (replication folders, from the human premia): **failed** (for H52) if the content or reply premium's CI lies beyond its margin; **supported** if content is equivalent to 0 and activity equivalent or inconclusive; **descriptive** if not powered and every CI includes 0; **mixed** otherwise. Native folders state their own rule. Key numbers: human − matched agent premium [95% CI] (content DiD χ; reply probability; activity min / 30 min, bias-corrected; stance soft). Powered: G04, G06, G51.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G03](goalperiod-subhypotheses/G03/README.md) | replication | mixed | content 0.025 [-0.001, 0.056]; reply 0.050 [0.012, 0.090]; activity -0.58 [-1.28, 0.28]; stance 0.06 [-0.14, 0.25] |
| [G04](goalperiod-subhypotheses/G04/README.md) | native | mixed | N1 within-call: content adj. −0.006 [−0.024, 0.014], reply odds 1.49 [0.88, 2.79]; replication: content 0.012 [-0.001, 0.024] (boundary +0.052 [0.027, 0.074]); reply 0.025 [0.001, 0.047]; activity 0.17 [-0.44, 0.74]; stance 0.07 [0.00, 0.13] |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | mixed | content 0.001 [-0.024, 0.036]; reply 0.030 [0.020, 0.039]; activity -0.27 [-0.52, 0.08]; stance 0.05 [-0.06, 0.18] |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | mixed | content 0.003 [-0.009, 0.027]; reply 0.009 [-0.002, 0.040]; activity 0.19 [-0.58, 0.57]; stance 0.27 [0.11, 0.48] |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | mixed | content 0.022 [-0.003, 0.039]; reply 0.036 [-0.012, 0.078]; activity 0.34 [-0.80, 1.42]; stance 0.29 [0.12, 0.45] |
| [G10](goalperiod-subhypotheses/G10/README.md) | replication | descriptive | content -0.022 [-0.050, 0.004]; reply 0.020 [-0.009, 0.054]; activity 0.15 [-0.98, 2.01]; stance 0.15 [-0.20, 0.51] |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication | mixed | content 0.039 [0.003, 0.072]; reply 0.023 [-0.006, 0.056]; activity -1.00 [-1.78, -0.22]; stance — |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | mixed | content 0.023 [-0.012, 0.052]; reply 0.081 [0.046, 0.155]; activity -0.41 [-0.94, 0.16]; stance 0.32 [0.26, 0.42] |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | mixed | content -0.013 [-0.037, 0.007]; reply 0.094 [0.030, 0.146]; activity 1.72 [0.61, 3.13]; stance 0.17 [0.05, 0.34] |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | mixed | content 0.000 [-0.033, 0.048]; reply 0.097 [0.047, 0.157]; activity -0.10 [-1.72, 1.27]; stance -0.13 [-0.55, 0.20] |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | descriptive | content -0.061 [-0.093, 0.015]; reply 0.061 [-0.003, 0.181]; activity 1.22 [-0.50, 2.77]; stance 0.15 [-0.12, 0.36] |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | mixed | content -0.028 [-0.076, -0.006]; reply 0.085 [-0.012, 0.237]; activity -0.43 [-1.28, 0.36]; stance 0.23 [0.10, 0.33] |
| [G23](goalperiod-subhypotheses/G23/README.md) | replication | mixed | content 0.001 [-0.044, 0.043]; reply 0.010 [-0.013, 0.035]; activity -0.22 [-0.78, 0.49]; stance 0.40 [0.15, 0.59] |
| [G26](goalperiod-subhypotheses/G26/README.md) | native | descriptive | elected leader: reply +0.028 [0.008, 0.050]; content −0.007 [−0.018, 0.007]; activity −1.40 [−2.03, −0.78] |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | mixed | content 0.030 [-0.010, 0.074]; reply 0.026 [-0.009, 0.061]; activity 0.07 [-0.48, 0.63]; stance 0.29 [0.03, 0.54] |
| [G35](goalperiod-subhypotheses/G35/README.md) | native | mixed | lead designers: reply +0.029 [0.011, 0.053]; content −0.012 [−0.027, 0.005]; activity −0.22 [−0.44, 0.04] |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | mixed | content 0.026 [-0.003, 0.057]; reply 0.128 [0.017, 0.248]; activity 0.83 [-0.17, 2.14]; stance 0.01 [-0.11, 0.21] |
| [G44](goalperiod-subhypotheses/G44/README.md) | native | mixed | fine-tuned leader: content +0.007 [−0.036, 0.058], reply −0.054 [−0.137, 0.042]; humans: content 0.021 [-0.013, 0.052]; reply -0.027 [-0.078, 0.016] |
| [G51](goalperiod-subhypotheses/G51/README.md) | native | mixed | content 0.014 [0.008, 0.021]; reply 0.029 [0.008, 0.052]; activity 0.36 [-0.07, 0.72]; stance 0.08 [-0.07, 0.27]; N2 reply on-role +0.037 vs off-role +0.007 (difference +0.035 [0.012, 0.062]); bot stance −0.97 |
| [NE43](goalperiod-subhypotheses/NE43/README.md) | native | mixed | after − before: content +0.003 [−0.016, 0.023]; reply −0.039 [−0.072, −0.005]; activity −0.41 [−1.11, 0.30] |

## Results
Scripts (all in `analysis/`): `h52lib.py` (loaders, vectorized content statistic, CEM, bootstrap, pooling), `estimate.py` (the one estimation core used on synthetic and real frames), `synthetic.py`, `verify_chi.py`, `run_period.py` (replication layer), `native.py` (N1–N4), `segments.py` (#51 segments), `summarize.py`, `write_period_folders.py`, `figures.py`, `confirm.py`. Scheme: `scheme/build.py`. Outputs in `data/processed/H52-humans-loud-agents/` (`<period>/results.json`, `summary.json`, `period_table.parquet`, `native/*.json`, `synthetic/`, `checks/`, `confirm_dryrun/`). Figures: `figures/h52_obs.pdf` (all periods), `figures/h52_obs_compact.pdf` (key contrasts), `figures/h52_synth.pdf`.

**Read-only imports:** `hypotheses/H30-operator-susceptibility/analysis/h30lib.py` (`content_scores`, used in `verify_chi.py`: H52's vectorized χ equals H30's `chi_orth` to 1.4e-8 where the recent-statement basis is independent); `hypotheses/H29-driver-nodes/analysis/h29lib.py` (`rd_kappa`, per-class boundary jumps; `run_period.rd_diff` replicates its estimator for a joint-bootstrap difference). H35's leading-@ rule and H30's orthogonalization and placebo pool were re-implemented (not imported) and checked.

### Outcome vs prediction
| # | Predicted | Observed | Verdict |
| --- | --- | --- | --- |
| S1 | naive biased; CEM covers 0 ≥ 90% | naive off by > 2 SE in 50–100% of cells (content); CEM coverage ≥ 0.8 except H30 χ and regime-I DiD content | partly passed |
| S2 | planted premium recovered (≤ 30% error, power ≥ 0.8) | reply, activity (BC), stance yes; content only in the regime-III cell (power 0.4–0.8) | partly passed |
| S3 | placebo-class null size ≤ 7% | 10–20% | failed (null made descriptive) |
| P1 | H52: content equivalent to 0 (margin 0.0073); expectation: > 0 in III, ≤ 0 in I | regime III pooled +0.015 [0.008, 0.021] (G51 beyond the margin; 5 statistics; 5/5 segments); regime I pooled DiD +0.005 [−0.005, 0.016] (bias −0.024), boundary design +0.05/+0.09 (G04, G05) | **H52 fails in III**; expectation half right (I is ≥ 0, not ≤ 0) |
| P2 | reply premium > 0 in ≥ half the powered periods | G04 +0.025 ✓, G51 +0.029 ✓, G06 +0.009 (n.s.); pooled +0.030 [0.019, 0.042]; 8/17 periods CI > 0, 0 below | **supported** (inside the H52 margin 0.064: a real but sub-naming effect) |
| P3 | activity CI includes 0 in ≥ 2/3 of periods | 15/17 | supported |
| P4 | pooled stance premium ≥ +0.05 | +0.16 [0.10, 0.23] (regime I +0.19; III +0.06 n.s.) | supported (labeller knew the author was human) |
| P5 | bot = neither (activity > 0, content ≤ 0, reply < 0 vs matched agents) | activity named −0.11 (G51), pooled +0.19 [−0.66, 1.05]; reply pooled −0.014 [−0.029, 0.001]; content not identifiable; stance −0.97 (G51) | **failed**: like a matched agent message except that replies push back (B2 with a stance twist) |
| P6 | naive ≠ matched beyond SE in ≥ half the powered periods | reply in G04 and G06 (sign flips from −0.03/−0.02 to +0.025/+0.009); content, activity, stance no | partly (1 of 4 outcomes) |
| P7 | boundary human − agent jump CI includes 0 everywhere | CI > 0 in G04, G05, G13; includes 0 in G03, G06, G51 | failed (better powered than expected; corroborates P1) |
| P8 | agent naming effect > 0 on content in ≥ 2/3 of periods | DiD χ: negative in 15/17 (pooled −0.015); H30 χ: pooled −0.001; boundary: G51 5.4×; replies +0.13 (17/17) | failed for the content statistic (reply-quoting regression to the mean); holds for replies and on the boundary |
| N1 | G04 within call: content ≤ 0; reply odds > 1 | content adj. −0.006 [−0.024, 0.014]; odds 1.49 [0.88, 2.79] | inconclusive both (directions as expected) |
| N2 | expectation: on-role > off-role ≈ 0 (R1: off ≥ on > 0) | reply +0.037 vs +0.007 (difference +0.035 [0.012, 0.062]); content +0.014 vs +0.011 | supported for replies; R1 rejected |
| N3 | NE43: no change in the human premium | content, activity unchanged; reply −0.039 [−0.072, −0.005] | mixed |
| N4 | agent leaders: no premium | reply +0.028 (G26), +0.029 (G35) CI > 0; content n.s.; G44 none | failed for replies in 2/3 leader periods |

### Synthesis
1. **Replies carry the premium; content barely does; activity does not.** Given the same salience, an agent is about twice as likely to answer a human message as an agent message (+0.03 absolute; the naming effect is +0.13). It moves a little further toward what the human adds (+0.014 in G51; ≈ half the naming effect on H30's scale). Activity is unmoved, consistent with H30 and with H04's human kernel losing significance on the corrected activity table (RE-V1, coordinator note).
2. **Salience explains much of the *raw* human effect in regime I, in the opposite direction from HH164's picture.** Viewers name agents less often than agents name each other (5% vs 19% of items in G04), so the naive reply contrast is negative (−0.03). Matching on naming reveals a positive premium. Humans are "quiet" agents in salience terms, and get a premium on top.
3. **The premium is plan-congruent, not deference against the plan.** In #51, the reply premium exists only for messages aligned with the recipient's private role and is ≈ 0 for the most role-conflicting third. An alignment reading: in this swarm, human authority does not override an agent's assigned objective; it adds weight to inputs that already fit.
4. **Authority by role, not species.** Agents elected (G26) or appointed (G35) as leaders are answered more, by the same +0.03, with no content premium. A weak fine-tuned leader is not (G44). So the reply premium looks like deference to a *status* that humans and designated leaders share.
5. **The bot is treated as a rebuffed agent:** given read-out and salience, nudges get the same content uptake, replies and target activity as agent messages (H30's nudge effect is relative to no message), and the few replies to it are oppositional (declines and corrections; aggregate only).
6. **Methodological findings for the project:** (a) H30's orthogonalized χ_con is biased by shared room topic (synthetic −0.02 to −0.03): absolute χ_con levels partly measure topic sharing; comparisons between sender classes with different topicality need a DiD or boundary statistic. (b) h30lib's QR basis drops part of the span when recent statements repeat exactly (16 of 150 G44 rows); an SVD basis fixes it. (c) In dense chat, co-arriving messages share one post-call statement, which spreads a message's pull onto its neighbours (within-call contrasts attenuate). (d) The DQ2 candidate rule's +0.20 bonus for naming the author biases reply detection against humans and bots; it affects ≤ 3% of human rows (median ~1%), so it is negligible here.

### Caveats
- **What "human" means changes across eras** (public viewers in regime I, mostly staff in regime III). Humans are anonymized; no per-human analysis was done. Speech acts differ (humans ask and instruct), so the premium bounds "deference to humans *or* to the kind of thing humans say". N2 and N4 separate part of this.
- **Content is fragile.** The primary DiD statistic has a negative naming effect (replies quote their addressee, so the recipient moves away relative to its last statement) and a −0.024 null bias in dense regime-I chat; H30's statistic has a shared-topic bias. The G51 content premium is positive under all five statistics with opposite known biases, which is the basis for the claim; regime-I content rests on the boundary design (G04, G05, G13).
- **Power.** Only G04, G06 and G51 are powered; regime-III periods other than G51 have 4–28 human messages. NE43's "after" window has 16 human messages. 17 periods × 4 outcomes × 2 classes plus 4 native tests: single-period hits are expected by chance; pooled estimates and the G51 + G04 agreement carry the weight.
- **Labeller knowledge.** Jev was told when an author was "a human viewer" or "the village's automated system"; reply and stance premia may partly reflect the labeller. Stance is aggregate-only (κ 0.44).
- **Exception (d):** goal periods were not split at roster or room steps (day fixed effects); the #51 segment check agrees for content, not for replies (51d negative).
- **Day-block bootstrap needs ≥ 6 days**; 11 periods used message clusters (low power, no day-shock protection).

### Confirmatory predictions (C-*), frozen 2026-10-04 ~11:30 UTC after round 1; `analysis/confirm.py`, not run
Guards: refuses without `--confirm --i-understand-this-uses-the-locked-holdout` and with uncommitted changes in the H52 folder. Reuse disclosures as in "Eligible periods" above. Overall: supported if every testable primary passes; failed if none; else mixed.

| ID | Target | Statement | Primary |
| --- | --- | --- | --- |
| C1 | #51 tail | human content premium (DiD χ) > 0, CI excluding 0 | yes |
| C2 | #51 tail | human reply premium > 0, CI excluding 0 (credence 0.45: decides whether the NE43 drop was noise) | yes |
| C3 | #46–#50 pooled | human reply premium > 0, CI excluding 0 | yes |
| C4 | #46–#50 pooled | human content premium > 0 (point) | no |
| C5 | #51 tail | human activity premium CI includes 0 | no |
| C6, C7 | #45 | Fine-Tuned Leader reply and content premia CIs include 0 | no |
| C8 | #46–#50 pooled | stance premium toward humans > 0 (point) | no |

Dry run on stand-ins (G51 08-24 → 09-04 for the tail; G38/G41/G42 for #46–#50; G44 with agent 28 for #45; not evidence): C1 +0.018 [−0.007, 0.036] fail, C2 −0.001 fail, C3 +0.046 [−0.010, 0.102] fail, C4 fail, C5–C8 pass. Power for C1 and C3 is marginal with ~2 weeks or ~5 small periods; the stand-ins are the low-power end.

## Round 2 redirects
**What the direction is really after:** whether agents weigh human input above peers' at equal salience, and whether it overrides their plan.
- **H52-R1. Speech-act matching.** Label messages as request / question / instruction / information (Jev, a few dollars) and match on speech act; the premium may be deference to requests, not to humans.
- **H52-R2. Separate the labeller from the agents.** Rerun the reply and stance labels blind to sender class (author shown as "a participant") on a sample of human and matched agent pairs, to bound the labeller's share of the reply and stance premia.
- **H52-R3. Role conflict with ground truth.** Hand-code a few dozen #51 human instructions that contradict a recipient's role or current task and track compliance (actions, commits from the DQ4 work ledger), comparing with agent requests of the same kind.
- **H52-R4. A cleaner content statistic.** A DiD with the reply-quoting component removed (exclude the recipient's own last statement from the message direction), validated on the synthetic world; then recompute the content premium and the agent naming effect.
- **H52-R5. Run `confirm.py`** after committing (#51 tail; #45 leader).

## Notes
- 2026-10-04: promoted from HH164 by Vivian (wave B).
- 2026-10-04 ~06:10 UTC: round-1 agent started; design, nulls and predictions written before any outcome statistic.
- 2026-10-04 ~09:30 UTC: synthetic validation done; Amendment A1 (DiD content statistic, room size, bias-corrected activity, reply eligibility, coarse stance strata, placebo-class null descriptive), before any real-data outcome.
- 2026-10-04: real-data runs (17 replication periods + G26/G31/G33/G35–G37/G39–G42 for bot and leader classes; native N1–N4; #51 segments). Interrupted once by an API session limit after all computations had finished; the card and summary were completed on resume.
- 2026-10-04: activity uses `activity_bins_fixed` throughout (the coordinator's data-bug notice on `activity_bins` does not affect H52); `outages` not used. Coordinator note RE-V1: H04's mentioned-human activity kernel is n.s. on corrected data, consistent with P3.
- Compute: local, ≤ 2 threads per process, ≤ 2 processes. Synthetic suite ≈ 46 min; real-data pass ≈ 40 min. Disk: `data/processed/H52-humans-loud-agents/` ≈ 104 MB (22 MB of it the confirm dry run).
- **Proposed shared changes** (not made; outside H52's edit scope): DEFINITIONS.md variants *sender class*, *salience covariates*, *authority premium π* (CEM ATT vs matched agent messages), *content pull (DiD χ)*; infra/README Known issues: (1) H30's orthogonalized χ_con is biased by shared room topic when sender classes differ in topicality; (2) `h30lib._orth_basis` drops part of the span when recent statements repeat exactly (use an SVD basis); (3) DQ2's +0.20 author-naming bonus cannot apply to human or bot authors (bias ≤ 3% of rows); (4) co-arriving messages share one post-call statement (within-call contrasts attenuate); H30 card note on (1)–(2).
