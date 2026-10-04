# H70: The semantic information of the artifact store

**Status:** **round 1 done (2026-10-04; exploratory, non-holdout; 13 periods, 2 natives).** **The artifact store holds *where* an agent works, not *how much* it gets done; the context window holds the value.** Across a forced erasure the agent returns to its own repo for 89% of first commits (placebo 87%), and the artifact pointer carries 0.14 [0.12, 0.16] bits per erasure beyond agent identity (7/9 regime-III periods). Re-reading the artifact after the erasure adds no output beyond its placebo association: ΔV_rel −0.05 [−0.13, +0.01], so κ_A ≈ 0 (rival R2, "reading precedes writing", wins). The erasure itself costs 41% [38, 44] of the next 20 calls' commits while destroying 0.08 bits: κ_C ≈ 5 commits per 20 calls per bit, the largest row. Memory note (0.04 bits) and room (0.02 bits) carry no measurable value. NE34: a new goal resets allocation (return 10% vs 80% within; #39 → #40 continuation 78%). HH261's "artifact loss costs more than memory loss" is not supported: neither has measurable value at erasures. Shared estimator `infra/shared/semantic_kappa.py` (`--verify` passes). `confirm.py` written, **not run**.
**Question (GOALS.md):** **Q4**, where does the swarm's information live, and what is it worth? H70 delivers the **artifact row of the HH307 κ table** (commits per bit by channel) with a shared estimator (`infra/shared/semantic_kappa.py`), so that other channels (history search, kickoff, human messages) can be added later with the same code. It also computes provisional context, memory-note and room rows with the same estimator.
**Fields:** information theory (Kolchinsky–Wolpert semantic information, plug-in mutual information), physics of life (stigmergic stores, viability), causal inference (difference-in-differences on natural scrambles)
**Literature:** [Kolchinsky & Wolpert 2018](../../literature/kolchinsky-2018-semantic-information-autonomous-agency.md) (value of information ΔV, thermodynamic multiplier κ = ΔV/I, stored vs observed information); [Sowinski et al. 2023](../../literature/sowinski-2023-semantic-information-resource-gathering-agents.md) (viability vs scrambled information; plateau then collapse); [Krakauer et al. 2020](../../literature/krakauer-2020-information-theory-of-individuality.md) (the agent + its environment as the individual).
**Definitions used** (`physics-models/DEFINITIONS.md`): Regime; Memory state; Semantic information (Kolchinsky–Wolpert); **Semantic information (natural-scramble variant)** (H15); Pseudo-erasure (H44); Re-acquisition path and Unit macro-state (allocation) (H58); Exposure (ledger receiving call) (RE-V1). New named variants defined below and proposed for DEFINITIONS.md: **allocation pointer (channel c)**, **channel information I_c (allocation bits)**, **channel value ΔV_c (open-channel DiD)**, **κ_c (commits per bit)**.
**From:** HH261 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` ("Making the faithful ones better") · **Models:** `physics-models/04-semantic-information/`
**Data inputs (shared tables first):** DQ1 context ledger (`context_ledger_turns`, `context_ledger_items`), DQ4 work ledger (`work_commits`, agent work only), `artifact_mentions` + `artifacts` + `work_repos` (repo identity of every mention), `events_core` (CONSOLIDATE), `period_units`, `calendar`, `roster`. Not used: `activity_bins`, `outages` (event-drop bug), `actions.error` (stderr).

## Question
Does losing artifact context cost more viability (work output) than losing memory or context, so that the artifact store is the main carrier of day-scale semantic information?

**What H15 already settled (round 1b, P11).** Agent-chosen repo switches cost nothing measurable (−0.00 SD, 54 estimable mid-period switches) and are confounded with task ends. There is no non-holdout involuntary scramble of the artifact store (NE24, GitHub → GitLab, is held out). H70 therefore does not re-run P11. It asks the KW question channel by channel at the two exogenous context erasures the village has: the **forced erasure** (NE41, call scale, timing set by the 41-call cap) and the **night** (day scale). At both, the context is wiped while the artifact, the memory note and the room stay. Each channel's information about the next allocation (bits) and its value (commits) are measured with one estimator; κ = ΔV/I is the commits-per-bit row of HH307.

## Design: two layers (Vivian, 2026-10-04; see `infra/data-quality/QUEUE.md`)
- **Replication:** the common estimator on every eligible goal period. Day scale (nights) on every non-holdout period with dense git (#30, #31, #33, #35–#42, #44, #51 head); call scale (forced erasures) on every regime-III non-holdout period (#36–#42, #44, #51 head). Period README role: `replication`.
- **Period-native tests:** NE41 (the pooled call-scale κ table over 21k forced erasures: artifact vs memory note vs room vs context) and NE34 (goal boundaries as relevance scrambles of the artifact store, with the #39 → #40 continuation boundary as the within-goal control). Period README role: `native`.
- **Faithfulness lever:** HH261 was written to raise **E** (scrambles as interventions) and **I** (NE24 on the holdout). H70 raises E with NE41's exogenous timing and NE34, and writes the NE24 test into `analysis/confirm.py` (frozen, not run).

## Model
**From:** `physics-models/04-semantic-information/` (Kolchinsky–Wolpert, natural-scramble variant).

- **System X:** one agent. Its state at a call is its **allocation**: the repo its next agent work commit goes to (DQ4; "none" if no commit in the window).
- **Stores and channels** that can carry allocation information across a context erasure:
  - **A, artifact store:** the agent's own artifact, i.e. the repo of its last work commit before the event (A⁻). The channel is *open* when the agent touches A⁻ in an executed command (any `artifact_mentions` action row resolving to A⁻: repo, file or site) in calls 1–5 after the event: the re-read path of H44/H58.
  - **M, memory note:** the latest intention (consolidation `nextSessionGoal` or session goal) before the event; its pointer is the repo it names. Open when it names A⁻.
  - **R, room:** chat items the agent receives (ledger receiving calls) in calls 1–5; the pointer is the repo they name most. Open when an item names A⁻.
  - **C, context window:** the repo touched most in calls −10…−1. Erased at F and N, intact at the matched placebos.
- **Events (scrambles of C):** F = forced erasure (first call after `reset_forced`, regime III); N = night (first call of the agent's PT day, all regimes). **Matched placebos** (context intact): P = the pseudo-erasure at position 21 of a no-reset run (H44), regime III; PN = one mid-day no-reset call per agent-day.
- **Information I_c (bits):** the plug-in mutual information I(X⁺; S_c) between the post-event allocation X⁺ and channel c's pointer S_c, Miller–Madow corrected, minus the mean over 200 within-agent permutations of S_c (so agent identity and repo popularity carry no bits). For C: I_C = I_P(X⁺; S_C) − I_F(X⁺; S_C), the allocation information the erasure destroys.
- **Value ΔV_c (commits per 20 calls):** with V = agent work commits in calls 1–20 after the event (rate × 20, truncated at the next reset, ≥ 10 calls), ΔV_c = β(open × scramble) in V ~ open + scramble + open × scramble + V_pre + agent-period fixed effects, events F ∪ P (call scale) or N ∪ PN (day scale). The placebo arm removes the part of "reading A precedes writing to A" that holds when nothing was erased. For C: ΔV_C = V(P) − V(F) with the same fixed effects (H15/H44's erasure cost).
- **κ_c = ΔV_c / I_c** (commits per 20 calls per bit), KW's "bang per bit" with natural scrambles in place of interventions. η = S/I is not identified (no optimal coarse-graining).
- **Departures from KW** (listed for axis A): the scramble is a *cut* of C, not a marginal-preserving shuffle; "open" channels are chosen by the agent, so ΔV_c is a DiD under a parallel-trends assumption (open vs closed would differ the same way with and without an erasure); allocation is a coarse-graining of the agent's state to repo identity.

### Rivals
- **R0, no store matters (allocation is prompt-held):** X⁺ is set by the role or goal in the prompt; I_A ≈ I_M ≈ 0 after the within-agent shuffle; ΔV_A ≈ 0.
- **R1, memory note carries it (KW stored information in M):** I_M ≥ I_A and ΔV_M ≥ ΔV_A.
- **R2, reading precedes writing (no semantic value):** the open × scramble interaction is ≈ 0: re-reading A raises V equally with and without an erasure.
- **R3, the room carries it (stigmergy through talk):** I_R and ΔV_R ≥ those of A.
- **R4, the goal carries it (field):** I_A collapses within a goal period once the goal is fixed, and all allocation information is the kickoff field. Tested by NE34 (N2).

## Data scheme (`scheme/`)
- **Script:** `scheme/build.py` (structure and pointers only from pre-event or early-window data; outcomes V and X⁺ are columns, not used in event selection).
- **Inputs:** `context_ledger_turns` (calls, `ctx_mode`, `ctx_pos`, reset flags, `first_of_day`), `context_ledger_items` (receiving call of each chat item), `work_commits` (agent work: `canonical & ~imported & author_kind == "agent" & ~automated`), `artifact_mentions` (`source` action / chat / intention; all `how`), `artifacts` (file and site → parent repo), `work_repos` (artifact ids ↔ repo name), `period_units`, `calendar`.
- **Transform:**
  1. Calls: all non-holdout ledger calls (`~holdout` and `holdout_mask`), the Claude Code agent excluded; per agent and PT day: sequence number, segments between resets (`reset_consol | reset_session | first_of_day`), position in segment.
  2. Work commits → the author's first call with `t_log` ≥ commit time (≤ 10 min; H44 rule). Action mentions → the call with `t_first` ≤ t ≤ `t_log` + 1 s. Chat mentions → each recipient's receiving call (`context_ledger_items`). Intentions → time.
  3. Artifact → repo: repo artifacts by `work_repos.artifacts`; files and sites by `artifacts.parent`.
  4. Events F, P (regime III, `ctx_mode == "cu"`), N, PN (all regimes) with the windows above; per event: A⁻ (last work commit before the event within 7 days), S_M, S_R, S_C, the four open flags, X⁺, V, V_pre (calls −20…−1), n calls in window, unit, period, regime.
- **Output:** `data/processed/H70-artifact-store-semantic-info/events.parquet` (codes and repo ids only, no text), `repo_ids.parquet` (repo name ↔ int id), `_provenance.json`; results in `results/`.
- **Regimes covered:** all three (nights); regime III (forced erasures). Allocation is measured on DQ4 commits, which are dense only from #30 (2026-02), so earlier periods are excluded (a zero there is ambiguous).

## Observables
Per period (replication) and pooled by DerSimonian–Laird across periods (CLAUDE.md exception (c): each event is a transition object); cluster bootstrap over agent-days (500 draws) for every CI.
- **O1 I_A** at nights and forced erasures (bits, shuffle-corrected), with the raw plug-in value and the permutation p.
- **O2 ΔV_A** (open × scramble DiD), commits per 20 calls and as a share of the placebo mean V.
- **O3 κ_A = ΔV_A / I_A**, ratio CI from the same bootstrap draws.
- **O4 the other rows** (I_c, ΔV_c, κ_c for M, R, C) pooled over regime III (N1) and at day scale.
- **O5 return probability** P(X⁺ = A⁻ | X⁺ ≠ none) after F vs P and after N vs PN (H58's descriptive anchor).
- **O6 NE34:** I_A for nights that cross a new-goal boundary vs within-period nights; the #39 → #40 continuation boundary separately.

## Null / baseline
- **Within-agent permutation of the pointer** (200 draws per period and event type): the information floor of I_c.
- **Placebo arm P / PN** (context intact, same agents, same periods): the DiD control for ΔV_c and the I_C reference.
- **Pre-event output V_pre** as a covariate (selection on busy stretches; DQ8 lever-design rule: eligibility from past information only, windows truncated identically in both arms).
- **Synthetic worlds at real counts** (axis F, `analysis/synthetic.py`, before real data): on the real event skeleton (agents, periods, event types, open-flag rates), plant (i) a valuable artifact channel (open raises V only after a scramble), (ii) "reading precedes writing" (open raises V equally in both arms; R2), (iii) nothing; and plant allocation information of known bits. The estimator must recover (i), keep size ≤ 0.07 under (ii) and (iii), and recover planted bits within ±0.1.
- **DQ8 null sizes:** no entry covers a DiD on per-event outputs; size is measured on the synthetic worlds instead (STANDARDS §3).

## Impostors (STANDARDS §1)
| Impostor | How it could fake an artifact store | How H70 removes it |
| --- | --- | --- |
| Scheduler field | Erasures and day starts fall at scheduler-set times; busy stretches carry both re-reads and commits | F timing is set by the 41-call cap; placebos come from the same agent-days; agent-period fixed effects; V_pre covariate; identical window truncation in both arms; nights compared with mid-day placebos, not cross-day |
| Exogenous field (goal, kickoff) | The goal names the repo, so allocation looks predictable from A⁻ | All estimates within a goal period; within-agent permutation; N2 treats the goal change as the scramble and #39 → #40 as the continuation control |
| Shared model priors | Some labs re-read more and commit more | Agent-period fixed effects; within-agent permutation; per-lab breakdown reported |
| Contemporaneous convergence | Room items name A⁻ because the agent is visibly working on it (R row) | Only items the agent actually received (ledger) count; the R row is compared at F vs P at the same lag; R is reported as provisional for HH307 |

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R0 prompt-held allocation; R1 memory note; R2 reading precedes writing; R3 room; R4 goal field.
**Locked holdout used for confirmation:** none yet. Planned in `analysis/confirm.py` (frozen, guarded, **not run**): NE24 (GitHub → GitLab, 2026-06-29, inside #50: the only involuntary scramble of the whole artifact store), plus the call-scale κ_A replication on held-out regime-III periods #43, #45–#50 and the #51 tail.

Round 1 scores (2026-10-04; evidence in "Round 1 results"):

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | pointers and outcomes from logged fields; KW departures listed (cut, agent-chosen open flags, repo coarse-graining) |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | parallel trends between arms assumed (checked only via the R2 synthetic); within-period stationarity assumed |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | I_A beats the permutation floor (7/9 call-scale periods); the value model does not beat R2 |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | return rates and the NE34 continuation contrast held; the κ ordering failed |
| E interventional | predicts the change across a natural experiment | 1 | 21k scaffold-timed erasures and goal boundaries; NE24 (involuntary artifact scramble) held out |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 | value and bits recovered at real counts; size ≈ 0.1 measured; additive-DiD trap found (A1) |
| G ground truth | agrees with known structure | 1 | erasure cost replicates H15/H44; the #39 → #40 continuation is known structure |
| H comparative | beats the named rivals | 1 | R2 beats the artifact-value model; R1 fails too |
| I transfer | holds in other same-mode periods, including the holdout | 1 | same pattern in 9 regime-III periods and at day scale; holdout not run |

## Prediction
*Written 2026-10-04 19:20 UTC, before running any outcome statistic (V, X⁺) on real data. Looked at before: counts of memory snapshots and work commits per period, the schema of the ledger and artifact tables, and H15/H44/H58's published numbers.*

| # | Prediction (H70 / HH261) | Counts against |
| --- | --- | --- |
| P1 | **The artifact store carries allocation bits across erasures.** Pooled I_A ≥ 0.3 bits after the within-agent shuffle at nights and at forced erasures; positive (permutation p < 0.05) in ≥ 2/3 of eligible periods at each scale. | pooled I_A < 0.1 bits, or positive in < 1/2 of periods |
| P2 | **The artifact channel has value only when the context was erased.** Pooled ΔV_A (open × scramble) > 0 with the CI excluding 0 at call scale (F vs P), ≥ +10% of the placebo mean V. | CI includes 0 or the sign is negative (R2 wins) |
| P3 | **Artifact beats memory note:** I_A > I_M and κ_A > κ_M at call scale, with non-overlapping CIs on I and ΔV_A > ΔV_M. | I_M ≥ I_A, or ΔV_M ≥ ΔV_A (R1) |
| P4 | **Artifact beats room:** I_A > 3 × I_R and ΔV_A > ΔV_R. | I_R ≥ I_A (R3) |
| P5 | **Context row (replication of H15/H44 on this estimator):** ΔV_C > 0 (V lower after F than at P) with I_C ≥ 0 small (< 0.3 × I_A): the erasure costs output but destroys little allocation information, because allocation survives in A. | I_C ≥ I_A (allocation lives in context) |
| P6 | **HH307 ordering for the rows H70 can estimate:** κ_A > κ_R > κ_M ≈ 0 (κ_M's CI includes 0). | any other order with non-overlapping CIs |
| P7 | **Return:** P(X⁺ = A⁻ \| a commit) ≥ 0.8 after F and N, within 0.1 of the placebo value. | < 0.6 after F |
| N1 | see `goalperiod-subhypotheses/NE41/README.md` | |
| N2 | see `goalperiod-subhypotheses/NE34/README.md` | |

**Verdict rule (per period, replication):** *supported* if I_A > 0 (p < 0.05) and ΔV_A's CI excludes 0 with a positive sign at the period's primary scale (call scale in regime III, day scale otherwise); *failed* if I_A is not significant or ΔV_A's CI excludes 0 with a negative sign; *mixed* if I_A > 0 and ΔV_A's CI includes 0; *descriptive* if fewer than 30 events per arm.

## Results by goal period
Verdict rule as pre-registered (A2: ΔV on the relative scale). "Failed" in G35 and G39 means the artifact pointer is constant within each agent (one repo per agent), so it carries no bits beyond agent identity; return rates there are 0.90–0.99.

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G30](goalperiod-subhypotheses/G30/README.md) | replication | descriptive | day: I_A -0.04 (p 1.000); ΔV_rel n/a; return 0.50 |
| [G31](goalperiod-subhypotheses/G31/README.md) | replication | mixed | day: I_A +0.21 (p 0.015); ΔV_rel +2.05 [-0.57, +19.81]; return 0.83 |
| [G33](goalperiod-subhypotheses/G33/README.md) | replication | descriptive | too few nights with a known artifact; return 1.00 |
| [G35](goalperiod-subhypotheses/G35/README.md) | replication | failed | day: I_A +0.00 (p 1.000); ΔV_rel -0.68 [-0.95, +2.43]; return 0.90 |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | mixed | call: I_A +0.04 (p 0.010); ΔV_rel +0.25 [-0.40, +1.41]; erasure cost 30%; return 0.71 |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | mixed | call: I_A +0.06 (p 0.005); ΔV_rel +0.01 [-0.65, +0.91]; erasure cost 12%; return 0.77 |
| [G38](goalperiod-subhypotheses/G38/README.md) | replication | mixed | call: I_A +0.11 (p 0.005); ΔV_rel +0.16 [-0.20, +0.67]; erasure cost 30%; return 0.87 |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | failed | call: I_A -0.00 (p 0.507); ΔV_rel -0.23 [-0.55, +0.17]; erasure cost 40%; return 0.99 |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | mixed | call: I_A +0.08 (p 0.005); ΔV_rel -0.27 [-0.47, +0.10]; erasure cost 34%; return 0.95 |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | mixed | call: I_A +0.34 (p 0.005); ΔV_rel +0.11 [-0.34, +0.68]; erasure cost 44%; return 0.88 |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | failed | call: I_A +0.02 (p 0.075); ΔV_rel +0.12 [-0.20, +0.61]; erasure cost 45%; return 0.98 |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | mixed | call: I_A +0.25 (p 0.005); ΔV_rel +0.20 [-0.36, +1.02]; erasure cost 44%; return 0.71 |
| [G51](goalperiod-subhypotheses/G51/README.md) | replication | mixed | call: I_A +0.14 (p 0.005); ΔV_rel -0.07 [-0.17, +0.02]; erasure cost 42%; return 0.88 |
| [NE41](goalperiod-subhypotheses/NE41/README.md) | native | failed | κ table (regime III pooled): I_A 0.14, ΔV_rel,A −0.05 [−0.13, +0.01]; I_M 0.04, I_R 0.02; context cost 41%, I_C 0.08, κ_C 5.2 [3.8, 8.4] |
| [NE34](goalperiod-subhypotheses/NE34/README.md) | native | supported | return at new goals 0.10 [0.02, 0.20] vs within 0.80 [0.67, 0.91]; #39 → #40 0.78 (n 9) |

## Round 1 results (2026-10-04, exploratory, non-holdout)
*Scripts: `scheme/build.py`; `analysis/{h70lib, synthetic, run, period_folders, figures, estimates_rows, confirm}.py`; shared estimator `infra/shared/semantic_kappa.py`. Numbers: `data/processed/H70-artifact-store-semantic-info/results/{periods, natives}.json`, `synthetic/synthetic.json`. Figures: `figures/summary_obs.pdf`, `figures/summary_synthetic.pdf`. Events: 21,165 forced erasures, 21,806 pseudo-erasures, 2,075 nights, 2,053 mid-day placebos (non-holdout, #30 on).*

### Synthetic validation (axis F, before real outcomes; after A1, A2)
On the real event skeleton (agents, periods, days, event types, real open flags and pointers), 8 replicates per world, B = 50:
- **Value:** a planted +30% channel value is recovered without bias (ΔV_rel 0.29–0.32 pooled; 0.29–0.39 per period). Power: call scale 1.0 (G51, G38, pooled), 0.63–0.88 (G41 size); day scale 0.88–1.0 (G51, pooled), 0.13–0.25 per mid-size period.
- **Size:** under "reading precedes writing" (×1.3 in both arms) and under the null, the rejection rate is 0.11 averaged over 32 configurations (0–0.38 per configuration; B = 50 makes intervals narrow). Per-period intervals are therefore mildly anticonservative; the pooled call-scale estimate is the primary result.
- **Information:** with no planted allocation information, I_A = 0.00 ± 0.01 and p < 0.05 in 3% of replicates; with planted return p = 0.6, I_A = 0.37–0.64 bits depending on the period's repo sets, p < 0.05 in 100%.

### Outcome vs prediction
| # | Prediction (locked 19:20 UTC) | Observed | Verdict |
| --- | --- | --- | --- |
| P1 | pooled I_A ≥ 0.3 bits; I_A > 0 in ≥ 2/3 of periods per scale | call 0.14 [0.12, 0.16] (DL 0.10 [0.04, 0.15]), 7/9 periods; day 0.08 [0.05, 0.11], 5/12 | **failed** (magnitude; day scale) |
| P2 | ΔV_A > 0, ≥ +10% (call) | ΔV_rel −0.05 [−0.13, +0.01]; −0.08 commits / 20 calls [−0.22, +0.02]; DL −0.07 [−0.15, +0.01] | **failed** (R2 wins) |
| P3 | I_A > I_M; ΔV_A > ΔV_M; κ_A > κ_M | I 0.14 vs 0.04 (non-overlapping); ΔV_M +0.05 [−0.07, +0.17]; both κ CIs include 0 | **mixed** (information yes, value no) |
| P4 | I_A > 3 I_R; ΔV_A > ΔV_R | 0.14 vs 0.02; ΔV_R +0.04 [−0.13, +0.31] | **mixed** |
| P5 | ΔV_C > 0; I_C < 0.3 I_A | cost 41% [38, 44]; I_C 0.08 [0.05, 0.10] = 0.56 I_A | **mixed** |
| P6 | κ_A > κ_R > κ_M ≈ 0 | κ_C 5.2 [3.8, 8.4]; κ_A −0.6 [−1.7, +0.2], κ_M, κ_R CIs include 0 | **failed** |
| P7 | P(return) ≥ 0.8 after F and N, within 0.1 of placebo | F 0.89 vs P 0.87; N 0.76 vs PN 0.82 | **mixed** (call yes, day 0.76) |
| N1 | NE41 κ table | see table above | **failed** |
| N2 | NE34 relevance scramble | new goal 0.10, within 0.80, continuation 0.78 | **supported** |

### The κ row (HH307), regime III pooled, call scale
| Channel | I_c (bits) | ΔV_rel | κ_c (commits / 20 calls / bit) |
| --- | --- | --- | --- |
| A own artifact | 0.138 [0.115, 0.161] | −0.05 [−0.13, +0.01] | −0.6 [−1.7, +0.2] |
| M memory note | 0.038 [0.019, 0.056] | +0.05 [−0.07, +0.17] | +1.0 [−1.6, +3.5] |
| R room | 0.020 [0.007, 0.033] | +0.04 [−0.13, +0.31] | +1.2 [−2.8, +5.7] |
| C context (erased) | 0.078 [0.051, 0.102] (destroyed) | 0.41 [0.38, 0.44] (lost) | **5.2 [3.8, 8.4]** |

Day scale (nights vs mid-day placebos, 12 periods): I_A 0.08 [0.05, 0.11], ΔV_rel,A +0.01 [−0.19, +0.26]; context cost 15% [6, 21], I_C 0.16 [0.06, 0.24], κ_C 1.0 [0.4, 2.5]. Rows for history search, kickoff and human messages can be added by building event frames with the same columns (`semantic_kappa.py` docstring).

### Answer to the question
No. Losing the context window costs output (41% of the next 20 calls); the artifact store and the memory note do not show measurable value when the agent uses them after an erasure. The artifact store is where allocation lives (89% return, 0.14 bits beyond identity; 80% next-day return within a goal), but allocation is cheap: what the erasure destroys is the working state, not the knowledge of which repo to open. A new goal, not the loss of a repo, is what scrambles the store's allocation information (NE34). Whether an *involuntary* loss of the artifact itself costs output is untested here: the only such scramble, NE24, is held out (`confirm.py` C1–C2).

### Impostors removed
- *Scheduler field:* forced erasures at cap-set times; placebos from the same agents and days; Poisson fixed effects at agent-period × arm; V_pre covariate.
- *Goal field:* estimation within goal periods; within-agent permutation; NE34 treats the goal change as the scramble.
- *Shared priors:* agent-period fixed effects; the permutation floor removes agent identity.
- *Convergence:* only received items count for R; R's open share is higher right after a reset (0.045 vs 0.018: the consolidation backlog), which the placebo arm cannot fully match, so R is provisional.

### Scorecard (round 1)
| Axis | Score | Evidence |
| --- | --- | --- |
| A mapping | 1 | every pointer and outcome from logged fields; departures from KW listed (cut, not shuffle; agent-chosen open flags; repo coarse-graining) |
| B assumptions | 1 | parallel trends between arms assumed, checked only through the R2 synthetic; stationarity within periods assumed |
| C adequacy | 1 | I_A beats the permutation floor in 7/9 call-scale periods; the value model does not beat R2 |
| D unfitted predictions | 1 | return rates and the NE34 continuation contrast predicted and held; κ ordering failed |
| E interventional | 1 | 21k scaffold-timed erasures and goal boundaries as scrambles; no involuntary artifact scramble outside the holdout |
| F identifiability | 2 | value and bits recovered at real counts; size measured (≈ 0.1) and the additive-DiD trap found (A1) |
| G ground truth | 1 | erasure cost replicates H15/H44 (−41% vs −39%); the continuation boundary is known structure |
| H comparative | 1 | R2 and R1 compared; R2 wins, which is the main result |
| I transfer | 1 | same pattern in 9 regime-III periods and at day scale; holdout not run |

**Scorecard: A1 B1 C1 D1 E1 F2 G1 H1 I1.** The HH261 lever (E) stays at 1: the decisive involuntary scramble (NE24) is in the holdout.

## Confirmatory design (written 2026-10-04 after round 1; `analysis/confirm.py`, frozen, guarded, NOT RUN)
Targets: NE24 (GitHub → GitLab, 2026-06-29, inside #50) and the held-out regime-III periods #43, #45–#50 and the #51 tail. Frozen predictions: C1 (NE24) on the first two migration days, agents' first-commit return to their own project (repo-name stem matched across hosts) is ≥ 0.5 [0.6]; C2 (NE24) daily work commits per agent on 06-29..06-30 fall below the mean of the 5 preceding non-weekend days by ≥ 20% (agent-paired, CI below 0) [0.55]; C3 the call-scale context cost (P vs F, Poisson) pooled over targets lies in [0.25, 0.55] with the CI excluding 0 [0.85]; C4 ΔV_rel,A pooled over targets has its CI including 0 or below 0 (no artifact-channel value) [0.7]; C5 I_A pooled over targets > 0 with the CI above 0 [0.8]. Guards: `--confirm --i-understand-this-uses-the-locked-holdout`; refuses with uncommitted H70 files; `holdout_ledger.check()` per target; `--dry-run` on stand-ins (#41, #42, #44, #51 08-24 → 09-04; NE24 stand-in: the #39 → #40 continuation boundary).

## Round 2 redirects (2026-10-04)
- **H70-R1.** Value the artifact by what is re-read: join post-erasure reads to the files touched before the erasure (H44-R3) and test whether re-reading the exact pre-erasure files shortens the dip.
- **H70-R2.** Add the history-search row (HH294: the 03-31/04-01 outage) and the kickoff row to the κ table with the shared estimator.
- **H70-R3.** Run `confirm.py` on NE24 after disclosure: the one involuntary scramble of the whole artifact medium.
- **H70-R4.** Allocation information by role: in #51 (private roles), split the artifact bits into identity, role and artifact parts.

## Notes
- 2026-10-04 19:20 UTC: card written before any outcome statistic (see the Prediction header). Holdout masked with `holdout_mask` and the ledger's `holdout` flag in every script; held-out counts never printed.
- 2026-10-04 ~20:00 UTC, **build fixes before any outcome (structural):** (i) the memory-note pointer join used an unsorted intention table, so S_M was set for 1% of events; fixed (27%). (ii) Day-scale windows were cut at regime-I/II session resets, which dropped most nights in #30–#35; N and PN windows now run 20 calls within the day (F and P still stop at the next reset). Counts only were looked at.
- 2026-10-04 ~20:40 UTC, **Amendment A1 (synthetic, before real outcomes): the value estimator is a Poisson DiD, not an additive one.** On the real G51 skeleton, a world where re-reading raises output ×1.3 in both arms and the erasure lowers output ×0.74 gave an additive open × scramble coefficient of −0.14 with 90% rejections: the additive DiD reads a multiplicative "reading precedes writing" effect as a *negative* channel value whenever the scramble itself lowers output. The estimator is now a Poisson pseudo-likelihood with stratum × arm fixed effects: ΔV_rel = exp(β_open×scramble) − 1 (scale-free) and ΔV (commits per 20 calls) = mean V of open scramble events × (1 − exp(−β)). The context row's cost is the same Poisson model on the scramble indicator. `semantic_kappa.py --verify` passes on multiplicative worlds (bias ≤ 0.02, coverage 0.9–1.0). P2's "≥ +10% of the placebo mean V" now reads ΔV_rel ≥ 0.10.
- 2026-10-04 ~21:30 UTC, **Amendment A2 (synthetic, before real outcomes): bootstrap strata.** The first synthetic pass relabelled each resampled cluster as its own fixed-effect stratum, which turned the agent-period fixed effect into an agent-day one inside the bootstrap; at day scale (one night and one placebo per agent-day) every interval collapsed (rejection rate 0 even with a planted effect). Resampled clusters now keep their original stratum. The synthetic was re-run in full after the fix; the verdict rule now reads ΔV_A's CI on the relative (Poisson) scale.
