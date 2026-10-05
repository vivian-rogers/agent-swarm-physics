# H41: Read-out gating gives the swarm a light cone

**Status:** exploratory round 1 done (2026-10-04); **round 1b (room-index fix, 2026-10-04) re-ran #33, #38, #44 and #51: see "Round 1b" below. Where this block and later sections disagree with Round 1b, Round 1b wins.** Card, definitions, nulls and dated predictions written ~06:00 UTC, before any real-data light-cone statistic; synthetic validation and amendments A1–A5 before real data; A6 (delay-matched jump) is post hoc and labelled.
- **Inside a room the logged light cone holds:** across 32 non-holdout periods (133,549 novel marker items, 45,183 adoptions), adoptions by agents in the source's room almost never precede the first model call that could read the item (robust acausal share median 0.6%, max 4% in a 25-adoption period). In one room this bound is only one call wide, and a shared field would also pass it (synthetic).
- **The pre-registered gating test mostly failed:** the hazard at the first entry call over the call in flight, J_in, has lower CI > 1 in 12/32 periods (verdicts by rule A4: 11 supported, 18 failed, 3 n/a). The cause is a recency confound: adoption hazard falls 10–20× with time since the item appeared, and in-flight calls all sit near t0. **Post hoc**, matching for delay since t0 (J_mh, validated afterwards on synthetic data: field ≈ 1, 8% false positives), the jump passes in 22/32 (post-hoc verdicts 20 supported, 9 failed, 3 n/a). The in-flight hazard is still ≈ 38% of the entry hazard: about a third of fast adoptions are co-generated. Names gate (J_mh,N lower CI > 1 in 24/29); numbers are co-generated (median J_mh,D 0.88); links essentially never appear before read-out.
- **Across rooms the logged cone is a cage, and NE42 moves it:** 75–100% of cross-room adoptions lie outside the logged cone in 7/8 two-room periods. In #38 the cross-room hazard is 0.001× the within-room hazard, and cross-room adoptions come about 71 h later. NE42's merge raised the cross-group hazard 82× over #39 and 863× over #41, and the cross-group acausal share went 1.00 → 0.02 → 1.00 (native verdict supported). ~~#51's #focus hoppers bridge rooms (97% of cross-room adoptions in the cone).~~ **1b:** with true rooms, #51's #general ↔ #focus hoppers bridge only half the time (51% of 839 cross-room adoptions in the cone, mostly over 2–3 hops); the 97% was a stale-room artifact.
- **The leaks cannot be traced from logs:** the channel classifier "explains" 82% of robust violations, but also 82% of in-cone controls. Shared repos (lift 1.04), sites (0.94) and history search (0.89) are not enriched. Only human cross-posts (27×), shared reply parents (2.1×), room moves (1.8×) and the agent's own private stream (1.5×) are.
- **Velocity is set by talk turns, not cadence or volume:** the front advances one hop per 47 / 46 / 16 receiving calls (regimes I / II / III), i.e. one hop per 5 / 2 / 1.5 talk calls, 6–25 min. Cadence predicts nothing within periods (b > 0 in 3/25), and more room traffic does not speed spread.
- Native tests: NE42 supported; G38 mixed (cage yes, artifact leak no); G31 mixed (regime-I gating not weaker than regime III; clock test inconclusive); G51 mixed (1b: hoppers bridge only half the time, fails; cadence fails; only one isolated adoption). Scorecard A1 B1 C1 D1 E1 F1 G1 H1 I1. `analysis/confirm.py` written and dry-run on stand-ins, not run. Not promoted.

**Fields:** info theory, stat mech, dynamics, sociophysics
**Literature:** none of the light-cone / temporal-network papers is in `literature/` yet; cited from memory (†): Lieb & Robinson, *Commun. Math. Phys.* 28, 251 (1972)†; Holme & Saramäki, *Phys. Rep.* 519, 97 (2012) (time-respecting paths)†; Pan et al., *PRL* 113, 238702 (2014) (path lengths in temporal networks)†. Project cards used: H08 (read-out gating), H34 (marker rule, field pitfall), H05 (rooms cut), H18, H29, H27, H31.
**Definitions used** (`physics-models/DEFINITIONS.md`): Regime; Population N(t); Interaction (broadcast) with the named variant **Exposure (turn read-out)** (H08; implemented by the DQ1 context ledger); Contagion / adoption event, with H34's **Idea (H34 marker rule)**. New terms, defined under "Operational definitions" and proposed for DEFINITIONS.md (not edited; outside H41's scope): **interaction (read-out, ledger)**, **logged light cone (time-respecting)**, **cone entry call**, **acausal adoption**, **cycles to adoption**, **static hop distance (pre-item read-out graph)**.
**From:** HH155 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` (with HH187) · **Models:** `physics-models/02-nonequilibrium-ising/`, `physics-models/03-contagion/`
**Data inputs (shared tables first):** DQ1 `call_windows`, `context_ledger_items` (who read what at which call); `chat_core`, `chat_text` (in memory only, non-holdout), `artifact_mentions` / `artifacts`, `artifact_commands_text` and `intentions_text` (in memory only, for the private-stream channel), `statement_flags`, `reply_pairs`, `rooms_timeline`, `kicks_classified`, `calendar`, `roster`. Read-only code import: H34's `scheme/markers.py` and `scheme/build_markers.py` (marker rule).

## Standards (2026-10-04)
*Documentation pass against `STANDARDS.md`. No analysis was re-run. Round 1 already ran on the corrected inputs. (Later the same day a pipeline bug, the room index, forced a re-run: see "Round 1b (room-index fix)".)*

**Question served:** Q1. The card measures how far and how fast information moves per read-out call, inside and across rooms.

| Impostor | Relevant? | How it was handled | Status |
| --- | --- | --- | --- |
| Scheduler field | partly | Hazards are per talk call on ledger call times; J_mh matches on delay since t0 (A6). No activity-synchrony statistic. | removed |
| Exogenous field (kickoff/goal/operator) | yes | Shared-field rival R1 simulated on real schedules (N1, T2): J_mh ≈ 1 under a field, 1/12 false positives. Numbers behave like a field (J_mh,D 0.88). Human and Claude Code uses are injectors, not relays. NE42 is confounded with #40's shared goal. | partly |
| Shared model priors | partly | Not handled. Same-family models may co-generate a marker without reading it. Close with J_mh split by same- vs cross-family source–adopter pairs (§1, row 3). | open |
| Contemporaneous convergence | yes | The design is the in-flight placebo: the call in flight at t0 vs the first post-entry call, matched on delay (J_mh). About a third of fast adoptions are co-generated (1/J_mh 0.38). The estimator is post hoc (A6). | removed |

**Inputs:** round 1 uses the context ledger, DQ2 `reply_pairs`, `statement_flags` and the 200-event cap. Still old: none of the listed inputs. Activity bins, embeddings, work and failures are not inputs.

**Two layers:** 29 replication folders. Native tests: 4 (`NE42` supported; `G31`, `G38` and `G51` mixed).

**Confirm script:** `analysis/confirm.py` exists, dry-run only, on ledger inputs, with J_mh as C1. No re-freeze for inputs. **Fix the broken C4 isolation check before any holdout run** (holdout.md item 16).

## Question
Does information propagate at most one read-out hop per call cycle, giving a Lieb–Robinson-style bound on how fast a novel item reaches agents k hops away on the interaction graph?

**Vivian's scope (2026-10-04):** measure the light cone over the interaction (read-out / exposure) graph, in graph hops counted in recipient call cycles, not over rooms. Rooms are one coarse-graining to compare against. Violations of the bound reveal unlogged channels (shared artifacts, memory, web).

## Design: two layers (Vivian, 2026-10-04; see `infra/data-quality/QUEUE.md`)
- **Replication:** the common estimator on every eligible goal period (comparable phase-diagram points). Period README role: `replication`.
- **Period-native tests:** 2–4 goal periods (or NEs) whose setup gives special leverage for this question, each with its own observable, null, ground truth or intervention, its own dated prediction, and period-specific tooling where needed. Period README role: `native`.

Chosen native tests (fixed before any real-data run):
1. **G38, the two-room cage** (#best / #rest, 17 days, the largest two-room period). Cross-room arrivals can only go through a room-mover, a human, or an unlogged channel (shared repos, the web). Leverage: a known cut in the read-out graph.
2. **NE42, merge and split** (#39 two rooms → #40 merged into #universe-coordination → #41 split back to the same partition). Graph distance between the two former groups drops from ≥ 2 (or ∞) to 1 and back: an A-B-A on hop distance.
3. **G31, a regime-I week** (one room, 11–12 agents). Chat-mode calls are *scheduled* (≈ 74 s cadence), not chained, so the cycle unit differs from regime III. Leverage: which clock (wall time, all calls, chat-mode calls) makes adoption delays homogeneous across agents.
4. **G51, isolation and hopping rooms** (21–29 agents). Newcomers sat alone in onboarding rooms (NE32's Sol/Terra/Luna rooms on 07-09, Grok 4.5's on 07-10), and agents hopped in and out of #focus from 08-05. An agent alone in a room has *no* logged input from other agents, so every #general-novel item it uses there is outside the logged cone. Leverage: a ground-truth "no logged channel" condition, plus the largest cadence spread for the cadence-vs-volume test.

## Model
**From:** `physics-models/02-nonequilibrium-ising` (asynchronous kinetic updates at call starts; H08's two-variable variant) and `physics-models/03-contagion` (adoption on a temporal network, with a field ε).

**H41 variant: contagion on the temporal read-out graph.** Each agent i updates only at its own model calls c, at times t_call(c) set by the scaffold. A call reads the chat messages posted in i's room since the previous receiving call (the DQ1 ledger) and nothing else that is logged. An item posted by source s at t0 can therefore influence i only through a **time-respecting read-out path**: s → j₁ → … → i, where each step is a read of a message posted *after* the sender itself entered the path. This defines a strict **logged light cone**: agent i enters it at its **entry call** K_i, the first call that reads a message from an agent already inside (the source is inside from t0).

- Cone entry: T_s = t0; T_i = min{ t_call(c) : c ∈ calls(i), c reads m, sender(m) = j, t_m ≥ T_j }.
- **Lieb–Robinson analogue.** With a strict cone the "commutator" is exactly zero outside (ξ → 0): no logged influence before K_i. The hop count H along the earliest path is at most the number of read-out events on it, so the front moves at most one hop per receiving call. In a synchronous (parallel-update) idealization this is "k hops need ≥ k recipient cycles"; with the village's asynchronous call phases a recipient can be k hops away and still be reached in fewer of *its own* cycles, so the recipient-cycle bound is approximate and its violation rate under pure relay is calibrated by simulation on the real call schedules.
- **Adoption.** At a talk call c of i, the item is used (first use) with hazard λ_i(c) = ε(t_c) + η_i(c) + q · 1[c ≥ K_i^item], where K_i^item is the first call that read an item-carrying message, ε is a shared field (pretraining, goal text, a common external stimulus), and η is an *unlogged channel* (shared artifacts, the web, memory, the history-search tool, a human outside the room). The light cone predicts: before entry, λ = ε + η; from the entry call on, λ jumps by q.
- **What the bound buys.** Adoptions outside the logged cone (acausal adoptions) measure ε + η directly. Classifying them by the channel that could carry the item (artifact, web, private stream, human, template, search) separates η from ε.
- **Velocity.** The adoption front moves at v = 1 / (cycles from first item exposure to use) hops per cycle, ≤ 1 by construction of the cone. Read-out gating predicts that the wall-clock time per hop scales with the recipient's call interval τ_c (cadence) and not with room message volume V: log Δt_hop = a + b log τ_c + c log V with b ≈ 1, c ≈ 0. A rate-driven (volume) contagion predicts b ≈ 0, c < 0.

**Rivals:**
- (R1) **shared field / common stimulus**: adoption times follow a common drive (pulse at the item's appearance), not exposure; predicts no hazard jump at the entry call (J ≈ 1) and many acausal adoptions;
- (R2) **room coarse-graining**: exposure is instantaneous for everyone in the source's room at t0 (wall-clock room membership, no cycles); predicts that a call already running at t0 (in flight) adopts as readily as the next call;
- (R3) **unlogged side channel**: hidden edges (artifacts, web) carry items across the cut; predicts acausal adoptions concentrated in cross-room agents and explained by artifact/web touches;
- (R4) **volume-driven spread**: arrival time ∝ 1 / room message rate.

## Operational definitions (written 2026-10-04 ~06:00 UTC, before any real-data run)
- **Item** (H34 marker rule, imported read-only): a hashed marker of class U (artifact: repo/site/file from `artifact_mentions`, chat, url or bare), D (number with ≥ 3 significant digits), N (name / identifier / hashtag / short quote) or W (rare word). An item is **novel in period g** if its first use in the non-holdout chat corpus falls in g. Eligible periods: H34's rule (non-holdout #5–#51 with ≥ 10,000 earlier non-holdout chat messages; #51 without its held-out tail), and ≥ 20 adoptions.
- **Source:** the speaker of the item's first-use message m0 (agent, human, automated, or the Claude Code agent); **t0** = time of m0; **room0** = its room.
- **Adoption:** a roster agent's first use of the item in g in a message with t > t0. The Claude Code agent is excluded as an adopter (it is not in `call_windows`) and treated as an external injector, like humans. **Using call** c_use: the talk call whose `t_first` is within 2 s of the message (nearest, same agent).
- **Calls and cycles:** an agent's *receiving* calls are its `call_windows` rows with `ctx_mode ≠ summary`. **Cycles to adoption** n = number of the adopter's receiving calls with t0 < t_call ≤ t_call(c_use). n = 0 means the using call was already running at t0 (in flight). Bound versions: n_hi counts calls with t_call_hi > t0 (lenient), n_lo calls with t_call_lo > t0.
- **Interaction (read-out, ledger):** a directed edge j → i at call c of i whenever c read a message of j (`context_ledger_items`). Humans and the automated speaker are pseudo-nodes that never read.
- **Static hop distance h (pre-item read-out graph):** G_W(t0) holds the edges read at calls with active time in [t0 − W, t0); W = 4 active hours (primary), 24 active hours (secondary). Seeds at distance 1: agents in room0 at t0 (`rooms_timeline`; the source's broadcast) plus the source's out-neighbours in G_W. h = 1 + breadth-first distance from the seed set; h = ∞ if unreachable.
- **Logged light cone (time-respecting):** entry calls K_i from the read events of the period as in the Model section, run from t0 to the latest adoption of the source's items (and at least 2 h). Hop count H_i along the earliest path. Two timing versions:
  - *best estimate:* the ledger's assignment of each (message, reader) pair to a call;
  - *lenient:* a pair flagged `uncertain` may instead be read at the reader's previous receiving call when t_m < t_call_hi of that call; entry is then at that call.
- **Acausal adoption:** index(c_use) < K_adopter (best estimate). **Robustly acausal:** also under the lenient version. A Claude Code, human or automated use is never a relay of the cone.
- **Item exposure:** the adopter read an item-carrying message (any speaker) at a call ≤ c_use. **Parent:** sender of the latest such message; **generation** g = g(parent) + 1, with the source (and humans, automated, Claude Code) at 0. **Cycles per hop** = adopter receiving calls from its first item-exposure call to c_use inclusive (≥ 1); also in talk calls and wall seconds (from the first exposing message to the use).
- **Room cone (coarse-graining R2):** the adopter is in the room cone if it was in room0 at any time in [t0, t_use], or a room-mover was in room0 after t0 and then in the adopter's room while the adopter was there, before t_use (h_room = 1, 2 or ∞). No cycles: room exposure is instantaneous.
- **Cone-boundary hazard:** for each (source message, at-risk agent) pair, the agent's talk calls whose message is posted in (t0, t0 + 2 h] and before the day's window ends, grouped as *pre-entry* (call index < K_i: the in-flight call in one room; every call before entry for agents in other rooms) and *post-entry offsets* o = 1, 2, 3 (the 1st, 2nd, 3rd talk call with index ≥ K_i). Hazard h(·) = adoptions at that call / at-risk calls (agent has not adopted yet). **Jump ratio J = h(o = 1) / h(pre)**. At-risk agents: roster agents (not the source, not Claude Code) with a receiving call after t0 on that PT day.
- **Templated:** the adopter's message is flagged `templated` (either embedding model) in `statement_flags`.
- **Violation channels** (checked in this order; the first match labels the violation; all matches are also recorded):
  1. *timing*: in the cone under the lenient version;
  2. *templated* adopter message;
  3. *human / operator injection*: a human, automated or Claude Code message containing the item before c_use (visible to the adopter: "logged injection"; in another room: "human cross-post");
  4. *common stimulus*: the source message and the adopter's message reply to the same parent message (`reply_pairs`, `parent` = true);
  5. *shared artifact*: the adopter touched (action or intention mention in `artifact_mentions`, `how` ∈ {url, output, bare, cwd}) in [t0 − 6 h, t_use) a repo or file that is the item itself (class U) or that the source mentioned in m0 or in actions/intentions in [t0 − 2 h, t0];
  6. *web / link*: the same with a site or domain;
  7. *private stream (memory / own work)*: the item's marker occurs in the adopter's own `intentions_text` (session goals, `nextSessionGoal`) or `artifact_commands_text` commands before c_use (text read in memory, non-holdout only, hashed with the same rule);
  8. *history search*: the adopter made a `search` call between t0 and c_use;
  9. *room move*: the adopter changed room between t0 and c_use;
  10. otherwise *unexplained*.

## Data scheme (`scheme/`)
- **Inputs:** shared tables listed above; holdout days are removed with `common.holdout_mask` and `calendar.holdout` before any text is read or any statistic computed.
- **Transform:**
  - `scheme/build.py markers`: re-runs H34's marker rule (imported, read-only) on non-holdout chat → `markers/uses.parquet` (message_id, marker hash, class), `markers/first_seen.parquet`.
  - `scheme/build.py periods`: per eligible period, the read events (ledger items × `call_windows` × `chat_core`), items, adoptions with n, h (W = 4 h, 24 h), h_room, cone entry (best, lenient), item exposure, generation, cycles per hop, cadence and volume covariates, the cone-boundary hazard table and the violation channels.
- **Output:** `data/processed/H41-readout-light-cone/` with `markers/`, `G<NN>/{items,adoptions,hazard,violations}.parquet`, `synthetic/`, `results/`, `_provenance.json`. Budget ≤ 200 MB; no text stored.
- **Regimes covered:** I (#5–#31), II (#33, #35, #36a), III (#36b–#51); every period is analysed within itself (unit of analysis); periods are compared through their fitted parameters.

## Observables
*Written 2026-10-04 ~06:00 UTC.*
- **O1, violation shares** per period: acausal share A (best estimate) and A_rob (lenient), among all adoptions and among *early* adoptions (use within 15 min of t0, where the cone binds); the static "cycles ≥ hops" violation share V = P(n < h) (W = 4 h; also 24 h, H and h_room), with its parts (h = 1 & n = 0; 2 ≤ h < ∞ & n < h; h = ∞).
- **O2, cone-boundary jump:** h(pre), h(1), h(2), h(3) and J with a day-cluster bootstrap 95% CI (B = 500).
- **O3, front velocity:** median cycles per hop (all receiving calls; talk calls; wall seconds) for item-exposed adopters with an agent parent; v = 1 / median; the share of hop events at the first post-exposure talk call; front curves P(adopted within n cycles | generation).
- **O4, cadence vs volume:** within period, log Δt_hop = b log τ_c + c log V + α_agent (τ_c: the adopter's median receiving-call interval over the 60 min before the first exposing message, intervals > 30 min dropped; V: messages per hour in the adopter's room over the same 60 min); day-cluster bootstrap. Across periods: Spearman of median Δt_hop with median τ_c and with median V.
- **O5, violation channels:** counts and shares of robustly acausal adoptions per channel; the unexplained residue; the same for in-cone adoptions that were never item-exposed (paraphrase relay or field).
- **O6, rooms vs interaction graph:** A and V under the room cone vs the logged cone; h(in-flight, room-exposed) vs h(o = 1).
- **Native observables:** see "Native tests" below.

## Null / baseline
*Written 2026-10-04 ~06:00 UTC, before any real-data run.*
- **N1, shared-field null (synthetic; strongest):** on the real call schedules and read graphs, items are seeded at real messages and adopted at real talk calls with a hazard that ignores exposure: a common pulse starting just before t0 (onset U(0, 5) min before t0, decay τ = 10 min) plus a weak constant field. Gives A, V and J for a pure field (expected J ≈ 1, A large for early adoptions).
- **N2, time-shuffled null (real data):** each adopter's using call is redrawn uniformly among its own talk calls within ±30 active min of the observed one (no conditioning on t0). Gives A_jit and V_jit: the violation shares expected if adoption were not locked to exposure at the call scale. 200 redraws.
- **N3, room-only coarse-graining (R2):** the room cone (instantaneous exposure by room membership) in place of the logged cone; compared on A, V and on whether the hazard jump sits at t0 (room) or at the entry call (cone).
- **N4, pure relay floor (synthetic):** one-hop-per-call relay on the same schedules, with "true" call starts drawn inside [t_call_lo, t_call_hi]: the violation shares that timing uncertainty alone manufactures.

## Synthetic validation plan (axis F; run before real data)
`analysis/synthetic.py` on three real skeletons: non-holdout #38 (two rooms, regime III), #31 (one room, regime I) and a #51 segment (07-06 → 07-23, isolation rooms included). Real call schedules (`call_windows`), real read events (`context_ledger_items`), real messages; ≈ 600 synthetic items per replicate seeded at random real agent messages; adoption only at real talk calls (the adopter's real message "carries" the item; carriers relay it through the real read graph). Truths:
- **T1 relay:** λ = q per talk call from the item-exposure call on (q ∈ {0.05, 0.15}), with a small constant field ε₀ = 0.001.
- **T2 shared field:** N1 above, no relay.
- **T3 hidden channel:** T1 plus hidden edges: in two-room skeletons each item reaches the other room's agents at a hidden time t0 + Exp(30 min) (an "artifact leak"); in the #51 skeleton isolated agents receive it the same way; in #31 two fixed agent pairs share a hidden instant channel.
- **T4 timing:** T1 with the generative call starts drawn uniformly in [t_call_lo, t_call_hi] and visibility recomputed; the analysis uses the ledger's best estimates.
**Pass criteria (fixed now):** (i) under T1 and T4, A_rob ≤ 0.01 and A (best) ≤ 0.03; (ii) under T2, J's CI includes 1 or lies below it in ≥ 80% of replicates, and A(early) ≥ 3× its T1 value; (iii) under T1, J lower CI > 1 in ≥ 80% of replicates; (iv) under T3, ≥ 70% of hidden-channel adoptions that precede their logged entry are flagged acausal, and ≤ 5% of non-hidden adoptions are; (v) the time-shuffled null gives A_jit > A_obs under T1 in ≥ 90% of replicates. A failed criterion makes the matching statistic uninterpretable on real data.
- *Clarification S0 (2026-10-04 ~06:03 UTC, before the synthetic run):* criterion (i) is evaluated on **relay-caused** adoptions (the planted ε₀ field produces genuine out-of-cone adoptions, which the test should flag, not count against it); the total A is reported alongside. In (iv), "logged entry" is the true cone entry of the generative process.

## Synthetic validation (axis F; run 2026-10-04 06:05–06:13 UTC, before any real-data light-cone statistic)
`analysis/synthetic.py` → `data/processed/H41-readout-light-cone/synthetic/{runs.parquet, summary.json}`. Skeletons: all non-holdout #38 days (two rooms), #31 (one room, regime I) and #51 07-06 → 07-23 (one big room plus onboarding / isolation rooms). 400 items per replicate, 4 replicates per truth, 60 runs. Synthetic uses go through the same `scheme/build.py: analyze` as the real data. J_in = h(first post-entry talk call)/h(in-flight talk call), both for agents in the source's room (defined in A1 below).

| Skeleton · truth | adoptions | A (best) | A early | A among source-lineage relay adoptions (max over reps) | J (all pre-entry) median, lower CI > 1 | J_in median, lower CI > 1 | cycles / talk calls per hop |
| --- | --- | --- | --- | --- | --- | --- | --- |
| #31 · T1 relay q 0.05 / 0.15 | 2381 / 3296 | 0.000 | 0.000 | 0.000 | 16 / 55, 4/4 | 16 / 55, 4/4 | 99 / 47 · 8 / 4 |
| #31 · T2 field | 652 | 0.021 | 0.029 | — | 0.6, 0/4 | 0.64, 0/4 | 19 · 2 |
| #31 · T3 hidden pairs | 3294 | 0.001 | 0.002 | 0.000 | 8.6, 4/4 | 8.6, 4/4 | 47 · 4 |
| #31 · T4 timing | 3308 | 0.001 | 0.002 | 0.001 (lenient 0) | 8.4, 4/4 | 8.4, 4/4 | 47 · 4 |
| #38 · T1 relay q 0.05 / 0.15 | 629 / 1090 | 0.088 / 0.068 | 0.024 / 0.023 | 0.000 | 25 / 67, 4/4 | 3.6 / 11, 3/4 / 4/4 | 105 / 64 · 5.5 / 3 |
| #38 · T2 field | 316 | 0.558 | 0.544 | — | **4.2, 4/4** | 0.37, 0/4 | 18 · 2 |
| #38 · T3 hidden (other room, t0 + Exp(30 min)) | 2122 | 0.524 | 0.247 | 0.000 | 1.7, 4/4 | 10.6, 4/4 | 64 · 3 |
| #38 · T4 timing | 1098 | 0.072 | 0.019 | 0.002 (lenient 0) | 55, 4/4 | 2.9, 4/4 | 68 · 3 |
| #51 · T1 relay q 0.05 / 0.15 | 3700 / 5564 | 0.000 | 0.000 | 0.000 | 17 / 56, 4/4 | 7.6 / 22, 3/4 / 4/4 | 134 / 76 · 7 / 3.5 |
| #51 · T2 field | 692 | 0.015 | 0.023 | — | 0.6, 0/4 | 0.64, 0/4 | 22 · 3 |
| #51 · T3 hidden (isolated agents) | 5586 | 0.002 | 0.000 | 0.000 | 10, 4/4 | 25, 4/4 | 74 · 3 |
| #51 · T4 timing | 5620 | 0.001 | 0.004 | 0.002 (lenient 0) | 5.1, 4/4 | 2.7, 4/4 | 75 · 3.75 |

**What the synthetic run showed:**
1. **Timing uncertainty does not manufacture violations.** Adoptions caused by logged relay from the source are never flagged under the ledger's timing (0/~18,000); with generative call starts drawn inside [t_call_lo, t_call_hi] (T4) at most 0.2% are flagged at best estimate and 0 under the lenient version. Criterion (i) passes.
2. **But timing error attenuates the jump.** Under T4, J_in falls 3–8× (#31: 55 → 8.4; #51: 22 → 2.7) because true post-entry adoptions are shifted into the in-flight bin. Real J_in is a lower bound on the true jump.
3. **J over all pre-entry calls is confounded in two-room periods.** A pure field gives J = 4.2 with lower CI > 1 in 4/4 #38 replicates, because other-room agents' pre-entry calls come later, when the pulse has decayed. The in-room version J_in is not fooled (0.37–0.64, CI includes 1 in 12/12 field runs) and detects relay in 22/24 relay runs (3/4 at q = 0.05 in #38 and #51 with only 400 items; real periods have 10–100× more items). Criteria (ii) and (iii) pass for J_in, fail for J.
4. **The acausal share separates relay from a field only where the logged path is long.** In #38 a field gives A = 0.56 against 0.07–0.09 for relay. In one room the logged cone reaches everyone within one call, so even a pure field gives A = 0.015–0.02. In two rooms, a tiny per-talk-call field (ε₀ = 0.001) seeding other-room cascades already gives A ≈ 0.07–0.09 under relay.
5. **Hidden channels are flagged where they can be.** Every hidden-channel adoption that preceded logged entry was flagged acausal (#38: 331 per replicate; #51: 16), and their relay descendants are correctly outside the source's cone (99%). In one room (#31 pairs) a side channel produced only ≈ 2 detectable adoptions per 3,300: the cone is one call wide, so side channels show only as in-flight adoptions. Criterion (iv) passes where testable.
6. **The time-shuffled null is not specific.** The observed A is below A_jit in 100% of runs under relay **and** under the field, because a field pulse locked to t0 is as time-locked as exposure. Criterion (v) passes trivially; the null cannot separate relay from a t0-locked field.
7. **Velocity.** Relay (q = 0.15) gives 46–76 receiving calls and 3–4 talk calls per hop; a field pulse gives a *faster* apparent front (18–22 calls, 2–3 talk calls).

## Amendments (2026-10-04 ~06:15 UTC, after the synthetic validation, before any real-data light-cone statistic)
- **A1 · Primary jump statistic = J_in.** h(o = 1) and h(pre) are restricted to agents in the source's room at t0 (the in-flight talk call vs the first post-entry talk call). P1 and P8 are scored on J_in; J over all pre-entry calls is reported only. Powered = ≥ 100 in-room pre-entry at-risk calls and ≥ 20 in-room adoptions at o = 1.
- **A2 · J_in is attenuated by timing error** (synthetic T4: 3–8×); its size is read as a lower bound, its sign as the test.
- **A3 · P3 is reported but leaves the verdict rule:** the time-shuffled null is beaten by a t0-locked field too.
- **A4 · Verdict rule (replaces the one above):**
  - **supported:** J_in lower CI > 1 **and** the robust acausal share among *within-room* adoptions (adopter in the source's room at t0) within P2's bound for its regime;
  - **failed:** J_in powered and its CI includes 1 or lies below it;
  - **mixed:** J_in passes but the within-room A_rob exceeds the bound;
  - **n/a:** J_in not powered (A, V and velocity reported descriptively).
  Cross-room acausal adoptions are the probe of unlogged channels, not a failure of the cone; P2 is still scored as written, with the synthetic calibration (two-room relay + ε₀ = 0.001 gives A ≈ 0.07–0.09) quoted next to it.
- **A5 · Criterion (iv)'s false-positive clause** is evaluated on source-lineage relay adoptions (0 flagged); descendants of field or hidden adopters are correctly outside the source's cone. Side channels inside one broadcast room are undetectable by the cone except as in-flight adoptions.

- **A6 · POST HOC (written ~06:43 UTC; the estimator was introduced ~06:25 UTC, right after the first real-data period, G40, had been computed; not pre-registered).** G40 gave J_in = 0.59 because the adoption hazard falls steeply with the delay since t0 (o = 1 hazard 4.5% for talk calls within 30 s of t0, 0.25% after 15 min), while in-flight calls all sit at short delays. This is H29's recency confound (`infra/README.md`, Known issues: compare within matched age bins), which the card should have anticipated. Added estimator: **J_mh**, the Mantel–Haenszel ratio of the o = 1 and in-flight hazards within delay-since-t0 bins (< 30 s, 30–60 s, 1–2, 2–5, 5–15, > 15 min), in-room agents only, day-bootstrap CI. Validated on a second synthetic run (`synthetic/runs_v2.parquet`, 72 runs, adding a relay whose hazard decays with time since exposure, T1d): J_mh is infinite (no in-flight adoptions) with lower CI > 1 in 40/40 relay runs, 0.83–1.19 under the shared field with lower CI > 1 in 1/12 field runs (8% false positives), and 6.7–23 under timing error (lower CI > 1 in 9/12). Disclosure: J_mh for the first 31 periods was computed (~06:33 UTC) before this validation run finished (~06:55 UTC). Both J_in (pre-registered) and J_mh (post hoc) are reported everywhere; verdicts by the pre-registered rule A4 stay primary, and a post-hoc verdict column uses J_mh in place of J_in. Also post hoc: hazards by item class and under the lenient cone.

## Prediction (round 1)
*Written 2026-10-04 ~06:00 UTC, before running the analysis on real data.* **Looked at beforehand:** schemas; the ledger documentation and validation; that agent chat messages map to talk calls (t = `t_first`, 99–100%); median call intervals (11–17 s for receiving calls in #20–#51); the share of chat-mode calls in regime I/II; `rooms_timeline` for #35–#51 (who sat in which room when); H34's per-period tree counts and HR₁₀; H08's C9 result. **No** item, adoption, cone, hop or hazard statistic had been computed.

"Powered" = ≥ 100 at-risk pre-entry talk calls and ≥ 20 adoptions at o = 1.

| # | Prediction | Counts against |
| --- | --- | --- |
| P1 | **Hazard jumps at the cone boundary (gating; beats R1, R2).** J = h(1)/h(pre) > 1 with the day-bootstrap lower CI > 1 in ≥ 70% of powered regime-II/III periods and ≥ 50% of powered regime-I periods (H08's regime-I call-rule caveat) | J ≤ 1 or CI includes 1 in > 30% of powered II/III periods: adoption is not gated by read-out (field or room-level exposure) |
| P2 | **Few acausal adoptions.** A_rob ≤ 0.05 of adoptions in every regime-II/III period and ≤ 0.10 in regime I; A (best) ≤ 0.08 / 0.15 | A_rob > 0.10 in most periods: a large unlogged channel or a broken visibility rule |
| P3 | **Beats the time-shuffled null.** A_obs < A_jit (upper CI of A_obs below the null mean) among early adoptions in ≥ 80% of periods | A_obs ≈ A_jit: adoption timing is unrelated to the cone at the call scale |
| P4 | **Static cycles ≥ hops.** In one-room periods V ≈ A (h = 1 for almost all adopters). In two-room periods ≥ 90% of cross-room adopters have h = ∞ on the pre-item graph (W = 4 h), so V exceeds A by about the cross-room adoption share | cross-room adopters mostly reachable on the pre-item graph (rooms are not cuts of the read-out graph) |
| P5 | **Front velocity is set by talk turns.** Median cycles per hop: ≤ 5 receiving calls in regime I, ≥ 10 in regime III (talk is rare per call there); in talk-call units the median is 1–2 in every regime (the item is used at the first or second talk call after exposure) | regime-III median cycles per hop < 5, or talk-call median ≥ 3 in most periods |
| P6 | **Cadence, not volume (R4).** Within period, b > 0 with CI excluding 0 in ≥ 1/2 of powered periods (≥ 200 hop events), b ∈ [0.5, 1.5] in most, and c > −0.2 (more room traffic does not speed arrivals); b > \|c\| in ≥ 2/3. Across periods, ρ(median Δt_hop, median τ_c) > ρ(median Δt_hop, 1/median V) | c < −0.5 with b ≈ 0 in most powered periods (volume-driven spread) |
| P7 | **Channels.** ≥ 50% of robustly acausal adoptions have at least one identified channel; in two-room periods the shared-artifact + web channels are the largest identified class for cross-room violations; the unexplained residue ≤ 50% | residue > 70% in most periods: violations are mostly unidentified (a field or invisible web reading) |
| P8 | **Interaction cone beats rooms.** The in-flight talk call (room-exposed, not yet read) has hazard ≤ 1/3 of the entry-call hazard (the room coarse-graining's instantaneous exposure is wrong at the call scale) in ≥ 2/3 of powered regime-II/III periods | in-flight hazard ≈ entry hazard: room membership, not read-out, sets exposure |

**Prior credences (Claude, 2026-10-04):** P1 0.6, P2 0.5, P3 0.6, P4 0.7, P5 0.45, P6 0.4, P7 0.35, P8 0.55.

**Per-period verdict rule (replication; written in each G card before its run):**
- **supported:** J lower CI > 1 (P1) **and** A_obs below the time-shuffled null (P3) **and** A_rob within P2's bound for its regime;
- **failed:** J's CI includes 1 (or J < 1) **and** A_obs not below the null;
- **mixed:** otherwise;
- **n/a:** < 20 adoptions or not powered for J (then P2/P3 are reported descriptively).

### Native tests (predictions written 2026-10-04 ~06:00 UTC, before any real-data run)
- **G38 (two-room cage).** Cross-room adoption = the adopter was in the other room at t0.
  - G38-a: ≥ 80% of cross-room adoptions are outside the logged cone at use (the room cut is a cut of the read-out graph; room-movers and humans bridge little).
  - G38-b: the cross-room adoption hazard per at-risk talk call within 2 h is ≤ 1/5 of the within-room hazard.
  - G38-c: among robustly acausal cross-room adoptions, shared artifact + web explain ≥ 30% (HH157's artifact leak), more than in within-room acausal adoptions.
  - G38-d: median wall time to cross-room adoption ≥ 3× the within-room median.
  - Verdict: supported if a, b and c hold; failed if a fails (cross-room spread mostly through logged paths would mean rooms are not cages) or b fails; mixed otherwise. Prior 0.4.
- **NE42 (merge / split, #39 → #40 → #41).** Groups = room in #39 (#best or #rest); in #41 the same partition (GPT-5 stayed in #rest throughout).
  - NE42-a: the cross-group adoption hazard per at-risk talk call (2 h horizon) in #40 is ≥ 3× its value in both #39 and #41.
  - NE42-b: cross-group acausal share ≥ 70% in #39 and #41, and in #40 within 0.05 of the within-group acausal share.
  - NE42-c: within-group cycles per hop change by < 30% across the three periods (the merge changes distance, not cadence).
  - Goal confound: #40 has a shared cross-world objective. Verdict: supported if a and b hold; failed if a fails; mixed otherwise. Prior 0.55.
- **G31 (regime-I clock).**
  - G31-a: J > 1 (lower CI > 1), but smaller than the regime-III median J (in-flight chat calls may be unlogged; H08).
  - G31-b: median cycles per hop ≤ 5 receiving calls; ≤ 2 chat-mode calls.
  - G31-c: clock test. Across adopters with ≥ 5 hop events, the between-agent SD of log median hop delay is smaller in receiving calls than in wall seconds (calls are the clock).
  - Verdict: supported if a and c hold; failed if c fails and J's CI includes 1; mixed otherwise. Prior 0.45.
- **G51 (isolation and hopping rooms).**
  - G51-a: every adoption of a #general-novel item by an agent alone in an onboarding / isolation room (while isolated) is acausal (by construction of the logged cone) and ≥ 50% of them have an identified channel (artifact, web, private stream, search, human).
  - G51-b: #focus hoppers bridge: cross-room (#general ↔ #focus) adoptions are mostly inside the logged cone (≥ 70%), unlike G38's, because membership changes on minute scales.
  - G51-c: the cadence test is powered here: b ∈ [0.5, 1.5] with CI excluding 0 and c > −0.2.
  - Verdict: supported if b and c hold and a's channel share ≥ 50% (or a has < 5 events: then on b and c); failed if c fails with b ≈ 0; mixed otherwise. Prior 0.35.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness". Round 1, exploratory, non-holdout.
**Rival models:** shared field / common stimulus (R1), room coarse-graining (R2), unlogged side channel (R3), volume-driven spread (R4).
**Locked holdout used for confirmation:** none yet. `analysis/confirm.py` (T1 #51 tail, T2 #47, T3 #28, T4 the #46–#50 onboarding rooms) is written and dry-run on stand-ins only.

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Items, sources, adoptions, the logged cone (entry calls), static hops and hazards all come from the DQ1 ledger, `call_windows`, `chat_core` and `rooms_timeline`, with every rule written before the run. **Not invariant:** a call means different things in regime I (scheduled chat calls) and III (chained computer use), so cycles per hop differ 3×; visibility is the ledger's room rule with estimated starts for non-Gemini agents; agents with no room record count as unknown. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | **Update order audited:** asynchronous call phases, timing bounds (lenient cone) and the 200-event cap. **Violated:** a constant per-call hazard (adoption hazard falls 10–20× with time since t0: the recency confound behind the failed J_in); the one-unit clock (G31's clock test inconclusive). |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | The in-flight call is the field/room null at the call scale. Pre-registered J_in beats it in 12/32 periods; post-hoc delay-matched J_mh in 22/32 (synthetic false-positive rate under a field 1/12). The time-shuffled null is beaten everywhere but is non-specific. No day-blocked held-out prediction. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | **Signature (strict cone):** within-room robust acausal share ≤ 4%, median 0.6%; NE42's cross-group acausal 1.00 / 0.02 / 1.00. **Static hops:** cross-room adopters unreachable on the pre-item graph in 5/8 two-room periods (in #35/#36 statically bridged, yet 78–83% outside the time-respecting cone). **Failed:** regime-I cycles per hop (predicted ≤ 5, observed 47), cadence scaling (b > 0 in 3/25). |
| E interventional | predicts the change across a natural experiment | 1 | NE42 (merge and split): predicted ≥ 3× cross-group hazard in #40 vs both #39 and #41; observed 82× [21, 223] and 863× [186, 2365], and the cross-group acausal share collapsed and returned. Confounded with #40's shared goal; one NE; the size of the effect follows almost mechanically from room visibility. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Two synthetic runs on real call schedules (#31, #38, #51; 132 runs): relay never flagged acausal (0/~18,000; ≤ 0.2% with timing error, 0 lenient); J_in and J_mh separate relay from a field; hidden channels flagged wherever logged paths are long. **Not identifiable:** side channels inside one room; the channel attribution (no ground truth, non-specific against controls). J_mh was chosen after the first real period. |
| G ground truth | agrees with known structure | 1 | The room cut is known structure: #38's cross-room hazard is 0.001× within-room, and NE42 reproduces the merge and the split. The isolation-room ground truth (#51) produced one usable adoption. No independent record of what agents actually read beyond the ledger's own validation. |
| H comparative | beats the named rivals | 1 | **R2 (rooms, instantaneous exposure):** beaten at matched delay in 22/32 periods (the call already running does not adopt like the next call), not by the pre-registered J_in. **R1 (field):** a third of fast adoptions behave like it (numbers especially). **R4 (volume):** not supported (c < 0 with CI in 7/25), but neither is cadence. **R3 (side channel):** cross-room leaks exist but are not attributable. |
| I transfer | holds in other same-mode periods, including the holdout | 1 | The within-room bound holds in 32/32 periods across all regimes; J_mh is significant in 15/21 regime-I, 2/3 regime-II and 5/8 regime-III periods; the cage holds in 7/8 two-room periods. Not run on the holdout; the dry run fails C1 on the #51 stand-in segment (08-24 → 09-05). |

## Results by goal period
Verdicts: pre-registered rule A4 (J_in) first, post-hoc rule (J_mh) in brackets. One folder per period in [`goalperiod-subhypotheses/`](goalperiod-subhypotheses/); native tests have their own verdicts (G31, G38, G51, NE42).

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | failed (post hoc supported) | regime I; 212 adoptions; J_in 0.83 [0.50, 1.61]; J_mh 2.20 [1.24, 5.41]; A_rob 0.009 (within-room 0.009, cross-room –); cycles/talk calls per hop 24/4.0 |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | supported (post hoc supported) | regime I; 165 adoptions; J_in 3.98 [1.83, 6.80]; J_mh ∞ [–, –]; A_rob 0.000 (within-room 0.000, cross-room –); cycles/talk calls per hop 108/13.0 |
| [G07](goalperiod-subhypotheses/G07/README.md) | replication | n/a (post hoc n/a) | regime I; 25 adoptions; J_in 0.97 [0.62, 1.32]; J_mh 1.96 [1.94, 2.00]; A_rob 0.040 (within-room 0.040, cross-room –); cycles/talk calls per hop 9/1.0 |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | n/a (post hoc n/a) | regime I; 236 adoptions; J_in 0.36 [0.14, 1.33]; J_mh 1.32 [0.00, 3.65]; A_rob 0.000 (within-room 0.000, cross-room –); cycles/talk calls per hop 386/39.0 |
| [G10](goalperiod-subhypotheses/G10/README.md) | replication | supported (post hoc supported) | regime I; 65 adoptions; J_in 4.60 [2.51, 6.41]; J_mh ∞ [–, –]; A_rob 0.000 (within-room 0.000, cross-room –); cycles/talk calls per hop 70/8.0 |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | failed (post hoc supported) | regime I; 147 adoptions; J_in 2.03 [0.69, 2.96]; J_mh 4.17 [3.12, 6.01]; A_rob 0.014 (within-room 0.014, cross-room –); cycles/talk calls per hop 9/2.0 |
| [G12](goalperiod-subhypotheses/G12/README.md) | replication | failed (post hoc supported) | regime I; 400 adoptions; J_in 1.39 [0.92, 2.17]; J_mh 2.01 [1.30, 3.04]; A_rob 0.007 (within-room 0.007, cross-room –); cycles/talk calls per hop 6/3.0 |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | failed (post hoc supported) | regime I; 227 adoptions; J_in 1.04 [0.65, 3.81]; J_mh 2.60 [1.51, 7.78]; A_rob 0.009 (within-room 0.009, cross-room –); cycles/talk calls per hop 47/8.0 |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | failed (post hoc failed) | regime I; 112 adoptions; J_in 0.38 [0.26, 1.35]; J_mh 1.30 [0.28, 3.02]; A_rob 0.018 (within-room 0.018, cross-room –); cycles/talk calls per hop 41/6.0 |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | failed (post hoc failed) | regime I; 125 adoptions; J_in 0.83 [0.18, 6.36]; J_mh 3.20 [0.48, 7.05]; A_rob 0.024 (within-room 0.024, cross-room –); cycles/talk calls per hop 50/11.0 |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | supported (post hoc supported); **1b:** failed (borderline bootstrap: J_in lower CI 0.98) | regime I; 1632 adoptions; J_in 2.04 [1.01, 4.79]; J_mh 2.34 [1.42, 4.73]; A_rob 0.006 (within-room 0.006, cross-room –); cycles/talk calls per hop 70/9.0 |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | supported (post hoc supported) | regime I; 889 adoptions; J_in 1.98 [1.21, 3.89]; J_mh 3.07 [1.71, 7.61]; A_rob 0.007 (within-room 0.007, cross-room –); cycles/talk calls per hop 40/4.0 |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | supported (post hoc supported) | regime I; 1307 adoptions; J_in 2.38 [1.52, 7.50]; J_mh 3.90 [1.81, 22.85]; A_rob 0.004 (within-room 0.004, cross-room –); cycles/talk calls per hop 46/5.0 |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | supported (post hoc supported) | regime I; 549 adoptions; J_in 2.20 [1.27, 12.95]; J_mh 4.52 [1.97, 9.03]; A_rob 0.000 (within-room 0.000, cross-room –); cycles/talk calls per hop 48/5.0 |
| [G23](goalperiod-subhypotheses/G23/README.md) | replication | failed (post hoc failed) | regime I; 276 adoptions; J_in 1.08 [0.21, 6.23]; J_mh 4.70 [0.96, 6.28]; A_rob 0.000 (within-room 0.000, cross-room –); cycles/talk calls per hop 138/8.0 |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | failed (post hoc failed) | regime I; 495 adoptions; J_in 0.93 [0.16, 3.78]; J_mh 3.55 [0.77, 16.29]; A_rob 0.006 (within-room 0.006, cross-room –); cycles/talk calls per hop 47/3.0 |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | failed (post hoc supported) | regime I; 826 adoptions; J_in 1.13 [0.62, 5.11]; J_mh 2.39 [1.33, 8.02]; A_rob 0.007 (within-room 0.007, cross-room –); cycles/talk calls per hop 62/5.0 |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | failed (post hoc supported) | regime I; 818 adoptions; J_in 2.65 [0.97, 7.87]; J_mh 3.12 [1.28, 8.60]; A_rob 0.001 (within-room 0.001, cross-room –); cycles/talk calls per hop 29/3.0 |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | supported (post hoc failed) | regime I; 3723 adoptions; J_in 1.61 [1.04, 3.65]; J_mh 2.29 [0.98, 5.61]; A_rob 0.002 (within-room 0.002, cross-room –); cycles/talk calls per hop 293/16.0 |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | failed (post hoc supported) | regime I; 1184 adoptions; J_in 1.49 [0.98, 2.24]; J_mh 2.21 [1.21, 3.59]; A_rob 0.007 (within-room 0.007, cross-room –); cycles/talk calls per hop 52/4.0 |
| [G31](goalperiod-subhypotheses/G31/README.md) | native | mixed (post hoc supported) | regime I; 1493 adoptions; J_in 1.86 [1.19, 3.94]; J_mh 2.95 [1.50, 6.53]; A_rob 0.002 (within-room 0.002, cross-room –); cycles/talk calls per hop 43/4.0 |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | supported (post hoc supported); 1b unchanged | regime II; 1767 adoptions; J_in 1.88 [1.30, 3.29] (1b 1.87 [1.31, 2.75]); J_mh 3.03 [2.19, 5.48] (1b 2.93 [2.28, 4.07]); A_rob 0.008 (within-room 0.008, cross-room –); cycles/talk calls per hop 20/2.0 |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | failed (post hoc failed) | regime II; 1907 adoptions; J_in 1.60 [0.80, 3.16]; J_mh 2.55 [0.99, 6.52]; A_rob 0.199 (within-room 0.003, cross-room 0.78); cycles/talk calls per hop 53/3.0 |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | supported (post hoc supported) | regime II; 1386 adoptions; J_in 6.55 [2.75, 26.05]; J_mh 25.44 [6.70, 42.92]; A_rob 0.271 (within-room 0.000, cross-room 0.83); cycles/talk calls per hop 46/2.0 |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | n/a (post hoc n/a) | regime III; 238 adoptions; J_in 2.48 [2.21, 4.08]; J_mh 10.31 [8.86, 11.59]; A_rob 0.017 (within-room 0.004, cross-room 0.75); cycles/talk calls per hop 6/1.0 |
| [G38](goalperiod-subhypotheses/G38/README.md) | native | mixed (post hoc supported) | regime III; 2904 adoptions; J_in 1.03 [0.67, 1.81]; J_mh 2.59 [1.72, 4.51]; A_rob 0.023 (within-room 0.005, cross-room 1.00); cycles/talk calls per hop 12/1.0 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | failed (post hoc failed) | regime III; 317 adoptions; J_in 1.50 [0.38, 8.20]; J_mh 2.59 [0.66, 3.65]; A_rob 0.032 (within-room 0.010, cross-room 1.00); cycles/talk calls per hop 62/3.0 |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | failed (post hoc failed) | regime III; 1955 adoptions; J_in 0.59 [0.34, 1.17]; J_mh 1.31 [0.83, 2.65]; A_rob 0.014 (within-room 0.014, cross-room 0.00); cycles/talk calls per hop 19/1.0 |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | failed (post hoc supported) | regime III; 1984 adoptions; J_in 1.04 [0.85, 1.22]; J_mh 2.34 [1.92, 3.19]; A_rob 0.022 (within-room 0.016, cross-room 0.87); cycles/talk calls per hop 11/1.0 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | failed (post hoc supported) | regime III; 638 adoptions; J_in 1.54 [0.91, 10.31]; J_mh 7.75 [3.21, 8.34]; A_rob 0.053 (within-room 0.007, cross-room 0.83); cycles/talk calls per hop 26/2.0 |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | failed (post hoc failed); 1b unchanged | regime III; 660 adoptions; J_in 0.68 [0.37, 1.73] (1b 0.70 [0.36, 1.84]); J_mh 1.45 [0.83, 5.82] (1b 1.47 [0.83, 4.18]); A_rob 0.029 (within-room 0.028, cross-room 0.11); cycles/talk calls per hop 9/2.0 |
| [G51](goalperiod-subhypotheses/G51/README.md) | native | mixed (post hoc supported); **1b:** mixed, replication supported / supported | regime III; 16521 adoptions; **1b:** J_in 2.08 [1.49, 3.10]; J_mh 9.16 [6.55, 13.89]; A_rob 0.027 (within-room 0.002, cross-room 0.47); round 1 (stale rooms): J_in 40.70, J_mh 15.80, cross-room 0.05; cycles/talk calls per hop 27/3.0 |
| [NE42](goalperiod-subhypotheses/NE42/README.md) | native | supported | cross-group hazard #40/#39 ×82, #40/#41 ×863; cross-group acausal 1.00 / 0.02 / 1.00 |

## Results
`analysis/explore.py` → `data/processed/H41-readout-light-cone/results/{period_table.parquet, summary.json}`; `analysis/native.py` → `results/native.json`; figures in `figures/` (`summary_obs`, `summary_obs2`, `hazard_by_delay`) and in the native period folders.

**1. Inside a room, the logged light cone holds, but it is only one call wide.**
- **Scale:** 32 periods, 133,549 novel items, 45,183 adoptions.
- **Strict cone:** among adopters who were in the source's room at t0, the robust acausal share (adoption by a call that started before the agent could have read the item, under lenient timing) is 0–4% per period, median 0.6%.
- **What it does and does not show:** in a broadcast room everyone enters the cone at their first call after t0, so the only possible violation is the call already in flight. The synthetic field gave the same 1.5–3% in one room. The within-room bound is therefore necessary but weak; the gating test (2) is the discriminating one.

**2. Gating at the cone boundary is real but partial, and the pre-registered estimator was confounded.**
- **Pre-registered J_in** (hazard at the first post-entry talk call over the in-flight talk call): lower CI > 1 in 12/32 periods (regime I 8/19 powered, II 2/3, III 1/7). **P1 fails as written.**
- **Why:** the per-call adoption hazard falls steeply with time since t0 (`figures/hazard_by_delay.pdf`: #51 from 5% within 30 s to 0.1% after 15 min). In-flight calls all sit at short delays, while first post-entry calls are spread over hours. This is H29's recency confound; the card should have matched on age from the start.
- **Post hoc (A6), delay-matched J_mh:** lower CI > 1 in 22/32 periods; median 2.6 in regime I, 3.0 in II, 2.6 in III, and 15.8 in #51 (1b: 9.2 [6.5, 13.9]; the 15.8 used stale rooms). In the synthetic data J_mh is ≈ 1 under a shared field (1/12 false positives) and unbounded under relay.
- **Co-generation is large:** the median in-flight/entry hazard ratio 1/J_mh is 0.38. About a third of fast adoptions happen in calls that could not have read the item.
- **It depends on the item class:**
  - names and identifiers gate (J_mh,N lower CI > 1 in 24/29 estimable periods, median 3.0);
  - numbers are co-generated (median J_mh,D 0.88; ≤ 1 in 10/18), as when two agents read the same dashboard;
  - links (U) and rare words (W) are almost never used in flight (J_mh unbounded in 13/16 and 19/26 periods).

**3. Across rooms the logged cone is a cage, and the cage moves with the rooms (NE42).**
- **Cross-room adoptions are leaks:** the share outside the logged cone is 0.75–1.00 in #35–#39, #41 and #42, and 0.11 in #44. These adoptions are rare (2–33% of adoptions) and slow: in #38 the median delay is 71 h vs 5 min within a room.
- **The cut is nearly complete:** #38's cross-room adoption hazard per talk call is 0.001 [0.0003, 0.002] of the within-room hazard.
- **NE42:**
  - the cross-group hazard per talk call rose from 3.5×10⁻⁵ (#39) to 2.9×10⁻³ (#40, merged) and fell to ≈ 3×10⁻⁶ (#41);
  - in the merged week cross-group pickup was 1.4× the within-group rate;
  - the cross-group acausal share was 1.00 / 0.02 / 1.00.
- ~~**Hopping rooms bridge:** in #51, agents moved between #general and #focus on minute scales, and 97% of cross-room adoptions were inside the logged cone (hop counts along the earliest path: 1588 at one hop, 70 at two, 11 at three).~~ **1b (rooms fixed):** hopping rooms leak half the time. Of 839 #general ↔ #focus adoptions, 51% lie inside the logged cone (hop counts 148 at one hop, 193 at two, 89 at three); over all #51 cross-room adoptions (865, 5% of adoptions) 47% lie outside. The round-1 97% counted same-room adoptions as cross-room.
- **Static vs time-respecting graphs:** on the pre-item read-out graph (4 active h), cross-room adopters are unreachable in 5/8 two-room periods. In #35/#36 bridges existed before the item (h = 2–4), but no time-respecting path after it: 78–83% of their cross-room adoptions were still outside the cone. The static graph overstates reach; the time-respecting cone is the right object, as Vivian's scope anticipated.

**4. The front velocity is set by talk turns.**
- **Cycles per hop** (receiving calls from an adopter's first item exposure to its use, median): 47 (regime I), 46.5 (II), 16 (III). In talk calls: 5 / 2 / 1.5. In wall time: 25 / 19 / 6 min. v = 1/median is 0.02–0.07 hops per receiving call, 0.2–0.7 per talk call. 29–50% of hop events use the item at the first talk call after exposure.
- **Not cadence:** within periods, log Δt_hop on the adopter's pre-exposure call interval has b > 0 (CI) in only 3/25 powered periods (#33, #35, #38). Regime-III intervals barely vary (median 12 s), so the test has little leverage.
- **Not volume either:** c is significantly negative in 7/25 (faster in busy rooms) and positive in 3/25, including #51 (+0.65: dilution).
- **Across periods:** ρ(median Δt_hop, median τ_c) = 0.32 (p 0.08) vs ρ(median Δt_hop, 1/median volume) = 0.22 (p 0.23). The ordering is the predicted one; neither is significant.

**5. Violations can be counted but not traced.**
- **Pooled over periods (descriptive):** 1,479 robustly acausal adoptions vs 10,736 in-cone, item-exposed controls (500 per period).
- **The pre-registered "identified" share is not diagnostic:** 82% of violations have at least one candidate channel, but so do 82% of controls.
- **Lift = rate among violations / rate among controls:**
  - human cross-post 27.5× (6.2% vs 0.2%);
  - shared reply parent (common stimulus) 2.1×;
  - room move 1.8×;
  - the adopter's own intentions or commands (private stream) 1.5×;
  - shared repo 1.04×, site/domain 0.94×, history search 0.89×, templated statement 0.2×.
- **Reading:** in this village everyone touches the same repos and sites, so "a shared artifact could explain it" is true of almost every adoption. Logs alone cannot timestamp the leak.

**6. Native tests.**
- **NE42 (supported):** see 3. Within-group cycles per hop changed (62 / 20 / 11), so NE42-c failed: cadence and goal changed with the merge.
- **G38 (mixed):**
  - a (≥ 80% of cross-room adoptions outside the cone): 1.00, pass;
  - b (hazard ratio ≤ 0.2): 0.001, pass;
  - c (artifact + web ≥ 30% of cross-room violations, above within-room): 19% vs 31%, fail;
  - d (delay ratio ≥ 3): 830, pass.
  - Cross-room violations are enriched for history search (28% of them).
- **G31 (mixed):**
  - J_in 1.86 [1.24, 3.61], larger than the regime-III median 1.04, not smaller as predicted;
  - cycles per hop 43 receiving / 3 chat-mode / 4 talk calls (predicted ≤ 5 / ≤ 2);
  - clock test: between-agent SD of log hop delay 0.67 in seconds, 0.59 in receiving calls, 0.53 in chat-mode calls; difference CI [−0.28, 0.12], nominal pass but inconclusive.
- **G51 (mixed):**
  - only one adoption by a strictly isolated agent (acausal; a shared-artifact touch);
  - #focus hoppers bridge (97% in the cone, pass); **1b:** 51% of 839, fail;
  - cadence b 0.04 [−0.44, 0.59] fails, c 0.65 [0.17, 1.19].

## Outcome vs prediction
| # | Prediction (written ~06:00 UTC; A1–A5 at ~06:15 UTC) | Outcome | Verdict |
| --- | --- | --- | --- |
| P1 / A1 | J_in lower CI > 1 in ≥ 70% of powered II/III and ≥ 50% of powered I periods | II/III 3/10, I 8/19 (12/32 overall). Post hoc J_mh: II/III 7/11, I 15/21 | **fail** (post hoc pass) |
| P2 | A_rob ≤ 0.05 (II/III) / 0.10 (I); A ≤ 0.08 / 0.15 | A_rob within bound in 29/32 (misses #35, #36, #42, all from cross-room leaks); within-room A_rob ≤ 0.04 everywhere; A within bound 30/32 | pass within rooms; fail as written in 3 two-room periods |
| P3 | early A below the time-shuffled null in ≥ 80% | 32/32; but the synthetic field also passes 100% | pass, non-specific |
| P4 | one room V ≈ A; two rooms ≥ 90% of cross-room adopters at h = ∞ | V ≈ A in every one-room period; h = ∞ for ≥ 90% in 5/8 two-room periods (#35 43%, #36 29%, #39 71%) | partial |
| P5 | cycles per hop ≤ 5 (I), ≥ 10 (III); talk calls 1–2 | I 47 / 5 talk; III 16 / 1.5 talk | III pass; I fail |
| P6 | b > 0 (CI) in ≥ ½, b ∈ [0.5, 1.5], c > −0.2; b > \|c\| in ≥ ⅔ | b > 0 in 3/25; b ∈ [0.5, 1.5] in 3/25; c > −0.2 in 14/25; b > \|c\| in 8/25 | **fail** |
| P7 | ≥ 50% of robust violations have a channel; artifact + web largest for cross-room; residue ≤ 50% | 13/16 periods with ≥ 5 violations ≥ 50%; controls 82%; artifact/web not enriched (lift ≈ 1) | pass as written, non-specific; cross-room clause fails |
| P8 | in-flight hazard ≤ ⅓ of the entry hazard in ≥ ⅔ of powered II/III | J_in ≥ 3 in 2/10; J_mh ≥ 3 in 4/10 | **fail** |
| G38 | a, b, c (d) | a 1.00, b 0.001, c 0.19 vs 0.31, d 830× | mixed |
| NE42 | a ≥ 3× both ways; b; c | a 82×, 863×; b 1.00 / 0.02 vs 0.03 within / 1.00; c fails (62 / 20 / 11) | supported |
| G31 | a J_in > 1 and < regime III; b; c clock | a: J_in 1.86 > 1 but above regime III; b fails; c nominal | mixed |
| G51 | a, b, c | a: 1 event; b 0.97; c b 0.04 fails, c 0.65. **1b:** b 0.51 (fail); c b 0.18 [−0.20, 0.53] fails, c 0.53 | mixed (1b: mixed, b and c fail) |

Prior credences were P1 0.6, P2 0.5, P3 0.6, P4 0.7, P5 0.45, P6 0.4, P7 0.35, P8 0.55; native 0.4 / 0.55 / 0.45 / 0.35.

## Caveats
- **The headline gating result is post hoc.** J_mh was introduced after the first real period (G40), and its synthetic validation finished after the 31-period table had been computed. The pre-registered J_in failed. Treat J_mh as a strong lead until the holdout.
- **Items are hashed markers.** Co-generated names, numbers and rare words look like adoptions; numbers in particular behave like a shared field. Novelty is relative to the non-holdout corpus, so items first used in held-out periods can reappear as "novel".
- **Visibility is the ledger's room rule.** Starts are measured for Gemini only. Agents without a room record count as "unknown room" (not cross-room). The 200-event cap is modelled (#51: 3.6% of reads dropped). Room moves are dated at the first room-tagged event.
- **Cross-room leaks are not attributed.** The channel flags are permissive (any shared repo, site or command marker), so they mark nearly every adoption; only lifts against in-cone controls are interpretable. The private-stream and control samples are mildly nondeterministic (control sampling follows row order).
- **The cadence test has little leverage** (regime-III call intervals vary little). NE42 is confounded with #40's shared goal. H_tr (cone hop counts) were wrong in the first build; fixed and rebuilt for all periods.
- **Multiplicity:** 32 periods × several statistics, no correction. Per-period verdicts are replications, not independent tests. The class-specific jumps and channel lifts are descriptive.

## Confirmatory predictions (written 2026-10-04 after round 1, before any holdout use; `analysis/confirm.py`, not run)
Targets:
- **T1:** #51 tail (09-07 → 09-21), primary;
- **T2:** #47 (two rooms);
- **T3:** #28 (regime I);
- **T4:** the #46–#50 onboarding / isolation rooms (NE21+NE23 window).

Frozen tests (SHA-256 sealed before reading held-out text):
- **C1:** delay-matched J_mh lower CI > 1 in T1 and in ≥ 2 of {T1, T2, T3}.
- **C2:** within-room robust acausal share ≤ 0.03 in T1, T2 and T3.
- **C3:** T2 cage: ≥ 0.60 of cross-room adoptions outside the cone and cross/within hazard ≤ 0.20.
- **C4:** T4: every adoption by an agent isolated since t0 is outside the cone (a pipeline check); counts reported.
- **C5:** unmatched J_in reported, not tested.
- **C6:** median talk calls per hop ≤ 3 in T1 and T2.

**Supported** if C1 and C2 pass; the cage is confirmed if C3 passes.

**Dry run on stand-ins** (#51 08-24 → 09-05, #42, #30, #51 07-06 → 07-24; `confirm/result_dry.json`): C2, C3 and C6 pass, and C1 fails. The #51 stand-in segment, after NE43 (nudger silent), gives J_mh 0.60 [0.15, 1.12]. This is a warning that T1 may fail; C1 was not changed after seeing it.

**Reuse disclosure** (policy in `../holdout.md`): the #51 tail is also targeted by the unrun scripts of H14, H18, H20, H22 and H34; #28 by H10 and H34; #46–#50 by S3 and H26. H41's observable (ledger-cone status and call-level jumps of marker adoptions) differs from all of them.

## Round 1b (room-index fix, 2026-10-04)
*A bug-fix re-run, not a new test. No new predictions were written; round-1 predictions and verdict rules are re-scored as written. Holdout untouched; no confirm script run.*

### What changed
- **The bug.** `scheme/h41core.load_skeleton` kept `rooms_timeline` rows with `te ≥ t_min − 1 day`. Open segments (`t_end` null: each agent's current, last segment) fail that comparison and were dropped, so `RoomIndex.at` returned the agent's previous room, or −1 (unknown) if it had none. Found by the re-freeze (`analysis/CONFIRM_R1B.md`); patched by the coordinator.
- **The fix and the switch.** `h41core.rooms_table` keeps open segments with `te = +∞`. `H41_ROOMS=old` reproduces round 1: rebuilding #44 with it gives identical items, adoptions and hazard tables.
- **What uses rooms:**
  - the source-room flag `in_room0` (J_in, J_mh and the hazard groups);
  - the adopter's room at t0 (`cross`: cross-room shares, the cage);
  - the static-hop seeds (h4, h24) and the room cone `h_room`;
  - the room volume V (cadence regression);
  - the `room_move` channel flag.
- **What does not use rooms:** the logged cone itself (K, T, H come from ledger reads), items, adoptions, acausal status and velocity. `native.py` reads the full timeline for the NE42 partition and for G51 isolation, so those were never affected.
- **Other H41 code paths.** `RoomIndex.rooms_in` and `moves` use segment starts only; they are correct once open rows are kept. No other path drops open rows. `confirm_r1b.fix_rooms` is now redundant but gives the same index. The frozen `confirm.py` picks up the fixed index through `load_skeleton`; it is superseded by `confirm_r1b.py` and was not run.
- **Second fix: deterministic bootstrap.** The J_in and J_mh day bootstraps drew from `unique()` days in arbitrary order, so CIs moved between runs. Days are now sorted (`analysis/h41stats.py`). This is not a room effect, but it moves borderline verdicts (below).

### Which periods the bug touched (`analysis/rooms_audit.py` → `results/rooms_audit.json`)
| Period | Hazard lookups (agent × source message) with a changed room | In-room flag changed | Adoptions with changed room at t0 | Cross-room label changed | Cause |
| --- | --- | --- | --- | --- | --- |
| #5–#31 | 0 | 0 | 0 | 0 | before rooms, everyone is in #general |
| #33 | 9.1% of 11,421 | 9.1% | 6.6% | 0 | one agent's open #general segment dropped → room unknown, not cross |
| #35–#42 | 0 | 0 | 0 | 0 | no open segment in the window. #38 is 0 at every call on non-holdout days; the re-freeze note's "5%" does not reproduce there |
| #44 | 3.0% of 16,934 | 0.7% | 2.0% | 0 | one agent's open room-2 segment |
| #51 | **62.9%** of 632,193 | **57.3%** | **51.8%** | **45.7%** | every agent's open #general segment from 07-06; cross-room adoptions 8,368 → 865 |

Rebuilt with `scheme/build.py periods --only 33,38,44,51` plus the `private` step. The #38 rebuild is identical: same adoptions, hazard and items. Its violations differ only in the in-cone control sample, which follows a nondeterministic row order. Then `explore.py`, `native.py`, `figures.py` and `write_estimates.py` were re-run. The synthetic validation was re-run on the #51 skeleton (`synthetic/runs_r1b_51.parquet`).

### Old → new (`analysis/round1b_compare.py` → `results/round1b_compare.json`)
| Statistic | Round 1 (stale rooms) | Round 1b |
| --- | --- | --- |
| #51 J_in (pre-registered) | 40.7 [12.2, 110]; in-flight n 158,639, h 0.0003 | **2.08 [1.49, 3.10]**; in-flight n 16,894, h 0.0033 |
| #51 J_mh (post hoc) | 15.8 [7.4, 31.1] | **9.2 [6.5, 13.9]** |
| #51 J_mh by class N / D / W | 18.7 / 11.3 / 12.8 | 11.0 / 7.8 / 2.5 |
| #51 cross-room share of adoptions | 0.51 | 0.052 (865) |
| #51 cross-room robust acausal share | 0.05 | **0.47** (408 / 865) |
| #51 within-room A_rob | 0.005 | 0.002 |
| #51 #focus bridging (native b) | 0.97 of 1,720; hops 1588 / 70 / 11 | **0.51** of 839; hops 148 / 193 / 89 |
| #51 cadence b; volume c | 0.04 [−0.44, 0.59]; 0.65 [0.17, 1.19] (n 7,665) | 0.18 [−0.20, 0.53]; 0.53 [0.09, 1.10] (n 15,146) |
| #51 static h = ∞ share; outside room cone | 0.050; 0.55 | 0.072; 0.019 |
| #33 J_in; J_mh | 1.88 [1.30, 3.29]; 3.03 [2.19, 5.48] | 1.87 [1.31, 2.75]; 2.93 [2.28, 4.07] |
| #44 J_in; J_mh; volume c | 0.68 [0.37, 1.73]; 1.45 [0.83, 5.82]; 0.07 [0.01, 0.67] | 0.70 [0.36, 1.84]; 1.47 [0.83, 4.18]; 0.06 [−0.00, 0.67] |
| #38 native (cage 0.001, a 1.00, c 0.19 vs 0.31, d 830×) | as listed | identical |
| NE42 (82× [21, 223], 863× [186, 2365]; acausal 1.00 / 0.02 / 1.00) | as listed | identical |
| Synthetic, #51 skeleton (24 runs): field J_mh; relay; timing error | 0.95, 1/4 false positives; ∞ 12/12; 8.0, 3/4 | 0.72, **0/4**; ∞ 12/12; 6.9, 4/4 |
| All periods: J_in lower CI > 1 | 12/32 (I 8/19 powered, II/III 3/10) | 10/32 (I 6/19, II/III 3/10) |
| All periods: J_mh lower CI > 1 | 22/32 (I 15/21, II/III 7/11) | 23/32 (I 15/21, II/III 8/11) |
| Verdicts, rule A4 (supported / failed / n/a) | 11 / 18 / 3 | 9 / 20 / 3 |
| Verdicts, post hoc | 20 / 9 / 3 | 21 / 8 / 3 |
| Within-room A_rob, median and max | 0.6%, 4% | 0.6%, 4% |
| P8: J_in ≥ 3; J_mh ≥ 3 (powered II/III) | 2/10; 4/10 | 1/10; 3/10 |
| P6: c > 0 with CI (of 25) | 3 (#37, #44, #51) | 2 (#37, #51) |
| Pooled channel lifts: room move; human cross-post; repo / site / search | 1.83; 27.5; 1.04 / 0.94 / 0.89 | 1.85; 22.8; 1.04 / 0.95 / 0.90 |

**Bootstrap jitter, not rooms, moves the counts outside #33, #44 and #51** (`results/round1b_seed_stability.json`, 20 seeds). Lower CI > 1 in:
- G18 J_in: 6/20 seeds;
- G27 J_in: 14/20 seeds; G27 J_mh: 9/20;
- G35 J_mh: 0/20 (the sorted draw gives 1.005);
- G23 J_mh: 2/20;
- G26 J_in: 4/20; G30 J_in: 3/20.

Read the gating counts as J_in 10–12/32 and J_mh 22–24/32. The human cross-post lift moved because the four rebuilt periods drew new in-cone control samples. It is 23–28×.

### Verdict changes
- **No verdict changes because of rooms.**
  - G51 native stays mixed, but b (#focus bridging) now fails as well as c (cadence).
  - G51 replication stays supported / supported, because J_in's lower CI is still > 1.
  - G33, G38, G44 and NE42 are unchanged.
- **Bootstrap-borderline periods.** The 1b verdict is the one that holds in the majority of 20 seeds.
  - G18 (rule A4): supported → **failed**.
  - G27 and G35 keep their round-1 verdicts, although the sorted draw flips them.
  - Each affected README has a `**Verdict (1b):**` line.

### Which headline claims survive
1. **Within-room bound** (robust acausal median 0.6%, max 4%): survives unchanged.
2. **Cage: 75–100% of cross-room adoptions outside the cone in 7/8 two-room periods** (#35–#39, #41, #42; #44 0.11): survives unchanged. Those periods had no stale lookups. #38's hazard ratio 0.001 [0.0003, 0.002] and the 71 h delay are unchanged.
3. **NE42's 82× and 863×, and the 1.00 / 0.02 / 1.00 acausal shares:** survive exactly. They never used the stale index.
4. **#51 #focus bridging (97% in the cone): does not survive.**
   - With true rooms, 51% of 839 #general ↔ #focus adoptions are inside the cone, mostly over two or three hops.
   - Over all #51 cross-room adoptions, 47% are outside the cone.
   - Hopping rooms are a leaky cage, between a broadcast room (about 100% in the cone) and #38's fixed split (0%).
   - The round-1 97% counted same-room adoptions as cross-room.
5. **#51's large jump: shrinks.**
   - J_in 40.7 was an artifact: mislabelled agents put 9× too many calls into the in-flight group.
   - The true values are J_in 2.1 [1.5, 3.1] and J_mh 9.2 [6.5, 13.9]. That is still the largest regime-III matched jump.
6. **Gating counts (12/32 pre-registered, 22/32 post hoc):** survive within bootstrap noise (10–12 and 22–24).
7. **Channel attribution:** survives. Human cross-posts are 23–28× enriched and room moves 1.8×; repos, sites and search are about 1.
8. **Velocity:** unchanged, because it is cone-based.
9. **Cadence:** still fails. #51's b is 0.18 [−0.20, 0.53] and its dilution c is 0.53.
10. **Synthetic validation (F):** holds and improves on the fixed #51 skeleton: the field gives J_mh 0.72 with 0/4 false positives.
11. **Confirm dry run:** the T1 stand-in's J_mh goes from 0.60 to 12.9 (`CONFIRM_R1B.md`). The "T1 may fail" warning was this bug.

### Scorecard after 1b
Unchanged: A1 B1 C1 D1 E1 F1 G1 H1 I1.
- G loses one supporting fact (#51 bridging). The #38 cage and NE42 still stand.
- F gains a cleaner field null on #51.
- C: the gating counts now carry a stated bootstrap uncertainty of ±2 periods.

### Code and data (1b)
- **Code:**
  - `scheme/h41core.py`: `rooms_table`, `ROOMS_MODE` (`H41_ROOMS`).
  - `scheme/build.py`: a partial rebuild merges `periods_meta.json`; the provenance entry `periods_partial` records the rooms mode.
  - `analysis/h41stats.py`: sorted bootstrap days.
  - New: `analysis/rooms_audit.py`, `analysis/round1b_compare.py`, `analysis/write_estimates.py`.
  - `analysis/figures.py`: uses `synthetic/runs_r1b_51.parquet` unless `H41_ROOMS=old`.
- **Data** (`data/processed/H41-readout-light-cone/`):
  - `round1/`: the round-1 tables of #35–#51 and round-1 `results/`, copied before the rebuild. `round1/G33` was regenerated with `H41_ROOMS=old`, because its snapshot was missed; it has no private-stream flags.
  - `results/rooms_audit.json`, `results/round1b_compare.json`, `results/round1b_seed_stability.json`.
- **Estimates:** all periods re-emitted to `per_period_estimates`. New statistics: `acausal_share_robust_cross_room`, `cross_room_hazard_ratio_cage` (G38) and `focus_cross_room_in_cone_share` (G51).

## Round 2 redirects (2026-10-04)
*Proposed by the round-1 agent; the coordinator may revise.*
- **What the direction is really after:** which channels actually move information between agents, and how fast. The logged chat channel is gated at the call scale and bounded by rooms, but a third of fast adoptions and almost all cross-room spread come from elsewhere.
- **H41-R1. Pre-register the matched jump and the class split.** Make J_mh (with names, numbers and links separately) the primary estimator for the holdout and for H34's re-evaluation on the ledger.
- **H41-R2. Time-stamp the unlogged channel.** Use DQ4's file-level commit history and the agents' URL fetches to test whether cross-room adopters read the source's file or page *after* the source's post and *before* their use, against matched in-cone controls. This replaces "touched the same repo" with an ordered event.
- **H41-R3. HH187: lags quantized in calls.** On hop events, test whether lags pile up at integer multiples of the recipient's call interval, and whether the multiple tracks the cone hop count where it exceeds 1 (#51 #focus, NE42).
- **H41-R4. Co-generation as a field.** Model the in-flight hazard as a common stimulus (shared reply parent, same dashboard, same tool output), and check whether it explains the numbers' J ≤ 1.
- **H41-R5. Exogenous cadence.** Use declared pause lengths (timer wakes) as an instrument for call cadence within agents, to test cycles vs wall time with real leverage.

## Round 2 (2026-10-05): ordered artifact reads, lags vs hops, co-generation as a field
*Items H41-R2, R3 and R4. R1 (pre-registering J_mh on reserved data) is skipped here: it needs the reserved data. Predictions, nulls and kill rules written 2026-10-05 03:50 UTC, before any round-2 statistic on real data. Reserved data are masked with `holdout_mask` and `calendar.holdout` in every script. Round-1 and 1b code and outputs are unchanged; round-2 code is in new files (`scheme/build_r2.py`, `analysis/r2_*.py`); outputs go to `data/processed/H41-readout-light-cone/r2/`.*

**Seen before writing:** the schemas of `artifact_mentions`, `artifact_commands_text`, `work_commits`, `work_repos`, `search_events`; the counts of action verbs by artifact kind since 2026-02-25 (no link to adoptions); that `git log --name-status` runs on the bare DQ4 clones (blobless clones keep trees; commits-only clones have no file names); round-1b table counts: cross-room robustly acausal adoptions per period (#35 376, #36 376, #38 58, #42 31, #51 408; #37, #39, #41, #44 ≤ 13), in-cone adoptions at cone hop count H ≥ 2 (#35 270, #36 213, #51 1,225, #38 20; #39–#41 ≤ 2), and class-D adoption counts; H05 round 2's one-line result (novel repos leak across rooms through command output, lift 21); H50 round 2 (length bias of in-flight anchors; relay reads batch). No round-2 statistic had been computed.

**Common rules.** Cross-room = the adopter's known room at t0 differs from room0 (both known). Active time is the calendar's active-window coordinate (`h41core.active_time`). Pooling across periods is exception (d) in `CLAUDE.md` (too few events per period): pooled numbers are Mantel–Haenszel or inverse-variance combinations with period strata, always shown next to the per-period values. CIs are 95%. Bootstraps resample 1-h blocks of t0 within PT days (Known issue: day clusters under-cover in 5-day periods), 400 draws.

### R2. Time-stamp the unlogged channel: ordered reads of the source's artifacts
**Question.** Do cross-room adopters read the source's file or page *after* the source wrote it and the source posted, and *before* their own use, more than matched agents who did not adopt?

**Definitions.**
- *Source-written artifacts* W(s, t0, t_use): (i) repos and files that the source committed to (DQ4 `work_commits`, author = source agent, not `automated`) with commit time t_w ∈ [t0 − 6 h, t_use); file paths come from `git log --name-status` on the DQ4 clones (new table, built by `scheme/build_r2.py files`, paths hashed, no content); (ii) repos and sites the source pushed or deployed (`artifact_mentions`, source agent, verb `git push` or `deploy`) in the same window; (iii) artifacts linked in the source message m0 (t_w = t0). A site whose `parent` is a written repo counts as written.
- *Read events* of the adopter a: `artifact_mentions` rows (source action, `how` ∈ {url, output, bare, cwd}) with a read verb: `git pull`, `git fetch`, `git clone`, `gh repo clone`, `glab repo clone`, `fetch`, `git show`, `git log`, `gh pr view`, `gh pr diff`, `gh issue view`, `glab mr view`, `glab issue view`, `gh api`, `gh api repos`, `glab api`, `glab api projects`, or a null verb with `how = url` (a page visit). Plus *local file reads*: a command row of a whose working-directory repo (`how = cwd`) is a written repo and whose command text names a path that the source committed (full relative path, or a basename of ≥ 8 characters outside a stoplist such as README.md and index.html). Command text is read in memory only.
- A read *matches* W when its artifact is a written artifact, a file or site of a written repo, or the repo of a written file, and t_r > t_w.
- *Ordered read* E_ord: a matching read with max(t0, t_w) < t_r < t_use (the card's wording). Variant E_ord⁻: t_w < t_r < t_use (a read between the source's write and its post also counts).
- *Post-use placebo* E_post: a matching read (same W) in (t_use, t_use + Δ], where Δ is the active length of (t0, t_use]. Where the period's non-reserved days end first, both windows shrink to the same Δ′ (pre-window (t_use − Δ′, t_use]).
- *Channels* of an ordered read: pull (git pull, fetch, clone), page (fetch or page visit of a site, repo or file URL), file (a file URL or a local file read of a source-committed path), api (gh / glab api, PR and issue views).

**Design: a case–control within items (partition contrast: adopter vs non-adopter at the same moment).** A stratum is one cross-room robustly acausal adoption (item, adopter a, t0, t_use). Its controls are the item's other at-risk cross-room agents: agents in another room than room0 at t0, with a receiving call in (t0, t_use], who never use the item in the period. Controls get the adopter's windows.
- OR_ord, OR_post: Mantel–Haenszel odds ratios of E_ord and E_post (adopter vs controls) over strata.
- **Primary: Λ = OR_ord / OR_post.** A shared project (both agents read the source's repo anyway) raises both ORs; an artifact that carries the item raises only OR_ord.
- Secondary: the specificity ratio OR_ord(source artifacts) / OR_ord(artifacts the source did not write, read in the same window), which removes "adopters are simply busier".
- **Card-literal comparison:** the ordered-read share among cross-room robustly acausal adoptions vs in-cone item-exposed adoptions, matched on period × delay bin (< 5 min, 5–30 min, 30 min–2 h, 2–8 h, 8–24 h, > 24 h) × item class; Mantel–Haenszel risk ratio L_ctrl. Expected bias: in-cone controls are mostly same-room pairs, which share repos more, so L_ctrl leans low.
- Descriptive: ordered-read shares by channel; the share with E_ord⁻.
- Periods: two-room or hopping periods with ≥ 20 cross-room robustly acausal adoptions (#35, #36, #38, #42, #51). Others (#37, #39, #41, #44) descriptive only.

**Synthetic validation first (real strata, real read events, real windows; only the identity of the adopter in each stratum is redrawn).**
- Z0 activity field: adopter drawn among stratum members ∝ talk calls in (t0, t_use].
- Z1 project field: ∝ the member's read rate of the source's artifacts over the whole period (unordered).
- Z3 length world: ∝ the summed wall length of the member's talk calls in the window (talk depends on call length).
- Z2 leak (f = 0.25, 0.5): with probability f the adopter is a member with an ordered read (if any), else Z0.
- Pass: Λ lower CI > 1 in ≤ 10% of Z0, Z1, Z3 runs (size); in ≥ 80% of Z2 runs at f = 0.25 (power). 50 runs per world.

**Predictions.**
- **P-R2a (primary):** pooled Λ > 1 with lower CI > 1. Per period, Λ > 1 in ≥ 3 of the 5 periods. Prior 0.4.
- **P-R2b (card-literal):** the ordered-read share among cross-room robustly acausal adoptions exceeds the delay-matched in-cone share (L_ctrl > 1, lower CI > 1). Prior 0.3 (bias above).
- **P-R2c:** pull is the largest channel among ordered reads; the specificity ratio > 1. Prior 0.4.
- **Kill rules.** (i) Λ's CI includes 1 or lies below it, with Z2 power ≥ 0.8 at f = 0.25: "ordered artifact reads do not carry cross-room items at a share ≥ 25%". With power < 0.8 the verdict is inconclusive. (ii) Size > 0.10 in Z0, Z1 or Z3: Λ is not interpretable and R2 is not scored.

### R3. Lags quantized in calls, and lag vs cone hop count
**R3-Q (quantization).** Hop events: exposed in-cone adoptions with an agent parent. τ_loc = the adopter's median receiving-call interval in the hour before exposure (intervals ≤ 30 min). Two phases: x_m = (t_use − t_m)/τ_loc from the first exposing message, and x_e = (t_use − t_call(c_e))/τ_loc from the start of the call that first read it. Statistic: phase concentration R = |mean exp(2πi x)|.
- *What the model says before any data:* a message arrives at a uniform phase of the recipient's call, so x_m is smeared under any coupling clock. x_e is quantized whenever uses are emitted at call starts, under relay and under a field alike. So R3-Q describes the emission process; it cannot score gating unless the synthetic relay and field worlds separate.
- **P-R3a:** real R_m ≤ 0.05 and within the synthetic range of both worlds; real R_e > R_m. Kill: none (descriptive). If relay and field worlds give overlapping R_e, R3-Q is declared non-discriminating.

**R3-H (does the multiple track the cone hop count?).** In-cone adoptions with H ≥ 1 (H = hop count of the earliest time-respecting read-out path at the cone entry). Lag in the recipient's calls: n = receiving calls with a start in (t0, t_use] (a start-time count with no in-flight anchor; H50's length bias does not enter). Statistics: M₂ = median n(H = 2) / median n(H = 1), the same for H ≥ 3, the front ratio F₂ (10th percentiles), Spearman ρ(n, H), and the multiple n/H by H (descriptive).
- *Null: entry-conditioned lag permutation.* Keep each adoption's source, t0, adopter, cone entry and H. Redraw the lag from the period's in-cone lags, conditioned on t0 + lag ≥ the adopter's cone entry (the adoption stays in the cone), and recount n on the adopter's calls. This removes the mechanical part (agents behind a bridge enter later, so late adopters have larger H). 500 draws. Excess Δ_M = M₂ − mean(M₂*), one-sided p.
- *Synthetic first, on real skeletons with H ≥ 2 paths:* #51 08-05 → 08-22 (#focus hopping) and #36 (two rooms with bridges). Worlds: T1d decaying relay; T2 field pulse; W_L, a field whose per-talk-call hazard is proportional to the call's own latency (talk depends on call length). Pass: p < 0.05 in ≤ 10% of T2 and W_L runs, and in ≥ 80% of T1d runs.
- Periods: those with ≥ 30 in-cone adoptions at H ≥ 2 (#35, #36, #51). NE42 (#39–#41) has ≤ 2 such adoptions per period: R3-H is n/a there (counts seen before writing).
- **P-R3b:** in #35, #36 and #51, Δ_M > 0 with p < 0.05, and M₂ ≥ 1.5. Prior 0.5.
- **Kill rules.** (i) Size > 0.10 in T2 or W_L: not scored. (ii) Power < 0.8 in T1d: inconclusive. (iii) Otherwise Δ_M ≤ 0 or p ≥ 0.05 in ≥ 2 of the 3 periods: "the lag does not track the cone hop count beyond entry".

### R4. Co-generation as a field: numbers, call length and common stimuli
**Units.** For each novel item (source message m0 at t0, room0) and each roster agent a ≠ source in room0 at t0: (1) a's talk call in flight at t0 (t_call < t0 < t_first ≤ t0 + 2 h, same day), and (2) a's first talk call with t_call > t0 (same horizon). A unit is at risk if a has not used the item before; the outcome is a's first use at that call. Coordinates: s = t_call − t0 (start time), lat = t_first − t_call, d = t_first − t0.
- *Why a new estimator:* matched on d, an in-flight call has lat > d and a post-t0 call has lat < d, so J_mh compares long calls with short ones (H50's length bias). Long calls write long messages, which hold more numbers. This is a rival for J_D ≤ 1 that round 1 did not test.
- **J_rd (start-time RD):** local-linear hazards in s on each side of 0 (|s| ≤ 60 s primary, 120 s secondary); J_rd = h₊(0)/h₋(0). At s → 0 both sides have the same delay and an unselected call length.
- **Common stimulus CS_art** (agent sources only): the agent and the source both touched the same artifact (or the same repo through `parent`) in an action (`how` ∈ {url, output, bare}): the source in [t0 − 30 min, t0], the agent in [t0 − 30 min, t_first of the unit's call). Only artifacts touched by ≤ 50% of that day's active agents count (a specific stimulus, not the village's common repo).
- Statistics per class (D numbers, N names, W rare words, U links): J_mh (round-1 estimator on these units), J_rd, ψ = MH ratio (over delay bins) of the in-flight hazard with CS_art = 1 vs 0, J_mh restricted to CS_art = 0 units, and the CS_art share of in-flight vs post-t0 adoptions. Descriptive: the share of in-flight adoptions whose message shares its DQ2 reply parent with m0.
- Periods: all 32 replication periods; pooled per regime.

**Synthetic validation first** (skeletons #38, #31, #51 07-06 → 07-23; 400 items per run, 4 seeds per world). Y0 decaying relay; Y1 relay + common stimulus (agents with CS_art = 1 get hazard 0.15 per talk call in [t0 − 5 min, t0 + 10 min], without reading); Y2 length field, no relay (pulse hazard ∝ lat); Y3 field pulse (T2); Y4 relay + length field. Pass: J_rd lower CI > 1 in ≤ 10% of Y2 and Y3 runs and in ≥ 80% of Y0 and Y4 runs; ψ lower CI > 1 in ≥ 80% of Y1 runs and ≤ 10% of Y0 runs; J_mh | CS = 0 lower CI > 1 in ≥ 80% of Y1 runs.

**Predictions.**
- **P-R4a (length rival rejected):** pooled regime-III J_rd,D has a CI that includes 1 or lies below it (numbers stay co-generated under the start-time design), while J_rd,N has lower CI > 1. Prior 0.5.
- **P-R4b (common stimulus present):** the CS_art share of in-flight D adoptions is ≥ 2× that of post-t0 D adoptions, and pooled ψ_D has lower CI > 1. Prior 0.35.
- **P-R4c (common stimulus explains J_D ≤ 1):** pooled regime-III J_mh,D | CS = 0 has lower CI > 1. Prior 0.3.
- **Kill rules.** (i) J_rd false positives > 10% in Y2 or Y3: J_rd not scored. (ii) J_rd,D lower CI > 1: numbers' J ≤ 1 was an artifact of the in-flight design (recency and length), and R4's field question is moot. (iii) J_mh,D | CS = 0 CI includes 1 and ψ_D CI includes 1: "the measured common stimulus does not explain the numbers' co-generation". (iv) If CS_art covers < 10% of in-flight D adoptions, CS_art cannot explain J_D ≤ 1 whatever ψ is.

**Reporting.** `per_period_estimates` rows (round 2): `r2_lambda_ordered_read`, `r2_or_ordered`, `r2_ordered_share_cross` (R2); `r3_M2_excess`, `r3_phase_R_m`, `r3_phase_R_e` (R3); `r4_J_rd_<class>`, `r4_J_mh_cs0_D`, `r4_psi_D` (R4). Overlap note: H05 round 2 measures a cross-room leak conductance through command output and history search. H41-R2 builds its own read and write tables in its own folder and does not use H05 files.

## Notes
- 2026-10-04: promoted from HH155 by Vivian; scope: the interaction graph, not rooms.
- 2026-10-04 ~06:00 UTC: round-1 agent wrote the operational definitions, observables, nulls, synthetic plan, predictions and native-test predictions before any real-data run.
- 06:05–06:13 UTC: synthetic run 1; amendments A1–A5 at ~06:15 UTC; period READMEs with dated predictions at 06:16 UTC.
- ~06:22 UTC: first real period (G40) built; J_in = 0.59 exposed the recency confound → A6 (post hoc). Synthetic run 2 (with a decaying relay and J_mh) ~06:35–06:55 UTC.
- **Bugs found and fixed during round 1:**
  - empty-array dtype in `active_time` (periods with agents without talk calls failed);
  - the cone's hop-count pass overwrote the source's hop count (H_tr wrong; K and T unaffected). Fixed, and all periods rebuilt;
  - ledger items beyond the 200-event cap are now excluded (#51 only; numbers moved by < 0.01);
  - cross-room is defined only for agents with a known room;
  - the confirm script imported H34's `build.py` by name (path order).
  - **round 1b (2026-10-04):** the room index dropped open `rooms_timeline` segments (stale rooms in #51, #33, #44); fixed, `H41_ROOMS=old` reproduces round 1. The J_in / J_mh day bootstrap was nondeterministic; days are now sorted. See "Round 1b".
- **Read-only imports:** `hypotheses/H34-idea-cascades/scheme/markers.py` (marker rule) and `scheme/build_markers.py` (`non_holdout_chat`, `_init`, `_work`). No other hypothesis code or data is used; H08's Claude Code tables (`cc/`) were empty, so no Claude Code ground truth.
- **Data:** `data/processed/H41-readout-light-cone/` (≈ 15 MB, `_provenance.json`): `markers/`, `G<NN>/{items, adoptions, hazard, violations}.parquet`, `synthetic/`, `results/`, `confirm/`. Hashes and ids only.
- **Proposed for `physics-models/DEFINITIONS.md`** (not edited; outside H41's scope):
  - *interaction (read-out, ledger)*;
  - *logged light cone (time-respecting)* and *cone entry call*;
  - *acausal adoption*;
  - *cycles per hop*;
  - *static hop distance (pre-item read-out graph)*;
  - *jump at the cone boundary (J_in; delay-matched J_mh)*.
- **Proposed pitfalls:**
  - `physics-models/03-contagion`: adoption hazards fall steeply with time since the item appeared, so any seen-vs-unseen or in-flight-vs-entry comparison must be matched on delay (H29's rule applies to adoption too); numbers are co-generated;
  - `02-nonequilibrium-ising`: a static (aggregated) read-out graph overstates reach; use time-respecting paths.
