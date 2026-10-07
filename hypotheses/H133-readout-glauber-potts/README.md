# H133: Read-out Glauber Potts: an agent switches project only at a call, driven by the named messages it just read

**Status:** pre-registered (not run). Card, observables, nulls, predictions and kill rules written 2026-10-07 from HH376 (approved by Vivian 2026-10-07), before any H133 statistic on real data. No scheme, synthetic or analysis code exists yet.
**Question (GOALS.md):** **Q1** (what couples agents: does project choice couple through named reads at the read-out call, as talk does?). Second: **Q2** (field vs coupling: is a project switch a response to a named read, or to a project-wide attention field that also produces the messages?).
**Fields:** stat mech (kinetic Potts, Glauber single-spin updates), sociophysics (discrete choice with social input), dynamics (discrete-time hazards on the call clock)
**Literature:** none in `literature/` covers kinetic Potts choice at a read-out. Cited from memory (†): Glauber, *J. Math. Phys.* 4, 294 (1963)† (single-spin-flip kinetics); McFadden (1974)† (conditional logit); Blume, *Games Econ. Behav.* 5, 387 (1993)† (logit dynamics).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime; Driving / external field; **Exposure (ledger receiving call)** and **Receiving call**; **Interaction (addressed)** implemented as H67's naming rule (`chat_mentions_clean.mentions_roster` contains the reader, the ledger `ment` flag); **In-flight placebo (matched-lag)** (H67); **Call clock; exposure-time elasticity η** (H40); **Agent state (categorical, project/artifact strict)** (H11) as the project map; **Host (work ledger, call-clock expiry)** (H77, H78) for the expiry rule. New named variants proposed for DEFINITIONS.md (not edited there; defined under Data scheme and Observables): **agent state (categorical, project per call)**, **project hop (call)**, **named read about b, N^nam_b(c)**, **unnamed read about b, N^un_b(c)**, **named in-flight read about b**, **background switch (call)**, **switch-span elasticity η_sw**.
**From:** HH376 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/10-potts/` (primary: kinetic Potts with Glauber updates at each agent's own calls), `physics-models/02-nonequilibrium-ising/` (asynchronous call-clock updates; read-out timing)

## Source HH (verbatim from the HH list)
- **HH376 · Read-out Glauber Potts: an agent switches project only at a call, and the switch is driven by the named messages it just read.** A kinetic Potts model on the call clock: at each call the agent stays, or moves to project b with a rate that rises with the number of messages naming b in that call's reads.
  - *Prediction:* the switch probability per call rises with named reads for b; unnamed reads about b add nothing. Without named reads, switches follow a flat background rate per call, not per hour.
  - *Check:* H11/H53 project ledger; DQ1 context ledger for which messages each call read; name detection from H67.
  - *Kill:* unnamed reads move the switch rate as much as named ones, or the rate scales with wall-clock time.
  - *Impostors:* a project that is hot gets both named messages and switches (common field). Compare the same project within one hour, across calls with and without a named read.
  - *Models:* 10, 02 · *Builds on:* H08, H67, H11, H53, H40

**Reading of "named" (fixed now).** In H67 and H42, a "named" message is one that names the reader (`mentions_roster` contains the reader). Here a **named read about b** is a message that the agent reads at its call, that names the agent, and that links project b. An **unnamed read about b** links b and does not name the agent. This keeps one meaning of "named" across H67, H90 and H133.

## What this card builds on (latest round of each cited card)
- **H08 (round 2, 2026-10-05):** naming and replying to a sender jump at the call that received the message (mention 14/17, reply author 17/17 periods; other-room placebo null 8/8). Content moves toward a read message only inside addressed replies (G51 matched-lag contrast +1.25 [+0.98, +1.60] cos×100 with them, −0.39 [−0.62, −0.12] without).
- **H67 (round 2, 2026-10-05):** in regime III a read message that names the recipient adds 0.079 [0.069, 0.089] talk calls per read; an unnamed one adds 0.004 [0.003, 0.006] (×19). On the chat clock, regime I has no read-out gain (−0.022 [−0.052, 0.009]).
- **H42 (round 2):** half the named talk effect comes with no exchange in progress (cold 0.046 vs thread-named 0.091 per read).
- **H40 (round 2, 2026-10-05):** in regimes II–III the reply hazard runs on the call clock (G51 η −0.00 ± 0.05; timer wakes −0.03 [−0.14, +0.08]; η given a talk call −0.11 [−0.16, −0.06]). Regime I runs on neither clock (η +0.51 [+0.41, +0.61]).
- **H11 (round 2, 2026-10-05):** joins follow a sublinear, time-symmetric co-arrival kernel (α 0.68 [0.38, 0.98] work, 0.52 [0.36, 0.67] attention; lag − lead ≈ 0). Read chat predicts joins better than artifact activity. The read vs unread contrast was not estimable in most units.
- **H53 (round 1):** adoptions jump about 20-fold at a project's first chat link (F1 22.5), stay in the poster's room (other-room ratio 0.12) and almost never happen without the link in context (1.5%). Read timing within one call cycle adds nothing (RR_timely 1.06 [0.93, 1.22]; 726 adoptions, 23 periods). The project's current share predicts herding (AUC 0.72). Post hoc: agents who talked in the previous 30 min adopt 3.1× [2.2, 4.4] more.
- **H28 (round 1b):** recipients switch to X at 6.5× baseline in the ~17 s before they can read a link to X, more than after reading (3.5×); future links beat past ones (pooled −1.04 ± 0.24). Links mark attention bursts. This is the strongest rival to H133.

## Question
At each model call, does an agent's chance of switching to project b rise with the read messages that name it and link b, while reads that link b without naming it add nothing? And without such reads, is the switch rate constant per call, whatever wall time the call spans?

**Practical payoff:** if project choice couples only through named reads, an operator moves an agent by naming it in a message that links the target. A broadcast link moves no one beyond the field it already carries.

## Model
**From:** `physics-models/10-potts/` (kinetic Potts) and `physics-models/02-nonequilibrium-ising/` (asynchronous updates).

**H133 variant: a read-out Glauber Potts walker.** Agent i holds one project σ_i(c) at each of its own calls c. At call c the agent updates once (Glauber, heat-bath form):
P(σ_i(c) = b | σ_i(c−1) = a, reads R_c) = exp(u_b) / [exp(u_stay) + Σ_{b′≠a} exp(u_b′)],
with
- u_stay = α_i + ln(1 + d) · φ (habit at dwell d, a nuisance term);
- u_b = κ_{b,h} + γ_nam · ln(1 + N^nam_b(c)) + γ_un · ln(1 + N^un_b(c)) + γ_if · ln(1 + N^if_b(c)) + ρ · [i held b before] + β_s · s_b(c),
- κ_{b,h} a project × active-hour fixed effect (the HH's impostor control: the same project within one hour);
- N^nam_b, N^un_b the named and unnamed reads about b at call c; N^if_b the named in-flight placebo (below);
- s_b(c) the share of present agents on b (H53's share rival, H93's βJ term).

**H133 says:** γ_nam > 0; γ_un = 0; γ_if = 0. Background switches (calls with no read about any project) occur at a rate per call that does not depend on the call's wall-time span.

**Rivals.**
- **R-field (H28; strongest rival):** a project-hour attention burst raises both messages about b and switches to b. Switches then rise with reads of both kinds and with in-flight messages that cannot be read (γ_if > 0). Project × hour effects absorb a burst only if it lasts the hour.
- **R-broadcast (H53):** any link in context moves the agent (γ_un ≈ γ_nam > 0).
- **R-share (H53, H93):** the switch follows the project's current share (β_s > 0), with no read effect.
- **R-wall clock:** background switches accumulate with wall time (η_sw = 1).

## Data scheme (`scheme/`)
A new shared builder, `infra/shared/project_calls.py` (to be written in round 1, with `--verify`; H134 uses the same table), writes `data/processed/shared/project_calls.parquet`. H133's own `scheme/build.py` writes `data/processed/H133-readout-glauber-potts/`.
- **Inputs:** DQ1 `call_windows` (turn_id, agent, t_call, t_first, t_end, kind, talk, ctx_mode), `context_ledger_items` (turn_id, message_id, sender, kind, ment), `context_ledger_turns` (room, reset flags); `artifact_mentions` and `artifacts` (strict rule and project map as in `project_states`); `infra/shared/copying.py: project_messages` (agent chat messages with the projects they link, strict rule); `chat_core`, `chat_mentions_clean` (naming of in-flight messages); `calendar`, `period_units`, `roster`, `rooms_timeline`. Read-only cross-checks: H129 `hops_*.parquet`, H53 `seeds.parquet`. No message text.
- **Agent state (categorical, project per call) (proposed variant):** σ_i(c) = the project of the strict artifact mentions (`speaker_kind` agent, `how ∈ {url, output, bare}`, sources action, chat, intention) with t in the call's window [t_first(c), t_end(c)]. Several projects: the modal one, ties to the latest mention. A call with no strict mention carries the previous label. The label expires after E = 100 of the agent's own calls without a mention (the Host expiry rule; variants E = 50, 300).
- **Project hop (call) (proposed variant):** a call whose label differs from the carried label of the agent's previous labelled call. The hop call is the first call that touches the new project. Expiry is not a hop.
- **Reads at call c:** ledger items received at c (`context_ledger_items.turn_id = c`, not omitted), agent senders only, linked to projects through `project_messages`. Variant with reads at c − 1 added (a switch one call after the read).
- **Named in-flight read about b (proposed variant; the placebo):** agent messages that name i and link b, posted in the call's latency window (t_call(c), t_call(c) + d_c], d_c = t_first(c) − t_call(c) clipped to [1, 120] s (H67's matched-lag rule). Call c cannot read them.
- **Risk set:** every labelled call of a present agent (Claude Code agent excluded) in a non-reserved unit, with the agent's current project known. Options at c: stay, or any project active in the unit that hour (≥ 1 strict mention by anyone in the last 4 active hours).
- **Call span:** span_c = t_call(c) − t_call(c − 1) of the same agent-day; first calls of the day dropped.
- **Output:** `calls.parquet` (unit, agent, call id, t, span, current project hash, hop flag, destination hash), `reads.parquet` (call id, project hash, N^nam, N^un, N^if), `results/`, `synthetic/`, `_provenance.json`. Project names hashed. Expected < 80 MB.
- **Regimes covered:** I, II and III. Reserved rows are dropped with the shared reserved-row mask in `infra/shared/common.py`; the ledger's own reserved flag is asserted.

**Structural precondition (counted before any outcome, then frozen in a dated note):** a unit is testable if it has ≥ 30 project hops (call) and ≥ 20 named reads about some project other than the reader's current one. Only counts are printed.

## Observables
- **O1 · Named read effect γ_nam (primary):** the conditional-logit coefficient on ln(1 + N^nam_b(c)) with project × active-hour effects, agent effects, habit, share and dwell. Agent-block bootstrap CIs (200 draws).
- **O2 · Address contrast Δγ = γ_nam − γ_un** with its bootstrap CI.
- **O3 · Placebo contrast γ_nam − γ_if:** the named read effect minus the named in-flight effect.
- **O4 · Background switch-span elasticity η_sw:** on calls with no read about any project other than the current one, cloglog P(hop at c) = α_i + η_sw · ln(span_c) + hour-of-day bins + kind of the previous call. Per call: η_sw = 0. Per hour: η_sw = 1.
- **O5 · Read-to-hop lag profile (descriptive):** among hops to b with ≥ 1 named read about b in the previous 5 calls, the share whose most recent named read came at the hop call itself, one call before, and so on.

## Null / baseline
- **N1 · Within-project-hour permutation:** inside each project × active-hour cell, permute the read counts N^nam_b and N^un_b across the risk-set calls (keeps the cell's reads and switches; breaks their call-level alignment). 1,000 draws; one-sided p for γ_nam.
- **N2 · In-flight placebo (STANDARDS §1, contemporaneous convergence):** γ_if as the reference for γ_nam (O3).
- **N3 · Synthetic worlds on the real skeletons (below):** sizes and powers for O1–O4.
- **Strongest rival:** R-field (H28's attention burst). It predicts γ_if ≈ γ_nam and γ_un ≈ γ_nam.

## Impostors (STANDARDS §1)
| Impostor | Relevant? | How it is handled | Status |
| --- | --- | --- | --- |
| Scheduler field | yes | The unit is the agent's own call, not a time bin. O4 tests the wall clock directly. Hour-of-day bins and agent effects enter every model. | planned (removed if O4 holds) |
| Exogenous field (kickoff, goal, operator) | yes | Project × active-hour effects absorb a project-wide field that lasts the hour. Kickoff-named projects are flagged (H54's rule via `infra/shared/kickoff_naming.py`) and a variant drops the first 4 active hours after each kickoff. Human messages are not in the named counts (agent senders only). | planned (partly) |
| Shared model priors | partly | Agent effects remove stable agent preferences. A cross-family split of γ_nam (same-lab vs cross-lab sender) is reported. | planned (partly) |
| Contemporaneous convergence | yes | The named in-flight placebo (O3) at matched lag: posted, naming the agent, linking b, not yet read. H28 found pre-read switching at 6.5×, so this placebo is primary. | planned |

## Design: two layers (STANDARDS §4)
**Unit of analysis:** one goal period, split at `period_units`; #51 units 51a–51l separately. A pooled γ across units is a random-effects mean reported next to the per-unit values (exception (d), small units). No complete pooling.
- **Replication (role `replication`):** every non-reserved unit that meets the structural precondition. Expected candidates, from H53's and H129's counts: regime I G04, G12, G13, G17–G21, G23–G27, G30, G31; regime II G33, G35, G36a; regime III G36b–c, G37, G38, G39, G40, G41, G42, G44, 51a–51l.
- **Natives (role `native`):**
  - **N1 · G38 (17 days, two rooms, births throughout).** The most hops of any shared week (H129). Enough calls per project-hour cell for the HH's "same project within one hour" contrast with cells that have both read and unread calls.
  - **N2 · G51 timer wakes.** Calls at pause expiry have a declared wait (H40: timer-wake η −0.03 [−0.14, +0.08] for replies). The background switch elasticity on timer-wake calls is the cleanest wall-clock test.
  - **N3 · G40 (NE42 merge; negative control).** The kickoff-named hub took 73% of work (H94) and 8 agents adopted it within 2 h at receptive count 0 (H53). Prediction: hub hops in the first 2 active hours carry no named read effect (a field, not a coupling).
  - **N4 · G31 (regime I, herding week).** H40 found no call clock for replies in regime I. Prediction: η_sw > 0 here, as the regime contrast to N2.
- **Reserved (confirmation only; never read in exploration):** goal periods #1, #9, #14, #15, #22, #28, #29, #32, #34, #43, #45–#50, the #51 tail (2026-09-07 → 09-21) and the NE12, NE21+NE23 and NE30 windows. A frozen `analysis/confirm.py` for #45–#47 and the #51 tail is written after round 1 and runs only with Vivian's sign-off. Family: `project_potts` (reuse disclosure with H93, H129, H77/H78, H104).

## Synthetic validation plan (axis F; run before any real-data statistic)
`analysis/synthetic.py` on the real call, read and project skeletons of G38, G31, 51c and 51h (real calls, real read sets with naming flags and project links, real project activity). Outcomes are simulated call by call. 200 runs per world.
- **W0 null:** constant per-call hop probability; destination ∝ current share.
- **W1 H133:** γ_nam = 1.0, γ_un = 0, γ_if = 0; background per call.
- **W2 broadcast:** γ_nam = γ_un = 1.0.
- **W3 attention burst (H28):** a latent project-hour burst (log-normal, 30-min half-life) raises message rates about b and hop rates to b, with no read effect. Hops start before reads.
- **W4 wall clock:** background hop probability ∝ span_c.
- **W5 share:** βJ = 2 on s_b (H93's shared-week range +1.9 to +5.8), no read effect.
- **Read:** size of O1 (γ_nam > 0) in W0, W3, W5; size of O2 in W2; size of O3 in W3; power of O1 and O2 at γ_nam = 1.0 and 0.5; bias and power of η_sw (W1 vs W4).
- **Pass rule:** a statistic is used as a test where its size is ≤ 0.10 and its power is ≥ 0.8 at the planted value on that skeleton. Otherwise it is descriptive, by a dated amendment written before any real-data statistic. If W3 makes O1 reject in > 10% of runs, O3 becomes the primary coupling test.

## Prediction
*Written 2026-10-07, before any H133 statistic on real data. What I had seen: the cards of H08, H40, H42, H53, H67, H11 and H28 at their latest rounds (numbers above); the schemas of `call_windows`, `context_ledger_items`, `artifact_mentions` and `project_states`. No per-call project label, hop count or read count had been computed.*

| ID | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| P1 (HH) | **Named reads drive switches.** γ_nam > 0 with bootstrap CI > 0 and N1 p < 0.05 in ≥ 1/2 of testable regime-II/III units; random-effects mean CI > 0 | CI includes 0 in > 1/2 at power ≥ 0.8 | 0.55 |
| P2 (HH) | **Unnamed reads add nothing.** γ_un CI includes 0, and Δγ > 0 with CI > 0, in ≥ 1/2 of testable regime-II/III units | γ_un CI > 0 with Δγ CI including 0 | 0.3 |
| P3 | **Reading, not the burst.** γ_nam − γ_if > 0 with CI > 0 (random-effects mean, regime II/III) | γ_if ≥ γ_nam (H28's pre-read switching) | 0.4 |
| P4 (HH) | **Per-call background.** η_sw CI includes 0 and excludes 1 in regime II/III (random-effects mean and N2) | η_sw CI includes 1 and excludes 0 | 0.6 |
| P5 | **Regime I differs.** η_sw > 0 with CI > 0 in the regime-I mean (N4 included), and γ_nam smaller than in regime III | η_sw CI includes 0 in regime I | 0.45 |
| P6 | Most read-driven hops come at the read call or the next one (O5: ≥ 0.6 of hops with a recent named read) | ≤ 0.3 | 0.4 |
| N1 | G38: P1–P3 hold in the within-project-hour contrast | γ_nam CI includes 0 at power ≥ 0.8 | 0.4 |
| N2 | G51 timer wakes: η_sw CI includes 0, excludes 1 | CI includes 1 | 0.6 |
| N3 | G40 hub hops in the first 2 active hours: γ_nam CI includes 0 (field, not coupling) | γ_nam CI > 0 | 0.5 |
| N4 | G31: η_sw > 0 | η_sw CI includes 0 at power ≥ 0.8 | 0.45 |

**Kill rules (from the HH, sharpened).**
- **Kill A (address):** in the regime-II/III random-effects mean, Δγ = γ_nam − γ_un has a CI that includes 0 with |γ_un| ≥ ½ γ_nam, at synthetic power ≥ 0.8 for Δγ = 0.5. Then "unnamed reads move the switch rate as much as named ones" holds, and H133 fails.
- **Kill B (clock):** the regime-II/III mean η_sw has a CI that includes 1 and excludes 0. Then background switches scale with wall time, and H133 fails.
- **Kill C (burst):** γ_if ≥ γ_nam with the O3 CI including 0 or below 0. Then the named effect is an attention burst (H28), and H133's coupling reading is withdrawn.

**Verdict rule.** *Supported:* P1, P2, P3 and P4 hold. *Narrowed:* P1 and P3 hold but P2 fails (reads couple, address does not matter), or P4 fails. *Failed:* any kill fires. *Inconclusive:* the precondition leaves < 3 testable regime-II/III units, or P1 is unpowered.

**My credence before data:** supported 0.15; narrowed 0.3; failed 0.35; inconclusive 0.2. The strongest reason for doubt: H53's first-link step (F1 22.5) comes from broadcast links, and H28's pre-read switching (6.5×) says links and switches share a burst.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R-field (H28 attention burst), R-broadcast (H53 link in context), R-share (H53, H93), R-wall clock.
**Reserved periods used for confirmation:** none yet. Planned: #45–#47 and the #51 tail (frozen after round 1; not run).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 0 | not run |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 0 | not run |
| C adequacy | beats the null hierarchy, day-blocked out-of-sample data | 0 | not run |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | not run |
| E interventional | predicts the change across a natural experiment | 0 | not run |
| F identifiability | synthetic recovery with village sampling; survives preprocessing variants | 0 | not run |
| G ground truth | agrees with known structure | 0 | not run |
| H comparative | beats the named rivals | 0 | not run |
| I transfer | holds in other same-mode periods, including the reserved periods | 0 | not run |

## Results by goal period
No period has been run. Period folders (`goalperiod-subhypotheses/G<NN>/`) are created with their dated predictions before each period is run. `goalperiod-subhypotheses/GNN/` is the unfilled template.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| replication units (precondition list) | replication | pending | not run |
| G38 | native N1 | pending | not run |
| G51 | native N2 | pending | not run |
| G40 | native N3 | pending | not run |
| G31 | native N4 | pending | not run |

## Results
Not run.

## Notes
- 2026-10-07: card written from HH376 (approved by Vivian 2026-10-07). Round-1 order: structural counts (no outcomes) → per-period READMEs with dated predictions → synthetic on the real skeletons → dated amendments → replication and natives → estimates rows (`h133_gamma_named`, `h133_gamma_unnamed`, `h133_gamma_inflight`, `h133_eta_switch`) → frozen `confirm.py` (dry run only).
- Shared code: the per-call project label is needed by H133 and H134, so it goes in `infra/shared/project_calls.py` (STANDARDS §8), not in either card's folder.
- Compute: ≤ 2 threads, one heavy job at a time (STANDARDS §9).
