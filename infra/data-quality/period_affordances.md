# DQ9: period-affordance catalog

**Code:** `infra/shared/period_affordances.py` (build; `--validate` reconciles with the sources; `--show` prints a summary).
**Table:** `data/processed/shared/period_affordances.parquet` (109 rows × 84 columns, 39 kB, zstd). Provenance key `period_affordances` in `data/processed/shared/_provenance.json`.
**Human-readable half:** `hypotheses/hypohypotheses/period-affordances.md` (one section per goal period, the leverage table, the hypothesis cross-index, corrections).
**Status:** built 2026-10-04 (UTC). Codes and counts only; no message text read or stored. Build ~10 s at 2 threads.

## Why
Most hypotheses ran one templated test on every goal period. The strongest round-1 results came from what a period uniquely offers (#12's drafted teams, #26's ballots, #51's roles, the 03-16 room cut, forced erasures). The re-evaluation adds 2–4 **period-native** tests per hypothesis (`QUEUE.md`, "Re-evaluation design rule"). This catalog says, per period unit, what ground truth, interventions, structure and outcomes exist, so agents can pick and design those tests.

## Table (one row per `period_units` unit)
| Group | Columns |
| --- | --- |
| keys | `unit_id`, `goal_no`, `seq`, `first_day`, `last_day`, `n_days`, `regime`, `holdout`, `by`, `mode` (goal-periods codes), `goal_slug` |
| size and time | `N` (roster agents active), `n_roster`, `doc_hours_per_day`, `doc_hours_total` (documented; all units), `active_hours_window` (calendar windows), `village_off_hours` (`outages.village_off`), `active_hours` (window − village-off) |
| rooms | `rooms_structural` (names), `n_rooms`, `has_rooms` (≥ 2 structural rooms), `transient_rooms` (onboarding, isolated, side rooms alive in the unit) |
| step changes | `reason` (period_units), `ne_inside` (NE ids landing in the unit by the period_units rule, plus NE43), `data_steps` (data-found dates, below), `n_roster_joins`, `n_roster_leaves` (launch roster excluded), `n_room_set_changes`, `n_hours_changes` |
| kicks and chat | `n_nudges`, `n_bookends` (operator pause/resume), `n_human_msgs`, `n_human_msgs_naming`, `n_human_kickoff_msgs`, `n_human_speakers` (distinct hashed humans), `n_agent_msgs`, `n_agent_mentions` |
| context (DQ1) | `n_calls`, `n_erasures_forced` (`reset_forced`, the 41-turn cap), `n_consolidations_voluntary` (`reset_consol & ~reset_forced`), `n_event_cap_hits` (NE22 cap) |
| platform | `n_village_off`, `n_infra_bursts` (`outages`) |
| structure (hand-coded) | `has_teams`, `has_votes`, `has_roles`, `has_rival_pairs`, `has_checkpoints`, `has_forks`, `has_leader`, `has_private_goals`, `has_hidden_roles`, `has_competition`, `has_room_goal_split`, `has_ext_event`, `has_operator_correction`, `has_isolated_newcomer_rooms`, `has_room_merge` |
| ground truth (DQ6) | `n_gt_rows`, `n_gt_structural_rows` (excluding room rows), `gt_kinds` (`kind:count`, preferred rows, room kinds excluded) |
| outcomes (DQ4) | `work_commits`, `work_committing_agents`, `work_distinct_files`, `work_new_repos`, `work_site_commits` (pages + site-default), `work_deploy_cmds`, `work_api_writes`, `work_commits_automated`, `active_agent_days`, `git_dense` (goal ≥ 30), `outcome_kinds`, `outcome_reliability` (`work_outcomes`), `outcome_narration` (outcomes known only from narration) |
| regime/scaffold flags (by date) | `rooms_era`, `forced_erasure_regime` (NE41), `event_cap_200` (NE22), `gitlab_era` (NE24), `private_plans` (NE26), `claude_code_present`, `cc_feed_replay` (H08), `nudger_era` (first to last nudge), `bookend_era` (first to last bookend) |
| index | `native_for`: hypotheses whose recommended native tests use this unit (the md cross-index inverted; non-holdout units only) |

**Typical use:** `pl.read_parquet(".../period_affordances.parquet").filter(~pl.col("holdout") & pl.col("has_votes"))`, or `.filter(pl.col("native_for").list.contains("H18"))`.

## Rules
- **Units** are `period_units.parquet`. A step change dated D lands in the unit holding the first active day ≥ D (the same rule).
- **Split days** (intra-day restarts: 2025-06-18 in #4, 2026-06-29 in #50): time-stamped rows (kicks, chat, calls, outages) go to the later unit from its start; day-level rows (work_daily, documented hours) go to the first unit; empirical hours are cut at the later unit's start.
- **Holdout:** every event-derived column (kicks, chat, calls, erasures, work, outages, empirical hours) is **null** on the 38 holdout units, and sources are filtered on `holdout == False` before any aggregation (chat_core has no holdout column, so its rows are kept only on PT days of non-holdout units). Kept on holdout units: setup metadata (N, documented hours, rooms, NEs, joins, hand-coded structure) and DQ6 ground-truth **counts by kind** (no label values were read; DQ6 already publishes these counts). `native_for` is empty on holdout units.
- **Hand-coded structure** (`GOALS`, `UNIT_OVERRIDES` in the script): flags mean the structure exists in the record (goal-periods.md, the NE catalog, the CHANGELOG, DQ6), not that it has been tested.
- **Work before #30** is an ambiguous zero (DQ4: git was rare); `git_dense` marks where it is a real measure. Filter automated commits (DQ4).

## Data-found step dates (`data_steps`)
Found by this build from counts only:
| date | step | evidence |
| --- | --- | --- |
| 2025-07-01 | public chat closed (estimate for the undated NE39) | human messages/day ~100 → ≤ 4, distinct human speakers ~16 → 1, between 06-30 and 07-01 (inside #6) |
| 2025-07-16 | human helpers B (CHANGELOG; no NE id) | #7 has 9–13 human speakers/day again |
| 2026-02-13 | first nudge in the record | NE10 is dated 02-10; before 02-13 the `automated` speaker posts only 2 bookends/day |
| 2026-08-04 | last daily pause/resume bookend | NE43 says bookends stop 08-21; from 08-05 every `automated` message is a nudge |
| 2026-08-20 | last nudge | NE43 |

`period_units` has no split at NE43 (it was added to the NE catalog after the units were built) or at 08-05: unit 51g (08-05 → 08-21) has nudges on 12 days and none on its last day. `period_affordances` lists NE43 in 51g's `ne_inside`.

## Validation (`--validate`)
Unit sums over non-holdout units reconcile exactly with their sources:
| check | catalog | source |
| --- | --- | --- |
| nudges | 1,071 | `kicks_classified` (non-holdout) 1,071 |
| human messages | 3,759 | 3,759 |
| bookends | 515 | 515 |
| forced erasures | 21,165 | `context_ledger_turns.reset_forced` 21,165 |
| model calls | 1,890,337 | `context_ledger_turns` 1,890,337 |
| work commits | 63,232 | `work_daily` agent level 63,232 |
| GT rows (preferred) | 2,228 | `ground_truth_labels` 2,228 |
| units | 109 | `period_units` 109 |

Holdout mask: 0 non-null event-derived values and 0 `native_for` entries on the 38 holdout units.

## Limits
- The structure flags and the native-test index are judgment calls from the record and the cards' questions, not results.
- `N` is `period_units.n_agents` (Claude Code excluded); the temporary fine-tuned leader is active in 44a before its roster join date.
- `n_human_speakers` counts hashed human ids; operators and helpers can't be told apart from viewers without text.
- `work_distinct_files` sums agent-day distinct files; bulk commits inflate it (#40, #51). Prefer `work_commits`.
- Outcomes for scored competitions, money raised, games completed and Juice Shop challenges are not in any ledger (`outcome_narration`).
- `ne_inside` uses the dated NE rows; regime-wide NE41 is a flag (`forced_erasure_regime`), and undated NE39/NE40 appear only as the data-found estimate (NE39).

## Text for `infra/README.md` (coordinator to add under "Built tables")
> ### Period-affordance catalog (DQ9, 2026-10-04): `infra/shared/period_affordances.py` → `period_affordances.parquet`
> One row per `period_units` unit (109; 39 kB): what the unit offers for period-native tests. Size and time (N, documented and empirical active hours), rooms (structural and transient), step changes (`ne_inside`, `data_steps`, joins, room and hours changes), kicks (nudges, bookends, human messages and speakers), DQ1 context counts (calls, forced erasures, voluntary consolidations), DQ6 ground-truth counts by kind, DQ4 outcomes (work commits, sites, deploys, API writes, outcome kinds), hand-coded structure flags (`has_teams`, `has_votes`, `has_roles`, `has_rival_pairs`, `has_checkpoints`, `has_forks`, `has_leader`, `has_private_goals`, `has_room_goal_split`, …), date flags, and `native_for` (hypotheses whose recommended native tests use the unit). **Event-derived columns are null on holdout units.** Human-readable catalog and hypothesis cross-index: `hypotheses/hypohypotheses/period-affordances.md`; docs: `infra/data-quality/period_affordances.md`. `--validate` reconciles every count with its source.

And under "Known issues":
> - **NE dates that the record contradicts** (DQ9): the first nudge is 2026-02-13, not 02-10 (NE10); the daily pause/resume bookends end 2026-08-04, two weeks before the nudges (08-20), so NE43 is two steps (08-05 and 08-21); public chat closed ≈ 2025-07-01 (inside #6), an estimate for the undated NE39. `period_units` has no split at NE43 or 08-05 (51g spans both).
> - **NE06 is not a clean Google-only change** (DQ9): the CHANGELOG lists all-agent system-prompt changes on the same days (2025-11-20/21).

## Registration text for `infra/shared/build_all.py` (coordinator to add to `STEPS`, after `ground_truth`)
```python
    {"name": "period_affordances", "cmd": "py", "script": "period_affordances.py", "outputs": ["period_affordances.parquet"]},
```
It depends on `period_units`, `kicks_classified`, `outages`, `context_ledger`, `work_ledger` and `ground_truth` (and reads `chat_core`, `calendar`, `rooms`). Rebuild after any of them, and after `period_units` gains an NE43 split (then drop `EXTRA_NE`).
