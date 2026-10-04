"""H107 synthetic validation (card P0, axis F) on the real statement skeletons of the eligible periods (non-holdout).

Generator, per statement s of agent i on day k at active time t (days since the period's first regime-consistent day;
t = k + min((win30 + 0.5)/8, 1)):
    x_s = a_i + eta_{i,k} + sgn(room_{i,k}) (beta g(t) / 2) u(t) + eps_s
  a_i ~ N(0, tau2 I)  (leftover agent constants: the full H100 constant variance, as if a_i were not removed)
  eta ~ N(0, s_eta2 I) agent-day deviation; eps ~ N(0, s_eps2 I) statement noise (calibrated on real statements:
  instrument calibration, no room statistic)
  beta = sqrt(rho * 64 * tau2) (H100's room-effect size rho = |D|^2 / E|a_i - a_j|^2)
Worlds: null; step (g = 1, fixed u; rho 0.3, 1); slow SSB (g = 1 - exp(-t / tau_g), tau_g 1, 2 days; u diffuses on the
half-day grid with D_j = D0 / (g_j^2 + 0.05), D0 = 0.02/62 per dimension, i.e. a total
angular variance of 0.02 rad^2 per half-day once saturated and 0.4 early: nucleation then coarsening); fast instability (tau_g 0.25 day,
about 1 active hour). The analysis runs without agent constants (consts=None).
Repo-field rule: in null and step worlds, f_repo is computed along the planted u (power) and along an independent random
unit vector (size).

Usage: uv run python hypotheses/H107-room-split-onset/analysis/synthetic.py [--reps 40]
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
import h107lib as L  # noqa: E402
import rslib as R  # noqa: E402

OUTD = L.DATA / "synthetic"
TAU2 = 0.0014  # H100 agent-constant variance per coordinate (constants panel)
D0 = 0.02 / 62  # per-dimension: total angular variance per half-day step 2*D*(n-1) = 0.02 at saturation, 0.4 early


def calibrate(st, V) -> dict:
    """Statement noise and agent-day deviation variances per coordinate (regime III, #36-#44, non-holdout)."""
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
    s_eta2 = float(max(np.median(between), 1e-6))
    return {"s_eps2": s_eps2, "s_eta2": s_eta2, "tau2": TAU2, "median_statements_per_agent_day": float(np.median(n_s))}


def unit(v):
    return v / np.linalg.norm(v)


def gen_period(st, P, cal, world, rho, rng, tau_g=None):
    sp = R.period_statements(st, P)
    days = sorted(sp["pt_date"].unique().to_list())
    kday = {d: k for k, d in enumerate(days)}
    d = 32
    beta = np.sqrt(rho * 64 * cal["tau2"])
    u0 = unit(rng.standard_normal(d))
    nj = 2 * len(days)
    U = np.zeros((nj, d)); U[0] = u0
    for j in range(1, nj):
        if world in ("slow", "fast"):
            tj = j / 2 + 0.25
            gj = 1 - np.exp(-tj / tau_g)
            Dj = D0 / (gj ** 2 + 0.05)
            xi = rng.standard_normal(d); xi -= (xi @ U[j - 1]) * U[j - 1]
            U[j] = unit(U[j - 1] + np.sqrt(2 * Dj) * xi)
        else:
            U[j] = u0
    agents = sp["agent"].unique().to_list()
    a = {x: rng.normal(0, np.sqrt(cal["tau2"]), d) for x in agents}
    eta = {}
    ag = sp["agent"].to_numpy(); dd = sp["pt_date"].to_list(); w30 = sp["win30"].to_numpy()
    rm = sp["room_day"].to_numpy(); half = sp["half"].to_numpy()
    X = np.empty((sp.height, d))
    for i in range(sp.height):
        key = (ag[i], dd[i])
        if key not in eta:
            eta[key] = rng.normal(0, np.sqrt(cal["s_eta2"]), d)
        k = kday[dd[i]]
        t = k + min((w30[i] + 0.5) / 8, 1.0)
        if world == "null":
            g = 0.0
        elif world == "step":
            g = 1.0
        else:
            g = 1 - np.exp(-t / tau_g)
        sg = 1.0 if rm[i] == R.BEST else (-1.0 if rm[i] == R.REST else 0.0)
        j = min(2 * k + int(half[i]), nj - 1)
        X[i] = a[ag[i]] + eta[key] + sg * (beta * g / 2) * U[j] + rng.normal(0, np.sqrt(cal["s_eps2"]), d)
    return sp["srow"].to_numpy(), X, u0


def run(reps: int, n_perm: int = 300):
    st = L.load_inputs()
    V = R.load_vectors("bge_small", "style_resid")
    cal = calibrate(st, V)
    print("calibration", cal, flush=True)
    Vs = np.zeros(V.shape, dtype=np.float64)
    periods = [P for P in R.PERIODS if P != 36]
    worlds = [("null", 0.0, None), ("step", 0.3, None), ("step", 1.0, None), ("slow", 1.0, 1.0), ("slow", 1.0, 2.0),
              ("fast", 1.0, 0.25)]
    rng = np.random.default_rng(20261004)
    out = {"calibration": cal, "reps": reps, "n_perm": n_perm, "worlds": {}}
    t0 = time.time()
    for world, rho, tg in worlds:
        key = f"{world}_rho{rho}" + (f"_tau{tg}" if tg else "")
        rec = {P: [] for P in periods}
        for r in range(reps):
            for P in periods:
                rows, X, u0 = gen_period(st, P, cal, world, rho, rng, tg)
                Vs[rows] = X
                pd_ = R.build_panel(st, Vs, P, "day", None, halves=True)
                ph = R.build_panel(st, Vs, P, "half", None)
                o = L.onset(pd_, ph, n_perm=n_perm, seed=r)
                rec_r = {k: o.get(k) for k in ("r1", "pi1", "c1", "c1_raw", "p_F", "p1", "r_h0", "pi_h0",
                                               "kill_onset", "ssb_onset", "ssb_onset_growth", "monotone")}
                if world in ("null", "step"):
                    fa = L.field_alignment(pd_, u0, n_null=500, seed=r)
                    fr = L.field_alignment(pd_, unit(rng.standard_normal(32)), n_null=500, seed=r + 7)
                    rec_r.update(repo_pow_period=fa["rule_period"], repo_pow_day1=fa["rule_day1"],
                                 repo_size_period=fr["rule_period"], repo_size_day1=fr["rule_day1"],
                                 f_period=fa.get("f_period"))
                rec[P].append(rec_r)
        summ = {}
        for P in periods + ["all"]:
            rr = [x for p in periods for x in rec[p]] if P == "all" else rec[P]
            f = lambda k: np.array([np.nan if x.get(k) is None else float(x[k]) for x in rr])  # noqa: E731
            s = {"rej_F": float(np.nanmean(f("p_F") < 0.05)), "rej_E1": float(np.nanmean(f("p1") < 0.05)),
                 "kill": float(np.nanmean(f("kill_onset"))), "ssb": float(np.nanmean(f("ssb_onset"))),
                 "ssb_growth": float(np.nanmean(f("ssb_onset_growth"))),
                 "pi1_ge06": float(np.nanmean(f("pi1") >= 0.6)), "r1_med": float(np.nanmedian(f("r1"))),
                 "pi1_med": float(np.nanmedian(f("pi1"))), "c1_med": float(np.nanmedian(f("c1_raw"))),
                 "r_h0_med": float(np.nanmedian(f("r_h0"))), "r_h0_le03": float(np.nanmean(f("r_h0") <= 0.3)),
                 "pi_h0_med": float(np.nanmedian(f("pi_h0")))}
            if world in ("null", "step"):
                for k in ("repo_pow_period", "repo_pow_day1", "repo_size_period", "repo_size_day1"):
                    s[k] = float(np.nanmean(f(k)))
            summ[str(P)] = s
        out["worlds"][key] = summ
        print(key, json.dumps({k: round(v, 3) for k, v in summ["all"].items()}), f"{time.time() - t0:.0f}s", flush=True)
    OUTD.mkdir(parents=True, exist_ok=True)
    (OUTD / "synthetic_summary.json").write_text(json.dumps(out, indent=1))
    return out


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=40)
    ap.add_argument("--perm", type=int, default=300)
    a = ap.parse_args()
    run(a.reps, a.perm)
