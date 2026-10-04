# DQ3: Jev behavior states v3 and the full run

Code is in `infra/behavior_states/`; design, validation and decision are in `infra/behavior_states/DESIGN.md` ("v3 and full run").

## Status (2026-10-04)
**Labelled:** 203,170 of 206,483 active windows (98.4%); non-holdout coverage is 100%.
- 3,313 windows on 2026-09-16 to 09-18 (goal #51, holdout) failed with HTTP 402: the shared OpenRouter account ran out of credit.
- Finish after a top-up with `label_v3.py --all --retry-errors` (about $0.22), then `--all --compile-only`.

**Spend:** $13.13 total for v3 ($0.093 validation, $13.04 full run), against the $15 cap.

**Validation:**
- κ 0.38 vs the blind Claude labels made on the v1 state (v2: 0.50); 68% agreement at conf ≥ 0.8 (v2: 87%).
- blocked κ 0.50 (v2: 0.38); others_work κ 0.41 (v2: 0.27).
- In the 41 windows where git printed a commit/push or a deploy ran, v3 says execute_task 100% of the time (v2: 44%).
- Two blinded A/B audits on the full evidence: v3 right 34, v2 right 15, both acceptable 13.
- Full run on v3.1; the deviation from the pre-written κ criterion is explained in DESIGN.md.

## Outputs

**`data/processed/shared/behavior_states_v3.parquet`** has one row per roster agent × 5-minute window of every calendar day (the `activity_bins` grid; Claude Code agent excluded). It covers all days, holdout included, and flags them with `holdout`. Inactive windows are kept with `labeled = false`. There is no text in the table.

- **Keys:** `pt_date`, `agent`, `w` (= minute // 5 of `activity_bins`), `t0`, `t1`, `goal_no`, `regime`, `holdout`, `active`, `in_span` (between the agent's first and last active window that day), `labeled`.
- **Behavior:**
  - `behavior` (argmax choice) and `behavior_conf`;
  - the full probability vector: `p_plan_coordinate`, `p_execute_task`, `p_research_browse`, `p_communicate_external`, `p_debug_recover`, `p_verify_report`, `p_monitor_wait`, `p_self_maintenance`, `p_social`, `p_meta`, `p_idle`.
  - Jev rounds to 0.01, so small probabilities are 0.
- **noul and score:**
  - `p_blocked` and `p_others_work`;
  - `p_addresses_participant`, only for windows with own chat;
  - `progress_score` (0–4), `progress_conf`, and `p_progress_0` … `p_progress_4`.
- **Assembly flags:**
  - counts from the activity grid: `n_talk`, `n_turns`, `n_idle_events`, `n_paused_min`, `n_consolidate`, `n_other_events`;
  - actions and failures: `n_actions`, `n_errors` (real failures), `n_stderr` (raw `actions.error`), `repeated_error_share`, `longest_run`, `noop_share`, `n_forced_mouse`;
  - artifact changes: `n_commit_ok`, `n_push_ok`, `n_file_write`, `n_api_write`, `n_deploy`;
  - chat: `n_own`, `has_chat`, `self_repeat_share`;
  - messages seen: `n_seen`, `n_seen_human`, `n_seen_automated`, `n_seen_mentioning`;
  - intention: `intention_age_min`, `intention_stale`, `intention_prev_day`, `intention_source`;
  - boot and reset: `first_active_window`, `min_since_first_activity`, `session_start_in_window`, `post_reset`, `declared_pause_s`;
  - bookkeeping: `state_chars` (the size of the state sent), `label_error`, `cost`.

Provenance: the `behavior_states_v3` key in `data/processed/shared/_provenance.json`, with spend, plus `data/processed/behavior_states/behavior_states_v3_provenance.json`.

**Intermediates** (gitignored, gated text, never in shared tables):
- `data/processed/behavior_states/turn_outcomes.parquet`: one row per bash/type turn, with real failures, change evidence and truncated command text;
- `jev_all_v3.jsonl.gz`: the raw Jev answers;
- `jev_draft_v3*.jsonl`: validation runs, with states.

## Text to add to `infra/README.md`

Under the built tables:

> ### Jev behavior states v3 (DQ3, 2026-10-04): `infra/behavior_states/label_v3.py`
> - **`behavior_states_v3`:** zero-shot Jev (typesafe/jev-1.13) behavior states for every agent × 5-min window, holdout included and flagged; `labeled = false` on inactive windows.
> - **Contents:**
>   - 11 states with full probability vectors (`p_*`), the argmax `behavior` and its confidence;
>   - noul probabilities `p_blocked`, `p_others_work`, `p_addresses_participant`;
>   - the progress score and its probabilities;
>   - assembly flags: real failures, artifact changes, looping, self-repeat, intention freshness, boot/reset windows.
> - **Use the probability vectors, not the argmax,** for Markov or dwell statistics. H17: argmax at κ ≈ 0.5 underestimates relaxation times 4–14×; use the shifted estimator C(1)⁻¹C(1+τ).
> - **Validation** (DESIGN.md): κ 0.38 against blind Claude labels made on the thin v1 state (v2: 0.50). But v3 wins blind audits on the full evidence 34 to 15 and labels every git-printed commit/push window execute_task (v2: 44%). blocked κ 0.50 and others_work κ 0.41 (v2: 0.38 and 0.27).
> - **Confidence is not a calibrated agreement probability.** 68% agreement with Claude at conf ≥ 0.8.
> - **H14/H17 loaders:** H14 uses `state_col='behavior', bin_col='w', day_col='pt_date'`; H17 uses `prob_cols=[c for c in df.columns if c.startswith('p_') and c[2:] in STATES]`. Mask the holdout first.
> - **Inactive windows** inside `in_span` are "idle by absence", not labelled; decide explicitly how to treat them.
> - **Rebuild:**
>   - `uv run python infra/behavior_states/scan_turn_outcomes.py` (about 8 min, one raw pass);
>   - `uv run --with httpx python infra/behavior_states/label_v3.py --all --max-usd 15` (about 30 min, about $13; resumable; skips windows already answered);
>   - `--compile-only` re-derives the table from the archived answers without calls.

Under Known issues:

> - **`actions.error` means "stderr was non-empty", not "the command failed"** (DQ3; see also `actions_bash_head_fixed.error_class`, the platform taxonomy, which agrees: use `error_class` for platform stalls and `turn_outcomes.failed` for task failures, since `failed` also catches stdout-only failures and rejected pushes). Git and curl write normal progress to stderr: 62% of `git push`, 54% of `git commit` and 49% of `git add` turns are flagged. Across bash turns, 58% of stderr flags are not failures, and 15% of real failures have empty stderr. Real failures are 6.9% of bash turns, against 14.1% with stderr.
>   - Use `data/processed/behavior_states/turn_outcomes.parquet` (`failed`, `fail_kind`) or `behavior_states_v3.n_errors`.
>   - Analyses that used `actions.error` or `artifact_commands_text.error` as failures/stuckness (H14, H16, H17, the v1/v2 Jev states) over-count failures in git-heavy work.
> - **Regime-III bash commands start with an agent comment line** (`# I'm committing …`, 75% of bash turns). `artifact_commands_text` strips comments; `turn_outcomes.note` keeps the first one (≤ 100 chars). It is agent narration: a claim, not ground truth.

## Text to add to `infra/shared/build_all.py`

Register as an optional, paid, network step, not part of the default rebuild:

```python
# DQ3 Jev behavior states v3 (network: OpenRouter Jev; ~$13; needs OPENROUTER_API_KEY in .env). Opt-in only.
OPTIONAL_STEPS["behavior_states_v3"] = [
    ["uv", "run", "python", "infra/behavior_states/scan_turn_outcomes.py"],
    ["uv", "run", "--with", "httpx", "python", "infra/behavior_states/label_v3.py", "--all", "--max-usd", "15"],
]
# Rebuilding the table from the archived answers is free and local:
STEPS.append(["uv", "run", "python", "infra/behavior_states/label_v3.py", "--all", "--compile-only"])  # after scan_turn_outcomes
```

## DQ10 fresh blind reference (2026-10-04)
200 non-holdout windows were blind-labelled on the full v3 evidence (two subagent labellers). Against v3.1:
- behavior κ 0.60 [0.52, 0.67], reweighted 0.62;
- 85% agreement at confidence ≥ 0.8 (n = 89);
- blocked κ 0.54, others_work κ 0.53, addresses κ 0.86, progress ρ 0.76;
- the two references agree with each other at κ 0.85.

Reading (pre-registered): **confirmed**. The main confusion is over-called execute_task (small own-notes commits inside checking or debugging windows). Details: `infra/behavior_states/DESIGN.md`, "Fresh blind reference on v3 states".

## Held-out #51 windows (DQ10, 2026-10-04)
The 3,313 windows left unlabelled by HTTP 402 are labelled (3,313 / 3,313, 0 errors, $0.21).
- **Where:** `data/processed/holdout_labels/behavior_states_v3_holdout.parquet` (holdout only).
- **Not merged** into `behavior_states_v3.parquet`.
- **Use:** confirm scripts join on `pt_date`, `agent`, `w`.
