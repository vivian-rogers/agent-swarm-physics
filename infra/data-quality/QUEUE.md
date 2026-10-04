# Data-quality work queue (2026-10-04)

Vivian's priority order: (1) postprocessed data quality; (2) re-evaluate every hypothesis on the improved data; (3) Kolchinsky-style physics-of-life HHs for her to vet (HH136–HH153).

| Item | Status | Output |
| --- | --- | --- |
| Consolidation into `infra/shared/` (goal fields, behavior states, project states, period units, classified kicks, text features, spectra, copy info, turn errors + outages, bash_head fix, `build_all.py`) | **done** (2026-10-04) | 47 MB of new tables; 13/13 tests pass; see `infra/README.md` → Shared pipeline |
| DQ1 turn-level context ledger (+ `call_windows`, pause-aware visibility: H29) | running | `context_ledger_turns.parquet`, `context_ledger_items.parquet`, `call_windows.parquet` |
| DQ2 reply threading + stance labels (Jev, cap $8) | running | `reply_pairs.parquet`, `reply_graph.parquet` |
| DQ3 Jev behavior states v3 + full run (cap $15) | running | `behavior_states_v3.parquet` |
| DQ4 work-output ledger (read-only fetch of public agent repos; ≤ 2 GB) | running (2026-10-04) | `work_commits.parquet`, `work_daily.parquet`, `work_outcomes.parquet` |
| DQ5 embedding robustness (second model, style-residualized vectors, statement flags) | running (2026-10-04) | `embeddings/*_<model>.npy`, `statement_flags.parquet` |
| DQ6 shared ground-truth labels (#12 teams, #26 votes, #51 roles, #44 checkpoints, leaders; #34 holdout flagged) | to do (small) | `ground_truth_labels.parquet` |
| DQ7 rebuild `chat_core` (clean mentions) and `actions` (fixed bash_head) atomically | after running agents finish | rebuilt core tables |
| DQ8 shared village-skeleton simulator + null library; per-period estimates schema; holdout (period × statistic) ledger | to do | `infra/shared/simulate.py`, `nulls.py`; schema doc |

Each DQ agent writes only new files in `infra/` and new tables in `data/processed/shared/`; never `hypotheses/` and never existing tables. Docs go in `infra/data-quality/<name>.md`; the coordinator merges README and `build_all` registration text.

**Added 2026-10-04** (from H29, H31, H36, H38):
- H38's outage tables (`outages`, `stall_minutes`, `turn_errors`, `sessions`) → `data/processed/shared/` (consolidation agent).
- `actions.error` → `error_class` from H38's categories (consolidation agent).
- H11 project labels: deterministic tie-break (consolidation agent).
- H25's `dial.py` (daily Curie–Weiss dial, null-calibrated stall mask) → `infra/shared/` once a second hypothesis imports it (H26 may).
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
- **Further consolidation candidates:** H18 `scheme/build.py` (imported by H28, H29, H31, H34), H05 analysis code (H13, H14, H22), H22 scheme (H37), H15 `h15common` (H33), H09 `idle_runs`, H25 `dial.py`.
- **Proposed CLAUDE.md conventions, for Vivian to approve:** rebuild shared tables with `build_all.py`; never import code from another hypothesis's folder (move it to `infra/shared/` with a `--verify`, leave a shim); use `period_units.parquet` unless the card justifies another split; use `bash_head_fixed` / `error_class` and `kicks_classified` instead of the raw columns.

