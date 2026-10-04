# DQ6: shared ground-truth labels

**Code:** `infra/shared/ground_truth.py` (build; `--validate` for the checks below).
**Table:** `data/processed/shared/ground_truth_labels.parquet` (2,288 rows, 53 kB, zstd). Provenance key `ground_truth` in `data/processed/shared/_provenance.json`.
**Status:** built 2026-10-04 (UTC). A full rebuild from raw is identical to the build from the cached #34 extract. Codes only, no message text.

## Why
Several hypotheses each re-derived the same known structure (who was on which #12 team, who voted for whom in #26, who held which #51 role, the #44 leader checkpoints, the #34 saboteurs) in slightly different ways. Validating any detector needs one documented answer key: H37 stance camps, H21 debate antiferromagnet, H22 #51 frustration, H11 herding, H31 votes, and H29/H30 human-message effects. Where existing derivations disagree, the table keeps one row per derivation and says which one to trust.

## Table
| Column | Meaning |
| --- | --- |
| `row_id` | int32, stable within a build (sorted by goal, kind, unit, time) |
| `goal_no` | goal period (int8) |
| `label_kind` | team, judge, debate_result, phase, tally, leader, ballot, vote_declaration, saboteur, checkpoint, role, role_class, rival_pair, opposed_pair, room_assignment, room_presence |
| `unit` | sub-unit where needed: `debate_NN`, `round1/round2`, `approval/runoff/confirmatory`, `term1/term2`, `day_YYYY-MM-DD` |
| `agent` | roster code for single-agent labels |
| `agent_a`, `agent_b` | pair labels; for `ballot` and `vote_declaration`, voter = `agent_a`, candidate = `agent_b` |
| `value` | the label (e.g. `gov`, `elected_leader`, `forecaster`, `rest`) |
| `detail` | structured codes (score, flags, end reference); never message text |
| `t_valid_from`, `t_valid_to` | UTC validity interval. For events (results, declarations), `to == from`. Open intervals end at the export (2026-09-20 13:05 UTC) or the period's end. |
| `source_kind` | `operator message` · `goal text` (raw `agent_goals`, `village_goals`) · `system event` (scaffold logs, tool output) · `agent declaration` · `derived` |
| `source_ref` | table + id: `chat_core:message_id=…`, `agent_goals:id=…`, `events_core:event_index=…`, `intentions:event_index=…`, `computer_use_turns:id=…`, `rooms_timeline:agent=…;t_start=…` |
| `confidence` | high / medium / low |
| `derived_by` | which existing code, rule or hand reading produced it |
| `conflict_group` | shared by rows from different derivations of the same label that disagree |
| `preferred` | the row to trust within a conflict group (True for every row outside a group) |
| `holdout` | `holdout_mask` of the row's start (PT date, goal). Rows crossing a holdout boundary are split there (the #51 tail starts 2026-09-07 07:00 UTC). |

**Typical use:** `pl.read_parquet(...).filter(~pl.col("holdout") & pl.col("preferred") & (pl.col("label_kind") == "team"))`. Exploratory work must keep `~holdout`.

## What is in it, by period
| Period | Kinds (non-holdout rows) | Source and confidence |
| --- | --- | --- |
| #12 debates | team 60, judge 10, debate_result 10, phase 30 | H21's hand-verified `scheme/labels/g12_debates.json`, which H37 and DQ2 read too. Teams and judges are declarations by the game's own officials (`agent declaration`, high). `deb` phase runs first speech → verdict (high); `pre`/`post` are rule windows (medium). `motion_side=pro/con` in `detail`. |
| #26 election | phase 8, tally 12, leader 2, ballot 64, vote_declaration 810 | Hand-read administrator and organizer announcements (high). **Two elections:** round 1 on 01-05 (chat approval vote → 9–9–9 tie → 7–1–0 runoff → agent 17 elected at 19:35:22 UTC) and round 2 on 01-09 (confirmatory plurality vote, 18:45–19:00 UTC, 17 re-elected 9–0). `ballot` = votes cast in the announced windows in the requested format (high: reproduces all three official tallies exactly). `vote_declaration` = H11's rule (low; flags `h11_primary` / `h31_primary` reproduce each consumer's subset). |
| #34 (holdout) | saboteur rows (agent-day); room_presence | 178 rows in total. See the #34 section below. |
| #35 | leader 6 | Lead Designer per room on 03-16/17/18, from the operator kickoff (high). Agent 19 (Claude Code), not 16, is the #rest designer on 03-17; the mention regex confuses them. |
| #44 | checkpoint 5, leader 1 | Temporary fine-tuned leader (agent 28): qwen-v3, qwen-v10, kimi-v2, kimi-v4-curated56, kimi-v7-aug-64. Starts and ends come from the operator's "up and running" / "stop" / "pause" messages (high). |
| #45 (holdout) | leader 2, checkpoint 3 | Fine-Tuned Leader (agent 30). The operator corrected its model string at 17:15:40 UTC on 06-01: the first ~11 min ran a 32k non-peft model (medium). |
| #51 | role 35, role_class 12, rival_pair 9, opposed_pair 2 (head); role 32, role_class 12, rival_pair 7, opposed_pair 2 (tail, holdout) | Raw `agent_goals` (`goal text`, high), plus one operator-message role (below). Pair classes use H22's coding: same short name = rival (high); Prankster × Ethicist/Psychologist = opposed (medium, coded from titles). `role_class` support/media lets consumers rebuild H22's SY and NC classes. |
| #35–#51 | room_assignment 149 (+ 182 holdout) | 18 hand-read operator messages that assign rooms (`ROOM_ASSIGN`; split / all / move). An assignment holds until the agent's next one. Rows not covered by any message are absent. |
| #32–#51 | room_presence 404 (+ holdout) | `rooms_timeline` (room tags on the agent's own events), rooms era (2026-02-25+). `detail` says `entry=agent_move` when the interval opens with the agent's own ENTER_ROOM tool call. Pieces with < 60 s inside the period's active windows are dropped (`village_goals` starts precede the kickoff by hours). |

## Conflicts between existing derivations, and which to trust
1. **#26 "runoff" timing: H11 and H31 measured the wrong election.** The record shows the runoff opened at 19:32:19 UTC on 01-05 (administrator, message `8d08d622…`) and closed 19:34:00 (7–1–0).
   - H31's onset rule (first agent message containing "runoff") fires at 18:02:30, a procedure proposal.
   - H11's rule (≥ 2 runoff-word messages in a 30-min window) fires at the window starting 19:01:32.
   - H31's consensus time (winner share ≥ 0.5) lands at **2026-01-09 18:46:36**: the round-2 confirmatory vote.
   - 9 of the 10 declarations in H11's "runoff snapshot" (counts [8, 1, 1]) are dated 01-09.
   - So H11's "abrupt runoff jump (0.18 → 0.80 in one 30-min window)" and H31's E-V τ_V ≈ 12.5 active h describe the 01-09 re-election (a near-unanimous plurality vote for the incumbent), not the 01-05 runoff.
   - **Trust:** the administrator's announcements (`phase`, `tally`, `ballot` rows). Conflict group `g26_runoff_onset`, preferred = record.
   - H11's declarations themselves are reproduced exactly (412 / 412 rows). They are still low-confidence state labels: they include tally reports and nominations, and name non-candidates.
2. **#51: Claude Opus 5 (agent 40) had no role from 07-24 to 07-29 in every existing derivation.** H22 `role_relations.role_on`, `goal_fields` and H37 all treat it as unrelated (U).
   - The operator assigned it the daily-users game goal on arrival (`0025a993…`, 07-24 18:51 UTC) and moved it to Mathematician on 07-29 (`ff0510b4…`, NE38).
   - The `agent_goals` row was overwritten: created 07-24, start 07-29.
   - That makes Opus 5 a **third game dev**, with two extra rival pairs (with agents 24 and 26) for those five days.
   - **Trust:** the operator-message row (conflict group `g51_role_a40_missing`; the H22 "no role" row is kept, preferred = False).
3. **#51 day granularity (not a conflict in value).** H22's `role_on` gives a role for the whole PT start day. The table uses the exact `agent_goals` start. This explains 6 of the 9 agent-day mismatches (agents 35–38, 42 and 45 on their join days); the other 3 are item 2. Otherwise 1,194 agent-days agree, the SR/OP pair sets are identical (9 = 9), and the 33 `agent_goals` ids equal `goal_fields`' `agent_goal` rows.
4. **#12 windows: H21 vs H37.** H21 clamps the post-verdict window at the day's last agent event; H37 doesn't. Zero debates differ, so there are no conflict rows. The team lists are one file used by both.
   - Minor slip in H21's labels file: debate 9's `motion_message_id` (`7d68cda8…`) is a debater restating the motion 9 s after the judge announced it (`6e2dabb4…`). It changes no window (the pre window starts at the lineup).
   - Debate 3's `lineup_message_id` is one debater's self-confirmation (the teams self-organised); the teams are confirmed by speech self-identification.
5. **#44 checkpoints: operator messages vs H23 `h23lib.CHECKPOINTS`.** The starts agree within 2.2 s (kimi-v2: 20:04:02 vs 20:04:00).
   - H23's segments are open-ended, so one agent-28 event (a START_USING_COMPUTER at 05-28 17:01:52, during the v10 deployment) would be labelled qwen-v3. The table ends qwen-v3 at the operator's stop on 05-26 19:26:51.
   - **Trust:** the table (adds end times). No message is affected.
6. **#34: two derivations per agent-day** (see below). Agreement deliberately not computed.

## #34 saboteurs (locked holdout)
- **Rows:** 178 rows for #34, all `holdout = True` (asserted at build). They are saboteur agent-day labels plus room presence; #voted-out membership is the `room_presence` rows with room `voted-out`, not derived separately.
- **Derivation A: H21's self-identification rule,** which H37 imports for its own confirmatory script. SAB/VIL regexes over the agent's own intentions and chat that day; ambiguous if both match; villager if neither matches.
  - Coded `agent declaration`, confidence **low**.
  - Known false-positive modes, from the patterns themselves (not measured on #34): restating the rules ("if you rolled a 1…"), accusations ("…as the saboteur"), and defaulting silent agents to villager.
- **Derivation B: the system-logged die roll.** The kickoff told agents to roll a d6 on their computer. Rows hold the first roll command of the day (randint(1,6), `$RANDOM % 6`, `shuf -i 1-6`, …) whose stdout prints a clean 1–6.
  - Coded `system event`, `source_ref = computer_use_turns:id`. Confidence high, or medium if the agent rolled again with a different value.
- **Preference:** where both exist for an agent-day they share a `conflict_group` (`g34_aNN_date`) and B is preferred. A is kept for the agent-days without a parseable roll.
- **Nothing was analysed on #34.** The only #34 outputs ever printed were the total row count, the masked command templates (digits replaced) needed to write the roll parser, and a silent assertion that both derivations produced rows. No label distribution, no agreement between A and B, and no outcome was looked at. The #34 rows are excluded from the hand check.
- **Who uses it:** H21 (`confirm_g34.py`) and H37 (`confirm_g34.py`) both plan to use this answer key. Both currently compute derivation A themselves. Switching to the preferred rows changes their ground truth to B where it exists, so any switch must be committed before their confirmatory runs (holdout reuse policy).

## Validation (non-holdout)
- **Coverage:** see the period table. 1,629 non-holdout rows; 15 kinds; #12 covers all 7 agents in 10 debates; #26 covers 10 voters in 3 rounds; #51 covers 32 agents' roles; rooms cover 35 agents in 11 periods.
- **#26 ballots vs the official tallies (exact):** approval {17:9, 0:9, 6:9, 16:7, 12:7, 15:4, 13:2} from 9 voters; runoff {17:7, 6:1, 0:0} from 8; confirmatory {17:9, 6:0} from 9.
- **#12 anchors:**
  - Each verdict message is by the labelled judge.
  - Each first speech is by Government.
  - Each lineup message is by a participant.
  - Exception (motion message): debate 9's motion message is the restatement described above.
- **Rooms (operator assignment vs system presence), share of the agent's room-tagged events in the assigned room:** median 1.00 over 149 rows; 142 at ≥ 0.9; 2 below 0.5. Both are real deviations, not tagging errors:
  - GPT-5 never moved to #universe-coordination in #40 (as NE42 notes).
  - The Claude Code agent sat in #general during #36.
  - Agents 6 and 29 spent ~45% of #51 in #focus.
- **References:** every `chat_core` (412), `agent_goals` (33), `events_core` (456) and `intentions` reference resolves.
- **Hand check (seed 20261004, 18 non-holdout rows, checked against raw `chat_messages`, `agent_goals` and `events`): 18 / 18 consistent.**

| row_id | kind | check against raw | result |
| --- | --- | --- | --- |
| 15 | team (#12 d3, agent 8 opp) | ref is GPT-5's self-confirmation; agent 8 speaks as Opposition Whip, teammates name it | pass (weak anchor) |
| 55 | team (#12 d10, agent 5 gov) | judge's lineup; agent 5 opens as Prime Minister | pass |
| 62 | judge (#12 d3, agent 11) | verdict message by agent 11 | pass |
| 72 | debate_result (#12 d3, opp) | verdict rules for the Opposition | pass |
| 89 | phase pre (#12 d4) | judge's lineup 09-01; window = first speech − 15 min by rule | pass |
| 121 | tally (#26 approval, agent 13 = 2) | administrator's official tally | pass |
| 130 | leader (#26 term 1, agent 17) | administrator's official result | pass |
| 148 | ballot (12 → 16, approval) | agent 12's approval ballot, 6 names | pass |
| 190 | ballot (6 → 17, runoff) | agent 6's runoff ballot | pass |
| 1313 | room_assignment (#37, agent 22 best) | operator kickoff room clause | pass |
| 1349 | room_presence (#38, agent 18 rest) | agent 18's 750 raw messages in the interval are all in #rest | pass |
| 1516 | checkpoint (#44 qwen-v10) | operator "v10 is up and running" in #best | pass |
| 1889 | role (#51, agent 20 forecaster) | raw agent_goals row | pass |
| 1913 | role (#51, agent 44 village helper) | raw agent_goals row | pass |
| 1974 | rival_pair (27–31 merch baron) | both raw rows "Merch baron" | pass |
| 1988 | opposed_pair (10 prankster × 13 psychologist) | raw rows; class is H22's coding | pass |
| 2002 | room_assignment (#51, agent 22 general) | operator kickoff "move to #general" | pass |
| 2215 | room_presence (#51, agent 33 focus, 20 s) | raw ENTER_ROOM into #focus then back to #general | pass |

## Limits
- **Agent declarations remain declarations.** #12 teams and #26 ballots and results are by agents (the game officials and voters). They are high confidence because they are performative and cross-checked: the tallies reproduce exactly, and speeches self-identify.
- **`agent_goals` is a current-state snapshot.** Overwritten roles are missing unless an operator message recovers them; only Opus 5 is recovered. Rows edited after their start are flagged in `detail` (Performance coach 09-04; Press baron 09-11, in the holdout), so their description may differ from what the agent saw earlier. No roles were looked for in the holdout tail beyond `agent_goals`.
- **#51 opposed pairs and role classes** are H22's judgment coding from role titles, not operator statements.
- **Room assignment** covers only the 18 operator messages read. Onboarding rooms, the GPT-5.6 isolated rooms (NE32) and some newcomers' placements are in `room_presence` only.
- **Presence start times** are the agent's first room-tagged event, not the move instant (except agent ENTER_ROOM calls). `rooms_timeline` inherits `events_core`'s forward-filled room tags.
- **#34 roll rows** miss agent-days where the die was rolled through the GUI (screenshots not downloaded), written to a file without printing, or not rolled at all; derivation A covers those at low confidence. A roll is what the agent drew, not necessarily how it then played.
- **Not covered:** debate captains (#12; not recorded by H21), #45 module assignments by the leader, other scored contests (#6 store profits, #23 chess, #27 Juice Shop, #32 challenges). No existing hypothesis derived them.
- **No `checkpoint` kind exists for scored milestones outside #44/#45;** "checkpoint" here means model checkpoints.

## Which hypotheses should switch, and what changes
| Hypothesis | Switch | What changes |
| --- | --- | --- |
| H21 | `team`, `judge`, `phase` (#12); `saboteur` preferred rows (#34, before its confirmatory run) | #12: nothing numerically (same file). #34: ground truth becomes the system-logged roll where available; must be committed before `confirm_g34.py` is run. |
| H37 | `team`/`phase` (#12); `role`, `rival_pair`, `opposed_pair`, `role_class` (#51); `ballot` (#26); `saboteur` (#34) | #51 gains the Opus 5 game-dev spell and two rival pairs (07-24 → 07-29), and exact start times. `g26_votes()` should use `ballot` rows: H11's declarations mix tally reports and the 01-09 re-election into "votes". #34 as for H21. |
| H22 | `role`, `rival_pair`, `opposed_pair`, `role_class` | Same as H37 for #51; replaces `role_relations.load_role_spells`/`role_on` (keeps its coding). Unit-majority roles can be recomputed from the intervals. |
| H11 (G26) | `phase`, `ballot`, `tally`, `leader` | Its HH22 tests need re-reading: the detected jump (window 27.2) and the runoff snapshot are the 01-09 confirmatory vote. P-G26a/b/c should be re-run per round, with the 01-05 runoff (7–1–0 in ~100 s) as the true runoff and the 9–9–9 approval tie as the symmetric point. |
| H31 (E-V) | `phase`, `ballot` | τ_V ≈ 12.5 active h is the time from a spurious onset to the 01-09 re-election; the true runoff consensus took < 2 min. E-V should be redefined per round from the `phase` windows. |
| H23 | `checkpoint`, `leader` (#44, #45) | Adds segment ends. `confirm_g45.py` should drop or flag agent 30's first ~11 min on 06-01 (wrong model string). |
| H01, H05, H18, H13 (rooms) | `room_assignment` + `room_presence` | One documented answer for "who was assigned where" vs "who was actually there". Known deviations (GPT-5 in #40, Claude Code in #36, #focus in #51) are explicit. |
| H29, H30 (human-message effects) | `checkpoint`/`leader` timing; the operator-message refs | Operator interventions that change structure (role reassignment NE38, room moves, leader model fix) are dated rows to exclude or model. |
| DQ2 | `team` (#12), `role`/pair rows (#51) | Its ground-truth checks currently import H21 and H22 directly. |

## Text for `infra/README.md` (coordinator to add under "Built tables")
> **Ground-truth labels (DQ6, 2026-10-04):** `infra/shared/ground_truth.py` → `ground_truth_labels.parquet` (2,288 rows, 53 kB; codes only).
> - One agreed answer key for detector validation. #12 teams/judges/results/phases; #26 election phases, official tallies, ballots, leader terms and H11's declarations; #34 saboteur agent-days (holdout); #35 lead designers; #44/#45 leader and checkpoints; #51 roles, role classes, rival and opposed pairs; operator room assignments (#35–#51) and system room presence (rooms era).
> - Columns: `goal_no`, `label_kind`, `unit`, `agent` / `agent_a`,`agent_b`, `value`, `detail`, `t_valid_from/to` (UTC), `source_kind`, `source_ref`, `confidence`, `derived_by`, `conflict_group`, `preferred`, `holdout`.
> - Use `preferred & ~holdout`. Docs, conflicts and validation: `infra/data-quality/ground_truth_labels.md`.
> - Rebuild needs one gzip+grep pass over raw `computer_use_turns` (~3 min idle, ~14 min on a loaded machine; 2 processes).

And under "Known issues":
> - **#26 had two elections** (DQ6): a 01-05 approval vote → 9–9–9 tie → 7–1–0 runoff, and a 01-09 confirmatory re-election (9–0). H11's "runoff jump" and runoff snapshot, and H31's E-V consensus time, are the 01-09 vote. Use `ground_truth_labels` `phase`/`ballot` rows.
> - **`agent_goals` is a snapshot** (DQ6): Claude Opus 5's first role (game dev, 07-24 → 07-29) was overwritten; the operator message recovers it. H22, H37 and `goal_fields` treat Opus 5 as roleless for those days.

## Registration text for `infra/shared/build_all.py` (coordinator to add to `STEPS`, after `outages`)
```python
    {"name": "ground_truth", "cmd": "py", "script": "ground_truth.py", "outputs": ["ground_truth_labels.parquet"]},
```
It depends on `scan_tables`, `build_derived` and `build_mentions_clean`. It reads H21's labels file and H21's SAB/VIL patterns read-only. `--turns-cache PATH` reuses a pre-filtered #34-day extract of `computer_use_turns` (`gzip -dc … | LC_ALL=C grep -E '"created_at":"2026-03-(0[5-9]|1[0-5]) '`).
