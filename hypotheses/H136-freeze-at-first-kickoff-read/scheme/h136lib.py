"""H136 shared library: kickoff units, active clock, kickoff read-out calls, delayed active readers.

Codes only; no message text is stored. Every call, mention and receipt row passes `holdout_mask` (reserved rows
dropped) before use. Terms follow physics-models/DEFINITIONS.md; the H136 variants (kickoff read-out call t_r,i, read
delay D_r, delayed active reader, freeze touch, post-read call lag K, freeze anchor) are defined in the card.
"""
from __future__ import annotations

import datetime as dt
import sys
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
SH = ROOT / "data/processed/shared"
OUTD = ROOT / "data/processed/H136-freeze-at-first-kickoff-read"
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import holdout_mask  # noqa: E402

SUMMARY_KINDS = ("consolidate", "session_start", "session_stop")   # H75's summary calls: not own decision calls
ACTIVE_BEFORE_MIN = 30.0      # delayed active reader: >= 1 own call in the 30 active min before t_k
DELAY_MIN = 2.0               # ... and D_r >= 2 active min
DELAY_CALLS = 2               # ... or >= 2 own calls in (t_k, t_r)
MIN_READERS = 5               # structural precondition per unit

# Candidate kickoff units (card, Design). Regime-I additions from H31 events_ep_w30 (frozen, t0_h <= 0.75 h):
# G18, G19, G26, G30. Room units in #38 and #44 (room 2 = #best, room 3 = #rest).
UNITS = [
    ("G18", 18, None), ("G19", 19, None), ("G26", 26, None), ("G30", 30, None), ("G31", 31, None),
    ("G33", 33, None), ("G35", 35, None), ("G36", 36, None),
    ("G37", 37, None), ("G38best", 38, 2), ("G38rest", 38, 3), ("G39", 39, None), ("G40", 40, None),
    ("G41", 41, None), ("G42", 42, None), ("G44best", 44, 2), ("G44rest", 44, 3),
]


def calendar() -> pl.DataFrame:
    c = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "win_start", "win_end", "goal_no"]).sort("pt_date")
    hm = holdout_mask(c["pt_date"].to_list(), c["goal_no"].to_list())
    c = c.with_columns(pl.Series("ho", hm),
                       ((pl.col("win_end") - pl.col("win_start")).dt.total_microseconds() / 6e7).alias("len_min"))
    return c.with_columns((pl.col("len_min").cum_sum() - pl.col("len_min")).alias("off_min"))


class Clock:
    """Active minutes: concatenated calendar windows (times are clamped into their PT day's window)."""

    def __init__(self, cal: pl.DataFrame | None = None):
        cal = calendar() if cal is None else cal
        self.ws = cal["win_start"].dt.epoch("us").to_numpy()
        self.we = cal["win_end"].dt.epoch("us").to_numpy()
        self.off = cal["off_min"].to_numpy()
        self.ln = cal["len_min"].to_numpy()

    def __call__(self, t_us) -> np.ndarray:
        t = np.atleast_1d(np.asarray(t_us, dtype=np.int64))
        k = np.searchsorted(self.ws, t, side="right") - 1          # last window starting at or before t
        k = np.clip(k, 0, len(self.ws) - 1)
        # times before a window start (e.g. a kickoff posted 1 min early) map to that window's start
        nxt = np.clip(k + 1, 0, len(self.ws) - 1)
        after_end = t > self.we[k]
        a = self.off[k] + np.minimum(np.maximum(t - self.ws[k], 0) / 6e7, self.ln[k])
        a = np.where(after_end & (nxt > k), self.off[nxt], a)
        return a


def us(x: dt.datetime) -> int:
    return int(x.timestamp() * 1_000_000)


def kickoff_messages() -> pl.DataFrame:
    """Non-reserved human kickoff messages (goal_fields rule via kicks_classified)."""
    k = pl.read_parquet(SH / "kicks_classified.parquet", columns=["t", "kind", "subkind", "room", "message_id", "goal_no",
                                                                   "pt_date", "holdout"])
    k = k.filter((pl.col("kind").cast(pl.String) == "human_message") & (pl.col("subkind").cast(pl.String) == "kickoff"))
    hm = holdout_mask(k["pt_date"].to_list(), k["goal_no"].to_list())
    return k.filter(~pl.Series(hm) & ~pl.col("holdout")).drop("kind", "subkind", "holdout")


def calls(days: list[str]) -> pl.DataFrame:
    """Own non-summary calls on the given days (reserved rows dropped)."""
    cw = (pl.scan_parquet(SH / "call_windows.parquet")
          .filter(pl.col("pt_date").is_in(days))
          .select("turn_id", "agent", "pt_date", "goal_no", "holdout", "kind", "ctx_mode", "t_call", "first_of_day")
          .collect())
    hm = holdout_mask(cw["pt_date"].to_list(), cw["goal_no"].to_list())
    cw = cw.filter(~pl.Series(hm) & ~pl.col("holdout"))
    return cw.filter(~pl.col("kind").cast(pl.String).is_in(list(SUMMARY_KINDS))).drop("holdout").sort(["agent", "t_call"])


def receipts(message_ids: list[str]) -> pl.DataFrame:
    """(message_id, agent, turn_id, t_call, pt_date) receiving calls from the DQ1 ledger; reserved calls dropped."""
    it = (pl.scan_parquet(SH / "context_ledger_items.parquet").filter(pl.col("message_id").is_in(message_ids))
          .select("turn_id", "message_id").collect())
    cw = (pl.scan_parquet(SH / "call_windows.parquet").filter(pl.col("turn_id").is_in(it["turn_id"].implode()))
          .select("turn_id", "agent", "t_call", "pt_date", "goal_no", "holdout").collect())
    hm = holdout_mask(cw["pt_date"].to_list(), cw["goal_no"].to_list())
    cw = cw.filter(~pl.Series(hm) & ~pl.col("holdout")).drop("holdout")
    return it.join(cw, on="turn_id")


def prev_day(cal: pl.DataFrame, d: str) -> str | None:
    p = cal.filter(pl.col("pt_date") < d)
    return p["pt_date"][-1] if p.height else None
