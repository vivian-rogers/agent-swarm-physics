# H69: Restatement loops are context fixed points

**Status:** round 1 done (2026-10-04; exploratory, non-holdout). **Half right: restatement loops are held by the context window, but the trigger is not a self-share threshold and novel input does not end them.**
- **Context-held (supported):** at matched lag and call distance, an agent near-copies its own earlier statement 3.4× [2.6, 4.5] more often when that statement is still in its context than when an erasure has removed it (4/4 scorable periods, I² 0; both embedding models; pseudo-erasure 1.13 [0.99, 1.28]). A forced erasure (NE41) between two statements raises loop exit 2.4× [1.2, 4.9] and lowers onset to 0.54× [0.34, 0.86].
- **Not a share threshold (failed):** own statements in the segment raise onset (b_O 0.34 [0.09, 0.60] per log unit), but room items in context do not dilute it (b_K +0.04 [−0.17, 0.25]); the self-share coefficient is not significant pooled (0.53 [−0.12, 1.19]). The threshold test has no power (synthetic ≤ 0.13).
- **Novel input does not end loops (failed):** exit per log(1 + novel reads) 1.23 [0.85, 1.78], no larger than the in-flight placebo (1.58 [0.97, 2.57]); in G51, nudges read inside a loop 0.81 [0.49, 1.34].
- Scorable periods (≥ 30 episodes): G38, G40, G41, G51. Verdicts: G38 supported (native), G40, G41 mixed, G51 failed (native: nudges), NE41 mixed, 5 descriptive. Predictions, synthetic validation (axis F) and amendments A1–A5 came before real data. `confirm.py` written, dry-run only, **not run**.
**Question:** **Q4** (where does the swarm's information live?): if a loop is held by the context window, the context carries the agent's self-reinforcing state and an erasure (an operator lever, Q5) ends it; if not, the loop lives in the agent or its task.
**Fields:** nonequilibrium stat mech (self-coupled spin, fixed points, bistability), information theory (copying vs transformation), dynamics (hazards, event studies)
**Literature:** [Kolchinsky & Corominas-Murtra 2020](../../literature/kolchinsky-2020-copying-versus-transformation.md) (a restatement is copy information from the agent's own past; the reference distribution can be "what the agent says at the same lag without the source in context").
**Definitions used** (`physics-models/DEFINITIONS.md`): Regime; *Context fill* (`ctx_pos`); *Context segment* (H45); *Loop episode (restatement / copy)* (H55: restatement = `self_repeat` by either model, copy = both); *Exposure (ledger receiving call)*; *Interaction (ledger-visible exposure)* and its *unread (in-flight) exposure placebo* (RE-D1); *Talk turn (ledger)*. New named variants proposed (not edited into DEFINITIONS.md), defined under Observables: **cross-call restatement**, **self-share (chat, segment)**, **novel input (read, bge)**, **in-context enrichment**.
**From:** HH259 in `hypotheses/hypohypotheses/HYPOHYPOTHESES.md` ("Making the faithful ones better") · **Models:** `physics-models/08-copying-vs-transformation/`, `physics-models/02-nonequilibrium-ising/`
**Data inputs (shared tables first):** DQ5 `statement_flags` (both models) and raw chat embeddings (`chat_bge_small`, `chat_gte_modernbert`); DQ1 ledger (`call_windows`, `context_ledger_turns`: `ctx_pos`, `k_ctx`, `chars_new`, reset flags; `context_ledger_items`); `events_core` (AGENT_TALK → call), `chat_core`, `kicks_classified` (nudge / human message classes), `roster`, `calendar` + `holdout_mask`.

## Question
H12 found that the lowest-dimensional regime-III weeks are agents restating themselves (restatements 12–25% of chat in #38–#40). H44 found that forced erasures break *command* loops (OR ≈ 0.1). Do *restatement* loops start when the agent's context fills with its own recent output above a threshold, and end at erasure or when novel input arrives?

## Design: two layers (Vivian, 2026-10-04; see `infra/data-quality/QUEUE.md`)
- **Replication:** the common estimators on every eligible regime-III period (#36 from 03-24, #37–#42, #44, #51 non-holdout days). Context segments and forced erasures exist only in regime III. Period README role: `replication`.
- **Period-native tests** (written before running them):
  - **NE41** (forced erasure at the 41-call cap): the erasure is timed by the scaffold, not the agent. The transition is the object (exception (c)): the event study compares the two sides of each erasure, per period, with a random-effects pool next to the per-period rows.
  - **G38** (the loop week: 17 days, 21% restatements): the in-context enrichment test at the highest pair count.
  - **G51** (operator and human input inside loops): nudges and human messages are exogenous novel input read at a known call; in-flight ones (posted, not yet read) are the placebo.
- **Faithfulness lever:** HH259 targets axis B (mechanism: the loop's state variable) and axis E (NE41 as an intervention). The scorecard says whether it moved them.

## Model
**From:** `physics-models/02-nonequilibrium-ising/` (a self-coupled spin in a field) and `08-copying-vs-transformation/` (a restatement is copy information from the agent's own past).

**Degrees of freedom.** Agent i's chat statements x_1, x_2, … in one PT day. A statement is a **restatement** (r_t = 1) when it nearly copies an earlier statement of the same agent from an earlier call; otherwise it transforms (new content). The context at the producing call holds O_t own statements and K_t room items since the last reset.

**H69 variant (self-conditioned generation).** The generation map x_{t} = F(x_{<t}; context) has a self-coupling proportional to the self-share s_t = O_t / (O_t + K_t):
logit P(r_t = 1 | r_{t−1} = 0) = a_i + J (s_t − s*)₊ + controls,
logit P(r_t = 0 | r_{t−1} = 1) = b_i − J′ s_t + c_E · E_t + c_ν · N^nov_t + controls.
- **Fixed point:** above the threshold s* the restatement state reinforces itself (each restatement raises O_t and s_t): a magnetized phase of one spin with self-coupling J s.
- **Exit:** an erasure (E_t = 1: a reset between t − 1 and t) empties O_t, so s → 0. Novel input read since t − 1 (N^nov_t) adds K and acts as a field pulling x away from the fixed point.
- **Source location:** a restatement copies a statement that is *still in context*. At the same lag, a statement erased from context is copied less.

**Rivals.**
- **R0 recency/topic (null):** restatements copy recent statements by time and call distance, independent of what is in context. No threshold, no erasure effect at matched lag and call distance, no input effect.
- **R1 input starvation (H72's clock):** restatements happen when no new input has arrived since the last statement; the count of own statements in context does not matter.
- **R2 task state:** agents restate while blocked or waiting (H16 traps); the loop lives in the task, so it survives erasure.
- **R3 context fill (H46):** style and content drift with `ctx_pos`; restatement rises with fill, not with self-share.

## Data scheme (`scheme/`)
- **Inputs:** listed above. Holdout rows are dropped with `calendar.holdout`, `holdout_mask` and the ledger's `holdout` flag before anything is computed.
- **Transform (`scheme/build.py`):**
  1. Regime-III, non-holdout agent chat statements (`statements.parquet`, kind = chat) with their DQ5 flags (`self_repeat_{bge,gte}`, sources `self_repeat_src_{bge,gte}`, `templated`, `cross_echo`).
  2. Each statement → its producing ledger call (AGENT_TALK event time in [t_first, t_log] of the agent's call, DQ2's rule). Calls are ordered per agent-day; a **segment** starts at a call with `reset_consol`, `reset_session` or `first_of_day`; `reset_forced` marks forced erasures (NE41).
  3. **Cross-call restatement** r_t: flagged by a model whose matched source lies in an *earlier call* (same-call sources are message splitting, not restatement). Primary: either model (H55's restatement); variants: bge, gte, both (copy); excluding templated statements.
  4. Per statement t: O_t (own statements in the segment before t), K_t = `k_ctx` at the producing call, s_t = O_t/(O_t + K_t) (0 when both are 0); the char-weighted variant (own chars vs `chars_new` summed in the segment); `ctx_pos`; n_prev (earlier own statements that day: the flag's opportunity); lag and calls since the previous own statement; resets between (forced / voluntary / session); items read since the previous statement (ledger) with their novelty; in-flight items (posted in the agent's room in [t_call, t_statement), not read).
  5. **Novelty** of a read item: ν = 1 − max cos(item, the agent's last 5 statements) on raw bge-small vectors; "novel" = ν above the period median over read items (gte variant).
  6. **Pairs** (t, u) for the source-location test: u an earlier same-day own statement from an earlier call within 3 h (at most the 40 most recent), with lag, calls between, `in_seg` (same segment as t) and near-copy (cos > the DQ5 threshold of that model).
- **Output:** `data/processed/H69-loops-context-fixed-points/G<NN>/statements.parquet`, `pairs.parquet`, `results.json`; `synthetic/`; `_provenance.json`. Codes and numbers only, no text.
- **Regimes covered:** regime III only (2026-03-24 → 2026-09-04, non-holdout days).

## Observables
*Written 2026-10-04 before any H69 statistic on real data.*
1. **Onset (entry) model:** conditional on r_{t−1} = 0, logit P(r_t) with agent fixed effects and controls log(1 + n_prev), log lag, log(1 + ctx_pos), log(1 + items since previous). Coefficients: b_s on s_t; in the split form, b_O on log(1 + O_t) and b_K on log(1 + K_t). H69: b_s > 0 and b_K < 0 at fixed O. R1: only items-since-previous matters. R3: only ctx_pos matters.
2. **Threshold:** hinge (s − s*)₊ vs linear in s (profile over s* ∈ [0.1, 0.9]); ΔAIC.
3. **Exit model:** conditional on r_{t−1} = 1, logit P(r_t = 0) with agent fixed effects: OR for a forced erasure between t − 1 and t, a voluntary erasure, novel items read, novel in-flight items (placebo), novel items read only by the *next* statement's call (future placebo), s_t; controls log calls between, log lag, log(1 + n_prev).
4. **In-context enrichment (source location):** over pairs (t, u), the Mantel–Haenszel odds ratio of a near-copy for u in the current segment vs u in an erased segment, stratified by agent × log-lag bin (0.1 decade) × calls-between bin. H69: OR > 1. R0/R2: OR ≈ 1.
5. **Loop statistics (descriptive):** restatement rate, persistence P(r_t = 1 | r_{t−1} = 1) vs P(r_t = 1 | r_{t−1} = 0), episode lengths.

## Null / baseline
- **R0 synthetic null** on real skeletons (real statement times, calls, segments, k, resets, items): restatements copy earlier statements with weights that decay with lag and calls between, with no role for segment membership, self-share or input. Every H69 statistic must be ≈ 0 (OR ≈ 1) there; its size is measured.
- **Placebos:** in-flight novel items and next-call novel items (cannot cause the exit at t).
- **Pseudo-erasure:** the enrichment OR computed with a fake segment boundary at the midpoint of each real segment (no erasure there) must be ≈ 1.

## Impostors (`STANDARDS.md` §1)
| Impostor | How it could fake H69 | How H69 removes it, or why it does not apply |
| --- | --- | --- |
| Scheduler field | Timer wakes with no news produce "still waiting" restatements; day starts reset segments | Per-call clock (calls between, not minutes, as the control); first statements of a day are not at risk (the flag needs an earlier same-day statement); items-since-previous control (R1) |
| Exogenous field (kickoff, goal, operator) | Agents restate the goal or an operator instruction; templated phrasing | Variant excluding `templated` and `cross_echo` statements; G51 native treats operator input as the exogenous field it is |
| Shared model priors (family, style) | Some families loop more; style drifts with context fill (H46) | Agent fixed effects in every model; per-lab breakdown; `ctx_pos` control (R3) |
| Contemporaneous convergence | Same-call message splitting and same-moment posts look like restatements; room moments co-move with exits | Cross-call restatements only; in-flight and future-call placebos for the input effect (RE-D1 rule); matched lag and call distance in the enrichment test |

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** R0 recency/topic, R1 input starvation, R2 task state, R3 context fill.
**Locked holdout used for confirmation:** none in round 1. Targets frozen in `analysis/confirm.py` (not run): #51 tail, #43, #45–#47, #49, #50.
**Scorecard (round 1): A1 B1 C1 D1 E1 F2 G1 H1 I1.**

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Restatements from DQ5 flags (either model, source in an earlier call), context segments and items from the DQ1 ledger, all from shared tables. The enrichment holds under bge (3.5), gte (6.1) and copies (both, 8.6). Not invariant: restatement rates run 0.7–25% by period, and only 4 periods have ≥ 30 episodes. Self-share counts chat items, not tokens (the char variant agrees). |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | **Lever moved:** the loop's state variable is located: the restated content must be in context (matched lag and call distance, pseudo-erasure null). The pre-registered state variable (self-share with a threshold) fails: own count matters, room dilution does not. Context fill (`ctx_pos`) also raises onset (controls +0.34 to +0.46 in G38–G41), so R3 is partly right. Per-call clock throughout. |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | The enrichment and erasure effects beat the R0 recency null (synthetic size 0–0.06 in scorable periods) and the pseudo-erasure placebo. No held-out days. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | Passed: source-location enrichment (3.4×), forced-boundary enrichment (3.5×), pseudo-erasure ≈ 1. Failed: room dilution of onset, novelty-driven exit, the threshold (no power). |
| E interventional | predicts the change across a natural experiment | 1 | **Lever moved:** NE41 forced erasures (timed by the 41-call cap) raise exit 2.4× [1.2, 4.9] and cut onset to 0.54× [0.34, 0.86]; the onset half misses the pre-registered ≤ 0.5 by its point estimate. Voluntary erasures act the same (2.4×). |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 2 | Real skeletons, simulated vectors, the real flag rule: sizes ≤ 0.07 and power ≥ 0.7 for P1, P3, P4 where ≥ 30 episodes; two design errors found and fixed before real data (A1, A2); P2 shown powerless; P5 shown not to separate starvation. Both embedding models; templated statements excluded as a variant (onset b_O unchanged). |
| G ground truth | agrees with known structure | 1 | Agrees with H44 (command loops break at erasure, OR 0.11), H12's loop weeks (#38–#40 carry the episodes) and H55 (directed input barely moves loop escape). No labelled loops exist. |
| H comparative | beats the named rivals | 1 | Beats R0 (recency) and R2 (task state: a task-held loop would survive erasure). Does not beat R1 (input starvation) on exit, and R3 (fill) shares onset with own count. |
| I transfer | holds in other same-mode periods, including the holdout | 1 | Enrichment > 1 in 4/4 scorable periods (2.7–4.1) and in G39 (2.2, 20 episodes); the erasure exit effect is heterogeneous (I² 0.74; G41 1.25, G51 1.36 n.s.). Holdout not used. |

## Prediction
*Written 2026-10-04 19:25 UTC, before any H69 statistic on real data.*

**What I had seen first:** H12's restatement shares per period (DQ5: 21% / 25% / 12% in #38 / #39 / #40), H44's command-loop result (OR 0.11), H55's loop-escape result (being addressed +0.05; corrections no effect), H46's style drift with context fill, H57's contemporaneous-convergence lesson, and the schemas and row counts of the ledger and flag tables. No H69 observable had been computed.

**Scorable period:** ≥ 30 restatement episodes and synthetic power ≥ 0.8 for the statistic at the H69 effect size (set before real data). The pooled values are random-effects means over scorable periods, reported next to the per-period values.

| # | Prediction | Counts against |
| --- | --- | --- |
| P1 | **Self-share drives onset.** b_s > 0 (CI excludes 0) in ≥ 50% of scorable periods and pooled; in the split form b_K < 0 at fixed O (pooled CI < 0) | b_s ≤ 0 pooled, or b_K ≥ 0: own output in context does not raise onset, or room input does not dilute it |
| P2 | **Threshold.** The hinge beats linear in s (pooled ΔAIC ≥ 4) with s* in [0.2, 0.8] | linear or concave fits as well |
| P3 | **Erasure ends loops.** Exit OR for a forced erasure ≥ 2 pooled (CI > 1) | OR CI includes 1 |
| P4 | **Restatements copy what is in context.** In-context enrichment OR ≥ 2 pooled (CI > 1) and > 1 in ≥ 60% of scorable periods; pseudo-erasure OR within [0.8, 1.25] | OR CI includes 1: the restated content does not need to be in context (R0, R2) |
| P5 | **Novel input ends loops.** Exit OR per novel item read > 1 pooled (CI > 1), and larger than the in-flight and future-call placebo ORs | read OR ≈ placebo OR |
| N-NE41 | Forced erasure: exit OR ≥ 2, and the onset rate in the first statement after an erasure ≤ 0.5 × the matched no-erasure rate | OR CI includes 1 |
| N-G38 | P1 and P4 hold in G38 (b_s > 0, enrichment OR ≥ 2) | either fails in G38 |
| N-G51 | A nudge or human message read inside a loop raises exit (OR ≥ 1.5, CI > 1); the same messages in flight do not (CI includes 1) | read OR CI includes 1, or in-flight OR as large |

**Verdict rule per period:** *supported* = P1 and P4 pass and P3 or P5 passes (where powered); *failed* = P1 and P4 both fail; *mixed* = otherwise; *descriptive* = not scorable.

Prior credences (Claude, 2026-10-04): P1 0.35, P2 0.15, P3 0.6, P4 0.45, P5 0.3, N-NE41 0.55, N-G38 0.3, N-G51 0.3.

## Synthetic validation (axis F; run 2026-10-04 ~19:50–20:40 UTC, before any H69 statistic on real data)
`analysis/synthetic.py`; outputs in `data/processed/H69-loops-context-fixed-points/synthetic/` (`worlds.parquet`, `summary.json`). Real skeletons of all 9 periods (G51: a random 25% of agent-days), 16 replicates per world (G51: 8). The flag is recomputed from simulated 32-d vectors with the real rule (max cosine to earlier-call statements > 0.95), and the overall rate is matched to each period's real cross-call restatement rate (a nuisance level; 1–22% by period).

Rejection rates (two-sided 5% tests read one-sided in the predicted direction; P4 = bootstrap CI above 0):

| Statistic | Z0 recency null (size) | Z1 H69 world (power) | Z2 starvation rival |
| --- | --- | --- | --- |
| P1 b_s > 0 | 0–0.07 in G38–G41, G51; 0.13–0.33 in tiny G37, G42 | ≥ 0.92 in G36–G39, G41, G42, G51; 0.19 G40, 0.31 G44 | 0–0.19 |
| P1 b_K < 0 | 0–0.06 | 1.0 G38; 0.19–0.75 elsewhere | 0–0.13 |
| P2 hinge ΔAIC ≥ 4 | 0–0.06 | **0–0.13 everywhere** | 0–0.13 |
| P3 forced-erasure exit | 0–0.06 where ≥ 30 episodes; 0.5–1.0 in G42, G44 (≤ 4 episodes) | 0.94 G38, 0.88 G39, 1.0 G51; 0.69–0.73 G40, G41 | 0.13–0.25 |
| P4 enrichment CI > 0 | 0 in G38–G41, G51; 0.19–0.75 in G36, G37 (≤ 1 episode) | 1.0 in G38–G41, G51 | 0–0.13 |
| P5 novel reads raise exit | 0–0.06 | 0.75 G38, G51; 0.13–0.5 elsewhere | 0.19–0.5 |
| P5 in-flight placebo | 0–0.19; **0.38 in G51** (subsample) | — | — |
| pseudo-erasure OR ≠ 1 | 0–0.13 | 0–0.25 | 0–0.19 |

Readings:
- Where a period has ≥ 30 restatement episodes, P1, P3 and P4 have size ≤ 0.07 and power ≥ 0.7 at the H69 effect size. Below that the exit and enrichment tests are unreliable (sizes up to 1.0), so the episode rule is needed.
- **P2 has no power** (≤ 0.13) at J = 4, s* = 0.3: in regime III the self-share rarely exceeds 0.3 (median O ≈ 1 own statement vs K ≈ 3 room items per segment).
- **P5 does not separate H69 from input starvation:** novel reads raise exit in Z2 too (0.19–0.5), because reads lower restatement generally there.
- The in-flight and next-call placebos reject too often in small samples (G51 subsample 0.25–0.38).

## Amendments (2026-10-04 ~20:45 UTC, after the synthetic validation, before any H69 statistic on real data)
- **A1 · Exit model without the self-share (primary).** An erasure acts through s (it sets O → 0). With s in the model the erasure coefficient is the direct effect only and had no power in Z1. The primary exit model leaves s out (total effect); the s-adjusted model is a variant.
- **A2 · Z1 corrected.** In the first Z1 draft an erased source was still copied whenever chosen, so erasure had no effect. Z1 now copies an erased source with probability 0.25 (the table above uses the corrected world).
- **A3 · P2 is inconclusive by design** (power ≤ 0.13). It is reported, and it cannot pass or fail.
- **A4 · Scorable rule.** A period is scorable when it has ≥ 30 restatement episodes; the pooled (random-effects) values use scorable periods only. Each per-period P is read only where Z1 power ≥ 0.8 for that statistic.
- **A5 · Placebos are descriptive.** The in-flight and next-call coefficients are reported next to the read coefficient; P5 needs read > 0 and a read coefficient outside the placebo CIs. P5 alone does not separate H69 from input starvation (Z2); only P1's split form (b_K at fixed O, which Z2 does not produce) and P4 do.

## Results by goal period
*Exploratory, non-holdout, regime III. Restatement: cross-call, either model. ORs from logits with agent effects and agent-day cluster SEs; enrichment: Mantel–Haenszel with an agent-day bootstrap.*

| Period | Role | Verdict | Key numbers |
| --- | --- | --- | --- |
| [G36](goalperiod-subhypotheses/G36/README.md) | replication | descriptive | 1,119 statements; restatement 1.2%; 1 episode |
| [G37](goalperiod-subhypotheses/G37/README.md) | replication | descriptive | 700; 0.7%; 0 episodes |
| [G38](goalperiod-subhypotheses/G38/README.md) | native | supported | 4,558; 21.3%; 154 episodes; b_s 0.80 [0.03, 1.57], b_K 0.01; enrichment 3.9 [2.6, 6.4]; forced exit 4.9 [2.9, 8.6]; novel-read exit 1.62 [1.20, 2.20] |
| [G39](goalperiod-subhypotheses/G39/README.md) | replication | descriptive | 865; 25.3%; 20 episodes; enrichment 2.2 |
| [G40](goalperiod-subhypotheses/G40/README.md) | replication | mixed | 1,731; 12.1%; 37 episodes; enrichment 3.7 [1.7, 7.5]; forced exit 3.0 [1.4, 6.1]; b_s n.s. |
| [G41](goalperiod-subhypotheses/G41/README.md) | replication | mixed | 2,146; 8.2%; 34 episodes; enrichment 4.1 [2.0, 15.7]; forced exit 1.3 n.s. |
| [G42](goalperiod-subhypotheses/G42/README.md) | replication | descriptive | 1,218; 2.5%; 6 episodes |
| [G44](goalperiod-subhypotheses/G44/README.md) | replication | descriptive | 1,743; 2.1%; 1 episode |
| [G51](goalperiod-subhypotheses/G51/README.md) | native | failed | 40,958; 3.8%; 182 episodes; nudge read in a loop: exit 0.81 [0.49, 1.34]; enrichment 2.7 [1.7, 3.9]; forced exit 1.36 [0.77, 2.38] |
| [NE41](goalperiod-subhypotheses/NE41/README.md) | native | mixed | pooled over 4 periods: forced-erasure exit 2.4 [1.2, 4.9]; onset after erasure 0.54 [0.34, 0.86] (predicted ≤ 0.5) |

## Results
*All numbers: `data/processed/H69-loops-context-fixed-points/results.json` (`analysis/run_periods.py`) and `G<NN>/results.json`. Figures: `figures/summary_obs.pdf` (effects), `figures/summary_obs2.pdf` (synthetic).*

### Outcome vs prediction (random-effects pools over G38, G40, G41, G51)
| # | Prediction | Observed | Outcome |
| --- | --- | --- | --- |
| P1 | b_s > 0 in ≥ 50% of scorable periods and pooled; b_K < 0 | b_s CI > 0 in 1/4 (G38); pooled 0.53 [−0.12, 1.19]; **b_K +0.04 [−0.17, 0.25]**; b_O 0.34 [0.09, 0.60] | **failed** (own count matters; the share does not) |
| P2 | hinge beats linear (ΔAIC ≥ 4) | ΔAIC ≤ 2 except G51 (6.6, s* at the grid edge 0.9) | inconclusive (no power, A3) |
| P3 | forced-erasure exit OR ≥ 2 | 2.40 [1.18, 4.88] (I² 0.74); s-adjusted 2.85 | **passed** |
| P4 | enrichment OR ≥ 2, > 1 in ≥ 60%; pseudo in [0.8, 1.25] | **3.38 [2.56, 4.46]**, 4/4 (I² 0); forced boundaries 3.53; pseudo 1.13 [0.99, 1.28] | **passed** |
| P5 | novel-read exit OR > 1, above placebos | 1.23 [0.85, 1.78]; in flight 1.58 [0.97, 2.57]; next call 0.92 | **failed** (G38 alone 1.62) |
| N-NE41 | exit OR ≥ 2; post-erasure onset ≤ 0.5× | 2.40 [1.18, 4.88]; 0.54 [0.34, 0.86] | **mixed** (onset misses by its point) |
| N-G38 | P1 and P4 hold in G38 | b_s 0.80 [0.03, 1.57]; enrichment 3.9 [2.6, 6.4] | **supported** (but b_K ≈ 0 there too) |
| N-G51 | nudge/human read raises exit (OR ≥ 1.5) | nudges 0.81 [0.49, 1.34]; humans 1.38 [0.48, 3.95] | **failed** |

### Findings
1. **The loop lives in the context window.** Restatement is copying from context: a statement still in context is near-copied 3.4× more often than one at the same lag and call distance that an erasure removed. The effect is the same at forced (scaffold-timed) boundaries, so the agent's own choice of when to consolidate does not create it.
2. **Erasure is the loop breaker.** A forced erasure between two statements more than doubles the chance that a loop ends (2.4×) and halves the chance that one starts (0.54×). This matches H44's command loops (OR 0.11) at a weaker strength.
3. **The trigger is own-content density, not self-share.** Each doubling of the agent's own statements in the segment raises onset odds by ×1.27 (e^{0.34 ln 2}). More room messages in the same context do not lower it. A loop is not a fixed point that room traffic can dilute; it is a copy from whatever own text the window holds.
4. **Input does not rescue a looping agent.** Novel messages read, nudges and human messages do not raise exit beyond placebos (pooled). G38 is the exception (1.62 per log unit), consistent with H55's small address effect.

### Caveats
- Only 4 periods have ≥ 30 episodes; G51 has 182 episodes but a 3.8% rate. The erasure exit effect is heterogeneous (G41 1.25, G51 1.36 n.s.).
- Statement-level geometry is model-dependent (DQ5); gte gives a larger enrichment (6.1) than bge (3.5). The direction holds in both.
- The self-share counts chat items. Own tool output, which dominates prompt tokens (H45), is not in it.
- Erased sources are not gone from the agent: memory and artifacts may carry them, so the enrichment is a lower bound on the context effect.
- Multiplicity: 9 periods × ~10 statistics. The pooled enrichment (p < 1e-15) and erasure effects (p 0.01–0.02) survive Bonferroni over the 10 pooled statistics only for the enrichment.

## Confirmatory design (written 2026-10-04 after round 1, before any holdout use; `analysis/confirm.py`, dry-run only, NOT run)
Frozen C1–C6 on #43, #45–#47, #49, #50 and the #51 tail (scored at ≥ 30 episodes): enrichment ≥ 1.5 with CI > 1; forced-erasure exit > 1; post-erasure onset < 1; b_K CI includes 0 or above; b_O > 0; novel-read exit CI includes 0. The dry run (G38, G41, G51 stand-ins, built in memory through the same scheme) reproduces G38's enrichment exactly. The scheme's holdout switch (`ALLOW_HOLDOUT`) is set only by `confirm.py`.

## Notes
- **Recheck (coordinator, 2026-10-04, definitions consolidation):** this scheme cuts context segments at `first_of_day` as well as at `reset_consol | reset_session`. The infra rule cuts only at resets (in regime III, `ctx_pos` carries over the night). Recheck the in-context enrichment with the infra segmentation in round 2.
- 2026-10-04 19:25 UTC: card, predictions and nulls written before any H69 statistic.
- 2026-10-04 ~19:50–20:45 UTC: synthetic validation; amendments A1–A5.
- 2026-10-04 ~20:50 UTC: real-data run; rerun ~21:00 with a quasi-separation guard (G44's exit model and G51's in-flight human coefficient were not estimable; no scorable-period number changed). Period READMEs, figures, estimates rows (61).
- Code map: `scheme/build.py`; `analysis/h69lib.py` (logit with agent effects, onset/exit, MH enrichment, pooling), `synthetic.py`, `run_periods.py`, `write_period_cards.py`, `figures.py`, `estimates_rows.py`, `confirm.py`.

## Round 2 redirects (2026-10-04)
- **H69-R1.** Measure own content in tokens (H45's prompt sizes) and test whether onset depends on own tool output as well as own chat.
- **H69-R2.** Dose of erasure: does a partial context trim (NE22's 200-event cap, NE03's chat window) break loops in proportion to how much own text it removes?
- **H69-R3.** Memory as the residual carrier: are post-erasure restatements of erased statements the ones written into memory at the consolidation (`memory_stats`)?
