"""H40 scheme: items, cadence and risk-set cells per goal period, from the shared tables only.

  uv run python hypotheses/H40-call-clock-coupling/scheme/build.py                 # all eligible periods
  uv run python hypotheses/H40-call-clock-coupling/scheme/build.py --period 38     # one period

Outputs (data/processed/H40-call-clock-coupling/G<NN>/):
  items.parquet    one row per (agent message, agent recipient) read-out, non-holdout: read-out call c1, t_m, W, rank,
                   batch, ment, unit, agent-unit code au, outcome calls r_tid (DQ2 parent), any_tid (labelled
                   p_reply >= 0.5), addr_tid (talk naming the sender), p_max. Codes only, no text, no message ids.
  cells.parquet    risk-set cells for the primary outcome (DQ2 parent), horizon 30 min (h40lib.aggregate)
  au.parquet       agent-unit codes
  cadence.parquet  per agent x unit call statistics (h40lib.cadence_table)
Holdout days never enter (items filtered on the call's holdout flag; cadence on non-holdout calls).
"""
from __future__ import annotations

import argparse
import sys
import time
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "analysis"))
import h40lib as L  # noqa: E402

MIN_RECV = 4
MIN_PARENTS = 100


def build_period(calls: L.Calls, goal: int, units: pl.DataFrame, btid: pl.DataFrame) -> dict | None:
    t0 = time.time()
    it = L.build_items(calls, goal, units, btid)
    if it.height == 0:
        return None
    n_par = int((it["r_tid"] >= 0).sum())
    n_recv = it["recv"].n_unique()
    info = dict(goal=goal, items=it.height, parents=n_par, recipients=n_recv,
                eligible=bool(n_recv >= MIN_RECV and n_par >= MIN_PARENTS))
    if not info["eligible"]:
        return info
    au = (it.select("recv", "unit_id").unique().sort(["unit_id", "recv"]).with_row_index("au")
          .with_columns(pl.col("au").cast(pl.Int32)))
    it = it.join(au, on=["recv", "unit_id"], how="left").sort("item")
    d = L.OUT / f"G{goal:02d}"
    d.mkdir(parents=True, exist_ok=True)
    keep = ["item", "c1", "sender", "recv", "t_m", "W", "rank", "ment", "uncertain", "k1", "day", "unit_id", "au",
            "r_tid", "any_tid", "addr_tid", "p_max", "goal_no"]
    it.select(keep).write_parquet(d / "items.parquet", compression="zstd")
    au.rename({"recv": "agent"}).write_parquet(d / "au.parquet", compression="zstd")
    cad = L.cadence_table(calls, goal, units)
    cad.write_parquet(d / "cadence.parquet", compression="zstd")
    # risk-set cells, chunked by day
    c1 = it["c1"].to_numpy()
    t_m = it["t_m"].to_numpy()
    rank = it["rank"].to_numpy().astype(np.int64)
    ment = it["ment"].to_numpy().astype(np.int64)
    day = it["day"].to_numpy()
    aucode = it["au"].to_numpy()
    rt = it["r_tid"].to_numpy()
    parts, n_rows = [], 0
    for dd in np.unique(day):
        s = np.flatnonzero(day == dd)
        rows = L.expand(calls, c1[s], t_m[s], rank[s])
        rows.item = s[rows.item]
        rows, y = L.truncate(rows, rt)
        n_rows += len(y)
        parts.append(L.aggregate(rows, y.astype(float), day, aucode, ment, rank))
    cells = L.merge_cells(parts)
    cells.write_parquet(d / "cells.parquet", compression="zstd")
    info.update(rows=n_rows, cells=cells.height, replies_in_window=float(cells["y"].sum()), secs=round(time.time() - t0, 1))
    return info


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", type=int, nargs="*")
    args = ap.parse_args()
    calls = L.load_calls()
    units = L.unit_map()
    btid = L._call_tid_of_messages(calls)
    print(f"B messages mapped to calls: exact {btid['b_exact'].mean():.3f}, any {(btid['b_tid'] >= 0).mean():.3f}",
          flush=True)
    goals = args.period or sorted(set(np.unique(calls.goal[~calls.holdout]).tolist()))
    infos = []
    for g in goals:
        info = build_period(calls, int(g), units, btid)
        if info:
            infos.append(info)
            print(info, flush=True)
    summ = L.OUT / "build_summary.parquet"
    new = pl.DataFrame(infos)
    if summ.exists() and args.period:
        old = pl.read_parquet(summ)
        new = pl.concat([old.filter(~pl.col("goal").is_in(new["goal"].to_list())), new], how="diagonal_relaxed")
    new.sort("goal").write_parquet(summ)
    L.write_provenance("scheme", "hypotheses/H40-call-clock-coupling/scheme/build.py",
                       ["call_windows", "context_ledger_turns", "context_ledger_items", "reply_pairs",
                        "reply_threading/b_meta_ledger", "reply_threading/msg_index", "chat_core",
                        "chat_mentions_clean", "period_units", "roster"],
                       dict(horizon_s=L.H_FIT_S, min_recipients=MIN_RECV, min_parents=MIN_PARENTS,
                            items="kind == agent, non-holdout, read-out call not first_of_day, not omitted",
                            outcome="DQ2 parent (cand, a_kind agent); sensitivity any p_reply>=0.5, addressing"))


if __name__ == "__main__":
    main()
