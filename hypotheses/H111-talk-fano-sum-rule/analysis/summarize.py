"""H111 summary: prediction scoring, period pools, natives, estimates rows, figures.

Usage: uv run python hypotheses/H111-talk-fano-sum-rule/analysis/summarize.py [--no-estimates]
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import spearmanr

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h111lib as L  # noqa: E402

ROOT = L.ROOT
RES = L.OUT / "results"
FIG = ROOT / "hypotheses/H111-talk-fano-sum-rule/figures"
MINWIN = 40


def load():
    d = pl.read_parquet(RES / "units.parquet")
    w = pl.read_parquet(RES / "units_wall.parquet")
    keep = ["phi_10", "phi_10_lo", "phi_10_hi", "phi_15", "phi_15_lo", "phi_15_hi", "r_F", "r_F_lo", "r_F_hi",
            "r_F_se_log", "phi_untrim", "phi_raw", "fano_ratio", "s_F", "phi_5", "phi_30"]
    w = w.select(["unit_id"] + [pl.col(c).alias(c + "_wall") for c in keep])
    d = d.join(w, on="unit_id", how="left")
    d = d.with_columns(((pl.col("nwin_10") >= MINWIN) & ((pl.col("phi_10_hi") - pl.col("phi_10_lo")) <= 1.0))
                       .alias("usable"))
    return d


def frac(mask):
    mask = [bool(x) for x in mask if x is not None]
    return (sum(mask), len(mask), (sum(mask) / len(mask)) if mask else float("nan"))


def score(d: pl.DataFrame) -> dict:
    S = {}
    u = d.filter(pl.col("nwin_10") >= MINWIN)
    r3 = u.filter(pl.col("regime") == "III")
    r3all = d.filter((pl.col("regime") == "III") & pl.col("r_F").is_finite())
    S["n_units"] = d.height
    S["n_units_minwin"] = u.height
    S["n_units_usable"] = int(d["usable"].sum())
    S["P1"] = {"minwin": frac(((r3["r_F"] >= 0.8) & (r3["r_F"] <= 1.2)).to_list()),
               "all_finite": frac(((r3all["r_F"] >= 0.8) & (r3all["r_F"] <= 1.2)).to_list()),
               "wall_minwin": frac(((r3["r_F_wall"] >= 0.8) & (r3["r_F_wall"] <= 1.2)).to_list())}
    mu, lo, hi, tau2 = L.re_pool(np.log(r3["r_F"].to_numpy()), r3["r_F_se_log"].to_numpy())
    S["r_F_pooled_III"] = [math.exp(mu), math.exp(lo), math.exp(hi), tau2]
    mu, lo, hi, tau2 = L.re_pool(np.log(r3["r_F_wall"].to_numpy()), r3["r_F_se_log_wall"].to_numpy())
    S["r_F_pooled_III_wall"] = [math.exp(mu), math.exp(lo), math.exp(hi), tau2]
    e = r3["E_F"].drop_nans().drop_nulls().to_numpy()
    S["P1b"] = {"median_E_F": float(np.median(e)) if len(e) else None, "n": len(e),
                "iqr": np.percentile(e, [25, 75]).tolist() if len(e) else None}
    S["P2"] = {"percall": frac((r3["phi_untrim"] > r3["phi_10"]).to_list()),
               "wall": frac((r3["phi_untrim_wall"] > r3["phi_10_wall"]).to_list()),
               "median_gap_percall": float((r3["phi_untrim"] - r3["phi_10"]).median()),
               "median_gap_wall": float((r3["phi_untrim_wall"] - r3["phi_10_wall"]).median()),
               "median_raw_minus_trim_wall": float((r3["phi_raw_wall"] - r3["phi_10_wall"]).median())}
    S["brackets_III"] = {"median_rF_g3": float((r3["phi_10"] / r3["phi_pred_g3"]).median()),
                         "median_rF_het": float((r3["phi_10"] / r3["phi_pred_het"]).median()),
                         "median_phi_pred": float(r3["phi_pred"].median()),
                         "median_phi_pred_g3": float(r3["phi_pred_g3"].median())}
    r1_ = u.filter((pl.col("regime") == "I") & pl.col("r_F").is_finite())
    mu, lo, hi, tau2 = L.re_pool(np.log(r1_["r_F"].to_numpy()), r1_["r_F_se_log"].to_numpy())
    S["r_F_pooled_I"] = [math.exp(mu), math.exp(lo), math.exp(hi), tau2]
    S["K"] = {"percall": frac((r3["r_F"] >= 2).to_list()), "wall": frac((r3["r_F_wall"] >= 2).to_list())}
    ex = u.filter(pl.col("r_F") > 1.2)
    S["P3"] = {"excess_units": ex.height, "sF_pos_sig": frac((ex["s_F_lo"] > 0).to_list()),
               "median_sF_excess": float(ex["s_F"].median()) if ex.height else None,
               "median_sF_all": float(u["s_F"].drop_nans().median())}
    r1 = u.filter(pl.col("regime") == "I")
    S["P4"] = {"phi_gt_1.2": frac((r1["phi_10"] > 1.2).to_list()),
               "median_phi_I": float(r1["phi_10"].median()),
               "ci_excl_1": frac((r1["phi_10_lo"] > 1).to_list()),
               "median_phi_II": float(u.filter(pl.col("regime") == "II")["phi_10"].median())}
    x = u.filter(pl.col("g").is_finite())
    rho, p = spearmanr(x["phi_10"].to_numpy() - 1, x["g"].to_numpy())
    rho3, p3 = spearmanr(r3["phi_10"].to_numpy() - 1, r3["g"].to_numpy())
    S["P5"] = {"rho_all": float(rho), "p_all": float(p), "n": x.height, "rho_III": float(rho3), "p_III": float(p3)}
    two = u.filter(pl.col("two_rooms"))
    S["P6"] = {"n_two_room": two.height, "same_gt_cross": frac((two["rho_same"] > two["rho_cross"]).to_list()),
               "cross_gt0_sig": frac((two["rho_cross_lo"] > 0).to_list()),
               "diff_sig": frac((two["rho_diff_lo"] > 0).to_list()),
               "median_same": float(two["rho_same"].median()), "median_cross": float(two["rho_cross"].median())}
    S["P7"] = {"cc_lt_wall10": frac((r3["phi_cc"] < r3["phi_10_wall"]).to_list()),
               "percall_lt_wall_T10": frac((r3["phi_10"] < r3["phi_10_wall"]).to_list()),
               "median_wall_minus_percall_III": float((r3["phi_10_wall"] - r3["phi_10"]).median()),
               "median_wall_minus_percall_I": float((r1["phi_10_wall"] - r1["phi_10"]).median())}
    S["P8"] = {"percall": frac(((u["fano_ratio"] / u["phi_10"] - 1).abs() <= 0.1).to_list()),
               "wall": frac(((u["fano_ratio_wall"] / u["phi_10_wall"] - 1).abs() <= 0.1).to_list())}
    S["exo"] = {"median_exo_in_minus_primary": float((u["phi_exo_in"] - u["phi_10"]).median())}
    S["null"] = {"phi_null_median": float(u["phi_null_mean"].median()),
                 "phi_null_q95_median": float(u["phi_null_q95"].median()),
                 "phi_gt_null_q95": frac((u["phi_10"] > u["phi_null_q95"]).to_list())}
    S["talkcalls"] = {"median_diff": float((u["phi_talkcalls"] - u["phi_10"]).median())}
    S["regime_medians"] = {reg: {"phi_10": float(u.filter(pl.col("regime") == reg)["phi_10"].median()),
                                 "phi_10_wall": float(u.filter(pl.col("regime") == reg)["phi_10_wall"].median()),
                                 "r_F": float(u.filter(pl.col("regime") == reg)["r_F"].median()),
                                 "n": u.filter(pl.col("regime") == reg).height} for reg in ("I", "II", "III")}
    return S


def periods(d: pl.DataFrame) -> pl.DataFrame:
    rows = []
    for (g,), grp in d.sort("unit_id").group_by(["goal_no"], maintain_order=True):
        ok = grp.filter(pl.col("r_F").is_finite() & pl.col("r_F_se_log").is_finite() & (pl.col("nwin_10") > 0))
        if ok.height:
            mu, lo, hi, tau2 = L.re_pool(np.log(ok["r_F"].to_numpy()), ok["r_F_se_log"].to_numpy())
            rF, rlo, rhi = math.exp(mu), math.exp(lo), math.exp(hi)
            pm = L.re_pool(ok["phi_10"].to_numpy(), ok["phi_10_se"].to_numpy())
        else:
            rF = rlo = rhi = float("nan")
            pm = (float("nan"),) * 4
        nwin = int(grp["nwin_10"].sum())
        wid = float((grp["phi_10_hi"] - grp["phi_10_lo"]).min()) if grp.height else float("nan")
        if nwin < MINWIN or not math.isfinite(rF) or (pm[2] - pm[1]) > 1.0:
            v = "descriptive"
        elif 0.8 <= rF <= 1.2:
            v = "supported"
        elif rF >= 2 or rF <= 0.5:
            v = "failed"
        else:
            v = "mixed"
        rows.append({"goal_no": int(g), "regime": grp["regime"][0], "units": ",".join(grp["unit_id"].to_list()),
                     "nwin": nwin, "phi": pm[0], "phi_lo": pm[1], "phi_hi": pm[2],
                     "phi_pred": float(np.average(grp["phi_pred"].to_numpy(), weights=np.maximum(grp["nwin_10"].to_numpy(), 1))),
                     "r_F": rF, "r_F_lo": rlo, "r_F_hi": rhi, "verdict": v, "min_ci_width": wid})
    return pl.DataFrame(rows)


def natives(d: pl.DataFrame) -> dict:
    N = {}
    get = lambda u, c: d.filter(pl.col("unit_id") == u)[c][0]  # noqa: E731
    # NE42
    o = {u: {c: get(u, c) for c in ("phi_10", "phi_10_lo", "phi_10_hi", "phi_pred", "r_F", "delta_F", "phi_10_wall",
                                    "nwin_10", "g")} for u in ("39", "40", "41")}
    side = (o["39"]["phi_10"] + o["41"]["phi_10"]) / 2
    pside = (o["39"]["phi_pred"] + o["41"]["phi_pred"]) / 2
    dside = (o["39"]["delta_F"] + o["41"]["delta_F"]) / 2
    N["NE42"] = {"units": o, "obs_drop": side - o["40"]["phi_10"], "pred_drop": pside - o["40"]["phi_pred"],
                 "N42a": (side - o["40"]["phi_10"]) >= 0.5 * (pside - o["40"]["phi_pred"]),
                 "delta_change": o["40"]["delta_F"] - dside, "N42b": abs(o["40"]["delta_F"] - dside) < 0.2}
    # NE14: 36a vs pool(36b, 36c)
    a = {c: get("36a", c) for c in ("phi_10", "phi_10_lo", "phi_10_hi", "phi_pred", "phi_untrim",
                                    "phi_untrim_wall", "phi_10_wall", "nwin_10", "g")}
    bc = d.filter(pl.col("unit_id").is_in(["36b", "36c"]))
    pb = L.re_pool(bc["phi_10"].to_numpy(), bc["phi_10_se"].to_numpy())
    pred_b = float(np.average(bc["phi_pred"].to_numpy(), weights=bc["nwin_10"].to_numpy()))
    gap_a = a["phi_untrim"] - a["phi_10"]
    gap_b = float(np.average((bc["phi_untrim"] - bc["phi_10"]).to_numpy(), weights=bc["nwin_10"].to_numpy()))
    gap_a_w = a["phi_untrim_wall"] - a["phi_10_wall"]
    gap_b_w = float(np.average((bc["phi_untrim_wall"] - bc["phi_10_wall"]).to_numpy(), weights=bc["nwin_10"].to_numpy()))
    N["NE14"] = {"36a": a, "36bc_phi": pb, "36bc_pred": pred_b, "obs_rise": pb[0] - a["phi_10"],
                 "pred_rise": pred_b - a["phi_pred"], "N14a": (pb[0] - a["phi_10"]) >= 0.5 * (pred_b - a["phi_pred"]),
                 "gap_a": gap_a, "gap_bc": gap_b, "N14b": gap_b > gap_a, "gap_a_wall": gap_a_w, "gap_bc_wall": gap_b_w}
    # NE43
    o = {u: {c: get(u, c) for c in ("phi_10", "phi_10_lo", "phi_10_hi", "phi_untrim", "phi_10_wall",
                                    "phi_untrim_wall", "phi_pred", "r_F", "nwin_10")} for u in ("51f", "51g", "51h")}
    N["NE43"] = {"units": o, "d_fg": o["51g"]["phi_10"] - o["51f"]["phi_10"],
                 "d_gh": o["51h"]["phi_10"] - o["51g"]["phi_10"],
                 "N43a": abs(o["51g"]["phi_10"] - o["51f"]["phi_10"]) < 0.15 and abs(o["51h"]["phi_10"] - o["51g"]["phi_10"]) < 0.15,
                 "gap_f": o["51f"]["phi_untrim"] - o["51f"]["phi_10"], "gap_g": o["51g"]["phi_untrim"] - o["51g"]["phi_10"],
                 "gap_f_wall": o["51f"]["phi_untrim_wall"] - o["51f"]["phi_10_wall"],
                 "gap_g_wall": o["51g"]["phi_untrim_wall"] - o["51g"]["phi_10_wall"]}
    N["NE43"]["N43b"] = N["NE43"]["gap_g"] < N["NE43"]["gap_f"]
    return N


def figures(d: pl.DataFrame, S: dict):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    FIG.mkdir(parents=True, exist_ok=True)
    col = {"I": "#86b6ef", "II": "#fab219", "III": "#1c5cab"}
    u = d.filter(pl.col("nwin_10") >= MINWIN)
    fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.1))
    for reg in ("I", "II", "III"):
        x = u.filter(pl.col("regime") == reg)
        ax[0].errorbar(x["phi_pred"], x["phi_10"], yerr=[x["phi_10"] - x["phi_10_lo"], x["phi_10_hi"] - x["phi_10"]],
                       fmt="o", ms=3.5, color=col[reg], ecolor=col[reg], alpha=0.8, lw=0.7, label=f"regime {reg}")
    t = np.linspace(0.9, 2.1, 10)
    ax[0].plot(t, t, "k-", lw=0.8)
    ax[0].fill_between(t, 0.8 * t, 1.2 * t, color="0.85", zorder=0, label="±20%")
    ax[0].plot(t, 2 * t, "k:", lw=0.8, label="kill (2×)")
    ax[0].set_xlim(0.9, 2.1)
    ax[0].set_ylim(0.4, 3.5)
    ax[0].set_xlabel(r"sum-rule prediction $\Phi_{\rm pred}(g_{\rm lag})$")
    ax[0].set_ylabel(r"observed $\Phi(10\,{\rm min})$, per-call clock")
    ax[0].legend(fontsize=6.5, loc="upper left", frameon=False)
    Ts = list(L.TS)
    for reg in ("I", "III"):
        x = u.filter(pl.col("regime") == reg)
        med = [float(x[f"phi_{T}"].drop_nans().median()) for T in Ts]
        q1 = [float(np.nanpercentile(x[f"phi_{T}"].to_numpy(), 25)) for T in Ts]
        q3 = [float(np.nanpercentile(x[f"phi_{T}"].to_numpy(), 75)) for T in Ts]
        ax[1].plot(Ts, med, "o-", color=col[reg], ms=3, label=f"regime {reg} (median, IQR)")
        ax[1].fill_between(Ts, q1, q3, color=col[reg], alpha=0.2)
    p3 = float(u.filter(pl.col("regime") == "III")["phi_pred"].median())
    ax[1].axhline(p3, color=col["III"], ls="--", lw=0.8, label=r"median $\Phi_{\rm pred}$ (III)")
    ax[1].axhline(1, color="k", lw=0.6)
    ax[1].set_xscale("log")
    ax[1].set_xticks(Ts)
    ax[1].set_xticklabels([str(T) for T in Ts])
    ax[1].set_xlabel("window T (min)")
    ax[1].set_ylabel(r"$\Phi(T)$")
    ax[1].legend(fontsize=6.5, frameon=False)
    fig.tight_layout()
    fig.savefig(FIG / "summary_obs_col.pdf")
    fig.savefig(FIG / "summary_obs_col.png", dpi=160)
    # synthetic figure
    s = pl.read_parquet(L.OUT / "synthetic/runs_final.parquet").filter(pl.col("unit_id") != "44b")
    fig, ax = plt.subplots(figsize=(3.5, 2.8))
    worlds = ["g0", "rho", "g15", "g30", "f5", "f30", "g15f30"]
    for k, w in enumerate(worlds):
        x = s.filter(pl.col("world") == w)
        r = (x["phi_10"] / x["phi_pred"]).to_numpy()
        ax.scatter(np.full(len(r), k) + np.random.default_rng(k).uniform(-0.2, 0.2, len(r)), r, s=6, color="#1c5cab",
                   alpha=0.6)
        ax.plot([k - 0.3, k + 0.3], [np.median(r)] * 2, "k-", lw=1.2)
    ax.axhspan(0.8, 1.2, color="0.85", zorder=0)
    ax.axhline(2, color="k", ls=":", lw=0.8)
    ax.set_xticks(range(len(worlds)))
    ax.set_xticklabels(["g=0", "private\npersist.", "g=.15", "g=.30", "field\n5 min", "field\n30 min", "g=.15\n+field"],
                       fontsize=6.5)
    ax.set_ylabel(r"$\Phi(10)/\Phi_{\rm pred}(g_{\rm true})$")
    fig.tight_layout()
    fig.savefig(FIG / "synthetic_col.pdf")
    fig.savefig(FIG / "synthetic_col.png", dpi=160)


def estimates(d: pl.DataFrame, P: pl.DataFrame, N: dict):
    sys.path.insert(0, str(ROOT / "infra/shared"))
    import estimates as E
    rows = []
    for r in d.iter_rows(named=True):
        if not (r["phi_10"] is not None and math.isfinite(r["phi_10"])):
            continue
        base = dict(period_unit=r["unit_id"], goal_no=r["goal_no"], n=float(r["nwin_10"]), n_kind="10-min windows",
                    role="replication", ci_level=0.95, first_day=r["first_day"], last_day=r["last_day"],
                    source="data/processed/H111-talk-fano-sum-rule/results/units.parquet")
        rows.append({**base, "statistic": "collective_fano_ratio", "channel": "talk_percall", "estimate": r["phi_10"],
                     "ci_lo": r["phi_10_lo"], "ci_hi": r["phi_10_hi"], "ci_kind": "percentile",
                     "method": "Phi(10 min) per-call residual, all-present window, hour-block demeaned; cell bootstrap",
                     "null": "per-agent circular block shift (Phi ~ 1)"})
        if r.get("phi_10_wall") is not None and math.isfinite(r["phi_10_wall"]):
            rows.append({**base, "statistic": "collective_fano_ratio", "channel": "talk_wall", "estimate": r["phi_10_wall"],
                         "ci_lo": r["phi_10_lo_wall"], "ci_hi": r["phi_10_hi_wall"], "ci_kind": "percentile",
                         "method": "Phi(10 min) wall clock, all-present window, hour-block demeaned; cell bootstrap",
                         "null": "per-agent circular block shift (Phi ~ 1)",
                         "source": "data/processed/H111-talk-fano-sum-rule/results/units_wall.parquet"})
        if r.get("r_F") is not None and math.isfinite(r["r_F"]):
            rows.append({**base, "statistic": "sum_rule_ratio", "channel": "talk_percall", "estimate": r["r_F"],
                         "ci_lo": r["r_F_lo"], "ci_hi": r["r_F_hi"], "ci_kind": "percentile",
                         "method": "Phi(10)/Phi_pred(H67 g_lag), g uncertainty propagated",
                         "null": "sum rule r_F = 1 (no free parameter)"})
            rows.append({**base, "statistic": "sum_rule_prediction", "channel": "talk_percall",
                         "estimate": r["phi_pred"], "ci_lo": None, "ci_hi": None, "ci_kind": "none",
                         "method": "mean-field linear Hawkes Phi_pred(g_lag, rooms)", "null": "none"})
    # natives
    nat = []
    ne = N["NE42"]
    nat.append(dict(period_unit="40", goal_no=40, statistic="ne42_phi_drop", channel="talk_percall",
                    estimate=ne["obs_drop"], ci_lo=None, ci_hi=None, ci_kind="none", n=3.0, n_kind="units",
                    method="mean Phi(10) of #39,#41 minus #40", null=f"sum-rule drop {ne['pred_drop']:.3f}",
                    role="native"))
    ne = N["NE14"]
    nat.append(dict(period_unit="36b", goal_no=36, statistic="ne14_phi_rise", channel="talk_percall",
                    estimate=ne["obs_rise"], ci_lo=None, ci_hi=None, ci_kind="none", n=3.0, n_kind="units",
                    method="Phi(10) pool 36b,36c minus 36a", null=f"sum-rule rise {ne['pred_rise']:.3f}",
                    role="native"))
    ne = N["NE43"]
    nat.append(dict(period_unit="51g", goal_no=51, statistic="ne43_phi_step_bookends", channel="talk_percall",
                    estimate=ne["d_fg"], ci_lo=None, ci_hi=None, ci_kind="none", n=2.0, n_kind="units",
                    method="Phi(10) 51g minus 51f", null="0 (trim removes the scheduler)", role="native"))
    nat.append(dict(period_unit="51h", goal_no=51, statistic="ne43_phi_step_nudger", channel="talk_percall",
                    estimate=ne["d_gh"], ci_lo=None, ci_hi=None, ci_kind="none", n=2.0, n_kind="units",
                    method="Phi(10) 51h minus 51g", null="0 (nudges are private inputs)", role="native"))
    for r in nat:
        r["source"] = "data/processed/H111-talk-fano-sum-rule/results/summary.json"
    E.write_estimates(rows + nat, hypothesis="H111")
    return len(rows) + len(nat)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-estimates", action="store_true")
    a = ap.parse_args()
    d = load()
    S = score(d)
    P = periods(d)
    N = natives(d)
    P.write_parquet(RES / "periods.parquet")
    out = {"scores": S, "natives": N, "periods": P.to_dicts()}
    (RES / "summary.json").write_text(json.dumps(out, indent=1, default=lambda o: o if not isinstance(o, (np.bool_,)) else bool(o)))
    figures(d, S)
    if not a.no_estimates:
        print("estimates rows:", estimates(d, P, N))
    print(json.dumps(S, indent=1, default=str))
    print(json.dumps(N, indent=1, default=str))
    print(P.select("goal_no", "regime", "nwin", "phi", "phi_pred", "r_F", "r_F_lo", "r_F_hi", "verdict"))


if __name__ == "__main__":
    main()
