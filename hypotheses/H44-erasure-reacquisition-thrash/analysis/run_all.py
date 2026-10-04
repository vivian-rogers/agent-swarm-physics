"""H44 real-data run (exploratory, non-holdout): the replication estimator on every eligible regime-III goal period,
plus the period-native tests (G51 paths / memory dose / work commits; G36 NE41 onset + NE16; G38 loops; NE41 forced vs
voluntary, pre-trends, pooled estimates, cross-period trends).

Outputs: data/processed/H44-erasure-reacquisition-thrash/G<NN>/results.json, NE41/results.json, summary.json,
         per_period_estimates_H44.parquet (rows in the shared estimates schema, for the coordinator to merge)
Usage:   uv run python hypotheses/H44-erasure-reacquisition-thrash/analysis/run_all.py [--periods G37,G51] [--B 1000]
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402
from scipy import stats as ss  # noqa: E402

import h44lib as L  # noqa: E402
from h44lib import C  # noqa: E402

PERIODS = ["G36", "G37", "G38", "G39", "G40", "G41", "G42", "G44", "G51"]
NATIVE = {"G36": "NE41 onset at NE14 + NE16 memory fix", "G38": "loops: does an erasure break them?",
          "G51": "re-acquisition path -> output recovery; memory dose; DQ4 work commits"}
V3_FEATS = ["H_v3", "p_research_browse", "p_execute_task", "p_self_maintenance", "p_debug_recover", "p_verify_report",
            "p_monitor_wait", "p_idle", "p_plan_coordinate", "p_communicate_external", "progress_score", "err_rate",
            "p_blocked"]
BASH = [C.CAT[c] for c in ("write", "local_read", "notes_read", "remote_read", "run", "monitor", "setup")]
GUIC = [C.CAT[c] for c in ("look", "gui", "gui_type")]
PATH = {**{C.CAT[c]: "artifact" for c in ("local_read", "notes_read")}, C.CAT["remote_read"]: "remote",
        **{C.CAT[c]: "screen" for c in ("look", "gui", "gui_type")}, **{C.CAT[c]: "room" for c in ("room_read", "talk")},
        **{C.CAT[c]: "direct" for c in ("write", "run")}}


def j(x):
    return json.loads(json.dumps(x, default=lambda o: o.tolist() if hasattr(o, "tolist") else float(o)))


# ------------------------------------------------------------------------------------------------- pieces
def v3_test(v: pl.DataFrame, B: int, seed: int) -> dict:
    """Windows starting 0-5 min after a forced (voluntary) reset vs windows >= 5 min after one, no reset inside;
    paired within agent-day."""
    v = v.with_columns((pl.col("n_errors") / pl.col("n_turns").clip(1)).alias("err_rate"))
    out = {}
    rng = np.random.default_rng(seed)
    for kind in ("forced", "voluntary"):
        w = v.filter((pl.col("reset_kind") == kind) & ~pl.col("reset_inside") & pl.col("active"))
        w = w.with_columns(pl.when(pl.col("min_since") < 5).then(pl.lit("A")).otherwise(pl.lit("R")).alias("bin"))
        g = w.group_by("agent", "pt_date", "bin").agg([pl.col(f).mean() for f in V3_FEATS] + [pl.len().alias("n")])
        a = g.filter(pl.col("bin") == "A").drop("bin"); r = g.filter(pl.col("bin") == "R").drop("bin")
        m = a.join(r, on=["agent", "pt_date"], suffix="_r")
        res = {"n_agent_days": m.height, "n_windows_A": int(a["n"].sum()), "n_windows_R": int(r["n"].sum())}
        # density-matched pre-reset windows: ending within 5 min before a reset of this kind, no reset inside
        pw = v.filter((pl.col("next_kind") == kind) & ~pl.col("reset_inside") & pl.col("active")
                      & (pl.col("min_until") >= 0) & (pl.col("min_until") < 5))
        gp = pw.group_by("agent", "pt_date").agg([pl.col(f).mean() for f in V3_FEATS] + [pl.len().alias("n")])
        mp = a.join(gp, on=["agent", "pt_date"], suffix="_p")
        res["pre_matched"] = {"n_agent_days": mp.height, "n_windows_P": int(gp["n"].sum())}
        if mp.height >= 10:
            for f in V3_FEATS:
                d = (mp[f] - mp[f + "_p"]).to_numpy().astype(float)
                dd = d[np.isfinite(d)]
                bs = dd[rng.integers(0, len(dd), (B, len(dd)))].mean(1)
                res["pre_matched"][f] = [float(dd.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)),
                                         float(mp[f + "_p"].mean())]
        if m.height < 10:
            out[kind] = res
            continue
        idx = rng.integers(0, m.height, (B, m.height))
        for f in V3_FEATS:
            d = (m[f] - m[f + "_r"]).to_numpy().astype(float)
            ok = np.isfinite(d)
            dd = d[ok]
            bs = dd[rng.integers(0, len(dd), (B, len(dd)))].mean(1)
            res[f] = [float(dd.mean()), float(np.percentile(bs, 2.5)), float(np.percentile(bs, 97.5)),
                      float(m[f + "_r"].mean())]
        out[kind] = res
    return out


def loop_test(calls: pl.DataFrame, ev: pl.DataFrame, B: int, seed: int, hcol: str = "h", lcol: str = "in_loop") -> dict:
    """Events whose -10..-1 window holds >= 3 in-loop calls: does a loop command (hash) recur in +1..+10?
    Forced vs pseudo31 (and voluntary). hcol/lcol = exact hash (primary) or normalized hash (robustness)."""
    rng = np.random.default_rng(seed)
    res = {}
    rates = {}
    for kind in ("forced", "voluntary", "pseudo31"):
        p = L.panel(calls, ev.filter(pl.col("ev_kind") == kind), -10, 10)
        p = p.with_columns(pl.col(hcol).alias("h"), pl.col(lcol).alias("in_loop"))
        pre = p.filter((pl.col("k") < 0))
        lp = pre.group_by("ev_id").agg(pl.col("in_loop").sum().alias("nl"),
                                       pl.col("h").filter(pl.col("in_loop") & pl.col("h").is_not_null()).alias("hs"),
                                       pl.col("cl").first())
        lp = lp.filter(pl.col("nl") >= 3)
        post = p.filter(pl.col("k") > 0).select("ev_id", "h", "in_loop")
        hits = (post.join(lp.select("ev_id", "hs").explode("hs"), on="ev_id")
                .filter(pl.col("h") == pl.col("hs")).select("ev_id").unique())
        lp = lp.with_columns(pl.col("ev_id").is_in(hits["ev_id"].implode()).alias("recur"))
        anyl = post.group_by("ev_id").agg(pl.col("in_loop").any().alias("loop_post"))
        lp = lp.join(anyl, on="ev_id", how="left")
        rates[kind] = lp
        res[kind] = {"n_loop_events": lp.height, "recur": float(lp["recur"].mean()) if lp.height else float("nan"),
                     "loop_post": float(lp["loop_post"].mean()) if lp.height else float("nan"),
                     "n_events": int(p["ev_id"].n_unique())}
    for kind in ("forced", "voluntary"):
        a, b = rates[kind], rates["pseudo31"]
        if a.height < 15 or b.height < 15:
            continue
        cls = np.unique(np.r_[a["cl"].to_numpy(), b["cl"].to_numpy()], return_inverse=True)[1]
        ia, ib = cls[: a.height], cls[a.height:]
        ncl = cls.max() + 1
        ya, yb = a["recur"].to_numpy().astype(float), b["recur"].to_numpy().astype(float)
        Sa, Na = np.bincount(ia, ya, ncl), np.bincount(ia, minlength=ncl).astype(float)
        Sb, Nb = np.bincount(ib, yb, ncl), np.bincount(ib, minlength=ncl).astype(float)
        W = L.boot_weights(ncl, B, rng)
        pa, pb = (W @ Sa) / np.clip(W @ Na, 1e-9, None), (W @ Sb) / np.clip(W @ Nb, 1e-9, None)
        odds = lambda x: np.clip(x, 1e-6, 1 - 1e-6) / (1 - np.clip(x, 1e-6, 1 - 1e-6))
        OR = odds(pa) / odds(pb)
        p0a, p0b = ya.mean(), yb.mean()
        res[f"OR_{kind}_vs_pseudo"] = [float(odds(p0a) / odds(p0b)), *L._ci(OR)]
    return res


def path_test(calls: pl.DataFrame, ev: pl.DataFrame, B: int, seed: int) -> dict:
    """Forced events: first substantive post-reset call (+1..+3) -> writes in +4..+10 minus the pre-erasure write rate
    (-20..-1), stratified by agent x pre-mode (shell / GUI / mixed); differences vs the 'screen' path."""
    rng = np.random.default_rng(seed)
    e = ev.filter((pl.col("ev_kind") == "forced") & (pl.col("n_post_avail") >= 10) & (pl.col("n_pre_avail") >= 20))
    p = L.panel(calls, e, -20, 10)
    sub = ~pl.col("cat").is_in([C.CAT[c] for c in ("setup", "other", "idle", "monitor")])
    first = (p.filter((pl.col("k") >= 1) & (pl.col("k") <= 3) & sub).sort("k").group_by("ev_id")
             .agg(pl.col("cat").first().alias("fcat")))
    pre = p.filter(pl.col("k") < 0).group_by("ev_id").agg(
        pl.col("any_write").mean().alias("w_pre"), pl.col("cat").is_in(BASH).mean().alias("bash_share"),
        pl.col("cat").is_in(GUIC).mean().alias("gui_share"), pl.col("cl").first(), pl.col("agent").first())
    post = p.filter((pl.col("k") >= 4) & (pl.col("k") <= 10)).group_by("ev_id").agg(
        pl.col("any_write").mean().alias("w_post"), pl.col("n_work").sum().alias("work_post"))
    fw = (p.filter((pl.col("k") >= 1) & pl.col("any_write")).group_by("ev_id").agg(pl.col("k").min().alias("k_first_w")))
    d = (pre.join(post, on="ev_id").join(first, on="ev_id", how="left").join(fw, on="ev_id", how="left")
         .with_columns(pl.col("fcat").replace_strict(PATH, default="none").fill_null("none").alias("path"),
                       pl.when(pl.col("bash_share") >= 0.6).then(pl.lit("shell")).when(pl.col("gui_share") >= 0.6)
                       .then(pl.lit("gui")).otherwise(pl.lit("mixed")).alias("mode"),
                       (pl.col("w_post") - pl.col("w_pre")).alias("dw"),
                       pl.col("k_first_w").fill_null(11).alias("kfw")))
    out = {"n": d.height, "path_shares": {k: float(v) for k, v in
                                           d.group_by("path").len().with_columns(pl.col("len") / d.height).rows()},
           "by_mode": {m: {pa: float(n) for pa, n in g.group_by("path").len().rows()} for (m,), g in d.group_by("mode")}}
    # stratified (agent x mode) mean of dw and kfw by path, relative to screen
    d = d.with_columns((pl.col("agent").cast(pl.Utf8) + "|" + pl.col("mode")).alias("st"))
    paths = ["artifact", "remote", "room", "direct", "none"]
    cl_codes, cl = np.unique(d["cl"].to_numpy(), return_inverse=True)
    ncl = len(cl_codes)
    st_codes, st = np.unique(d["st"].to_numpy(), return_inverse=True)
    pathv = d["path"].to_numpy()
    W = L.boot_weights(ncl, B, rng)

    def strat_diff(y, w_cl, target):
        # per stratum means for target and screen; weight strata by min(n_t, n_s)
        w = w_cl[cl] if w_cl is not None else np.ones(len(pathv))
        res = []
        for ycol in y:
            mt = pathv == target; ms = pathv == "screen"
            St_t = np.bincount(st[mt], ycol[mt] * w[mt], len(st_codes)); Nt = np.bincount(st[mt], w[mt], len(st_codes))
            St_s = np.bincount(st[ms], ycol[ms] * w[ms], len(st_codes)); Ns = np.bincount(st[ms], w[ms], len(st_codes))
            ok = (Nt > 0) & (Ns > 0)
            wt = np.minimum(Nt, Ns) * ok
            diff = np.where(ok, St_t / np.clip(Nt, 1e-9, None) - St_s / np.clip(Ns, 1e-9, None), 0)
            res.append(float((diff * wt).sum() / max(wt.sum(), 1e-9)))
        return res

    ys = [d["dw"].to_numpy().astype(float), d["kfw"].to_numpy().astype(float)]
    out["vs_screen"] = {}
    for t in paths:
        if (pathv == t).sum() < 30:
            continue
        pt = strat_diff(ys, None, t)
        bs = np.array([strat_diff(ys, W[b], t) for b in range(min(B, 300))])
        out["vs_screen"][t] = {"n": int((pathv == t).sum()), "d_write_rate": [pt[0], *L._ci(bs[:, 0])],
                               "d_k_first_write": [pt[1], *L._ci(bs[:, 1])]}
    out["raw_means"] = {k: {"dw": float(g["dw"].mean()), "kfw": float(g["kfw"].mean()), "n": g.height}
                        for (k,), g in d.group_by("path")}
    return out


def dose_test(calls: pl.DataFrame, ev: pl.DataFrame) -> dict:
    e = ev.filter((pl.col("ev_kind") == "forced") & pl.col("lines_added").is_not_null())
    p = L.panel(calls, e, -20, 10)
    g = p.group_by("ev_id").agg(pl.col("any_write").filter(pl.col("k").is_between(1, 10)).mean().alias("wp"),
                                pl.col("any_write").filter(pl.col("k").is_between(-20, -11)).mean().alias("wf"),
                                pl.col("agent").first())
    g = g.join(e.select("ev_id", "lines_added", "n_lines"), on="ev_id").drop_nulls()
    g = g.with_columns((pl.col("wp") - pl.col("wf")).alias("dip"),
                       (pl.col("lines_added") / pl.col("n_lines").clip(1)).alias("dose"))
    if g.height < 30:
        return {"n": g.height}
    gd = g.with_columns([(pl.col(c) - pl.col(c).mean().over("agent")).alias(c + "_dm") for c in ("dip", "dose", "lines_added")])
    r1 = ss.spearmanr(gd["dose_dm"], gd["dip_dm"])
    r2 = ss.spearmanr(gd["lines_added_dm"], gd["dip_dm"])
    return {"n": g.height, "rho_dose_dip_within": [float(r1.statistic), float(r1.pvalue)],
            "rho_lines_dip_within": [float(r2.statistic), float(r2.pvalue)],
            "median_lines_added": float(g["lines_added"].median()), "median_dose": float(g["dose"].median())}


def deltaV(cur: dict, st: dict, n_forced: int, calls: pl.DataFrame) -> dict:
    """Write calls and work commits lost per forced erasure over +1..+20 (curve minus the far-pre rate)."""
    ks = np.array(cur["k"])
    m = (ks >= 1) & (ks <= 20)
    far = st["windows"]["far"]
    wl = float(np.sum(np.array(cur["W"]["est"])[m] - far["W"][0]))
    kl = float(np.sum(np.array(cur["work"]["est"])[m] - far["work"][0]))
    tw = float(calls["any_write"].sum()); tk = float(calls["n_work"].sum())
    return {"write_calls_lost_per_erasure": wl, "work_commits_lost_per_erasure": kl,
            "share_write_calls_lost": -wl * n_forced / max(tw, 1), "share_work_commits_lost": -kl * n_forced / max(tk, 1),
            "erasures_per_100_calls": 100 * n_forced / max(calls.height, 1)}


def verdict(stF: dict, sus: dict) -> tuple[str, dict]:
    c5, c10 = stF["contrasts"]["post5_vs_far"], stF["contrasts"]["post10_vs_far"]
    th, om, sg, dh = c5["Theta_c"], c10["Omega"], c5["d_sigma"], c5["d_H"]
    ok_th = th[1] > 0 and th[0] >= L.THETA_FLOOR
    ok_om = om[2] < 0
    ok_temp = sg[1] > 0 or dh[1] > 0
    sus_opp = bool(sus.get("rr_post") and sus["rr_post"][2] < 1)
    flags = {"Theta_pos": ok_th, "Omega_neg": ok_om, "sigma_or_H_up": ok_temp, "P4b_opposite": sus_opp}
    if stF["n_events"] < 150:
        return "descriptive", flags
    if th[2] < 0.01 or om[1] >= 0:
        return "failed", flags
    if ok_th and ok_om and ok_temp and not sus_opp:
        return "supported", flags
    return "mixed", flags


def run_period(per: str, calls_all, ev_all, v3_all, rp_all, pp_all, B: int) -> dict:
    t0 = time.time()
    calls = calls_all.filter(pl.col("period") == per)
    ev = ev_all.filter(pl.col("period") == per)
    res = {"period": per, "role": "native" if per in NATIVE else "replication", "n_calls": calls.height,
           "n_agents": int(calls["agent"].n_unique()), "n_days": int(calls["pt_date"].n_unique()),
           "events": {k: int(v) for k, v in ev.group_by("ev_kind").len().rows()}}
    stats, curv = {}, {}
    for kind, (kmin, kmax) in (("forced", (-20, 20)), ("voluntary", (-20, 20)), ("pseudo31", (-20, 10)),
                               ("pseudo21", (-10, 20))):
        p = L.panel(calls, ev.filter(pl.col("ev_kind") == kind), kmin, kmax)
        if p.height == 0:
            continue
        stats[kind] = L.window_stats(p, B=B, seed=1)
        stats[kind]["class"] = L.classify(stats[kind]) if kind != "pseudo21" else L.classify(stats[kind], "post5_vs_near", "post10_vs_near")
        if kind in ("forced", "voluntary", "pseudo21"):
            curv[kind] = L.curves(p, B=300, seed=2, kmin=kmin, kmax=kmax)
        if kind == "forced":
            # balanced subset: events with the full +1..+20 window
            full = ev.filter((pl.col("ev_kind") == "forced") & (pl.col("n_post_avail") >= 20) & (pl.col("n_pre_avail") >= 20))
            pb = L.panel(calls, full, -20, 20)
            stats["forced_balanced"] = L.window_stats(pb, B=300, seed=3, windows=("post5", "post10", "far"))
    res["stats"], res["curves"] = stats, curv
    res["v3"] = v3_test(v3_all.filter(pl.col("period") == per), B=B, seed=4)
    rp = rp_all.filter(pl.col("period") == per)
    res["replies"] = {k: L.reply_rates(rp, k, B=B, seed=5) for k in ("forced", "voluntary")}
    pp = pp_all.filter(pl.col("period") == per)
    res["pull"] = {f"{lab}_{m}": L.pull_did(pp, lab, m, B=300, seed=6) for lab in ("forced", "voluntary") for m in ("bge", "gte")}
    res["loops"] = loop_test(calls, ev, B=B, seed=7)
    res["loops_norm"] = loop_test(calls, ev, B=B, seed=7, hcol="h_norm", lcol="in_loop_norm")
    res["dose"] = dose_test(calls, ev)
    if "forced" in stats:
        res["deltaV"] = deltaV(curv["forced"], stats["forced"], res["events"].get("forced", 0), calls)
        res["verdict"], res["verdict_flags"] = verdict(stats["forced"], res["replies"]["forced"])
    if per == "G51" or per == "G38":
        res["paths"] = path_test(calls, ev, B=B, seed=8)
    if per == "G36":
        res["native_G36"] = {}
        for u in ("36b", "36c"):
            cu = calls.filter(pl.col("unit_id") == u)
            eu = ev.filter((pl.col("unit_id") == u) & (pl.col("ev_kind") == "forced"))
            pu = L.panel(cu, eu, -20, 20)
            su = L.window_stats(pu, B=B, seed=9)
            res["native_G36"][u] = {"n_events": su["n_events"], "Theta": su["contrasts"]["post5_vs_far"]["Theta"],
                                    "Theta_c": su["contrasts"]["post5_vs_far"]["Theta_c"],
                                    "Omega": su["contrasts"]["post10_vs_far"]["Omega"],
                                    "d_sigma": su["contrasts"]["post5_vs_far"]["d_sigma"],
                                    "dR": su["contrasts"]["post5_vs_far"]["dR"],
                                    "mem_lines_added_median": float(eu["lines_added"].median()) if eu["lines_added"].drop_nulls().len() else None,
                                    "mem_lines_added_mean": float(eu["lines_added"].mean()) if eu["lines_added"].drop_nulls().len() else None,
                                    "n_mem": int(eu["lines_added"].drop_nulls().len())}
            res["native_G36"][u]["notes_read_share"] = float((cu["cat"] == C.CAT["notes_read"]).mean())
        # first two days of forced erasure
        d2 = ["2026-03-24", "2026-03-25"]
        e2 = ev.filter(pl.col("pt_date").is_in(d2) & (pl.col("ev_kind") == "forced"))
        s2 = L.window_stats(L.panel(calls, e2, -20, 20), B=B, seed=10)
        res["native_G36"]["first_two_days"] = {"n_events": s2["n_events"], "Theta": s2["contrasts"]["post5_vs_far"]["Theta"],
                                               "Theta_c": s2["contrasts"]["post5_vs_far"]["Theta_c"],
                                               "Omega": s2["contrasts"]["post10_vs_far"]["Omega"]}
    res["notes_read_share"] = float((calls["cat"] == C.CAT["notes_read"]).mean())
    res["reacq_share_all"] = float(calls["cat"].is_in(C.REACQ_IDX).mean())
    res["write_share_all"] = float(calls["any_write"].mean())
    # hour-of-day match of pseudo vs forced
    hf = ev.filter(pl.col("ev_kind") == "forced")["hour_pt"].to_numpy()
    hp = ev.filter(pl.col("ev_kind") == "pseudo31")["hour_pt"].to_numpy()
    if len(hf) and len(hp):
        res["hour_ks"] = float(ss.ks_2samp(hf, hp).statistic)
    C.log(per, res.get("verdict"), f"{time.time() - t0:.0f}s")
    return j(res)


def ne41(results: dict) -> dict:
    """Spanning NE41 folder: forced vs voluntary, pooled random effects, pre-trends, cross-period trends."""
    out = {"pooled": {}, "per_period": {}}
    for kind in ("forced", "voluntary", "pseudo31"):
        for tag, stat in (("post5_vs_far", "Theta"), ("post5_vs_far", "Theta_c"), ("post5_vs_far", "dR"), ("post10_vs_far", "Omega"),
                          ("post5_vs_far", "d_sigma"), ("post5_vs_far", "d_H"), ("post10_vs_far", "work_rel"),
                          ("near_vs_far", "Omega"), ("near_vs_far", "dR"), ("near_vs_far", "Theta")):
            e, lo, hi = [], [], []
            for per, r in results.items():
                c = r["stats"].get(kind, {}).get("contrasts", {}).get(tag, {}).get(stat)
                if c:
                    e.append(c[0]); lo.append(c[1]); hi.append(c[2])
            out["pooled"][f"{kind}:{tag}:{stat}"] = L.dl_pool(e, lo, hi)
    for key in ("log_did", "rr_post", "rr_has_parent", "rr_pre_erased"):
        for kind in ("forced", "voluntary"):
            e, lo, hi = [], [], []
            for per, r in results.items():
                c = r["replies"][kind].get(key)
                if c and np.isfinite(c[0]) and c[0] > 0 or (key == "log_did" and c and np.isfinite(c[0])):
                    v = np.array(c, float)
                    if key != "log_did":
                        v = np.log(np.clip(v, 1e-9, None))
                    if np.all(np.isfinite(v)):
                        e.append(v[0]); lo.append(v[1]); hi.append(v[2])
            out["pooled"][f"replies:{kind}:{key}(log)"] = L.dl_pool(e, lo, hi)
    for key in ("D", "d_post", "d_pre"):
        for lab in ("forced_bge", "forced_gte", "voluntary_bge"):
            e, lo, hi = [], [], []
            for per, r in results.items():
                c = r["pull"].get(lab, {}).get(key)
                if c and np.all(np.isfinite(c)):
                    e.append(c[0]); lo.append(c[1]); hi.append(c[2])
            out["pooled"][f"pull:{lab}:{key}"] = L.dl_pool(e, lo, hi)
    e, lo, hi = [], [], []
    for per, r in results.items():
        c = r["loops"].get("OR_forced_vs_pseudo")
        if c and all(np.isfinite(c)) and c[1] > 0:
            e.append(np.log(c[0])); lo.append(np.log(c[1])); hi.append(np.log(c[2]))
    out["pooled"]["loops:log_OR_forced_vs_pseudo"] = L.dl_pool(e, lo, hi)
    order = [p for p in PERIODS if p in results]
    th = [results[p]["stats"]["forced"]["contrasts"]["post5_vs_far"]["Theta_c"][0] for p in order]
    nr = [results[p]["notes_read_share"] for p in order]
    om = [results[p]["stats"]["forced"]["contrasts"]["post10_vs_far"]["Omega"][0] for p in order]
    ix = list(range(len(order)))
    out["trend"] = {"periods": order, "Theta": th, "notes_read_share": nr, "Omega": om,
                    "rho_Theta_time": list(map(float, ss.spearmanr(ix, th))) if len(ix) > 3 else None,
                    "rho_notes_time": list(map(float, ss.spearmanr(ix, nr))) if len(ix) > 3 else None,
                    "rho_Omega_time": list(map(float, ss.spearmanr(ix, om))) if len(ix) > 3 else None}
    for per, r in results.items():
        f, v = r["stats"].get("forced", {}), r["stats"].get("voluntary", {})
        out["per_period"][per] = {
            "Theta_F": f.get("contrasts", {}).get("post5_vs_far", {}).get("Theta"),
            "Theta_V": v.get("contrasts", {}).get("post5_vs_far", {}).get("Theta"),
            "Thetac_F": f.get("contrasts", {}).get("post5_vs_far", {}).get("Theta_c"),
            "Thetac_V": v.get("contrasts", {}).get("post5_vs_far", {}).get("Theta_c"),
            "Omega_F": f.get("contrasts", {}).get("post10_vs_far", {}).get("Omega"),
            "Omega_V": v.get("contrasts", {}).get("post10_vs_far", {}).get("Omega"),
            "pre_W_F": f.get("contrasts", {}).get("near_vs_far", {}).get("Omega"),
            "pre_W_V": v.get("contrasts", {}).get("near_vs_far", {}).get("Omega"),
            "pre_W_P": r["stats"].get("pseudo31", {}).get("contrasts", {}).get("near_vs_far", {}).get("Omega"),
            "class_F": f.get("class"), "class_V": v.get("class"), "class_P31": r["stats"].get("pseudo31", {}).get("class"),
            "class_P21": r["stats"].get("pseudo21", {}).get("class")}
    return j(out)


def estimates_rows(results: dict, ne: dict) -> pl.DataFrame:
    """Rows in the shared per_period_estimates schema (written to H44's own folder; the coordinator merges them)."""
    import datetime as dt
    rows = []
    now = dt.datetime.now(dt.timezone.utc)
    for per, r in results.items():
        g = int(per[1:])
        for kind in ("forced", "voluntary", "pseudo31"):
            st = r["stats"].get(kind)
            if not st:
                continue
            for tag, stat in (("post5_vs_far", "Theta"), ("post5_vs_far", "Theta_c"), ("post10_vs_far", "Omega"),
                              ("post5_vs_far", "d_sigma"), ("post5_vs_far", "dR"), ("post5_vs_far", "d_H")):
                c = st["contrasts"].get(tag, {}).get(stat)
                if c:
                    rows.append({"hypothesis": "H44", "period_unit": str(g), "goal_no": g, "statistic": f"{stat}_{tag}",
                                 "channel": kind, "estimate": c[0], "ci_lo": c[1], "ci_hi": c[2],
                                 "n": float(st["n_events"]), "method": "reset event study, ratio of sums",
                                 "null": "pseudo-erasure (pos 31) and far-pre reference", "role": r["role"],
                                 "holdout": False, "regime": "III", "built_at": now, "git_commit": C.git_commit(),
                                 "ci_level": 0.95, "ci_kind": "agent-day cluster bootstrap", "se": None,
                                 "n_kind": "events", "unit_local": None, "first_day": None, "last_day": None,
                                 "confirmatory": False, "post_hoc": stat in ("Theta_c",), "status": "exploratory",
                                 "source": f"data/processed/H44-erasure-reacquisition-thrash/{per}/results.json",
                                 "source_mtime": None, "notes": "Theta_c added by Amendment A2 (synthetic)"})
    return pl.DataFrame(rows)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--periods", default=",".join(PERIODS))
    ap.add_argument("--B", type=int, default=1000)
    a = ap.parse_args()
    calls = pl.read_parquet(C.OUT / "calls.parquet")
    ev = pl.read_parquet(C.OUT / "events.parquet")
    v3 = pl.read_parquet(C.OUT / "v3_windows.parquet")
    rp = pl.read_parquet(C.OUT / "reply_pools.parquet")
    pp = pl.read_parquet(C.OUT / "pull_pairs.parquet")
    for df, nm in ((calls, "calls"), (ev, "events"), (v3, "v3"), (rp, "replies"), (pp, "pull")):
        C.refuse_holdout(df["pt_date"].unique().to_list(), nm)
    results = {}
    for per in a.periods.split(","):
        r = run_period(per, calls, ev, v3, rp, pp, a.B)
        (C.OUT / per).mkdir(parents=True, exist_ok=True)
        (C.OUT / per / "results.json").write_text(json.dumps(r, indent=1))
        results[per] = r
    if len(results) == len(PERIODS):
        ne = ne41(results)
        (C.OUT / "NE41").mkdir(exist_ok=True)
        (C.OUT / "NE41" / "results.json").write_text(json.dumps(ne, indent=1))
        estimates_rows(results, ne).write_parquet(C.OUT / "per_period_estimates_H44.parquet")
        summ = {p: {"verdict": r.get("verdict"), "flags": r.get("verdict_flags"), "role": r["role"],
                    "n_forced": r["events"].get("forced")} for p, r in results.items()}
        (C.OUT / "summary.json").write_text(json.dumps(summ, indent=1))
    C.log("done")


if __name__ == "__main__":
    main()
