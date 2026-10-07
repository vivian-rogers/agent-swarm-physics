"""H141 native N3 (NE38): Claude Opus 5 (agent 40) is reassigned from the game-dev role to mathematics at
2026-07-29 16:51 UTC. Day-scale persistence (O3 form) of its content along the new goal axis and along the old goal axis,
before (07-24 -> 07-29 16:51) and after (07-29 16:51 -> 08-12). Wells are arm-specific and leave the day pair out.
One agent, few days: descriptive.

    uv run python hypotheses/H141-easy-plane-anisotropy/analysis/natives.py
Output: data/processed/H141-easy-plane-anisotropy/results/ne38.json
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h141lib as L  # noqa: E402

AGENT = 40
LAST_AFTER = "2026-08-12"


def arm(D: L.Data, plane: str, last_day: str) -> L.Data:
    m = ((D.st["agent"] == AGENT) & (D.st["plane"] == plane) & (D.st["pt_date"] <= last_day)).to_numpy()
    st = D.st.filter(pl.Series(m)).drop("i").with_row_index("i")
    return L.Data(goal=51, st=st, Z=D.Z[m], X=D.X[m], ok=D.ok[m], planes=D.planes, texts=D.texts, model=D.model)


def persistence(Da: L.Data, axes: dict) -> dict:
    days = sorted(Da.st["pt_date"].unique().to_list())
    DA = L.day_accumulate(Da, days, min_stmt=4)
    out = {"days": days, "n_pairs": float(DA.npairs.sum()), "n_statements": Da.st.height}
    if DA.npairs.sum() < 1:
        return out
    for name, u in axes.items():
        P = np.outer(u, u)[None]
        out[f"P_{name}"] = float(L.day_persistence(DA, P)[0])
    return out


def main():
    res = {}
    for model, variant in L.VARIANTS:
        D = L.load(51, model, variant)
        axes = {"new": D.texts["a40"], "old": D.texts["a40old"]}
        before = arm(D, "a40old", "2026-07-29")
        after = arm(D, "a40", LAST_AFTER)
        r = {"before": persistence(before, axes), "after": persistence(after, axes)}
        b, a = r["before"], r["after"]
        if all(k in b for k in ("P_new", "P_old")) and all(k in a for k in ("P_new", "P_old")):
            r["consistent"] = bool(a["P_new"] > a["P_old"] and b["P_old"] > b["P_new"])
            r["after_order"] = bool(a["P_new"] > a["P_old"])
            r["before_order"] = bool(b["P_old"] > b["P_new"])
        res[f"{model}|{variant}"] = r
        print(model, variant, json.dumps(r), flush=True)
    (L.DATA / "results").mkdir(parents=True, exist_ok=True)
    (L.DATA / "results" / "ne38.json").write_text(json.dumps(res, indent=1))


if __name__ == "__main__":
    main()
