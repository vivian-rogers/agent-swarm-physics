"""H111 scheme: per-unit talk messages, receiving calls, day windows and exogenous times (codes and times only).

Builds data/processed/H111-talk-fano-sum-rule/ from shared tables:
  calls/<unit>.parquet   receiving calls (ctx_mode != summary): agent, day, t_call, t_first, talk, room (seconds since
                         EPOCH as float64)
  msgs/<unit>.parquet    agent talk messages (chat_core speaker_kind == agent): t, day, agent, room
  days/<unit>.parquet    per day: ap_lo, ap_hi (DQ8 all-present window, H67's rule), win_start, win_end (calendar),
                         kickoff_day flag
  present/<unit>.parquet per day x present agent (>= 20 receiving calls): modal room, n_calls
  exo/<unit>.parquet     human-message times in the unit (kicks_classified kind human_message)
  unit_meta.parquet, _provenance.json

Holdout: asserted twice (calendar.holdout and common.holdout_mask). allow_holdout only from analysis/confirm.py.
Usage: uv run python hypotheses/H111-talk-fano-sum-rule/scheme/build.py [--units 27,41]
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
from common import git_commit, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H111-talk-fano-sum-rule"
H67 = ROOT / "data/processed/H67-lagged-criticality-dial/results/units.parquet"
EPOCH = dt.datetime(2025, 1, 1, tzinfo=dt.timezone.utc)
MIN_CALLS_PRESENT = 20


def secs(col: str, alias: str | None = None) -> pl.Expr:
    return ((pl.col(col) - pl.lit(EPOCH)).dt.total_microseconds() / 1e6).alias(alias or col)


def load_shared(allow_holdout: bool = False):
    cw = (pl.scan_parquet(SH / "call_windows.parquet")
          .filter(pl.lit(allow_holdout) | ~pl.col("holdout"))
          .filter(pl.col("ctx_mode") != "summary")
          .select("turn_id", "agent", "pt_date", "goal_no", "talk", "t_call", "t_first")
          .collect())
    lt = (pl.scan_parquet(SH / "context_ledger_turns.parquet")
          .filter(pl.lit(allow_holdout) | ~pl.col("holdout"))
          .select("turn_id", "room").collect())
    cc = (pl.scan_parquet(SH / "chat_core.parquet")
          .filter((pl.col("speaker_kind") == "agent") & (pl.lit(allow_holdout) | ~pl.col("pt_date").is_in(
              pl.read_parquet(SH / "calendar.parquet").filter(pl.col("holdout"))["pt_date"].to_list())))
          .select("t", "pt_date", "goal_no", "room", "agent").collect())
    kk = (pl.read_parquet(SH / "kicks_classified.parquet")
          .filter(pl.col("kind") == "human_message")
          .filter(pl.lit(allow_holdout) | ~pl.col("holdout"))
          .select("t", "pt_date", "goal_no", "room", "subkind"))
    cal = pl.read_parquet(SH / "calendar.parquet")
    gp = cal.filter(pl.col("goal_no").is_not_null()).group_by("goal_no").agg(pl.col("pt_date").min().alias("first_day"))
    return cw, lt, cc, kk, cal, gp


def build_unit(u: dict, cw, lt, cc, kk, cal, gp, out: Path = OUT, allow_holdout: bool = False) -> dict | None:
    days = sorted(u["days"])
    if not allow_holdout:
        held = holdout_mask(days, [u["goal_no"]] * len(days))
        assert not any(held), f"holdout day in unit {u['unit_id']}"
        assert not cal.filter(pl.col("pt_date").is_in(days) & pl.col("holdout")).height, "calendar holdout"
    s, e = u["start"], u["end"]
    dmap = {d: k for k, d in enumerate(days)}
    calls = (cw.filter(pl.col("pt_date").is_in(days) & (pl.col("goal_no") == u["goal_no"])
                       & (pl.col("t_call") >= s) & (pl.col("t_call") < e))
             .join(lt, on="turn_id", how="left")
             .with_columns(secs("t_call"), secs("t_first"),
                           pl.col("pt_date").replace_strict(dmap, return_dtype=pl.Int16).alias("day"))
             .select("agent", "day", "t_call", "t_first", "talk", "room").sort("day", "agent", "t_call"))
    if calls.height == 0:
        return None
    pres = (calls.group_by("day", "agent")
            .agg(pl.len().alias("n_calls"), pl.col("t_call").min().alias("f"), pl.col("t_call").max().alias("l"),
                 pl.col("room").drop_nulls().mode().first().alias("room"))
            .filter(pl.col("n_calls") >= MIN_CALLS_PRESENT).sort("day", "agent"))
    ap = pres.group_by("day").agg(pl.col("f").max().alias("ap_lo"), pl.col("l").min().alias("ap_hi"),
                                  pl.len().alias("n_present"))
    calw = (cal.filter(pl.col("pt_date").is_in(days))
            .with_columns(secs("win_start"), secs("win_end"),
                          pl.col("pt_date").replace_strict(dmap, return_dtype=pl.Int16).alias("day"))
            .select("day", "pt_date", "win_start", "win_end"))
    g = gp.filter(pl.col("goal_no") == u["goal_no"])
    kick_day = str(g["first_day"][0])[:10] if g.height else None
    dd = (ap.join(calw, on="day", how="left").sort("day")
          .with_columns((pl.col("pt_date") == pl.lit(kick_day)).fill_null(False).alias("kickoff_day")))
    msgs = (cc.filter(pl.col("pt_date").is_in(days) & (pl.col("goal_no") == u["goal_no"])
                      & (pl.col("t") >= s) & (pl.col("t") < e))
            .with_columns(secs("t"), pl.col("pt_date").replace_strict(dmap, return_dtype=pl.Int16).alias("day"))
            .select("t", "day", "agent", "room").sort("t"))
    exo = (kk.filter(pl.col("pt_date").is_in(days) & (pl.col("t") >= s) & (pl.col("t") < e))
           .with_columns(secs("t"), pl.col("pt_date").replace_strict(dmap, return_dtype=pl.Int16).alias("day"))
           .select("t", "day", "room", "subkind"))
    uid = u["unit_id"]
    for sub, df in (("calls", calls), ("msgs", msgs), ("days", dd), ("present", pres.drop("f", "l")), ("exo", exo)):
        (out / sub).mkdir(parents=True, exist_ok=True)
        df.write_parquet(out / sub / f"{uid}.parquet", compression="zstd")
    return {"unit_id": uid, "goal_no": u["goal_no"], "regime": u["regime"], "n_days": len(days),
            "first_day": days[0], "last_day": days[-1], "kick_day": kick_day,
            "n_calls": calls.height, "n_msgs": msgs.height, "n_exo": exo.height,
            "n_present_mean": float(ap["n_present"].mean()) if ap.height else 0.0}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--units", default="")
    a = ap.parse_args()
    pu = pl.read_parquet(SH / "period_units.parquet").filter(~pl.col("holdout"))
    ok = pl.read_parquet(H67).filter(pl.col("ok"))["unit_id"].to_list()
    pu = pu.filter(pl.col("unit_id").is_in(ok))
    if a.units:
        pu = pu.filter(pl.col("unit_id").is_in(a.units.split(",")))
    cw, lt, cc, kk, cal, gp = load_shared()
    meta = []
    for u in pu.iter_rows(named=True):
        r = build_unit(u, cw, lt, cc, kk, cal, gp)
        if r:
            meta.append(r)
            print(r["unit_id"], r["n_days"], r["n_msgs"], flush=True)
    if not a.units:
        pl.DataFrame(meta).write_parquet(OUT / "unit_meta.parquet")
        prov = {"built_by": "hypotheses/H111-talk-fano-sum-rule/scheme/build.py", "git_commit": git_commit(),
                "inputs": [{"source": "ai-village", "tables": ["call_windows", "context_ledger_turns", "chat_core",
                                                                "kicks_classified", "calendar",
                                                                "period_units"]},
                           {"source": "H67", "tables": ["results/units.parquet (unit list only)"]}],
                "params": {"min_calls_present": MIN_CALLS_PRESENT, "epoch": EPOCH.isoformat()},
                "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
        (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    main()
