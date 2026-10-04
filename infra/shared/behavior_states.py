"""Shared rule-based behavior states (action classes) per agent record and per agent-minute. Moved here from H14
(hypotheses/H14-behavior-entropy-production/scheme/build_states.py, also used by H17 and H39). Not to be confused
with the Jev LLM behavior labels (infra/behavior_states/, behavior_states_draft_*.parquet).

Scaffold artifacts removed (H14 rules, unchanged):
  mirror turns   a computer-use turn `pause` / `send_message_back_to_chat` / `search_history` / `move_to_room` is
                 dropped when the same agent logged the mirrored event (PAUSE / AGENT_TALK / SEARCH_HISTORY /
                 ENTER_ROOM) within 2 s (nearest as-of join);
  forced mouse   the first computer-use turn after a context boundary (CONSOLIDATE / START_USING_COMPUTER event) or of
                 the day, if it is a `mouse_move` (the scaffold forces one after ~85% of consolidations);
  gap logging    WAIT and CONSOLIDATE are logged at their end: minutes from the agent's previous record + 1 up to the
                 event's minute are idle (WAIT) or consolidate (CONSOLIDATE); a declared PAUSE is idle forward until
                 min(t + seconds, next record).
Schemes:
  fine (act, 11)    shell click scroll look type chat idle consolidate search session other
  coarse (6)        browse type shell chat idle consolidate   (-1 = removed from coarse sequences: class `other`)
  lumped (lump4, 4) work (browse/type/shell) chat idle consolidate
Minute state (coarse_min): chat if any chat record, else consolidate if any, else the majority work class
(shell >= type >= browse on ties), else consolidate inside a logged consolidation gap, else idle.

Outputs (data/processed/shared/), ALL days; `holdout` flags locked-holdout days (exploration must filter it):
  states_turn.parquet  agent, t, pt_date, goal_no, regime, kind (raw action / action type), src (turn / event),
                       act (fine code), coarse (coarse code, -1 removed), pause_s   [= H14's columns]
                       + lump4 (lumped code, -1 removed), holdout
  states_min.parquet   pt_date, minute, agent, coarse_min, n_rec, present (>= 10 records that day)   [= H14's columns]
                       + lump4_min, in_span (minute between the agent's first and last record minute of the day;
                       outside it "idle" is really absent, see infra/README Known issues), goal_no, regime, holdout
Grid: every minute of each day's calendar window x every roster agent on that day (Claude Code agent excluded), as in
activity_bins.

Usage: uv run python infra/shared/behavior_states.py            (build the shared tables)
       uv run python infra/shared/behavior_states.py --verify   (compare with H14's tables on non-holdout days)
Library: build(days, audit) returns exactly H14's (states_turn, states_min) for those days (in memory).
"""
from __future__ import annotations

import os

for _v, _n in (("POLARS_MAX_THREADS", "2"), ("OMP_NUM_THREADS", "2"), ("OPENBLAS_NUM_THREADS", "2"),
               ("MKL_NUM_THREADS", "2"), ("VECLIB_MAXIMUM_THREADS", "2")):
    os.environ.setdefault(_v, _n)

import json  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from pathlib import Path  # noqa: E402

import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import OUT, ROOT, holdout_mask, write_provenance  # noqa: E402

SH = OUT

# ----------------------------------------------------------------------------- class maps (H14, unchanged)
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
MIRROR_WINDOW_US = 2_000_000
PRESENT_MIN_RECORDS = 10
COARSE_TO_LUMP4_CODE = {COARSE.index(c): LUMP4.index(l) for c, l in COARSE_TO_LUMP4.items()}


def nonholdout_days() -> list[str]:
    cal = pl.read_parquet(SH / "calendar.parquet")
    m = holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    assert list(m) == cal["holdout"].to_list(), "calendar.holdout disagrees with holdout.json"
    return cal.filter(~pl.col("holdout"))["pt_date"].to_list()


def all_days() -> list[str]:
    return pl.read_parquet(SH / "calendar.parquet", columns=["pt_date"])["pt_date"].to_list()


def _pt_date(col="t"):
    return pl.col(col).dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.Utf8).alias("pt_date")


def build(days: list[str], audit: dict | None = None):
    """Build (states_turn, states_min) DataFrames for the given PT days (in memory). Identical to H14's build()."""
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
            mirrored = (pl.col("te").is_not_null() & ((pl.col("te") - pl.col("t")).dt.total_microseconds().abs() <= MIRROR_WINDOW_US))
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
    present = s.group_by("pt_date", "agent").len().filter(pl.col("len") >= PRESENT_MIN_RECORDS).select("pt_date", "agent", pl.lit(True).alias("present"))
    states_min = (g.join(present, on=["pt_date", "agent"], how="left")
                  .with_columns(pl.col("present").fill_null(False))
                  .select("pt_date", pl.col("minute").cast(pl.Int16), pl.col("agent").cast(pl.Int8), "coarse_min", "n_rec", "present")
                  .sort("pt_date", "agent", "minute"))
    audit["minute_mix"] = {COARSE[k]: int(v) for k, v in states_min.filter(pl.col("present")).group_by("coarse_min").len().sort("coarse_min").iter_rows()}
    return states_turn, states_min


def extend(states_turn: pl.DataFrame, states_min: pl.DataFrame):
    """Add lump4, holdout, goal/regime and the in-span flag (shared-table columns; H14's columns unchanged)."""
    cal = pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "goal_no", "regime", "holdout"]) \
            .with_columns(pl.col("regime").cast(pl.Utf8), pl.col("goal_no").cast(pl.Int8))
    lump = lambda c: pl.col(c).replace_strict(COARSE_TO_LUMP4_CODE, default=-1, return_dtype=pl.Int8)  # noqa: E731
    st = states_turn.with_columns(lump("coarse").alias("lump4")).join(cal.select("pt_date", "holdout"), on="pt_date", how="left")
    span = (st.with_columns(pl.col("t")).join(pl.read_parquet(SH / "calendar.parquet", columns=["pt_date", "win_start"]), on="pt_date")
            .with_columns(((pl.col("t") - pl.col("win_start")).dt.total_seconds() // 60).cast(pl.Int16).alias("minute"))
            .group_by("pt_date", "agent").agg(pl.col("minute").min().alias("m_first"), pl.col("minute").max().alias("m_last")))
    sm = (states_min.with_columns(lump("coarse_min").alias("lump4_min"))
          .join(span, on=["pt_date", "agent"], how="left")
          .with_columns(((pl.col("minute") >= pl.col("m_first")) & (pl.col("minute") <= pl.col("m_last"))).fill_null(False).alias("in_span"))
          .drop("m_first", "m_last")
          .join(cal, on="pt_date", how="left")
          .sort("pt_date", "agent", "minute"))
    return st, sm


def main():
    t0 = time.time()
    audit = {}
    days = all_days()
    st, sm = build(days, audit)
    st, sm = extend(st, sm)
    st.write_parquet(SH / "states_turn.parquet", compression="zstd")
    sm.write_parquet(SH / "states_min.parquet", compression="zstd")
    audit["rows"] = {"states_turn": st.height, "states_min": sm.height,
                     "states_turn_nonholdout": st.filter(~pl.col("holdout")).height,
                     "states_min_nonholdout": sm.filter(~pl.col("holdout")).height}
    print(json.dumps({k: audit[k] for k in ("records_in", "mirror_dropped", "forced_mouse_move_dropped", "rows")}, indent=1))
    write_provenance("behavior_states", ["actions", "events_core", "calendar", "roster"],
                     {"days": "all calendar days; holdout flagged", "mirror_window_s": MIRROR_WINDOW_US / 1e6,
                      "forced_mouse_move": "first computer-use turn after CONSOLIDATE/START_USING_COMPUTER or of the day",
                      "present_min_records": PRESENT_MIN_RECORDS,
                      "classes": {"act": ACT_CLASSES, "coarse": COARSE, "lump4": LUMP4},
                      "source": "hypotheses/H14-behavior-entropy-production/scheme/build_states.py (logic unchanged)",
                      "audit": audit})
    print(f"done in {time.time() - t0:.1f}s")


def verify():
    """Shared tables restricted to non-holdout days vs H14's tables (exact)."""
    h14 = ROOT / "data/processed/H14-behavior-entropy-production"
    res = {}
    for name, keys in (("states_turn", ["agent", "t", "src", "kind"]), ("states_min", ["pt_date", "agent", "minute"])):
        a = pl.read_parquet(h14 / f"{name}.parquet")
        b = pl.read_parquet(SH / f"{name}.parquet").filter(~pl.col("holdout")).select(a.columns)
        a = a.with_columns([pl.col(c).cast(pl.String) for c, t in a.schema.items() if t == pl.Categorical]).sort(a.columns)
        b = b.with_columns([pl.col(c).cast(pl.String) for c, t in b.schema.items() if t == pl.Categorical]).sort(a.columns)
        res[name] = {"h14_rows": a.height, "shared_rows": b.height, "equal": a.equals(b)}
        if not res[name]["equal"]:
            res[name]["anti_h14_not_shared"] = a.join(b, on=a.columns, how="anti", nulls_equal=True).height
            res[name]["anti_shared_not_h14"] = b.join(a, on=a.columns, how="anti", nulls_equal=True).height
    print(res)
    return res


if __name__ == "__main__":
    if "--verify" in sys.argv:
        verify()
    else:
        main()
