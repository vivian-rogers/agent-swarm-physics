"""H108 synthetic validation (card P0, axis F) on the real statement skeletons of the eligible periods (non-holdout).

Generator, per statement s of agent i on day k:  x_s = a_i + eta_{i,k} + sgn(room_{i,k}) (beta / 2) u_k + eps_s
  a_i ~ N(0, tau2 I) leftover agent constants (full H100 variance; conservative), eta ~ N(0, s_eta2 I), eps ~ N(0, s_eps2 I)
  (statement and agent-day noise calibrated on real statements: instrument calibration, no room statistic; the
  calibration routine is a copy of H107's), beta = sqrt(rho * 64 * tau2).
Direction u_k: pinned (u_k = u_0); Goldstone with planted lag-1 cosine c (u_{k+1} = c u_k + sqrt(1 - c^2) v_perp,
v_perp a random unit vector orthogonal to u_k); regenerating (c = 0); null (beta = 0).
Contrast worlds are assembled from independent per-period runs: identical periods Goldstone (c = 0.5) and fielded
periods pinned (A: the HH's prediction); all pinned (B); all Goldstone c = 0.5 (C).

Usage: uv run python hypotheses/H108-goldstone-room-wandering/analysis/synthetic.py [--reps 30 --boot 100]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h108lib as L  # noqa: E402
import rslib as R  # noqa: E402

OUTD = L.DATA / "synthetic"
TAU2 = 0.0014


def calibrate(st, V) -> dict:
    s = st.filter(pl.col("goal_no").is_in([36, 37, 38, 39, 41, 42, 44]) & (pl.col("regime") == "III"))
    g = s.group_by("goal_no", "agent", "pt_date").agg(pl.col("srow"))
    within, n_s = [], []
    for rows in g["srow"].to_list():
        if len(rows) >= 5:
            X = np.asarray(V[np.array(rows)], dtype=np.float64)
            within.append(X.var(0, ddof=1).mean()); n_s.append(len(rows))
    s_eps2 = float(np.median(within))
    ad, Xc = R.day_centered_agent_days(s, V, [36, 37, 38, 39, 41, 42, 44])
    ad = ad.with_columns(pl.Series("ix", np.arange(ad.height)))
    between = []
    for _, gg in ad.group_by("goal_no", "agent"):
        if gg.height >= 3:
            ix = gg["ix"].to_numpy()
            between.append(Xc[ix].var(0, ddof=1).mean() - s_eps2 / gg["n"].mean())
    return {"s_eps2": s_eps2, "s_eta2": float(max(np.median(between), 1e-6)), "tau2": TAU2}


def unit(v):
    return v / np.linalg.norm(v)


def gen_period(st, P, cal, c, rho, rng):
    """c: None = pinned; float = planted lag-1 cosine. rho = 0 gives the null."""
    sp = R.period_statements(st, P)
    days = sorted(sp["pt_date"].unique().to_list()); kday = {d: k for k, d in enumerate(days)}
    d = 32
    beta = np.sqrt(rho * 64 * cal["tau2"])
    U = np.zeros((len(days), d)); U[0] = unit(rng.standard_normal(d))
    for k in range(1, len(days)):
        if c is None:
            U[k] = U[0]
        else:
            v = rng.standard_normal(d); v -= (v @ U[k - 1]) * U[k - 1]; v = unit(v)
            U[k] = unit(c * U[k - 1] + np.sqrt(max(1 - c * c, 0)) * v)
    agents = sp["agent"].unique().to_list()
    a = {x: rng.normal(0, np.sqrt(cal["tau2"]), d) for x in agents}
    ag = sp["agent"].to_numpy(); dd = sp["pt_date"].to_list(); rm = sp["room_day"].to_numpy()
    eta = {}
    X = np.empty((sp.height, d))
    for i in range(sp.height):
        key = (ag[i], dd[i])
        if key not in eta:
            eta[key] = rng.normal(0, np.sqrt(cal["s_eta2"]), d)
        sg = 1.0 if rm[i] == R.BEST else (-1.0 if rm[i] == R.REST else 0.0)
        X[i] = a[ag[i]] + eta[key] + sg * (beta / 2) * U[kday[dd[i]]] + rng.normal(0, np.sqrt(cal["s_eps2"]), d)
    return sp["srow"].to_numpy(), X


def ratio_stats(id_s, f_s, id_b, f_b):
    """R_D = D_id / D_f from pooled sums, and its bootstrap 95% CI from per-period bootstrap replicates."""
    Did = L.D_of(L.pooled_P(id_s)); Df = L.D_of(L.pooled_P(f_s))
    RD = Did / Df if (np.isfinite(Did) and np.isfinite(Df) and Df > 0) else (np.inf if Did > 0 and Df == 0 else np.nan)
    nb = min(len(b) for b in id_b + f_b)
    rr = []
    for j in range(nb):
        di = L.D_of(L.pooled_P([b[j] for b in id_b])); df = L.D_of(L.pooled_P([b[j] for b in f_b]))
        if df == 0 and di > 0:
            rr.append(np.inf)
        elif df > 0 and np.isfinite(df):
            rr.append(di / df)
    rr = np.array(rr, dtype=float)
    lo = float(np.percentile(rr, 2.5)) if len(rr) >= 20 else np.nan
    return RD, lo


def run(reps: int, n_boot: int, n_perm: int = 300):
    st = L.load_inputs()
    V = R.load_vectors("bge_small", "style_resid")
    cal = calibrate(st, V)
    print("calibration", cal, flush=True)
    Vs = np.zeros(V.shape, dtype=np.float64)
    periods = R.PERIODS
    rng = np.random.default_rng(20261005)
    single = [("null", None, 0.0), ("pinned", None, 0.3), ("pinned", None, 1.0), ("gold", 0.3, 1.0),
              ("gold", 0.5, 1.0), ("gold", 0.6, 1.0), ("gold", 0.9, 1.0),
              ("regen", 0.0, 1.0)]
    out = {"calibration": cal, "reps": reps, "boot": n_boot, "single": {}, "contrast": {}}
    t0 = time.time()
    store = {}
    for name, c, rho in single:
        key = f"{name}_c{c}_rho{rho}"
        rec = {P: [] for P in periods}
        for r in range(reps):
            for P in periods:
                rows, X = gen_period(st, P, cal, c, rho, rng)
                Vs[rows] = X
                pan = R.build_panel(st, Vs, P, "day", None, halves=True)
                s = L.sums(pan, n_perm=n_perm, seed=r)
                do_boot = key in ("pinned_cNone_rho1.0", "gold_c0.5_rho1.0") and n_boot > 0
                if do_boot:
                    s["boot"] = L.boot_sums(pan, n_boot, 100, seed=r)
                rec[P].append(s)
        store[key] = rec
        summ = {}
        for P in periods:
            P1 = np.array([L.P_from(s) for s in rec[P]]); Psh = np.array([L.P_from(s, key="sh") for s in rec[P]])
            pp = np.array([s.get("persist_p", np.nan) for s in rec[P]])
            summ[str(P)] = {"P1_med": float(np.nanmedian(P1)), "P1_q10_q90": [float(np.nanpercentile(P1, 10)),
                                                                                float(np.nanpercentile(P1, 90))],
                            "Psh_med": float(np.nanmedian(Psh)), "persist_rej": float(np.nanmean(pp < 0.05))}
        pid = [L.pooled_P([rec[P][r] for P in R.IDENTICAL]) for r in range(reps)]
        pf = [L.pooled_P([rec[P][r] for P in R.FIELDED]) for r in range(reps)]
        summ["pooled_identical_P1_med"] = float(np.nanmedian(pid)); summ["pooled_fielded_P1_med"] = float(np.nanmedian(pf))
        # scaling check (O4): Spearman of D vs 1/(N_eff E_mean) over identical periods
        rhos = []
        for r in range(reps):
            Dv = [L.D_of(L.P_from(rec[P][r])) for P in R.IDENTICAL]
            xv = [1 / (rec[P][r]["N_eff"] * rec[P][r]["E_mean"]) if rec[P][r]["E_mean"] > 0 else np.nan for P in R.IDENTICAL]
            ok = [i for i in range(len(Dv)) if np.isfinite(xv[i]) and not np.isnan(Dv[i])]
            if len(ok) >= 4:
                a = np.array([min(Dv[i], 50) for i in ok]); b = np.array([xv[i] for i in ok])
                rk = lambda v: np.argsort(np.argsort(v))  # noqa: E731
                rhos.append(np.corrcoef(rk(a), rk(b))[0, 1])
        summ["scaling_abs_rho_lt09"] = float(np.mean(np.abs(rhos) < 0.9)) if rhos else None
        summ["scaling_rho_med"] = float(np.median(rhos)) if rhos else None
        out["single"][key] = summ
        print(key, json.dumps({P: (round(v["P1_med"], 2), round(v["Psh_med"], 2), round(v["persist_rej"], 2))
                               for P, v in summ.items() if isinstance(v, dict)}),
              round(summ["pooled_identical_P1_med"], 2), round(summ["pooled_fielded_P1_med"], 2),
              f"{time.time() - t0:.0f}s", flush=True)
    # contrast worlds (need bootstrap replicates: pinned rho 1 and gold c 0.5)
    if n_boot > 0:
        pin, gold = store["pinned_cNone_rho1.0"], store["gold_c0.5_rho1.0"]
        for cname, idw, fw in (("A_id_gold_f_pinned", gold, pin), ("B_all_pinned", pin, pin), ("C_all_gold", gold, gold)):
            passes, RDs = [], []
            for r in range(reps):
                ids = [idw[P][r] for P in R.IDENTICAL]; fs = [fw[P][r] for P in R.FIELDED]
                RD, lo = ratio_stats(ids, fs, [s["boot"] for s in ids], [s["boot"] for s in fs])
                RDs.append(RD); passes.append(bool(RD >= 2 and np.isfinite(lo) and lo > 1))
            out["contrast"][cname] = {"pass_rate": float(np.mean(passes)), "RD_med": float(np.nanmedian(RDs))}
            print(cname, out["contrast"][cname], flush=True)
    OUTD.mkdir(parents=True, exist_ok=True)
    (OUTD / "synthetic_summary.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=30)
    ap.add_argument("--boot", type=int, default=100)
    ap.add_argument("--perm", type=int, default=300)
    a = ap.parse_args()
    run(a.reps, a.boot, a.perm)
