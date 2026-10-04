"""H36 synthetic validation (axis F): swarms with known structural switches and known stalls, at village sampling.

Each run is 30 active days with one switch at day 15 (or none). Per run: n in {7, 12, 15}, a day length drawn from the
real calendar's mix (120-480 min) and held fixed (hours are constant for weeks in the village).

Activity: synchronous 1-min kinetic Ising (Glauber) with self-persistence, a start-up ramp, a shared slow 30-min field
and day-level jitter of the agents' fields (so day-to-day variability is not artificially small):
    P(s_i(t+1)=+1) = sigmoid(2 [h_i + r(t) + b(t) + K s_i(t) + (J0/n) sum_{j!=i} s_j(t)])
4-state behavior: active -> talk w.p. 0.3 else act; silent -> idle w.p. 0.3 else silent.
Content: per 30-min window, each agent speaks w.p. 0.6; v_i(w) = normalize(gamma g + alpha a_i + kappa u(w) + xi_i(w))
in d = 32 with anisotropic low-dimensional u and xi (spectrum exp(-k/4); H20: 5-12 effective dims).

Scenarios (card, "Synthetic validation"): S0 nothing; S1 coupling up; S2 coupling down; S3 field step at a day
boundary; S4 content goal switch; S5 mid-day field step; S6 content coupling up; S7 stalls only.
The whole real pipeline (h36lib: surrogate excesses, trailing z, families, Z_phys >= 2.0) is applied unchanged.

Usage: uv run python hypotheses/H36-reorganization-alarm/analysis/synthetic.py [--runs 30] [--workers 2]
Outputs: data/processed/H36-reorganization-alarm/synthetic/{days.parquet, summary.json}; figures/synthetic.pdf
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h36lib as L  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

D_DAYS, SWITCH = 30, 15
DIM = 32
DAYLENS = [120, 180, 240, 240, 240, 480, 480]
NS = [7, 12, 15]
BASE = dict(J0=0.2, K=0.8, h_mu=-0.15, h_sd=0.35, b_sd=0.30, jit=0.15, gamma=1.0, alpha=1.0, kappa=0.6, xi=1.2,
            p_speak=0.6)
SCEN = {
    "S0": "nothing",
    "S1": "coupling up (J0 0.2 -> 0.7)",
    "S8": "moderate coupling up (J0 0.2 -> 0.45; power-curve extension)",
    "S2": "coupling down (J0 0.7 -> 0.2)",
    "S3": "field step at a day boundary (+0.5 common, N(0,0.6) reshuffle)",
    "S4": "content goal switch at a day boundary (new g)",
    "S5": "mid-day field step (the S3 change at T/2 of day 15)",
    "S6": "content coupling up (kappa 0.6 -> 1.8)",
    "S7": "stalls only (joint silences, village-off gaps)",
}


def spectrum(d=DIM):
    # Amendment 1: total variance 1 (was 1 per dim). With gamma = alpha = 1, kappa = 0.6, xi = 1.2 the same-window
    # pairwise cosine is ~0.36 and the cross-window one ~0.26, matching the round-1 alignment level (~0.3; H24, H01).
    # The first version made window drift and noise ~30x the goal field, which no real period resembles.
    lam = np.exp(-np.arange(d) / 4.0)
    return lam / lam.sum()


def rand_unit(rng, d=DIM):
    x = rng.normal(size=d)
    return x / np.linalg.norm(x)


def sim_activity(rng, h, J0, K, T, b_sd, mid=None):
    """Returns n x T spins (+-1). mid = (t_switch, h_new) applies a field step inside the day."""
    n = h.size
    s = -np.ones(n)
    ramp = -2.0 * np.exp(-np.arange(T) / 20.0)
    b = np.repeat(rng.normal(0, b_sd, size=T // 30 + 1), 30)[:T]
    X = np.empty((n, T), np.int8)
    hh = h.copy()
    for t in range(T):
        if mid is not None and t == mid[0]:
            hh = mid[1]
        heff = hh + ramp[t] + b[t] + K * s + (J0 / n) * (s.sum() - s)
        p = 1.0 / (1.0 + np.exp(-2.0 * heff))
        s = np.where(rng.random(n) < p, 1.0, -1.0)
        X[:, t] = s
    return X


def behavior(rng, X):
    u = rng.random(X.shape)
    return np.where(X > 0, np.where(u < 0.3, 3, 2), np.where(u < 0.3, 1, 0)).astype(np.int8)


def sim_content(rng, n, W, g, A, kappa, P, gamma, alpha, xi, p_speak):
    """Returns V (n x W x d unit), M (n x W bool)."""
    sq = np.sqrt(spectrum())
    u = (rng.normal(size=(W, DIM)) * sq) @ P.T  # shared window drift, rotated anisotropic
    noise = (rng.normal(size=(n, W, DIM)) * sq) @ P.T
    V = gamma * g[None, None, :] + alpha * A[:, None, :] + kappa * u[None, :, :] + xi * noise
    V /= np.linalg.norm(V, axis=2, keepdims=True)
    M = rng.random((n, W)) < p_speak
    return V, M


def add_stalls(rng, X, T):
    """Joint silences (~5% of minutes, runs of 3-20 min) on 30% of days, plus a 60-120 min village-off gap on 15%."""
    X = X.copy()
    kind = []
    if rng.random() < 0.30:
        target = int(0.05 * T); done = 0
        while done < target:
            L_ = int(rng.integers(3, 21)); s0 = int(rng.integers(30, max(31, T - L_)))
            X[:, s0:s0 + L_] = -1; done += L_
        kind.append("js")
    if rng.random() < 0.15:
        L_ = int(rng.integers(60, 121)); s0 = int(rng.integers(30, max(31, T - L_ - 10)))
        X[:, s0:s0 + L_] = -1
        kind.append("off")
    return X, "+".join(kind)


def day_rows(rng, X, Bh, V, M, extra):
    K = (X > 0).sum(0)
    rows = {}
    m = ~L.off_runs(K)
    for tag, keep in (("", m), ("_nomask", np.ones_like(m))):
        a = L.activity_stats(X[:, keep].astype(float), Bh[:, keep], rng)
        rows.update({k + tag: v for k, v in a.items() if k in L.ACT_STATS})
        if tag == "":
            rows["act_level"] = float((X[:, keep] > 0).mean())
    c = L.content_stats(V, M, rng)
    rows.update({k: v for k, v in c.items() if k in L.CONT_STATS})
    mbar = np.where(M[..., None], V, 0).sum((0, 1)) / max(M.sum(), 1)
    rows["_mbar"] = mbar
    rows.update(extra)
    return rows


def run_one(args):
    scen, r = args
    rng = np.random.default_rng([L.SEED, int(scen[1]), r])
    p = dict(BASE)
    n = int(rng.choice(NS)); T = int(rng.choice(DAYLENS)); W = T // 30
    h = rng.normal(p["h_mu"], p["h_sd"], size=n)
    g = rand_unit(rng); A = np.vstack([rand_unit(rng) for _ in range(n)])
    P, _ = np.linalg.qr(rng.normal(size=(DIM, DIM)))
    J0 = 0.7 if scen == "S2" else p["J0"]
    kappa = p["kappa"]
    h_new = h + 0.5 + rng.normal(0, 0.6, size=n)
    out = []
    mbar_prev = None
    for d in range(D_DAYS):
        post = d >= SWITCH
        Jd, hd, gd, kd, mid = J0, h, g, kappa, None
        if scen == "S1" and post:
            Jd = 0.7
        if scen == "S8" and post:
            Jd = 0.45
        if scen == "S2" and post:
            Jd = 0.2
        if scen == "S3" and post:
            hd = h_new
        if scen == "S5":
            if d == SWITCH:
                mid = (T // 2, h_new)
            elif d > SWITCH:
                hd = h_new
        if scen == "S4" and post:
            if d == SWITCH:
                g2 = rand_unit(rng)
            gd = g2
        if scen == "S6" and post:
            kd = 1.8
        hday = hd + rng.normal(0, p["jit"], size=n)
        midday = None if mid is None else (mid[0], mid[1] + (hday - hd))
        X = sim_activity(rng, hday, Jd, p["K"], T, p["b_sd"], midday)
        stall = ""
        if scen == "S7":
            X, stall = add_stalls(rng, X, T)
        Bh = behavior(rng, X)
        V, M = sim_content(rng, n, W, gd, A, kd, P, p["gamma"], p["alpha"], p["xi"], p["p_speak"])
        row = day_rows(rng, X, Bh, V, M, {"scen": scen, "run": r, "day": d, "n": n, "T": T, "stall": stall})
        mb = row.pop("_mbar")
        row["R1_shift"] = np.nan if mbar_prev is None else float(1 - mb @ mbar_prev / (np.linalg.norm(mb) * np.linalg.norm(mbar_prev)))
        row["R3_polar"] = float(np.linalg.norm(mb))
        mbar_prev = mb
        out.append(row)
    return out


SCORES = ["Z_phys", "Z_phys_2s", "Z_or", "Z_chan", "Z_act", "Z_cont", "Z_I", "Z_chi", "Z_C", "R1", "R2", "R3", "Z_phys_nomask"]
THR = {k: (L.OR_THRESH if k == "Z_or" else L.THRESH) for k in SCORES}


def run_scores(x: pl.DataFrame) -> dict:
    Zs = {s: L.trailing_z(x[s].to_numpy().astype(float)) for s in L.ACT_STATS + L.CONT_STATS}
    Zn = {s: (L.trailing_z(x[s + "_nomask"].to_numpy().astype(float)) if s in L.ACT_STATS else Zs[s])
          for s in L.ACT_STATS + L.CONT_STATS}
    A = L.alarm_scores(Zs); An = L.alarm_scores(Zn)
    out = {k: A[k] for k in ["Z_phys", "Z_or", "Z_chan", "Z_act", "Z_cont", "Z_I", "Z_chi", "Z_C"]}
    out["Z_phys_2s"] = np.abs(A["Z_phys"])
    out["Z_phys_nomask"] = An["Z_phys"]
    out["R1"] = L.trailing_z(x["R1_shift"].to_numpy().astype(float))
    out["R2"] = L.trailing_z(x["act_level"].to_numpy().astype(float), two_sided=True)
    out["R3"] = L.trailing_z(x["R3_polar"].to_numpy().astype(float), two_sided=True)
    return out


def wmax(a, c):
    w = a[c - 1:c + 2]
    return np.nanmax(w) if np.isfinite(w).any() else np.nan


def evaluate(df: pl.DataFrame) -> dict:
    per = {}
    for scen in SCEN:
        sub = df.filter(pl.col("scen") == scen)
        ev = {k: [] for k in SCORES}; pday = {k: [] for k in SCORES}; pwin = {k: [] for k in SCORES}
        persist, stall = [], {"stall_mask": [], "stall_nomask": [], "clean_mask": [], "clean_nomask": []}
        for r in sub["run"].unique().sort().to_list():
            x = sub.filter(pl.col("run") == r).sort("day")
            sc = run_scores(x)
            pdays = ([d for d in range(L.MIN_BASE, D_DAYS) if abs(d - SWITCH) >= L.PLACEBO_DIST] if scen in ("S0", "S7")
                     else list(range(L.MIN_BASE, SWITCH - L.PLACEBO_DIST + 1)))
            pcent = [d for d in pdays if d - 1 >= L.MIN_BASE and d + 1 < D_DAYS and (d + 1 in pdays) and (d - 1 in pdays)]
            for k in SCORES:
                ev[k].append(wmax(sc[k], SWITCH))
                pday[k].extend(sc[k][pdays].tolist())
                pwin[k].extend([wmax(sc[k], c) for c in pcent])
            persist.append(float(np.nanmean(sc["Z_phys"][SWITCH + 2:SWITCH + 10] >= L.THRESH)))
            if scen == "S7":
                st = x["stall"].to_numpy()
                for d in range(L.MIN_BASE, D_DAYS):
                    key = "stall" if st[d] else "clean"
                    stall[key + "_mask"].append(bool(sc["Z_phys"][d] >= L.THRESH))
                    stall[key + "_nomask"].append(bool(sc["Z_phys_nomask"][d] >= L.THRESH))
        per[scen] = dict(ev={k: np.array(v, float) for k, v in ev.items()}, pday={k: np.array(v, float) for k, v in pday.items()},
                         pwin={k: np.array(v, float) for k, v in pwin.items()}, persist=persist, stall=stall,
                         runs=int(sub["run"].n_unique()))
    # matched-FAR thresholds from S0 placebo days (per-day FAR 0.05)
    s0 = per["S0"]["pday"]
    thr05 = {k: float(np.nanquantile(s0[k][np.isfinite(s0[k])], 0.95)) for k in SCORES}
    res = {"_thr_far05": thr05}
    rng = np.random.default_rng(L.SEED)
    for scen, P in per.items():
        e = {}
        for k in SCORES:
            evk, pd_, pw = P["ev"][k], P["pday"][k], P["pwin"][k]
            e[k] = {"hit": float(np.mean(np.nan_to_num(evk, nan=-9) >= THR[k])),
                    "far_day": float(np.mean(np.nan_to_num(pd_[np.isfinite(pd_)], nan=-9) >= THR[k])),
                    "far_win": float(np.mean(np.nan_to_num(pw[np.isfinite(pw)], nan=-9) >= THR[k])),
                    "auc": L.auc(evk, pw), "auc_ci": L.auc_ci(evk, pw, rng, 500),
                    "hit_at_far05": float(np.mean(np.nan_to_num(evk, nan=-9) >= thr05[k]))}
        res[scen] = {"desc": SCEN[scen], "runs": P["runs"], "scores": e,
                     "post_persistence_Zphys": float(np.nanmean(P["persist"]))}
        if scen == "S7":
            res[scen]["stall_far"] = {k: (float(np.mean(v)) if v else None) for k, v in P["stall"].items()}
            res[scen]["stall_n"] = {k: len(v) for k, v in P["stall"].items()}
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--runs", type=int, default=30)
    ap.add_argument("--workers", type=int, default=2)
    a = ap.parse_args()
    t0 = time.time()
    out = L.OUT / "synthetic"; out.mkdir(parents=True, exist_ok=True)
    jobs = [(s, r) for s in SCEN for r in range(a.runs)]
    rows = []
    with ProcessPoolExecutor(max_workers=min(2, a.workers)) as ex:
        for res in ex.map(run_one, jobs, chunksize=2):
            rows.extend(res)
    df = pl.DataFrame(rows)
    df.write_parquet(out / "days.parquet", compression="zstd")
    res = evaluate(df)
    res["_params"] = {"base": BASE, "days": D_DAYS, "switch": SWITCH, "runs": a.runs, "n": NS, "daylens": DAYLENS,
                      "n_surr": L.N_SURR, "thresh": L.THRESH, "elapsed_s": round(time.time() - t0, 1)}
    (out / "summary.json").write_text(json.dumps(res, indent=1))
    L.write_provenance("hypotheses/H36-reorganization-alarm/analysis/synthetic.py", [], res["_params"])
    ks = ["Z_phys", "Z_chan", "Z_or", "Z_act", "Z_cont", "R1", "R2"]
    print("scen  " + "  ".join(f"{k:>16s}" for k in ks) + "   (hit / far_win / auc / hit@far05)")
    for s in SCEN:
        e = res[s]["scores"]
        print(s, "  ".join(f"{e[k]['hit']:.2f}/{e[k]['far_win']:.2f}/{e[k]['auc']:.2f}/{e[k]['hit_at_far05']:.2f}" for k in ks),
              f"| FARday Zphys {e['Z_phys']['far_day']:.3f} nomask {e['Z_phys_nomask']['far_day']:.3f}")
    if "stall_far" in res["S7"]:
        print("S7 stall FAR", res["S7"]["stall_far"], res["S7"]["stall_n"])
    print(f"done in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
