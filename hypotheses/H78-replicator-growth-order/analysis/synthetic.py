"""H78 + H77 synthetic validation (axis F) on each period's real call schedule.

Worlds (infra/shared/replicator_sim.py): neutral (p = 1, A = 1; H06/Hubbell limit), conformist (p = 1.4, sigma_A = 0.5),
parabolic (p = 0.5, sigma_A = 0.5), field (p = 0, sigma_A = 0.5); and two neutral worlds with the idle hazard x0.25 and x4
(to move sigma*). Each world is calibrated to the period's real measured counts of recruitments, births and expiries
(aggregate counts only), then replicated. Measurement runs through the real label builder.

Per run: growth order p (primary pooled over units; whole-period fit; repo FE; conditional logit), sigma* measured vs true
(true = the same plateau rule on the simulated true events), the resolution statistic and its permutation p, the departure
order q. Outputs: data/processed/H78-replicator-growth-order/synthetic/runs_G<NN>.parquet and
data/processed/H77-repos-as-replicators/synthetic/runs_G<NN>.parquet (same rows; H77 reads the sigma* columns).
Usage: uv run python hypotheses/H78-replicator-growth-order/analysis/synthetic.py --periods 31 33 --reps 30
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import json  # noqa: E402
import math  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
import replicator_fit as F  # noqa: E402
import replicator_hosts as R  # noqa: E402
import replicator_sim as S  # noqa: E402

OUT78 = ROOT / "data/processed/H78-replicator-growth-order/synthetic"
OUT77 = ROOT / "data/processed/H77-repos-as-replicators/synthetic"
WORLDS = {"neutral": dict(p=1.0, sigma_A=0.0), "conformist": dict(p=1.4, sigma_A=0.5),
          "parabolic": dict(p=0.5, sigma_A=0.5), "field": dict(p=0.0, sigma_A=0.5),
          "neutral_eps_lo": dict(p=1.0, sigma_A=0.0, eps_x=0.25), "neutral_eps_hi": dict(p=1.0, sigma_A=0.0, eps_x=4.0),
          # A2 (post hoc, after the first real run): fitness heterogeneity without interaction (p = 1)
          "fitness05": dict(p=1.0, sigma_A=0.5), "fitness10": dict(p=1.0, sigma_A=1.0), "fitness15": dict(p=1.0, sigma_A=1.5)}


def real_targets(g: int) -> dict:
    d = ROOT / f"data/processed/H77-repos-as-replicators/G{g:02d}"
    ev = pl.read_parquet(d / "events.parquet")
    bt = pl.read_parquet(d / "bins.parquet")
    k = dict(ev.group_by("kind").len().iter_rows())
    ncom = pl.read_parquet(d / "repos.parquet")["n_commits"].sum()
    hc = bt["C_host"].sum()
    return {"R": k.get("recruit", 0), "B": k.get("birth", 0), "X": k.get("expire", 0) + k.get("leave", 0),
            "pi_c": float(ncom / max(hc, 1)), "calls": int(bt.select("bin", "C").unique()["C"].sum())}


E_MEAS = 100


def measure(commits, calls, umap, labs, days, g):
    ev, bt, lt = R.build_from_frames(commits, calls, umap, labs, {}, g, days, tag=False, E=E_MEAS)
    return ev, bt


def one_run(ctx, prm, seed, true_too=True):
    calls, umap, labs, days, g = ctx
    com, tev = S.simulate(calls, p=prm["p"], c=prm["c"], beta=prm["beta"], eps=prm["eps"], pi_c=prm["pi_c"],
                          sigma_A=prm["sigma_A"], seed=seed)
    if com.height == 0:
        return None, None, None
    ev, bt = measure(com, calls, umap, labs, days, g)
    tbt = None
    if true_too:
        cb = R.clock_bins(calls, umap)
        tbt, _ = R.bin_table(tev, cb, labs)
    return ev, bt, tbt


def calibrate(ctx, world, tgt, iters=4):
    """Calibrated with the real tables expiry (E = 100) whatever E the measurement sweep uses."""
    global E_MEAS
    e_keep, E_MEAS = E_MEAS, 100
    calls = ctx[0]
    host_calls = tgt["calls"] * 0.5
    prm = {"p": world["p"], "sigma_A": world["sigma_A"], "pi_c": max(min(tgt["pi_c"], 0.9), 0.005),
           "beta": max(tgt["B"], 1) / len(calls), "eps": max(tgt["X"], 1) / host_calls * world.get("eps_x", 1.0),
           "c": max(tgt["R"], 1) / len(calls) * 2}
    for it in range(iters):
        ev, bt, _ = one_run(ctx, prm, 10_000 + it, true_too=False)
        if ev is None:
            prm["pi_c"] *= 2
            continue
        k = dict(ev.group_by("kind").len().iter_rows())
        rm, bm, xm = k.get("recruit", 0), k.get("birth", 0), k.get("expire", 0)
        prm["c"] *= min(max((tgt["R"] + 1) / (rm + 1), 0.2), 5)
        prm["beta"] *= min(max((tgt["B"] + 1) / (bm + 1), 0.2), 5)
        if "eps_x" not in world:
            prm["eps"] *= min(max((tgt["X"] + 1) / (xm + 1), 0.2), 5)
    E_MEAS = e_keep
    return prm


def stats(bt, tbt, ev):
    row = {}
    po = F.period_order(bt)
    row["p_pooled"] = po["pooled"]["est"] if po["pooled"] else None
    row["p_pooled_se"] = po["pooled"]["se"] if po["pooled"] else None
    row["p_whole"] = po["whole"]["est"] if po["whole"] else None
    row["p_whole_se"] = po["whole"]["se"] if po["whole"] else None
    row["p_testable"] = po["testable"]
    row["n_rec"] = po["n_events"]
    fe = F.poisson_order(bt, fe=True)
    row["p_fe"] = fe["est"] if fe else None
    row["p_fe_se"] = fe["se"] if fe else None
    cl = F.clogit_order(R.choice_sets(ev))
    row["p_clogit"] = cl["est"] if cl else None
    row["p_clogit_se"] = cl["se"] if cl else None
    q = F.depart_order(bt)
    row["q"] = q["est"] if q else None
    allb = sorted(bt["bin"].unique().to_list())
    sg = F.sigma_star(bt, allb)
    if sg:
        row.update({"sigma": sg["est"], "sigma_se": sg["se"], "sigma_testable": sg["testable"], "J_plus": sg["J_plus"],
                    "J_minus": sg["J_minus"]})
        rs = F.resolution(bt, allb, sg, n_perm=199)
        row.update({"res_frac": rs.get("frac"), "res_p": rs.get("p_perm"), "res_n_extinct": rs.get("n_extinct"),
                    "n_frustrated": rs.get("n_frustrated")})
    if tbt is not None and tbt.height:
        tb = sorted(tbt["bin"].unique().to_list())
        ts = F.sigma_star(tbt, tb)
        row["sigma_true"] = ts["est"] if ts else None
    return row


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--periods", type=int, nargs="+", required=True)
    ap.add_argument("--reps", type=int, default=30)
    ap.add_argument("--worlds", nargs="*", default=list(WORLDS))
    ap.add_argument("--E", type=int, default=100, help="label expiry used by the measurement (amendment A1 sweep)")
    ap.add_argument("--tag", default="", help="output suffix")
    a = ap.parse_args()
    global E_MEAS
    E_MEAS = a.E
    OUT77.mkdir(parents=True, exist_ok=True)
    OUT78.mkdir(parents=True, exist_ok=True)
    labs = dict(R.roster().select("agent", "lab").iter_rows())
    for g in a.periods:
        t0 = time.time()
        days = R.period_days(g)
        calls = R.load_calls(g, days)
        umap = R.unit_of_day(g)
        ctx = (calls, umap, labs, days, g)
        tgt = real_targets(g)
        rows, cal = [], {}
        for wn in a.worlds:
            w = WORLDS[wn]
            prm = calibrate(ctx, w, tgt)
            cal[wn] = prm
            for r in range(a.reps):
                ev, bt, tbt = one_run(ctx, prm, 1000 * list(WORLDS).index(wn) + r)
                if ev is None or bt.height == 0:
                    continue
                row = {"period": g, "world": wn, "rep": r, "p_true": w["p"], **stats(bt, tbt, ev)}
                rows.append(row)
            print(f"G{g:02d} {wn} done ({time.time() - t0:.0f}s)", flush=True)
        df = pl.DataFrame(rows, infer_schema_length=None)
        df.write_parquet(OUT78 / f"runs_G{g:02d}{a.tag}.parquet")
        df.write_parquet(OUT77 / f"runs_G{g:02d}{a.tag}.parquet")
        (OUT78 / f"calib_G{g:02d}{a.tag}.json").write_text(json.dumps({"targets": tgt, "params": cal}, indent=1))


if __name__ == "__main__":
    main()
