"""H45 post-hoc checks (NOT pre-registered; added 2026-10-04 after seeing the round-1 results).

PH1 momentum: pooled regime-III share dependence with an indicator for "the agent's previous talk call is in the same
    segment" (R_old > 0 only then), so g_R is not just conversational momentum.
PH2 erasure decomposition: replies per call after a forced reset = talk propensity x reply share; the product's
    k-adjusted profile (is net import per call up or down?).
PH3 dilution exponent with the pending set restricted to the current segment (items erased by a reset excluded).
Writes posthoc.json.
"""
from __future__ import annotations

import json

import numpy as np
import polars as pl

import h45lib as L
from run_periods import prepare


def main():
    cu, _ = prepare()
    x3 = cu.filter(pl.col("regime").cast(pl.Utf8) == "III")
    out = {}
    # PH1
    t = L.talk_rows(x3).filter(pl.col("W").is_not_null() & (pl.col("W") > 0))
    t = t.with_columns((pl.col("R_old") > 0).cast(pl.Float64).alias("prev_in_seg"))
    y = t["eng_pending"].cast(pl.Float64).to_numpy()
    j = t["ctx_pos"].to_numpy()
    bands = np.minimum((j - 1) // 5, 8)
    X = np.column_stack([np.log(t["k_since_talk"].to_numpy().astype(float)),
                         np.log1p(t["R_old"].to_numpy() / 500), np.log(t["W"].to_numpy() / 1000),
                         t["prev_in_seg"].to_numpy()] + [(bands == q).astype(float) for q in range(1, 9)])
    g = L.codes(t["agent"].to_numpy(), t["pt_date"].to_numpy())
    keep = L._drop_constant_groups(y, g)
    y, X, g, days = y[keep], X[keep], L.codes(g[keep]), t["pt_date"].to_numpy()[keep]
    b, lt = L.cloglog_fe(y, X, g)
    rng = np.random.default_rng(21)
    bt = np.array([L.cloglog_fe(y, X, g, w=L.day_weights(days, rng), b0=b, lt0=lt, outer=15)[0][:4] for _ in range(100)])
    out["PH1_momentum"] = {"n": int(len(y)), **{f"{nm}": float(b[i]) for i, nm in enumerate(["g_k", "g_R", "g_W", "g_prev_in_seg"])},
                           **{f"{nm}_ci": L.ci(bt[:, i]) for i, nm in enumerate(["g_k", "g_R", "g_W", "g_prev_in_seg"])}}
    # same model restricted to talks whose previous talk is in the segment (R_old > 0 always)
    t2 = t.filter(pl.col("R_old") > 0)
    out["PH1_within_seg_only"] = L.share_dependence(t2, B=100)
    # PH2: replies per call (talk & eng_pending) after forced resets, k-adjusted
    x3b = x3.with_columns((pl.col("talk") & pl.col("eng_pending").fill_null(False)).alias("reply_call"))
    r = L.reset_profile(x3b, "open_forced", "reply_call", B=100)
    out["PH2_reply_per_call_forced"] = {k: r.get(k) for k in ("n", "baseline", "overshoot", "overshoot_ci", "tau", "tau_ci", "delta")}
    r = L.reset_profile(x3b.with_columns((pl.col("open_consol").fill_null(False) & ~pl.col("open_forced").fill_null(False)).alias("open_vol")),
                        "open_vol", "reply_call", B=100)
    out["PH2_reply_per_call_vol"] = {k: r.get(k) for k in ("n", "baseline", "overshoot", "overshoot_ci", "tau", "tau_ci")}
    # PH3: beta with k = items received in the current segment since the previous talk (erased items excluded)
    seg_k = (x3.sort("agent", "t_first")
             .with_columns(pl.col("talk").cast(pl.Int32).cum_sum().over("seg").alias("_tc"))
             .with_columns((pl.col("_tc") - pl.col("talk").cast(pl.Int32)).alias("_grp"))
             .with_columns(pl.col("k_new").cum_sum().over("seg", "_grp").alias("k_seg_pending")))
    tt = L.talk_rows(seg_k).filter(pl.col("k_seg_pending") >= 1).with_columns(pl.col("k_seg_pending").alias("k_since_talk"))
    out["PH3_beta_segment_pending"] = L.fit_beta_glm(tt, B=100)
    out["PH3_beta_ledger_pending"] = L.fit_beta_glm(L.talk_rows(x3), B=100)
    (L.DATA / "posthoc.json").write_text(json.dumps(out, indent=1, default=float))
    print(json.dumps({k: {kk: vv for kk, vv in v.items() if kk != "delta"} for k, v in out.items()}, indent=1, default=float))


if __name__ == "__main__":
    main()
