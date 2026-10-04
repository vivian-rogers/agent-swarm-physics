"""H109 synthetic validation (axis F) on the real skeleton: real statements (agents, times, rooms, producing calls,
reset segments, boundaries, ledger reads), synthetic vectors.

  x_t = a_i + 1[scoped] sigma_r m_P g_t u_P + eps_t,  eps ~ N(0, Sigma_res)
  a_i ~ N(0, tau2 I) with tau2 = 0.0014 (H100 calibration); Sigma_res = covariance of the real day-centred,
  agent-goal-demeaned statement vectors (an instrument, not an outcome); m_P = sqrt(S_spont_P)/2 from H100's
  per-period room separation (bge; 51g gets the median); u_P a random unit direction per period.

Worlds (g_t from the statement's rank k in its reset segment and the room items R read since the segment start):
  null     g = 1
  drop30   g = 0.7 for k <= 3, then 1 - 0.3 exp(-(R - R_3)/5)            (HH339's 30% drop, recovery by reading)
  drop50   as drop30 with 0.5
  read30   g = 1 - 0.6 exp(-R/15)    (drop set by reads only; noise-free estimand delta_F = 0.29 pooled, A1)
  read50   g = 1 - 0.8 exp(-R/15)    (estimand 0.48)
  noise    g = 1; statements with k <= 3 get noise x sqrt(1.5)            (size check)
  ramp     g = 0.7 + 0.3 min(k/10, 1)                                    (context build-up)
  drive    g = 1 + 0.5 sin(2 pi t / 3 d), common to all agents           (size check: slow common drive)
Usage: uv run python hypotheses/H109-erasure-demagnetizing-pulse/analysis/synthetic.py [--reps 30]
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
sys.path.insert(0, str(HERE.parent / "scheme"))
import h109lib as L  # noqa: E402
import build as B  # noqa: E402

OUT = L.D / "synthetic"
H100RAW = L.ROOT / "data/processed/H100-room-symmetry-breaking/results/raw_bge_small_style_resid.json"
TAU2 = 0.0014
WORLDS = ["null", "drop30", "drop50", "read30", "read50", "noise", "ramp", "drive"]


def skeleton():
    st, b, r = L.load_tables()
    ct = B.ledger_counters()
    first = ct.sort("agent", "t_call", "turn_id").group_by("agent", "seg").agg(
        (pl.col("cum_items").first() - pl.col("n_agent").first().cast(pl.Int64)).alias("cum_before"))
    st2 = st.join(first, on=["agent", "seg"], how="left")
    R = (st2["cum_items"] - st2["cum_before"]).fill_null(0).to_numpy().astype(float)
    # rank within segment (all statements of the agent in that segment, chronological)
    k = st.with_columns(pl.int_range(1, pl.len() + 1).over("agent", "seg").alias("kseg"))["kseg"].to_numpy()
    R3 = st.with_columns(pl.Series("R", R)).with_columns(pl.int_range(1, pl.len() + 1).over("agent", "seg").alias("k")) \
        .with_columns(pl.col("R").filter(pl.col("k") <= 3).max().over("agent", "seg").alias("R3"))["R3"].fill_null(0).to_numpy()
    return st, b, r, R, k, R3


def calibration(st, model):
    X = L.load_X(st, model)
    Xc = L.day_center(st, X)
    key = st["agent"].cast(pl.Int64).to_numpy() * 1000 + st["goal_no"].cast(pl.Int64).to_numpy()
    uk, inv = np.unique(key, return_inverse=True)
    M = np.zeros((len(uk), 32))
    np.add.at(M, inv, Xc)
    M /= np.bincount(inv)[:, None]
    E = Xc - M[inv]
    S = np.cov(E.T)
    raw = json.loads(H100RAW.read_text())["periods"]
    m = {int(k[1:]): float(np.sqrt(max(v.get("S_spont") or v["S"], 1e-6)) / 2) for k, v in raw.items()}
    med = float(np.median([m[p] for p in L.PERIODS if p in m]))
    mP = {p: m.get(p, med) for p in L.PERIODS}
    return S, mP


def gen(st, R, k, R3, S, mP, world, rng):
    n = st.height
    ag = st["agent"].to_numpy().astype(int)
    gl = st["goal_no"].to_numpy().astype(int)
    sig = st["sigma"].to_numpy().astype(float)
    sc = st["scoped"].to_numpy()
    Lc = np.linalg.cholesky(S + 1e-9 * np.eye(32))
    eps = rng.standard_normal((n, 32)) @ Lc.T
    if world == "noise":
        eps[k <= 3] *= np.sqrt(1.5)
    ua = np.unique(ag)
    a = {u: rng.standard_normal(32) * np.sqrt(TAU2) for u in ua}
    X = eps + np.array([a[u] for u in ag])
    g = np.ones(n)
    if world in ("drop30", "drop50"):
        d0 = 0.3 if world == "drop30" else 0.5
        g = np.where(k <= 3, 1 - d0, 1 - d0 * np.exp(-np.maximum(R - R3, 0) / 5.0))
    elif world in ("read30", "read50"):
        g = 1 - (0.6 if world == "read30" else 0.8) * np.exp(-R / 15.0)
    elif world == "ramp":
        g = 0.7 + 0.3 * np.minimum(k / 10.0, 1.0)
    elif world == "drive":
        tt = st["t"].dt.epoch("s").to_numpy().astype(float)
        g = 1 + 0.5 * np.sin(2 * np.pi * tt / (3 * 86400.0))
    for P in L.PERIODS:
        u = L.unit(rng.standard_normal(32))
        ix = np.where(sc & (gl == P))[0]
        X[ix] += (sig[ix] * mP[P] * g[ix])[:, None] * u[None, :]
    return X


def g_of(st, R, k, R3, world):
    n = st.height
    if world in ("drop30", "drop50"):
        d0 = 0.3 if world == "drop30" else 0.5
        return np.where(k <= 3, 1 - d0, 1 - d0 * np.exp(-np.maximum(R - R3, 0) / 5.0))
    if world in ("read30", "read50"):
        return 1 - (0.6 if world == "read30" else 0.8) * np.exp(-R / 15.0)
    if world == "ramp":
        return 0.7 + 0.3 * np.minimum(k / 10.0, 1.0)
    return np.ones(n)


def estimand(st, b, g):
    """Noise-free value of the drop estimator (alignment proportional to g)."""
    val = np.where(st["scoped"].to_numpy(), g, np.nan)
    ev = L.event_table(b, st, val, "restate")
    out = {}
    for P in L.PERIODS:
        e = ev.filter(pl.col("period") == P)
        out[P] = float(L._delta_core(e["label"].to_numpy(), e["D"].to_numpy(), e["pre"].to_numpy(),
                                     e["stratum"].to_numpy(), np.ones(e.height))[2])
    out["all"] = float(L._delta_core(ev["label"].to_numpy(), ev["D"].to_numpy(), ev["pre"].to_numpy(),
                                     ev["stratum"].to_numpy(), np.ones(ev.height))[2])
    return out


def run_one(st, b, r, X, F, nboot=200, seed=0, with_recovery=False, rec_boot=100):
    Xc = L.day_center(st, X)
    A = L.agent_constants(st, Xc)
    a, _, _ = L.axes_and_alignment(st, Xc, X, A, F, project_fields=False)
    ev = L.event_table(b, st, a, "restate")
    out = {}
    for P in L.PERIODS:
        out[P] = L.delta(ev.filter(pl.col("period") == P), "F", nboot=nboot, seed=seed)
    out["pooled_re"] = L.re_meta([out[P].get("delta", np.nan) for P in L.PERIODS],
                                 [out[P].get("delta_se", np.nan) for P in L.PERIODS])
    if with_recovery:
        out["recovery"] = L.recovery(b, r, st, a, "restate", nboot=rec_boot, seed=seed)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=30)
    ap.add_argument("--model", default="bge_small")
    ap.add_argument("--worlds", default=",".join(WORLDS))
    ap.add_argument("--rec-reps", type=int, default=10)
    ap.add_argument("--rec-boot", type=int, default=100)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    st, b, r, R, k, R3 = skeleton()
    S, mP = calibration(st, a.model)
    F = L.field_dirs(a.model)
    worlds = a.worlds.split(",")
    res = {w: [] for w in worlds}
    t0 = time.time()
    for w in worlds:
        for rep in range(a.reps):
            rng = np.random.default_rng(1000 * WORLDS.index(w) + rep)
            X = gen(st, R, k, R3, S, mP, w, rng)
            o = run_one(st, b, r, X, F, seed=rep, with_recovery=(rep < a.rec_reps), rec_boot=a.rec_boot)
            res[w].append(o)
        print(w, f"{time.time() - t0:.0f}s", flush=True)
    summ = {"m_P": mP, "tau2": TAU2, "reps": a.reps, "model": a.model, "worlds": {}}
    for w in worlds:
        per = {}
        for P in L.PERIODS:
            d = [o[P] for o in res[w] if o[P].get("n", 0) > 0]
            dl = np.array([x["delta"] for x in d])
            lo = np.array([x["delta_ci"][0] for x in d])
            hi = np.array([x["delta_ci"][1] for x in d])
            ident = np.array([x["A_pre_ci"][0] > 0 for x in d])
            per[P] = {"delta_med": float(np.nanmedian(dl)), "reject_pos": float(np.nanmean(lo > 0)),
                      "reject_neg": float(np.nanmean(hi < 0)), "kill_fires": float(np.nanmean(hi < 0.3)),
                      "identified": float(ident.mean()), "coverage_med": float(np.median([x["coverage"] for x in d])),
                      "n_F": int(np.median([x["n"] for x in d]))}
        pr = [o["pooled_re"] for o in res[w] if "mu" in o["pooled_re"]]
        pooled = {"mu_med": float(np.median([p["mu"] for p in pr])),
                  "reject_pos": float(np.mean([p["ci"][0] > 0 for p in pr])),
                  "kill_fires": float(np.mean([p["ci"][1] < 0.3 for p in pr])),
                  "hh_pass": float(np.mean([(p["mu"] >= 0.3) and (p["ci"][0] > 0) for p in pr]))}
        rec = [o["recovery"] for o in res[w] if "recovery" in o and "kR" in o["recovery"]]
        recs = {"kR_med": float(np.median([x["kR"] for x in rec])) if rec else None,
                "kR_pos": float(np.mean([x["kR_ci"][0] > 0 for x in rec])) if rec else None,
                "kU_med": float(np.median([x["kU"] for x in rec])) if rec else None,
                "kRkU_pos": float(np.mean([x["kR_minus_kU_ci"][0] > 0 for x in rec])) if rec else None,
                "kR_q95": float(np.percentile([x["kR"] for x in rec], 95)) if rec else None,
                "kRkU_q95": float(np.percentile([x["kR_minus_kU"] for x in rec], 95)) if rec else None,
                "kR_all": [x["kR"] for x in rec], "kRkU_all": [x["kR_minus_kU"] for x in rec]}
        summ["worlds"][w] = {"periods": per, "pooled": pooled, "recovery": recs,
                             "estimand": estimand(st, b, g_of(st, R, k, R3, w))}
    (OUT / f"synthetic_summary_{a.model}{a.tag}.json").write_text(json.dumps(summ, indent=1, default=float))
    for w in worlds:
        s = summ["worlds"][w]
        print(w, "pooled", s["pooled"], "recovery", s["recovery"])
        print("   per-period reject_pos", {P: round(s["periods"][P]["reject_pos"], 2) for P in L.PERIODS})


if __name__ == "__main__":
    main()
