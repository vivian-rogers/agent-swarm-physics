# Data-quality work queue (2026-10-04)

Vivian's priority order: (1) postprocessed data quality; (2) re-evaluate every hypothesis on the improved data; (3) Kolchinsky-style physics-of-life HHs for her to vet (HH136–HH153).

| Item | Status | Output |
| --- | --- | --- |
| Consolidation into `infra/shared/` (goal fields, behavior states, project states, period units, classified kicks, text features, spectra, copy info, bash_head fix, `build_all.py`) | running | see the consolidation agent's report |
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
