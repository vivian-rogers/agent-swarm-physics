"""H67 synthesis: period pooling, prediction scoring (P1-P7), comparisons with H25 / H42 / H50, natives (NE14, NE42,
G51), per-period estimates and figures.

    uv run python hypotheses/H67-lagged-criticality-dial/analysis/summarize.py
"""
from __future__ import annotations

import json
import sys

import numpy as np
import polars as pl
from scipy import stats

import h67lib as L

sys.path.insert(0, str(L.ROOT / "infra/shared"))
import estimates as E  # noqa: E402

RES = L.OUT / "results"
FIG = L.ROOT / "hypotheses/H67-lagged-criticality-dial/figures"


def re_pool(est, se):
    est, se = np.asarray(est, float), np.asarray(se, float)
    ok = np.isfinite(est) & np.isfinite(se) & (se > 0)
    est, se = est[ok], se[ok]
    if not len(est):
        return {"mean": np.nan, "se": np.nan, "lo": np.nan, "hi": np.nan, "k": 0}
    w = 1 / se ** 2
    m = (w * est).sum() / w.sum()
    Q = (w * (est - m) ** 2).sum()
    tau2 = max(0.0, (Q - (len(est) - 1)) / (w.sum() - (w ** 2).sum() / w.sum())) if len(est) > 1 else 0.0
    ws = 1 / (se ** 2 + tau2)
    mm = (ws * est).sum() / ws.sum()
    s = np.sqrt(1 / ws.sum())
    return {"mean": float(mm), "se": float(s), "lo": float(mm - 1.96 * s), "hi": float(mm + 1.96 * s), "k": int(len(est)),
            "tau2": float(tau2)}


def se_of(df, col):
    return ((df[f"{col}_hi"] - df[f"{col}_lo"]) / 3.92).to_numpy()


def main():
    u = pl.read_parquet(RES / "units.parquet").filter(pl.col("ok").fill_null(False)).sort("goal_no", "unit_id")
    out = {"n_units": u.height, "n_periods": u["goal_no"].n_unique(),
           "n_calls": int(u["n_rows_trim"].sum())}
    # ---------------------------------------------------------------- period pooling
    per = []
    for (g,), s in u.group_by(["goal_no"], maintain_order=True):
        pg = re_pool(s["g"].to_numpy(), s["g_se"].to_numpy())
        pj = re_pool(s["J1"].to_numpy(), s["J1_se"].to_numpy())
        w = s["n_rows_trim"].to_numpy().astype(float)
        geq = s["g_eq"].to_numpy()
        ok = np.isfinite(geq)
        per.append({"goal_no": g, "regime": s["regime"][0], "units": s["unit_id"].to_list(), "N": float(s["N"].mean()),
                    "g": pg["mean"], "g_lo": pg["lo"], "g_hi": pg["hi"], "g_se": pg["se"],
                    "J1": pj["mean"], "J1_lo": pj["lo"], "J1_hi": pj["hi"],
                    "g_eq": float((geq[ok] * w[ok]).sum() / w[ok].sum()) if ok.any() else np.nan,
                    "rbar": float((s["rbar"] * w).sum() / w.sum()),
                    "g_named": float(np.nansum(s["g_named"].to_numpy() * w) / w.sum()),
                    "g_unnamed": float(np.nansum(s["g_unnamed"].to_numpy() * w) / w.sum()),
                    "n_rows": int(w.sum()), "max_unit_g_hi": float(s["g_hi"].max())})
    P = pl.DataFrame(per)
    # external references
    est = E.read_estimates()
    h25 = (est.filter((pl.col("hypothesis") == "H25") & (pl.col("statistic") == "loop_gain_g_daily_dial_trim")
                      & (pl.col("channel") == "talk")).select("goal_no", pl.col("estimate").alias("g_h25_trim"))
           .group_by("goal_no").agg(pl.col("g_h25_trim").mean()))
    h42 = pl.read_parquet(L.ROOT / "data/processed/H42-readout-hawkes-kernel/periods.parquet").select(
        "goal_no", "nxB_w", "nxA_w")
    P = P.with_columns(pl.col("goal_no").cast(pl.Int64)).join(h25.with_columns(pl.col("goal_no").cast(pl.Int64)),
                                                              on="goal_no", how="left")
    P = P.join(h42.with_columns(pl.col("goal_no").cast(pl.Int64)), on="goal_no", how="left")
    # verdicts
    v = []
    for r in P.iter_rows(named=True):
        if r["g_hi"] is not None and r["max_unit_g_hi"] is not None and np.isfinite(r["g"]):
            jpos = r["J1_lo"] > 0
            bigger = r["g"] > r["g_eq"]
            sub = r["max_unit_g_hi"] < 1
            if not sub:
                v.append("failed")
            elif jpos and bigger:
                v.append("supported")
            elif (not jpos) and (not bigger):
                v.append("failed")
            else:
                v.append("mixed")
        else:
            v.append("descriptive")
    P = P.with_columns(pl.Series("verdict", v))
    P.write_parquet(RES / "periods.parquet")
    # ---------------------------------------------------------------- predictions
    sc = {}
    sc["P1"] = {"max_g_hi": float(u["g_hi"].max()), "units_g_lo_ge_1": int((u["g_lo"] >= 1).sum()),
                "share_g_below_0.5": float((u["g"] < 0.5).mean()), "median_g": float(u["g"].median()),
                "median_g_regIII": float(u.filter(pl.col("regime") == "III")["g"].median()),
                "median_g_regI": float(u.filter(pl.col("regime") == "I")["g"].median())}
    pp = P.filter(pl.col("g_eq").is_not_nan())
    sc["P2"] = {"share_periods_g_gt_geq": float((pp["g"] > pp["g_eq"]).mean()),
                "median_ratio": float((pp["g"] / pp["g_eq"]).median()), "n": pp.height,
                "share_vs_h25": float((P.drop_nulls("g_h25_trim")["g"] > P.drop_nulls("g_h25_trim")["g_h25_trim"]).mean()),
                "median_ratio_h25": float((P.drop_nulls("g_h25_trim")["g"] / P.drop_nulls("g_h25_trim")["g_h25_trim"]).median()),
                "regIII_share_g_gt_geq": float((pp.filter(pl.col("regime") == "III")["g"]
                                                > pp.filter(pl.col("regime") == "III")["g_eq"]).mean()),
                "regI_median_geq_minus_g": float((pp.filter(pl.col("regime") == "I")["g_eq"]
                                                  - pp.filter(pl.col("regime") == "I")["g"]).median()),
                "regIII_median_geq_minus_g": float((pp.filter(pl.col("regime") == "III")["g_eq"]
                                                    - pp.filter(pl.col("regime") == "III")["g"]).median())}
    ph = P.drop_nulls("nxB_w").filter(pl.col("nxB_w").is_not_nan())
    rho = stats.spearmanr(ph["g"], ph["nxB_w"])
    rhoA = stats.spearmanr(ph["g"], ph["nxA_w"])
    sc["P3"] = {"spearman_g_nxB": float(rho.statistic), "p": float(rho.pvalue), "n": ph.height,
                "median_ratio_g_over_nxB": float((ph["g"] / ph["nxB_w"].clip(1e-4)).median()),
                "median_nxB": float(ph["nxB_w"].median()), "spearman_g_nxA": float(rhoA.statistic)}
    h50 = pl.read_parquet(L.ROOT / "data/processed/H50-field-vs-coupling-transfer-lag/unit_table.parquet").select(
        pl.col("unit").alias("unit_id"), pl.col("J1").alias("J1_h50"))
    uu = u.join(h50, on="unit_id", how="inner").with_columns((pl.col("J1_h50") * pl.col("rbar")).alias("g_h50"))
    r50 = stats.spearmanr(uu["g"], uu["g_h50"])
    sc["P3b"] = {"spearman_g_vs_h50_J1_rbar": float(r50.statistic), "p": float(r50.pvalue), "n": uu.height,
                 "median_g_h50": float(uu["g_h50"].median())}
    sc["P4"] = {"share_units_J1_ci_pos": float((u["J1_lo"] > 0).mean()),
                "share_units_bRm_gt_bP": float((u["b_R_m"] > u["b_P"]).mean()),
                "shift_null_excl0_share_mean": float(u["shift_excl0_share"].mean()),
                "regIII_share_J1_ci_pos": float((u.filter(pl.col("regime") == "III")["J1_lo"] > 0).mean())}
    for reg in ("I", "III"):
        s = u.filter(pl.col("regime") == reg)
        a = re_pool(s["J1_named"].to_numpy(), s["J1_named_se"].to_numpy())
        b = re_pool(s["J1_unnamed"].to_numpy(), s["J1_unnamed_se"].to_numpy())
        sc.setdefault("P5", {})[reg] = {"J1_named": a, "J1_unnamed": b, "ratio": a["mean"] / b["mean"] if b["mean"] else None,
                                        "median_share_named": float(s["share_named"].median()),
                                        "median_g_named": float(s["g_named"].median()),
                                        "median_g_unnamed": float(s["g_unnamed"].median())}
    rel = lambda a, b: float(np.median(np.abs(a - b)) / max(np.median(np.abs(b)), 1e-9))  # noqa: E731
    s3 = u.filter(pl.col("regime") == "III")
    sc["P6"] = {"median_g_trim": float(u["g"].median()), "median_g_untrim": float(u["g_untrim"].median()),
                "median_g_noexo": float(u["g_noexo"].median()),
                "regIII_median_g": float(s3["g"].median()), "regIII_median_g_untrim": float(s3["g_untrim"].median()),
                "regIII_median_g_noexo": float(s3["g_noexo"].median()),
                "regIII_median_g_quiet": float(s3["g_quiet"].median()),
                "regIII_median_g_dm": float(s3["g_dm"].median()), "regIII_median_g_all": float(s3["g_all"].median()),
                "regIII_median_g_het": float(s3["g_het"].median()), "regIII_median_g3": float(s3["g3"].median()),
                "regIII_median_naive": float(s3["g_naive"].median())}
    rj = stats.spearmanr(s3["J1"], s3["N"])
    rg = stats.spearmanr(s3["g"], s3["N"])
    sc["P7"] = {"regIII_spearman_J1_N": float(rj.statistic), "p_J1": float(rj.pvalue),
                "regIII_spearman_g_N": float(rg.statistic), "p_g": float(rg.pvalue), "n": s3.height}
    out["scores"] = sc
    # ---------------------------------------------------------------- natives
    nat = {}
    ua = u.filter(pl.col("unit_id") == "36a")
    ub = u.filter(pl.col("unit_id").is_in(["36b", "36c"]))
    pb = re_pool(ub["g"].to_numpy(), ub["g_se"].to_numpy())
    wb = ub["n_rows_trim"].to_numpy()
    geq_b = float((ub["g_eq"].to_numpy() * wb).sum() / wb.sum())
    nat["NE14"] = {"g_36a": ua["g"][0], "g_36a_ci": [ua["g_lo"][0], ua["g_hi"][0]], "g_36bc": pb["mean"],
                   "g_36bc_ci": [pb["lo"], pb["hi"]], "geq_36a": ua["g_eq"][0], "geq_36bc": geq_b,
                   "med_call_s_36a": ua["med_call_s"][0], "med_call_s_36bc": float(ub["med_call_s"].mean())}
    s39, s40, s41 = (u.filter(pl.col("unit_id") == x).row(0, named=True) for x in ("39", "40", "41"))
    nat["NE42"] = {k: {"g": s[k2] if False else s["g"], "g_ci": [s["g_lo"], s["g_hi"]], "J1": s["J1"],
                       "J1_ci": [s["J1_lo"], s["J1_hi"]], "rbar": s["rbar"], "g_eq": s["g_eq"],
                       "g_named": s["g_named"], "J1_named": s["J1_named"]}
                   for k, s, k2 in (("39", s39, "g"), ("40", s40, "g"), ("41", s41, "g"))}
    rr = s40["rbar"] / np.mean([s39["rbar"], s41["rbar"]])
    gr = s40["g"] / np.mean([s39["g"], s41["g"]])
    nat["NE42"]["rbar_ratio"] = rr
    nat["NE42"]["g_ratio"] = gr
    nat["NE42"]["J1_40_lt_mean"] = s40["J1"] < np.mean([s39["J1"], s41["J1"]])
    s51 = u.filter(pl.col("goal_no") == 51)
    r1 = stats.spearmanr(s51["g"], s51["N"])
    r2 = stats.spearmanr(s51["J1"], s51["N"])
    nat["G51"] = {"units": s51["unit_id"].to_list(), "max_g_hi": float(s51["g_hi"].max()),
                  "units_g_hi_ge_0.5": int((s51["g_hi"] >= 0.5).sum()),
                  "spearman_g_N": float(r1.statistic), "p_g": float(r1.pvalue),
                  "spearman_J1_N": float(r2.statistic), "p_J1": float(r2.pvalue),
                  "median_g": float(s51["g"].median()), "median_g_named": float(s51["g_named"].median())}
    out["natives"] = nat
    (RES / "summary.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps(out, indent=1, default=float))
    with pl.Config(tbl_rows=60, tbl_cols=16, tbl_width_chars=220):
        print(P.select("goal_no", "regime", "N", "g", "g_lo", "g_hi", "J1", "g_eq", "g_h25_trim", "nxB_w", "g_named",
                       "verdict").with_columns(pl.col(pl.Float64).round(3)))
    # ---------------------------------------------------------------- estimates
    rows = []
    for r in u.iter_rows(named=True):
        base = {"period_unit": r["unit_id"], "goal_no": r["goal_no"], "channel": "talk", "role": "replication",
                "source": "data/processed/H67-lagged-criticality-dial/results/units.parquet",
                "first_day": r["first_day"], "last_day": r["last_day"]}
        rows.append({**base, "statistic": "readout_loop_gain_g_lag", "estimate": r["g"], "ci_lo": r["g_lo"],
                     "ci_hi": r["g_hi"], "ci_kind": "percentile", "se": r["g_se"], "n": float(r["n_rows_trim"]),
                     "n_kind": "receiving calls (all-present window)",
                     "method": "H67 g_lag = m_bar r_bar J1*, J1* = matched-lag read-out jump (reads posted within the call latency before t_call minus in-flight messages posted within it after); agent x day x call-class fields; 1-h block bootstrap",
                     "null": "in-flight placebo; sender time-shift (19 draws)"})
        rows.append({**base, "statistic": "readout_jump_J1_matched", "estimate": r["J1"], "ci_lo": r["J1_lo"],
                     "ci_hi": r["J1_hi"], "ci_kind": "percentile", "se": r["J1_se"], "n": float(r["n_rows_trim"]),
                     "n_kind": "receiving calls (all-present window)",
                     "method": "H67 extra talk probability per peer message read at the call, minus the in-flight placebo",
                     "null": "in-flight placebo"})
        if np.isfinite(r["g_eq"] or np.nan):
            rows.append({**base, "statistic": "equal_time_talk_dial_same_data", "estimate": r["g_eq"],
                         "ci_lo": r.get("g_eq_lo"), "ci_hi": r.get("g_eq_hi"),
                         "ci_kind": "percentile" if r.get("g_eq_lo") is not None and np.isfinite(r.get("g_eq_lo") or np.nan) else "none",
                         "n": float(r["n_days_eq"] or 0), "n_kind": "days",
                         "method": "H67: H25's equal-time talk dial (1-min talk-call spins, 30-min blocks) on the same all-present windows",
                         "null": "none"})
        rows.append({**base, "statistic": "readout_loop_gain_named_part", "estimate": r["g_named"],
                     "ci_lo": r["g_named_lo"], "ci_hi": r["g_named_hi"], "ci_kind": "percentile",
                     "n": float(r["n_rows_trim"]), "n_kind": "receiving calls", "post_hoc": True,
                     "method": "H67 post hoc: m_bar r_bar s_named J1*_named (messages naming the recipient)",
                     "null": "in-flight named placebo"})
    rows = [{k: (None if (isinstance(v, float) and not np.isfinite(v)) else v) for k, v in r.items()} for r in rows]
    for rr_ in rows:
        if rr_.get("ci_lo") is None or rr_.get("ci_hi") is None:
            rr_["ci_kind"] = "none"
    E.write_estimates(rows, hypothesis="H67")
    print("estimates rows:", len(rows))
    figures(u, P)


def figures(u, P):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    FIG.mkdir(parents=True, exist_ok=True)
    col = {"I": "#2c7fb8", "II": "#7f8c8d", "III": "#c0392b"}
    fig, ax = plt.subplots(1, 2, figsize=(7.0, 2.7))
    for reg in ("I", "II", "III"):
        s = P.filter(pl.col("regime") == reg)
        ax[0].errorbar(s["g_eq"], s["g"], yerr=[s["g"] - s["g_lo"], s["g_hi"] - s["g"]], fmt="o", ms=3.5,
                       color=col[reg], lw=0.7, label=f"regime {reg}")
    m = 0.5
    ax[0].plot([-0.1, m], [-0.1, m], "k--", lw=0.6)
    ax[0].axhline(0, color="k", lw=0.4)
    ax[0].set_xlabel("equal-time talk dial $g_{eq}$ (same data)", fontsize=7)
    ax[0].set_ylabel("read-out loop gain $g_{lag}$", fontsize=7)
    ax[0].legend(fontsize=6, frameon=False)
    ax[0].tick_params(labelsize=7)
    s3 = u.filter(pl.col("regime") == "III").sort("N")
    x = np.arange(s3.height)
    ax[1].bar(x, s3["g_named"], color="#c0392b", label="named messages")
    ax[1].bar(x, s3["g_unnamed"], bottom=s3["g_named"], color="#f1948a", label="unnamed")
    ax[1].errorbar(x, s3["g"], yerr=[s3["g"] - s3["g_lo"], s3["g_hi"] - s3["g"]], fmt="k.", ms=3, lw=0.6,
                   label="$g_{lag}$ (95% CI)")
    ax[1].set_xticks(x, s3["unit_id"].to_list(), rotation=90, fontsize=5)
    ax[1].set_ylabel("loop gain (regime III units, by N)", fontsize=7)
    ax[1].legend(fontsize=6, frameon=False)
    ax[1].tick_params(labelsize=7)
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs.pdf")
    plt.close(fig)
    s = pl.read_parquet(L.OUT / "synthetic/runs.parquet")
    fig, ax = plt.subplots(figsize=(3.4, 2.1))
    for w, c in (("null", "#7f8c8d"), ("burst", "#e67e22"), ("g015", "#2c7fb8"), ("g030", "#8e44ad"),
                 ("g060", "#c0392b")):
        q = s.filter(pl.col("world") == w)
        ax.scatter(q["g_true"], q["g_pm"], s=8, color=c, label=f"{w}: $g_{{lag}}$")
        ax.scatter(q["g_true"] + 0.01, q["g_eq"], s=8, marker="x", color=c, alpha=0.6)
    ax.plot([0, 0.7], [0, 0.7], "k--", lw=0.6)
    ax.set_xlabel("planted read-out gain", fontsize=7)
    ax.set_ylabel("estimate (o lagged, x equal-time)", fontsize=7)
    ax.tick_params(labelsize=7)
    ax.legend(fontsize=5, frameon=False, ncol=1)
    fig.tight_layout()
    fig.savefig(FIG / "synthetic.pdf")
    plt.close(fig)


if __name__ == "__main__":
    main()
