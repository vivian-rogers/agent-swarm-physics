# Behavior states via Jev: design

A shared observable: a **finite, regime-invariant behavior state** for every agent and every 5-minute window of active time. It is classified zero-shot by **Jev** (TypeSafe AI's hosted typed-classification model). Decided by Vivian on 2026-10-03.

## Why
- **Measurement invariance (faithfulness axis A).** Action labels changed meaning with the shift from GUI to bash; behavior classes don't.
- **Hidden structure.** In regime III most activity is inside computer-use sessions, where event types are blind. H09 E2 found event-level entropy production nearly vanishing there.
- **A finite state space** for currents, entropy production, Markov state models, occupancy free energies, dwell times and Potts couplings.
- **Ideas served:** HH04, HH05, HH07, HH08, HH17, HH19, HH21, HH45, HH47, HH50–HH53, HH55, HH56, HH61–HH63, HH67; H09 T1, T4–T7; H01 D2.3, D7, D8; H02 and H05 (couplings in behavior space).

## Unit
One agent × one 5-minute window of active time (from `activity_bins` / `calendar`). Windows with no activity at all are labeled `idle/absent` without a call. Estimate: ~300k windows, of which ~200k have activity.

## Input text per window (assembled locally; truncated to ~2k tokens)
- **Actions:** action types with counts; bash head commands; error count; reasoning length (from `actions`). The full command text and outputs aren't in the shared tables yet. If the labels need them, add a truncated `command_text` column (first ~200 characters per turn; ~50 MB) through one more scan of `computer_use_turns`.
- **Chat:** the agent's own messages in the window (from `chat_text`), plus counts of messages it was exposed to (from `exposure`).
- **Intentions:** the current self-written session or consolidation goal (from `intentions_text`).
- **Context line:** room; goal number; regime. Not the goal text, to avoid leaking the field into the label.

## Jev questions (typed)
1. **choice, the behavior state (one of about 10):** plan/coordinate · build/execute · research/browse · communicate externally · debug/recover · verify/report · self-maintenance (memory, reflection) · social chatter · meta (about the village or the agent itself) · idle/wait.
2. **noul (yes/no probabilities):**
   - blocked or failing?
   - working on another agent's artifact?
   - responding to a specific agent?
   - goal-aligned?
3. **choice, a message act** (chat windows only): propose · agree · disagree · assign · report · ask · thank/praise · other.
4. **score:** progress, 0–4.

Keep Jev's confidence for every value. Soft labels (a probability per state) feed the √p vector representation (model 11), and low-confidence windows can be audited.

## Validation (before labeling at scale)
1. **Draft round.** Label ~200 **non-holdout** windows stratified by regime, family and mode; Vivian reviews the taxonomy.
2. **Hand audit.** ~200 windows for agreement (Cohen's κ against our labels); the confusion matrix guides merging or splitting classes.
3. **Invariance.** Class frequencies and confusion should be stable across model families and regimes; flag classes that only exist in one era.
4. **Markov check.** Is a 5-minute state sequence roughly first-order? Use a Chapman–Kolmogorov test on non-holdout days.

## Cost, storage, terms
- **Cost:** ~200k windows × 1–3k tokens ≈ 200–600M input tokens × $0.042/M ≈ **$8–25**. Output tokens are free.
- **Storage:** labels plus confidences, a few MB in `data/processed/shared/behavior_states.parquet`. Assembled inputs are not kept beyond a small audit sample.
- **Terms:** zero-shot classification is analysis, not training; no model is trained on the data. Window text is sent to Jev via OpenRouter, which Vivian approved.
- **Holdout:** label every window, including held-out days. The labels are a measurement. Exploratory analyses must still mask the holdout.

## Access (settled 2026-10-03)
- **Endpoint:** OpenRouter Decisions API, `POST https://openrouter.ai/api/alpha/decisions`, model `typesafe/jev-1.13`. Body `{model, state, questions}`; answers carry `choice` + `confidence` + `probabilities` (choice), `noul` (noul), `score` + `probabilities` (score), and `usage.cost`.
- **Key:** `OPENROUTER_API_KEY`, read from the environment, else from the project `.env` (gitignored, mode 600). Never print or commit it.
- **Script:** `label_windows.py` (`--draft N`, `--all`, `--limit`, `--compile-only`, `--max-usd` cap). Resumable JSONL in `data/processed/behavior_states/`.
- **Measured cost:** ~$0.00005 per window, so the full run is ~$10, at the low end of the estimate.

## Draft round 1 (2026-10-03): 200 non-holdout windows, stratified by regime × lab
- $0.0096, 0 errors. Behavior: verify_report 64, build_execute 44, research_browse 26, debug_recover 24, idle_wait 15, plan_coordinate 9, communicate_external 8, social 6, self_maintenance 3, meta 1. Mean confidence 0.71; 22% below 0.5.
- Message act (99 windows with own chat): report 81, propose 9, thank_praise 4, others ≤ 2. **Too coarse:** "report" swallows almost everything. Candidate split: status update / result announcement / handoff.
- **verify_report may be absorbing chat-heavy windows**: check in the hand audit whether it is really "posted a status message".
- Next: hand audit (κ) on ~40 windows by Vivian, revise taxonomy, then invariance and Markov checks, then `--all`.

## Validation (2026-10-03)
**Taxonomy v2** (`label_windows.py`; execute_task with an artifact-change tie-breaker, narrower verify_report, idle_monitor, stricter blocked/others_work, addresses_participant; adds intention age, previous-window actions, longest identical-action run, first-window flag; `--keys` to relabel an exact sample, since polars grouped sampling isn't reproducible):
  - Same 200 windows, vs blind Claude labels (v1 definitions, mapped): behavior κ 0.50 (v1: 0.53). But agreement when Jev's confidence ≥ 0.8 rose to **87%** (v1: 75%; n = 69).
  - **blocked κ 0.38** (v1: 0.15; agreement 0.93). others_work κ 0.28 (v1: 0.20). verify→execute confusion 14 (v1: 19).
  - Cost $0.011 per 200 windows.
  - Plan: use Jev's full probability vectors as soft states (ψ = √p, model 11) rather than hard labels. Vectorize state assembly before the full ~200k-window run (~$10).

- **v1 blind second labeler** (Claude agent, all 200 windows, no access to Jev's answers): behavior κ 0.53 (61%); message_act κ 0.54; progress rank correlation 0.70; blocked κ 0.15; others_work κ 0.20.
- **Ambiguities it reported:** build vs verify; "monitoring"; producing vs posting externally; looping agents; courtesy openers in message acts; replies addressed to humans; behaviors with no home (gameplay, trading).
- **State-assembly gaps:** stale intentions; recap messages desynchronized from the actions; boot windows; looping agents.
