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

## v3 and full run (2026-10-04)

### Decision rule (written before the final v3 validation run)
The blind Claude reference labels were made on the thin v1 state (no command text, `bash_head` null for most regime-III turns). So κ against them partly measures agreement with what that labeler could see. v3 replaces v2 if:
- (a) behavior κ is within 0.05 of v2's 0.50 in Claude's v1 label space, or the monitor-aware κ is at least 0.50;
- (b) blocked and others_work κ do not get worse;
- (c) on the label-free evidence check (windows where git printed a commit or push, or a deploy ran, which the execute tie-breaker settles as execute_task), v3's execute share is at least v2's.

Otherwise the full run uses whichever of {v2 questions, v3 questions} × {v2-style state, v3 state} did best.

### What v3 changed
**Code:** `assemble_v3.py` (vectorized state assembly), `scan_turn_outcomes.py` (one raw pass), `label_v3.py` (taxonomy, calls, compile) and `compare_labels.py` (validation). `label_windows.py` (v2) is unchanged, so v1 and v2 stay reproducible.

**Vectorized assembly.** Every action, command, event, chat message, exposure row and intention gets its window key (pt_date, agent, w = minute // 5, exactly as in `activity_bins`) once; then everything is grouped. All 206,483 active windows assemble in about 25 s, where v2 took about 1 s per window.

**Real failures instead of stderr.** `actions.error` is `bool(raw error)`, i.e. "stderr was non-empty". Git and curl write normal progress to stderr, so 62% of `git push`, 54% of `git commit` and 49% of `git add` turns are flagged as errors. `scan_turn_outcomes.py` (one gzcat pass, about 8 min) classifies the raw error and output text instead:
- 58% of stderr-flagged bash turns are not failures, and 15% of real failures have empty stderr;
- real failures are 6.9% of bash turns (stderr: 14.1%), split as not_found, traceback, timeout, git_rejected, exit_code, http_error, usage and other.

Shown to Jev as `failed_actions`, with `[failed]` on the affected command samples.

**Artifact-change evidence** (the execute tie-breaker needs it; v2 never saw it): git-printed commits (5.8% of bash turns) and pushes (5.6%); file writes (23%; shell redirects, tee, `sed -i`, patches and git staging outside heredoc bodies, or write calls inside Python heredocs; rm/mkdir/cp/mv/clone and redirects into /tmp or /dev excluded); API/PR writes (3.5%); deploys (0.3%).

**Command text for every bash turn**, including the agent's own first comment line (`# I'm committing and pushing …`, on 75% of bash turns). `bash_head` is null for most regime-III turns, and the artifact sidecar strips comments.

**Assembly-gap fixes:**
- **intention freshness:** age in minutes; stale above 60 min (beyond the ~97th percentile of update intervals); previous-day flag; source.
- **recap/action desync:** the previous window's actions, last 2 commands and own-message count; the next window's first actions and first 2 commands. The instruction says messages may recap earlier windows.
- **boot windows:** the agent's first active window of the PT day (not calendar w == 0), minutes since first activity, a session start in the window, and a context reset in the previous window.
- **looping:** the longest identical action+command run, excluding scaffold mirror turns and the forced mouse_move (the forced mouse_move is also dropped from the action counts); the share of failures repeating an earlier failure; the share of no-op (`none`) actions.
- **self-repeat:** own messages with cosine > 0.95 (bge-small) to an earlier own message the same PT day (H12's rule).
- **messages seen** that mention the agent (from `chat_mentions_clean`).

Zero and false fields are omitted to save tokens.

**Taxonomy v3.1** (11 states): v2 with idle_monitor split into **monitor_wait** (waiting for a specific expected event and checking for it) and **idle** (nothing purposeful; purposeful clicks and loops are not idle). Other changes:
- **debug_recover** is debugging only when it is the main activity ("failures met while doing something else do not count").
- **The behavior instruction** says: if the agent only chatted, label the chat; the intention is a plan, not evidence.
- **blocked** now means stalled by failures, a loop, or waiting on others.
- **others_work** now excludes co-building a shared project.
- **message_act was dropped** (v1 found "report" swallowed it; DQ2 labels stance on reply pairs) to fund the richer state within the cap. The progress score and addresses_participant are kept.

The draft supports the monitor split: the blind labeler flagged "monitoring" as an ambiguity, and 23 of its 200 notes describe monitoring or waiting for something, spread over research_browse, idle_wait and verify_report.

### Validation (same 200 draft windows; v3 spend on validation $0.093)
Runs:
- **v3a:** the first v3 state, with stderr shown as failures.
- **v3b:** real failures, the broad file-write rule.
- **v3 (= v3.1):** final.
- **q3_sX:** v3 questions on the v1 or v2 state.

Claude reference = blind labels on the v1 state, mapped to the v1 categories (execute_task → build_execute; idle, monitor_wait, idle_monitor → idle_wait).

| run | behavior κ (agree) | κ, conf ≥ 0.8 (n, agree) | κ, 0.5–0.8 (n) | κ, < 0.5 (n) | regime I / II / III | blocked κ | others κ | addresses κ | progress ρ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| v2 | 0.50 (0.60) | 0.83 (69, 0.87) | 0.51 (71) | 0.09 (60) | 0.56 / 0.52 / 0.45 | 0.38 | 0.27 | 0.78 | 0.76 |
| v2 rerun | 0.49 | 0.85 (68, 0.88) | 0.42 | 0.16 | — | 0.38 | 0.26 | 0.80 | 0.75 |
| q3_s1 | 0.48 (0.58) | 0.74 (72, 0.79) | 0.46 | 0.15 | 0.57 / 0.48 / 0.42 | 0.66 | 0.27 | 0.82 | 0.73 |
| q3_s2 | 0.46 (0.56) | 0.71 (64, 0.77) | 0.44 | 0.22 | 0.51 / 0.48 / 0.42 | 0.56 | 0.31 | 0.78 | 0.76 |
| v3a | 0.38 (0.52) | 0.55 (70, 0.69) | 0.31 | 0.27 | 0.49 / 0.30 / 0.35 | 0.48 | 0.31 | 0.78 | 0.63 |
| v3b | 0.37 (0.53) | 0.43 (93, 0.67) | 0.35 | 0.17 | 0.46 / 0.29 / 0.35 | 0.52 | 0.26 | 0.78 | 0.63 |
| **v3.1** | **0.38 (0.54)** | **0.43 (91, 0.68)** | **0.30 (69)** | **0.31 (40)** | **0.48 / 0.28 / 0.38** | **0.50** | **0.41** | **0.78** | **0.63** |

What the runs show:
- **Jev is near-deterministic:** a v2 rerun agrees κ 0.96 with v2.
- **The v3 taxonomy on the old states costs little κ** (0.46–0.48) and lifts blocked from 0.38 to 0.56–0.66. In the "monitor-aware" reference (Claude's monitoring notes re-labelled monitor_wait), its κ is 0.50.
- **The v3 state is what moves Jev away from the Claude reference.** v3.1 vs v2 agree only κ 0.38. On the 128 windows with no commit, push, deploy or file write, κ vs Claude is 0.41 for v3.1 and 0.56 for v2.

Two checks don't depend on what the Claude labeler could see:
- **Evidence check.** In 41 windows git printed a commit or push, or a deploy ran. The execute tie-breaker (in v2 and v3 alike) settles these as execute_task. Execute share: v3.1 100%, Claude 66%, v2 44%, q3_s2 39%. v2 breaks its own rule there because it can't see the commits.
- **Two blinded A/B audits** of v2 vs v3 disagreements, judged by Claude Code (this agent) against the v3 definitions using the full v3 evidence, without knowing which run gave which label:
  - audit 1 (v3b, 32 windows): v3 right 17, v2 right 9, both acceptable 6;
  - audit 2 (v3.1, 30 fresh windows): v3 right 17, v2 right 6, both acceptable 7 (sign test p = 0.035);
  - combined, v3 is right 34 times to v2's 15.
  - v3.1's remaining errors: checking or playtesting labelled research or execute instead of verify_report; one no-op loop with a consolidation labelled self_maintenance; one label leaked from the next window's commands.

**Decision: full run on v3.1.** By the pre-written rule, v3.1 passes (b) (blocked 0.38 → 0.50; others_work 0.27 → 0.41) and (c) (execute share 100% vs 44%), but fails (a) (κ 0.38 vs 0.50). That is a deliberate deviation from the rule, made after seeing the data. The reason: the reference cannot see the evidence v3 adds. On every check that can see it (the evidence windows, two blind audits, and the stuckness and others' work flags), v3.1 beats v2.

Costs of the decision:
- **Confidence no longer predicts agreement with Claude:** 68% agreement at conf ≥ 0.8, against v2's 87%.
- **Progress agrees less with Claude:** ρ 0.63, against v2's 0.76.

A fresh blind reference labelled on v3 states (Vivian, or a labeler she approves) is the missing check.

### Full run (2026-10-04)
**Scope:** every active roster agent × 5-min window, 2025-04-02 → 2026-09-18, holdout included and flagged.
- **Calls:** 206,433 in 32 min, about 110/s with 16 concurrent requests and one CPU thread (asyncio). 110 retries.
- **Spend:** full run $13.04; total v3 spend including validation $13.13, against the $15 cap. Mean $0.000063 per window.

**Coverage:** 203,170 of 206,483 active windows (98.4%).
- The last 3,313 calls returned **HTTP 402 (Payment Required)**: the shared OpenRouter key/account ran out of credit before the $15 cap, which counts v3 spend only.
- All of them are on the last three days, 2026-09-16 (31% missing), 09-17 (53%) and 09-18 (99%). These are goal #51 holdout days, so **non-holdout coverage is 100%**.
- They carry `labeled = false` and `label_error = '402'`.
- Once credit is topped up: `uv run --with httpx python infra/behavior_states/label_v3.py --all --retry-errors --max-usd 15` (about $0.22), then `--all --compile-only`.

**State mix** (argmax share of labelled windows): execute_task 52.3%, research_browse 13.5%, monitor_wait 8.6%, verify_report 8.3%, self_maintenance 5.6%, debug_recover 4.9%, communicate_external 2.7%, idle 2.4%, plan_coordinate 1.0%, social 0.5%, meta 0.2%.

Mean probability mass by regime:

| | execute | research | monitor_wait | verify | self_maint. | debug |
| --- | --- | --- | --- | --- | --- | --- |
| I | 0.38 | 0.18 | 0.13 | 0.11 | 0.02 | 0.08 |
| II | 0.41 | 0.23 | 0.03 | 0.18 | 0.01 | 0.09 |
| III | 0.52 | 0.11 | 0.07 | 0.07 | 0.10 | 0.05 |

Other per-regime figures:
- Mean confidence: 0.69 (I), 0.69 (II), 0.73 (III).
- `p_blocked` ≥ 0.5: 22% (I), 8% (II), 8% (III).
- `p_others_work` ≥ 0.5: 7%, 19%, 3%.
- Probability vectors sum to 0.99–1.00.

**Outputs:**
- `data/processed/shared/behavior_states_v3.parquet`: 7.5 MB, 295,161 rows = the full agent × window grid; schema in `infra/data-quality/DQ3-behavior-states-v3.md`.
- Raw answers: `data/processed/behavior_states/jev_all_v3.jsonl.gz` (9 MB). Resume, compile and the spend total read it.
- `turn_outcomes.parquet`: 32 MB.

**Relation to `actions_bash_head_fixed.error_class`** (`infra/shared/turn_errors.py`, the platform-failure taxonomy built in parallel): the two agree.
- `turn_outcomes.failed` holds on 1.2% of `error_class = none` turns, 7% of `git_info` turns, and 69–93% of timeout/other/resource turns.
- `failed` also catches failures reported only on stdout (80% of `http_error` turns have no `error_class`) and treats `! [rejected]` pushes as failures (42% of these are `git_info` in `error_class`).
- Use `error_class` for platform stalls (H38) and `failed` for task failure and stuckness.

### Limits
- **Validation reference.** κ is measured against blind labels made on the thin v1 state. The adjudication behind the v3 decision is two blinded A/B audits (62 windows) by Claude Code against the v3 definitions: one adjudicator, the same model family as the reference labeler. A fresh human (or approved) blind reference on v3 states is still owed.
- **execute_task dominates (52%)** because of the artifact-change tie-breaker. A window with a commit plus a status message is execute_task. Downstream state models may want execute split by `n_commit_ok`/`n_push_ok`/`n_file_write`, or use the probability vector.
- **plan_coordinate (1%), social and meta are rare** and partly under-called in chat-only windows (two audit misses).
- **The progress score agrees less with the reference** (ρ 0.63 vs v2's 0.76). It now reflects artifact changes the reference couldn't see.
- **Confidence is not a calibrated agreement probability** (68% agreement at ≥ 0.8). Use the vectors, not thresholds.
- **Heuristic evidence.** File writes are a command-text heuristic; failures are text-pattern classes. Agent comment lines are narration, a claim and not ground truth.
- **Context windows can leak.** The previous and next window's commands are shown as context; one audit miss took its label from the next window.
- **message_act is not in v3.** Use v2's draft or DQ2's reply stance.
- **Inactive windows inside an agent's span** (`active = false`, `in_span = true`) are unlabeled idle-by-absence. Decide explicitly how a state model treats them.
