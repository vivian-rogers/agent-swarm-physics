"""H103 scheme: 30-min agent windows with clocks (night, active-hour, wall, reset), slots, own call gaps (no text).

Writes data/processed/H103-nights-demagnetize/:
  windows.parquet   one row per eligible agent x 30-min window (DQ5 agent_win30 row `gid`), non-holdout:
                    agent, pt_date, goal_no, regime, unit_id, t_mid, slot (quarter of the day's window), day_idx
                    (active-day index within the goal's non-holdout days), hcum (active hours since the goal's first
                    non-holdout window start, summed over calendar windows), r_cum (the agent's resets since the goal's
                    first day), n_stmt
  days.parquet      per non-holdout day: goal, regime, unit, day_idx, win_start/end, night_before_h (wall hours since
                    the previous active day's window end), weekend_before (night_before_h > 30)
  gaps.parquet      the agent's own call-free intervals >= 60 min inside a day (agent, pt_date, g_start, g_end)
  periods.parquet   O1 eligible goal periods: t0 (kickoff), fit days, incumbents
  _provenance.json
Vectors are not copied: the analysis reads the shared agent_win30 / agent_day arrays by row.

Usage: uv run python hypotheses/H103-nights-demagnetize/scheme/build.py
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import numpy as np
import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import OUT, REVISION, git_commit, holdout_mask, load_holdout  # noqa: E402

DATA = ROOT / "data/processed/H103-nights-demagnetize"
EXCLUDE_AGENTS = {19, 28, 30}
EXCLUDE_GOALS = {23}            # H10's blind #22 -> #23 pair (H54 did the same)
O1_EXCLUDE = {2, 7, 23, 36}     # no kickoff / 2 days / blind / regime boundary in the first days
MIN_STMT = 2
FIT_DAYS = 5
GAP_MIN = 60.0


def main(include_goals=None, out_dir=None, tail_window=False):
    """include_goals / tail_window are for analysis/confirm.py only (locked holdout); defaults reproduce round 1."""
    global DATA
    if out_dir is not None:
        DATA = Path(out_dir)
    DATA.mkdir(parents=True, exist_ok=True)
    held = set(load_holdout()["goal_periods_held_out"]) - set(include_goals or [])
    cal = pl.read_parquet(OUT / "calendar.parquet").with_columns(pl.col("regime").cast(pl.String)).sort("pt_date")
    ho = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    if include_goals:
        ho = [h and not (g in include_goals or (tail_window and g == 51 and d >= "2026-09-07"))
              for h, g, d in zip(ho, cal["goal_no"].to_list(), cal["pt_date"].to_list())]
    cal = cal.with_columns(pl.Series("ho", ho))
    pu = pl.read_parquet(OUT / "period_units.parquet")
    day_unit = {d: u for u, ds in zip(pu["unit_id"].to_list(), pu["days"].to_list()) for d in ds}
    cal = cal.with_columns(pl.col("pt_date").replace_strict(day_unit, default=None).alias("unit_id"))
    cal = cal.with_columns((pl.col("win_start") - pl.col("win_end").shift(1)).dt.total_seconds().truediv(3600)
                           .alias("night_before_h"))
    days = cal.filter(~pl.col("ho") & ~pl.col("goal_no").is_in(list(EXCLUDE_GOALS | held)))
    days = days.with_columns(pl.int_range(pl.len()).over("goal_no").alias("day_idx"),
                             (pl.col("window_s") / 3600).alias("day_h"))
    days = days.with_columns((pl.col("day_h").cum_sum().over("goal_no") - pl.col("day_h")).alias("h_before"),
                             (pl.col("night_before_h") > 30).alias("weekend_before"))
    days.select("pt_date", "goal_no", "regime", "unit_id", "day_idx", "win_start", "win_end", "window_s", "day_h",
                "h_before", "night_before_h", "weekend_before").write_parquet(DATA / "days.parquet")

    # windows
    w = pl.read_parquet(OUT / "embeddings/agent_win30.parquet")
    w = w.filter(pl.col("pt_date").is_in(days["pt_date"].to_list()) & ~pl.col("agent").is_in(list(EXCLUDE_AGENTS))
                 & ((pl.col("n_chat") + pl.col("n_intent")) >= MIN_STMT))
    w = w.join(days.select("pt_date", "unit_id", "day_idx", "win_start", "window_s", "h_before"), on="pt_date",
               how="inner")
    w = w.with_columns((pl.col("win_start") + pl.duration(seconds=pl.col("win30").cast(pl.Int64) * 1800 + 900))
                       .alias("t_mid"))
    w = w.with_columns(((pl.col("t_mid") - pl.col("win_start")).dt.total_seconds().clip(0, None)
                        / pl.col("window_s")).clip(0, 0.9999).alias("frac"))
    w = w.with_columns((pl.col("frac") * 4).floor().cast(pl.Int8).alias("slot"),
                       (pl.col("h_before") + pl.col("frac") * pl.col("window_s") / 3600).alias("hcum"),
                       (pl.col("n_chat") + pl.col("n_intent")).alias("n_stmt"))
    if not include_goals:
        assert not any(holdout_mask(w["pt_date"].to_list(), w["goal_no"].to_list()))

    # resets per agent (cumulative within goal period), joined as-of at the window midpoint
    t = pl.read_parquet(OUT / "context_ledger_turns.parquet",
                        columns=["agent", "pt_date", "goal_no", "holdout", "t_call", "turn_id", "reset_consol",
                                 "reset_session", "reset_forced"])
    t = t.filter(pl.col("pt_date").is_in(days["pt_date"].to_list()))
    rs = t.filter(pl.col("reset_consol") | pl.col("reset_session") | pl.col("reset_forced")).sort("agent", "t_call",
                                                                                                  "turn_id")
    rs = rs.with_columns(pl.int_range(1, pl.len() + 1).over("agent", "goal_no").alias("r_cum"))
    w = w.sort("t_mid").join_asof(rs.select("agent", "goal_no", "t_call", "r_cum").sort("t_call"),
                                  left_on="t_mid", right_on="t_call", by=["agent", "goal_no"], strategy="backward")
    w = w.with_columns(pl.col("r_cum").fill_null(0))
    w = w.select("gid", "agent", "pt_date", "goal_no", "regime", "unit_id", "day_idx", "win30", "t_mid", "slot",
                 "hcum", "r_cum", "n_stmt").sort("goal_no", "agent", "t_mid")
    w.write_parquet(DATA / "windows.parquet")

    # own call gaps >= 60 min inside a day
    cw = pl.read_parquet(OUT / "call_windows.parquet", columns=["agent", "pt_date", "holdout", "t_call", "turn_id"])
    cw = cw.filter(pl.col("pt_date").is_in(days["pt_date"].to_list())).sort("agent", "t_call",
                                                                                                  "turn_id")
    cw = cw.with_columns(pl.col("t_call").shift(1).over("agent", "pt_date").alias("t_prev"))
    gaps = cw.filter((pl.col("t_call") - pl.col("t_prev")).dt.total_seconds() >= GAP_MIN * 60) \
             .select("agent", "pt_date", pl.col("t_prev").alias("g_start"), pl.col("t_call").alias("g_end"))
    gaps.write_parquet(DATA / "gaps.parquet")

    # O1 periods
    goals = pl.read_parquet(OUT / "embeddings/goals.parquet").with_columns(pl.col("kind").cast(pl.String))
    per = []
    for g in sorted(days["goal_no"].unique().to_list()):
        if g in O1_EXCLUDE:
            continue
        k = goals.filter((pl.col("goal_no") == g) & (pl.col("kind") == "kickoff"))
        dd = days.filter(pl.col("goal_no") == g).sort("pt_date")
        if k.height == 0 or dd.height < 3:
            continue
        first = dd["pt_date"][0]
        if first != cal.filter(pl.col("goal_no") == g)["pt_date"].min():
            continue  # the kickoff day itself must be non-holdout
        fit = dd.head(FIT_DAYS)
        if fit["regime"].n_unique() > 1:
            continue
        t0 = k["win_start"][0]
        inc = w.filter((pl.col("pt_date") == first) & (pl.col("t_mid") >= t0) & (pl.col("goal_no") == g))["agent"]
        per.append({"goal_no": g, "regime": fit["regime"][0], "t0": t0, "fit_days": fit["pt_date"].to_list(),
                    "incumbents": sorted(inc.unique().to_list()), "n_days": dd.height})
    per = pl.DataFrame(per)
    per.write_parquet(DATA / "periods.parquet")

    prov = {"built_by": "hypotheses/H103-nights-demagnetize/scheme/build.py", "git_commit": git_commit(),
            "inputs": [{"source": "ai-village", "revision": REVISION,
                        "tables": ["calendar", "period_units", "embeddings/agent_win30", "embeddings/agent_day",
                                   "agent_{win30,day}_{style_resid,white32}_{bge_small,gte_modernbert}",
                                   "embeddings/goals", "goal_vectors", "context_ledger_turns", "call_windows"]}],
            "params": {"exclude_agents": sorted(EXCLUDE_AGENTS), "exclude_goals": sorted(EXCLUDE_GOALS),
                       "o1_exclude": sorted(O1_EXCLUDE), "min_stmt_window": MIN_STMT, "fit_days": FIT_DAYS,
                       "gap_min": GAP_MIN},
            "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    (DATA / "_provenance.json").write_text(json.dumps(prov, indent=1, default=str))
    print(f"windows {w.height}, days {days.height}, gaps {gaps.height}, O1 periods {per.height}")
    print(per.select("goal_no", "regime", "n_days", pl.col("incumbents").list.len().alias("n_inc")))


if __name__ == "__main__":
    main()
