# Data-quality work queue (2026-10-04)

Vivian's priority order: (1) postprocessed data quality; (2) re-evaluate every hypothesis on the improved data; (3) Kolchinsky-style physics-of-life HHs for her to vet (HH136–HH153).

| Item | Status | Output |
| --- | --- | --- |
| Consolidation into `infra/shared/` (goal fields, behavior states, project states, period units, classified kicks, text features, spectra, copy info, turn errors + outages, bash_head fix, `build_all.py`) | **done** (2026-10-04) | 47 MB of new tables; 13/13 tests pass; see `infra/README.md` → Shared pipeline |
| DQ1 turn-level context ledger (+ `call_windows`, pause-aware visibility: H29) | **done** (2026-10-04) | `context_ledger_turns.parquet`, `context_ledger_items.parquet`, `call_windows.parquet` |
| DQ2 reply threading + stance labels (Jev, cap $8) | **done** (2026-10-04; $7.90) | `reply_pairs.parquet`, `reply_graph.parquet` |
| DQ3 Jev behavior states v3 + full run (cap $15) | running | `behavior_states_v3.parquet` |
| DQ4 work-output ledger (read-only fetch of public agent repos; ≤ 2 GB) | **done** (2026-10-04) | `work_commits.parquet`, `work_daily.parquet`, `work_outcomes.parquet` |
| DQ5 embedding robustness (second model, style-residualized vectors, statement flags) | **done** (2026-10-04) | `embeddings/*_<model>.npy`, `statement_flags.parquet` |
| DQ6 shared ground-truth labels (#12 teams, #26 votes, #51 roles, #44 checkpoints, leaders; #34 holdout flagged) | **done** (2026-10-04) | `ground_truth_labels.parquet` |
| DQ7 rebuild `chat_core` (clean mentions), `actions` (fixed bash_head), **`activity_bins` (DQ8 join fix, code already patched) and everything downstream (`outages`, `stall_minutes`, `reasons`, `per_period_estimates`)** atomically | after running agents finish; **highest priority** | rebuilt core tables |
| DQ9 period-affordance catalog (Vivian, 2026-10-04): per goal period, what it uniquely offers for testing (ground truth: teams, votes, roles, saboteurs, checkpoints; interventions inside it; structure: rooms, forks, private goals; outcome measures; N and length; holdout status), from `goal-periods.md`, DQ6 ground truth, `period_units`, NE catalog | **done** (2026-10-04) | `hypotheses/hypohypotheses/period-affordances.md` + `period_affordances.parquet` |
| DQ8 shared village-skeleton simulator + null library; per-period estimates schema; holdout (period × statistic) ledger | **done** (2026-10-04) | `infra/shared/simulate.py`, `nulls.py`; schema doc |

Each DQ agent writes only new files in `infra/` and new tables in `data/processed/shared/`; never `hypotheses/` and never existing tables. Docs go in `infra/data-quality/<name>.md`; the coordinator merges README and `build_all` registration text.

**Added 2026-10-04** (from H29, H31, H36, H38):
- H38's outage tables (`outages`, `stall_minutes`, `turn_errors`, `sessions`) → `data/processed/shared/` (consolidation agent).
- `actions.error` → `error_class` from H38's categories (consolidation agent).
- H11 project labels: deterministic tie-break (consolidation agent).
- H25's `dial.py` (daily Curie–Weiss dial, null-calibrated stall mask) → `infra/shared/` once a second hypothesis imports it (H26 may).
- Work ledger: an outcome-resolved write flag (CI/deploy result, push success). `artifact_commands_text.error` means "stderr non-empty" and is set for 65% of pushes (H01 R2).
- `period_units`: add splits at NE43's two steps (2026-08-05, 2026-08-21) and decide on the DQ9 candidate steps (#39 04-27 reshuffle, per-room goal overrides).
- DQ6 `ground_truth_labels`: give #51 rival-pair rows time bounds (Opus 5 is listed as game-dev after its 07-29 reassignment; H54).
- `kicks_classified`: add `primary_target` (the nudge's leading @; 29% of nudges mention other agents too, H35).
- DQ7 rebuild should also apply stall-adjusted (agent-state conditioned) variants of the collective statistics used by H02, H12 and H19.


## Re-evaluation wave (Vivian, 2026-10-04: "go back through the older Hs with the better quality data")
Starts once the consolidation, DQ1 (context ledger + `call_windows`), DQ5 (embedding pack) and DQ7 (atomic rebuild of `chat_core` / `actions`) have landed; DQ2–DQ4 and DQ6 join as they finish. One agent per hypothesis cluster, ≤ 2 threads each, holdout still locked. Each agent re-runs its hypotheses' pipelines on the shared tables, writes a dated "Round 1b (improved data)" section in the card and period folders (old numbers kept next to new), and fills the page-2 summary sections.

| Cluster | Hypotheses | What changes for them |
| --- | --- | --- |
| Collective activity | H02, H03, H12, H19 | stall-adjusted / agent-state-conditioned statistics (H38); clean mentions; read-out Hawkes kernels (HH174) |
| Visibility and response | H04, H08, H18, H29, H30 | context-ledger visibility and `call_windows` (pause-aware); matched-age boundary tests |
| Content geometry | H01, H10, H13, H20, H21, H22, H24, H26, H36 | second embedding model; style-residualized vectors; `self_repeat` / `cross_echo` flags |
| Projects and outcomes | H11, H15, H27, H31, H33, H35 | deterministic project states; work-output ledger as the viability / productivity measure |
| Behavior states | H14, H16, H17, H39 | Jev v3 behavior states; `bash_head` fix; `error_class`; NE43 (nudger off) |
| Stance and ground truth | H21, H22, H37 | DQ2 reply labels (correction vs oppose); DQ6 ground-truth labels; calibrated agent-field null |
| Remaining | H05, H06, H07, H09, H23, H25, H28, H32, H34 | whichever of the above tables they consume (listed in each card's data scheme) |

## After consolidation (2026-10-04)
- **Shims, deferred until the running agents finish** (switching libraries under a running agent is risky): pure shims for H12 (`spectra`), H07 (`copy_info`), H13 (`text_features`), H38 (`turn_errors`, `outages`), H10 (`goal_fields`), and H14 (`behavior_states`), switching H17's sha256 check at the same time. **Result-changing adoptions go into the re-evaluation wave:** H11 → `project_states` (8.1% of labels change: 111 tie re-picks, 499 renumberings, 52 in/out of "other"; consumers H06, H27, H28, H31); H01 → `goal_fields` (fixes the #38 kickoff swap, also in H20 and H32); H04/H08/H16 → `kicks_classified`; H03/H18/H01/H12/H22/H17 → `period_units`; H09 → `outages.idle_spells`.
- **H01 #38 room-2/3 kickoff vectors are swapped** in H01's processed files (inherited by H20, H32). The H01 round-2 and H32 agents were told; H20 is rechecked in the re-evaluation wave.
- **DQ7 is now a single command** once agents finish: `uv run python infra/shared/scan_tables.py --only turns` (stable sort; the bash_head fix), then the chat_core rebuild with clean mentions. Until then use the `actions_bash_head_fixed` sidecar (`bash_head_fixed`, `error_class`, `system_class`).
- **Further consolidation candidates:** H18 `scheme/build.py` (imported by H28, H29, H31, H34), H05 analysis code (H13, H14, H22), H22 scheme (H37), H15 `h15common` (H33), H09 `idle_runs`, H25 `dial.py`, H26 `h26lib` (room-excess estimator; imported by H47).
- **Proposed CLAUDE.md conventions, for Vivian to approve:** rebuild shared tables with `build_all.py`; never import code from another hypothesis's folder (move it to `infra/shared/` with a `--verify`, leave a shim); use `period_units.parquet` unless the card justifies another split; use `bash_head_fixed` / `error_class` and `kicks_classified` instead of the raw columns.

### Re-evaluation design rule: two layers per hypothesis (Vivian, 2026-10-04)
Audit (2026-10-04): in ~15 of 34 hypotheses the period READMEs are near-identical apart from numbers (median word-set similarity 0.75–0.92; almost all written by a `write_period_folders.py`-style script). Only H07, H10, H37, H06, H22, H30, H35, H01 tailor their tests to each period. The strongest round-1 results came from period-specific leverage (H37 on #12 teams, H05's room cut, H08/H15 on NE41, H29 on #51 naming), so:
- **Layer 1, replication:** the hypothesis's common estimator on every eligible period, giving comparable phase-diagram points. Period README role: `replication`. A templated prediction is fine here, labelled as such.
- **Layer 2, period-native tests:** for each hypothesis, 2–4 periods whose setup gives special leverage for *that* question (from the affordance catalog, DQ9). Each gets its own design: an observable, null, ground truth or intervention that only that period allows, its own prediction written before the run, and period-specific infra where needed (e.g. a #26 ballot parser, #12 team map, #51 role/goal fields, #35 fork trees, #44 checkpoints, NE43 nudger-off). Period README role: `native`.
- The overview and dashboard should show the role, so a column of 35 replications isn't read as 35 independent tests.

## New hypotheses H40–H58 (promoted 2026-10-04): launch plan
| Wave | Hypotheses | Launch when |
| --- | --- | --- |
| A | H43, H46, H47, H49, H54, H56, H50 | launched 2026-10-04; paused by the session-limit outage, resume as DQ / near-done agents finish |
| B | H40, H41, H42, H48, H52, H53, H45 | **unblocked** (DQ1 landed 2026-10-04); launch after wave A resumes |
| C | H44 (DQ1 + DQ3 + DQ4), H55 (DQ2 + DQ5), H57 (DQ1 + DQ5), H58 (DQ4 + H01 round 2) | their inputs land |
| D | H51 (one dial) | after waves B–C and the re-evaluation wave |
Slots are capped at 20 concurrent agents; queued work launches as slots free, data-quality and re-evaluation first.

