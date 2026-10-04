"""H28 round 1b scheme (2026-10-04): context-ledger link exposures, receiving-call times, and work-commit touches.

  uv run python hypotheses/H28-links-spread-herding/scheme/build_r1b.py [--goals 31 41]

Reads the round-1 period folders (links, touches, turns, ... are unchanged) and writes
data/processed/H28-links-spread-herding/r1b/G<NN>/:
  exposures.parquet     msg, recipient, t_vis_ms     t_vis = t_call of the recipient's call that received the link
                                                     (DQ1 context_ledger_items x call_windows); replaces call-start visibility
  calls.parquet         agent, t_ms                  t_call of every receiving call (ctx_mode != summary), for the shift null
  touches_work.parquet  agent, t_ms, project, source agent work commits (DQ4: canonical & ~imported & author_kind agent &
                                                     ~automated) to round 1's universe projects; source = 2
  meta_r1b.json         counts, agreement with round 1's exposure set, visibility delays
Holdout: only the round-1 (non-holdout) days are used; ledger and commit rows are asserted non-holdout.
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h28lib import ALL_PERIODS, OUT, SHARED, assert_not_holdout, gname, write_provenance  # noqa: E402

R1B = OUT / "r1b"


def build(g: int, chat_ids: pl.DataFrame, items: pl.LazyFrame, cw: pl.LazyFrame, wc: pl.LazyFrame, cc: set):
    src = OUT / gname(g)
    meta = json.loads((src / "meta.json").read_text())
    days = meta["days"]
    t0 = dt.datetime.fromtimestamp(days[0]["ws_ms"] / 1000 - 7200, dt.timezone.utc)
    t1 = dt.datetime.fromtimestamp(days[-1]["we_ms"] / 1000 + 26 * 3600, dt.timezone.utc)
    links = pl.read_parquet(src / "links.parquet")
    lm = links.select("msg", "sender").unique("msg").join(chat_ids, on="msg", how="left")
    assert lm["message_id"].null_count() == 0
    calls = cw.filter((pl.col("t_call") >= t0) & (pl.col("t_call") <= t1)).collect()
    it = items.join(lm.lazy().select("message_id", "msg", "sender"), on="message_id", how="inner").collect()
    ex = it.join(calls.select("turn_id", "agent", "t_call", "holdout"), on="turn_id", how="inner")
    assert not ex["holdout"].any(), "holdout ledger row"
    ex = ex.filter((pl.col("agent").cast(pl.Int16) != pl.col("sender")) & ~pl.col("agent").is_in(list(cc)))
    exposures = (ex.group_by("msg", "agent").agg(pl.col("t_call").min())
                 .select(pl.col("msg").cast(pl.UInt32), pl.col("agent").cast(pl.Int8).alias("recipient"),
                         pl.col("t_call").dt.epoch("ms").alias("t_vis_ms")).sort("msg", "recipient"))
    rc = (calls.filter(pl.col("ctx_mode").cast(pl.String) != "summary")
          .select(pl.col("agent").cast(pl.Int8), pl.col("t_call").dt.epoch("ms").alias("t_ms")).sort("agent", "t_ms"))
    # work touches on the universe
    uni = [u["project"] for u in meta["universe"]]
    ws, we = days[0]["ws_ms"], days[-1]["we_ms"]
    w = (wc.filter(pl.col("repo").cast(pl.String).is_in(uni)).collect()
         .with_columns(pl.col("t").dt.epoch("ms").alias("t_ms")))
    dws = np.array([d["ws_ms"] for d in days]); dwe = np.array([d["we_ms"] for d in days])
    tm = w["t_ms"].to_numpy()
    k = np.clip(np.searchsorted(dws, tm, "right") - 1, 0, len(dws) - 1)
    inwin = (tm >= dws[k]) & (tm <= dwe[k])
    w = w.filter(pl.Series(inwin))
    assert not w["holdout"].any(), "holdout commit"
    tw = w.select(pl.col("author_agent").alias("agent").cast(pl.Int8), "t_ms", pl.col("repo").cast(pl.String).alias("project"),
                  pl.lit(2, pl.Int8).alias("source")).filter(~pl.col("agent").is_in(list(cc))).sort("t_ms")
    # agreement with round 1's exposure set and delays
    old = pl.read_parquet(src / "exposures.parquet")
    both = old.join(exposures, on=["msg", "recipient"], how="inner", suffix="_r1b")
    tpost = links.select("msg", "t_ms").unique("msg")
    dl = exposures.join(tpost, on="msg").with_columns(((pl.col("t_vis_ms") - pl.col("t_ms")) / 1000).alias("d"))
    m = {"goal": g, "exposures_r1": old.height, "exposures_r1b": exposures.height, "pairs_in_both": both.height,
         "median_delay_s_r1b": float(dl["d"].median()) if dl.height else None,
         "median_delay_s_r1": float(old.join(tpost, on="msg").select(((pl.col("t_vis_ms") - pl.col("t_ms")) / 1000).median()).item())
         if old.height else None,
         "receiving_calls": rc.height, "work_touches": tw.height, "work_agents": int(tw["agent"].n_unique())}
    d = R1B / gname(g)
    d.mkdir(parents=True, exist_ok=True)
    for name, df in [("exposures", exposures), ("calls", rc), ("touches_work", tw)]:
        df.write_parquet(d / f"{name}.parquet", compression="zstd", compression_level=9)
    (d / "meta_r1b.json").write_text(json.dumps(m, indent=1))
    print(m, flush=True)
    return m


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--goals", type=int, nargs="*", default=None)
    a = ap.parse_args()
    goals = a.goals or ALL_PERIODS
    assert_not_holdout(goals)
    roster = pl.read_parquet(SHARED / "roster.parquet")
    cc = set(roster.filter(pl.col("claude_code"))["agent"].to_list())
    chat_ids = pl.read_parquet(SHARED / "chat_core.parquet", columns=["message_id", "t"]).with_row_index("msg").select(
        pl.col("msg").cast(pl.UInt32), "message_id")
    items = pl.scan_parquet(SHARED / "context_ledger_items.parquet").select("turn_id", "message_id")
    cw = pl.scan_parquet(SHARED / "call_windows.parquet").select("turn_id", "agent", "t_call", "ctx_mode", "holdout")
    wc = pl.scan_parquet(SHARED / "work_commits.parquet").filter(
        pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind").cast(pl.String) == "agent") & ~pl.col("automated")
        & pl.col("author_agent").is_not_null()).select("repo", "t", "author_agent", "holdout")
    ms = [build(g, chat_ids, items, cw, wc, cc) for g in goals]
    (R1B / "meta_r1b_all.json").write_text(json.dumps(ms, indent=1))
    write_provenance(R1B, "hypotheses/H28-links-spread-herding/scheme/build_r1b.py",
                     ["context_ledger_items", "call_windows", "work_commits", "chat_core", "roster", "H28 round-1 G<NN>/ folders"],
                     {"visibility": "t_vis = t_call of the recipient's call that received the link (DQ1 ledger)",
                      "work": "canonical & ~imported & author_kind == agent & ~automated, round-1 universe, day windows",
                      "goals": goals}, key="scheme_r1b")


if __name__ == "__main__":
    main()
