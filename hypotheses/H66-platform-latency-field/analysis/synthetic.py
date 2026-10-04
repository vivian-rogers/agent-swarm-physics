"""H66 synthetic validation (axis F): minute-level swarms at the skeleton of real units, run through the same
estimator as the real data (h66lib.analyze_grid).

Worlds (card, "Synthetic validation"):
  W0  independent agents, no field
  W1  latency field present in the measured turnaround only (activity independent of it)
  W1b latency field also slows calls (mechanical: a call > 60 s leaves an empty minute)
  W2  W1b + the field raises the pause hazard (weak latency loading, rho_lat ~ 0.05)
  W2s W2 with a strong latency loading
  W3  room coupling only (talk raises room-mates' pause-exit hazard next minute); field measured, not acting
  W4  W2 + W3
  W5  provider (lab) fields only, acting like W2 within each lab
Truth: f_true = 1 - E(field switched off in the dynamics, same seed) / E(world).
Run: OMP_NUM_THREADS=1 uv run python hypotheses/H66-platform-latency-field/analysis/synthetic.py [--seeds 8] [--workers 2]
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import argparse  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from concurrent.futures import ProcessPoolExecutor  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h66lib as L  # noqa: E402

ROOT = HERE.parents[2]
OUT = ROOT / "data/processed/H66-platform-latency-field"

WORLDS = {
    "W0": dict(beta=0.0, mech=False, gamma=0.0, kappa=0.0, lab=0.0),
    "W1": dict(beta=0.1, mech=False, gamma=0.0, kappa=0.0, lab=0.0),
    "W1b": dict(beta=0.1, mech=True, gamma=0.0, kappa=0.0, lab=0.0),
    "W2": dict(beta=0.1, mech=True, gamma=0.8, kappa=0.0, lab=0.0),
    "W2s": dict(beta=0.5, mech=True, gamma=0.8, kappa=0.0, lab=0.0),
    "W3": dict(beta=0.1, mech=False, gamma=0.0, kappa=1.5, lab=0.0),
    "W4": dict(beta=0.1, mech=True, gamma=0.8, kappa=1.5, lab=0.0),
    "W5": dict(beta=0.0, mech=True, gamma=0.8, kappa=0.0, lab=0.15),
    # post hoc (after the real-data sign check): congestion; latency rises with the number of active agents, plus a
    # slow common drive on activity (so there is co-activation to absorb); no latency action on activity
    "W6": dict(beta=0.0, mech=False, gamma=0.0, kappa=0.0, lab=0.0, cong=0.15, drive=0.8),
}


def ou(T, tau, rng):
    x = np.zeros(T)
    a = np.exp(-1 / tau)
    s = np.sqrt(1 - a * a)
    x[0] = rng.normal()
    for t in range(1, T):
        x[t] = a * x[t - 1] + s * rng.normal()
    return x


def skeleton(unit):
    g = pl.read_parquet(OUT / "grid" / f"{unit}.parquet")
    agents = sorted(g["agent"].unique().to_list())
    lab_of = dict(zip(g["agent"].to_list(), g["lab"].to_list()))
    days = g.group_by("pt_date").agg(pl.col("m").max().alias("T")).sort("pt_date")["T"].to_list()
    rooms = g.group_by("agent").agg(pl.col("room").drop_nulls().mode().first()).sort("agent")["room"].to_list()
    return {"unit": unit, "agents": agents, "labs": [lab_of[a] for a in agents], "T": [int(t) + 1 for t in days],
            "rooms": [r if r is not None else 0 for r in rooms]}


def simulate(sk, world, seed, field_dyn=True):
    """field_dyn=False keeps the measured field but removes its action on the dynamics (truth run)."""
    p = WORLDS[world]
    rng = np.random.default_rng(seed)
    N = len(sk["agents"])
    labs = np.array(sk["labs"]); rooms = np.array(sk["rooms"])
    mu = np.log(12.0) + rng.normal(0, 0.2, N)
    h_wp = rng.uniform(0.03, 0.07, N)   # work -> pause per minute (mean work run 14-33 min)
    h_pw = rng.uniform(0.12, 0.25, N)   # pause -> work (mean pause 4-8 min)
    rows = []
    for di, T in enumerate(sk["T"]):
        Lf = ou(T, 10.0, rng)
        Df = ou(T, 10.0, rng)  # slow common activity drive (W6 only)
        lab_f = {l: ou(T, 10.0, rng) for l in np.unique(labs)}
        state = rng.random(N) < 0.75
        talk_prev = np.zeros(N, bool)
        for m in range(T):
            lab_term = np.array([lab_f[l][m] for l in labs])
            drive = p["beta"] * Lf[m] + p["lab"] * lab_term   # measured log-latency shift
            act_drive = drive if (p["mech"] and field_dyn) else 0.0 * drive
            # pause hazard
            g_term = p["gamma"] * (Lf[m] if p["beta"] > 0 else 0) + p["gamma"] * (lab_term if p["lab"] > 0 else 0)
            g_term = g_term if field_dyn else 0.0 * g_term
            hz_wp = np.clip(h_wp * np.exp(g_term - p.get("drive", 0.0) * Df[m]), 0, 0.9)
            nroom = np.array([talk_prev[rooms == rooms[i]].sum() - talk_prev[i] for i in range(N)])
            hz_pw = np.clip(h_pw * (1 + p["kappa"] * nroom), 0, 0.95)
            flip = rng.random(N)
            new = np.where(state, flip >= hz_wp, flip < hz_pw)
            state = new
            # calls in a working minute
            tau_dyn = np.exp(mu + act_drive + rng.normal(0, 0.3, N))
            ncalls = np.where(state, rng.poisson(60.0 / tau_dyn), 0)
            talk = state & (rng.random(N) < 0.1)
            talk_prev = talk
            cong = p.get("cong", 0.0) * (state.sum() - 0.7 * N) / np.sqrt(N)
            for i in range(N):
                if ncalls[i] > 0:
                    lt = mu[i] + drive[i] + cong + rng.normal(0, 0.6, ncalls[i])
                    lat = float(np.median(lt))
                else:
                    lat = None
                rows.append((f"d{di:02d}", m, sk["agents"][i], int(ncalls[i] > 0), int(ncalls[i]), lat,
                             int(sk["labs"][i]), int(rooms[i])))
    g = pl.DataFrame(rows, schema=["pt_date", "m", "agent", "a", "n", "lat", "lab", "room"], orient="row")
    return g.with_columns(pl.lit(None, pl.Float32).alias("api"), pl.lit(0).alias("err"),
                          pl.col("lat").cast(pl.Float32))


def job(args):
    sk, world, seed = args
    g = simulate(sk, world, seed)
    r = L.analyze_grid(g, seed=seed, R=49, K=10, B=50, full=False)
    out = {"unit": sk["unit"], "world": world, "seed": seed, "E": r["binary"]["E"], "p_E": r["binary"]["p_E"],
           "f_lat": r["binary"]["f_lat"], "delta_f": r["binary"]["delta_f"], "delta_f_ci": r["binary"]["delta_f_ci"],
           "lam": r["field_reliability"]["lambda"],
           "rho_lat": r["lat_strength"]["all"]["rho"], "p_lat": r["lat_strength"]["all"]["p"],
           "rho_lat_same": r["lat_strength"]["same_lab"]["rho"], "rho_lat_cross": r["lat_strength"]["cross_lab"]["rho"],
           "E_same_room": r["binary"].get("E_same_room"), "E_cross_room": r["binary"].get("E_cross_room")}
    if WORLDS[world]["gamma"] > 0 or WORLDS[world]["mech"]:
        g0 = simulate(sk, world, seed, field_dyn=False)
        r0 = L.analyze_grid(g0, seed=seed, R=49, K=2, B=2, full=False)
        out["E_nofield"] = r0["binary"]["E"]
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=8)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--units", default="44b,51c")
    ap.add_argument("--summary-only", action="store_true")
    a = ap.parse_args()
    if a.summary_only:
        return summarize(pl.read_parquet(OUT / "synthetic" / "runs.parquet"))
    sks = [skeleton(u) for u in a.units.split(",")]
    jobs = [(sk, w, 1000 + s) for sk in sks for w in WORLDS for s in range(a.seeds)]
    with ProcessPoolExecutor(a.workers) as ex:
        res = list(ex.map(job, jobs))
    df = pl.DataFrame(res, infer_schema_length=None)
    (OUT / "synthetic").mkdir(parents=True, exist_ok=True)
    df.write_parquet(OUT / "synthetic" / "runs.parquet")
    summarize(df)


def summarize(df):
    summ = []
    for (u, w), d in df.group_by("unit", "world", maintain_order=True):
        E = d["E"].to_numpy(); E0 = d["E_nofield"].cast(pl.Float64).to_numpy() if "E_nofield" in d.columns and d["E_nofield"].null_count() < d.height else None
        f_true = float(1 - np.nanmean(E0) / np.nanmean(E)) if E0 is not None else 0.0
        lo = np.array([c[0] for c in d["delta_f_ci"]]); hi = np.array([c[1] for c in d["delta_f_ci"]])
        summ.append({"unit": u, "world": w, "n": d.height, "E_mean": float(np.mean(E)), "sig_E": float(np.mean(d["p_E"].to_numpy() < 0.05)),
                     "delta_f_mean": float(np.nanmean(d["delta_f"].to_numpy())),
                     "lam": float(np.nanmean(d["lam"].cast(pl.Float64).to_numpy())), "delta_f_sd": float(np.nanstd(d["delta_f"].to_numpy())),
                     "f_true": f_true, "ci_covers_truth": float(np.mean((lo <= f_true) & (f_true <= hi))),
                     "delta_f_ci_excl0": float(np.mean(lo > 0)),
                     "rho_lat": float(np.nanmean(d["rho_lat"].cast(pl.Float64).to_numpy())), "sig_lat": float(np.mean(d["p_lat"].to_numpy() < 0.05)),
                     "rho_lat_same": float(np.nanmean(d["rho_lat_same"].cast(pl.Float64).to_numpy())), "rho_lat_cross": float(np.nanmean(d["rho_lat_cross"].cast(pl.Float64).to_numpy())),
                     "E_same_room": float(np.nanmean(d["E_same_room"].cast(pl.Float64).to_numpy())) if d["E_same_room"].null_count() < d.height else None,
                     "E_cross_room": float(np.nanmean(d["E_cross_room"].cast(pl.Float64).to_numpy())) if d["E_cross_room"].null_count() < d.height else None})
    (OUT / "synthetic" / "summary.json").write_text(json.dumps(summ, indent=1))
    for s in summ:
        print({k: (round(v, 3) if isinstance(v, float) else v) for k, v in s.items()})


if __name__ == "__main__":
    main()
