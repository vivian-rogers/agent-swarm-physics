"""H59 replication pipeline, one goal period: baseline, triples (day bootstrap), leave-one-class-out skill, kernel,
pre-read term, inbox-decay check, read-out delays, templated verdict.

Usage: uv run python analysis/run_period.py --goal 51 [--nboot 100]
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
import h59lib as L  # noqa: E402


def readout_delays(goal):
    r = pl.read_parquet(L.OUT / "readout.parquet").filter(pl.col("goal_no") == goal)
    out = {}
    for c in L.CLASSES:
        a = r.filter(pl.col("cls") == c)["age_s"].to_numpy()
        if len(a):
            out[c] = {"n_items": int(len(a)), "median_s": float(np.median(a)), "q25_s": float(np.quantile(a, .25)),
                      "q75_s": float(np.quantile(a, .75)), "q90_s": float(np.quantile(a, .9))}
    return out


def amp_groups(kd, B, c, groups, lag=0):
    """MLE scale s_g of class c's lag-`lag` contribution for each row group (list of boolean masks over kd rows);
    everything else fixed. Returns scales and profile-ish SEs (numerical Hessian)."""
    from scipy.optimize import minimize
    base = L.contrib(kd, B)
    cc = np.zeros((kd.m, 3))
    for i in range(3):
        r = kd.by[i]
        cc[r] = kd.D[r, c, lag][:, None] * B[c, lag, i][None, :]
    G = len(groups)

    def nll(s):
        extra = base.copy()
        for g, m in enumerate(groups):
            extra += (s[g] - 1) * cc * m[:, None]
        return kd.nll_grad(np.zeros_like(B), np.ones(kd.m), extra)[0]
    r = minimize(nll, np.ones(G), method="L-BFGS-B")
    s = r.x
    H = np.zeros((G, G))
    e = 1e-3
    for a in range(G):
        for b in range(G):
            ea, eb = np.eye(G)[a] * e, np.eye(G)[b] * e
            H[a, b] = (nll(s + ea + eb) - nll(s + ea - eb) - nll(s - ea + eb) + nll(s - ea - eb)) / (4 * e * e)
    try:
        cov = np.linalg.inv(H)
    except np.linalg.LinAlgError:
        cov = np.full((G, G), np.nan)
    return s, cov


def implied(tri, cls):
    """H39-style translation at the receiving call: idle-escape log-odds (I->W, I->T) and talk pull from W."""
    th = np.radians(tri["theta_deg"]["est"])
    u, _ = L.u_vec(th)
    out = {}
    for c in cls:
        k, h = tri[L.CLASSES[c]]["kappa"]["est"], tri[L.CLASSES[c]]["h"]["est"]
        out[L.CLASSES[c]] = {"I_to_W": k + h * (u[1] - u[0]) / 2, "I_to_T": k + h * (u[2] - u[0]) / 2,
                             "W_to_T": k + h * (u[2] - u[1]) / 2, "W_to_I": k + h * (u[0] - u[1]) / 2,
                             "T_to_I": k + h * (u[0] - u[2]) / 2, "T_to_W": k + h * (u[1] - u[2]) / 2}
    return out


def verdict(lo):
    """Templated (card P1/P6)."""
    cells = []
    for c, x in lo.items():
        T = x["T"]
        free_ci = x["ci"]["free"]
        lev_ci = x["ci"]["lever"]
        fl_ci = x["ci"]["free-lever"]
        if free_ci[0] <= 0:
            cells.append("uninformative")
        elif T is not None and T >= 0.8 and lev_ci[0] > 0:
            cells.append("pass")
        elif (T is None or T < 0.5) and fl_ci[0] > 0:
            cells.append("fail")
        else:
            cells.append("mixed")
    if all(v == "uninformative" for v in cells):
        return "descriptive", cells
    inf = [v for v in cells if v != "uninformative"]
    if any(v == "fail" for v in inf):
        return "failed", cells
    if all(v == "pass" for v in inf):
        return "supported", cells
    return "mixed", cells


def run(goal, nboot=100, nboot_loco=200, days=None, tag=None):
    t0 = time.time()
    d = L.arrays(L.load(goal, days))
    cls = L.powered(d)
    b = L.baseline(d)
    kd = L.KD(d, b["off"])
    tri, v, lv = L.triples(kd, cls, nboot=nboot)
    lo = L.loco(d, kd, cls, nboot=nboot_loco)
    stale = {}
    for c in cls:
        a = d["age0"][kd.idx, c]
        rec = kd.D[:, c, 0] > 0
        if rec.sum() < 2 * L.MIN_REC:
            continue
        med = np.nanmedian(a[rec])
        s, cov = amp_groups(kd, lv.B(v), c, [rec & (a <= med), rec & (a > med)])
        ratio = s[1] / s[0] if s[0] != 0 else np.nan
        # delta-method SE of the ratio
        gvec = np.array([-s[1] / s[0] ** 2, 1 / s[0]])
        se = float(np.sqrt(max(gvec @ cov @ gvec, 0))) if np.all(np.isfinite(cov)) else np.nan
        stale[L.CLASSES[c]] = {"median_age_s": float(med), "fresh": float(s[0]), "stale": float(s[1]),
                               "ratio": float(ratio), "ratio_ci": [float(ratio - 1.96 * se), float(ratio + 1.96 * se)]}
    pre = {L.CLASSES[c]: {f"{L.STATES[i]}->{L.STATES[j]}": float(b["Bfull"][c, 0, i, j]) for i in range(3)
                          for j in L.OTHER[i]} for c in cls}
    free_kernel = {L.CLASSES[c]: {L.LAG_LABELS[l]: {f"{L.STATES[i]}->{L.STATES[j]}": float(b["Bfull"][c, l + 1, i, j])
                                                    for i in range(3) for j in L.OTHER[i]} for l in range(L.NL)}
                   for c in cls}
    vd, cells = verdict(lo)
    res = {"goal": goal, "tag": tag, "days": [d["days"][0], d["days"][-1], len(d["days"])], "n_transitions": d["n"],
           "n_exposed": kd.m, "classes": [L.CLASSES[c] for c in cls], "triples": tri, "implied_lag0": implied(tri, cls),
           "loco": lo, "stale": stale, "pre_read_beta": pre, "free_kernel_alldays": free_kernel,
           "readout": readout_delays(goal), "verdict": vd, "cells": dict(zip([L.CLASSES[c] for c in cls], cells)),
           "secs": time.time() - t0}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--goal", type=int, required=True)
    ap.add_argument("--nboot", type=int, default=100)
    a = ap.parse_args()
    res = run(a.goal, nboot=a.nboot)
    od = L.OUT / f"G{a.goal:02d}"
    od.mkdir(parents=True, exist_ok=True)
    (od / "results.json").write_text(json.dumps(res, indent=1))
    print(json.dumps({k: res[k] for k in ("verdict", "cells", "classes", "secs")}))
    for c, x in res["loco"].items():
        print(c, "T", x["T"], "S", {k: round(v, 1) for k, v in x["S"].items()}, "ci f-l", np.round(x["ci"]["free-lever"], 1),
              "l-d", np.round(x["ci"]["lever-delay"], 1))
    print("theta", res["triples"]["theta_deg"], "K", [round(k["est"], 2) for k in res["triples"]["K"]])
    for c in res["classes"]:
        print(c, res["triples"][c])
    print("stale", res["stale"])


if __name__ == "__main__":
    main()
