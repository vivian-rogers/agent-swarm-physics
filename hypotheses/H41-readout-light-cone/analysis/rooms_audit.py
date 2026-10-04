"""H41 round 1b: which periods does the room-index fix change? (2026-10-04)

  uv run python hypotheses/H41-readout-light-cone/analysis/rooms_audit.py

For every eligible period, builds the round-1 room index (open rooms_timeline segments dropped, H41_ROOMS=old) and
the fixed one, and compares RoomIndex lookups:
  - hazard lookups: every (source message t0, present agent) pair -> the agent's room at t0 (sets in_room0, J_in, J_mh);
  - adoption lookups: room_t0 of every stored round-1 adoption (sets `cross`), and rooms_in(agent, t0, t_use)
    (sets h_room and the room cone).
Reads only call_windows times, rooms_timeline and the round-1 tables in round1/ (or G<NN>/ for unaffected periods).
Writes results/rooms_audit.json. Holdout days are excluded (calendar.hold, as in load_skeleton).
"""
from __future__ import annotations

import json
import os
import sys
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent / "scheme"))
import h41core as C  # noqa: E402

OUT = C.OUT
R1 = OUT / "round1"


class _Sk:
    def __init__(self, rooms):
        self.rooms = rooms


def lookups(ri: C.RoomIndex, agents, t: np.ndarray) -> np.ndarray:
    """Room of each agent (rows) at each time (columns), vectorised RoomIndex.at."""
    out = np.full((len(agents), len(t)), -1, dtype=np.int64)
    pre = t < C.ROOMS_START
    for k, a in enumerate(agents):
        v = ri.by.get(int(a))
        if v is None:
            out[k, pre] = 0
            continue
        i = np.searchsorted(v[0], t, side="right") - 1
        r = np.where(i >= 0, v[2][np.maximum(i, 0)], -1)
        out[k] = np.where(pre, 0, r)
    return out


def audit(goal: int, cal: pl.DataFrame) -> dict:
    days = cal.filter((pl.col("goal_no") == goal) & ~pl.col("hold"))["pt_date"].to_list()
    cc = C.cc_agents()
    cw = (pl.scan_parquet(C.SH / "call_windows.parquet")
          .filter(pl.col("pt_date").is_in(days) & ~pl.col("holdout") & (pl.col("ctx_mode") != "summary")
                  & ~pl.col("agent").is_in(cc))
          .select("agent", C.ts("t_call").alias("t")).collect())
    t_min, t_max = float(cw["t"].min()), float(cw["t"].max())
    agents = np.unique(cw["agent"].to_numpy())
    ri_old = C.RoomIndex(_Sk(C.rooms_table(t_min, t_max, "old")))
    ri_new = C.RoomIndex(_Sk(C.rooms_table(t_min, t_max, "fixed")))
    src = R1 if (R1 / f"G{goal:02d}").exists() else OUT
    items = pl.read_parquet(src / f"G{goal:02d}/items.parquet").unique("m0").select("t0", "room0", "src")
    t0 = items["t0"].to_numpy()
    r0 = items["room0"].to_numpy()
    s0 = items["src"].to_numpy()
    lo, ln = lookups(ri_old, agents, t0), lookups(ri_new, agents, t0)
    valid = agents[:, None] != s0[None, :]
    rooms_era = (t0 >= C.ROOMS_START)[None, :] & valid
    ch = (lo != ln) & valid
    inr_o, inr_n = (lo == r0[None, :]), (ln == r0[None, :])
    res = dict(goal=goal, n_lookups=int(valid.sum()), n_lookups_rooms_era=int(rooms_era.sum()),
               share_room_changed=float(ch.sum() / valid.sum()) if valid.sum() else 0.0,
               share_in_room0_changed=float(((inr_o != inr_n) & valid).sum() / valid.sum()) if valid.sum() else 0.0,
               n_in_room0_old=int((inr_o & valid).sum()), n_in_room0_new=int((inr_n & valid).sum()))
    # adoptions: room_t0 and rooms_in
    p = src / f"G{goal:02d}/adoptions.parquet"
    if p.exists():
        adf = pl.read_parquet(p, columns=["agent", "t0", "t_use", "room0", "room_t0"])
        a_ = adf["agent"].to_numpy()
        ta, tu, rr0 = adf["t0"].to_numpy(), adf["t_use"].to_numpy(), adf["room0"].to_numpy()
        rt0_old = np.array([ri_old.at(a, t) for a, t in zip(a_, ta)])
        rt0_new = np.array([ri_new.at(a, t) for a, t in zip(a_, ta)])
        stored = adf["room_t0"].to_numpy()
        cross_o = (rt0_old != rr0) & (rt0_old >= 0)
        cross_n = (rt0_new != rr0) & (rt0_new >= 0)
        rin_o = [ri_old.rooms_in(a, x, y) for a, x, y in zip(a_, ta, tu)]
        rin_n = [ri_new.rooms_in(a, x, y) for a, x, y in zip(a_, ta, tu)]
        res.update(n_adopt=adf.height, adopt_reproduces_round1=bool(np.array_equal(stored, rt0_old)),
                   share_adopt_room_t0_changed=float(np.mean(rt0_old != rt0_new)) if adf.height else 0.0,
                   share_adopt_cross_changed=float(np.mean(cross_o != cross_n)) if adf.height else 0.0,
                   n_cross_old=int(cross_o.sum()), n_cross_new=int(cross_n.sum()),
                   share_adopt_rooms_in_changed=float(np.mean([x != y for x, y in zip(rin_o, rin_n)])) if adf.height else 0.0)
    return res


def main():
    cal = C.calendar()
    goals = sorted(int(d.name[1:]) for d in OUT.glob("G[0-9][0-9]") if (d / "items.parquet").exists())
    out = []
    for g in goals:
        r = audit(g, cal)
        out.append(r)
        print(json.dumps(r), flush=True)
    (OUT / "results").mkdir(exist_ok=True)
    (OUT / "results/rooms_audit.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
