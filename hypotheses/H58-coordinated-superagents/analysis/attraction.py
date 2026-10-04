"""H58 post-hoc diagnostic (amendment A3, written after the replication results): is a positive coordination gain g
attraction (members move onto the artifact the others are on: a group store) or avoidance (members move anywhere but
the others' artifacts: territoriality)? g's join-only M1 rewards both. For a unit: among member moves (k != own last
artifact) made while the others sit on a different R_G artifact o, the observed join rate P(k = o) vs the rate the
null unit (agent + own artifacts) expects, E[pi_j(o) / (1 - pi_j(ell))] with member-specific popularity (in-sample).
attraction = observed / expected (> 1 attraction, < 1 avoidance), with a binomial z. Writes results/attraction.json."""
from __future__ import annotations

import glob
import json
import math
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h58data as HD  # noqa: E402
import h58lib as L  # noqa: E402
from run import jsonable  # noqa: E402

RES = HD.D / "results"


def attraction(U, members):
    T = L._transitions(U, members)
    if T is None or T["nR"] == 0:
        return {"n_moves": 0}
    k, ell, o, r, j = T["k"], T["ell"], T["o"], T["r"], T["j"]
    P = np.zeros((T["n_mem"], T["K"]))
    np.add.at(P, (j, k), 1)
    pool = P.sum(0)
    pi = (P + 2 * (pool + 0.5) / (pool + 0.5).sum()) / (P.sum(1, keepdims=True) + 2)
    mv = (r == 2) & (ell >= 0) & (k != ell)
    if mv.sum() == 0:
        return {"n_moves": 0}
    exp = pi[j[mv], o[mv]] / np.maximum(1 - pi[j[mv], ell[mv]], 1e-9)
    obs = (k[mv] == o[mv]).astype(float)
    e, n = float(exp.sum()), int(mv.sum())
    var = float((exp * (1 - exp)).sum())
    return {"n_moves": n, "joins": int(obs.sum()), "expected": e, "attraction": float(obs.sum() / e) if e > 0 else None,
            "z": float((obs.sum() - e) / math.sqrt(var)) if var > 0 else None}


def main():
    out = {}
    for f in sorted(glob.glob(str(RES / "units" / "*.json"))):
        r = json.loads(Path(f).read_text())
        u = r["unit"]
        U = HD.load_unit(u)
        rows = []
        for kind, cs in r["candidates"].items():
            for c in cs:
                if c["qualifies"] or kind in ("search", "multi"):
                    a = attraction(U, c["members"])
                    rows.append({"kind": kind, "agents": c["agents"], "qualifies": c["qualifies"], "g": c["g"], **a})
        out[u] = rows
        for x in rows:
            if x["qualifies"] or x["kind"] == "search":
                print(u, x["kind"], len(x["agents"]), "q" if x["qualifies"] else "-", "moves", x.get("n_moves"),
                      "joins", x.get("joins"), "exp", None if x.get("expected") is None else round(x["expected"], 1),
                      "attr", None if x.get("attraction") is None else round(x["attraction"], 2),
                      "z", None if x.get("z") is None else round(x["z"], 1))
    (RES / "attraction.json").write_text(json.dumps(jsonable(out), indent=1))


if __name__ == "__main__":
    main()
