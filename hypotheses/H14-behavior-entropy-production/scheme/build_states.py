"""H14 scheme: categorical behavior-state tables from the shared Phase 0 tables (non-holdout days only).

Outputs (data/processed/H14-behavior-entropy-production/):
  states_turn.parquet  one row per agent record (computer-use turn or agent event), scaffold artifacts removed:
                       agent, t, pt_date, goal_no, regime, kind (raw action / action type), act (fine class code),
                       coarse (coarse state code, -1 = removed from coarse sequences)
  states_min.parquet   agent x minute of each day's window (same grid as activity_bins): pt_date, minute, agent,
                       coarse_min (coarse state code), n_rec (records in the minute), present (agent has >= 10
                       records that day)
  scheme_audit.json    counts for every removal rule and the class mix by regime
  _provenance.json

Holdout days are never read: rows are restricted to calendar.holdout == False before any processing. The
confirmatory script calls build(days=...) in memory for its own (holdout) days.

Usage: uv run python hypotheses/H14-behavior-entropy-production/scheme/build_states.py
"""
from __future__ import annotations

import os

os.environ.setdefault("POLARS_MAX_THREADS", "2")

import datetime as dt
import json
import sys
import time
from pathlib import Path

import polars as pl

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "infra/shared"))
from common import REVISION, git_commit, holdout_mask  # noqa: E402

SH = ROOT / "data/processed/shared"
OUT = ROOT / "data/processed/H14-behavior-entropy-production"

# ----------------------------------------------------------------------------- class maps
ACT_CLASSES = ["shell", "click", "scroll", "look", "type", "chat", "idle", "consolidate", "search", "session", "other"]
COARSE = ["browse", "type", "shell", "chat", "idle", "consolidate"]
LUMP4 = ["work", "chat", "idle", "consolidate"]

TURN_TO_ACT = {
    "bash": "shell",
    "left_click": "click", "double_click": "click", "triple_click": "click", "right_click": "click",
    "middle_click": "click", "left_click_drag": "click", "left_mouse_down": "click", "left_mouse_up": "click",
    "mouse_move": "click", "cursor_position": "click",
    "scroll": "scroll",
    "screenshot": "look", "get_pixel_coords_of_element": "look", "view_clipboard": "look", "wait": "look",
    "type": "type", "key": "type", "hold_key": "type",
    # mirrors (kept only when no matching event exists)
    "send_message_back_to_chat": "chat", "pause": "idle", "search_history": "search",
}
EVENT_TO_ACT = {
    "AGENT_TALK": "chat", "PAUSE": "idle", "WAIT": "idle", "CONSOLIDATE": "consolidate",
    "SEARCH_HISTORY": "search", "START_USING_COMPUTER": "session", "STOP_USING_COMPUTER": "session",
}
ACT_TO_COARSE = {"shell": "shell", "click": "browse", "scroll": "browse", "look": "browse", "type": "type",
                 "chat": "chat", "idle": "idle", "consolidate": "consolidate", "search": "consolidate",
                 "session": "consolidate", "other": None}
COARSE_TO_LUMP4 = {"browse": "work", "type": "work", "shell": "work", "chat": "chat", "idle": "idle",
                   "consolidate": "consolidate"}
MIRRORS = {"pause": "PAUSE", "send_message_back_to_chat": "AGENT_TALK", "search_history": "SEARCH_HISTORY",
           "move_to_room": "ENTER_ROOM"}
BOUNDARY_EVENTS = ("CONSOLIDATE", "START_USING_COMPUTER")


def nonholdout_days() -> list[str]:
    cal = pl.read_parquet(SH / "calendar.parquet")
    m = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    assert list(m) == cal["holdout"].to_list(), "calendar.holdout disagrees with holdout.json"
    return cal.filter(~pl.col("holdout"))["pt_date"].to_list()


def _pt_date(col="t"):
    return pl.col(col).dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.Utf8).alias("pt_date")


def build(days: list[str], audit: dict | None = None):
    """Build (states_turn, states_min) DataFrames for the given PT days (in memory)."""
    audit = {} if audit is None else audit
    days_set = set(days)
    cal = pl.read_parquet(SH / "calendar.parquet").filter(pl.col("pt_date").is_in(days_set))
    roster = pl.read_parquet(SH / "roster.parquet")

    acts = (pl.read_parquet(SH / "actions.parquet", columns=["t", "agent", "action"])
            .filter(pl.col("agent").is_not_null())
            .with_columns(_pt_date(), pl.col("action").cast(pl.Utf8).alias("kind"))
            .filter(pl.col("pt_date").is_in(days_set))
            .select("t", "agent", "pt_date", "kind")
            .with_columns(pl.lit("turn").alias("src"), pl.lit(None, dtype=pl.Float32).alias("pause_s")))
    ev = (pl.read_parquet(SH / "events_core.parquet",
                          columns=["t", "pt_date", "actor_kind", "agent", "action_type", "pause_s"])
          .filter((pl.col("actor_kind") == "agent") & pl.col("agent").is_not_null() & pl.col("pt_date").is_in(days_set))
          .with_columns(pl.col("action_type").cast(pl.Utf8).alias("kind"))
          .select("t", "agent", "pt_date", "kind", pl.lit("event").alias("src"), "pause_s"))
    audit["records_in"] = {"turns": acts.height, "events": ev.height}

    # --- mirrors: drop a mirror turn if the same agent logged the mirrored event within 2 s
    keep = [acts.filter(~pl.col("kind").is_in(list(MIRRORS)))]
    audit["mirror_dropped"] = {}
    for turn_kind, ev_kind in MIRRORS.items():
        A = acts.filter(pl.col("kind") == turn_kind).sort("agent", "t")
        E = ev.filter(pl.col("kind") == ev_kind).select("agent", pl.col("t").alias("te")).sort("agent", "te")
        if A.height == 0:
            continue
        if E.height:
            j = A.join_asof(E, left_on="t", right_on="te", by="agent", strategy="nearest", check_sortedness=False)
            mirrored = (pl.col("te").is_not_null() & ((pl.col("te") - pl.col("t")).dt.total_microseconds().abs() <= 2_000_000))
            audit["mirror_dropped"][turn_kind] = int(j.filter(mirrored).height)
            keep.append(j.filter(~mirrored).drop("te"))
        else:
            audit["mirror_dropped"][turn_kind] = 0
            keep.append(A)
    rec = pl.concat([pl.concat(keep, how="vertical_relaxed"), ev], how="vertical_relaxed").sort("agent", "t")

    # --- scaffold-forced mouse_move: the first computer-use turn after a context boundary (or of the day)
    rec = rec.with_columns(
        (pl.col("kind").is_in(BOUNDARY_EVENTS) & (pl.col("src") == "event")).cast(pl.Int32).alias("_b"))
    rec = rec.with_columns(pl.col("_b").cum_sum().over(["agent", "pt_date"]).alias("_seg"))
    rec = rec.with_columns(((pl.col("src") == "turn").cast(pl.Int32).cum_sum().over(["agent", "pt_date", "_seg"])).alias("_turn_rank"))
    forced = (pl.col("src") == "turn") & (pl.col("kind") == "mouse_move") & (pl.col("_turn_rank") == 1)
    audit["forced_mouse_move_dropped"] = {
        "after_boundary": int(rec.filter(forced & (pl.col("_seg") > 0)).height),
        "first_turn_of_day": int(rec.filter(forced & (pl.col("_seg") == 0)).height),
        "mouse_move_kept": int(rec.filter((pl.col("kind") == "mouse_move") & ~forced).height)}
    rec = rec.filter(~forced).drop("_b", "_seg", "_turn_rank")

    # --- classes
    rec = rec.with_columns(
        pl.when(pl.col("src") == "turn").then(pl.col("kind").replace_strict(TURN_TO_ACT, default="other"))
        .otherwise(pl.col("kind").replace_strict(EVENT_TO_ACT, default="other")).alias("act_s"))
    rec = rec.with_columns(pl.col("act_s").replace_strict(ACT_TO_COARSE, default=None).alias("coarse_s"))
    rec = rec.join(cal.select("pt_date", "goal_no", "regime"), on="pt_date", how="inner")
    act_code = {c: i for i, c in enumerate(ACT_CLASSES)}
    co_code = {c: i for i, c in enumerate(COARSE)}
    states_turn = rec.select(
        pl.col("agent").cast(pl.Int8), "t", "pt_date", pl.col("goal_no").cast(pl.Int8), pl.col("regime").cast(pl.Utf8),
        pl.col("kind").cast(pl.Categorical), pl.col("src").cast(pl.Categorical),
        pl.col("act_s").replace_strict(act_code, return_dtype=pl.Int8).alias("act"),
        pl.col("coarse_s").replace_strict(co_code, default=-1, return_dtype=pl.Int8).alias("coarse"),
        pl.col("pause_s"))
    audit["act_mix_by_regime"] = {
        r: {ACT_CLASSES[k]: int(v) for k, v in g.group_by("act").len().sort("act").iter_rows()}
        for (r,), g in states_turn.group_by("regime")}

    # --- minute grid
    win = cal.select("pt_date", "win_start", "window_s")
    s = states_turn.join(win, on="pt_date").with_columns(
        ((pl.col("t") - pl.col("win_start")).dt.total_seconds() // 60).cast(pl.Int32).alias("minute"))
    s = s.sort("agent", "t").with_columns(
        pl.col("minute").shift(1).over(["agent", "pt_date"]).alias("m_prev"),
        pl.col("t").shift(-1).over(["agent", "pt_date"]).alias("t_next"))
    per_min = s.group_by("pt_date", "agent", "minute").agg(
        pl.len().cast(pl.Int16).alias("n_rec"),
        (pl.col("coarse") == co_code["chat"]).any().alias("chat"),
        (pl.col("coarse") == co_code["consolidate"]).any().alias("cons"),
        (pl.col("coarse") == co_code["shell"]).sum().alias("n_shell"),
        (pl.col("coarse") == co_code["type"]).sum().alias("n_type"),
        (pl.col("coarse") == co_code["browse"]).sum().alias("n_browse"),
        (pl.col("coarse") == co_code["idle"]).any().alias("idle_rec"))
    # gap intervals logged at their end: WAIT (idle) and CONSOLIDATE (consolidate); declared PAUSE forward
    gaps_end = (s.filter(pl.col("kind").cast(pl.Utf8).is_in(["WAIT", "CONSOLIDATE"]) & (pl.col("src") == "event") & pl.col("m_prev").is_not_null())
                .select("pt_date", "agent", (pl.col("m_prev") + 1).alias("m0"), pl.col("minute").alias("m1"),
                        pl.when(pl.col("kind").cast(pl.Utf8) == "CONSOLIDATE").then(pl.lit(2)).otherwise(pl.lit(1)).alias("gap")))
    pz = (s.filter((pl.col("kind").cast(pl.Utf8) == "PAUSE") & pl.col("pause_s").is_not_null())
          .with_columns(pl.min_horizontal(pl.col("t") + pl.duration(seconds=pl.col("pause_s")),
                                          pl.col("t_next").fill_null(pl.col("t") + pl.duration(seconds=pl.col("pause_s")))).alias("t_end"))
          .select("pt_date", "agent", "minute", ((pl.col("t_end") - pl.col("win_start")).dt.total_seconds() // 60).cast(pl.Int32).alias("m1"))
          .select("pt_date", "agent", pl.col("minute").alias("m0"), "m1", pl.lit(1).alias("gap")))
    gaps = pl.concat([gaps_end, pz], how="vertical_relaxed").filter(pl.col("m1") >= pl.col("m0"))
    gaps = (gaps.with_columns(pl.int_ranges(pl.col("m0"), pl.col("m1") + 1).alias("minute")).explode("minute")
            .group_by("pt_date", "agent", "minute").agg(pl.col("gap").max()))
    grid = (cal.select("pt_date", "window_s").with_columns(pl.int_ranges(0, (pl.col("window_s") // 60 + 1).cast(pl.Int32)).alias("minute"))
            .explode("minute").select("pt_date", pl.col("minute").cast(pl.Int32)))
    ros = roster.filter(~pl.col("claude_code")).select(pl.col("agent").cast(pl.Int8), "joined", "left")
    grid = grid.join(ros, how="cross").filter(
        (pl.col("pt_date") >= pl.col("joined")) & (pl.col("left").is_null() | (pl.col("pt_date") < pl.col("left")))).drop("joined", "left")
    g = (grid.join(per_min, on=["pt_date", "agent", "minute"], how="left")
         .join(gaps.with_columns(pl.col("minute").cast(pl.Int32)), on=["pt_date", "agent", "minute"], how="left")
         .with_columns(pl.col("n_rec").fill_null(0)))
    work_major = (pl.when((pl.col("n_shell") >= pl.col("n_type")) & (pl.col("n_shell") >= pl.col("n_browse")) & (pl.col("n_shell") > 0)).then(co_code["shell"])
                  .when((pl.col("n_type") >= pl.col("n_browse")) & (pl.col("n_type") > 0)).then(co_code["type"])
                  .when(pl.col("n_browse") > 0).then(co_code["browse"]).otherwise(None))
    g = g.with_columns(
        pl.when(pl.col("chat").fill_null(False)).then(co_code["chat"])
        .when(pl.col("cons").fill_null(False)).then(co_code["consolidate"])
        .otherwise(work_major).alias("_w"))
    g = g.with_columns(
        pl.when(pl.col("_w").is_not_null()).then(pl.col("_w"))
        .when(pl.col("gap") == 2).then(co_code["consolidate"])
        .otherwise(co_code["idle"]).cast(pl.Int8).alias("coarse_min"))
    present = s.group_by("pt_date", "agent").len().filter(pl.col("len") >= 10).select("pt_date", "agent", pl.lit(True).alias("present"))
    states_min = (g.join(present, on=["pt_date", "agent"], how="left")
                  .with_columns(pl.col("present").fill_null(False))
                  .select("pt_date", pl.col("minute").cast(pl.Int16), pl.col("agent").cast(pl.Int8), "coarse_min", "n_rec", "present")
                  .sort("pt_date", "agent", "minute"))
    audit["minute_mix"] = {COARSE[k]: int(v) for k, v in states_min.filter(pl.col("present")).group_by("coarse_min").len().sort("coarse_min").iter_rows()}
    return states_turn, states_min


def main():
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    days = nonholdout_days()
    audit = {"days": len(days)}
    st, sm = build(days, audit)
    st.write_parquet(OUT / "states_turn.parquet", compression="zstd")
    sm.write_parquet(OUT / "states_min.parquet", compression="zstd")
    audit["rows"] = {"states_turn": st.height, "states_min": sm.height}
    audit["classes"] = {"act": ACT_CLASSES, "coarse": COARSE, "lump4": LUMP4}
    (OUT / "scheme_audit.json").write_text(json.dumps(audit, indent=1))
    prov_path = OUT / "_provenance.json"
    prov = json.loads(prov_path.read_text()) if prov_path.exists() else {}
    prov["states"] = {"built_by": "hypotheses/H14-behavior-entropy-production/scheme/build_states.py",
                      "git_commit": git_commit(),
                      "inputs": [{"source": "ai-village", "revision": REVISION,
                                  "tables": ["shared/actions", "shared/events_core", "shared/calendar", "shared/roster"]}],
                      "params": {"days": "calendar.holdout == False", "mirror_window_s": 2,
                                 "forced_mouse_move": "first computer-use turn after CONSOLIDATE/START_USING_COMPUTER or of the day",
                                 "classes": audit["classes"]},
                      "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    prov_path.write_text(json.dumps(prov, indent=1))
    print(json.dumps(audit, indent=1))
    print(f"done in {time.time() - t0:.1f}s")


if __name__ == "__main__":
    main()
