"""H85 scheme: per-unit outputs Y, scheduled hours T and active population N (no text; holdout dropped).

Inputs (data/processed/shared/): period_units, period_affordances (mode, git_dense, active_hours), calendar (windows),
activity_bins_fixed (active population), chat_core + chat_mentions_clean (messages, addressed pairs), reply_pairs (DQ2
parents), work_commits (DQ4 agent work), context_ledger_turns (talk calls, k_since_talk), rooms_timeline, roster.
Output (data/processed/H85-output-scaling-with-n/):
  units.parquet        one row per eligible non-holdout period unit: T_h, N (active, roster, span), outputs, covariates
  days.parquet         one row per (unit, pt_date): n_d, h_d and the same outputs (for the #51 sweep)
  agent_units.parquet  one row per (unit, agent): present hours and outputs (for NE42 per-agent rates)
  room_days.parquet    one row per (unit, pt_date, room) in multi-room units: room population and outputs (G38)
  _provenance.json
Rules: a record belongs to the unit whose [start, end) holds its timestamp; T = overlap of calendar windows with the
unit; N = hour-weighted mean of agents with >= 1 record per day; Claude Code agents excluded throughout.
Usage: uv run python hypotheses/H85-output-scaling-with-n/scheme/build.py
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
OUT = ROOT / "data/processed/H85-output-scaling-with-n"
SHARED_MODES = {"C", "M"}  # shared objective, teams; everything else (I, F, K, I/K) is own-artifact


def git_commit() -> str:
    r = subprocess.run(["git", "-C", str(ROOT), "rev-parse", "--short", "HEAD"], capture_output=True, text=True)
    d = subprocess.run(["git", "-C", str(ROOT), "status", "--porcelain", "hypotheses/H85-output-scaling-with-n"],
                       capture_output=True, text=True).stdout
    return (r.stdout.strip() or "none") + ("+uncommitted" if d.strip() else "")


def load_units(include_holdout: bool = False) -> pl.DataFrame:
    pu = pl.read_parquet(SH / "period_units.parquet")
    if not include_holdout:
        pu = pu.filter(~pl.col("holdout"))
    pa = pl.read_parquet(SH / "period_affordances.parquet").select("unit_id", "mode", "git_dense", "active_hours")
    return (pu.join(pa, on="unit_id", how="left")
            .with_columns(pl.col("mode").is_in(list(SHARED_MODES)).alias("shared_mode"))
            .sort("start"))


def assign(df: pl.DataFrame, units: pl.DataFrame, tcol: str = "t") -> pl.DataFrame:
    """Attach unit_id by as-of join on start, keep rows with t < end."""
    u = units.select("unit_id", "start", "end").sort("start")
    df = df.with_columns(pl.col(tcol).cast(pl.Datetime("us", "UTC"))).sort(tcol)
    out = df.join_asof(u, left_on=tcol, right_on="start", strategy="backward")
    return out.filter(pl.col("unit_id").is_not_null() & (pl.col(tcol) < pl.col("end"))).drop("start", "end")


def build(include_holdout: bool = False):
    units = load_units(include_holdout)
    cc = set(pl.read_parquet(SH / "roster.parquet").filter(pl.col("claude_code"))["agent"].to_list())
    cal = pl.read_parquet(SH / "calendar.parquet").select("pt_date", "win_start", "win_end", "goal_no")
    days_ok = cal.filter(~pl.Series(holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())))["pt_date"]
    if include_holdout:
        days_ok = cal["pt_date"]

    # ---- unit-day hours: overlap of the calendar window with the unit
    ud = (units.select("unit_id", "start", "end", "days").explode("days").rename({"days": "pt_date"})
          .join(cal.select("pt_date", "win_start", "win_end"), on="pt_date", how="inner")
          .with_columns(pl.max_horizontal("win_start", "start").alias("lo"), pl.min_horizontal("win_end", "end").alias("hi"))
          .with_columns(((pl.col("hi") - pl.col("lo")).dt.total_seconds() / 3600).clip(lower_bound=0).alias("h_d"))
          .filter(pl.col("h_d") > 0).select("unit_id", "pt_date", "h_d", "win_start"))

    # ---- active population from the minute grid
    ab = (pl.scan_parquet(SH / "activity_bins_fixed.parquet")
          .filter(pl.col("pt_date").is_in(days_ok.to_list()))
          .with_columns((pl.col("talk") + pl.col("idle") + pl.col("consolidate") + pl.col("other_event") + pl.col("turns"))
                        .alias("rec"))
          .filter(pl.col("rec") > 0).select("pt_date", "minute", "agent").collect())
    ab = (ab.join(cal.select("pt_date", "win_start"), on="pt_date")
          .with_columns((pl.col("win_start") + pl.duration(minutes=pl.col("minute"))).alias("t"))
          .filter(~pl.col("agent").is_in(list(cc))))
    ab = assign(ab, units)
    pres = (ab.group_by("unit_id", "pt_date", "agent")
            .agg(pl.col("minute").min().alias("m0"), pl.col("minute").max().alias("m1"))
            .with_columns(((pl.col("m1") - pl.col("m0") + 1) / 60).alias("span_h")))
    nd = pres.group_by("unit_id", "pt_date").agg(pl.len().alias("n_d"), pl.col("span_h").sum().alias("span_h"))

    # ---- messages and addressed pairs
    cm = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "pt_date", "goal_no", "room", "speaker_kind", "agent"])
    cm = cm.filter((pl.col("speaker_kind") == "agent") & pl.col("agent").is_not_null()
                   & ~pl.col("agent").is_in(list(cc)) & pl.col("pt_date").is_in(days_ok.to_list()))
    ment = pl.read_parquet(SH / "chat_mentions_clean.parquet", columns=["message_id", "mentions_roster"])
    cm = cm.join(ment, on="message_id", how="left")
    cm = cm.with_columns(
        pl.col("mentions_roster").fill_null([]).list.unique()
        .list.eval(pl.element()).alias("mr"))
    cm = cm.with_columns((pl.col("mr").list.len() - pl.col("mr").list.contains(pl.col("agent")).cast(pl.Int32)).alias("ment"))
    cm = assign(cm.drop("mentions_roster", "mr"), units)

    # ---- reply parents (DQ2): B's parent, cand set
    rp = (pl.scan_parquet(SH / "reply_pairs.parquet")
          .filter(pl.col("parent") & (pl.col("pair_set") == "cand"))
          .select("B_message_id", "a_kind").collect())
    cm = (cm.join(rp.rename({"B_message_id": "message_id"}), on="message_id", how="left")
          .with_columns((pl.col("a_kind") == 0).fill_null(False).cast(pl.Int32).alias("reply"),
                        pl.col("a_kind").is_not_null().cast(pl.Int32).alias("reply_any"))
          .drop("a_kind"))

    # ---- agent work commits
    wc = (pl.scan_parquet(SH / "work_commits.parquet")
          .filter(pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind") == "agent") & ~pl.col("automated")
                  & pl.col("author_agent").is_not_null())
          .select("t", "pt_date", "goal_no", "repo", pl.col("author_agent").alias("agent")).collect())
    wc = wc.filter(~pl.col("agent").is_in(list(cc)) & pl.col("pt_date").is_in(days_ok.to_list()))
    wc = assign(wc.with_columns(pl.col("repo").cast(pl.String)), units)

    # ---- talk calls and pending sets (context ledger)
    lt = (pl.scan_parquet(SH / "context_ledger_turns.parquet")
          .filter(pl.col("talk") & pl.col("pt_date").is_in(days_ok.to_list()))
          .select("agent", "pt_date", pl.col("t_call").alias("t"), "room", "k_since_talk").collect())
    lt = assign(lt.filter(~pl.col("agent").is_in(list(cc)) & pl.col("t").is_not_null()), units)

    # ---- holdout guard
    for name, df in (("activity", ab), ("chat", cm), ("commits", wc), ("ledger", lt)):
        if not include_holdout and df.height:
            g = df.join(cal.select("pt_date", pl.col("goal_no").alias("g_cal")), on="pt_date", how="left")
            hm = holdout_mask(g["pt_date"].to_list(), g["g_cal"].to_list())
            assert not any(hm), f"held-out rows in {name}"

    # ---- per (unit, day)
    def agg_day(keys):
        a = cm.group_by(keys).agg(pl.len().alias("msg"), pl.col("ment").sum().alias("ment"),
                                  (pl.col("ment") > 0).sum().alias("ment_msgs"),
                                  pl.col("reply").sum().alias("reply"), pl.col("reply_any").sum().alias("reply_any"))
        b = wc.group_by(keys).agg(pl.len().alias("commit"), pl.col("repo").n_unique().alias("repos"))
        c = lt.group_by(keys).agg(pl.len().alias("talk_calls"), pl.col("k_since_talk").sum().alias("k_sum"),
                                  pl.col("k_since_talk").is_not_null().sum().alias("k_n"))
        return a, b, c

    a, b, c = agg_day(["unit_id", "pt_date"])
    days = (ud.join(nd, on=["unit_id", "pt_date"], how="left")
            .join(a, on=["unit_id", "pt_date"], how="left").join(b, on=["unit_id", "pt_date"], how="left")
            .join(c, on=["unit_id", "pt_date"], how="left")
            .with_columns(pl.col(x).fill_null(0) for x in ("n_d", "span_h", "msg", "ment", "ment_msgs", "reply", "reply_any", "commit",
                                                            "repos", "talk_calls", "k_sum", "k_n"))
            .filter(pl.col("n_d") > 0).sort("unit_id", "pt_date"))

    # ---- per unit
    uo = (days.group_by("unit_id").agg(
        pl.col("h_d").sum().alias("T_h"), pl.len().alias("n_daysw"),
        ((pl.col("n_d") * pl.col("h_d")).sum() / pl.col("h_d").sum()).alias("N"),
        (pl.col("span_h").sum() / pl.col("h_d").sum()).alias("N_span"),
        *[pl.col(x).sum() for x in ("msg", "ment", "ment_msgs", "reply", "reply_any", "commit", "talk_calls", "k_sum", "k_n")],
        pl.col("repos").mean().alias("repos_day"))
        .with_columns((pl.col("k_sum") / pl.col("k_n")).alias("k_talk"),
                      (pl.col("T_h") / pl.col("n_daysw")).alias("h_day")))
    unit_repos = wc.group_by("unit_id").agg(pl.col("repo").n_unique().alias("repos_unit"))
    uo = (units.select("unit_id", "goal_no", "seq", "first_day", "last_day", "n_days", "n_agents", "n_roster", "rooms",
                       "regime", "mode", "shared_mode", "git_dense", "active_hours", "start", "end")
          .join(uo, on="unit_id", how="inner").join(unit_repos, on="unit_id", how="left")
          .with_columns(pl.col("repos_unit").fill_null(0)).sort("start"))

    # ---- per (unit, agent)
    ap = pres.join(ud.select("unit_id", "pt_date", "h_d"), on=["unit_id", "pt_date"]).group_by("unit_id", "agent").agg(
        pl.col("h_d").sum().alias("present_h"), pl.len().alias("days_present"))
    aa, bb, cc_ = agg_day(["unit_id", "agent"])
    agent_units = (ap.join(aa, on=["unit_id", "agent"], how="left").join(bb, on=["unit_id", "agent"], how="left")
                   .join(cc_, on=["unit_id", "agent"], how="left")
                   .with_columns(pl.col(x).fill_null(0) for x in ("msg", "ment", "ment_msgs", "reply", "reply_any", "commit", "repos",
                                                                   "talk_calls", "k_sum", "k_n")))

    # ---- room days (multi-room units): room population = active agents whose room interval covers the window midpoint
    multi = units.filter(pl.col("rooms").list.len() > 1)["unit_id"].to_list()
    rt = pl.read_parquet(SH / "rooms_timeline.parquet")
    mid = (ud.filter(pl.col("unit_id").is_in(multi)).join(cal.select("pt_date", "win_end"), on="pt_date")
           .with_columns((pl.col("win_start") + (pl.col("win_end") - pl.col("win_start")) / 2).alias("t_mid")))
    pr = pres.filter(pl.col("unit_id").is_in(multi)).join(mid.select("unit_id", "pt_date", "t_mid"), on=["unit_id", "pt_date"])
    pr = (pr.join(rt, on="agent", how="inner")
          .filter((pl.col("t_start") <= pl.col("t_mid")) & (pl.col("t_end").is_null() | (pl.col("t_end") > pl.col("t_mid"))))
          .sort("t_start").group_by("unit_id", "pt_date", "agent").agg(pl.col("room").last()))
    nroom = pr.group_by("unit_id", "pt_date", "room").agg(pl.len().alias("n_room"))
    cmm, lmm = cm.filter(pl.col("unit_id").is_in(multi)), lt.filter(pl.col("unit_id").is_in(multi))
    ra = cmm.group_by("unit_id", "pt_date", "room").agg(pl.len().alias("msg"), pl.col("ment").sum().alias("ment"),
                                                        pl.col("reply").sum().alias("reply"))
    rc = lmm.group_by("unit_id", "pt_date", "room").agg(pl.len().alias("talk_calls"), pl.col("k_since_talk").mean().alias("k_talk"))
    room_days = (nroom.join(ra, on=["unit_id", "pt_date", "room"], how="left").join(rc, on=["unit_id", "pt_date", "room"], how="left")
                 .join(ud.select("unit_id", "pt_date", "h_d"), on=["unit_id", "pt_date"])
                 .with_columns(pl.col(x).fill_null(0) for x in ("msg", "ment", "reply", "talk_calls"))
                 .sort("unit_id", "pt_date", "room"))
    return uo, days, agent_units, room_days


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    uo, days, agent_units, room_days = build()
    uo.write_parquet(OUT / "units.parquet", compression="zstd")
    days.write_parquet(OUT / "days.parquet", compression="zstd")
    agent_units.write_parquet(OUT / "agent_units.parquet", compression="zstd")
    room_days.write_parquet(OUT / "room_days.parquet", compression="zstd")
    prov = {"built_by": "hypotheses/H85-output-scaling-with-n/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["shared/period_units", "shared/period_affordances", "shared/calendar",
                                   "shared/activity_bins_fixed", "shared/chat_core", "shared/chat_mentions_clean",
                                   "shared/reply_pairs", "shared/work_commits", "shared/context_ledger_turns",
                                   "shared/rooms_timeline", "shared/roster"]}],
            "params": {"shared_modes": sorted(SHARED_MODES), "work_filter": "canonical & ~imported & agent & ~automated",
                       "reply": "parent & pair_set=cand (a_kind=0 for agent parents)", "holdout": "dropped"},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (OUT / "_provenance.json").write_text(json.dumps(prov, indent=1))
    print(f"units {uo.height}  days {days.height}  agent_units {agent_units.height}  room_days {room_days.height}")


if __name__ == "__main__":
    main()
