"""Load H11 processed labels into Snap objects (shared by explore.py and confirm_holdout.py).

Label source switch (round 1b, 2026-10-04): H11_LABELS=h11 (default; round 1's own files in
data/processed/H11-potts-labor-vs-herding/G<NN>/) or H11_LABELS=shared (scheme/build_r1b.py's files in .../r1b/G<NN>/:
shared deterministic project_states, deterministic action classes, and the new work-ledger state `work`).
An explicit `base` argument overrides both. The environment variable is read at call time, so spawned workers see it."""
from __future__ import annotations

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h11common as HC  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import potts_core as P  # noqa: E402


def label_base() -> Path:
    src = os.environ.get("H11_LABELS", "h11")
    if src not in ("h11", "shared"):
        raise ValueError(f"H11_LABELS must be 'h11' or 'shared', not {src!r}")
    return HC.OUT / "r1b" if src == "shared" else HC.OUT


def load_period(g, W=30, state="project", variant="merged", pool_rooms=False, qmax=None, base=None, pt_dates=None):
    """Return (snap, df) for period g. variant: 'merged' (labels 0..q, 0 neutral) or 'raw' (every project its own
    coupled state). state: 'project' or 'action'."""
    base = Path(base) if base else label_base()
    f = base / f"G{g:02d}"
    df = pl.read_parquet(f / f"labels_{state}_w{W}.parquet")
    if state in ("projectact", "work"):
        state = "project"
    wins = pl.read_parquet(f / f"windows_w{W}.parquet")
    if pt_dates is not None:  # round 1b: one period unit (a subset of the period's days)
        df = df.filter(pl.col("pt_date").is_in(list(pt_dates)))
        wins = wins.filter(pl.col("pt_date").is_in(list(pt_dates)))
        dmap = wins.select("pt_date").unique().sort("pt_date").with_row_index("day_u").with_columns(pl.col("day_u").cast(pl.Int16))
        wins = wins.join(dmap, on="pt_date").drop("day").rename({"day_u": "day"})
        df = df.join(dmap, on="pt_date").drop("day").rename({"day_u": "day"})
    wins = wins.sort("day", "win").with_row_index("gwin")
    df = df.join(wins.select("day", "win", "gwin"), on=["day", "win"], how="left")
    if state == "project" and variant == "raw":
        ranks = df.group_by("project").agg(pl.len().alias("n")).sort(["n", "project"], descending=[True, False]).with_row_index("r")
        df = df.join(ranks.select("project", (pl.col("r") + 1).cast(pl.Int64).alias("lab")), on="project")
        S = int(df["lab"].max()) + 1
        coupled = np.ones(S, bool)
        coupled[0] = False  # state 0 unused
        lab = df["lab"].to_numpy()
    elif state == "project":
        lab = df["label"].to_numpy().astype(np.int64)
        if qmax is not None:
            lab = np.where(lab > qmax, 0, lab)
        S = int(max(lab.max(), 1)) + 1
        coupled = np.ones(S, bool)
        coupled[0] = False
    else:
        lab = df["label"].to_numpy().astype(np.int64)
        S = 6
        coupled = np.ones(S, bool)
        coupled[0] = False  # class 0 never stored
    room = np.zeros(df.height, dtype=np.int64) if pool_rooms else df["room"].to_numpy().astype(np.int64)
    day_len = wins.group_by("day").agg(pl.len().alias("K")).sort("day")["K"].to_numpy()
    s = P.snap_from_arrays(df["agent"].to_numpy(), lab, df["day"].to_numpy(), df["win"].to_numpy(), S, coupled, room=room,
                           day_len=day_len[np.unique(df["day"].to_numpy())] if df.height else None)
    s.gwin = df["gwin"].to_numpy()
    s.agent_codes = np.unique(df["agent"].to_numpy())
    return s, df


def blocks_ge(snap, n=3):
    return int((snap.N >= n).sum())
