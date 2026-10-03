# infra

Shared processing code used by more than one hypothesis.

Belongs here: loaders for raw tables, time and regime handling (a
machine-readable regime table from `data/raw/ai-village/CHANGELOG.md`), common
transforms (e.g. building interaction networks), and processing schemes that
two or more hypotheses share.

Doesn't belong here: code specific to one hypothesis. Keep it in that
hypothesis's `scheme/` or `model/` until a second hypothesis needs it.

## Planned shared tables (Phase 0)

**Built 2026-10-03** by `infra/shared/scan_tables.py` (four parallel scans, ~72 s) then `infra/shared/build_derived.py` (~1 s), into `data/processed/shared/` (~120 MB), each with `_provenance.json`. Text is stripped from every core table; text lives only in separate `*_text` sidecars, used in Phase 2. Designed around the export's actual shape:
- the village is active only 2–8 h per weekday, so wall-clock time is mostly empty;
- `event_index` is the canonical order;
- agent events name the actor in `speakerId` (`AGENT_TALK`) or `agentId` (everything else);
- `roomId` is on ~100% of `AGENT_TALK`, `CONSOLIDATE` and `PAUSE` events and 93% of `SEARCH_HISTORY`, but only 2% of `WAIT` and 14% of the (mostly pre-rooms) start/stop events;
- every chat message has a room;
- human-side chat has 602 speaker IDs, of which `automated` (2,230 messages) is the bot.

| Table | Rows (approx.) | Contents | Used by |
| --- | --- | --- | --- |
| `calendar` | 404 days | PT date, village day, empirical active window (first and last agent event), documented hours, goal #, regime, active NEs, #best/#rest scope | everything (time base) |
| `goal_periods`, `natural_experiments`, `scaffold_changes` | 51 / 40 / 125 | machine-readable versions of the catalogs and the CHANGELOG | everything |
| `roster` (+ `roster_daily`) | 46 (× days) | id, name, model, lab, join, leave, flags (Claude Code, fine-tuned) | everything |
| `events_core` | 381,610 | event index, UTC time, **active time**, day, goal #, regime, actor and actor kind (agent / human / automated), action type, room (filled forward where missing, flagged), tokens in/out, message and session links | Hawkes, aging, Green's functions |
| `chat_core` | 183,485 | message id, time, room, speaker kind and id, length, @-mentions of agents, extracted URLs and repo names, reply proxy | contagion, couplings |
| `rooms_timeline` | agent × interval | which room each agent was in when; everyone in #general before 2026-02-25 | S4, H01 |
| **`exposure`** | ~2M | for each message: the agents in the room, and when each would next see it (its next turn; capped at 200 events after NE22) | contagion, S1, S4, S5, H01 (the most reused table) |
| `activity_bins` | ~1.5M at 1 min | agent × active-time bin (1, 5, 15 min): talk / act / idle / consolidate flags and counts, a regime-invariant action class, and a mask for agents not on the roster | Ising, Potts, susceptibility, entropy production |
| `kicks` | ~10k + events | outside impulses: automated messages, human messages, goal kickoffs, operator corrections, roster changes, NEs; with time and target (agent / room / all) | Green's functions, Hawkes, susceptibility |
| `intentions` | ~26k + 78k + 52k | the self-written goal stream: session goals before F, `CONSOLIDATE` `nextSessionGoal` after; agent, time; text in a sidecar | project labels (S6, Potts, model 07) |
| `actions` | 2.51M | computer-use turns without raw messages: agent, time, action type, bash head command, git verbs and repo names, URL domains, error and redaction flags, reasoning length | S7, tool drift, HH05, HH17 |
| `artifacts` | — | repos, sites, files and URLs, with first-seen agent and time, plus every later mention across chat, actions and memories | contagion, model 05, model 08, S7 |
| `memory_diffs` | 246,151 | per consolidation: length and line-level diff vs. the previous snapshot (added / removed / kept); text in a sidecar | HH12, H01 D5 and D10 |
| `embeddings/` (Phase 2) | — | chat, intentions, memory sections; topic and meaning clusters | S5, S6, models 10 and 11 |

**Design rules:**
- **Active time.** Use active time, not wall-clock time, as the default coordinate.
- **Regime-invariant action classes.** Map events to classes that mean the same before and after the March 2026 switch to always-on computer use (session start/stop before it, consolidation after) and across the shift to bash.
- **Keep the Claude Code agent's separate tables out of the core tables;** flag that agent.
- **No identities for human speakers** beyond the kind label (agent, human, automated).

### Built tables: key semantics (2026-10-03)
- **Codes.** `agent` is an int8 code (`roster.parquet`: agent, agent_id, name, model_string, lab, joined, left, claude_code, fine_tuned). `room` is an int8 code (`rooms.parquet`).
- **Human speakers** appear only as a 10-character hash (`human`). `speaker_kind` / `actor_kind` ∈ {agent, human, automated, system}; `automated` is the nudger/bot.
- **`events_core`:** event_index, t (UTC), pt_date, goal_no, regime, actor_kind, agent, human, action_type, room, tokens_in, tokens_out, message_id, session_id, pause_s.
- **`chat_core`:** message_id, t, pt_date, goal_no, regime, room, speaker_kind, agent, human, length, mentions (list of agent codes), n_urls. Text is in `chat_text` (message_id, text, urls).
- **`actions`:** t, agent, action (bash/left_click/…), bash_head, error, redacted, tok_in, tok_cache_read, tok_cache_write, tok_out, reasoning_chars. Token fields are null for ~42% of turns, whose provider shape carries no usage.
- **`intentions`:** event_index, t, agent, source (START_USING_COMPUTER / CONSOLIDATE). Text is in `intentions_text`.
- **`memory_stats`:** t, agent, n_chars, n_lines, n_headers, lines_kept/added/removed, jaccard_prev.
- **`calendar`:** pt_date, win_start, win_end, n_agent_events, goal_no, regime, window_s, gap_before_s, active_offset_s, documented_hours, weekday, holdout. Empirical windows match documented hours (medians 2.0/3.0/4.0/8.1 h); the undocumented first weeks ran ~2 h/day.
- **`rooms_timeline`:** agent, room, t_start, t_last, t_end.
- **`exposure`:** msg (row index into `chat_core` sorted by t), agent (recipient), lag_s (time to the recipient's next action). 2.1M rows; median 9 recipients per message; median lag 248 s.
- **`activity_bins`:** pt_date, minute, active_min, agent, talk, idle, consolidate, other_event, turns, paused, state (1 silent, 2 idle incl. declared pauses, 3 act, 4 talk). Agents on the roster only; Claude Code agent excluded.
- **`kicks`:** t, kind ∈ {human_message, automated_message, goal_kickoff, roster_join, roster_leave, natural_experiment}, room, agent, ref.
- **Holdout:** `calendar.holdout`, or `infra/shared/common.py: holdout_mask(pt_dates, goal_nos)`.
