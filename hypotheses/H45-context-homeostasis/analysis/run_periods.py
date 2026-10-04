"""H45 replication layer: the common estimators on every eligible non-holdout goal period.

For each period: set points (agent-level s*), regulation (eps, eta_W, RI; agent x unit fixed effects), the band test
(observed CV vs the within-agent W-permutation CV), the segment-length lever, P growth, the dilution exponent beta
(E1, cloglog with agent-day effects), the share dependence of engagement (g_R, g_W; cu talk calls), and the
k-adjusted talk profile after forced and voluntary resets. Writes data/processed/H45-context-homeostasis/G<NN>/results.json
and a cross-period summary.json.

Usage: uv run python hypotheses/H45-context-homeostasis/analysis/run_periods.py [--periods 38,41] [--B 200]
"""
from __future__ import annotations

import argparse
import json
import time

import numpy as np
import polars as pl

import h45lib as L

ELIGIBLE = [4, 5, 6, 8, 10, 11, 12, 13, 16, 17, 18, 19, 20, 21, 23, 24, 25, 26, 27, 30, 31, 33, 35, 36, 37, 38, 39,
            40, 41, 42, 44, 51]


def prepare(scale_other: float = 1.0) -> tuple[pl.DataFrame, pl.DataFrame]:
    """cu-mode calls with r, R, W, s (and R_old); all talk calls (any mode) for beta."""
    cal = L.load_calibration()
    c = L.load_calls()
    assert not c["holdout"].any()
    cu = L.add_share(c.filter((pl.col("ctx_mode") == "cu") & pl.col("seg").is_not_null()), cal, scale_other)
    # voluntary segment end: regime III = consolidation not at the cap; regimes I/II = the agent's session stop.
    # Segments whose next segment is on another day are censored by the day end (not voluntary).
    seg = (cu.group_by("seg").agg(pl.col("agent").first(), pl.col("pt_date").first(), pl.col("t_first").min().alias("t0"),
                                  pl.col("regime").first())
           .sort("agent", "t0").with_columns(pl.col("pt_date").shift(-1).over("agent").alias("next_date")))
    cu = cu.join(seg.select("seg", "next_date"), on="seg", how="left")
    vol = (pl.col("next_date") == pl.col("pt_date")) & pl.when(pl.col("regime").cast(pl.Utf8) == "III").then(
        pl.col("end_consol").fill_null(False) & ~pl.col("end_forced").fill_null(False)).otherwise(
        pl.col("end_session").fill_null(False) & ~pl.col("end_consol").fill_null(False))
    cu = cu.with_columns(vol.fill_null(False).alias("end_vol"))
    # the lever function reads end_consol/end_forced: map the regime-specific voluntary flag onto them
    cu = cu.with_columns(pl.col("end_vol").alias("end_consol"), pl.lit(False).alias("end_forced_lever"))
    talks = c.filter(pl.col("talk") & pl.col("eng_pending").is_not_null())
    return cu, talks


def w_permutation_cv(bs: pl.DataFrame, n_perm: int = 200, seed: int = 7) -> dict:
    """Band test: within-agent CV of segment shares observed vs after permuting W_bar across the agent's segments
    (keeps each segment's inflow, breaks any W-inflow coupling). A controller gives CV_obs < CV_perm."""
    x = bs.with_columns((pl.col("lam") * pl.col("j_bar")).alias("Rb")).filter(pl.col("agent").count().over("agent") >= 10)
    if x.height < 30:
        return {"n_seg": x.height}
    rng = np.random.default_rng(seed)
    ag = x["agent"].to_numpy()
    Rb, Wb = x["Rb"].to_numpy(), x["W_bar"].to_numpy()

    def cv(s):
        df = pl.DataFrame({"a": ag, "s": s})
        g = df.group_by("a").agg((pl.col("s").std() / pl.col("s").mean()).alias("cv"))
        return float(g["cv"].mean())

    obs = cv(Rb / (Rb + Wb))
    idx = {a: np.where(ag == a)[0] for a in np.unique(ag)}
    perm = []
    for _ in range(n_perm):
        Wp = Wb.copy()
        for a, ii in idx.items():
            Wp[ii] = Wb[rng.permutation(ii)]
        perm.append(cv(Rb / (Rb + Wp)))
    perm = np.array(perm)
    return {"n_seg": int(x.height), "cv_obs": obs, "cv_perm_median": float(np.median(perm)),
            "ratio": obs / float(np.median(perm)), "p_lower": float((np.sum(perm <= obs) + 1) / (n_perm + 1))}


def period_stats(cu: pl.DataFrame, talks: pl.DataFrame, g: int, B: int = 200) -> dict:
    t0 = time.time()
    x = cu.filter(pl.col("goal_no") == g)
    tk = talks.filter(pl.col("goal_no") == g)
    out = {"period": f"G{g:02d}", "goal_no": g, "regime": ",".join(sorted(set(x["regime"].cast(pl.Utf8).to_list()))),
           "n_cu_calls": x.height, "n_cu_calls_P": int(x["P"].is_not_null().sum()), "n_agents": int(x["agent"].n_unique()),
           "days": int(x["pt_date"].n_unique()), "units": sorted(set(x["unit_id"].cast(pl.Utf8).drop_nulls().to_list()))}
    sp = L.set_points(x, by=("agent",))
    out["set_points"] = {"n_agents": sp.height, "s_star_median": float(sp["s_star"].median()) if sp.height else None,
                         "s_star_min": float(sp["s_star"].min()) if sp.height else None,
                         "s_star_max": float(sp["s_star"].max()) if sp.height else None,
                         "by_agent": sp.select("agent", "lab", "s_star", "s_q25", "s_q75", "lam_med", "P_med", "n").to_dicts()}
    bs = L.band_segments(x)
    out["regulation"] = L.elasticities(bs, group_cols=("agent", "unit_id"), B=B)
    out["band_cv"] = w_permutation_cv(bs)
    lev = x.with_columns(pl.col("end_forced_lever").alias("end_forced"))
    out["lever"] = L.segment_length_lever(lev, B=B, group_cols=("agent",))
    out["p_growth"] = L.p_growth(x)
    tr = L.talk_rows(tk)
    out["beta"] = L.fit_beta_glm(tr, B=min(B, 100))
    # share dependence: cu talk calls with an observed share
    tcu = L.talk_rows(x)
    out["share_dependence"] = L.share_dependence(tcu, B=min(B, 100)) if x["regime"].cast(pl.Utf8).is_in(["II", "III"]).any() else {"n": 0}
    if (x["open_forced"].fill_null(False)).sum() > 200:
        out["reset_forced_talk"] = L.reset_profile(x, "open_forced", "talk", B=min(B, 100))
        vol_open = x.with_columns((pl.col("open_consol").fill_null(False) & ~pl.col("open_forced").fill_null(False)).alias("open_vol"))
        out["reset_vol_talk"] = L.reset_profile(vol_open, "open_vol", "talk", B=min(B, 100))
        out["share_profile_forced"] = L.share_profile(x, "open_forced")
    out["seconds"] = round(time.time() - t0, 1)
    return out


def verdict(r: dict) -> tuple[str, str]:
    """Amendment A2 (2026-10-04 06:46 UTC, after the synthetic, before real data): the per-period verdict uses P1 (RI)
    alone; per-period g_R/g_W are reported but not identified at single-period counts (synthetic)."""
    reg = r.get("regulation", {})
    ri, lo, hi = reg.get("RI"), *(reg.get("RI_ci") or [np.nan, np.nan])
    if ri is None or not np.isfinite(lo):
        return "n/a", "too few segments for the regulation estimate"
    if ri >= 0.5 and lo > 0:
        return "supported", f"RI {ri:.2f} [{lo:.2f}, {hi:.2f}]"
    if hi < 0.5:
        return "failed", f"RI {ri:.2f} [{lo:.2f}, {hi:.2f}]"
    return "mixed", f"RI {ri:.2f} [{lo:.2f}, {hi:.2f}]"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--periods", default=",".join(map(str, ELIGIBLE)))
    ap.add_argument("--B", type=int, default=200)
    ap.add_argument("--scale-other", type=float, default=1.0)
    ap.add_argument("--tag", default="")
    a = ap.parse_args()
    cu, talks = prepare(a.scale_other)
    res = {}
    for g in [int(v) for v in a.periods.split(",")]:
        r = period_stats(cu, talks, g, B=a.B)
        r["verdict"], r["verdict_text"] = verdict(r)
        res[r["period"]] = r
        d = L.DATA / r["period"]
        d.mkdir(exist_ok=True)
        (d / f"results{a.tag}.json").write_text(json.dumps(r, indent=1, default=float))
        reg = r["regulation"]
        print(f"{r['period']} {r['regime']:6s} segs {reg.get('n_seg')} s* {r['set_points']['s_star_median']} "
              f"RI {reg.get('RI')} {reg.get('RI_ci')} etaW {reg.get('eta_W')} beta {r['beta'].get('beta')} "
              f"gR {r['share_dependence'].get('g_R')} gW {r['share_dependence'].get('g_W')} "
              f"over {r.get('reset_forced_talk', {}).get('overshoot')} -> {r['verdict']} ({r['seconds']}s)", flush=True)
    if a.periods == ",".join(map(str, ELIGIBLE)):
        (L.DATA / f"replication{a.tag}.json").write_text(json.dumps(res, indent=1, default=float))


if __name__ == "__main__":
    main()
