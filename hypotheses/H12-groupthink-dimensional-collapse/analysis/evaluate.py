"""H12 evaluation of P1-P10 (card + Amendment 1 + clarifications), NE34 kickoff study, H02 comparison, per-period verdicts.

Reads data/processed/H12-groupthink-dimensional-collapse/G*/{rmt_*.json, pr30_*.parquet, prday_*.parquet}.
Writes: unit_table.parquet, ne34_kickoffs.parquet, ne34_placebos.parquet, h02_compare.parquet, period_means.parquet,
outcomes.json, period_results.json (for write_period_folders.py results).

Usage: uv run python hypotheses/H12-groupthink-dimensional-collapse/analysis/evaluate.py
"""
from __future__ import annotations

import json
import math

import h12lib as L
import numpy as np
import polars as pl
from scipy.stats import mannwhitneyu, spearmanr

from write_period_folders import CONSENSUS, FREE, PERIODS, SHARED, TWO_ROOM, transitions

TOL = 1e-12


def load_all():
    rmt, p30, pday = {}, [], []
    for f in sorted(L.OUT.glob("G*/rmt_*.json")):
        r = json.loads(f.read_text()); rmt[r["unit"]] = r
    for f in sorted(L.OUT.glob("G*/pr30_*.parquet")):
        p30.append(pl.read_parquet(f))
    for f in sorted(L.OUT.glob("G*/prday_*.parquet")):
        pday.append(pl.read_parquet(f))
    units = pl.read_parquet(L.OUT / "units.parquet")
    p30 = pl.concat(p30, how="diagonal_relaxed").join(units.select("unit", "goal_no", "regime", "mode"), on="unit")
    pday = pl.concat(pday, how="diagonal_relaxed").join(units.select("unit", "goal_no", "regime", "mode"), on="unit")
    return rmt, p30, pday, units


def sig_sep(block, key, kmax):
    """Smallest permutation p among signal eigenvectors (index < kmax), or None."""
    ps = [s[key] for s in block.get("sep", [])[:kmax] if s.get(key) is not None]
    return min(ps) if ps else None


def unit_table(rmt, units):
    rows = []
    for r in units.sort("goal_no", "unit").iter_rows(named=True):
        x = rmt.get(r["unit"], {})
        a, t, c = x.get("act", {}), x.get("talk", {}), x.get("content", {})
        if not a.get("eig"):
            continue
        l1 = a["eig"][0]; ll1 = a["eig_lull"][0]
        row = {"unit": r["unit"], "goal_no": r["goal_no"], "regime": r["regime"], "mode": r["mode"], "scored": r["scored"],
               "n_days": r["n_days"], "two_room": r["unit"] in TWO_ROOM,
               "N_act": a["N"], "k_cd": a["k_cd"], "k_lull": a["k_lull"], "k_circ": a["k_circ"], "k_mp": a["k_mp"],
               "k_mpeff": a["k_mpeff"], "k_rank": a["k_rank"], "l1": l1, "edge_cd": a["edge_cd"], "l1_edge": l1 / a["edge_cd"],
               "l1_edge_lull": ll1 / a["edge_lull"], "lull_drop": 1 - (ll1 / a["edge_lull"]) / (l1 / a["edge_cd"]),
               "lull_frac": a["lull_frac"], "VR": a["VR"], "VR_l1": a["VR"] / l1, "sign_share": a["modes"][0]["sign_share"],
               "ipr": a["modes"][0]["ipr"], "tauB": a["tauB"], "l1_block": a["l1_block"], "VR_block": a["VR_block"],
               "rho_bar": a["rho_bar"], "act_p_room": sig_sep(a, "p_room", max(a["k_cd"], 1)), "act_p_lab": sig_sep(a, "p_lab", max(a["k_cd"], 1)),
               "N_talk": t.get("N"), "k_talk": t.get("k_cd"), "talk_l1_edge": (t["eig"][0] / t["edge_cd"]) if t.get("eig") else None,
               "talk_p_room": sig_sep(t, "p_room", t.get("k_cd", 0)) if t.get("eig") else None,
               "talk_p_room_top3": sig_sep(t, "p_room", 3) if t.get("eig") else None,
               "N_content": c.get("N"), "k_content": c.get("k_cd"), "content_l1_edge": (c["eig"][0] / c["edge_cd"]) if c.get("eig") else None,
               "content_sign_share": c["modes"][0]["sign_share"] if c.get("eig") else None,
               "content_p_lab": sig_sep(c, "p_lab", c.get("k_cd", 0)) if c.get("eig") else None,
               "content_p_room": sig_sep(c, "p_room", c.get("k_cd", 0)) if c.get("eig") else None,
               "k_content_d8": x.get("content_d8", {}).get("k_cd"), "k_content_chat": x.get("content_chat", {}).get("k_cd"),
               "content_fill": c.get("fill")}
        rows.append(row)
    return pl.DataFrame(rows, infer_schema_length=None)


# ------------------------------------------------------------------------------------------------ PR helpers
def first_hour(p30, date):
    x = p30.filter((pl.col("pt_date") == date) & (pl.col("win30") <= 1))
    v = x["pr"].drop_nans().drop_nulls(); tv = x["tv"].drop_nans().drop_nulls()
    return (float(v.mean()) if len(v) else np.nan, float(tv.mean()) if len(tv) else np.nan)


def ne34(p30, units):
    tr = transitions(units)
    kick = []
    for g, (pre, post) in sorted(tr.items()):
        a, ta = first_hour(p30, pre); b, tb = first_hour(p30, post)
        mode_from = units.filter(pl.col("goal_no") == g - 1)["mode"][0]; mode_to = units.filter(pl.col("goal_no") == g)["mode"][0]
        reg = units.filter(pl.col("goal_no") == g)["regime"][0]
        kick.append({"goal_to": g, "pre": pre, "post": post, "mode_from": mode_from, "mode_to": mode_to, "regime": reg,
                     "pr_pre": a, "pr_post": b, "d_pr": b - a, "rel": (b - a) / a if a == a else np.nan, "tv_pre": ta, "tv_post": tb, "d_tv": tb - ta})
    kick = pl.DataFrame(kick).filter(pl.col("d_pr").is_not_nan())
    plac = []
    for u in units.iter_rows(named=True):
        ds = u["days"]
        for k in range(len(ds) - 1):
            a, ta = first_hour(p30, ds[k]); b, tb = first_hour(p30, ds[k + 1])
            if a == a and b == b:
                plac.append({"unit": u["unit"], "goal_no": u["goal_no"], "regime": u["regime"], "k": k, "pre": ds[k], "post": ds[k + 1],
                             "pr_pre": a, "d_pr": b - a, "rel": (b - a) / a, "d_tv": tb - ta})
    plac = pl.DataFrame(plac)
    return kick, plac


def ols_slope(y, X):
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    return beta


def day_slope_fe(df):
    """Slope of PR30 on day index with window-of-day fixed effects."""
    df = df.filter(pl.col("pr").is_not_nan())
    if df["day"].n_unique() < 2:
        return np.nan
    wins = sorted(df["win30"].unique().to_list())
    X = np.column_stack([df["day"].to_numpy().astype(float)] + [(df["win30"] == w).to_numpy().astype(float) for w in wins])
    return float(ols_slope(df["pr"].to_numpy(), X)[0])


def within_day_slope(df):
    df = df.filter(pl.col("pr").is_not_nan())
    if df.height < 3:
        return np.nan
    X = np.column_stack([np.ones(df.height), df["win30"].to_numpy().astype(float)])
    return float(ols_slope(df["pr"].to_numpy(), X)[1])


# ------------------------------------------------------------------------------------------------ H02 chunks
def h02_compare():
    mf = pl.read_parquet(L.ROOT / "data/processed/H02-couplings-are-real/mf_cw.parquet")
    nl = pl.read_parquet(L.ROOT / "data/processed/H02-couplings-are-real/mf_cw_nolull.parquet").select("chunk", "bJ0_nolull", "z_nolull")
    cal = pl.read_parquet(L.SH / "calendar.parquet")
    hm = L.holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    cal = cal.with_columns(pl.Series("hm", hm)).filter(~pl.col("hm") & ~pl.col("holdout"))
    ab = pl.read_parquet(L.SH / "activity_bins.parquet", columns=["pt_date", "minute", "agent", "state"])
    rows = []
    for ch in mf.iter_rows(named=True):
        g = int(ch["chunk"][1:3]); k = int(ch["chunk"].split("c")[1])
        days = sorted(cal.filter(pl.col("goal_no") == g)["pt_date"].to_list())[5 * k:5 * k + 5]
        x = ab.filter(pl.col("pt_date").is_in(days))
        pres = x.group_by("agent").agg(pl.col("pt_date").n_unique().alias("nd"), (pl.col("state") >= 3).sum().alias("na"))
        agents = sorted(pres.filter((pl.col("nd") == len(days)) & (pl.col("na") >= 30))["agent"].to_list())
        dl = []
        for dd in days:
            y = x.filter((pl.col("pt_date") == dd) & pl.col("agent").is_in(agents))
            S = -np.ones((len(agents), int(y["minute"].max()) + 1))
            S[np.searchsorted(agents, y["agent"].to_numpy()), y["minute"].to_numpy()] = np.where(y["state"].to_numpy() >= 3, 1, -1)
            B = S.copy()
            for s in range(0, S.shape[1], 30):
                B[:, s:s + 30] = S[:, s:s + 30] - S[:, s:s + 30].mean(1, keepdims=True)
            dl.append(B)
        X = np.concatenate(dl, 1); X = X[X.std(1) > 0]
        w, V, C = L.corr_eig(X, vectors=True)
        u = np.ones(len(w)) / np.sqrt(len(w))
        rows.append({"chunk": ch["chunk"], "regime": ch["regime"], "mode": ch["mode"], "N": len(w), "l1_block": float(w[0]),
                     "VR_block": float(u @ C @ u), "sign_share": L.mode_summary(V[:, 0])["sign_share"],
                     "bJ0_h02": ch["bJ0"], "VR_h02": ch["VR"], "z_h02": ch["z"]})
    return pl.DataFrame(rows).join(nl, on="chunk", how="left")


# ------------------------------------------------------------------------------------------------ main
def main():
    rmt, p30, pday, units = load_all()
    ut = unit_table(rmt, units)
    ut.write_parquet(L.OUT / "unit_table.parquet")
    sc = ut.filter(pl.col("scored"))
    O = {}

    # ---------------- P1 / P1'
    n = sc.height
    f13 = sc.filter(pl.col("k_cd").is_between(1, 3)).height / n
    f0 = sc.filter(pl.col("k_cd") == 0).height / n
    fmp = sc.filter(pl.col("k_mp") >= pl.col("k_cd") + 1).height / n
    O["P1"] = {"n_units": n, "frac_k_1_3": f13, "frac_k0": f0, "frac_k_ge4": sc.filter(pl.col("k_cd") >= 4).height / n, "frac_kmp_inflated": fmp,
               "k_cd_dist": sc["k_cd"].value_counts().sort("k_cd").to_dicts(),
               "pass": bool(f13 >= 2 / 3 and f0 <= 1 / 6 and fmp >= 0.5)}
    l13 = sc.filter(pl.col("k_lull").is_between(1, 3)).height / n
    l0 = sc.filter(pl.col("k_lull") == 0).height / n
    O["P1prime"] = {"frac_k_1_3": l13, "frac_k0": l0, "k_lull_dist": sc["k_lull"].value_counts().sort("k_lull").to_dicts(),
                    "pass": bool(l13 >= 2 / 3 and l0 <= 1 / 6)}
    O["P1_secondary"] = {"k_circ_dist": sc["k_circ"].value_counts().sort("k_circ").to_dicts(),
                         "k_mpeff_dist": sc["k_mpeff"].value_counts().sort("k_mpeff").to_dicts(),
                         "k_rank_dist": sc["k_rank"].value_counts().sort("k_rank").to_dicts()}

    # ---------------- P2
    s1 = sc.filter(pl.col("k_cd") >= 1)
    shape_ok = s1.filter((pl.col("sign_share") >= 0.8 - TOL) & (pl.col("VR_l1") >= 0.7 - TOL)).height / max(s1.height, 1)
    med = {r: float(sc.filter(pl.col("regime") == r)["l1_edge"].median()) for r in ["I", "II", "III"]}
    lull30 = sc.filter(pl.col("lull_drop") >= 0.3).height / n
    O["P2"] = {"n_k_ge1": s1.height, "frac_shape_ok": shape_ok, "median_l1_edge": med, "frac_lull_drop_ge30": lull30,
               "median_lull_drop": float(sc["lull_drop"].median()), "median_sign_share": float(s1["sign_share"].median()) if s1.height else None,
               "median_VR_l1": float(s1["VR_l1"].median()) if s1.height else None,
               "parts": {"shape": shape_ok >= 2 / 3, "III_gt_I": med["III"] > med["I"], "lull": lull30 >= 0.5}}
    O["P2"]["pass"] = bool(all(O["P2"]["parts"].values()))
    h2 = h02_compare(); h2.write_parquet(L.OUT / "h02_compare.parquet")
    rho = spearmanr(h2["l1_block"] - 1, h2["bJ0_h02"]).statistic
    O["P2_h02"] = {"spearman_l1block_vs_bJ0": float(rho), "n_chunks": h2.height, "consistent": bool(rho >= 0.6),
                   "median_VRblock_over_l1block": float((h2["VR_block"] / h2["l1_block"]).median()),
                   "spearman_VRblock_vs_VRh02": float(spearmanr(h2["VR_block"], h2["VR_h02"]).statistic)}

    # ---------------- P3
    tt = sc.filter(pl.col("k_talk").is_not_null())
    f_talk = tt.filter(pl.col("k_talk") <= pl.col("k_cd")).height / max(tt.height, 1)
    tr2 = sc.filter(pl.col("two_room"))
    room_ok = tr2.filter(pl.col("talk_p_room").is_not_null() & (pl.col("talk_p_room") < 0.05)).height / max(tr2.height, 1)
    O["P3"] = {"frac_talk_le_act": f_talk, "n_two_room": tr2.height, "frac_room_sep": room_ok,
               "room_sep_top3_any": tr2.filter(pl.col("talk_p_room_top3").is_not_null() & (pl.col("talk_p_room_top3") < 0.05)).height,
               "k_talk_dist": tt["k_talk"].value_counts().sort("k_talk").to_dicts(),
               "pass": bool(f_talk >= 2 / 3 and room_ok >= 0.5)}

    # ---------------- P4
    cc = sc.filter(pl.col("k_content").is_not_null())
    f_c = cc.filter(pl.col("k_content") >= 1).height / max(cc.height, 1)
    by = {}
    for r in ["I", "III"]:
        x = cc.filter(pl.col("regime") == r)
        mc = x.filter(pl.col("mode") == "C")["content_l1_edge"].median()
        mi = x.filter(pl.col("mode").is_in(["I", "F"]))["content_l1_edge"].median()
        mi51 = x.filter(pl.col("mode").is_in(["I", "F", "I/K"]))["content_l1_edge"].median()
        by[r] = {"C": mc, "IF": mi, "IF_with_51": mi51, "C_gt_IF": (mc is not None and mi is not None and mc > mi)}
    O["P4"] = {"frac_k_ge1": f_c, "k_content_dist": cc["k_content"].value_counts().sort("k_content").to_dicts(), "by_regime": by,
               "k_d8_dist": cc["k_content_d8"].value_counts().sort("k_content_d8").to_dicts(),
               "k_chat_dist": cc["k_content_chat"].value_counts().sort("k_content_chat").to_dicts(),
               "pass": bool(f_c >= 0.5 and all(v["C_gt_IF"] for v in by.values()))}

    # ---------------- P5 (descriptive)
    labs = sc.filter(pl.col("act_p_lab").is_not_null() | pl.col("content_p_lab").is_not_null())
    lab_ok = labs.filter(((pl.col("act_p_lab") < 0.05) & (pl.col("k_cd") >= 1)).fill_null(False) | (pl.col("content_p_lab") < 0.05).fill_null(False)).height
    O["P5"] = {"n_eligible": labs.height, "n_lab_sep": lab_ok, "descriptive": True}

    # ---------------- P6 (NE34)
    kick, plac = ne34(p30, units)
    kick.write_parquet(L.OUT / "ne34_kickoffs.parquet"); plac.write_parquet(L.OUT / "ne34_placebos.parquet")
    pv = mannwhitneyu(kick["d_pr"], plac["d_pr"], alternative="less").pvalue
    plac2 = plac.filter(pl.col("k") >= 1)
    pv2 = mannwhitneyu(kick["d_pr"], plac2["d_pr"], alternative="less").pvalue
    pvt = mannwhitneyu(kick["d_tv"].drop_nans(), plac["d_tv"].drop_nans(), alternative="less").pvalue
    O["P6"] = {"n_kick": kick.height, "n_placebo": plac.height, "median_d": float(kick["d_pr"].median()),
               "frac_neg": float((kick["d_pr"] < 0).mean()), "median_rel": float(kick["rel"].median()), "p_mw": float(pv),
               "p_mw_no_day1_placebos": float(pv2), "placebo_median_d": float(plac["d_pr"].median()),
               "placebo_sd_rel": float(plac["rel"].std()), "placebo_iqr_rel": [float(plac["rel"].quantile(.25)), float(plac["rel"].quantile(.75))],
               "tv_median_d": float(kick["d_tv"].median()), "tv_p_mw": float(pvt), "tv_frac_neg": float((kick["d_tv"] < 0).mean()),
               "by_regime": {r: {"n": kick.filter(pl.col("regime") == r).height, "median_d": kick.filter(pl.col("regime") == r)["d_pr"].median()} for r in ["I", "II", "III"]}}
    O["P6"]["pass"] = bool(O["P6"]["median_d"] < 0 and O["P6"]["frac_neg"] >= 2 / 3 and pv < 0.05 and O["P6"]["median_rel"] <= -0.10)

    # ---------------- P7
    p7 = []
    for g in sorted(set(units["goal_no"].to_list())):
        us = units.filter(pl.col("goal_no") == g).sort("unit")
        u0 = us["unit"][0]; days_all = [d for dd in us["days"].to_list() for d in dd]
        if len(days_all) < 3:
            continue
        pdg = pday.filter(pl.col("goal_no") == g).sort("pt_date")
        d1 = pdg.filter(pl.col("pt_date") == days_all[0])["prday"]
        later = pdg.filter(pl.col("pt_date") != days_all[0])["prday"].drop_nans()
        x30 = p30.filter(pl.col("unit") == u0)
        s1_ = within_day_slope(x30.filter(pl.col("day") == 0))
        so = [within_day_slope(x30.filter(pl.col("day") == k)) for k in range(1, x30["day"].max() + 1)] if x30.height else []
        so = [v for v in so if v == v]
        p7.append({"goal_no": g, "unit": u0, "regime": us["regime"][0], "mode": us["mode"][0], "N": us["N_catalog"][0],
                   "prday_d1": float(d1[0]) if len(d1) and d1[0] == d1[0] else np.nan,
                   "prday_later_med": float(later.median()) if len(later) else np.nan,
                   "slope_d1": s1_, "slope_other_mean": float(np.mean(so)) if so else np.nan})
    p7 = pl.DataFrame(p7).with_columns((pl.col("prday_d1") < pl.col("prday_later_med")).alias("d1_lower"),
                                       (pl.col("slope_d1") - pl.col("slope_other_mean")).alias("slope_diff"))
    p7s = p7.filter(pl.col("N") >= 10)
    a7 = p7s.filter(pl.col("prday_d1").is_not_nan() & pl.col("prday_later_med").is_not_nan())
    b7 = p7s.filter(pl.col("slope_diff").is_not_nan())
    O["P7"] = {"n_a": a7.height, "frac_d1_lower": float(a7["d1_lower"].mean()), "n_b": b7.height,
               "frac_slope_up": float((b7["slope_diff"] > 0).mean()), "median_rel_d1": float(((a7["prday_d1"] - a7["prday_later_med"]) / a7["prday_later_med"]).median()),
               "all_periods_frac_d1_lower": float(p7.filter(pl.col("prday_d1").is_not_nan() & pl.col("prday_later_med").is_not_nan())["d1_lower"].mean())}
    O["P7"]["pass"] = bool(O["P7"]["frac_d1_lower"] >= 2 / 3 and O["P7"]["frac_slope_up"] >= 2 / 3)
    O["P7"]["R4_consensus_wins"] = bool(1 - O["P7"]["frac_d1_lower"] >= 0.5)
    p7.write_parquet(L.OUT / "p7_day1.parquet")

    # ---------------- P8
    slopes = []
    for u in units.filter(pl.col("n_days") >= 3).iter_rows(named=True):
        x = p30.filter((pl.col("unit") == u["unit"]) & (pl.col("day") >= 1))
        if u["unit"] in ("36b", "38b", "38c", "51b", "51c", "51d", "51e"):  # sub-units not starting at the kickoff: all days
            x = p30.filter(pl.col("unit") == u["unit"])
        slopes.append({"unit": u["unit"], "goal_no": u["goal_no"], "regime": u["regime"], "slope": day_slope_fe(x),
                       "consensus": u["goal_no"] in CONSENSUS, "scored": u["scored"]})
    slopes = pl.DataFrame(slopes)
    p8 = {}
    for g in sorted(CONSENSUS):
        s = slopes.filter(pl.col("goal_no") == g)
        reg = s["regime"][0]
        ref = slopes.filter((pl.col("regime") == reg) & ~pl.col("consensus") & pl.col("slope").is_not_nan())["slope"].median()
        p8[g] = {"slope": float(s["slope"][0]), "regime_median_nonconsensus": float(ref), "neg": bool(s["slope"][0] < 0),
                 "below_ref": bool(s["slope"][0] < ref)}
    O["P8"] = {"by_period": p8, "pass": bool(all(v["neg"] and v["below_ref"] for v in p8.values()))}
    slopes.write_parquet(L.OUT / "p8_slopes.parquet")

    # ---------------- P9
    pm = (pday.group_by("goal_no", "regime", "mode").agg(pl.col("prday").drop_nans().mean().alias("prday_mean"),
                                                         pl.col("prday").drop_nans().count().alias("n_days_pr"),
                                                         pl.col("tvday").drop_nans().mean().alias("tv_mean"),
                                                         pl.col("pr_between").drop_nans().mean().alias("pr_between_mean"))
          .sort("goal_no"))
    pm.write_parquet(L.OUT / "period_means.parquet")
    get = lambda g: pm.filter(pl.col("goal_no") == g)["prday_mean"][0]  # noqa: E731
    fI = [get(g) for g in FREE["I"]]; sI = [get(g) for g in SHARED["I"]]
    pI = mannwhitneyu(fI, sI, alternative="greater", method="exact").pvalue
    fIII = get(37); sIII = [get(g) for g in SHARED["III"]]
    O["P9"] = {"free_I": dict(zip(FREE["I"], fI)), "shared_I": dict(zip(SHARED["I"], sI)), "shared_I_median": float(np.median(sI)),
               "all_free_above": bool(all(v > np.median(sI) for v in fI)), "p_exact": float(pI),
               "III": {"free_37": fIII, "shared": dict(zip(SHARED["III"], sIII)), "rank_37_of_4": int(1 + sum(v > fIII for v in sIII))},
               "individual_I": {g: get(g) for g in [10, 17, 20, 21]}, "competition_I": {g: get(g) for g in [23, 27]}}
    O["P9"]["pass"] = bool(O["P9"]["all_free_above"] and pI <= 0.05)
    kk = kick.filter(pl.col("goal_to").is_in([31, 37, 11]))
    O["P9"]["to_free_kickoffs"] = kk.select("goal_to", "d_pr").to_dicts()

    # ---------------- P10
    pmu = pday.group_by("unit").agg(pl.col("prday").drop_nans().median().alias("prday_med"))
    x = sc.join(pmu, on="unit")
    p10 = {}
    for r in ["I", "III"]:
        y = x.filter((pl.col("regime") == r) & pl.col("content_l1_edge").is_not_null() & pl.col("prday_med").is_not_nan())
        rr = spearmanr(y["content_l1_edge"], y["prday_med"])
        p10[r] = {"n": y.height, "rho": float(rr.statistic), "p": float(rr.pvalue)}
    O["P10"] = {"by_regime": p10, "pass": bool(all(v["rho"] < 0 for v in p10.values()) and any(abs(v["rho"]) >= 0.3 for v in p10.values()))}

    (L.OUT / "outcomes.json").write_text(json.dumps(O, indent=1, default=float))
    period_results(ut, kick, plac, p7, slopes, pm, O, units, pday)
    L.write_provenance("hypotheses/H12-groupthink-dimensional-collapse/analysis/evaluate.py",
                       ["H12 G*/rmt_*.json, pr30_*.parquet, prday_*.parquet; H02 mf_cw*.parquet; shared activity_bins, calendar"],
                       {"outputs": "unit_table, ne34_*, h02_compare, period_means, p7_day1, p8_slopes, outcomes.json, period_results.json"})
    print(json.dumps({k: v.get("pass") for k, v in O.items() if isinstance(v, dict)}, indent=0))
    return O


def fmt(v, d=2):
    if v is None or (isinstance(v, float) and (math.isnan(v))):
        return "–"
    return f"{v:.{d}f}" if isinstance(v, float) else str(v)


def period_results(ut, kick, plac, p7, slopes, pm, O, units, pday):
    out = {}
    plac_rel = plac["d_pr"].to_numpy()
    for g in PERIODS:
        us = ut.filter(pl.col("goal_no") == g).sort("unit")
        allu = units.filter(pl.col("goal_no") == g).sort("unit")
        checks = {}
        sc_u = us.filter(pl.col("scored"))
        if sc_u.height:
            ok = sc_u.filter(pl.col("k_cd").is_between(1, 3) & (pl.col("sign_share") >= 0.8 - TOL)).height
            checks["HH77 (k_cd ∈ 1–3, uniform top mode)"] = ok / sc_u.height >= 2 / 3
        r7 = p7.filter(pl.col("goal_no") == g)
        if r7.height and r7["prday_d1"][0] == r7["prday_d1"][0] and r7["prday_later_med"][0] == r7["prday_later_med"][0]:
            checks["P7a (PRday day 1 < later)"] = bool(r7["d1_lower"][0])
        kg = kick.filter(pl.col("goal_to") == g)
        if kg.height:
            checks["P6 (ΔPR_kick < 0)"] = bool(kg["d_pr"][0] < 0)
        if g in CONSENSUS:
            v = O["P8"]["by_period"][g]; checks["P8 (consensus decline)"] = v["neg"] and v["below_ref"]
        reg_last = allu["regime"][-1]
        mean_g = pm.filter(pl.col("goal_no") == g)["prday_mean"][0]
        if g in FREE.get(reg_last, []):
            ref = np.median([pm.filter(pl.col("goal_no") == x)["prday_mean"][0] for x in SHARED[reg_last]])
            checks["P9 (free above shared median)"] = bool(mean_g > ref)
        elif g in SHARED.get(reg_last, []):
            ref = np.median([pm.filter(pl.col("goal_no") == x)["prday_mean"][0] for x in FREE[reg_last]])
            checks["P9 (shared below free median)"] = bool(mean_g < ref)
        vals = list(checks.values())
        verdict = "supported" if vals and all(vals) else ("failed" if vals and not any(vals) else ("mixed" if vals else "descriptive"))
        # markdown
        md = ["**Random-matrix arm** (cross-day edge, 200 surrogates; λ₁/edge > 1 means above the noise edge):", "",
              "| Unit | N | days | k_cd act | k after lull filter | k circ / MP / MP_eff | λ₁/edge (lull-filtered) | sign share · VR/λ₁ | k_cd talk (room p) | k_cd content (λ₁/edge) |",
              "| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        for r in us.iter_rows(named=True):
            md.append(f"| {r['unit']}{'' if r['scored'] else ' (not scored)'} | {r['N_act']} | {r['n_days']} | {r['k_cd']} | {r['k_lull']} | {r['k_circ']} / {r['k_mp']} / {r['k_mpeff']} | "
                      f"{fmt(r['l1_edge'])} ({fmt(r['l1_edge_lull'])}) | {fmt(r['sign_share'])} · {fmt(r['VR_l1'])} | {r['k_talk']} ({fmt(r['talk_p_room'], 3) if r['two_room'] else 'one room'}) | "
                      f"{r['k_content']} ({fmt(r['content_l1_edge'])}) |")
        if not us.height:
            md.append("| (no unit with ≥ 6 present agents and ≥ 2 days) | | | | | | | | | |")
        md += ["", "**Dimensionality arm** (chat, whitened d = 32):", ""]
        pdg = pday.filter(pl.col("goal_no") == g).sort("pt_date")
        md.append(f"- Mean PRday {fmt(mean_g)} (6 agents × 15 statements; {pdg['prday'].drop_nans().len()} of {pdg.height} days valid); mean spread TV {fmt(pm.filter(pl.col('goal_no') == g)['tv_mean'][0])}; "
                  f"between-agent PR (noise-corrected) {fmt(pm.filter(pl.col('goal_no') == g)['pr_between_mean'][0])}.")
        if r7.height:
            md.append(f"- P7: PRday day 1 = {fmt(r7['prday_d1'][0])} vs median of later days {fmt(r7['prday_later_med'][0])}; within-day PR30 slope day 1 {fmt(r7['slope_d1'][0], 3)} vs other days {fmt(r7['slope_other_mean'][0], 3)} per window.")
        if kg.height:
            pct = float((plac_rel <= kg["d_pr"][0]).mean())
            md.append(f"- P6: first-hour PR {fmt(kg['pr_pre'][0])} (last day of #{g - 1}) → {fmt(kg['pr_post'][0])} (day 1): Δ = {fmt(kg['d_pr'][0])} "
                      f"({fmt(100 * kg['rel'][0], 0)}%); placebo percentile {pct:.2f}; ΔTV {fmt(kg['d_tv'][0])}.")
        if g in CONSENSUS:
            v = O["P8"]["by_period"][g]
            md.append(f"- P8: PR30 slope over days 2..D (window-of-day FE) {fmt(v['slope'], 3)} per day vs regime median of non-consensus units {fmt(v['regime_median_nonconsensus'], 3)}.")
        md += ["", "| Check | Holds |", "| --- | --- |"] + [f"| {k} | {'yes' if v else 'no'} |" for k, v in checks.items()]
        md += ["", f"Figure: `figures/G{g:02d}_summary.pdf`. Data: `data/processed/H12-groupthink-dimensional-collapse/G{g:02d}/`."]
        sm = []
        if sc_u.height:
            kl = sc_u["k_lull"].to_list()
            sm.append(f"- **C (nulls):** activity modes beyond the cross-day null in {sc_u.filter(pl.col('k_cd') >= 1).height}/{sc_u.height} unit(s); after the lull filter in {sum(k >= 1 for k in kl)}/{sc_u.height}.")
            sm.append(f"- **D (Curie–Weiss shape):** sign share {', '.join(fmt(v) for v in sc_u['sign_share'])}; VR/λ₁ {', '.join(fmt(v) for v in sc_u['VR_l1'])}.")
            tr2 = sc_u.filter(pl.col("two_room"))
            if tr2.height:
                sm.append(f"- **G (rooms):** talk-mode room separation p = {', '.join(fmt(v, 3) for v in tr2['talk_p_room'])} (– = no signal talk mode).")
        if kg.height:
            sm.append(f"- **E (NE34 kickoff):** ΔPR_kick = {fmt(kg['d_pr'][0])} ({'negative' if kg['d_pr'][0] < 0 else 'not negative'}).")
        if not sm:
            sm.append("- Only the dimensionality checks apply here (N < 10).")
        out[str(g)] = {"verdict": verdict, "checks": {k: bool(v) for k, v in checks.items()}, "result_md": "\n".join(md), "score_md": "\n".join(sm)}
    (L.OUT / "period_results.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
