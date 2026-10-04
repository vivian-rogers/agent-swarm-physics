"""H02 round 1b: what did the activity_bins event-drop bug do to the #45 confirmatory rule's power? (synthetic only;
no holdout data is read.)

Village-like systems as in harness.run_C (N = 18, 241 one-min bins per day, 5 days, background couplings, a planted
leader with outgoing J_L to 5 followers, common + agent block drive), with per-agent (h, J_self) drawn from either the
round-1 calibration (buggy bins: active ~0.5) or the round-1b calibration (activity_bins_fixed: active ~0.67).
Each replicate is scored by the frozen #45 rule (KI-1 + block fields, rank 1 and z(I_k) >= 2 vs N1 surrogates) on
  clean     the simulated spins;
  thinned   the same spins after the bug's effect: each active minute of day d is kept with probability rho_d,
            rho_d drawn from the empirical day-level retention of active agent-minutes (old / fixed) over the
            non-holdout regime-III days (median 0.87, IQR 0.64-0.94, 5% quantile 0.14).
Output: data/processed/H02-couplings-are-real/r1b/thinning.parquet
Usage: OMP_NUM_THREADS=2 uv run python hypotheses/H02-couplings-are-real/analysis/r1b_thinning.py [reps] [n_surr]
"""
from __future__ import annotations

import os

os.environ.setdefault("VECLIB_MAXIMUM_THREADS", "1"); os.environ.setdefault("OMP_NUM_THREADS", "1")
import json  # noqa: E402
import sys  # noqa: E402
from multiprocessing import Pool  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h02lib as L  # noqa: E402
import r1b_common as RB  # noqa: E402

N, TD, KL, RHO, NBLK, D = 18, 241, 5, 0.15, 8, 5
CALS = {"r1": json.loads((RB.BASE / "calibration.json").read_text())["III"],
        "r1b": json.loads((RB.BASE / "r1b/calibration.json").read_text())["III"]}


def retention():
    cal = pl.read_parquet(RB.SH / "calendar.parquet").filter(~pl.col("holdout") & (pl.col("regime").cast(pl.String) == "III"))
    days = cal["pt_date"].to_list()
    o = (pl.scan_parquet(RB.SH / "activity_bins.parquet").filter(pl.col("pt_date").is_in(days)).group_by("pt_date")
         .agg((pl.col("state") >= 3).sum().alias("old")).collect())
    f = (pl.scan_parquet(RB.SH / "activity_bins_fixed.parquet").filter(pl.col("pt_date").is_in(days)).group_by("pt_date")
         .agg((pl.col("state") >= 3).sum().alias("new")).collect())
    d = o.join(f, on="pt_date")
    return (d["old"] / d["new"]).to_numpy()


RET = None


def system(rng, cal, JL):
    k = rng.integers(0, len(cal["h0"]), N)
    h0 = np.array(cal["h0"])[k]; Js = np.array(cal["Jself"])[k]
    Jx = np.zeros((N, N))
    m = rng.random((N, N)) < RHO; np.fill_diagonal(m, False)
    Jx[m] = rng.uniform(0.05, 0.25, m.sum()) * np.where(rng.random(m.sum()) < 0.7, 1, -1)
    if JL > 0:
        Jx[rng.choice(np.arange(1, N), KL, replace=False), 0] = JL
    field = rng.normal(0, cal["sigma_common"], (D, NBLK, 1)) + rng.normal(0, cal["sigma_agent"], (D, NBLK, N))
    return h0, Js, Jx, field


def rule(S, day, minute, rng, n_surr):
    J, _, _ = L.fit_kinetic(S, day, minute, "block", "1")
    I = L.net_influence(J)
    segs = L.segments(day, minute, "block")
    In = np.array([L.net_influence(L.fit_kinetic(L.circular_shift(S, segs, rng), day, minute, "block", "1")[0])
                   for _ in range(n_surr)])
    z = (I - In.mean(0)) / In.std(0)
    return L.rank_of(I, 0), float(z[0])


def job(args):
    calname, JL, rep, n_surr, ret = args
    rng = np.random.default_rng([20261004, int(JL * 100), rep, calname == "r1b"])
    h0, Js, Jx, field = system(rng, CALS[calname], JL)
    S, day, minute = L.simulate(h0, Js, Jx, D, TD, rng, blockfield=field)
    out = {"cal": calname, "JL": JL, "rep": rep, "active_clean": float((S > 0).mean())}
    r, z = rule(S, day, minute, rng, n_surr)
    out.update({"rank_clean": r, "z_clean": z, "pass_clean": bool(r == 1 and z >= 2)})
    rho = rng.choice(ret, D, replace=True)
    keep = rng.random(S.shape) < rho[day][:, None]
    St = np.where((S > 0) & ~keep, -1, S).astype(np.int8)
    r, z = rule(St, day, minute, rng, n_surr)
    out.update({"rank_thin": r, "z_thin": z, "pass_thin": bool(r == 1 and z >= 2), "active_thin": float((St > 0).mean()),
                "rho_mean": float(rho.mean())})
    return out


def main():
    reps = int(sys.argv[1]) if len(sys.argv) > 1 else 30
    n_surr = int(sys.argv[2]) if len(sys.argv) > 2 else 100
    ret = retention()
    jobs = [(c, JL, r, n_surr, ret) for c in ("r1", "r1b") for JL in (0.2, 0.3, 0.5) for r in range(reps)]
    with Pool(2) as p:
        res = pl.DataFrame(p.map(job, jobs, chunksize=2))
    res.write_parquet(RB.BASE / "r1b/thinning.parquet")
    print(res.group_by("cal", "JL").agg(pl.len(), pl.col("pass_clean").mean().round(2), pl.col("pass_thin").mean().round(2),
                                        (pl.col("rank_clean") == 1).mean().round(2).alias("rank1_clean"),
                                        (pl.col("rank_thin") == 1).mean().round(2).alias("rank1_thin"),
                                        pl.col("z_clean").median().round(2), pl.col("z_thin").median().round(2),
                                        pl.col("active_clean").mean().round(2), pl.col("active_thin").mean().round(2)).sort("cal", "JL"))


if __name__ == "__main__":
    main()
