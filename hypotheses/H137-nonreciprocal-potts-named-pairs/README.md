# H137: Nonreciprocal Potts: project hops break detailed balance only along named pairs

**Status:** pre-registered (not run). Card, observables, nulls, predictions and kill rules written 2026-10-07 from HH380 (approved by Vivian 2026-10-07), before any H137 statistic on real data. No scheme, synthetic or analysis code exists yet.
**Question (GOALS.md):** **Q1** (what couples agents: does a directed name make the named agent follow the namer's project?). Second: **Q6** (thermodynamics: is the irreversibility of project hopping carried by named pairs, as H90 found for talk?).
**Fields:** stat mech (nonreciprocal kinetic Potts, directed couplings), stochastic thermodynamics (pair currents, Schnakenberg affinities, AIK bound), sociophysics (following and leadership)
**Literature:** [Aguilera, Ito & Kolchinsky 2026](../../literature/aguilera-2026-entropy-production-nonequilibrium-maxent.md) (EP lower bound from antisymmetric observables; θ_ij − θ_ji ≈ β(w_ij − w_ji) in a kinetic Ising model with asymmetric couplings); [Kolchinsky, Dechant, Yoshimura & Ito 2026](../../literature/kolchinsky-2026-generalized-free-energy-excess-housekeeping.md) (pair currents and housekeeping). Cited from memory (†): Schnakenberg, *Rev. Mod. Phys.* 48, 571 (1976)† (edge affinities); Fruchart, Hanai, Littlewood & Vitelli, *Nature* 592, 363 (2021)† (nonreciprocal phase transitions).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime; **Interaction (addressed)** with H90's naming weights (`chat_mentions_clean.mentions_roster`, agent speakers only); **Exposure (ledger receiving call)**; **In-flight placebo (matched-lag)** (H67); **Entropy production / irreversibility** in H90's named variant **entropy production (AIK cross-agent bound on categorical states)**; H90's **address-split collective EP σ_nam / σ_un** (proposed there); **Agent state (categorical, project/artifact strict)** (H11); from H129 (proposed there) **project hop (H129)**; from H133 (proposed there) **agent state (categorical, project per call)** and **project hop (call)**. New named variants proposed for DEFINITIONS.md (not edited there; defined under Data scheme and Observables): **follow hop**, **read-named follow hop**, **naming class (one-way, mutual, none)**, **oriented pair follow asymmetry A_ij**, **pair follow EP σ_ij**, **follow-direction coefficient θ_name**.
**From:** HH380 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/10-potts/` (kinetic Potts with directed couplings), `physics-models/02-nonequilibrium-ising/` (asymmetric couplings break detailed balance), `physics-models/15-stochastic-thermodynamics-selection/` (pair EP inference)

## Source HH (verbatim from the HH list)
- **HH380 · Nonreciprocal Potts: project hops break detailed balance only along named pairs.** H90 found the collective arrow of time only in named talk. A kinetic Potts model with directed couplings, only from named senders, makes the pair hop flows asymmetric where naming is one-way.
  - *Prediction:* the joint hop current between agents i and j (i moves to j's project after j named i) is asymmetric when naming is one-way and symmetric when naming is mutual or absent. The pair EP is positive only for named pairs.
  - *Check:* H129 hop sequences; H67 name graph; AIK pair EP (model 15).
  - *Kill:* the pair asymmetry is the same for named and unnamed pairs.
  - *Impostors:* leaders both get named and attract hops. Condition on the target agent's popularity.
  - *Models:* 10, 02, 15 · *Builds on:* H90, H129, H67

## What this card builds on (latest round of each cited card)
- **H90 (round 1, 2026-10-04):** in G51 the collective talk arrow sits entirely on named partners: σ_nam = 7.6 [4.3, 11.2]×10⁻³ nats/min, σ_un = −0.4 [−1.7, 0.5]×10⁻³, address contrast 8.0 [5.1, 12.1]×10⁻³ (block-shift p = 0.01). **Its pairwise native (N2) failed:** per-pair θ signs do not follow the naming direction (sign agreement 0.52 vs null q95 0.55; Spearman of |θ| with naming 0.08 vs null q95 0.16), because naming is mostly reciprocal. Power at G51's effect size is ≤ 0.05 in 5-day periods and 0.45 in G38. A lagged common field passes the block-shift null in 63–100% of synthetic worlds; only the address split separates coupling from lagged fields.
- **H129 (round 1, 2026-10-04):** project hops carry no circulation beyond age drift (0/9 shared unit-channels; power 0.55–0.97 at 2 nats). Net flow to newer projects is small but consistent (m_2 > 0 in 30/37). Work hops number 2–120 per period outside #51.
- **H67 (round 2, 2026-10-05):** in regime III a read message that names the recipient adds 0.079 [0.069, 0.089] talk calls per read; an unnamed one adds 0.004 [0.003, 0.006] (×19).
- **H11 (round 2, 2026-10-05):** joins follow a time-symmetric co-arrival kernel (lag − lead ≈ 0): agents arrive at a project in the same hour, not after earlier activity. Read chat predicts joins better than artifact activity.
- **H06 (rounds 1 and 1b):** in free weeks only 0.23–0.53 of project switches go to a project another agent holds; the copying that exists follows what agents have read.

## Question
When agent j names agent i and i does not name j back, does i move onto j's project more often than j moves onto i's? And is the pair's follow current balanced when naming is mutual or absent, so that the irreversibility of project hops lives only on one-way named pairs?

**Practical payoff:** if a one-way name makes the named agent follow, an operator can recruit an agent to a project by having a project member name it. If following is symmetric whatever the naming, names do not steer allocation, and H90's talk arrow does not reach the work.

## Model
**From:** `physics-models/10-potts/`, `physics-models/02-nonequilibrium-ising/`, `physics-models/15-stochastic-thermodynamics-selection/`.

**H137 variant: a kinetic Potts walker with directed, read-out couplings.** At its call c agent i hops (H133's update) with destination utility
u_b = κ_b + Σ_j J_{i←j}(c) · 1[σ_j(c) = b] + habit + share,
with J_{i←j}(c) = J · ln(1 + R_{i←j}(c)), where R_{i←j}(c) counts the messages by j that name i and that i read in its last 10 calls (ledger). Couplings exist only from named senders, so J_{i←j} ≠ J_{j←i} where naming is one-way. A walker with J_{i←j} ≠ J_{j←i} breaks detailed balance on the pair's joint state: the current "i joins j" exceeds "j joins i" in the direction of the naming.
- **H137 says:** in one-way named pairs the follow current runs from the namer's project to the named agent (i follows j); in mutual and unnamed pairs it is symmetric; the pair EP is above its null only in one-way pairs.

**Rivals.**
- **R-popularity (strongest rival; the HH's impostor):** popular agents are named more and attract more joins. Direction follows popularity, and naming adds nothing once popularity is held fixed.
- **R-co-arrival (H11):** pairs arrive at projects in the same hour in random order. The follow current is symmetric in every class.
- **R-broadcast following:** i follows any agent whose messages it reads, named or not (J on all reads). Asymmetry then tracks read volume, not naming.
- **R-reciprocal (H90 N2):** naming is mostly mutual, so one-way pairs are too few to carry a current.

## Data scheme (`scheme/`)
`scheme/build.py` writes `data/processed/H137-nonreciprocal-potts-named-pairs/` from shared tables only.
- **Inputs:** per-call project labels from the shared builder `infra/shared/project_calls.py` (proposed by H133; attention channel, primary for counts); `project_states` (W = 30; H129's attention hops, variant); DQ4 `work_commits` through `infra/shared/replicator_hosts.py` (work hops, variant); DQ1 `call_windows`, `context_ledger_items` (sender, `ment`); `chat_core` and `chat_mentions_clean` (naming weights; in-flight messages); `rooms_timeline`, `calendar`, `period_units`, `roster`. No message text.
- **Follow hop (proposed variant):** agent i's project hop at call c onto project b, where b is the current project of at least one other present agent j at t_call(c). The hop counts for each such j with weight 1 / n_b(c), n_b(c) the number of other agents on b.
- **Read-named follow hop (proposed variant):** a follow hop of i onto j's project at which i had read ≥ 1 message by j naming i in its last 10 calls (ledger receiving calls).
- **Naming weights:** w_ji = agent messages by j whose `mentions_roster` contains i, per unit (H90's rule). Variant: leading-@ targets (STANDARDS §2; H90-R3).
- **Naming class (proposed variant), per unordered pair and unit:** *one-way* if max(w_ji, w_ij) ≥ 3 and min ≤ max / 3 (the namer is the larger side); *mutual* if both ≥ 3 and within a factor 3; *none* if both are 0; other pairs are *weak* and are left out of the class contrasts.
- **Popularity (impostor control):** pop_j = follow hops onto j's projects by agents other than the pair (leave-pair-out), and j's naming in-degree (messages naming j from agents other than the pair).
- **In-flight named messages:** messages by j naming i posted in the hop call's latency window (t_call(c), t_call(c) + d_c], d_c clipped to [1, 120] s (H67's rule). Call c cannot read them.
- **Output:** `follows.parquet` (unit, hopper, target agent, call, weight, read-named flag, in-flight flag, room match), `pairs.parquet` (unit, pair, w_ji, w_ij, class, F_{i←j}, F_{j←i}, popularity terms), `results/`, `synthetic/`, `_provenance.json`. Agent ids only; project names hashed. Expected < 20 MB.
- **Regimes covered:** I, II and III where per-call labels exist; the read-named version needs the ledger (all regimes). Reserved rows are dropped with the shared reserved-row mask in `infra/shared/common.py`.

**Structural precondition (counted before any outcome):** a unit is testable if it has ≥ 20 follow hops within one-way pairs and ≥ 8 one-way pairs with ≥ 1 follow hop. Units below it enter only the pooled fit.

## Observables
- **O1 · Oriented pair follow asymmetry A_ij (one-way pairs):** A = ln[(F_{named←namer} + ½) / (F_{namer←named} + ½)], with F the weighted follow counts. Mean over one-way pairs, pair-bootstrap CI.
- **O2 · Follow-direction coefficient θ_name (primary; the HH's impostor control):** over all follow hops between members of classified pairs, logit P(the hop is "i joins j") = θ_name · z_ij + δ · [ln pop_j − ln pop_i] + ε · [ln indeg_j − ln indeg_i] + unit effects, with z_ij = +1 if j names i one-way, −1 if i names j one-way, 0 for mutual and none. H137: θ_name > 0.
- **O3 · Pair follow EP σ_ij:** σ_ij = (F_{i←j} − F_{j←i}) · ln[(F_{i←j} + ½)/(F_{j←i} + ½)] per pair (Schnakenberg edge term). Class means σ_one, σ_mutual, σ_none, each against its direction-flip null. Secondary: H90's cross-fitted Newton bound on the antisymmetric follow observable g_ij = 1[i joins j] − 1[j joins i], per class.
- **O4 · Read-out timing:** the follow rate onto j's project after a read named message from j, against the same rate after an in-flight named message from j (matched lag).
- **O5 · Class counts (descriptive):** the number of one-way, mutual and none pairs per unit and their follow-hop totals. This tests R-reciprocal directly.

## Null / baseline
- **N1 · Direction-flip null:** each follow hop between i and j is assigned to i←j or j←i with probability ½, keeping each pair's total. 2,000 draws; for O1 and O3.
- **N2 · Class permutation within popularity strata:** permute the naming classes across pairs inside quintiles of |ln pop_j − ln pop_i|. 2,000 draws; for O2 and the class contrast in O3.
- **N3 · Synthetic worlds** (below) for size and power at real counts.
- **Strongest rival:** R-popularity. It predicts θ_name ≈ 0 once δ and ε are in, and a raw O1 > 0 that the controls remove.

## Impostors (STANDARDS §1)
| Impostor | Relevant? | How it is handled | Status |
| --- | --- | --- | --- |
| Scheduler field | partly | Follow hops are ordered events on the call clock. Agents who start their day together co-arrive (H11); the direction of a pair's hops, not their timing, is the statistic, and N1 keeps the pair totals. | planned (partly) |
| Exogenous field (kickoff, goal, operator) | yes | A kickoff-named project pulls everyone in one direction (from old to named). Hops in the first 4 active hours after each kickoff and hops onto kickoff-named projects are a dropped variant. | planned (partly) |
| Shared model priors | partly | Same-lab pairs may both name and follow each other. θ_name is reported for same-lab and cross-lab pairs. | planned (partly) |
| Contemporaneous convergence | yes | O4 compares read named messages with in-flight named messages at matched lag. | planned |
| (HH impostor) Leaders get named and attract hops | yes | Popularity and naming in-degree in O2; class permutation within popularity strata (N2). | planned |

## Design: two layers (STANDARDS §4)
**Unit of analysis:** one goal period, split at `period_units`; #51 units separately. Few follow hops per unit are expected, so θ_name is also fitted by hierarchical partial pooling (unit-specific θ with shrinkage), reported next to the per-unit values (exception (d)). No complete pooling.
- **Replication (role `replication`):** every non-reserved unit that meets the precondition. Candidates: shared-goal weeks G30, G31, G33, G35, G36, G37, G38, G40, G41, G44; own-role weeks G39, G42 and units 51a–51l (follow hops expected rare: H94 found ownership carries 0.79–0.95 of #51's allocation information); regime-I herding weeks with project labels (G13, G18, G19, G24, G25, G26; H11).
- **Natives (role `native`):**
  - **N1 · G51 pooled over 51a–51l (the largest naming graph).** The direct comparison with H90's failed talk-channel pair test (N2): if the project channel shows the naming direction that talk did not, the coupling acts on work, not on talk timing.
  - **N2 · G38 rooms.** Rooms route reading. Same-room one-way pairs should carry the asymmetry; cross-room one-way pairs (rarely read) should not.
  - **N3 · G44 #best vs #rest (descriptive).** The assigned #best room's hop graph is a tree (H129). Follow currents in #best should run toward the assigned repo regardless of naming; in #rest any asymmetry should follow naming.
- **Reserved (confirmation only; never read in exploration):** #43, #45–#50 and the #51 tail (2026-09-07 → 09-21), plus the regime-I and II reserved periods (#1, #9, #14, #15, #22, #28, #29, #32, #34). A frozen `analysis/confirm.py` on #45–#47 and the #51 tail is written after round 1 and runs only with Vivian's sign-off. Families `entropy_production`, `project_potts`; disclose reuse with H90, H129, H93, H133.

## Synthetic validation plan (axis F; run before any real-data statistic)
`analysis/synthetic.py` on the real skeletons of G38, G31 and two #51 units: real agents, call clocks, read sets with naming flags, project availability, naming weights. 300 runs per world.
- **W0 no following:** destinations by project share and habit.
- **W1 H137:** directed coupling from read named messages, J = 1.0 and 0.5 on the log-odds scale.
- **W2 popularity:** destinations favor projects of popular agents (log-odds 1.0 per e-fold of popularity), with popularity correlated with naming in-degree as observed. No naming effect.
- **W3 co-arrival (H11):** pairs arrive at a project within the same hour in random order.
- **W4 broadcast following:** coupling from every read message of j, named or not.
- **Read:** the size of O2 (θ_name > 0) and of the O3 class contrast in W0, W2, W3 and W4; their power in W1 at J = 1.0 and 0.5; the size of O1 without controls in W2 (how much the raw asymmetry popularity alone makes).
- **Pass rule:** a statistic is a test where its size is ≤ 0.10 and its power at J = 1.0 is ≥ 0.8 on the pooled real counts. Otherwise it is descriptive, by a dated amendment written before any real-data statistic. If the pooled power at J = 1.0 is < 0.8, the HH is untestable at village counts and the card says so before outcomes.

## Prediction
*Written 2026-10-07, before any H137 statistic on real data. What I had seen: the cards of H90, H129, H67, H11 and H06 at their latest rounds (numbers above). No follow hop, naming class count or pair asymmetry had been computed.*

| ID | Prediction | Counts against | Credence |
| --- | --- | --- | --- |
| S0 (precondition) | ≥ 1 unit passes the precondition, and the pooled power at J = 1.0 is ≥ 0.8 | neither | 0.4 |
| P1 (HH) | **One-way naming makes a current.** Pooled θ_name > 0 with CI > 0, with popularity and in-degree controls, and the N2 p < 0.05 | θ_name CI ∋ 0 at power ≥ 0.8 | 0.2 |
| P2 (HH) | **Symmetric otherwise.** σ_mutual and σ_none inside their direction-flip nulls in ≥ 2/3 of testable units | beyond the null in > 1/3 | 0.6 |
| P3 (HH) | **Pair EP only on named pairs.** σ_one − σ_none > 0 with CI > 0 (pooled) | CI ∋ 0 at power ≥ 0.8 | 0.2 |
| P4 | **At the read-out call.** Follow rate after a read named message > after an in-flight named message (CI of the difference > 0) | CI ∋ 0 or below | 0.25 |
| P5 | **Few one-way pairs (R-reciprocal, descriptive check).** One-way pairs are < 1/3 of classified pairs in most units | ≥ 1/2 | 0.6 |
| N1 | G51 pooled: θ_name > 0 with CI > 0 | CI ∋ 0 | 0.15 |
| N2 | G38: same-room one-way pairs show θ_name > 0; cross-room do not | no same-room effect | 0.2 |
| N3 | G44: descriptive | none (descriptive) | none |

**Kill rules (from the HH, sharpened).**
- **Kill (HH):** the class contrast σ_one − σ_none and θ_name both have CIs that include 0, at a pooled synthetic power ≥ 0.8 for J = 1.0. The pair asymmetry is then the same for named and unnamed pairs, and H137 fails.
- **Kill (popularity):** raw O1 > 0 but θ_name's CI includes 0 once popularity and in-degree are in. The asymmetry is then leadership, not naming.
- **Untestable:** S0 fails. The verdict is then "untestable at village counts" for the exploration data, stated before any outcome.

**Verdict rule.** *Supported:* P1, P2 and P3 hold, and P4 holds. *Narrowed ("one-way naming orients joins, not at the read-out call"):* P1 and P3 hold, P4 fails. *Failed:* either kill fires. *Inconclusive:* S0 fails, or the tests are unpowered.

**My credence before data:** supported 0.05; narrowed 0.1; failed 0.35; inconclusive 0.5. The main reasons for doubt: H90's talk-channel pair test already failed because naming is mostly mutual, H11 finds co-arrival rather than following, and project hops are few.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R-popularity (leaders), R-co-arrival (H11), R-broadcast following, R-reciprocal (H90 N2).
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
No period has been run. Period folders (`goalperiod-subhypotheses/G<NN>/`) are created with their dated predictions before each run. `goalperiod-subhypotheses/GNN/` is the unfilled template.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| replication units (precondition list) | replication | pending | not run |
| G51 (51a–51l pooled) | native N1 | pending | not run |
| G38 | native N2 | pending | not run |
| G44 | native N3 (descriptive) | pending | not run |

## Results
Not run.

## Notes
- 2026-10-07: card written from HH380 (approved by Vivian 2026-10-07). Round-1 order: structural counts (follow hops by class; no direction) → precondition note → period READMEs with dated predictions → synthetic → dated amendments → replication and natives → estimates rows (`h137_theta_name`, `h137_pair_ep_oneway`, `h137_pair_ep_none`, `h137_follow_read_vs_inflight`) → frozen `confirm.py` (dry run only).
- The HH's "i moves to j's project after j named i" is implemented twice: with static per-unit naming classes (HH-literal, O1–O3) and with read named messages at the hop call (O4, read-named follow hop).
- Compute: ≤ 2 threads, one heavy job at a time (STANDARDS §9).
