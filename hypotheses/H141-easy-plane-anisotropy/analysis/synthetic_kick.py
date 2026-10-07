"""H141 synthetic check of the P4 kick estimator (added to the card's plan; axis F) on the real 51c skeleton (statements,
call clock, reads). Isotropic OU wells (g 0.01) plus a read kick k_i that decays per call at g_k:
  k <- (1 - g_k) k + kappa * sum_{m read at the call} (z_m - h_i);   z_B = h_i + x_i + k_i + eps
Worlds: K-none (kappa 0), K-one-call (g_k 1: the kick lives only in the reading call; true lag-1 ratio 0),
K-fast (g_k 0.15, H130's measured kick decay; true ratio 0.85). Same scales as synthetic.py.

    uv run python hypotheses/H141-easy-plane-anisotropy/analysis/synthetic_kick.py --reps 10
Output: data/processed/H141-easy-plane-anisotropy/synthetic/kick_runs.parquet, kick_summary.json
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
import h141lib as L  # noqa: E402
import kick as K  # noqa: E402
from synthetic import VAR, DIM, G0, low_rank_cov  # noqa: E402

OUT = L.DATA / "synthetic"
WORLDS = {"K-none": dict(kappa=0.0, g_k=1.0, truth=np.nan), "K-one-call": dict(kappa=0.006, g_k=1.0, truth=0.0),
          "K-fast": dict(kappa=0.006, g_k=0.15, truth=0.85)}


def simulate(st, calls, rd, P, seed):
    rng = np.random.default_rng(seed)
    st = st.sort("agent", "t", maintain_order=True).with_row_index("i")
    _, S = low_rank_cov(rng)
    Ls = np.linalg.cholesky(S)
    agents = np.unique(st["agent"].to_numpy())
    h = {a: Ls @ rng.normal(0, np.sqrt(VAR["h"]), DIM) for a in agents}
    q = VAR["x"] * (1 - (1 - G0) ** 2)
    x = {a: rng.normal(0, np.sqrt(VAR["x"]), DIM) for a in agents}
    k = {a: np.zeros(DIM) for a in agents}
    Z = np.zeros((st.height, DIM))
    done = np.zeros(st.height, bool)
    sid = dict(zip(st["srow"].to_list(), st["i"].to_list()))
    by_turn_st, by_turn_rd = {}, {}
    for tid, i in zip(st["turn_id"].to_list(), st["i"].to_list()):
        by_turn_st.setdefault(tid, []).append(i)
    for tid, sm in zip(rd["turn_id"].to_list(), rd["srow_m"].to_list()):
        j = sid.get(sm)
        if j is not None:
            by_turn_rd.setdefault(tid, []).append(j)
    ag_st = st["agent"].to_numpy()
    cs = calls.sort("t_call", "turn_id")
    for tid, a in zip(cs["turn_id"].to_list(), cs["agent"].to_list()):
        if a not in x:
            continue
        x[a] = (1 - G0) * x[a] + np.sqrt(q) * rng.normal(size=DIM)
        k[a] = (1 - P["g_k"]) * k[a]
        for j in by_turn_rd.get(tid, ()):
            if done[j] and ag_st[j] != a and P["kappa"]:
                k[a] += P["kappa"] * (Z[j] - h[a])
        for i in by_turn_st.get(tid, ()):
            Z[i] = h[a] + x[a] + k[a] + Ls @ rng.normal(0, np.sqrt(VAR["eps"]), DIM)
            done[i] = True
    for i in np.flatnonzero(~done):
        Z[i] = h[ag_st[i]] + rng.normal(0, np.sqrt(VAR["x"] + VAR["eps"]), DIM)
    return st.drop("i"), Z


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=10)
    ap.add_argument("--unit", default="51c")
    ap.add_argument("--B", type=int, default=50)
    a = ap.parse_args()
    st = pl.read_parquet(L.DATA / "G51/statements.parquet").filter(pl.col("unit_id") == a.unit)
    calls = pl.read_parquet(L.DATA / "G51/calls.parquet").filter(pl.col("unit_id") == a.unit)
    rd = pl.read_parquet(L.DATA / "G51/reads.parquet").filter(pl.col("unit_id") == a.unit)
    rd = rd.join(st.select(pl.col("srow").alias("srow_m")), on="srow_m", how="semi")
    rows = []
    for rep in range(a.reps):
        for w, P in WORLDS.items():
            t0 = time.time()
            seed = zlib.crc32(f"H141k|{a.unit}|{w}|{rep}".encode()) % (2 ** 31)
            st2, Z = simulate(st, calls, rd, P, seed)
            D = L.load(51, Z_override=Z, st=st2)
            W = K.day_wells(D)
            r = K.kick_unit(D, rd, W, a.B, seed + 1)
            row = {"world": w, "rep": rep, "truth": P["truth"], "secs": time.time() - t0}
            for nm in ("par", "perp"):
                row[f"b0_{nm}"], row[f"b1_{nm}"] = r[f"beta_{nm}"][0], r[f"beta_{nm}"][1]
                row[f"se0_{nm}"], row[f"se1_{nm}"] = r[f"se_{nm}"][0], r[f"se_{nm}"][1]
                row[f"ratio_{nm}"] = r[f"ratio_{nm}"]
            rows.append(row)
            print(w, rep, {k_: round(v, 4) for k_, v in row.items() if isinstance(v, float)}, flush=True)
            pl.DataFrame(rows).write_parquet(OUT / "kick_runs.parquet")
    df = pl.DataFrame(rows)
    summ = {}
    for w in WORLDS:
        d = df.filter(pl.col("world") == w)
        summ[w] = {c: float(d[c].median()) for c in d.columns if c not in ("world", "rep", "truth")}
        summ[w]["b0_perp_pos_sig"] = float(np.mean(d["b0_perp"].to_numpy() - 1.96 * d["se0_perp"].to_numpy() > 0))
        summ[w]["truth_ratio"] = WORLDS[w]["truth"]
    (OUT / "kick_summary.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
