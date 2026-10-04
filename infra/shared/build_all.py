"""One entry point for the shared postprocessing pipeline: runs every shared builder in dependency order, one at a
time, each in its own process (thread caps set in the environment), with timing.

Steps (outputs in data/processed/shared/):
  scan_tables          raw -> roster, rooms, events_core, intentions(+_text), chat_core(+_text), actions, memory_stats
  build_derived        calendar, rooms_timeline, exposure, activity_bins, kicks (also labels `automated` in chat_core)
  build_embeddings     embeddings/{chat,intentions}_bge_small.npy (+ index)        [expensive: skipped when present]
  build_agent_vectors  embeddings/statements, agent_day, agent_win30, whitening_<regime>
  build_mentions_clean chat_mentions_clean
  build_artifacts      artifact_commands_text (raw scan), artifacts, artifact_mentions
  turn_errors          turn_errors, sessions, actions_bash_head_fixed (one raw pass over computer_use_turns, ~80 s)
  goal_fields          embeddings/goals.parquet + goal_vectors.npy
  period_units         period_units, period_step_changes
  behavior_states      states_turn, states_min
  turn_outcomes        DQ3 raw pass: real failures vs stderr, artifact-change evidence, command text (expensive, ~8 min)
  behavior_states_v3   DQ3 Jev v3.1 states compiled from stored answers (labelling itself is paid and manual)
  project_states       project_states
  kicks_classified     kicks_classified
  text_features        text_features
  build_embeddings_v2  second embedding model gte-modernbert (expensive: ~46 min on MPS)
  style_resid          32-d whitened and style-residualized statement / agent vectors (both models)
  statement_flags      self_repeat / cross_echo / templated per model + _both consensus
  embedding_agreement  bge vs gte agreement metrics
  outages              outages, stall_minutes, reasons (H38's rule; idle spells recomputed with H09's rule)
  context_ledger       call_starts_logged (raw scan), call_windows, context_ledger_turns/_items (+ validation JSON)
  visibility           producing_calls (H28/H32/H34 "seen iff posted before the producing call's t_call"; + helpers)
  pair_day_reads       pair_day_reads (H05's ledger read counts per pair-day)
  kicks_targets        kicks_targets, kicks_receipts (leading-@ primary target; receiving call per message x agent)
  calls                calls (H15/H44 regime-III per-call failures, write evidence, work commits, segments)
  sustained_runs       sustained_run_starts (H35 and H43 rules)
  copying              project_mentions_chat (+ H06's MH copying test as functions)
  (each of these six takes --verify against the hypothesis copies it replaced; steps carry `deps`, shown by --list)
  work_ledger          work_repos, work_commits, work_api_writes, work_daily, work_outcomes (offline; `work_ledger.py refresh` refetches)
  ground_truth         ground_truth_labels (one gzip+grep pass over raw computer_use_turns)
  period_affordances   period_affordances (DQ9 catalog; event columns null on holdout units)
  activity_bins_fixed  sidecar check: activity_bins rebuilt with the (pt_date, minute, agent) join (build_derived now does this itself)
  null_sizes           DQ8 null size table (expensive, ~4 min)
  per_period_estimates DQ8 per-period estimates backfill
  reply_*              reply_pairs, reply_graph (DQ2: candidates, ledger candidates, validate, compile; no API calls)
  stance_v2_validate_* DQ10 stance v2 validation records (gate failed: no reply_stance_v2 table); no API calls
  blind_reference_v31  DQ10 fresh blind reference for behavior states v3.1 (kappa, confusion); no API calls
  round-2 consolidation (2026-10-04; each takes --verify against the hypothesis copies it replaced):
  pending_sets         pending_sets/G<NN>/ (H18 ledger k: talks, pending, invisible, wakes, wake_pending; non-holdout)
  event_catalog        event_catalog, event_catalog_days (H56's dated step-change catalog; all days, holdout0 flagged)
  schema_diff          schema_diff/ signatures_daily, signature_dict, search_format, schema_diff_daily (H74; raw pass ~75 s)
  style_features       style_messages, style_standardization.json, style_ne41_pairs (H46 / H73 style ruler, NE41 pairs)
  idle_gates           idle_gates/idle_gates.parquet (H60 / H72 gates, trap clocks, in-flight placebo counts)
  day_matrices         day_matrices/ content_<model>{,_style_resid_period,_restate}.npz, spins.npz, rooms, days (H91 / H92)
  culture_vectors      culture_vectors/ agentdays, vecs_<model>_<variant>.npy, dirs_<model>, blocks (H81 / H82)
  libraries (lib: no build step; `--verify` runs their self-checks / reproductions): hazard_fe, semantic_kappa,
  kickoff_naming, idea_markers, idea_ledger, replicator_hosts, replicator_fit, replicator_sim, read_response,
  ep_newton (Newton-step EP estimators, legacy + corrected; 2026-10-04)
Tests (--tests): infra/shared/tests/test_*.py

Usage:
  uv run python infra/shared/build_all.py --list                     steps, commands, outputs and whether they exist
  uv run python infra/shared/build_all.py                            run everything (embeddings skipped when present)
  uv run python infra/shared/build_all.py --skip-existing            skip every step whose outputs all exist
  uv run python infra/shared/build_all.py --only goal_fields,text_features
  uv run python infra/shared/build_all.py --from goal_fields         this step and everything after it
  uv run python infra/shared/build_all.py --force-embeddings         re-embed even if the vectors exist
  uv run python infra/shared/build_all.py --dry-run                  print what would run
  uv run python infra/shared/build_all.py --tests                    run the tests after the steps (or alone with --only none)
  uv run python infra/shared/build_all.py --verify --only pending_sets,read_response
                                                                     run `<script> --verify` instead of building, for every
                                                                     selected step whose script has one (libraries included)
  --threads N   thread cap exported to every step (POLARS_MAX_THREADS, OMP/BLAS; default 2)
Each run appends one line per step to data/processed/shared/build_all.log.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OUT = ROOT / "data/processed/shared"
ST = ["uv", "run", "--with", "sentence-transformers", "python"]  # steps that embed text (offline HF cache)

STEPS = [
    {"name": "scan_tables", "cmd": "py", "script": "scan_tables.py",
     "outputs": ["roster.parquet", "rooms.parquet", "events_core.parquet", "intentions.parquet", "intentions_text.parquet",
                 "chat_core.parquet", "chat_text.parquet", "actions.parquet", "memory_stats.parquet"]},
    {"name": "build_derived", "cmd": "py", "script": "build_derived.py",
     "outputs": ["calendar.parquet", "rooms_timeline.parquet", "exposure.parquet", "activity_bins.parquet", "kicks.parquet"]},
    {"name": "activity_bins_fixed", "cmd": "py", "script": "activity_bins_fixed.py", "outputs": ["activity_bins_fixed.parquet"]},
    {"name": "build_embeddings", "cmd": "st", "script": "build_embeddings.py", "expensive": True,
     "outputs": ["embeddings/chat_bge_small.npy", "embeddings/chat_index.parquet", "embeddings/intentions_bge_small.npy",
                 "embeddings/intentions_index.parquet"]},
    {"name": "build_agent_vectors", "cmd": "py", "script": "build_agent_vectors.py",
     "outputs": ["embeddings/statements.parquet", "embeddings/agent_day.parquet", "embeddings/agent_day_vec.npy",
                 "embeddings/agent_win30.parquet", "embeddings/agent_win30_vec.npy", "embeddings/whitening_III.npz"]},
    {"name": "build_mentions_clean", "cmd": "py", "script": "build_mentions_clean.py", "outputs": ["chat_mentions_clean.parquet"]},
    {"name": "build_artifacts", "cmd": "py", "script": "build_artifacts.py",
     "outputs": ["artifact_commands_text.parquet", "artifacts.parquet", "artifact_mentions.parquet"]},
    {"name": "turn_errors", "cmd": "py", "script": "turn_errors.py",
     "outputs": ["turn_errors.parquet", "sessions.parquet", "actions_bash_head_fixed.parquet"]},
    {"name": "work_ledger", "cmd": "py", "script": "work_ledger.py",
     "outputs": ["work_repos.parquet", "work_commits.parquet", "work_api_writes.parquet", "work_daily.parquet",
                 "work_outcomes.parquet", "work_ledger_validation.json"]},
    {"name": "goal_fields", "cmd": "st", "script": "goal_fields.py",
     "outputs": ["embeddings/goals.parquet", "embeddings/goal_vectors.npy"]},
    {"name": "period_units", "cmd": "py", "script": "period_units.py",
     "outputs": ["period_units.parquet", "period_step_changes.parquet"]},
    {"name": "behavior_states", "cmd": "py", "script": "behavior_states.py", "outputs": ["states_turn.parquet", "states_min.parquet"]},
    # DQ3 Jev v3.1 states: the raw outcome scan is expensive; labelling is paid and manual
    # (`label_v3.py --all --max-usd 15`, ~$13, resumable); the rebuild only recompiles from the stored answers.
    {"name": "turn_outcomes", "cmd": "py", "script": "../behavior_states/scan_turn_outcomes.py", "expensive": True,
     "outputs": ["../behavior_states/turn_outcomes.parquet"]},
    {"name": "behavior_states_v3", "cmd": "py", "script": "../behavior_states/label_v3.py", "args": ["--all", "--compile-only"],
     "outputs": ["behavior_states_v3.parquet"]},
    {"name": "project_states", "cmd": "py", "script": "project_states.py", "outputs": ["project_states.parquet"]},
    {"name": "kicks_classified", "cmd": "py", "script": "kicks_classified.py", "outputs": ["kicks_classified.parquet"]},
    {"name": "text_features", "cmd": "py", "script": "text_features.py", "outputs": ["text_features.parquet"]},
    {"name": "build_embeddings_v2", "cmd": "st", "script": "build_embeddings_v2.py", "expensive": True,
     "outputs": ["embeddings/chat_gte_modernbert.npy", "embeddings/intentions_gte_modernbert.npy",
                 "embeddings/agent_day_vec_gte_modernbert.npy", "embeddings/agent_win30_vec_gte_modernbert.npy",
                 "embeddings/whitening_gte_modernbert_III.npz", "embeddings/goal_vectors_gte_modernbert.npy"]},
    {"name": "style_resid", "cmd": "py", "script": "style_resid.py",
     "outputs": ["embeddings/statements_style_resid_period32_bge_small.npy",
                 "embeddings/statements_style_resid_period32_gte_modernbert.npy",
                 "embeddings/agent_day_style_resid_period_gte_modernbert.npy",
                 "embeddings/agent_win30_style_resid_gte_modernbert.npy"]},
    {"name": "statement_flags", "cmd": "st", "script": "statement_flags.py",
     "outputs": ["statement_flags.parquet", "statement_flags_meta.json", "statement_flags_by_period.parquet"]},
    {"name": "embedding_agreement", "cmd": "py", "script": "embedding_agreement.py",
     "outputs": ["embeddings/agreement_gte_modernbert.parquet"]},
    {"name": "outages", "cmd": "py", "script": "outages.py",
     "outputs": ["outages.parquet", "stall_minutes.parquet", "reasons.parquet"]},
    {"name": "outages_fixed", "cmd": "py", "script": "outages.py", "args": ["--fixed"],
     "outputs": ["outages_fixed/outages.parquet", "outages_fixed/stall_minutes.parquet", "outages_fixed/reasons.parquet"]},
    {"name": "context_ledger", "cmd": "py", "script": "context_ledger.py",
     "outputs": ["call_starts_logged.parquet", "call_windows.parquet", "context_ledger_turns.parquet",
                 "context_ledger_items.parquet"]},
    # helpers consolidated from hypothesis folders (2026-10-04); each script also takes --verify against its originals
    {"name": "visibility", "cmd": "py", "script": "visibility.py", "deps": ["scan_tables", "context_ledger"],
     "outputs": ["producing_calls.parquet"]},
    {"name": "pair_day_reads", "cmd": "py", "script": "pair_day_reads.py", "deps": ["context_ledger"],
     "outputs": ["pair_day_reads.parquet"]},
    {"name": "kicks_targets", "cmd": "py", "script": "kicks_targets.py", "deps": ["kicks_classified", "context_ledger"],
     "outputs": ["kicks_targets.parquet", "kicks_receipts.parquet"]},
    {"name": "calls", "cmd": "py", "script": "calls.py",
     "deps": ["scan_tables", "turn_errors", "turn_outcomes", "work_ledger", "context_ledger"], "outputs": ["calls.parquet"]},
    {"name": "sustained_runs", "cmd": "py", "script": "sustained_runs.py", "deps": ["context_ledger"],
     "outputs": ["sustained_run_starts.parquet"]},
    {"name": "copying", "cmd": "py", "script": "copying.py", "deps": ["scan_tables", "build_artifacts", "context_ledger"],
     "outputs": ["project_mentions_chat.parquet"]},
    {"name": "ground_truth", "cmd": "py", "script": "ground_truth.py", "outputs": ["ground_truth_labels.parquet"]},
    {"name": "period_affordances", "cmd": "py", "script": "period_affordances.py", "outputs": ["period_affordances.parquet"]},
    # DQ2 reply threading: rebuild never calls the Jev API (`reply_threading.py label --phase ...` is manual)
    {"name": "reply_candidates", "cmd": "py", "script": "reply_threading.py", "args": ["candidates"], "outputs": []},
    {"name": "reply_candidates_ledger", "cmd": "py", "script": "reply_threading.py",
     "args": ["candidates", "--visibility", "ledger"], "outputs": []},
    {"name": "reply_validate", "cmd": "py", "script": "reply_threading.py", "args": ["validate"], "outputs": []},
    {"name": "reply_compile", "cmd": "py", "script": "reply_threading.py", "args": ["compile"],
     "outputs": ["reply_pairs.parquet", "reply_graph.parquet"]},
    # DQ10 stance v2: rebuild never calls the Jev API (`stance_v2.py label --phase ...` is manual and capped)
    # validation records (the v2.0 draft, v2.1 on the draft, v2.1 on the fresh sheet); the gate failed 2026-10-04, so no
    # reply_stance_v2.parquet is built and the compile step (which refuses without a passed gate) is not registered
    {"name": "stance_v2_validate_draft", "cmd": "py", "script": "stance_v2.py",
     "args": ["validate", "--which", "draft", "--taxonomy", "stance-v2.0"], "deps": ["reply_compile"], "outputs": []},
    {"name": "stance_v2_validate_draft_v21", "cmd": "py", "script": "stance_v2.py",
     "args": ["validate", "--which", "draft", "--taxonomy", "stance-v2.1"], "deps": ["reply_compile"], "outputs": []},
    {"name": "stance_v2_validate_fresh", "cmd": "py", "script": "stance_v2.py",
     "args": ["validate", "--which", "fresh", "--taxonomy", "stance-v2.1"], "deps": ["reply_compile"], "outputs": []},
    {"name": "blind_reference_v31", "cmd": "py", "script": "../behavior_states/blind_reference_v3.py", "args": ["compare"],
     "deps": ["behavior_states_v3"], "outputs": []},
    # round-2 consolidation (2026-10-04): builders moved out of hypothesis folders; each takes --verify
    {"name": "pending_sets", "cmd": "py", "script": "pending_sets.py",
     "deps": ["scan_tables", "build_derived", "build_mentions_clean", "context_ledger", "reply_compile"],
     "outputs": ["pending_sets/_provenance.json", "pending_sets/G51/talks.parquet", "pending_sets/G51/pending.parquet"]},
    {"name": "event_catalog", "cmd": "py", "script": "event_catalog.py",
     "deps": ["build_derived", "period_units", "kicks_classified"],
     "outputs": ["event_catalog.parquet", "event_catalog_days.parquet"]},
    {"name": "schema_diff", "cmd": "py", "script": "schema_diff.py", "deps": ["scan_tables", "build_derived", "context_ledger"],
     "outputs": ["schema_diff/signatures_daily.parquet", "schema_diff/signature_dict.parquet",
                 "schema_diff/search_format.parquet", "schema_diff/schema_diff_daily.parquet"]},
    {"name": "style_features", "cmd": "py", "script": "style_features.py",
     "deps": ["text_features", "build_agent_vectors", "statement_flags", "period_units", "context_ledger"],
     "outputs": ["style_messages.parquet", "style_standardization.json", "style_ne41_pairs.parquet"]},
    {"name": "idle_gates", "cmd": "py", "script": "idle_gates.py",
     "deps": ["scan_tables", "build_derived", "build_embeddings", "statement_flags", "period_units", "context_ledger"],
     "outputs": ["idle_gates/idle_gates.parquet"]},
    {"name": "day_matrices", "cmd": "py", "script": "day_matrices.py",
     "deps": ["build_derived", "period_units", "activity_bins_fixed", "build_agent_vectors", "build_embeddings_v2",
              "style_resid", "statement_flags"],
     "outputs": ["day_matrices/content_bge.npz", "day_matrices/content_gte.npz", "day_matrices/spins.npz",
                 "day_matrices/days.parquet", "day_matrices/rooms.parquet"]},
    {"name": "culture_vectors", "cmd": "py", "script": "culture_vectors.py",
     "deps": ["build_agent_vectors", "build_embeddings_v2", "style_resid", "goal_fields", "kicks_classified",
              "period_units"],
     "outputs": ["culture_vectors/agentdays.parquet", "culture_vectors/blocks.parquet",
                 "culture_vectors/dirs_bge_small.npz", "culture_vectors/dirs_gte_modernbert.npz"]},
    # libraries: nothing to build; registered so that --verify runs their checks and --list shows their deps
    {"name": "hazard_fe", "cmd": "py", "script": "hazard_fe.py", "lib": True, "deps": [], "outputs": []},
    {"name": "semantic_kappa", "cmd": "py", "script": "semantic_kappa.py", "lib": True, "deps": [], "outputs": []},
    {"name": "kickoff_naming", "cmd": "py", "script": "kickoff_naming.py", "lib": True, "deps": ["build_artifacts"],
     "outputs": []},
    {"name": "idea_markers", "cmd": "py", "script": "idea_markers.py", "lib": True,
     "deps": ["scan_tables", "build_artifacts"], "outputs": []},
    {"name": "idea_ledger", "cmd": "py", "script": "idea_ledger.py", "lib": True,
     "deps": ["scan_tables", "build_mentions_clean", "context_ledger", "reply_compile"], "outputs": []},
    {"name": "replicator_hosts", "cmd": "py", "script": "replicator_hosts.py", "lib": True,
     "deps": ["work_ledger", "context_ledger", "build_artifacts", "goal_fields", "period_units", "kickoff_naming"],
     "outputs": []},
    {"name": "replicator_fit", "cmd": "py", "script": "replicator_fit.py", "lib": True, "deps": ["replicator_hosts"],
     "outputs": []},
    {"name": "replicator_sim", "cmd": "py", "script": "replicator_sim.py", "lib": True,
     "deps": ["replicator_hosts", "replicator_fit"], "outputs": []},
    {"name": "read_response", "cmd": "py", "script": "read_response.py", "lib": True,
     "deps": ["build_agent_vectors", "build_embeddings_v2", "style_resid", "goal_fields"], "outputs": []},
    {"name": "ep_newton", "cmd": "py", "script": "ep_newton.py", "lib": True, "deps": [], "outputs": []},
    {"name": "null_sizes", "cmd": "py", "script": "nulls.py", "args": ["--calibrate", "--reps", "100", "--surr", "49", "--workers", "2"],
     "expensive": True, "outputs": ["null_sizes.parquet"]},
    {"name": "per_period_estimates", "cmd": "py", "script": "estimates.py", "args": ["--backfill"],
     "outputs": ["per_period_estimates.parquet"]},
]
NAMES = [s["name"] for s in STEPS]


def command(step: dict) -> list[str]:
    path = str(HERE / step["script"])
    base = [sys.executable, path] if step["cmd"] == "py" else ST + [path]
    return base + list(step.get("args", []))


def has_verify(step: dict) -> bool:
    """The step's script takes --verify (steps with extra args share a script with a plain step: verified once there)."""
    if step.get("args"):
        return False
    txt = (HERE / step["script"]).read_text()
    return '"--verify" in sys.argv' in txt or 'add_argument("--verify"' in txt


def outputs_exist(step: dict) -> bool:
    return bool(step["outputs"]) and all((OUT / o).exists() for o in step["outputs"])


def env_for(threads: int) -> dict:
    env = dict(os.environ)
    for v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
              "NUMEXPR_NUM_THREADS"):
        env[v] = str(threads)
    env.setdefault("UV_OFFLINE", "1")
    env.setdefault("HF_HUB_OFFLINE", "1")
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    return env


def log(line: dict):
    OUT.mkdir(parents=True, exist_ok=True)
    with open(OUT / "build_all.log", "a") as f:
        f.write(json.dumps(line) + "\n")


def run_tests(env) -> int:
    fails = 0
    for t in sorted((HERE / "tests").glob("test_*.py")):
        t0 = time.time()
        r = subprocess.run([sys.executable, str(t)], env=env, cwd=ROOT)
        print(f"[tests] {t.name}: {'ok' if r.returncode == 0 else 'FAILED'} ({time.time() - t0:.1f}s)", flush=True)
        fails += r.returncode != 0
    return fails


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--only", help="comma-separated step names (or 'none' with --tests)")
    ap.add_argument("--from", dest="start", help="start at this step")
    ap.add_argument("--skip-existing", action="store_true", help="skip steps whose outputs all exist")
    ap.add_argument("--force-embeddings", action="store_true", help="re-run build_embeddings even if its outputs exist")
    ap.add_argument("--list", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--tests", action="store_true")
    ap.add_argument("--verify", action="store_true", help="run each selected step's `--verify` instead of building it")
    ap.add_argument("--threads", type=int, default=2)
    a = ap.parse_args()

    steps = STEPS
    if a.only:
        want = [x.strip() for x in a.only.split(",") if x.strip()]
        unknown = [w for w in want if w not in NAMES + ["none"]]
        if unknown:
            sys.exit(f"unknown step(s) {unknown}; steps: {', '.join(NAMES)}")
        steps = [s for s in STEPS if s["name"] in want]
    if a.start:
        if a.start not in NAMES:
            sys.exit(f"unknown step {a.start}; steps: {', '.join(NAMES)}")
        steps = [s for s in steps if NAMES.index(s["name"]) >= NAMES.index(a.start)]

    if a.list:
        for i, s in enumerate(STEPS, 1):
            cmd = " ".join(Path(c).name if c.endswith(".py") else c for c in command(s))
            status = "library" if s.get("lib") else ("present" if outputs_exist(s) else "missing")
            print(f"{i:2d}. {s['name']:<21} {status:<8}  {cmd}{'   [--verify]' if has_verify(s) else ''}")
            if s.get("deps"):
                print(f"      deps: {', '.join(s['deps'])}")
            for o in s["outputs"]:
                print(f"      {'+' if (OUT / o).exists() else '-'} {o}")
        return

    env = env_for(a.threads)
    run_id = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    timings, t_all = [], time.time()
    for s in steps:
        name = s["name"]
        if a.verify:
            if not has_verify(s):
                continue
            cmd = command(s) + ["--verify"]
            if a.dry_run:
                print(f"[{name}] would verify: {' '.join(cmd)}")
                continue
            print(f"[{name}] verifying: {' '.join(cmd)}", flush=True)
            t0 = time.time()
            r = subprocess.run(cmd, env=env, cwd=ROOT)
            el = time.time() - t0
            status = "verified" if r.returncode == 0 else f"failed ({r.returncode})"
            timings.append((name, status, el))
            log({"run": run_id, "step": name, "status": status, "mode": "verify", "seconds": round(el, 1)})
            print(f"[{name}] {status} in {el:.1f}s", flush=True)
            continue
        if s.get("lib"):
            print(f"[{name}] library: nothing to build (run with --verify)", flush=True)
            continue
        skip = (a.skip_existing and outputs_exist(s)) or (s.get("expensive") and outputs_exist(s) and not a.force_embeddings)
        if skip:
            print(f"[{name}] skipped (outputs present)", flush=True)
            timings.append((name, "skipped", 0.0)); log({"run": run_id, "step": name, "status": "skipped"})
            continue
        cmd = command(s)
        if a.dry_run:
            print(f"[{name}] would run: {' '.join(cmd)}")
            continue
        print(f"[{name}] running: {' '.join(cmd)}", flush=True)
        t0 = time.time()
        r = subprocess.run(cmd, env=env, cwd=ROOT)
        el = time.time() - t0
        status = "ok" if r.returncode == 0 else f"failed ({r.returncode})"
        timings.append((name, status, el))
        log({"run": run_id, "step": name, "status": status, "seconds": round(el, 1), "threads": a.threads})
        print(f"[{name}] {status} in {el:.1f}s", flush=True)
        if r.returncode != 0:
            print("stopping: later steps depend on this one", flush=True)
            break
    if a.tests and not a.dry_run:
        fails = run_tests(env)
        timings.append(("tests", "ok" if not fails else f"{fails} failed", 0.0))
    if timings:
        print("\nstep                  status      seconds")
        for n, st, el in timings:
            print(f"{n:<21} {st:<11} {el:8.1f}")
        print(f"total {time.time() - t_all:.1f}s")
    if any(st.startswith("failed") for _, st, _ in timings):
        sys.exit(1)


if __name__ == "__main__":
    main()
