"""H48 shared helpers: paths, thread caps, holdout guard, period lists, active-time clock.

Every H48 script imports this first. It caps BLAS / polars threads at 2 (shared machine).
"""
from __future__ import annotations

import os

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
           "NUMEXPR_NUM_THREADS", "POLARS_MAX_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from functools import lru_cache  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
HDIR = ROOT / "hypotheses/H48-settling-mixing-time"
SH = ROOT / "data/processed/shared"
ED = SH / "embeddings"
OUT = ROOT / "data/processed/H48-settling-mixing-time"
H20 = ROOT / "data/processed/H20-content-aging"
H54 = ROOT / "data/processed/H54-kickoff-quench-target"
H31 = ROOT / "data/processed/H31-consensus-time-spectral-gap"
sys.path.insert(0, str(ROOT / "infra/shared"))
import common  # noqa: E402

CLAUDE_CODE = 19
SEED = 48_2026
UTC = dt.timezone.utc

# Replication layer (card "Candidate goal periods"): non-holdout, >= 5 active days.
REPLICATION = [4, 5, 6, 8, 10, 11, 12, 13, 16, 17, 18, 19, 20, 21, 24, 25, 26, 27, 30, 31, 35, 38, 39, 40, 41, 42, 51]
PREDICTORS_ONLY = {36: "crosses the 2026-03-24 regime boundary on day 2 (no settling)",
                   23: "kept blind for H10's confirmatory #22 -> #23 pair (H54 rule; no kickoff-alignment settling)"}
ALL_PERIODS = sorted(REPLICATION + list(PREDICTORS_ONLY))
NATIVE = ["NE42", "G38", "G51", "NE32"]
MAX_FIT_DAYS = 10          # settling fits use at most the first 10 active days


class HoldoutError(RuntimeError):
    pass


@lru_cache(maxsize=2)
def calendar(allow_holdout: bool = False) -> pl.DataFrame:
    cal = pl.read_parquet(SH / "calendar.parquet").with_columns(pl.col("regime").cast(pl.String))
    cal = cal.filter(pl.col("goal_no") > 0)
    ho = common.holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    cal = cal.with_columns(pl.Series("ho", ho))
    if not allow_holdout:
        cal = cal.filter(~pl.col("ho"))
    return cal.sort("pt_date")


def period_days(g: int, allow_holdout: bool = False) -> pl.DataFrame:
    c = calendar(allow_holdout).filter(pl.col("goal_no") == g).sort("pt_date")
    return c.with_row_index("day0")


def regime_of(g: int) -> str:
    c = calendar(True).filter(pl.col("goal_no") == g)
    return str(c["regime"][-1])


@lru_cache(maxsize=1)
def kickoff_times() -> dict:
    k = pl.read_parquet(H54 / "kickoffs.parquet").filter(pl.col("room").is_null())
    return dict(zip(k["goal_no"].to_list(), k["t0"].to_list()))


def kickoff_t0(g: int, allow_holdout: bool = False) -> dt.datetime:
    """Village kickoff message time (H54's table); fallback: the first window start of the period."""
    kt = kickoff_times().get(g)
    days = period_days(g, allow_holdout)
    if days.height == 0:
        raise HoldoutError(f"#{g}: no non-holdout days")
    first = days["win_start"][0]
    if kt is None or kt > days["win_end"][0] or kt < first - dt.timedelta(hours=12):
        return first
    return kt


def active_hours(t: pl.Series | np.ndarray, pt_date: pl.Series | list, g: int, allow_holdout: bool = False,
                 t0: dt.datetime | None = None) -> np.ndarray:
    """Active hours since the kickoff: active_offset_s(day) + clip(t - win_start, 0, window_s) - a(t0)."""
    days = period_days(g, allow_holdout)
    m = {d: (ws, w, off) for d, ws, w, off in zip(days["pt_date"], days["win_start"], days["window_s"],
                                                   days["active_offset_s"])}
    t0 = t0 or kickoff_t0(g, allow_holdout)
    d0 = days["pt_date"][0]
    ws0, w0, off0 = m[d0]
    a0 = off0 + min(max((t0 - ws0).total_seconds(), 0.0), w0)
    ts = pl.Series(t).to_list() if not isinstance(t, list) else t
    pds = list(pt_date)
    out = np.full(len(ts), np.nan)
    for k, (ti, pd_) in enumerate(zip(ts, pds)):
        r = m.get(pd_)
        if r is None or ti is None:
            continue
        ws, w, off = r
        out[k] = (off + min(max((ti - ws).total_seconds(), 0.0), w) - a0) / 3600.0
    return out


def active_hours_fast(t_us: np.ndarray, pt_date: np.ndarray, g: int, allow_holdout: bool = False,
                      t0: dt.datetime | None = None) -> np.ndarray:
    """Vectorized version: t_us = epoch microseconds (int64), pt_date = array of strings."""
    days = period_days(g, allow_holdout)
    t0 = t0 or kickoff_t0(g, allow_holdout)
    ws = days["win_start"].dt.epoch("us").to_numpy()
    w = days["window_s"].to_numpy().astype(float)
    off = days["active_offset_s"].to_numpy().astype(float)
    idx = {d: k for k, d in enumerate(days["pt_date"].to_list())}
    t0_us = int(t0.timestamp() * 1e6)
    a0 = off[0] + min(max((t0_us - ws[0]) / 1e6, 0.0), w[0])
    k = np.array([idx.get(d, -1) for d in pt_date])
    out = np.full(len(t_us), np.nan)
    ok = k >= 0
    kk = k[ok]
    out[ok] = (off[kk] + np.clip((t_us[ok] - ws[kk]) / 1e6, 0.0, w[kk]) - a0) / 3600.0
    return out


def hours_per_day(g: int) -> float:
    return float(np.median(period_days(g)["window_s"].to_numpy()) / 3600.0)


def guard_unit(g: int, allow_holdout: bool = False):
    held = set(common.load_holdout()["goal_periods_held_out"])
    if g in held and not allow_holdout:
        raise HoldoutError(f"#{g} is in the locked holdout")


def save_json(path: Path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)

    def conv(o):
        if isinstance(o, (np.floating,)):
            return None if not np.isfinite(o) else float(o)
        if isinstance(o, (np.integer,)):
            return int(o)
        if isinstance(o, np.ndarray):
            return [conv(x) for x in o.tolist()]
        if isinstance(o, float) and not np.isfinite(o):
            return None
        if isinstance(o, dict):
            return {str(k): conv(v) for k, v in o.items()}
        if isinstance(o, (list, tuple)):
            return [conv(x) for x in o]
        if isinstance(o, (dt.datetime, dt.date)):
            return o.isoformat()
        return o
    path.write_text(json.dumps(conv(obj), indent=1))


def load_json(path: Path):
    return json.loads(Path(path).read_text())
