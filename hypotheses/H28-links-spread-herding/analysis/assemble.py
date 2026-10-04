"""Assemble H28 round 1 across goal periods: per-period table, random-effects pooling, card-level verdicts.

  uv run python hypotheses/H28-links-spread-herding/analysis/assemble.py

Writes data/processed/H28-links-spread-herding/results_round1.parquet and cross_period_round1.json; prints the tables
used in the card. Periods are compared only through fitted parameters (goal period = unit of analysis); pooling is a
DerSimonian-Laird random-effects meta-analysis of per-period estimates (named exception: hierarchical partial pooling).
"""
from __future__ import annotations

import json
import math
import sys
from pathlib import Path

import numpy as np
from scipy.stats import norm

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scheme"))
from h28lib import ALL_PERIODS, CANDIDATES, CONTRAST, HERDING, OUT, POST_NE09, PRE_NE09, gname  # noqa: E402
from period_folders import verdict  # noqa: E402


def dl(b, se):
    """DerSimonian-Laird random-effects pooled estimate."""
    b, se = np.asarray(b, float), np.asarray(se, float)
    ok = np.isfinite(b) & np.isfinite(se) & (se > 0)
    b, se = b[ok], se[ok]
    if len(b) == 0:
        return dict(b=float("nan"), se=float("nan"), p=float("nan"), tau2=float("nan"), k=0, I2=float("nan"))
    w = 1 / se ** 2
    bf = np.sum(w * b) / w.sum()
    Q = float(np.sum(w * (b - bf) ** 2))
    k = len(b)
    tau2 = max(0.0, (Q - (k - 1)) / (w.sum() - np.sum(w ** 2) / w.sum())) if k > 1 else 0.0
    ws = 1 / (se ** 2 + tau2)
    bp = float(np.sum(ws * b) / ws.sum())
    sp = float(math.sqrt(1 / ws.sum()))
    return dict(b=bp, se=sp, p=float(2 * norm.sf(abs(bp / sp))), tau2=tau2, k=k,
                I2=float(max(0.0, (Q - (k - 1)) / Q)) if Q > 0 else 0.0)


def load():
    rs = {}
    for g in ALL_PERIODS:
        p = OUT / gname(g) / "round1.json"
        if p.exists():
            rs[g] = json.loads(p.read_text())
    return rs


def main():
    import polars as pl
    rs = load()
    rows = []
    for g, r in rs.items():
        a = r["attr"]
        es = r["event_study"]
        cf = r.get("cf_summary", {})
        cc = r.get("cf_calibration", {})
        row = dict(goal=g, role=("candidate" if g in CANDIDATES else "herding" if g in HERDING else "contrast"),
                   tested=r["tested"], verdict=verdict(r), arrivals=r["arrivals"], arrivals_first=r["arrivals_first"],
                   links=r["links_universe"], K=r["K"], days=r["days"], agents=r["agents"],
                   kappa=r["kappa"], se=r["se"], p=r["p"], z_shift=r["z_shift"], null_mean=r["null"]["mean"],
                   J=r["J"], J_pd=r["pd"]["J"]["b"], J_nolinks=r["J_without_links"]["b"],
                   kappa_pd=r["pd"]["kappa"]["b"],
                   lead=r["lead"]["lead"]["b"], se_lead=r["lead"]["lead"]["se"], se_diff_lead=r["lead"]["diff"].get("se", np.nan), kappa_wlead=r["lead"]["kappa"]["b"], diff_lead=r["lead"]["diff"]["d"],
                   p_diff_lead=r["lead"]["diff"]["p"],
                   kappa_mom=r["momentum"]["kappa"]["b"], p_mom=r["momentum"]["kappa"]["p"], se_mom=r["momentum"]["kappa"]["se"],
                   kappa_naive=r["naive"]["b"], se_naive=r["naive"]["se"], p_naive=r["naive"]["p"],
                   kappa_action=r["action_only"]["b"], kappa_Uplus=r.get("Uplus", {}).get("kappa", {}).get("b", float("nan")),
                   d11=r["dose"]["d11"]["b"], se_d11=r["dose"]["d11"]["se"], d12=r["dose"]["d12"]["b"], se_d12=r["dose"]["d12"]["se"],
                   d13=r["dose"]["d13"]["b"], se_d13=r["dose"]["d13"]["se"], dS2=r["dose"]["dS2"]["b"], se_dS2=r["dose"]["dS2"]["se"],
                   S2_beyond=r["complex_S2"]["b"], se_S2_beyond=r["complex_S2"]["se"],
                   cv_complex_minus_simple=r["cv"]["complex"] - r["cv"]["simple"],
                   cv_primary_minus_occ=r["cv"]["primary"] - r["cv"]["occ_only"],
                   cv_primary_minus_fields=r["cv"]["primary"] - r["cv"]["fields"],
                   k015=r["kernel"]["lE015"]["b"], se_k015=r["kernel"]["lE015"]["se"],
                   k1560=r["kernel"]["lE1560"]["b"], se_k1560=r["kernel"]["lE1560"]["se"],
                   k60240=r["kernel"]["lE60240"]["b"], se_k60240=r["kernel"]["lE60240"]["se"],
                   addr=r["addressed"]["addr"]["b"], se_addr=r["addressed"]["addr"]["se"], n_addr=r["addressed"]["n"],
                   lam=a["lam"], lam_lo=a.get("lam_ci", [np.nan, np.nan])[0], lam_hi=a.get("lam_ci", [np.nan, np.nan])[1],
                   R_link=a["R_link"], R_lo=a.get("R_ci", [np.nan, np.nan])[0], R_hi=a.get("R_ci", [np.nan, np.nan])[1],
                   R_all=r["R_all"], n_exp=a["n_exp"], pi=r["pi_links_per_arrival"], k_s=r["k_s_per_link"],
                   es_pre=es["pre"]["O"] / es["pre"]["E"] if es["pre"]["E"] > 0 else np.nan,
                   es_post=es["post"]["O"] / es["post"]["E"] if es["post"]["E"] > 0 else np.nan,
                   es_pre_O=es["pre"]["O"], es_post_O=es["post"]["O"], es_pre_E=es["pre"]["E"], es_post_E=es["post"]["E"],
                   lat_med=r["latency"]["median_excess_lag"], lat_015=r["latency"]["excess_0_15"],
                   lat_1560=r["latency"]["excess_15_60"], lat_60240=r["latency"]["excess_60_240"],
                   cf_f05=cf.get("f05", {}).get("peak_occ", np.nan), cf_f0=cf.get("f0", {}).get("peak_occ", np.nan),
                   cf_cap=cf.get("cap2h", {}).get("peak_occ", np.nan), cf_f0_burst=cf.get("f0", {}).get("burst60", np.nan),
                   cf_f0_arr=cf.get("f0", {}).get("arrivals", np.nan), cf_f0_top=cf.get("f0", {}).get("top_visitors", np.nan),
                   obs_peak=cc.get("peak_occ", {}).get("obs", np.nan), sim_peak_lo=cc.get("peak_occ", {}).get("lo", np.nan),
                   sim_peak_hi=cc.get("peak_occ", {}).get("hi", np.nan), sim_peak_mean=cc.get("peak_occ", {}).get("mean", np.nan),
                   peak_inside=cc.get("peak_occ", {}).get("inside", None),
                   obs_burst=cc.get("burst60", {}).get("obs", np.nan), sim_burst_lo=cc.get("burst60", {}).get("lo", np.nan),
                   sim_burst_hi=cc.get("burst60", {}).get("hi", np.nan),
                   burst_inside=cc.get("burst60", {}).get("inside", None),
                   sim_arrivals=cc.get("arrivals", {}).get("mean", np.nan))
        if "room" in r:
            row.update(kappa_same=r["room"]["same"]["b"], kappa_other=r["room"]["other"]["b"], se_other=r["room"]["other"]["se"],
                       p_other=r["room"]["other"]["p"], other_rows=r["room"]["other_rows"], other_events=r["room"]["other_events"])
        rows.append(row)
    df = pl.DataFrame(rows, infer_schema_length=None).sort("goal")
    df.write_parquet(OUT / "results_round1.parquet")
    T = df.filter(pl.col("tested") & pl.col("role").is_in(["candidate", "herding"]))
    out = {}
    out["P1_counts"] = {v: int((T["verdict"] == v).sum()) for v in ("supported", "weak", "failed")}
    out["P1_tested"] = T.height
    out["P1_pooled"] = dl(T["kappa"], T["se"])
    nsup = out["P1_counts"]["supported"]
    out["P1_card"] = ("supported" if nsup >= math.ceil(2 * T.height / 3) and out["P1_pooled"]["b"] > 0 and out["P1_pooled"]["p"] < 0.01
                      else "failed" if nsup <= T.height / 3 else "mixed")
    S = T.filter(pl.col("verdict") == "supported")
    out["P2a"] = dict(n_pass=int(((S["diff_lead"] > 0) & (S["p_diff_lead"] < 0.05)).sum()), n=S.height,
                      pooled_lead=dl(T["lead"], T["se_lead"]), pooled_diff=dl(T["diff_lead"], T["se_diff_lead"]))
    out["P2b"] = dict(n_pass=int(((S["kappa_mom"] >= 0.5 * S["kappa"]) & (S["p_mom"] < 0.05)).sum()), n=S.height,
                      pooled=dl(T["kappa_mom"], T["se_mom"]))
    if "kappa_other" in df.columns:
        Rm = df.filter(pl.col("goal").is_in([37, 38, 41]) & pl.col("kappa_other").is_not_null())
        out["P2c"] = [dict(goal=int(r["goal"]), same=r["kappa_same"], other=r["kappa_other"], se_other=r["se_other"],
                           p_other=r["p_other"], other_rows=r["other_rows"], other_events=r["other_events"],
                           passes=bool(r["kappa_other"] < r["kappa_same"] and r["p_other"] > 0.05)) for r in Rm.iter_rows(named=True)]
        Ra = df.filter(pl.col("kappa_other").is_not_null())
        out["P2c_all_multiroom"] = [dict(goal=int(r["goal"]), same=r["kappa_same"], other=r["kappa_other"], se_other=r["se_other"],
                                         other_events=r["other_events"]) for r in Ra.iter_rows(named=True)]
    out["P3a_pooled_naive"] = dl(T["kappa_naive"], T["se_naive"])
    pre_O, pre_E, post_O, post_E = (float(T[c].sum()) for c in ("es_pre_O", "es_pre_E", "es_post_O", "es_post_E"))
    out["P3b"] = dict(pre=pre_O / pre_E, post=post_O / post_E, pre_O=pre_O, post_O=post_O,
                      passes=bool(post_O / post_E > 1 and (pre_O / pre_E - 1) < 0.5 * (post_O / post_E - 1)))
    out["P4"] = dict(d11=dl(T["d11"], T["se_d11"]), d12=dl(T["d12"], T["se_d12"]), d13=dl(T["d13"], T["se_d13"]),
                     dS2=dl(T["dS2"], T["se_dS2"]), S2_beyond=dl(T["S2_beyond"], T["se_S2_beyond"]),
                     complex_wins=int((T["cv_complex_minus_simple"] > 0).sum()), n=T.height)
    out["kernel"] = dict(k015=dl(T["k015"], T["se_k015"]), k1560=dl(T["k1560"], T["se_k1560"]), k60240=dl(T["k60240"], T["se_k60240"]))
    out["addressed"] = dl(T["addr"], T["se_addr"])
    out["P5"] = dict(lam_median=float(np.median(S["lam"])) if S.height else float("nan"),
                     lam_all_median=float(np.median(T["lam"])),
                     in_range=int(((S["lam"] >= 0.01) & (S["lam"] <= 0.15)).sum()), n=S.height)
    out["P6"] = dict(R_median=float(np.median(T["R_link"])), R_max=float(T["R_link"].max()),
                     all_below_half=bool((T["R_link"] < 0.5).all()), R_all_median=float(np.median(T["R_all"])))
    C = df.filter(pl.col("tested") & pl.col("cf_f0").is_not_null())
    if C.height:
        out["P7"] = dict(f0_median=float(np.median(C["cf_f0"])), f05_median=float(np.median(C["cf_f05"])),
                         cap_median=float(np.median(C["cf_cap"])), f0_burst_median=float(np.median(C["cf_f0_burst"])),
                         f0_arrivals_median=float(np.median(C["cf_f0_arr"])),
                         min_f0=float(C["cf_f0"].min()), calib_inside=int(C["peak_inside"].sum()), n=C.height,
                         burst_inside=int(C["burst_inside"].sum()))
    pre = df.filter(pl.col("goal").is_in(PRE_NE09))
    post = df.filter(pl.col("goal").is_in(POST_NE09))

    def lat_share(goals):
        H, N = 0, 0
        for g in goals:
            if g in rs:
                L = rs[g]["latency"]
                H = H + np.array(L["h_obs"]) - np.array(L["h_null"])
                N += L["n_pairs"]
        if N == 0:
            return float("nan"), float("nan")
        pos = np.clip(H, 0, None)
        return float(pos[:3].sum() / max(pos.sum(), 1e-9)), float(1000 * H[0] / N)
    s_pre, b_pre = lat_share(PRE_NE09)
    s_post, b_post = lat_share(POST_NE09)
    out["P8"] = dict(pre=dict(zip(pre["goal"].to_list(), pre["lat_med"].to_list())),
                     post=dict(zip(post["goal"].to_list(), post["lat_med"].to_list())),
                     pre_median=float(np.nanmedian(pre["lat_med"])) if pre.height else float("nan"),
                     post_median=float(np.nanmedian(post["lat_med"])) if post.height else float("nan"),
                     pre_share015=s_pre, post_share015=s_post, pre_excess_0_5_per1000=b_pre, post_excess_0_5_per1000=b_post,
                     passes=bool(np.nanmedian(post["lat_med"]) < np.nanmedian(pre["lat_med"]) and s_post > s_pre))
    shared = df.filter(pl.col("role").is_in(["candidate", "herding"]) & pl.col("tested"))
    contr = df.filter(pl.col("role") == "contrast")
    out["P9"] = dict(shared_lam_median=float(np.median(shared["lam"])),
                     contrast=dict(zip(contr["goal"].to_list(), contr["lam"].to_list())),
                     passes=int((contr["lam"] < np.median(shared["lam"])).sum()), n=contr.height)
    out["P10"] = dict(n_pass=int(((T["J"] > 0) & (T["J_pd"] > 0)).sum()), n=T.height,
                      drop=[float((a - b) / a) if a else float("nan") for a, b in zip(T["J_nolinks"], T["J"])])
    out["periods"] = df.select("goal", "role", "verdict", "kappa", "se", "z_shift", "lam", "R_link").to_dicts()
    (OUT / "cross_period_round1.json").write_text(json.dumps(out, indent=1, default=float))
    with pl.Config(tbl_rows=30, tbl_cols=30, tbl_width_chars=250, float_precision=3):
        print(df.select("goal", "role", "verdict", "arrivals", "links", "kappa", "se", "p", "z_shift", "null_mean", "lead",
                        "diff_lead", "p_diff_lead", "kappa_mom", "kappa_naive", "J", "J_pd"))
        print(df.select("goal", "lam", "lam_lo", "lam_hi", "R_link", "R_all", "d11", "dS2", "S2_beyond", "cv_complex_minus_simple",
                        "cv_primary_minus_occ", "es_pre", "es_post", "lat_med", "cf_f05", "cf_f0", "cf_cap", "obs_peak",
                        "sim_peak_lo", "sim_peak_hi", "kappa_action", "kappa_Uplus", "kappa_pd"))
    print(json.dumps({k: v for k, v in out.items() if k != "periods"}, indent=1, default=float))


if __name__ == "__main__":
    main()
