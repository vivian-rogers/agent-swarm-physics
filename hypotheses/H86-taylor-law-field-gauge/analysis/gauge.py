"""H86 replication layer: Taylor coefficients and the shared-field gauge per unit, channel and grid.

Reads bins15.parquet / bins60.parquet (scheme/build.py). Writes replication/gauge.parquet (one row per unit x channel x
grid), replication/daily.parquet (per day, for the natives) and replication/replication.json (card-level tests).
Usage: uv run python hypotheses/H86-taylor-law-field-gauge/analysis/gauge.py [--B 200] [--surr 49]
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
import h86lib as L  # noqa: E402

ROOT = L.ROOT
sys.path.insert(0, str(ROOT / "infra" / "shared"))
from common import load_holdout  # noqa: E402

CH15 = ("activity", "calls", "msg")
STATS = ("c_T", "a", "b", "b_ad", "c_x", "c_xw", "phi", "n_agents", "mu_med", "fano_med")


def unit_rows(df, unit, channel, width, rng, B, n_surr):
    rows = []
    for grid in ("raw", "trim"):
        sub = df if grid == "raw" else df.filter(pl.col("trim"))
        if sub.height == 0:
            continue
        Y, days, _ = L.matrix(sub, channel)
        st = L.taylor(Y, days)
        r = {"unit_id": unit, "channel": channel, "grid": grid, "bin_min": width, "n_cells": int(Y.shape[0]),
             "n_days": int(len(np.unique(days)))}
        r |= {k: (float(st[k]) if k in st and st[k] is not None else np.nan) for k in STATS}
        if np.isfinite(r["c_x"]) and B:
            ci = L.boot(Y, days, rng, B=B)
            for k in ("c_T", "b", "c_x", "c_xw", "phi"):
                r[f"{k}_lo"], r[f"{k}_hi"] = ci[k]
        if grid == "trim" and np.isfinite(r.get("c_xw", np.nan)) and n_surr:
            keep = (~np.isnan(Y)).sum(0) >= L.MIN_CELLS
            nul = L.shift_null(Y[:, keep], days, rng, n_surr)
            obs = L.c_cross_within(Y[:, keep], days)
            r["c_xw_null_mean"] = float(np.nanmean(nul))
            r["c_xw_p"] = float((1 + (nul >= obs).sum()) / (n_surr + 1))
        rows.append(r)
    return rows


def daily(df, unit, channel, width):
    rows = []
    for d in df["pt_date"].unique().sort().to_list():
        for grid in ("raw", "trim"):
            sub = df.filter(pl.col("pt_date") == d)
            if grid == "trim":
                sub = sub.filter(pl.col("trim"))
            if sub.height == 0:
                continue
            Y, days, _ = L.matrix(sub, channel)
            st = L.taylor(Y, days, min_cells=4, ad=False)
            rows.append({"unit_id": unit, "pt_date": d, "channel": channel, "grid": grid, "bin_min": width,
                         "n_cells": int(Y.shape[0]), **{k: float(st.get(k, np.nan)) for k in ("c_T", "b", "c_x", "phi", "n_agents")}})
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--B", type=int, default=200)
    ap.add_argument("--surr", type=int, default=49)
    a = ap.parse_args()
    rng = np.random.default_rng(20261004)
    b15 = pl.read_parquet(L.DATA / "bins15.parquet")
    b60 = pl.read_parquet(L.DATA / "bins60.parquet")
    pu = pl.read_parquet(ROOT / "data/processed/shared/period_units.parquet").select("unit_id", "goal_no", "regime", "holdout")
    held = set(load_holdout()["goal_periods_held_out"])
    units = pu.filter(~pl.col("holdout") & pl.col("unit_id").is_in(b15["unit_id"].unique().to_list()))
    assert not set(units["goal_no"].to_list()) & held
    rows, drows = [], []
    for unit in units["unit_id"].to_list():
        d15 = b15.filter(pl.col("unit_id") == unit)
        for ch in CH15:
            rows += unit_rows(d15, unit, ch, 15, rng, a.B, a.surr)
            drows += daily(d15, unit, ch, 15)
        d60 = b60.filter(pl.col("unit_id") == unit)
        rows += unit_rows(d60, unit, "commit", 60, rng, a.B, a.surr)
        print(unit, flush=True)
    g = pl.DataFrame(rows, infer_schema_length=None).join(units.select("unit_id", "goal_no", "regime"), on="unit_id")
    dd = pl.DataFrame(drows, infer_schema_length=None).join(units.select("unit_id", "goal_no", "regime"), on="unit_id")
    out = L.DATA / "replication"
    out.mkdir(parents=True, exist_ok=True)
    g.write_parquet(out / "gauge.parquet")
    dd.write_parquet(out / "daily.parquet")
    res = tests(g)
    (out / "replication.json").write_text(json.dumps(res, indent=1, default=float))
    print(json.dumps(res, indent=1, default=float))


def med(s):
    s = s.drop_nulls().drop_nans() if s.dtype in (pl.Float64, pl.Float32) else s.drop_nulls()
    return {"median": float(s.median()) if len(s) else np.nan,
            "iqr": [float(s.quantile(0.25)), float(s.quantile(0.75))] if len(s) else [np.nan, np.nan], "n": len(s)}


def tests(g: pl.DataFrame) -> dict:
    res = {}
    act = g.filter(pl.col("channel") == "activity")
    w = act.pivot(on="grid", index=["unit_id", "regime", "goal_no"], values=["b", "c_T", "c_x", "c_xw", "phi", "c_xw_p"])
    res["P1_b_raw"] = med(w["b_raw"])
    res["P1_cT_raw_pos_share"] = float((w["c_T_raw"] > 0).mean())
    res["P2_b_trim"] = med(w["b_trim"])
    for r in ("I", "III"):
        s = w.filter(pl.col("regime") == r)
        sx = s.filter(pl.col("c_x_raw") > 0.01)
        st = s.filter(pl.col("c_T_raw") > 0.01)
        res[f"P3_rx_{r}"] = med(1 - sx["c_x_trim"] / sx["c_x_raw"])
        res[f"P3_rT_{r}"] = med(1 - st["c_T_trim"] / st["c_T_raw"])
        res[f"cx_raw_{r}"] = med(s["c_x_raw"]); res[f"cx_trim_{r}"] = med(s["c_x_trim"])
        res[f"cT_raw_{r}"] = med(s["c_T_raw"]); res[f"cT_trim_{r}"] = med(s["c_T_trim"])
        res[f"phi_trim_{r}"] = med(s["phi_trim"]); res[f"phi_raw_{r}"] = med(s["phi_raw"])
        res[f"cxw_sig_share_{r}"] = float((s["c_xw_p_trim"].drop_nulls() < 0.05).mean()) if s["c_xw_p_trim"].drop_nulls().len() else np.nan
        res[f"b_raw_{r}"] = med(s["b_raw"]); res[f"b_trim_{r}"] = med(s["b_trim"])
    s3 = w.filter(pl.col("regime") == "III")
    res["P4_kill"] = bool(res["phi_trim_III"]["median"] >= 0.5 and res["cxw_sig_share_III"] >= 2 / 3)
    # P5 calls vs activity, regime III trimmed
    cl = g.filter((pl.col("grid") == "trim")).pivot(on="channel", index=["unit_id", "regime"], values=["b", "c_T"])
    c3 = cl.filter(pl.col("regime") == "III")
    res["P5_calls_lower_b_share"] = float((c3["b_calls"] < c3["b_activity"]).mean())
    res["P5_calls_lower_cT_share"] = float((c3["c_T_calls"] < c3["c_T_activity"]).mean())
    res["P5_b_calls_trim_III"] = med(c3["b_calls"]); res["P5_cT_calls_trim_III"] = med(c3["c_T_calls"])
    # P6 commits
    cm = g.filter((pl.col("channel") == "commit") & (pl.col("grid") == "trim"))
    res["P6_b_commit_trim"] = med(cm["b"])
    res["P6_cx_commit_trim"] = med(cm["c_x"])
    kick = (pl.read_parquet(ROOT / "data/processed/H54-kickoff-quench-target/kickoffs.parquet")
            .filter(pl.col("room").is_null()).select(pl.col("goal_no").cast(pl.Int8), "S_text"))
    gd = set(pl.read_parquet(ROOT / "data/processed/shared/period_affordances.parquet").filter(pl.col("git_dense"))["unit_id"].to_list())
    cg = (cm.filter(pl.col("unit_id").is_in(list(gd)) & pl.col("c_x").is_not_nan()).group_by("goal_no")
          .agg(pl.col("c_x").mean(), pl.col("c_T").mean()).join(kick, on="goal_no"))
    if cg.height >= 5:
        rho, p = spearmanr(cg["c_x"], cg["S_text"])
        rho2, p2 = spearmanr(cg["c_T"], cg["S_text"])
        res["P6_spearman_cx_Stext"] = {"rho": float(rho), "p_one_sided": float(p / 2 if rho > 0 else 1 - p / 2), "n_goals": cg.height}
        res["P6_spearman_cT_Stext"] = {"rho": float(rho2), "p_two_sided": float(p2)}
    # P7 cross-check with H38 f_scaffold
    est = pl.read_parquet(ROOT / "data/processed/shared/per_period_estimates.parquet").filter(
        (pl.col("hypothesis") == "H38") & (pl.col("statistic") == "f_scaffold") & (pl.col("channel") == "activity"))
    fs = est.group_by("period_unit").agg(pl.col("estimate").mean().alias("f_scaffold"))
    j = w.filter(pl.col("c_x_raw") > 0.01).with_columns((1 - pl.col("c_x_trim") / pl.col("c_x_raw")).alias("r_x")).join(
        fs, left_on="unit_id", right_on="period_unit")
    if j.height >= 5:
        rho, p = spearmanr(j["r_x"], j["f_scaffold"])
        res["P7_spearman_rx_fscaffold"] = {"rho": float(rho), "p": float(p), "n": j.height}
    j2 = w.with_columns((pl.col("c_x_raw") - pl.col("c_x_trim")).alias("d_x")).join(fs, left_on="unit_id", right_on="period_unit")
    if j2.height >= 5:
        rho, p = spearmanr(j2["d_x"], j2["f_scaffold"])
        res["P7b_spearman_dx_fscaffold"] = {"rho": float(rho), "p": float(p), "n": j2.height}
    # P8 talk vs activity
    m = g.filter(pl.col("grid") == "trim").pivot(on="channel", index="unit_id", values="phi")
    nmsg = pl.read_parquet(L.DATA / "bins15.parquet").group_by("unit_id").agg(pl.col("msg").sum().alias("nmsg"))
    m = m.join(nmsg, on="unit_id").filter(pl.col("nmsg") >= 300).drop_nulls(["msg", "activity"])
    res["P8_phi_msg_gt_act_share"] = float((m["msg"] > m["activity"]).mean()) if m.height else np.nan
    res["P8_n"] = m.height
    res["phi_msg_trim"] = med(m["msg"]); res["phi_act_trim_msgunits"] = med(m["activity"])
    # all channels summary
    res["summary"] = {f"{ch}_{gr}": {k: med(g.filter((pl.col("channel") == ch) & (pl.col("grid") == gr))[k])["median"]
                                     for k in ("b", "c_T", "c_x", "c_xw", "phi", "fano_med", "mu_med")}
                      for ch in ("activity", "calls", "msg", "commit") for gr in ("raw", "trim")}
    return res


if __name__ == "__main__":
    main()
