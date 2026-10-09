"""H147 shared helpers (scheme and analysis): paths, the #51 day list, 2-h bins, active-time coordinates, windows.

Every frame this module returns is restricted to #51 non-reserved days (07-06 -> 09-04); the reserved tail 51m
(09-07 -> 09-18) is masked with common.holdout_mask and asserted absent.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from functools import lru_cache  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
HYP = ROOT / "hypotheses/H147-egregore-value-and-hosts-51"
SHARED = ROOT / "data/processed/shared"
ED = SHARED / "embeddings"
OUT = ROOT / "data/processed/H147-egregore-value-and-hosts-51"
H145_OUT = ROOT / "data/processed/H145-ideology-egregores-51"
SCRATCH = Path("/private/tmp/claude-501/-Users-wrogers-Documents-school-fun-agenttesting/"
               "015f2aa2-05c1-4a7e-ba6c-25bf6c9d1344/scratchpad")
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask, git_commit, REVISION  # noqa: E402

GOAL = 51
FIRST, LAST = "2026-07-06", "2026-09-04"
BIN_S = 7200                       # 2-h bins (H145's default bin; memeplex.make_bins)
CLAUDE_CODE = 19
UTC = dt.timezone.utc
# H143 windows (robustness splits; also the "window" in the own-repo rule)
WINDOWS = [("A", "2026-07-06", "2026-07-16"), ("B", "2026-07-17", "2026-07-28"), ("C", "2026-07-29", "2026-08-04"),
           ("D", "2026-08-05", "2026-08-23"), ("E", "2026-08-24", "2026-09-04")]


def ts(s: str) -> dt.datetime:
    return dt.datetime.fromisoformat(s).replace(tzinfo=UTC) if "+" not in s else dt.datetime.fromisoformat(s)


def window_of(pt_date: str) -> str:
    for w, a, b in WINDOWS:
        if a <= pt_date <= b:
            return w
    return "?"


@lru_cache(maxsize=1)
def days() -> pl.DataFrame:
    """#51 non-reserved active days: pt_date, win_start, win_end, day_idx, weekday, a0 (active seconds before the day),
    unit_id, window, n_bins."""
    cal = pl.read_parquet(SHARED / "calendar.parquet").filter(pl.col("goal_no") == GOAL)
    cal = cal.filter(~pl.Series(holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())))
    cal = cal.filter((pl.col("pt_date") >= FIRST) & (pl.col("pt_date") <= LAST)).sort("pt_date")
    assert cal["pt_date"].max() <= LAST and not cal["holdout"].any()
    pu = pl.read_parquet(SHARED / "period_units.parquet").filter(pl.col("goal_no") == GOAL)
    d2u = {d: u for u, ds in zip(pu["unit_id"], pu["days"]) for d in ds}
    win = (cal["win_end"] - cal["win_start"]).dt.total_seconds().to_numpy()
    a0 = np.r_[0, np.cumsum(win)[:-1]]
    return cal.select("pt_date", "win_start", "win_end", "weekday").with_columns(
        pl.int_range(pl.len()).cast(pl.Int16).alias("day_idx"),
        pl.Series("a0", a0, dtype=pl.Float64), pl.Series("win_s", win, dtype=pl.Float64),
        pl.col("pt_date").replace_strict(d2u, default=None).alias("unit_id"),
        pl.col("pt_date").map_elements(window_of, return_dtype=pl.String).alias("window"),
        pl.Series("n_bins", np.ceil(win / BIN_S).astype(np.int16)))


@lru_cache(maxsize=1)
def mbins():
    """memeplex.Bins at 2 h (H145's bins: 16:00 UTC anchor, 4 bins of 2 h per day, DQ8 per-agent presence trim)."""
    import memeplex as MP
    b = MP.make_bins(GOAL, BIN_S // 60, days=days()["pt_date"].to_list())
    assert b.days[-1] <= LAST
    return b


@lru_cache(maxsize=1)
def bins() -> pl.DataFrame:
    """Global 2-h bins (H145's): bin, pt_date, k (bin in day), t0, t1, unit_id, window, day_idx."""
    mb = mbins()
    d = days()
    df = pl.DataFrame({"bin": np.arange(mb.nB, dtype=np.int32),
                       "pt_date": [mb.days[i] for i in mb.day_of_bin],
                       "k": mb.bin_in_day.astype(np.int8),
                       "t0": mb.t0}).with_columns(pl.col("t0").dt.replace_time_zone("UTC"))
    df = df.with_columns((pl.col("t0") + pl.duration(seconds=BIN_S)).alias("t1"))
    return df.join(d.select("pt_date", "unit_id", "window", "day_idx"), on="pt_date", how="left")


def assign_bins(df: pl.DataFrame, tcol: str = "t") -> pl.DataFrame:
    """Add `bin` and `k` (H145's 2-h bins); rows outside every bin (before 16:00 UTC, after the 8-h day) get null."""
    b = bins()
    t0 = b["t0"].dt.epoch("us").to_numpy()
    t = df[tcol].dt.epoch("us").to_numpy()
    pos = np.searchsorted(t0, t, side="right") - 1
    ok = (pos >= 0) & (t < t0[np.clip(pos, 0, None)] + BIN_S * 10**6)
    binv = np.where(ok, pos, -1)
    kk = b["k"].to_numpy()
    return df.with_columns(pl.Series("k", np.where(ok, kk[np.clip(pos, 0, None)], -1).astype(np.int8)).replace(-1, None),
                           pl.Series("bin", binv.astype(np.int32)).replace(-1, None))


def active_time(t_us: np.ndarray) -> np.ndarray:
    """Active seconds since the start of #51 (village-off gaps removed); times between windows map to the window
    end before them."""
    d = days()
    ws = d["win_start"].dt.epoch("us").to_numpy()
    we = d["win_end"].dt.epoch("us").to_numpy()
    a0 = d["a0"].to_numpy()
    i = np.clip(np.searchsorted(ws, t_us, side="right") - 1, 0, len(ws) - 1)
    off = np.clip(t_us - ws[i], 0, we[i] - ws[i]) / 1e6
    return a0[i] + off


def from_active(a: np.ndarray) -> np.ndarray:
    """Inverse of active_time (epoch us)."""
    d = days()
    ws = d["win_start"].dt.epoch("us").to_numpy()
    a0 = d["a0"].to_numpy()
    i = np.clip(np.searchsorted(a0, a, side="right") - 1, 0, len(a0) - 1)
    return (ws[i] + (a - a0[i]) * 1e6).astype(np.int64)


def provenance(name: str, built_by: str, tables: list[str], params: dict | None = None, extra: dict | None = None):
    OUT.mkdir(parents=True, exist_ok=True)
    path = OUT / "_provenance.json"
    prov = json.loads(path.read_text()) if path.exists() else {}
    prov[name] = {"built_by": built_by, "git_commit": git_commit(),
                  "inputs": [{"source": "ai-village", "revision": REVISION, "tables": tables}],
                  "params": params or {}, "built_at": dt.datetime.now(UTC).isoformat(), **(extra or {})}
    path.write_text(json.dumps(prov, indent=1, default=str))
