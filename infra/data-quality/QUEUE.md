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

