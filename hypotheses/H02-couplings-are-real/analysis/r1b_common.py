"""H02 round 1b (improved data, 2026-10-04): data-version switch and the DQ8 / H38 masks.

Data version (env var H02_DATA, read by every analysis script through `data_dir()`):
  r1        round-1 inputs: shared activity_bins (drops ~half of all events, DQ8) -> data/processed/H02-.../
  r1b       activity_bins_fixed + outages_fixed (reasons, scheduled minutes)     -> data/processed/H02-.../r1b/
Row masks (env var H02_MASK, applied in calibrate.load_chunks BEFORE any fit or surrogate):
  none      round-1 design (whole-day grid)
  trim      DQ8: the all-present window (no present agent before its first / after its last active minute)
  trim_stall  trim, then H38's explained joint-silence minutes removed (DQ8's `cw_gain_trim_h38mask`)
Outputs of a masked run go to <data_dir>/<mask>/ so every variant stays side by side.

The stall / imputation helpers are copied (frozen, read-only source) from
hypotheses/H38-platform-stalls/analysis/h38lib.py (`stall_flags`, `impute`, `MASK_SETS`), so a concurrent edit of
that file cannot change H02's numbers. Reason codes: 0 none, 1 pre, 2 post, 3 infra_err, 4 consol, 5 pause.
"""
from __future__ import annotations

import os
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[3]
BASE = ROOT / "data/processed/H02-couplings-are-real"
SH = ROOT / "data/processed/shared"

R_NONE, R_PRE, R_POST, R_INFRA, R_CONSOL, R_PAUSE = 0, 1, 2, 3, 4, 5
MASK_SETS = {"mask_edge": (R_PRE, R_POST), "mask_infra": (R_PRE, R_POST, R_INFRA),
             "mask_scaffold": (R_PRE, R_POST, R_INFRA, R_CONSOL), "mask_all": (R_PRE, R_POST, R_INFRA, R_CONSOL, R_PAUSE)}


def version() -> str:
    v = os.environ.get("H02_DATA", "r1")
    assert v in ("r1", "r1b"), v
    return v


def mask_kind() -> str:
    m = os.environ.get("H02_MASK", "none")
    assert m in ("none", "trim", "trim_stall"), m
    return m


def spins_dir() -> Path:
    """Where spins.parquet lives for the current data version."""
    return BASE if version() == "r1" else BASE / "r1b"


def data_dir() -> Path:
    """Where the current (version, mask) run reads and writes its result files."""
    d = spins_dir()
    m = mask_kind()
    d = d if m == "none" else d / m
    d.mkdir(parents=True, exist_ok=True)
    return d


def bins_path() -> Path:
    return SH / ("activity_bins.parquet" if version() == "r1" else "activity_bins_fixed.parquet")


# ------------------------------------------------------------------------------------------ H38 (copied)
def stall_flags(S: np.ndarray, R: np.ndarray, sched: np.ndarray, strict: bool = False) -> dict:
    """h38lib.stall_flags: K, joint silence js (K <= 1), explained (js & (sched | >= half of silent agents have a
    recorded reason))."""
    act = S > 0
    K = act.sum(1)
    sil = ~act
    nrec = (sil & (R > 0)).sum(1)
    n_sil = S.shape[1] - K
    js = K <= 1
    expl_r = (nrec >= n_sil - 1) if strict else (2 * nrec >= n_sil)
    return {"K": K, "js": js, "explained": js & (sched | expl_r)}


def impute(S: np.ndarray, R: np.ndarray, bid: np.ndarray, codes) -> np.ndarray:
    """h38lib.impute (agent-state conditioning): silent agent-minutes whose reason is in `codes` are set to the
    agent's mean spin over its available minutes of the same block, so synchronized scaffold states add no covariance."""
    X = S.astype(np.float64)
    un = np.isin(R, codes) & (S < 0)
    if not un.any():
        return X
    nb = int(bid.max()) + 1
    N = S.shape[1]
    av = ~un
    sums = np.zeros((nb, N)); cnt = np.zeros((nb, N))
    np.add.at(sums, bid, np.where(av, X, 0.0))
    np.add.at(cnt, bid, av.astype(np.float64))
    mean = np.where(cnt > 0, sums / np.maximum(cnt, 1), -1.0)
    X[un] = mean[bid][un]
    return X


def trim_mask(R: np.ndarray) -> np.ndarray:
    """DQ8 `nulls.all_present_window` on reason codes: no present agent is before its first or after its last active
    minute (R_PRE / R_POST are exactly those agent-minutes)."""
    return ~np.any((R == R_PRE) | (R == R_POST), axis=1)


def row_mask(S: np.ndarray, R: np.ndarray, sched: np.ndarray, kind: str | None = None) -> np.ndarray:
    kind = mask_kind() if kind is None else kind
    if kind == "none":
        return np.ones(S.shape[0], bool)
    keep = trim_mask(R)
    if kind == "trim_stall":
        keep &= ~stall_flags(S, R, sched)["explained"]
    return keep


def keep_runs(day: np.ndarray, keep: np.ndarray, min_rows: int = 10) -> np.ndarray:
    """Drop days with fewer than `min_rows` kept minutes (DQ8 rule)."""
    out = keep.copy()
    for d in np.unique(day):
        m = day == d
        if keep[m].sum() < min_rows:
            out[m] = False
    return out
