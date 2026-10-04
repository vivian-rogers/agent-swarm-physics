"""H42: collect per-unit JSONs into tables, score P1-P9, consistency across regimes, period verdicts.

Writes data/processed/H42-readout-hawkes-kernel/{units.parquet, scores.json, periods.parquet}.
Usage: uv run python hypotheses/H42-readout-hawkes-kernel/analysis/summarize.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

import h42lib as L  # noqa: E402

FLOOR = 1e-3   # n_cross floor for log-scale consistency statistics
FIELD_FLOOR = 0.05   # A3: max world-B n_cross produced by a shared 15-min field with no cross-excitation (synthetic 0.046)


def cvpe(spec):
    return spec["cv_ll"] / spec["cv_n"] if spec.get("cv_n") else np.nan


def tau_mean(contrib, fam):
    num = sum(float(k.split("_")[1]) * v for k, v in contrib.items() if L.colfam(k) == fam)
    den = sum(v for k, v in contrib.items() if L.colfam(k) == fam)
    return num / den if den > 0 else np.nan


def unit_row(r):
    row = {k: r[k] for k in ("unit_id", "goal_no", "regime", "n_days", "n_agents", "n_talk")}
    for w in ("pr", "A", "B"):
        T = r["talk"][w]
        meta = T["meta"]
        if w == "pr":
            row.update({"n_events": meta["n_events"], "n_pairs": meta["n_pairs"],
                        "rec_per_msg": meta.get("recipients_per_msg", meta["n_pairs"] / max(meta["n_msgs"], 1)),
                        "lag_med": meta["readout_lag_med"], "lag_q90": meta["readout_lag_q90"],
                        "lag_mean": meta["readout_lag_mean"]})
        for s, v in T["specs"].items():
            p = f"{w}:{s}"
            row[f"{p}:nx"] = v["n_cross"]
            row[f"{p}:ns"] = v["n_self"]
            row[f"{p}:ll"] = v["ll"]
            row[f"{p}:cv"] = cvpe(v)
            c = v.get("contrib", {})
            if s in ("B", "C", "C_g") and v["n_cross"] > 0:
                bm = {k: x for k, x in c.items() if L.colfam(k) == "B"}
                tot = sum(bm.values())
                if tot > 0:
                    row[f"{p}:B01"] = (bm.get("B_0", 0) + bm.get("B_1", 0)) / tot
                    row[f"{p}:B0"] = bm.get("B_0", 0) / tot
                row[f"{p}:Bshare"] = tot / v["n_cross"]
            if s in ("A", "A_H03", "B_t", "A_g", "C"):
                for fam in ("A", "H", "Bt", "Ag"):
                    tm = tau_mean(c, fam)
                    if np.isfinite(tm):
                        row[f"{p}:tau_{fam}"] = tm
    # nulls
    N = r["talk_nulls"]
    for w, nl in N.items():
        for kind in ("shift", "dayblock"):
            reps = nl.get(kind, [])
            if not reps:
                continue
            for s in reps[0]:
                if s == "S0":
                    continue
                vals = np.array([x[s]["n_cross"] for x in reps])
                row[f"{w}:{s}:{kind}_q95"] = float(np.quantile(vals, 0.95))
                row[f"{w}:{s}:{kind}_mean"] = float(vals.mean())
                row[f"{w}:{s}:{kind}_max"] = float(vals.max())
            if w == "pr" and kind == "shift":
                d = np.array([x["B"]["ll"] - x["A"]["ll"] for x in reps])
                row["pr:dBA_in_null_q95"] = float(np.quantile(d, 0.95))
        cvs = nl.get("shift_cv", [])
        if cvs:
            if w == "pr":
                row["pr:dcvBA_null"] = float(np.mean([(x["B"]["cv_ll"] - x["A"]["cv_ll"]) / x["B"]["cv_n"] for x in cvs]))
                row["pr:dcvB0_null"] = float(np.mean([(x["B"]["cv_ll"] - x["S0"]["cv_ll"]) / x["B"]["cv_n"] for x in cvs]))
            if w == "B":
                row["B:dcvBAg_null"] = float(np.mean([(x["B"]["cv_ll"] - x["A_g"]["cv_ll"]) / x["B"]["cv_n"] for x in cvs]))
                row["B:dcvB0_null"] = float(np.mean([(x["B"]["cv_ll"] - x["S0"]["cv_ll"]) / x["B"]["cv_n"] for x in cvs]))
    # sensitivity
    for var, d in r.get("sens", {}).items():
        for w, blk in d.items():
            for s, v in blk.items():
                row[f"sens_{var}:{w}:{s}:nx"] = v["n_cross"]
                row[f"sens_{var}:{w}:{s}:cv"] = cvpe(v)
    # activity
    if "act" in r:
        for s, v in r["act"]["specs"].items():
            row[f"act:{s}:nx"] = v["n_cross"]
            row[f"act:{s}:cv"] = cvpe(v)
            row[f"act:{s}:ll"] = v["ll"]
            for fam in ("Av", "Ai", "Bv", "Bi"):
                row[f"act:{s}:n_{fam}"] = v.get(f"n_{fam}", 0.0)
        row["act:n_events"] = r["act"]["meta"]["n_events"]
        an = r["act_nulls"]["shift"]
        for s in ("A", "B"):
            row[f"act:{s}:null_max"] = float(max(x[s]["n_cross"] for x in an))
            for fam in ("Av", "Ai", "Bv", "Bi"):
                row[f"act:{s}:null_n_{fam}_max"] = float(max(x[s].get(f"n_{fam}", 0) for x in an))
            row[f"act:{s}:null_ll_max"] = float(max(x[s]["ll"] - x["S0"]["ll"] for x in an))
    return row


def load_units() -> pl.DataFrame:
    rows = []
    for p in sorted(L.DATA.glob("G*/units/*.json")):
        rows.append(unit_row(json.loads(p.read_text())))
    df = pl.DataFrame(rows, infer_schema_length=None)
    lu = L.list_units().select("unit_id", "mode", "n_rooms", "cv", "n_calls")
    return df.join(lu, on="unit_id", how="left")


def frac(x):
    x = np.asarray(x, bool)
    return float(x.mean()) if len(x) else np.nan


def consistency(df, col):
    v = df.select("regime", col).drop_nulls()
    if len(v) == 0:
        return {}
    x = np.log(np.maximum(v[col].to_numpy(), FLOOR))
    med = v.group_by("regime").agg(pl.col(col).median().alias("m")).sort("regime")
    m = dict(zip(med["regime"].to_list(), med["m"].to_list()))
    mm = [max(val, FLOOR) for val in m.values()]
    return {"regime_medians": m, "max_min_ratio": float(max(mm) / min(mm)) if mm else np.nan,
            "cv_log": float(np.std(x) / abs(np.mean(x))) if abs(np.mean(x)) > 0 else np.nan,
            "sd_log": float(np.std(x)), "n": int(len(x)), "frac_floor": float((v[col].to_numpy() <= FLOOR).mean())}


def score(df: pl.DataFrame) -> dict:
    cvd = df.filter(pl.col("cv") == True)  # noqa: E712
    S = {"n_units": len(df), "n_cv_units": len(cvd)}
    dBA = (cvd["pr:B:cv"] - cvd["pr:A:cv"]).to_numpy()
    S["P1_pr"] = {"frac_B_gt_A": frac(dBA > 0), "median_dBA_per_event": float(np.median(dBA)),
                  "by_regime": {g: frac((sub["pr:B:cv"] - sub["pr:A:cv"]).to_numpy() > 0)
                                for (g,), sub in cvd.group_by(["regime"])}}
    gB = (cvd["B:B:cv"] - cvd["B:S0:cv"]).to_numpy()
    gA = (cvd["A:A:cv"] - cvd["A:S0:cv"]).to_numpy()
    S["P1_amended"] = {"frac_crossgainB_gt_crossgainA": frac(gB > gA), "median_gain_B": float(np.median(gB)),
                       "median_gain_A": float(np.median(gA)), "frac_gainB_pos": frac(gB > 0), "frac_gainA_pos": frac(gA > 0),
                       "by_regime": {g: {"gainB_gt_gainA": frac((s["B:B:cv"] - s["B:S0:cv"]).to_numpy() >
                                                                (s["A:A:cv"] - s["A:S0:cv"]).to_numpy()),
                                         "gainB_pos": frac((s["B:B:cv"] - s["B:S0:cv"]).to_numpy() > 0)}
                                     for (g,), s in cvd.group_by(["regime"])}}
    d_in = (df["pr:B:ll"] - df["pr:A:ll"]).to_numpy()
    S["P2"] = {"frac_real_gt_null_q95": frac(d_in > df["pr:dBA_in_null_q95"].to_numpy()),
               "frac_cv_gain_gt_null_pr": frac((cvd["pr:B:cv"] - cvd["pr:A:cv"]).to_numpy() > cvd["pr:dcvBA_null"].to_numpy()),
               "frac_cv_gain_gt_null_B": frac((cvd["B:B:cv"] - cvd["B:A_g:cv"]).to_numpy() > cvd["B:dcvBAg_null"].to_numpy())}
    rB, rA = df["pr:B:nx"].to_numpy(), df["pr:A:nx"].to_numpy()
    wB, wA = df["B:B:nx"].to_numpy(), df["A:A:nx"].to_numpy()
    S["P3_pr"] = {"frac_B_gt_A": frac(rB > rA), "median_ratio": float(np.median(np.maximum(rB, FLOOR) / np.maximum(rA, FLOOR))),
                  "median_nx_B": float(np.median(rB)), "median_nx_A": float(np.median(rA))}
    S["P3_amended"] = {"frac_B_gt_A": frac(wB > wA), "median_ratio": float(np.median(np.maximum(wB, FLOOR) / np.maximum(wA, FLOOR))),
                       "median_nx_worldB_B": float(np.median(wB)), "median_nx_worldA_A": float(np.median(wA)),
                       "median_nx_worldA_H03": float(np.median(df["A:A_H03:nx"].to_numpy())),
                       "median_nx_worldA_Bt": float(np.median(df["A:B_t:nx"].to_numpy()))}
    S["P4"] = {c: consistency(df, c) for c in ("pr:B:nx", "pr:A:nx", "B:B:nx", "A:A:nx", "A:A_H03:nx", "B:A_g:nx")}
    S["P5"] = {"median_B01_pr": float(np.nanmedian(df["pr:B:B01"].to_numpy())) if "pr:B:B01" in df.columns else np.nan,
               "median_B01_worldB": float(np.nanmedian(df["B:B:B01"].to_numpy())) if "B:B:B01" in df.columns else np.nan,
               "median_C_Bshare_pr": float(np.nanmedian(df["pr:C:Bshare"].to_numpy())) if "pr:C:Bshare" in df.columns else np.nan,
               "median_C_Bshare_worldB": float(np.nanmedian(df["B:C:Bshare"].to_numpy())) if "B:C:Bshare" in df.columns else np.nan,
               "median_Cg_Bshare_worldB": float(np.nanmedian(df["B:C_g:Bshare"].to_numpy())) if "B:C_g:Bshare" in df.columns else np.nan}
    db = df.filter(pl.col("pr:B:dayblock_mean").is_not_null())
    S["P6"] = {"pr_frac_gt_shift_q95": frac(df["pr:B:nx"].to_numpy() > df["pr:B:shift_q95"].to_numpy()),
               "pr_frac_gt_dayblock_mean": frac(db["pr:B:nx"].to_numpy() > db["pr:B:dayblock_mean"].to_numpy()),
               "B_frac_gt_shift_q95": frac(df["B:B:nx"].to_numpy() > df["B:B:shift_q95"].to_numpy()),
               "B_frac_gt_dayblock_mean": frac(db["B:B:nx"].to_numpy() > db["B:B:dayblock_mean"].to_numpy()),
               "B_frac_gt_dayblock_max": frac(db["B:B:nx"].to_numpy() > db["B:B:dayblock_max"].to_numpy()),
               "A_frac_gt_shift_q95": frac(df["A:A:nx"].to_numpy() > df["A:A:shift_q95"].to_numpy())}
    S["P7"] = {"frac_B_ge_Bt": frac((cvd["pr:B:cv"] - cvd["pr:B_t:cv"]).to_numpy() >= 0)}
    S["P8"] = {"pr_frac_B_ge_Ag": frac((cvd["pr:B:cv"] - cvd["pr:A_g:cv"]).to_numpy() >= 0),
               "B_frac_B_ge_Ag": frac((cvd["B:B:cv"] - cvd["B:A_g:cv"]).to_numpy() >= 0),
               "B_median_dBAg": float(np.median((cvd["B:B:cv"] - cvd["B:A_g:cv"]).to_numpy())),
               "B_frac_Cg_gt_B": frac((cvd["B:C_g:cv"] - cvd["B:B:cv"]).to_numpy() > 0),
               "B_frac_C_gt_B": frac((cvd["B:C:cv"] - cvd["B:B:cv"]).to_numpy() > 0)}
    if "act:B:cv" in df.columns:
        ac = cvd.filter(pl.col("act:B:cv").is_not_null() & pl.col("act:B:cv").is_not_nan())
        S["P9"] = {"frac_B_gt_A": frac((ac["act:B:cv"] - ac["act:A:cv"]).to_numpy() > 0),
                   "median_dBA": float(np.median((ac["act:B:cv"] - ac["act:A:cv"]).to_numpy())),
                   "n_cv_units": len(ac),
                   "frac_Bi_within_null": frac(df["act:B:n_Bi"].to_numpy() <= df["act:B:null_n_Bi_max"].to_numpy() * 1.0 + 1e-9),
                   "frac_Bv_gt_null": frac(df["act:B:n_Bv"].to_numpy() > df["act:B:null_n_Bv_max"].to_numpy()),
                   "frac_Bll_gt_null": frac((df["act:B:ll"] - df["act:S0:ll"]).to_numpy() > df["act:B:null_ll_max"].to_numpy()),
                   "median_n_Bv": float(np.median(df["act:B:n_Bv"].to_numpy())),
                   "median_n_Bi": float(np.median(df["act:B:n_Bi"].to_numpy())),
                   "median_n_Av": float(np.median(df["act:A:n_Av"].to_numpy())),
                   "median_n_Ai": float(np.median(df["act:A:n_Ai"].to_numpy()))}
    # cross-world comparison: absolute held-out log-likelihood per event (event sets differ by < 2%: world B drops
    # messages before an agent's first receiving call)
    bestB = np.max(np.column_stack([cvd[f"B:{x}:cv"].to_numpy() for x in ("S0", "B", "A_g", "C", "C_g")]), axis=1)
    bestA = np.max(np.column_stack([cvd[f"A:{x}:cv"].to_numpy() for x in ("S0", "A", "A_H03", "B_t")]), axis=1)
    bestP = np.max(np.column_stack([cvd[f"pr:{x}:cv"].to_numpy() for x in ("S0", "A", "A_H03", "A_g", "B", "B_t", "C")]), axis=1)
    S["worlds"] = {"frac_bestB_gt_bestA": frac(bestB > bestA), "median_bestB_minus_bestA": float(np.median(bestB - bestA)),
                   "median_S0B_minus_S0A": float(np.median((cvd["B:S0:cv"] - cvd["A:S0:cv"]).to_numpy())),
                   "frac_bestB_gt_bestPr": frac(bestB > bestP), "median_bestB_minus_bestPr": float(np.median(bestB - bestP)),
                   "best_spec_worldB": {k: int(v) for k, v in zip(*np.unique(np.array(["S0", "B", "A_g", "C", "C_g"])[np.argmax(np.column_stack([cvd[f"B:{x}:cv"].to_numpy() for x in ("S0", "B", "A_g", "C", "C_g")]), axis=1)], return_counts=True))},
                   "best_spec_worldA": {k: int(v) for k, v in zip(*np.unique(np.array(["S0", "A", "A_H03", "B_t"])[np.argmax(np.column_stack([cvd[f"A:{x}:cv"].to_numpy() for x in ("S0", "A", "A_H03", "B_t")]), axis=1)], return_counts=True))}}
    nz = df.filter(pl.col("B:B:nx") > 0.005)
    S["P5"]["median_B01_worldB_nonzero"] = float(np.nanmedian(nz["B:B:B01"].to_numpy()))
    S["P5"]["median_B0_worldB_nonzero"] = float(np.nanmedian(nz["B:B:B0"].to_numpy()))
    S["P5"]["n_nonzero_worldB"] = len(nz)
    # sensitivity
    sens = {}
    for var in ("lo", "hi", "trim"):
        c1 = f"sens_{var}:B:B:nx"
        if c1 in df.columns:
            sens[var] = {"median_nx_B_worldB": float(np.median(df[c1].to_numpy())),
                         "median_ratio_to_point": float(np.median(np.maximum(df[c1].to_numpy(), FLOOR) /
                                                                  np.maximum(df["B:B:nx"].to_numpy(), FLOOR))),
                         "median_nx_B_pr": float(np.median(df[f"sens_{var}:pr:B:nx"].to_numpy())),
                         "frac_gainB_pos": frac((cvd[f"sens_{var}:B:B:cv"] - cvd[f"sens_{var}:B:S0:cv"]).to_numpy() > 0)}
    S["sensitivity"] = sens
    return S


def period_verdicts(df: pl.DataFrame) -> pl.DataFrame:
    rows = []
    for (g,), sub in df.group_by(["goal_no"]):
        c = sub.filter(pl.col("cv") == True)  # noqa: E712
        r = {"goal_no": g, "units": ",".join(sorted(sub["unit_id"].to_list())), "regime": ",".join(sorted(set(sub["regime"].to_list()))),
             "n_cv": len(c)}
        if len(c) == 0:
            r["verdict_pr"] = "descriptive"
            r["verdict_am"] = "descriptive"
        else:
            w = c["n_events"].to_numpy()
            dBA = float(((c["pr:B:cv"] - c["pr:A:cv"]).to_numpy() * w).sum())
            bx = float(np.average(c["pr:B:nx"].to_numpy(), weights=w)); ax = float(np.average(c["pr:A:nx"].to_numpy(), weights=w))
            nul = bool((c["pr:B:nx"].to_numpy() > c["pr:B:shift_q95"].to_numpy()).mean() > 0.5)
            r.update(dBA_pr=dBA, nxB_pr=bx, nxA_pr=ax, beats_null_pr=nul)
            if dBA > 0 and bx > ax and nul:
                r["verdict_pr"] = "supported"
            elif dBA <= 0 and bx <= ax:
                r["verdict_pr"] = "failed"
            else:
                r["verdict_pr"] = "mixed"
            # amended reading: world-B read-out cross gain vs world-A exponential cross gain, and world-B null
            gB = float(((c["B:B:cv"] - c["B:S0:cv"]).to_numpy() * w).sum())
            gA = float(((c["A:A:cv"] - c["A:S0:cv"]).to_numpy() * w).sum())
            bxw = float(np.average(c["B:B:nx"].to_numpy(), weights=w)); axw = float(np.average(c["A:A:nx"].to_numpy(), weights=w))
            dbm = c["B:B:dayblock_max"].to_numpy() if "B:B:dayblock_max" in c.columns else np.full(len(c), np.nan)
            nulB = bool(np.nanmean((c["B:B:nx"].to_numpy() > np.nan_to_num(dbm, nan=np.inf)) &
                                   (c["B:B:nx"].to_numpy() > c["B:B:shift_q95"].to_numpy())) > 0.5)
            r.update(gainB=gB, gainA=gA, nxB_w=bxw, nxA_w=axw, beats_null_B=nulB)
            r["above_field_floor"] = bxw > FIELD_FLOOR
            if gB > 0 and gB > gA and nulB and bxw > FIELD_FLOOR:
                r["verdict_am"] = "supported"
            elif gB <= 0 or not nulB:
                r["verdict_am"] = "failed"
            else:
                r["verdict_am"] = "mixed"
        rows.append(r)
    return pl.DataFrame(rows, infer_schema_length=None).sort("goal_no")


def main():
    df = load_units()
    df.write_parquet(L.DATA / "units.parquet")
    S = score(df)
    (L.DATA / "scores.json").write_text(json.dumps(S, indent=1, default=float))
    pv = period_verdicts(df)
    pv.write_parquet(L.DATA / "periods.parquet")
    print(json.dumps(S, indent=1, default=float))
    print(pv)


if __name__ == "__main__":
    main()
