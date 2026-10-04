"""H02 round 1b: compile round 1 vs round 1b numbers (card section, summary page, period READMEs, estimates).

Variants: r1 (round-1 files), r1b (activity_bins_fixed, whole-day grid: the round-1 null on corrected data),
r1b_trim (all-present window), r1b_trim_stall (DQ8's corrected null: trim + explained joint silences removed before
the surrogates). The H38 agent-state-conditioned gain (mask_scaffold) per chunk comes from H19's round-1b estimates
(same estimator and chunks: data/processed/H19-loop-gain-collapse/r1b/estimates_window.parquet, H19.geq_active_scaf).
Output: data/processed/H02-couplings-are-real/r1b/report.json (+ per-chunk table chunks_1b.parquet)
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "data/processed/H02-couplings-are-real"
VARS = {"r1": BASE, "r1b": BASE / "r1b", "r1b_trim": BASE / "r1b/trim", "r1b_trim_stall": BASE / "r1b/trim_stall"}
GROUPS = ["regime", "mode"]


def med(df, col):
    return {f"{r[0]}-{r[1]}": r[2] for r in df.group_by(GROUPS).agg(pl.col(col).median()).sort(GROUPS).iter_rows()}


def cnt(df, expr, name="n"):
    return {f"{r[0]}-{r[1]}": int(r[2]) for r in df.group_by(GROUPS).agg(expr.sum().alias(name)).sort(GROUPS).iter_rows()}


def variant(d: Path) -> dict:
    out = {}
    rc = pl.read_parquet(d / "real_chunks.parquet")
    out["ki1_frac_sig_median"] = med(rc, "block_N1_frac_sig")
    out["naive_N0_frac_sig_median"] = med(rc, "naive_N0_frac_sig")
    out["box5_frac_sig_median"] = med(rc, "box5_N1_frac_sig")
    out["eq_frac_sig_median"] = med(rc, "eq_N1_frac_sig")
    out["bh_ki1"] = cnt(rc, pl.col("block_N1_bh"))
    out["excess_absJ_median"] = {k: v for k, v in med(rc.with_columns((pl.col("block_N1_absJ") - pl.col("block_N1_absJ_null")).alias("ex")), "ex").items()}
    out["ho_days_M3_gt_M1"] = int(rc["ho_days_M3_gt_M1"].sum()); out["ho_days"] = int(rc["n_days"].sum())
    for reg in ("I", "III"):
        a = rc.filter((pl.col("regime") == reg) & (pl.col("mode") == "I"))["block_N1_frac_sig"].median()
        b = rc.filter((pl.col("regime") == reg) & (pl.col("mode") == "C"))["block_N1_frac_sig"].median()
        out[f"ratio_C_over_I_{reg}"] = float(b / a) if a else None
    if (d / "heldout_null.parquet").exists():
        h = pl.read_parquet(d / "heldout_null.parquet")
        out["ho_M3_p05"] = cnt(h, pl.col("p31") < 0.05); out["ho_M2_p05"] = cnt(h, pl.col("p21") < 0.05)
        out["ho_M3_p05_total"] = int((h["p31"] < 0.05).sum()); out["ho_M2_p05_total"] = int((h["p21"] < 0.05).sum())
        out["ho_z21_median"] = med(h, "z21")
    m = pl.read_parquet(d / "mf_cw.parquet").with_columns((pl.col("bJ0") * pl.col("q")).alias("g"))
    out["cw_bJ0_median"] = med(m, "bJ0"); out["cw_g_median"] = med(m, "g")
    out["cw_sig"] = cnt(m, pl.col("z") > 2); out["cw_sig_total"] = int((m["z"] > 2).sum())
    out["cw_gmax"] = float(m["g"].max())
    sig = m.filter(pl.col("z") > 2)
    out["pk_cw_better_in_sig"] = f"{int((sig['tvd_cw'] < sig['tvd_ind']).sum())}/{sig.height}"
    lo_bad = sig.filter((pl.col("obs_lo") > 2 * pl.col("cw_lo")) | (pl.col("obs_lo") < 0.5 * pl.col("cw_lo")))
    out["pk_low_tail_off_2x_in_sig"] = f"{lo_bad.filter(pl.col('obs_lo') > 0.005).height}/{sig.height}"
    if (d / "mf_cw_nolull.parquet").exists():
        n = pl.read_parquet(d / "mf_cw_nolull.parquet")
        out["cw_sig_nolull"] = cnt(n, pl.col("z_nolull") > 2); out["cw_sig_nolull_total"] = int((n["z_nolull"] > 2).sum())
        out["lull_drop_frac_median"] = float(n["drop_frac"].median())
    lf = pl.read_parquet(d / "mf_lf.parquet")
    out["lf_frac_zA_gt2"] = {f"{r[0]}-{r[1]}": r[2] for r in lf.group_by(GROUPS).agg((pl.col("z_A") > 2).mean()).sort(GROUPS).iter_rows()}
    out["lf_zff_median"] = med(lf, "z_ff")
    cp = pl.read_parquet(d / "real_couplings.parquet")
    k = cp.filter(pl.col("est") == "block_N1")
    s_same = k.filter(pl.col("same_lab")); s_x = k.filter(~pl.col("same_lab"))
    out["family_enrichment"] = float(((s_same["z"].abs() > 1.96).mean()) / max((s_x["z"].abs() > 1.96).mean(), 1e-9))
    eq = cp.filter((pl.col("est") == "eq_N1") & (pl.col("z").abs() > 1.96))
    out["eq_sig_neg_share"] = float((eq["z"] < 0).mean()) if eq.height else None
    inf = pl.read_parquet(d / "real_influence.parquet")
    g26 = inf.filter((pl.col("chunk") == "g26c0") & (pl.col("agent") == 17))
    out["g26_leader"] = {r["est"]: {"rank": r["rank"], "zI": r["zI"], "N": inf.filter((pl.col("chunk") == "g26c0") & (pl.col("est") == r["est"])).height}
                         for r in g26.iter_rows(named=True)}
    top = inf.filter(pl.col("est") == "block").group_by("chunk").agg(pl.col("zI").max().alias("zmax"), pl.col("I").max().alias("Imax"))
    out["top_zI_range"] = [float(top["zmax"].min()), float(top["zmax"].max())]
    out["top_I_range"] = [float(top["Imax"].min()), float(top["Imax"].max())]
    if "kept_share" in rc.columns:
        pass
    return out


def chunk_table() -> pl.DataFrame:
    cols = ["chunk", "goal_no", "mode", "regime", "N", "act", "block_N1_frac_sig", "naive_N0_frac_sig", "ho_days_M3_gt_M1", "n_days"]
    rows = None
    for v, d in VARS.items():
        rc = pl.read_parquet(d / "real_chunks.parquet").select(cols)
        m = pl.read_parquet(d / "mf_cw.parquet").select("chunk", "bJ0", "q", "z")
        h = pl.read_parquet(d / "heldout_null.parquet").select("chunk", "p31", "p21") if (d / "heldout_null.parquet").exists() else None
        t = rc.join(m, on="chunk", how="left")
        if h is not None:
            t = t.join(h, on="chunk", how="left")
        t = t.rename({c: f"{c}__{v}" for c in t.columns if c not in ("chunk", "goal_no", "mode", "regime")})
        rows = t if rows is None else rows.join(t, on=["chunk", "goal_no", "mode", "regime"], how="left")
    # H38 agent-state conditioning (H19's r1b estimates on H02's chunks)
    w = pl.read_parquet(ROOT / "data/processed/H19-loop-gain-collapse/r1b/estimates_window.parquet")
    sc = (w.filter(pl.col("method") == "H19.geq_active_scaf").select(pl.col("window").alias("chunk"), pl.col("value").alias("g_scaf"),
                                                                    pl.col("bJ0").alias("bJ0_scaf"), pl.col("se").alias("g_scaf_se")))
    raw = (w.filter(pl.col("method") == "H19.geq_active").select(pl.col("window").alias("chunk"), pl.col("value").alias("g_raw_fixed"),
                                                                pl.col("E").alias("E_raw"), pl.col("z").alias("z_raw_h19")))
    tr = (w.filter(pl.col("method") == "H19.geq_active_trim").select(pl.col("window").alias("chunk"), pl.col("value").alias("g_trim"),
                                                                    pl.col("E").alias("E_trim"), pl.col("z").alias("z_trim_h19"),
                                                                    pl.col("kept_share")))
    return rows.join(sc, on="chunk", how="left").join(raw, on="chunk", how="left").join(tr, on="chunk", how="left").sort("chunk")


def main():
    rep = {v: variant(d) for v, d in VARS.items()}
    ct = chunk_table()
    ct.write_parquet(BASE / "r1b/chunks_1b.parquet")
    # day-edge share of the regime-III collective gain (H38's f_scaffold analogue) from the chunk table
    ct = ct.with_columns(((pl.col("g_raw_fixed") - pl.col("g_scaf")) / pl.col("g_raw_fixed")).alias("f_scaf"),
                         ((pl.col("g_raw_fixed") - pl.col("g_trim")) / pl.col("g_raw_fixed")).alias("f_trim"))
    rep["f_scaffold_median"] = {f"{r[0]}": {"scaf": r[1], "trim": r[2]} for r in
                               ct.group_by("regime").agg(pl.col("f_scaf").median(), pl.col("f_trim").median()).sort("regime").iter_rows()}
    rep["g_by_regime_mode"] = {f"{r[0]}-{r[1]}": {"raw": r[2], "trim": r[3], "scaf": r[4]} for r in
                              ct.group_by("regime", "mode").agg(pl.col("g_raw_fixed").median(), pl.col("g_trim").median(),
                                                                pl.col("g_scaf").median()).sort("regime", "mode").iter_rows()}
    for v in ("r1b",):
        tk = BASE / "r1b/real_chunks_talk.parquet"
        if tk.exists():
            t = pl.read_parquet(tk)
            rep["talk_r1b"] = {"ki1_frac_sig_median": med(t, "block_N1_frac_sig"), "bh": cnt(t, pl.col("block_N1_bh"))}
            h = pl.read_parquet(BASE / "r1b/heldout_null_talk.parquet")
            rep["talk_r1b"]["ho_M3_p05"] = cnt(h, pl.col("p31") < 0.05)
    for f in ("native_g12.json", "native_g44.json", "thinning.parquet"):
        p = BASE / "r1b" / f
        if p.suffix == ".json" and p.exists():
            rep[f.split(".")[0]] = json.loads(p.read_text())
        elif p.exists():
            th = pl.read_parquet(p)
            rep["thinning"] = th.group_by("cal", "JL").agg(pl.len().alias("reps"), pl.col("pass_clean").mean(), pl.col("pass_thin").mean(),
                                                         (pl.col("rank_clean") == 1).mean().alias("rank1_clean"),
                                                         (pl.col("rank_thin") == 1).mean().alias("rank1_thin"),
                                                         pl.col("z_clean").median(), pl.col("z_thin").median()).sort("cal", "JL").to_dicts()
    (BASE / "r1b/report.json").write_text(json.dumps(rep, indent=1, default=float))
    print(json.dumps({k: v for k, v in rep.items() if not k.startswith("native")}, indent=1, default=float)[:9000])


if __name__ == "__main__":
    main()
