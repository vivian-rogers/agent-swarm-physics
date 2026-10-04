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
