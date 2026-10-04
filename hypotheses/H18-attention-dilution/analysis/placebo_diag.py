"""Post-hoc diagnostic (added 2026-10-03 after P10 failed in regime I; not pre-registered).

Why are senders of *invisible* messages (arrived during the talk's own model call) mentioned above the non-pending
baseline? Two readings:
  (a) the call-start visibility rule is wrong (the message was visible);
  (b) mentions mark an ongoing dyad: i keeps addressing j because they are mid-exchange, whatever j just sent.
Stratify every candidate sender j at talk tau by engagement = (i mentioned j at its previous talk turn) and by status
(pending / invisible-only / other room-mates active that day). Under (b) the invisible excess disappears among
non-engaged senders; under (a) it persists.

  uv run python hypotheses/H18-attention-dilution/analysis/placebo_diag.py
Writes data/processed/H18-attention-dilution/placebo_diag.json.
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import json
import sys
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from periods import PERIODS, gname  # noqa: E402

ROOT = HERE.parents[2]
DATA = ROOT / "data/processed/H18-attention-dilution"
SH = ROOT / "data/processed/shared"


def run(gp, ment_by_msg, detectable):
    d = DATA / gp
    talks = pl.read_parquet(d / "talks.parquet").sort("agent", "t_us")
    pend = pl.read_parquet(d / "pending.parquet").filter(pl.col("scored"))
    inv = pl.read_parquet(d / "invisible.parquet")
    pend_s = pend.group_by("talk_id").agg(pl.col("sender").unique())
    inv_s = inv.group_by("talk_id").agg(pl.col("sender").unique())
    P = dict(zip(pend_s["talk_id"].to_list(), [set(x) for x in pend_s["sender"].to_list()]))
    I = dict(zip(inv_s["talk_id"].to_list(), [set(x) for x in inv_s["sender"].to_list()]))
    # active room-mates per (day, room): agents with talks in that room that day
    act = talks.group_by("pt_date", "room").agg(pl.col("agent").unique())
    A = {(r[0], r[1]): set(r[2]) for r in act.iter_rows()}
    cnt = {}
    prev_ment = {}
    for r in talks.iter_rows(named=True):
        a, tid = r["agent"], r["talk_id"]
        ment = ment_by_msg.get(r["msg"], set())
        key_prev = (a, r["pt_date"])
        pm = prev_ment.get(key_prev, set())
        pset, iset = P.get(tid, set()), I.get(tid, set())
        others = (A.get((r["pt_date"], r["room"]), set()) & detectable) - pset - iset - {a}
        for status, S in (("pending", pset), ("invisible", iset - pset), ("other", others)):
            for j in S:
                e = "engaged" if j in pm else "not_engaged"
                c = cnt.setdefault((status, e), [0, 0])
                c[0] += 1
                c[1] += int(j in ment)
        prev_ment[key_prev] = ment
    return {f"{s}|{e}": dict(n=v[0], rate=v[1] / v[0] if v[0] else None) for (s, e), v in sorted(cnt.items())}


def main():
    chat = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id"]).with_row_index("msg")
    men = pl.read_parquet(SH / "chat_mentions_clean.parquet", columns=["mentions_roster"])
    m = pl.concat([chat, men], how="horizontal")
    ment_by_msg = {int(i): set(x or []) for i, x in zip(m["msg"].to_list(), m["mentions_roster"].to_list())}
    sys.path.insert(0, str(ROOT / "infra/shared"))
    from common import mention_regexes
    ros = pl.read_parquet(SH / "roster.parquet")
    detectable = set(mention_regexes(ros.select(pl.col("agent").alias("id"), "name").to_dicts()).keys())
    out = {}
    for g in PERIODS:
        gp = gname(g)
        if (DATA / gp / "talks.parquet").exists():
            out[gp] = run(gp, ment_by_msg, detectable)
            o = out[gp]
            print(gp, {k: (v["n"], round(v["rate"], 3) if v["rate"] is not None else None) for k, v in o.items()})
    (DATA / "placebo_diag.json").write_text(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
