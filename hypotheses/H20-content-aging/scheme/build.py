"""H20 scheme: statements with whitened coordinates, active-day indices and goal directions.

Builds data/processed/H20-content-aging/ from the shared tables (non-holdout statements of
non-holdout goal periods only; the Claude Code agent excluded):
  statements.parquet   kind, agent, t, pt_date, goal_no, regime, d (active day, 1 = kickoff day), d_cal (calendar day)
  stmt_w64.npy         fp16 whitened 64-d coordinates in the regime basis (first n columns = n-d basis), row-aligned
  days.parquet         goal_no, pt_date, d, d_cal, gap_before_s, weekend_gap (gap > 36 h), holdout  (ALL calendar
                       days, so day indices are the same in exploration and confirmation; holdout days carry no data here)
  goal_raw.npy + goal_dirs.parquet   raw 384-d bge goal / kickoff / agent-goal vectors (from H01's scheme), whitened
                       downstream with common.load_whitener(regime, n)
No text is stored. Usage: uv run python hypotheses/H20-content-aging/scheme/build.py
"""
from __future__ import annotations

import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h20common as hc  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402


def build_days() -> pl.DataFrame:
    cal = (pl.read_parquet(hc.SH / "calendar.parquet", columns=["pt_date", "goal_no", "gap_before_s", "holdout"])
           .filter(pl.col("goal_no") > 0).sort("pt_date"))
    cal = cal.with_columns(pl.col("pt_date").str.to_date().alias("_date"))
    cal = cal.with_columns(
        (pl.col("_date").rank("ordinal").over("goal_no")).cast(pl.Int16).alias("d"),
        ((pl.col("_date") - pl.col("_date").min().over("goal_no")).dt.total_days() + 1).cast(pl.Int16).alias("d_cal"),
        (pl.col("gap_before_s") > 36 * 3600).alias("weekend_gap"))
    return cal.drop("_date").sort("goal_no", "d")


def main():
    t0 = time.time()
    hc.OUT.mkdir(parents=True, exist_ok=True)
    days = build_days()
    days.write_parquet(hc.OUT / "days.parquet", compression="zstd")

    held = hc.held_out_goals()
    st = pl.read_parquet(hc.ED / "statements.parquet")
    st = st.filter(~pl.col("holdout") & (pl.col("agent") != hc.CLAUDE_CODE_AGENT) & (pl.col("goal_no") > 0)
                   & ~pl.col("goal_no").is_in(list(held)))
    st = st.join(days.select("goal_no", "pt_date", "d", "d_cal"), on=["goal_no", "pt_date"], how="inner").sort("t")
    hc.assert_not_holdout(st["goal_no"].to_list(), st["pt_date"].to_list())
    print(f"statements kept: {st.height}", flush=True)

    Ec = np.load(hc.ED / "chat_bge_small.npy", mmap_mode="r")
    Ei = np.load(hc.ED / "intentions_bge_small.npy", mmap_mode="r")
    kind = st["kind"].to_numpy()
    src = st["src_row"].to_numpy()
    reg = st["regime"].to_numpy()
    Z = np.zeros((st.height, 64), dtype=np.float16)
    for r in sorted(set(reg)):
        W = hc.common.load_whitener(r, 64)
        for k, E in (("chat", Ec), ("intent", Ei)):
            sel = np.flatnonzero((reg == r) & (kind == k))
            if sel.size:
                # chunked to keep memory small
                for a in range(0, sel.size, 20000):
                    s = sel[a:a + 20000]
                    Z[s] = W(np.asarray(E[src[s]], dtype=np.float32)).astype(np.float16)
    np.save(hc.OUT / "stmt_w64.npy", Z)
    st.select("kind", "agent", "t", "pt_date", "goal_no", "regime", "room", "d", "d_cal") \
      .write_parquet(hc.OUT / "statements.parquet", compression="zstd")

    # goal directions (raw 384-d, H01's goal + kickoff + agent-goal embeddings; no text)
    g = pl.read_parquet(hc.H01 / "goals.parquet").unique(subset=["gid"]).sort("gid")
    graw = np.load(hc.H01 / "goals_raw.npy")
    g = g.filter(~pl.col("goal_no").is_in(list(held)))
    np.save(hc.OUT / "goal_raw.npy", graw[g["gid"].to_numpy()].astype(np.float32))
    g.with_row_index("row").select("row", "goal_no", "kind", "room", "agent", "valid_from", "valid_to", "regime") \
     .write_parquet(hc.OUT / "goal_dirs.parquet", compression="zstd")

    hc.write_provenance(
        {"embedding_model": "BAAI/bge-small-en-v1.5", "whitening": "common.load_whitener(regime, 64), fit on non-holdout",
         "stored_dim": 64, "statements": "agent chat + intentions (shared instrument)", "exclude_agent": hc.CLAUDE_CODE_AGENT,
         "holdout": "masked (statements.holdout and holdout goal periods)", "day_index": "active-day rank within goal period",
         "weekend_gap_h": 36},
        ["shared/embeddings/statements", "shared/embeddings/*_bge_small.npy", "shared/embeddings/whitening_*",
         "shared/calendar", "H01/goals.parquet + goals_raw.npy (goal/kickoff/agent-goal bge vectors)"],
        "hypotheses/H20-content-aging/scheme/build.py")
    print(f"done in {time.time() - t0:.0f}s", flush=True)


if __name__ == "__main__":
    main()
