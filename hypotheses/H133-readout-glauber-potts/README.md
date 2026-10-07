# H133: Read-out Glauber Potts: an agent switches project only at a call, driven by the named messages it just read

**Status:** exploratory round 1 **done (2026-10-07, non-reserved data): inconclusive by the card's rule.** Named-read coupling (P1–P3) is untestable at the planted effect (A1: power ≈ 0 per unit). Background switches run on the call clock in regime II/III (P4 holds: η_sw −0.02 [−0.07, +0.02]). P5, N2 and N4 fail: η_sw is −0.34 in regime I and +0.46 at G51 timer wakes. Post hoc and descriptive: hops onto a project in a named read are 2.8× expected; unnamed 0.93×; in-flight 1.1×. Card, predictions and kill rules were written 2026-10-07 from HH376 (approved by Vivian), before any H133 statistic on real data. Synthetic run and Amendments A1–A3 were committed before real data (c471f13).
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

## Round 1 (2026-10-07)

### Shared builder and scheme
- **Per-call labels:** `infra/shared/project_calls.py` (commit 18e52ee, `--verify`) writes `data/processed/shared/project_calls.parquet` and `project_call_touches.parquet`. It implements the card's *agent state (categorical, project per call)* and *project hop (call)* variants. Verify on non-reserved rows: all invariants hold; an independent recompute on G38 and G51 has 0 mismatches. 98.6% of strict mentions map to a call. The W30 `project_states` mode is among the window's call touches in 98.2% of windows.
- **Call hops are fine-grained:** 61,939 non-reserved hops, 7–14× H129's W30 attention hops per period. 25.7% return to the previous project at the next hop within 5 calls (A → B → A).
- **Scheme:** `scheme/build.py` writes `data/processed/H133-readout-glauber-potts/<unit>/` (calls, reads, touches, labels; project names hashed; 42 MB). Non-reserved units only; the reserved flag is asserted false.

### Structural precondition (frozen 2026-10-07, counts only, before any outcome)
A unit is testable with ≥ 30 project hops (call) and ≥ 20 named reads about a project other than the reader's current one (`structural_counts.json`).
- **Regime I (17):** 4c, 12a, 13, 17, 18b, 19a, 20d, 21a, 21b, 24, 25, 26, 30b, 31a–31d.
- **Regime II/III (24):** 33, 36a, 36b, 36c, 37, 38a, 39, 40, 41, 42a, 44a, 44b, 51a–51l.
- **Below the precondition:** 38b–38e, 35, 42b and most early regime-I units. G38's native N1 therefore rests on 38a only.

### Synthetic validation (axis F; run before any real-data statistic)
`analysis/synthetic.py` on the real skeletons of 38a, 31a, 51c and 51h (real risk calls, option sets, reads with naming flags, project activity, dwell). The hop rate is calibrated to each skeleton's hop count. Output: `data/processed/H133-readout-glauber-potts/synthetic/`.
- **Design facts.** An option set holds 5–141 active projects per call (38a: 44; 51c: 67). Named reads about a non-current project are rare: 97–451 option rows per unit out of 0.5–5 million.
- **Part A: O1–O3 cannot be estimated.** Expected chosen rows with a named read under W1 (γ_nam = 1.0): 0.27 (38a), 0.30 (31a), 0.50 (51c), 1.19 (51h). A read term needs ≥ 5 chosen rows (Known issue H11 r2). P(≥ 5) is 9e-6 to 7.5e-3 per unit at γ_nam = 1.0, and ≤ 0.5 even at γ_nam = 3.
- **Stacks (complete pooling; not allowed as a test, reported for scale).** A count test of chosen named rows has power 0.61 (12 #51 units) and 0.64 (24 regime-II/III units) at γ_nam = 1.0. It has power 0.25 at 0.5. It reaches 0.997–0.999 only at γ_nam = 2.0. Regime I: 0.17 at 1.0.
- **Part B: fitted runs (50 per world; 38a, 31a).** γ_nam entered in 0/600 runs and γ_if in 0/600, so O1, O2 and O3 were never estimable. γ_un entered in 0–78% of runs. Its false-positive rate was 0.00–0.06 in W0, W1, W3 and W5; its power in W2 (γ_un = 1) was 0.02 (38a) and 0.14 (31a). The share term detects W5 (β_J = 2) in 0.64 / 0.72 of runs.
- **Part C: background switch-span elasticity η_sw (200 runs per world, 4 skeletons).**

| World (truth) | Card model: median η (sd); P(CI excludes 0); P(CI excludes 1) | With ln(1 + n options): median η; P(excl. 0) |
| --- | --- | --- |
| W0 null (η = 0) | −0.009 to −0.001 (0.02–0.06); 0.03–0.09; 1.00 | same; 0.035–0.09 |
| W1 H133 (η = 0) | −0.019 to −0.001; 0.035–**0.13** (51c); 1.00 | −0.001 to 0.004; 0.055–0.105 |
| W3 burst (η = 0) | −0.023 to +0.015; 0.06–0.08; **51h: +0.131, 0.975**; 1.00 | same pattern; 51h 0.975 |
| W4 wall clock (η = 1) | 1.000–1.004 (0.02–0.05); 1.00; 0.04–0.065 | same |
| W5 share (η = 0) | −0.018 to −0.002; 0.05–0.10; 1.00 | 0.065–0.075 |

  - Timer-wake background calls (51c 992, 51h 574 calls): bias ≤ 0.05 in W0, W1, W5 and +0.07 in W4. Power to exclude 1 is 0.955–1.00 at η = 0. Size is 0.05–0.075. In 51h W3 the bias is +0.22 and the size 0.185.
  - Reading: the "excludes 1" half of P4 and Kill B are valid tests everywhere (power 1.00, W4 coverage 0.935–0.965). The "includes 0" half has size ≤ 0.10 except under an attention burst on 51h (η ≈ +0.13). A small positive η therefore cannot separate a wall clock from a burst field.

### Amendments (dated 2026-10-07, written after the synthetic run and before any real-data statistic)
- **A1 (O1, O2, O3 untestable; the card's untestability rule fires).** At the planted γ_nam = 1.0 and 0.5, O1 has power ≈ 0 per unit (Part A, B). P1, P2, P3, native N1 (G38) and native N3 (G40) are **untestable**. The coupling verdict is "inconclusive" by the card's rule. Real-data logit coefficients are reported only as descriptive, where a term enters. N1 (within-project-hour permutation) is reported as a descriptive p. A pooled observed/expected count of chosen rows with a named, unnamed or in-flight read, at the fit without read terms, is added **post hoc** (descriptive; the stacks above give its scale). Kill A and Kill C cannot fire, because their inputs are not estimable.
- **A2 (O4 model).** The card's O4 has size 0.13 on 51c in the H133 world W1, because the hop rate varies with the size of the option set. P4, P5, N2 and N4 use the O4 model plus ln(1 + n options) as primary (W1 size 0.055–0.105, bias ≤ 0.004). The card's model is reported next to it. Under an attention burst both versions give η ≈ +0.13 (51h), so η > 0 alone does not mean a wall clock.
- **A3 (implementation notes, not changes):** N1's p uses the score for γ_nam at the fit without the nam and un terms. The permuted columns then do not enter the fitted probabilities, so no refit per draw is needed. A read term enters a fit only with ≥ 5 chosen rows having that read (Known issue H11 r2). CIs are agent-cluster sandwich (t, G − 1 df); the agent-block bootstrap (200) is run wherever γ_nam enters.

- **A4 (implementation changes during the real-data run; no outcome-driven change).** Two slow steps were replaced after the first units had run. (1) N1's statistic is now T = Σ over chosen rows of ln(1 + N_nam), permuted within cells with an exact random-subset draw; the score form of A3 is dropped. On 31a and 36b the p values were unchanged (0.002, 0.001). (2) The agent-block bootstrap now uses frequency weights with a warm start; on 18b its γ_nam percentile CI was unchanged ([−1.07, +2.76]). All units were then rerun with the final code. A β ridge of 1e-8 was added so that an all-zero feature cannot make the Hessian singular.

### Results on exploration data (run 2026-10-07; 41 units, 57,743 hops in option sets, 2,931 birth hops dropped)
Per-unit tables are in the period folders. Data: `data/processed/H133-readout-glauber-potts/results/` (`units.json`, `summary.json`). Random-effects means are DerSimonian–Laird over units.

| ID | Prediction | Result (95% CI) | Verdict by the rule |
| --- | --- | --- | --- |
| P1 | γ_nam > 0 (CI > 0, N1 p < 0.05) in ≥ ½ of regime-II/III units; RE mean CI > 0 | Untestable (A1). Descriptive: γ_nam enters in 13/24 units; CI > 0 with N1 p < 0.05 in 9/24 (36b, 44a, 51a, 51d–51g, 51i, 51l). The RE mean over the 13 is +2.30 [+1.64, +2.96], biased up because a unit enters only with ≥ 5 named hops. | untestable (inconclusive) |
| P2 | γ_un CI ∋ 0 and Δγ CI > 0 in ≥ ½ | Untestable (A1). Descriptive: RE γ_un +0.09 [−0.16, +0.34] (20 units). Δγ CI > 0 in 9/13 units where both enter. | untestable |
| P3 | γ_nam − γ_if > 0 (RE mean) | Untestable (A1). γ_if enters in 3 units: O3 +0.88 [−0.06, +1.82] (41), +1.68 [−0.01, +3.38] (51a), +3.78 [+1.74, +5.81] (51g). | untestable |
| P4 | η_sw CI ∋ 0 and ∌ 1 (regime II/III RE mean, and N2) | RE η_sw −0.02 [−0.07, +0.02] (24 units; card model −0.03 [−0.07, +0.02]). The CI excludes 1 in 24/24 units and includes 0 in 18/24 (negative in 33, 36b, 37; positive in 41, 51c, 51d). | **holds** (RE mean) |
| P5 | Regime I: η_sw > 0 (CI > 0); γ_nam smaller than regime III | RE η_sw −0.34 [−0.51, −0.17] (17 units): negative, CI < 0 in 5 units and > 0 in none. γ_nam enters in 3/17 regime-I units. | **failed** (opposite sign) |
| P6 | ≥ 0.6 of hops with a recent named read have it at lag 0 or 1 | 0.55 (863 hops, regime II/III). Lags 0–5: 0.33, 0.21, 0.15, 0.11, 0.09, 0.10. | not met (0.3 < 0.55 < 0.6) |
| N1 | G38: P1–P3 hold within project-hours | 38a only; γ_nam has 3 named hops (< 5). | untestable |
| N2 | G51 timer wakes: η_sw CI ∋ 0, ∌ 1 | RE +0.46 [+0.09, +0.84] (11 units, A2 model); card model +0.31 [−0.00, +0.63]. | **failed** on the primary model (excludes 0) |
| N3 | G40 hub hops in the first 2 h: γ_nam CI ∋ 0 | 76 hub hops; 1 had a named read about the hub; γ_nam not estimable. | untestable (descriptive: a field) |
| N4 | G31: η_sw > 0 | RE −0.22 [−0.34, −0.09] (31a–31d). | **failed** |
| Kill A | RE Δγ CI ∋ 0 with \|γ_un\| ≥ ½ γ_nam | Inputs not estimable (A1). Descriptively it would not fire: γ_un ≈ 0.09, γ_nam ≈ 2.3. | cannot fire |
| Kill B | RE η_sw CI ∋ 1 and ∌ 0 | −0.02 [−0.07, +0.02] | **does not fire** |
| Kill C | γ_if ≥ γ_nam with O3 CI ≤ 0 | O3 > 0 in the 3 estimable units | cannot fire (descriptive: not fired) |

**Post hoc (descriptive; not a test).** Chosen option rows with a read about the destination, against the expectation of the fit without read terms (project × hour, agent, habit, held-before, share), summed over units. Poisson 95% intervals:

| Read about the destination | Regime II/III: observed / expected = ratio | Regime I |
| --- | --- | --- |
| named (names the reader; read at the call) | 289 / 103.7 = **2.79** [2.48, 3.13]; unit permutation p < 0.05 in 16/24 | 35 / 16.8 = 2.08 [1.45, 2.90] |
| unnamed (read at the call) | 766 / 827.0 = **0.93** [0.86, 0.99]; 7/24 | 125 / 100.9 = 1.24 [1.03, 1.48] |
| named in-flight (posted, not yet readable) | 55 / 50.2 = **1.10** [0.83, 1.43]; 5/24 | 13 / 10.9 = 1.19 [0.64, 2.04] |

Agents hop onto a project about 2.8 times as often as expected when they have just read a message that names them and links it. A link they read without being named gives no lift. A named link still in flight gives 1.1. This is the card's pattern (named > unnamed ≈ in-flight ≈ 1). It is descriptive only: A1 made the pre-registered tests untestable, and this ratio was chosen after the synthetic run.

**Other fitted terms (regime II/III, descriptive).** Habit φ (stay utility per ln(1 + dwell)): median +0.54, CI > 0 in 22/24 units, so stickiness grows with dwell (as H129's hazard aging). Held-before: median +4.8, CI > 0 in 23/24. Share: median +23 per unit share, CI > 0 in 24/24 (R-share is a strong extra term, not a rival that excludes reads).

**Verdict (card rule): inconclusive.** P1 is unpowered at the planted effect (A1), so the coupling part cannot be supported or failed. The clock part splits by regime: P4 holds in regime II/III; P5, N2 and N4 fail. Background switches are not on a wall clock anywhere (Kill B does not fire). In regime I and at G51 timer wakes, η_sw departs from 0 in opposite directions.

**Impostors (round 1).**

| Impostor | Relevant? | How it was handled | Status |
| --- | --- | --- | --- |
| Scheduler field | yes | The unit is the agent's own call. O4 tests the clock directly (η_sw −0.02 [−0.07, +0.02] in regime II/III). Agent effects and 4-h bins enter O4; agent stay effects and project × active-hour cells enter the logit. | removed (II/III); open (regime I, η < 0) |
| Exogenous field (kickoff, goal, operator) | yes | Project × active-hour effects absorb a project field that lasts the hour. G40 hub: 1 of 76 early hub hops had a named read (field-like). The kickoff-drop variant was not run. | partly |
| Shared model priors | partly | Agent stay effects only. The same-lab vs cross-lab split of γ_nam was built (`reads.parquet`) but not fitted, because γ_nam is untestable. | open |
| Contemporaneous convergence | yes | Named in-flight placebo at matched lag: 1.10 [0.83, 1.43] vs named read 2.79 [2.48, 3.13] (post hoc, descriptive). O3 > 0 in the 3 estimable units. | partly (descriptive) |

**New constants (exploration, non-reserved).**
- η_sw (II/III) = −0.02 [−0.07, +0.02]: background switch-span elasticity, 24 regime-II/III units (A2 model).
- η_sw (I) = −0.34 [−0.51, −0.17]: the same, 17 regime-I units.
- η_sw (timer) = +0.46 [+0.09, +0.84]: the same on timer-wake background calls, 11 #51 units.
- R_nam = 2.79 [2.48, 3.13]: post hoc observed/expected hops onto a project in a named read, regime II/III. R_un = 0.93 [0.86, 0.99]; R_if = 1.10 [0.83, 1.43].
- f_flick = 0.257: share of call hops that return to the previous project at the next hop within 5 calls (all non-reserved hops, `project_calls --verify`).

**Claim that stands:** In regime II/III, an agent's background project-switch hazard runs on its own call clock, not on wall time (switch-span elasticity −0.02 [−0.07, +0.02] over 24 units; a wall clock gives 1). **Exclusions:** the named-read coupling (P1–P3, N1, N3) is untestable at the planted effect (A1). The post hoc read ratios (named 2.79, unnamed 0.93, in-flight 1.10) are descriptive only. Regime I (η −0.34, P5 failed), G31 (N4 failed) and G51 timer wakes (η +0.46, N2 failed) are excluded. P6 is not met.

## Round 2 redirects
**What the direction is really after:** whether naming an agent in a message that links a project moves that agent onto the project, beyond the attention burst that produces the message. Round 1 saw a 2.8× lift only post hoc, so round 2 must test it with power at the observed scale.
- **H133-R1. Test the named-read ratio with power at γ ≈ 2.** Pre-register R_nam as the primary statistic. The stacked count test has power 0.997 at γ_nam = 2. Keep units separate and use hierarchical shrinkage, not a stack.
- **H133-R2. Add a sender-side impostor.** The named message may answer the reader's own earlier mention of the project. Condition on the reader's last touch of b.
- **H133-R3. Explain η < 0 in regime I and η > 0 at timer wakes.** Split spans by gap kind (pause, long tool call, scheduled chat call). Test whether a long gap resets attention to the current project.
- **H133-R4. Fit the deferred variants.** Same-lab vs cross-lab senders and the kickoff-drop variant.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R-field (H28 attention burst), R-broadcast (H53 link in context), R-share (H53, H93), R-wall clock.
**Reserved periods used for confirmation:** none. Frozen and dry-run only: `analysis/confirm.py` (#45–#47 and the #51 tail; C1 = P4 on the A2 model; the read ratio descriptive). Dry run on stand-in 44a reproduces its η_sw (−0.09).

| Axis | Test | Score | Evidence (round 1, 2026-10-07) |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | per-call labels from strict mentions (`project_calls --verify`: 98.6% of mentions mapped, 0 recompute mismatches); η_sw is not invariant across regimes (−0.34 I, −0.02 II/III) |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | time-rescaling: per-call clock holds in II/III, not in regime I or at timer wakes; Markov order: 45% of read-linked hops come 2–5 calls after the read (O5) |
| C adequacy | beats the null hierarchy, day-blocked out-of-sample data | 1 | within-cell permutation: named-read ratio beyond the null in 16/24 II/III units (post hoc, descriptive); no out-of-sample test |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | O5 lag profile (0.55 at lag ≤ 1; P6 not met); in-flight and unnamed ratios ≈ 1, not fitted |
| E interventional | predicts the change across a natural experiment | 0 | no NE test in round 1 |
| F identifiability | synthetic recovery with village sampling; survives preprocessing variants | 1 | η_sw recovered (bias ≤ 0.02; W4 coverage 0.94–0.97); γ_nam not identifiable at the planted 1.0 (A1) |
| G ground truth | agrees with known structure | 0 | none |
| H comparative | beats the named rivals | 1 | R-wall clock rejected (Kill B); R-field and R-broadcast disfavoured only descriptively (in-flight 1.10, unnamed 0.93 vs named 2.79); R-share is a strong extra term |
| I transfer | holds in other same-mode periods, including the reserved periods | 0 | reserved periods not run |

## Results by goal period
Round 1 (2026-10-07). Folders: `goalperiod-subhypotheses/G<NN>/` (23 goal periods, 41 units). Verdict per folder: descriptive = P4 holds (or a small η is unpowered) and the coupling is untestable; mixed = η_sw CI excludes 0 in some unit (Kill B never fires) or a native fails; failed = a native fails or regime-I η_sw < 0.

| Period | Role | Verdict | Key numbers (η_sw A2 [95%]; named hops observed/expected) |
| --- | --- | --- | --- |
| G04, G12, G13, G18, G20, G24, G25, G26 | replication (regime I) | descriptive | η_sw CI ∋ 0 in each unit; γ_nam enters only in 18b and 26 |
| G17, G19, G21, G30 | replication (regime I) | failed | η_sw < 0 (17: −0.93 [−1.38, −0.48]; 30b: −0.29 [−0.53, −0.04]) |
| G31 | native N4 | failed | RE η_sw −0.22 [−0.34, −0.09] |
| G33, G36, G37, G41 | replication (regime II/III) | mixed | η_sw CI excludes 0 in 33, 36b, 37 (< 0) and 41 (> 0); 36b γ_nam +3.68 [+1.35, +6.55] |
| G38 | native N1 | descriptive | 38a η_sw −0.21 [−0.55, +0.13]; N1 untestable (3 named hops) |
| G39, G42, G44 | replication (regime II/III) | descriptive | P4 holds; 44a γ_nam +1.51 [+0.24, +2.79] |
| G40 | native N3 | descriptive | η_sw +0.07 [−0.21, +0.35]; 1 of 76 early hub hops had a named read |
| G51 | native N2 | mixed | 51a–51l η_sw −0.10 to +0.10 (CI > 0 in 51c, 51d); timer wakes RE +0.46 [+0.09, +0.84] (N2 failed); named hops 241 / 78.6 expected |

## Results
See "Round 1 (2026-10-07)" above: inconclusive by the card's rule. P4 holds in regime II/III. P5, N2 and N4 fail. P1–P3 are untestable. Post hoc and descriptive: named-read hop ratio 2.79 [2.48, 3.13].

## Notes
- 2026-10-07: card written from HH376 (approved by Vivian 2026-10-07). Round-1 order: structural counts (no outcomes) → per-period READMEs with dated predictions → synthetic on the real skeletons → dated amendments → replication and natives → estimates rows (`h133_gamma_named`, `h133_gamma_unnamed`, `h133_gamma_inflight`, `h133_eta_switch`) → frozen `confirm.py` (dry run only).
- Shared code: the per-call project label is needed by H133 and H134, so it goes in `infra/shared/project_calls.py` (STANDARDS §8), not in either card's folder.
- Compute: ≤ 2 threads, one heavy job at a time (STANDARDS §9).
- 2026-10-07: round 1 done. Shared builder `infra/shared/project_calls.py` (commit 18e52ee; used by H134 and H137). Synthetic and amendments committed before real data (c471f13). Estimates rows: `h133_eta_switch` (41 units), `h133_gamma_named` / `_unnamed` / `_inflight` (descriptive, where a term enters), and the natives `h133_eta_switch_timer` (#51 units), `h133_eta_switch_timer_RE` (G51) and `h133_eta_switch_RE` (G31).
