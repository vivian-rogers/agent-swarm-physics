# H50: Field or coupling: transfer functions and lag tell which

**Status:** exploratory round 1 done (2026-10-04). Predictions were written at 05:40 UTC, before any real-data statistic. Synthetic validation came first; amendments were written at 06:50 UTC, still before real data. Ran on 71 non-holdout units (35 goal periods) plus 4 native tests. Confirmatory script written and dry-run; **not run**.
**Headline: the field/coupling split is identifiable, and it falls along channels.**
- **Activity co-movement** (H12's market mode) is a **field**: the scaffold's daily start and stop. Edges alone explain 0.62 (regime I) and 0.67 (regime III) of it beyond a shifted-input null. Agents start within about 9–22 s of each other (under two call cycles), and in #38 they are halted at the pause message without reading it.
- **Talk co-movement** is a **gated coupling**. A peer message raises the chance that the recipient's *next* call is a talk call: J₁ > 0 in 45/71 units, < 0 in none, onset exactly at hop 1. The coupling changes *what* the read-out call does (talk instead of work); whether the agent is active is unchanged. A counterfactual built from this kernel accounts for roughly all talk co-movement (median f_C 0.92 in regime I, ≥ 1 in regime III).
- **HH167's regime split fails.** Regime-I calls are not message-triggered (wake ratio 1.03–1.07). Both regimes have field-driven activity and coupling-driven talk.
- **NE43** (as a native test): the nudge path vanishes after 08-20, while peer coupling and the day-start field persist. The bookends had already stopped after 08-04, which is a data finding.
- **Scorecard:** A1 B1 C1 D1 E1 F1 G1 H2 I1.
**Fields:** dynamics, stat mech, sociophysics, info theory
**Literature:** none of the notes in `literature/` covers system identification; the method references are in the model folders: Cugliandolo, Kurchan & Peliti, *PRE* 55, 3898 (1997)† (`physics-models/02-nonequilibrium-ising`, response vs correlation); Filimonov & Sornette 2015† (`physics-models/09-hawkes`, nonstationary baselines fake endogeneity). Standard linear-systems tools (FIR/ARX identification, Welch cross-spectra, coherence, group delay) and regression-discontinuity design need no project note.
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Population N(t) (variant *day-present*, H36); Regime; Driving / external field (human messages, nudges, operator bookends, platform errors); Interaction (broadcast) with **Exposure (turn read-out)** (H08; implemented by the shared context ledger); Action (turn-merged) via the ledger's calls; Agent state (vector), *whitened statement mean* basis (H01) for the content channel. **New named variants proposed for DEFINITIONS.md** (not edited here; outside H50's scope), defined under Model: *call cycle (hop)*, *read-out jump (gate coupling)*, *field share (measured)*, *coupling share (gated)*.
**From:** HH167 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` (approved by Vivian 2026-10-04); folds in HH185–HH190 where the data allow · **Models:** `physics-models/02-nonequilibrium-ising/` (linear response, response function R_ij), `physics-models/01-inverse-ising/` (equal-time co-movement, susceptibility), `physics-models/09-hawkes/` (kernels and their pitfalls)
**Data inputs (shared tables first):** `call_windows`, `context_ledger_turns`, `context_ledger_items` (DQ1), `kicks_classified`, `turn_errors`, `calendar`, `period_units`, `rooms_timeline`, `chat_core`, `chat_mentions_clean`, `embeddings/statements*` (content channel). No raw rescans.

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
| D unfitted predictions | unfitted statistics and the model's signature | 1 | The gated-coupling signature appears in 45 units: a step at the read-out call, onset at hop 1, no response before read-out, no unit with the ungated (J₁ < 0) pattern. The schedule-field signature (zero relative lag in call cycles) holds: onset IQR 9 s in #38 and 22 s in #51. Not predicted: regime III's plateau after the hop-2 drop, regime I's continuing rise, and the immediate (hop-1) nudge talk response. |
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
- **HH187 (quantized lags): tested at hop resolution.** The response is quantized at the read-out call (hop 1, never hop 0). The hop-distance-on-the-read-out-graph clause is round 2.
- **HH188 (T_eff(ω)): not tested.**
- **HH189 (dead-time stability): descriptive.** No damped oscillation. Human and nudge kernels undershoot after their peak (activity is advanced, not added). No phase margin estimated.
- **HH190 (per-agent transfer): partial.** Per-agent J₁ is strongly heterogeneous (Q = 685 on 16 df in I; 325 on 30 df in III) and tracks the agent's talk rate in regime III (r = 0.48). Lab medians are noisy.

### Caveats
- **Regime-I timing.** Chat-mode call starts are latency-placed, and talk calls run longer than the median latency, which could fake a talk jump. On logged-start (Gemini) recipients in #24–#31 the jump holds (0.030 ± 0.008), but early regime I (#2–#21) has no logged starts. The regime-I kernel beyond hop 2 (continuing rise) is not validated in synthetic worlds. The "certain items" sensitivity variant is invalid for an RD: it drops near-boundary pairs on one side.
- **Multiplicity and power.** Per-unit CIs come from a day bootstrap (1-hour blocks for units with < 3 days) and are mildly anti-conservative (synthetic false-positive rate ≈ 9%). 71 units × several statistics; the cross-unit counts are the evidence, not single units. The named-target and relay tests in #51 have about 100 pairs.
- **Decomposition shares are model-based and non-additive.** CF f_C > 1 is overshoot at low talk co-movement (median per-pair talk ρ̄ 0.01–0.04). Activity field excess depends on the full-window grid (pre-start minutes are zero).
- **NE43 confounds:** the #focus room split (08-05), the merge (08-24) and roster joins in C.
- **Content channel not done** (C3).
- **`activity_bins` bug notice:** H50 does not use that table; all series come from `call_windows`. Not affected.

## Round 2 redirects
**What the direction is really after:** which levers move a swarm together (fields) and which only propagate through who reads whom (couplings), measured in the units the scaffold imposes (calls), so an operator knows what an input will do to collective behavior.
- **H50-R1. Content gate (C3).** The read-out jump for content (whitened statement cosine to the source message), with H29's matched-age control, by hop. Does content couple at hop 1 the way talk does, and is it also address-gated in regime III?
- **H50-R2. Validate the regime-I dead-time kernel.** Build regime-I synthetic worlds with mixed chat-mode and computer-use calls and planted dead times. Re-estimate the kernel on logged-start recipients only, and split read-out calls by mode.
- **H50-R3. HH188 frequency-dependent T_eff.** Compare spontaneous talk cross-spectra with the gated response spectrum per band; and HH189's phase margin from the hop kernel and the talk loop gain.
- **H50-R4. HH190 agent impedance.** Per-agent kernels (gain, onset hop, persistence) against H29's net influence current and H32's information current; family and scaffold clustering with partial pooling.
- **H50-R5. Human-input relay with power.** Pool the human-rich regime-I periods (#4–#6) and use the hop 2–4 kernel for bystanders, with 3W bandwidth.
- **H50-R6. HH187 graph clause.** Lags vs hop distance on the read-out graph (A reads B reads C): does C's response to A appear at hop 2 of C's calls?
- **H50-R7. Confirm on the holdout** (`confirm.py`: CP1–CP5, NE23 nudger off/on).

## Notes
- 2026-10-04 05:40 UTC: round 1 started; card filled before any real-data statistic. The first attempt (2026-10-04 ~02:40 UTC) was cut off by an API limit after reading context and inspecting input counts; nothing had been written. DQ1's context ledger exists, so lags are in call cycles from the start (`exposure.lag_s` is not used: it overstates visibility lags).
- 2026-10-04 ~06:00–06:50 UTC: synthetic validation (three iterations; estimator fixes listed under Amendments), scheme build (NE43 bookend finding), amendments, then period predictions at 07:00 UTC, then the real-data run.
- 2026-10-04: coordinator's `activity_bins` bug notice received mid-run. H50 never used `activity_bins`, `outages` or `stall_minutes`, so nothing was rerun.
- 2026-10-04: robustness check added after the first real-data pass: the regime-I jump on logged-start recipients (`check_logged_starts.py`). The work/idle outcome split and the edges-vs-rest attribution were added after seeing that talk+wait calls are coded idle; both are reported as post hoc refinements.
- **Data finding (for the NE catalog):** the `automated` daily pause/resume bookends stop after **2026-08-04** (last resume and pause on 08-04), not on 08-21. Only the nudges stop after 08-20. NE43 as catalogued conflates two switch-offs.
- **Data finding:** in #38 the pause bookend arrives as agents are halted: 94% of agents make no call after it, and last calls end within about 23 s (q90). The bookend is an announcement, not an input.
- Proposed for `physics-models/DEFINITIONS.md` (outside H50's edit scope): *call cycle (hop)*, *read-out jump (gate coupling)*, *field excess (shifted-input null)*, *coupling share (CF, gated kernel)*, as defined in the Model section and Amendments.
