"""H136 structural pass (run before any freeze time; card "Structural precondition", H131's lesson).

For each candidate kickoff unit: t_k (first kickoff message of the unit), each member's kickoff read-out call t_r,i
(first DQ1 receiving call of any unit kickoff message), read delay D_r (active min), the active-before flag (>= 1 own
non-summary call in the 30 active min before t_k), the number of own calls in (t_k, t_r), the first call of the day,
and the delayed-active-reader flag. No artifact, mention, commit or freeze time is read here.

  uv run python hypotheses/H136-freeze-at-first-kickoff-read/scheme/structure.py
Writes data/processed/H136-.../structure/readers.parquet and units.json.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h136lib as L  # noqa: E402
from common import git_commit, REVISION  # noqa: E402


def unit_readers(name: str, goal: int, room, cal: pl.DataFrame, clk: L.Clock, km: pl.DataFrame) -> tuple[pl.DataFrame, dict]:
    d0 = cal.filter(pl.col("goal_no") == goal)["pt_date"].min()
    k = km.filter((pl.col("goal_no") == goal) & (pl.col("pt_date") == d0))
    if room is not None:
        k = k.filter(pl.col("room") == room)
    info = {"unit": name, "goal_no": goal, "room": room, "kickoff_day": d0, "n_kickoff_msgs": k.height}
    if k.height == 0:
        info["excluded"] = "no non-reserved kickoff message"
        return pl.DataFrame(), info
    t_k = k["t"].min()
    goal_days = cal.filter(pl.col("goal_no") == goal).sort("pt_date")
    days = goal_days["pt_date"].to_list()
    pd_ = L.prev_day(cal, d0)
    prev_reserved = bool(cal.filter(pl.col("pt_date") == pd_)["ho"][0]) if pd_ else True
    cw = L.calls(days + ([pd_] if pd_ else []))
    rc = L.receipts(k["message_id"].to_list())
    rc = rc.filter(pl.col("goal_no") == goal)
    first = rc.sort("t_call").group_by("agent", maintain_order=True).first().select(
        "agent", pl.col("t_call").alias("t_r"), pl.col("turn_id").alias("turn_r"), pl.col("pt_date").alias("read_day"))
    ak = float(clk([L.us(t_k)])[0])
    rows = []
    for a, t_r, turn_r, rday in first.iter_rows():
        c = cw.filter(pl.col("agent") == a)
        ta = c["t_call"].dt.epoch("us").to_numpy()
        aa = clk(ta) if len(ta) else np.array([])
        tk_us = L.us(t_k)
        tr_us = L.us(t_r)
        before = (ta < tk_us) & (aa >= ak - L.ACTIVE_BEFORE_MIN)
        same_day_before = (ta < tk_us) & (c["pt_date"].to_numpy() == d0)
        n_between = int(((ta > tk_us) & (ta < tr_us)).sum())
        day = c.filter(pl.col("pt_date") == d0)
        fc = day["t_call"].min() if day.height else None
        D_r = float(clk([tr_us])[0] - ak)
        rows.append(dict(unit=name, agent=int(a), t_k=t_k, t_r=t_r, turn_r=int(turn_r), read_day=rday,
                         D_r_min=D_r, D_r_wall_min=(t_r - t_k).total_seconds() / 60,
                         n_calls_before_30=int(before.sum()), active_before=bool(before.any()),
                         active_before_sameday=bool(same_day_before.any()),
                         n_calls_between=n_between, first_call_day=fc,
                         read_is_first_call=bool(fc is not None and t_r == fc),
                         read_on_kickoff_day=rday == d0))
    df = pl.DataFrame(rows)
    df = df.with_columns(((pl.col("D_r_min") >= L.DELAY_MIN) | (pl.col("n_calls_between") >= L.DELAY_CALLS)).alias("delayed"))
    df = df.with_columns((pl.col("active_before") & pl.col("delayed")).alias("delayed_active_reader"))
    dar = df.filter(pl.col("delayed_active_reader"))
    info.update(t_k=t_k.isoformat(), prev_day=pd_, prev_day_reserved=prev_reserved,
                n_readers=df.height, n_read_kickoff_day=int(df["read_on_kickoff_day"].sum()),
                n_active_before=int(df["active_before"].sum()), n_delayed=int(df["delayed"].sum()),
                n_delayed_active_readers=dar.height,
                n_read_is_first_call=int(df["read_is_first_call"].sum()),
                D_r_median_all=float(df["D_r_min"].median()), D_r_max_all=float(df["D_r_min"].max()),
                D_r_dar=sorted(round(x, 2) for x in dar["D_r_min"].to_list()),
                D_r_dar_iqr=(float(np.percentile(dar["D_r_min"], 75) - np.percentile(dar["D_r_min"], 25)) if dar.height else None),
                passes_precondition=dar.height >= L.MIN_READERS)
    return df, info


def main():
    cal = L.calendar()
    clk = L.Clock(cal)
    km = L.kickoff_messages()
    out = L.OUTD / "structure"
    out.mkdir(parents=True, exist_ok=True)
    allr, infos = [], []
    for name, goal, room in L.UNITS:
        df, info = unit_readers(name, goal, room, cal, clk, km)
        infos.append(info)
        if df.height:
            allr.append(df)
        print({k: info.get(k) for k in ("unit", "n_readers", "n_active_before", "n_delayed", "n_delayed_active_readers",
                                         "n_read_is_first_call", "prev_day_reserved", "D_r_median_all", "D_r_dar")})
    R = pl.concat(allr, how="diagonal_relaxed")
    R.write_parquet(out / "readers.parquet", compression="zstd")
    summ = {"built_at": dt.datetime.now(dt.timezone.utc).isoformat(), "git_commit": git_commit(),
            "rule": {"active_before_min": L.ACTIVE_BEFORE_MIN, "delay_min": L.DELAY_MIN, "delay_calls": L.DELAY_CALLS,
                     "min_readers": L.MIN_READERS},
            "units": infos, "n_units_pass": sum(bool(i.get("passes_precondition")) for i in infos)}
    (out / "units.json").write_text(json.dumps(summ, indent=1, default=str))
    prov = {"built_by": "hypotheses/H136-freeze-at-first-kickoff-read/scheme/structure.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["calendar", "kicks_classified", "call_windows", "context_ledger_items"]}],
            "params": summ["rule"], "built_at": summ["built_at"]}
    (L.OUTD / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print("units passing precondition:", summ["n_units_pass"])


if __name__ == "__main__":
    main()
