"""H114 scheme: per-unit reply forest (one DQ2 parent per message), reply depth, pair gains (codes only, no text).

Builds data/processed/H114-griffiths-phase-pairs/:
  msgs/<unit>.parquet   agent messages: i (row), t (s since EPOCH), day, author, room, in_win (DQ8 all-present window),
                        par (row of the agent parent in the same unit and PT day, -1 none), root_kind (none / human /
                        automated / cross_day / agent), p_reply, names (child names the parent's author), depth
  reads/<unit>.parquet  R_ij = j's messages read by i at ledger calls (pair_day_reads, kind agent), unit days
  unit_meta.parquet, _provenance.json
Holdout asserted twice (calendar.holdout and common.holdout_mask). allow_holdout only from analysis/confirm.py.
Usage: uv run python hypotheses/H114-griffiths-phase-pairs/scheme/build.py
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import json  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import numpy as np  # noqa: E402
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import git_commit, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H114-griffiths-phase-pairs"
EPOCH = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)
MIN_CALLS_PRESENT = 20
MIN_MSGS, MIN_LINKS = 300, 100


def secs(col: str) -> pl.Expr:
    return ((pl.col(col) - pl.lit(EPOCH)).dt.total_microseconds() / 1e6).alias(col)


def load_shared(allow_holdout: bool = False):
    hd = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("holdout"))["pt_date"].to_list()
    cc = (pl.scan_parquet(SH / "chat_core.parquet")
          .filter((pl.col("speaker_kind") == "agent") & (pl.lit(allow_holdout) | ~pl.col("pt_date").is_in(hd)))
          .select("message_id", "t", "pt_date", "goal_no", "room", "agent").collect())
    rp = (pl.scan_parquet(SH / "reply_pairs.parquet")
          .filter(pl.col("parent") & (pl.col("pair_set") == "cand") & (pl.lit(allow_holdout) | ~pl.col("holdout")))
          .select("B_message_id", "A_message_id", "a_kind", "a_agent", "pt_date", "p_reply", "b_names_a").collect())
    cw = (pl.scan_parquet(SH / "call_windows.parquet")
          .filter((pl.lit(allow_holdout) | ~pl.col("holdout")) & (pl.col("ctx_mode") != "summary"))
          .select("agent", "pt_date", "goal_no", "t_call").collect())
    pdr = (pl.scan_parquet(SH / "pair_day_reads.parquet")
           .filter(pl.lit(allow_holdout) | ~pl.col("holdout")).collect())
    cal = pl.read_parquet(SH / "calendar.parquet")
    return cc, rp, cw, pdr, cal


def depth_pass(par: np.ndarray) -> np.ndarray:
    """Depth along parent links; rows are time-sorted, so a parent precedes its child."""
    d = np.zeros(len(par), np.int32)
    for k in range(len(par)):
        p = par[k]
        if p >= 0:
            d[k] = d[p] + 1
    return d


def build_unit(u: dict, cc, rp, cw, pdr, cal, out: Path = OUT, allow_holdout: bool = False, write: bool = True):
    days = sorted(u["days"])
    if not allow_holdout:
        held = holdout_mask(days, [u["goal_no"]] * len(days))
        assert not any(held), f"holdout day in unit {u['unit_id']}"
        assert not cal.filter(pl.col("pt_date").is_in(days) & pl.col("holdout")).height, "calendar holdout"
    s, e = u["start"], u["end"]
    dmap = {d: k for k, d in enumerate(days)}
    m = (cc.filter(pl.col("pt_date").is_in(days) & (pl.col("goal_no") == u["goal_no"])
                   & (pl.col("t") >= s) & (pl.col("t") < e))
         .sort("t").with_row_index("i")
         .with_columns(secs("t"), pl.col("pt_date").replace_strict(dmap, return_dtype=pl.Int16).alias("day")))
    if m.height == 0:
        return None
    # all-present window per day (H67's rule)
    c = (cw.filter(pl.col("pt_date").is_in(days) & (pl.col("goal_no") == u["goal_no"])
                   & (pl.col("t_call") >= s) & (pl.col("t_call") < e))
         .with_columns(secs("t_call"), pl.col("pt_date").replace_strict(dmap, return_dtype=pl.Int16).alias("day")))
    ap = (c.group_by("day", "agent").agg(pl.len().alias("n"), pl.col("t_call").min().alias("f"),
                                         pl.col("t_call").max().alias("l"))
          .filter(pl.col("n") >= MIN_CALLS_PRESENT)
          .group_by("day").agg(pl.col("f").max().alias("ap_lo"), pl.col("l").min().alias("ap_hi")))
    m = m.join(ap, on="day", how="left").with_columns(
        ((pl.col("t") >= pl.col("ap_lo")) & (pl.col("t") <= pl.col("ap_hi"))).fill_null(False).alias("in_win"))
    # parents
    idx = m.select(pl.col("message_id").alias("A_message_id"), pl.col("i").alias("a_i"), pl.col("day").alias("a_day"))
    lk = (rp.join(m.select(pl.col("message_id").alias("B_message_id"), "i"), on="B_message_id", how="inner")
          .join(idx, on="A_message_id", how="left"))
    m = m.join(lk.select("i", "a_kind", "a_i", "a_day", "p_reply", "b_names_a"), on="i", how="left").sort("i")
    m = m.with_columns(
        pl.when(pl.col("a_kind").is_null()).then(pl.lit("none"))
        .when(pl.col("a_kind") == 1).then(pl.lit("human"))
        .when(pl.col("a_kind") == 2).then(pl.lit("automated"))
        .when(pl.col("a_i").is_null()).then(pl.lit("outside"))
        .when(pl.col("a_day") != pl.col("day")).then(pl.lit("cross_day"))
        .otherwise(pl.lit("agent")).alias("root_kind"))
    par = np.where(m["root_kind"].to_numpy() == "agent", m["a_i"].fill_null(-1).to_numpy(), -1).astype(np.int64)
    assert (par < np.arange(len(par))).all(), "parent after child"
    m = m.with_columns(pl.Series("par", par), pl.Series("depth", depth_pass(par)))
    m = m.select("i", "t", "day", pl.col("agent").alias("author"), "room", "in_win", "par", "root_kind", "p_reply",
                 pl.col("b_names_a").fill_null(False).alias("names"), "depth")
    # reads R_ij (i reads j)
    pr = pdr.filter(pl.col("pt_date").is_in(days))
    R = pl.concat([pr.select(pl.col("i").alias("reader"), pl.col("j").alias("author"), pl.col("reads_i_from_j").alias("R")),
                   pr.select(pl.col("j").alias("reader"), pl.col("i").alias("author"), pl.col("reads_j_from_i").alias("R"))])
    R = R.group_by("reader", "author").agg(pl.col("R").sum()).filter(pl.col("R") > 0)
    n_links = int((m["par"] >= 0).sum())
    meta = {"unit_id": u["unit_id"], "goal_no": u["goal_no"], "regime": u["regime"], "n_days": len(days),
            "first_day": days[0], "last_day": days[-1], "n_msgs": m.height, "n_links": n_links,
            "n_in_win": int(m["in_win"].sum()), "n_agents": int(m["author"].n_unique()),
            "eligible": bool(m.height >= MIN_MSGS and n_links >= MIN_LINKS)}
    if write:
        for sub, df in (("msgs", m), ("reads", R)):
            (out / sub).mkdir(parents=True, exist_ok=True)
            df.write_parquet(out / sub / f"{u['unit_id']}.parquet", compression="zstd")
    return meta, m, R


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", default="")
    a = ap.parse_args()
    pu = pl.read_parquet(SH / "period_units.parquet").filter(~pl.col("holdout"))
    if a.units:
        pu = pu.filter(pl.col("unit_id").is_in(a.units.split(",")))
    cc, rp, cw, pdr, cal = load_shared()
    metas = []
    for u in pu.iter_rows(named=True):
        r = build_unit(u, cc, rp, cw, pdr, cal)
        if r:
            metas.append(r[0])
    meta = pl.DataFrame(metas)
    if not a.units:
        meta.write_parquet(OUT / "unit_meta.parquet")
        prov = {"built_by": "hypotheses/H114-griffiths-phase-pairs/scheme/build.py", "git_commit": git_commit(),
                "inputs": [{"source": "ai-village", "tables": ["chat_core", "reply_pairs (DQ2)", "call_windows",
                                                                "pair_day_reads", "calendar", "period_units"]}],
                "params": {"min_msgs": MIN_MSGS, "min_links": MIN_LINKS, "min_calls_present": MIN_CALLS_PRESENT,
                           "parent_rule": "DQ2 parent (pair_set cand, p_reply >= 0.5); cross-day links cut"},
                "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
        (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print(meta.select("unit_id", "regime", "n_msgs", "n_links", "eligible").filter(pl.col("eligible")).height,
          "eligible of", meta.height)


if __name__ == "__main__":
    main()
