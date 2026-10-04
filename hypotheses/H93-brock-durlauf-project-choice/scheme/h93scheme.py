"""H93 scheme library: choice streams per channel and the event x option long table (Brock-Durlauf covariates).

A *stream* is a time-ordered polars frame with one row per state change:
  agent (int), t (datetime UTC), op ('arrive' | 'drop'), repo (str), unit (str), pt_date (str), paired (bool: the arrival is
  a switch away from `prev` at the same instant, so `prev` is not an option), prev (str | None), cls (str | None: work
  arrival tag), cls_touch (str | None), win_key (int: attention window ordinal; arrivals with the same key are applied
  together, after all of them have been scored on the state before the window; -1 = apply immediately).

`long_table(stream, named, ...)` replays the stream and writes one row per (choice event, option) with:
  eid, unit, pt_date, agent, opt (option key; '__NEW__' = a repo/project not yet seen in the unit), chosen,
  s (share of the other active agents on the option), n (their count), named, prev (the chooser held the option earlier in
  the period), logcum (log1p cumulative arrivals to the option before the event), new (NEW indicator),
  s_in / s_out (hosts in the chooser's room / other rooms), s_same / s_cross (same / other lab), s_seen / s_unseen (the
  chooser had read a chat link to the option, or mentioned it, before the event), blind (event tag), fold (4 contiguous
  time blocks per unit, for cross-fitting).
Used unchanged for real data (scheme/build.py) and synthetic worlds (analysis/synthetic.py).
"""
from __future__ import annotations

import bisect
import datetime as dt
import math

import numpy as np
import polars as pl

NEW = "__NEW__"


def _key(t):
    return t if isinstance(t, (int, float)) else t.timestamp()


def long_table(stream: pl.DataFrame, named: dict, room_of=None, lab_of=None, seen_t=None, n_folds: int = 4,
               read_t=None):
    """Replay `stream` and build the long choice table plus an event table and an occupancy trace.
    room_of(agent, t) -> room | None; lab_of: dict agent -> lab; seen_t: dict (agent, opt) -> earliest datetime seen."""
    host: dict[int, str] = {}
    held: dict[int, set] = {}
    cum: dict[str, int] = {}
    seen_unit: set = set()
    cur_unit = None
    rows = {k: [] for k in ("eid", "opt", "chosen", "s", "n", "named", "prev", "logcum", "new", "s_in", "s_out",
                            "s_same", "s_cross", "s_seen", "s_unseen", "s_read", "s_noread")}
    evrows = []
    occ = []
    eid = 0
    recs = stream.to_dicts()
    i = 0
    nrec = len(recs)
    while i < nrec:
        # group: rows sharing a win_key >= 0 are scored on the same pre-state; win_key -1 rows are single
        wk = recs[i].get("win_key", -1)
        j = i + 1
        if wk is not None and wk >= 0:
            while j < nrec and recs[j].get("win_key", -1) == wk:
                j += 1
        group = recs[i:j]
        pending = []
        for r in group:
            if r["unit"] != cur_unit:
                cur_unit = r["unit"]
                seen_unit = set()
            a = int(r["agent"])
            if r["op"] == "drop":
                pending.append(("drop", a, r["repo"]))
                continue
            # ---------------------------------------------------------------- score an arrival on the pre-state
            t = r["t"]
            excl = r["prev"] if r.get("paired") else None
            others = {b: rep for b, rep in host.items() if b != a}
            nact = len(others)
            cnt: dict[str, int] = {}
            for rep in others.values():
                cnt[rep] = cnt.get(rep, 0) + 1
            opts = (seen_unit | set(cnt)) - {excl, None}
            chosen = r["repo"] if r["repo"] in opts else NEW
            if len(opts) >= 1:
                ra = room_of(a, t) if room_of else None
                la = lab_of.get(a) if lab_of else None
                rooms_o = {b: room_of(b, t) for b in others} if room_of else {}
                hset = held.get(a, set())
                for o in sorted(opts):
                    n = cnt.get(o, 0)
                    s = n / nact if nact else 0.0
                    hs = [b for b, rep in others.items() if rep == o]
                    nin = sum(1 for b in hs if ra is not None and rooms_o.get(b) == ra)
                    nsame = sum(1 for b in hs if la is not None and lab_of.get(b) == la)
                    sn = bool(seen_t and (st := seen_t.get((a, o))) is not None and st <= t)
                    rows["eid"].append(eid); rows["opt"].append(o); rows["chosen"].append(o == chosen)
                    rows["s"].append(s); rows["n"].append(n); rows["named"].append(bool(named.get(o, False)))
                    rows["prev"].append(o in hset); rows["logcum"].append(math.log1p(cum.get(o, 0))); rows["new"].append(False)
                    rows["s_in"].append(nin / nact if nact else 0.0); rows["s_out"].append((n - nin) / nact if nact else 0.0)
                    rows["s_same"].append(nsame / nact if nact else 0.0); rows["s_cross"].append((n - nsame) / nact if nact else 0.0)
                    rows["s_seen"].append(s if sn else 0.0); rows["s_unseen"].append(0.0 if sn else s)
                    rd = bool(read_t and (rt_ := read_t.get((a, o))) is not None and rt_ <= t)
                    rows["s_read"].append(s if rd else 0.0); rows["s_noread"].append(0.0 if rd else s)
                rows["eid"].append(eid); rows["opt"].append(NEW); rows["chosen"].append(chosen == NEW)
                for k in ("s", "n", "logcum", "s_in", "s_out", "s_same", "s_cross", "s_seen", "s_unseen", "s_read", "s_noread"):
                    rows[k].append(0 if k == "n" else 0.0)
                rows["named"].append(False); rows["prev"].append(False); rows["new"].append(True)
                top = max(cnt.values()) if cnt else 0
                evrows.append({"eid": eid, "unit": r["unit"], "pt_date": r["pt_date"], "t": t, "agent": a,
                               "chosen": chosen, "repo": r["repo"], "is_new": chosen == NEW, "n_opts": len(opts) + 1,
                               "nact": nact, "top": top, "cls": r.get("cls"), "cls_touch": r.get("cls_touch"),
                               "blind": r.get("cls") == "blind", "named_chosen": bool(named.get(r["repo"], False)),
                               "prev_chosen": r["repo"] in hset})
                eid += 1
            pending.append(("arrive", a, r["repo"]))
        # ------------------------------------------------------------------- apply the group's changes
        for op, a, rep in pending:
            if op == "drop":
                if host.get(a) == rep:
                    del host[a]
            else:
                host[a] = rep
                held.setdefault(a, set()).add(rep)
                cum[rep] = cum.get(rep, 0) + 1
                seen_unit.add(rep)
        if host:
            c2: dict[str, int] = {}
            for rep in host.values():
                c2[rep] = c2.get(rep, 0) + 1
            occ.append({"t": group[-1]["t"], "unit": group[-1]["unit"], "nhost": len(host), "top": max(c2.values()),
                        "top_opt": max(sorted(c2), key=lambda k: c2[k]),
                        "hhi": sum(v * v for v in c2.values()) / len(host) ** 2})
        i = j
    if not evrows:
        return None, None, None
    ev = pl.DataFrame(evrows)
    lt = pl.DataFrame(rows).with_columns(pl.col("eid").cast(pl.Int32), pl.col("n").cast(pl.Int16))
    # contiguous time folds within unit (cross-fitting)
    ev = ev.with_columns((pl.int_range(pl.len()).over("unit") * n_folds // pl.len().over("unit")).cast(pl.Int8).alias("fold"))
    lt = lt.join(ev.select("eid", "unit", "pt_date", "agent", "fold", "blind"), on="eid", how="left")
    return ev, lt, pl.DataFrame(occ)


# ================================================================================================ helpers for real data
def rooms_lookup(rt: pl.DataFrame):
    """room_of(agent, t) from rooms_timeline (null t_end = open)."""
    far = dt.datetime(2100, 1, 1, tzinfo=dt.timezone.utc)
    by = {}
    for (a,), g in rt.sort("t_start").group_by(["agent"], maintain_order=True):
        ts = [_key(x) for x in g["t_start"].to_list()]
        te = [_key(x if x is not None else far) for x in g["t_end"].to_list()]
        by[int(a)] = (ts, te, g["room"].to_list())

    def room_of(a, t):
        v = by.get(int(a))
        if v is None:
            return None
        ts, te, rm = v
        k = bisect.bisect_right(ts, _key(t)) - 1
        if k < 0:
            return None
        return rm[k] if _key(t) < te[k] else rm[k]  # last known room if the interval closed (agent idle)
    return room_of


def work_stream(ev: pl.DataFrame, unit_map: dict) -> pl.DataFrame:
    """replicator_hosts events -> stream. depart(old -> new) + arrive(new) at the same t = paired switch."""
    out = []
    last_depart = {}
    for r in ev.sort("t").iter_rows(named=True):  # replay_events order is already (t, kind order, agent)
        a = int(r["agent"])
        if r["kind"] == "depart":
            last_depart[a] = (r["t"], r["repo"])
            out.append({"agent": a, "t": r["t"], "op": "drop", "repo": r["repo"], "paired": False, "prev": None,
                        "cls": None, "cls_touch": None})
        elif r["kind"] in ("expire", "leave"):
            out.append({"agent": a, "t": r["t"], "op": "drop", "repo": r["repo"], "paired": False, "prev": None,
                        "cls": None, "cls_touch": None})
        else:
            ld = last_depart.get(a)
            paired = ld is not None and ld[0] == r["t"]
            out.append({"agent": a, "t": r["t"], "op": "arrive", "repo": r["repo"], "paired": paired,
                        "prev": ld[1] if paired else None, "cls": r.get("cls"), "cls_touch": r.get("cls_touch")})
    s = pl.DataFrame(out, schema={"agent": pl.Int16, "t": pl.Datetime("us", "UTC"), "op": pl.String, "repo": pl.String,
                                  "paired": pl.Boolean, "prev": pl.String, "cls": pl.String, "cls_touch": pl.String})
    return s


def attach_unit(stream: pl.DataFrame, cal: pl.DataFrame, unit_map: dict) -> pl.DataFrame:
    """pt_date = the calendar day whose [win_start, win_end + 6 h) contains t (else the PT date); unit from unit_map."""
    s = stream.with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias("pt_date"))
    s = s.with_columns(pl.col("pt_date").replace_strict(unit_map, default=None).alias("unit"))
    # events before the first unit day (carry-in) or between units: forward/backward fill the unit
    s = s.with_columns(pl.col("unit").fill_null(strategy="forward").fill_null(strategy="backward"))
    return s.with_columns(pl.lit(-1).cast(pl.Int32).alias("win_key"))


def attention_stream(ps: pl.DataFrame, cal: pl.DataFrame, unit_map: dict, expiry_windows: int = 4) -> pl.DataFrame:
    """project_states rows (one period, W = 30, non-holdout) -> stream. An agent's attention label persists until it
    changes or until `expiry_windows` consecutive windows pass without a label (day boundaries count as a long gap).
    A choice is a labelled window whose project differs from the agent's current label, or any labelled window when the
    agent has no current label."""
    cal2 = cal.select("pt_date", "win_start")
    d = ps.join(cal2, on="pt_date", how="left").with_columns(
        (pl.col("win_start") + pl.duration(minutes=30) * pl.col("win").cast(pl.Int64) + pl.duration(minutes=15)).alias("t"))
    days = sorted(d["pt_date"].unique().to_list())
    dix = {x: k for k, x in enumerate(days)}
    d = d.with_columns((pl.col("pt_date").replace_strict(dix, return_dtype=pl.Int64) * 10000 + pl.col("win").cast(pl.Int64)).alias("wk"))
    d = d.sort("wk", "agent")
    cur: dict[int, tuple[str, int]] = {}  # agent -> (label, last wk)
    out = []
    for wk, g in d.group_by("wk", maintain_order=True):
        wk = int(wk[0]) if isinstance(wk, tuple) else int(wk)
        # expiries before this window
        for a in list(cur):
            lab, lw = cur[a]
            gap = (wk - lw) if wk // 10000 == lw // 10000 else 10 ** 6
            if gap > expiry_windows:
                out.append({"agent": a, "t": g["t"][0] - dt.timedelta(minutes=15), "op": "drop", "repo": lab,
                            "paired": False, "prev": None, "wk": wk - 1, "pt_date": g["pt_date"][0]})
                del cur[a]
        for a, p, t, pdte in g.select("agent", "project", "t", "pt_date").iter_rows():
            a = int(a); p = str(p)
            c = cur.get(a)
            if c is not None and c[0] == p:
                cur[a] = (p, wk)
                continue
            if c is not None:
                out.append({"agent": a, "t": t, "op": "drop", "repo": c[0], "paired": False, "prev": None, "wk": wk,
                            "pt_date": pdte})
            out.append({"agent": a, "t": t, "op": "arrive", "repo": p, "paired": c is not None, "prev": c[0] if c else None,
                        "wk": wk, "pt_date": pdte})
            cur[a] = (p, wk)
    s = pl.DataFrame(out, schema={"agent": pl.Int16, "t": pl.Datetime("us", "UTC"), "op": pl.String, "repo": pl.String,
                                  "paired": pl.Boolean, "prev": pl.String, "wk": pl.Int64, "pt_date": pl.String})
    # drops must be applied after the window's arrivals are scored but they belong to the same window: give them the
    # same win_key; long_table applies a group's changes after scoring the whole group.
    s = s.with_columns(pl.col("pt_date").replace_strict(unit_map, default=None).alias("unit"),
                       pl.col("wk").cast(pl.Int32).alias("win_key"), pl.lit(None, pl.String).alias("cls"),
                       pl.lit(None, pl.String).alias("cls_touch"))
    s = s.with_columns(pl.col("unit").fill_null(strategy="forward").fill_null(strategy="backward"))
    return s.sort("win_key", "op", "agent", descending=[False, True, False]).drop("wk")


def seen_times(goal_days: list[str], projects: list[str], project_map: pl.DataFrame, shared, reads_only: bool = False) -> dict:
    """(agent, project) -> earliest time the agent read a chat link to the project (ledger receiving call t_call) or
    mentioned it itself (strict). Codes only."""
    pm = project_map.filter(pl.col("project").is_in(projects))
    am = (pl.scan_parquet(shared / "artifact_mentions.parquet").filter(pl.col("artifact").is_in(pm["artifact"].implode()))
          .collect().join(pm, on="artifact"))
    am = am.with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias("pt_date"))
    am = am.filter(pl.col("pt_date").is_in(goal_days))
    out: dict = {}
    selfm = am.filter(pl.col("how").cast(pl.String).is_in(["url", "output", "bare"]) & (pl.col("speaker_kind").cast(pl.String) == "agent")
                      & pl.col("agent").is_not_null())
    if not reads_only:
        for (a, p), g in selfm.group_by(["agent", "project"]):
            out[(int(a), p)] = g["t"].min()
    links = am.filter((pl.col("source").cast(pl.String) == "chat") & pl.col("how").cast(pl.String).is_in(["url", "bare"])
                      & pl.col("message_id").is_not_null()).select("message_id", "project", pl.col("agent").alias("poster")).unique()
    if links.height:
        li = (pl.scan_parquet(shared / "context_ledger_items.parquet").filter(pl.col("message_id").is_in(links["message_id"].unique().implode()))
              .select("turn_id", "message_id").collect())
        cw = (pl.scan_parquet(shared / "call_windows.parquet").filter(pl.col("turn_id").is_in(li["turn_id"].implode()))
              .select("turn_id", "agent", "t_call").collect())
        reads = li.join(cw, on="turn_id").join(links, on="message_id")
        if reads_only:  # A2: links posted by someone else, read through the ledger (no self-mentions)
            reads = reads.filter(pl.col("poster").is_null() | (pl.col("poster") != pl.col("agent")))
        for (a, p), g in reads.group_by(["agent", "project"]):
            k = (int(a), p)
            t = g["t_call"].min()
            out[k] = min(out[k], t) if k in out else t
    return out


def order_parameter(occ: pl.DataFrame, min_hosts: int = 3) -> dict:
    """Event-averaged largest-option share of hosted agents (states with >= min_hosts hosts), per unit and overall."""
    if occ is None or occ.height == 0:
        return {}
    o = occ.filter(pl.col("nhost") >= min_hosts).with_columns((pl.col("top") / pl.col("nhost")).alias("m"))
    res = {"all": float(o["m"].mean()) if o.height else None, "n": o.height}
    for (u,), g in o.group_by(["unit"]):
        res[str(u)] = float(g["m"].mean())
    return res


def np_mean(x):
    x = [v for v in x if v is not None and np.isfinite(v)]
    return float(np.mean(x)) if x else None
