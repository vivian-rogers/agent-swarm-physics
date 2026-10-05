# H72: Trap aging is input starvation

**Status:** exploratory round 2 done (2026-10-05): starvation still **failed**, now on held-out log scores; in #51 the context's self-share carries 65% [59, 71] of the aging clocks' held-out information, chatter 22%, directed-input starvation −1%; undirected chatter adds a small hold (β_C −0.085 [−0.140, −0.045]) that a directed read cancels. See "Round 2".
**Round 1 status:** exploratory round 1 done (2026-10-04): **failed.** Trap aging is not input starvation. Card, design and predictions were written before any outcome; the synthetic validation came first (amendment A1). Replication on 18 goal periods (≥ 200 idle gates each); natives NE43, blocked spells (G27 + G51) and the #focus room (G51g). `analysis/confirm.py` is frozen and dry-run on stand-ins; **not run**.
**Headline:** in every period where traps age with power (G17, G18, G38, G51), the aging slope survives the starvation control unchanged (G51: β_a0 −0.48 [−0.54, −0.41] → β_a −0.53 [−0.59, −0.44]; aging absorbed ρ −0.09). The input clock has the *opposite* sign to H72: recent input lowers escape (G51 β_s +0.23 [+0.11, +0.33]; CI above 0 in 7/18 periods, below 0 in 0/18). Recent chatter holds an idle agent at its gate. Directed starvation (no recent nudge or @-mention) does not absorb aging either (G51 β_s,dir +0.09). Blocked spells (Jev `p_blocked`) age at −0.54 (G51) and −0.70 (G27) with or without the directed clock.
**Fields:** stat mech (aging, trap models), dynamics (renewal hazards, exogenous point processes), info theory (input supply)
**Literature:** none of the notes in `literature/` covers aging hazards. Textbook references: Bouchaud, *J. Phys. I France* 2, 1705 (1992)† (trap model, aging from a broad trap-depth distribution); Cox, *Renewal Theory* (1962)†; Allison, *Discrete-time methods for the analysis of event histories* (1982)† (discrete-time hazard with time-varying covariates). † = not in `literature/`.
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime; Action; Agent state (categorical: action class, call level: idle vs active); Driving / external field (human messages, nudges); Interaction (broadcast) and Interaction (addressed) for agent messages; Exposure via the DQ1 context ledger and H43's **receiving call**. New named variants proposed (not edited into DEFINITIONS.md): **"idle gate"**, **"trap age a (call clock)"**, **"input starvation s"** and **"novel item"**, defined under Data scheme.
**From:** HH260 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` ("Making the faithful ones better") · **Models:** `physics-models/09-hawkes/` (exogenous input events and a response kernel), `physics-models/02-nonequilibrium-ising/` (kinetic escape from the idle state)
**Data inputs (shared tables first):** new shared builder `infra/shared/idle_gates.py` → `data/processed/shared/idle_gates/idle_gates.parquet` (DQ1 `call_windows`, `context_ledger_items`, `context_ledger_turns`; leading-@ nudge targets; DQ5 `statement_flags`), DQ3 `behavior_states_v3` (`p_blocked`, native N2), `period_units`, `calendar`, `rooms`. H60 reads the same gate table.

**Question served:** Q4 (where the swarm's information lives and what it is worth: does incoming information keep an agent out of traps?). Q5 second: if escape tracks input, the operator lever is input supply, not a wake-up call.

## Question
H16 found that the escape hazard from long inactivity falls with time in the trap (aging; G51 β ≈ −0.4 to −0.8 per ln unit). Is that aging really *input starvation*? That is: does escape depend on the time since the agent last read a novel context item, so that trap age adds nothing once starvation is controlled?

## Design: two layers (Vivian, 2026-10-04)
- **Replication:** the common two-clock hazard on every eligible goal period (≥ 200 idle gates; 18 periods). Role `replication`.
- **Natives:** NE43 (the nudger stops inside #51), blocked spells from Jev `p_blocked` in G51 and G27 (HH260's own check), and the #focus room in G51 (an input-poor room). Role `native`.
- **Faithfulness lever:** HH260 targets **H** (a rival clock) and **D** (aging should vanish, an unfitted prediction). The scorecard says whether it moved them.

## Model
**From:** `physics-models/09-hawkes/` and `physics-models/02-nonequilibrium-ising/`.

**H72 variant: a two-clock discrete-time escape hazard on the call clock.**
- **Degrees of freedom.** Each agent alternates between idle calls (pause or wait, not talking) and active calls. An **idle gate** g is a call whose previous call was idle; at the gate the agent acts or idles again. Inputs are chat items that enter the agent's context at a call (DQ1 ledger).
- **Hazard.** For gate g of agent i,

  logit P(escape_g) = α_i + β_a ln(a_g / 1 min) + β_s ln(s_g / 1 min) + γ·c_g + δ·z_g,

  with a_g the trap age, s_g the input starvation, c_g the items read at the gate itself (current reads: directed, undirected, own nudge, bookend), and z_g nuisance terms (declared duration of the previous pause, hours since the day's window start, the share of other agents active in the last 10 min, length of the last active run).
- **H72 (starvation):** β_s < 0 and β_a = 0. The agent's context at the gate is assembled from recent items. When no new item has entered for a long time, the newest context is the agent's own idling, and it idles again. Aging in the marginal hazard is then an artifact of s growing with a when no input arrives.
- **Rivals.**
  - **R1 intrinsic aging** (H16 round 1b, NE43: "aging is intrinsic"): β_a < 0, β_s = 0. The trap deepens by itself (self-reinforcement in the context, a Bouchaud-type depth distribution, or frailty not removed by agent FE).
  - **R2 two clocks:** β_a < 0 and β_s < 0.
  - **R3 kick-only (memoryless given input):** only current reads c_g matter; neither clock does.
  - **R4 common field (impostor):** room lulls and the day's schedule lower both the input rate and escape; s then predicts escape without any reading. Removed by the swarm-activity and time-of-day terms and the in-flight placebo (below).

## Data scheme
Shared builder `infra/shared/idle_gates.py` (written for H72 and H60; `--verify` recounts 40 random agent-days by brute force: 720 gates, 0 mismatches). H72's `scheme/build.py` selects the eligible periods and writes `data/processed/H72-trap-aging-input-starvation/`.
- **Sequence:** an agent-day's non-summary calls (`call_windows.ctx_mode != "summary"`) sorted by `t_call`; Claude Code agent and held-out days (`holdout_mask`) excluded.
- **Idle call:** kind ∈ {pause, wait} and not talking (H43 / H59 rule). Every other call is active.
- **Idle gate:** a call whose previous call (same agent-day) is idle.
- **Escape (two definitions, Known issue "escape outcomes are definition-sensitive"):**
  - *sustained* (primary): the gate call and the next two calls are all active (a run of ≥ 3 active calls starts at the gate); censored when the day ends first.
  - *any* (secondary): the gate call is active (a glance counts).
- **Trap age (call clock):** a_sus = t_call(gate) − t_end(last call of the last sustained active run) for the primary outcome; a_any = t_call(gate) − t_end(last active call) for the secondary one. Gates before the agent's first qualifying run of the day are dropped (cold start). Floor 10 s.
- **Novel item:** a ledger item (`context_ledger_items`, not omitted) of kind agent, human or nudge. Pause/resume bookends are not input.
- **Input starvation s:** t_call(gate) − t_call of the latest *earlier* call of the same agent-day that read ≥ 1 novel item. Items read at the gate itself are current reads, not part of s. Variants: **s_content** (novel minus agent items that DQ5 flags as a restatement, `self_repeat` or `cross_echo` under either embedding model), **s_dir** (directed: an item that names the recipient, or a nudge whose leading @ is the recipient), **s_peer** (agent and human items only). Floor 10 s.
- **Current reads c_g:** log(1 + directed items), log(1 + other novel items), own-nudge indicator, bookend indicator.
- **Nuisance z_g:** ln declared duration of the previous pause (bins; "wait" and "no duration" as levels), hours since the calendar window start (bins of 1 h, last bin ≥ 6 h), swarm_act10 (share of other present agents with an active call in the last 10 min), ln length of the last active run.
- **In-flight placebo:** messages by others posted in the gate's room *during the gate call* (t_call, t_end], which the gate's context cannot hold and which cannot answer the gate's own output (posted at t_end or later).
- **Output:** `data/processed/H72-trap-aging-input-starvation/gates.parquet` (eligible periods; codes and numbers only), `G<NN>/results.json`, `native/`, `synthetic/`, `confirm_dryrun/`, `_provenance.json`.
- **Regimes covered:** I (wait gates in chat mode) and III (pause gates). Regime II has < 200 gates per period.

**Structural counts seen before the predictions (no outcomes):** non-holdout gates per period: G51 25,477 (32 agents); G38 1,628; G18 1,425; G17 1,009; G19 778; G04 725; G21 604; G12 557; G20 516; G44 429; G08 408; G41 316; G03 304; G16 274; G37 250; G06 232; G25 221; G40 205; all other periods < 200. Design correlations corr(ln a_sus, ln s_novel): G51 0.63, G38 0.42, G41 0.76, regime I 0.08–0.51. Median s_novel is ≤ 1.4 min in every regime-I period (chat arrives at almost every call) and 2.9–10 min in regime III. s_novel > a_sus at 38–79% of regime-III gates.

## Observables (per period; agent fixed effects; day-block bootstrap, 200 draws)
- **O1 baseline aging** β_a0: the model without s (H16-style aging on the ledger clock).
- **O2 two-clock slopes** β_a and β_s (s = s_novel primary; s_content, s_dir, s_peer variants).
- **O3 aging absorbed** ρ = 1 − β_a/β_a0 (reported when β_a0 < 0 with CI below 0).
- **O4 day-blocked cross-validated log-likelihood** (5 interleaved day folds): s-adds = LL(a, s) − LL(a); a-adds = LL(a, s) − LL(s); nats per 1,000 gates, with a day-block bootstrap of per-day contributions.
- **O5 secondary outcome:** O1–O4 on escape (any) with a_any.
- **O6 in-flight placebo:** the coefficient of log(1 + in-flight messages) added to the two-clock model.
- **Robustness:** cloglog link; trimmed to h_day ≥ 0.25 h and to the agent's own [first, last] call window; the period's first day excluded (kickoff field).

**Per-period verdict rule (replication, primary s_novel and sustained escape).** Powered: ≥ 30 escapes and ≥ 30 non-escapes. Not powered → descriptive.
- *No aging to explain:* β_a0's CI includes 0 → descriptive (n/a for H72).
- *Supported:* β_s < 0 with CI below 0, and β_a's CI includes 0 or |β_a| ≤ 0.15.
- *Failed:* β_a < 0 with CI below 0, and ρ < 0.25 or β_s's CI includes 0.
- *Mixed:* otherwise (both clocks carry weight).

## Null / baseline
- **N1 synthetic (axis F):** parametric bootstrap on the real design. Real gate rows (G51, G38, G18) keep their covariates; outcomes are drawn from planted worlds: intrinsic aging (β_a −0.5, β_s 0), starvation (β_a 0, β_s −0.5), two clocks (−0.3, −0.3), null (0, 0), each with agent heterogeneity (SD 0.5), day effects (SD 0.3) and a planted directed-read kick (+0.7). Because the hazard conditions on the at-risk gate, drawing each gate's outcome given its real covariates is an exact parametric bootstrap of the conditional model. Read: bias, CI coverage, the false-verdict rates of the decision rule, and power.
- **N2 day-block bootstrap** (200 draws) for every CI.
- **N3 in-flight placebo** (O6) for the contemporaneous-convergence impostor.
- **Rivals:** R1–R4 (Model).

## Impostors
| Impostor | Relevant? | How it is handled | Status (after round 1) |
| --- | --- | --- | --- |
| Scheduler field | yes | Hours-since-window-start bins; swarm_act10 (others' activity in the last 10 min); cold-start gates dropped; calls are the clock (H40). Trimming to h_day ≥ 0.25 h leaves G51 at β_a −0.53, β_s +0.24 | removed |
| Exogenous field (kickoff, goal, operator) | yes | Human messages, nudges and bookends read at the gate enter as current reads. Dropping the period's first day: G51 β_a −0.52, β_s +0.23 | removed |
| Shared model priors | partly | Agent fixed effects (style, pause habits). The planned β_s-by-lab breakdown was not run | partly |
| Contemporaneous convergence | yes | s counts only items read at earlier calls. In-flight placebo (messages posted during the gate call's model latency; A2): CI includes 0 in 16/18 periods; G51 +0.16 [+0.08, +0.25], and adding it leaves β_s at +0.24 | removed (small common term in G51) |

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness". Scored after round 1 (2026-10-04); rows C and H updated after round 2 (2026-10-05).
**Rival models:** R1 intrinsic aging, R2 two clocks, R3 kick-only, R4 common field.
**Locked holdout used for confirmation:** none. Planned targets (frozen in `analysis/confirm.py`, not run): #45 (regime III, long pauses), #47–#50 (regime III, short pauses), the #51 tail (09-07 → 09-18), #32 (regime I).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Gates, clocks and input classes come from the DQ1 ledger and `call_windows`; assumptions listed. Not invariant: "idle" is a wait call in regime I and a pause in regime III, and in regime I input arrives at almost every call (median s ≤ 1.4 min) |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Discrete hazard per gate on the call clock with agent FE; the agent's own aging is in the model. Stationarity across NE43 holds only partly (Δβ_a −0.16 [−0.33, −0.01]). Day effects are not modelled (day-block CIs absorb them) |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 2 | **Round 2:** starvation, chatter and self-share compared on day-blocked held-out log scores on the same G51 wakes (G(F) +19.8, G(C) +5.7, G(S) −0.4 nats per 1,000 wakes; ε_F 0.65 [0.59, 0.71]). Round 1: On held-out days (5 day folds) trap age adds 14.9 [10.9, 19.0] nats per 1,000 gates in G51; starvation adds 1.3 [0.2, 2.4], with the wrong sign. The H72 model (starvation only) loses to the age clock in every powered period |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | H72's signature (aging vanishes under control) is absent: the starvation-implied aging b_impl is +0.03 [+0.01, +0.04] in G51 against an observed −0.48. Predicted and held: blocked-spell aging untouched by directed input (N2), a-adds ≫ s-adds (P6) |
| E interventional | predicts the change across a natural experiment | 1 | NE43 (nudger stop): the directed clock did not lengthen (×0.97), so the stop is not a starvation manipulation; escape at fixed age is unchanged (C indicator −0.18 [−0.40, +0.02]); β_a steepens slightly (−0.16) |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 | Parametric bootstrap on the real G51, G38, G18 designs: β_a, β_s within 0.02 of truth; the rule calls intrinsic aging "failed" 100% and null "supported" ≤ 5%. Day-bootstrap SD 1.0–1.6× Wald. Results stable under cloglog, the h ≥ 0.25 trim, dropping the first day and four input definitions |
| G ground truth | agrees with known structure | 1 | Reproduces H16's gate aging on the ledger clock (G51 −0.48 vs TS2r −0.38) and blocked-spell aging (G27 −0.70, G51 −0.54 vs H16 −1.24, −0.39). The positive β_s matches RE-R1's "unaddressed chatter holds agents at the timer gate" |
| H comparative | beats the named rivals | 1 | **Round 2:** the reconciled account (self-share + chatter hold) beats starvation (ε −0.01) and the intrinsic-aging and frailty proxy worlds (ε_F ≤ 0.22); H72's own starvation model still loses. Round 1: H72 loses to R1 (intrinsic aging) in 4/4 powered aging periods. R4 (common field) is mostly excluded: the in-flight placebo is ≈ 0 in 16/18 periods and leaves β_s unchanged; G51 shows a small common term (+0.16) |
| I transfer | holds in other same-mode periods, including the holdout | 1 | The negative result transfers across regimes I and III (G17, G18, G38, G51) and across four input definitions. Holdout not used |

**Faithfulness lever (HH260 aimed at H and D):** it moved both to a clear answer, against the hypothesis: the rival clock (trap age) wins (H 0 for the H72 model), and the unfitted signature is absent (D 1).

## Prediction
*Written 2026-10-04 (UTC), before any H72 outcome statistic on real data and before the synthetic validation.*

**What I had seen:** the H16 card (round 1 and 1b: TS1r aging in G51 −0.77, TS2r gate aging −0.38, NE43 aging unchanged with the nudger off, directed kicks raise gate escape OR 1.5–2.9, messages never break failure loops, blocked spells age in G51 −0.39 and G27 −1.24), H43 (no refractory window; one read = one kick; a nudge buys a glance, not sustained work), H35, H59, H04, H30, H39 round-1b headlines, the lever table, Known issues, the structural counts and design correlations above. I had computed no escape rate, hazard or clock coefficient.

**Card-level predictions (credences in brackets).**
- **P1 baseline aging (G51).** β_a0 < 0 with CI below 0 on sustained escape [0.85].
- **P2 starvation does not absorb aging (G51, s_novel).** After s control, β_a < −0.2 with CI below 0, and ρ < 0.5 [0.7]. β_s's CI includes 0 or |β_s| < 0.2 [0.55]. Reason: in #51's busy room, novel items enter at most calls, so s stays short while traps age.
- **P3 directed starvation absorbs part of it (G51, s_dir).** β_s,dir < 0 with CI below 0, and 0.1 ≤ ρ_dir ≤ 0.6 [0.4]. Reason: directed kicks raise gate escape (H16), and their absence grows with trap age.
- **P4 replication count.** Among powered periods with baseline aging, the per-period verdict is "supported" in at most a third [0.65].
- **P5 regime I.** s_novel barely varies (median ≤ 1.4 min), so β_s is unidentified: CI width > 1 or descriptive in most regime-I periods [0.6].
- **P6 cross-validation (G51).** a-adds > s-adds, and a-adds' CI lies above 0 [0.7].
- **P7 in-flight placebo.** The placebo coefficient's CI includes 0 in G51 and in ≥ 80% of powered periods [0.6].
- **P8 secondary outcome (any escape, a_any).** The same ordering as P2 in G51 (β_a < 0 after s control) [0.6].

**What would count for H72:** in G51, β_a0 < −0.3 while β_a's CI covers 0 with |β_a| ≤ 0.15 after s control, β_s < 0 with CI below 0, and s-adds > a-adds.
**What would count against H72 (and for R1):** β_a stays < 0 with CI below 0 after control for every s variant.

**Natives (dated 2026-10-04, before running).**
- **N1, NE43 (nudger stop inside #51).** B = 08-07 → 08-20 (nudges on, bookends gone) vs C = 08-21 → 09-02 (no nudges). (a) Design: the directed starvation clock lengthens after the stop (median s_dir up ≥ 20%) [0.7]. (b) Invariance: β_a and β_s (s_novel) differ by < 0.3 between B and C, with the difference's CI including 0 [0.6]. (c) A C indicator in the pooled B+C two-clock model (agent FE) has a CI including 0 [0.55]. If H72 were right and the nudger fed the starvation clock, escape at fixed a would fall in C.
- **N2, blocked spells (Jev v3.1, G51 and G27).** A blocked spell is a run of 5-min windows with `p_blocked` ≥ 0.5 (H16 TS5). Discrete hazard per window of leaving the spell, agent FE, slope on ln(windows elapsed), with the directed starvation at the window start (time since the last directed read) and the window's reads as covariates. Blocked-spell aging survives the control (ρ < 0.3) in both periods, and β_s's CI includes 0 [0.65]. Reason: a blocked agent is busy, and messages never break failure loops (H16 P-c6r).
- **N3, #focus room (G51, 08-05 → 08-24).** Agents with gates in both #focus and #general. (a) Design: gates in #focus have longer s_novel (median ratio ≥ 2) [0.7]. (b) The #focus coefficient on sustained escape (agent FE) moves by less than 30% of itself, or by < 0.1 logit, when the s clocks are added: starvation does not mediate the room difference [0.5]. Low power: 5 agents.

### Amendment A1 (2026-10-04, from the synthetic validation, before any real-data outcome)
- **What the synthetic showed** (`analysis/synthetic.py`; 20–40 replicates per world on the real G51, G38 and G18 designs): the estimator is unbiased (β_a within 0.02, β_s within 0.01 of truth at G51; Wald coverage 0.8–1.0; day-bootstrap SD 1.0–1.5× the Wald SE). The rule separates the worlds: intrinsic aging → "failed" 100%; two clocks → "failed" 75–100%. But a pure starvation world (β_s −0.5, β_a 0) produces only weak marginal aging, β_a0 −0.06 (G51) to −0.10 (G18), because s and a are only partly correlated. The rule then calls it "no aging to explain" in 5% (G51), 62% (G18) and 80% (G38) of replicates.
- **Consequence 1, a new unfitted observable (O3b):** the **starvation-implied aging** b_impl = β_s × κ, with κ the within-agent slope of ln s on ln a (same nuisance terms). If starvation explains aging, b_impl ≈ β_a0. Given the real design, a starvation world with |β_s| ≤ 1 cannot produce β_a0 below about −0.2.
- **Consequence 2, verdict rule:** when β_a0's CI includes 0, the period is "supported (starvation without aging)" if β_s < 0 with CI below 0 and β_a's CI includes 0; otherwise "descriptive (no aging to explain)". The other branches are unchanged.
- **CIs:** day-block bootstrap as pre-registered (the check on 8 G51 replicates shows bootstrap SDs of 1.0–1.6× the Wald SE, centred on the point estimates).

### Amendment A2 (2026-10-04, POST HOC bug fix, after the first placebo numbers)
- **What I had seen:** the round-1 results of all 18 periods, including a strongly negative in-flight placebo in G51 (−0.77 ± 0.03).
- **The bug:** the placebo window (t_call, t_end] used the gate call's end time. For a pause call, t_end includes the timer (median 302 s for re-pauses vs 12 s for active gate calls), so re-pausing gates got longer windows and more "in-flight" messages. The placebo was outcome-dependent.
- **Fix:** the window ends at the gate call's model latency, (t_call, t_call + latency_s], capped at 60 s (`infra/shared/idle_gates.py`, `n_inflight_call`). The gate's output cannot exist before then. Only the placebo changed; no clock, outcome or verdict moved. P7 is scored on the fixed window and labelled post hoc.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G03](goalperiod-subhypotheses/G03/README.md) | replication (I) | descriptive | 303 gates; β_a0 +0.15 [-0.01, +2.97]; β_a -0.13; β_s +1.02 [-0.41, +2.38] (no aging to explain) |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication (I) | descriptive | 716 gates; β_a0 +0.20 [-0.00, +0.50]; β_a +0.01; β_s +0.35 [-0.03, +0.55] (no aging to explain) |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication (I) | descriptive | 228 gates; β_a0 +0.38 [+0.18, +1.09]; β_a +0.44; β_s -0.23 [-0.83, +0.15] (no aging to explain) |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication (I) | descriptive | 400 gates; β_a0 +0.03 [-0.47, +0.88]; β_a +0.03; β_s +0.18 [-0.23, +0.55] (no aging to explain) |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication (I) | descriptive | 552 gates; β_a0 +0.01 [-0.18, +0.49]; β_a -0.07; β_s +0.33 [+0.07, +0.62] (no aging to explain) |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication (I) | descriptive | 270 gates; β_a0 -0.71 [-1.56, +0.41]; β_a -1.15; β_s +1.22 [-0.65, +1.78] (no aging to explain) |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication (I) | failed | 1000 gates; β_a0 -0.53 [-0.74, -0.17]; β_a -0.59; β_s +0.25 [-0.16, +0.42] |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication (I) | failed | 1418 gates; β_a0 -0.44 [-0.67, -0.08]; β_a -0.56; β_s +0.41 [+0.19, +0.58] |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication (I) | descriptive | 772 gates; β_a0 -0.16 [-0.30, +0.25]; β_a -0.39; β_s +0.73 [+0.33, +1.02] (no aging to explain) |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication (I) | descriptive | 505 gates; β_a0 +0.12 [-0.17, +1.01]; β_a -0.08; β_s +0.95 [+0.63, +1.72] (no aging to explain) |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication (I) | descriptive | 603 gates; β_a0 -0.62 [-0.87, +0.17]; β_a -0.65; β_s +0.29 [-0.17, +1.68] (no aging to explain) |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication (I) | descriptive | 219 gates; β_a0 -0.25 [-0.43, +23.95]; β_a -0.22; β_s +1.28 [+0.26, +2.63] (no aging to explain) |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication (III) | descriptive | 240 gates; β_a0 -0.28 [-0.52, +6.56]; β_a -0.23; β_s -0.09 [-2.34, +0.35] (no aging to explain) |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication (III) | failed | 1616 gates; β_a0 -0.38 [-0.53, -0.16]; β_a -0.39; β_s +0.03 [-0.21, +0.32] |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication (III) | descriptive | 204 gates; β_a0 +1.14 [-0.35, +6.19]; β_a +1.07; β_s +0.21 [-1.45, +0.57] (no aging to explain) |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication (III) | descriptive | 299 gates; β_a0 -0.18 [-0.19, +0.77]; β_a -0.21; β_s +0.11 [-0.39, +0.60] (no aging to explain) |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication (III) | descriptive | 418 gates; β_a0 +0.05 [-0.04, +1.61]; β_a +0.02; β_s +0.22 [+0.01, +1.66] (no aging to explain) |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication (III) | failed | 22797 gates; β_a0 -0.48 [-0.54, -0.41]; β_a -0.53; β_s +0.23 [+0.11, +0.33] |
| [NE43](goalperiod-subhypotheses/NE43/README.md) | native | descriptive | s_dir ×0.97 after the stop (a fails); Δβ_a -0.16 [-0.33, -0.01], Δβ_s +0.22 (b fails); C indicator -0.18 [-0.40, +0.02] (c holds) |
| [G27](goalperiod-subhypotheses/G27/README.md) | native (blocked spells, + G51) | failed | G27 β_age -0.70 → -0.71, β_s,dir +0.04 [-0.04, +0.10]; G51 -0.54 → -0.54, β_s,dir +0.01 [-0.03, +0.05] |
| [G51g](goalperiod-subhypotheses/G51g/README.md) | native (#focus room) | failed | s_novel #focus/#general ×1.76 (a fails); β_#focus +0.89 → +0.84, Δ -0.05 [-0.12, +0.09] (b holds) |

## Results
### Exploratory round 1 (2026-10-04; non-holdout; 18 replication periods, 3 natives)
- **Scripts:** `infra/shared/idle_gates.py` (shared gate table, `--verify`), `infra/shared/hazard_fe.py` (FE logit/OLS, `--test`), `scheme/build.py`, `analysis/h72lib.py`, `analysis/synthetic.py`, `analysis/run_period.py --all`, `analysis/placebo.py` (A2), `analysis/native.py`, `analysis/figures.py`, `analysis/write_outputs.py` (period folders, 108 estimate rows), `analysis/confirm.py` (frozen, dry run only).
- **Numbers:** `data/processed/H72-trap-aging-input-starvation/` (`G<NN>/results.json`, `native/native.json`, `synthetic/`, `confirm_dryrun/`; ≈ 3 MB).
- **Figures:** `figures/summary_obs.pdf` (clock slopes per period; G51 by input variant), `figures/synthetic_validation.pdf`.

**Outcome vs prediction.**

| Prediction | Outcome | Verdict |
| --- | --- | --- |
| P1 baseline aging in G51 | β_a0 −0.48 [−0.54, −0.41] | holds |
| P2 aging survives s_novel (β_a < −0.2, ρ < 0.5); β_s ≈ 0 | β_a −0.53 [−0.59, −0.44], ρ −0.09 [−0.14, −0.05] ✓; β_s **+0.23 [+0.11, +0.33]** ✗ | first part holds; β_s is not ≈ 0 but has the opposite sign to H72 |
| P3 s_dir absorbs part of aging (0.1 ≤ ρ ≤ 0.6, β_s,dir < 0) | ρ_dir −0.04; β_s,dir +0.09 [+0.06, +0.11] | fails |
| P4 "supported" in ≤ ⅓ of powered aging periods | 0/4 (G17, G18, G38, G51 all "failed") | holds |
| P5 regime I: β_s unidentified or descriptive in most | 10/12 regime-I periods descriptive (no aging to explain) | holds |
| P6 CV: a-adds > s-adds, a-adds CI > 0 (G51) | a 14.9 [10.9, 19.0] vs s 1.3 [0.2, 2.4] nats per 1,000 gates | holds |
| P7 in-flight placebo ≈ 0 (G51 and ≥ 80% of periods; A2 window, post hoc) | 16/18 periods ≈ 0; G51 +0.16 [+0.08, +0.25] | fails narrowly (G51) |
| P8 any escape: β_a < 0 after control (G51) | β_a −0.88 [−0.98, −0.74]; β_s +0.55 | holds |
| N1 NE43 | (a) s_dir ×0.97 ✗; (b) Δβ_a −0.16 [−0.33, −0.01] ✗; (c) C −0.18 [−0.40, +0.02] ✓ | mixed; NE43 is not a starvation step |
| N2 blocked spells | G51 −0.54 → −0.54, G27 −0.70 → −0.71; β_s,dir CIs include 0 | holds |
| N3 #focus | (a) s ×1.76 ✗; (b) Δβ_#focus −0.05 [−0.12, +0.09] ✓ | mixed |

**Reading.**
1. **Aging is intrinsic to the trap, not supplied by the input stream.** In #51, the odds of starting a sustained run at a gate fall as a^−0.5 with trap age a, and controlling for the time since the last novel, content-novel, peer or directed read changes that slope by less than 0.05. If starvation drove aging, the observed design would turn β_s into an aging slope of only b_impl = β_s·κ = +0.03 (κ = 0.12, the within-agent slope of ln s on ln a).
2. **Recent input holds idle agents idle.** β_s > 0 means that a gate that comes long after the last read escapes *more* often. Fresh undirected chatter keeps an agent at its timer gate (RE-R1, H09). Directed input has a smaller positive slope (+0.09). Input read *at* the gate still matters as a kick (current-read terms, as H16), but the memory of earlier input does not.
3. **Regime I has little aging to explain.** Chat arrives at almost every call (median s ≤ 1.4 min); only G17 and G18 age with power, and both fail the same way.
4. **Blocked spells age by themselves.** A Jev-blocked agent leaves the spell at a rate that falls with spell length (G51 −0.54, G27 −0.70) and does not depend on how long ago it was addressed.
5. **Field controls.** Time of day, others' activity and the kickoff day do not move the slopes. The in-flight placebo is ≈ 0 except a +0.16 common term in G51, which leaves β_s unchanged.

**Caveats.**
- Selection on observables: β_s and β_a are conditional associations on the gate's at-risk set; an unobserved agent state that makes agents both read less and wake more could produce β_s > 0.
- Trap age is measured from the last sustained run, so a glance inside a trap does not reset it; the glance-sensitive version (any escape, a_any) gives the same answer.
- 14/18 replication periods are descriptive: four-hour regime-I and short regime-III periods have too little aging to test.
- The β_s-by-lab breakdown (shared-priors impostor) was planned and not run.
- Amendment A1 (rule, before data) and A2 (placebo bug, post hoc) are labelled above.

## Round 2 redirects (2026-10-04)
- **H72-R1 (done in round 2, 2026-10-05). Chatter hold as the object.** Model the gate decision as a competition between the agent's own timer and the undirected-chatter rate: does escape at fixed age fall with the *number* of undirected items read in the last N calls, and does a mention cancel it (RE-R1's OR 3.1)?
- **H72-R2 (done in round 2, 2026-10-05). What does age measure?** Test H16-R1's urn: the self-share of the context items at the gate (own pause turns vs others' items, DQ1 `k_ctx`) as the aging variable, against trap age, on the same gates.
- **H72-R3 (open; needs re-freezing on round-2 statistics). Run `analysis/confirm.py`** on the #51 tail, #45, #47–#50 and #32 after commit and LOG disclosure.

## Round 2 (2026-10-05): chatter hold as the object, and which mechanism carries the aging
*Predictions, nulls and kill rules written 2026-10-05 ~04:00 UTC, before any round-2 outcome statistic on real data. Exploratory; reserved data excluded (`holdout_mask`; #51 before 09-03 as in H16 round 2). Serves Q5 (what keeps an idle agent idle) and Q4 (which input carries information to the wake decision). R3 (the frozen confirm script) is not run: it needs reserved data. Code: `scheme/build_r2.py`, `analysis/r2lib.py`, `analysis/synthetic_r2.py`, `analysis/run_r2.py`. Numbers: `data/processed/H72-trap-aging-input-starvation/r2/`. Round 1 reproduces unchanged (its code paths are not touched).*

**Vocabulary.** A **wake** is a call whose previous call was idle (round 1's "idle gate"). A **timer wake** is a wake at pause expiry (`gap_kind` = pause; 94% of G51 wakes). The **wake index** k is k_sus (1 = the first wake after the last sustained run).

**What I had seen first.**
- Round 1 of this card; H16 rounds 1–2 (summary in the task brief and the card: the own-call-share urn predicts the timer-wake exponent, −0.36 vs −0.35, and absorbs ρ 0.47 [0.33, 0.70] with coefficient 1.05; a forced erasure inside a trap lifts next-wake escape 0.47 → 0.84; a directed read works by address; per-trap frailty fakes timer-clock aging unless ln k is in the model; 45–58% of regime-III TS1r spells are consolidation latency; with ln k in the model, k carries the aging, −1.55, post hoc); RE-R1 (unaddressed chatter holds agents at the timer: 85% vs 65%; a mention restores it, OR 3.1); H43 round 1 headlines.
- **Structural counts with no outcome** (`r2/wakes_r2.parquet`): the copied composition reproduces H16's G51 design exactly (21,361 at-risk wakes, 276 forced and 417 voluntary resets inside traps, median f_call 0.19). Consolidation-start traps: 5.3% of G51 wakes, 1.1% of G38. Undirected items read at the 5 calls before a wake (U5): G51 median 4 (90th percentile 48; 16% zero), G38 median 1 (46% zero), regime I G17/G18 median 7–10 (1–3% zero). Design correlations in G51 (non-consolidation wakes): corr(ln(1+U5), ln a) 0.71, with ln k 0.58, with ln(1 − f_call) −0.50, with ln(5-call window duration) 0.74; corr(ln a, ln window) 0.90; corr(ln k, ln(1 − f_call)) −0.69; ln s_dir correlates ≤ 0.13 with all of them. G38: corr(ln(1+U5), ln a) 0.26, corr(ln k, ln(1 − f_call)) −0.66.

### Degrees of freedom and model
At a wake the agent acts (sustained escape, round-1 definition) or idles again. Four term families compete on the **same wakes**, on top of one base:
- **Base B:** agent FE; round-1 nuisance (previous pause bins, hour-of-day bins, others' activity in the last 10 min, ln last run length); current reads at the wake (ln(1 + directed), ln(1 + undirected), own nudge, bookend); a short-window flag (< 5 earlier calls today); reset at the wake (forced, voluntary; regime III; H16's context step); trap kind at start (after a failure, after talk, after other work).
- **A, the aging clocks:** ln a (trap age, min) and ln k (wake index). A describes aging; it is not a mechanism.
- **S, input starvation** (no new directed input): ln s_dir, minutes since the last directed read (round-1 clock), with its no-read flag.
- **C, chatter hold** (undirected input keeps the agent waiting): ln(1 + U5).
- **F, context self-share** (H16 U-call urn): ln(1 − f_call), f_call = own idle calls / own calls in the context segment. Regime III only (regime-I chat-mode calls have no segment).

**Chatter-hold model (R1).** The agent's own timer and the chatter rate compete for the wake decision. The weak form says β_C < 0: more undirected input read recently, lower escape at fixed a and k. The strong **competing-rates form** says escape odds = r_i / (c·λ_u), with λ_u the undirected-chatter rate (items per minute over the 5-call window), so the slope on ln λ_u at fixed age is exactly −1 (an unfitted number).

**Spell kind at start.** Traps that begin with a consolidation (a summary call starts within [−30 s, +60 s] of the end of the last sustained run) are dropped from the primary sample: their age includes the consolidation's latency (H16). The "all wakes" sample is a bridge to H16.

### R1 · Chatter hold (replication on all 18 periods; G51 primary)
Estimator: agent-FE logit of sustained escape on B + A + C (+ F in regime III); day-block bootstrap CIs (200 draws).

| # | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| R1-P1 | **Dose holds.** G51: β_C < 0 with CI below 0 in B + A + C | CI includes 0 at power ≥ 0.8, or β_C > 0 | 0.65 |
| R1-P2 | **Separable from age and self-share.** G51: β_C stays < 0 with CI below 0 in B + S + C + F + A, and moves by < 30% from R1-P1 | CI includes 0, or \|change\| ≥ 30% | 0.55 |
| R1-P3 | **Not frailty.** G51, first wakes of each trap only (k = 1, no survivor selection; B + ln a + C): β_C < 0 | β_C > 0 with CI above 0 | 0.6 (sign); CI below 0: 0.4 |
| R1-P4 | **Not a common field.** G51 with agent + day FE: β_C keeps CI below 0; the in-flight placebo (round-1 A2 window) added to B + S + C + F + A has CI including 0 and moves β_C by < 0.05 | β_C CI includes 0 under day FE | 0.55 |
| R1-P5 | **A mention cancels the hold.** G51: interaction ln(1 + U5) × 1[directed read at the wake] > 0 with CI above 0 | CI includes 0 at power ≥ 0.8 | 0.35 |
| R1-P6 | **The competing-rates form fails.** G51, wakes with U5 ≥ 1: the slope on ln λ_u (B + A + ln λ_u) has a CI excluding −1, with \|β\| < 0.5 | CI includes −1 | 0.9 |
| R1-P7 | **Replication.** Among powered periods (≥ 30 escapes and non-escapes), β_C < 0 with CI below 0 in ≥ 1/3, and β_C > 0 with CI above 0 in none | CI above 0 in any powered period | 0.45 |
| R1-P8 | Descriptive: dose windows N = 3 and 10; peer-only undirected dose; directed dose ln(1 + D5) as a starvation-as-dose term | — | — |

**Per-period R1 verdict** (scored for the chatter-hold sub-hypothesis, reported in each period README's Round 2 section; the round-1 verdict line, which scores H72's starvation claim, is unchanged): powered and β_C CI below 0 → supported; β_C CI above 0 → failed; CI includes 0 → failed if the period's synthetic power at β_C = −0.25 is ≥ 0.8, else descriptive (unpowered).

**Kill rule (R1).** "Recent undirected chatter holds an idle agent" (round-1 reading of β_s > 0) is **withdrawn** if R1-P1 fails at power ≥ 0.8, or if R1-P4's day-FE estimate loses its CI below 0. It is **adopted as a separable chatter hold** if R1-P1, R1-P2 and R1-P4 hold.

### Reconcile · Which mechanism carries the aging (G51 primary; regime-III periods)
**Score: held-out log score, not in-sample fit.** Day-blocked cross-validation (5 interleaved day folds; agent FE refitted per fold) on models B, B+A, B+S, B+C, B+F, B+S+A, B+C+A, B+F+A, B+S+C+F, B+S+C+F+A, scored in nats per 1,000 wakes; CIs from a day bootstrap of per-day held-out contributions (1,000 draws).
- **Gain** G(M) = LL(B+M) − LL(B): held-out information in mechanism M.
- **Aging information** G(A) = LL(B+A) − LL(B).
- **Aging share explained** ε(M) = 1 − [LL(B+M+A) − LL(B+M)] / G(A): the share of the clocks' held-out information that M makes redundant. ε = 1: M explains the aging; ε = 0: M is unrelated to it.
- **Across periods (transfer):** M's slopes fitted on all G51 wakes enter each other regime-III period with ≥ 200 wakes (G37, G38, G40, G41, G44) as a fixed offset; the target's base is refitted on its training folds; the held-out gain over the target's base is the transfer score TG(M).
- **Calibration of ε(F):** f_call tracks k (corr −0.69), so F can absorb aging that is really intrinsic to re-pausing. The synthetic world W1 (pure ln k aging, no urn) gives the ε(F) a proxy alone produces at the real design; W2 (pure urn) gives the ceiling.

| # | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| RC-P1 | **Starvation explains no aging.** G51: ε(S) < 0.1 | ε(S) ≥ 0.25 with CI above 0 | 0.85 |
| RC-P2 | **Self-share explains the most aging.** G51: ε(F) > ε(C) and ε(F) > ε(S), both difference CIs above 0 | either difference CI includes 0 or is below 0 | 0.7 |
| RC-P3 | **About half.** G51: 0.25 ≤ ε(F) ≤ 0.75 | outside | 0.55 |
| RC-P4 | **Self-share is more than a proxy for the wake index.** ε(F) above the 97.5th percentile of ε(F) in the intrinsic-k world W1 (planted at the observed aging strength) | inside the W1 band | 0.35 |
| RC-P5 | **Chatter is not the aging mechanism.** G51: ε(C) < ε(F); ε(C) CI below 0.25 | ε(C) ≥ ε(F) | 0.5 |
| RC-P6 | **Aging is left over.** G51: LL(B+S+C+F+A) − LL(B+S+C+F) > 0 with CI above 0 (ε(SCF) < 1) | CI includes 0 | 0.75 |
| RC-P7 | **Chatter adds held-out information.** G51: G(C) > 0 with CI above 0 | CI includes 0 or below | 0.55 |
| RC-P8 | **Transfer.** TG(F) > 0 with CI above 0 in G38; TG(S) CI includes 0 in every target | TG(F) CI includes 0 (G38) | 0.5 |

**Kill rule (reconcile).** If RC-P1 holds, "aging is input starvation" stays failed on the held-out score as well as in-sample. The card adopts "**the aging is carried by context self-share**" only if RC-P2 and RC-P4 hold. If RC-P2 holds and RC-P4 fails, it states "self-share is the best single proxy for aging, but it is not separable from intrinsic re-pause aging at this design". If ε(C) ≥ ε(F) with CI, chatter hold replaces self-share as the leading account. Periods other than G51 are read only where the synthetic power for the statistic is ≥ 0.8; otherwise descriptive.

### Impostors (round 2 plan)
- **Scheduler field:** call clock; hour-of-day bins and others' activity in every model; agent + day FE robustness (R1-P4).
- **Exogenous field:** nudges and human messages enter as current reads; directed and undirected separated.
- **Shared priors:** agent FE.
- **Contemporaneous convergence / common field:** the dose counts only items read at earlier calls; the in-flight placebo (posted during the wake call's latency, unread) is added (R1-P4); day FE remove day-level states (H16 post hoc P4 showed day states can fake wall-clock aging).

### Nulls and validation plan (before any real-data round-2 statistic)
`analysis/synthetic_r2.py` on the real G51 and G38 primary skeletons. Outcomes simulated **sequentially within traps** (stop at the first escape, censor at the real trap end; H16). Agent intercepts SD 0.5. Worlds: **W0** null; **W1** intrinsic aging (−0.6 per ln k); **W2** urn (+1.0 × ln(1 − f_call), logit form); **W3** chatter hold (−0.25 per ln(1 + U5)); **W4** starvation (−0.4 per ln s_dir); **W5** per-trap frailty (SD 1.5, nothing conditional); **W6** mixture (W1 −0.3 + W2 + W3); **W7** W3 + a mention-cancel interaction (+0.25). Read: bias and size of β_C (W0, W1, W2, W4, W5), power at −0.25 (W3), the ε of each mechanism in each world (W1 band for RC-P4), the CV classifier's hit rate (the planted mechanism has the largest ε), and the interaction's power (W7). Per-period power for R1 at β_C = −0.25 on every replication skeleton (W3, 40 runs). Pass: size ≤ 0.10, power ≥ 0.8; otherwise the statistic is read as descriptive (dated amendment).

### Round-2 synthetic validation (run 2026-10-05 ~04:05–04:15 UTC, before any round-2 outcome statistic)
`analysis/synthetic_r2.py`; outputs `r2/synthetic/{main,power}.json`. G51: 30 runs per world; G38: 60. Rejection rates are Wald tests at 5%; ε values are means [2.5–97.5% of runs].

| Statistic | Null / rival worlds (size) | Planted world (power) | Notes |
| --- | --- | --- | --- |
| β_C in B + A + C | W0 0.07; W1a 0.07; W1c 0.13; **W5 frailty 0.03**; **W2 urn −0.05 (0.53)**; **W4 starvation +0.04 (0.30, positive)** | W3 −0.247 (truth −0.25): 1.00 | the urn and starvation leak into β_C when F and S are left out |
| β_C in B + S + C + F + A | W2 0.00 (0.00); W4 0.00 (0.03); W0, W1, W5 ≤ 0.10 | W3 1.00; W6 −0.25: 1.00 | the full model removes both leaks |
| β_C at first wakes (k = 1), full model | ≤ 0.07 in every world (W2 0.00, W4 0.07, W5 0.07) | W3 −0.248: 1.00 | in B + A + C the urn and starvation leak as above (0.47, 0.27) |
| β_C with agent + day FE, full model | ≤ 0.13 (W1c 0.13; others ≤ 0.10) | W3 1.00 | — |
| interaction U5 × directed read, full model | ≤ 0.10 | W7 +0.26 (truth +0.25): 1.00 | — |
| slope on ln λ_u (rate) | ≤ 0.07 | W3 −0.21 | recovers the dose slope on the rate scale |
| ε(F) in proxy worlds (no urn) | W1a 0.04 [−0.03, 0.12]; W1b 0.08 [0.00, 0.17]; W1c 0.06 [−0.01, 0.13]; **W5 frailty 0.11 [0.04, 0.22]** | W6 (urn + chatter + k aging): 0.73 [0.62, 0.84] | a proxy alone makes ε(F) ≤ 0.22 |
| ε(C) | W1 0.05–0.07; W5 0.07 | W6 0.54 [0.45, 0.65] | — |
| ε(S) | ≤ 0.02 | W4 1.27 [0.74, 1.78] | — |
| largest ε picks the planted mechanism | W1a: C 0.60 / F 0.40 (both ≈ 0.05) | W2 F 0.90; W3 C 0.87; W4 S 1.00; W6 F 1.00 | — |
| ε(F) − ε(C) CI above 0 | W1a 0.10; W1b 0.07; W5 0.07 | W6: **0.63** | not powered at 0.8 |
| ε(F) − ε(S) CI above 0 | W1 0.07–0.50 (ε small) | W6 1.00 | — |
| ε when the clocks carry no information (W0, W2, W3) | unstable (G(A) ≈ 0) | — | read ε only when G(A) > 0 with CI above 0 |
| β_C power per period at −0.25 | size 0.00–0.13 | **G51 1.00**; G18 0.43; G38 0.33; G04 0.28; every other period ≤ 0.23 | only G51 is powered for R1 |
| G38 reconcile | CV gains: 95% range ≈ 10 nats per 1,000 wakes | W1b G(A) CI above 0 in 0.93; W3 G(C) 0.10; W4 G(S) 0.80 | G38 is not powered for the reconcile |

A pure chatter world (W3) also produces apparent wake-index aging (b_k −0.15, rejection 0.50), because the dose grows with k: chatter *can* make aging, and ε(C) measures how much it does.

### Round-2 amendments (2026-10-05 ~04:15 UTC, after the synthetic validation, before any round-2 outcome statistic)
- **R2-A1 · R1-P1 is scored on the full model** B + S + C + F + A (B + S + C + A in regime I). In B + A + C, an urn world fakes β_C −0.05 (rejection 0.53) and a starvation world fakes +0.04 (0.30); the full model removes both. B + A + C is reported; R1-P2 compares the two. R1-P3 (k = 1) and R1-P5 (interaction) also use the full model.
- **R2-A2 · Only G51 is powered for R1** (1.00 at −0.25; every other period ≤ 0.43). Other periods' R1 verdicts are descriptive unless the CI excludes 0. R1-P7 is read as "β_C CI above 0 in no period".
- **R2-A3 · ε is read only when G(A) > 0 with CI above 0.** The reconcile is read in G51 only; G38 and the 4-h regime-III periods are descriptive (power < 0.8). Transfer scores are descriptive.
- **R2-A4 · RC-P4's band is 0.22**, the largest 97.5th percentile of ε(F) across the proxy worlds W1a, W1b, W1c and W5 (frailty).
- **R2-A5 · RC-P2's F-versus-C difference is not powered** (0.63 in W6): a CI including 0 is inconclusive, not failed. F versus S is powered (1.00).
- **R2-A6 · POST HOC bug fix (transfer only), after the first transfer numbers.** The first offset fit had no step halving. It diverged under quasi-separation in the small target periods and gave held-out losses of −25 to −750 nats per 1,000 wakes for every family, even near-zero offsets. `r2lib.fit_offset` now uses step halving and the same ridge as `hazard_fe.fit_binary`; only the transfer was re-run (`run_r2.py --transfer-only`). No R1, CV or in-sample number moved. Transfer scores were descriptive before the fix (R2-A3) and stay so.

### Round-2 results (run 2026-10-05 ~04:20–04:35 UTC; exploratory, non-reserved)
*Scripts: `analysis/run_r2.py`, `analysis/estimates_r2.py` (113 rows), `analysis/figure_r2.py` → `figures/r2_summary.pdf`. Numbers: `r2/results_r2.json`. CIs: day-block bootstrap (200 draws for slopes, 1,000 for held-out scores). G51 primary sample: 20,237 at-risk wakes (9,873 sustained escapes, 43 days, 29 agents) after dropping 1,124 wakes in consolidation-start traps. Compute: one local process, ≤ 2 threads, ≈ 5 min.*

**R1 · Chatter hold (G51 unless noted)**

| # | Prediction | Observed | Outcome |
| --- | --- | --- | --- |
| R1-P1 | β_C < 0, CI below 0 (full model, A1) | **−0.085 [−0.140, −0.045]** per ln(1 + U5) | **holds** |
| R1-P2 | stays < 0 and moves < 30% from B + A + C | B + A + C −0.130 [−0.177, −0.093] → full −0.085 (34%) | **fails narrowly**: the sign and CI survive, but a third of the B + A + C dose is shared with self-share and starvation (the leak the synthetic predicted) |
| R1-P3 | first wakes (k = 1) | −0.076 [−0.138, −0.024] (10,038 wakes) | **holds**: not survivor selection inside traps |
| R1-P4 | agent + day FE; in-flight placebo ≈ 0, β_C moves < 0.05 | day FE −0.090 [−0.135, −0.046] ✓; placebo **+0.29 [+0.18, +0.39]** ✗; β_C with placebo −0.096 ✓ | **mixed**: day states do not make the dose; the in-flight term is again non-zero (round 1: +0.16) but leaves β_C unchanged |
| R1-P5 | a directed read cancels the hold | interaction **+0.138 [+0.063, +0.205]** | **holds**: at wakes with a directed read the dose slope is +0.05 |
| R1-P6 | competing-rates form fails (slope on ln λ_u ≠ −1, \|β\| < 0.5) | −0.094 [−0.148, −0.041] (B + A); −0.064 [−0.121, −0.013] (full) | **holds**: the hold is 10× weaker than a race between timer and chatter |
| R1-P7 | CI below 0 in ≥ 1/3 of periods, above 0 in none | below 0 in 4/18 (G19, G20, G25, G51), **above 0 in 2/18 (G03, G17)**; point estimates negative in 9/18 | **fails** |
| R1-P8 | descriptive | N = 3: −0.03 ± 0.02; N = 10: −0.13 ± 0.02; peer-only N = 5: −0.09 ± 0.02 (Wald); rate at fixed window: −0.052 [−0.109, −0.005]; directed dose ln(1 + D5): −0.07 [−0.18, +0.04] | the hold grows with the window: it is a slow accumulation, not the last call |

Other full-model slopes in G51: wake index ln k −0.63 [−0.73, −0.47]; trap age ln a +0.08 [−0.04, +0.20] (timer-like once k is in, as H16 post hoc P2); starvation ln s_dir +0.05 [+0.01, +0.08] (round 1's +0.23 shrinks once the dose is in); urn coefficient on ln(1 − f_call) **+1.09 [0.81, 1.33]** (the urn's +1; H16 1.05).

**Reconcile · Held-out log scores, G51** (nats per 1,000 wakes; ε = share of the clocks' held-out information made redundant)

| Mechanism M | Gain G(M) | ε(M) | ε(F) − ε(M) |
| --- | --- | --- | --- |
| clocks A (ln a + ln k; reference) | +22.2 [17.5, 27.2] | — | — |
| S, directed-input starvation | −0.4 [−0.8, +0.0] | **−0.01 [−0.03, −0.00]** | +0.67 [0.60, 0.73] |
| C, chatter hold | +5.7 [3.9, 7.9] | **0.22 [0.17, 0.27]** | +0.43 [0.35, 0.52] |
| F, context self-share | +19.8 [15.3, 24.3] | **0.65 [0.59, 0.71]** | — |
| S + C + F | +20.9 [16.1, 25.4] | 0.69 [0.64, 0.75] | — |

| # | Prediction | Observed | Outcome |
| --- | --- | --- | --- |
| RC-P1 | ε(S) < 0.1 | −0.01 [−0.03, −0.00] | **holds**: starvation explains no aging, held out as well as in-sample |
| RC-P2 | ε(F) largest, both differences CI above 0 | +0.43 [0.35, 0.52] vs C; +0.67 [0.60, 0.73] vs S | **holds** |
| RC-P3 | 0.25 ≤ ε(F) ≤ 0.75 | 0.65 | **holds** |
| RC-P4 | ε(F) above the proxy band (0.22, A4) | 0.65 [0.59, 0.71] | **holds**: self-share is more than a stand-in for the wake index or per-trap frailty |
| RC-P5 | ε(C) < ε(F); ε(C) CI below 0.25 | 0.22 [0.17, 0.27] | **fails narrowly** (upper bound 0.27): chatter carries about a fifth of aging, because the dose grows with trap depth |
| RC-P6 | aging left over after S + C + F | ε(SCF) 0.69 [0.64, 0.75] < 1 | **holds**: 31% of the clocks' information (≈ 7 nats per 1,000 wakes) is in none of the three |
| RC-P7 | G(C) > 0 | +5.7 [3.9, 7.9] | **holds** |
| RC-P8 | TG(F) > 0 in G38; TG(S) CI includes 0 everywhere | TG(F) G38 **+10.2 [+0.2, +19.9]**; TG(S) G38 −1.1 [−1.9, −0.3], G41 −2.1 [−4.3, −0.2] | **mixed**: F holds; S fails as worded, in the direction *against* starvation (G51's starvation slope hurts elsewhere) |

**Across periods (transfer, descriptive, A3/A6).** G51's self-share slope raises held-out scores in G37 +46 [+7, +121], G38 +10 [+0, +20] and G40 +32 [+9, +70]; G41 +16 [−4, +34]; G44 −1 [−14, +7]. The chatter slope transfers only to G41 (+18 [+1, +40]); the starvation slope never helps. In reverse, G38's self-share slope scores +19.8 [14.4, 25.1] on G51, the same as G51's own fit (+19.8): **the urn coefficient is portable across regime-III periods; chatter and starvation slopes are not.** G38's own reconcile agrees in direction (ε(F) 0.72 [0.41, 1.33], ε(C) −0.07, ε(S) 0.04; descriptive, A3).

**Bridge to H16.** With trap age alone (no ln k) and H16's sample (consolidation-start traps kept), F absorbs ρ 0.26 of the age slope in this base (0.41 with them dropped), against H16's 0.47. The base differs: it holds the reset-at-wake step, which H16's absorption model left to F.

**Findings (round 2).**
1. **Aging lives in the context's self-share.** In #51, the share of the agent's own idle calls in its context makes 65% of the aging clocks' held-out information redundant. A world where aging is intrinsic to re-pausing or to per-trap depth gives at most 22%. The coefficient is the urn's +1 (1.09), and G38's coefficient predicts G51 as well as G51's own.
2. **Input starvation explains none of it.** Time since the last directed read adds no held-out information (−0.4 nats per 1,000 wakes) and explains −1% of aging. H72's hypothesis fails on the held-out score as it did in-sample.
3. **Chatter holds, weakly and slowly.** Each e-fold of undirected items read in the last five calls lowers the odds of a sustained escape by 8% (β_C −0.085). From no chatter to the 90th percentile (48 items) that is −0.33 logit. The hold survives day FE and first wakes. A directed read at the wake cancels it. It explains about a fifth of aging because chatter piles up as a trap deepens. The strong competing-rates form (slope −1) fails by a factor of ten.
4. **About a third of aging is still unexplained** by self-share, chatter and starvation together.

### Impostors (round 2)
| Impostor | Relevant? | Handling | Status |
| --- | --- | --- | --- |
| Scheduler field | yes | Call clock; hour-of-day bins and others' activity in every model; agent + day FE leave β_C at −0.090 | removed |
| Exogenous field | yes | Nudges and human messages enter as current reads; directed and undirected doses separated | removed |
| Shared model priors | partly | Agent FE; no family split of β_C | partly |
| Contemporaneous convergence / common field | yes | Dose counts only earlier reads; in-flight placebo +0.29 [+0.18, +0.39] is non-zero but leaves β_C unchanged (−0.096); first wakes −0.076 | partly (the in-flight term is unexplained; one candidate is that escaping calls have longer model latency, which lengthens the window) |

### Scorecard (round 2; round 1 in brackets)
A 1 [1] · B 1 [1] · **C 2 [1]** · D 1 [1] · E 1 [1] · F 2 [2] · G 1 [1] · **H 1 [0]** · I 1 [1].
- **C 2:** three named mechanisms compared on day-blocked held-out log scores with CIs on the same wakes.
- **D 1:** the urn's unfitted +1 holds (1.09) and G38's slope predicts G51; the competing-rates −1 fails.
- **H 1:** the reconciled account (self-share + chatter) beats starvation and intrinsic-proxy worlds; H72's own model (starvation) still loses.
- **I 1:** the self-share slope transfers to 3/5 regime-III periods; no reserved data used.

### Old → new
| Number | Round 1 | Round 2 |
| --- | --- | --- |
| G51 starvation slope β_s | +0.23 [+0.11, +0.33] (s_novel, a only) | +0.05 [+0.01, +0.08] (s_dir, full model) |
| "Recent chatter holds agents" | read from β_s > 0 | dose β_C −0.085 [−0.140, −0.045]; cancelled by a directed read (+0.14) |
| G51 aging | β_a0 −0.48 per ln a | ln a +0.08, ln k −0.63 (full model); clocks carry 22.2 nats per 1,000 wakes held out, 65% of it self-share |
| Held-out comparison | a adds 14.9, s adds 1.3 | G(A) 22.2, G(F) 19.8, G(C) 5.7, G(S) −0.4 |
| Urn coefficient | — (H16: 1.05) | 1.09 [0.81, 1.33] with chatter, starvation and the clocks in |

**Verdicts:** period verdict lines unchanged (they score round 1's starvation claim). Each replication period README gains a Round 2 section with its chatter-hold verdict: supported G19, G20, G25, G51; failed G03, G17 (CI above 0); descriptive (unpowered, A2) elsewhere.

**Operator reading.** To read how stuck an idle agent is, count its own pauses in the current context, not the time since anyone wrote to it: a context made of its own re-pauses is the trap, and erasing it works (H16). Do not expect quiet to help, and do not expect chatter to help either: 48 undirected messages lower the next-wake escape odds by about a quarter, unless one of them names the agent.

**Claim that stands:** in #51, trap aging is carried by the context's self-share, not by input: ln(1 − own idle share of the context) makes 65% [59, 71] of the aging clocks' held-out information redundant (directed-input starvation −1%, chatter 22%; intrinsic-aging and frailty worlds ≤ 22%), with the urn's coefficient (1.09 [0.81, 1.33]) and a slope that transfers to G38 (+10 [+0, +20] nats per 1,000 wakes). Excluded: the chatter hold as more than a G51 result (β_C −0.085 [−0.140, −0.045] in G51; CI above 0 in G03 and G17; only G51 powered) and its full separability (R1-P2, 34% shared); the competing-rates form (slope −0.09, not −1); the in-flight placebo (+0.29, unexplained); transfer to the 4-h periods and the G38 reconcile (descriptive); the 31% of aging none of the three explains; the transfer numbers' post hoc fix (A6).

## Notes
- 2026-10-04: round 1 started. The gate table is a new shared builder (`infra/shared/idle_gates.py`) because H60 needs the same table; registration in `build_all.py` is proposed in the report, not made (other agents are editing shared files).
- 2026-10-04: round 1 done. Compute: local, ≤ 4 threads until the coordinator's load notice, then ≤ 2 threads and one job at a time; ≈ 25 min CPU in total. Disk: `data/processed/H72-trap-aging-input-starvation/` ≈ 3 MB; shared `idle_gates/` ≈ 3 MB.
- 2026-10-04: holdout. Every exploratory load goes through the shared table, which excludes held-out days (`holdout_mask`); the scheme re-asserts it. No held-out count was printed.
