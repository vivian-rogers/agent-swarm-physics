"""H67 scheme: per non-holdout period unit, the receiving calls and agent chat messages needed for the call-clock
read-out loop gain. Codes only (no text). Output: data/processed/H67-lagged-criticality-dial/units/<unit>.parquet
(calls) and msgs/<unit>.parquet (messages), unit_meta.parquet, _provenance.json.

    uv run python hypotheses/H67-lagged-criticality-dial/scheme/build.py [--units 38a,40]

Holdout is asserted twice (calendar.holdout and common.holdout_mask). Times are float seconds since EPOCH (UTC).
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
from common import git_commit, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H67-lagged-criticality-dial"
EPOCH = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)
WAKE = {"pause", "pause_early", "first_of_day", "after_summary", "session_start", "marker"}
MIN_CALLS_PRESENT = 20      # an agent counts as present on a day with >= 20 receiving calls (all-present window)


def secs(col: str) -> pl.Expr:
    return ((pl.col(col) - pl.lit(EPOCH)).dt.total_microseconds() / 1e6).alias(col)


def load_shared(allow_holdout: bool = False):
    """allow_holdout is only set by analysis/confirm.py (guarded)."""
    cw = (pl.scan_parquet(SH / "call_windows.parquet")
          .filter(pl.lit(allow_holdout) | ~pl.col("holdout"))
          .select("turn_id", "agent", "pt_date", "goal_no", "regime", "talk", "ctx_mode", "t_call", "t_first",
                  "gap_kind", "first_of_day", "start_conf")
          .collect())
    lt = pl.read_parquet(SH / "context_ledger_turns.parquet",
                         columns=["turn_id", "room", "n_agent", "holdout", "reset_forced", "reset_consol"])
    lt = lt.filter(pl.lit(allow_holdout) | ~pl.col("holdout")).drop("holdout")
    it = (pl.scan_parquet(SH / "context_ledger_items.parquet")
          .filter(pl.col("kind").is_in(["human", "nudge"]))
          .group_by("turn_id")
          .agg((pl.col("kind") == "human").sum().alias("E_h"),
               (pl.col("kind") == "nudge").sum().alias("E_n"),
               ((pl.col("kind") == "nudge") & pl.col("ment")).sum().alias("E_nme"))
          .collect())
    cc = (pl.scan_parquet(SH / "chat_core.parquet")
          .filter(pl.col("speaker_kind") == "agent")
          .select("message_id", "t", "pt_date", "goal_no", "room", "agent")
          .collect())
    mc = pl.read_parquet(SH / "chat_mentions_clean.parquet", columns=["message_id", "mentions_roster"])
    cc = cc.join(mc, on="message_id", how="left")
    return cw, lt, it, cc


def build_unit(u: dict, cw, lt, it, cc, cal, out_dir: Path | None = None, allow_holdout: bool = False) -> dict | None:
    days = list(u["days"])
    if not allow_holdout:
        held = holdout_mask(days, [u["goal_no"]] * len(days))
        assert not any(held), f"holdout day in unit {u['unit_id']}"
        assert not cal.filter(pl.col("pt_date").is_in(days) & pl.col("holdout")).height, "calendar holdout"
    s, e = u["start"], u["end"]
    calls = (cw.filter(pl.col("pt_date").is_in(days) & (pl.col("goal_no") == u["goal_no"])
                       & (pl.col("t_call") >= s) & (pl.col("t_call") < e))
             .join(lt, on="turn_id", how="left")
             .join(it, on="turn_id", how="left")
             .with_columns(pl.col("E_h").fill_null(0), pl.col("E_n").fill_null(0), pl.col("E_nme").fill_null(0)))
    if calls.height == 0:
        return None
    # receiving calls only (summary calls read nothing new); keep order per agent-day
    calls = (calls.filter(pl.col("ctx_mode") != "summary")
             .with_columns(secs("t_call"), secs("t_first"))
             .sort("agent", "pt_date", "t_call"))
    dmap = {d: k for k, d in enumerate(sorted(days))}
    calls = calls.with_columns(
        pl.col("pt_date").replace_strict(dmap, return_dtype=pl.Int16).alias("day"),
        pl.col("t_call").shift(1).over(["agent", "pt_date"]).alias("t_prev"),
        (pl.col("ctx_mode") == "chat").cast(pl.Int8).alias("is_chat"),
        pl.col("gap_kind").cast(pl.String).is_in(list(WAKE)).cast(pl.Int8).alias("is_wake"),
    ).with_columns((pl.col("is_chat") * 2 + pl.col("is_wake")).alias("cls"))
    # all-present window per day (DQ8): agents with >= MIN_CALLS_PRESENT receiving calls that day
    pres = (calls.group_by("day", "agent").agg(pl.len().alias("n"), pl.col("t_call").min().alias("f"),
                                               pl.col("t_call").max().alias("l"))
            .filter(pl.col("n") >= MIN_CALLS_PRESENT)
            .group_by("day").agg(pl.col("f").max().alias("ap_lo"), pl.col("l").min().alias("ap_hi"),
                                 pl.len().alias("n_present")))
    calls = calls.join(pres, on="day", how="left").with_columns(
        ((pl.col("t_call") >= pl.col("ap_lo")) & (pl.col("t_call") <= pl.col("ap_hi"))).fill_null(False)
        .alias("trim"))
    msgs = (cc.filter(pl.col("pt_date").is_in(days) & (pl.col("goal_no") == u["goal_no"])
                      & (pl.col("t") >= s) & (pl.col("t") < e))
            .with_columns(secs("t"), pl.col("pt_date").replace_strict(dmap, return_dtype=pl.Int16).alias("day"))
            .select("message_id", "t", "day", "room", "agent", "mentions_roster").sort("t"))
    calls = calls.select("turn_id", "agent", "day", "t_call", "t_first", "t_prev", "room", "cls", "is_chat",
                         "is_wake", "talk", "first_of_day", "start_conf", "trim", "ap_lo", "ap_hi", "n_present",
                         "E_h", "E_n", "E_nme", "n_agent", "reset_forced", "reset_consol")
    base = out_dir or OUT
    d = base / "units"
    d.mkdir(parents=True, exist_ok=True)
    (base / "msgs").mkdir(parents=True, exist_ok=True)
    calls.write_parquet(d / f"{u['unit_id']}.parquet", compression="zstd")
    msgs.drop("message_id").write_parquet(base / "msgs" / f"{u['unit_id']}.parquet", compression="zstd")
    tr = calls.filter(pl.col("trim"))
    return {"unit_id": u["unit_id"], "goal_no": u["goal_no"], "regime": u["regime"], "n_days": len(days),
            "first_day": u["first_day"], "last_day": u["last_day"],
            "n_agents_calling": calls["agent"].n_unique(), "n_calls": calls.height, "n_calls_trim": tr.height,
            "n_msgs": msgs.height, "n_talk_calls": int(calls["talk"].sum()), "rooms": len(set(calls["room"].drop_nulls().to_list())),
            "trim_share": tr.height / max(calls.height, 1)}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", default="")
    a = ap.parse_args()
    cal = pl.read_parquet(SH / "calendar.parquet")
    pu = pl.read_parquet(SH / "period_units.parquet").filter(~pl.col("holdout"))
    if a.units:
        pu = pu.filter(pl.col("unit_id").is_in(a.units.split(",")))
    cw, lt, it, cc = load_shared()
    meta = []
    for u in pu.sort("goal_no", "seq").to_dicts():
        r = build_unit(u, cw, lt, it, cc, cal)
        if r:
            meta.append(r)
            print(r["unit_id"], r["n_calls"], r["n_calls_trim"], r["n_msgs"], flush=True)
    m = pl.DataFrame(meta)
    if a.units and (OUT / "unit_meta.parquet").exists():
        old = pl.read_parquet(OUT / "unit_meta.parquet").filter(~pl.col("unit_id").is_in(m["unit_id"]))
        m = pl.concat([old, m], how="diagonal_relaxed")
    m.sort("goal_no", "unit_id").write_parquet(OUT / "unit_meta.parquet")
    prov = {"built_by": "hypotheses/H67-lagged-criticality-dial/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": "shared tables (DQ1 context ledger)",
                        "tables": ["call_windows", "context_ledger_turns", "context_ledger_items", "chat_core",
                                   "chat_mentions_clean", "calendar", "period_units"]}],
            "params": {"min_calls_present": MIN_CALLS_PRESENT, "wake_gap_kinds": sorted(WAKE),
                       "epoch": EPOCH.isoformat(), "holdout": "excluded, asserted twice"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    main()
