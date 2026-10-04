"""H19 round 1b: NE14 (regime II -> III, 2026-03-24: permanent computer use, consolidation, pause tool), the
transition exception (c). H38's design (hypotheses/H38-platform-stalls/analysis/ne14.py) on the corrected tables:
the last regime-II days (#35, #36 before 03-24) vs the first regime-III days (#36 from 03-24, #37); each side is one
window with its own present population (a row on every day of the side and >= 30 active bins).

Equal-time gain g = 1 - 1/VR (H19's E1 estimator; H02's beta*J0 = g / q) in three versions (scheme/geq_r1b.py):
  raw (round-1 definition), trim (DQ8: all-present window + explained joint silences removed before the surrogates),
  scaf (H38 agent-state conditioning, the day-edge adjustment H38 used for its +0.15 -> +0.01).
E = g - mean of 200 joint N1 block-shift surrogates (drawn after the masks); Delta E = E_III - E_II with a day-bootstrap
SE (300 resamples per side). Both the round-1 tables (bins old) and the fixed tables (bins fixed); a sensitivity drops
2026-03-31 (a 513-min operator-off gap; H38's disclosed sensitivity).

Output: data/processed/H19-loop-gain-collapse/r1b/NE14/result.json
Usage: uv run python hypotheses/H19-loop-gain-collapse/analysis/r1b_ne14.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h19common as C  # noqa: E402
import geq_r1b as G  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

N_SURR, N_BOOT = 200, 300
VARS = ("raw", "trim", "scaf")


def sides():
    cal = C.calendar_nonholdout()
    d35 = cal.filter(pl.col("goal_no") == 35)["pt_date"].to_list()
    d36 = cal.filter(pl.col("goal_no") == 36)["pt_date"].to_list()
    d37 = cal.filter(pl.col("goal_no") == 37)["pt_date"].to_list()
    ii = sorted(d35 + [d for d in d36 if d < "2026-03-24"])
    iii = sorted([d for d in d36 if d >= "2026-03-24"] + d37)
    C.assert_no_holdout(ii + iii, [35] * len(ii) + [36] * len(iii))
    return ii, iii


def window(days, bins, rng):
    ab, sm = G.load_bins(days, bins)
    pres = (ab.group_by("agent").agg(pl.col("pt_date").n_unique().alias("nd"), (pl.col("state") >= 3).sum().alias("nact"),
                                     (pl.col("state") == 4).sum().alias("ntalk"))
            .filter((pl.col("nd") == len(days)) & (pl.col("nact") >= G.MIN_ACTIVE_BINS)).sort("agent"))
    agents = pres["agent"].to_list()
    talk_ok = np.array([n >= G.MIN_ACTIVE_BINS for n in pres["ntalk"].to_list()])
    S, Tk, R, day, minute, sched = G.matrices(ab, sm, days, agents)
    est = G.chunk_estimates(S, Tk, R, day, minute, sched, talk_ok, rng, n_surr=N_SURR)
    out = {"days": days, "N": len(agents), "N_talk": int(talk_ok.sum())}
    for spin, rec in est.items():
        for v in VARS:
            if v not in rec:
                continue
            r = rec[v]
            sd, _ = G.boot_se(r["st"], rng, N_BOOT)
            out[f"{spin}|{v}"] = {k: r.get(k) for k in ("g", "bJ0", "q", "VR", "null_mean", "null_sd", "E", "z", "kept_share")}
            out[f"{spin}|{v}"]["boot_sd"] = sd
    # the scaf variant has no surrogate in geq_r1b (H38 conditioning is a point adjustment); its null is the raw one
    for spin in est:
        sc = out.get(f"{spin}|scaf")
        if sc is not None and sc.get("null_mean") is None:
            sc["null_mean"] = out[f"{spin}|raw"]["null_mean"]
            sc["E"] = sc["g"] - sc["null_mean"]
    return out


def delta(A, B):
    res = {}
    for k in B:
        if "|" not in k or k not in A:
            continue
        dE = B[k]["E"] - A[k]["E"]
        dg = B[k]["g"] - A[k]["g"]
        se = float(np.hypot(A[k]["boot_sd"], B[k]["boot_sd"]))
        res[k] = {"dE": dE, "dg": dg, "d_bJ0": B[k]["bJ0"] - A[k]["bJ0"], "se": se, "lo": dE - 1.96 * se, "hi": dE + 1.96 * se}
    return res


def main():
    rng = np.random.default_rng([20261004, 14])
    ii, iii = sides()
    res = {}
    for bins in ("old", "fixed"):
        A, B = window(ii, bins, rng), window(iii, bins, rng)
        B2 = window([d for d in iii if d != "2026-03-31"], bins, rng)
        res[bins] = {"II": A, "III": B, "III_no0331": B2, "delta": delta(A, B), "delta_no0331": delta(A, B2)}
        for k, v in res[bins]["delta"].items():
            print(f"{bins:5s} {k:14s} II E={A[k]['E']:+.3f}  III E={B[k]['E']:+.3f}  dE={v['dE']:+.3f} ± {1.96 * v['se']:.3f}   "
                  f"(no 03-31: {res[bins]['delta_no0331'][k]['dE']:+.3f})", flush=True)
    od = C.BASE / "r1b/NE14"
    od.mkdir(parents=True, exist_ok=True)
    (od / "result.json").write_text(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
