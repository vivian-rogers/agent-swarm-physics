"""H86 scheme: per-agent bin counts on raw and DQ8-trimmed grids, four channels (no text; holdout dropped).

Inputs (data/processed/shared/): period_units, calendar, activity_bins_fixed (records, presence spans), call_windows
(per-call clock, H40), chat_core (agent messages), work_commits (DQ4 agent work), roster.
Output (data/processed/H86-taylor-law-field-gauge/):
  bins15.parquet  one row per (unit, pt_date, bin, agent) for present agent-days, 15-min clock bins of the window:
                  activity (turns + talk + other_event + consolidate), calls, msg; trim = bin wholly inside the
                  day's all-present window (every present agent between its first and last record)
  bins60.parquet  the same with 60-min bins and channel commit (agent work commits)
  spans.parquet   one row per present agent-day: first/last record minute (m0, m1) and the day's window [M0, M1]
  _provenance.json
Presence: >= 1 record that day in activity_bins_fixed; span = first..last record minute (DQ8 / H38 rule).
Partial bins at the end of a window are dropped. Claude Code agents excluded.
Usage: uv run python hypotheses/H86-taylor-law-field-gauge/scheme/build.py
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")
import datetime as dt  # noqa: E402
import json  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra" / "shared"))
from common import REVISION, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H86-taylor-law-field-gauge"


def git_commit() -> str:
    r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    d = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "hypotheses/H86-taylor-law-field-gauge"],
                       capture_output=True, text=True).stdout
    return (r.stdout.strip() or "none") + ("+uncommitted" if d.strip() else "")


def build(include_holdout: bool = False, only_days: list[str] | None = None):
    pu = pl.read_parquet(SH / "period_units.parquet")
    if not include_holdout:
        pu = pu.filter(~pl.col("holdout"))
    units = pu.select("unit_id", "goal_no", "regime", "start", "end").sort("start")
    cc = set(pl.read_parquet(SH / "roster.parquet").filter(pl.col("claude_code"))["agent"].to_list())
    cal = pl.read_parquet(SH / "calendar.parquet").select("pt_date", "win_start", "window_s", "goal_no")
    hm = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    cal = cal.with_columns(pl.Series("held", hm))
    if not include_holdout:
        cal = cal.filter(~pl.col("held"))
    if only_days is not None:
        cal = cal.filter(pl.col("pt_date").is_in(only_days))
    days = cal["pt_date"].to_list()

    ab = (pl.scan_parquet(SH / "activity_bins_fixed.parquet").filter(pl.col("pt_date").is_in(days))
          .with_columns((pl.col("turns") + pl.col("talk") + pl.col("other_event") + pl.col("consolidate")).alias("activity"),
                        (pl.col("turns") + pl.col("talk") + pl.col("other_event") + pl.col("consolidate") + pl.col("idle")).alias("rec"))
          .select("pt_date", "minute", "agent", "activity", "rec").collect()
          .filter(~pl.col("agent").is_in(list(cc))))
    span = (ab.filter(pl.col("rec") > 0).group_by("pt_date", "agent")
            .agg(pl.col("minute").min().alias("m0"), pl.col("minute").max().alias("m1")))
    win = span.group_by("pt_date").agg(pl.col("m0").max().alias("M0"), pl.col("m1").min().alias("M1"), pl.len().alias("n_present"))

    def minute_of(df, tcol):
        return (df.join(cal.select("pt_date", "win_start", "window_s"), on="pt_date")
                .with_columns(((pl.col(tcol) - pl.col("win_start")).dt.total_seconds() // 60).cast(pl.Int64).alias("minute"))
                .filter((pl.col("minute") >= 0) & (pl.col("minute") * 60 < pl.col("window_s")))
                .select("pt_date", "minute", "agent"))

    cw = (pl.scan_parquet(SH / "call_windows.parquet").filter(pl.col("pt_date").is_in(days))
          .select("pt_date", "agent", "t_call").collect().filter(pl.col("t_call").is_not_null() & ~pl.col("agent").is_in(list(cc))))
    calls = minute_of(cw, "t_call").group_by("pt_date", "minute", "agent").agg(pl.len().alias("calls"))
    cm = pl.read_parquet(SH / "chat_core.parquet", columns=["t", "pt_date", "speaker_kind", "agent"])
    cm = cm.filter((pl.col("speaker_kind") == "agent") & pl.col("agent").is_not_null() & pl.col("pt_date").is_in(days)
                   & ~pl.col("agent").is_in(list(cc)))
    msg = minute_of(cm, "t").group_by("pt_date", "minute", "agent").agg(pl.len().alias("msg"))
    wc = (pl.scan_parquet(SH / "work_commits.parquet")
          .filter(pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind") == "agent") & ~pl.col("automated")
                  & pl.col("author_agent").is_not_null() & pl.col("pt_date").is_in(days))
          .select("t", "pt_date", pl.col("author_agent").alias("agent")).collect().filter(~pl.col("agent").is_in(list(cc))))
    com = minute_of(wc, "t").group_by("pt_date", "minute", "agent").agg(pl.len().alias("commit"))

    # minute table for present agent-days (the dense grid restricted to present agents)
    m = (ab.join(span.select("pt_date", "agent"), on=["pt_date", "agent"], how="inner")
         .join(calls, on=["pt_date", "minute", "agent"], how="left").join(msg, on=["pt_date", "minute", "agent"], how="left")
         .join(com, on=["pt_date", "minute", "agent"], how="left")
         .with_columns(pl.col(c).fill_null(0) for c in ("calls", "msg", "commit")))

    out = {}
    for width in (15, 60):
        b = (m.with_columns((pl.col("minute") // width).alias("bin"))
             .group_by("pt_date", "bin", "agent")
             .agg(pl.col("activity").sum(), pl.col("calls").sum(), pl.col("msg").sum(), pl.col("commit").sum(),
                  pl.len().alias("n_min")))
        b = (b.join(cal.select("pt_date", "win_start", "window_s"), on="pt_date").join(win, on="pt_date")
             .filter((pl.col("bin") + 1) * width * 60 <= pl.col("window_s"))                     # full bins only
             .with_columns(((pl.col("bin") * width >= pl.col("M0")) & ((pl.col("bin") + 1) * width - 1 <= pl.col("M1"))).alias("trim"),
                           (pl.col("win_start") + pl.duration(minutes=pl.col("bin") * width)).alias("t_bin")))
        b = b.sort("t_bin").join_asof(units.select("unit_id", "start", "end"), left_on="t_bin", right_on="start", strategy="backward")
        b = (b.filter(pl.col("unit_id").is_not_null() & (pl.col("t_bin") < pl.col("end")))
             .select("unit_id", "pt_date", "bin", "agent", "trim", "n_present", "activity", "calls", "msg", "commit")
             .with_columns(pl.col("activity").cast(pl.Int32), pl.col("calls").cast(pl.Int32), pl.col("msg").cast(pl.Int16),
                           pl.col("commit").cast(pl.Int16))
             .sort("unit_id", "pt_date", "bin", "agent"))
        out[width] = b
    if not include_holdout:
        for b in out.values():
            g = b.join(cal.select("pt_date", "goal_no"), on="pt_date", how="left")
            assert not any(holdout_mask(g["pt_date"].to_list(), g["goal_no"].to_list())), "held-out rows"
    return out[15], out[60], span.join(win, on="pt_date")


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    b15, b60, spans = build()
    spans.write_parquet(OUT / "spans.parquet", compression="zstd")
    b15.write_parquet(OUT / "bins15.parquet", compression="zstd")
    b60.drop("activity", "calls", "msg").write_parquet(OUT / "bins60.parquet", compression="zstd")
    prov = {"built_by": "hypotheses/H86-taylor-law-field-gauge/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["shared/period_units", "shared/calendar", "shared/activity_bins_fixed",
                                   "shared/call_windows", "shared/chat_core", "shared/work_commits", "shared/roster"]}],
            "params": {"bins_min": [15, 60], "activity": "turns+talk+other_event+consolidate",
                       "presence": ">=1 record (incl. idle) that day", "trim": "bin wholly inside [max m0, min m1]",
                       "work_filter": "canonical & ~imported & agent & ~automated", "holdout": "dropped"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print(f"bins15 {b15.height}  bins60 {b60.height}  units {b15['unit_id'].n_unique()}")


if __name__ == "__main__":
    main()
