# H136: Zero-temperature Potts freeze at the read-out call: each agent commits to a named target at its first read of the kickoff, not at the kickoff time

**Status:** round 1 done (2026-10-07): **inconclusive; the HH's kill is untestable on exploration data.** The structural precondition failed in 17 of 17 kickoff units (at most 2 delayed active readers per unit; 5 needed), so no freeze time was computed. The reserved kickoffs are the only remaining test. Card first written 2026-10-07 from HH379 (approved by Vivian 2026-10-07), before any H136 statistic on real data.
**Question (GOALS.md):** **Q1** (what couples agents to a field: does the kickoff act on each agent at its own read-out call, as messages do in H08?). Second: **Q5** (operator lever: a target named in a kickoff is adopted as soon as each agent reads it, so the read-out spread sets the freeze time).
**Fields:** stat mech (zero-temperature kinetic Potts quench in a strong field), dynamics (event timing on the call clock), sociophysics (field vs copying)
**Literature:** [Kolchinsky, Dechant, Yoshimura & Ito 2026](../../literature/kolchinsky-2026-generalized-free-energy-excess-housekeeping.md) (Wasserstein speed limit T ≥ W/Ā, which H75 found saturated by named kickoffs). Cited from memory (†): Glauber, *J. Math. Phys.* 4, 294 (1963)† (single-spin-flip kinetics; at zero temperature in a strong field each spin aligns at its first update).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime; Driving / external field (the kickoff); **Exposure (ledger receiving call)** and **Receiving call**; **Agent state (categorical, project/artifact strict)** (H11) as the project map; H54's **quench target t̂_p** and kickoff naming rule (`infra/shared/kickoff_naming.py`); H75's **committing population**, **repo allocation p(t)**, **settling time T_e** and **agent settling time t_i**; H95's **speed-limit slack S** reading. New named variants proposed for DEFINITIONS.md (not edited there; defined under Data scheme and Observables): **kickoff read-out call t_r,i**, **read delay D_r**, **freeze touch t_f,i**, **post-read call lag K_i**, **delayed active reader**, **freeze anchor (kickoff read vs peer link)**.
**From:** HH379 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/10-potts/` (zero-temperature kinetic Potts in a strong field), `physics-models/02-nonequilibrium-ising/` (asynchronous updates at each agent's own calls; quench)

## Source HH (verbatim from the HH list)
- **HH379 · Freeze onto a named target happens at each agent's first read of the kickoff, not at the kickoff time.** H75/H95 found an instant freeze onto named targets. In a zero-temperature Potts model with a strong field, an agent commits at its first update after the field appears, and its updates are its calls that read the kickoff.
  - *Prediction:* per-agent commit time equals the time of that agent's first call whose context includes the kickoff, plus about one call. Agents who read it late commit late, by the same delay.
  - *Check:* kickoff messages; DQ1 context ledger; commit and first-action times per agent.
  - *Kill:* commit times align with the kickoff timestamp, not with each agent's first read.
  - *Impostors:* agents who start late both read and commit late. Use agents who were active before the kickoff but whose first post-kickoff call came later.
  - *Models:* 10, 02 · *Builds on:* H75, H95, H54, HH374

## What this card builds on (latest round of each cited card)
- **H75 (round 1, 2026-10-04):** where the kickoff names an artifact (G39, G40, G51), the allocation freezes within 15–30 active min (T_e 0.25–0.5 h) with slack S 1.00–1.40: each agent's first post-kickoff commit lands on its settled repo. G41 (no shared target) settles in 9.5 h (S 5.1). In G44, the room with a named target settles in 0.75 h (S 2.5) and the free room in 4.25 h (S 14.5) at equal switch rates (3.3 vs 3.4 per agent-hour). Newcomers settle in a median 0.28 active h (0.01–2.5 h). Limits: the state is seen only at commits, and T_e sits on a 0.25-h grid.
- **H95 (round 1, post hoc):** kickoffs that assign a concrete artifact give S 1.0–2.5 and T_e 0.25–0.75 h (G39, G40, G42, G44 #best, G51); open kickoffs give S 3.0–14.5 and T_e 4–13 h (G37, G38, G41, G44 #rest); exact Mann–Whitney p = 0.008. H95's pre-registered specificity gauge failed as a measurement.
- **H54 (round 2, 2026-10-04):** the day-1 content centroid identifies its own kickoff (top-1 18/33 bge, 20/33 gte). A human message pulls each reader at its first post-read message by Δ ≈ 0.09; reading adds +0.11–0.12 over in-flight messages at matched lag, and in-flight messages carry 40–50% of the pull. 9 of 13 kickoff-frozen projects carry the goal text's words.
- **H131 (HH374; round 1, 2026-10-04):** the read-aligned and clock-aligned switch-off could not be separated: no rival reply fell between a verdict and its speaker's read (0 in #12, 0 in #26). Verdict read delays had per-debate medians of 10–66 s (maximum 366 s) in #12 and 2–83 s in #26. That partition was empty on exploration data; H136 has the same risk.
- **H53 (round 1):** read-out delays of present agents have a median of 25 s; 88% fall within 2 min in regimes I/II but only 67% in regime III (90% within ≈ 12 min; 95% within ≈ 29 min). In G40 the kickoff-frozen hub was link-seeded 2.4 min into the kickoff, and 8 agents adopted it within 2 h at receptive count 0.
- **H128 (round 1):** the domain-wall fraction of work projects does not separate free from named kickoffs (freeze time p = 0.32, 7 vs 5 units). This disagrees with H75 and H95 on a different statistic; H136 tests per-agent timing, not the domain count.

## Question
After a kickoff that names a target, does each agent commit to the target at its own first call that has the kickoff in context (plus about one call)? Or do agents commit at a common delay after the kickoff post, whatever their read time?

**Practical payoff:** if the freeze is read-locked, an operator who needs the whole swarm on a new target within T minutes must make every agent read the kickoff within T minus one call. In regime III that means waking paused agents, because 33% of present agents read after 2 min (H53).

## Model
**From:** `physics-models/10-potts/` (zero-temperature kinetic Potts) and `physics-models/02-nonequilibrium-ising/` (asynchronous updates).

**H136 variant: a zero-temperature Potts quench with read-out updates.** At the kickoff post t_k a strong field h appears on the named target x. Agent i updates only at its own calls. At zero temperature with h larger than every other field (habit, ownership, share), the agent moves to x at its first update that sees h. The kickoff enters the agent's state at its kickoff read-out call t_r,i, the first call whose context holds the kickoff message (DQ1 ledger). So
t_f,i = t_r,i + K_i calls, K_i small (0–2) and independent of the read delay D_r,i = t_r,i − t_k.
At a finite temperature K_i is geometric, with a mean that rises as the field falls. It still does not depend on D_r.

**Rivals.**
- **R-clock (the HH's kill):** the freeze follows the kickoff post by a common delay, t_f,i = t_k + D_i with D_i independent of D_r (subject to t_f ≥ t_r). Late readers then commit sooner after reading (K falls with D_r).
- **R-copy (H53, H28):** agents freeze when they read a peer's link to or work on x, not when they read the kickoff. The freeze anchors on the first peer-link read.
- **R-late starter (the HH's impostor):** agents who start their day late read late and commit late. The anchor is the agent's first call of the day.
- **R-plan:** agents plan for a fixed number of calls after their day starts, then commit. The anchor is again the first call of the day, with a longer lag.

## Data scheme (`scheme/`)
`scheme/build.py` writes `data/processed/H136-freeze-at-first-kickoff-read/` from shared tables only.
- **Inputs:** `kicks_classified` (kind `goal_kickoff`; room kickoffs where DQ6 or H54 lists them), DQ1 `call_windows` and `context_ledger_items` (receiving calls of the kickoff message), `artifact_mentions` and `artifacts` (strict rule; project map as in `project_states`), DQ4 `work_commits` (agent-work filter; periods ≥ #30), `infra/shared/kickoff_naming.py` and `embeddings/goals.parquet` (named targets), `infra/shared/copying.py: project_messages` (peer links to the target), `calendar`, `period_units`, `roster`, `rooms_timeline`, `ground_truth_labels` (`room_assignment`, #44; role rows, #51). Read-only cross-check: H75's `agents.parquet` (settled repos, t_i). No message text.
- **Kickoff unit:** one goal kickoff message (or one room kickoff in #38 and #44) with ≥ 1 named target. Named targets come from H54's naming rule (strict link in the kickoff, or a distinctive name token in the kickoff or goal text).
- **Kickoff read-out call t_r,i (proposed variant):** the agent's receiving call of the kickoff message (`context_ledger_items.message_id`). **Read delay D_r,i** = t_r,i − t_k in active time (calendar windows).
- **Freeze touch t_f,i (proposed variant; primary):** the agent's first strict touch of its target after t_k, from sources action and intention (work-side mentions, not chat announcements). The target is the named project on which the agent settles (H75's settled repo, held longest in the last 4 active hours of a 20-h horizon). Agents whose settled project is not named are "not frozen" and leave the timing sample. **Variants:** sources including chat; the first DQ4 agent work commit to the target (periods ≥ #30; H75's t_i).
- **Post-read call lag K_i (proposed variant):** the number of the agent's own calls strictly after t_r,i and up to the freeze call (0 = the read call itself touched the target).
- **Delayed active reader (proposed variant; the HH's impostor control):** an agent with ≥ 1 own call in the 30 active min before t_k and with D_r ≥ 2 min or ≥ 2 own calls after t_k.
- **Peer-link anchor:** the agent's first receiving call, after t_k, of an agent message that links the target (`project_messages` × ledger).
- **First call of the day:** the agent's first `call_windows` row on the kickoff's PT day.
- **Output:** `agents.parquet` (unit, agent, t_k, t_r, D_r, active-before flag, t_f per variant, K per variant, peer-link anchor, first call of the day; target hashed), `results/`, `synthetic/`, `_provenance.json`. Expected < 5 MB.
- **#51 note:** #51's private goals enter through `agent_goals`, not a chat message, so the ledger cannot time their read. #51 is excluded unless a DQ6 role row points to a readable message. NE38 is kept only if its reassignment is a readable message.
- **Reserved rows** are dropped with the shared reserved-row mask in `infra/shared/common.py`.

**Structural precondition (counted before any outcome; H131's lesson):** for each kickoff unit, count the delayed active readers and the spread of D_r among them. The kill test (O1, O3) is testable in a unit only with ≥ 5 delayed active readers. If no unit passes, the HH's kill is declared untestable on exploration data before any freeze time is computed.

## Observables
- **O1 · Read-alignment slope b:** across agents within a kickoff unit, Theil–Sen and OLS slope of D_f = t_f − t_k on D_r (active time). H136: b = 1. R-clock: b near 0 (above 0 only through truncation at t_f ≥ t_r, sized by the synthetic). Pooled across testable units by random effects (exception (d)), next to per-unit slopes.
- **O2 · Post-read call lag K:** median K and the share with K ≤ 2, per unit and per variant.
- **O3 · Lag independence:** Spearman ρ(K_i, D_r,i) among delayed active readers. H136: ρ ≈ 0. R-clock: ρ < 0.
- **O4 · Anchor comparison:** the spread (median absolute deviation, in own calls) of the freeze relative to each anchor: kickoff read, peer-link read, first call of the day, kickoff post. H136 predicts the kickoff-read anchor gives the smallest spread.
- **O5 · Freeze share (descriptive):** the share of the committing population whose settled project is named.

## Null / baseline
- **N1 · Synthetic worlds on the real skeletons (decision null):** W1 read-locked, W2 clock, W3 late starter, W4 copy (below). The observed b, K and ρ are read against W1 and W2 bands.
- **N2 · Within-unit permutation of D_r:** permute read delays among the unit's delayed active readers (keeps both marginals, breaks the alignment). 2,000 draws for O1 and O3.
- **Strongest rival:** R-clock with truncation, which can produce b > 0 when read delays are as long as commit delays.

## Impostors (STANDARDS §1)
| Impostor | Relevant? | How it is handled | Status |
| --- | --- | --- | --- |
| Scheduler field | yes | Day starts make late readers late committers (R-late starter). The decisive sample is delayed active readers (active before t_k); the first-call-of-the-day anchor is a rival in O4. | planned |
| Exogenous field (kickoff, goal, operator) | yes, the object | The kickoff is the field. Other human messages after t_k are flagged; agents that read a human message about the target before their freeze are reported separately. | n/a (object of study) |
| Shared model priors | partly | Every model may pick the same first project for a goal genre. The named-target restriction and H54's genericness correction address this partly; lab mix of K is reported. | planned (partly) |
| Contemporaneous convergence | yes | Agents may copy early movers (R-copy). The peer-link anchor (O4) and a flag for agents whose freeze follows a peer-link read are reported; an in-flight placebo uses peer links posted but not yet read at the freeze call. | planned |

## Design: two layers (STANDARDS §4)
**Unit of analysis:** one kickoff (goal period, or room kickoff), a transition design (exception (c): the transition is the object). Kickoffs are compared as phase-diagram points; the pooled slope is a random-effects mean next to per-unit values.
- **Replication (role `replication`):** every non-reserved kickoff with a named target that meets the precondition. Candidates: regime III G37, G38 (two room kickoffs), G39, G40, G41, G42, G44 (#best and #rest); regime II G33, G35, G36; regime I G30, G31 and the regime-I kickoffs with an H31 kickoff-frozen consensus event (listed from H31's events file at the structural pass).
- **Natives (role `native`):**
  - **N1 · G44 rooms (same day).** #best has a named target; #rest picks freely. H136 predicts a read-locked freeze in #best (K small, independent of D_r) and no freeze to time in #rest.
  - **N2 · G40 (NE42 merge; R-copy test).** The kickoff named the hub, and a link seeded it 2.4 min in (H53). The anchor comparison (O4) decides between the kickoff read and the hub-link read.
  - **N3 · NE38 (descriptive; one agent).** Opus 5's role reassignment on 2026-07-29: the read of the reassignment message (if it is a readable message) against the first touch of the new role's repo (H75: 2.0 h on commits).
- **Reserved (confirmation only; never read in exploration):** the kickoffs of #43 and #45–#50 (H75's and H95's confirmation targets), the regime-I and II reserved kickoffs (#1, #9, #14, #15, #22, #28, #29, #32, #34) and the #51 tail. A frozen `analysis/confirm.py` is written after round 1 and runs only with Vivian's sign-off. Disclosure: the H95 agent read #47's setup lines (a Help Kit live within 11 minutes), so any #47 freeze-time result carries that disclosure. Reuse with H75, H95, H54 and H97 (kickoff family) is disclosed in `LOG.md` when run.

## Synthetic validation plan (axis F; run before any real-data statistic)
`analysis/synthetic.py` on the real kickoff skeletons of G39, G40, G42, G44 #best and one regime-I kickoff: real per-agent call times around t_k, real kickoff receipts, real peer-link receipts. 500 runs per world.
- **W1 read-locked (H136):** freeze at the read call plus K calls, K ~ Geometric(0.5) − 1.
- **W2 clock:** freeze at t_k + D, D log-normal with median 20 active min and log-SD 0.8 (H75's 15–30 min scale), truncated to after the read call.
- **W3 late starter:** freeze at the agent's first call of the day plus a log-normal delay; reads unrelated.
- **W4 copy:** freeze at the first peer-link read plus K calls.
- **Read:** the power to separate W1 from W2 with O1 (b CI ∋ 1 and excludes 0) and O3 (ρ CI ∋ 0 vs ρ < 0) at the real D_r spread; the b that truncation alone gives in W2; the O4 anchor that wins in each world.
- **Pass rule:** O1 and O3 count as the HH's kill test only in units where W1 vs W2 power is ≥ 0.8 and size ≤ 0.10. Elsewhere they are descriptive. A dated amendment, written before any freeze time is computed, records which units qualify.

## Prediction
*Written 2026-10-07, before any H136 statistic on real data. What I had seen: the cards of H75, H95, H54, H131, H53 and H128 at their latest rounds (numbers above); the `kicks_classified` kinds (51 goal kickoffs). No kickoff receipt, read delay, freeze time or call lag had been computed.*

| ID | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| S0 (precondition) | ≥ 2 kickoff units have ≥ 5 delayed active readers (regime III kickoffs most likely) | < 2 units | 0.4 |
| S1 | In units with fewer than 10 delayed active readers, W1 vs W2 power is < 0.8 | power ≥ 0.8 | 0.7 |
| P1 (HH) | **Read alignment.** Pooled b CI ∋ 1 and excludes 0, outside W2's band | b CI ∋ 0 (R-clock) | 0.4 |
| P2 (HH) | **About one call.** K ≤ 2 for ≥ 1/2 of frozen agents (freeze touch, action and intention sources) | median K ≥ 5 | 0.45 |
| P3 (HH) | **Late readers lag by the same delay.** Spearman ρ(K, D_r) CI ∋ 0 among delayed active readers | ρ < 0 with CI < 0 | 0.45 |
| P4 | **The kickoff read is the anchor.** O4 spread is smallest for the kickoff-read anchor in ≥ 2/3 of testable units | peer-link or day-start anchor smaller in > 1/3 | 0.45 |
| P5 | On commits (DQ4 variant) the median K is ≥ 5 calls (commit latency, H75's 15–30 min) and ρ(K, D_r) still ∋ 0 | none (descriptive) | 0.5 |
| N1 | G44: #best meets P2 and P3; #rest has < 1/3 of agents frozen on a named target within 2 active h | #best K large or ρ < 0 | 0.4 |
| N2 | G40: the kickoff-read anchor beats the hub-link anchor (O4) | the hub-link anchor wins (R-copy) | 0.35 |
| N3 | NE38: descriptive (one agent) | none (descriptive) | none |

**Kill rules (from the HH, sharpened).**
- **Kill (HH):** in units that pass the synthetic rule, the pooled b has a CI that includes 0 and excludes 1, or ρ(K, D_r) < 0 with CI < 0. Commit times then align with the kickoff post, and H136 fails.
- **Untestable:** if S0 fails (no unit with ≥ 5 delayed active readers) or no unit passes the synthetic rule, the kill is untestable on exploration data. P2 and P4 are then reported as descriptive, and the reserved kickoffs are the only test.

**Verdict rule.** *Supported:* P1, P2 and P3 hold in units that pass the synthetic rule, and P4 holds. *Narrowed ("freeze within about one call of the first read; read vs clock untestable"):* P2 and P4 hold with the kill untestable. *Failed:* the kill fires, or the peer-link anchor wins in ≥ 2/3 of units (R-copy). *Inconclusive:* otherwise.

**My credence before data:** supported 0.15; narrowed 0.3; failed 0.2; inconclusive 0.35. The main risk is H131's: reads follow the kickoff within seconds for most active agents, so the read and clock alignments coincide.

## Round 1 (2026-10-07)
Order run: structural pass (no freeze time) → precondition record → synthetic on real skeletons → Amendment A1 → stop. Code: `scheme/h136lib.py`, `scheme/structure.py`, `analysis/synthetic.py`, `analysis/run.py`, `analysis/figures.py`. Data: `data/processed/H136-freeze-at-first-kickoff-read/` (`structure/`, `synthetic/`, `results/`; < 1 MB). Every call and receipt row passes `holdout_mask`; reserved days are dropped.

### 1. Structural precondition (counted 2026-10-07, before any freeze time)
**Units (17).** The card's candidates: G30, G31, G33, G35, G36, G37, G38 (#best, #rest), G39, G40, G41, G42, G44 (#best, #rest). H31's `events_ep_w30` adds the regime-I kickoffs with a kickoff-frozen event (frozen, t0 ≤ 0.75 h): G18, G19, G26 (G30 is already listed). Kickoff messages are the `kicks_classified` human kickoffs (goal_fields rule); t_k is the unit's first kickoff message; t_r,i is the first DQ1 receiving call of any unit kickoff message. "Own calls" exclude summary calls (consolidate, session start and stop; H75's rule). The named-target condition was not evaluated, because no unit passed the count.

**Rule as applied.** A delayed active reader has ≥ 1 own call in the 30 active min before t_k, and D_r ≥ 2 active min or ≥ 2 own calls in (t_k, t_r). Active minutes concatenate the calendar windows.

| Unit | Readers | Active before | Delayed | Delayed active readers | Read = first call of day | Max D_r (active min) |
| --- | --- | --- | --- | --- | --- | --- |
| G18 | 7 | 7 | 0 | 0 | 1 | 0.2 |
| G19 | 7 | 7 | 0 | 0 | 5 | 0.2 |
| G26 | 10 | 10 | 0 | 0 | 7 | 0.6 |
| G30 | 11 | 0 (prev. day reserved) | 0 | 0 | 1 | 0.5 |
| G31 | 11 | 11 | 0 | 0 | 7 | 0.6 |
| G33 | 11 | 0 (prev. day reserved) | 3 | 0 | 5 | 18.8 |
| G35 | 11 | 0 (prev. day reserved) | 1 | 0 | 11 | 5.7 |
| G36 | 12 | 12 | 0 | 0 | 8 | 1.1 |
| G37 | 12 | 12 | 0 | 0 | 12 | 0.0 |
| G38 #best | 3 | 3 | 0 | 0 | 3 | 0.0 |
| G38 #rest | 9 | 8 | 0 | 0 | 9 | 0.8 |
| G39 | 14 | 12 | 3 | **2** | 13 | 243.9 |
| G40 | 15 | 15 | 0 | 0 | 15 | 1.4 |
| G41 | 14 | 14 | 0 | 0 | 14 | 0.2 |
| G42 | 15 | 15 | 0 | 0 | 15 | 0.3 |
| G44 #best | 4 | 0 (prev. day reserved) | 0 | 0 | 4 | 1.4 |
| G44 #rest | 12 | 0 (prev. day reserved) | 0 | 0 | 12 | 0.2 |

- **Pooled (descriptive):** 178 kickoff readers. 171 (96%) read within 2 active min. The wall-clock read delay has a median of 68 s and a 90th percentile of 93 s; most of it is the gap between the kickoff post and the day window start.
- **Why.** Every kickoff in these units is posted 0.6–1.6 min *before* the day window opens. The agents boot at the window start, so the kickoff read is the agent's first decision call of the day in 142 of 178 cases. In the other 36 it is a summary or session-start call just before it. No reader has any own call between t_k and t_r (0 of 178).
- **Sensitivity.** Dropping the active-before condition entirely gives at most 3 delayed readers per unit (G33, G39). The count also fails for the 5 units whose previous day is reserved. The failure does not depend on the masked days.
- **Declared 2026-10-07, before any freeze time:** S0 fails (0 units with ≥ 5 delayed active readers; the card expected ≥ 2). **The HH's kill (O1, O3) is untestable on exploration data in all 17 units.** As instructed for this run, the outcome analysis stops for these units. No freeze touch, commit time, settled project, call lag K or peer-link read was computed. P2 and P4, which the card would report as descriptive, were therefore not computed either.
- **NE38 (native N3):** excluded by the card's own rule. DQ6's role row for Opus 5's new role (2026-07-29) cites `agent_goals`, not a chat message, so the ledger cannot time its read.
- **#51:** excluded by the card's #51 note (private goals via `agent_goals`).

### 2. Synthetic validation (real skeletons; 500 runs per world; seed 20261007)
The skeletons are G39, G40, G42, G44 #best and G26 (regime I). Each uses the real t_r and real own-call times after it. The worlds are W0 (no coupling: a random own call in the first 240 active min), W1 (read-locked), W2 (clock, the strongest rival) and W3 (late starter). W4 (copy) was not run, because it needs the named target's peer-link reads, which the stop keeps closed. A read-lock call means the Theil–Sen 95% CI of b contains 1 and excludes 0. A clock call means the Fisher-z 95% CI of ρ(K, D_r) lies below 0.

| Skeleton | n (card sample / all readers) | O1 power W1 (card / all) | O1 size W2 (all) | O1 rate W3 (all) | O3 power W2 (all) | O3 size W1 (all) | Passes the card's rule |
| --- | --- | --- | --- | --- | --- | --- | --- |
| G39 | 2 / 14 | 0.00 / 0.96 | 0.05 | 0.10 | 0.07 | 0.02 | no (card sample); all-readers only |
| G40 | 0 / 15 | 0.00 / 0.58 | 0.00 | 0.00 | 0.05 | 0.00 | no |
| G42 | 0 / 15 | 0.00 / 0.31 | 0.00 | 0.00 | 0.08 | 0.02 | no |
| G44 #best | 0 / 4 | 0.00 / 0.51 | 0.01 | 0.01 | 0.00 | 0.00 | no |
| G26 | 0 / 10 | 0.00 / 0.02 | 0.00 | 0.00 | 0.06 | 0.02 | no |

- **S1 (power < 0.8 below 10 delayed active readers): holds.** The card sample has 0–2 readers, so O1 and O3 make no decision (power 0). The truncation bias of W2's slope is not identifiable at this D_r spread: W2's median b is −0.8 to 2.0, and its 90% band reaches −64 to +112.
- **O3 cannot detect R-clock** even when all readers are used: the power is ≤ 0.08 in every skeleton. Most readers have D_r = 0, so ρ(K, D_r) has almost no spread.
- **The all-readers O1 in G39 (power 0.96, size 0.05) is a widening, not the card's test.** Its leverage is one reader who read the next day (D_r 244 active min, not active before t_k). That reader is the late-starter case, and W3 gives a read-lock call in 10% of runs. This is recorded as a round-2 idea, not as a test.
- **O4 anchors coincide.** No own call falls between t_k and t_r, so the kickoff-read and kickoff-post anchors give the same call count for every reader. In 76–100% of runs no anchor wins strictly, in every world.

### 3. Amendment A1 (2026-10-07, before any freeze time; not post hoc on outcomes)
- **O4 / P4 amended.** On exploration skeletons the kickoff-read and kickoff-post anchors are identical in own-call units (0 of 178 readers have a call in between). The first call of the day differs from them by at most one summary call. O4 can therefore separate the kickoff read only from the peer-link anchor. P4 is restated as "the kickoff-read anchor beats the peer-link anchor". The day-start and post anchors are reported as tied by construction.
- **Active-before window.** All kickoffs are posted just before the day window opens, so "30 active min before t_k" falls on the previous day's last half hour. The impostor control then selects agents who were active the evening before. It does not select agents who were active just before the kickoff. Any reserved-kickoff run should add a same-day variant (≥ 1 own call on the kickoff day before t_k). That variant is empty for all 17 exploration units.
- **No unit qualifies under the synthetic pass rule** (power ≥ 0.8 and size ≤ 0.10 in the card's sample). The amendment the card requires before any freeze time therefore lists no qualifying unit.

### 4. Predictions vs results
| ID | Prediction | Result (95% CI, scope) | Verdict by the rule |
| --- | --- | --- | --- |
| S0 | ≥ 2 units with ≥ 5 delayed active readers | 0 of 17 units; maximum 2 (G39). Without the active-before condition, the maximum is 3 (G33, G39) | **failed** → kill untestable |
| S1 | Below 10 delayed active readers, W1 vs W2 power < 0.8 | Card sample: power 0.00 in all 5 skeletons. All readers: 0.02–0.58, except G39 0.96 (one next-day reader) | **holds** |
| P1 | Pooled b CI ∋ 1, excludes 0, outside W2's band | not computed (precondition stop) | untestable |
| P2 | K ≤ 2 for ≥ 1/2 of frozen agents | not computed (precondition stop; the card's descriptive fallback was not run) | not run |
| P3 | ρ(K, D_r) CI ∋ 0 among delayed active readers | not computed; O3 power under W2 is ≤ 0.08 even on all readers | untestable |
| P4 (A1) | The kickoff-read anchor beats the peer-link anchor | not computed (precondition stop). The read, post and day-start anchors coincide by construction (A1) | not run |
| P5 | Commits: median K ≥ 5, ρ ∋ 0 | not computed | not run |
| N1 | G44: #best meets P2, P3; #rest < 1/3 frozen within 2 h | #best 0 and #rest 0 delayed active readers (4 and 12 readers). Previous day reserved | untestable |
| N2 | G40: the kickoff-read anchor beats the hub-link anchor | 0 delayed active readers of 15. Not computed | untestable |
| N3 | NE38 descriptive | excluded: the reassignment is an `agent_goals` row, not a readable message | n/a |
| Kill (HH) | b CI ∋ 0 and excludes 1, or ρ < 0 with CI < 0, in qualifying units | no qualifying unit | **untestable** |

**Read-out statistics** (descriptive, all 17 units; `per_period_estimates`, channel `readout`). 171 of 178 readers (96%) read within 2 active min. Per unit, the share is 0.79 [0.52, 0.92] in G39, 0.73 [0.43, 0.90] in G33, 0.91 [0.62, 0.98] in G35 and 1.00 in the other 14 units (Wilson 95%). The per-unit median wall-clock read delay is 31–88 s (bootstrap 95% CIs in the period READMEs). It is set mainly by the boot gap after the kickoff post.

**Verdict by the card's rule: inconclusive.** The kill is untestable. P2 and P4 were not computed, so the "narrowed" outcome cannot be reached.

### 5. Impostors (STANDARDS §1), as handled in round 1
| Impostor | Relevant? | How it is handled | Status |
| --- | --- | --- | --- |
| Scheduler field | yes, decisive | The kickoff is posted about 1 min before the day window opens. Kickoff read and day boot therefore coincide for 142 of 178 readers, and for the other 36 they are one summary call apart. The delayed-active-reader control was counted and is empty (≤ 2 per unit). | open (untestable on exploration data) |
| Exogenous field (kickoff, goal, operator) | yes, the object | The kickoff is the field. No other human messages were examined, because no freeze time was computed. | n/a (object of study) |
| Shared model priors | partly | Not reached (no target or freeze data read). | open |
| Contemporaneous convergence | yes | Not reached. The peer-link anchor (O4) and W4 were not run. | open |

### 6. Scorecard (round 1)
A 1 · B 0 · C 0 · D 0 · E 0 · F 1 · G 0 · H 0 · I 0 (details in the main scorecard below).

**Claim that stands:** In 17 non-reserved day-start kickoff units (G18–G44), 171 of 178 kickoff readers (96%) read the kickoff within 2 active min, at day boot, with at most 2 delayed active readers per unit. So the read-locked vs clock freeze test is untestable on exploration data. *Exclusions:* P1–P5, N1 and N2 not computed (precondition stop); NE38 excluded (no readable message); the G39 all-readers O1 power of 0.96 is a synthetic, post hoc widening and not a result.

## Round 2 redirects
**What the direction is really after:** whether a field acts on each agent at its own read-out call; this needs a field that arrives while agents are already calling, not at day boot.
- **H136-R1. Mid-day fields.** Test read vs clock on fields that a chat message carries mid-day: operator reassignments with a `chat_core` source in DQ6, room kickoffs posted inside a window, or NE events with readable messages. Day-start goal kickoffs cannot separate read from clock.
- **H136-R2. Reserved kickoffs: check the post time first.** The reserved kickoffs (#45–#47, #49) are probably day-start kickoffs too, and then the same precondition fails. Compare each post time with its window start (a calendar fact) before spending a reserved use. No `confirm.py` was frozen in round 1, because no freeze-time pipeline exists yet.
- **H136-R3. All-readers widening (post hoc idea).** The G39 all-readers O1 power (0.96, synthetic) rests on one next-day reader. If pre-registered, it needs the late-starter world (W3) as its null.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R-clock (common delay after the post), R-copy (peer-link anchor), R-late starter, R-plan.
**Reserved periods used for confirmation:** none yet. Planned: the kickoffs of #45–#47 and #49 (frozen after round 1; not run).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | t_k, t_r,i, D_r and the delayed-active-reader flag are built from `kicks_classified`, DQ1 receipts and `call_windows` in 17 units across regimes I–III. The freeze touch and K were not built (precondition stop). |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 0 | not reached |
| C adequacy | beats the null hierarchy, day-blocked out-of-sample data | 0 | not reached |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | not reached |
| E interventional | predicts the change across a natural experiment | 0 | NE38 excluded (no readable message); no mid-day kickoff |
| F identifiability | synthetic recovery with village sampling; survives preprocessing variants | 1 | Synthetic on 5 real skeletons (4 worlds × 500). Read vs clock is not identifiable at the real D_r spread (card-sample power 0; O3 power ≤ 0.08). The check worked and showed the design cannot. |
| G ground truth | agrees with known structure | 0 | no ground truth for freeze times |
| H comparative | beats the named rivals | 0 | not reached |
| I transfer | holds in other same-mode periods, including the reserved periods | 0 | not run |

## Results by goal period
Round 1 (2026-10-07). Each folder holds the structural counts and, where a skeleton was used, the synthetic power. `goalperiod-subhypotheses/GNN/` is the unfilled template.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | n/a (untestable) | 7 readers, 0 delayed active readers |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | n/a (untestable) | 7 readers, 0 |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication (synthetic skeleton) | n/a (untestable) | 10 readers, 0; all-readers O1 power 0.02 |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | n/a (untestable) | 11 readers, 0 (previous day reserved) |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | n/a (untestable) | 11 readers, 0 |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | n/a (untestable) | 11 readers, 0 (3 delayed; previous day reserved) |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | n/a (untestable) | 11 readers, 0 (previous day reserved) |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | n/a (untestable) | 12 readers, 0 |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | n/a (untestable) | 12 readers, 0 |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication (#best, #rest) | n/a (untestable) | 3 + 9 readers, 0 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication (synthetic skeleton) | n/a (untestable) | 14 readers, 2 (the maximum) |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication + native N2 | n/a (untestable) | 15 readers, 0 |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | n/a (untestable) | 14 readers, 0 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication (synthetic skeleton) | n/a (untestable) | 15 readers, 0 |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication + native N1 | n/a (untestable) | 4 + 12 readers, 0 (previous day reserved) |
| [NE38](goalperiod-subhypotheses/NE38/README.md) | native N3 | n/a (excluded) | reassignment not a readable message |

## Results
**Round 1 (2026-10-07): inconclusive; the kill is untestable on exploration data.** Every non-reserved goal kickoff is posted about 1 min before the day window opens, so each agent reads it at boot. In 17 units, 171 of 178 readers (96%) read within 2 active min, and no unit has more than 2 delayed active readers (5 needed). No freeze time was computed. Details: Round 1 above.

## Notes
- 2026-10-07: card written from HH379 (approved by Vivian 2026-10-07). Round-1 order: structural counts (kickoff receipts, delayed active readers; no freeze time) → precondition note → period READMEs with dated predictions → synthetic → dated amendment naming the qualifying units → replication and natives → estimates rows (`h136_read_alignment_slope`, `h136_postread_call_lag`, `h136_lag_delay_rho`) → frozen `confirm.py` (dry run only).
- H75's freeze times are on commits and a 0.25-h grid. H136's primary freeze touch uses action and intention mentions, which H75-R2 notes are about 25× denser than commits.
- Compute: ≤ 2 threads, one heavy job at a time (STANDARDS §9).
- 2026-10-07 (round 1): the precondition failed in 17/17 units; outcome analysis stopped before any freeze time. Estimates rows written: `h136_delayed_active_readers`, `h136_kickoff_read_delay_median_s`, `h136_share_read_within_2_active_min` (channel `readout`, 17 units each, `local:k<unit>`). The planned slope, lag and ρ rows were not written. No `confirm.py` was frozen.
