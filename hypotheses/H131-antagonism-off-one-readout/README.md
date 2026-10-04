# H131: Assigned antagonism switches off in one read-out after the prize goes: a field quench with no remanence

**Status:** exploratory round 1 **done (2026-10-04): narrowed by the pre-registered rule.** Assigned antagonism is fully off by each former rival's first reply after it reads the verdict. The HH's kill test (read vs wall clock) is untestable on non-holdout data: no reply falls between a verdict and its speaker's read.
- **Debates (#12, ten verdicts):** while the prize is open, 34/85 rival replies carry a validated disagreement flag against 0/87 teammate replies. After the speaker's read, rivals are at 0/57 and teammates at 0/33. Read-gated DiD Δ +0.32 [+0.16, +0.52], permutation p 0.0002.
- **Each speaker's first post-read rival reply:** 0/21 flagged, against 0.45 while open (p 0.0002). On the soft scale a residual of about 7% of the open level remains (0.031 vs 0.45).
- **#26 election:** no antagonism to switch off (0/14 rival replies flagged while open; P1 power 0.11): inconclusive.
- **Synthetic (A1):** read- and clock-gated prize states coincide on 262/262 #12 replies. P1 power 0.65; N2 power 0.43, against 0.05–0.12 under remanence or clock-delay worlds.
- **Timing:** card written 22:19–22:24 UTC and Amendment A1 ~23:03 UTC, both before any outcome. `analysis/confirm.py` is frozen and dry-run, **not run**.
**Question (GOALS.md):** **Q1** (what couples agents: is the verdict's effect on stance gated by each agent's read-out of it, as H08 found for responses?). Second: **Q2** (antagonism as a field: does it vanish when the field goes, with no remanence?).
**Fields:** sociophysics, stat mech (kinetic Ising quench)
**Literature:** none in `literature/` covers stance relaxation after a quench. Cited from memory (†): Glauber, *J. Math. Phys.* 4, 294 (1963)† (single-spin-flip kinetics; relaxation in ≈ one update per spin when the coupling is weak); Mattis, *Phys. Lett. A* 56, 421 (1976)† (two-camp antiferromagnet as a gauge-transformed ferromagnet, as in H64).
**Definitions used** (`physics-models/DEFINITIONS.md`): Agent; Regime; Driving / external field (the contest incentive); Exposure (turn read-out) (H08), implemented by the DQ1 context ledger (receiving call of the verdict message); H64's **prize state O(t)**, **rival pair (exclusive prize) R_ij** and **prize-gated antagonism Δ**, used as defined there. New named variants proposed for DEFINITIONS.md (not edited there; defined under Observables): **prize state, read-gated O_j(c)**, **verdict read-out call**, **post-read call index k**, **in-flight reply (verdict)**, **read-out relaxation kernel r(k)**, **conflict flag (stance v2.1, agent)** for `disagree_validated_agent`.
**From:** HH374 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/02-nonequilibrium-ising/` (kinetic Ising: each agent updates at its own calls; field removal; primary), `physics-models/10-potts/` (two camps as a q = 2 Mattis state)

## Source HH (verbatim from the HH list, including refinements)
- **HH374 · Assigned antagonism switches off in one read-out after the prize goes: a field quench with no remanence.** H64 found assigned antagonism switches off within minutes of a verdict and leaves no resentment. In a kinetic Ising model with the field removed and weak coupling, the order decays in about one update per agent.
  - *Prediction:* the opposing-stance rate between former rivals falls to the baseline within each agent's first call after it reads the verdict, not on a wall-clock time; agents who read the verdict later switch later.
  - *Check:* verdict times in #12, #6, #27 and #29 competitions; per-agent first read of the verdict (context ledger); stance labels (DQ2 aggregate; stance v2.1 if it passes).
  - *Kill:* the switch-off is aligned to wall-clock time, not to each agent's read.
  - *Impostors:* the end of the competition period is a field step for everyone; the per-agent read timing is the partition contrast.
  - *Models:* 02, 10 · *Builds on:* H64, H37, H08

## Standards (2026-10-04)
**Question served:** Q1 (second: Q2).

| Impostor | Relevant? | How it is handled | Status |
| --- | --- | --- | --- |
| Scheduler field | partly | Stance is a reply-level label, not an activity statistic. The read-out call comes from the ledger, so idle time is not counted as exposure. Debate phase and debate fixed effects absorb timing differences between phases. | n/a for activity; phase FE |
| Exogenous field (kickoff, goal, operator) | yes: the verdict is the field step | The verdict is a field step for everyone at one wall-clock instant. The HH's partition contrast is per-agent read timing: replies posted after the verdict but produced by a call assembled before the speaker read it (in flight) should keep the open-prize stance. **That partition is empty in #12 and #26 (structural count, below)**, so the clock and read alignments cannot be told apart on non-holdout data. | open (partition empty) |
| Shared model priors (family, style) | partly | Speaker agreeableness and target likability enter as speaker and target effects; the DiD compares the same agents across relations and settlement; the labeller (stance v2.1) reads text, so family style shifts labels equally across relations. | partly |
| Contemporaneous convergence | no | Replies are DQ2 candidate pairs on ledger visibility (B's author had A in context). No copying or influence claim is made. | n/a |

**Inputs:** `reply_stance_v2` (DQ10 stance v2.1; `disagree_validated_agent` primary, `p_disagree` and `s2_soft` secondary), DQ2 `reply_pairs` keys (via `reply_stance_v2`), DQ6 `ground_truth_labels` (`preferred & ~holdout`: #12 teams, judges, phases, verdict messages; #26 phases, runoff candidates, result message), DQ1 context ledger via `infra/shared/visibility.py` (`receipts` of the verdict messages; `producing_calls` for each reply's producing call), `call_windows` (talk calls), `chat_core` (message times). No text is read.

**Two layers:** replication: the read-aligned settlement DiD on every non-holdout period with a DQ6-dated prize settlement and rival pairs (#12, #26) (role `replication`). Natives (role `native`): G12 in-flight partition (the HH's kill test), G12 read-out relaxation kernel (one read-out), G12 switch-on at the team assignment (the reverse quench), G26 runoff result.

**Unit-of-analysis exception (named):** (c) **the transition is the object**: every test compares the two sides of a dated settlement (or assignment) inside one period. Periods are not pooled.

**Periods named by the HH but not usable:** #6 and #27 have no DQ6-dated verdict, and a search of human chat in memory for a winner announcement found none (the winner was not announced inside the period). #29 is held out (confirmation only). #23's game ends are not messages that agents read, so they are not read-out events.

## Question
When a contest is settled, does each former rival stop disagreeing with its rivals at its own first call after it reads the verdict, rather than at a common wall-clock time? And is the first post-read reply already at the baseline (no remanence), as a kinetic Ising spin relaxes in one update when the field is removed and the coupling is weak?

**Practical payoff:** if antagonism is a read-gated field, an operator ends a conflict by making sure every party reads the settlement; the conflict ends one call later, with no cool-down.

## Model
**From:** `physics-models/02-nonequilibrium-ising/` (kinetic Ising, asynchronous updates at each agent's calls) with the two-camp field of `physics-models/10-potts/` (q = 2, Mattis).

**H131 variant: read-gated field quench on reply bonds.** A reply e by agent j (speaker) to agent i's message, produced by j's call c, carries a latent conflict indicator z_e ∈ {0, 1}:
logit P(z_e = 1) = μ + u_j + v_i + h · R_ij · O_j(c) + r_rel · R_ij + φ · O_j(c) + w_debate,phase,
and the observed flag y_e = `disagree_validated_agent` passes through the labeller's confusion: P(y = 1 | z = 1) = ρ (recall ≈ 0.6), P(y = 1 | z = 0) = ε (false-positive rate ≈ 0.005, from the population flag rate 1.3% and precision 0.61–0.67).
- R_ij = 1 for rivals (opposite debate teams; runoff candidates).
- **Read-gated prize state O_j(c)** = 1 while the prize is open *for j*: j's call c was assembled before j's verdict read-out call (t_call(c) < t_read,j). The **clock-aligned rival** uses O(t) = 1[t_post < t_verdict + δ] for a common delay δ.
- **Relaxation (remanence) variant:** after the read, h decays over j's talk calls: h_k = h · e^{−(k − 1)/κ}, k = 1 at the read-out call. H131 says κ → 0 (h_1 ≈ 0: the first post-read reply is at baseline). Remanence rival: κ ≥ 3 calls; clock-decay rival: h decays in wall time with τ ≈ 5 min.
- **Glauber reading:** with coupling J ≪ 1 and the field removed, each spin relaxes to the paramagnetic background at its next update; read-out gating (H08) makes "next update" = the first call that has the verdict in context.

**Rivals.**
- **R-clock (the HH's kill):** the switch-off is aligned to wall-clock time (the verdict instant plus a common delay), not to each agent's read.
- **R-remanence (slow relaxation):** antagonism decays over several post-read calls (κ ≥ 3) or minutes.
- **R-relation (H64's remanence rival):** rival pairs stay antagonistic after settlement (r_rel < 0).
- **R-heat:** the open prize raises disagreement on every pair (φ), not only between rivals.

## Data scheme (`scheme/`)
`scheme/build.py` builds `data/processed/H131-antagonism-off-one-readout/` (codes only).
- **Replies:** `reply_stance_v2` rows with `labelled`, A by an agent (`a_kind` agent), A's author ≠ B's author, non-holdout (re-masked by PT date and goal). Columns kept: goal, unit (debate id or #26 window), speaker j, target i, t_B, y (`disagree_validated_agent`), p_disagree, s2_soft, the producing call t_call_prod (`producing_calls`), relation R, read status, clock status, post-read call index k.
- **#12:** debaters = the debate's `gov`/`opp` team rows (DQ6; judges and bench excluded as speakers and targets); a reply belongs to debate d if t_B is inside d's window [team start, team end). Phases: `pre` and `deb` = open, `post` = settled (H64's rule). Verdict message = the `debate_result` row's source message.
- **#26:** rivals = pairs among the three runoff candidates (agents 0, 6, 17). Open = from the first agent message of 2026-01-05 to the runoff result (19:35:22 UTC); settled = from the result to the confirmatory vote (01-09 18:45 UTC). Verdict message = the `phase = result` row of round 1.
- **Read-out:** t_read,j = t_call of j's receiving call for the verdict message (`visibility.receipts`). Read status of a reply: t_call_prod ≥ t_read,j (`seen_by_receipt`). Clock status: t_B ≥ t_verdict. **In-flight reply (verdict):** clock status 1 and read status 0.
- **Post-read call index k:** 1 + the number of j's talk calls (`call_windows.talk`) with t_read,j ≤ t_call < t_call_prod (k = 1: produced by the read-out call or j's first talk call after it).
- **Switch-on (native N3):** the `pre` phase message (team assignment) of each debate plays the verdict's role; k counts talk calls after reading it.
- **Output:** `replies.parquet`, `reads.parquet` (debate × agent read delays), `_provenance.json`; results under `results/`, `synthetic/`.
- **Regimes covered:** I (both #12 and #26 are regime I).

## Observables
*Specified 2026-10-04 22:19–22:24 UTC.*
- **O1 read-aligned settlement DiD (replication, G12 and G26):** linear probability model of y on speaker and target fixed effects, a debate × phase (or window) effect, R, R·O and O, with O = the read-gated prize state; Δ̂ = coefficient on R·O; γ_open = rival − mate contrast while open, γ_set = the same after the speaker's read. Inference: relation permutation within the structural unit (team labels re-drawn within each debate; the rival set re-drawn among the period's agents in #26), 5,000 draws; cluster bootstrap over debates for CIs. Soft p_disagree as a secondary outcome.
- **O2 in-flight partition (native, the kill test):** rival flag rate among in-flight replies vs read replies after the verdict instant. Testable only with ≥ 10 in-flight rival replies.
- **O3 read-out relaxation kernel r(k) (native, one read-out):** rival flag rate by post-read call index, k = 1 vs k ≥ 2; compared with the open-prize rival rate r_open (the `deb` phase) and the mate rate after the read.
- **O4 switch-on kernel (native):** after the team assignment, the rival flag rate in each speaker's k = 1 replies vs its later open-prize replies (`deb` phase).
- **O5 read delays (descriptive):** t_read,j − t_verdict per debater and debate.
- **Labeller confusion in every null:** synthetic labels pass through recall ρ ∈ {0.55, 0.6, 0.65} and false-positive rate ε ∈ {0.004, 0.006}; the observed-rate contrasts are attenuated by ρ and floored at ε, so every effect size is reported on the flag scale and the latent scale (divide the contrast by ρ).

## Null / baseline
- **N1 relation permutation** within debates (team labels re-drawn, 5,000 draws) for every contrast involving R.
- **N2 synthetic worlds on the real #12 skeleton (axis F), run first:** (W0) no antagonism; (W1) read-gated quench with κ → 0 (H131); (W2) clock-gated quench at the verdict instant; (W3) clock-gated with a common delay δ = 2 or 5 min; (W4) remanence κ = 3 and 6 calls; (W5) clock decay τ = 5 min; (W6) relation-bound antagonism (no settlement effect). Open-prize rival latent rate 0.2–0.35, baseline 0.03, labeller confusion as above, 500 replicates per world. Measures the size and power of O1–O4 and whether R-clock and H131 are distinguishable at all.
- **N3 two-way fixed effects** (speaker agreeableness, target likability) in O1.

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R-clock (wall-clock switch-off), R-remanence (slow relaxation over calls or minutes), R-relation (pair-bound antagonism), R-heat (contest-wide field).
**Locked holdout used for confirmation:** none yet. Planned: held-out periods with a DQ6 settlement message (scan of #29, #34, #45–#50, #1, #14, #15, #28, #43; `analysis/confirm.py`, frozen, not run).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | DQ6 rivals and verdicts; DQ1 read-out; validated stance flag; regime I only |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | read-gating audited (0 in flight); agent and phase effects |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 2 | #12 DiD p 0.0002 vs team permutation |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | first post-read rival reply 0/21 (predicted); read alignment untestable |
| E interventional | predicts the change across a natural experiment | 1 | ten dated verdicts; no read/clock partition |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 | synthetic on the real skeleton before data (A1) |
| G ground truth | agrees with known structure | 2 | DQ6 teams and verdicts |
| H comparative | beats the named rivals | 1 | R-relation and remanence rejected; R-clock not separable; topic-change rival open |
| I transfer | holds in other same-mode periods, including the holdout | 0 | #26 has no antagonism; holdout not run |

## Prediction
*Written 2026-10-04 22:19–22:24 UTC, before running the analysis on real data.*

**What I had seen when writing this:** H64's card in full (#12: opponents 0.78 soft-stance units more negative than teammates while open, −0.09 after the verdict, Δ −0.69; no heat, no resentment; DiD power 0.42 / 0.78 at 1 / 2 logit on hard DQ2 labels), the H21/H37 status lines (#12 order switches off within ≈ 10 min of the verdict), DQ10's validation of stance v2.1 (`disagree_validated` precision 0.67 [0.54, 0.80], recall ≈ 0.6; 707 flags in 55k pairs), and H08 (responses are gated at the read-out call). **Structural counts only for H131 (no stance value):** verdict read delays in #12 (median per debate 10–66 s, maximum 366 s) and #26 (2–83 s); the reply counts by relation × clock status × read status in #12 (debater windows extended 30 min: rival 85 before / 228 after the verdict, mate 87 / 114) and #26 (±3 h: rival 14 / 41, other 82 / 130). **In both periods no rival reply posted after the verdict was produced before its speaker read the verdict (in-flight rival replies: 0 in #12, 0 in #26; one non-rival in #26).** That makes the HH's kill test untestable on non-holdout data; it is declared here, before any outcome.

**Synthetic (axis F; run first, on the real #12 and #26 reply structures).**

| # | Prediction | Counts against |
| --- | --- | --- |
| S1 | The read-gated (W1) and clock-gated (W2) worlds give identical O1–O3 statistics on the real skeleton (the in-flight partition is empty), so O2 has power = size; with a common delay δ ≥ 2 min (W3) the read-aligned O3 kernel shows k = 1 replies above baseline | W1 and W2 distinguishable at ≥ 0.3 power |
| S2 | O1 (read-aligned DiD, flag outcome) has power ≥ 0.8 in #12 at a latent open-rival rate 0.3 vs 0.03 | power < 0.5 |
| S3 | O3 (k = 1 vs k ≥ 2) has power < 0.5 against remanence κ = 3 calls (a low-power native) | power ≥ 0.8 |

**Replication layer.**

| # | Prediction [credence] | Counts against |
| --- | --- | --- |
| **P1** (primary) | **Read-aligned switch-off.** In #12: Δ̂ < 0 with relation-permutation p < 0.05, γ_set's bootstrap CI contains 0 and \|γ̂_set\| < ½\|γ̂_open\| [0.7]. In #26: low power; verdict inconclusive unless γ_open's permutation p < 0.05 [0.1] | Δ̂ ≥ 0, or γ_set CI below 0 with \|γ̂_set\| ≥ ½\|γ̂_open\| (R-relation) |

**Native layer** (each repeated in its period README).

| # | Unit | Prediction [credence] | Counts against |
| --- | --- | --- | --- |
| **N1** (HH kill test) | G12 | In-flight rival replies keep the open rate; read replies drop. **Untestable (0 in-flight rival replies; declared before outcomes)** | **(kill) in-flight replies drop like read replies** |
| **N2** (one read-out) | G12 | The rival flag rate at k = 1 equals the post-read baseline: r(k = 1) − r(k ≥ 2) 90% CI contains 0 and r(k = 1) < r_open (one-sided relation-permutation p < 0.05) [0.45] | r(k = 1) ≥ r_open (remanence) |
| N3 (switch-on) | G12 | The field switches on in one read-out of the team assignment: the rival flag rate at k = 1 after the `pre` message is not below the `deb`-phase rival rate (r_on(k = 1) − r_deb 90% CI contains 0 or is above 0) [0.4] | r_on(k = 1) well below r_deb (CI below 0): antagonism builds up |
| N4 | G26 | Runoff rivals' flag rate falls after each one's read of the result. Expected inconclusive (14 open rival replies) [0.1] | — |

**Hypothesis-level verdict rule.** **Supported** only if N1 is testable and passes and P1 passes. **Narrowed ("settlement switches assigned conflict off by the first post-read reply")** if P1 and N2 pass with N1 untestable. **Failed** if the kill fires (N1 testable and in-flight replies drop) or P1 fails toward R-relation. **Inconclusive** otherwise, including N1 untestable and N2 not passed.

**My credence before data:** supported 0.0 (N1 untestable); narrowed 0.35; inconclusive 0.5; failed 0.15.


### Amendment A1 (2026-10-04 ~23:03 UTC; after the synthetic, before any stance outcome was read)
Synthetic: `analysis/synthetic.py` → `data/processed/H131-antagonism-off-one-readout/synthetic/` (`g12.parquet`, `g26.parquet`, `summary.json`). 100 replicates per world on the real #12 skeleton (262 debater replies) and #26 skeleton. Open-rival latent rate 0.3, baseline 0.03, labeller recall 0.55–0.65 and false-positive rate 0.004–0.006. The real flags were never loaded.

| World | P1 pass | N2 pass | N3 pass |
| --- | --- | --- | --- |
| W0 no antagonism | 0.02 | 0.00 | 0.97 |
| **W1 read-gated, κ → 0 (H131)** | **0.65** | **0.43** | 0.95 |
| W2 clock-gated at the verdict | 0.63 | 0.25 | 0.90 |
| W3 clock + 2 min / 5 min | 0.26 / 0.09 | 0.08 / 0.06 | 0.89 / 0.92 |
| W4 remanence κ = 3 / 6 calls | 0.37 / 0.30 | 0.05 / 0.08 | 0.94 / 0.87 |
| W5 clock decay τ = 5 min | 0.32 | 0.12 | 0.93 |
| W6 relation-bound | 0.03 | 0.03 | 0.93 |
| WON2 switch-on builds up | 0.53 | 0.17 | 0.78 |
| #26 (W0 / W1 / W6) | 0.02 / 0.11 / 0.01 | — | — |

**Findings:**
1. **S1 confirmed:** in #12 the read-gated and clock-gated prize states disagree on 0 of 262 replies. In #26 they disagree on 13 replies, all non-rival. The HH's kill test (N1) is untestable on non-holdout data; W1 and W2 differ only by sampling noise.
2. **S2 failed:** P1's power is 0.65, not ≥ 0.8. Its size is 0.02–0.03 under W0 and W6. It passes 0.09–0.37 of the time under slow-relaxation worlds, because its γ_set clause partly catches remanence.
3. **S3 confirmed:** N2 is a low-power native (0.43 under W1; 0.05–0.12 under remanence or clock-delay worlds). A pass is informative (likelihood ratio ≈ 4–8 against the slow worlds); a non-pass is not.
4. **N2's "counts against" clause (r_first ≥ r_open) is not specific:** it fires in 49% of W0 and 50% of W6 replicates, where there is no settlement effect at all, against 14–37% in remanence worlds.
5. **N3 does not discriminate:** it passes 0.78–0.97 in every world, including the build-up world WON2.

**Pre-data changes:**
1. **Sign convention:** the outcome is the conflict flag (higher means more disagreement), so the settlement effect is **Δ̂ > 0**. The relation permutation is one-sided upward. The "Δ̂ < 0" wording in P1 above was copied from H64's stance scale (support − oppose) and is corrected here.
2. **N2 kernel cell:** the k = 1 cell held 6 rival replies (structural count). The test now compares **each speaker's first post-read rival reply in each debate** (21 replies; median k = 2) with its later post-read rival replies (36). The switch-on version compares each speaker's first rival reply after reading the team assignment (36) with its later `deb`-phase rival replies (46).
3. **N2 verdict:** supported if it passes. Otherwise "not passed (inconclusive)"; the non-specific fail clause is dropped.
4. **N3 is demoted to descriptive.**
5. **Verdict rule, restated:**
   - **Narrowed ("assigned conflict ends by the first post-read reply")** if P1 and N2 both pass.
   - **Failed** if P1 fails toward R-relation (γ_set CI excluding 0 with |γ̂_set| ≥ ½|γ̂_open|).
   - **Inconclusive** otherwise.
   - "Supported" is not reachable on non-holdout data, because N1 is untestable.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G12](goalperiod-subhypotheses/G12/README.md) | exploratory (replication + natives) | supported (narrowed) | DiD Δ +0.32 [+0.16, +0.52], p 0.0002; rivals open 34/85, after read 0/57; first post-read rival reply 0/21; in-flight 0 (N1 untestable) |
| [G26](goalperiod-subhypotheses/G26/README.md) | exploratory (replication + native) | mixed (inconclusive) | Δ −0.01 [−0.04, +0.02], p 0.72; 6 flags in 779 replies; power 0.11 |

## Results
*Round 1, 2026-10-04 (UTC). Code: `scheme/build.py`; `analysis/{h131lib,synthetic,run,write_rows,confirm}.py`. Data: `data/processed/H131-antagonism-off-one-readout/` (`replies.parquet`, `reads.parquet`, `synthetic/`, `results/results.json`; < 1 MB). Figure: `figures/h131_obs.pdf`. Estimates: 16 rows in `per_period_estimates`.*

**Headline.** A judged prize turns stance antagonism on between drafted rivals and off at settlement. By each rival's first reply after it reads the verdict, the antagonism is gone (0/21). On non-holdout data the read-out alignment cannot be separated from wall-clock alignment, because every post-verdict reply was produced after its speaker read the verdict.

### Outcome vs prediction
| Prediction | Credence | Observed | Verdict |
| --- | --- | --- | --- |
| S1 read and clock indistinguishable | — | 0/262 #12 replies differ in prize state | confirmed |
| S2 P1 power ≥ 0.8 | — | 0.65 | failed (A1) |
| S3 N2 power < 0.5 against remanence | — | 0.05–0.12 (0.43 under H131) | confirmed |
| P1 #12 read-gated switch-off | 0.7 | Δ +0.32 [+0.16, +0.52], p 0.0002; γ_set +0.03 [−0.04, +0.18], below ½ of γ_open (+0.35) | **pass** |
| P1 #26 | 0.1 | Δ −0.01, p 0.72 | inconclusive |
| N1 kill test (in-flight replies) | — | 0 in-flight rival replies (#12 and #26) | **untestable** |
| N2 first post-read reply at baseline | 0.45 | 0/21 vs open 0.45 (p 0.0002); later 0/36 | **pass** |
| N3 switch-on in one read-out (descriptive after A1) | 0.4 | first post-assignment rival reply 0.44 vs later 0.39 | consistent; not discriminating |
| N4 #26 | 0.1 | 0/14 open rival flags | inconclusive |
| **Overall (A1 rule)** | narrowed 0.35 | P1 and N2 pass; N1 untestable | **narrowed** |

### Physics reading
In the kinetic Ising picture, the debate is a staggered field on two camps. Removing the field leaves no measurable order by each spin's first observed post-read update: the order relaxes in about one update, so coupling-borne antagonism (remanence) is ≤ 7% of the open level on the soft scale and 0 on the validated flag. That matches HH374's weak-coupling quench. Whether the update is clocked by the read-out (H08) or by the wall clock is not identifiable, because in regime-I chat mode the read follows the verdict within a median 20 s and the first rival reply comes later (median 93 s).

### Caveats
1. The `post` phase ends the debate protocol, so a topic change also removes disagreement (H37's protocol rival). The teammate contrast while open (0/87) shows the open-phase antagonism is relation-specific; the switch-off itself cannot exclude "nothing left to argue about".
2. All 34 flags come from one period with ten debates. The cluster bootstrap over debates is coarse.
3. The flag has precision 0.61–0.67 and recall ≈ 0.6. Zero flags after the read bounds the latent post-read rival rate at roughly ≤ 0.08 (95%, 57 replies, recall 0.6).
4. The first post-read rival reply sits at a median of k = 2 talk calls after the read; only 6 sit at k = 1.

### Confirmatory test (frozen 2026-10-04 after round 1; `analysis/confirm.py`, **not run**)
- **Guards:** `--confirm`, `H131_CONFIRM=1`, a SHA-256 match (`analysis/confirm.sha256`) and `holdout_ledger.check`. The dry run on #12 and #26 reproduces the round-1 counts (`confirm_dryrun.json` in `$TMPDIR/h131_confirm_dry/`).
- **Targets:** held-out periods with a DQ6 settlement message and named rivals, scanned over #29, #34, #45–#50, #1, #14, #15, #28 and #43. Targets without such rows report "untestable". #34's vote-outs are room moves, not messages.
- **C0:** ≥ 10 in-flight rival replies (precondition).
- **C1 (kill test):** the in-flight rival flag rate exceeds the read rate (Fisher exact p < 0.05). "Kill" if the in-flight rate lies within the read rate's 90% CI.
- **C2:** read-gated DiD Δ > 0, permutation p < 0.05, where ≥ 20 open rival replies exist.
- **Held-out stance:** DQ10's prepared file `holdout_labels/reply_stance_v2_holdout.parquet` (never inspected).
- **Ledger:** family `stance`; overlaps H37 and H64 on #29 and #34 (disclose).

### Scorecard (round 1)
| Axis | Score | Evidence |
| --- | --- | --- |
| A mapping | 1 | Rivals and verdicts from DQ6; read-out from the DQ1 ledger; stance from the validated v2.1 flag (precision 0.61–0.67). Regime I only. |
| B assumptions | 1 | Read-gating rule audited (0 in-flight); speaker, target and phase effects; label noise built into the synthetic. |
| C adequacy | 2 | #12 DiD beats team permutation (p 0.0002) and two-way effects; soft outcome agrees. |
| D unfitted predictions | 1 | First-reply switch-off predicted and observed (0/21); the read alignment is untestable. |
| E interventional | 1 | Ten dated verdict instants; no partition to separate read from clock. |
| F identifiability | 2 | Synthetic on the real skeleton before data: P1 power 0.65, N2 0.43; read and clock non-identifiable, declared before outcomes. |
| G ground truth | 2 | DQ6 teams and verdicts. |
| H comparative | 1 | R-relation and remanence rejected (γ_set ≈ 0, first reply 0/21); R-clock not separable; R-protocol (topic change) open. |
| I transfer | 0 | #26 has no antagonism to test; holdout not run. |

**Claim that stands:** In the #12 debates, stance antagonism between drafted rivals (34/85 replies while open, 0/87 between teammates) is fully off by each rival's first reply after it reads the verdict (0/21; DiD +0.32 [+0.16, +0.52]). Exclusions: read-out vs wall-clock alignment (untestable, no in-flight replies); #26 (no antagonism); switch-on (non-discriminating).

## Round 2 redirects
- **H131-R1. Find an in-flight partition.** Settlements in regime II/III (long calls) or deliberately delayed reads are needed. Run the frozen confirm on held-out settlements, which tests C0 first.
- **H131-R2. Separate the field from the topic.** Label whether post-verdict rival replies still discuss the motion; compare disagreement on motion-related replies only.
- **H131-R3. Latent-scale bound.** Report the post-read latent rate bound with the labeller's confusion as a posterior, not a flag count.


## Notes
- 2026-10-04 22:19 UTC: card written from HH374 (Vivian approved in the dashboard). Round-1 protocol: card → G-folder predictions → synthetic on the real skeleton → amendments → replication + natives → estimates → confirm.py frozen (dry-run only) → summary.
- Stance input: DQ10 stance v2.1 (`reply_stance_v2.disagree_validated_agent`), validated 2026-10-04 (precision 0.61–0.67, recall ≈ 0.6). H21 and H37 are being re-tested with stance v2.1 by another agent; their cards are not edited here.
- The ledger read time comes from `infra/shared/visibility.py` (`receipts`, `producing_calls`), the same ledger that `pending_sets.py` uses.
- 2026-10-04 ~22:30 UTC: `scheme/build.py` built `replies.parquet` and `reads.parquet`; only structural counts were printed. ~22:35 UTC: one-replicate smoke tests of the synthetic exposed the sign convention and the 6-reply k = 1 cell (both fixed in A1, before outcomes).
- 2026-10-04 22:51–23:02 UTC: synthetic (100 replicates per world; a first 200-replicate launch was stopped for compute). ~23:03 UTC: Amendment A1, then the real run, 16 estimates rows, figure, `confirm.py` dry-run on #12/#26 (reproduces 262 replies, 57 read rival replies, 0 in flight) and freeze (`analysis/confirm.sha256`). **Not run.**
- Proposed DEFINITIONS.md variants (H131): **verdict read-out call** = the speaker's receiving call (DQ1 ledger) for the settlement message; **prize state, read-gated O_j(c)** = 1 while j's call c was assembled before j's verdict read-out call; **post-read call index k** = 1 + j's talk calls between its read-out call and the reply's producing call; **in-flight reply (verdict)** = a reply posted after the verdict instant but produced by a call assembled before its speaker read the verdict; **read-out relaxation kernel r(k)** = the rival conflict-flag rate at post-read call index k; **conflict flag (stance v2.1, agent)** = `reply_stance_v2.disagree_validated_agent` (stance2 = disagree, confidence ≥ 0.6, parent by an agent or human).
