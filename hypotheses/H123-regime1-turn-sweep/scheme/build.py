"""H123 scheme: event-time update steps (one row per model call) for regime-I units and the NE14 units.

Output: data/processed/H123-regime1-turn-sweep/steps/<unit>.parquet with
  day (pt_date), step (0.. within day), agent (int8 code), t_call, t_log, talk (bool), cu (bool: ctx_mode == cu),
  kind, named_mask (int64 bitmask over agent codes named in the latest agent chat message before t_call, <= 10 min)
plus _provenance.json. Holdout rows never enter (calendar holdout and holdout_mask both applied).

Day-present agents: >= 5 calls that day (roster agents, Claude Code agent excluded). Steps before every day-present
agent has called once are kept here (flag `warm` = False) and dropped by the analysis.

Usage: uv run python hypotheses/H123-regime1-turn-sweep/scheme/build.py
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import git_commit, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H123-regime1-turn-sweep"
NE14_UNITS = ["33", "35", "36a", "36b", "36c", "37"]
MIN_CALLS = 5
NAME_WINDOW_S = 600


def units() -> pl.DataFrame:
    pu = pl.read_parquet(SH / "period_units.parquet")
    reg1 = pu.filter((pl.col("regime") == "I") & (~pl.col("holdout")))
    ne14 = pu.filter(pl.col("unit_id").is_in(NE14_UNITS) & (~pl.col("holdout")))
    return pl.concat([reg1, ne14]).unique("unit_id").sort("start")


def make_steps(U: pl.DataFrame, allow_holdout: bool = False) -> tuple[dict, list]:
    """Step tables for the units in U (in memory). allow_holdout=True is for the guarded confirm script only."""
    roster = pl.read_parquet(SH / "roster.parquet")
    cc = set(roster.filter(pl.col("claude_code"))["agent"].to_list())
    all_days = sorted({d for ds in U["days"].to_list() for d in ds})
    q = pl.scan_parquet(SH / "call_windows.parquet").filter(pl.col("pt_date").is_in(all_days))
    if not allow_holdout:
        q = q.filter(~pl.col("holdout"))
    cw = q.select("turn_id", "agent", "pt_date", "goal_no", "kind", "talk", "ctx_mode", "t_call", "t_log").collect()
    cw = cw.filter(~pl.col("agent").is_in(list(cc)))
    if not allow_holdout:
        hm = holdout_mask(cw["pt_date"].to_list(), cw["goal_no"].to_list())
        cw = cw.filter(~pl.Series(hm))
    msgs = (pl.scan_parquet(SH / "chat_core.parquet")
            .filter(pl.col("pt_date").is_in(all_days) & (pl.col("speaker_kind") == "agent"))
            .select("message_id", "t", "pt_date", "goal_no", "agent").collect()
            .join(pl.read_parquet(SH / "chat_mentions_clean.parquet").select("message_id", "mentions_roster"),
                  on="message_id", how="left"))
    if not allow_holdout:
        hm = holdout_mask(msgs["pt_date"].to_list(), msgs["goal_no"].to_list())
        msgs = msgs.filter(~pl.Series(hm))
    msgs = msgs.with_columns(
        pl.col("mentions_roster").list.unique().list.eval(pl.lit(2, dtype=pl.Int64).pow(pl.element().cast(pl.Int64)))
        .list.sum().fill_null(0).cast(pl.Int64).alias("mask")).sort("t")
    summary, out = [], {}
    for row in U.iter_rows(named=True):
        days = row["days"]
        d = cw.filter(pl.col("pt_date").is_in(days)).sort("pt_date", "t_call", "turn_id")
        frames = []
        for day in sorted(days):
            x = d.filter(pl.col("pt_date") == day)
            if x.height == 0:
                continue
            cnt = x.group_by("agent").len()
            pres = cnt.filter(pl.col("len") >= MIN_CALLS)["agent"].to_list()
            x = x.filter(pl.col("agent").is_in(pres))
            if len(pres) < 2:
                continue
            # warm: after every present agent has called once
            first = x.with_row_index("i").group_by("agent").agg(pl.col("i").min())["i"].max()
            x = x.with_row_index("step").with_columns((pl.col("step") >= first).alias("warm"))
            m = msgs.filter(pl.col("pt_date") == day).select(pl.col("t").alias("t_msg"), "mask")
            x = x.sort("t_call").join_asof(m, left_on="t_call", right_on="t_msg", strategy="backward")
            age = (x["t_call"] - x["t_msg"]).dt.total_seconds()
            x = x.with_columns(pl.when(age.is_not_null() & (age <= NAME_WINDOW_S)).then(pl.col("mask"))
                               .otherwise(0).fill_null(0).alias("named_mask")).sort("step")
            frames.append(x.select(pl.col("pt_date").alias("day"), pl.col("step").cast(pl.Int32), "agent", "t_call",
                                   "t_log", "talk", (pl.col("ctx_mode") == "cu").alias("cu"), "kind",
                                   pl.col("named_mask").cast(pl.Int64), "warm"))
        if not frames:
            continue
        S = pl.concat(frames)
        out[row["unit_id"]] = S
        summary.append({"unit": row["unit_id"], "goal_no": row["goal_no"], "regime": row["regime"],
                        "n_days": S["day"].n_unique(), "n_steps": S.height,
                        "n_agents": S["agent"].n_unique()})
    return out, summary


def build():
    OUT.joinpath("steps").mkdir(parents=True, exist_ok=True)
    out, summary = make_steps(units())
    for u, S in out.items():
        S.write_parquet(OUT / "steps" / f"{u}.parquet", compression="zstd")
    pl.DataFrame(summary).write_parquet(OUT / "units.parquet")
    (OUT / "_provenance.json").write_text(json.dumps({
        "built_by": "hypotheses/H123-regime1-turn-sweep/scheme/build.py", "git_commit": git_commit(),
        "inputs": [{"source": "shared", "tables": ["call_windows", "chat_core", "chat_mentions_clean",
                                                   "period_units", "roster"]}],
        "params": {"min_calls": MIN_CALLS, "name_window_s": NAME_WINDOW_S, "ne14_units": NE14_UNITS},
        "built_at": __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()}, indent=1))
    print(pl.DataFrame(summary))




if __name__ == "__main__":
    build()
