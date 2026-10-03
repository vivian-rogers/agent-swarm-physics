"""H07 leakage channels between the #best and #rest forks (exploratory, non-holdout: T0 -> 2026-05-01).

Channels:
  room      an agent present in the other team's room, or both teams' agents co-present in #general and talking there
  commit    a post-split commit by an agent of the other team (git authorship; room of the author at commit time)
  artifact  an explicit reference (URL / git output / scheme-less ref; not directory guesses) to the other team's
            repository or site, or to the shared original repo rpg-game, by an agent of a team (chat or action)
  search    a history search whose query mentions the other team or fork
Output: data/processed/H07-rpg-forks/leakage.parquet (event list) and leakage_summary.json.
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from pathlib import Path

import polars as pl

sys.path.insert(0, str(Path(__file__).resolve().parent))
from h07lib import P, SH, T0, T35_END, UTC

T1 = dt.datetime(2026, 5, 1, tzinfo=UTC)
BEST_AGENTS = {20, 22, 23}  # Opus 4.6, Gemini 3.1 Pro, GPT-5.4 (#best at the split)
REPO_NAMES = {"best": ["github.com/ai-village-agents/rpg-game-best", "ai-village-agents.github.io/rpg-game-best"],
              "rest": ["github.com/ai-village-agents/rpg-game-rest", "ai-village-agents.github.io/rpg-game-rest",
                       "github.com/ai-village-agents/rpg-game-rest-week"],
              "origin": ["github.com/ai-village-agents/rpg-game", "ai-village-agents.github.io/rpg-game"]}


def team(agent):
    return "best" if agent in BEST_AGENTS else "rest"


def main():
    ro = pl.read_parquet(SH / "roster.parquet").select("agent", "name")
    names = dict(ro.iter_rows())
    rt = pl.read_parquet(SH / "rooms_timeline.parquet").filter(
        (pl.col("t_end") > T0) & (pl.col("t_start") < T1) & pl.col("room").is_in([0, 2, 3]))
    ev = []
    # --- room channel: presence in the other team's room
    for a, room, ts, te in rt.select("agent", "room", "t_start", "t_end").iter_rows():
        tm = team(a)
        if (tm == "rest" and room == 2) or (tm == "best" and room == 3):
            ev.append({"t": max(ts, T0), "t_end": min(te, T1), "agent": a, "team": tm, "channel": "room:visit",
                       "target": "best" if room == 2 else "rest", "detail": f"in #{'best' if room == 2 else 'rest'}"})
    # --- room channel: #general co-presence with talk from both teams
    cc = pl.read_parquet(SH / "chat_core.parquet", columns=["message_id", "t", "room", "speaker_kind", "agent"])
    gen = cc.filter((pl.col("room") == 0) & (pl.col("t") >= T0) & (pl.col("t") < T1) & (pl.col("speaker_kind") == "agent"))
    gen = gen.with_columns(pl.col("agent").map_elements(team, return_dtype=pl.Utf8).alias("team"),
                           pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().alias("pt_date"))
    gsum = gen.group_by("pt_date").agg(pl.len().alias("n_msgs"), (pl.col("team") == "best").sum().alias("n_best"),
                                        (pl.col("team") == "rest").sum().alias("n_rest"),
                                        pl.col("t").min().alias("t_first"), pl.col("t").max().alias("t_last")).sort("pt_date")
    for d, n, nb, nr, tf, tl in gsum.iter_rows():
        if nb > 0 and nr > 0:
            ev.append({"t": tf, "t_end": tl, "agent": None, "team": "both", "channel": "room:general_joint",
                       "target": "both", "detail": f"#general {n} msgs (best {nb}, rest {nr}) on {d}"})
    # --- commit channel
    cm = pl.read_parquet(P / "commits.parquet")
    for lin, sha, author, a, t, rname in cm.select("lineage", "sha", "author", "agent", "t_commit",
                                                    "author_room_name").iter_rows():
        if a is None or t >= T1:
            continue
        tm = team(a)
        home = "best" if lin == "best" else ("rest" if lin in ("rest", "restweek") else "origin")
        if home in ("best", "rest") and tm != home:
            ev.append({"t": t, "t_end": t, "agent": a, "team": tm, "channel": "commit:cross_fork", "target": home,
                       "detail": f"{lin} {sha[:8]} by {author} (room at commit: {rname})"})
        if home == "origin" and tm == "rest":
            ev.append({"t": t, "t_end": t, "agent": a, "team": tm, "channel": "commit:origin_by_rest", "target": "origin",
                       "detail": f"rpg-game {sha[:8]} by {author}"})
    # --- artifact channel (explicit references only)
    art = pl.read_parquet(SH / "artifacts.parquet").select("artifact", "name")
    ids = {k: set(art.filter(pl.col("name").is_in(v))["artifact"].to_list()) for k, v in REPO_NAMES.items()}
    m = pl.read_parquet(SH / "artifact_mentions.parquet").filter(
        (pl.col("t") >= T0) & (pl.col("t") < T1) & pl.col("how").is_in(["url", "output", "bare"])
        & pl.col("agent").is_not_null())
    allids = set().union(*ids.values())
    m = m.filter(pl.col("artifact").is_in(list(allids)))
    inv = {a: k for k, v in ids.items() for a in v}
    aname = dict(art.iter_rows())
    msum = []
    for a_id, t, a, source, how, verb, room in m.select("artifact", "t", "agent", "source", "how", "verb",
                                                       "room").iter_rows():
        tm = team(a)
        tgt = inv[a_id]
        msum.append((tm, tgt, source, t <= T35_END))
        if tgt != tm:
            ev.append({"t": t, "t_end": t, "agent": a, "team": tm, "channel": f"artifact:{source}", "target": tgt,
                       "detail": f"{aname[a_id]} ({how}{', ' + str(verb) if verb else ''}{', room ' + str(room) if room is not None else ''})"})
    # --- search channel
    sh = pl.read_parquet(P / "search_history_text.parquet")
    for t, a, q, qb, qr, ar, ab, arr in sh.select("t", "agent", "query", "q_best", "q_rest", "a_rpg", "a_best",
                                                  "a_rest").iter_rows():
        tm = team(a)
        other_q = qr if tm == "best" else qb
        if other_q:
            ev.append({"t": t, "t_end": t, "agent": a, "team": tm, "channel": "search:query_mentions_other",
                       "target": "rest" if tm == "best" else "best", "detail": q[:160]})
    led = pl.DataFrame(ev, infer_schema_length=None).with_columns(pl.col("agent").cast(pl.Int8)).sort("t")
    led = led.with_columns(pl.col("agent").replace_strict(names, default=None, return_dtype=pl.Utf8).alias("agent_name"),
                           (pl.col("t") <= T35_END).alias("in_35"))
    led.write_parquet(P / "leakage.parquet")
    ms = pl.DataFrame(msum, schema=["team", "target", "source", "in_35"], orient="row").group_by(
        "team", "target", "source", "in_35").len().sort("team", "target", "source", "in_35")
    summary = {"by_channel": led.group_by("channel", "in_35").len().sort("channel", "in_35").to_dicts(),
               "artifact_refs_by_team_target": ms.to_dicts(),
               "general_joint_days": gsum.with_columns(pl.col("pt_date").cast(pl.Utf8)).to_dicts(),
               "searches_total": len(sh), "searches_mention_rpg": int(sh["q_rpg"].sum())}
    (P / "leakage_summary.json").write_text(json.dumps(summary, indent=1, default=str))
    pl.Config.set_tbl_rows(200); pl.Config.set_tbl_width_chars(250); pl.Config.set_fmt_str_lengths(110)
    print(led.filter(pl.col("t") <= dt.datetime(2026, 4, 5, tzinfo=UTC)).select(
        "t", "agent_name", "team", "channel", "target", "detail"))
    print(json.dumps(summary, indent=1, default=str)[:4000])


if __name__ == "__main__":
    main()
