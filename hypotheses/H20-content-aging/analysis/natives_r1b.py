"""H20 round 1b period-native tests (predictions in goalperiod-subhypotheses/{G51,G27,NE43}/README.md, written before
this script ran on real data). Non-holdout only (h20lib.load_period guards).

  G51   newcomers' own clock: onboarding transient K_i on the agent's own clock vs a random-start placebo; own-clock A_i
  G27   block structure (a mid-period switch) B_max = max_s [non-straddling - straddling C at matched lags], Amendment-2
        stationary null; the same test on every long / medium period as a calibration
  NE43  #51 drive withdrawal: straddling-minus-non-straddling C at matched lags at 08-05 (bookends end) and 08-21
        (nudges end), Amendment-2 stationary null and a placebo over every other day boundary

Outputs data/processed/H20-content-aging/r1b/natives_<tag>.json.
Usage: uv run python natives_r1b.py --emb bge_small [--dedupe restate] [--only g51,g27,ne43,calib]
"""
from __future__ import annotations

import argparse
import dataclasses
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h20lib as L  # noqa: E402
from h20lib import hc  # noqa: E402

import numpy as np  # noqa: E402
from scipy.stats import wilcoxon  # noqa: E402

B_NULL = 500
SEED = 20261004


def fitted(P, ndim=32):
    xbar, v, n, valid = L.states(P, "raw", ndim)
    C, npair = L.two_time(xbar, v, valid)
    Cx, cnt = L.cross_agent_C(xbar, v, valid)
    nm = L.fit_null_model(C, npair, Cx, cnt, P.wk_gap, P.T)
    Rs, Rp, _, _ = L.estimate_shapes(xbar, v, valid)
    nm = dataclasses.replace(nm, Rs=Rs, Rp=Rp)
    design = L.design_from_states(xbar, v, valid, n, ndim)
    return xbar, v, n, valid, C, npair, nm, design


def matched_diff(C, npair, k, tw_min=2, tau_max=None):
    """Lag-matched mean C of pairs straddling boundary k (0-based first day of block 2) minus non-straddling pairs.
    Pairs use days with index >= tw_min - 1 only (the kickoff day is excluded, as in A). Weights: npair."""
    T = C.shape[0]
    d1, d2 = np.triu_indices(T, 1)
    ok = (d1 >= tw_min - 1) & np.isfinite(C[d1, d2]) & (npair[d1, d2] > 0)
    if tau_max is not None:
        ok &= (d2 - d1) <= tau_max
    d1, d2 = d1[ok], d2[ok]
    c, w, lag = C[d1, d2], npair[d1, d2], d2 - d1
    st = (d1 < k) & (d2 >= k)
    num, den = 0.0, 0.0
    for t in np.unique(lag):
        s = lag == t
        a, b = s & st, s & ~st
        if a.any() and b.any():
            wt = min(a.sum(), b.sum())
            num += wt * (np.average(c[a], weights=w[a]) - np.average(c[b], weights=w[b]))
            den += wt
    return num / den if den > 0 else np.nan


def block_max(C, npair, T, s_lo=3, s_hi=None):
    """B(s) = non-straddling minus straddling at matched lags, s = first (1-based) day of block 2; max over s."""
    s_hi = T - 2 if s_hi is None else s_hi
    vals = {s: -matched_diff(C, npair, s - 1) for s in range(s_lo, s_hi + 1)}
    vals = {s: b for s, b in vals.items() if np.isfinite(b)}
    if not vals:
        return np.nan, None, vals
    s_best = max(vals, key=vals.get)
    return vals[s_best], s_best, vals


# --------------------------------------------------------------------------------------------------- block test
def block_test(g, rng, B=B_NULL):
    P = L.load_period(g)
    xbar, v, n, valid, C, npair, nm, design = fitted(P)
    T = P.T
    out = {"g": g, "T": T}
    xc, vc, okc = L.common_removed(xbar, v, valid)
    Cc, npc = L.two_time(xc, vc, okc)
    for lab, (CC, NN) in (("raw", (C, npair)), ("common_removed", (Cc, npc))):
        bm, sb, vals = block_max(CC, NN, T)
        out[lab] = {"B_max": bm, "s_hat": sb, "B_by_s": {int(k): float(x) for k, x in vals.items()}}
    nulls = {"raw": [], "common_removed": []}
    for _ in range(B):
        xb, vv, ok = L.simulate_states(nm, design, rng)
        Cs, ns = L.two_time(xb, vv, ok)
        nulls["raw"].append(block_max(Cs, ns, T)[0])
        xc2, vc2, ok2 = L.common_removed(xb, vv, ok)
        Cc2, nc2 = L.two_time(xc2, vc2, ok2)
        nulls["common_removed"].append(block_max(Cc2, nc2, T)[0])
    for lab in nulls:
        a = np.array(nulls[lab], float)
        out[lab].update(p_upper=L.p_upper(out[lab]["B_max"], a), null_q95=float(np.nanquantile(a, 0.95)),
                        null_mean=float(np.nanmean(a)))
    out["pt_dates"] = P.pt_dates
    return out


# --------------------------------------------------------------------------------------------------- NE43
def ne43(rng, B=B_NULL):
    P = L.load_period(51)
    xbar, v, n, valid, C, npair, nm, design = fitted(P)
    T = P.T
    tm = L.tau_max_for(T)
    steps = {"bookends_end_0805": "2026-08-05", "nudges_end_0821": "2026-08-21"}
    ks = {}
    for name, d in steps.items():
        k = next(i for i, x in enumerate(P.pt_dates) if x >= d)
        ks[name] = k
    xc, vc, okc = L.common_removed(xbar, v, valid)
    Cc, npc = L.two_time(xc, vc, okc)
    out = {"T": T, "steps": {nm_: P.pt_dates[k] for nm_, k in ks.items()}}
    for lab, (CC, NN) in (("raw", (C, npair)), ("common_removed", (Cc, npc))):
        res = {name: {"R": matched_diff(CC, NN, k, tau_max=tm)} for name, k in ks.items()}
        plac = [matched_diff(CC, NN, k, tau_max=tm) for k in range(6, T - 4) if k not in ks.values()]
        plac = np.array([x for x in plac if np.isfinite(x)])
        for name in res:
            res[name]["placebo_q05"] = float(np.quantile(plac, 0.05))
            res[name]["placebo_rank_low"] = float((plac <= res[name]["R"]).mean())
        res["placebo_n"] = int(plac.size)
        out[lab] = res
    nulls = {lab: {name: [] for name in ks} for lab in ("raw", "common_removed")}
    for _ in range(B):
        xb, vv, ok = L.simulate_states(nm, design, rng)
        Cs, ns = L.two_time(xb, vv, ok)
        xc2, vc2, ok2 = L.common_removed(xb, vv, ok)
        Cc2, nc2 = L.two_time(xc2, vc2, ok2)
        for name, k in ks.items():
            nulls["raw"][name].append(matched_diff(Cs, ns, k, tau_max=tm))
            nulls["common_removed"][name].append(matched_diff(Cc2, nc2, k, tau_max=tm))
    for lab in nulls:
        for name in ks:
            a = np.array(nulls[lab][name], float)
            out[lab][name].update(p_lower=L.p_lower(out[lab][name]["R"], a), null_q05=float(np.nanquantile(a, 0.05)),
                                  null_q95=float(np.nanquantile(a, 0.95)))
    return out


# --------------------------------------------------------------------------------------------------- G51 joiners
def g51_joiners(rng, n_placebo=20):
    P = L.load_period(51)
    xbar, v, n, valid = L.states(P, "raw", 32)
    Ci = L.per_agent_C(xbar, v, valid)
    T = P.T

    def K_from(i, f):
        vals = []
        for t in (1, 2, 3):
            if f + 1 + t < T:
                a, b = Ci[i, f + 1, f + 1 + t], Ci[i, f, f + t]
                if np.isfinite(a) and np.isfinite(b):
                    vals.append(a - b)
        return float(np.mean(vals)) if len(vals) >= 2 else np.nan

    joiners, inc = [], []
    for i in range(len(P.agents)):
        ks = np.flatnonzero(valid[i])
        if ks.size == 0:
            continue
        f = int(ks[0])
        if f >= 2 and ks.size >= 6:
            sub = slice(f, T)
            C1, np1 = L.two_time(xbar[i:i + 1, sub], v[i:i + 1, sub], valid[i:i + 1, sub])
            Aown, _, _ = L.aging_slope(L.entries(C1, np1, P.wk_gap[sub], tw_min=2, tau_max=L.tau_max_for(T - f)))
            joiners.append({"agent": int(P.agents[i]), "first_day": f + 1, "first_date": P.pt_dates[f], "days": int(ks.size),
                            "K_own": K_from(i, f), "A_own": float(Aown),
                            "C_own_1_2": float(Ci[i, f, f + 1]) if f + 1 < T else None,
                            "C_own_2_3": float(Ci[i, f + 1, f + 2]) if f + 2 < T else None})
        elif f <= 1 and ks.size >= 12:
            cand = [s for s in range(3, T - 4) if np.isfinite(K_from(i, s))]
            if cand:
                for s in rng.choice(cand, size=min(n_placebo, len(cand)), replace=False):
                    inc.append(K_from(i, int(s)))
    K = np.array([j["K_own"] for j in joiners], float)
    A = np.array([j["A_own"] for j in joiners], float)
    inc = np.array([x for x in inc if np.isfinite(x)])
    out = {"joiners": joiners, "n_joiners": len(joiners), "n_placebo": int(inc.size),
           "K_own_median": float(np.nanmedian(K)), "K_own_pos": int(np.nansum(K > 0)),
           "placebo_K_q90": float(np.quantile(inc, 0.9)), "placebo_K_median": float(np.median(inc)),
           "A_own_median": float(np.nanmedian(A)),
           "A_own_wilcoxon_p_greater": float(wilcoxon(A[np.isfinite(A)], alternative="greater").pvalue) if np.isfinite(A).sum() >= 5 else None}
    out["N1a"] = bool(out["K_own_pos"] >= 4 and out["K_own_median"] > out["placebo_K_q90"])
    out["N1b"] = bool(out["A_own_wilcoxon_p_greater"] is None or out["A_own_wilcoxon_p_greater"] >= 0.05 or out["A_own_median"] <= 0)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--emb", default="bge_small", choices=["bge_small", "gte_modernbert"])
    ap.add_argument("--dedupe", default="none", choices=["none", "copies", "restate"])
    ap.add_argument("--only", default="g51,g27,ne43,calib")
    args = ap.parse_args()
    L.configure(args.emb, args.dedupe, False)
    tag = L.cfg_tag()
    f = L.R1B / f"natives_{tag}.json"
    res = json.loads(f.read_text()) if f.exists() else {}
    res["config"] = tag
    if "g51" in args.only:
        res["G51_joiners"] = g51_joiners(np.random.default_rng(SEED))
        print("G51", {k: v for k, v in res["G51_joiners"].items() if k != "joiners"}, flush=True)
    if "g27" in args.only:
        res["G27_block"] = block_test(27, np.random.default_rng(SEED + 27))
        print("G27", {k: (v if not isinstance(v, dict) else {kk: vv for kk, vv in v.items() if kk != "B_by_s"})
                      for k, v in res["G27_block"].items() if k != "pt_dates"}, flush=True)
    if "ne43" in args.only:
        res["NE43"] = ne43(np.random.default_rng(SEED + 43))
        print("NE43", json.dumps(res["NE43"], default=float)[:1500], flush=True)
    if "calib" in args.only:
        cal = {}
        for g in hc.LONG + hc.MEDIUM:
            if g == 27:
                continue
            r = block_test(g, np.random.default_rng(SEED + g), B=200)
            cal[str(g)] = {lab: {k: r[lab][k] for k in ("B_max", "s_hat", "p_upper", "null_q95")} for lab in ("raw", "common_removed")}
            cal[str(g)]["T"] = r["T"]
            print("calib", g, cal[str(g)], flush=True)
        res["block_calibration"] = cal
    f.write_text(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
