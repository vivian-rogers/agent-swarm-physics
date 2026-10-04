"""H45 period-native tests: NE41 (forced erasures, pooled regime III), NE42 (merge A-B-A), G51 (N sweep, cap hits),
NE03 (chat-mode fetch limit). Predictions are in goalperiod-subhypotheses/<id>/README.md (written before running).

Usage: uv run python hypotheses/H45-context-homeostasis/analysis/natives.py [--only NE41,NE42,G51,NE03] [--B 200]
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
import polars as pl

import h45lib as L
from run_periods import prepare

ROOT = L.ROOT
SH = ROOT / "data/processed/shared"
REG3 = [36, 37, 38, 39, 40, 41, 42, 44, 51]


def write(name: str, obj: dict):
    d = L.DATA / name
    d.mkdir(exist_ok=True)
    (d / "native.json").write_text(json.dumps(obj, indent=1, default=float))


# ----------------------------------------------------------------------------------------------- NE41

def ne41(cu: pl.DataFrame, B: int) -> dict:
    x = cu.filter(pl.col("goal_no").is_in(REG3) & (pl.col("regime").cast(pl.Utf8) == "III"))
    out = {"n_forced_segments": int(x.filter(pl.col("open_forced").fill_null(False))["seg"].n_unique()),
           "n_vol_segments": int(x.filter(pl.col("open_consol").fill_null(False) & ~pl.col("open_forced").fill_null(False))["seg"].n_unique())}
    out["forced_talk"] = L.reset_profile(x, "open_forced", "talk", B=B)
    xv = x.with_columns((pl.col("open_consol").fill_null(False) & ~pl.col("open_forced").fill_null(False)).alias("open_vol"))
    out["vol_talk"] = L.reset_profile(xv, "open_vol", "talk", B=B)
    # E1 profile (talk calls only) after forced resets: k_since_talk bins as the k control
    xt = L.talk_rows(x)
    out["forced_E1"] = L.reset_profile(xt, "open_forced", "eng_pending", B=B, kcol="k_since_talk")
    out["vol_E1"] = L.reset_profile(xt.with_columns((pl.col("open_consol").fill_null(False) & ~pl.col("open_forced").fill_null(False)).alias("open_vol")),
                                    "open_vol", "eng_pending", B=B, kcol="k_since_talk")
    out["share_forced"] = L.share_profile(x, "open_forced")
    out["share_vol"] = L.share_profile(xv, "open_vol")
    # k_new and search calls by position after forced resets (reading proxy)
    kp = (x.filter(pl.col("open_forced").fill_null(False) & pl.col("ctx_pos").is_between(1, 41))
          .group_by("ctx_pos").agg(pl.col("k_new").mean().alias("k_mean"), (pl.col("kind").cast(pl.Utf8) == "search").mean().alias("search"),
                                   pl.col("talk").mean().alias("talk"), pl.len().alias("n")).sort("ctx_pos"))
    out["position_raw"] = {k: kp[k].to_list() for k in kp.columns}
    # per-period overshoot (forced), for N1's per-period count
    per = {}
    for g in REG3:
        xg = x.filter(pl.col("goal_no") == g)
        if xg.filter(pl.col("open_forced").fill_null(False)).height > 500:
            r = L.reset_profile(xg, "open_forced", "talk", B=min(B, 100))
            per[f"G{g:02d}"] = {k: r.get(k) for k in ("n", "n_segments", "baseline", "overshoot", "overshoot_ci", "tau", "tau_ci")}
    out["per_period"] = per
    out["snapshot"] = reset_snapshot(x, B)
    return out


def reset_snapshot(x: pl.DataFrame, B: int) -> dict:
    """B1 = P(j=1) - r(j=1) on segments opened by a reset (action-row tokens) vs room chars received in the 30 min
    before the reset call; agent-day FE; also for forced resets only."""
    x = x.sort("agent", "t_first")
    # rolling 30-min sum of chars_new received before each call (same agent)
    res = {}
    rows = []
    for (a,), sub in x.select("agent", "t_call", "chars_new", "k_new").group_by(["agent"]):
        tt = sub["t_call"].dt.epoch("us").to_numpy()
        o = np.argsort(tt)
        tt = tt[o]
        ch = sub["chars_new"].to_numpy()[o].astype(float)
        cs = np.concatenate([[0], np.cumsum(ch)])
        lo = np.searchsorted(tt, tt - 30 * 60 * 1_000_000, side="left")
        v30 = cs[np.arange(len(tt))] - cs[lo]          # chars received strictly before this call, within 30 min
        rows.append(pl.DataFrame({"agent": np.full(len(tt), a), "t_us": tt, "v30": v30}))
    v = pl.concat(rows)
    y = (x.filter((pl.col("ctx_pos") == 1) & (pl.col("p_src").cast(pl.Utf8) == "act") & pl.col("open_consol").fill_null(False))
         .with_columns(pl.col("t_call").dt.epoch("us").alias("t_us"), (pl.col("P") - pl.col("r")).alias("B1"))
         .join(v, on=["agent", "t_us"], how="left").filter(pl.col("v30").is_not_null()))
    for name, sub in (("all_consol", y), ("forced", y.filter(pl.col("open_forced").fill_null(False)))):
        if sub.height < 100:
            res[name] = {"n": sub.height}
            continue
        g = L.codes(sub["agent"].to_numpy(), sub["pt_date"].to_numpy())
        yy0, xx0 = sub["B1"].to_numpy().astype(float), sub["v30"].to_numpy() / 1000.0
        days = sub["pt_date"].to_numpy()

        def fit(w=None):
            yy, xx = L.demean(g, yy0, xx0, w=w)
            return L.wls(xx[:, None], yy, w)[0]

        b = fit()
        rng = np.random.default_rng(11)
        bt = np.array([fit(L.day_weights(days, rng)) for _ in range(B)])
        res[name] = {"n": int(sub.height), "slope_tok_per_kchar": float(b), "ci": L.ci(bt),
                     "B1_median": float(np.median(yy0)), "v30_median_kchar": float(np.median(xx0)),
                     "room_tok_per_kchar_calibrated": 1000 * float(L.load_calibration()["Anthropic"]["b_per_char"])}
    return res


# ----------------------------------------------------------------------------------------------- NE42

def ne42(cu: pl.DataFrame, B: int) -> dict:
    x = cu.filter(pl.col("goal_no").is_in([39, 40, 41]))
    sp = L.set_points(x, by=("agent", "goal_no"))
    bs = L.band_segments(x)
    lam = bs.group_by("agent", "goal_no").agg(pl.col("lam").median().alias("lam_seg"))
    sp = sp.join(lam, on=["agent", "goal_no"], how="left")
    piv_s = sp.pivot(on="goal_no", index="agent", values="s_star")
    piv_l = sp.pivot(on="goal_no", index="agent", values="lam_seg")
    both = piv_s.join(piv_l, on="agent", suffix="_l").drop_nulls()
    if both.height < 4:
        return {"n_agents": both.height}
    ls = np.log(both.select(["39", "40", "41"]).to_numpy())
    ll = np.log(both.select(["39_l", "40_l", "41_l"]).to_numpy())
    s_bar = float(np.exp(ls).mean())
    dS = ls[:, 1] - ls[:, [0, 2]].mean(1)
    dL = ll[:, 1] - ll[:, [0, 2]].mean(1)
    phi_i = dS / ((1 - s_bar) * dL)

    def slope(idx):
        a, b = ls[idx], ll[idx]
        a = a - a.mean(1, keepdims=True)
        b = b - b.mean(1, keepdims=True)
        return float((a * b).sum() / (b * b).sum()) / (1 - s_bar)

    rng = np.random.default_rng(12)
    n = both.height
    bt_phi = [float(np.median(phi_i[rng.integers(0, n, n)])) for _ in range(B)]
    bt_sl = [slope(rng.integers(0, n, n)) for _ in range(B)]
    agg = (cu.filter(pl.col("goal_no").is_in([39, 40, 41])).group_by("goal_no")
           .agg((pl.col("R") / pl.col("ctx_pos")).filter(pl.col("ctx_pos").is_between(15, 35)).median().alias("lam_med"),
                pl.col("s").filter(pl.col("ctx_pos").is_between(15, 35)).median().alias("s_med"),
                pl.col("k_new").mean().alias("k_new_mean")).sort("goal_no"))
    return {"n_agents": n, "s_bar": s_bar, "frac_lam_up": float(np.mean(dL > 0)), "dlnlam_median": float(np.median(dL)),
            "dlns_median": float(np.median(dS)), "phi_median": float(np.median(phi_i)), "phi_ci": L.ci(np.array(bt_phi)),
            "slope_norm": slope(np.arange(n)), "slope_norm_ci": L.ci(np.array(bt_sl)),
            "per_agent": both.with_columns(pl.Series("phi", phi_i)).to_dicts(), "by_period": agg.to_dicts()}


# ----------------------------------------------------------------------------------------------- G51

def g51(cu: pl.DataFrame, B: int) -> dict:
    x = cu.filter(pl.col("goal_no") == 51)
    pu = pl.read_parquet(SH / "period_units.parquet").filter(pl.col("goal_no") == 51).select("unit_id", "n_agents", "first_day")
    sp = L.set_points(x, by=("agent", "unit_id"), min_calls=30)
    bs = L.band_segments(x)
    lam = bs.group_by("agent", "unit_id").agg(pl.col("lam").median().alias("lam_seg"))
    sp = sp.join(lam, on=["agent", "unit_id"], how="left").filter(pl.col("lam_seg") > 0)
    sp = sp.filter(pl.col("agent").count().over("agent") >= 3)
    s_bar = float(sp["s_star"].mean())
    g = L.codes(sp["agent"].to_numpy())
    y0, x0 = np.log(sp["s_star"].to_numpy()), np.log(sp["lam_seg"].to_numpy())

    def fit(w=None):
        yy, xx = L.demean(g, y0, x0, w=w)
        return L.wls(xx[:, None], yy, w)[0] / (1 - s_bar)

    b = fit()
    rng = np.random.default_rng(13)
    ua = np.unique(g)
    bt = []
    for _ in range(B):
        draw = rng.choice(ua, len(ua))
        w = np.bincount(draw, minlength=len(ua)).astype(float)[g]
        bt.append(fit(w))
    units = (x.group_by(pl.col("unit_id").cast(pl.Utf8)).agg(
        (pl.col("R") / pl.col("ctx_pos")).filter(pl.col("ctx_pos").is_between(15, 35)).median().alias("lam_med"),
        pl.col("s").filter(pl.col("ctx_pos").is_between(15, 35)).median().alias("s_med"),
        pl.col("k_new").mean().alias("k_new_mean"), pl.len().alias("n_calls"))
        .join(pu.with_columns(pl.col("unit_id").cast(pl.Utf8)), on="unit_id", how="left").sort("unit_id"))
    from scipy.stats import spearmanr
    rho_lam = spearmanr(units["n_agents"], units["lam_med"]).statistic
    rho_s = spearmanr(units["n_agents"], units["s_med"]).statistic
    # 200-event cap hits (all #51 calls, not just cu receiving calls)
    allc = L.load_calls(columns=["goal_no", "cap_hit", "n_omitted", "k_new", "first_of_day", "gap_kind", "after_pause"]).filter(pl.col("goal_no") == 51)
    cap = {"n_calls": allc.height, "n_cap_hit": int(allc["cap_hit"].sum()), "share": float(allc["cap_hit"].mean()),
           "omitted_items": int(allc["n_omitted"].sum()),
           "cap_hit_first_of_day_share": float(allc.filter(pl.col("cap_hit"))["first_of_day"].mean()) if allc["cap_hit"].sum() else None,
           "cap_hit_gap_kinds": allc.filter(pl.col("cap_hit"))["gap_kind"].cast(pl.Utf8).value_counts().to_dicts()}
    capc = x.filter(pl.col("cap_hit"))
    cap["cu_cap_hits"] = capc.height
    cap["cap_hit_ctx_pos_median"] = float(capc["ctx_pos"].median()) if capc.height else None
    return {"n_agent_units": sp.height, "n_agents": int(sp["agent"].n_unique()), "s_bar": s_bar,
            "slope_norm": float(b), "slope_norm_ci": L.ci(np.array(bt)), "rho_N_lam": float(rho_lam), "rho_N_s": float(rho_s),
            "units": units.to_dicts(), "cap": cap}


# ----------------------------------------------------------------------------------------------- NE03

def ne03(B: int) -> dict:
    c = L.load_calls(columns=["agent", "lab", "pt_date", "goal_no", "ctx_mode", "t_call", "P", "holdout", "room"])
    before = [d for d in pl.date_range(pl.date(2025, 8, 4), pl.date(2025, 8, 12), eager=True).cast(pl.Utf8).to_list()] + \
             ["2025-08-18", "2025-08-19"]
    after = pl.date_range(pl.date(2025, 8, 20), pl.date(2025, 8, 29), eager=True).cast(pl.Utf8).to_list()
    x = c.filter((pl.col("ctx_mode") == "chat") & pl.col("pt_date").is_in(before + after) & pl.col("P").is_not_null())
    assert not x["holdout"].any()
    chat = (pl.read_parquet(SH / "chat_core.parquet", columns=["t", "pt_date", "agent", "speaker_kind"])
            .filter(pl.col("pt_date").is_in(before + after)))
    # m_day: messages by others earlier the same day before t_call
    rows = []
    for (d,), sub in x.group_by(["pt_date"]):
        ch = chat.filter(pl.col("pt_date") == d)
        tt = np.sort(ch["t"].dt.epoch("us").to_numpy())
        own = {a: np.sort(ch.filter(pl.col("agent") == a)["t"].dt.epoch("us").to_numpy()) for a in sub["agent"].unique().to_list()}
        tc = sub["t_call"].dt.epoch("us").to_numpy()
        ag = sub["agent"].to_numpy()
        m_all = np.searchsorted(tt, tc, side="left")
        m_own = np.array([np.searchsorted(own[a], t, side="left") for a, t in zip(ag, tc)])
        rows.append(sub.with_columns(pl.Series("m_day", (m_all - m_own).astype(float))))
    x = pl.concat(rows).with_columns(pl.col("pt_date").is_in(after).alias("after"))
    out = {}
    agents_both = set(x.filter(~pl.col("after"))["agent"].unique().to_list()) & set(x.filter(pl.col("after"))["agent"].unique().to_list())
    for name, sub in (("all", x), ("agents_both_sides", x.filter(pl.col("agent").is_in(list(agents_both))))):
        res = {}
        for side in (False, True):
            s = sub.filter(pl.col("after") == side)
            med = s.group_by("agent", "pt_date").agg(pl.col("m_day").median().alias("mmed"))
            s = s.join(med, on=["agent", "pt_date"]).with_columns((pl.col("m_day") > pl.col("mmed")).alias("upper"))
            rr = {}
            for half in (False, True):
                h = s.filter(pl.col("upper") == half)
                if h.height < 50:
                    continue
                g = L.codes(h["agent"].to_numpy(), h["pt_date"].to_numpy())
                y0, x0 = h["P"].to_numpy().astype(float), h["m_day"].to_numpy().astype(float)
                days = h["pt_date"].to_numpy()

                def fit(w=None):
                    yy, xx = L.demean(g, y0, x0, w=w)
                    return L.wls(xx[:, None], yy, w)[0]

                b = fit()
                rng = np.random.default_rng(14)
                bt = np.array([fit(L.day_weights(days, rng)) for _ in range(B)])
                rr["upper" if half else "lower"] = {"n": int(h.height), "slope_tok_per_msg": float(b), "ci": L.ci(bt),
                                                    "m_median": float(np.median(x0)), "P_median": float(np.median(y0))}
            res["after" if side else "before"] = rr
        bu, au = res.get("before", {}).get("upper"), res.get("after", {}).get("upper")
        if bu and au:
            res["upper_ratio_after_before"] = au["slope_tok_per_msg"] / bu["slope_tok_per_msg"] if bu["slope_tok_per_msg"] else None
        out[name] = res
    # binned profile for the figure
    prof = (x.with_columns(pl.col("m_day").clip(0, 400).floordiv(20).alias("mb"))
            .group_by("after", "mb").agg(pl.col("P").median().alias("P_med"), pl.len().alias("n")).sort("after", "mb"))
    out["profile"] = prof.to_dicts()
    out["n_calls"] = {"before": int((~x["after"]).sum()), "after": int(x["after"].sum())}
    out["agents_both_sides"] = sorted(agents_both)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", default="NE41,NE42,G51,NE03")
    ap.add_argument("--B", type=int, default=200)
    a = ap.parse_args()
    todo = a.only.split(",")
    cu = None
    if set(todo) & {"NE41", "NE42", "G51"}:
        cu, _ = prepare()
    if "NE42" in todo:
        r = ne42(cu, a.B); write("NE42", r)
        print("NE42", {k: v for k, v in r.items() if k not in ("per_agent", "by_period")}, r["by_period"], flush=True)
    if "G51" in todo:
        r = g51(cu, a.B); write("G51", r)
        print("G51", {k: v for k, v in r.items() if k != "units"}, flush=True)
    if "NE03" in todo:
        r = ne03(a.B); write("NE03", r)
        print("NE03", {k: v for k, v in r.items() if k != "profile"}, flush=True)
    if "NE41" in todo:
        r = ne41(cu, a.B); write("NE41", r)
        print("NE41", {k: (v if not isinstance(v, dict) else {kk: vv for kk, vv in v.items() if kk not in ("raw", "delta")})
                       for k, v in r.items() if k not in ("share_forced", "share_vol", "position_raw")}, flush=True)


if __name__ == "__main__":
    main()
