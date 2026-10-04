"""C1: how well does a room rule reproduce what the Claude Code agent actually saw?

  uv run python hypotheses/H08-context-is-the-coupling/analysis/cc_exposure.py

Ground truth: event ids returned by its `get_events` calls (scheme/build_cc_exposure.py; holdout dates already dropped).
Rule: every event by another actor posted in the agent's room (the event's roomId, else the actor's room from
rooms_timeline; everyone in #general before 2026-02-25), on a PT day the agent fetched, up to its last fetch of that
day. Per goal period: recall (share of truly seen events the rule predicts), precision (share of predicted events seen),
coverage by event type and by room (own / other), delay (first fetch - creation), fetch cadence.
Writes data/processed/H08-context-is-the-coupling/cc/c1.json.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
from h08lib import *  # noqa: E402,F403

CC = OUT / "cc"
ROOMS_V1 = dt.datetime(2026, 2, 25, tzinfo=dt.timezone.utc)


def room_lookup():
    tl = {}
    rt = pl.read_parquet(SH / "rooms_timeline.parquet").sort("agent", "t_start")
    for (a,), sub in rt.group_by(["agent"], maintain_order=True):
        tl[int(a)] = (us(sub["t_start"]), sub["room"].to_numpy())
    return tl


def room_at(tl, a, t):
    if a not in tl:
        return np.full(len(t), -1, dtype=np.int16)
    ts, rm = tl[a]
    idx = np.searchsorted(ts, t, side="right") - 1
    return np.where(idx >= 0, rm[np.clip(idx, 0, None)], -1).astype(np.int16)


def q(x, ps=(10, 25, 50, 75, 90, 99)):
    x = np.asarray(x, float)
    x = x[np.isfinite(x)]
    return {str(p): float(np.percentile(x, p)) for p in ps} if len(x) else None


def main(cc_dir: Path | None = None, periods=None, out_name: str = "c1.json"):
    CC = cc_dir or (OUT / "cc")
    periods = periods or CC_PERIODS
    fe = pl.read_parquet(CC / "cc_fetches.parquet")
    se = pl.read_parquet(CC / "cc_seen.parquet")
    ev = pl.read_parquet(CC / "cc_village_events.parquet")
    cal = calendar().select("pt_date", "goal_no", "holdout")
    gmap = dict(zip(cal["pt_date"].to_list(), cal["goal_no"].to_list()))
    fe = fe.with_columns(pl.col("t_result").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.Utf8).alias("pt_date"))
    fe = fe.with_columns(pl.col("pt_date").replace_strict(gmap, default=None).alias("goal_no"))
    ev = ev.with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.Utf8).alias("pt_date"))
    tl = room_lookup()
    # event room: roomId, else the actor's room at the time, else #general before rooms v1
    t_e = us(ev["t"])
    room = ev["room"].to_numpy().astype(np.int16)
    agent = ev["agent"].to_numpy()
    fill = np.full(len(ev), -1, np.int16)
    for a in np.unique(agent[(room < 0) & (agent >= 0)]):
        sel = (room < 0) & (agent == a)
        fill[sel] = room_at(tl, int(a), t_e[sel])
    eroom = np.where(room >= 0, room, fill)
    eroom = np.where((eroom < 0) & (t_e < int(ROOMS_V1.timestamp() * US)), 0, eroom)
    ccroom = room_at(tl, CC_AGENT, t_e)
    ev = ev.with_columns(pl.Series("eroom", eroom), pl.Series("ccroom", ccroom), pl.Series("t_us", t_e))
    # seen: first fetch per event id
    fs = se.join(fe.select("fetch_id", "t_result", "pt_date", "goal_no"), on="fetch_id", how="inner")
    fs = fs.with_columns(pl.col("t_event_api").dt.cast_time_unit("us"))
    first = fs.sort("t_result").group_by("event_id").agg(pl.col("t_result").first().alias("t_seen"),
                                                         pl.col("goal_no").first().alias("goal_seen"),
                                                         pl.col("t_event_api").first().alias("t_api"),
                                                         pl.col("action").first().alias("action_api"),
                                                         pl.col("fetch_id").n_unique().alias("n_fetches"))
    n_ids = first.height
    m = first.join(ev.select("event_id", "t", "t_us", "action", "actor_kind", "agent", "eroom", "ccroom", "pt_date"),
                   on="event_id", how="left")
    out = {"n_seen_ids_nonholdout": n_ids, "id_match_share": float(m["t"].is_not_null().mean())}
    # every fetched event has its creation time in the API payload (matches the events table to the second)
    m = m.with_columns(pl.coalesce("t", "t_api").alias("t_any"), pl.coalesce("action", "action_api").alias("action"))
    m = m.with_columns(((pl.col("t_seen") - pl.col("t_any")).dt.total_microseconds() / US).alias("delay_s"))
    m = m.with_columns((pl.col("delay_s") > 86400).alias("replay"))
    allseen = m
    m = m.filter(pl.col("t").is_not_null())
    out["periods"] = {}
    for g in periods:
        fg = fe.filter(pl.col("goal_no") == g)
        if not fg.height:
            out["periods"][gname(g)] = {"n_fetches": 0}
            continue
        days = sorted(fg["pt_date"].unique().to_list())
        lastf = {d: int(x.timestamp() * US) for d, x in fg.group_by("pt_date").agg(pl.col("t_result").max()).iter_rows()}
        firstf = {d: int(x.timestamp() * US) for d, x in fg.group_by("pt_date").agg(pl.col("t_result").min()).iter_rows()}
        evg = ev.filter(pl.col("pt_date").is_in(days) & (pl.col("agent") != CC_AGENT))
        evg = evg.filter(pl.col("t_us") <= pl.col("pt_date").replace_strict(lastf, default=0))
        seen_all_g = allseen.filter(pl.col("goal_seen") == g)
        seen_g = m.filter((pl.col("goal_seen") == g) & (pl.col("agent") != CC_AGENT))
        seen_ids = set(seen_g["event_id"].to_list()) | set(seen_all_g.filter(pl.col("t").is_null())["event_id"].to_list())
        cur_ids = set(seen_g.filter(~pl.col("replay"))["event_id"].to_list())
        own = evg.filter((pl.col("eroom") == pl.col("ccroom")) & (pl.col("eroom") >= 0))
        other = evg.filter((pl.col("eroom") != pl.col("ccroom")) & (pl.col("eroom") >= 0))
        pred_ids = set(own["event_id"].to_list())
        inter = len(seen_ids & pred_ids)
        r = {"days": days, "n_fetches": fg.height, "n_seen": len(seen_ids), "n_pred_rule": len(pred_ids),
             "recall": inter / max(1, len(seen_ids)), "precision": inter / max(1, len(pred_ids)),
             "seen_outside_window_or_room": len(seen_ids - pred_ids),
             "replay_share": float(seen_all_g["replay"].mean()) if seen_all_g.height else None,
             "replay_created_range": ([str(x) for x in (seen_all_g.filter(pl.col("replay"))["t_any"].min(),
                                                         seen_all_g.filter(pl.col("replay"))["t_any"].max())]
                                      if seen_all_g.filter(pl.col("replay")).height else None),
             "recall_current_feed": (len(cur_ids & pred_ids) / len(cur_ids)) if cur_ids else None,
             "n_current_feed": len(cur_ids)}
        # baselines: sees everything (all rooms) / own-room chat only
        all_ids = set(evg["event_id"].to_list())
        chat_ids = set(own.filter(pl.col("action").is_in(["AGENT_TALK", "USER_TALK"]))["event_id"].to_list())
        r["baseline_everything"] = {"recall": len(seen_ids & all_ids) / max(1, len(seen_ids)),
                                    "precision": len(seen_ids & all_ids) / max(1, len(all_ids))}
        r["baseline_own_chat"] = {"recall": len(seen_ids & chat_ids) / max(1, len(seen_ids)),
                                  "precision": len(seen_ids & chat_ids) / max(1, len(chat_ids))}
        r["other_room_events"] = other.height
        r["other_room_coverage"] = (len(seen_ids & set(other["event_id"].to_list())) / other.height) if other.height else None
        r["coverage_by_type_own_room"] = {
            a: {"n": int(sub.height), "seen": int(sum(x in seen_ids for x in sub["event_id"].to_list())),
                "coverage": float(np.mean([x in seen_ids for x in sub["event_id"].to_list()]))}
            for (a,), sub in own.group_by(["action"]) if sub.height >= 5}
        r["seen_by_type"] = dict(seen_g.group_by("action").len().iter_rows())
        r["delay_s"] = q(seen_g.filter(~pl.col("replay"))["delay_s"].to_numpy())
        r["delay_s_incl_replay"] = q(seen_all_g["delay_s"].to_numpy())
        r["delay_s_talk"] = q(seen_g.filter(pl.col("action") == "AGENT_TALK")["delay_s"].to_numpy())
        tr_ = np.sort(us(fg["t_result"]))
        gaps = np.diff(tr_) / US
        same = np.array([fg.sort("t_result")["pt_date"][i] == fg.sort("t_result")["pt_date"][i + 1] for i in range(len(tr_) - 1)])
        r["fetch_interval_s"] = q(gaps[same]) if same.any() else None
        r["fetches_per_active_hour"] = float(fg.height / max(1e-9, sum((lastf[d] - firstf[d]) / US / 3600 for d in days)))
        r["has_more_share"] = float(fg["has_more"].fill_null(False).mean())
        r["unseen_count_q"] = q(fg["unseen"].drop_nulls().to_numpy().astype(float))
        r["cc_rooms"] = sorted(set(own["ccroom"].to_list()))
        out["periods"][gname(g)] = r
        print(f"{gname(g)}: fetches {fg.height}, seen {len(seen_ids)}, pred {len(pred_ids)}, recall {r['recall']:.3f}, "
              f"precision {r['precision']:.3f}, other-room cov {r['other_room_coverage']}, "
              f"delay med {r['delay_s']['50'] if r['delay_s'] else None}", flush=True)
    jdump(out, CC / out_name)
    write_provenance("cc/c1.json", "hypotheses/H08-context-is-the-coupling/analysis/cc_exposure.py",
                     ["cc/* (H08 scheme)", "rooms_timeline", "calendar"],
                     {"rule": "own room (roomId, else actor's room), up to the last fetch of the PT day",
                      "periods": CC_PERIODS})


if __name__ == "__main__":
    main()
