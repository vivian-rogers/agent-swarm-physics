"""H67 round-2 synthesis: R3 ladder attribution, R4 multi-hop pools and the Fano check, R1 chat clock, prediction
scoring, per-period pools and verdicts, estimates rows, figure. Reads round2/units.parquet (r2_run.py), round-1
results, H50's unit table and H111's unit results (read as data, never recomputed).
Writes round2/{periods.parquet, summary.json}, figures/round2_col.pdf, and per_period_estimates rows.

    uv run python hypotheses/H67-lagged-criticality-dial/analysis/r2_summarize.py
"""
from __future__ import annotations

import json
import math
import sys

import numpy as np
import polars as pl
from scipy import stats

import h67lib as L
import r2lib as R

sys.path.insert(0, str(L.ROOT / "infra/shared"))
import estimates as E  # noqa: E402

FIG = L.ROOT / "hypotheses/H67-lagged-criticality-dial/figures"
H111 = L.ROOT / "data/processed/H111-talk-fano-sum-rule"
RUNGS = ["L0", "L1", "L2", "L3", "L4", "L4W", "L5", "L6", "L7", "L8", "L9", "L9b"]
PATH = ["L1", "L2", "L3", "L4", "L8", "L9"]          # main path; one change per step
STEP_NAME = {("L1", "L2"): "trimming", ("L2", "L3"): "bandwidth W -> w_bar", ("L3", "L4"): "call-class cells",
             ("L4", "L8"): "pair RD + shifted-time placebo -> call counts + in-flight placebo",
             ("L8", "L9"): "controls (R_o, lagged reads, y_{c-1}, exogenous)"}


def re_pool(est, se):
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    if not len(est):
        return {"mean": np.nan, "se": np.nan, "lo": np.nan, "hi": np.nan, "k": 0, "tau2": np.nan}
    w = 1 / se ** 2
    m = (w * est).sum() / w.sum()
    Q = (w * (est - m) ** 2).sum()
    tau2 = max(0.0, (Q - (len(est) - 1)) / (w.sum() - (w ** 2).sum() / w.sum())) if len(est) > 1 else 0.0
    ws = 1 / (se ** 2 + tau2)
    mm = (ws * est).sum() / ws.sum()
    s = np.sqrt(1 / ws.sum())
    return {"mean": float(mm), "se": float(s), "lo": float(mm - 1.96 * s), "hi": float(mm + 1.96 * s),
            "k": int(len(est)), "tau2": float(tau2)}


def ivw(est, se):
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    if not ok.any():
        return np.nan
    w = 1 / se[ok] ** 2
    return float((w * est[ok]).sum() / w.sum())


def med(s):
    s = s.drop_nulls().drop_nans() if s.dtype in (pl.Float64, pl.Float32) else s.drop_nulls()
    return float(s.median()) if len(s) else np.nan


def invert_phi(phi, present):
    """g with unit_phi_pred(g) = phi (bisection on [-0.9, 0.99])."""
    if not np.isfinite(phi):
        return np.nan
    f = lambda g: R.unit_phi_pred(g, present) - phi  # noqa: E731
    lo, hi = -0.9, 0.99
    flo, fhi = f(lo), f(hi)
    if not (np.isfinite(flo) and np.isfinite(fhi)) or flo * fhi > 0:
        return lo if phi < R.unit_phi_pred(lo, present) else (hi if phi > R.unit_phi_pred(hi, present) else np.nan)
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if f(mid) * flo > 0:
            lo, flo = mid, f(mid)
        else:
            hi = mid
    return 0.5 * (lo + hi)


def main():
    u2 = pl.read_parquet(R.R2 / "units.parquet").filter(pl.col("ok"))
    u1 = pl.read_parquet(L.OUT / "results" / "units.parquet").select(
        "unit_id", "goal_no", "regime", "N", "n_rows_trim", "g", "g_lo", "g_hi", "g_se", "g3", "g_eq", "first_day",
        "last_day")
    h50 = pl.read_parquet(L.ROOT / "data/processed/H50-field-vs-coupling-transfer-lag/unit_table.parquet").select(
        pl.col("unit").alias("unit_id"), pl.col("J1").alias("J_L0"), pl.col("J1_se").alias("J_L0_se"))
    h111 = pl.read_parquet(H111 / "results" / "units.parquet").select(
        "unit_id", "phi_10", "phi_10_se", "phi_10_lo", "phi_10_hi", "phi_pred", "r_F")
    u = u1.join(u2, on="unit_id", how="inner").join(h50, on="unit_id", how="left").join(h111, on="unit_id",
                                                                                         how="left")
    # rung gains and SEs on one scale (m_bar r_bar x per-read jump)
    u = u.with_columns((pl.col("J_L0") * pl.col("gmul")).alias("g_L0"),
                       (pl.col("J_L0_se") * pl.col("gmul")).alias("g_L0_se"),
                       (pl.col("J_L9_se") * pl.col("gmul")).alias("g_L9_se"))
    for t in ("L1", "L2", "L3", "L4", "L4W", "L5", "L7", "L8"):
        u = u.with_columns((pl.col(f"{t}_J_se") * pl.col("gmul")).alias(f"g_{t}_se"))
    S = {"n_units": u.height}
    # ================================================================ R3
    r3 = {}
    x = u.filter(pl.col("J_L0").is_not_null() & pl.col("L1_J").is_not_null())
    rho = stats.spearmanr(x["L1_J"], x["J_L0"])
    ratio = (x["L1_J"] / x["J_L0"]).filter((x["J_L0"].abs() > 0.005))
    r3["reproduction"] = {"spearman": float(rho.statistic), "p": float(rho.pvalue), "n": x.height,
                          "median_ratio_L1_over_L0 (|J_L0|>0.005)": float(ratio.median()),
                          "median_diff_J": float((x["L1_J"] - x["J_L0"]).median()),
                          "median_J_L0": float(x["J_L0"].median()), "median_J_L1": float(x["L1_J"].median())}
    for reg in ("I", "II", "III"):
        s = u.filter(pl.col("regime") == reg)
        d = {"n": s.height}
        for t in RUNGS:
            col = f"g_{t}"
            if col in s.columns:
                d[t] = {"median": med(s[col])}
                if f"{col}_se" in s.columns:
                    p = re_pool(s[col], s[f"{col}_se"])
                    d[t].update({"pool": p["mean"], "pool_lo": p["lo"], "pool_hi": p["hi"]})
        steps = []
        tot = d["L1"]["median"] - d["L9"]["median"]
        totp = d["L1"].get("pool", np.nan) - d["L9"].get("pool", np.nan)
        for a, b in zip(PATH[:-1], PATH[1:]):
            dm = d[a]["median"] - d[b]["median"]
            dp = d[a].get("pool", np.nan) - d[b].get("pool", np.nan)
            pdiff = (s[f"g_{a}"] - s[f"g_{b}"]).drop_nulls().drop_nans()
            steps.append({"step": f"{a}->{b}", "what": STEP_NAME[(a, b)], "drop_median": dm,
                          "share_median": dm / tot if tot else np.nan, "drop_pool": dp,
                          "share_pool": dp / totp if totp else np.nan,
                          "paired_median_diff": float(pdiff.median()) if len(pdiff) else np.nan,
                          "sign_share_positive": float((pdiff > 0).mean()) if len(pdiff) else np.nan})
        d["path_total_median"] = tot
        d["path_total_pool"] = totp
        d["steps"] = steps
        side = {}
        for a, b, what in (("L4", "L5", "shifted-time placebo inside the pair RD (L4 with vs L5 without)"),
                           ("L2", "L4W", "cells at H50's bandwidth"), ("L7", "L8", "cells in the call design"),
                           ("L1", "L7", "pair RD (H50) vs pooled call counts"), ("L9", "L9b", "H67 window capped at W")):
            pd_ = (s[f"g_{a}"] - s[f"g_{b}"]).drop_nulls().drop_nans()
            side[f"{a}->{b}"] = {"what": what, "drop_median": d[a]["median"] - d[b]["median"],
                                 "drop_pool": d[a].get("pool", np.nan) - d[b].get("pool", np.nan),
                                 "paired_median_diff": float(pd_.median()) if len(pd_) else np.nan}
        d["side"] = side
        d["first_stage_L6fs_median"] = med(s["L6fs_J"])
        d["first_stage_L1fs_median"] = med(s["L1fs_J"])
        r3[reg] = d
    # unit pooling: period pools of L1 and L9 by IVW and RE
    pp = []
    for (g,), s in u.group_by(["goal_no"]):
        pp.append({"goal_no": g, "regime": s["regime"][0],
                   "L1_ivw": ivw(s["g_L1"], s["g_L1_se"]), "L1_re": re_pool(s["g_L1"], s["g_L1_se"])["mean"],
                   "L9_ivw": ivw(s["g_L9"], s["g_L9_se"]), "L9_re": re_pool(s["g_L9"], s["g_L9_se"])["mean"]})
    pp = pl.DataFrame(pp)
    r3["unit_pooling"] = {"median_L1_ivw_minus_re": float((pp["L1_ivw"] - pp["L1_re"]).median()),
                          "median_L9_ivw_minus_re": float((pp["L9_ivw"] - pp["L9_re"]).median()),
                          "max_abs_L9_ivw_minus_re": float((pp["L9_ivw"] - pp["L9_re"]).abs().max())}
    S["r3"] = r3
    # ================================================================ R4
    r4 = {}
    s3 = u.filter(pl.col("regime") == "III")
    for h in range(1, 6):
        p = re_pool(s3[f"r4_G{h}"], s3[f"r4_G{h}_se"])
        r4[f"G{h}"] = {"median": med(s3[f"r4_G{h}"]), "pool": p["mean"], "lo": p["lo"], "hi": p["hi"], "k": p["k"]}
        pdl = re_pool(s3[f"r4_delta{h}"], s3[f"r4_delta{h}_se"])
        r4[f"delta{h}"] = {"median": med(s3[f"r4_delta{h}"]), "pool": pdl["mean"], "lo": pdl["lo"], "hi": pdl["hi"]}
    r4["g_lag_r1_median_III"] = med(s3["g"])
    r4["g_lag_r1_pool_III"] = re_pool(s3["g"], s3["g_se"])["mean"]
    r4["g3_r1_median_III"] = med(s3["g3"])
    r4["noslope_G5_median_III"] = med(s3["r4ns_G5"])
    r4["units_G5_lo_ge_1"] = int((u["r4_G5_lo"] >= 1).sum())
    r4["units_G5_hi_lt_1"] = int((u["r4_G5_hi"] < 1).sum())
    r4["n_units_G5"] = int(u["r4_G5"].is_not_null().sum())
    r4["units_G5_hi_lt_1_III"] = int((s3["r4_G5_hi"] < 1).sum())
    r4["n_units_G5_III"] = int(s3["r4_G5"].is_not_null().sum())
    # Fano check: Phi_pred at the pooled regime-III G5 (unit room sizes), against H111's Phi_obs(10)
    fano = []
    G5p, G5se = r4["G5"]["pool"], (r4["G5"]["hi"] - r4["G5"]["lo"]) / 3.92
    for r in s3.iter_rows(named=True):
        f = H111 / "present" / f"{r['unit_id']}.parquet"
        if not f.exists() or r["phi_10"] is None or not np.isfinite(r["phi_10"] or np.nan):
            continue
        pres = pl.read_parquet(f)
        pg5 = R.unit_phi_pred(G5p, pres)
        pglag = R.unit_phi_pred(r["g"], pres)
        dlog = (math.log(R.unit_phi_pred(G5p + 0.01, pres)) - math.log(R.unit_phi_pred(G5p - 0.01, pres))) / 0.02
        gF = invert_phi(r["phi_10"], pres)
        gF_lo = invert_phi(r["phi_10_lo"], pres) if r["phi_10_lo"] is not None else np.nan
        gF_hi = invert_phi(r["phi_10_hi"], pres) if r["phi_10_hi"] is not None else np.nan
        fano.append({"unit_id": r["unit_id"], "phi_obs": r["phi_10"], "phi_pred_G5pool": pg5,
                     "phi_pred_glag_mine": pglag, "phi_pred_h111": r["phi_pred"],
                     "logr": math.log(r["phi_10"] / pg5),
                     "logr_se": math.sqrt((r["phi_10_se"] / r["phi_10"]) ** 2 + (dlog * G5se) ** 2),
                     "g_fano": gF, "g_fano_se": (gF_hi - gF_lo) / 3.92 if np.isfinite(gF_hi - gF_lo) else np.nan,
                     "g_lag": r["g"], "G5": r["r4_G5"]})
    fz = pl.DataFrame(fano)
    p = re_pool(fz["logr"], fz["logr_se"])
    pf = re_pool(fz["g_fano"], fz["g_fano_se"])
    r4["fano"] = {"k": fz.height, "r_F_G5pool": math.exp(p["mean"]), "r_F_lo": math.exp(p["lo"]),
                  "r_F_hi": math.exp(p["hi"]),
                  "check_phi_pred_glag_vs_h111_median_ratio": float((fz["phi_pred_glag_mine"]
                                                                      / fz["phi_pred_h111"]).median()),
                  "g_fano_pool": pf["mean"], "g_fano_lo": pf["lo"], "g_fano_hi": pf["hi"],
                  "g_fano_median": float(fz["g_fano"].median()),
                  "spearman_gfano_glag": float(stats.spearmanr(fz["g_fano"], fz["g_lag"]).statistic),
                  "spearman_gfano_G5": float(stats.spearmanr(fz["g_fano"], fz["G5"]).statistic)}
    S["r4"] = r4
    # ================================================================ R1
    r1 = {}
    s1 = u.filter((pl.col("regime") == "I") & pl.col("g_chat").is_not_null())
    s1 = s1.with_columns((pl.col("g_cu") + pl.col("g_chat")).alias("g_I"),
                         (pl.col("g_cu_se") ** 2 + pl.col("g_chat_se") ** 2).sqrt().alias("g_I_se"))
    r1["n_units"] = s1.height
    r1["g_chat_median"] = med(s1["g_chat"])
    r1["g_chat_pool"] = re_pool(s1["g_chat"], s1["g_chat_se"])
    r1["share_Jchat_pos95"] = float((s1["chat_J_lo"] > 0).mean())
    r1["share_Jchat_neg95"] = float((s1["chat_J_hi"] < 0).mean())
    r1["g_cu_median"] = med(s1["g_cu"])
    r1["g_cu_pool"] = re_pool(s1["g_cu"], s1["g_cu_se"])
    r1["g_I_median"] = med(s1["g_I"])
    r1["g_I_pool"] = re_pool(s1["g_I"], s1["g_I_se"])
    r1["g_lag_r1_median_I"] = med(s1["g"])
    r1["chat_base_talk_median"] = med(s1["chat_base_talk"])
    lg = s1.filter(pl.col("g_chat_logged").is_not_null())
    r1["logged"] = {"n_units": lg.height, "pool": re_pool(lg["g_chat_logged"], lg["g_chat_logged_se"]),
                    "median": med(lg["g_chat_logged"])}
    pn = re_pool(s1["chat_J1_named"], s1["chat_J1_named_se"])
    pu = re_pool(s1["chat_J1_unnamed"], s1["chat_J1_unnamed_se"])
    r1["named"] = {"J_named_pool": pn, "J_unnamed_pool": pu,
                   "ratio": pn["mean"] / pu["mean"] if pu["mean"] and abs(pu["mean"]) > 1e-6 else np.nan}
    # Fano with g_I (regime I)
    fr = []
    for r in s1.iter_rows(named=True):
        f = H111 / "present" / f"{r['unit_id']}.parquet"
        if not f.exists() or r["phi_10"] is None or not np.isfinite(r["phi_10"] or np.nan) or r["phi_10_se"] is None:
            continue
        pres = pl.read_parquet(f)
        gi = r["g_I"] if r["g_I"] is not None else np.nan
        if not np.isfinite(gi) or gi >= 0.95 or r["g_I_se"] is None:
            continue
        pg = R.unit_phi_pred(gi, pres)
        dlog = (math.log(R.unit_phi_pred(gi + 0.01, pres)) - math.log(R.unit_phi_pred(gi - 0.01, pres))) / 0.02
        fr.append({"logr": math.log(r["phi_10"] / pg),
                   "se": math.sqrt((r["phi_10_se"] / r["phi_10"]) ** 2 + (dlog * r["g_I_se"]) ** 2),
                   "logr_glag": math.log(r["phi_10"] / R.unit_phi_pred(r["g"], pres)),
                   "se_glag": r["phi_10_se"] / r["phi_10"]})
    frd = pl.DataFrame(fr)
    pI = re_pool(frd["logr"], frd["se"])
    pL = re_pool(frd["logr_glag"], frd["se_glag"])
    r1["fano"] = {"k": frd.height, "r_F_gI": math.exp(pI["mean"]), "lo": math.exp(pI["lo"]), "hi": math.exp(pI["hi"]),
                  "r_F_glag_same_units": math.exp(pL["mean"]), "lo_glag": math.exp(pL["lo"]),
                  "hi_glag": math.exp(pL["hi"])}
    s2 = u.filter((pl.col("regime") == "II") & pl.col("g_chat").is_not_null())
    r1["regime_II"] = {"n": s2.height, "g_chat": s2.select("unit_id", "g_chat", "g_chat_lo", "g_chat_hi").to_dicts()}
    S["r1"] = r1
    # ================================================================ predictions
    rr3 = r3["III"]
    shares = {st["step"]: st["share_median"] for st in rr3["steps"]}
    sharesp = {st["step"]: st["share_pool"] for st in rr3["steps"]}
    sc = {}
    rep = r3["reproduction"]
    sc["R3-P1"] = {"obs": f"median L1/L0 {rep['median_ratio_L1_over_L0 (|J_L0|>0.005)']:.2f}, Spearman {rep['spearman']:.2f}",
                   "pass": bool(0.85 <= rep["median_ratio_L1_over_L0 (|J_L0|>0.005)"] <= 1.15 and rep["spearman"] >= 0.8),
                   "kill": bool(not (0.7 <= rep["median_ratio_L1_over_L0 (|J_L0|>0.005)"] <= 1.4))}
    cells_pl = shares.get("L3->L4", 0) + shares.get("L4->L8", 0)
    sc["R3-P2"] = {"obs": {"shares_median": shares, "shares_pool": sharesp},
                   "pass": bool(cells_pl >= 0.5 and abs(shares.get("L1->L2", 0)) < 0.25
                                and abs(shares.get("L2->L3", 0)) < 0.25)}
    sc["R3-P3"] = {"obs": rr3["first_stage_L6fs_median"], "pass": bool(0.8 <= rr3["first_stage_L6fs_median"] <= 1.25)}
    ri = r3["I"]
    rem = (ri["L3"]["median"] - ri["L4"]["median"]) / ri["L3"]["median"] if ri["L3"]["median"] > 0 else np.nan
    remW = (ri["L2"]["median"] - ri["L4W"]["median"]) / ri["L2"]["median"] if ri["L2"]["median"] > 0 else np.nan
    sc["R3-P4"] = {"obs": {"removed_L3_L4": rem, "removed_L2_L4W": remW}, "pass": bool(np.isfinite(rem) and rem >= 0.7)}
    sc["R3-P5"] = {"obs": "synthetic: L1 +43%/+35% at g 0.15/0.30, +0.05/+0.07 in no-coupling worlds", "pass": False}
    g5m = r4["G5"]["median"]
    glm = r4["g_lag_r1_median_III"]
    sc["R4-P1"] = {"obs": {"G5_median": g5m, "G5_pool": r4["G5"]["pool"], "ratio_median": g5m / glm},
                   "pass": bool(0.7 * glm <= g5m <= 1.5 * glm), "against": bool(g5m >= 2.5 * glm),
                   "descriptive_only": True}
    sc["R4-P2"] = {"obs": {"G3_median": r4["G3"]["median"], "G3_pool": r4["G3"]["pool"]},
                   "pass": bool(r4["G3"]["median"] < 0.20), "against": bool(r4["G3"]["median"] >= 0.28),
                   "descriptive_only": True}
    sc["R4-P3"] = {"obs": {"units_hi_lt_1": r4["units_G5_hi_lt_1"], "n": r4["n_units_G5"],
                           "units_lo_ge_1": r4["units_G5_lo_ge_1"]},
                   "pass": bool(r4["units_G5_hi_lt_1"] == r4["n_units_G5"]), "against": bool(r4["units_G5_lo_ge_1"] > 0)}
    fz_ = r4["fano"]
    sc["R4-P4"] = {"obs": fz_, "pass": bool(0.8 <= fz_["r_F_G5pool"] <= 1.25 and fz_["r_F_lo"] <= 1 <= fz_["r_F_hi"]),
                   "against": bool(fz_["r_F_G5pool"] < 0.7)}
    sc["R1-P1"] = {"obs": {"median_g_chat": r1["g_chat_median"], "share_pos95": r1["share_Jchat_pos95"],
                           "pool": r1["g_chat_pool"]},
                   "pass": bool(r1["g_chat_median"] >= 0.05 and r1["share_Jchat_pos95"] >= 1 / 3),
                   "against": bool(r1["g_chat_median"] <= 0.02 and r1["share_Jchat_pos95"] <= 0.10)}
    sc["R1-P2"] = {"obs": r1["fano"], "pass": bool(0.8 <= r1["fano"]["r_F_gI"] <= 1.25),
                   "against": bool(r1["fano"]["r_F_gI"] >= 1.25)}
    ratio = r1["named"]["ratio"]
    sc["R1-P3"] = {"obs": {"ratio": ratio, "named": r1["named"]["J_named_pool"]["mean"],
                           "unnamed": r1["named"]["J_unnamed_pool"]["mean"]},
                   "pass": bool(np.isfinite(ratio) and ratio < 3)}
    S["scores"] = sc
    # ================================================================ per-period pools and verdicts
    P = []
    for (g,), s in u.sort("unit_id").group_by(["goal_no"], maintain_order=True):
        reg = s["regime"][0]
        row = {"goal_no": g, "regime": reg, "units": s["unit_id"].to_list(), "n_rows": int(s["n_rows_trim"].sum())}
        for col in ("g_L1", "g_L4W", "g_L8", "g_L9"):
            p = re_pool(s[col], s[f"{col}_se"])
            row[col], row[col + "_lo"], row[col + "_hi"] = p["mean"], p["lo"], p["hi"]
        for h in (1, 3, 5):
            p = re_pool(s[f"r4_G{h}"], s[f"r4_G{h}_se"])
            row[f"G{h}"], row[f"G{h}_lo"], row[f"G{h}_hi"] = p["mean"], p["lo"], p["hi"]
        row["g_eq"] = float(s["g_eq"].mean())
        sc_ = s.filter(pl.col("g_chat").is_not_null())
        if sc_.height:
            # g_I falls back to g_chat where the computer-use fit is missing (unit 3)
            sc_ = sc_.with_columns((pl.col("g_cu").fill_null(0.0) + pl.col("g_chat")).alias("g_I"),
                                   (pl.col("g_cu_se").fill_null(0.0) ** 2 + pl.col("g_chat_se") ** 2).sqrt()
                                   .alias("g_I_se"))
            for col in ("g_chat", "g_cu", "g_I"):
                p = re_pool(sc_[col], sc_[f"{col}_se"])
                row[col], row[col + "_lo"], row[col + "_hi"] = p["mean"], p["lo"], p["hi"]
            p = re_pool(sc_["chat_J"], sc_["chat_J_se"])
            row["J_chat"], row["J_chat_lo"], row["J_chat_hi"] = p["mean"], p["lo"], p["hi"]
            row["n_chat_rows"] = int(sc_["chat_n_rows"].sum())
            if reg == "I":
                gI_lo_units = (sc_["g_I"] - 1.96 * sc_["g_I_se"]).max()
                gI_lo_units = -np.inf if gI_lo_units is None else gI_lo_units
                if row["n_chat_rows"] < 200:
                    v = "descriptive"
                elif (row["g_I_hi"] < 1 and row["J_chat_lo"] > 0 and row["g_I"] > row["g_eq"]):
                    v = "supported"
                elif (row["J_chat_hi"] >= 0 >= row["J_chat_lo"] or row["J_chat"] <= 0) and row["g_I"] <= row["g_eq"]:
                    v = "failed"
                elif gI_lo_units >= 1:
                    v = "failed"
                else:
                    v = "mixed"
                row["verdict_r2"] = v
        P.append(row)
    P = pl.DataFrame(P, infer_schema_length=None)
    P.write_parquet(R.R2 / "periods.parquet")
    S["r1"]["period_verdicts"] = dict(zip(*[P.filter(pl.col("regime") == "I")[c].to_list()
                                            for c in ("goal_no", "verdict_r2")]))
    (R.R2 / "summary.json").write_text(json.dumps(S, indent=1, default=float))
    print(json.dumps({k: S[k] for k in ("scores",)}, indent=1, default=float))
    if "--no-write" not in sys.argv:
        write_rows(u)
    figure(u, S)


def write_rows(u):
    rows = []
    src = "data/processed/H67-lagged-criticality-dial/round2/units.parquet"
    for r in u.iter_rows(named=True):
        base = {"period_unit": r["unit_id"], "goal_no": r["goal_no"], "channel": "talk", "role": "replication",
                "source": src, "first_day": r["first_day"], "last_day": r["last_day"], "ci_level": 0.95}
        rows.append({**base, "statistic": "readout_loop_gain_multihop_G5", "estimate": r.get("r4_G5"),
                     "ci_lo": r.get("r4_G5_lo"), "ci_hi": r.get("r4_G5_hi"), "se": r.get("r4_G5_se"),
                     "ci_kind": "percentile", "n": float(r.get("r4_n_rows") or 0), "n_kind": "receiving calls",
                     "status": "descriptive",
                     "method": "H67 r2 (R4): m_bar r_bar sum_{h<=5} delta(h); lagged in-flight design, disjoint "
                               "symmetric windows with local-linear offsets; agent x day x class cells; 1-h blocks",
                     "null": "in-flight placebo at each lagged call",
                     "notes": "descriptive: synthetic S-R4a/b failed (per-run SD 0.4-1.5; bias up to +0.14)"})
        rows.append({**base, "statistic": "h50_pair_rd_gain_reimplemented", "estimate": r.get("g_L1"),
                     "ci_lo": (r.get("L1_J_lo") or np.nan) * r["gmul"], "ci_hi": (r.get("L1_J_hi") or np.nan) * r["gmul"],
                     "ci_kind": "percentile", "n": float(r.get("L1_n_pairs") or 0), "n_kind": "message-recipient pairs",
                     "method": "H67 r2 (R3 rung L1): H50's boundary RD re-implemented (W = H50's, 2-s donut, local "
                               "linear, shifted-time placebo) x m_bar r_bar",
                     "null": "shifted-time placebo", "notes": "synthetic: +0.05 to +0.07 in no-coupling worlds"})
        rows.append({**base, "statistic": "pair_rd_gain_call_class_cells", "estimate": r.get("g_L4W"),
                     "ci_lo": (r.get("L4W_J_lo") or np.nan) * r["gmul"], "ci_hi": (r.get("L4W_J_hi") or np.nan) * r["gmul"],
                     "ci_kind": "percentile", "n": float(r.get("L4W_n_pairs") or 0), "n_kind": "message-recipient pairs",
                     "method": "H67 r2 (R3 rung L4W): L1 on the all-present window with talk demeaned in agent x day x "
                               "call-class cells", "null": "shifted-time placebo"})
        if r.get("g_chat") is not None and np.isfinite(r.get("g_chat") or np.nan):
            rows.append({**base, "statistic": "readout_loop_gain_chat_clock", "estimate": r["g_chat"],
                         "ci_lo": r.get("g_chat_lo"), "ci_hi": r.get("g_chat_hi"), "se": r.get("g_chat_se"),
                         "ci_kind": "percentile", "n": float(r.get("chat_n_rows") or 0), "n_kind": "chat-mode calls",
                         "method": "H67 r2 (R1): m_bar r_bar_chat J*_chat; chat-mode calls only, t_prev = previous chat "
                                   "call, matched-lag in-flight placebo at the chat call",
                         "null": "in-flight placebo", "notes": "lower bound: start-time error attenuates to ~0.23 x truth (synthetic)"})
            if r.get("g_cu") is not None and np.isfinite(r.get("g_cu") or np.nan):
                gi = r["g_chat"] + r["g_cu"]
                se = math.sqrt((r.get("g_chat_se") or np.nan) ** 2 + (r.get("g_cu_se") or np.nan) ** 2)
                rows.append({**base, "statistic": "readout_loop_gain_regimeI_total", "estimate": gi,
                             "ci_lo": gi - 1.96 * se, "ci_hi": gi + 1.96 * se, "se": se, "ci_kind": "se_z",
                             "n": float(r.get("chat_n_rows") or 0), "n_kind": "chat-mode calls",
                             "method": "H67 r2 (R1): g_cu (hop-1 on computer-use calls, reads at cu calls) + g_chat",
                             "null": "in-flight placebo"})
    rows = [{k: (None if (isinstance(v, float) and not np.isfinite(v)) else v) for k, v in r.items()} for r in rows]
    for r in rows:
        if r.get("ci_lo") is None or r.get("ci_hi") is None:
            r["ci_kind"] = "none"
        if r.get("estimate") is None:
            r["estimate"] = float("nan")
    rows = [r for r in rows if r["estimate"] == r["estimate"]]
    E.write_estimates(rows, hypothesis="H67")
    print("estimates rows:", len(rows))


def figure(u, S):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    FIG.mkdir(parents=True, exist_ok=True)
    col = {"I": "#2c7fb8", "II": "#7f8c8d", "III": "#c0392b"}
    fig, ax = plt.subplots(1, 3, figsize=(7.0, 2.4))
    rungs = ["L0", "L1", "L2", "L3", "L4", "L8", "L9"]
    labels = ["H50", "L1", "trim", "bw", "cells", "calls", "H67"]
    for reg in ("I", "III"):
        d = S["r3"][reg]
        y = [d[t]["median"] for t in rungs]
        ax[0].plot(range(len(rungs)), y, "o-", color=col[reg], ms=3, lw=0.9, label=f"regime {reg}")
    ax[0].axhline(0, color="k", lw=0.4)
    ax[0].set_xticks(range(len(rungs)))
    ax[0].set_xticklabels(labels, fontsize=6, rotation=45)
    ax[0].set_ylabel("loop gain g (unit median)", fontsize=7)
    ax[0].set_title("R3: H50 to H67", fontsize=7)
    ax[0].legend(fontsize=6, frameon=False)
    r4 = S["r4"]
    hs = np.arange(1, 6)
    dl = [r4[f"delta{h}"]["pool"] for h in hs]
    lo = [r4[f"delta{h}"]["lo"] for h in hs]
    hi = [r4[f"delta{h}"]["hi"] for h in hs]
    ax[1].errorbar(hs, dl, yerr=[np.array(dl) - np.array(lo), np.array(hi) - np.array(dl)], fmt="o", color=col["III"],
                   ms=3, lw=0.8)
    ax[1].axhline(0, color="k", lw=0.4)
    ax[1].set_xlabel("hop h", fontsize=7)
    ax[1].set_ylabel(r"kernel $\delta(h)$ per read (pool, III)", fontsize=7)
    ax[1].set_title("R4: descriptive", fontsize=7)
    s1 = u.filter((pl.col("regime") == "I") & pl.col("g_chat").is_not_null()).sort("goal_no")
    ax[2].errorbar(np.arange(s1.height), s1["g_chat"], yerr=[s1["g_chat"] - s1["g_chat_lo"],
                                                            s1["g_chat_hi"] - s1["g_chat"]],
                   fmt="o", color=col["I"], ms=2.5, lw=0.6, label="chat clock")
    ax[2].plot(np.arange(s1.height), s1["g"], "x", color="k", ms=3, label="hop 1, all calls (r1)")
    ax[2].axhline(0, color="k", lw=0.4)
    ax[2].set_xlabel("regime-I units (by period)", fontsize=7)
    ax[2].set_ylabel("loop gain", fontsize=7)
    ax[2].set_title("R1: chat clock", fontsize=7)
    ax[2].legend(fontsize=5.5, frameon=False)
    for a in ax:
        a.tick_params(labelsize=6)
    fig.tight_layout()
    fig.savefig(FIG / "round2_col.pdf")
    print("figure written")


if __name__ == "__main__":
    main()
