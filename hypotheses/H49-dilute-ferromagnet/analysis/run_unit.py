"""H49 pipeline, one unit at a time (replication units and native windows from units.parquet; non-holdout only).

Per unit: conditioned / edge / raw pseudolikelihood bonds on activity (and talk) spins, 200 joint block-shift
surrogates (spins, reasons and talk spins shifted together within (day, 30-min block); every step recomputed),
bond statistics against the pooled leave-one-out surrogate null, significant positive-bond graph and its percolation
statistics, CV-C10, 200-replicate day-block bootstrap of the conditioned fit.

Output: data/processed/H49-dilute-ferromagnet/<group>/<unit>.json and bonds/<unit>.parquet
Usage: uv run python hypotheses/H49-dilute-ferromagnet/analysis/run_unit.py --unit 40
       uv run python hypotheses/H49-dilute-ferromagnet/analysis/run_unit.py --all [--workers 2]
"""
from __future__ import annotations

import os

os.environ.setdefault("OMP_NUM_THREADS", "1")
import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
import zlib  # noqa: E402
from multiprocessing import Pool  # noqa: E402
from pathlib import Path  # noqa: E402

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "infra/shared"))
import h49lib as L  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from common import holdout_mask  # noqa: E402

N_SURR, N_BOOT = 200, 200


def scalarize(d):
    out = {}
    for k, v in d.items():
        if isinstance(v, np.ndarray):
            continue
        if isinstance(v, (np.floating, np.integer)):
            v = v.item()
        out[k] = v
    return out


def run(uid: str, n_surr=N_SURR, n_boot=N_BOOT, extra_sched=None, tag=None, seed_off=0, rows=None):
    """Run one unit. extra_sched: boolean (T,) minutes to drop like off-schedule minutes (native sensitivity runs).
    rows: boolean (T,) subset of minutes (split halves). tag: output name suffix; if tag is set, returns the result
    without writing the standard outputs."""
    units = pl.read_parquet(L.DATA / "units.parquet")
    meta = units.filter(pl.col("unit") == uid).to_dicts()[0]
    m = np.load(L.DATA / "mats" / f"{uid}.npz")
    days = [str(d) for d in m["days"]]
    cal = pl.read_parquet(L.SH / "calendar.parquet").filter(pl.col("pt_date").is_in(days))
    assert not cal["holdout"].any() and not any(holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list()))
    S, Tk, R, day, minute, sched = m["S"], m["Tk"], m["R"], m["day"], m["minute"], m["sched"].copy()
    agents = m["agents"].astype(int)
    if extra_sched is not None:
        sched = sched | extra_sched
    if rows is not None:
        S, Tk, R, day, minute, sched = S[rows], Tk[rows], R[rows], day[rows], minute[rows], sched[rows]
    t0 = time.time()
    seed = L.SEED + (zlib.crc32(uid.encode()) % 100_000) + seed_off
    res = L.run_dataset(S, R, sched, day, minute, Tk, n_surr=n_surr, seed=seed, n_boot=n_boot)
    N = res["N"]
    iu = L.triu(N)
    out = {"unit": uid, "meta": meta, "N": N, "T": res["T"], "n_pairs": res["n_pairs"], "n_surr": n_surr,
           "agents": agents.tolist(), "talk_agents": agents[res["talk_cols"]].tolist(), "variants": {}}
    brow = []
    for v, e in res["variants"].items():
        b = e["bonds"]
        ent = {k: e[k] for k in ("g", "VR", "E", "z_g", "rho_bar_ex", "cv_c10", "cv_c10_orig", "cv_c10_parts",
                                 "dC_tot", "dC_half_tot", "share_sig", "c10_insample", "iters")}
        ent["bonds"] = scalarize(b)
        ent["graph"] = e["graph"]
        if "talk" in e:
            ent["talk"] = {"N": e["talk"]["N"], "g": e["talk"]["g"], "E": e["talk"]["E"], "z_g": e["talk"]["z_g"],
                           "bonds": scalarize(e["talk"]["bonds"]), "graph": e["talk"]["graph"]}
        out["variants"][v] = ent
        bd = {"unit": [uid] * iu[0].size, "variant": [v] * iu[0].size, "channel": ["activity"] * iu[0].size,
              "a": agents[iu[0]], "b": agents[iu[1]], "J": b["dJ"] + b["mu"], "dJ": b["dJ"], "z": b["z"],
              "p_pos": b["p_pos"], "p_neg": b["p_neg"], "sig_pos": b["sig_pos"], "sig_neg": b["sig_neg"],
              "bh": b["bh"], "dC": e["dC"]}
        if v == "scaffold" and "boot" in res:
            bt = res["boot"]
            bd.update({"z_lo": bt["z_lo"], "z_hi": bt["z_hi"], "stab": bt["stab"]})
        brow.append(pl.DataFrame(bd))
        if "talk" in e:
            ta = agents[res["talk_cols"]]
            it = L.triu(len(ta))
            bt_ = e["talk"]["bonds"]
            brow.append(pl.DataFrame({"unit": [uid] * it[0].size, "variant": [v] * it[0].size,
                                      "channel": ["talk"] * it[0].size, "a": ta[it[0]], "b": ta[it[1]],
                                      "J": bt_["dJ"] + bt_["mu"], "dJ": bt_["dJ"], "z": bt_["z"],
                                      "p_pos": bt_["p_pos"], "p_neg": bt_["p_neg"], "sig_pos": bt_["sig_pos"],
                                      "sig_neg": bt_["sig_neg"], "bh": bt_["bh"]}))
    if "boot" in res:
        out["boot"] = {k: v for k, v in res["boot"].items() if not isinstance(v, np.ndarray)}
    out["runtime_s"] = time.time() - t0
    bonds = pl.concat(brow, how="diagonal_relaxed").with_columns(
        pl.col(pl.Float64).cast(pl.Float32), pl.col("a").cast(pl.Int16), pl.col("b").cast(pl.Int16))
    if tag is not None:
        return out, bonds
    gdir = L.DATA / meta["group"]
    gdir.mkdir(parents=True, exist_ok=True)
    (gdir / f"{uid}.json").write_text(json.dumps(out, indent=1, default=float))
    (L.DATA / "bonds").mkdir(exist_ok=True)
    bonds.write_parquet(L.DATA / "bonds" / f"{uid}.parquet", compression="zstd")
    return {"unit": uid, "runtime_s": out["runtime_s"]}


def _job(uid):
    t = time.time()
    r = run(uid)
    print(f"{uid} done {time.time() - t:.0f}s", flush=True)
    return r


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--unit")
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    if a.unit:
        print(run(a.unit))
        return
    units = pl.read_parquet(L.DATA / "units.parquet").sort("T", descending=True)["unit"].to_list()
    with Pool(min(a.workers, 2)) as pool:
        for r in pool.imap_unordered(_job, units):
            pass


if __name__ == "__main__":
    main()
