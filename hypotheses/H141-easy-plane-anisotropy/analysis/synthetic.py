"""H141 synthetic validation on real skeletons (axis F; runs before any real-data statistic).

Keeps each unit's real statements (agent, time, room, producing call, plane key), the real per-call clock and the real
text planes (texts only); the content vectors are synthetic (32-d):
  z_B = h_i + x_i(c_B) + D_room(t_B) + eps_B
  x_i(c+1) = (1 - Gamma) x_i(c) + xi,   Gamma = g_par P_E + g_perp (1 - P_E)  (isotropic innovations, so the stationary
                                         variance per direction is q / (1 - (1-g)^2): fluctuation-dissipation holds)
  h_i ~ N(0, 0.25 S), eps ~ N(0, 0.6 S), S = low-rank content covariance with 8 active (Haar) directions carrying 3/4
  of the variance; the OU state has variance 0.2 per direction at g = 0.01. The call clock c runs on across the unit's
  days (nights carry the state over).
Worlds (card): W-easy (g_par 0.001, g_perp 0.01), W-iso (0.01), W-hard (0.03 / 0.01), W-modes (0.001 along 3 random
active directions with E projected out; 0.01 elsewhere), W-drive (W-iso plus a common OU drift along E, wall time scale
1-6 h, variance 0.2 per direction; in #51 along the village goal axis).

    uv run python hypotheses/H141-easy-plane-anisotropy/analysis/synthetic.py --reps 100 [--units 51c,51g,38a,41]
Output: data/processed/H141-easy-plane-anisotropy/synthetic/{runs.parquet, summary.json}
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
from scipy.signal import lfilter  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h141lib as L  # noqa: E402

OUT = L.DATA / "synthetic"
DIM = 32
VAR = {"h": 0.25, "x": 0.2, "eps": 0.6, "drive": 0.2}
G0 = 0.01
WORLDS = {
    "W-easy": dict(g_par=0.001, g_perp=0.01, truth=np.log(10.0)),
    "W-iso": dict(g_par=0.01, g_perp=0.01, truth=0.0),
    "W-hard": dict(g_par=0.03, g_perp=0.01, truth=np.log(1 / 3)),
    "W-modes": dict(g_par=0.01, g_perp=0.01, slow_modes=3, g_slow=0.001, truth=0.0),
    "W-drive": dict(g_par=0.01, g_perp=0.01, drive=True, truth=0.0),
}
UNIT_GOAL = {"51c": 51, "51g": 51, "38a": 38, "41": 41}


def skeleton(unit: str):
    goal = UNIT_GOAL[unit]
    st = pl.read_parquet(L.DATA / f"G{goal:02d}" / "statements.parquet").filter(pl.col("unit_id") == unit)
    calls = (pl.read_parquet(L.DATA / f"G{goal:02d}" / "calls.parquet").filter(pl.col("unit_id") == unit)
             .sort("agent", "t_call", "turn_id"))
    return goal, st, calls


def low_rank_cov(rng, k: int = 8, share: float = 0.75):
    Q, _ = np.linalg.qr(rng.normal(size=(DIM, DIM)))
    s = np.r_[np.full(k, share * DIM / k), np.full(DIM - k, (1 - share) * DIM / (DIM - k))]
    return Q, (Q * s) @ Q.T


def ou_series(n: int, gam: np.ndarray, rng) -> np.ndarray:
    """n x 32 AR(1) series with per-column rate gam and isotropic innovation variance q (stationary start)."""
    q = VAR["x"] * (1 - (1 - G0) ** 2)
    Y = np.zeros((n, DIM))
    for g in np.unique(gam):
        cols = np.flatnonzero(gam == g)
        a = 1 - g
        e = rng.normal(0, np.sqrt(q), (n, len(cols)))
        y0 = rng.normal(0, np.sqrt(q / (1 - a * a)), len(cols))
        Y[:, cols], _ = lfilter([1.0], [1.0, -a], e, axis=0, zi=(a * y0)[None, :])
    return Y


def simulate(goal: int, st: pl.DataFrame, calls: pl.DataFrame, planes: dict, texts: dict, W: dict, seed: int):
    rng = np.random.default_rng(seed)
    st = st.sort("agent", "t", maintain_order=True)
    Qa, S = low_rank_cov(rng)
    Ls = np.linalg.cholesky(S + 1e-12 * np.eye(DIM))
    agents = np.unique(st["agent"].to_numpy())
    plane_of = dict(st.group_by("agent").agg(pl.col("plane").mode().first()).iter_rows())
    # slow modes (W-modes): 3 random active directions with the shared axis projected out
    slow = None
    if W.get("slow_modes"):
        shared = planes["P"] if "P" in planes else texts["goal"][:, None]
        Pe = L.proj(shared)
        Vs = (np.eye(DIM) - Pe) @ Qa[:, :8] @ rng.normal(size=(8, W["slow_modes"]))
        slow, _ = np.linalg.qr(Vs)
    Z = np.zeros((st.height, DIM))
    a_st = st["agent"].to_numpy()
    turn = st["turn_id"].to_numpy()
    for ag in agents:
        cs = calls.filter(pl.col("agent") == ag)
        cidx = {t: k for k, t in enumerate(cs["turn_id"].to_list())}
        if slow is not None:
            U, _ = np.linalg.qr(np.column_stack([slow, rng.normal(size=(DIM, DIM - slow.shape[1]))]))
            gam = np.r_[np.full(slow.shape[1], W["g_slow"]), np.full(DIM - slow.shape[1], G0)]
        else:
            E = planes[plane_of[ag]]
            U, _ = np.linalg.qr(np.column_stack([E, rng.normal(size=(DIM, DIM - E.shape[1]))]))
            gam = np.r_[np.full(E.shape[1], W["g_par"]), np.full(DIM - E.shape[1], W["g_perp"])]
        Y = ou_series(len(cs), gam, rng)
        Xc = Y @ U.T
        h = Ls @ rng.normal(0, np.sqrt(VAR["h"]), DIM)
        rows = np.flatnonzero(a_st == ag)
        ci = np.array([cidx[t] for t in turn[rows]])
        Z[rows] = h + Xc[ci] + (Ls @ rng.normal(0, np.sqrt(VAR["eps"]), (DIM, len(rows)))).T
    if W.get("drive"):
        ax = planes["P"] if "P" in planes else texts["goal"][:, None]
        TD = rng.uniform(3600, 21600)
        t = st["t"].dt.epoch("us").to_numpy() / 1e6
        room = st["room"].fill_null(-1).to_numpy()
        for r in np.unique(room):
            k = np.flatnonzero(room == r)
            o = k[np.argsort(t[k])]
            v = np.zeros((len(o), ax.shape[1]))
            v[0] = rng.normal(0, np.sqrt(VAR["drive"]), ax.shape[1])
            for j in range(1, len(o)):
                a = np.exp(-(t[o[j]] - t[o[j - 1]]) / TD)
                v[j] = a * v[j - 1] + np.sqrt(VAR["drive"] * (1 - a * a)) * rng.normal(size=ax.shape[1])
            Z[o] += v @ ax.T
    return st, Z


def run_one(unit: str, world: str, rep: int, B: int, n_rand: int, cache: dict) -> dict:
    goal, st, calls = cache[unit]
    planes, texts = L.load_planes(goal, "bge_small")
    seed = zlib.crc32(f"H141|{unit}|{world}|{rep}".encode()) % (2 ** 31)
    st2, Z = simulate(goal, st, calls, planes, texts, WORLDS[world], seed)
    D = L.load(goal, Z_override=Z, st=st2)
    A = L.accumulate(D)
    days = sorted(st2["pt_date"].unique().to_list())
    r = L.analyze_unit(D, A, days, B=B, n_rand=n_rand, seed=seed + 1)
    r.update({"unit": unit, "world": world, "rep": rep, "truth": float(WORLDS[world]["truth"])})
    return r


def summarize(df: pl.DataFrame) -> dict:
    out = {}
    for w in WORLDS:
        d = df.filter(pl.col("world") == w)
        if d.height == 0:
            continue
        s = {"n": d.height, "truth_ln_rho": float(WORLDS[w]["truth"])}
        lr = np.log(d["rho"].to_numpy())
        s["ln_rho_median_by_unit"] = {u: float(np.nanmedian(np.log(d.filter(pl.col("unit") == u)["rho"].to_numpy())))
                                      for u in sorted(d["unit"].unique().to_list())}
        s["ln_rho_median"] = float(np.nanmedian(lr))
        s["frac_within_0.5"] = float(np.nanmean(np.abs(lr - WORLDS[w]["truth"]) <= 0.5))
        s["frac_edge_par"] = float(np.mean(d["edge_par"].to_numpy() == -1))
        s["raw_ln_rho_median"] = float(np.nanmedian(np.log(d["raw_rho"].to_numpy())))
        s["frac_rho_gt3"] = float(np.nanmean(d["rho"].to_numpy() > 3))
        s["frac_raw_rho_gt3"] = float(np.nanmean(d["raw_rho"].to_numpy() > 3))
        s["frac_rho_in_[1/3,3]"] = float(np.nanmean((d["rho"].to_numpy() >= 1 / 3) & (d["rho"].to_numpy() <= 3)))
        s["frac_rand_pct_gt_0.95"] = float(np.nanmean(d["rand_pct"].to_numpy() > 0.95))
        s["V_A_median"] = float(np.nanmedian(d["V_A"].to_numpy()))
        s["V_A_lag1_median"] = float(np.nanmedian(d["V_A_lag1"].to_numpy()))
        s["pca_ln_rho_median"] = float(np.nanmedian(np.log(d["pca_rho"].to_numpy()))) if "pca_rho" in d.columns else None
        rho_ = d["rho"].to_numpy()
        for vk in ("V_A", "V_A_lag1"):
            rr_ = d[vk].to_numpy() / rho_
            s[f"P3_{vk}_within2"] = float(np.nanmean((rr_ >= 0.5) & (rr_ <= 2)))
        s["frac_raw_rho_in_[1/3,3]"] = float(np.nanmean((d["raw_rho"].to_numpy() >= 1 / 3) & (d["raw_rho"].to_numpy() <= 3)))
        for tag in ("", "cen_", "vg_", "vgcen_"):
            if f"{tag}P_diff" in d.columns:
                pdf = d[f"{tag}P_diff"].to_numpy()
                ci = np.array([json.loads(x) if isinstance(x, str) else [np.nan, np.nan] for x in d[f"{tag}P_diff_ci95"]])
                s[f"{tag}P_par_median"] = float(np.nanmedian(d[f"{tag}P_par"].to_numpy()))
                s[f"{tag}P_perp_median"] = float(np.nanmedian(d[f"{tag}P_perp"].to_numpy()))
                s[f"{tag}P_diff_median"] = float(np.nanmedian(pdf))
                s[f"{tag}P_diff_pos_sig"] = float(np.nanmean(ci[:, 0] > 0))
                s[f"{tag}P_diff_neg_sig"] = float(np.nanmean(ci[:, 1] < 0))
                s[f"{tag}P_rand_pct_gt_0.95"] = float(np.nanmean(d[f"{tag}P_rand_pct"].to_numpy() > 0.95))
        # pooled over the four skeleton units per replicate (the registered P1 / kill are on a pool)
        pools = []
        for rep in sorted(d["rep"].unique().to_list()):
            q = d.filter(pl.col("rep") == rep)
            mu, se, t2, i2, k = L.dl_pool(np.log(q["rho"].to_numpy()), q["se_ln"].to_numpy())
            if k >= 2:
                pools.append((mu, se))
        if pools:
            P = np.array(pools)
            lo90, hi90 = P[:, 0] - 1.645 * P[:, 1], P[:, 0] + 1.645 * P[:, 1]
            s["pool_ln_rho_median"] = float(np.median(P[:, 0]))
            s["pool_bias"] = float(np.median(P[:, 0]) - WORLDS[w]["truth"])
            s["pool_within_0.5"] = float(np.mean(np.abs(P[:, 0] - WORLDS[w]["truth"]) <= 0.5))
            s["pool_kill_fires"] = float(np.mean((lo90 >= np.log(1 / 3)) & (hi90 <= np.log(3))))
            s["pool_reverse_kill_fires"] = float(np.mean((P[:, 0] < np.log(1 / 3)) & (hi90 < 0)))
            s["pool_P1_passes"] = float(np.mean((P[:, 0] >= np.log(10)) & (lo90 >= np.log(3))))
            s["pool_se_median"] = float(np.median(P[:, 1]))
            s["n_pools"] = len(pools)
        out[w] = s
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=100)
    ap.add_argument("--units", default="51c,51g,38a,41")
    ap.add_argument("--worlds", default=",".join(WORLDS))
    ap.add_argument("--B", type=int, default=100)
    ap.add_argument("--n_rand", type=int, default=200)
    ap.add_argument("--tag", default="")
    ap.add_argument("--summary-only", action="store_true")
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / f"runs{a.tag}.parquet"
    if a.summary_only:
        df = pl.read_parquet(path)
        print(json.dumps(summarize(df), indent=1))
        (OUT / f"summary{a.tag}.json").write_text(json.dumps(summarize(df), indent=1))
        return
    rows = pl.read_parquet(path).to_dicts() if path.exists() else []
    done = {(r["unit"], r["world"], r["rep"]) for r in rows}
    cache = {u: skeleton(u) for u in a.units.split(",")}
    for rep in range(a.reps):
        for w in a.worlds.split(","):
            for u in a.units.split(","):
                if (u, w, rep) in done:
                    continue
                t0 = time.time()
                r = run_one(u, w, rep, a.B, a.n_rand, cache)
                r["secs"] = time.time() - t0
                rows.append({k: (json.dumps(v) if isinstance(v, (list, tuple)) else v) for k, v in r.items()})
                print(f"{u} {w} {rep} rho {r['rho']:.2f} raw {r['raw_rho']:.2f} pct {r['rand_pct']:.2f} "
                      f"V {r['V_A']:.2f} Pd {r.get('P_diff', np.nan):.3f} vgPd {r.get('vg_P_diff', np.nan):.3f} "
                      f"({r['secs']:.1f}s)", flush=True)
        pl.DataFrame(rows, infer_schema_length=None).write_parquet(path)
    df = pl.DataFrame(rows, infer_schema_length=None)
    df.write_parquet(path)
    summ = summarize(df)
    (OUT / f"summary{a.tag}.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
