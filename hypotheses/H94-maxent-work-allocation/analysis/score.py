"""H94: score P1-P8 and the kill from results/G<NN>.json; write the estimates rows (--write-estimates).
Scoring follows amendment A1: P1/P3 against the run-preserving persistence floor; P7/P8 against the persistence null.
Groups (card, fixed before data): own-artifact units 39, 42a, 42b, 44a, 44b, 51a-51l; shared units the rest.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from scipy.stats import mannwhitneyu

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DATA = ROOT / "data/processed/H94-maxent-work-allocation"
PERIODS = [30, 31, 33, 35, 36, 37, 38, 39, 40, 41, 42, 44, 51]
NATIVE = {35, 40, 44}


def units():
    out = {}
    for g in PERIODS:
        p = DATA / "results" / f"G{g:02d}.json"
        if p.exists():
            for u, v in json.loads(p.read_text())["units"].items():
                out[u] = {**v, "g": g}
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--write-estimates", action="store_true")
    a = ap.parse_args()
    U = units()
    T = {u: v for u, v in U.items() if v.get("testable")}
    own = {u: v for u, v in T.items() if v["own_unit"]}
    sh = {u: v for u, v in T.items() if not v["own_unit"]}
    sc = {"testable": list(T), "own": list(own), "shared": list(sh)}
    ex = {u: v["D1"] - v["pfloor1"] for u, v in T.items()}
    sc["P1"] = {"excess_bits": ex, "n_ge_0.5": sum(x >= 0.5 for x in ex.values()), "n": len(ex),
                "verdict": "supported" if all(x >= 0.5 for x in ex.values()) else "failed",
                "patefield_excess": {u: v["D1"] - v["floor1"] for u, v in T.items()}}
    os_ = {u: v["own_share"] for u, v in T.items()}
    a1 = sum(os_[u] >= 0.5 for u in own) >= 2 / 3 * len(own)
    a2 = sum(os_[u] < 0.5 for u in sh) >= 2 / 3 * len(sh)
    sc["P2"] = {"own_share": os_, "own_ge_half": sum(os_[u] >= 0.5 for u in own), "shared_lt_half": sum(os_[u] < 0.5 for u in sh),
                "verdict": "supported" if (a1 and a2) else ("mixed" if (a1 or a2) else "failed")}
    res = {u: (min(v["D3"], v["D2"]) - v["pfloor3"]) / v["D1"] for u, v in T.items()}
    sc["P3"] = {"resid_frac": res, "n_le_0.2": sum(x <= 0.2 for x in res.values()), "n": len(res),
                "verdict": "supported" if sum(x <= 0.2 for x in res.values()) >= len(res) / 2 else "failed"}
    lo = [v["lam_own"] for v in own.values()]
    ls = [v["lam_own"] for v in sh.values()]
    mw = mannwhitneyu(lo, ls, alternative="greater")
    sc["P4"] = {"lam_own": {u: v["lam_own"] for u, v in T.items()}, "ci": {u: [v.get("lam_own_lo"), v.get("lam_own_hi")] for u, v in T.items()},
                "median_own": float(np.median(lo)), "median_shared": float(np.median(ls)), "p": float(mw.pvalue),
                "verdict": "supported" if mw.pvalue < 0.05 else "failed"}
    k = {u: (v.get("kappa") or {}).get("kappa") for u, v in T.items()}
    band = {u: (v.get("kappa") or {}).get("be_band") for u, v in T.items()}
    cls = {}
    for u in T:
        if k[u] is None or not band[u]:
            cls[u] = None
        else:
            cls[u] = "above_BE" if k[u] > band[u][1] else ("below_BE" if k[u] < band[u][0] else "BE")
    b1 = sum((k[u] or 0) >= 1 for u in sh) >= 2 / 3 * len(sh)
    b2 = sum(k[u] is not None and k[u] < 1 for u in own) >= 2 / 3 * len(own)
    sc["P5"] = {"kappa": k, "class": cls, "shared_ge1": sum((k[u] or 0) >= 1 for u in sh), "own_lt1": sum(k[u] is not None and k[u] < 1 for u in own),
                "verdict": "supported" if (b1 and b2) else ("mixed" if (b1 or b2) else "failed")}
    knn = {u: (v.get("kappa_no_named") or {}).get("kappa") for u, v in T.items()}
    base = [u for u in sh if (k[u] or 0) >= 1 and T[u]["named_repos"] > 0]
    drop = [u for u in base if knn[u] is not None and knn[u] < 1]
    sc["P6"] = {"base": base, "drops_below_1": drop, "kappa_no_named": knn,
                "verdict": "supported" if base and len(drop) >= len(base) / 2 else "failed"}
    s7 = {}
    for u, v in T.items():
        o = v["sig_M2"]["singletons_obs"]
        p2 = v["sig_M2"].get("singletons_persist")
        p1 = v["sig_M1"].get("singletons_persist")
        s7[u] = {"obs": o, "M2": p2, "M1": p1,
                 "M2_ok": o > 0 and p2 is not None and abs(p2 - o) <= 0.25 * o,
                 "M1_worse": p1 is not None and p2 is not None and abs(p1 - o) > abs(p2 - o)}
    n7 = sum(x["M2_ok"] and x["M1_worse"] for x in s7.values())
    sc["P7"] = {"singletons": s7, "n_ok": n7, "n": len(s7), "verdict": "supported" if n7 >= len(s7) / 2 else "failed"}
    br = {u: v["sig_M2"].get("breadth_ratio_persist") for u, v in T.items()}
    sc["P8"] = {"breadth_persist": br, "analytic": {u: v["sig_M2"]["breadth_ratio"] for u, v in T.items()},
                "n_lt_0.8": sum(x is not None and x < 0.8 for x in br.values()), "n": len(br),
                "verdict": "supported" if sum(x is not None and x < 0.8 for x in br.values()) >= 2 / 3 * len(br) else "failed"}
    sc["kill"] = {"met": all(x > 0.5 for x in res.values())}
    sc["persist_resid_frac"] = {u: (min(v["D3"], v["D2"]) - v["pfloor3"]) / v["D1"] for u, v in T.items()}
    lam = [v["lam_own"] for u, v in T.items() if u.startswith("51")]
    sc["G51_lambda_cv"] = float(np.std(lam) / np.mean(lam)) if lam else None
    (DATA / "results" / "score.json").write_text(json.dumps(sc, indent=1, default=float))
    for kk in ("P1", "P2", "P3", "P4", "P5", "P6", "P7", "P8"):
        print(kk, sc[kk]["verdict"])
    print("kill", sc["kill"], "G51 lambda CV", sc["G51_lambda_cv"])
    if a.write_estimates:
        write_rows(U)


def write_rows(U):
    sys.path.insert(0, str(ROOT / "infra/shared"))
    import estimates as E
    rows = []
    for u, v in U.items():
        if "D1" not in v:
            continue
        g = v["g"]
        role = "native" if g in NATIVE else "replication"
        src = f"data/processed/H94-maxent-work-allocation/results/G{g:02d}.json"
        st = "ok" if v.get("testable") else "underpowered"
        base = {"period_unit": u, "goal_no": g, "channel": "project (work)", "role": role, "status": st, "source": src,
                "n": v["N"], "n_kind": "work quanta (agent x 30-min window x repo)"}
        rows.append({**base, "statistic": "maxent_alloc_D1_bits", "estimate": v["D1"], "ci_kind": "none",
                     "method": "KL(observed || independence max-ent with row and column margins), bits per quantum",
                     "null": f"run-preserving persistence floor {v.get('pfloor1'):.3f}" if v.get("pfloor1") is not None else None})
        if v.get("testable"):
            rows.append({**base, "statistic": "maxent_alloc_resid_bits", "estimate": min(v["D3"], v["D2"]) - v["pfloor3"],
                         "ci_kind": "none", "method": "KL after margins + ownership (+ room in two-room units) minus the "
                         "run-preserving persistence floor, bits per quantum", "null": "max-ent given constraints (= 0)"})
            rows.append({**base, "statistic": "maxent_ownership_share", "estimate": v["own_share"], "ci_kind": "none",
                         "method": "(D1 - D2)/D1: share of I(agent; repo) carried by the ownership constraint", "null": None})
            rows.append({**base, "statistic": "maxent_lambda_own_nats", "estimate": v["lam_own"], "ci_lo": v.get("lam_own_lo"),
                         "ci_hi": v.get("lam_own_hi"), "ci_level": 0.95, "ci_kind": "percentile",
                         "method": "ownership price (log-linear max-ent with margins + ownership); agent-block bootstrap, 200 "
                                   "draws; capped at 20 (quasi-separation)", "null": "0 (no ownership preference)"})
        kap = v.get("kappa")
        kap = kap if isinstance(kap, dict) else {"kappa": kap, "be_band": None, "N": None}
        if kap.get("kappa") is not None:
            band = kap.get("be_band") or [None, None]
            rows.append({**base, "statistic": "maxent_kappa_concentration", "estimate": kap["kappa"], "ci_kind": "none",
                         "n": kap.get("N"), "n_kind": "work episodes (runs)",
                         "method": "kappa = (H_MB - H_obs)/(H_MB - H_BE) on work episodes per repo at fixed K and N",
                         "null": f"BE (neutral Polya) 95% band [{band[0]:.2f}, {band[1]:.2f}]" if band[0] is not None else "BE = 1"})
            if kap.get("N") is None:
                rows[-1]["n"] = None
    E.write_estimates(rows, hypothesis="H94")
    print(len(rows), "estimate rows")


if __name__ == "__main__":
    main()
