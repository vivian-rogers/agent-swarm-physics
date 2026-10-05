"""H13 round 2, R2-A real run: graded style ladder on every round-1b unit, bge and gte (card: Round 2, R2-A).

Usage: uv run python hypotheses/H13-family-fields/analysis/r2_ladder.py
Writes data/processed/H13-family-fields/r2/ladder.json
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import r2lib as R  # noqa: E402
import build as B  # noqa: E402
import h13lib as L  # noqa: E402
from common import holdout_mask  # noqa: E402

NPERM = 2000


def main():
    t0 = time.time()
    rng = np.random.default_rng(20261005)
    lab_of, _ = R.roster_labs()
    out = {"units": {}, "summary": {}}
    for model in ("bge", "gte"):
        pu = {}
        for u in R.COUNTED + R.DESCRIPTIVE:
            t = R.load_stmts(u)
            days = sorted(t["pt_date"].unique().to_list())
            assert not any(holdout_mask(days, [B.UNITS[u][1]] * len(days)))
            U = R.vectors(t, model)
            blk, inv, cnt = R.blocks(t)
            sk = R.UnitSkel(t, lab_of)
            res = R.ladder_unit(U, blk, inv, cnt, sk, nperm=NPERM, rng=rng, jack=True, lfo=("L0", "W3"))
            if model == "bge":
                for name, X in (("Gmix", blk["G"]), ("FWmix", blk["FW50g"]), ("S20mix", blk["S20g"])):
                    Hx = R.agent_mean_vectors(X, t, sk.ags)
                    ft = sk.T(Hx, nperm=NPERM, rng=rng, jack=True)
                    res[name] = {"T": ft["obs"], "p": ft["p"], "se": ft.get("se_jack", np.nan)}
            res["N"] = int(len(sk.ags)); res["K"] = sk.K
            pu[u] = res
            print(model, u, {k: round(v["T"], 3) for k, v in res.items() if isinstance(v, dict)}, f"{time.time() - t0:.0f}s",
                  flush=True)
        out["units"][model] = pu
        S = {}
        levels = list(R.LEVELS) + ["L0_lfo", "W3_lfo"] + (["Gmix", "FWmix", "S20mix"] if model == "bge" else [])
        for lv in levels:
            m = R.re_summary(pu, R.COUNTED, lv)
            m["n_sig"] = int(sum(pu[u][lv]["p"] < 0.05 for u in R.COUNTED))
            m["median_T"] = float(np.median([pu[u][lv]["T"] for u in R.COUNTED]))
            m["median_r2_map"] = float(np.median([pu[u][lv].get("r2_map", np.nan) for u in R.COUNTED]))
            S[lv] = m
        for lv in R.LEVELS:
            S[lv]["retention"] = S[lv]["mu"] / S["L0"]["mu"]
        # A-A3 calibrated location on the synthetic curves (descriptive)
        syn = json.loads((R.R2 / "synthetic_A.json").read_text())["worlds"]
        curve = [("S0", 0.0)] + [(f"S1_c{c}", c) for c in (0.1, 0.15, 0.2, 0.3)]
        cal = {}
        for lv in ("W3", "S-a", "P3", "L0"):
            xs = np.array([c for _, c in curve]); ys = np.array([syn[k][lv]["re_mu_mean"] for k, _ in curve])
            v = S[lv]["mu"]
            cal[lv] = float(np.interp(v, ys, xs, left=np.nan, right=np.nan)) if np.all(np.diff(ys) > 0) else None
            cal[lv + "_curve"] = ys.tolist()
        S["calibrated_c"] = cal
        out["summary"][model] = S
        print(model, {lv: (round(S[lv]["mu"], 3), round(S[lv]["lo"], 3), round(S[lv]["hi"], 3), S[lv]["n_sig"])
                      for lv in levels}, cal, flush=True)
    out["seconds"] = round(time.time() - t0)
    R.dump(out, R.R2 / "ladder.json")


if __name__ == "__main__":
    main()
