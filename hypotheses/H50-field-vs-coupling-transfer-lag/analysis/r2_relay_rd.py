"""R6 follow-up (POST HOC, written after the pre-registered event study failed its pre-trend check on real data).
(1) Diagnosis: synthetic worlds where talk depends on the call's own interval length (W0L, W1L) on the real skeleton.
    If the event study's pre-trend appears there with the real sign, the failure is length bias at e = -1.
(2) A length-robust graph-clause estimator: start-time RD at the relay posting time t_M on C's calls, anchors restricted
    to C-hops >= 2 on A's clock (r2lib.relay_rd). Validated on W0, W0L, W1, W1L, W2, then run on real units.
Writes r2/synthetic_relay_rd.json, r2/relay_rd_units.parquet, r2/relay_rd_summary.json.

Usage: uv run python hypotheses/H50-field-vs-coupling-transfer-lag/analysis/r2_relay_rd.py --synth [--seeds 5] | --real
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ.setdefault(_v, "2")
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import r2lib as R2  # noqa: E402
import r2_relay as RR  # noqa: E402

OUT = RR.OUT
LEN = {"III": -1.0, "I": 1.0}     # sign of the real dependence: long regime-III calls are pauses, long regime-I calls chat


def run_one(U, R, P, T, y, nboot, seed):
    r = RR.analyse(U, P, y, R, nboot=nboot, seed=seed)
    ev = r["treated"]
    out = dict(G=ev[0], gm2=ev[-2], gp1=ev[1])
    for lab, sel, mh in (("rd2", None, 2), ("rd2_named", T["named"], 2), ("rd2_unnamed", ~T["named"], 2), ("rd1", None, 1)):
        out[lab] = R2.relay_rd(U, R, T, y, sel=sel, min_ahop=mh, nboot=nboot, seed=seed)
    return out


def synth(seeds):
    res = {}
    for u in ("51b", "38a", "27", "51c"):
        U, R = RR.load(u)
        reg = str(U["regime"])
        P = R2.relay_pairs(U, R)
        T = R2.relay_triples(U, R)
        worlds = {"W0": dict(J=0.0, J_named=0.0), "W0L": dict(J=0.0, J_named=0.0, len_beta=LEN[reg]),
                  "W1": {}, "W1L": dict(len_beta=LEN[reg]), "W2": dict(dead=1)}
        for w, wp in worlds.items():
            prm = dict(RR.COMMON, **RR.SIZES[reg])
            prm.update(wp)
            key = f"{u}|{w}"
            res[key] = []
            for sd in range(seeds):
                t0 = time.time()
                y, truth = R2.syn_talk(U, R, prm, seed=300 + sd)
                o = run_one(U, R, P, T, y.astype(float), 100, sd)
                tv = np.array([truth.get((int(m), int(c)), np.nan) for m, c in zip(T["M"], T["C"])])
                o["truth"] = float(np.nanmean(tv)) if np.isfinite(tv).any() else 0.0
                res[key].append(o)
                print(f"{key} s{sd} {time.time() - t0:.0f}s ES G {o['G'][0]:.4f} g-2 {o['gm2'][0]:.4f} | RD2 {o['rd2']['J']:.4f} "
                      f"[{o['rd2']['lo']:.4f},{o['rd2']['hi']:.4f}] named {o['rd2_named']['J']:.4f} RD1 {o['rd1']['J']:.4f} "
                      f"truth {o['truth']:.4f}", flush=True)
            (OUT / "r2/synthetic_relay_rd.json").write_text(json.dumps(res, default=float))


def real():
    units = pl.read_parquet(OUT / "units.parquet").filter(pl.col("eligible") & (pl.col("kind") == "period_unit"))
    rows = []
    for u, reg, g in zip(units["unit"], units["regime"], units["goal_no"]):
        U, R = RR.load(u)
        T = R2.relay_triples(U, R)
        y = U["calls"]["talk"].astype(float)
        row = dict(unit=u, regime=reg, goal_no=int(g), n_triples=len(T["M"]))
        if len(T["M"]) < 300:
            rows.append(dict(row, eligible=False))
            continue
        row["eligible"] = True
        for lab, sel, mh in (("rd2", None, 2), ("rd2_named", T["named"], 2), ("rd2_unnamed", ~T["named"], 2), ("rd1", None, 1)):
            if sel is not None and sel.sum() < 100:
                continue
            r = R2.relay_rd(U, R, T, y, sel=sel, min_ahop=mh, nboot=200, seed=5)
            for k in ("J", "lo", "hi", "se", "n_rows"):
                row[f"{lab}_{k}"] = r[k]
        rows.append(row)
        print(f"{u} ({reg}) triples {len(T['M'])} RD2 {row['rd2_J']:.4f} [{row['rd2_lo']:.4f},{row['rd2_hi']:.4f}] "
              f"named {row.get('rd2_named_J', float('nan')):.4f} unnamed {row.get('rd2_unnamed_J', float('nan')):.4f} "
              f"RD1 {row['rd1_J']:.4f}", flush=True)
    df = pl.DataFrame(rows, infer_schema_length=None)
    df.write_parquet(OUT / "r2/relay_rd_units.parquet")
    summ = {}
    for reg in ("I", "II", "III"):
        s = df.filter(pl.col("eligible") & (pl.col("regime") == reg))
        if not len(s):
            continue
        d = dict(n_units=len(s))
        for lab in ("rd2", "rd2_named", "rd2_unnamed", "rd1"):
            if f"{lab}_J" not in s.columns:
                continue
            ss = s.filter(pl.col(f"{lab}_J").is_not_null() & pl.col(f"{lab}_se").is_not_nan())
            m, se = R2.ivw(ss[f"{lab}_J"].to_numpy(), ss[f"{lab}_se"].to_numpy())
            d[lab] = dict(J=m, se=se, pos=int((ss[f"{lab}_lo"] > 0).sum()), neg=int((ss[f"{lab}_hi"] < 0).sum()), n=len(ss))
        summ[reg] = d
        print(reg, json.dumps(d))
    (OUT / "r2/relay_rd_summary.json").write_text(json.dumps(summ, indent=1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--synth", action="store_true")
    ap.add_argument("--real", action="store_true")
    ap.add_argument("--seeds", type=int, default=5)
    a = ap.parse_args()
    if a.synth:
        synth(a.seeds)
    if a.real:
        real()


if __name__ == "__main__":
    main()
