"""H58 loader: builds h58lib.Unit panels from data/processed/H58-coordinated-superagents/ (non-holdout only)."""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
D = ROOT / "data/processed/H58-coordinated-superagents"
SH = ROOT / "data/processed/shared"
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "infra/shared"))
import h58lib as L  # noqa: E402
from common import holdout_mask  # noqa: E402

_CACHE = {}


def set_base(path):
    """Point the loader at another panel directory (the confirmatory script's holdout panels); clears the cache."""
    global D
    D = Path(path)
    _CACHE.clear()


def units_meta():
    return json.loads((D / "units.json").read_text())


def _tables():
    if not _CACHE:
        _CACHE["commits"] = pl.read_parquet(D / "commits.parquet")
        _CACHE["exog"] = pl.read_parquet(D / "exog.parquet")
        _CACHE["content"] = pl.read_parquet(D / "content.parquet")
        _CACHE["rooms"] = pl.read_parquet(D / "rooms.parquet")
        _CACHE["presence"] = pl.read_parquet(D / "presence.parquet")
        _CACHE["layers"] = pl.read_parquet(D / "layers.parquet")
        _CACHE["repos"] = pl.read_parquet(D / "repos.parquet")
    return _CACHE


ALLOW_HOLDOUT = False   # set only by analysis/confirm.py behind its two flags


def assert_no_holdout(meta):
    if ALLOW_HOLDOUT:
        return
    for x in meta:
        assert not any(holdout_mask(x["days"], [x["goal_no"]] * len(x["days"]))), x["unit"]


def load_unit(name: str, bin_min: int = 30, commits: pl.DataFrame | None = None, repo_col="repo_id") -> L.Unit:
    """Allocation panel for one unit of analysis at the given bin width."""
    meta = {x["unit"]: x for x in units_meta()}[name]
    assert_no_holdout([meta])
    T = _tables()
    cm = (T["commits"] if commits is None else commits).filter(pl.col("unit") == name)
    # bins per day
    nb_day = []
    for ws, we in zip(meta["win_start"], meta["win_end"]):
        w = (dt.datetime.fromisoformat(we) - dt.datetime.fromisoformat(ws)).total_seconds() / 60
        nb_day.append(int(np.ceil(w / bin_min)))
    offs = np.concatenate([[0], np.cumsum(nb_day)])
    nB = int(offs[-1])
    day_of_bin = np.repeat(np.arange(len(nb_day)), nb_day)
    agents = sorted(cm["agent"].unique().to_list())
    apos = {a: i for i, a in enumerate(agents)}
    repos = sorted(cm[repo_col].unique().to_list())
    rpos = {r: i for i, r in enumerate(repos)}
    nA, nR = len(agents), len(repos)
    b = (offs[cm["day"].to_numpy()] + (cm["m"].to_numpy() // bin_min)).astype(int)
    b = np.minimum(b, offs[cm["day"].to_numpy() + 1] - 1)
    ai = np.array([apos[a] for a in cm["agent"].to_list()])
    ri = np.array([rpos[r] for r in cm[repo_col].to_list()])
    cnt = np.zeros((nA, nB, nR), np.int32)
    np.add.at(cnt, (ai, b, ri), 1)
    N = cnt.sum(2)
    # dominant repo; ties -> the latest commit in the bin
    S = np.where(N > 0, cnt.argmax(2), -1)
    tie = (cnt == cnt.max(2, keepdims=True)).sum(2) > 1
    if tie.any():
        order = np.argsort(cm["m"].to_numpy(), kind="stable")
        last = {}
        for t in order:
            last[(ai[t], b[t])] = ri[t]
        for (a_, b_) in zip(*np.nonzero(tie & (N > 0))):
            S[a_, b_] = last[(a_, b_)]
    Wn = np.zeros((nA, nR), np.int64)
    np.add.at(Wn, (ai, ri), 1)
    # exogenous input
    ex = T["exog"].filter(pl.col("unit") == name)
    yh = np.zeros(nB, bool)
    if ex.height:
        eb = (offs[ex["day"].to_numpy()] + (ex["m"].to_numpy() // bin_min)).astype(int)
        eb = np.minimum(eb, offs[ex["day"].to_numpy() + 1] - 1)
        yh[eb] = True
    # content clusters (30-min windows; mapped by bin midpoint)
    C = np.full((nA, nB), -1, np.int64)
    co = T["content"].filter((pl.col("unit") == name) & pl.col("agent").is_in(agents))
    for (a, d, w, c) in co.select("agent", "day", "win30", "cluster").iter_rows():
        lo = int((w * 30) // bin_min)
        hi = int(((w + 1) * 30 - 1) // bin_min)
        for bb in range(lo, hi + 1):
            if bb < nb_day[d]:
                C[apos[a], offs[d] + bb] = c
    # rooms at 30-min bins mapped to this width
    Rm = np.full((nA, nB), -1, np.int64)
    ro = T["rooms"].filter((pl.col("unit") == name) & pl.col("agent").is_in(agents))
    for (a, d, b30, room) in ro.select("agent", "day", "bin30", "room").iter_rows():
        lo = int((b30 * 30) // bin_min)
        hi = int(((b30 + 1) * 30 - 1) // bin_min)
        for bb in range(lo, hi + 1):
            if bb < nb_day[d]:
                Rm[apos[a], offs[d] + bb] = room
    U = L.Unit(name, meta["regime"], agents, repos, day_of_bin, S, N, yh, C=C, rooms=Rm,
               extra={"Wn": Wn, "offs": offs, "nb_day": nb_day, "goal_no": meta["goal_no"], "days": meta["days"],
                      "bin_min": bin_min})
    return U


def layer_rows(name: str):
    T = _tables()
    return T["layers"].filter(pl.col("unit") == name).select("i", "j", *L.LAYERS).rows()


def modal_rooms(U: L.Unit) -> dict:
    """Time-weighted modal room per agent over the unit (bins with a known room)."""
    out = {}
    for a in range(U.nA):
        r = U.rooms[a][U.rooms[a] >= 0]
        if len(r):
            v, c = np.unique(r, return_counts=True)
            out[a] = int(v[c.argmax()])
    return out


def labs() -> dict:
    ro = pl.read_parquet(SH / "roster.parquet").select("agent", "lab")
    return dict(ro.iter_rows())
