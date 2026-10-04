# Context ledger (turn-level visibility)

**What it answers:** for every model call of every agent, which chat messages newly entered its context since its previous call, and when the call's context was assembled.

**Built by** `infra/shared/context_ledger.py`. All days are included; `holdout` flags locked-holdout days, and exploratory users must drop them. No text is kept, only message ids. Built 2026-10-04 on revision `838b415`.

```
uv run python infra/shared/context_ledger.py scan                  # raw pass for logged call starts (~1 min; cache)
uv run python infra/shared/context_ledger.py build --validate      # tables + validation JSON (~40 s + ~15 s; 3 GB RAM)
uv run python infra/shared/context_ledger.py build --dry-run 38 [--validate] [--out DIR]   # one goal period, in memory
```

Outputs:
- `infra/data-quality/context_ledger_validation.json` (every number quoted below);
- `context_ledger_calibration.json` (scaffold overheads and latencies).

## Tables (`data/processed/shared/`)

| Table | Rows | Size | One row per |
| --- | --- | --- | --- |
| `call_windows.parquet` | 2,604,092 | 106 MB | model call: the timing layer |
| `context_ledger_turns.parquet` | 2,604,092 | 59 MB | model call: the content layer (same `turn_id`) |
| `context_ledger_items.parquet` | 2,101,842 | 47 MB | (receiving call, chat message) |
| `call_starts_logged.parquet` | 515,097 | 5 MB | Gemini response carrying HTTP timing (scan cache) |

The Claude Code agent is excluded as a recipient, as in `exposure`; its messages are items for others. Its own input stream is used for validation instead.

### `call_windows`
- **Identity:** `turn_id` (int32, sorted by agent, then time), `agent`, `pt_date`, `goal_no`, `regime`, `holdout`.
- **Call content:**
  - `kind` (primary): cu_action, talk, pause, wait, consolidate, session_start, session_stop, search, room_move, request. `talk` is a separate flag (a call can talk and wait, or talk and pause).
  - `src`: event, action or both. "both" is a computer-use row merged with the event it mirrors.
  - `ctx_mode`: chat (regime I/II call outside a computer-use session), cu, or summary (CONSOLIDATE or STOP_USING_COMPUTER; receives no items).
  - `n_rec`: records merged into the call.
- **`t_call`, `t_call_lo`, `t_call_hi`:** best estimate of when the call's context was assembled, with bounds (≈90% coverage where it could be checked).
  - `start_src`: logged, prev_end, pause_expiry, marker, latency.
  - `start_conf`: high = logged; medium = chained computer-use call; low = latency-placed.
- **Logged times:**
  - `t_first`, `t_log`: the call's first and last logged record. Rows are written once, after the action executes.
  - `t_end`: when the call stopped occupying the agent. That is `t_log`, except for a PAUSE: min(expiry, next record).
  - `t_prev_end`: the previous call's `t_end`.
  - `t_marker`: latest scaffold marker in between.
- **What sits in between:**
  - `gap_kind`: busy, pause, pause_early, after_summary, marker, session_start, long_prev, first_of_day.
  - `after_pause`, `wake_early`, `long_prev` (previous call busy for more than 60 s from its start to its logged end), `prev_busy_s`, `first_of_day`.
- **Measured timing (Gemini calls only):** `logged_start` and `dur_api_s` (server time); `exec_s` (logged end minus API response, i.e. tool execution); `latency_s` (`t_first − t_call`); `pause_s`.

### `context_ledger_turns`
- **Timing:** `turn_id`, identity columns, `t_call`, `t_prev_call` (the window opens here: previous *receiving* call's `t_call`), `t_first`, `t_log`.
- **Call:** `src`, `kind`, `talk`, `ctx_mode`; `room` (agent's room at `t_call`); `room_changed` (room at window start ≠ room at call).
- **New items by kind:** `n_agent`, `n_human`, `n_nudge`, `n_pause_resume`, `n_automated_other`.
  - `n_ment`: items whose `chat_mentions_clean.mentions_roster` names this agent.
  - `n_nudge_me`: nudges naming it.
  - `k_new`: all new items; `chars_new`: their characters.
- **Backlogs:**
  - `k_since_talk`: items received since the agent's previous talk call. At talk calls this is H18's k under the corrected rule.
  - `k_ctx`: items received since the last context reset; computer-use mode only.
  - `ctx_pos`: receiving calls since the last reset.
- **Uncertainty:**
  - `n_inflight`: messages that arrived while this call was being generated (`t_call ≤ t_msg < t_first`); they go to the next call.
  - `n_uncertain`: items within the start bounds of this call or the previous one.
- **Cap:** `n_ev` (events by others in the room during the window); `cap_hit` (from 2026-06-11, `n_ev` > 200); `n_omitted` (items older than the 200 newest events).
- **Resets since the previous receiving call:**
  - `reset_consol`: a CONSOLIDATE.
  - `reset_forced`: that consolidation closed a 41–42-record segment (H15's forced-erasure rule, the 41-turn cap; NE41).
  - `reset_session`: a session start or stop, or a scaffold marker (fresh computer context).
  - `first_of_day`; `prev_seg_len` (records in the segment that the consolidation closed).
- **Other:** `outage_s` (seconds of the window inside a joint-silence run of the shared `outages` table, H38's rule); `outage_off` (overlaps a village-off run); `lookback_capped` (window longer than 7 days).

### `context_ledger_items`
- `turn_id` (the receiving call) and `message_id` (join `chat_core` for time, room and length).
- `sender`: agent code; null for human and automated messages.
- `kind`: agent, human, nudge, pause_resume or automated_other. Automated kinds come from `kicks_classified`; they agree 100% with the text rule.
- `age_s`: `t_call − t_msg`, float32.
- `ment`: the message names the recipient.
- `rank`: 1 = newest in the batch.
- `during_prev`: arrived while the previous call was being generated.
- `uncertain`: within the start bounds.
- `omitted`: beyond the 200-event cap.

## Semantics

**Visibility rule.** A message m is in context for call c iff it was posted by someone else, in the agent's room at posting time (`rooms_timeline`; #general before 2026-02-25), before c's context assembly `t_call(c)`. It is *new* at c iff `t_call(previous receiving call) ≤ t_msg < t_call(c)`.

The windows tile time, so each (message, recipient) pair is assigned to exactly one call: the first call that could see it. A PAUSE, a long tool call or any other gap is time during which arrivals become visible to the next call, never to the call that is already running.

**Calls (turns) per regime.** Records are `actions` rows plus agent `events_core` events, with these rules:
- **Mirrors.** A computer-use row and the event it mirrors are one call when they are ≤ 2 s apart: send_message_back_to_chat ↔ AGENT_TALK, pause ↔ PAUSE, search_history, move_to_room, request_Google_sign_in, request_human_helper, cancel_request_for_human_helper, request_approval_for_unsolicited_outreach. The last four are new relative to H14's list; their pairs match 1:1.
- **Same call.** Records ≤ 1 s apart are one call: parallel tool calls (until 2026-06-03), WAIT+AGENT_TALK, START_USING_COMPUTER+AGENT_TALK. 99.98% of event pairs ≤ 1 s apart carry identical input tokens.
- **Markers, not calls.**
  - The forced `mouse_move` that opens a fresh computer context: the first computer-use row after CONSOLIDATE / START_USING_COMPUTER or of the day, if it is a mouse_move. Where usage is logged, 99.99% have 0 input tokens (no model call), against 1.3% of other mouse_moves.
  - RESTARTING_AFTER_GOOGLE_SIGN_IN.
  - Markers anchor the next call's start (if ≤ 10 min before it) and set `reset_session`.
- **Ignored.** STOP_HUMAN_USE_SESSION and OUTREACH_APPROVAL_RESPONSE: external, though attributed to the agent.
- **Regime I/II.** Chat-mode calls are event-only calls outside a computer-use session (WAIT, AGENT_TALK, START_USING_COMPUTER, ...). Computer-use calls are `actions` rows between START and STOP. STOP_USING_COMPUTER is the session-summary call.
- **Regime III.** Everything is a computer-use call except CONSOLIDATE (the memory call).
- **Logged times.** CONSOLIDATE and STOP are logged at completion; their start is chained to the previous call. CONSOLIDATE and STOP calls receive no items: arrivals during them roll over to the next call.

**Call start `t_call`.** Calibrated on 341,637 non-holdout Gemini calls whose responses log the HTTP `date` header and the server-timing duration (start = date + 0.5 s − dur, ±0.5 s).
- **Logged** (19% of calls; Gemini 2.5 Pro, 3 Pro, 3.1 Pro, 3.5 Flash and 3.8 Flash, from 2025-12-19 on): used directly.
- **Chained computer-use calls** (75%): the previous end + 1.70 s. The scaffold overhead has median 1.70 s, 5th–95th percentile 0.53–7.8 s; only 0.10% start more than 2 s before the previous end. So the busy-loop assumption holds for computer use.
- **After a timer PAUSE:** expiry + 3.2 s (q95 28 s). Wakes are at the timer in 99.8% of regime-III and 98.8% of regime-I cases. (An apparent "68% early wake" in regime I was an artifact of PAUSE+AGENT_TALK calls.)
- **After a marker:** marker + 1.8 s. After a summary call: previous end + 0.8 s.
- **Latency-placed** (2.3%): `t_first − m_agent·ρ`, where m_agent is the agent's median chained-call latency.
  - ρ is calibrated on Gemini: chat 0.94 [0.49, 1.83]; computer use 1.0 [0.43, 2.66].
  - Used for chat-mode calls, the first call of a day without a nearby marker, and early wakes.
  - **Chat-mode calls are scheduled, not chained.** Logged starts sit a median 55 s (q05–q95 22–130 s) after the previous end. In #30–#31 the start-to-start cadence had median 74 s (IQR 54–99 s), and 45% of calls had no new message in the gap, so they are not message-triggered. Latency is tight (median 9 s), so placing by latency beats chaining.

## Validation (full build; non-holdout where it matters)

1. **Consistency:** 0 violations on every check:
   - `t_call ≤ t_first ≤ t_log`; bounds contain `t_call`; `t_call` monotone per agent;
   - items never at or after `t_call` and never before the window;
   - no items on summary calls; no duplicate (agent, message); no self-items;
   - room at posting time = recipient's room;
   - Σ `k_new` = item rows.
2. **Spot checks:** a brute-force recount for 300 random receiving calls per regime gives 0 mismatches. A raw `chat_messages.jsonl.gz` check (324 items) finds 0 time or room mismatches.
3. **Claude Code agent's input stream** (H08's C1 fetch tables; 14 current-feed days in #30, #31, #33 and #35, before its 2026-03-17 replay; fetch = context assembly):
   - **Room rule:** membership recall 0.9998. Of 4,372 chat messages it saw, 1 came from another room; it saw 1 of 167 other-room messages.
   - **Timing:** 85.4% of the messages it saw entered at exactly the call the window rule predicts; 91.0% within one call. 14% entered later than predicted (its pull loop with limits and re-reads); 0.6% earlier.
   - **By period:** exact-call share 0.88 (#30), 0.82 (#31), 0.88 (#33), 0.81 (#35).
   - **Precision 0.60:** it never fetched 40% of the in-room messages, consistently with H08 (0.57–0.64). This is a property of its pull loop (`get_events` with limits, `markAsSeen` false on 44% of fetches), not of the room rule. The standard scaffold pushes all unseen events at every call.
   - **Coverage by kind:** agent 0.60, human 0.65, automated 0.55.
4. **Leave-logged-out (Gemini, 158,199 items):** re-estimating starts without the logged time assigns 91.0% of items to the same call. By gap kind: chained 0.88, pause 0.92, after summary 0.98, marker 0.96, first of day 1.00. The start error has median 0 s and \|err\| ≤ 2 s on 83% of chained calls; the bounds contain the logged start for 88–93% of calls in each class. For non-Gemini agents, expect about 10% of items one call off; `uncertain` flags 21% of items as near a boundary.
5. **Token growth** (988,795 computer-use calls with usage, within a context segment): the jump in prompt tokens over the previous call correlates with the characters of the ledger's new items.

   | Assignment | r (all) | r (calls where ledger and naive disagree, n = 95,105) |
   | --- | --- | --- |
   | Ledger | 0.228 | 0.297 |
   | Naive (H18) rule | 0.103 | 0.030 |
   | Ledger shifted one call later | 0.058 | — |
   | Ledger shifted one call earlier | 0.035 | — |

   - The pattern is the same for Anthropic (0.305 vs 0.008 where they disagree) and Gemini (0.342 vs 0.079).
   - The correlation is present from 2025-04 on (r 0.14–0.40 by month), so chat entered computer-use context throughout. The 2025-12-20 CHANGELOG fix was a timezone hotfix, not the start of interleaving.
6. **Naive rule vs ledger (status changes, non-holdout pairs).** The naive rule is H18's: call start = the agent's previous logged record, and every call receives.

   | Regime | Pairs | Receiving call changes | Talk "invisible" under naive | Of those, visible under ledger |
   | --- | --- | --- | --- | --- |
   | I | 454,897 | 150,064 (33.0%) | 122,776 | 85,451 (69.6%) |
   | II | 39,504 | 8,923 (22.6%) | 5,487 | 3,772 (68.7%) |
   | III | 1,063,403 | 341,083 (32.1%) | 49,643 | 32,434 (65.3%) |

   - In regime III the flips are almost all PAUSE windows (95.6% of naive-invisible messages after a pause are visible) and first calls of the day (93%). Only 14% of the busy ones flip.
   - In regimes I/II they are scheduled chat calls (71–73% of busy) and long previous calls (80–86%).
   - This confirms and quantifies H29's 39–70%.
7. **vs `exposure`:** the same (message, recipient) pairs (2,101,313 shared; 449 exposure-only; 529 ledger-only, from the pre-rooms #general fallback). But `exposure.lag_s` overstates the time to visibility: median 131 s vs 18 s (I), 179 s vs 19 s (II), 290 s vs 50 s (III). It is more than 60 s too long for 50–60% of pairs.
8. **H18's k vs `k_since_talk`** at the same talk messages: log-correlation 0.80–0.99. 19–30% of talks differ each way in regime I (#24–#31), 2–11% in regime III.

## Known limits
- **Start times are measured only for Gemini.** Everyone else's starts are calibrated estimates. The scaffold overhead is provider-independent, but latency-placed calls (chat mode, first call of a day) rely on the agent's own computer-use latency scaled by Gemini's ratio. Use `start_conf`, the bounds and `uncertain` for sensitivity.
- **Unknown truncation in chat mode.** Chat mode rebuilt its prompt from the recent chat each call, and 2025-08-20 "limited the number of chat messages fetched"; the limit is unknown. "New" is the delta since the previous call, but not all of it is guaranteed to be shown when bursts exceed the limit. After 2026-06-11 the 200-event cap is modeled (585 calls hit it; 47,080 items `omitted`).
- **Unknown context after resets.** After a reset, the fresh context also re-shows a room-state snapshot (2026-02-27) and memory. The ledger lists only new items; old items re-shown at a reset are not items. Roll-over during CONSOLIDATE / STOP (arrivals go to the next call, not to the memory call) is an assumption, not tested: CONSOLIDATE token counts are too erratic to test it.
- **Non-chat events are counted, not listed.** Other agents' events (PAUSE, CONSOLIDATE, room moves, ...) enter context too. `n_ev` counts them but they have no item rows. Room membership comes from `rooms_timeline` (as-of on room-tagged agent events), so moves are dated at the first room-tagged event in the new room.
- **New agents.** A new agent's first call opens its window at that day's calendar start, not earlier.
- **Claude Code agent.** It is not in the tables (pull-based input; replayed feed from 2026-03-17). Use H08's `cc/` tables for it.
- **First-of-day calls.** The windows of first-of-day calls span the night; filter `first_of_day` for within-day statistics.
- **Validation is limited to one agent.** It rests on one atypical agent and five Gemini models. Mentions are still claims, not uptake (H18's placebo).

## Using it
- **Per call:** `context_ledger_turns` filtered to `~holdout` and `ctx_mode != "summary"`. Message details: join items on `turn_id`, then `chat_core` on `message_id`.
- **H18-style pending sets:** at talk calls, `k_since_talk`. The members are the items of the receiving calls since the previous talk call. Messages that arrived during the talk's own generation are the next call's items with `during_prev`.
- **Sensitivity:** recompute with `t_call_lo` / `t_call_hi` (in `call_windows`), or drop `uncertain` items and `start_conf == "low"` calls.
