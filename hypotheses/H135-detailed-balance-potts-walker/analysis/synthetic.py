"""H135 synthetic validation (axis F): walkers with planted truth on real unit skeletons.

  POLARS_MAX_THREADS=1 ... uv run python hypotheses/H135-detailed-balance-potts-walker/analysis/synthetic.py [--runs 200]
      [--only 51g|attention ...]

Skeletons (card): 31a, 38a, 41, 44a, 51c (work) and 38a (attention), the largest unit of each card period; plus the
unit-channels that pass the structural precondition under the 80% co-alive variant (51a, 51c, 51f, 51g, 51h
attention) and G40 (both channels, native N3). Real agents, own-call clocks, project availability windows, first
labels; pi from the unit's own H94 fit. Worlds W0 (heat-bath), W0M (Metropolis), W1 (age drift, lambda 1.5, habit 2),
W2 (sink, occupants^1.5), W3 (cycle, kappa 2, habit 2), W4 (habit 2); all share the field ln pi_i. Dwell aging
gamma = -0.3; the hazard intercept is calibrated per world to the observed hop count.
Per run, both co-alive rules: O1 (slope, r, pass), m_pi, m2co, (theta, beta), pair-flip p values; O4 (psi, rho) on
the first 50 runs of W0, W0M, W4; the LR interaction test on the first 30 W0 runs; G40: hub flux on days 1-2.
Writes data/processed/H135-detailed-balance-potts-walker/synthetic/<unit>_<channel>.parquet (checkpoint per skeleton).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
import zlib  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h135lib as L  # noqa: E402

SKELETONS = [("31a", "work"), ("38a", "work"), ("41", "work"), ("44a", "work"), ("51c", "work"), ("38a", "attention"),
             ("51a", "attention"), ("51c", "attention"), ("51f", "attention"), ("51g", "attention"), ("51h", "attention"),
             ("40", "work"), ("40", "attention")]
WORLDS = ["W0", "W0M", "W1", "W2", "W3", "W4"]


def goal_of(unit: str) -> int:
    return int(unit[:2])


def load_skeleton(unit: str, ch: str, rule: str = "coalive") -> tuple[L.Skeleton, dict]:
    g = goal_of(unit)
    d = L.D / f"G{g:02d}"
    calls = pl.read_parquet(d / "calls.parquet").filter(pl.col("unit") == unit)
    ct = {int(a): np.sort(gg["t"].to_numpy()) for (a,), gg in calls.group_by(["agent"])}
    first = {int(a): (p, t) for a, p, t in pl.read_parquet(d / f"first_{ch}.parquet").filter(pl.col("unit") == unit)
             .select("agent", "first_project", "t_first").iter_rows()}
    av = pl.read_parquet(d / f"avail_{ch}.parquet").filter(pl.col("unit") == unit)
    occ = pl.read_parquet(d / f"occupancy_{ch}.parquet").filter(pl.col("unit") == unit)
    hops = pl.read_parquet(d / f"hops_{ch}.parquet").filter(pl.col("unit") == unit)
    pi_unit = dict(occ.group_by("project").agg(pl.col("pi").first()).iter_rows())
    av = av.filter(pl.col("project").is_in(list(pi_unit)))          # projects without quanta have no pi
    avail = {p: (a0, a1) for p, a0, a1 in av.select("project", "a0", "a1").iter_rows()}
    rank = dict(av.select("project", "age_rank").iter_rows())
    lnpi = {(int(a), p): float(np.log(max(x, np.exp(L.LNPI_FLOOR)))) for a, p, x in occ.select("agent", "project", "pi_i").iter_rows()}
    co = {r: set(av.filter(pl.col(r))["project"].to_list()) for r in ("coalive", "coalive80")}
    sk = L.Skeleton(ct, first, avail, lnpi, rank, hops.height, co[rule], pi_unit)
    return sk, {"avail": avail, "lnpi": lnpi, "co": co, "hops": hops, "occ": occ}


def hub_flux(H: pl.DataFrame, hub: str, t_split: float) -> float:
    e = H.filter(pl.col("t") <= t_split)
    i, o = e.filter(pl.col("dst") == hub).height, e.filter(pl.col("src") == hub).height
    return (i - o) / (i + o) if i + o else np.nan


def g40_meta(ch):
    d = L.D / "G40"
    occ = pl.read_parquet(d / "occupancy_work.parquet")
    hub = occ.group_by("project").agg(pl.col("pi").first()).sort("pi", descending=True)["project"][0]
    cal = pl.read_parquet(L.ROOT / "data/processed/shared/calendar.parquet").filter(pl.col("goal_no") == 40).sort("pt_date")
    return hub, cal["win_end"][1].timestamp()


def run_skeleton(unit, ch, n_runs, out_dir):
    f = out_dir / f"{unit}_{ch}.parquet"
    if f.exists():
        print(f"skip {f.name}", flush=True)
        return
    t0 = time.time()
    sk, meta = load_skeleton(unit, ch)
    hub = t_split = None
    if unit == "40":
        hub, t_split = g40_meta(ch)
    rows, cal = [], {}
    for w in WORLDS:
        rng = np.random.default_rng(zlib.crc32(f"{unit}|{ch}|{w}".encode()))
        c = L.calibrate_c(sk, w, rng, n=3)
        cal[w] = c
        for k in range(n_runs):
            H, Tp = L.simulate(sk, w, c, rng)
            rec = {"unit": unit, "channel": ch, "world": w, "run": k, "c": c}
            for rule in ("coalive", "coalive80"):
                sk.coalive = meta["co"][rule]
                st = L.sim_stats(sk, H, Tp, meta["lnpi"], meta["avail"],
                                 with_o4=(rule == "coalive80" and k < 50 and w in ("W0", "W0M", "W4", "W1")),
                                 lr=(rule == "coalive80" and k < 30 and w == "W0"))
                pre = "" if rule == "coalive" else "v80_"
                rec.update({pre + key: (float(v) if v is not None else None) for key, v in st.items()})
            if hub is not None:
                rec["hub_flux_early"] = hub_flux(H, hub, t_split)
            rows.append(rec)
        print(f"{unit}|{ch} {w} c={c:.2f} {time.time() - t0:.0f}s", flush=True)
    df = pl.DataFrame(rows, infer_schema_length=None)
    df.write_parquet(f, compression="zstd")
    print(f"done {unit}|{ch} hops_obs {sk.n_hops} in {time.time() - t0:.0f}s", flush=True)


LR_SKELETONS = [("51a", "attention"), ("51c", "attention"), ("51f", "attention"), ("51g", "attention"), ("51h", "attention")]


def lr_null(n_runs, out_dir):
    """Amendment A1: W0 null distribution of O4's LR interaction test (chi2 p and statistic) on the variant-testable
    skeletons, 80% co-alive rule, the W0 hazard intercept taken from the main synthetic file."""
    for unit, ch in LR_SKELETONS:
        f = out_dir / f"lrnull_{unit}_{ch}.parquet"
        if f.exists():
            continue
        t0 = time.time()
        sk, meta = load_skeleton(unit, ch, "coalive80")
        c = float(pl.read_parquet(out_dir / f"{unit}_{ch}.parquet").filter(pl.col("world") == "W0")["c"][0])
        rng = np.random.default_rng(zlib.crc32(f"lrnull|{unit}|{ch}".encode()))
        rows = []
        for k in range(n_runs):
            H, _ = L.simulate(sk, "W0", c, rng)
            r4 = L.o4(H, meta["avail"], meta["lnpi"], lr=True)
            if r4:
                rows.append({"run": k, "lr": r4.get("lr"), "lr_df": r4.get("lr_df"), "lr_p": r4.get("lr_p"), "psi": r4["psi"],
                             "rho": r4["rho"]})
        pl.DataFrame(rows).write_parquet(f)
        print(f"lrnull {unit}|{ch} {len(rows)} runs {time.time() - t0:.0f}s", flush=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=200)
    ap.add_argument("--only", action="append")
    ap.add_argument("--lr-null", type=int, default=0, help="Amendment A1: W0 LR null runs per variant skeleton")
    a = ap.parse_args()
    out = L.D / "synthetic"
    out.mkdir(parents=True, exist_ok=True)
    if a.lr_null:
        lr_null(a.lr_null, out)
        return
    sks = SKELETONS if not a.only else [tuple(x.split("|")) for x in a.only]
    for u, ch in sks:
        run_skeleton(u, ch, a.runs, out)


if __name__ == "__main__":
    main()
