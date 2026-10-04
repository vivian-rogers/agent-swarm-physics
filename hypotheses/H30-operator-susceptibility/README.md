# H30: An operator-susceptibility gauge χ_op: how steerable is the swarm today?

**Status:** exploratory round 1 done (2026-10-03; 16 non-holdout goal periods; holdout not run). **A period-level χ_op exists in both channels, but the daily gauge is not stable enough to act on.**
- **Nudges move the targeted agent's activity**, modestly: in G51 (875 nudges), χ_act = 0.59 [0.24, 0.93] extra active minutes in the next 30 min (pre-registered model), 1.04 [0.77, 1.33] with a day fixed effect. The first nudge of an episode gives 1.36 [0.98, 1.75]; repeat nudges give 0.26 [−0.13, 0.63]. Bystanders show ≈ 0. Elsewhere the activity response is unresolved.
- **Human messages move content, not activity:** recipients' next statements turn toward the message's new content, χ_con = 0.026 [0.021, 0.030] (pooled undirected, 8 periods; 6 with CI > 0). Named agents move more: 0.046 [0.036, 0.057]. Activity response to human messages is ≈ 0 in every period.
- **No aging, no context sawtooth, no family effect.** Day-to-day variation is at most weak (G51 permutation p = 0.08, R₁ = 0.28) and does not persist (lag-1 −0.09). The daily gauge is a period constant plus noise.
- **H04's nudge A30 (1.5–1.7) is inflated** by its isolation rule, which conditions on the nudger *not* re-firing (52% of G51 nudges are re-fired within 60 min).

`confirm.py` is written and dry-run on stand-ins; **not run**.
- **Round 1b (improved data, 2026-10-04):** on the fixed activity bins, with the nudge's leading @ as its only target, kicks timed at the receiving call (DQ1 ledger) and past-only controls with a day fixed effect, **the nudge response roughly doubles and is now resolved in both large periods**: G51 0.98 [0.63, 1.37] (round 1: 0.59), G38 0.95 [0.38, 1.54] (round 1: −0.08); P1 passes. Most of the change is the event-drop fix (G51 0.59 → 1.29 with fixed bins alone). First nudges 1.21, repeats 0.44 [−0.19, 1.10]. **Round 1's "don't nudge into a swarm-wide lull" reverses** (lull 1.74 [0.94, 2.63] vs 0.72): it was an artifact of the dropped events. Human content steering is unchanged and holds under a second embedding model (0.024 room-mates, 0.041 named). The daily gauge now shows some day-to-day variation in G51 (permutation p 0.026, R₁ 0.48) but no persistence (lag-1 0.08): P6 fails as written, HH116's falsifier is still not met. Natives: #5 dilution failed by its rule (the first three dose bins fall 0.025 → 0.013, the 8+ bin is noisy), NE44 failed in reverse (nudges buy more under the 5-min pause default), NE10 failed (low power). Scorecard unchanged (A1 B1 C1 D1 E0 F1 G1 H1 I1).
**Fields:** stat mech, sociophysics, info theory
**Origin:** HH116 (`../hypohypotheses/HYPOHYPOTHESES.md`; `../promotion-shortlist.md`); HH117 (context sawtooth) and HH98 (family steerability) as sub-questions; HH52 (catalyst vs field) for reading the two channels.
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime; Population N(t) (active-population variant: ≥ 1 active minute that day); Driving / external field (human messages; automated nudges); Interaction (broadcast) for room recipients and Interaction (addressed) for named agents; Agent state (vector), whitened statement variant (per-regime whitening, n = 32). New operational terms (operator kick classes, activity susceptibility χ_act, content susceptibility χ_con, context fill) are defined below and proposed as named variants in the round-1 report (DEFINITIONS.md is not edited here).

## Question
How much does one operator or human message move the swarm, and does that number change from day to day in a way an operator could track? Two channels:
- **(a) activity:** extra active minutes of the targeted agent (and of the whole swarm, the collective activity mode) in the 30 min after a message;
- **(b) content:** movement of the recipients' statements toward the message's direction in embedding space, relative to a matched placebo message.

Sub-questions: does steerability fall as a goal ages, or as an agent's context fills (HH117)? Does it differ by regime, or by model family (HH98, optional)? Practical aim (usefulness-first batch): a daily number χ_op an operator can compute from logs, plus an honest statement of whether it is stable enough to act on.

## Model
**From:** `physics-models/01-inverse-ising` (susceptibility as response to a field) and `physics-models/11-vector-spins` (the message as a vector field h_k u_k; longitudinal response along it).

**H30 variant (linear response to impulsive fields).** Each operator message k is an impulse field on its recipients. For agent i with activity spin n_i(t) ∈ {0, 1} and content state s_i(t) ∈ S^31 (whitened statement vector):
- activity: E[n_i(t_k + τ) | kick] − E[n_i(t_k + τ) | no kick, same pre-history] = χ_act,i(d) R(τ), with Σ_{τ=1}^{30} R(τ) = 1, so χ_act is the time-integrated (A30) response in extra active minutes;
- content: E[s_i(t > t_k) · u_k] − E[s_i(t > t_k) · u_p] = χ_con,i(d), where u_p is a placebo direction matched on pre-kick alignment;
- the gauge is the day average χ_op(d) = ⟨χ⟩_{kicks on day d}, per message class.

HH116's hypothesis is that χ_op(d) is a slowly varying state of the swarm (falls with goal age, or with context fill). The null is a constant χ (all day-to-day variation is sampling noise) or χ = 0. H04's reading (a message couples to unread context and is read out at the next scheduled turn, ~4 min dead time, plateau by ~15 min) fixes the window τ = 1–30 min. HH52's reading: a nudge is a catalyst (raises activity, no content direction), a human message can be a field (content direction).

**Rivals.**
- **R0 no response:** χ = 0 (messages are read but ignored).
- **R1 constant susceptibility:** χ > 0 but the same every day; daily variation is noise. Then the daily gauge is useless and a period constant suffices.
- **R2 selection artifact:** the nudger fires on agents that have been idle a long time. If escape hazards age (H16), a pre-history match that is too short makes the post-kick activity look high or low regardless of any effect.
- **R3 engagement / common cause (H18):** a message and the recipient's later content share a topic because the conversation was already there (for nudges, the nudger writes the message *from* the agent's recent chat). Then alignment after the kick is regression or persistence, not steering.

## Definitions (operational; shared tables only)
- **Operator message classes** (from `chat_core` + `chat_mentions_clean.mentions_roster`; the polluted `chat_core.mentions` is never used):
  - `nudge` = automated message naming ≥ 1 agent on that day's roster; `bookend` = any other automated message (daily pause/resume), dropped;
  - `human` = speaker_kind human.
- **Kick classes** (one kick = one message × one recipient; recipients from `exposure`, plus named agents for nudges, as in H04):
  - `N_tgt` nudge to a named agent; `N_by` nudge seen by an unnamed room-mate;
  - `H_men` human message naming the agent; `H_und` human message in the agent's room not naming it.
- **Activity:** n_i(m) = 1 if `activity_bins.state` ∈ {3 act, 4 talk} in minute m of the day's window (H04 convention); idle = state 2; silent = state 1. The kick minute m_k = ⌊(t_k − win_start)/60⌋.
- **Activity susceptibility (local projection):** for every present agent-minute (i, m) with m ≥ 15 and m + 30 inside the window, Y_i(m) = Σ_{τ=1}^{30} n_i(m+τ) and
  Y_i(m) = α_{s(i,m)} + Σ_c χ_c K^c_i(m) + β_post K^post_i(m) + β_pre K^pre_i(m) + ε,
  where K^c = class-c kicks reaching i at minute m, K^post / K^pre = all kicks reaching i in [m+1, m+30] / [m−30, m−1] (overlap adjustment, needed where messages are dense), and the stratum s = agent × state(m−1) × active-minutes in [m−15, m−1] (4 bins) × idle-minutes in [m−15, m−1] (3 bins) × **minutes since the agent's last active minute** (0, 1–4, 5–14, 15–29, 30+, not yet active today) × day-third. Strata are absorbed by within-stratum demeaning (Frisch–Waugh–Lovell). The silent-run bin is added to H04's strata because of rival R2.
  - Per-kick contribution r_k = residual of Y at the kick cell after removing the fitted nuisance terms; **daily gauge χ_act^c(d) = weighted mean of r_k over class-c kicks on day d**, SE from the within-day spread.
  - Period estimate: the FWL coefficient, 95% CI from a day-block bootstrap.
- **Collective activity mode:** per message, χ_coll = Σ over its recipients of their responses = χ(N_tgt)·n_tgt + χ(N_by)·n_by for nudges, χ(H_men)·n_men + χ(H_und)·n_und for humans (per day). H12 found one Curie–Weiss-like collective mode with near-uniform loadings, so the summed response is its projection.
- **Content susceptibility:**
  - statements = the agent's own chat messages and intentions (`embeddings/statements.parquet`), embedded with bge-small, whitened with `common.load_whitener(regime, 32)` and normalized; message direction u_k = the operator message's whitened, normalized embedding;
  - per kick: P̄ = mean of the recipient's statements in [t_k − 60 min, t_k) (last ≤ 5), Q̄ = mean of its statements in (t_k, t_k + 60 min] (first ≤ 5); both needed; Δ(u) = (Q̄ − P̄)·u, a_pre(u) = P̄·u;
  - **matched placebo:** the 10 same-class messages from *other days* of the same period whose a_pre(u_p) on these same statements is closest to a_pre(u_k) (rival R3: equal pre-alignment, so equal regression to the mean); for nudges the pool is restricted to nudges naming the same agent when ≥ 10 exist;
  - χ_con,k = Δ(u_k) − mean Δ(u_p); daily gauge χ_con^c(d) = mean over class-c kicks on day d. Unit: cosine in the whitened space (a random statement has SD ≈ 0.18 on a random direction).
- **Context fill at the kick:** turns since the target's last context reset, counting its `actions` rows except scaffold mirror turns (`pause`, `send_message_back_to_chat`, `search_history`, `move_to_room`). Reset = last `CONSOLIDATE` (regime III) or `START_USING_COMPUTER` (regimes I–II). Secondary: prompt size of the target's last turn (tok_in + cache read + cache write, where logged).
- **Goal age:** active-day index within the goal period (0 = first day).
- **Family:** `roster.lab` of the target.

## Data scheme (`scheme/`)
- **Inputs:** `activity_bins`, `calendar`, `chat_core`, `chat_mentions_clean`, `exposure`, `roster`, `events_core` (CONSOLIDATE / START_USING_COMPUTER), `actions` (turn counts and prompt tokens), `embeddings/{statements, chat_index, chat_bge_small, intentions_bge_small, whitening_*}`. No text is read.
- **Library:** `analysis/h30lib.py` (generic gauge core usable on any swarm log, plus village loaders). H04's `h04lib.py` is imported unmodified for the matched-control cross-check.
- **Output:** `data/processed/H30-operator-susceptibility/G<NN>/` (kicks with covariates and per-kick responses, content pairs with projections, daily gauge table; parquet, no text) with `_provenance.json`; `synthetic/` for the validation.

## Candidate goal periods (unit of analysis: one goal period; non-holdout only)
Structural check done before predictions (message counts only, no response computed): nudges exist from 2026-02-13 (#30). Non-holdout counts (nudges / human messages naming an agent / other human messages / active days): #4 0/336/1377/25 · #5 0/146/735/5 · #6 0/67/376/15 · #13 0/34/16/10 · #30 12/7/8/5 · #31 25/5/4/5 · #33 22/0/1/3 · #35 17/4/7/5 · #37 20/5/0/3 · #38 110/15/13/17 · #39 7/4/9/5 · #40 11/1/3/5 · #41 59/7/0/5 · #42 25/7/3/5 · #44 27/19/40/4 · #51 729/69/44/45 (8 h days). Most later periods have 0–3 human messages a day.

| Period | Regime | Channel with power | Role |
| --- | --- | --- | --- |
| G04, G05, G06 | I (N = 4, 2 h days, public chat) | human (dense: 30–175 messages/day) | human gauge; daily series |
| G13 | I (N = 6) | human (5/day) | low power |
| G30, G31 | I | nudges (first weeks of the nudger) | low power; regime-I nudges |
| G33, G35 | II | nudges | low power |
| G37–G42, G44 | III (4 h) | nudges; G44 humans | G38 (17 d) and G41 carry weight |
| G51 (07-06 → 09-04, non-holdout part) | III (8 h, up to 32 agents) | nudges (~16/day) | the main daily series |
| 🔒 #45, #46–#50, #51 tail | III | | confirmation only (`analysis/confirm.py`) |

## Observables
Per period, per message class (N_tgt, N_by, H_men, H_und):
1. **Period χ_act** (A30, extra active minutes per kick) with day-block bootstrap CI; collective χ_coll per message.
2. **Period χ_con** (cosine units) with day-block bootstrap CI.
3. **Daily gauge series** χ_act^c(d), χ_con^c(d) with SE and kick counts.
4. **Stability** of each daily series with ≥ 4 days carrying ≥ 3 kicks:
   - between-day variance of the true gauge τ² (DerSimonian–Laird) and Cochran's Q test of "same χ every day" (rival R1), plus a permutation version (kicks shuffled across days);
   - single-day reliability R₁ = τ² / (τ² + median SE²), and the reliability of w-day rolling windows;
   - split-half (odd/even kicks within day) correlation across days, Spearman–Brown corrected;
   - lag-1 autocorrelation of the daily series (does today predict tomorrow?);
   - kicks per day needed for R₁ = 0.5.
5. **Goal aging:** slope of per-kick response on goal-day index (agent fixed effects), and of the inverse-variance-weighted daily series.
6. **Context fill:** slope of per-kick response on turns since reset, in thirds of the agent's cycle (regime III: 0–13, 14–27, 28+; HH117's sawtooth), agent fixed effects; prompt tokens as a secondary covariate.
7. **Regime and family:** period χ by regime; per-lab χ_act(N_tgt) in G51 and G38 (HH98).
8. **Cross-check:** H04's matched-control A30 for N_tgt in the same periods (imported `h04lib`), to show the H30 estimator reproduces H04.

## Null / baseline
1. **Pre-window placebo (R2):** the same local projection with the outcome Σ_{τ=−30}^{−16} n(m+τ), which lies before the kick and outside the matching window. A coefficient ≠ 0 means selection on history the strata miss.
2. **Day-swap kick null (R0):** each agent-day's kick times are replaced by the same agent's kick times on another day of the period, at the same window offset (20 draws). This keeps kick density and schedule and destroys within-day alignment.
3. **Bystander response:** N_by and H_und as within-message non-target controls (H04: ≈ 0 for nudges).
4. **Content placebo (R3):** pre-alignment-matched placebo messages (the baseline built into χ_con); also an unmatched placebo (any other-day same-class message), and a pseudo-true null in which a random other-day message is treated as the true one (20 draws), which gives the null distribution of the daily content gauge.
5. **Constant-χ null (R1) for stability:** Cochran's Q and the across-day kick permutation.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness". **Scored after round 1** (2026-10-03). The "model" is linear response to impulsive operator fields, read out per day. It holds at period level in two channels; HH116's *daily-varying* susceptibility is not supported.
**Rival models:** R0 no response; R1 constant susceptibility; R2 selection artifact; R3 engagement / common cause.
**Locked holdout used for confirmation:** none. Planned: #51 tail (primary), #45 (secondary, disclosed reuse), #46–#50 content only (`analysis/confirm.py`, not run).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Kicks, activity, statements and fill are defined from shared-table fields (clean mentions; bookends dropped; no text read), with assumptions listed. Not invariant across regimes: activity means sessions in I and continuous turns in III. Dense regime-I chat breaks the activity estimator's identification (overlapping kicks). Whitening is per regime |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Linearity tested directly: first vs repeat nudges (1.36 vs 0.26) shows **saturation**, as H16 found. Within-period stationarity of χ tested by the day-permutation (weak or no heterogeneity). No Markov audit |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | χ_act(N_tgt) beats the day-swap and zero nulls in G51 (and in G41 under the pre-registered model). χ_con(human) beats the pseudo-true placebo in 6/8 periods. But the daily gauge does **not** predict the next day (lag-1 ≈ 0), which is the held-out test of HH116 |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | Bystander ≈ 0 (G51, pre-registered model) and the pre-window placebo (0.11) are within bounds. Repeat-nudge saturation, H_men > H_und in content, and the RTM-free content null hold. The context-fill signature (P8) and the predicted regime-I human activity response (P3) are absent |
| E interventional | predicts the change across a natural experiment | 0 | No NE tested. The undocumented end of all automated messages on 2026-08-20 (found here) is a candidate (proposed NE43) |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Synthetic recovery at three village samplings with 6 scenarios. It found and fixed three biases: future-nudge conditioning (−1 to −3 min at zero effect), RTM in content (−0.07), and day-shock false heterogeneity (60%). Period-level χ_act on real data is specification-sensitive (0.59 vs 1.04). No embedding swap |
| G ground truth | agrees with known structure | 1 | Reproduces H04's G51 number exactly with H04's code (1.66) and explains the gap. Named agents move more in content than room-mates (addressed > broadcast). Regime-III nudges act on the target only (bystanders ≈ 0), as in H04 |
| H comparative | beats the named rivals | 1 | Beats R0 in G51 activity and in human content. R2 and R3 are handled by design (validated). **R1 (constant χ) is not beaten** at day scale: HH116's daily-varying susceptibility loses |
| I transfer | holds in other same-mode periods, including the holdout | 1 | Human→content transfers across regimes I and III (6/8 periods; I² = 0.38). Nudge→activity is resolved only in G51: G38 is null, and the 3–5-day periods are mixed (4/9 positive). Holdout not run |
## Prediction
*Written 2026-10-03, before any H30 response, alignment or gauge statistic was computed on real data.*

**What I had seen first:** the round-1 results in `LOG.md` (H04, H09, H12, H13, H15, H16, H18, H20); H04's pooled kernels in `data/processed/H04-reversible-forcing/explore_kernels.json` (regime III N_tgt A30 1.54 [0.80, 2.29]; human mentioned 5.6, unmentioned 1.1; bystanders ≈ 0); the message counts above; and, privately, the text of 16 nudges (not quoted anywhere). Nudges are a fixed template (a notice that the agent seems to be idling plus a request to act) with a tailored first sentence that describes the agent's *recent* behaviour. In #51 they are almost pure template; in #31–#41 the tailored part names a concrete task.

**Decision rules.** Per-period verdicts use 95% CIs; card-level claims need the stated count of periods. With ~16 periods × ~10 statistics, single-period hits are expected by chance; only counts and the well-powered periods (G51, G38, G04–G06) carry weight.

**P1 (activity, nudges):** χ_act(N_tgt) > 0 with CI excluding 0 in G51 and G38; size 0.8–2.5 extra active minutes per nudge. In the low-power nudge periods (G30, G31, G33, G35, G37, G39–G42, G44) the point estimate is positive in ≥ 60%, with most CIs including 0.
**P2 (collective mode):** the bystander response χ_act(N_by) per bystander is within ±0.15 min of 0 in G51 and G38, so χ_coll per nudge is within a factor 1.5 of χ_act(N_tgt). A nudge moves one agent, not the swarm.
**P3 (activity, humans):** in G04–G06, χ_act(H_men) > χ_act(H_und) (ratio ≥ 2) and χ_act(H_und) > 0 in ≥ 2 of 3; per-recipient human χ_act in regime I ≥ regime III (G44, G51) (regime I is message-triggered, III timer-gated; H09).
**P4 (content, humans):** χ_con(H_men or H_und) > 0 with CI excluding 0 in ≥ 2 of G04–G06, size 0.02–0.10; H_men ≥ H_und.
**P5 (content, nudges):** χ_con(N_tgt) in G51 is within ±0.02 and its CI includes 0 (templated nudges carry no message-specific direction). In G38/G41 (tailored nudges) it may be positive; no count rule.
**P6 (the gauge is not stable at day scale).**
- Activity: Cochran's Q does **not** reject a constant χ (p > 0.05) in ≥ 2/3 of the eligible periods, and single-day reliability R₁ < 0.3 in G51 (about 16 nudges a day give a per-day SE of ≈ 2 min against a mean of ≈ 1.5).
- Content (human-dense periods): R₁ higher than activity, but < 0.5.
- Lag-1 autocorrelation of the daily activity series in G51 is not distinguishable from 0.
- Usable window for the activity gauge ≥ 5 days at #51's nudge rate.
- **What would count against P6 (for HH116):** R₁ ≥ 0.5 with Q rejecting in ≥ 2 periods, and a positive lag-1 autocorrelation in G51.
**P7 (goal aging, HH116):** **no** within-goal decline. The per-kick slope on goal-day index has a CI including 0 in G51 and G38 (activity) and in G04 (content). Credence ~60%; a significant negative slope in G51 would support HH116.
**P8 (context fill, HH117):** in regime III the activity response is larger early in the context cycle (turns 0–13) than late (28+), ratio ≥ 1.3, and the per-kick slope on turns since reset is negative, in G51. Credence ~40% (H15's erasure dip and H18's dilution point this way; H16's saturating triggers point to no dependence).
**P9 (regime):** per-nudge χ_act(N_tgt) does not differ between regime I/II and III by more than its CI (low power in I/II; no count rule).
**P10 (family, HH98):** in G51 no lab's χ_act(N_tgt) differs from the pooled value beyond its CI after Holm correction (H13: family effects are style only).
**P11 (nulls):** the pre-window placebo coefficient for N_tgt is within ±0.5 min of 0 in G51 and G38; the day-swap null's χ_act(N_tgt) is within its 95% band of 0; the pseudo-true content null is centered on 0.

**Usefulness rule (fixed now).** The daily gauge is **usable** in a channel if the period χ beats nulls 1–4 and R₁ ≥ 0.5 in ≥ 2 periods; **usable at window w** if w-day windows reach reliability ≥ 0.5; otherwise it is **a period-level constant only**.

## Synthetic validation (axis F; done 2026-10-03, before any real-data run)
`analysis/synthetic.py` runs the same estimators (`h30lib`) on simulated swarms; results in `data/processed/H30-operator-susceptibility/synthetic/` (10 replicates per design × scenario). **Simulated data:** agents active/inactive per minute, with aging idle hazards (H16) and declared pauses. A nudger fires on agents idle ≥ 20 min, with a 45-min refractory per agent; humans post Poisson messages to the room, 35% naming one agent. A kick multiplies the target's activation hazard and stay-active odds by (1 + g) during τ = 4–15 min (H04's delay). g = g(day) × (1 − φ·fill/41) × agent factor; bystanders g = 0. Content: whitened 32-d anisotropic OU states; a message read at the agent's next active minute shifts it along u_k. Nudge directions = template + 0.6 × the target's recent statements (rival R3) + a specific part; human directions are random topics. Truth per kick comes from common-random-number counterfactuals. **Designs:**
- G51-like: 16 agents, 8 h, 20 d, ~16 nudges/day;
- G38-like: 12 agents, 4 h, 17 d;
- G05-like: 4 agents, 2 h, 5 d, ~150 human messages/day.

**Scenarios:** S0 null; S1 constant; S2 lognormal day factors (sd 0.6); S3 −70% aging over the period; S4 context fill (φ = 0.8).

| Check | Result | Consequence |
| --- | --- | --- |
| Activity estimator as first written (H04 strata + adjustment for all future kicks), S0 null | N_tgt **−1.0 to −3.4** min (truth 0) | **Rival R2 is real**: nudges go to agents that stay idle, so "future nudges" is an outcome-dependent control, and the nudger decides on the kick minute itself. Fixed by Amendment A1 |
| After A1, S0 null | N_tgt −0.10 / +0.08 (G51-/G38-like); day-swap null −0.01 / +0.23; pre-window placebo −0.06 / −0.14; N_by, H_und ≈ 0 | unbiased under the null |
| S1 constant response | N_tgt 1.62 vs true 2.11 (−23%), 1.24 vs 2.10 (−40%); H_und 1.17 vs 1.18; dense chat H_und 0.06 vs 0.06, H_men 0.65 vs 0.88 | **χ_act(N_tgt) is policy-relative** (a control agent may be nudged later in its window), 20–40% below the per-kick effect; human χ unbiased |
| Daily activity gauge | correlation with the true daily mean 0.4–0.65; daily 95% CI coverage 0.86–0.94 (dense chat 0.70–0.78) | per-day SEs honest except in dense chat |
| "Same χ every day" tests | Cochran's Q rejects in **20–30% of null replicates** (per-day SEs too small). The kick permutation is calibrated (0–10%), with power 0.7 (G51-like) / 0.3 (G38-like) against lognormal sd-0.6 day factors. In dense chat the activity permutation is invalid (60% false positives) | **permutation primary** (A1); no daily activity heterogeneity test in G04–G06 |
| Reliability R₁ | permutation-calibrated R₁ 0.07–0.16 under the null; 0.41 when the true R₁ is 0.61 (G51-like S2) | read R₁ < 0.2 as "no detectable day signal" |
| Aging slope (S3) | −0.091 vs −0.105 /day, CI < 0 in 6/10 (G51-like); 4/10 (G38-like); 0–1/10 false positives | detectable at G51 sampling |
| Fill slope (S4) | −0.054 vs −0.056 per turn, CI < 0 in 8/10 (G51-like); 3/10 (G38-like); 1/10 false positives | detectable at G51 sampling |
| Content, humans | orth 0.106 vs 0.125 (G51-like), 0.114 vs 0.128, dense 0.062 vs 0.076; null ≈ 0 | recovered with ~15% attenuation |
| Content, nudges written from the agent's own recent text | **matched placebo −0.07 (truth 0)**; regression-adjusted −0.06; **orthogonalized −0.009 to −0.017**; when the true response is 0.04–0.06, orth gives ≈ 0 | matched placebo fails rival R3 → orth primary (A1). The message-specific content of templated nudges is **not identifiable**; bias bound −0.02 |
| Daily content gauge, humans | S2: correlation with truth 0.75–0.84; permutation power 0.7–1.0; false positives ≤ 0.1 | a daily *content* gauge can work with ≳ 40 recipient-messages a day |

### Amendment A1 (2026-10-03; after the synthetic validation, before any real-data H30 statistic)
1. **Activity strata** (replaces the definition above):
   - history runs through the kick minute itself;
   - minutes since the last active minute use finer bins: 0, 1–4, 5–14, 15–19, 20–29, 30–44, 45–89, 90+, and not yet active today;
   - new bin: minutes since the agent's last *directed* kick (N_tgt or H_men): 1–15, 16–30, 31–60, none.
   - **Future-kick adjustment only for undirected classes** (N_by, H_und). Past kicks are adjusted per class.
   - H04's strata are kept as a sensitivity variant (`strata="h04"`).
2. **Content estimator:**
   - primary χ_con = **orthogonalized**. The true and placebo directions are projected off the span of the recipient's last ≤ 8 statements in the 2 h before the kick, then the post-statement alignment is compared with the mean over the same-class other-day pool.
   - The pre-registered matched estimator is reported alongside.
3. **Stability:**
   - primary heterogeneity test = **kick permutation across days**, with permutation-calibrated R₁ (R₁ = 1 − Var_perm/Var_obs of daily means). Cochran's Q and SE-based R₁ are reported but known to over-reject.
   - No activity heterogeneity test in the dense-chat periods (G04–G06).
4. **Reading χ_act(N_tgt):** it is the effect of a nudge *now* relative to the nudger's default policy, expected 20–40% below the per-kick effect. H04's A30 shares the estimand.
5. **Predictions unchanged.** P5 now carries a known bias bound (−0.02). The P6 thresholds apply to the permutation-calibrated R₁.

### Amendment A2 (2026-10-03; POST HOC: made after seeing first-pass real-data results; sensitivity and design fixes)
**What I had seen.** First-pass real-data results with the A1 design (no day fixed effect):
- G51 χ_act(N_tgt) 0.59, a daily permutation p of 0.002 with R₁ 0.62, and an aging slope of −0.065 /day;
- G38 near zero;
- H04's G51 number reproduced at 1.66 by H04's own code.

**Changes.** Each is labelled in the results; the pre-registered numbers are always reported next to it.
1. **Day fixed effect** (alternating projections) added to the activity model for all *day-to-day* questions (daily gauge, stability, aging, fill).
   - *Why:* per-kick residuals carried each day's swarm-wide activity level. In a new synthetic scenario (S5: constant χ, day-level activity shocks), the permutation test then rejected "same χ every day" in 60% (G51-like) and 30% (G38-like) of replicates. With day FE it rejected in 0%; power against true day variation stayed at 0.5.
   - *Levels* (P1–P3) keep the pre-registered model as primary.
2. **Message-cluster permutation** (all recipients of a message move together) is primary for stability; a within-agent permutation controls for which agents were kicked that day. Kick-level permutation is reported but anti-conservative.
3. **Outage mask:** cells within [m−15, m+30] of a run of ≥ 30 min in which every present agent is silent are excluded, as a sensitivity check. Meaningful in regime III only; in regime I such runs are session gaps (17–40% of cells).
4. **Fill-phase design for P8:** control cells are stratified by their *own* context phase (turns since reset: 0–13, 14–27, 28+), because scheduled consolidations add activity late in the cycle whether or not a message arrived.
5. **Descriptive splits:** first vs repeat nudge (no directed kick in the previous 30 min; past-only, so pre-treatment), and swarm-lull vs not (the bottom quartile of the fraction of agents active in the previous 5 min).
6. **H04 isolation check:** H04's isolation rule applied inside the H30 model, on real data and on synthetic swarms.

## Results by goal period
Verdict rule (per period): all rows supported → supported; none → failed; else mixed. Round-1b verdicts are in each folder's `Verdict (1b)` line (changes: G39 failed → mixed; G31, G42 mixed → failed); G05 also carries the #5 dilution native test (failed). Low-power periods (≤ 5 days or < 30 nudge kicks) are flagged. In the G-folder verdict lines, `*` marks a content CI excluding 0. Activity numbers use the pre-registered model; content uses the orthogonalized estimator (A1).

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G04](goalperiod-subhypotheses/G04/README.md) | exploratory, regime I, human-dense | mixed | content H_und 0.030 [0.025, 0.035], H_men 0.033 [0.021, 0.049]; human activity ≈ 0 (H_und −0.21 [−0.64, 0.17]); daily content gauge p 0.004, R₁ 0.28 |
| [G05](goalperiod-subhypotheses/G05/README.md) | exploratory, regime I, human-dense (5 d) | mixed | content H_und 0.023 [0.019, 0.027], H_men 0.046 [0.035, 0.054]; H_men activity −0.96 [−1.63, −0.46] |
| [G06](goalperiod-subhypotheses/G06/README.md) | exploratory, regime I, human-dense | mixed | content H_und 0.012 [0.005, 0.037]; daily content gauge p 0.002, R₁ 0.53, lag-1 −0.17 |
| [G13](goalperiod-subhypotheses/G13/README.md) | exploratory, regime I | mixed | content H_und 0.036 [0.015, 0.046], H_men 0.066 [0.053, 0.102]; activity ≈ 0 |
| [G30](goalperiod-subhypotheses/G30/README.md) | exploratory, regime I (nudger starts) | mixed (low power) | 11 nudge kicks, CI unstable; content H_und 0.036 [0.002, 0.048] |
| [G31](goalperiod-subhypotheses/G31/README.md) | exploratory, regime I | mixed (low power) | nudge 0.68 [−0.25, 2.00] (n 18); bystander 0.41 [0.10, 0.86] |
| [G33](goalperiod-subhypotheses/G33/README.md) | exploratory, regime II (3 d) | mixed (low power) | nudge 0.14 [−2.11, 1.33]; bystander −0.98 |
| [G35](goalperiod-subhypotheses/G35/README.md) | exploratory, regime II | failed (low power) | nudge −0.75 [−5.67, 0.22] (n 6) |
| [G37](goalperiod-subhypotheses/G37/README.md) | exploratory, regime III (3 d) | mixed (low power) | nudge 0.49 [−3.23, 1.84]; pre-window placebo −2.2 |
| [G38](goalperiod-subhypotheses/G38/README.md) | exploratory, regime III (17 d) | mixed | nudge −0.08 [−0.98, 0.82] (n 82; day FE 0.38; first nudge 0.72); bystander −0.54; pre-window placebo −0.59; content H_und 0.020 [−0.001, 0.036] |
| [G39](goalperiod-subhypotheses/G39/README.md) | exploratory, regime III | failed (low power) | 7 nudge kicks |
| [G40](goalperiod-subhypotheses/G40/README.md) | exploratory, regime III | failed (low power) | nudge −1.15 [−2.72, 0.82] (n 9) |
| [G41](goalperiod-subhypotheses/G41/README.md) | exploratory, regime III | mixed (low power) | nudge 0.86 [0.51, 1.26] (n 53; day FE 0.28 [−0.60, 1.22]) |
| [G42](goalperiod-subhypotheses/G42/README.md) | exploratory, regime III | mixed (low power) | nudge 0.57 [−1.76, 2.12] (n 18) |
| [G44](goalperiod-subhypotheses/G44/README.md) | exploratory, regime III (4 d) | mixed (low power) | nudge −0.32 [−1.19, 0.70]; human H_und activity 0.62 [0.23, 3.15]; content n.s. |
| [G51](goalperiod-subhypotheses/G51/README.md) | exploratory, regime III (45 d, 8 h) | mixed | nudge 0.59 [0.24, 0.93] (n 875; day FE 1.04; first 1.36, repeat 0.26); bystander 0.13 [−0.11, 0.38]; content H_und 0.025 [0.014, 0.033], H_men 0.063 [0.043, 0.101]; nudge content 0.003; daily gauge p 0.08, R₁ 0.28, lag-1 −0.09; no aging, no fill effect, no lab effect |
| [NE44](goalperiod-subhypotheses/NE44/README.md) | native (round 1b) | failed | 12-h pause default pooled 0.57 [0.04, 1.10] vs G51 0.98: Δ −0.41 [−1.05, 0.24]; first nudges Δ −0.69 [−1.36, −0.02] (reversed) |
| [NE10](goalperiod-subhypotheses/NE10/README.md) | native (round 1b) | failed (low power) | first nudges ever + first fortnight pooled −0.42 [−1.27, 0.42] (22 kicks) |

## Results
### Exploratory round 1 (2026-10-03; non-holdout; 16 goal periods)
- **Scripts:** `scheme/build.py`; `analysis/run_period.py --period G<NN>`; `analysis/summarize.py`; `analysis/synthetic.py`; `analysis/synthetic_h04check.py`; `analysis/figures_synth.py`; `analysis/write_period_folders.py`; `analysis/confirm.py`; and the operator API `analysis/gauge.py`.
- **Library:** `analysis/h30lib.py`, which imports `h04lib` unmodified.
- **Numbers** (all in `data/processed/H30-operator-susceptibility/`):
  - `G<NN>/results.json`, `daily.parquet`, `kick_resp.parquet`;
  - `summary.json`;
  - `synthetic/`;
  - `confirm_dryrun/`.
- **Figures:**
  - `figures/H30_summary.pdf` (one-page figure summary);
  - `figures/summary_obs.pdf`;
  - `figures/synthetic_validation.pdf`;
  - `goalperiod-subhypotheses/G<NN>/figures/daily_gauge.pdf`.

**Outcome vs prediction.**

| Prediction | Predicted | Outcome | Verdict |
| --- | --- | --- | --- |
| P1 nudge → target activity | G51 and G38 > 0 with CI excl. 0, 0.8–2.5 min; ≥ 60% of low-power periods positive | G51 0.59 [0.24, 0.93] (day FE 1.04 [0.77, 1.33]); G38 −0.08 [−0.98, 0.82] (day FE 0.38); low-power 4/9 positive | **sign supported in G51 only**; size below the band; G38 and count rule failed |
| P2 bystanders ≈ 0; χ_coll ≈ χ_target | \|N_by\| ≤ 0.15 in G51, G38 | G51 0.13 [−0.11, 0.38] (≈ 0 within swarm-state subsets; day FE pooled 0.43, a composition effect); G38 −0.54 [−1.01, −0.01] | **supported in G51**, failed in G38; χ_coll not resolved (≈ 21 bystanders per nudge magnify noise) |
| P3 human → activity (H_men ≥ 2 × H_und > 0; regime I ≥ III) | ≥ 2 of G04–G06 | H_und ≈ 0 or negative everywhere in regime I (−0.06 to −0.34); H_men never above H_und; regime III H_und 0.26 (G51), 0.62 (G44) | **failed** |
| P4 human → content | χ_con > 0 (CI) in ≥ 2 of G04–G06, 0.02–0.10; H_men ≥ H_und | G04 0.030, G05 0.023, G06 0.012 (CI > 0, below band), G13 0.036, G51 0.025; H_men 0.033–0.066; pooled H_und 0.026 [0.021, 0.030], H_men 0.046 [0.036, 0.057] | **supported** (regime III too) |
| P5 nudge → content ≈ 0 | \|χ\| < 0.02, CI incl. 0 (G51) | 0.003 [0.000, 0.005]; G38 0.000, G41 0.008 (n.s.) | size supported, **CI clause failed** (negligible effect; RTM bias bound −0.02) |
| P6 gauge unstable at day scale | perm p ≥ 0.05; R₁ < 0.3; lag-1 ≈ 0; ≥ 5-day windows needed | G51 activity p 0.08, R₁ 0.28, lag-1 −0.09 (p 0.68). w-day windows R 0.21 / 0.08 / 0.32 / 0.41 (w = 2, 3, 5, 10). G38 p 0.16, R₁ 0.40. Content: G04 p 0.004, R₁ 0.28; G06 p 0.002, R₁ 0.53; G51 R₁ 0. *Pre-registered model:* G51 p 0.002, R₁ 0.62, the day-shock signature | **supported** (no window reaches R 0.5; no persistence). HH116's falsifier is not met |
| P7 no aging | slope CI incl. 0 (G51, G38 activity; G04 content) | G51 −0.019 [−0.049, 0.012] /day (day FE; pre-registered −0.065 [−0.113, −0.017] = baseline drift); G38 0.016; G04 content +0.0007 [0.0002, 0.0012] (rising) | **supported**: nothing declines with goal age |
| P8 context sawtooth | early ≥ 1.3 × late; slope < 0 (G51) | G51 early 0.94 [0.67, 1.22] (n 685), mid 1.38, late 1.00 [−0.58, 2.53] (n 45); G38 early 1.21, late −0.15 (n.s.) | **failed** (nudged agents are idle, so 80% of nudges land early in the cycle) |
| P9 regime | no difference beyond CI | random effects: I/II 0.40 [−0.50, 1.29], III excl. G51 0.15 [−0.52, 0.83], III 0.37 [−0.06, 0.79] | supported (low power) |
| P10 family | no Holm-significant lab | G51: Anthropic 1.56 [0.69, 2.42], OpenAI 1.04, DeepSeek 0.78, Google 0.13 (day FE); Holm p ≥ 0.74 | supported |
| P11 nulls | pre-window placebo within ±0.5; day-swap band incl. 0; content null at 0 | G51 0.11 (day FE 0.31), day-swap 0.03 [−0.25, 0.19], content null −0.001; G38 placebo −0.59 | supported in G51; **failed in G38** |
| Usefulness rule | daily gauge usable if R₁ ≥ 0.5 in ≥ 2 periods | activity: never; content: G06 only (0.53, no persistence) | **period-level constant only** |

**Reading.**
1. **Two channels, two kinds of operator message (HH52's reading, partly).** Nudges are a short, local *activity* kick: about one extra active minute in the next half hour for the named agent, nothing for room-mates, and no message-specific content. Human messages carry a content *field*: recipients' next statements move toward what the message adds, by about 0.03 (cosine, whitened) for room-mates and 0.05 for named agents, with no activity response. Neither channel is a pure catalyst (cf. H39).
2. **Repeats don't work.** First nudge 1.36 [0.98, 1.75] vs repeat 0.26 [−0.13, 0.63] (G51, day FE). Re-nudging an agent that didn't respond within 30 min buys almost nothing (H16's saturation).
3. **Nudging into a swarm-wide lull does little** (post hoc). With the bottom quartile of swarm activity in the previous 5 min the response is 0.18 [−0.07, 0.50]; outside lulls it is 0.84 [0.52, 1.18] (G51).
4. **There is no daily steerability state to track.**
   - Day-to-day variation of χ_act is at most weak once each day's own activity level is removed (G51 p 0.08, R₁ 0.28). It shows no persistence and no trend with goal age.
   - Context fill doesn't modulate it, and labs don't differ beyond noise.
   - What did look like day-to-day steerability in the pre-registered model (R₁ 0.62, aging −0.065/day) is day-level activity shifting. The synthetic S5 scenario reproduces it.
   - The content gauge does vary by day in two regime-I periods (G04, G06), probably because human messages differ in how much new content they carry; it doesn't persist either.
5. **H04's isolated nudge A30 is inflated.** Applying H04's isolation rule (no other directed kick in [m−30, m+60]) inside the H30 model moves G51 from 0.59 to 1.61. That rule keeps the 320 nudges that the nudger did not need to repeat. Kicks followed by a re-nudge respond 0.56; the others 1.33. In synthetic swarms the same rule biased the estimate by −0.9 to −2.0 min at zero effect. The direction depends on the nudger's policy, so isolation on future kicks should not be used.
6. **Specification sensitivity of the level.** The G51 nudge response is 0.59 (pre-registered), 1.04 (day FE), 1.00 (agent-day FE), 0.90 (outage-masked) or 0.98 (swarm-state strata). The honest statement is "≈ 0.6–1.0 min per nudge, ≈ 1–1.4 for a first nudge". With day FE the pre-window placebo is 0.31 ± 0.08 (residual within-day selection); without it, 0.11.

### Operator-facing gauge (`analysis/gauge.py`)
`chi_op(actions, op_msgs, statements=None, windows=None)` takes plain logs and returns per-day, per-class χ_act (extra active minutes per message, 30-min horizon) and χ_con (cosine shift toward the message's new content), period estimates with day-block CIs, and the stability report (permutation p, R₁, lag-1, window reliabilities). Inputs:
- `actions`: agent, t, optional `paused`;
- `op_msgs`: msg, t, kind (nudge / human), named targets, recipients, optional embedding;
- `statements`: agent, t, embedding.

On another swarm:
1. bin actions to 1-min activity per agent within each day's active window;
2. classify each operator message's recipients as named or room-mates;
3. run the local projection with matched pre-history strata plus a day fixed effect, adjusting past kicks and future *undirected* kicks only (never future directed ones);
4. for content, whiten embeddings on the swarm's own statements, project each message off the span of the recipient's last 8 statements, and compare post-message alignment with same-kind messages from other days.

Self-test on a simulated swarm: N_tgt 1.77 vs true 1.70; bystanders 0.03 vs 0.

**How to use it (and how not to):**
- **Read it as a period constant.** At about 25 nudges a day, a single day's χ_act has an SE of about 1–2 min against a mean of about 1. The kicks needed for a usable daily value are ~100+ when there is real day variation, and the observed variation is small.
- **Act on the stable facts instead:** first nudges work, repeats and lull-time nudges don't, room-mates don't respond, and named agents follow content more.

### Caveats
- **Power.** Only G51 resolves the nudge response. The 3–5-day periods have ≤ 35 bootstrap resamples, and their bystander estimates swing between −1.4 and +0.9. Human activity in dense regime-I chat is not identified: overlapping kicks leave no kick-free variation, and the activity permutation is invalid there (synthetic false-positive rate 0.6).
- **Estimand.** χ_act(N_tgt) is policy-relative: the effect of nudging now, given that the nudger may nudge again. It sits 20–40% below the per-kick effect in synthetic swarms.
- **Level depends on specification** (0.59–1.04 in G51; see Reading 6). With day FE the pre-window placebo is 0.31 in G51.
- **Content.**
  - χ_con measures *message-specific* steering relative to same-kind messages. For templated nudges it is not identifiable (synthetic), and the RTM bias bound is −0.02.
  - Human messages can be replies to the agents (common cause, H18); the orthogonalization removes alignment already present in the recipient's last 8 statements, but not shared topics that are about to come up.
  - One embedding model (bge-small); no swap.
- **Coverage.** About 5% of nudges fall in the last 30 min of the day, where the horizon doesn't fit, and are dropped (late-day reminders).
- **Undocumented step.** All automated messages stop after 2026-08-20; G51's nudge series covers 07-06 → 08-20.
- **Multiplicity.** 16 periods × ~12 rows; single-period hits are expected by chance. Several design choices are post hoc (A2), each listed with what I had seen.

### Confirmatory predictions (C-*): for the locked holdout, written 2026-10-03 after round 1, not run
Script: `analysis/confirm.py`. It refuses without `--confirm --i-understand-this-uses-the-locked-holdout` and refuses if the H30 folder has uncommitted changes. `--dry-run` writes `data/processed/H30-operator-susceptibility/confirm_dryrun/` using stand-ins: G51 08-07 → 08-20, G44, and G41/G42.

**Reuse disclosures (holdout policy):**
- **#51 tail:** primary; no confirmatory run has used it.
- **#45:** H02 used it for activity-timing couplings and βJ₀; H23 plans leader message-content statistics. H30's kick-triggered activity response and its recipient alignment with operator messages are different statistics.
- **#46–#50:** content only. H04 ran nudge activity responses inside NE21/NE23, so `confirm.py` builds no activity panels there.

The tail may contain no nudges (automated messages stop on 08-20 in the non-holdout data; the tail was not inspected), so the tail's activity prediction is conditional.

| ID | Target | Statement | Primary |
| --- | --- | --- | --- |
| C-act | T2 (+ T1 if ≥ 30 nudge kicks) | random-effects pooled χ_act(N_tgt), pre-registered model, > 0 with CI excluding 0 | yes |
| C51-2 | #51 tail | χ_con(H_und) > 0 with CI excluding 0 | yes |
| C4650-1 | #46–#50 | pooled χ_con over human recipients > 0 with CI excluding 0 | yes |
| C51-1 | #51 tail | χ_act(N_tgt) > 0 with CI excluding 0 (n/a if < 30 nudge kicks) | no |
| C51-3 | #51 tail | first-nudge χ_act > repeat-nudge χ_act (day FE) | no |
| C51-4 | #51 tail | \|χ_act(N_by)\| ≤ 0.3 | no |
| C51-5 | #51 tail | no usable day signal: message-permutation p ≥ 0.05 or R₁ < 0.5, and lag-1 p ≥ 0.05 | no |
| C51-6 | #51 tail | \|χ_con(N_tgt)\| < 0.02 | no |
| C45-1, C45-2 | #45 | χ_act(N_tgt) > 0; χ_con(H_und) > 0 (points) | no |
| C4650-2 | #46–#50 | \|pooled χ_con(N_tgt)\| < 0.02 | no |

- **Overall rule:** supported if every testable primary passes; failed if none does; otherwise mixed.
- **Dry run (stand-ins, not evidence):** C-act fail (pooled 0.22 [−0.65, 1.10]); C51-2 fail (one day carries all the stand-in's human pairs; degenerate CI); C4650-1 n/a (too few human pairs in G41/G42). Expected power: C51-2 good if the tail has ~2.5 human messages a day; C-act weak unless the tail has nudges.

## Round 1b (improved data, 2026-10-04)
*Re-run of the round-1 pipeline on corrected inputs (`scheme/build.py --data r1b`, `analysis/run_period.py --data r1b`, `analysis/r1b_extra.py`), with three period-native tests. Predictions P1–P11, the usefulness rule and the per-period verdict rule are unchanged; native predictions were written in their folders at 07:31 UTC, before any round-1b statistic on those periods.*

**What changed in the inputs.**
- **Activity:** `activity_bins_fixed` (round 1's table dropped about half of all events, DQ8). Outage masks are recomputed from it.
- **Nudge target = the leading @** (H35; `infra/README.md` Known issue). In G51, 239 named-second exposures that round 1 counted as targets become bystanders; 723 of 729 nudges reach their target's receiving call (6 never read).
- **Kick time = the receiving call** (DQ1 `context_ledger_items` → `call_windows.t_call`), and recipients come from the ledger instead of `exposure`. Median read-out wait for nudges: 122 s in G51, 25–75 s elsewhere. Pairs read on a later day than posted are dropped (266 of 19,947 items in G51).
- **Design:** strata use history through m − 1 only, plus an indicator that a model call starts at m (kicked cells always sit on a receiving call, so they are compared with call minutes); the outcome counts active minutes from the receiving call itself (τ = 0 … 29); **past-only kick adjustment** (round 1's A1 regressors for future undirected kicks are dropped, DQ8 `lever_design`), **day fixed effect primary for levels** (round 1 used the no-FE model for levels). The A1 variant and the no-FE model are reported as sensitivities.
- **Content:** pre/post windows at the receiving call; bge-small (primary) and gte-modernbert.
- H04's cross-check (`h04lib`, old activity table) is not part of round 1b. Old paths run unchanged by default; round-1b outputs are in `data/processed/H30-operator-susceptibility/r1b/`.

**What moved the G51 nudge response** (decomposition, `r1b/decomposition.json`; day FE / no FE):

| Step | G51 | G38 |
| --- | --- | --- |
| (a) round 1 | 1.04 [0.77, 1.33] / 0.59 [0.24, 0.93] | 0.38 / −0.08 |
| (b) + fixed activity bins | 1.43 [1.15, 1.77] / 1.29 [1.00, 1.64] | 0.78 [0.16, 1.57] / 0.74 |
| (c) + leading @ and ledger recipients (posting minute) | 1.58 / 1.40 | 0.68 / 0.64 |
| (d) + receiving-call timing (A1 future-undirected adjustment kept) | 1.56 / 1.16 | 1.03 / 0.96 |
| (e) + past-only adjustment = **round 1b** | **0.98 [0.63, 1.37]** / 1.07 [0.73, 1.47] | **0.95 [0.38, 1.54]** / 0.91 |

The event-drop fix carries most of the change (dropping half the events shrinks every active-minute count, and with it the response). With past-only controls the day-FE and no-FE levels agree (0.98 vs 1.07); the A1 future-kick regressors interact with the day FE (1.56), which is one more reason not to condition on future kicks. **Honest level: ≈ 1.0 extra active minute per nudge in G51 and G38**, matching RE-V1's corrected H04 A30 in #51 (1.16 [0.75, 1.57]).

**Old vs new.**

| Prediction / statistic | Round 1 | Round 1b | Verdict 1b (round 1) |
| --- | --- | --- | --- |
| P1 χ_act(N_tgt), G51 · G38 | 0.59 [0.24, 0.93] · −0.08 [−0.98, 0.82] | **0.98 [0.63, 1.37] · 0.95 [0.38, 1.54]** | **supported** (G51 only) |
| P1 low-power periods with point > 0 | 4/9 | 5/10 (G33, G37*, G39, G41, G44) | count rule fails (fails) |
| random-effects χ_act: regime III all · III excl. G51 · I/II | 0.37 [−0.06, 0.79] · 0.15 · 0.40 | **0.76 [0.39, 1.14] · 0.57 [0.04, 1.10]** · −0.29 [−1.06, 0.47] | – |
| G51 first · repeat nudge (day FE) | 1.36 [0.98, 1.75] · 0.26 [−0.13, 0.63] | 1.21 [0.80, 1.66] (n 478) · 0.44 [−0.19, 1.10] (n 180) | – |
| G51 nudge during a swarm lull · not | 0.18 [−0.07, 0.50] · 0.84 [0.52, 1.18] | **1.74 [0.94, 2.63] · 0.72 [0.34, 1.15]** | reversed |
| P2 bystanders G51 · G38 | 0.13 [−0.11, 0.38] · −0.54 [−1.01, −0.01] | −0.01 [−0.09, 0.08] · −0.09 [−0.43, 0.31] | **supported** in both (G51 only) |
| P3 human → activity (regime I) | H_und ≤ 0; H_men never > H_und | H_und 0.02–0.15 (CIs ∋ 0); H_men > H_und in G06, G13 only | failed (failed) |
| P4 human → content, pooled H_und · H_men (bge) | 0.026 [0.021, 0.030] · 0.046 [0.036, 0.057]; CI > 0 in 6/8 | 0.024 [0.021, 0.027] · 0.041 [0.034, 0.048]; 6/9 | supported (supported) |
| P4 second model (gte) H_und · H_men | – | 0.024 [0.021, 0.028] · 0.044 [0.028, 0.060]; 7/9 | supported |
| P5 nudge → content, G51 | 0.003 [0.000, 0.005] | 0.002 [−0.001, 0.005] | **supported** (CI clause failed) |
| P6 G51 daily χ_act: message-cluster permutation p · R₁ · lag-1 | 0.08 · 0.28 · −0.09 | **0.026 · 0.48** · 0.08 (p 0.22) | **failed as written** (supported) |
| P6 SE-based window reliability, w = 2 / 3 / 5 / 10 days (G51) | 0.21 / 0.08 / 0.32 / 0.41 | 0.62 / 0.74 / 0.72 / 0.35 | see text |
| P7 aging slope, G51 (day FE) | −0.019 [−0.049, 0.012] | 0.020 [−0.027, 0.067] | supported (supported) |
| P8 context fill, early · late (G51, phase-matched) | 0.94 · 1.00 | 0.66 [0.32, 1.04] · 1.49 [−0.01, 3.12] | failed (failed) |
| P10 lab differences (G51) | none Holm-significant | none (DeepSeek 1.95, Anthropic 1.51, OpenAI 0.71, Google −0.33; Holm p ≥ 0.17) | supported (supported) |
| P11 nulls: pre-window placebo G51 · G38; day-swap G51 | 0.11 · −0.59; 0.03 | 0.02 · 0.05; 0.06 [−0.15, 0.29] | **supported** in both (G51 only) |
| per-period verdicts mixed / failed | 13 / 3 | 12 / 4 (G39 failed → mixed; G31, G42 mixed → failed) | – |

\* CI excludes 0.

**P6 and the usefulness rule.** With the fixed bins the G51 daily nudge gauge has detectable day-to-day variation (message-cluster permutation p 0.026; within-agent p 0.064; R₁ 0.48), so P6 fails as written. It still does not persist (lag-1 0.08, p 0.22), and R₁ stays below 0.5, so HH116's falsifier (R₁ ≥ 0.5 with rejection in ≥ 2 periods and positive lag-1) is not met. The SE-based window reliabilities now exceed 0.5 for 2–5-day windows, but the same statistic gives 0.68–0.89 in G38, where the calibrated permutation finds no day signal at all (p 0.77, R₁ 0): it inherits Cochran's over-rejection (synthetic validation), so I do not count it. **Usefulness verdict unchanged: a period-level constant, now ≈ 1 minute per nudge in both large periods.**

**Native tests (layer 2).**

| Folder | Design | Prediction | Result | Verdict |
| --- | --- | --- | --- | --- |
| [G05](goalperiod-subhypotheses/G05/README.md) | #5 human dose: per-message χ_con by the number of human messages read in the same call (k_h) | slope < 0 (CI), ratio k=1 / k≥8 ≥ 2 | bins 1 / 2–3 / 4–7 / 8+: 0.025 / 0.020 / 0.013 / 0.047 (n 1,501 / 1,207 / 435 / 196); slope +0.19 [−1.17, 0.46]; gte the same shape; named > unnamed in both bins with data | **failed** by the rule (monotone 1/k^0.4-like fall over the three well-sampled bins; the 8+ bin is noisy) |
| [NE44](goalperiod-subhypotheses/NE44/README.md) | χ_act(N_tgt) under the 12-h pause default (G37–G44, pooled) vs 5-min (G51) | Δ > 0 | 12-h 0.57 [0.04, 1.10] vs G51 0.98: Δ −0.41 [−1.05, 0.24]; first nudges Δ −0.69 [−1.36, −0.02] | **failed** (reversed) |
| [NE10](goalperiod-subhypotheses/NE10/README.md) | first nudges ever (G30) and the first fortnight (G31) vs G51 first nudges | pooled point > 0, no novelty premium | pooled −0.42 [−1.27, 0.42] (9 + 13 kicks); G51 first 1.21 | **failed** (low power) |

Reading: nudges are not a novelty effect (NE10) and they buy *more* under the short pause default (NE44), consistent with RE-V1 (no early wakes at nudge-receiving calls before or after NE44; the response is immediate at the receiving call) and with H43 (nudges make idle agents glance; the 5-min scaffold provides more gates to glance at). A long pause default makes agents sleep through some nudges' effect window rather than waking them for sustained work.

**Scorecard after 1b** (scores unchanged, evidence updated): A 1; B 1 (saturation still: first 1.21 vs repeat 0.44); C 1 (χ_act beats the day-swap and zero nulls in G51 *and* G38 now; the daily gauge still does not predict the next day); D 1 (bystanders ≈ 0 and pre-window placebo within bounds in both large periods; P5 passes; the fill signature is absent); E 0 (NE44 reversed; NE10 underpowered); F 1; G 1 (agrees with RE-V1's corrected H04 number and with H43's read-out timing); H 1; I 1 (nudge → activity now resolved in two periods and pooled regime III excluding G51, 0.57 [0.04, 1.10]; holdout not run). **A1 B1 C1 D1 E0 F1 G1 H1 I1.**

**Operator rules, revised.** (1) One nudge buys about a minute of extra activity from the receiving call on, in both regime-III eras; the first nudge of an episode about 1.2 min, repeats about 0.4 (CI includes 0). (2) **Nudging during a swarm-wide lull is fine, even better** (round 1's warning was a data artifact). (3) Room-mates don't respond to others' nudges. (4) Short scaffold pauses make nudges more effective, not less (NE44). (5) To steer what an agent writes, name it and add new content (+0.04 vs +0.02 for room-mates, both embedding models); when many human messages arrive at once, each one's pull falls over 1–7 messages.

**Disclosure.** A probe for the leading-@ rule printed per-period nudge counts including held-out periods (#32, #34, #45–#50, #51 tail); no outcome was computed there.

## Round 2 redirects
**What the direction is really after:** a trustworthy answer to "will my next message change what this swarm does?". Round 1 says it is per situation, not a daily state.
- **H30-R1. Situational χ instead of daily χ.** Estimate χ_act and χ_con by message situation (first vs repeat, swarm lull vs active, target idle duration, named vs room) with hierarchical pooling across periods. These are the levers round 1 found; test them in G51 with day-blocked cross-validation.
- **H30-R2. The 2026-08-20 switch-off as a natural experiment.** All automated messages stop (proposed NE43). Use it to measure what the nudger buys at swarm level (idle share, output) with day-matched controls; coordinate with H39, which saw it too.
- **H30-R3. Embedding swap and reply control for χ_con.** Rerun content with a second embedding model, and exclude human messages that reply to an agent's previous statement, to bound the common-cause share (H18).
- **H30-R4. Per-message content strength.** Model χ_con as a function of how much new content a message carries (‖u⊥‖) and whether it names a task. This could explain the day-to-day content variation in G04/G06.
- **H30-R5. Run `confirm.py`** after the card is committed.

## Notes
- 2026-10-04: promoted from HH116 by Vivian (usefulness-first batch); wave 1.
- 2026-10-03: round-1 agent started; card pre-registration written before any H30 statistic on real data.
- 2026-10-03: round 1 done. Compute: local, ≤ 2 processes. Synthetic suite ≈ 7 min × 3 runs; real-data periods ≈ 4 min per full pass. Disk: `data/processed/H30-operator-susceptibility/` ≈ 5 MB.
- 2026-10-03: data facts for everyone:
  - all automated messages stop after 2026-08-20 (undocumented; proposed NE43);
  - 52% of G51 nudges are followed by another directed kick to the same agent within 60 min;
  - ~5% of nudges land in the last 30 min of the day.
- 2026-10-03: the session was interrupted by an API limit after the confirmatory dry run. Nothing was lost (all period runs had finished); the card and summary were completed on resume.
- 2026-10-04: round 1b on fixed activity bins, leading-@ targets, receiving-call timing, past-only controls with day FE, two embedding models; natives G05 (#5 dilution), NE44, NE10; ~25 min of compute on ≤ 2 processes; disk +6.5 MB in `data/processed/H30-operator-susceptibility/r1b/`.
