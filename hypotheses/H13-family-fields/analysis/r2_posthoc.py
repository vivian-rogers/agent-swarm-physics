"""H13 round 2 POST HOC diagnostics (written after seeing the round-2 real results; labelled post hoc in the card).

PH1  read-out family contrast with lab main effects held fixed: the same-lab minus cross-lab jump computed within
     receiver-lab strata (fixes receiver susceptibility) and within sender-lab strata (fixes sender potency), each
     crossed with naming; paired 1-h block bootstrap, fixed-weight pooling (as C-A1).
PH2  read-out contrast without #51 same-role pairs (a shared role, not the lab, could carry the pull).
PH3  per-unit sign count of Delta_J^adj.
PH4  enculturation splits: #51 vs earlier joiners; slope without the join day.
Usage: uv run python hypotheses/H13-family-fields/analysis/r2_posthoc.py
Writes data/processed/H13-family-fields/r2/posthoc.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import r2lib as R  # noqa: E402
import r2_readout as Q  # noqa: E402

NBOOT = 400


def strat_jumps(D, y, strata, sel_base=None, nboot=NBOOT, seed=9):
    """Delta = sum_s w_s (J_same,s - J_cross,s) over strata s (array of stratum codes, -1 = drop);
    w_s = share of same-lab hop-1 rows (age < 60 s) in s. Paired block bootstrap."""
    blk, nblk = Q.blocks(D)
    h, age, same = D["h"], D["age"], D["same"]
    base = np.ones(len(h), bool) if sel_base is None else sel_base
    codes = [s for s in np.unique(strata) if s >= 0]
    C, W = {}, {}
    for s in codes:
        m = base & (strata == s)
        if ((m & same & (h == 1) & (age < 60)).sum() < 20) or ((m & ~same & (h == 1) & (age < 60)).sum() < 20):
            continue
        C[s] = (Q.cells(y, h, age, blk, nblk, m & same), Q.cells(y, h, age, blk, nblk, m & ~same))
        W[s] = float((m & same & (h == 1) & (age < 60)).sum())
    if not C:
        return None
    tot = sum(W.values())

    def stat(w):
        v = 0.0
        for s, (cs, cc) in C.items():
            a, b = Q.jump(*cs, w), Q.jump(*cc, w)
            if not (np.isfinite(a) and np.isfinite(b)):
                return np.nan
            v += W[s] / tot * (a - b)
        return v
    est = stat(None)
    used = np.unique(blk[base & np.isfinite(y) & (age < 60) & (h <= 1)])
    rng = np.random.default_rng(seed)
    dr = np.array([stat(np.bincount(rng.choice(used, len(used)), minlength=nblk).astype(float)) for _ in range(nboot)])
    return dict(est=est, se=float(np.nanstd(dr)), lo=float(np.nanpercentile(dr, 2.5)), hi=float(np.nanpercentile(dr, 97.5)),
                draws=dr, weight=tot)


def main():
    lab_of, _ = R.roster_labs()
    labs = sorted({l for l in lab_of.values() if l is not None})
    lcode = {l: k for k, l in enumerate(labs)}
    out = {"PH1": {}, "PH2": {}, "PH3": {}}
    rd = json.loads((R.R2 / "readout.json").read_text())
    units = [u for u in Q.REGIME_III if rd["units"].get(u, {}).get("eligible")]
    res = {k: {} for k in ("recv", "send", "norole")}
    for u in units:
        D = Q.load(u)
        y = Q.outcome(D, "bge", "white32")
        rl = np.array([lcode[lab_of[int(a)]] for a in D["r_agent"]])
        sl = np.array([lcode[lab_of[int(a)]] for a in D["s_agent"]])
        nm = D["ment"].astype(int)
        res["recv"][u] = strat_jumps(D, y, rl * 2 + nm)
        res["send"][u] = strat_jumps(D, y, sl * 2 + nm)
        t = R.load_stmts(u)
        role = dict(zip(t["agent"].to_list(), t["role"].to_list()))
        sr = np.array([role.get(int(a)) for a in D["s_agent"]], dtype=object)
        rr = np.array([role.get(int(a)) for a in D["r_agent"]], dtype=object)
        share = np.array([(a is not None) and (a == b) for a, b in zip(sr, rr)])
        res["norole"][u] = strat_jumps(D, y, nm, sel_base=~share)
        out["PH2"][u] = {"same_role_rows_dropped": int(share.sum())}
    for k, v in res.items():
        ok = [u for u in units if v[u] is not None]
        p = Q.pool_draws([v[u] for u in ok], [v[u]["weight"] for u in ok])
        out["PH1" if k != "norole" else "PH2"][k] = dict(pooled=p, units={u: {kk: vv for kk, vv in v[u].items() if kk != "draws"}
                                                                          for u in ok})
        print(k, p, flush=True)
    da = {u: rd["units"][u]["bge_white32"]["delta_adj"]["est"] for u in units}
    out["PH3"] = {"per_unit": da, "n_pos": int(sum(x > 0 for x in da.values())), "n": len(da),
                  "sign_p_one_sided": float(sum(__import__("math").comb(len(da), k) for k in range(sum(x > 0 for x in da.values()), len(da) + 1)) / 2 ** len(da))}
    print(out["PH3"], flush=True)
    # PH4 enculturation splits
    enc = json.loads((R.R2 / "encult.json").read_text())
    rng = np.random.default_rng(4)
    ph4 = {}
    for key in ("bge_white32", "bge_srp", "gte_white32"):
        P = enc[key]["per_joiner"]

        def sl_(a):
            a = [x for x in a if x is not None]
            return float(np.polyfit(np.arange(len(a)), a, 1)[0]) if len(a) >= 3 else np.nan
        from r2_encult import boot_mean
        g = {}
        for name, f in (("g51", lambda p: p["goal_no"] == 51), ("pre51", lambda p: p["goal_no"] != 51)):
            g[name] = {"a1": boot_mean([p["a"][0] for p in P if f(p)], rng),
                       "slope": boot_mean([sl_(p["a"]) for p in P if f(p)], rng)}
        g["slope_without_join_day"] = boot_mean([sl_(p["a"][1:]) for p in P], rng)
        g["a_by_day"] = [float(np.mean([p["a"][k] for p in P if len(p["a"]) > k and p["a"][k] is not None]))
                         for k in range(6)]
        ph4[key] = g
        print(key, g, flush=True)
    out["PH4"] = ph4
    R.dump(out, R.R2 / "posthoc.json")


if __name__ == "__main__":
    main()
