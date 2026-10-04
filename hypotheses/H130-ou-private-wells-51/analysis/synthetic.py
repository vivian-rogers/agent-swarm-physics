"""H130 synthetic validation on the real #51 skeleton (axis F; before any real-data statistic).

Keeps each unit's real statements (agent, time, room, producing call), the real per-call clock, the real reads
(which message each call read) and the real forced resets; only the content vectors are synthetic (32-d):
  z_B = h_i + x_i(n_B) + k_i(n_B) + D_room(t_B) + eps_B
  x_i(n+1) = (1 - gamma) x_i(n) + kappa * sum_{m read at n} (z_m - h_i) + xi      (OU well with read kicks)
  k_i: context-held kick (world W2): k <- (1 - gamma_k) k + kappa_k * sum (z_m - h_i); k = 0 at a forced reset
  D_room(t): room drive, OU in seconds with time scale T_D (common field)
Worlds: W0 OU, no kicks; W1 OU + kicks; W1s slow well; W2 context-held kick; W3 strong fast common drive, no kicks.

    uv run python hypotheses/H130-ou-private-wells-51/analysis/synthetic.py [--reps 4] [--units 51c,51d,51g]
Output: data/processed/H130-ou-private-wells-51/synthetic/{runs.parquet, summary.json}
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

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
import h130lib as L  # noqa: E402

OUT = L.DATA / "synthetic"
DIM = 32
VAR = {"h": 0.25, "x": 0.2, "eps": 0.6}

WORLDS = {
    "W0_null": dict(gamma=0.01, kappa=0.0, D=0.05, TD=1800.0),
    "W1_kick": dict(gamma=0.01, kappa=0.003, D=0.05, TD=1800.0),
    "W1_kick_strong": dict(gamma=0.01, kappa=0.006, D=0.05, TD=1800.0),
    "W1s_slow": dict(gamma=0.003, kappa=0.003, D=0.05, TD=1800.0),
    "W2_context": dict(gamma=0.01, kappa=0.0, kappa_k=0.01, gamma_k=0.05, D=0.05, TD=1800.0),
    "W3_drive": dict(gamma=0.01, kappa=0.0, D=0.2, TD=300.0),
    "W1_fastdrive": dict(gamma=0.01, kappa=0.003, D=0.1, TD=300.0),
    "W1_slowdrive": dict(gamma=0.01, kappa=0.003, D=0.1, TD=10800.0),
}


def skeleton(unit: str):
    st = pl.read_parquet(L.DATA / "statements.parquet").filter(pl.col("unit_id") == unit)
    rd = pl.read_parquet(L.DATA / "reads.parquet").filter(pl.col("unit_id") == unit)
    rd = rd.join(st.select(pl.col("srow").alias("srow_m")), on="srow_m", how="semi")
    calls = pl.read_parquet(L.DATA / "calls.parquet").filter(pl.col("unit_id") == unit).sort("t_call", "turn_id")
    return st, rd, calls


def room_drive(st: pl.DataFrame, D: float, TD: float, rng):
    t = st["t"].dt.epoch("us").to_numpy() / 1e6
    room = st["room"].to_numpy()
    out = np.zeros((len(t), DIM))
    if D <= 0:
        return out
    for r in np.unique(room):
        k = np.flatnonzero(room == r)
        o = np.argsort(t[k])
        tt = t[k][o]
        v = np.zeros((len(tt), DIM))
        v[0] = rng.normal(0, np.sqrt(D), DIM)
        for j in range(1, len(tt)):
            a = np.exp(-(tt[j] - tt[j - 1]) / TD)
            v[j] = a * v[j - 1] + np.sqrt(D * (1 - a * a)) * rng.normal(0, 1, DIM)
        out[k[o]] = v
    return out


def simulate(st: pl.DataFrame, rd: pl.DataFrame, calls: pl.DataFrame, P: dict, seed: int, return_h: bool = False):
    """Content vectors for the unit's statements (row order of st sorted by agent, t as in L.load)."""
    rng = np.random.default_rng(seed)
    st = st.sort("agent", "t").with_row_index("i")
    agents = np.unique(st["agent"].to_numpy())
    h = {a: rng.normal(0, np.sqrt(VAR["h"]), DIM) for a in agents}
    g, kap = P["gamma"], P["kappa"]
    gk, kk = P.get("gamma_k", 0.0), P.get("kappa_k", 0.0)
    sx = np.sqrt(VAR["x"] * (1 - (1 - g) ** 2))
    Dv = room_drive(st, P["D"], P["TD"], rng)
    Z = np.zeros((st.height, DIM))
    done = np.zeros(st.height, bool)
    sid = dict(zip(st["srow"].to_list(), st["i"].to_list()))
    by_turn_st = {}
    for tid, i in zip(st["turn_id"].to_list(), st["i"].to_list()):
        by_turn_st.setdefault(tid, []).append(i)
    by_turn_rd = {}
    for tid, sm in zip(rd["turn_id"].to_list(), rd["srow_m"].to_list()):
        j = sid.get(sm)
        if j is not None:
            by_turn_rd.setdefault(tid, []).append(j)
    ag_st = st["agent"].to_numpy()
    x = {a: rng.normal(0, np.sqrt(VAR["x"]), DIM) for a in agents}
    k = {a: np.zeros(DIM) for a in agents}
    last_day = {}
    for tid, a, day, rf in zip(calls["turn_id"].to_list(), calls["agent"].to_list(), calls["pt_date"].to_list(),
                               calls["reset_forced"].to_list()):
        if a not in x:
            continue
        if last_day.get(a) != day:                 # new day: stationary restart
            x[a] = rng.normal(0, np.sqrt(VAR["x"]), DIM)
            k[a] = np.zeros(DIM)
            last_day[a] = day
        x[a] = (1 - g) * x[a] + sx * rng.normal(0, 1, DIM)
        if kk:
            k[a] = (1 - gk) * k[a]
            if rf:
                k[a] = np.zeros(DIM)
        reads = by_turn_rd.get(tid)
        if reads:
            for j in reads:
                if not done[j] or ag_st[j] == a:
                    continue
                if kap:
                    x[a] += kap * (Z[j] - h[a])
                if kk:
                    k[a] += kk * (Z[j] - h[a])
        for i in by_turn_st.get(tid, []):
            Z[i] = h[a] + x[a] + k[a] + Dv[i] + rng.normal(0, np.sqrt(VAR["eps"]), DIM)
            done[i] = True
    # statements whose producing call is not in calls (should not happen): pure noise around the well
    for i in np.flatnonzero(~done):
        Z[i] = h[ag_st[i]] + rng.normal(0, np.sqrt(VAR["x"] + VAR["eps"]), DIM)
    return (Z, h) if return_h else Z


def evaluate(st, rd, Z, B: int, seed: int, mode: str = "past") -> dict:
    D = L.load(Z_override=Z, st=st, rd=rd)
    return L.analyze(D, B=B, seed=seed, do_old=True, do_natives=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=4)
    ap.add_argument("--units", default="51c,51d,51g")
    ap.add_argument("--worlds", default=",".join(WORLDS))
    ap.add_argument("--B", type=int, default=60)
    ap.add_argument("--mode", default="past")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    rows = []
    for unit in a.units.split(","):
        st, rd, calls = skeleton(unit)
        for w in a.worlds.split(","):
            for rep in range(a.reps):
                t0 = time.time()
                seed = zlib.crc32(f"{unit}|{w}|{rep}".encode()) % (2 ** 31)
                Z = simulate(st, rd, calls, WORLDS[w], seed)
                res = evaluate(st, rd, Z, a.B, seed + 1, a.mode)
                res.update({"unit": unit, "world": w, "rep": rep, "mode": a.mode, "secs": time.time() - t0, **{f"p_{k}": v for k, v in WORLDS[w].items()}})
                rows.append(res)
                print(unit, w, rep, f"g_auto {res['g_auto']:.4f} (raw {res['g_auto_raw']:.4f}) g_kick {res['g_kick']:.4f} "
                      f"(msgdir {res['g_kick_msgdir']:.4f}) rho {res['rho']:.2f} ci90 {np.round(res['ci_rho90'], 2)} "
                      f"J {res['J']:.4f} {np.round(res['ci_J'], 3)} Jp {res['J_pair']:.4f} {np.round(res['ci_J_pair'], 4)} "
                      f"R_C {res['R_C']:.2f} R_K {res['R_K']:.2f} ({res['secs']:.0f}s)", flush=True)
                pl.DataFrame([{k: (json.dumps(v) if isinstance(v, list) else v) for k, v in r.items()} for r in rows]).write_parquet(OUT / "runs.parquet")
    df = pl.DataFrame([{k: (json.dumps(v) if isinstance(v, list) else v) for k, v in r.items()} for r in rows])
    summ = {}
    for w in WORLDS:
        d = df.filter(pl.col("world") == w)
        if d.height == 0:
            continue
        jl = np.array([json.loads(x) for x in d["ci_J"]])
        jp = np.array([json.loads(x) for x in d["ci_J_pair"]])
        rl = np.array([json.loads(x) for x in d["ci_rho90"]])
        rho = d["rho"].to_numpy()
        summ[w] = {"n": d.height, "params": WORLDS[w],
                   "g_auto_med": float(d["g_auto"].median()), "g_auto_raw_med": float(d["g_auto_raw"].median()),
                   "g_kick_med": float(d["g_kick"].median()), "g_kick_msgdir_med": float(d["g_kick_msgdir"].median()),
                   "rho_med": float(np.nanmedian(rho)), "rho_in_[0.5,2]": float(np.mean((rho >= 0.5) & (rho <= 2))),
                   "K1_fires": float(np.mean([(not (0.5 <= r <= 2)) and not (lo <= 1 <= hi) for r, (lo, hi) in zip(rho, rl)])),
                   "J_med": float(d["J"].median()), "J_pos_sig": float(np.mean(jl[:, 0] > 0)),
                   "Jpair_med": float(d["J_pair"].median()), "Jpair_pos_sig": float(np.mean(jp[:, 0] > 0)),
                   "R_C_med": float(d["R_C"].median()), "R_K_med": float(d["R_K"].median())}
    (OUT / "summary.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
