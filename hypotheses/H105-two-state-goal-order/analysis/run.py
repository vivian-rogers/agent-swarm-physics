"""H105 replication layer: free -> assigned pairs (P1-P5, P7, calibrated tilt test) and kickoff transitions (P6).
Writes data/processed/H105-two-state-goal-order/{G<NN>/results.json, NE34/summary.parquet, replication.json}.
Usage: uv run python analysis/run.py [--boot 1000] [--nsim 200]
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h105lib as L  # noqa: E402

PRIMARY_PAIRS = ["P11_12", "P16_17", "P37_38"]
SECONDARY_PAIRS = ["P03_04", "P05_06"]
CONFIGS = {  # name: (model, variant, q, rule, day_demean)
    "primary": ("bge_small", "white", 95, "tie", False),
    "gte": ("gte_modernbert", "white", 95, "tie", False),
    "style": ("bge_small", "style", 95, "tie", False),
    "gte_style": ("gte_modernbert", "style", 95, "tie", False),
    "q90": ("bge_small", "white", 90, "tie", False),
    "q98": ("bge_small", "white", 98, "tie", False),
    "strict": ("bge_small", "white", 95, "strict", False),
    "daydemean": ("bge_small", "white", 95, "tie", True),
}


def tables(design, model, variant, q, rule, direction="goal"):
    st, pr, thr = L.load(design)
    y = pr[f"{direction}|{model}|{variant}"]
    on = y > L.threshold(thr, direction, model, variant, q)
    F = L.spin_tables(st, on, "F", rule=rule); A = L.spin_tables(st, on, "A", rule=rule)
    ag = L.common_agents(F, A)
    return L.restrict(F, ag), L.restrict(A, ag), st, pr, thr, ag


def analyze(design, cfg, n_boot, full=False, seed=0):
    model, variant, q, rule, dd = CONFIGS[cfg]
    F, A, st, pr, thr, ag = tables(design, model, variant, q, rule)
    if len(ag) < 4:
        return dict(design=design, cfg=cfg, n_agents=len(ag), testable=False)
    core = L.pair_core(F["S"], A["S"], dd, F["days"], A["days"])
    bs = L.boot_pair(F, A, n_boot=n_boot, seed=seed, day_demean=dd)
    lo, hi = float(np.nanpercentile(bs["rho"], 5)), float(np.nanpercentile(bs["rho"], 95))
    out = dict(design=design, cfg=cfg, n_agents=len(ag), testable=True,
               **{k: (float(v) if isinstance(v, (int, float, np.floating, bool, np.bool_)) else v) for k, v in core.items()},
               rho_lo=lo, rho_hi=hi, p1=L.p1_verdict(core["rho"], lo, hi),
               dg_lo=float(np.nanpercentile(bs["dg"], 5)), dg_hi=float(np.nanpercentile(bs["dg"], 95)),
               pA_lo=float(np.nanpercentile(bs["pA"], 5)), pA_hi=float(np.nanpercentile(bs["pA"], 95)),
               pF_lo=float(np.nanpercentile(bs["pF"], 5)), pF_hi=float(np.nanpercentile(bs["pF"], 95)),
               growth_lo=float(np.nanpercentile(bs["growth_obs"], 5)), growth_hi=float(np.nanpercentile(bs["growth_obs"], 95)))
    out["p3"] = "supported" if out["dg_lo"] <= 0 <= out["dg_hi"] else ("failed" if out["dg_lo"] > 0 else "other")
    ls = L.logit_slope(F, A, n_boot=n_boot, seed=seed + 1)
    out.update(s=ls["s"], s_lo=ls["lo"], s_hi=ls["hi"], s_rel=ls["rel_F"], p2=L.p2_verdict(ls["s"], ls["lo"], ls["hi"]))
    if full:
        # P4 transverse: 50 random directions orthogonal to g-hat, own 95% decoy thresholds
        Y = pr[f"perp|{model}|white"]; Q = pr[f"perp_q95|{model}|white"]
        pf, pa, rr = [], [], []
        for j in range(Y.shape[1]):
            on = Y[:, j] > Q[j]
            Fj = L.restrict(L.spin_tables(st, on, "F", rule=rule), ag); Aj = L.restrict(L.spin_tables(st, on, "A", rule=rule), ag)
            c = L.pair_core(Fj["S"], Aj["S"])
            pf.append(c["pF"]); pa.append(c["pA"]); rr.append(c["rho"])
        out.update(perp_pF=float(np.nanmedian(pf)), perp_pA=float(np.nanmedian(pa)), perp_rho=float(np.nanmedian(rr)),
                   perp_rho_q10=float(np.nanpercentile(rr, 10)), perp_rho_q90=float(np.nanpercentile(rr, 90)))
        # P5 day trajectory inside A: per day, observed V_d vs the tilt prediction with J_F and a per-day lambda
        sF = L.seg_stats(F["S"])
        traj = []
        for d in np.unique(A["days"]):
            m = A["days"] == d
            if m.sum() < 4:
                continue
            tp = L.tilt_prediction(F["S"], A["S"][m], sF["J"])
            sd = L.seg_stats(A["S"][m], p_i=L.seg_stats(A["S"])["p_i"])
            traj.append(dict(day=str(d), p=sd["p"], V=sd["V"], V_pred=tp["V_pred"], T=int(m.sum())))
        out["trajectory"] = traj
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--nsim", type=int, default=200)
    args = ap.parse_args()
    designs = pl.read_parquet(L.DATA / "designs.parquet")
    rows, full = [], {}
    for d in PRIMARY_PAIRS + SECONDARY_PAIRS:
        for cfg in CONFIGS:
            r = analyze(d, cfg, args.boot if cfg == "primary" else 300, full=(cfg == "primary"))
            rows.append({k: v for k, v in r.items() if k != "trajectory"})
            if cfg == "primary":
                full[d] = r
            print(d, cfg, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()
                           if k in ("n_agents", "pF", "pA", "gF", "gA", "rho", "rho_lo", "rho_hi", "p1", "s", "p2", "dg", "p3", "crit")}, flush=True)
    # calibrated tilt test for the primary pairs (Amendment 1)
    import calibrated as C
    calib = {}
    for d in PRIMARY_PAIRS:
        F, A, *_ = tables(d, *CONFIGS["primary"][:4])
        r = full[d]
        par = C.calibrate(F, A, r["pF"], r["gF"], r["pA"], seed=11)
        nH = C.null_distribution(F, A, par, "H", n_sim=args.nsim, seed=12)
        nR = C.null_distribution(F, A, par, "R5", n_sim=args.nsim, seed=13)
        n2 = C.null_distribution(F, A, par, "R2", n_sim=args.nsim, seed=14)
        calib[d] = dict(par=par, rho_pct_H=C.percentile(r["rho"], nH["rho"]), rho_pct_R5=C.percentile(r["rho"], nR["rho"]),
                        s_pct_H=C.percentile(r["s"], nH["s"]), s_pct_R2=C.percentile(r["s"], n2["s"]),
                        R2_s_q=[float(np.nanpercentile(n2["s"], q)) for q in (5, 50, 95)],
                        p2_calibrated=("supported" if (0.05 <= C.percentile(r["s"], nH["s"]) <= 0.95 and C.percentile(r["s"], n2["s"]) > 0.95)
                                       else "failed" if (C.percentile(r["s"], nH["s"]) < 0.05 and 0.05 <= C.percentile(r["s"], n2["s"]) <= 0.95)
                                       else "inconclusive"),
                        dg_pct_H=C.percentile(r["dg"], nH["dg"]),
                        dg_pct_R5=C.percentile(r["dg"], nR["dg"]),
                        H_rho_q=[float(np.nanpercentile(nH["rho"], q)) for q in (5, 50, 95)],
                        R5_rho_q=[float(np.nanpercentile(nR["rho"], q)) for q in (5, 50, 95)],
                        H_s_q=[float(np.nanpercentile(nH["s"], q)) for q in (5, 50, 95)],
                        H_dg_q=[float(np.nanpercentile(nH["dg"], q)) for q in (5, 50, 95)],
                        R5_dg_q=[float(np.nanpercentile(nR["dg"], q)) for q in (5, 50, 95)])
        print("calibrated", d, json.dumps(calib[d], default=float)[:400], flush=True)
    # kickoff transitions (P6)
    krows = []
    for d in designs.filter(pl.col("kind") == "kickoff")["design"].to_list():
        r = analyze(d, "primary", 300)
        rg = analyze(d, "gte", 300)
        krows.append({**{k: v for k, v in r.items() if k != "trajectory"}, "rho_gte": rg.get("rho"), "p1_gte": rg.get("p1")})
        print(d, {k: (round(v, 3) if isinstance(v, float) else v) for k, v in r.items()
                  if k in ("n_agents", "pF", "pA", "gF", "gA", "rho", "p1", "growth_obs", "growth_pred")}, flush=True)
    kdf = pl.DataFrame(krows, infer_schema_length=None)
    ok = kdf.filter(pl.col("testable") & pl.col("rho").is_finite())
    inside = float((ok["rho"].abs() < L.LN15).mean()) if ok.height else np.nan
    gg = ok.filter(pl.col("growth_obs").is_finite() & pl.col("growth_pred").is_finite())
    sp = spearmanr(gg["growth_obs"], gg["growth_pred"]) if gg.height >= 4 else None
    rep = dict(P6=dict(n=ok.height, frac_inside=inside, spearman_growth=float(sp.statistic) if sp else None,
                       p_growth=float(sp.pvalue) if sp else None,
                       verdicts=dict(zip(ok["design"].to_list(), ok["p1"].to_list()))),
               calibrated=calib)
    out = L.DATA
    (out / "NE34").mkdir(exist_ok=True)
    pl.DataFrame(rows, infer_schema_length=None).write_parquet(out / "NE34/pairs_all_configs.parquet")
    kdf.write_parquet(out / "NE34/kickoffs.parquet")
    for d, r in full.items():
        g = int(d.split("_")[1])
        (out / f"G{g:02d}").mkdir(exist_ok=True)
        (out / f"G{g:02d}/results.json").write_text(json.dumps({k: v for k, v in r.items() if k not in ("p_i",)}, indent=1, default=float))
    (out / "replication.json").write_text(json.dumps(rep, indent=1, default=float))
    print(json.dumps(rep["P6"], indent=1, default=float))


if __name__ == "__main__":
    main()
