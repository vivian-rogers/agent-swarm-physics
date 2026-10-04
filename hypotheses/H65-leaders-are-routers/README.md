# H65: Leaders are routers, not sources

**Status:** exploratory round 1 **done (2026-10-04): mixed. Leaders are attention hubs, not content routers; the elected leader is a content source.** Design, observables, nulls, rivals and predictions written 2026-10-04 19:35 UTC; Amendment A1 (synthetic) ~21:15 UTC; both before any H65 outcome statistic.
- **No router calls** in the four leader natives under the primary embedding (1 of 12 native × model runs: #35 under gte only).
- **Attention, yes:** designated leaders receive +0.39 more agent replies per statement than on their other days (#35, permutation p 0.005); judges +0.45 (#12, p 0.007) and they answer more distinct agents (+0.16 breadth, p 0.003); the elected leader ranks 0.89 in replies received (#26).
- **Content inflow, no:** the role changes the leader's read-gated susceptibility χ by +0.09 (#35, p 0.18; gte +0.18, p 0.009) and −0.03 (#12 judges). **The elected leader (#26) is a content source:** outflow percentile 1.00 / 0.89 / 0.89 (bge / gte / style) against a skeleton-null mean of 0.32, inflow percentile 0.11–0.22.
- **Replication (46 units):** answering is absorbing (ρ(reply-out share, χ) median +0.29, 36/46 > 0, sign p 0.0002, all three embedding variants), but attention is not aligned with either inflow or outflow (D_p median −0.04, 17/40 > 0). The unread in-flight term carries 0.61 of the read response (co-response).
- Scorecard A1 B1 C1 D1 E1 F1 G1 H1 I0. `analysis/confirm.py` (#45 leader, #28) frozen and dry-run, **not run**.
**Fields:** sociophysics, info theory, stat mech
**Question served:** **Q1** (what couples agents?): which way does coupling run around a designated leader: out of it (source) or into it (aggregator)? **Q5** second: an operator who installs or elects a leader needs to know whether it broadcasts or only collects.
**Literature:** none of the notes in `literature/` covers leadership or brokerage. Cited from memory (†, not in `literature/`): Freeman, *Sociometry* 40, 35 (1977)† (betweenness: brokers sit on paths); Burt, *Structural Holes* (1992)† (brokers aggregate non-redundant information); Leavitt, *J. Abnorm. Soc. Psychol.* 46, 38 (1951)† (centralized nets route messages through the hub); Schreiber, *PRL* 85, 461 (2000)† and Barnett, Barrett & Seth, *PRL* 103, 238701 (2009)† (transfer entropy and Granger causality for directed information flow).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime; Driving / external field (goal, kickoffs, human messages); Agent state, vector variant (whitened statement embedding, 32-d; bge-small primary, gte-modernbert second, style-residualized-per-period third); Exposure (turn read-out) as implemented by the context ledger (DQ1); Interaction, variant reply (DQ2 parents); H32's *content transfer* (as a cross-check only). New terms defined below and proposed for the shared file: **read-gated susceptibility χ (content inflow)**, **read-gated influence κ (content outflow)**, **reply-out share and breadth**, **reply-in rate**, **router index ρ_R**.
**From:** HH264 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` ("Making the faithful ones better") · **Models:** `physics-models/02-nonequilibrium-ising/` (directed couplings; in- vs out-strength), `physics-models/04-semantic-information/` (where information flows) · **Faithfulness lever:** G (DQ6 leaders as ground truth).
**Data inputs (shared tables first):** DQ1 context ledger (`call_windows`, `context_ledger_items`), DQ2 `reply_pairs` (`pair_set = cand`, labelled), DQ5 statement vectors (`statements_white32_<model>`, `statements_style_resid_period32_bge_small`) and goal fields (`goals.parquet`, `goal_vectors*`), DQ6 `ground_truth_labels` (`leader`, `judge`, `team`, `phase`; `preferred & ~holdout`), `chat_core`, `period_units`, `roster`. H32's per-period outputs (`data/processed/H32-information-current-leaders/r1b/`, read-only) for the cross-check R4.

## Question
H32 found that elected, designated and installed leaders are not content sources. HH264 asks what they are instead. The router picture: a leader reads and answers everyone (many inbound reports, broad replies), its own statements follow what it reads (high content inflow), and its messages do not move what others say next (low outflow). Leadership in agent swarms would then be aggregation, not broadcasting. The rival pictures: the leader is a source after all on a per-message basis (H32 measured total outflow, which penalizes quiet agents), or the leader is simply an attention target with no special content role.

## Design: two layers (Vivian, 2026-10-04; see `infra/data-quality/QUEUE.md`)
- **Replication:** the common estimator on every eligible goal period: per agent, content inflow χ and outflow κ (read-gated linear response) and reply-in / reply-out rates. The period statistic is how attention (reply-in) aligns with inflow vs outflow. Period README role: `replication`.
- **Period-native tests** (role `native`), each with its own dated prediction: **G26** (an elected leader with a known start), **G35** (daily-rotating designated lead designers: a within-agent design), **G44** (an installed fine-tuned leader in #best), **G12** (rotating debate judges: within-agent, judge vs debater).
- **Faithfulness lever:** G (DQ6 leaders). The scorecard says whether it moved.

## Model
**From:** `physics-models/02-nonequilibrium-ising/` (linear response with directed couplings J_ij ≠ J_ji; the in- and out-strength of a node) and `physics-models/04-semantic-information/` (information that enters an agent from the swarm vs information that leaves it).

**H65 variant: read-gated linear response (RGLR).** Agent j's statement B (chat, time t_B, room r, day d) has a content state z_B ∈ ℝ³² (DQ5 whitened unit vector with the period's field subspace projected out). It responds linearly to what j has read:

z_B = a_j z_{P} + a′_j e_j + b_j f_{d,r,−j} + h_j H_B + λ_j U_B + Σ_i κ_{i→j} S_{iB} + ξ_B,

- z_P: j's previous statement that day; e_j: j's exponentially weighted own mean (half-life 5 statements);
- f: the day × room mean of other agents' statements (slow common drive, H32's field);
- H_B: decayed sum of human messages j had read; U_B: decayed sum of same-room agent messages posted during B's producing call, which j had **not** read (the in-flight co-response placebo, H57);
- S_{iB}: decayed, saturating sum of agent i's messages that j had **read** by B's producing call (context ledger), weights exp(−age/τ), τ = 15 min, window 45 min: Σ w z_A / (1 + Σ w).
- Coefficients are scalars (isotropic couplings), fitted by least squares on the stacked 32 coordinates.

Two node-level summaries of the directed coupling matrix κ_{i→j}:
- **Susceptibility (inflow) χ_j:** the coefficient on R_B = the pooled read input from all agents in j's own regression. It measures how far j's next statement moves toward what it has read.
- **Influence (outflow) κ_i:** one shared coefficient on S_{iB} across all targets j ≠ i, each target's other terms (including R_B without i) partialled out first. It measures how far other agents move toward i's messages per unit read.
Both are per unit of read input, so a quiet leader is not penalized for posting little (H32's caveat).

**Router index** of agent L in a unit: ρ_R(L) = pct(χ_L) − pct(κ_L), with pct the rank percentile among the unit's agents (0 = lowest, 1 = highest). A router has ρ_R > 0 (high inflow, low outflow); a source has ρ_R < 0.

**Reply channel (DQ2).** Per agent and window: **reply-out share** RO = share of its statements that are replies (p_reply ≥ 0.5) to an agent; **reply-out breadth** BO = exp(entropy of the authors it replied to) / (N_present − 1); **reply-in rate** RI = agent replies received per own statement. A router has high RO and BO; a broadcaster has high RI and high κ.

**H65 (HH264):** designated leaders have pct(χ) > 0.5, pct(κ) ≤ 0.5 and BO above the median: aggregation, not broadcasting.

**Rivals.**
- **R-source (per message):** leaders are sources once outflow is measured per unit read (κ high), and H32's negative was a volume artifact.
- **R-attention (status only):** leaders receive more replies (H29, H52) but have no special content role (pct(χ) and pct(κ) both near 0.5).
- **R-agenda (judges):** a leader who sets the topic (a debate motion, an elected leader's goal) acts as a field source on everyone (high κ), not a router.
- **R-volume:** any apparent router index is message count in disguise (partialled out in the replication layer).

**Theory notes, written before the data.**
1. *Why per-unit coefficients.* H32's Out sums gains over pairs and messages, so low-volume senders rank low by construction. χ and κ are slopes per unit of read input; a leader who speaks rarely but is followed when it does would show a high κ.
2. *The co-response confound.* H32 r1b found about a third of short-lag "transfer" in messages the target had not read yet (both answer the same prior turn). The unread term U_B absorbs a common co-response; λ̂ next to χ̂ reports its size.
3. *Answering is absorbing.* A reply is partly about its parent, so high RO mechanically raises χ. The router picture is the claim that leaders *do* this more than others; R1 checks that the mechanics hold at all.

## Data scheme (`scheme/`)
- **`scheme/build.py --period G<NN>`** → `data/processed/H65-leaders-are-routers/G<NN>/` (zstd parquet; codes and float32 coefficients only; no text, no vectors stored):
  - `targets.parquet`: one row per agent chat statement B (non-holdout): statement row, agent, t_B, room, day, producing call (`call_windows`: the agent's last call with t_call ≤ t_B on that PT day), DQ2 reply flags (has agent parent; parent author).
  - `reads.parquet`: per target B, the agent and human messages B's author read by B's producing call within 45 min (ledger items at its calls with t_call ≤ t_call(c_B)), with sender, statement row and age at t_B; plus the unread in-flight set U (same-room agent messages posted in [t_call(c_B), t_B)).
- **Vectors:** `statements_white32_bge_small` (primary), `statements_white32_gte_modernbert`, `statements_style_resid_period32_bge_small`. Field subspace per period (K ≤ 5): `goal_whole`, each `kickoff_room` (whitened in the period's regime basis with `load_whitener(regime, 32, model)`), and the period mean of agent statements; orthonormalized and projected out (not renormalized).
- **Eligibility:** non-holdout goal periods with ≥ 4 agents having ≥ 30 statements with nonzero read input. #51 is split by `period_units` (51a–51l; units with ≥ 4 eligible agents only).
- **Regimes covered:** I, II, III.

## Observables
*Written 2026-10-04 19:35 UTC.*
**Per agent and unit:** χ̂ (inflow), κ̂ (outflow), λ̂ (unread co-response), RO, BO, RI, statement count n; standard errors from a block bootstrap over room × 30-min blocks (100 replicates).

**Replication layer (every eligible period p):**
- **O1 router mechanics:** ρ₁ = Spearman(RO, χ̂) across agents.
- **O2 attention alignment (primary):** D_p = ρ(RI, χ̂) − ρ(RI, κ̂), partial Spearman correlations controlling for log n. D_p > 0 means the agents others reply to are content sinks (routers); D_p < 0 means they are content sources.
- **O3 axis distinctness:** ρ(χ̂, κ̂).
- **O4 instrument cross-check:** ρ(κ̂, H32 Out) and ρ(χ̂, H32 In) on H32's periods (r1b, bge), read-only.
- **O5 co-response share:** median over agents of λ̂ / χ̂.

**Native layer:**
- **O6 leader percentiles** (G26, G44): pct(χ̂_L), pct(κ̂_L), pct(BO_L), pct(RI_L), and ρ_R(L), within the leader's window (G26: term 1, 2026-01-05 19:35:22 → 01-09 19:00:43 UTC; G44: #best from 2026-05-26 19:15:47 UTC); bootstrap distribution of the ranks.
- **O7 within-agent leader-day contrast** (G35): agent × room-day estimates of χ, κ, RO, BO, RI; Δ = leader-day − the same agent's non-leader days, averaged over the 6 leader-days, minus the same contrast for non-leaders (two-way agent and room-day effects); null = leader labels permuted among the agents present in each room-day (5,000).
- **O8 within-agent judge contrast** (G12): each agent's statements as judge (inside its judged debate's window) vs as debater (inside other debates' windows): Δχ, Δκ, ΔRO, ΔBO, ΔRI; null = the judge label permuted among each debate's participants.

## Null / baseline
*Written 2026-10-04 19:35 UTC.*
- **N1 rank null:** with no leader effect, a leader's percentiles are uniform on [0, 1]; a router call (pct χ ≥ 0.6 and pct κ ≤ 0.5) has probability ≈ 0.2 for one leader. Natives are combined by counting router calls against this base rate.
- **N2 permutation of leader labels** within room-day (G35) and among debate participants (G12).
- **N3 co-response:** the unread in-flight term U_B in every regression.
- **N4 field:** the period's goal and kickoff directions and the period mean projected out; the day × room mean f in every regression; human messages as a separate term.
- **N5 synthetic** (`analysis/synthetic.py`): the RGLR estimator on synthetic vectors generated by the model on real skeletons (real statement times, rooms and ledger read sets) with a planted router, a planted source, and no leader.
- **N6 volume:** log n partialled out in the replication correlations; per-unit coefficients by design.
- **Unit-of-analysis exception (named, CLAUDE.md):** none for the replication layer (one estimate per period). The natives compare agents inside one period (G26, G44) or roles inside one period (G35, G12); no pooling across periods.

## Impostors (STANDARDS §1)
| Impostor | Relevant? | How it is removed | Status |
| --- | --- | --- | --- |
| Scheduler field | weak | Content states, not activity. Day × room field f and per-target nuisance terms absorb day-level shifts. Reply rates are per statement. | addressed |
| Exogenous field (kickoff, goal, operator) | yes | Goal, room kickoffs and the period mean projected out of every vector (K ≤ 5); the day × room mean in every regression; human messages as their own term H_B. A leader who announces the agenda (R-agenda) would load on κ through the non-removed part; reported as such. | addressed |
| Shared model priors (family, style) | yes | A third run on DQ5 `style_resid_period` vectors; leaders' coefficients are compared within one period, so family is fixed per agent. | addressed by variant |
| Contemporaneous convergence | yes | Reads come from the context ledger at B's producing call; the in-flight unread term U_B absorbs co-response; λ̂ reported. | addressed |

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R-source (per-message), R-attention (status only), R-agenda (topic setter as field source), R-volume.
**Locked holdout used for confirmation:** none yet. Planned (`analysis/confirm.py`, frozen, not run): #45 (the installed Fine-Tuned Leader) and #28 (replication D_p).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Reads from the context ledger at the producing call; replies from DQ2 parents; leaders and judges from DQ6; three vector variants (bge, gte, style-residualized). The isotropic linear-response mapping is an assumption; inflow is model-dependent at the 0.1 level (#35: +0.09 bge, +0.18 gte). |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Co-response modelled (unread term λ; λ/χ 0.61); linearity, isotropy and the 15-min kernel not tested; per-agent coefficients assumed stationary within a period or role window. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | Role contrasts beat the role-permutation null for replies received and reply breadth (p ≤ 0.007), not for content. R1 beats the sign null (p 0.0002). No held-out days. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | R1 (answering is absorbing) and R3 (inflow and outflow distinct, ρ 0.14) hold as predicted; R2 (attention to sinks) and the router signature fail. |
| E interventional | predicts the change across a natural experiment | 1 | Operator-rotated lead designers (#35) and rotating judges (#12) used as within-agent role switches: attention follows the role, content inflow does not. No village-level NE. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Within-agent designs recover planted routers and sources (1.00) with null call rates 0.00–0.15; single-leader percentiles were mis-sized (0.50 under the null) and are now calibrated on the skeleton null; #44 cannot identify a router at all. Results agree across three vector variants except #35 inflow. |
| G ground truth | agrees with known structure | 1 | DQ6 leaders, lead designers and judges: the reply premium of H29/H52 is reproduced; leaders are not content routers. |
| H comparative | beats the named rivals | 1 | R-attention fits #35 and #12; R-source/R-agenda fits #26 only; R-agenda rejected for judges (Δκ −0.06); R-volume removed by per-unit coefficients and log n. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Holdout not run. |

**Overall A–I (round 1):** A1 B1 C1 D1 E1 F1 G1 H1 I0. **Faithfulness lever (G):** unchanged at 1: the DQ6 leaders were used, and they contradict the router claim.

## Prediction
*Written 2026-10-04 19:35 UTC, before running any H65 statistic on real data.*

**What I had seen.** The round-1 and 1b results of H23, H29, H32 and H52 (cards). In particular: H32 r1b ranks the elected leader 5/10 by total outflow over its term, #35's designated leaders at percentile 0.43, and #44's installed leader last of 6; H29 found #35 leaders get 1.39× more replies per message and no broadcast pull, and #26's elected leader's broadcast pull rose more than anyone's (regime I); H52 found a reply premium for elected and appointed leaders (+0.03). Structural counts only for H65: statements per agent per day for agent 17 (#26) and agent 28 (#44: 27 statements), and per agent × room-day in #35. No χ, κ, RO, BO or RI value was computed.

**Synthetic (axis F; run first, at real skeletons G26, G35, G44, G12).**
| # | Prediction | Counts against |
| --- | --- | --- |
| S1 | A planted router (χ × 2, outflow weight × 0.2) gets pct χ ≥ 0.6 and pct κ ≤ 0.5 in ≥ 70% of replicates at G26 and G35 sampling | < 50% |
| S2 | A planted source (outflow weight × 3) gets pct κ ≥ 0.6 in ≥ 70% | < 50% |
| S3 | With no leader effect, the router call for a fixed agent fires at its base rate (≈ 0.2 ± 0.1) | > 0.35 |
| S4 | G44's leader (27 statements) is too sparse for a reliable χ̂: router recovery < 50% (its native verdict then needs CI-based wording) | |

**Replication layer** (templated across periods).
| # | Prediction [credence] | Counts against |
| --- | --- | --- |
| R1 | Router mechanics: ρ(RO, χ̂) > 0 in ≥ 2/3 of periods, median > 0 [0.6] | median ≤ 0 |
| R2 (primary) | Attention goes to sinks: D_p > 0 in ≥ 2/3 of periods and median D > 0 (sign test p < 0.05) [0.35] | median D ≤ 0 (attention goes to sources) |
| R3 | Inflow and outflow are distinct axes: median ρ(χ̂, κ̂) < 0.5 [0.7] | |
| R4 | Instrument check: median ρ(κ̂, H32 Out) > 0.3 [0.5] | ≤ 0 (the two outflow estimators disagree) |
| R5 | Co-response: median λ̂/χ̂ between 0.1 and 0.6 (descriptive; H32's "about a third") | |

**Native layer** (each period README repeats its own prediction).
- **N1 G26 (elected leader, agent 17, term 1).** pct χ̂ ≥ 0.6 [0.45]; pct κ̂ ≤ 0.5 [0.6]; pct BO ≥ 0.5 [0.55]; router call [0.3].
- **N2 G35 (lead designers, within agent).** Δχ > 0 [0.5]; Δκ ≤ 0 [0.6]; ΔBO > 0 [0.5]; ΔRI > 0 [0.7, H29]. Router call = Δχ > 0 and Δκ ≤ 0 with permutation p(Δχ) < 0.10 [0.25].
- **N3 G44 (installed leader, agent 28, #best).** pct κ̂ ≤ 0.5 [0.8]; pct χ̂ ≥ 0.6 [0.5] (H23: its plans track the room); router call [0.4]. Expected low reliability (27 statements).
- **N4 G12 (judges, within agent).** Δκ > 0 (judges set the motion: R-agenda) [0.45]; Δχ > 0 [0.5]; router call [0.3].

**Hypothesis-level verdict rule.**
- **Supported:** router calls in ≥ 3 of the 4 natives (pct or within-agent version), *and* R2 holds.
- **Failed:** in ≥ 3 of 4 natives the leader's κ percentile (or Δκ) exceeds its χ percentile (or Δχ) (leaders are sources), *or* R2's median D < 0 with sign-test p < 0.05.
- **Mixed / inconclusive:** otherwise; "inconclusive" if the synthetic power for router recovery at the natives' sampling is < 0.5.

**My credence before data:** supported 0.2; failed 0.2; mixed or inconclusive 0.6.

### Synthetic validation (axis F; done 2026-10-04 ~20:30–21:10 UTC, before any real-data outcome)
`analysis/synthetic.py` → `data/processed/H65-leaders-are-routers/synthetic/{natives,null_extra}.json` (+ per-replicate parquet). Real skeletons; vectors from the card's model (a 0.3, a′ 0.2, b 0.4, χ₀ 0.4, h 0.2, noise σ 1); router = leader χ × 2 and outflow weight × 0.2; weak router = × 1.3 and × 0.6; source = outflow weight × 3; 20 replicates per cell (60 for the G26/G44 nulls).
| Native | router call: null | router | weak router | source | reading |
| --- | --- | --- | --- | --- | --- |
| G35 (within agent, permutation) | 0.15 | 1.00 | 1.00 | 0.00 (source call 1.00) | calibrated; powered |
| G12 (within agent, permutation) | 0.00 | 1.00 | 0.55 | 0.00 (source call 1.00) | calibrated; powered for the strong router |
| G26 (percentiles, one leader) | **0.50** | 1.00 | 0.95 | 0.00 | **mis-sized**: under no leader effect agent 17's skeleton gives mean pct χ̂ 0.59 and pct κ̂ 0.32 |
| G44 (percentiles, one leader) | **0.53** | 1.00 | 0.95 | 0.25 | **mis-sized**: agent 28's late join and sparse exposure give pct κ̂ 0.08 under the null |
- S1, S2 pass for every native; **S3 fails for the percentile natives (G26, G44)**: the skeleton itself places a single leader high in χ̂ and low in κ̂, so the raw percentile rule fires in about half of null replicates. S4: G44's leader is recovered at the planted effect sizes, but the null is so skewed that a router cannot be told from no effect there.

### Amendment A1 (synthetic-based; written 2026-10-04 ~21:15 UTC, before any real-data outcome statistic)
1. **G26 and G44 router calls are calibrated against their own skeleton null:** router call = the leader's router index ρ_R exceeds the 90th percentile of the 60 null replicates (p_syn < 0.10) *and* pct κ̂ ≤ 0.5. The raw percentiles are reported as descriptive. At G44 the null's 90th percentile is 1.0, so **G44 cannot yield a router call** (verdict at best "inconclusive" for the router clause; its κ̂ percentile is read against the null mean 0.08).
2. Everything else is unchanged: the within-agent natives (G35, G12) use the permutation nulls as written; replication predictions R1–R5 unchanged.

## Results by goal period
Replication folders: **supported** if D_p's block-bootstrap CI is above 0 (attention to content sinks), **failed** if below 0, **descriptive** otherwise (and for N = 4 periods, where D_p is undefined). bge-small primary.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G02](goalperiod-subhypotheses/G02/README.md) | replication | descriptive | 4 agents; ρ(RO, χ) +0.20; D_p —; λ/χ 6.98 |
| [G03](goalperiod-subhypotheses/G03/README.md) | replication | descriptive | 4 agents; ρ(RO, χ) -0.40; D_p —; λ/χ 1.93 |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | descriptive | 6 agents; ρ(RO, χ) +0.43; D_p +0.53 [-0.57, +1.14]; λ/χ 6.42 |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | descriptive | 4 agents; ρ(RO, χ) +0.20; D_p —; λ/χ 1.74 |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | descriptive | 4 agents; ρ(RO, χ) +0.40; D_p —; λ/χ 1.89 |
| [G07](goalperiod-subhypotheses/G07/README.md) | replication | descriptive | 4 agents; ρ(RO, χ) +0.80; D_p —; λ/χ 0.56 |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | descriptive | 4 agents; ρ(RO, χ) +0.60; D_p —; λ/χ 1.54 |
| [G10](goalperiod-subhypotheses/G10/README.md) | replication | descriptive | 7 agents; ρ(RO, χ) +0.04; D_p -0.78 [-1.62, +0.71]; λ/χ 1.99 |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | descriptive | 7 agents; ρ(RO, χ) -0.14; D_p +0.45 [-1.24, +1.18]; λ/χ 2.06 |
| [G12](goalperiod-subhypotheses/G12/README.md) | native | mixed | 7 agents; ρ(RO, χ) +0.50; D_p -0.37 [-1.09, +0.19]; λ/χ 1.73; role Δχ -0.028 (p 0.59), Δκ -0.059, ΔRI +0.45 (p 0.007), ΔBO +0.16 (p 0.003) |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | descriptive | 6 agents; ρ(RO, χ) +0.54; D_p -0.05 [-1.03, +0.31]; λ/χ 5.66 |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | descriptive | 7 agents; ρ(RO, χ) +0.14; D_p +0.18 [-1.05, +0.77]; λ/χ 1.32 |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | descriptive | 7 agents; ρ(RO, χ) +0.39; D_p -0.58 [-1.33, +0.58]; λ/χ 1.52 |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | failed | 8 agents; ρ(RO, χ) +0.19; D_p -0.48 [-0.96, -0.08]; λ/χ 1.84 |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | descriptive | 8 agents; ρ(RO, χ) -0.48; D_p -0.00 [-0.64, +0.60]; λ/χ 1.45 |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | descriptive | 10 agents; ρ(RO, χ) +0.03; D_p +0.09 [-0.51, +0.42]; λ/χ 0.87 |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | descriptive | 9 agents; ρ(RO, χ) +0.22; D_p +0.60 [-0.33, +0.78]; λ/χ 0.71 |
| [G23](goalperiod-subhypotheses/G23/README.md) | replication | descriptive | 10 agents; ρ(RO, χ) -0.25; D_p -0.51 [-0.87, +0.29]; λ/χ 0.37 |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | descriptive | 10 agents; ρ(RO, χ) -0.08; D_p +0.43 [-0.62, +1.04]; λ/χ 0.50 |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | descriptive | 10 agents; ρ(RO, χ) +0.47; D_p -0.43 [-0.88, +0.36]; λ/χ 1.23 |
| [G26](goalperiod-subhypotheses/G26/README.md) | native | failed | 10 agents; ρ(RO, χ) +0.22; D_p -0.44 [-0.95, +0.13]; λ/χ 1.14; leader pct χ 0.22, pct κ 1.00 (null means 0.59, 0.32), pct RI 0.89 |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | descriptive | 10 agents; ρ(RO, χ) -0.59; D_p -0.74 [-0.82, +0.09]; λ/χ 0.24 |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | descriptive | 11 agents; ρ(RO, χ) -0.15; D_p -0.35 [-0.82, +0.28]; λ/χ 0.64 |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | supported | 12 agents; ρ(RO, χ) +0.47; D_p +0.73 [+0.14, +0.92]; λ/χ 0.53 |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | descriptive | 10 agents; ρ(RO, χ) +0.36; D_p +0.11 [-0.32, +0.60]; λ/χ 0.54 |
| [G35](goalperiod-subhypotheses/G35/README.md) | native | mixed | 11 agents; ρ(RO, χ) +0.32; D_p +0.19 [-0.93, +0.81]; λ/χ 0.82; role Δχ +0.091 (p 0.18), Δκ +0.003, ΔRI +0.39 (p 0.005), ΔBO +0.06 (p 0.104) |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | descriptive | 11 agents; ρ(RO, χ) +0.23; D_p +0.67 [-0.13, +1.01]; λ/χ 0.65 |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | descriptive | 9 agents; ρ(RO, χ) +0.07; D_p +0.08 [-0.55, +1.60]; λ/χ 0.30 |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | failed | 12 agents; ρ(RO, χ) +0.36; D_p -0.94 [-1.34, -0.17]; λ/χ 0.93 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | descriptive | 11 agents; ρ(RO, χ) +0.43; D_p +0.17 [-0.70, +0.89]; λ/χ 0.49 |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | descriptive | 11 agents; ρ(RO, χ) +0.70; D_p -0.01 [-0.32, +0.49]; λ/χ 0.54 |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | descriptive | 14 agents; ρ(RO, χ) +0.44; D_p -0.08 [-0.55, +0.46]; λ/χ 0.79 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | descriptive | 12 agents; ρ(RO, χ) +0.71; D_p +0.11 [-0.72, +0.58]; λ/χ 0.48 |
| [G44](goalperiod-subhypotheses/G44/README.md) | native | descriptive | 14 agents; ρ(RO, χ) -0.03; D_p -0.03 [-0.69, +0.30]; λ/χ 0.59; leader pct χ 0.20, pct κ 0.00 (null means 0.50, 0.08), pct RI 0.40 |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication | descriptive | 12 units; median ρ(RO, χ) +0.38; median D_p -0.14 |

## Results
*Round 1, 2026-10-04 (UTC). Code: `scheme/build.py`; `analysis/{h65lib,run,synthetic,summarize,period_folders,estimates_rows,figures,confirm}.py`. Data: `data/processed/H65-leaders-are-routers/` (`G<NN>/{targets,reads}.parquet`, `replication/<model>/{periods.json,agents.parquet}`, `replication/summary.json`, `natives/<model>/G*.json`, `synthetic/`, `confirm/dryrun.json`; ≈ 40 MB). Figures: `figures/h65_obs.pdf`, `figures/h65_synth.pdf`. 582 rows in `per_period_estimates` (three vector variants).*

**Headline.** Designated leaders in this village are where replies go, not where content goes in or comes out. Elected, designated and judging agents receive about +0.4 more replies per statement than they do off-role, and judges answer more agents, but their next statements do not follow what they read more than before, and they do not pull others' content more. The one exception is the elected leader of #26, whose messages move others more than any other agent's: a source, not a router.

### Outcome vs prediction
| Prediction | Observed (bge; gte; style) | Verdict |
| --- | --- | --- |
| S1–S2 planted router/source recovered ≥ 70% | 1.00 in every native (weak router: 0.55–1.00) | pass |
| S3 null router-call rate ≈ base rate | 0.00–0.15 within agent; **0.50–0.53 for single leaders** | fail → A1 (skeleton-null calibration) |
| R1 ρ(RO, χ) > 0 in ≥ 2/3, median > 0 [0.6] | +0.29 (36/46); +0.35 (38/46); +0.28 (38/46) | **pass** |
| R2 D_p > 0 in ≥ 2/3, sign p < 0.05 [0.35] | −0.04 (17/40); −0.07 (15/40); −0.06 (18/40); CI > 0 in 1, < 0 in 3 | **fail** (no alignment either way) |
| R3 median ρ(χ, κ) < 0.5 [0.7] | 0.14; 0.09; 0.14 | pass |
| R4 median ρ(κ, H32 Out) > 0.3 [0.5] | 0.43 (27/32); χ vs H32 In 0.40 (23/32) | pass |
| R5 λ/χ in [0.1, 0.6] (descriptive) | 0.61; 0.62; 0.52 | at the edge |
| N1 #26 router call [0.3] | pct χ 0.22 / 0.11 / 0.22, pct κ 1.00 / 0.89 / 0.89 (null means 0.59, 0.32); router index −0.78 [−1.0, −0.33] | **fail: source** |
| N2 #35 router call [0.25] | Δχ +0.09 (p 0.18); +0.18 (p 0.009); +0.07 (p 0.24); Δκ ≈ 0; ΔRI +0.39 (p 0.005); ΔBO +0.06 (p 0.10) | mixed (call under gte only) |
| N3 #44 router call [0.4] | pct χ 0.2 / 0.6 / 0.6, pct κ 0.0 (null mean 0.08); no call possible (A1) | descriptive |
| N4 #12 judges: Δκ > 0 (R-agenda) [0.45]; router [0.3] | Δκ −0.06 (p_less 0.06); Δχ −0.03 / +0.08 / −0.13 (n.s.); ΔBO +0.16 (p 0.003); ΔRI +0.45 (p 0.007) | R-agenda rejected; no router |

**Verdict by the card's rule:** router calls in 0 of 4 natives (bge) → not supported; leaders are sources in 1 of 4 (#26) and R2's median is not significantly negative → not failed. **Mixed.** The pre-registered rivals sort it: R-attention (status buys replies, not a content role) fits #35 and #12; R-source/R-agenda fits #26 alone.

### Physics reading
In the directed linear-response network κ_{i→j}, a designated leader is not a sink node (its susceptibility χ does not rise with the role) and, except for the elected leader, not a source node either. The role changes the *reply* graph only: in-degree rises and, for judges, out-degree breadth rises. Content coupling is set by reading and answering (ρ(RO, χ) +0.29 in 36/46 units), and attention (who is answered) is statistically independent of who moves content (D_p ≈ 0). The co-response term is large: same-room messages the agent had not yet read predict its statement at 0.6 of the weight of read ones (H32, H57: contemporaneous convergence).

### Caveats
1. **Per-agent content coefficients are noisy** at the role-window scale (≥ 10 statements per agent-room-day in #35, ≥ 5 per agent-debate in #12); the #35 inflow result changes significance with the embedding model.
2. **Single-leader percentiles are skeleton-biased** (the null puts #26's leader at pct χ 0.59, #44's at pct κ 0.08); the calibrated rule removes the bias but leaves one leader per period, so N1 and N3 are weak tests. #26's source result survives it (pct κ 1.00 vs null mean 0.32; p_syn for a router call 1.0).
3. **χ includes answering mechanics** (a reply is about its parent; DQ2 parents are partly content-selected). R1 is partly built in; the leader contrasts are not, because the same agent is compared with itself.
4. **λ/χ ≈ 0.6:** much of what looks like inflow is co-response to the same prior turn; the ranking of agents survives it (λ is in every regression) but absolute χ values overstate reading-driven uptake.
5. The installed leader (#44) has 27 statements; no router or source claim is possible there.

### Confirmatory test (frozen 2026-10-04 after round 1; `analysis/confirm.py`, **not run**)
Guards: refuses without `--confirm --i-understand-this-uses-the-locked-holdout` and with uncommitted changes in the H65 folder; `scheme/build.py` writes held-out builds only to `confirm_build/` when the confirm script sets its switch. Dry run on stand-ins (#44 leader, #27) runs end to end (`confirm/dryrun.json`). Ledger: #45 activity timing run by H02 and H04; content planned by H23 and others (disclosure needed); #28 planned by H32, H34 and others; nobody has computed read-gated inflow/outflow or reply rates on either.
- **C1 (primary):** the #45 Fine-Tuned Leader is not a router (router index below its skeleton null's 90th percentile). Credence 0.8.
- **C2:** its reply-in rate is at or above the median agent. Credence 0.6.
- **C3:** #28 D_p CI includes 0. Credence 0.75. **C4:** #28 ρ(RO, χ) > 0. Credence 0.75. **C5:** #28 λ/χ in [0.4, 0.8]. Credence 0.7.
- **Decision:** "leaders are attention hubs, not content routers" confirmed if C1 and C2 pass; "answering is absorbing; attention is unaligned with content flow" confirmed if C3 and C4 pass.

## Round 2 redirects
**What the direction is really after:** whether any agent in a swarm relays information (a two-hop path through it), and what makes an elected leader a content source.
- **H65-R1. A direct relay test.** For messages addressed to a leader, measure the two-hop transfer i → L → k (k reads L's next statement) against i → k directly and against non-leader intermediaries. Routing is a path property, not a node property.
- **H65-R2. The agenda event.** Event-study the #26 leader's goal announcement and its follow-ups: is its source status one agenda-setting message (a field step) or sustained conversation (a coupling)?
- **H65-R3. Co-response-matched inflow.** Re-estimate χ at matched read vs unread age (τ = 60 s, as H32 r1b) per agent, so that inflow means reading.
- **H65-R4. Run `confirm.py`** after committing (#45, #28).

## Notes
- 2026-10-04: promoted from HH264 by Vivian.
- 2026-10-04 19:35 UTC: round-1 agent started; question, model, scheme, observables, nulls, impostor table and predictions written before any H65 outcome statistic.
- 2026-10-04 20:15 UTC: per-period predictions written in the G folders. G44 native thresholds (15 statements / 15 exposed targets) fixed in code before the run, because the leader has 27 statements.
- 2026-10-04 ~21:15 UTC: synthetic validation and Amendment A1 (skeleton-null calibration for single-leader natives), then the real-data runs (bge, then gte and style).
- Compute: local; synthetic ≈ 15 min (4 workers, then 2 after the coordinator's load notice); real runs ≈ 15 min. Disk ≈ 40 MB.
- **Read-only inputs from another hypothesis:** H32's r1b per-agent Out/Net (`data/processed/H32-information-current-leaders/r1b/bge/`) for the cross-check R4 only; no H32 code imported.
- **Proposed shared changes** (not made): DEFINITIONS.md named variants *read-gated susceptibility χ (content inflow)*, *read-gated influence κ (content outflow)*, *router index ρ_R*, *reply-out share / breadth*, *reply-in rate*. infra/README Known issue: single-agent percentile tests on village skeletons are biased by exposure structure (a no-effect synthetic puts #26's leader at pct χ 0.59 and #44's at pct κ 0.08); calibrate any "where does agent X rank" claim on a skeleton null. Suggested shared code: H65's `h65lib` block-Gram RGLR estimator (any window, block bootstrap as weighted sums) could serve H29/H32/H52 as `infra/shared/read_response.py`.
