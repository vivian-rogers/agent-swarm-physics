"""H118 round 1 (exploratory, non-holdout): replica overlap of the two rooms after the NE15 fork and after every
two-room kickoff; code overlap of the RPG forks.

Usage: uv run python hypotheses/H118-forked-rpg-replicas/analysis/run.py [--boot 300] [--relabel 500]
Writes data/processed/H118-forked-rpg-replicas/results/results.json (+ per-period tables) and per-period estimates rows
(write_estimates) unless --no-estimates.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import h118lib as L  # noqa: E402

sys.path.insert(0, str(L.ROOT / "infra/shared"))
from common import git_commit  # noqa: E402

PERIODS = ("35", "36", "36a", "37", "38", "39", "41", "42", "44")
MODELS = ("bge_small", "gte_modernbert")
RES = L.DATA / "results"


def summarize_boot(bs, nd):
    out = {"q_eq_d_ci": {}, "M_d_ci": {}}
    for d in range(1, nd + 1):
        out["q_eq_d_ci"][d] = L.ci([b["q_eq_d"].get(d, np.nan) for b in bs])
        out["M_d_ci"][d] = L.ci([b["M_d"].get(d, np.nan) for b in bs])
    out["q_late_ci"] = L.ci([b["q_late"] for b in bs])
    out["q_all_ci"] = L.ci([b["q_all"] for b in bs])
    out["tau_ci"] = L.ci([b["tau"] for b in bs])
    out["M_late_ci"] = L.ci([b["M_late"] for b in bs])
    return out


def rebin2(pdat):
    p = dict(pdat)
    hr2 = p["hour"] // 2
    p["bin"] = p["day"] * 100 + hr2
    # mid-time of the 2-h bin
    p["t"] = p["t"] - (p["hour"] - 2 * hr2) + 0.5
    return p


def period_centre(pdat):
    p = dict(pdat)
    p["X"] = p["X"] - p["X"].mean(0)
    return p


def analyse(pdat, boot, relabel, rng, kinds=("agent_bin", "stmt_bin")):
    r = L.overlap_stats(pdat)
    ft = L.fit_tau(r["t"], r["q_bin"], r["w_bin"])
    rel = L.relabel_ref(pdat, R=relabel, rng=rng)
    out = {"q_eq_d": r["q_eq_d"], "q_lag_d": r["q_lag_d"], "M_d": r["M_d"], "q_late": r["q_late"], "q_all": r["q_all"],
           "M_late": r["M_late"], "tau": ft, "q_rel_d": rel["q_rel_d"], "q_rel_late": rel["q_rel_late"],
           "n_days": pdat["n_days"], "n_bins_usable": int(len(r["bins"])),
           "hourly": {"t": r["t"].tolist(), "q": r["q_bin"].tolist(), "w": r["w_bin"].tolist(),
                      "bins": r["bins"].tolist()},
           "n_stmt": int(len(pdat["agent"])),
           "n_agents": {str(rm): int(len(np.unique(pdat["agent"][pdat["room"] == rm]))) for rm in (2, 3)}}
    for k in kinds:
        out["boot_" + k] = summarize_boot(L.bootstrap(pdat, kind=k, B=boot, rng=rng), pdat["n_days"])
    return out


def code_analysis():
    ch = pl.read_parquet(L.DATA / "code_hourly.parquet").sort("t")
    from scipy.stats import hypergeom
    rows = []
    for r in ch.iter_rows(named=True):
        rec = {"pt_date": r["pt_date"], "hour": r["hour"], "kind": r["kind"], "t": r["t"].isoformat()}
        for fam in ("files", "src", "functions"):
            ub = np.array([c == "1" for c in r[f"{fam}_unch_best_bits"]])
            ur = np.array([c == "1" for c in r[f"{fam}_unch_rest_bits"]])
            K, kb, kr, kbr = len(ub), int(ub.sum()), int(ur.sum()), int((ub & ur).sum())
            p_hot = float(hypergeom.sf(kbr - 1, K, kb, kr)) if K else np.nan
            rec |= {f"{fam}_q": r[f"{fam}_q"], f"{fam}_cA": r[f"{fam}_cA"], f"{fam}_cB": r[f"{fam}_cB"],
                    f"{fam}_q_ind": r[f"{fam}_cA"] * r[f"{fam}_cB"],
                    f"{fam}_X": r[f"{fam}_q"] - r[f"{fam}_cA"] * r[f"{fam}_cB"],
                    f"{fam}_X_unch": r[f"{fam}_both_unch"] - r[f"{fam}_cA"] * r[f"{fam}_cB"],
                    f"{fam}_X_same_new": r[f"{fam}_both_changed_same"],
                    f"{fam}_F": r[f"{fam}_both_unch"], f"{fam}_p_hot": p_hot, f"{fam}_K": K}
        rows.append(rec)
    return pl.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=300)
    ap.add_argument("--relabel", type=int, default=500)
    ap.add_argument("--no-estimates", action="store_true")
    ap.add_argument("--code-only", action="store_true", help="recompute only the game-state part of results.json")
    a = ap.parse_args()
    if a.code_only:
        out = json.loads((RES / "results.json").read_text())
        code = code_analysis()
        code.write_parquet(RES / "code_overlap.parquet")
        out["code"] = code.drop([c for c in code.columns if c.endswith("_K")]).to_dicts()
        out["code_rebuilt_at"] = dt.datetime.now(dt.timezone.utc).isoformat()
        (RES / "results.json").write_text(json.dumps(out, indent=1, default=float))
        print("code part rewritten")
        return
    rng = np.random.default_rng(20261004)
    RES.mkdir(parents=True, exist_ok=True)
    out = {"built_at": dt.datetime.now(dt.timezone.utc).isoformat(), "git_commit": git_commit(), "periods": {}}
    for m in MODELS:
        for p in PERIODS:
            pdat = L.period_data(p, m)
            out["periods"][f"{p}|{m}|main"] = analyse(pdat, a.boot, a.relabel, rng)
            print(p, m, "q_late", round(out["periods"][f"{p}|{m}|main"]["q_late"], 3),
                  "tau", round(out["periods"][f"{p}|{m}|main"]["tau"]["tau"], 2), flush=True)
    # robustness (bge only): white32, 2-h bins, period-centred
    for p in PERIODS:
        out["periods"][f"{p}|bge_small|white32"] = analyse(L.period_data(p, "bge_small", "white32"), 100, 100, rng,
                                                            kinds=("agent_bin",))
        out["periods"][f"{p}|bge_small|bin2h"] = analyse(rebin2(L.period_data(p, "bge_small")), 100, 100, rng,
                                                          kinds=("agent_bin",))
        out["periods"][f"{p}|bge_small|pcentred"] = analyse(period_centre(L.period_data(p, "bge_small")), 100, 100, rng,
                                                             kinds=("agent_bin",))
    code = code_analysis()
    code.write_parquet(RES / "code_overlap.parquet")
    out["code"] = code.drop([c for c in code.columns if c.endswith("_K")]).to_dicts()
    (RES / "results.json").write_text(json.dumps(out, indent=1, default=float))
    print("written", RES / "results.json")


if __name__ == "__main__":
    main()
