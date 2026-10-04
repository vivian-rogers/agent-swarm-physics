"""H132 real-data run on G12 (registered statistics, both models, masked and unmasked inputs).

    uv run python hypotheses/H132-debate-limit-cycle/analysis/run.py [--perm 5000]
Output: data/processed/H132-debate-limit-cycle/results/results.json
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h132lib as L  # noqa: E402

RES = L.DATA.parent / "results"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--perm", type=int, default=5000)
    a = ap.parse_args()
    RES.mkdir(parents=True, exist_ok=True)
    out = {}
    for model in ("bge_small", "gte_modernbert"):
        for src in ("masked", "unmasked"):
            M = L.load(model, src)
            key = f"{model}|{src}"
            T = L.turns(M, ("deb",))
            r = {"deb": L.shuffle_test(T, a.perm, seed=11),
                 "deb_detrend": L.shuffle_test(T, a.perm, seed=12, detrend=True, keys=("rho1", "rho2", "Lam")),
                 "per_debate": L.per_debate(T),
                 "n_turns": int(len(T.ya))}
            Tp = L.turns(M, ("post",))
            r["post"] = L.shuffle_test(Tp, a.perm, seed=13, keys=("rho1", "rho2", "Lam", "A"))
            r["msg"] = L.message_level(M, "deb", n_perm=a.perm, seed=14)
            out[key] = r
            d = r["deb"]
            print(key, "turns", r["n_turns"], {k: (round(d[k]["obs"], 3), round(d[k].get("p_hi", np.nan), 4),
                                                   round(d[k].get("p_lo", np.nan), 4)) for k in ("rho1", "rho2", "Lam", "A", "L", "rho1_vec", "dRho_vis") if k in d},
                  "post Lam", round(r["post"]["Lam"]["obs"], 3), round(r["post"]["Lam"]["p_hi"], 3),
                  "msg", {k: (round(r["msg"][k]["obs"], 3), round(r["msg"][k]["p_lo"], 3)) for k in ("rho_same", "rho_cross", "N3_contrast")},
                  flush=True)
            (RES / "results.json").write_text(json.dumps(out, indent=1, default=float))


if __name__ == "__main__":
    main()
