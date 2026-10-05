"""H52 round 2, R3: hand-coded role conflict (#51 non-reserved days). Prints coding sheets to the terminal (text in
memory only); codes are typed by the coder into CSV files that hold ids and codes, never text.

Subcommands
  sheet1 [--start i --n k]     pass-1 sheets for the human messages (instruction, recipient role, recipient's last <= 3
                               chat messages before the instruction). No outcome is shown.
  agentlist                    seeded random order of agent messages naming one other roster agent, with the directive
                               prefilter flag -> data/processed/H52-humans-loud-agents/r2/r3_agent_order.parquet (ids only)
  sheet1a [--start i --n k]    pass-1 sheets for prefiltered agent messages in that order
  sheet2 --file f [--start i --n k]  pass-2 sheets (what followed in 3 h) for the units listed in a pass-1 code file
  analyze                      statistics from analysis/r3_codes_pass1.csv and analysis/r3_codes_pass2.csv
Usage: uv run python hypotheses/H52-humans-loud-agents/analysis/r3_code.py sheet1 --start 0 --n 15
"""
from __future__ import annotations

import argparse
import datetime as dt
import gzip
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h52lib as L  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

SH = L.SH
GOAL = 51
HYP = L.HYP / "analysis"
R3OUT = L.OUT / "r2"
PRE_RX = re.compile(r"\b(stop|instead|switch|pause|please|can you|could you|should|don't|do not|need you|focus on|"
                    r"make sure|go ahead|let's|try to|start|move to|work on)\b", re.I)
UTC = dt.timezone.utc


def days():
    d = L.period_days(GOAL)
    L.assert_no_holdout(d, GOAL)
    return d


def names():
    r = pl.read_parquet(SH / "roster.parquet")
    return dict(zip(r["agent"].to_list(), r["name"].to_list())), dict(zip(r["agent_id"].to_list(), r["agent"].to_list()))


def roles():
    """agent -> list of (start, end, short_name, goal text) from the raw agent goals (role text; read in memory)."""
    _, aid = names()
    out = {}
    with gzip.open(L.ROOT / "data/raw/ai-village/agent_goals.jsonl.gz", "rt") as f:
        for line in f:
            r = json.loads(line)
            a = aid.get(r["agent_id"])
            if a is None:
                continue
            out.setdefault(a, []).append((str(r["start_time"]), str(r["end_time"]), r["short_name"], r["name"],
                                          str(r.get("description"))))
    return out


def role_at(rl, a, t):
    best = None
    for s, e, sn, nm, desc in rl.get(a, []):
        if s <= t.strftime("%Y-%m-%d %H:%M:%S") and (e in ("None", "") or t.strftime("%Y-%m-%d %H:%M:%S") < e):
            best = (sn, nm, desc)
    return best


def chat_frame():
    d = days()
    cc = pl.read_parquet(SH / "chat_core.parquet").filter((pl.col("goal_no") == GOAL) & pl.col("pt_date").is_in(d))
    cm = pl.read_parquet(SH / "chat_mentions_clean.parquet", columns=["message_id", "mentions_roster"])
    kc = pl.read_parquet(SH / "kicks_classified.parquet", columns=["message_id", "subkind"])
    return cc.join(cm, on="message_id", how="left").join(kc, on="message_id", how="left")


def texts(ids):
    t = pl.read_parquet(SH / "chat_text.parquet", columns=["message_id", "text"]).filter(pl.col("message_id").is_in(list(ids)))
    return dict(zip(t["message_id"].to_list(), t["text"].to_list()))


def clip(s, n):
    s = (s or "").replace("\n", " ")
    return s if len(s) <= n else s[:n] + " [...]"


def prior_msgs(cc, a, t, k=3):
    return cc.filter((pl.col("agent") == a) & (pl.col("t") < t)).sort("t").tail(k)


def human_units():
    cc = chat_frame()
    h = cc.filter((pl.col("speaker_kind") == "human") & (pl.col("subkind").cast(pl.Utf8) != "kickoff")).sort("t")
    return cc, h


def print_unit(cc, rl, nm, mid, t, room, text, targets, kind, compact=False):
    tl, pl_, kp = (380, 150, 2) if compact else (1800, 400, 3)
    print(f"=== {kind} {mid[:8]} | {t:%Y-%m-%d %H:%M} | room {room} | named {[f'{a}:{nm.get(a)}' for a in targets]}")
    print("TEXT:", clip(text, tl))
    if len(targets) > 6:
        print("  (broadcast-size name list)")
        return
    for a in targets:
        ro = role_at(rl, a, t)
        print(f"  -> {a} {nm.get(a)} | role: {ro[0] if ro else None} :: {clip(ro[1], 300 if not compact else 90) if ro else ''}")
        pm = prior_msgs(cc, a, t, kp)
        tx = texts(pm["message_id"].to_list())
        for r in pm.iter_rows(named=True):
            print(f"     before {int((t - r['t']).total_seconds() // 60)} min: {clip(tx.get(r['message_id']), pl_)}")


def sheet1(start, n):
    cc, h = human_units()
    nm, _ = names()
    rl = roles()
    sub = h.slice(start, n)
    tx = texts(sub["message_id"].to_list())
    for i, r in enumerate(sub.iter_rows(named=True)):
        tg = [int(a) for a in (r["mentions_roster"] or [])]
        print(f"\n[#{start + i}]", end=" ")
        print_unit(cc, rl, nm, r["message_id"], r["t"], r["room"], tx.get(r["message_id"]), tg, "HUMAN")


def agentlist():
    cc = chat_frame()
    a = cc.filter((pl.col("speaker_kind") == "agent") & (pl.col("mentions_roster").list.len() == 1))
    a = a.filter(pl.col("mentions_roster").list.first() != pl.col("agent").cast(pl.Int64))
    tx = texts(a["message_id"].to_list())
    pre = np.array([bool(PRE_RX.search(tx.get(m) or "")) for m in a["message_id"].to_list()])
    rng = np.random.default_rng(5203)
    order = rng.permutation(a.height)
    out = a.select("message_id", "t", "agent", pl.col("mentions_roster").list.first().alias("target")).with_columns(
        pl.Series("prefilter", pre))[order].with_row_index("order")
    R3OUT.mkdir(parents=True, exist_ok=True)
    out.write_parquet(R3OUT / "r3_agent_order.parquet")
    print("agent messages naming one other agent:", a.height, "prefiltered:", int(pre.sum()))
    # same flag on human units
    _, h = human_units()
    ht = texts(h["message_id"].to_list())
    hp = pl.DataFrame({"message_id": h["message_id"], "prefilter": [bool(PRE_RX.search(ht.get(m) or "")) for m in h["message_id"]]})
    hp.write_parquet(R3OUT / "r3_human_prefilter.parquet")
    print("human messages prefiltered:", int(hp["prefilter"].sum()), "of", hp.height)


def sheet1a(start, n):
    cc = chat_frame()
    nm, _ = names()
    rl = roles()
    o = pl.read_parquet(R3OUT / "r3_agent_order.parquet").filter(pl.col("prefilter")).sort("order").slice(start, n)
    tx = texts(o["message_id"].to_list())
    room = dict(zip(cc["message_id"].to_list(), cc["room"].to_list()))
    for i, r in enumerate(o.iter_rows(named=True)):
        print(f"\n[a#{start + i}] from {r['agent']} ({(role_at(rl, r['agent'], r['t']) or ['?'])[0]})", end=" ")
        print_unit(cc, rl, nm, r["message_id"], r["t"], room.get(r["message_id"]), tx.get(r["message_id"]), [int(r["target"])], "AGENT",
                   compact=True)


# ============================================================================ pass 2
def receiving_call(mid, a):
    it = pl.scan_parquet(SH / "context_ledger_items.parquet").filter(pl.col("message_id") == mid).select("turn_id").collect()
    tu = pl.scan_parquet(SH / "context_ledger_turns.parquet").filter(pl.col("turn_id").is_in(it["turn_id"].implode()) & (pl.col("agent") == a)).select(
        "t_call").collect()
    return tu["t_call"].min() if tu.height else None


def sheet2(file, start, n):
    cc = chat_frame()
    nm, _ = names()
    c1 = pl.read_csv(HYP / file).filter(pl.col("directive") == 1).slice(start, n)
    cmd = pl.read_parquet(SH / "artifact_commands_text.parquet", columns=["t", "agent", "act", "cmd", "out_urls"])
    wc = pl.read_parquet(SH / "work_commits.parquet", columns=["repo", "t", "author_agent", "author_kind", "automated", "canonical",
                                                                "imported", "holdout"]).filter(
        pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind").cast(pl.Utf8) == "agent") & ~pl.col("automated") & ~pl.col("holdout"))
    for r in c1.iter_rows(named=True):
        mid, a = r["message_id"], int(r["target"])
        t0 = receiving_call(mid, a)
        tm = cc.filter(pl.col("message_id") == mid)["t"]
        tm = tm[0] if tm.len() else None
        if t0 is None:
            t0 = tm
        t1 = t0 + dt.timedelta(hours=3)
        print(f"\n=== unit {r['unit']} | {mid} -> {a}:{nm.get(a)} | received {t0:%Y-%m-%d %H:%M} UTC")
        print("INSTRUCTION:", clip(texts([mid]).get(mid), 900))
        after = cc.filter((pl.col("agent") == a) & (pl.col("t") >= t0) & (pl.col("t") <= t1)).sort("t")
        tx = texts(after["message_id"].to_list())
        for x in after.head(12).iter_rows(named=True):
            print(f"   chat +{int((x['t'] - t0).total_seconds() // 60)} min: {clip(tx.get(x['message_id']), 350)}")
        if after.height > 12:
            print(f"   ... {after.height - 12} more chat messages")
        cm = cmd.filter((pl.col("agent") == a) & (pl.col("t") >= t0) & (pl.col("t") <= t1)).sort("t")
        for x in cm.head(15).iter_rows(named=True):
            print(f"   cmd +{int((x['t'] - t0).total_seconds() // 60)} min [{x['act']}]: {clip(x['cmd'], 160)}")
        if cm.height > 15:
            print(f"   ... {cm.height - 15} more commands")
        w = wc.filter((pl.col("author_agent") == a) & (pl.col("t") >= t0) & (pl.col("t") <= t1))
        wb = wc.filter((pl.col("author_agent") == a) & (pl.col("t") >= t0 - dt.timedelta(hours=3)) & (pl.col("t") < t0))
        print(f"   commits 3h after: {w.height} {sorted(set(w['repo'].cast(pl.Utf8).to_list()))[:6]} | 3h before: {wb.height} "
              f"{sorted(set(wb['repo'].cast(pl.Utf8).to_list()))[:6]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd")
    ap.add_argument("--start", type=int, default=0)
    ap.add_argument("--n", type=int, default=15)
    ap.add_argument("--file", default="r3_codes_pass1.csv")
    a = ap.parse_args()
    if a.cmd == "sheet1":
        sheet1(a.start, a.n)
    elif a.cmd == "agentlist":
        agentlist()
    elif a.cmd == "sheet1a":
        sheet1a(a.start, a.n)
    elif a.cmd == "sheet2":
        sheet2(a.file, a.start, a.n)


if __name__ == "__main__":
    main()
