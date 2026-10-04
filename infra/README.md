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

### Artifacts tables (built by H07, 2026-10-03): `infra/shared/build_artifacts.py [scan|build]`
One orjson pass over raw `computer_use_turns` (scan 184 s, 2 processes; build 25 s). All time, **including the holdout**: mask before exploring.
- **`artifacts`** (13,186 rows, 0.45 MB; no text): one row per artifact.
  - Columns: `artifact` (int32), `kind` (repo / site / file / domain), canonical `name`, `host`, `domain`, `parent` (file → repo; site → repo where derivable), `first_t`, `first_agent` (int8; null for humans), `first_speaker_kind`, `first_source`, `last_t`, `n_chat`, `n_action`, `n_intention`, `n_mentions`, `n_agents`.
  - Counts: 2,404 repos, 1,355 sites, 5,747 files, 3,680 domains.
- **`artifact_mentions`** (573,227 rows, 5.0 MB): artifact, t, agent, speaker_kind, `source` (chat 23,438 / action 536,399 / intention 13,390), `how` (url, bare, output, cwd, session_cwd), `verb` (git push/clone/fetch, gh pr view, deploy, fetch, …), room and message_id (chat only), `ref_index` (event_index for intentions; sidecar row for actions).
- **`artifact_commands_text`** (sidecar, 739,733 rows, 23 MB): row, t, agent, session, act (bash / type), verbs, `cmd` (relevant non-comment lines, ≤ 300 chars; null for rows kept only for `cd` or restart tracking), urls, dirs, restart, clone_src, clone_dir, out_urls, `out_hashes` (commit hashes from git output), new_branch, error.
- **Canonical names:**
  - repo: `github.com/o/r` or `gitlab.com/ai-village-agents/village/<p>` (API URLs map to their repo);
  - file: `<repo>:<path>`, plus Google Docs / Drive ids;
  - site: `o.github.io/r`, GitLab Pages hosts, hosting platforms;
  - domain: the registrable domain;
  - localhost and private IPs dropped.
- **Caveats:**
  - Directory-based resolution is only 0.89 precise (`cwd`) and 0.81 (`session_cwd`) against git-printed remotes; strict uses should keep `how ∈ {url, output, bare}`.
  - Raw turns are out of time order within a session (934k inversions), so the working directory is resolved after sorting.
  - The Claude Code stream and memories are not scanned.
- **Repo clones** used by H07 live in `data/raw/repos/` (bare, `--filter=blob:none`, plus blobs fetched by id; 5.8 MB; re-fetch commands in its `_source.md`).

### Shared pipeline (consolidated 2026-10-03): `infra/shared/build_all.py`
One entry point runs every shared builder in dependency order, one at a time, each in its own process with thread caps (default 2):
`scan_tables → build_derived → build_embeddings (skipped when present) → build_agent_vectors → build_mentions_clean → build_artifacts → turn_errors → goal_fields → period_units → behavior_states → project_states → kicks_classified → text_features → outages`.
- `uv run python infra/shared/build_all.py --list` shows steps, commands and which outputs exist.
- Options: `--only a,b`, `--from NAME`, `--skip-existing`, `--force-embeddings`, `--dry-run`, `--tests` (runs `infra/shared/tests/test_*.py`), `--threads N`. Per-step timings print at the end and go to `data/processed/shared/build_all.log`.
- `goal_fields` and `build_embeddings` run under `uv run --with sentence-transformers` (offline HF cache, MPS or CPU).

Every module below was moved out of a hypothesis folder and verified against the original output. The originals still run unchanged and will become thin shims later. All tables cover **all days**, with a `holdout` flag: they are measurements, so **exploration must filter `holdout == False`**. No new text is stored. The new tables total 47 MB.

| Table (data/processed/shared/) | Builder | From | Serves | Verification |
| --- | --- | --- | --- | --- |
| `embeddings/goals.parquet` + `goal_vectors.npy` | `goal_fields.py` | H01, H10 | H01, H10, H20, H32 (read H01's vectors) | H10 equal to fp16 (max \|Δ\| 2.4e-4); H01 111/113 rows; H01's 2 #38 room rows are swapped (an H01 bug inherited by H20/H32) |
| `states_turn`, `states_min` | `behavior_states.py` | H14 | H14, H17, H39 | identical to H14 (non-holdout rows) |
| `project_states` | `project_states.py` | H11 | H06, H11, H27, H28, H31 | identical in untied windows; ties now deterministic |
| `period_units`, `period_step_changes` | `period_units.py` | H01/H12/H13, H03/H18, H16, H17, H22 | everyone | one rule; disagreements listed by `--compare` |
| `kicks_classified` | `kicks_classified.py` | H04, H16 | H04, H08, H16, H35, H39 | H04 human count equal, nudges 1,071 vs 1,070; H16's 5 classes equal |
| `text_features` | `text_features.py` | H13 | H13 | H13 agent-day aggregates exact |
| `turn_errors`, `sessions`, `actions_bash_head_fixed` | `turn_errors.py` | H38 | H25, H26, H36, H38 | equal to H38; sidecar aligned to `actions` |
| `outages`, `stall_minutes`, `reasons` | `outages.py` | H38 (+ H09's idle-spell rule) | H25, H26, H36, H38 | equal to H38; idle spells equal to H09 |
| (functions) | `spectra.py` | H12 | H12, H33 | tests reproduce H12's synthetic numbers exactly |
| (functions) | `copy_info.py` | H07 | H07, H23 | tests (analytic cases, equivalence with h07lib) |

Each builder takes `--verify` (or `--compare` for `period_units`) to rerun its check against the original, read-only.

- **`embeddings/goals.parquet`** (249 rows) + **`goal_vectors.npy`** (fp16, 384-d raw bge-small; the mean of unit chunk embeddings, *not* renormalized).
  - Columns: `gid` (row in the .npy), goal_no, `kind`, room, agent, first_day, win_start, valid_from, valid_to, regime, holdout, n_msgs, n_rooms, n_chunks, n_chars, fallback, `ref` (raw agent_goals id).
  - `kind` values:
    - `goal`: the village_goals text in ≤ 700-character chunks (H10).
    - `goal_whole`: the text as one string (H01).
    - `kickoff`: all rooms combined (H10).
    - `kickoff_room`: one row per room (H01).
    - `agent_goal`: the #51 private role, `name. description` (H01).
  - Kickoff rule: human messages of ≥ 250 characters within [−10, +45] min of the window start on the goal's first active day. If there are none, the day's longest such message (`fallback`). Sentences about the previous goal are stripped. Goal #2 has no kickoff.
  - Whiten downstream with `common.load_whitener(regime)`.
- **`states_turn`** (2.67M rows) / **`states_min`** (1.47M): H14's rule-based action-class states. These are *not* the Jev `behavior_states_draft_*`.
  - Scaffold artifacts are removed: mirror turns within 2 s of their event, and the forced `mouse_move` after context boundaries.
  - Gap logging is handled: WAIT and CONSOLIDATE are back-filled from the previous record, and a PAUSE fills forward.
  - Schemes: `act` (11 fine classes), `coarse` (browse / type / shell / chat / idle / consolidate; −1 = removed), and `lump4` (work / chat / idle / consolidate).
  - `states_min` adds `in_span`: the minute lies between the agent's first and last record of the day. Outside the span, "idle" is really absent.
  - `build(days)` returns exactly H14's tables.
- **`project_states`** (w_min ∈ {15, 30, 60} × sources ∈ {all, action}): the modal project per agent per window, from strict artifact mentions (`how ∈ {url, output, bare}`). Files and sites map to their parent repo.
  - Columns: goal_no, pt_date, day, win, agent, room (at the window midpoint), `project` (canonical artifact name), n, n_all, `n_tied`, `label` (0 = other, 1..8), holdout.
  - Labels: the top ≤ 8 projects with ≥ 2% of agent-windows, ranked on the period's non-holdout rows.
  - Ties go to the most recent mention. **Exact ties** (n_tied > 1; 2.6% of 30-min windows) go to the project first seen earliest in the dataset, then to its name. H11's choice in exact ties varied from run to run (unstable sort).
  - At W = 30, 633/7,802 labels differ from H11's current files:
    - 111 rows are tied windows that now pick a different project;
    - 499 are pure renumbering, among projects within a few agent-windows of each other;
    - 52 rows (#8, #17, #20, #21, #24, #25, #40) change "other" membership.
  - Helpers: `window_table(cal, W)` (all windows, for circular shifts) and `projects_table(df)`.
- **`period_units`** (109 units; 24 of 51 periods split; 30 one-day units) and **`period_step_changes`**. **The one rule:** a goal period's active days split at every step change, where a change dated D starts a unit on the first active day ≥ D. The changes are:
  - every dated row of `hypotheses/natural-experiments.md`;
  - roster joins and leaves (Claude Code agent excluded);
  - changes in the structural room set (rooms that are the modal room of ≥ 2 agents that day);
  - documented-hours changes;
  - holdout boundaries;
  - intra-day restarts: ≥ 60 min with no agent record and ≥ 30 min / ≥ 100 records on both sides (06-18 in #4, 06-29 in #50; such a day is listed in both units).

  Columns: unit_id (`51c`, …), goal_no, seq, start / end (UTC), first_day, last_day, n_days, days, reason, reasons, n_agents (roster agents active in the unit), n_roster, rooms, regime, holdout, n_offgaps (stray-record gaps that don't split).
- **`kicks_classified`** (105,830 rows): t, `kind`, subkind, targeted, room, speaker, `targets` (from `mentions_roster`), n_targets, `recipients` (from `exposure`), msg, message_id, goal_no, pt_date, holdout, ref. The kinds:
  - `nudge`: automated message naming roster agents, or @-addressed (3 messages have unparsed targets);
  - `pause_resume` (subkind `pause` / `resume`): the daily bookends, which never name agents;
  - `human_message` (subkind `kickoff` / `mention` / `plain`);
  - `mention`: an agent message naming another roster agent;
  - `goal_kickoff`: the village_goals start;
  - `automated_other`: 0 rows.

  H16's (message, recipient) classes are `explode("recipients")` crossed with whether the recipient is in `targets`.
- **`text_features`** (173,493 agent chat messages; no human or automated rows): H13's 20 style features (`f_*`, Float64), `words`, and 37 marker counts (`m_*`). Keys: message_id, msg, agent, t, pt_date, goal_no, room, holdout.
- **`turn_errors`** (153,245 rows) / **`sessions`** (78,362 computer-use sessions): H38's error categories for every turn with an `error` or `system` string.
  - Columns: t, agent, session, `err_cat`, `sys_cat`, pt_date, holdout.
  - Categories: none / timeout / vm / resource / network / git_info / progress / tool_use / other. The infrastructure categories are timeout, vm, resource and network.
- **`actions_bash_head_fixed`** (2.51M rows, row-aligned with `actions.parquet`):
  - Columns: row, t (for an alignment check), `bash_head_fixed`, `error_class`, `system_class`.
  - **Use `bash_head_fixed` instead of `actions.bash_head`**: regime-III coverage rises from 12.8% to 99.6% (regimes I/II from 96.5% to 99.8%); old non-null heads are unchanged.
  - **Use `error_class` instead of `actions.error`**: of the flagged turns, 39% are `git_info`, 1.4% `progress` and 16% infrastructure.
  - Note: a command whose first line is `cd X` (no `&&`) gets head `cd`.
- **`outages`** (3,590 joint-silence runs), **`stall_minutes`** (98,863 day-minutes), **`reasons`** (561,019 silent agent-minutes with a reason): H38's tables (definitions in `outages.py` and the H38 card). The idle spells are recomputed with H09's rule, so nothing depends on a hypothesis folder. `village_off` marks runs with ≥ 10 min of K = 0.
- **`spectra.py`** provides:
  - `corr_eig`, `overlap_eig`, `mp_edge`, `bartlett_tau`;
  - the `crossday_surrogate` and `circshift_surrogate` nulls;
  - `spectrum_test`, `lull_filter`, `mode_summary`, `label_separation`;
  - the participation-ratio estimators `pr_from_samples`, `pr_rarefied` (PR30), `pr_balanced` (PRday) and `between_pr`;
  - `near_dup_share` and `near_dup_share_by`.
- **`copy_info.py`** provides `mi_parts`, `decompose` (with the shuffle null), `transform_test` (the conditional null), `vertical`, `horizontal` and `set_stats`.

## Known issues
- **`chat_core.mentions` is polluted: use `chat_mentions_clean.parquet` instead** (found by H04; root cause found 2026-10-03). `o1`'s alias set was empty (names under 4 characters were dropped), and the empty regex matched almost every message: 175k of 183k messages carry a spurious `o1`. **Fixed** in `common.mention_regexes` (o1 and o3 case-sensitive; agents with no alias skipped). `infra/shared/build_mentions_clean.py` writes the sidecar `chat_mentions_clean.parquet` (chat_core row order: `message_id`, `mentions_clean`, `mentions_roster` = also restricted to that day's roster); 342k → 168k mentions. chat_core itself is rebuilt by `scan_tables.py` once running analyses finish. Analyses that only looked at mentions of *current* agents were unaffected; anything counting "any mention" or mentions per message was not.
- **`automated` speaker** covers the daily "pausing / resuming the village" messages as well as the nudger; separate them by text before treating `automated` as nudges. Shared `kicks_classified.parquet` does this: `nudge` vs `pause_resume`.
- **Memory snapshots precede their consolidation event** by microseconds (found by H15): join a CONSOLIDATE event to its memory snapshot with a backward or nearest as-of join, never forward.
- **Synchronized lulls** (≤ 1 active agent) cover 0–42% of minutes per period and drive much of the collective co-activation (H02, H12). Report lull-filtered variants of any collective statistic.
- **Self-repetition:** in #38–#40, 16–60% of an agent's chat messages per day are near-copies of its own earlier text (H12). Dedupe within agent-day (cosine > 0.95) before content-diversity statistics.
- **`exposure.lag_s` uses `events_core` turns only,** so in regime III (computer-use turns live in `actions`) it overstates the lag to an agent's next turn. Use `actions` together with events for turn times (H18).
- **Mention-based "responses" are contaminated:** agents name senders whose message they could not yet have seen 3–10× more often than other room-mates (H18 placebo). Mentions partly reflect conversation state or co-addressing, not uptake of a specific message.
- **`actions.bash_head` is null for ~87% of regime-III bash turns** (H14): those commands start with a `#` comment line, and `BASH_HEAD` doesn't skip comments or blank lines. Regime I/II coverage is 96–97%. **Fixed in code** (`scan_tables.bash_head`; 2026-10-03), and the sidecar **`actions_bash_head_fixed.parquet`** (row-aligned) gives regime-III coverage of 99.6%: use its `bash_head_fixed` now. `actions.parquet` itself is rebuilt later with `uv run python infra/shared/scan_tables.py --only turns`, once running analyses finish; that also rewrites `roster.parquet` (same content), sorts stably, and leaves the other tables untouched.
- **Scaffold artifacts in `actions`** (H14): mirror turns (`pause`, `send_message_back_to_chat`, `search_history`, `move_to_room`) duplicate events within 2 s; a forced `mouse_move` follows ~85% of consolidations; CONSOLIDATE is logged at completion, ~3 min after the previous turn.
- **Calendar windows can span village-off gaps** (H16): e.g. #37 on 03-31 has a 755-min window containing a 513-min all-silent gap; also in #38 and on 6 days of #51. These affect censoring and swarm statistics. **Now tabulated** by H38: `outages.parquet` (one row per joint-silence run, cause shares, `village_off`, `at_day_edge`) and `stall_minutes.parquet`, **now in `data/processed/shared/`** (`infra/shared/outages.py`; identical to H38's copies). 84% of village-off minutes fall between the operator's pause and resume messages.
- **Minute-grid idle includes minutes before an agent's first and after its last action of the day** (H17): 80% of idle minutes in #37.
- **The Claude Code agent's `get_events` feed replayed 2025 history** from 2026-03-17 until it left (≈ one historical day per real day; H08). Any analysis treating its fetched events as current exposure is wrong after that date. Its Claude Code API payloads use Pacific-time locale text in `createdAt`.
- **Regime-I calls that produce chat may be unlogged** (H08): addressing peaks at turns the call-start rule classes as "in flight". Treat turn timing in regime I with care.
- **H18's placebo contamination** comes from recipients mid-exchange, who address senders they were already talking with, not from seeing messages early (H08).
- **Regime-III synchrony statistics need edge trimming** (H38): about two thirds of regime-III activity co-activation (H02 βJ₀, H19 g_eq; median f_scaffold 0.68) is agents starting and stopping together at the operator's daily resume and pause. The regime II → III rise in co-activation goes away under adjustment (NE14: +0.15 → +0.01). Trim each day to the window in which all present agents are running, or use H38's agent-state conditioning (`h38lib.gains`, variant `mask_scaffold`), before any synchrony statistic. Regime I is not affected (f 0.11).
- **`actions.error` means "stderr non-empty"** (H38): about 41% of flagged rows are benign git/curl output; only about 16% are infrastructure errors (timeout, VM/display, resource, network). Use H38's error categories, not the raw boolean: shared `turn_errors.parquet`, or `actions_bash_head_fixed.error_class`, which is row-aligned with `actions`.
- **H18's call-start visibility rule mislabels messages that arrive during a PAUSE or long tool call** (H29): 39–70% of regime-III "invisible" rows are of this kind, and the agent's next call does see them. H08's read-out rule (call start = pause expiry after a pause turn) handles pauses; long tool calls remain ambiguous until the context ledger's `call_windows` exists. H18's failed placebo is partly this, as well as ongoing exchanges (H08).
- **Recency confound in seen-vs-unseen content tests** (H29): content similarity to a message falls 5–23× as the message ages from under 10 s to over 20 min, so the messages closest in time to a reply look like influence whether seen or not. Compare visible and invisible messages within matched age bins.
- **H11 project labels are not bit-reproducible** (H31): `modal()` breaks ties via `group_by` without `maintain_order`, so about 1% of labels flip between rebuilds. **Fixed** in shared `project_states.parquet`: exact ties now go to the earliest first-seen project, then the name, so rebuilds are byte-identical. 633/7,802 W30 labels differ from H11's files, mostly renumbering; see the module notes above. H11's own confirmatory run should use the fixed version.
- **Spectral gaps in broadcast rooms are volume proxies** (H31): the binary-graph λ₂ ≈ N/(N−1), and the weighted λ₂ tracks message volume (r = 0.87). Decompose into volume and structure (volume/λ₂) before reading λ₂ as topology.
- **Day-level fluctuation statistics fire on roster and day-length changes** and on returns from gaps (H36). A trailing robust z with trimmed SD needs a consistency factor (0.70 at 10 baseline days), or z is inflated about 1.4×.
- **Sign-shuffle and per-pair FDR nulls are anti-conservative on signed reply graphs** with agent effects removed (H37): 10–28% false alarms under agent effects only, 100% at #51's structure. Use the calibrated ordered-logit agent-field null (`hypotheses/H37-stance-spins/analysis/calibrate.py`; size 0.04).
- **Jev zero-shot stance over-calls "oppose"** (H37): precision oppose 0.30, neutral 0.96, support 0.65 against blind labels (sign κ ≈ 0.56 population-weighted). Many "opposes" are task corrections or polite declines. Raw negative share has a label-noise floor of about 0.065; never alarm on it alone.
- **The `automated` speaker goes silent from 2026-08-21** (H39; not in the CHANGELOG): no nudges after 08-20 and no daily pause/resume bookends. Catalogued as NE43. Anything that uses nudges or the operator schedule (H04, H16, H38, H39) must treat #51 after 08-21 as a different regime of drive.
- **Controls that condition on a kick-free future are biased for targeted levers** (H39 synthetic null): requiring control episodes to stay kick-free afterwards manufactured a field effect at p = 0.01. Select controls on past information only and cut both arms at the next kick.
- **H01's goal vectors for #38's two rooms are swapped** (found by the 2026-10-03 consolidation): in `data/processed/H01-emergent-superagents-exist/goals_raw.npy`, the row labeled #best (room 2) holds the #rest kickoff embedding, and vice versa (cosine 1.000 to the other room's text). The likely cause is `--reuse-goal-emb`, which reloads vectors saved by an earlier run whose `group_by("room")` order differed; only the row count is checked. H20 and H32 read the same file. Any #38 per-room goal-field statistic should be rechecked with shared `embeddings/goals.parquet` (`kind == "kickoff_room"`).
- **The operator resume regex misses 4 bookends** ("resuming for today"; H38's `RESUME_RX`, used by `outages.py` for scheduled minutes). `kicks_classified` matches them (`resum\w* (the village|for today)`). Effect on `outages` is negligible; kept for identity with H38.
- **H12's lull filter biases variance-ratio statistics** (H25 synthetic): dropping every minute with ≤ 1 active agent truncates the distribution and gives VR bias −0.37 at g = 0 when N ≤ 6. Use the null-calibrated per-minute stall mask (`hypotheses/H25-criticality-dial/analysis/dial.py: find_stalls`) or H38's agent-state conditioning. Dropping VR ≤ 0 days instead of flooring them biases g upward by about 0.25.
- **Days with ≤ 4 active agents give optimistic bootstrap SEs** (H25), which then dominate fixed-effect means; use random-effects means or require N ≥ 5.
