"""H15 scheme: agent-day viability candidates, exposure share, scramble catalog, consolidation segments.

Builds data/processed/H15-semantic-information-scrambles/ from the shared tables (no raw text is read):
  agent_day.parquet        one row per agent x non-holdout active day (viability candidates, exposure, memory)
  scramble_catalog.parquet one row per scramble event (ML, MG, MR, MN, CC); detection uses scramble variables only
  consolidations.parquet   regime III CONSOLIDATE events with turn-level outcomes in the 10 turns before/after
  consolidation_profile.parquet  mean write/error rate by turn offset (-20..+20) per unit x kind

Run:  uv run python hypotheses/H15-semantic-information-scrambles/scheme/build.py
Holdout days are dropped before any detection (refuse_holdout asserts it).
"""
from __future__ import annotations

import time

from h15common import (CLAUDE_CODE_AGENT, EMB, OUT, SH, WRITE_VERBS, calendar_nonholdout, holdout_days,
                       pt_date_expr, refuse_holdout, unit_expr, write_provenance)

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

T0 = time.time()


def log(msg):
    print(f"[{time.time() - T0:6.1f}s] {msg}", flush=True)


def build(cal_in: pl.DataFrame, hold: set, out, guard: bool = True):
    """Build all H15 tables for the days in cal_in (a calendar_nonholdout()-shaped frame).

    The exploratory build passes the non-holdout calendar and guard=True (refuse_holdout asserts). Only
    analysis/confirm_ne30.py, behind its confirmation flags, calls it with holdout days and guard=False."""

    # ----------------------------------------------------------------------------- base
    cal = cal_in
    DAYS = set(cal["pt_date"].to_list())
    calj = cal.select("pt_date", "goal_no", "regime", "unit", "win_start", "win_end", "win_h")
    roster = pl.read_parquet(SH / "roster.parquet")

    ab = (pl.scan_parquet(SH / "activity_bins.parquet")
          .filter(pl.col("pt_date").is_in(list(DAYS)) & (pl.col("agent") != CLAUDE_CODE_AGENT))
          .group_by("pt_date", "agent")
          .agg(pl.len().alias("n_min"), (pl.col("state") >= 3).mean().alias("V_eng"),
               (pl.col("state") == 4).mean().alias("talk_frac"), (pl.col("state") == 2).mean().alias("idle_frac"))
          .collect())
    base = ab.join(calj, on="pt_date", how="left")
    log(f"base agent-days {base.height}")

    # ----------------------------------------------------------------------------- V_out (write turns per window hour)
    am = (pl.scan_parquet(SH / "artifact_mentions.parquet")
          .filter((pl.col("source") == "action") & pl.col("verb").cast(pl.Utf8).is_in(WRITE_VERBS))
          .select("agent", "t").unique().collect())
    writes = am.with_columns(pt_date_expr("t").alias("pt_date")).filter(pl.col("pt_date").is_in(list(DAYS)))
    wday = writes.group_by("pt_date", "agent").agg(pl.len().alias("n_writes"))

    # ----------------------------------------------------------------------------- V_rel and action mix (V_ord)
    act = (pl.scan_parquet(SH / "actions.parquet").select("t", "agent", "action", "error")
           .filter(pl.col("action") != "pause")  # pause turns mirror PAUSE events (H09)
           .with_columns(pt_date_expr("t").alias("pt_date"))
           .filter(pl.col("pt_date").is_in(list(DAYS))).collect())
    rel = act.group_by("pt_date", "agent").agg(pl.len().alias("n_turns"), pl.col("error").mean().alias("err_frac"))
    ev = (pl.scan_parquet(SH / "events_core.parquet")
          .filter((pl.col("actor_kind") == "agent") & pl.col("pt_date").is_in(list(DAYS)))
          .select("event_index", "t", "pt_date", "agent", "action_type").collect())
    mix = pl.concat([act.select("pt_date", "agent", pl.col("action").cast(pl.Utf8).alias("cat")),
                     ev.select("pt_date", "agent", ("EV_" + pl.col("action_type").cast(pl.Utf8)).alias("cat"))])
    cnt = mix.group_by("pt_date", "agent", "cat").agg(pl.len().alias("c"))
    ent = (cnt.with_columns(pl.col("c").sum().over("pt_date", "agent").alias("n"))
           .with_columns((pl.col("c") / pl.col("n")).alias("p"))
           .group_by("pt_date", "agent")
           .agg(pl.col("n").first().alias("n_actions"), pl.len().alias("K"),
                (-(pl.col("p") * pl.col("p").log()).sum()).alias("H_plug"))
           .with_columns((-(pl.col("H_plug") + (pl.col("K") - 1) / (2 * pl.col("n_actions")))).alias("V_ord")))
    log("actions done")

    # ----------------------------------------------------------------------------- V_coh (plan coherence)
    it = pl.read_parquet(SH / "intentions.parquet")
    idx = pl.read_parquet(EMB / "intentions_index.parquet").with_row_index("row")
    emb = np.load(EMB / "intentions_bge_small.npy", mmap_mode="r")
    it = (it.join(idx, on="event_index", how="inner").with_columns(pt_date_expr("t").alias("pt_date"))
          .filter(pl.col("pt_date").is_in(list(DAYS)) & (pl.col("agent") != CLAUDE_CODE_AGENT)).sort("agent", "t"))
    rows = it["row"].to_numpy()
    E = np.asarray(emb[np.sort(rows)], dtype=np.float32)
    pos = {r: i for i, r in enumerate(np.sort(rows))}
    E_it = E[[pos[r] for r in rows]]
    E_it /= np.linalg.norm(E_it, axis=1, keepdims=True) + 1e-9
    same = (it["agent"].to_numpy()[1:] == it["agent"].to_numpy()[:-1]) & (it["pt_date"].to_numpy()[1:] == it["pt_date"].to_numpy()[:-1])
    cos = np.einsum("ij,ij->i", E_it[1:], E_it[:-1])
    pairs = pl.DataFrame({"agent": it["agent"].to_numpy()[1:][same], "pt_date": it["pt_date"].to_numpy()[1:][same],
                          "cos": cos[same]})
    coh = (pairs.group_by("pt_date", "agent").agg(pl.len().alias("n_int_pairs"), pl.col("cos").mean().alias("V_coh"))
           .with_columns(pl.col("agent").cast(pl.Int8)))
    log("coherence done")

    # ----------------------------------------------------------------------------- exposure share s
    chat = (pl.read_parquet(SH / "chat_core.parquet").sort("t").with_row_index("msg")
            .select("msg", "pt_date", "speaker_kind", pl.col("agent").alias("speaker"), "room"))
    chat = chat.filter(pl.col("pt_date").is_in(list(DAYS)))
    ag_msgs = chat.filter(pl.col("speaker_kind") == "agent")
    tot = ag_msgs.group_by("pt_date").agg(pl.len().alias("n_agent_msgs"))
    own = ag_msgs.group_by("pt_date", "speaker").agg(pl.len().alias("n_own")).rename({"speaker": "agent"})
    expo = (pl.scan_parquet(SH / "exposure.parquet").select("msg", "agent").collect()
            .join(chat, on="msg", how="inner"))
    exp_ag = (expo.filter((pl.col("speaker_kind") == "agent") & (pl.col("speaker") != pl.col("agent")))
              .group_by("pt_date", "agent").agg(pl.len().alias("n_exposed_agent")))
    exp_all = expo.group_by("pt_date", "agent").agg(pl.len().alias("n_exposed_all"))
    log("exposure done")

    # modal room per agent-day (as-of the window midpoint) and the most populated room
    rt = pl.read_parquet(SH / "rooms_timeline.parquet").sort("agent", "t_start")
    mid = calj.select("pt_date", (pl.col("win_start") + (pl.col("win_end") - pl.col("win_start")) / 2).alias("t_mid"))
    room_day = (base.select("pt_date", "agent").join(mid, on="pt_date").sort("t_mid")
                .join_asof(rt.select("agent", "room", "t_start"), left_on="t_mid", right_on="t_start", by="agent",
                           strategy="backward").select("pt_date", "agent", "room"))
    main = (room_day.group_by("pt_date", "room").agg(pl.len().alias("n_in_room")).sort("n_in_room", descending=True)
            .group_by("pt_date").agg(pl.col("room").first().alias("main_room"), pl.col("n_in_room").first().alias("n_main")))
    room_day = room_day.join(main, on="pt_date").with_columns((pl.col("room") == pl.col("main_room")).alias("in_main_room"))

    # ----------------------------------------------------------------------------- memory per agent-day
    ms_all = pl.read_parquet(SH / "memory_stats.parquet").with_columns(pt_date_expr("t").alias("pt_date")).sort("agent", "t")
    mday = (ms_all.filter(pl.col("pt_date").is_in(list(DAYS)))
            .group_by("pt_date", "agent").agg(pl.len().alias("n_snap"), pl.col("n_chars").median().alias("mem_chars_med"),
                                              pl.col("jaccard_prev").mean().alias("mem_jacc_mean")))

    # ----------------------------------------------------------------------------- assemble agent_day
    ad = (base.join(wday, on=["pt_date", "agent"], how="left")
          .join(rel, on=["pt_date", "agent"], how="left")
          .join(ent.select("pt_date", "agent", "n_actions", "V_ord"), on=["pt_date", "agent"], how="left")
          .join(coh, on=["pt_date", "agent"], how="left")
          .join(tot, on="pt_date", how="left").join(own, on=["pt_date", "agent"], how="left")
          .join(exp_ag, on=["pt_date", "agent"], how="left").join(exp_all, on=["pt_date", "agent"], how="left")
          .join(room_day, on=["pt_date", "agent"], how="left")
          .join(mday, on=["pt_date", "agent"], how="left")
          .with_columns(pl.col("n_writes").fill_null(0), pl.col("n_own").fill_null(0),
                        pl.col("n_exposed_agent").fill_null(0), pl.col("n_exposed_all").fill_null(0))
          .with_columns((pl.col("n_writes") / pl.col("win_h")).alias("V_out"),
                        pl.when(pl.col("n_turns") >= 20).then(1 - pl.col("err_frac")).otherwise(None).alias("V_rel"),
                        pl.when(pl.col("n_actions") >= 20).then(pl.col("V_ord")).otherwise(None).alias("V_ord"),
                        pl.when(pl.col("n_int_pairs") >= 2).then(pl.col("V_coh")).otherwise(None).alias("V_coh"),
                        (pl.col("n_exposed_agent") / (pl.col("n_agent_msgs") - pl.col("n_own")).clip(1, None))
                        .alias("expo_share"),
                        (pl.col("n_exposed_all") / pl.col("win_h")).alias("inflow_per_h")))
    # tenure in calendar days and in active days (from roster join; first activity from the full calendar of activity)
    first_act = (pl.scan_parquet(SH / "activity_bins.parquet").filter(pl.col("state") >= 2)
                 .group_by("agent").agg(pl.col("pt_date").min().alias("first_active")).collect())
    ad = (ad.join(roster.select("agent", "name", "lab", "joined", "left"), on="agent", how="left")
          .join(first_act, on="agent", how="left")
          .with_columns(((pl.col("pt_date").str.to_date() - pl.col("joined").str.to_date()).dt.total_days()).alias("tenure_d"))
          .sort("agent", "pt_date"))
    ad = ad.select("pt_date", "agent", "name", "lab", "goal_no", "unit", "regime", "win_h", "n_min", "tenure_d",
                   "first_active", "V_out", "V_eng", "V_rel", "V_ord", "V_coh", "n_writes", "n_turns", "n_actions",
                   "n_int_pairs", "talk_frac", "idle_frac", "expo_share", "inflow_per_h", "n_exposed_agent",
                   "n_agent_msgs", "room", "main_room", "in_main_room", "n_main", "n_snap", "mem_chars_med",
                   "mem_jacc_mean")
    ad = ad.with_columns(pl.col("regime").cast(pl.Utf8), pl.col("V_out").cast(pl.Float32), pl.col("V_eng").cast(pl.Float32),
                         pl.col("V_rel").cast(pl.Float32), pl.col("V_ord").cast(pl.Float32), pl.col("V_coh").cast(pl.Float32),
                         pl.col("expo_share").cast(pl.Float32), pl.col("inflow_per_h").cast(pl.Float32))
    if guard:
        refuse_holdout(ad["pt_date"].unique().to_list(), "agent_day")
    out.mkdir(parents=True, exist_ok=True)
    ad.write_parquet(out / "agent_day.parquet", compression="zstd")
    log(f"agent_day {ad.height} rows")

    # ============================================================================= scramble catalog
    HOLD = hold
    cat_rows = []

    # ---- memory: ML / MG / MR (non-holdout snapshots only; SP from non-holdout compressed snapshots)
    ms = ms_all.with_columns(pl.col("pt_date").shift(1).over("agent").alias("prev_pt_date"),
                             pl.col("n_chars").shift(1).over("agent").alias("prev_chars_true"))
    ms = ms.filter(~pl.col("pt_date").is_in(list(HOLD)) & (pl.col("agent") != CLAUDE_CODE_AGENT))
    ms = ms.join(roster.select("agent", "joined"), on="agent").with_columns(
        ((pl.col("pt_date").str.to_date() - pl.col("joined").str.to_date()).dt.total_days()).alias("tenure_d"))
    out_ms = []
    for (a,), g in ms.group_by(["agent"], maintain_order=True):
        g = g.sort("t")
        n = g["n_chars"].to_numpy().astype(float)
        prev = np.r_[np.nan, n[:-1]]
        sp = np.full(len(n), np.nan)
        buf: list[float] = []
        for i in range(len(n)):
            if len(buf) >= 10:
                sp[i] = np.median(buf[-30:])
            if i > 0 and n[i] < prev[i]:
                buf.append(n[i])
        nxt = np.full(len(n), np.nan)
        for i in range(len(n) - 5):
            nxt[i] = np.median(n[i + 1:i + 6])
        out_ms.append(g.with_columns(pl.Series("SP", sp), pl.Series("next5med", nxt)))
    ms = pl.concat(out_ms).with_columns(pl.col("SP").fill_nan(None), pl.col("next5med").fill_nan(None))
    ok_prev = ~pl.col("prev_pt_date").is_in(list(HOLD))
    loss = ms.filter(ok_prev & pl.col("SP").is_not_null() & (pl.col("n_chars") < 0.5 * pl.col("SP"))
                     & (pl.col("jaccard_prev") < 0.3) & (pl.col("tenure_d") >= 3) & pl.col("next5med").is_not_null())
    loss = loss.with_columns((pl.col("next5med") < 0.7 * pl.col("SP")).alias("persist"))
    for kind, flt in (("ML", pl.col("persist")), ("MG", ~pl.col("persist"))):
        e = loss.filter(flt).sort("t").unique(["agent", "pt_date"], keep="first").sort("t")
        for r in e.iter_rows(named=True):
            cat_rows.append(dict(type=kind, agent=r["agent"], t=r["t"], pt_date=r["pt_date"],
                                 dose=float(1 - r["n_chars"] / r["SP"]), sp=float(r["SP"]), n_chars=int(r["n_chars"]),
                                 jaccard=float(r["jaccard_prev"]), lines_removed=r["lines_removed"],
                                 lines_kept=r["lines_kept"], run_len=None, s_pre=None, note=""))
    ml_days = {(r["agent"], r["pt_date"]) for r in cat_rows if r["type"] == "ML"}
    rw = ms.filter(ok_prev & (pl.col("jaccard_prev") < 0.05) & (pl.col("tenure_d") >= 3)
                   & ((pl.col("n_chars") / pl.col("prev_chars_true")).is_between(0.7, 1.4)))
    rw = rw.sort("t").unique(["agent", "pt_date"], keep="first").sort("t")
    for r in rw.iter_rows(named=True):
        d = r["pt_date"]
        near = any((r["agent"], x) in ml_days for x in
                   [(np.datetime64(d) + np.timedelta64(k, "D")).astype(str) for k in (-1, 0, 1)])
        if near:
            continue
        cat_rows.append(dict(type="MR", agent=r["agent"], t=r["t"], pt_date=d,
                             dose=float(1 - r["jaccard_prev"]), sp=float(r["SP"]) if r["SP"] else None,
                             n_chars=int(r["n_chars"]), jaccard=float(r["jaccard_prev"]), lines_removed=r["lines_removed"],
                             lines_kept=r["lines_kept"], run_len=None, s_pre=None, note="size kept"))
    log("memory events done")

    # ---- newcomers: MN (join and reference windows must be non-holdout)
    cal_all = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("n_agent_events") > 0).sort("pt_date")
    all_days = cal_all["pt_date"].to_list()
    for r in roster.filter(pl.col("agent") != CLAUDE_CODE_AGENT).iter_rows(named=True):
        act_days = sorted(ad.filter(pl.col("agent") == r["agent"])["pt_date"].to_list())
        # active-day sequence from the full calendar starting at the join date (dates only, no outcomes)
        seq = [d for d in all_days if d >= r["joined"] and (r["left"] is None or d < r["left"])]
        if len(seq) < 12:
            continue
        first3, ref = seq[:3], seq[5:12]
        if any(d in HOLD for d in first3):
            continue
        ref_ok = [d for d in ref if d not in HOLD and d in act_days]
        if len(ref_ok) < 3 or seq[0] not in act_days:
            continue
        cat_rows.append(dict(type="MN", agent=r["agent"], t=None, pt_date=seq[0], dose=1.0, sp=None, n_chars=None,
                             jaccard=None, lines_removed=None, lines_kept=None, run_len=None, s_pre=None,
                             note=f"ref days {len(ref_ok)}"))
    log("newcomers done")

    # ---- chat cut: CC from exposure share (sustained >= 2 active days, not in the main room)
    for (a,), g in ad.group_by(["agent"], maintain_order=True):
        g = g.sort("pt_date")
        s = g["expo_share"].to_numpy().astype(float)
        inmain = g["in_main_room"].fill_null(True).to_numpy()
        units = g["unit"].to_list()
        days = g["pt_date"].to_list()
        i = 5
        while i < len(s):
            pre = s[max(0, i - 5):i]
            pre = pre[np.isfinite(pre)]
            if len(pre) < 3 or np.median(pre) <= 0:
                i += 1
                continue
            spre = np.median(pre)
            j = i
            while j < len(s) and np.isfinite(s[j]) and s[j] < 0.3 * spre and not inmain[j]:
                j += 1
            if j - i >= 2:
                cat_rows.append(dict(type="CC", agent=a, t=None, pt_date=days[i], dose=float(1 - np.mean(s[i:j]) / spre),
                                     sp=None, n_chars=None, jaccard=None, lines_removed=None, lines_kept=None,
                                     run_len=int(j - i), s_pre=float(spre),
                                     note=f"return {days[j] if j < len(days) else 'none'}; unit {units[i]}"))
                i = j + 1
            else:
                i += 1
    log("chat cuts done")

    CAT_SCHEMA = {"type": pl.Utf8, "agent": pl.Int8, "t": pl.Datetime("us", "UTC"), "pt_date": pl.Utf8,
                  "dose": pl.Float64, "sp": pl.Float64, "n_chars": pl.Int32, "jaccard": pl.Float64,
                  "lines_removed": pl.Int32, "lines_kept": pl.Int32, "run_len": pl.Int32, "s_pre": pl.Float64,
                  "note": pl.Utf8}
    catalog = pl.DataFrame(cat_rows, schema=CAT_SCHEMA)
    catalog = (catalog.join(cal.select("pt_date", "goal_no", "regime", "unit"), on="pt_date", how="left")
               .join(roster.select("agent", "name"), on="agent", how="left")
               .with_columns(pl.col("regime").cast(pl.Utf8)).sort("type", "pt_date", "agent"))
    if guard:
        refuse_holdout(catalog["pt_date"].to_list(), "catalog")
    catalog.write_parquet(out / "scramble_catalog.parquet", compression="zstd")
    log(f"catalog: {catalog.group_by('type').agg(pl.len()).sort('type').rows()}")

    # ============================================================================= consolidations (regime III)
    r3days = set(cal.filter(pl.col("regime") == "III")["pt_date"].to_list())
    wset = writes.select("agent", "t").with_columns(pl.lit(1, pl.Int8).alias("w"))
    turns = (act.filter(pl.col("pt_date").is_in(list(r3days)))
             .join(wset, on=["agent", "t"], how="left")
             .select("agent", "t", "pt_date", pl.col("w").fill_null(0).alias("w"), pl.col("error").cast(pl.Int8).alias("e"),
                     pl.lit(0, pl.Int8).alias("isc")))
    cons = (ev.filter((pl.col("action_type") == "CONSOLIDATE") & pl.col("pt_date").is_in(list(r3days)))
            .select("agent", "t", "pt_date", pl.lit(0, pl.Int8).alias("w"), pl.lit(0, pl.Int8).alias("e"),
                    pl.lit(1, pl.Int8).alias("isc")))
    seq = pl.concat([turns, cons]).sort("agent", "t", "isc")
    seq = seq.with_columns(pl.col("isc").cum_sum().over("agent").alias("seg"))
    tt = seq.filter(pl.col("isc") == 0).with_columns(
        pl.int_range(pl.len()).over("agent", "seg").alias("pos"), pl.len().over("agent", "seg").alias("seg_len"))
    tt = tt.with_columns((pl.col("seg_len") - pl.col("pos")).alias("rpos"))  # 1 = last turn of the segment
    segs = tt.group_by("agent", "seg").agg(pl.col("seg_len").first(), pl.col("pt_date").first().alias("d0"),
                                           pl.col("pt_date").last().alias("d1"))
    pre = (tt.filter(pl.col("rpos") <= 10).group_by("agent", "seg")
           .agg(pl.col("w").mean().alias("w_pre"), pl.col("e").mean().alias("e_pre"), pl.len().alias("n_pre")))
    far = (tt.filter(pl.col("rpos").is_between(11, 20)).group_by("agent", "seg")
           .agg(pl.col("w").mean().alias("w_far"), pl.col("e").mean().alias("e_far"), pl.len().alias("n_far")))
    post = (tt.filter(pl.col("pos") < 10).group_by("agent", "seg")
            .agg(pl.col("w").mean().alias("w_post"), pl.col("e").mean().alias("e_post"), pl.len().alias("n_post")))
    ce = seq.filter(pl.col("isc") == 1).select("agent", "t", "pt_date", "seg")  # consolidation that starts segment `seg`
    ce = (ce.join(segs.rename({"seg_len": "seg_len_pre", "d0": "pre_d0", "d1": "pre_d1"})
                  .with_columns((pl.col("seg") + 1).alias("seg")), on=["agent", "seg"], how="left")
          .join(segs.select("agent", "seg", pl.col("seg_len").alias("seg_len_post"), pl.col("d0").alias("post_d0")),
                on=["agent", "seg"], how="left")
          .join(pre.with_columns((pl.col("seg") + 1).alias("seg")), on=["agent", "seg"], how="left")
          .join(far.with_columns((pl.col("seg") + 1).alias("seg")), on=["agent", "seg"], how="left")
          .join(post, on=["agent", "seg"], how="left"))
    ce = ce.with_columns(pl.when(pl.col("seg_len_pre").is_between(41, 42)).then(pl.lit("CF"))
                         .when(pl.col("seg_len_pre").is_between(10, 38)).then(pl.lit("CV")).otherwise(pl.lit("other"))
                         .alias("kind"))
    ce = ce.filter((pl.col("pre_d1") == pl.col("pt_date")) & (pl.col("post_d0") == pl.col("pt_date")))
    # memory snapshot written at this consolidation (nearest within 180 s)
    msn = ms_all.select("agent", pl.col("t").alias("t_mem"), "n_chars", "n_lines", "lines_added", "lines_removed",
                        "lines_kept", "jaccard_prev").sort("t_mem")
    ce = (ce.sort("t").join_asof(msn, left_on="t", right_on="t_mem", by="agent", strategy="nearest",
                                 tolerance="180s")  # snapshot is logged microseconds before the event
          .with_columns((pl.col("lines_added") / pl.col("n_lines").clip(1, None)).alias("stored_dose"),
                        (pl.col("lines_removed") / (pl.col("lines_kept") + pl.col("lines_removed")).clip(1, None))
                        .alias("removed_frac")))
    ce = (ce.join(cal.select("pt_date", "goal_no", "unit"), on="pt_date", how="left")
          .select("agent", "t", "pt_date", "goal_no", "unit", "kind", "seg_len_pre", "seg_len_post", "w_pre", "w_post",
                  "e_pre", "e_post", "n_pre", "n_post", "w_far", "e_far", "n_far", "n_chars", "n_lines", "lines_added", "lines_removed",
                  "stored_dose", "removed_frac", "jaccard_prev"))
    if guard:
        refuse_holdout(ce["pt_date"].unique().to_list(), "consolidations")
    ce.write_parquet(out / "consolidations.parquet", compression="zstd")
    log(f"consolidations {ce.height} ({ce.group_by('kind').agg(pl.len()).rows()})")

    # profile by turn offset (-20..-1 before, +1..+20 after) per unit x kind
    kinds = ce.select("agent", "seg", "kind", "unit") if "seg" in ce.columns else None
    cseg = (seq.filter(pl.col("isc") == 1).select("agent", "seg", "pt_date")
            .join(segs.rename({"seg_len": "seg_len_pre"}).with_columns((pl.col("seg") + 1).alias("seg"))
                  .select("agent", "seg", "seg_len_pre", pl.col("d1").alias("pre_d1")), on=["agent", "seg"], how="left")
            .filter(pl.col("pre_d1") == pl.col("pt_date"))
            .with_columns(pl.when(pl.col("seg_len_pre").is_between(41, 42)).then(pl.lit("CF"))
                          .when(pl.col("seg_len_pre").is_between(10, 38)).then(pl.lit("CV")).otherwise(pl.lit("other"))
                          .alias("kind"))
            .join(cal.select("pt_date", "unit"), on="pt_date", how="left"))
    before = (tt.filter(pl.col("rpos") <= 20).with_columns((-pl.col("rpos")).alias("off"), (pl.col("seg") + 1).alias("cseg"))
              .join(cseg.select("agent", pl.col("seg").alias("cseg"), "kind", "unit", pl.col("pt_date").alias("cd")),
                    on=["agent", "cseg"], how="inner").filter(pl.col("pt_date") == pl.col("cd")))
    after = (tt.filter(pl.col("pos") < 20).with_columns((pl.col("pos") + 1).alias("off"), pl.col("seg").alias("cseg"))
             .join(cseg.select("agent", pl.col("seg").alias("cseg"), "kind", "unit", pl.col("pt_date").alias("cd")),
                   on=["agent", "cseg"], how="inner").filter(pl.col("pt_date") == pl.col("cd")))
    prof = (pl.concat([before.select("unit", "kind", "off", "w", "e"), after.select("unit", "kind", "off", "w", "e")])
            .group_by("unit", "kind", "off").agg(pl.col("w").mean().alias("w_rate"), pl.col("e").mean().alias("e_rate"),
                                                 pl.len().alias("n")).sort("unit", "kind", "off"))
    prof.write_parquet(out / "consolidation_profile.parquet", compression="zstd")
    log("profile done")

    if guard:
        write_provenance("build", ["memory_stats", "events_core", "actions", "artifact_mentions", "activity_bins",
                               "exposure", "chat_core", "rooms_timeline", "roster", "calendar", "intentions",
                               "embeddings/intentions_bge_small"],
                     {"holdout": "dropped before detection", "ML": "n<0.5*SP, jacc<0.3, persistent next5<0.7*SP",
                      "MR": "jacc<0.05, size ratio 0.7-1.4", "CC": "s<0.3*median(prev 5), not main room, >=2 days",
                      "CF": "segment 41-42 turns", "CV": "segment 10-38 turns", "write_verbs": WRITE_VERBS})
    log("done")

    return {"agent_day": ad, "catalog": catalog, "consolidations": ce}


if __name__ == "__main__":
    build(calendar_nonholdout(), holdout_days(), OUT, guard=True)
