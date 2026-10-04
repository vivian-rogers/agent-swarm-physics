"""H128 scheme: project-count curves after each kickoff from the shared host replay.

For every replication period (G30 ... G42, G51 first 20 active h) and the natives (G44 rooms, G37 rooms, NE42
boundaries 05-04 and 05-11 with labels carried), writes
  data/processed/H128-coarsening-vs-freeze/<unit>/curve.parquet   t (active h from the kickoff), N_h, N_p, N_p_m,
                                                                  K_eff, rho, dw = (N_p - 1)/(N_h - 1)
  .../<unit>/deaths.parquet   t, repo (hashed), kind (merge / hop_new / finish), agent, to_repo (hashed), cls_touch
  .../<unit>/meta.json        days, H, events dropped by the active clock, room agents
and _provenance.json. Host replay: infra/shared/replicator_hosts.py (W 30, E 100, arrival tags; non-holdout days only).
Repo names are hashed on output; no message text is stored (kickoff text only in memory inside the shared tagger).

Usage: uv run python hypotheses/H128-coarsening-vs-freeze/scheme/build.py
"""
from __future__ import annotations

import datetime as dt
import json
import sys
import time
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "analysis"))
import h128lib as L  # noqa: E402
from common import REVISION, git_commit  # noqa: E402  (infra/shared on sys.path via h128lib)

RH = L.RH


def room_agents() -> dict:
    gt = pl.read_parquet(L.ROOT / "data/processed/shared/ground_truth_labels.parquet").filter(
        (pl.col("label_kind") == "room_assignment") & (pl.col("goal_no") == 44) & pl.col("preferred") & ~pl.col("holdout"))
    out = {"G44best": set(gt.filter(pl.col("value") == "best")["agent"].cast(pl.Int64).to_list()),
           "G44rest": set(gt.filter(pl.col("value") == "rest")["agent"].cast(pl.Int64).to_list())}
    import rooms_asof as RA
    c = RH.load_commits(37, RH.period_days(37))
    first = RA.room_asof(c.group_by("agent").agg(pl.col("t").min()).sort("agent"), t="t", agent="agent", out="room")
    out["G37best"] = set(first.filter(pl.col("room") == 2)["agent"].cast(pl.Int64).to_list())
    out["G37rest"] = set(first.filter(pl.col("room") == 3)["agent"].cast(pl.Int64).to_list())
    return out


def tag_deaths(de: pl.DataFrame, ev: pl.DataFrame, clock, t0_h=0.0) -> pl.DataFrame:
    """cls_touch of the arrival that carried each merge (the departing agent's arrival at to_repo)."""
    arr = ev.filter(pl.col("kind").is_in(["recruit", "birth"]))
    ta = clock(L.epoch(arr["t"])) - t0_h
    arr = arr.with_columns(pl.Series("ta", ta)).select(pl.col("agent").cast(pl.Int16), pl.col("repo").alias("to_repo"),
                                                       "ta", "cls_touch")
    if "cls_touch" not in ev.columns or de.height == 0:
        return de.with_columns(pl.lit(None, dtype=pl.String).alias("cls_touch"))
    j = de.join(arr, on=["agent", "to_repo"], how="left").filter(
        pl.col("ta").is_null() | ((pl.col("ta") - pl.col("t")).abs() < 1e-6))
    return j.unique(subset=["t", "repo", "agent"], keep="first").drop("ta").sort("t")


def write_unit(name, cur, de, meta):
    o = L.D / name
    o.mkdir(parents=True, exist_ok=True)
    cur.write_parquet(o / "curve.parquet")
    RH.hashed(de, cols=("repo", "to_repo")).write_parquet(o / "deaths.parquet")
    (o / "meta.json").write_text(json.dumps(meta, indent=1, default=str))


def main():
    t0 = time.time()
    L.D.mkdir(parents=True, exist_ok=True)
    rooms = room_agents()
    counts = {}
    for g in L.REPL + [44]:
        d = L.real_events(g, tag=True)
        days = d["days"][:3] if g == 51 else d["days"]
        clock = L.ActiveClock(days)
        ev = d["events"]
        if g == 51:
            ev = ev.filter(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).is_in(days))
        units = {f"G{g:02d}": None}
        if g == 44:
            units = {"G44best": rooms["G44best"], "G44rest": rooms["G44rest"], "G44": None}
        if g == 37:
            units.update({"G37best": rooms["G37best"], "G37rest": rooms["G37rest"]})
        for name, ag in units.items():
            clock.n_drop = 0
            cur, de = L.curve_from_events(ev, clock, agents=ag)
            de = tag_deaths(de, ev if ag is None else ev.filter(pl.col("agent").is_in(list(ag))), clock)
            meta = {"goal_no": g, "days": days, "H": float(cur["t"].max()), "active_h_total": clock.total_h,
                    "events_dropped_by_clock": clock.n_drop, "n_agents": len(ag) if ag else int(ev["agent"].n_unique()),
                    "room_agents": sorted(ag) if ag else None}
            write_unit(name, cur, de, meta)
            counts[name] = {"grid": cur.height, "deaths": de.height, "dropped": clock.n_drop}
        RH.hashed(ev).write_parquet(L.D / f"G{g:02d}" / "events.parquet")
        print(f"G{g:02d} {time.time() - t0:.0f}s", flush=True)
    # NE42: continuous replay #39 -> #41, labels carried across the 05-04 and 05-11 boundaries
    days = RH.period_days(39) + RH.period_days(40) + RH.period_days(41)
    calls = pl.concat([RH.load_calls(g, RH.period_days(g)) for g in (39, 40, 41)]).sort("t_call", "agent")
    commits = pl.concat([RH.load_commits(g, RH.period_days(g)) for g in (39, 40, 41)])
    leave = {}
    for g in (39, 40, 41):
        leave.update(RH.leave_times(g, calls, RH.period_days(g)))
    ev = RH.classify_arrivals(RH.replay_events(RH.window_labels(commits, 30), calls, E=100, leave_t=leave))
    clock = L.ActiveClock(days)
    for b, gday in (("NE42_merge", RH.period_days(40)[0]), ("NE42_split", RH.period_days(41)[0])):
        t0h = float(clock(L.epoch(RH.calendar().filter(pl.col("pt_date") == gday)["win_start"]))[0])
        clock.n_drop = 0
        cur, de = L.curve_from_events(ev, clock, t0_h=t0h, H=min(L.HORIZON_H, clock.total_h - t0h))
        # pre-boundary reference: the last 4 active hours before the boundary
        pre, _ = L.curve_from_events(ev, clock, t0_h=t0h - 4.0, H=4.0)
        de = de.with_columns(pl.lit(None, dtype=pl.String).alias("cls_touch"))
        meta = {"boundary_day": gday, "t0_active_h": t0h, "H": float(cur["t"].max()), "carried": True,
                "pre_dw_median": float(pre["dw"].drop_nans().median()) if pre["dw"].drop_nans().len() else None,
                "pre_N_p_median": float(pre["N_p"].median()), "events_dropped_by_clock": clock.n_drop}
        write_unit(b, cur, de, meta)
        counts[b] = {"grid": cur.height, "deaths": de.height}
    prov = {"built_by": "hypotheses/H128-coarsening-vs-freeze/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["work_commits", "call_windows", "calendar", "period_units", "roster", "rooms_timeline",
                                   "ground_truth_labels", "artifact_mentions", "context_ledger_items", "chat_core",
                                   "chat_text (kickoff text, in memory only, inside replicator_hosts.kickoff_named)"]}],
            "params": {"host_labels": "replicator_hosts W=30 E=100", "grid_h": L.GRID_H, "horizon_h": L.HORIZON_H,
                       "G51": "first 3 non-holdout days (51a)", "holdout": "masked via replicator_hosts.period_days"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat(), "counts": counts}
    (L.D / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print(f"built in {time.time() - t0:.0f}s")


if __name__ == "__main__":
    main()
