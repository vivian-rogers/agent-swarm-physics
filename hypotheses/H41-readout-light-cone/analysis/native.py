"""H41 period-native tests (layer 2): G38 two-room cage, NE42 merge/split, G31 regime-I clock, G51 isolation rooms.

  uv run python hypotheses/H41-readout-light-cone/analysis/native.py

Predictions: ../README.md, "Native tests" (written 2026-10-04 before any real-data run).
Reads the scheme's G<NN>/ tables (and call_windows for talk-call counts); writes results/native.json.
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE.parent / "scheme"))
import h41core as C  # noqa: E402
import h41stats as S  # noqa: E402
from explore import channel_label, fix_cross  # noqa: E402

OUT = C.OUT
RES = OUT / "results"
SH = C.SH
H2 = 7200.0


def load(g):
    d = OUT / f"G{g:02d}"
    adf = fix_cross(pl.read_parquet(d / "adoptions.parquet"))
    hz = pl.read_parquet(d / "hazard.parquet")
    v = pl.read_parquet(d / "violations.parquet")
    items = pl.read_parquet(d / "items.parquet")
    return adf, hz, v, items


def boot_ratio(days, num, den, B=500, seed=0):
    """Day-bootstrap CI of a ratio of hazards; num/den: dict day -> (adopt, at_risk)."""
    rng = np.random.default_rng(seed)
    ud = sorted(set(num) | set(den))
    out = []
    for _ in range(B):
        pick = rng.choice(ud, size=len(ud), replace=True)
        a = np.sum([num.get(p, (0, 0)) for p in pick], axis=0)
        b = np.sum([den.get(p, (0, 0)) for p in pick], axis=0)
        if a[1] == 0 or b[1] == 0:
            continue
        out.append(((a[0] + .5) / (a[1] + .5)) / ((b[0] + .5) / (b[1] + .5)))
    return (float(np.quantile(out, .025)), float(np.quantile(out, .975))) if len(out) > 20 else (np.nan, np.nan)


# ------------------------------------------------------------------------------------------------ G38
def g38():
    adf, hz, v, _ = load(38)
    v = channel_label(v.join(adf.select("marker", "agent", "cross", "in_cone_len"), on=["marker", "agent"], how="left"))
    cross = adf.filter(pl.col("cross"))
    within = adf.filter(~pl.col("cross"))
    res = dict(n_adopt=adf.height, n_cross=cross.height, share_cross=cross.height / adf.height)
    res["a_cross_out_of_cone"] = float((~cross["in_cone"]).mean()) if cross.height else np.nan
    res["a_cross_out_of_cone_rob"] = float((~cross["in_cone_len"]).mean()) if cross.height else np.nan
    res["within_out_of_cone"] = float((~within["in_cone"]).mean())
    incone_cross = cross.filter(pl.col("in_cone"))
    res["cross_incone_Htr"] = incone_cross.group_by("H_tr").len().sort("H_tr").rows()
    # b: hazard per at-risk talk call within 2 h, in-room vs other-room
    num, den = {}, {}
    for (day, inr), sub in hz.group_by(["day", "in_room0"]):
        (den if inr else num)[day] = (int(sub["adopt"].sum()), int(sub["at_risk"].sum()))
    a_out = np.sum(list(num.values()), axis=0)
    a_in = np.sum(list(den.values()), axis=0)
    res["h_out"] = float(a_out[0] / a_out[1])
    res["h_in"] = float(a_in[0] / a_in[1])
    res["b_ratio"] = res["h_out"] / res["h_in"]
    res["b_ratio_ci"] = boot_ratio(None, num, den, seed=38)
    # c: channels of robustly acausal adoptions, cross vs within
    rob = v.filter(~pl.col("in_cone") & ~pl.col("in_cone_len"))
    for key, sub in [("cross", rob.filter(pl.col("cross"))), ("within", rob.filter(~pl.col("cross")))]:
        res[f"c_{key}_n"] = sub.height
        if sub.height:
            res[f"c_{key}_artweb"] = float((sub["artifact"].fill_null(False) | sub["web"].fill_null(False)).mean())
            res[f"c_{key}_identified"] = float((sub["channel"] != "unexplained").mean())
            res[f"c_{key}_mix"] = {r["channel"]: r["len"] / sub.height for r in sub.group_by("channel").len().iter_rows(named=True)}
    # d: delays
    res["d_med_delay_cross_s"] = float(cross["delay"].median()) if cross.height else np.nan
    res["d_med_delay_within_s"] = float(within["delay"].median())
    res["d_ratio"] = res["d_med_delay_cross_s"] / res["d_med_delay_within_s"]
    res["verdict"] = verdict_g38(res)
    return res


def verdict_g38(r):
    a = r["a_cross_out_of_cone"] >= 0.8
    b = r["b_ratio"] <= 0.2
    c = (r.get("c_cross_artweb", 0) or 0) >= 0.3 and (r.get("c_cross_artweb", 0) or 0) > (r.get("c_within_artweb", 0) or 0)
    if a and b and c:
        return "supported", dict(a=a, b=b, c=c)
    if (not a) or (not b):
        return "failed", dict(a=a, b=b, c=c)
    return "mixed", dict(a=a, b=b, c=c)


# ------------------------------------------------------------------------------------------------ NE42
def talk_calls(goal):
    cal = C.calendar()
    days = cal.filter((pl.col("goal_no") == goal) & ~pl.col("hold"))["pt_date"].to_list()
    cw = (pl.scan_parquet(SH / "call_windows.parquet")
          .filter(pl.col("pt_date").is_in(days) & ~pl.col("holdout") & (pl.col("ctx_mode") != "summary"))
          .select("agent", "pt_date", "talk", C.ts("t_first").alias("tf"), C.ts("t_call").alias("t")).collect())
    talk = {a: np.sort(sub.filter(pl.col("talk"))["tf"].to_numpy()) for (a,), sub in cw.group_by(["agent"])}
    calls = {a: np.sort(sub["t"].to_numpy()) for (a,), sub in cw.group_by(["agent"])}
    dayend = dict(zip(cal["pt_date"].to_list(), cal["we"].to_list()))
    return talk, calls, dayend


def ne42():
    cal = C.calendar()
    rt = pl.read_parquet(SH / "rooms_timeline.parquet").with_columns(C.ts("t_start").alias("ts"))
    t_merge = 1777914000.0  # 2026-05-04 17:00 UTC, just before the merge
    t_split = 1778519000.0  # 2026-05-11 17:03 UTC, just after the split
    part = {}
    for (a,), sub in rt.group_by(["agent"]):
        sub = sub.sort("ts")
        pre = sub.filter(pl.col("ts") <= t_merge)
        if pre.height:
            part[int(a)] = int(pre["room"][-1])
    post = {}
    for (a,), sub in rt.group_by(["agent"]):
        sub = sub.sort("ts")
        p2 = sub.filter(pl.col("ts") <= t_split + 3600)
        if p2.height:
            post[int(a)] = int(p2["room"][-1])
    out = {"partition_pre": part, "partition_post": post}
    for g in [39, 40, 41]:
        adf, hz, v, items = load(g)
        grp = part if g in (39, 40) else post
        a = adf.filter((pl.col("src") >= 0) & (pl.col("src") < 64))
        a = a.with_columns(pl.col("src").replace_strict(grp, default=None).alias("gs"),
                           pl.col("agent").replace_strict(grp, default=None).alias("ga"))
        a = a.filter(pl.col("gs").is_in([2, 3]) & pl.col("ga").is_in([2, 3]))
        a = a.with_columns((pl.col("gs") != pl.col("ga")).alias("xg"))
        r = dict(n_adopt=a.height, n_cross=int(a["xg"].sum()))
        for key, sub in [("cross", a.filter(pl.col("xg"))), ("within", a.filter(~pl.col("xg")))]:
            r[f"acaus_{key}"] = float((~sub["in_cone"]).mean()) if sub.height else np.nan
            r[f"acaus_rob_{key}"] = float((~sub["in_cone_len"]).mean()) if sub.height else np.nan
            e = sub.filter(pl.col("exposed") & pl.col("cyc_hop").is_not_null())
            r[f"cyc_med_{key}"] = float(e["cyc_hop"].median()) if e.height else np.nan
            r[f"n_{key}"] = sub.height
        # hazard per at-risk talk call within 2 h: cross-group vs within-group (agent sources of known group)
        talk, calls, dayend = talk_calls(g)
        it = items.filter((pl.col("src") >= 0) & (pl.col("src") < 64))
        it = it.with_columns(pl.col("src").replace_strict(grp, default=None).alias("gs")).filter(pl.col("gs").is_in([2, 3]))
        ad_map = {(m, ag): t for m, ag, t in zip(adf["marker"].to_list(), adf["agent"].to_list(), adf["t_use"].to_list())}
        cnt = {}
        for mk, t0, src, gs, day0 in zip(it["marker"].to_list(), it["t0"].to_list(), it["src"].to_list(), it["gs"].to_list(),
                                         it["day0"].to_list()):
            hz_end = min(t0 + H2, dayend.get(day0, t0 + H2))
            for ag, tf in talk.items():
                if ag == src or grp.get(ag) not in (2, 3):
                    continue
                ca = calls.get(ag)
                if ca is None or not np.any((ca > t0) & (ca <= dayend.get(day0, t0 + H2))):
                    continue
                sel = tf[(tf > t0) & (tf <= hz_end)]
                if len(sel) == 0:
                    continue
                tu = ad_map.get((mk, ag))
                if tu is not None and tu <= hz_end:
                    nr, ad = int(np.searchsorted(sel, tu + 1e-6)), 1
                    nr = max(nr, 1)
                else:
                    nr, ad = len(sel), 0
                key = ("x" if grp[ag] != gs else "w", day0)
                c0 = cnt.get(key, [0, 0])
                c0[0] += ad
                c0[1] += nr
                cnt[key] = c0
        num = {d: tuple(v_) for (k, d), v_ in cnt.items() if k == "x"}
        den = {d: tuple(v_) for (k, d), v_ in cnt.items() if k == "w"}
        ax = np.sum(list(num.values()), axis=0) if num else np.array([0, 0])
        aw = np.sum(list(den.values()), axis=0) if den else np.array([0, 0])
        r["h_cross"] = float(ax[0] / ax[1]) if ax[1] else np.nan
        r["h_within"] = float(aw[0] / aw[1]) if aw[1] else np.nan
        r["risk_cross"], r["risk_within"] = int(ax[1]), int(aw[1])
        r["ratio_cross_within"] = r["h_cross"] / r["h_within"] if r["h_within"] else np.nan
        r["ratio_ci"] = boot_ratio(None, num, den, seed=g)
        r["_num"], r["_den"] = num, den
        out[f"G{g}"] = r
    # A-B-A contrasts
    h = {g: out[f"G{g}"]["h_cross"] for g in (39, 40, 41)}
    out["a_ratio_40_39"] = h[40] / h[39] if h[39] else np.inf
    out["a_ratio_40_41"] = h[40] / h[41] if h[41] else np.inf
    # bootstrap the A-B-A ratio by days within each period
    rng = np.random.default_rng(42)
    rr = []
    for _ in range(500):
        hs = {}
        for g in (39, 40, 41):
            num = out[f"G{g}"]["_num"]
            ud = list(num)
            pick = rng.choice(ud, size=len(ud), replace=True)
            a_ = np.sum([num[p] for p in pick], axis=0)
            hs[g] = (a_[0] + .5) / (a_[1] + .5)
        rr.append((hs[40] / hs[39], hs[40] / hs[41]))
    rr = np.array(rr)
    out["a_ratio_40_39_ci"] = (float(np.quantile(rr[:, 0], .025)), float(np.quantile(rr[:, 0], .975)))
    out["a_ratio_40_41_ci"] = (float(np.quantile(rr[:, 1], .025)), float(np.quantile(rr[:, 1], .975)))
    for g in (39, 40, 41):
        out[f"G{g}"].pop("_num")
        out[f"G{g}"].pop("_den")
    a_ok = out["a_ratio_40_39"] >= 3 and out["a_ratio_40_41"] >= 3
    b_ok = (out["G39"]["acaus_cross"] >= 0.7 and out["G41"]["acaus_cross"] >= 0.7
            and abs(out["G40"]["acaus_cross"] - out["G40"]["acaus_within"]) <= 0.05)
    cw = [out[f"G{g}"]["cyc_med_within"] for g in (39, 40, 41)]
    c_ok = (max(cw) - min(cw)) / np.median(cw) < 0.3 if all(np.isfinite(cw)) else False
    out["checks"] = dict(a=a_ok, b=b_ok, c=bool(c_ok))
    out["verdict"] = "supported" if (a_ok and b_ok) else ("failed" if not a_ok else "mixed")
    return out


# ------------------------------------------------------------------------------------------------ G31
def g31(period_table: pl.DataFrame):
    adf, hz, v, _ = load(31)
    hj = S.hazard_jump(hz, B=500, seed=31)
    res = dict(J_in=hj["J_in"], J_in_ci=hj["J_in_ci"], risk_pre_in=hj["risk_pre_in"], adopt_o1_in=hj["adopt_o1_in"],
               powered_in=hj["powered_in"])
    r3 = period_table.filter((pl.col("regime") == "III") & pl.col("powered_in"))
    res["J_in_regIII_median"] = float(r3["J_in"].median()) if r3.height else np.nan
    # chat-mode calls between first exposure and use
    cal = C.calendar()
    days = cal.filter((pl.col("goal_no") == 31) & ~pl.col("hold"))["pt_date"].to_list()
    cc = C.cc_agents()
    cw = (pl.scan_parquet(SH / "call_windows.parquet")
          .filter(pl.col("pt_date").is_in(days) & ~pl.col("holdout") & (pl.col("ctx_mode") != "summary") & ~pl.col("agent").is_in(cc))
          .select("turn_id", "agent", C.ts("t_call").alias("t"), pl.col("ctx_mode").cast(pl.Utf8)).collect()
          .sort("agent", "t", "turn_id").with_columns(pl.int_range(pl.len()).over("agent").alias("ci")))
    chat_ci = {a: sub.filter(pl.col("ctx_mode") == "chat")["ci"].to_numpy() for (a,), sub in cw.group_by(["agent"])}
    e = adf.filter(pl.col("exposed") & pl.col("cyc_hop").is_not_null() & (pl.col("parent") >= 0) & (pl.col("parent") < 64))
    nchat = []
    for a, f, u in zip(e["agent"].to_list(), e["first_exp_ci"].to_list(), e["ci_use"].to_list()):
        cc_ = chat_ci.get(a, np.array([]))
        nchat.append(int(np.sum((cc_ >= f) & (cc_ <= u))))
    e = e.with_columns(pl.Series("chat_hop", nchat))
    res["cyc_med"] = float(e["cyc_hop"].median())
    res["chat_med"] = float(e["chat_hop"].median())
    res["talk_med"] = float(e["talk_hop"].median())
    res["n_hops"] = e.height
    # clock test: between-agent SD of log median hop delay, seconds vs receiving calls vs chat calls
    per = (e.group_by("agent").agg(pl.len().alias("n"), pl.col("dt_hop").median().alias("s"), pl.col("cyc_hop").median().alias("c"),
                                   pl.col("chat_hop").median().alias("k"))
           .filter(pl.col("n") >= 5))
    res["clock_n_agents"] = per.height
    if per.height >= 4:
        sd = lambda x: float(np.std(np.log(np.maximum(np.asarray(x, float), 0.5)), ddof=1))
        res["sd_log_seconds"] = sd(per["s"])
        res["sd_log_calls"] = sd(per["c"])
        res["sd_log_chatcalls"] = sd(per["k"])
        rng = np.random.default_rng(31)
        diffs = []
        for _ in range(1000):
            ii = rng.integers(0, per.height, per.height)
            diffs.append(sd(per["c"].to_numpy()[ii]) - sd(per["s"].to_numpy()[ii]))
        res["sd_diff_calls_minus_seconds_ci"] = (float(np.quantile(diffs, .025)), float(np.quantile(diffs, .975)))
    a_ok = bool(np.isfinite(hj["J_in_ci"][0]) and hj["J_in_ci"][0] > 1 and hj["J_in"] < res["J_in_regIII_median"])
    c_ok = bool(res.get("sd_log_calls", np.inf) < res.get("sd_log_seconds", -np.inf))
    b_ok = bool(res["cyc_med"] <= 5 and res["chat_med"] <= 2)
    res["checks"] = dict(a=a_ok, b=b_ok, c=c_ok)
    j_null = not (np.isfinite(hj["J_in_ci"][0]) and hj["J_in_ci"][0] > 1)
    res["verdict"] = "supported" if (a_ok and c_ok) else ("failed" if ((not c_ok) and j_null) else "mixed")
    return res


# ------------------------------------------------------------------------------------------------ G51
def g51(period_table: pl.DataFrame):
    adf, hz, v, items = load(51)
    cal = C.calendar()
    sk_rooms = pl.read_parquet(SH / "rooms_timeline.parquet").with_columns(C.ts("t_start").alias("ts"), C.ts("t_end").alias("te"))

    class _Sk:  # minimal stand-in for RoomIndex
        rooms = sk_rooms
    ri = C.RoomIndex(_Sk)
    agents = sorted(set(adf["agent"].to_list()) | set(items.filter(pl.col("src") < 64)["src"].to_list()))
    iso, occ_room = [], []
    for a, t, t0, r0 in zip(adf["agent"].to_list(), adf["t_use"].to_list(), adf["t0"].to_list(), adf["room0"].to_list()):
        r = ri.at(a, t)
        others = sum(1 for b in agents if b != a and ri.at(b, t) == r)
        # isolated: alone in a non-#general room at use AND never in the source's room between t0 and use
        iso.append(r != 0 and others == 0 and r0 not in ri.rooms_in(a, t0, t))
        occ_room.append(r)
    adf = adf.with_columns(pl.Series("isolated", iso), pl.Series("room_use", occ_room))
    vv = channel_label(v.join(adf.select("marker", "agent", "isolated", "room_use", "in_cone_len", "room0", "room_t0"),
                              on=["marker", "agent"], how="left"))
    isox = adf.filter(pl.col("isolated") & (pl.col("room0") == 0))
    res = dict(n_isolated=isox.height, isolated_rooms=sorted(set(isox["room_use"].to_list())))
    if isox.height:
        res["a_isolated_acausal"] = float((~isox["in_cone"]).mean())
        vi = vv.filter(pl.col("isolated").fill_null(False) & (pl.col("room0") == 0) & ~pl.col("in_cone"))
        res["a_isolated_identified"] = float((vi["channel"] != "unexplained").mean()) if vi.height else np.nan
        res["a_isolated_mix"] = {r["channel"]: r["len"] for r in vi.group_by("channel").len().iter_rows(named=True)}
    # #focus (room 15) <-> #general cross-room adoptions
    fx = adf.filter(((pl.col("room0") == 0) & (pl.col("room_t0") == 15)) | ((pl.col("room0") == 15) & (pl.col("room_t0") == 0)))
    res["n_focus_cross"] = fx.height
    if fx.height:
        res["b_focus_cross_incone"] = float(fx["in_cone"].mean())
        res["b_focus_cross_incone_rob"] = float(fx["in_cone_len"].mean())
        res["b_focus_Htr"] = fx.filter(pl.col("in_cone")).group_by("H_tr").len().sort("H_tr").rows()
    pr = period_table.filter(pl.col("goal") == 51)
    for k, col in [("b", "b"), ("b_lo", "b_ci_lo"), ("b_hi", "b_ci_hi"), ("c", "c"), ("c_lo", "c_ci_lo"), ("c_hi", "c_ci_hi"),
                   ("n_reg", "n_reg")]:
        res[f"cad_{k}"] = pr[col][0] if col in pr.columns and pr.height else None
    b_ok = res["cad_b"] is not None and 0.5 <= res["cad_b"] <= 1.5 and res["cad_b_lo"] > 0
    c_ok = res["cad_c"] is not None and res["cad_c"] > -0.2
    focus_ok = res.get("b_focus_cross_incone", 0) >= 0.7
    iso_ok = (res.get("a_isolated_identified", 0) or 0) >= 0.5 if res["n_isolated"] >= 5 else True
    res["checks"] = dict(a_iso_channels=iso_ok, b_focus=focus_ok, c_cadence_b=b_ok, c_cadence_c=c_ok)
    if b_ok and c_ok and iso_ok and focus_ok:
        res["verdict"] = "supported"
    elif (not c_ok) and (res["cad_b"] is not None and abs(res["cad_b"]) < 0.2):
        res["verdict"] = "failed"
    else:
        res["verdict"] = "mixed"
    return res


def focus_hops(fx: pl.DataFrame):
    """Hop count along the earliest logged path for in-cone #focus cross-room adoptions (recomputed with the fixed
    hop-count pass of h41core.cone; the stored H_tr column of round 1 is wrong, K and T are not affected)."""
    if fx.height == 0:
        return []
    cal = C.calendar()
    sk = C.load_skeleton(51, cal)
    msgs = sk.msgs
    hs = []
    for (m0,), sub in fx.group_by(["m0"]):
        t0 = float(msgs["t"][m0])
        src = int(msgs["node"][m0])
        t_end = float(sub["t_use"].max()) + 1
        T, K, H = C.cone(sk, src, t0, t_end)
        hs += [int(H[a]) for a in sub["agent"].to_list()]
    v, c = np.unique(hs, return_counts=True)
    return [[int(a), int(b)] for a, b in zip(v, c)]


def main():
    pt = pl.read_parquet(RES / "period_table.parquet")
    out = {"G38": g38(), "NE42": ne42(), "G31": g31(pt), "G51": g51(pt)}
    (RES / "native.json").write_text(json.dumps(out, indent=1, default=lambda o: float(o) if isinstance(o, (np.floating, np.integer))
                                                 else (list(o) if isinstance(o, tuple) else str(o))))
    for k, v in out.items():
        print(k, json.dumps(v, default=str)[:1500])


if __name__ == "__main__":
    main()
