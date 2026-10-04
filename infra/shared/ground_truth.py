"""DQ6: the shared ground-truth labels table (one agreed answer key for detector validation).

Long format, codes only, no text. One row per (label, derivation). Where two existing derivations disagree, each
gets its own row, they share a `conflict_group`, and `preferred` marks the one to trust (docs give the reason).

Kinds built (goal period in brackets; HO = locked holdout, rows carry holdout = True):
  team, judge, debate_result, phase           #12 debates (H21's hand-verified labels file; H37 reads the same file)
  phase, tally, leader, ballot, vote_declaration
                                              #26 election (administrator announcements; H11's declaration rule)
  saboteur                                    #34 (HO) agent-day roles: H21/H37 self-identification rule, and the
                                              system-logged d6 roll in the agent's own computer-use output
  leader, checkpoint                          #35 lead designers (operator kickoff); #44 temporary fine-tuned leader
                                              and its checkpoints (operator messages; H23); #45 (HO) Fine-Tuned Leader
                                              and its model-string correction
  role, role_class, rival_pair, opposed_pair  #51 private roles (raw agent_goals = operator-written goal text;
                                              operator messages; H22's pair coding). Tail 09-07+ is HO.
  room_assignment                             operator messages that assign rooms (#35-#51)
  room_presence                               system room tags (rooms_timeline), rooms era (2026-02-25+)

Columns: row_id, goal_no, label_kind, unit, agent, agent_a, agent_b, value, detail, t_valid_from, t_valid_to (UTC),
  source_kind (operator message | goal text | system event | agent declaration | derived), source_ref (table + id),
  confidence (high | medium | low), derived_by, conflict_group, preferred, holdout.
Pairs use agent_a / agent_b (agent is null); a vote or ballot is the pair voter (agent_a) -> candidate (agent_b).
Events (declarations, results) have t_valid_to == t_valid_from.

#34 is in the locked holdout. Its rows are an answer key, not an analysis: this script extracts them and computes no
statistic on them; `--validate` reports only their row count. The roll scan needs one pass over raw
computer_use_turns (gzip -dc | grep, 2 processes; `--turns-cache` reuses a pre-filtered extract).

Usage:
  uv run python infra/shared/ground_truth.py                 build data/processed/shared/ground_truth_labels.parquet
  uv run python infra/shared/ground_truth.py --validate      coverage, derivation disagreements, hand-check sample
Docs: infra/data-quality/ground_truth_labels.md
"""
from __future__ import annotations

import os

for _v in ("POLARS_MAX_THREADS", "OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS", "VECLIB_MAXIMUM_THREADS"):
    os.environ.setdefault(_v, "2")

import argparse  # noqa: E402
import datetime as dt  # noqa: E402
import gzip  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import subprocess  # noqa: E402
import sys  # noqa: E402
from pathlib import Path  # noqa: E402

import orjson  # noqa: E402
import polars as pl  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import (OUT, PT, RAW, REVISION, ROOT, UTC, git_commit, holdout_mask, load_goals,  # noqa: E402
                    load_holdout, mention_regexes)

TABLE = OUT / "ground_truth_labels.parquet"
H21_LABELS = ROOT / "hypotheses/H21-debate-antiferromagnet/scheme/labels/g12_debates.json"
EXPORT_END = dt.datetime(2026, 9, 20, 13, 5, 12, tzinfo=UTC)  # manifest exportedAt: end of open intervals
ROOMS_ERA = "2026-02-25"  # NE12: rooms exist from here; before it everyone is in #general

SK_OP, SK_GOAL, SK_SYS, SK_DECL, SK_DER = "operator message", "goal text", "system event", "agent declaration", "derived"


# ============================================================================================ helpers
def T(s: str) -> dt.datetime:
    """ISO string (with or without offset; naive = UTC) -> aware UTC datetime."""
    t = dt.datetime.fromisoformat(s.replace("Z", "+00:00"))
    return (t if t.tzinfo else t.replace(tzinfo=UTC)).astimezone(UTC)


def pt_midnight(d: str) -> dt.datetime:
    return dt.datetime.fromisoformat(d).replace(tzinfo=PT).astimezone(UTC)


def ptd(t: dt.datetime) -> str:
    return t.astimezone(PT).date().isoformat()


def roster():
    return pl.read_parquet(OUT / "roster.parquet")


def name_codes():
    r = roster()
    return dict(zip(r["name"].to_list(), r["agent"].to_list())), dict(zip(r["agent_id"].to_list(), r["agent"].to_list()))


GOALS = None


def goals():
    global GOALS
    if GOALS is None:
        g = load_goals()
        for i, x in enumerate(g):
            x["end_eff"] = g[i + 1]["start"] if i + 1 < len(g) else EXPORT_END
        GOALS = {x["goal_no"]: x for x in g}
    return GOALS


def goal_of(t: dt.datetime) -> int:
    n = 0
    for g in goals().values():
        if t >= g["start"]:
            n = g["goal_no"]
    return n


def R(goal_no, kind, value, t0, t1, source_kind, source_ref, confidence, derived_by, *, agent=None, agent_a=None,
      agent_b=None, unit=None, detail=None, conflict_group=None, preferred=True):
    return {"goal_no": goal_no, "label_kind": kind, "unit": unit, "agent": agent, "agent_a": agent_a, "agent_b": agent_b,
            "value": None if value is None else str(value), "detail": detail, "t_valid_from": t0,
            "t_valid_to": t1 if t1 is not None else t0, "source_kind": source_kind, "source_ref": source_ref,
            "confidence": confidence, "derived_by": derived_by, "conflict_group": conflict_group, "preferred": preferred}


def chat_ref(mid):
    return f"chat_core:message_id={mid}"


_NORM = str.maketrans({c: "-" for c in "‐‑‒–—―−"})


def norm_text(s: str) -> str:
    """Hyphen variants -> '-', 'Opus-4.7' -> 'Opus 4.7' (the name regexes need the plain forms)."""
    return re.sub(r"(Opus|Sonnet|Haiku|Fable)-(\d)", r"\1 \2", (s or "").translate(_NORM))


def name_matchers():
    """agent code -> compiled name regex (common.mention_regexes, keyed by code)."""
    r = roster()
    pats = mention_regexes([{"id": a, "name": n} for a, n in zip(r["agent"].to_list(), r["name"].to_list())])
    return pats


def first_candidate(text: str, after: int, candidates, pats):
    """The candidate whose name occurs first at or after position `after` in text (None if none)."""
    best, pos = None, None
    for c in candidates:
        m = pats[c].search(text, after)
        if m and (pos is None or m.start() < pos):
            best, pos = c, m.start()
    return best


# ============================================================================================ #12 debates
def g12_windows(debates, day_end, rule):
    """Phase windows per held debate. rule 'H21' = H21 build_g12 (post end clamped at the day's last agent event);
    'H37' = H37 select_samples.debate_windows (no day-end clamp). Both: pre = max(lineup, motion, first speech - 15 min,
    previous post end); post = [verdict, min(verdict + 10 min, next pre))."""
    out = []
    for k, d in enumerate(debates):
        pre = max(T(d["t_lineup"]), T(d["t_motion"]), T(d["t_first_speech"]) - dt.timedelta(minutes=15))
        if k > 0:
            pre = max(pre, out[-1]["post_end"])
        post = T(d["t_verdict"]) + dt.timedelta(minutes=10)
        if k + 1 < len(debates):
            nx = debates[k + 1]
            post = min(post, max(T(nx["t_lineup"]), T(nx["t_motion"]), T(nx["t_first_speech"]) - dt.timedelta(minutes=15)))
        if rule == "H21":
            post = min(post, day_end[ptd(T(d["t_verdict"]))])
        out.append({"debate": d["debate"], "pre": pre, "fs": T(d["t_first_speech"]), "verdict": T(d["t_verdict"]),
                    "post_end": post})
    return out


def rows_g12():
    lab = json.loads(H21_LABELS.read_text())
    deb = sorted([d for d in lab["debates"] if d["held"]], key=lambda d: T(d["t_first_speech"]))
    n2c, _ = name_codes()
    cal = pl.read_parquet(OUT / "calendar.parquet").filter(pl.col("goal_no") == 12)
    day_end = dict(zip(cal["pt_date"].to_list(), cal["win_end"].to_list()))
    w21 = {w["debate"]: w for w in g12_windows(deb, day_end, "H21")}
    w37 = {w["debate"]: w for w in g12_windows(deb, day_end, "H37")}
    src = "H21 scheme/labels/g12_debates.json (hand-verified 2026-10-03; read by H37 select_samples.debate_windows, DQ2)"
    out = []
    for d in deb:
        k, w = d["debate"], w21[d["debate"]]
        u = f"debate_{k:02d}"
        for side in ("gov", "opp", "bench"):
            for nm in d[side]:
                det = {"gov": "motion_side=pro" if d["gov_argues_for_motion"] else "motion_side=con",
                       "opp": "motion_side=con" if d["gov_argues_for_motion"] else "motion_side=pro",
                       "bench": "unassigned (absent at draft)"}[side]
                out.append(R(12, "team", side, w["pre"], w["post_end"], SK_DECL, chat_ref(d["lineup_message_id"]), "high",
                             src, agent=n2c[nm], unit=u, detail=det))
        out.append(R(12, "judge", "judge", w["pre"], w["post_end"], SK_DECL, chat_ref(d["verdict_message_id"]), "high", src,
                     agent=n2c[d["judge"]], unit=u, detail=f"motion_chosen_by={d['motion_chosen_by']}"))
        out.append(R(12, "debate_result", d["winner"].lower(), w["verdict"], w["verdict"], SK_DECL,
                     chat_ref(d["verdict_message_id"]), "high", src, unit=u,
                     detail=f"score={d['score']}" if d["score"] else "score=not stated"))
        # phases: deb is anchored on two messages (high); pre/post are rule windows (medium)
        out.append(R(12, "phase", "deb", w["fs"], w["verdict"], SK_DER, chat_ref(d["first_speech_message_id"]), "high",
                     "H21 phase rule = H37 debate_windows (first speech -> verdict)", unit=u))
        out.append(R(12, "phase", "pre", w["pre"], w["fs"], SK_DER, chat_ref(d["lineup_message_id"]), "medium",
                     "H21 phase rule = H37 debate_windows (max(lineup, motion, first speech - 15 min, previous post end))",
                     unit=u))
        same = w37[k]["post_end"] == w["post_end"]
        cg = None if same else f"g12_post_end_d{k:02d}"
        out.append(R(12, "phase", "post", w["verdict"], w["post_end"], SK_DER, chat_ref(d["verdict_message_id"]), "medium",
                     "H21 build_g12 (post end = min(verdict + 10 min, next pre, day's last agent event))", unit=u,
                     conflict_group=cg))
        if not same:
            out.append(R(12, "phase", "post", w["verdict"], w37[k]["post_end"], SK_DER, chat_ref(d["verdict_message_id"]),
                         "medium", "H37 select_samples.debate_windows (no day-end clamp)", unit=u, conflict_group=cg,
                         preferred=False))
    return out


# ============================================================================================ #26 election
# Structural anchors, hand-read from the #26 chat (2026-10-04); the administrator (GPT-5, agent 10) ran round 1.
G26_PHASES = [  # (value, t_from, t_to, ref message id, detail)
    ("approval_vote", "2026-01-05T19:26:03.168653", "2026-01-05T19:30:00", "2c6cfb2f-9ed5-4046-b554-5b0affb2f7f7",
     "chat approval ballot after the Form ballot failed; 7 candidates; deadline 11:30:00 PT; one vote posted 11:25 PT accepted"),
    ("runoff", "2026-01-05T19:32:19.951842", "2026-01-05T19:34:00", "8d08d622-da7d-4341-a2e6-6512641d1a92",
     "single-choice runoff among the tied three (17, 0, 6); deadline 11:34:00 PT"),
    ("result", "2026-01-05T19:35:22.589746", "2026-01-05T19:35:22.589746", "0aa5f445-470c-44b2-80b6-bd0db48c652b",
     "official result: agent 17 elected; accepted by agent 17 at chat_core:message_id=b0f75a7e-d3b1-437c-ac1a-ab14fe922722"),
    ("confirmatory_vote", "2026-01-09T18:45:00", "2026-01-09T19:00:00", "d9ff6720-986d-414b-850b-bf0f03725fe0",
     "plurality re-election of the incumbent (17 vs 6); plan at chat_core:message_id=a90dfe16-2b82-4b81-a266-70f4af3e8afc"),
    ("result", "2026-01-09T19:00:43.077738", "2026-01-09T19:00:43.077738", "a87324f0-47b8-4dae-b2e7-b20879dc6033",
     "final result: agent 17 re-elected 9-0; confirmed by agent 17 at chat_core:message_id=d0752202-6c53-41a9-b7c4-4b5404bb17b3"),
]
G26_TALLIES = [  # (unit, ref, {candidate: count}) transcribed from the official announcements
    ("approval", "8d08d622-da7d-4341-a2e6-6512641d1a92", {17: 9, 0: 9, 6: 9, 16: 7, 12: 7, 15: 4, 13: 2}),
    ("runoff", "0aa5f445-470c-44b2-80b6-bd0db48c652b", {17: 7, 6: 1, 0: 0}),
    ("confirmatory", "a87324f0-47b8-4dae-b2e7-b20879dc6033", {17: 9, 6: 0}),
]
G26_ROUNDS = {  # ballot extraction rule per round: window, ballot pattern, candidates
    "approval": ("2026-01-05T19:20:00", "2026-01-05T19:30:00.999999", r"\bI\s+approve\b", (17, 0, 6, 16, 12, 15, 13), True),
    # the ballot format the administrator asked for ("Runoff: I choose X"); "[one of: ...]" is the template itself
    "runoff": ("2026-01-05T19:32:19.951842", "2026-01-05T19:34:00.999999",
               r"\brun-?off:?\s*I\s+(?:choose|pick|vote(?:\s+for)?)\b\s*(?!\[)", (17, 0, 6), False),
    # first-person only ("Please cast your vote for either ..." is not a ballot)
    "confirmatory": ("2026-01-09T18:45:00", "2026-01-09T19:00:00.999999",
                     r"\bI\s+vote\s+for\b|\bmy\s+vote\s+(?:is|goes\s+to)\b|\bI(?:'m|\s+am)\s+voting\s+for\b|\bI\s+cast\s+my\s+vote\s+for\b",
                     (17, 6), False),
}
# H11's rule (hypotheses/H11-potts-labor-vs-herding/scheme/build.py: build_votes), copied verbatim
H11_VOTE_RE = re.compile(r"\b(vot(e|es|ed|ing)|ballot|approve|approval)\b", re.I)
H11_FIRST_RE = re.compile(r"\b(i|i'm|i am|my|we|our)\b[^.!?\n]{0,40}\b(vot(e|es|ed|ing)|approv(e|al|ing)|ballot|support|endors(e|ing))\b", re.I)
H11_RUNOFF_RE = re.compile(r"\brun-?off\b", re.I)


def g26_chat():
    c = pl.read_parquet(OUT / "chat_core.parquet", columns=["message_id", "t", "pt_date", "goal_no", "speaker_kind", "agent"])
    m = pl.read_parquet(OUT / "chat_mentions_clean.parquet", columns=["message_id", "mentions_roster"])
    assert c.height == m.height and (c["message_id"] == m["message_id"]).all()
    c = c.with_columns(m["mentions_roster"]).filter((pl.col("goal_no") == 26) & (pl.col("speaker_kind").cast(pl.String) == "agent"))
    tx = pl.read_parquet(OUT / "chat_text.parquet", columns=["message_id", "text"]).filter(
        pl.col("message_id").is_in(c["message_id"].to_list()))
    return c.join(tx, on="message_id", how="left").sort("t", "message_id")


def h11_votes(c):
    """H11 build_votes, reimplemented on the same inputs (validated against H11's votes.parquet in --validate)."""
    rows = []
    for r in c.iter_rows(named=True):
        s = r["text"] or ""
        vote, runoff = bool(H11_VOTE_RE.search(s)), bool(H11_RUNOFF_RE.search(s))
        if not (vote or runoff):
            continue
        named = sorted(set(r["mentions_roster"] or []))
        rows.append({"message_id": r["message_id"], "agent": r["agent"], "t": r["t"], "vote_word": vote,
                     "first_person": bool(H11_FIRST_RE.search(s)), "runoff_word": runoff, "named": named,
                     "n_named": len(named), "candidate": named[0] if len(named) == 1 else None})
    return rows


def g26_ballots(c):
    """Ballots cast inside the announced voting windows: one per voter per round (last for approval, first otherwise)."""
    pats = name_matchers()
    anchors = {x[3] for x in G26_PHASES} | {x[1] for x in G26_TALLIES} | {"2c6cfb2f-9ed5-4046-b554-5b0affb2f7f7"}
    out = {}
    for rnd, (a, b, pat, cands, multi) in G26_ROUNDS.items():
        rx = re.compile(pat, re.I)
        x = c.filter((pl.col("t") >= T(a)) & (pl.col("t") <= T(b)) & ~pl.col("message_id").is_in(list(anchors)))
        got = {}
        for r in x.iter_rows(named=True):
            s = norm_text(r["text"])
            m = rx.search(s)
            if not m:
                continue
            if multi:
                chosen = sorted(cc for cc in cands if pats[cc].search(s, m.end()))
            else:
                one = first_candidate(s, m.end(), cands, pats)
                chosen = [one] if one is not None else []
            if not chosen:
                continue
            if multi or r["agent"] not in got:  # approval: the last ballot counts; single-choice rounds: the first
                got[r["agent"]] = (r["message_id"], r["t"], chosen)
        out[rnd] = got
    return out


def rows_g26():
    c = g26_chat()
    out = []
    g27 = goals()[27]["start"]
    for val, a, b, ref, det in G26_PHASES:
        unit = "round1" if a.startswith("2026-01-05") else "round2"
        out.append(R(26, "phase", val, T(a), T(b), SK_DECL, chat_ref(ref), "high",
                     "hand-read administrator / organizer announcements (DQ6)", unit=unit, detail=det))
    for unit, ref, counts in G26_TALLIES:
        t = c.filter(pl.col("message_id") == ref)["t"][0]
        for cand, n in counts.items():
            out.append(R(26, "tally", n, t, t, SK_DECL, chat_ref(ref), "high", "transcribed from the official announcement (DQ6)",
                         agent=cand, unit=unit))
    t1, t2 = T(G26_PHASES[2][1]), T(G26_PHASES[4][1])
    out.append(R(26, "leader", "elected_leader", t1, t2, SK_DECL, chat_ref(G26_PHASES[2][3]), "high",
                 "administrator's official result; corroborated by the winner's acceptance, the 01-09 re-election and the dataset's goal summary",
                 agent=17, unit="term1", detail="runoff 7-1-0 after a 9-9-9 approval tie"))
    out.append(R(26, "leader", "elected_leader", t2, g27, SK_DECL, chat_ref(G26_PHASES[4][3]), "high",
                 "organizer's final result (confirmatory plurality vote)", agent=17, unit="term2", detail="re-elected 9-0"))
    # ballots (strict rule, validated against the official tallies)
    ball = g26_ballots(c)
    for rnd, got in ball.items():
        close = T(G26_ROUNDS[rnd][1])
        for voter, (mid, t, chosen) in got.items():
            for cand in chosen:
                out.append(R(26, "ballot", {"approval": "approve", "runoff": "runoff_choice", "confirmatory": "vote"}[rnd],
                             t, close, SK_DECL, chat_ref(mid), "high",
                             "infra/shared/ground_truth.py g26_ballots (announced window + ballot format)",
                             agent_a=voter, agent_b=cand, unit=rnd, detail=f"n_named={len(chosen)}"))
    # H11 declarations (the rule H11 and H31 use); low confidence: any vote-word message naming roster agents
    for v in h11_votes(c):
        if not v["named"]:
            continue
        h11p = v["vote_word"] and v["first_person"]
        h31p = h11p and v["candidate"] is not None
        det = (f"first_person={int(v['first_person'])};vote_word={int(v['vote_word'])};runoff_word={int(v['runoff_word'])};"
               f"n_named={v['n_named']};h11_primary={int(h11p)};h31_primary={int(h31p)}")
        for cand in v["named"]:
            out.append(R(26, "vote_declaration", "declared", v["t"], v["t"], SK_DECL, chat_ref(v["message_id"]), "low",
                         "H11 scheme/build.py build_votes (reimplemented; also read by H31 ev26, H37 g26_votes)",
                         agent_a=v["agent"], agent_b=cand, detail=det))
    # runoff onset: record vs the two keyword rules (conflict)
    cg = "g26_runoff_onset"
    out.append(R(26, "phase", "runoff_onset", T(G26_PHASES[1][1]), T(G26_PHASES[1][1]), SK_DECL, chat_ref(G26_PHASES[1][3]),
                 "high", "administrator's runoff announcement", unit="round1", conflict_group=cg))
    hv = h11_votes(c)
    ro = sorted((v for v in hv if v["runoff_word"]), key=lambda v: v["t"])
    if ro:
        out.append(R(26, "phase", "runoff_onset", ro[0]["t"], ro[0]["t"], SK_DER, chat_ref(ro[0]["message_id"]), "low",
                     "H31 analysis/explore.py ev26 (first agent message containing 'runoff')", conflict_group=cg, preferred=False))
        t_on, mid_on = h11_onset(ro)
        if t_on is not None:
            out.append(R(26, "phase", "runoff_onset", t_on, t_on, SK_DER, chat_ref(mid_on), "low",
                         "H11 analysis/explore.py votes_g26 (first 30-min window with >= 2 'runoff' messages; window start)",
                         conflict_group=cg, preferred=False))
    return out


def h11_onset(ro):
    """H11's onset: first 30-min window (from each day's calendar win_start) holding >= 2 runoff-word agent messages."""
    cal = pl.read_parquet(OUT / "calendar.parquet").filter(pl.col("goal_no") == 26).sort("pt_date")
    for d, ws, we in zip(cal["pt_date"].to_list(), cal["win_start"].to_list(), cal["win_end"].to_list()):
        k = 0
        while ws + dt.timedelta(minutes=30 * k) <= we:
            a, b = ws + dt.timedelta(minutes=30 * k), ws + dt.timedelta(minutes=30 * (k + 1))
            inw = [v for v in ro if a <= v["t"] < b]
            if len(inw) >= 2:
                return a, inw[1]["message_id"]
            k += 1
    return None, None


# ============================================================================================ #34 saboteurs (HOLDOUT)
def h21_patterns():
    """H21's pre-registered SAB/VIL patterns, read from its script (H37 does the same); H21's code is not modified."""
    src = (ROOT / "hypotheses/H21-debate-antiferromagnet/analysis/confirm_g34.py").read_text()
    ns: dict = {}
    for name in ("SAB_PATTERNS", "VIL_PATTERNS"):
        m = re.search(rf"^{name} = \[.*?^\]", src, re.S | re.M)
        exec(m.group(0), {}, ns)
    return ns["SAB_PATTERNS"], ns["VIL_PATTERNS"]


def g34_days():
    cal = pl.read_parquet(OUT / "calendar.parquet").filter(pl.col("goal_no") == 34)
    return sorted(cal["pt_date"].to_list())


def rows_g34_rule():
    """H21 confirm_g34.label_agent_days (= H37 confirm_g34.label_agent_days), keeping the first matching row ids."""
    SAB, VIL = h21_patterns()
    sab, vil = re.compile("|".join(SAB), re.I), re.compile("|".join(VIL), re.I)
    days = set(g34_days())
    it = (pl.read_parquet(OUT / "intentions.parquet", columns=["event_index", "t", "agent"])
          .with_columns(pl.col("t").dt.convert_time_zone("America/Los_Angeles").dt.date().cast(pl.String).alias("pt_date"))
          .filter(pl.col("pt_date").is_in(list(days)))
          .join(pl.read_parquet(OUT / "intentions_text.parquet", columns=["event_index", "goal_text"]), on="event_index", how="left")
          .select("agent", "pt_date", "t", pl.col("goal_text").alias("text"),
                  pl.format("intentions:event_index={}", pl.col("event_index")).alias("ref")))
    ch = (pl.read_parquet(OUT / "chat_core.parquet", columns=["message_id", "t", "pt_date", "goal_no", "speaker_kind", "agent"])
          .filter((pl.col("goal_no") == 34) & (pl.col("speaker_kind").cast(pl.String) == "agent"))
          .join(pl.read_parquet(OUT / "chat_text.parquet", columns=["message_id", "text"]), on="message_id", how="left")
          .select("agent", "pt_date", "t", "text", pl.format("chat_core:message_id={}", pl.col("message_id")).alias("ref")))
    allt = pl.concat([it, ch]).sort("agent", "pt_date", "t")
    out = []
    for (a, d), g in allt.group_by(["agent", "pt_date"], maintain_order=True):
        sref = next((r for t, r in zip(g["text"].to_list(), g["ref"].to_list()) if sab.search(t or "")), None)
        vref = next((r for t, r in zip(g["text"].to_list(), g["ref"].to_list()) if vil.search(t or "")), None)
        label = "ambiguous" if (sref and vref) else "saboteur" if sref else "villager"
        ref = sref or vref or f"intentions+chat_core:agent={a};pt_date={d} (no pattern matched)"
        det = f"sab_ref={sref or '-'};vil_ref={vref or '-'};n_texts={g.height}"
        out.append(R(34, "saboteur", label, pt_midnight(d), pt_midnight(d) + dt.timedelta(days=1), SK_DECL, ref, "low",
                     "H21 analysis/confirm_g34.py label_agent_days (SAB/VIL self-identification patterns; shared by H37)",
                     agent=int(a), unit=f"day_{d}", conflict_group=f"g34_a{int(a):02d}_{d}"))
    return out


ROLL_CMD = re.compile(r"randint\(\s*1\s*,\s*6\s*\)|randrange\(\s*1\s*,\s*7\s*\)|randbelow\(\s*6\s*\)|shuf\s+-i\s*1\s*-\s*6"
                      r"|RANDOM\s*%\s*6|choice\(\s*(?:range\(\s*1\s*,\s*7\s*\)|\[\s*1\s*,\s*2\s*,\s*3\s*,\s*4\s*,\s*5\s*,\s*6\s*\])"
                      r"|\bd6\b|\bdice\b|\bdie\b|\broll", re.I)


def parse_roll(output: str | None):
    """The d6 value printed by a roll command (None if not a clean 1..6 result)."""
    if not output:
        return None
    s = output.strip()
    if re.fullmatch(r"[1-6]", s):
        return int(s)
    m = re.search(r"(?:roll(?:ed)?|result|d6|dice|die)\D{0,15}?\b([1-6])\b(?![\d.])", s, re.I)
    if m and len(s) <= 200:
        return int(m.group(1))
    lines = [x.strip() for x in s.splitlines() if x.strip()]
    if lines and re.fullmatch(r"[1-6]", lines[-1]) and len(lines) <= 3:
        return int(lines[-1])
    return None


def scan_g34_turns(cache: Path | None):
    """Computer-use turns on #34 days whose bash command looks like a die roll: codes + parsed value only."""
    days = set(g34_days())
    lo, hi = min(days), max(days)
    if cache and cache.exists():
        src = open(cache, "rb")
        proc = None
    else:
        cmd = (f"gzip -dc '{RAW / 'computer_use_turns.jsonl.gz'}' | LC_ALL=C grep -E "
               "'\"created_at\":\"2026-03-(0[5-9]|1[0-5]) '")
        proc = subprocess.Popen(cmd, shell=True, stdout=subprocess.PIPE)
        src = proc.stdout
    sess = {}
    found = []
    for line in src:
        r = orjson.loads(line)
        act = r.get("agent_action") or {}
        cmdtxt = act.get("command") if isinstance(act, dict) else None
        if not cmdtxt or not ROLL_CMD.search(cmdtxt):
            continue
        t = T(r["created_at"])
        if not (lo <= ptd(t) <= hi):
            continue
        found.append({"turn_id": r["id"], "session_id": r["session_id"], "t": t, "pt_date": ptd(t),
                      "value": parse_roll(r.get("output")), "strong": bool(re.search(
                          r"randint\(\s*1\s*,\s*6|randrange\(\s*1\s*,\s*7|randbelow\(\s*6|shuf\s+-i\s*1\s*-\s*6|RANDOM\s*%\s*6|choice\(", cmdtxt))})
    src.close()
    if proc:
        proc.wait()
    need = {f["session_id"] for f in found}
    _, id2c = name_codes()
    with gzip.open(RAW / "computer_use_sessions.jsonl.gz", "rb") as f:
        for line in f:
            if b'"id":"' not in line:
                pass
            s = orjson.loads(line)
            if s["id"] in need:
                sess[s["id"]] = id2c.get(s["agent_id"])
    for f_ in found:
        f_["agent"] = sess.get(f_["session_id"])
    return found


def rows_g34_rolls(cache):
    """One row per agent-day with a parsed roll: the first strong roll command of the day (system-logged output)."""
    found = [f for f in scan_g34_turns(cache) if f["agent"] is not None and f["value"] is not None and f["strong"]]
    by = {}
    for f in sorted(found, key=lambda f: f["t"]):
        by.setdefault((f["agent"], f["pt_date"]), []).append(f)
    out = []
    for (a, d), fs in by.items():
        first = fs[0]
        vals = {f["value"] for f in fs}
        conf = "high" if len(vals) == 1 else "medium"
        det = f"n_rolls={len(fs)};values_agree={int(len(vals) == 1)}"
        out.append(R(34, "saboteur", "saboteur" if first["value"] == 1 else "villager", pt_midnight(d),
                     pt_midnight(d) + dt.timedelta(days=1), SK_SYS, f"computer_use_turns:id={first['turn_id']}", conf,
                     "infra/shared/ground_truth.py rows_g34_rolls (first d6 roll command of the day; value from its stdout)",
                     agent=int(a), unit=f"day_{d}", detail=det, conflict_group=f"g34_a{int(a):02d}_{d}"))
    return out


def rows_g34(cache):
    rule, rolls = rows_g34_rule(), rows_g34_rolls(cache)
    have_roll = {r["conflict_group"] for r in rolls}
    have_rule = {r["conflict_group"] for r in rule}
    for r in rule:
        r["preferred"] = r["conflict_group"] not in have_roll
        if r["conflict_group"] not in have_roll:
            r["conflict_group"] = None
    for r in rolls:
        if r["conflict_group"] not in have_rule:
            r["conflict_group"] = None
    return rule + rolls


# ============================================================================================ #44 / #45 leader
CHECKPOINTS = [  # (name, from, to, ref of 'up and running', ref of the end) from the operator (human b9e8869cbd) in #best
    ("qwen-v3", "2026-05-26T19:15:47.698593", "2026-05-26T19:26:51.051790", "c1c9cbfe-3769-4f22-98ee-40cd0d34aafc",
     "a04c6bc4-eb8d-4d4c-875a-5f9c7a8f9058"),
    ("qwen-v10", "2026-05-28T17:04:46.230846", "2026-05-28T20:04:02.231489", "5e50d554-2d4b-4781-a778-ee52ac3a6475",
     "97acae3e-87c7-4d99-a324-825178c6de81"),
    ("kimi-v2", "2026-05-28T20:04:02.231489", "2026-05-28T20:07:10.329865", "97acae3e-87c7-4d99-a324-825178c6de81",
     "ce39e4b1-7cbf-4ce1-8c88-2c8951c3ca2a"),
    ("kimi-v4-curated56", "2026-05-28T20:07:10.329865", "2026-05-28T20:41:18.412911", "ce39e4b1-7cbf-4ce1-8c88-2c8951c3ca2a",
     "40d7b01d-3d46-4569-9842-ef796feca2be"),
    ("kimi-v7-aug-64", "2026-05-29T18:24:51.012390", None, "90edede8-ac21-425c-ba4a-38d0fefa14a7", None),
]
H23_CHECKPOINTS = {"qwen-v3": "2026-05-26T19:15:47", "qwen-v10": "2026-05-28T17:04:46", "kimi-v2": "2026-05-28T20:04:00",
                   "kimi-v4-curated56": "2026-05-28T20:07:10", "kimi-v7-aug-64": "2026-05-29T18:24:51"}  # h23lib.CHECKPOINTS


LEAD_DESIGNERS = [  # #35 kickoff (operator): one Lead Designer per room on each of the first three days
    ("2026-03-16", 2, 23), ("2026-03-16", 3, 18), ("2026-03-17", 2, 20), ("2026-03-17", 3, 19),
    ("2026-03-18", 2, 22), ("2026-03-18", 3, 6)]
LEAD_REF = "e2f20a53-3c89-4dbe-9b61-e39ad420812d"
# #45 (holdout): the operator corrected the Fine-Tuned Leader's model string 11 min into its first day
G45_FIX = ("2026-06-01T17:15:40.790213", "79436bf6-a97f-4eea-a47c-3d8ab9d622d5")


def rows_leaders():
    out = []
    for d, room, a in LEAD_DESIGNERS:
        out.append(R(35, "leader", "lead_designer", pt_midnight(d), pt_midnight(d) + dt.timedelta(days=1), SK_OP,
                     chat_ref(LEAD_REF), "high", "operator kickoff #35 (lead-designer schedule), hand-read (DQ6)", agent=a,
                     unit=f"day_{d}", detail=f"room={ROOM_NAMES()[room]}; directs that room's fork for the day"))
    end44 = goals()[45]["start"]
    for name, a, b, ref, ref_end in CHECKPOINTS:
        t1 = T(b) if b else end44
        det = f"end_ref={chat_ref(ref_end)}" if ref_end else "runs to the end of #44; same weights as agent 30 in #45 (roster.model_string)"
        out.append(R(44, "checkpoint", name, T(a), t1, SK_OP, chat_ref(ref), "high",
                     "operator messages in #best (H23 analysis/h23lib.py CHECKPOINTS uses the same starts)", agent=28,
                     detail=det))
    out.append(R(44, "leader", "temporary_finetuned_leader", T(CHECKPOINTS[0][1]), end44, SK_OP, chat_ref(CHECKPOINTS[0][3]),
                 "high", "operator message (first deployment) + roster agent 28 + goal text #44", agent=28,
                 detail="test deployments of the leader being fine-tuned; ran intermittently (see checkpoint rows)"))
    g45 = goals()[45]
    tfix = T(G45_FIX[0])
    out.append(R(45, "checkpoint", "kimi-leader 32k non-peft model string", g45["start"], tfix, SK_OP, chat_ref(G45_FIX[1]),
                 "medium", "operator message: the leader started the day on the 32k-context non-peft model string", agent=30,
                 detail="first ~11 min of agent 30's first day (its first event 2026-06-01 17:04 UTC)"))
    out.append(R(45, "checkpoint", "kimi-leader-v7-aug-64", tfix, g45["end_eff"], SK_OP, chat_ref(G45_FIX[1]), "high",
                 "operator message (corrected model string; roster.model_string of agent 30)", agent=30))
    out.append(R(45, "leader", "finetuned_leader", g45["start"], g45["end_eff"], SK_GOAL,
                 "village_goals:goal_no=45;roster:agent=30;chat_core:message_id=10d59e72-ff8b-4817-9b74-3209a4de6d55", "high",
                 "goal text 'Follow your leader!' + roster (agent 30 joined 06-01, left 06-08) + operator kickoff (#best)", agent=30,
                 detail="leads #best only; #rest has its own goal"))
    return out


# ============================================================================================ #51 roles
SUPPORT = {"performance coach", "psychologist", "village helper", "village tooler"}  # H22 role_relations.SUPPORT
MEDIA = {"twitterati", "youtuber", "substacker", "reporter", "press baron"}  # H22 role_relations.MEDIA
OPPOSED = [("prankster", "ethicist"), ("prankster", "psychologist")]  # H22 role_relations.OPPOSED
# Roles not in agent_goals (overwritten rows), from operator messages.
EXTRA_ROLES = [  # (agent, role, from, to, ref, note)
    (40, "game dev", "2026-07-24T18:51:52.287799", "2026-07-29T16:50:01.718572", "0025a993-674e-4a53-aa85-1b26aa67ada8",
     "operator assigned the daily-users game goal on arrival; reassigned to Mathematician at chat_core:message_id="
     "ff0510b4-4d1f-4da0-ab71-6ab8f0dffd8c (NE38); the agent_goals row 900abb19 was overwritten (created 07-24, start 07-29)"),
]


def role_spells():
    _, id2c = name_codes()
    sp = []
    with gzip.open(RAW / "agent_goals.jsonl.gz", "rb") as f:
        for line in f:
            r = orjson.loads(line)
            a = id2c.get(r["agent_id"])
            if a is None:
                continue
            sp.append({"agent": a, "role": r["short_name"].strip().lower(), "t0": T(r["start_time"]) if r["start_time"] else T(r["created_at"]),
                       "t1": T(r["end_time"]) if r["end_time"] else EXPORT_END, "ref": f"agent_goals:id={r['id']}",
                       "src": SK_GOAL, "edited": T(r["updated_at"]) > (T(r["start_time"]) if r["start_time"] else T(r["created_at"])) + dt.timedelta(minutes=5)})
    for a, role, t0, t1, ref, note in EXTRA_ROLES:
        sp.append({"agent": a, "role": role, "t0": T(t0), "t1": T(t1), "ref": chat_ref(ref), "src": SK_OP, "note": note, "edited": False})
    return sorted(sp, key=lambda s: (s["agent"], s["t0"]))


def rows_g51():
    sp = role_spells()
    out = []
    der = "raw agent_goals (the rows H22 role_relations.load_role_spells and infra/shared/goal_fields agent_goal read)"
    for s in sp:
        if s["src"] == SK_OP:
            out.append(R(51, "role", s["role"], s["t0"], s["t1"], SK_OP, s["ref"], "high", "operator message (DQ6)",
                         agent=s["agent"], detail=s["note"], conflict_group=f"g51_role_a{s['agent']:02d}_missing"))
            out.append(R(51, "role", None, s["t0"], s["t1"], SK_DER, "agent_goals (no row for this interval)", "low",
                         "H22 role_relations.role_on / goal_fields: agent has no role here (pair class U)", agent=s["agent"],
                         conflict_group=f"g51_role_a{s['agent']:02d}_missing", preferred=False))
        else:
            out.append(R(51, "role", s["role"], s["t0"], s["t1"], SK_GOAL, s["ref"], "high", der, agent=s["agent"],
                         detail="row edited after its start (description may have changed)" if s["edited"] else None))
        cls = "support" if s["role"] in SUPPORT else "media" if s["role"] in MEDIA else None
        if cls:
            out.append(R(51, "role_class", cls, s["t0"], s["t1"], SK_DER, s["ref"], "medium",
                         "H22 role_relations (SUPPORT / MEDIA sets coded from role titles)", agent=s["agent"]))
    for i, x in enumerate(sp):
        for y in sp[i + 1:]:
            if x["agent"] == y["agent"]:
                continue
            t0, t1 = max(x["t0"], y["t0"]), min(x["t1"], y["t1"])
            if t0 >= t1:
                continue
            a, b = sorted((x["agent"], y["agent"]))
            cg = None
            for s in (x, y):
                if s["src"] == SK_OP:
                    cg = f"g51_role_a{s['agent']:02d}_missing"
            refs = f"{x['ref']};{y['ref']}"
            if x["role"] == y["role"]:
                out.append(R(51, "rival_pair", x["role"], t0, t1, SK_DER, refs, "high",
                             "same role short name (H22 role_relations.pair_class SR)" + ("; absent from H22 (missing role)" if cg else ""),
                             agent_a=a, agent_b=b, conflict_group=cg))
            elif (x["role"], y["role"]) in OPPOSED or (y["role"], x["role"]) in OPPOSED:
                out.append(R(51, "opposed_pair", f"{x['role']} x {y['role']}" if x["role"] == "prankster" else f"{y['role']} x {x['role']}",
                             t0, t1, SK_DER, refs, "medium", "H22 role_relations.pair_class OP (coded from role titles)",
                             agent_a=a, agent_b=b, conflict_group=cg))
    return out


# ============================================================================================ rooms
# Operator messages that assign rooms, hand-read (2026-10-04). split: listed agents -> #best, every other agent on the
# day's roster -> #rest; all: everyone -> room; move: one agent -> room.
ROOM_ASSIGN = [
    ("e2f20a53-3c89-4dbe-9b61-e39ad420812d", "split", [23, 20, 22], None, "NE15 split; #rest = all other agents"),
    ("f4733971-0995-4ac8-be08-33f8d5df1d87", "split", [23, 22, 20], None, "restated at #36 kickoff"),
    ("e7fe71d0-c9d6-44e0-ab8e-1febbdcc9d65", "split", [23, 22, 20], None, "restated at #37 kickoff"),
    ("2f27ebb9-08ed-4908-91e9-644a74b53b4e", "move", [21], 2, "#38: Sonnet 4.6 joins #best"),
    ("7e8c5bcd-bd1c-4fbf-9708-1135c7322a95", "split", [26, 24, 22, 25], None, "#39 rejig"),
    ("aaa87e87-7ca1-4fd2-a71f-ac157993e97a", "all", None, 4, "#40 merge into #universe-coordination (NE42)"),
    ("66c417f0-ecfc-4a18-9794-b9d5213181f1", "split", [22, 26, 24, 25], None, "#41 split back (NE42)"),
    ("06f01d56-eed6-410c-be90-28509b4841ae", "split", [22, 26, 24, 25], None, "#42"),
    ("f46149db-93f7-4991-b7ff-7d562410c3b6", "split", [27, 26, 24, 25], None, "#43"),
    ("e88f498c-00f4-4969-ab80-639cef7d4821", "split", [27, 26, 24, 25], None, "#44"),
    ("10d59e72-ff8b-4817-9b74-3209a4de6d55", "split", [27, 26, 29, 25, 30], None, "#45 (Opus 4.7 to #rest, NE19)"),
    ("b5645770-c9a2-445c-8efc-532d863d461d", "split", [27, 26, 29, 25], None, "#46"),
    ("86fe341d-5066-42b9-bf20-5c839a066f0a", "move", [31], 2, "Fable 5: own onboarding room first, then #best"),
    ("ad0d80c0-fa18-409e-9154-4f27427e9a7a", "all", None, 0, "#48 everyone to #general"),
    ("b864917e-adc3-4504-90b9-c5c232d188b6", "all", None, 0, "#49 stay in #general"),
    ("9ecd518f-7d48-40ca-b474-7b841c0de270", "split", [27, 26, 29, 25], None, "#50"),
    ("1be20d7f-422c-42ef-9c22-67fad30491ef", "all", None, 0, "#51 everyone to #general"),
    ("78ded0a6-6731-4042-b495-37cfb4edfbaa", "move", [39], 0, "Kimi K3 to #general"),
]


def roster_on(day: str):
    r = roster()
    return [a for a, j, lf in zip(r["agent"].to_list(), r["joined"].to_list(), r["left"].to_list())
            if j <= day and (lf is None or day < lf)]


_WIN = None


def active_overlap_s(g, a, b):
    """Seconds of [a, b) inside goal g's empirical active windows (calendar win_start..win_end per PT day)."""
    global _WIN
    if _WIN is None:
        cal = pl.read_parquet(OUT / "calendar.parquet")
        _WIN = {}
        for gn, ws, we in zip(cal["goal_no"].to_list(), cal["win_start"].to_list(), cal["win_end"].to_list()):
            _WIN.setdefault(gn, []).append((ws, we))
    return sum(max(0.0, (min(b, we) - max(a, ws)).total_seconds()) for ws, we in _WIN.get(g, []))


def split_goals(t0, t1, min_active_s=0):
    """[(goal_no, a, b)] pieces of [t0, t1) cut at goal starts; pieces with < min_active_s seconds inside the period's
    active windows are dropped (village_goals starts precede the day's kickoff by hours, which leaves empty slivers)."""
    cuts = sorted({g["start"] for g in goals().values() if t0 < g["start"] < t1})
    edges = [t0] + cuts + [t1]
    out = [(goal_of(a), a, b) for a, b in zip(edges[:-1], edges[1:]) if b > a]
    return [x for x in out if min_active_s <= 0 or active_overlap_s(*x) >= min_active_s]


def rows_room_assign():
    c = pl.read_parquet(OUT / "chat_core.parquet", columns=["message_id", "t"])
    tmap = dict(c.filter(pl.col("message_id").is_in([x[0] for x in ROOM_ASSIGN])).iter_rows())
    rr = roster()
    left = {a: (pt_midnight(lf) if lf else EXPORT_END) for a, lf in zip(rr["agent"].to_list(), rr["left"].to_list())}
    events = []  # (t, agent, room, ref, note)
    for mid, kind, agents, room, note in ROOM_ASSIGN:
        t = tmap[mid]
        on = roster_on(ptd(t))
        if kind == "split":
            for a in on:
                events.append((t, a, 2 if a in agents else 3, mid, note + ("" if a in agents else " (#rest = everyone else)")))
        elif kind == "all":
            for a in on:
                events.append((t, a, room, mid, note))
        else:
            for a in agents:
                events.append((t, a, room, mid, note))
    events.sort(key=lambda e: (e[1], e[0]))
    out = []
    for i, (t, a, room, mid, note) in enumerate(events):
        nxt = next((e[0] for e in events[i + 1:] if e[1] == a), None)
        t1 = min(x for x in (nxt, left[a], EXPORT_END) if x is not None)
        if t1 <= t:
            continue
        for g, x, y in split_goals(t, t1, min_active_s=60):
            out.append(R(g, "room_assignment", ROOM_NAMES()[room], x, y, SK_OP, chat_ref(mid), "high",
                         "hand-read operator room assignments (DQ6 ROOM_ASSIGN); holds until the agent's next assignment",
                         agent=a, detail=note))
    return out


_RN = None


def ROOM_NAMES():
    global _RN
    if _RN is None:
        r = pl.read_parquet(OUT / "rooms.parquet")
        _RN = dict(zip(r["room"].to_list(), r["name"].to_list()))
    return _RN


def rows_room_presence():
    rt = pl.read_parquet(OUT / "rooms_timeline.parquet")
    er = (pl.read_parquet(OUT / "events_core.parquet", columns=["event_index", "t", "agent", "room", "action_type", "actor_kind"])
          .filter((pl.col("actor_kind").cast(pl.String) == "agent") & pl.col("agent").is_not_null() & pl.col("room").is_not_null()))
    first = {(a, t): (ei, at) for ei, t, a, at in zip(er["event_index"].to_list(), er["t"].to_list(), er["agent"].to_list(),
                                                    er["action_type"].cast(pl.String).to_list())}
    era = pt_midnight(ROOMS_ERA)
    out = []
    for a, room, t0, tl, te in rt.iter_rows():
        t1 = te if te is not None else tl
        if t1 <= era:
            continue
        ei, at = first.get((a, t0), (None, None))
        entry = "agent_move" if at == "ENTER_ROOM" else ("rooms_era_start" if t0 < era else "assigned_or_first_event")
        x0 = max(t0, era)
        ref = f"rooms_timeline:agent={a};t_start={t0.isoformat()}" + (f";events_core:event_index={ei}" if ei is not None else "")
        pieces = split_goals(x0, t1 if t1 > x0 else x0 + dt.timedelta(microseconds=1), min_active_s=60)
        if not pieces:  # keep single-event intervals whole rather than dropping them
            pieces = split_goals(x0, t1 if t1 > x0 else x0 + dt.timedelta(microseconds=1))[:1]
        for g, x, y in pieces:
            out.append(R(g, "room_presence", ROOM_NAMES()[room], x, y, SK_SYS, ref, "high",
                         "infra/shared/build_derived.py rooms_timeline (room tags on the agent's own events)", agent=a,
                         detail=f"entry={entry}" + (";open_end=last_event" if te is None else "")))
    return out


# ============================================================================================ assembly
def ne_cuts():
    h = load_holdout()
    return sorted({pt_midnight(w["start"]) for w in h["ne_windows"]} | {pt_midnight(w["end"]) for w in h["ne_windows"]})


def split_holdout(rows):
    cuts = ne_cuts()
    out = []
    for r in rows:
        a, b = r["t_valid_from"], r["t_valid_to"]
        inner = [c for c in cuts if a < c < b]
        if not inner:
            out.append(r)
            continue
        edges = [a] + inner + [b]
        for x, y in zip(edges[:-1], edges[1:]):
            if r["label_kind"] in ("room_assignment", "room_presence") and active_overlap_s(r["goal_no"], x, y) < 60:
                continue  # empty piece outside the period's active windows
            out.append({**r, "t_valid_from": x, "t_valid_to": y})
    return out


SCHEMA = {"row_id": pl.Int32, "goal_no": pl.Int8, "label_kind": pl.String, "unit": pl.String, "agent": pl.Int8,
          "agent_a": pl.Int8, "agent_b": pl.Int8, "value": pl.String, "detail": pl.String,
          "t_valid_from": pl.Datetime("us", "UTC"), "t_valid_to": pl.Datetime("us", "UTC"), "source_kind": pl.String,
          "source_ref": pl.String, "confidence": pl.String, "derived_by": pl.String, "conflict_group": pl.String,
          "preferred": pl.Boolean, "holdout": pl.Boolean}
KIND_ORDER = ["team", "judge", "debate_result", "phase", "tally", "leader", "ballot", "vote_declaration", "saboteur",
              "checkpoint", "role", "role_class", "rival_pair", "opposed_pair", "room_assignment", "room_presence"]


def build(cache):
    rows = rows_g12() + rows_g26() + rows_g34(cache) + rows_leaders() + rows_g51() + rows_room_assign() + rows_room_presence()
    rows = split_holdout(rows)
    for r in rows:
        r["holdout"] = bool(holdout_mask([ptd(r["t_valid_from"])], [r["goal_no"]])[0])
        if r["goal_no"] == 34:
            assert r["holdout"], "every #34 row must be held out"
    df = pl.DataFrame(rows, schema={k: v for k, v in SCHEMA.items() if k != "row_id"})
    df = (df.with_columns(pl.col("label_kind").replace_strict({k: i for i, k in enumerate(KIND_ORDER)}).alias("_k"))
          .sort("goal_no", "_k", "unit", "t_valid_from", "agent", "agent_a", "agent_b", "value", "derived_by", nulls_last=True)
          .drop("_k").with_row_index("row_id").with_columns(pl.col("row_id").cast(pl.Int32)))
    df = df.select(list(SCHEMA))
    TABLE.parent.mkdir(parents=True, exist_ok=True)
    df.write_parquet(TABLE, compression="zstd", compression_level=10)
    path = OUT / "_provenance.json"
    prov = json.loads(path.read_text()) if path.exists() else {}
    prov["ground_truth"] = {
        "built_by": "infra/shared/ground_truth.py", "git_commit": git_commit(),
        "inputs": [{"source": "ai-village", "revision": REVISION,
                    "tables": ["agent_goals", "computer_use_turns (#34 days, roll commands only)", "computer_use_sessions"]},
                   {"shared": ["chat_core", "chat_text (read in memory; no text stored)", "chat_mentions_clean", "calendar",
                               "roster", "rooms", "rooms_timeline", "events_core", "intentions", "intentions_text"]},
                   {"hypothesis_files_read_only": ["hypotheses/H21-debate-antiferromagnet/scheme/labels/g12_debates.json",
                                                   "hypotheses/H21-debate-antiferromagnet/analysis/confirm_g34.py (SAB/VIL patterns)"]}],
        "params": {"export_end": EXPORT_END.isoformat(), "rooms_era": ROOMS_ERA, "n_rows": df.height,
                   "kinds": dict(df.group_by("label_kind").len().sort("label_kind").iter_rows()),
                   "holdout_rows": int(df["holdout"].sum()), "no_text": True},
        "output": "data/processed/shared/ground_truth_labels.parquet",
        "built_at": dt.datetime.now(UTC).isoformat()}
    path.write_text(json.dumps(prov, indent=1))
    print(f"wrote {TABLE} ({df.height} rows, {TABLE.stat().st_size / 1e3:.0f} kB); holdout rows {int(df['holdout'].sum())}")
    return df


# ============================================================================================ validation
def _hdr(s):
    print(f"\n=== {s}")


def validate(seed=20261004, n_hand=18):
    """Coverage, disagreement between existing derivations, and a seeded hand-check sample (non-holdout rows only).
    #34 (holdout): row count only; nothing else is computed or printed for it."""
    df = pl.read_parquet(TABLE)
    nh = df.filter(~pl.col("holdout"))
    _hdr("coverage (non-holdout): rows / agents / periods by kind")
    ag = nh.with_columns(pl.concat_list([pl.col("agent"), pl.col("agent_a"), pl.col("agent_b")]).list.drop_nulls().alias("_ag"))
    cov = (ag.group_by("label_kind").agg(pl.len().alias("rows"), pl.col("_ag").list.explode(keep_nulls=False, empty_as_null=False).n_unique().alias("agents"),
                                         pl.col("goal_no").unique().sort().alias("periods"),
                                         (pl.col("conflict_group").is_not_null()).sum().alias("in_conflict"))
           .sort("label_kind"))
    for r in cov.iter_rows(named=True):
        ps = r["periods"]
        pstr = ",".join(map(str, ps)) if len(ps) <= 8 else f"{ps[0]}..{ps[-1]} ({len(ps)} periods)"
        print(f"  {r['label_kind']:<17} rows {r['rows']:>5}  agents {r['agents']:>3}  conflict-rows {r['in_conflict']:>3}  periods {pstr}")
    _hdr("rows per goal period x kind (non-holdout)")
    pk = nh.group_by("goal_no", "label_kind").len().sort("goal_no", "label_kind")
    for g in sorted(set(pk["goal_no"].to_list())):
        x = pk.filter(pl.col("goal_no") == g)
        print(f"  #{g}: " + ", ".join(f"{k} {n}" for k, n in zip(x["label_kind"].to_list(), x["len"].to_list())))
    _hdr("holdout rows (counts only)")
    ho = df.filter(pl.col("holdout"))
    print(f"  #34: {ho.filter(pl.col('goal_no') == 34).height} rows (no further statistic computed)")
    for g in sorted(set(ho["goal_no"].to_list()) - {34}):
        x = ho.filter(pl.col("goal_no") == g).group_by("label_kind").len().sort("label_kind")
        print(f"  #{g}: " + ", ".join(f"{k} {n}" for k, n in x.iter_rows()))

    # ---------------------------------------------------------------- #12
    _hdr("#12: speaker consistency of the H21 anchor messages; H21 vs H37 window rule")
    lab = json.loads(H21_LABELS.read_text())
    n2c, _ = name_codes()
    cc = pl.read_parquet(OUT / "chat_core.parquet", columns=["message_id", "t", "agent", "goal_no", "speaker_kind"])
    spk = dict(zip(cc["message_id"].to_list(), cc["agent"].to_list()))
    bad = []
    for d in lab["debates"]:
        if not d["held"]:
            continue
        j, gov, opp = n2c[d["judge"]], {n2c[x] for x in d["gov"]}, {n2c[x] for x in d["opp"]}
        if spk.get(d["verdict_message_id"]) != j:
            bad.append((d["debate"], "verdict speaker != judge", spk.get(d["verdict_message_id"])))
        if spk.get(d["first_speech_message_id"]) not in gov:
            bad.append((d["debate"], "first speech not by Government", spk.get(d["first_speech_message_id"])))
        if d["motion_chosen_by"] == "judge" and spk.get(d["motion_message_id"]) != j:
            bad.append((d["debate"], "motion announced by non-judge", spk.get(d["motion_message_id"])))
        if spk.get(d["lineup_message_id"]) not in gov | opp | {j}:
            bad.append((d["debate"], "lineup message by non-participant", spk.get(d["lineup_message_id"])))
    print(f"  10 debates checked; issues: {bad if bad else 'none'}")
    g12c = df.filter((pl.col("goal_no") == 12) & pl.col("conflict_group").is_not_null())
    print(f"  post-end conflicts (H21 day-end clamp vs H37): {g12c['conflict_group'].n_unique()} debates")
    for cg in g12c["conflict_group"].unique().to_list():
        x = g12c.filter(pl.col("conflict_group") == cg).sort("t_valid_to")
        a, b = x["t_valid_to"][0], x["t_valid_to"][-1]
        nm = cc.filter((pl.col("t") >= a) & (pl.col("t") < b)).height
        print(f"    {cg}: windows differ by {(b - a).total_seconds() / 60:.1f} min; chat messages in the gap: {nm}")

    # ---------------------------------------------------------------- #26
    _hdr("#26: H11 votes reimplementation vs H11's votes.parquet; ballots vs official tallies; onset rules")
    c = g26_chat()
    mine = h11_votes(c)
    try:
        h11 = pl.read_parquet(ROOT / "data/processed/H11-potts-labor-vs-herding/G26/votes.parquet")
        a = {(v["message_id"], tuple(v["named"]), v["first_person"], v["runoff_word"]) for v in mine}
        b = {(m, tuple(nl), fp, ro) for m, nl, fp, ro in zip(h11["message_id"].to_list(), h11["named"].to_list(),
                                                            h11["first_person"].to_list(), h11["runoff_word"].to_list())}
        print(f"  reimplementation {len(a)} rows, H11 file {len(b)} rows, identical: {a == b} (only mine {len(a - b)}, only H11 {len(b - a)})")
    except Exception as e:  # noqa: BLE001
        print(f"  H11 votes.parquet not readable: {e}")
    ball = g26_ballots(c)
    for unit, ref, counts in G26_TALLIES:
        got = ball[unit]
        tally = {}
        for voter, (_, _, chosen) in got.items():
            for cnd in chosen:
                tally[cnd] = tally.get(cnd, 0) + 1
        ok = all(tally.get(k, 0) == v for k, v in counts.items()) and set(tally) <= set(counts)
        print(f"  {unit:<12} official {dict(sorted(counts.items()))}  extracted {dict(sorted(tally.items()))}  voters {len(got)}  match: {ok}")
    on = df.filter(pl.col("conflict_group") == "g26_runoff_onset").sort("t_valid_from")
    for r in on.iter_rows(named=True):
        print(f"  runoff onset {r['t_valid_from'].isoformat()[:19]}  preferred={r['preferred']}  {r['derived_by'][:70]}")
    # where H11/H31's "runoff" consensus actually happened
    dec = [v for v in mine if v["vote_word"] and v["first_person"] and v["candidate"] is not None]
    ro = sorted((v for v in mine if v["runoff_word"]), key=lambda v: v["t"])
    post = [v for v in sorted(dec, key=lambda v: v["t"]) if v["t"] >= ro[0]["t"]]
    cur, tcons = {}, None
    for v in post:
        cur[v["agent"]] = v["candidate"]
        if tcons is None and len(cur) >= 3 and sum(1 for x in cur.values() if x == 17) / len(cur) >= 0.5:
            tcons = v["t"]
    last_single = {}
    for v in sorted(dec, key=lambda v: v["t"]):
        if v["n_named"] == 1:
            last_single[v["agent"]] = v
    on9 = sum(1 for v in last_single.values() if ptd(v["t"]) == "2026-01-09")
    print(f"  H31 rule: winner share first >= 0.5 (n >= 3) at {tcons.isoformat()[:19] if tcons else None} UTC (record: runoff closed 2026-01-05T19:34:00)")
    print(f"  H11 runoff snapshot (last single-candidate first-person declaration per agent): {on9}/{len(last_single)} dated 2026-01-09")

    # ---------------------------------------------------------------- #51
    _hdr("#51: table roles vs H22 role_on (per agent x PT day, non-holdout days) and goal_fields agent_goal rows")
    sys.path.insert(0, str(ROOT / "hypotheses/H22-private-goals-spin-glass/scheme"))
    import role_relations as RRm  # read-only import
    _, id2c = name_codes()
    sp22 = RRm.load_role_spells(id2c)
    cal = pl.read_parquet(OUT / "calendar.parquet").filter((pl.col("goal_no") == 51) & ~pl.col("holdout"))
    days = sorted(cal["pt_date"].to_list())
    roles = df.filter((pl.col("label_kind") == "role") & pl.col("preferred"))
    mism, n = [], 0
    for a in sorted(set(roles["agent"].to_list())):
        ra = roles.filter(pl.col("agent") == a)
        for d in days:
            if d not in roster_on(d) and a not in roster_on(d):
                continue
            n += 1
            noon = pt_midnight(d) + dt.timedelta(hours=12)
            mine_r = ra.filter((pl.col("t_valid_from") <= noon) & (pl.col("t_valid_to") > noon))["value"].to_list()
            mine_r = mine_r[0] if mine_r else None
            h22 = RRm.role_on(sp22, a, d)
            if mine_r != h22:
                mism.append((a, d, h22, mine_r))
    print(f"  agent-days compared {n}; mismatches {len(mism)}")
    for a, d, h, m in mism[:12]:
        print(f"    agent {a} {d}: H22 {h!r} vs table (role at 12:00 PT) {m!r}")
    try:
        gf = pl.read_parquet(OUT / "embeddings/goals.parquet").filter(pl.col("kind") == "agent_goal")
        refs = set(gf["ref"].to_list())
        trefs = {r.split("=", 1)[1] for r in roles.filter(pl.col("source_kind") == SK_GOAL)["source_ref"].to_list()}
        print(f"  goal_fields agent_goal rows {len(refs)}; table agent_goals refs {len(trefs)}; same ids: {refs == trefs}")
    except Exception as e:  # noqa: BLE001
        print(f"  goal_fields not readable: {e}")
    sr22 = set()
    for i, x in enumerate(sp22):
        for y in sp22[i + 1:]:
            if x[0] != y[0] and RRm.pair_class(x[1], y[1]) in (1, 2):
                sr22.add((min(x[0], y[0]), max(x[0], y[0]), RRm.pair_class(x[1], y[1])))
    tp = df.filter(pl.col("label_kind").is_in(["rival_pair", "opposed_pair"]) & pl.col("conflict_group").is_null())
    tset = {(a, b, 1 if k == "rival_pair" else 2) for a, b, k in zip(tp["agent_a"].to_list(), tp["agent_b"].to_list(), tp["label_kind"].to_list())}
    print(f"  SR/OP pairs: H22 {len(sr22)}, table (excluding the operator-message role) {len(tset)}, same: {sr22 == tset}")

    # ---------------------------------------------------------------- #44
    _hdr("#44: checkpoint starts, operator messages vs H23 h23lib.CHECKPOINTS")
    for name, a, *_ in CHECKPOINTS:
        print(f"  {name:<18} operator {a[:19]}  H23 {H23_CHECKPOINTS[name]}  diff {(T(a) - T(H23_CHECKPOINTS[name])).total_seconds():+.1f} s")
    ev28 = pl.read_parquet(OUT / "events_core.parquet", columns=["t", "agent", "action_type"]).filter(
        (pl.col("agent") == 28) & (pl.col("t") < T(CHECKPOINTS[1][1])) & (pl.col("t") > T(CHECKPOINTS[0][2])))
    print(f"  agent-28 events between the v3 stop and the v10 start (H23 would label them qwen-v3): {ev28.height} "
          f"{ev28['action_type'].cast(pl.String).to_list()}")

    # ---------------------------------------------------------------- rooms
    _hdr("rooms: operator assignment vs system presence (share of the agent's room-tagged events in the assigned room)")
    rn = {v: k for k, v in ROOM_NAMES().items()}
    er = pl.read_parquet(OUT / "events_core.parquet", columns=["t", "agent", "room", "actor_kind"]).filter(
        (pl.col("actor_kind").cast(pl.String) == "agent") & pl.col("room").is_not_null())
    asg = nh.filter(pl.col("label_kind") == "room_assignment")
    shares = []
    for r in asg.iter_rows(named=True):
        x = er.filter((pl.col("agent") == r["agent"]) & (pl.col("t") >= r["t_valid_from"]) & (pl.col("t") < r["t_valid_to"]))
        if x.height == 0:
            continue
        shares.append((float((x["room"] == rn[r["value"]]).mean()), r["row_id"], r["agent"], r["goal_no"], r["value"], x.height))
    import statistics
    sh = [s[0] for s in shares]
    print(f"  assignment rows with events {len(sh)} of {asg.height}; median share {statistics.median(sh):.3f}; "
          f">= 0.9: {sum(s >= 0.9 for s in sh)}; < 0.5: {sum(s < 0.5 for s in sh)}")
    for s in sorted(shares)[:10]:
        print(f"    row {s[1]} agent {s[2]} #{s[3]} assigned {s[4]}: share {s[0]:.2f} of {s[5]} events")

    # ---------------------------------------------------------------- hand-check sample
    _hdr(f"hand-check sample (seed {seed}; non-holdout; checked against raw tables, see the docs)")
    strata = {"team": 2, "judge": 1, "debate_result": 1, "ballot": 2, "tally": 1, "leader": 1, "role": 2, "rival_pair": 1,
              "checkpoint": 1, "room_assignment": 2, "room_presence": 2, "opposed_pair": 1, "phase": 1}
    samp = []
    for k, m in strata.items():
        x = nh.filter((pl.col("label_kind") == k) & pl.col("preferred"))
        if x.height:
            samp.append(x.sample(min(m, x.height), seed=seed))
    samp = pl.concat(samp).head(n_hand)
    for r in samp.iter_rows(named=True):
        who = r["agent"] if r["agent"] is not None else f"{r['agent_a']}->{r['agent_b']}"
        print(f"  row {r['row_id']:>5} #{r['goal_no']} {r['label_kind']:<15} {str(who):<7} {str(r['value'])[:22]:<22} "
              f"{r['t_valid_from'].isoformat()[:19]} {r['source_ref'][:90]}")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--validate", action="store_true")
    ap.add_argument("--turns-cache", type=Path, default=None,
                    help="pre-filtered #34-day computer_use_turns lines (gzip -dc | grep created_at); else scanned from raw")
    a = ap.parse_args()
    if a.validate:
        validate()
    else:
        build(a.turns_cache)


if __name__ == "__main__":
    main()
