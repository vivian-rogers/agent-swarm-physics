"""H58 round-2 real-data run for R1 (attraction rule, territorial rule, village level, static partition) and R2
(file-level allocation inside shared repos). Card: "Round 2 design" and amendments R2-A1.. (written before this run).

R1: per unit (38a-c, 51a-e replication; 39, 40, 41, 44 native) the observed and 100 rotation draws of the pair matrices;
    every round-1 candidate set (results/units/<u>.json) through the A-rule and the T-rule; village Lambda_V, T_V;
    static partition. Any qualifier is re-run at 15- and 60-min bins.
R2: per eligible (unit, shared repo) the file-level panel (scheme r2/files_shared.parquet): Lambda_file, T_file
    against rotations, exclusivity E against the random partition; pooled Stouffer; issue-reference coverage.
Outputs: data/processed/H58-coordinated-superagents/r2/r1_results.json, r2_results.json
Run: uv run python hypotheses/H58-coordinated-superagents/analysis/r2_run.py [--r1] [--r2]
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ.setdefault(_v, "2")

import json  # noqa: E402
import re  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r2lib58 as R  # noqa: E402

KINDS = ("multi", "w_sync", "w_coad", "w_reply", "w_coart", "crew", "search", "room", "lab")


def file_panels():
    """Eligible shared repos at file level: key 'unit|repo_id' -> Panel (artifacts = files)."""
    meta = {x["unit"]: x for x in R.units_meta()}
    fs = pl.read_parquet(R.R2 / "files_shared.parquet")
    # one row per (commit, file): the panel takes the dominant file per writer-bin
    out = {}
    for (u, rid), g in fs.partition_by(["unit", "repo_id"], as_dict=True).items():
        R.assert_no_reserved([meta[u]])
        P = R.panel_from_commits(f"{u}|{rid}", g, meta[u], 30, art_col="file_id")
        out[f"{u}|{rid}"] = P
    return out


def candidates(u, P):
    r = json.loads((R.D / "results" / "units" / f"{u}.json").read_text())
    pos = {a: i for i, a in enumerate(P.agents)}
    out = []
    for kind in KINDS:
        for c in r["candidates"].get(kind, []):
            mem = sorted(pos[a] for a in c["agents"] if a in pos)
            if len(mem) >= 2:
                out.append({"kind": kind, "agents": c["agents"], "members": mem,
                            "r1_qualifies": bool(c.get("qualifies_search") if kind == "search" else c.get("qualifies"))})
    return out


def run_r1():
    res = {}
    t0 = time.time()
    for u in R.REPL + R.NATIVE:
        P = R.load_panel(u)
        Dr = R.make_draws(P, R=100, seed=sum(map(ord, u)))
        v = R.village(Dr)
        sp = R.static_partition(P, n_draw=200, seed=1)
        cands = []
        for i, c in enumerate(candidates(u, P)):
            a = R.a_rule(Dr, c["members"], seed=100 + i)
            t = R.t_rule(Dr, c["members"], seed=100 + i)
            cands.append({**c, "A": a, "T": t})
        # bin-width variants for any qualifier
        for c in cands:
            if c["A"]["qualifies"] or c["T"]["qualifies"]:
                c["variants"] = {}
                for bm in (15, 60):
                    Pv = R.load_panel(u, bin_min=bm)
                    pos = {a: k for k, a in enumerate(Pv.agents)}
                    mem = sorted(pos[a] for a in c["agents"] if a in pos)
                    Dv = R.make_draws(Pv, R=100, seed=bm)
                    c["variants"][bm] = {"A": R.a_rule(Dv, mem, seed=bm), "T": R.t_rule(Dv, mem, seed=bm)}
        res[u] = {"nA": P.nA, "nB": P.nB, "village": v, "static": sp, "candidates": cands}
        nq_a = sum(c["A"]["qualifies"] for c in cands)
        nq_t = sum(c["T"]["qualifies"] for c in cands)
        print(f"{u}: {len(cands)} candidates; A-rule {nq_a}, T-rule {nq_t}; {time.time() - t0:.0f}s", flush=True)
    (R.R2 / "r1_results.json").write_text(json.dumps(R.jsonable(res), indent=1))


ISSUE_RX = re.compile(r"(?<![\w/])#\d+\b|\b(?:issue|closes|fixes|resolves)\s+#?\d+", re.I)


def issue_coverage(repo, hashes):
    env = dict(os.environ, GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_NOSYSTEM="1", GIT_TERMINAL_PROMPT="0")
    txt = subprocess.run(["git", "-C", str(R.ROOT / "data/raw/repos" / f"{repo}.git"), "log", "--all", "--format=%H %s"],
                         capture_output=True, text=True, env=env, errors="replace").stdout
    hs = set(hashes)
    n = k = 0
    for line in txt.splitlines():
        h, _, s = line.partition(" ")
        if h in hs:
            n += 1
            k += bool(ISSUE_RX.search(s))
    return k / n if n else None


def run_r2():
    panels = file_panels()
    repos = dict(pl.read_parquet(R.D / "repos.parquet").select("repo_id", "repo").iter_rows())
    fs = pl.read_parquet(R.R2 / "files_shared.parquet")
    res = {}
    for key, P in sorted(panels.items()):
        u, rid = key.split("|")
        Dr = R.make_draws(P, R=100, seed=int(rid))
        v = R.village(Dr)
        sp = R.static_partition(P, n_draw=200, seed=2, min_act=3)
        hashes = fs.filter((pl.col("unit") == u) & (pl.col("repo_id") == int(rid)))["hash"].unique().to_list()
        res[key] = {"unit": u, "repo_id": int(rid), "repo": repos[int(rid)].split("/")[-1], "n_writers": P.nA,
                    "n_files": P.K, "n_bins_working": int((P.S >= 0).sum()), "village": v, "static": sp,
                    "issue_share": issue_coverage(repos[int(rid)], hashes)}
        print(key, res[key]["repo"], P.nA, P.K, flush=True)
    (R.R2 / "r2_results.json").write_text(json.dumps(R.jsonable(res), indent=1))


def main():
    if "--r1" in sys.argv:
        run_r1()
    if "--r2" in sys.argv:
        run_r2()


if __name__ == "__main__":
    main()
