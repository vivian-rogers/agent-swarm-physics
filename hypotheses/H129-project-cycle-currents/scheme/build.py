"""H129 scheme: project hops, visits and age ranks per goal period and channel.

Work channel: the shared host replay (infra/shared/replicator_hosts.py, W 30, E 100, non-holdout days); a hop is a
change between consecutive distinct host labels of one agent within a unit (direct departure or expiry then a later
arrival; `direct` flags the first). Attention channel: shared project_states (w_min 30, sources all, raw project,
non-holdout rows); a hop is a change between consecutive labelled windows. Age rank: first non-holdout appearance of
the repo (agent work commit) or project (labelled window) over all periods; older = smaller.
Units: #51 by period_units (51a-51l); every other period whole.

Writes data/processed/H129-project-cycle-currents/G<NN>/{hops,visits}_<channel>.parquet (names hashed; age ranks kept)
and _provenance.json. No message text is read.

Usage: uv run python hypotheses/H129-project-cycle-currents/scheme/build.py
"""
from __future__ import annotations

import datetime as dt
import json
import sys
import time
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "analysis"))
import h129lib as L  # noqa: E402
from common import REVISION, git_commit  # noqa: E402

RH = L.RH


def main():
    t0 = time.time()
    counts = {}
    for g in L.GOALS:
        o = L.D / f"G{g:02d}"
        o.mkdir(parents=True, exist_ok=True)
        for ch in ("work", "attention"):
            d = L.work_hops(g) if ch == "work" else L.attention_hops(g)
            age = L.work_age() if ch == "work" else L.attention_age()
            h, v = d["hops"], d["visits"]
            names = set(h["src"].to_list()) | set(h["dst"].to_list()) | set(v["repo"].to_list())
            rank = L.rank_of(age, names)
            h = h.with_columns(pl.col("src").replace_strict(rank, return_dtype=pl.Int32).alias("src_rank"),
                               pl.col("dst").replace_strict(rank, return_dtype=pl.Int32).alias("dst_rank"))
            RH.hashed(h, cols=("src", "dst")).write_parquet(o / f"hops_{ch}.parquet")
            RH.hashed(v, cols=("repo",)).write_parquet(o / f"visits_{ch}.parquet")
            counts[f"G{g:02d}/{ch}"] = {"hops": h.height, "visits": v.height, "projects": len(names),
                                        "units": sorted(set(h["unit"].to_list()))}
        print(f"G{g:02d} {time.time() - t0:.0f}s", flush=True)
    prov = {"built_by": "hypotheses/H129-project-cycle-currents/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["work_commits", "call_windows", "calendar", "period_units", "roster", "project_states"]}],
            "params": {"host_labels": "replicator_hosts W=30 E=100 (no arrival tags)",
                       "attention": "project_states w_min=30 sources=all raw project, non-holdout",
                       "age": "first non-holdout appearance over all periods", "units": "#51 by period_units; else whole period"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat(), "counts": counts}
    (L.D / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print(f"built in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
