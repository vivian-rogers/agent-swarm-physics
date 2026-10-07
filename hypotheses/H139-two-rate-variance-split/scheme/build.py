"""H139 scheme: regime-III statements on the per-call clock, the agent messages each call read, per-call read counts
and reset flags, for one goal period. Codes and row ids only, no text.

    uv run python hypotheses/H139-two-rate-variance-split/scheme/build.py --period G51

Adapted (copied, not imported; STANDARDS 8) from hypotheses/H130-ou-private-wells-51/scheme/build.py, with three
changes: any regime-III goal period; a per-call count of every agent item read from another agent (the read rate r_bar,
counted from the ledger whether or not the read message has a DQ5 statement row); `reset_session` as a third reset kind.

Output (data/processed/H139-two-rate-variance-split/G<NN>/):
  statements.parquet  srow, message_id, agent, t, pt_date, room, unit_id, turn_id (producing call), t_call, n (agent-day
                      call index), nf / nc / ns (forced / voluntary / session resets before the producing call, that day)
  reads.parquet       reader, turn_id, t_call, n, nf, sender, srow_m (read message's statements row), t_post, room_m,
                      pt_date, unit_id   [reads of messages that have a statement row; used for synthetic kicks, J_K]
  calls.parquet       agent, pt_date, turn_id, t_call, n, kind, talk, reset_forced, reset_consol, reset_session, nf, nc,
                      ns, room, unit_id, n_read (all agent items from other agents newly in context at the call)
  _provenance.json
Reserved data (hypotheses/holdout.md) are dropped twice: calendar.holdout and common.holdout_mask (asserted).
Regime III only. Exact self-repeats and fallback producing calls are dropped (H130's rules).
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "1")

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
OUT = ROOT / "data/processed/H139-two-rate-variance-split"


def days_for(goal: int) -> list[str]:
    cal = pl.read_parquet(SH / "calendar.parquet").filter((pl.col("goal_no") == goal) & (pl.col("n_agent_events") > 0)
                                                          & (pl.col("regime") == "III"))
    cal = cal.filter(~pl.col("holdout"))
    hm = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    cal = cal.filter(~pl.Series(hm))
    hm2 = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    assert not any(hm2), "reserved day in the exploratory day list"
    return sorted(cal["pt_date"].to_list())


def unit_of(goal: int, days: list[str]) -> pl.DataFrame:
    pu = pl.read_parquet(SH / "period_units.parquet").filter((pl.col("goal_no") == goal) & ~pl.col("holdout"))
    rows = [(d, r["unit_id"], r["start"]) for r in pu.iter_rows(named=True) for d in r["days"]]
    df = pl.DataFrame(rows, schema={"pt_date": pl.String, "unit_id": pl.String, "ustart": pl.Datetime("us", "UTC")},
                      orient="row")
    # a day listed in two units goes to the latest-starting unit (Known issue: duplicated days; as H130)
    df = df.sort("ustart").group_by("pt_date").agg(pl.col("unit_id").last())
    return df.filter(pl.col("pt_date").is_in(days))


def build(goal: int) -> dict:
    days = days_for(goal)
    units = unit_of(goal, days)
    out = OUT / f"G{goal:02d}"
    out.mkdir(parents=True, exist_ok=True)

    cw = (pl.scan_parquet(SH / "call_windows.parquet")
          .filter((pl.col("goal_no") == goal) & pl.col("pt_date").is_in(days))
          .select("turn_id", "agent", "pt_date", "t_call", "kind", "talk", "holdout").collect())
    assert not cw["holdout"].any()
    ct = (pl.scan_parquet(SH / "context_ledger_turns.parquet").filter(pl.col("goal_no") == goal)
          .select("turn_id", "reset_forced", "reset_consol", "reset_session", "room").collect())
    calls = (cw.join(ct, on="turn_id", how="left")
             .with_columns([pl.col(c).fill_null(False) for c in ("reset_forced", "reset_consol", "reset_session")])
             .sort("agent", "pt_date", "t_call", "turn_id")
             .with_columns(pl.int_range(pl.len()).over("agent", "pt_date").cast(pl.Int32).alias("n"))
             .with_columns(pl.col("reset_forced").cast(pl.Int32).cum_sum().over("agent", "pt_date").alias("nf"),
                           (pl.col("reset_consol") & ~pl.col("reset_forced")).cast(pl.Int32).cum_sum()
                           .over("agent", "pt_date").alias("nc"),
                           (pl.col("reset_session") & ~pl.col("reset_forced") & ~pl.col("reset_consol"))
                           .cast(pl.Int32).cum_sum().over("agent", "pt_date").alias("ns"))
             .drop("holdout"))
    calls = calls.join(units, on="pt_date", how="inner")

    st = (pl.scan_parquet(SH / "embeddings/statements.parquet").with_row_index("srow")
          .filter((pl.col("kind") == "chat") & (pl.col("goal_no") == goal) & pl.col("pt_date").is_in(days))
          .select("srow", "src_row", "agent", "t", "pt_date", "room", "holdout").collect())
    assert not st["holdout"].any()
    ci = pl.read_parquet(SH / "embeddings/chat_index.parquet").with_row_index("src_row")
    cc = pl.scan_parquet(SH / "chat_core.parquet").select("message_id", "speaker_kind", pl.col("agent").alias("a_cc")).collect()
    st = (st.join(ci, on="src_row", how="left").join(cc, on="message_id", how="left")
          .filter((pl.col("speaker_kind") == "agent") & (pl.col("a_cc") == pl.col("agent"))).drop("a_cc"))
    fl = pl.scan_parquet(SH / "statement_flags.parquet").select("srow", "exact_self_repeat").collect()
    st = st.join(fl, on="srow", how="left").with_columns(pl.col("exact_self_repeat").fill_null(False))
    pc = (pl.scan_parquet(SH / "producing_calls.parquet").filter(pl.col("goal_no") == goal)
          .select("message_id", "turn_id_prod", "t_call_prod", "prod_fallback").collect())
    st = st.join(pc, on="message_id", how="left")
    allst = st
    tgt = (st.filter(pl.col("turn_id_prod").is_not_null() & ~pl.col("prod_fallback").fill_null(True)
                     & ~pl.col("exact_self_repeat"))
           .join(calls.select(pl.col("turn_id").alias("turn_id_prod"), "n", "nf", "nc", "ns", "unit_id"),
                 on="turn_id_prod", how="inner")
           .rename({"turn_id_prod": "turn_id", "t_call_prod": "t_call"})
           .select("srow", "message_id", "agent", "t", "pt_date", "room", "unit_id", "turn_id", "t_call", "n", "nf",
                   "nc", "ns")
           .sort("agent", "t"))

    items = (pl.scan_parquet(SH / "context_ledger_items.parquet").filter(pl.col("kind") == "agent")
             .select("turn_id", "message_id", "sender").collect())
    items = items.join(calls.select("turn_id", pl.col("agent").alias("reader"), "pt_date", "t_call", "n", "nf",
                                    "unit_id"), on="turn_id", how="inner")
    items = items.filter(pl.col("sender") != pl.col("reader"))
    nread = items.group_by("turn_id").agg(pl.len().cast(pl.Int16).alias("n_read"))
    calls = calls.join(nread, on="turn_id", how="left").with_columns(pl.col("n_read").fill_null(0))
    msg = allst.select("message_id", pl.col("srow").alias("srow_m"), pl.col("t").alias("t_post"),
                       pl.col("room").alias("room_m"), pl.col("agent").alias("sender_st"))
    reads = (items.join(msg, on="message_id", how="inner")
             .filter(pl.col("sender_st") != pl.col("reader"))
             .select("reader", "turn_id", "t_call", "n", "nf", pl.col("sender_st").alias("sender"), "srow_m",
                     "t_post", "room_m", "pt_date", "unit_id")
             .sort("reader", "t_call", "t_post"))

    tgt.write_parquet(out / "statements.parquet", compression="zstd")
    reads.write_parquet(out / "reads.parquet", compression="zstd")
    calls.write_parquet(out / "calls.parquet", compression="zstd")
    summ = {"days": len(days), "statements": tgt.height, "reads_matched": reads.height,
            "reads_all": int(items.height), "calls": calls.height,
            "units": sorted(units["unit_id"].unique().to_list())}
    prov = {"built_by": "hypotheses/H139-two-rate-variance-split/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["embeddings/statements", "embeddings/chat_index", "chat_core", "statement_flags",
                                   "producing_calls", "call_windows", "context_ledger_items", "context_ledger_turns",
                                   "calendar", "period_units"]}],
            "params": {"goal": goal, "regime": "III", "reserved_masked": True, "summary": summ},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (out / "_provenance.json").write_text(json.dumps(prov, indent=1, default=str))
    # top-level provenance lists the per-period folders
    top = OUT / "_provenance.json"
    P = json.loads(top.read_text()) if top.exists() else {"built_by": prov["built_by"], "inputs": prov["inputs"],
                                                          "periods": {}}
    P["periods"][f"G{goal:02d}"] = {"git_commit": prov["git_commit"], "built_at": prov["built_at"], "summary": summ}
    P["git_commit"], P["built_at"], P["params"] = prov["git_commit"], prov["built_at"], {"regime": "III"}
    top.write_text(json.dumps(P, indent=1, default=str))
    return summ


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--period", required=True, help="e.g. G51, G38")
    a = ap.parse_args()
    print(json.dumps(build(int(a.period.lstrip("G"))), indent=1))


if __name__ == "__main__":
    main()
