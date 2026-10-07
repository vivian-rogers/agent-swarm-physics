"""Section II figure: genericness-corrected similarity of each period's day-1 content centroid (rows) to every
candidate kickoff text (columns), 33 x 33, bge (H54, model 11).

    uv run python writeup/figures-js/export/s2_kickoff_matrix.py

Reuses load() and corrected() from writeup/visuals/H54-kickoff-quench-target/make.py unchanged (it asserts that the
ranks equal the card table). Inputs are the non-reserved NE34 periods only (the H54 scheme excludes reserved periods);
we check that again with holdout_mask on the period list.
Inputs: data/processed/H54-kickoff-quench-target/NE34/{S_kick.npy, periods.parquet, results.json}, G51/native.json.
"""
from __future__ import annotations

import importlib.util

import numpy as np

from common import ROOT, write


def load_h54():
    f = ROOT / "writeup/visuals/H54-kickoff-quench-target/make.py"
    spec = importlib.util.spec_from_file_location("h54_make", f)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def load_shared_common():
    spec = importlib.util.spec_from_file_location("shared_common", ROOT / "infra/shared/common.py")
    sc = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(sc)
    return sc


def main():
    h54 = load_h54()
    d = h54.load()
    sc = load_shared_common()
    Sh, goals, n = d["Sh"], d["goals"], d["n"]
    held = set(sc.load_holdout()["goal_periods_held_out"])
    assert not held & set(goals), f"reserved periods in the matrix: {held & set(goals)}"
    assert n == 33 and Sh.shape == (33, 33)
    v = float(np.nanpercentile(np.abs(Sh), 98))
    print("n", n, "top1", d["top1"], "vmax(98%)", round(v, 4), "range", round(float(Sh.min()), 3), round(float(Sh.max()), 3))
    write("s2_kickoff_matrix", dict(goals=goals, S=Sh, rank=d["rank"], top1=d["top1"], n=n, vmax98=v),
          "writeup/figures-js/export/s2_kickoff_matrix.py",
          ["data/processed/H54-kickoff-quench-target/NE34/S_kick.npy", "NE34/periods.parquet", "NE34/results.json"],
          dict(embedding="bge", correction="S_pq - mean_{p'!=q} S_p'q"))


if __name__ == "__main__":
    main()
