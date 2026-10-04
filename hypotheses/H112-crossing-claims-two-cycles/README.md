# H112: Crossing claims anti-coordinate: parallel updates make 2-cycles

**Status:** exploratory round 1 done (2026-10-04, non-holdout only). **Failed as posed: no 2-cycle and no 2× departure excess after crossing co-switches.** Over 9 testable periods (2,227 co-switch pairs), pairs whose movers had not read each other's claim depart within 5 calls 1.15 [1.08, 1.22]× as often as pairs where one had read the other (86% vs 73%), far below HH343's 2× and capped by the high base rate. The literal crossing class (both claims in flight) has 20 pairs: RR_F 1.04 [0.80, 1.35]. Once a partner claim exists in both classes the excess disappears (1.02 [0.92, 1.13], post hoc A2), so the 1.15 is chat engagement, not update order. Mutual leaving is not higher after unaware co-switches (M 1.07 vs 1.19 read); departures do not follow the read of the partner's claim in #51 (0.79 [0.37, 1.64]); the own-role weeks show no larger effect (ratio 0.88 [0.73, 1.06]). A synthetic on the real call schedules shows that a read-gated avoidance model predicts RR_U < 1, not ≥ 2. `analysis/confirm.py` is frozen and dry-run, not run. Card written 2026-10-04 21:30 UTC before any departure statistic; A1 (pre-data) and A2 (post hoc) below. Approved by Vivian in the dashboard vetting panel 2026-10-04 from HH343.
**Fields:** stat mech (kinetic Ising/Potts under parallel vs sequential update; Little-model 2-cycles), sociophysics (anti-coordination, minority games), dynamics
**Literature:** no paper in `literature/` covers the Little model or update-order 2-cycles. Classical background named, not filed (†): Little, "The existence of persistent states in the brain", *Math. Biosci.* 19, 101 (1974)†; Peretto, "Collective properties of neural networks: a statistical physics approach", *Biol. Cybern.* 50, 51 (1984)† (parallel dynamics, period-2 cycles); Goles & Olivos (1980)† (cycles of length ≤ 2 for symmetric parallel threshold networks); Challet & Zhang (1997)† (minority game). Nearest filed note: model 02's update-rule table (`physics-models/02-nonequilibrium-ising/README.md`).
**Definitions used** (`physics-models/DEFINITIONS.md`): *Agent state (categorical, project/artifact strict)* (H11) at call resolution; *Switch (attention arrival)* (H104), here in a call-level variant from action touches; *Interaction (ledger-visible exposure)* and *Unread (in-flight) exposure placebo* (RE-D1); *Mutually invisible (in-flight) set I(B)* (H57); *Exposure (ledger receiving call)* (RE-V1); *Regime*; *Population N(t)*. New named variants proposed here (not edited into DEFINITIONS.md; see the report): **switch-in (action, call-level; H112)**, **co-switch (H112)**, **awareness class (read / in flight / silent; H112)**, **departure within K calls (H112)**, **mutual-leave excess M (H112)**, defined under Data scheme and Observables.
**From:** HH343 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/02-nonequilibrium-ising/` (primary: the update-rule table, parallel updates allow 2-cycles), `physics-models/10-potts/` (categorical project states; antiferromagnetic coupling = avoidance)
**Question served:** **Q1** (what couples agents: does the coupling act only through what was read, so that the order of reading sets the outcome?). Q3 is secondary (a 2-cycle would be a collective dynamical mode that no field produces).

## Source HH (verbatim from the HH list, including refinements)
- **HH343 · Crossing claims anti-coordinate: parallel updates make 2-cycles.** In the Little model (all spins update at once), coupled spins can fall into period-2 oscillations that sequential updating never shows. In the village, two agents can switch to the same project within one read-out window without having read each other (a crossing, both messages in flight), or one after reading the other (sequential). H93 found that agents avoid occupied repos in #42 and #51.
  - *Prediction:* after a crossing co-switch, at least one of the two leaves the project within 5 calls ≥ 2× as often as after a sequential co-switch. Leaving is mostly mutual (a 2-cycle: both leave). Sequential co-switches stick (herding, H63).
  - *Check:* co-switches from `project_states` and DQ4 commits; crossing vs sequential classified from the ledger (each message's presence in the other agent's producing call); a time-shuffled null at matched lag.
  - *Kill:* departure rates are equal within CI.
  - *Impostors:* convergence: the in-flight vs read split is the design. Scheduler: matched lag. Exogenous: kickoff-named projects stratified. Priors: pair fixed effects.
  - *Models:* 02, 10 · *Builds on:* H93, H63, H40, H57

## Question
When two agents move onto the same project within minutes, does the order of reading decide what happens next? The Little-model reading: if neither had read the other's move (a parallel update), each moved on the old state; once each reads the other, an avoiding (antiferromagnetic) pair should both leave. If one moved after reading the other (a sequential update), the move was made on the new state and should stick.

## Model
**From:** `physics-models/02-nonequilibrium-ising/` ("Non-random update order": parallel updates are not Boltzmann and allow 2-cycles at low T) with `physics-models/10-potts/` states.

**H112 variant: kinetic Potts with read-gated beliefs and a per-call clock.** Agent i holds project σ_i. At each of its calls it updates with probability p_u:
P(σ_i → j) ∝ exp(h_j + h_ij + J · n̂_ij(t)),
where n̂_ij is the number of other agents that i *believes* are on j. Beliefs change only at read-out: an agent learns of j's move when it reads a message of j that names the project (the ledger receiving call, H08/H40). The read-out delay d (median ≈ 20 s, q99 6–16 min; H42) sets the effective update order:
- **sequential pair:** the second mover had read the first mover's claim (belief updated before the move);
- **parallel (crossing) pair:** the second mover had not read it (both moved on the old state).
For J < 0 (avoidance; H93 #42, #51), a crossing pair is a frustrated configuration once both read each other: each leaves with probability ∝ 1 − e^{J}, so leaving is frequent and mutual (a 2-cycle). A sequential pair formed despite J < 0 only when the field h_j outweighed the avoidance, so it should stick. For J > 0 (herding; H63), both kinds stick. For J = 0 the read order is irrelevant.

**What would make HH343 true:** departures after unread co-switches exceed departures after read co-switches by ≥ 2× at matched lag; departures after unread co-switches are mutual beyond independence; read co-switches stick at or below the solo-switch departure rate. The effect should be largest where H93 found avoidance (#42, #51).

## Data scheme (`scheme/`)
`scheme/build.py --period G<NN>` writes `data/processed/H112-crossing-claims-two-cycles/G<NN>/` from shared tables only (no text; project names hashed on output).
- **Inputs:** `artifact_mentions` (strict `how ∈ {url, output, bare}`; sources action and chat) with `project_states.project_map` (files and sites → parent repo); `project_mentions_chat` (claims: agent chat messages strictly naming a project); `producing_calls`, `call_windows` and `context_ledger_items` via `infra/shared/visibility.py` (`load_calls`, `producing_call`, `receipts`); DQ4 `work_commits` (agent-work filter: `canonical & ~imported & author_kind == agent & ~automated`; secondary channel); `replicator_hosts.kickoff_named` (H54/kickoff_naming rule) for the exogenous stratum; `calendar`, `period_units`, `roster`. Holdout days dropped with `common.holdout_mask` before anything is computed.
- **Switch-in (action, call-level; H112):** an action touch of project P by agent i at time t (the call that holds the touch = i's latest call with t_call < t), when i's previous touch that PT day was a different project and i did not touch P in the previous 60 min (H104's arrival rule at touch resolution). Work channel (secondary): H104's *switch (work arrival)* on DQ4 commits.
- **Co-switch (H112):** two switch-ins onto the same P by different agents i (first, at t_i) and j (second, at t_j) on the same PT day with lag Δ = t_j − t_i ≤ 15 min. An event belongs to at most one co-switch: its nearest partner. Triples are split into their earliest pair.
- **Claims:** agent chat messages strictly naming P (`project_mentions_chat`), by i posted in [t_i − 15 min, t_j) and by j posted in [t_j − 15 min, t_i).
- **Awareness class (H112)**, from each claim's presence in the other agent's switch call (visibility rule: seen iff the claim's receiving call for that agent has t_call ≤ the switch call's t_call):
  - **read (sequential):** j's switch call had seen ≥ 1 claim of i (or i's had seen ≥ 1 claim of j);
  - **in flight (crossing, HH343's literal class):** a claim of the partner existed before the switch but neither switch call had seen it;
  - **silent:** no claim of the partner existed before either switch.
  - **unaware** = in flight ∪ silent (neither mover could have read the other's move in chat).
- **Departure within K calls (H112):** after t* = t_j, agent a's project label at its K-th call after t* is its most recent strict action touch up to that call's end (carried forward; no touch = stays). a departs if that label ≠ P. K = 5 (HH343); K = 10 and 20 as variants. Work channel: a departs if its next agent work commit within 60 min is on another repo.
- **Solo switch-ins:** switch-ins with no other agent's switch-in onto P within ±15 min; same departure rule, measured from t + the median co-switch lag.
- **Output:** `G<NN>/switches.parquet` (agent, t, call, project hash, named, solo flag), `G<NN>/pairs.parquet` (pair id, agents, lag, class, named, departure flags for K ∈ {5, 10, 20}, both channels where available), `counts.json`, `_provenance.json`.
- **Regimes covered:** every non-holdout period with action touches (regimes I–III). The ledger models scheduled chat-mode calls in regimes I/II (low-confidence starts; Known issues), so regime I/II classes are a sensitivity layer; the primary scope is regime III.

## Observables
1. **Departure risk ratio RR_U** (primary): P(≥ 1 of the pair departs within K = 5 calls | unaware) / P(same | read). Mantel–Haenszel over strata period × lag bin (0–60 s, 60–300 s, 300–900 s) × kickoff-named(P); Greenland–Robins CI.
2. **RR_F** (HH343's literal contrast): in flight vs read, same strata.
3. **Mutual-leave excess M (H112):** M = P(both depart) / [P(i departs) P(j departs)] within a class; M > 1 = mutual (2-cycle signature). Compared between classes.
4. **Stick ratio S:** P(departure of the second mover | read) / P(departure | solo switch-in), MH over period × named.
5. **Unaware share u:** the share of co-switches that are unaware (an update-order descriptor per period).
6. **Phase contrast:** RR_U in own-role weeks (H93 avoidance: #42, #51 a–l) over RR_U in shared weeks (H93 βĴ > 0: #31, #33, #36, #38, #40, #41).

## Null / baseline
- **Time-shuffled null at matched lag (HH343):** permute the awareness labels within strata (period × lag bin × named), 2,000 draws; one-sided p for RR ≥ observed.
- **No coupling (J = 0) on the real skeleton:** the synthetic world W0 (below) gives the RR distribution when update order cannot matter.
- **Common project field (rival R1):** project lifetimes end for everyone at once (a goal pivot, a finished deliverable). It makes M > 1 in both classes and RR ≈ 1. The between-class comparison of M removes it.
- **Power rule:** a null RR counts as "failed" only where the synthetic power to detect RR = 2 at the period's real counts is ≥ 0.8; otherwise "inconclusive".

## Rivals and impostors
- **Rivals:** (R1) common project field: co-departures from a shared end of interest, no coupling; (R2) ferromagnetic herding (H63, H93 shared weeks): both classes stick, RR ≈ 1 with low departure; (R3) read-gated avoidance acting only after reading (sequential avoidance): the read class departs more, RR < 1.

| Impostor | Relevant? | How it is handled | Status |
| --- | --- | --- | --- |
| Scheduler field | yes | Matched lag (strata 0–60 s, 60–300 s, 300–900 s); departures counted on each agent's own call clock (H40); pairs with < K + 1 same-day calls after t* are censored. Round 1: RR_U is 1.13 [1.06, 1.20] in regime III alone. | removed |
| Exogenous field (kickoff/goal/operator) | yes | Kickoff-named projects as a stratum. The planned drop of co-switches after a human message naming P is void: human chat almost never names repos (H87). | partly |
| Shared model priors | yes | Cross-lab pairs: 1.14 [1.07, 1.22]; same-lab 1.23 [1.00, 1.50]. Pair strata (160 agent pairs with both classes): 1.11 [1.04, 1.19]. | removed |
| Contemporaneous convergence | yes | The design: read vs in flight at matched lag (RR_F 1.04 [0.80, 1.35]; 20 in-flight pairs, so underpowered). The engagement confound that the unaware/read split carries is removed post hoc by requiring a partner claim in both classes (A2). | partly |

## Synthetic validation (axis F; before any real departure statistic)
Simulator `analysis/synthetic.py`: each period's real call schedule (non-holdout `call_windows` t_call per agent) and real project count. Agents follow the H112 variant above: a switch at a call with probability p_u, a claim message posted at the switch with probability p_c (calibrated to the real claim share), read at the reader's first call with t_call > post time, touches of the current project at later calls with probability p_t (calibrated to real touch density). Worlds: **W0** J = 0; **W1** J = −2 (avoidance); **W2** J = +2 (herding); **W3** J = 0 plus a common project field (projects end for all hosts at random times, rate matched); **W4** J = −2 plus W3's field. 40 runs per world per skeleton. Report the RR_U and RR_F distributions, size (CI excludes 1 in W0 and W3), and power (CI > 1 in W1 and W4). **Decision rule fixed now:** a contrast counts as a test only if its false-positive rate is ≤ 0.10 in W0 and W3 and its power to detect the W1 effect is reported; a period whose RR_U power in W1 is < 0.8 can only be "inconclusive" on a null.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** common project field (R1), ferromagnetic herding (R2), sequential read-gated avoidance (R3).
**Locked holdout used for confirmation:** #45, #46, #47, #50 and the #51 tail (51m), frozen in `analysis/confirm.py` (dry-run on stand-ins only, not run).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Switch-ins, claims, read/in-flight classes and departures are ledger and touch fields, defined the same in regimes I–III. Limit: touch labels are noisy (a glance at another agent's site counts), so departure within 5 calls is 73–86% in both classes. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | The update-order audit is the point: 84% of co-switches are silent (no claim), 15% read, 1% in flight. True crossings are rare because read-out takes ~20 s. Departure is measured on each agent's call clock. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | The pooled RR_U beats the label-permutation null (p 0.0005) and the synthetic no-coupling band (0/40 runs CI > 1), but the excess vanishes under the engagement control (A2). No held-out likelihood. |
| D unfitted predictions | unfitted statistics and the model's signature | 0 | The 2-cycle signature is absent: mutual leaving is not higher after unaware co-switches; no departure onset at the read (#51). |
| E interventional | predicts the change across a natural experiment | 0 | The phase contrast (avoidance weeks vs herding weeks) goes the wrong way (0.88). The #44 assigned arm has no read pairs. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | 7 worlds × 4 real skeletons × 40 runs: size 0 for CI > 1; a planted RR 2 is recovered (1.84, power 1.0 pooled); RR_F, M and S are not identified (A1). |
| G ground truth | agrees with known structure | 1 | #44's assigned #best co-switches are all unaware (no chat needed to join an assigned task); the #51 avoidance found by H93 does not show as update-order departures. |
| H comparative | beats the named rivals | 0 | R1 (common project field plus engagement) explains the data; HH343 and the read-gated avoidance model (RR_U < 1) both fail. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Holdout not run. RR_U > 1 (point) in 7/9 testable periods, but the excess is engagement. |

## Prediction
*Written 2026-10-04 21:30 UTC, before running the analysis on real data.*

**What I had seen when writing this:** the cards of H93 (βĴ < 0 in #42 and #51; positive in shared weeks), H63, H57, H104, H18 and H40; the shared-module docs. To check feasibility I counted, on non-holdout days, action switch-ins and co-switch pairs per period (e.g. #51: 10,884 switch-ins, 2,623 pairs within 15 min; #31: 837 and 547; #42: 93 and 9) and the awareness classes of those pairs (in flight is rare: 1–18 per period, ~60 in all; read 2–431; silent the rest), and claim-based co-switch pairs (235 read, 29 crossing; median lag 113 s vs 4 s). No departure, mutuality or risk-ratio statistic was computed.

**Periods and roles.** Replication (`replication`), primary channel action touches: every non-holdout period with ≥ 30 co-switch pairs and ≥ 5 pairs in each of the read and unaware classes. From the counts this is about #18, #19, #24, #26, #30, #31, #33, #36, #37, #38, #39, #40, #41, #44 and #51 (51a–l); others are descriptive. Natives (`native`): **G51** (the avoidance week with the most pairs: mutuality and the post-read onset), **G42** (the other avoidance week; descriptive by count, used in the phase contrast), **G44** (assigned #best vs self-chosen #rest on the same days).

**Testability rule (fixed now).** A period is testable if it has ≥ 30 co-switch pairs with both agents uncensored at K = 5 and ≥ 5 pairs in each of read and unaware. The HH-literal contrast (in flight vs read) is testable only in pools (pooled over periods by MH with period strata; exception (d) is named because in-flight pairs number 1–18 per period).

| ID | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| P1 (HH343 core) | RR_U ≥ 2 with CI > 1, pooled over testable periods (MH, period × lag × named strata) | RR_U CI includes 1 (powered) or RR_U < 1 | 0.15 |
| P1′ (HH343 literal) | RR_F ≥ 2 with CI > 1, pooled | RR_F CI includes 1 (powered) | 0.10 |
| P2 (2-cycle) | mutual leaving: M_unaware > 1 with CI > 1, and M_unaware > M_read | M_unaware CI includes 1, or M_unaware ≤ M_read | 0.25 |
| P3 (sequential sticks) | S = P(second mover departs \| read) / P(departs \| solo) < 1 with CI < 1, pooled | S ≥ 1 | 0.40 |
| P4 (phase sign) | RR_U in own-role weeks (#42, #51) ≥ 1.5 × RR_U in shared weeks | ratio < 1.5 | 0.25 |
| P5 (per-period replication) | RR_U > 1 (point estimate) in ≥ 2/3 of testable periods | ≤ 1/2 | 0.30 |
| Kill (HH343) | departure rates equal within CI: pooled RR_U CI includes 1 with synthetic power ≥ 0.8 at RR = 2 | — | P(kill) 0.65 |

**Verdict rules (fixed now).** Per period: *supported* if RR_U ≥ 2 with CI > 1; *failed* if the RR_U CI includes 1 and the period's W1 power ≥ 0.8, or RR_U < 1 with CI < 1; *mixed* if RR_U > 1 with CI including 1 and power ≥ 0.8 is not met in either direction; *descriptive* if not testable. Card: supported if P1 and P2 hold; failed if the kill is met; mixed otherwise.

Per-period predictions are in each `goalperiod-subhypotheses/G<NN>/README.md`, written before that period is run.

**Amendment A1 (2026-10-04 21:49 UTC, after the synthetic validation, before any real departure statistic).** What I had seen: the synthetic summaries (`data/processed/H112-crossing-claims-two-cycles/synthetic/summary.json`; skeletons G18, G31, G38, G51c–d; 40 runs per world) and the real per-period pair and class counts (`G<NN>/counts.json`, listed in the build log). No real departure rate, RR, M or S.
- **Two worlds added before data** (W5, W6): agents also learn a project's current hosts when they touch it, so unaware co-switchers discover each other after the move. W5 (J = −2) is the HH343 world (a Little 2-cycle); W6 (J = 0) is its size check. A read-out-triggered update (probability 0.3 at a call that read news) is part of every world.
- **What the pipeline reads in each world** (pooled MH over the four skeletons): no coupling W0/W3/W6: RR_U median 0.90–1.02, CI > 1 in 0/40 runs, CI < 1 in 0–12.5%. Avoidance W1/W4/W5: RR_U 0.79–0.90, CI < 1 in 15–38%. Herding W2: 0.95. **No world produces RR_U ≥ 2.** Under read-gated avoidance the *read* pairs depart more: the first mover reads the second mover's claim and leaves, while most unaware pairs (silent) never learn of each other.
- **Power for HH343's effect:** a planted RR = 2 on the W0 frames (unaware departures at twice the stratum's read rate, capped at 1) is recovered as a median pooled RR 1.84 with CI > 1 in 40/40 runs. The pooled P1 test is powered (≥ 0.8). Per period, base departure rates of 0.2–0.7 cap RR at 1/p, so RR ≥ 2 is reachable only where read pairs depart < 50%.
- **Consequences (no prediction or credence changed):**
  1. P1 (RR_U ≥ 2) and the kill stand as written; the kill is powered in the pool.
  2. RR_U < 1 is not interpretable alone: its false-positive rate reaches 0.125 under no coupling (W0). It is reported against the synthetic null band, not as avoidance.
  3. **P1′ (RR_F) is descriptive only:** in-flight pairs are 0 in the median synthetic run and 26 in all real periods together.
  4. **P2 (mutual-leave excess M) is descriptive only:** M is 0.85–1.9 in every world, including no coupling (shared agent-day activity), and does not separate the worlds.
  5. **P3 (stick ratio S) is not a test:** under no coupling S has CI < 1 in 35–62% of runs on the G31 and G51 skeletons (second movers depart less than solo switch-ins for reasons unrelated to reading). S is reported descriptively.
  6. P4 and P5 stand; P4 reads RR_U only against P1's direction.

**Amendment A2 (2026-10-04 21:57 UTC, post hoc, after the first real run; disclosed).** Two checks added after seeing that silent pairs depart at 86% and read pairs at 73%: (a) the engagement control: restrict to pairs where a partner claim naming P exists within ±15 min of either switch (`claim_i | claim_j`), and to pairs where both movers claimed (`claim_i & claim_j`); (b) risk differences beside the risk ratios, because a base rate near 0.75 caps any RR at ~1.35. Neither changes P1–P5, the kill or the verdict rules; both enter the confirmatory design (C2, C3).

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | mixed | 50 pairs; RR_U 0.82 [0.33, 2.07]; read 0.36, silent 0.24 |
| [G26](goalperiod-subhypotheses/G26/README.md) | replication | mixed | 41 pairs; RR_U 1.03 [0.55, 1.93] |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | mixed | 63 pairs; RR_U 1.22 [0.78, 1.92] |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | mixed | 201 pairs; RR_U 1.55 [1.04, 2.30]; read 0.50, silent 0.81 |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | mixed | 180 pairs; RR_U 1.16 [0.91, 1.48] |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | mixed | 62 pairs; RR_U 1.46 [0.97, 2.21] |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | mixed | 56 pairs; RR_U 0.86 [0.61, 1.22] |
| [G44](goalperiod-subhypotheses/G44/README.md) | native (also replication) | mixed | 87 pairs; RR_U 1.22 [0.79, 1.87]; #best arm: 12 pairs, 0 read (no contrast) |
| [G51](goalperiod-subhypotheses/G51/README.md) | native (also replication) | mixed | 1,487 pairs; RR_U 1.12 [1.05, 1.20]; post-read onset 0.79 [0.37, 1.64] (failed); phase ratio 0.88 (failed) |
| [G42](goalperiod-subhypotheses/G42/README.md) | native | descriptive | 7 pairs, all silent |

## Results
*Exploratory round 1, 2026-10-04 21:57 UTC, non-holdout days only.*
- **Code:** `scheme/h112scheme.py`, `scheme/build.py`; `analysis/h112lib.py` (MH risk ratios, permutation null, M, S, DL pool), `synthetic.py`, `run.py`, `natives.py` (G44, G51 and A2), `score.py` (estimates, figures), `confirm.py` (frozen, dry-run only).
- **Data:** `data/processed/H112-crossing-claims-two-cycles/` (`G<NN>/` switches, pairs, solo and work pairs; `synthetic/`; `results/`; `confirm_dryrun/`; `_provenance.json`; ~2 MB).
- **Figures:** [`figures/summary_obs.pdf`](figures/summary_obs.pdf) (RR_U per period, pooled, engagement-controlled, in flight; departure rates by class), [`figures/summary_synth.pdf`](figures/summary_synth.pdf) (RR_U by synthetic world).
- **Estimates:** 70 rows in `per_period_estimates` (`crossing_departure_rr_unaware_vs_read`, `crossing_departure_rate_read|silent`, `crossing_post_read_departure_ratio`).

**Outcome vs prediction**

| Prediction | Outcome | Verdict |
| --- | --- | --- |
| P1 RR_U ≥ 2 with CI > 1, pooled | 1.15 [1.08, 1.22] (9 periods, 2,227 pairs; permutation p 0.0005) | failed |
| P1′ RR_F ≥ 2 (literal crossing) | 1.04 [0.80, 1.35] (20 in-flight pairs) | failed (descriptive, A1) |
| P2 mutual leaving after unaware co-switches | M_unaware 1.07 [1.04, 1.10] < M_read 1.19 [1.10, 1.29] | failed (descriptive, A1) |
| P3 sequential sticks (S < 1) | S 0.70 [0.63, 0.77], but S < 1 arises without coupling (A1) | not a test |
| P4 own-role RR_U ≥ 1.5 × shared | 1.12 vs 1.27; ratio 0.88 [0.73, 1.06] | failed |
| P5 RR_U > 1 in ≥ 2/3 of testable periods | 7/9 | supported |
| Kill: departure rates equal within CI (powered) | not met: CI excludes 1, but A2 removes the excess | not met by the letter; met in substance after A2 |
| N G51 post-read onset > 1 | 0.79 [0.37, 1.64] | failed |
| N G44 free ≥ assigned arm | #best has no read pairs | descriptive |
| A2 engagement control (post hoc) | any partner claim: 1.02 [0.92, 1.13] (577 pairs); both claimed: 0.88 [0.51, 1.52] (90) | — |

**Sensitivity.** K = 10: 1.06 [1.01, 1.12]; K = 20: 1.03 [0.99, 1.07] (the excess fades within ~10 calls). Regime III only: 1.13 [1.06, 1.20]. Work channel (DQ4 commits, 119 pairs): 0.99 [0.84, 1.18]. Risk difference unaware − read: +0.14 [+0.09, +0.19].

**Synthesis.**
1. **True crossings are rare.** Only 1% of co-switches have a partner claim in flight at the switch; 84% are silent (no claim at all). Read-out takes ~20 s, so two agents rarely post about the same project inside one read-out window.
2. **There is no 2-cycle.** After unaware co-switches agents do not leave more mutually, do not leave after reading the partner's claim, and do not leave more in the weeks where H93 found avoidance.
3. **The raw excess is engagement.** Silent pairs depart more because a project nobody wrote about is usually a glance (a URL visit), not a join. Matching on the existence of a partner claim removes the whole excess.
4. **The Little-model prediction was mis-signed for this system.** On the real call schedules a read-gated avoidance model gives RR_U ≈ 0.8: the first mover reads the second mover's claim and leaves, while silent pairs never learn of each other. HH343's "sequential sticks, crossing leaves" needs agents to learn of each other without reading, which the synthetic artifact-awareness world (W5) also failed to produce at village sampling.

**Claim that stands:** Co-switch departures do not depend on whether the movers had read each other once chat engagement is matched (RR 1.02 [0.92, 1.13], 577 pairs, 9 periods); HH343's 2× crossing effect and 2-cycle are absent (raw RR 1.15 [1.08, 1.22]). Exclusions: P1′ and P2 descriptive (in-flight pairs 20; M not identified), P3 not a test (S biased), the engagement control is post hoc (A2).

## Confirmatory design (frozen 2026-10-04 in `analysis/confirm.py`; dry-run on stand-ins only, NOT RUN)
Targets #45, #46, #47, #50 and the #51 tail (51m); #48 and #49 reported, not scored. **C1:** pooled RR_U upper 95% bound < 2. **C2:** with a partner claim present, RR_U's CI includes 1 and its point estimate lies in [0.8, 1.25]. **C3:** over all pairs RR_U > 1 with CI > 1, and no-claim pairs depart at least as often as claimed unaware pairs. **C4:** #51-tail post-read departure ratio ≤ 1.5. Dry run (stand-ins #38, #41, #44 and units 51h–51l; 484 pairs): C1–C4 pass (a pipeline check, not evidence). Guard: `--confirm --i-understand-this-uses-the-locked-holdout`, a committed H112 folder, `holdout_ledger.check()` (family `update_order_departure`). Reuse: H93 (`project_potts`), H94, H77/H78 plan #45–#47, #50 and the #51 tail on project choice; H112's statistic (departures by read class) is different but shares the choice events, so disclose.

## Round 2 redirects (proposed by the round-1 agent, 2026-10-04)
- **H112-R1. Measure joins, not touches.** Use DQ4 commits or a ≥ 2-touch rule so that departure rates fall below 50% and a 2× effect becomes reachable; the work channel had only 119 pairs.
- **H112-R2. Crossings by design.** Pool the 26 in-flight pairs with the holdout and other villages (Q7); a literal crossing test needs several hundred in-flight pairs (size it on the synthetic first).
- **H112-R3. Read-gated avoidance's own sign.** The model predicts that the *first* mover leaves after reading the second mover's claim; test first-mover vs second-mover departures in read pairs in #42 and #51.

## Notes
- 2026-10-04 21:30 UTC: round-1 agent (H112 together with H113). Card written before any departure statistic; feasibility counts listed above.
- 2026-10-04 21:49 UTC: A1 after the synthetic. 21:55 UTC: replication and natives run. 21:57 UTC: A2 (post hoc) and results. Compute: ≤ 2 threads, one job at a time, no LLM labels.
