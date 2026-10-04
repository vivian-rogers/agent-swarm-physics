"""H28 post hoc checks (written 2026-10-04 AFTER the round-1 real-data run; labelled post hoc everywhere).

1. Short-lag asymmetry. The round-1 lead placebo (links posted in the next 60 min) came out larger than kappa. Is there
   a directed component at short lags? Model: indicators for a visible link to X in the last 0-15 min and 15-60 min,
   and for a link to X that i will receive posted in the next 0-15 min and 15-60 min, plus Eold and the primary
   controls (agent + project + day FE). Statistic: b_lag15 - b_lead15 (cluster-robust), and z of b_lag15 against the
   link time-shift null.
2. Action-only latency (NE09). Excess arrivals after link posting using computer-use action touches only (no chat
   touches), to see whether the fast pre-NE09 response is carried by chat replies.

  uv run python hypotheses/H28-links-spread-herding/analysis/posthoc.py [--goals ...] [--shifts 49]
"""
from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h28core as hc  # noqa: E402
from h28lib import ALL_PERIODS, OUT, gname  # noqa: E402

SPEC = ["L15", "L1560", "Eold", "F15", "F1560"] + hc.CONTROLS


def sharp_features(P, R, link_t=None, t_vis=None):
    L, E = P["links"], P["expo"]
    K = P["K"]
    lt = L["t"] if link_t is None else link_t
    tv = E["t_vis"] if t_vis is None else t_vis
    lid = E["lid"]
    x = L["x"][lid]
    m = (x >= 0) & (tv >= 0)
    key = E["ri"][m] * K + x[m]
    base = (R["ai"] * K + R["x"]) * hc.BIG + R["T"]
    cv = np.sort(key * hc.BIG + tv[m])
    cp = np.sort(key * hc.BIG + lt[lid[m]])
    F = {}
    F["L15"] = (hc._count(cv, base - hc.W15, base) > 0).astype(float)
    F["L1560"] = (hc._count(cv, base - hc.W60, base - hc.W15) > 0).astype(float)
    F["Eold"] = np.log1p(hc._count(cv, base - hc.W240, base - hc.W60))
    right = lambda lo, hi: np.searchsorted(cp, base + hi, "right") - np.searchsorted(cp, base + lo, "right")  # noqa: E731
    F["F15"] = (right(0, hc.W15) > 0).astype(float)
    F["F1560"] = (right(hc.W15, hc.W60) > 0).astype(float)
    return F


def run(g, shifts=49, seed=4028):
    P = hc.load_period(OUT / gname(g))
    R, B, G = hc.build_rows(P)
    F = sharp_features(P, R)
    res = hc.fit(R, F, SPEC)
    names = res["names"]
    i, j = names.index("L15"), names.index("F15")
    d = res["beta"][i] - res["beta"][j]
    vd = res["V"][i, i] + res["V"][j, j] - 2 * res["V"][i, j]
    out = dict(goal=g, **{f"b_{n}": float(res["beta"][names.index(n)]) for n in ("L15", "L1560", "F15", "F1560")},
               **{f"se_{n}": float(res["se"][names.index(n)]) for n in ("L15", "L1560", "F15", "F1560")},
               diff15=float(d), se_diff15=float(np.sqrt(vd)), p_diff15=float(norm.sf(d / np.sqrt(vd))))
    rng = np.random.default_rng(seed + g)
    null = []
    for _ in range(shifts):
        lt, tv = hc.shift_links(P, rng)
        r0 = hc.fit(R, sharp_features(P, R, lt, tv), SPEC)
        null.append(r0["beta"][r0["names"].index("L15")])
    null = np.array([v for v in null if np.isfinite(v)])
    out.update(null15_mean=float(null.mean()), null15_sd=float(null.std(ddof=1)),
               z15=float((out["b_L15"] - null.mean()) / null.std(ddof=1)))
    # action-only latency
    Pa = copy.copy(P)
    T = P["touches"]
    ma = T["src"] == 0
    Pa["touches"] = {k: v[ma] for k, v in T.items()}
    out["latency_action"] = hc.latency(Pa, shifts=19)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--goals", type=int, nargs="*", default=ALL_PERIODS)
    ap.add_argument("--shifts", type=int, default=49)
    a = ap.parse_args()
    path = OUT / "posthoc_round1.json"
    allres = json.loads(path.read_text()) if path.exists() else {}
    for g in a.goals:
        r = run(g, shifts=a.shifts if g != 51 else min(a.shifts, 19))
        allres[str(g)] = r
        print(json.dumps({k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items() if k != "latency_action"},
                         default=float), "lat_action", r["latency_action"]["median_excess_lag"], flush=True)
        path.write_text(json.dumps(allres, indent=1, default=float))


if __name__ == "__main__":
    main()
