"""Hero figure (page 1): one real day of goal period 51 as a spin network and a spin raster.

    uv run python writeup/figures-js/export/hero.py

Spins: each model call is talk (kind == 'talk', red) or not (computer use, search, pause, consolidation: blue).
Couplings: chat messages that name another agent (chat_mentions_clean.mentions_roster), counted per directed pair.
Network day: 2026-09-04 (G51, 32 agents calling). Spin state at the snapshot time t: talk if the agent made a talk
call in [t-10 min, t), not-talk if it made only other calls, off if no call. t is the mid-day moment (after the first
hour) whose talking share among active agents is closest to one half; the caption states this choice.
Raster: 2026-09-02..04, per agent, per 6-min bin: talk (any talk call), other calls only, or no call; nights cut.
All days checked against the reserved data with holdout_mask.
"""
from __future__ import annotations

import numpy as np
import polars as pl

from common import ROOT, write

SH = ROOT / "data/processed/shared"
DAY, GOAL = "2026-09-04", 51


RASTER_DAYS, RBIN = ["2026-09-02", "2026-09-03", "2026-09-04"], 6
SNAP_W = 10


def load_shared_common():
    import importlib.util
    spec = importlib.util.spec_from_file_location("shared_common", ROOT / "infra/shared/common.py")
    sc = importlib.util.module_from_spec(spec); spec.loader.exec_module(sc)
    return sc


def calls(days):
    cw = (pl.scan_parquet(SH / "call_windows.parquet")
          .filter((pl.col("goal_no") == GOAL) & pl.col("pt_date").is_in(days) & ~pl.col("holdout"))
          .select("agent", "pt_date", "kind", "t_call").collect())
    return cw.with_columns((pl.col("kind") == "talk").alias("talk"))


def main():
    sc = load_shared_common()
    assert not any(sc.holdout_mask(RASTER_DAYS, [GOAL] * len(RASTER_DAYS))), "a figure day is reserved"
    ros = pl.read_parquet(SH / "roster.parquet", columns=["agent", "name", "lab"])
    names = dict(zip(ros["agent"].to_list(), ros["name"].to_list()))
    labs = dict(zip(ros["agent"].to_list(), ros["lab"].to_list()))

    # ---------------- network day
    cw = calls([DAY])
    day_start = cw["t_call"].min().replace(minute=0, second=0, microsecond=0)
    cw = cw.with_columns(((pl.col("t_call") - day_start).dt.total_seconds() / 60.0).alias("m"))
    agents = cw.group_by("agent").agg(pl.len().alias("calls"), pl.col("talk").sum().alias("talks"))
    ag = set(agents["agent"].to_list())

    def state_at(t):
        w = cw.filter((pl.col("m") >= t - SNAP_W) & (pl.col("m") < t)).group_by("agent").agg(pl.col("talk").any())
        return {r["agent"]: ("up" if r["talk"] else "down") for r in w.iter_rows(named=True)}

    best, bestgap = None, 9
    for t in np.arange(60 + SNAP_W, cw["m"].max() - 30, 1.0):
        st = state_at(t)
        if len(st) < 0.8 * len(ag):
            continue
        share = sum(v == "up" for v in st.values()) / len(st)
        if abs(share - 0.5) < bestgap:
            best, bestgap = float(t), abs(share - 0.5)
    snap = state_at(best)

    cc = (pl.scan_parquet(SH / "chat_core.parquet").filter((pl.col("goal_no") == GOAL) & (pl.col("pt_date") == DAY)
                                                         & (pl.col("speaker_kind") == "agent"))
          .select("message_id", "agent", "t").collect())
    mc = pl.read_parquet(SH / "chat_mentions_clean.parquet").join(cc, on="message_id", how="inner")
    e = (mc.explode("mentions_roster", empty_as_null=True).drop_nulls("mentions_roster")
         .filter(pl.col("mentions_roster").is_in(list(ag)) & (pl.col("mentions_roster") != pl.col("agent"))
                 & pl.col("agent").is_in(list(ag)))
         .group_by("agent", "mentions_roster").agg(pl.len().alias("n")).sort("n", descending=True))
    msgs = cc.group_by("agent").agg(pl.len().alias("msgs"))
    msgs = dict(zip(msgs["agent"].to_list(), msgs["msgs"].to_list()))
    nodes = [dict(id=int(r["agent"]), name=names.get(r["agent"], str(r["agent"])), lab=labs.get(r["agent"]),
                  calls=int(r["calls"]), talks=int(r["talks"]), msgs=int(msgs.get(r["agent"], 0)),
                  state=snap.get(r["agent"], "off")) for r in agents.sort("agent").iter_rows(named=True)]
    links = [dict(source=int(r["agent"]), target=int(r["mentions_roster"]), n=int(r["n"])) for r in e.iter_rows(named=True)]

    # ---------------- raster over three days (each day from its first to its last call)
    rc = calls(RASTER_DAYS)
    order = (rc.group_by("agent").agg(pl.col("talk").mean().alias("ts")).sort("ts", descending=True)["agent"].to_list())
    days = []
    for d in RASTER_DAYS:
        s = rc.filter(pl.col("pt_date") == d)
        t0 = s["t_call"].min()
        s = s.with_columns(((pl.col("t_call") - t0).dt.total_seconds() / 60.0).alias("m"))
        nb = int(np.ceil(s["m"].max() / RBIN)) + 1
        rows = []
        for a in order:
            sa = s.filter(pl.col("agent") == a)
            b = (sa["m"].to_numpy() // RBIN).astype(int)
            tot = np.bincount(b, minlength=nb); tk = np.bincount(b, weights=sa["talk"].to_numpy().astype(float), minlength=nb)
            rows.append("".join("." if n == 0 else ("u" if t > 0 else "d") for t, n in zip(tk, tot)))
        days.append(dict(day=d, start_utc=t0.isoformat(), n_bins=nb, rows=rows,
                         talk_share=float(s["talk"].mean()), agents=int(s["agent"].n_unique())))

    st = [n["state"] for n in nodes]
    first_off = (cw["t_call"].min() - day_start).total_seconds() / 60.0   # raster days start at the first call
    data = dict(day=DAY, goal=GOAL, snapshot=dict(t_min=best, t_from_first=best - first_off, window_min=SNAP_W, n_up=st.count("up"),
                                                 n_down=st.count("down"), n_off=st.count("off")),
                nodes=nodes, links=links, raster=dict(bin_min=RBIN, order=order, days=days),
                totals=dict(calls=int(cw.height), talk_share=float(cw["talk"].mean()), agent_msgs=int(cc.height),
                            named_msgs=int(mc.filter(pl.col("mentions_roster").list.len() > 0).height),
                            pairs=len(links)))
    print("snapshot", data["snapshot"], "totals", data["totals"],
          "raster", [(d["day"], d["n_bins"], d["agents"], round(d["talk_share"], 3)) for d in days])
    write("hero", data, "writeup/figures-js/export/hero.py",
          ["data/processed/shared/call_windows.parquet", "chat_core.parquet", "chat_mentions_clean.parquet", "roster.parquet"],
          dict(day=DAY, goal=GOAL, raster_days=RASTER_DAYS, raster_bin_min=RBIN, snapshot_window_min=SNAP_W))


if __name__ == "__main__":
    main()
