# Per-period estimates table (DQ8)

`data/processed/shared/per_period_estimates.parquet` is one long table of headline statistics, one row per
(hypothesis, period unit, statistic, channel, method). It exists so that:
- periods can be compared as points on a phase diagram (H51 "one dial");
- replications are not mistaken for independent tests;
- every estimate carries its CI convention, null, provenance and holdout status.

**Writer:** `infra/shared/estimates.py` (`write_estimates`, `read_estimates`, `ci_from_se`).
**Backfill:** `uv run python infra/shared/estimates.py --backfill`, which is read-only on hypothesis outputs.

## Columns

| Column | Type | Meaning |
| --- | --- | --- |
| `hypothesis` | str | `H25` |
| `period_unit` | str | Which days the estimate covers (see "Period units" below). |
| `goal_no` | int16 | Goal period number. |
| `statistic` | str | Short snake_case name, stable across periods: `loop_gain_g_daily_dial`, `branching_ratio_R`. |
| `channel` | str | `activity`, `talk`, `content`, `project`, `stance`, `behavior`, or a lever such as `N_tgt`; free text where needed. |
| `estimate` | float64 | The point estimate. |
| `ci_lo`, `ci_hi` | float64 | Confidence interval at `ci_level`; null when none exists. Null quantiles are never CIs. |
| `n` | float64 | Sample size, in the units given by `n_kind`. |
| `method` | str | One line: the estimator and how its uncertainty was computed. |
| `null` | str | The null or baseline used for significance, or null. |
| `role` | str | `replication` (the hypothesis's common estimator on every eligible period) or `native` (a period-specific design: #12 teams, #44 leader, #21 switch-on, NE-specific tests). See QUEUE.md, "two layers". |
| `holdout` | bool | Derived by the writer from `hypotheses/holdout.json` and `period_units`. |
| `regime` | str | `I`, `II`, `III`, or `II/III` for #36. Derived from `period_units`. |
| `built_at` | datetime (UTC) | Filled by the writer. |
| `git_commit` | str | Filled by the writer (`common.git_commit`, with a `+uncommitted` suffix when the tree is dirty). |
| `ci_level` | float64 | 0.90 or 0.95. Optional, but always filled when a CI exists. |
| `ci_kind` | str | `percentile`, `se_z`, `se_t`, `profile`, `jackknife_z`, `parametric` or `none`. `se_*` and `jackknife_z` mean the writer derived the CI from a stored SE. |
| `se` | float64 | The stored SE, when the source has one. |
| `n_kind` | str | `days`, `agents`, `events`, `episodes`, `agent-days`, … |
| `unit_local` | str | The hypothesis's own unit id, kept verbatim. |
| `first_day`, `last_day` | str | PT dates, when known. |
| `confirmatory` | bool | True only for a pre-registered confirmatory run. |
| `post_hoc` | bool | True for post-hoc statistics (e.g. H15's context-erasure dip). |
| `status` | str | `backfilled` for rows extracted by DQ8; a hypothesis may write `ok`, `underpowered`, `unstable`. |
| `source` | str | File the value came from. |
| `source_mtime` | str | Modification time of that file. |
| `notes` | str | Caveats, e.g. "H01 #38 kickoff-vector swap affects G38". |

## Rules

- **Holdout.** The writer refuses rows on held-out periods or windows unless `confirmatory=True`. A confirmatory row must also appear as a `run` entry in the holdout ledger (`infra/data-quality/holdout_ledger.json`, `holdout_ledger.record_run`).
- **Period units.**
  - Use the shared `period_units` id when the estimate covers exactly that unit's days. A single-unit period's unit id is its goal number (`"41"`).
  - Use `G<NN>` for a whole multi-unit goal period.
  - Otherwise use `local:<id>` and keep `unit_local`. Many hypotheses use H01's unit split (`36b`, `38a`–`c`, `51a`–`e`), which does **not** match the shared ids. For example, H26's `51b` is 19 days, while shared `51b` is 1 day.
  - `estimates.map_unit(goal_no, first_day, last_day)` maps a date range to a shared id when one matches.
- **One model per period.** Each row is an estimate fitted within one period unit; never write pooled-period fits. Transition designs (NE event studies, e.g. H10's NE34 pairs) are not single-period rows. They need their own table (future: `per_transition_estimates`) and are not backfilled.
- **Upsert.** `write_estimates` replaces the hypothesis's earlier rows that have the same `(statistic, channel, method, role, source)` and appends the rest. Re-running a pipeline therefore does not duplicate rows. The backfill replaces only rows with `status == "backfilled"`.
- **Comparability.** Compare periods on one `(hypothesis, statistic, channel, method)` at a time. The same physical quantity estimated by two hypotheses is not interchangeable without a calibration. For example, H19's `loop_gain_g_eq` and H25's `loop_gain_g_daily_dial` use different blocks, stall handling and aggregation.

## Writing from a hypothesis pipeline

```python
import sys; sys.path.insert(0, "infra/shared")
import estimates as E
rows = [{"period_unit": "41", "goal_no": 41, "statistic": "loop_gain_g_daily_dial", "channel": "activity",
         "estimate": g, "ci_lo": lo, "ci_hi": hi, "ci_level": 0.90, "ci_kind": "percentile", "n": k_days,
         "n_kind": "days", "method": "...", "null": None, "role": "replication",
         "source": "data/processed/H25-criticality-dial/dial_period.parquet"}]
E.write_estimates(rows, hypothesis="H25")
```

## Backfill coverage (2026-10-04)

914 rows from 30 hypotheses, 35 goal periods and 37 statistics (911 replication, 3 native). No held-out rows. 726 rows (79%) have a CI.

**Specs** live in `estimates.B`, chosen from the DQ8 read-only survey of every hypothesis's per-period outputs. Values were spot-checked against the survey's verified numbers:
- H34 G38: R = 0.257 [0.247, 0.266]
- H03 G38 TALK: n = 0.321 [0.078, 0.607]
- H18 G38: β = 0.695 [0.621, 0.800]

| Hypothesis | Statistic(s) | Periods | CI |
| --- | --- | --- | --- |
| H01 | exposure_coupling_slope (P6) | 10 (15 units) | SE → z |
| H02 | cw_beta_J0 (per 5-day chunk, `local:g<NN>c<k>`) | 15 (21 chunks) | none |
| H03 | hawkes_branching_n (TALK, ALL) | 35 | 95% percentile |
| H05 | mf_block_J_in_minus_out (talk) | 8 | 95% percentile |
| H08 | readout_gate_jump_D (addr, talk) | 17 | 95% percentile |
| H10 | loop_gain_g_along_goal | 7 | 90% percentile |
| H11 | potts_coupling_bJ_CW | 14 | jackknife SE → t |
| H12 | lambda1_over_crossday_edge, collective_mode_count_k_cd | 18 (24 units) | none |
| H13 | family_field_T, family_coupling_delta | 10 (15 units) | jackknife z / 95% percentile |
| H14 | frac_agents_ep_above_null, collective_ep_excess_mf | 9 | none |
| H15 | context_erasure_write_dip (post hoc) | 9 | 95% percentile |
| H16 | trap_aging_slope_deep | 10 | 95% percentile |
| H17 | implied_timescale_t2_min | 27 | 95% percentile |
| H18 | dilution_exponent_beta (D1, D2) | 16 | 95% percentile |
| H19 | loop_gain_g_eq (active, talk) | 35 | SE → z |
| H20 | aging_slope_A | 29 | none (null SD only) |
| H21 | staggered_order_delta (native, #12) | 1 | 95% percentile |
| H22 | mean_coupling_Jbar (content) | 4 (10 units) | 90% percentile |
| H23 | leader_corpus_marker_rate (native, #44) | 1 | 95% percentile |
| H24 | alignment_step_at_switch_on (native, #21) | 1 | 90% percentile |
| H25 | loop_gain_g_daily_dial (activity, talk, content) | 35 | SE → z (90%) |
| H26 | room_excess_gain_day (content, activity, talk) | 10 (16 units) | 95% percentile |
| H28 | link_coupling_kappa | 14 | SE → z |
| H29 | net_pull_kappa | 8 (12 units) | 95% percentile |
| H30 | chi_act (N_tgt, H_und) | 16 | 95% percentile |
| H33 | two_lines_slope_b1, b2 | 14 | CR1 SE → t |
| H34 | branching_ratio_R, exposure_hazard_ratio_HR10 | 32 | 95% percentile / profile |
| H37 | negative_stance_share | 4 | 90% percentile |
| H38 | excess_gain_raw, f_scaffold | 35 | none |
| H39 | catalytic_K, field_phi (per lever, status ok) | 30 | 95% percentile |

**Not backfilled (and why):**
- H04: only NE rows (NE10 pre/post); its weekly values are H19's construction.
- H06: outputs regenerated 2026-10-03 with empty README results (unstable).
- H07, H09, H32: no per-period file.
- H27: per-period AUC from 0–2 onsets, mostly null.
- H31: only a predictor (λ₂) is per block; consensus times are per event and censored.
- H35: card still says "Results: Pending"; confirm with the owner.
- H36: one kickoff score per period; no per-period alarm table.
- H40–H58: not run yet.
- Transition rows (H10 NE34, H12 NE34 kickoffs): no single-period meaning.

**Values that will move in the re-evaluation wave:**
- `activity_bins` drops a day-specific share of events (DQ8 finding, `activity_bins_fixed.py`). Every activity/talk statistic built from it shifts: H02, H05, H12, H13, H19, H22, H25, H26, H30, H38 and others.
- H11 labels move to `project_states`, which changes H11, H27, H28 and H31.
- Behavior states move to Jev v3, which changes H14, H16, H17 and H39.
- H01's #38 kickoff vectors are swapped, which affects G38 in H01, H10 and H20.

Rows carry `source_mtime`, so stale rows are easy to find. Re-run the backfill (or have the hypotheses write their own rows) after the rebuild.
