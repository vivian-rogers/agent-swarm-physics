"""H99 round 2 summary: W0-corrected removal stack, call-clock kernel pools, room partition, R2 indirect-inference fit
against H67's g_lag, c_x gauge, R4 kicks; prediction scoring; per_period_estimates rows; per-period README sections.

Inputs: r2/results/{units,curves}.parquet, r2/results/kicks_r4.json, r2/synthetic/runs.parquet; H67 g_lag and H86
taylor_c_shared rows of per_period_estimates (read as data).
Outputs: r2/results/{r2_units.parquet, r2_summary.json}; per_period_estimates rows (role replication / native);
goalperiod-subhypotheses/G<NN>/README.md gets a "Round 2" section (idempotent).
Usage: uv run python .../r2_summarize.py [--no-write]
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

import numpy as np
import polars as pl
from scipy.stats import spearmanr

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parents[2] / "infra/shared"))
import h99lib as L  # noqa: E402
import r2run as RR  # noqa: E402

RES = RR.R2 / "results"
CARD = HERE.parent
SRC = "data/processed/H99-glauber-fluctuation-relaxation/r2/results/"
VARS = ["V0", "V1", "V2", "V3", "V4", "V5", "V3s", "V5s"]
N_W0 = 8


def iso_curve(g, y):
    """Mean synthetic drho1 per g1, made non-decreasing (pool adjacent violators)."""
    o = np.argsort(g)
    g, y = np.asarray(g)[o], np.asarray(y, float)[o]
    blocks = [[v] for v in y]
    i = 0
    while i < len(blocks) - 1:
        if np.mean(blocks[i]) > np.mean(blocks[i + 1]):
            blocks[i] = blocks[i] + blocks.pop(i + 1)
            i = max(i - 1, 0)
        else:
            i += 1
    yy = np.concatenate([[np.mean(b)] * len(b) for b in blocks])
    return g, yy


def invert(g, y, v):
    """g1 at which the curve reaches v (linear interpolation; linear extrapolation beyond 0.45; 0 below the curve)."""
    if not np.isfinite(v):
        return np.nan
    if v <= y[0]:
        return 0.0
    for k in range(len(g) - 1):
        if y[k] <= v <= y[k + 1] and y[k + 1] > y[k]:
            return float(g[k] + (v - y[k]) * (g[k + 1] - g[k]) / (y[k + 1] - y[k]))
    sl = (y[-1] - y[-2]) / (g[-1] - g[-2]) if g[-1] > g[-2] else np.nan
    return float(g[-1] + (v - y[-1]) / sl) if sl and sl > 0 else np.nan


def unit_table():
    U = pl.read_parquet(RES / "units.parquet")
    C = pl.read_parquet(RES / "curves.parquet")
    E = pl.read_parquet(RR.SH / "per_period_estimates.parquet")
    h67 = (E.filter((pl.col("hypothesis") == "H67") & (pl.col("statistic") == "readout_loop_gain_g_lag"))
           .select(pl.col("period_unit").alias("unit"), pl.col("estimate").alias("h67_g_lag"),
                   pl.col("ci_lo").alias("h67_g_lag_lo"), pl.col("ci_hi").alias("h67_g_lag_hi")))
    h86 = (E.filter((pl.col("hypothesis") == "H86") & (pl.col("statistic") == "taylor_c_shared")
                    & (pl.col("channel") == "activity_trim"))
           .select(pl.col("period_unit").alias("unit"), pl.col("estimate").alias("c_x")))
    for v in VARS:
        U = U.with_columns((pl.col(f"cg_{v}_drho1") - pl.col(f"w0_{v}_drho1")).alias(f"d_{v}"),
                           ((pl.col(f"cg_{v}_drho1_se") ** 2 + pl.col(f"w0sd_{v}_drho1") ** 2 / N_W0) ** 0.5).alias(f"d_{v}_se"))
    U = U.with_columns((pl.col("k_rho_s") - pl.col("w0_rho_s")).alias("rho_s_c"),
                       (pl.col("k_rho_s_lo") - pl.col("w0_rho_s")).alias("rho_s_c_lo"),
                       (pl.col("k_rho_s_hi") - pl.col("w0_rho_s")).alias("rho_s_c_hi"))
    fits = []
    for u in C["unit"].unique().to_list():
        cu = C.filter(pl.col("unit") == u).group_by("g1").agg(pl.col("V0_drho1").mean()).sort("g1")
        g, y = iso_curve(cu["g1"].to_numpy(), cu["V0_drho1"].to_numpy())
        r = U.filter(pl.col("unit") == u).to_dicts()[0]
        v, lo, hi = r["cg_V0_drho1"], r.get("cg_V0_drho1_lo"), r.get("cg_V0_drho1_hi")
        fits.append({"unit": u, "g1_fit": invert(g, y, v), "g1_fit_lo": invert(g, y, lo if lo is not None else np.nan),
                     "g1_fit_hi": invert(g, y, hi if hi is not None else np.nan), "curve_slope": float((y[-1] - y[0]) / (g[-1] - g[0])),
                     "curve": [round(float(x), 4) for x in y]})
    F = pl.DataFrame(fits)
    U = U.join(F, on="unit", how="left").join(h67, on="unit", how="left").join(h86, on="unit", how="left")
    U = U.with_columns((pl.col("g1_fit") / pl.col("h67_g_lag")).alias("ratio_fit_glag"),
                       (pl.col("g1_fit") / pl.col("k_g1_room")).alias("ratio_fit_g1room"))
    return U


def pool(S, c, se=None):
    p = L.re_pool(S[c].to_numpy(), S[se or c + "_se"].to_numpy())
    return {"median": float(np.nanmedian(S[c].to_numpy())) if S.height else np.nan, "re": p["mean"], "lo": p["lo"],
            "hi": p["hi"], "k": p["k"]}


def r2_validation(U):
    """Indirect-inference recovery on the synthetic W1 runs of the validation units (curves from the real run)."""
    p = RR.R2 / "synthetic" / "runs.parquet"
    if not p.exists():
        return None
    S = pl.read_parquet(p).filter(pl.col("world").is_in(["W1a", "W1b"]))
    C = pl.read_parquet(RES / "curves.parquet")
    out = []
    for r in S.iter_rows(named=True):
        cu = C.filter(pl.col("unit") == r["unit"]).group_by("g1").agg(pl.col("V0_drho1").mean()).sort("g1")
        if not cu.height:
            continue
        g, y = iso_curve(cu["g1"].to_numpy(), cu["V0_drho1"].to_numpy())
        f = invert(g, y, r["V0_drho1"])
        out.append({"world": r["world"], "true": r["p_g1"], "fit": f})
    D = pl.DataFrame(out)
    return {w: {"median_fit": float(D.filter(pl.col("world") == w)["fit"].median()),
                "share_within_x2": float(D.filter(pl.col("world") == w).select(
                    ((pl.col("fit") / pl.col("true")).is_between(0.5, 2.0))).to_series().mean()),
                "n": D.filter(pl.col("world") == w).height} for w in ("W1a", "W1b")}


def summarize(U):
    S3 = U.filter(pl.col("regime") == "III")
    S1 = U.filter(pl.col("regime") == "I")
    S2 = U.filter(pl.col("regime") == "II")
    G51 = U.filter(pl.col("goal_no") == 51)
    out = {"n_units": U.height, "n_III": S3.height}
    out["removal"] = {reg: {v: pool(S, f"d_{v}") for v in VARS} for reg, S in (("I", S1), ("II", S2), ("III", S3))}
    out["removal"]["G51"] = {v: pool(G51, f"d_{v}") for v in VARS}
    out["removal_round1grid_III"] = {v: float(np.nanmedian(S3[f"r1g_{v}_drho1"].to_numpy())) for v in VARS if f"r1g_{v}_drho1" in S3.columns}
    ok = np.isfinite(U["cg_V0_drho1"].to_numpy()) & np.isfinite(U["r1g_V0_drho1"].fill_null(np.nan).to_numpy())
    out["grid_agreement_r"] = float(np.corrcoef(U["cg_V0_drho1"].to_numpy()[ok], U["r1g_V0_drho1"].to_numpy()[ok])[0, 1])
    # c_x gauge
    cx = S3.filter(pl.col("c_x").is_not_null())
    out["cx"] = {}
    for v in ("V0", "V5"):
        x = cx.filter(pl.col(f"d_{v}").is_finite())
        rho, p = spearmanr(x["c_x"].to_numpy(), x[f"d_{v}"].to_numpy())
        out["cx"][v] = {"spearman": float(rho), "p": float(p), "n": x.height}
    out["cx"]["c_x_median_III"] = float(cx["c_x"].median())
    # call-clock kernel
    keys = ["beta_R1", "beta_P0", "beta_X1", "beta_X0", "beta_R2", "beta_X2", "rho_Y1", "J1_inflight", "J1_room", "J0_room",
            "J2_room", "beta_R1n", "beta_R1u", "beta_P0n", "beta_P0u", "beta_R2n", "beta_R2u", "J1n_inflight", "J1u_inflight",
            "J1u_room", "J2n_room", "J2u_room", "g1_inflight", "g1_room", "g2_room", "g0_room"]
    out["kernel"] = {reg: {k: {**pool(S, "k_" + k), "share_ci_pos": float((S["k_" + k + "_lo"] > 0).mean()),
                               "share_ci_neg": float((S["k_" + k + "_hi"] < 0).mean())} for k in keys}
                     for reg, S in (("I", S1), ("III", S3), ("G51", G51))}
    for reg, S in (("I", S1), ("III", S3)):
        rs = S.filter(pl.col("rho_s_c").is_finite())
        out["kernel"][reg]["rho_s_c"] = {"median": float(rs["rho_s_c"].median()),
                                         "share_resolved": float(((rs["rho_s_c_lo"] > 0) | (rs["rho_s_c_hi"] < 0)).mean()),
                                         "share_neg": float((rs["rho_s_c_hi"] < 0).mean()),
                                         "share_pos": float((rs["rho_s_c_lo"] > 0).mean()), "n": rs.height,
                                         "raw_median": float(rs["k_rho_s"].median()), "w0_median": float(rs["w0_rho_s"].median())}
        out["kernel"][reg]["ratio_named_unnamed_median"] = float(S["k_ratio_named_unnamed"].median())
        out["kernel"][reg]["ratio_J2_J1_median"] = float(S["k_ratio_J2_J1"].median())
    k3 = out["kernel"]["III"]
    out["kernel"]["III"]["pooled_ratios"] = {
        "named_over_unnamed_J1": k3["J1n_inflight"]["re"] / k3["J1u_inflight"]["re"],
        "P0n_over_R1n": k3["beta_P0n"]["re"] / k3["beta_R1n"]["re"],
        "J2_over_J1room": k3["J2_room"]["re"] / k3["J1_room"]["re"],
        "J2n_over_J1n": k3["J2n_room"]["re"] / k3["J1n_inflight"]["re"],
        "R2n_over_R1n": k3["beta_R2n"]["re"] / k3["beta_R1n"]["re"]}
    # room partition (minute grid)
    part = {}
    for v in ("V0", "V5"):
        P = S3.filter(pl.col(f"cg_{v}_pair_r1_diff").is_not_null() & pl.col(f"cg_{v}_pair_r1_diff_se").is_finite())
        if P.height:
            part[v] = {"n_units": P.height, "units": P["unit"].to_list(),
                       "r1_same": pool(P, f"cg_{v}_pair_r1_same"), "r1_cross": pool(P, f"cg_{v}_pair_r1_cross"),
                       "diff": pool(P, f"cg_{v}_pair_r1_diff"), "share_same": float(np.nanmedian(P[f"cg_{v}_pair_share_same_lag1"].to_numpy())),
                       "diff_ci_pos_share": float((P[f"cg_{v}_pair_r1_diff_lo"] > 0).mean()),
                       "w0_diff_median": float(np.nanmedian((P[f"w0_{v}_pair_r1_same"] - P[f"w0_{v}_pair_r1_cross"]).to_numpy()))
                       if f"w0_{v}_pair_r1_same" in P.columns else None}
            rs, rx = part[v]["r1_same"]["re"], part[v]["r1_cross"]["re"]
            part[v]["Pi_pooled"] = rs / rx if rx else np.nan
    out["partition"] = part
    # R2
    R2 = S3.filter(pl.col("g1_fit").is_finite())
    res_units = R2.filter(pl.col("h67_g_lag_lo") > 0)
    out["R2"] = {"n": R2.height, "g1_fit_median": float(R2["g1_fit"].median()),
                 "h67_g_lag_median": float(R2["h67_g_lag"].median()),
                 "g1_room_median": float(R2["k_g1_room"].median()),
                 "ratio_median_all": float(R2["ratio_fit_glag"].median()),
                 "ratio_of_medians": float(R2["g1_fit"].median() / R2["h67_g_lag"].median()),
                 "n_resolved": res_units.height,
                 "ratio_median_resolved": float(res_units["ratio_fit_glag"].median()) if res_units.height else np.nan,
                 "share_within_x2_resolved": float(res_units["ratio_fit_glag"].is_between(0.5, 2.0).mean()) if res_units.height else np.nan,
                 "share_above_2_resolved": float((res_units["ratio_fit_glag"] > 2).mean()) if res_units.height else np.nan,
                 "ratio_fit_g1room_median": float(R2["ratio_fit_g1room"].median()),
                 "g51": {"g1_fit_median": float(R2.filter(pl.col("goal_no") == 51)["g1_fit"].median()),
                         "h67_median": float(R2.filter(pl.col("goal_no") == 51)["h67_g_lag"].median())},
                 "validation": r2_validation(U)}
    k = RES / "kicks_r4.json"
    out["R4"] = json.loads(k.read_text()) if k.exists() else None
    return out


def score(s):
    rem3, rem51 = s["removal"]["III"]["V5"], s["removal"]["G51"]["V5"]
    k3 = s["kernel"]["III"]
    rs = k3["rho_s_c"]
    sc = {}
    sc["Q-R1a"] = {"obs": f"rho_s - W0 median {rs['median']:+.3f}; resolved {rs['share_resolved']:.0%} (negative {rs['share_neg']:.0%})",
                   "verdict": "failed" if rs["median"] < 0 else ("supported" if rs["share_resolved"] >= 0.7 else "mixed")}
    sc["Q-R1b"] = {"obs": f"beta(P0 named) {k3['beta_P0n']['re']:+.4f} vs beta(R1 named) {k3['beta_R1n']['re']:+.4f}",
                   "verdict": "supported" if k3["beta_P0n"]["re"] <= k3["beta_R1n"]["re"] / 3 else "failed"}
    j2, j2r = k3["J2_room"], k3["pooled_ratios"]["J2_over_J1room"]
    j2n = k3["J2n_room"]
    sc["Q-R1c"] = {"obs": f"J2 {j2['re']:+.4f} [{j2['lo']:+.4f}, {j2['hi']:+.4f}], J2/J1(room) {j2r:.2f}; named J2 {j2n['re']:+.4f} [{j2n['lo']:+.4f}, {j2n['hi']:+.4f}], ratio to named J1* {k3['pooled_ratios']['J2n_over_J1n']:.2f}",
                   "verdict": "supported" if (j2["lo"] > 0 and 0.2 <= j2r <= 0.8) else ("mixed" if j2n["lo"] > 0 else "failed")}
    r2 = s["R2"]
    sc["Q-R2"] = {"obs": f"g1_fit/g_lag median {r2['ratio_median_all']:.2f} (all {r2['n']}), {r2['ratio_median_resolved']:.2f} resolved ({r2['n_resolved']}); within x2 {r2['share_within_x2_resolved']:.0%}",
                  "verdict": "supported" if (0.5 <= r2["ratio_median_all"] <= 2 and r2["share_within_x2_resolved"] >= 0.6) else
                  ("failed" if r2["ratio_median_all"] > 2 or r2["ratio_median_all"] < 0.5 else "mixed")}
    sc["Q-S1"] = {"obs": f"V5 drho1(c) regime III median {rem3['median']:+.3f}; #51 RE {rem51['re']:+.3f} [{rem51['lo']:+.3f}, {rem51['hi']:+.3f}]",
                  "verdict": "supported" if (rem3["median"] >= 0.04 and rem51["lo"] > 0) else
                  ("failed" if (rem3["median"] < 0.02 and rem51["lo"] <= 0) else "mixed")}
    cx = s["cx"]["V5"]
    sc["Q-S2"] = {"obs": f"Spearman(drho1 V5, c_x) {cx['spearman']:+.2f} (p {cx['p']:.2f}, n {cx['n']})",
                  "verdict": "supported" if cx["spearman"] <= 0.3 else ("failed" if cx["spearman"] >= 0.5 and cx["p"] < 0.05 else "mixed")}
    pv = s["partition"].get("V5") or s["partition"].get("V0")
    if pv:
        pi, d = pv["Pi_pooled"], pv["diff"]
        cross = pv["r1_cross"]
        sc["Q-P1"] = {"obs": f"r1 same {pv['r1_same']['re']:+.4f}, cross {cross['re']:+.4f} [{cross['lo']:+.4f}, {cross['hi']:+.4f}], diff {d['re']:+.4f} [{d['lo']:+.4f}, {d['hi']:+.4f}], Pi {pi:.1f} ({pv['n_units']} units)",
                      "verdict": "supported" if (d["lo"] > 0 and (pi >= 2 or cross["re"] <= 0) and cross["lo"] <= 0 <= cross["hi"]) else
                      ("failed" if d["lo"] <= 0 <= d["hi"] else "mixed")}
    nu = k3["pooled_ratios"]["named_over_unnamed_J1"]
    x1, r1u = k3["beta_X1"]["re"], k3["beta_R1u"]["re"]
    sc["Q-P2"] = {"obs": f"named/unnamed J1* {nu:.1f}; beta(X1) {x1:+.4f} vs unnamed beta(R1) {r1u:+.4f} vs beta(R1) {k3['beta_R1']['re']:+.4f}",
                  "verdict": "supported" if (nu >= 5 and abs(x1) < r1u) else ("failed" if (nu <= 2 or x1 >= k3["beta_R1"]["re"]) else "mixed")}
    r4 = s["R4"] or {}
    ng = (r4.get("nudge_G51") or {}).get("ya")
    if ng:
        lo, hi = ng["omega_ci"]
        sc["Q-R4a"] = {"obs": f"#51 nudge Omega {ng['omega']:.2f} [{lo:.2f}, {hi:.2f}] (n {ng['n']}, peak lag {ng['peak']}); round-1 form {ng['ratio_round1_form']:.1f}",
                       "verdict": "supported" if ng["omega"] <= 2 else ("failed" if (lo is not None and lo > 2) else "mixed")}
    hr = r4.get("human_regimeIII") or {}
    hm = hr.get("ya")
    if hm:
        lo, hi = hm["omega_ci"]
        if lo is None:   # activity response unresolved (G at its peak ~ 0): score on talk per call (Amendment B2)
            hc = hr.get("yc")
            lo, hi = hc["omega_ci"]
            sc["Q-R4b"] = {"obs": f"regime-III human: activity response unresolved (A30 {hm['A']:.2f}, no CI); talk per call Omega {hc['omega']:.2f} [{lo:.2f}, {hi:.2f}] (n {hc['n']})",
                           "verdict": "supported" if (0.5 <= lo and hi <= 2) else ("failed" if (lo > 2 or hi < 0.5) else "mixed")}
        else:
            sc["Q-R4b"] = {"obs": f"regime-III human Omega {hm['omega']:.2f} [{lo:.2f}, {hi:.2f}] (n {hm['n']}, peak lag {hm['peak']})",
                           "verdict": "supported" if (0.5 <= lo and hi <= 2) else ("failed" if (lo > 2 or hi < 0.5) else "mixed")}
    return sc


def estimates_rows(U, s):
    rows = []
    for r in U.iter_rows(named=True):
        base = {"period_unit": r["unit"], "goal_no": int(r["goal_no"]), "role": "replication", "source": SRC + "r2_units.parquet"}
        def add(stat, ch, est, lo, hi, method, null, n=None, nk=None, ph=False, se=None, notes=None):
            if est is None or not np.isfinite(est):
                return
            lo = lo if (lo is not None and np.isfinite(lo)) else None
            hi = hi if (hi is not None and np.isfinite(hi)) else None
            rows.append({**base, "statistic": stat, "channel": ch, "estimate": float(est), "ci_lo": lo, "ci_hi": hi,
                         "ci_kind": "percentile" if lo is not None else "none", "se": se, "n": n, "n_kind": nk,
                         "method": method, "null": null, "post_hoc": ph, "notes": notes})
        for v in ("V0", "V5"):
            e, se = r[f"d_{v}"], r[f"d_{v}_se"]
            add(f"r2_drho1_{v}_w0corrected", "talk", e, e - 1.96 * se if se else None, e + 1.96 * se if se else None,
                f"round 2: call-skeleton minute grid, removal stack {v} (B1), drho1 minus mean of 8 W0 worlds (independent talk at the real calls); "
                "SE = block bootstrap and W0 spread in quadrature", "0 (W0 world)", r["n_calls_trim"], "trimmed receiving calls",
                True, se, "A2 statistic (post hoc in round 1); round-2 removal pre-registered")
        add("r2_readout_gain_room_gated", "talk", r.get("k_g1_room"), r.get("k_g1_room_lo"), r.get("k_g1_room_hi"),
            "round 2 R1: m_bar r_bar (beta(read at call, matched lag) - beta(cross-room, same window)); agent x day x class FE; own lags; 1-h block bootstrap",
            "0 (cross-room messages)", r.get("k_n_calls"), "receiving calls", False, r.get("k_g1_room_se"))
        add("r2_readout_gain_inflight_gated", "talk", r.get("k_g1_inflight"), r.get("k_g1_inflight_lo"), r.get("k_g1_inflight_hi"),
            "round 2 R1: m_bar r_bar (beta(read, matched) - beta(in flight, matched)); in-flight coefficient is negative in regime III",
            "0 (in-flight messages)", r.get("k_n_calls"), "receiving calls", False, r.get("k_g1_inflight_se"))
        add("r2_hop2_gain_room_gated", "talk", r.get("k_g2_room"), r.get("k_g2_room_lo"), r.get("k_g2_room_hi"),
            "round 2 R1: m_bar r_bar (beta(read one call earlier) - beta(cross-room, same window))", "0", r.get("k_n_calls"),
            "receiving calls", False, r.get("k_g2_room_se"))
        add("r2_named_J1_inflight", "talk", r.get("k_J1n_inflight"), r.get("k_J1n_inflight_lo"), r.get("k_J1n_inflight_hi"),
            "round 2 R1: per-message talk-probability jump of a read message naming the recipient over a named in-flight message",
            "0", r.get("k_n_calls"), "receiving calls", False, r.get("k_J1n_inflight_se"))
        add("r2_unnamed_J1_inflight", "talk", r.get("k_J1u_inflight"), r.get("k_J1u_inflight_lo"), r.get("k_J1u_inflight_hi"),
            "round 2 R1: per-message jump of an unnamed read message over an unnamed in-flight message", "0", r.get("k_n_calls"),
            "receiving calls", False, r.get("k_J1u_inflight_se"))
        add("r2_self_memory_call_clock", "talk", r.get("rho_s_c"), r.get("rho_s_c_lo"), r.get("rho_s_c_hi"),
            "round 2 R1: lag-1-call autocorrelation of talk centred in (agent, day, 30-min block), minus the W0 mean (centring bias)",
            "0", r.get("k_n_calls"), "receiving calls", False)
        if r.get("g1_fit") is not None and np.isfinite(r.get("g1_fit") or np.nan):
            add("r2_g1_fit_minute_memory", "talk", r["g1_fit"], r.get("g1_fit_lo"), r.get("g1_fit_hi"),
                "round 2 R2: hop-1 read-out gain needed by a call-skeleton simulator to reproduce the unit's minute-grid drho1 (V0); "
                "CI by inverting the drho1 CI", "H67 g_lag", r["n_calls_trim"], "trimmed receiving calls", True)
    r4 = s.get("R4") or {}
    for name, unit, goal, key in (("nudge_G51", "51g", 51, "ya"), ("nudge_G51", "51g", 51, "yc"),
                                  ("human_regimeIII", "51g", 51, "yc"), ("human_regimeI", "27", 27, "yc")):
        x = (r4.get(name) or {}).get(key)
        if not x or x["omega_ci"][0] is None:
            continue
        lo, hi = x["omega_ci"]
        rows.append({"period_unit": unit, "goal_no": goal, "role": "native", "statistic": f"r2_{name}_omega_receiving_call",
                     "channel": "activity" if key == "ya" else "talk_per_call", "estimate": x["omega"], "ci_lo": lo, "ci_hi": hi, "ci_kind": "percentile",
                     "n": x["n"], "n_kind": "kicked receiving calls", "source": SRC + "kicks_r4.json", "post_hoc": True,
                     "method": "round 2 R4: kick aligned on the recipient's receiving call; same agent-day-class placebo calls (past-only); "
                               "Omega = sum_k G(k) / (G(0) sum_k S(k)/S(0)), S = spontaneous regression; agent-day cluster bootstrap",
                     "null": "Onsager regression (1)", "notes": f"scope {name}; pooled over the scope's non-holdout units; period_unit = largest unit"})
    return rows


ROUND2_HDR = "## Round 2 (2026-10-04)"


def period_sections(U, s):
    sc = s["scoring"]
    for gdir in sorted((CARD / "goalperiod-subhypotheses").glob("G*")):
        m = re.match(r"G(\d+)", gdir.name)
        if not m:
            continue
        g = int(m.group(1))
        P = U.filter(pl.col("goal_no") == g).sort("unit")
        if not P.height:
            continue
        lines = [ROUND2_HDR, "",
                 "*Round-2 tests (card section \"Round 2\"; predictions written 21:20 UTC and Amendment B1 21:30 UTC, before real data). "
                 "Exploratory, non-holdout. Talk statistics stay post hoc in the A2 sense.*", "",
                 "| Unit | Δρ₁ V0 (W0-corr.) | Δρ₁ V5 (W0-corr.) | ρ_s − W0 | g₁ room-gated | g₁ in-flight-gated | g₂ room-gated | g₁,fit (R2) | H67 g_lag |",
                 "| --- | --- | --- | --- | --- | --- | --- | --- | --- |"]
        def f(x, d=3):
            return "–" if x is None or not np.isfinite(x) else f"{x:+.{d}f}"
        def fci(r, k, d=3):
            e, lo, hi = r.get(k), r.get(k + "_lo"), r.get(k + "_hi")
            if e is None or not np.isfinite(e):
                return "–"
            if lo is None or hi is None or not (np.isfinite(lo) and np.isfinite(hi)):
                return f(e, d)
            return f"{e:+.{d}f} [{lo:+.{d}f}, {hi:+.{d}f}]"
        for r in P.iter_rows(named=True):
            d0 = f"{f(r['d_V0'])} ± {r['d_V0_se']:.3f}" if r.get("d_V0_se") and np.isfinite(r["d_V0_se"]) else f(r["d_V0"])
            d5 = f"{f(r['d_V5'])} ± {r['d_V5_se']:.3f}" if r.get("d_V5_se") and np.isfinite(r["d_V5_se"]) else f(r["d_V5"])
            lines.append(f"| {r['unit']} | {d0} | {d5} | {fci(r, 'rho_s_c')} | {fci(r, 'k_g1_room')} | {fci(r, 'k_g1_inflight')} | "
                         f"{fci(r, 'k_g2_room')} | {fci(r, 'g1_fit', 2)} | {f(r.get('h67_g_lag'), 3)} |")
        reg = P["regime"][0]
        lines += ["", f"Regime {reg}. ± is one SE (block bootstrap and W0 spread). Data: `{SRC}r2_units.parquet`.", ""]
        if reg == "III":
            lines.append("Reading: the collective talk memory survives scheduler removal where it was present in round 1; reads couple at the next call "
                         "(room-gated g₁ ≈ H67's g_lag), mostly through named messages. See the card for pooled tests.")
        elif reg == "I":
            lines.append("Reading (descriptive): regime-I reads and in-flight messages raise talk equally (no read-out gate), so any collective memory here is field-like.")
        else:
            lines.append("Reading (descriptive): regime II, three units in all; see the card.")
        lines.append("")
        txt = (gdir / "README.md").read_text()
        if ROUND2_HDR in txt:
            txt = txt[:txt.index(ROUND2_HDR)].rstrip() + "\n\n"
        else:
            txt = txt.rstrip() + "\n\n"
        (gdir / "README.md").write_text(txt + "\n".join(lines))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--no-write", action="store_true")
    a = ap.parse_args()
    U = unit_table()
    s = summarize(U)
    s["scoring"] = score(s)
    keep = [c for c in U.columns if not c.startswith(("w0sd_",)) and c != "curve"]
    U.select(keep).write_parquet(RES / "r2_units.parquet")
    (RES / "r2_summary.json").write_text(json.dumps(s, indent=1, default=float))
    print(json.dumps(s["scoring"], indent=1))
    if not a.no_write:
        import estimates as E
        rows = estimates_rows(U, s)
        E.write_estimates(rows, hypothesis="H99")
        print("estimates rows", len(rows))
        period_sections(U, s)


if __name__ == "__main__":
    main()
