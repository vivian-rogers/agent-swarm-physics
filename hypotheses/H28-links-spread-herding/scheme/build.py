"""H28 scheme: touches, links, call-start-visible link exposures, active bins, plans and kicks, per goal period.

  uv run python hypotheses/H28-links-spread-herding/scheme/build.py               # all H28 periods (non-holdout days)
  uv run python hypotheses/H28-links-spread-herding/scheme/build.py --goals 31 41

Writes data/processed/H28-links-spread-herding/G<NN>/ (zstd parquet, no text):
  touches.parquet     agent, t_ms, project, source (0 action, 1 chat)       strict mentions (how in url/output/bare)
  links.parquet       msg, t_ms, sender (-1 human), room, project, how, addressed (list of agent codes)
  exposures.parquet   msg, recipient, t_vis_ms                               call-start visibility (pre-NE09: next events_core turn)
  turns.parquet       agent, t_ms, is_event                                  actions minus pause mirrors, plus events_core (H18 rule)
  turn_bins.parquet   day, bin, agent, room                                  active 5-min bins and the agent's room at bin start
  plans.parquet       plan, agent, t_ms ; plan_projects.parquet plan, project
  kicks.parquet       t_ms, kind, room, agent
  meta.json           days (windows), universe, roster per day, flags, counts
Times are int64 milliseconds since the Unix epoch (UTC). Holdout days are dropped before anything is computed unless
--allow-holdout (only analysis/confirm_holdout.py passes it).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h28lib import (ALL_PERIODS, BIN_S, C, K_MAX, NE09, OUT, SHARED, STRICT_LINK, STRICT_TOUCH, assert_not_holdout,  # noqa: E402
                    gname, h11_build, h18_build, write_provenance)


def ms(s: pl.Series) -> np.ndarray:
    return s.dt.epoch("ms").to_numpy().astype(np.int64)


class Shared:
    def __init__(self):
        t = time.time()
        self.cal = pl.read_parquet(SHARED / "calendar.parquet")
        self.roster = pl.read_parquet(SHARED / "roster.parquet")
        self.cc = set(self.roster.filter(pl.col("claude_code"))["agent"].to_list())
        chat = pl.read_parquet(SHARED / "chat_core.parquet", columns=["message_id", "t", "room", "speaker_kind", "agent"])
        assert chat["t"].is_sorted(), "chat_core must be sorted by t (exposure.msg is a row index into it)"
        men = pl.read_parquet(SHARED / "chat_mentions_clean.parquet", columns=["message_id", "mentions_roster"])
        self.chat = chat.with_row_index("msg").join(men, on="message_id", how="left")
        self.exposure = pl.read_parquet(SHARED / "exposure.parquet", columns=["msg", "agent"])
        self.am = pl.read_parquet(SHARED / "artifact_mentions.parquet")
        self.pm = h11_build().project_map()            # H11: artifact -> project (imported, not modified)
        self.ev = pl.read_parquet(SHARED / "events_core.parquet", columns=["t", "pt_date", "actor_kind", "agent", "action_type"]
                                  ).filter((pl.col("actor_kind") == "agent") & pl.col("agent").is_not_null())
        self.intent = pl.read_parquet(SHARED / "intentions.parquet")
        self.kicks = pl.read_parquet(SHARED / "kicks.parquet")
        self.rooms_tl = pl.read_parquet(SHARED / "rooms_timeline.parquet").sort("agent", "t_start")
        self.h18 = h18_build()
        print(f"shared tables loaded in {time.time() - t:.0f}s", flush=True)


def period_days(sh: Shared, g: int, allow_holdout=False, only_holdout=False) -> pl.DataFrame:
    cal = sh.cal.filter((pl.col("goal_no") == g) & (pl.col("n_agent_events") > 0)).sort("pt_date")
    ho = np.array(C.holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())) | cal["holdout"].to_numpy()
    cal = cal.with_columns(pl.Series("ho", ho))
    if only_holdout:
        cal = cal.filter(pl.col("ho"))
    elif not allow_holdout:
        cal = cal.filter(~pl.col("ho"))
    return cal.select("pt_date", "win_start", "win_end", "window_s", "ho")


def in_windows(df: pl.DataFrame, days: pl.DataFrame) -> pl.DataFrame:
    df = df.with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias("pt_date"))
    df = df.join(days.select("pt_date", "win_start", "win_end"), on="pt_date", how="inner")
    return df.filter((pl.col("t") >= pl.col("win_start")) & (pl.col("t") <= pl.col("win_end"))).drop("win_start", "win_end")


def room_at(sh: Shared, agents: np.ndarray, t: pl.Series) -> np.ndarray:
    """Room code of each (agent, time) from rooms_timeline (-1 if unknown)."""
    df = pl.DataFrame({"i": np.arange(len(agents)), "agent": agents.astype(np.int8), "t": t})
    j = df.sort("t").join_asof(sh.rooms_tl.select("agent", "room", pl.col("t_start").alias("t")).sort("t"),
                               on="t", by="agent", strategy="backward")
    return j.sort("i")["room"].fill_null(-1).to_numpy().astype(np.int16)


def build_period(sh: Shared, g: int, allow_holdout=False, only_holdout=False, out: Path = OUT, verbose=True):
    days = period_days(sh, g, allow_holdout, only_holdout)
    if days.is_empty():
        return None
    pre_ne09 = days["pt_date"].max() < NE09
    if days["pt_date"].min() < NE09 <= days["pt_date"].max():
        raise SystemExit(f"G{g}: period straddles NE09; split it first")
    dates = days["pt_date"].to_list()
    t0 = days["win_start"].min()
    t1 = days["win_end"].max()
    ros = sh.roster.filter(~pl.col("claude_code"))
    roster_day = {d: sorted(int(r["agent"]) for r in ros.iter_rows(named=True)
                            if r["joined"] <= d and (r["left"] is None or d < r["left"])) for d in dates}

    # touches: strict mentions by agents in actions and their own chat
    am = sh.am.filter((pl.col("t") >= t0) & (pl.col("t") <= t1))
    tch = am.filter((pl.col("speaker_kind").cast(pl.String) == "agent") & pl.col("agent").is_not_null()
                    & pl.col("source").cast(pl.String).is_in(["action", "chat"])
                    & pl.col("how").cast(pl.String).is_in(list(STRICT_TOUCH)))
    tch = tch.join(sh.pm, on="artifact", how="inner").filter(~pl.col("agent").is_in(list(sh.cc)))
    tch = tch.with_columns(pl.coalesce(pl.col("message_id"), pl.col("ref_index").cast(pl.String)).alias("ref"))
    tch = tch.unique(subset=["agent", "source", "ref", "project"]).pipe(in_windows, days)
    touches = tch.select("agent", pl.col("t").dt.epoch("ms").alias("t_ms"), "project",
                         (pl.col("source").cast(pl.String) == "chat").cast(pl.Int8).alias("source")).sort("t_ms")
    # universe: touched by >= 2 distinct agents
    uni = touches.group_by("project").agg(pl.col("agent").n_unique().alias("n_agents"), pl.len().alias("n_touch")).filter(
        pl.col("n_agents") >= 2).sort(["n_agents", "n_touch", "project"], descending=[True, True, False]).head(K_MAX)

    # links: strict chat mentions by anyone
    lk = am.filter((pl.col("source").cast(pl.String) == "chat") & pl.col("how").cast(pl.String).is_in(list(STRICT_LINK)))
    lk = lk.join(sh.pm, on="artifact", how="inner").unique(subset=["message_id", "project"]).pipe(in_windows, days)
    lk = lk.join(sh.chat.select("message_id", "msg", pl.col("room").alias("room_c"), "speaker_kind", pl.col("agent").alias("spk"),
                                "mentions_roster"), on="message_id", how="inner")
    links = lk.select(pl.col("msg").cast(pl.UInt32), pl.col("t").dt.epoch("ms").alias("t_ms"),
                      pl.when(pl.col("speaker_kind").cast(pl.String) == "agent").then(pl.col("spk")).otherwise(-1)
                      .cast(pl.Int16).alias("sender"),
                      pl.col("room_c").cast(pl.Int16).alias("room"), "project", pl.col("how").cast(pl.String),
                      pl.col("mentions_roster").alias("addressed")).sort("t_ms", "msg", "project")

    # turns (H18 rule) for visibility and activity
    tt = sh.h18.turn_times(sh, t0 - dt.timedelta(hours=2), t1 + dt.timedelta(hours=26))
    evt = sh.ev.filter((pl.col("t") >= t0 - dt.timedelta(hours=2))
                       & (pl.col("t") < t1 + dt.timedelta(hours=26))).select("t", "agent").sort("agent", "t")
    ev_turns = {int(a): ms(sub["t"]) for (a,), sub in evt.group_by(["agent"], maintain_order=True)}
    turn_rows = []
    for a, us in tt.items():
        if a in sh.cc:
            continue
        tm = (us // 1000).astype(np.int64)
        e = ev_turns.get(a, np.zeros(0, np.int64))
        is_ev = np.isin(tm, e)
        turn_rows.append(pl.DataFrame({"agent": np.full(len(tm), a, np.int8), "t_ms": tm, "is_event": is_ev}))
    turns = pl.concat(turn_rows).sort("agent", "t_ms")

    # exposures: recipients of each link (exposure table), visibility time
    ex = sh.exposure.filter(pl.col("msg").is_in(links["msg"].unique().implode())).rename({"agent": "recipient"})
    ex = ex.join(links.select("msg", "sender", "t_ms").unique("msg"), on="msg").filter(
        (pl.col("recipient") != pl.col("sender")) & ~pl.col("recipient").is_in(list(sh.cc)))
    vis = []
    for (a,), sub in ex.group_by(["recipient"], maintain_order=True):
        tv = (ev_turns.get(int(a), np.zeros(0, np.int64)) if pre_ne09
              else turns.filter(pl.col("agent") == a)["t_ms"].to_numpy())
        tm = sub["t_ms"].to_numpy()
        j = np.searchsorted(tv, tm, side="left")
        ok = j < len(tv)
        t_vis = np.where(ok, tv[np.clip(j, 0, max(len(tv) - 1, 0))] if len(tv) else 0, -1)
        vis.append(sub.select("msg", pl.col("recipient").cast(pl.Int8)).with_columns(pl.Series("t_vis_ms", t_vis.astype(np.int64))))
    exposures = pl.concat(vis).filter(pl.col("t_vis_ms") >= 0).sort("msg", "recipient")

    # active bins and rooms
    dayinfo = []
    tb = []
    for di, r in enumerate(days.iter_rows(named=True)):
        ws, we = int(r["win_start"].timestamp() * 1000), int(r["win_end"].timestamp() * 1000)
        nb = max(1, int(np.ceil((we - ws) / (BIN_S * 1000))))
        dayinfo.append({"pt_date": r["pt_date"], "ws_ms": ws, "we_ms": we, "nb": nb})
        x = turns.filter((pl.col("t_ms") >= ws) & (pl.col("t_ms") <= we))
        b = ((x["t_ms"].to_numpy() - ws) // (BIN_S * 1000)).clip(0, nb - 1)
        tb.append(pl.DataFrame({"day": np.full(len(b), di, np.int16), "bin": b.astype(np.int16),
                                "agent": x["agent"].to_numpy().astype(np.int8)}).unique())
    turn_bins = pl.concat(tb).sort("day", "bin", "agent")
    ws_arr = np.array([d["ws_ms"] for d in dayinfo], np.int64)
    tstart = ws_arr[turn_bins["day"].to_numpy()] + turn_bins["bin"].to_numpy().astype(np.int64) * BIN_S * 1000
    turn_bins = turn_bins.with_columns(pl.Series("room", room_at(sh, turn_bins["agent"].to_numpy(),
                                                                  pl.Series(tstart * 1000).cast(pl.Datetime("us", "UTC")))))
    turn_bins = turn_bins.filter(pl.struct("day", "agent").map_elements(
        lambda s: s["agent"] in roster_day[dates[s["day"]]], return_dtype=pl.Boolean))

    # plans: intentions and the projects they name
    it = sh.intent.filter((pl.col("t") >= t0) & (pl.col("t") <= t1) & ~pl.col("agent").is_in(list(sh.cc)))
    plans = it.select(pl.col("event_index").alias("plan"), "agent", pl.col("t").dt.epoch("ms").alias("t_ms")).sort("t_ms")
    pp = am.filter((pl.col("source").cast(pl.String) == "intention") & pl.col("how").cast(pl.String).is_in(list(STRICT_LINK)))
    pp = pp.join(sh.pm, on="artifact", how="inner").select(pl.col("ref_index").alias("plan"), "project").unique()
    plan_projects = pp.filter(pl.col("plan").is_in(plans["plan"].implode()))

    kicks = sh.kicks.filter((pl.col("t") >= t0 - dt.timedelta(hours=2)) & (pl.col("t") <= t1)
                            & pl.col("kind").is_in(["human_message", "automated_message", "goal_kickoff"]))
    kicks = kicks.select(pl.col("t").dt.epoch("ms").alias("t_ms"), "kind", pl.col("room").cast(pl.Int16),
                         pl.col("agent").cast(pl.Int16))

    meta = {"goal": g, "pre_ne09": bool(pre_ne09), "days": dayinfo, "roster_day": roster_day,
            "universe": uni.to_dicts(), "holdout_days": int(days["ho"].sum()),
            "counts": {"touches": touches.height, "links": links.height, "link_msgs": links["msg"].n_unique(),
                       "links_universe": links.filter(pl.col("project").is_in(uni["project"].implode())).height,
                       "exposures": exposures.height, "turns": turns.height, "active_bins": turn_bins.height,
                       "plans": plans.height, "plan_projects": plan_projects.height}}
    d = out / gname(g)
    d.mkdir(parents=True, exist_ok=True)
    for name, df in [("touches", touches), ("links", links), ("exposures", exposures), ("turns", turns),
                     ("turn_bins", turn_bins), ("plans", plans), ("plan_projects", plan_projects), ("kicks", kicks)]:
        df.write_parquet(d / f"{name}.parquet", compression="zstd", compression_level=9)
    (d / "meta.json").write_text(json.dumps(meta, indent=1))
    if verbose:
        print(f"{gname(g)}: {len(dates)} days, universe {uni.height}, touches {touches.height}, links {links.height} "
              f"({meta['counts']['links_universe']} to universe), exposures {exposures.height}, active bins {turn_bins.height}"
              f"{' [pre-NE09]' if pre_ne09 else ''}", flush=True)
    return meta


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--goals", type=int, nargs="*", default=None)
    ap.add_argument("--allow-holdout", action="store_true", help="only for analysis/confirm_holdout.py")
    a = ap.parse_args()
    goals = a.goals or ALL_PERIODS
    assert_not_holdout(goals, a.allow_holdout)
    sh = Shared()
    for g in goals:
        build_period(sh, g, allow_holdout=a.allow_holdout)
    write_provenance(OUT, "hypotheses/H28-links-spread-herding/scheme/build.py",
                     ["calendar", "roster", "chat_core", "chat_mentions_clean", "exposure", "artifact_mentions", "artifacts",
                      "events_core", "actions", "intentions", "kicks", "rooms_timeline"],
                     {"bin_s": BIN_S, "k_max": K_MAX, "strict_touch": list(STRICT_TOUCH), "strict_link": list(STRICT_LINK),
                      "touch_sources": ["action", "chat"], "universe": ">= 2 distinct touching agents",
                      "visibility": "first logged turn (actions minus pause mirrors + events_core) at or after the post; "
                                    "pre-NE09 (2025-12-20): first events_core turn",
                      "project_map": "H11 scheme/build.py project_map", "turn_rule": "H18 scheme/build.py turn_times",
                      "goals": goals, "holdout": "excluded (calendar.holdout | holdout_mask)"}, key="scheme")


if __name__ == "__main__":
    main()
