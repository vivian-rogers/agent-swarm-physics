"""H11 synthetic validation (axis F): kinetic mean-field Potts at village N with village sampling.

S1  sign recovery and power of the primary (βJ_CW, period fields, day-jackknife t) and the secondary
    (βJ_PL with agent fields vs circular-shift and within-agent-day permutation nulls).
S2  confounds at βJ = 0: agent specialization (σ_h) and common day-level drift.
S3  first-order jump detection: field ramps at several βJ, an abrupt field step at βJ = 0, and constant fields.
S4  plmDCA (secondary) sign recovery.

Outputs: data/processed/H11-potts-labor-vs-herding/synthetic/*.parquet, figures/synthetic_*.pdf
Usage: uv run python analysis/synthetic.py [--reps 40] [--workers 2]
"""
from __future__ import annotations

import argparse
import json
import sys
from multiprocessing import Pool
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h11common as HC  # noqa: E402  (sets thread env vars)
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import potts_core as P  # noqa: E402

OUTD = HC.OUT / "synthetic"
N_NULL = 29


def one_rep(args):
    (cell, seed) = args
    rng = np.random.default_rng(seed)
    sim = P.simulate(N=cell["N"], q=cell["q"], bj=cell["bj"], days=cell["days"], wins_per_day=cell["wpd"],
                     p_obs=cell["p_obs"], sigma_h=cell["sigma_h"], drift=cell.get("drift"),
                     sweeps_per_window=cell.get("sweeps", 0.5), rng=rng)
    s = P.snap_from_arrays(sim["agent"], sim["label"], sim["day"], sim["win"], sim["S"], sim["coupled"], wins_per_day=cell["wpd"])
    full, se, _ = P.jackknife_cw(s, "period")
    D = s.n_days
    tcrit = stats.t.ppf(0.975, max(D - 1, 1))
    bj_cw = full["bj"]
    t_cw = bj_cw / se if se and se > 0 else np.nan
    pl_obs = P.fit_pl(s, "agent")["bj"]
    nul_shift = np.array([P.fit_pl(P.shift_snap(s, rng), "agent")["bj"] for _ in range(N_NULL)])
    nul_pday = np.array([P.fit_pl(s.with_labels(P.null_labels(s, "perm_day", rng)), "agent")["bj"] for _ in range(N_NULL)])
    z_shift = (pl_obs - nul_shift.mean()) / max(nul_shift.std(ddof=1), 1e-9)
    z_pday = (pl_obs - nul_pday.mean()) / max(nul_pday.std(ddof=1), 1e-9)
    return dict(**{k: (v if v is not None else 0.0) for k, v in cell.items()}, seed=seed, bj_cw=bj_cw, se_cw=se,
                t_cw=t_cw, sig_cw=bool(abs(t_cw) > tcrit) if np.isfinite(t_cw) else False, lr_cw=full.get("lr", np.nan),
                bj_pl=pl_obs, z_shift=z_shift, z_pday=z_pday, n_obs=len(s.label))


def jump_rep(args):
    cell, seed = args
    rng = np.random.default_rng(seed)
    kw = dict(N=cell["N"], q=cell["q"], bj=cell["bj"], days=cell["days"], wins_per_day=cell["wpd"], p_obs=cell["p_obs"],
              sigma_h=0.0, sweeps_per_window=0.5, rng=rng)
    if cell["kind"] == "ramp":
        kw["field_ramp"] = (1, -2.0, 3.0)
    elif cell["kind"] == "step":
        kw["field_step"] = (0.5, 1, 3.0)
    sim = P.simulate(**kw)
    s = P.snap_from_arrays(sim["agent"], sim["label"], sim["day"], sim["win"], sim["S"], sim["coupled"], wins_per_day=cell["wpd"])
    gw = sim["day"] * cell["wpd"] + sim["win"]
    t, k, n = P.dominant_series(s, 1, gw)
    j = P.fit_jump(t, k, n)
    cw = P.fit_cw(s, "period")
    # effective number of options before the transition (perplexity of real-state shares in the first third)
    first = gw < (cell["days"] * cell["wpd"]) / 3
    c = np.bincount(s.label[first & (s.label > 0)], minlength=sim["S"])[1:]
    p = c / max(c.sum(), 1)
    qeff = float(np.exp(-(p[p > 0] * np.log(p[p > 0])).sum())) if c.sum() else np.nan
    qr = max(2, int(round(qeff))) if np.isfinite(qeff) else 2
    mf_first_order = bool(cw["bj"] >= P.bj_spinodal(qr)) if qr >= 3 else bool(cw["bj"] >= 2.0)
    return dict(**cell, seed=seed, verdict=j["verdict"], tau=j.get("tau", np.nan), amp=j.get("amp", np.nan),
                pers=j.get("persistence_below_mid", np.nan), bj_cw=cw["bj"], qeff=qeff, mf_first_order=mf_first_order)


def plm_rep(args):
    cell, seed = args
    rng = np.random.default_rng(seed)
    sim = P.simulate(N=cell["N"], q=cell["q"], bj=cell["bj"], days=cell["days"], wins_per_day=cell["wpd"],
                     p_obs=cell["p_obs"], sigma_h=0.5, rng=rng)
    s = P.snap_from_arrays(sim["agent"], sim["label"], sim["day"], sim["win"], sim["S"], sim["coupled"], wins_per_day=cell["wpd"])
    d_obs, _ = P.plm_diag(s)
    nul = np.array([P.plm_diag(s.with_labels(P.null_labels(s, "perm", rng)))[0] for _ in range(9)])
    return dict(**cell, seed=seed, d_obs=d_obs, z=(d_obs - nul.mean()) / max(nul.std(ddof=1), 1e-9))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=40)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--only", default="S1,S2,S3,S4")
    a = ap.parse_args()
    OUTD.mkdir(parents=True, exist_ok=True)
    only = set(a.only.split(","))
    seed0 = 20261003
    with Pool(min(a.workers, 2)) as pool:
        if "S1" in only:
            cells = [dict(bj=bj, N=N, days=dw[0], wpd=dw[1], p_obs=po, sigma_h=sh, q=4)
                     for bj in (-4, -2, -1, 0, 1, 2, 4) for N in (7, 13) for dw in ((5, 9), (10, 8))
                     for po in (0.5, 0.75) for sh in (0.0, 1.0)]
            jobs = [(c, seed0 + 1000 * i + r) for i, c in enumerate(cells) for r in range(a.reps)]
            res = pool.map(one_rep, jobs, chunksize=8)
            pl.DataFrame(res).write_parquet(OUTD / "S1_power.parquet")
            print("S1 done", len(res))
        if "S2" in only:
            cells = ([dict(bj=0, N=10, days=5, wpd=9, p_obs=0.6, sigma_h=sh, q=4, drift=None, conf="specialization")
                      for sh in (0.0, 0.5, 1.0, 2.0)]
                     + [dict(bj=0, N=10, days=5, wpd=9, p_obs=0.6, sigma_h=0.0, q=4, drift=dr, conf="drift")
                        for dr in (0.5, 1.0, 2.0)])
            jobs = [(c, seed0 + 500000 + 1000 * i + r) for i, c in enumerate(cells) for r in range(a.reps)]
            res = pool.map(one_rep, jobs, chunksize=8)
            pl.DataFrame(res).with_columns(pl.col("drift").cast(pl.Float64)).write_parquet(OUTD / "S2_confounds.parquet")
            print("S2 done", len(res))
        if "S3" in only:
            cells = ([dict(kind="ramp", bj=bj, N=10, q=4, days=5, wpd=9, p_obs=0.7) for bj in (0.0, 2.0, 4.0, 6.0)]
                     + [dict(kind="step", bj=0.0, N=10, q=4, days=5, wpd=9, p_obs=0.7),
                        dict(kind="const", bj=0.0, N=10, q=4, days=5, wpd=9, p_obs=0.7),
                        dict(kind="const", bj=2.0, N=10, q=4, days=5, wpd=9, p_obs=0.7)])
            jobs = [(c, seed0 + 900000 + 1000 * i + r) for i, c in enumerate(cells) for r in range(a.reps * 2)]
            res = pool.map(jump_rep, jobs, chunksize=8)
            pl.DataFrame(res).write_parquet(OUTD / "S3_jumps.parquet")
            print("S3 done", len(res))
        if "S4" in only:
            cells = [dict(bj=bj, N=10, q=4, days=5, wpd=9, p_obs=0.7) for bj in (-3.0, 0.0, 3.0)]
            jobs = [(c, seed0 + 1500000 + 1000 * i + r) for i, c in enumerate(cells) for r in range(max(a.reps // 4, 6))]
            res = pool.map(plm_rep, jobs, chunksize=2)
            pl.DataFrame(res).write_parquet(OUTD / "S4_plm.parquet")
            print("S4 done", len(res))
    HC.write_provenance(OUTD, "hypotheses/H11-potts-labor-vs-herding/analysis/synthetic.py", [],
                        {"reps": a.reps, "n_null": N_NULL, "seed0": seed0, "note": "synthetic only, no dataset input"})


if __name__ == "__main__":
    main()
