"""H77 pipeline, one goal period per call: sigma* of the top repo, the selection-resolution bound, uncopying order q,
the step-1 recruitment order (H78's estimator on the same tables), Mathis signatures M2/M3, and the neutral-null band.

  sigma*   top repo T (largest call-clock mean n); plateau; sigma* = ln[(J+ + 1/2)/(J- + 1/2)], J+ = all recruitments
           (primary), J+_ff = formation-free (variant); per-unit plateau counts and their RE pool; E150/Einf/B100/B400
  D3       fitness f = formation-free recruitments per host per 1,000 free calls while n <= 2; s = 1 - f_k/f_T; fraction
           of testable extinct rivals with s >= exp(-sigma*); fitness-permutation null (999)
  q        switch-out order
  null     the neutral synthetic world on this period's schedule (H78 analysis/synthetic.py): sigma* 95th percentile
Writes data/processed/H77-repos-as-replicators/results/G<NN>.json.
Usage: uv run python hypotheses/H77-repos-as-replicators/analysis/run.py --period 31 [--arm 2]
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
import replicator_fit as F  # noqa: E402
import replicator_hosts as R  # noqa: E402

DATA = ROOT / "data/processed/H77-repos-as-replicators"


def load(g, arm=None):
    d = DATA / f"G{g:02d}" / (f"arm_{arm}" if arm is not None else "")
    return {k: pl.read_parquet(d / f"{k}.parquet") for k in ("events", "bins", "repos", "bin_time")}


def rnd(x):
    if isinstance(x, dict):
        return {k: rnd(v) for k, v in x.items()}
    if isinstance(x, list):
        return [rnd(v) for v in x]
    if isinstance(x, float):
        return round(x, 4)
    return x


def sigma_block(bins, allb):
    sg = F.sigma_star(bins, allb)
    if sg is None:
        return None, None
    ff = F.sigma_star(bins, allb, top=sg["top"], R="R_ff")
    units = {}
    for u in sorted(bins["unit"].unique().to_list()):
        su = F.sigma_star(bins, allb, top=sg["top"], unit=u)
        if su and su["J_plus"] + su["J_minus"] > 0:
            units[u] = su
    pool = F.re_pool([v["est"] for v in units.values()], [v["se"] for v in units.values()]) if units else None
    sg["formation_free"] = {k: ff[k] for k in ("est", "se", "J_plus", "J_minus")} if ff else None
    sg["units"] = {u: {k: v[k] for k in ("est", "se", "J_plus", "J_minus", "D")} for u, v in units.items()}
    sg["unit_pool"] = pool
    return sg, sg["top"]


def neutral_band(g):
    p = DATA / "synthetic" / f"runs_G{g:02d}.parquet"
    if not p.exists():
        return None
    d = pl.read_parquet(p).filter((pl.col("world") == "neutral") & pl.col("sigma").is_not_null())
    if d.height == 0:
        return None
    s = d["sigma"].to_numpy()
    out = {"n": int(len(s)), "median": float(np.median(s)), "q95": float(np.quantile(s, 0.95))}
    if "res_frac" in d.columns:
        rf = d.filter(pl.col("res_frac").is_not_null())
        out["res_frac_median"] = float(rf["res_frac"].median()) if rf.height else None
        out["res_size"] = float((rf["res_p"] < 0.05).mean()) if rf.height else None
    return out


def analyze(g, arm=None):
    D = load(g, arm)
    ev, bins, repos, bt = D["events"], D["bins"], D["repos"], D["bin_time"]
    allb = sorted(bt["bin"].to_list())
    named = set(repos.filter(pl.col("named"))["repo"].to_list())
    res = {"period": g, "arm": arm}
    sg, top = sigma_block(bins, allb)
    res["sigma"] = sg
    if sg:
        res["top_named"] = top in named
        arr = ev.filter(pl.col("kind").is_in(["recruit", "birth"]) & (pl.col("repo") == top))
        res["top_arrivals"] = {"n": arr.height, "births": arr.filter(pl.col("kind") == "birth").height,
                               "named": int(arr.filter(pl.col("named")).height),
                               "blind": arr.filter(pl.col("cls") == "blind").height,
                               "cls": dict(arr.group_by("cls").len().iter_rows())}
        res["resolution"] = F.resolution(bins, allb, sg, R="R_ff", n_perm=999)
        ff = ev.filter((pl.col("kind") == "recruit") & (pl.col("cls") != "blind") & ~pl.col("named")).sort("t")
        res["M2_nucleus_is_top"] = (ff["repo"][0] == top) if ff.height else None
        res["M3_frustrated"] = res["resolution"].get("n_frustrated")
    res["q"] = F.depart_order(bins)
    po = F.period_order(bins, R="R_ff", exclude=named)
    res["step1_p"] = {"pooled": po["pooled"], "testable": po["testable"], "n_events": po["n_events"],
                      "e": (po["pooled"]["est"] - 1) if po["pooled"] else None}
    if arm is None:
        base = R.build_period(g)
        for lab, kw in {"E50": dict(E=50), "E150": dict(E=150), "E300": dict(E=300), "Einf": dict(E=None), "B100": dict(B=100), "B400": dict(B=400)}.items():
            d = R.build_period(g, named=base["named"], **kw)
            ab = sorted(d["bins"]["bin"].unique().to_list())
            s = F.sigma_star(d["bins"], ab)
            res[f"sigma_{lab}"] = {k: s[k] for k in ("est", "se", "J_plus", "J_minus", "testable")} if s else None
        res["neutral_null"] = neutral_band(g)
    return rnd(res)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", type=int, required=True)
    ap.add_argument("--arm", type=int, default=None)
    a = ap.parse_args()
    res = analyze(a.period, a.arm)
    out = DATA / "results"
    out.mkdir(parents=True, exist_ok=True)
    name = f"G{a.period:02d}" + (f"_arm{a.arm}" if a.arm is not None else "")
    (out / f"{name}.json").write_text(json.dumps(res, indent=1, default=str))
    s = res["sigma"]
    print(name, "sigma*", s and (s["est"], s["J_plus"], s["J_minus"], s["testable"]), "res", res.get("resolution", {}).get("frac"),
          "q", res["q"] and res["q"]["est"])


if __name__ == "__main__":
    main()
