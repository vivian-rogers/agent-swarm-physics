# Data-quality work queue (2026-10-04)

Vivian's priority order: (1) postprocessed data quality; (2) re-evaluate every hypothesis on the improved data; (3) Kolchinsky-style physics-of-life HHs for her to vet (HH136–HH153).

| Item | Status | Output |
| --- | --- | --- |
| Consolidation into `infra/shared/` (goal fields, behavior states, project states, period units, classified kicks, text features, spectra, copy info, turn errors + outages, bash_head fix, `build_all.py`) | **done** (2026-10-04) | 47 MB of new tables; 13/13 tests pass; see `infra/README.md` → Shared pipeline |
| DQ1 turn-level context ledger (+ `call_windows`, pause-aware visibility: H29) | **done** (2026-10-04) | `context_ledger_turns.parquet`, `context_ledger_items.parquet`, `call_windows.parquet` |
| DQ2 reply threading + stance labels (Jev, cap $8) | **done** (2026-10-04; $7.90) | `reply_pairs.parquet`, `reply_graph.parquet` |
| DQ3 Jev behavior states v3 + full run (cap $15) | **done** 98.4% ($13.13); 3,313 #51 holdout windows await OpenRouter credit (`--retry-errors`) | `behavior_states_v3.parquet`; doc `DQ3-behavior-states-v3.md` |
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
- `actions_bash_head_fixed.system_class` is constant `none`: fix the classifier (H56).
- Move `h56lib.newton_counts` / `cfx_counts` (H14's EP estimators from count matrices, ~100× faster) to `infra/shared/`.
- `outages.py`: derive `scheduled` from runner start/stop (empty after 08-04 with the operator-message rule; RE-A1).
- Move the trim-before-surrogate functions (H38 `trim_gains`/`l1_trim_blockshift`, H12 `trim_rows`/`spectrum_test_blockshift`, H25 trim variant) into `infra/shared/nulls.py`.
- A stable shared statement id across `statements.parquet`, embeddings and `statement_flags` (H12 had to join on kind, agent, t, pt_date).
- Per-period estimate files from H55 and others don't always follow the shared schema (value/se/p instead of estimate/ci; missing period_unit): the coordinator converts them; agents should call `write_estimates` with `map_unit(goal_no)`.
- `estimates.py`: consider allowing `cluster_bootstrap` as a `ci_kind` (H44 had to map its agent-day cluster bootstrap to `percentile`).
- Move H02's `r1b_common.py` (trim / stall / impute on reason codes) and H19's `scheme/geq_r1b.py` (gains raw/trim/scaf with joint surrogates) into `infra/shared/` together with the H38/H12/H25 trim functions; four hypotheses implement the same logic.
- New shared tables: "realizations" (days split at operator-off gaps ≥ 60 min) and a Hawkes exogenous-drive table (human + nudge, bookends separate) for H04, H42 and others.
- `per_period_estimates`: add a `data_version` column and mark the backfilled round-1 activity rows of H02, H19 (and other activity_bins users) as superseded; the round-1b rows say they supersede them.
- Add an event-time agent-shift row to the DQ8 null size table (RE-A2).
- `actions_bash_head_fixed`: add a shell sub-class column (`head_class`: vcs/net/run/read/write/wait/other; H14's `build_r1b.py`).
- Context ledger: add a per-call prompt-token column (H45's `calls.parquet`; Anthropic from `actions` cache fields).
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

### Sidecars available now (2026-10-04), so the re-evaluation need not wait for DQ7
- `activity_bins_fixed.parquet` (DQ8) and `outages_fixed/` (`outages.py --fixed`: joint silences 14.3% → 5.3% of non-holdout minutes; outage runs 3,590 → 682). Re-evaluation agents use these; DQ7 later swaps them into the main tables.

### Re-evaluation progress
| Agent | Hypotheses | Status |
| --- | --- | --- |
| RE-A1 | H38, H12, H25 | **done** (2026-10-04) |
| RE-C3 | H01 (round 1), H26, H36 | running (2026-10-04): shared goal vectors, both models, fixed bins, trimmed nulls, NE40/NE45 as detection targets |
| RE-O1 | H15, H33, H35 | running (2026-10-04): work-ledger viability/productivity, real failures, both embedding models |
| RE-V2 | H29, H30, H39 | running (2026-10-04): ledger visibility, fixed bins, leading-@ targets, lever_design, v3 states |
| RE-A2 | H02, H19, H03 | **done** (2026-10-04) |
| RE-V1 | H18, H08, H04 | **done** (2026-10-04) |
| RE-B1 | H17, H16, H14 | **done** (2026-10-04) |
| RE-C1 | H10, H20, H24 | running (2026-10-04): shared goal vectors, both embedding models, dedupe flags |
| RE-C2 | H13, H21, H22 | running (2026-10-04): DQ6 ground truth (Opus 5 role), stance channel with calibrated null, style residuals, behavioral family test |
| RE-P1 | H11, H31, H27 | running (2026-10-04): shared labels, #26 per round, attention vs work space |
| next | H05 (gains on fixed bins, needed by H19), H44 (new, unblocked by DQ3); H05, H06, H07, H09, H23, H28, H32, H34 | queued, 2–3 hypotheses per agent as slots free |

