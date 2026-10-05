# H50: Field or coupling: transfer functions and lag tell which

**Status:** exploratory round 1 done (2026-10-04). Predictions were written at 05:40 UTC, before any real-data statistic. Synthetic validation came first; amendments were written at 06:50 UTC, still before real data. Ran on 71 non-holdout units (35 goal periods) plus 4 native tests. Confirmatory script written and dry-run; **not run**.
**Headline: the field/coupling split is identifiable, and it falls along channels.**
- **Activity co-movement** (H12's market mode) is a **field**: the scaffold's daily start and stop. Edges alone explain 0.62 (regime I) and 0.67 (regime III) of it beyond a shifted-input null. Agents start within about 9–22 s of each other (under two call cycles), and in #38 they are halted at the pause message without reading it.
- **Talk co-movement** is a **gated coupling**. A peer message raises the chance that the recipient's *next* call is a talk call: J₁ > 0 in 45/71 units, < 0 in none, onset exactly at hop 1. The coupling changes *what* the read-out call does (talk instead of work); whether the agent is active is unchanged. A counterfactual built from this kernel accounts for roughly all talk co-movement (median f_C 0.92 in regime I, ≥ 1 in regime III).
- **HH167's regime split fails.** Regime-I calls are not message-triggered (wake ratio 1.03–1.07). Both regimes have field-driven activity and coupling-driven talk.
- **NE43** (as a native test): the nudge path vanishes after 08-20, while peer coupling and the day-start field persist. The bookends had already stopped after 08-04, which is a data finding.
- **Scorecard:** A1 B1 C1 D1 E1 F1 G1 H2 I1.
- **Round 2 (2026-10-05; pre-registered 02:50 UTC; see "Round 2").**
  - **Content couples at the read-out call (regime III):** J^c_1 = 0.033 [0.027, 0.039] (bge; gte 0.046), CI > 0 in 10/16 units. Address-gated ×5 (named 0.077, unnamed 0.016).
  - **Graph clause:** the pre-registered event study is inconclusive (length bias at the in-flight call, reproduced in synthetic worlds). Reads batch: C reads A and B's relay at the same call in 60% of cases. Post hoc relay RD at C-hops ≥ 2: 0.014 [0.006, 0.022], and 0.115 when the relay names C.
  - **Regime I:** the hop-1 jump is not a latency artifact. The "continuing rise" is withdrawn. About 70% of the talk jump is a switch into chat mode (ΔP = 0.024 [0.019, 0.029]).
  - Scorecard A1 B1 C1 **D2** E1 F1 G1 H2 I1.
**Fields:** dynamics, stat mech, sociophysics, info theory
**Literature:** none of the notes in `literature/` covers system identification; the method references are in the model folders: Cugliandolo, Kurchan & Peliti, *PRE* 55, 3898 (1997)† (`physics-models/02-nonequilibrium-ising`, response vs correlation); Filimonov & Sornette 2015† (`physics-models/09-hawkes`, nonstationary baselines fake endogeneity). Standard linear-systems tools (FIR/ARX identification, Welch cross-spectra, coherence, group delay) and regression-discontinuity design need no project note.
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Population N(t) (variant *day-present*, H36); Regime; Driving / external field (human messages, nudges, operator bookends, platform errors); Interaction (broadcast) with **Exposure (turn read-out)** (H08; implemented by the shared context ledger); Action (turn-merged) via the ledger's calls; Agent state (vector), *whitened statement mean* basis (H01) for the content channel. **New named variants proposed for DEFINITIONS.md** (not edited here; outside H50's scope), defined under Model: *call cycle (hop)*, *read-out jump (gate coupling)*, *field share (measured)*, *coupling share (gated)*.
**From:** HH167 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` (approved by Vivian 2026-10-04); folds in HH185–HH190 where the data allow · **Models:** `physics-models/02-nonequilibrium-ising/` (linear response, response function R_ij), `physics-models/01-inverse-ising/` (equal-time co-movement, susceptibility), `physics-models/09-hawkes/` (kernels and their pitfalls)
**Data inputs (shared tables first):** `call_windows`, `context_ledger_turns`, `context_ledger_items` (DQ1), `kicks_classified`, `turn_errors`, `calendar`, `period_units`, `rooms_timeline`, `chat_core`, `chat_mentions_clean`, `embeddings/statements*` (content channel). No raw rescans.

## Standards (2026-10-04)
*Documentation pass against `STANDARDS.md`. No analysis was re-run. H50 has no round-1b section; round 1 already ran on the corrected inputs.*

**Question served:** Q2. The card splits co-movement into field (zero relative lag) and coupling (lag quantized at the read-out call). Q1 second: talk coupling is gated at hop 1.

| Impostor | Relevant? | How it was handled | Status |
| --- | --- | --- | --- |
| Scheduler field | yes | Schedule edges are measured inputs against a shifted-input null; an all-running (trim) window variant; series from `call_windows`, not `activity_bins`. Edges explain 0.62 / 0.67 of activity co-movement. | removed |
| Exogenous field (kickoff/goal/operator) | yes | Human messages, nudges, bookends and platform errors enter as FIR fields (Part A). Goal kickoffs are named in the scope but not among the fitted inputs; about half of activity co-movement stays unexplained (f_0). Close by adding kickoffs and `goal_fields` directions as inputs (§1, row 2). | partly |
| Shared model priors | no | The gate is a discontinuity at the read-out call; a family prior cannot create a step there. | n/a |
| Contemporaneous convergence | yes | The read-out RD compares the call in flight with the read-out call, with shifted placebos (C2); κ ≈ 0.9–1.0, so the in-flight side is not elevated. Synthetic slow-drive worlds give J₁ ≈ 0. | removed |

**Inputs:** round 1 uses the context ledger and `call_windows`; it never reads `activity_bins`, `outages` or `stall_minutes` (Amendment 8). Still old: the platform input uses `turn_errors` categories, not `turn_outcomes.failed`; the addressing split uses `chat_mentions_clean`, not the leading-@ target. The content channel (C3) is done in round 2 (bge and gte, `style_resid_period` and `statement_flags` dedupe as variants).

**Two layers:** 33 replication folders. Native tests: 4 (`G38` supported; `G51`, `NE14` and `NE43` mixed).

**Confirm script:** `analysis/confirm.py` exists, frozen (CP1–CP5) and dry-run, built on ledger inputs. No re-freeze needed.

## Question
Can the swarm's collective co-movement be split into a **field** part (a common input moves every agent at its next model call: zero relative lag between agents, counted in call cycles) and a **coupling** part (agents move each other: the recipient responds only at the call that first reads the sender's message, so the lag is quantized in the recipient's call cycles), using impulse responses and lag structure?

**Vivian's scope (2026-10-04):** think in transfer functions and lag. Estimate impulse responses and phase from inputs (human messages, nudges, kickoffs, platform events, schedule edges) to outputs (activity, talk, content) and between agents. A field has zero relative lag; a coupling has a lag quantized in call cycles. Future variants: HH185–HH190.

## Design: two layers (Vivian, 2026-10-04; see `infra/data-quality/QUEUE.md`)
- **Replication (layer 1):** the common estimator (Parts A–C below) on every eligible non-holdout period unit. Period README role: `replication`. Predictions there are templated from this card and labelled as such.
- **Period-native tests (layer 2):** four tests whose setup gives leverage no other unit has, each with its own observable, null and dated prediction. Role: `native`.
  - **NE43** (#51, 2026-08-21): the `automated` speaker (nudges and bookends) goes silent; the scaffold's daily start and stop stay. An input switch-off.
  - **#51 human input:** the most human messages of regime III (113 non-holdout, 69 naming agents), with a named target and room bystanders: the field-vs-relay test.
  - **Regime I vs regime III:** HH167's premise that regime-I waits are message-triggered, and the predicted coupling-vs-field split.
  - **#38 pause gates:** 17 daily resume (16:59:30) and pause (21:00) bookends at fixed times; a square-wave input that tests scaffold kill vs read-out response.

## Model
**From:** `physics-models/02-nonequilibrium-ising/` (response function, linearized kinetic dynamics) with the read-out gating of H08, and `01-inverse-ising` for the equal-time co-movement it decomposes.

**H50 variant: a gated linear-response swarm.** Each agent i makes model calls c = 1, 2, … at context-assembly times t_i(c) (the ledger's `t_call`). Its context at call c holds every room message posted in [t_i(c−1), t_i(c)) (the ledger's items). The call's outcome Y_i(c) (talk; continue working rather than pause or wait) follows a weakly nonlinear (logistic) kinetic rule with local field

  H_i(c) = h_i + b_i(t_i(c)) + Σ_k Σ_{u ∈ new_i(c−k)} g_{class(u)}(k) + Σ_k Σ_{m ∈ peer-new_i(c−k)} J(k),

where b_i(t) is the agent's slow baseline (schedule, day edges), new_i(c) the exogenous items first seen at call c (human messages, nudges, bookends), peer-new_i(c) the peer chat items first seen at c, and k ≥ 0 counts **hops** (call cycles) after read-out. Platform events (infrastructure errors) enter b_i as agent-level impulses. Two ways to make agents co-move:
- **Field.** A common input u at time t_u is read by every recipient at its own first call after t_u (hop 1), so all respond at hop 1: **zero relative lag in call cycles.** In wall-clock time the responses spread by the read-out wait w (the residual of the call interval; renewal theory gives p(w) = S_Δ(w)/⟨Δ⟩), identically for every agent.
- **Coupling.** Agent j's response to i's message m is gated: it can appear only at calls with t_j(c) > t_m. So the response is zero at hop 0 (the call in flight when m was posted) and steps up at hop 1, possibly later with dead time d (hop 1 + d). **The lag is quantized in the recipient's call cycles.**

**Transfer functions.** Aggregating to the minute grid, the swarm output y(t) (fraction of present agents active, or talking) responds to an input class c with an impulse response g_c(τ) = (read-out wait density) ⊗ (post-read-out response). Its Fourier transform G_c(f) gives gain |G|, phase φ(f), group delay −dφ/(2π df) ≈ dead time, and corner frequency f_c. A swarm that responds at read-out with a short memory is a low-pass filter whose corner is set by the read-out wait and the response decay (HH186).

**Decomposition of co-movement.** For the minute-level equal-time co-movement S = Σ_{i≠j} Cov(a_i, a_j) / Σ_i Var(a_i) (= VR − 1; ρ̄ = S/(N−1), H25), nested fits give
  S = S_field(measured inputs) + S_peer(peer chat, two-sided lags) + S_0(unexplained, zero lag),
and the read-out gate splits the peer part into causal coupling (κ, the share of the peer association that steps up at the read-out call) and common drive (1 − κ). **Coupling share** f_C = κ · f_peer; **field share** f_F (measured) plus unmeasured common drive f_U = f_0 + (1 − κ) f_peer.

**Rivals:**
- **R1 pure field:** all co-movement comes from common inputs (measured or not); no read-out jump for peer messages (J = 0).
- **R2 ungated (instantaneous) coupling:** agents respond to peers without waiting for read-out; the peer response shows at hop 0 as much as at hop 1 (or co-movement at zero lag that does not depend on call timing).
- **R3 HH167's regime split:** regime-I co-movement is coupling through message-triggered waits; regime III is field.

**Operational definitions (proposed for DEFINITIONS.md).**
- **Call cycle (hop):** for an event at time t and a recipient j, hop h = the index of j's call relative to the first call whose `t_call` > t (h = 1, the read-out call); h = 0 is the call in flight at t (latest `t_call` ≤ t); h < 0 earlier calls. Lags in call cycles are hops. In wall-clock units, the unit's *mean read-out wait* w̄ = E[Δ²]/(2E[Δ]) over its call intervals Δ converts minutes to call cycles.
- **Read-out jump (gate coupling) J:** for a source message at t_m and recipient calls with start offset s = t_call − t_m, the discontinuity at s = 0 of E[Y | s] (local linear on each side, bandwidth W, donut |s| < 2 s for start-time error), minus the same statistic at shifted placebo times.
- **Field share (measured) f_F:** the fraction of S removed by per-agent FIR responses to measured exogenous inputs (fit on other days, applied to the held-out day).
- **Coupling share (gated) f_C = κ · f_peer**, with κ = J / X⁺, X⁺ the placebo-corrected excess of Y on the readable side (0 ≤ s < W).

## Data scheme (`scheme/`)
`scheme/build.py` builds per-unit tables from the shared tables (no raw rescans):
- **Inputs:** `call_windows` (t_call, t_log, kind, talk, start_conf, gap_kind, first_of_day), `context_ledger_items` (turn_id, message_id, sender, kind, age_s, ment), `chat_core` (message time, room, speaker), `kicks_classified` (resume / pause bookends, human messages by subkind, nudges with targets and recipients), `turn_errors` (err_cat ∈ timeout / vm / resource / network → platform input), `calendar` (windows, holdout), `period_units` (units), `rooms_timeline` (room at a time), `embeddings/statements.parquet` + `statements_white32_bge_small.npy` (content channel).
- **Transform:**
  1. Units: non-holdout `period_units`; eligible if ≥ 3 agents make calls, and ≥ 100 agent chat messages. Holdout rows dropped with a hard assertion (`calendar.holdout` and `common.holdout_mask` must agree).
  2. **Calls table** per unit: agent, day, t_call, t_log, outcome flags talk and act (act = kind not in pause / wait / consolidate / session_stop), first_of_day, start_conf.
  3. **Minute grid** per unit-day over the calendar window: a_i(m) = 1 if agent i logs an act call in minute m, t_i(m) = 1 if it logs a talk call; the agent's day span (first to last call) as the presence mask; exposure series per agent and input class (posting-time counts of the inputs whose `recipients` include i; nudges split target / bystander; human messages split naming-i / not).
  4. **Event–call pairs** for peer messages and exogenous inputs: for each message and each recipient in the room, the recipient's calls with |s| ≤ 10 min, their hop index (h = 1 is the ledger's receiving call) and outcomes; the sender's "was it responding to the recipient" flag (any item from the recipient among the sender's last two receiving calls, from the ledger).
- **Output:** `data/processed/H50-field-vs-coupling-transfer-lag/` (`units.parquet`, `calls/<unit>.parquet`, `grid/<unit>.parquet`, per-unit results in `G<NN>/`, `NE43/`, synthetic results in `synthetic/`, `_provenance.json`). Budget ≤ 200 MB.
- **Regimes covered:** I, II, III (non-holdout). Lags are compared within a regime, since call cadence differs (regime-I chat-mode calls are scheduled about every 74 s; regime-III computer-use calls are chained about every 13 s, with timer pauses of 3–15 min).

## Observables
**Part A. Input → output transfer functions (wall-clock minutes; HH185, HH186).** Per unit, a ridge FIR (second-difference smoothness penalty, λ by leave-one-day-out CV) of swarm activity fraction A(m) and talk fraction T(m) on the inputs' minute counts at lags −10…+60 min, all classes jointly (overlapping inputs deconvolved), with day intercepts. Classes: resume, pause, human (all), nudge, platform (agents with an infrastructure-error turn). For each class:
- **dead time** τ_d: first lag ≥ 0 at which the cumulative response reaches 10% of its 0–30 min extreme; in minutes and in call cycles (÷ w̄);
- **gain** G30 = Σ_{k=0}^{30} g(k) (agent-fraction-minutes per input; ×N = agent-minutes);
- **decay** τ_1/e after the peak; **corner frequency** f_c, where |DFT g| falls to 1/√2 of its DC value; **pre-trend** Σ_{k=−10}^{−1} g(k) (anticipation or schedule clustering; should be ≈ 0);
- **ringing** (HH189): the most negative post-peak lobe relative to the peak.
- **Coherence and phase vs frequency (Bode):** Welch cross-spectra between each input series and the day-demeaned output, one segment per day (Hann taper), pooled per regime; coherence γ²(f), phase φ(f), group delay. Bands: periods > 60, 15–60, 4–15 and 2–4 min.
Day-block bootstrap (200) for CIs.

**Part B. Hop-indexed impulse responses (call cycles; HH185, HH187).** For each input event and each recipient: the outcome rate of the recipient's calls at hops h = −5…+10, minus a placebo profile (the same recipients at times shifted within the same day by 5–30 min). Per input class: r(h); **dead time in call cycles** = first h ≥ 1 with r(h) > 0 at 95% (one-sided); **gate check** r(0) ≈ 0; for common inputs, the **relative onset hop** across recipients (field ⇒ the same hop for everyone).

**Part C. Field/coupling decomposition.**
- **C1 (minute grid; equal-time co-movement):** S on residual activity (and talk) after agent-day means, over minutes where both agents are within their day spans. Nested, cross-fitted by day: + exogenous FIRs per agent exposure → f_F; + peer chat in the agent's room (others' messages, posting time, lags −10…+30) → f_peer; residual f_0. Variants: full window (day edges kept, edges modeled by the resume / day-start input) and edge-trimmed (H38's all-running window).
- **C2 (call level; the gate):** read-out jump J for outcomes talk and act, source = peer chat messages, bandwidth W = 120 s, donut 2 s, placebo-corrected; X⁺, X⁻ (placebo-corrected excess on each side) and κ = J / X⁺. Variants: drop sources that were themselves responses to the recipient (ledger filter); drop `start_conf == low` calls; mention vs non-mention sources.
- **Lag distribution of the peer component:** the placebo-corrected hop profile r(h), its antisymmetric part r(h) − r(1 − h), and the wall-clock read-out delay (t_call at hop 1 − t_m).
- **C3 (content; optional in round 1):** cosine of whitened statement vectors between a peer message and the recipient's next statement, read-out (visible) vs in flight, matched on |s| in 10-s bins (H29's recency control).

**Per-agent (HH190, descriptive):** per-agent read-out jump and nudge response; spread across agents and by lab.

## Null / baseline
- **N0 independent agents:** placebo times (shifted 5–30 min within the day) for Part B and C2; day-shift surrogates (each agent's day series paired with other agents' series from another day of the unit) for C1. These keep each agent's own schedule.
- **N1 field only:** the measured-input model of C1 (f_peer and J should be 0 under it).
- **N2 unmeasured common drive:** synthetic worlds with a slow Ornstein–Uhlenbeck field shared by all agents and no coupling. The gate must read J ≈ 0 there even though f_peer > 0.
- **N3 ungated coupling (R2):** synthetic coupling that acts within the in-flight call; the gate should then show r(0) > 0.
- **Mechanical bias:** a call in flight at a random time is length-biased (pauses are long), so hop-0 outcomes differ from hop-1 outcomes even with no influence. The start-time RD (s-based) avoids it; the hop profile is always placebo-corrected.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R1 pure field; R2 ungated coupling; R3 HH167's regime split.
**Locked holdout used for confirmation:** none run (round 1). `analysis/confirm.py` (frozen CP1–CP5; guarded by `--confirm` + `H50_CONFIRM=1`; dry-run on stand-ins 42a, 44a, 21a, 24, NE43B/C) targets every held-out period unit (#1, #9, #14, #15, #22, #28, #29, #32, #34, #43, #45–#50, #51 tail) and NE23 (nudger off 06-13..06-14). Reuse disclosure: #45 was used by H02 (activity couplings) and H23 (content); #46–#50 by H04 (branching ratio, NE23 manipulation check). H50's statistics (the read-out jump at call boundaries, the field excess of the edge inputs, the CF coupling share) are different and unexamined there.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Calls, read-out calls and items come from the DQ1 ledger; the hop-1 rule agrees with the ledger's receiving call in 100% of pairs (checked in 3 units). Outcomes are per-call talk / work / idle; inputs come from `kicks_classified` and `turn_errors`. The same definitions are used in every regime. Limits: regime-I chat-mode starts are latency-placed (checked on logged-start recipients: J₁ 0.030 ± 0.008 vs 0.034); a talk+wait call is coded idle-plus-talk; content is not done. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | **Update-order audit done:** regime-I calls are not message-triggered (wake ratio 1.03–1.07 vs a uniform-arrival null), and regime-III pauses wake on their timer (0.99). So the gate's premise (influence only at the next scheduled call) holds. RD continuity is checked with shifted-time placebos. Linearity and stationarity within a unit are assumed. Field and coupling interact (non-additive shares, shown in synthetic worlds). |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | J₁ beats the shifted-time placebo in 45/71 units (day or 1-hour-block bootstrap). The activity field excess beats the shifted-input null in 69/71 units (> 0.10). No held-out-day prediction. The synthetic null false-positive rate is 3/35 seeds (≈ 9% at nominal 5%), so per-unit significance is mildly anti-conservative. |
| D unfitted predictions | unfitted statistics and the model's signature | 2 (round 2; was 1) | The gated-coupling signature appears in 45 units: a step at the read-out call, onset at hop 1, no response before read-out, no unit with the ungated (J₁ < 0) pattern. The schedule-field signature (zero relative lag in call cycles) holds: onset IQR 9 s in #38 and 22 s in #51. Not predicted: regime III's plateau after the hop-2 drop, regime I's continuing rise, and the immediate (hop-1) nudge talk response. **Round 2:** the content channel was never used in fitting. The pre-registered prediction of a hop-1 content jump with address gating holds: J^c_1 = 0.033 [0.027, 0.039] (bge; 0.046 with gte), named ×5. |
| E interventional | predicts the change across a natural experiment | 1 | NE43 B→C (nudges off): the nudge path vanishes, peer J₁ is 0.69× (inside ±50%), activity ρ̄ does not fall. A→B (bookends off): the start-up step is unchanged, so the scaffold (not the message) starts agents. #38: agents are halted at the pause message. Two locked numeric bounds were missed on the trim variant; the room changes confound the comparisons. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Gated swarms with real schedules. J₁ bias −2% to −17% in regime-III coupling worlds (−17%, −31% in regime-I worlds); ≈ 0 in field, slow-drive and edge-clustered-input worlds; dead time 2 recovered as onset hop 3 (5/5); the ungated rival gives J₁ < 0. The field excess is specific (≈ 0 without a field). CF f_C tracks the true coupling share in regime III (0.92 vs 0.93; 0.73 vs 0.82) but not in regime I. Robust to W × 3 (smaller, same sign) and to dropping low-confidence starts in regime III; not robust to that in regime I (see A). |
| G ground truth | agrees with known structure | 1 | Agrees with the documented scaffold (chained 13-s computer-use calls; timer pauses; operator start at 16:01 UTC) and DQ1's ledger validation; agrees with H08 (read-out gating), H29 (influence is address-gated: regime-III J₁ is 0.17 for messages naming the recipient vs 0.004 otherwise), H38 (edge co-activation). |
| H comparative | beats the named rivals | 2 | **R2 (ungated coupling) is rejected:** no unit has J₁ < 0, and synthetic ungated worlds give J₁ < 0. **R1 (pure field) is rejected for talk** (J₁ > 0 in 45/71 units; κ ≈ 0.9–1.0, so the left side of the read-out boundary is not elevated) and accepted for activity. **R3 (HH167's regime split) is rejected:** the premise fails and the field excess does not differ by regime (difference 0.03, p 0.10). |
| I transfer | holds in other same-mode periods, including the holdout | 1 | Replicates across 35 non-holdout periods in all three regimes (25 supported, 10 mixed, 0 failed by the templated rule). Holdout not run. |

## Prediction
*Written 2026-10-04 05:40 UTC, before running any H50 analysis on real data.* Prior knowledge used (disclosed): H04 (nudge response delayed ~5 min; human→mentioned agent immediate), H08 (addressing gated by read-out; nudge read-out median 104 s), H38 (regime-III co-activation ≈ 2/3 day edges), H25 (equal-time dial ≈ 0.1; blind to delayed coupling), H39 (NE43), DQ1's documentation (regime-I chat-mode calls scheduled, not message-triggered; regime-III wakes at the pause timer in 99.8%). I have looked at input counts, call-interval quantiles and bookend clock times, but at no response, correlation or co-movement statistic.

**P1 (identifiability, synthetic; axis F).** At village sampling with real input schedules, (a) the read-out jump recovers planted coupling with |bias| < 30% of the planted call-level effect and is |J| < 2 SE in field-only and unmeasured-slow-field worlds; (b) f_F recovers a planted measured-field share within ±0.10, including when inputs cluster at schedule edges; (c) Part B recovers a planted dead time to within one call cycle; (d) the ungated rival (N3) shows r(0) > 0. *Against:* any of (a)–(d) failing means the corresponding real-data number is not interpretable.

**P2 (inputs act at read-out; HH185).** For every exogenous class with ≥ 30 events in a unit: placebo-corrected r(h ≤ 0) ≈ 0 (no response before read-out), and the response onset is at hop 1 for human messages naming the recipient (talk). Nudges: the talk/act onset is delayed, at hop ≥ 2 in call cycles (H08's ~5 min). Gains: human-mention talk gain ≥ 3× plain-human gain per recipient. *Against:* r(0) significantly > 0 in most units (anticipation, or start-time error).

**P3 (low-pass; HH186).** Swarm activity responds to human messages and nudges as a low-pass filter: corner period between 5 and 40 min; coherence concentrated at periods > 15 min (γ² in the > 15 min bands at least twice the 2–4 min band). Resume and day start dominate the low-frequency response (largest |G30|). *Against:* flat coherence or corner period < 5 min.

**P4 (field signature for common inputs).** For human messages and bookends, the onset hop is the same (hop 1) for all recipients that respond (≥ 70% of responders at hop 1 or 2); the relative onset lag across agents in call cycles has median 0. *Against:* bystanders responding systematically later in hops than targets for plain messages.

**P5 (coupling is gated and quantized; HH187).** Peer chat → recipient talk: placebo-corrected read-out jump J > 0 at 95% in ≥ 60% of eligible units; r(0) ≈ 0 (ungated rival R2 rejected); the response decays within ≤ 5 hops. Peer chat → act (continue vs pause): smaller jump (|J_act| < |J_talk|) because regime-III pauses wake on their timer. *Against:* J ≈ 0 in most units (R1), or r(0) ≈ r(1) with no step (R2).

**P6 (decomposition, replication).** Activity co-movement: measured-field share f_F, full-window variant, regime-III median ≥ 0.30 (day edges, H38) and regime-I median ≤ 0.20; gated coupling share f_C < f_F in regime III. Talk co-movement: f_peer > f_F in ≥ 70% of units (talk co-movement is conversational). Unexplained zero-lag share f_0 ≥ 0.3 in most units (unmeasured common drive remains). *Against:* f_F ≈ 0 in regime III, or f_C > f_F in most regime-III units.

**P7 (HH167 regime split; native, see below).** *Against HH167 as posed:* if regime-I call starts are not message-triggered (P-R1 below), the premise fails regardless of P6.

Native-test predictions (also in each NE/G README):
- **NE43 (#51 before vs after 2026-08-21).** (i) The nudge path disappears (no nudges after 08-20), and the pre-period nudge field share of activity co-movement is small (f_nudge < 0.05), because nudges hit one agent at a time. (ii) The day-start step response persists after 08-21: the scaffold, not the bookend message, starts agents (onset dispersion across agents in call cycles changes by < 50%). (iii) Peer read-out jump (talk) after 08-21 within the pre-period 95% CI or within ±50% of it. (iv) Edge-trimmed activity co-movement ρ̄ after 08-21 within ±25% of before. *Against:* ρ̄ falls by > 25% (the nudger or the bookend messages carried co-movement) or the peer jump collapses.
- **#51 human input.** Human messages naming agents: target talk jumps at hop 1 (field on the target). Bystanders (room-mates not named): a smaller hop-1 response (the message as a weak field), plus a hop ≥ 2 response that is larger when the target's reply was already visible to the bystander than when it was not (relay coupling). Plain human messages: recipients respond at hop 1 with no target/bystander lag difference. *Against:* bystander response independent of the target's visible reply.
- **Regime I vs III.** P-R1: in regime-I chat mode, the hazard of a call start in the 30 s after a room message is ≤ 1.2× the hazard in the 30 s before (scheduled calls, per DQ1); if > 1.5×, HH167's premise (message-triggered waits) holds. P-R2: activity f_F higher in regime III than regime I (median difference ≥ 0.15). P-R3: talk read-out jump present in both regimes; κ_talk higher in regime I than in regime III.
- **#38 pause gates.** (i) Resume: ≥ 80% of agents make their first call of the day before the first peer message of the day reaches their room, so onsets cannot be peer-driven (field; zero relative lag in call cycles). (ii) Pause: agents read the pause message at hop 1 and stop after a small, roughly constant number of calls set by the scaffold's stop time, not by reading peers' goodbyes; the number of calls after read-out is not predicted by peer messages read after the pause. (iii) Talk at the pause read-out call is elevated over the placebo (a message field on everyone at once).

## Amendments (written 2026-10-04 ~06:50 UTC, after the synthetic validation and the scheme build, before any real-data response, correlation or co-movement statistic)
1. **Gate bandwidth.** W = 1.5 × the unit's median start-to-start interval of act calls (≈ 17–20 s in regime III), not 120 s. At 120 s the jump was 60% low in synthetic worlds, because the planted response decays within 1–3 calls. 3W is kept as a sensitivity variant.
2. **Hop kernel by successive boundaries.** The jump at boundary k (outcome call k − 1 calls after an anchor call that starts just before vs just after the message) estimates δ(k) − δ(k − 1); the kernel is their cumulative sum, and the onset hop is the first boundary whose jump CI is > 0. The placebo-corrected hop profile r(h) is descriptive only: under a common field it is biased by length-biased in-flight calls (talk calls are longer), so r(1) − r(0) failed in the synthetic OU world and is not used as a coupling estimate.
3. **κ** = J / E⁺, with E⁺ the placebo-corrected local-linear right limit. Coupling-generated bursts also raise the left side, so κ < 1 even in a pure-coupling world; κ is a lower bound on the coupling share of the near-coincident excess.
4. **C1 changes.** In-sample fit of shared smooth (tent-basis) kernels instead of day cross-fitting: cross-fit noise in broadcast regressors added spurious co-movement (f_F of −0.2 to −0.3 in worlds without a field). f_F is compared with a shifted-input null (each day's inputs circularly shifted); **field excess = f_F − f_F,null**. The two-sided peer regression is dropped: it removes covariance mechanically (f_peer > 1 in synthetic worlds). A strictly lagged peer term (1–30 min, f_lag) is kept as a minute-scale check.
5. **Coupling share f_C** comes from a counterfactual (CF): subtract from each agent's minute talk series the expected talk caused by the gated hop-1 kernel at every read-out. It is computed for the talk channel only. In regime-III synthetic worlds it tracks the true coupling share; in regime-I worlds it does not, so regime-I f_C is reported but not scored. The κ · f_peer formula is abandoned. **Field and coupling interact:** coupling amplifies field-driven co-movement, and the true shares sum to more than 1. P6's "f_C < f_F" is therefore read channel by channel: activity field excess (full window) against talk f_C.
6. **Activity within spans** has almost no co-movement in synthetic regime-III worlds (agents act on about 98% of calls). The activity decomposition is scored on the full and trim variants; the span variant is descriptive.
7. **NE43 re-targeted (data finding in the scheme build).** The daily bookends in #51 stop after 2026-08-04 (last resume and pause on 08-04); the nudges stop after 08-20. Segments: **A** 07-29..08-04 (bookends and nudges), **B** 08-05..08-20 (nudges only), **C** 08-21..09-04 (neither). B vs C tests the nudge switch-off (P-NE43 i, iii, iv). A vs B tests the bookend switch-off, which is prediction (ii) (scaffold vs message), confounded with the #focus room split on 08-05. C's rooms merge back on 08-24 (a confound for B vs C).
8. **Data notices.** `activity_bins` (coordinator's bug notice, 2026-10-04) is not used: every H50 activity and talk series is built from `call_windows`. `outages` and `stall_minutes` are not used either; edge trimming uses the agents' own call spans.

## Results by goal period
Replication verdicts use the templated rule (card): **25 supported, 10 mixed, 0 failed** of 35 periods. The ten mixed periods are those where pooled J₁ is not significant (mostly small or 1–2-unit regime-I periods, plus #40, #41). The activity field excess exceeds 0.10 in every period. Native: G38 supported, G51 mixed, NE14 mixed, NE43 mixed. Talk f_C ≥ 1 means the counterfactual removes all talk co-movement (values above 1 are estimator overshoot at low co-movement).

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G02](goalperiod-subhypotheses/G02/README.md) | replication | mixed | I, 1 unit(s); J₁ 0.122 [-0.003, 0.246]; activity field excess 0.30; talk f_C 0.50 |
| [G03](goalperiod-subhypotheses/G03/README.md) | replication | mixed | I, 1 unit(s); J₁ 0.002 [-0.020, 0.024]; activity field excess 0.42; talk f_C 0.03 |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | mixed | I, 4 unit(s); J₁ 0.007 [-0.011, 0.026]; activity field excess 0.52; talk f_C 0.45 |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | supported | I, 1 unit(s); J₁ 0.086 [0.070, 0.102]; activity field excess 0.52; talk f_C ≥ 1 |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | supported | I, 2 unit(s); J₁ 0.090 [0.048, 0.132]; activity field excess 0.55; talk f_C ≥ 1 |
| [G07](goalperiod-subhypotheses/G07/README.md) | replication | mixed | I, 1 unit(s); J₁ -0.029 [-0.087, 0.029]; activity field excess 0.36; talk f_C 0.00 |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | mixed | I, 1 unit(s); J₁ 0.003 [-0.030, 0.036]; activity field excess 0.65; talk f_C – |
| [G10](goalperiod-subhypotheses/G10/README.md) | replication | mixed | I, 2 unit(s); J₁ 0.010 [-0.014, 0.034]; activity field excess 0.46; talk f_C 0.34 |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | supported | I, 1 unit(s); J₁ 0.054 [0.014, 0.094]; activity field excess 0.51; talk f_C ≥ 1 |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication | supported | I, 2 unit(s); J₁ 0.054 [0.041, 0.066]; activity field excess 0.42; talk f_C ≥ 1 |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | supported | I, 1 unit(s); J₁ 0.044 [0.023, 0.066]; activity field excess 0.74; talk f_C ≥ 1 |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | supported | I, 1 unit(s); J₁ 0.067 [0.054, 0.079]; activity field excess 0.60; talk f_C ≥ 1 |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | supported | I, 1 unit(s); J₁ 0.112 [0.080, 0.144]; activity field excess 0.78; talk f_C ≥ 1 |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | supported | I, 3 unit(s); J₁ 0.090 [0.079, 0.101]; activity field excess 0.49; talk f_C ≥ 1 |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | supported | I, 2 unit(s); J₁ 0.088 [0.076, 0.100]; activity field excess 0.52; talk f_C ≥ 1 |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | supported | I, 4 unit(s); J₁ 0.008 [0.002, 0.013]; activity field excess 0.48; talk f_C 0.79 |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | supported | I, 2 unit(s); J₁ 0.026 [0.006, 0.046]; activity field excess 0.41; talk f_C 0.59 |
| [G23](goalperiod-subhypotheses/G23/README.md) | replication | mixed | I, 1 unit(s); J₁ 0.008 [-0.013, 0.029]; activity field excess 0.68; talk f_C 0.28 |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | supported | I, 1 unit(s); J₁ 0.027 [0.011, 0.043]; activity field excess 0.63; talk f_C 0.67 |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | supported | I, 1 unit(s); J₁ 0.036 [0.022, 0.050]; activity field excess 0.53; talk f_C 0.96 |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | supported | I, 1 unit(s); J₁ 0.028 [0.014, 0.041]; activity field excess 0.29; talk f_C 0.60 |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | supported | I, 1 unit(s); J₁ 0.026 [0.017, 0.035]; activity field excess 0.65; talk f_C ≥ 1 |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | supported | I, 2 unit(s); J₁ 0.021 [0.009, 0.033]; activity field excess 0.42; talk f_C 0.70 |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | supported | I, 4 unit(s); J₁ 0.016 [0.003, 0.028]; activity field excess 0.25; talk f_C 0.94 |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | mixed | II, 1 unit(s); J₁ -0.002 [-0.023, 0.020]; activity field excess 0.43; talk f_C 0.00 |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | supported | II, 1 unit(s); J₁ 0.012 [0.002, 0.022]; activity field excess 0.60; talk f_C 0.38 |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | supported | II, 3 unit(s); J₁ 0.031 [0.008, 0.055]; activity field excess 0.46; talk f_C 0.62 |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | supported | III, 1 unit(s); J₁ 0.097 [0.087, 0.107]; activity field excess 0.66; talk f_C ≥ 1 |
| [G38](goalperiod-subhypotheses/G38/README.md) | native | supported (replication supported) | III, 5 unit(s); J₁ 0.009 [0.001, 0.017]; activity field excess 0.66; talk f_C 0.66 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | supported | III, 1 unit(s); J₁ 0.026 [0.003, 0.049]; activity field excess 0.73; talk f_C 0.88 |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | mixed | III, 1 unit(s); J₁ 0.010 [-0.001, 0.022]; activity field excess 0.68; talk f_C ≥ 1 |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | mixed | III, 1 unit(s); J₁ 0.024 [-0.005, 0.052]; activity field excess 0.70; talk f_C 0.74 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | supported | III, 2 unit(s); J₁ 0.022 [0.018, 0.027]; activity field excess 0.54; talk f_C 0.91 |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | supported | III, 2 unit(s); J₁ 0.025 [0.008, 0.043]; activity field excess 0.44; talk f_C ≥ 1 |
| [G51](goalperiod-subhypotheses/G51/README.md) | native | mixed (replication supported) | III, 12 unit(s); J₁ 0.016 [0.015, 0.018]; activity field excess 0.53; talk f_C ≥ 1 |
| [NE14](goalperiod-subhypotheses/NE14/README.md) | native | mixed | regime-I calls not message-triggered (wake ratio 1.03–1.07); activity field excess I 0.51 vs III 0.55; J₁ > 0 in 27/41 (I), 17/27 (III); κ I 0.87 < III 1.02 |
| [NE43](goalperiod-subhypotheses/NE43/README.md) | native | mixed | nudge→target talk J₁ 0.21 (B), gone in C; peer J₁ 0.019 → 0.013 (×0.69); ρ̄ (span) 0.015 → 0.014; onset IQR 22 s with and without bookends |

## Results
### Exploratory round 1 (2026-10-04; non-holdout only)
Code in `analysis/`:
- `h50lib.py`: estimators.
- `simulate.py`, `schedules.py`, `synthetic.py`, `synth_summary.py`: axis F.
- `run_unit.py`: the replication layer.
- `native.py`, `write_native_results.py`: the native tests.
- `summarize.py`, `write_period_results.py`, `figs_summary.py`: synthesis and figures.
- `check_logged_starts.py`: the latency-placement check.
- `confirm.py`: not run.

Scheme: `scheme/build.py`. Data: `data/processed/H50-field-vs-coupling-transfer-lag/` (`unit_table.parquet`, `summary.json`, `G<NN>/`, `NE14/`, `NE43/`, `synthetic/`; 45 MB).

Figures (`figures/`):
- `summary_kernel_split_col.pdf`: call-cycle kernel and field/coupling split.
- `hop_kernels.pdf`: peer and input hop kernels by regime.
- `bode.pdf`: coherence and phase, pooled by regime.
- `summary_obs.pdf`: per-unit J₁ and shares.
- `synthetic_validation.pdf`, `synthetic_col.pdf`.

**Synthetic validation (axis F; 15 scenarios × 5 seeds; N = 10 regime-III agents on #51c–d schedules, N = 8 regime-I agents on #4c schedules).**
- **Gate J₁ recovers planted coupling.** Bias −2% to −17% in regime-III coupling worlds, and in edge-clustered-input and slow-drive worlds. Bias −17% and −31% in the two regime-I coupling worlds.
- **No false coupling in field, slow-drive or null worlds:** 3/35 seeds positive at 95%, one-sided.
- **Dead time and the ungated rival are told apart.** A planted dead time of 2 hops shows up as onset hop 3 in 5/5 seeds; the ungated rival gives J₁ < 0.
- **The field excess is specific** (≈ 0 without a planted field).
- **The CF coupling share tracks the truth in regime III only:** 0.92 vs 0.93, 0.73 vs 0.82, but not in regime I.
- **Pre-data amendments followed** (see Amendments): the 120-s bandwidth was biased 60% low; the hop-profile difference fails under a common drive (length-biased in-flight calls); the two-sided peer regression removes covariance mechanically.

**Outcome vs prediction.**

| Prediction | Observed | Verdict |
| --- | --- | --- |
| P1a gate recovers coupling (\|bias\| < 30%), null-safe | bias ≤ 17% in 7/8 coupling worlds (31% in one regime-I world); false positives 3/35 | mostly passed |
| P1b f_F recovers the field share ± 0.10 | shares are non-additive (coupling amplifies field); field excess is specific but not a share estimate | amended / partial |
| P1c dead time within one call | onset hop 3 for dead time 2, 5/5 | passed |
| P1d ungated rival visible | J₁ < 0 (amended from r(0) > 0) | passed |
| P2 inputs act at read-out; human-mention gain ≥ 3× plain; nudges onset ≥ hop 2 | in-room human messages: J₁ 0.003 [0.002, 0.004] (I), 0.020 [0.011, 0.029] (III), onset hop 1 in most units with an onset; named-target jumps underpowered (685 / 95 pairs); **nudged agents talk at hop 1** (J₁ 0.14 [0.08, 0.20], III) | mixed (nudge part failed) |
| P3 low-pass, corner 5–40 min, coherence at > 15 min | coherence 8–10× higher at 15–60 min than at 2–4 min (human 0.03–0.04 vs 0.004); edges dominate the lowest band (γ² ≈ 0.25); human and nudge kernels peak at 2–4 min, decay in 4–6 min, then undershoot (ring −0.5 to −0.8), so the "corner" from the DC gain sits at 55–125 min and is not meaningful | mixed |
| P4 common inputs: zero relative lag in call cycles | first-call onsets IQR 9 s in #38 (0.7 cycles), 22 s in #51 (1.6–1.9 cycles); 82% of agents start before any peer message; pause = synchronous halt; in-room human messages: onset hop 1–2 in 89% (I) / 67% (III) of units with an onset | supported |
| P5 coupling gated (J₁ > 0 in ≥ 60%), no hop-0 response, decays ≤ 5 hops, \|J_act\| < \|J_talk\| | J₁ > 0 in 45/71 (63%), < 0 in none; onset hop 1 in all 45; regime III drops at hop 2 (J₂ < 0 in 8/27) and then plateaus (kernel ≈ 0.015 to hop 6); regime I keeps rising (J₂ > 0 in 13/41); act/idle ≈ 0, work −0.02 to −0.03 (talk replaces work) | mostly supported (decay clause failed) |
| P6 activity f_F ≥ 0.30 (III), ≤ 0.20 (I); talk coupling > talk field; f_0 ≥ 0.3 | activity field excess 0.55 (III) ✓, 0.51 (I) ✗; edges alone 0.67 / 0.62; f_C > talk field excess in 25/27 (III), 32/41 (I) ✓; about half of activity co-movement unexplained ✓ | mostly supported (regime-I clause failed) |
| P7 / NE14 HH167 regime split | premise fails as predicted (calls not message-triggered); field excess III − I = 0.03 (p 0.10); κ I 0.87 < III 1.02 | HH167 rejected |
| NE43 (i)–(iv) | nudge path gone; edge step unchanged without bookends; peer J₁ ×0.69; trim ρ̄ +41% from 0.009 (span/full within ±10%) | mixed (core supported) |
| G51 human relay | plain messages: hop-1 field (J₁ 0.19 [0.02, 0.26]); target and relay jumps not significant | mixed (underpowered) |
| G38 pause gates | resume: 82% start before any peer message; pause: 94% of agents make no further call; last calls end within +23 s (q90) | supported |

**Impulse responses per input class (Part A, swarm activity; medians over units with that input).**

| Input | Regime | Gain G30 (agent-fraction-min) | Dead time | Decay | Coherence 15–60 min / 2–4 min | Call-level gate (talk) |
| --- | --- | --- | --- | --- | --- | --- |
| day start (resume or scaffold edge) | I / III | +2.7 / +5.6 (positive in 15/32, 11/23 units) | 8.5 / 4 min | 16–17 min | 0.026 / 0.001 (lowest band ≈ 0.25) | n/a (agents start before peers talk) |
| pause bookend | I / III | −7.0 / −9.3 | 1–2 min | 11–13 min | ≈ 0 | n/a (agents halted without reading it) |
| human message | I / III | +0.17 / +0.34 | 2 min | 4–6 min, then undershoot | 0.04 / 0.005 | in-room J₁ 0.003 (I), 0.020 (III); onset hop 1 |
| nudge | III | +0.58 (positive in 6/20) | 2 min | 6 min | 0.015 / 0.003 | target J₁ 0.14 [0.08, 0.20], onset hop 1; bystanders 0.010 [−0.004, 0.023] |
| platform (infra errors) | I / III | +0.65 / +0.34 | 1–2 min | 4–6 min | I 0.04 / 0.008; III 0.12 / 0.035 | — |

**The field/coupling decomposition.**
- **Zero-lag common component (field).** Activity co-movement in the full window: ρ̄ 0.26 (I), 0.15 (III). The measured inputs explain a field excess of 0.51 (I) and 0.55 (III) of it, almost all from the schedule edges (edges alone 0.62 / 0.67; human, nudge and platform inputs alone 0.04 / 0.14). Within the all-agents-running window, activity co-movement nearly vanishes (ρ̄ 0.056 in I, 0.005 in III): **the activity market mode is the schedule.** Talk's field excess is 0.24 (I) and 0.15 (III).
- **Lagged peer component (coupling).**
  - *Size and timing.* A peer message raises the chance that the recipient's read-out call is a talk call by J₁ ≈ 0.034 (I) and 0.019 (III), pooled IVW. That is +25% and +44% over the base talk rate. The read-out call starts a median 16 s (I) and 24 s (III) after the message; q90 is 2–5 min (pauses).
  - *Lag structure in call cycles.* The response appears at hop 1 and is absent at hop 0. In regime III it drops at hop 2 and plateaus near 0.015; in regime I it rises over 2–5 hops, which is not validated beyond hop 2.
  - *What it acts on.* It converts work calls into talk calls (J₁ work −0.034 / −0.023); the idle share is unchanged.
  - *Addressing.* In regime III it is address-gated: messages naming the recipient give J₁ 0.17, others 0.004. In regime I unaddressed messages couple too (0.031 vs 0.042).
  - *Share of talk co-movement.* The CF from the hop-1 kernel accounts for roughly all talk co-movement (median f_C 0.92 in I, ≥ 1 in III; CI lower bound medians 0.32 / 0.37). κ ≈ 0.9–1.0: the excess talk just after a peer message is almost entirely caused by reading it.
  - *Slow peer influence* (lagged peer chat at 1–30 min) adds ≤ 0.09.
- **The two parts interact.** Coupling amplifies field-driven talk (true shares sum > 1 in synthetic worlds), so the numbers above are separate shares, not a partition.

**NE43 result.** The nudge path is real but local: a nudged agent talks more at the call that reads the nudge (J₁ 0.21, hop 1). Switching the nudger off (08-21) leaves peer coupling (×0.69, inside ±50%) and activity co-movement (span ρ̄ 0.015 → 0.014; full 0.062 → 0.066) in place. The nudger moved individual agents, not the collective mode (Δf_F from the nudge classes: 0.03 span, 0.08 trim). The bookend messages (gone after 08-04) were not inputs either: the day-start step and the 22-s onset spread are unchanged without them.

**HH185–HH190.**
- **HH185 (transfer function): tested.** Per-class FIR impulse responses (dead time, gain, decay) and call-level gate kernels.
- **HH186 (Bode): tested.** Coherence and phase pooled by regime (`figures/bode.pdf`). The swarm passes the day-scale edge input, while human and nudge inputs are sparse and weakly coherent (γ² ≤ 0.05). The "more nudges add little" reading fits: nudges move single agents for a few minutes.
- **HH187 (quantized lags): tested at hop resolution.** The response is quantized at the read-out call (hop 1, never hop 0). The hop-distance-on-the-read-out-graph clause is round 2. Round 2: the event study is inconclusive; the post hoc relay RD supports it in regime III; reads batch (ρ = 1 in 60%).
- **HH188 (T_eff(ω)): not tested.**
- **HH189 (dead-time stability): descriptive.** No damped oscillation. Human and nudge kernels undershoot after their peak (activity is advanced, not added). No phase margin estimated.
- **HH190 (per-agent transfer): partial.** Per-agent J₁ is strongly heterogeneous (Q = 685 on 16 df in I; 325 on 30 df in III) and tracks the agent's talk rate in regime III (r = 0.48). Lab medians are noisy.

### Caveats
- **Regime-I timing.** Chat-mode call starts are latency-placed, and talk calls run longer than the median latency, which could fake a talk jump. On logged-start (Gemini) recipients in #24–#31 the jump holds (0.030 ± 0.008), but early regime I (#2–#21) has no logged starts. The regime-I kernel beyond hop 2 (continuing rise) is not validated in synthetic worlds. The "certain items" sensitivity variant is invalid for an RD: it drops near-boundary pairs on one side.
- **Multiplicity and power.** Per-unit CIs come from a day bootstrap (1-hour blocks for units with < 3 days) and are mildly anti-conservative (synthetic false-positive rate ≈ 9%). 71 units × several statistics; the cross-unit counts are the evidence, not single units. The named-target and relay tests in #51 have about 100 pairs.
- **Decomposition shares are model-based and non-additive.** CF f_C > 1 is overshoot at low talk co-movement (median per-pair talk ρ̄ 0.01–0.04). Activity field excess depends on the full-window grid (pre-start minutes are zero).
- **NE43 confounds:** the #focus room split (08-05), the merge (08-24) and roster joins in C.
- **Content channel:** done in round 2 (see "Round 2"). Regime-I content beyond hop 1 is not validated.
- **`activity_bins` bug notice:** H50 does not use that table; all series come from `call_windows`. Not affected.

## Round 2 redirects
**What the direction is really after:** which levers move a swarm together (fields) and which only propagate through who reads whom (couplings), measured in the units the scaffold imposes (calls), so an operator knows what an input will do to collective behavior.
- **H50-R1. Content gate (C3).** *Done in round 2 (superseded; see "Round 2").* The read-out jump for content (whitened statement cosine to the source message), with H29's matched-age control, by hop. Does content couple at hop 1 the way talk does, and is it also address-gated in regime III?
- **H50-R2. Validate the regime-I dead-time kernel.** *Done in round 2 (superseded; see "Round 2").* Build regime-I synthetic worlds with mixed chat-mode and computer-use calls and planted dead times. Re-estimate the kernel on logged-start recipients only, and split read-out calls by mode.
- **H50-R3. HH188 frequency-dependent T_eff.** Compare spontaneous talk cross-spectra with the gated response spectrum per band; and HH189's phase margin from the hop kernel and the talk loop gain.
- **H50-R4. HH190 agent impedance.** Per-agent kernels (gain, onset hop, persistence) against H29's net influence current and H32's information current; family and scaffold clustering with partial pooling.
- **H50-R5. Human-input relay with power.** Pool the human-rich regime-I periods (#4–#6) and use the hop 2–4 kernel for bystanders, with 3W bandwidth.
- **H50-R6. HH187 graph clause.** *Done in round 2 (superseded; see "Round 2").* Lags vs hop distance on the read-out graph (A reads B reads C): does C's response to A appear at hop 2 of C's calls?
- **H50-R7. Confirm on the holdout** (`confirm.py`: CP1–CP5, NE23 nudger off/on).
- **H50-R8. Regime-I mode channel: field or coupling?** Is the switch into chat mode gated at the read-out call or set by the scheduler? Use scheduler ticks, logged starts and a matched in-flight placebo.
- **H50-R9. Graph clause, confirmatory.** Pre-register the relay RD (C-hops ≥ 2, named vs unnamed) for the reserved data. Add the content relay: does C's statement move toward A after it reads B's relay?
- **H50-R10. Length-dependent null worlds for every hop-indexed design.** Any profile indexed by calls around an event inherits the length bias of the in-flight call. Use a start-time RD, or validate on W0L-type worlds.
- **H50-R11. Content gate in the two-room weeks** (#36–#44) with pooled age bins.

## Round 2 (2026-10-04/05): content gate, graph clause, regime-I kernel
*Items H50-R1, H50-R6 and H50-R2. Predictions, nulls and kill rules written 2026-10-05 02:50 UTC, before any round-2 statistic on real data. Seen before writing: the round-1 results above; the regime-I call composition (chat-mode calls are 5–38% of regime-I calls and 78% of them talk; computer-use calls talk 4%; logged starts exist only in #23–#31, about 20% of calls); logged latencies (chat-mode talk median 8.7 s, chat-mode non-talk 14.1 s, computer-use 11.4–11.8 s). No content, relay or round-2 kernel statistic had been computed. Code: `analysis/r2_*.py`. Data: `data/processed/H50-field-vs-coupling-transfer-lag/r2/`. Reserved data are masked with `holdout_mask` in every script.*

### R1. Content gate (C3)
**Rows.** Source m = an agent chat message with a statement vector. Recipient j = a ledger receiver of m (`context_ledger_items`, kind agent; receiving call r). Response B = one of j's next 8 chat statements after t_m, same PT day, within 30 min. B's producing call comes from `producing_calls`. The hop of B is h = pos(prod(B)) − pos(r) + 1 in j's non-summary call sequence. So h = 1 is a statement made by the read-out call. h = 0 is a statement made by the call in flight at t_m: it is posted after m, but that call could not read m (the in-flight placebo).

**Outcome.** y = cos(z_B, z_m) − cos(z_B, z_m′). Here z is the 32-d whitened, unit-normalized statement vector (bge-small primary, gte-modernbert second). m′ is a seeded random statement of the same sender at least 2 h away from t_m in the same unit (mean of 2 draws). It removes the sender's static style and position.

**Estimator: matched-age jump by hop (H29's control).** Age a = t_B − t_m. For hop h ≥ 1:
J^c_h = Σ_b w_b [ȳ(h, b) − ȳ(0, b)], over age bins b of 10 s in [0, 60) s, with w_b ∝ n_hb n_0b / (n_hb + n_0b).
The age match removes co-response: similarity falls steeply with age (H29), and hop-0 rows are young by construction. Primary statistic: J^c_1. Also J^c_2, J^c_3 (onset), named vs unnamed (ledger `ment`: m names j). CIs: day bootstrap (1-h blocks for units with < 3 days), 400 draws. Pooled per regime by inverse-variance weights over units.
- Variants (descriptive): H29's original bins [0, 30) s; `style_resid_period` vectors; drop B flagged `self_repeat_both`; age × latency-tercile matching (visible rows at a given age come from shorter calls); raw cosine without m′.
- Eligible units: round-1 units with ≥ 200 hop-1 and ≥ 200 hop-0 rows in [0, 60) s.

**Synthetic validation first (axis F), on the real skeleton.** Units #51b (regime III, one room), #38a (regime III, two rooms) and #27 (regime I). Real message times, real ledger reads, real producing calls; only the vectors are synthetic. Each statement is a normalized sum of: own persistence, a shared room topic (slow OU, τ = 30 min, plus fast OU, τ = 60 s: the co-response field), noise, and a gated pull a·z_m for every message read by the producing call or earlier (decaying over the statements that follow; named messages × 5). Truth = the oracle difference in cos(z_B, z_m) between the world and the same world with a = 0 (same noise), at hop 1.
- **N0, no pull** (topic fields only): J^c_1 within 2 SE of 0 in ≥ 90% of seeds. The unmatched visible-minus-invisible contrast should be biased (H29's failure).
- **N1, gated pull:** |bias of J^c_1| < 30% of truth; named / unnamed ratio recovered within a factor of 1.5.
- **N2, ungated rival** (pull from every message posted before t_B, read or not): J^c_1 ≈ 0.
- **N3, dead time 1** (pull starts at hop 2): J^c_1 ≈ 0 and J^c_2 > 0.
- **Power:** at the pull that gives J^c_1 equal to half the named effect H29 measured, pooled regime-III power ≥ 0.8. Without it, a null verdict is "inconclusive".

**Predictions (real data, non-reserved).**
- **P-R1a (content couples at hop 1):** pooled regime-III J^c_1 > 0 with the CI above 0, in both embedding models. CI > 0 in ≥ 1/3 of eligible regime-III units.
- **P-R1b (address gating):** in regime III, named J^c_1 ≥ 3 × unnamed; unnamed CI includes 0 (pooled, bge).
- **P-R1c (onset at hop 1, like talk):** J^c_1 > 0 and J^c_1 ≥ J^c_2 (pooled regime III).
- **P-R1d (regime I, low confidence):** pooled J^c_1 ≥ 0, with unnamed messages coupling too (unnamed CI > 0), as for talk. Latency-placed starts blur the hop-0 / hop-1 split, which attenuates J^c_1.
- **Kill rules.** (i) Pooled regime-III J^c_1 CI includes 0 in both models while synthetic power ≥ 0.8 → "content does not couple at hop 1" (H50 then holds for talk only). (ii) Unnamed ≥ named / 2 with unnamed CI > 0 in regime III → content is not address-gated. (iii) J^c_1 ≈ 0 and J^c_2 > 0 → content has a dead time of one call (not "like talk"). (iv) If N0 gives |J^c_1| > 2 SE in > 20% of seeds, the estimator is not interpretable and R1 is not scored.
- **Rivals.** R1 pure field: J^c_h = 0 at every hop. R2 ungated: the pull is already present at hop 0, so J^c_1 ≈ 0 at matched age. Convergence (STANDARDS §1): removed by the hop-0 in-flight placebo at matched age. Shared priors: m′ (same sender) and `style_resid_period`.

### R6. Graph clause (HH187): lag vs hop distance on the read-out graph
**Triples.** Source A (an agent message, sender a). Relay m_B = a chat message by B ∉ {a} whose producing call is B's ledger receiving call of A (B posts at the call that reads A). Third agent C ∉ {a, B} reads both A and m_B (ledger). ρ = pos(r_C(m_B)) − pos(r_C(A)) + 1 is the C-hop, on A's clock, of the call that reads the relay. Per (A, C) pair, keep the earliest relay read.

**Estimator: event study on the relay read inside C's clock.** Outcome Y = C's talk at C-hops h = 1…6 after A. Per unit, a linear probability model with pair effects and hop effects:
Y_{p,h} = α_p + β_h + Σ_e γ_e 1[h − ρ_p = e] + ε, for e ∈ {−3, −2, 0, 1, 2}, e = −1 the reference.
- β_h carries the direct response to A (read at hop 1) and the common kernel shape. γ_0 is the **relay step G**: the extra talk at the call that reads B's relay, beyond A's own clock.
- Identification comes from variation in ρ across pairs. Primary sample: ρ ∈ {2, …, 5}. Sensitivity: add pairs with no relay read by hop 6 (never-treated). Pre-trend check: γ_{−2}, γ_{−3}.
- Secondary: G for relays that name C; the distribution of ρ (descriptive); the standard gate J₁ of the relay messages at C (RD on t_{m_B}) for comparison.
- CIs: day bootstrap over A's day (1-h blocks for short units), 200 draws; pooled per regime by inverse-variance weights.

**Synthetic validation first, on the real skeleton** (#51b, #38a, #27; real messages, reads and relays; synthetic talk outcomes at every call). Outcome logit = agent-day base + own previous talk + a shared OU field + Σ gated read effects.
- **W0, no coupling:** G within 2 SE of 0 in ≥ 90% of seeds; no pre-trend.
- **W1, gated per-read coupling** (every read message, named × 10, decaying over hops): G recovers the planted per-relay effect with |bias| < 30%.
- **W2, A-clock rival** (C responds only to messages it reads directly, with a dead time of one call; relays carry no effect): G ≈ 0, and the response sits in β_2.
- **Power** at the round-1 per-read size (regime III: named 0.17, unnamed 0.004; regime I: 0.03): ≥ 0.8 pooled, or the verdict is "inconclusive".

**Predictions.**
- **P-R6a:** pooled regime-III G > 0 with the CI above 0. Pre-trend γ_{−2} within 2 SE of 0.
- **P-R6b:** G for relays naming C ≥ 3 × G for the others (address gating carries through the relay).
- **P-R6c:** pooled regime-I G > 0.
- **P-R6d (descriptive):** the modal ρ is 2 in regime III (B posts at its read-out call; C's next call after that is its hop 2).
- **Kill rules.** (i) G ≤ 0, or its CI includes 0 with power ≥ 0.8 → the lag is not set by the read-out path: the graph clause fails. (ii) |γ_{−2}| > 2 SE and > G / 2 → design confounded; R6 is inconclusive. (iii) G significant in W0 or W2 synthetic worlds → estimator invalid; not scored.

### R2. Regime-I dead-time kernel
**Synthetic worlds on the real regime-I skeleton** (units #27 and #24: mixed chat-mode and computer-use calls, about 20% logged-start calls).
- True starts: logged calls and chained computer-use calls keep their `t_call`. Latency-placed calls get t* = t_first − L, with L drawn from the logged latency distribution of their mode.
- Talk is decided at t* from the real peer messages read in [t*_{c−1}, t*_c). Base logit by mode (chat ≈ 0.78, computer use ≈ 0.04) plus agent effects plus the planted gated kernel on the logit.
- Then the first record is redrawn as t* + L(mode, talk), and latency-placed starts are re-estimated as in the ledger: the first record minus the agent's median chained-call latency. The estimator sees only these estimated starts.
- Kernels: K0 (no coupling); K1 (hop-1 spike, decay 1.5 hops) with dead time d ∈ {0, 1, 2}; K2 (cumulative rise over hops 1–5).
- Estimates: the K = 6 boundary kernel on all recipients and on logged-start recipients only (≥ 80% logged calls). Also split by the mode of the recipient's in-flight call at t_m (chat vs computer use; set before the message, so not affected by it).

**Predictions.**
- **P-R2a (synthetic):** on logged-start recipients the onset hop equals d + 1 in ≥ 4/5 seeds for each d. The cumulative kernel at hop 5 is within 30% of the truth for K1 and K2.
- **P-R2b (artifact size):** in K0 worlds the all-recipient J₁ is within 2 SE of 0 (latency placement does not create a jump). The all-recipient kernel shows no rise over hops 2–5.
- **P-R2c (real data, logged-start recipients, #23–#31):** onset at hop 1, and the regime-I rise survives: the cumulative kernel at hop 4 exceeds hop 1 (pooled, one-sided 95%). Prior about 0.5.
- **P-R2d (mode split):** J₁ > 0 for recipients in chat mode at t_m, and for recipients in computer-use mode.
- **Kill rules.** (i) If P-R2a fails, the regime-I kernel beyond hop 1 is not identifiable: it stays unvalidated. (ii) If on logged-start recipients the hop-4 kernel ≤ hop-1, the regime-I "continuing rise" is withdrawn as a latency-placement artifact. (iii) If K0 worlds give a significant all-recipient J₁, the round-1 regime-I all-recipient J₁ is reported as biased by that amount.

### Round-2 amendments (dated; each says whether it is post hoc)
- **R6-A1 (2026-10-05 ~03:40 UTC; synthetic-based, before any real R6 statistic).** In W1 worlds the raw event step G was 2–4× the per-relay truth, because other items read at the same call bundle in. Fix: controls for the other agent items (unnamed, named) read at the outcome call and at the call before. Also: 1-h blocks in every unit, because day blocks in 5-day units gave anti-conservative CIs. W2 is implemented as a one-call dead time for every read: almost every message is a relay of something, so "relays carry no effect" equals "no coupling".
- **R6-A2 (POST HOC, after the real event study failed its pre-trend check).** Diagnosis worlds W0L and W1L: talk depends on the call's own interval to the next call (regime III: long calls are pauses; regime I: long calls are chat mode). Added estimator, also post hoc: a start-time RD at the relay posting time on C's calls, with anchors at C-hops ≥ 2 on A's clock (`r2lib.relay_rd`). This design is immune to the length bias of hop-indexed profiles, as in round-1 Amendment 2.
- **R2-A1 (POST HOC).** Splitting on the mode of the in-flight call is invalid by construction: the in-flight call is the RD's left anchor, so its mode sets the left limit. The split now uses the mode of the recipient's last call that started before t_m − W (outside the anchor window). Also post hoc: K0flat, K1d0flat and K1d2flat worlds (talk rate independent of mode), to separate estimator artifacts from the mode sequence.
- **R1:** the pre-registered estimator ran unchanged. Single-day units have no placebo statement 2 h away for some senders; those rows drop out of the placebo-corrected outcome only.

### Round-2 results (non-reserved data)
Code: `scheme/build_r2.py`; `analysis/r2lib.py`, `r2_content_synth.py`, `r2_content_run.py`, `r2_relay.py`, `r2_relay_rd.py`, `r2_kernel_I.py`, `r2_pairs.py`, `r2_write.py`, `r2_figs.py`. Data: `data/processed/H50-field-vs-coupling-transfer-lag/r2/` (17 MB of unit tables plus result parquets). Figure: `figures/r2_summary_col.pdf`. Estimates: 872 rows in `per_period_estimates` (round 2, plus a round-1 backfill of J₁ and the activity field excess). All CIs are 95%. Pooled numbers are inverse-variance means over units.

**R1: content couples at the read-out call (regime III).**
- *Synthetic (real skeleton, 5 seeds × 4 units).* Pooled over #51b, #38a and #51c:
  - N0 (no pull): 0/5 false positives. The unmatched contrast is negative, which reproduces H29's failure.
  - N1 (gated pull): bias −4% overall, −7% for named messages.
  - N2 (ungated pull): J^c_1 = −0.010 (0/5 with CI > 0). N3 (dead time 1): J^c_1 = 0.005 (0/5), J^c_2 > 0.
  - Regime I (#27): J^c_1 is attenuated about −40%.
  - Power: the named effect at quarter strength is found in 5/5 seeds from 3 units. The real pool has 16 units.
- *Real data.* 16 of 27 regime-III units are eligible; most two-room weeks (#36–#44) have < 200 hop-0 rows.

  | statistic (regime III, bge unless noted) | estimate | units CI > 0 / < 0 |
  | --- | --- | --- |
  | **J^c_1, all** | **0.033 [0.027, 0.039]** | 10 / 0 of 16 |
  | J^c_1, gte-modernbert | 0.046 [0.038, 0.055] | 12 / 0 |
  | J^c_1, `style_resid_period` | 0.038 [0.031, 0.045] | 10 / 0 |
  | J^c_1, self-repeats dropped | 0.032 [0.026, 0.037] | 11 / 0 |
  | J^c_1, age × latency-tercile matched | 0.047 [0.040, 0.055] | 10 / 0 |
  | **J^c_1 named / unnamed** | **0.077 [0.063, 0.091] / 0.016 [0.009, 0.022]** (×5) | 7 / 5 |
  | named / unnamed, gte | 0.094 [0.083, 0.105] / 0.019 [0.011, 0.026] | |
  | J^c_2 / J^c_3 (vs hop 0, matched age) | 0.039 [0.030, 0.047] / 0.011 [−0.005, 0.027] | |
  | regime I (36 units): J^c_1 all / named / unnamed | 0.020 [0.014, 0.025] / 0.012 [0.003, 0.022] / 0.014 [0.009, 0.020] | 10 / 2 |
  | regime I: J^c_2 | 0.051 [0.041, 0.061] (not validated) | |

**R6: graph clause.**
- **Pre-registered event study: inconclusive** (kill rule ii).
  - Regime III: G = 0.014 (SE 0.001), but the pre-trend γ₋₂ = +0.032 (SE 0.001; significant in 16/25 units).
  - Regime I: G = 0.032 (SE 0.001), but γ₋₂ = −0.092 (SE 0.002).
  - Diagnosis (W0L, no coupling, talk tied to call length) reproduces both signs and sizes: regime III γ₋₂ = +0.019 (5/5 seeds) with a spurious G of +0.009 (4/5); #27 γ₋₂ = −0.113 vs −0.092 real.
  - Cause: the reference call (e = −1) is the call in flight at the relay post, which is length-biased. It is a pause in regime III and a chat-mode call in regime I. The real profile is what a no-coupling world with length-dependent talk produces (figure b).
  - The pre-registered synthetic worlds missed this: their talk did not depend on call length.
- **P-R6d fails: reads batch.** C reads A and B's relay at the same call (ρ = 1) in 60% of relay pairs in regime III (ρ = 2: 19%) and in 41% in regime I (ρ = 2: 33%). Path length 2 collapses into one C-hop whenever B answers faster than C's next call (C pauses).
- **Post hoc relay RD at C-hops ≥ 2 (length-robust).**
  - Synthetic regime III: W0 −0.004, W0L −0.003; W1 0.020 vs truth 0.017; W1L 0.013 vs 0.016; W2 0.002.
  - Synthetic regime I: W0L gives +0.025, so the estimator is not valid there.
  - Real regime III (27 units): **J_relay = 0.014 [0.006, 0.022]** (5 / 0 units). Relays that name C: **0.115 [0.078, 0.152]**. Unnamed relays: 0.006 [−0.002, 0.014].
  - So C's response to A via B steps up at the call that reads B's relay, two or more C-hops after A. It does so only when the relay names C (×19, as for direct reads: H67's ×19, round-1's 0.17 vs 0.004).

**R2: regime-I kernel.**
- *Synthetic, latency placement.* In mode-free worlds latency placement creates no jump and no rise. K0flat all-recipient k₁ = −0.007 (#27) and 0.004 (#24); logged-start recipients ≈ 0.
- *Synthetic, dead time.* Dead times are recovered on all recipients: onset = d + 1 in 5/5, 5/5, 4/5 seeds (#27) and 5/5, 4/5, 4/5 (#24). On logged-start recipients: 4/5, 5/5, 5/5 (#27) and 3/5, 2/5, 4/5 (#24, only 2 logged agents).
- *Synthetic, pre-registered K0 (talk by the real mode sequence, no coupling).* It produces a rising kernel in #27: all recipients k₄ − k₁ = +0.024; logged-start recipients +0.107. #24 shows ≈ 0. The cumulative kernel at hop 5 misses the truth by more than 30% in mode-based worlds. **P-R2a fails on shape (kill i):** beyond hop 1 the regime-I talk kernel mixes coupling with the real mode sequence.
- *Real data (10 units, #24–#31), logged-start recipients.*
  - k₁ = 0.030 [0.021, 0.039] (onset hop 1 in 5/10 units); k₃ = 0.047 [0.034, 0.060]; k₄ = 0.043 [0.020, 0.066]; k₆ = 0.024 [0.000, 0.048].
  - k₄ − k₁ = +0.013, not significant. **P-R2c fails:** the "continuing rise" of round 1 is withdrawn. It is not shown to be a latency artifact; it is unsupported.
  - The hop-1 jump is not a latency artifact: logged-start 0.030 vs all recipients 0.025 [0.020, 0.030].
- **Chat-mode channel.** After a read, the next call is more often a chat-mode call: ΔP(chat mode) = 0.024 [0.019, 0.029] at hop 1, held at 0.026–0.041 to hop 6. With talk rates of 0.78 (chat) and 0.04 (computer use), switching mode accounts for about 0.018 of the 0.025 talk jump (about 70%).
- **Mode split (R2-A1).** Recipients in chat mode before the message carry the jump: k₁ = 0.110 [0.087, 0.133] (logged-start 0.158 [0.110, 0.206]). Recipients in computer use: 0.005 [0.003, 0.008] (logged-start −0.006 [−0.014, 0.003]). **P-R2d: mixed.**

**Outcome vs prediction (round 2).**

| Prediction | Observed | Verdict |
| --- | --- | --- |
| P-R1a content couples at hop 1 (III, both models, ≥ 1/3 units) | 0.033 [0.027, 0.039] bge, 0.046 [0.038, 0.055] gte; 10/16 units | **supported** |
| P-R1b named ≥ 3 × unnamed; unnamed CI includes 0 | ×5 (bge and gte); unnamed 0.016 [0.009, 0.022] | mostly supported (unnamed weakly > 0; kill ii not met) |
| P-R1c J^c_1 ≥ J^c_2 | bge 0.033 vs 0.039 (overlap); gte 0.046 vs 0.033; named 0.077 vs 0.056 | mixed (onset at hop 1; content persists to hop 2) |
| P-R1d regime I ≥ 0, unnamed couples | 0.020 [0.014, 0.025]; unnamed 0.014 [0.009, 0.020]; no named premium (named 0.012) | supported (attenuated; regime-I J^c_2 > J^c_1 not validated) |
| P-R6a relay step G > 0, no pre-trend | G > 0 but pre-trend significant in both regimes; length bias reproduced in W0L | **inconclusive** (kill ii); post hoc RD: 0.014 [0.006, 0.022] (III) |
| P-R6b naming C ≥ 3 × others | post hoc RD: 0.115 vs 0.006 (×19) | supported (post hoc estimator) |
| P-R6c regime I G > 0 | event study invalid; RD biased in regime I | inconclusive |
| P-R6d modal ρ = 2 | modal ρ = 1 (60% III, 41% I) | **failed** |
| P-R2a dead time and shape recovered (logged) | onsets mostly recovered; shape fails in mode-based worlds | failed on shape (kill i) |
| P-R2b no latency artifact | none in mode-free worlds; the mode sequence alone makes a rise in #27 | supported for latency; mode channel found |
| P-R2c regime-I rise survives (logged) | k₄ − k₁ = +0.013, n.s. | **failed** (rise withdrawn) |
| P-R2d J₁ > 0 in chat and computer-use mode | 0.110 vs 0.005 (logged: 0.158 vs −0.006) | mixed |

**Rivals.**
- **R1 (pure field) is rejected for content.** At matched age, read statements beat in-flight statements, and convergence cannot do this (N0 gives 0/5).
- **R2 (ungated) is rejected for content.** The synthetic ungated world gives J^c_1 ≤ 0, while the real J^c_1 is > 0.
- **The A-clock rival (a fixed dead time on the source's clock)** is beaten in regime III only by the post hoc RD: the step follows the relay's posting time.

**Scorecard (old → new):**
- **D 1 → 2:** the gated model predicted, before any content statistic, a hop-1 content jump with address gating. It holds in both embedding models and in 10/16 units.
- **F stays 1:** R1 and the dead-time recovery pass. The pre-registered R6 worlds missed the length bias, and the regime-I kernel shape is not identifiable.
- All other axes are unchanged.
- A1 B1 C1 D1 E1 F1 G1 H2 I1 → **A1 B1 C1 D2 E1 F1 G1 H2 I1**.

**For H67** (round-2 gain reconciliation): `data/processed/H50-field-vs-coupling-transfer-lag/r2/pair_J1.parquet` has the round-1 hop-1 talk jump per directed pair (sender → recipient, roster codes) and unit: 1,094 pairs with ≥ 300 reads, with SEs, read counts and named counts.

### Round-3 redirects
Listed under "Round 2 redirects" above (H50-R8 to R11, added 2026-10-05).

**Claim that stands:** In regime III, content couples at the recipient's read-out call, as talk does. The matched-age content jump is J^c_1 = 0.033 [0.027, 0.039] (whitened cosine, bge; gte 0.046 [0.038, 0.055]), with CI > 0 in 10/16 units and none below 0. It is address-gated ×5 (named 0.077 vs unnamed 0.016). *Excluded:* the graph-clause event study (inconclusive: length bias); the relay RD (post hoc, supporting only); regime-I content beyond hop 1 and the regime-I kernel shape (not identifiable: chat-mode channel); the regime-I mode split (post hoc amendment R2-A1).

## Notes
- 2026-10-04 05:40 UTC: round 1 started; card filled before any real-data statistic. The first attempt (2026-10-04 ~02:40 UTC) was cut off by an API limit after reading context and inspecting input counts; nothing had been written. DQ1's context ledger exists, so lags are in call cycles from the start (`exposure.lag_s` is not used: it overstates visibility lags).
- 2026-10-04 ~06:00–06:50 UTC: synthetic validation (three iterations; estimator fixes listed under Amendments), scheme build (NE43 bookend finding), amendments, then period predictions at 07:00 UTC, then the real-data run.
- 2026-10-04: coordinator's `activity_bins` bug notice received mid-run. H50 never used `activity_bins`, `outages` or `stall_minutes`, so nothing was rerun.
- 2026-10-04: robustness check added after the first real-data pass: the regime-I jump on logged-start recipients (`check_logged_starts.py`). The work/idle outcome split and the edges-vs-rest attribution were added after seeing that talk+wait calls are coded idle; both are reported as post hoc refinements.
- **Data finding (for the NE catalog):** the `automated` daily pause/resume bookends stop after **2026-08-04** (last resume and pause on 08-04), not on 08-21. Only the nudges stop after 08-20. NE43 as catalogued conflates two switch-offs.
- **Data finding:** in #38 the pause bookend arrives as agents are halted: 94% of agents make no call after it, and last calls end within about 23 s (q90). The bookend is an announcement, not an input.
- Proposed for `physics-models/DEFINITIONS.md` (outside H50's edit scope): *call cycle (hop)*, *read-out jump (gate coupling)*, *field excess (shifted-input null)*, *coupling share (CF, gated kernel)*, as defined in the Model section and Amendments.
- 2026-10-05 02:50 UTC: round 2 pre-registered (commit 582aecd), before any round-2 statistic. Order: scheme (`build_r2.py`), R1 synthetic → R1 real; R6 synthetic → amendment R6-A1 → R6 real (pre-trend failed) → post hoc diagnosis (W0L) and relay RD; R2 synthetic (K0 rise found) → added mode-free worlds → R2 real → amendment R2-A1 (split outside the anchor window). Then the pair table for H67, estimates, period blocks, figure.
- Data finding (round 2): in regime I, chat-mode calls talk 78% and computer-use calls 4%. After a peer message, the next calls are more often chat mode (ΔP 0.024). So regime-I "talk coupling" is mostly a mode switch.
- Method finding (round 2): hop-indexed event profiles around an event are biased when the outcome depends on call length, because the in-flight call is length-biased. Start-time RDs are not (regime III). In regime I even the start-time RD is biased (+0.025) in a world where talk depends on call length. Proposed as an `infra/README.md` Known issue.
- **Cross-note (2026-10-05, from H67 round 2, R3):** H50's talk J₁ magnitude (≈ 0.24 in gain units, about 2× g_lag 0.13) is an estimator artifact. In regime III it comes from the pair-RD design: about half is the local-linear extrapolation to s = 0 and half is pair sampling. The pair RD reads +0.05 to +0.07 with no coupling in synthetic worlds, and its scale exceeds the Fano bound (g_Fano 0.149 [0.123, 0.175]). In regime I it is call-class composition: agent × day × call-class cells remove 69–95% of it. H50's regime-I ΔP(chat mode) is about 3/4 chat-turn schedule (H67 skeleton null 0.0054 of 0.0080 per read; mode-free excess 0.035 [0.023, 0.046], post hoc). The hop-1 onset and the named/unnamed contrast stand.
- **Cross-note (2026-10-05, consolidation of round 2 wave 1): H50's unnamed content jump vs H08's negative unaddressed content.** The two numbers are different estimands. H50's "unnamed" restricts the *message*: m does not name the recipient, and every response statement counts, replies to the sender included (J^c_1 unnamed 0.016 [0.009, 0.022], regime III). H08's "no name, no reply" restricts the *response*: it drops statements that mention the sender or reply to it (Δ_cont −0.39 [−0.62, −0.12], G51). The nulls also differ: H50 uses a same-sender statement ≥ 2 h away and hop-0 statements at matched age in [0, 60) s on 32-d whitened vectors; H08 uses the same message against the recipient's statements 20–60 min away, with lag × density strata up to 300 s. H08's all-statement contrast is positive (+1.25 [+0.98, +1.60], G51), in line with H50's J^c_1 > 0. So the results are compatible if H50's unnamed jump rides on replies that answer the sender. That is not tested. The decisive run is H50's J^c_1 on response statements that neither name nor reply to the sender. Status: open.
