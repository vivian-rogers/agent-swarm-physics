"""H11 round 1b scheme (improved data, 2026-10-04): the same label files as round 1, rebuilt from the shared,
deterministic tables, plus work-ledger states and the DQ6 #26 ballots.

Writes data/processed/H11-potts-labor-vs-herding/r1b/G<NN>/ in round 1's layout, so analysis/h11data.load_period
reads it unchanged when H11_LABELS=shared (the round-1 path, data/processed/H11-.../G<NN>/, stays as it was):
  labels_project_w{15,30,60}.parquet  shared project_states (sources = all; deterministic tie-break; ranking on
                                      non-holdout rows), held-out days dropped, day re-indexed over non-holdout days
  labels_projectact_w30.parquet       shared project_states (sources = action)
  labels_action_w{15,30,60}.parquet   H11's action-class rule, with the shared deterministic tie-break
  labels_work_w{15,30,60}.parquet     NEW, agent state (categorical, project, work ledger): the repo with the most
                                      agent work commits by agent i in window w (DQ4 default filter: canonical &
                                      ~imported & author_kind == agent & ~automated; author time). Ties -> latest
                                      commit, then the repo's first commit, then the name. No commit = missing.
                                      Labels 1..q (q <= 8, share >= 2%), rest 0 = "other", as for attention.
  projects_w*.parquet, projects_work_w*.parquet, windows_w*.parquet
  G26/ballots.parquet                 DQ6 ballots: round (approval | runoff | confirmatory), voter, candidate, t
  G26/phases.parquet                  DQ6 phase and tally rows (codes and times only)
No text is read or stored.

Usage:  uv run python hypotheses/H11-potts-labor-vs-herding/scheme/build_r1b.py [--goals 30 31 ...]
Non-holdout goal periods only (2-44 minus the holdout, plus #51 outside its locked tail).
"""
from __future__ import annotations

import argparse
import datetime as dt
import json
import sys
from pathlib import Path

from h11common import C, OUT, SHARED, assert_not_holdout, nonholdout_goals  # noqa: F401  (sets thread env vars)
import polars as pl  # noqa: E402

sys.path.insert(0, str(C.ROOT / "infra/shared"))
import project_states as PS  # noqa: E402

R1B = OUT / "r1b"
WINDOWS = (15, 30, 60)
WORK_FILTER = (pl.col("canonical") & ~pl.col("imported") & (pl.col("author_kind").cast(pl.String) == "agent")
               & ~pl.col("automated") & pl.col("author_agent").is_not_null())

ACTION_CLASS = {
    "send_message_back_to_chat": 1,
    **{a: 2 for a in ["left_click", "scroll", "mouse_move", "screenshot", "get_pixel_coords_of_element",
                      "double_click", "triple_click", "right_click", "middle_click", "left_click_drag",
                      "left_mouse_down", "left_mouse_up", "cursor_position"]},
    **{a: 3 for a in ["type", "key", "hold_key", "view_clipboard"]},
    "bash": 4,
    **{a: 5 for a in ["wait", "pause"]},
}
EVENT_CLASS = {"AGENT_TALK": 1, "WAIT": 5, "PAUSE": 5}


def default_goals() -> list[int]:
    return nonholdout_goals() + [51]


def shared_labels(cal: pl.DataFrame, W: int, sources: str) -> pl.DataFrame:
    """project_states rows for the calendar's (non-holdout) days, with H11's column layout and day index."""
    ps = pl.scan_parquet(SHARED / "project_states.parquet").filter(
        (pl.col("w_min") == W) & (pl.col("sources").cast(pl.String) == sources) & ~pl.col("holdout")).collect()
    ps = ps.drop("day").join(cal.select("pt_date", "goal_no", "day"), on=["pt_date", "goal_no"], how="inner")
    return ps.select(pl.col("goal_no").cast(pl.Int8), "pt_date", "day", "win", "agent",
                     pl.col("project").cast(pl.String), pl.col("n").cast(pl.UInt32), pl.col("n_all").cast(pl.UInt32),
                     "n_tied", "room", "label")


def build_action(cal, W, wins):
    a = pl.scan_parquet(SHARED / "actions.parquet").select("t", "agent", pl.col("action").cast(pl.String)).collect()
    a = a.with_columns(pl.col("action").replace_strict(ACTION_CLASS, default=0).cast(pl.Int8).alias("cls"))
    e = pl.scan_parquet(SHARED / "events_core.parquet").filter(pl.col("actor_kind").cast(pl.String) == "agent").select(
        "t", "agent", pl.col("action_type").cast(pl.String)).collect()
    e = e.with_columns(pl.col("action_type").replace_strict(EVENT_CLASS, default=0).cast(pl.Int8).alias("cls"))
    x = pl.concat([a.select("t", "agent", "cls"), e.select("t", "agent", "cls")]).filter(pl.col("cls") > 0)
    x = PS.assign_windows(x, cal, W)
    lab = PS.modal(x, "cls").rename({"cls": "label"})          # deterministic: count, latest, then the class code
    return PS.attach_rooms(lab, wins)


def work_first_seen() -> pl.DataFrame:
    wr = pl.read_parquet(SHARED / "work_repos.parquet").select(pl.col("repo").alias("project"),
                                                              pl.col("first_commit_t").alias("first_seen"))
    return wr.drop_nulls("first_seen")


def build_work(cal, W, wins) -> pl.DataFrame:
    wc = pl.scan_parquet(SHARED / "work_commits.parquet").filter(WORK_FILTER).select(
        pl.col("repo").cast(pl.String).alias("project"), "t", pl.col("author_agent").alias("agent")).collect()
    wc = PS.assign_windows(wc, cal, W)
    lab = PS.modal(wc, "project", work_first_seen())
    return PS.attach_rooms(lab, wins)


def ballots_26() -> tuple[pl.DataFrame, pl.DataFrame]:
    gt = pl.read_parquet(SHARED / "ground_truth_labels.parquet").filter(pl.col("goal_no") == 26)
    b = gt.filter((pl.col("label_kind") == "ballot") & pl.col("preferred")).select(
        pl.col("unit").alias("round"), pl.col("agent_a").alias("voter"), pl.col("agent_b").alias("candidate"),
        pl.col("t_valid_from").alias("t"), pl.col("source_ref").str.replace("chat_core:message_id=", "").alias("message_id"),
        "confidence").sort("t", "voter", "candidate")
    ph = gt.filter(pl.col("label_kind").is_in(["phase", "tally", "leader"])).select(
        "label_kind", "unit", "agent", "value", "t_valid_from", "t_valid_to", "confidence", "preferred",
        pl.col("source_ref").str.replace("chat_core:message_id=", "").alias("message_id")).sort("t_valid_from")
    return b, ph


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--goals", type=int, nargs="*", default=None)
    a = ap.parse_args()
    goals = a.goals or default_goals()
    assert_not_holdout([g for g in goals if g != 51])
    cal = PS.load_calendar(goals, allow_holdout=False)
    summary = {}
    for W in WINDOWS:
        wins = PS.window_table(cal, W)
        lp = shared_labels(cal, W, "all")
        la = build_action(cal, W, wins)
        lw, pw = PS.label_projects(build_work(cal, W, wins))
        lpa = shared_labels(cal, W, "action") if W == 30 else None
        for g in sorted(set(cal["goal_no"].to_list())):
            f = R1B / f"G{g:02d}"
            f.mkdir(parents=True, exist_ok=True)
            lpg = lp.filter(pl.col("goal_no") == g).sort("day", "win", "agent")
            lpg.write_parquet(f / f"labels_project_w{W}.parquet", compression="zstd")
            PS.projects_table(lpg).write_parquet(f / f"projects_w{W}.parquet", compression="zstd") if lpg.height else None
            la.filter(pl.col("goal_no") == g).sort("day", "win", "agent").write_parquet(f / f"labels_action_w{W}.parquet", compression="zstd")
            lwg = lw.filter(pl.col("goal_no") == g).sort("day", "win", "agent")
            lwg.write_parquet(f / f"labels_work_w{W}.parquet", compression="zstd")
            pw.filter(pl.col("goal_no") == g).write_parquet(f / f"projects_work_w{W}.parquet", compression="zstd")
            if lpa is not None:
                lpa.filter(pl.col("goal_no") == g).sort("day", "win", "agent").write_parquet(
                    f / f"labels_projectact_w{W}.parquet", compression="zstd")
            wins.filter(pl.col("goal_no") == g).write_parquet(f / f"windows_w{W}.parquet", compression="zstd")
            summary.setdefault(g, {})[f"w{W}"] = {"project_rows": lpg.height, "work_rows": lwg.height}
        print(f"W={W}: project {lp.height}, action {la.height}, work {lw.height}", flush=True)
    if 26 in goals:
        b, ph = ballots_26()
        b.write_parquet(R1B / "G26" / "ballots.parquet", compression="zstd")
        ph.write_parquet(R1B / "G26" / "phases.parquet", compression="zstd")
        print(f"#26 ballots: {b.height} rows ({b.group_by('round').len().sort('round').rows()})")
    prov = {"built_by": "hypotheses/H11-potts-labor-vs-herding/scheme/build_r1b.py", "git_commit": C.git_commit(),
            "inputs": [{"source": "ai-village", "revision": C.REVISION,
                        "tables": ["project_states", "calendar", "rooms_timeline", "actions", "events_core", "work_commits",
                                   "work_repos", "ground_truth_labels"],
                        "via": "data/processed/shared (infra/shared/project_states.py, work_ledger.py, ground_truth.py)"}],
            "params": {"windows_min": list(WINDOWS), "goals": goals, "q_max": PS.Q_MAX, "min_share": PS.MIN_SHARE,
                       "work_filter": "canonical & ~imported & author_kind == agent & ~automated (DQ4 default); author time t",
                       "attention": "project_states sources=all, holdout rows dropped, day re-indexed on non-holdout days",
                       "action_tie_break": "count, latest action, class code (deterministic)"},
            "rows": summary, "built_at": dt.datetime.now(dt.timezone.utc).isoformat()}
    R1B.mkdir(parents=True, exist_ok=True)
    (R1B / "_provenance.json").write_text(json.dumps(prov, indent=1))


if __name__ == "__main__":
    main()
