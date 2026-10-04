"""H102 synthetic validation (axis F, card P0) on the real statement skeletons (agent, day, room of each statement)
and the real hopping read-outs of every unit.

Generator, per statement s of agent i on day d said in room r:
  x_s = a_i + mu_{home(i)} + shift_{i,d} (mu_other - mu_home) + gamma * 1[r != home] (mu_r - mu_home) + eps_s
  shift_{i,d} = kappa * log1p(R_hop_{i,d}) + phi * shift_{i,d-1}            (coupling; phi = 0.5 persistence)
  selection world: shift_{i,d} = kappa * log1p(R_hop_{i,d}), phi = 0          (content and hops co-occur, no carry)
  field world: shift_{i,d} = f_i constant for hoppers (their own field puts them between the domains), kappa = 0
  mixture world: gamma = 1, kappa = 0
a_i ~ N(0, tau^2 I), eps ~ N(0, sigma_s^2 I); |mu_B - mu_A|^2 = rho * 2 * 32 * tau^2.
sigma_s (statement noise) and tau (agent constant spread, H100's calibration value) are instrument calibrations.

Usage: uv run python hypotheses/H102-room-domain-walls/analysis/synthetic.py [--reps 40]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h102lib as L  # noqa: E402

TAU2 = 0.0014  # agent-constant variance per coordinate (H100 synthetic calibration, agent-day means, bge style_resid)


def calibrate(st, Xc):
    key = (st["agent"].cast(pl.String) + "|" + st["pt_date"]).to_numpy()
    v = []
    for k in np.unique(key)[:3000]:
        m = key == k
        if m.sum() >= 5:
            v.append(Xc[m].var(0, ddof=1).mean())
    return float(np.median(v))


def gen(st, dom, rd, unit, world, rho, kappa, sig2, rng, gamma=0.0):
    sub = st.filter(pl.col("unit") == unit)
    d = dom.filter(pl.col("unit") == unit)
    home = dict(zip(d["agent"].to_list(), d["home"].to_list()))
    role = dict(zip(d["agent"].to_list(), d["role"].to_list()))
    A, B = L.rooms_of(dom, unit)
    dim = 32
    v = rng.standard_normal(dim); v /= np.linalg.norm(v)
    sep = np.sqrt(rho * 2 * dim * TAU2)
    mu = {A: np.zeros(dim), B: sep * v}
    for r in sub["room_at"].drop_nulls().unique().to_list():
        mu.setdefault(r, rng.normal(0, np.sqrt(TAU2), dim))
    a = {k: rng.normal(0, np.sqrt(TAU2), dim) for k in home}
    rdd = {(x["agent"], x["pt_date"]): x["R_hop"] for x in rd.filter(pl.col("unit") == unit).to_dicts()}
    days = sorted(sub["pt_date"].unique().to_list())
    shift = {}
    for k in home:
        prev = 0.0
        fk = rng.uniform(0.2, 0.6) if (world == "field" and role[k] == "hopper") else 0.0
        for dd in days:
            R = np.log1p(rdd.get((k, dd), 0))
            if world == "coupling":
                s = kappa * R + 0.5 * prev
            elif world == "selection":
                s = kappa * R
            elif world == "field":
                s = fk
            else:
                s = 0.0
            shift[(k, dd)] = s; prev = s
    g = gamma if world == "mixture" else 0.0
    X = np.empty((sub.height, dim))
    for i, (k, dd, r) in enumerate(zip(sub["agent"].to_list(), sub["pt_date"].to_list(), sub["room_at"].to_list())):
        h = home[k]; o = B if h == A else A
        x = a[k] + mu[h] + shift[(k, dd)] * (mu[o] - mu[h])
        if r is not None and r != h and r in mu:
            x = x + g * (mu[r] - mu[h])
        X[i] = x + rng.normal(0, np.sqrt(sig2), dim)
    return sub, X


def run(reps):
    st, Xc, dom, rd = L.load()
    sig2 = calibrate(st, Xc)
    rng = np.random.default_rng(20261004)
    out = {"sigma_s2": sig2, "tau2": TAU2, "reps": reps, "bimodality": {}, "hoppers": {}}
    # (1) bimodality size and power on the fixed-room units
    for rho in (0.0, 0.3, 1.0):
        rej, Ds = [], []
        for r in range(reps):
            for u in ["G35", "G37", "G38", "G39", "G41", "G42", "G44"]:
                sub, X = gen(st, dom, rd, u, "none", rho, 0, sig2, rng)
                Xd = L.day_center(sub, X)
                fr = sub.with_columns(pl.Series("ix", np.arange(sub.height))).join(
                    dom.filter(pl.col("unit") == u).select("agent", "home", "role"), on="agent", how="left")
                ah = L.agent_halves(fr, Xd)
                A, B = L.rooms_of(dom, u)
                t = L.bimodality_test(ah, A, B, n_null=100, seed=r)
                if t:
                    rej.append(t["p"] < 0.05 and t["D"] >= 2); Ds.append(t["D"])
        out["bimodality"][f"rho{rho}"] = {"rej_rate(D>=2 & p<0.05)": float(np.mean(rej)), "D_med": float(np.median(Ds)),
                                          "D_q10_q90": [float(np.percentile(Ds, 10)), float(np.percentile(Ds, 90))]}
        print("bimodality", rho, out["bimodality"][f"rho{rho}"], flush=True)
    # (2) hopper worlds on 51g
    for world, kappa in [("none", 0.0), ("coupling", 0.1), ("coupling", 0.3), ("selection", 0.3), ("field", 0.0),
                         ("mixture", 0.0)]:
        rec = {"kR": [], "kU": [], "p_R": [], "kR_lag": [], "s_all": [], "s_home": [], "stay_p95": []}
        for r in range(reps):
            sub, X = gen(st, dom, rd, "51g", world, 1.0, kappa, sig2, rng, gamma=1.0)
            Xd = L.day_center(sub, X)
            fr = sub.with_columns(pl.Series("ix", np.arange(sub.height))).join(
                dom.filter(pl.col("unit") == "51g").select("agent", "home", "role"), on="agent", how="left")
            ah = L.agent_halves(fr, Xd)
            hp = L.hopper_positions(fr, Xd, ah, L.GENERAL, L.FOCUS)
            dr = L.dose_response(hp, rd, "51g", n_boot=200, seed=r)
            dl = L.dose_response(hp, rd, "51g", n_boot=50, seed=r, lag=True)
            if "kappa_R" in dr:
                rec["kR"].append(dr["kappa_R"]); rec["kU"].append(dr["kappa_U"]); rec["p_R"].append(dr["p_R_day"])
            if "kappa_R" in dl:
                rec["kR_lag"].append(dl["kappa_R"])
            for k, h in hp["hoppers"].items():
                if h["n_other"] >= 5:
                    rec["s_all"].append(h["s_all"]); rec["s_home"].append(h["s_home"])
            rec["stay_p95"].append(hp["home_stayers_p95"])
        s = {k: (float(np.nanmedian(v)) if len(v) else None) for k, v in rec.items() if k != "p_R"}
        s["power_kR_p05"] = float(np.mean(np.array(rec["p_R"]) < 0.05)) if rec["p_R"] else None
        out["hoppers"][f"{world}_k{kappa}"] = s
        print("hoppers", world, kappa, s, flush=True)
    (L.DATA / "synthetic").mkdir(exist_ok=True)
    (L.DATA / "synthetic/synthetic_summary.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=30)
    run(ap.parse_args().reps)
