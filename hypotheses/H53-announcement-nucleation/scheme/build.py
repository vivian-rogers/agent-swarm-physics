"""H53 scheme: seeds (first chat link to a project per goal period), their recipients' read-out timing (DQ1 context
ledger), commitment, activity, and every agent's adoption times (project label W=15, action-only, mention, work commit).

Writes data/processed/H53-announcement-nucleation/:
  projects.parquet    project code -> canonical artifact name (data folder only)
  adoptions.parquet   goal_no, agent, proj, t/a per adoption variant (label, action, mention, commit)
  seeds.parquet       one row per seed (non-holdout days), covariates
  recipients.parquet  one row per seed x roster agent present on the seed day (in-room and other-room)
  calls_cache.parquet per-call agent, t_call, active time, talk, receiving flag (non-holdout), for synthetic/analysis
Holdout days are excluded (holdout_mask); calls on holdout days count as unobserved. --allow-holdout is for confirm.py.

Usage: uv run python hypotheses/H53-announcement-nucleation/scheme/build.py [--allow-holdout] [--goals 26,31]
"""
from __future__ import annotations

import argparse
import math
import time

import numpy as np
import polars as pl

from h53lib import (FU_S, H_S, LINK_HOW, LOOKBACK_S, OUT, SH, SHIFTS_MIN, STRICT_HOW, W15, add_active, add_pt_date,
                    load_cal, on_roster, project_map, provenance, room_at, room_lookup, roster)


def log(*a):
    print(f"[{time.strftime('%H:%M:%S')}]", *a, flush=True)


def build(allow_holdout: bool = False, goals: list[int] | None = None, out=OUT):
    t0 = time.time()
    out.mkdir(parents=True, exist_ok=True)
    cal = load_cal()
    okday = cal if allow_holdout else cal.filter(~pl.col("ho"))
    okdays = set(okday["pt_date"].to_list())
    pm = project_map()

    # ---------------------------------------------------------------- strict agent mentions (all days, used for history)
    am = pl.read_parquet(SH / "artifact_mentions.parquet",
                         columns=["artifact", "t", "agent", "speaker_kind", "source", "how", "room", "message_id", "ref_index"])
    am = am.join(pm, on="artifact", how="inner")
    projects = sorted(am["project"].unique().to_list())
    pcode = {p: i for i, p in enumerate(projects)}
    pl.DataFrame({"proj": np.arange(len(projects), dtype=np.int32), "project": projects}).write_parquet(out / "projects.parquet")
    am = am.with_columns(pl.col("project").replace_strict(pcode, return_dtype=pl.Int32).alias("proj"))
    strict = am.filter((pl.col("speaker_kind").cast(pl.String) == "agent") & pl.col("agent").is_not_null()
                       & pl.col("how").cast(pl.String).is_in(STRICT_HOW))
    strict = strict.with_columns(pl.coalesce(pl.col("message_id"), pl.col("ref_index").cast(pl.String)).alias("ref"))
    strict = strict.unique(subset=["agent", "source", "ref", "proj"], keep="first")
    strict = add_active(strict, cal, keep_goal=True).rename({"a_goal": "goal_no", "a_pt_date": "pt_date", "a_ho": "ho"})
    strict = strict.filter(pl.col("goal_no").is_not_null())
    log("strict mentions", strict.height)

    # ---------------------------------------------------------------- adoption times per (goal, agent, project)
    cw15 = cal.select("pt_date", "win_start")
    def first_label(src: str) -> pl.DataFrame:
        ps = pl.read_parquet(SH / "project_states.parquet").filter((pl.col("w_min") == 15) & (pl.col("sources").cast(pl.String) == src))
        ps = ps.with_columns(pl.col("project").cast(pl.String).replace_strict(pcode, default=None, return_dtype=pl.Int32).alias("proj"))
        ps = ps.filter(pl.col("proj").is_not_null())
        if not allow_holdout:
            ps = ps.filter(~pl.col("holdout"))
        fw = ps.sort("pt_date", "win").group_by("goal_no", "agent", "proj", maintain_order=True).agg(pl.col("pt_date").first(), pl.col("win").first())
        m = strict if src == "all" else strict.filter(pl.col("source").cast(pl.String) == "action")
        m = m.join(cw15, on="pt_date").with_columns(((pl.col("t") - pl.col("win_start")).dt.total_seconds() // W15).cast(pl.Int16).alias("win"))
        j = fw.join(m.select("goal_no", "agent", "proj", "pt_date", "win", "t", "a"), on=["goal_no", "agent", "proj", "pt_date", "win"], how="left")
        j = j.group_by("goal_no", "agent", "proj").agg(pl.col("t").min(), pl.col("a").min())
        return j
    lab = first_label("all").rename({"t": "t_label", "a": "a_label"})
    act = first_label("action").rename({"t": "t_action", "a": "a_action"})
    s_ok = strict if allow_holdout else strict.filter(~pl.col("ho"))
    men = s_ok.group_by("goal_no", "agent", "proj").agg(pl.col("t").min().alias("t_mention"), pl.col("a").min().alias("a_mention"))
    wc = pl.read_parquet(SH / "work_commits.parquet", columns=["repo", "t", "author_agent", "author_kind", "canonical", "imported", "automated"])
    wc = wc.filter(pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind").cast(pl.String) == "agent") & ~pl.col("automated")
                   & pl.col("author_agent").is_not_null())
    wc = wc.with_columns(pl.col("repo").cast(pl.String).replace_strict(pcode, default=None, return_dtype=pl.Int32).alias("proj")).filter(pl.col("proj").is_not_null())
    wc = add_active(wc, cal, keep_goal=True).rename({"a_goal": "goal_no", "a_ho": "ho"}).filter(pl.col("goal_no").is_not_null())
    if not allow_holdout:
        wc = wc.filter(~pl.col("ho"))
    com = wc.group_by("goal_no", pl.col("author_agent").alias("agent"), "proj").agg(pl.col("t").min().alias("t_commit"), pl.col("a").min().alias("a_commit"))
    keys = ["goal_no", "agent", "proj"]
    adopt = (lab.join(act, on=keys, how="full", coalesce=True).join(men, on=keys, how="full", coalesce=True)
             .join(com, on=keys, how="full", coalesce=True))
    adopt = adopt.with_columns(pl.col("goal_no").cast(pl.Int8), pl.col("agent").cast(pl.Int8), pl.col("proj").cast(pl.Int32))
    adopt.write_parquet(out / "adoptions.parquet", compression="zstd")
    log("adoptions", adopt.height)

    # ---------------------------------------------------------------- calls (ledger timing layer)
    cwin = pl.read_parquet(SH / "call_windows.parquet", columns=["turn_id", "agent", "goal_no", "pt_date", "holdout", "t_call", "talk", "ctx_mode", "gap_kind"])
    cwin = add_active(cwin, cal, col="t_call")
    cwin = cwin.with_columns((pl.col("ctx_mode").cast(pl.String) != "summary").alias("recv"))
    if not allow_holdout:
        cwin = cwin.with_columns(pl.col("holdout").alias("ho_call"))
    else:
        cwin = cwin.with_columns(pl.lit(False).alias("ho_call"))
    cwin = cwin.sort("agent", "t_call")
    # call cycle per (goal, agent): median start-to-start interval, non-holdout, (0, 3600) s
    cyc = (cwin.filter(~pl.col("holdout") | pl.lit(allow_holdout))
           .with_columns(pl.col("t_call").diff().over("agent", "goal_no").dt.total_microseconds().truediv(1e6).alias("dt"))
           .filter((pl.col("dt") > 0) & (pl.col("dt") < 3600)).group_by("goal_no", "agent").agg(pl.col("dt").median().alias("cyc_s")))
    cc = cwin.select("agent", "t_call", "a", "talk", "recv", "ho_call", "goal_no")
    cc.write_parquet(out / "calls_cache.parquet", compression="zstd")
    calls = {}
    for (a,), sub in cc.group_by(["agent"], maintain_order=True):
        calls[int(a)] = dict(t=sub["t_call"].dt.epoch("us").to_numpy(), a=sub["a"].fill_null(np.nan).to_numpy(),
                             talk=sub["talk"].to_numpy(), recv=sub["recv"].to_numpy(), ho=sub["ho_call"].to_numpy())
    log("calls", cc.height)

    # ---------------------------------------------------------------- seeds: first chat link per (goal, project)
    links = am.filter((pl.col("source").cast(pl.String) == "chat") & pl.col("how").cast(pl.String).is_in(LINK_HOW)
                      & pl.col("message_id").is_not_null())
    links = add_active(links, cal, keep_goal=True).rename({"a_goal": "goal_no", "a_pt_date": "pt_date", "a_ho": "ho"}).filter(pl.col("goal_no").is_not_null())
    links = links.unique(subset=["message_id", "proj"], keep="first").sort("t")
    seeds = links.group_by("goal_no", "proj", maintain_order=True).first()
    if goals:
        seeds = seeds.filter(pl.col("goal_no").is_in(goals))
    n_all = seeds.height
    seeds = seeds.filter(pl.col("pt_date").is_in(list(okdays)))
    log(f"seeds {seeds.height} (of {n_all}; holdout-day seeds dropped)")
    # first-seen of the project in the dataset (carried over from an earlier period?)
    art = pl.read_parquet(SH / "artifacts.parquet", columns=["artifact", "first_t"]).join(pm, on="artifact")
    fs = art.group_by("project").agg(pl.col("first_t").min().alias("first_seen")).with_columns(
        pl.col("project").replace_strict(pcode, default=None, return_dtype=pl.Int32).alias("proj")).drop("project")
    gstart = cal.group_by("goal_no").agg(pl.col("win_start").min().alias("g_start"))
    seeds = seeds.join(fs, on="proj", how="left").join(gstart, on="goal_no", how="left")
    seeds = seeds.with_columns((pl.col("first_seen") < pl.col("g_start")).fill_null(False).alias("carried"))
    # period non-holdout active end (for censoring)
    gend = okday.group_by("goal_no").agg((pl.col("active_offset_s") + pl.col("window_s")).max().alias("a_gend"))
    seeds = seeds.join(gend, on="goal_no", how="left")
    # units
    pu = pl.read_parquet(SH / "period_units.parquet", columns=["unit_id", "goal_no", "start", "end", "n_agents"])
    seeds = seeds.join(pu, on="goal_no", how="left").filter(
        (pl.col("t") >= pl.col("start")) & (pl.col("t") < pl.col("end")) | pl.col("unit_id").is_null())
    seeds = seeds.sort("t").unique(subset=["goal_no", "proj"], keep="first", maintain_order=True)
    # day position
    seeds = seeds.join(cal.select("pt_date", "win_start", "window_s", "regime"), on="pt_date", how="left")
    seeds = seeds.with_columns(((pl.col("t") - pl.col("win_start")).dt.total_seconds() / pl.col("window_s")).clip(0, 1).alias("tod"))
    # human messages / kickoffs in the poster's room in the 30 active min before
    kc = pl.read_parquet(SH / "kicks_classified.parquet", columns=["t", "kind", "room"]).filter(
        pl.col("kind").cast(pl.String).is_in(["human_message", "goal_kickoff"]))
    kc = add_active(kc, cal)
    kt = kc["a"].fill_null(-1).to_numpy(); kr = kc["room"].fill_null(-1).to_numpy()
    kick_near = []
    for a_s, rm in zip(seeds["a"].to_list(), seeds["room"].fill_null(-1).to_list()):
        sel = (kt >= a_s - LOOKBACK_S) & (kt < a_s) & ((kr == rm) | (kr == -1))
        kick_near.append(bool(sel.any()))
    seeds = seeds.with_columns(pl.Series("kick_near", kick_near))
    seeds = seeds.with_columns(pl.when(pl.col("speaker_kind").cast(pl.String) == "human").then(pl.lit(-1)).otherwise(pl.col("agent")).cast(pl.Int8).alias("poster"),
                               (pl.col("speaker_kind").cast(pl.String) == "human").alias("human"),
                               (pl.col("a") + H_S > pl.col("a_gend")).alias("censored"))
    seeds = seeds.with_row_index("sid").with_columns(pl.col("sid").cast(pl.Int32))

    # ---------------------------------------------------------------- poster status (DQ2 reply graph, non-holdout days)
    rg = pl.read_parquet(SH / "reply_graph.parquet").filter((pl.col("scale").cast(pl.String) == "day") & (pl.col("replier") >= 0) & (pl.col("target") >= 0))
    if not allow_holdout:
        rg = rg.filter(~pl.col("holdout"))
    rgp = rg.group_by("goal_no", "replier", "target").agg(pl.col("reply_soft").sum())
    instr = rgp.group_by("goal_no", "target").agg(pl.col("reply_soft").sum().alias("instr"))
    pr_rows = []
    for (g,), d in rgp.group_by(["goal_no"]):
        nodes = sorted(set(d["replier"].to_list()) | set(d["target"].to_list()))
        ix = {n: i for i, n in enumerate(nodes)}
        n = len(nodes)
        W = np.zeros((n, n))
        for r, tg, w in zip(d["replier"].to_list(), d["target"].to_list(), d["reply_soft"].to_list()):
            if r != tg:
                W[ix[r], ix[tg]] += w
        out_s = W.sum(1, keepdims=True)
        P = np.where(out_s > 0, W / np.where(out_s > 0, out_s, 1), 1.0 / n)
        v = np.full(n, 1.0 / n)
        for _ in range(200):
            v = 0.15 / n + 0.85 * v @ P
        for nd in nodes:
            pr_rows.append((int(g), int(nd), float(v[ix[nd]] * n)))
    prdf = pl.DataFrame(pr_rows, schema={"goal_no": pl.Int8, "target": pl.Int16, "pagerank": pl.Float64}, orient="row")
    stat = instr.join(prdf, on=["goal_no", "target"], how="full", coalesce=True).rename({"target": "poster"}).with_columns(
        pl.col("poster").cast(pl.Int8), pl.col("goal_no").cast(pl.Int8))
    seeds = seeds.join(stat, on=["goal_no", "poster"], how="left")

    # ---------------------------------------------------------------- mentions per agent (for commitment) and labels (share)
    ment = {}
    for (a,), sub in strict.select("agent", "a", "proj").drop_nulls("a").sort("agent", "a").group_by(["agent"], maintain_order=True):
        ment[int(a)] = (sub["a"].to_numpy(), sub["proj"].to_numpy())
    ps30 = pl.read_parquet(SH / "project_states.parquet").filter((pl.col("w_min") == 30) & (pl.col("sources").cast(pl.String) == "all"))
    ps15 = pl.read_parquet(SH / "project_states.parquet").filter((pl.col("w_min") == 15) & (pl.col("sources").cast(pl.String) == "all"))
    if not allow_holdout:
        ps30 = ps30.filter(~pl.col("holdout")); ps15 = ps15.filter(~pl.col("holdout"))
    def wtimes(ps, W):
        ps = ps.join(cal.select("pt_date", "win_start"), on="pt_date").with_columns(
            (pl.col("win_start") + pl.duration(seconds=pl.col("win").cast(pl.Int64) * W)).alias("w0"))
        return ps.with_columns(pl.col("project").cast(pl.String).replace_strict(pcode, default=None, return_dtype=pl.Int32).alias("proj"))
    ps30 = wtimes(ps30, 1800); ps15 = wtimes(ps15, W15)
    k30 = ps30.group_by("goal_no", "w0", "proj").agg(pl.col("agent").n_unique().alias("k"))

    # ---------------------------------------------------------------- ledger items for all link messages
    link_ids = links["message_id"].unique().to_list()
    items = pl.scan_parquet(SH / "context_ledger_items.parquet").filter(pl.col("message_id").is_in(link_ids)).select(
        "turn_id", "message_id", "age_s", "rank", "uncertain").collect()
    items = items.join(cwin.select("turn_id", "agent", "t_call", "a", "ho_call", "gap_kind"), on="turn_id", how="inner")
    turns_k = pl.scan_parquet(SH / "context_ledger_turns.parquet").select("turn_id", "k_new").collect()
    items = items.join(turns_k, on="turn_id", how="left")
    # earliest read of any link to X per (goal, agent, proj) (for F3), non-holdout calls only
    lk = links.select("message_id", "proj", "goal_no").unique()
    it_x = items.filter(~pl.col("ho_call")).join(lk, on="message_id", how="inner")
    first_link_read = it_x.group_by("goal_no", "agent", "proj").agg(pl.col("t_call").min().alias("t_flread"))

    # ---------------------------------------------------------------- recipients
    tl = room_lookup()
    ro = roster()
    adopt_d = {(r[0], r[1], r[2]): r for r in adopt.select("goal_no", "agent", "proj", "t_label", "a_label", "t_action", "a_action",
                                                                  "t_mention", "a_mention", "t_commit", "a_commit").iter_rows()}
    flr = {(r[0], r[1], r[2]): r[3] for r in first_link_read.iter_rows()}
    cyc_d = {(r[0], r[1]): r[2] for r in cyc.iter_rows()}
    seed_items = items.filter(pl.col("message_id").is_in(seeds["message_id"].to_list()))
    sit = {}
    for r in seed_items.iter_rows(named=True):
        sit.setdefault(r["message_id"], {})[int(r["agent"])] = r
    rows = []
    shares, herd_max, n_room_l, n_lab_l = [], [], [], []
    for s in seeds.iter_rows(named=True):
        g, X, ts_us = s["goal_no"], s["proj"], int(s["t"].timestamp() * 1e6)
        a_s = s["a"]
        present = on_roster(ro, s["pt_date"])
        if s["agent"] is not None and not s["human"] and s["agent"] not in present:
            present.append(int(s["agent"]))
        cand = sorted(set(present) | set(sit.get(s["message_id"], {}).keys()))
        roomv = {a: int(room_at(tl, a, np.array([ts_us]))[0]) for a in cand}
        n_room = sum(1 for a in cand if roomv[a] == s["room"] and a != s["poster"])
        n_room_l.append(n_room)
        # current share of X among in-room agents labelled in the last 30 min (W15 windows starting in [t-30m, t))
        w = ps15.filter((pl.col("goal_no") == g) & (pl.col("w0") >= s["t"] - pl.duration(minutes=30)) & (pl.col("w0") < s["t"]))
        w = w.filter(pl.col("agent").is_in([a for a in cand if roomv[a] == s["room"]]))
        last = w.sort("w0").group_by("agent").agg(pl.col("proj").last())
        n_lab = last.height
        shares.append(float((last["proj"] == X).sum() / n_lab) if n_lab else 0.0)
        n_lab_l.append(n_lab)
        kk = k30.filter((pl.col("goal_no") == g) & (pl.col("proj") == X) & (pl.col("w0") + pl.duration(minutes=15) > s["t"]))
        herd_max.append(int(kk["k"].max()) if kk.height else 0)
        for a in cand:
            if a == s["poster"]:
                continue
            it = sit.get(s["message_id"], {}).get(a)
            ad = adopt_d.get((g, a, X))
            c = calls.get(a)
            r = dict(sid=s["sid"], goal_no=g, agent=a, in_room=roomv[a] == s["room"], room=roomv[a], cyc_s=cyc_d.get((g, a)))
            if it is not None and not it["ho_call"]:
                r.update(t_read=it["t_call"], a_read=it["a"], age_s=float(it["age_s"]), k_new=it["k_new"], rank=it["rank"],
                         gap_kind=str(it["gap_kind"]), uncertain=bool(it["uncertain"]))
            else:
                r.update(t_read=None, a_read=None, age_s=None, k_new=None, rank=None, gap_kind=None, uncertain=None)
            for v in ("label", "action", "mention", "commit"):
                ix = {"label": (3, 4), "action": (5, 6), "mention": (7, 8), "commit": (9, 10)}[v]
                r[f"t_{v}"] = ad[ix[0]] if ad else None
                r[f"a_{v}"] = ad[ix[1]] if ad else None
            r["t_flread"] = flr.get((g, a, X))
            # commitment: strict mentions of other projects in [a_s - 30 min, a_s)
            if a in ment:
                ma, mp = ment[a]
                lo, hi = np.searchsorted(ma, a_s - LOOKBACK_S, "left"), np.searchsorted(ma, a_s, "left")
                r["n_other30"] = int((mp[lo:hi] != X).sum())
            else:
                r["n_other30"] = 0
            # activity before the seed, and calls from read-out to adoption, follow-up call counts
            if c is not None:
                ca = c["a"]
                lo, hi = np.searchsorted(ca, a_s - LOOKBACK_S, "left"), np.searchsorted(ca, a_s, "left")
                r["calls30"] = int(hi - lo)
                r["talk30"] = bool(c["talk"][lo:hi].any()) if hi > lo else False
                if r["a_read"] is not None:
                    i0 = np.searchsorted(c["t"], int(r["t_read"].timestamp() * 1e6), "left")
                    i1 = np.searchsorted(ca, r["a_read"] + FU_S, "right")
                    r["n_fu"] = int(max(i1 - i0, 0))
                    if r["t_label"] is not None:
                        ia = np.searchsorted(c["t"], int(r["t_label"].timestamp() * 1e6), "right")
                        r["k_adopt"] = int(ia - i0)  # 1 = the reading call itself produced the mention (or earlier: <= 0)
                    else:
                        r["k_adopt"] = None
                else:
                    r["n_fu"], r["k_adopt"] = None, None
                # shifted pseudo-seed read-out ages (active time; receiving calls on non-holdout days)
                for dmin in (0,) + SHIFTS_MIN:
                    a2 = a_s + 60 * dmin
                    j = np.searchsorted(ca, a2, "right")
                    while j < len(ca) and (not c["recv"][j] or c["ho"][j]):
                        j += 1
                    r[f"age_sh{dmin:+d}"] = float(ca[j] - a2) if j < len(ca) and not np.isnan(ca[j]) else None
            else:
                r.update(calls30=0, talk30=False, n_fu=None, k_adopt=None)
                for dmin in (0,) + SHIFTS_MIN:
                    r[f"age_sh{dmin:+d}"] = None
            rows.append(r)
    seeds = seeds.with_columns(pl.Series("share", shares), pl.Series("herd_kmax", herd_max), pl.Series("n_room", n_room_l),
                               pl.Series("n_lab_room", n_lab_l))
    rec = pl.DataFrame(rows, infer_schema_length=None)
    rec = rec.with_columns(pl.col("sid").cast(pl.Int32), pl.col("goal_no").cast(pl.Int8), pl.col("agent").cast(pl.Int8), pl.col("room").cast(pl.Int8))
    keep = ["sid", "goal_no", "unit_id", "proj", "message_id", "t", "a", "pt_date", "regime", "room", "poster", "human", "speaker_kind",
            "carried", "censored", "kick_near", "tod", "instr", "pagerank", "share", "herd_kmax", "n_room", "n_lab_room", "first_seen", "a_gend"]
    seeds = seeds.select([c for c in keep if c in seeds.columns]).rename({"t": "t_seed", "a": "a_seed"})
    seeds.write_parquet(out / "seeds.parquet", compression="zstd")
    rec.write_parquet(out / "recipients.parquet", compression="zstd")
    log(f"seeds {seeds.height}, recipients {rec.height}, {time.time() - t0:.0f}s")
    provenance("scheme/build.py" + (" --allow-holdout" if allow_holdout else ""),
               ["artifact_mentions", "artifacts", "project_states", "call_windows", "context_ledger_items", "context_ledger_turns",
                "rooms_timeline", "roster", "calendar", "reply_graph", "work_commits", "kicks_classified", "period_units"],
               dict(H_S=H_S, FU_S=FU_S, LOOKBACK_S=LOOKBACK_S, W15=W15, shifts_min=list(SHIFTS_MIN), allow_holdout=allow_holdout,
                    goals=goals), "hypotheses/H53-announcement-nucleation/scheme/build.py", out=out)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--allow-holdout", action="store_true")
    ap.add_argument("--goals", default="")
    ap.add_argument("--out", default="")
    a = ap.parse_args()
    from pathlib import Path
    build(a.allow_holdout, [int(x) for x in a.goals.split(",") if x] or None, Path(a.out) if a.out else OUT)
