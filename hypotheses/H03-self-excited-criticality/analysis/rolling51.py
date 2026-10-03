"""#51 (private-role era) drift: Hawkes fits in windows of consecutive non-holdout #51 days (tail from 2026-09-07 is
held out and absent from the processed data).

  rolling: 5-day windows, step 1 day; M1_B2 (+ profile CI), P_B2, M2_grid, M3_sc
  block:   non-overlapping 5-day blocks; M1_B2 and M3_sc with day-level bootstrap (B reps); used for the P5 test

Output: data/processed/H03-self-excited-criticality/rolling51.parquet, rolling51_boot.parquet
Run: uv run python hypotheses/H03-self-excited-criticality/analysis/rolling51.py [B]
"""
from __future__ import annotations

import sys
import time
from multiprocessing import Pool

import numpy as np
import polars as pl

from common import DATA, N_WORKERS, fit_model, hc, load, specs, write_provenance

WIN = 5
G = {}


def _init():
    days, ev, exo = load()
    G["days"] = days
    G["dm"] = {s: hc.make_days(ev, exo, days, s) for s in ("TALK", "ALL")}


def run_window(task):
    kind, w0, keys, eset, B = task
    t0 = time.time()
    days, dm = G["days"], G["dm"][eset]
    sub = days.filter(pl.col("day_id").is_in(keys))
    meta = {"kind": kind, "w0": w0, "set": eset, "first_date": sub["pt_date"].min(), "last_date": sub["pt_date"].max(),
            "N_active": float(sub["n_active"].mean()), "hours": float(sub["T_s"].median() / 3600),
            "events_per_day": float((sub["n_talk"] if eset == "TALK" else sub["n_all"]).mean())}
    sp = specs()
    rows, boots = [], []
    models = ["M1_B2", "P_B2", "M2_grid", "M3_sc", "M3_self", "M1_B0"] if kind == "rolling" else ["M1_B2", "M3_sc"]
    fits = {}
    for m in models:
        ds = hc.Dataset(dm, keys, sp[m])
        f = fit_model(m, ds)
        fits[m] = f
        s = f.summary()
        s.update(meta); s["model"] = m
        if m == "M1_B2" and kind == "rolling":
            s["n_prof_lo"], s["n_prof_hi"] = hc.profile_ci_n(f)
        rows.append(s)
    if B:
        rng = np.random.default_rng(w0 * 10 + (eset == "ALL"))
        for m in ("M1_B2", "M3_sc"):
            for b in range(B):
                bk = list(rng.choice(keys, len(keys), replace=True))
                ds = hc.Dataset(dm, bk, sp[m])
                p0, _ = hc.transfer_params(fits[m], ds)
                f = fit_model(m, ds, p0=p0, beta_starts=[1 / 10, 1 / 1000] if ds.free_beta else None)
                s = f.summary()
                boots.append({**meta, "model": m, "rep": b, "n": s["n"], "n_self": s.get("n_self", np.nan),
                              "n_cross": s.get("n_cross", np.nan), "tau_s": s.get("tau_s", np.nan)})
    print(f"{kind} {w0} {eset} {meta['first_date']}: {time.time() - t0:.0f}s", flush=True)
    return rows, boots


def main():
    B = int(sys.argv[1]) if len(sys.argv) > 1 else 100
    days, _, _ = load()
    d51 = days.filter(pl.col("goal_no") == 51).sort("pt_date")
    assert d51["pt_date"].max() < "2026-09-07"
    keys = d51["day_id"].to_list()
    tasks = []
    for eset in ("ALL", "TALK"):
        for w0 in range(0, len(keys) - WIN + 1):
            tasks.append(("rolling", w0, keys[w0:w0 + WIN], eset, 0))
        for w0 in range(0, len(keys) - WIN + 1, WIN):
            tasks.append(("block", w0, keys[w0:w0 + WIN], eset, B))
    tasks.sort(key=lambda t: -t[4])  # bootstrap blocks first
    with Pool(N_WORKERS, initializer=_init) as pool:
        out = pool.map(run_window, tasks, chunksize=1)
    pl.DataFrame([r for o in out for r in o[0]], infer_schema_length=None).write_parquet(
        DATA / "rolling51.parquet", compression="zstd")
    pl.DataFrame([r for o in out for r in o[1]]).write_parquet(DATA / "rolling51_boot.parquet", compression="zstd")
    write_provenance({"rolling51.parquet": {"built_by": "analysis/rolling51.py", "window_days": WIN, "B_block": B,
                                            "days": f"{d51['pt_date'].min()}..{d51['pt_date'].max()} ({len(keys)})"}})


if __name__ == "__main__":
    main()
