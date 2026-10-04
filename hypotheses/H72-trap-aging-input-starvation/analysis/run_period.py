"""H72 replication: the two-clock hazard on one goal period (or all eligible periods).

Usage: uv run python hypotheses/H72-trap-aging-input-starvation/analysis/run_period.py --period G51
       uv run python hypotheses/H72-trap-aging-input-starvation/analysis/run_period.py --all
Writes data/processed/H72-trap-aging-input-starvation/G<NN>/results.json.
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h72lib as L  # noqa: E402


def one(df: pl.DataFrame, per: int) -> dict:
    t0 = time.time()
    res = {"period": f"G{per:02d}", "regime": df["regime"][0], "days": df["pt_date"].n_unique(),
           "agents": df["agent"].n_unique(), "gates": df.height}
    # primary: sustained escape, s_novel
    P = L.prep(df, "sus", "novel")
    n_esc = int(P["y"].sum())
    res["primary"] = prim = {"n": P["n"], "n_escape": n_esc, "escape_rate": n_esc / max(P["n"], 1),
                             "median_a_min": float(np.median(np.exp(P["la"]))),
                             "median_s_min": float(np.median(np.exp(P["ls"])))}
    if n_esc < L.MIN_EVENTS or P["n"] - n_esc < L.MIN_EVENTS:
        prim["verdict"] = "descriptive (underpowered)"
        return res
    pt = L.point(P)
    bt = L.bootstrap(P, L.B_PRIMARY, seed=per)
    prim.update({k: v for k, v in pt.items()})
    prim.update({k: bt[k] for k in ("ci_a0", "ci_a", "ci_s", "ci_rho", "n_draws")})
    k_ = L.kappa(P)
    prim["kappa"] = k_
    prim["b_impl"] = pt["beta_s"] * k_
    D = np.array(bt["draws"])
    rng = np.random.default_rng(per)
    # bootstrap of b_impl needs kappa per draw: recompute on the same day draws
    rpd = L.HF.rows_per_day(P["day"])
    kd = []
    for i in range(min(100, len(D))):
        idx = L.HF.block_resample(P["day"], rng, rpd)
        kd.append(L.kappa(P, idx))
    bi = D[: len(kd), 2] * np.array(kd)
    prim["ci_b_impl"] = [float(np.percentile(bi, 2.5)), float(np.percentile(bi, 97.5))]
    pdays = L.cv_ll(P)
    prim["cv"] = L.cv_summary(pdays, seed=per)
    prim["cv_per_1000"] = {k: v / P["n"] * 1000 for k, v in prim["cv"].items() if not k.endswith("_ci")}
    prim["verdict"] = L.verdict(prim, n_esc, P["n"] - n_esc)
    # variants of s
    res["variants"] = {}
    for v in ("content", "dir", "peer"):
        Pv = L.prep(df, "sus", v)
        ptv = L.point(Pv)
        btv = L.bootstrap(Pv, L.B_VARIANT, seed=per + 1000)
        r = {k: ptv[k] for k in ("beta_a0", "beta_a", "beta_s", "rho", "se_a", "se_s")}
        r.update({k: btv[k] for k in ("ci_a0", "ci_a", "ci_s", "ci_rho")})
        r["kappa"] = L.kappa(Pv)
        r["b_impl"] = ptv["beta_s"] * r["kappa"]
        r["verdict"] = L.verdict(r, int(Pv["y"].sum()), Pv["n"] - int(Pv["y"].sum()))
        res["variants"][v] = r
    # secondary outcome: any escape with a_any
    Pa = L.prep(df, "any", "novel")
    na = int(Pa["y"].sum())
    if na >= L.MIN_EVENTS and Pa["n"] - na >= L.MIN_EVENTS:
        pta = L.point(Pa)
        bta = L.bootstrap(Pa, L.B_VARIANT, seed=per + 2000)
        r = {k: pta[k] for k in ("beta_a0", "beta_a", "beta_s", "rho", "se_a", "se_s")}
        r.update({k: bta[k] for k in ("ci_a0", "ci_a", "ci_s", "ci_rho")})
        r.update({"n": Pa["n"], "n_escape": na, "verdict": L.verdict(r, na, Pa["n"] - na)})
        res["any"] = r
    # in-flight placebo (Wald)
    ptp = L.point(P, extra={"inflight": P["inflight"]})
    res["placebo"] = {"beta_inflight": ptp["beta_inflight"], "se_inflight": ptp["se_inflight"],
                      "ci_inflight": [ptp["beta_inflight"] - 1.96 * ptp["se_inflight"],
                                      ptp["beta_inflight"] + 1.96 * ptp["se_inflight"]],
                      "beta_s_with": ptp["beta_s"], "beta_a_with": ptp["beta_a"],
                      "share_with_inflight": float(np.mean(P["inflight"] > 0))}
    # robustness (point + Wald)
    rob = {}
    ptc = L.point(P, link="cloglog")
    rob["cloglog"] = {k: ptc[k] for k in ("beta_a0", "beta_a", "beta_s", "se_a", "se_s")}

    def sub(mask):
        Q = {k: (v[mask] if isinstance(v, np.ndarray) and len(v) == P["n"] else v) for k, v in P.items()}
        Q["nuis"] = {k: v[mask] for k, v in P["nuis"].items()}
        Q["nuis"] = {k: v for k, v in Q["nuis"].items() if np.std(v) > 0}
        Q["n"] = int(mask.sum())
        return Q
    for nm, mask in (("trim_h025", P["h_day"] >= 0.25), ("no_first_day", ~P["first_day"])):
        if mask.sum() > 100 and P["y"][mask].sum() >= L.MIN_EVENTS:
            q = L.point(sub(mask))
            rob[nm] = {k: q[k] for k in ("beta_a0", "beta_a", "beta_s", "se_a", "se_s")}
    res["robust"] = rob
    res["runtime_s"] = round(time.time() - t0, 1)
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    g = pl.read_parquet(L.OUT / "gates.parquet")
    pers = sorted(g["goal_no"].unique().to_list()) if a.all else [int(a.period.lstrip("G"))]
    for per in pers:
        df = g.filter(pl.col("goal_no") == per)
        r = one(df, per)
        od = L.OUT / f"G{per:02d}"
        od.mkdir(parents=True, exist_ok=True)
        (od / "results.json").write_text(json.dumps(r, indent=1, default=float))
        p = r["primary"]
        print(r["period"], r["regime"], p["n"], p.get("verdict"), {k: round(p[k], 3) for k in
              ("beta_a0", "beta_a", "beta_s", "rho", "b_impl") if k in p}, r.get("runtime_s"), flush=True)


if __name__ == "__main__":
    main()
