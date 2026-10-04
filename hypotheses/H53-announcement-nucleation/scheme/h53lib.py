"""H53 helpers: paths, calendar / active time, rooms, roster. Read-only imports from infra/shared."""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
HYP = ROOT / "hypotheses/H53-announcement-nucleation"
SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H53-announcement-nucleation"
sys.path.insert(0, str(ROOT / "infra/shared"))

from common import REVISION, git_commit, holdout_mask  # noqa: E402
from project_states import project_map  # noqa: E402

STRICT_HOW = ["url", "output", "bare"]
LINK_HOW = ["url", "bare"]
H_S = 7200          # pre-registered wave horizon (active seconds)
FU_S = 3600         # agent-level follow-up after own read-out (active seconds)
LOOKBACK_S = 1800   # commitment / activity look-back (active seconds)
W15 = 900
ROOMS_V1_US = int(np.datetime64("2026-02-25T00:00:00", "us").astype(np.int64))
SHIFTS_MIN = (-120, -60, -30, 30, 60, 120)


def load_cal() -> pl.DataFrame:
    """Every calendar day with active window, active offset, goal, regime and the holdout flag (holdout_mask)."""
    cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("n_agent_events") > 0)
    ho = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    return cal.with_columns(pl.Series("ho", ho)).select(
        "pt_date", "goal_no", pl.col("regime").cast(pl.String), "win_start", "win_end", "window_s", "active_offset_s", "ho")


def add_pt_date(df: pl.DataFrame, col: str = "t", out: str = "pt_date") -> pl.DataFrame:
    return df.with_columns(pl.col(col).dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias(out))


def add_active(df: pl.DataFrame, cal: pl.DataFrame, col: str = "t", out: str = "a", keep_goal: bool = False) -> pl.DataFrame:
    """Active time (s): active_offset_s + clip(t - win_start, 0, window_s) of t's PT day. Null if the day is not active."""
    tmp = add_pt_date(df, col, "_pd")
    c = cal.select(pl.col("pt_date").alias("_pd"), pl.col("win_start").alias("_ws"), pl.col("window_s").alias("_wl"),
                   pl.col("active_offset_s").alias("_ao"), pl.col("goal_no").alias("_g"), pl.col("ho").alias("_ho"))
    tmp = tmp.join(c, on="_pd", how="left")
    tmp = tmp.with_columns((pl.col("_ao") + ((pl.col(col) - pl.col("_ws")).dt.total_microseconds() / 1e6)
                            .clip(0, pl.col("_wl").cast(pl.Float64))).alias(out))
    keep = ["_pd", "_g", "_ho"] if keep_goal else []
    tmp = tmp.drop([c for c in ["_ws", "_wl", "_ao", "_pd", "_g", "_ho"] if c not in keep])
    if keep_goal:
        tmp = tmp.rename({"_pd": f"{out}_pt_date", "_g": f"{out}_goal", "_ho": f"{out}_ho"})
    return tmp


def room_lookup() -> dict:
    rt = pl.read_parquet(SH / "rooms_timeline.parquet").sort("agent", "t_start")
    tl = {}
    for (a,), sub in rt.group_by(["agent"], maintain_order=True):
        tl[int(a)] = (sub["t_start"].dt.epoch("us").to_numpy(), sub["room"].to_numpy().astype(np.int16))
    return tl


def room_at(tl: dict, a: int, t_us: np.ndarray) -> np.ndarray:
    """Agent a's room at times t (as-of backward, same rule as infra/shared/context_ledger.room_at); #general before rooms v1."""
    t = np.asarray(t_us, dtype=np.int64)
    out = np.full(len(t), -1, dtype=np.int16)
    if a in tl:
        ts, rm = tl[a]
        idx = np.searchsorted(ts, t, side="right") - 1
        out = np.where(idx >= 0, rm[np.clip(idx, 0, None)], -1).astype(np.int16)
    return np.where((out < 0) & (t < ROOMS_V1_US), 0, out).astype(np.int16)


def roster() -> pl.DataFrame:
    return pl.read_parquet(SH / "roster.parquet")


def on_roster(ro: pl.DataFrame, pt_date: str) -> list[int]:
    r = ro.filter(~pl.col("claude_code") & (pl.col("joined") <= pt_date) & (pl.col("left").is_null() | (pl.col("left") > pt_date)))
    return r["agent"].to_list()


def provenance(name: str, tables: list[str], params: dict, built_by: str, out: Path | None = None):
    import datetime as dt
    out = OUT if out is None else out
    out.mkdir(parents=True, exist_ok=True)
    p = out / "_provenance.json"
    prov = json.loads(p.read_text()) if p.exists() else {}
    prov[name] = {"built_by": built_by, "git_commit": git_commit(),
                  "inputs": [{"source": "ai-village", "revision": REVISION, "tables": tables}],
                  "params": params, "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    p.write_text(json.dumps(prov, indent=1))
