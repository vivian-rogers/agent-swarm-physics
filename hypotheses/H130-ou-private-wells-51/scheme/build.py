"""H130 scheme: #51 statements on the per-call clock, the agent messages each call read, and the per-call reset flags.
Codes and row ids only, no text.

    uv run python hypotheses/H130-ou-private-wells-51/scheme/build.py

Output (data/processed/H130-ou-private-wells-51/):
  statements.parquet  srow (DQ5 statements row), message_id, agent, t, pt_date, room, unit_id, turn_id (producing
                      call), t_call, n (agent-day call index of the producing call), nf / nc (forced / voluntary resets
                      of the agent before the producing call, that day), exact_self_repeat
  reads.parquet       reader, turn_id (receiving call), t_call, n (reader's call index), nf, nc, sender, srow_m (the read
                      message's statements row), t_post, room_m, pt_date, unit_id
  calls.parquet       agent, pt_date, turn_id, t_call, n, reset_forced, reset_consol, nf, nc, room
  _provenance.json
Holdout: #51 tail and any held-out day removed, asserted twice (calendar.holdout and common.holdout_mask).
--include-holdout (needs --i-understand-this-uses-the-locked-holdout, --dates A B, --out DIR outside the round-1
folder) is for analysis/confirm.py only.
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

import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H130-ou-private-wells-51"
GOAL = 51


def days_for(allow_holdout: bool, dates: tuple[str, str] | None) -> list[str]:
    cal = pl.read_parquet(SH / "calendar.parquet").filter((pl.col("goal_no") == GOAL) & (pl.col("n_agent_events") > 0))
    if dates:
        cal = cal.filter((pl.col("pt_date") >= dates[0]) & (pl.col("pt_date") < dates[1]))
    if not allow_holdout:
        cal = cal.filter(~pl.col("holdout"))
        hm = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
        assert not any(hm), "holdout day in the exploratory day list"
    return sorted(cal["pt_date"].to_list())


def unit_of(days: list[str], extra_units: list[dict] | None = None) -> pl.DataFrame:
    pu = pl.read_parquet(SH / "period_units.parquet").filter(pl.col("goal_no") == GOAL)
    rows = []
    for r in pu.iter_rows(named=True):
        for d in r["days"]:
            rows.append((d, r["unit_id"], r["start"]))
    for u in extra_units or []:
        for d in u["days"]:
            rows.append((d, u["unit_id"], dt.datetime(2100, 1, 1, tzinfo=dt.timezone.utc)))
    df = pl.DataFrame(rows, schema={"pt_date": pl.String, "unit_id": pl.String, "ustart": pl.Datetime("us", "UTC")},
                      orient="row")
    if extra_units:
        df = df.filter(pl.col("unit_id").is_in([u["unit_id"] for u in extra_units]))
    # a day listed in two units goes to the latest-starting unit (Known issue: duplicated days)
    df = df.sort("ustart").group_by("pt_date").agg(pl.col("unit_id").last())
    return df.filter(pl.col("pt_date").is_in(days))


def build(allow_holdout: bool = False, dates: tuple[str, str] | None = None, out_root: Path = OUT,
          extra_units: list[dict] | None = None) -> dict:
    days = days_for(allow_holdout, dates)
    units = unit_of(days, extra_units)
    out_root.mkdir(parents=True, exist_ok=True)

    # ---- calls (per-call clock) and resets
    cw = (pl.scan_parquet(SH / "call_windows.parquet")
          .filter((pl.col("goal_no") == GOAL) & pl.col("pt_date").is_in(days))
          .select("turn_id", "agent", "pt_date", "t_call", "holdout").collect())
    if not allow_holdout:
        assert not cw["holdout"].any()
    ct = (pl.scan_parquet(SH / "context_ledger_turns.parquet").filter(pl.col("goal_no") == GOAL)
          .select("turn_id", "reset_forced", "reset_consol", "room").collect())
    calls = (cw.join(ct, on="turn_id", how="left")
             .with_columns(pl.col("reset_forced").fill_null(False), pl.col("reset_consol").fill_null(False))
             .sort("agent", "pt_date", "t_call", "turn_id")
             .with_columns(pl.int_range(pl.len()).over("agent", "pt_date").cast(pl.Int32).alias("n"))
             .with_columns(pl.col("reset_forced").cast(pl.Int32).cum_sum().over("agent", "pt_date").alias("nf"),
                           (pl.col("reset_consol") & ~pl.col("reset_forced")).cast(pl.Int32).cum_sum()
                           .over("agent", "pt_date").alias("nc"))
             .drop("holdout"))
    calls = calls.join(units, on="pt_date", how="inner")

    # ---- statements (agent chat, #51 days)
    st = (pl.scan_parquet(SH / "embeddings/statements.parquet").with_row_index("srow")
          .filter((pl.col("kind") == "chat") & (pl.col("goal_no") == GOAL) & pl.col("pt_date").is_in(days))
          .select("srow", "src_row", "agent", "t", "pt_date", "room", "holdout").collect())
    if not allow_holdout:
        assert not st["holdout"].any()
    # statements.src_row indexes embeddings/chat_index (message ids sorted), not chat_core
    ci = pl.read_parquet(SH / "embeddings/chat_index.parquet").with_row_index("src_row")
    cc = pl.scan_parquet(SH / "chat_core.parquet").select("message_id", "speaker_kind", pl.col("agent").alias("a_cc")).collect()
    st = (st.join(ci, on="src_row", how="left").join(cc, on="message_id", how="left")
          .filter((pl.col("speaker_kind") == "agent") & (pl.col("a_cc") == pl.col("agent"))).drop("a_cc"))
    fl = pl.scan_parquet(SH / "statement_flags.parquet").select("srow", "exact_self_repeat").collect()
    st = st.join(fl, on="srow", how="left").with_columns(pl.col("exact_self_repeat").fill_null(False))
    pc = (pl.scan_parquet(SH / "producing_calls.parquet").filter(pl.col("goal_no") == GOAL)
          .select("message_id", "turn_id_prod", "t_call_prod", "prod_fallback").collect())
    st = st.join(pc, on="message_id", how="left")
    allst = st  # every agent statement of these days (read-message lookup)
    tgt = (st.filter(pl.col("turn_id_prod").is_not_null() & ~pl.col("prod_fallback").fill_null(True))
           .join(calls.select(pl.col("turn_id").alias("turn_id_prod"), "n", "nf", "nc", "unit_id"),
                 on="turn_id_prod", how="inner")
           .rename({"turn_id_prod": "turn_id", "t_call_prod": "t_call"})
           .select("srow", "message_id", "agent", "t", "pt_date", "room", "unit_id", "turn_id", "t_call", "n", "nf",
                   "nc", "exact_self_repeat")
           .sort("agent", "t"))

    # ---- reads: agent items at these calls, joined to the sender's statement row
    items = (pl.scan_parquet(SH / "context_ledger_items.parquet").filter(pl.col("kind") == "agent")
             .select("turn_id", "message_id", "sender").collect())
    items = items.join(calls.select("turn_id", pl.col("agent").alias("reader"), "pt_date", "t_call", "n", "nf", "nc",
                                    "unit_id"), on="turn_id", how="inner")
    msg = allst.select("message_id", pl.col("srow").alias("srow_m"), pl.col("t").alias("t_post"),
                       pl.col("room").alias("room_m"), pl.col("agent").alias("sender_st"))
    reads = (items.join(msg, on="message_id", how="inner")
             .filter(pl.col("sender_st") != pl.col("reader"))
             .select("reader", "turn_id", "t_call", "n", "nf", "nc", pl.col("sender_st").alias("sender"), "srow_m",
                     "t_post", "room_m", "pt_date", "unit_id")
             .sort("reader", "t_call", "t_post"))

    tgt.write_parquet(out_root / "statements.parquet", compression="zstd")
    reads.write_parquet(out_root / "reads.parquet", compression="zstd")
    calls.write_parquet(out_root / "calls.parquet", compression="zstd")
    summ = {"days": len(days), "statements": tgt.height, "reads": reads.height, "calls": calls.height,
            "units": sorted(units["unit_id"].unique().to_list()),
            "dropped_no_call": int(st.height - tgt.height), "items_unmatched": int(items.height - reads.height)}
    prov = {"built_by": "hypotheses/H130-ou-private-wells-51/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["embeddings/statements", "chat_core", "statement_flags", "producing_calls",
                                   "call_windows", "context_ledger_items", "context_ledger_turns", "calendar",
                                   "period_units"]}],
            "params": {"goal": GOAL, "allow_holdout": allow_holdout, "dates": dates, "summary": summ},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (out_root / "_provenance.json").write_text(json.dumps(prov, indent=1, default=str))
    return summ


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--include-holdout", action="store_true")
    ap.add_argument("--i-understand-this-uses-the-locked-holdout", dest="ack", action="store_true")
    ap.add_argument("--dates", nargs=2)
    ap.add_argument("--out")
    a = ap.parse_args()
    if a.include_holdout:
        if not (a.ack and a.dates and a.out):
            sys.exit("--include-holdout needs --i-understand-this-uses-the-locked-holdout, --dates and --out")
        out = Path(a.out).resolve()
        if str(out).startswith(str(OUT.resolve())) and out.name != "confirm":
            sys.exit("refusing to write held-out rows into the round-1 folder")
        print(build(True, tuple(a.dates), out))
    else:
        print(json.dumps(build(False, tuple(a.dates) if a.dates else None), indent=1))


if __name__ == "__main__":
    main()
