"""H49 synthetic validation (axis F): Glauber (heat-bath) Ising swarms at real village schedules.

Templates: real units 40 (N 15, 5 days x 4 h), 44b (N 17, 2 days x 4 h), 51d (N 26, 5 days x 8 h). From each:
real day/minute layout, off-schedule minutes, real scaffold masks (agent-minutes silent with reason pre / post /
infra_err / consol are forced off: the day-edge drive and stalls), block fields h_i(b) = 0.5 logit(p_i(b)) from the
agent's real on-rate over its available minutes of each (day, 30-min block).
Dynamics: each minute, every non-forced agent updates with probability 0.35, in random order, by heat bath
P(s_i = +1) = sigma(2 (h_i(b) + sum_j J_ij s_j)). Forced agents sit at -1 and are felt by their partners.
Planted J: null; dilute (3 disjoint pairs + 1 triangle, J = 0.5 or 0.25); dense (all pairs J = 1.2/N, matched to the real surviving excess); perc
(Erdos-Renyi, mean degree 3, J = 0.3). Marker recall 0.7: 30% of reason spells unmarked (still forced off).

Output: data/processed/H49-dilute-ferromagnet/synthetic/results.parquet (+ summary.json)
Usage: uv run python hypotheses/H49-dilute-ferromagnet/analysis/synthetic.py [--reps 30] [--n-surr 100] [--workers 2]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
import zlib
from multiprocessing import Pool
from pathlib import Path

sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parent))
import h49lib as L  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

TEMPLATES = ["40", "44b", "51d"]
CONDS = [("null", 1.0), ("null", 0.7), ("dilute05", 1.0), ("dilute025", 1.0), ("dense", 1.0), ("perc", 1.0),
         ("dilute05", 0.7)]
UPD = 0.35
OUT = L.DATA / "synthetic"


def template(uid):
    m = np.load(L.DATA / "mats" / f"{uid}.npz")
    S, R, day, minute, sched = m["S"], m["R"], m["day"], m["minute"], m["sched"]
    forced = np.isin(R, (1, 2, 3, 4)) | sched[:, None]
    bid = L.h02.block_ids(day, minute)
    nb = bid.max() + 1
    N = S.shape[1]
    av = ~forced
    on = np.zeros((nb, N)); cnt = np.zeros((nb, N))
    np.add.at(on, bid, (av & (S > 0)).astype(float))
    np.add.at(cnt, bid, av.astype(float))
    p = np.where(cnt > 0, (on + 0.5) / (cnt + 1.0), 0.5)
    p = np.clip(p, 0.02, 0.98)
    h = 0.5 * np.log(p / (1 - p))
    return {"R": R, "day": day, "minute": minute, "sched": sched, "forced": forced, "bid": bid, "h": h, "N": N}


def plant(kind, N, rng):
    J = np.zeros((N, N))
    edges = []
    if kind.startswith("dilute"):
        val = 0.5 if kind == "dilute05" else 0.25
        ag = rng.permutation(N)
        groups = [ag[0:2], ag[2:4], ag[4:6], ag[6:9]]
        for g in groups:
            for a in range(len(g)):
                for b in range(a + 1, len(g)):
                    edges.append((g[a], g[b]))
        for a, b in edges:
            J[a, b] = J[b, a] = val
    elif kind == "dense":
        J[:] = 1.2 / N  # conditioned g ~ 0.25-0.38, the range of the real units with surviving excess (H38: #44, #51)
        np.fill_diagonal(J, 0.0)
        edges = [(a, b) for a in range(N) for b in range(a + 1, N)]
    elif kind == "perc":
        p = 3.0 / (N - 1)
        for a in range(N):
            for b in range(a + 1, N):
                if rng.random() < p:
                    J[a, b] = J[b, a] = 0.3
                    edges.append((a, b))
    return J, edges


def simulate(tp, J, rng):
    T, N = tp["forced"].shape
    S = -np.ones((T, N), np.int8)
    day, bid, h, forced = tp["day"], tp["bid"], tp["h"], tp["forced"]
    s = -np.ones(N)
    for t in range(T):
        if t == 0 or day[t] != day[t - 1]:
            p0 = 1 / (1 + np.exp(-2 * h[bid[t]]))
            s = np.where(rng.random(N) < p0, 1.0, -1.0)
        f = forced[t]
        s[f] = -1.0
        upd = np.flatnonzero((~f) & (rng.random(N) < UPD))
        if upd.size:
            hb = h[bid[t]]
            for i in rng.permutation(upd):
                H = hb[i] + J[i] @ s
                s[i] = 1.0 if rng.random() < 1 / (1 + np.exp(-2 * H)) else -1.0
        S[t] = s
    return S


def unmark(R, recall, rng):
    if recall >= 1:
        return R
    R2 = R.copy()
    T, N = R.shape
    for i in range(N):
        r = R[:, i]
        nz = r > 0
        if not nz.any():
            continue
        st = np.flatnonzero(nz & np.r_[True, (r[1:] != r[:-1])])
        en = np.r_[st[1:], T]
        for a, b in zip(st, en):
            seg = np.arange(a, b)
            seg = seg[R[seg, i] == R[a, i]]
            if rng.random() > recall:
                R2[seg, i] = 0
    return R2


def one(args):
    uid, kind, recall, rep, n_surr = args
    seed = (zlib.crc32(f"{uid}|{kind}|{recall}".encode()) % 10_000) * 1000 + rep
    rng = np.random.default_rng(seed)
    tp = template(uid)
    N = tp["N"]
    J, edges = plant(kind, N, rng)
    S = simulate(tp, J, rng)
    R = np.where(S > 0, 0, unmark(tp["R"], recall, rng)).astype(np.int8)
    t0 = time.time()
    res = L.run_dataset(S, R, tp["sched"], tp["day"], tp["minute"], None, n_surr=n_surr, seed=seed + 7,
                        variants=("scaffold", "raw"), graph_cm=100)
    iu = L.triu(N)
    truth = np.zeros(iu[0].size, bool)
    eset = {(min(a, b), max(a, b)) for a, b in edges}
    for k, (a, b) in enumerate(zip(*iu)):
        truth[k] = (a, b) in eset
    out = {"template": uid, "cond": kind, "recall": recall, "rep": rep, "N": N, "n_planted": len(eset),
           "runtime_s": time.time() - t0}
    for v in ("scaffold", "raw"):
        e = res["variants"][v]; b = e["bonds"]; g = e["graph"]
        sig = b["sig_pos"]
        tp_ = int((sig & truth).sum())
        out.update({f"{v}_frac05": b["frac05_pos"], f"{v}_n_pos": b["n_pos"], f"{v}_n_neg": b["n_neg"],
                    f"{v}_n_bh_pos": b["n_bh_pos"], f"{v}_mean_k": g["mean_k"], f"{v}_kappa": g["kappa"],
                    f"{v}_S1": g["S1"], f"{v}_cv_c10": e["cv_c10"], f"{v}_cv_c10_orig": e["cv_c10_orig"],
                    f"{v}_c10_in": e["c10_insample"], f"{v}_share_sig": e["share_sig"],
                    f"{v}_p_mean": b["p_mean"], f"{v}_p_skew": b["p_skew"], f"{v}_skew": b["skew_z"],
                    f"{v}_q95_skew": b["q95_skew"], f"{v}_mean_z": b["mean_z"], f"{v}_g": e["g"], f"{v}_E": e["E"],
                    f"{v}_z_g": e["z_g"], f"{v}_tp": tp_, f"{v}_fp": int((sig & ~truth).sum()),
                    f"{v}_recall": tp_ / truth.sum() if truth.sum() else np.nan,
                    f"{v}_precision": tp_ / sig.sum() if sig.sum() else np.nan,
                    f"{v}_null_fp_mean": b["null_fp_mean"], f"{v}_pi1": b["pi1"]})
        if kind == "null":
            out[f"{v}_frac05_all"] = b["frac05_pos"]
        if truth.any() and (~truth).any():
            out[f"{v}_frac05_nonplanted"] = float((b["p_pos"][~truth] < 0.05).mean())
    return out


def summarize(df: pl.DataFrame) -> dict:
    df = df.with_columns([pl.col(c).fill_nan(None) for c in df.columns if df[c].dtype == pl.Float64])
    exc = pl.col("scaffold_z_g") > 2
    agg = (df.group_by("template", "cond", "recall").agg(
        pl.len().alias("n"),
        *[pl.col(c).mean().alias(c) for c in ["scaffold_frac05", "raw_frac05", "scaffold_n_pos", "raw_n_pos",
                                             "scaffold_recall", "scaffold_precision", "raw_recall",
                                             "scaffold_mean_k", "scaffold_S1", "scaffold_g", "raw_g",
                                             "scaffold_E", "scaffold_null_fp_mean", "scaffold_pi1"]],
        pl.col("scaffold_cv_c10").filter(exc).median().alias("cv_c10_med_excess"),
        (pl.col("scaffold_cv_c10").filter(exc) >= 0.4).mean().alias("cv_ge04_excess"),
        (pl.col("scaffold_cv_c10").filter(exc) <= 0.2).mean().alias("cv_le02_excess"),
        pl.col("raw_cv_c10").filter(pl.col("raw_z_g") > 2).median().alias("raw_cv_c10_med_excess"),
        (pl.col("scaffold_fp")).mean().alias("scaffold_fp_bonds"),
        pl.col("scaffold_frac05_nonplanted").mean().alias("frac05_nonplanted"),
        (pl.col("scaffold_kappa") < 2).mean().alias("below_kappa"),
        ((pl.col("scaffold_kappa") < 2) & (pl.col("scaffold_S1") <= 0.3)).mean().alias("below_verdict"),
        ((pl.col("scaffold_kappa") >= 2) & (pl.col("scaffold_S1") >= 0.5)).mean().alias("perc_detected"),
        (pl.col("scaffold_z_g") > 2).mean().alias("excess_sig"),
        (pl.col("scaffold_p_mean") < 0.05).mean().alias("meanz_sig"),
        ((pl.col("scaffold_skew") > pl.col("scaffold_q95_skew")) & (pl.col("scaffold_cv_c10") >= 0.4) & exc)
        .fill_null(False).mean().alias("heavy_tail_call"),
        (exc & (pl.col("scaffold_cv_c10") <= 0.2)).fill_null(False).mean().alias("dense_call"),
        (pl.col("scaffold_n_pos") >= 4).mean().alias("ge4_bonds"),
    ).sort("template", "cond", "recall"))
    return {"table": agg.to_dicts()}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--reps", type=int, default=30)
    ap.add_argument("--n-surr", type=int, default=100)
    ap.add_argument("--workers", type=int, default=2)
    ap.add_argument("--templates", default=",".join(TEMPLATES))
    a = ap.parse_args()
    OUT.mkdir(parents=True, exist_ok=True)
    jobs = [(u, k, r, rep, a.n_surr) for u in a.templates.split(",") for (k, r) in CONDS for rep in range(a.reps)]
    t0 = time.time()
    rows = []
    with Pool(min(a.workers, 2)) as pool:
        for i, r in enumerate(pool.imap_unordered(one, jobs)):
            rows.append(r)
            if (i + 1) % 20 == 0:
                print(f"{i + 1}/{len(jobs)} {time.time() - t0:.0f}s", flush=True)
                pl.DataFrame(rows).write_parquet(OUT / "results_partial.parquet")
    df = pl.DataFrame(rows)
    df.write_parquet(OUT / "results.parquet")
    (OUT / "results_partial.parquet").unlink(missing_ok=True)
    sm = summarize(df)
    sm["params"] = {"reps": a.reps, "n_surr": a.n_surr, "templates": a.templates, "update_prob": UPD,
                    "conds": CONDS, "runtime_s": time.time() - t0}
    (OUT / "summary.json").write_text(json.dumps(sm, indent=1, default=float))
    with pl.Config(tbl_rows=60, tbl_width_chars=250):
        print(pl.DataFrame(sm["table"]))


if __name__ == "__main__":
    main()
