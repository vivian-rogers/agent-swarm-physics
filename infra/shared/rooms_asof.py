"""Room of an agent at a time ("room of each statement"): as-of lookup on rooms_timeline with open rooms closed at +inf.

Moved from H100 and H102 (`scheme/build.py`: `rooms_timeline`, `statement_rooms`; byte-for-byte the same rule in both;
round-3 consolidation, STANDARDS §8, 2026-10-04). The hypothesis copies stay in place.

Rule:
- `rooms_timeline` rows are (agent, room, t_start, t_last, t_end). The open (current) stay of an agent has a null
  `t_end`; it is filled with FAR (2100-01-01 UTC), i.e. +inf (infra Known issues: filtering on `t_end` without the fill
  silently drops open rooms and makes as-of lookups return the previous room, H41).
- room at (agent, t): the stay with the latest `t_start <= t` (backward as-of join by agent), kept only if `t < t_end`;
  otherwise null (gap between stays, or t before the agent's first stay). Ties on `t_start` follow polars' backward
  join_asof (the last row of the tie in (agent, t_start) order), exactly as H100/H102.
- statements: chat rows (`kind == "chat"`) keep their message room (`room`); every other kind (intentions) gets the
  as-of room (`room_at`).
Nothing here reads holdout-flagged rows on its own: callers filter their statements first.

Functions:
  rooms_timeline(path=None)        -> rooms_timeline with null t_end -> FAR, sorted by (agent, t_start)
  room_asof(df, t="t", agent="agent", out="room_rt")   -> df with the as-of room column (row order kept)
  statement_rooms(st)              -> H100/H102 `statement_rooms`: adds `room_at`; keeps st's row order
  room_at_us(agent, t_us)          -> numpy lookup for one agent (int16, -1 = no stay), for loops over calls

Verify: uv run python infra/shared/rooms_asof.py --verify
  (1) statement_rooms on every non-holdout shared statement equals H100's and H102's functions (read-only imports);
  (2) H102's statements.parquet `room_at` equals a recomputation; (3) H100's agent_days room / room_share / n_rooms equal
  a recomputation from the shared rule.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt  # noqa: E402
import importlib.util  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from functools import lru_cache  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SH = ROOT / "data/processed/shared"
FAR = dt.datetime(2100, 1, 1, tzinfo=dt.timezone.utc)


def rooms_timeline(path: Path | None = None) -> pl.DataFrame:
    """rooms_timeline with null t_end filled by FAR (+inf), sorted by (agent, t_start)."""
    return (pl.read_parquet(path or SH / "rooms_timeline.parquet")
            .with_columns(pl.col("t_end").fill_null(pl.lit(FAR).cast(pl.Datetime("us", "UTC"))))
            .sort("agent", "t_start"))


def room_asof(df: pl.DataFrame, t: str = "t", agent: str = "agent", out: str = "room_rt",
              rt: pl.DataFrame | None = None) -> pl.DataFrame:
    """Add the as-of room (null outside every stay) to df, keeping df's row order."""
    rt = rooms_timeline() if rt is None else rt
    r = rt.select(pl.col("agent").alias(agent), pl.col("t_start").alias(t), pl.col("room").alias("__room"),
                  pl.col("t_end").alias("__t_end"))
    if r.schema[agent] != df.schema[agent]:
        r = r.with_columns(pl.col(agent).cast(df.schema[agent]))
    s = df.with_row_index("__row").sort(agent, t)
    j = s.join_asof(r, on=t, by=agent, strategy="backward", check_sortedness=False)
    j = j.with_columns(pl.when(pl.col(t) < pl.col("__t_end")).then(pl.col("__room")).otherwise(None).alias(out))
    return j.sort("__row").drop("__row", "__room", "__t_end")


def statement_rooms(st: pl.DataFrame, rt: pl.DataFrame | None = None) -> pl.DataFrame:
    """Room of every statement: chat = message room; other kinds = as-of rooms_timeline (t_start <= t < t_end).
    st needs kind, agent, t, room. Returns st (same row order) with `room_at` added."""
    j = room_asof(st, "t", "agent", "__room_rt", rt)
    return j.with_columns(pl.when(pl.col("kind") == "chat").then(pl.col("room")).otherwise(pl.col("__room_rt"))
                          .alias("room_at")).drop("__room_rt")


@lru_cache(maxsize=1)
def _lookup() -> dict:
    rt = rooms_timeline()
    out = {}
    for (a,), sub in rt.group_by(["agent"], maintain_order=True):
        out[int(a)] = (sub["t_start"].dt.epoch("us").to_numpy(), sub["t_end"].dt.epoch("us").to_numpy(),
                       sub["room"].to_numpy())
    return out


def room_at_us(agent: int, t_us: np.ndarray) -> np.ndarray:
    """Same rule for one agent on epoch-µs times (int16 room codes, -1 = no stay). Ties on t_start: last row."""
    t_us = np.asarray(t_us, dtype=np.int64)
    tl = _lookup().get(int(agent))
    if tl is None:
        return np.full(len(t_us), -1, dtype=np.int16)
    ts, te, rm = tl
    idx = np.searchsorted(ts, t_us, side="right") - 1
    ok = (idx >= 0) & (t_us < te[np.clip(idx, 0, None)])
    return np.where(ok, rm[np.clip(idx, 0, None)], -1).astype(np.int16)


# ---------------------------------------------------------------------------------------------- verify
def _load(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def verify() -> dict:
    from common import holdout_mask  # noqa: E402
    res, ok = {}, True
    st = pl.read_parquet(SH / "embeddings/statements.parquet").with_row_index("srow")
    st = st.filter(~pl.col("holdout"))
    st = st.filter(pl.Series(~np.array(holdout_mask(st["pt_date"].to_list(), st["goal_no"].fill_null(-1).to_list()))))
    mine = statement_rooms(st)
    res["statements_checked"] = mine.height
    res["room_at_null_share"] = float(mine["room_at"].is_null().mean())
    for h, rel in (("H100", "hypotheses/H100-room-symmetry-breaking/scheme/build.py"),
                   ("H102", "hypotheses/H102-room-domain-walls/scheme/build.py")):
        mod = _load(ROOT / rel, f"{h.lower()}_scheme_ro")
        if h == "H100":   # H100 adds (and drops) its own row index `srow`, so it gets the frame without one
            theirs = mod.statement_rooms(st.drop("srow")).with_columns(st["srow"])
        else:             # H102 sorts by the shared `srow` (the frame is already srow-ordered)
            theirs = mod.statement_rooms(st)
        same = theirs["room_at"].equals(mine["room_at"]) and theirs["srow"].equals(mine["srow"])
        res[f"{h}_statement_rooms"] = "identical" if same else \
            f"differ in {int((theirs['room_at'] != mine['room_at']).sum())} rows"
        ok &= same
    # numpy lookup agrees with the polars rule on intentions
    it = mine.filter(pl.col("kind") != "chat")
    npv = np.concatenate([room_at_us(a, g["t"].dt.epoch("us").to_numpy())
                          for (a,), g in it.group_by(["agent"], maintain_order=True)])
    pv = np.concatenate([g["room_at"].fill_null(-1).to_numpy() for _, g in it.group_by(["agent"], maintain_order=True)])
    res["room_at_us_vs_polars"] = "identical" if np.array_equal(npv, pv) else f"differ in {int((npv != pv).sum())}"
    ok &= np.array_equal(npv, pv)
    # on-disk outputs
    p102 = ROOT / "data/processed/H102-room-domain-walls/statements.parquet"
    if p102.exists():
        d = pl.read_parquet(p102, columns=["srow", "room_at"])
        m = d.join(mine.select("srow", pl.col("room_at").alias("mine")), on="srow", how="left")
        n_bad = int((m["room_at"].fill_null(-99) != m["mine"].fill_null(-99)).sum())
        res["H102_statements_parquet"] = "identical" if n_bad == 0 else f"{n_bad} of {d.height} differ"
        ok &= n_bad == 0
    p100 = ROOT / "data/processed/H100-room-symmetry-breaking/agent_days.parquet"
    if p100.exists():
        roster = pl.read_parquet(SH / "roster.parquet")
        cc = roster.filter(pl.col("claude_code"))["agent"].to_list()
        s = mine.filter(pl.col("goal_no").is_in(list(range(33, 52))) & ~pl.col("agent").is_in(cc))
        rd = (s.drop_nulls("room_at").group_by("agent", "pt_date", "room_at").len()
              .sort(["agent", "pt_date", "len", "room_at"], descending=[False, False, True, False]))
        room_day = rd.group_by("agent", "pt_date", maintain_order=True).agg(
            pl.col("room_at").first().alias("room_m"), (pl.col("len").first() / pl.col("len").sum()).alias("share_m"),
            pl.len().alias("n_rooms_m"))
        d = pl.read_parquet(p100, columns=["agent", "pt_date", "room", "room_share", "n_rooms"])
        m = d.join(room_day, on=["agent", "pt_date"], how="left")
        bad = m.filter((pl.col("room").fill_null(-99) != pl.col("room_m").fill_null(-99))
                       | (pl.col("n_rooms").fill_null(-1) != pl.col("n_rooms_m").fill_null(-1))
                       | ((pl.col("room_share") - pl.col("share_m")).abs().fill_null(0) > 1e-12))
        res["H100_agent_days_room"] = "identical" if bad.height == 0 else f"{bad.height} of {d.height} differ"
        ok &= bad.height == 0
    res["ok"] = bool(ok)
    print(json.dumps(res, indent=1))
    return res


if __name__ == "__main__":
    sys.path.insert(0, str(HERE))
    if "--verify" in sys.argv:
        sys.exit(0 if verify()["ok"] else 1)
    print(__doc__)
