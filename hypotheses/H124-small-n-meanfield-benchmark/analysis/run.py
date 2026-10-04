"""H124 real-data benchmark (after synthetic.py). Per unit: exact ML vs nMF, TAP, MS (+ own-spin stratified variants,
A1) on the per-call talk clock; day-bootstrap CIs; ML noise nu_J; circular-shift coupling-free null; leave-one-day-out
log-likelihood per estimator; 1-min grid companion (talk, activity). Natives N1 (G04 vs G06 J-bar) and N2 (G08
data-length curve).

Output: data/processed/H124-small-n-meanfield-benchmark/results/{percall,grid,n1,n2}.json
Usage: uv run python hypotheses/H124-small-n-meanfield-benchmark/analysis/run.py [--boot 200]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h124lib as L  # noqa: E402

UNITS = ["2", "3", "4a", "4c", "5", "6a", "6b", "7", "8"]


def q(v):
    v = np.asarray([x for x in v if x == x])
    return [float(np.quantile(v, 0.025)), float(np.quantile(v, 0.975))] if len(v) > 5 else [None, None]


def bench(rows, N, rng, B, shift_fn=None, n_shift=20, ll=True):
    res = L.fit_all(rows, N)
    e = L.errors(res)
    off = ~np.eye(N, dtype=bool)
    J = res["ML"][1]
    out = {"ML_J": J.tolist(), "ML_h": res["ML"][0].tolist(), "ref_sigma": e["ref_sigma"],
           "normJ_off": e["ref_normJ_off"], "Jbar_off": float(np.nanmean(J[off])),
           "Jii": np.diag(J).tolist(), "m": [float(rows[i][1].mean()) for i in range(N)],
           "n_rows": [int(len(rows[i][1])) for i in range(N)]}
    for k in L.METHODS:
        out[k] = {kk: e[k][kk] for kk in ("epsJ", "epsJ_all", "eps_sigma", "cover", "shrink", "sigma")}
    boots = {k: {"epsJ": [], "eps_sigma": []} for k in L.METHODS}
    nu, jbar, sig = [], [], []
    for _ in range(B):
        rb = L.boot_days(rows, rng)
        rr = L.fit_all(rb, N)
        eb = L.errors(rr)
        for k in L.METHODS:
            boots[k]["epsJ"].append(eb[k]["epsJ"])
            boots[k]["eps_sigma"].append(eb[k]["eps_sigma"])
        Jb = rr["ML"][1]
        nu.append(float(np.linalg.norm((Jb - J)[off]) / np.linalg.norm(J[off])))
        jbar.append(float(np.nanmean(Jb[off])))
        sig.append(eb["ref_sigma"])
    for k in L.METHODS:
        out[k]["epsJ_ci"] = q(boots[k]["epsJ"])
        out[k]["eps_sigma_ci"] = q(boots[k]["eps_sigma"])
        out[k]["boot_fail_share"] = float(np.mean([x != x for x in boots[k]["epsJ"]]))
    out["nu_J"] = float(np.median(nu)) if nu else None
    out["Jbar_ci"] = q(jbar)
    out["ref_sigma_ci"] = q(sig)
    if shift_fn is not None:
        nulls = []
        for _ in range(n_shift):
            rs = shift_fn(rng)
            Js = L.fit_all(rs, N, methods=())["ML"][1]
            nulls.append(float(np.linalg.norm(Js[off])))
        out["normJ_off_null_q95"] = float(np.quantile(nulls, 0.95))
        out["normJ_off_null_med"] = float(np.median(nulls))
        out["informative"] = bool(out["normJ_off"] > out["normJ_off_null_q95"])
    if ll:
        out["heldout_ll"] = {k: L.heldout_ll(rows, N, k) for k in ("ML",) + L.METHODS}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=200)
    a = ap.parse_args()
    R = L.OUT / "results"
    R.mkdir(exist_ok=True)
    rng = np.random.default_rng(124)
    t0 = time.time()
    pc, gr = {}, {}
    for u in UNITS:
        rows, N = L.percall_rows(u)
        pc[u] = bench(rows, N, rng, a.boot, shift_fn=lambda r, u=u: L.shift_null_rows(u, r))
        print(u, "percall", {k: (round(pc[u][k]["epsJ"], 3), round(pc[u][k]["eps_sigma"], 3) if pc[u][k]["eps_sigma"] == pc[u][k]["eps_sigma"] else None, round(pc[u][k]["cover"], 2)) for k in L.METHODS},
              "nu", round(pc[u]["nu_J"], 3), "inf", pc[u]["informative"], f"{time.time() - t0:.0f}s", flush=True)
        gr[u] = {}
        for ch in ("talk", "act"):
            g, N = L.grid_rows(u, ch)
            if g is None or len(set(g[0][2])) < 2:
                continue
            try:
                gr[u][ch] = bench(g, N, rng, min(a.boot, 100), ll=False)
                print(u, "grid", ch, {k: round(gr[u][ch][k]["epsJ"], 3) for k in L.METHODS}, flush=True)
            except Exception as ex:  # noqa: BLE001
                gr[u][ch] = {"error": str(ex)}
    (R / "percall.json").write_text(json.dumps(pc, indent=1, default=float))
    (R / "grid.json").write_text(json.dumps(gr, indent=1, default=float))
    # N1: J-bar cooperation (4a, 4c) vs competition (6a, 6b): pooled per period via day bootstrap of each unit
    n1 = {u: {"Jbar": pc[u]["Jbar_off"], "ci": pc[u]["Jbar_ci"]} for u in ("4a", "4c", "6a", "6b")}
    (R / "n1.json").write_text(json.dumps(n1, indent=1))
    # N2: G08 data-length curve
    rows, N = L.percall_rows("8")
    full = L.fit_all(rows, N)["ML"][1]
    off = ~np.eye(N, dtype=bool)
    days = sorted(set(np.concatenate([d for _, _, d in rows.values()])))
    n2 = {}
    for nd in (2, 4, 8, 16):
        rec = {k: [] for k in L.METHODS}
        rec["nu_full"] = []
        for _ in range(20):
            keep = rng.choice(days, nd, replace=False)
            rs = L.subset_days(rows, keep)
            rr = L.fit_all(rs, N)
            e = L.errors(rr)
            for k in L.METHODS:
                rec[k].append(e[k]["epsJ"])
            rec["nu_full"].append(float(np.linalg.norm((rr["ML"][1] - full)[off]) / np.linalg.norm(full[off])))
        n2[nd] = {k: float(np.nanmedian(v)) if np.isfinite(v).any() else None for k, v in rec.items()}
        print("N2", nd, n2[nd], flush=True)
    (R / "n2.json").write_text(json.dumps(n2, indent=1))


if __name__ == "__main__":
    main()
