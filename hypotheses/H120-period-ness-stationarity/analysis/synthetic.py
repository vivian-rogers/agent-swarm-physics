"""H120 synthetic validation (axis F; run before any real-data fit): kinetic Ising worlds on the real skeletons
(core agents x trimmed minutes x kept days, weekdays, session lengths) of each window.

Settings (card N4): S0 stationary + day-level field noise (sd 0.3 on h); S1 = S0 + weekday fields (sd 0.3 per agent x
weekday) + a session-length field (psi_i ~ N(0, 0.3) on standardized length); S2 linear J drift with total change
dJ ~ N(0, 0.3^2) per entry (the drift that matters); S3 half of S2; S4 a step of the S2 size at the window's unit
boundary (G38: 04-14; 51main: 08-05; others: the middle day).
Generating J: diagonal 2.0 (activity) / 0.5 (talk); off-diagonal N(0, 0.3^2); h_i set by mean field from each core
agent's marginal spin rate (a skeleton descriptive, not an outcome).

Usage: uv run python hypotheses/H120-period-ness-stationarity/analysis/synthetic.py [--worlds 60] [--perm 200]
Writes data/processed/H120-period-ness-stationarity/synthetic/summary.json
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h120lib as L  # noqa: E402

WINDOWS = ("G38", "38a", "51main", "4c", "6b", "8", "13", "19a", "27", "51g")
BOUNDARY = {"G38": "2026-04-14", "51main": "2026-08-05"}
JII = {"act": 2.0, "talk": 0.5}


def logit(p):
    p = np.clip(p, 1e-3, 1 - 1e-3)
    return np.log(p / (1 - p))


def simulate(win, setting, rng):
    S_real = win["S"]
    D, N = len(S_real), S_real[0].shape[1]
    m = np.clip(np.concatenate(S_real).mean(0), 0.01, 0.99)
    J0 = rng.normal(0, 0.3, (N, N))
    np.fill_diagonal(J0, JII[win["channel"]])
    h0 = logit(m) - J0 @ m
    dJ = rng.normal(0, 0.3, (N, N))
    wd = win["weekday"]
    Lz = (win["trim_len"] - win["trim_len"].mean()) / (win["trim_len"].std() or 1.0)
    phi = rng.normal(0, 0.3, (N, 8)) if setting == "S1" else np.zeros((N, 8))
    psi = rng.normal(0, 0.3, N) if setting == "S1" else np.zeros(N)
    if win["name"] in BOUNDARY and BOUNDARY[win["name"]] in win["days"]:
        b = win["days"].index(BOUNDARY[win["name"]])
    else:
        b = D // 2
    out = []
    for d in range(D):
        f = d / max(D - 1, 1) - 0.5
        J = J0.copy()
        if setting == "S2":
            J = J0 + f * dJ
        elif setting == "S3":
            J = J0 + 0.5 * f * dJ
        elif setting == "S4":
            J = J0 + (0.5 if d >= b else -0.5) * dJ
        h = h0 + rng.normal(0, 0.3, N) + phi[:, wd[d]] + psi * Lz[d]
        T = len(S_real[d])
        s = np.zeros((T, N))
        s[0] = rng.random(N) < m
        for t in range(1, T):
            s[t] = rng.random(N) < L._sig(h + J @ s[t - 1])
        out.append(s)
    w2 = dict(win)
    w2["S"] = out
    return w2


def tests(win, rng, n_perm, n_perm_ep, do_ep=True):
    des = L.design(win)
    F = L.fit(des)
    n = len(des["days"])
    nulls = L.random_splits(n, n_perm, rng)
    t1 = L.perm_test(F, L.contiguous_tau(n), nulls)
    perms = [L.trend_tau(n)[rng.permutation(n)] for _ in range(n_perm)]
    t2 = L.perm_test(F, L.trend_tau(n), perms)
    res = {"T1": t1["p"], "T2": t2["p"], "R1": t1["R"]}
    if do_ep:
        stats, block = L.ep_day_stats(win)
        t3 = L.ep_split_test(stats, block, list(range(n // 2)), nulls[:n_perm_ep], n)
        res["T3"] = t3["p"]
    if win["name"] in BOUNDARY and BOUNDARY[win["name"]] in win["days"]:
        res["brank"] = L.boundary_rank(F, n, win["days"].index(BOUNDARY[win["name"]]))["rank_frac"]
    return res


def run(worlds=60, n_perm=200, n_perm_ep=100, seed=20261004, windows=WINDOWS):
    rng = np.random.default_rng(seed)
    summ = {}
    for wname in windows:
        for ch in ("act", "talk"):
            win = L.load_window(wname, ch)
            big = len(win["core"]) > 15
            nw = 20 if big else worlds
            npe = 40 if big else n_perm_ep
            npm = 100 if big else n_perm
            for setting in ("S0", "S1", "S2", "S3", "S4"):
                recs = []
                for _ in range(nw):
                    recs.append(tests(simulate(win, setting, rng), rng, npm, npe))
                r = {k: float(np.mean([x[k] < 0.05 for x in recs])) for k in ("T1", "T2", "T3")}
                r["T1orT2"] = float(np.mean([(x["T1"] < 0.05) or (x["T2"] < 0.05) for x in recs]))
                hol = [L.holm([x["T1"], x["T2"], x["T3"]]) for x in recs]
                r["any_holm3"] = float(np.mean([np.any(h < 0.05) for h in hol]))
                r["R1_median"] = float(np.median([x["R1"] for x in recs]))
                if "brank" in recs[0]:
                    r["boundary_top10"] = float(np.mean([x["brank"] <= 0.10 for x in recs]))
                r["worlds"] = nw
                r["perm"] = npm
                summ[f"{wname}|{ch}|{setting}"] = r
                print(wname, ch, setting, r, flush=True)
            out = L.DATA / "synthetic"
            out.mkdir(parents=True, exist_ok=True)
            (out / "summary.json").write_text(json.dumps(summ, indent=1))
    return summ


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--worlds", type=int, default=60)
    ap.add_argument("--perm", type=int, default=200)
    ap.add_argument("--windows", nargs="*", default=list(WINDOWS))
    a = ap.parse_args()
    run(a.worlds, a.perm, windows=a.windows)
