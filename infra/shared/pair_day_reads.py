"""Shared pair-day ledger read counts: how many of agent j's chat messages entered agent i's model calls on PT day d.

Moved from H05 (hypotheses/H05-rooms-cut/analysis/r1b_reads.py: pair_reads, which wrote
data/processed/H05-rooms-cut/r1b/pair_day_reads.parquet). The count rule is unchanged: items of kind `agent` in
`context_ledger_items` (DQ1 visibility rule) joined to the receiving call in `context_ledger_turns`; the day is the
receiving call's pt_date; self-reads are dropped. H05 used it to control room coupling for reading (RE-R1: co-location
z 5.1 -> 0.2 with log(1 + reads)); H18, H29, H47 and H50 could reuse it.

Output (data/processed/shared/pair_day_reads.parquet, zstd, codes only, ALL days; `holdout` flags locked-holdout days,
so exploratory users filter `~holdout`):
  pt_date, goal_no, holdout, i, j (unordered pair, i < j, Int8 agent codes), reads_i_from_j, reads_j_from_i (UInt32;
  j's messages that entered i's calls and vice versa), calls_i, calls_j (ledger calls of i / j that day, all ctx
  modes; 0 when absent). Sparse: only pairs with >= 1 read in either direction; a missing pair-day has 0 reads.
  Directed use: reads(i <- j) = reads_i_from_j. Pair total = reads_i_from_j + reads_j_from_i (H05's `reads`).

Usage: uv run python infra/shared/pair_day_reads.py            (build)
       uv run python infra/shared/pair_day_reads.py --verify   (compare with H05's r1b/pair_day_reads.parquet on its
                                                                 days; read-only)
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS",
           "RAYON_NUM_THREADS"):
    os.environ.setdefault(_v, "2")

import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT, ROOT, holdout_mask, write_provenance  # noqa: E402

SH = OUT
H05 = ROOT / "data/processed/H05-rooms-cut/r1b"


def directed_reads(days=None, exclude_holdout: bool = False) -> pl.DataFrame:
    """(pt_date, recipient, sender, n): agent-message reads per receiving agent-day (self-reads dropped)."""
    it = pl.scan_parquet(SH / "context_ledger_items.parquet").filter(pl.col("kind") == "agent").select("turn_id", "sender")
    tu = pl.scan_parquet(SH / "context_ledger_turns.parquet").select("turn_id", "agent", "pt_date", "holdout")
    if days is not None:
        tu = tu.filter(pl.col("pt_date").is_in(list(days)))
    if exclude_holdout:
        tu = tu.filter(~pl.col("holdout"))
    return (it.join(tu, on="turn_id").filter(pl.col("agent") != pl.col("sender"))
            .group_by("pt_date", "agent", "sender").agg(pl.len().alias("n"))
            .rename({"agent": "recipient"}).collect())


def pair_reads(days=None, exclude_holdout: bool = False) -> pl.DataFrame:
    """H05's unordered pair-day form (pt_date, i, j, reads_i_from_j, reads_j_from_i)."""
    r = directed_reads(days, exclude_holdout)
    a = r.with_columns(pl.min_horizontal("recipient", "sender").alias("i"), pl.max_horizontal("recipient", "sender").alias("j"),
                       (pl.col("recipient") < pl.col("sender")).alias("i_recv"))
    out = (a.group_by("pt_date", "i", "j")
           .agg(pl.col("n").filter(pl.col("i_recv")).sum().alias("reads_i_from_j"),
                pl.col("n").filter(~pl.col("i_recv")).sum().alias("reads_j_from_i")))
    return out.with_columns(pl.col("i").cast(pl.Int8), pl.col("j").cast(pl.Int8))


def build() -> pl.DataFrame:
    pr = pair_reads()
    tu = pl.scan_parquet(SH / "context_ledger_turns.parquet").select("agent", "pt_date", "goal_no")
    calls = tu.group_by("pt_date", "agent").agg(pl.len().cast(pl.UInt32).alias("calls")).collect()
    day = tu.group_by("pt_date").agg(pl.col("goal_no").first()).collect()
    day = day.with_columns(pl.Series("holdout", holdout_mask(day["pt_date"].to_list(), day["goal_no"].to_list())))
    ci = calls.rename({"agent": "i", "calls": "calls_i"}).with_columns(pl.col("i").cast(pl.Int8))
    cj = calls.rename({"agent": "j", "calls": "calls_j"}).with_columns(pl.col("j").cast(pl.Int8))
    out = (pr.join(day, on="pt_date", how="left").join(ci, on=["pt_date", "i"], how="left")
           .join(cj, on=["pt_date", "j"], how="left")
           .with_columns(pl.col("calls_i").fill_null(0), pl.col("calls_j").fill_null(0)))
    return out.select("pt_date", "goal_no", "holdout", "i", "j", "reads_i_from_j", "reads_j_from_i", "calls_i", "calls_j"
                      ).sort("pt_date", "i", "j")


def main():
    t0 = time.time()
    df = build()
    p = SH / "pair_day_reads.parquet"
    df.write_parquet(p, compression="zstd", compression_level=9)
    nh = df.filter(~pl.col("holdout"))
    summ = {"rows": df.height, "rows_nonholdout": nh.height, "days": int(df["pt_date"].n_unique()),
            "reads_nonholdout": int((nh["reads_i_from_j"] + nh["reads_j_from_i"]).sum())}
    write_provenance("pair_day_reads", ["context_ledger_items", "context_ledger_turns"],
                     {"rule": "count of kind == agent ledger items from j entering i's calls; day = receiving call's "
                              "pt_date; self-reads dropped; unordered pairs i < j; sparse (pairs with >= 1 read)",
                      "calls": "context_ledger_turns rows per agent-day (all ctx modes)", "holdout": "all days, flagged",
                      "source": "hypotheses/H05-rooms-cut/analysis/r1b_reads.py: pair_reads (rule unchanged)",
                      "summary": summ})
    print(f"pair_day_reads.parquet: {df.height} rows, {p.stat().st_size / 1e6:.2f} MB, {time.time() - t0:.0f}s", flush=True)
    print(json.dumps(summ), flush=True)


def verify() -> dict:
    """H05's table covers the non-holdout days of its r1b pair_day_bin1 panel; compare on exactly those days."""
    sh = pl.read_parquet(SH / "pair_day_reads.parquet")
    old = pl.read_parquet(H05 / "pair_day_reads.parquet")
    days = sorted(pl.read_parquet(H05 / "pair_day_bin1.parquet", columns=["pt_date"])["pt_date"].unique().to_list())
    mine = (sh.filter(pl.col("pt_date").is_in(days) & ~pl.col("holdout"))
            .select("pt_date", "i", "j", "reads_i_from_j", "reads_j_from_i").sort("pt_date", "i", "j"))
    old = old.sort("pt_date", "i", "j")
    res = {"h05_rows": old.height, "shared_rows_on_h05_days": mine.height, "days": len(days),
           "holdout_rows_on_h05_days": sh.filter(pl.col("pt_date").is_in(days) & pl.col("holdout")).height,
           "identical": bool(old.equals(mine))}
    if not res["identical"]:
        j = old.join(mine, on=["pt_date", "i", "j"], how="full", coalesce=True, suffix="_s")
        res["only_h05"] = int(j["reads_i_from_j_s"].is_null().sum())
        res["only_shared"] = int(j["reads_i_from_j"].is_null().sum())
        res["count_diff"] = int(((j["reads_i_from_j"] != j["reads_i_from_j_s"]) | (j["reads_j_from_i"] != j["reads_j_from_i_s"])).sum())
    print(json.dumps(res), flush=True)
    return res


if __name__ == "__main__":
    if "--verify" in sys.argv:
        verify()
    else:
        main()
