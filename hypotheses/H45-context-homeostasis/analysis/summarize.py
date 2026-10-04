"""H45 cross-period summary: prediction counts (P1-P9), pooled share dependence (P5, regime III), set-point variance
shares (P7), random-effects pooled RI by regime, comparison with H18's mention-based exponents. Writes summary.json."""
from __future__ import annotations

import json

import numpy as np
import polars as pl

import h45lib as L
from run_periods import prepare

# H18 round-1 beta (D1, mention-based, old visibility rule), from hypotheses/H18-attention-dilution/README.md
H18_BETA = {"G24": 0.56, "G25": 0.59, "G26": 0.50, "G27": 0.69, "G30": 0.55, "G31": 0.46, "G35": 0.75, "G36": 0.78,
            "G37": 0.75, "G38": 0.69, "G39": 0.62, "G40": 0.60, "G41": 0.65, "G42": 0.72, "G44": 0.72, "G51": 0.61}


def dl_pool(est, lo, hi):
    """DerSimonian-Laird random-effects mean from estimates and 95% CIs."""
    est, se = np.array(est), (np.array(hi) - np.array(lo)) / 3.92
    w = 1 / se ** 2
    m = (w * est).sum() / w.sum()
    q = (w * (est - m) ** 2).sum()
    tau2 = max(0.0, (q - (len(est) - 1)) / (w.sum() - (w ** 2).sum() / w.sum()))
    ws = 1 / (se ** 2 + tau2)
    mr = (ws * est).sum() / ws.sum()
    return {"mean": float(mr), "se": float(np.sqrt(1 / ws.sum())), "tau2": float(tau2), "k": int(len(est)),
            "I2": float(max(0, (q - (len(est) - 1)) / q)) if q > 0 else 0.0}


def main():
    rep = json.loads((L.DATA / "replication.json").read_text())
    ps = sorted(rep.values(), key=lambda r: r["goal_no"])
    reg_of = lambda r: "III" if "III" in r["regime"] else ("II" if "II" in r["regime"].split(",") else "I")
    out = {"n_periods": len(ps)}
    # P1
    ri = [(r["period"], reg_of(r), r["regulation"]) for r in ps if r["regulation"].get("RI") is not None]
    out["P1"] = {"n": len(ri), "n_RI_ge_0.5_ci_excl_0": sum(x["RI"] >= 0.5 and x["RI_ci"][0] > 0 for _, _, x in ri),
                 "n_upper_below_0.5": sum(x["RI_ci"][1] < 0.5 for _, _, x in ri),
                 "RI_range": [min(x["RI"] for _, _, x in ri), max(x["RI"] for _, _, x in ri)],
                 "eta_W_range": [min(x["eta_W"] for _, _, x in ri), max(x["eta_W"] for _, _, x in ri)],
                 "max_abs_RI_minus_etaW": max(abs(x["RI"] - x["eta_W"]) for _, _, x in ri),
                 "pooled_all": dl_pool([x["RI"] for _, _, x in ri], [x["RI_ci"][0] for _, _, x in ri], [x["RI_ci"][1] for _, _, x in ri])}
    for rg in ("I", "II", "III"):
        sub = [x for _, g, x in ri if g == rg]
        if sub:
            out["P1"][f"pooled_{rg}"] = dl_pool([x["RI"] for x in sub], [x["RI_ci"][0] for x in sub], [x["RI_ci"][1] for x in sub])
    # P2 lever
    lev = [(r["period"], reg_of(r), r["lever"]) for r in ps if r["lever"].get("slope") is not None]
    out["P2"] = {"n": len(lev), "n_neg_ci": sum(x["slope_ci"][1] < 0 for _, _, x in lev),
                 "n_pos_ci": sum(x["slope_ci"][0] > 0 for _, _, x in lev),
                 "median_slope": float(np.median([x["slope"] for _, _, x in lev])),
                 "regime_III": {"n": sum(g == "III" for _, g, _ in lev),
                                "n_neg_ci": sum(x["slope_ci"][1] < 0 for _, g, x in lev if g == "III"),
                                "median": float(np.median([x["slope"] for _, g, x in lev if g == "III"]))}}
    # P3 band
    bc = [r["band_cv"] for r in ps if r["band_cv"].get("ratio") is not None]
    out["P3"] = {"n": len(bc), "n_ratio_le_0.5": sum(x["ratio"] <= 0.5 for x in bc),
                 "ratio_range": [min(x["ratio"] for x in bc), max(x["ratio"] for x in bc)],
                 "ratio_median": float(np.median([x["ratio"] for x in bc]))}
    # P4 beta
    be = [(r["period"], reg_of(r), r["beta"]) for r in ps if r["beta"].get("beta") is not None]
    out["P4"] = {"n": len(be), "n_in_band": sum(0.4 <= x["beta"] <= 0.9 and x["beta_ci"][0] > 0 for _, _, x in be),
                 "n_above_0.9": sum(x["beta"] > 0.9 for _, _, x in be),
                 "pooled_all": dl_pool([x["beta"] for _, _, x in be], [x["beta_ci"][0] for _, _, x in be], [x["beta_ci"][1] for _, _, x in be])}
    for rg in ("I", "II", "III"):
        sub = [x for _, g, x in be if g == rg]
        if sub:
            out["P4"][f"pooled_{rg}"] = dl_pool([x["beta"] for x in sub], [x["beta_ci"][0] for x in sub], [x["beta_ci"][1] for x in sub])
    both = [(p, x["beta"], H18_BETA[p]) for p, _, x in be if p in H18_BETA]
    if len(both) >= 5:
        from scipy.stats import spearmanr
        out["P4"]["vs_H18"] = {"n": len(both), "spearman": float(spearmanr([b for _, b, _ in both], [h for _, _, h in both]).statistic),
                               "median_diff": float(np.median([b - h for _, b, h in both])), "pairs": both}
    # P5 per period (reported) and pooled regime III
    sd = [(r["period"], r["share_dependence"]) for r in ps if r["share_dependence"].get("g_R") is not None]
    out["P5_per_period"] = {"n": len(sd), "n_controller_pattern": sum(x["g_R_ci"][1] < 0 and x["g_W_ci"][0] > 0 for _, x in sd),
                            "n_gW_neg_ci": sum(x["g_W_ci"][1] < 0 for _, x in sd), "n_gW_pos_ci": sum(x["g_W_ci"][0] > 0 for _, x in sd),
                            "n_gR_neg_ci": sum(x["g_R_ci"][1] < 0 for _, x in sd), "n_gR_pos_ci": sum(x["g_R_ci"][0] > 0 for _, x in sd)}
    cu, _ = prepare()
    t3 = L.talk_rows(cu.filter(pl.col("regime").cast(pl.Utf8) == "III"))
    out["P5_pooled_III"] = L.share_dependence(t3, B=100)
    t3a = t3.filter(pl.col("lab").cast(pl.Utf8).is_in(list(L.LABS_ACT)))
    out["P5_pooled_III_act_labs"] = L.share_dependence(t3a, B=100)
    # P6 overshoot
    ov = [(r["period"], r["reset_forced_talk"], r["reset_vol_talk"]) for r in ps if "reset_forced_talk" in r and r["reset_forced_talk"].get("overshoot") is not None]
    out["P6"] = {"n": len(ov), "n_met": sum(f["overshoot"] >= 1.2 and f["overshoot_ci"][0] > 1 for _, f, _ in ov),
                 "n_undershoot_ci": sum(f["overshoot_ci"][1] < 1 for _, f, _ in ov),
                 "forced_range": [min(f["overshoot"] for _, f, _ in ov), max(f["overshoot"] for _, f, _ in ov)],
                 "vol": [(p, v.get("overshoot")) for p, _, v in ov]}
    # P7 set points: variance shares and regime contrast
    sp = L.set_points(cu, by=("agent", "goal_no"))
    sp = sp.join(cu.select("goal_no", pl.col("regime").cast(pl.Utf8)).unique(subset=["goal_no"], keep="last"), on="goal_no")
    out["P7"] = L.variance_shares(sp)
    med = sp.group_by("regime").agg(pl.col("s_star").median().alias("s_med"), pl.len().alias("n")).sort("regime")
    out["P7"]["s_star_by_regime"] = med.to_dicts()
    s1 = med.filter(pl.col("regime") == "I")["s_med"]
    s3 = med.filter(pl.col("regime") == "III")["s_med"]
    if len(s1) and len(s3):
        out["P7"]["ratio_III_over_I"] = float(s3[0] / s1[0])
    out["P7"]["by_lab"] = sp.group_by(pl.col("lab").cast(pl.Utf8)).agg(pl.col("s_star").median().alias("s_med"), pl.len().alias("n")).sort("s_med").to_dicts()
    # P8
    pg = [r["p_growth"] for r in ps if r["p_growth"].get("ratio_median") is not None]
    pg3 = [r["p_growth"] for r in ps if r["p_growth"].get("ratio_median") is not None and reg_of(r) == "III"]
    out["P8"] = {"n": len(pg), "n_ge_1.3": sum(x["ratio_median"] >= 1.3 for x in pg), "III_n": len(pg3),
                 "III_n_ge_1.3": sum(x["ratio_median"] >= 1.3 for x in pg3),
                 "range": [min(x["ratio_median"] for x in pg), max(x["ratio_median"] for x in pg)]}
    # set point summary
    sps = [r["set_points"]["s_star_median"] for r in ps if r["set_points"]["s_star_median"] is not None]
    out["set_point_period_medians"] = {"min": min(sps), "max": max(sps), "median": float(np.median(sps)),
                                       "by_period": {r["period"]: r["set_points"]["s_star_median"] for r in ps}}
    out["verdicts"] = {r["period"]: r["verdict"] for r in ps}
    (L.DATA / "summary.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps({k: v for k, v in out.items() if k not in ("set_point_period_medians",)}, indent=1, default=float)[:8000])


if __name__ == "__main__":
    main()
