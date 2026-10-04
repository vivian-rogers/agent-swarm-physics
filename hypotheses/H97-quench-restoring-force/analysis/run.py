"""H97 replication layer: every eligible kickoff transition (same regime, both neighbours non-holdout, #23 excluded).
Per transition and configuration: kickoff memory (rho: disattenuated correlation, primary after Amendment 1; beta: IV
slope), placebo memory, extra forgetting, isotropy, HH-literal shape along k, per-agent chi. Across transitions:
random-effects meta-analysis (never pooled fits), agent constancy, lab effect, moderators, weekend placebo.
Writes data/processed/H97-quench-restoring-force/{G<NN>/results.json, NE34/*.parquet, NE34/summary.json}.
Usage: uv run python analysis/run.py [--boot 1000] [--perm 2000]
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import mannwhitneyu, spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h97lib as L  # noqa: E402
from calibrate import placebo_boundaries  # noqa: E402

CONFIGS = {"primary": ("bge_small", "white", False, False), "gte": ("gte_modernbert", "white", False, False),
           "style": ("bge_small", "style", False, False), "gte_style": ("gte_modernbert", "style", False, False),
           "dedupe": ("bge_small", "white", True, False), "center": ("bge_small", "white", False, True),
           "gte_center": ("gte_modernbert", "white", False, True)}


def build_inputs(design, tr, cfg):
    model, variant, dedupe, center = CONFIGS[cfg]
    stmt, _ = L.load_design(design)
    k = L.vectors(design, "k", model)
    cen = L.agent_center_means(tr["regime"], {tr["p"], tr["prev"]}, model, variant) if center else None
    sv = lambda m: L.seg_vectors(stmt, m, model, variant, dedupe, cen)  # noqa: E731
    kick = L.boundary(sv(pl.col("seg") == "prev"), sv(pl.col("seg") == "day1"))
    plat = sv(pl.col("seg") == "plateau")
    pT = L.plateau_targets(plat, k)
    plac, gaps = [], []
    for g, d0, d1 in placebo_boundaries(stmt, tr):
        bd = L.boundary(sv((pl.col("goal_no") == g) & (pl.col("pt_date") == d0)), sv((pl.col("goal_no") == g) & (pl.col("pt_date") == d1)))
        if len(bd) >= L.MIN_N_TRANSITION:
            plac.append(bd)
            gaps.append((dt.date.fromisoformat(d1) - dt.date.fromisoformat(d0)).days)
    return kick, plac, pT, k, gaps


def noise_ceiling(kick, seed=0):
    """Reliability of chi_mem across agents from two random halves of the day-1 statements (Spearman-Brown)."""
    rng = np.random.default_rng(seed)
    a1, a2 = {}, {}
    for a, (X, Y) in kick.items():
        if len(Y) < 2 * L.MIN_STMT:
            continue
        p = rng.permutation(len(Y)); h = len(Y) // 2
        a1[a] = (X, Y[p[:h]]); a2[a] = (X, Y[p[h:]])
    if len(a1) < L.MIN_N_TRANSITION:
        return np.nan
    c1 = L.agent_chi_mem(*L.split_arrays(a1, n_splits=10, seed=1)[:3])
    c2 = L.agent_chi_mem(*L.split_arrays(a2, n_splits=10, seed=1)[:3])
    r = spearmanr(c1, c2).statistic
    return float(2 * r / (1 + r)) if np.isfinite(r) and r > -0.99 else np.nan


def jsonable(d):
    out = {}
    for k, v in d.items():
        if k.startswith("_"):
            continue
        if isinstance(v, np.ndarray):
            v = v.tolist()
        if isinstance(v, (np.floating, np.integer)):
            v = v.item()
        out[k] = v
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--perm", type=int, default=2000)
    ap.add_argument("--configs", default=",".join(CONFIGS))
    args = ap.parse_args()
    trs = pl.read_parquet(L.DATA / "transitions.parquet").filter(pl.col("kind") == "kickoff")
    roster = pl.read_parquet(L.S / "roster.parquet").select("agent", "lab")
    lab = dict(zip(roster["agent"].to_list(), roster["lab"].to_list()))
    per, chi_rows, gap_rows = [], [], []
    for tr in trs.iter_rows(named=True):
        for cfg in args.configs.split(","):
            if cfg != "primary" and not tr["same_regime"]:
                continue
            kick, plac, pT, k, gaps = build_inputs(tr["design"], tr, cfg)
            if len(kick) < L.MIN_N_AGENT:
                continue
            r = L.analyze_transition(kick, plac, pT, k, n_boot=args.boot if cfg == "primary" else 0, seed=tr["p"])
            r.update(design=tr["design"], p=tr["p"], cfg=cfg, regime=tr["regime"], same_regime=tr["same_regime"],
                     mode=tr["mode"], first_day=tr["first_day"], named=int(tr["n_frozen_named_goal"] or 0))
            if cfg == "primary":
                r["noise_ceiling"] = noise_ceiling(kick, seed=tr["p"])
                for g, v in zip(gaps, r["rho0_full_all"]):
                    gap_rows.append(dict(design=tr["design"], gap=g, rho0=v))
            for a, cm, cp in zip(r["agents"], r["chi_mem_i"], r.get("chi_par_i", [np.nan] * r["N"])):
                chi_rows.append(dict(design=tr["design"], cfg=cfg, agent=a, lab=lab.get(a), first_day=tr["first_day"],
                                     regime=tr["regime"], same_regime=tr["same_regime"], chi_mem=float(cm), chi_par=float(cp)))
            per.append(jsonable(r))
            if cfg in ("primary", "gte", "center"):
                print(tr["design"], cfg, "N", r["N"], "rho %.2f rho0 %.2f drho %.2f | beta %.2f beta0 %.2f | iso %.2f | a %s" % (
                    r["rho_full"], r["rho0_full"], r["drho_full"], r["beta_full"], r["beta0_full"], r["iso_diff"],
                    ("%.3f" % r["shape_a"]) if "shape_a" in r else "-"), flush=True)
    perdf = pl.DataFrame([{k: v for k, v in p.items() if not isinstance(v, list)} for p in per], infer_schema_length=None)
    chidf = pl.DataFrame(chi_rows, infer_schema_length=None)
    out = L.DATA / "NE34"
    out.mkdir(exist_ok=True)
    perdf.write_parquet(out / "transitions_all_configs.parquet")
    chidf.write_parquet(out / "chi_agents.parquet")
    pl.DataFrame(gap_rows).write_parquet(out / "placebo_gaps.parquet")
    for p in per:
        if p["cfg"] == "primary":
            g = L.DATA / f"G{p['p']:02d}"
            g.mkdir(exist_ok=True)
            (g / "results.json").write_text(json.dumps(p, indent=1, default=float))

    # ------------------------------------------------------------------ cross-transition tests
    summ = {}
    for cfg in args.configs.split(","):
        d = perdf.filter((pl.col("cfg") == cfg) & pl.col("same_regime") & (pl.col("N") >= L.MIN_N_TRANSITION)
                         & (pl.col("n_placebo") > 0))
        if d.height < 3:
            continue
        m = L.dl_meta(d["drho_full"].to_numpy(), d["se_drho_full"].to_numpy())
        mb = L.dl_meta(d["dbeta_full"].to_numpy(), d["se_dbeta_full"].to_numpy())
        mpar = L.dl_meta(d["drho_par"].to_numpy(), d["se_drho_par"].to_numpy())
        mperp = L.dl_meta(d["drho_perp"].to_numpy(), d["se_drho_perp"].to_numpy())
        iso = L.dl_meta(d["iso_diff"].to_numpy(), d["se_iso_diff"].to_numpy())
        sa = L.dl_meta(d["shape_a"].to_numpy(), d["se_shape_a"].to_numpy()) if "shape_a" in d.columns else {}
        sb = L.dl_meta(d["shape_b"].to_numpy(), d["se_shape_b"].to_numpy()) if "shape_b" in d.columns else {}
        frac = float((d["drho_full"] > 0).mean())
        summ[cfg] = dict(n=d.height, drho=m, frac_drho_pos=frac, sign_p=L.sign_test_p(d["drho_full"].to_numpy()),
                         dbeta=mb, drho_par=mpar, drho_perp=mperp, iso_beta=iso, shape_a=sa, shape_b=sb,
                         P1=bool(m["mean"] - 1.645 * m["se"] > 0 and frac >= 2 / 3),
                         P1_fail=bool(m["mean"] <= 0 or frac <= 0.5),
                         P2_pass=bool(abs(iso["mean"]) < 0.2 and iso["mean"] - 1.645 * iso["se"] < 0 < iso["mean"] + 1.645 * iso["se"]),
                         P2_fail=bool(iso["mean"] + 1.645 * iso["se"] < 0 and iso["mean"] <= -0.2),
                         rho_kick_median=float(d["rho_full"].median()), rho0_median=float(d["rho0_full"].median()))
        if cfg == "primary":
            summ[cfg]["noise_ceiling_median"] = float(d["noise_ceiling"].median())
            # P5 moderators
            free = d.filter(pl.col("mode") == "F")["drho_full"].to_numpy(); nonfree = d.filter(pl.col("mode") != "F")["drho_full"].to_numpy()
            named = d.filter(pl.col("named") > 0)["drho_full"].to_numpy(); unnamed = d.filter(pl.col("named") == 0)["drho_full"].to_numpy()
            summ[cfg]["P5"] = dict(free=free.tolist(), nonfree_median=float(np.median(nonfree)),
                                   free_median=float(np.median(free)) if len(free) else None,
                                   mw_p=float(mannwhitneyu(nonfree, free, alternative="greater").pvalue) if len(free) >= 2 else None,
                                   named_median=float(np.median(named)) if len(named) else None,
                                   unnamed_median=float(np.median(unnamed)) if len(unnamed) else None,
                                   mw_named_p=float(mannwhitneyu(named, unnamed, alternative="greater").pvalue) if len(named) >= 2 else None)
    # agent constancy (P4) and lab effect (P6)
    cons = {}
    for cfg in ("primary", "gte", "center", "style"):
        c = chidf.filter((pl.col("cfg") == cfg) & pl.col("same_regime"))
        if c.height == 0:
            continue
        cons[cfg] = {col: L.constancy(c.select("design", "agent", "first_day", col), col, n_perm=args.perm) for col in ("chi_mem", "chi_par")}
        print("constancy", cfg, {kk: {k2: round(v2, 3) if isinstance(v2, float) else v2 for k2, v2 in vv.items()} for kk, vv in cons[cfg].items()}, flush=True)
    c = L.rank_within(chidf.filter((pl.col("cfg") == "primary") & pl.col("same_regime") & pl.col("chi_mem").is_finite()), "chi_mem")
    c = c.filter(pl.col("lab").is_not_null())

    def labstat(df):
        g = df.group_by("lab").agg(pl.col("rk").mean().alias("m"), pl.len().alias("n")).filter(pl.col("n") >= 5)
        return float(((g["m"] - 0.5) ** 2 * g["n"]).sum() / g["n"].sum())

    l0 = labstat(c)
    rng = np.random.default_rng(3)
    des = c["design"].to_numpy(); labs = c["lab"].to_numpy()
    null = []
    for _ in range(args.perm):
        l2 = labs.copy()
        for z in np.unique(des):
            ix = np.flatnonzero(des == z); l2[ix] = labs[rng.permutation(ix)]
        null.append(labstat(c.with_columns(pl.Series("lab", l2))))
    lab_p = float((np.sum(np.array(null) >= l0) + 1) / (len(null) + 1))
    lab_means = c.group_by("lab").agg(pl.col("rk").mean(), pl.len()).sort("lab").to_dicts()
    gp = pl.DataFrame(gap_rows)
    p8 = dict(weekday=float(gp.filter(pl.col("gap") == 1)["rho0"].median()), weekend=float(gp.filter(pl.col("gap") >= 2)["rho0"].median()),
              n_weekday=int((gp["gap"] == 1).sum()), n_weekend=int((gp["gap"] >= 2).sum()))
    res = dict(meta=summ, constancy=cons, lab=dict(stat=l0, p=lab_p, means=lab_means), P8=p8)
    (out / "summary.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk in ("n", "drho", "frac_drho_pos", "iso_beta", "shape_a", "P1", "P2_pass", "P2_fail")}
                      for k, v in summ.items()}, indent=1, default=float))
    print("lab", l0, lab_p, "P8", p8)


if __name__ == "__main__":
    main()
