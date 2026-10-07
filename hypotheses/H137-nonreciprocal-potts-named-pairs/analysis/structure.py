"""H137 structural counts (card round-1 order step 1; no follow direction is computed or printed).

Per non-reserved unit: calls, agents, project hops (call), follow hops, follow-hop rows by naming class, pairs by class
(O5, from naming only), one-way pairs with >= 1 follow hop, and the structural precondition (>= 20 follow-hop rows in
one-way pairs and >= 8 one-way pairs with >= 1 follow hop). Undirected totals only: F_ab + F_ba per pair.

Writes data/processed/H137-nonreciprocal-potts-named-pairs/results/structure.parquet.
Usage: uv run python hypotheses/H137-nonreciprocal-potts-named-pairs/analysis/structure.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h137lib as L  # noqa: E402
import real_labels as RL  # noqa: E402


def main():
    t0 = time.time()
    pu = L.units_table().sort("start")
    rows = []
    for u in pu["unit_id"].to_list():
        try:
            S = L.load_skeleton(u)
        except Exception as e:  # noqa: BLE001
            print(u, "skip", e, flush=True)
            continue
        if S["n"] == 0 or S["A"] < 2:
            continue
        lab = RL.labels_for(S)
        fh = L.follow_hops(S, lab["cur"], lab["label"], lab["hop"])
        cl = L.naming_classes(S["W"])
        und = {}
        if fh.height:
            h = fh.with_columns(pl.min_horizontal("hopper", "target").alias("a"), pl.max_horizontal("hopper", "target").alias("b"))
            for a, b, n in h.group_by("a", "b").len().iter_rows():
                und[(a, b)] = n
        r = {"unit": u, "goal_no": S["goal_no"], "calls": S["n"], "agents": S["A"], "hops": int(lab["hop"].sum()),
             "follow_hops": int(fh["call"].n_unique()) if fh.height else 0, "follow_rows": fh.height,
             "named_read_calls": int((S["r_nam1"] > 0).any(axis=1).sum()), "n_projects": lab["n_projects"]}
        for c in L.CLASSES:
            prs = [k for k, v in cl.items() if v[0] == c]
            r[f"pairs_{c}"] = len(prs)
            r[f"pairs_{c}_hit"] = sum(1 for k in prs if und.get(k, 0) > 0)
            r[f"rows_{c}"] = sum(und.get(k, 0) for k in prs)
        r["testable"] = bool(r["rows_one"] >= 20 and r["pairs_one_hit"] >= 8)
        rows.append(r)
        print(f"{u} {time.time() - t0:.0f}s calls {r['calls']} hops {r['hops']} follow {r['follow_hops']} "
              f"one-way pairs {r['pairs_one']} (hit {r['pairs_one_hit']}, rows {r['rows_one']}) "
              f"mutual {r['pairs_mutual']} none {r['pairs_none']} testable {r['testable']}", flush=True)
    out = L.D / "results"
    out.mkdir(parents=True, exist_ok=True)
    pl.DataFrame(rows).write_parquet(out / "structure.parquet")
    print(f"done {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
