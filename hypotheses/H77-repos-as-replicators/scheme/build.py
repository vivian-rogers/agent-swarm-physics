"""H77 / H78 scheme: host labels, events and swarm call-clock bins per goal period (shared builder
infra/shared/replicator_hosts.py). Writes data/processed/<hyp>/G<NN>/ (repo names hashed; no text):
  events.parquet   agent, t, kind (recruit/birth/depart/expire/leave), repo, to_repo, n_before, cls, named
  bins.parquet     per (repo, swarm call-clock bin of B = 200 calls): n, n_cum, C, C_host, C_free, recruit counts by class,
                   births, departs, expires, new contributors, t0, unit
  labs.parquet     per (repo, bin, lab): n_same, n_cross, C_free_lab, R (formation-free recruits by that lab)
  choice.parquet   conditional-logit choice sets (eid, repo, n, chosen)
  repos.parquet    repo hash, named (H54 rule), n_commits, first commit time
  bin_time.parquet bin -> t0, active hours since the period start (for the A0 ramp)
  G44/arm_<room>/  the same per room arm (agents assigned to the room on most of their calls)
Usage: uv run python hypotheses/H77-repos-as-replicators/scheme/build.py --hyp H77 [--periods 31 33 ...] [--allow-holdout]
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
import replicator_hosts as R  # noqa: E402
from common import REVISION, git_commit  # noqa: E402

DIRS = {"H77": ROOT / "data/processed/H77-repos-as-replicators", "H78": ROOT / "data/processed/H78-replicator-growth-order"}
PERIODS = {"H77": [31, 33, 39, 40, 41, 42, 44, 51], "H78": [31, 33, 39, 40, 41, 42, 44, 51]}


def active_hours(bt: pl.DataFrame) -> pl.DataFrame:
    cal = pl.read_parquet(R.SHARED / "calendar.parquet", columns=["pt_date", "win_start", "active_offset_s"])
    b = bt.select("bin", "t0").unique().with_columns(
        pl.col("t0").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias("pt_date"))
    b = b.join(cal, on="pt_date", how="left").with_columns(
        ((pl.col("active_offset_s") + (pl.col("t0") - pl.col("win_start")).dt.total_seconds().clip(lower_bound=0)) / 3600).alias("t_act_h"))
    b = b.with_columns((pl.col("t_act_h") - pl.col("t_act_h").min()).alias("t_act_h"))
    return b.select("bin", "t0", "t_act_h").sort("bin")


def write_set(out: Path, d: dict, goal_no: int):
    out.mkdir(parents=True, exist_ok=True)
    ev, bt, lt = d["events"], d["bins"], d["labs"]
    R.hashed(ev).write_parquet(out / "events.parquet")
    R.hashed(bt).write_parquet(out / "bins.parquet")
    R.hashed(lt).write_parquet(out / "labs.parquet")
    R.hashed(R.choice_sets(ev)).write_parquet(out / "choice.parquet")
    cm = d["commits"].group_by("repo").agg(pl.len().alias("n_commits"), pl.col("t").min().alias("first_t"))
    rp = cm.with_columns(pl.col("repo").replace_strict(d["named"], default=False).alias("named"))
    R.hashed(rp).write_parquet(out / "repos.parquet")
    active_hours(bt).write_parquet(out / "bin_time.parquet")


def arm_agents(goal_no: int, days: list[str], calls: pl.DataFrame) -> dict[int, list[int]]:
    """Room arm per agent: the room it sat in at most of its calls (rooms_timeline intervals)."""
    rt = pl.read_parquet(R.SHARED / "rooms_timeline.parquet")
    out: dict[int, list[int]] = {}
    for (a,), g in calls.group_by(["agent"]):
        r = rt.filter(pl.col("agent") == a)
        best, cnt = None, -1
        for room, ts, te in r.select("room", "t_start", "t_end").iter_rows():
            te = te or dt.datetime(2100, 1, 1, tzinfo=dt.timezone.utc)
            k = g.filter((pl.col("t_call") >= ts) & (pl.col("t_call") < te)).height
            if k > cnt:
                best, cnt = room, k
        if best is not None and cnt > 0:
            out.setdefault(int(best), []).append(int(a))
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--hyp", choices=["H77", "H78"], required=True)
    ap.add_argument("--periods", type=int, nargs="*")
    ap.add_argument("--allow-holdout", action="store_true")
    ap.add_argument("--out", default=None)
    a = ap.parse_args()
    base = Path(a.out) if a.out else DIRS[a.hyp]
    periods = a.periods or PERIODS[a.hyp]
    t0 = time.time()
    summary = {}
    for g in periods:
        d = R.build_period(g, allow_holdout=a.allow_holdout)
        out = base / f"G{g:02d}"
        write_set(out, d, g)
        summary[g] = {"calls": d["calls"].height, "commits": d["commits"].height,
                      "events": dict(d["events"].group_by("kind").len().iter_rows())}
        if g == 44:
            arms = arm_agents(g, d["days"], d["calls"])
            labs = dict(R.roster().select("agent", "lab").iter_rows())
            for room, ags in arms.items():
                calls = d["calls"].filter(pl.col("agent").is_in(ags))
                com = d["commits"].filter(pl.col("agent").is_in(ags))
                if com.height == 0:
                    continue
                ev, bt, lt = R.build_from_frames(com, calls, d["unit_map"], labs, d["named"], g, d["days"], leave=d["leave"])
                write_set(out / f"arm_{room}", {**d, "events": ev, "bins": bt, "labs": lt, "commits": com}, g)
                summary[f"44_arm_{room}"] = {"agents": ags, "commits": com.height}
        print(f"G{g:02d} done ({time.time() - t0:.0f}s)", flush=True)
    prov = {"built_by": "hypotheses/H77-repos-as-replicators/scheme/build.py (shared builder infra/shared/replicator_hosts.py)",
            "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["work_commits (DQ4)", "call_windows (DQ1)", "context_ledger_items (DQ1)", "artifact_mentions",
                                   "artifacts", "chat_core", "chat_text (kickoff naming, in memory)", "roster", "rooms_timeline",
                                   "period_units", "calendar", "village_goals"]}],
            "params": {**R.DEFAULTS, "blind_window_s": R.BLIND_S, "periods": periods, "allow_holdout": a.allow_holdout,
                       "hypothesis": a.hyp},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat(), "summary": {str(k): v for k, v in summary.items()}}
    (base / "_provenance.json").write_text(json.dumps(prov, indent=1, default=str))


if __name__ == "__main__":
    main()
