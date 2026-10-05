# H08: Context is the coupling

**Status:** round 1b done (2026-10-04, improved data): on the context ledger, responses are gated by read-out in every regime (addressing 14/17 periods, reply author 17/17; regime I's round-1 failure was the call-start rule), the nudge response starts at the receiving call (the ~3-min post-read-out lag was an artifact), erasure cuts reply coupling 21% (NE41), and newcomers name an old-timer only after receiving its message (NE32, 35/35). Round 1 (below) kept for comparison. Holdout script written, not run.
**History:** reactivated 2026-10-04 (Vivian: start the hypotheses never worked on). Originally parked on 2026-10-03 after a misread. Since then H04 (delayed, context-mediated responses), H15 (context-erasure dip, NE41) and H18 (attention dilution) have all pointed at it. Primary test: HH92, the response kernel predicted from turn timing.
**Exploratory round 1 done (2026-10-04; 17 non-holdout goal periods + NE41; predictions written before any real-data run).**
- **Coupling is gated by read-out (C9).** A recipient's chance of addressing a sender jumps at the first turn whose model call started *after* the message, and not before. This holds in 10/11 regime-II/III periods. Among recipients who had not just talked, the jump holds in 16/17 periods and the in-flight floor is ≈ 0. That explains H18's failed placebo.
- **HH92 is not supported for nudges (C8).** In #51 the read-out comes fast (median 1.7 min), but the activity response starts at ≈ 5 min. A constant delay fits as well as the zero-parameter read-out model; immediate and Hawkes kernels lose.
- **Context erasure cuts coupling (NE41).** Forced consolidation lowers the chance of addressing senders read before it by 18% (9/9 periods negative; predicted ≥ 30%).
- **Ground truth breaks the room rule (C1).** The Claude Code agent's fetches match the room rule (recall 0.97–1.00) until 2026-03-17, when its feed began replaying the village from April 2025.
- **HH91.** #51's afternoon halves run hotter (n̂ 0.70 vs 0.50).
- Period verdicts: 6 supported, 11 failed (all on the talk clause; every regime-I/II period). NE41 mixed. Scorecard A1 B1 C1 D1 E1 F1 G1 H1 I1. Holdout script written, not run.
**Round 1b (2026-10-04, improved data): see "Round 1b" below.** Period verdicts (1b): 6 supported (G36 replaces G44), 11 failed (talk clause only); natives NE32 supported, NE41 mixed, NE03 descriptive. Scorecard A1 B1 C1 D1 E1 F1 G1 **H2** I1.
**Fields:** info theory, dynamics, stat mech
**Literature:** [Kolchinsky & Wolpert 2018](../../literature/kolchinsky-2018-semantic-information-autonomous-agency.md) (interventions on information channels)
**Definitions used:** Interaction / exposure (broadcast; `physics-models/DEFINITIONS.md`); Regime; Action (turn-merged); Driving / external field. New operational terms ("call start (pause-aware)", "read-out time", "in-flight turn") are defined under "Operational definitions" and proposed for DEFINITIONS.md as the named variant **"Exposure (turn read-out)"**.
**Origin of the primary test:** HH92 (messages couple to a hidden variable); HH91 (longer sessions run hotter) as C10.

## Standards (2026-10-04)
**Question served:** Q1 (coupling is gated at the recipient's read-out call).

| Impostor | Relevant? | How it was handled | Status |
| --- | --- | --- | --- |
| Scheduler field | partly | Turn-offset discontinuity within each recipient's call sequence; pseudo-message null with the same pair at shifted times (Null / baseline). | removed |
| Exogenous field (kickoff/goal/operator) | partly | Common cause (both agents react to one earlier event) is simulated in the synthetic validation; other-room placebo passes 8/8 (Round 1b). A shared field cannot create a jump at the read-out call. | removed |
| Shared model priors | no | The design compares the same recipient before and after read-out. | n/a |
| Contemporaneous convergence | yes | The in-flight floor is the in-flight placebo: messages posted but not yet read give ≈ 0 (C9 on the ledger, Round 1b). The content jump is negative in regime I (recency confound). | removed |

**Inputs:** round 1b uses the context ledger, DQ2 reply pairs and H04's round-1b nudge design (`activity_bins_fixed`, leading-@). Still old: the content response uses bge only; C1, C2 and C10 were not re-run.

**Two layers:** 17 replication periods. Natives: 3 (NE32 supported, NE41 mixed, NE03 descriptive).

**Confirm script:** `confirm_holdout.py` (CF1–CF5), written, not run. Re-freeze: yes; it still builds round-1 inputs and must switch to the ledger (holdout item 10).

## Question
Agents interact *only* through what enters their context. So the coupling between agents is, mechanically, *context inclusion*: what each agent saw, and when. How faithfully can we reconstruct that from the logs, and how much of each agent's behavior does it explain?

Every other direction needs a good answer. Contagion, couplings (S1, S4), field vs. coupling (S5) and H01's natural scrambles all rest on an exposure model.

## Data situation
- **The exact prompts (`llm_calls`) are not public.** AI Digest publishes only `aidigestorg/ai-village`, which has no `llm_calls` file; the prompts are available on request to vetted researchers. Vivian can't obtain them (2026-10-03), so **C4–C6 are blocked**. C1–C3 remain possible from the Claude Code agent's stream and the token accounting.
- **Ground truth for one agent.** The Claude Code agent ("Opus 4.5 (Claude Code)", 2026-01-26 → 04-02) logged its full input side in `claude_code_messages`:
  - every village-API fetch, with the event IDs it returned, `unseenEventsCount`, `hasMore`, the current goal and memory-update reminders;
  - context compactions, with `pre_tokens`;
  - synthetic continuation summaries.

  Its tenure spans the rooms change (NE12, 2026-02-25).
- **Per-call token accounting for everyone.** `computer_use_turns.agent_messages` holds provider responses (no prompts, no sampling parameters) with input tokens and prompt-cache reads and writes. The uncached part of the input is a proxy for *new context per call*.

## Sub-hypotheses
- **C1 · Exposure reconstruction.** A room-based rule ("an agent sees every event in its room between its consecutive turns") reproduces what the agent actually saw.
- **C2 · Information inflow.** New context per call (uncached input tokens) tracks room activity, and drives the next action's latency and type: a Green's function from inflow to action.
- **C3 · Context compression.** Compactions and consolidations are erasure events: their frequency and the context size just before them behave like an equation of state (HH57). *Round 1 adds the NE41 coupling test: erasing the context cuts the coupling to what was in it.*
- **C4 · Context → action attribution.** Which context elements predict the next action. Needs `llm_calls` for the standard agents; the Claude Code agent first. **Blocked.**
- **C5 · Scaffold ground truth.** Exact prompt diffs at each natural experiment, turning field changes into measured ones. Needs `llm_calls`. **Blocked.**
- **C6 · Replay.** Counterfactual scrambles for H01 (Tier R). Needs `llm_calls`. **Blocked.**
- **C7 · Sampling parameters.** A literal temperature, from the operators. Not pursued.
- **C8 · Zero-parameter response kernel (HH92; primary).** The response of an agent's activity to a message is the read-out delay (the wait until the agent's next call starts) convolved with a fast response. So the kernel G(τ) measured by H04 is predictable, with no free shape parameter, from the agent's turn schedule. *Added 2026-10-04.*
- **C9 · Visibility discontinuity (agent → agent).** An agent's turn can respond to a room message only if the model call that produced it started after the message arrived. Responses (talking, addressing the sender) should jump at the first such turn and not before. *Added 2026-10-04.*
- **C10 · Longer sessions run hotter (HH91).** The unread backlog per turn grows with time in the session and raises the branching ratio. *Added 2026-10-04.*

## Model
**From:** `physics-models/02-nonequilibrium-ising` (kinetic Ising: response function, update order) and `physics-models/09-hawkes` (kernels, branching ratio), with `04-semantic-information` for the erasure reading of C3. H08 is also the measurement that calibrates the exposure input of models 01, 02, 03, 09, 11 and H01.

**Two-variable kinetic model (H08 variant, written 2026-10-04).** Each agent i has
- a visible spin n_i(t) ∈ {0, 1}: active in minute t (H04's activity);
- a hidden field c_i(t): the *unread context*, the set of events posted in i's room since i's last call start;
- a turn schedule set by the scaffold: call starts s_{i,1} < s_{i,2} < … . A call starts when the previous action finishes, or when a self-declared pause timer expires (H09: room messages do not interrupt pauses).

At each call start s, the unread context is read into the prompt and reset (c_i → ∅). The action that call produces is a kinetic-Ising update with local field
  H_i(s) = h_i + Σ_{e ∈ c_i(s)} J_{i, src(e)}.
Couplings therefore act **only at read-out**. For a message arriving at t_m, the response of i is
  G_i(τ) = Σ_w p_i(w | t_m) · ΔR_i(τ − w),
where p_i(w | t_m) is the distribution of the read-out delay w (from the turn schedule) and ΔR_i is the response after read-out. With a fast step response ΔR = A·Θ(τ − w), the kernel's shape is the read-out CDF:
  G(τ) = A · F_W(τ),
with **no free shape parameter**. For messages arriving at random times, renewal theory gives the residual-wait density p_ren(w) = S_Δ(w)/⟨Δ⟩, where S_Δ is the survival function of the intervals Δ between call starts (inspection paradox).

**Rivals:**
- (R1) **immediate coupling:** the message acts on activity at once, G = A for τ ≥ 1;
- (R2) **constant delay:** an intrinsic processing dead time d, G = A·Θ(τ − d);
- (R3) **Hawkes exogenous kernel:** G = A e^{−(τ−1)/θ}, a response that peaks at once and decays;
- (R4) **memory-mediated coupling:** the message matters only after it has gone through memory (the next consolidation); used in the synthetic validation and in C3;
- (R5) **flexible fitted kernel** (gamma-CDF rise, 3 parameters): a fit-quality ceiling, not a mechanism.

## Data scheme (`scheme/`)
- **C1 script:** `scheme/build_cc_exposure.py`.
  - **Inputs:** `claude_code_messages`, `events` (id → event index, type, actor, room; one pass, no text kept), the shared `rooms_timeline`, `calendar`, `roster`.
  - **Outputs** (`data/processed/H08-context-is-the-coupling/`):
    - `cc_fetches.parquet`: one row per village-API fetch;
    - `cc_seen.parquet`: one row per event seen, with event time, fetch time, delay, type, actor and room;
    - `cc_usage.parquet`: per assistant message: input, cache-read, cache-write and output tokens;
    - `cc_compactions.parquet`;
    - `cc_village_events.parquet`: the village events of the agent's tenure (no text), for the room-rule reconstruction.
  - **Regimes covered:** I (to 2026-02-25), II (to 03-24), III (to 04-02).
- **C8–C10, C2, C3 script:** `scheme/build_turns.py`, from the shared tables only (`actions`, `events_core`, `chat_core`, `chat_mentions_clean`, `exposure` (membership only, not `lag_s`), `calendar`, `roster`). Outputs per goal period (`G<NN>/`):
  - `turns.parquet`: one row per turn-merged action of each agent: time, pause-aware call start, talk / pause / consolidate flags, mentions, provider-aware uncached and context tokens;
  - `readout.parquet`: one row per (message, room recipient): read-out delay, in-flight flag, turn offsets.
  - Holdout days are dropped before anything is computed (`common.holdout_mask` and `calendar.holdout`).
- Kernels (C8) reuse H04's machinery by import (`hypotheses/H04-reversible-forcing/analysis/h04lib.py`); the consolidation catalog (C3) reuses H15's `consolidations.parquet` (forced = 41–42-turn segment, voluntary = 10–38); the backlog k (C10) reuses H18's `talks.parquet`. None of those files is modified.

## Operational definitions (written 2026-10-04, before any real-data run)
- **Turn of i:** an `actions` row of i (excluding the `pause` mirrors) or an `events_core` event with actor i; rows within 1 s of the previous one merge into one turn ("Action (turn-merged)"). A **talk turn** contains an `AGENT_TALK`; a **pause turn** contains a `PAUSE` (with `pause_s`); a **consolidation turn** contains a `CONSOLIDATE`.
- **Call start s(τ) (pause-aware):** the time of i's previous turn, except after a pause turn, where it is min(t_pause + pause_s, t_τ − 1 s) (the wake). The first turn of a PT day has s = −∞ (everything posted earlier that day is visible to it).
- **Read-out time R_i(m)** of a message m (posted at t_m in i's room): the time of i's first turn τ with s(τ) > t_m, i.e. the first action produced by a call that started after the message. **Read-out delay** W = R − t_m. A turn with t_τ > t_m but s(τ) ≤ t_m is **in flight**: its call was already running when m arrived, so it cannot respond to m.
- **Room recipients:** the `exposure` rows of the message (room occupants at posting); `exposure.lag_s` is not used (Known issues).
- **Kick sets (C8):** exactly H04's (`h04lib.load_messages`, `build_sets`): nudge → target (`nudge_target_iso`), human → mentioned agent, human → room occupants; isolation on direct kicks in [−30, +60] min; daily pause/resume bookends excluded.
- **Read-out minute** of a treated cell: τ_r = ⌊(R − start of the kick minute)/60 s⌋. **Predicted kernel shape** F(τ) = P(τ_r ≤ τ) over the period's treated cells, in three versions:
  - F_obs: R from the observed turns (primary);
  - F_sched: for agents in a declared pause at the kick, R = pause expiry + 10 s (fixed in advance; set before the kick, so strictly pre-treatment); otherwise as F_obs;
  - F_ren: renewal residual from the period's distribution of call-start intervals (no kick information at all), with a uniform offset inside the kick minute.
- **Onset fraction** Φ(a, b) = mean_{τ∈[a,b]} G(τ) / mean_{τ∈[16,45]} G(τ): how much of the late plateau the kernel has reached by minutes a–b. Φ_pred uses F in place of G. Primary: Φ(1, 5); secondary: Φ(6, 15).
- **Pause bin (pre-treatment):** at time t, i is in a declared pause if its latest turn before t is a pause turn and t is before its expiry; remaining time r = expiry − t, binned {not paused, ≤ 2, 2–5, 5–10, 10–20, > 20 min}. Used as an extra matching stratum in the **pause-matched kernel** (H04's strata × pause bin, evaluated at the cell's minute + 30 s).
- **Turn offsets (C9):** o = 1 is the read-out turn; o = 0 the turn just before it (in flight if t > t_m); o = −1, −2 earlier turns; o = 2, 3 later turns. Units for the discontinuity are (message, recipient) pairs whose o = 0 turn is in flight.
- **Responses (C9):** talk (turn o is a talk turn); addressing (turn o is a talk turn whose `chat_mentions_clean.mentions_roster` contains the sender; agent senders with detectable names only).
- **Pseudo-message null (C9):** the same (sender, recipient) pair at t′ = t_m ± U(20, 60) min, same PT day and window; G(o) = mean y_o(real) − mean y_o(pseudo). **Other-room placebo** (two-room era): messages from a room the recipient is not in, same construction.
- **Uncached tokens per call (C2):** H09's provider-aware rule: "exclusive" accounting (Anthropic: tok_in excludes cache reads): uncached = tok_in + tok_cache_write, context = tok_in + tok_cache_read + tok_cache_write; "inclusive" (Gemini): uncached = tok_in − tok_cache_read, context = tok_in; other providers null. **New messages at a call:** room messages by others with s(τ_prev) ≤ t_m < s(τ).
- **Erasure units (C3/NE41):** (talk turn τ of i, agent sender j in i's room) where j's latest message before s(τ) has age a = s(τ) − t_mj ∈ (0, 30] min and was already read by an earlier call of i ("old"); **erased** = a `CONSOLIDATE` of i lies between the read-out of m_j and s(τ); forced / voluntary from H15's catalog. **Post-consolidation turn** PC(τ) = a consolidation of i in the 30 min before s(τ). Response: τ addresses j.
- **Backlog per talk turn (C10):** H18's k (messages by others in i's room since the call start of i's previous talk turn), from H18's `talks.parquet`. **Session hour:** hours since the day's window start.

## Observables
- **C1:** delay (fetch time − event creation), coverage by event type and by room (own vs. other), and the room rule's **recall** (share of events the agent truly saw, excluding its own, that the rule predicts) and **precision** (share of rule-predicted events it saw), per goal period.
- **C8:**
  1. per period, H04's kernel G(τ) for nudge → target (H04 design), and the pause-matched kernel;
  2. Φ(1, 5) and Φ(6, 15), measured vs predicted from F_obs, F_sched, F_ren (day-bootstrap CIs, B = 500);
  3. day-split cross-validation (100 random half-splits): weighted held-out SSE over τ ∈ [1, 45] for M_ctx (A·F, 1 parameter; F from the held-out fold's own cells), M_ctx-d (context with an exponential decay after read-out, 2), R1 immediate (1), R2 constant delay (2), R3 Hawkes exponential (2), R5 gamma CDF (3);
  4. read-out stratification: pause-matched kernels for kicks to agents with ≥ 5 min of declared pause left vs to non-paused agents;
  5. the same Φ comparison for human → mentioned agent and human → room, by regime (exception (d): too few per period), as secondary.
- **C9:** per period, G_talk(o) and G_addr(o) for o ∈ {−2, …, 3}; the discontinuities D_talk = G_talk(1) − G_talk(0) and D_addr = G_addr(1) − G_addr(0); the other-room placebo; the decay G(2)/G(1); the physical read-out delay W of active recipients (median, IQR). Day-cluster bootstrap, B = 200.
- **C2:** per regime-III period, the within-agent-day slope b of log(1 + uncached) on log(1 + new messages) and its partial R²; the talk-turn ratio P(talk | ≥ 1 new message)/P(talk | 0); Spearman ρ between uncached tokens and call latency (t_τ − s(τ)) within agent-days.
- **C3 / NE41:** β_F and β_V, the change in the probability of addressing an "old" sender when a forced (voluntary) erasure separates its read-out from the talk turn, from a linear probability model with agent×day effects, 5 age bins, the engaged flag (i addressed j in its previous talk turn), PC(τ), and a pending-sender (new) indicator; per period and random-effects pooled. Equation of state: within-period Spearman ρ between a voluntary segment's length and its mean uncached tokens per turn; pre-consolidation context size, forced vs voluntary.
- **C10:** per period, Spearman ρ and the within-agent-day slope of log(1 + k) on session hour; Hawkes n̂ (H04's fitter, agent chat, 10 s bins) on the first vs second half of each day (#51, and regime-III 4 h periods with ≥ 5 days); across #51's weeks, ρ(n̂, mean k).

## Null / baseline
- **C1:** "sees everything instantly" (all-to-all, zero delay) and "sees only its own room's chat".
- **C8:** the rivals R1–R3 and R5 (model section); for each Φ, the immediate-coupling value Φ = 1. Matched no-kick controls throughout (H04), and pause-matched controls for the stratified test.
- **C9:** the pseudo-message null (same pair, shifted time), and the other-room placebo. **Common cause** (both agents reacting to the same earlier event) is the strongest rival: it raises responses at o ≤ 0. It is simulated in the synthetic validation to measure the discontinuity it alone can produce.
- **C2:** zero slope; tool output and screenshots dominate the uncached tokens, so the message share may be negligible.
- **C3:** memory-mediated coupling (R4) and "consolidation is only a restart overhead": no difference between old senders read before vs after the erasure, at equal age, in the same post-consolidation talk turns.
- **C10:** no trend in k with session hour; n̂ equal in the two halves; the week-to-week noise of n̂ (H04's placebo: |Δn| median 0.12 between adjacent weeks).

## Prediction (round 1)
*Written 2026-10-04 (~01:30 UTC), before any H08 analysis of real data.* **What had been looked at:** schemas; the CHANGELOG; the turn order of one regime-III agent-day and one pause (to fix the call-start rule: a wake call starts at the pause expiry); the regime-III pause-duration distribution (median 3 min, 90th percentile 15 min); the key structure (no values) of the Claude Code stream and its `get_events` results; the Claude Code agent's room timeline; goal-period dates. **Known from other cards:** H04's pooled regime-III nudge kernel (≈ 0 for 1–4 min, plateau from ≈ 15 min; share of A30 after 5 min 0.99); H18's β ≈ 0.6 and its failed invisible-message placebo; H15's forced-erasure write dip; H09's 0.22% early wakes; H03's fast cross-triggering at 10–30 s.

**Per-period rule.** Each `goalperiod-subhypotheses/G<NN>/README.md` restates the predictions that apply to that period, dated before that period is run. C8 is judged per period where a period has ≥ 30 isolated nudge-target cells; smaller periods are pooled within regime III with random effects (exception (d)) and labelled as such.

| # | Prediction | Counts against |
| --- | --- | --- |
| C8-P1 | **Onset shape is the read-out CDF.** Measured Φ(1, 5) agrees with Φ_pred from F_obs (the 95% CI of the difference includes 0) in every powered period and in the pooled small periods, and the immediate-coupling value Φ = 1 is excluded | difference CI excludes 0, or Φ(1, 5) ≈ 1 |
| C8-P2 | **No dead time beyond the scheduler.** The predicted F_obs reaches half its 45-min value between 3 and 15 min for nudge targets (most are in pauses or long gaps when nudged), matching H04's 4-min dead time and ≈ 15-min plateau | t½ outside [3, 15] min |
| C8-P3 | **M_ctx wins the cross-validation:** lower held-out SSE than R1, R2 and R3 in ≥ 60% of splits, and within 10% of R5 (median ratio ≤ 1.1) | a rival wins in ≥ 60% of splits, or R5 is > 10% better |
| C8-P4 | **The renewal version misses the nudger's selection:** F_ren predicts a faster onset (Φ_ren(1, 5) > Φ_obs(1, 5)) for nudges, because the nudger picks idle agents; for human → room the two agree within 0.15 | Φ_ren ≤ Φ_obs for nudges |
| C8-P5 | **Read-out stratification:** in the pause-matched design, kicks to agents with ≥ 5 min of declared pause left show Φ(1, 5) < 0.3, kicks to non-paused agents Φ(1, 5) > 0.5; the difference has a CI excluding 0 where powered (#51) | equal onsets in the two strata (the R2 signature) |
| C8-P6 | **Human → mentioned agent responds at once because the mentioned agents are mostly active:** Φ_pred(1, 5) ≥ 0.5 and the measured Φ agrees (regime-pooled; likely underpowered) | measured immediate response with Φ_pred < 0.3 (mentions wake agents: a channel outside the model) |
| C9-V1 | **Talk jumps at read-out:** D_talk > 0 with the CI excluding 0 in ≥ 70% of periods | D_talk ≤ 0 in > 30% of periods |
| C9-V2 | **Addressing jumps at read-out, with a contaminated floor:** D_addr > 0 (CI excludes 0) in ≥ 70% of periods; G_addr(0) > 0 (H18's placebo) but G_addr(0) < ½ G_addr(1) in most periods | G_addr(0) ≥ G_addr(1) in most periods (mentions are not responses to visible messages) |
| C9-V3 | **Other rooms are invisible:** in the two-room-era periods (#35–#42, #44), the other-room placebo has \|D\| below a third of the own-room D, with a CI including 0 | other-room D comparable to own-room D |
| C9-V4 | **Fast response:** G_talk(2) < G_talk(1) in ≥ 70% of periods (the response sits on the first visible turn) | flat or rising after o = 1 |
| C9-V5 | **The physical kernel is the turn cadence:** the median read-out delay W of in-flight (active) recipients is 10–40 s in regime III, the window of H03's fast cross-triggering | median W outside [10, 40] s |
| C1 | as written on 2026-10-03 (below), scored per the amendment below | see below |
| C2-I1 | b > 0 with the CI excluding 0 in ≥ 70% of regime-III periods, but messages explain little: partial R² < 0.05 | b ≤ 0, or R² ≥ 0.05 (messages dominate inflow) |
| C2-I2 | P(talk \| ≥ 1 new message) / P(talk \| 0) > 1.2 in ≥ 70% of periods; ρ(uncached, latency) > 0 in ≥ 70% | ratio ≤ 1 |
| C3-E1 | **Erasure cuts the coupling:** β_F < 0 (CI excludes 0) in ≥ 2/3 of regime-III periods with ≥ 300 erased units; pooled relative drop ≥ 30% of the non-erased rate at the same age | β_F ≈ 0 (memory carries the coupling, R4) |
| C3-E2 | β_V within ±50% of β_F (forced and voluntary erasures cut alike; forced gives the exogenous-timing estimate) | β_V and β_F of opposite sign with non-overlapping CIs |
| C3-E3 | Equation of state: voluntary segments are shorter when inflow per turn is higher (ρ < 0 in ≥ 2/3 of periods) | ρ ≥ 0 in most periods |
| C10-L1 | (HH91 as stated) k grows with session hour: ρ > 0 and slope CI > 0 in ≥ 2/3 of regime-III periods | no trend or a decline |
| C10-L2 | n̂(second half) − n̂(first half) > 0 in #51 with a day-bootstrap CI excluding 0 | Δn̂ ≤ 0, or inside the week-to-week noise |
| C10-L3 | across #51's weeks, ρ(n̂, mean k) > 0 | ρ ≤ 0 |

**Prior credences (Claude, 2026-10-04):** C8-P1 0.6, P2 0.55, P3 0.5, P4 0.7, P5 0.55, P6 0.35; C9-V1 0.6, V2 0.55, V3 0.6, V4 0.6, V5 0.5; C2-I1 0.5, I2 0.5; C3-E1 0.45, E2 0.5, E3 0.35; C10-L1 0.3, L2 0.3, L3 0.35.

**Synthetic guard (axis F; run before real data).** On real turn skeletons (non-holdout #38 and 15 days of #51), inject synthetic kicks at nudger-like cells (agents idle for ≥ 8 of the previous 15 min) and synthetic responses under four truths: context (step from the read-out minute), immediate (step from the kick minute), constant delay (8 min), memory-mediated (step from the next consolidation). Pass if: under context truth, M_ctx wins the CV in ≥ 80% of replicates and the Φ difference CI covers 0 in ≥ 80%; under immediate and memory truths, M_ctx loses and the Φ difference CI excludes 0 in ≥ 80%. For C9: under injected read-out responses D recovers the injected effect within ±30%; under a pure common-cause process the spurious D is reported, and real-data D is read relative to it.

## Synthetic validation (axis F; run 2026-10-04 before any real-data fit)
`analysis/synthetic.py`; outputs `data/processed/H08-context-is-the-coupling/synthetic/c8_synthetic.json`, `c9_synthetic.json`. Skeletons: real activity states, turns and kicks of non-holdout #38 (17 days) and the first 15 non-holdout days of #51. Real kicks stay in the data as direct hits (so they stay out of the controls) but are not treated. 6 replicates per configuration; ~150–200 synthetic kicks per replicate; responses flip inactive minutes to active with probability p for 60 min from the onset the truth sets.

**C8 (kernel).** The CV winner below is the model family with the lowest median held-out SSE in a replicate:
- ctx = ctx, ctx_step, ctx_d;
- imm = imm, imm_hr;
- delay = delay, delay_hr.

| Skeleton · selection · p | Truth | A30 (mean) | Pooled Φ(1,5) measured / predicted (F_hr) | CV winner (6 reps) |
| --- | --- | --- | --- | --- |
| #38 · random idle · 0.35 | context | 3.1 | 0.36 / 0.55 | **ctx 6/6** |
| | immediate | 6.2 | 0.78 / 0.57 | **imm 5/6** |
| | delay 8 min | 4.6 | 0.02 / 0.57 | **delay 5/6** |
| | memory | 1.4 | −0.09 / 0.57 | gamma 6/6 (ctx loses 6/6) |
| #38 · random idle · 0.12 (H04-like signal) | context | 0.8 | 0.50 / 0.57 | ctx 4/6, gamma 2/6 |
| | immediate | 1.9 | 0.86 / 0.57 | imm 5/6 |
| | delay 8 min | 1.4 | 0.07 / 0.58 | gamma 3, delay 2, imm 1 |
| | memory | 0.3 | −0.05 / 0.57 | gamma 4, ctx 2 |
| #38 · nudger-like idle · 0.12 | context | 1.0 | 0.62 / 0.63 | imm 3, ctx 2, delay 1 |
| | none (null) | −0.16 (pre-window −0.8) | — | — |
| #51 · random or nudger-like idle | context, memory | ≈ 0 | — | uninformative |
| | immediate / delay | 3.6–10.7 / 2.2–8.5 | 0.9–1.0 / 0.0–0.1 vs 0.35–0.40 | imm 6/6, 4/6; delay 5/6 (p = 0.12) |

**What the synthetic run showed:**
1. **The plain step overpredicts the early response.** After read-out the agent is usually active anyway, so extra activity needs *headroom*. The step F gives Φ(1, 5) ≈ 0.8 where the truth is ≈ 0.4–0.6. Weighting the step by the post-wake inactivity profile h(u) fixes most of it. h(u) is measured on no-kick cells with the same state at m−1 and the same exact number of idle minutes in the previous 15 (amendment A1).
2. **H04's coarse strata leave a pre-kick imbalance.** With nudger-like selection, G over [−15, −1] is −0.8 under the null, and the first 1–2 post-kick minutes are depressed. So under the context truth, Φ measured runs 0–0.2 below the prediction. Exact idleness matching removes the pre-window imbalance (−0.8 → 0.00) but shows a +1.2 A30 bias under the null with my 90-min-spaced nudger-like kicks. That design is therefore only a sensitivity check (A4).
3. **Power.**
   - At high signal, the CV identifies all four truths in #38 (5–6/6).
   - At H04-like signal (A30 ≈ 1–2, ~150–200 kicks) it identifies the context truth in 4/6, and much less under nudger-like selection.
   - Per-period Φ CIs are too wide to separate the truths at realistic signal.
   - **Per-period C8 verdicts will mostly be inconclusive.** The pooled regime-III kernel (exception (d)) carries the cross-period statement.
4. **#51 skeletons give no testable response under the context truth.** Idle agents in #51 sit in long silences, with read-outs more than 60 min away. In #51, the context model therefore predicts a small or late kernel wherever the targets' own read-outs are far.
- **Guard (as pre-registered): passes at high signal in #38** (CV ≥ 5/6 correct for all four truths). **Fails at realistic signal** (context 4/6 < 80%; Φ difference rarely excludes a wrong truth). Real-data C8 is read accordingly.

**C9 (discontinuity), #38 turns, 3 replicates, q = 0.15:**
- **Injected read-out responses** give D_talk = 0.11–0.14 and D_addr = 0.13–0.15 (the truth is 0.15 × (1 − talk base rate) ≈ 0.14), with G(o ≤ 0) ≈ 0.
- **Pure common cause** (sender and recipient both reacting to a latent event) raises G(−1) ≈ G(0) ≈ G(1) ≈ 0.025–0.03, flat, with D = −0.013 to +0.005.
- **Null:** |D| < 0.004.
- **The C9 guard passes:** D isolates read-out-gated responses, and a common cause shows up as a flat floor, not a jump.

## Amendments (2026-10-04, after the synthetic validation, before any real-data fit)
- **A1 · Zero-parameter prediction = headroom-weighted read-out CDF.** F_hr(τ) = mean over treated cells of 1(τ ≥ τ_r)·h(τ − τ_r). Here h(u) is the inactivity profile u minutes after a "wake" (the agent's next turn), from control-eligible no-kick cells with the same headroom key: state at m−1 × exact idle minutes in [m−15, m−1]. No response data enters F_hr. The plain step F_obs and the scheduled (F_sched) and renewal (F_ren) versions are reported, each headroom-weighted, and the step is also reported unweighted.
- **A2 · Φ verdict band.** C8-P1 is *consistent* where the 95% CI of Φ_meas − Φ_pred overlaps [−0.3, +0.1], and *inconsistent* where it lies outside. This is the synthetic calibration: under the context truth the H04-design measurement runs 0 to −0.2 below the prediction; immediate +0.2 to +0.6; delay or memory −0.5 to −1.2. The clause "Φ = 1 excluded" is dropped, because with headroom even immediate coupling gives Φ < 1; rival comparison moves to the CV.
- **A3 · CV model set and P3 rule.** Context family: ctx (A·F_hr), ctx_step, ctx_d. Rivals: imm, imm_hr (A·(1 − E0), E0 = the matched-control mean), delay, delay_hr, hawkes. gamma is the ceiling. P3 holds if the best context model beats the best model of every rival family in ≥ 60% of splits, and its median SSE is ≤ 1.1 × gamma's.
- **A4 · Kernel designs.**
  - **Primary:** H04's design, run per period (these are "the kernels H04 measured", per period instead of pooled).
  - **P5 (read-out stratification):** H04's strata × pause bin.
  - **Sensitivity:** exact-idleness (+ pause) matching.
- **A5 · Pooling (exception (d)).** The pooled regime-III kernel concatenates the per-period matched day sums (each period with its own controls) and is analysed like a period. H04's published pooled regime-III curve is compared with the pooled F_hr.
- **A6 · C9 diagnostic added:** pre = G(0) − G(−1), expected ≈ 0 (a common cause is flat).

### Amendment to the C1 predictions (2026-10-04, before C1 is run)
Two facts learned after the C1 predictions were written, both from structure, not from C1 outcomes:
1. **NE12 (2026-02-23 → 03-02) is in the locked holdout,** and so are #28, #29, #32 and #34 (with NE30). The Claude Code agent's non-holdout days are #30, #31 (regime I, one room), #33 (regime II, #general), #35, #36 and #37 (two rooms).
2. **H05 found that 2026-02-25 separated nobody:** everyone stayed in #general until #voted-out (03-05) and the #best/#rest split (03-16). From the room timeline, the Claude Code agent was in #rest from 03-16, briefly in #best on 03-23, and back in #general from 03-24, while the others were in #best or #rest.

So prediction 1 is scored as: before the split (#30, #31, #33) the agent sees events from the whole village; in #35–#37 it sees ≲ 5% of the events posted in rooms it was not in. "Recall" in prediction 4 is read as the share of truly seen events (excluding its own) that the room rule predicts; the fetch-limit clause is about **precision** (rule-predicted events the agent never fetched). Predictions 2–3 are unchanged.

## Prediction (C1)
*Written 2026-10-03, before running the analysis.*
1. **Coverage collapses at NE12.** Before 2026-02-25 the agent sees events from the whole village. After it, it sees ≲ 5% of events originating in other rooms; room filtering is real and near-total.
2. **Not all event types are visible.** Other agents' `AGENT_TALK`, session start/stop and `CONSOLIDATE` events are visible, but not WAITs or pauses. Coverage differs by type.
3. **Median delay is minutes, not seconds:** set by the agent's own turn cadence. The delay distribution is heavy-tailed: long gaps when the agent was busy or paused.
4. **The room-based rule reaches recall ≥ 0.9 after NE12.** Recall drops before NE12 if the agent didn't actually see everything, because of fetch limits.

**Falsifiers:** substantial cross-room visibility after NE12; uniform visibility across types; or recall < 0.7 for the room rule.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness". Round 1, exploratory, non-holdout.

**Rival models:**
- immediate coupling (R1);
- constant processing delay (R2);
- Hawkes exogenous kernel (R3);
- memory-mediated coupling (R4);
- common cause (simulated);
- flexible gamma kernel (ceiling).

**Locked holdout used for confirmation:** none yet. `analysis/confirm_holdout.py` (CF1–CF5) is written and dry-run on stand-ins only.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | event IDs match exactly between the fetched feed and `events`; turns, call starts and read-out defined from dataset fields | 1 | **Fetch timestamps agree with `events` to the second** (14,466 matched events); 85% of the agent's non-holdout fetched ids match the tenure-window table (the rest are 2025 events: the replay). Turns, pause-aware call starts and read-out come from `actions` + `events_core`. **The call-start rule works in regime III but not in regime I:** there, addressing peaks at turns classified as in flight (D_addr < 0 in 4/6), so regime-I chat calls are probably not all logged. **Round 1b:** with the ledger's call windows the regime-I in-flight peak disappears (addressing jumps at read-out in 4/6 regime-I periods): it was the call-start rule, not unlogged calls. Score stays 1 (talk and content responses still differ by regime). |
| B assumptions | call-start rule; pause timers; step response | 1 | Pause timers hold (wake calls start at the expiry). **The fast-step response fails for nudges:** the onset lags read-out by ≈ 3 min (#51). Activity responses need headroom weighting (synthetic). A6's "common cause is flat" fails: replies to the recipient's own talk raise o = −1, and o = 0 is refractory. |
| C adequacy | beats the rivals on held-out days | 1 | C9: the read-out discontinuity beats the pseudo-message null for addressing in 10/11 regime-II/III periods and for talk in 6/9 regime-III periods; the other-room placebo is null in 6/8. C8 (#51): the context model beats immediate (77–89% of splits) and Hawkes (80%), but not constant delay (41–46%). |
| D unfitted predictions | kernel shape predicted from turn timing alone | 1 | **The location of the response is predicted with no parameters:** the jump sits on the first turn whose call started after the message (C9-V4 17/17; post hoc, the clean-recipient floor at o = 0 ≈ 0 in 15/17). **The kernel's time course is not:** Φ(1,5) is 0.03 measured vs 0.52 predicted (#51); pooled 355 cells, −0.03 vs 0.52. P2 and P4 pass. |
| E interventional | NE41 forced erasures (exogenous timing) | 1 | Forced erasure lowers the chance of addressing a sender whose message was only in the erased context: 9/9 periods negative, CI excluding 0 in 6/9; pooled −2.5 pp, −18% ± 6% (predicted ≤ −30%). Voluntary erasures act alike. Not yet on the holdout. |
| F identifiability | synthetic recovery on real skeletons | 1 | C9 guard passes: injected read-out responses are recovered, and a common cause gives no jump. C8: at high signal the CV identifies all four truths in #38 (5–6/6); at H04-like signal only 4/6, and less under nudger-like selection. Φ tests are underpowered per period. #51 skeletons are uninformative under the context truth (read-outs > 60 min away). |
| G ground truth | the Claude Code agent's logged inputs | 1 | While its feed was current, the room rule's recall was 0.97–1.00 and other-room coverage 1.6% (#35, one day). But type coverage was uniform (WAITs too), delays were seconds, not minutes, and **from 2026-03-17 its feed replayed the village from April 2025** (65% of #35's, 100% of #36's fetched events), so the room rule fails completely there. One atypical agent. |
| H comparative | immediate, constant-delay, Hawkes, memory-mediated | 2 | Immediate and Hawkes are rejected for nudges. Memory-mediated coupling is rejected by NE41 (β_F < 0). A common cause cannot produce the discontinuity (synthetic). Round 1: constant delay **not** rejected. **Round 1b (2026-10-04): constant delay rejected** (the nudge onset follows the receiving call: t₂₅ 4, 4, 15 min for read-outs ≤ 1, 1–3, 3–10 min; read-out-aligned t₂₅ 1 min), and NE41 holds on reply labels (8/9). Score 1 → 2. |
| I transfer | across periods and regimes; holdout | 1 | The C9 addressing discontinuity holds in every regime-II/III period. In the clean-recipient subset it holds in 16/17, including regime I. The talk discontinuity is absent in regime I. NE41 is consistent in sign across 9 periods. No holdout run. |

## Results by goal period
One folder per goal period in [`goalperiod-subhypotheses/`](goalperiod-subhypotheses/), each with its dated prediction, verdict and results table; the cross-hypothesis table is [../OVERVIEW.md](../OVERVIEW.md).
- **Verdict rule (fixed in each card before running).**
  - *Supported* = C9's talk and addressing discontinuities both pass (CI excluding 0) and no other applicable test (C8 where ≥ 30 isolated nudge cells, C3 where ≥ 300 forced-erased units, C1 where the Claude Code agent fetched) fails.
  - *Failed* = the C9 test fails.
  - *Mixed* = C9 passes but another test fails.
- **Columns.** D values are in percentage points, with day-bootstrap 95% CIs.
  - "clean" = post-hoc subset of recipients who did not talk at o = −2 or −1.
  - C8 is the count of isolated nudge → target cells; Φ is measured vs predicted, where powered.
  - C3 is β_F (forced erasure).

| G | regime · mode | days | D_talk | D_addr | D_addr, clean (post hoc) | C8 nudge cells | C1 (Claude Code) | C3 β_F (pp) | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [G24](goalperiod-subhypotheses/G24/README.md) | I · C | 5 | -0.17 [-0.41, +0.16] | +0.18 [+0.04, +0.26] | +0.52 [+0.33, +0.71] | — | — | — | failed |
| [G25](goalperiod-subhypotheses/G25/README.md) | I · C | 5 | -0.10 [-0.74, +0.43] | -0.63 [-1.08, +0.04] | +0.56 [+0.16, +0.99] | — | — | — | failed |
| [G26](goalperiod-subhypotheses/G26/README.md) | I · C | 5 | -0.14 [-1.58, +1.78] | -1.22 [-1.86, -0.46] | +0.43 [-0.12, +0.84] | — | — | — | failed |
| [G27](goalperiod-subhypotheses/G27/README.md) | I · K | 10 | -0.71 [-1.41, -0.04] | -0.58 [-1.30, +0.06] | +0.43 [+0.24, +0.61] | — | — | — | failed |
| [G30](goalperiod-subhypotheses/G30/README.md) | I · C | 5 | -0.28 [-0.87, +0.58] | -0.31 [-0.52, -0.07] | +0.38 [+0.21, +0.55] | 1 cells | recall 0.99, replay 0% | — | failed |
| [G31](goalperiod-subhypotheses/G31/README.md) | I · F | 5 | -0.59 [-1.01, -0.07] | +0.13 [-0.35, +0.57] | +0.48 [+0.35, +0.59] | 8 cells | recall 0.97, replay 1% | — | failed |
| [G33](goalperiod-subhypotheses/G33/README.md) | II · C | 3 | +0.12 [-0.64, +0.60] | -0.01 [-0.17, +0.22] | +0.71 [+0.34, +1.05] | 8 cells | recall 1.00, replay 0% | — | failed |
| [G35](goalperiod-subhypotheses/G35/README.md) | II · C | 5 | -0.72 [-1.20, -0.21] | +0.61 [+0.43, +0.82] | +0.77 [+0.40, +1.07] | 4 cells | recall 0.31, replay 65% | — | failed |
| [G36](goalperiod-subhypotheses/G36/README.md) | II/III · C | 5 | +1.13 [-0.24, +2.84] | +1.47 [+0.94, +2.63] | +1.43 [+0.98, +2.35] | 2 cells | recall 0.00, replay 100% | -2.95 [-6.46, +0.03] | failed |
| [G37](goalperiod-subhypotheses/G37/README.md) | III · F | 3 | +3.27 [+1.95, +3.79] | +2.60 [+1.55, +3.10] | +2.29 [+1.40, +2.67] | 12 cells | no fetches | -10.86 [-13.65, -3.78] | supported |
| [G38](goalperiod-subhypotheses/G38/README.md) | III · C | 17 | +0.85 [+0.29, +1.46] | +0.88 [+0.62, +1.11] | +0.83 [+0.58, +1.06] | 26 cells | — | -0.98 [-2.39, +1.22] | supported |
| [G39](goalperiod-subhypotheses/G39/README.md) | III · I | 5 | +0.39 [-0.29, +0.97] | +0.43 [+0.33, +0.61] | +0.26 [+0.08, +0.57] | 2 cells | — | -2.22 [-9.76, -0.11] | failed |
| [G40](goalperiod-subhypotheses/G40/README.md) | III · C | 5 | +0.21 [-0.21, +0.62] | +0.62 [+0.52, +0.78] | +0.58 [+0.46, +0.72] | 5 cells | — | -1.04 [-2.09, -0.02] | failed |
| [G41](goalperiod-subhypotheses/G41/README.md) | III · I | 5 | +1.43 [+0.75, +2.13] | +1.02 [+0.64, +1.32] | +0.85 [+0.39, +1.30] | 14 cells | — | -1.27 [-4.60, +2.25] | supported |
| [G42](goalperiod-subhypotheses/G42/README.md) | III · I | 5 | +1.41 [+0.57, +2.03] | +1.57 [+1.02, +2.03] | +1.06 [+0.73, +1.32] | 9 cells | — | -4.45 [-8.12, -1.63] | supported |
| [G44](goalperiod-subhypotheses/G44/README.md) | III · C | 4 | +1.25 [+0.44, +1.90] | +1.26 [+0.43, +1.85] | +0.83 [+0.34, +1.15] | 9 cells | — | -4.92 [-7.12, -2.38] | supported |
| [G51](goalperiod-subhypotheses/G51/README.md) | III · P | 45 | +0.61 [+0.47, +0.74] | +0.68 [+0.60, +0.75] | +0.47 [+0.42, +0.54] | 303 cells, Φ 0.03 vs 0.52 | — | -1.74 [-2.00, -1.50] | supported |

**Verdicts: 6 supported (G37, G38, G41, G42, G44, G51), 11 failed, 0 mixed; [NE41](goalperiod-subhypotheses/NE41/README.md): mixed.**
- All 11 failures are of the pre-registered talk-discontinuity clause.
  - **Regime I/II (G24–G36):** the talk jump is absent, and in regime I addressing peaks at the in-flight turn.
  - **G39, G40:** addressing passes, but the talk CI includes 0.
- Every regime-II/III period passes the addressing clause.
- In the post-hoc clean-recipient subset, addressing jumps at read-out in 16/17 periods, regime I included.

## Results
*All numbers: `data/processed/H08-context-is-the-coupling/` (`summary.json`, `G<NN>/c9|c8|c2|c3|c10.json`, `c8_pooled.json`, `ne41_pooled.json`, `c10_hawkes.json`, `cc/c1.json`, `synthetic/`). Code map in Notes. Exploratory, non-holdout; nothing here is confirmation.*

### Outcome vs prediction
| # | Prediction | Observed | Outcome |
| --- | --- | --- | --- |
| C8-P1 | Φ(1,5) measured vs F_hr: difference CI overlaps [−0.3, +0.1] (A2) | **#51** (303 cells): 0.03 [−0.83, 0.57] vs 0.52 [0.48, 0.57]; difference −0.50 [−1.37, +0.01]. **Pooled regime III** (355 cells): −0.03 vs 0.52; difference [−1.31, −0.08]. H04's published regime-III kernel: 0.08 | **fails in substance:** the point estimates lie far outside the band and only the CI edge touches it. The response starts at minute 5–6, while the median read-out is 1.7 min |
| C8-P2 | t½ of F_hr ∈ [3, 15] min | #51 3 min; #38 4; #41 3 | supported (but the measured kernel is later still) |
| C8-P3 | context beats immediate, delay and Hawkes in ≥ 60% of splits; ≤ 1.1 × gamma | #51: beats imm 0.77 (imm_hr 0.89), Hawkes 0.80, but delay only 0.41 (delay_hr 0.46); gamma/ctx 0.97. Pooled: gamma best 64% | **not supported** (constant delay is as good) |
| C8-P4 | Φ_ren > Φ_obs for nudges | 0.57 > 0.52 (#51); 0.72 > 0.45 (#38); 0.69 > 0.60 (#41) | supported (small) |
| C8-P5 | pause-matched early response larger for non-paused than for ≥ 5 min paused targets | difference −0.02 [−0.09, +0.05] (n = 98 / 42); both ≈ 0 for 4–5 min | **not supported**: non-paused targets do not respond sooner |
| C8-P6 | human → mentioned: Φ_pred ≥ 0.5 and measured agrees | #51 only (15 cells): 0.94 vs 0.71 (CI wide) | consistent, underpowered |
| C9-V1 | D_talk > 0 (CI) in ≥ 70% of periods | 6/17 (6/9 regime III; 0/8 regime I/II) | **not supported** (regime III only) |
| C9-V2 | D_addr > 0 (CI) in ≥ 70%; floor 0 < G_addr(0) < ½ G_addr(1) | 11/17 (10/11 regime II/III, 1/6 regime I). Floor clause holds in regime III; in regime I G_addr(0) ≥ G_addr(1) | **not supported overall; supported in regimes II/III** |
| C9-V3 | other-room placebo \|D\| < ⅓ own-room D, CI includes 0 | 6/8 two-room periods | supported |
| C9-V4 | G_talk(2) < G_talk(1) | 17/17 | supported |
| C9-V5 | median read-out delay of active recipients 10–40 s (regime III) | 32–49 s; 4/9 inside | not supported (slightly slower) |
| A6 | pre = G(0) − G(−1) ≈ 0 | 8/17. In regime III G(−1) is elevated and the in-flight turn dips | not supported. *Post hoc:* recipients who did not talk at o = −2 or −1 have a floor of ≈ 0 at o = 0 (15/17) and the jump at o = 1 (16/17) |
| C1-1 | ≲ 5% of other-room events seen | #35 (the one current-feed two-room day): 1.6%; #36 0% (replay) | supported (thin) |
| C1-2 | visibility differs by type (WAIT and PAUSE invisible) | coverage 0.53–0.69 for every type, WAIT included | **refuted** |
| C1-3 | median delay minutes, heavy tail | 14–23 s in #30–#33 (90th 3–9 min), when the agent fetched ~100–185 times per active hour. 266 s on #35's current-feed day, at 8 fetches per hour | **refuted** where it fetched often: delay tracks its fetch cadence |
| C1-4 | room-rule recall ≥ 0.9 | 0.97–1.00 in #30, #31, #33 and on #35's current feed (0.96). 0.31 (#35) and 0.00 (#36) once the feed replayed 2025. Precision 0.57–0.64 (has_more on only 2–4% of fetches, so not fetch limits) | supported while the feed was current; **fails at the replay** |
| C2-I1 | b > 0 (CI) in ≥ 70%; R² < 0.05 | raw b < 0 in 9/9; R² 0.002–0.04. *Post hoc,* controlling the previous action: b = 0.22–0.60, CI > 0 in 7/9 | **not supported as stated.** Token inflow is dominated by the tool output of the previous action |
| C2-I2 | talk ratio > 1.2; ρ(uncached, latency) > 0 | ratio 1.17–2.80 (8/9 > 1.2); ρ CI > 0 in 7/9 | supported |
| C3-E1 | β_F < 0 (CI) in ≥ 2/3 of periods; pooled drop ≥ 30% | 6/9; pooled −2.5 pp [−3.7, −1.4], relative −18% ± 6% | **sign supported, size not** (NE41 *mixed*) |
| C3-E2 | β_V within ±50% of β_F | pooled −2.2 vs −2.5 pp | supported |
| C3-E3 | equation of state: ρ < 0 in ≥ 2/3 | 5/9 | not supported |
| C10-L1 | k rises with session hour (ρ > 0, slope CI > 0) in ≥ 2/3 | slope CI > 0 in 4/8 (+1.8 to +5% per hour); \|ρ\| < 0.07 | not supported (tiny where present) |
| C10-L2 | n̂ higher in the second half of the day (#51) | 0.50 → 0.70, Δ +0.20 [+0.10, +0.29]; #38 (4 h) −0.05 [−0.18, +0.09] | **supported in #51** |
| C10-L3 | ρ(n̂, mean k) > 0 across #51 weeks | +0.62 (9 weeks; not significant) | supported in sign |
| G1 | synthetic guard | C9 passes; C8 passes at high signal, fails at realistic signal (4/6) | partial |

Prior credences were C8-P1 0.6, C9-V1 0.6, C3-E1 0.45, C10-L2 0.3. Of these, only C10-L2 came out cleanly as stated.

### Findings
1. **Agent-to-agent coupling is gated by the read-out boundary (C9).** In regimes II and III, a recipient's chance of addressing the sender jumps exactly at the first turn whose model call started after the message: +0.5 to +2.9 pp over the pseudo-message baseline at that turn (a jump of D = +0.4 to +2.6 pp from the in-flight turn). It stays small at the in-flight turn (a call already running when the message arrived) and decays by the next turn. The physical delay to that turn is the recipient's turn cadence: median 32–49 s for active recipients, which covers H03's fast cross-triggering window.
   - **H18's failed placebo is explained.** H18 found senders addressed 3–10× above baseline in the "invisible" window. That elevation comes from recipients who had just talked (an ongoing exchange). Among recipients who had not talked at the previous two turns, the in-flight floor is ≈ 0 in 15/17 periods, and the jump at read-out remains in 16/17, regime I included.
   - **Regime I is different.** Addressing there peaks at turns my rule calls in flight, which is consistent with chat calls the logs do not record.
2. **The nudge kernel is not just the read-out delay (C8, HH92).** In #51, nudge targets read the nudge fast: median 104 s after it, 68% of them mid-pause, so the read-out CDF is half done by minute 3. Yet the activity response starts at minute 5–6. Rivals:
   - the zero-parameter read-out model beats an immediate response and a Hawkes kernel;
   - it does not beat a constant ≈ 5-min delay;
   - the pause-stratified test finds no earlier response for non-paused targets.

   So H04's 4-min dead time is about half scheduler read-out and half something slower after read-out. Candidates are an acknowledgement turn before work resumes, or idle loops that need several turns to break. HH92 as stated, "G(τ) predictable with no free parameters from turn timing", is **not supported** for nudges. It holds for *where* in the turn sequence agent-to-agent responses land (finding 1).
3. **Erasing the context cuts the coupling to what was only in it (NE41).** After a forced consolidation (timing set by the 41-turn cap), an agent addresses a sender whose message it read *before* the erasure 18% less often than an equally old sender read *after* it, in the same post-consolidation talk turns. This holds in 9/9 periods (6/9 with CIs excluding 0). Voluntary consolidations act the same. Whatever the agents write to memory keeps most of the thread, but not all: the coupling lives partly in the session context, partly in memory or the room's visible history. Memory-mediated coupling alone (β_F ≈ 0) is rejected.
4. **The room rule is right while the feed is current, and the feed can silently break (C1).** The Claude Code agent's logged fetches cover 97–100% of what a room rule predicts in the one-room periods. They contain only 1.6% of other-room events on the two-room day with a current feed. Delays are seconds, and every event type (WAITs included) is shown about equally.
   - **From 2026-03-17 its feed replayed the village from 2025-04-02, about one historical day per real day, until it left.** For its last two weeks the agent's "unread context" was a year-old history, and no room rule could reconstruct it.
   - That is a ground-truth demonstration that exposure can decouple from the room structure entirely.
5. **Token inflow is a poor proxy for message inflow (C2).** Uncached input falls with new messages, because chat-mode turns carry small tool outputs. With the previous action controlled, the elasticity is +0.2 to +0.6, but messages explain < 4% of its variance. New messages do drive behavior: P(talk) at the call that sees them is 1.2–2.8× higher.
6. **Longer sessions run hotter within #51's 8 h days (C10, HH91).** The Hawkes branching ratio is 0.70 in afternoon halves vs 0.50 in morning halves, and weekly n̂ tracks the mean backlog (ρ = +0.62, 9 weeks). This is the same direction as H04's holdout result. But the per-turn backlog barely grows within the day (+2–5% per hour in 4/8 periods), so the "more unread context per turn" mechanism does not explain it. The 4 h #38 shows no half-day effect.

### Post-hoc analyses (not pre-registered; labelled in every table)
- **C9 clean-recipient subset** (no talk at o = −2, −1), added after the o = −1 elevation and o = 0 dip were seen.
- **C2 previous-action control**, added after b < 0 everywhere.
- **C1:** zoned API timestamps parsed to identify the replay. This is a scheme correction, not an analysis choice.

### Caveats
- **Power (C8).** Only #51 has ≥ 30 isolated nudges. The synthetic run shows that at this signal the CV picks the true mechanism about 2/3 of the time, and the Φ test has CIs ~1 wide. The C8 conclusion rests on #51's point estimates and the pooled kernel.
- **H04's design** leaves a pre-kick imbalance under nudger-like selection (synthetic). The exact-idleness sensitivity for #51 gives Φ(1,5) = 0.28 [−0.15, 0.71] vs 0.52, so the lag is still there, but it is less extreme.
- **Mentions as responses.** Addressing is mention-based. The discontinuity design differences out common causes, but the response measure is still a name in a message.
- **Regime I visibility.** The call-start rule is doubtful there. Regime-I failures may reflect unlogged chat calls, not absent coupling.
- **Multiplicity.** 17 periods × ~20 predictions + 3 post-hoc analyses, with no adjustment. The headline C9 addressing result (10/11 regime-II/III periods, #51 at z ≈ 17) and NE41's pooled sign (z ≈ 4.4) would survive any correction; C10-L3 and the per-period C3 CIs would not.
- **One Claude Code agent**, with a different scaffold. Its replay may be specific to that scaffold.
- **C10-L2** may partly be nonstationarity absorbed by the Hawkes slow kernel (H04's caveat). Afternoon halves differ in more than session length.

### Figures (`figures/`)
- `summary_obs.pdf` (summary page 1): addressing excess by turn offset, for clean recipients. Thin lines are periods, bold lines regime medians.
- `summary_obs2.pdf` (page 2):
  - (a) the #51 nudge kernel vs the zero-parameter read-out prediction and the constant-delay fit;
  - (b) NE41 β_F per period, with the pooled estimate.
- `overview_two_panel.pdf`: both main results side by side, at full width.
- `c9_offsets.pdf`: all 17 periods, primary vs clean vs other-room.
- `c8_kernels.pdf`: #51 predictions; pooled kernel vs H04's published curve; pause-matched strata.
- `c1_cc.pdf`: the Claude Code agent's replay share by day; recall and precision by period.
- `ne41.pdf`: β_F and β_V per period, with the pooled estimate.
- `c2_c10.pdf`: C2 elasticities, raw and controlled; C10 backlog slopes.
- Per period: `goalperiod-subhypotheses/G<NN>/figures/c9_offsets.pdf`.
- Summary page: `summary/summary.pdf` (two pages; `summary/content.tex`, `summary/meta.json`).

## Round 1b (improved data, 2026-10-04)
*Re-evaluation on the corrected shared tables (Vivian's priority 2; RE wave). Predictions and verdict rules are the pre-registered ones, unchanged. Round-1 outputs stay in `data/processed/H08-context-is-the-coupling/G<NN>/`; round-1b outputs are in `.../r1b/`. Holdout untouched.*

### What changed
| Input | Round 1 | Round 1b |
| --- | --- | --- |
| Turns, call starts, read-out | H08's own rule: turn-merged `actions` + `events_core` records, call start = previous record (pause expiry after a pause) | DQ1 ledger: `call_windows` calls (`t_call` = context assembly; summary calls excluded), read-out call = the call that received the message in `context_ledger_items` (exact by construction). In-flight share of own-room pairs falls from 0.91 to 0.63 (G38) |
| Responses (C9, C3) | @-mention (`chat_mentions_clean`) | mention (pre-registered) **plus** the DQ2 reply-parent author (`reply_pairs`, `pair_set = cand`, `parent`) and the content cosine of the talk with the message (bge-small; non-mention, H08-R2) |
| Erasures (C3 / NE41) | H15's consolidation catalog (41–42-turn segment) | ledger `reset_forced` / `reset_consol` between the read-out call and the talk call (round 1's ambiguous units no longer arise) |
| Nudge kernel (C8) | H04's round-1 design (old `activity_bins`, all-mention targets, future-kick isolation) | H04's round-1b design (`activity_bins_fixed`, leading-@ target, past-only eligibility, day fixed effect, presence mask), aligned on the target's **receiving call** (ledger `age_s`) |
| Code (switch) | `scheme/build_turns.py`, `analysis/visibility.py`, `erasure.py` (unchanged, still runnable) | `scheme/build_turns_ledger.py`, `analysis/visibility_ledger.py`, `erasure_ledger.py`, `ne32_newcomers.py`, `r1b_summarize.py` |

### C9: read-out discontinuity, old vs new
D in percentage points with day-bootstrap 95% CIs; "clean" = recipients with no talk at o = −2, −1 (post hoc in round 1); content D in cosine ×100. Full per-period tables in each G folder.

| G | regime | D_talk: old → **new** | D_addr: old → **new** | D reply author (new) | D content (new) | verdict: old → **1b** |
| --- | --- | --- | --- | --- | --- | --- |
| G24 | I | −0.17 → +0.30 [−0.30, +0.97] | +0.18 → **+0.53 [+0.09, +1.20]** | +0.62 [+0.28, +1.01] | −0.49 [−1.92, +0.66] | failed → failed |
| G25 | I | −0.10 → +0.26 [−0.24, +1.04] | −0.63 → +0.52 [−0.02, +0.83] | +0.76 [+0.30, +1.06] | −0.85 [−1.44, +0.12] | failed → failed |
| G26 | I | −0.14 → −1.01 [−3.11, +0.76] | −1.22 → +0.20 [−0.17, +0.68] | +1.02 [+0.69, +1.63] | −0.65 [−1.47, +0.16] | failed → failed |
| G27 | I | −0.71 → −0.18 [−0.69, +0.42] | −0.58 → **+0.34 [+0.18, +0.48]** | +0.35 [+0.19, +0.51] | −0.70 [−1.69, +0.06] | failed → failed |
| G30 | I | −0.28 → −0.13 [−0.82, +0.52] | −0.31 → **+0.31 [+0.18, +0.43]** | +0.32 [+0.17, +0.44] | −0.79 [−1.53, −0.07] | failed → failed |
| G31 | I | −0.59 → +0.10 [−0.63, +0.79] | +0.13 → **+0.26 [+0.08, +0.46]** | +0.32 [+0.19, +0.40] | −1.00 [−1.99, −0.04] | failed → failed |
| G33 | II | +0.12 → −0.22 [−0.52, +0.06] | −0.01 → **+0.73 [+0.44, +1.21]** | +0.59 [+0.38, +0.84] | +0.15 [−0.03, +0.33] | failed → failed |
| G35 | II | −0.72 → +0.75 [−0.08, +1.25] | +0.61 → +0.48 [+0.17, +0.71] | +1.03 [+0.84, +1.19] | −0.33 [−0.90, +0.57] | failed → failed |
| G36 | II/III | +1.13 → **+1.10 [+0.16, +2.72]** | +1.47 → +1.60 [+0.87, +3.22] | +1.85 [+1.15, +2.84] | +2.47 [+0.56, +7.08] | failed → **supported** |
| G37 | III | +3.27 → +2.68 [+2.47, +3.09] | +2.60 → +2.50 [+0.83, +3.34] | +3.21 [+1.70, +3.90] | +1.74 [−2.84, +9.84] | supported → supported |
| G38 | III | +0.85 → +1.60 [+0.93, +2.22] | +0.88 → +1.14 [+0.80, +1.41] | +1.69 [+1.39, +1.95] | +2.00 [+0.14, +3.69] | supported → supported |
| G39 | III | +0.39 → +0.38 [−0.21, +1.18] | +0.43 → +0.26 [−0.22, +0.48] | +0.60 [+0.34, +0.83] | +3.15 [+1.41, +6.62] | failed → failed |
| G40 | III | +0.21 → +0.11 [−0.83, +1.06] | +0.62 → +0.71 [+0.44, +1.01] | +0.56 [+0.35, +0.72] | +0.82 [−0.46, +2.55] | failed → failed |
| G41 | III | +1.43 → +1.53 [+0.95, +2.15] | +1.02 → +1.41 [+1.11, +1.62] | +1.55 [+1.12, +1.96] | +0.37 [−0.56, +2.65] | supported → supported |
| G42 | III | +1.41 → +1.11 [+0.56, +1.50] | +1.57 → +1.87 [+1.20, +2.41] | +1.90 [+1.23, +2.59] | +3.42 [+0.48, +6.71] | supported → supported |
| G44 | III | +1.25 → +0.45 [−0.26, +1.06] | +1.26 → +1.22 [+0.22, +1.76] | +1.50 [+0.81, +2.07] | +1.35 [+1.09, +1.82] | supported → **failed** |
| G51 | III | +0.61 → +0.69 [+0.53, +0.89] | +0.68 → +0.81 [+0.71, +0.91] | +0.93 [+0.85, +1.03] | +1.99 [+1.68, +2.35] | supported → supported |

| Prediction | Round 1 | Round 1b | Outcome (1b) |
| --- | --- | --- | --- |
| C9-V1 talk jumps (≥ 70%) | 6/17 | 6/17 (G36 in, G44 out; 0/8 regime I/II) | not supported (unchanged) |
| C9-V2 addressing jumps (≥ 70%) | 11/17 (10/11 regime II/III, 1/6 regime I) | **14/17** (10/11 regime II/III, **4/6 regime I**); reply author **17/17**; clean subset 15/17 | **supported** (was: supported in II/III only) |
| C9-V2 floor: G(0) < ½ G(1) | fails in regime I (addressing peaked in flight) | regime-I in-flight peak gone | supported |
| C9-V3 other-room placebo | 6/8 | **8/8** (\|D\| ≤ 0.15 pp, CIs at 0) | supported |
| C9-V4 G(2) < G(1) | 17/17 | 17/17 | supported |
| C9-V5 median read-out delay of active recipients 10–40 s | 32–49 s; 4/9 regime III inside | first record of the read-out call 29–41 s in regime III (8/9 inside); context assembly 10–17 s | supported (was not) |
| Non-mention response (H08-R2, new) | — | content jump D_cos > 0 (CI) in 6/9 regime-III periods; negative in regime I (G30, G31) | new: gating holds on content in regime III |

**Reading.** The round-1 regime-I failure ("addressing peaks at turns classed in flight; chat calls may be unlogged") was the call-start rule: regime-I chat-mode calls are scheduled, not chained, and the ledger places them correctly. The known issue "Regime-I calls that produce chat may be unlogged" can be retired. The talk clause still fails in every regime-I/II period: in chat mode a call that sees a message is not more likely to talk than a pseudo-message baseline, although when it talks it addresses the sender. The content jump is negative in regime I, where in-flight talk sits closer in time to the message (H29's recency confound runs against the hypothesis there).

### C8: the nudge kernel aligned on the receiving call (from H04 round 1b, #51)
| Statistic | Round 1 | Round 1b |
| --- | --- | --- |
| median read-out delay of nudges (to the target's call) | 104 s (H08 rule) | 108 s to context assembly, 118 s to the call's first record (ledger; H43: 122 s) |
| response in the first 5 min after the kick (A5) | ≈ 0 ("nothing for 4–5 min") | **0.23 [0.12, 0.33]**; the isolated subset H04 used still shows ≈ 0, all nudges do not |
| kernel aligned on the receiving call | — | t₂₅ = **1 min** [1, 3]; A5 after read-out 0.52 [0.40, 0.65]; peak at 2 min |
| onset by read-out delay (≤ 1, 1–3, 3–10 min) | — | t₂₅ = 4, 4, 15 min: the onset follows the read-out (a constant delay predicts equal onsets) |
| Φ(1,5) measured vs predicted (A2 band) | 0.03 vs 0.52 (fails, too late) | 1.76 [0.90, 4.69] vs 0.52 (F_hr) / 0.71 (plain step): fails the band in the **other** direction (a transient at read-out that decays, not a step to a plateau) |

- **C8-P1** fails in substance again, but for a different reason: the onset is the read-out (as HH92 says), the shape is a transient (glance-then-return; H43: escapes start at the receiving call in 78–96% of cases, sustained work rarely follows). **C8-P3** was not re-run; the read-out-bin onsets reject the constant-delay rival directly. **Round 1's finding 2 ("about half of H04's dead time is something slower after read-out") is withdrawn:** it came from the dropped events in `activity_bins` and from H04's future-kick isolation, which keeps late responders.

### C3 / NE41 and the natives
| Test | Round 1 | Round 1b | Verdict (1b) |
| --- | --- | --- | --- |
| NE41 forced erasure, pooled β_F | mention −2.5 pp [−3.7, −1.4], −18% ± 6% (6/9 CI) | mention −2.5 ± 1.4 pp, −16% ± 8%; **reply author −1.97 ± 0.64 pp, −21% ± 7% (8/9 CI)**; β_V reply −1.70 ± 0.59 | mixed (unchanged; sign yes, size < 30%) |
| NE32 newcomers (native, new) | — | 0 talk calls in isolation (N32a untestable); first naming of an old-timer after first receipt in **35/35** pairs (71/84 pairs received j only after the newcomer had started naming others); naming rate 0.22 at calls that just received j vs 0.014 | **supported** |
| NE03 fetch limit (native, new) | — | rank > 10 pairs 621 (#10a) vs 80 (#10b): underpowered | descriptive |
| C1, C2, C10 | as round 1 | not re-run: C1 uses the Claude Code fetch logs (unaffected); C2 uses token accounting; C10's k from H18 barely changes under the ledger (k = k_since_talk at 98% of talks) | unchanged |

### Scorecard changes (round 1b)
- **A 1** (unchanged): the ledger removes the regime-I mapping failure for addressing, but the talk clause and the content response still differ by regime.
- **H 1 → 2:** every named rival is now beaten: immediate and Hawkes (round 1), memory-mediated (NE41, on replies), common cause (synthetic), and constant delay (onset follows read-out delay; round 1 could not reject it).
- **D 1** (unchanged): the location and onset of responses are predicted from turn timing with no free parameter; the transient shape is not.
- **E 1** (unchanged): NE41 sign replicated on replies and NE32 passes, but no predicted size was met.
- Others unchanged. Faithfulness 2.5 → 3.0 suggested (meta.json).

### Cross-hypothesis notes
- **H18:** the "invisible message" placebo is explained by visibility (see H18 round 1b), and the ledger also removes H08's regime-I in-flight peak.
- **H04 / H43:** the response to a nudge starts at the receiving call; H04's dead time is read-out delay plus paused targets that respond late or not at all.
- **H35:** none of the 991 non-holdout nudge read-outs in regime III (#36–#44, #51) is an early wake (`wake_early` = 0), before or after NE44; pre-NE44 read-outs are shorter because fewer targets were mid-pause (38% vs 73% of receiving calls after a pause).

## Round 2 (2026-10-05): content response, memory dose, exposure audit
*Pre-registration written 2026-10-05 02:45 UTC, before any round-2 statistic on real data. Scope: the card's H08-R2, R4 and R5 (R1 and R3 were superseded by round 1b). Reserved data are never read: every builder drops reserved days with `holdout_mask` and `calendar.holdout` before any computation. Round-1 and round-1b code and outputs are unchanged; round-2 code is new files (`analysis/r2_*.py`, `scheme/build_memory_names.py`), outputs in `data/processed/H08-context-is-the-coupling/r2/`.*

**What had been looked at before writing this:** table schemas (`context_ledger_items`, `call_windows`, `memory_stats`, `chat_index`, both chat embedding matrices, `statements`, `statement_flags`, `cc_fetches`, `cc_seen`); the timing of one G38 agent-day's consolidation calls, memory snapshots and reset calls (no outcome); the ledger documentation of the 200-event cap. Known from round 1b: the call-offset content jump D_cos (pseudo-message null) is positive in 6/9 regime-III periods and negative in regime I; the Claude Code feed replays 2025 from 2026-03-17; H44 finds memory dose does not shorten the output dip (ρ ≈ 0).

### R2 · Non-mention content response at matched lag
**Question.** Does the recipient's *content* move toward a sender's message only once a call has read it, with names and reply labels removed?

**Units.** (agent message m by sender j, recipient i) pairs from `context_ledger_items` (agent senders only; i ≠ j), and every talk statement s of i posted at lag ℓ = t_s − t_m ∈ (0, 300] s. The producing call of s is the ledger call with t_first ≤ t_s ≤ t_log. s is **read** if its producing call is the receiving call of m or later; s is **in flight** if its producing call started before m (t_call ≤ t_m < t_s). Same 17 replication periods as round 1b.

**Response (message-specific null).** x(s, m) = cos(s, m) − b(m, i). The null b(m, i) is the mean cosine of the *same message* with the recipient's statements on the same PT day at |t − t_m| ∈ [20, 60] min. It removes the message's baseline overlap with this recipient's talk and the day's shared topic. Secondary null: the recipient's statements on other non-reserved days of the period.

**Estimator (partition contrast, read vs in flight at matched lag).** Lag bins (0, 15], (15, 30], (30, 60], (60, 120], (120, 300] s. Δ = Σ_b w_b (x̄_read,b − x̄_flight,b) / Σ_b w_b, with w_b = n_r n_f / (n_r + n_f). Convergence share κ_c = Σ_b w_b x̄_flight,b / Σ_b w_b x̄_read,b. Day-cluster bootstrap, B = 200. Both embedding models (bge-small, gte-modernbert).
- **Non-name subset (primary):** drop statements that mention j or whose DQ2 reply parent was written by j.
- **Robustness:** all statements; copies removed (`statement_flags.self_repeat_both`); the other-day null; a paired version (only (m, i) pairs with statements on both sides).
- **Other-room placebo (two-room periods):** messages from a room the recipient is not in; "read" means the producing call started after m (it would have been read had it been visible).

**Rivals.** Contemporaneous convergence (both agents follow one earlier event: equal x on both sides at equal lag); the day's shared topic (removed by b); the recipient's style prior (same recipient on both sides); recency (removed by lag matching).

| # | Prediction | Counts against |
| --- | --- | --- |
| R2-P1 | **Content is read-gated without names (primary):** Δ_nonname > 0 with CI excluding 0 in both models in ≥ 6/9 regime-III periods | CI includes 0 in ≥ 5/9 in either model |
| R2-P2 | **Regime I/II:** with recency removed by lag matching, Δ_nonname > 0 in sign in both models in ≥ 5/8 periods; no period has Δ < 0 with CI excluding 0 in both models | Δ < 0 (CI excluding 0) in ≥ 2/8 |
| R2-P3 | **Convergence share:** median κ_c over regime-III periods (bge, non-name) in [0.2, 0.6]: in-flight statements already carry part of the near-time alignment (Known issues: a third to a half) | median κ_c < 0.2 or > 0.6 |
| R2-P4 | **Other-room placebo:** \|Δ_other\| < ⅓ Δ_own, CI including 0, in ≥ 6/8 two-room periods (bge) | Δ_other comparable to Δ_own |
| R2-P5 | **Paired version** agrees in sign with Δ_nonname in ≥ 7/9 regime-III periods | sign disagreement in ≥ 3/9 |

**Kill rule.** If R2-P1 fails with CIs including 0 in ≥ 5/9 regime-III periods in either model, the content arm of the gating claim is withdrawn; the claim then stands on names and reply labels only. If the synthetic ungated world gives Δ with CI excluding 0 in > 20% of replicates, R2 is reported as descriptive only.

**Synthetic guard (run first).** Real call skeletons, statement times and ledger receipts of G38 and G41; synthetic 64-d embeddings. A day field T_d(t) drifts as an Ornstein–Uhlenbeck process (τ = 60 min) shared by all agents (contemporaneous convergence by construction). m = norm(T(t_m) + a_j + ε); s = norm(T(t_s) + a_i + ε + α Σ m̂) over the messages of the last 5 min. Truths: *gated* (sum over messages the producing call has read, α = 0.3), *ungated* (all messages posted before t_s), *mixed* (gated 0.3 + ungated 0.15; expected κ_c ≈ 0.3–0.5), *null* (α = 0). 20 replicates each. Pass: gated Δ CI > 0 in ≥ 80%; ungated and null Δ CI covers 0 in ≥ 80% (false positives ≤ 20%); mixed κ_c recovered within ±0.2.

**R2 synthetic guard (run 2026-10-05, before any real-data run; `r2/r2_synthetic.json`).** 20 replicates per truth; entries are the share of replicates with the Δ CI above 0 (below 0 in brackets).

| Skeleton · truth | pre-registered (lag strata, day bootstrap) | lag strata, hour-block bootstrap | **lag × density strata, hour-block bootstrap** | median Δ · κ_c (last column) |
| --- | --- | --- | --- | --- |
| G38 · gated | 1.00 | 1.00 | **1.00** | +0.096 · 0.72 |
| G38 · ungated | 0.05 | 0.00 | **0.10** | +0.007 · 0.98 |
| G38 · mixed | 1.00 | 1.00 | **1.00** | +0.065 · 0.83 |
| G38 · null | 0.15 | 0.10 | **0.10** | +0.002 · 0.99 |
| G41 · gated | 1.00 | 1.00 | **1.00** | +0.092 · 0.76 |
| G41 · ungated | **0.30** | 0.15 | **0.05 (0.05)** | +0.007 · 0.98 |
| G41 · mixed | 1.00 | 1.00 | **0.90** | +0.036 · 0.90 |
| G41 · null | 0.10 (0.10) | 0.00 (0.05) | **0.00 (0.10)** | −0.000 · 1.00 |

- **The pre-registered estimator fails the guard in G41** (5 days): the ungated world gives a false positive in 30% of replicates (> 20%), and the null in 20%. Five day clusters make the percentile bootstrap too narrow; a leave-one-day-out jackknife-t was tried and loses the gated signal (power 0.20).
- **κ_c is not a pure convergence share.** In a world with only gated responses, the shared drifting topic alone gives κ_c ≈ 0.73. The prediction band [0.2, 0.6] was set without that term.

**Amendments (2026-10-05, after the guard, before any real-data statistic):**
- **R2-A1 · Resampling unit:** 1-hour blocks of message time within a PT day (G41: about 20 blocks), percentile bootstrap, B = 200. The day bootstrap stays as a reported comparison (`prereg_nonname`).
- **R2-A2 · Matching strata:** lag bin × density bin, where density is the number of own-room messages the recipient received in the 300 s before the statement (0–1, 2–3, 4–7, 8+). Busy stretches put more read statements in dense windows; that leaked convergence into Δ under the ungated truth (G41 median +0.015 → +0.007).
- **R2-A3 · κ_c:** R2-P3 is scored as written, but κ_c is read against the synthetic references: ≈ 0.73 (gated only, with the shared drift), ≈ 0.85–0.90 (mixed), ≈ 0.98 (ungated).
- With A1 and A2 the guard passes in both skeletons (gated 1.00 / 1.00; ungated and null false positives ≤ 0.10 one-sided, ≤ 0.10 two-sided). The kill rule's estimator clause is not triggered under the amended estimator.

### R4 · NE41 memory dose
**Question.** When an agent writes a sender's name into memory at a forced erasure, is the coupling to that sender protected after the wipe?

**Units.** Round 1b's NE41 units (`analysis/erasure_ledger.py`, unchanged): (talk call k of i, agent sender j) with j's latest message read in the 30 min before k; erased = a `reset_forced` (CF) or `reset_consol` (CV) call between the read-out call and k. Regime III: G36 (from 03-24), G37–G42, G44, G51.

**Dose.** From the memory text (`agent_memories`, read locally; only name bitmasks are written). For a consolidation: S_before = the latest snapshot before the consolidation call's t_call; S_after = the latest snapshot at or before the next call's t_call (the memory in that prompt). **Added names** = agents named (the `common.mention_regexes` rule) in lines added by the snapshots in (S_before, S_after] and still named in S_after. The dose z of a unit is "j is an added name" at the **adjacent consolidation**: for erased units, the consolidation between the read-out and k; for non-erased units, the next consolidation after k (a placebo dose: same salience signal, but it cannot have acted on k). Secondary: z_stock = j named anywhere in the prompt's memory at k.

**Estimator.** Round 1b's linear probability model with agent×day effects (age bins, engaged, PC, new), plus z, CF×z and CV×z. Response: reply author (y_auth; primary, because a name in memory could prime a mention without any coupling); mention (secondary). Protection ratio π = β_{CF×z} / (−β_CF). Day-bootstrap B = 200; DerSimonian–Laird pooling over periods (exception (c): the erasure is the object).

| # | Prediction | Counts against |
| --- | --- | --- |
| R4-P1 | **Memory protects the thread:** pooled β_{CF×z} > 0 (CI excluding 0) on y_auth, with π ≥ 0.5 | pooled β_{CF×z} ≤ 0, or CI includes 0 at power ≥ 0.8 for π = 0.5 |
| R4-P2 | **Salience:** in non-erased units the placebo dose predicts replies (β_z > 0, CI excluding 0, pooled): agents write down the senders they are engaged with | β_z ≤ 0 |
| R4-P3 | **Dose rate (descriptive):** share of CF units with z = 1, per period | — |

**Kill rule.** If the pooled CF×z CI includes 0 and the synthetic power at π = 0.5 is ≥ 0.8, "memory carries the thread" is rejected for names. If the power is < 0.8 the verdict is inconclusive.

**Synthetic guard (run first).** Real unit skeletons (units, z, CF/CV flags, agent-days) of G38, G41 and G51. y ~ Bernoulli(p₀ · (1 + 0.5 z) · (1 − 0.21 · CF · (1 − π z))), with p₀ the unit's real mean response rate by age bin. Truths π ∈ {0, 0.5, 1}; 50 replicates each. Pass: π = 0 gives the CF×z CI excluding 0 (positive) in ≤ 10%; π = 1 recovered (CI excludes 0) in ≥ 80%. The power at π = 0.5 sets the R4 verdict rule.

**R4 synthetic guard (run 2026-10-05, before any real-data fit; `r2/r4_synthetic.json`, `r4_synthetic_all9.json`).** 50 replicates per truth on the real units (G38 13,989 units with a dose, G41, G51).
- **As pre-registered, the estimator is biased.** CF×z came out at −0.03 to −0.07 under every truth, π = 1 included. Cause: the dose's salience effect is multiplicative on an age-dependent base rate, erased units are old (base ≈ 0.04 vs 0.16), and an additive z term cannot absorb it.
- **Amendment R4-A1 (before real data):** add z × age-bin terms. With them, π = 0 gives a positive CF×z CI in 0–12% of replicates per period and 0% pooled (pass).
- **Power is far too low.** A full protection (π = 1) is detected pooled over all nine periods in 22% of replicates; π = 0.5 in 4%. The forced cut is about 0.2 × an old-unit base rate of a few percent, and the dose splits it further.
- A relative-scale protection ratio was tried and rejected: it gives false positives in 30% of replicates at π = 0 (ratios of small numbers).
- **Consequence, fixed now:** by the kill rule, R4's verdict cannot be "rejected" (power < 0.8). It can only be "supported" (pooled CF×z CI > 0) or "inconclusive". The real fit is reported with its power.

### R5 · Exposure audit
**Question.** Where input logs exist, how often and for how long were agents silently decoupled by a stale or replayed feed? Can a log-free monitor find the same thing?

**R5-a, fetch-log audit (the Claude Code agent, non-reserved days).** Per fetch: the creation times of the returned events (`cc_seen`, event ids joined to `events`). A returned event is *stale* if it was created > 24 h before the fetch; a fetch is stale if ≥ 50% of its returned events are stale. Freshness lag L = fetch time − newest returned event. A **decoupled episode** is a maximal run of ≥ 3 consecutive stale fetches. Also: the goal text in each fetch result (if present) vs the village goal at that time.

**R5-b, log-free monitor (all agents).** M(agent-day) = mean over the agent's statements of [cos(s, c₃₀(s)) − cos(s, c₃₀ˢʰⁱᶠᵗ(s))]. Here c₃₀ is the normalized centroid of other speakers' messages in the agent's room (room rule) in the 30 min before s, and c₃₀ˢʰⁱᶠᵗ is the same clock window on another non-reserved day of the period. An agent-day is *flagged* if it has ≥ 10 statements and the bootstrap 95% lower bound of M is ≤ 0. The expected flag rate under full coupling comes from resampling each agent-day at its agent-period median M (power floor). Both models.

**R5-c, scaffold truncation (descriptive).** The share of received agent messages that the ledger marks `omitted` (beyond the 200-event cap, from 2026-06-11), per period.

| # | Prediction | Counts against |
| --- | --- | --- |
| R5-P1 | **One episode:** exactly one decoupled episode on non-reserved days, from 2026-03-17 to the agent's exit; ≥ 90% of its fetches in that span stale; no episode before 03-17 | a second episode, or < 90% stale in the span |
| R5-P2 | **Goal stays current:** the goal in fetch results matches the village goal in ≥ 95% of fetches, during the replay too (the replay is in the event feed only) | < 95% |
| R5-P3 | **A log monitor detects it fast:** "median age of returned events over the last 5 fetches > 1 h" fires within 1 active hour of the episode onset, with no alarm on current-feed days | delay > 1 h or a false alarm |
| R5-P4 | **The log-free monitor sees the replay:** the Claude Code agent's M on replay days < ½ of its M on current-feed days, in both models | ratio ≥ ½ in either model |
| R5-P5 | **No hidden episodes in standard agents:** in every regime-III period the flagged share exceeds the power floor by ≤ 2 pp, and no agent has a run of ≥ 3 consecutive flagged days | excess > 2 pp, or such a run |
| R5-P6 | **Truncation is rare:** omitted share < 1% in every period before 2026-06-11 and ≤ 5% in G51 | larger shares |

**Synthetic guard for R5-b (run first).** Real statement times and rooms of G38 and G51; synthetic embeddings with a drifting day field per room. Coupled agents' statements add α · c₃₀; for a planted "replayed" agent the term uses a window from another day instead. Pass: the planted agent's days are flagged in ≥ 80% of replicates; coupled agent-days flagged at the power floor ± 2 pp.

**Prior credences (Claude, 2026-10-05):** R2-P1 0.6, P2 0.4, P3 0.4, P4 0.7, P5 0.7; R4-P1 0.3, P2 0.7; R5-P1 0.7, P2 0.5, P3 0.6, P4 0.5, P5 0.6, P6 0.7.

## Confirmatory predictions (written 2026-10-04 after round 1, before any holdout use; `analysis/confirm_holdout.py`, not run)
Run only after this card and the script are committed and Vivian signs off. The script refuses without `--confirm --i-understand-this-uses-the-locked-holdout`; `--dry-run` runs the same code on non-holdout stand-ins (`data/processed/H08-context-is-the-coupling/confirm_dryrun/dryrun.json`).

| # | Prediction |
| --- | --- |
| CF1 | C9, primary design, regime-III held-out units #43, #45–#50 and the #51 tail (8 units): D_addr > 0 (CI) in ≥ 7/8; D_talk > 0 (CI) in ≥ 5/8; reply/refractory signature G_addr(0) − G_addr(−1) < 0 in ≥ 6/8 |
| CF2 | C9, clean recipients, all 10 held-out units (incl. regime-I #28, #29): D_addr > 0 (CI) in ≥ 8/10; floor \|G_addr(0)\| < ⅓ G_addr(1) in ≥ 8/10 |
| CF3 | C8, #51 tail only: A30 > 0 (CI); Φ(1,5) measured − predicted < −0.2; context beats the immediate and Hawkes families in ≥ 60% of splits but the constant-delay family in < 60% |
| CF4 | C3 / NE41, regime-III held-out units, random-effects pooled: β_F < 0 (CI); relative drop in [−0.35, −0.08]; β_V < 0 |
| CF5 | C1, the Claude Code agent's held-out days (#28, #29, #32, #34): recall ≥ 0.9 and replay share < 5% each; other-room coverage ≤ 5% during #34 (incl. the #voted-out stints); median current-feed delay < 60 s |

**Holdout reuse** (policy in `../holdout.md`):
- **#45:** used by H02 (activity couplings) and by H04 as segment A1 (kernels, Hawkes).
- **#46–#50:** used by H04 (Hawkes n, nudge-kernel A30, mean-field).
- **So C8 is not tested on #45–#50.**
- C9's turn-offset discontinuity, C3's erasure-coupling and C1's fetch logs have never been computed on any held-out period; they are a different statistic or modality.
- NE12 (H05) and NE30 enter only through CF5's fetch logs.
- Disclose in both cards and in `LOG.md` when run.

## Round 2 redirects (2026-10-04, proposed by the H08 agent after round 1)
- **Where round 1 went sideways:** the activity kernel assumed a fast step response at read-out. Nudge responses lag read-out by about 3 min, and binary activity has a ceiling (headroom), so a zero-parameter shape needs a post-read-out stage.
- **What the direction is really after:** Coupling is what enters each model call, and when: responses are gated at call boundaries, and the response kernel is the read-out delay followed by a measurable post-read-out lag.
- **H08-R1.** (Superseded by round 1b, 2026-10-04: on corrected data the nudge response starts at the receiving call, so there is no post-read-out lag to decompose.) Two-stage kernel: read-out delay convolved with a post-read-out lag counted in turns (talk and action turns aligned on the read-out turn), to decompose the nudge's 5-min onset and retest HH92 / H04-R1.
- **H08-R2.** A non-mention response for the C9 discontinuity (content similarity to the sender's message against a message-specific null), so the gating result does not rest on names.
- **H08-R3.** (Superseded by round 1b, 2026-10-04: the context ledger's scheduled chat-mode calls remove the regime-I in-flight peak.) Regime-I call logging: identify which calls produce chat turns and redo the read-out rule, since addressing peaks at turns currently classed as in flight.
- **H08-R4.** NE41 dose: whether writing a sender or thread to memory at the erasure protects the coupling (needs memory text: stored-line overlap with sender names).
- **H08-R5.** Exposure audit: detect stale or replayed feeds (like the Claude Code agent's from 2026-03-17) wherever input logs exist, as a monitor for silent decoupling.

## Next steps
1. **What happens between read-out and the activity response to a nudge?** Talk-level or action-level responses aligned on the read-out turn would show whether the first post-read-out turns are acknowledgements, and how many turns the response takes. This could close HH92 with a two-stage kernel: read-out, then a k-turn lag.
2. **A non-mention response for C9:** content similarity of the recipient's next message to the sender's (a stricter, message-specific null), or an action citing the message's artifact.
3. **Regime I:** find which calls produce chat turns (session text turns vs computer-use calls), and redo the read-out rule there.
4. **NE41 dose:** relate β_F to what the agent wrote to memory at the erasure (H15's stored dose, which needs text). Does saving the sender's name protect the thread?
5. **C10:** test the half-day effect against a time-of-day baseline (morning vs afternoon on 4 h days, which sit at different clock hours), and with a per-half flexible baseline.
6. Report the Claude Code replay (2026-03-17 → 04-02) to the dataset notes, so others don't treat that agent's late inputs as current.
7. Run `confirm_holdout.py` after sign-off.

## Notes
- **From H44 (2026-10-04):** coupling to items read before a forced erasure drops to 0.60 [0.44, 0.81] of baseline; susceptibility to new room content does not rise (RR 0.97).
- 2026-10-03: opened on a misread; parked. `llm_calls` confirmed unavailable on Hugging Face. C1 is ready to run on the Claude Code agent whenever wanted. Its predictions above were written before any data was touched.
- 2026-10-04: reactivated. Round-1 operational definitions, observables, nulls and predictions (C8–C10, C2, C3, C1 amendment) written before any H08 analysis of real data.
- 2026-10-04: synthetic validation, then amendments A1–A6, before real data. Period cards written with dated predictions, then round 1 run (non-holdout only). Post-hoc analyses are labelled (C9 clean subset, C2 previous-action control).
- **Code map:**
  - `scheme/`:
    - `h08lib.py`: turns, pause-aware call starts, read-out, token accounting;
    - `build_turns.py`: `G<NN>/turns.parquet` and `readout.parquet`;
    - `build_cc_exposure.py`: Claude Code fetches, seen events, village events.
  - `analysis/`:
    - `c8lib.py` + `kernels.py`: C8, importing H04's `h04lib`;
    - `synthetic.py`: axis F;
    - `visibility.py`: C9;
    - `cc_exposure.py`: C1;
    - `inflow.py`: C2;
    - `erasure.py`: C3 / NE41, using H15's catalog;
    - `sessions.py`: C10, using H18's `talks.parquet` and H04's `hawkes.py`;
    - `figures.py`, `summarize.py`, `write_period_cards.py` + `fill_period_results.py`;
    - `confirm_holdout.py`.
  - No file of H04, H15 or H18 was modified.
