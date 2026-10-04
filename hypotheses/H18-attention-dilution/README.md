# H18: Attention dilutes as 1/k: response to a message falls with the number of messages waiting at the agent's turn

**Status:** running. Exploratory round 1 done (2026-10-03; 16 non-holdout goal periods; predictions written before any real-data run).
- **Dilution is real, everywhere, and sub-linear.** Within agent-days, the chance that a talk turn addresses a given pending sender falls as ≈ k^−0.6: β̂ > 0 in 16/16 periods, pooled 0.63 ± 0.02 (regime I 0.55, regime III 0.69). It is a saturating curve, ∝ 1/(k₀ + k) with k₀ ≈ 2–8, **not a literal 1/k budget**. Recency (newest messages first) explains as much in about half the periods.
- **Not only a turn-timing artifact in #51.** In #51, timer-wake batches (exogenous k) give β̂_D2 = 0.50 [0.45, 0.56]. In the small two-room-era periods D2 is weak or contradictory.
- **Across periods the per-turn budget is roughly conserved while per-pair uptake falls with room size.** p̄ vs. N_room: ρ = −0.55 (#51 segments: −0.87); B̂ vs. N_room: ρ = −0.03. This is the J ∝ N^−β normalization behind H03's falling per-pair triggering and part of H05's within-room rise.
- **Failed:** literal 1/k (P2); mention bypass (P4); the 05-04 merge (P7); the room-size contrast in half the two-room periods (P6); and the invisible-message placebo (P10) everywhere. Mentions partly mark ongoing exchanges, not responses to a specific message.
- Per-period verdicts: 3 supported, 13 mixed, 0 failed. Not promoted.
- **Round 1b (2026-10-04, improved data; section "Round 1b" below):** on context-ledger pending sets (`k_since_talk`) the exponent is unchanged (pooled **0.66 ± 0.02**, 16/16), the shape is still saturating or recency-led, and the placebo failure mostly goes away (invisible senders addressed at 0.49× the pending rate, was 0.85×; 3/16 pass, was 0/16). On DQ2 reply labels the exponent rises to 0.85 and recency wins 14/16, but a message has one reply parent, so that exponent has a budget built in. Verdicts (1b): 4 supported (G39 added), 12 mixed; natives NE42 failed, G51 N sweep mixed, NE03 failed. Scorecard G 0 → 1.
**Fields:** stat mech, sociophysics, dynamics
**Origin:** HH99 (`../hypohypotheses/HYPOHYPOTHESES.md`; `../promotion-shortlist.md`)
**Definitions used:** Regime; Population N(t); Action; Interaction, variant *addressed* (i's message names j, from `chat_mentions_clean.mentions_roster`). New operational terms are defined under "Operational definitions" below and proposed for DEFINITIONS.md as **"talk turn"**, **"pending set (talk-turn backlog)"** and **"Interaction (addressed, pending-sender)"**.

## Standards (2026-10-04)
**Question served:** Q1 (an attention budget: per-pair uptake falls with room size).

| Impostor | Relevant? | How it was handled | Status |
| --- | --- | --- | --- |
| Scheduler field | partly | Endogenous turn timing is the strongest null; D2 uses timer wakes as exogenous k (Null / baseline). D2 is convincing only in #51. | partly |
| Exogenous field (kickoff/goal/operator) | partly | Agent×day propensities absorb day-level fields (M_const null). | removed |
| Shared model priors | no | Within agent-day design. | n/a |
| Contemporaneous convergence | yes | Ledger-strict invisible placebo: invisible senders are addressed at 0.49× the pending rate (3/16 pass); the residual is conversation state (Round 1b, P10). | partly |

**Inputs:** round 1b uses the context ledger (`k_since_talk`, `call_windows`) and DQ2 reply pairs. Activity, embeddings and failures do not apply. P11 (content reply) was not re-run.

**Two layers:** 15 replication folders. Natives: 3 (NE42 failed, G51 N sweep mixed, NE03 failed).

**Confirm script:** `confirm_holdout.py` (C1–C6), written, not run. Re-freeze: yes; it still builds round-1 inputs (call-start rule) and must switch to the ledger (holdout item 10).

## Question
When an agent takes its next turn, it faces k unread messages. Does the probability of responding to a given one fall as ~1/k (a fixed attention budget), making the mean-field J/N normalization literal? Does this micro-mechanism explain H03's finding that per-pair triggering and the branching ratio fall with N, and H05's rise in within-room coupling after the split (HH90)? Practical payoff: how coupling scales with swarm size and channel design.

## Model
**From:** `physics-models/01-inverse-ising` (mean-field J/N), `09-hawkes` (cross-excitation per pair), `02-nonequilibrium-ising`. Rival models: constant per-message response (no budget), saturating response, and recency-only (only the latest message matters).

**Uptake model (H18 variant, written 2026-10-03).** At talk turn τ of recipient i on day d, each pending message m is "taken up" independently with hazard λ_m = θ_{i,d} · h_m. Sender j is addressed iff at least one of its pending messages is taken up:

P(r_{τj} = 1) = 1 − exp(−θ_{i,d} · Σ_{m ∈ P_j(τ)} h_m)

(complementary log-log link; a noisy-OR over j's messages, so a sender with several pending messages is not counted several times). θ_{i,d} is an agent×day propensity (ridge-penalized log θ toward the period mean, σ = 1.5), which absorbs busy days, agent style and day-level goal state: **the k-dependence is identified only from variation in k within an agent-day.** The families differ only in h:

| Model | h_m | Reading |
| --- | --- | --- |
| M_const | 1 | no budget: each message has its own fixed chance |
| **M_inv** | 1/k | fixed budget: total uptake per turn ≈ θ, independent of k (the literal J/N) |
| M_sat | (1 + k₀)/(k₀ + k), k₀ ≥ 0 | saturating total uptake θ·k(1+k₀)/(k₀+k); nests const (k₀ → ∞) and inv (k₀ → 0) |
| M_rec | ρ^{rank_m − 1}, 0 < ρ ≤ 1 | recency-only: depends on position from the newest (rank 1), not on k |
| M_pow (summary) | k^{−β} | β = 1 fixed budget, β = 0 constant; the per-period exponent β̂ is the headline number |
| M_recbud (secondary) | ρ^{rank−1}/Σ_{s=1..k} ρ^{s−1} | a budget allocated by recency; ρ → 1 gives M_inv |

Every family also carries a mention factor e^{γ·1[m @-mentions i]}; the bypass variant gives mention messages their own exponent (h = e^γ k^{−β_M}).

Mean-field link: if each agent has a fixed budget B per turn and k ≈ (N_room − 1)·(messages per agent per turn interval), the per-pair coupling is J_ij ∝ B/(N_room − 1) and the row sum Σ_j J_ij ≈ B is conserved across cuts and merges (HH90).

## Data scheme (`scheme/`)
Shared tables in `data/processed/shared/` (see `infra/README.md`). Use `chat_mentions_clean.parquet`, not `chat_core.mentions`. `exposure` (msg → recipient, lag to the recipient's next turn), `chat_core` + `chat_mentions_clean`, `actions` and `events_core` (turn times), `rooms_timeline`. Response = the recipient's next message addresses the sender or replies to the message's content; define it from mentions and, optionally, embedding similarity (`data/processed/shared/embeddings/`).
- **Script:** `scheme/build.py` (one pass, all target periods; holdout days are dropped with `calendar.holdout` and `common.holdout_mask` before anything is computed).
- **Output:** `data/processed/H18-attention-dilution/` (one subfolder per goal period, `G<NN>/`), with `_provenance.json`:
  - `talks.parquet`: one row per talk turn (agent, day, time, call start, gap, k, k_agent, k_s, room size, after-pause flag, number of mentions);
  - `pending.parquet`: one row per (talk, pending message): sender kind and code, rank from newest, whether it mentions i, whether the talk mentions the sender (response), content cosine (secondary);
  - `wakes.parquet` / `wake_pending.parquet`: the regime-III timer-wake design (D2);
  - no text anywhere.

### Operational definitions (written 2026-10-03, before any real-data run)
- **Talk turn τ of i:** an `AGENT_TALK` event (a `chat_core` row with speaker_kind = agent, agent = i).
- **Call start s(τ):** the latest logged turn of i (any `actions` row except the `pause` mirrors, or any `events_core` event of i) strictly earlier than t_τ − 1 s. The `send_message_back_to_chat` action logged ~0.06 s before each regime-III `AGENT_TALK` is the same model call, hence the 1 s guard. The scaffold shows each call the events that arrived since the previous call ("unseen events"), so a message m is visible to the call producing τ iff t_m < s(τ).
- **Pending set P(τ) (D1, "talk-turn backlog"):** messages by anyone other than i (agent, human, automated) that were in i's room when posted (`exposure` rows for recipient i) with s(τ_prev) ≤ t_m < s(τ), τ_prev = i's previous talk turn on the same PT day. Each agent's first talk turn of a day is excluded (its window spans the overnight gap and the morning consolidation).
- **k(τ) = |P(τ)|** (all speaker kinds; they all occupy context). Variants: k_agent (agent messages only), k_s (distinct agent senders). n_j = j's messages in P(τ); rank_m = position from the newest (1 = the last message before s(τ)).
- **Response (primary): "addressed (mention-based)".** r_{τj} = 1 iff τ's `mentions_roster` contains j. Scored units: (τ, j) for every agent sender j in P(τ) whose name the mention parser can detect (not the Claude Code agent, not "[Temporary]" agents). Human and automated messages count in k but are not scored.
- **Response (secondary): "content reply".** cos(e_τ, e_m) of the bge-small embeddings above θ_c, the 95th percentile of a per-period null in which τ is replaced by a talk turn of the same agent on a different day of the same period. Reported as the excess over the null rate, per k bin.
- **"Acts on it"** (action-based responses) is not used in round 1.
- **D2, timer-wake batches (regime III only; the identification design).** H09 showed a regime-III PAUSE is a timer that room messages do not interrupt (0.22% early wakes). For each PAUSE of i that ends at its timer (wake at i's next turn, ≥ declared expiry − 30 s), the **batch** is the messages posted in i's room from the start of the call that issued the PAUSE to the expiry. Its size k_w is fixed by a duration the agent chose before the messages arrived, so it is exogenous to their content. Response: i's first talk turn after the wake and before its next PAUSE (same day) mentions j; r = 0 if i does not talk in that stint. Sensitivity: first talk within 5 min of the wake.
- **Room size N_room:** agents (roster, not the Claude Code agent) in i's room at t_τ, from `rooms_timeline`.

## Candidate goal periods
Regime III non-holdout (#35–#44), #51 non-holdout days (N varies with roster changes), regime I for contrast. Room events (NE15, 05-04 merge) as spanning tests.

**Chosen (2026-10-03, before data):**
- **Two-room era (rooms split 03-16):** #35, #36 (regime II, then III from 03-24), #37, #38, #39, #40 (merged room, except GPT-5), #41, #42, #44. #43 is held out.
- **#51** non-holdout days (07-06 → 09-04), with segments at roster changes (N 21 → 29) as a within-period size gradient.
- **Regime I contrast:** #24, #25, #26, #27, #30, #31: all after NE09 (2025-12-20, "chat interleaved into computer-use context"), so the visibility rule is the same as later; all in #general with N ≈ 10–12. Earlier regime-I periods are excluded because before NE09 chat may not have been visible during computer sessions, which would break the call-start visibility rule.
- **Spanning tests:** NE15 (only the post-split side is non-holdout, so exploration uses the same-day small-room vs large-room contrast inside #35; the before/after comparison is confirmatory) and the 05-04 merge / 05-11 split (#39 → #40 → #41, an A-B-A; it has no NE ID yet, folder `NE42/`).

## Links to other hypotheses
H03 (per-pair triggering falls with N), H05 (J_in rose after the split; HH90), H04 (delayed, context-mediated response), H08 (context is the coupling).

## Observables
*Written 2026-10-03, before any real-data run. All fits are within one goal period (agent×day propensities); periods are compared only through their fitted parameters.*
1. **P(r | k) curves:** the binned addressing rate per pending sender, for senders with exactly one pending message (n_j = 1), in bins k ∈ {1, 2, 3–4, 5–8, 9–16, 17–32, 33–64, ≥65}; day-bootstrap CIs.
2. **β̂ (M_pow exponent)** with agent×day propensities, per period and per segment; day-level bootstrap CI (B = 200; 100 for #51).
3. **Model comparison:** held-out log-likelihood per scored unit of M_const, M_inv, M_sat, M_rec (primary set) and M_pow, M_recbud (secondary). **Primary CV: within-day blocks** (each day's talk turns split into 4 contiguous time blocks; fold f holds out block f of every day, so the agent×day propensity is learned from the same day). Secondary CV: day-blocked folds with agent-level propensities. Day-level paired bootstrap of the differences.
4. **Σ ≈ const (HH90 mechanism):** S(τ) = number of distinct pending senders addressed by τ; its within-agent-day elasticity ε_S = d log E[S]/d log k (Poisson regression of S on log k with agent×day effects), and binned S(k). Under M_inv ε_S ≈ 0, under M_const ε_S ≈ 1 until senders saturate.
5. **Mention bypass:** e^γ (uptake ratio for messages that @-mention i) and β_M vs. β_other in the bypass variant.
6. **D2 wake design (regime III):** β̂_D2, the same model ladder, and the D2 vs. D1 comparison.
7. **Room size:** per-pair uptake and k̄ in the small vs. large room on the same days (agent and day effects; the agent×day propensity would absorb room); the room coefficient with and without k in the model.
8. **Per-period summary parameters for the cross-period comparison:** p̄ (mean per-pair addressing rate), B̂ = mean predicted S per talk turn at the period's median k, β̂, k̄, N, N_room. Compared across periods (Spearman with N) and across #51 segments.
9. **Placebo (ground truth for the visibility rule):** the addressing rate for messages that arrived during τ's own model call (t_m ∈ [s(τ), t_τ), invisible to τ) must sit at the rate of mentioning non-pending agents, not at the pending rate.
10. **Content reply (secondary):** excess content-reply rate per pending message vs. k.

## Null / baseline
*Written 2026-10-03, before any real-data run.*
- **No budget (M_const)** with the same agent×day propensities and mention factor: uptake independent of k.
- **Recency-only (M_rec):** only position in the queue matters; at fixed rank, k is irrelevant.
- **Strongest null: endogenous turn timing.** If replies are *triggered* (a message from j makes i talk soon, addressing j), the reply itself creates small k, and P(r | k) falls with k even with no budget. This null is simulated at village sampling (synthetic "reactive-constant" agents) to measure the spurious β it produces in D1. D2 (timer wakes, exogenous k) is the design that should not be fooled; a D1 slope without a D2 slope is read as timing, not dilution.
- **Sender saturation:** with at most N_room − 1 senders, a per-message analysis that ignores multiple messages from one sender flattens P(r | k) at large k; the noisy-OR handles this and the synthetic check quantifies it.
- **Room-blind k:** counting messages from other rooms in k (a room-blind exposure) dilutes spuriously; checked synthetically.
- **Invisible-message placebo** (Observable 9).

## Faithfulness scorecard
Scored per model, mapping and window; 0 = not done or failed, 1 = partial, 2 = passed. Scheme and promotion thresholds: `writeup/paper.tex`, Sec. "Assessing model faithfulness".
**Rival models:** M_const (no budget), M_rec (recency-only), M_sat (saturating), and the reactive-timing null (endogenous turn timing, simulated).
**Locked holdout used for confirmation:** none yet. `analysis/confirm_holdout.py` (C1–C6) is written and dry-run on stand-ins only. Targets: #51 tail, #45–#47, #49, #50, #28, #29, and the NE15 pre-split days (#34, 03-09 → 03-13).

Scores for round 1 (exploratory, non-holdout; mapping = mention-addressed responses at talk turns, D1; timer wakes, D2).

| Axis | Test | Score | Evidence |
| --- | --- | --- | --- |
| A mapping | variables defined from dataset fields; assumptions listed; invariant across families and regimes | 1 | Talk turns, call starts, pending sets and responses all come from shared tables; assumptions are listed in the card. Not invariant: the call-start visibility rule is doubtful in regime I (placebo), and the mention proxy mixes responses with ongoing exchanges. |
| B assumptions | stationarity, Markov order, time-rescaling, update-order audit | 1 | **Turn timing:** endogenous turn timing is the main threat (synthetic: β̂_D1 ≈ 0.78 with no budget). The exogenous-k design D2 excludes it in #51 only (0.50 [0.45, 0.56]). D2 is underpowered or contradictory in the small periods (G38 −0.13). **Engagement:** controlled post hoc; β̂ unchanged in regime III. **Stationarity:** within-period heterogeneity large (#51 segments I² = 0.99). |
| C adequacy | beats the null hierarchy, day-blocked held-out data | 1 | The best k-dependent model beats M_const on within-day-block held-out data in 16/16 periods (CI excl. 0); day-blocked CV agrees in 15/16. It does not beat recency-only in 5/16, and the timing null is excluded only in #51. |
| D unfitted predictions | unfitted statistics and the model's signature | 1 | **Passed:** P9 (cross-period p̄ falls with N while B̂ does not); G35's same-day room ratio (p̄ ratio 2.05 vs. 3.6^0.75 ≈ 2.6 predicted from β̂). **Partial:** content-reply excess falls with k in 11/11 periods with signal, but more shallowly (slopes −0.16 to −0.44). **Failed:** P6 in half the two-room periods. |
| E interventional | predicts the change across a natural experiment | 1 | **NE15 side (#35):** k absorbs the small-room uptake advantage (log effect 0.95 → −0.14). **Merge 05-04:** failed (k̄ ×1.45, per-pair uptake not down on both sides; goal-confounded). No holdout used. |
| F identifiability | synthetic recovery with village sampling; robust to preprocessing | 1 | **Recovery:** β̂ recovered without bias at village sampling (1/k → 1.00 ± 0.03, constant → 0.00 ± 0.04, k^−0.5 → 0.50), and the model family is selected correctly under exogenous timing. **Not identified in D1:** under reactive timing D1 confuses no budget with dilution, and recency truth also gives β̂ ≈ 0.85. D2 is unbiased but attenuated (≈ 0.6×) and noisy. Room-blind k and talk-time windows bias β̂ down (quantified). |
| G ground truth | agrees with known structure | 1 | **Round 1b (2026-10-04): 0 → 1.** On strict context-ledger visibility the placebo passes in 3/16 and invisible senders are addressed at 0.49× the pending rate (was 0.85×); the residual 1.8× over non-pending room-mates is conversation state (H08), and DQ2's reply labels show the same thread-membership component. Round 1: **The invisible-message placebo fails in 16/16.** Senders whose messages arrived during the talk's own model call are mentioned 3–10× above other room-mates even when not engaged, and in regime I and #51 above pending senders. The response proxy is contaminated. |
| H comparative | beats the named rivals | 1 | **Shape:** a near-literal budget is best in 5/16, saturating in 6, recency-only in 5, constant in 0. 1/k never beats recency-only (CI); recency beats 1/k in 8/16. **Post hoc:** k adds held-out value at fixed rank in 5/16. |
| I transfer | holds in other same-mode periods, including the holdout | 1 | β̂ > 0 in every period, mode and regime (0.46–0.78). The shape and the magnitude are heterogeneous (I² = 0.92). No holdout run. |

## Prediction
*Written 2026-10-03, before running on real data. Only schemas, the CHANGELOG, H09's pause findings and the event order of one regime-I day and one regime-III agent-day (to understand how turns and talk events are logged) were looked at; no k distribution and no response rate.*

Scored per period on D1 (primary) unless stated; "periods" means the 16 chosen periods with ≥ 300 scored units.

| # | Prediction | Counts against |
| --- | --- | --- |
| P1 | **Dilution exists.** β̂ > 0 with the 95% CI excluding 0 in ≥ 70% of periods; random-effects pooled β̂ (reported next to the per-period values) in [0.5, 1.2] | β̂ CI includes 0 in > 30% of periods, or pooled β̂ < 0.3 |
| P2 | **Shape: a budget, not a constant or recency.** M_inv or M_sat has the best held-out (within-day block) log-likelihood among M_const, M_inv, M_sat, M_rec in ≥ 70% of periods; where M_sat wins, k̂₀ < 3 in most periods | M_const or M_rec best in > 30% of periods |
| P2b | Within a turn, newer messages are favored (ρ̂ < 1 in M_recbud), but at fixed rank k still matters: M_recbud beats M_rec in ≥ 70% of periods | M_rec ≥ M_recbud in most periods |
| P3 | **Σ ≈ const (HH90).** ε_S ∈ [−0.2, 0.5] in most periods (pooled CI inside it), and binned S at k ≥ 17 is within ×1.5 of S at k = 3–8 | ε_S ≥ 0.7 (S ∝ k: no budget) |
| P4 | **Mentions bypass dilution.** e^γ ≥ 3, and β_M < β_other − 0.3 (pooled; per period where ≥ 100 mention units) | β_M ≥ β_other |
| P5 | **Not a timing artifact (D2, regime III).** β̂_D2 > 0 with CI excluding 0 in ≥ 50% of regime-III periods with ≥ 200 D2 units; pooled β̂_D2 within ±0.4 of pooled β̂_D1 (regime III) | pooled β̂_D2 < 0.2 with CI including 0 while β̂_D1 > 0.5 → the D1 slope is turn timing, and P1 fails as a mechanism claim |
| P6 | **Room size (NE15 / #35; two-room days of #37–#44).** On the same days, per-pair uptake is higher in the smaller room, with p̄_small/p̄_large within ×2 of k̄_large/k̄_small; the room coefficient shrinks toward 0 (CI includes 0) once k enters the model | the room effect survives k, or the small room has *lower* uptake |
| P7 | **Merge 05-04 (#39 → #40 → #41).** k̄ rises in #40 for the merged agents, per-pair uptake falls in #40 relative to both #39 and #41, and S per talk turn changes by < 30%. Direction only (goal changes coincide with both boundaries) | uptake does not fall in #40 in both comparisons |
| P8 | **Regime invariance.** Pooled β̂ in regime I (#24–#31 non-holdout) within ±0.3 of pooled regime III | \|Δβ\| > 0.3 with non-overlapping CIs |
| P9 | **Cross-period link to H03 / HH90.** Across periods (each a point), p̄ falls with N (Spearman ρ < −0.5) while B̂ does not (\|ρ\| < 0.3), and CV(B̂) < CV(p̄). In #51 segments (N 21 → 29), p̄ falls and B̂ is flat | B̂ falls with N as steeply as p̄ (no conservation) |
| P10 | **Placebo.** Addressing rate for invisible (same-call) messages ≤ 1.5× the rate of mentioning non-pending agents, and ≤ 1/2 the pending rate at the same k | invisible messages addressed at the pending rate → mentions are not responses, or the visibility rule is wrong |
| P11 (secondary) | Content-reply excess per pending message falls with k with a log-log slope within ±0.4 of −β̂ | slope ≈ 0 |
| G1 | **Synthetic guard** (village sampling: real message times, rooms, talk times of a non-holdout period; synthetic responses). Fixed-budget truth → β̂ within ±0.15 of 1 and M_inv or M_sat selected in ≥ 80% of runs; constant truth → β̂ within ±0.15 of 0 and M_const selected; recency truth → M_rec selected. Reactive-constant agents (endogenous timing): report D1's spurious β̂; D2 must return β̂ within ±0.15 of 0 | guard fails → real-data β̂ uninterpretable for that design |

Prior credences (Claude, 2026-10-03): P1 0.65, P2 0.5, P3 0.4, P4 0.6, P5 0.4, P6 0.5, P7 0.4, P8 0.35, P9 0.45, P10 0.75.

## Synthetic validation (axis F; run 2026-10-03 before any real-data fit)
`analysis/synthetic.py`; outputs in `data/processed/H18-attention-dilution/synthetic/` (`A.parquet`, `B.parquet`, and two simulated periods, `SIMinv/` and `SIMrc/`, run through the full `fit_periods.py` pipeline).

**A. Known rules on real village skeletons** (real talk turns, pending sets, ranks, mention flags and agent-days of G25, G38, G41 and 12 days of G51; synthetic responses only; mean rate 0.15; 8 reps per rule and period, 4 of them with CV).

| Truth | β̂ (mean ± sd across reps, 4 periods) | Within-day-block CV winner (16 runs) |
| --- | --- | --- |
| constant | −0.003 to 0.001 ± 0.015–0.048 | const 7, sat 5, rec 4: all are the constant model at their limits (k₀ → ∞, ρ → 1); hence amendment A2 |
| 1/k | 0.99–1.02 ± 0.01–0.04 | inv 13, sat 3 (k₀ → 0): **100% budget-like** |
| k^−0.5 | 0.48–0.52 ± 0.01–0.04 | sat 16 |
| saturating, k₀ = 3 | 0.58–0.75 | sat 16 |
| recency-only, ρ = 0.5 | **0.81–0.94** | rec 16 |

β̂ is recovered without bias at village sampling. But **β̂ alone does not tell a budget from recency**: a recency-only rule gives β̂ ≈ 0.8–0.9. The discriminating statistic is the M_inv vs. M_rec held-out comparison.

**B. Generative agents** (13 agents in rooms of 3 + 10; 4 h days × 10; model calls with 4–12 s latency; timer pauses; ~14–19 talk turns per agent-day, median k ≈ 10, as in the real two-room era; 8 reps each). β̂ by design:

| Scenario | D1 β̂ | D1 best | D2 β̂, 60 s window | D2, 300 s | D2, whole stint |
| --- | --- | --- | --- | --- | --- |
| exogenous timing, 1/k | 0.97 ± 0.04 | inv (7/8) | too few responses | 0.63 | 0.52 |
| exogenous, constant | −0.03 ± 0.04 | const (7/8) | 0.06 ± 0.46 | 0.09 | 0.12 |
| exogenous, saturating k₀ = 3 | 0.67 | sat (8/8) | 0.45 | 0.29 | 0.30 |
| exogenous, recency ρ = 0.5 | 0.94 | rec (8/8) | 0.85 | 0.73 | 0.62 |
| **reactive timing, constant (strongest null)** | **0.78 ± 0.02** | **rec (8/8)** | −0.08 ± 0.19 | **−0.00** | 0.06 |
| reactive timing, 1/k | 1.63 | inv/rec | 0.18 | 0.26 | 0.33 |
| exogenous 1/k, **room-blind k** | 0.80 | | | | |
| exogenous 1/k, **naive window** (talk times, not call starts) | 0.46 | | | | |

Readings:
- **Endogenous turn timing fakes dilution in D1** (β̂ ≈ 0.8 with no budget at all), with a recency signature (M_rec wins). The talk-turn backlog alone cannot establish the mechanism; P2's M_inv-vs-M_rec comparison and D2 are what discriminate.
- **D2 (timer wakes) is not fooled** (≈ 0 under reactive-constant agents). But it is **attenuated** when the true budget runs over the whole unanswered backlog (≈ 0.6 × β), and noisy at village sampling (sd 0.2–0.45 per 10-day run).
- Room-blind k and the naive window boundary both bias β̂ down (0.97 → 0.80 and → 0.46), so room-aware exposure and call starts matter.
- **Full-pipeline dry runs:**
  - `SIMinv`: β̂ = 1.02 [0.96, 1.07]; CV winner sat with k₀ → 0; ε_S = 0.01; invisible placebo 0; room effect 0.95 → −0.15 once k is in the model.
  - `SIMrc` (reactive-constant): β̂_D1 = 0.80, M_rec beats M_inv, β̂_D2 = −0.09 [−0.27, 0.08]. Its verdict under the per-period rule is *mixed*, not supported.
  - ε_S was 0.21 there, inside P3's band: **P3 is not diagnostic on its own.**
- **G1 guard:**
  - passes for the 1/k, power, saturating and recency truths;
  - for constant truth it passes for β̂ and passes for selection only with the effective-winner rule (A2);
  - D2 passes the reactive null.

## Amendments (2026-10-03, after the synthetic validation, before any real-data fit)
- **A1 · D2 response window.** Primary: i's first talk turn within **300 s** of the wake (r = 0 otherwise). 60 s and whole-stint are sensitivity variants. Reasons:
  - at village sampling, the 60 s window leaves ~1% responses;
  - the whole-stint version is more attenuated and picks up some timing bias.
- **A2 · Effective winner for P2.**
  - An M_sat win with k̂₀ ≥ the period's 90th-percentile k is scored as constant-like, and one with k̂₀ < 3 as budget-like.
  - An M_rec win with ρ̂^(k_q90 − 1) ≥ 0.5 (recency weights flat over the data) is scored as constant-like.
  - P2 counts "M_inv, or M_sat budget-like / intermediate" as a budget win.
- **A3 · Rejected variant (recorded, not used).** D2 with the whole backlog at the wake call as k (units still the batch messages) was biased to β̂ ≈ −0.5 under constant truth: a sender's pre-pause messages can earn the mention. D2 keeps the batch size as k.
- **A4 · Reading of P1.** Because reactive timing and recency both produce β̂ ≈ 0.8, a period counts as *supported* only with P2 (budget beats M_rec) and no D2 contradiction; this was already the verdict rule. P5's ±0.4 tolerance stands, given D2's attenuation under a true backlog budget.

## Results by goal period
*Exploratory, non-holdout. D1 = talk-turn backlog (primary). β̂: M_pow exponent with agent×day propensities, day-bootstrap 95% CI. CV: within-day-block held-out winner among M_const, M_inv, M_sat, M_rec, with the effective label of amendment A2 ("sat" = saturating, 3 ≤ k̂₀ < k_q90; "sat~inv" = k̂₀ < 3). Δℓ inv−rec is the held-out log-likelihood per unit ×10³ (negative = recency-only better). D2 = timer wakes, 300 s window. Verdict rule as fixed in each G card: supported needs P1, P2 (literal-budget-like: M_inv, or M_sat with k̂₀ < 3) and no D2 contradiction.*

| G | regime · mode | days | N_room | k med / mean | units (rate) | β̂ [95% CI] | CV best (effective) | Δℓ inv−rec ×10³ | ε_S | e^γ | β̂_D2 [CI] (units, resp.) | verdict |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| [G24](goalperiod-subhypotheses/G24/README.md) | I · C | 5 | 10.0 | 7 / 10.0 | 5718 (0.090) | 0.56 [0.52, 0.66] | sat (sat) | -7.6 | 0.38 | 4.5 | — | mixed |
| [G25](goalperiod-subhypotheses/G25/README.md) | I · C | 5 | 10.0 | 4 / 9.3 | 8211 (0.211) | 0.59 [0.56, 0.62] | sat (sat) | -9.3 | 0.42 | 1.3 | — | mixed |
| [G26](goalperiod-subhypotheses/G26/README.md) | I · C | 5 | 10.0 | 4 / 9.4 | 7201 (0.205) | 0.50 [0.44, 0.53] | sat (sat) | -22.9 | 0.49 | 1.1 | — | mixed |
| [G27](goalperiod-subhypotheses/G27/README.md) | I · K | 10 | 10.0 | 6 / 10.1 | 13743 (0.116) | 0.69 [0.56, 0.80] | sat (sat~inv) | -0.6 | 0.33 | 1.2 | — | supported |
| [G30](goalperiod-subhypotheses/G30/README.md) | I · C | 5 | 11.0 | 7 / 12.7 | 9196 (0.131) | 0.55 [0.52, 0.58] | rec (rec) | -18.8 | 0.44 | 0.8 | — | mixed |
| [G31](goalperiod-subhypotheses/G31/README.md) | I · F | 5 | 11.2 | 8 / 13.1 | 11946 (0.144) | 0.46 [0.41, 0.50] | rec (rec) | -23.2 | 0.50 | 1.7 | — | mixed |
| [G35](goalperiod-subhypotheses/G35/README.md) | II · C | 5 | 7.3 | 4 / 7.7 | 5568 (0.161) | 0.75 [0.63, 0.82] | rec (rec) | -12.1 | 0.25 | 1.1 | — | mixed |
| [G36](goalperiod-subhypotheses/G36/README.md) | II/III · C | 5 | 6.3 | 3 / 5.7 | 2842 (0.262) | 0.78 [0.74, 0.82] | sat (sat~inv) | 1.7 | 0.22 | 2.2 | underpowered (40, 8) | supported |
| [G37](goalperiod-subhypotheses/G37/README.md) | III · F | 3 | 6.9 | 2 / 5.0 | 937 (0.393) | 0.75 [0.52, 0.98] | rec (rec) | -28.9 | 0.19 | 2.1 | 0.79 [0.71, 0.86] (301, 47) | mixed |
| [G38](goalperiod-subhypotheses/G38/README.md) | III · C | 17 | 6.4 | 3 / 5.3 | 6806 (0.194) | 0.69 [0.62, 0.80] | sat (sat~inv) | -5.6 | 0.29 | 2.4 | -0.13 [-0.41, 0.03] (1335, 89) | mixed |
| [G39](goalperiod-subhypotheses/G39/README.md) | III · I | 5 | 10.0 | 4 / 7.6 | 2280 (0.091) | 0.62 [0.45, 0.78] | sat (sat) | -4.4 | 0.34 | 3.5 | underpowered (0, 0) | mixed |
| [G40](goalperiod-subhypotheses/G40/README.md) | III · C | 5 | 14.0 | 6 / 11.0 | 7002 (0.117) | 0.60 [0.51, 0.71] | sat (sat) | -7.5 | 0.38 | 2.7 | 0.57 [-0.03, 1.81] (206, 13) | mixed |
| [G41](goalperiod-subhypotheses/G41/README.md) | III · I | 5 | 9.4 | 4 / 8.0 | 5976 (0.232) | 0.65 [0.55, 0.74] | sat (sat~inv) | -9.4 | 0.34 | 1.9 | 0.14 [-0.83, 0.62] (617, 113) | mixed |
| [G42](goalperiod-subhypotheses/G42/README.md) | III · I | 5 | 9.7 | 4 / 7.0 | 2744 (0.245) | 0.72 [0.69, 0.86] | rec (rec) | -17.1 | 0.17 | 5.2 | underpowered (125, 34) | mixed |
| [G44](goalperiod-subhypotheses/G44/README.md) | III · C | 4 | 10.5 | 4 / 7.6 | 4444 (0.276) | 0.72 [0.69, 0.76] | sat (sat~inv) | -7.2 | 0.23 | 3.3 | 0.31 [0.09, 0.58] (500, 55) | supported |
| [G51](goalperiod-subhypotheses/G51/README.md) | III · P | 45 | 23.7 | 7 / 19.9 | 195913 (0.102) | 0.61 [0.58, 0.63] | sat (sat) | -8.8 | 0.21 | 11.6 | 0.50 [0.45, 0.56] (129567, 3520) | mixed |

Verdicts: **3 supported (G27, G36, G44), 13 mixed, 0 failed.**
- Every period has dilution: β̂ > 0 with the CI excluding 0, and the k-dependent model beats the constant one on held-out data.
- What makes 13 of them *mixed*:
  - the shape is saturating rather than literal 1/k (G24–G26, G39, G40, G51);
  - recency-only wins (G30, G31, G35, G37, G42);
  - D2 contradicts D1 (G38, G41).
- Spanning tests:
  - [`NE15/`](goalperiod-subhypotheses/NE15/README.md): mixed (the #35 room effect is absorbed by k; replication 3 of 7 two-room periods);
  - [`NE42/`](goalperiod-subhypotheses/NE42/README.md): failed.

## Results
*All numbers: `data/processed/H18-attention-dilution/summary.json` (`analysis/summarize.py`), per-period `G<NN>/fits.json`, `spanning.json`, `posthoc_*.json`. Figures: `figures/summary.pdf` (one page), `figures/synthetic.pdf`, `G<NN>/figures/curves.pdf`, `NE15/figures/rooms.pdf`, `NE42/figures/merge.pdf`.*

### Outcome vs. prediction
| # | Prediction | Observed | Outcome |
| --- | --- | --- | --- |
| P1 | β̂ > 0 (CI) in ≥ 70% of periods; pooled β̂ in [0.5, 1.2] | **16/16**; pooled (DerSimonian–Laird, next to the per-period values) **0.63 ± 0.02**, I² = 0.92; median 0.64; regime I 0.55 ± 0.02, regime III 0.69 ± 0.03 | **supported** |
| P2 | M_inv or M_sat best in ≥ 70%; k̂₀ < 3 where M_sat wins | near-literal budget (M_inv / M_sat with k̂₀ < 3) **5/16**; saturating (k̂₀ 3–8) 6; recency-only 5; constant 0. k̂₀ < 3 in 5 of 11 M_sat wins. M_inv never beats M_rec (CI); M_rec beats M_inv in 8/16 | **not supported**: dilution is saturating, not a literal fixed budget |
| P2b | M_recbud beats M_rec in ≥ 70% | 2/16 | **not supported** (but see post hoc: k matters at fixed rank in 5/16) |
| P3 | ε_S ∈ [−0.2, 0.5] | pooled **0.32 ± 0.03**, 16/16 in band; S(k ≥ 17)/S(k = 3–8) within ×1.5 in 11/16 | **supported by the letter, uninformative**: reactive-constant synthetic agents also give 0.21. Total response grows as ≈ k^0.3, so it is not conserved within a period |
| P4 | e^γ ≥ 3 and β_M < β_other − 0.3 | pooled e^γ **2.2** (0.8–11.6); β_M − β_other = **−0.06 ± 0.07**. Passes only in **#51**: e^γ = 11.6, β_M 0.39 vs. β_other 0.81. e^γ ≥ 3 in 5/16; β_M < β_other − 0.3 in 1/16 | **not supported** (1/16). Being @-mentioned roughly doubles uptake, and is diluted just as much, except in #51 |
| P5 | D2: β̂_D2 > 0 (CI) in ≥ 50% of powered regime-III periods; pooled within ±0.4 of D1 | powered in 6. CI excl. 0 in 3: G37 0.79, G44 0.31, **G51 0.50 [0.45, 0.56]**. G38 −0.13 [−0.41, 0.03]; G40 0.57 [−0.03, 1.81]; G41 0.14. Pooled 0.37 ± 0.14 vs. D1 0.69 (Δ −0.31) | **supported by the letter; convincing only in #51.** #51's D2/D1 = 0.82 is above the synthetic attenuation (~0.6) under a true backlog budget. It is robust to the window (60 s 0.51, stint 0.50) and to engagement (0.48). Small-period batches are 1–2 messages, too little range |
| P6 | small room: higher uptake by ≈ the k̄ ratio; room effect gone once k is in | pass in G37, G41, G42 (effect absorbed, CI includes 0). G35 near-pass: k̄ ratio 3.6, p̄ ratio 2.05, log effect 0.95 → −0.14 [−0.19, −0.09]. Fail in G38 and G39 (the effect survives k) and in G36 and G44 (no small-room advantage) | **mixed (3–4/8)** |
| P7 | merge: k̄ up, per-pair uptake down vs. both #39 and #41, S within ±30% | k̄ ×1.48 / ×1.43 ✓. p̄: #39 0.091, **#40 0.117**, #41 0.237 ✗. S: 0.31 / 0.54 / 0.79 ✗. Within-side β̂ stable (0.58–0.65) | **not supported**: period-level uptake follows the goal, not k |
| P8 | \|β̂_I − β̂_III\| ≤ 0.3 | Δ = −0.14 ± 0.04 | **supported** (regime III dilutes somewhat more) |
| P9 | across periods p̄ falls with N (ρ < −0.5), B̂ does not (\|ρ\| < 0.3), CV(B̂) < CV(p̄); #51 segments likewise | ρ(p̄, N_room) = **−0.55** (p = 0.03); ρ(B̂, N_room) = **−0.03**; CV 0.24 vs. 0.43. #51 segments (N 21 → 31): ρ(p̄) = −0.87 (p = 0.001), ρ(B̂) = −0.38 (p = 0.28) | **supported** (the #51 B̂ part borderline) |
| P10 | invisible-message senders addressed ≤ 1.5× the non-pending rate and ≤ ½ the pending rate | **0/16** | **failed** (see post-hoc diagnostic) |
| P11 | content-reply excess slope within ±0.4 of −β̂ | 7/11 periods with signal. Slopes −0.16 to −0.44, all negative but shallower than −β̂. No signal in 5 (incl. #51) | **weak / partial** |
| G1 | synthetic guard | passes (constant-truth selection only with A2); D2 passes the reactive null | **passes** |

### Findings
1. **Attention dilutes sub-linearly.**
   - **Size of the effect:** within a recipient's day, addressing a pending sender falls from ≈ 0.34 at k = 1 to ≈ 0.03 at k ≈ 100 in #51 (`G51/figures/curves.pdf`).
   - **Exponent:** β̂ ≈ 0.46–0.78 in every period; the saturating form fits best overall.
   - **Mean-field reading:** per-pair coupling scales as J ∝ N^−β, with β ≈ 0.6. That is between "no normalization" (β = 0) and the literal J/N (β = 1).
2. **Recency and k are hard to separate where k is small; in #51 it is k.** In the post-hoc M_recsat (independent ρ and k₀):
   - k adds held-out value at fixed rank in 5/16 periods (G25, G26, G27, G30, **G51 with ρ̂ = 1.00, k̂₀ = 7**);
   - rank adds value at fixed k in 4/16;
   - in the small two-room periods (median k = 2–4) neither can be distinguished, and recency-only even wins in G37 and G42.
3. **Not just turn timing, at least in #51.** Timer-wake batches, whose size is set by a pause duration chosen before the messages arrived, dilute almost as steeply (0.50) as the backlog (0.61). The reactive-timing null predicts ≈ 0 there. In the smaller periods this test lacks range (batches of 1–2 messages) and once contradicts (G38).
4. **The budget per turn is conserved across periods but not within them.**
   - **Within a period** S grows ≈ k^0.32.
   - **Across periods** B̂ (0.3–0.8 senders addressed per talk turn) does not depend on room size (ρ = −0.03), while per-pair uptake falls from ≈ 0.15–0.4 in rooms of ~7 to ≈ 0.10 in #51's rooms of ~24 (ρ = −0.55). #51's roster growth reproduces this within one period (p̄: ρ = −0.87).
   - **The mechanism H03 and HH90 asked for:**
     - H03's per-pair triggering falls with N (ρ = −0.73);
     - after the 03-16 split, a k ratio of ≈ 3.6 predicts a per-pair rise of ≈ 2.2–2.6×; observed in #35: 2.05×.
     - H05's ~6× rise in within-room J is larger than dilution alone predicts, so other changes at the split contribute.
5. **Mentions are not a clean response signal.**
   - **Engagement:** whether i addressed j in its previous talk turn predicts mentions at 30–65%, whatever j's current status.
   - **Invisible messages:** even among non-engaged senders, those whose message the agent could not yet have seen are mentioned 3–10× above other room-mates (`placebo_diag.json`).
   - **Either:**
     - a common cause (several agents react to the same event and name each other);
     - or, in regime I, unlogged model calls that make the call-start rule wrong.
   - **What survives:** the k-slope survives an engagement control (post hoc, `posthoc_engagement.json`: regime III β̂ unchanged; regime I −0.01 to −0.06). But the absolute response rates should not be read as message-level uptake.
6. **Mentions bypass dilution only in #51.** Being @-mentioned roughly doubles the chance of being addressed back, but in 15/16 periods those messages are diluted as steeply as the rest (β_M ≈ β_other). The exception is #51 (private roles, the largest rooms): there a mention raises uptake ×11.6 and its slope is half the others' (0.39 vs. 0.81), i.e. a directed channel that partly escapes the crowd.
7. **Heterogeneity is large.**
   - Across periods: I² = 0.92 for β̂ and 0.97 for ε_S.
   - Inside #51: segment β̂ ranges from 0.49 to 1.11, I² = 0.99.
   - Read β̂ as a per-period parameter on a ~0.5–0.8 band, not a universal constant.

### Post-hoc analyses (not pre-registered; added 2026-10-03 after seeing results)
- `analysis/placebo_diag.py`: placebo stratified by engagement (finding 5).
- `analysis/posthoc_engagement.py`: M_pow_eng (engagement factor e^δ, δ̂ ≈ 0.4–1.5); β̂ on non-engaged units alone.
  - **Regime I (D1):** 0.56→0.50 (G24), 0.59→0.54, 0.50→0.46, 0.69→0.63, 0.55→0.52, 0.46→0.45.
  - **Regime III (D1):** unchanged within ±0.02 (e.g. G51 0.61→0.61, G38 0.69→0.70).
  - **D2:** G51 0.50→0.48, G38 −0.13→−0.25.
- `analysis/posthoc_recsat.py`: finding 2.
- Scoring note: the first summary pass counted intermediate-k̂₀ M_sat wins as budget-like. Before the cards were filled, this was corrected to the G cards' own wording ("if M_sat, k̂₀ < 3"). That turned 6 provisional *supported* verdicts into *mixed*.

### Caveats
- **Response proxy:** see the placebo failure. Mentions mix responses, ongoing exchanges and common-cause co-addressing. Responses to humans and the nudger are not scored.
- **Turn timing:** D1's slope is excluded as a timing artifact only where D2 has power (#51).
- **Recency vs. budget:** not separable in small-k periods.
- **Regime I visibility:** chat may reach the model through calls that are not logged; the call-start rule is doubtful there (placebo stronger in regime I).
- **Multiplicity:** 16 periods × 12 predictions, plus 3 post-hoc analyses. Per-period CIs are not multiplicity-adjusted. The headline (β̂ > 0 in 16/16, held-out wins in 16/16) would survive any correction; the borderline items (P6, P9's #51 B̂, the D2 small periods) would not.
- **Bootstrap size:** B = 200 (60 for #51; segment bootstraps 50 / 20).
- **The goal confound:** at the merge, and across periods.
- **Cross-period N:** the comparison is confounded with era. #51 is the only large-N period and the only 8 h one.
- **Content measure:** the content-reply measure has no signal in #51, where private roles make an agent's other-day messages a poor null.
- **Rooms:** the room-size contrast compares different agents (#best vs. #rest); agent effects are not removed.

### Figures (`figures/`)
- `summary.pdf`: one-page summary. Panels:
  - (a) observed/expected addressing vs. k under M_const with agent×day propensities;
  - (b) β̂ per period, D1 and D2, with pooled regime estimates;
  - (c) held-out Δℓ of 1/k vs. constant and vs. recency;
  - (d) senders addressed per talk turn vs. k;
  - (e) per-pair uptake vs. room size;
  - (f) per-turn budget vs. room size.
- `synthetic.pdf`: recovery on village skeletons (A); D1 vs. D2 under exogenous and reactive timing (B).
- Per period: `G<NN>/figures/curves.pdf`.
- Spanning: `NE15/figures/rooms.pdf`, `NE42/figures/merge.pdf`.

## Round 1b (improved data, 2026-10-04)
*Re-evaluation on the corrected shared tables (Vivian's priority 2; RE wave). Predictions and the per-period verdict rule are the pre-registered ones, unchanged. Round-1 outputs stay in `data/processed/H18-attention-dilution/G<NN>/`; round-1b outputs are in `.../r1b/`. Holdout untouched; `confirm_holdout.py` still builds round-1 inputs and must be switched to the ledger before any confirmatory run.*

### What changed
| Input | Round 1 | Round 1b |
| --- | --- | --- |
| talk turns, call starts | `AGENT_TALK` messages; call start = the agent's previous logged record | ledger talk calls (`call_windows`; message → call via its AGENT_TALK event, as DQ2) with `t_call` |
| pending set P(τ), k | room messages with s(τ_prev) ≤ t < s(τ) under the call-start rule (mislabels 65–70% of "invisible" messages: pauses, scheduled chat calls) | the ledger items of the recipient's calls since its previous talk call (= `context_ledger_turns.k_since_talk`; equal at 98% of talks) |
| response | @-mention of the sender | mention (pre-registered, kept for like-for-like comparison) **and** the DQ2 reply response: one of the sender's pending messages is the talk's `reply_pairs.parent` (`pair_set = cand`) |
| invisible placebo | messages during the talk's call under the call-start rule | strictly ledger-invisible messages (t_call ≤ t_m < t_talk); reply version from DQ2's labelled invisible pairs (`vis_uncertain` excluded), matched on naming × cosine decile |
| D2 timer wakes | PAUSEs ending at their timer, batch from the pause call | ledger calls with `gap_kind = pause` (not early wakes); batch = that call's items |
| code | `scheme/build.py`, `analysis/fit_periods.py` (unchanged default path) | `scheme/build_ledger.py`; `fit_periods.py --dir .../r1b --resp resp|resp_reply --tag …`; `r1b_placebo.py`, `r1b_native.py`, `r1b_summarize.py` |

### Old vs new, per period
β̂ = M_pow exponent with agent×day propensities (day bootstrap; B = 100, #51 40); CV = within-day-block effective winner; verdict by the G cards' rule (supported = β̂ CI > 0, budget-like winner, no D2 contradiction).

| G | regime | Round 1 β̂ · CV · verdict | **Ledger k, mention** β̂ · CV · verdict | Ledger k, reply parent β̂ · CV |
| --- | --- | --- | --- | --- |
| G24 | I | 0.56 [0.52, 0.66] · sat · mixed | 0.54 [0.48, 0.77] · sat · mixed | 0.72 [0.63, 0.86] · sat~inv |
| G25 | I | 0.59 [0.56, 0.62] · sat · mixed | 0.64 [0.62, 0.69] · sat · mixed | 0.75 [0.70, 0.80] · rec |
| G26 | I | 0.50 [0.44, 0.53] · sat · mixed | 0.56 [0.52, 0.58] · sat · mixed | 0.66 [0.60, 0.72] · rec |
| G27 | I | 0.69 [0.56, 0.80] · sat~inv · supported | 0.72 [0.61, 0.81] · sat~inv · supported | 0.78 [0.72, 0.84] · rec |
| G30 | I | 0.55 [0.52, 0.58] · rec · mixed | 0.65 [0.64, 0.67] · sat · mixed | 0.85 [0.80, 0.89] · rec |
| G31 | I | 0.46 [0.41, 0.50] · rec · mixed | 0.52 [0.44, 0.59] · rec · mixed | 0.74 [0.69, 0.78] · rec |
| G35 | II | 0.75 [0.63, 0.82] · rec · mixed | 0.77 [0.69, 0.82] · rec · mixed | 0.97 [0.85, 1.06] · rec |
| G36 | II/III | 0.78 [0.74, 0.82] · sat~inv · supported | 0.80 [0.76, 0.84] · sat~inv · supported | 1.08 [0.95, 1.23] · rec |
| G37 | III | 0.75 [0.52, 0.98] · rec · mixed | 0.72 [0.53, 0.91] · rec · mixed | 1.05 [1.00, 1.19] · inv |
| G38 | III | 0.69 [0.62, 0.80] · sat~inv · mixed (D2) | 0.69 [0.62, 0.80] · sat~inv · mixed (D2 −0.02) | 0.99 [0.94, 1.06] · rec |
| G39 | III | 0.62 [0.45, 0.78] · sat · mixed | 0.63 [0.47, 0.77] · sat~inv · **supported** | 1.00 [0.91, 1.15] · rec |
| G40 | III | 0.60 [0.51, 0.71] · sat · mixed | 0.60 [0.51, 0.73] · sat · mixed | 0.83 [0.77, 0.94] · rec |
| G41 | III | 0.65 [0.55, 0.74] · sat~inv · mixed (D2) | 0.65 [0.52, 0.76] · sat~inv · mixed (D2 0.14) | 0.91 [0.84, 0.99] · rec |
| G42 | III | 0.72 [0.69, 0.86] · rec · mixed | 0.72 [0.68, 0.90] · rec · mixed | 0.94 [0.85, 1.06] · rec |
| G44 | III | 0.72 [0.69, 0.76] · sat~inv · supported | 0.70 [0.68, 0.73] · sat~inv · supported | 0.78 [0.72, 0.86] · rec |
| G51 | III | 0.61 [0.58, 0.63] · sat · mixed | 0.61 [0.58, 0.62] · sat · mixed | 0.72 [0.69, 0.75] · rec |

### Predictions re-scored
| # | Round 1 | Round 1b (ledger k; mention unless stated) | Outcome (1b) |
| --- | --- | --- | --- |
| P1 β̂ > 0 in ≥ 70%; pooled in [0.5, 1.2] | 16/16; 0.63 ± 0.02 | 16/16; **0.66 ± 0.02** (I² 0.89); regime I 0.61, III 0.68. Replies: 16/16, 0.85 ± 0.03 | supported (unchanged) |
| P2 budget-like winner in ≥ 70% | 5/16 (sat 6, rec 5) | 6/16 (sat 6, rec 4). Replies: recency 14/16 | not supported (unchanged) |
| P3 ε_S ∈ [−0.2, 0.5] | 16/16 (uninformative) | 16/16 (0.16–0.45) | by the letter (unchanged) |
| P4 mention bypass | 1/16 | 1/16 (e^γ median 2.2; β_M − β median −0.11) | not supported |
| P5 D2 timer wakes | CI > 0 in 3/6 powered; G38 −0.13 | 3/6 (G37 0.77, G44 0.53, G51 0.45 [0.41, 0.50]); G38 −0.02 [−0.29, 0.19]. Replies: 5/6 (G38 0.55, G41 0.86, G51 0.62) | supported by the letter, #51 convincing (unchanged) |
| P6 room size absorbed by k | 3–4/8 | same pattern: absorbed in G35, G37, G41, G42; survives in G38, G39; no small-room advantage in G36, G44 | mixed (unchanged) |
| P7 05-04 merge | failed | NE42 native: k ×1.48/×1.44, raw p̄ not lower than #39; but in a joint fit k absorbs 86% (replies) / 53% (mentions) of the #40 contrast | failed (N2c new, positive) |
| P8 regime invariance | Δ −0.14 | Δ −0.07 | supported |
| P9 p̄ falls with N, B̂ does not | ρ −0.55 / −0.03 | ρ −0.57 / −0.02; CV 0.42 vs 0.25. #51 N sweep (native): p̄ ρ −0.73 (mentions), −0.80 (replies); B̂ ρ −0.28 (mentions), −0.64 (replies) | supported on mentions; on replies the per-turn budget falls too |
| P10 invisible placebo | 0/16; invisible ≈ 0.85× the pending rate, 3.4× non-pending | **3/16** (G31, G35, G38); invisible **0.49×** the pending rate, 1.8× non-pending. Replies (DQ2 labelled pairs): invisible/visible p_reply 0.80 (I), 0.58 (II), 0.72 (III); threshold 0.5 | **mostly explained by visibility; residual = conversation state** (still fails by the letter) |
| P11 content reply | 7/11 partial | not re-run (no content term in the ledger scheme) | — |

### Reading
- **The dilution law survives the visibility fix.** Re-counting k with the ledger changes it for 2–30% of talks (most in regime I) but moves the exponent by ≤ 0.1 in every period; pooled 0.63 → 0.66. The saturating shape and the recency competition are unchanged. Round 1's conclusions about the law stand; the regime-I values rise slightly (0.55 → 0.61) as the call-start rule's mislabelled windows are removed.
- **The placebo failure was mostly the visibility rule.** With strictly invisible messages, senders are addressed at about half their pending rate (round 1: 85%), and the remaining excess over non-pending room-mates (1.8×) is the mid-exchange effect H08 found. The reply labels say the same: invisible pairs keep 0.6–0.8 of a visible pair's reply score (DQ2: p_reply partly encodes thread membership).
- **Reply labels cannot measure the exponent as posed.** A talk message has at most one reply parent and DQ2 labelled mostly the top candidate, so β̂ on replies ≈ 1 − (elasticity of "replies to someone pending" in k). That elasticity is 0.0–0.1 in regime III and 0.1–0.35 in regime I (independent uptake would give ≈ 0.7), which looks like a fixed one-reply budget but is partly the labelling. What replies *do* show: **which** pending message gets the reply is decided by recency (M_rec wins 14/16).
- **Natives:** NE42 fails on raw rates but k explains the merged week's contrast in a joint fit; the #51 N sweep shows per-pair uptake falling with room size (ρ ≈ −0.8); NE03 shows no fetch-cap signature (uptake falls at every depth after 08-20).

### Scorecard changes (round 1b)
- **G 0 → 1:** the placebo now passes in 3/16 periods and the invisible/pending ratio halves under strict ledger visibility; the residual is explained (conversation state), not unexplained contamination.
- **A 1** (unchanged): k is now ledger-defined in every regime, but the mention response still mixes uptake and conversation state, and the reply response imposes a one-parent budget.
- **E 1** (unchanged): NE42's joint-fit contrast is absorbed by k, but the pre-registered raw comparison fails again.
- Others unchanged. Suggested ratings: faithfulness 2.0 → 2.5, usefulness 2.0 (meta.json).

## Confirmatory predictions (written 2026-10-03 after round 1, before any holdout use; `analysis/confirm_holdout.py`, not run)
Run only after this card and the script are committed and Vivian signs off. The script refuses without `--confirm --i-understand-this-uses-the-locked-holdout`; `--dry-run` uses non-holdout stand-ins.

Holdout reuse under the 2026-10-03 policy: H18's statistic (mention responses vs. the pending count) has not been computed on these days by anyone. Earlier uses, to be disclosed in both cards and LOG.md:
- #45: H02 (activity couplings);
- #46–#50: H04 (hours and Hawkes);
- NE15 pre-split: H05 (activity couplings).

| # | Prediction |
| --- | --- |
| C1 | #51 tail (09-07 → 09-21): β̂_D1 CI excludes 0 and β̂ ∈ [0.35, 0.85]; the effective CV winner is M_sat or M_rec (not M_const, not M_inv) |
| C2 | regime-III held-out periods #45, #46, #47, #49, #50: β̂ CI excludes 0 in ≥ 4 of 5; pooled β̂ ∈ [0.45, 0.95]; M_const never the effective winner |
| C3 | across those 6 holdout points, p̄ falls with N_room (Spearman ρ < 0) and CV(B̂) < CV(p̄) |
| C4 | regime-I held-out #28, #29: β̂ ∈ [0.3, 0.8] with CI excluding 0 in both |
| C5 | NE15 before/after (#34 pre-split days vs. #35, agents on both sides): #best agents' per-pair uptake rises (post/pre > 1); their S changes by < 50%; #rest agents change less |
| C6 | #51 tail timer wakes: β̂_D2 > 0 with the CI excluding 0 |

### Next steps
1. A cleaner response measure, to address the placebo failure:
   - reply threading via embedding similarity with a stricter, message-specific null;
   - or actions that cite a message's artifact.
   Then retest P10 and P2.
2. Fit M_recsat as a pre-registered model in round 2, and test recency vs. k on #51-like large-k data.
3. D2 with more range: pool the two-room era hierarchically (exception d); use the pause-duration distribution as an explicit instrument for k.
4. Map the inconsistent rooms (G38, G39) with agent fixed effects or agents who switch rooms.
5. Run the confirmatory script after sign-off.
6. Feed β̂ into H03 and H05 as the per-pair normalization J ∝ N^−β, and test whether it closes H03's n̂-vs-N trend.

## Notes
- **From H45 (2026-10-04):** a reply-based (DQ2 parent) dilution exponent on ledger backlog is β 0.82 pooled (regime I 0.73, regime III 0.98), correlating with this card's per-period β at ρ 0.71 but 0.28 steeper (DQ2 keeps one reply parent per message).
- **From DQ1 + DQ2 (2026-10-04): the failed placebo is mostly the visibility rule.** Under the context ledger, about 30% of this card's "invisible" pairs were in fact visible, and strictly invisible pairs score p_reply 0.24 vs 0.32 for matched visible pairs (0.21 vs 0.59 in regime III). The pre-registered threshold (< 0.227) missed narrowly (0.239). Re-run P10 and the k exponent on `context_ledger_turns.k_since_talk` and `reply_pairs.parent` in the re-evaluation wave.
- **From H29 (2026-10-04):** the call-start visibility rule labels messages that arrive during a PAUSE or long tool call as invisible, but the next call sees them (39–70% of regime-III invisible rows). Content similarity also falls 5–23× with message age. Together with H08's mid-exchange explanation, this accounts for the failed placebo. Re-run on the context ledger's visibility.
- 2026-10-03: promoted from HH99.
- 2026-10-03: observables, nulls, predictions and the choice of periods written before any real-data run.
- 2026-10-03: synthetic validation, then amendments A1–A4, before any real-data fit. Round-1 fits, post-hoc diagnostics and the confirmatory script (not run). Code map:
  - `scheme/build.py`: `assemble()` is shared by real and synthetic data;
  - `analysis/`:
    - `h18lib.py`: models, profile likelihood, CV, bootstrap;
    - `fit_periods.py --period G<NN>`;
    - `synthetic.py A|B`;
    - `spanning.py`, `summarize.py`, `summarize_lib.py`, `figures.py`, `write_period_cards.py`;
    - `placebo_diag.py`, `posthoc_engagement.py`, `posthoc_recsat.py`;
    - `confirm_holdout.py`;
    - `periods.py`.

## Round 2 redirects (2026-10-04)
*From the round-1 reflection (`writeup/round1-reflection/round1-reflection.pdf`).*
- **Where round 1 went sideways:** The result is good, but responses were measured through mentions, which are contaminated.
- **What the direction is really after:** Attention is the scarce resource, and coupling is its allocation.
- **H18-R1.** A salience law, uptake = f(mention, recency, novelty, sender status), is fit and predicts held-out uptake (E5).
- **H18-R2.** Total attention per turn is conserved; re-test with reply-threading labels.
- **H18-R3.** An optimal room size maximizes total useful uptake (HH111).
