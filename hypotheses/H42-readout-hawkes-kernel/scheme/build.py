"""H42 scheme: per-unit event tables for read-out Hawkes fits, built from shared tables only.

For every non-holdout period unit (data/processed/shared/period_units.parquet) and each of its village days, writes
(times are float seconds since the realization's start = max(calendar win_start, unit start)):

  G<NN>/days.parquet   unit_id, day (int, per unit), pt_date, t0 (UTC), T (s), first_goal_day, regime
  G<NN>/calls.parquet  unit_id, day, agent, turn_id, t_call, t_lo, t_hi, t_first, t_end, recv (ctx_mode != summary),
                       talk, kind, ctx_mode, gap_kind, start_conf, wake, reset_forced, reset_consol, reset_session, k_new
  G<NN>/talk.parquet   unit_id, day, agent, t, room, turn_id (the talk call it belongs to)
  G<NN>/items.parquet  unit_id, day, recipient, sender (-1 = human/automated), kind, s (posting time), turn_id
                       (receiving call), ment, uncertain, room. Same-day only (posted inside the realization).
  G<NN>/mask.parquet   unit_id, day, m0, m1: masked village-off gaps (>= 10 min with no agent call in progress,
                       rebuilt from call_windows; the shared stall tables derive from the buggy activity_bins)

The Claude Code agent is never a recipient (no call_windows rows), but its messages are items for others.
Holdout is asserted twice (calendar/period_units flag and infra/shared/common.py: holdout_mask). No text is read.

Usage: uv run python hypotheses/H42-readout-hawkes-kernel/scheme/build.py [--period G38]
"""
from __future__ import annotations

import datetime as dt
import json
import os
import subprocess
import sys
from pathlib import Path

os.environ.setdefault("POLARS_MAX_THREADS", "2")
import polars as pl  # noqa: E402

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H42-readout-hawkes-kernel"
WAKE_GAPS = ["pause", "pause_early", "first_of_day", "marker", "session_start"]
OFF_GAP_S = 600.0   # village-off: >= 10 min with no agent call in progress (H16/H38 rule, rebuilt on call_windows)


def secs(col: str, t0: str = "t0") -> pl.Expr:
    return ((pl.col(col) - pl.col(t0)).dt.total_microseconds() / 1e6).alias(col)


def git_commit() -> str:
    r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    dirty = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "hypotheses/H42-readout-hawkes-kernel"],
                           capture_output=True, text=True).stdout
    return (r.stdout.strip() or "none") + ("+uncommitted" if dirty.strip() else "")


def realizations(holdout_units: list[str] | None = None) -> pl.DataFrame:
    """Non-holdout units (default). holdout_units: build exactly these held-out units (confirm.py only, guarded)."""
    pu = pl.read_parquet(SH / "period_units.parquet")
    if holdout_units is None:
        pu = pu.filter(~pl.col("holdout"))
    else:
        pu = pu.filter(pl.col("unit_id").is_in(holdout_units))
    cal = pl.read_parquet(SH / "calendar.parquet")
    goal_first = cal.group_by("goal_no").agg(pl.col("pt_date").min().alias("goal_first"))
    rows = (pu.select("unit_id", "goal_no", "start", "end", "days", "regime").explode("days").rename({"days": "pt_date"})
            .join(cal.select("pt_date", "win_start", "win_end", pl.col("holdout").alias("cal_holdout")), on="pt_date")
            .join(goal_first, on="goal_no"))
    if holdout_units is None:
        assert not rows["cal_holdout"].any(), "holdout day in a non-holdout unit"
        hm = holdout_mask(rows["pt_date"].to_list(), rows["goal_no"].to_list())
        assert not any(hm), "holdout_mask flags a day in a non-holdout unit"
    rows = rows.with_columns(
        pl.max_horizontal("win_start", "start").alias("t0"), pl.min_horizontal("win_end", "end").alias("t1"),
        (pl.col("pt_date") == pl.col("goal_first")).alias("first_goal_day"))
    rows = rows.filter(pl.col("t1") > pl.col("t0")).sort("unit_id", "t0")
    rows = rows.with_columns(pl.int_range(pl.len()).over("unit_id").cast(pl.Int16).alias("day"),
                             ((pl.col("t1") - pl.col("t0")).dt.total_microseconds() / 1e6).alias("T"))
    return rows.select("unit_id", "goal_no", "day", "pt_date", "t0", "t1", "T", "first_goal_day", "regime")


def build(goals: list[int] | None = None, holdout_units: list[str] | None = None, out_root: Path | None = None):
    global OUT
    if out_root is not None:
        OUT = out_root
    R = realizations(holdout_units)
    if goals:
        R = R.filter(pl.col("goal_no").is_in(goals))
    dates = R["pt_date"].unique().to_list()
    hflt = ~pl.col("holdout") if holdout_units is None else pl.lit(True)
    cw = (pl.scan_parquet(SH / "call_windows.parquet").filter(pl.col("pt_date").is_in(dates) & hflt)
          .select("turn_id", "agent", "pt_date", "goal_no", "kind", "talk", "ctx_mode", "t_call", "t_call_lo",
                  "t_call_hi", "start_conf", "t_first", "t_end", "gap_kind").collect())
    lt = (pl.scan_parquet(SH / "context_ledger_turns.parquet").filter(pl.col("pt_date").is_in(dates))
          .select("turn_id", "reset_forced", "reset_consol", "reset_session", "k_new").collect())
    cw = cw.join(lt, on="turn_id", how="left")
    cc = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "pt_date", "goal_no", "room",
                                                             "speaker_kind", "agent"])
    it = (pl.scan_parquet(SH / "context_ledger_items.parquet")
          .filter(pl.col("turn_id").is_in(cw["turn_id"].implode()))
          .select("turn_id", "message_id", "sender", "kind", "ment", "uncertain").collect())
    for g in sorted(R["goal_no"].unique().to_list()):
        Rg = R.filter(pl.col("goal_no") == g)
        out = OUT / f"G{g:02d}"
        out.mkdir(parents=True, exist_ok=True)
        key = Rg.select("unit_id", "day", "pt_date", "t0", "t1")
        # calls: assign to the realization whose window holds the call record (split days handled by t0/t1)
        c = (cw.filter(pl.col("goal_no") == g).join(key, on="pt_date")
             .filter((pl.col("t_first") >= pl.col("t0")) & (pl.col("t_first") <= pl.col("t1"))))
        c = c.with_columns((pl.col("ctx_mode") != "summary").alias("recv"),
                           pl.col("gap_kind").cast(pl.String).is_in(WAKE_GAPS).alias("wake"),
                           *[secs(x) for x in ("t_call", "t_call_lo", "t_call_hi", "t_first", "t_end")])
        c = (c.rename({"t_call_lo": "t_lo", "t_call_hi": "t_hi"})
             .select("unit_id", "day", "agent", "turn_id", "t_call", "t_lo", "t_hi", "t_first", "t_end", "recv", "talk",
                     pl.col("kind").cast(pl.String), pl.col("ctx_mode").cast(pl.String), pl.col("gap_kind").cast(pl.String),
                     pl.col("start_conf").cast(pl.String), "wake", pl.col("reset_forced").fill_null(False),
                     pl.col("reset_consol").fill_null(False), pl.col("reset_session").fill_null(False),
                     pl.col("k_new").fill_null(0))
             .sort("unit_id", "day", "agent", "t_call"))
        # talk events: agent messages of calling agents, as-of mapped to their talk call
        m = (cc.filter((pl.col("goal_no") == g) & (pl.col("speaker_kind") == "agent")).join(key, on="pt_date")
             .filter((pl.col("t") >= pl.col("t0")) & (pl.col("t") <= pl.col("t1"))))
        tc = (cw.filter((pl.col("goal_no") == g) & pl.col("talk")).select("agent", "turn_id", "t_first").sort("t_first"))
        m_call = m.filter(pl.col("agent").is_in(c["agent"].unique().implode())).sort("t")
        m_call = m_call.join_asof(tc, left_on="t", right_on="t_first", by="agent", strategy="backward",
                                  check_sortedness=False)
        talk = (m_call.with_columns(secs("t")).select("unit_id", "day", "agent", "t", "room", "turn_id")
                .sort("unit_id", "day", "agent", "t"))
        # items: same-day ledger items of receiving calls in these realizations
        cm = c.select("turn_id", "unit_id", "day", pl.col("agent").alias("recipient"))
        ii = (it.join(cm, on="turn_id").join(cc.select("message_id", pl.col("t").alias("s_abs"), "room"), on="message_id")
              .join(key.select("unit_id", "day", "t0", "t1"), on=["unit_id", "day"])
              .filter((pl.col("s_abs") >= pl.col("t0")) & (pl.col("s_abs") <= pl.col("t1")))
              .with_columns(((pl.col("s_abs") - pl.col("t0")).dt.total_microseconds() / 1e6).alias("s"))
              .select("unit_id", "day", "recipient", pl.col("sender").fill_null(-1), pl.col("kind").cast(pl.String),
                      "s", "turn_id", "ment", "uncertain", "room")
              .sort("unit_id", "day", "recipient", "s"))
        # masks: village-off gaps rebuilt from call_windows (>= OFF_GAP_S with no agent call in progress, i.e. outside
        # the union of all agents' [t_call, t_end]); the shared stall_minutes / outages derive from the buggy
        # activity_bins (coordinator notice 2026-10-04: joint silences over-counted; 6% of talk fell inside them).
        merged = []
        for (u, d), grp in c.group_by(["unit_id", "day"], maintain_order=True):
            T = float(Rg.filter((pl.col("unit_id") == u) & (pl.col("day") == d))["T"][0])
            iv = grp.select(pl.col("t_call").clip(0.0, T).alias("a"),
                            pl.max_horizontal("t_end", "t_first").clip(0.0, T).alias("b")).sort("a")
            edge = 0.0
            for a, b in zip(iv["a"].to_list(), iv["b"].to_list()):
                if a - edge >= OFF_GAP_S:
                    merged.append((u, d, edge, a))
                edge = max(edge, b)
            if T - edge >= OFF_GAP_S:
                merged.append((u, d, edge, T))
        mask = pl.DataFrame(merged, schema={"unit_id": pl.String, "day": pl.Int16, "m0": pl.Float64, "m1": pl.Float64},
                            orient="row")
        days = Rg.select("unit_id", "day", "pt_date", "t0", "T", "first_goal_day", "regime")
        for name, df in (("days", days), ("calls", c), ("talk", talk), ("items", ii), ("mask", mask)):
            df.write_parquet(out / f"{name}.parquet", compression="zstd")
        print(f"G{g:02d}: {len(days)} unit-days, {len(c)} calls, {len(talk)} msgs, {len(ii)} items, {len(mask)} masks",
              flush=True)

    prov_path = OUT / "_provenance.json"
    prov = {"built_by": "hypotheses/H42-readout-hawkes-kernel/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["shared/call_windows", "shared/context_ledger_turns", "shared/context_ledger_items",
                                   "shared/chat_core", "shared/calendar", "shared/period_units"]}],
            "params": {"wake_gaps": WAKE_GAPS, "mask": "village-off gaps >= 600 s outside the union of all agents' [t_call, t_end] (call_windows); shared stall_minutes/outages not used (activity_bins bug)",
                       "times": "seconds since max(win_start, unit start)", "holdout": "excluded (asserted twice)"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    if prov_path.exists():
        old = json.loads(prov_path.read_text())
        old.update({k: v for k, v in prov.items()})
        prov = old
    prov_path.write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    goals = None
    if "--period" in sys.argv:
        goals = [int(x.strip().lstrip("Gg#")) for x in sys.argv[sys.argv.index("--period") + 1].split(",")]
    build(goals)
