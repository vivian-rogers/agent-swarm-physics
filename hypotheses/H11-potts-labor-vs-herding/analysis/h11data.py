"""Load H11 processed labels into Snap objects (shared by explore.py and confirm_holdout.py)."""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scheme"))
import h11common as HC  # noqa: E402
import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import potts_core as P  # noqa: E402


def load_period(g, W=30, state="project", variant="merged", pool_rooms=False, qmax=None, base=None):
    """Return (snap, df) for period g. variant: 'merged' (labels 0..q, 0 neutral) or 'raw' (every project its own
    coupled state). state: 'project' or 'action'."""
    base = Path(base) if base else HC.OUT
    f = base / f"G{g:02d}"
    df = pl.read_parquet(f / f"labels_{state}_w{W}.parquet")
    if state == "projectact":
        state = "project"
    wins = pl.read_parquet(f / f"windows_w{W}.parquet").sort("day", "win").with_row_index("gwin")
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
