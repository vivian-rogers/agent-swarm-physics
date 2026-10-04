"""H11 scheme: categorical agent states per window, one folder per goal period.

Builds data/processed/H11-potts-labor-vs-herding/G<NN>/ from the shared tables:
  labels_project_w{W}.parquet  goal_no, pt_date, day, win, agent, room, project, n, label (0 = other, 1..q)
  labels_action_w{W}.parquet   same keys, action class label (1 talk, 2 gui, 3 type, 4 bash, 5 wait)
  projects_w{W}.parquet        label -> project name, agent-window count, share, distinct agents
  windows_w{W}.parquet         every window of every active day (for circular shifts)
  votes.parquet                (#26 only) chat-declared single-candidate votes: agent, t, candidate (codes only, no text)

Usage:  uv run python hypotheses/H11-potts-labor-vs-herding/scheme/build.py [--goals 13 18 ...]
Holdout periods are refused unless --allow-holdout (used only by analysis/confirm_holdout.py).
"""
from __future__ import annotations

import argparse
import re

import polars as pl

from h11common import (C, OUT, SHARED, STRICT_HOW, WINDOWS_MIN, Q_MAX, MIN_SHARE, assert_not_holdout,
                       nonholdout_goals, write_provenance)

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
ACTION_NAMES = {0: "other", 1: "talk", 2: "gui", 3: "type", 4: "bash", 5: "wait"}
DEPLOY_PREVIEW = r"^deploy-preview-\d+--"


def load_calendar(goals, allow_holdout):
    cal = pl.read_parquet(SHARED / "calendar.parquet").filter(pl.col("goal_no").is_in(goals))
    cal = cal.filter(pl.col("n_agent_events") > 0)
    mask = C.holdout_mask(cal["pt_date"].to_list(), cal["goal_no"].to_list())
    cal = cal.with_columns(pl.Series("ho", mask))
    if not allow_holdout:
        cal = cal.filter(~pl.col("ho"))
    cal = cal.sort("pt_date").with_columns(pl.col("pt_date").rank("dense").over("goal_no").cast(pl.Int16).sub(1).alias("day"))
    return cal.select("pt_date", "goal_no", "day", "regime", "win_start", "win_end", "window_s", "ho")


def project_map():
    art = pl.read_parquet(SHARED / "artifacts.parquet").select("artifact", "kind", "name", "parent")
    par = art.select(pl.col("artifact").alias("parent"), pl.col("name").alias("parent_name"))
    art = art.join(par, on="parent", how="left")
    art = art.filter(pl.col("kind").cast(pl.String).is_in(["repo", "site", "file"]))
    art = art.with_columns(pl.coalesce("parent_name", "name").alias("project"))
    art = art.with_columns(pl.col("project").str.replace(DEPLOY_PREVIEW, ""))
    art = art.filter(~pl.col("project").str.contains(r"/e$"))  # Google 'published' placeholder ids
    return art.select("artifact", "project")


def assign_windows(df, cal, W):
    df = df.with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias("pt_date"))
    df = df.join(cal.select("pt_date", "goal_no", "day", "win_start", "win_end"), on="pt_date", how="inner")
    df = df.filter((pl.col("t") >= pl.col("win_start")) & (pl.col("t") <= pl.col("win_end")))
    return df.with_columns(((pl.col("t") - pl.col("win_start")).dt.total_seconds() // (W * 60)).cast(pl.Int16).alias("win"))


def modal(df, key):
    """Modal value of `key` per (goal, day, win, agent); ties -> the most recent."""
    g = df.group_by("goal_no", "pt_date", "day", "win", "agent", key).agg(pl.len().alias("n"), pl.col("t").max().alias("tl"))
    g = g.sort(["n", "tl"], descending=True).group_by("goal_no", "pt_date", "day", "win", "agent").agg(
        pl.col(key).first(), pl.col("n").first(), pl.col("n").sum().alias("n_all"))
    return g


def window_table(cal, W):
    rows = []
    for r in cal.iter_rows(named=True):
        nk = int(-(-r["window_s"] // (W * 60))) if r["window_s"] else 0
        for k in range(max(nk, 1)):
            rows.append({"goal_no": r["goal_no"], "pt_date": r["pt_date"], "day": r["day"], "win": k})
    w = pl.DataFrame(rows, schema={"goal_no": pl.Int8, "pt_date": pl.String, "day": pl.Int16, "win": pl.Int16})
    w = w.join(cal.select("pt_date", "win_start"), on="pt_date").with_columns(
        (pl.col("win_start") + pl.duration(seconds=(pl.col("win").cast(pl.Int64) * W * 60 + W * 30))).alias("t_mid")).drop("win_start")
    return w.with_columns(pl.col("win").cast(pl.Int16))


def attach_rooms(lab, wins):
    rt = pl.read_parquet(SHARED / "rooms_timeline.parquet")
    keys = lab.select("goal_no", "pt_date", "day", "win", "agent").unique().join(wins, on=["goal_no", "pt_date", "day", "win"])
    j = keys.join(rt, on="agent", how="left").filter(
        (pl.col("t_start") <= pl.col("t_mid")) & (pl.col("t_end").is_null() | (pl.col("t_mid") < pl.col("t_end"))))
    j = j.sort("t_start", descending=True).group_by("goal_no", "pt_date", "day", "win", "agent").agg(pl.col("room").first())
    lab = lab.join(j, on=["goal_no", "pt_date", "day", "win", "agent"], how="left")
    return lab.with_columns(pl.col("room").fill_null(0).cast(pl.Int8))


def build_project(cal, W, wins, sources=None):
    pm = project_map()
    am = pl.scan_parquet(SHARED / "artifact_mentions.parquet").filter(
        (pl.col("speaker_kind").cast(pl.String) == "agent") & pl.col("how").cast(pl.String).is_in(list(STRICT_HOW))
        & pl.col("agent").is_not_null()).select("artifact", "t", "agent", "source", "message_id", "ref_index").collect()
    am = am.join(pm, on="artifact", how="inner")
    if sources is not None:
        am = am.filter(pl.col("source").cast(pl.String).is_in(list(sources)))
    am = am.with_columns(pl.coalesce(pl.col("message_id"), pl.col("ref_index").cast(pl.String)).alias("ref"))
    am = am.unique(subset=["agent", "source", "ref", "project"])
    am = assign_windows(am, cal, W)
    lab = modal(am, "project")
    return attach_rooms(lab, wins)


def build_action(cal, W, wins):
    a = pl.scan_parquet(SHARED / "actions.parquet").select("t", "agent", pl.col("action").cast(pl.String)).collect()
    a = a.with_columns(pl.col("action").replace_strict(ACTION_CLASS, default=0).cast(pl.Int8).alias("cls"))
    e = pl.scan_parquet(SHARED / "events_core.parquet").filter(pl.col("actor_kind").cast(pl.String) == "agent").select(
        "t", "agent", pl.col("action_type").cast(pl.String)).collect()
    e = e.with_columns(pl.col("action_type").replace_strict(EVENT_CLASS, default=0).cast(pl.Int8).alias("cls"))
    x = pl.concat([a.select("t", "agent", "cls"), e.select("t", "agent", "cls")]).filter(pl.col("cls") > 0)
    x = assign_windows(x, cal, W)
    lab = modal(x, "cls").rename({"cls": "label"})
    return attach_rooms(lab, wins)


def label_projects(lab):
    """Per goal: rank projects by labeled agent-windows; keep <= Q_MAX with share >= MIN_SHARE."""
    out, proj = [], []
    for (g,), d in lab.group_by(["goal_no"], maintain_order=True):
        tot = d.height
        c = d.group_by("project").agg(pl.len().alias("aw"), pl.col("agent").n_unique().alias("n_agents")).sort(
            ["aw", "project"], descending=[True, False])
        c = c.with_columns((pl.col("aw") / tot).alias("share"))
        keep = c.filter(pl.col("share") >= MIN_SHARE).head(Q_MAX)
        mp = {p: i + 1 for i, p in enumerate(keep["project"].to_list())}
        out.append(d.with_columns(pl.col("project").replace_strict(mp, default=0).cast(pl.Int8).alias("label")))
        proj.append(c.with_columns(pl.lit(g).cast(pl.Int8).alias("goal_no"),
                                   pl.col("project").replace_strict(mp, default=0).cast(pl.Int8).alias("label")))
    return pl.concat(out), pl.concat(proj)


VOTE_RE = re.compile(r"\b(vot(e|es|ed|ing)|ballot|approve|approval)\b", re.I)
# first-person declarations ("I vote for X", "my vote: X", "I approve X and Y", "we support X")
FIRST_RE = re.compile(r"\b(i|i'm|i am|my|we|our)\b[^.!?\n]{0,40}\b(vot(e|es|ed|ing)|approv(e|al|ing)|ballot|support|endors(e|ing))\b", re.I)
RUNOFF_RE = re.compile(r"\brun-?off\b", re.I)


def build_votes(goal=26):
    """Chat-declared votes in the election week (HH22, folded into H11 G26).

    Candidates named = `chat_mentions_clean.mentions_roster` (the o1-bug-free mention sidecar, restricted to
    that day's roster). Only structural facts are stored: agent, t, named candidate codes, flags. No text."""
    ch = pl.scan_parquet(SHARED / "chat_core.parquet").filter((pl.col("goal_no") == goal) & (pl.col("speaker_kind").cast(pl.String) == "agent")
                                                            ).select("message_id", "t", "agent").collect()
    mc = pl.read_parquet(SHARED / "chat_mentions_clean.parquet").select("message_id", "mentions_roster")
    tx = pl.scan_parquet(SHARED / "chat_text.parquet").select("message_id", "text").collect()
    ch = ch.join(mc, on="message_id", how="left").join(tx, on="message_id", how="left")
    rows = []
    for r in ch.iter_rows(named=True):
        s = r["text"] or ""
        vote = bool(VOTE_RE.search(s))
        runoff = bool(RUNOFF_RE.search(s))
        if not (vote or runoff):
            continue
        named = sorted(set(r["mentions_roster"] or []))
        rows.append({"message_id": r["message_id"], "agent": r["agent"], "t": r["t"], "vote_word": vote,
                     "first_person": bool(FIRST_RE.search(s)), "runoff_word": runoff, "named": named,
                     "n_named": len(named), "candidate": named[0] if len(named) == 1 else None})
    return pl.DataFrame(rows, schema={"message_id": pl.String, "agent": pl.Int8, "t": pl.Datetime("us", "UTC"),
                                      "vote_word": pl.Boolean, "first_person": pl.Boolean, "runoff_word": pl.Boolean,
                                      "named": pl.List(pl.Int8), "n_named": pl.Int16, "candidate": pl.Int8})


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--goals", type=int, nargs="*", default=None)
    ap.add_argument("--allow-holdout", action="store_true", help="only for analysis/confirm_holdout.py")
    ap.add_argument("--out", default=str(OUT))
    a = ap.parse_args()
    goals = a.goals or nonholdout_goals()
    assert_not_holdout(goals, a.allow_holdout)
    from pathlib import Path
    out = Path(a.out)
    cal = load_calendar(goals, a.allow_holdout)
    for W in WINDOWS_MIN:
        wins = window_table(cal, W)
        lp, proj = label_projects(build_project(cal, W, wins))
        la = build_action(cal, W, wins)
        # post-hoc robustness variant (added 2026-10-03 after seeing #31's O1): computer-use actions only
        lpa = None
        if W == 30:
            lpa, _ = label_projects(build_project(cal, W, wins, sources=("action",)))
        for g in sorted(set(cal["goal_no"].to_list())):
            f = out / f"G{g:02d}"
            f.mkdir(parents=True, exist_ok=True)
            lp.filter(pl.col("goal_no") == g).sort("day", "win", "agent").write_parquet(f / f"labels_project_w{W}.parquet", compression="zstd")
            la.filter(pl.col("goal_no") == g).sort("day", "win", "agent").write_parquet(f / f"labels_action_w{W}.parquet", compression="zstd")
            if lpa is not None:
                lpa.filter(pl.col("goal_no") == g).sort("day", "win", "agent").write_parquet(f / f"labels_projectact_w{W}.parquet", compression="zstd")
            proj.filter(pl.col("goal_no") == g).write_parquet(f / f"projects_w{W}.parquet", compression="zstd")
            wins.filter(pl.col("goal_no") == g).write_parquet(f / f"windows_w{W}.parquet", compression="zstd")
        print(f"W={W}: project labels {lp.height}, action labels {la.height}")
    if 26 in goals:
        v = build_votes(26)
        v.write_parquet(out / "G26" / "votes.parquet", compression="zstd")
        print(f"votes #26: {v.height} vote/runoff-word messages; first-person vote with named candidates: "
              f"{v.filter(pl.col('vote_word') & pl.col('first_person') & (pl.col('n_named') > 0)).height}")
    write_provenance(out, "hypotheses/H11-potts-labor-vs-herding/scheme/build.py",
                     ["artifacts", "artifact_mentions", "actions", "events_core", "calendar", "rooms_timeline", "roster",
                      "chat_core", "chat_mentions_clean", "chat_text (#26 vote/runoff keyword flags only; no text stored)"],
                     {"windows_min": list(WINDOWS_MIN), "q_max": Q_MAX, "min_share": MIN_SHARE, "strict_how": list(STRICT_HOW),
                      "goals": sorted(set(cal["goal_no"].to_list())), "allow_holdout": a.allow_holdout,
                      "action_classes": ACTION_NAMES})


if __name__ == "__main__":
    main()
