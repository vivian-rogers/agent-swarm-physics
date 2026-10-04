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

### Work-output ledger (DQ4, 2026-10-04): `infra/shared/work_ledger.py`
What the swarm produced, read from the public git histories of every repo the agents worked in: 633 bare clones in `data/raw/repos/<host>/<path>.git` (1.47 GB; fetch record in `data/raw/repos/_source.md`). All time; mask with `holdout`. Docs and validation: `infra/data-quality/work_ledger.md`.
- **`work_commits`** (376k rows): repo × commit; author time `t`, `author_agent` / `author_kind`, files, lines, merge/branch/pages flags, message length only. **Agent work** = `canonical & ~imported & author_kind=="agent" & ~automated` (80k commits by 36 agents). **`automated`** (112k) = scripts, CI and cron under an agent identity (no turn within 5 min, or more commits than the agent's turns).
- **`work_daily`**: agent-days (zero-filled for active days) and repo-days: commits, lines, `distinct_files`, `new_repos`, deploy/publish counts, GitLab/GitHub API writes, raw push/commit command counts.
- **`work_api_writes`**: non-GET `glab api` / `gh api` / curl calls recovered from `artifact_commands_text`. Content writes are already commits (85% leave one within 10 min); don't add them.
- **`work_repos`**: inventory, fetch result, history summary, `has_site`. **`work_outcomes`**: goal-specific descriptive outcomes (#20 posts, #23 games, #42 videos, site goals) with source and reliability.
- Validation: 92% of commit hashes printed in agents' commands are in the histories (95% where fetched); author agrees with the committing agent 99.6%. Dense from #30 (2026-02) on; earlier periods barely used git, so a zero there is ambiguous. 1.6% of write mentions are in private or deleted repos. Line stats cover 56% of work commits (blobless big repos): use commits and `distinct_files` as the main size measures.

### Ground-truth labels (DQ6, 2026-10-04): `infra/shared/ground_truth.py` → `ground_truth_labels.parquet`
2,288 rows, 53 kB, codes only: one agreed answer key for detector validation. #12 teams/judges/results/phases; #26 election phases, official tallies, ballots, leader terms and H11's declarations; #34 saboteur agent-days (holdout); #35 lead designers; #44/#45 leader and checkpoints; #51 roles, role classes, rival and opposed pairs; operator room assignments (#35–#51) and system room presence. Columns: `goal_no`, `label_kind`, `unit`, `agent` / `agent_a`, `agent_b`, `value`, `detail`, `t_valid_from/to` (UTC), `source_kind`, `source_ref`, `confidence`, `derived_by`, `conflict_group`, `preferred`, `holdout`. **Use `preferred & ~holdout`.** Docs, conflicts and validation: `infra/data-quality/ground_truth_labels.md`.

### Embedding robustness pack (DQ5, 2026-10-04): `infra/data-quality/embedding_robustness.md`
Second model `Alibaba-NLP/gte-modernbert-base` (768-d, fp16, pinned revision; same inputs as bge: 2,000-char cut, 256 tokens), different lineage from bge-small. Loaders in `infra/shared/embed_models.py` (`statement_embeddings`, `load_whitener(regime, dim, model)`, `agent_vectors(level, model, variant)`, `goal_vectors`).
- `embeddings/{chat,intentions}_gte_modernbert.npy`, `agent_{day,win30}_vec_gte_modernbert.npy`, `whitening_gte_modernbert_<regime>.npz`, `goal_vectors_gte_modernbert.npy` (`build_embeddings_v2.py`).
- `embeddings/statements_{white32,style_resid32,style_resid_period32}_<model>.npy` and `agent_{day,win30}_{white32,style_resid,style_resid_period}_<model>.npy`: 32-d whitened, style-residualized within regime or within goal period (non-holdout fit; `style_resid.py`). **Use `style_resid_period` for identity, family or role claims** (it removes H13's family field: 8/16 → 1/16 units significant, in both models, while goal-period classification rises 0.75 → 0.90).
- `statement_flags.parquet` (rows = statements): lengths, token counts, exact repeats, `self_repeat` / `cross_echo` / `templated` per model (bge 0.95, gte 0.938 rate-matched), and `_both` consensus flags (`statement_flags.py`).
- `embeddings/agreement_gte_modernbert.{parquet,json}` (`embedding_agreement.py`): agent-day aggregates are robust across models (CKA 0.91, pair cosines ρ 0.91), statement-level geometry is not (10-NN overlap 0.26); #51 is the least robust period.

### Reply threading and stance labels (DQ2, 2026-10-04): `infra/shared/reply_threading.py`
Doc (pre-registration, amendments, schema, validation, limits): `infra/data-quality/reply_threading.md`. Jev zero-shot labels, $7.90.
- **`reply_pairs`** (536,673 rows; codes only): for each agent message B, the K = 3 most plausible parents A visible to its author (context-ledger `t_call` cutoff; H18 rule as fallback for ~2.6k messages), plus placebo pairs (`pair_set` = invisible: A during B's call; reversed: A after B). Labels: `p_reply` (direct reply), stance probabilities (supports / opposes / asks / neutral), opposition subtype; H37's labels attached in `h37_*` columns. `parent` = best labelled candidate with p_reply ≥ 0.5 (75,266 messages; 37% / 48% / 54% in regimes I / II / III).
- **`reply_graph`** (34,548 rows): replier → target (−1 human, −2 automated) per day and per period, soft (sum of p_reply) and hard (parent counts), stance soft/hard counts, and mention counts for comparison. Holdout flagged.
- **Validation:** reply κ 0.56 (random) / 0.61 (reweighted); p_reply ≥ 0.8 → 93% replies on a blind check. Stance κ 0.44. #12 opposite-team debaters "oppose" in 33% of replies vs 6% within teams (p = 0.0005).

### Period-affordance catalog (DQ9, 2026-10-04): `infra/shared/period_affordances.py` → `period_affordances.parquet`
One row per `period_units` unit (109; 40 kB): what the unit offers for period-native tests. Size and time (N, documented and empirical active hours), rooms, step changes (`ne_inside`, `data_steps`, joins, room and hours changes), kicks (nudges, bookends, human messages and speakers), DQ1 context counts (calls, forced erasures, voluntary consolidations), DQ6 ground-truth counts by kind, DQ4 outcomes, hand-coded structure flags (`has_teams`, `has_votes`, `has_roles`, `has_rival_pairs`, `has_checkpoints`, `has_forks`, `has_leader`, `has_private_goals`, `has_room_goal_split`, …), and `native_for` (hypotheses whose recommended native tests use the unit). **Event-derived columns are null on holdout units.** Human-readable catalog and the H01–H58 cross-index: `hypotheses/hypohypotheses/period-affordances.md`; docs: `infra/data-quality/period_affordances.md`. `--validate` reconciles every count with its source.

### Simulator, null library, estimates table, holdout ledger (DQ8, 2026-10-04)
Docs: `infra/data-quality/simulator_and_nulls.md`, `estimates_schema.md`. Tests: `infra/shared/tests/test_simulate.py`, `test_nulls.py`.
- **`simulate.py`**: village-skeleton simulator. `extract_skeleton(unit_id)` takes a real non-holdout `period_units` unit's structure (no text; held-out units raise); `simulate(sk, seed, **preset(...))` plugs in dynamics (rate-matched independent agents, global/room/time-of-day/day fields, day-edge drive, kinetic Ising with read-out delay, multivariate Hawkes with parents, O(32) vector spins / DeGroot, Potts herding waves, stalls, field or catalytic kick responses) and returns frames in the shared schemas, so any pipeline runs unchanged on synthetic input, plus `Sim.truth`.
- **`nulls.py`**: surrogates (`crossday`, `circshift`, `block_shift`, `room_relabel`), placebo designs (`placebo_dates`, `lever_design`, `crossday_message_placebo`), signed-graph nulls (`agent_field_null`), masks (`all_present_window`, `explained_silence_mask`, `stall_mask`), statistics. **`null_sizes.parquet`** (+ `infra/data-quality/null_sizes.json`): false-positive rate per null × statistic × nuisance (100 reps × 49 surrogates).
- **`per_period_estimates.parquet`** (`estimates.py`): one row per (hypothesis, period unit, statistic, channel, method, role); 914 rows backfilled from 30 hypotheses. Pipelines should call `write_estimates`; held-out rows only with `confirmatory=True`.
- **Holdout ledger** (`holdout_ledger.py` → `infra/data-quality/holdout_ledger.json`): every planned or executed confirmatory use, by hypothesis × target × modality × estimator family. Call `check()` before any confirmatory run and `record_run()` after.
- **`activity_bins_fixed.parquet`**: the corrected activity_bins (see Known issue), same schema and rows. `build_derived.py` itself is fixed as of 2026-10-04; the main table is rebuilt in DQ7.

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

### Context ledger (DQ1, 2026-10-04): `infra/shared/context_ledger.py`
Docs and validation: `infra/data-quality/context_ledger.md`, `context_ledger_validation.json`. All days, `holdout` flagged, message ids only (no text). About 217 MB; the full build takes ~1 min at 2 threads.
- **`call_windows`** (2.60M rows): one row per model call. `t_call` is when the call's context was assembled: measured for Gemini (19% of calls, from HTTP headers), otherwise calibrated (chained computer-use calls: previous end + 1.7 s; after a timer pause: expiry + 3.2 s; scheduled chat-mode calls: first record minus latency), with bounds, `start_src` and `start_conf`. `gap_kind` says what sits between calls (busy / pause / after_summary / marker / long_prev / first_of_day).
- **`context_ledger_turns`** (2.60M): per call, the chat items that newly entered its context by kind (agent / human / nudge / pause_resume), @-mentions, `k_since_talk` (H18's backlog, corrected), `k_ctx`, reset flags (`reset_forced` = the 41-turn cap, NE41; `reset_consol`), the 200-event cap after 2026-06-11, and outage overlap.
- **`context_ledger_items`** (2.10M): one row per (receiving call, message_id), with sender, kind (agrees with `kicks_classified`), `age_s`, mention, `during_prev`, `uncertain` (21%) and `omitted` flags.
- **Visibility rule:** a message is new at call c iff it was posted in the recipient's room by someone else at or after the previous receiving call's `t_call` and before c's. A pause or long tool call makes arrivals visible to the *next* call. Windows tile time, so each (message, recipient) pair goes to exactly one call. The Claude Code agent is excluded as a recipient (as in `exposure`).
- **Validation:** 0 consistency violations; 0 mismatches in brute-force recounts. The Claude Code input stream enters at exactly the predicted call 85% of the time (91% within one call). Prompt-token jumps track new-item characters (r 0.30 vs 0.03 for the naive rule where they disagree).

## Known issues
- **`chat_core.mentions` is polluted: use `chat_mentions_clean.parquet` instead** (found by H04; root cause found 2026-10-03). `o1`'s alias set was empty (names under 4 characters were dropped), and the empty regex matched almost every message: 175k of 183k messages carry a spurious `o1`. **Fixed** in `common.mention_regexes` (o1 and o3 case-sensitive; agents with no alias skipped). `infra/shared/build_mentions_clean.py` writes the sidecar `chat_mentions_clean.parquet` (chat_core row order: `message_id`, `mentions_clean`, `mentions_roster` = also restricted to that day's roster); 342k → 168k mentions. chat_core itself is rebuilt by `scan_tables.py` once running analyses finish. Analyses that only looked at mentions of *current* agents were unaffected; anything counting "any mention" or mentions per message was not.
- **`automated` speaker** covers the daily "pausing / resuming the village" messages as well as the nudger; separate them by text before treating `automated` as nudges. Shared `kicks_classified.parquet` does this: `nudge` vs `pause_resume`.
- **Memory snapshots precede their consolidation event** by microseconds (found by H15): join a CONSOLIDATE event to its memory snapshot with a backward or nearest as-of join, never forward.
- **Synchronized lulls** (≤ 1 active agent) cover 0–42% of minutes per period and drive much of the collective co-activation (H02, H12). Report lull-filtered variants of any collective statistic.
- **Self-repetition is mostly restatement, not copying** (DQ5, 2026-10-04; revises H12): exact repeats are ≈ 0% in regime III, and #38/#40 rates halve under the second model (#38: 20% of chat under bge, 10% under gte; agent-day top decile 71% vs 26%). Dedupe with `statement_flags.self_repeat_both` to remove copies, or with either model's flag to remove restatements, and report both. Original H12 note: in #38–#40, 16–60% of an agent's daily chat was flagged as near-copies (bge cosine > 0.95).
- **Statement-level embedding geometry is model-dependent** (DQ5): clusters, nearest-neighbour graphs, copy chains and per-statement projections change between bge and gte (10-NN overlap 0.26; whitened CKA 0.70). Agent-day and window aggregates are robust (ρ 0.88–0.91). Report statement-level results with both models. Negation is not fixed by gte.
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
- **Use the context ledger for visibility** (DQ1, 2026-10-04): `exposure.lag_s` overstates the time to visibility in *every* regime (median 131/179/290 s vs 18/19/50 s in regimes I/II/III), and H18's previous-record call-start rule mislabels 65–70% of "invisible" messages (PAUSE windows in regime III, scheduled chat-mode calls in I/II, first calls of the day). The ledger's `call_windows` / `context_ledger_items` are the fix. Original finding below.
- **H18's call-start visibility rule mislabels messages that arrive during a PAUSE or long tool call** (H29): 39–70% of regime-III "invisible" rows are of this kind, and the agent's next call does see them. H08's read-out rule (call start = pause expiry after a pause turn) handles pauses; long tool calls remain ambiguous until the context ledger's `call_windows` exists. H18's failed placebo is partly this, as well as ongoing exchanges (H08).
- **Recency confound in seen-vs-unseen content tests** (H29): content similarity to a message falls 5–23× as the message ages from under 10 s to over 20 min, so the messages closest in time to a reply look like influence whether seen or not. Compare visible and invisible messages within matched age bins.
- **H11 project labels are not bit-reproducible** (H31): `modal()` breaks ties via `group_by` without `maintain_order`, so about 1% of labels flip between rebuilds. **Fixed** in shared `project_states.parquet`: exact ties now go to the earliest first-seen project, then the name, so rebuilds are byte-identical. 633/7,802 W30 labels differ from H11's files, mostly renumbering; see the module notes above. H11's own confirmatory run should use the fixed version.
- **Spectral gaps in broadcast rooms are volume proxies** (H31): the binary-graph λ₂ ≈ N/(N−1), and the weighted λ₂ tracks message volume (r = 0.87). Decompose into volume and structure (volume/λ₂) before reading λ₂ as topology.
- **Day-level fluctuation statistics fire on roster and day-length changes** and on returns from gaps (H36). A trailing robust z with trimmed SD needs a consistency factor (0.70 at 10 baseline days), or z is inflated about 1.4×.
- **Sign-shuffle and per-pair FDR nulls are anti-conservative on signed reply graphs** with agent effects removed (H37): 10–28% false alarms under agent effects only, 100% at #51's structure. Use the calibrated ordered-logit agent-field null (`hypotheses/H37-stance-spins/analysis/calibrate.py`; size 0.04).
- **Jev zero-shot stance over-calls "oppose"** (H37): precision oppose 0.30, neutral 0.96, support 0.65 against blind labels (sign κ ≈ 0.56 population-weighted). Many "opposes" are task corrections or polite declines. Raw negative share has a label-noise floor of about 0.065; never alarm on it alone.
- **The `automated` speaker winds down in two steps** (H39, H30; dates corrected by H35 and `kicks_classified`; not in the CHANGELOG): the daily pause/resume bookends stop after **2026-08-05**, nudges after **2026-08-20**. Catalogued as NE43. Anything that uses nudges or the operator schedule (H04, H16, H38, H39) must treat #51 after 08-21 as a different regime of drive.
- **Controls that condition on a kick-free future are biased for targeted levers** (H39 synthetic null): requiring control episodes to stay kick-free afterwards manufactured a field effect at p = 0.01. Select controls on past information only and cut both arms at the next kick.
- **H01's goal vectors for #38's two rooms are swapped** (found by the 2026-10-03 consolidation): in `data/processed/H01-emergent-superagents-exist/goals_raw.npy`, the row labeled #best (room 2) holds the #rest kickoff embedding, and vice versa (cosine 1.000 to the other room's text). The likely cause is `--reuse-goal-emb`, which reloads vectors saved by an earlier run whose `group_by("room")` order differed; only the row count is checked. H20 and H32 read the same file. Any #38 per-room goal-field statistic should be rechecked with shared `embeddings/goals.parquet` (`kind == "kickoff_room"`).
- **The operator resume regex misses 4 bookends** ("resuming for today"; H38's `RESUME_RX`, used by `outages.py` for scheduled minutes). `kicks_classified` matches them (`resum\w* (the village|for today)`). Effect on `outages` is negligible; kept for identity with H38.
- **H12's lull filter biases variance-ratio statistics** (H25 synthetic): dropping every minute with ≤ 1 active agent truncates the distribution and gives VR bias −0.37 at g = 0 when N ≤ 6. Use the null-calibrated per-minute stall mask (`hypotheses/H25-criticality-dial/analysis/dial.py: find_stalls`) or H38's agent-state conditioning. Dropping VR ≤ 0 days instead of flooring them biases g upward by about 0.25.
- **Days with ≤ 4 active agents give optimistic bootstrap SEs** (H25), which then dominate fixed-effect means; use random-effects means or require N ≥ 5.
- **Split-half variances of rare talk events are unreliable at day level** (H26): some split-half correlations exceed 1. Use ≥ 30-min windows or pooled estimators for talk.
- **H34's cascade trees use H18's call-start visibility rule**, so their parent assignment inherits the pause / long-tool-call misclassification (H29). Re-run on the context ledger's visibility in the re-evaluation wave.
- **#26 had two elections** (DQ6): a 01-05 approval vote → 9–9–9 tie → 7–1–0 runoff (about 100 s), and a 01-09 confirmatory re-election (9–0). H11's "runoff jump" and runoff snapshot, and H31's E-V consensus time, measured the 01-09 vote. Use `ground_truth_labels` `phase` / `ballot` / `tally` rows and analyse per election round.
- **`agent_goals` is a snapshot** (DQ6): Claude Opus 5's first #51 role (game dev, 07-24 → 07-29) was overwritten; an operator message recovers it. H22, H37 and `goal_fields` treat Opus 5 as roleless for those days. Use `ground_truth_labels`.
- **Commits under agent identities are not all agent work** (DQ4): 112k of 192k agent-identity commits are automated (scripts, CI, cron), e.g. an 81.6k-commit cron stream under GPT-5's identity still running on 2026-10-04. Filter with `work_commits.automated`.
- **Never isolate kicks on future kicks** (H30, H39): the nudger re-fires on agents that stay idle (52% within 60 min in G51), so requiring a kick-free future selects the kicks that worked and inflates their effect (H04's A30 1.66 vs 0.59–1.04 over all nudges). Adjust for past kicks and future *undirected* kicks only, and include a day fixed effect: per-kick responses otherwise carry day-level activity shifts (H30 synthetic: Cochran's Q over-rejects at 30%).
- **`h04lib.window_sum` sums in int64** (H30), so it truncates float inputs. About 5% of nudges fall in the last 30 min of the day and drop out of 30-min response windows.
- **Reply and stance labels (DQ2):** `p_reply` is calibrated but partly reflects thread membership (strictly invisible pairs keep ~75% of the score) and ignores direction, so always restrict to `pair_set = cand`. **Pair-level "opposes" precision is 0.08** (≥ 5.2 of its 5.7 points are noise): use soft sums, group contrasts and confidence ≥ 0.8, never single labels. `opp_type` is unvalidated (κ 0.11, n = 16). `reply_graph` is a primary-parent graph (the top 3 hold only 28% of reply links). Graph-level nulls: H37's calibrated agent-field null.
- **Mention-based "responses" are superseded** by `reply_pairs` (`parent`, `p_reply`) and the context ledger. A mention is not a reply: 35% of top-1 pairs where B names A's author get p_reply < 0.5. H18's placebo failure was mostly the visibility rule: under the ledger, strictly invisible pairs score 0.24 vs 0.32 for matched visible ones (0.21 vs 0.59 in regime III).
- **A nudge's target is its leading @** (H35): 29% of nudges also mention other agents, so mapping every mention to a target (H04, H16, and `kicks_classified.targets`) adds false targets (239 in G51). Use the leading mention as the primary target; a `primary_target` column is queued for `kicks_classified`.
- **The 2026-06-11 pause default change (12 h → 5 min, NE44)** creates two response regimes for any directed message: before it, a message wakes a sleeping agent at any trap age; after it, agents read at the next short timer gate, and only early re-pauses respond (H35).
- **Circular-shift nulls within agent-day are not pure bias floors** on real data (H35): they keep real "which agent-days" information. Subtract a full-permutation null for marginal terms.
- **`h16lib` inserts its analysis folder at `sys.path[0]`** (H35), so importers' modules with the same names (e.g. `run_period.py`) collide. Import it with importlib or rename modules.
- **Regime-I visibility is doubtful under the old call-start rule** (H28): before NE09, link → switch co-timing is as fast as after it (2.5 vs 7.5 min), which contradicts the H18 rule's regime-I timing. The context ledger models scheduled chat-mode calls in regimes I/II (low-confidence starts, `start_conf`); re-check with it.
- **NE dates the record contradicts** (DQ9): the first nudge is 2026-02-13, not 02-10 (NE10); the bookends end 2026-08-04 PT, two weeks before the nudges (NE43 is two steps); public chat closed ≈ 2025-07-01 (dates NE39). **`period_units` has no split at NE43's steps** (51g spans both): add 08-05 and 08-21 splits in the next `period_units` rebuild.
- **NE06 is not a clean Google-only change** (DQ9): the CHANGELOG lists all-agent system-prompt changes on the same days (2025-11-20/21).
- **`activity_bins` dropped about half of all events** (DQ8, 2026-10-04; confirmed by the coordinator): events were joined to the minute grid on an `active_min` key computed differently for events (`(offset + Δt)//60`) and the grid (`offset//60 + minute`), so about (`active_offset_s mod 60`)/60 of each day's events vanished (median day keeps 53% of talk events, worst days 1–2%; totals 90,765 vs 170,870 talk events, 1.30M vs 2.50M turns; 24% of agent-minute states change). **Use `activity_bins_fixed.parquet`** until DQ7 rebuilds `activity_bins` and `outages` / `stall_minutes` / `reasons` (which inherit the bug: joint silences over-counted on high-offset days). `build_derived.py` is patched (join on pt_date, minute, agent) and reproduces the fixed table exactly. **Every activity/talk statistic built on activity_bins needs re-running**, including H02, H04, H05, H08, H09, H12, H13, H15, H19, H22, H25, H26, H30, H33, H36, H38 and the executed holdout runs of H02, H04 and H05.
- **Synchrony nulls need trimming and masks first** (DQ8 size table): on whole-day grids block-shift and circular-shift nulls reject 28–34% of independent swarms; trim to the all-present window before drawing surrogates. No surrogate separates a same-day shared field from coupling. λ₁ against the cross-day edge picks up the shared schedule (size 0.19); use the block shift. Room relabeling is anti-conservative under room-specific drives (0.82). Lever designs need past-only eligibility, presence masking and uncut windows (window means cut at the next kick: 0.43). Per-pair FDR on signed graphs is anti-conservative; use the agent-field null. Cross-day message placebos fail under day-level drives (1.00).
- **Style depends on context position** (H46): it drifts as the context fills and resets at erasures, which bears on H12 self-repetition, H13 family fields and anything that averages style over sessions. The digit and uppercase style features are topic-adjacent.
- **Erasure-pair tests need fine time-gap strata** (H46 synthetic): 0.25-decade gap bins left a recency bias (false "content moves" in 58–70% of null replicates); 0.05-decade bins remove it. Cross-validated R² with two-way demeaning is inflated at small samples: report it null-corrected (permutation).
