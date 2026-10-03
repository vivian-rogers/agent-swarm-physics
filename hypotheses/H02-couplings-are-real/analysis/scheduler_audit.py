"""Scheduler / turn-taking audit at event level (card, Observables 3), non-holdout chunk days only.

For every agent event (events_core agent rows + actions turns), the gap to the nearest event of a *different*
present agent. Compared with a baseline that circularly shifts each agent's event times within the day's
window (keeps each agent's own timing, destroys cross-agent alignment). A scheduler that lets one agent act at
a time leaves a deficit (ratio < 1) at small gaps; common triggering gives an excess (ratio > 1).
Output: data/processed/H02-couplings-are-real/scheduler_audit.parquet
"""
from __future__ import annotations

from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
DATA = ROOT / "data/processed/H02-couplings-are-real"
SHARED = ROOT / "data/processed/shared"
EDGES = np.array([0, 1, 2, 5, 10, 30, 60, 300])
NSHIFT = 20


def nearest_other(times_by_agent):
    """Gap from each event to the nearest event of another agent. times_by_agent: list of sorted arrays (s)."""
    allt = np.concatenate(times_by_agent)
    lab = np.concatenate([np.full(t.size, k) for k, t in enumerate(times_by_agent)])
    o = np.argsort(allt, kind="stable"); allt, lab = allt[o], lab[o]
    n = allt.size
    gaps = np.full(n, np.inf)
    # forward: next event of a different agent; scan with "last index of a different label" trick
    # for each position, nearest different-label neighbour to the right/left via run boundaries
    change = np.r_[True, lab[1:] != lab[:-1]]
    run_id = np.cumsum(change) - 1
    run_start = np.flatnonzero(change); run_end = np.r_[run_start[1:], n]  # [start, end)
    # left neighbour of different label = element just before the run start; right = element at run end
    left_idx = run_start[run_id] - 1
    right_idx = run_end[run_id]
    okl = left_idx >= 0; okr = right_idx < n
    gl = np.full(n, np.inf); gr = np.full(n, np.inf)
    gl[okl] = allt[okl] - allt[left_idx[okl]]
    gr[okr] = allt[right_idx[okr]] - allt[okr]
    return np.minimum(gl, gr)


def main():
    sp = pl.read_parquet(DATA / "spins.parquet").select("chunk", "regime", "mode", "pt_date", "agent").unique()
    days = sp.select("pt_date", "regime", "mode").unique()
    cal = pl.read_parquet(SHARED / "calendar.parquet").select("pt_date", "win_start", "win_end", "holdout")
    cal = cal.join(days, on="pt_date")
    assert not cal["holdout"].any()
    dl = cal["pt_date"].to_list()
    ev = (pl.scan_parquet(SHARED / "events_core.parquet")
          .filter(pl.col("pt_date").is_in(dl) & (pl.col("actor_kind") == "agent") & pl.col("agent").is_not_null())
          .select("t", "agent", (pl.col("action_type") == "AGENT_TALK").alias("talk")).collect())
    ev = ev.with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.Utf8).alias("pt_date"))
    ac = (pl.scan_parquet(SHARED / "actions.parquet").select("t", "agent").collect()
          .with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.Utf8).alias("pt_date"),
                        pl.lit(False).alias("talk"))
          .filter(pl.col("pt_date").is_in(dl)))
    allev = pl.concat([ev.select("t", "agent", "talk", "pt_date"), ac.select("t", "agent", "talk", "pt_date")])
    present = sp.select("pt_date", "agent").unique()
    allev = allev.join(present, on=["pt_date", "agent"], how="semi").join(cal, on="pt_date")
    allev = allev.filter((pl.col("t") >= pl.col("win_start")) & (pl.col("t") <= pl.col("win_end")))
    allev = allev.with_columns(((pl.col("t") - pl.col("win_start")).dt.total_microseconds() / 1e6).alias("x"),
                               ((pl.col("win_end") - pl.col("win_start")).dt.total_microseconds() / 1e6).alias("W"))
    rng = np.random.default_rng(20261003)
    rows = []
    for (d, reg, mode), g in allev.group_by(["pt_date", "regime", "mode"]):
        W = g["W"][0]
        for kind, gg in [("all", g), ("talk", g.filter(pl.col("talk")))]:
            tb = [np.sort(x["x"].to_numpy()) for _, x in gg.group_by("agent")]
            tb = [t for t in tb if t.size > 0]
            if len(tb) < 2:
                continue
            real = np.histogram(nearest_other(tb), EDGES)[0]
            base = np.zeros(EDGES.size - 1)
            for _ in range(NSHIFT):
                sh = [np.sort((t + rng.uniform(0, W)) % W) for t in tb]
                base += np.histogram(nearest_other(sh), EDGES)[0]
            base /= NSHIFT
            for k in range(EDGES.size - 1):
                rows.append({"pt_date": d, "regime": reg, "mode": mode, "kind": kind, "lo": EDGES[k], "hi": EDGES[k + 1],
                             "real": int(real[k]), "base": float(base[k]), "n_events": int(sum(t.size for t in tb))})
    out = pl.DataFrame(rows)
    out.write_parquet(DATA / "scheduler_audit.parquet")
    summ = (out.group_by("regime", "kind", "lo", "hi").agg(pl.col("real").sum(), pl.col("base").sum())
            .with_columns((pl.col("real") / pl.col("base")).round(3).alias("ratio")).sort("regime", "kind", "lo"))
    with pl.Config(tbl_rows=40):
        print(summ)


if __name__ == "__main__":
    main()
