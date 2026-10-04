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
  project_states       project_states
  kicks_classified     kicks_classified
  text_features        text_features
  build_embeddings_v2  second embedding model gte-modernbert (expensive: ~46 min on MPS)
  style_resid          32-d whitened and style-residualized statement / agent vectors (both models)
  statement_flags      self_repeat / cross_echo / templated per model + _both consensus
  embedding_agreement  bge vs gte agreement metrics
  outages              outages, stall_minutes, reasons (H38's rule; idle spells recomputed with H09's rule)
  context_ledger       call_starts_logged (raw scan), call_windows, context_ledger_turns/_items (+ validation JSON)
  work_ledger          work_repos, work_commits, work_api_writes, work_daily, work_outcomes (offline; `work_ledger.py refresh` refetches)
  ground_truth         ground_truth_labels (one gzip+grep pass over raw computer_use_turns)
  period_affordances   period_affordances (DQ9 catalog; event columns null on holdout units)
  activity_bins_fixed  sidecar check: activity_bins rebuilt with the (pt_date, minute, agent) join (build_derived now does this itself)
  null_sizes           DQ8 null size table (expensive, ~4 min)
  per_period_estimates DQ8 per-period estimates backfill
  reply_*              reply_pairs, reply_graph (DQ2: candidates, ledger candidates, validate, compile; no API calls)
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
    {"name": "context_ledger", "cmd": "py", "script": "context_ledger.py",
     "outputs": ["call_starts_logged.parquet", "call_windows.parquet", "context_ledger_turns.parquet",
                 "context_ledger_items.parquet"]},
    {"name": "ground_truth", "cmd": "py", "script": "ground_truth.py", "outputs": ["ground_truth_labels.parquet"]},
    {"name": "period_affordances", "cmd": "py", "script": "period_affordances.py", "outputs": ["period_affordances.parquet"]},
    # DQ2 reply threading: rebuild never calls the Jev API (`reply_threading.py label --phase ...` is manual)
    {"name": "reply_candidates", "cmd": "py", "script": "reply_threading.py", "args": ["candidates"], "outputs": []},
    {"name": "reply_candidates_ledger", "cmd": "py", "script": "reply_threading.py",
     "args": ["candidates", "--visibility", "ledger"], "outputs": []},
    {"name": "reply_validate", "cmd": "py", "script": "reply_threading.py", "args": ["validate"], "outputs": []},
    {"name": "reply_compile", "cmd": "py", "script": "reply_threading.py", "args": ["compile"],
     "outputs": ["reply_pairs.parquet", "reply_graph.parquet"]},
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
            status = "present" if outputs_exist(s) else "missing"
            print(f"{i:2d}. {s['name']:<21} {status:<8}  {cmd}")
            for o in s["outputs"]:
                print(f"      {'+' if (OUT / o).exists() else '-'} {o}")
        return

    env = env_for(a.threads)
    run_id = dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")
    timings, t_all = [], time.time()
    for s in steps:
        name = s["name"]
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
