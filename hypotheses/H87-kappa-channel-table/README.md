# H87: κ table: commits per bit by channel

**Status:** **exploratory round 1 done (2026-10-04, non-holdout only). Mixed: the κ table has one valuable channel.** Pooled over 18,760 forced erasures (NE41), the context window is worth κ_C = 5.2 [3.8, 7.9] commits per 20 calls per bit (erasure costs 41% of the next 20 calls' commits for 0.08 bits). Every other channel's value is consistent with 0: own artifact κ_A = −0.6 [−1.6, +0.3] (0.14 bits, the most informative store), memory note, chat reads, history search and human messages (≤ 0.04 bits each, κ not identified), kickoff (0.36 bits, κ_K CI includes 0). The HH ordering fails at its first step (P(κ_C > κ_A) = 1.00). Memory size at erasure does nothing (+0.01). Receiving any chat after an erasure raises output 22% [8, 36] beyond its placebo effect, without allocation bits. `confirm.py` written, **not run**. (Approved by Vivian 2026-10-04 from HH307; card filled ~20:07 UTC before any new-row outcome.)
**Question (GOALS.md):** **Q4**, where does the swarm's information live, and what is it worth? H87 is the flagship quantitative Kolchinsky–Wolpert test: one table of κ_c = ΔV_c / I_c (commits per 20 calls per bit) for seven channels, measured with one shared estimator (`infra/shared/semantic_kappa.py`, built by H70).
**Fields:** information theory (Kolchinsky–Wolpert semantic information, plug-in mutual information with bias correction), physics of life (viability per bit, stigmergic stores), causal inference (natural scrambles, Poisson difference-in-differences)
**Literature:** [Kolchinsky & Wolpert 2018](../../literature/kolchinsky-2018-semantic-information-autonomous-agency.md) (value of information ΔV; thermodynamic multiplier κ = ΔV/I; η = S/I); [Sowinski et al. 2023](../../literature/sowinski-2023-semantic-information-resource-gathering-agents.md) (viability per bit, plateau then collapse; most bits can be semantically irrelevant).
**Definitions used** (`physics-models/DEFINITIONS.md`): Regime; Memory state; Semantic information (Kolchinsky–Wolpert); **Semantic information (natural-scramble variant)** (H15); Pseudo-erasure (H44); Unit macro-state (allocation), Re-acquisition path (H58). H70's proposed variants are used unchanged: **allocation pointer (channel c)**, **channel information I_c (allocation bits)**, **channel value ΔV_c (open-channel DiD)**, **κ_c (commits per bit)** (H70 card; not yet in DEFINITIONS.md). New here: **channel value ΔV_c (own-scramble variant)**, the value measured at the channel's own natural scramble.
**From:** HH307 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` · **Models:** `physics-models/04-semantic-information/`, `physics-models/12-information-dynamics/` (tool: plug-in information estimators)

## Source HH (verbatim from the HH list, including literature refinements)
The semantic-information channel table: κ in commits per bit, by channel. This is the flagship quantitative Kolchinsky test. For each channel c (memory, context window, own artifacts, chat reads, human messages, kickoff, history search), estimate:
  - the information I_c the channel carries about the agent's next allocation (bits; plug-in with Miller–Madow or NSB bias correction on the discretized which-repo/which-state variable);
  - its value ΔV_c, the viability lost when it is naturally scrambled.

  Viability is commits in the next 40 calls, or P(return to own artifact). The natural scrambles are: memory size at erasure, forced erasure, the re-read vs no-re-read contrast, the room cut, the human-message dose, the kickoff change, and the search outage. Report κ_c = ΔV_c / I_c and η_c = S_c / I_c.

  Prediction, ordered: κ_artifact > κ_context > κ_chat > κ_kickoff > κ_memory ≈ 0. From H15, κ_memory has a CI including 0. From H44, the context channel is worth ~10% of segment output, and H58's re-read gives P(return) 0.96 vs 0.85. *Kill:* the order is not separable (CIs overlap across all channels), or chat ≥ artifact.
  *Models:* 04 · *Builds on:* H15, H44, H58, H05, H54, HH294

## Question
How many commits does one bit of allocation information buy, channel by channel, and does the ordering artifact > context > chat > kickoff > memory hold?

## Design: two layers (Vivian, 2026-10-04)
- **Replication** (role `replication`): the call-scale table (rows C, A, M, G, H, Q) on every regime-III non-holdout period with ≥ 300 forced erasures: #36, #37, #38, #39, #40, #41, #42, #44, #51 (non-holdout head).
- **Natives** (role `native`):
  - **N1, NE41:** the pooled call-scale table over all non-holdout forced erasures (period-stratified fixed effects), with paired bootstrap ordering tests and the memory-size own scramble. Folder `goalperiod-subhypotheses/NE41/`.
  - **N2, G37 search outage:** the search row's own-scramble value, from H84's dose DiD in commits per 20 calls. Folder `goalperiod-subhypotheses/G37/`.
  - **N3, NE34 kickoff change:** the kickoff row at day scale (nights that start a new goal vs within-goal nights). Folder `goalperiod-subhypotheses/NE34/`.

## Model
**From:** `physics-models/04-semantic-information/` (Kolchinsky–Wolpert, natural-scramble variant); estimators from `physics-models/12-information-dynamics/` (plug-in MI, ≤ 7-symbol discipline relaxed to repo ids with a permutation floor).
- **System X:** one agent. Its state after an event is its **allocation** X⁺: the repo of its first agent work commit in the window (DQ4; −1 = none).
- **Events:** H70's frame (data reuse, `data/processed/H70-artifact-store-semantic-info/events.parquet`): F = forced erasure (NE41), P = pseudo-erasure at position 21 of a no-reset segment ≥ 40 calls (H44), N = first call of the agent's day, PN = mid-day placebo. H87 maps every event back to its ledger call and adds pointers.
- **Channels and pointers S_c** (repo ids; −1 = none), each "open" when S_c names the agent's own artifact A⁻ (repo of its last work commit before the event):
  - **C context window:** repo touched most in calls −10…−1 (H70). Scrambled at F, intact at P.
  - **A own artifact:** A⁻ itself; open = A⁻ touched in an executed command in calls 1–5 (the re-read path).
  - **M memory note:** repo named by the latest intention (consolidation note) before the event (H70).
  - **G chat reads (agent senders):** repo named most by `agent`-kind ledger items received in calls 1–5.
  - **H human messages:** repo named most by `human`-kind ledger items received in calls 1–5.
  - **Q history search:** repo named most by the answers of the agent's search calls in calls 1–5 (raw SEARCH_HISTORY rows; repo ids only).
  - **K kickoff (day scale):** the standing goal field. Scrambled at a night that starts a new goal period; intact at within-goal nights.
- **Information I_c (bits):** I(X⁺; S_c) at scramble events, Miller–Madow plug-in, minus the mean of 200 within-stratum (agent × period) permutations. For C and K, the information the scramble destroys: I_C = I_P(X⁺; S_C) − I_F(X⁺; S_C); I_K = I_within(X⁺; A⁻) − I_newgoal(X⁺; A⁻).
- **Value ΔV_c (commits per 20 calls):**
  - *open-channel DiD* (uniform column, rows A, M, G, H, Q): Poisson pseudo-ML, log E[V] = FE(stratum × arm) + b₁ open + b₂ open × scramble + b₃ log(1 + V_pre); ΔV_c = mean V of open scramble events × (1 − e^{−b₂}) (`semantic_kappa.did_value`).
  - *scramble cost* (rows C, K): ΔV = mean placebo V × (1 − e^{b}) with stratum FE (`semantic_kappa.scramble_cost`).
  - *own-scramble column:* M by memory size at erasure (top vs bottom tercile of memory chars, × scramble, Poisson DiD); Q by the outage (H84, commits per 20 calls at the mean searcher dose); A by the re-read contrast (= its open-channel DiD); H by human-message dose (any human item in calls 1–5, × scramble); G by any agent item naming any repo (× scramble). The room cut (NE12) is held out.
- **κ_c = ΔV_c / I_c**, with paired bootstrap draws (the same agent-day clusters for every row) so that P(κ_i > κ_j) is a proper paired probability.
- **η_c = S_c / I_c is not identified:** S needs the least-information viability-preserving intervention; natural scrambles give only the all-or-nothing point. Reported as "n.i." with that reason.
- **Viability:** V = work commits in calls 1–20 (H70's; primary, for comparability with H70) and V40 = commits in calls 1–40 truncated at the next reset (the HH's choice; sensitivity). Secondary: P(X⁺ = A⁻ | a commit) by open flag.

### Rivals
- **R0, uniform worthlessness:** every channel has ΔV ≈ 0 except the context window, whose erasure costs output whatever the other channels carry (the "attention, not information" reading of H15/H44).
- **R1, artifact first (HH ordering):** κ_A > κ_C > κ_G > κ_K > κ_M ≈ 0.
- **R2, reading precedes writing:** open-channel effects are equal at scramble and placebo (b₂ = 0 for all rows).
- **R3, field dominance:** the kickoff carries most allocation bits (I_K ≫ I_A) but buys no commits (κ_K ≈ 0).

## Data scheme (`scheme/`)
- **`scheme/build.py`:** reads H70's events (data, not code), reloads the ledger calls with H70's documented rule (cu/chat calls, Claude Code agent excluded, pt_date ≥ 2026-02-09, holdout masked, sorted by agent and `t_first`, `seq` per agent-day), and joins each event to its call on (agent, pt_date, seq), checking `t_call`. It adds S_G, S_H, S_Q and their open flags, `n_agent_items`, `n_human_items`, `n_search` in calls 1–5, memory chars at the event (`memory_stats` as-of, rows with `lines_removed > 0`), V40, and the new-goal flag for nights.
- **Search pointers** come from `data/processed/H84-search-outage-memory-scramble/search_events.parquet` (built by H84's scheme; codes and repo ids only).
- **Output:** `data/processed/H87-kappa-channel-table/events_plus.parquet`, `_provenance.json`; results in `results/`.
- **Regimes covered:** regime III (call scale); all dense-git periods #30 onward at day scale (K row).

## Observables
- **O1** per row: I_c (bits, CI), ΔV_c (commits per 20 calls, CI), ΔV_rel, κ_c (CI), open share at scramble and placebo; n events, n clusters.
- **O2** paired ordering probabilities P(κ_i > κ_j) for adjacent rows of the predicted order, and P(κ_G ≥ κ_A).
- **O3** own-scramble column (M size, Q outage, H dose, G any-item, K goal change).
- **O4** V40 sensitivity; P(return) by open flag (H58 anchor).
- **O5** per-period tables (replication); the per-period rank of each channel.

## Null / baseline
- **Within-stratum permutation of S_c** (agent × period): the information floor; agent identity and repo popularity carry no bits.
- **Placebo arm P / PN:** the DiD control (R2) and the I_C reference.
- **Synthetic at real counts** (axis F, `analysis/synthetic.py`, before real outcomes): on the real F/P skeleton of NE41 (agents, periods, open rates of every row), plant (i) a world with known κ per row (e.g. κ_A = 3, κ_C = 5, κ_G = 1, κ_M = 0) and (ii) R2 (reading raises V ×1.3 in both arms, no channel value). The paired bootstrap must recover the planted order with P(κ_i > κ_j) ≥ 0.9 where planted gaps are ≥ 2 commits per 20 calls per bit, and size ≤ 0.10 for ordering claims under (ii). Rows with open share < 1% are flagged "unpowered" from their synthetic CI widths.
- `semantic_kappa.py --verify` passes (H70).

## Impostors (STANDARDS §1)
| Impostor | How it could fake a channel value | How H87 removes it | Status |
| --- | --- | --- | --- |
| Scheduler field | Erasure timing and busy stretches carry both re-reads and commits | F timing is set by the 41-call cap; placebos from the same agent-days; stratum × arm FE; V_pre covariate; identical window truncation | removed |
| Exogenous field (goal, kickoff) | The goal names the repo, so pointers look informative | Within-agent × period permutation floor; K row treats the goal change itself as the scramble | partly |
| Shared model priors | Some families re-read, chat and commit more | Agent × period FE in every DiD; within-stratum permutation | partly |
| Contemporaneous convergence | Chat and human items name A⁻ because the agent is visibly working on it | Only items received at the agent's ledger receiving calls count; the open × scramble interaction subtracts the same naming at placebo calls; G and H are labelled provisional if their open share at P exceeds that at F | partly |

## Scorecard scheme, rivals and holdout
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R0 uniform worthlessness; R1 artifact first; R2 reading precedes writing; R3 field dominance.
**Locked holdout used for confirmation:** none yet. Planned in `analysis/confirm.py` (frozen, guarded, **not run**): the call-scale table on held-out regime-III periods (#43, #45–#50, #51 tail).

*(Round 1 scores in "Faithfulness scorecard" below.)*


## Prediction
*Written 2026-10-04 ~20:07 UTC, before any statistic of the new rows (G, H, Q, K estimator, M size, V40) was computed. Prior knowledge, stated: H70's provisional NE41 rows were read before writing this card: κ_C = 5.2 [3.8, 8.4] (erasure costs 41% of the next 20 calls' commits), κ_A = −0.6 [−1.7, +0.2] with I_A = 0.14 bits, I_M = 0.04 bits and I_R = 0.02 bits with no value; NE34: I_A within-goal 0.49 bits vs 0.12 at new-goal nights. The HH ordering (P1) was written before H70 and is kept unchanged, although H70 already indicates its first step fails.*

| # | Prediction | Counts against |
| --- | --- | --- |
| P1 | **HH ordering:** κ_A > κ_C > κ_G > κ_K > κ_M ≈ 0, each adjacent pair with paired P ≥ 0.9; κ_M's CI includes 0. | any adjacent pair reversed with P ≥ 0.9; *kill:* all CIs overlap, or κ_G ≥ κ_A |
| P2 | **Context row replicates H70** on the mapped frame: κ_C within ±20% of 5.2; erasure cost 35–47% of V. | outside |
| P3 | **Chat reads (agent senders):** I_G ≤ 0.05 bits; κ_G CI includes 0. | κ_G > 0 with CI excluding 0 |
| P4 | **Human messages:** open share < 1% of F events; I_H ≤ 0.05 bits; κ_H CI includes 0 (an unpowered row). | κ_H CI excludes 0 |
| P5 | **History search:** I_Q > 0 only in #51; κ_Q (own scramble, outage) CI includes 0. | κ_Q CI excludes 0 |
| P6 | **Kickoff (R3):** I_K ≥ 0.2 bits (the goal change destroys most artifact-pointer bits), κ_K CI includes 0. | I_K < 0.1 bits |
| P7 | **Memory size at erasure:** top vs bottom memory tercile × scramble ΔV_rel within ±0.10 (H15/H44: memory dose does nothing). | ΔV_rel beyond ±0.10 with CI excluding 0 |
| P8 | **V40 sensitivity:** the sign of every row's ΔV is unchanged. | a sign flip with CI excluding 0 |
| R | **Replication:** κ_C > 0 (CI excluding 0) in ≥ 2/3 of eligible periods; κ_C is the largest finite κ in ≥ 2/3 of them. | < 1/2 |
| N1 | see `goalperiod-subhypotheses/NE41/README.md` | |
| N2 | see `goalperiod-subhypotheses/G37/README.md` | |
| N3 | see `goalperiod-subhypotheses/NE34/README.md` | |

**Analyst's expectation (stated):** the table will show one valuable channel (context) and a set of channels whose information is real but buys no measurable commits. If so, the HH ordering fails at its first step, and the result is "the context window is the only channel worth commits per bit".

**Verdict rule (overall):** *supported* if P1 holds; *failed* if the kill condition holds (κ_G ≥ κ_A, or all CIs overlap); *mixed* otherwise.

## Synthetic validation (axis F; run 2026-10-04 20:22–20:46 UTC, two passes with the same seeds, before any new-row outcome statistic)
`analysis/synthetic.py` → `data/processed/H87-kappa-channel-table/synthetic/synthetic.json` (`synthetic_pass1.json`: the first pass, identical numbers, without saved per-replicate records). Real NE41 skeleton: 18,760 F and 19,886 P events with an own artifact, real strata, clusters, open flags and V_pre; X and V replaced. 25 replicates per world, paired bootstrap B = 50. `infra/shared/semantic_kappa.py --verify` passes (H70).

| World | Row | planted ΔV_rel | recovered (mean) | 95% CI coverage | mean I (bits) | identified (I CI lower > 0.02) |
| --- | --- | --- | --- | --- | --- | --- |
| W1 | A | 0.50 | 0.52 | 0.88 | 0.29 | 1.00 |
| W1 | M | 0 | 0.05 | 0.76 | 0.026 | 0.04 |
| W1 | G | 0.20 | 0.25 | 0.84 | 0.015 | 0.00 |
| W1 | Q | 0 | −0.05 | 0.84 | 0.000 | 0.00 |
| W0 (R2) | A / M / G / Q | 0 | 0.00 / 0.00 / −0.00 / 0.04 | 1.00 / 0.88 / 0.88 / 0.92 | as W1 | as W1 |
| W0 | C cost | 0.39 | 0.39 | — | 0.06 | 0.92 |

- **The open-channel ΔV estimator works:** bias ≤ 0.05, coverage 0.76–1.0 at B = 50, and no false value under R2.
- **The κ ratio does not order rows whose information is near the floor.** With raw paired probabilities, some ordering claim with P ≥ 0.9 appeared in 24% of W0 replicates (no channel has value) and the false claim κ_G > κ_A in 32% of W1 replicates: when I_c is about 0.02 bits, κ_c = ΔV_c / I_c explodes.
- **Restricted to identified rows** (I CI lower bound > 0.02 bits), there are no wrong-direction claims (0/25 in both worlds), and the true κ_C > κ_A is claimed in 23/25 replicates (0.92). At real counts only A and C are identified (M in ≤ 8% of replicates, G and Q never).
- In W1 the context cost falls to 0.28 (from 0.39) because open channels compensate after an erasure. This is a property of the world, not a bias.

## Amendments (2026-10-04 20:47 UTC, after the synthetic, before any new-row outcome statistic)
- **A1 (ordering rule):** κ ordering claims (paired P ≥ 0.9) are made only between **identified** rows, where the I CI lower bound > 0.02 bits. A row that is not identified gets κ "n.i.". It is placed by its ΔV: "κ ≈ 0 (consistent)" if its ΔV CI includes 0, and "unresolved" otherwise. P1 is evaluated on this rule. The kill clause "all CIs overlap" is read on ΔV_rel for non-identified rows.
- **A2 (H row):** no human ledger item in a non-holdout call window names a repo, so I_H is 0 by construction (repo pointer). The H row reports only its own-scramble ΔV (any human item in calls 1–5 × erasure); κ_H is n.i. P4's "open share < 1%" is met trivially (0%).
- **A3 (G row = H70's R row):** because human items never name repos, the agent-chat pointer S_G equals H70's room pointer S_R on every event. The G row is therefore a replication of H70's R row on the same frame, not a new measurement.

## Results by goal period
| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [NE41](goalperiod-subhypotheses/NE41/README.md) | native (N1, pooled table) | mixed | κ_C 5.2 [3.8, 7.9]; κ_A −0.6 [−1.6, +0.3]; M, G, Q, H κ ≈ 0; P(κ_C > κ_A) 1.00 |
| [G37](goalperiod-subhypotheses/G37/README.md) | native (N2, search outage) + replication point | mixed (inconclusive) | ΔV_Q −0.03 ± 1.0; I_Q 0.012 [−0.011, 0.035]; κ_Q n.i. |
| [NE34](goalperiod-subhypotheses/NE34/README.md) | native (N3, kickoff) | mixed | I_K 0.36 [−0.05, 0.79] bits; ΔV_K −0.29 [−1.46, 0.32]; κ_K CI includes 0 |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | failed | cost 0.30 [−0.00, 0.50]; I_C n.i. |
| G37 (replication point, in the N2 folder) | replication | failed | cost 0.12 [−0.20, 0.44]; I_C n.i. |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | supported | κ_C 0.87 [0.39, 1.98]; κ_A 0.81 [−1.44, 2.32] |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | mixed | cost 0.40 [0.29, 0.50]; I_C n.i. |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | mixed | cost 0.34 [0.25, 0.41]; I_C n.i. |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | mixed | cost 0.44 [0.35, 0.53]; I_C n.i. |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | mixed | cost 0.45 [0.30, 0.55]; I_C −0.01 |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | mixed | cost 0.44 [0.27, 0.52]; I_C −0.09 |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication | supported | κ_C 7.0 [4.9, 13.5]; κ_A −0.8 [−2.0, +0.4] |

## Outcome vs prediction
| # | Prediction | Observed | Verdict |
| --- | --- | --- | --- |
| P1 | κ_A > κ_C > κ_G > κ_K > κ_M ≈ 0 | identified rows: κ_C 5.2 ≫ κ_A −0.6 (P = 1.00); G, K, M, Q, H not identified, all ΔV CIs include 0 | **fail** (first step reversed); kill clause not met (κ_G n.i.; C separates) |
| P2 | κ_C within ±20% of 5.2; cost 35–47% | 5.24 [3.79, 7.88]; 41% [38, 44] | pass (replicates H70 on the mapped frame) |
| P3 | I_G ≤ 0.05 bits; κ_G CI includes 0 | 0.020 bits; ΔV_rel +0.04 [−0.17, +0.25]; κ n.i. | pass |
| P4 | human open share < 1%; I_H ≤ 0.05; κ_H CI includes 0 | 0% (no repo-naming human item); dose ΔV_rel +0.09 [−0.20, +0.40] | pass (trivially) |
| P5 | I_Q > 0 only in #51; κ_Q CI includes 0 | I_Q > 0 in G36 and G51 (H84); κ_Q n.i. | partial |
| P6 | I_K ≥ 0.2 bits; κ_K CI includes 0 | 0.36 [−0.05, 0.79]; κ_K −0.8 [−16.5, 0.7] | partial (point yes, CI includes 0) |
| P7 | memory size × erasure within ±0.10 | +0.01 [−0.06, +0.09] | pass |
| P8 | no V40 sign flip | none; A at V40 −0.19 [−0.25, −0.14] (V20 −0.05) | pass |
| R | κ_C > 0 (CI excl. 0) and largest in ≥ 2/3 periods | A1 rule: 2/9 (G38, G51); point rule (pre-clarification): 6/9; erasure cost > 0 (CI excl. 0) in 7/9 | fail (A1); pass (point rule) |

## Results
**The κ table (NE41, call scale, commits per 20 calls per bit; ΔV with 95% CIs).**

| Channel | Natural scramble | I_c (bits) | ΔV_c | κ_c | η_c |
| --- | --- | --- | --- | --- | --- |
| Context window (C) | forced erasure (NE41) | 0.078 [0.052, 0.104] | 0.41 [0.36, 0.45] | **5.2 [3.8, 7.9]** | n.i. |
| Own artifact (A) | re-read vs no re-read × erasure | 0.137 [0.115, 0.159] | −0.08 [−0.21, +0.04] | −0.6 [−1.6, +0.3] | n.i. |
| Memory note (M) | note names A⁻ × erasure; memory size tercile | 0.038 [0.017, 0.059] | +0.04 [−0.06, +0.14]; size: +0.01 rel | n.i. (≈ 0) | n.i. |
| Chat reads (G) | item names A⁻ × erasure; any item | 0.020 [0.007, 0.034] | +0.02 [−0.11, +0.12]; any item: +0.13 [+0.05, +0.19] | n.i. (≈ 0) | n.i. |
| Human messages (H) | any human item × erasure | 0 (no repo naming) | +0.06 [−0.15, +0.24] | n.i. | n.i. |
| History search (Q) | answer names A⁻ × erasure; outage (H84) | 0.001 [−0.002, 0.003]; 0.012 pooled (H84) | −0.08 [−0.36, +0.30]; outage −0.03 ± 1.0 | n.i. | n.i. |
| Kickoff (K, day scale) | new-goal night (NE34) | 0.36 [−0.05, 0.79] | −0.29 [−1.46, +0.32] | −0.8 [−16.5, +0.7] | n.i. |

- **One channel is worth commits per bit.** Erasing the context window costs 0.41 commits per 20 calls (41% of output) and removes 0.08 bits of allocation information: 5.2 commits per 20 calls per bit. In the two periods where I_C is identified alone, κ_C is 0.87 (#38) and 7.0 (#51).
- **The most informative store is not the most valuable.** The own artifact carries 0.14 bits, twice the context's, and its re-read raises the return rate to 0.96 from 0.80. But the same premium appears at placebo calls (0.96 vs 0.76), and the open × erasure DiD is −5% [−13%, +3%] at 20 calls and −19% [−25%, −14%] at 40 calls. Reading precedes writing (R2); after an erasure, the re-read costs calls.
- **Memory, chat, search and human messages carry ≤ 0.04 bits each and no measurable value.** Memory size at erasure changes nothing (+1% [−6%, +9%]), as in H15/H44.
- **Chat has value without allocation bits.** Receiving any agent chat item in the five calls after an erasure raises output 22% [8%, 36%] beyond its effect at placebo calls. The items name the agent's repo in only 4.5% of erasures, so the value is not repo information. Candidate readings: chat restarts activity (a kick), or chat carries task information below the repo level. Post hoc in interpretation; the contrast itself was pre-registered (own-scramble G column).
- **The kickoff field carries bits, not commits.** A goal change removes 0.36 bits (CI includes 0 at day resampling) and does not lower output.
- **η is not identified anywhere:** natural scrambles give only the all-or-nothing point, not the information/viability curve.
- **Phase-diagram reading:** the erasure cost is 0.30–0.45 of output in 7/9 periods (stable), while I_C varies around 0 (identified in #38 and #51 only). The cost is a constant; the bits it removes are small and noisy. "Context is worth commits" is robust; "context is worth commits *per allocation bit*" holds where it is measurable.

## Faithfulness scorecard
*Round 1, 2026-10-04.*
| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Allocation, pointers, viability and scrambles come from the ledger, DQ4, `artifact_mentions`, `memory_stats` and raw search rows (ids only); KW departures listed (cuts, not shuffles; agent-chosen open flags). Regime III only at call scale; repo-level coarse-graining misses sub-repo information (the chat row). |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | DiD assumes parallel trends between open and closed events across arms; the placebo arm removes "reading precedes writing". Within-agent × period permutation floor. Day-scale K row resampled by day. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | C beats its placebo (cost CI excludes 0, 7/9 periods); A, M, G, Q, H, K do not beat theirs. No held-out-day prediction. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | P2 (κ_C ±20% of H70's value) and the memory-size null (P7) are out-of-design checks that held; V40 sign stable. |
| E interventional | predicts the change across a natural experiment | 1 | Three natural scrambles (forced erasure, outage, goal change); the predicted ordering fails, the predicted nulls hold. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 | Synthetic at real counts: ΔV bias ≤ 0.05, coverage 0.76–1.0; ratio ordering sized and restricted (A1: 0 wrong-direction claims, power 0.92 for C > A); V20/V40 variants. |
| G ground truth | agrees with known structure | 1 | Reproduces H70's NE41 rows exactly on an independent mapping; the re-read return rate matches H58 (0.96). |
| H comparative | beats the named rivals | 1 | R1 (artifact first) rejected; R2 fits A; R0 fits every row but C; R3 consistent for K. |
| I transfer | holds in other same-mode periods, including the holdout | 1 | Erasure cost positive in 7/9 periods; κ_C identified in 2/9 (both supported). Holdout not run. |

## Confirmatory predictions (written 2026-10-04 ~20:54 UTC after round 1, before any holdout use; `analysis/confirm.py`, **not run**)
Targets: held-out regime-III periods #43, #45–#50 and the #51 tail (call scale, forced erasures).
- **C1** pooled erasure cost ΔV_rel(C) in [0.30, 0.50], CI excluding 0.
- **C2** κ_C > κ_A with paired P ≥ 0.9, if both rows are identified; otherwise κ_C identified and > 0.
- **C3** the open-channel ΔV_rel of A, M and G each has a CI that includes 0, or is negative (no positive artifact, memory or chat-pointer value).
- **C4** memory size × erasure ΔV_rel within ±0.10.
- **C5** any agent chat item × erasure ΔV_rel > 0 (CI excluding 0) — the round-1 surprise, now a prediction.
- Overall: CONFIRMED if C1, C2 and C3 pass.

## Caveats
- κ is a ratio of two noisy numbers. It is defined only where I_c is identified (C and A pooled; C in 2/9 periods alone).
- Allocation is coarse-grained to the repo of the next commit. Channels that carry sub-repo or non-allocation information (chat, human messages) are scored near 0 bits by construction.
- Open flags are chosen by the agent; the DiD assumes the open/closed contrast would be the same without an erasure.
- The search and human rows are unpowered at call scale (46 open F events; 0 repo-naming human items).
- The G row equals H70's R row (A3), so it is a replication, not new evidence.
- The K row's bits are not identified at day resampling (98 new-goal nights, 8 boundaries).
- The per-period verdict rule was clarified after the run (A1 applied to C); both counts are reported.

## Round 2 redirects (2026-10-04)
*Proposed by the round-1 agent; the coordinator may revise.*
- **Where round 1 went sideways:** the repo-level allocation variable cannot see what chat and human messages carry; the κ ratio is undefined for every low-information channel.
- **H87-R1.** Finer X: the next behavior state (DQ3, 11 states) or the next file within the repo, so chat and human rows can carry measurable bits.
- **H87-R2.** The chat-after-erasure value (+22%): split by item kind (mention of the agent, question, status), with H57's in-flight placebo, and test whether it is a kick (activity) or information (content).
- **H87-R3.** Graded scrambles for η: use erasure position within long segments and memory-size quantiles as a dose to trace an information/viability curve.
- **H87-R4.** Move H70's event builder and H87's pointer builder into `infra/shared/` (STANDARDS §8), so `confirm.py` runs without reading another hypothesis's data folder.

## Notes
- 2026-10-04 ~20:07 UTC: card written before any new-row statistic. Holdout masked with `holdout_mask` and the ledger's `holdout` flag in every script; held-out counts never printed.
- 2026-10-04 ~20:05 UTC: coordinator message (before predictions were fixed): use `infra/shared/semantic_kappa.py` (passes `--verify`), the Poisson DiD and the original-stratum bootstrap; `memory_stats` writes two rows per regime-III consolidation, so filter to `lines_removed > 0` before using memory size. All three are followed.
- 2026-10-04 20:52 UTC, **clarification after the run (disclosed):** the templated per-period rule accepted κ_C whenever its point estimate was finite. Amendment A1 (written before the run) makes κ "n.i." for any row whose I CI lower bound is ≤ 0.02 bits; applying A1 to the context row too gives 2 supported, 5 mixed, 2 failed periods, against 6 supported, 3 failed under the point rule. Both are reported; the A1 count is the headline.
- 2026-10-04: the H row has no information estimate (A2) and the G row reproduces H70's R row (A3). Both were found from pointer counts before any new-row outcome.

## Round 2 (2026-10-05): behavior-state allocation, the chat-after-erasure value, graded scrambles
*Scope: H87-R1, R2 and R3 (round-2 redirects). H87-R4 (move the event and pointer builders into `infra/shared/`) is done in part by the round-3 consolidation (`channel_pointers.py`); the rest is listed for the shared queue, not done here. Non-reserved data only (`load_calls` drops reserved calls; `holdout_mask` on behavior windows; an assert on every event day). Round-1 scripts and outputs are unchanged. Round 2 lives in new scripts (`scheme/build_r2.py`, `analysis/r2lib.py`, `analysis/r2_synthetic.py`, `analysis/r2_run.py`, `analysis/r2_rows.py`) and writes to `data/processed/H87-kappa-channel-table/r2/`. Shared code only (`infra/shared/channel_pointers.py`, `semantic_kappa.py`, `estimates.py`); nothing from another hypothesis folder. H70 round 2 runs in parallel (search and kickoff rows, role split); this round does not touch those rows.*

### Round 2 design, predictions and kill rules
*Written 2026-10-05 05:03 UTC, before any round-2 statistic on real data.* Facts seen beforehand (structure and coverage counts only, from `scheme/build_r2.py --counts` and a coverage print; no outcome V or allocation X was summarized):
- Frame: 1,374,780 non-reserved ledger calls. F 18,760 and P 19,886 events with n_win ≥ 10 and A⁻ known (round 1's sample; the rebuilt V, X⁺, A⁻ and V_pre equal the shared `channel_pointers` events on 100% of rows). Graded-scramble events in forced-opened segments: F2 18,612, F5 18,355, F10 17,887, F20 16,438.
- DQ3 v3.1 labels (existing only; no new labelling): 145,683 labelled non-reserved 5-min windows. The next-state X_beh is defined for 95.5% of F and 95.3% of P events; the pre-event state S_Cb for 96% / 95%. The argmax of the 11 probabilities equals the stored label in 99.7% of regime-III windows (ties 0.3%, broken by a fixed state order).
- Agent chat in calls 1–5: any item F 0.90 / P 0.70; a backlog item at call 1 (posted during the consolidation) F 0.87 / P 0.27; a fresh item at calls 2–5 F 0.59 / P 0.64. Kinds (any item of the kind): mention of the recipient F 0.23 / P 0.11; question (not a mention) 0.44 / 0.22; status (neither) 0.87 / 0.63; an item from a sender whose last work commit is in the recipient's A⁻ 0.19 / 0.10. Median items received in calls −20…−1: F 6, P 10. Median before-message age 51 s in both arms.
- Human items in calls 1–5: 239 F, 110 P events (mentions 14 / 10). Search in calls 1–5: 385 F, 264 P events.
- In-flight span S (first 60 s after call 1 starts; the median time from call 1 to call 5 is 51–59 s): an agent item posted in S and read by call 5 in 9,359 F / 10,567 P events; posted in S but in flight at call 5 in 2,576 F / 2,081 P events.
- Memory size at F is known for 99.96% of F events.

**Shared rules.** Sample, strata (agent × period), clusters (agent-day), V (work commits in calls 1–20, rate × 20 if truncated, n_win ≥ 10), V_pre, the Poisson DiD (`semantic_kappa.did_value` / `poisson_fe`, stratum × arm fixed effects, log(1 + V_pre)) and the A1 identification rule (I CI lower bound > 0.02 bits) are round 1's. Modal pointers break ties to the smallest id (deterministic). Pooled values are NE41 fits with period-stratified fixed effects and a paired agent-day cluster bootstrap (B = 300; CLAUDE.md exception (c)); per-period values (≥ 300 F events) are the replication layer, with a DerSimonian–Laird pool as a companion.

**R1, a finer allocation variable.** X_beh = the DQ3 behavior state of the agent's first labelled window that starts after call 5 ends (≤ 15 min; −1 = none, kept as a symbol). It sits after the receiving calls 1–5, so chat, human and search items can carry bits about it. Rows and pointers (one pointer per row; each row's I is computed under both X_repo, round 1's, and X_beh):
- **C:** S_Cb = the behavior state of the last labelled window that ends before call −1 ends. I_C = I_P(X; S_Cb) − I_F(X; S_Cb). ΔV_C = the erasure cost (round 1).
- **A:** A⁻ (repo id), open = openA. **M:** S_M (note repo), open = openM.
- **G:** kind code of agent items received in calls 1–5: 0 none, 1 status only, 2 a question (no mention), 3 a mention. ΔV_G = any agent item × F (round 1's own-scramble value, +22%).
- **H:** 0 none, 1 human item, 2 human item that mentions the agent; ΔV_H = any human item × F.
- **Q:** 0 none, 1 search with no repo in the answers, 2 answers name A⁻, 3 answers name another repo; ΔV_Q = any search × F.
- κ^beh_c = ΔV_c / I^beh_c on paired draws (commits per 20 calls per bit of next-state information). Ordering only between identified rows (A1).
- **P-R1a (prior 0.75):** I^beh_C is identified. *(prior 0.6)* it exceeds round 1's I^repo_C = 0.078 bits.
- **P-R1b (prior 0.65):** I^beh_G is identified, while the same kind code carries ≤ 0.02 bits about X_repo (prior 0.8): chat tells the agent what to do next, not where to commit.
- **P-R1c (prior 0.7):** H and Q stay not identified under X_beh (239 and 385 open F events).
- **P-R1d (prior 0.6):** A and M carry ≤ 0.05 bits about X_beh; their ΔV is round 1's (CI includes 0), so κ ≈ 0.
- **P-R1e (prior 0.5):** if C and G are both identified, κ^beh_C > κ^beh_G with paired P ≥ 0.9.
- **Kill for "a finer X makes chat measurable":** I^beh_G is not identified while the synthetic power to identify 0.05 bits at the real G counts is ≥ 0.8.
- Per period: I^beh_C, I^beh_G and κ^beh for C and G (replication rows).

**R2, the chat-after-erasure value (is the +22% a kick or information?).** Outcome V; Poisson with stratum × arm fixed effects and log(1 + V_pre); pooled agent-day bootstrap B = 300; per-period agent-day bootstrap B = 200 and a DL pool.
- *R2-0 replication:* any agent item × F (round 1: RR 1.22 [1.08, 1.36]).
- *R2-1 timing:* backlog (an item at call 1) × F and fresh (an item at calls 2–5) × F, fitted jointly. At F the backlog is the consolidation's arrivals (87% vs 27% at P): its "absent" events are the 13% of erasures that land in a quiet room.
- *R2-2 composition:* R2-0 and R2-1 with arm × room-rate fixed effects (items received in calls −20…−1: 0, 1–3, 4–10, 11–30, > 30) and arm × before-age fixed effects (< 30 s, 30–120 s, 120–600 s, > 600 s or none). This compares arrivals after an erasure with arrivals at pseudo-erasures in equally busy rooms.
- *R2-3 kinds:* in the R2-2 model, add mention × F, question × F and same-repo sender × F on top of any item × F (and their main effects), plus dose (1, 2–3, 4–9, ≥ 10 items) × F. Generic presence is the any-item term; content is the add-on terms.
- *R2-4 in-flight placebo at matched lag and before-age:* events with ≥ 1 agent item posted in S (the 60 s after call 1 starts). Arms: read (an item of S received by call 5) vs in flight (S items exist, none received by call 5). Fixed effects stratum × arm and arm × lag bin (0–20, 20–40, 40–60 s, lag of the first S item) × before-age bin (< 30, 30–120, ≥ 120 s or none); covariate arm × log(seconds from call 1 to call 5), because read status at a fixed lag depends on the agent's call speed. RR_read = exp(b_{read × F}). Both arms have the same room activity at the same lag; only reading by call 5 differs. In-flight items are read at calls 6+, so a reading effect that also acts from call 6 biases RR_read toward 1 (a conservative test of early reading).
- **Decision rule (kick vs information):** *activity, not reading* if the R2-4 RR_read CI includes 1 and the R2-2 fresh × F CI includes 1; *kick* if a reading effect survives (R2-4 RR_read CI > 1, or the R2-2 any-item or fresh term CI > 1) and every content add-on (mention, question, same-repo sender) has a CI that includes 1; *content-dependent (information)* if any content add-on CI excludes 1 (sign reported; a negative mention term is a reply burden); otherwise *unresolved*.
- **P-R2a (prior 0.9):** R2-0 reproduces RR 1.22 ± 0.05 (same data, shared frame).
- **P-R2b (prior 0.6):** the value sits in the backlog term (CI > 1); the fresh term's CI includes 1.
- **P-R2c (prior 0.55):** with the composition fixed effects, the any-item RR falls to ≤ 1.10 (point).
- **P-R2d (prior 0.55):** R2-4 RR_read CI includes 1 (no early-reading effect at matched lag).
- **P-R2e (prior 0.6):** every content add-on CI includes 1; the mention point is < 1 (H42: named reads raise talk, which costs calls).
- Overall priors: activity/composition 0.45, kick 0.35, information 0.20.
- **Kill for "information":** every content add-on CI includes 1 while the synthetic power at an add-on RR of 1.20 is ≥ 0.8.

**R3, graded scrambles (an information–viability curve for the context channel).**
- *R3a, context-size dose.* The cap sets every forced erasure at call 41, so the position of an event inside a forced-opened segment is an exogenous dose of retained context: at Fk the agent holds only its last k calls (k = 0 is F; k = 2, 5, 10, 20). For each k: I_k = I(X⁺; S_C) at Fk events (repo X primary; X_beh with S_Cb secondary), with the within-stratum permutation floor; c_k = 1 − exp(b_k) from one Poisson fit over all Fk events (stratum fixed effects, k dummies, log(1 + V_pre)), the share of k = 20 output lost. Recovery fractions: information f_k = (I_k − I_0)/(I_20 − I_0), viability v_k = 1 − c_k / c_0. A constant KW multiplier along the curve means f_k = v_k. η_C = f at the smallest k with v_k ≥ 0.9 (the share of the context's allocation bits that buys 90% of its value). Paired bootstrap B = 300 over agent-day clusters.
- *R3b, memory-size dose.* Memory-size quintiles (within agent × period, F and P events): the erasure cost c_q and I_C,q per quintile; slope of c_q over quintile index.
- *Not done:* erasure position within a long task run (the run of calls on one repo across segments). It needs a task-run definition that this round has not validated; it is listed as a round-3 redirect.
- **P-R3a (prior 0.7):** I_k rises with k (I_0 < I_5 < I_20, CIs separate) and c_k falls (c_0 > c_5 > c_10; c_10 CI includes 0 or ≤ 0.1, H44: tail ≈ 8 calls).
- **P-R3b (prior 0.55):** bits return before commits: f_k > v_k at k = 2 and k = 5 (paired P ≥ 0.9). The opposite (v > f) means output returns before allocation information; f ≈ v is the constant-κ (linear KW) reading.
- **P-R3c (prior 0.75):** memory does not grade the scramble: the slope of c_q over quintiles has a CI inside ±0.03 per quintile, and I_C,q shows no trend.
- **Kill for "a graded curve exists":** I_k shows no rise with k (I_20 − I_0 CI includes 0) — then the context channel has no measurable dose and η stays n.i.

**Synthetic validation first (axis F).** On the real skeletons (agents, strata, clusters, arms, kinds, lags, call speeds, room rates, V_pre, open flags), with X and V replaced:
- *R1:* a null world (X_beh drawn from agent-specific state shares, independent of every pointer) for the identified false-positive rate per row; planted worlds (X copies a function of the pointer with probability p, set for ≈ 0.05 and ≈ 0.10 bits) for identification power per row. A row's identification is read only where the false-positive rate is ≤ 0.10.
- *R2:* null worlds where V depends on room activity (room rate, before-age), on arm-specific call speed, and on the backlog's quiet-room composition, with no reading or content effect; planted worlds with a reading effect (RR 1.20 for items read by call 5 after F) and a content effect (mention add-on RR 1.20 and 0.80). Each statistic is read only where its size is ≤ 0.10; every null result gets its MDE₈₀.
- *R3:* a planted curve (c_k = 0.40, 0.30, 0.15, 0.05, 0 and I_k rising) for bias and coverage of c_k, f_k, v_k; a null memory world for the slope's size.

**Impostors.** *Scheduler:* the cap times F and Fk; P sits in the same kind of segments; stratum × arm fixed effects; R2-4 holds the lag fixed. *Exogenous field:* estimation within agent × period; R2-2 compares arrivals in equally busy rooms (room rate, before-age) after F and P. *Shared priors:* agent × period fixed effects; permutation within agent × period. *Convergence:* R2-4 is the read vs in-flight contrast at matched lag and before-age (STANDARDS §1; H54 r2 Amendment R2-1).

**Estimates.** Rows `r2_*` via `write_estimates`, role `replication` per regime-III period (R1 I^beh and κ^beh for C and G; R2 composition-adjusted any-item and fresh RR; R3 c_0 and I_20 − I_0). Pooled NE41 numbers stay in `r2/results.json` and the card.
