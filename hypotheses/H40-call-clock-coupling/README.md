# H40: The call clock sets the coupling

**Status:** exploratory round 1 **done (2026-10-04): the call clock holds in the computer-use scaffold (regimes II–III), not in the regime-I chat scaffold.** Card, observables and predictions written 2026-10-04 ~06:10 UTC, before any coupling statistic on real data; amendments A1–A4 dated below.
- **Regimes II–III (11 periods, incl. G51 with 18k replies): call clock.** A call that spans more wall time carries no more reply hazard: η = −0.00 ± 0.05 in G51, pooled −0.16 [−0.32, +0.01] (III) and −0.01 [−0.12, +0.11] (II); 0.00 at timer wakes whose wait was declared in advance (G51, −0.03 [−0.14, +0.08]). Relevance decays per recipient call (φ −0.60) and per newer message (χ −0.72), barely per minute (ψ −0.19).
- **Regime I (22 periods): neither clock.** η +0.51 [+0.41, +0.61] (chat-mode calls +0.60), robust to start-time source and to short spans; G18's native test failed (η 0.81).
- **Heavy spins (G51, 32 agents, 243 agent-units):** per-call coupling does not depend on cadence (s +0.11 [−0.03, +0.25]; −0.00 with lab + style controls) and is a family/style trait (lab + style R² 0.25, cadence 0.01); per-hour coupling scales ~linearly with call rate (slope 1.00 [0.81, 1.19]; cadence R² 0.50 vs lab + style 0.33). Slowest-fifth agents (25 calls/h) answer within 5 min 8× less often than the fastest fifth (184/h).
- **Operator statement:** doubling a recipient's call rate (all intervals halved, message stream fixed) raises its 5-min reply coupling by ×2^0.57 ≈ 1.5 [1.3, 1.7] (regime III pooled; G51 ×1.32 [1.29, 1.36]) and its 30-min coupling by ×1.39 [1.27, 1.51] (G51 ×1.21). Cross-sectionally the association is steeper (slope 1.0 in G51).
- Pooled across agents and periods, s = −0.12 [−0.28, +0.04] (rival s = −1 excluded). Natives: G51 supported, NE41 mixed (no catch-up after forced erasure; raw ratio failed), G18 and G36 (NE14) failed. Replication verdicts 15 supported / 14 mixed / 4 failed (all non-supported in regime I). Scorecard A1 B1 C1 D1 E1 F2 G1 H1 I1. `confirm.py` (NE20 in #45, NE44 in #46, transfer #45–#47, #28) written, frozen and dry-run; **not run**.
- **Round 2 (2026-10-05; section "Round 2"):** G38/G44's negative η is mostly call-type composition: long tool calls are followed by fewer talk calls (η_talk −0.28 [−0.39, −0.18]). Given a talk call, the span elasticity is −0.11 [−0.16, −0.06], the same in all four regime-III periods tested. Previous-call job, arrivals, rooms and label truncation are rejected. Regime-I span split inconclusive (274 logged replies); full-strength scheduler-wait exposure and the start-placement artifact are excluded. The tertile collapse is withdrawn: synthetic worlds show it cannot tell the clocks apart.
**Fields:** stat mech, dynamics, sociophysics
**Literature:** [Aguilera, Ito & Kolchinsky 2026](../../literature/aguilera-2026-entropy-production-nonequilibrium-maxent.md) (kinetic Ising as the dynamical model). Not in `literature/` (cited from memory, †): Glauber, *J. Math. Phys.* 4, 294 (1963)† (single-spin-flip kinetics, attempt rate); Brown, Barbieri, Ventura, Kass & Frank, *Neural Comput.* 14, 325 (2002)† (time-rescaling: a point process is Poisson in its own intensity clock); Singer & Willett, *Applied Longitudinal Data Analysis* (2003)† (discrete-time hazard models, complementary log-log link).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime; Population N(t); **Exposure (turn read-out)** as implemented by the shared context ledger (a message is read out by the recipient's first call whose context was assembled after the message); Interaction, variant *reply* replaced by the DQ2 reply label (see the Known issue "Mention-based responses are superseded"); Action (turn-merged) only through the ledger's call definition. New named variants proposed here (not edited into DEFINITIONS.md, outside H40's scope): **call clock** (a recipient's model-call count since read-out), **per-call coupling** and **per-hour coupling** (defined under Operational definitions), **exposure-time elasticity η** and **cadence elasticity ε(T)**.
**From:** HH154 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` (with HH187, lags quantized in call cycles, as a secondary check) · **Models:** `physics-models/02-nonequilibrium-ising/` (Glauber attempt rates), `physics-models/09-hawkes/` (response kernels)
**Data inputs (shared tables first):** DQ1 `call_windows`, `context_ledger_items`, `context_ledger_turns`; DQ2 `reply_pairs` (`pair_set = cand`, `parent`, `p_reply`) and `reply_threading/b_meta_ledger` (the call that produced each reply); `chat_core`, `chat_mentions_clean`, `roster`, `calendar`, `period_units`; DQ5 agent-day `white32` / `style_resid_period` vectors (style controls); H29's boundary estimator is *not* used in round 1 (see Notes).

## Standards (2026-10-04)
*Documentation pass against `STANDARDS.md`. No analysis was re-run. H40 has no round-1b section; round 1 already ran on the corrected inputs.*

**Question served:** Q1. The card measures whether coupling runs per recipient model call or per minute.

| Impostor | Relevant? | How it was handled | Status |
| --- | --- | --- | --- |
| Scheduler field | partly | The hazard is per item after its read-out call, on ledger call times, not activity synchrony. Overnight `first_of_day` read-outs are dropped (Data scheme). The pause-timer dose uses waits declared before the message (N1a). | removed |
| Exogenous field (kickoff/goal/operator) | partly | Items are agent-to-agent messages only; human and operator messages are not items. Agent × unit intercepts absorb period-level drives. There is no kickoff-day control. | partly |
| Shared model priors | yes | Lab fixed effects and two DQ5 style PCs in the between-agent slope s (Observables 2); per-call coupling is a lab/style trait (R² 0.25). The tertile collapse (P5) is confounded by family. Close by matching on family before the collapse (R5). | partly |
| Contemporaneous convergence | partly | Risk sets start at the read-out call, so m is in context before any reply counts. DQ2 parents are partly content-selected (axis A). | removed |

**Inputs:** round 1 uses the context ledger (`call_windows`, items, turns), DQ2 replies and DQ5 style vectors; it never reads `activity_bins` (Notes). Still old: the `ment` covariate uses `chat_mentions_clean`, not the leading-@ target. Work, failures and gte are not inputs.

**Two layers:** 30 replication folders (regime I 20, II 3, III 7). Native tests: 4 (`G51` supported; `NE41` mixed; `G18` and `G36` failed).

**Confirm script:** `analysis/confirm.py` exists, frozen and dry-run on the ledger and DQ2 inputs. No re-freeze needed (round-1b synthesis decision 3: frozen and ready).

## Question
Is a recipient's coupling per unit wall time its coupling per model call times its call rate, so that call cadence is a coupling knob and slow-cadence agents are weakly coupled "heavy spins"? Equivalently: does the response to another agent's message run on the recipient's **call clock** (a fixed chance per model call) or on the **wall clock** (a fixed chance per minute, whatever the cadence)?

## Design: two layers (Vivian, 2026-10-04; see `infra/data-quality/QUEUE.md`)
- **Replication:** the common estimator (the call-clock hazard model below) on every eligible goal period (comparable phase-diagram points). Period README role: `replication`.
- **Period-native tests:** four goal periods or NEs whose setup gives special leverage, each with its own observable, null and dated prediction (below). Period README role: `native`.

## Model
**From:** `physics-models/02-nonequilibrium-ising` (kinetic Ising with Glauber single-spin updates at agent-specific attempt rates) and `physics-models/09-hawkes` (the response kernel to a message).

**H40 variant: kinetic Ising on the call clock.** Recipient i updates only at its model calls c = 1, 2, … (attempt times t_c, the ledger's `t_call`). For a message m from sender j that i reads out at call c₁ (the first call assembled after m), each later call c_n (n = 1 is the read-out call) is an update attempt at which i replies to m with probability h_n:

  cloglog h_n = α_i + [n = 1]·(β₁ + η₁ log W) + [n ≥ 2]·(φ log n + ψ log a_n + χ log(1 + b_n) + η log e_n) + δ log(1 + k_n) + ζ·ment + controls,

with W = t_{c₁} − t_m (the wait to read-out), a_n = t_{c_n} − t_m (wall age of m at call n), b_n = newer room messages since m (burial), e_n = t_{c_n} − t_{c_{n−1}} (the wall time call n spans), k_n = new items at call n, ment = m names i. The complementary log-log link makes the wall-clock alternative exact: if i accrues a reply hazard λ per unit wall time and can only act at calls (H08's read-out gating), then h_n = 1 − exp(−λ e_n), i.e. cloglog h_n = log λ + **1**·log e_n.
- **Call clock (H40):** η = 0 and η₁ = 0: each call is one Glauber update with a fixed coupling, however much wall time it spans. The per-hour coupling (wall-time hazard h/e) is then per-call coupling × call rate r = 1/e.
- **Wall clock (rival R1, "attention per hour"):** η = 1: the per-call hazard grows with the time the call spans, so per-hour coupling does not depend on cadence.
- **General:** per-hour coupling ∝ r^(1−η). **ε = 1 − η is the cadence elasticity of the instantaneous per-hour coupling.**
- **Which clock does relevance decay on?** φ (recipient's calls), ψ (wall age), χ (newer messages: the "message clock" of burial). H40 predicts call-count decay in regime III, where every call appends tool output to a persistent context and pushes m back; in regime-I/II chat mode the prompt is rebuilt from recent chat each call, so burial (χ) is the natural clock there.
- **Between agents:** α_i is i's per-call coupling. H40: α_i does not depend on i's call rate r_i (slope s = 0). Rival R1 at the agent level: α_i ∝ −log r_i (s = −1), so all agents have the same per-hour coupling. **Rival R2 (model family / attention trait):** per-hour coupling is set by the agent's family or habits, independent of cadence: lab and style explain the per-hour coupling at least as well as cadence does.
- **Mechanical nuance (worth stating up front).** If each message is read out once and answered (or not) at that call, cadence sets only the *delay*, not the eventual response; per-hour coupling then scales with r only on timescales shorter than the response's lifetime. So the deliverable is horizon-dependent: ε(T), the elasticity of P(reply within T of arrival) to a uniform cadence speed-up, for T = 5, 15, 30 min. Dilution (H18: per-message uptake ∝ k^−0.6) makes slow agents (bigger batches) weaker per message as well, a second route by which cadence sets coupling; the model carries it through δ.

## Data scheme (`scheme/build.py`)
- **Inputs:** `call_windows` (t_call, t_call_lo/hi, start_conf, gap_kind, ctx_mode, talk, first_of_day, pause_s), `context_ledger_turns` (k_new, reset flags, cap_hit), `context_ledger_items` (turn_id = read-out call, message_id, sender, kind, age_s, ment, rank, uncertain, omitted), `reply_pairs` (parent pairs and soft p_reply on `cand` pairs), `b_meta_ledger` (each reply B's call start), `chat_core` (t, room), `roster`, `period_units`, `calendar` holdout flag.
- **Transform:**
  1. Items = agent-sender messages read out by agent recipients (ledger `kind == agent`), non-holdout, read-out call not `first_of_day` (overnight windows), not `omitted` (200-event cap).
  2. Each reply B (DQ2 `parent` pair, A = m, B by recipient i) is mapped to the call that produced it (`b_meta_ledger.s_us` = that call's `t_call`; 98.6% exact matches, else i's latest call starting before t_B). y = 1 at that call.
  3. Risk set per item: i's calls from c₁ while a_n ≤ 30 min (the DQ2 candidate pool reaches back 60 min; 30 min keeps late replies detectable), same PT day, stopping at the reply. Summary calls (CONSOLIDATE, session stop) cannot talk: they are dropped from the risk set and their duration counts toward the next call's e_n.
  4. Rows are aggregated into cells (day × agent-unit × bins of n, a, e, k, b, rank, gap kind, ment, reset-since-read-out, previous-call-talked), keeping the within-cell sums of each log covariate (no midpoint attenuation).
- **Output:** `data/processed/H40-call-clock-coupling/G<NN>/`: `items.parquet` (item rows, codes only, no message ids or text), `cells.parquet` (risk-set cells), `cadence.parquet` (agent × unit call statistics), `au.parquet`; plus `build_summary.parquet`, `results/`, `native/`, `posthoc/`, `synthetic/`, `confirm_dryrun/` and `_provenance.json`. 130 MB (budget 200 MB).
- **Regimes covered:** I, II, III, non-holdout goal periods with ≥ 4 recipients and ≥ 100 agent-to-agent reply parents (34 periods; #10 drops out).

## Operational definitions (written 2026-10-04, before any real-data run)
- **Call rate r_{i,u}:** i's calls per hour of presence in unit u (presence = first call start to last call end, per PT day, summed). Pauses count as presence: a paused agent is a slow spin.
- **Per-call coupling (model-free):** β_i(10) = share of items i replies to within its first 10 calls after read-out. **Per-hour coupling (model-free):** P_i(5 min) = share replied to within 5 min of the message's arrival, divided by 5 min. 10 calls ≈ 5 min at the median regime-III cadence (~130 calls/h), so the two horizons coincide for a typical agent.
- **Per-call coupling (model-based):** α_{i,u} from the hazard model. **Per-hour coupling (model-based):** α_{i,u} + log r_{i,u} (log scale, instantaneous).
- **Exposure-time elasticity η:** the coefficient of log e_n at calls n ≥ 2; η₁ the coefficient of log W at the read-out call. Estimated separately for busy (chained) calls, pause wakes and post-consolidation calls by interacting log e_n with gap kind.
- **Cadence elasticity ε(T):** d log P(reply within T) / d log(speed-up factor), computed from each period's fitted model on its real items by compressing every call interval by a factor c (batch sizes and burial counts scale with the interval) and differencing at c = 0.9 vs 1.1.
- **Reply outcome:** DQ2 primary parent (hard). Sensitivity: soft (maximum p_reply over i's candidate pairs with A = m, counted where ≥ 0.5) and addressing (i's talk call names j; contaminated, used only as a third check).
- **Style controls:** per agent × period, the mean of DQ5 agent-day (`white32` − `style_resid_period`) vectors (the style component that DQ5 removes), reduced to its first two principal components within the period. Family control: `roster.lab`.

## Observables
1. η, η₁ (and by gap kind), φ, ψ, χ, δ per period (replication), with day-block bootstrap CIs (B = 200 refits on reweighted days).
2. Between-agent slope s of α_{i,u} on log r_{i,u} (inverse-variance weighted, unit FE, lab FE, two style PCs), per period and pooled across periods by a random-effects mean (exception (d): hierarchical pooling across periods, reported next to the per-period estimates). *Clarification written before the run:* the primary per-period s uses unit FE only; the controlled version (lab FE + two style PCs) is computed only where ≥ 6 residual degrees of freedom remain (in practice G51 and the larger regime-III periods), and the R2 comparison is made in G51. The bootstrap CI of s propagates the uncertainty of each α by refitting on day-reweighted data.
   The primary η of P1 is the common log e_n coefficient at calls n ≥ 2 (gap-kind and call-mode main effects in the model, no interactions); gap-specific η (busy, long previous call, pause wake, after forced / voluntary consolidation) and the chat-mode η come from the same model with log e_n × gap and × mode interactions.
3. Model-free collapse: cumulative reply curves of the slow, middle and fast cadence tertiles of recipients, in call count and in wall time; the collapse statistic D_call vs D_wall = mean absolute log-ratio between tertile curves at matched horizons (lower = better collapse).
4. Held-out prediction (day-blocked, even/odd days): call-clock model vs wall-clock model (η fixed at 1, ψ carries the decay) on held-out reply times, Δ log-likelihood per item.
5. ε(5), ε(15), ε(30) per period, with bootstrap CIs.
6. Native-test statistics (below).

## Null / baseline
- **Wall-clock null (R1):** η = 1 (offset), the model refitted; the rival for every η test and for the held-out comparison.
- **Agent-level rival (R1′):** s = −1.
- **Family rival (R2):** lab FE + style PCs alone vs log r alone, partial R² for the per-hour coupling across recipients.
- **Permutation null for s:** shuffle r across recipients within unit (1,000 draws).
- **Synthetic calibration:** every estimator is run on replies simulated on the real call schedules under the call clock, the wall clock and a 50/50 mix, at real counts (axis F, below), so the real-data numbers are read against estimator bias.

## Native tests (each with its own observable, null and prediction)
- **N1 · G51 (#51, private roles; 32 agents, call-rate SD 0.81 in log units, the widest spread of cadence).** (a) *Pause-timer dose:* after NE44 (06-11) agents pause on short timers; a message that arrives during a pause is read at the timer wake, so W is set by a timer declared before the message (pre-treatment). Observable η_pause: elasticity of the read-out-call reply hazard to log W among timer-wake read-outs, controlling batch size and rank. (b) *Heavy spins:* between-agent s with 32 agents, lab and style controls, and a pair-level version with sender FE. (c) η per unit (51a–51l).
- **N2 · NE41 (forced consolidation as an exogenous call gap; regime-III non-holdout periods).** A forced consolidation at the 41-turn cap is a summary call of a few minutes whose timing the scaffold sets. Messages arriving during it are read at the next call after a long, exogenous gap. Observable: η at post-forced-consolidation calls (e_n = the consolidation gap), and the ratio of P(reply within 10 calls of read-out) for messages that arrived during the forced consolidation vs during the busy call before it. Confound: the context is erased at the same moment (H08: −18% to pre-erasure senders); the messages themselves are new, so erasure acts on competition, not on m.
- **N3 · G18 (regime I, scheduled chat-mode calls).** In regime I, chat-mode calls are scheduled (start-to-start ≈ 74 s, not message-triggered; DQ1). Their interval jitter is exogenous to any one message. Observable: η within chat-mode calls (busy gap), and the chat-mode vs computer-use contrast in per-call coupling (descriptive: the mode switch changes attention as well as cadence). G18 has the most chat-mode calls of any non-holdout period (8,200).
- **N4 · G36 (NE14 regime switch inside the period, 36a regime II → 36b/36c regime III, plus #35 as extra pre-days).** Within-agent cadence change at a scaffold step. Observable: per agent, the change in per-call coupling α (call clock: unchanged) and in per-hour coupling (call clock: changes by the change in log r). Weak (one pre-day in #36; regime switch changes context structure too); labelled as such.
- **Considered and not used:** NE06 (2025-11-20/25, Gemini one tool call per turn, inside #20): daily call rates of the Gemini agents swing from 37 to 245 per hour on both sides of the change, so there is no usable first stage (checked on cadence only, before any outcome). NE20 and NE44 lie inside the locked holdout (#45, #46 / the NE21+NE23 window): confirmatory only.

## Synthetic validation plan (axis F; `analysis/synthetic.py`)
Replies are simulated on the **real** call schedules and the **real** item rows (message arrivals, read-out calls, batch sizes) of G38a, G51c, G18 and G31, so counts and cadence heterogeneity are the village's. Truth uses call times redrawn uniformly within each call's [t_call_lo, t_call_hi] bounds (re-deriving which call reads each message); estimation uses the ledger's point estimates, so call-start uncertainty is propagated. Scenarios: S1 call clock (η = 0, φ < 0); S2 wall clock (η = 1, ψ < 0); S3 mixed (η = 0.5); S4 call clock with agent couplings correlated with cadence (α_i = 0.5 log r_i; the between-agent slope must read 0.5 and η must stay 0); S5 call clock plus a detection loss that grows with burial (the DQ2 candidate ranking's recency penalty). Base rates are matched to the period's overall reply rate. Pass: η recovered within ±0.15 with ≥ 90% CI coverage in S1–S3; power ≥ 0.9 to reject η = 1 under S1 and η = 0 under S2 per powered period; s recovered within ±0.2 in S4.

### Synthetic validation results (2026-10-04; `analysis/synthetic.py`, `data/processed/H40-call-clock-coupling/results/synthetic_summary.parquet`, figure `figures/synthetic_compact.pdf`)
Real call schedules and real item rows of G38 (regime III, 14 agents), G51c (25 agents), G18 and G31 (regime I); 20 replicates per scenario (10 in G51c); truth on call starts jittered within their bounds, estimation on the ledger's point estimates.

| Scenario (true η) | η̂ mean (SD) across periods | 95% CI coverage | rejects η = 1 / η = 0 | held-out picks call clock | ε(5 min) true → estimated |
| --- | --- | --- | --- | --- | --- |
| S1 call clock (0) | 0.003–0.015 (0.05–0.09) | 0.95–1.0 | 1.00 / ≤ 0.05 | 100% | 0.62–0.72 → 0.61–0.77 |
| S2 wall clock (1) | 0.95–0.98 (0.04–0.07) | 0.90–1.0 | ≤ 0.10 / 1.00 | 0% | 0.33–0.51 → 0.34–0.49 |
| S3 mixed (0.5) | 0.46–0.50 (0.05–0.07) | 0.85–1.0 | 1.00 / 1.00 | 30–80% | 0.45–0.60 → 0.48–0.63 |
| S4 agent couplings ∝ r^0.5 (0) | −0.03–0.01 | 0.90 | 1.00 / ≤ 0.10 | 100% | — |
| S5 burial-dependent detection loss (0) | −0.02–0.03 | 0.85–1.0 | 1.00 / ≤ 0.05 | 100% | — |

- **Pass on every pre-set criterion for η** (bias ≤ 0.05, coverage ≥ 0.85, power 1.00 against the wrong clock per period); φ and ψ are recovered (S1: φ̂ −0.57 to −0.64 vs −0.6, ψ̂ ≈ 0; S2 the reverse).
- **Between-agent slope:** S4 reads 0.40–0.53 (true 0.5), S1 −0.10 to −0.01 (true 0); per-period SD 0.13–0.37, so single periods (8–32 agent-units) cannot separate s = 0 from s = −1 reliably except G51; pooling across periods is needed. S5 pulls s slightly negative in G31 (−0.22 ± 0.23).
- **ε(T)** is recovered within ≈ 0.05. Under the call clock, ε(5) ≈ 0.6–0.7 and ε(30) ≈ 0.45–0.58; under the wall clock read-out gating alone still gives ε(5) ≈ 0.3–0.5 (an agent cannot reply before its next call), so ε is not a clean discriminator on its own; η is.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R1 wall clock (attention per hour, η = 1, s = −1); R2 family / attention trait (per-hour coupling set by lab and style); R3 message clock (relevance decays with newer messages, not calls); reply-at-read-out-only (cadence sets only delay).
**Locked holdout used for confirmation:** none yet. `analysis/confirm.py` (frozen, dry-run, not run) targets NE20 in #45, NE44 in #46, transfer in #45–#47 and #28.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Every variable from shared tables (ledger calls, DQ2 replies); assumptions listed. Not invariant across regimes: regime I behaves differently. DQ2's primary-parent rule undercounts multi-target replies (bias toward dilution). |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Discrete-time cloglog hazard with log-linear clocks; censoring and day ends handled; endogenous cadence addressed only through the pause-timer dose. The tertile collapse (a time-rescaling check) is confounded by family differences (P5 63%). |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Day-blocked held-out: the call clock beats the wall clock in 33/33 periods; in regime I the free-η model sits between. Permutation and meta-regression nulls for s. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | Pause-timer dose η₁ ≈ 0 (G51) and ε(5) > ε(30) (P6) as predicted; collapse (P5) marginal fail; G18 chat-jitter failed. |
| E interventional | predicts the change across a natural experiment | 1 | Quasi-interventions: timer waits set in advance (supported); forced consolidation gaps: no catch-up (mixed, raw ratio failed); NE14 failed; NE20/NE44 holdout not run. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 | Synthetic on the real schedules of G18, G31, G38, G51c with call-start jitter propagated: η bias ≤ 0.05, coverage 0.85–1.0, power 1.0 against the wrong clock; s recovered (0.40–0.53 for 0.5). Real η robust to outcome definition, certain items, jittered starts. |
| G ground truth | agrees with known structure | 1 | Consistent with read-out gating (H08, RE-V1) and with the stateless-call mechanism of the perma-computer-use loop; no external ground truth for cadence effects. |
| H comparative | beats the named rivals | 1 | Beats the wall clock (R1) and the agent-compensation rival (s = −1) in regimes II–III; family/style (R2) explain per-call but not per-hour coupling; the message clock (burial, R3) is a real second clock. In regime I the wall-leaning model wins on η. |
| I transfer | holds in other same-mode periods, including the holdout | 1 | Holds in all 11 regime-II/III periods and 9/9 G51 units; fails in regime I. Holdout not run. |

## Prediction
*Written 2026-10-04 ~06:10 UTC, before running the analysis on real data.*
- **P1 (call clock within agents; replication, primary).** The per-call reply hazard does not grow with the wall time a call spans: pooled η (random-effects over powered periods) has its 95% CI inside [−0.25, 0.25], and per-period η < 0.5 in ≥ 80% of powered periods. *Against:* pooled η ≥ 0.5 (the wall clock carries at least half). Between: mixed.
- **P2 (decay clock).** In regime III, relevance decays with the recipient's calls: φ < 0 with CI below 0 and |φ| > |ψ| in ≥ 2/3 of powered regime-III periods. Regime I/II: descriptive only (burial χ expected to dominate in chat mode).
- **P3 (between agents: per-call coupling invariant, per-hour coupling ∝ call rate).** Pooled s has CI inside [−0.4, 0.4] and excluding −1; model-free: the slope of log β_i(10) on log r_i in [−0.4, 0.4], of log P_i(5 min) on log r_i ≥ 0.5. Cadence explains more between-agent variance in per-hour coupling than lab + style (R2) in G51. *Against:* pooled s CI includes −1 and excludes 0 (agents compensate), or lab + style beat cadence.
- **P4 (held-out adequacy).** On odd days, the call-clock model fitted on even days predicts reply times better (Δ log-lik per item > 0) than the wall-clock model in ≥ 2/3 of powered periods.
- **P5 (collapse).** Cadence tertiles' reply curves collapse better in call count than in wall time: D_call < D_wall in ≥ 2/3 of powered periods.
- **P6 (operator statement).** In regime III, ε(5 min) ∈ [0.5, 1.0] and ε(30 min) < ε(5 min): a 2× faster cadence raises 5-min coupling by roughly 40–100%, with a smaller gain at 30 min.
- **N1 (G51).** (a) η_pause CI inside [−0.3, 0.3]; the wall clock predicts ≈ 1. (b) s CI inside [−0.4, 0.4]; the slowest cadence quintile's per-hour coupling ≤ 0.5× the fastest quintile's while its per-call coupling is within 0.67–1.5×. (c) η < 0.5 in ≥ 80% of units with ≥ 2 days.
- **N2 (NE41).** η at post-forced-consolidation calls CI inside [−0.3, 0.3] (no catch-up burst); the 10-call reply ratio (arrived during the forced consolidation vs during the call before) lies in [0.75, 1.33].
- **N3 (G18).** η within scheduled chat-mode calls CI inside [−0.3, 0.3]. No prediction for the chat vs computer-use contrast (descriptive).
- **N4 (G36, NE14).** Across the switch, the within-agent change in per-call coupling is smaller in magnitude than the change in log call rate (|Δα| < |Δ log r|) for the median agent. Weak test.
- **Per-period verdict rule (replication folders; written 2026-10-04 ~07:25 UTC, after G37, G02 and G03 had come out, before any other period):** *supported* if η's 95% CI lies below 0.5 and the held-out call-clock model beats the wall-clock model (Δ log-lik > 0); *failed* if η's CI lies above 0.5, or η ≥ 0.5 with Δ log-lik ≤ 0; *mixed* otherwise; *n/a* if η's SE > 0.5. The CI uses the larger of the day-bootstrap and model SEs (the day bootstrap is degenerate in periods of 2–4 days; found on G37, the first run). The between-agent slope s and the collapse are reported per period but do not enter the verdict (≤ 18 agent-units per period outside G51; synthetic SD of s ≈ 0.2–0.35).
- **Prior (stated so the outcome can be scored against it):** about 65% that P1 holds (LLM calls are stateless decisions given context, but agents in deep tool loops may talk less per call), 50% for P3 (fast cadence often means short tool calls during focused work, which may lower per-call talk), 60% for P2.

## Amendments (dated; what had been seen)
- **A1 (2026-10-04 ~07:15 UTC, after the first real-data run, G37 only, a smoke test).** (i) CIs use the larger of the day-bootstrap and model SEs: G37 has 3 days, and its day bootstrap gave agent intercepts with SE 0.06 from 16 replies. (ii) The between-agent slope s and the model-free slopes are estimated by a random-effects meta-regression over agent-units (Paule–Mandel τ², unit FE, t-based CI), because a bootstrap of intercepts alone ignores real agent-to-agent scatter (G37: s CI ±0.12 → ±0.96). Estimator definitions are unchanged.
- **A2 (~07:20 UTC, from the synthetic run, before the replication run).** Held-out log-likelihood is evaluated only for agent-units with ≥ 3 replies in the training fold. One-day units (e.g. 38c) have no training data in one fold, and their zero intercepts made the held-out comparison favour the call clock even in the wall-clock synthetic (fixed; the synthetic was rerun).
- **A3 (~07:45 UTC, machine load ~140).** Day-bootstrap refits B = 100 per period (B = 40 in G51; G51 has 45 days) instead of 200; the model SE remains a floor.
- **A4.** 33 eligible periods (#7 and #10 have 99 and 60 unique agent-to-agent reply pairs, < 100), not 34.

## Results by goal period
G18, G36 and G51 are native (their verdict is the native test's; G36's replication η passes). Replication verdicts use the rule under Prediction.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G02](goalperiod-subhypotheses/G02/README.md) | replication | mixed | reg I; 199 replies; η +0.62 ± 0.19; φ/ψ -0.35/-0.36; s -0.32; ε5 0.28 |
| [G03](goalperiod-subhypotheses/G03/README.md) | replication | failed | reg I; 502 replies; η +0.90 ± 0.15; φ/ψ -0.66/-0.46; s -2.05; ε5 0.32 |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | mixed | reg I; 1922 replies; η +0.59 ± 0.08; φ/ψ -0.38/-0.45; s +0.05; ε5 0.35 |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | mixed | reg I; 299 replies; η +0.46 ± 0.18; φ/ψ -0.37/-0.65; s -1.64; ε5 0.47 |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | mixed | reg I; 370 replies; η +0.43 ± 0.17; φ/ψ -0.15/-0.32; s -0.59; ε5 0.48 |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | mixed | reg I; 374 replies; η +0.50 ± 0.12; φ/ψ +0.06/-0.71; s -2.09; ε5 0.73 |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | mixed | reg I; 436 replies; η +0.62 ± 0.17; φ/ψ -0.09/-0.57; s -0.48; ε5 0.63 |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication | failed | reg I; 910 replies; η +0.82 ± 0.11; φ/ψ -0.47/-0.45; s -0.19; ε5 0.46 |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | supported | reg I; 915 replies; η +0.19 ± 0.15; φ/ψ -0.50/-0.21; s -0.35; ε5 0.62 |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | mixed | reg I; 277 replies; η +0.29 ± 0.16; φ/ψ -0.41/-0.30; s +0.54; ε5 0.60 |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | mixed | reg I; 363 replies; η +0.66 ± 0.14; φ/ψ -0.29/-0.58; s -1.34; ε5 0.69 |
| [G18](goalperiod-subhypotheses/G18/README.md) | native | failed | reg I; 2276 replies; η +0.75 ± 0.06; φ/ψ -0.43/-0.45; s +0.49; ε5 0.37 |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | failed | reg I; 1629 replies; η +0.81 ± 0.12; φ/ψ -0.15/-0.56; s -0.24; ε5 0.47 |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | mixed | reg I; 1175 replies; η +0.68 ± 0.09; φ/ψ -0.03/-0.55; s -0.08; ε5 0.60 |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | mixed | reg I; 459 replies; η +0.59 ± 0.17; φ/ψ +0.17/-0.75; s -0.36; ε5 0.73 |
| [G23](goalperiod-subhypotheses/G23/README.md) | replication | supported | reg I; 292 replies; η -0.16 ± 0.17; φ/ψ +0.29/-0.41; s +0.20; ε5 0.93 |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | mixed | reg I; 305 replies; η +0.24 ± 0.18; φ/ψ -0.52/-0.45; s -0.65; ε5 0.50 |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | supported | reg I; 952 replies; η +0.22 ± 0.13; φ/ψ -0.59/+0.01; s -0.40; ε5 0.50 |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | mixed | reg I; 785 replies; η +0.58 ± 0.09; φ/ψ -0.38/-0.46; s +0.39; ε5 0.57 |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | mixed | reg I; 1077 replies; η +0.43 ± 0.07; φ/ψ -0.06/-0.74; s +0.07; ε5 0.74 |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | mixed | reg I; 792 replies; η +0.42 ± 0.10; φ/ψ +0.30/-0.85; s -0.91; ε5 0.87 |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | supported | reg I; 865 replies; η +0.28 ± 0.10; φ/ψ -0.12/-0.38; s -0.28; ε5 0.72 |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | supported | reg II; 728 replies; η -0.05 ± 0.09; φ/ψ -0.36/-0.20; s +0.78; ε5 0.57 |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | supported | reg II; 873 replies; η +0.02 ± 0.09; φ/ψ -0.01/-0.49; s +0.81; ε5 0.74 |
| [G36](goalperiod-subhypotheses/G36/README.md) | native | failed | reg II; 594 replies; η +0.08 ± 0.15; φ/ψ -0.28/-0.54; s -0.22; ε5 0.56 |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | supported | reg III; 393 replies; η -0.19 ± 0.19; φ/ψ -0.72/-0.39; s -0.12; ε5 0.56 |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | supported | reg III; 1625 replies; η -0.57 ± 0.10; φ/ψ -0.76/+0.02; s +0.09; ε5 0.72 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | supported | reg III; 127 replies; η -0.05 ± 0.23; φ/ψ +0.23/-0.72; s -0.67; ε5 0.80 |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | supported | reg III; 516 replies; η -0.06 ± 0.12; φ/ψ -0.24/-0.39; s +0.26; ε5 0.71 |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | supported | reg III; 1014 replies; η -0.05 ± 0.09; φ/ψ -0.67/-0.14; s +0.80; ε5 0.50 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | supported | reg III; 503 replies; η +0.04 ± 0.13; φ/ψ -0.56/-0.29; s -1.41; ε5 0.42 |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | supported | reg III; 1084 replies; η -0.34 ± 0.13; φ/ψ -0.62/-0.04; s -0.53; ε5 0.65 |
| [G51](goalperiod-subhypotheses/G51/README.md) | native | supported | reg III; 18352 replies; η -0.00 ± 0.05; φ/ψ -0.80/-0.03; s +0.11; ε5 0.40 |
| [NE41](goalperiod-subhypotheses/NE41/README.md) | native | mixed | no catch-up after forced erasure: read-out × 0.44 [0.37, 0.54], η₁ −0.09 [−0.20, +0.01]; A/B ratio 1.86 failed its band |

## Results
### Exploratory round 1 (2026-10-04; 33 non-holdout periods, 4 native tests; `analysis/replication.py`, `native.py`, `posthoc_conf.py`, `summarize.py`)
Numbers: `data/processed/H40-call-clock-coupling/results/summary.json`, `replication_table.parquet`, `native/*.json`. Figures: `figures/summary_obs.pdf` (η per period; G51 heavy spins), `figures/eta_by_gap.pdf`, `figures/synthetic_compact.pdf`.

**Outcome vs prediction**
| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1 pooled η in [−0.25, 0.25]; η < 0.5 in ≥ 80% of powered periods | pooled +0.30 [+0.17, +0.43] (τ 0.36); 21/33 below 0.5. By regime: I +0.51 [+0.41, +0.61]; II −0.01 [−0.12, +0.11]; III −0.16 [−0.32, +0.01] | **failed overall; supported in II–III** |
| P2 regime III: φ < 0 and \|φ\| > \|ψ\| in ≥ 2/3 | 6/8; φ −0.60 [−0.74, −0.47], ψ −0.19 [−0.31, −0.07], χ −0.72 | supported |
| P3 pooled s in [−0.4, 0.4], excludes −1; model-free per-call slope in [−0.4, 0.4]; per-hour slope ≥ 0.5; cadence beats lab + style (G51) | s −0.12 [−0.28, +0.04]; per-call +0.14 [−0.17, +0.45]; per-hour +0.32 [−0.02, +0.66] (III +0.74 [+0.35, +1.13]; I −0.00); R² 0.50 vs 0.33 | supported, except per-hour scaling in regime I |
| P4 held-out call > wall in ≥ 2/3 | 33/33 | supported (the wall model is the strict η = 1 rival) |
| P5 collapse better in calls in ≥ 2/3 | 21/33 (64%) | failed (marginal; tertiles also differ in family) |
| P6 regime III ε(5) in [0.5, 1.0], ε(30) < ε(5) | 0.57 [0.36, 0.78]; 0.47 [0.35, 0.60] | supported |
| N1 G51 (pause dose; heavy spins; units) | η₁,pause −0.03 [−0.14, +0.08]; s +0.11 [−0.03, +0.25]; hour ratio 0.12; per-call ratio 0.87 model / 0.18 model-free; 9/9 units | supported (model-free per-call ratio outside band) |
| N2 NE41 | η at later post-erasure calls +0.06 [−0.35, +0.47] (too wide); no catch-up (η₁ −0.09, level × 0.44); A/B 1.86 [1.50, 2.31] | mixed |
| N3 G18 chat jitter η in [−0.3, 0.3] | +0.81 [+0.68, +0.95] | failed |
| N4 G36 NE14 \|Δα\| < \|Δ log r\| | 1/11 agents | failed |

**What it means.**
1. *Which clock.* In the perma-computer-use loop (regimes II–III) each model call is one Glauber update with a fixed reply coupling: the hazard per call is independent of how much wall time the call spans, including spans set in advance by pause timers. Long tool calls even carry slightly less hazard (η long previous call −0.47 [−0.65, −0.28] in III). In the regime-I chat scaffold the hazard per scheduled chat call grows with its span (η ≈ 0.6, chat calls ≈ 0.8 in G18), so time, not calls, carries part of the coupling there. Post hoc checks rule out the two artifacts I could test: latency-placed start times (logged Gemini chat calls give the same sign in #24–#31) and unlogged calls hidden in long gaps (restricting to spans < 128 s leaves η unchanged). η declines through regime I (≈ 0.6–0.9 in #3–#21, ≈ 0.2–0.4 in #23–#31) and reaches ≈ 0 at the regime II boundary.
2. *Heavy spins.* Per-call coupling (at fixed batch and burial) is an agent's family/style trait and is flat in cadence. Per-hour coupling is per-call coupling × call rate, so in G51 cadence explains half of who is coupled to whom in wall time. Slow agents' calls also face bigger, more buried batches (read-out rank −0.60 per log rank; χ −0.51), which lowers their model-free per-call uptake: dilution and burial are the routes by which cadence acts beyond the attempt rate.
3. *Operator statement (regime III).* ε(5 min) = 0.57 [0.36, 0.78] pooled (G51 0.40 [0.37, 0.45]); ε(30 min) = 0.47 [0.35, 0.60] (G51 0.27). Halving every call interval of an agent raises the chance it answers a message within 5 min by about 50% (G51 32%), within 30 min by about 40% (G51 21%). Long horizons gain less because relevance decays per call. The model counterfactual is smaller than the cross-sectional association (G51 slope 1.0), which also carries composition differences between fast and slow agents. Synthetic: under a pure wall clock read-out gating alone still gives ε(5) ≈ 0.3–0.5, so ε is the operational number and η the mechanism.
4. *Erasure gaps* (NE41): no catch-up after a forced consolidation; the first post-erasure read-out answers 56% less than an ordinary read-out with the same batch (re-orientation, cf. H39/H15).
5. *Consistent with RE-V1* (read-out gating holds in every regime): gating says *when* a message can first be answered; H40 adds that after read-out, the hazard is per call in regimes II–III and partly per minute in regime I.

## Confirmatory predictions (C-*): for the locked holdout, frozen 2026-10-04 after round 1, not run (`analysis/confirm.py`)
- **C1 (NE20, #45, 06-03, one tool call per turn for Anthropic):** first stage |DiD in log call rate (Anthropic − others)| ≥ 0.10; otherwise C2–C3 are not scored.
- **C2:** DiD in per-call coupling α within |0.5| with CI containing 0.
- **C3:** DiD in log per-hour coupling P(5 min) has the sign of the first stage and its CI contains 0.57 × the first stage (ε(5), regime III).
- **C4 (NE44, #46, 06-11; confounded with the 200-event cap):** median read-out wait of pause-wake items falls by ≥ 20%.
- **C5:** the per-call reply hazard at wake read-outs does not change (|Δα| ≤ 0.5, CI contains 0) while the 5-min coupling of pause-wake items rises.
- **C6 (transfer):** η's CI upper bound < 0.5 in #45, #46, #47; #28 (regime I) descriptive, expected η > 0.
- Dry run on stand-ins (#44 for NE20, 51c split at 07-13 for NE44, #38/#40/#19 for transfer): code path runs; stand-in η reproduces the replication values (−0.57, −0.06, +0.81). Reuse: #45–#50 are targeted by unrun H04, H30 and H35 scripts (activity responses to nudges); H40's statistic (reply hazard on the call clock, DQ2 labels) differs. Disclose in LOG.md when run.

## Round 2 redirects
**What the direction is really after:** a measured coupling-per-call that an operator can multiply by cadence, and an explanation of why the regime-I chat scaffold does not obey it.
- **H40-R1. Why regime I is not a call clock.** Split the chat-call span into generation time (logged `dur_api_s` for Gemini) and scheduler wait; test whether long generations (engaged agents) carry the positive η (endogenous cadence) or the scheduler wait does.
- **H40-R2. Content channel.** Rebuild H29's boundary pull on the ledger and test per-call invariance of content pull (φ vs ψ vs burial) as for replies.
- **H40-R3. Lags in call cycles (HH187).** Pairwise lagged content correlations with lags in recipient calls; quantization should hold in regimes II–III only.
- **H40-R4. Run confirm.py** on NE20/NE44 and the transfer periods; NE20 is the cleanest cadence intervention in the dataset.
- **H40-R5. Fix the collapse test** by matching agents on per-call coupling (family) before comparing cadence tertiles, and add multi-parent reply labels (DQ2 holds only the primary parent).
- **H40-R6. Negative η in G38 and G44** (coordinator, 2026-10-04): η = −0.57 [−0.77, −0.38] and −0.34 [−0.60, −0.08] sit significantly below the call clock, yet the period rule labels them supported. Longer calls carrying *less* reply hazard is neither clock; candidates are burial (long calls receive bigger batches) or long calls being work-absorbed. Check with the batch-size and gap-type splits (`eta_by_gap`) before calling regime III a pure call clock.

## Round 2 (2026-10-05): R6 negative η, R1 regime-I span split, R5 collapse fix
### Pre-registration (written 2026-10-05 02:45–03:10 UTC, before any round-2 statistic on real data)
**Question served:** Q1 (what couples agents: per call or per minute), with Q5 (cadence as an operator knob).

**Already seen before writing this (disclosed):** all round-1 outputs, including η by gap kind (G38 busy −0.62, G44 busy −0.33), the round-1 sensitivity rows (addressing outcome: G38 −0.18, G44 −0.32; jittered starts G38 −0.35/−0.37), and the collapse table. New covariate-only descriptives (no outcome): G38 busy spans have median 12 s (p90 28 s, p99 47 s; G44 17 / 36 / 53 s); 91–94% of busy calls follow a `cu_action` call and 2–9% a talk call; Gemini agents have logged starts (2 of 14 recipients in G38, 3 of 18 in G44); regime-I chat-mode calls with logged starts on both sides exist only in #24–#31 (366–892 calls per period); DQ2 labels 84% of rank-1 candidates but only 16% / 6% of rank-2 / rank-3 candidates (regime I), and 4–11% of replying messages carry more than one labelled parent.

**Common estimator.** The round-1 hazard model (SPEC_FULL: agent-unit FE, η, η₁, φ, ψ, χ, δ, gap and mode terms) refitted on risk-set cells built from the round-1 items with extra keys. **CIs:** the larger of the model SE and a 1-hour block bootstrap SE (blocks = PT day × hour of the message's arrival, B = 50; H67: day blocks with ≤ 5 days are anti-conservative). Δη between a diagnostic and the base model uses paired bootstrap draws. Reserved data never enter (round-1 items are built with `holdout_mask` already).

**R6 · Why η < 0 in G38 and G44.** Targets G38 and G44; contrast periods G41 and G40 (regime III, η ≈ 0) get the same diagnostics, descriptive only. Each mechanism names the pattern it predicts. "Moves η toward 0" means |η_diag| ≤ 0.5 |η_base| **and** the paired Δη CI excludes 0.

| Mechanism | Diagnostic | Pattern it predicts |
| --- | --- | --- |
| **M1 call-type composition** (long calls are tool work that crowds out talk) | **D1 talk split:** the same risk rows, two models: (i) talk hazard, y = call n posts any chat message; (ii) reply given talk, rows where call n talks, y = reply to m | η_talk < 0 (CI below 0) and reply-given-talk η_rep\|talk moves toward 0 (\|η_rep\|talk\| ≤ 0.5 \|η_base\|, CI includes 0) |
| **M1b work absorption** (the previous call's job type) | **D2:** add the previous call's kind (talk / search / room move / other vs cu_action), its action-row count (log), failure flag and write flag (`calls`) | η moves toward 0; the work terms are negative |
| **M2 selection on arrivals** (what arrives during a long call competes with m, or the thread has moved on) | **D3:** add at call n log(1 + new items naming i), log(1 + new human items), any new agent item, and log(1 + third-party DQ2 replies to m posted before call n) | η moves toward 0; the third-party term is negative |
| **M3 room structure / agent-day state** | **D4:** replace agent-unit FE by agent × day × room FE (room at the read-out call) | η moves toward 0 |
| **M4 reply-label truncation** (long spans bring new arrivals that push m out of DQ2's top-3 candidates) | **D5:** η on rows with no new item at call n (k_n = 0). The addressing-outcome η (round 1) is reported but is not a fresh test | \|η(k_n = 0)\| ≤ 0.5 \|η_base\| with CI including 0 |
| (descriptive) generation vs tool time | **D6:** Gemini recipients only: log e_n split into log (API time of call n−1) and log (rest of the span) | none (2–3 agents per period) |
| (descriptive) shape | **D0:** η as a step function over e_n bins | none |

- **Kill rule (R6):** if no diagnostic moves η toward 0 in either target period **and** η_rep\|talk has its CI below 0 in both, the negative wall term is unexplained: regime III is then reported as "no wall clock (η ≤ 0)", not as an exact call clock, and the regime-III claim loses its "η = 0" wording.
- **Prior:** M1 50%, M4 15%, M2 15%, M3 10%, unexplained 10%.

**R1 · Regime I: generation time or scheduler wait.** Sample: regime-I periods with logged chat-mode starts (#24, #25, #26, #27, #30, #31), Gemini recipients, rows at calls n ≥ 2 where calls n and n−1 are both chat-mode with logged starts. Split the span e_n = busy_{n−1} + wait_n, busy = t_log − t_call of call n−1 (generation plus tool time, measured), wait = t_call,n − t_log,n−1 (the scheduler's wait). Model: replace η log e by η_busy log busy + η_wait log wait. Per-period fits and a random-effects mean (exception (d): too few replies per period; per-period estimates reported next to it).
- **Engagement (H40-consistent):** pooled η_wait CI inside [−0.25, 0.25] and pooled η_busy CI above 0.
- **Exposure (wall-clock rival):** pooled η_wait ≥ 0.3 with CI above 0. For small changes the wall clock predicts η_wait / η_busy ≈ wait share / busy share of the span (> 1 here).
- **Precondition:** the pooled total η on this subset has CI above 0; otherwise the split is moot and R1 is reported as "the positive η is absent where starts are measured".
- **R1c · start-placement artifact.** On the same Gemini rows, refit η with t_call replaced by the latency placement that non-Gemini chat calls get (t_first minus the agent's median latency on logged chat calls). Placement puts a call's own generation time into its span, and reply calls generate longer. **Prediction:** η_placed − η_logged ≥ 0.2 (paired CI above 0), so part of regime I's η in agents without logged starts is a placement artifact. No effect if the difference CI includes 0.
- **Kill rule (R1):** exposure holds → regime I keeps "partly wall clock" with exposure as the cause. Engagement holds → regime I is a call clock with an endogenous span. Synthetic power < 0.8 to tell η_wait = 0.5 from 0 → R1 inconclusive.
- **Prior:** engagement 40%, exposure 25%, inconclusive 35%; R1c effect 50%.

**R5 · Collapse with matched per-call coupling.** For every round-1 period, recompute the fast-vs-slow tertile collapse (D_call vs D_wall, same grids) with item weights that give every cadence tertile the period's overall mix of (a) **lab** (primary; labs absent from a tertile are dropped from all tertiles) and (b) **bins of α̂** (secondary; terciles of the round-1 agent-unit intercepts from the η-free model). Outcomes: DQ2 parent (primary) and the multi-parent label (every labelled candidate with p_reply ≥ 0.5, the round-1 `any_tid`; secondary).
- **P5′ (regimes II–III):** lab-balanced D_call < D_wall in ≥ 2/3 of the 11 regime-II/III periods. Regime I: reported, no directional prediction.
- **Validity rule (decided now):** synthetic worlds on real schedules with the real fitted coefficients and real agent intercepts, under the call clock (η = ψ = 0) and the wall clock (η = 1, φ = 0). If the lab-balanced collapse picks the call clock in < 80% of call-clock worlds, the collapse also measures burial and dilution (slow agents face bigger batches per call), and P5/P5′ are withdrawn as uninformative, not scored as failed.
- **Multi-parent bias (no new labels exist):** DQ2 has no multi-label sample. The multi-parent outcome adds only labelled secondary candidates. Rank-2/3 candidates are mostly unlabelled, so replies to second and third parents stay undercounted. I quantify the bias by DQ2 pool size per cadence tertile: if slow agents' reply messages have larger pools, the bias lowers slow agents' per-call curves and inflates D_call (against the call clock).
- **Prior:** 55% that P5′ passes; 30% that the validity rule withdraws it.

**Synthetic validation (before real data, on the real call schedules and real item rows; `analysis/round2.py --synthetic`):**
- R6: S1 (call clock, η = 0) must give η̂ within ±0.15 under every diagnostic (controls do not create or remove η); S6 (call clock acting only at the real talk calls) must give η̂_rep\|talk within ±0.15 of 0; S7 (as S6 with a true −0.5 per log span given talk) must give η̂_rep\|talk within ±0.15 of −0.5; S8 (call clock plus detection loss that grows with new arrivals) must give η̂(k_n = 0) within ±0.15 of 0. Periods G38 and G44.
- R1: on the pooled Gemini rows, S-eng (η_busy 0.6, η_wait 0) and S-wall (η = 1 on the total span) must be told apart: power ≥ 0.8 for the engagement rule under S-eng and for the exposure rule under S-wall.
- R5: as in the validity rule, on G18, G31, G38, G41 and G51c.

### Synthetic validation results (2026-10-05 ~03:40 UTC, before any round-2 real-data statistic; `analysis/round2.py r6syn / r1syn / r5syn`, `data/processed/H40-call-clock-coupling/round2/*syn*.parquet`)
Truth on call starts jittered within their bounds (R6, R5) or on logged starts (R1); estimation on the ledger's point estimates; real items, real call schedules, real round-1 coefficients and agent intercepts.

| World (truth) | Statistic | G38 mean (SD) | G44 mean (SD) | Pass? |
| --- | --- | --- | --- | --- |
| S1 call clock (η = 0) | η̂ base / D2 / D3 / D4 / D5 | +0.01 / +0.01 / +0.00 / +0.00 / +0.01 (≈ 0.05) | −0.01 / −0.01 / −0.01 / −0.01 / −0.02 (0.08–0.10) | yes: controls neither create nor remove η |
| S6 call clock only at real talk calls | η̂ reply-given-talk; η̂ base | +0.01 (0.06); **−0.26** | +0.00 (0.04); **−0.13** | yes |
| S7 as S6, −0.5 per log span given talk | η̂ reply-given-talk | −0.45 (0.04) | −0.43 (0.04) | yes (attenuated by ≈ 0.06; coverage 0.9 / 0.5) |
| S8 call clock + detection loss at ≥ 2 new items | η̂ base; η̂ D5 | +0.02; −0.00 | −0.03; −0.03 | yes (D5 unbiased); this loss does not create η < 0 because δ absorbs it |

- **R6 by-product (not a test):** the real talk-call schedule alone gives η̂ = −0.26 (G38) and −0.13 (G44) under a pure call clock, because talk calls follow shorter spans. So call-type composition can produce part of the negative η.
- **R1 (6 periods pooled, 20 worlds each):** exposure rule (η̂_wait ≥ 0.3, CI above 0): power **1.00** under S-wall (η̂_wait 0.84), size 0.05 under S-call, 0.00 under S-eng. Engagement rule: power **0.00** under S-eng: the pooled η̂_wait CI half-width is 0.34, wider than the ±0.25 band. η̂_busy recovers 0.57 for 0.6 (CI above 0 in 75% of worlds). Under S-eng the total η̂ is only +0.17, and its CI is above 0 in 5% of worlds.
- **R5 (10 worlds per clock):** the collapse statistic does not tell the clocks apart. The raw D_call < D_wall holds in 0.7–1.0 of call-clock worlds and in 0.5–1.0 of wall-clock worlds (G18 1.0 / 1.0; G51c 1.0 / 1.0; G41 1.0 / 0.9). The lab-balanced version picks the call clock in 1.0 (G18, G51c), 0.2 (G31, G41) and 0.0 (G38) of call-clock worlds.

**Amendment A5 (2026-10-05 ~03:45 UTC, from the synthetic results above, before any round-2 real-data statistic):**
- **R5 withdrawn as uninformative** by the pre-set validity rule (< 80% in 3/5 periods). The tertile collapse measures burial, dilution and agent heterogeneity, not the clock. P5 (round 1, 21/33) is re-scored as uninformative, not failed. The real-data R5 run is kept as descriptive only, for the multi-parent bias (pool sizes by tertile).
- **R1: the engagement branch is unpowered by design** (power 0.00; a looser band, η_wait upper bound < 0.5 with η_busy > 0, reaches only 0.55, so I do not adopt it). Under the pre-set kill rule, a non-exposure result is reported as "exposure excluded; engagement vs call clock inconclusive". The exposure branch stays decisive (power 1.00, size 0.05).
- **R6:** unchanged. Every diagnostic passed its synthetic check.

### Results (2026-10-05, non-reserved data only; `analysis/round2.py r6 / r1 / r5`, figure `figures/round2_summary.pdf`)
Numbers: `data/processed/H40-call-clock-coupling/round2/r6_G38.json`, `r6_G44.json`, `r6_G40.json`, `r6_G41.json`, `r1.json`, `r5.json`. CIs: larger of model SE and 1-h block bootstrap SE (B = 50; B = 30 for G40/G41). Per-period rows: `per_period_estimates` (statistics `eta_talk_span_elasticity`, `eta_reply_given_talk`, `eta_busy_prev_call`, `eta_scheduler_wait`, `eta_placement_artifact`).

**R6: the talk split (D1) and the rejected mechanisms (D2–D5).**

| Period | base η | η_talk (talk propensity) | η_rep\|talk (reply given talk) | Δη (D1 vs base) | D2 / D3 / D4 / D5 η |
| --- | --- | --- | --- | --- | --- |
| G38 (target) | −0.57 [−0.67, −0.46] | **−0.33 [−0.44, −0.22]** | −0.11 [−0.19, −0.03] | +0.46 [+0.36, +0.56] | −0.58 / −0.58 / −0.55 / −0.59 |
| G44 (target) | −0.34 [−0.44, −0.24] | **−0.22 [−0.36, −0.07]** | −0.09 [−0.17, −0.02] | +0.25 [+0.14, +0.35] | −0.36 / −0.34 / −0.34 / −0.38 |
| G41 (contrast) | −0.04 [−0.18, +0.09] | +0.08 [−0.07, +0.23] | −0.16 [−0.31, −0.01] | — | −0.19 / −0.04 / −0.08 / −0.10 |
| G40 (contrast) | −0.04 [−0.27, +0.20] | +0.05 [−0.05, +0.15] | −0.10 [−0.33, +0.12] | — | −0.07 / −0.02 / +0.00 / +0.07 |
| Random-effects mean | targets −0.45 [−0.68, −0.23] | targets −0.28 [−0.39, −0.18]; contrast +0.06 [−0.02, +0.14] | **all four −0.11 [−0.16, −0.06], τ = 0, Q = 0.58** | | |

| Mechanism | Predicted pattern | Observed | Verdict |
| --- | --- | --- | --- |
| M1 call-type composition | η_talk < 0; η_rep\|talk ≤ 0.5 \|η_base\| with CI including 0 | η_talk < 0 in both; η_rep\|talk is 19% (G38) and 26% (G44) of base, Δη CI above 0; but its CI excludes 0 by 0.02–0.03 | **mostly supported** (strict pattern missed on the CI clause) |
| M1b work absorption (previous-call job) | η moves toward 0 | Δη −0.01 / −0.02 | rejected |
| M2 selection on arrivals | η moves toward 0; third-party term < 0 | Δη −0.01 / −0.02; third-party term **positive** (+0.86, +0.32) | rejected |
| M3 room / agent-day state | η moves toward 0 | Δη +0.02 / −0.00 | rejected |
| M4 label truncation | \|η(k_n = 0)\| ≤ 0.5 \|η_base\| | −0.59 / −0.38 | rejected |
| Kill rule | no diagnostic moves η and η_rep\|talk < 0 in both | D1 moves η toward 0 in both | **not triggered** |

- **What it means.** In every regime-III period tested, a talk call answers a pending message with nearly the same hazard whatever wall time the previous call spanned: η_rep\|talk = −0.11 per log span, the same in all four periods (doubling the span lowers it by 7%). What differs between periods is the talk channel. In G38 and G44 a long tool call is followed by fewer talk calls (η_talk −0.28). In G40 and G41 it is not (+0.06). That difference explains about 3/4 of the negative η and all of the between-period spread (Q 34 in talk vs 0.6 given talk). The real talk schedule alone gives η̂ = −0.26 / −0.13 under a pure call clock (S6), which matches this.
- **D6 (descriptive, Gemini, 2–3 agents).** API generation time of the previous call carries a positive elasticity (G44 +0.56 [+0.24, +0.88], G38 +0.38 [−0.04, +0.81]); the rest of the span (tool execution) carries the negative one (G44 −1.05 [−1.25, −0.85], G38 −0.33, G41 −0.44). Long thinking goes with replying; long tool jobs go with not talking.
- **D0 shape (G38).** The negative slope holds across the span bins (8–16 s −0.41, 16–32 s −0.78, 32–64 s −0.58 vs < 8 s); it is not a tail effect.
- **Caveat.** Conditioning on talk conditions on a variable that m can cause (H50: a read message turns the next call into talk). S6 shows the split is unbiased when talk is exogenous; it is not tested when m causes talk.

**R1: regime-I span split (Gemini recipients, logged starts, #24–#31).** 274 replies at qualifying calls (G24: 2; G25 61, G26 95, G27 67, G30 33, G31 16). Busy time of the previous call is a median 12–14% of the span (median span 54–90 s, busy 8–12 s, wait 45–77 s).

| Statistic | Pooled (random effects, 6 periods) | Pre-set rule | Verdict |
| --- | --- | --- | --- |
| Precondition: total η on this subset | +0.30 [−0.14, +0.73] | CI above 0 | **failed** (underpowered: CI includes both 0 and the regime-I value +0.51) |
| η_busy (generation + tool time of call n−1) | +0.28 [−0.11, +0.67] | engagement: > 0 | not shown |
| η_wait (scheduler wait) | +0.18 [−0.17, +0.53] | exposure: ≥ 0.3 with CI above 0 | **exposure not supported**; full-strength exposure (η_wait ≈ 0.84 in S-wall) is excluded |
| R1c: η_placed − η_logged | +0.04 [−0.06, +0.13] | ≥ 0.2 | **failed**: latency placement does not inflate η |

- R1 is **inconclusive** under the pre-set rules (precondition failed; engagement branch unpowered, A5). Two things are learned: a wall clock acting through the scheduler's wait at full strength is excluded, and the start-placement artifact is excluded, so regime I's η in non-Gemini agents is not a timing artifact. The cause of regime I's η stays open.

**R5: collapse (withdrawn by A5; descriptive).** Lab-balanced D_call < D_wall in 8/10 regime-II/III periods with common lab support (G37 has none) and 4/12 regime-I periods; α̂-balanced 8/10 and 10/14 (raw, as in round 1: 8/11 and 13/22). These numbers do not score P5 (the synthetic shows the statistic cannot tell the clocks apart). **Multi-parent bias:** DQ2 pools (visible candidates per reply message) are larger for the slowest cadence tertile in several regime-II/III periods (G35 36.5 vs 26.6 for the fastest; G41 35.8 vs 28.4; G42 29.4 vs 18.7), equal (≈ 38) in regime I. With only rank-1 candidates mostly labelled, slow agents' secondary replies are undercounted more, which lowers their per-call curves (bias against the call clock in any per-call comparison across cadence). The multi-parent outcome (all labelled candidates) changes D values by at most 0.20 (G24, lab-balanced) and changes no regime-II/III call-vs-wall ordering.

**Outcome vs prediction (round 2).**
| Item | Prediction | Result | Verdict |
| --- | --- | --- | --- |
| R6 | one mechanism explains η < 0 (prior M1 50%) | M1 explains ≈ 3/4; M1b, M2, M3, M4 rejected; residual −0.11 common to all regime-III periods | M1 mostly supported |
| R1 | engagement (40%) / exposure (25%) / inconclusive (35%) | inconclusive; full exposure excluded | inconclusive |
| R1c | placement artifact ≥ 0.2 (50%) | +0.04 [−0.06, +0.13] | failed (no artifact) |
| R5 | P5′ ≥ 2/3 (55%); withdrawn (30%) | withdrawn by the validity rule | withdrawn |

**Scorecard changes:** D stays 1 (P5 re-scored uninformative, not failed). H stays 1: M1 beats four named rivals for G38/G44, but regime I is unresolved. B stays 1 (talk composition identified; conditioning on talk is untested when m causes talk). Others unchanged: A1 B1 C1 D1 E1 F2 G1 H1 I1.

**New constants (proposed for `interpretation/swarm-constants.json`):**
- η_rep\|talk (reply-given-talk span elasticity) = −0.11 [−0.16, −0.06]; regime III; G38, G40, G41, G44 (4 periods, τ = 0); DQ2 parents; synthetic attenuation ≈ 10% (S7).
- η_talk (talk-propensity span elasticity) = −0.28 [−0.39, −0.18] in G38 + G44; +0.06 [−0.02, +0.14] in G40 + G41; regime III.
- η_wait (regime-I scheduler-wait elasticity) = +0.18 [−0.17, +0.53]; regime I, Gemini logged chat calls, #24–#31 pooled.

**Round-2 redirects:** (1) Test whether m causes the talk call (talk split under H50's read-out jump) before reading η_rep\|talk as a clean call clock. (2) Regime I needs more logged starts: no non-reserved period has enough; H40-R4 (`confirm.py`, NE20) remains the decisive test. (3) Drop the tertile collapse from the toolkit; use η and the pause-timer dose.

**Claim that stands:** In the computer-use scaffold (regimes II–III), a talk call answers a pending message with a hazard that barely depends on the wall time its previous call spanned (η_rep\|talk = −0.11 [−0.16, −0.06], 4 periods, homogeneous); the negative total η of G38 and G44 is mostly call-type composition (long tool calls are followed by fewer talk calls, η_talk −0.28 [−0.39, −0.18]), and the wall clock (η = 1) is excluded in every regime-II/III period. *Exclusions:* R5 collapse withdrawn (invalid statistic); R1 inconclusive (precondition failed, engagement branch unpowered); the residual −0.11 has no identified cause; regime I's η stays unexplained (only full-strength scheduler-wait exposure and the start-placement artifact are excluded).

## Notes
- 2026-10-04: H29's boundary pull (content channel) was considered as the per-call coupling. Its rows are built on H18's visibility rule and per-unit H29 tables; rebuilding them on the ledger is a separate project. Round 1 uses the reply channel; the content channel is a round-2 redirect.
- 2026-10-04: compute limits: ≤ 2 threads per process, no pools larger than 2, no sub-agents.
- 2026-10-04 (coordinator data-bug notice: `activity_bins` drops about half of all events; `outages` / `stall_minutes` derive from it and will be rebuilt in DQ7): **H40 is not affected.** No H40 script reads `activity_bins`, `outages` or `stall_minutes` (checked by grep). `call_windows` and the context ledger are built from raw events and actions. The ledger's `outage_s` / `outage_off` columns do derive from `outages`, but H40 never loads them.
