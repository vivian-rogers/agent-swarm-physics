"""H78 pipeline, one goal period per call: growth order p of repo recruitment on the swarm call clock.

  primary  formation-free recruitments (no blind window, no kickoff-named repo), named repos excluded, per unit then
           random-effects pooled (exception (d)); C_free offset; quasi-Poisson SE
  v1 all recruitments, all repos   v2 read-only (known + read)   v3 repo fixed effects   v4 conditional logit
  v5 cumulative contributors       v6 wall-clock 30-min bins     v7 cross-lab order      E150 / Einf / B100 / B400
  named stratum (all recruitments into named repos), formation share, A0 Mathis step test
Reads data/processed/H78-replicator-growth-order/G<NN>/ (built by scheme/build.py); rebuilds variants in memory with the
shared builder. Writes results/G<NN>.json. Holdout days are never loaded (period_days masks them).
Usage: uv run python hypotheses/H78-replicator-growth-order/analysis/run.py --period 31 [--arm 2]
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
import replicator_fit as F  # noqa: E402
import replicator_hosts as R  # noqa: E402

DATA = ROOT / "data/processed/H78-replicator-growth-order"


def load(g: int, arm: int | None = None) -> dict:
    d = DATA / f"G{g:02d}" / (f"arm_{arm}" if arm is not None else "")
    return {k: pl.read_parquet(d / f"{k}.parquet") for k in ("events", "bins", "labs", "choice", "repos", "bin_time")}


def pr(r):
    if r is None:
        return None
    return {k: (round(v, 4) if isinstance(v, float) else v) for k, v in r.items() if k != "units"} | (
        {"units": {u: {kk: round(vv, 4) if isinstance(vv, float) else vv for kk, vv in x.items()} for u, x in r["units"].items()}}
        if "units" in r else {})


def order_block(bins, labs, choice, named, R_col="R_ff", excl=True):
    ex = named if excl else None
    out = {"primary": pr(F.period_order(bins, R=R_col, exclude=ex))}
    return out


def analyze(g: int, arm: int | None = None) -> dict:
    D = load(g, arm)
    ev, bins, labs, choice, repos, bt = D["events"], D["bins"], D["labs"], D["choice"], D["repos"], D["bin_time"]
    named = set(repos.filter(pl.col("named"))["repo"].to_list())
    res = {"period": g, "arm": arm, "n_repos": repos.height, "n_named": len(named)}
    k = dict(ev.group_by("kind").len().iter_rows())
    arr = ev.filter(pl.col("kind").is_in(["recruit", "birth"]))
    res["counts"] = {**k, "cls": dict(arr.filter(pl.col("kind") == "recruit").group_by("cls").len().iter_rows()),
                     "named_recruits": int(arr.filter((pl.col("kind") == "recruit") & pl.col("named")).height)}
    form = k.get("birth", 0) + arr.filter((pl.col("kind") == "recruit") & (pl.col("named") | (pl.col("cls") == "blind"))).height
    res["formation_share"] = form / max(arr.height, 1)
    res["primary"] = pr(F.period_order(bins, R="R_ff", exclude=named))
    res["v1_all"] = pr(F.period_order(bins, R="R_all"))
    b2 = bins.with_columns((pl.col("R_known") + pl.col("R_read") - 0).alias("R_ro"))
    # read-only among formation-free: known/read recruits into non-named repos (named excluded by row filter)
    res["v2_readonly"] = pr(F.period_order(b2, R="R_ro", exclude=named))
    res["v3_fe"] = pr(F.poisson_order(bins.filter(~pl.col("repo").is_in(list(named))), R="R_ff", fe=True))
    res["v4_clogit"] = pr(F.clogit_order(choice))
    res["v5_contrib"] = pr(F.period_order(bins, R="new_contrib", n="n_cum", exclude=named))
    res["v9_touch"] = pr(F.period_order(bins, R="R_ff2", exclude=named))
    res["counts"]["cls_touch"] = dict(arr.filter(pl.col("kind") == "recruit").group_by("cls_touch").len().iter_rows())
    top_ = F.top_repo(bins, 0)
    rr = ev.filter((pl.col("kind") == "recruit") & (pl.col("cls") != "blind") & ~pl.col("named"))
    res["top_share_of_ff_recruits"] = (rr.filter(pl.col("repo") == top_).height / rr.height) if rr.height else None
    res["v8_first_time"] = pr(F.period_order(bins, R="new_contrib", exclude=named))
    res["v7_crosslab"] = pr(F.lab_order(labs.filter(~pl.col("repo").is_in(list(named)))))
    res["named_stratum"] = pr(F.poisson_order(bins.filter(pl.col("repo").is_in(list(named))), R="R_all")) if named else None
    # rebuilt variants (unhashed in memory, then hashed names are irrelevant: fits do not use names except exclusion)
    if arm is None:
        base = R.build_period(g)
        nm = {r for r, v in base["named"].items() if v}
        for lab, kw in {"E50": dict(E=50), "E150": dict(E=150), "E300": dict(E=300), "Einf": dict(E=None), "B100": dict(B=100), "B400": dict(B=400),
                        "v6_wall": dict(wall_min=30)}.items():
            d = R.build_period(g, named=base["named"], **kw)
            res[lab] = pr(F.period_order(d["bins"], R="R_ff", exclude=nm))
    # A0 Mathis step
    th = dict(zip(bt["bin"].to_list(), bt["t_act_h"].to_list()))
    res["A0"] = F.mathis_step(bins, named, th)
    # nucleus vs winner (shared with H77)
    top = F.top_repo(bins, 0)
    ff = ev.filter((pl.col("kind") == "recruit") & (pl.col("cls") != "blind") & ~pl.col("named")).sort("t")
    res["nucleus_is_top"] = (ff["repo"][0] == top) if ff.height else None
    return res


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
    p = res["primary"]
    print(name, "p_pooled", p["pooled"], "whole", p["whole"] and round(p["whole"]["est"], 3), "events", p["n_events"],
          "testable", p["testable"])


if __name__ == "__main__":
    main()
