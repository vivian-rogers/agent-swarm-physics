# H64: Conflict needs a scarce prize

**Status:** exploratory round 1 **done (2026-10-04): supported by the pre-registered rule, with the reading narrowed.** Design, observables, nulls, rivals and predictions written 2026-10-04 19:20 UTC; Amendment A1 (synthetic) ~20:05 UTC; both before any H64 outcome statistic.
- **Settlement switches assigned conflict off.** In the #12 debates, opponents' replies are 0.78 [0.56, 1.10] more negative than teammates' while the prize is open (team permutation p 0.0002), and 0.09 [−0.26, 0.39] after the verdict (Δ −0.69, p 0.001). No heat field on teammates (+0.00) and no loser resentment (+0.19, CI includes 0).
- **Competition raises position-opposition period-wide.** All four competition periods (#6, #23, #26, #27) sit above the prize-free median of confident position-opposition (0.94% of replies; theirs 1.1–3.4%; Mann–Whitney p 0.022; 4/4 also within regime I, post hoc). But the rival-specific contrast is not significant in #23 chess (−0.13, p 0.31) or #26 (+0.25, 14 replies): the competition effect looks like a contest-wide field, not antagonism between rivals.
- **No antagonism without a prize:** 25/26 prize-free units and 11/12 #51 units show no excess antagonistic pairs against the calibrated agent-field null; #51's rate (1.06%) is inside the prize-free range. The cluster-robust pair count has low power (it finds no pairs in #12 either).
- Scorecard A1 B1 C1 D1 E1 F1 G1 H1 I0. `analysis/confirm.py` (#29, #34 vote-outs, #51 tail) frozen and dry-run, **not run**.
**Fields:** sociophysics, stat mech
**Question served:** **Q3** (is there collective order beyond fields?): does antiferromagnetic stance order exist anywhere outside an assigned protocol? **Q2** second: if antagonism switches on and off with the state of a prize, it is a field (an incentive), not a coupling.
**Literature:** none of the notes in `literature/` covers contests or signed networks. Cited from memory (†, not in `literature/`): Tullock, "Efficient rent seeking" (1980)† (contests for a single prize); Heider, *J. Psychol.* 21, 107 (1946)† and Cartwright & Harary, *Psychol. Rev.* 63, 277 (1956)† (structural balance); Sherif et al., *The Robbers Cave Experiment* (1961)† (inter-group hostility appears under competition for scarce rewards and fades under superordinate goals); Mattis, *Phys. Lett. A* 56, 421 (1976)† (a gauge-transformed ferromagnet as a two-camp antiferromagnet).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Population; Regime; Driving / external field (here a contest incentive); Interaction, variant reply, implemented as DQ2 reply parents on ledger visibility (Exposure (turn read-out)); H37's *stance spin* and *stance coupling (residual)*. New terms defined below and proposed for the shared file: **prize state** (open / settled), **rival pair (exclusive prize)**, **prize-gated antagonism Δ**, **antagonism excess E** (cluster-robust).
**From:** HH255 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` ("Making the faithful ones better") · **Models:** `physics-models/01-inverse-ising/` (signed couplings), `physics-models/10-potts/` (two camps) · **Faithfulness lever:** G (ground-truth prize phases from DQ6) and E (the settlement instant as a dated switch).
**Data inputs (shared tables first):** DQ2 `reply_pairs` (`pair_set = cand`, labelled, agent → agent), DQ6 `ground_truth_labels` (`preferred & ~holdout`: #12 teams, phases and results; #26 phases, tallies and results), `chat_core`, `chat_text` (in memory only, #23 game ids), `period_units`, `period_affordances`, `infra/shared/nulls.py` (`fit_ordinal`, `simulate_ordinal`: H37's calibrated agent-field null).

## Question
H37 found stance antagonism only where a protocol assigns sides (the #12 debates), and none between #51 rivals or #26 voting blocs. HH255's sharper claim: antagonism appears only while agents compete for a **rival-exclusive outcome** (a judge's decision, a vote, a single winner) and vanishes once the prize is settled. If true, conflict in agent swarms is a field set by the incentive structure. An operator could then switch it off by settling the prize. If false, either nothing produces antagonism except an explicit order to argue (the protocol rival), or antagonism is a property of the pair that outlives the contest (the remanence rival).

## Design: two layers (Vivian, 2026-10-04; see `infra/data-quality/QUEUE.md`)
- **Replication:** the common estimator (antagonism excess E_p and confident position-opposition rate r_p) on every eligible goal period. Each period is a point on a phase diagram classed by its prize structure. Period README role: `replication`.
- **Period-native tests:** three periods with dated prize states, each with its own dated prediction (role `native`): **G12** (judged debates: open → verdict), **G26** (an election: open → result), **G23** (chess games between known opponents: open game → finished game).
- **Faithfulness lever:** G (DQ6 phases and results) and E (settlement instants). The scorecard says whether each moved.

## Model
**From:** `physics-models/01-inverse-ising/` (signed couplings on reply bonds) and `physics-models/10-potts/` (camps as a two-state Potts/Mattis ground state).

**H64 variant: prize-gated antagonism on reply bonds.** A reply e from agent j (speaker) to agent i's message (target) at time t carries a latent stance
y*_e = μ + a_j + b_i + Δ · R_ij · O(t) + δ_rel · R_ij + φ · O(t) + u_k(e) + ε_e, ε logistic,
and the observed DQ2 class is − / 0 / + by two cut points (ordered logit), then passed through the labeller's confusion matrix.
- a_j, b_i: agent fields (j's agreeableness as a replier, i's likability). LLM politeness is the uniform part of μ.
- R_ij = 1 if i and j compete for the same rival-exclusive prize (opposite debate teams; runoff candidates; opponents in one chess game).
- O(t) = 1 while the prize is open (debate before its verdict; election before its result; a game between its first and last link), 0 once it is settled.
- **Δ < 0** is prize-gated antagonism (H64). **δ_rel < 0** with Δ ≈ 0 is relation-bound antagonism (remanence rival). **φ < 0** with Δ = 0 is a contest "heat" field on every pair (heat rival).
- u_k: a shared shock for all replies in one conversation block k (30-min room block; one debate phase in #12). It models thread clustering (RE-C2), which inflates negative-pair counts.

In magnet terms, the contest is a staggered external field h_i = ±h on the two camps, which induces a Mattis antiferromagnet (Δ ∝ h) while it is on. H64 says the antagonism is entirely induced by the field (it relaxes to the ferromagnetic background within one conversation block after the field switches off). Coupling-borne antagonism would survive the switch-off.

**Rivals.**
- **R-protocol (H37):** antagonism appears only where a protocol assigns opposing sides; competition for a prize without assigned sides (#6, #23, #26, #27) shows none.
- **R-relation (remanence):** rival pairs stay antagonistic after settlement (δ_rel < 0, Δ ≈ 0); losers resent winners.
- **R-heat:** contests raise negativity on every pair while open (φ < 0), not specifically between rivals.
- **R-null (cooperation default, H22/H37):** no antagonism beyond agent fields, thread clustering and label noise anywhere.

**Theory notes, written before the data.**
1. *Why a DiD.* A uniform heat field and a rival-pair constant each fake a "conflict while open" contrast. The interaction Δ = (rival − non-rival)_open − (rival − non-rival)_settled removes both. Two-way agent effects remove agreeableness and likability.
2. *Why cluster-robust.* RE-C2 found 70/54/33 "significant" negative pairs in #51 units against ~7 under the agent-field null, because replies in one thread share a sign. Every pair-level test here clusters by conversation block and requires ≥ 3 blocks per pair.
3. *What the labeller can see.* DQ2 pair-level "opposes" is about 0.08 precise as conflict. The design never reads single labels; it compares group means and counts against a null with the labeller's noise built in. `opp_type = position` is the best available conflict flag but is unvalidated (κ 0.11), so it is a secondary channel.

## Data scheme (`scheme/`)
- **Inputs:** listed above; non-holdout rows only (`holdout_mask` re-applied by PT date and goal).
- **`scheme/build.py`** → `data/processed/H64-conflict-scarce-prize/` (zstd parquet, codes only):
  - `replies.parquet`: one row per DQ2 candidate pair with `pair_set = cand`, `labelled`, A and B by agents, A's author ≠ B's author, **p_reply ≥ 0.5** (the reply set; weight p_reply kept). Columns: goal, unit, PT date, t_B, room, speaker j, target i, hard class y ∈ {−1, 0, +1} (opposes / neutral or asks / supports), soft s = p_supports − p_opposes, stance_conf, confident-opposes flag (opposes, conf ≥ 0.8), position flag (confident opposes with `opp_type = position`), `opp_type` present, conversation block k (room × 30-min block of t_B; in #12, debate × phase).
  - `g12_rel.parquet`, `g26_rel.parquet`, `g23_rel.parquet`: per native reply, relation R, prize state O, window labels.
  - `g23_games.parquet`: game id hash, the two opponent agents, first and last link time (from agent chat text in memory; codes only).
- **Rules fixed now:**
  - **#12:** debaters = the debate's team rows; replies between two debaters of the same debate, B inside that debate's `pre`, `deb` or `post` window. R = opposite teams. O = 1 in `pre` and `deb`, 0 in `post`. Judge replies excluded.
  - **#26:** rivals = pairs among the three tied approval-vote candidates (agents 0, 6, 17), who contested the runoff. O = 1 from the first agent message of 2026-01-05 to the result (19:35:22 UTC); O = 0 from the result to the confirmatory vote (01-09 18:45 UTC). The confirmatory window (01-09 18:45 → end of the period, a 9–0 uncontested vote) is a third state, reported separately.
  - **#23:** a game id is a Lichess 8-character id linked in agent chat; opponents = the two agents who both link it (games linked by ≥ 3 agents dropped). A game is open from its first to its last link, plus 10 min. R = the reply's two agents are opponents in some game; O = 1 if t_B falls inside an open window of one of *their* games.
- **Regimes covered:** I, II, III (all non-holdout periods with enough replies).

## Observables
*Written 2026-10-04 19:20 UTC.*
**Replication layer (every eligible period p).**
- **O1 antagonism excess E_p.** Two-way additive fit y = μ + a_j + b_i on hard labels; residual pair means over replies in both directions; per-pair cluster-robust one-sided t-test (clusters = conversation blocks; pairs with ≥ 3 blocks and ≥ 5 replies); Benjamini–Hochberg at q = 0.1. n_neg = the number of significantly negative pairs. **E_p = n_neg − mean n_neg under the calibrated agent-field null** (ordered logit with speaker and target fields fitted to the period's hard labels, simulated 200 times on the real reply structure, same test). Reported with the null's 95th percentile and p_AF = P(null ≥ observed).
- **O2 confident position-opposition rate r_p:** share of replies with a confident "opposes" (conf ≥ 0.8) and `opp_type = position`; and r⁻_p, the confident-opposes share of any subtype. CIs from a day-cluster bootstrap (1,000).
- **O3 mean stance** ȳ_p (hard) and s̄_p (soft), day-cluster CI. Descriptive.
- **O4 naive count** n_neg with independent replies (the H37/RE-C2 per-pair t-test), next to the cluster-robust one: how much of the "antagonism" is thread clustering.
- **Prize class** (pre-registered from the period records, `period_affordances`): **assigned-sides prize** #12; **competition prize** #6 (most store profit wins), #23 (chess games), #26 (an election), #27 (most challenges solved); **rivalry without an exclusive prize** #51 (role holders compete on shared metrics; no single winner, no settlement); **prize-free** every other eligible period.

**Native layer.**
- **O5 prize-gated DiD (G12, G26, G23).** OLS of hard y on speaker and target fixed effects, a window fixed effect (debate × phase in #12; window in #26; day in #23), R, R·O and O: Δ̂ = coefficient on R·O; γ_open = rival − non-rival contrast while open, γ_set = the same after settlement. CIs: cluster bootstrap over conversation blocks (debates in #12; 1,000). Null: relation permutation within the structural unit (team labels re-drawn within debate; the rival set re-drawn among the 10 agents in #26; the opponent graph's node labels permuted in #23), 5,000 draws. Soft s as robustness; the position channel as secondary.
- **O6 resentment after settlement (G12):** among post-verdict opposite-team replies, losers → winners minus winners → losers.
- **O7 heat (G12, G26):** φ̂, the open − settled shift on non-rival pairs (teammates in #12).

**Multiplicity:** primary tests are P1 (replication), N1a, N1b, N2a, N3a (Holm across five for the headline). Everything else is secondary or descriptive.

## Null / baseline
*Written 2026-10-04 19:20 UTC.*
- **N1 calibrated agent-field null** (H37 Amendment 2; `nulls.agent_field_null`) for E_p. Size checked again here under thread shocks (S1).
- **N2 relation permutation** within the structural unit for every native DiD.
- **N3 two-way fixed effects** (speaker agreeableness, target likability) inside every contrast.
- **N4 heat and remanence:** the DiD removes a uniform open-window field (R-heat) and a constant rival-pair term (R-relation); both are planted in the synthetic runs to measure the false-call rate.
- **N5 label noise:** synthetic labels pass through a DQ2-like confusion matrix (recall − 0.45, 0 0.65, + 0.82; noisier than H37's measured matrix because DQ2's stance κ is 0.44).
- **N6 cluster-robust inference** by conversation block for every pair test and bootstrap.
- **Unit-of-analysis exception (named, CLAUDE.md):** (c) **the transition is the object** in the natives: each native compares the two sides of a dated settlement instant inside one period. The replication layer stays one period, one estimate.

## Impostors (STANDARDS §1)
| Impostor | Relevant? | How it is removed | Status |
| --- | --- | --- | --- |
| Scheduler field | no | Reply-level stance labels; no activity or co-activation statistic. Day and window fixed effects in the DiD absorb day-level label drift. | n/a |
| Exogenous field (kickoff, goal, operator) | yes: the contest *is* a field | The claim is a field claim: antagonism should follow the prize state. Agent fields and the politeness field are removed by two-way effects and the ordered-logit null; a uniform contest field (R-heat) by the DiD with non-rival pairs in the same window. | addressed by design |
| Shared model priors (family, style) | partly | Agreeableness by model family is an agent field (two-way FE). The labeller reads text, so family writing style can shift labels; the within-pair before/after design (same agents, same labeller) removes it for the DiD. | addressed in natives; replication relies on agent FE |
| Contemporaneous convergence | no (by construction) | Pairs are DQ2 candidates on ledger visibility: B's author had A in context. The in-flight placebo set (`pair_set` invisible/reversed) is not used. | n/a |

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R-protocol (H37), R-relation (remanence), R-heat (contest field on all pairs), R-null (cooperation default).
**Locked holdout used for confirmation:** none yet. Planned (`analysis/confirm.py`, frozen, not run): #34 (vote-outs: a rival-exclusive outcome with dated settlements), #51 tail (rivalry without an exclusive prize), #29 (breaking-news competition).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Rivals and prize states from DQ6 (#12, #26) and linked games (#23); stance from DQ2 (κ 0.44; pair-level opposes 0.08 precise as conflict); the replication rate r_p uses the unvalidated `opp_type = position` subtype (κ 0.11). Prize class hand-coded from the period records before the run. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | Thread clustering audited (cluster-robust pair tests, block bootstraps); additive agent fields on an ordinal scale (the calibrated ordered-logit null); stationarity within windows assumed. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | #12: the rival contrast beats team permutation (p 0.0002) and two-way agent effects; Δ beats it (p 0.001). Competition periods beat the prize-free set (Mann–Whitney p 0.022). No held-out days. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | The settlement switch-off (Δ < 0, γ_set ≈ 0) and the competition contrast (P1) were predicted, not fitted, and both hold. P3 (#12 highest r_p) failed: #40 and #23 are higher. |
| E interventional | predicts the change across a natural experiment | 1 | Ten dated verdict instants (#12): the contrast drops from −0.78 to −0.09 at settlement. The election and chess settlements are underpowered (14 and 44 rival replies while open). |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | Cluster-robust pair count calibrated (size ≤ 0.07); DiD power 0.42 / 0.78 at Δ = −1 / −2 logit in #12 (hard labels); the card's equivalence clause was not identifiable and was replaced before the run (A1). Soft and hard labels agree in #12. |
| G ground truth | agrees with known structure | 1 | DQ6 teams, phases and results reproduce the debate antagonism and its switch-off; no ground truth exists for antagonism outside #12. |
| H comparative | beats the named rivals | 1 | R-heat (teammates' open − settled shift +0.00) and R-relation (no residual contrast, no loser resentment) rejected in #12. R-protocol rejected at period level only (P1), on an unvalidated subtype; in #23 the opponent-specific contrast is not significant, which fits a contest-wide heat field. |
| I transfer | holds in other same-mode periods, including the holdout | 0 | Natives outside #12 inconclusive; holdout not run (`confirm.py` frozen, dry-run only). |

**Overall A–I (round 1):** A1 B1 C1 D1 E1 F1 G1 H1 I0. **Faithfulness lever:** E moved (0 → 1 for a dated settlement design); G unchanged at 1 (only #12 has ground truth for antagonism).

## Prediction
*Written 2026-10-04 19:20 UTC, before running any H64 statistic on real data.*

**What I had seen.** The round-1 and 1b results of H21, H22, H37, H55 and DQ2 (cards). In particular: #12 stance order switches off within 10 min of the verdict (H21 S3, H37 P5; pre-phase Δ already 0.44 in H21); #23 opponents show no stance contrast over the whole period (H22 native, −0.005); #51 rivals are friendlier than unrelated pairs; #26 stance does not track ballots. Structural counts only for H64: labelled agent→agent replies with p_reply ≥ 0.5 per period; #12 debater-to-debater replies by phase and relation (pre 39, deb 135, post 97); #26 replies by window and rival status (open 92 with 14 among the runoff three; settled 687 with 65; confirmatory 244 with 33). No H64 statistic, mean stance or opposes rate of any period was computed.

**Synthetic (axis F; run first, at real reply structures).**
| # | Prediction | Counts against |
| --- | --- | --- |
| S1 | Under agent fields plus thread shocks (σ_u = 0.5–1 logit), the naive per-pair count exceeds the agent-field null's 95th percentile in ≥ 30% of replicates (RE-C2 reproduced), and the cluster-robust count in ≤ 10% | cluster-robust size > 15% |
| S2 | The G12 DiD detects planted gated antagonism Δ = −1 logit with power ≥ 0.8; false "gated" calls (γ_open < 0 with CI below 0 *and* γ_set equivalent to 0) under R-heat and R-relation stay ≤ 10% | power < 0.5 or false calls > 20% |
| S3 | G26 and G23 have power < 0.5 at Δ = −1 logit (low-power natives; their verdicts become "inconclusive" unless the CI excludes 0) | |

**Replication layer.**
| # | Prediction [credence] | Counts against |
| --- | --- | --- |
| P1 (primary) | **Prize contrast.** The four competition-prize periods (#6, #23, #26, #27) have higher r_p than the prize-free periods: ≥ 3 of 4 above the prize-free median and Mann–Whitney one-sided p < 0.10 [0.25] | ≤ 2 of 4 above the median (R-protocol) |
| P2 | **Prize-free floor.** E_p's agent-field p_AF > 0.05 (no excess antagonistic pairs) in ≥ 80% of prize-free periods [0.6] | excess in > 20% of prize-free periods (antagonism without a prize) |
| P3 | **Assigned sides stand out.** #12 has the highest r_p of all eligible periods [0.6] | |
| P4 | **Rivalry without a prize (#51) is like prize-free:** r_51 below the prize-free 75th percentile [0.6] | |
| P5 | **Thread clustering (descriptive).** The naive count exceeds the cluster-robust count in ≥ 2/3 of periods | |

**Native layer** (each period README repeats its own prediction).
- **N1 G12 (judged debates).**
  - N1a: γ_open < 0, cluster-bootstrap CI below 0 and permutation p < 0.01 [0.9; known from H21/H37].
  - N1b: the contrast vanishes after the verdict: γ_set's 95% CI lies within ±⅓|γ̂_open|, and Δ̂ < 0 with CI below 0 [0.7].
  - N1c (R-heat): teammates' open − settled shift φ̂ has a CI that includes 0 [0.6].
  - N1d (R-relation, resentment): after the verdict, losers → winners minus winners → losers has a CI that includes 0 [0.6].
- **N2 G26 (election).** N2a: γ_open < 0 among the runoff three before the result, γ_set ≈ 0 after [credence that the CI of γ_open excludes 0: 0.15]. Expected verdict: inconclusive (14 rival replies while open). N2b (descriptive): the confirmatory window looks like the settled one.
- **N3 G23 (chess).** N3a: opponents' replies during their open games are more negative than their replies at other times, beyond non-opponent pairs at the same times (β_open < 0, CI below 0) [0.15]. Untestable if fewer than 15 opponent replies fall inside open windows.

**Hypothesis-level verdict rule.**
- **Supported:** N1b passes *and* (P1 passes or at least one of N2a, N3a passes with CI excluding 0).
- **Narrowed to "settlement switches off assigned conflict":** N1b passes, P1 fails, N2a and N3a do not pass. This reading keeps H37's protocol rival for *where* antagonism appears and adds the settlement switch-off.
- **Failed:** N1b fails (antagonism outlives the verdict), or P2 fails (antagonism appears without any prize).

**My credence before data:** supported 0.2; narrowed 0.55; failed 0.15; other 0.1.

### Synthetic validation (axis F; done 2026-10-04 ~20:00 UTC, before any real-data outcome)
`analysis/synthetic.py` → `data/processed/H64-conflict-scarce-prize/synthetic/{s1,s2}.json`. Real reply structures; hard labels from the ordered-logit model with agent fields (sd 0.6), DQ2-like label noise, block shocks σ_u and pair × block shocks σ_pb.
- **S1 (size of the antagonistic-pair count; 30 replicates per cell, 5 structures: G13, G26, G38, G41, 51g):** the cluster-robust count exceeds the agent-field null's 95th percentile in 0–7% of replicates in every cell (pass). The naive count is also near nominal (0–7%) under block shocks up to 1 logit and pair × block shocks of 1 logit. **S1's first clause fails:** thread shocks of this size do not reproduce RE-C2's inflation (70 vs 8 pairs). That inflation must come from something the shock model lacks: soft-label sums or true pair heterogeneity.
- **S2 (DiD, 100 replicates per cell, hard labels):** power for "open contrast CI below 0" at Δ = −1 / −2 logit is 0.42 / 0.78 (G12), 0.14 / 0.47 (G23), 0.06 / 0.33 (G26); size under the null 0.01–0.08; the heat rival never produces it beyond size (0.04–0.06); the relation rival does (0.12–0.33), as expected, but not with Δ < 0 (0.02–0.08). **The card's equivalence clause for γ_set (CI within ±⅓|γ̂_open|) is never met, even at Δ = −2 (0/100 in G12 and G23; 7/100 in G26): it is not identifiable at these sample sizes.** The cluster bootstrap over 10 debates is also weak for Δ (power 0.29 at Δ = −2 in G12).

### Amendment A1 (synthetic-based; written 2026-10-04 ~20:05 UTC, before any real-data outcome statistic)
1. **Primary native outcome = soft stance** s = p_supports − p_opposes (as in H21/H37), not the hard class. The hard-label synthetic power is a lower bound; hard labels are reported as robustness.
2. **N1b decision rule (replaces the equivalence clause):** the contrast "vanishes after settlement" if Δ̂ < 0 with **relation-permutation p < 0.05** (teams re-drawn within each debate), the cluster-bootstrap CI of γ̂_set includes 0, and |γ̂_set| < ½|γ̂_open|. The remanence rival predicts |γ̂_set| ≈ |γ̂_open| and Δ̂ ≈ 0.
3. **Inference for Δ and γ_open in every native** uses the relation-permutation null (primary) with the cluster bootstrap CI reported next to it.
4. **G26 and G23 are low-power natives** (S3 confirmed: power ≤ 0.47 at Δ = −2 on hard labels). Their verdict is "inconclusive" unless γ̂_open's permutation p < 0.05.
5. Predictions P1–P5 and N1a, N1c, N1d, N2, N3 are unchanged.

## Results by goal period
Replication folders: **supported** = prize-free (or #51) period with no excess antagonistic pairs, or competition period above the prize-free median; **failed** otherwise. Native folders state their own rule. r_p = confident position-opposition share of agent → agent replies (day-cluster 95% CI).

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G02](goalperiod-subhypotheses/G02/README.md) | replication | supported | prize free; r_p 0.00% [0.00, 0.00]; excess pairs 0 vs 0.09 (p_AF 1.00) |
| [G03](goalperiod-subhypotheses/G03/README.md) | replication | supported | prize free; r_p 0.12% [0.00, 0.49]; excess pairs 0 vs 0.03 (p_AF 1.00) |
| [G04](goalperiod-subhypotheses/G04/README.md) | replication | supported | prize free; r_p 0.39% [0.19, 0.62]; excess pairs 0 vs 0.01 (p_AF 1.00) |
| [G05](goalperiod-subhypotheses/G05/README.md) | replication | supported | prize free; r_p 1.08% [0.17, 2.67]; excess pairs 0 vs 0.00 (p_AF 1.00) |
| [G06](goalperiod-subhypotheses/G06/README.md) | replication | supported | competition; r_p 1.60% [0.00, 4.89]; excess pairs 0 vs 0.00 (p_AF 1.00) |
| [G08](goalperiod-subhypotheses/G08/README.md) | replication | supported | prize free; r_p 0.31% [0.00, 0.83]; excess pairs 0 vs 0.01 (p_AF 1.00) |
| [G11](goalperiod-subhypotheses/G11/README.md) | replication | supported | prize free; r_p 0.28% [0.00, 0.98]; excess pairs 0 vs 0.04 (p_AF 1.00) |
| [G12](goalperiod-subhypotheses/G12/README.md) | native | supported | assigned; r_p 3.20% [1.89, 5.18]; excess pairs 0 vs 0.03 (p_AF 1.00); native γ_open -0.78 (p 0.0002), γ_set -0.09, Δ -0.69 (p 0.001) |
| [G13](goalperiod-subhypotheses/G13/README.md) | replication | supported | prize free; r_p 1.29% [0.55, 2.22]; excess pairs 0 vs 0.03 (p_AF 1.00) |
| [G16](goalperiod-subhypotheses/G16/README.md) | replication | supported | prize free; r_p 0.65% [0.00, 1.69]; excess pairs 0 vs 0.04 (p_AF 1.00) |
| [G17](goalperiod-subhypotheses/G17/README.md) | replication | supported | prize free; r_p 0.75% [0.19, 1.32]; excess pairs 0 vs 0.02 (p_AF 1.00) |
| [G18](goalperiod-subhypotheses/G18/README.md) | replication | failed | prize free; r_p 1.45% [0.86, 2.16]; excess pairs 1 vs 0.01 (p_AF 0.02) |
| [G19](goalperiod-subhypotheses/G19/README.md) | replication | supported | prize free; r_p 1.33% [0.74, 1.96]; excess pairs 0 vs 0.01 (p_AF 1.00) |
| [G20](goalperiod-subhypotheses/G20/README.md) | replication | supported | prize free; r_p 1.15% [0.62, 1.69]; excess pairs 0 vs 0.04 (p_AF 1.00) |
| [G21](goalperiod-subhypotheses/G21/README.md) | replication | supported | prize free; r_p 1.56% [0.61, 2.95]; excess pairs 1 vs 0.07 (p_AF 0.08) |
| [G23](goalperiod-subhypotheses/G23/README.md) | native | mixed | competition; r_p 3.35% [1.20, 7.14]; excess pairs 0 vs 0.07 (p_AF 1.00); native γ_open -0.13 (p 0.3087), γ_set +0.04, Δ -0.17 (p 0.197) |
| [G24](goalperiod-subhypotheses/G24/README.md) | replication | supported | prize free; r_p 0.51% [0.00, 1.18]; excess pairs 0 vs 0.20 (p_AF 1.00) |
| [G25](goalperiod-subhypotheses/G25/README.md) | replication | supported | prize free; r_p 0.88% [0.46, 1.21]; excess pairs 0 vs 0.04 (p_AF 1.00) |
| [G26](goalperiod-subhypotheses/G26/README.md) | native | mixed | competition; r_p 1.08% [0.59, 1.70]; excess pairs 0 vs 0.04 (p_AF 1.00); native γ_open +0.25 (p 0.8632), γ_set -0.03, Δ +0.28 (p 0.889) |
| [G27](goalperiod-subhypotheses/G27/README.md) | replication | supported | competition; r_p 1.83% [1.31, 2.48]; excess pairs 0 vs 0.05 (p_AF 1.00) |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | supported | prize free; r_p 1.35% [0.89, 1.86]; excess pairs 0 vs 0.02 (p_AF 1.00) |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | supported | prize free; r_p 1.26% [0.82, 1.67]; excess pairs 0 vs 0.01 (p_AF 1.00) |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | supported | prize free; r_p 1.49% [0.99, 2.90]; excess pairs 0 vs 0.08 (p_AF 1.00) |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | supported | prize free; r_p 2.84% [2.39, 3.30]; excess pairs 0 vs 0.01 (p_AF 1.00) |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | supported | prize free; r_p 0.57% [0.00, 1.56]; excess pairs 0 vs 0.56 (p_AF 1.00) |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | supported | prize free; r_p 0.58% [0.40, 0.79]; excess pairs 1 vs 1.03 (p_AF 0.64) |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | supported | prize free; r_p 0.73% [0.42, 1.04]; excess pairs 0 vs 0.12 (p_AF 1.00) |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | supported | prize free; r_p 3.67% [0.38, 6.27]; excess pairs 0 vs 0.07 (p_AF 1.00) |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | supported | prize free; r_p 1.93% [0.78, 3.39]; excess pairs 0 vs 0.03 (p_AF 1.00) |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | supported | prize free; r_p 0.50% [0.00, 0.80]; excess pairs 0 vs 0.64 (p_AF 1.00) |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | supported | prize free; r_p 0.99% [0.50, 1.52]; excess pairs 0 vs 0.20 (p_AF 1.00) |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication | supported | 12 units; r_p 0.56–2.85%; units with excess pairs 1/12 |

## Results
*Round 1, 2026-10-04 (UTC). Code: `scheme/build.py`; `analysis/{h64lib,synthetic,run,period_folders,estimates_rows,figures,confirm}.py`. Data: `data/processed/H64-conflict-scarce-prize/` (`replies.parquet`, `g12_rel`, `g26_rel`, `g23_rel`, `g23_games`, `replication/{units,summary}.json`, `natives/G*.json`, `synthetic/`, `confirm/dryrun.json`; 3 MB). Figures: `figures/h64_obs.pdf`, `figures/h64_synth.pdf`. 190 rows in `per_period_estimates`.*

**Headline.** A judged prize switches stance antagonism on and its settlement switches it off; competition without assigned sides raises disagreement across the whole room, not between rivals.
1. **#12 debates (native, 10 dated verdicts).** While the prize is open, opponents treat each other 0.78 [0.56, 1.10] (soft stance units) worse than teammates (team permutation p 0.0002; hard labels −0.85). After the verdict the contrast is −0.09 [−0.39, +0.26]; Δ = −0.69 [−1.20, −0.27], p 0.001 (hard labels −0.65, p 0.016). Teammates do not change across settlement (φ +0.00 [−0.24, +0.34]): no heat field. Losers are not colder to winners than winners to losers (+0.19 [−0.04, +0.33], n 64): no remanence.
2. **Competition periods (replication P1).** The confident position-opposition rate is 1.08–3.35% of replies in #6, #23, #26 and #27, all four above the prize-free median 0.94% (Mann–Whitney p 0.022; within regime I alone, post hoc: median 0.88%, p 0.010). Any-subtype confident opposes: 3/4 above, p 0.11. Mean soft stance is lower in competition periods (0.38–0.64 vs median 0.57; p 0.18).
3. **But not between rivals.** In #23 chess, opponents' replies during their own open games are −0.13 [−0.41, +0.25] vs other pairs (node permutation p 0.31; 44 replies), and opponents outside games +0.04. In #26 the three runoff candidates are +0.25 [−0.51, +0.45] toward each other before the result (14 replies; exact permutation p 0.86). Both are low-power natives (synthetic power ≤ 0.47 at 2 logit).
4. **Floor (P2, P4).** 25/26 prize-free units and 11/12 #51 units have no more significantly negative pairs than the calibrated agent-field null (cluster-robust, BH 0.1). #51's rate (1.06% [0.85, 1.32]) is inside the prize-free range. The pair count has low power: it finds 0 pairs in #12 too, because re-drafting mixes each pair across both relations.
5. **P3 failed:** #12 (3.20%) is third; #40 (3.67%, the merged universe-coordination week; H37 saw 20% "opposes" there, mostly corrections) and #23 (3.35%) are higher.

### Outcome vs prediction
| Prediction | Observed | Verdict |
| --- | --- | --- |
| S1 cluster-robust pair count sized ≤ 10%; naive inflated ≥ 30% | robust 0–7%; naive also 0–7% under ≤ 1-logit thread shocks | half (RE-C2 inflation not reproduced) |
| S2 #12 DiD power ≥ 0.8 at Δ = −1; equivalence identifiable | 0.42 (Δ −1), 0.78 (Δ −2); equivalence never met | failed → Amendment A1 |
| P1 competition > prize-free r_p (≥ 3/4 above median, p < 0.10) [0.25] | 4/4, p 0.022 | **pass** |
| P2 no excess pairs in ≥ 80% of prize-free units [0.6] | 25/26 (96%) | pass (low-power test) |
| P3 #12 highest r_p [0.6] | third (#40, #23 higher) | fail |
| P4 #51 below prize-free 75th percentile [0.6] | 1.06% < 1.35% | pass |
| P5 naive > robust count in ≥ 2/3 (descriptive) | 7/43 | fail |
| N1a #12 open contrast < 0, p < 0.01 [0.9] | −0.78, p 0.0002 | **pass** |
| N1b contrast vanishes at the verdict (A1 rule) [0.7] | Δ −0.69 (p 0.001); γ_set −0.09, CI ∋ 0, < ½|γ_open| | **pass** |
| N1c no heat on teammates [0.6] | +0.00, CI ∋ 0 | pass |
| N1d no loser resentment [0.6] | +0.19, CI ∋ 0 | pass |
| N2a #26 runoff rivals < 0 while open [0.15] | +0.25 (14 replies), p 0.86 | not passed (inconclusive) |
| N3a #23 opponents < 0 in open games [0.15] | −0.13, p 0.31 | not passed (inconclusive) |

**Verdict by the card's rule:** N1b passes and P1 passes → **supported (exploratory)**. Holm over the five primaries: N1a 0.001, N1b 0.004, P1 0.066, N2a 1, N3a 1. The reading is narrower than HH255: settlement switches off *assigned* antagonism within one conversation phase, and an open prize raises disagreement period-wide; neither the election nor chess shows rival-specific antagonism.

### Physics reading
In the Mattis picture the contest is a staggered field h on two camps. The #12 data say the stance order follows the field with no measurable remanence: the induced antagonism relaxes to the ferromagnetic background (mean soft stance +0.45) within the post-verdict phase (≤ 10 min). Competition without assigned camps acts like a uniform field that lowers the agreement level on every bond, not a staggered one: R-heat holds at the period level, while inside #12 R-heat is rejected. No coupling-borne antagonism (δ_rel) appears anywhere.

### Caveats
1. **P1 rests on DQ2's unvalidated `opp_type = position` subtype** (κ 0.11, 3 blind items). The any-subtype rate gives the same order but p 0.11.
2. Four competition periods, all in regime I, and #40 is a prize-free outlier; the contrast could be topic (competitions talk about scores and rules) rather than incentive.
3. The cluster-robust pair test has little power (it misses #12); P2's "floor" is weak evidence.
4. #26 and #23 natives are underpowered (14 and 44 rival replies while open); #23's opponent list uses chat links only (13 games vs H22's 28 from chat, intentions and commands).
5. Stance is labelled by one zero-shot model (κ 0.44); the labeller saw both messages and the names, not the prize state.
6. The #12 switch-off was known from H21/H37 (disclosed in the prediction); H64's new parts are the DiD with heat/remanence tests and the competition contrast.

### Confirmatory test (frozen 2026-10-04 after round 1; `analysis/confirm.py`, **not run**)
Guards: refuses without `--confirm --i-understand-this-uses-the-locked-holdout` and with uncommitted changes in the H64 folder. Dry run on stand-ins (#27, #26 with stand-in vote-outs, 51h–51l) runs end to end (`confirm/dryrun.json`). Ledger: #29 unused; #34 used by H05 (activity) and planned by H37 (stance, saboteurs); #51 tail planned by H37. H64's statistics (position-opposition rate; a vote-out DiD) have not been computed on these targets.
- **C1 (primary):** r_p(#29) > 0.94%. Credence 0.6. **C2 (primary):** r_p(#34) > 0.94%. Credence 0.5.
- **C3:** #34 vote-outs: replies involving the agent voted out are more negative in the 2 h before its move to #voted-out than in the preceding 30 h, beyond other replies (accused-label permutation p < 0.05). Credence 0.3.
- **C4:** r_p(#51 tail) < 1.35% and at most half of the tail units show excess pairs. Credence 0.6.
- **Decision:** "competition raises position-opposition" confirmed if C1 and C2 pass; the settlement switch-off generalizes beyond debates if C3 passes.

## Round 2 redirects
**What the direction is really after:** what in an incentive structure makes LLM agents disagree, and how fast the disagreement relaxes when the incentive is removed.
- **H64-R1. Validate the conflict sensor.** A blind second rater on 100 confident-opposes replies from competition and prize-free periods: precision of `position` by class. P1 stands or falls with it.
- **H64-R2. Rival-specific vs room-wide.** In #23 and #27, label each reply's target as rival or not with more games (H22's chat + intentions + commands rule) and test whether the competition excess is on rival bonds or spread.
- **H64-R3. Relaxation time.** Fit the post-verdict decay of the #12 contrast at minute resolution (exponential vs step) as a field switch-off time constant.
- **H64-R4. Run `confirm.py`** after committing (#29, #34, #51 tail).

## Notes
- 2026-10-04: promoted from HH255 by Vivian.
- 2026-10-04 19:20 UTC: round-1 agent started; question, model, scheme, observables, nulls, impostor table and predictions written before any H64 outcome statistic.
- 2026-10-04 ~20:00 UTC: synthetic validation; ~20:05 UTC Amendment A1 (soft outcome, N1b rule, permutation inference); 20:10 UTC per-period predictions written in the G folders; then the real-data run.
- 2026-10-04: the first replication pass read the position flag as null where `opp_type` was missing (NaN rates); fixed in `scheme/build.py` (null → False) and the replication re-run before any result was read into the card.
- Compute: local, ≤ 4 then ≤ 2 workers (coordinator's load notice); synthetic ≈ 15 min, real run ≈ 5 min. Disk 3 MB.
- **Proposed shared changes** (not made): DEFINITIONS.md named variants *prize state (open / settled)*, *rival pair (exclusive prize)*, *prize-gated antagonism Δ (DiD)*, *antagonism excess E (cluster-robust)*. infra/README Known issues: (1) DQ2-scale thread shocks (≤ 1 logit, block or pair × block) do not inflate the naive negative-pair count in synthetic runs, so RE-C2's 70-vs-8 excess is more likely true pair heterogeneity or soft-label summing; (2) the cluster-robust per-pair test (≥ 3 blocks) has low power on village reply graphs (0 pairs in #12).
