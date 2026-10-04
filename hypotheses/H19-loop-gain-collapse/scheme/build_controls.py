"""H19 scheme, part 1: per-goal-period control parameters (non-holdout days only).

Output: data/processed/H19-loop-gain-collapse/controls.parquet (one row per non-holdout goal period) and
        controls_days.parquet (per day, for the confirmatory script's reuse of the same definitions).

Definitions (fixed 2026-10-03 before any control parameter was related to any loop gain; see the card):
  N_roster      mean daily count of roster agents (Claude Code agent excluded) on the period's non-holdout days
  N_active      mean daily count of roster agents with >= 1 turn that day
  turn (LLM step)    an agent's computer-use turn (`actions` row) or agent event in `events_core` other than
                     START/STOP_USING_COMPUTER, merged when within 1 s of the same agent's previous one
  turn (village)     an agent event in `events_core` other than START/STOP_USING_COMPUTER, merged within 1 s
                     (the shared `exposure` table's notion of "next turn")
  m_turn_*      agent chat messages (Claude Code excluded) per agent turn
  m_hour        agent chat messages per on-roster agent-hour (sum over days of N_roster_d x window_h_d)
  k_*           messages written by other agents delivered to a roster agent (room rule, `exposure`) per turn:
                the attention load, i.e. mean number of new agent messages waiting at a turn
  N_room        mean over agent messages of (recipients + 1): the room size a message actually reaches
  n_rooms       rooms that carried >= 5% of the period's agent messages
  human_share   human messages / all chat messages; auto_share likewise for the `automated` speaker
  hours_doc     median documented hours/day (null before 2025-05-23); hours_emp median empirical window (h)
  x_att_*       (N_room - 1) / (1 + k_*): attended partners per unit attention (H18 1/k dilution, card Model)
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import h19common as C  # noqa: E402
import polars as pl  # noqa: E402

MERGE_S = 1.0


def turns_per_agent_day(cal: pl.DataFrame, roster: pl.DataFrame) -> pl.DataFrame:
    days = cal["pt_date"].to_list()
    agents = roster.filter(~pl.col("claude_code"))["agent"].to_list()
    ev = (pl.scan_parquet(C.SHARED / "events_core.parquet")
          .filter((pl.col("actor_kind") == "agent") & pl.col("agent").is_in(agents) & pl.col("pt_date").is_in(days)
                  & ~pl.col("action_type").cast(pl.Utf8).is_in(["START_USING_COMPUTER", "STOP_USING_COMPUTER"]))
          .select("t", "agent", "pt_date").collect())
    ac = (pl.scan_parquet(C.SHARED / "actions.parquet").filter(pl.col("agent").is_in(agents)).select("t", "agent")
          .with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.Utf8).alias("pt_date"))
          .filter(pl.col("pt_date").is_in(days)).collect())

    def merged(df: pl.DataFrame, name: str) -> pl.DataFrame:
        df = df.sort("agent", "t")
        gap = (pl.col("t") - pl.col("t").shift(1).over("agent")).dt.total_microseconds() / 1e6
        df = df.with_columns(gap.alias("gap"))
        df = df.filter(pl.col("gap").is_null() | (pl.col("gap") > MERGE_S))
        return df.group_by("pt_date", "agent").agg(pl.len().alias(name))

    t_llm = merged(pl.concat([ev, ac.select("t", "agent", "pt_date")]), "turns_llm")
    t_vil = merged(ev, "turns_village")
    return t_llm.join(t_vil, on=["pt_date", "agent"], how="full", coalesce=True).fill_null(0)


def build(cal: pl.DataFrame | None = None, allow_holdout: bool = False, write_days: bool = True) -> pl.DataFrame:
    """Controls for the goal periods in `cal` (default: every non-holdout day). Only analysis/confirm.py passes
    held-out days, and only behind its confirmation flags (allow_holdout=True)."""
    if cal is None:
        cal = C.calendar_nonholdout()
    if not allow_holdout:
        C.assert_no_holdout(cal["pt_date"], cal["goal_no"])
    roster = pl.read_parquet(C.SHARED / "roster.parquet")
    meta = C.goal_period_meta()
    days = cal["pt_date"].to_list()

    # roster per day
    ros = roster.filter(~pl.col("claude_code")).select("agent", "joined", "left")
    rd = (cal.select("pt_date").join(ros, how="cross")
          .filter((pl.col("pt_date") >= pl.col("joined")) & (pl.col("left").is_null() | (pl.col("pt_date") < pl.col("left"))))
          .group_by("pt_date").agg(pl.len().alias("N_roster_d")))
    tpd = turns_per_agent_day(cal, roster)
    act = tpd.filter(pl.col("turns_llm") > 0).group_by("pt_date").agg(pl.len().alias("N_active_d"))
    td = tpd.group_by("pt_date").agg(pl.col("turns_llm").sum(), pl.col("turns_village").sum())

    # chat
    cc_agent = roster.filter(pl.col("claude_code"))["agent"].to_list()
    chat = pl.read_parquet(C.SHARED / "chat_core.parquet", columns=["t", "pt_date", "room", "speaker_kind", "agent"]).with_row_index("msg")
    chat = chat.with_columns(pl.col("speaker_kind").cast(pl.Utf8))
    cd = (chat.filter(pl.col("pt_date").is_in(days))
          .with_columns(((pl.col("speaker_kind") == "agent") & ~pl.col("agent").is_in(cc_agent)).alias("is_agent"),
                        ((pl.col("speaker_kind") == "agent") & pl.col("agent").is_in(cc_agent)).alias("is_cc")))
    cday = cd.group_by("pt_date").agg(pl.col("is_agent").sum().alias("msgs_agent"), pl.col("is_cc").sum().alias("msgs_cc"),
                                      (pl.col("speaker_kind") == "human").sum().alias("msgs_human"),
                                      (pl.col("speaker_kind") == "automated").sum().alias("msgs_auto"),
                                      pl.len().alias("msgs_all"))
    # exposure: deliveries of agent-written messages (incl. the Claude Code agent's) to roster agents
    exp = pl.read_parquet(C.SHARED / "exposure.parquet").select("msg", "agent")
    ex = exp.join(cd.select(pl.col("msg").cast(pl.UInt32), "pt_date", "speaker_kind"), on="msg", how="inner")
    eday = ex.group_by("pt_date").agg((pl.col("speaker_kind") == "agent").sum().alias("deliv_agent"),
                                      pl.len().alias("deliv_all"))
    # recipients per agent message -> N_room
    rec = exp.group_by("msg").agg(pl.len().alias("n_rec"))
    am = (cd.filter(pl.col("speaker_kind") == "agent").select(pl.col("msg").cast(pl.UInt32), "pt_date", "room")
          .join(rec, on="msg", how="left").with_columns(pl.col("n_rec").fill_null(0)))

    day = (cal.select("pt_date", "goal_no", pl.col("regime").cast(pl.Utf8), "window_s", "documented_hours")
           .join(rd, on="pt_date", how="left").join(act, on="pt_date", how="left").join(td, on="pt_date", how="left")
           .join(cday, on="pt_date", how="left").join(eday, on="pt_date", how="left")
           .fill_null(strategy="zero")
           .with_columns((pl.col("N_roster_d") * pl.col("window_s") / 3600.0).alias("agent_hours")))
    if write_days:
        day.write_parquet(C.OUT / "controls_days.parquet", compression="zstd")

    rows = []
    for (g,), d in day.group_by(["goal_no"], maintain_order=True):
        g = int(g)
        regs = d["regime"].value_counts().sort("count", descending=True)
        a = am.filter(pl.col("pt_date").is_in(d["pt_date"].to_list()))
        room_share = a.group_by("room").len().with_columns((pl.col("len") / pl.col("len").sum()).alias("s"))
        dates = [C.dt.date.fromisoformat(x) for x in d["pt_date"].to_list()]
        mid = (min(dates) - C.DAY0).days + ((max(dates) - min(dates)).days) / 2
        s = d.select(pl.all().exclude("pt_date", "goal_no", "regime", "documented_hours", "window_s").sum()).row(0, named=True)
        r = {"goal_no": g, "period": C.pname(g), "n_days": d.height, "first_day": min(d["pt_date"]), "last_day": max(d["pt_date"]),
             "date_mid": float(mid), "regime": regs["regime"][0], "regime_mixed": regs.height > 1,
             "hours_doc": float(d["documented_hours"].filter(d["documented_hours"] > 0).median()) if (d["documented_hours"] > 0).any() else None,
             "hours_emp": float((d["window_s"] / 3600).median()),
             "N_roster": float(d["N_roster_d"].mean()), "N_active": float(d["N_active_d"].mean()),
             "N_room": float((a["n_rec"] + 1).mean()) if a.height else None,
             "n_rooms": int((room_share["s"] >= 0.05).sum()) if a.height else 0}
        r.update({k: s[k] for k in ("turns_llm", "turns_village", "msgs_agent", "msgs_cc", "msgs_human", "msgs_auto",
                                    "msgs_all", "deliv_agent", "deliv_all", "agent_hours")})
        rows.append(r)
    df = pl.DataFrame(rows).join(meta.select("goal_no", "mode", "by"), on="goal_no", how="left")
    df = df.with_columns(
        (pl.col("msgs_agent") / pl.col("turns_llm")).alias("m_turn_llm"),
        (pl.col("msgs_agent") / pl.col("turns_village")).alias("m_turn_village"),
        (pl.col("msgs_agent") / pl.col("agent_hours")).alias("m_hour"),
        (pl.col("deliv_agent") / pl.col("turns_llm")).alias("k_llm"),
        (pl.col("deliv_agent") / pl.col("turns_village")).alias("k_village"),
        (pl.col("deliv_agent") / pl.col("agent_hours")).alias("k_hour"),
        (pl.col("turns_llm") / pl.col("agent_hours")).alias("turns_llm_per_hour"),
        (pl.col("turns_village") / pl.col("agent_hours")).alias("turns_village_per_hour"),
        (pl.col("msgs_human") / pl.col("msgs_all")).alias("human_share"),
        (pl.col("msgs_auto") / pl.col("msgs_all")).alias("auto_share"),
    ).with_columns(
        ((pl.col("N_room") - 1) / (1 + pl.col("k_llm"))).alias("x_att_llm"),
        ((pl.col("N_room") - 1) / (1 + pl.col("k_village"))).alias("x_att_village"),
    ).sort("goal_no")
    if not allow_holdout:
        C.assert_no_holdout(day["pt_date"], day["goal_no"])
    return df


def main():
    C.OUT.mkdir(parents=True, exist_ok=True)
    df = build()
    df.write_parquet(C.OUT / "controls.parquet", compression="zstd")
    C.write_provenance("controls.parquet", "hypotheses/H19-loop-gain-collapse/scheme/build_controls.py",
                       [{"source": "ai-village", "revision": C.REVISION,
                         "tables": ["calendar", "roster", "events_core", "actions", "chat_core", "exposure"]},
                        {"source": "hypotheses/hypohypotheses/goal-periods.md", "tables": ["At a glance (mode, by)"]}],
                       {"merge_s": MERGE_S, "holdout": "excluded (calendar.holdout and infra holdout_mask)",
                        "claude_code_agent": "excluded from turns, N and msgs_agent; its messages count as deliveries"})
    with pl.Config(tbl_rows=60, tbl_cols=30, tbl_width_chars=250):
        print(df.select("period", "n_days", "regime", "mode", "N_roster", "N_active", "N_room", "n_rooms", "hours_emp",
                        "m_turn_llm", "m_turn_village", "m_hour", "k_llm", "k_village", "human_share", "x_att_llm", "x_att_village"))


if __name__ == "__main__":
    main()
