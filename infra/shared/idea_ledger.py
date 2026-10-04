"""Idea timelines on the context ledger (shared by H61 and H62; written 2026-10-04 by the H61/H62 round-1 agent).

One goal period's chat timeline with everything an idea-spread analysis needs, in numpy arrays aligned to the
period's chat rows (chat_core row index `msg`, sorted by time):

  t (us), kind (0 agent, 1 human, 2 automated, 3 other), sender (agent code or -1), room, day index, message_id
  TS[m, a]  t_call (us) of agent a's earliest receiving call of message m (DQ1 ledger: context_ledger_items x
            call_windows); INF if a never read m
  cs[m]     for agent messages: t_call of the call that produced m (the sender's latest call with t_call < t_m,
            within 6 h; else t_m - 1 s, flagged in cs_fb)
  use_pos / use_marker / use_cls: uses of the period's novel ideas (H34 marker rule; data read from
            data/processed/H34-idea-cascades/markers/, hashes only)
  parent[m] position (in this period's rows) of m's DQ2 reply parent (reply_pairs: pair_set == cand & parent), or -1
  named[m]  roster agents m names (chat_mentions_clean.mentions_roster), as a list per row

This reproduces H34's round-1b visibility rule (scheme/h34core.py, H34_DATA=r1b) without importing H34 code.
Held-out days are excluded with common.holdout_mask and calendar.holdout before any table is read; the ledger join
asserts that no held-out call enters. No text is read.

  uv run python infra/shared/idea_ledger.py --verify      # reproduces H34 r1b first-use status for G38 and G20
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import datetime as dt  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from common import ROOT, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
MARKERS = ROOT / "data/processed/H34-idea-cascades/markers"
US = 1_000_000
INF_US = np.iinfo(np.int64).max // 4
GUARD_US = 1 * US
STALE_US = 6 * 3600 * US
KIND = {"agent": 0, "human": 1, "automated": 2}


def _us(s: pl.Series) -> np.ndarray:
    return s.dt.epoch("us").to_numpy().astype(np.int64)


class Base:
    """Tables shared by every period (loaded once)."""

    def __init__(self, markers: bool = True, allow_holdout: bool = False):
        self.allow_holdout = allow_holdout          # confirm scripts only: keeps held-out DQ2 parents
        self.cal = pl.read_parquet(SH / "calendar.parquet")
        self.chat = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "pt_date", "goal_no", "room",
                                                                       "speaker_kind", "agent", "length"]).with_row_index("msg")
        self.roster = pl.read_parquet(SH / "roster.parquet")
        self.cc = set(self.roster.filter(pl.col("claude_code"))["agent"].to_list())
        self.n_agents = int(self.roster["agent"].max()) + 1
        if markers:
            self.uses = pl.read_parquet(MARKERS / "uses.parquet")
            self.first_seen = pl.read_parquet(MARKERS / "first_seen.parquet")
        self._rp = None
        self._ment = None

    def period_days(self, g: int, allow_holdout: bool = False) -> list[str]:
        cal = self.cal.filter(pl.col("goal_no") == g)
        days = cal["pt_date"].to_list()
        if allow_holdout:
            return sorted(days)
        hm = holdout_mask(days, [g] * len(days))
        hflag = cal["holdout"].fill_null(False).to_list()
        return sorted(d for d, a, b in zip(days, hm, hflag) if not (a or b))

    @property
    def reply_parents(self) -> pl.DataFrame:
        if self._rp is None:
            self._rp = (pl.read_parquet(SH / "reply_pairs.parquet", columns=["b_msg", "a_msg", "pair_set", "parent",
                                                                            "holdout", "p_reply"])
                        .filter((pl.col("pair_set") == "cand") & pl.col("parent")
                                & (pl.lit(self.allow_holdout) | ~pl.col("holdout")))
                        .select("b_msg", "a_msg", "p_reply"))
        return self._rp

    @property
    def mentions(self) -> pl.DataFrame:
        if self._ment is None:
            self._ment = pl.read_parquet(SH / "chat_mentions_clean.parquet", columns=["message_id", "mentions_roster"])
        return self._ment


def ledger_arrays(chat: pl.DataFrame, t: np.ndarray, kind: np.ndarray, sender: np.ndarray, n_agents: int,
                  t0, t1, allow_holdout: bool = False) -> dict:
    """TS (n_msgs x n_agents) and cs (producing-call start per agent message): H34 round-1b rule."""
    mids = chat["message_id"].to_list()
    pos = pl.DataFrame({"message_id": mids, "pos": np.arange(len(mids), dtype=np.int64)})
    it = pl.scan_parquet(SH / "context_ledger_items.parquet").select("turn_id", "message_id").join(
        pos.lazy(), on="message_id", how="inner").collect()
    cw = (pl.scan_parquet(SH / "call_windows.parquet").select("turn_id", "agent", "t_call", "talk", "holdout")
          .filter((pl.col("t_call") >= t0) & (pl.col("t_call") <= t1)).collect())
    if not allow_holdout:
        assert not cw.filter(pl.col("turn_id").is_in(it["turn_id"].implode()))["holdout"].any(), \
            "holdout call in a ledger join"
    j = it.join(cw.select("turn_id", "agent", "t_call"), on="turn_id", how="inner")
    TS = np.full((len(mids), n_agents), INF_US, dtype=np.int64)
    if j.height:
        np.minimum.at(TS, (j["pos"].to_numpy(), j["agent"].to_numpy().astype(np.int64)), _us(j["t_call"]))
    cs = t - GUARD_US
    cfb = np.ones(len(t), dtype=bool)
    calls = {}
    for a in np.unique(sender[kind == 0]):
        if a < 0:
            continue
        ca = np.sort(_us(cw.filter(pl.col("agent") == int(a))["t_call"]))
        calls[int(a)] = ca
        idx = np.where((kind == 0) & (sender == a))[0]
        if len(ca) == 0:
            continue
        k = np.searchsorted(ca, t[idx], side="left") - 1
        ok = k >= 0
        ok &= (t[idx] - ca[np.clip(k, 0, None)]) <= STALE_US
        cs[idx[ok]] = ca[k[ok]]
        cfb[idx[ok]] = False
    return dict(TS=TS, cs=cs, cs_fb=cfb, n_ledger_items=int(j.height), calls=calls)


def load_period(base: Base, g: int, days: list[str] | None = None, allow_holdout: bool = False,
                ideas: np.ndarray | None = None, with_markers: bool = True) -> dict | None:
    """All arrays for goal period g (non-holdout days unless allow_holdout, which only confirm scripts may set)."""
    days = days if days is not None else base.period_days(g, allow_holdout=allow_holdout)
    if not days:
        return None
    if not allow_holdout:
        hm = holdout_mask(days, [g] * len(days))
        assert not any(hm), "held-out day requested without allow_holdout"
    chat = base.chat.filter((pl.col("goal_no") == g) & pl.col("pt_date").is_in(days)).sort("msg")
    if chat.height == 0:
        return None
    rows = chat["msg"].to_numpy().astype(np.int64)
    t = _us(chat["t"])
    kind = chat["speaker_kind"].cast(pl.Utf8).replace_strict(KIND, default=3).to_numpy().astype(np.int8)
    sender = chat["agent"].fill_null(-1).to_numpy().astype(np.int16)
    sender = np.where(kind == 0, sender, -1).astype(np.int16)
    day_idx = {d: i for i, d in enumerate(days)}
    t0 = chat["t"].min() - dt.timedelta(hours=8)
    t1 = chat["t"].max() + dt.timedelta(hours=1)
    out = dict(goal=g, days=days, rows=rows, t=t, kind=kind, sender=sender, cc=base.cc,
               room=chat["room"].fill_null(-1).to_numpy().astype(np.int16),
               day=np.array([day_idx[d] for d in chat["pt_date"].to_list()], dtype=np.int16),
               length=chat["length"].fill_null(0).to_numpy().astype(np.int64),
               message_id=chat["message_id"].to_list(), n_agents=base.n_agents)
    out.update(ledger_arrays(chat, t, kind, sender, base.n_agents, t0, t1, allow_holdout=allow_holdout))
    # DQ2 parents (positions within this period's rows)
    pos_of = {int(r): i for i, r in enumerate(rows)}
    rp = base.reply_parents.filter(pl.col("b_msg").is_in(rows))
    parent = np.full(len(rows), -1, dtype=np.int64)
    for b, a in zip(rp["b_msg"].to_list(), rp["a_msg"].to_list()):
        if int(a) in pos_of:
            parent[pos_of[int(b)]] = pos_of[int(a)]
    out["parent"] = parent
    ment = chat.select("message_id").join(base.mentions, on="message_id", how="left")
    out["named"] = [list(x) if x is not None else [] for x in ment["mentions_roster"].to_list()]
    if with_markers:
        if ideas is None:
            ideas = base.first_seen.filter(pl.col("first_goal") == g)["marker"].to_numpy()
        uses = base.uses.filter(pl.col("msg").is_in(rows) & pl.col("marker").is_in(ideas))
        out["use_pos"] = np.array([pos_of[int(m)] for m in uses["msg"].to_numpy()], dtype=np.int64)
        out["use_marker"] = uses["marker"].to_numpy().astype(np.int64)
        out["use_cls"] = uses["cls"].to_numpy().astype(np.int8)
    return out


def ideas_grouped(P: dict):
    """Yield (marker, cls, positions sorted by time) for each idea of the period."""
    order = np.lexsort((P["use_pos"], P["use_marker"]))
    um, up, uc = P["use_marker"][order], P["use_pos"][order], P["use_cls"][order]
    brk = np.r_[0, np.where(np.diff(um) != 0)[0] + 1, len(um)]
    for b in range(len(brk) - 1):
        lo, hi = brk[b], brk[b + 1]
        yield int(um[lo]), int(uc[lo]), up[lo:hi]


def first_uses(P: dict, pos: np.ndarray) -> dict:
    """{agent: position of its first use} for non-Claude-Code agents, among the idea's use positions `pos`."""
    fu = {}
    for p in pos:
        if P["kind"][p] == 0:
            a = int(P["sender"][p])
            if a >= 0 and a not in P["cc"] and a not in fu:
                fu[a] = int(p)
    return fu


def verify(goals=(38, 20)) -> bool:
    """Recompute H34 round-1b first-use status (seed / exposed / unexposed) and compare with H34's table."""
    base = Base()
    ok_all = True
    for g in goals:
        P = load_period(base, g)
        rows = []
        for mk, cl, pos in ideas_grouped(P):
            fu = first_uses(P, pos)
            first = int(pos[0])
            spk = np.where(P["kind"][pos] == 0, P["sender"][pos].astype(np.int64), -100 - P["kind"][pos])
            for a, u in fu.items():
                if u == first:
                    st = 0
                else:
                    vis = (P["TS"][pos, a] <= P["cs"][u]) & (spk != a)
                    st = 1 if vis.any() else 2
                rows.append((mk, a, st))
        mine = pl.DataFrame(rows, schema=["idea", "agent", "status_new"], orient="row")
        h34 = pl.read_parquet(ROOT / f"data/processed/H34-idea-cascades/r1b/G{g:02d}/first_uses.parquet",
                              columns=["idea", "agent", "status"])
        j = h34.join(mine, on=["idea", "agent"], how="full", coalesce=True)
        agree = float((j["status"] == j["status_new"]).mean())
        miss = int(j["status"].is_null().sum() + j["status_new"].is_null().sum())
        print(f"G{g:02d}: {h34.height} H34 first uses, {mine.height} recomputed, status agreement {agree:.4f}, "
              f"unmatched {miss}")
        ok_all &= agree > 0.999 and miss == 0
    print("verify:", "OK" if ok_all else "MISMATCH")
    return ok_all


if __name__ == "__main__":
    if "--verify" in sys.argv:
        sys.exit(0 if verify() else 1)
    print(__doc__)
