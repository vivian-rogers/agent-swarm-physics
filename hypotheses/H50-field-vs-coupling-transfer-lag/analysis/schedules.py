"""Real input schedules (bookends, human messages, nudges) for the synthetic swarms. Inputs only, non-holdout."""
from __future__ import annotations

import datetime as dt
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
SH = ROOT / "data/processed/shared"
BASE = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)


def secs(col):
    return (col.dt.epoch("us").to_numpy() / 1e6) - BASE.timestamp()


def real_schedule(days: list[str], N: int, seed: int = 0, rooms=None):
    """Calendar windows and exogenous inputs of real days; real target agents mapped at random onto N synthetic
    agents (consistently within a day). rooms: synthetic room per agent (inputs keep room 0 unless two rooms)."""
    rng = np.random.default_rng(seed)
    cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("pt_date").is_in(days)).sort("pt_date")
    assert not cal["holdout"].any(), "holdout day in a synthetic schedule"
    k = pl.read_parquet(SH / "kicks_classified.parquet").filter(pl.col("pt_date").is_in(days),
                                                                pl.col("kind").is_in(["human_message", "nudge", "pause_resume"]))
    w0, w1 = secs(cal["win_start"]), secs(cal["win_end"])
    out_days = list(zip(w0, w1))
    inputs = []
    tk = secs(k["t"])
    for r, t in zip(k.iter_rows(named=True), tk):
        kind = {"human_message": "human", "nudge": "nudge"}.get(r["kind"], r["subkind"])
        tg = r["targets"] or []
        mp = {}
        tgs = []
        for a in tg:
            if a not in mp:
                mp[a] = int(rng.integers(N))
            tgs.append(mp[a])
        room = 0
        if rooms is not None and kind in ("human", "nudge"):
            room = int(rng.integers(max(rooms) + 1)) if not tgs else int(rooms[tgs[0]])
        if kind in ("resume", "pause"):
            room = -1
        inputs.append((float(t), kind, room, tuple(tgs)))
    # days without a resume bookend get an 'edge' input at the window start
    for (a, b) in out_days:
        if not any(kd == "resume" and a - 900 <= t <= b for (t, kd, _, _) in inputs):
            inputs.append((float(a), "edge", -1, ()))
    inputs.sort()
    return dict(days=out_days, inputs=inputs)
