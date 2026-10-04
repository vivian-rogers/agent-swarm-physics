"""H93 scheme: choice events and event x option long tables per goal period, two channels (work, attention).

  uv run python hypotheses/H93-brock-durlauf-project-choice/scheme/build.py --period 31 [--period 38 ...] [--all]

Writes data/processed/H93-brock-durlauf-project-choice/G<NN>/{events,long,occupancy}_{work,attention}.parquet (option
keys hashed; no text) and counts.json; updates _provenance.json. Holdout days are dropped (replicator_hosts.period_days
and an explicit common.holdout_mask filter). --allow-holdout exists only for analysis/confirm.py (import build_period).
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

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
sys.path.insert(0, str(HERE))
import replicator_hosts as R  # noqa: E402
from common import REVISION, git_commit, holdout_mask  # noqa: E402

import h93scheme as S  # noqa: E402

OUT = ROOT / "data/processed/H93-brock-durlauf-project-choice"
PERIODS = [30, 31, 33, 35, 36, 37, 38, 39, 40, 41, 42, 44, 51]
CLAUDE_CODE = 19


def _hash_opts(df: pl.DataFrame, cols) -> pl.DataFrame:
    for c in cols:
        if c in df.columns:
            df = df.with_columns(pl.col(c).map_elements(lambda x: x if x == S.NEW else R.rhash(x), return_dtype=pl.String).alias(c))
    return df


def build_period(g: int, allow_holdout: bool = False, write: bool = True) -> dict:
    t0 = time.time()
    d = R.build_period(g, allow_holdout=allow_holdout)
    days = d["days"]
    cal = R.calendar().filter(pl.col("pt_date").is_in(days))
    umap = d["unit_map"]
    labs = dict(R.roster().select("agent", "lab").iter_rows())
    rt = pl.read_parquet(R.SHARED / "rooms_timeline.parquet")
    room_of = S.rooms_lookup(rt)
    pm = R.project_map()
    res = {"goal_no": g, "days": len(days)}

    # ------------------------------------------------------------------------------------------------ work
    ws = S.attach_unit(S.work_stream(d["events"], umap), cal, umap)
    if not allow_holdout:
        ho = holdout_mask(ws["pt_date"].to_list(), [g] * ws.height)
        ws = ws.filter(~pl.Series(ho))
    repos = sorted(set(ws["repo"].to_list()))
    seen_w = S.seen_times(days, repos, pm, R.SHARED)
    read_w = S.seen_times(days, repos, pm, R.SHARED, reads_only=True)
    ev_w, lt_w, occ_w = S.long_table(ws, d["named"], room_of=room_of, lab_of=labs, seen_t=seen_w, read_t=read_w)
    res["work"] = {"events": 0 if ev_w is None else ev_w.height, "rows": 0 if lt_w is None else lt_w.height,
                   "repos": len(repos), "named": sum(bool(v) for v in d["named"].values())}

    # ------------------------------------------------------------------------------------------------ attention
    ps = (pl.scan_parquet(R.SHARED / "project_states.parquet")
          .filter((pl.col("w_min") == 30) & (pl.col("sources").cast(pl.String) == "all") & (pl.col("goal_no") == g)
                  & pl.col("pt_date").is_in(days) & (pl.col("agent") != CLAUDE_CODE))
          .select("pt_date", "win", "agent", "room", "project", "holdout").collect()
          .with_columns(pl.col("project").cast(pl.String)))
    if not allow_holdout:
        ps = ps.filter(~pl.col("holdout"))
        ps = ps.filter(~pl.Series(holdout_mask(ps["pt_date"].to_list(), [g] * ps.height)))
    ev_a = lt_a = occ_a = None
    ast = None
    named_a = {}
    if ps.height:
        ast = S.attention_stream(ps, cal, umap)
        projects = sorted(set(ast["repo"].to_list()))
        named_a = R.kickoff_named(g, projects)
        seen_a = S.seen_times(days, projects, pm, R.SHARED)
        read_a = S.seen_times(days, projects, pm, R.SHARED, reads_only=True)
        ev_a, lt_a, occ_a = S.long_table(ast, named_a, room_of=room_of, lab_of=labs, seen_t=seen_a, read_t=read_a)
        res["attention"] = {"events": 0 if ev_a is None else ev_a.height, "rows": 0 if lt_a is None else lt_a.height,
                            "projects": len(projects), "named": sum(bool(v) for v in named_a.values())}
    res["build_s"] = round(time.time() - t0, 1)
    out = {"work": (ev_w, lt_w, occ_w), "attention": (ev_a, lt_a, occ_a), "named_work": d["named"], "named_att": named_a,
           "counts": res, "skeleton": d, "streams": {"work": ws, "attention": ast}}
    if write:
        od = OUT / f"G{g:02d}"
        od.mkdir(parents=True, exist_ok=True)
        for ch, (ev, lt, occ) in (("work", out["work"]), ("attention", out["attention"])):
            if ev is None:
                continue
            _hash_opts(ev, ["chosen", "repo"]).write_parquet(od / f"events_{ch}.parquet", compression="zstd")
            _hash_opts(lt, ["opt"]).write_parquet(od / f"long_{ch}.parquet", compression="zstd")
            _hash_opts(occ, ["top_opt"]).write_parquet(od / f"occupancy_{ch}.parquet", compression="zstd")
        (od / "counts.json").write_text(json.dumps(res, indent=1))
    return out


def provenance(periods):
    p = OUT / "_provenance.json"
    prov = json.loads(p.read_text()) if p.exists() else {}
    prov.update({"built_by": "hypotheses/H93-brock-durlauf-project-choice/scheme/build.py", "git_commit": git_commit(),
                 "inputs": [{"source": "ai-village", "revision": REVISION,
                             "tables": ["work_commits", "call_windows", "context_ledger_items", "artifact_mentions", "artifacts",
                                        "project_states", "rooms_timeline", "roster", "period_units", "calendar", "chat_core",
                                        "chat_text (kickoff text, in memory only)", "village_goals (in memory only)"]}],
                 "params": {"host_labels": "replicator_hosts W=30 E=100", "attention": "project_states w_min=30 sources=all, "
                            "expiry 4 windows", "folds": 4, "named": "H54 rule via replicator_hosts.kickoff_named"},
                 "built_at": dt.datetime.now(dt.timezone.utc).isoformat()})
    prov.setdefault("periods_built", [])
    prov["periods_built"] = sorted(set(prov["periods_built"]) | set(periods))
    p.write_text(json.dumps(prov, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", type=int, action="append")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    periods = PERIODS if a.all else (a.period or [])
    OUT.mkdir(parents=True, exist_ok=True)
    for g in periods:
        r = build_period(g)
        print(json.dumps(r["counts"]), flush=True)
    provenance(periods)


if __name__ == "__main__":
    main()
