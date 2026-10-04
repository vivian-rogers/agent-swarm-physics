"""H65 scheme: per non-holdout goal period, the target statements and their ledger read sets (DQ1), plus the
in-flight unread sets and DQ2 reply parents. Codes, times and vector-row indices only (no text, no vectors).

    uv run python hypotheses/H65-leaders-are-routers/scheme/build.py [--period G26 | --all]

Writes data/processed/H65-leaders-are-routers/G<NN>/{targets,reads}.parquet and _provenance.json.
Rules are the card's (written 2026-10-04 19:35 UTC, before any H65 outcome statistic).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "4")

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H65-leaders-are-routers"
WIN_S = 2700.0     # read window: 45 min (3 tau)
UTC = dt.timezone.utc


ALLOW_HOLDOUT = False   # set only by analysis/confirm.py under --confirm (writes to confirm_build/)


def statements(goal: int) -> pl.DataFrame:
    st = pl.read_parquet(SH / "embeddings/statements.parquet").with_row_index("srow").filter(
        (pl.col("kind") == "chat") & (pl.col("goal_no") == goal) & (ALLOW_HOLDOUT | ~pl.col("holdout"))
        & (pl.col("agent") >= 0))
    ci = pl.read_parquet(SH / "embeddings/chat_index.parquet").with_row_index("cidx")
    st = st.join(ci, left_on="src_row", right_on="cidx", how="left").with_columns(cidx=pl.col("src_row"))
    if ALLOW_HOLDOUT:
        return st.sort("t")
    hm = holdout_mask(st["pt_date"].to_list(), st["goal_no"].to_list())
    return st.filter(~pl.Series(hm)).sort("t")


def build(goal: int) -> dict:
    st = statements(goal)
    if st.height == 0:
        return {"goal": goal, "skipped": "no statements"}
    calls = pl.read_parquet(SH / "call_windows.parquet", columns=["turn_id", "agent", "pt_date", "goal_no", "holdout",
                                                                  "t_call"])
    calls = calls.filter((pl.col("goal_no") == goal) & (ALLOW_HOLDOUT | ~pl.col("holdout")))
    # producing call: the author's last call with t_call <= t_B on the same PT day
    tg = st.select("srow", "message_id", "cidx", "agent", "t", "pt_date", "room", "goal_no").sort("t").join_asof(
        calls.select(pl.col("agent"), pl.col("t_call"), pl.col("turn_id"), pl.col("pt_date").alias("call_day"))
        .sort("t_call"), left_on="t", right_on="t_call", by="agent", strategy="backward")
    tg = tg.with_columns(pl.when(pl.col("call_day") == pl.col("pt_date")).then(pl.col("t_call")).otherwise(None)
                         .alias("t_call")).drop("call_day")
    # DQ2 parents (agent authors only)
    rp = pl.read_parquet(SH / "reply_pairs.parquet", columns=["B_message_id", "a_agent", "a_kind", "parent",
                                                               "pair_set", "labelled", "b_agent", "goal_no"])
    rp = rp.filter((pl.col("goal_no") == goal) & (pl.col("pair_set") == "cand") & pl.col("labelled")
                   & pl.col("parent") & (pl.col("a_kind") == 0) & (pl.col("a_agent") >= 0)
                   & (pl.col("a_agent") != pl.col("b_agent"))).select(
        pl.col("B_message_id").alias("message_id"), pl.col("a_agent").alias("parent_agent")).unique("message_id")
    tg = tg.join(rp, on="message_id", how="left").with_row_index("tgt")
    # ledger reads: items at the recipient's calls (agent and human senders)
    items = pl.read_parquet(SH / "context_ledger_items.parquet", columns=["turn_id", "message_id", "sender", "kind",
                                                                          "omitted"])
    items = items.join(calls.select("turn_id", pl.col("agent").alias("recv")), on="turn_id", how="inner").filter(
        ~pl.col("omitted") & pl.col("kind").cast(pl.String).is_in(["agent", "human"]))
    cc = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "goal_no", "pt_date"])
    items = items.join(cc.select("message_id", pl.col("t").alias("t_a")), on="message_id", how="left")
    ci = pl.read_parquet(SH / "embeddings/chat_index.parquet").with_row_index("cidx")
    sall = pl.read_parquet(SH / "embeddings/statements.parquet").with_row_index("srow").filter(
        pl.col("kind") == "chat").select("srow", pl.col("src_row").alias("cidx"))
    items = items.join(ci, on="message_id", how="left").join(sall, on="cidx", how="left")
    items = items.with_columns(is_h=(pl.col("kind").cast(pl.String) == "human")).filter(
        (pl.col("is_h") | pl.col("srow").is_not_null()) & pl.col("t_a").is_not_null())
    # the read sets
    rows_t, rows_k, rows_s, rows_v, rows_age = [], [], [], [], []
    ta_ns = items["t_a"].dt.epoch("us").to_numpy() / 1e6
    by_recv = {}
    recv = items["recv"].to_numpy()
    for a in np.unique(recv):
        idx = np.flatnonzero(recv == a)
        o = idx[np.argsort(ta_ns[idx], kind="stable")]
        by_recv[int(a)] = o
    snd = items["sender"].fill_null(-1).to_numpy()
    ish = items["is_h"].to_numpy()
    vrow = np.where(ish, items["cidx"].fill_null(-1).to_numpy(), items["srow"].fill_null(-1).to_numpy())
    tB = tg["t"].dt.epoch("us").to_numpy() / 1e6
    tC = tg["t_call"].dt.epoch("us").fill_null(np.nan).to_numpy() / 1e6
    ag = tg["agent"].to_numpy()
    for k in range(tg.height):
        if not np.isfinite(tC[k]):
            continue
        o = by_recv.get(int(ag[k]))
        if o is None:
            continue
        ts = ta_ns[o]
        lo = np.searchsorted(ts, tB[k] - WIN_S, "left")
        hi = np.searchsorted(ts, tC[k], "left")
        if hi <= lo:
            continue
        sel = o[lo:hi]
        sel = sel[snd[sel] != ag[k]]
        rows_t.append(np.full(len(sel), k))
        rows_k.append(ish[sel].astype(np.int8))
        rows_s.append(snd[sel])
        rows_v.append(vrow[sel])
        rows_age.append(tB[k] - ta_ns[sel])
    # in-flight unread: same-room agent statements posted in [t_call, t_B) by others
    room = tg["room"].to_numpy()
    srow_all = tg["srow"].to_numpy()
    for r in np.unique(room):
        idx = np.flatnonzero(room == r)
        ts = tB[idx]
        for k in idx:
            if not np.isfinite(tC[k]):
                continue
            lo = np.searchsorted(ts, tC[k], "left")
            hi = np.searchsorted(ts, tB[k], "left")
            if hi <= lo:
                continue
            sel = idx[lo:hi]
            sel = sel[ag[sel] != ag[k]]
            if len(sel) == 0:
                continue
            rows_t.append(np.full(len(sel), k))
            rows_k.append(np.full(len(sel), 2, np.int8))
            rows_s.append(ag[sel])
            rows_v.append(srow_all[sel])
            rows_age.append(tB[k] - tB[sel])
    reads = pl.DataFrame({"tgt": np.concatenate(rows_t).astype(np.int32),
                          "src_kind": np.concatenate(rows_k).astype(np.int8),
                          "sender": np.concatenate(rows_s).astype(np.int16),
                          "vrow": np.concatenate(rows_v).astype(np.int64),
                          "age_s": np.concatenate(rows_age).astype(np.float32)})
    pu = pl.read_parquet(SH / "period_units.parquet").select("unit_id", "goal_no", "start")
    tg = tg.sort("t").join_asof(pu.filter(pl.col("goal_no") == goal).drop("goal_no").sort("start"),
                                left_on="t", right_on="start", strategy="backward").drop("start").sort("tgt")
    d = (OUT / "confirm_build" if ALLOW_HOLDOUT else OUT) / f"G{goal:02d}"
    d.mkdir(parents=True, exist_ok=True)
    tg.select("tgt", "srow", "cidx", "agent", "t", "pt_date", "room", "unit_id", "t_call", "turn_id",
              "parent_agent").write_parquet(d / "targets.parquet", compression="zstd")
    reads.write_parquet(d / "reads.parquet", compression="zstd")
    return {"goal": goal, "targets": tg.height, "with_call": int(np.isfinite(tC).sum()),
            "reads_agent": int((reads["src_kind"] == 0).sum()), "reads_human": int((reads["src_kind"] == 1).sum()),
            "unread": int((reads["src_kind"] == 2).sum()), "agents": int(tg["agent"].n_unique())}


def all_goals() -> list[int]:
    pa = pl.read_parquet(SH / "period_affordances.parquet").filter(~pl.col("holdout"))
    return sorted(set(pa["goal_no"].to_list()))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period")
    ap.add_argument("--all", action="store_true")
    a = ap.parse_args()
    goals = all_goals() if a.all else [int(a.period.lstrip("G"))]
    OUT.mkdir(parents=True, exist_ok=True)
    pf = OUT / "_provenance.json"
    prov = json.loads(pf.read_text()) if pf.exists() else {"counts": {}}
    for g in goals:
        c = build(g)
        print(json.dumps(c))
        prov["counts"][f"G{g:02d}"] = c
    prov.update({"built_by": "hypotheses/H65-leaders-are-routers/scheme/build.py", "git_commit": git_commit(),
                 "inputs": [{"source": "ai-village", "revision": REVISION,
                             "tables": ["shared/embeddings/statements", "shared/embeddings/chat_index",
                                        "shared/call_windows", "shared/context_ledger_items", "shared/chat_core",
                                        "shared/reply_pairs", "shared/period_units"]}],
                 "params": {"read_window_s": WIN_S, "producing_call": "author's last call_windows t_call <= t_B, same PT day",
                            "unread": "same-room agent statements in [t_call, t_B) by others"},
                 "built_at": dt.datetime.now(UTC).isoformat()})
    pf.write_text(json.dumps(prov, indent=1, default=str))


if __name__ == "__main__":
    main()
