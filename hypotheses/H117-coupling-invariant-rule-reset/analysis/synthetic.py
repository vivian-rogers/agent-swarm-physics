"""H117 P0: synthetic validation of the coupling-shift test on real skeletons (axis F).

Skeleton = the before side of a real step window: eligible agents, kept minute grids, and each agent's smoothed talk rate
per (day, 30-min block). Both synthetic sides reuse that skeleton (matched hours), so any difference between sides is
planted. Dynamics: KI-5 kinetic Ising with symmetric planted J (density min(0.3, 3/(N-1)): about 3 partners per agent; J ~ N(0.8, 0.3)), self terms, a global
OU drive (tau 10 min, sd 0.5) seen with agent-specific lags 0-3 min (H90's impostor), and block-rate baselines
corrected for the expected coupling input (approximate rate matching).
Worlds: null (no change), field (after: dh_i ~ N(0, 0.5^2) - 0.3), field+drive (field plus OU sd 0.5 -> 1.0 after),
J step (after: half the pairs' J^s change by +-J_mag, J_mag in {0.6, 1.2}).
Test: Q (E1 block, all pairs) and Q-naive against the skeleton's null-world 95th percentile; F as the first stage.

Usage: uv run python hypotheses/H117-coupling-invariant-rule-reset/analysis/synthetic.py [--worlds 30] [--null 50]
"""
from __future__ import annotations

import argparse
import json
import zlib
import sys
import time
from concurrent.futures import ProcessPoolExecutor
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scheme"))
import ki_talk as K  # noqa: E402

OUT = K.ROOT / "data/processed/H117-coupling-invariant-rule-reset/synthetic"
SKELETONS = {
    "NE17": (["2026-04-10", "2026-04-13"], ["2026-04-14", "2026-04-15"]),
    "NE38": (["2026-07-27", "2026-07-28"], ["2026-07-29", "2026-07-30"]),
    "NE06": (["2025-11-18", "2025-11-19"], ["2025-11-20", "2025-11-21"]),
    "NE38k3": (["2026-07-24", "2026-07-27", "2026-07-28"], ["2026-07-29", "2026-07-30", "2026-07-31"]),
}


def skeleton(name: str) -> dict:
    before, after = SKELETONS[name]
    sp = K.day_spins(before + after)
    ag = K.eligible(sp, [before, after])
    st = K.stack(sp, before, ag)
    prof = []
    for d, S, mins, t0 in st:
        blk = mins // K.BLOCK_MIN
        ub, inv = np.unique(blk, return_inverse=True)
        P = np.zeros((len(ag), len(ub)))
        for n in range(len(ag)):
            k = np.bincount(inv, (S[n] > 0).astype(float), len(ub))
            c = np.bincount(inv, None, len(ub))
            P[n] = (k + 0.25) / (c + 1.0)
        prof.append((mins, inv, P))
    return {"agents": ag, "prof": prof}


def ou(T, tau, sd, rng):
    a = np.exp(-1.0 / tau)
    x = np.zeros(T)
    e = rng.normal(0, sd * np.sqrt(1 - a * a), T)
    x[0] = rng.normal(0, sd)
    for t in range(1, T):
        x[t] = a * x[t - 1] + e[t]
    return x


def simulate_side(sk, J, dh, drive_sd, lags, rng, Kself=0.2, Kbox=0.3, off=None):
    N = len(sk["agents"])
    off = np.zeros(N) if off is None else off
    out = []
    for di, (mins, inv, P) in enumerate(sk["prof"]):
        T = len(mins)
        lp = np.log(P / (1 - P))
        # expected coupling input at the block rate: m+1 ~ 2p
        base = lp - (J @ (2 * P)) - Kself * 2 * P - Kbox * 2 * P
        f = ou(T + 4, 10.0, drive_sd, rng)
        S = -np.ones((N, T), np.int8)
        S[:, 0] = np.where(rng.random(N) < P[:, inv[0]], 1, -1)
        csum = np.zeros((N, T + 1))
        csum[:, 1] = S[:, 0]
        for t in range(T - 1):
            lo = max(0, t - K.BOX + 1)
            m = (csum[:, t + 1] - csum[:, lo]) / (t + 1 - lo)
            fl = f[t + 4 - lags]
            eta = base[:, inv[t + 1]] + off + dh + fl + Kself * (S[:, t] + 1) + Kbox * (m + 1) + J @ (m + 1)
            S[:, t + 1] = np.where(rng.random(N) < 1 / (1 + np.exp(-eta)), 1, -1)
            csum[:, t + 2] = csum[:, t + 1] + S[:, t + 1]
        out.append((str(di), S, mins, None))
    return out


def calibrate(sk, J, lags, rng, iters=8, damp=0.6):
    """Per-agent offsets so the null-side talk rate matches the skeleton's real rate (self-excitation and the OU
    drive raise rates beyond the linear correction)."""
    N = len(sk["agents"])
    target = np.array([np.mean(np.concatenate([P[n, inv] for mins, inv, P in sk["prof"]])) for n in range(N)])
    off = np.zeros(N)
    for _ in range(iters):
        s = simulate_side(sk, J, np.zeros(N), 0.5, lags, rng, off=off)
        r = np.array([np.mean(np.concatenate([(x[1][n] > 0) for x in s])) for n in range(N)])
        r = np.clip(r, 1e-3, 1 - 1e-3)
        off += damp * (np.log(target / (1 - target)) - np.log(r / (1 - r)))
    return off


def planted_J(N, rng):
    J = np.zeros((N, N))
    iu = np.triu_indices(N, 1)
    on = rng.random(len(iu[0])) < min(0.3, 3.0 / max(N - 1, 1))   # ~3 partners per agent at any N
    v = np.where(on, rng.normal(0.8, 0.3, len(on)), 0.0)
    J[iu] = v
    return J + J.T


def one_world(args):
    name, kind, seed, jmag = args
    sk = SK[name]
    rng = np.random.default_rng(seed)
    N = len(sk["agents"])
    J = planted_J(N, rng)
    lags = rng.integers(0, 4, N)
    dh = np.zeros(N)
    sd_a = 0.5
    Ja = J.copy()
    if kind in ("field", "field_drive"):
        dh = rng.normal(0, 0.5, N) - 0.3
        if kind == "field_drive":
            sd_a = 1.0
    if kind == "jscale":
        Ja = J * jmag            # global coupling change (attention): every coupling scaled by jmag
    if kind == "jstep":
        iu = np.triu_indices(N, 1)
        ch = rng.random(len(iu[0])) < 0.5
        delta = np.where(ch, rng.choice([-1.0, 1.0], len(ch)) * jmag, 0.0)
        D = np.zeros((N, N)); D[iu] = delta
        Ja = J + D + D.T
    off = calibrate(sk, J, lags, rng)
    sb = simulate_side(sk, J, np.zeros(N), 0.5, lags, rng, off=off)
    sa = simulate_side(sk, Ja, dh, sd_a, lags, rng, off=off)
    res = {"skeleton": name, "kind": kind, "seed": seed, "jmag": jmag, "N": N}
    pm = ~np.eye(N, dtype=bool)
    for fields in ("block", "naive"):
        Jb, SEb, _ = K.fit_e1_full(sb, fields, lam=LAM)
        Jaf, SEa, _ = K.fit_e1_full(sa, fields, lam=LAM)
        q = K.q_stats(Jaf, SEa, Jb, SEb, pm)
        res[f"Q_{fields}"] = q["Q"]; res[f"DF_{fields}"] = q["DF"]
        if fields == "block" and kind == "jstep":
            Js_true = (Ja - J)[np.triu_indices(N, 1)]
            Jsh = ((Jaf + Jaf.T) / 2 - (Jb + Jb.T) / 2)[np.triu_indices(N, 1)]
            res["corr_dJ"] = float(np.corrcoef(Js_true, Jsh)[0, 1]) if Js_true.std() > 0 else np.nan
    bb, sbb = K.fit_e1_mf(sb); ba, sba = K.fit_e1_mf(sa)
    res["Q_mf"] = float(np.nanmean((ba - bb) ** 2 / (sba ** 2 + sbb ** 2)))
    res["dmf"] = float(np.nanmean(ba - bb))
    hb, seb = K.field_logit(sb); ha, sea = K.field_logit(sa)
    res["F"] = K.f_stat(ha, sea, hb, seb)
    res["talk_rate_b"] = float(np.mean([(s[1] > 0).mean() for s in sb]))
    return res


SK = {}
LAM = K.LAM


def _init(names, lam=None):
    global LAM
    if lam is not None:
        LAM = lam
    for n in names:
        SK[n] = skeleton(n)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", type=int, default=30)
    ap.add_argument("--null", type=int, default=50)
    ap.add_argument("--skeletons", default="NE17,NE38,NE06")
    ap.add_argument("--lam", type=float, default=K.LAM)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    names = a.skeletons.split(",")
    jobs = []
    for name in names:
        s = zlib.crc32(name.encode()) % 10_000
        jobs += [(name, "null", 1000 * s + i, 0.0) for i in range(a.null)]
        for kind in ("field", "field_drive"):
            jobs += [(name, kind, 2000 * s + 7 * i + len(kind), 0.0) for i in range(a.worlds)]
        for jm in (0.6, 1.2):
            jobs += [(name, "jstep", 3000 * s + 11 * i + int(10 * jm), jm) for i in range(a.worlds)]
        for jm in (0.0, 2.0):
            jobs += [(name, "jscale", 4000 * s + 13 * i + int(10 * jm), jm) for i in range(a.worlds)]
    t = time.time()
    with ProcessPoolExecutor(2, initializer=_init, initargs=(names, a.lam)) as ex:
        rows = list(ex.map(one_world, jobs, chunksize=4))
    df = pl.DataFrame(rows, infer_schema_length=None)
    OUT.mkdir(parents=True, exist_ok=True)
    df.write_parquet(OUT / f"p0_worlds{a.tag}.parquet")
    summ = {}
    for name in names:
        d = df.filter(pl.col("skeleton") == name)
        nul = d.filter(pl.col("kind") == "null")
        thr = {f: float(np.quantile(nul[f"Q_{f}"].to_numpy(), 0.95)) for f in ("block", "naive", "mf")}
        fthr = float(np.quantile(nul["F"].to_numpy(), 0.90))
        s = {"N": int(d["N"][0]), "talk_rate": float(nul["talk_rate_b"].mean()), "Q95_null": thr,
             "Q_null_median": float(nul["Q_block"].median()), "F90_null": fthr}
        for kind, jm in (("field", 0.0), ("field_drive", 0.0), ("jstep", 0.6), ("jstep", 1.2), ("jscale", 0.0),
                         ("jscale", 2.0)):
            w = d.filter((pl.col("kind") == kind) & (pl.col("jmag") == jm))
            key = kind if kind not in ("jstep", "jscale") else f"{kind}_{jm}"
            s[key] = {"rej_block": float((w["Q_block"] > thr["block"]).mean()),
                      "rej_naive": float((w["Q_naive"] > thr["naive"]).mean()),
                      "rej_mf": float((w["Q_mf"] > thr["mf"]).mean()),
                      "F_rej": float((w["F"] > fthr).mean()),
                      "Q_block_median": float(w["Q_block"].median())}
            if kind == "jstep":
                s[key]["corr_dJ"] = float(w["corr_dJ"].median())
        summ[name] = s
    summ["_meta"] = {"worlds": a.worlds, "null": a.null, "lam": a.lam, "seconds": round(time.time() - t, 1)}
    (OUT / f"p0_summary{a.tag}.json").write_text(json.dumps(summ, indent=1))
    print(json.dumps(summ, indent=1))


if __name__ == "__main__":
    main()
